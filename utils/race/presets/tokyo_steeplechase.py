"""Race presets for Tokyo (Steeplechase)."""

from utils.race.race_preset_constants import G2_RACE_THUMBNAIL, G3_RACE_THUMBNAIL

TRACK_PATHS = {'CUSTOM_DIAMONDSTAKES': [1, 3, 4, 2, 2, 1, 1, 1, 1, 3, 4, 2, 2, 1, 1, 1]}


RACES = {
    'DiamondStakes': {
        'name': 'Diamond Stakes (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': 'https://media.discordapp.net/attachments/1494730857259471030/1502921936437645352/10304.png?ex=6a0178a0&is=6a002720&hm=a3e87de431da172dde53be441bde97c234caa3814e7f5bd4223380c05366f3a3&=&format=webp&quality=lossless&width=1482&height=735',
        'track': 'turf',
        'course': {'venue': 'Tokyo (Steeplechase)',
 'surface': 'turf',
 'distance_m': 3400,
 'course_id': 1,
 'direction': 'left'},
        'path': TRACK_PATHS['CUSTOM_DIAMONDSTAKES'],
        'fans': {'required': 1500, 'reward_first': 4100},
        'story': 'GIII ระยะไกล 3,400 เมตรของ Tokyo สำหรับสาวม้ารุ่น Senior สายความอึด.',

    },
}
