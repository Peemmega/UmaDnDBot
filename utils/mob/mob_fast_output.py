"""Text output used when compact Mob rendering is enabled."""

from __future__ import annotations

import math

from utils.race.result_display import format_bonus_display, format_stamina_line


def build_mob_fast_roll_text(
    *,
    game_player: dict,
    result: dict,
    payload: dict,
    path_label: str,
) -> str:
    """Mirror the important race-dice card details without creating an image."""
    name = game_player.get("username") or game_player.get("display_name") or "Mob"
    display = str(result.get("display") or "-").strip()
    bonus = format_bonus_display(result.get("bonus_display", "-"), block_label="BLOCK")
    speed = math.floor(float(game_player.get("current_max_speed", 0) or 0))
    lane = int(result.get("current_lane", game_player.get("current_lane", 1)) or 1)
    color = result.get("distance_color") or "White"
    gained = int(result.get("total", 0) or 0)
    score = int(payload.get("new_score", game_player.get("score", 0)) or 0)
    stamina_note = format_stamina_line(
        payload.get("stamina_note") or "-",
        drafting_active=bool(result.get("drafting_active", game_player.get("drafting_active", False))),
    )

    lines = [
        f"🤖 **{name}**",
        f"🎲 {display}",
        f"🏇 Speed {speed} | {path_label} | {color} | Lane {lane}",
    ]
    if bonus != "-":
        lines.append(f"✨ โบนัส: {bonus}")
    lines.extend((
        f"❤️ Stamina: {stamina_note}",
        f"🏁 ได้คะแนน **+{gained}** | คะแนนรวม **{score}**",
    ))
    return "\n".join(lines)
