import sqlite3
import unittest
from contextlib import contextmanager
from unittest.mock import patch

from utils.race import race_history


class RaceHistoryTrainerTests(unittest.TestCase):
    def test_new_snapshot_uses_trainer_username(self):
        with patch.object(race_history, "get_trainee_trainer", return_value={"user_id": "t1", "username": "Trainer One"}):
            identity = race_history._participant_identity("u1", {"display_name": "Uma"})
        self.assertEqual(identity["trainer_id"], "t1")
        self.assertEqual(identity["trainer_name"], "Trainer One")

    def test_history_resolves_missing_name_from_recorded_trainer_id(self):
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        self.addCleanup(conn.close)
        conn.executescript("""
            CREATE TABLE race_history (race_id TEXT, source TEXT, finished_at TEXT, record_type TEXT, total_turns INTEGER);
            CREATE TABLE race_participants (race_id TEXT, participant_id TEXT, uma_id TEXT, uma_name TEXT,
                trainer_id TEXT, trainer_name TEXT, participant_type TEXT, running_style TEXT,
                final_rank INTEGER, final_score INTEGER, snapshot_json TEXT);
            CREATE TABLE profile_presets (user_id TEXT, profile_type TEXT, name TEXT);
            CREATE TABLE race_participant_turns (race_id TEXT, turn_number INTEGER, position INTEGER, participant_id TEXT);
            CREATE TABLE race_participant_actions (race_id TEXT, turn_number INTEGER, action_id INTEGER);
            INSERT INTO race_history VALUES ('r1', 'race', '2026-01-01', 'practice', 0);
            INSERT INTO profile_presets VALUES ('t1', 'trainer', 'Current Trainer Name');
            INSERT INTO race_participants VALUES ('r1', 'u1', 'u1', 'Uma', 't1', NULL, 'uma', 'Pace', 1, 100, '{}');
            INSERT INTO race_participants VALUES ('r1', 'u2', 'u2', 'Uma 2', 't1', 'Snapshot Name', 'uma', 'Front', 2, 90, '{}');
            INSERT INTO race_participants VALUES ('r1', 'u3', 'u3', 'Uma 3', NULL, NULL, 'uma', 'End', 3, 80, '{}');
        """)

        @contextmanager
        def connection():
            yield conn

        with patch.object(race_history, "database_connection", connection):
            detail = race_history.get_race_by_id("r1")
            history = race_history.get_participant_history(column="uma_id", value="u1")
            races = race_history.list_race_history()
        self.assertEqual([p["trainer_name"] for p in detail["participants"]], ["Current Trainer Name", "Snapshot Name", None])
        self.assertEqual(history[0]["trainer_name"], "Current Trainer Name")
        self.assertEqual(races[0]["winner_trainer_name"], "Current Trainer Name")


if __name__ == "__main__":
    unittest.main()
