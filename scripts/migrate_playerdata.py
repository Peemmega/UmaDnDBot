"""Move player stats/aptitudes and skills/zones into dedicated SQLite tables.

Stop all application writers before applying. Dry-run uses an in-memory backup;
apply creates a SQLite Backup API copy and rehearses against that exact copy.
"""
import argparse
from contextlib import closing
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sqlite3


STATS_FIELDS = (
    "speed", "stamina", "power", "gut", "wit", "turf", "dirt", "sprint",
    "mile", "medium", "long", "front", "pace", "late", "end_style",
    "stats_point",
)
SKILL_ZONE_FIELDS = (
    "fans", "skill_point", "skill_slot_1", "skill_slot_2", "skill_slot_3",
    "skill_slot_4", "default_skill_loadout_seeded", "zone_name",
    "zone_image_url", "zone_points", "zone_build", "legacy_uma_coin",
)
IDENTITY_FIELDS = ("user_id", "username", "profile_image_url", "profile_image_updated_at")
DEFAULT_SKILLS = ("rec_010", "rec_011", "vel_023", "vel_024")
DEFAULT_ZONE_IMAGE = "https://media.discordapp.net/attachments/697810514448744448/1495378081085657162/tm_zone.gif"
VERSION = "playerdata_v1"


def checked(conn):
    integrity = [row[0] for row in conn.execute("PRAGMA integrity_check")]
    foreign = list(conn.execute("PRAGMA foreign_key_check"))
    if integrity != ["ok"] or foreign:
        raise RuntimeError(
            f"Database checks failed: integrity={integrity}, foreign key violations={len(foreign)}"
        )


def source_snapshot(conn):
    columns = [tuple(row) for row in conn.execute("PRAGMA table_info(players)")]
    if not columns:
        raise RuntimeError("Missing players table")
    rows = sorted(
        (tuple(row) for row in conn.execute("SELECT * FROM players")), key=repr
    )
    return columns, rows


def _value(row, field, default):
    return row[field] if field in row else default


def migrate(conn):
    conn.row_factory = sqlite3.Row
    objects = {
        row["name"]: row["type"]
        for row in conn.execute("SELECT name, type FROM sqlite_master WHERE name NOT LIKE 'sqlite_%'")
    }
    if objects.get("players") != "table":
        raise RuntimeError("Expected the legacy players table")
    if any(name in objects for name in ("player_stats_aptitude", "player_skill_zone", "playerdata")):
        raise RuntimeError("Player data target objects already exist; refusing to overwrite")

    columns = {row[1] for row in conn.execute("PRAGMA table_info(players)")}
    required_identity = {"user_id", "username"}
    if not required_identity <= columns:
        raise RuntimeError("Unexpected players schema: user_id and username are required")
    known = set(IDENTITY_FIELDS) | set(STATS_FIELDS) | set(SKILL_ZONE_FIELDS) | {"uma_coin"}
    unknown = columns - known
    if unknown:
        raise RuntimeError(f"Unexpected players columns; review before migration: {sorted(unknown)}")

    incoming_foreign_keys = []
    for table, kind in objects.items():
        if kind != "table" or table == "players":
            continue
        for fk in conn.execute(f'PRAGMA foreign_key_list("{table}")'):
            if fk["table"] == "players":
                incoming_foreign_keys.append(table)
                break
    if incoming_foreign_keys:
        raise RuntimeError(
            "Other tables reference players and need an explicit foreign-key migration: "
            + ", ".join(sorted(incoming_foreign_keys))
        )
    if conn.execute("SELECT 1 FROM sqlite_master WHERE type IN ('index','trigger') AND tbl_name='players' AND name NOT LIKE 'sqlite_%'").fetchone():
        raise RuntimeError("Custom players indexes/triggers need an explicit migration")

    old_rows = [dict(row) for row in conn.execute("SELECT * FROM players")]
    player_sql = """CREATE TABLE players_new (
        user_id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        profile_image_url TEXT,
        profile_image_updated_at INTEGER
    )"""
    stats_sql = """CREATE TABLE player_stats_aptitude_new (
        user_id INTEGER PRIMARY KEY REFERENCES players_new(user_id) ON DELETE CASCADE,
        speed INTEGER NOT NULL DEFAULT 1, stamina INTEGER NOT NULL DEFAULT 1,
        power INTEGER NOT NULL DEFAULT 1, gut INTEGER NOT NULL DEFAULT 1,
        wit INTEGER NOT NULL DEFAULT 1, turf INTEGER NOT NULL DEFAULT 1,
        dirt INTEGER NOT NULL DEFAULT 1, sprint INTEGER NOT NULL DEFAULT 1,
        mile INTEGER NOT NULL DEFAULT 1, medium INTEGER NOT NULL DEFAULT 1,
        long INTEGER NOT NULL DEFAULT 1, front INTEGER NOT NULL DEFAULT 1,
        pace INTEGER NOT NULL DEFAULT 1, late INTEGER NOT NULL DEFAULT 1,
        end_style INTEGER NOT NULL DEFAULT 1, stats_point INTEGER NOT NULL DEFAULT 5
    )"""
    zone_sql = f"""CREATE TABLE player_skill_zone_new (
        user_id INTEGER PRIMARY KEY REFERENCES players_new(user_id) ON DELETE CASCADE,
        fans INTEGER NOT NULL DEFAULT 1, skill_point INTEGER NOT NULL DEFAULT 12,
        skill_slot_1 TEXT, skill_slot_2 TEXT, skill_slot_3 TEXT, skill_slot_4 TEXT,
        default_skill_loadout_seeded INTEGER NOT NULL DEFAULT 0,
        zone_name TEXT DEFAULT 'Default Zone', zone_image_url TEXT DEFAULT '{DEFAULT_ZONE_IMAGE}',
        zone_points INTEGER NOT NULL DEFAULT 5, zone_build TEXT DEFAULT ('{{}}'),
        legacy_uma_coin INTEGER
    )"""
    conn.execute(player_sql)
    conn.execute(stats_sql)
    conn.execute(zone_sql)

    stats_rows, zone_rows = [], []
    for row in old_rows:
        if "fans" in columns:
            fans = _value(row, "fans", 1)
        elif "uma_coin" in columns:
            fans = row.get("uma_coin") if (row.get("uma_coin") or 0) > 0 else 1
        else:
            fans = 1
        slots = [_value(row, f"skill_slot_{slot}", None) for slot in range(1, 5)]
        seeded = int(_value(row, "default_skill_loadout_seeded", 0) or 0)
        if not seeded and not any(slots):
            slots = list(DEFAULT_SKILLS)
            seeded = 1
        elif any(slots):
            seeded = 1

        conn.execute(
            "INSERT INTO players_new VALUES (?, ?, ?, ?)",
            (row["user_id"], row["username"], row.get("profile_image_url"), row.get("profile_image_updated_at")),
        )
        stats_values = [
            _value(row, field, 5 if field == "stats_point" else 1)
            for field in STATS_FIELDS
        ]
        conn.execute(
            f"INSERT INTO player_stats_aptitude_new (user_id, {', '.join(STATS_FIELDS)}) "
            f"VALUES ({', '.join('?' for _ in range(1 + len(STATS_FIELDS)))})",
            (row["user_id"], *stats_values),
        )
        zone_values = {
            "fans": fans,
            "skill_point": _value(row, "skill_point", 12),
            "default_skill_loadout_seeded": seeded,
            "zone_name": _value(row, "zone_name", "Default Zone"),
            "zone_image_url": _value(row, "zone_image_url", DEFAULT_ZONE_IMAGE),
            "zone_points": _value(row, "zone_points", 5),
            "zone_build": _value(row, "zone_build", "{}"),
            "legacy_uma_coin": row.get("uma_coin"),
        }
        zone_values.update({f"skill_slot_{slot}": slots[slot - 1] for slot in range(1, 5)})
        zone_columns = ("fans", "skill_point", "skill_slot_1", "skill_slot_2", "skill_slot_3", "skill_slot_4", "default_skill_loadout_seeded", "zone_name", "zone_image_url", "zone_points", "zone_build", "legacy_uma_coin")
        conn.execute(
            f"INSERT INTO player_skill_zone_new (user_id, {', '.join(zone_columns)}) "
            f"VALUES ({', '.join('?' for _ in range(1 + len(zone_columns)))})",
            (row["user_id"], *(zone_values[field] for field in zone_columns)),
        )
        stats_rows.append((row["user_id"], *stats_values))
        zone_rows.append((row["user_id"], *(zone_values[field] for field in zone_columns)))

    old_count = len(old_rows)
    if conn.execute("SELECT COUNT(*) FROM players_new").fetchone()[0] != old_count:
        raise RuntimeError("Player identity count mismatch")
    if conn.execute("SELECT COUNT(*) FROM player_stats_aptitude_new").fetchone()[0] != old_count:
        raise RuntimeError("Stats/Aptitude row count mismatch")
    if conn.execute("SELECT COUNT(*) FROM player_skill_zone_new").fetchone()[0] != old_count:
        raise RuntimeError("Skill/Zone row count mismatch")
    actual_stats = [tuple(row) for row in conn.execute(
        f"SELECT user_id, {', '.join(STATS_FIELDS)} FROM player_stats_aptitude_new ORDER BY user_id"
    )]
    actual_zone = [tuple(row) for row in conn.execute(
        "SELECT user_id, fans, skill_point, skill_slot_1, skill_slot_2, skill_slot_3, skill_slot_4, "
        "default_skill_loadout_seeded, zone_name, zone_image_url, zone_points, zone_build, legacy_uma_coin "
        "FROM player_skill_zone_new ORDER BY user_id"
    )]
    if {row[0]: row[1:] for row in stats_rows} != {
        row[0]: row[1:] for row in actual_stats
    }:
        raise RuntimeError("Stats/Aptitude values differ from source")
    if {row[0]: row[1:] for row in zone_rows} != {
        row[0]: row[1:] for row in actual_zone
    }:
        raise RuntimeError("Skill/Zone values differ from source")

    conn.execute("DROP TABLE players")
    conn.execute("ALTER TABLE players_new RENAME TO players")
    conn.execute("ALTER TABLE player_stats_aptitude_new RENAME TO player_stats_aptitude")
    conn.execute("ALTER TABLE player_skill_zone_new RENAME TO player_skill_zone")
    checked(conn)
    return {
        "players": old_count,
        "stats_aptitude": old_count,
        "skill_zone": old_count,
        "legacy_uma_coin_column_present": int("uma_coin" in columns),
    }


def run(path, dry_run=False):
    path = Path(path).resolve()
    if not path.is_file():
        raise FileNotFoundError(path)
    uri = path.as_uri() + ("?mode=ro" if dry_run else "?mode=rw")
    with closing(sqlite3.connect(uri, uri=True, timeout=10)) as source:
        source.row_factory = sqlite3.Row
        checked(source)
        backup_path = None
        if dry_run:
            work = sqlite3.connect(":memory:")
            work.row_factory = sqlite3.Row
            source.backup(work)
        else:
            suffix = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            backup_path = path.with_name(f"{path.name}.before-playerdata-{suffix}.sqlite3")
            with backup_path.open("xb"):
                pass
            with closing(sqlite3.connect(backup_path)) as backup:
                source.backup(backup)
                checked(backup)
                source_before = source_snapshot(backup)
                with closing(sqlite3.connect(":memory:")) as rehearsal:
                    rehearsal.row_factory = sqlite3.Row
                    backup.backup(rehearsal)
                    rehearsal.execute("BEGIN IMMEDIATE")
                    expected = migrate(rehearsal)
                    rehearsal.rollback()
            work = source
        try:
            work.execute("BEGIN IMMEDIATE")
            if not dry_run and source_snapshot(work) != source_before:
                raise RuntimeError("players changed after backup; stop all writers and retry")
            result = migrate(work)
            if not dry_run and result != expected:
                raise RuntimeError("Migration did not match its backup rehearsal")
            if dry_run:
                work.rollback()
            else:
                work.commit()
            result.update(
                dry_run=dry_run,
                database=str(path),
                backup=str(backup_path) if backup_path else None,
                version=VERSION,
            )
            return result
        except Exception:
            work.rollback()
            raise
        finally:
            if dry_run:
                work.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--db-path", default=os.getenv("PLAYER_DB_PATH", "/app/data/player.db"))
    args = parser.parse_args()
    print(json.dumps(run(args.db_path, args.dry_run), ensure_ascii=False))
