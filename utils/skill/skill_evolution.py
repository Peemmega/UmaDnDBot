"""Skill upgrade relationships that cannot be equipped together.

Keys are upgraded skill IDs; values are the common skill IDs they replace.
"""

SKILL_UPGRADES_FROM = {
    "acc_001": "acc_012",  # Encroaching Shadow replaces Straightaway Spurt.
    "acc_003": "acc_018",  # On Your Left! replaces Slick Surge.
    "acc_004": "acc_015",  # Turbo Sprint replaces Sprinting Gear.
    "acc_006": "acc_010",  # No Stopping Me! replaces Nimble Navigator.
    "acc_007": "acc_017",  # Neck and Neck replaces Head-On.
    "acc_009": "acc_019",  # Unrestrained replaces Final Push.
    "acc_014": "acc_013",  # Taking the Lead replaces Early Lead.
    "debuff_002": "debuff_011",  # Stamina Siphon replaces Stamina Eater.
    "debuff_003": "debuff_008",  # Dominator replaces Tether.
    "debuff_009": "debuff_010",  # Adored by All replaces Intimidate.
    "rec_001": "rec_010",  # Swinging Maestro replaces Corner Recovery.
    "rec_002": "rec_014",  # Go-Home Specialist replaces After-School Stroll.
    "rec_005": "rec_011",  # Breath of Fresh Air replaces Straightaway Recovery.
    "rec_008": "rec_015",  # Restless replaces Moxie.
    "rec_012": "rec_013",  # Gourmand replaces Hydrate.
    "utl_004": "utl_003",  # Lane Legerdemain replaces Go with the Flow.
    "vel_001": "vel_023",  # Professor of Curvature replaces Corner Adept.
    "vel_005": "vel_028",  # Killer Tunes replaces Up-Tempo.
    "vel_006": "vel_030",  # Speed Star replaces Prepared to Pass.
    "vel_007": "vel_024",  # Beeline Burst replaces Straightaway Adept.
    "vel_010": "vel_029",  # Sturm und Drang replaces Masterful Gambit.
    "vel_011": "vel_016",  # In Body and Mind replaces Homestretch Haste.
    "vel_012": "vel_031",  # Rising Dragon replaces Outer Swell.
    "vel_017": "vel_035",  # Daring Strike replaces Early Start.
    "vel_018": "vel_032",  # Escape Artist replaces Fast-Paced.
    "vel_019": "vel_034",  # 15,000,000 CC replaces 1,500,000 CC.
    "vel_021": "vel_033",  # Unstoppable replaces On the Attack.
    "vel_037": "vel_036",  # Dauntless replaces Fearless.
}


def find_incompatible_skill_pair(skill_ids):
    equipped = {skill_id for skill_id in skill_ids if skill_id}
    for upgraded_id, base_id in SKILL_UPGRADES_FROM.items():
        if upgraded_id in equipped and base_id in equipped:
            return base_id, upgraded_id
    return None


def skill_conflict_message(pair):
    base_id, upgraded_id = pair
    return (
        f"ติดตั้ง `{upgraded_id}` พร้อมกับ `{base_id}` ไม่ได้ "
        "เพราะเป็นสกิลสายอัปเกรดเดียวกัน"
    )


def normalize_skill_slots(slots):
    """Keep the upgraded skill if an old loadout contains both versions."""
    normalized = dict(slots)
    equipped = {skill_id for skill_id in normalized.values() if skill_id}
    base_ids_to_remove = {
        base_id
        for upgraded_id, base_id in SKILL_UPGRADES_FROM.items()
        if upgraded_id in equipped and base_id in equipped
    }
    for slot, skill_id in normalized.items():
        if skill_id in base_ids_to_remove:
            normalized[slot] = None
    return normalized
