<template>
  <div class="dashboard fade-in">
    <header class="page-head">
      <div class="page-head-text">
        <h1>系统概览</h1>
        <p class="lead">主题、文档、实体、关系的全局指标,以及最近抽取任务进度。</p>
      </div>
    </header>

    <section class="stat-grid">
      <div class="stat-card" v-for="(s, i) in items" :key="i" :style="{'animation-delay': i*60+'ms'}">
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
            <template #default="{row}"><span class="job-type">{{ row.job_type }}</span></template>
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
.lead { color: var(--ink-3); font-size: 14px; max-width: 640px; margin: 6px 0 0; line-height: 1.6; }

.stat-grid {
  display: grid; grid-template-columns: repeat(4, 1fr);
  gap: var(--s-4);
  margin-bottom: var(--s-7);
}
.stat-num {
  font-size: 36px; font-weight: 700;
  color: var(--ink);
  letter-spacing: -0.025em;
  line-height: 1.05;
  font-feature-settings: 'tnum';
}
.stat-name { margin-top: var(--s-3); font-size: 13.5px; font-weight: 600; color: var(--ink); }
.stat-meta {
  margin-top: 3px;
  font-family: var(--font-mono);
  font-size: 10.5px;
  color: var(--ink-4);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.section-head {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: var(--s-4);
}
.section-head h2 { margin: 0; }
.view-all {
  font-size: 13px; color: var(--purple); text-decoration: none;
  font-weight: 600; transition: color var(--t);
}
.view-all:hover { color: var(--purple-hover); }

.job-card {
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  background: var(--canvas);
  overflow: hidden;
  transition: border-color var(--t);
}
.job-card:hover { border-color: var(--border-strong); }
.job-type { font-family: var(--font-mono); font-size: 12px; color: var(--ink-2); }
</style>
