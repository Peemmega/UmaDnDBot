"""Race presets for Funabashi."""

from utils.race.race_preset_constants import G2_RACE_THUMBNAIL, G3_RACE_THUMBNAIL

TRACK_PATHS = {'FUNABASHI_1600': [1, 2, 1, 1, 2, 2, 1, 1]}


RACES = {
    'KashiwaKinen': {
        'name': 'Kashiwa Kinen (GI)',
        'thumnail': 'https://media.discordapp.net/attachments/1494730857259471030/1542853078884155423/11402.png?ex=6a92bd66&is=6a916be6&hm=efd7d2bf7b2c22ab4efc428b2e317882b7f65d1a5ba1fb8d7a789c6cd8e23075&=&format=webp&quality=lossless',
        'image': 'https://media.discordapp.net/attachments/1494730857259471030/1542853078452277308/1109.png?ex=6a92bd66&is=6a916be6&hm=897157db4da181e5a92eb346db12b8401cc123b9dc1a61f81c2e31a0de582829&=&format=webp&quality=lossless',
        'track': 'dirt',
        'course': {'venue': 'Funabashi', 'surface': 'dirt', 'distance_m': 1600, 'course_id': 1, 'direction': 'left'},
        'path': TRACK_PATHS['FUNABASHI_1600'],
        'fans': {'required': 12000, 'reward_first': 8000},
        'story': 'ฟุนาบาชิคือที่ของความเร็ว! สายลมบนทะเลทราย!',

    },
}
