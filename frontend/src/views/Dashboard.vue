<template>
  <div>
    <h2>系统概览</h2>
    <el-row :gutter="16">
      <el-col :span="6"><el-card><div class="stat">{{ stats.topics }}</div><div>主题</div></el-card></el-col>
      <el-col :span="6"><el-card><div class="stat">{{ stats.docs }}</div><div>文档</div></el-card></el-col>
      <el-col :span="6"><el-card><div class="stat">{{ stats.entities }}</div><div>实体</div></el-card></el-col>
      <el-col :span="6"><el-card><div class="stat">{{ stats.rels }}</div><div>关系</div></el-card></el-col>
    </el-row>

    <el-card style="margin-top:16px">
      <template #header>最近抽取任务</template>
      <el-table :data="jobs" size="small">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="job_type" label="类型" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{row}">
            <el-tag :type="statusType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="topic_id" label="Topic" width="80" />
        <el-table-column prop="document_id" label="Doc" width="80" />
        <el-table-column prop="created_at" label="创建时间" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import client from '../api/client'

const stats = reactive({ topics: 0, docs: 0, entities: 0, rels: 0 })
const jobs = ref<any[]>([])

function statusType(s: string) {
  return { pending: 'info', running: 'warning', completed: 'success', failed: 'danger' }[s] || ''
}

onMounted(async () => {
  const [t, d, e, r, j] = await Promise.all([
    client.get('/topics'),
    client.get('/documents'),
    client.get('/entities'),
    client.get('/relationships'),
    client.get('/jobs?limit=10'),
  ])
  stats.topics = t.data.length
  stats.docs = d.data.length
  stats.entities = e.data.length
  stats.rels = r.data.length
  jobs.value = j.data.slice(0, 10)
})
</script>

<style scoped>.stat { font-size: 36px; font-weight: bold; color: #1890ff; }</style>
