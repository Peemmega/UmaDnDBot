"""Race presets for Hakodate."""

from utils.race.race_preset_constants import G2_RACE_THUMBNAIL, G3_RACE_THUMBNAIL

TRACK_PATHS = {'CUSTOM_HAKODATEJUNIORSTAKES': [3, 1, 1, 2, 2, 2, 1, 1],
 'HAKODATE_1200': [2, 1, 1, 1, 2, 2, 1, 1],
 'HAKODATE_2000': [1, 1, 3, 2, 2, 3, 1, 1, 2, 2, 1, 1]}


RACES = {
    'HakodateJuniorStakes': {
        'name': 'Hakodate Junior Stakes (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': 'https://media.discordapp.net/attachments/1494730857259471030/1502922265770070056/10202.png?ex=6a0178ef&is=6a00276f&hm=939624812ce640e97d8fc466c9bec8d96c99aea83d9680d4d4e86cdc534d519a&=&format=webp&quality=lossless&width=1370&height=755',
        'track': 'turf',
        'course': {'venue': 'Hakodate', 'surface': 'turf', 'distance_m': 1200, 'course_id': 1, 'direction': 'right'},
        'path': TRACK_PATHS['CUSTOM_HAKODATEJUNIORSTAKES'],
        'fans': {'required': 350, 'reward_first': 3100},
        'story': 'GIII ฤดูร้อนสำหรับสาวม้ารุ่น Junior เปิดโอกาสให้ดาวรุ่งแจ้งเกิดที่ Hakodate.',

    },
    'HakodateSprintStakes': {
        'name': 'Hakodate Sprint Stakes (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Hakodate', 'surface': 'turf', 'distance_m': 1200, 'direction': 'right'},
        'path': TRACK_PATHS['HAKODATE_1200'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Hakodate Sprint Stakes (GIII) ที่สนาม Hakodate',

    },
    'HakodateKinen': {
        'name': 'Hakodate Kinen (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Hakodate', 'surface': 'turf', 'distance_m': 2000, 'direction': 'right'},
        'path': TRACK_PATHS['HAKODATE_2000'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Hakodate Kinen (GIII) ที่สนาม Hakodate',

    },
}
