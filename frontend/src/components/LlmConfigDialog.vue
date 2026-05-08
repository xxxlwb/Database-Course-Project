<template>
  <el-dialog v-model="show" title="LLM 模型配置" width="520">
    <div class="dialog-body">
      <div class="status-row" :class="{ active: !cfg?.mock }">
        <span class="status-dot"></span>
        <span class="status-text">
          <template v-if="cfg?.mock">Mock 模式（无 API key 或显式开启）</template>
          <template v-else>已连接 · {{ cfg?.model }}</template>
        </span>
      </div>

      <el-form label-position="top" style="margin-top:16px">
        <el-form-item label="服务商">
          <el-select v-model="form.provider" disabled style="width:100%">
            <el-option label="MiniMax" value="minimax" />
          </el-select>
          <div class="hint">本期仅支持 MiniMax；后续可扩展</div>
        </el-form-item>

        <el-form-item label="模型">
          <el-select v-model="form.model" style="width:100%">
            <el-option v-for="m in cfg?.available_models || []"
                       :key="m" :label="m" :value="m" />
          </el-select>
        </el-form-item>

        <el-form-item label="Base URL">
          <el-input v-model="form.base_url" placeholder="https://api.minimax.io/v1" />
          <div class="hint">官方主域 api.minimax.io，备用 api.minimaxi.com</div>
        </el-form-item>

        <el-form-item label="API Key">
          <el-input v-model="form.api_key" type="password" show-password
                    :placeholder="cfg?.api_key_set ? '已配置 — 留空则保持不变' : 'sk-...'" />
          <div class="hint">明文存储在后端进程内存，重启后回退到 .env</div>
        </el-form-item>

        <el-form-item>
          <el-checkbox v-model="form.mock">强制 Mock 模式（不调真 LLM）</el-checkbox>
        </el-form-item>
      </el-form>

      <el-alert v-if="error" type="error" :title="error" :closable="false" />
    </div>
    <template #footer>
      <el-button @click="show = false">取消</el-button>
      <el-button type="primary" :loading="busy" @click="save">保存并应用</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import client from '../api/client'

const show = defineModel<boolean>({ required: true })
const cfg = ref<any>(null)
const busy = ref(false)
const error = ref('')
const form = reactive({
  provider: 'minimax',
  model: 'MiniMax-M2',
  base_url: 'https://api.minimax.io/v1',
  api_key: '',
  mock: false,
})

async function load() {
  error.value = ''
  try {
    const r = await client.get('/admin/llm-config')
    cfg.value = r.data
    form.model = r.data.model
    form.base_url = r.data.base_url
    form.api_key = ''  // never echo back
    form.mock = r.data.mock && !r.data.api_key_set  // initial mock state
  } catch (e: any) {
    error.value = e.response?.data?.detail || '加载失败（仅 admin 可访问）'
  }
}

watch(show, (v) => { if (v) load() })

async function save() {
  busy.value = true
  error.value = ''
  try {
    const payload: any = {
      model: form.model,
      base_url: form.base_url,
      mock: form.mock,
    }
    // Only send api_key if user typed something (empty means keep existing)
    if (form.api_key.trim()) payload.api_key = form.api_key.trim()
    const r = await client.post('/admin/llm-config', payload)
    cfg.value = r.data
    ElMessage.success('已应用 · ' + r.data.model)
    show.value = false
  } catch (e: any) {
    error.value = e.response?.data?.detail || '保存失败'
  } finally {
    busy.value = false
  }
}
</script>

<style scoped>
.dialog-body { padding: 0 4px; }
.status-row {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 14px; border-radius: 6px;
  background: var(--surface);
  border: 1px solid var(--border);
}
.status-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: var(--ink-4);
}
.status-row.active { background: var(--purple-soft); border-color: var(--purple-light); }
.status-row.active .status-dot { background: var(--purple); box-shadow: 0 0 0 4px rgba(140,125,239,0.20); }
.status-text { font-size: 13px; color: var(--ink-2); }
.hint { font-size: 11.5px; color: var(--ink-4); margin-top: 4px; font-family: var(--font-mono); }
</style>
