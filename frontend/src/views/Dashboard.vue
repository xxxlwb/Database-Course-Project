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
        <div class="card-art" v-html="ART[s.tone]"></div>
        <div class="card-foot">
          <div class="foot-top">
            <div class="stat-num">{{ s.value }}</div>
            <span class="card-arrow">→</span>
          </div>
          <div class="stat-name">{{ s.name }}</div>
          <div class="stat-meta">{{ s.meta }}</div>
        </div>
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
  { value: stats.value.topics,   name: '主题空间', meta: 'TOPICS',        to: '/topics',        tone: 'red'    },
  { value: stats.value.docs,     name: '文档',     meta: 'DOCUMENTS',     to: '/documents',     tone: 'purple' },
  { value: stats.value.entities, name: '实体',     meta: 'ENTITIES',      to: '/entities',      tone: 'blue'   },
  { value: stats.value.rels,     name: '关系',     meta: 'RELATIONSHIPS', to: '/relationships', tone: 'pink'   },
])

// SVG illustrations: pastel-on-pastel, MiniMax product-card vibe
// Each viewBox 200×120, shapes echo the category (clusters / stacks / nodes / arrows)
const ART: Record<string, string> = {
  // 主题空间 → 散落聚类（topic clusters）
  red: `
    <svg viewBox="0 0 200 120" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid slice">
      <circle cx="42"  cy="62" r="38" fill="#F4B4AB" opacity="0.95"/>
      <circle cx="98"  cy="38" r="28" fill="#E58075" opacity="0.85"/>
      <circle cx="155" cy="78" r="34" fill="#DC4D44" opacity="0.92"/>
      <circle cx="78"  cy="98" r="20" fill="#FBE0DA" opacity="0.95"/>
      <circle cx="135" cy="22" r="11" fill="#FCEAE6" opacity="0.85"/>
      <circle cx="180" cy="42" r="7"  fill="#F4B4AB" opacity="0.7"/>
    </svg>`,
  // 文档 → 文档堆栈条形（document stacks）
  purple: `
    <svg viewBox="0 0 200 120" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid slice">
      <rect x="22"  y="20" width="26" height="92" rx="5" fill="#D9D2F8"/>
      <rect x="60"  y="36" width="26" height="76" rx="5" fill="#B4A8F0"/>
      <rect x="98"  y="48" width="26" height="64" rx="5" fill="#8C7DEF"/>
      <rect x="136" y="28" width="26" height="84" rx="5" fill="#C9C2F5"/>
      <rect x="174" y="56" width="20" height="56" rx="5" fill="#E8E5FF"/>
    </svg>`,
  // 实体 → 节点连线（entity graph nodes）
  blue: `
    <svg viewBox="0 0 200 120" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid slice">
      <line x1="48"  y1="38"  x2="118" y2="62"  stroke="#7FB1DA" stroke-width="2" opacity="0.55"/>
      <line x1="118" y1="62"  x2="158" y2="100" stroke="#7FB1DA" stroke-width="2" opacity="0.55"/>
      <line x1="48"  y1="38"  x2="158" y2="100" stroke="#7FB1DA" stroke-width="2" opacity="0.35"/>
      <line x1="118" y1="62"  x2="180" y2="28"  stroke="#7FB1DA" stroke-width="2" opacity="0.45"/>
      <circle cx="48"  cy="38"  r="20" fill="#A6C8E5"/>
      <circle cx="118" cy="62"  r="28" fill="#4A6FA5"/>
      <circle cx="158" cy="100" r="18" fill="#7FB1DA"/>
      <circle cx="180" cy="28"  r="11" fill="#DCE9F4"/>
    </svg>`,
  // 关系 → 箭头雪佛龙（relationship chevrons）
  pink: `
    <svg viewBox="0 0 200 120" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid slice">
      <path d="M 18 30 L 58 60 L 18 90 Z" fill="#F8C5D9" opacity="0.95"/>
      <path d="M 68 30 L 108 60 L 68 90 Z" fill="#EE5BAB" opacity="0.95"/>
      <path d="M 118 30 L 158 60 L 118 90 Z" fill="#C8367F" opacity="0.95"/>
      <circle cx="178" cy="60" r="6" fill="#F8C5D9"/>
    </svg>`,
}

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

/* Card base — two-zone (pastel art on top, white text below), MiniMax product-card vibe */
.stat-card {
  display: flex; flex-direction: column;
  border-radius: var(--r-lg);
  border: 1px solid var(--border);
  background: var(--canvas);
  overflow: hidden;
  text-decoration: none;
  color: var(--ink);
  transition: transform var(--t), box-shadow var(--t), border-color var(--t);
  cursor: pointer;
}
.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 28px rgba(24, 30, 37, 0.10);
  border-color: var(--border-strong);
}
.stat-card:active { transform: translateY(-1px); }

/* Top: pastel art zone hosting the inline SVG */
.card-art {
  height: 130px;
  display: flex; align-items: stretch; justify-content: stretch;
}
.card-art :deep(svg) { width: 100%; height: 100%; display: block; }

/* Bottom: clean white footer with stat + name + arrow */
.card-foot {
  padding: var(--s-4) var(--s-4) var(--s-4);
  border-top: 1px solid var(--border-faint);
}
.foot-top {
  display: flex; align-items: flex-start; justify-content: space-between;
  margin-bottom: 4px;
}
.stat-num {
  font-size: 32px; font-weight: 700;
  color: var(--ink);
  letter-spacing: -0.025em;
  line-height: 1;
  font-feature-settings: 'tnum';
}
.card-arrow {
  width: 26px; height: 26px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 50%;
  background: var(--surface);
  color: var(--ink-3);
  font-size: 13px;
  border: 1px solid var(--border);
  transition: background var(--t), color var(--t), transform var(--t), border-color var(--t);
}
.stat-card:hover .card-arrow {
  transform: translateX(2px);
}
.t-red:hover    .card-arrow { background: var(--red);    color: white; border-color: var(--red); }
.t-purple:hover .card-arrow { background: var(--purple); color: white; border-color: var(--purple); }
.t-blue:hover   .card-arrow { background: var(--blue);   color: white; border-color: var(--blue); }
.t-pink:hover   .card-arrow { background: var(--pink);   color: white; border-color: var(--pink); }

.stat-name { margin-top: 6px; font-size: 14px; font-weight: 600; color: var(--ink); }
.stat-meta {
  margin-top: 3px;
  font-family: var(--font-mono);
  font-size: 10.5px;
  color: var(--ink-4);
  letter-spacing: 0.08em;
}

/* Pastel tinted backgrounds for the art zone — three-shade gradients matching MiniMax cards */
.t-red    .card-art { background: linear-gradient(135deg, #FCEDE9 0%, #F8DAD3 100%); }
.t-purple .card-art { background: linear-gradient(135deg, #F1EEFC 0%, #E2DCF8 100%); }
.t-blue   .card-art { background: linear-gradient(135deg, #E8F0F8 0%, #CFDFF0 100%); }
.t-pink   .card-art { background: linear-gradient(135deg, #FAE3EC 0%, #F5C9DC 100%); }

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
