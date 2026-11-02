# Character profile migration

The website uses the existing basic-profile API;
the API storage functions now use `character_profiles`. Discord and game
identity continue to use players and `profile_presets` as before. The preset
and account-role tables are not migrated or removed.

The target key is `(user_id, profile_type)`. Role rows win on overlap, including
empty values, preserving the existing API's behavior. A legacy-only row becomes
a trainee profile. For old role schemas without division/dorm, those fields
are taken from the legacy row where present, matching the old startup upgrade.
Differing shared fields are recorded in `character_profile_migration_conflicts`;
both original tables and a full backup are retained. The script aborts on an
unexpected schema, invalid role, failed integrity/foreign-key check, existing
target table, or if profile data changes between backup and write lock. It is
safe to repeat only by using a fresh copy: it refuses to overwrite an existing
target. Profile data is not printed to the console.

The bot and API both call `init_db`. On an unmigrated existing database the
new code refuses to start; on an empty database it creates the new table. Do
not deploy this application version against the old schema. The old code must
not write after migration: retained old tables are not synchronized.

## Rehearsal

Run on a separate, up-to-date SQLite backup and check the result, for example:

```powershell
python scripts/migrate_profiles.py --dry-run --db-path C:\path\to\copy.sqlite3
python scripts/migrate_profiles.py --db-path C:\path\to\copy.sqlite3
python -m unittest discover -s tests -v
```

Dry-run migrates only an in-memory SQLite backup; it does not change the source.
Apply makes a timestamped full SQLite Backup API file alongside the database,
checks it and rehearses on a copy before starting a transaction. It validates
all selected profile values, counts, integrity and foreign keys before commit.
Review conflict counts and inspect the conflict table and retained sources.
The backup contains private data; protect it and store an independent copy.

## Coordinated cutover, only after explicit authorization

1. Confirm Railway project, environment, service, actual `PLAYER_DB_PATH`,
   mounted volume, all active writer processes and deployment instances. Test
   against a fresh snapshot from that exact service, not a presumed copy.
2. Stage a **migration-only** release containing the script and the old
   application code. Verify that `scripts/migrate_profiles.py` exists in the
   service image and run `railway ssh -s SERVICE -e ENVIRONMENT -- python
   scripts/migrate_profiles.py --dry-run` against the intended database.
3. Arrange maintenance so every writer is stopped or blocked, including bot,
   API workers, other deployments and admin tools. Keep an SSH-capable service
   with the volume available; do not rely on traffic blocking alone to stop
   background writers. Verify the maintenance mechanism before proceeding.
4. Run `railway ssh -s SERVICE -e ENVIRONMENT -- python scripts/migrate_profiles.py`.
   Record the backup path, preserve an independent copy and inspect results.
   Keep writers stopped. On any error, investigate; do not start new code.
5. Deploy the new application version while still in maintenance. Confirm old
   instances and writers have stopped, verify startup and test basic profile
   reads, writes and role-specific behavior, Discord and website flows. Resume
   traffic only after verification. Do not drop either old table in this change.

For rollback, stop all writers, preserve post-migration data for analysis, and
restore the checked backup together with the old application version. Restoring
an older backup discards writes made after that backup; reconcile them first.
SQLite backup is a consistent database snapshot, but an on-volume backup does
not protect against loss of that volume.

## Retiring the legacy profile tables

After the new application is deployed and verified, use
`scripts/prune_legacy_profiles.py --dry-run` to review row counts, then
`scripts/prune_legacy_profiles.py --apply` to back up the database and drop
only the two legacy profile tables. The cleanup keeps `character_profiles`,
`profile_presets`, `account_roles`, `race_history`, and every other table.
Both flags are explicit; the script refuses to run without exactly one.

## Player data separation

`players` keeps account identity and profile-image fields. Numeric stats and
aptitudes move to `player_stats_aptitude`; fans, skill points, equipped skill
slots, and zone settings move to `player_skill_zone`. `playerdata` is a
read-only compatibility view used by older response-building code. The
SQLite tables are the source of truth; writes go directly to the owning table.
`skill_loadout_presets` and `player_skills` remain separate.

Rehearse and apply only to a fresh copy or the intended Test database after all
writers are stopped:

```powershell
python scripts/migrate_playerdata.py --dry-run --db-path C:\path\to\test-copy.sqlite3
python scripts/migrate_playerdata.py --db-path C:\path\to\test-copy.sqlite3
```

The migration creates a timestamped SQLite Backup API copy, rehearses on that
copy, checks every player's identity, stats, aptitudes, skill slots and zone
values, and only then replaces the old `players` table. It preserves the old
`uma_coin` value in `player_skill_zone.legacy_uma_coin` when present, while
mapping it to `fans` only when the old schema had no `fans` column. The new
application refuses to start against an unmigrated `players` schema. Deploy
the migration script with old code first; stop all writers, apply the schema
migration, then deploy the new code and verify the API, Discord commands,
website, skills, zone edits, and race reads before resuming service.
