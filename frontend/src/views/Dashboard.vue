<template>
  <div class="dashboard">
    <header class="page-head">
      <h1>系统概览</h1>
      <p class="lead">
        在此查看主题、文档、实体和关系的全局指标,以及最近的抽取任务进度。
      </p>
    </header>

    <section class="stat-grid">
      <div class="stat-card" v-for="(s, i) in items" :key="i" :style="{'--delay': i*60+'ms'}">
        <div class="stat-num">{{ s.value }}</div>
        <div class="stat-name">{{ s.name }}</div>
        <div class="stat-meta">{{ s.meta }}</div>
      </div>
    </section>

    <section>
      <header class="section-head">
        <h2>最近抽取任务</h2>
        <router-link to="/jobs" class="view-all">查看全部 →</router-link>
      </header>
      <div class="job-card">
        <el-table :data="jobs" size="default">
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
          <el-table-column prop="created_at" label="创建时间" />
        </el-table>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import client from '../api/client'

const stats = ref({ topics: 0, docs: 0, entities: 0, rels: 0 })
const jobs = ref<any[]>([])

const items = computed(() => [
  { value: stats.value.topics, name: '主题空间', meta: 'Topics' },
  { value: stats.value.docs, name: '文档', meta: 'Documents' },
  { value: stats.value.entities, name: '实体', meta: 'Entities' },
  { value: stats.value.rels, name: '关系', meta: 'Relationships' },
])

onMounted(async () => {
  const [t, d, e, r, j] = await Promise.all([
    client.get('/topics'),
    client.get('/documents'),
    client.get('/entities'),
    client.get('/relationships'),
    client.get('/jobs?limit=10'),
  ])
  stats.value = { topics: t.data.length, docs: d.data.length, entities: e.data.length, rels: r.data.length }
  jobs.value = j.data.slice(0, 8)
})
</script>

<style scoped>
.dashboard { max-width: 1200px; }

.stat-grid {
  display: grid; grid-template-columns: repeat(4, 1fr);
  gap: var(--space-4);
  margin-bottom: var(--space-7);
}
.stat-card {
  padding: var(--space-5) var(--space-5) var(--space-4);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  background: var(--surface-elev);
  transition: border-color var(--t), transform var(--t), box-shadow var(--t);
  animation: fade-up 0.5s var(--delay, 0ms) ease both;
}
.stat-card:hover {
  border-color: var(--border-strong);
  transform: translateY(-2px);
  box-shadow: var(--shadow);
}
.stat-num {
  font-family: var(--font-display);
  font-size: 44px;
  font-weight: 350;
  color: var(--ink);
  line-height: 1;
  letter-spacing: -0.025em;
}
.stat-name {
  margin-top: var(--space-3);
  font-size: 14px;
  font-weight: 500;
  color: var(--ink);
}
.stat-meta {
  margin-top: 2px;
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--ink-faint);
  letter-spacing: 0.04em;
}

.job-card {
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  background: var(--surface-elev);
  overflow: hidden;
}
.job-type { font-family: var(--font-mono); font-size: 12px; color: var(--ink-secondary); }

@keyframes fade-up {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}
</style>
