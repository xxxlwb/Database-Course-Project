<template>
  <div class="sql-console">
    <header class="page-head">
      <div class="page-head-text">
        <h1>SQL 控制台</h1>
        <p class="lead">面向管理员的通用执行台。所有语句都会写入审计日志。</p>
      </div>
      <div class="page-head-actions toolbar">
        <button class="preset" @click="run('SHOW TABLES')">
          <span class="zh">数据表</span><span class="en">SHOW TABLES</span>
        </button>
        <button class="preset" @click="run('SHOW PROCEDURE STATUS WHERE Db = DATABASE()')">
          <span class="zh">存储过程</span><span class="en">SHOW PROCEDURES</span>
        </button>
        <button class="preset" @click="run('SHOW TRIGGERS')">
          <span class="zh">触发器</span><span class="en">SHOW TRIGGERS</span>
        </button>
        <button class="preset" @click="run(`SHOW FULL TABLES WHERE Table_type = 'VIEW'`)">
          <span class="zh">视图</span><span class="en">SHOW VIEWS</span>
        </button>
        <button class="preset" @click="run('SHOW INDEX FROM entities')">
          <span class="zh">索引</span><span class="en">SHOW INDEXES</span>
        </button>
        <el-button type="primary" @click="execute" :loading="busy">▶ 执行 RUN</el-button>
      </div>
    </header>

    <div class="split">
      <div class="editor-wrap">
        <div class="panel-bar">
          <span class="panel-title">编辑器 EDITOR</span>
          <span class="panel-meta">{{ sql.length }} chars · MySQL</span>
        </div>
        <vue-monaco-editor
          v-model:value="sql"
          language="sql"
          theme="vs-dark"
          height="100%"
          :options="editorOptions"
        />
      </div>

      <div ref="resultBox" class="result-wrap">
        <div class="panel-bar light">
          <span class="panel-title">结果 RESULT</span>
          <span v-if="result" class="panel-meta">
            {{ result.kind }} · {{ result.elapsed_ms }}ms ·
            {{ result.row_count ?? result.affected_rows ?? 0 }} 行
          </span>
        </div>
        <div class="result-body">
          <div v-if="busy" class="placeholder">
            <span class="dot"></span> 执行中…
          </div>
          <template v-else-if="result">
            <el-table v-if="result.rows" :data="tableRows" size="small" border height="100%">
              <el-table-column v-for="c in result.columns" :key="c" :prop="c" :label="c" min-width="120" />
            </el-table>
            <el-alert
              v-else
              :type="result.kind==='ddl'||result.kind==='dml'?'success':'info'"
              :title="`✓ ${result.kind} 执行成功，影响 ${result.affected_rows ?? 0} 行`"
              :closable="false"
            />
          </template>
          <el-alert v-else-if="error" type="error" :title="error" :closable="false" />
          <div v-else class="placeholder muted">
            <div>
              <div class="placeholder-emoji">⌨</div>
              <div>编辑左侧 SQL 后按「执行 RUN」</div>
              <div class="placeholder-hint">或点击上方预设按钮快速查询</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { VueMonacoEditor } from '@guolao/vue-monaco-editor'
import client from '../api/client'

const sql = ref('SELECT id, canonical_name, mention_count FROM entities ORDER BY mention_count DESC LIMIT 10;')
const result = ref<any>(null)
const error = ref('')
const busy = ref(false)
const resultBox = ref<HTMLElement>()

const editorOptions = {
  minimap: { enabled: false },
  fontSize: 13,
  fontFamily: 'JetBrains Mono, SF Mono, Menlo, monospace',
  lineNumbers: 'on' as const,
  scrollBeyondLastLine: false,
  automaticLayout: true,
  tabSize: 2,
  wordWrap: 'on' as const,
  padding: { top: 12, bottom: 12 },
}

async function execute() { run(sql.value) }
async function run(q: string) {
  busy.value = true; error.value = ''; result.value = null
  try { result.value = (await client.post('/dev/sql/execute', { sql: q })).data }
  catch (e: any) { error.value = e.response?.data?.detail || String(e) }
  finally { busy.value = false }
}

const tableRows = computed(() => {
  if (!result.value?.rows) return []
  return result.value.rows.map((r: any[]) => Object.fromEntries(
    result.value.columns.map((c: string, i: number) => [c, r[i]])
  ))
})
</script>

<style scoped>
.sql-console { display: flex; flex-direction: column; gap: var(--s-4); height: calc(100vh - 160px); min-height: 540px; }

.toolbar { display: flex; gap: var(--s-2); flex-wrap: wrap; align-items: center; }

/* Bilingual preset button — Chinese on top of mono English */
.preset {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 6px 12px;
  background: var(--canvas);
  border: 1px solid var(--border-strong);
  border-radius: var(--r);
  cursor: pointer;
  font-family: var(--font);
  transition: background var(--t), border-color var(--t), transform var(--t);
}
.preset:hover {
  background: var(--surface);
  border-color: var(--ink-3);
  transform: translateY(-1px);
}
.preset:active { transform: translateY(0); }
.preset .zh {
  font-size: 13px; font-weight: 600; color: var(--ink);
}
.preset .en {
  font-family: var(--font-mono);
  font-size: 10.5px; font-weight: 500;
  color: var(--ink-4);
  letter-spacing: 0.04em;
}

/* Split view: editor LEFT, result RIGHT, equal columns, fill remaining height */
.split {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: var(--s-4);
  flex: 1;
  min-height: 0;
}

/* Shared panel chrome (title bar + body) */
.editor-wrap, .result-wrap {
  display: flex; flex-direction: column;
  border: 1px solid var(--border-strong);
  border-radius: var(--r-md);
  overflow: hidden;
  min-height: 0;
}
.editor-wrap { background: #1e1e1e; }
.result-wrap { background: var(--canvas); }

.panel-bar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 8px 14px;
  background: #2D3540;
  border-bottom: 1px solid #1A2028;
  flex-shrink: 0;
}
.panel-bar.light {
  background: var(--surface);
  border-bottom-color: var(--border);
}
.panel-title {
  font-size: 12px; font-weight: 600;
  color: rgba(255,255,255,0.85);
  letter-spacing: 0.04em;
}
.panel-bar.light .panel-title { color: var(--ink); }
.panel-meta {
  font-family: var(--font-mono);
  font-size: 11px;
  color: rgba(255,255,255,0.55);
  letter-spacing: 0.04em;
}
.panel-bar.light .panel-meta { color: var(--ink-3); }

/* Editor wrap holds Monaco directly; ensure it stretches */
.editor-wrap :deep(.monaco-editor),
.editor-wrap :deep(.monaco-editor .overflow-guard) {
  flex: 1;
  height: 100% !important;
}

.result-body {
  flex: 1;
  min-height: 0;
  overflow: hidden;
  padding: var(--s-3);
  display: flex; flex-direction: column;
}
.result-body :deep(.el-table) { flex: 1; }

.placeholder {
  flex: 1;
  display: flex; align-items: center; justify-content: center;
  color: var(--ink-4);
  font-size: 13px;
  text-align: center;
  gap: 8px;
}
.placeholder.muted { color: var(--ink-4); }
.placeholder-emoji { font-size: 32px; margin-bottom: 8px; opacity: 0.55; }
.placeholder-hint { font-size: 11.5px; color: var(--ink-5); margin-top: 4px; font-family: var(--font-mono); }
.placeholder .dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: var(--purple);
  animation: pulse 1.2s infinite ease;
}
@keyframes pulse {
  0%, 100% { opacity: 0.3; transform: scale(0.85); }
  50%      { opacity: 1;   transform: scale(1.1); }
}

/* Stack vertically on narrow screens */
@media (max-width: 1100px) {
  .sql-console { height: auto; }
  .split { grid-template-columns: 1fr; }
  .editor-wrap, .result-wrap { min-height: 360px; }
}
</style>
