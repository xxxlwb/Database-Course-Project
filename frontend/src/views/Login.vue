<template>
  <div class="login-page">
    <div class="login-hero">
      <div class="hero-content">
        <div class="hero-mark">N</div>
        <h1 class="hero-title">叙事 · 知识图谱</h1>
        <p class="hero-sub">Narrative Knowledge Graph Management System</p>
        <div class="hero-divider"></div>
        <p class="hero-desc">
          一套面向编辑、研究与团队复盘的知识沉淀工具。
          上传文档、自动构建认知地图与跨文档分析蓝图,
          形成可查询、可合并、可视化的全局图谱。
        </p>
        <div class="hero-meta">
          <span>MySQL 8</span>
          <span class="dot">·</span>
          <span>FastAPI</span>
          <span class="dot">·</span>
          <span>Vue 3</span>
          <span class="dot">·</span>
          <span>MiniMax</span>
        </div>
      </div>
    </div>
    <div class="login-form-wrap">
      <div class="form-card">
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
            <span v-if="!busy">进入工作台 →</span>
            <span v-else>登录中…</span>
          </button>
          <p class="hint">默认演示账号:admin / editor / viewer,密码 demo123</p>
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
            <span v-if="!busy">创建账号 →</span>
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
  display: grid; grid-template-columns: 1.1fr 1fr;
  width: 100vw; height: 100vh;
  background: var(--cream);
}
.login-hero {
  background:
    radial-gradient(ellipse at 80% 20%, rgba(204, 120, 92, 0.08), transparent 60%),
    radial-gradient(ellipse at 20% 80%, rgba(232, 197, 181, 0.18), transparent 60%),
    var(--surface);
  border-right: 1px solid var(--border);
  display: flex; align-items: center; justify-content: center;
  padding: var(--space-7);
  position: relative;
  overflow: hidden;
}
.login-hero::before {
  content: '';
  position: absolute; inset: 0;
  background-image: radial-gradient(circle at 1px 1px, rgba(26,26,26,0.06) 1px, transparent 0);
  background-size: 24px 24px;
  opacity: 0.4;
  pointer-events: none;
}
.hero-content { max-width: 460px; position: relative; z-index: 1; }
.hero-mark {
  display: inline-flex; align-items: center; justify-content: center;
  width: 56px; height: 56px;
  background: var(--rust);
  color: white;
  font-family: var(--font-display);
  font-size: 28px;
  font-weight: 400;
  border-radius: var(--radius);
  margin-bottom: var(--space-5);
}
.hero-title {
  font-family: var(--font-display);
  font-size: 56px;
  font-weight: 350;
  line-height: 1.05;
  letter-spacing: -0.025em;
  margin: 0;
  color: var(--ink);
}
.hero-sub {
  font-family: var(--font-display);
  font-style: italic;
  color: var(--ink-muted);
  font-size: 17px;
  margin: var(--space-3) 0 var(--space-5);
}
.hero-divider { width: 48px; height: 2px; background: var(--rust); margin: var(--space-5) 0; }
.hero-desc {
  font-size: 15px;
  line-height: 1.7;
  color: var(--ink-secondary);
  margin: 0 0 var(--space-6);
}
.hero-meta {
  display: flex; align-items: center; gap: var(--space-2);
  font-size: 12px; color: var(--ink-muted);
  font-family: var(--font-mono);
  letter-spacing: 0.04em;
}
.hero-meta .dot { color: var(--ink-faint); }

.login-form-wrap {
  display: flex; align-items: center; justify-content: center;
  padding: var(--space-7);
}
.form-card {
  width: 100%; max-width: 380px;
}
.tab-row { display: flex; gap: var(--space-5); margin-bottom: var(--space-6); border-bottom: 1px solid var(--border); }
.tab {
  background: none; border: none; padding: 0 0 var(--space-3);
  font-family: var(--font-body); font-weight: 500;
  font-size: 15px; color: var(--ink-muted); cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: color var(--t), border-color var(--t);
  margin-bottom: -1px;
}
.tab:hover { color: var(--ink); }
.tab.active { color: var(--ink); border-bottom-color: var(--rust); }

.field { display: block; margin-bottom: var(--space-4); }
.label {
  display: block;
  font-size: 12px;
  font-weight: 500;
  letter-spacing: 0.04em;
  color: var(--ink-muted);
  text-transform: uppercase;
  margin-bottom: var(--space-2);
}
.field input {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-sm);
  background: var(--surface-elev);
  font-family: var(--font-body);
  font-size: 15px;
  color: var(--ink);
  transition: border-color var(--t), box-shadow var(--t);
}
.field input:hover { border-color: var(--ink-muted); }
.field input:focus {
  outline: none;
  border-color: var(--rust);
  box-shadow: 0 0 0 3px var(--rust-bg);
}

.primary {
  width: 100%; padding: 12px 18px;
  background: var(--rust); color: white;
  border: 1px solid var(--rust);
  border-radius: var(--radius);
  font-family: var(--font-body);
  font-weight: 500;
  font-size: 15px;
  cursor: pointer;
  margin-top: var(--space-3);
  transition: background var(--t), transform var(--t-fast), box-shadow var(--t);
}
.primary:hover:not(:disabled) {
  background: var(--rust-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow);
}
.primary:disabled { opacity: 0.6; cursor: not-allowed; }

.hint {
  margin-top: var(--space-4);
  font-size: 12px;
  color: var(--ink-muted);
  text-align: center;
  font-family: var(--font-mono);
}

@media (max-width: 800px) {
  .login-page { grid-template-columns: 1fr; }
  .login-hero { display: none; }
}
</style>
