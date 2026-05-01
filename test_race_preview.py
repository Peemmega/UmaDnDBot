import asyncio
from utils.race_dice_preview import create_race_dice_preview

# mock player
player = {
    "username": "Oguri Cap",
    "style": "Late",
    "current_max_speed": 28,

    "stamina_left": 9,
    "wit_mana": 150,
    "reroll_left": 2,
    "wit_reroll_left": 2,

    "image_url": "https://cdn.discordapp.com/embed/avatars/0.png"
}

# mock result (สำคัญมาก)
result = {
    "phase": 2,
    "turn": 2,
    "display": "28, 25",
    "bonus_display": "+21 +20 +15",
    "total": 81
}

async def main():
    card = await create_race_dice_preview(
        game_player=player,
        result=result,
        new_score=1244,
        path_label="ทางตรง",
        character_image_url=player["image_url"],

        # optional (ใส่ก็ได้ ไม่ใส่ก็ได้)
        stamina_before=10,
        stamina_after=9,
        wit_before=100,
        wit_after=150,
    )

    card.save("test_dice_preview.png")
    print("สร้างภาพเสร็จแล้ว: test_dice_preview.png")


asyncio.run(main())