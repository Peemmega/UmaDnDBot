"""Plan Mob skill and Zone use over the remaining race.

Future opponents, distance colors and stamina are uncertain: the plan assumes
the current pack color and is rebuilt from the actual state every turn.
"""

from itertools import combinations

from utils.dice.dice_presets import MAX_SPEED_PHASE
from utils.game.progression import ACCELERATION_SCALE
from utils.mob.mob_profiles import get_ai_profile
from utils.mob.mob_stamina import forecast_stamina
from utils.race.race_dice import get_distance_color, get_dice_rule, get_phase_from_turn
from utils.race.race_lane import calculate_lane_block_penalty
from utils.race.race_tracks import get_path_effect
from utils.skill.skill_presets import SKILLS
from utils.zone.zone_manager import get_zone_effects_from_build

BEAM_WIDTH = 12
_DYNAMIC_CONDITIONS = {
    "position_group", "distance_color", "target_distance_min", "target_distance_max",
    "front_blocked", "nearby_uma_count", "used_rush", "skill_use_count_min",
}


def expected_roll(rule, cap, floor, add_d=0, add_kh=0):
    """Approximate the expected sum of the highest dice for lane/plan scoring."""
    dice = max(1, int(rule.get("d", 1)) + int(add_d))
    base_keep = rule.get("kh")
    keep = dice if base_keep is None else max(0, min(dice, int(base_keep) + int(add_kh)))
    low = max(0, float(floor))
    high = max(low, float(cap))
    return keep * (low + (high - low) * (2 * dice - keep + 1) / (2 * (dice + 1)))


def _possible(condition, game, player, turn):
    """Check known course constraints; changing race conditions are provisional."""
    condition = condition or {}
    max_turn = int(game.get("max_turn", 1))
    phase = get_phase_from_turn(turn, max_turn)
    path = game.get("path") or []
    path_type = path[min(turn - 1, len(path) - 1)] if path else 1
    if condition.get("path_type") is not None and condition["path_type"] != path_type:
        return False
    if condition.get("style") is not None and condition["style"] != player.get("style"):
        return False
    course_values = (
        ("track", game.get("track")),
        ("distance_type", game.get("distance_type") or game.get("distance")),
    )
    for key, actual in course_values:
        if condition.get(key) is not None and str(condition[key]).lower() != str(actual).lower():
            return False
    if turn < condition.get("turn_min", 1) or turn > condition.get("turn_max", max_turn):
        return False
    if phase < condition.get("phase_min", 1) or phase > condition.get("phase_max", 4):
        return False
    if condition.get("last_turn") is True and turn != max_turn:
        return False
    if condition.get("lastspurt") is not None and (phase == 4) != condition["lastspurt"]:
        return False
    last_corner = next((i + 1 for i in range(len(path) - 1, -1, -1) if path[i] == 2), -1)
    if condition.get("last_corner") is not None and (turn == last_corner) != condition["last_corner"]:
        return False
    stats = player.get("base_race_stats") or player.get("race_profile") or {}
    return all(int(stats.get(key, 0) or 0) >= int(value) for key, value in (condition.get("base_stats_min") or {}).items())


def _effects(skill, game, player, turn):
    return [effect for effect in skill.get("effects", []) if _possible(effect.get("condition"), game, player, turn)]


def _projected_speed(game, player, turn):
    style = player.get("style", "Pace")
    stats = player.get("effective_race_stats") or {}
    race_stats = player.get("race_profile") or {}
    power = float(stats.get("effective_power", race_stats.get("power", 1))) * 1.5
    speed = float(player.get("current_max_speed", 20) or 20)
    for future_turn in range(int(game.get("turn", 1)) + 1, turn + 1):
        phase = get_phase_from_turn(future_turn, int(game.get("max_turn", 1)))
        phase_key = "last_spurt" if phase == 4 else "late" if phase == 3 else "mid"
        limit = MAX_SPEED_PHASE[style][phase_key] + float(stats.get("effective_speed", race_stats.get("speed", 0))) + float(player.get("zone_speed_cap_bonus", 0) or 0)
        speed = min(limit, speed + .3 + ACCELERATION_SCALE[style][phase - 1] * power)
    return speed


def _action_value(game, player, turn, rule, effects, zone, stamina_by_turn=None):
    """Estimate score gain, including dice/cap synergy and acceleration phase."""
    path = game.get("path") or []
    path_type = path[min(turn - 1, len(path) - 1)] if path else 1
    path_effect = get_path_effect(path_type, dict(player), player.get("race_profile") or {})
    speed = _projected_speed(game, player, turn)
    current_turn = turn == int(game.get("turn", 1))
    pending_cap = float(player.get("next_roll_cap_bonus", 0) or 0) if current_turn else 0
    pending_floor = float(player.get("next_roll_floor_bonus", 0) or 0) if current_turn else 0
    pending_d = int(player.get("next_roll_add_d", 0) or 0) if current_turn else 0
    pending_kh = int(player.get("next_roll_add_kh", 0) or 0) if current_turn else 0
    cap = speed + pending_cap + path_effect["extra_max_from_wit"] - path_effect["reduce_dice_value"]
    floor = int(cap * 0.25) + pending_floor + path_effect["extra_floor_from_wit"]
    add_d = add_kh = cap_bonus = floor_bonus = flat = 0.0
    accel = recovery = race_bonus = block_reduction = 0.0
    for effect in effects:
        kind = effect.get("type")
        value = float(effect.get("value", 0) or 0)
        if kind == "add_d":
            add_d += value
        elif kind == "add_kh":
            add_kh += value
        elif kind == "add_dkh":
            add_d += value
            add_kh += value
        elif kind == "modify_roll_cap":
            cap_bonus += value
        elif kind == "modify_roll_floor":
            floor_bonus += value
        elif kind in {"cap_floor", "modify_roll_cap_floor"}:
            cap_bonus += float(effect.get("cap", value))
            floor_bonus += float(effect.get("floor", value))
        elif kind in {"modify_velocity", "modify_selected_die"}:
            flat += value
        elif kind == "modify_current_speed":
            accel += value
        elif kind in {"recover_stamina", "self_heal_stamina"}:
            recovery += value
        elif kind == "add_race_velocity_bonus":
            race_bonus += value
        elif kind == "reduce_block_penalty":
            block_reduction += value
        elif kind in {"reduce_stamina", "modify_enemy_velocity", "slow_enemy", "apply_debuff_next_turn"}:
            flat += abs(value) * 8
    skill_cap_floor = max(0, cap_bonus) + max(0, floor_bonus)
    if zone:
        add_d += zone["add_dkh"]
        add_kh += zone["add_dkh"]
        cap_bonus += zone["cap"]
        floor_bonus += zone["floor"]
        flat += zone["flat"]
        accel += zone["modify_current_speed"]
        recovery += zone["self_heal_stamina"] / 10
        block_reduction += zone["reduce_block_penalty"] / 10
    baseline = expected_roll(rule, cap, floor, pending_d, pending_kh)
    adjusted = expected_roll(rule, cap + cap_bonus, floor + floor_bonus + int((cap + cap_bonus) * .25) - int(cap * .25), pending_d + add_d, pending_kh + add_kh)
    dice = int(rule.get("d", 1) + pending_d + add_d)
    kept = max(1, dice if rule.get("kh") is None else min(dice, int(rule["kh"] + pending_kh + add_kh)))
    remaining = max(1, int(game.get("max_turn", 1)) - turn + 1)
    phase = get_phase_from_turn(turn, int(game.get("max_turn", 1)))
    style = player.get("style", "Pace")
    power = (player.get("effective_race_stats") or {}).get("effective_power", (player.get("race_profile") or {}).get("power", 1))
    stats = player.get("effective_race_stats") or {}
    race_stats = player.get("race_profile") or {}
    phase_key = "last_spurt" if phase == 4 else "late" if phase == 3 else "mid"
    speed_limit = MAX_SPEED_PHASE[style][phase_key] + float(stats.get("effective_speed", race_stats.get("speed", 0))) + float(player.get("zone_speed_cap_bonus", 0) or 0) + (zone["race_speed"] if zone else 0)
    acceleration = min(max(0, speed_limit - speed), 0.3 + ACCELERATION_SCALE[style][phase - 1] * float(power) * 1.5 * accel) if accel else 0
    if turn == game.get("turn") and player.get("current_lane") in (game.get("wet_lanes") or []):
        acceleration *= .5
    projected_stamina = (stamina_by_turn or {}).get(turn, player.get("stamina_left", 0))
    missing = max(0, 1 - projected_stamina / max(1, float(player.get("max_stamina", 1) or 1)))
    roll_gain = adjusted - baseline + flat
    if current_turn and game.get("race_mode", "discord_classic") != "web_timing":
        user_id = next((pid for pid, candidate in game.get("players", {}).items() if candidate is player), None)
        if user_id is not None:
            scores = game.get("turn_snapshot_scores") or {}
            players = {pid: {**candidate, "score": scores.get(pid, candidate.get("score", 0))} for pid, candidate in game["players"].items()}
            me = players[user_id]
            stats_bonus = sum(float((player.get("race_profile") or {}).get(k, 1) or 1) * factor for k, factor in (("speed", 2), ("power", 1), ("stamina", 1)))
            base_total = max(0, int(baseline + stats_bonus))
            base_reduction = max(0, int(player.get("next_roll_block_reduction", 0) or 0))
            before = calculate_lane_block_penalty(me, players, base_total, int(power), base_reduction)["final_score"]
            after = calculate_lane_block_penalty(me, players, max(0, int(base_total + roll_gain)), int(power), base_reduction + int(block_reduction))["final_score"]
            roll_gain = after - before
    value = roll_gain + acceleration * kept * min(remaining, 4) * .8
    # Healing beyond the predicted missing stamina has no practical value.
    value += min(missing, max(0, recovery) * .1) * 200
    value += sum(max(0, race_bonus - offset) for offset in range(remaining))
    if zone:
        value += zone["race_speed"] * kept * min(remaining, 4) * .4
        # Prefer combining Zone cap/floor with other per-die bonuses when
        # comparable rolls offer the same number of selected dice.
        other_cap_floor = skill_cap_floor + max(0, pending_cap) + max(0, pending_floor) + max(0, path_effect["extra_max_from_wit"]) + max(0, path_effect["extra_floor_from_wit"])
        value += (zone["cap"] + zone["floor"]) * min(other_cap_floor, 30) * kept * .05
    return max(0.0, value)


def build_race_plan(game, user_id, usable_skills):
    """Beam search the remaining turns, respecting mana, cooldowns and Zone use."""
    if not (game.get("game_rules") or {}).get("AllowSkill", True):
        return {}
    player = game["players"][user_id]
    start = int(game.get("turn", 1))
    end = int(game.get("max_turn", 1))
    profile = get_ai_profile(player)
    no_debuff = bool((game.get("game_rules") or {}).get("NoDebuff"))
    equipped = list(dict.fromkeys(sid for sid in (player.get("skills") or {}).values() if sid in SKILLS and SKILLS[sid].get("activation") != "passive" and not (no_debuff and "debuff" in SKILLS[sid].get("tags", []))))
    current = dict(usable_skills)
    stamina_by_turn = {step["turn"]: step["stamina_before"] for step in forecast_stamina(game, user_id)["turns"]}
    scores = game.get("turn_snapshot_scores") or {pid: p.get("score", 0) for pid, p in game["players"].items()}
    color, _ = get_distance_color(user_id, scores, player.get("active_effects") or [], game["players"])
    zone = get_zone_effects_from_build((player.get("zone") or {}).get("build", {}))
    zone_available = bool(player.get("zone_left", 0) and player.get("zone") and (game.get("game_rules") or {}).get("AllowSkill", True))
    regen = int((player.get("effective_race_stats") or {}).get("effective_wit_gain", 10))
    initial_cd = tuple(max(0, int((player.get("skill_cooldowns") or {}).get(sid, 0))) for sid in equipped)
    # Each state: score, mana, cooldowns, zone available, skill use count, plan.
    states = [(0.0, int(player.get("wit_mana", 0) or 0), initial_cd, zone_available, int(player.get("skill_use_count", 0) or 0), {})]
    candidates = {}
    for turn in range(start, end + 1):
        phase = get_phase_from_turn(turn, end)
        rule = get_dice_rule(player.get("style", "Pace"), color, phase)
        available = []
        for index, sid in enumerate(equipped):
            skill = current.get(sid) if turn == start else SKILLS[sid]
            if skill is None or not _possible(skill.get("trigger"), game, player, turn):
                continue
            available.append((index, sid, skill, _effects(skill, game, player, turn)))
        actions = []
        for size in range(min(profile["max_skills"], len(available)) + 1):
            for combo in combinations(available, size):
                effects = [effect for item in combo for effect in item[3]]
                cost = sum(int(item[2].get("cost", 0) or 0) for item in combo)
                dynamic = any(set(item[2].get("trigger") or {}) & _DYNAMIC_CONDITIONS for item in combo)
                factor = .8 if turn > start and dynamic else 1.0
                for use_zone in ((False, True) if zone_available else (False,)):
                    value = _action_value(game, player, turn, rule, effects, zone if use_zone else None, stamina_by_turn) * factor
                    actions.append((combo, cost, use_zone, value))
        candidates[turn] = actions
    # The optimistic bound keeps resource-saving plans in the beam even when
    # an immediately available action has a large short-term value.
    future_best = {}
    future_zone = {}
    for turn in range(start, end + 1):
        future_best[turn] = [max((a[3] for t in range(turn + 1, end + 1) for a in candidates[t] if len(a[0]) == 1 and a[0][0][0] == i and not a[2]), default=0) for i in range(len(equipped))]
        future_zone[turn] = max((a[3] for t in range(turn + 1, end + 1) for a in candidates[t] if not a[0] and a[2]), default=0)
    for turn in range(start, end + 1):
        next_states = []
        for score, mana, cooldowns, zone_left, use_count, plan in states:
            for combo, cost, use_zone, value in candidates[turn]:
                if cost > mana or (use_zone and not zone_left) or any(cooldowns[item[0]] > 0 for item in combo):
                    continue
                if any(int(item[2].get("trigger", {}).get("skill_use_count_min", 0) or 0) > use_count for item in combo):
                    continue
                new_cd = list(cooldowns)
                for index, sid, skill, _ in combo:
                    new_cd[index] = int(skill.get("cooldown", 0) or 0)
                new_cd = tuple(max(0, cd - 1) for cd in new_cd)
                new_plan = {**plan, turn: {"skills": [item[1] for item in combo], "zone": use_zone}}
                new_score = score + value
                potential = sum(future_best[turn][i] for i, cd in enumerate(new_cd) if turn + cd < end)
                if zone_left and not use_zone:
                    potential += future_zone[turn]
                next_states.append((new_score + potential, new_score, mana - cost + regen, new_cd, zone_left and not use_zone, use_count + len(combo), new_plan))
        next_states.sort(key=lambda state: state[0], reverse=True)
        states = [(s, m, cd, z, count, plan) for _, s, m, cd, z, count, plan in next_states[:BEAM_WIDTH]]
    return max(states, key=lambda state: state[0])[5] if states else {}
