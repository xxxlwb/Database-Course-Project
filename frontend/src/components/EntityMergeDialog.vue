<template>
  <el-dialog v-model="show" title="合并实体" width="500">
    <el-alert type="warning" title="合并不可逆：被合并实体将被删除，所有关系/映射/别名迁移到保留实体" />
    <el-form style="margin-top:12px">
      <el-form-item label="保留">
        <el-select v-model="keepId" filterable>
          <el-option v-for="e in entities" :key="e.id" :label="`${e.id} · ${e.canonical_name}`" :value="e.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="合并">
        <el-select v-model="mergeId" filterable>
          <el-option v-for="e in entities" :key="e.id" :label="`${e.id} · ${e.canonical_name}`" :value="e.id" />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="show=false">取消</el-button>
      <el-button type="primary" @click="confirm" :disabled="!keepId || !mergeId || keepId===mergeId">确认合并</el-button>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, defineModel, defineProps, defineEmits } from 'vue'
import { ElMessage } from 'element-plus'
import client from '../api/client'
const show = defineModel<boolean>({ required: true })
defineProps<{ entities: any[] }>()
const emit = defineEmits(['merged'])
const keepId = ref<number>()
const mergeId = ref<number>()
async function confirm() {
  try { await client.post('/entities/merge', { keep_id: keepId.value, merge_id: mergeId.value })
        ElMessage.success('合并成功'); show.value = false; emit('merged') }
  catch (e: any) { ElMessage.error(e.response?.data?.detail || '失败') }
}
</script>
