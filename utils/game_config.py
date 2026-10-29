"""Frequently adjusted gameplay limits, selected by the bot environment.

Aptitude levels map to G=1, F=2, E=3, D=4, C=5, B=6, A=7, S=8.
Changing a limit does not alter values already saved in player records.
"""

from utils.icon_presets import USING_MAIN_EMOJIS

MAIN_MAX_CORE_STAT = 8
TEST_MAX_CORE_STAT = 12
MAIN_MAX_APTITUDE_LEVEL = 3
TEST_MAX_APTITUDE_LEVEL = 8

MAX_CORE_STAT = MAIN_MAX_CORE_STAT if USING_MAIN_EMOJIS else TEST_MAX_CORE_STAT
MAX_APTITUDE_LEVEL = (
    MAIN_MAX_APTITUDE_LEVEL if USING_MAIN_EMOJIS else TEST_MAX_APTITUDE_LEVEL
)

if not 1 <= MAX_APTITUDE_LEVEL <= 8:
    raise ValueError("Aptitude level limit must be between 1 (G) and 8 (S)")
if not 1 <= MAX_CORE_STAT <= 12:
    raise ValueError("Core stat limit must be between 1 and 12")
