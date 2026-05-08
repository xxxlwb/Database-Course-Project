<template>
  <div class="sql-console">
    <header class="page-head">
      <div class="page-head-text">
        <h1>SQL 控制台</h1>
        <p class="lead">面向管理员的通用执行台。所有语句都会写入审计日志。</p>
      </div>
      <div class="page-head-actions toolbar">
        <el-button @click="run('SHOW TABLES')">SHOW TABLES</el-button>
        <el-button @click="run('SHOW PROCEDURE STATUS WHERE Db = DATABASE()')">SHOW PROCEDURES</el-button>
        <el-button @click="run('SHOW TRIGGERS')">SHOW TRIGGERS</el-button>
        <el-button type="primary" @click="execute" :loading="busy">▶ 执行</el-button>
      </div>
    </header>
    <div class="editor-wrap">
      <vue-monaco-editor v-model:value="sql" language="sql" theme="vs-dark" :height="240" />
    </div>
    <div v-if="result" class="result">
      <el-alert :type="result.kind==='ddl'||result.kind==='dml'?'success':'info'"
                :title="`${result.kind} · ${result.elapsed_ms}ms · ${result.row_count ?? result.affected_rows ?? 0} 行`" />
      <el-table v-if="result.rows" :data="tableRows" size="small" border max-height="400" style="margin-top:12px">
        <el-table-column v-for="c in result.columns" :key="c" :prop="c" :label="c" />
      </el-table>
    </div>
    <el-alert v-if="error" type="error" :title="error" style="margin-top:12px" />
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
async function execute() { run(sql.value) }
async function run(q: string) {
  busy.value = true; error.value = ''; result.value = null
  try { result.value = (await client.post('/dev/sql/execute', { sql: q })).data }
  catch (e: any) { error.value = e.response?.data?.detail || String(e) }
  finally { busy.value = false }
}
const tableRows = computed(() => {
  if (!result.value?.rows) return []
  return result.value.rows.map((r: any[]) => Object.fromEntries(result.value.columns.map((c: string, i: number) => [c, r[i]])))
})
</script>
<style scoped>
.sql-console { display: flex; flex-direction: column; gap: var(--s-4); }
.toolbar { display: flex; gap: var(--s-2); flex-wrap: wrap; }
.editor-wrap {
  border: 1px solid var(--border);
  border-radius: var(--r);
  overflow: hidden;
}
.result { display: flex; flex-direction: column; }
</style>
