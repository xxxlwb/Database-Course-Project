<template>
  <div class="login-page">
    <div class="hero">
      <!-- Decorative SVG layer: M2-her style overlapping shapes + yellow balloon -->
      <svg class="hero-art" viewBox="0 0 600 800" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
        <!-- soft cream overlapping ovals (top) -->
        <ellipse cx="120" cy="-40" rx="280" ry="200" fill="#FFD7C5" opacity="0.18"/>
        <ellipse cx="520" cy="80"  rx="240" ry="180" fill="#FF8A6E" opacity="0.22"/>
        <!-- big translucent center swirl -->
        <circle cx="200" cy="380" r="240" fill="#FF7A66" opacity="0.16"/>
        <circle cx="450" cy="420" r="280" fill="#7A1F1A" opacity="0.30"/>
        <circle cx="320" cy="500" r="180" fill="#FFB7A0" opacity="0.14"/>
        <!-- bottom dark anchor -->
        <ellipse cx="180" cy="780" rx="320" ry="180" fill="#5A140F" opacity="0.40"/>
        <ellipse cx="540" cy="820" rx="260" ry="160" fill="#3A0B08" opacity="0.30"/>
        <!-- gold balloon accent (M2-her signature element) -->
        <line x1="475" y1="120" x2="510" y2="60" stroke="#FFD27D" stroke-width="2" opacity="0.85"/>
        <circle cx="510" cy="58" r="6" fill="#FFD27D"/>
        <!-- cream curve sweep -->
        <path d="M -40 600 Q 180 540 380 620 T 700 580" stroke="#FFE6CC" stroke-width="1.5" fill="none" opacity="0.45"/>
        <!-- small dot cluster -->
        <circle cx="80"  cy="700" r="3" fill="#FFE6CC" opacity="0.7"/>
        <circle cx="100" cy="720" r="2" fill="#FFE6CC" opacity="0.5"/>
        <circle cx="60"  cy="730" r="2" fill="#FFE6CC" opacity="0.6"/>
      </svg>
      <div class="hero-grid"></div>
      <div class="hero-content">
        <div class="hero-mark">M</div>
        <div class="hero-eyebrow">NARRATIVE KNOWLEDGE GRAPH</div>
        <h1 class="hero-title">把散落的笔记<br/>编成一张<span class="accent">活的图谱</span></h1>
        <p class="hero-desc">
          上传文档,自动抽取人/事/项目/概念,跨文档构建认知地图与全局蓝图。
          可视化、可合并、可追溯,每一次写入都被审计。
        </p>
        <div class="hero-tags">
          <span class="hero-tag t-mysql"><span class="dot"></span>MySQL 8</span>
          <span class="hero-tag t-api"><span class="dot"></span>FastAPI</span>
          <span class="hero-tag t-vue"><span class="dot"></span>Vue 3</span>
          <span class="hero-tag t-mm"><span class="dot"></span>MiniMax</span>
        </div>
      </div>
    </div>
    <div class="form-wrap">
      <div class="form-card">
        <div class="form-head">
          <h2>欢迎回来</h2>
          <p>登录以访问你的知识图谱工作台</p>
        </div>
        <div class="tab-row">
          <button :class="['tab', tab==='login' && 'active']" @click="tab='login'">登录</button>
          <button :class="['tab', tab==='register' && 'active']" @click="tab='register'">注册</button>
        </div>
        <form v-if="tab==='login'" @submit.prevent="onLogin">
          <label class="field">
            <span class="label">用户名</span>
            <input v-model="form.username" placeholder="admin" autofocus />
          </label>
          <label class="field">
            <span class="label">密码</span>
            <input v-model="form.password" type="password" placeholder="demo123" />
          </label>
          <button class="primary" type="submit" :disabled="busy">
            <span v-if="!busy">登录</span>
            <span v-else>登录中…</span>
          </button>
          <p class="hint">演示账号 admin / editor / viewer · 密码 demo123</p>
        </form>
        <form v-else @submit.prevent="onRegister">
          <label class="field">
            <span class="label">用户名</span>
            <input v-model="form.username" placeholder="至少 3 字符" />
          </label>
          <label class="field">
            <span class="label">邮箱</span>
            <input v-model="form.email" type="email" placeholder="you@example.com" />
          </label>
          <label class="field">
            <span class="label">密码</span>
            <input v-model="form.password" type="password" placeholder="至少 6 字符" />
          </label>
          <button class="primary" type="submit" :disabled="busy">
            <span v-if="!busy">创建账号</span>
            <span v-else>注册中…</span>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'

const tab = ref<'login' | 'register'>('login')
const form = reactive({ username: '', email: '', password: '' })
const busy = ref(false)
const router = useRouter()
const auth = useAuthStore()

async function onLogin() {
  if (!form.username || !form.password) return ElMessage.warning('请填用户名和密码')
  busy.value = true
  try { await auth.login(form.username, form.password); router.push('/') }
  catch (e: any) { ElMessage.error(e.response?.data?.detail || '登录失败') }
  finally { busy.value = false }
}
async function onRegister() {
  if (!form.username || !form.email || !form.password) return ElMessage.warning('请填全')
  busy.value = true
  try { await auth.register(form.username, form.email, form.password); router.push('/') }
  catch (e: any) { ElMessage.error(e.response?.data?.detail || '注册失败') }
  finally { busy.value = false }
}
</script>

<style scoped>
.login-page {
  display: grid; grid-template-columns: 1.05fr 1fr;
  width: 100vw; height: 100vh;
  background: var(--canvas);
}

.hero {
  position: relative;
  /* Deeper coral-to-burgundy base — leaves room for decorative SVG to pop */
  background:
    radial-gradient(ellipse 80% 70% at 30% 20%, #E0584C 0%, transparent 60%),
    radial-gradient(ellipse 60% 70% at 70% 90%, #5A140F 0%, transparent 60%),
    linear-gradient(160deg, #C73E36 0%, #8B2620 100%);
  display: flex; align-items: center; justify-content: center;
  padding: var(--s-7);
  overflow: hidden;
}
.hero-art {
  position: absolute; inset: 0;
  width: 100%; height: 100%;
  pointer-events: none;
  z-index: 0;
}
.hero-grid {
  position: absolute; inset: 0;
  background-image:
    linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px);
  background-size: 32px 32px;
  mask-image: radial-gradient(ellipse 60% 50% at 50% 50%, black, transparent);
  pointer-events: none;
  z-index: 0;
}
.hero-content { position: relative; z-index: 1; max-width: 480px; }
.hero-mark {
  display: inline-flex; align-items: center; justify-content: center;
  width: 52px; height: 52px;
  background: white;
  color: var(--red);
  font-size: 26px; font-weight: 700; letter-spacing: -0.02em;
  border-radius: var(--r-md);
  margin-bottom: var(--s-5);
  box-shadow: 0 8px 24px rgba(70,15,15,0.45), inset 0 -2px 0 rgba(0,0,0,0.06);
}
.hero-eyebrow {
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.18em;
  color: rgba(255,255,255,0.78);
  margin-bottom: var(--s-3);
}
.hero-title {
  color: white;
  font-size: 44px;
  font-weight: 700;
  line-height: 1.15;
  letter-spacing: -0.025em;
  margin: 0 0 var(--s-5);
  text-shadow: 0 2px 16px rgba(70,15,15,0.40);
}
.hero-title .accent { color: #FFE4A8; position: relative; }
.hero-title .accent::after {
  content: '';
  position: absolute; left: 0; right: 0; bottom: -4px;
  height: 3px; background: #FFD27D; border-radius: 2px;
  opacity: 0.85;
}
.hero-desc {
  color: rgba(255,255,255,0.92);
  font-size: 15px;
  line-height: 1.7;
  margin: 0 0 var(--s-6);
  max-width: 420px;
}

/* Tags: hover micro-interaction with per-tech accent color */
.hero-tags { display: flex; gap: var(--s-2); flex-wrap: wrap; }
.hero-tag {
  display: inline-flex; align-items: center; gap: 6px;
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.04em;
  padding: 5px 11px 5px 9px;
  border: 1px solid rgba(255,255,255,0.30);
  border-radius: var(--r-sm);
  color: rgba(255,255,255,0.85);
  background: rgba(255,255,255,0.06);
  backdrop-filter: blur(4px);
  cursor: default;
  transition:
    background var(--t),
    border-color var(--t),
    color var(--t),
    transform var(--t),
    box-shadow var(--t);
}
.hero-tag .dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: rgba(255,255,255,0.55);
  transition: background var(--t), box-shadow var(--t), transform var(--t);
}

/* Per-tech hover accents */
.hero-tag.t-mysql:hover {
  background: rgba(0,117,143,0.22);
  border-color: #00758F;
  color: #B8E5EE;
  transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(0,117,143,0.35);
}
.hero-tag.t-mysql:hover .dot { background: #00758F; box-shadow: 0 0 0 4px rgba(0,117,143,0.30); }

.hero-tag.t-api:hover {
  background: rgba(0,150,136,0.22);
  border-color: #009688;
  color: #9FE5DD;
  transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(0,150,136,0.35);
}
.hero-tag.t-api:hover .dot { background: #009688; box-shadow: 0 0 0 4px rgba(0,150,136,0.30); }

.hero-tag.t-vue:hover {
  background: rgba(65,184,131,0.22);
  border-color: #41B883;
  color: #B5E6CE;
  transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(65,184,131,0.35);
}
.hero-tag.t-vue:hover .dot { background: #41B883; box-shadow: 0 0 0 4px rgba(65,184,131,0.30); }

.hero-tag.t-mm {
  border-color: #FFD27D;
  color: #FFE4A8;
  background: rgba(255,210,125,0.14);
}
.hero-tag.t-mm .dot { background: #FFD27D; }
.hero-tag.t-mm:hover {
  background: rgba(255,210,125,0.26);
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(255,210,125,0.45);
}
.hero-tag.t-mm:hover .dot { box-shadow: 0 0 0 4px rgba(255,210,125,0.40); transform: scale(1.15); }

.form-wrap {
  display: flex; align-items: center; justify-content: center;
  padding: var(--s-7);
  background: var(--canvas);
}
.form-card { width: 100%; max-width: 380px; }
.form-head { margin-bottom: var(--s-6); }
.form-head h2 { margin: 0; font-size: 24px; font-weight: 700; letter-spacing: -0.02em; }
.form-head p { color: var(--ink-3); font-size: 14px; margin: var(--s-2) 0 0; }

.tab-row { display: flex; gap: var(--s-5); margin-bottom: var(--s-5); border-bottom: 1px solid var(--border); }
.tab {
  background: none; border: none; padding: 0 0 var(--s-3);
  font-family: var(--font);
  font-weight: 500; font-size: 14px;
  color: var(--ink-3); cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: color var(--t), border-color var(--t);
  margin-bottom: -1px;
}
.tab:hover { color: var(--ink); }
.tab.active { color: var(--purple); border-bottom-color: var(--purple); }

.field { display: block; margin-bottom: var(--s-4); }
.label {
  display: block;
  font-size: 12px; font-weight: 600;
  letter-spacing: 0.04em;
  color: var(--ink-3);
  text-transform: uppercase;
  margin-bottom: var(--s-2);
}
.field input {
  width: 100%;
  padding: 10px 14px; height: 38px;
  border: 1px solid var(--border-strong);
  border-radius: var(--r);
  background: var(--canvas);
  font-family: var(--font);
  font-size: 14px; color: var(--ink);
  transition: border-color var(--t), box-shadow var(--t);
}
.field input:hover { border-color: var(--ink-3); }
.field input:focus {
  outline: none;
  border-color: var(--purple);
  box-shadow: var(--shadow-glow);
}

.primary {
  width: 100%;
  padding: 11px 18px; height: 42px;
  background: var(--purple);
  color: white;
  border: 1px solid var(--purple);
  border-radius: var(--r);
  font-family: var(--font);
  font-weight: 600; font-size: 14px;
  cursor: pointer;
  margin-top: var(--s-3);
  transition: background var(--t), box-shadow var(--t);
  letter-spacing: 0.01em;
}
.primary:hover:not(:disabled) {
  background: var(--purple-hover);
  box-shadow: 0 6px 18px rgba(140,125,239,0.36);
}
.primary:disabled { opacity: 0.55; cursor: not-allowed; }

.hint {
  margin-top: var(--s-4);
  font-size: 12px;
  color: var(--ink-3);
  text-align: center;
  font-family: var(--font-mono);
}

@media (max-width: 800px) {
  .login-page { grid-template-columns: 1fr; }
  .hero { display: none; }
}
</style>
