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

I'll stop the plan file here and write Phase 4 (Stored Procedures) in a follow-up edit, plus Phases 5-14. The plan above is now ~14K characters and complete through Phase 3. Let me commit what's written, then continue appending in chunks.