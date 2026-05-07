<template>
  <div>
    <div class="bar">
      <h2>关系管理</h2>
      <el-button type="primary" @click="dlg=true">+ 新建关系</el-button>
    </div>
    <el-table :data="rows" border>
      <el-table-column prop="id" width="60" />
      <el-table-column prop="topic_id" label="Topic" width="80" />
      <el-table-column prop="source_entity_id" label="源" width="80" />
      <el-table-column prop="target_entity_id" label="目标" width="80" />
      <el-table-column prop="relation_type" label="类型" width="120" />
      <el-table-column prop="description" label="描述" />
      <el-table-column label="操作" width="100">
        <template #default="{row}">
          <el-button size="small" type="danger" @click="del(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dlg" title="新建关系" width="500">
      <el-form>
        <el-form-item label="Topic">
          <el-select v-model="form.topic_id" @change="loadEnts"><el-option v-for="t in topics" :key="t.id" :label="t.name" :value="t.id" /></el-select>
        </el-form-item>
        <el-form-item label="源实体"><el-select v-model="form.source_entity_id" filterable><el-option v-for="e in ents" :key="e.id" :label="e.canonical_name" :value="e.id" /></el-select></el-form-item>
        <el-form-item label="目标实体"><el-select v-model="form.target_entity_id" filterable><el-option v-for="e in ents" :key="e.id" :label="e.canonical_name" :value="e.id" /></el-select></el-form-item>
        <el-form-item label="关系类型"><el-input v-model="form.relation_type" placeholder="如 知道/负责/位于" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dlg=false">取消</el-button><el-button type="primary" @click="create">创建</el-button></template>
    </el-dialog>
  </div>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import client from '../api/client'

const rows = ref<any[]>([])
const topics = ref<any[]>([])
const ents = ref<any[]>([])
const dlg = ref(false)
const form = reactive({ topic_id: 0, source_entity_id: 0, target_entity_id: 0, relation_type: '', description: '' })

async function load() { rows.value = (await client.get('/relationships')).data; topics.value = (await client.get('/topics')).data }
async function loadEnts() { ents.value = (await client.get(`/entities?topic_id=${form.topic_id}`)).data }
async function create() {
  try { await client.post('/relationships', form); dlg.value = false; await load(); ElMessage.success('已创建') }
  catch (e: any) { ElMessage.error(e.response?.data?.detail || '失败（可能跨 Topic 被触发器拒绝）') }
}
async function del(row: any) { await ElMessageBox.confirm('确认删除？'); await client.delete(`/relationships/${row.id}`); await load() }

onMounted(load)
</script>
<style scoped>.bar { display: flex; justify-content: space-between; align-items: center; }</style>
