<template>
  <div>
    <header class="page-head">
      <h1>系统维护</h1>
      <p class="lead">调用游标存储过程进行批量维护操作。</p>
    </header>
    <el-card style="margin-bottom:16px">
      <template #header>实体提及次数重算（调 sp_recompute_entity_mentions）</template>
      <el-button type="primary" @click="recompute" :loading="busy1">运行</el-button>
    </el-card>
    <el-card style="margin-bottom:16px">
      <template #header>归档不活跃 Topic（调 sp_archive_inactive_topics）</template>
      <div class="row">
        <el-input-number v-model="days" :min="1" :max="365" />
        <span class="suffix">天</span>
      </div>
      <el-button type="primary" @click="archive" :loading="busy2" style="margin-top:12px">运行</el-button>
    </el-card>
    <el-card>
      <template #header>实体批量改名（调 sp_propagate_entity_rename）</template>
      <div class="rename-form">
        <el-input-number v-model="renameForm.topic_id" placeholder="topic_id" />
        <el-input v-model="renameForm.pattern" placeholder="LIKE 模式 (如 'foo%')" style="width:240px" />
        <el-input v-model="renameForm.new_name" placeholder="新名称" style="width:240px" />
      </div>
      <el-button type="primary" @click="rename" :loading="busy3" style="margin-top:12px">运行</el-button>
    </el-card>
  </div>
</template>
<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import client from '../api/client'
const busy1 = ref(false); const busy2 = ref(false); const busy3 = ref(false)
const days = ref(30)
const renameForm = reactive({ topic_id: 1, pattern: '', new_name: '' })
async function recompute() { busy1.value = true; try { await client.post('/admin/recompute-mentions'); ElMessage.success('已完成') } finally { busy1.value = false } }
async function archive() { busy2.value = true; try { const r = await client.post(`/admin/archive-inactive-topics?days=${days.value}`); ElMessage.success(`归档 ${r.data.archived} 个`) } finally { busy2.value = false } }
async function rename() { busy3.value = true; try { await client.post(`/admin/propagate-rename?topic_id=${renameForm.topic_id}&pattern=${encodeURIComponent(renameForm.pattern)}&new_name=${encodeURIComponent(renameForm.new_name)}`); ElMessage.success('已完成') } finally { busy3.value = false } }
</script>
<style scoped>
.row { display: flex; align-items: center; gap: var(--space-3); }
.suffix { color: var(--ink-muted); font-size: 14px; }
.rename-form { display: flex; gap: var(--space-3); flex-wrap: wrap; align-items: center; }
</style>
