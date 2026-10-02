"""Race presets for Nakayama."""

from utils.race.race_preset_constants import G2_RACE_THUMBNAIL, G3_RACE_THUMBNAIL

TRACK_PATHS = {'NAKAYAMA_1800': [3, 2, 4, 2, 1, 2, 2, 3],
 'NAKAYAMA_1600': [1, 4, 2, 1, 1, 2, 3, 1],
 'NAKAYAMA_2000': [3, 1, 3, 2, 4, 2, 1, 1, 2, 2, 3, 1],
 'NAKAYAMA_2200': [3, 1, 3, 2, 4, 2, 1, 2, 1, 2, 3, 1],
 'NAKAYAMA_1200': [4, 1, 2, 1, 2, 2, 3, 1],
 'NAKAYAMA_2500': [1, 2, 2, 1, 3, 1, 3, 2, 4, 2, 1, 1, 2, 2, 3, 1],
 'NAKAYAMA_3600': [3, 1, 3, 2, 4, 2, 1, 1, 1, 1, 2, 2, 1, 3, 1, 3]}


RACES = {
    'SpringStakes': {
        'name': 'Spring Stakes (GII)',
        'thumnail': G2_RACE_THUMBNAIL,
        'image': G2_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Nakayama', 'surface': 'turf', 'distance_m': 1800, 'course_id': 2, 'direction': 'right'},
        'path': TRACK_PATHS['NAKAYAMA_1800'],
        'fans': {'required': 1750, 'reward_first': 5400},
        'story': 'สนาม Trial Race สำคัญบนทางสู่ Satsuki Sho.',

    },
    'NewZealandTrophy': {
        'name': 'New Zealand Trophy (GII)',
        'thumnail': G2_RACE_THUMBNAIL,
        'image': G2_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Nakayama', 'surface': 'turf', 'distance_m': 1600, 'course_id': 3, 'direction': 'right'},
        'path': TRACK_PATHS['NAKAYAMA_1600'],
        'fans': {'required': 1750, 'reward_first': 5400},
        'story': 'สนาม Trial Race ระยะไมล์ที่เชื่อมไปยัง NHK Mile Cup.',

    },
    'YayoiSho': {
        'name': 'Yayoi Sho Deep Impact Kinen (GII)',
        'thumnail': G2_RACE_THUMBNAIL,
        'image': G2_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Nakayama', 'surface': 'turf', 'distance_m': 2000, 'course_id': 2, 'direction': 'right'},
        'path': TRACK_PATHS['NAKAYAMA_2000'],
        'fans': {'required': 1750, 'reward_first': 5400},
        'story': 'สนาม Trial Race ระยะ 2,000 เมตรสำหรับสาวม้ารุ่น Classic ก่อน Satsuki Sho.',

    },
    'StLiteKinen': {
        'name': 'St. Lite Kinen (GII)',
        'thumnail': G2_RACE_THUMBNAIL,
        'image': G2_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Nakayama', 'surface': 'turf', 'distance_m': 2200, 'course_id': 3, 'direction': 'right'},
        'path': TRACK_PATHS['NAKAYAMA_2200'],
        'fans': {'required': 1750, 'reward_first': 5400},
        'story': 'สนาม Trial Race ช่วงฤดูใบไม้ร่วงสำหรับผู้มุ่งสู่ Kikuka Sho.',

    },
    'SatsukiSho': {
        'name': 'Satsuki Sho (GI)',
        'thumnail': 'https://media.discordapp.net/attachments/1494730857259471030/1494730962477519049/thum_race_rt_000_1005_00.png?ex=69e454f0&is=69e30370&hm=7e84d8f95186e443c0e78149ac3dcee1be20600fb14f672bf37e781a94bbb9fa&=&format=webp&quality=lossless&width=192&height=96',
        'image': 'https://media.discordapp.net/attachments/1494730857259471030/1494730963538804886/10504.png?ex=69e454f0&is=69e30370&hm=1534a1ad5575876856ca045835669f89bb38a510e064c5ab028c3697d3fb46d2&=&format=webp&quality=lossless&width=1433&height=812',
        'track': 'turf',
        'course': {'venue': 'Nakayama', 'surface': 'turf', 'distance_m': 2000, 'course_id': 2, 'direction': 'right'},
        'path': TRACK_PATHS['NAKAYAMA_2000'],
        'fans': {'required': 4500, 'reward_first': 11000},
        'story': 'ด่านแรกของสามมงกุฎ บททดสอบความเร็วและไหวพริบระยะ 2,000 เมตร สังเวียนคัดกรองสาวม้าที่เฉียบคมและว่องไวที่สุดในรุ่น ผู้ที่เร็วที่สุดเท่านั้นที่จะคว้าชัย',

    },
    'HopefulStakes': {
        'name': 'Hopeful Stakes (GI)',
        'thumnail': 'https://media.discordapp.net/attachments/1494730857259471030/1494730962477519049/thum_race_rt_000_1005_00.png?ex=69e454f0&is=69e30370&hm=7e84d8f95186e443c0e78149ac3dcee1be20600fb14f672bf37e781a94bbb9fa&=&format=webp&quality=lossless&width=192&height=96',
        'image': 'https://media.discordapp.net/attachments/1494730857259471030/1542838972458336316/1024.png?ex=6a92b043&is=6a915ec3&hm=c1068a136aced734793690ce2bf11139a5181ea377f25ef6696e1171f2c4f425&=&format=webp&quality=lossless',
        'track': 'turf',
        'course': {'venue': 'Nakayama', 'surface': 'turf', 'distance_m': 2000, 'course_id': 2, 'direction': 'right'},
        'path': TRACK_PATHS['NAKAYAMA_2000'],
        'fans': {'required': 1000, 'reward_first': 7000},
        'story': 'จุดกำเนิดแห่งความหวัง ใครกันนะดางเด่นแห่งยุคถัดไป',

    },
    'SprintersStakes': {
        'name': 'Sprinters Stakes (GI)',
        'thumnail': 'https://media.discordapp.net/attachments/1494730857259471030/1542839396556873778/10501.png?ex=6a92b0a8&is=6a915f28&hm=0e6aa72b609f66d4efb06d95000b3c62aceadb6839f3000248b892ae50470817&=&format=webp&quality=lossless',
        'image': 'https://media.discordapp.net/attachments/1494730857259471030/1542839096001560607/1013.png?ex=6a92b061&is=6a915ee1&hm=1a0f4d3afa65591f711254f9e4391485a8ae410d69948db4f89c9ff501d8d589&=&format=webp&quality=lossless',
        'track': 'turf',
        'course': {'venue': 'Nakayama', 'surface': 'turf', 'distance_m': 1200, 'course_id': 3, 'direction': 'right'},
        'path': TRACK_PATHS['NAKAYAMA_1200'],
        'fans': {'required': 15000, 'reward_first': 13000},
        'story': '68 วินาที ชี้ชะตาราชาและราชินีแห่งความเร็วระยะสั้น',

    },
    'ArimaKinen': {
        'name': 'Arima Kinen (GI)',
        'thumnail': 'https://media.discordapp.net/attachments/1494730857259471030/1494752842714710156/thum_race_rt_000_1023_00.png?ex=69e46950&is=69e317d0&hm=039c53a2ecceb4dadd4503f9ef11694182db84d3d7a514566fd5875cb11f2a24&=&format=webp&quality=lossless&width=192&height=96',
        'image': 'https://media.discordapp.net/attachments/1494730857259471030/1494752843184209930/10506.png?ex=69e46950&is=69e317d0&hm=e1434749606b63deb19bbd9f520fb7eb4e7b9ec09a236e0805f822e1de5eb1aa&=&format=webp&quality=lossless&width=1433&height=875',
        'track': 'turf',
        'course': {'venue': 'Nakayama', 'surface': 'turf', 'distance_m': 2500, 'course_id': 2, 'direction': 'right'},
        'path': TRACK_PATHS['NAKAYAMA_2500'],
        'fans': {'required': 25000, 'reward_first': 30000},
        'story': 'ความฝันแห่งหยาดน้ำตา อันตัวข้าจักถูกเล่านขานชั่วกาลนาน',

    },
    'StayersStakes': {
        'name': 'Sports Nippon Sho Stayers Stakes (GII)',
        'thumnail': G2_RACE_THUMBNAIL,
        'image': G2_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Nakayama', 'surface': 'turf', 'distance_m': 3600, 'direction': 'right'},
        'path': TRACK_PATHS['NAKAYAMA_3600'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Sports Nippon Sho Stayers Stakes (GII) ที่สนาม Nakayama',

    },
    'NakayamaKimpai': {
        'name': 'Nakayama Kimpai (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Nakayama', 'surface': 'turf', 'distance_m': 2000, 'direction': 'right'},
        'path': TRACK_PATHS['NAKAYAMA_2000'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Nakayama Kimpai (GIII) ที่สนาม Nakayama',

    },
    'FairyStakes': {
        'name': 'Fairy Stakes (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Nakayama', 'surface': 'turf', 'distance_m': 1600, 'direction': 'right'},
        'path': TRACK_PATHS['NAKAYAMA_1600'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Fairy Stakes (GIII) ที่สนาม Nakayama',

    },
    'KeiseiHai': {
        'name': 'Keisei Hai (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Nakayama', 'surface': 'turf', 'distance_m': 2000, 'direction': 'right'},
        'path': TRACK_PATHS['NAKAYAMA_2000'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Keisei Hai (GIII) ที่สนาม Nakayama',

    },
    'AmericanJockeyClubCup': {
        'name': 'American Jockey Club Cup (GII)',
        'thumnail': G2_RACE_THUMBNAIL,
        'image': G2_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Nakayama', 'surface': 'turf', 'distance_m': 2200, 'direction': 'right'},
        'path': TRACK_PATHS['NAKAYAMA_2200'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ American Jockey Club Cup (GII) ที่สนาม Nakayama',

    },
    'OceanStakes': {
        'name': 'Ocean Stakes (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Nakayama', 'surface': 'turf', 'distance_m': 1200, 'direction': 'right'},
        'path': TRACK_PATHS['NAKAYAMA_1200'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Ocean Stakes (GIII) ที่สนาม Nakayama',

    },
    'NakayamaKinen': {
        'name': 'Nakayama Kinen (GII)',
        'thumnail': G2_RACE_THUMBNAIL,
        'image': G2_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Nakayama', 'surface': 'turf', 'distance_m': 1800, 'direction': 'right'},
        'path': TRACK_PATHS['NAKAYAMA_1800'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Nakayama Kinen (GII) ที่สนาม Nakayama',

    },
    'NakayamaHimbaStakes': {
        'name': 'Nakayama Himba Stakes (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Nakayama', 'surface': 'turf', 'distance_m': 1800, 'direction': 'right'},
        'path': TRACK_PATHS['NAKAYAMA_1800'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Nakayama Himba Stakes (GIII) ที่สนาม Nakayama',

    },
    'FlowerCup': {
        'name': 'Flower Cup (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Nakayama', 'surface': 'turf', 'distance_m': 1800, 'direction': 'right'},
        'path': TRACK_PATHS['NAKAYAMA_1800'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Flower Cup (GIII) ที่สนาม Nakayama',

    },
    'NikkeiSho': {
        'name': 'Nikkei Sho (GII)',
        'thumnail': G2_RACE_THUMBNAIL,
        'image': G2_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Nakayama', 'surface': 'turf', 'distance_m': 2500, 'direction': 'right'},
        'path': TRACK_PATHS['NAKAYAMA_2500'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Nikkei Sho (GII) ที่สนาม Nakayama',

    },
    'MarchStakes': {
        'name': 'March Stakes (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'dirt',
        'course': {'venue': 'Nakayama', 'surface': 'dirt', 'distance_m': 1800, 'direction': 'right'},
        'path': TRACK_PATHS['NAKAYAMA_1800'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ March Stakes (GIII) ที่สนาม Nakayama',

    },
    'LordDerbyChallengeTrophy': {
        'name': 'Lord Derby Challenge Trophy (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Nakayama', 'surface': 'turf', 'distance_m': 1600, 'direction': 'right'},
        'path': TRACK_PATHS['NAKAYAMA_1600'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Lord Derby Challenge Trophy (GIII) ที่สนาม Nakayama',

    },
    'KeiseiHaiAutumnHandicap': {
        'name': 'Keisei Hai Autumn Handicap (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Nakayama', 'surface': 'turf', 'distance_m': 1600, 'direction': 'right'},
        'path': TRACK_PATHS['NAKAYAMA_1600'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Keisei Hai Autumn Handicap (GIII) ที่สนาม Nakayama',

    },
    'ShionStakes': {
        'name': 'Shion Stakes (GII)',
        'thumnail': G2_RACE_THUMBNAIL,
        'image': G2_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Nakayama', 'surface': 'turf', 'distance_m': 2000, 'direction': 'right'},
        'path': TRACK_PATHS['NAKAYAMA_2000'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Shion Stakes (GII) ที่สนาม Nakayama',

    },
    'CapellaStakes': {
        'name': 'Capella Stakes (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'dirt',
        'course': {'venue': 'Nakayama', 'surface': 'dirt', 'distance_m': 1200, 'direction': 'right'},
        'path': TRACK_PATHS['NAKAYAMA_1200'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Capella Stakes (GIII) ที่สนาม Nakayama',

    },
    'TurquoiseStakes': {
        'name': 'Turquoise Stakes (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Nakayama', 'surface': 'turf', 'distance_m': 1600, 'direction': 'right'},
        'path': TRACK_PATHS['NAKAYAMA_1600'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Turquoise Stakes (GIII) ที่สนาม Nakayama',

    },
}
