import asyncio
from utils.player_card import create_stats_card

# mock player data
player = {
    "username": "Fujimasa March",
    "speed": 4,
    "stamina": 1,
    "power": 3,
    "gut": 1,
    "wit": 1,
    "turf": 7,
    "dirt": 1,
    "sprint": 2,
    "mile": 3,
    "medium": 7,
    "long": 7,
    "front": 1,
    "pace": 2,
    "late": 3,
    "end_style": 7,

    "stats_point": 12,
    "uma_coin": 9999,
    "skill_point": 10,

}

avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"


async def main():
    card = await create_stats_card(player, avatar_url)

    # เซฟเป็นไฟล์
    card.save("test_output.png")
    print("สร้างภาพเสร็จแล้ว: test_output.png")


asyncio.run(main())