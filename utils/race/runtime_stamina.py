from __future__ import annotations

RACE_RUNTIME_STAMINA_SCALE = 100
LEGACY_RUNTIME_STAMINA_BASE = 8


def runtime_stamina_from_stat(stat: int) -> int:
    return max(0, int(stat)) * RACE_RUNTIME_STAMINA_SCALE


def runtime_stamina_effect_units(amount: int) -> int:
    return int(amount) * RACE_RUNTIME_STAMINA_SCALE


def _resolve_stamina_stat(player: dict) -> int:
    race_profile = player.get("race_profile") or {}
    return int(player.get("stamina_stat", race_profile.get("stamina", 0)) or 0)


def _resolve_expected_max(player: dict) -> int:
    return runtime_stamina_from_stat(_resolve_stamina_stat(player))


def _calculate_percent(current_stamina: int, max_stamina: int) -> int:
    if max_stamina <= 0:
        return 0
    return int(round((current_stamina / max_stamina) * 100))


def set_runtime_stamina(
    player: dict,
    stamina_stat: int,
    current_stamina: int | None = None,
) -> dict:
    max_stamina = runtime_stamina_from_stat(stamina_stat)
    if current_stamina is None:
        current_stamina = max_stamina

    current_stamina = max(0, min(int(current_stamina), max_stamina))
    player["stamina_stat"] = int(stamina_stat)
    player["max_stamina"] = max_stamina
    player["stamina_left"] = current_stamina
    player["current_stamina"] = current_stamina
    player["stamina_percent"] = _calculate_percent(current_stamina, max_stamina)
    return get_runtime_stamina_snapshot(player)


def sync_runtime_stamina(player: dict) -> dict:
    stamina_stat = _resolve_stamina_stat(player)
    expected_max = _resolve_expected_max(player)
    stored_max = int(player.get("max_stamina", 0) or 0)
    current_stamina = int(player.get("stamina_left", 0) or 0)

    if expected_max <= 0:
        return set_runtime_stamina(player, stamina_stat, 0)

    if stored_max <= 0:
        legacy_max = LEGACY_RUNTIME_STAMINA_BASE + stamina_stat
        if 0 < current_stamina <= legacy_max and legacy_max > 0:
            current_stamina = int(round((current_stamina / legacy_max) * expected_max))
        elif current_stamina <= 0:
            current_stamina = expected_max
        stored_max = expected_max
    elif stored_max != expected_max:
        current_stamina = int(round((current_stamina / stored_max) * expected_max))
        stored_max = expected_max

    current_stamina = max(0, min(current_stamina, stored_max))
    return set_runtime_stamina(player, stamina_stat, current_stamina)


def apply_runtime_stamina_delta(player: dict, delta: int) -> dict:
    snapshot = sync_runtime_stamina(player)
    return set_runtime_stamina(
        player,
        snapshot["stamina_stat"],
        snapshot["current_stamina"] + int(delta),
    )


def get_runtime_stamina_snapshot(player: dict) -> dict:
    if int(player.get("max_stamina", 0) or 0) <= 0:
        snapshot = sync_runtime_stamina(player)
    else:
        snapshot = {
            "stamina_stat": int(player.get("stamina_stat", 0) or 0),
            "current_stamina": int(player.get("stamina_left", 0) or 0),
            "max_stamina": int(player.get("max_stamina", 0) or 0),
        }
    snapshot["stamina_percent"] = _calculate_percent(
        snapshot["current_stamina"],
        snapshot["max_stamina"],
    )
    player["current_stamina"] = snapshot["current_stamina"]
    player["stamina_percent"] = snapshot["stamina_percent"]
    return snapshot


def format_runtime_stamina(player: dict) -> str:
    snapshot = get_runtime_stamina_snapshot(player)
    return f"{snapshot['current_stamina']} / {snapshot['max_stamina']}"


def build_runtime_stamina_note(
    player: dict,
    *,
    gain: int = 0,
    drain: int = 0,
    penalty: bool = False,
    uphill: bool = False,
) -> str:
    lines = [f"Stamina: {format_runtime_stamina(player)}"]
    if gain > 0:
        lines.append(f"Gain: +{int(gain)}")
    if drain > 0:
        label = "Uphill Drain" if uphill else "Drain"
        lines.append(f"{label}: -{int(drain)}")
    if penalty:
        lines.append("Penalty: -25% total")
    return "\n".join(lines)
