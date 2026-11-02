"""Remove the retired duplicate profile tables after a verified migration.

Dry-run is read-only. Applying requires --apply and creates a full SQLite
backup before dropping only character_basic_profiles and
character_role_basic_profiles.
"""
import argparse
from contextlib import closing
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sqlite3


LEGACY = ("character_basic_profiles", "character_role_basic_profiles")
KEEP = ("character_profiles", "profile_presets", "account_roles", "race_history")


def checks(conn):
    integrity = [row[0] for row in conn.execute("PRAGMA integrity_check")]
    foreign = list(conn.execute("PRAGMA foreign_key_check"))
    if integrity != ["ok"] or foreign:
        raise RuntimeError(f"Database checks failed: integrity={integrity}; foreign key violations={len(foreign)}")


def table_names(conn):
    return {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}


def snapshot_counts(conn):
    names = table_names(conn)
    if "character_profiles" not in names:
        raise RuntimeError("character_profiles is missing")
    missing = [name for name in KEEP if name not in names]
    if missing:
        raise RuntimeError(f"Required tables are missing: {missing}")
    return {
        name: conn.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0]
        for name in (*LEGACY, *KEEP)
        if name in names
    }


def drop_legacy(conn):
    before = snapshot_counts(conn)
    for name in LEGACY:
        if name in table_names(conn):
            conn.execute(f'DROP TABLE "{name}"')
    after_names = table_names(conn)
    if any(name in after_names for name in LEGACY):
        raise RuntimeError("A legacy table remains")
    for name in KEEP:
        if conn.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0] != before[name]:
            raise RuntimeError(f"Preserved table changed: {name}")
    checks(conn)
    return {"removed": {name: before.get(name, 0) for name in LEGACY},
            "preserved": {name: before[name] for name in KEEP}}


def run(db_path, apply=False):
    path = Path(db_path).resolve()
    if not path.is_file():
        raise FileNotFoundError(path)
    mode = "rw" if apply else "ro"
    with closing(sqlite3.connect(path.as_uri() + f"?mode={mode}", uri=True, timeout=10)) as source:
        source.row_factory = sqlite3.Row
        checks(source)
        backup_path = None
        if apply:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            backup_path = path.with_name(f"{path.name}.before-profile-cleanup-{timestamp}.sqlite3")
            with backup_path.open("xb"):
                pass
            with closing(sqlite3.connect(backup_path)) as backup:
                source.backup(backup)
                checks(backup)
                expected = snapshot_counts(backup)
                with closing(sqlite3.connect(":memory:")) as rehearsal:
                    backup.backup(rehearsal)
                    rehearsal.execute("BEGIN IMMEDIATE")
                    drop_legacy(rehearsal)
                    rehearsal.rollback()
            source.execute("BEGIN IMMEDIATE")
            if snapshot_counts(source) != expected:
                raise RuntimeError("Database changed after backup; retry with writers paused")
            result = drop_legacy(source)
            source.commit()
        else:
            with closing(sqlite3.connect(":memory:")) as rehearsal:
                source.backup(rehearsal)
                rehearsal.execute("BEGIN IMMEDIATE")
                result = drop_legacy(rehearsal)
                rehearsal.rollback()
        result.update(dry_run=not apply, database=str(path), backup=str(backup_path) if backup_path else None)
        return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db-path", default=os.getenv("PLAYER_DB_PATH", "/app/data/player.db"))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true", help="create a backup, then drop the two legacy profile tables")
    args = parser.parse_args()
    if args.apply == args.dry_run:
        parser.error("choose exactly one of --dry-run or --apply")
    print(json.dumps(run(args.db_path, args.apply), ensure_ascii=False))
