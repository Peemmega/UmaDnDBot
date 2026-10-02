"""Race presets for Other."""

from utils.race.race_preset_constants import G2_RACE_THUMBNAIL, G3_RACE_THUMBNAIL

TRACK_PATHS = {'CUSTOM_TRAINING_TRACK_SHORT': [1, 1, 2, 2, 1, 1, 1, 1],
 'CUSTOM_TRAINING_TRACK_MEDIUM': [1, 1, 2, 2, 1, 1, 1, 2, 2, 1, 1, 1],
 'CUSTOM_TRAINING_TRACK_LONG': [1, 1, 3, 3, 2, 2, 4, 4, 1, 1, 1, 2, 2, 1, 1, 1]}


RACES = {
    'Training Track Short': {
        'name': 'Test Mile Short',
        'track': 'Turf',
        'background': 'training_track_temp.png',
        'preview_thumbnail_key': 'Debut',
        'thumnail': 'https://media.discordapp.net/attachments/1494730857259471030/1496520361968406598/thum_race_rt_000_9002_00.png?ex=69ed7a72&is=69ec28f2&hm=8306829b74f79dcfd3a6f7b65cef14fdd6c96dfa0f5d614b106e4ba11efa8c39&=&format=webp&quality=lossless&width=192&height=96',
        'image': 'https://cdn.discordapp.com/attachments/1494730857259471030/1543612932724629546/IMG_20260830_200719.jpg?ex=6a958112&is=6a942f92&hm=2e4c0e3f1d7203e59ebf1df07d486f1b816d774b7a4a5bcea7193b1371f713b4',
        'path': TRACK_PATHS['CUSTOM_TRAINING_TRACK_SHORT'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Test Mile Short ที่สนาม Other',
        'course': {'venue': 'Other', 'surface': 'Turf', 'distance_m': 1600},

    },
    'Training Track Medium': {
        'name': 'Training Track Medium',
        'background': 'training_track_temp.png',
        'preview_thumbnail_key': 'Debut',
        'thumnail': 'https://media.discordapp.net/attachments/1494730857259471030/1496520361968406598/thum_race_rt_000_9002_00.png?ex=69ed7a72&is=69ec28f2&hm=8306829b74f79dcfd3a6f7b65cef14fdd6c96dfa0f5d614b106e4ba11efa8c39&=&format=webp&quality=lossless&width=192&height=96',
        'image': 'https://cdn.discordapp.com/attachments/1494730857259471030/1543613505607831692/261_20260830173536.jpg?ex=6a95819a&is=6a94301a&hm=4835eacf66fc1010e86ef493d7b664146f3ac456034bc97cbfbb0ab4e091918e',
        'track': 'turf',
        'path': TRACK_PATHS['CUSTOM_TRAINING_TRACK_MEDIUM'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Training Track Medium ที่สนาม Other',
        'course': {'venue': 'Other', 'surface': 'turf', 'distance_m': 2000},

    },
    'Training Track Long': {
        'name': 'Training Track Long',
        'background': 'training_track_temp.png',
        'preview_thumbnail_key': 'Debut',
        'thumnail': 'https://media.discordapp.net/attachments/1494730857259471030/1496520361968406598/thum_race_rt_000_9002_00.png?ex=69ed7a72&is=69ec28f2&hm=8306829b74f79dcfd3a6f7b65cef14fdd6c96dfa0f5d614b106e4ba11efa8c39&=&format=webp&quality=lossless&width=192&height=96',
        'image': 'https://cdn.discordapp.com/attachments/1494730857259471030/1543613904138018886/261_20260830200253.jpg?ex=6a9581f9&is=6a943079&hm=a437747bae7f49b81d9b9636620d518cf2c35d9a146ddcd127a411cd5bb2e7b1',
        'track': 'turf',
        'path': TRACK_PATHS['CUSTOM_TRAINING_TRACK_LONG'],
        'fans': {'required': None, 'reward_first': None},
        'story': 'รายการ Training Track Long ที่สนาม Other',
        'course': {'venue': 'Other', 'surface': 'turf', 'distance_m': 3000},

    },
}
