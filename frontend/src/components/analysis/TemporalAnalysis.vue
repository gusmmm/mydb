<template>
  <div class="temporal-analysis">
    <div class="grid grid-cols-1 xl:grid-cols-2 gap-8">
      <!-- Yearly Admissions Trend -->
      <Card v-if="temporal.yearly_admissions">
        <template #header>
          <div class="p-4 pb-0">
            <h3 class="text-lg font-semibold flex items-center gap-2">
              <i class="pi pi-chart-line text-blue-500"></i>
              Yearly Admissions Trend
            </h3>
          </div>
        </template>
        
        <template #content>
          <div class="chart-container">
            <canvas ref="yearlyChart"></canvas>
          </div>
        </template>
      </Card>

      <!-- Monthly Patterns -->
      <Card v-if="temporal.monthly_patterns">
        <template #header>
          <div class="p-4 pb-0">
            <h3 class="text-lg font-semibold flex items-center gap-2">
              <i class="pi pi-calendar text-green-500"></i>
              Monthly Admission Patterns
            </h3>
          </div>
        </template>
        
        <template #content>
          <div class="chart-container">
            <canvas ref="monthlyChart"></canvas>
          </div>
        </template>
      </Card>
    </div>

    <!-- Seasonal Distribution -->
    <Card v-if="temporal.seasonal_distribution" class="mt-6">
      <template #header>
        <div class="p-4 pb-0">
          <h3 class="text-lg font-semibold flex items-center gap-2">
            <i class="pi pi-sun text-orange-500"></i>
            Seasonal Distribution
          </h3>
        </div>
      </template>
      
      <template #content>
        <div class="space-y-4">
          <div class="chart-container" style="height: 250px;">
            <canvas ref="seasonalChart"></canvas>
          </div>
          
          <div class="seasonal-grid">
            <div 
              v-for="(count, season) in temporal.seasonal_distribution" 
              :key="season"
              class="text-center p-4 rounded-lg"
              :class="getSeasonClass(season)"
            >
              <i :class="`text-2xl mb-2 ${getSeasonIcon(season)}`"></i>
              <p class="font-semibold text-gray-700">{{ season }}</p>
              <p class="text-2xl font-bold">{{ count.toLocaleString() }}</p>
              <p class="text-sm text-gray-600">
                {{ ((count / getTotalSeasonal()) * 100).toFixed(1) }}%
              </p>
            </div>
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
import type { TemporalAnalysis } from '@/services/api'

Chart.register(...registerables)

interface Props {
  temporal: TemporalAnalysis
}

const props = defineProps<Props>()

// Template refs
const yearlyChart = ref<HTMLCanvasElement>()
const monthlyChart = ref<HTMLCanvasElement>()
const seasonalChart = ref<HTMLCanvasElement>()

// Chart instances
let yearlyChartInstance: Chart | null = null
let monthlyChartInstance: Chart | null = null
let seasonalChartInstance: Chart | null = null

// Methods
const getTotalSeasonal = () => {
  if (!props.temporal.seasonal_distribution) return 1
  return Object.values(props.temporal.seasonal_distribution).reduce((sum, count) => sum + count, 0)
}

const getSeasonClass = (season: string) => {
  const classes: Record<string, string> = {
    'Spring': 'bg-green-50 border border-green-200',
    'Summer': 'bg-yellow-50 border border-yellow-200', 
    'Autumn': 'bg-orange-50 border border-orange-200',
    'Winter': 'bg-blue-50 border border-blue-200'
  }
  return classes[season] || 'bg-gray-50'
}

const getSeasonIcon = (season: string) => {
  const icons: Record<string, string> = {
    'Spring': 'pi pi-sun text-green-500',
    'Summer': 'pi pi-sun text-yellow-500',
    'Autumn': 'pi pi-cloud text-orange-500', 
    'Winter': 'pi pi-cloud text-blue-500'
  }
  return icons[season] || 'pi pi-calendar'
}

const createYearlyChart = () => {
  if (!yearlyChart.value || !props.temporal.yearly_admissions) return

  const ctx = yearlyChart.value.getContext('2d')
  if (!ctx) return

  if (yearlyChartInstance) {
    yearlyChartInstance.destroy()
  }

  const data = props.temporal.yearly_admissions
  const labels = Object.keys(data).sort()
  const values = labels.map(year => data[year])

  yearlyChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'Admissions',
        data: values,
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
        fill: true
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            precision: 0
          }
        }
      },
      plugins: {
        legend: {
          display: false
        }
      }
    }
  })
}

const createMonthlyChart = () => {
  if (!monthlyChart.value || !props.temporal.monthly_patterns) return

  const ctx = monthlyChart.value.getContext('2d')
  if (!ctx) return

  if (monthlyChartInstance) {
    monthlyChartInstance.destroy()
  }

  const data = props.temporal.monthly_patterns
  const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const labels = []
  const values = []

  for (let i = 1; i <= 12; i++) {
    labels.push(monthNames[i - 1])
    values.push(data[i] || 0)
  }

  monthlyChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Admissions',
        data: values,
        backgroundColor: 'rgba(34, 197, 94, 0.6)',
        borderColor: 'rgb(34, 197, 94)',
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            precision: 0
          }
        }
      },
      plugins: {
        legend: {
          display: false
        }
      }
    }
  })
}

const createSeasonalChart = () => {
  if (!seasonalChart.value || !props.temporal.seasonal_distribution) return

  const ctx = seasonalChart.value.getContext('2d')
  if (!ctx) return

  if (seasonalChartInstance) {
    seasonalChartInstance.destroy()
  }

  const data = props.temporal.seasonal_distribution
  const labels = Object.keys(data)
  const values = Object.values(data)
  const colors = ['#10B981', '#F59E0B', '#EF4444', '#3B82F6'] // Green, Yellow, Orange, Blue

  seasonalChartInstance = new Chart(ctx, {
    type: 'pie',
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
  createYearlyChart()
  createMonthlyChart() 
  createSeasonalChart()
})

// Watch for data changes
watch(() => props.temporal, () => {
  createYearlyChart()
  createMonthlyChart()
  createSeasonalChart()
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

/* Seasonal distribution grid */
.seasonal-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  width: 100%;
}

@media (min-width: 768px) {
  .seasonal-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}
</style>