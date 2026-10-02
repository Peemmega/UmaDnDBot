"""Race presets for Sapporo."""

from utils.race.race_preset_constants import G2_RACE_THUMBNAIL, G3_RACE_THUMBNAIL

TRACK_PATHS = {'SAPPORO_2000': [1, 1, 2, 2, 2, 1, 1, 2, 2, 2, 1, 1],
 'SAPPORO_1800': [1, 2, 2, 1, 1, 2, 2, 1],
 'SAPPORO_1700': [1, 2, 2, 1, 1, 2, 2, 1],
 'SAPPORO_1200': [1, 1, 1, 2, 2, 2, 1, 1]}


RACES = {
    'SapporoKinen': {
        'name': 'Sapporo Kinen (GII)',
        'thumnail': G2_RACE_THUMBNAIL,
        'image': G2_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Sapporo', 'surface': 'turf', 'distance_m': 2000, 'direction': 'right'},
        'path': TRACK_PATHS['SAPPORO_2000'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Sapporo Kinen (GII) ที่สนาม Sapporo',

    },
    'QueenStakes': {
        'name': 'Queen Stakes (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Sapporo', 'surface': 'turf', 'distance_m': 1800, 'direction': 'right'},
        'path': TRACK_PATHS['SAPPORO_1800'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Queen Stakes (GIII) ที่สนาม Sapporo',

    },
    'ElmStakes': {
        'name': 'Elm Stakes (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'dirt',
        'course': {'venue': 'Sapporo', 'surface': 'dirt', 'distance_m': 1700, 'direction': 'right'},
        'path': TRACK_PATHS['SAPPORO_1700'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Elm Stakes (GIII) ที่สนาม Sapporo',

    },
    'KeenelandCup': {
        'name': 'Keeneland Cup (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Sapporo', 'surface': 'turf', 'distance_m': 1200, 'direction': 'right'},
        'path': TRACK_PATHS['SAPPORO_1200'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Keeneland Cup (GIII) ที่สนาม Sapporo',

    },
    'SapporoNisaiStakes': {
        'name': 'Sapporo Nisai Stakes (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Sapporo', 'surface': 'turf', 'distance_m': 1800, 'direction': 'right'},
        'path': TRACK_PATHS['SAPPORO_1800'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Sapporo Nisai Stakes (GIII) ที่สนาม Sapporo',

    },
}
