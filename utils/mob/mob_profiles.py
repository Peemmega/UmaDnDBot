"""Mob AI profile configuration independent of decision strategies."""

AI_LEVEL_CONFIG = {
    1: {"max_skills": 1, "min_combo_score": 75, "lane_candidates": 4, "simulation_samples": 0},
    2: {"max_skills": 1, "min_combo_score": 65, "lane_candidates": 3, "simulation_samples": 0},
    3: {"max_skills": 2, "min_combo_score": 55, "lane_candidates": 2, "simulation_samples": 0},
    4: {"max_skills": 2, "min_combo_score": 50, "lane_candidates": 2, "simulation_samples": 12},
    5: {"max_skills": 2, "min_combo_score": 45, "lane_candidates": 1, "simulation_samples": 24},
    6: {"max_skills": 3, "min_combo_score": 42, "lane_candidates": 1, "simulation_samples": 40},
    7: {"max_skills": 3, "min_combo_score": 38, "lane_candidates": 1, "simulation_samples": 60},
    8: {"max_skills": 3, "min_combo_score": 35, "lane_candidates": 1, "simulation_samples": 80},
}


def get_ai_profile(player: dict) -> dict:
    preset_key = str(player.get("mob_preset_key", "") or "").strip().lower()
    if player.get("is_mob") and not preset_key.startswith("rookie_"):
        return {"level": 8, **AI_LEVEL_CONFIG[8]}
    level = max(1, min(int(player.get("ai_level", player.get("mob_level", 1)) or 1), 8))
    return {"level": level, **AI_LEVEL_CONFIG[level]}
