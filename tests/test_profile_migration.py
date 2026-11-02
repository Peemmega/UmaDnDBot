import importlib.util
from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from utils.storage import database

spec = importlib.util.spec_from_file_location("migrate_profiles", Path(__file__).resolve().parents[1] / "scripts" / "migrate_profiles.py")
migration = importlib.util.module_from_spec(spec)
spec.loader.exec_module(migration)


class MigrationTests(unittest.TestCase):
    def test_migrate_backup_and_runtime(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "db.sqlite3"
            with patch.object(database, "DB_PATH", str(path)):
                database.init_db()
            with closing(sqlite3.connect(path)) as conn, conn:
                conn.execute("DROP TABLE character_profiles")
                conn.execute("CREATE TABLE character_basic_profiles (user_id TEXT PRIMARY KEY, self_intro TEXT, name_th TEXT, name_en TEXT, division TEXT, birthday_day INTEGER, birthday_month INTEGER, height_cm INTEGER, dorm TEXT, likes TEXT, dislikes TEXT, personality TEXT, biography TEXT, additional TEXT, updated_at TEXT)")
                conn.execute("CREATE TABLE character_role_basic_profiles (user_id TEXT, profile_type TEXT, self_intro TEXT, name_th TEXT, name_en TEXT, age INTEGER, birthday_day INTEGER, birthday_month INTEGER, height_cm INTEGER, likes TEXT, dislikes TEXT, personality TEXT, biography TEXT, additional TEXT, updated_at TEXT, PRIMARY KEY(user_id, profile_type))")
                conn.execute("INSERT INTO character_basic_profiles(user_id,name_th,division,dorm) VALUES ('1','old','Junior','Miho')")
                conn.execute("INSERT INTO character_role_basic_profiles(user_id,profile_type,name_th) VALUES ('1','trainee','new'),('1','npc','npc')")
                conn.execute("INSERT INTO profile_presets(user_id,profile_type,name,image_url) VALUES ('1','npc','Preset','image')")
            with patch.object(database, "DB_PATH", str(path)):
                with self.assertRaisesRegex(RuntimeError, "Profile migration required"):
                    database.init_db()
            dry = migration.run(path, True)
            self.assertEqual((dry["profiles"], dry["conflicting_fields"]), (2, 1))
            with closing(sqlite3.connect(path)) as conn:
                self.assertIsNone(conn.execute("SELECT name FROM sqlite_master WHERE name='character_profiles'").fetchone())
            result = migration.run(path)
            self.assertTrue(Path(result["backup"]).exists())
            with closing(sqlite3.connect(result["backup"])) as backup:
                self.assertIsNone(backup.execute("SELECT name FROM sqlite_master WHERE name='character_profiles'").fetchone())
            with closing(sqlite3.connect(path)) as conn:
                self.assertEqual(conn.execute("SELECT name_th,division,dorm FROM character_profiles WHERE profile_type='trainee'").fetchone(), ('new','Junior','Miho'))
                self.assertEqual(conn.execute("SELECT count(*) FROM character_basic_profiles").fetchone()[0], 1)
                self.assertEqual(conn.execute("SELECT count(*) FROM character_role_basic_profiles").fetchone()[0], 2)
                self.assertEqual(conn.execute("SELECT name,image_url FROM profile_presets").fetchone(), ('Preset','image'))
            with patch.object(database, "DB_PATH", str(path)):
                database.init_db()
                self.assertEqual(database.get_character_basic_profile('1','npc')['name_th'], 'npc')
                profile = database.get_character_basic_profile('1','trainee')
                profile['name_th'] = 'edited'
                database.save_character_basic_profile('1','trainee',profile)
                self.assertEqual(database.get_character_basic_profile('1','trainee')['name_th'], 'edited')
                self.assertEqual(database.get_character_basic_profile('1','npc')['name_th'], 'npc')
            with self.assertRaises(RuntimeError):
                migration.run(path, True)


if __name__ == '__main__':
    unittest.main()
