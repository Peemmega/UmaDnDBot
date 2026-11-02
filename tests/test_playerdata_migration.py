import importlib.util
from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from utils.storage import database


spec = importlib.util.spec_from_file_location(
    "migrate_playerdata",
    Path(__file__).resolve().parents[1] / "scripts" / "migrate_playerdata.py",
)
migration = importlib.util.module_from_spec(spec)
spec.loader.exec_module(migration)


class PlayerDataMigrationTests(unittest.TestCase):
    def make_database(self, path, *, legacy_coin=False):
        with closing(sqlite3.connect(path)) as conn, conn:
            common = """
                user_id INTEGER PRIMARY KEY, username TEXT NOT NULL,
                speed INTEGER NOT NULL, stamina INTEGER NOT NULL,
                power INTEGER NOT NULL, gut INTEGER NOT NULL, wit INTEGER NOT NULL,
                turf INTEGER NOT NULL, dirt INTEGER NOT NULL,
                sprint INTEGER NOT NULL, mile INTEGER NOT NULL, medium INTEGER NOT NULL,
                long INTEGER NOT NULL, front INTEGER NOT NULL, pace INTEGER NOT NULL,
                late INTEGER NOT NULL, end_style INTEGER NOT NULL,
                stats_point INTEGER NOT NULL,
            """
            if legacy_coin:
                sql = common + "uma_coin INTEGER NOT NULL DEFAULT 0, skill_point INTEGER NOT NULL DEFAULT 0, "
                sql += "skill_slot_1 TEXT, skill_slot_2 TEXT, zone_name TEXT, zone_image_url TEXT, zone_points INTEGER, zone_build TEXT"
            else:
                sql = common + "fans INTEGER NOT NULL DEFAULT 1, skill_point INTEGER NOT NULL DEFAULT 12, "
                sql += """
                    skill_slot_1 TEXT, skill_slot_2 TEXT, skill_slot_3 TEXT, skill_slot_4 TEXT,
                    profile_image_url TEXT, profile_image_updated_at INTEGER,
                    zone_name TEXT, zone_image_url TEXT, zone_points INTEGER, zone_build TEXT,
                    default_skill_loadout_seeded INTEGER NOT NULL DEFAULT 1
                """
            conn.execute(f"CREATE TABLE players ({sql})")
            if legacy_coin:
                columns = (
                    "user_id, username, speed, stamina, power, gut, wit, turf, dirt, "
                    "sprint, mile, medium, long, front, pace, late, end_style, stats_point, "
                    "uma_coin, skill_point, zone_name, zone_image_url, zone_points, zone_build"
                )
                conn.execute(
                    f"INSERT INTO players ({columns}) VALUES ({','.join('?' for _ in columns.split(','))})",
                    (7, "Legacy", 4, 3, 2, 1, 5, 8, 7, 6, 5, 4, 3, 2, 1, 2, 3, 9, 250, 6,
                     "Legacy Zone", "legacy.png", 11, '{\"flat\":2}'),
                )
            else:
                columns = (
                    "user_id, username, speed, stamina, power, gut, wit, turf, dirt, "
                    "sprint, mile, medium, long, front, pace, late, end_style, stats_point, "
                    "fans, skill_point, skill_slot_1, skill_slot_2, skill_slot_3, skill_slot_4, "
                    "profile_image_url, profile_image_updated_at, zone_name, zone_image_url, "
                    "zone_points, zone_build, default_skill_loadout_seeded"
                )
                conn.execute(
                    f"INSERT INTO players ({columns}) VALUES ({','.join('?' for _ in columns.split(','))})",
                    (42, "Trainee", 8, 7, 6, 5, 4, 3, 2, 1, 2, 3, 4, 5, 6, 7, 8, 10,
                     900, 14, "rec_010", "vel_023", None, "rec_011", "/img.webp", 123,
                     "Speed Zone", "/zone.webp", 9, '{"flat":1}', 1),
                )

    def test_dry_run_and_apply_moves_all_fields_and_runtime_reads_them(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "player.db"
            self.make_database(path)
            with patch.object(database, "DB_PATH", str(path)):
                with self.assertRaisesRegex(RuntimeError, "Player data migration required"):
                    database.init_db()

            dry = migration.run(path, dry_run=True)
            self.assertEqual((dry["players"], dry["stats_aptitude"], dry["skill_zone"]), (1, 1, 1))
            with closing(sqlite3.connect(path)) as conn:
                self.assertEqual(conn.execute("SELECT COUNT(*) FROM players").fetchone()[0], 1)
                self.assertIsNone(conn.execute("SELECT name FROM sqlite_master WHERE name='player_stats_aptitude'").fetchone())

            result = migration.run(path)
            self.assertTrue(Path(result["backup"]).is_file())
            with closing(sqlite3.connect(path)) as conn:
                self.assertEqual(
                    [row[1] for row in conn.execute("PRAGMA table_info(players)")],
                    ["user_id", "username", "profile_image_url", "profile_image_updated_at"],
                )
                self.assertEqual(conn.execute("SELECT speed, wit, turf, stats_point FROM player_stats_aptitude").fetchone(), (8, 4, 3, 10))
                self.assertEqual(conn.execute("SELECT fans, skill_slot_1, skill_slot_4, zone_name, zone_points FROM player_skill_zone").fetchone(), (900, "rec_010", "rec_011", "Speed Zone", 9))
                self.assertEqual(conn.execute("PRAGMA integrity_check").fetchone()[0], "ok")
                self.assertEqual(conn.execute("PRAGMA foreign_key_check").fetchall(), [])

            with patch.object(database, "DB_PATH", str(path)):
                database.init_db()
                player = database.get_player(42)
                self.assertEqual(player["speed"], 8)
                self.assertEqual(player["StatsAptitude"]["turf"], 3)
                self.assertEqual(player["SkillZone"]["skills"], ["rec_010", "vel_023", None, "rec_011"])
                database.update_player_stats(42, speed=7, fans=901, skill_point=15)
                player = database.get_player(42)
                self.assertEqual((player["speed"], player["fans"], player["skill_point"]), (7, 901, 15))
                self.assertEqual((player["StatsAptitude"]["speed"], player["SkillZone"]["fans"]), (7, 901))
                database.set_admin_player_value(42, "fans", 902)
                self.assertEqual(database.get_player(42)["SkillZone"]["fans"], 902)
                database.set_player_zone_name(42, "Updated Zone")
                self.assertEqual(database.get_player(42)["zone"]["name"], "Updated Zone")
                database.set_player_zone_build(42, {"flat": 2})
                self.assertEqual(database.get_player(42)["SkillZone"]["zone"]["build"]["flat"], 2)

    def test_legacy_uma_coin_is_mapped_and_retained(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "legacy.db"
            self.make_database(path, legacy_coin=True)
            result = migration.run(path)
            self.assertEqual(result["legacy_uma_coin_column_present"], 1)
            with closing(sqlite3.connect(path)) as conn:
                self.assertEqual(conn.execute("SELECT fans, legacy_uma_coin, skill_point FROM player_skill_zone").fetchone(), (250, 250, 6))
                self.assertEqual(conn.execute("SELECT skill_slot_1, skill_slot_4, default_skill_loadout_seeded FROM player_skill_zone").fetchone(), ("rec_010", "vel_024", 1))
            with patch.object(database, "DB_PATH", str(path)):
                database.init_db()
                player = database.get_player(7)
                self.assertEqual((player["fans"], player["SkillZone"]["fans"]), (250, 250))


if __name__ == "__main__":
    unittest.main()
