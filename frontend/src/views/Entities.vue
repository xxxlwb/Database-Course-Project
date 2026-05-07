<template>
  <div>
    <div class="bar">
      <h2>实体管理</h2>
      <div>
        <el-input v-model="q" placeholder="搜索实体名" style="width:200px" @input="load" />
        <el-button type="primary" @click="mergeDlg=true" style="margin-left:8px">⚙ 合并实体</el-button>
      </div>
    </div>
    <el-table :data="rows" border>
      <el-table-column prop="id" width="60" />
      <el-table-column prop="canonical_name" label="名称" />
      <el-table-column prop="entity_type" label="类型" width="100" />
      <el-table-column prop="topic_id" label="Topic" width="80" />
      <el-table-column prop="mention_count" label="提及" width="80" />
      <el-table-column prop="description" label="描述" />
      <el-table-column label="操作" width="180">
        <template #default="{row}">
          <el-button size="small" @click="showAliases(row)">别名</el-button>
          <el-button size="small" type="danger" @click="del(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <EntityMergeDialog v-model="mergeDlg" :entities="rows" @merged="load" />

    <el-dialog v-model="aliasDlg" title="别名">
      <el-table :data="aliases" size="small"><el-table-column prop="alias" /><el-table-column prop="source" width="100" /><el-table-column prop="confidence" width="100" /></el-table>
      <el-input v-model="newAlias" placeholder="添加别名" /><el-button @click="addAlias">添加</el-button>
    </el-dialog>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import client from '../api/client'
import EntityMergeDialog from '../components/EntityMergeDialog.vue'

const rows = ref<any[]>([])
const q = ref('')
const mergeDlg = ref(false)
const aliasDlg = ref(false)
const aliases = ref<any[]>([])
const currentEid = ref<number>()
const newAlias = ref('')

async function load() { rows.value = (await client.get(`/entities?q=${encodeURIComponent(q.value)}`)).data }
async function showAliases(row: any) { currentEid.value = row.id; aliases.value = (await client.get(`/entities/${row.id}/aliases`)).data; aliasDlg.value = true }
async function addAlias() { await client.post(`/entities/${currentEid.value}/aliases`, { alias: newAlias.value }); aliases.value = (await client.get(`/entities/${currentEid.value}/aliases`)).data; newAlias.value = '' }
async function del(row: any) { await ElMessageBox.confirm('确认删除？'); await client.delete(`/entities/${row.id}`); await load(); ElMessage.success('已删除') }

onMounted(load)
</script>
<style scoped>.bar { display: flex; justify-content: space-between; align-items: center; }</style>
