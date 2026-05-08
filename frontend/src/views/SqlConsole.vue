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

    <div class="editor-wrap">
      <vue-monaco-editor
        v-model:value="sql"
        language="sql"
        theme="vs-dark"
        height="320px"
        :options="editorOptions"
      />
    </div>

    <div v-if="result" class="result">
      <el-alert
        :type="result.kind==='ddl'||result.kind==='dml'?'success':'info'"
        :title="`${result.kind} · ${result.elapsed_ms}ms · ${result.row_count ?? result.affected_rows ?? 0} 行`"
        :closable="false"
      />
      <el-table v-if="result.rows" :data="tableRows" size="small" border max-height="400" style="margin-top:12px">
        <el-table-column v-for="c in result.columns" :key="c" :prop="c" :label="c" />
      </el-table>
    </div>
    <el-alert v-if="error" type="error" :title="error" style="margin-top:12px" :closable="false" />
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
.sql-console { display: flex; flex-direction: column; gap: var(--s-4); }

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

.editor-wrap {
  border: 1px solid var(--border-strong);
  border-radius: var(--r-md);
  overflow: hidden;
  min-height: 320px;
  background: #1e1e1e;
}

.result { display: flex; flex-direction: column; }
</style>
