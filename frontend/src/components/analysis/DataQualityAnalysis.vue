<template>
  <div class="data-quality-analysis">
    <!-- Overall Quality Score -->
    <Card class="mb-6">
      <template #header>
        <div class="p-4 pb-0">
          <h3 class="text-lg font-semibold flex items-center gap-2">
            <i class="pi pi-check-circle text-green-500"></i>
            Overall Data Quality Score
          </h3>
        </div>
      </template>
      
      <template #content>
        <div class="text-center py-6">
          <div class="relative inline-block">
            <div 
              class="w-32 h-32 rounded-full flex items-center justify-center text-4xl font-bold text-white"
              :class="getQualityScoreClass()"
            >
              {{ overview.data_completeness?.completeness_rate || 0 }}%
            </div>
          </div>
          <p class="mt-4 text-lg text-gray-600">
            {{ getQualityDescription() }}
          </p>
          <p class="text-sm text-gray-500 mt-2">
            {{ overview.data_completeness?.complete_records || 0 }} of {{ overview.total_records || 0 }} records are complete
          </p>
        </div>
      </template>
    </Card>

    <!-- Missing Data Details -->
    <div class="quality-analysis-grid">
      <!-- Missing Data Chart -->
      <Card v-if="hasMissingData">
        <template #header>
          <div class="p-4 pb-0">
            <h3 class="text-lg font-semibold flex items-center gap-2">
              <i class="pi pi-chart-bar text-orange-500"></i>
              Missing Data by Column
            </h3>
          </div>
        </template>
        
        <template #content>
          <div class="chart-container">
            <canvas ref="missingDataChart"></canvas>
          </div>
        </template>
      </Card>

      <!-- Data Quality Issues -->
      <Card>
        <template #header>
          <div class="p-4 pb-0">
            <h3 class="text-lg font-semibold flex items-center gap-2">
              <i class="pi pi-exclamation-triangle text-yellow-500"></i>
              Data Quality Issues
            </h3>
          </div>
        </template>
        
        <template #content>
          <div class="space-y-4">
            <!-- Critical Issues -->
            <div v-if="getCriticalIssues().length > 0">
              <h4 class="font-medium text-red-600 mb-2 flex items-center gap-2">
                <i class="pi pi-times-circle"></i>
                Critical Issues (>60% missing)
              </h4>
              <div class="space-y-2">
                <div 
                  v-for="issue in getCriticalIssues()"
                  :key="issue.column"
                  class="flex justify-between items-center p-2 bg-red-50 border border-red-200 rounded"
                >
                  <span class="font-medium">{{ formatColumnName(issue.column) }}</span>
                  <Badge :value="`${issue.percentage}%`" severity="danger" />
                </div>
              </div>
            </div>

            <!-- Warning Issues -->
            <div v-if="getWarningIssues().length > 0">
              <h4 class="font-medium text-yellow-600 mb-2 flex items-center gap-2">
                <i class="pi pi-exclamation-triangle"></i>
                Warning Issues (30-60% missing)
              </h4>
              <div class="space-y-2">
                <div 
                  v-for="issue in getWarningIssues()"
                  :key="issue.column"
                  class="flex justify-between items-center p-2 bg-yellow-50 border border-yellow-200 rounded"
                >
                  <span class="font-medium">{{ formatColumnName(issue.column) }}</span>
                  <Badge :value="`${issue.percentage}%`" severity="warning" />
                </div>
              </div>
            </div>

            <!-- Minor Issues -->
            <div v-if="getMinorIssues().length > 0">
              <h4 class="font-medium text-blue-600 mb-2 flex items-center gap-2">
                <i class="pi pi-info-circle"></i>
                Minor Issues (10-30% missing)
              </h4>
              <div class="space-y-2">
                <div 
                  v-for="issue in getMinorIssues()"
                  :key="issue.column"
                  class="flex justify-between items-center p-2 bg-blue-50 border border-blue-200 rounded"
                >
                  <span class="font-medium">{{ formatColumnName(issue.column) }}</span>
                  <Badge :value="`${issue.percentage}%`" severity="info" />
                </div>
              </div>
            </div>

            <!-- Good Quality -->
            <div v-if="getGoodQuality().length > 0">
              <h4 class="font-medium text-green-600 mb-2 flex items-center gap-2">
                <i class="pi pi-check-circle"></i>
                Good Quality (<10% missing)
              </h4>
              <p class="text-sm text-green-700">
                {{ getGoodQuality().length }} columns have good data quality
              </p>
            </div>
          </div>
        </template>
      </Card>
    </div>

    <!-- Data Quality Recommendations -->
    <Card class="mt-6">
      <template #header>
        <div class="p-4 pb-0">
          <h3 class="text-lg font-semibold flex items-center gap-2">
            <i class="pi pi-lightbulb text-blue-500"></i>
            Data Quality Recommendations
          </h3>
        </div>
      </template>
      
      <template #content>
        <div class="space-y-3">
          <div v-for="recommendation in getRecommendations()" :key="recommendation.type" class="flex gap-3 p-3 border rounded-lg">
            <i :class="recommendation.icon"></i>
            <div>
              <h4 class="font-medium text-gray-900">{{ recommendation.title }}</h4>
              <p class="text-sm text-gray-600">{{ recommendation.description }}</p>
            </div>
          </div>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import Card from 'primevue/card'
import Badge from 'primevue/badge'
import { Chart, registerables } from 'chart.js'
import type { AnalysisOverview } from '@/services/api'

Chart.register(...registerables)

interface Props {
  overview: AnalysisOverview
}

interface QualityIssue {
  column: string
  percentage: number
  count: number
}

const props = defineProps<Props>()

// Template refs
const missingDataChart = ref<HTMLCanvasElement>()

// Chart instances
let missingDataChartInstance: Chart | null = null

// Computed properties
const hasMissingData = computed(() => {
  return props.overview.missing_data_summary && 
         Object.keys(props.overview.missing_data_summary).length > 0
})

const qualityIssues = computed((): QualityIssue[] => {
  if (!props.overview.missing_data_summary) return []
  
  return Object.entries(props.overview.missing_data_summary).map(([column, data]) => ({
    column,
    percentage: data.missing_percentage,
    count: data.missing_count
  }))
})

// Methods
const getQualityScoreClass = () => {
  const rate = props.overview.data_completeness?.completeness_rate || 0
  if (rate >= 80) return 'bg-green-500'
  if (rate >= 60) return 'bg-yellow-500'
  return 'bg-red-500'
}

const getQualityDescription = () => {
  const rate = props.overview.data_completeness?.completeness_rate || 0
  if (rate >= 80) return 'Excellent data quality'
  if (rate >= 60) return 'Good data quality'
  if (rate >= 40) return 'Fair data quality'
  return 'Poor data quality'
}

const formatColumnName = (column: string) => {
  return column
    .replace(/_/g, ' ')
    .replace(/\b\w/g, l => l.toUpperCase())
}

const getCriticalIssues = () => qualityIssues.value.filter(issue => issue.percentage > 60)
const getWarningIssues = () => qualityIssues.value.filter(issue => issue.percentage > 30 && issue.percentage <= 60)
const getMinorIssues = () => qualityIssues.value.filter(issue => issue.percentage > 10 && issue.percentage <= 30)
const getGoodQuality = () => qualityIssues.value.filter(issue => issue.percentage <= 10)

const getRecommendations = () => {
  const recommendations = []
  const criticalCount = getCriticalIssues().length
  const warningCount = getWarningIssues().length
  
  if (criticalCount > 0) {
    recommendations.push({
      type: 'critical',
      icon: 'pi pi-exclamation-circle text-red-500',
      title: 'Address Critical Missing Data',
      description: `${criticalCount} columns have >60% missing data. Consider data collection improvements or field requirements.`
    })
  }
  
  if (warningCount > 0) {
    recommendations.push({
      type: 'warning', 
      icon: 'pi pi-exclamation-triangle text-yellow-500',
      title: 'Improve Data Collection',
      description: `${warningCount} columns have significant missing data. Review data entry processes and training.`
    })
  }
  
  recommendations.push({
    type: 'info',
    icon: 'pi pi-info-circle text-blue-500',
    title: 'Data Validation Rules',
    description: 'Implement validation rules to prevent incomplete records and improve data quality over time.'
  })
  
  return recommendations
}

const createMissingDataChart = () => {
  if (!missingDataChart.value || !hasMissingData.value) return

  const ctx = missingDataChart.value.getContext('2d')
  if (!ctx) return

  if (missingDataChartInstance) {
    missingDataChartInstance.destroy()
  }

  const sortedIssues = qualityIssues.value
    .sort((a, b) => b.percentage - a.percentage)
    .slice(0, 10) // Top 10 missing data issues

  const labels = sortedIssues.map(issue => formatColumnName(issue.column))
  const values = sortedIssues.map(issue => issue.percentage)
  const colors = values.map(percentage => {
    if (percentage > 60) return '#EF4444' // Red
    if (percentage > 30) return '#F59E0B' // Yellow
    if (percentage > 10) return '#3B82F6' // Blue
    return '#10B981' // Green
  })

  missingDataChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Missing %',
        data: values,
        backgroundColor: colors,
        borderWidth: 1,
        borderColor: colors
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: 'y',
      scales: {
        x: {
          beginAtZero: true,
          max: 100,
          ticks: {
            callback: function(value) {
              return value + '%'
            }
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
  createMissingDataChart()
})

// Watch for data changes
watch(() => props.overview, () => {
  createMissingDataChart()
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

/* Quality analysis grid layout */
.quality-analysis-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
  width: 100%;
  margin-bottom: 2rem;
}

@media (min-width: 1200px) {
  .quality-analysis-grid {
    grid-template-columns: 1fr 1fr;
  }
}
</style>