"""Race presets for Morioka."""

from utils.race.race_preset_constants import G2_RACE_THUMBNAIL, G3_RACE_THUMBNAIL

TRACK_PATHS = {'MORIOKA_1600': [1, 1, 4, 2, 2, 3, 1, 1]}


RACES = {
    'MCNambuHai': {
        'name': 'M.C. Nambu Hai (GI)',
        'thumnail': 'https://media.discordapp.net/attachments/1494730857259471030/1542862288254537768/10611.png?ex=6a92c5fa&is=6a91747a&hm=907feb0422a55f40ccefcd726036c937aa689f240661b9e31f73648fc21d2abc&=&format=webp&quality=lossless',
        'image': 'https://media.discordapp.net/attachments/1494730857259471030/1542862287910608958/1110.png?ex=6a92c5fa&is=6a91747a&hm=ed2e278859208eb2b6280220df32bdd27825f766b6d52b0bc6d0c57724f1f1be&=&format=webp&quality=lossless',
        'track': 'dirt',
        'course': {'venue': 'Morioka', 'surface': 'dirt', 'distance_m': 1600, 'course_id': 1, 'direction': 'left'},
        'path': TRACK_PATHS['MORIOKA_1600'],
        'fans': {'required': 12000, 'reward_first': 6000},
        'story': 'ไมล์สนามดินทางเรียบ เร็วก็พอแล้วเนาะ',

    },
}
