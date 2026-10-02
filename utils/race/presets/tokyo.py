"""Race presets for Tokyo."""

from utils.race.race_preset_constants import G2_RACE_THUMBNAIL, G3_RACE_THUMBNAIL

TRACK_PATHS = {'TOKYO_2400': [1, 2, 2, 2, 3, 4, 2, 2, 2, 3, 3, 1],
 'TOKYO_2000': [1, 3, 2, 2, 4, 1, 3, 1, 1, 2, 2, 1],
 'TOKYO_1600': [1, 3, 4, 2, 2, 3, 1, 1],
 'TOKYO_Dirt_1400': [1, 1, 4, 2, 2, 3, 1, 1],
 'TOKYO_1800': [2, 3, 4, 2, 2, 3, 1, 1],
 'TOKYO_1400': [1, 3, 4, 2, 2, 3, 1, 1],
 'TOKYO_2500': [3, 3, 1, 1, 2, 2, 1, 3, 1, 4, 2, 2, 3, 3, 1, 1]}


RACES = {
    'AobaSho': {
        'name': 'Aoba Sho (GII)',
        'thumnail': G2_RACE_THUMBNAIL,
        'image': G2_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Tokyo', 'surface': 'turf', 'distance_m': 2400, 'course_id': 1, 'direction': 'left'},
        'path': TRACK_PATHS['TOKYO_2400'],
        'fans': {'required': 1800, 'reward_first': 5400},
        'story': 'สนาม Trial Race ที่มอบเส้นทางสำคัญสู่ Japanese Derby.',

    },
    'FloraStakes': {
        'name': 'Flora Stakes (GII)',
        'thumnail': G2_RACE_THUMBNAIL,
        'image': G2_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Tokyo', 'surface': 'turf', 'distance_m': 2000, 'course_id': 1, 'direction': 'left'},
        'path': TRACK_PATHS['TOKYO_2000'],
        'fans': {'required': 1750, 'reward_first': 5200},
        'story': 'สนาม Trial Race ของสาวม้ารุ่น Classic ก่อน Japanese Oaks.',

    },
    'NHK': {
        'name': 'NHK Mile Cup (GI)',
        'thumnail': 'https://media.discordapp.net/attachments/1493695524812095489/1494219182676512858/thum_race_rt_000_1007_00.png?ex=69e1cf8e&is=69e07e0e&hm=b343ae355428ebe48951cadbae8cd18e5870346e5efb6eef401f613faa449997&=&format=webp&quality=lossless&width=192&height=96',
        'image': 'https://media.discordapp.net/attachments/1493695524812095489/1494219216809627789/10602.png?ex=69e1cf96&is=69e07e16&hm=579e4e375f156ce70ee13c5cb16687e279c952a42776c9df1273960d85bb9c76&=&format=webp&quality=lossless&width=1440&height=929',
        'track': 'turf',
        'course': {'venue': 'Tokyo', 'surface': 'turf', 'distance_m': 1600, 'course_id': 1, 'direction': 'left'},
        'path': TRACK_PATHS['TOKYO_1600'],
        'fans': {'required': 5000, 'reward_first': 10500},
        'story': 'GI ระยะไมล์สำหรับสาวม้ารุ่น Classic ซึ่งเป็นเป้าหมายสำคัญนอกสาย Classic ระยะกลาง.',

    },
    'JapaneseOaks': {
        'name': 'Japanese Oaks (GI)',
        'thumnail': 'https://media.discordapp.net/attachments/1494730857259471030/1494731127385100428/thum_race_rt_000_1010_00.png?ex=69e45517&is=69e30397&hm=c31d08d5c4f4b6abf6a4d31e4331ff2459a9903aff29d6eadefdd553f78eff5e&=&format=webp&quality=lossless&width=192&height=96',
        'image': 'https://media.discordapp.net/attachments/1494730857259471030/1542831170813698078/1009.png?ex=6a92a8ff&is=6a91577f&hm=307af9ecda833bfd5baf4f7dd10afa79d379f84e67b5c6ae11f15cf78c195c1a&=&format=webp&quality=lossless',
        'track': 'turf',
        'course': {'venue': 'Tokyo', 'surface': 'turf', 'distance_m': 2400, 'course_id': 1, 'direction': 'left'},
        'path': TRACK_PATHS['TOKYO_2400'],
        'fans': {'required': 6000, 'reward_first': 11000},
        'story': '2,400 เมตร ที่ไม่เพียงแต่เร็ว แต่ต้องมีหัวใจทรหดและพละกำลังที่สง่างามสมดั่งราชินีแห่งโอ็ค',

    },
    'JapaneseDerby': {
        'name': 'Tokyo Yushun (Japanese Derby) (GI)',
        'thumnail': 'https://media.discordapp.net/attachments/1494730857259471030/1494731127385100428/thum_race_rt_000_1010_00.png?ex=69e45517&is=69e30397&hm=c31d08d5c4f4b6abf6a4d31e4331ff2459a9903aff29d6eadefdd553f78eff5e&=&format=webp&quality=lossless&width=192&height=96',
        'image': 'https://media.discordapp.net/attachments/1494730857259471030/1494731127682760825/10606.png?ex=69e45517&is=69e30397&hm=f33351514052039ff0bf65d941f40771384d694427afe961be403fe0fa84b4e4&=&format=webp&quality=lossless&width=1607&height=927',
        'track': 'turf',
        'course': {'venue': 'Tokyo', 'surface': 'turf', 'distance_m': 2400, 'course_id': 1, 'direction': 'left'},
        'path': TRACK_PATHS['TOKYO_2400'],
        'fans': {'required': 6000, 'reward_first': 20000},
        'story': 'จุดสูงสุดของสาวม้ารุ่นคลาสซิกหนึ่งชีวิต หนึ่งหนย่อมแลกทุกอย่างเพียงเพื่อได้จารึกชื่อในดาร์บี้ตลอดกาล ผู้ซึ่งโชคดีที่สุดจะชี้นำพา',

    },
    'TennoShoAutumn': {
        'name': 'Tenno Sho (Autumn) (GI)',
        'thumnail': 'https://media.discordapp.net/attachments/1494730857259471030/1495035900818751598/thum_race_rt_000_1016_00.png?ex=69e4c82f&is=69e376af&hm=9dfb903aa4a2ca5c03acf2d67c32ee70d04ef389eeb251ff7ddb64596ad2b796&=&format=webp&quality=lossless&width=192&height=96',
        'image': 'https://media.discordapp.net/attachments/1494730857259471030/1495035901087318036/10604.png?ex=69e4c82f&is=69e376af&hm=89286fb782c955579e4cedc8c44c0b4ab54afed16ff6b88bd6ec8967b05eb7e6&=&format=webp&quality=lossless&width=1745&height=930',
        'track': 'turf',
        'course': {'venue': 'Tokyo', 'surface': 'turf', 'distance_m': 2000, 'course_id': 1, 'direction': 'left'},
        'path': TRACK_PATHS['TOKYO_2000'],
        'fans': {'required': 20000, 'reward_first': 15000},
        'story': ' สงครามความเร็วระยะ 2,000 เมตร เกียรติยศแบะความเร็ว ราชาทางเรียบ !',

    },
    'JapanCup': {
        'name': 'Japan Cup (GI)',
        'thumnail': 'https://media.discordapp.net/attachments/1494730857259471030/1495036145363320903/thum_race_rt_000_1019_00.png?ex=69e4c869&is=69e376e9&hm=f940df4979f39cbe2532b6170ad84b0562f72193fbd0fac4aec78fa498f9048f&=&format=webp&quality=lossless&width=192&height=96',
        'image': 'https://media.discordapp.net/attachments/1494730857259471030/1495036145900195930/10606.png?ex=69e4c869&is=69e376e9&hm=2fea0f4fba9309b9b9374e873a8fa581847e7a86f2c69d56bebfdea9a20ea8e6&=&format=webp&quality=lossless&width=1607&height=927',
        'track': 'turf',
        'course': {'venue': 'Tokyo', 'surface': 'turf', 'distance_m': 2400, 'course_id': 1, 'direction': 'left'},
        'path': TRACK_PATHS['TOKYO_2400'],
        'fans': {'required': 25000, 'reward_first': 30000},
        'story': 'ยอดนักกรีฑาแห่งโลกาทั้งหลายจงดู สลักไว้ในความทรงจำ นี้คือพลังของอาชาสาวแห่งอุทัยทิศ!',

    },
    'YasudaKinen': {
        'name': 'Yasuda Kinen (GI)',
        'thumnail': 'https://media.discordapp.net/attachments/1493695524812095489/1494219182676512858/thum_race_rt_000_1007_00.png?ex=69e1cf8e&is=69e07e0e&hm=b343ae355428ebe48951cadbae8cd18e5870346e5efb6eef401f613faa449997&=&format=webp&quality=lossless&width=192&height=96',
        'image': 'https://media.discordapp.net/attachments/1494730857259471030/1542831632053182595/1011.png?ex=6a92a96d&is=6a9157ed&hm=729281b3e638493908077aad006f061ddff4005b3f4090e434b6b08f7941dc43&=&format=webp&quality=lossless',
        'track': 'turf',
        'course': {'venue': 'Tokyo', 'surface': 'turf', 'distance_m': 1600, 'course_id': 1, 'direction': 'left'},
        'path': TRACK_PATHS['TOKYO_1600'],
        'fans': {'required': 15000, 'reward_first': 13000},
        'story': 'ไมล์ทางตรงมหาโหด ใครไม่ยอมไปก่อนเลย!',

    },
    'FebruaryStakes': {
        'name': 'February Stakes (GI)',
        'thumnail': 'https://media.discordapp.net/attachments/1493695524812095489/1494219182676512858/thum_race_rt_000_1007_00.png?ex=69e1cf8e&is=69e07e0e&hm=b343ae355428ebe48951cadbae8cd18e5870346e5efb6eef401f613faa449997&=&format=webp&quality=lossless&width=192&height=96',
        'image': 'https://media.discordapp.net/attachments/1494730857259471030/1542832798941843517/1001.png?ex=6a92aa83&is=6a915903&hm=c9778de409038dab6b005889bb069ee05dac2936510579e0de819e444fd6ffc5&=&format=webp&quality=lossless',
        'track': 'dirt',
        'course': {'venue': 'Tokyo', 'surface': 'dirt', 'distance_m': 1600, 'course_id': 1, 'direction': 'left'},
        'path': TRACK_PATHS['TOKYO_1600'],
        'fans': {'required': 12000, 'reward_first': 10000},
        'story': 'สังเวียนแรกของเหล่าปีศาจสนามฝุ่น',

    },
    'VictoriaMileTokyo': {
        'name': 'Victoria Mile Tokyo (GI)',
        'thumnail': 'https://media.discordapp.net/attachments/1493695524812095489/1494219182676512858/thum_race_rt_000_1007_00.png?ex=69e1cf8e&is=69e07e0e&hm=b343ae355428ebe48951cadbae8cd18e5870346e5efb6eef401f613faa449997&=&format=webp&quality=lossless&width=192&height=96',
        'image': 'https://media.discordapp.net/attachments/1494730857259471030/1542833275863834704/1008.png?ex=6a92aaf5&is=6a915975&hm=d9cedaae9a2dd439067e038338467f88b064d611210f025344e0e25a7b1e404f&=&format=webp&quality=lossless',
        'track': 'turf',
        'course': {'venue': 'Tokyo', 'surface': 'turf', 'distance_m': 1600, 'course_id': 1, 'direction': 'left'},
        'path': TRACK_PATHS['TOKYO_1600'],
        'fans': {'required': 10000, 'reward_first': 10500},
        'story': 'เทียร่าลงสนาม ฉันนี้แหละยอดสตรีสนามไมล์!',

    },
    'SaudiArabiaRoyalCup': {
        'name': 'Saudi Arabia Royal Cup (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': 'https://media.discordapp.net/attachments/1494730857259471030/1502921213033451520/10807.png?ex=6a0766b4&is=6a061534&hm=50268c29a32b616fc0c480a8b2841ac631b5f32a210c9f77a5a3b5305bb0bef0&=&format=webp&quality=lossless&width=1481&height=875',
        'track': 'turf',
        'course': {'venue': 'Tokyo', 'surface': 'turf', 'distance_m': 1600, 'course_id': 1, 'direction': 'left'},
        'path': TRACK_PATHS['TOKYO_1600'],
        'fans': {'required': 350, 'reward_first': 3300},
        'story': 'GIII ระยะไมล์ของ Tokyo สำหรับสาวม้ารุ่น Junior ในช่วงต้นฤดูกาล.',

    },
    'NegishiStakes': {
        'name': 'Negishi Stakes (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'dirt',
        'course': {'venue': 'Tokyo', 'surface': 'dirt', 'distance_m': 1400, 'direction': 'left'},
        'path': TRACK_PATHS['TOKYO_Dirt_1400'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Negishi Stakes (GIII) ที่สนาม Tokyo',

    },
    'KyodoNewsHai': {
        'name': 'Kyodo News Hai (Tokinominoru Kinen) (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Tokyo', 'surface': 'turf', 'distance_m': 1800, 'direction': 'left'},
        'path': TRACK_PATHS['TOKYO_1800'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Kyodo News Hai (Tokinominoru Kinen) (GIII) ที่สนาม Tokyo',

    },
    'KeioHaiSpringCup': {
        'name': 'Keio Hai Spring Cup (GII)',
        'thumnail': G2_RACE_THUMBNAIL,
        'image': G2_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Tokyo', 'surface': 'turf', 'distance_m': 1400, 'direction': 'left'},
        'path': TRACK_PATHS['TOKYO_1400'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Keio Hai Spring Cup (GII) ที่สนาม Tokyo',

    },
    'EpsomCup': {
        'name': 'Epsom Cup (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Tokyo', 'surface': 'turf', 'distance_m': 1800, 'direction': 'left'},
        'path': TRACK_PATHS['TOKYO_1800'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Epsom Cup (GIII) ที่สนาม Tokyo',

    },
    'MeguroKinen': {
        'name': 'Meguro Kinen (GII)',
        'thumnail': G2_RACE_THUMBNAIL,
        'image': G2_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Tokyo', 'surface': 'turf', 'distance_m': 2500, 'direction': 'left'},
        'path': TRACK_PATHS['TOKYO_2500'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Meguro Kinen (GII) ที่สนาม Tokyo',

    },
    'FuchuHimbaStakes': {
        'name': 'Fuchu Himba Stakes (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Tokyo', 'surface': 'turf', 'distance_m': 1800, 'direction': 'left'},
        'path': TRACK_PATHS['TOKYO_1800'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Fuchu Himba Stakes (GIII) ที่สนาม Tokyo',

    },
    'MainichiOkan': {
        'name': 'Mainichi Okan (GII)',
        'thumnail': G2_RACE_THUMBNAIL,
        'image': G2_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Tokyo', 'surface': 'turf', 'distance_m': 1800, 'direction': 'left'},
        'path': TRACK_PATHS['TOKYO_1800'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Mainichi Okan (GII) ที่สนาม Tokyo',

    },
    'IrelandTrophy': {
        'name': 'Ireland Trophy (GII)',
        'thumnail': G2_RACE_THUMBNAIL,
        'image': G2_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Tokyo', 'surface': 'turf', 'distance_m': 1800, 'direction': 'left'},
        'path': TRACK_PATHS['TOKYO_1800'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Ireland Trophy (GII) ที่สนาม Tokyo',

    },
    'KeioHaiNisaiStakes': {
        'name': 'Keio Hai Nisai Stakes (GII)',
        'thumnail': G2_RACE_THUMBNAIL,
        'image': G2_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Tokyo', 'surface': 'turf', 'distance_m': 1400, 'direction': 'left'},
        'path': TRACK_PATHS['TOKYO_1400'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Keio Hai Nisai Stakes (GII) ที่สนาม Tokyo',

    },
    'CopaRepublicaArgentina': {
        'name': 'Copa Republica Argentina (GII)',
        'thumnail': G2_RACE_THUMBNAIL,
        'image': G2_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Tokyo', 'surface': 'turf', 'distance_m': 2500, 'direction': 'left'},
        'path': TRACK_PATHS['TOKYO_2500'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Copa Republica Argentina (GII) ที่สนาม Tokyo',

    },
    'TokyoSportsHaiNisaiStakes': {
        'name': 'Tokyo Sports Hai Nisai Stakes (GII)',
        'thumnail': G2_RACE_THUMBNAIL,
        'image': G2_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Tokyo', 'surface': 'turf', 'distance_m': 1800, 'direction': 'left'},
        'path': TRACK_PATHS['TOKYO_1800'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Tokyo Sports Hai Nisai Stakes (GII) ที่สนาม Tokyo',

    },
    'TokyoShimbunHai': {
        'name': 'Tokyo Shimbun Hai (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Tokyo', 'surface': 'turf', 'distance_m': 1600, 'direction': 'left'},
        'path': TRACK_PATHS['TOKYO_1600'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Tokyo Shimbun Hai (GIII) ที่สนาม Tokyo',

    },
    'DailyHaiQueenCup': {
        'name': 'Daily Hai Queen Cup (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Tokyo', 'surface': 'turf', 'distance_m': 1600, 'direction': 'left'},
        'path': TRACK_PATHS['TOKYO_1600'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Daily Hai Queen Cup (GIII) ที่สนาม Tokyo',

    },
    'UnicornStakes': {
        'name': 'Unicorn Stakes (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'dirt',
        'course': {'venue': 'Tokyo', 'surface': 'dirt', 'distance_m': 1600, 'direction': 'left'},
        'path': TRACK_PATHS['TOKYO_1600'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Unicorn Stakes (GIII) ที่สนาม Tokyo',

    },
    'FujiStakes': {
        'name': 'Fuji Stakes (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Tokyo', 'surface': 'turf', 'distance_m': 1600, 'direction': 'left'},
        'path': TRACK_PATHS['TOKYO_1600'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Fuji Stakes (GIII) ที่สนาม Tokyo',

    },
    'ArtemisStakes': {
        'name': 'Artemis Stakes (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Tokyo', 'surface': 'turf', 'distance_m': 1600, 'direction': 'left'},
        'path': TRACK_PATHS['TOKYO_1600'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Artemis Stakes (GIII) ที่สนาม Tokyo',

    },
    'MusashinoStakes': {
        'name': 'Musashino Stakes (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'dirt',
        'course': {'venue': 'Tokyo', 'surface': 'dirt', 'distance_m': 1600, 'direction': 'left'},
        'path': TRACK_PATHS['TOKYO_1600'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Musashino Stakes (GIII) ที่สนาม Tokyo',

    },
}
