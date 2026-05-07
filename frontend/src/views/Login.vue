<template>
  <div class="login-bg">
    <el-card class="card">
      <h2>NKG · 叙事知识图谱</h2>
      <el-tabs v-model="tab">
        <el-tab-pane label="登录" name="login">
          <el-form @submit.prevent="onLogin">
            <el-form-item>
              <el-input v-model="form.username" placeholder="用户名" />
            </el-form-item>
            <el-form-item>
              <el-input v-model="form.password" type="password" placeholder="密码" />
            </el-form-item>
            <el-button type="primary" native-type="submit" :loading="busy" style="width:100%">
              登录
            </el-button>
          </el-form>
        </el-tab-pane>
        <el-tab-pane label="注册" name="register">
          <el-form @submit.prevent="onRegister">
            <el-form-item><el-input v-model="form.username" placeholder="用户名（≥3字）" /></el-form-item>
            <el-form-item><el-input v-model="form.email" placeholder="邮箱" /></el-form-item>
            <el-form-item><el-input v-model="form.password" type="password" placeholder="密码（≥6字）" /></el-form-item>
            <el-button type="primary" native-type="submit" :loading="busy" style="width:100%">
              注册并登录
            </el-button>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'

const tab = ref('login')
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
.login-bg { width: 100vw; height: 100vh; background: linear-gradient(135deg, #667eea, #764ba2);
  display: flex; align-items: center; justify-content: center; }
.card { width: 400px; padding: 16px; }
h2 { text-align: center; }
</style>
