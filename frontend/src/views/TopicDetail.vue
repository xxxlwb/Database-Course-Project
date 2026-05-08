<template>
  <div v-if="topic">
    <header class="page-head">
      <h1>{{ topic.name }}
        <span :class="['status-pill', topic.blueprint_status==='ready'?'s-completed':'s-pending']" style="margin-left:8px;vertical-align:middle">
          {{ topic.blueprint_status }}
        </span>
      </h1>
      <p class="lead">{{ topic.description || '主题详情:管理本主题的文档、实体、关系与蓝图。' }}</p>
    </header>

    <el-tabs v-model="tab">
      <el-tab-pane label="文档" name="docs">
        <el-button type="primary" size="small" @click="$router.push(`/documents?topic_id=${topic.id}`)">
          管理本 Topic 文档
        </el-button>
        <el-table :data="docs" size="small" style="margin-top:12px">
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="title" label="标题" />
          <el-table-column prop="status" label="状态" width="120">
            <template #default="{row}">
              <span :class="['status-pill', `s-${row.status}`]">{{ row.status }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="chunks_count" label="块数" width="80" />
          <el-table-column label="操作" width="120">
            <template #default="{row}">
              <el-button size="small" @click="$router.push(`/documents/${row.id}`)">查看</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="实体" name="entities">
        <el-table :data="entities" size="small">
          <el-table-column prop="canonical_name" label="名称" />
          <el-table-column prop="entity_type" label="类型" width="120">
            <template #default="{row}"><el-tag>{{ row.entity_type }}</el-tag></template>
          </el-table-column>
          <el-table-column prop="mention_count" label="提及次数" width="120" />
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="关系" name="rels">
        <el-table :data="rels" size="small">
          <el-table-column prop="relation_type" label="类型" width="140">
            <template #default="{row}"><el-tag>{{ row.relation_type }}</el-tag></template>
          </el-table-column>
          <el-table-column prop="source_entity_id" label="源" width="80" />
          <el-table-column prop="target_entity_id" label="目标" width="80" />
          <el-table-column prop="description" label="描述" />
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="蓝图" name="blueprint">
        <el-button type="primary" size="small" @click="genBlueprint">生成/重建</el-button>
        <pre v-if="blueprint" style="margin-top:12px">{{ JSON.stringify(blueprint, null, 2) }}</pre>
        <el-empty v-else description="尚无蓝图" />
      </el-tab-pane>

      <el-tab-pane label="抽取" name="extract">
        <el-alert title="LLM 抽取" type="info" show-icon />
        <el-button type="primary" style="margin-top:12px" @click="extract">运行抽取</el-button>
        <pre v-if="extractResult">{{ JSON.stringify(extractResult, null, 2) }}</pre>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import client from '../api/client'

const route = useRoute()
const tid = Number(route.params.id)
const tab = ref('docs')
const topic = ref<any>(null)
const docs = ref<any[]>([])
const entities = ref<any[]>([])
const rels = ref<any[]>([])
const blueprint = ref<any>(null)
const extractResult = ref<any>(null)

async function load() {
  topic.value = (await client.get(`/topics/${tid}`)).data
  docs.value = (await client.get(`/documents?topic_id=${tid}`)).data
  entities.value = (await client.get(`/entities?topic_id=${tid}`)).data
  rels.value = (await client.get(`/relationships?topic_id=${tid}`)).data
  try { blueprint.value = (await client.get(`/topics/${tid}/blueprint`)).data } catch { blueprint.value = null }
}

async function genBlueprint() {
  try { blueprint.value = (await client.post(`/topics/${tid}/blueprint`)).data; ElMessage.success('已生成') }
  catch (e: any) { ElMessage.error(e.response?.data?.detail || '失败') }
}

async function extract() {
  try { extractResult.value = (await client.post(`/topics/${tid}/extract`)).data; await load() }
  catch (e: any) { ElMessage.error(e.response?.data?.detail || '失败') }
}

onMounted(load)
</script>
