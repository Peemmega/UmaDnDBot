"""Race presets for Fukushima."""

from utils.race.race_preset_constants import G2_RACE_THUMBNAIL, G3_RACE_THUMBNAIL

TRACK_PATHS = {'FUKUSHIMA_1800': [1, 2, 2, 3, 1, 2, 2, 1], 'FUKUSHIMA_2000': [1, 1, 1, 2, 2, 3, 1, 1, 2, 2, 1, 1]}


RACES = {
    'FukushimaUmamusumeStakes': {
        'name': 'Fukushima Umamusume Stakes (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Fukushima', 'surface': 'turf', 'distance_m': 1800, 'direction': 'right'},
        'path': TRACK_PATHS['FUKUSHIMA_1800'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Fukushima Umamusume Stakes (GIII) ที่สนาม Fukushima',

    },
    'FukushimaHimbaStakes': {
        'name': 'Fukushima Himba Stakes (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Fukushima', 'surface': 'turf', 'distance_m': 1800, 'direction': 'right'},
        'path': TRACK_PATHS['FUKUSHIMA_1800'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Fukushima Himba Stakes (GIII) ที่สนาม Fukushima',

    },
    'RadioNikkeiSho': {
        'name': 'Radio Nikkei Sho (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Fukushima', 'surface': 'turf', 'distance_m': 1800, 'direction': 'right'},
        'path': TRACK_PATHS['FUKUSHIMA_1800'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Radio Nikkei Sho (GIII) ที่สนาม Fukushima',

    },
    'TanabataSho': {
        'name': 'Tanabata Sho (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Fukushima', 'surface': 'turf', 'distance_m': 2000, 'direction': 'right'},
        'path': TRACK_PATHS['FUKUSHIMA_2000'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Tanabata Sho (GIII) ที่สนาม Fukushima',

    },
    'FukushimaKinen': {
        'name': 'Fukushima Kinen (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Fukushima', 'surface': 'turf', 'distance_m': 2000, 'direction': 'right'},
        'path': TRACK_PATHS['FUKUSHIMA_2000'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Fukushima Kinen (GIII) ที่สนาม Fukushima',

    },
}
