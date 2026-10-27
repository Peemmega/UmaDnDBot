"""Central persistence and query service for completed race history.

Race state remains in memory while a race is running.  This module writes one
atomic, idempotent snapshot only when the race has actually finished, then
derives leaderboards and career history from those completed records.
"""

from __future__ import annotations

import copy
import json
import uuid
from datetime import datetime, timezone
from typing import Any

from utils.database import database_connection, get_trainee_trainer
from utils.skill.skill_presets import SKILLS

OFFICIAL = "official"
PRACTICE = "practice"


def classify_record_type(game: dict) -> str:
    explicit = str(game.get("record_type") or "").lower()
    if explicit in {OFFICIAL, PRACTICE}:
        return explicit

    # Missing metadata must never publish a result to the official leaderboard.
    return PRACTICE


def ensure_race_history_id(game: dict) -> str:
    race_id = game.get("race_history_id")
    if not race_id:
        race_id = uuid.uuid4().hex
        game["race_history_id"] = race_id
    return str(race_id)


def record_race_action(
    game: dict,
    player_id,
    action_type: str,
    details: dict | None = None,
    target_id=None,
) -> None:
    """Collect a structured action for later atomic completion persistence."""
    player = (game.get("players") or {}).get(player_id)
    if player is None:
        return
    game.setdefault("race_action_logs", []).append(
        {
            "turn": int(game.get("turn", 0) or 0),
            "player_id": str(player_id),
            "player_name": str(
                player.get("display_name") or player.get("username") or player_id
            ),
            "action_type": str(action_type).lower(),
            "target_id": str(target_id) if target_id is not None else None,
            "details": copy.deepcopy(details or {}),
        }
    )


def record_turn_snapshot(game: dict, turn_number: int) -> None:
    """Mark the turn logs as history data; writing is deferred until finish."""
    if turn_number > 0:
        game.setdefault("race_history_turns_recorded", set()).add(int(turn_number))


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, default=str, separators=(",", ":"))


def _participant_identity(player_id, player: dict) -> dict:
    is_mob = bool(player.get("is_mob")) or str(player_id).startswith("mob_")
    persistent_uma = not is_mob and not player.get("using_mob_preset")
    participant_type = (
        "mob" if is_mob else ("npc" if player.get("using_mob_preset") else "uma")
    )
    trainer = get_trainee_trainer(str(player_id)) if persistent_uma else None
    return {
        "participant_id": str(player_id),
        "uma_id": str(player_id) if persistent_uma else None,
        "uma_name": str(
            player.get("display_name") or player.get("username") or player_id
        ),
        "trainer_id": str(trainer["user_id"]) if trainer else None,
        "trainer_name": trainer.get("name") if trainer else None,
        "participant_type": participant_type,
        "mob_id": str(player.get("mob_preset_key") or player_id) if is_mob else None,
    }


def _participant_snapshot(player: dict) -> dict:
    profile = copy.deepcopy(player.get("race_profile") or {})
    if not profile:
        profile = {
            key: player.get(key)
            for key in (
                "speed",
                "stamina",
                "power",
                "gut",
                "wit",
                "turf",
                "dirt",
                "sprint",
                "mile",
                "medium",
                "long",
                "front",
                "pace",
                "late",
                "end_style",
            )
            if player.get(key) is not None
        }
    effective = copy.deepcopy(player.get("effective_race_stats") or {})
    skills = player.get("skills") or {}
    selected_skills = [_skill_snapshot(skill) for skill in skills.values() if skill]
    return {
        "display_name": player.get("display_name") or player.get("username"),
        "base_stats": {
            key: profile.get(key) for key in ("speed", "stamina", "power", "gut", "wit")
        },
        "aptitudes": {
            key: profile.get(key)
            for key in (
                "turf",
                "dirt",
                "sprint",
                "mile",
                "medium",
                "long",
                "front",
                "pace",
                "late",
                "end_style",
            )
        },
        "running_style": player.get("style"),
        "skills": selected_skills,
        "zone": copy.deepcopy(player.get("zone") or {}),
        "effective_race_stats": effective,
    }


def _skill_snapshot(skill: Any) -> dict:
    """Keep a display-ready skill reference even when the game stores only its id."""
    if isinstance(skill, str):
        skill_id = skill
        supplied = {}
    elif isinstance(skill, dict):
        supplied = copy.deepcopy(skill)
        skill_id = str(supplied.get("id") or supplied.get("skill_id") or "")
    else:
        skill_id = str(skill)
        supplied = {}

    definition = SKILLS.get(skill_id, {})
    supplied_name = supplied.get("name")
    # Older snapshots often stored the id again as the name. Prefer the
    # authoritative preset label in that case so history remains readable.
    display_name = (
        definition.get("name")
        if definition.get("name") and (not supplied_name or supplied_name == skill_id)
        else supplied_name or skill_id or str(skill)
    )
    return {
        "id": skill_id or str(supplied.get("name") or skill),
        "name": display_name,
        "icon": supplied.get("icon") or definition.get("icon"),
    }


def _hydrate_participant_snapshot(snapshot: Any) -> dict:
    if not isinstance(snapshot, dict):
        return {}
    skills = snapshot.get("skills")
    if isinstance(skills, list):
        snapshot["skills"] = [_skill_snapshot(skill) for skill in skills if skill]
    return snapshot


def _aptitude_modifier(value: Any) -> float:
    ranks = {"G": 1.0, "F": 1.05, "E": 1.1, "D": 1.15, "C": 1.2, "B": 1.25, "A": 1.3, "S": 1.35}
    normalized = str(value or "").strip().upper()
    if normalized.isdigit():
        index = int(normalized) - 1
        normalized = ("G", "F", "E", "D", "C", "B", "A", "S")[index] if 0 <= index < 8 else ""
    return ranks.get(normalized, 1.0)


def _participant_replay_states(participant: dict, turns: list[dict], actions: list[dict], total_turns: int) -> dict:
    """Derive per-phase Wit and skill state from the same race rules used in play."""
    participant_id = str(participant.get("participant_id") or "")
    snapshot = participant.get("snapshot") or {}
    base_stats = snapshot.get("base_stats") or {}
    aptitudes = snapshot.get("aptitudes") or {}
    effective_stats = snapshot.get("effective_race_stats") or {}
    base_wit = int(base_stats.get("wit") or 0)
    style_key = {
        "front": "front", "pace": "pace", "late": "late", "end": "end_style",
    }.get(str(snapshot.get("running_style") or participant.get("running_style") or "pace").strip().lower(), "pace")
    wit_gain = effective_stats.get("effective_wit_gain")
    if wit_gain is None:
        wit_gain = round((10 + base_wit * 2) * _aptitude_modifier(aptitudes.get(style_key)))
    wit_gain = int(wit_gain)

    skills_by_id = {}
    for skill in snapshot.get("skills") or []:
        normalized = _skill_snapshot(skill)
        if normalized.get("id"):
            skills_by_id[normalized["id"]] = normalized

    snapshot_uses: dict[str, dict[int, dict]] = {}
    action_uses: dict[str, dict[int, dict]] = {}

    def add_use(destination: dict, skill_id: Any, turn_number: Any, cost: Any = None, cooldown: Any = None) -> None:
        skill_id = str(skill_id or "")
        try:
            turn_number = int(turn_number)
        except (TypeError, ValueError):
            return
        if not skill_id or turn_number < 1:
            return
        definition = SKILLS.get(skill_id) or {}
        use = destination.setdefault(skill_id, {}).setdefault(turn_number, {
            "cost": 0,
            "count": 0,
            "cooldown": int(cooldown if cooldown is not None else definition.get("cooldown", 0) or 0),
        })
        use["cost"] += int(cost if cost is not None else definition.get("cost", 0) or 0)
        use["count"] += 1

    for turn in turns:
        if str(turn.get("participant_id")) != participant_id:
            continue
        data = turn.get("turn_data") or {}
        for skill in data.get("skills") or []:
            if isinstance(skill, dict):
                add_use(snapshot_uses, skill.get("id") or skill.get("skill_id"), turn.get("turn_number"), skill.get("cost"), skill.get("cooldown"))
            else:
                add_use(snapshot_uses, skill, turn.get("turn_number"))

    for action in actions:
        if str(action.get("participant_id")) != participant_id or str(action.get("action_type") or "").lower() != "skill":
            continue
        data = action.get("action_data") or {}
        add_use(action_uses, data.get("skill_id") or data.get("id"), action.get("turn_number"), data.get("cost"), data.get("cooldown"))

    # Action records include actual costs and repetitions; turn snapshots are a fallback for older races.
    uses_by_skill = {skill_id: dict(turn_uses) for skill_id, turn_uses in snapshot_uses.items()}
    for skill_id, turn_uses in action_uses.items():
        uses_by_skill.setdefault(skill_id, {}).update(turn_uses)

    # Include a skill seen in history even if an older race snapshot omitted it.
    for skill_id in uses_by_skill:
        skills_by_id.setdefault(skill_id, _skill_snapshot(skill_id))

    replay_states = {}
    recorded_wit_by_turn = {
        int(turn.get("turn_number") or 0): (turn.get("turn_data") or {})
        for turn in turns
        if str(turn.get("participant_id")) == participant_id
    }
    for turn_number in range(1, max(0, int(total_turns)) + 1):
        replay_states[str(turn_number)] = {}
        for phase in ("lane", "run"):
            eligible = {}
            for skill_id, turn_uses in uses_by_skill.items():
                for used_turn, use in turn_uses.items():
                    is_prior = used_turn < turn_number
                    is_current_use = used_turn == turn_number and (
                        phase == "run" or (SKILLS.get(skill_id) or {}).get("activation", "active") == "passive"
                    )
                    if is_prior or is_current_use:
                        eligible.setdefault(skill_id, {})[used_turn] = use

            spent_wit = sum(use["cost"] for turn_uses in eligible.values() for use in turn_uses.values())
            skill_states = {}
            for skill_id, skill in skills_by_id.items():
                uses = eligible.get(skill_id) or {}
                latest_turn = max(uses) if uses else None
                cooldown = uses[latest_turn]["cooldown"] if latest_turn is not None else int((SKILLS.get(skill_id) or {}).get("cooldown", 0) or 0)
                elapsed = max(0, turn_number - latest_turn) if latest_turn is not None else 0
                skill_states[skill_id] = {
                    "used": bool(uses),
                    "use_count": sum(use["count"] for use in uses.values()),
                    "cooldown_remaining": max(0, cooldown - elapsed) if latest_turn is not None else 0,
                }
            turn_data = recorded_wit_by_turn.get(turn_number) or {}
            wit_keys = ("wit_mana_after", "wit_after") if phase == "run" else ("wit_mana_before", "wit_before")
            recorded_candidates = [turn_data.get(key) for key in wit_keys]
            recorded_candidates.append((turn_data.get("roll") or {}).get(wit_keys[0]))
            recorded_wit = next((value for value in recorded_candidates if value is not None), None)
            try:
                wit_value = int(recorded_wit) if recorded_wit is not None else None
            except (TypeError, ValueError):
                wit_value = None
            replay_states[str(turn_number)][phase] = {
                "wit": wit_value if wit_value is not None else 100 + base_wit * 10 + wit_gain * (turn_number - 1) - spent_wit,
                "wit_gain": wit_gain,
                "skills": skill_states,
                "source": "recorded" if wit_value is not None else "simulated",
            }
    return replay_states


def _turn_rows(game: dict) -> list[dict]:
    rows_by_key: dict[tuple[str, int], dict] = {}
    for log in game.get("turn_score_logs", []):
        player_id = str(log.get("player_id"))
        turn = int(log.get("turn", 0) or 0)
        if not player_id or turn < 1:
            continue
        key = (player_id, turn)
        roll = copy.deepcopy(log.get("roll") or {})
        lane_change = roll.get("lane_change")
        existing = rows_by_key.get(key)
        if existing is None or not lane_change:
            rows_by_key[key] = {
                "participant_id": player_id,
                "turn_number": turn,
                "run_score": roll.get("total") if roll else None,
                "score_before": int(log.get("score_before", 0) or 0),
                "score_after": int(log.get("score_after", 0) or 0),
                "stamina_before": (roll.get("stamina") or {}).get("before"),
                "stamina_after": (roll.get("stamina") or {}).get("current_stamina"),
                "lane": roll.get("current_lane"),
                "position": log.get("position"),
                "data": {
                    "roll": roll,
                    "skills": copy.deepcopy(log.get("skills") or []),
                },
            }
        elif lane_change:
            existing["lane"] = lane_change.get("to", existing.get("lane"))
            existing["data"]["lane_change"] = lane_change
    return list(rows_by_key.values())


def save_completed_race(game: dict, ranked_players) -> str:
    """Atomically replace one completed race snapshot using a stable race id."""
    race_id = ensure_race_history_id(game)
    if game.get("race_history_saved"):
        return race_id

    participants = []
    rank_by_id = {
        str(player_id): index
        for index, (player_id, _) in enumerate(ranked_players, start=1)
    }
    for player_id, player in game.get("players", {}).items():
        identity = _participant_identity(player_id, player)
        final_score = int(player.get("web_distance", player.get("score", 0)) or 0)
        identity.update(
            {
                "running_style": str(player.get("style") or ""),
                "entry_number": int(player.get("entry_number", 0) or 0) or None,
                "final_rank": rank_by_id.get(str(player_id)),
                "final_score": final_score,
                "snapshot_json": _json(_participant_snapshot(player)),
            }
        )
        participants.append(identity)

    if not participants:
        raise ValueError("Cannot save a completed race without participants")

    turn_rows = _turn_rows(game)
    actions = list(game.get("race_action_logs", []))
    now = datetime.now(timezone.utc).isoformat()
    with database_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO race_history (
                race_id, stage_key, stage_name, track, distance, total_turns,
                race_mode, record_type, is_legend, room_id, started_at, finished_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(race_id) DO UPDATE SET
                stage_key=excluded.stage_key, stage_name=excluded.stage_name,
                track=excluded.track, distance=excluded.distance,
                total_turns=excluded.total_turns, race_mode=excluded.race_mode,
                record_type=excluded.record_type, is_legend=excluded.is_legend, room_id=excluded.room_id,
                finished_at=excluded.finished_at
            """,
            (
                race_id,
                str(game.get("stage_key") or "unknown"),
                "Legend Race" if game.get("is_legend") else str(game.get("stage_name") or "Unknown"),
                game.get("track"),
                game.get("distance"),
                int(game.get("max_turn", 0) or 0),
                str(game.get("race_mode") or "discord_classic"),
                classify_record_type(game),
                1 if game.get("is_legend") else 0,
                str(game.get("room_id") or game.get("channel_id") or "") or None,
                game.get("race_started_at"),
                now,
            ),
        )
        cursor.execute(
            "DELETE FROM race_participant_actions WHERE race_id = ?", (race_id,)
        )
        cursor.execute(
            "DELETE FROM race_participant_turns WHERE race_id = ?", (race_id,)
        )
        cursor.execute("DELETE FROM race_participants WHERE race_id = ?", (race_id,))
        for participant in participants:
            cursor.execute(
                """INSERT INTO race_participants (
                    race_id, participant_id, uma_id, uma_name, trainer_id, trainer_name,
                    participant_type, mob_id, running_style, entry_number, final_rank,
                    final_score, snapshot_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    race_id,
                    *[
                        participant[key]
                        for key in (
                            "participant_id",
                            "uma_id",
                            "uma_name",
                            "trainer_id",
                            "trainer_name",
                            "participant_type",
                            "mob_id",
                            "running_style",
                            "entry_number",
                            "final_rank",
                            "final_score",
                            "snapshot_json",
                        )
                    ],
                ),
            )
        participant_ids = {
            participant["participant_id"] for participant in participants
        }
        for turn in turn_rows:
            if turn["participant_id"] not in participant_ids:
                continue
            cursor.execute(
                """INSERT INTO race_participant_turns (
                    race_id, participant_id, turn_number, run_score, score_before, score_after,
                    stamina_before, stamina_after, lane, position, turn_data_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    race_id,
                    turn["participant_id"],
                    turn["turn_number"],
                    turn["run_score"],
                    turn["score_before"],
                    turn["score_after"],
                    turn["stamina_before"],
                    turn["stamina_after"],
                    turn["lane"],
                    turn["position"],
                    _json(turn["data"]),
                ),
            )
        for action in actions:
            participant_id = str(action.get("player_id") or "")
            if participant_id not in participant_ids:
                continue
            cursor.execute(
                """INSERT INTO race_participant_actions (
                    race_id, participant_id, turn_number, action_type,
                    target_participant_id, action_data_json
                ) VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    race_id,
                    participant_id,
                    int(action.get("turn", 0) or 0),
                    str(action.get("action_type") or "other"),
                    action.get("target_id"),
                    _json(action.get("details") or {}),
                ),
            )

    game["race_history_saved"] = True
    return race_id


def _decode(row: dict, key: str) -> dict:
    row[key.removesuffix("_json")] = json.loads(row.get(key) or "{}")
    row.pop(key, None)
    return row


def get_race_by_id(race_id: str) -> dict | None:
    with database_connection() as conn:
        cursor = conn.cursor()
        race = cursor.execute(
            "SELECT * FROM race_history WHERE race_id = ?", (race_id,)
        ).fetchone()
        if race is None:
            return None
        participants = [
            dict(row)
            for row in cursor.execute(
                "SELECT * FROM race_participants WHERE race_id = ? ORDER BY final_rank ASC, participant_id ASC",
                (race_id,),
            ).fetchall()
        ]
        turns = [
            dict(row)
            for row in cursor.execute(
                "SELECT * FROM race_participant_turns WHERE race_id = ? ORDER BY turn_number, position, participant_id",
                (race_id,),
            ).fetchall()
        ]
        actions = [
            dict(row)
            for row in cursor.execute(
                "SELECT * FROM race_participant_actions WHERE race_id = ? ORDER BY turn_number, action_id",
                (race_id,),
            ).fetchall()
        ]
    for row in participants:
        _decode(row, "snapshot_json")
        row["snapshot"] = _hydrate_participant_snapshot(row.get("snapshot"))
    for row in turns:
        _decode(row, "turn_data_json")
    for row in actions:
        _decode(row, "action_data_json")
    total_turns = max(
        int((dict(race) if race else {}).get("total_turns") or 0),
        max((int(row.get("turn_number") or 0) for row in turns), default=0),
    )
    for participant in participants:
        participant["replay_states"] = _participant_replay_states(
            participant, turns, actions, total_turns
        )
    return {
        "race": dict(race),
        "participants": participants,
        "turns": turns,
        "actions": actions,
    }


def list_race_history(
    *,
    stage_key: str | None = None,
    record_type: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[dict]:
    clauses, params = ["h.source != 'legacy_race_rankings'"], []
    if stage_key:
        clauses.append("stage_key = ?")
        params.append(stage_key)
    if record_type in {OFFICIAL, PRACTICE}:
        clauses.append("record_type = ?")
        params.append(record_type)
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    with database_connection() as conn:
        rows = conn.execute(
            f"""SELECT h.*,
                       (SELECT p.participant_id FROM race_participants p
                         WHERE p.race_id = h.race_id
                         ORDER BY p.final_rank ASC, p.final_score DESC, p.participant_id ASC
                         LIMIT 1) AS winner_id,
                       (SELECT p.uma_name FROM race_participants p
                         WHERE p.race_id = h.race_id
                         ORDER BY p.final_rank ASC, p.final_score DESC, p.participant_id ASC
                         LIMIT 1) AS winner_name,
                       (SELECT p.trainer_name FROM race_participants p
                         WHERE p.race_id = h.race_id
                         ORDER BY p.final_rank ASC, p.final_score DESC, p.participant_id ASC
                         LIMIT 1) AS winner_trainer_name,
                       (SELECT p.running_style FROM race_participants p
                         WHERE p.race_id = h.race_id
                         ORDER BY p.final_rank ASC, p.final_score DESC, p.participant_id ASC
                         LIMIT 1) AS winner_running_style,
                       (SELECT p.final_score FROM race_participants p
                         WHERE p.race_id = h.race_id
                         ORDER BY p.final_rank ASC, p.final_score DESC, p.participant_id ASC
                         LIMIT 1) AS winner_score
                FROM race_history h {where}
                ORDER BY h.finished_at DESC LIMIT ? OFFSET ?""",
            (*params, max(1, min(int(limit), 100)), max(0, int(offset))),
        ).fetchall()
    return [dict(row) for row in rows]


def get_participant_history(
    *,
    column: str,
    value: str,
    record_type: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    if column not in {"uma_id", "trainer_id"}:
        raise ValueError("Unsupported history identity")
    clauses = [f"p.{column} = ?", "h.source != 'legacy_race_rankings'"]
    params: list[Any] = [str(value)]
    if record_type in {OFFICIAL, PRACTICE}:
        clauses.append("h.record_type = ?")
        params.append(record_type)
    with database_connection() as conn:
        rows = conn.execute(
            f"""SELECT h.*, p.participant_id, p.uma_id, p.uma_name, p.trainer_id,
                       p.trainer_name, p.participant_type, p.running_style,
                       p.final_rank, p.final_score
                FROM race_participants p JOIN race_history h ON h.race_id = p.race_id
                WHERE {' AND '.join(clauses)}
                ORDER BY h.finished_at DESC LIMIT ? OFFSET ?""",
            (*params, max(1, min(int(limit), 100)), max(0, int(offset))),
        ).fetchall()
    return [dict(row) for row in rows]


def get_course_leaderboard(
    stage_key: str, limit: int = 10, record_type: str = OFFICIAL
) -> list[dict]:
    """One best official score per persistent Uma for the course."""
    with database_connection() as conn:
        rows = conn.execute(
            """WITH ranked AS (
                    SELECT p.uma_id AS user_id, p.uma_name AS username,
                           p.final_score AS best_score, p.running_style AS style,
                           h.finished_at AS updated_at, h.record_type,
                           ROW_NUMBER() OVER (
                             PARTITION BY p.uma_id
                             ORDER BY p.final_score DESC, h.finished_at ASC
                           ) AS personal_best_row
                    FROM race_participants p
                    JOIN race_history h ON h.race_id = p.race_id
                    WHERE h.stage_key = ? AND h.record_type = ?
                      AND p.uma_id IS NOT NULL
                )
                SELECT ? AS stage_key, user_id, username, best_score, style, updated_at, record_type
                FROM ranked WHERE personal_best_row = 1
                ORDER BY best_score DESC, updated_at ASC LIMIT ?""",
            (stage_key, record_type, stage_key, max(1, min(int(limit), 100))),
        ).fetchall()
    return [dict(row) for row in rows]
