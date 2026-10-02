"""Race presets for Kokura."""

from utils.race.race_preset_constants import G2_RACE_THUMBNAIL, G3_RACE_THUMBNAIL

TRACK_PATHS = {'KOKURA_2000': [1, 1, 1, 3, 2, 2, 1, 1, 2, 2, 1, 1],
 'KOKURA_1800': [1, 3, 2, 1, 2, 2, 1, 1],
 'KOKURA_1200': [4, 1, 1, 1, 2, 2, 1, 1]}


RACES = {
    'KokuraKinen': {
        'name': 'Kokura Kinen (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Kokura', 'surface': 'turf', 'distance_m': 2000, 'direction': 'right'},
        'path': TRACK_PATHS['KOKURA_2000'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Kokura Kinen (GIII) ที่สนาม Kokura',

    },
    'KokuraHimbaStakes': {
        'name': 'Kokura Himba Stakes (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Kokura', 'surface': 'turf', 'distance_m': 2000, 'direction': 'right'},
        'path': TRACK_PATHS['KOKURA_2000'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Kokura Himba Stakes (GIII) ที่สนาม Kokura',

    },
    'KokuraDaishoten': {
        'name': 'Kokura Daishoten (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Kokura', 'surface': 'turf', 'distance_m': 1800, 'direction': 'right'},
        'path': TRACK_PATHS['KOKURA_1800'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Kokura Daishoten (GIII) ที่สนาม Kokura',

    },
    'KitakyushuKinen': {
        'name': 'Kitakyushu Kinen (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Kokura', 'surface': 'turf', 'distance_m': 1200, 'direction': 'right'},
        'path': TRACK_PATHS['KOKURA_1200'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Kitakyushu Kinen (GIII) ที่สนาม Kokura',

    },
}
