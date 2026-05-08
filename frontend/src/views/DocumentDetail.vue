<template>
  <div v-if="doc">
    <header class="page-head">
      <div class="page-head-text">
        <h1>{{ doc.title }}
          <span :class="['status-pill', `s-${doc.status}`]" style="margin-left:8px;vertical-align:middle">
            {{ doc.status }}
          </span>
        </h1>
        <p class="lead">文档详情:查看原文、切块结果与 LLM 生成的认知地图。</p>
      </div>
    </header>
    <el-tabs>
      <el-tab-pane label="原文">
        <pre style="white-space:pre-wrap">{{ doc.content }}</pre>
      </el-tab-pane>
      <el-tab-pane label="切块">
        <el-table :data="chunks" size="small">
          <el-table-column prop="chunk_index" label="#" width="60" />
          <el-table-column prop="content" label="内容" />
          <el-table-column prop="token_count" label="长度" width="80" />
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="认知地图">
        <el-button v-if="!cogmap" type="primary" @click="genCog">生成认知地图</el-button>
        <pre v-if="cogmap" style="margin-top:12px">{{ JSON.stringify(cogmap, null, 2) }}</pre>
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
const did = Number(route.params.id)
const doc = ref<any>(null)
const chunks = ref<any[]>([])
const cogmap = ref<any>(null)

async function load() {
  doc.value = (await client.get(`/documents/${did}`)).data
  chunks.value = (await client.get(`/documents/${did}/chunks`)).data
  try { cogmap.value = (await client.get(`/documents/${did}/cognitive-map`)).data } catch { cogmap.value = null }
}

async function genCog() {
  try { cogmap.value = (await client.post(`/documents/${did}/cognitive-map`)).data; ElMessage.success('已生成') }
  catch (e: any) { ElMessage.error(e.response?.data?.detail || '失败') }
}

onMounted(load)
</script>
