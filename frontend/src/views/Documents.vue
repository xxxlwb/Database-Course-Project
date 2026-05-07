<template>
  <div>
    <div class="bar">
      <h2>文档管理</h2>
      <el-button type="primary" @click="dlg=true">+ 上传文档</el-button>
    </div>
    <el-table :data="rows" border>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="title" label="标题" />
      <el-table-column prop="topic_id" label="Topic" width="80" />
      <el-table-column prop="status" label="状态" width="120" />
      <el-table-column prop="chunks_count" label="块数" width="80" />
      <el-table-column label="操作" width="180">
        <template #default="{row}">
          <el-button size="small" @click="$router.push(`/documents/${row.id}`)">详情</el-button>
          <el-button size="small" type="danger" @click="del(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dlg" title="上传文档" width="640">
      <el-form>
        <el-form-item label="Topic">
          <el-select v-model="form.topic_id"><el-option v-for="t in topics" :key="t.id" :label="t.name" :value="t.id" /></el-select>
        </el-form-item>
        <el-form-item label="标题"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="类型">
          <el-radio-group v-model="form.source_type"><el-radio value="text">text</el-radio><el-radio value="markdown">markdown</el-radio></el-radio-group>
        </el-form-item>
        <el-form-item label="内容"><el-input v-model="form.content" type="textarea" :rows="10" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dlg=false">取消</el-button><el-button type="primary" @click="upload">上传</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import client from '../api/client'

const rows = ref<any[]>([])
const topics = ref<any[]>([])
const dlg = ref(false)
const form = reactive({ topic_id: 0, title: '', source_type: 'text', content: '' })

async function load() {
  rows.value = (await client.get('/documents')).data
  topics.value = (await client.get('/topics')).data
}

async function upload() {
  if (!form.topic_id || !form.title || !form.content) return ElMessage.warning('请填全')
  await client.post('/documents', form)
  dlg.value = false; ElMessage.success('已上传'); await load()
}

async function del(row: any) {
  await ElMessageBox.confirm('确认删除？')
  await client.delete(`/documents/${row.id}`)
  await load(); ElMessage.success('已删除')
}

onMounted(load)
</script>
<style scoped>.bar { display: flex; justify-content: space-between; align-items: center; }</style>
