<template>
  <div class="burn-severity-analysis">
    <div class="grid grid-cols-1 xl:grid-cols-2 gap-8">
      <!-- ASCQ Distribution -->
      <Card v-if="burnSeverity.ascq_distribution">
        <template #header>
          <div class="p-4 pb-0">
            <h3 class="text-lg font-semibold flex items-center gap-2">
              <i class="pi pi-chart-pie text-red-500"></i>
              ASCQ Burn Severity Distribution
            </h3>
          </div>
        </template>
        
        <template #content>
          <div class="space-y-4">
            <div class="chart-container">
              <canvas ref="ascqChart"></canvas>
            </div>
            
            <div v-if="burnSeverity.ascq_statistics" class="grid grid-cols-2 gap-3">
              <div class="bg-red-50 p-3 rounded-lg text-center">
                <p class="text-sm text-red-600">Mean ASCQ</p>
                <p class="text-xl font-bold text-red-700">{{ burnSeverity.ascq_statistics.mean }}%</p>
              </div>
              <div class="bg-orange-50 p-3 rounded-lg text-center">
                <p class="text-sm text-orange-600">Median ASCQ</p>
                <p class="text-xl font-bold text-orange-700">{{ burnSeverity.ascq_statistics.median }}%</p>
              </div>
            </div>
          </div>
        </template>
      </Card>

      <!-- Inhalation Injury -->
      <Card v-if="burnSeverity.inhalation_injury">
        <template #header>
          <div class="p-4 pb-0">
            <h3 class="text-lg font-semibold flex items-center gap-2">
              <i class="pi pi-heart text-blue-500"></i>
              Inhalation Injury
            </h3>
          </div>
        </template>
        
        <template #content>
          <div class="space-y-4">
            <div class="grid grid-cols-1 gap-3">
              <div 
                v-for="(count, status) in burnSeverity.inhalation_injury.counts" 
                :key="status"
                class="flex justify-between items-center p-3 bg-gray-50 rounded-lg"
              >
                <span class="font-medium">{{ getInjuryLabel(status) }}:</span>
                <div class="text-right">
                  <span class="font-bold text-lg">{{ count.toLocaleString() }}</span>
                  <span class="text-sm text-gray-600 ml-2">
                    ({{ burnSeverity.inhalation_injury.percentages[status] }}%)
                  </span>
                </div>
              </div>
            </div>
          </div>
        </template>
      </Card>
    </div>

    <!-- BAUX Score Statistics -->
    <Card v-if="burnSeverity.baux_statistics" class="mt-6">
      <template #header>
        <div class="p-4 pb-0">
          <h3 class="text-lg font-semibold flex items-center gap-2">
            <i class="pi pi-calculator text-purple-500"></i>
            BAUX Score Statistics
          </h3>
          <p class="text-sm text-gray-600 mt-1">
            BAUX Score = Age + %TBSA (predicts mortality risk)
          </p>
        </div>
      </template>
      
      <template #content>
        <div class="baux-stats-grid">
          <div class="bg-purple-50 p-4 rounded-lg text-center">
            <p class="text-sm text-purple-600">Mean BAUX</p>
            <p class="text-2xl font-bold text-purple-700">{{ burnSeverity.baux_statistics.mean }}</p>
          </div>
          <div class="bg-blue-50 p-4 rounded-lg text-center">
            <p class="text-sm text-blue-600">Median BAUX</p>
            <p class="text-2xl font-bold text-blue-700">{{ burnSeverity.baux_statistics.median }}</p>
          </div>
          <div class="bg-red-50 p-4 rounded-lg text-center">
            <p class="text-sm text-red-600">Max BAUX</p>
            <p class="text-2xl font-bold text-red-700">{{ burnSeverity.baux_statistics.max }}</p>
          </div>
          <div class="bg-green-50 p-4 rounded-lg text-center">
            <p class="text-sm text-green-600">Sample Size</p>
            <p class="text-2xl font-bold text-green-700">{{ burnSeverity.baux_statistics.count.toLocaleString() }}</p>
          </div>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import Card from 'primevue/card'
import { Chart, registerables } from 'chart.js'
import type { BurnSeverityAnalysis } from '@/services/api'

Chart.register(...registerables)

interface Props {
  burnSeverity: BurnSeverityAnalysis
}

const props = defineProps<Props>()

// Template refs
const ascqChart = ref<HTMLCanvasElement>()

// Chart instances
let ascqChartInstance: Chart | null = null

// Methods
const getInjuryLabel = (status: string) => {
  const labels: Record<string, string> = {
    'S': 'Yes',
    'N': 'No',
    's': 'Yes', 
    'n': 'No'
  }
  return labels[status] || status
}

const createASCQChart = () => {
  if (!ascqChart.value || !props.burnSeverity.ascq_distribution) return

  const ctx = ascqChart.value.getContext('2d')
  if (!ctx) return

  if (ascqChartInstance) {
    ascqChartInstance.destroy()
  }

  const data = props.burnSeverity.ascq_distribution
  const labels = Object.keys(data)
  const values = Object.values(data)
  const colors = ['#10B981', '#F59E0B', '#EF4444', '#7C3AED']

  ascqChartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data: values,
        backgroundColor: colors.slice(0, labels.length),
        borderWidth: 2,
        borderColor: '#ffffff'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom'
        }
      }
    }
  })
}

// Lifecycle
onMounted(() => {
  createASCQChart()
})

// Watch for data changes
watch(() => props.burnSeverity, () => {
  createASCQChart()
}, { deep: true })
</script>

<style scoped>
.chart-container {
  height: 350px;
  position: relative;
  padding: 1rem;
}

:deep(.p-card-content) {
  padding: 1.5rem;
}

:deep(.p-card-header) {
  padding: 1.5rem 1.5rem 0.5rem 1.5rem;
}

/* BAUX stats grid */
.baux-stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  width: 100%;
}

@media (min-width: 768px) {
  .baux-stats-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}
</style>