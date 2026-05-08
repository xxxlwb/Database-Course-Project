<template>
  <div>
    <header class="page-head">
      <div class="page-head-text">
        <h1>实体</h1>
        <p class="lead">图谱中的核心节点。支持别名管理与跨实体合并。</p>
      </div>
      <div class="page-head-actions toolbar">
        <el-input v-model="q" placeholder="搜索实体名" style="width:220px" @input="load" />
        <el-button type="primary" @click="mergeDlg=true">⚙ 合并实体</el-button>
      </div>
    </header>
    <el-table :data="rows" border>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="canonical_name" label="名称" />
      <el-table-column prop="entity_type" label="类型" width="120">
        <template #default="{row}">
          <el-tag>{{ row.entity_type }}</el-tag>
        </template>
      </el-table-column>
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
      <el-table :data="aliases" size="small">
        <el-table-column prop="alias" label="别名" />
        <el-table-column prop="source" label="来源" width="100" />
        <el-table-column prop="confidence" label="置信度" width="100" />
      </el-table>
      <div class="alias-add">
        <el-input v-model="newAlias" placeholder="添加别名" />
        <el-button type="primary" @click="addAlias">添加</el-button>
      </div>
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
<style scoped>
.toolbar { display: flex; gap: var(--s-3); align-items: center; }
.alias-add { display: flex; gap: var(--s-3); margin-top: var(--s-4); }
</style>
