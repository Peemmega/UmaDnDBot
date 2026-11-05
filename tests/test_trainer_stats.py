import asyncio
import hashlib
import hmac
import json
import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException

import api_server
from utils.storage import database


class TrainerStatsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db = patch.object(database, "DB_PATH", str(Path(self.temp.name) / "test.db"))
        self.db.start()
        self.addCleanup(self.db.stop)
        self.limit = patch.object(database, "MAX_CORE_STAT", 8)
        self.limit.start()
        self.addCleanup(self.limit.stop)
        database.init_db()
        database.create_player(101, "Trainer")
        database.create_player(102, "Trainee")
        with database.database_connection() as conn:
            conn.executemany("INSERT INTO account_roles (user_id, role) VALUES (?, ?)", [("101", "trainer"), ("102", "trainee")])
            conn.execute("UPDATE player_stats_aptitude SET stats_point = 2 WHERE user_id = 101")
        self.stats = {field: 8 for field in database.CORE_STAT_FIELDS}

    def test_trainer_can_set_stats_without_spending_or_refunding_points(self):
        updated = database.update_trainer_stats("101", self.stats)
        self.assertEqual([updated[key] for key in database.CORE_STAT_FIELDS], [8] * 5)
        self.assertEqual(updated["stats_point"], 2)
        updated = database.update_trainer_stats("101", {field: 1 for field in database.CORE_STAT_FIELDS})
        self.assertEqual(updated["stats_point"], 2)
        self.assertEqual(database.get_player(101)["speed"], 1)

    def test_other_roles_and_invalid_stats_are_rejected(self):
        with self.assertRaises(PermissionError):
            database.update_trainer_stats("102", self.stats)
        for invalid in ({**self.stats, "speed": 9}, {**self.stats, "speed": True}, {"speed": 1}):
            with self.assertRaises(ValueError):
                database.update_trainer_stats("101", invalid)
        self.assertEqual(database.get_player(101)["stats_point"], 2)

    def test_regular_stat_pool_still_rejects_unfunded_increase(self):
        with self.assertRaisesRegex(ValueError, "Invalid total stat pool"):
            database.update_player_stat_pool("102", stats=self.stats, stats_point=0)
        self.assertEqual(database.get_player(102)["speed"], 1)

    def test_unchanged_existing_stat_above_limit_is_preserved(self):
        with database.database_connection() as conn:
            conn.execute("UPDATE player_stats_aptitude SET speed = 10 WHERE user_id = 101")
        self.assertEqual(database.update_trainer_stats("101", {**self.stats, "speed": 10})["speed"], 10)
        with self.assertRaises(ValueError):
            database.update_trainer_stats("101", {**self.stats, "speed": 11})

    def test_signed_bot_endpoint_checks_signature_and_role(self):
        secret = "test-secret"
        with patch.dict(os.environ, {"APTITUDE_SYNC_SECRET": secret}):
            def send(user_id, signature_valid=True):
                body = json.dumps({"user_id": user_id, "stats": self.stats}, separators=(",", ":")).encode()
                timestamp = str(int(time.time()))
                signature = hmac.new(secret.encode(), timestamp.encode() + b"." + body, hashlib.sha256).hexdigest()
                if not signature_valid:
                    signature = "invalid"
                class Request:
                    headers = {"x-aptitude-timestamp": timestamp, "x-aptitude-signature": signature}
                    async def body(self):
                        return body
                return asyncio.run(api_server.api_update_trainer_stats(Request()))
            with self.assertRaises(HTTPException) as invalid:
                send("101", False)
            self.assertEqual(invalid.exception.status_code, 403)
            with self.assertRaises(HTTPException) as wrong_role:
                send("102")
            self.assertEqual(wrong_role.exception.status_code, 403)
            response = send("101")
            self.assertEqual(response["player"]["stats_point"], 2)
            self.assertEqual(response["player"]["speed"], 8)

            aptitudes = {field: 1 for field in database.APTITUDE_FIELDS}
            body = json.dumps({"user_id": "101", "aptitudes": aptitudes}, separators=(",", ":")).encode()
            timestamp = str(int(time.time()))
            signature = hmac.new(secret.encode(), timestamp.encode() + b"." + body, hashlib.sha256).hexdigest()
            class AptitudeRequest:
                headers = {"x-aptitude-timestamp": timestamp, "x-aptitude-signature": signature}
                async def body(self):
                    return body
            response = asyncio.run(api_server.api_update_trainer_aptitudes(AptitudeRequest()))
            self.assertEqual(response["player"]["turf"], 1)
            self.assertEqual(response["player"]["speed"], 8)


if __name__ == "__main__":
    unittest.main()
