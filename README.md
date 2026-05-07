# NKG — Narrative Knowledge Graph Management System

Database course final project.

## Quick Start (local MySQL)

```bash
mysql -u root -p -e "CREATE DATABASE nkg DEFAULT CHARSET utf8mb4;"
cp .env.example .env  # fill DB_USER / DB_PASSWORD / MINIMAX_API_KEY
make db-init
make demo-load

cd backend && uv venv && source .venv/bin/activate && uv pip install -e .
cd .. && make backend  # http://localhost:8000

cd frontend && pnpm install && pnpm dev  # http://localhost:5173
```

## Quick Start (Docker MySQL)

```bash
docker compose up -d mysql adminer
make db-init && make demo-load
```

See `docs/05-操作手册.md` for full instructions.
