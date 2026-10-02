"""Race presets for Kawasaki."""

from utils.race.race_preset_constants import G2_RACE_THUMBNAIL, G3_RACE_THUMBNAIL

TRACK_PATHS = {'KAWASAKI_1600': [1, 1, 1, 2, 1, 1, 2, 1], 'KAWASAKI_2100': [1, 1, 1, 2, 1, 1, 2, 1, 1, 2, 1, 1]}


RACES = {
    'ZenNipponJuniorYushun': {
        'name': 'Zen-Nippon Junior Yushun (GI)',
        'thumnail': 'https://media.discordapp.net/attachments/1494730857259471030/1542852081600434329/11302.png?ex=6a92bc79&is=6a916af9&hm=795ce3d95c6123b6e9c229c0e4b37aa0044ead8af8258f9a59e2d940446331cb&=&format=webp&quality=lossless',
        'image': 'https://media.discordapp.net/attachments/1494730857259471030/1542851857108443167/1101.png?ex=6a92bc43&is=6a916ac3&hm=ff6e569752fcb8c9083ad82f4fb4df3a896901a0579046c9b058a75ac2f64003&=&format=webp&quality=lossless',
        'track': 'dirt',
        'course': {'venue': 'Kawasaki', 'surface': 'dirt', 'distance_m': 1600, 'course_id': 1, 'direction': 'left'},
        'path': TRACK_PATHS['KAWASAKI_1600'],
        'fans': {'required': 1000, 'reward_first': 4200},
        'story': 'คอยดูเถอะค่ะรุ่นพี่ สาวม้าสนามดืนเองก็มีของดีอยู่เหมือนกัน!',

    },
    'KawasakiKinen': {
        'name': 'Kawasaki Kinen (GI)',
        'thumnail': 'https://media.discordapp.net/attachments/1494730857259471030/1542852203637645343/11303.png?ex=6a92bc96&is=6a916b16&hm=f2965a405df3fd8c596d4f83839feb6bdce2702171d2b4ad4cc20de5aa3af6af&=&format=webp&quality=lossless',
        'image': 'https://media.discordapp.net/attachments/1494730857259471030/1542852203264348222/1107.png?ex=6a92bc96&is=6a916b16&hm=b86c41bbac734be28f3f930bed0444d13ed9a102a3a78ebf87c5e5f4dfcfd54c&=&format=webp&quality=lossless',
        'track': 'dirt',
        'course': {'venue': 'Kawasaki', 'surface': 'dirt', 'distance_m': 2100, 'course_id': 1, 'direction': 'left'},
        'path': TRACK_PATHS['KAWASAKI_2100'],
        'fans': {'required': 12000, 'reward_first': 6000},
        'story': 'โค้งแค๊บคาวาซากิ ร้องโอดกันทุกคน!',

    },
}
