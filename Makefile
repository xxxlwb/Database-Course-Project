.PHONY: help db-init db-drop db-reset db-create db-ping backend frontend test perf-load demo-load \
        ensure-uv ensure-node ensure-mysql-client install-backend install-frontend doctor

# Make sure newly-installed user-local tools (uv, npm globals) are findable
# in every recipe's child shell, not just the login shell.
export PATH := $(HOME)/.local/bin:$(PATH)

# Auto-load .env (KEY=VALUE pairs, # comments OK) so DB_USER/DB_PASSWORD/etc.
# are available as Make vars and exported to recipe shells.
ifneq (,$(wildcard .env))
  include .env
  export
endif

# Defaults if .env didn't define them
DB_HOST     ?= 127.0.0.1
DB_PORT     ?= 3306
DB_USER     ?= root
DB_PASSWORD ?=
DB_NAME     ?= nkg

# Use MYSQL_PWD env var instead of -p flag: works with empty password
# (no prompt) and keeps the password out of `ps` listings.
MYSQL_CONN = MYSQL_PWD="$(DB_PASSWORD)" mysql -u $(DB_USER) -h $(DB_HOST) -P $(DB_PORT) $(DB_NAME)
MYSQL_ADMIN = MYSQL_PWD="$(DB_PASSWORD)" mysql -u $(DB_USER) -h $(DB_HOST) -P $(DB_PORT)

# ============================================================
# Cross-platform helpers
#   - Linux/Ubuntu: auto-install missing deps via apt + official scripts
#   - macOS / others: print install hint, do NOT auto-run sudo
# ============================================================

# Detect Ubuntu / Debian
IS_UBUNTU := $(shell [ -f /etc/os-release ] && . /etc/os-release && \
              echo "$$ID $$ID_LIKE" | grep -qiE 'ubuntu|debian' && echo yes)

help:
	@echo "Targets:"
	@echo "  backend         start FastAPI dev server (auto-installs uv + deps if missing)"
	@echo "  frontend        start Vite dev server (auto-installs node + deps if missing)"
	@echo "  test            run pytest"
	@echo "  db-init         apply 01-05 SQL files"
	@echo "  db-reset        drop + re-init + load demo data"
	@echo "  db-drop         drop everything"
	@echo "  demo-load       load sql/06_seed.sql"
	@echo "  perf-load       load sql/07_seed_perf.sql (~50K rows)"
	@echo "  doctor          report which tools are installed"

# ------------------------------------------------------------
# Tool checks + auto-install (Ubuntu only)
# ------------------------------------------------------------

ensure-uv:
	@if command -v uv >/dev/null 2>&1; then \
	  echo "✓ uv $$(uv --version)"; \
	else \
	  echo "✗ uv not found"; \
	  if [ "$(IS_UBUNTU)" = "yes" ]; then \
	    echo "→ installing uv (Astral) ..."; \
	    curl -LsSf https://astral.sh/uv/install.sh | sh; \
	    echo "✓ uv installed → 重启 shell 或执行 'source $$HOME/.local/bin/env' 让 PATH 生效"; \
	  else \
	    echo "请手动安装 uv:"; \
	    echo "  macOS:  brew install uv"; \
	    echo "  其他:    curl -LsSf https://astral.sh/uv/install.sh | sh"; \
	    exit 1; \
	  fi; \
	fi

ensure-node:
	@if command -v node >/dev/null 2>&1 && command -v npm >/dev/null 2>&1; then \
	  echo "✓ node $$(node --version) · npm $$(npm --version)"; \
	else \
	  echo "✗ node/npm not found"; \
	  if [ "$(IS_UBUNTU)" = "yes" ]; then \
	    echo "→ installing Node.js 20 (NodeSource) ..."; \
	    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -; \
	    sudo apt-get install -y nodejs; \
	    echo "✓ node installed: $$(node --version)"; \
	  else \
	    echo "请手动安装 node 18+:"; \
	    echo "  macOS:  brew install node"; \
	    echo "  Win:     https://nodejs.org/"; \
	    exit 1; \
	  fi; \
	fi

ensure-mysql-client:
	@if command -v mysql >/dev/null 2>&1; then \
	  echo "✓ mysql client"; \
	else \
	  echo "✗ mysql client not found"; \
	  if [ "$(IS_UBUNTU)" = "yes" ]; then \
	    echo "→ installing mysql-client ..."; \
	    sudo apt-get update && sudo apt-get install -y mysql-client; \
	  else \
	    echo "请手动安装 mysql client (brew install mysql-client / 等)"; \
	    exit 1; \
	  fi; \
	fi

doctor:
	@$(MAKE) -s ensure-uv || true
	@$(MAKE) -s ensure-node || true
	@$(MAKE) -s ensure-mysql-client || true
	@echo "---"
	@if [ -d backend/.venv ]; then echo "✓ backend/.venv exists"; else echo "✗ backend/.venv missing (运行 make backend 自动创建)"; fi
	@if [ -d frontend/node_modules ]; then echo "✓ frontend/node_modules exists"; else echo "✗ frontend/node_modules missing (运行 make frontend 自动创建)"; fi

# ------------------------------------------------------------
# Backend
# ------------------------------------------------------------

install-backend: ensure-uv
	@cd backend && \
	if [ ! -d .venv ]; then \
	  echo "→ creating venv ..."; \
	  uv venv; \
	fi && \
	if [ ! -f .venv/bin/uvicorn ]; then \
	  echo "→ installing backend deps ..."; \
	  uv pip install -e ".[dev]"; \
	fi

backend: install-backend
	cd backend && uv run uvicorn app.main:app --reload --port 8000

# ------------------------------------------------------------
# Frontend
# ------------------------------------------------------------

install-frontend: ensure-node
	@cd frontend && \
	if [ ! -d node_modules ]; then \
	  echo "→ installing frontend deps (npm install) ..."; \
	  npm install; \
	fi

frontend: install-frontend
	cd frontend && npm run dev

# ------------------------------------------------------------
# Tests
# ------------------------------------------------------------

test: install-backend
	cd backend && uv run pytest -v

# ------------------------------------------------------------
# Database
# ------------------------------------------------------------

db-init: ensure-mysql-client
	$(MYSQL_CONN) < sql/01_schema.sql
	$(MYSQL_CONN) < sql/02_indexes.sql
	$(MYSQL_CONN) < sql/03_views.sql
	$(MYSQL_CONN) < sql/04_triggers.sql
	$(MYSQL_CONN) < sql/05_procedures.sql

db-drop: ensure-mysql-client
	$(MYSQL_CONN) < sql/00_drop_all.sql

db-reset: db-drop db-init demo-load

demo-load: ensure-mysql-client
	$(MYSQL_CONN) < sql/06_seed.sql

perf-load: ensure-mysql-client
	$(MYSQL_CONN) < sql/07_seed_perf.sql

# Quick connection check + show effective config
db-ping: ensure-mysql-client
	@echo "DB_HOST=$(DB_HOST) DB_PORT=$(DB_PORT) DB_USER=$(DB_USER) DB_NAME=$(DB_NAME)"
	@$(MYSQL_ADMIN) -e "SELECT VERSION() AS mysql_version, DATABASE() AS db, USER() AS user;"

# Create the database (if it doesn't exist) — for fresh cloud servers
db-create: ensure-mysql-client
	@echo "Creating database $(DB_NAME) (if not exists) ..."
	$(MYSQL_ADMIN) -e "CREATE DATABASE IF NOT EXISTS $(DB_NAME) DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;"
	$(MYSQL_ADMIN) -e "SET GLOBAL log_bin_trust_function_creators = 1;" 2>/dev/null || echo "(skip log_bin_trust — non-fatal)"
