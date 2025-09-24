<template>
  <div class="outcomes-analysis">
    <div class="grid grid-cols-1 xl:grid-cols-2 gap-8">
      <!-- Discharge Destinations -->
      <Card v-if="outcomes.discharge_destinations">
        <template #header>
          <div class="p-4 pb-0">
            <h3 class="text-lg font-semibold flex items-center gap-2">
              <i class="pi pi-map-marker text-blue-500"></i>
              Patient Outcomes
            </h3>
          </div>
        </template>
        
        <template #content>
          <div class="space-y-4">
            <div class="chart-container">
              <canvas ref="outcomesChart"></canvas>
            </div>
            
            <!-- Mortality Rate Highlight -->
            <div v-if="outcomes.mortality_rate !== undefined" 
                 class="bg-red-50 border border-red-200 p-4 rounded-lg text-center">
              <p class="text-sm text-red-600">Mortality Rate</p>
              <p class="text-3xl font-bold text-red-700">{{ outcomes.mortality_rate }}%</p>
            </div>
          </div>
        </template>
      </Card>

      <!-- Time to Admission -->
      <Card v-if="outcomes.time_to_admission">
        <template #header>
          <div class="p-4 pb-0">
            <h3 class="text-lg font-semibold flex items-center gap-2">
              <i class="pi pi-clock text-green-500"></i>
              Time from Burn to Admission
            </h3>
          </div>
        </template>
        
        <template #content>
          <div class="space-y-4">
            <div class="time-stats-grid">
              <div class="bg-green-50 p-3 rounded-lg text-center">
                <p class="text-sm text-green-600">Mean Time</p>
                <p class="text-xl font-bold text-green-700">{{ outcomes.time_to_admission.mean_days }} days</p>
              </div>
              <div class="bg-blue-50 p-3 rounded-lg text-center">
                <p class="text-sm text-blue-600">Median Time</p>
                <p class="text-xl font-bold text-blue-700">{{ outcomes.time_to_admission.median_days }} days</p>
              </div>
            </div>
            
            <div class="time-details-grid">
              <div class="bg-orange-50 p-3 rounded-lg text-center">
                <p class="text-sm text-orange-600">Same Day</p>
                <p class="text-xl font-bold text-orange-700">{{ outcomes.time_to_admission.same_day_admissions }}</p>
                <p class="text-xs text-gray-600">{{ getSameDayPercentage() }}%</p>
              </div>
              <div class="bg-red-50 p-3 rounded-lg text-center">
                <p class="text-sm text-red-600">Delayed (>1 day)</p>
                <p class="text-xl font-bold text-red-700">{{ outcomes.time_to_admission.delayed_admissions }}</p>
                <p class="text-xs text-gray-600">{{ getDelayedPercentage() }}%</p>
              </div>
            </div>
          </div>
        </template>
      </Card>
    </div>

    <!-- Detailed Outcomes Breakdown -->
    <Card v-if="outcomes.discharge_destinations" class="mt-6">
      <template #header>
        <div class="p-4 pb-0">
          <h3 class="text-lg font-semibold flex items-center gap-2">
            <i class="pi pi-list text-purple-500"></i>
            Detailed Outcomes Breakdown
          </h3>
        </div>
      </template>
      
      <template #content>
        <div class="outcomes-breakdown-grid">
          <div 
            v-for="(count, destination) in outcomes.discharge_destinations" 
            :key="destination"
            class="p-4 rounded-lg border text-center"
            :class="getDestinationClass(destination)"
          >
            <i :class="`text-2xl mb-2 ${getDestinationIcon(destination)}`"></i>
            <p class="font-semibold text-gray-700">{{ destination }}</p>
            <p class="text-2xl font-bold">{{ count.toLocaleString() }}</p>
            <p class="text-sm text-gray-600">
              {{ ((count / getTotalOutcomes()) * 100).toFixed(1) }}%
            </p>
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
import type { OutcomeAnalysis } from '@/services/api'

Chart.register(...registerables)

interface Props {
  outcomes: OutcomeAnalysis
}

const props = defineProps<Props>()

// Template refs
const outcomesChart = ref<HTMLCanvasElement>()

// Chart instances
let outcomesChartInstance: Chart | null = null

// Methods
const getTotalOutcomes = () => {
  if (!props.outcomes.discharge_destinations) return 1
  return Object.values(props.outcomes.discharge_destinations).reduce((sum, count) => sum + count, 0)
}

const getSameDayPercentage = () => {
  if (!props.outcomes.time_to_admission) return 0
  const total = props.outcomes.time_to_admission.count
  const sameDay = props.outcomes.time_to_admission.same_day_admissions
  return ((sameDay / total) * 100).toFixed(1)
}

const getDelayedPercentage = () => {
  if (!props.outcomes.time_to_admission) return 0
  const total = props.outcomes.time_to_admission.count
  const delayed = props.outcomes.time_to_admission.delayed_admissions
  return ((delayed / total) * 100).toFixed(1)
}

const getDestinationClass = (destination: string) => {
  const classes: Record<string, string> = {
    'Home': 'bg-green-50 border-green-200',
    'Death': 'bg-red-50 border-red-200',
    'Ward': 'bg-blue-50 border-blue-200',
    'Other Hospital': 'bg-purple-50 border-purple-200',
    'Other': 'bg-gray-50 border-gray-200'
  }
  return classes[destination] || 'bg-gray-50 border-gray-200'
}

const getDestinationIcon = (destination: string) => {
  const icons: Record<string, string> = {
    'Home': 'pi pi-home text-green-500',
    'Death': 'pi pi-times-circle text-red-500',
    'Ward': 'pi pi-building text-blue-500',
    'Other Hospital': 'pi pi-send text-purple-500',
    'Other': 'pi pi-question-circle text-gray-500'
  }
  return icons[destination] || 'pi pi-circle text-gray-500'
}

const createOutcomesChart = () => {
  if (!outcomesChart.value || !props.outcomes.discharge_destinations) return

  const ctx = outcomesChart.value.getContext('2d')
  if (!ctx) return

  if (outcomesChartInstance) {
    outcomesChartInstance.destroy()
  }

  const data = props.outcomes.discharge_destinations
  const labels = Object.keys(data)
  const values = Object.values(data)
  const colors = labels.map(label => {
    const colorMap: Record<string, string> = {
      'Home': '#10B981',
      'Death': '#EF4444', 
      'Ward': '#3B82F6',
      'Other Hospital': '#7C3AED',
      'Other': '#6B7280'
    }
    return colorMap[label] || '#6B7280'
  })

  outcomesChartInstance = new Chart(ctx, {
    type: 'doughnut',
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
          position: 'bottom'
        }
      }
    }
  })
}

// Lifecycle
onMounted(() => {
  createOutcomesChart()
})

// Watch for data changes
watch(() => props.outcomes, () => {
  createOutcomesChart()
}, { deep: true })
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

/* Outcomes grids */
.outcomes-breakdown-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
  width: 100%;
}

@media (min-width: 640px) {
  .outcomes-breakdown-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .outcomes-breakdown-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

.time-stats-grid,
.time-details-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  width: 100%;
}
</style>