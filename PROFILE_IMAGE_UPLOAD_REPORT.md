# Profile Image Upload Report

## Backend endpoint added

- `POST /player/{user_id}/profile-image`
- Request type: `multipart/form-data`
- Field: `file`
- Accepts: `jpg`, `jpeg`, `png`, `webp`
- Max size: `2 MB`
- Processing:
  - validates `content_type`
  - rejects empty or oversized files
  - sanitizes `user_id` to numeric-only
  - crops/resizes to `256x256`
  - converts to `webp`
  - overwrites the existing file for that user

## Backend storage path

- Primary upload root:
  - `UPLOAD_DIR` if provided
  - otherwise `static/uploads`
- Profile image file:
  - `{UPLOAD_DIR}/profiles/{user_id}.webp`
  - fallback: `static/uploads/profiles/{user_id}.webp`
- Static serving:
  - FastAPI serves upload root at `/uploads`
  - profile image URL shape: `/uploads/profiles/{user_id}.webp?v={updated_at}`

## Player data updates

- Added database columns:
  - `profile_image_url`
  - `profile_image_updated_at`
- `get_player()` now returns:
  - `profile_image_url`
  - `profile_image_updated_at`
- Returned URLs are resolved against `PUBLIC_BASE_URL` when needed.

## Required Railway volume and env

- To persist uploads across redeploys, mount a Railway Volume to the upload root.
- Recommended env:
  - `UPLOAD_DIR=/data/uploads`
  - `PUBLIC_BASE_URL=https://umadndbot-production.up.railway.app`
- Local dev example:
  - `PUBLIC_BASE_URL=http://127.0.0.1:8000`

Without a mounted persistent volume, uploaded files will be lost on redeploy or container replacement.

## Frontend UI added

- Web profile page now includes:
  - current profile image
  - `Change Image / เปลี่ยนรูป` button
  - file picker
  - local preview before upload
  - upload button
  - loading state
  - success/error message
- Frontend upload API:
  - `uploadProfileImage(userId, file)`
  - uses `FormData`
  - does not send JSON for file upload

## Web avatar usage

Avatar resolution order on web:

1. `player.profile_image_url`
2. Discord avatar
3. default avatar icon

Applied to:

- profile page
- race UI player avatars
- race score/ranking winner displays
- TCG room avatar display
- session-level avatar state used by race and TCG room creation payloads

## Discord usage locations

Avatar resolution order for bot-visible player displays:

1. shared `profile_image_url`
2. Discord avatar
3. existing fallback behavior

Updated usage points:

- `cogs/profile.py`
  - profile card image source
- `views/profile_stat_view.py`
  - stat embed thumbnail
- `utils/game_manager.py`
  - run embed thumbnail
- `cogs/game.py`
  - race dice preview image source
- `views/join_view.py`
  - join embed thumbnail and race preview image source

## TCG usage

- TCG room payloads now prefer the uploaded profile image when creating/joining a room if the backend player profile has one.
- Frontend TCG room UI renders resolved avatar URLs with fallback handling.

## Fallback behavior

- Stored `profile_image_url` present:
  - use it everywhere possible
- Otherwise:
  - use Discord avatar if available
- Otherwise:
  - use the existing UI fallback or default avatar icon

## Verification run

- Backend:
  - `python -m compileall utils api_server.py` ✅
  - Live upload smoke test via local `uvicorn` + `curl` ✅
  - PNG upload under 2 MB saved to `profiles/{user_id}.webp` ✅
  - Unsupported file rejected with `Unsupported image type` ✅
  - Oversized file rejected with `File too large` ✅
  - Existing image path overwritten in place ✅
  - `/uploads/profiles/{user_id}.webp` served as `image/webp` ✅
- Frontend:
  - `npm run build` in `uma-dashboard-ui` ✅

## Not fully exercised end-to-end in this run

- Discord runtime embed rendering against a live public URL

These still need a live app process plus a real upload request to confirm operational behavior outside static/build validation.
