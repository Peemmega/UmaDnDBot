"""Race presets for Special."""

from utils.race.race_preset_constants import G2_RACE_THUMBNAIL, G3_RACE_THUMBNAIL

TRACK_PATHS = {'CUSTOM_DEBUT': [1, 3, 1, 2, 1, 4, 1, 1]}


RACES = {
    'Debut': {
        'name': 'Debut',
        'track': 'Turf',
        'thumnail': 'https://media.discordapp.net/attachments/1494730857259471030/1496520361968406598/thum_race_rt_000_9002_00.png?ex=69ed7a72&is=69ec28f2&hm=8306829b74f79dcfd3a6f7b65cef14fdd6c96dfa0f5d614b106e4ba11efa8c39&=&format=webp&quality=lossless&width=192&height=96',
        'image': 'https://media.discordapp.net/attachments/1494730857259471030/1496520362337243336/uma-musume-pretty-derby.gif?ex=69ea2eb2&is=69e8dd32&hm=7768738070afad1ade85f8cf04f2d87cf71edb46ccb86d127fb0dc608252892f&=&width=747&height=420',
        'auto_mobs': ['rookie_front',
 'rookie_pace',
 'rookie_late',
 'rookie_end',
 'rookie_alt_front',
 'rookie_alt_pace',
 'rookie_alt_late',
 'rookie_alt_end'],
        'path': TRACK_PATHS['CUSTOM_DEBUT'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Debut ที่สนาม Special',
        'course': {'venue': 'Special', 'surface': 'Turf', 'distance_m': 1600},

    },
}
