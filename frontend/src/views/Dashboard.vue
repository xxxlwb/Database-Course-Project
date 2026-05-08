<template>
  <div class="dashboard fade-in">
    <header class="page-head">
      <div class="page-head-text">
        <h1>系统概览</h1>
        <p class="lead">主题、文档、实体、关系的全局指标,以及最近抽取任务进度。</p>
      </div>
    </header>

    <section class="stat-grid">
      <router-link
        v-for="(s, i) in items"
        :key="i"
        :to="s.to"
        :class="['stat-card', `t-${s.tone}`]"
        :style="{'animation-delay': i*60+'ms'}"
      >
        <div class="card-bg"></div>
        <div class="card-content">
          <div class="stat-num">{{ s.value }}</div>
          <div class="stat-name">{{ s.name }}</div>
          <div class="stat-meta">{{ s.meta }}</div>
        </div>
        <span class="card-arrow">→</span>
      </router-link>
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
  { value: stats.value.topics,   name: '主题空间', meta: 'Topics',        to: '/topics',        tone: 'red'    },
  { value: stats.value.docs,     name: '文档',     meta: 'Documents',     to: '/documents',     tone: 'purple' },
  { value: stats.value.entities, name: '实体',     meta: 'Entities',      to: '/entities',      tone: 'blue'   },
  { value: stats.value.rels,     name: '关系',     meta: 'Relationships', to: '/relationships', tone: 'pink'   },
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

/* Card base — vibrant colored block, MiniMax product-card vibe */
.stat-card {
  position: relative;
  display: block;
  padding: var(--s-5);
  border-radius: var(--r-lg);
  overflow: hidden;
  text-decoration: none;
  color: white;
  min-height: 168px;
  transition: transform var(--t), box-shadow var(--t), filter var(--t);
  cursor: pointer;
  isolation: isolate;
}
.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 32px rgba(24, 30, 37, 0.16);
  filter: brightness(1.05);
}
.stat-card:active { transform: translateY(-1px); }

/* Decorative layer with soft circles + gradient sheen for depth */
.card-bg {
  position: absolute; inset: 0;
  z-index: 0;
  background-image:
    radial-gradient(circle at 88% 14%, rgba(255,255,255,0.20) 0, rgba(255,255,255,0.20) 28px, transparent 29px),
    radial-gradient(circle at 96% 38%, rgba(255,255,255,0.10) 0, rgba(255,255,255,0.10) 14px, transparent 15px),
    radial-gradient(circle at 78% 88%, rgba(0,0,0,0.10) 0, rgba(0,0,0,0.10) 22px, transparent 23px),
    linear-gradient(135deg, rgba(255,255,255,0.18), transparent 60%);
}

.card-content { position: relative; z-index: 1; }
.card-arrow {
  position: absolute; right: var(--s-5); bottom: var(--s-4);
  z-index: 1;
  width: 28px; height: 28px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 50%;
  background: rgba(255,255,255,0.22);
  color: white; font-size: 14px; line-height: 1;
  transition: background var(--t), transform var(--t);
}
.stat-card:hover .card-arrow {
  background: rgba(255,255,255,0.36);
  transform: translateX(2px);
}

.stat-num {
  font-size: 40px; font-weight: 700;
  color: white;
  letter-spacing: -0.025em;
  line-height: 1.05;
  font-feature-settings: 'tnum';
}
.stat-name {
  margin-top: var(--s-3);
  font-size: 14px; font-weight: 600;
  color: white;
}
.stat-meta {
  margin-top: 3px;
  font-family: var(--font-mono);
  font-size: 11px;
  color: rgba(255,255,255,0.72);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

/* Tone variants — solid + slight gradient for depth */
.t-red    { background: linear-gradient(135deg, #DC4D44 0%, #C13E36 100%); }
.t-purple { background: linear-gradient(135deg, #8C7DEF 0%, #6E5FE0 100%); }
.t-blue   { background: linear-gradient(135deg, #4A6FA5 0%, #355881 100%); }
.t-pink   { background: linear-gradient(135deg, #E54998 0%, #C8367F 100%); }

/* Recent jobs section */
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

@media (max-width: 1024px) {
  .stat-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 600px) {
  .stat-grid { grid-template-columns: 1fr; }
}
</style>
