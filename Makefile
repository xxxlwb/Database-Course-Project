.PHONY: help db-init db-drop db-reset backend frontend test perf-load demo-load

help:
	@echo "Targets: db-init, db-drop, db-reset, backend, frontend, test, perf-load, demo-load"

db-init:
	mysql -u $${DB_USER} -p$${DB_PASSWORD} -h $${DB_HOST} -P $${DB_PORT} $${DB_NAME} < sql/01_schema.sql
	mysql -u $${DB_USER} -p$${DB_PASSWORD} -h $${DB_HOST} -P $${DB_PORT} $${DB_NAME} < sql/02_indexes.sql
	mysql -u $${DB_USER} -p$${DB_PASSWORD} -h $${DB_HOST} -P $${DB_PORT} $${DB_NAME} < sql/03_views.sql
	mysql -u $${DB_USER} -p$${DB_PASSWORD} -h $${DB_HOST} -P $${DB_PORT} $${DB_NAME} < sql/04_triggers.sql
	mysql -u $${DB_USER} -p$${DB_PASSWORD} -h $${DB_HOST} -P $${DB_PORT} $${DB_NAME} < sql/05_procedures.sql

db-drop:
	mysql -u $${DB_USER} -p$${DB_PASSWORD} -h $${DB_HOST} -P $${DB_PORT} $${DB_NAME} < sql/00_drop_all.sql

db-reset: db-drop db-init demo-load

demo-load:
	mysql -u $${DB_USER} -p$${DB_PASSWORD} -h $${DB_HOST} -P $${DB_PORT} $${DB_NAME} < sql/06_seed.sql

perf-load:
	mysql -u $${DB_USER} -p$${DB_PASSWORD} -h $${DB_HOST} -P $${DB_PORT} $${DB_NAME} < sql/07_seed_perf.sql

backend:
	cd backend && uv run uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && pnpm dev

test:
	cd backend && uv run pytest -v
