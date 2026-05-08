<template>
  <div>
    <header class="page-head with-action">
      <div class="head-text">
        <h1>抽取任务</h1>
        <p class="lead">异步任务队列:认知地图、蓝图、图谱抽取的状态轨迹。</p>
      </div>
      <div class="head-action">
        <el-button @click="load">刷新</el-button>
      </div>
    </header>
    <el-table :data="rows" border>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="job_type" label="类型" width="140">
        <template #default="{row}">
          <span class="job-type">{{ row.job_type }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="120">
        <template #default="{row}">
          <span :class="['status-pill', `s-${row.status}`]">{{ row.status }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="topic_id" label="Topic" width="80" />
      <el-table-column prop="document_id" label="Doc" width="80" />
      <el-table-column prop="progress" label="进度" width="160">
        <template #default="{row}"><el-progress :percentage="row.progress || 0" /></template>
      </el-table-column>
      <el-table-column prop="error_message" label="错误" />
      <el-table-column prop="created_at" label="创建时间" width="180" />
    </el-table>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import client from '../api/client'
const rows = ref<any[]>([])
async function load() { rows.value = (await client.get('/jobs')).data }
onMounted(load)
</script>
<style scoped>
.job-type { font-family: var(--font-mono); font-size: 12px; color: var(--ink-secondary); }
</style>
