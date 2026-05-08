<template>
  <div>
    <header class="page-head">
      <div class="page-head-text">
        <h1>知识图谱 · {{ topicName }}</h1>
        <p class="lead">主题内的实体节点与语义关系网络。可拖拽、缩放与平移。</p>
      </div>
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

// MiniMax-aligned palette: purple brand + accents + state colors
const TYPE_COLORS: Record<string,string> = {
  person:    '#6B6BFA', // brand purple
  project:   '#00B42A', // success green
  task:      '#FF7D00', // warning orange
  concept:   '#CAC9FF', // light purple
  decision:  '#165DFF', // info blue
  event:     '#E8A93D', // gold
  place:     '#4E5969', // ink-3
  other:     '#D01316', // accent red (rare, for distinction)
}

const option = computed(() => ({
  tooltip: {
    backgroundColor: '#FFFFFF',
    borderColor: '#E5E6EB',
    textStyle: { color: '#181E25', fontFamily: 'Manrope, sans-serif' },
  },
  legend: [{
    data: Object.keys(TYPE_COLORS),
    textStyle: { color: '#4E5969', fontFamily: 'Manrope, sans-serif' },
  }],
  series: [{
    type: 'graph', layout: 'force', roam: true, draggable: true,
    label: { show: true, position: 'right', fontFamily: 'Manrope, sans-serif', color: '#181E25' },
    force: { repulsion: 200, edgeLength: 80 },
    edgeSymbol: ['none', 'arrow'],
    edgeLabel: { show: true, formatter: (p: any) => p.data.label, fontSize: 10, fontFamily: 'JetBrains Mono, monospace', color: '#4E5969' },
    lineStyle: { color: '#C9CDD2', opacity: 0.6 },
    categories: Object.keys(TYPE_COLORS).map(name => ({ name, itemStyle: { color: TYPE_COLORS[name] } })),
    data: nodes.value.map(n => ({
      id: n.id, name: n.name, value: n.value,
      symbolSize: 10 + Math.min(30, n.value),
      category: n.type, itemStyle: { color: TYPE_COLORS[n.type] || '#86909C' },
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
  border-radius: var(--r-lg);
  background: var(--canvas);
  padding: var(--s-3);
}
</style>
