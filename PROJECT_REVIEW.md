# Project review

This repository copy was prepared for GitHub from the supplied ZIP.

## Corrected before publishing

- Removed the committed `.env`, local virtual environment, Python caches, generated reports, and one-off patch scripts.
- Added `.gitignore` and `.env.example`.
- Added an initial database migration.
- Fixed the test application configuration so tests use an in-memory SQLite database before the app is created.
- Connected route-level authentication rate limits to the application limiter.
- Added refresh-token signature, type, revocation, and expiry checks.
- Applied the same registration validation to the web form and API.
- Added category update validation and bounded task pagination.
- Replaced deprecated Pydantic v1 validator and serialization calls.
- Escaped user-generated values rendered through JavaScript to reduce stored-XSS risk.
- Removed misleading fake profile data and disabled unimplemented account/security actions.
- Changed frontend logout to POST and revoke the stored refresh token.
- Removed the duplicate refresh-token model file.
- Removed delete-orphan behavior from assigned tasks to avoid deleting another user's task when an assignee is deleted.

## Still worth improving

- Replace browser `localStorage` tokens with secure HttpOnly cookies and add CSRF protection.
- Hash refresh tokens before storing them in the database.
- Add database transaction handling for integrity errors and structured application logging.
- Complete task editing in the web interface.
- Add CI, formatting, linting, coverage, and deployment configuration.
- Add a chosen open-source license only when the owner intends to grant those rights.
