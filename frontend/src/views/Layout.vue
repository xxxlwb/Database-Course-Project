<template>
  <el-container class="app">
    <el-aside width="220px" class="aside">
      <div class="logo">NKG</div>
      <el-menu :default-active="route.path" router :collapse="false">
        <el-menu-item index="/">📊 Dashboard</el-menu-item>
        <el-menu-item index="/topics">📁 Topics</el-menu-item>
        <el-menu-item index="/documents">📄 Documents</el-menu-item>
        <el-menu-item index="/entities">🧩 Entities</el-menu-item>
        <el-menu-item index="/relationships">🔗 Relationships</el-menu-item>
        <el-menu-item index="/jobs">⚙️ Jobs</el-menu-item>
        <el-menu-item index="/audit">📋 Audit</el-menu-item>
        <el-menu-item v-if="auth.user?.role==='admin'" index="/dev/sql">💻 SQL Console</el-menu-item>
        <el-menu-item v-if="auth.user?.role==='admin'" index="/settings">⚙ Settings</el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <span>{{ auth.user?.username }} · {{ auth.user?.role }}</span>
        <el-button text @click="logout">退出</el-button>
      </el-header>
      <el-main><router-view /></el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.app { height: 100vh; }
.aside { background: #001529; color: white; }
.logo { font-size: 22px; font-weight: bold; padding: 16px; color: white; text-align: center; }
.header { display: flex; justify-content: space-between; align-items: center;
  background: #fff; border-bottom: 1px solid #eee; }
:deep(.el-menu) { background: transparent; border: none; }
:deep(.el-menu-item) { color: #ccc; }
:deep(.el-menu-item.is-active) { color: #fff; background: #1890ff; }
</style>
