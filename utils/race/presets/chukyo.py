"""Race presets for Chukyo."""

from utils.race.race_preset_constants import G2_RACE_THUMBNAIL, G3_RACE_THUMBNAIL

TRACK_PATHS = {'CHUKYO_1800': [1, 2, 4, 2, 2, 3, 3, 1],
 'CHUKYO_1200': [4, 1, 2, 2, 2, 3, 1, 1],
 'CUSTOM_CHUNICHISHIMBUNHAI': [3, 1, 2, 2, 2, 2, 1, 1, 4, 4, 2, 2],
 'CHUKYO_2000': [3, 1, 2, 2, 1, 3, 1, 2, 2, 3, 3, 1],
 'CHUKYO_1400': [1, 4, 1, 2, 2, 3, 1, 1],
 'CHUKYO_1600': [1, 2, 1, 3, 2, 2, 3, 1]}


RACES = {
    'ChampionsCup': {
        'name': 'Champions Cup (GI)',
        'thumnail': 'https://media.discordapp.net/attachments/1494730857259471030/1542844413523402752/10708.png?ex=6a92b554&is=6a9163d4&hm=d774373d77c48556794947a016d6564dad67e394fac94d27dc07699d162446d0&=&format=webp&quality=lossless',
        'image': 'https://media.discordapp.net/attachments/1494730857259471030/1542844413187854346/1020.png?ex=6a92b554&is=6a9163d4&hm=3831fded3b4cf3f0f174bf4a35e103ef7ac74fbf50b255693f170935b51fbd63&=&format=webp&quality=lossless',
        'track': 'dirt',
        'course': {'venue': 'Chukyo', 'surface': 'dirt', 'distance_m': 1800, 'course_id': 1, 'direction': 'left'},
        'path': TRACK_PATHS['CHUKYO_1800'],
        'fans': {'required': 12000, 'reward_first': 10000},
        'story': 'บทสถาปนาแชมป์แห่งสนามดิน',

    },
    'TakamatsunomiyaKinen': {
        'name': 'Takamatsunomiya Kinen (GI)',
        'thumnail': 'https://media.discordapp.net/attachments/1494730857259471030/1542844671049466047/10701.png?ex=6a92b592&is=6a916412&hm=61ed77d7552681b42d3e2819007abff9d8e78a7b15247c1a9f769b8a650a4521&=&format=webp&quality=lossless',
        'image': 'https://media.discordapp.net/attachments/1494730857259471030/1542844624056361001/1002.png?ex=6a92b587&is=6a916407&hm=c791ef3f5f215b1d3e096c70535774e7f21c5e18ff4229e6bda83b8340d4c996&=&format=webp&quality=lossless',
        'track': 'turf',
        'course': {'venue': 'Chukyo', 'surface': 'turf', 'distance_m': 1200, 'course_id': 1, 'direction': 'left'},
        'path': TRACK_PATHS['CHUKYO_1200'],
        'fans': {'required': 15000, 'reward_first': 13000},
        'story': '1,200 เมตร สายฟ้า ความเร็ว สายลม สปีด!!',

    },
    'ChunichiShimbunHai': {
        'name': 'Chunichi Shimbun Hai (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': 'https://media.discordapp.net/attachments/1494730857259471030/1502921350313148486/10704.png?ex=6a0766d4&is=6a061554&hm=041ec3c8ad0302885c147b70d00f9dfe0106e2a05564da81f7fb9709ea475ef9&=&format=webp&quality=lossless&width=1446&height=819',
        'track': 'turf',
        'course': {'venue': 'Chukyo', 'surface': 'turf', 'distance_m': 2000, 'course_id': 1, 'direction': 'left'},
        'path': TRACK_PATHS['CUSTOM_CHUNICHISHIMBUNHAI'],
        'fans': {'required': 1500, 'reward_first': 4100},
        'story': 'GIII ระยะ 2,000 เมตรของ Chukyo ในฤดูหนาว สำหรับสาวม้ารุ่น Senior สายระยะกลาง.',

    },
    'KinkoSho': {
        'name': 'Tokai TV Hai Kinko Sho (GII)',
        'thumnail': G2_RACE_THUMBNAIL,
        'image': G2_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Chukyo', 'surface': 'turf', 'distance_m': 2000, 'direction': 'left'},
        'path': TRACK_PATHS['CHUKYO_2000'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Tokai TV Hai Kinko Sho (GII) ที่สนาม Chukyo',

    },
    'FalconStakes': {
        'name': 'Chunichi Sports Sho Falcon Stakes (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Chukyo', 'surface': 'turf', 'distance_m': 1400, 'direction': 'left'},
        'path': TRACK_PATHS['CHUKYO_1400'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Chunichi Sports Sho Falcon Stakes (GIII) ที่สนาม Chukyo',

    },
    'AichiHai': {
        'name': 'Aichi Hai (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Chukyo', 'surface': 'turf', 'distance_m': 2000, 'direction': 'left'},
        'path': TRACK_PATHS['CHUKYO_2000'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Aichi Hai (GIII) ที่สนาม Chukyo',

    },
    'ChukyoKinen': {
        'name': 'Chukyo Kinen (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Chukyo', 'surface': 'turf', 'distance_m': 1600, 'direction': 'left'},
        'path': TRACK_PATHS['CHUKYO_1600'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Chukyo Kinen (GIII) ที่สนาม Chukyo',

    },
    'ChukyoNisaiStakes': {
        'name': 'Chukyo Nisai Stakes (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Chukyo', 'surface': 'turf', 'distance_m': 1800, 'direction': 'left'},
        'path': TRACK_PATHS['CHUKYO_1800'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Chukyo Nisai Stakes (GIII) ที่สนาม Chukyo',

    },
    'CentaurStakes': {
        'name': 'Sankei Sho Centaur Stakes (GII)',
        'thumnail': G2_RACE_THUMBNAIL,
        'image': G2_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Chukyo', 'surface': 'turf', 'distance_m': 1200, 'direction': 'left'},
        'path': TRACK_PATHS['CHUKYO_1200'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Sankei Sho Centaur Stakes (GII) ที่สนาม Chukyo',

    },
    'TokaiStakes': {
        'name': 'Tokai Stakes (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'dirt',
        'course': {'venue': 'Chukyo', 'surface': 'dirt', 'distance_m': 1800, 'direction': 'left'},
        'path': TRACK_PATHS['CHUKYO_1800'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Tokai Stakes (GIII) ที่สนาม Chukyo',

    },
    'CBCSho': {
        'name': 'CBC Sho (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Chukyo', 'surface': 'turf', 'distance_m': 1200, 'direction': 'left'},
        'path': TRACK_PATHS['CHUKYO_1200'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ CBC Sho (GIII) ที่สนาม Chukyo',

    },
}
