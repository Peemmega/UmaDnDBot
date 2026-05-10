import argparse
import contextlib
import copy
import io
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from utils.game_manager import create_game, delete_game, games, run_bot_race_test
from utils.race.race_presets import RACE_PRESET


DEFAULT_STAGES = ("Test Mile", "Test Med", "Test Long")


def format_float(value: float) -> str:
    return f"{value:.2f}"


def get_player_name(player: dict) -> str:
    return (
        player.get("display_name")
        or player.get("username")
        or player.get("name")
        or "Unknown"
    )


def create_test_game(channel_id: int, stage_key: str) -> dict:
    success = create_game(channel_id, stage_key, owner_id=0)
    if not success:
        raise RuntimeError(f"Cannot create test game for stage: {stage_key}")

    game = games[channel_id]
    return game


def disable_player_skills(game: dict) -> None:
    for player in game["players"].values():
        player["skills"] = {}
        player["skill_cooldowns"] = {}


def flatten_player_stats(game: dict) -> None:
    base_stats = {
        "speed": 1,
        "stamina": 1,
        "power": 1,
        "gut": 1,
        "wit": 1,
    }

    for player in game["players"].values():
        race_profile = copy.deepcopy(player.get("race_profile", {}))
        for stat_name, value in base_stats.items():
            race_profile[stat_name] = value

        player["race_profile"] = race_profile
        player["stamina_left"] = 9
        player["wit_mana"] = 106


def print_stage_setup(stage_key: str, game: dict) -> None:
    stage = RACE_PRESET[stage_key]
    print(f"\n=== {stage_key} setup ===")
    print(f"Name: {stage.get('name')}")
    print(f"Distance: {stage.get('distance')} | Track: {stage.get('track')} | Turns: {stage.get('turn')}")
    print(f"Path: {stage.get('path')}")
    print("Players:")

    for player_id, player in game["players"].items():
        skills = player.get("skills", {})
        skill_text = ", ".join(str(skill_id) for skill_id in skills.values() if skill_id)
        print(
            f"- {player_id}: {get_player_name(player)} | "
            f"{player.get('style')} | skills: {skill_text or '-'}"
        )


def run_single_race(
    channel_id: int,
    stage_key: str,
    *,
    show_logs: bool,
    debug_ai: bool,
    zone_only: bool,
    flat_stats: bool,
) -> dict:
    game = create_test_game(channel_id, stage_key)

    if zone_only:
        disable_player_skills(game)

    if flat_stats:
        flatten_player_stats(game)

    if show_logs:
        print_stage_setup(stage_key, game)

    output = io.StringIO()
    stdout_context = contextlib.nullcontext() if debug_ai else contextlib.redirect_stdout(output)

    with stdout_context:
        success, payload = run_bot_race_test(channel_id)

    if not success:
        raise RuntimeError(payload.get("message", f"Race test failed: {stage_key}"))

    ranked_players = payload["ranked_players"]
    winner_id, winner = ranked_players[0]

    result = {
        "stage_key": stage_key,
        "winner_style": winner.get("style"),
        "winner_name": get_player_name(winner),
        "ranked_players": ranked_players,
        "turn_score_logs": payload.get("turn_score_logs", []),
    }

    if show_logs:
        print(f"\n=== {stage_key} result ===")
        for index, (player_id, player) in enumerate(ranked_players, start=1):
            print(
                f"{index}. {get_player_name(player)} | "
                f"{player.get('style')} | score: {player.get('score', 0)}"
            )

        if result["turn_score_logs"]:
            print("\nTurn logs:")
            for log in result["turn_score_logs"]:
                roll = log.get("roll") or {}
                skills = log.get("skills") or []
                skill_text = ", ".join(skill.get("id", "?") for skill in skills)
                roll_text = ""
                if roll:
                    roll_text = (
                        f" | P{roll.get('phase')} "
                        f"{roll.get('distance_color')} {roll.get('rule')}"
                    )
                if skill_text:
                    roll_text += f" | skills: {skill_text}"

                print(
                    f"T{log.get('turn')} {log.get('name')} "
                    f"+{log.get('gain')} => {log.get('score_after')}{roll_text}"
                )

    delete_game(channel_id)
    return result


def summarize_stage(stage_key: str, results: list[dict]) -> None:
    wins = Counter(result["winner_style"] for result in results)
    winner_names = Counter(result["winner_name"] for result in results)
    scores_by_style = defaultdict(list)
    places_by_style = defaultdict(list)

    for result in results:
        for place, (_, player) in enumerate(result["ranked_players"], start=1):
            style = player.get("style")
            scores_by_style[style].append(player.get("score", 0))
            places_by_style[style].append(place)

    print(f"\n=== {stage_key} summary ({len(results)} run(s)) ===")
    print("Wins by style:")
    for style, count in wins.most_common():
        print(f"- {style}: {count}")

    print("Average by style:")
    for style in sorted(scores_by_style):
        print(
            f"- {style}: avg score {format_float(mean(scores_by_style[style]))}, "
            f"avg place {format_float(mean(places_by_style[style]))}"
        )

    print("Top winners:")
    for name, count in winner_names.most_common(8):
        print(f"- {name}: {count}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run prepared bot race tests for Test Mile and Test Med."
    )
    parser.add_argument(
        "--stage",
        choices=DEFAULT_STAGES,
        action="append",
        help="Stage to run. Can be passed multiple times. Default: Test Mile and Test Med.",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=1,
        help="Number of simulations per stage.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducible results.",
    )
    parser.add_argument(
        "--logs",
        action="store_true",
        help="Print player setup, ranking, and turn logs for each run.",
    )
    parser.add_argument(
        "--debug-ai",
        action="store_true",
        help="Allow mob AI debug prints if enabled in game code.",
    )
    parser.add_argument(
        "--zone-only",
        action="store_true",
        help="Disable equipped skills for the run. Zone effects are still allowed.",
    )
    parser.add_argument(
        "--flat-stats",
        action="store_true",
        help="Set speed/stamina/power/gut/wit to 1 for every player before the run.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    stages = tuple(args.stage or DEFAULT_STAGES)

    if args.runs < 1:
        raise SystemExit("--runs must be at least 1")

    if args.seed is not None:
        random.seed(args.seed)

    base_channel_id = 990000000

    for stage_index, stage_key in enumerate(stages):
        results = []

        for run_index in range(args.runs):
            channel_id = base_channel_id + (stage_index * 100000) + run_index
            if channel_id in games:
                delete_game(channel_id)

            result = run_single_race(
                channel_id,
                stage_key,
                show_logs=args.logs,
                debug_ai=args.debug_ai,
                zone_only=args.zone_only,
                flat_stats=args.flat_stats,
            )
            results.append(result)

        summarize_stage(stage_key, results)


if __name__ == "__main__":
    main()
