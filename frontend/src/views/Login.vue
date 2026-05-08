<template>
  <div class="login-page">
    <div class="hero">
      <div class="hero-bg"></div>
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
          <span class="hero-tag">MySQL 8</span>
          <span class="hero-tag">FastAPI</span>
          <span class="hero-tag">Vue 3</span>
          <span class="hero-tag accent">MiniMax</span>
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
  background: var(--chrome);
  display: flex; align-items: center; justify-content: center;
  padding: var(--s-7);
  overflow: hidden;
}
.hero-bg {
  position: absolute; inset: 0;
  background:
    radial-gradient(800px 500px at 80% 0%, rgba(107,107,250,0.20), transparent 60%),
    radial-gradient(600px 400px at 20% 100%, rgba(202,201,255,0.10), transparent 60%);
  pointer-events: none;
}
.hero-grid {
  position: absolute; inset: 0;
  background-image:
    linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
  background-size: 32px 32px;
  mask-image: radial-gradient(ellipse 80% 60% at 50% 50%, black, transparent);
  pointer-events: none;
}
.hero-content { position: relative; z-index: 1; max-width: 480px; }
.hero-mark {
  display: inline-flex; align-items: center; justify-content: center;
  width: 52px; height: 52px;
  background: var(--purple);
  color: white;
  font-size: 26px; font-weight: 700; letter-spacing: -0.02em;
  border-radius: var(--r-md);
  margin-bottom: var(--s-5);
  box-shadow: 0 8px 24px rgba(107,107,250,0.40);
}
.hero-eyebrow {
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.18em;
  color: var(--ink-on-dark-3);
  margin-bottom: var(--s-3);
}
.hero-title {
  color: var(--ink-on-dark);
  font-size: 44px;
  font-weight: 700;
  line-height: 1.15;
  letter-spacing: -0.025em;
  margin: 0 0 var(--s-5);
}
.hero-title .accent { color: var(--purple-light); position: relative; }
.hero-title .accent::after {
  content: '';
  position: absolute; left: 0; right: 0; bottom: -4px;
  height: 3px; background: var(--purple); border-radius: 2px;
  opacity: 0.7;
}
.hero-desc {
  color: var(--ink-on-dark-2);
  font-size: 15px;
  line-height: 1.7;
  margin: 0 0 var(--s-6);
  max-width: 420px;
}
.hero-tags { display: flex; gap: var(--s-2); flex-wrap: wrap; }
.hero-tag {
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.04em;
  padding: 4px 10px;
  border: 1px solid var(--chrome-3);
  border-radius: var(--r-sm);
  color: var(--ink-on-dark-2);
  background: rgba(255,255,255,0.02);
}
.hero-tag.accent {
  border-color: var(--purple);
  color: var(--purple-light);
  background: rgba(107,107,250,0.12);
}

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
  box-shadow: 0 6px 18px rgba(107,107,250,0.36);
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
