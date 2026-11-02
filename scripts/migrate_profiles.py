"""Migrate basic character profiles. Stop all database writers before applying.

Use --dry-run for a read-only rehearsal in memory. Applying creates a SQLite
backup beside the database before a transactional, non-destructive migration.
"""
import argparse
from contextlib import closing
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sqlite3


FIELDS = ("self_intro", "name_th", "name_en", "division", "age", "birthday_day",
          "birthday_month", "height_cm", "dorm", "likes", "dislikes", "personality",
          "biography", "additional", "updated_at")
NUMBERS = {"age", "birthday_day", "birthday_month", "height_cm"}
VERSION = "character_profiles_v1"


def checked(conn):
    integrity = [row[0] for row in conn.execute("PRAGMA integrity_check")]
    foreign = list(conn.execute("PRAGMA foreign_key_check"))
    if integrity != ["ok"] or foreign:
        raise RuntimeError(f"Database checks failed: integrity={integrity}, foreign key violations={len(foreign)}")


def legacy_snapshot(conn):
    result = {}
    for name in ("character_basic_profiles", "character_role_basic_profiles"):
        columns = [tuple(r) for r in conn.execute(f"PRAGMA table_info({name})")]
        if not columns:
            raise RuntimeError(f"Missing table {name}")
        rows = sorted((tuple(r) for r in conn.execute(f"SELECT * FROM {name}")), key=repr)
        result[name] = (columns, rows)
    return result


def migrate(conn):
    conn.row_factory = sqlite3.Row
    names = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    required = {"character_basic_profiles", "character_role_basic_profiles"}
    if not required <= names:
        raise RuntimeError("Missing a legacy profile table; inspect the database before migration")
    if "character_profiles" in names:
        raise RuntimeError("character_profiles already exists; refusing to overwrite or rerun migration")
    role_columns = {r[1] for r in conn.execute("PRAGMA table_info(character_role_basic_profiles)")}
    basic_columns = {r[1] for r in conn.execute("PRAGMA table_info(character_basic_profiles)")}
    if not (set(FIELDS) - {"division", "dorm"}) <= role_columns or not (set(FIELDS) - {"age"}) <= basic_columns:
        raise RuntimeError("Unexpected legacy profile schema")
    fields_sql = ", ".join(f"{name} {'INTEGER' if name in NUMBERS else 'TEXT'}" for name in FIELDS)
    conn.execute(f"CREATE TABLE character_profiles (user_id TEXT NOT NULL, profile_type TEXT NOT NULL CHECK(profile_type IN ('trainee','trainer','npc')), {fields_sql}, PRIMARY KEY(user_id, profile_type))")
    conn.execute("""CREATE TABLE character_profile_migration_conflicts (
        user_id TEXT NOT NULL, profile_type TEXT NOT NULL, field TEXT NOT NULL,
        selected_source TEXT NOT NULL, role_value_json TEXT NOT NULL, legacy_value_json TEXT NOT NULL,
        PRIMARY KEY(user_id, profile_type, field))""")
    role_rows = [dict(r) for r in conn.execute("SELECT * FROM character_role_basic_profiles")]
    legacy_rows = [dict(r) for r in conn.execute("SELECT * FROM character_basic_profiles")]
    merged = {}
    for row in role_rows:
        key = (str(row["user_id"]), row["profile_type"])
        if key[1] not in ("trainee", "trainer", "npc") or key in merged:
            raise RuntimeError("Invalid or duplicate role profile")
        merged[key] = {field: row.get(field, "" if field in {"division", "dorm"} else None) for field in FIELDS}
    for row in legacy_rows:
        key = (str(row["user_id"]), "trainee")
        if key not in merged:
            merged[key] = {field: row.get(field) for field in FIELDS}
            continue
        for field in set(FIELDS) & basic_columns & role_columns:
            if field == "updated_at":
                continue
            selected, legacy = merged[key][field], row[field]
            if selected != legacy:
                conn.execute("INSERT INTO character_profile_migration_conflicts VALUES (?, ?, ?, ?, ?, ?)",
                             (*key, field, "character_role_basic_profiles", json.dumps(selected, ensure_ascii=False), json.dumps(legacy, ensure_ascii=False)))
        # Match the old startup upgrade for schemas which lacked these columns.
        for field in ("division", "dorm"):
            if field not in role_columns:
                merged[key][field] = row.get(field)
    columns = ("user_id", "profile_type", *FIELDS)
    query = f"INSERT INTO character_profiles ({', '.join(columns)}) VALUES ({', '.join('?' for _ in columns)})"
    for key, fields in merged.items():
        conn.execute(query, [*key, *(fields[f] for f in FIELDS)])
    actual = {(r["user_id"], r["profile_type"]): {f: r[f] for f in FIELDS} for r in conn.execute("SELECT * FROM character_profiles")}
    if actual != merged:
        raise RuntimeError("Profile count or field validation failed")
    checked(conn)
    return {"legacy_rows": len(legacy_rows), "role_rows": len(role_rows), "profiles": len(actual),
            "conflicting_fields": conn.execute("SELECT COUNT(*) FROM character_profile_migration_conflicts").fetchone()[0]}


def run(path, dry_run=False):
    path = Path(path).resolve()
    if not path.is_file():
        raise FileNotFoundError(path)
    uri = path.as_uri() + ("?mode=ro" if dry_run else "?mode=rw")
    with closing(sqlite3.connect(uri, uri=True, timeout=10)) as source:
        checked(source)
        backup_path = None
        if dry_run:
            work = sqlite3.connect(":memory:")
        else:
            suffix = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            backup_path = path.with_name(f"{path.name}.before-profiles-{suffix}.sqlite3")
            with backup_path.open("xb"):
                pass
            with closing(sqlite3.connect(backup_path)) as backup:
                source.backup(backup)
                checked(backup)
                expected_legacy = legacy_snapshot(backup)
                # Prove the migration against the exact backup before applying it.
                with closing(sqlite3.connect(":memory:")) as rehearsal:
                    backup.backup(rehearsal)
                    rehearsal.execute("BEGIN IMMEDIATE")
                    expected = migrate(rehearsal)
                    rehearsal.rollback()
            work = source
        try:
            if dry_run:
                source.backup(work)
            work.execute("BEGIN IMMEDIATE")
            if not dry_run and legacy_snapshot(work) != expected_legacy:
                raise RuntimeError("Legacy profiles changed after backup; stop all writers and retry")
            result = migrate(work)
            if not dry_run and result != expected:
                raise RuntimeError("Migration did not match its backup rehearsal")
            work.commit()
            result.update(dry_run=dry_run, database=str(path), backup=str(backup_path) if backup_path else None, version=VERSION)
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
