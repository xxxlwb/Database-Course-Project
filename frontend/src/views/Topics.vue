<template>
  <div>
    <div class="bar">
      <h2>主题管理</h2>
      <el-button type="primary" @click="openCreate">+ 新建主题</el-button>
    </div>
    <el-table :data="rows" border>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="名称" width="220" />
      <el-table-column prop="description" label="描述" />
      <el-table-column prop="doc_count" label="文档数" width="80" />
      <el-table-column prop="blueprint_status" label="蓝图状态" width="100">
        <template #default="{row}">
          <el-tag :type="row.blueprint_status==='ready'?'success':'info'">
            {{ row.blueprint_status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="is_archived" label="归档" width="80">
        <template #default="{row}">
          <el-tag v-if="row.is_archived" type="warning">已归档</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="240">
        <template #default="{row}">
          <el-button size="small" @click="$router.push(`/topics/${row.id}`)">详情</el-button>
          <el-button size="small" @click="$router.push(`/topics/${row.id}/graph`)">图谱</el-button>
          <el-button size="small" type="warning" @click="archive(row)">
            {{ row.is_archived ? '取消归档' : '归档' }}
          </el-button>
          <el-button size="small" type="danger" @click="del(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dlg" title="新建主题">
      <el-form>
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dlg=false">取消</el-button>
        <el-button type="primary" @click="create">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import client from '../api/client'

const rows = ref<any[]>([])
const dlg = ref(false)
const form = reactive({ name: '', description: '' })

async function load() {
  rows.value = (await client.get('/topics')).data
}

function openCreate() {
  form.name = ''; form.description = ''; dlg.value = true
}

async function create() {
  try { await client.post('/topics', form); dlg.value = false; await load(); ElMessage.success('已创建') }
  catch (e: any) { ElMessage.error(e.response?.data?.detail || '失败') }
}

async function archive(row: any) {
  await client.patch(`/topics/${row.id}`, { is_archived: !row.is_archived })
  await load()
}

async function del(row: any) {
  await ElMessageBox.confirm('确认删除？将同时删除其下文档/实体/关系', '危险', { type: 'warning' })
  await client.delete(`/topics/${row.id}`)
  await load()
  ElMessage.success('已删除')
}

onMounted(load)
</script>

<style scoped>.bar { display: flex; justify-content: space-between; align-items: center; }</style>
