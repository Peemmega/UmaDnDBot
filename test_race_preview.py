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
    "phase": 1,
    "turn": 2,
    "display": "28, 25",
    "bonus_display": "+21 +20 +15",
    "total": 181,
    "distance_color": "White",
    "new_score": 81
}

payload = {
    "stamina_note": "8",
    "new_score": 81
}

async def main():
    card = await create_race_dice_preview(
        game_player=player,
        result=result,
        payload=payload,
        path_label="ทางตรง",
        character_image_url=player["image_url"],
    )

    card.save("test_dice_preview.png")
    print("สร้างภาพเสร็จแล้ว: test_dice_preview.png")


asyncio.run(main())