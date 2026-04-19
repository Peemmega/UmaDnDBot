import sys
import os
import asyncio

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.narrater import generate_commentary

if __name__ == "__main__":
    async def main():
        previous_players = [
            {"name": "Special Week", "pos": 1, "score": 120, "gap_from_leader": 0},
            {"name": "Silence Suzuka", "pos": 2, "score": 118, "gap_from_leader": 2},
            {"name": "Tokai Teio", "pos": 3, "score": 113, "gap_from_leader": 7},
            {"name": "Mejiro McQueen", "pos": 4, "score": 110, "gap_from_leader": 10},
            {"name": "Oguri Cap", "pos": 5, "score": 108, "gap_from_leader": 12},
            {"name": "Rice Shower", "pos": 6, "score": 106, "gap_from_leader": 14},
            {"name": "Gold Ship", "pos": 7, "score": 101, "gap_from_leader": 19},
            {"name": "Vodka", "pos": 8, "score": 99, "gap_from_leader": 21},
        ]

        current_players = [
            {"name": "Special Week", "pos": 2, "score": 140, "gap_from_leader": 3},
            {"name": "Silence Suzuka", "pos": 1, "score": 143, "gap_from_leader": 0},
            {"name": "Tokai Teio", "pos": 4, "score": 132, "gap_from_leader": 11},
            {"name": "Mejiro McQueen", "pos": 3, "score": 136, "gap_from_leader": 7},
            {"name": "Oguri Cap", "pos": 5, "score": 131, "gap_from_leader": 12},
            {"name": "Rice Shower", "pos": 6, "score": 127, "gap_from_leader": 16},
            {"name": "Gold Ship", "pos": 7, "score": 126, "gap_from_leader": 17},
            {"name": "Vodka", "pos": 8, "score": 118, "gap_from_leader": 25},
        ]

        text = await generate_commentary(
            previous_players,
            current_players,
            turn=7,
            max_turn=10,
            event_text="Silence Suzuka แซงขึ้นนำสำเร็จ"
        )
        print(text)

    asyncio.run(main())