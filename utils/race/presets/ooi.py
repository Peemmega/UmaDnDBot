"""Race presets for Ooi."""

from utils.race.race_preset_constants import G2_RACE_THUMBNAIL, G3_RACE_THUMBNAIL

TRACK_PATHS = {'OOI_2000': [1, 1, 1, 2, 2, 1, 1, 1, 2, 2, 1, 1]}


RACES = {
    'JapanDirtDerby': {
        'name': 'Japan Dirt Derby (GI)',
        'thumnail': 'https://media.discordapp.net/attachments/1494730857259471030/1542851351405666304/11103.png?ex=6a92bbca&is=6a916a4a&hm=cd7e27f6c05ef85a51c87646182fd7f87ff63d481ed85b6d3841e2dd759975ba&=&format=webp&quality=lossless',
        'image': 'https://media.discordapp.net/attachments/1494730857259471030/1542851350952550431/1102.png?ex=6a92bbca&is=6a916a4a&hm=74cd50ffddf2f561f3cc7cb78c3688ff47f9d2f1f2650223f43454fa4ef6eda4&=&format=webp&quality=lossless',
        'track': 'dirt',
        'course': {'venue': 'Ooi', 'surface': 'dirt', 'distance_m': 2000, 'course_id': 1, 'direction': 'right'},
        'path': TRACK_PATHS['OOI_2000'],
        'fans': {'required': 4000, 'reward_first': 4500},
        'story': 'อย่าได้ลืมซะล่ะ สามมงกุฎเองก็มีสายดินเหมือนกันนะคะ!',

    },
    'TokyoDaishoten': {
        'name': 'Tokyo Daishoten (GI)',
        'thumnail': 'https://media.discordapp.net/attachments/1494730857259471030/1542851351405666304/11103.png?ex=6a92bbca&is=6a916a4a&hm=cd7e27f6c05ef85a51c87646182fd7f87ff63d481ed85b6d3841e2dd759975ba&=&format=webp&quality=lossless',
        'image': 'https://media.discordapp.net/attachments/1494730857259471030/1542851772328972299/1106.png?ex=6a92bc2f&is=6a916aaf&hm=037193dfc721e8d021415c47566cbb5e1f7daae304637d7189a983ff1648dc95&=&format=webp&quality=lossless',
        'track': 'dirt',
        'course': {'venue': 'Ooi', 'surface': 'dirt', 'distance_m': 2000, 'course_id': 1, 'direction': 'right'},
        'path': TRACK_PATHS['OOI_2000'],
        'fans': {'required': 12000, 'reward_first': 8000},
        'story': 'บทสรุปขิงเจ้าแห่งฝุ่น ไม่ว่าจะมากจากที่ใด ฉันจะปดขยี้มันเอง',

    },
    'TeioSho': {
        'name': 'Teio Sho (GI)',
        'thumnail': 'https://media.discordapp.net/attachments/1494730857259471030/1542851351405666304/11103.png?ex=6a92bbca&is=6a916a4a&hm=cd7e27f6c05ef85a51c87646182fd7f87ff63d481ed85b6d3841e2dd759975ba&=&format=webp&quality=lossless',
        'image': 'https://media.discordapp.net/attachments/1494730857259471030/1542851857108443167/1101.png?ex=6a92bc43&is=6a916ac3&hm=ff6e569752fcb8c9083ad82f4fb4df3a896901a0579046c9b058a75ac2f64003&=&format=webp&quality=lossless',
        'track': 'dirt',
        'course': {'venue': 'Ooi', 'surface': 'dirt', 'distance_m': 2000, 'course_id': 1, 'direction': 'right'},
        'path': TRACK_PATHS['OOI_2000'],
        'fans': {'required': 12000, 'reward_first': 6000},
        'story': 'มาโชว์ลวดลายยามค่ำกันหน่อยทุกโค๊น!',

    },
}
