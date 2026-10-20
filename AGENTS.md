# PrintingHouse

Web app for calculating and managing print orders: FastAPI backend (`backend/`), React frontend (`frontend/`), PostgreSQL.

## Commands

- Full stack: `docker-compose up --build` (needs `.env` in repo root, see README); applies Alembic migrations before backend start.
- Backend tests, from repo root: `python -m pytest backend/test`
- Migrations: `alembic -c backend/storage/alembic.ini upgrade head`
- Backend local run: cwd `backend/`, repo root on `PYTHONPATH`, then `python main.py` (needs DB env vars from README).
- Frontend, in `frontend/`: `npm start`, `npm test`, `npm run build`

## Structure

- Backend code imports by absolute package path `backend.*`; repo root must be on `PYTHONPATH`.
- `backend/`: `server/` (FastAPI routers, handlers), `storage/` (SQLAlchemy tables, repositories, Alembic), `models/` (domain models), `cost_reporter/` (cost calculation), `instruction_maker/` (production instructions), `test/` (pytest).

## Docs

- [Agent setup](.agents/docs/onboarding.md): read when wiring an agent, adding a skill or doc, or changing agent config.
- [Agent setup](.agents/docs/Index.md): read always.

## Plans

Save plans to `.agents/plans/` (gitignored).
