<template>
  <div>
    <h2>抽取任务</h2>
    <el-table :data="rows" border>
      <el-table-column prop="id" width="60" />
      <el-table-column prop="job_type" label="类型" width="120" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{row}"><el-tag :type="t(row.status)">{{ row.status }}</el-tag></template>
      </el-table-column>
      <el-table-column prop="topic_id" label="Topic" width="80" />
      <el-table-column prop="document_id" label="Doc" width="80" />
      <el-table-column prop="progress" label="进度" width="100">
        <template #default="{row}"><el-progress :percentage="row.progress || 0" /></template>
      </el-table-column>
      <el-table-column prop="error_message" label="错误" />
      <el-table-column prop="created_at" label="创建时间" width="160" />
    </el-table>
    <el-button @click="load" style="margin-top:8px">刷新</el-button>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import client from '../api/client'
const rows = ref<any[]>([])
function t(s:string) { return ({pending:'info',running:'warning',completed:'success',failed:'danger'} as any)[s] || '' }
async function load() { rows.value = (await client.get('/jobs')).data }
onMounted(load)
</script>
