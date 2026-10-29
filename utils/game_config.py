"""Frequently adjusted gameplay limits, selected by the bot environment.

Aptitude levels map to G=1, F=2, E=3, D=4, C=5, B=6, A=7, S=8.
Changing a limit does not alter values already saved in player records.
"""

from utils.icon_presets import USING_MAIN_EMOJIS

MAIN_MAX_CORE_STAT = 8
TEST_MAX_CORE_STAT = 12
MAIN_MAX_APTITUDE_LEVEL = 3
TEST_MAX_APTITUDE_LEVEL = 8

# Stamina shortage reduces the run result by base percent minus Guts relief.
# Each Guts point lowers the penalty by the configured percentage points.
MAIN_STAMINA_PENALTY_BASE_PERCENT = 70
TEST_STAMINA_PENALTY_BASE_PERCENT = 70
MAIN_STAMINA_PENALTY_GUTS_REDUCTION = 2
TEST_STAMINA_PENALTY_GUTS_REDUCTION = 2

MAX_CORE_STAT = MAIN_MAX_CORE_STAT if USING_MAIN_EMOJIS else TEST_MAX_CORE_STAT
MAX_APTITUDE_LEVEL = (
    MAIN_MAX_APTITUDE_LEVEL if USING_MAIN_EMOJIS else TEST_MAX_APTITUDE_LEVEL
)
STAMINA_PENALTY_BASE_PERCENT = (
    MAIN_STAMINA_PENALTY_BASE_PERCENT
    if USING_MAIN_EMOJIS
    else TEST_STAMINA_PENALTY_BASE_PERCENT
)
STAMINA_PENALTY_GUTS_REDUCTION = (
    MAIN_STAMINA_PENALTY_GUTS_REDUCTION
    if USING_MAIN_EMOJIS
    else TEST_STAMINA_PENALTY_GUTS_REDUCTION
)

if not 1 <= MAX_APTITUDE_LEVEL <= 8:
    raise ValueError("Aptitude level limit must be between 1 (G) and 8 (S)")
if not 1 <= MAX_CORE_STAT <= 12:
    raise ValueError("Core stat limit must be between 1 and 12")
