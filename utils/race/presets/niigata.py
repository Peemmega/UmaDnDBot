"""Race presets for Niigata."""

from utils.race.race_preset_constants import G2_RACE_THUMBNAIL, G3_RACE_THUMBNAIL

TRACK_PATHS = {'NIIGATA_1600': [1, 3, 4, 2, 2, 1, 1, 1],
 'NIIGATA_2000': [1, 1, 1, 1, 3, 1, 4, 2, 2, 1, 1, 1],
 'NIIGATA_1000': [3, 1, 4, 1, 1, 1, 1, 1],
 'NIIGATA_1800': [1, 2, 2, 1, 1, 2, 2, 1]}


RACES = {
    'NiigataJuniorStakes': {
        'name': 'Niigata Junior Stakes (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': 'https://media.discordapp.net/attachments/1494730857259471030/1502921936437645352/10304.png?ex=6a0178a0&is=6a002720&hm=a3e87de431da172dde53be441bde97c234caa3814e7f5bd4223380c05366f3a3&=&format=webp&quality=lossless&width=1482&height=735',
        'track': 'turf',
        'course': {'venue': 'Niigata', 'surface': 'turf', 'distance_m': 1600, 'course_id': 3, 'direction': 'left'},
        'path': TRACK_PATHS['NIIGATA_1600'],
        'fans': {'required': 350, 'reward_first': 3100},
        'story': 'GIII สำหรับสาวม้ารุ่น Junior บนระยะไมล์ เป็นด่านสร้างชื่อช่วงฤดูร้อน.',

    },
    'NiigataDaishoten': {
        'name': 'Niigata Daishoten (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Niigata', 'surface': 'turf', 'distance_m': 2000, 'direction': 'left'},
        'path': TRACK_PATHS['NIIGATA_2000'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Niigata Daishoten (GIII) ที่สนาม Niigata',

    },
    'SekiyaKinen': {
        'name': 'Sekiya Kinen (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Niigata', 'surface': 'turf', 'distance_m': 1600, 'direction': 'left'},
        'path': TRACK_PATHS['NIIGATA_1600'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Sekiya Kinen (GIII) ที่สนาม Niigata',

    },
    'IbisSummerDash': {
        'name': 'Ibis Summer Dash (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Niigata', 'surface': 'turf', 'distance_m': 1000, 'direction': 'straight'},
        'path': TRACK_PATHS['NIIGATA_1000'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Ibis Summer Dash (GIII) ที่สนาม Niigata',

    },
    'LeopardStakes': {
        'name': 'Leopard Stakes (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'dirt',
        'course': {'venue': 'Niigata', 'surface': 'dirt', 'distance_m': 1800, 'direction': 'left'},
        'path': TRACK_PATHS['NIIGATA_1800'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Leopard Stakes (GIII) ที่สนาม Niigata',

    },
    'NiigataKinen': {
        'name': 'Niigata Kinen (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Niigata', 'surface': 'turf', 'distance_m': 2000, 'direction': 'left'},
        'path': TRACK_PATHS['NIIGATA_2000'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Niigata Kinen (GIII) ที่สนาม Niigata',

    },
}
