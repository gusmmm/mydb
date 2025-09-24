<template>
  <div class="etiology-analysis">
    <div class="etiology-grid">
      <!-- Top Causes -->
      <Card v-if="etiology.top_causes">
        <template #header>
          <div class="p-4 pb-0">
            <h3 class="text-lg font-semibold flex items-center gap-2">
              <i class="pi pi-fire text-orange-500"></i>
              Top Burn Causes
            </h3>
          </div>
        </template>

        <template #content>
          <div class="space-y-4">
            <!-- Horizontal Bar Chart improves scanability -->
            <div class="chart-container" :style="{ height: topChartHeight }">
              <canvas ref="topCausesChart"></canvas>
            </div>

            <!-- Compact two-column list for quick reference -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
              <div
                v-for="([cause, count], idx) in topCausesEntries"
                :key="cause"
                class="flex items-center justify-between rounded-lg px-3 py-2 bg-gray-50"
              >
                <div class="flex items-center gap-2 min-w-0">
                  <span class="inline-flex items-center justify-center w-6 h-6 text-sm font-bold rounded-full bg-orange-100 text-orange-700">{{ idx + 1 }}</span>
                  <span class="font-medium truncate" :title="formatCause(cause)">{{ formatCause(cause) }}</span>
                </div>
                <div class="flex items-center gap-2 text-right">
                  <span class="font-semibold">{{ Number(count).toLocaleString() }}</span>
                  <span class="text-xs px-2 py-0.5 rounded-full bg-orange-50 text-orange-700 border border-orange-200">{{ etiology.top_causes_percentages?.[cause] ?? 0 }}%</span>
                </div>
              </div>
            </div>
          </div>
        </template>
      </Card>

      <!-- Categorized Causes -->
      <Card v-if="etiology.categorized_causes">
        <template #header>
          <div class="p-4 pb-0">
            <h3 class="text-lg font-semibold flex items-center gap-2">
              <i class="pi pi-chart-pie text-red-500"></i>
              Cause Categories
            </h3>
          </div>
        </template>
        
        <template #content>
          <div class="space-y-4">
            <div class="chart-container">
              <canvas ref="categoryChart"></canvas>
            </div>
            
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <div
                v-for="(count, category) in etiology.categorized_causes"
                :key="category"
                class="flex items-center justify-between p-2 rounded bg-gray-50"
              >
                <div class="flex items-center gap-2">
                  <span
                    class="w-3 h-3 rounded-full"
                    :style="{ backgroundColor: getCategoryColor(category) }"
                  ></span>
                  <span class="font-medium">{{ category }}</span>
                </div>
                <span class="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-800 border border-gray-200">{{ Number(count).toLocaleString() }}</span>
              </div>
            </div>
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import Card from 'primevue/card'
import { Chart, registerables } from 'chart.js'
import type { EtiologyAnalysis } from '@/services/api'

Chart.register(...registerables)

interface Props {
  etiology: EtiologyAnalysis
}

const props = defineProps<Props>()

// Template refs
const categoryChart = ref<HTMLCanvasElement>()
const topCausesChart = ref<HTMLCanvasElement>()

// Chart instances
let categoryChartInstance: Chart | null = null
let topCausesChartInstance: Chart | null = null

// Methods
const formatCause = (cause: string) => {
  return cause.charAt(0).toUpperCase() + cause.slice(1)
}

const getCategoryColor = (category: string) => {
  const colors: Record<string, string> = {
    'Fire/Flame': '#EF4444',
    'Hot Liquids': '#F59E0B', 
    'Electrical': '#3B82F6',
    'Chemical': '#10B981',
    'Other': '#6B7280'
  }
  return colors[category] || '#6B7280'
}

const createCategoryChart = () => {
  if (!categoryChart.value || !props.etiology.categorized_causes) return

  const ctx = categoryChart.value.getContext('2d')
  if (!ctx) return

  if (categoryChartInstance) {
    categoryChartInstance.destroy()
  }

  const data = props.etiology.categorized_causes
  const labels = Object.keys(data)
  const values = Object.values(data)
  const colors = labels.map(getCategoryColor)

  categoryChartInstance = new Chart(ctx, {
    type: 'pie',
    data: {
      labels,
      datasets: [{
        data: values,
        backgroundColor: colors,
        borderWidth: 2,
        borderColor: '#ffffff'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        }
      }
    }
  })
}

// ---- Top causes horizontal bar chart ----
const TOP_N = 10

const topCausesEntries = computed(() => {
  const data = props.etiology?.top_causes ?? {}
  return Object.entries<number>(data).slice(0, TOP_N)
})

const topChartHeight = computed(() => {
  const bars = topCausesEntries.value.length || 1
  // 30px per bar + header/margins padding
  return `${Math.min(bars, TOP_N) * 30 + 70}px`
})

const createTopCausesChart = () => {
  if (!topCausesChart.value || topCausesEntries.value.length === 0) return

  const ctx = topCausesChart.value.getContext('2d')
  if (!ctx) return

  if (topCausesChartInstance) {
    topCausesChartInstance.destroy()
  }

  const labels = topCausesEntries.value.map(([cause]) => formatCause(cause))
  const values = topCausesEntries.value.map(([, count]) => Number(count))

  // Color emphasis: top 3 highlighted
  const base = '#f59e0b' // amber
  const mute = '#e5e7eb' // gray-200
  const colors = values.map((_, i) => (i < 3 ? base : mute))

  topCausesChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          data: values,
          backgroundColor: colors,
          borderColor: '#ffffff',
          borderWidth: 1,
          borderSkipped: false,
          barThickness: 18
        }
      ]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          grid: { color: 'rgba(107,114,128,0.2)' },
          ticks: { color: '#9CA3AF' }
        },
        y: {
          grid: { display: false },
          ticks: { color: '#D1D5DB', font: { weight: '600' } }
        }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => `${ctx.parsed.x?.toLocaleString?.() || ctx.parsed.x}`
          }
        }
      }
    }
  })
}

// Lifecycle
onMounted(() => {
  createCategoryChart()
  createTopCausesChart()
})

// Watch for data changes
watch(
  () => props.etiology,
  () => {
    createCategoryChart()
    createTopCausesChart()
  },
  { deep: true }
)
</script>

<style scoped>
.chart-container {
  height: 300px;
  position: relative;
  padding: 1rem;
}

:deep(.p-card-content) {
  padding: 1.5rem;
}

:deep(.p-card-header) {
  padding: 1.5rem 1.5rem 0.5rem 1.5rem;
}

/* Etiology full-width grid layout */
.etiology-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
  width: 100%;
}

@media (min-width: 1200px) {
  .etiology-grid {
    grid-template-columns: 1fr 1fr;
  }
}
</style>