def build_single_wit_regen_text(game_player: dict) -> str:
    effective_stats = game_player.get("effective_race_stats") or {}
    regen = int(effective_stats.get("effective_wit_gain", 10))
    current_mana = game_player.get("wit_mana", 0)
    return f"{current_mana} → {current_mana + regen}"
