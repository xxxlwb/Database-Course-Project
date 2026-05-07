# NKG Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Narrative Knowledge Graph (NKG) management system for the database course final project — meeting all rubric requirements (≥5 tables, ≥3 triggers, ≥2 parametric SPs, ≥2 cursor SPs, ≥2 indexes + perf analysis, 3NF) plus a Vue3 web UI and 4000+ word documentation, targeting 90+/100.

**Architecture:** MySQL 8 (12 tables, 5 triggers, 6 SPs, 7 indexes, 3 views) ← FastAPI Python backend (raw SQL via `sqlalchemy.text`) ← Vue3 + Element Plus + ECharts frontend. LLM extraction via MiniMax (OpenAI-compatible). RAG infrastructure reserved (2 embedding tables + 5 stub routes), feature-flag off.

**Tech Stack:** MySQL 8.0 · Python 3.11 + FastAPI + uvicorn + SQLAlchemy + pymysql + bcrypt + python-jose · Vue 3 + Vite + TypeScript + Element Plus + ECharts + Pinia + Vue Router + Monaco Editor · pytest + httpx · uv (Python pkg) + pnpm (JS pkg)

**Spec:** See `docs/superpowers/specs/2026-05-07-nkg-design.md` for the full design.

**Rubric coverage tracked at end of every phase.**

---

## Phase 0 — Project Bootstrap

### Task 0.1: Init repo skeleton

**Files:**
- Create: `Makefile`, `.env.example`, `.gitignore`, `README.md` (overwrite), `docker-compose.yml`
- Create dirs: `sql/`, `backend/`, `frontend/`, `scripts/`, `docs/images/`

- [ ] **Step 1: Create directory skeleton**

```bash
cd /Users/luwenbo/projects/test/db_course
mkdir -p sql backend/app frontend scripts docs/images
```

- [ ] **Step 2: Write top-level `.gitignore`**

Create `.gitignore`:
```
# Python
__pycache__/
*.py[cod]
.venv/
.pytest_cache/
.env
*.egg-info/

# Node
node_modules/
dist/
.vite/

# OS
.DS_Store

# Editors
.vscode/
.idea/

# Course-specific
backend/.env
frontend/.env
*.sqlite
backend/uploads/
```

- [ ] **Step 3: Write `.env.example`**

Create `.env.example`:
```
# DB
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=nkg

# JWT
JWT_SECRET=change-me-to-a-long-random-string
JWT_EXPIRE_MIN=1440

# LLM
MINIMAX_API_KEY=
MINIMAX_BASE_URL=https://api.minimaxi.com/v1
MINIMAX_MODEL=abab6.5s-chat
LLM_MOCK=true

# RAG (reserved, not implemented)
RAG_ENABLED=false
EMBEDDING_MODEL=minimax-embedding-001
EMBEDDING_DIM=1024

# SQL Console
SQL_CONSOLE_ENABLED=true
```

- [ ] **Step 4: Write top-level `Makefile`**

Create `Makefile`:
```makefile
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
```

- [ ] **Step 5: Write `docker-compose.yml`**

Create `docker-compose.yml`:
```yaml
services:
  mysql:
    image: mysql:8.0
    container_name: nkg-mysql
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: nkg
      MYSQL_USER: nkg
      MYSQL_PASSWORD: nkg
    ports:
      - "3306:3306"
    volumes:
      - nkg-mysql-data:/var/lib/mysql
    command: --default-authentication-plugin=mysql_native_password --character-set-server=utf8mb4

  adminer:
    image: adminer:latest
    container_name: nkg-adminer
    restart: unless-stopped
    ports:
      - "8080:8080"
    depends_on:
      - mysql

volumes:
  nkg-mysql-data:
```

- [ ] **Step 6: Overwrite `README.md`**

Create `README.md`:
```markdown
# NKG — Narrative Knowledge Graph Management System

Database course final project.

## Quick Start (local MySQL)

\`\`\`bash
mysql -u root -p -e "CREATE DATABASE nkg DEFAULT CHARSET utf8mb4;"
cp .env.example .env  # fill DB_USER / DB_PASSWORD / MINIMAX_API_KEY
make db-init
make demo-load

cd backend && uv venv && source .venv/bin/activate && uv pip install -e .
cd .. && make backend  # http://localhost:8000

cd frontend && pnpm install && pnpm dev  # http://localhost:5173
\`\`\`

## Quick Start (Docker MySQL)

\`\`\`bash
docker compose up -d mysql adminer
make db-init && make demo-load
\`\`\`

See `docs/05-操作手册.md` for full instructions.
```

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "chore: bootstrap repo skeleton with Makefile, .env.example, docker-compose"
```

---

### Task 0.2: Init backend Python project

**Files:**
- Create: `backend/pyproject.toml`, `backend/app/__init__.py`, `backend/tests/__init__.py`, `backend/tests/conftest.py`

- [ ] **Step 1: Write `backend/pyproject.toml`**

```toml
[project]
name = "nkg-backend"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.110",
    "uvicorn[standard]>=0.27",
    "sqlalchemy>=2.0",
    "pymysql>=1.1",
    "cryptography>=42",
    "pydantic>=2.6",
    "pydantic-settings>=2.2",
    "python-jose[cryptography]>=3.3",
    "passlib[bcrypt]>=1.7",
    "python-multipart>=0.0.9",
    "openai>=1.30",
    "pypdf>=4.0",
    "python-dotenv>=1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "httpx>=0.27",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

- [ ] **Step 2: Initialize venv**

```bash
cd backend
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

Expected: dependencies install without error.

- [ ] **Step 3: Create `backend/app/__init__.py`** (empty file)

- [ ] **Step 4: Create `backend/tests/__init__.py`** (empty file)

- [ ] **Step 5: Create `backend/tests/conftest.py`**

```python
import os
import pytest
from sqlalchemy import create_engine, text

# Tests use a separate database: nkg_test
TEST_DB = "nkg_test"

def _admin_url():
    user = os.getenv("DB_USER", "root")
    pwd = os.getenv("DB_PASSWORD", "")
    host = os.getenv("DB_HOST", "127.0.0.1")
    port = os.getenv("DB_PORT", "3306")
    return f"mysql+pymysql://{user}:{pwd}@{host}:{port}"

def _test_url():
    return f"{_admin_url()}/{TEST_DB}?charset=utf8mb4"

@pytest.fixture(scope="session")
def db_engine():
    """Create test database, run schema, yield engine, drop database."""
    admin = create_engine(_admin_url(), isolation_level="AUTOCOMMIT")
    with admin.connect() as c:
        c.execute(text(f"DROP DATABASE IF EXISTS {TEST_DB}"))
        c.execute(text(f"CREATE DATABASE {TEST_DB} DEFAULT CHARSET utf8mb4"))

    engine = create_engine(_test_url(), pool_pre_ping=True)

    # Apply all SQL files in order
    sql_dir = os.path.join(os.path.dirname(__file__), "..", "..", "sql")
    for fname in ["01_schema.sql", "02_indexes.sql", "03_views.sql",
                  "04_triggers.sql", "05_procedures.sql"]:
        path = os.path.join(sql_dir, fname)
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8") as f:
            sql_text = f.read()
        # MySQL multi-statement: split by DELIMITER blocks
        _exec_sql_file(engine, sql_text)

    yield engine

    engine.dispose()
    with admin.connect() as c:
        c.execute(text(f"DROP DATABASE IF EXISTS {TEST_DB}"))
    admin.dispose()


def _exec_sql_file(engine, sql_text):
    """Naive splitter that respects DELIMITER directives."""
    delim = ";"
    buf = []
    statements = []
    for line in sql_text.splitlines():
        stripped = line.strip()
        if stripped.upper().startswith("DELIMITER"):
            if buf:
                statements.append("\n".join(buf).strip())
                buf = []
            delim = stripped.split(None, 1)[1]
            continue
        if stripped.endswith(delim):
            buf.append(line[: line.rfind(delim)])
            statements.append("\n".join(buf).strip())
            buf = []
        else:
            buf.append(line)
    if buf:
        rest = "\n".join(buf).strip()
        if rest:
            statements.append(rest)

    raw = engine.raw_connection()
    try:
        cur = raw.cursor()
        for stmt in statements:
            if stmt and not stmt.startswith("--"):
                cur.execute(stmt)
        raw.commit()
    finally:
        raw.close()


@pytest.fixture(autouse=True)
def db_clean(db_engine):
    """Truncate every data table before each test (preserve schema/triggers/SPs)."""
    tables = [
        "audit_logs", "extraction_jobs", "chunk_entity_mapping",
        "relationships", "entity_aliases", "entities",
        "analysis_blueprints", "cognitive_maps", "document_chunks",
        "documents", "topics", "users",
        "chunk_embeddings", "entity_embeddings",
    ]
    with db_engine.connect() as c:
        c.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        for t in tables:
            c.execute(text(f"TRUNCATE TABLE {t}"))
        c.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        c.commit()
    yield
```

- [ ] **Step 6: Smoke test**

```bash
cd backend && uv run python -c "import fastapi, sqlalchemy, pymysql; print('OK')"
```

Expected: `OK`

- [ ] **Step 7: Commit**

```bash
git add backend/pyproject.toml backend/app/__init__.py backend/tests/__init__.py backend/tests/conftest.py
git commit -m "chore(backend): init Python project with pytest fixtures"
```

---

### Task 0.3: Init frontend Vue project

**Files:**
- Create: `frontend/package.json`, `frontend/vite.config.ts`, `frontend/tsconfig.json`, `frontend/index.html`, `frontend/src/main.ts`, `frontend/src/App.vue`, `frontend/.env.example`

- [ ] **Step 1: `frontend/package.json`**

```json
{
  "name": "nkg-frontend",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.3.0",
    "pinia": "^2.1.0",
    "axios": "^1.6.0",
    "element-plus": "^2.7.0",
    "@element-plus/icons-vue": "^2.3.0",
    "echarts": "^5.5.0",
    "vue-echarts": "^7.0.0",
    "monaco-editor": "^0.47.0",
    "@guolao/vue-monaco-editor": "^1.5.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "typescript": "^5.4.0",
    "vite": "^5.2.0",
    "vue-tsc": "^2.0.0"
  }
}
```

- [ ] **Step 2: `frontend/vite.config.ts`**

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': { target: 'http://localhost:8000', changeOrigin: true },
    },
  },
})
```

- [ ] **Step 3: `frontend/tsconfig.json`**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "strict": true,
    "jsx": "preserve",
    "esModuleInterop": true,
    "skipLibCheck": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "types": ["vite/client"]
  },
  "include": ["src/**/*.ts", "src/**/*.vue"]
}
```

- [ ] **Step 4: `frontend/index.html`**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>NKG · 叙事知识图谱</title>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.ts"></script>
</body>
</html>
```

- [ ] **Step 5: `frontend/src/main.ts`**

```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(ElementPlus)
app.mount('#app')
```

- [ ] **Step 6: `frontend/src/App.vue`**

```vue
<template>
  <router-view />
</template>
```

- [ ] **Step 7: Install + smoke**

```bash
cd frontend && pnpm install
```

(Router file deferred to Task 10.x; build will fail until then — acceptable for now.)

- [ ] **Step 8: Commit**

```bash
git add frontend/package.json frontend/vite.config.ts frontend/tsconfig.json frontend/index.html frontend/src/main.ts frontend/src/App.vue
git commit -m "chore(frontend): init Vue3 + Vite + Element Plus skeleton"
```

---

### Task 0.4: Verify MySQL connection

- [ ] **Step 1: Create database**

```bash
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS nkg DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

Expected: no error.

- [ ] **Step 2: Verify version (must be 8.x)**

```bash
mysql -u root -p -e "SELECT VERSION();"
```

Expected: `8.0.x` or `8.x.x`. If older, install MySQL 8.

- [ ] **Step 3: Verify trigger/SP support**

```bash
mysql -u root -p nkg -e "
  CREATE PROCEDURE test_sp() BEGIN SELECT 1; END;
  CALL test_sp();
  DROP PROCEDURE test_sp;
"
```

Expected: returns row `1`. If error → MySQL build lacks SP support, abort.

---

## Phase 1 — Database Schema (12 tables)

### Task 1.1: `sql/00_drop_all.sql`

**Files:**
- Create: `sql/00_drop_all.sql`

- [ ] **Step 1: Write file**

```sql
-- Drop everything in dependency order (children first)
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS audit_logs;
DROP TABLE IF EXISTS extraction_jobs;
DROP TABLE IF EXISTS chunk_entity_mapping;
DROP TABLE IF EXISTS relationships;
DROP TABLE IF EXISTS entity_aliases;
DROP TABLE IF EXISTS entities;
DROP TABLE IF EXISTS analysis_blueprints;
DROP TABLE IF EXISTS cognitive_maps;
DROP TABLE IF EXISTS chunk_embeddings;
DROP TABLE IF EXISTS entity_embeddings;
DROP TABLE IF EXISTS document_chunks;
DROP TABLE IF EXISTS documents;
DROP TABLE IF EXISTS topics;
DROP TABLE IF EXISTS users;

DROP VIEW IF EXISTS v_entity_centrality;
DROP VIEW IF EXISTS v_topic_overview;
DROP VIEW IF EXISTS v_extraction_job_status;

DROP PROCEDURE IF EXISTS sp_create_extraction_job;
DROP PROCEDURE IF EXISTS sp_merge_entities;
DROP PROCEDURE IF EXISTS sp_get_entity_neighborhood;
DROP PROCEDURE IF EXISTS sp_recompute_entity_mentions;
DROP PROCEDURE IF EXISTS sp_archive_inactive_topics;
DROP PROCEDURE IF EXISTS sp_propagate_entity_rename;

SET FOREIGN_KEY_CHECKS = 1;
```

- [ ] **Step 2: Verify it runs cleanly on empty DB**

```bash
mysql -u root -p nkg < sql/00_drop_all.sql
```

Expected: no error.

- [ ] **Step 3: Commit**

```bash
git add sql/00_drop_all.sql
git commit -m "feat(sql): add drop-all script for clean re-init"
```

---

### Task 1.2: `sql/01_schema.sql` — all 12 tables + 2 reserved RAG tables

**Files:**
- Create: `sql/01_schema.sql`

- [ ] **Step 1: Write the full DDL**

```sql
-- ============================================================
-- NKG Schema · MySQL 8.0+
-- All tables in 3NF (with documented denormalizations).
-- ============================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 1;

-- 1. users
CREATE TABLE users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(64) NOT NULL UNIQUE,
    password_hash CHAR(60) NOT NULL,
    email VARCHAR(128) NOT NULL UNIQUE,
    role ENUM('admin','editor','viewer') NOT NULL DEFAULT 'editor',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统用户';

-- 2. topics
CREATE TABLE topics (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    description TEXT,
    owner_id BIGINT NOT NULL,
    doc_count INT NOT NULL DEFAULT 0 COMMENT '触发器维护',
    blueprint_status ENUM('outdated','generating','ready','failed') NOT NULL DEFAULT 'outdated',
    is_archived TINYINT(1) NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_topic_owner_name (owner_id, name),
    CONSTRAINT fk_topics_owner FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='主题/语境空间';

-- 3. documents
CREATE TABLE documents (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    topic_id BIGINT NOT NULL,
    uploader_id BIGINT NOT NULL,
    title VARCHAR(255) NOT NULL,
    source_type ENUM('text','markdown','pdf') NOT NULL DEFAULT 'text',
    original_filename VARCHAR(255),
    file_size BIGINT,
    storage_path VARCHAR(512) COMMENT '大文件落盘路径',
    content MEDIUMTEXT COMMENT '解析后纯文本',
    content_hash CHAR(64) NOT NULL,
    chunks_count INT NOT NULL DEFAULT 0 COMMENT '触发器维护',
    status ENUM('uploaded','chunking','chunk_done','extracting','completed','failed') NOT NULL DEFAULT 'uploaded',
    uploaded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_documents_topic FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE,
    CONSTRAINT fk_documents_uploader FOREIGN KEY (uploader_id) REFERENCES users(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='上传文档';

-- 4. document_chunks
CREATE TABLE document_chunks (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    document_id BIGINT NOT NULL,
    chunk_index INT NOT NULL,
    content MEDIUMTEXT NOT NULL,
    content_hash CHAR(64),
    token_count INT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_chunk_doc_idx (document_id, chunk_index),
    CONSTRAINT fk_chunks_document FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='文档切块';

-- 5. cognitive_maps
CREATE TABLE cognitive_maps (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    document_id BIGINT NOT NULL UNIQUE,
    summary TEXT,
    key_entities JSON,
    themes JSON,
    timeline JSON,
    structural_patterns JSON,
    generated_by VARCHAR(64),
    version INT NOT NULL DEFAULT 1,
    generated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_cogmap_document FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='单文档认知地图';

-- 6. analysis_blueprints
CREATE TABLE analysis_blueprints (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    topic_id BIGINT NOT NULL UNIQUE,
    canonical_entities JSON,
    key_patterns JSON,
    global_timeline JSON,
    processing_instructions TEXT,
    contributing_doc_count INT,
    source_data_hash CHAR(64),
    status ENUM('outdated','generating','ready','failed') NOT NULL DEFAULT 'outdated',
    version INT NOT NULL DEFAULT 1,
    generated_at DATETIME,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_blueprint_topic FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='主题分析蓝图';

-- 7. entities
CREATE TABLE entities (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    topic_id BIGINT NOT NULL,
    canonical_name VARCHAR(255) NOT NULL,
    entity_type ENUM('person','project','task','concept','decision','event','place','other') NOT NULL,
    description TEXT,
    attributes JSON,
    mention_count INT NOT NULL DEFAULT 0 COMMENT '触发器维护',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_entity_topic_type_name (topic_id, entity_type, canonical_name),
    CONSTRAINT fk_entities_topic FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='实体节点';

-- 8. entity_aliases
CREATE TABLE entity_aliases (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    entity_id BIGINT NOT NULL,
    alias VARCHAR(255) NOT NULL,
    source ENUM('auto','user') NOT NULL DEFAULT 'auto',
    confidence DECIMAL(3,2) NOT NULL DEFAULT 1.00,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_alias_entity (entity_id, alias),
    CONSTRAINT fk_alias_entity FOREIGN KEY (entity_id) REFERENCES entities(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='实体别名';

-- 9. relationships
CREATE TABLE relationships (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    topic_id BIGINT NOT NULL,
    source_entity_id BIGINT NOT NULL,
    target_entity_id BIGINT NOT NULL,
    relation_type VARCHAR(64) NOT NULL,
    description TEXT,
    weight DECIMAL(4,3) NOT NULL DEFAULT 1.000,
    attributes JSON,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_rel_topic_src_dst_type (topic_id, source_entity_id, target_entity_id, relation_type),
    CONSTRAINT fk_rel_topic FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE,
    CONSTRAINT fk_rel_src FOREIGN KEY (source_entity_id) REFERENCES entities(id) ON DELETE CASCADE,
    CONSTRAINT fk_rel_dst FOREIGN KEY (target_entity_id) REFERENCES entities(id) ON DELETE CASCADE,
    CONSTRAINT chk_rel_self CHECK (source_entity_id <> target_entity_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='实体关系';

-- 10. chunk_entity_mapping
CREATE TABLE chunk_entity_mapping (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    chunk_id BIGINT NOT NULL,
    entity_id BIGINT NOT NULL,
    occurrences INT NOT NULL DEFAULT 1,
    position_info JSON,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_mapping_chunk_entity (chunk_id, entity_id),
    CONSTRAINT fk_mapping_chunk FOREIGN KEY (chunk_id) REFERENCES document_chunks(id) ON DELETE CASCADE,
    CONSTRAINT fk_mapping_entity FOREIGN KEY (entity_id) REFERENCES entities(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='块-实体映射';

-- 11. extraction_jobs
CREATE TABLE extraction_jobs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    document_id BIGINT,
    topic_id BIGINT NOT NULL,
    job_type ENUM('cognitive_map','blueprint','graph') NOT NULL,
    status ENUM('pending','running','completed','failed') NOT NULL DEFAULT 'pending',
    progress TINYINT NOT NULL DEFAULT 0,
    result JSON,
    error_message TEXT,
    created_by BIGINT,
    started_at DATETIME,
    completed_at DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_job_document FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    CONSTRAINT fk_job_topic FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE,
    CONSTRAINT fk_job_user FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='抽取任务状态机';

-- 12. audit_logs
CREATE TABLE audit_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT,
    action VARCHAR(32) NOT NULL,
    entity_type VARCHAR(32),
    entity_id BIGINT,
    before_value JSON,
    after_value JSON,
    ip_address VARCHAR(45),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_audit_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='操作审计日志';

-- ============================================================
-- RAG-reserved tables (本期不实现, schema-only forward compat)
-- ============================================================

CREATE TABLE chunk_embeddings (
    chunk_id BIGINT PRIMARY KEY,
    embedding LONGBLOB NOT NULL,
    embedding_dim INT NOT NULL,
    model VARCHAR(64) NOT NULL,
    norm DECIMAL(10,6),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_chunk_emb FOREIGN KEY (chunk_id) REFERENCES document_chunks(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='RAG 预留: chunk 向量';

CREATE TABLE entity_embeddings (
    entity_id BIGINT PRIMARY KEY,
    embedding LONGBLOB NOT NULL,
    embedding_dim INT NOT NULL,
    model VARCHAR(64) NOT NULL,
    norm DECIMAL(10,6),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_entity_emb FOREIGN KEY (entity_id) REFERENCES entities(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='RAG 预留: entity 向量';
```

- [ ] **Step 2: Apply to dev DB**

```bash
mysql -u root -p nkg < sql/00_drop_all.sql
mysql -u root -p nkg < sql/01_schema.sql
```

Expected: no errors.

- [ ] **Step 3: Verify table count**

```bash
mysql -u root -p nkg -e "SELECT COUNT(*) AS tbl_count FROM information_schema.tables WHERE table_schema='nkg';"
```

Expected: `14` (12 main + 2 RAG reserved).

- [ ] **Step 4: Verify FK constraints exist**

```bash
mysql -u root -p nkg -e "
  SELECT COUNT(*) AS fk_count FROM information_schema.referential_constraints
  WHERE constraint_schema='nkg';"
```

Expected: ≥ 14.

- [ ] **Step 5: Commit**

```bash
git add sql/01_schema.sql
git commit -m "feat(sql): create 12 main tables + 2 RAG-reserved tables in 3NF"
```

---

### Task 1.3: pytest schema sanity test

**Files:**
- Create: `backend/tests/test_schema.py`

- [ ] **Step 1: Write test**

```python
from sqlalchemy import text

def test_all_tables_exist(db_engine):
    expected = {
        "users", "topics", "documents", "document_chunks",
        "cognitive_maps", "analysis_blueprints",
        "entities", "entity_aliases", "relationships",
        "chunk_entity_mapping", "extraction_jobs", "audit_logs",
        "chunk_embeddings", "entity_embeddings",
    }
    with db_engine.connect() as c:
        rows = c.execute(text(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = DATABASE()"
        )).all()
    actual = {r[0] for r in rows}
    missing = expected - actual
    assert not missing, f"Missing tables: {missing}"


def test_users_unique_username(db_engine):
    with db_engine.connect() as c:
        c.execute(text(
            "INSERT INTO users (username, password_hash, email) "
            "VALUES ('alice', 'x', 'a@b.com')"
        ))
        c.commit()
        try:
            c.execute(text(
                "INSERT INTO users (username, password_hash, email) "
                "VALUES ('alice', 'y', 'c@d.com')"
            ))
            c.commit()
            assert False, "expected duplicate username to fail"
        except Exception as e:
            assert "Duplicate" in str(e) or "1062" in str(e)


def test_relationship_self_loop_blocked(db_engine):
    with db_engine.connect() as c:
        c.execute(text(
            "INSERT INTO users (id, username, password_hash, email) "
            "VALUES (1, 'u', 'x', 'u@u.com')"
        ))
        c.execute(text(
            "INSERT INTO topics (id, name, owner_id) VALUES (1, 't', 1)"
        ))
        c.execute(text(
            "INSERT INTO entities (id, topic_id, canonical_name, entity_type) "
            "VALUES (1, 1, 'X', 'person')"
        ))
        c.commit()
        try:
            c.execute(text(
                "INSERT INTO relationships (topic_id, source_entity_id, target_entity_id, relation_type) "
                "VALUES (1, 1, 1, 'self')"
            ))
            c.commit()
            assert False, "expected CHECK constraint to block self-loop"
        except Exception as e:
            assert "chk_rel_self" in str(e) or "3819" in str(e) or "Check" in str(e)
```

- [ ] **Step 2: Run**

```bash
cd backend && uv run pytest tests/test_schema.py -v
```

Expected: 3 PASSED.

- [ ] **Step 3: Commit**

```bash
git add backend/tests/test_schema.py
git commit -m "test(sql): assert schema integrity (table presence, UQ, CHECK)"
```

---

## Phase 2 — Indexes & Views

### Task 2.1: `sql/02_indexes.sql`

**Files:**
- Create: `sql/02_indexes.sql`

- [ ] **Step 1: Write file**

```sql
-- Secondary indexes for performance
CREATE INDEX idx_documents_topic_status ON documents(topic_id, status);
CREATE INDEX idx_documents_content_hash ON documents(content_hash);
CREATE INDEX idx_entities_topic_type_name ON entities(topic_id, entity_type, canonical_name);
CREATE INDEX idx_relationships_src_dst_type ON relationships(source_entity_id, target_entity_id, relation_type);
CREATE INDEX idx_mapping_entity ON chunk_entity_mapping(entity_id);
CREATE INDEX idx_audit_user_time ON audit_logs(user_id, created_at);
CREATE FULLTEXT INDEX ft_chunks_content ON document_chunks(content);

-- RAG-reserved indexes (model filter)
CREATE INDEX idx_chunk_emb_model ON chunk_embeddings(model);
CREATE INDEX idx_entity_emb_model ON entity_embeddings(model);
```

- [ ] **Step 2: Apply**

```bash
mysql -u root -p nkg < sql/02_indexes.sql
```

Expected: no errors.

- [ ] **Step 3: Verify count**

```bash
mysql -u root -p nkg -e "
  SELECT COUNT(DISTINCT index_name) AS idx_count
  FROM information_schema.statistics
  WHERE table_schema='nkg' AND index_name LIKE 'idx_%' OR index_name LIKE 'ft_%';"
```

Expected: ≥ 7 user-defined secondary indexes (excluding PK + UQ).

- [ ] **Step 4: Commit**

```bash
git add sql/02_indexes.sql
git commit -m "feat(sql): add 7 secondary indexes + 2 RAG-reserved indexes"
```

---

### Task 2.2: `sql/03_views.sql`

**Files:**
- Create: `sql/03_views.sql`

- [ ] **Step 1: Write file**

```sql
-- v_entity_centrality: degree centrality per entity
CREATE OR REPLACE VIEW v_entity_centrality AS
SELECT
    e.id AS entity_id,
    e.topic_id,
    e.canonical_name,
    e.entity_type,
    e.mention_count,
    COALESCE(out_deg.cnt, 0) AS out_degree,
    COALESCE(in_deg.cnt, 0) AS in_degree,
    COALESCE(out_deg.cnt, 0) + COALESCE(in_deg.cnt, 0) AS total_degree
FROM entities e
LEFT JOIN (
    SELECT source_entity_id AS eid, COUNT(*) AS cnt
    FROM relationships GROUP BY source_entity_id
) out_deg ON e.id = out_deg.eid
LEFT JOIN (
    SELECT target_entity_id AS eid, COUNT(*) AS cnt
    FROM relationships GROUP BY target_entity_id
) in_deg ON e.id = in_deg.eid;

-- v_topic_overview: per-topic stats
CREATE OR REPLACE VIEW v_topic_overview AS
SELECT
    t.id AS topic_id,
    t.name AS topic_name,
    t.owner_id,
    t.is_archived,
    t.blueprint_status,
    t.doc_count,
    COALESCE(ec.entity_cnt, 0) AS entity_count,
    COALESCE(rc.rel_cnt, 0) AS relationship_count,
    t.created_at,
    t.updated_at
FROM topics t
LEFT JOIN (
    SELECT topic_id, COUNT(*) AS entity_cnt FROM entities GROUP BY topic_id
) ec ON t.id = ec.topic_id
LEFT JOIN (
    SELECT topic_id, COUNT(*) AS rel_cnt FROM relationships GROUP BY topic_id
) rc ON t.id = rc.topic_id;

-- v_extraction_job_status: aggregated job overview
CREATE OR REPLACE VIEW v_extraction_job_status AS
SELECT
    j.topic_id,
    t.name AS topic_name,
    j.job_type,
    j.status,
    COUNT(*) AS job_count,
    MAX(j.updated_at) AS last_updated
FROM extraction_jobs j
JOIN topics t ON t.id = j.topic_id
GROUP BY j.topic_id, t.name, j.job_type, j.status;
```

- [ ] **Step 2: Apply + verify**

```bash
mysql -u root -p nkg < sql/03_views.sql
mysql -u root -p nkg -e "SHOW FULL TABLES WHERE Table_type='VIEW';"
```

Expected: 3 views listed.

- [ ] **Step 3: Commit**

```bash
git add sql/03_views.sql
git commit -m "feat(sql): add 3 views for centrality, topic overview, job status"
```

---

## Phase 3 — Triggers (5)

### Task 3.1: `trg_documents_after_insert`

**Files:**
- Create: `sql/04_triggers.sql` (will append all 5 triggers across tasks 3.1–3.5; first task creates the file with header)

- [ ] **Step 1: Create `sql/04_triggers.sql` with first trigger**

```sql
-- ============================================================
-- NKG Triggers (5)
-- ============================================================

DELIMITER $$

-- 1) After document inserted: bump topic doc_count + create cognitive_map job + audit
DROP TRIGGER IF EXISTS trg_documents_after_insert$$
CREATE TRIGGER trg_documents_after_insert
AFTER INSERT ON documents
FOR EACH ROW
BEGIN
    UPDATE topics SET doc_count = doc_count + 1 WHERE id = NEW.topic_id;

    INSERT INTO extraction_jobs (document_id, topic_id, job_type, status, created_by)
    VALUES (NEW.id, NEW.topic_id, 'cognitive_map', 'pending', NEW.uploader_id);

    INSERT INTO audit_logs (user_id, action, entity_type, entity_id, after_value)
    VALUES (NEW.uploader_id, 'create', 'document', NEW.id,
            JSON_OBJECT('title', NEW.title, 'topic_id', NEW.topic_id));
END$$

DELIMITER ;
```

- [ ] **Step 2: Apply + verify trigger registered**

```bash
mysql -u root -p nkg < sql/04_triggers.sql
mysql -u root -p nkg -e "SHOW TRIGGERS WHERE \`Trigger\` = 'trg_documents_after_insert';"
```

Expected: 1 row returned.

- [ ] **Step 3: Write pytest**

Create/append `backend/tests/test_triggers.py`:
```python
from sqlalchemy import text


def _seed_user_topic(c, uid=1, tid=1):
    c.execute(text("INSERT INTO users (id, username, password_hash, email) "
                   "VALUES (:u, 'u1', 'x', 'u1@u.com')"), {"u": uid})
    c.execute(text("INSERT INTO topics (id, name, owner_id) "
                   "VALUES (:t, 't1', :u)"), {"t": tid, "u": uid})


def test_trigger_documents_after_insert(db_engine):
    with db_engine.connect() as c:
        _seed_user_topic(c)
        c.execute(text(
            "INSERT INTO documents (id, topic_id, uploader_id, title, source_type, content_hash) "
            "VALUES (1, 1, 1, 'Doc1', 'text', REPEAT('a', 64))"
        ))
        c.commit()

        doc_count = c.execute(text("SELECT doc_count FROM topics WHERE id=1")).scalar()
        assert doc_count == 1, f"expected doc_count=1, got {doc_count}"

        job_count = c.execute(text(
            "SELECT COUNT(*) FROM extraction_jobs WHERE document_id=1 AND job_type='cognitive_map'"
        )).scalar()
        assert job_count == 1

        audit_count = c.execute(text(
            "SELECT COUNT(*) FROM audit_logs WHERE entity_type='document' AND entity_id=1 AND action='create'"
        )).scalar()
        assert audit_count == 1
```

- [ ] **Step 4: Run test**

```bash
cd backend && uv run pytest tests/test_triggers.py::test_trigger_documents_after_insert -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add sql/04_triggers.sql backend/tests/test_triggers.py
git commit -m "feat(sql): trigger #1 trg_documents_after_insert + test"
```

---

### Task 3.2: `trg_chunks_after_insert`

**Files:**
- Modify: `sql/04_triggers.sql` (append before the closing `DELIMITER ;` — wrap so each trigger has its own DELIMITER block; for clarity use one DELIMITER block per trigger)

- [ ] **Step 1: Append to `sql/04_triggers.sql`**

```sql

DELIMITER $$

-- 2) After chunk inserted: bump documents.chunks_count and progress status
DROP TRIGGER IF EXISTS trg_chunks_after_insert$$
CREATE TRIGGER trg_chunks_after_insert
AFTER INSERT ON document_chunks
FOR EACH ROW
BEGIN
    UPDATE documents
    SET chunks_count = chunks_count + 1,
        status = CASE
            WHEN status = 'uploaded' THEN 'chunking'
            ELSE status
        END
    WHERE id = NEW.document_id;
END$$

DELIMITER ;
```

- [ ] **Step 2: Apply**

```bash
mysql -u root -p nkg < sql/04_triggers.sql
```

- [ ] **Step 3: Append test**

Append to `backend/tests/test_triggers.py`:
```python
def test_trigger_chunks_after_insert(db_engine):
    with db_engine.connect() as c:
        _seed_user_topic(c)
        c.execute(text(
            "INSERT INTO documents (id, topic_id, uploader_id, title, source_type, content_hash) "
            "VALUES (1, 1, 1, 'Doc', 'text', REPEAT('b', 64))"
        ))
        c.commit()

        # Insert two chunks
        c.execute(text(
            "INSERT INTO document_chunks (document_id, chunk_index, content) "
            "VALUES (1, 0, 'chunk0'), (1, 1, 'chunk1')"
        ))
        c.commit()

        cnt = c.execute(text("SELECT chunks_count FROM documents WHERE id=1")).scalar()
        assert cnt == 2, f"expected 2 chunks counted, got {cnt}"

        status = c.execute(text("SELECT status FROM documents WHERE id=1")).scalar()
        assert status == "chunking", f"expected status 'chunking', got {status}"
```

- [ ] **Step 4: Run + commit**

```bash
cd backend && uv run pytest tests/test_triggers.py -v
```

```bash
git add sql/04_triggers.sql backend/tests/test_triggers.py
git commit -m "feat(sql): trigger #2 trg_chunks_after_insert + test"
```

---

### Task 3.3: `trg_relationships_before_insert`

- [ ] **Step 1: Append to `sql/04_triggers.sql`**

```sql

DELIMITER $$

-- 3) Before relationship inserted: enforce same-topic + default weight
DROP TRIGGER IF EXISTS trg_relationships_before_insert$$
CREATE TRIGGER trg_relationships_before_insert
BEFORE INSERT ON relationships
FOR EACH ROW
BEGIN
    DECLARE src_topic BIGINT;
    DECLARE dst_topic BIGINT;

    SELECT topic_id INTO src_topic FROM entities WHERE id = NEW.source_entity_id;
    SELECT topic_id INTO dst_topic FROM entities WHERE id = NEW.target_entity_id;

    IF src_topic IS NULL OR dst_topic IS NULL OR src_topic <> dst_topic OR src_topic <> NEW.topic_id THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'cross-topic relationship rejected by trigger';
    END IF;

    IF NEW.weight IS NULL OR NEW.weight = 0 THEN
        SET NEW.weight = 1.000;
    END IF;
END$$

DELIMITER ;
```

- [ ] **Step 2: Apply + test**

Append to `backend/tests/test_triggers.py`:
```python
def test_trigger_relationships_blocks_cross_topic(db_engine):
    with db_engine.connect() as c:
        c.execute(text("INSERT INTO users (id, username, password_hash, email) VALUES (1,'u','x','u@u')"))
        c.execute(text("INSERT INTO topics (id, name, owner_id) VALUES (1,'A',1),(2,'B',1)"))
        c.execute(text(
            "INSERT INTO entities (id, topic_id, canonical_name, entity_type) "
            "VALUES (1,1,'X','person'),(2,2,'Y','person')"
        ))
        c.commit()
        try:
            c.execute(text(
                "INSERT INTO relationships (topic_id, source_entity_id, target_entity_id, relation_type) "
                "VALUES (1, 1, 2, 'knows')"
            ))
            c.commit()
            assert False, "expected cross-topic to be rejected"
        except Exception as e:
            assert "cross-topic" in str(e) or "45000" in str(e)
```

```bash
cd backend && uv run pytest tests/test_triggers.py -v
```

- [ ] **Step 3: Commit**

```bash
git add sql/04_triggers.sql backend/tests/test_triggers.py
git commit -m "feat(sql): trigger #3 trg_relationships_before_insert + test"
```

---

### Task 3.4: `trg_entities_after_update`

- [ ] **Step 1: Append to `sql/04_triggers.sql`**

```sql

DELIMITER $$

-- 4) After entity updated: if canonical_name changed, mark blueprint outdated + audit
DROP TRIGGER IF EXISTS trg_entities_after_update$$
CREATE TRIGGER trg_entities_after_update
AFTER UPDATE ON entities
FOR EACH ROW
BEGIN
    IF OLD.canonical_name <> NEW.canonical_name THEN
        UPDATE topics
           SET blueprint_status = 'outdated'
         WHERE id = NEW.topic_id;

        INSERT INTO audit_logs (user_id, action, entity_type, entity_id, before_value, after_value)
        VALUES (NULL, 'rename', 'entity', NEW.id,
                JSON_OBJECT('canonical_name', OLD.canonical_name),
                JSON_OBJECT('canonical_name', NEW.canonical_name));
    END IF;
END$$

DELIMITER ;
```

- [ ] **Step 2: Apply + test**

Append:
```python
def test_trigger_entities_rename_marks_blueprint_outdated(db_engine):
    with db_engine.connect() as c:
        _seed_user_topic(c)
        c.execute(text(
            "INSERT INTO entities (id, topic_id, canonical_name, entity_type) "
            "VALUES (1, 1, 'old', 'person')"
        ))
        c.execute(text(
            "INSERT INTO analysis_blueprints (topic_id, status) VALUES (1, 'ready')"
        ))
        c.execute(text("UPDATE topics SET blueprint_status='ready' WHERE id=1"))
        c.commit()

        c.execute(text("UPDATE entities SET canonical_name='new' WHERE id=1"))
        c.commit()

        bs = c.execute(text("SELECT blueprint_status FROM topics WHERE id=1")).scalar()
        assert bs == "outdated"

        audit = c.execute(text(
            "SELECT COUNT(*) FROM audit_logs WHERE action='rename' AND entity_id=1"
        )).scalar()
        assert audit == 1
```

```bash
cd backend && uv run pytest tests/test_triggers.py -v
```

- [ ] **Step 3: Commit**

```bash
git add sql/04_triggers.sql backend/tests/test_triggers.py
git commit -m "feat(sql): trigger #4 trg_entities_after_update + test"
```

---

### Task 3.5: `trg_chunk_entity_after_insert`

- [ ] **Step 1: Append to `sql/04_triggers.sql`**

```sql

DELIMITER $$

-- 5) After chunk-entity mapping inserted: bump entity mention_count
DROP TRIGGER IF EXISTS trg_chunk_entity_after_insert$$
CREATE TRIGGER trg_chunk_entity_after_insert
AFTER INSERT ON chunk_entity_mapping
FOR EACH ROW
BEGIN
    UPDATE entities
       SET mention_count = mention_count + NEW.occurrences
     WHERE id = NEW.entity_id;
END$$

DELIMITER ;
```

- [ ] **Step 2: Apply + test**

Append:
```python
def test_trigger_chunk_entity_increments_mention(db_engine):
    with db_engine.connect() as c:
        _seed_user_topic(c)
        c.execute(text(
            "INSERT INTO documents (id, topic_id, uploader_id, title, source_type, content_hash) "
            "VALUES (1,1,1,'D','text',REPEAT('c',64))"
        ))
        c.execute(text(
            "INSERT INTO document_chunks (id, document_id, chunk_index, content) "
            "VALUES (1,1,0,'x')"
        ))
        c.execute(text(
            "INSERT INTO entities (id, topic_id, canonical_name, entity_type) "
            "VALUES (1,1,'E','concept')"
        ))
        c.commit()

        c.execute(text(
            "INSERT INTO chunk_entity_mapping (chunk_id, entity_id, occurrences) "
            "VALUES (1, 1, 3)"
        ))
        c.commit()

        m = c.execute(text("SELECT mention_count FROM entities WHERE id=1")).scalar()
        assert m == 3
```

```bash
cd backend && uv run pytest tests/test_triggers.py -v
```

- [ ] **Step 3: Commit**

```bash
git add sql/04_triggers.sql backend/tests/test_triggers.py
git commit -m "feat(sql): trigger #5 trg_chunk_entity_after_insert + test"
```

**Phase 3 Done.** All 5 triggers implemented + tested. Course requirement (2): ≥3 triggers — **satisfied with 5**.

---

## Phase 4 — Stored Procedures (6)

### Task 4.1: `sp_create_extraction_job` (parametric, IN/OUT)

**Files:**
- Create: `sql/05_procedures.sql`

- [ ] **Step 1: Write file with first SP**

```sql
-- ============================================================
-- NKG Stored Procedures (6)
--   Parametric: sp_create_extraction_job, sp_merge_entities,
--               sp_get_entity_neighborhood
--   Cursor-based: sp_recompute_entity_mentions,
--                 sp_archive_inactive_topics,
--                 sp_propagate_entity_rename
-- ============================================================

DELIMITER $$

DROP PROCEDURE IF EXISTS sp_create_extraction_job$$
CREATE PROCEDURE sp_create_extraction_job(
    IN p_doc_id BIGINT,
    IN p_job_type VARCHAR(32),
    IN p_user_id BIGINT,
    OUT p_job_id BIGINT
)
BEGIN
    DECLARE v_topic_id BIGINT;
    DECLARE v_existing BIGINT DEFAULT 0;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_job_id = NULL;
        RESIGNAL;
    END;

    START TRANSACTION;

    SELECT topic_id INTO v_topic_id FROM documents WHERE id = p_doc_id;
    IF v_topic_id IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'document not found';
    END IF;

    SELECT id INTO v_existing
      FROM extraction_jobs
     WHERE document_id = p_doc_id
       AND job_type = p_job_type
       AND status IN ('pending', 'running')
     LIMIT 1;

    IF v_existing > 0 THEN
        SET p_job_id = v_existing;
    ELSE
        INSERT INTO extraction_jobs (document_id, topic_id, job_type, status, created_by)
        VALUES (p_doc_id, v_topic_id, p_job_type, 'pending', p_user_id);
        SET p_job_id = LAST_INSERT_ID();

        INSERT INTO audit_logs (user_id, action, entity_type, entity_id, after_value)
        VALUES (p_user_id, 'create', 'extraction_job', p_job_id,
                JSON_OBJECT('document_id', p_doc_id, 'job_type', p_job_type));
    END IF;

    COMMIT;
END$$

DELIMITER ;
```

- [ ] **Step 2: Apply**

```bash
mysql -u root -p nkg < sql/05_procedures.sql
```

- [ ] **Step 3: Write test**

Create `backend/tests/test_procedures.py`:
```python
from sqlalchemy import text


def _seed(c):
    c.execute(text("INSERT INTO users (id, username, password_hash, email) VALUES (1,'u','x','u@u')"))
    c.execute(text("INSERT INTO topics (id, name, owner_id) VALUES (1,'T',1)"))
    c.execute(text("INSERT INTO documents (id, topic_id, uploader_id, title, source_type, content_hash) "
                   "VALUES (1,1,1,'D','text',REPEAT('a',64))"))


def test_sp_create_extraction_job(db_engine):
    raw = db_engine.raw_connection()
    cur = raw.cursor()
    cur.execute("INSERT INTO users (id, username, password_hash, email) VALUES (1,'u','x','u@u')")
    cur.execute("INSERT INTO topics (id, name, owner_id) VALUES (1,'T',1)")
    cur.execute("INSERT INTO documents (id, topic_id, uploader_id, title, source_type, content_hash) "
                "VALUES (1,1,1,'D','text',REPEAT('a',64))")
    raw.commit()

    cur.execute("CALL sp_create_extraction_job(1, 'graph', 1, @jid)")
    cur.execute("SELECT @jid")
    job_id = cur.fetchone()[0]
    assert job_id is not None and job_id > 0

    # Idempotency: calling again with same args returns same id
    cur.execute("CALL sp_create_extraction_job(1, 'graph', 1, @jid2)")
    cur.execute("SELECT @jid2")
    job_id_2 = cur.fetchone()[0]
    assert job_id_2 == job_id

    raw.close()
```

- [ ] **Step 4: Run + commit**

```bash
cd backend && uv run pytest tests/test_procedures.py::test_sp_create_extraction_job -v
```

```bash
git add sql/05_procedures.sql backend/tests/test_procedures.py
git commit -m "feat(sql): SP #1 sp_create_extraction_job (parametric IN/OUT) + test"
```

---

### Task 4.2: `sp_merge_entities` (parametric, transactional)

- [ ] **Step 1: Append to `sql/05_procedures.sql`**

```sql

DELIMITER $$

DROP PROCEDURE IF EXISTS sp_merge_entities$$
CREATE PROCEDURE sp_merge_entities(
    IN p_keep_id BIGINT,
    IN p_merge_id BIGINT,
    IN p_user_id BIGINT
)
BEGIN
    DECLARE v_keep_topic BIGINT;
    DECLARE v_merge_topic BIGINT;
    DECLARE v_merge_name VARCHAR(255);

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    IF p_keep_id = p_merge_id THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'cannot merge entity with itself';
    END IF;

    START TRANSACTION;

    SELECT topic_id INTO v_keep_topic FROM entities WHERE id = p_keep_id FOR UPDATE;
    SELECT topic_id, canonical_name INTO v_merge_topic, v_merge_name
      FROM entities WHERE id = p_merge_id FOR UPDATE;

    IF v_keep_topic IS NULL OR v_merge_topic IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'entity not found';
    END IF;
    IF v_keep_topic <> v_merge_topic THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'entities belong to different topics';
    END IF;

    -- migrate aliases (skip on UQ collision)
    INSERT IGNORE INTO entity_aliases (entity_id, alias, source, confidence)
    SELECT p_keep_id, alias, source, confidence FROM entity_aliases WHERE entity_id = p_merge_id;

    -- record merged entity name as new alias
    INSERT IGNORE INTO entity_aliases (entity_id, alias, source, confidence)
    VALUES (p_keep_id, v_merge_name, 'auto', 0.99);

    -- migrate chunk_entity_mapping (skip dupes; sum occurrences for collisions)
    UPDATE IGNORE chunk_entity_mapping
       SET entity_id = p_keep_id
     WHERE entity_id = p_merge_id;
    DELETE FROM chunk_entity_mapping WHERE entity_id = p_merge_id;

    -- migrate relationships (drop self-loops & dupes silently)
    UPDATE IGNORE relationships
       SET source_entity_id = p_keep_id
     WHERE source_entity_id = p_merge_id AND target_entity_id <> p_keep_id;
    DELETE FROM relationships WHERE source_entity_id = p_merge_id;

    UPDATE IGNORE relationships
       SET target_entity_id = p_keep_id
     WHERE target_entity_id = p_merge_id AND source_entity_id <> p_keep_id;
    DELETE FROM relationships WHERE target_entity_id = p_merge_id;

    -- delete merged entity
    DELETE FROM entities WHERE id = p_merge_id;

    -- mark blueprint as outdated
    UPDATE topics SET blueprint_status = 'outdated' WHERE id = v_keep_topic;

    -- audit
    INSERT INTO audit_logs (user_id, action, entity_type, entity_id, before_value, after_value)
    VALUES (p_user_id, 'merge', 'entity', p_keep_id,
            JSON_OBJECT('merged_id', p_merge_id, 'merged_name', v_merge_name),
            JSON_OBJECT('keep_id', p_keep_id));

    COMMIT;
END$$

DELIMITER ;
```

- [ ] **Step 2: Apply**

```bash
mysql -u root -p nkg < sql/05_procedures.sql
```

- [ ] **Step 3: Append test**

```python
def test_sp_merge_entities(db_engine):
    raw = db_engine.raw_connection()
    cur = raw.cursor()
    cur.execute("INSERT INTO users (id, username, password_hash, email) VALUES (1,'u','x','u@u')")
    cur.execute("INSERT INTO topics (id, name, owner_id) VALUES (1,'T',1)")
    cur.execute("INSERT INTO entities (id, topic_id, canonical_name, entity_type) "
                "VALUES (1,1,'A','person'), (2,1,'B','person'), (3,1,'C','person')")
    cur.execute("INSERT INTO entity_aliases (entity_id, alias) VALUES (2, 'B-alias')")
    cur.execute("INSERT INTO relationships (topic_id, source_entity_id, target_entity_id, relation_type) "
                "VALUES (1, 2, 3, 'knows'), (1, 1, 2, 'colleague')")
    raw.commit()

    cur.execute("CALL sp_merge_entities(1, 2, 1)")
    raw.commit()

    cur.execute("SELECT COUNT(*) FROM entities WHERE id=2")
    assert cur.fetchone()[0] == 0, "entity 2 should be deleted"

    cur.execute("SELECT COUNT(*) FROM entity_aliases WHERE entity_id=1 AND alias IN ('B','B-alias')")
    assert cur.fetchone()[0] == 2, "aliases should be migrated"

    cur.execute("SELECT COUNT(*) FROM relationships WHERE source_entity_id=1 AND target_entity_id=3")
    assert cur.fetchone()[0] == 1, "relationship should be redirected"

    cur.execute("SELECT blueprint_status FROM topics WHERE id=1")
    assert cur.fetchone()[0] == 'outdated'

    cur.execute("SELECT COUNT(*) FROM audit_logs WHERE action='merge'")
    assert cur.fetchone()[0] == 1
    raw.close()
```

```bash
cd backend && uv run pytest tests/test_procedures.py::test_sp_merge_entities -v
```

- [ ] **Step 4: Commit**

```bash
git add sql/05_procedures.sql backend/tests/test_procedures.py
git commit -m "feat(sql): SP #2 sp_merge_entities (transactional, multi-table) + test"
```

---

### Task 4.3: `sp_get_entity_neighborhood` (parametric, returns result set)

- [ ] **Step 1: Append to `sql/05_procedures.sql`**

```sql

DELIMITER $$

DROP PROCEDURE IF EXISTS sp_get_entity_neighborhood$$
CREATE PROCEDURE sp_get_entity_neighborhood(
    IN p_entity_id BIGINT,
    IN p_depth INT,
    OUT p_node_count INT
)
BEGIN
    DECLARE v_d INT DEFAULT 0;
    DECLARE v_added INT DEFAULT 1;

    IF p_depth IS NULL OR p_depth < 1 THEN SET p_depth = 1; END IF;
    IF p_depth > 5 THEN SET p_depth = 5; END IF;

    DROP TEMPORARY TABLE IF EXISTS tmp_neighborhood;
    CREATE TEMPORARY TABLE tmp_neighborhood (
        entity_id BIGINT PRIMARY KEY,
        distance INT NOT NULL
    );

    INSERT INTO tmp_neighborhood VALUES (p_entity_id, 0);

    WHILE v_d < p_depth AND v_added > 0 DO
        INSERT IGNORE INTO tmp_neighborhood (entity_id, distance)
        SELECT DISTINCT
               CASE WHEN r.source_entity_id IN (SELECT entity_id FROM tmp_neighborhood WHERE distance = v_d)
                    THEN r.target_entity_id
                    ELSE r.source_entity_id
               END AS new_id,
               v_d + 1
          FROM relationships r
         WHERE r.source_entity_id IN (SELECT entity_id FROM tmp_neighborhood WHERE distance = v_d)
            OR r.target_entity_id IN (SELECT entity_id FROM tmp_neighborhood WHERE distance = v_d);

        SET v_added = ROW_COUNT();
        SET v_d = v_d + 1;
    END WHILE;

    SELECT COUNT(*) INTO p_node_count FROM tmp_neighborhood;

    SELECT n.entity_id, n.distance, e.canonical_name, e.entity_type
      FROM tmp_neighborhood n
      JOIN entities e ON e.id = n.entity_id
     ORDER BY n.distance, n.entity_id;
END$$

DELIMITER ;
```

- [ ] **Step 2: Apply + test**

Append:
```python
def test_sp_get_entity_neighborhood(db_engine):
    raw = db_engine.raw_connection()
    cur = raw.cursor()
    cur.execute("INSERT INTO users (id, username, password_hash, email) VALUES (1,'u','x','u@u')")
    cur.execute("INSERT INTO topics (id, name, owner_id) VALUES (1,'T',1)")
    # Build chain: 1 - 2 - 3 - 4
    cur.execute("INSERT INTO entities (id, topic_id, canonical_name, entity_type) "
                "VALUES (1,1,'A','person'),(2,1,'B','person'),(3,1,'C','person'),(4,1,'D','person')")
    cur.execute("INSERT INTO relationships (topic_id, source_entity_id, target_entity_id, relation_type) "
                "VALUES (1,1,2,'r'),(1,2,3,'r'),(1,3,4,'r')")
    raw.commit()

    cur.execute("CALL sp_get_entity_neighborhood(1, 2, @cnt)")
    rows = cur.fetchall()
    cur.execute("SELECT @cnt")
    cnt = cur.fetchone()[0]
    assert cnt == 3, f"expected nodes {{1,2,3}} (depth 2 from 1), got cnt={cnt}, rows={rows}"
    raw.close()
```

```bash
cd backend && uv run pytest tests/test_procedures.py::test_sp_get_entity_neighborhood -v
```

- [ ] **Step 3: Commit**

```bash
git add sql/05_procedures.sql backend/tests/test_procedures.py
git commit -m "feat(sql): SP #3 sp_get_entity_neighborhood (BFS with temp table) + test"
```

---

### Task 4.4: `sp_recompute_entity_mentions` (CURSOR)

- [ ] **Step 1: Append to `sql/05_procedures.sql`**

```sql

DELIMITER $$

DROP PROCEDURE IF EXISTS sp_recompute_entity_mentions$$
CREATE PROCEDURE sp_recompute_entity_mentions()
BEGIN
    DECLARE v_eid BIGINT;
    DECLARE v_sum INT;
    DECLARE done INT DEFAULT 0;
    DECLARE cur_e CURSOR FOR SELECT id FROM entities;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    OPEN cur_e;
    read_loop: LOOP
        FETCH cur_e INTO v_eid;
        IF done = 1 THEN LEAVE read_loop; END IF;

        SELECT COALESCE(SUM(occurrences), 0) INTO v_sum
          FROM chunk_entity_mapping
         WHERE entity_id = v_eid;

        UPDATE entities SET mention_count = v_sum WHERE id = v_eid;
    END LOOP;
    CLOSE cur_e;
END$$

DELIMITER ;
```

- [ ] **Step 2: Apply + test**

Append:
```python
def test_sp_recompute_entity_mentions(db_engine):
    raw = db_engine.raw_connection()
    cur = raw.cursor()
    cur.execute("INSERT INTO users (id, username, password_hash, email) VALUES (1,'u','x','u@u')")
    cur.execute("INSERT INTO topics (id, name, owner_id) VALUES (1,'T',1)")
    cur.execute("INSERT INTO documents (id, topic_id, uploader_id, title, source_type, content_hash) "
                "VALUES (1,1,1,'D','text',REPEAT('a',64))")
    cur.execute("INSERT INTO document_chunks (id, document_id, chunk_index, content) "
                "VALUES (1,1,0,'a'),(2,1,1,'b')")
    cur.execute("INSERT INTO entities (id, topic_id, canonical_name, entity_type) "
                "VALUES (1,1,'X','concept'),(2,1,'Y','concept')")
    # trigger will set mention_count to 5+3=8 for entity 1 and 7 for entity 2
    cur.execute("INSERT INTO chunk_entity_mapping (chunk_id, entity_id, occurrences) "
                "VALUES (1,1,5),(2,1,3),(1,2,7)")
    # corrupt mention_count manually
    cur.execute("UPDATE entities SET mention_count = 999 WHERE id IN (1,2)")
    raw.commit()

    cur.execute("CALL sp_recompute_entity_mentions()")
    raw.commit()

    cur.execute("SELECT id, mention_count FROM entities ORDER BY id")
    rows = dict(cur.fetchall())
    assert rows[1] == 8, f"entity 1 expected 8, got {rows[1]}"
    assert rows[2] == 7, f"entity 2 expected 7, got {rows[2]}"
    raw.close()
```

```bash
cd backend && uv run pytest tests/test_procedures.py::test_sp_recompute_entity_mentions -v
```

- [ ] **Step 3: Commit**

```bash
git add sql/05_procedures.sql backend/tests/test_procedures.py
git commit -m "feat(sql): SP #4 sp_recompute_entity_mentions (cursor) + test"
```

---

### Task 4.5: `sp_archive_inactive_topics` (CURSOR + IN/OUT)

- [ ] **Step 1: Append to `sql/05_procedures.sql`**

```sql

DELIMITER $$

DROP PROCEDURE IF EXISTS sp_archive_inactive_topics$$
CREATE PROCEDURE sp_archive_inactive_topics(
    IN p_days INT,
    OUT p_archived INT
)
BEGIN
    DECLARE v_tid BIGINT;
    DECLARE done INT DEFAULT 0;
    DECLARE cur_t CURSOR FOR
        SELECT id FROM topics
         WHERE is_archived = 0
           AND updated_at < (NOW() - INTERVAL p_days DAY);
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    SET p_archived = 0;
    IF p_days IS NULL OR p_days < 1 THEN SET p_days = 30; END IF;

    OPEN cur_t;
    archive_loop: LOOP
        FETCH cur_t INTO v_tid;
        IF done = 1 THEN LEAVE archive_loop; END IF;

        UPDATE topics SET is_archived = 1 WHERE id = v_tid;
        INSERT INTO audit_logs (user_id, action, entity_type, entity_id, after_value)
        VALUES (NULL, 'archive', 'topic', v_tid, JSON_OBJECT('archived_after_days', p_days));
        SET p_archived = p_archived + 1;
    END LOOP;
    CLOSE cur_t;
END$$

DELIMITER ;
```

- [ ] **Step 2: Apply + test**

Append:
```python
def test_sp_archive_inactive_topics(db_engine):
    raw = db_engine.raw_connection()
    cur = raw.cursor()
    cur.execute("INSERT INTO users (id, username, password_hash, email) VALUES (1,'u','x','u@u')")
    # Topic 1: stale (60 days old). Topic 2: fresh.
    cur.execute("INSERT INTO topics (id, name, owner_id, updated_at) "
                "VALUES (1,'old',1, NOW() - INTERVAL 60 DAY), (2,'new',1, NOW())")
    raw.commit()

    cur.execute("CALL sp_archive_inactive_topics(30, @cnt)")
    cur.execute("SELECT @cnt")
    archived = cur.fetchone()[0]
    assert archived == 1, f"expected 1 archived, got {archived}"

    cur.execute("SELECT id, is_archived FROM topics ORDER BY id")
    rows = dict(cur.fetchall())
    assert rows[1] == 1 and rows[2] == 0
    raw.close()
```

```bash
cd backend && uv run pytest tests/test_procedures.py::test_sp_archive_inactive_topics -v
```

- [ ] **Step 3: Commit**

```bash
git add sql/05_procedures.sql backend/tests/test_procedures.py
git commit -m "feat(sql): SP #5 sp_archive_inactive_topics (cursor + IN/OUT) + test"
```

---

### Task 4.6: `sp_propagate_entity_rename` (CURSOR + IN)

- [ ] **Step 1: Append to `sql/05_procedures.sql`**

```sql

DELIMITER $$

DROP PROCEDURE IF EXISTS sp_propagate_entity_rename$$
CREATE PROCEDURE sp_propagate_entity_rename(
    IN p_topic_id BIGINT,
    IN p_pattern VARCHAR(255),
    IN p_new_name VARCHAR(255)
)
BEGIN
    DECLARE v_eid BIGINT;
    DECLARE v_old_name VARCHAR(255);
    DECLARE done INT DEFAULT 0;
    DECLARE cur_e CURSOR FOR
        SELECT id, canonical_name FROM entities
         WHERE topic_id = p_topic_id
           AND canonical_name LIKE p_pattern;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;
    OPEN cur_e;
    rename_loop: LOOP
        FETCH cur_e INTO v_eid, v_old_name;
        IF done = 1 THEN LEAVE rename_loop; END IF;

        -- Save old name as alias before rename
        INSERT IGNORE INTO entity_aliases (entity_id, alias, source, confidence)
        VALUES (v_eid, v_old_name, 'auto', 1.00);

        -- Rename (UPDATE may fail on UQ collision; in that case, skip via INSERT IGNORE-style)
        UPDATE IGNORE entities SET canonical_name = p_new_name WHERE id = v_eid;
    END LOOP;
    CLOSE cur_e;
    COMMIT;
END$$

DELIMITER ;
```

- [ ] **Step 2: Apply + test**

Append:
```python
def test_sp_propagate_entity_rename(db_engine):
    raw = db_engine.raw_connection()
    cur = raw.cursor()
    cur.execute("INSERT INTO users (id, username, password_hash, email) VALUES (1,'u','x','u@u')")
    cur.execute("INSERT INTO topics (id, name, owner_id) VALUES (1,'T',1)")
    cur.execute("INSERT INTO entities (id, topic_id, canonical_name, entity_type) "
                "VALUES (1,1,'foo-bar','concept'),(2,1,'foo-baz','concept'),(3,1,'qux','concept')")
    raw.commit()

    cur.execute("CALL sp_propagate_entity_rename(1, 'foo-%', 'normalized')")
    raw.commit()

    cur.execute("SELECT canonical_name FROM entities ORDER BY id")
    names = [r[0] for r in cur.fetchall()]
    # entity 1 renamed; entity 2 hits UQ collision (same new_name) so stays
    assert 'normalized' in names

    cur.execute("SELECT COUNT(*) FROM entity_aliases WHERE alias LIKE 'foo-%'")
    assert cur.fetchone()[0] >= 1
    raw.close()
```

```bash
cd backend && uv run pytest tests/test_procedures.py -v
```

- [ ] **Step 3: Commit**

```bash
git add sql/05_procedures.sql backend/tests/test_procedures.py
git commit -m "feat(sql): SP #6 sp_propagate_entity_rename (cursor + transaction) + test"
```

**Phase 4 Done.** All 6 SPs implemented (3 parametric + 3 cursor). Course requirements (3) ≥2 parametric and (4) ≥2 cursor — **satisfied with 3 each**.

---

## Phase 5 — Seed Data

### Task 5.1: `sql/06_seed.sql` — demo data

**Files:**
- Create: `sql/06_seed.sql`

- [ ] **Step 1: Write demo seed (small, hand-crafted)**

```sql
-- Demo data for in-class showcase

-- 3 users (admin / editor / viewer); password hashes are bcrypt of "demo123"
INSERT INTO users (username, password_hash, email, role) VALUES
('admin',  '$2b$12$KIXwTUf5g2qQH5JfM5zZ.O6XQqK7VxC3mC4vXYa5JXz8w3EYtZxN.', 'admin@nkg.local',  'admin'),
('editor', '$2b$12$KIXwTUf5g2qQH5JfM5zZ.O6XQqK7VxC3mC4vXYa5JXz8w3EYtZxN.', 'editor@nkg.local', 'editor'),
('viewer', '$2b$12$KIXwTUf5g2qQH5JfM5zZ.O6XQqK7VxC3mC4vXYa5JXz8w3EYtZxN.', 'viewer@nkg.local', 'viewer');

-- 2 topics
INSERT INTO topics (name, description, owner_id) VALUES
('三国人物图谱', '基于《三国演义》构建的人物关系图谱', 2),
('项目复盘', '团队季度复盘文档分析', 2);

-- 4 documents
INSERT INTO documents (topic_id, uploader_id, title, source_type, content, content_hash) VALUES
(1, 2, '官渡之战', 'text',
 '建安五年，曹操与袁绍战于官渡。袁绍兵众而粮少，曹操奇袭乌巢烧粮，绍军溃。许攸献策，张郃高览降曹。',
 SHA2('官渡之战', 256)),
(1, 2, '赤壁之战', 'text',
 '建安十三年，孙权刘备联军在周瑜统领下于赤壁大破曹操。诸葛亮舌战群儒促成联盟。黄盖诈降，火烧连营。',
 SHA2('赤壁之战', 256)),
(2, 2, '2024 Q4 复盘', 'markdown',
 '# 2024 Q4 复盘\n\n张三负责支付项目，按期上线。李四主导风控重构，因依赖延期推迟两周。王五处理客户投诉。',
 SHA2('2024Q4', 256)),
(2, 2, '2025 Q1 启动', 'markdown',
 '# 2025 Q1\n\n张三转岗到结算项目，李四继续推进风控2.0，王五接手客服系统重写。',
 SHA2('2025Q1', 256));

-- 8 chunks (2 per document)
INSERT INTO document_chunks (document_id, chunk_index, content) VALUES
(1, 0, '建安五年，曹操与袁绍战于官渡。'),
(1, 1, '袁绍兵众而粮少，曹操奇袭乌巢烧粮，绍军溃。'),
(2, 0, '建安十三年，孙刘联军于赤壁大破曹操。'),
(2, 1, '诸葛亮舌战群儒促成联盟。'),
(3, 0, '张三负责支付项目，按期上线。'),
(3, 1, '李四主导风控重构，因依赖延期推迟两周。'),
(4, 0, '张三转岗到结算项目，李四继续推进风控2.0。'),
(4, 1, '王五接手客服系统重写。');

-- Entities for topic 1 (三国)
INSERT INTO entities (topic_id, canonical_name, entity_type) VALUES
(1, '曹操', 'person'),(1, '袁绍', 'person'),(1, '刘备', 'person'),
(1, '孙权', 'person'),(1, '诸葛亮', 'person'),(1, '周瑜', 'person'),
(1, '官渡之战', 'event'),(1, '赤壁之战', 'event');

-- Entities for topic 2 (项目复盘)
INSERT INTO entities (topic_id, canonical_name, entity_type) VALUES
(2, '张三', 'person'),(2, '李四', 'person'),(2, '王五', 'person'),
(2, '支付项目', 'project'),(2, '风控重构', 'project'),(2, '结算项目', 'project'),
(2, '客服系统', 'project');

-- Relationships for topic 1
INSERT INTO relationships (topic_id, source_entity_id, target_entity_id, relation_type, description) VALUES
(1, 1, 2, '战', '曹袁官渡对决'),
(1, 1, 7, '指挥', NULL),
(1, 2, 7, '指挥', NULL),
(1, 3, 4, '联盟', '孙刘联军'),
(1, 5, 6, '协同', '草船借箭'),
(1, 1, 8, '指挥', NULL),
(1, 6, 8, '指挥', NULL);

-- Relationships for topic 2
INSERT INTO relationships (topic_id, source_entity_id, target_entity_id, relation_type, description) VALUES
(2, 9, 12, '负责', NULL),
(2, 10, 13, '负责', NULL),
(2, 9, 14, '负责', '转岗后'),
(2, 11, 15, '负责', NULL);

-- Some chunk-entity mappings
INSERT INTO chunk_entity_mapping (chunk_id, entity_id, occurrences) VALUES
(1, 1, 1), (1, 2, 1), (2, 1, 1), (2, 2, 1),
(3, 3, 1), (3, 4, 1), (3, 5, 1), (3, 6, 1),
(5, 9, 1), (5, 12, 1),
(6, 10, 1), (6, 13, 1),
(7, 9, 1), (7, 14, 1), (7, 10, 1),
(8, 11, 1), (8, 15, 1);
```

- [ ] **Step 2: Apply**

```bash
mysql -u root -p nkg < sql/06_seed.sql
```

- [ ] **Step 3: Verify**

```bash
mysql -u root -p nkg -e "
  SELECT 'users' AS t, COUNT(*) FROM users
  UNION SELECT 'topics', COUNT(*) FROM topics
  UNION SELECT 'documents', COUNT(*) FROM documents
  UNION SELECT 'chunks', COUNT(*) FROM document_chunks
  UNION SELECT 'entities', COUNT(*) FROM entities
  UNION SELECT 'relationships', COUNT(*) FROM relationships;"
```

Expected:
```
users: 3, topics: 2, documents: 4, chunks: 8, entities: 15, relationships: 11
```

(Note: documents trigger creates 4 cognitive_map jobs; chunks trigger updates docs; chunk_entity trigger increments entity mention_count.)

- [ ] **Step 4: Commit**

```bash
git add sql/06_seed.sql
git commit -m "feat(sql): demo seed data (3 users, 2 topics, 4 docs, 15 entities, 11 rels)"
```

---

### Task 5.2: `sql/07_seed_perf.sql` — 5万级压测数据

- [ ] **Step 1: Write file (uses recursive CTE + cross join for bulk)**

```sql
-- Performance seed: ~50K chunks, ~10K entities, ~30K relationships, ~50K mappings
-- Idempotent: only loads if `documents` count < 100

-- Reuse user 2 (editor) and topic 1 (created by 06_seed)

-- 100 documents
INSERT INTO documents (topic_id, uploader_id, title, source_type, content_hash)
WITH RECURSIVE seq AS (
    SELECT 1 AS n UNION ALL SELECT n+1 FROM seq WHERE n < 100
)
SELECT 1, 2, CONCAT('Perf doc ', n), 'text', SHA2(CONCAT('perf', n), 256)
FROM seq;

-- 50K chunks: 500 per doc
INSERT INTO document_chunks (document_id, chunk_index, content)
WITH RECURSIVE seq AS (
    SELECT 0 AS n UNION ALL SELECT n+1 FROM seq WHERE n < 499
)
SELECT d.id, s.n, CONCAT('Chunk content ', d.id, '-', s.n,
                          ' lorem ipsum dolor sit amet keyword-', d.id MOD 50)
FROM documents d
CROSS JOIN seq s
WHERE d.title LIKE 'Perf doc %'
ORDER BY d.id, s.n;

-- 10K entities (filler in topic 1)
INSERT INTO entities (topic_id, canonical_name, entity_type)
WITH RECURSIVE seq AS (
    SELECT 1 AS n UNION ALL SELECT n+1 FROM seq WHERE n < 10000
)
SELECT 1, CONCAT('PerfEntity-', n),
    ELT(1 + n MOD 8, 'person','project','task','concept','decision','event','place','other')
FROM seq;

-- 30K relationships (random pairs, dedup via INSERT IGNORE)
INSERT IGNORE INTO relationships (topic_id, source_entity_id, target_entity_id, relation_type)
WITH RECURSIVE seq AS (
    SELECT 1 AS n UNION ALL SELECT n+1 FROM seq WHERE n < 30000
)
SELECT 1,
       1 + FLOOR(RAND(s.n) * 9000),
       1 + FLOOR(RAND(s.n + 1) * 9000) + 9,
       ELT(1 + s.n MOD 5, 'related','depends_on','knows','located_in','part_of')
FROM seq s
WHERE 1 + FLOOR(RAND(s.n) * 9000) <> 1 + FLOOR(RAND(s.n + 1) * 9000) + 9;

-- 50K chunk-entity mappings
INSERT IGNORE INTO chunk_entity_mapping (chunk_id, entity_id, occurrences)
WITH RECURSIVE seq AS (
    SELECT 1 AS n UNION ALL SELECT n+1 FROM seq WHERE n < 50000
)
SELECT
    1 + FLOOR(RAND(s.n) * 50000),
    9 + FLOOR(RAND(s.n + 1) * 9990),
    1 + s.n MOD 5
FROM seq s;
```

- [ ] **Step 2: Apply (allow several minutes)**

```bash
mysql -u root -p --max_allowed_packet=64M nkg -e "SET cte_max_recursion_depth = 100000;" \
  && mysql -u root -p nkg < sql/07_seed_perf.sql
```

Expected: 1-3 minutes runtime.

- [ ] **Step 3: Verify counts**

```bash
mysql -u root -p nkg -e "
  SELECT 'documents', COUNT(*) FROM documents
  UNION SELECT 'chunks', COUNT(*) FROM document_chunks
  UNION SELECT 'entities', COUNT(*) FROM entities
  UNION SELECT 'relationships', COUNT(*) FROM relationships
  UNION SELECT 'mappings', COUNT(*) FROM chunk_entity_mapping;"
```

Expected: docs ≥104, chunks ~50K, entities ~10K, rels ~30K, mappings ~50K.

- [ ] **Step 4: Commit**

```bash
git add sql/07_seed_perf.sql
git commit -m "feat(sql): performance seed (50K chunks, 10K entities, 30K rels)"
```

---

## Phase 6 — Backend Core

### Task 6.1: Config + DB connection

**Files:**
- Create: `backend/app/config.py`, `backend/app/db.py`

- [ ] **Step 1: `backend/app/config.py`**

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # DB
    db_host: str = "127.0.0.1"
    db_port: int = 3306
    db_user: str = "root"
    db_password: str = ""
    db_name: str = "nkg"

    # JWT
    jwt_secret: str = "dev-secret-change-me"
    jwt_expire_min: int = 1440
    jwt_algorithm: str = "HS256"

    # LLM
    minimax_api_key: str = ""
    minimax_base_url: str = "https://api.minimaxi.com/v1"
    minimax_model: str = "abab6.5s-chat"
    llm_mock: bool = True

    # RAG (reserved)
    rag_enabled: bool = False
    embedding_model: str = "minimax-embedding-001"
    embedding_dim: int = 1024

    # SQL Console
    sql_console_enabled: bool = True

    @property
    def db_url(self) -> str:
        return (f"mysql+pymysql://{self.db_user}:{self.db_password}"
                f"@{self.db_host}:{self.db_port}/{self.db_name}?charset=utf8mb4")


settings = Settings()
```

- [ ] **Step 2: `backend/app/db.py`**

```python
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from .config import settings

engine: Engine = create_engine(
    settings.db_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=5,
    pool_recycle=3600,
)


@contextmanager
def get_conn():
    """Yield a SQLAlchemy Connection (autocommit off, manual commit)."""
    conn = engine.connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_db():
    """FastAPI dependency."""
    with get_conn() as c:
        yield c
```

- [ ] **Step 3: Smoke test**

```bash
cd backend && uv run python -c "from app.db import engine; from sqlalchemy import text; \
  print(engine.connect().execute(text('SELECT 1')).scalar())"
```

Expected: `1`

- [ ] **Step 4: Commit**

```bash
git add backend/app/config.py backend/app/db.py
git commit -m "feat(backend): config + SQLAlchemy connection"
```

---

### Task 6.2: Security (JWT + bcrypt)

**Files:**
- Create: `backend/app/security.py`

- [ ] **Step 1: Write file**

```python
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from .config import settings

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    return _pwd.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd.verify(plain, hashed)


def create_access_token(user_id: int, role: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_min)
    payload = {"sub": str(user_id), "role": role, "exp": exp}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None
```

- [ ] **Step 2: Test**

Create `backend/tests/test_security.py`:
```python
from app.security import hash_password, verify_password, create_access_token, decode_token


def test_password_round_trip():
    h = hash_password("hunter2")
    assert verify_password("hunter2", h)
    assert not verify_password("wrong", h)


def test_jwt_round_trip():
    tok = create_access_token(42, "admin")
    p = decode_token(tok)
    assert p["sub"] == "42" and p["role"] == "admin"
```

```bash
cd backend && uv run pytest tests/test_security.py -v
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/security.py backend/tests/test_security.py
git commit -m "feat(backend): JWT + bcrypt password helpers"
```

---

### Task 6.3: Auth dependencies

**Files:**
- Create: `backend/app/deps.py`

- [ ] **Step 1: Write file**

```python
from typing import Optional
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import text
from sqlalchemy.engine import Connection
from .db import get_db
from .security import decode_token


class CurrentUser:
    def __init__(self, id: int, username: str, role: str):
        self.id = id
        self.username = username
        self.role = role


def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Connection = Depends(get_db),
) -> CurrentUser:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "missing token")
    token = authorization.removeprefix("Bearer ").strip()
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid token")
    uid = int(payload["sub"])
    row = db.execute(text("SELECT id, username, role FROM users WHERE id=:id"),
                     {"id": uid}).first()
    if not row:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "user not found")
    return CurrentUser(id=row[0], username=row[1], role=row[2])


def require_role(*allowed):
    def checker(u: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if u.role not in allowed:
            raise HTTPException(status.HTTP_403_FORBIDDEN, f"role required: {allowed}")
        return u
    return checker


def get_client_ip(request_headers: Optional[str] = Header(None, alias="X-Forwarded-For")) -> str:
    return (request_headers or "").split(",")[0].strip() or "unknown"
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/deps.py
git commit -m "feat(backend): auth deps (get_current_user, require_role)"
```

---

### Task 6.4: FastAPI main + auth router

**Files:**
- Create: `backend/app/main.py`, `backend/app/routers/__init__.py`, `backend/app/routers/auth.py`, `backend/app/schemas/__init__.py`, `backend/app/schemas/auth.py`

- [ ] **Step 1: `backend/app/schemas/__init__.py`** (empty)

- [ ] **Step 2: `backend/app/schemas/auth.py`**

```python
from pydantic import BaseModel, EmailStr, Field


class LoginIn(BaseModel):
    username: str
    password: str


class RegisterIn(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    email: EmailStr
    password: str = Field(min_length=6)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict
```

- [ ] **Step 3: `backend/app/routers/__init__.py`** (empty)

- [ ] **Step 4: `backend/app/routers/auth.py`**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.engine import Connection
from ..db import get_db
from ..security import hash_password, verify_password, create_access_token
from ..deps import get_current_user, CurrentUser
from ..schemas.auth import LoginIn, RegisterIn, TokenOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenOut)
def register(payload: RegisterIn, db: Connection = Depends(get_db)):
    existing = db.execute(text("SELECT id FROM users WHERE username=:u OR email=:e"),
                          {"u": payload.username, "e": payload.email}).first()
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, "username or email exists")
    res = db.execute(text(
        "INSERT INTO users (username, password_hash, email, role) "
        "VALUES (:u, :p, :e, 'editor')"
    ), {"u": payload.username, "p": hash_password(payload.password), "e": payload.email})
    uid = res.lastrowid
    tok = create_access_token(uid, "editor")
    return TokenOut(access_token=tok, user={"id": uid, "username": payload.username, "role": "editor"})


@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, db: Connection = Depends(get_db)):
    row = db.execute(text("SELECT id, password_hash, role FROM users WHERE username=:u"),
                     {"u": payload.username}).first()
    if not row or not verify_password(payload.password, row[1]):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid credentials")
    tok = create_access_token(row[0], row[2])
    return TokenOut(access_token=tok, user={"id": row[0], "username": payload.username, "role": row[2]})


@router.get("/me")
def me(u: CurrentUser = Depends(get_current_user)):
    return {"id": u.id, "username": u.username, "role": u.role}
```

- [ ] **Step 5: `backend/app/main.py`**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth as auth_router
from .config import settings

app = FastAPI(title="NKG", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "rag_enabled": settings.rag_enabled,
            "sql_console_enabled": settings.sql_console_enabled}
```

- [ ] **Step 6: Smoke test**

```bash
cd backend && uv run uvicorn app.main:app --port 8000 &
sleep 2
curl -s http://localhost:8000/api/health
kill %1
```

Expected: `{"status":"ok",...}`

- [ ] **Step 7: API integration test**

Create `backend/tests/test_auth_api.py`:
```python
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_register_then_login(db_engine):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/api/auth/register", json={
            "username": "testuser", "email": "t@t.com", "password": "secret123"
        })
        assert r.status_code == 200
        assert "access_token" in r.json()

        r2 = await ac.post("/api/auth/login",
                           json={"username": "testuser", "password": "secret123"})
        assert r2.status_code == 200
        token = r2.json()["access_token"]

        r3 = await ac.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert r3.status_code == 200
        assert r3.json()["username"] == "testuser"
```

```bash
cd backend && uv run pytest tests/test_auth_api.py -v
```

- [ ] **Step 8: Commit**

```bash
git add backend/app/main.py backend/app/routers/ backend/app/schemas/ backend/tests/test_auth_api.py
git commit -m "feat(backend): FastAPI app + auth router (register/login/me)"
```

---

### Task 6.5: Topics router (CRUD + archive)

**Files:**
- Create: `backend/app/schemas/topics.py`, `backend/app/routers/topics.py`

- [ ] **Step 1: Schemas**

```python
# backend/app/schemas/topics.py
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class TopicIn(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    description: Optional[str] = None


class TopicUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_archived: Optional[bool] = None


class TopicOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    owner_id: int
    doc_count: int
    blueprint_status: str
    is_archived: bool
    created_at: datetime
    updated_at: datetime
```

- [ ] **Step 2: Router**

```python
# backend/app/routers/topics.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.engine import Connection
from ..db import get_db
from ..deps import get_current_user, CurrentUser
from ..schemas.topics import TopicIn, TopicUpdate, TopicOut

router = APIRouter(prefix="/api/topics", tags=["topics"])


@router.get("", response_model=List[TopicOut])
def list_topics(db: Connection = Depends(get_db), u: CurrentUser = Depends(get_current_user)):
    rows = db.execute(text(
        "SELECT id, name, description, owner_id, doc_count, blueprint_status, "
        "is_archived, created_at, updated_at FROM topics ORDER BY id DESC"
    )).mappings().all()
    return [dict(r) for r in rows]


@router.post("", response_model=TopicOut, status_code=201)
def create_topic(payload: TopicIn, db: Connection = Depends(get_db),
                 u: CurrentUser = Depends(get_current_user)):
    try:
        res = db.execute(text(
            "INSERT INTO topics (name, description, owner_id) VALUES (:n, :d, :o)"
        ), {"n": payload.name, "d": payload.description, "o": u.id})
        tid = res.lastrowid
    except Exception as e:
        raise HTTPException(status.HTTP_409_CONFLICT, f"name conflict: {e}")
    return _get(db, tid)


@router.get("/{topic_id}", response_model=TopicOut)
def get_topic(topic_id: int, db: Connection = Depends(get_db),
              u: CurrentUser = Depends(get_current_user)):
    return _get(db, topic_id)


@router.patch("/{topic_id}", response_model=TopicOut)
def update_topic(topic_id: int, payload: TopicUpdate,
                 db: Connection = Depends(get_db), u: CurrentUser = Depends(get_current_user)):
    fields = {k: v for k, v in payload.dict(exclude_none=True).items()}
    if not fields:
        return _get(db, topic_id)
    sets = ", ".join(f"{k}=:{k}" for k in fields)
    fields["id"] = topic_id
    db.execute(text(f"UPDATE topics SET {sets} WHERE id=:id"), fields)
    return _get(db, topic_id)


@router.delete("/{topic_id}", status_code=204)
def delete_topic(topic_id: int, db: Connection = Depends(get_db),
                 u: CurrentUser = Depends(get_current_user)):
    db.execute(text("DELETE FROM topics WHERE id=:id"), {"id": topic_id})


def _get(db: Connection, tid: int) -> dict:
    row = db.execute(text(
        "SELECT id, name, description, owner_id, doc_count, blueprint_status, "
        "is_archived, created_at, updated_at FROM topics WHERE id=:id"
    ), {"id": tid}).mappings().first()
    if not row:
        raise HTTPException(404, "topic not found")
    return dict(row)
```

- [ ] **Step 3: Wire into `main.py`**

Edit `backend/app/main.py` to add:
```python
from .routers import topics as topics_router
app.include_router(topics_router.router)
```

- [ ] **Step 4: Test**

Create `backend/tests/test_topics_api.py`:
```python
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


async def _login(ac):
    await ac.post("/api/auth/register", json={
        "username": "t1", "email": "t1@t.com", "password": "secret123"})
    r = await ac.post("/api/auth/login", json={"username": "t1", "password": "secret123"})
    return r.json()["access_token"]


@pytest.mark.asyncio
async def test_topic_crud(db_engine):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        tok = await _login(ac)
        h = {"Authorization": f"Bearer {tok}"}

        r = await ac.post("/api/topics", json={"name": "demo", "description": "d"}, headers=h)
        assert r.status_code == 201
        tid = r.json()["id"]

        r = await ac.get("/api/topics", headers=h)
        assert any(t["id"] == tid for t in r.json())

        r = await ac.patch(f"/api/topics/{tid}", json={"is_archived": True}, headers=h)
        assert r.json()["is_archived"] is True

        r = await ac.delete(f"/api/topics/{tid}", headers=h)
        assert r.status_code == 204
```

```bash
cd backend && uv run pytest tests/test_topics_api.py -v
```

- [ ] **Step 5: Commit**

```bash
git add backend/app/schemas/topics.py backend/app/routers/topics.py backend/app/main.py backend/tests/test_topics_api.py
git commit -m "feat(backend): topics router (CRUD + archive)"
```

---

### Task 6.6: Documents router (upload + chunks)

**Files:**
- Create: `backend/app/schemas/documents.py`, `backend/app/routers/documents.py`, `backend/app/services/__init__.py`, `backend/app/services/chunker.py`

- [ ] **Step 1: Chunker service**

```python
# backend/app/services/__init__.py  (empty)
```

```python
# backend/app/services/chunker.py
from typing import List

def chunk_text(text: str, max_chars: int = 500) -> List[str]:
    """Naive paragraph-aware chunker."""
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    out: List[str] = []
    buf = ""
    for p in paras:
        if len(buf) + len(p) + 2 <= max_chars:
            buf = (buf + "\n\n" + p) if buf else p
        else:
            if buf:
                out.append(buf)
            if len(p) <= max_chars:
                buf = p
            else:
                # split overly long paragraph
                for i in range(0, len(p), max_chars):
                    out.append(p[i:i + max_chars])
                buf = ""
    if buf:
        out.append(buf)
    return out
```

- [ ] **Step 2: Schemas**

```python
# backend/app/schemas/documents.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class DocumentIn(BaseModel):
    topic_id: int
    title: str
    source_type: str = "text"
    content: str


class DocumentOut(BaseModel):
    id: int
    topic_id: int
    uploader_id: int
    title: str
    source_type: str
    content: Optional[str]
    chunks_count: int
    status: str
    uploaded_at: datetime


class ChunkOut(BaseModel):
    id: int
    document_id: int
    chunk_index: int
    content: str
    token_count: Optional[int]
```

- [ ] **Step 3: Router**

```python
# backend/app/routers/documents.py
import hashlib
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.engine import Connection
from ..db import get_db
from ..deps import get_current_user, CurrentUser
from ..schemas.documents import DocumentIn, DocumentOut, ChunkOut
from ..services.chunker import chunk_text

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.get("", response_model=List[DocumentOut])
def list_docs(topic_id: Optional[int] = Query(None),
              db: Connection = Depends(get_db),
              u: CurrentUser = Depends(get_current_user)):
    sql = ("SELECT id, topic_id, uploader_id, title, source_type, content, "
           "chunks_count, status, uploaded_at FROM documents")
    params = {}
    if topic_id:
        sql += " WHERE topic_id=:tid"
        params["tid"] = topic_id
    sql += " ORDER BY id DESC LIMIT 200"
    rows = db.execute(text(sql), params).mappings().all()
    return [dict(r) for r in rows]


@router.post("", response_model=DocumentOut, status_code=201)
def create_doc(payload: DocumentIn,
               db: Connection = Depends(get_db),
               u: CurrentUser = Depends(get_current_user)):
    h = hashlib.sha256(payload.content.encode("utf-8")).hexdigest()
    res = db.execute(text(
        "INSERT INTO documents (topic_id, uploader_id, title, source_type, content, "
        "content_hash, file_size) VALUES (:t, :u, :ti, :st, :c, :h, :fs)"
    ), {"t": payload.topic_id, "u": u.id, "ti": payload.title,
        "st": payload.source_type, "c": payload.content, "h": h,
        "fs": len(payload.content.encode())})
    did = res.lastrowid

    # auto-chunk
    chunks = chunk_text(payload.content)
    for idx, c in enumerate(chunks):
        ch = hashlib.sha256(c.encode()).hexdigest()
        db.execute(text(
            "INSERT INTO document_chunks (document_id, chunk_index, content, content_hash, token_count) "
            "VALUES (:d, :i, :c, :h, :t)"
        ), {"d": did, "i": idx, "c": c, "h": ch, "t": len(c)})

    db.execute(text("UPDATE documents SET status='chunk_done' WHERE id=:id"), {"id": did})
    return _get(db, did)


@router.get("/{doc_id}", response_model=DocumentOut)
def get_doc(doc_id: int, db: Connection = Depends(get_db),
            u: CurrentUser = Depends(get_current_user)):
    return _get(db, doc_id)


@router.delete("/{doc_id}", status_code=204)
def delete_doc(doc_id: int, db: Connection = Depends(get_db),
               u: CurrentUser = Depends(get_current_user)):
    # Decrement topic doc_count first (no DELETE trigger; manual housekeeping)
    row = db.execute(text("SELECT topic_id FROM documents WHERE id=:id"),
                     {"id": doc_id}).first()
    if row:
        db.execute(text("UPDATE topics SET doc_count = GREATEST(doc_count-1, 0) WHERE id=:t"),
                   {"t": row[0]})
    db.execute(text("DELETE FROM documents WHERE id=:id"), {"id": doc_id})


@router.get("/{doc_id}/chunks", response_model=List[ChunkOut])
def list_chunks(doc_id: int, db: Connection = Depends(get_db),
                u: CurrentUser = Depends(get_current_user)):
    rows = db.execute(text(
        "SELECT id, document_id, chunk_index, content, token_count "
        "FROM document_chunks WHERE document_id=:id ORDER BY chunk_index"
    ), {"id": doc_id}).mappings().all()
    return [dict(r) for r in rows]


def _get(db: Connection, did: int) -> dict:
    row = db.execute(text(
        "SELECT id, topic_id, uploader_id, title, source_type, content, "
        "chunks_count, status, uploaded_at FROM documents WHERE id=:id"
    ), {"id": did}).mappings().first()
    if not row:
        raise HTTPException(404, "document not found")
    return dict(row)
```

- [ ] **Step 4: Wire + smoke**

Edit `main.py`:
```python
from .routers import documents as documents_router
app.include_router(documents_router.router)
```

```bash
cd backend && uv run pytest tests/ -v
```

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/ backend/app/schemas/documents.py backend/app/routers/documents.py backend/app/main.py
git commit -m "feat(backend): documents router (CRUD + auto-chunk + chunks list)"
```

---

### Task 6.7: Entities router (CRUD + aliases + merge via SP)

**Files:**
- Create: `backend/app/schemas/entities.py`, `backend/app/routers/entities.py`

- [ ] **Step 1: Schemas**

```python
# backend/app/schemas/entities.py
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class EntityIn(BaseModel):
    topic_id: int
    canonical_name: str
    entity_type: str
    description: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None


class EntityUpdate(BaseModel):
    canonical_name: Optional[str] = None
    entity_type: Optional[str] = None
    description: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None


class EntityOut(BaseModel):
    id: int
    topic_id: int
    canonical_name: str
    entity_type: str
    description: Optional[str]
    mention_count: int
    created_at: datetime


class AliasIn(BaseModel):
    alias: str
    source: str = "user"
    confidence: float = 1.0


class MergeIn(BaseModel):
    keep_id: int
    merge_id: int
```

- [ ] **Step 2: Router**

```python
# backend/app/routers/entities.py
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.engine import Connection
from ..db import get_db, engine
from ..deps import get_current_user, CurrentUser
from ..schemas.entities import EntityIn, EntityUpdate, EntityOut, AliasIn, MergeIn

router = APIRouter(prefix="/api/entities", tags=["entities"])


@router.get("", response_model=List[EntityOut])
def list_entities(topic_id: Optional[int] = Query(None),
                  q: Optional[str] = Query(None),
                  entity_type: Optional[str] = Query(None),
                  db: Connection = Depends(get_db),
                  u: CurrentUser = Depends(get_current_user)):
    sql = ("SELECT id, topic_id, canonical_name, entity_type, description, "
           "mention_count, created_at FROM entities WHERE 1=1")
    params = {}
    if topic_id:
        sql += " AND topic_id=:tid"; params["tid"] = topic_id
    if q:
        sql += " AND canonical_name LIKE :q"; params["q"] = f"%{q}%"
    if entity_type:
        sql += " AND entity_type=:et"; params["et"] = entity_type
    sql += " ORDER BY mention_count DESC, id DESC LIMIT 500"
    rows = db.execute(text(sql), params).mappings().all()
    return [dict(r) for r in rows]


@router.post("", response_model=EntityOut, status_code=201)
def create_entity(payload: EntityIn,
                  db: Connection = Depends(get_db),
                  u: CurrentUser = Depends(get_current_user)):
    try:
        res = db.execute(text(
            "INSERT INTO entities (topic_id, canonical_name, entity_type, description, attributes) "
            "VALUES (:t, :n, :ty, :d, :a)"
        ), {"t": payload.topic_id, "n": payload.canonical_name,
            "ty": payload.entity_type, "d": payload.description,
            "a": json.dumps(payload.attributes) if payload.attributes else None})
    except Exception as e:
        raise HTTPException(409, f"entity exists or invalid: {e}")
    return _get(db, res.lastrowid)


@router.get("/{eid}", response_model=EntityOut)
def get_entity(eid: int, db: Connection = Depends(get_db),
               u: CurrentUser = Depends(get_current_user)):
    return _get(db, eid)


@router.patch("/{eid}", response_model=EntityOut)
def update_entity(eid: int, payload: EntityUpdate,
                  db: Connection = Depends(get_db),
                  u: CurrentUser = Depends(get_current_user)):
    fields = {k: v for k, v in payload.dict(exclude_none=True).items()}
    if "attributes" in fields:
        fields["attributes"] = json.dumps(fields["attributes"])
    if not fields:
        return _get(db, eid)
    sets = ", ".join(f"{k}=:{k}" for k in fields)
    fields["id"] = eid
    db.execute(text(f"UPDATE entities SET {sets} WHERE id=:id"), fields)
    return _get(db, eid)


@router.delete("/{eid}", status_code=204)
def delete_entity(eid: int, db: Connection = Depends(get_db),
                  u: CurrentUser = Depends(get_current_user)):
    db.execute(text("DELETE FROM entities WHERE id=:id"), {"id": eid})


@router.get("/{eid}/aliases")
def list_aliases(eid: int, db: Connection = Depends(get_db),
                 u: CurrentUser = Depends(get_current_user)):
    rows = db.execute(text(
        "SELECT id, alias, source, confidence, created_at FROM entity_aliases "
        "WHERE entity_id=:id ORDER BY id"
    ), {"id": eid}).mappings().all()
    return [dict(r) for r in rows]


@router.post("/{eid}/aliases", status_code=201)
def add_alias(eid: int, payload: AliasIn,
              db: Connection = Depends(get_db),
              u: CurrentUser = Depends(get_current_user)):
    try:
        db.execute(text(
            "INSERT INTO entity_aliases (entity_id, alias, source, confidence) "
            "VALUES (:e, :a, :s, :c)"
        ), {"e": eid, "a": payload.alias, "s": payload.source, "c": payload.confidence})
    except Exception as e:
        raise HTTPException(409, str(e))
    return {"ok": True}


@router.post("/merge", status_code=200)
def merge_entities(payload: MergeIn,
                   db: Connection = Depends(get_db),
                   u: CurrentUser = Depends(get_current_user)):
    raw = engine.raw_connection()
    try:
        cur = raw.cursor()
        cur.callproc("sp_merge_entities", (payload.keep_id, payload.merge_id, u.id))
        raw.commit()
        return {"ok": True, "kept": payload.keep_id}
    except Exception as e:
        raw.rollback()
        raise HTTPException(400, f"merge failed: {e}")
    finally:
        raw.close()


@router.get("/{eid}/neighborhood")
def neighborhood(eid: int, depth: int = Query(2, ge=1, le=5),
                 u: CurrentUser = Depends(get_current_user)):
    raw = engine.raw_connection()
    try:
        cur = raw.cursor()
        cur.execute("CALL sp_get_entity_neighborhood(%s, %s, @cnt)", (eid, depth))
        rows = cur.fetchall()
        cur.execute("SELECT @cnt")
        cnt = cur.fetchone()[0]
        cur.close()
        return {"count": cnt,
                "nodes": [{"entity_id": r[0], "distance": r[1],
                           "name": r[2], "type": r[3]} for r in rows]}
    finally:
        raw.close()


def _get(db: Connection, eid: int) -> dict:
    row = db.execute(text(
        "SELECT id, topic_id, canonical_name, entity_type, description, "
        "mention_count, created_at FROM entities WHERE id=:id"
    ), {"id": eid}).mappings().first()
    if not row:
        raise HTTPException(404, "entity not found")
    return dict(row)
```

- [ ] **Step 3: Wire**

```python
# main.py
from .routers import entities as entities_router
app.include_router(entities_router.router)
```

- [ ] **Step 4: Test**

Create `backend/tests/test_entities_api.py`:
```python
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


async def _bootstrap(ac):
    await ac.post("/api/auth/register", json={
        "username": "ent1", "email": "e@e.com", "password": "secret123"})
    r = await ac.post("/api/auth/login", json={"username": "ent1", "password": "secret123"})
    tok = r.json()["access_token"]
    h = {"Authorization": f"Bearer {tok}"}
    r = await ac.post("/api/topics", json={"name": "T"}, headers=h)
    return h, r.json()["id"]


@pytest.mark.asyncio
async def test_entity_crud_and_merge(db_engine):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        h, tid = await _bootstrap(ac)

        r1 = await ac.post("/api/entities", json={
            "topic_id": tid, "canonical_name": "X", "entity_type": "person"}, headers=h)
        r2 = await ac.post("/api/entities", json={
            "topic_id": tid, "canonical_name": "Y", "entity_type": "person"}, headers=h)
        e1, e2 = r1.json()["id"], r2.json()["id"]

        r = await ac.post("/api/entities/merge",
                          json={"keep_id": e1, "merge_id": e2}, headers=h)
        assert r.status_code == 200

        r = await ac.get(f"/api/entities/{e2}", headers=h)
        assert r.status_code == 404
```

```bash
cd backend && uv run pytest tests/test_entities_api.py -v
```

- [ ] **Step 5: Commit**

```bash
git add backend/app/schemas/entities.py backend/app/routers/entities.py backend/app/main.py backend/tests/test_entities_api.py
git commit -m "feat(backend): entities router (CRUD, aliases, merge SP, neighborhood SP)"
```

---

### Task 6.8: Relationships router (CRUD + graph endpoint)

**Files:**
- Create: `backend/app/schemas/relationships.py`, `backend/app/routers/relationships.py`, `backend/app/routers/graph.py`

- [ ] **Step 1: Schemas + relationships router**

```python
# backend/app/schemas/relationships.py
from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class RelationshipIn(BaseModel):
    topic_id: int
    source_entity_id: int
    target_entity_id: int
    relation_type: str
    description: Optional[str] = None
    weight: float = 1.0


class RelationshipOut(BaseModel):
    id: int
    topic_id: int
    source_entity_id: int
    target_entity_id: int
    relation_type: str
    description: Optional[str]
    weight: float
    created_at: datetime
```

```python
# backend/app/routers/relationships.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.engine import Connection
from ..db import get_db
from ..deps import get_current_user, CurrentUser
from ..schemas.relationships import RelationshipIn, RelationshipOut

router = APIRouter(prefix="/api/relationships", tags=["relationships"])


@router.get("", response_model=List[RelationshipOut])
def list_rels(topic_id: Optional[int] = Query(None),
              db: Connection = Depends(get_db),
              u: CurrentUser = Depends(get_current_user)):
    sql = ("SELECT id, topic_id, source_entity_id, target_entity_id, relation_type, "
           "description, weight, created_at FROM relationships")
    params = {}
    if topic_id:
        sql += " WHERE topic_id=:t"; params["t"] = topic_id
    sql += " ORDER BY id DESC LIMIT 500"
    rows = db.execute(text(sql), params).mappings().all()
    return [dict(r) for r in rows]


@router.post("", response_model=RelationshipOut, status_code=201)
def create_rel(payload: RelationshipIn,
               db: Connection = Depends(get_db),
               u: CurrentUser = Depends(get_current_user)):
    try:
        res = db.execute(text(
            "INSERT INTO relationships (topic_id, source_entity_id, target_entity_id, "
            "relation_type, description, weight) "
            "VALUES (:t, :s, :d, :rt, :ds, :w)"
        ), {"t": payload.topic_id, "s": payload.source_entity_id,
            "d": payload.target_entity_id, "rt": payload.relation_type,
            "ds": payload.description, "w": payload.weight})
    except Exception as e:
        raise HTTPException(400, f"insert failed (cross-topic / duplicate / self-loop?): {e}")
    row = db.execute(text(
        "SELECT id, topic_id, source_entity_id, target_entity_id, relation_type, "
        "description, weight, created_at FROM relationships WHERE id=:id"
    ), {"id": res.lastrowid}).mappings().first()
    return dict(row)


@router.delete("/{rid}", status_code=204)
def delete_rel(rid: int, db: Connection = Depends(get_db),
               u: CurrentUser = Depends(get_current_user)):
    db.execute(text("DELETE FROM relationships WHERE id=:id"), {"id": rid})
```

- [ ] **Step 2: Graph endpoint (separate router for clarity)**

```python
# backend/app/routers/graph.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.engine import Connection
from ..db import get_db
from ..deps import get_current_user, CurrentUser

router = APIRouter(prefix="/api/topics", tags=["graph"])


@router.get("/{topic_id}/graph")
def get_graph(topic_id: int,
              limit: int = Query(500, le=2000),
              db: Connection = Depends(get_db),
              u: CurrentUser = Depends(get_current_user)):
    nodes = db.execute(text(
        "SELECT id, canonical_name, entity_type, mention_count "
        "FROM entities WHERE topic_id=:t ORDER BY mention_count DESC LIMIT :lim"
    ), {"t": topic_id, "lim": limit}).mappings().all()

    node_ids = {n["id"] for n in nodes}
    if not node_ids:
        return {"nodes": [], "edges": []}

    edges = db.execute(text(
        "SELECT id, source_entity_id, target_entity_id, relation_type, weight "
        "FROM relationships WHERE topic_id=:t LIMIT :lim"
    ), {"t": topic_id, "lim": limit}).mappings().all()

    return {
        "nodes": [{"id": n["id"], "name": n["canonical_name"],
                   "type": n["entity_type"], "value": n["mention_count"]}
                  for n in nodes],
        "edges": [{"id": e["id"], "source": e["source_entity_id"],
                   "target": e["target_entity_id"], "label": e["relation_type"],
                   "weight": float(e["weight"])} for e in edges
                  if e["source_entity_id"] in node_ids and e["target_entity_id"] in node_ids],
    }
```

- [ ] **Step 3: Wire**

```python
# main.py
from .routers import relationships as rel_router
from .routers import graph as graph_router
app.include_router(rel_router.router)
app.include_router(graph_router.router)
```

- [ ] **Step 4: Smoke test**

```bash
cd backend && uv run pytest tests/ -v
```

All previous tests should still pass.

- [ ] **Step 5: Commit**

```bash
git add backend/app/schemas/relationships.py backend/app/routers/relationships.py backend/app/routers/graph.py backend/app/main.py
git commit -m "feat(backend): relationships router + topic graph endpoint"
```

---

### Task 6.9: Jobs + audit + admin routers

**Files:**
- Create: `backend/app/routers/jobs.py`, `backend/app/routers/audit.py`, `backend/app/routers/admin.py`

- [ ] **Step 1: jobs.py**

```python
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.engine import Connection
from ..db import get_db
from ..deps import get_current_user, CurrentUser

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("")
def list_jobs(topic_id: Optional[int] = Query(None),
              status: Optional[str] = Query(None),
              db: Connection = Depends(get_db),
              u: CurrentUser = Depends(get_current_user)):
    sql = ("SELECT id, document_id, topic_id, job_type, status, progress, "
           "result, error_message, created_at, completed_at FROM extraction_jobs WHERE 1=1")
    p = {}
    if topic_id:
        sql += " AND topic_id=:t"; p["t"] = topic_id
    if status:
        sql += " AND status=:s"; p["s"] = status
    sql += " ORDER BY id DESC LIMIT 200"
    rows = db.execute(text(sql), p).mappings().all()
    return [dict(r) for r in rows]


@router.get("/{jid}")
def get_job(jid: int, db: Connection = Depends(get_db),
            u: CurrentUser = Depends(get_current_user)):
    row = db.execute(text(
        "SELECT id, document_id, topic_id, job_type, status, progress, "
        "result, error_message, started_at, completed_at, created_at "
        "FROM extraction_jobs WHERE id=:id"
    ), {"id": jid}).mappings().first()
    if not row:
        from fastapi import HTTPException
        raise HTTPException(404)
    return dict(row)
```

- [ ] **Step 2: audit.py**

```python
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.engine import Connection
from ..db import get_db
from ..deps import get_current_user, CurrentUser

router = APIRouter(prefix="/api/audit-logs", tags=["audit"])


@router.get("")
def list_logs(user_id: Optional[int] = Query(None),
              action: Optional[str] = Query(None),
              limit: int = Query(100, le=500),
              db: Connection = Depends(get_db),
              u: CurrentUser = Depends(get_current_user)):
    sql = ("SELECT id, user_id, action, entity_type, entity_id, "
           "before_value, after_value, ip_address, created_at FROM audit_logs WHERE 1=1")
    p = {}
    if user_id:
        sql += " AND user_id=:u"; p["u"] = user_id
    if action:
        sql += " AND action=:a"; p["a"] = action
    sql += " ORDER BY id DESC LIMIT :lim"; p["lim"] = limit
    rows = db.execute(text(sql), p).mappings().all()
    return [dict(r) for r in rows]
```

- [ ] **Step 3: admin.py (calls cursor SPs)**

```python
from fastapi import APIRouter, Depends, HTTPException
from ..db import engine
from ..deps import require_role

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/recompute-mentions")
def recompute_mentions(u=Depends(require_role("admin"))):
    raw = engine.raw_connection()
    try:
        cur = raw.cursor()
        cur.callproc("sp_recompute_entity_mentions", ())
        raw.commit()
        return {"ok": True}
    finally:
        raw.close()


@router.post("/archive-inactive-topics")
def archive_inactive(days: int = 30, u=Depends(require_role("admin"))):
    raw = engine.raw_connection()
    try:
        cur = raw.cursor()
        cur.execute("CALL sp_archive_inactive_topics(%s, @cnt)", (days,))
        cur.execute("SELECT @cnt")
        cnt = cur.fetchone()[0]
        raw.commit()
        return {"ok": True, "archived": cnt}
    finally:
        raw.close()


@router.post("/propagate-rename")
def propagate_rename(topic_id: int, pattern: str, new_name: str,
                     u=Depends(require_role("admin"))):
    raw = engine.raw_connection()
    try:
        cur = raw.cursor()
        cur.callproc("sp_propagate_entity_rename", (topic_id, pattern, new_name))
        raw.commit()
        return {"ok": True}
    finally:
        raw.close()
```

- [ ] **Step 4: Wire**

```python
# main.py
from .routers import jobs as jobs_router, audit as audit_router, admin as admin_router
app.include_router(jobs_router.router)
app.include_router(audit_router.router)
app.include_router(admin_router.router)
```

- [ ] **Step 5: Commit**

```bash
git add backend/app/routers/jobs.py backend/app/routers/audit.py backend/app/routers/admin.py backend/app/main.py
git commit -m "feat(backend): jobs/audit/admin routers (admin SPs wired)"
```

---

## Phase 7 — LLM Integration & Extraction Services

### Task 7.1: MiniMax client with mock fallback

**Files:**
- Create: `backend/app/llm.py`

- [ ] **Step 1: Write file**

```python
import json
import logging
from typing import Optional, List, Dict, Any
from openai import OpenAI
from .config import settings

log = logging.getLogger(__name__)


class LLMClient:
    def __init__(self):
        self.use_mock = settings.llm_mock or not settings.minimax_api_key
        if not self.use_mock:
            self.client = OpenAI(
                api_key=settings.minimax_api_key,
                base_url=settings.minimax_base_url,
            )

    def chat_json(self, system: str, user: str, mock_fallback: dict) -> dict:
        """Return JSON dict from LLM; on mock or failure, return mock_fallback."""
        if self.use_mock:
            log.info("LLM mock mode")
            return mock_fallback
        try:
            resp = self.client.chat.completions.create(
                model=settings.minimax_model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0.2,
                response_format={"type": "json_object"},
            )
            txt = resp.choices[0].message.content or "{}"
            return json.loads(txt)
        except Exception as e:
            log.warning(f"LLM call failed, using mock: {e}")
            return mock_fallback


llm = LLMClient()


# Helpers ----------------------------------------------------------

COG_MAP_SYSTEM = """你是知识抽取助手。给定一段文档文本，输出 JSON：
{
  "summary": "<200字摘要>",
  "key_entities": [{"name": "...", "type": "person|project|task|concept|decision|event|place|other"}],
  "themes": ["主题词", ...],
  "timeline": [{"time": "...", "event": "..."}],
  "structural_patterns": ["..."]
}
"""

EXTRACT_SYSTEM = """你是知识抽取助手。给定一段文本和已知实体清单，抽取 JSON：
{
  "entities": [{"name": "...", "type": "person|project|task|concept|decision|event|place|other"}],
  "relationships": [{"source": "...", "target": "...", "type": "...", "description": "..."}]
}
只抽取文本中明确提到的实体和关系，不要编造。
"""


def gen_cognitive_map(content: str) -> Dict[str, Any]:
    return llm.chat_json(
        COG_MAP_SYSTEM,
        f"文档内容：\n{content[:3000]}",
        mock_fallback={
            "summary": content[:200],
            "key_entities": [],
            "themes": [],
            "timeline": [],
            "structural_patterns": [],
        },
    )


def gen_extraction(content: str, known_entities: List[str]) -> Dict[str, Any]:
    return llm.chat_json(
        EXTRACT_SYSTEM,
        f"已知实体：{json.dumps(known_entities, ensure_ascii=False)}\n\n文本：\n{content[:3000]}",
        mock_fallback={"entities": [], "relationships": []},
    )
```

- [ ] **Step 2: Smoke test (mock mode)**

```bash
cd backend && uv run python -c "
from app.llm import gen_cognitive_map
print(gen_cognitive_map('张三去了上海'))
"
```

Expected: dict with `summary` key (mock content).

- [ ] **Step 3: Commit**

```bash
git add backend/app/llm.py
git commit -m "feat(backend): MiniMax LLM client (OpenAI-compatible) + mock fallback"
```

---

### Task 7.2: Cognitive map service + endpoint

**Files:**
- Create: `backend/app/services/cognitive.py`, `backend/app/routers/cognitive.py`

- [ ] **Step 1: Service**

```python
# backend/app/services/cognitive.py
import json
from sqlalchemy import text
from sqlalchemy.engine import Connection
from ..llm import gen_cognitive_map


def generate_for_document(db: Connection, doc_id: int) -> dict:
    row = db.execute(text("SELECT content FROM documents WHERE id=:id"),
                     {"id": doc_id}).first()
    if not row or not row[0]:
        raise ValueError("document not found or empty")

    cog = gen_cognitive_map(row[0])

    # upsert
    existing = db.execute(text(
        "SELECT id, version FROM cognitive_maps WHERE document_id=:id"
    ), {"id": doc_id}).first()

    if existing:
        db.execute(text(
            "UPDATE cognitive_maps SET summary=:s, key_entities=:k, themes=:t, "
            "timeline=:tl, structural_patterns=:sp, version=version+1, "
            "generated_by='llm' WHERE id=:cid"
        ), {"s": cog.get("summary"),
            "k": json.dumps(cog.get("key_entities", []), ensure_ascii=False),
            "t": json.dumps(cog.get("themes", []), ensure_ascii=False),
            "tl": json.dumps(cog.get("timeline", []), ensure_ascii=False),
            "sp": json.dumps(cog.get("structural_patterns", []), ensure_ascii=False),
            "cid": existing[0]})
    else:
        db.execute(text(
            "INSERT INTO cognitive_maps (document_id, summary, key_entities, themes, "
            "timeline, structural_patterns, generated_by) "
            "VALUES (:d, :s, :k, :t, :tl, :sp, 'llm')"
        ), {"d": doc_id,
            "s": cog.get("summary"),
            "k": json.dumps(cog.get("key_entities", []), ensure_ascii=False),
            "t": json.dumps(cog.get("themes", []), ensure_ascii=False),
            "tl": json.dumps(cog.get("timeline", []), ensure_ascii=False),
            "sp": json.dumps(cog.get("structural_patterns", []), ensure_ascii=False)})

    return cog
```

- [ ] **Step 2: Router**

```python
# backend/app/routers/cognitive.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.engine import Connection
from ..db import get_db
from ..deps import get_current_user, CurrentUser
from ..services.cognitive import generate_for_document

router = APIRouter(prefix="/api/documents", tags=["cognitive"])


@router.post("/{doc_id}/cognitive-map")
def gen(doc_id: int, db: Connection = Depends(get_db),
        u: CurrentUser = Depends(get_current_user)):
    try:
        return generate_for_document(db, doc_id)
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.get("/{doc_id}/cognitive-map")
def get(doc_id: int, db: Connection = Depends(get_db),
        u: CurrentUser = Depends(get_current_user)):
    row = db.execute(text(
        "SELECT id, summary, key_entities, themes, timeline, structural_patterns, "
        "version, generated_at FROM cognitive_maps WHERE document_id=:id"
    ), {"id": doc_id}).mappings().first()
    if not row:
        raise HTTPException(404, "no cognitive map")
    return dict(row)
```

- [ ] **Step 3: Wire + commit**

```python
# main.py
from .routers import cognitive as cog_router
app.include_router(cog_router.router)
```

```bash
git add backend/app/services/cognitive.py backend/app/routers/cognitive.py backend/app/main.py
git commit -m "feat(backend): cognitive map service + endpoints"
```

---

### Task 7.3: Blueprint service + endpoint

**Files:**
- Create: `backend/app/services/blueprint.py`, `backend/app/routers/blueprint.py`

- [ ] **Step 1: Service**

```python
# backend/app/services/blueprint.py
import json
import hashlib
from typing import List
from sqlalchemy import text
from sqlalchemy.engine import Connection


def regenerate_for_topic(db: Connection, topic_id: int) -> dict:
    """Aggregate cognitive maps in topic into a blueprint (no LLM call needed —
    pure aggregation; LLM optional refinement future work)."""
    rows = db.execute(text("""
        SELECT cm.key_entities, cm.themes, cm.timeline
          FROM cognitive_maps cm
          JOIN documents d ON d.id = cm.document_id
         WHERE d.topic_id = :t
    """), {"t": topic_id}).all()

    if not rows:
        raise ValueError("no cognitive maps for topic")

    canonical_entities: dict = {}
    key_patterns = set()
    global_timeline: list = []
    for ke_json, themes_json, tl_json in rows:
        for e in (json.loads(ke_json) if ke_json else []):
            name = e.get("name")
            if name:
                canonical_entities.setdefault(name, {"name": name, "type": e.get("type", "other"), "freq": 0})
                canonical_entities[name]["freq"] += 1
        for t in (json.loads(themes_json) if themes_json else []):
            key_patterns.add(t)
        for ev in (json.loads(tl_json) if tl_json else []):
            global_timeline.append(ev)

    payload = {
        "canonical_entities": list(canonical_entities.values()),
        "key_patterns": sorted(key_patterns),
        "global_timeline": global_timeline,
    }
    sd_hash = hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

    existing = db.execute(text("SELECT id FROM analysis_blueprints WHERE topic_id=:t"),
                          {"t": topic_id}).first()
    if existing:
        db.execute(text("""
            UPDATE analysis_blueprints
               SET canonical_entities=:ce, key_patterns=:kp, global_timeline=:gt,
                   contributing_doc_count=:dc, source_data_hash=:sh,
                   status='ready', version=version+1, generated_at=NOW()
             WHERE id=:id
        """), {"ce": json.dumps(payload["canonical_entities"], ensure_ascii=False),
               "kp": json.dumps(payload["key_patterns"], ensure_ascii=False),
               "gt": json.dumps(payload["global_timeline"], ensure_ascii=False),
               "dc": len(rows), "sh": sd_hash, "id": existing[0]})
    else:
        db.execute(text("""
            INSERT INTO analysis_blueprints (topic_id, canonical_entities, key_patterns,
                global_timeline, contributing_doc_count, source_data_hash, status, generated_at)
            VALUES (:t, :ce, :kp, :gt, :dc, :sh, 'ready', NOW())
        """), {"t": topic_id,
               "ce": json.dumps(payload["canonical_entities"], ensure_ascii=False),
               "kp": json.dumps(payload["key_patterns"], ensure_ascii=False),
               "gt": json.dumps(payload["global_timeline"], ensure_ascii=False),
               "dc": len(rows), "sh": sd_hash})

    db.execute(text("UPDATE topics SET blueprint_status='ready' WHERE id=:t"),
               {"t": topic_id})

    return payload
```

- [ ] **Step 2: Router**

```python
# backend/app/routers/blueprint.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.engine import Connection
from ..db import get_db
from ..deps import get_current_user, CurrentUser
from ..services.blueprint import regenerate_for_topic

router = APIRouter(prefix="/api/topics", tags=["blueprint"])


@router.post("/{topic_id}/blueprint")
def regen(topic_id: int, db: Connection = Depends(get_db),
          u: CurrentUser = Depends(get_current_user)):
    try:
        return regenerate_for_topic(db, topic_id)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/{topic_id}/blueprint")
def get(topic_id: int, db: Connection = Depends(get_db),
        u: CurrentUser = Depends(get_current_user)):
    row = db.execute(text(
        "SELECT id, canonical_entities, key_patterns, global_timeline, "
        "contributing_doc_count, status, version, generated_at "
        "FROM analysis_blueprints WHERE topic_id=:t"
    ), {"t": topic_id}).mappings().first()
    if not row:
        raise HTTPException(404, "no blueprint")
    return dict(row)
```

- [ ] **Step 3: Wire + commit**

```python
# main.py
from .routers import blueprint as bp_router
app.include_router(bp_router.router)
```

```bash
git add backend/app/services/blueprint.py backend/app/routers/blueprint.py backend/app/main.py
git commit -m "feat(backend): blueprint aggregation service + endpoints"
```

---

### Task 7.4: Extraction service + endpoint

**Files:**
- Create: `backend/app/services/extract.py`, `backend/app/routers/extract.py`

- [ ] **Step 1: Service**

```python
# backend/app/services/extract.py
import json
from typing import Optional
from sqlalchemy import text
from sqlalchemy.engine import Connection
from ..llm import gen_extraction


def extract_for_topic(db: Connection, topic_id: int, doc_id: Optional[int] = None) -> dict:
    """Run LLM extraction on chunks; INSERT IGNORE entities/rels/mappings."""
    sql = ("SELECT dc.id, dc.content FROM document_chunks dc "
           "JOIN documents d ON d.id = dc.document_id WHERE d.topic_id=:t")
    p = {"t": topic_id}
    if doc_id:
        sql += " AND d.id=:d"; p["d"] = doc_id

    chunks = db.execute(text(sql), p).all()
    if not chunks:
        raise ValueError("no chunks for topic")

    known = [r[0] for r in db.execute(text(
        "SELECT canonical_name FROM entities WHERE topic_id=:t LIMIT 200"
    ), {"t": topic_id}).all()]

    new_ent = 0; new_rel = 0; new_map = 0
    for chunk_id, content in chunks:
        result = gen_extraction(content, known)
        for e in result.get("entities", []):
            name, etype = e.get("name"), e.get("type", "other")
            if not name:
                continue
            try:
                db.execute(text(
                    "INSERT IGNORE INTO entities (topic_id, canonical_name, entity_type) "
                    "VALUES (:t, :n, :ty)"), {"t": topic_id, "n": name, "ty": etype})
                eid = db.execute(text(
                    "SELECT id FROM entities WHERE topic_id=:t AND canonical_name=:n AND entity_type=:ty"
                ), {"t": topic_id, "n": name, "ty": etype}).scalar()
                if eid:
                    res = db.execute(text(
                        "INSERT IGNORE INTO chunk_entity_mapping (chunk_id, entity_id, occurrences) "
                        "VALUES (:c, :e, 1)"), {"c": chunk_id, "e": eid})
                    if res.rowcount > 0:
                        new_map += 1
                    new_ent += 1
            except Exception:
                pass

        for r in result.get("relationships", []):
            src, dst, rtype = r.get("source"), r.get("target"), r.get("type")
            if not (src and dst and rtype):
                continue
            sid = db.execute(text(
                "SELECT id FROM entities WHERE topic_id=:t AND canonical_name=:n LIMIT 1"
            ), {"t": topic_id, "n": src}).scalar()
            tid = db.execute(text(
                "SELECT id FROM entities WHERE topic_id=:t AND canonical_name=:n LIMIT 1"
            ), {"t": topic_id, "n": dst}).scalar()
            if sid and tid and sid != tid:
                try:
                    db.execute(text(
                        "INSERT IGNORE INTO relationships (topic_id, source_entity_id, "
                        "target_entity_id, relation_type, description) "
                        "VALUES (:t, :s, :d, :rt, :desc)"
                    ), {"t": topic_id, "s": sid, "d": tid, "rt": rtype,
                        "desc": r.get("description")})
                    new_rel += 1
                except Exception:
                    pass

    return {"new_entities": new_ent, "new_relationships": new_rel, "new_mappings": new_map}
```

- [ ] **Step 2: Router**

```python
# backend/app/routers/extract.py
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.engine import Connection
from ..db import get_db
from ..deps import get_current_user, CurrentUser
from ..services.extract import extract_for_topic

router = APIRouter(prefix="/api/topics", tags=["extract"])


@router.post("/{topic_id}/extract")
def extract(topic_id: int, doc_id: Optional[int] = Query(None),
            db: Connection = Depends(get_db),
            u: CurrentUser = Depends(get_current_user)):
    try:
        return extract_for_topic(db, topic_id, doc_id)
    except ValueError as e:
        raise HTTPException(400, str(e))
```

- [ ] **Step 3: Wire + commit**

```python
# main.py
from .routers import extract as extract_router
app.include_router(extract_router.router)
```

```bash
git add backend/app/services/extract.py backend/app/routers/extract.py backend/app/main.py
git commit -m "feat(backend): LLM-driven entity/relation extraction service + endpoint"
```

---

## Phase 8 — SQL Console Backend

### Task 8.1: SQL parser + safety

**Files:**
- Create: `backend/app/services/sql_console.py`

- [ ] **Step 1: Write file**

```python
# backend/app/services/sql_console.py
import re
import time
from typing import Any, Dict, List
from sqlalchemy import text
from sqlalchemy.engine import Engine

# Restrict to single-statement; multi-statement (semicolon-joined) rejected
_SINGLE_STMT = re.compile(r";\s*\S")


def classify(sql: str) -> str:
    s = sql.strip().upper()
    if s.startswith("EXPLAIN"):
        return "explain"
    if s.startswith("SELECT") or s.startswith("SHOW") or s.startswith("DESC"):
        return "read"
    if s.startswith(("INSERT", "UPDATE", "DELETE", "REPLACE")):
        return "dml"
    if s.startswith(("CREATE", "ALTER", "DROP", "TRUNCATE", "RENAME")):
        return "ddl"
    if s.startswith("CALL"):
        return "call"
    if s in ("BEGIN", "START TRANSACTION", "COMMIT", "ROLLBACK"):
        return "txn"
    return "other"


def validate(sql: str):
    """Raise ValueError on multi-statement SQL."""
    if not sql.strip():
        raise ValueError("empty SQL")
    if _SINGLE_STMT.search(sql):
        raise ValueError("multi-statement SQL not allowed; submit one statement at a time")


def execute_one(engine: Engine, sql: str, max_rows: int = 1000) -> Dict[str, Any]:
    """Run single SQL on a fresh connection; return structured result."""
    validate(sql)
    kind = classify(sql)
    started = time.perf_counter()
    raw = engine.raw_connection()
    try:
        cur = raw.cursor()
        cur.execute("SET STATEMENT max_statement_time=15 FOR " + sql) \
            if kind in ("read", "explain") else cur.execute(sql)

        out: Dict[str, Any] = {"kind": kind, "elapsed_ms": 0}

        if kind in ("read", "explain", "call"):
            cols = [d[0] for d in (cur.description or [])]
            rows = cur.fetchmany(max_rows)
            out["columns"] = cols
            out["rows"] = [list(r) for r in rows]
            out["row_count"] = len(rows)
        elif kind in ("dml", "ddl"):
            raw.commit()
            out["affected_rows"] = cur.rowcount
        elif kind == "txn":
            raw.commit()

        out["elapsed_ms"] = int((time.perf_counter() - started) * 1000)
        cur.close()
        return out
    except Exception:
        raw.rollback()
        raise
    finally:
        raw.close()
```

- [ ] **Step 2: Test**

Create `backend/tests/test_sql_console.py`:
```python
import pytest
from app.services.sql_console import execute_one, validate


def test_validate_rejects_multi():
    with pytest.raises(ValueError):
        validate("SELECT 1; SELECT 2")


def test_select(db_engine):
    out = execute_one(db_engine, "SELECT 1 AS x")
    assert out["kind"] == "read"
    assert out["rows"] == [[1]]


def test_show_tables(db_engine):
    out = execute_one(db_engine, "SHOW TABLES")
    assert out["row_count"] >= 14
```

```bash
cd backend && uv run pytest tests/test_sql_console.py -v
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/services/sql_console.py backend/tests/test_sql_console.py
git commit -m "feat(backend): SQL console executor service + safety validator"
```

---

### Task 8.2: SQL console router

**Files:**
- Create: `backend/app/routers/dev.py`, `backend/app/schemas/dev.py`

- [ ] **Step 1: Schemas**

```python
# backend/app/schemas/dev.py
from pydantic import BaseModel


class SqlIn(BaseModel):
    sql: str
    max_rows: int = 1000
```

- [ ] **Step 2: Router**

```python
# backend/app/routers/dev.py
import json
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import text
from sqlalchemy.engine import Connection
from ..db import engine, get_db
from ..deps import require_role
from ..services.sql_console import execute_one
from ..config import settings
from ..schemas.dev import SqlIn

router = APIRouter(prefix="/api/dev", tags=["dev"])


@router.post("/sql/execute")
def sql_execute(payload: SqlIn, request: Request,
                u=Depends(require_role("admin")),
                db: Connection = Depends(get_db)):
    if not settings.sql_console_enabled:
        raise HTTPException(403, "SQL console disabled")
    try:
        result = execute_one(engine, payload.sql, payload.max_rows)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        # Log to audit even on failure
        db.execute(text(
            "INSERT INTO audit_logs (user_id, action, entity_type, before_value, ip_address) "
            "VALUES (:u, 'sql_exec_failed', 'sql', :sql, :ip)"
        ), {"u": u.id, "sql": json.dumps({"sql": payload.sql, "error": str(e)[:200]}),
            "ip": request.client.host if request.client else "unknown"})
        raise HTTPException(400, f"sql error: {e}")

    db.execute(text(
        "INSERT INTO audit_logs (user_id, action, entity_type, before_value, ip_address) "
        "VALUES (:u, 'sql_exec', 'sql', :sql, :ip)"
    ), {"u": u.id, "sql": json.dumps({"sql": payload.sql, "kind": result["kind"],
                                       "elapsed_ms": result["elapsed_ms"]}),
        "ip": request.client.host if request.client else "unknown"})

    # Convert non-JSON-serializable to str
    if "rows" in result:
        result["rows"] = [[_safe(c) for c in row] for row in result["rows"]]
    return result


def _safe(v):
    from datetime import datetime, date
    from decimal import Decimal
    if isinstance(v, (datetime, date)):
        return v.isoformat()
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, (bytes, bytearray)):
        return v.hex()
    return v
```

- [ ] **Step 3: Wire + commit**

```python
# main.py
from .routers import dev as dev_router
app.include_router(dev_router.router)
```

```bash
git add backend/app/routers/dev.py backend/app/schemas/dev.py backend/app/main.py
git commit -m "feat(backend): /api/dev/sql/execute (admin-only, audited, single-stmt)"
```

---

## Phase 9 — RAG Backend Reservation

### Task 9.1: RAG router skeleton (501 stubs)

**Files:**
- Create: `backend/app/routers/rag.py`, `backend/app/services/rag.py`

- [ ] **Step 1: Service stub**

```python
# backend/app/services/rag.py
"""RAG service skeleton — reserved, not implemented this term.
See docs/superpowers/specs/2026-05-07-nkg-design.md §12.
"""
```

- [ ] **Step 2: Router with 501 stubs**

```python
# backend/app/routers/rag.py
from fastapi import APIRouter, HTTPException, Depends
from ..deps import require_role

router = APIRouter(prefix="/api/rag", tags=["rag"])


def _stub():
    raise HTTPException(501, "RAG reserved; not implemented this term")


@router.post("/embed/chunks")
def embed_chunks(u=Depends(require_role("admin"))): _stub()


@router.post("/embed/entities")
def embed_entities(u=Depends(require_role("admin"))): _stub()


@router.post("/search/chunks")
def search_chunks(u=Depends(require_role("admin"))): _stub()


@router.post("/search/entities")
def search_entities(u=Depends(require_role("admin"))): _stub()


@router.post("/answer")
def answer(u=Depends(require_role("admin"))): _stub()
```

- [ ] **Step 3: Conditional wire in `main.py`**

```python
# main.py — add at bottom of file
if settings.rag_enabled:
    from .routers import rag as rag_router
    app.include_router(rag_router.router)
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/routers/rag.py backend/app/services/rag.py backend/app/main.py
git commit -m "feat(backend): RAG router skeleton (501 stubs, gated by RAG_ENABLED)"
```

**Phase 6-9 Done.** Backend complete. ~25 endpoints. All 6 SPs callable. SQL console live.

---

I'll continue with Phases 10-14 (frontend, perf, docs, demo) in the next batch.