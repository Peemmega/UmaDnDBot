import random
from typing import Any


def format_length(score_gap: int) -> str:
    length = score_gap / 20.0

    if score_gap <= 0:
        return "ตีคู่"
    if length < 0.5:
        return "แค่ช่วงคอ"
    if length < 1:
        return "ไม่ถึงช่วงตัว"
    if length < 2:
        return "ราว 1 ช่วงตัว"
    if length < 4:
        return f"ประมาณ {round(length)} ช่วงตัว"
    if length < 7:
        return f"ราว {round(length)} ช่วงตัว"
    if length < 10:
        return f"ห่างประมาณ {round(length)} ช่วงตัว"
    return "ทิ้งห่างไปไกลมาก"


def get_race_stage_text(turn: int, max_turn: int) -> str:
    progress = turn / max_turn if max_turn > 0 else 0

    if progress <= 0.25:
        return "ต้นเกม"
    if progress <= 0.5:
        return "ช่วงตั้งจังหวะ"
    if progress <= 0.75:
        return "กลางถึงปลายเกม"
    if turn >= max_turn:
        return "โค้งสุดท้าย"
    return "ช่วงท้าย"


def prettify_local_lines(lines: list[str], limit: int = 4) -> str:
    clean: list[str] = []
    seen = set()

    for line in lines:
        text = " ".join(str(line).split())
        if not text or text in seen:
            continue
        clean.append(text)
        seen.add(text)

    return "\n".join(clean[:limit])


def build_player_lookup(players: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {player["name"]: player for player in players}


def classify_movement(pos_delta: int, score_delta: int, pos: int) -> str:
    if pos == 1 and pos_delta > 0:
        return "take_lead"
    if pos_delta >= 2:
        return "big_climb"
    if pos_delta == 1:
        return "climb"
    if pos_delta <= -2:
        return "big_drop"
    if pos_delta == -1:
        return "drop"
    if score_delta >= 45:
        return "huge_gain"
    if score_delta >= 25:
        return "gain"
    if score_delta <= 5:
        return "quiet"
    return "steady"


def analyze_changes(
    previous_players: list[dict[str, Any]],
    current_players: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    previous_lookup = build_player_lookup(previous_players)
    analyzed: list[dict[str, Any]] = []

    for current in current_players:
        previous = previous_lookup.get(current["name"], {})
        previous_pos = previous.get("pos")
        previous_score = previous.get("score", current.get("score", 0))

        pos_delta = 0
        if previous_pos is not None:
            pos_delta = previous_pos - current["pos"]

        score_delta = current.get("score", 0) - previous_score
        gap_score = current.get("gap_from_leader", 0)

        analyzed.append({
            **current,
            "gap_text": format_length(gap_score),
            "score_delta": score_delta,
            "pos_delta": pos_delta,
            "movement_tag": classify_movement(pos_delta, score_delta, current["pos"]),
        })

    return analyzed


def get_excitement_level(analyzed_players: list[dict[str, Any]], turn: int, max_turn: int) -> str:
    if not analyzed_players:
        return "normal"

    lead_gap = analyzed_players[1]["gap_from_leader"] if len(analyzed_players) > 1 else 999
    max_pos_delta = max(abs(player.get("pos_delta", 0)) for player in analyzed_players)
    max_gain = max(player.get("score_delta", 0) for player in analyzed_players)
    late_race = turn >= max(1, int(max_turn * 0.7))

    if max_pos_delta >= 2 or max_gain >= 50 or (late_race and lead_gap <= 20):
        return "high"
    if max_pos_delta >= 1 or max_gain >= 25 or lead_gap <= 20:
        return "medium"
    return "normal"


def choose_opener(level: str, turn: int, max_turn: int) -> str:
    stage = get_race_stage_text(turn, max_turn)

    if level == "high":
        return random.choice([
            f"{stage}เดือดขึ้นมาทันที จังหวะนี้อันดับเริ่มสั่นแล้ว",
            f"เข้าสู่{stage}แล้วเกมเปิดหน้าแลกกันชัดเจน",
            f"บรรยากาศตอนนี้ตึงมาก ทุกแต้มเริ่มมีน้ำหนักแล้ว",
        ])

    if level == "medium":
        return random.choice([
            f"{stage}เริ่มมีแรงกดดันมากขึ้น กลุ่มนำยังหนีไม่ขาด",
            f"จังหวะนี้เกมเริ่มขยับ มีคนเร่งขึ้นมาท้าทายแล้ว",
            f"ภาพรวมยังสูสี แต่เริ่มเห็นคนที่มีแรงปลายชัดขึ้น",
        ])

    return random.choice([
        f"{stage}ยังเป็นช่วงคุมจังหวะ ทุกคนกำลังหาโอกาสของตัวเอง",
        f"เกมยังไม่เปิดเต็มที่ แต่ตำแหน่งในกลุ่มเริ่มมีความหมายแล้ว",
        f"สนามยังนิ่งในภาพรวม แต่ช่องว่างเล็ก ๆ เริ่มก่อตัวขึ้น",
    ])


def build_event_line(event_text: str | None) -> str | None:
    if not event_text:
        return None
    return event_text.rstrip("!。.!") + "!"


def build_leader_line(analyzed_players: list[dict[str, Any]]) -> str | None:
    if not analyzed_players:
        return None

    leader = analyzed_players[0]
    chaser = analyzed_players[1] if len(analyzed_players) > 1 else None

    if not chaser:
        return f"{leader['name']} วิ่งอยู่คนเดียวแบบไม่ต้องมองหลัง"

    gap = chaser.get("gap_from_leader", 0)
    gap_text = chaser.get("gap_text", "ไม่ไกล")

    if gap <= 0:
        return f"{leader['name']} กับ {chaser['name']} แทบจะตีคู่กันอยู่ หายใจรดต้นคอกันแล้ว"
    if gap <= 20:
        return f"{leader['name']} ยังนำอยู่ แต่ {chaser['name']} จี้มาในระยะ {gap_text} เท่านั้น"
    if gap <= 60:
        return f"{leader['name']} ยืนหัวแถวได้ดี ส่วน {chaser['name']} ยังตามมาในระยะ {gap_text}"
    return f"{leader['name']} เริ่มฉีกหนีออกไปแล้ว ช่องว่างกับ {chaser['name']} อยู่ที่ {gap_text}"


def build_momentum_line(analyzed_players: list[dict[str, Any]]) -> str | None:
    if not analyzed_players:
        return None

    movers = [
        player for player in analyzed_players
        if player.get("pos_delta", 0) > 0 or player.get("score_delta", 0) >= 20
    ]

    if not movers:
        quiet = analyzed_players[0]
        return f"{quiet['name']} ยังประคองจังหวะได้แน่น แต่ด้านหลังยังไม่มีใครยอมปล่อยให้หนีง่าย ๆ"

    def momentum_score(player: dict[str, Any]) -> int:
        return player.get("pos_delta", 0) * 40 + player.get("score_delta", 0)

    player = max(movers, key=momentum_score)
    name = player["name"]
    pos_delta = player.get("pos_delta", 0)
    score_delta = player.get("score_delta", 0)
    tag = player.get("movement_tag")

    if tag == "take_lead":
        return f"{name} เร่งจนแซงขึ้นหัวแถวได้สำเร็จ เทิร์นนี้เปลี่ยนจังหวะเกมไปเลย"
    if pos_delta >= 2:
        return f"{name} ไต่ขึ้นมาทีเดียว {pos_delta} อันดับ แรงส่งตอนนี้น่ากลัวมาก"
    if pos_delta == 1:
        return f"{name} ขยับขึ้นมา 1 อันดับแบบเนียน ๆ แต่แต้มที่บวกมา {score_delta} ทำให้ต้องจับตา"
    if score_delta >= 45:
        return f"{name} กดแต้มเทิร์นนี้หนักมาก บวก {score_delta} แต้มจนระยะด้านหน้าเริ่มหดลง"
    return f"{name} ทำแต้มเพิ่ม {score_delta} แต้ม ยังรักษาแรงไล่ได้ต่อเนื่อง"


def build_pressure_line(analyzed_players: list[dict[str, Any]]) -> str | None:
    if len(analyzed_players) < 3:
        return None

    close_pack = [
        player for player in analyzed_players[:4]
        if player.get("gap_from_leader", 999) <= 40
    ]
    dropper = min(analyzed_players, key=lambda player: player.get("pos_delta", 0))

    if len(close_pack) >= 3:
        names = ", ".join(player["name"] for player in close_pack[:3])
        return f"กลุ่มหน้าอย่าง {names} ยังอยู่ในระยะที่พลาดนิดเดียวอันดับสลับได้ทันที"

    if dropper.get("pos_delta", 0) <= -2:
        return f"{dropper['name']} เสียตำแหน่งลงไป {abs(dropper['pos_delta'])} อันดับ ต้องรีบหาจังหวะกลับมา"

    return None


def generate_local_commentary(
    previous_players: list[dict[str, Any]],
    current_players: list[dict[str, Any]],
    turn: int,
    max_turn: int,
    *,
    event_text: str | None = None,
) -> str:
    analyzed = analyze_changes(previous_players, current_players)
    level = get_excitement_level(analyzed, turn, max_turn)

    lines = [
        choose_opener(level, turn, max_turn),
        build_event_line(event_text),
        build_leader_line(analyzed),
        build_momentum_line(analyzed),
        build_pressure_line(analyzed),
    ]

    return prettify_local_lines([line for line in lines if line])


def generate_local_finish_commentary(
    final_players: list[dict[str, Any]],
    *,
    stage_name: str | None = None,
) -> str:
    if not final_players:
        return "การแข่งขันจบลงแล้ว แต่ยังไม่มีข้อมูลผู้เข้าเส้นชัย"

    winner = final_players[0]
    second = final_players[1] if len(final_players) > 1 else None
    third = final_players[2] if len(final_players) > 2 else None

    lines = []
    if stage_name:
        lines.append(f"{stage_name} ปิดฉากลงแล้ว และคนที่ยืนอยู่หน้าสุดคือ {winner['name']}")
    else:
        lines.append(f"เข้าเส้นชัยแล้ว คนที่ยืนอยู่หน้าสุดคือ {winner['name']}")

    if second:
        gap = second.get("gap_from_leader", 0)
        if gap <= 20:
            lines.append(f"{second['name']} ไล่มาจนเกือบถึง เส้นชัยตัดสินกันแค่ {second.get('gap_text', 'ระยะสั้นมาก')}")
        else:
            lines.append(f"{winner['name']} ทิ้ง {second['name']} ไว้ที่ {second.get('gap_text', 'ระยะหนึ่ง')} และปิดเกมได้เด็ดขาด")

    if third:
        lines.append(f"ส่วน {third['name']} เก็บโพเดียมอันดับ 3 ได้สำเร็จ ทำให้กลุ่มหน้าแข่งกันเข้มจนถึงท้ายสนาม")

    lines.append(f"ชัยชนะนี้เป็นของ {winner['name']} แบบที่ทั้งสนามต้องจำชื่อไว้")
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


def build_narrator_players_from_ranked(
    ranked_players: list[tuple[int, dict]],
    score_overrides: dict[Any, int] | None = None,
) -> list[dict[str, Any]]:
    if not ranked_players:
        return []

    score_overrides = score_overrides or {}

    normalized = []
    for index, (user_id, info) in enumerate(ranked_players, start=1):
        score = score_overrides.get(user_id, info.get("score", 0))
        player_name = (
            info.get("username")
            or info.get("display_name")
            or info.get("name")
            or f"Player {index}"
        )
        normalized.append((user_id, info, player_name, score))

    normalized.sort(key=lambda item: item[3], reverse=True)
    leader_score = normalized[0][3]

    result: list[dict[str, Any]] = []
    for index, (_, info, player_name, score) in enumerate(normalized, start=1):
        gap = leader_score - score
        result.append({
            "name": player_name,
            "style": info.get("style"),
            "pos": index,
            "score": score,
            "gap_from_leader": gap,
            "gap_text": format_length(gap),
            "score_delta": 0,
            "pos_delta": 0,
            "movement_tag": "final",
        })

    return result


def convert_game_players_to_ranked_list(players: dict[int, dict[str, Any]]) -> list[dict[str, Any]]:
    ranked = sorted(
        players.items(),
        key=lambda item: item[1].get("score", 0),
        reverse=True
    )

    return build_narrator_players_from_ranked(ranked)
