<template>
  <div>
    <h2>操作日志</h2>
    <el-table :data="rows" border>
      <el-table-column prop="id" width="80" />
      <el-table-column prop="user_id" label="用户" width="80" />
      <el-table-column prop="action" label="操作" width="120" />
      <el-table-column prop="entity_type" label="对象类型" width="100" />
      <el-table-column prop="entity_id" label="对象ID" width="100" />
      <el-table-column label="变更详情">
        <template #default="{row}">
          <pre style="font-size:11px">{{ JSON.stringify({before: row.before_value, after: row.after_value}, null, 2) }}</pre>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="时间" width="160" />
    </el-table>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import client from '../api/client'
const rows = ref<any[]>([])
onMounted(async () => { rows.value = (await client.get('/audit-logs')).data })
</script>
