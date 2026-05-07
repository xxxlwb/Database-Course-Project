# NKG —— 叙事型知识图谱管理系统 · 设计文档（数据库大作业）

- **作者**：luwenbo
- **日期**：2026-05-07
- **目标**：面向《数据库》课程大作业的满分（≥90）实施
- **目标交付物**：可运行的 Web 系统 + 12 张表的 MySQL 数据库 + 7 份文档

---

## 0. 背景与定位

本项目是一份**面向数据库课程**的大作业。课程评分硬指标包括：≥5 张表、≥3 触发器、≥2 带参存储过程、≥2 游标存储过程、≥2 二级索引 + 性能分析、规范化（≥3NF）论证、需求/设计/测试/操作文档、≥4000 字主报告、UI 与交互、创新与难度、答辩。

由于 TiDB 不支持触发器/存储过程/游标/UDF，硬指标无法在 TiDB 上落地，因此本作业**独立部署在本地 MySQL 8** 上完成。题材沿用 luwenbo 既有研究方向（叙事型知识图谱），但 schema、代码、文档全部为本课程独立编写。

**主题：通用叙事知识图谱平台（NKG）**。用户按 Topic 组织文档（项目复盘、读书笔记、案例研究、传记、会议纪要等任一题材），系统自动构建"单文档认知地图 → Topic 分析蓝图 → 全局知识图谱"三段式知识沉淀，支持图谱可视化、实体合并去重、跨文档查询。

---

## 1. 业务流程

```
┌─────────────┐  upload  ┌────────────┐  ETL chunk  ┌──────────────┐
│ User        │─────────▶│ Document   │────────────▶│ DocumentChunk│
└─────────────┘          └────────────┘             └──────┬───────┘
                                                            │ trigger
                                                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│ ExtractionJob (state: pending → cog_map → blueprint → graph → done) │
└──┬──────────────────┬───────────────────┬──────────────────────────-┘
   ▼                  ▼                   ▼
┌──────────┐   ┌──────────────────┐  ┌──────────────────────────┐
│ MiniMax  │──▶│ CognitiveMap (1) │──▶│ AnalysisBlueprint(Topic) │
│ LLM      │   └──────────────────┘  └──────────────┬───────────┘
└──────────┘                                         │
       └──────────────────┬──────────────────────────┘
                          ▼
                 ┌──────────────────────────────┐
                 │ Entities + Relationships     │
                 │ + ChunkEntityMapping         │
                 └──────────┬───────────────────┘
                            ▼
                  ┌─────────────────┐
                  │  Web UI / Graph │
                  │  Visualization  │
                  └─────────────────┘
```

### 核心抽象

| 概念 | 含义 | 落地表 |
|---|---|---|
| Topic | 主题/语境边界 | `topics` |
| Document | 一个原始文档 | `documents` |
| Chunk | 文档切块（图节点雏形） | `document_chunks` |
| Cognitive Map | 单文档认知地图（key entities / themes / timeline / patterns） | `cognitive_maps` |
| Analysis Blueprint | Topic 级跨文档分析蓝图（canonical entities / patterns / timeline） | `analysis_blueprints` |
| Entity | 高层实体节点 | `entities` |
| Entity Alias | 实体别名（去重） | `entity_aliases` |
| Relationship | 实体间关系（图边） | `relationships` |
| Chunk Entity Mapping | 块↔实体多对多 | `chunk_entity_mapping` |
| Extraction Job | 异步抽取任务状态机 | `extraction_jobs` |
| Audit Log | 操作审计 | `audit_logs` |
| User | 用户（含角色） | `users` |

---

## 2. 数据库设计

### 2.1 表清单（12 张）

| # | 表 | 主键 | 关键外键 |
|---|----|------|---------|
| 1 | `users` | id | — |
| 2 | `topics` | id | owner_id→users |
| 3 | `documents` | id | topic_id→topics、uploader_id→users |
| 4 | `document_chunks` | id | document_id→documents |
| 5 | `cognitive_maps` | id | document_id→documents (UQ) |
| 6 | `analysis_blueprints` | id | topic_id→topics (UQ) |
| 7 | `entities` | id | topic_id→topics |
| 8 | `entity_aliases` | id | entity_id→entities |
| 9 | `relationships` | id | topic_id、source_entity_id、target_entity_id |
| 10 | `chunk_entity_mapping` | id | chunk_id、entity_id |
| 11 | `extraction_jobs` | id | document_id、topic_id、created_by |
| 12 | `audit_logs` | id | user_id |

参照链：documents → chunks → mapping → entities ← relationships，4 级深度。
**满足要求 (1) ≥5 表 + 参照关系 — 远超**。

### 2.2 字段定义（节选关键字段，完整 DDL 见 `sql/01_schema.sql`）

```
users(id BIGINT PK AUTO_INCREMENT,
      username VARCHAR(64) UNIQUE NOT NULL,
      password_hash CHAR(60) NOT NULL,
      email VARCHAR(128) UNIQUE NOT NULL,
      role ENUM('admin','editor','viewer') NOT NULL DEFAULT 'editor',
      created_at DATETIME, updated_at DATETIME)

topics(id BIGINT PK,
       name VARCHAR(128) NOT NULL,
       description TEXT,
       owner_id BIGINT NOT NULL FK,
       doc_count INT NOT NULL DEFAULT 0,                 -- 触发器维护
       blueprint_status ENUM('outdated','generating','ready','failed') DEFAULT 'outdated',
       is_archived TINYINT(1) DEFAULT 0,
       created_at, updated_at,
       UNIQUE(owner_id, name))

documents(id BIGINT PK,
          topic_id BIGINT NOT NULL FK,
          uploader_id BIGINT NOT NULL FK,
          title VARCHAR(255) NOT NULL,
          source_type ENUM('text','markdown','pdf') NOT NULL,
          original_filename VARCHAR(255),
          file_size BIGINT,
          storage_path VARCHAR(512),                     -- 大文件落盘路径（PDF 必填）
          content MEDIUMTEXT,                            -- 解析后的纯文本（PDF 也存解析结果）
          content_hash CHAR(64) NOT NULL,                -- SHA-256，去重
          chunks_count INT DEFAULT 0,                    -- 触发器维护
          status ENUM('uploaded','chunking','chunk_done',
                      'extracting','completed','failed') DEFAULT 'uploaded',
          uploaded_at, updated_at)

document_chunks(id BIGINT PK,
                document_id BIGINT NOT NULL FK,
                chunk_index INT NOT NULL,
                content MEDIUMTEXT NOT NULL,
                content_hash CHAR(64),
                token_count INT,
                created_at,
                UNIQUE(document_id, chunk_index))

cognitive_maps(id BIGINT PK,
               document_id BIGINT NOT NULL UNIQUE FK,
               summary TEXT,
               key_entities JSON,
               themes JSON,
               timeline JSON,
               structural_patterns JSON,
               generated_by VARCHAR(64),
               version INT DEFAULT 1,
               generated_at, updated_at)

analysis_blueprints(id BIGINT PK,
                    topic_id BIGINT NOT NULL UNIQUE FK,
                    canonical_entities JSON,
                    key_patterns JSON,
                    global_timeline JSON,
                    processing_instructions TEXT,
                    contributing_doc_count INT,
                    source_data_hash CHAR(64),
                    status ENUM('outdated','generating','ready','failed') DEFAULT 'outdated',
                    version INT DEFAULT 1,
                    generated_at, updated_at)

entities(id BIGINT PK,
         topic_id BIGINT NOT NULL FK,
         canonical_name VARCHAR(255) NOT NULL,
         entity_type ENUM('person','project','task','concept',
                          'decision','event','place','other') NOT NULL,
         description TEXT,
         attributes JSON,
         mention_count INT DEFAULT 0,                    -- 触发器维护
         created_at, updated_at,
         UNIQUE(topic_id, canonical_name, entity_type))

entity_aliases(id BIGINT PK,
               entity_id BIGINT NOT NULL FK,
               alias VARCHAR(255) NOT NULL,
               source ENUM('auto','user') DEFAULT 'auto',
               confidence DECIMAL(3,2) DEFAULT 1.00,
               created_at,
               UNIQUE(entity_id, alias))

relationships(id BIGINT PK,
              topic_id BIGINT NOT NULL FK,
              source_entity_id BIGINT NOT NULL FK,
              target_entity_id BIGINT NOT NULL FK,
              relation_type VARCHAR(64) NOT NULL,
              description TEXT,
              weight DECIMAL(4,3) DEFAULT 1.000,
              attributes JSON,
              created_at, updated_at,
              UNIQUE(topic_id, source_entity_id, target_entity_id, relation_type),
              CHECK(source_entity_id <> target_entity_id))

chunk_entity_mapping(id BIGINT PK,
                     chunk_id BIGINT NOT NULL FK,
                     entity_id BIGINT NOT NULL FK,
                     occurrences INT DEFAULT 1,
                     position_info JSON,
                     created_at,
                     UNIQUE(chunk_id, entity_id))

extraction_jobs(id BIGINT PK,
                document_id BIGINT FK,
                topic_id BIGINT NOT NULL FK,
                job_type ENUM('cognitive_map','blueprint','graph') NOT NULL,
                status ENUM('pending','running','completed','failed') DEFAULT 'pending',
                progress TINYINT DEFAULT 0,                -- 0-100
                result JSON,
                error_message TEXT,
                created_by BIGINT FK,
                started_at, completed_at,
                created_at, updated_at)

audit_logs(id BIGINT PK,
           user_id BIGINT FK,
           action VARCHAR(32) NOT NULL,
           entity_type VARCHAR(32),
           entity_id BIGINT,
           before_value JSON,
           after_value JSON,
           ip_address VARCHAR(45),
           created_at)
```

### 2.3 触发器（5 个 — 要求 ≥3）

| Trigger | 时机 | 表 | 职责 |
|---|---|---|---|
| `trg_documents_after_insert` | AFTER INSERT | documents | 自动创建 cognitive_map 抽取任务 + 写审计日志 + topics.doc_count++ |
| `trg_chunks_after_insert` | AFTER INSERT | document_chunks | 维护 documents.chunks_count；首次插入将 status: uploaded → chunking |
| `trg_relationships_before_insert` | BEFORE INSERT | relationships | 校验 source/target 同 topic、拒绝 cross-topic、设默认 weight |
| `trg_entities_after_update` | AFTER UPDATE | entities | canonical_name 变了 → topics.blueprint_status='outdated'；写审计 |
| `trg_chunk_entity_after_insert` | AFTER INSERT | chunk_entity_mapping | entities.mention_count += occurrences |

→ **满足要求 (2)**

### 2.4 存储过程（共 6 个）

#### 带参（3 个，要求 ≥2）

| 名称 | 入参 / 出参 | 用途 |
|---|---|---|
| `sp_create_extraction_job` | IN doc_id BIGINT, IN job_type VARCHAR(32), IN user_id BIGINT, OUT job_id BIGINT | 事务性创建抽取任务，校验文档存在性与去重 |
| `sp_merge_entities` | IN keep_id BIGINT, IN merge_id BIGINT, IN user_id BIGINT | 实体合并：迁移所有关系/映射/别名 → 删除被合并实体 → 事务 + 审计；冲突回滚 |
| `sp_get_entity_neighborhood` | IN entity_id BIGINT, IN depth INT, OUT node_count INT | BFS 求 N 度邻居（depth ≤ 5 限制）。实现：在 sp 内创建会话级临时表 `tmp_neighborhood(entity_id BIGINT, distance INT)`，BFS 写入；sp 末尾 `SELECT * FROM tmp_neighborhood`，调用方拿 result set + OUT 参数 |

#### 用游标（3 个，要求 ≥2）

| 名称 | 入参 / 出参 | 游标用途 |
|---|---|---|
| `sp_recompute_entity_mentions` | — | 游标遍历所有实体，按 chunk_entity_mapping 重算 mention_count |
| `sp_archive_inactive_topics` | IN p_days INT, OUT p_count INT | 游标遍历 N 天未更新的 topic，逐个标记归档 + 写审计 |
| `sp_propagate_entity_rename` | IN topic_id BIGINT, IN pattern VARCHAR(255), IN new_name VARCHAR(255) | 游标遍历 topic 内匹配 pattern 的实体，逐个改名 + 自动建别名 |

→ **满足要求 (3)(4)**

### 2.5 索引（7 个，要求 ≥2）

```sql
CREATE INDEX idx_documents_topic_status ON documents(topic_id, status);
CREATE INDEX idx_documents_content_hash ON documents(content_hash);   -- 去重查询
CREATE INDEX idx_entities_topic_type_name ON entities(topic_id, entity_type, canonical_name);
CREATE INDEX idx_relationships_src_dst_type ON relationships(source_entity_id, target_entity_id, relation_type);
CREATE INDEX idx_mapping_entity ON chunk_entity_mapping(entity_id);   -- 反向查询
CREATE INDEX idx_audit_user_time ON audit_logs(user_id, created_at);
CREATE FULLTEXT INDEX ft_chunks_content ON document_chunks(content);   -- 加分项
```

#### 性能分析方案

种子脚本生成：5 万 chunks + 1 万 entities + 3 万 relationships + 5 万 mappings。

4 段对照实验：
1. `idx_relationships_src_dst_type` ON/OFF → 邻居查询响应时间
2. `idx_mapping_entity` ON/OFF → "实体出现在哪些块" 反查
3. `ft_chunks_content` vs `LIKE '%xxx%'` → 全文检索
4. 复合 index 的最左前缀验证（`WHERE entity_type=...` 不带 topic_id 走不走 index）

每段贴 `EXPLAIN ANALYZE` 的 cost / rows scanned 对比表。完整文档见 `docs/07-性能分析实验.md`。

→ **满足要求 (5)**

### 2.6 视图（3 个，加分）

```sql
CREATE VIEW v_entity_centrality AS ...        -- 实体度中心性
CREATE VIEW v_topic_overview AS ...           -- 每个 topic 的文档/实体/关系数量
CREATE VIEW v_extraction_job_status AS ...    -- 抽取任务总览
```

### 2.7 规范化（3NF）论证

文档 `docs/02-系统设计文档.md` 中"规范化推导"节按以下顺序写：

1. **从 ER 推关系模式**：先用最朴素方式画 ER（documents 字段和 entities 字段都堆在一张大表里）
2. **1NF 违反**：`entities.attributes` 若用 "k1=v1,k2=v2" 字符串违反 1NF；改用 JSON 字段属于业界共识的合规妥协（论文里说明）
3. **2NF 违反与拆解**：把 documents 大表里"chunk 内容"拆出来 → `document_chunks`，因为 chunk 内容只依赖 (document_id, chunk_index)，与 documents 主属性无完全依赖
4. **3NF 违反与拆解**：实体的"别名"原本嵌在 entities 大表里（alias1/alias2/...），存在传递依赖 `entity_id → alias_set → 各别名`，拆出 `entity_aliases`；同理 chunk_entity_mapping 拆出来消除多对多冗余
5. **特意保留的反规范字段**：`topics.doc_count`、`documents.chunks_count`、`entities.mention_count` 都是冗余字段，**用触发器维护一致性**，明确说明"为读性能做的反规范化"

→ **满足要求 (6)**

---

## 3. 应用架构

### 3.1 整体

```
┌──────────────────┐         HTTP/JSON        ┌──────────────────┐
│  Vue3 + Vite     │ ◄─────────────────────► │ FastAPI (Python) │
│  Element Plus    │                          │  └─ uvicorn      │
│  ECharts (force) │                          └────────┬─────────┘
│  Pinia + Router  │                                   │
│  Monaco Editor   │                                   │ SQLAlchemy Core (raw SQL)
└──────────────────┘                                   │ + 直接走 DB-API 调存储过程
                                                       ▼
                                            ┌──────────────────────┐
                                            │     MySQL 8          │
                                            │  ─ 12 tables         │
                                            │  ─ 5 triggers        │
                                            │  ─ 6 stored procs    │
                                            │  ─ 7 indexes         │
                                            │  ─ 3 views           │
                                            └──────────────────────┘
                                                       ▲
                                                       │
                                            ┌──────────────────────┐
                                            │ MiniMax LLM API      │
                                            │ (OpenAI-compatible)  │
                                            └──────────────────────┘
```

**关键决策**：
- 所有触发器/存储过程在 SQL 层定义；FastAPI 通过 `CALL sp_xxx(...)` 调用
- ORM 只用 Core 层 `text()` + 参数绑定，不用 Session ORM，让代码里能看到原始 SQL
- LLM 调用支持异步 worker，但同步抽取按钮保留以便答辩演示
- 抽取支持 mock 模式：未配置 MINIMAX_API_KEY 时自动回退到预设规则抽取

### 3.2 后端 API（FastAPI 路由）

| 模块 | 路由 | 方法 |
|---|---|---|
| 鉴权 | `/api/auth/login`、`/register`、`/me` | POST/GET |
| 用户 | `/api/users`、`/{id}` | CRUD（admin） |
| Topic | `/api/topics`、`/{id}` | CRUD + archive |
| 文档 | `/api/documents`、`/{id}`、`/{id}/chunks` | CRUD + 上传 |
| Cognitive Map | `/api/documents/{id}/cognitive-map` | POST/GET |
| Blueprint | `/api/topics/{id}/blueprint` | POST/GET |
| 抽取 | `/api/topics/{id}/extract` | POST |
| 实体 | `/api/entities`、`/{id}`、`/{id}/aliases`、`/merge` | CRUD + merge |
| 关系 | `/api/relationships`、`/{id}` | CRUD |
| 图谱 | `/api/topics/{id}/graph` | GET |
| 邻居 | `/api/entities/{id}/neighborhood?depth=N` | GET（调 sp） |
| 抽取任务 | `/api/jobs`、`/{id}` | GET（轮询） |
| 审计 | `/api/audit-logs` | GET |
| **SQL 控制台** | `/api/dev/sql/execute` | POST（admin） |
| 维护 | `/api/admin/recompute-mentions`、`/archive-inactive-topics` | POST（调游标 sp） |

### 3.3 前端页面（13 页）

| # | 页面 | 路径 |
|---|---|---|
| 1 | 登录/注册 | `/login` |
| 2 | Dashboard | `/` |
| 3 | Topic 管理 | `/topics` |
| 4 | Topic 详情（tab：文档/实体/关系/蓝图/图谱） | `/topics/:id` |
| 5 | 文档管理 | `/documents` |
| 6 | 文档详情（内容/chunks/认知地图/实体引用） | `/documents/:id` |
| 7 | 实体库（含合并对话框、别名管理） | `/entities` |
| 8 | 关系库 | `/relationships` |
| 9 | 图谱可视化（ECharts force-directed） | `/topics/:id/graph` |
| 10 | 抽取任务 | `/jobs` |
| 11 | 操作日志 | `/audit` |
| 12 | **SQL 控制台**（通用执行台） | `/dev/sql` |
| 13 | 用户/系统设置（admin） | `/settings` |

### 3.4 SQL 控制台规格（升级版 — 通用执行台）

支持任何合法 SQL，结果按类型可视化：

| 语句类型 | 后端识别 | 前端展示 |
|---|---|---|
| `SELECT ...` | 取行集 | 表格（分页 + 列宽自适应 + 复制 + 导出 CSV） |
| `EXPLAIN [ANALYZE] ...` | 取计划 | 表格 + 计划树（可折叠节点，cost/rows） |
| `INSERT/UPDATE/DELETE` | 取 affected rows | "✓ 成功，影响 N 行" + 用时 |
| `CREATE/ALTER/DROP/TRUNCATE` | 取状态 | "✓ DDL 执行成功" + 用时 + 二次确认 |
| `CALL sp_xxx(...)` | 取多结果集 + OUT 参数 | 多 tab 表格（OUT 参数单独一栏） |
| `SHOW TABLES/INDEX/CREATE...` | 取行集 | 表格 |
| `BEGIN/COMMIT/ROLLBACK` | 见下方"事务模式" | 状态条显示"事务中"|

**安全护栏**：
- 仅 `admin` 角色访问
- 每次执行写 audit_logs（SQL 原文 / user / affected rows / 耗时 / ip）
- 全局开关 `SQL_CONSOLE_ENABLED`（.env），默认 true
- DDL/DROP 二次确认弹窗
- `SET STATEMENT max_statement_time=15` 防死循环
- 一次只允许一条 SQL（拒绝 `;` 拼接），防止注入式批量
- 历史抽屉：最近 50 条本人执行的 SQL

**事务模式**：
- 默认每条语句独立事务（autocommit=ON）
- 用户点"开启事务"按钮 → 后端在内存 dict 里为该 user 申领一个独占连接（连接池外另起），key=user_id，TTL 5 分钟
- 期间所有 SQL 走该连接；用户点 COMMIT/ROLLBACK 或 TTL 到期时归还连接
- 若同 user 连两个 SQL 控制台 tab：第二个看到"已有活动事务"提示，需先结束

**前端组件**：
- 编辑器：Monaco（VSCode 同款 + MySQL 高亮）
- 结果区：tab（数据 / 执行计划 / 元信息）
- 顶栏快捷按钮：`SHOW TABLES` / `SHOW PROCEDURE STATUS` / `SHOW TRIGGERS` / `EXPLAIN` 模板

### 3.5 仓库目录

```
db_course/
├── README.md
├── Makefile                           # make db-init / make backend / make frontend
├── docker-compose.yml                 # 可选 MySQL + adminer
├── .env.example
│
├── docs/
│   ├── 01-需求分析文档.md             # 1500 字
│   ├── 02-系统设计文档.md             # 3500 字（含 ER + 3NF）
│   ├── 03-数据库实施文档.md           # 1500 字
│   ├── 04-测试报告.md                 # 2000 字
│   ├── 05-操作手册.md                 # 1500 字
│   ├── 06-大作业总报告.md             # ≥4500 字（不含代码）
│   ├── 07-性能分析实验.md             # 1800 字
│   └── images/                        # ER 图 / 流程图 / 12 张拷屏
│
├── sql/
│   ├── 00_drop_all.sql
│   ├── 01_schema.sql
│   ├── 02_indexes.sql
│   ├── 03_views.sql
│   ├── 04_triggers.sql                # 5 个
│   ├── 05_procedures.sql              # 6 个
│   ├── 06_seed.sql                    # 演示数据
│   ├── 07_seed_perf.sql               # 5 万行压力数据
│   └── 99_perf_queries.sql            # EXPLAIN 实验脚本
│
├── backend/
│   ├── pyproject.toml                 # uv / pip-tools
│   ├── .env.example
│   └── app/
│       ├── main.py
│       ├── config.py
│       ├── db.py                      # 连接池 (pymysql + sqlalchemy.text)
│       ├── deps.py                    # 鉴权依赖
│       ├── security.py                # JWT + bcrypt
│       ├── llm.py                     # MiniMax 客户端（含 mock）
│       ├── schemas/                   # Pydantic
│       ├── services/                  # 业务（CALL sp_xxx）
│       └── routers/
│           ├── auth.py
│           ├── topics.py
│           ├── documents.py
│           ├── chunks.py
│           ├── cognitive.py
│           ├── blueprint.py
│           ├── entities.py
│           ├── relationships.py
│           ├── graph.py
│           ├── jobs.py
│           ├── audit.py
│           └── dev.py                 # /sql/execute
│
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── index.html
│   └── src/
│       ├── main.ts
│       ├── App.vue
│       ├── router/
│       ├── stores/
│       ├── api/
│       ├── components/
│       │   ├── EntityMergeDialog.vue
│       │   ├── GraphCanvas.vue
│       │   ├── ExplainViewer.vue
│       │   ├── SqlEditor.vue          # Monaco 包装
│       │   └── ...
│       ├── views/                     # 13 页
│       └── styles/
│
└── scripts/
    ├── init_db_local.sh
    ├── init_db_docker.sh
    └── load_demo_data.sh
```

### 3.6 启动方式

**本地 MySQL 8（默认，优先）**：
```bash
mysql -u root -p < sql/00_drop_all.sql
make db-init                                  # 顺序执行 01→07

cd backend && uv venv && source .venv/bin/activate
uv pip install -r requirements.txt
cp .env.example .env                          # 填 DB_URL + MINIMAX_API_KEY
uvicorn app.main:app --reload

cd frontend && pnpm install && pnpm dev
# → http://localhost:5173
```

**Docker 退路**：
```bash
docker compose up -d mysql adminer
make db-init
# 后端、前端启动同上
```

---

## 4. 文档与字数

| 文件 | 目标字数 | 评分点 |
|---|---|---|
| `01-需求分析文档.md` | 1500 | 文档评分 5 |
| `02-系统设计文档.md` | 3500 | 文档评分 5；含 ER + 3NF |
| `03-数据库实施文档.md` | 1500 | 数据库实施 5-10 |
| `04-测试报告.md` | 2000 | 文档评分 5 |
| `05-操作手册.md` | 1500 | 文档评分 5 |
| `06-大作业总报告.md` | **≥4500** | **课程硬要求 4000+** |
| `07-性能分析实验.md` | 1800 | 扩展功能 5-10 |

合计 ~16K 字。**主报告(06)**单独超过 4000 字硬指标。

### 主报告(06)结构

```
1. 系统简介与背景        ── 400
2. 功能与目标             ── 400
3. 需求分析摘要           ── 600
4. 系统总体设计           ── 600
   4.1 架构图
   4.2 模块划分
   4.3 技术选型理由
5. 数据库设计              ── 1200
   5.1 ER 图
   5.2 关系模式与 3NF 推导
   5.3 表结构概览
   5.4 触发器/存储过程职责
   5.5 索引与性能优化
6. 关键实现                ── 700
   6.1 LLM 抽取流水线
   6.2 实体合并算法
   6.3 图谱可视化
7. 测试与性能              ── 400
8. 心得与未来工作          ── 200
合计 ≈ 4500
```

---

## 5. 测试

| 维度 | 用例 |
|---|---|
| 单元 | 核心 service 函数（pytest） |
| 集成 | API 端到端（httpx async client） |
| 触发器 | 5 个触发器逐个写专项测试，断言副作用 |
| 存储过程 | 6 个存储过程 + IN/OUT/CURSOR 全覆盖 |
| 性能 | 7 个索引 ON/OFF 对比 |
| 事务 | 实体合并的回滚测试 |
| 安全 | SQL 注入尝试 + 越权访问 |
| UI | 关键页面 12 张截图清单 |

---

## 6. 创新点

1. **LLM 驱动的三段式知识抽取**（cognitive map → blueprint → graph）
2. **实体合并的事务级原子操作**（关系/映射/别名一次性迁移 + 回滚）
3. **MySQL FULLTEXT 索引 vs LIKE 性能对比** 实验
4. **EXPLAIN 可视化 + 通用 SQL 执行台**
5. **触发器维护的反规范化字段**（doc_count / chunks_count / mention_count）
6. **图谱力导向可视化**（ECharts + 度中心性视图）

---

## 7. 演示拷屏清单（12 张）

按这个顺序：
1. 登录页
2. Dashboard
3. 上传文档
4. 文档详情 → cognitive map 生成中
5. 文档详情 → cognitive map 完成
6. Topic 蓝图（blueprint）展示
7. 实体管理列表
8. 实体合并对话框（演示 sp_merge_entities）
9. 关系列表 + 新建（演示触发器拒绝 cross-topic）
10. 图谱可视化
11. 抽取任务列表
12. SQL 执行台（CALL 存储过程 + EXPLAIN 对比）

---

## 8. 评分对账总表（瞄准 95+）

| 大项 | 子项 | 满分 | 设计落点 | 自评 |
|---|---|---|---|---|
| **一. 功能实现** | 基本完整性 | 15 | 12 表 CRUD + 完整约束 | 15 |
|  | 高级功能 | 15 | 多表连接、视图、6 SP、5 TR、事务 | 15 |
|  | 扩展功能 | 10 | 索引/全文/SQL 控制台/审计/角色权限 | 9-10 |
| **二. 数据库设计** | ER 模型 | 10 | ER 图 + 完整属性 + 3NF 论证 | 10 |
|  | 关系模式转换 | 10 | 完整推导 + PK/FK 全覆盖 | 10 |
|  | 数据库实施 | 10 | DDL/DML 分文件 + 数据类型论证 | 10 |
| **三. 界面与交互** | 用户界面 | 10 | Vue3 + Element Plus + ECharts | 9-10 |
|  | 系统交互 | 10 | 全表单校验、错误提示、Loading、操作反馈 | 9 |
| **四. 文档** | 需求分析 | 5 | 1500 字 + 用例图 | 5 |
|  | 设计 | 5 | 3500 字 + ER + 时序 | 5 |
|  | 测试 | 5 | 2000 字 + 覆盖矩阵 | 5 |
|  | 操作手册 | 5 | 1500 字 + 截图 | 5 |
| **五. 创新难度** | 综合 | 10 | LLM + KG + 性能实验 + SQL 控制台 | 9-10 |
| **六. 答辩** | 综合 | 15 | 12 张拷屏 + 演示脚本 + Q&A 预案 | 留给答辩 |

→ **预期总分：90-100**

---

## 9. 时间表

| 批次 | 产出 |
|---|---|
| 启动后 1-2 天 | sql/01_schema.sql + 02_indexes.sql + 03_views.sql 跑通 |
| 3-5 天 | sql/04_triggers.sql + 05_procedures.sql + 06_seed.sql + SQL 测试 |
| 6-8 天 | backend 全部 API + LLM 集成（含 mock） |
| 9-11 天 | frontend 13 页 |
| 12-14 天 | 性能实验 + 全部文档 + 截图 |

---

## 10. 关键约束与风险

- **TiDB 不支持触发器/存储过程/游标/UDF** → 已选独立 MySQL 8，不复用 luwenbo 既有 TiDB 项目
- **MiniMax API key 可能限速/欠费** → 后端 `llm.py` 提供 mock 模式回退，不依赖网络也能演示
- **SQL 控制台风险** → 仅 admin、写审计、单条限制、超时限制；可 .env 关闭
- **演示环境** → 4000 字主报告 + 7 份子文档 + 12 张拷屏 + 现场跑 demo 三选一也能撑场
- **答辩问答**：触发器副作用、3NF 推导、合并事务、索引选型 — 主报告里都有原文可读

---

## 11. 不在范围内（YAGNI）

- 多租户 / SaaS（仅单实例）
- OAuth / SSO（仅本地 JWT）
- 实时协同编辑
- 移动端
- 国际化（仅中文 UI）
- LLM 模型微调

---

## 12. RAG 预留（本期不实现、不测试）

为了不让后续做 RAG 时改大表结构，**本期保留 schema 与 API 骨架**，但**不写业务逻辑、不写测试、文档里也不计入功能分**。所有 RAG 相关入口都被 feature flag 关掉，避免误触发抽取。

### 12.1 预留表（2 张，DDL 进 `sql/01_schema.sql`，不在 12 张主表统计内）

```sql
-- 文档块向量（与 document_chunks 1:1）
chunk_embeddings(
    chunk_id BIGINT PRIMARY KEY,
    embedding LONGBLOB NOT NULL,                    -- float32[] 紧凑存储
    embedding_dim INT NOT NULL,                     -- e.g. 1024 / 1536
    model VARCHAR(64) NOT NULL,                     -- e.g. "minimax-embedding-001"
    norm DECIMAL(10,6),                             -- 预算 L2 norm，加速余弦
    created_at DATETIME,
    FOREIGN KEY (chunk_id) REFERENCES document_chunks(id) ON DELETE CASCADE
)

-- 实体向量（与 entities 1:1）
entity_embeddings(
    entity_id BIGINT PRIMARY KEY,
    embedding LONGBLOB NOT NULL,
    embedding_dim INT NOT NULL,
    model VARCHAR(64) NOT NULL,
    norm DECIMAL(10,6),
    created_at DATETIME,
    FOREIGN KEY (entity_id) REFERENCES entities(id) ON DELETE CASCADE
)
```

**为什么用 LONGBLOB 而不是 JSON / VECTOR**：
- MySQL 8.0 无原生 VECTOR 类型（9.x 才有）
- JSON 数组每维一个 ASCII 数字，4096 维约 80KB；LONGBLOB float32 仅 16KB，4×节省
- 明文 BLOB 不利于人工排查，但本期不做检索演示，可接受
- 后续若升级 MySQL 9 / 接入 TiDB Vector / Milvus，仅需改这两张表的列定义和 ORM mapper

**索引**：本期**不建** ANN 索引（MySQL 8 无原生支持）；预留 `idx_chunk_emb_model`、`idx_entity_emb_model` 普通 B+树，按 model 过滤。

### 12.2 预留 API（返回 501 Not Implemented）

```
POST /api/rag/embed/chunks       # 批量 embed，feature flag 关闭
POST /api/rag/embed/entities
POST /api/rag/search/chunks      # 给定 query，返回 top-k chunks
POST /api/rag/search/entities    # 给定 query，返回 top-k entities
POST /api/rag/answer             # RAG 问答（chunks 检索 + LLM 合成）
```

骨架文件：`backend/app/services/rag.py`、`backend/app/routers/rag.py`。
路由注册时按 `RAG_ENABLED` 决定是否挂载；默认关闭。

### 12.3 预留前端

- `frontend/src/views/RagSearch.vue` 占位页面
- 路由 `/rag` 仅 admin 可见，feature flag 关闭时显示"模块预留中，本期不可用"
- 不进 13 页主导航；走"实验性功能"折叠菜单

### 12.4 Feature Flag

```
# .env.example
RAG_ENABLED=false              # 本期默认关闭
EMBEDDING_MODEL=minimax-embedding-001
EMBEDDING_DIM=1024
```

后端启动时读取，false → 路由不注册、UI 隐藏、不消耗任何 LLM 配额。

### 12.5 文档处理

- 主报告 06 中"未来工作"节列 RAG 为下一阶段目标，**1 段话**说明
- 设计文档 02 中加一节"扩展点：向量与 RAG"，描述 schema 与升级路径，**不超过 1 页**
- 测试报告 04 **不**列 RAG 用例
- 评分对账表中 RAG 不计入任何子项

### 12.6 升级路径（仅备忘，不在本期工作量内）

未来切到 MySQL 9 / TiDB / Milvus 时，需要改：
1. 两张 embeddings 表的列类型（BLOB → VECTOR）
2. 添加 ANN 索引（HNSW / IVF）
3. 实现 `services/rag.py` 中的检索逻辑
4. 打开 `RAG_ENABLED`，前端 `RagSearch.vue` 实现搜索表单和结果列表
5. 跑 RAG 端到端测试
