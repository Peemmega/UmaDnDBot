from utils.race.race_dice import get_phase_from_turn

import random
from typing import Any


HYPE_OPENERS_NORMAL = [
    "เอาละครับ!",
    "มาแล้วครับ!",
    "จังหวะนี้เอง!",
]

HYPE_OPENERS_MEDIUM = [
    "เอาละครับ! เกมเริ่มเข้มข้นขึ้นแล้ว!",
    "มาแล้วครับ! จังหวะนี้เริ่มมีแรงกระเพื่อม!",
    "จังหวะนี้เอง! เริ่มมีการขยับอันดับแล้วครับ!",
]

HYPE_OPENERS_HIGH = [
    "เร็วมาก เร็วมาก! ไม่มีใครต้านไหวแล้ว!!",
    "จังหวะนี้เอง! พลิกขึ้นมาจริง ๆ!!",
    "เข้าสู่โค้งสุดท้ายแล้ว! และนี่คือการเร่งที่บ้าคลั่งสุด ๆ!",
]

FINISH_OPENERS = [
    "และนี่คือจุดสิ้นสุดของการแข่งขันครับ!",
    "เข้าเส้นชัยแล้วครับ!",
    "จบลงแล้วกับการแข่งขันสุดเดือดครั้งนี้!",
]

MOVEMENT_LINES = {
    "ขึ้นนำสำเร็จ": [
        "{name} แซงขึ้นนำได้แล้วครับ!!",
        "{name} พลิกขึ้นมาเป็นที่ 1 สำเร็จ!",
        "จังหวะนี้เอง! {name} ขึ้นนำแล้ว!",
    ],
    "แซงขึ้นแรง": [
        "{name} พุ่งขึ้นมาแรงมาก!",
        "{name} ไล่แซงแบบไม่เกรงใจใคร!",
        "{name} เร่งเครื่องขึ้นมาหลายอันดับ!",
    ],
    "อันดับร่วงหนัก": [
        "{name} เสียจังหวะอย่างหนัก!",
        "{name} หลุดฟอร์มไปพอสมควร!",
    ],
    "แต้มพุ่ง": [
        "{name} เร่งสปีดขึ้นมาอย่างบ้าคลั่ง!",
        "{name} คะแนนพุ่งแรงแบบผิดปกติ!",
    ],
}


def choose_opener(level: str, is_finish: bool = False) -> str:
    if is_finish:
        return "เข้าเส้นชัยแล้วครับ!!"

    if level == "high":
        return random.choice([
            "เร็วมาก เร็วมาก! ไม่มีใครต้านไหวแล้ว!!",
            "จังหวะนี้เอง! เกมกำลังเดือดสุด ๆ!",
            "โค้งสุดท้ายแล้วครับ! ใครจะอยู่ใครจะไป!",
        ])

    if level == "medium":
        return random.choice([
            "เริ่มเข้มข้นขึ้นแล้วครับ!",
            "เกมเริ่มมีจังหวะแล้ว!",
        ])

    return random.choice([
        "เอาละครับ!",
        "มาแล้วครับ!",
    ])


def prettify_local_lines(lines: list[str]) -> str:
    clean = [line.strip() for line in lines if line and line.strip()]
    return "\n".join(clean[:4])


def score_to_length(score_gap: int) -> float:
    return score_gap / 20.0

def format_length(score_gap: int) -> str:
    length = score_gap / 20.0

    if length <= 0:
        return "ตีคู่"
    if length < 0.5:
        return "ช่วงคอ"
    if length < 1.0:
        return "ช่วงตัว"
    if length < 3.0:
        return "ไม่ถึง 3 ช่วงตัว"
    if length < 4.0:
        return "ราว 3 ช่วงตัว"
    if length < 6.0:
        return f"ประมาณ {round(length)} ช่วงตัว"
    if length < 10.0:
        return f"ห่างอยู่ราว {round(length)} ช่วงตัว"
    return "ทิ้งห่างไปไกลมาก"

def format_gap_human(score_gap: int) -> str:
    length = score_gap / 20

    if length <= 0:
        return "ตีคู่กันอยู่!"
    if length < 0.5:
        return "ห่างแค่ช่วงคอ!"
    if length < 1:
        return "เบียดกันสุด ๆ!"
    if length < 2:
        return "ห่างแค่ประมาณ 1 ช่วงตัว!"
    if length < 4:
        return f"เริ่มมีระยะห่างราว {round(length)} ตัว"
    if length < 7:
        return "ทิ้งห่างพอสมควรแล้ว!"
    if length < 10:
        return "เริ่มหนีออกไปชัดเจน!"
    
    return "หนีห่างไปไกลมากแล้ว!!"

def get_race_stage_text(turn: int, max_turn: int) -> str:
    progress = turn / max_turn if max_turn > 0 else 0

    if progress <= 0.25:
        return "ช่วงต้นของการแข่งขัน"
    if progress <= 0.75:
        return "ช่วงกลางของการแข่งขัน"
    return "ช่วงท้ายของการแข่งขัน"


def is_first_turn_of_phase(turn: int, max_turn: int) -> bool:
    if turn <= 1:
        return True

    current_phase = get_phase_from_turn(turn, max_turn)
    prev_phase = get_phase_from_turn(turn - 1, max_turn)
    return current_phase != prev_phase, current_phase


def build_player_lookup(players: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {p["name"]: p for p in players}


def classify_movement(pos_delta: int, score_delta: int, pos: int) -> str:
    if pos == 1 and pos_delta > 0:
        return "ขึ้นนำสำเร็จ"
    if pos_delta >= 2:
        return "แซงขึ้นแรง"
    if pos_delta == 1:
        return "ขยับอันดับขึ้น"
    if pos_delta <= -2:
        return "อันดับร่วงหนัก"
    if pos_delta == -1:
        return "เสียอันดับ"
    if score_delta >= 25:
        return "แต้มพุ่ง"
    if score_delta <= 5:
        return "จังหวะยังไม่เปลี่ยนมาก"
    return "ทรงตัว"


def analyze_changes(
    previous_players: list[dict[str, Any]],
    current_players: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    prev_lookup = build_player_lookup(previous_players)
    analyzed: list[dict[str, Any]] = []

    for current in current_players:
        name = current["name"]
        prev = prev_lookup.get(name, {})

        prev_pos = prev.get("pos")
        prev_score = prev.get("score", 0)

        pos_delta = 0
        if prev_pos is not None:
            pos_delta = prev_pos - current["pos"]

        score_delta = current["score"] - prev_score
        gap_score = current.get("gap_from_leader", 0)

        analyzed.append({
            "name": name,
            "pos": current["pos"],
            "score": current["score"],
            "gap_from_leader": gap_score,
            "gap_text": format_length(gap_score),
            "score_delta": score_delta,
            "pos_delta": pos_delta,
            "movement_tag": classify_movement(pos_delta, score_delta, current["pos"]),
        })

    return analyzed


def pick_interesting_players(
    analyzed_players: list[dict[str, Any]],
    top_n: int = 3,
) -> list[dict[str, Any]]:
    def interest_score(player: dict[str, Any]) -> int:
        score = 0
        score += abs(player.get("pos_delta", 0)) * 100
        score += abs(player.get("score_delta", 0)) * 2

        if player.get("pos") == 1:
            score += 40
        if player.get("movement_tag") == "ขึ้นนำสำเร็จ":
            score += 80
        if player.get("movement_tag") == "แซงขึ้นแรง":
            score += 60
        if player.get("movement_tag") == "อันดับร่วงหนัก":
            score += 50

        return score

    return sorted(analyzed_players, key=interest_score, reverse=True)[:top_n]


def get_excitement_level(
    analyzed_players: list[dict[str, Any]],
    turn: int,
    max_turn: int,
    event_text: str | None = None,
) -> str:
    if not analyzed_players:
        return "normal"

    high_impact = False
    medium_impact = False

    for player in analyzed_players:
        pos_delta = abs(player.get("pos_delta", 0))
        score_delta = abs(player.get("score_delta", 0))
        gap_score = player.get("gap_from_leader", 999999)

        if player.get("movement_tag") in ["ขึ้นนำสำเร็จ", "แซงขึ้นแรง", "อันดับร่วงหนัก"]:
            high_impact = True

        if pos_delta >= 2 or score_delta >= 30:
            high_impact = True

        if pos_delta >= 1 or score_delta >= 15:
            medium_impact = True

        if turn >= max(1, int(max_turn * 0.75)) and gap_score <= 10:
            high_impact = True

    if event_text:
        strong_words = ["แซง", "ขึ้นนำ", "สกิล", "last spurt", "โค้งสุดท้าย", "ชัยชนะ", "พลิก"]
        event_text_lower = event_text.lower()
        if any(word in event_text_lower for word in strong_words):
            high_impact = True

    if high_impact:
        return "high"
    if medium_impact:
        return "medium"
    return "normal"


def build_event_line(event_text: str | None) -> str | None:
    if not event_text:
        return None
    return f"{event_text}!"

def build_leader_line(
    leader: dict[str, Any] | None,
    chaser: dict[str, Any] | None,
    stage_text: str,
) -> str:
    if not leader:
        return f"{stage_text} และการแข่งขันยังคงเข้มข้นครับ!"

    if chaser:
        gap_text = chaser.get("gap_text", "ไม่ไกล")
        return (
            f"{leader['name']} ยังนำอยู่ในตอนนี้! "
            f"ส่วน {chaser['name']} ไล่ตามมา{gap_text}!"
        )

    return f"{leader['name']} ยังครองตำแหน่งผู้นำได้อย่างเหนียวแน่นใน{stage_text}!"

def build_interest_line(player):
    tag = player.get("movement_tag")
    name = player["name"]

    if tag in MOVEMENT_LINES:
        return random.choice(MOVEMENT_LINES[tag]).format(name=name)

    return f"{name} ยังอยู่ในเกมได้ดี!"

def generate_local_commentary(
    previous_players,
    current_players,
    turn,
    max_turn,
    *,
    event_text=None,
):
    stage_text = get_race_stage_text(turn, max_turn)
    analyzed = analyze_changes(previous_players, current_players)
    interesting = pick_interesting_players(analyzed, top_n=2)
    level = get_excitement_level(analyzed, turn, max_turn, event_text=event_text)

    leader = min(analyzed, key=lambda p: p["pos"]) if analyzed else None
    chaser = next((p for p in analyzed if p["pos"] == 2), None)

    lines = []

    # 🔥 opener
    lines.append(choose_opener(level))

    # 🔥 event
    if event_text:
        lines.append(f"{event_text}!")

    # 🔥 leader
    if leader:
        leader_line = build_leader_line(leader, chaser, stage_text)
        lines.append(leader_line)

    # 🔥 highlight
    if interesting:
        lines.append(build_interest_line(interesting[0]))

    return prettify_local_lines(lines)


def generate_local_finish_commentary(
    final_players: list[dict[str, Any]],
    *,
    stage_name: str | None = None,
) -> str:
    if not final_players:
        return "การแข่งขันจบลงแล้วครับ!"

    winner = final_players[0]
    second = final_players[1] if len(final_players) > 1 else None

    lines = [choose_opener("high", is_finish=True)]

    if stage_name:
        lines.append(f"สนาม {stage_name} ปิดฉากลงอย่างเป็นทางการแล้วครับ!")

    if second:
        lines.append(
            f"ผู้ชนะในครั้งนี้คือ {winner['name']} "
            f"เข้าเส้นชัยเป็นอันดับ 1 และทิ้งห่าง {second['name']} อยู่ที่ {second.get('gap_text', 'ไม่ไกล')}!"
        )
    else:
        lines.append(f"ผู้ชนะในครั้งนี้คือ {winner['name']} คว้าชัยไปครองได้สำเร็จ!")

    lines.append(f"{winner['name']} ปิดเกมได้อย่างยอดเยี่ยมจริง ๆ!")

    return prettify_local_lines(lines)


async def generate_commentary(
    previous_players: list[dict[str, Any]],
    current_players: list[dict[str, Any]],
    turn: int,
    max_turn: int,
    *,
    event_text: str | None = None,
) -> str:
    return generate_local_commentary(
        previous_players,
        current_players,
        turn,
        max_turn,
        event_text=event_text,
    )


async def generate_finish_commentary(
    final_players: list[dict[str, Any]],
    *,
    stage_name: str | None = None,
) -> str:
    return generate_local_finish_commentary(
        final_players,
        stage_name=stage_name,
    )


def build_narrator_players_from_ranked(ranked_players: list[tuple[int, dict]]) -> list[dict[str, Any]]:
    if not ranked_players:
        return []

    leader_score = ranked_players[0][1].get("score", 0)
    result: list[dict[str, Any]] = []

    for index, (_, info) in enumerate(ranked_players, start=1):
        score = info.get("score", 0)

        # ✅ ใช้ username จาก playerInGame ก่อน
        player_name = (
            info.get("username")
            or info.get("display_name")
            or info.get("name")
            or f"Player {index}"
        )

        result.append({
            "name": player_name,
            "pos": index,
            "score": score,
            "gap_from_leader": leader_score - score,
            "gap_text": format_length(leader_score - score),
            "score_delta": 0,
            "pos_delta": 0,
            "movement_tag": "ผลการแข่งขันสุดท้าย",
        })

    return result



def convert_game_players_to_ranked_list(players: dict[int, dict[str, Any]]) -> list[dict[str, Any]]:
    ranked = sorted(
        players.items(),
        key=lambda item: item[1].get("score", 0),
        reverse=True
    )

    if not ranked:
        return []

    leader_score = ranked[0][1].get("score", 0)
    result: list[dict[str, Any]] = []

    for index, (_, info) in enumerate(ranked, start=1):
        score = info.get("score", 0)

        # ✅ ใช้ username จาก playerInGame ก่อน
        player_name = (
            info.get("username")
            or info.get("display_name")
            or info.get("name")
            or f"Player {index}"
        )

        result.append({
            "name": player_name,
            "pos": index,
            "score": score,
            "gap_from_leader": leader_score - score,
            "gap_text": format_length(leader_score - score),
        })

    return result