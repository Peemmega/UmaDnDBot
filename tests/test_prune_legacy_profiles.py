import importlib.util
from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("prune_legacy_profiles", Path(__file__).resolve().parents[1] / "scripts" / "prune_legacy_profiles.py")
prune = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prune)


class PruneLegacyProfilesTests(unittest.TestCase):
    def test_dry_run_and_apply_preserve_canonical_and_game_data(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "db.sqlite3"
            with closing(sqlite3.connect(path)) as conn, conn:
                conn.executescript("""
                    CREATE TABLE character_basic_profiles(user_id TEXT);
                    CREATE TABLE character_role_basic_profiles(user_id TEXT, profile_type TEXT);
                    CREATE TABLE character_profiles(user_id TEXT, profile_type TEXT, PRIMARY KEY(user_id,profile_type));
                    CREATE TABLE profile_presets(user_id TEXT, profile_type TEXT);
                    CREATE TABLE account_roles(user_id TEXT, role TEXT);
                    CREATE TABLE race_history(race_id TEXT PRIMARY KEY);
                    INSERT INTO character_basic_profiles VALUES ('u1');
                    INSERT INTO character_role_basic_profiles VALUES ('u1','trainee'),('u1','npc');
                    INSERT INTO character_profiles VALUES ('u1','trainee'),('u1','npc');
                    INSERT INTO profile_presets VALUES ('u1','trainer');
                    INSERT INTO account_roles VALUES ('u1','trainer');
                    INSERT INTO race_history VALUES ('r1');
                """)
            dry = prune.run(path)
            self.assertTrue(dry["dry_run"])
            with closing(sqlite3.connect(path)) as conn:
                self.assertEqual(conn.execute("SELECT COUNT(*) FROM character_role_basic_profiles").fetchone()[0], 2)
            result = prune.run(path, apply=True)
            self.assertTrue(Path(result["backup"]).exists())
            self.assertEqual(result["removed"], {"character_basic_profiles": 1, "character_role_basic_profiles": 2})
            with closing(sqlite3.connect(path)) as conn:
                for table in ("character_profiles", "profile_presets", "account_roles", "race_history"):
                    self.assertEqual(conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0], 2 if table == "character_profiles" else 1)
                self.assertEqual(conn.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            with closing(sqlite3.connect(result["backup"])) as conn:
                self.assertEqual(conn.execute("SELECT COUNT(*) FROM character_role_basic_profiles").fetchone()[0], 2)


if __name__ == "__main__":
    unittest.main()
