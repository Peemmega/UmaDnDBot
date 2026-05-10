def build_single_wit_regen_text(game_player: dict) -> str:
    race_profile = game_player.get("race_profile", {})
    wit_stat = race_profile.get("wit", 0)
    regen = 10 + (wit_stat * 1)
    current_mana = game_player.get("wit_mana", 0)
    return f"{current_mana} → {current_mana + regen}"
