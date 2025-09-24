<template>
  <div class="demographics-analysis">
    <div class="grid grid-cols-1 xl:grid-cols-2 gap-8">
      <!-- Gender Distribution -->
      <Card>
        <template #header>
          <div class="p-4 pb-0">
            <h3 class="text-lg font-semibold flex items-center gap-2">
              <i class="pi pi-users text-blue-500"></i>
              Gender Distribution
            </h3>
          </div>
        </template>
        
        <template #content>
          <div v-if="demographics.gender_distribution" class="space-y-4">
            <!-- Chart Container -->
            <div class="chart-container">
              <canvas ref="genderChart"></canvas>
            </div>
            
            <!-- Stats Table -->
            <div class="bg-gray-50 p-3 rounded-lg">
              <div class="space-y-2">
                <div 
                  v-for="(count, gender) in demographics.gender_distribution.counts" 
                  :key="gender"
                  class="flex justify-between items-center"
                >
                  <span class="font-medium">{{ getGenderLabel(gender) }}:</span>
                  <div class="text-right">
                    <span class="font-bold">{{ count.toLocaleString() }}</span>
                    <span class="text-sm text-gray-600 ml-2">
                      ({{ demographics.gender_distribution.percentages[gender] }}%)
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>
      </Card>

      <!-- Age Distribution -->
      <Card v-if="demographics.age_statistics">
        <template #header>
          <div class="p-4 pb-0">
            <h3 class="text-lg font-semibold flex items-center gap-2">
              <i class="pi pi-chart-bar text-green-500"></i>
              Age Distribution
            </h3>
          </div>
        </template>
        
        <template #content>
          <div class="space-y-4">
            <!-- Chart Container -->
            <div class="chart-container">
              <canvas ref="ageChart"></canvas>
            </div>
            
            <!-- Age Statistics -->
            <div class="grid grid-cols-2 gap-4">
              <div class="bg-blue-50 p-3 rounded-lg text-center">
                <p class="text-sm text-blue-600">Mean Age</p>
                <p class="text-xl font-bold text-blue-700">
                  {{ demographics.age_statistics.mean }} years
                </p>
              </div>
              
              <div class="bg-green-50 p-3 rounded-lg text-center">
                <p class="text-sm text-green-600">Median Age</p>
                <p class="text-xl font-bold text-green-700">
                  {{ demographics.age_statistics.median }} years
                </p>
              </div>
              
              <div class="bg-orange-50 p-3 rounded-lg text-center">
                <p class="text-sm text-orange-600">Age Range</p>
                <p class="text-xl font-bold text-orange-700">
                  {{ demographics.age_statistics.min }} - {{ demographics.age_statistics.max }}
                </p>
              </div>
              
              <div class="bg-purple-50 p-3 rounded-lg text-center">
                <p class="text-sm text-purple-600">Sample Size</p>
                <p class="text-xl font-bold text-purple-700">
                  {{ demographics.age_statistics.count.toLocaleString() }}
                </p>
              </div>
            </div>
          </div>
        </template>
      </Card>
    </div>

    <!-- Age Range Distribution (if available) -->
    <Card v-if="demographics.age_distribution" class="mt-6">
      <template #header>
        <div class="p-4 pb-0">
          <h3 class="text-lg font-semibold flex items-center gap-2">
            <i class="pi pi-chart-line text-purple-500"></i>
            Age Range Distribution
          </h3>
        </div>
      </template>
      
      <template #content>
        <div class="age-range-grid">
          <div 
            v-for="(count, ageRange) in demographics.age_distribution" 
            :key="ageRange"
            class="bg-gradient-to-br from-purple-50 to-blue-50 p-4 rounded-lg text-center"
          >
            <p class="text-sm text-gray-600">{{ ageRange }} years</p>
            <p class="text-2xl font-bold text-purple-700">{{ count.toLocaleString() }}</p>
            <p class="text-xs text-gray-500">
              {{ ((count / getTotalAgeDistribution()) * 100).toFixed(1) }}%
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
import type { DemographicAnalysis } from '@/services/api'

Chart.register(...registerables)

interface Props {
  demographics: DemographicAnalysis
}

const props = defineProps<Props>()

// Template refs
const genderChart = ref<HTMLCanvasElement>()
const ageChart = ref<HTMLCanvasElement>()

// Chart instances
let genderChartInstance: Chart | null = null
let ageChartInstance: Chart | null = null

// Methods
const getGenderLabel = (gender: string) => {
  const labels: Record<string, string> = {
    'M': 'Male',
    'F': 'Female',
    'other': 'Other'
  }
  return labels[gender] || gender
}

const getTotalAgeDistribution = () => {
  if (!props.demographics.age_distribution) return 1
  return Object.values(props.demographics.age_distribution).reduce((sum, count) => sum + count, 0)
}

const createGenderChart = () => {
  if (!genderChart.value || !props.demographics.gender_distribution) return

  const ctx = genderChart.value.getContext('2d')
  if (!ctx) return

  // Destroy existing chart
  if (genderChartInstance) {
    genderChartInstance.destroy()
  }

  const data = props.demographics.gender_distribution.counts
  const labels = Object.keys(data).map(getGenderLabel)
  const values = Object.values(data)
  const colors = ['#3B82F6', '#EF4444', '#10B981', '#F59E0B']

  genderChartInstance = new Chart(ctx, {
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

const createAgeChart = () => {
  if (!ageChart.value || !props.demographics.age_distribution) return

  const ctx = ageChart.value.getContext('2d')
  if (!ctx) return

  // Destroy existing chart
  if (ageChartInstance) {
    ageChartInstance.destroy()
  }

  const data = props.demographics.age_distribution
  const labels = Object.keys(data)
  const values = Object.values(data)

  ageChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Number of Patients',
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

// Lifecycle
onMounted(() => {
  createGenderChart()
  createAgeChart()
})

// Watch for data changes
watch(() => props.demographics, () => {
  createGenderChart()
  createAgeChart()
}, { deep: true })
</script>

<style scoped>
.chart-container {
  height: 350px;
  position: relative;
  padding: 1rem;
}

.demographics-analysis {
  width: 100%;
}

:deep(.p-card-content) {
  padding: 1.5rem;
}

:deep(.p-card-header) {
  padding: 1.5rem 1.5rem 0.5rem 1.5rem;
}

/* Age range distribution grid */
.age-range-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  width: 100%;
}

@media (min-width: 768px) {
  .age-range-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (min-width: 1024px) {
  .age-range-grid {
    grid-template-columns: repeat(5, 1fr);
  }
}
</style>