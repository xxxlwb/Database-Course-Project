<template>
  <div>
    <header class="page-head">
      <div class="page-head-text">
        <h1>审计日志</h1>
        <p class="lead">由触发器和存储过程自动写入的全量操作记录。</p>
      </div>
    </header>
    <el-table :data="rows" border>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="user_id" label="用户" width="80" />
      <el-table-column prop="action" label="操作" width="140">
        <template #default="{row}">
          <el-tag>{{ row.action }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="entity_type" label="对象类型" width="120" />
      <el-table-column prop="entity_id" label="对象ID" width="100" />
      <el-table-column label="变更详情">
        <template #default="{row}">
          <pre class="audit-pre">{{ JSON.stringify({before: row.before_value, after: row.after_value}, null, 2) }}</pre>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="时间" width="180" />
    </el-table>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import client from '../api/client'
const rows = ref<any[]>([])
onMounted(async () => { rows.value = (await client.get('/audit-logs')).data })
</script>
<style scoped>
.audit-pre {
  font-size: 11px;
  margin: 0;
  max-height: 200px;
  overflow: auto;
}
</style>
