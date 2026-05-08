<template>
  <el-container class="app">
    <el-aside width="240px" class="aside">
      <div class="brand">
        <button class="brand-mark" @click="openCfg" type="button" :title="brandTitle">
          <span class="mark-glyph">{{ modelLetter }}</span>
        </button>
        <div class="brand-text">
          <div class="brand-name">NKG</div>
          <div class="brand-sub">Knowledge Graph</div>
        </div>
      </div>

      <div class="aside-menu">
        <div class="nav-section">
          <div class="nav-label">主导航</div>
          <el-menu :default-active="route.path" router>
            <el-menu-item index="/"><span class="nav-glyph">⌂</span><span>概览</span></el-menu-item>
            <el-menu-item index="/topics"><span class="nav-glyph">▦</span><span>主题空间</span></el-menu-item>
            <el-menu-item index="/documents"><span class="nav-glyph">▤</span><span>文档库</span></el-menu-item>
          </el-menu>
        </div>

        <div class="nav-section">
          <div class="nav-label">知识图谱</div>
          <el-menu :default-active="route.path" router>
            <el-menu-item index="/entities"><span class="nav-glyph">●</span><span>实体</span></el-menu-item>
            <el-menu-item index="/relationships"><span class="nav-glyph">⇌</span><span>关系</span></el-menu-item>
          </el-menu>
        </div>

        <div class="nav-section">
          <div class="nav-label">运维</div>
          <el-menu :default-active="route.path" router>
            <el-menu-item index="/jobs"><span class="nav-glyph">⚙</span><span>抽取任务</span></el-menu-item>
            <el-menu-item index="/audit"><span class="nav-glyph">⌕</span><span>审计日志</span></el-menu-item>
            <el-menu-item v-if="auth.user?.role==='admin'" index="/dev/sql"><span class="nav-glyph">{ }</span><span>SQL 控制台</span></el-menu-item>
            <el-menu-item v-if="auth.user?.role==='admin'" index="/settings"><span class="nav-glyph">✦</span><span>系统设置</span></el-menu-item>
          </el-menu>
        </div>
      </div>

      <div class="aside-footer">
        <div class="footer-line">v0.1 · NKG</div>
        <div class="footer-line subtle">Powered by MiniMax</div>
      </div>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="breadcrumb">{{ pageTitle }}</div>
        <div class="header-right">
          <div class="user-chip">
            <div class="user-avatar">{{ initial }}</div>
            <div class="user-meta">
              <span class="user-name">{{ auth.user?.username }}</span>
              <span class="user-role">{{ auth.user?.role }}</span>
            </div>
          </div>
          <button class="logout" @click="logout">退出</button>
        </div>
      </el-header>
      <el-main class="main"><router-view /></el-main>
    </el-container>
    <LlmConfigDialog v-model="cfgOpen" />
  </el-container>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'
import client from '../api/client'
import LlmConfigDialog from '../components/LlmConfigDialog.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const initial = computed(() => (auth.user?.username || '?').charAt(0).toUpperCase())

const cfgOpen = ref(false)
const currentModel = ref('')
const modelLetter = computed(() => {
  // First letter of provider/model name (M for MiniMax, future: D for DeepSeek, G for Gemini, O for OpenAI)
  return (currentModel.value || 'minimax').charAt(0).toUpperCase()
})
const brandTitle = computed(() =>
  auth.user?.role === 'admin'
    ? '点击配置 LLM'
    : '当前模型: MiniMax · 仅 admin 可切换'
)

async function loadModel() {
  if (auth.user?.role !== 'admin') {
    currentModel.value = 'MiniMax'  // non-admin sees the letter but can't change
    return
  }
  try {
    const r = await client.get('/admin/llm-config')
    currentModel.value = r.data.model
  } catch {
    currentModel.value = 'MiniMax'
  }
}

function openCfg() {
  if (auth.user?.role !== 'admin') {
    ElMessage.info('仅 admin 可切换模型')
    return
  }
  cfgOpen.value = true
}

onMounted(loadModel)

// Re-load after dialog closes (so the letter reflects the new model immediately)
watch(cfgOpen, (v) => { if (!v) loadModel() })

const pageTitle = computed(() => {
  const p = route.path
  if (p === '/') return '概览'
  if (p === '/topics') return '主题空间'
  if (p === '/documents') return '文档库'
  if (p === '/entities') return '实体'
  if (p === '/relationships') return '关系'
  if (p === '/jobs') return '抽取任务'
  if (p === '/audit') return '审计日志'
  if (p === '/dev/sql') return 'SQL 控制台'
  if (p === '/settings') return '系统设置'
  if (/^\/topics\/\d+\/graph$/.test(p)) return '知识图谱'
  if (/^\/topics\/\d+$/.test(p)) return '主题详情'
  if (/^\/documents\/\d+$/.test(p)) return '文档详情'
  return p
})

function logout() { auth.logout(); router.push('/login') }
</script>

<style scoped>
.app { height: 100vh; background: var(--canvas); }

.aside {
  background: var(--chrome);
  border-right: 1px solid var(--chrome-border);
  display: flex; flex-direction: column;
  padding: var(--s-5) 0;
  overflow-y: auto;
}

.brand {
  display: flex; align-items: center; gap: var(--s-3);
  padding: 0 var(--s-5) var(--s-6);
  border-bottom: 1px solid var(--chrome-border);
  margin-bottom: var(--s-4);
}
.brand-mark {
  width: 38px; height: 38px;
  background:
    radial-gradient(circle at 25% 22%, rgba(255,200,180,0.55), transparent 55%),
    linear-gradient(135deg, #F26354 0%, #DC4D44 48%, #B8362E 100%);
  display: flex; align-items: center; justify-content: center;
  border-radius: var(--r-md);
  position: relative;
  border: none;
  cursor: pointer;
  padding: 0;
  box-shadow: inset 0 -1px 0 rgba(0,0,0,0.10);
  transition: transform var(--t), box-shadow var(--t);
}
.brand-mark:hover {
  transform: translateY(-1px);
  box-shadow:
    inset 0 -1px 0 rgba(0,0,0,0.10),
    0 8px 22px rgba(220,77,68,0.45);
}
.brand-mark:active { transform: translateY(0); }
.brand-mark::after {
  content: '';
  position: absolute; inset: 0;
  border-radius: var(--r-md);
  background: linear-gradient(135deg, rgba(255,255,255,0.16), transparent 60%);
  pointer-events: none;
}
.mark-glyph {
  color: white; font-weight: 700; font-size: 18px;
  letter-spacing: -0.02em;
}
.brand-name {
  color: var(--ink-on-dark);
  font-size: 17px; font-weight: 700;
  line-height: 1.1; letter-spacing: -0.01em;
}
.brand-sub {
  color: var(--ink-on-dark-3);
  font-size: 11px;
  margin-top: 3px;
  font-family: var(--font-mono);
  letter-spacing: 0.02em;
}

.aside-menu { flex: 1; }
.nav-section { margin-bottom: var(--s-4); }
.nav-label {
  padding: 0 var(--s-5) var(--s-2);
  font-size: 10.5px;
  letter-spacing: 0.14em;
  color: var(--ink-on-dark-3);
  text-transform: uppercase;
  font-weight: 600;
}
.nav-glyph {
  display: inline-block;
  width: 18px;
  margin-right: var(--s-3);
  color: var(--ink-on-dark-3);
  font-family: var(--font-mono);
  font-size: 12px;
  text-align: center;
  transition: color var(--t);
}
.aside-menu :deep(.el-menu-item):hover .nav-glyph,
.aside-menu :deep(.el-menu-item.is-active) .nav-glyph { color: var(--purple); }

.aside-footer {
  padding: var(--s-4) var(--s-5) 0;
  border-top: 1px solid var(--chrome-border);
  margin-top: var(--s-4);
}
.footer-line { color: var(--ink-on-dark-3); font-size: 11px; font-family: var(--font-mono); }
.footer-line.subtle { opacity: 0.6; margin-top: 2px; }

.header {
  background: var(--canvas);
  border-bottom: 1px solid var(--border);
  display: flex; justify-content: space-between; align-items: center;
  padding: 0 var(--s-6);
  height: 60px;
  flex-shrink: 0;
}
.breadcrumb { font-size: 16px; font-weight: 600; color: var(--ink); }
.header-right { display: flex; align-items: center; gap: var(--s-3); }

.user-chip {
  display: flex; align-items: center; gap: var(--s-2);
  padding: 4px var(--s-3) 4px 4px;
  border: 1px solid var(--border);
  border-radius: 999px;
  background: var(--surface);
  transition: border-color var(--t), background var(--t);
}
.user-chip:hover { border-color: var(--border-strong); background: var(--canvas); }
.user-avatar {
  width: 28px; height: 28px;
  border-radius: 50%;
  background: var(--chrome);
  color: white; font-size: 12px; font-weight: 600;
  display: flex; align-items: center; justify-content: center;
  letter-spacing: -0.01em;
}
.user-meta { display: flex; align-items: center; gap: var(--s-2); }
.user-name { font-weight: 500; font-size: 13px; color: var(--ink); }
.user-role {
  font-size: 10.5px; font-weight: 600;
  letter-spacing: 0.06em; text-transform: uppercase;
  color: var(--purple-deep);
  padding: 2px 6px;
  background: var(--purple-soft);
  border-radius: var(--r-sm);
}

.logout {
  background: transparent;
  border: 1px solid var(--border-strong);
  color: var(--ink-2);
  font-family: var(--font);
  font-size: 13px; font-weight: 500;
  padding: 6px 14px;
  border-radius: var(--r);
  cursor: pointer;
  transition: all var(--t);
}
.logout:hover {
  background: var(--purple);
  border-color: var(--purple);
  color: white;
}

.main {
  padding: var(--s-6) var(--s-7);
  background: var(--canvas);
  overflow-y: auto;
}
</style>
