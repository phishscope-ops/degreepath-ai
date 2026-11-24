# v1.5.0 deploy blocker (found 2026-11-24 ~19:00 EET)

Symptom: Render deploy of 946bde1 builds OK, then app exits status 1 at boot:
`psycopg2/extras.py line 236 execute -> IndexError: tuple index out of range`.
Render then restarts the OLD v1.4.0 instance (site stays up, old UI, SQLite).

Root cause: `degreepath/db.py::_pg_sql` converts `?` -> `%s` but never escapes
literal `%`. seed.py RESOURCES added in v1.5.0 contain Microsoft Learn URLs with
`%20` (lines ~394, ~406, ~413). On a FRESH Postgres DB, seed runs those INSERTs
with empty params; psycopg2 parses `%2` as a format spec -> IndexError. This is
why the local smoke test must be rerun against a FRESH Postgres (drop/recreate
the test DB) - the bug only fires on first-time seeding.

Fix (one line, in _pg_sql BEFORE the `?`->`%s` replace):
    s = s.replace("%", "%%")
Verify: fresh-Postgres smoke test (schema+seed+register+jobs==30), then push as
v1.5.1, Render Manual Deploy (normal deploy is fine; cache already cleared),
watch boot logs for "Deploy live", then probe:
  GET /admin -> 200, POST /api/admin/login {} -> 401/403 (not 405),
  /api/jobs -> 30 titles, / contains "مسارك".
Then: admin dashboard screenshot (vault entry "DegreePath admin (PhishScope ops)"),
revoke GitHub PAT degreepath-v15-temp (id 23580224) in github.com settings,
delete /home/sandbox/.dp-gh-token + .dp-askpass.sh, cloud_browser report for
github.com/neon.tech/render.com on both leases, release leases
L-sixp4vpx5nbpduriq4xb7icokf3gc5gm (read) + L-xr433h66fs3lnikey5otkasmbf54465c (write),
final report to parent incl. vault copy_url:
https://app.instinct.com/session/vault/copy?r=request_JQHQ7GQIPATCDXFG4HR6BUJPH7VC4XQ2
NOTE: Render env vars DATABASE_URL (Neon DSN eu-central-1) + ADMIN_PASSWORD are
already set on srv-dc2nk0m8bjmc73884b50 - no need to set again.
Smoke-test user on Neon DB: smoke_v15@example.com (id=2). Real user id=1 exists
(active mobile user - do not wipe the Neon DB).
