import io

import discord

from utils.race.rank_display import gold_range_marker


def build_race_log_text(game: dict, ranked_players, markdown: bool = True) -> str:
    rank_lines = []

    for index, (user_id, info) in enumerate(ranked_players, start=1):
        name = (
            info.get("display_name")
            or info.get("username")
            or str(user_id)
        )

        marker = gold_range_marker(user_id, info, ranked_players)
        if markdown:
            rank_lines.append(
                f"**{index}. {name}{marker}** | {info.get('style')} | Score: **{info.get('score', 0)}**"
            )
        else:
            rank_lines.append(
                f"{index}. {name}{marker} | {info.get('style')} | Score: {info.get('score', 0)}"
            )

    turn_logs = game.get("turn_score_logs", [])
    player_logs = {}

    for log in turn_logs:
        player_name = log["name"]

        if player_name not in player_logs:
            player_logs[player_name] = {
                "style": log.get("style"),
                "logs": []
            }

        player_logs[player_name]["logs"].append(log)

    log_lines = []

    for player_name, data in player_logs.items():
        style = data["style"]
        header = f"\n**{player_name}** ({style})" if markdown else f"\n{player_name} ({style})"
        log_lines.append(header)

        for item in data["logs"]:
            detail_parts = []
            roll = item.get("roll") or {}

            if roll:
                phase = roll.get("phase")
                color = roll.get("distance_color")
                rule = roll.get("rule")
                detail_parts.append(f"P{phase} {color} {rule}")

            skills = item.get("skills") or []
            if skills:
                skill_ids = ", ".join(skill.get("id", "?") for skill in skills)
                detail_parts.append(f"skills: {skill_ids}")

            detail = f" | {' | '.join(detail_parts)}" if detail_parts else ""
            position = item.get("position")
            position_text = f" | Position: #{position}" if position else ""
            log_lines.append(
                f"{item['turn']} {item['score_after']} (+{item['gain']}){position_text}{detail}"
            )

    action_lines = []
    for action in game.get("race_action_logs", []):
        target = f" -> {action['target_name']}" if action.get("target_name") else ""
        details = action.get("details") or {}
        summary = details.get("summary")
        summary_text = f" | {summary}" if summary else ""
        action_lines.append(
            f"Turn {action.get('turn', 0)}: {action.get('player_name')} used "
            f"{action.get('action_type')}{target}{summary_text}"
        )

    if markdown:
        description = (
            f"สนาม: **{game.get('stage_name', 'Unknown')}**\n\n"
            f"🏆 **อันดับสุดท้าย**\n"
            + "\n".join(rank_lines)
            + "\n\n📜 **Turn Score Log**\n"
            + "\n".join(log_lines)
        )
    else:
        description = (
            f"สนาม: {game.get('stage_name', 'Unknown')}\n\n"
            f"อันดับสุดท้าย\n"
            + "\n".join(rank_lines)
            + "\n\nTurn Score Log\n"
            + "\n".join(log_lines)
        )

    if action_lines:
        action_label = "\n\nâš¡ **Race Actions**\n" if markdown else "\n\nRace Actions\n"
        description += action_label + "\n".join(action_lines)

    if markdown and len(description) > 3900:
        description = description[:3900] + "\n...log ยาวเกินไป ถูกตัดบางส่วน"

    return description


def build_race_log_embed(game: dict, ranked_players):
    return discord.Embed(
        title="📘 Race Result Log",
        description=build_race_log_text(game, ranked_players, markdown=True),
        color=discord.Color.blue(),
    )


def build_race_log_file(game: dict, ranked_players, filename: str = "race_result_log.txt"):
    content = build_race_log_text(game, ranked_players, markdown=False)
    buffer = io.BytesIO(content.encode("utf-8"))
    return discord.File(buffer, filename=filename)
