<template>
  <div>
    <header class="page-head">
      <h1>知识图谱 · {{ topicName }}</h1>
      <p class="lead">主题内的实体节点与语义关系网络。可拖拽、缩放与平移。</p>
    </header>
    <div class="chart-card">
      <v-chart ref="chartRef" :option="option" autoresize style="height:600px" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { GraphChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import client from '../api/client'

use([CanvasRenderer, GraphChart, TooltipComponent, LegendComponent])

const route = useRoute()
const tid = Number(route.params.id)
const nodes = ref<any[]>([])
const edges = ref<any[]>([])
const topicName = ref('')
const chartRef = ref()

// Warm editorial palette aligned with theme
const TYPE_COLORS: Record<string,string> = {
  person:    '#CC785C', // rust
  project:   '#4A7C4E', // success green
  task:      '#B8862E', // warning amber
  concept:   '#A04545', // danger maroon
  decision:  '#5A6B7A', // info slate
  event:     '#6B5B95', // muted purple
  place:     '#8C6E54', // earth brown
  other:     '#A39E94', // ink-faint
}

const option = computed(() => ({
  tooltip: {
    backgroundColor: '#FFFFFF',
    borderColor: '#E5DFD3',
    textStyle: { color: '#1A1A1A', fontFamily: 'Geist, sans-serif' },
  },
  legend: [{
    data: Object.keys(TYPE_COLORS),
    textStyle: { color: '#6B6660', fontFamily: 'Geist, sans-serif' },
  }],
  series: [{
    type: 'graph', layout: 'force', roam: true, draggable: true,
    label: { show: true, position: 'right', fontFamily: 'Geist, sans-serif', color: '#1A1A1A' },
    force: { repulsion: 200, edgeLength: 80 },
    edgeSymbol: ['none', 'arrow'],
    edgeLabel: { show: true, formatter: (p: any) => p.data.label, fontSize: 10, fontFamily: 'Geist Mono, monospace', color: '#6B6660' },
    lineStyle: { color: '#C9C0AE', opacity: 0.6 },
    categories: Object.keys(TYPE_COLORS).map(name => ({ name, itemStyle: { color: TYPE_COLORS[name] } })),
    data: nodes.value.map(n => ({
      id: n.id, name: n.name, value: n.value,
      symbolSize: 10 + Math.min(30, n.value),
      category: n.type, itemStyle: { color: TYPE_COLORS[n.type] || '#A39E94' },
    })),
    links: edges.value.map(e => ({
      source: e.source, target: e.target, label: e.label, value: e.weight,
    })),
  }],
}))

onMounted(async () => {
  const t = await client.get(`/topics/${tid}`); topicName.value = t.data.name
  const g = await client.get(`/topics/${tid}/graph?limit=200`)
  nodes.value = g.data.nodes; edges.value = g.data.edges
})
</script>

<style scoped>
.chart-card {
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  background: var(--surface-elev);
  padding: var(--space-3);
}
</style>
