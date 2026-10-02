"""Race presets for Hanshin."""

from utils.race.race_preset_constants import G2_RACE_THUMBNAIL, G3_RACE_THUMBNAIL

TRACK_PATHS = {'HANSHIN_1400': [1, 1, 2, 4, 2, 2, 3, 1],
 'HANSHIN_1600': [1, 1, 2, 2, 4, 1, 3, 1],
 'HANSHIN_1800': [1, 1, 1, 2, 4, 1, 3, 1],
 'HANSHIN_2400': [3, 1, 2, 2, 1, 1, 2, 2, 4, 3, 3, 1],
 'HANSHIN_2200': [4, 3, 1, 2, 2, 1, 4, 2, 2, 1, 3, 1],
 'HANSHIN_2000': [3, 1, 2, 2, 1, 1, 2, 2, 4, 3, 1, 1],
 'HANSHIN_3000': [1, 1, 4, 2, 2, 1, 3, 1, 2, 2, 1, 4, 2, 2, 3, 1]}


RACES = {
    'FilliesRevue': {
        'name': "Fillies' Revue (GII)",
        'thumnail': G2_RACE_THUMBNAIL,
        'image': G2_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Hanshin', 'surface': 'turf', 'distance_m': 1400, 'course_id': 2, 'direction': 'right'},
        'path': TRACK_PATHS['HANSHIN_1400'],
        'fans': {'required': 1750, 'reward_first': 5200},
        'story': 'สนาม Trial Race สำคัญสู่ Oka Sho สำหรับสาวม้ารุ่น Classic.',

    },
    'TulipSho': {
        'name': 'Tulip Sho (GII)',
        'thumnail': G2_RACE_THUMBNAIL,
        'image': G2_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Hanshin', 'surface': 'turf', 'distance_m': 1600, 'course_id': 3, 'direction': 'right'},
        'path': TRACK_PATHS['HANSHIN_1600'],
        'fans': {'required': 1750, 'reward_first': 5200},
        'story': 'สนาม Trial Race ระยะไมล์ที่ใช้เตรียมสู่ Oka Sho.',

    },
    'RoseStakes': {
        'name': 'Rose Stakes (GII)',
        'thumnail': G2_RACE_THUMBNAIL,
        'image': G2_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Hanshin', 'surface': 'turf', 'distance_m': 1800, 'course_id': 3, 'direction': 'right'},
        'path': TRACK_PATHS['HANSHIN_1800'],
        'fans': {'required': 1750, 'reward_first': 5200},
        'story': 'สนาม Trial Race ช่วงฤดูใบไม้ร่วงสำหรับเส้นทางสู่ Shuka Sho.',

    },
    'KobeShimbunHai': {
        'name': 'Kobe Shimbun Hai (GII)',
        'thumnail': G2_RACE_THUMBNAIL,
        'image': G2_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Hanshin', 'surface': 'turf', 'distance_m': 2400, 'course_id': 3, 'direction': 'right'},
        'path': TRACK_PATHS['HANSHIN_2400'],
        'fans': {'required': 1750, 'reward_first': 5400},
        'story': 'หนึ่งในสนาม Trial Race หลักก่อน Kikuka Sho สำหรับสาวม้ารุ่น Classic.',

    },
    'OkaSho': {
        'name': 'Oka Sho (GI)',
        'thumnail': 'https://media.discordapp.net/attachments/1494730857259471030/1495054919999291593/thum_race_rt_000_1004_00.png?ex=69e4d9e5&is=69e38865&hm=43e097df171288de94a09c609093567b36f63d96492082d1912cb59068534280&=&format=webp&quality=lossless&width=192&height=96',
        'image': 'https://media.discordapp.net/attachments/1494730857259471030/1495054920347422842/10903.png?ex=69e4d9e5&is=69e38865&hm=3896e24d0545c6aa3b3c7e288cdb72c8a42bda905ed39dd8b605ecf65daeebaf&=&format=webp&quality=lossless&width=1479&height=995',
        'track': 'turf',
        'course': {'venue': 'Hanshin', 'surface': 'turf', 'distance_m': 1600, 'course_id': 3, 'direction': 'right'},
        'path': TRACK_PATHS['HANSHIN_1600'],
        'fans': {'required': 4500, 'reward_first': 10500},
        'story': 'ศึกสปรินต์ไมล์ 1,600 เมตร บนกลีบซากุระที่ผลิบาน เวทีประชันความเร็วเพื่อช่วงชิงมงกุฎแรกแห่งราชินี',

    },
    'AsahiHaiFuturityStakes': {
        'name': 'Asahi Hai Futurity Stakes (GI)',
        'thumnail': 'https://media.discordapp.net/attachments/1494730857259471030/1495054919999291593/thum_race_rt_000_1004_00.png?ex=69e4d9e5&is=69e38865&hm=43e097df171288de94a09c609093567b36f63d96492082d1912cb59068534280&=&format=webp&quality=lossless&width=192&height=96',
        'image': 'https://media.discordapp.net/attachments/1494730857259471030/1542823759117815849/1022.png?ex=6a92a218&is=6a915098&hm=b3307bae901053346fb5c1122fc665caf4eb9edbbe45e07b292d0a01c8222970&=&format=webp&quality=lossless',
        'track': 'turf',
        'course': {'venue': 'Hanshin', 'surface': 'turf', 'distance_m': 1600, 'course_id': 3, 'direction': 'right'},
        'path': TRACK_PATHS['HANSHIN_1600'],
        'fans': {'required': 1000, 'reward_first': 7000},
        'story': 'ได้ยินจากรุ่นพี่ว่าทางตรงเร็วที่สุด (แต่นี่มันไมล์นะ!?)',

    },
    'HanshinJuvenileFillies': {
        'name': 'Hanshin Juvenile Fillies (GI)',
        'thumnail': 'https://media.discordapp.net/attachments/1494730857259471030/1495054919999291593/thum_race_rt_000_1004_00.png?ex=69e4d9e5&is=69e38865&hm=43e097df171288de94a09c609093567b36f63d96492082d1912cb59068534280&=&format=webp&quality=lossless&width=192&height=96',
        'image': 'https://media.discordapp.net/attachments/1494730857259471030/1542823759419932673/1021.png?ex=6a92a218&is=6a915098&hm=135cb90f0f3b95cb65d6e03680107d473a4bb32e022d703996827208d4acc1a7&=&format=webp&quality=lossless',
        'track': 'turf',
        'course': {'venue': 'Hanshin', 'surface': 'turf', 'distance_m': 1600, 'course_id': 3, 'direction': 'right'},
        'path': TRACK_PATHS['HANSHIN_1600'],
        'fans': {'required': 1000, 'reward_first': 6500},
        'story': 'รุ่นน้องแล้วไง ก็เก่งเหมือนกันนะคะ!',

    },
    'TakarazukaKinen': {
        'name': 'Takarazuka Kinen (GI)',
        'thumnail': 'https://media.discordapp.net/attachments/1493695524812095489/1494219500743163954/thum_race_rt_000_1012_00.png?ex=69e1cfda&is=69e07e5a&hm=9aaa79075889b9f8a5fad33f09a31c72c252e586b3f753d472bff3ea15422de2&=&format=webp&quality=lossless&width=192&height=96',
        'image': 'https://media.discordapp.net/attachments/1493695524812095489/1494219501019992196/10906.png?ex=69e1cfda&is=69e07e5a&hm=89bf0bdf5173efa05fe2a6f91ac19dae5dee0499b0f4296f6a4fa24c50c5073c&=&format=webp&quality=lossless&width=1359&height=984',
        'track': 'turf',
        'course': {'venue': 'Hanshin', 'surface': 'turf', 'distance_m': 2200, 'course_id': 2, 'direction': 'right'},
        'path': TRACK_PATHS['HANSHIN_2200'],
        'fans': {'required': 20000, 'reward_first': 15000},
        'story': 'สังเวียนชี้ชะตาระยะกลาง 2,200 เมตร ดาราแห่งวสันตฤดู',

    },
    'OsakaHai': {
        'name': 'Osaka Hai (GI)',
        'thumnail': 'https://media.discordapp.net/attachments/1494730857259471030/1495036503619797082/thum_race_rt_000_1003_00.png?ex=69e4c8be&is=69e3773e&hm=ad4fa8db3cd21e0e73c01cacb03d76c77d8faa4f5cca48dd68b274a762b9b569&=&format=webp&quality=lossless&width=192&height=96',
        'image': 'https://media.discordapp.net/attachments/1494730857259471030/1495036503917723739/10905.png?ex=69e4c8be&is=69e3773e&hm=42d5d562d0ff0c090347a983d78de62e5f108732ed3331d8dc09ad6b25f26b74&=&format=webp&quality=lossless&width=1359&height=932',
        'track': 'turf',
        'course': {'venue': 'Hanshin', 'surface': 'turf', 'distance_m': 2000, 'course_id': 2, 'direction': 'right'},
        'path': TRACK_PATHS['HANSHIN_2000'],
        'fans': {'required': 20000, 'reward_first': 13500},
        'story': ' ปะทะซีเนียร์หัวกะทิ ประตูบานแรกสู่การครองบัลลังก์ระยะกลางประจำปี!',

    },
    'HanshinDaishoten': {
        'name': 'Hanshin Daishoten (GII)',
        'thumnail': G2_RACE_THUMBNAIL,
        'image': G2_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Hanshin', 'surface': 'turf', 'distance_m': 3000, 'direction': 'right'},
        'path': TRACK_PATHS['HANSHIN_3000'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Hanshin Daishoten (GII) ที่สนาม Hanshin',

    },
    'HankyuHai': {
        'name': 'Hankyu Hai (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Hanshin', 'surface': 'turf', 'distance_m': 1400, 'direction': 'right'},
        'path': TRACK_PATHS['HANSHIN_1400'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Hankyu Hai (GIII) ที่สนาม Hanshin',

    },
    'MainichiHai': {
        'name': 'Mainichi Hai (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Hanshin', 'surface': 'turf', 'distance_m': 1800, 'direction': 'right'},
        'path': TRACK_PATHS['HANSHIN_1800'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Mainichi Hai (GIII) ที่สนาม Hanshin',

    },
    'ChurchillDownsCup': {
        'name': 'Churchill Downs Cup (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Hanshin', 'surface': 'turf', 'distance_m': 1600, 'direction': 'right'},
        'path': TRACK_PATHS['HANSHIN_1600'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Churchill Downs Cup (GIII) ที่สนาม Hanshin',

    },
    'HanshinHimbaStakes': {
        'name': 'Hanshin Himba Stakes (GII)',
        'thumnail': G2_RACE_THUMBNAIL,
        'image': G2_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Hanshin', 'surface': 'turf', 'distance_m': 1600, 'direction': 'right'},
        'path': TRACK_PATHS['HANSHIN_1600'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Hanshin Himba Stakes (GII) ที่สนาม Hanshin',

    },
    'AntaresStakes': {
        'name': 'Antares Stakes (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'dirt',
        'course': {'venue': 'Hanshin', 'surface': 'dirt', 'distance_m': 1800, 'direction': 'right'},
        'path': TRACK_PATHS['HANSHIN_1800'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Antares Stakes (GIII) ที่สนาม Hanshin',

    },
    'ShirasagiStakes': {
        'name': 'Shirasagi Stakes (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Hanshin', 'surface': 'turf', 'distance_m': 1600, 'direction': 'right'},
        'path': TRACK_PATHS['HANSHIN_1600'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Shirasagi Stakes (GIII) ที่สนาม Hanshin',

    },
    'ChallengeCup': {
        'name': 'Challenge Cup (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Hanshin', 'surface': 'turf', 'distance_m': 2000, 'direction': 'right'},
        'path': TRACK_PATHS['HANSHIN_2000'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Challenge Cup (GIII) ที่สนาม Hanshin',

    },
    'SiriusStakes': {
        'name': 'Sirius Stakes (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'dirt',
        'course': {'venue': 'Hanshin', 'surface': 'dirt', 'distance_m': 2000, 'direction': 'right'},
        'path': TRACK_PATHS['HANSHIN_2000'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Sirius Stakes (GIII) ที่สนาม Hanshin',

    },
    'NaruoKinen': {
        'name': 'Naruo Kinen (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Hanshin', 'surface': 'turf', 'distance_m': 1800, 'direction': 'right'},
        'path': TRACK_PATHS['HANSHIN_1800'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Naruo Kinen (GIII) ที่สนาม Hanshin',

    },
    'HanshinCup': {
        'name': 'Hanshin Cup (GII)',
        'thumnail': G2_RACE_THUMBNAIL,
        'image': G2_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Hanshin', 'surface': 'turf', 'distance_m': 1400, 'direction': 'right'},
        'path': TRACK_PATHS['HANSHIN_1400'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Hanshin Cup (GII) ที่สนาม Hanshin',

    },
}
