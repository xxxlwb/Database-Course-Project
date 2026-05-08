<template>
  <el-container class="app">
    <el-aside width="240px" class="aside">
      <div class="brand">
        <div class="brand-mark">N</div>
        <div class="brand-text">
          <div class="brand-name">NKG</div>
          <div class="brand-sub">Narrative Knowledge Graph</div>
        </div>
      </div>
      <div class="nav-section">
        <div class="nav-label">主导航</div>
        <el-menu :default-active="route.path" router>
          <el-menu-item index="/">
            <span class="nav-icon">◇</span>
            <span>概览</span>
          </el-menu-item>
          <el-menu-item index="/topics">
            <span class="nav-icon">◈</span>
            <span>主题空间</span>
          </el-menu-item>
          <el-menu-item index="/documents">
            <span class="nav-icon">▤</span>
            <span>文档库</span>
          </el-menu-item>
        </el-menu>
      </div>
      <div class="nav-section">
        <div class="nav-label">知识图谱</div>
        <el-menu :default-active="route.path" router>
          <el-menu-item index="/entities">
            <span class="nav-icon">●</span>
            <span>实体</span>
          </el-menu-item>
          <el-menu-item index="/relationships">
            <span class="nav-icon">⇌</span>
            <span>关系</span>
          </el-menu-item>
        </el-menu>
      </div>
      <div class="nav-section">
        <div class="nav-label">运维</div>
        <el-menu :default-active="route.path" router>
          <el-menu-item index="/jobs">
            <span class="nav-icon">⚙</span>
            <span>抽取任务</span>
          </el-menu-item>
          <el-menu-item index="/audit">
            <span class="nav-icon">⌕</span>
            <span>审计日志</span>
          </el-menu-item>
          <el-menu-item v-if="auth.user?.role==='admin'" index="/dev/sql">
            <span class="nav-icon">{ }</span>
            <span>SQL 控制台</span>
          </el-menu-item>
          <el-menu-item v-if="auth.user?.role==='admin'" index="/settings">
            <span class="nav-icon">✦</span>
            <span>系统设置</span>
          </el-menu-item>
        </el-menu>
      </div>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div class="breadcrumb">{{ pageTitle }}</div>
        <div class="user-chip">
          <span class="user-name">{{ auth.user?.username }}</span>
          <span class="user-role">{{ auth.user?.role }}</span>
          <el-button text @click="logout" class="logout-btn">退出</el-button>
        </div>
      </el-header>
      <el-main class="main"><router-view /></el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const pageTitle = computed(() => {
  const map: Record<string, string> = {
    '/': '概览',
    '/topics': '主题空间',
    '/documents': '文档库',
    '/entities': '实体',
    '/relationships': '关系',
    '/jobs': '抽取任务',
    '/audit': '审计日志',
    '/dev/sql': 'SQL 控制台',
    '/settings': '系统设置',
  }
  if (map[route.path]) return map[route.path]
  if (route.path.startsWith('/topics/') && route.path.endsWith('/graph')) return '知识图谱'
  if (route.path.startsWith('/topics/')) return '主题详情'
  if (route.path.startsWith('/documents/')) return '文档详情'
  return route.path
})

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.app { height: 100vh; background: var(--cream); }
.aside {
  background: var(--surface);
  border-right: 1px solid var(--border);
  padding: var(--space-5) 0 var(--space-4);
  overflow-y: auto;
}
.brand {
  display: flex; align-items: center; gap: var(--space-3);
  padding: 0 var(--space-5) var(--space-6);
  border-bottom: 1px solid var(--border-faint);
  margin-bottom: var(--space-5);
}
.brand-mark {
  width: 36px; height: 36px;
  background: var(--rust);
  color: white;
  font-family: var(--font-display);
  font-weight: 500;
  font-size: 18px;
  display: flex; align-items: center; justify-content: center;
  border-radius: var(--radius-sm);
}
.brand-name {
  font-family: var(--font-display);
  font-size: 18px;
  font-weight: 500;
  color: var(--ink);
  line-height: 1.1;
}
.brand-sub {
  font-size: 11px;
  color: var(--ink-muted);
  letter-spacing: 0.04em;
  margin-top: 2px;
}
.nav-section { margin-bottom: var(--space-5); }
.nav-label {
  padding: 0 var(--space-5) var(--space-2);
  font-size: 10.5px;
  letter-spacing: 0.12em;
  color: var(--ink-faint);
  text-transform: uppercase;
  font-weight: 600;
}
.nav-icon {
  display: inline-block;
  width: 18px;
  margin-right: var(--space-3);
  color: var(--ink-faint);
  font-family: var(--font-mono);
  font-size: 12px;
  text-align: center;
  transition: color var(--t);
}
:deep(.el-menu-item:hover .nav-icon),
:deep(.el-menu-item.is-active .nav-icon) { color: var(--rust); }

.header {
  background: var(--cream);
  border-bottom: 1px solid var(--border);
  display: flex; justify-content: space-between; align-items: center;
  padding: 0 var(--space-6);
  height: 64px;
}
.breadcrumb {
  font-family: var(--font-display);
  font-size: 17px;
  font-weight: 500;
  color: var(--ink);
}
.user-chip {
  display: flex; align-items: center; gap: var(--space-3);
  padding: 6px var(--space-3) 6px var(--space-4);
  border: 1px solid var(--border);
  border-radius: 999px;
  background: var(--surface-elev);
}
.user-name { font-weight: 500; color: var(--ink); font-size: 13px; }
.user-role {
  font-size: 10.5px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--ink-muted);
  padding: 2px 8px;
  background: var(--surface-sunken);
  border-radius: var(--radius-sm);
}
.logout-btn { font-size: 13px; color: var(--ink-muted); padding: 4px 8px; }
.logout-btn:hover { color: var(--rust); }

.main {
  padding: var(--space-6) var(--space-7);
  background: var(--cream);
}
</style>
