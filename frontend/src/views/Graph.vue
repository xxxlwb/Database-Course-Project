<template>
  <div>
    <h2>知识图谱：{{ topicName }}</h2>
    <v-chart ref="chartRef" :option="option" autoresize style="height:600px" />
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

const TYPE_COLORS: Record<string,string> = {
  person:'#5470c6', project:'#91cc75', task:'#fac858',
  concept:'#ee6666', decision:'#73c0de', event:'#3ba272',
  place:'#fc8452', other:'#9a60b4',
}

const option = computed(() => ({
  tooltip: {},
  legend: [{ data: Object.keys(TYPE_COLORS) }],
  series: [{
    type: 'graph', layout: 'force', roam: true, draggable: true,
    label: { show: true, position: 'right' },
    force: { repulsion: 200, edgeLength: 80 },
    edgeSymbol: ['none', 'arrow'],
    edgeLabel: { show: true, formatter: (p: any) => p.data.label, fontSize: 10 },
    categories: Object.keys(TYPE_COLORS).map(name => ({ name })),
    data: nodes.value.map(n => ({
      id: n.id, name: n.name, value: n.value,
      symbolSize: 10 + Math.min(30, n.value),
      category: n.type, itemStyle: { color: TYPE_COLORS[n.type] },
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
