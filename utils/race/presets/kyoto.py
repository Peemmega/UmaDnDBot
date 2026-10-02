"""Race presets for Kyoto."""

from utils.race.race_preset_constants import G2_RACE_THUMBNAIL, G3_RACE_THUMBNAIL

TRACK_PATHS = {'KYOTO_2400': [1, 1, 1, 2, 2, 3, 3, 4, 2, 2, 1, 1],
 'KYOTO_3000': [3, 3, 4, 2, 2, 1, 1, 2, 2, 3, 3, 4, 2, 2, 1, 1],
 'KYOTO_2000': [1, 1, 2, 2, 1, 3, 1, 4, 2, 2, 1, 1],
 'KYOTO_2200': [1, 1, 2, 2, 3, 3, 4, 2, 2, 2, 1, 1],
 'KYOTO_1600': [1, 3, 3, 4, 2, 2, 1, 1],
 'KYOTO_3200': [1, 3, 3, 4, 2, 2, 1, 1, 2, 3, 3, 4, 2, 2, 1, 1],
 'CUSTOM_KYOTOJUNIORSTAKES': [1, 1, 1, 2, 2, 1, 3, 1, 4, 2, 2, 2],
 'CUSTOM_AOI_STAKES': [3, 1, 4, 2, 2, 2, 1, 1],
 'KYOTO_1800': [1, 1, 3, 3, 4, 2, 2, 1],
 'KYOTO_1200': [1, 3, 4, 2, 2, 1, 1, 1],
 'KYOTO_1400': [1, 3, 3, 4, 2, 2, 1, 1]}


RACES = {
    'KyotoDaishoten': {
        'name': 'Kyoto Daishoten (GII)',
        'thumnail': G2_RACE_THUMBNAIL,
        'image': G2_RACE_THUMBNAIL,
        'track': 'turf',
        'path': TRACK_PATHS['KYOTO_2400'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Kyoto Daishoten (GII) ที่สนาม Kyoto',
        'course': {'venue': 'Kyoto', 'surface': 'turf', 'distance_m': 2400},

    },
    'KikukaSho': {
        'name': 'Kikuka Sho (GI)',
        'thumnail': 'https://media.discordapp.net/attachments/1494730857259471030/1542847069192982568/10810.png?ex=6a92b7ce&is=6a91664e&hm=428e52dc08c70de0f664036b5aa71302ab6700e29938a58f295506cbc71cb172&=&format=webp&quality=lossless',
        'image': 'https://media.discordapp.net/attachments/1494730857259471030/1542847068824014919/1015.png?ex=6a92b7cd&is=6a91664d&hm=b8cff58a7f357c393d38349a98f57ed6de00599b4c5c031389b58eb8cb9b2d0a&=&format=webp&quality=lossless',
        'track': 'turf',
        'course': {'venue': 'Kyoto', 'surface': 'turf', 'distance_m': 3000, 'course_id': 3, 'direction': 'right'},
        'path': TRACK_PATHS['KYOTO_3000'],
        'fans': {'required': 7500, 'reward_first': 12000},
        'story': 'ด่านสุดท้ายแห่งเกียรติยศสามมงกุฎ 3,000 เมตร สังเวียนสังเวียนแห่งผู้ที่แข็งแกร่งที่สุดเท่านั้นจะยืนหยัด',

    },
    'ShukaSho': {
        'name': 'Shuka Sho (GI)',
        'thumnail': 'https://media.discordapp.net/attachments/1494730857259471030/1542847180253958144/10807.png?ex=6a92b7e8&is=6a916668&hm=5454d86691b9e9131dea4f0c41f9e789b309eb1f42437c2139bd251a4b1d91cd&=&format=webp&quality=lossless',
        'image': 'https://media.discordapp.net/attachments/1494730857259471030/1542847179444715570/1014.png?ex=6a92b7e8&is=6a916668&hm=a96a455f618630acaa665a4af2dcb438271dd8eaea067fee700d065b760f54f7&=&format=webp&quality=lossless',
        'track': 'turf',
        'course': {'venue': 'Kyoto', 'surface': 'turf', 'distance_m': 2000, 'course_id': 2, 'direction': 'right'},
        'path': TRACK_PATHS['KYOTO_2000'],
        'fans': {'required': 7500, 'reward_first': 10000},
        'story': 'ขับเคี่ยวบนโค้งในสุดแคบของสนามเกียวโต บทสรุปมงกุฎสุดท้าย ผู้ใดกันคือราชีนีที่แท้จริง?',

    },
    'QueenElizabethIICup': {
        'name': 'Queen Elizabeth II Cup (GI)',
        'thumnail': 'https://media.discordapp.net/attachments/1494730857259471030/1542847180253958144/10807.png?ex=6a92b7e8&is=6a916668&hm=5454d86691b9e9131dea4f0c41f9e789b309eb1f42437c2139bd251a4b1d91cd&=&format=webp&quality=lossless',
        'image': 'https://media.discordapp.net/attachments/1494730857259471030/1542847179444715570/1014.png?ex=6a92b7e8&is=6a916668&hm=a96a455f618630acaa665a4af2dcb438271dd8eaea067fee700d065b760f54f7&=&format=webp&quality=lossless',
        'track': 'turf',
        'course': {'venue': 'Kyoto', 'surface': 'turf', 'distance_m': 2200, 'course_id': 3, 'direction': 'right'},
        'path': TRACK_PATHS['KYOTO_2200'],
        'fans': {'required': 10000, 'reward_first': 10500},
        'story': 'ผู้ปราชัยจักก้มลงสู่ธรณี เหตุเพราะเบื้องหน้าแย้ม ราชีรีแห่งกรีฑาสถาน',

    },
    'MileChampionship': {
        'name': 'Mile Championship (GI)',
        'thumnail': 'https://media.discordapp.net/attachments/1494730857259471030/1495055108503769119/thum_race_rt_000_1018_00.png?ex=69e4da12&is=69e38892&hm=9759f8c8444de9fdd8a4b4caefdb30ab909e4df33d7e66dae61f97e4b444912d&=&format=webp&quality=lossless&width=192&height=96',
        'image': 'https://media.discordapp.net/attachments/1494730857259471030/1495055108877189201/10805.png?ex=69e4da12&is=69e38892&hm=a6887c5def45a878eccb079f4aaaa57b027538a8161909939e488a87e0a3651a&=&format=webp&quality=lossless&width=1700&height=890',
        'track': 'turf',
        'course': {'venue': 'Kyoto', 'surface': 'turf', 'distance_m': 1600, 'course_id': 3, 'direction': 'right'},
        'path': TRACK_PATHS['KYOTO_1600'],
        'fans': {'required': 15000, 'reward_first': 11000},
        'story': '1,600 เมตรนี้ใครจะคมที่สุด ? ก็ต้องเป็นฉันอยู่แล้ว!',

    },
    'TennoShoSpring': {
        'name': 'Tenno Sho (Spring) (GI)',
        'thumnail': 'https://media.discordapp.net/attachments/1493695524812095489/1494219631861432391/thum_race_rt_000_1006_00.png?ex=69e1cff9&is=69e07e79&hm=c8eb47ad4d7d54d2369332b321100cd08b37b014505a00f27b2f046e6f3be98e&=&format=webp&quality=lossless&width=192&height=96',
        'image': 'https://media.discordapp.net/attachments/1493695524812095489/1494219666858704996/10811.png?ex=69e1d001&is=69e07e81&hm=2753992d6a484e9b83f1311b9e0c6488fa1108828c537d6ec3e1156d3beee76d&=&format=webp&quality=lossless&width=1532&height=890',
        'track': 'turf',
        'course': {'venue': 'Kyoto', 'surface': 'turf', 'distance_m': 3200, 'course_id': 3, 'direction': 'right'},
        'path': TRACK_PATHS['KYOTO_3200'],
        'fans': {'required': 20000, 'reward_first': 15000},
        'story': '3,200 เมตรแห่งความทรหด ยุทธการแย่งชิงโล่องค์จักรพรรดิของผู้แข็งแกร่ง',

    },
    'KyotoJuniorStakes': {
        'name': 'Kyoto Junior Stakes (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': 'https://media.discordapp.net/attachments/1494730857259471030/1502921213033451520/10807.png?ex=6a0766b4&is=6a061534&hm=50268c29a32b616fc0c480a8b2841ac631b5f32a210c9f77a5a3b5305bb0bef0&=&format=webp&quality=lossless&width=1481&height=875',
        'track': 'turf',
        'course': {'venue': 'Kyoto', 'surface': 'turf', 'distance_m': 2000, 'course_id': 2, 'direction': 'right'},
        'path': TRACK_PATHS['CUSTOM_KYOTOJUNIORSTAKES'],
        'fans': {'required': 350, 'reward_first': 3300},
        'story': 'GIII สำหรับสาวม้ารุ่น Junior ระยะ 2,000 เมตรที่ Kyoto.',

    },
    'Aoi Stakes': {
        'name': 'Aoi Stakes (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': 'https://media.discordapp.net/attachments/1494730857259471030/1504720667973779526/10801.png?ex=6a0803d3&is=6a06b253&hm=808b90a858437aa3092828076af6fc9f31194dec39ecf5e6767889482995bd7d&=&format=webp&quality=lossless&width=1194&height=875',
        'track': 'turf',
        'course': {'venue': 'Kyoto', 'surface': 'turf', 'distance_m': 1200, 'course_id': 2, 'direction': 'right'},
        'path': TRACK_PATHS['CUSTOM_AOI_STAKES'],
        'fans': {'required': 1250, 'reward_first': 3900},
        'story': 'GIII ระยะสปรินต์สำหรับสาวม้ารุ่น Classic ที่ Kyoto Racecourse.',

    },
    'ProcyonStakes': {
        'name': 'Procyon Stakes (GII)',
        'thumnail': G2_RACE_THUMBNAIL,
        'image': G2_RACE_THUMBNAIL,
        'track': 'dirt',
        'course': {'venue': 'Kyoto', 'surface': 'dirt', 'distance_m': 1800, 'direction': 'right'},
        'path': TRACK_PATHS['KYOTO_1800'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Procyon Stakes (GII) ที่สนาม Kyoto',

    },
    'SilkRoadStakes': {
        'name': 'Silk Road Stakes (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Kyoto', 'surface': 'turf', 'distance_m': 1200, 'direction': 'right'},
        'path': TRACK_PATHS['KYOTO_1200'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Silk Road Stakes (GIII) ที่สนาม Kyoto',

    },
    'KisaragiSho': {
        'name': 'Kisaragi Sho (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Kyoto', 'surface': 'turf', 'distance_m': 1800, 'direction': 'right'},
        'path': TRACK_PATHS['KYOTO_1800'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Kisaragi Sho (GIII) ที่สนาม Kyoto',

    },
    'HeianStakes': {
        'name': 'Heian Stakes (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'dirt',
        'course': {'venue': 'Kyoto', 'surface': 'dirt', 'distance_m': 1900, 'direction': 'right'},
        'path': TRACK_PATHS['KYOTO_2000'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Heian Stakes (GIII) ที่สนาม Kyoto',

    },
    'SwanStakes': {
        'name': 'MBS Sho Swan Stakes (GII)',
        'thumnail': G2_RACE_THUMBNAIL,
        'image': G2_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Kyoto', 'surface': 'turf', 'distance_m': 1400, 'direction': 'right'},
        'path': TRACK_PATHS['KYOTO_1400'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ MBS Sho Swan Stakes (GII) ที่สนาม Kyoto',

    },
    'FantasyStakes': {
        'name': 'KBS Kyoto Sho Fantasy Stakes (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Kyoto', 'surface': 'turf', 'distance_m': 1400, 'direction': 'right'},
        'path': TRACK_PATHS['KYOTO_1400'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ KBS Kyoto Sho Fantasy Stakes (GIII) ที่สนาม Kyoto',

    },
    'MiyakoStakes': {
        'name': 'Miyako Stakes (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'dirt',
        'course': {'venue': 'Kyoto', 'surface': 'dirt', 'distance_m': 1800, 'direction': 'right'},
        'path': TRACK_PATHS['KYOTO_1800'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Miyako Stakes (GIII) ที่สนาม Kyoto',

    },
    'KeihanHai': {
        'name': 'Keihan Hai (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Kyoto', 'surface': 'turf', 'distance_m': 1200, 'direction': 'right'},
        'path': TRACK_PATHS['KYOTO_1200'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Keihan Hai (GIII) ที่สนาม Kyoto',

    },
    'KyotoKimpai': {
        'name': 'Kyoto Kimpai (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Kyoto', 'surface': 'turf', 'distance_m': 1600, 'direction': 'right'},
        'path': TRACK_PATHS['KYOTO_1600'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Kyoto Kimpai (GIII) ที่สนาม Kyoto',

    },
    'ShinzanKinen': {
        'name': 'Shinzan Kinen (GIII)',
        'thumnail': G3_RACE_THUMBNAIL,
        'image': G3_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Kyoto', 'surface': 'turf', 'distance_m': 1600, 'direction': 'right'},
        'path': TRACK_PATHS['KYOTO_1600'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Shinzan Kinen (GIII) ที่สนาม Kyoto',

    },
    'NikkeiShinshunHai': {
        'name': 'Nikkei Shinshun Hai (GII)',
        'thumnail': G2_RACE_THUMBNAIL,
        'image': G2_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Kyoto', 'surface': 'turf', 'distance_m': 2400, 'direction': 'right'},
        'path': TRACK_PATHS['KYOTO_2400'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Nikkei Shinshun Hai (GII) ที่สนาม Kyoto',

    },
    'KyotoKinen': {
        'name': 'Kyoto Kinen (GII)',
        'thumnail': G2_RACE_THUMBNAIL,
        'image': G2_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Kyoto', 'surface': 'turf', 'distance_m': 2200, 'direction': 'right'},
        'path': TRACK_PATHS['KYOTO_2200'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Kyoto Kinen (GII) ที่สนาม Kyoto',

    },
    'MilersCup': {
        'name': 'Milers Cup (GII)',
        'thumnail': G2_RACE_THUMBNAIL,
        'image': G2_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Kyoto', 'surface': 'turf', 'distance_m': 1600, 'direction': 'right'},
        'path': TRACK_PATHS['KYOTO_1600'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Milers Cup (GII) ที่สนาม Kyoto',

    },
    'KyotoShimbunHai': {
        'name': 'Kyoto Shimbun Hai (GII)',
        'thumnail': G2_RACE_THUMBNAIL,
        'image': G2_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Kyoto', 'surface': 'turf', 'distance_m': 2200, 'direction': 'right'},
        'path': TRACK_PATHS['KYOTO_2200'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Kyoto Shimbun Hai (GII) ที่สนาม Kyoto',

    },
    'DailyHaiNisaiStakes': {
        'name': 'Daily Hai Nisai Stakes (GII)',
        'thumnail': G2_RACE_THUMBNAIL,
        'image': G2_RACE_THUMBNAIL,
        'track': 'turf',
        'course': {'venue': 'Kyoto', 'surface': 'turf', 'distance_m': 1600, 'direction': 'right'},
        'path': TRACK_PATHS['KYOTO_1600'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Daily Hai Nisai Stakes (GII) ที่สนาม Kyoto',

    },
}
