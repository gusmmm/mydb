<template>
  <div class="overview-grid">
    <!-- Total Records -->
    <Card class="overview-card">
      <template #content>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600">Total Records</p>
            <p class="text-2xl font-bold text-blue-600">
              {{ overview.total_records?.toLocaleString() || '0' }}
            </p>
          </div>
          <i class="pi pi-database text-blue-500 text-3xl"></i>
        </div>
      </template>
    </Card>

    <!-- Unique Patients -->
    <Card class="overview-card">
      <template #content>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600">Unique Patients</p>
            <p class="text-2xl font-bold text-green-600">
              {{ overview.total_patients?.toLocaleString() || '0' }}
            </p>
          </div>
          <i class="pi pi-users text-green-500 text-3xl"></i>
        </div>
      </template>
    </Card>

    <!-- Year Range -->
    <Card class="overview-card">
      <template #content>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600">Year Range</p>
            <p class="text-2xl font-bold text-purple-600">
              {{ overview.year_range?.min_year || '?' }} - {{ overview.year_range?.max_year || '?' }}
            </p>
            <p class="text-xs text-gray-500">
              ({{ overview.year_range?.years_span || 0 }} years)
            </p>
          </div>
          <i class="pi pi-calendar text-purple-500 text-3xl"></i>
        </div>
      </template>
    </Card>

    <!-- Data Completeness -->
    <Card class="overview-card">
      <template #content>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600">Data Completeness</p>
            <p class="text-2xl font-bold" :class="getCompletenessColor()">
              {{ overview.data_completeness?.completeness_rate || 0 }}%
            </p>
            <p class="text-xs text-gray-500">
              {{ overview.data_completeness?.complete_records || 0 }} complete records
            </p>
          </div>
          <i :class="`pi pi-chart-pie text-3xl ${getCompletenessIconColor()}`"></i>
        </div>
      </template>
    </Card>
  </div>

  <!-- Missing Data Summary -->
  <Card v-if="hasMissingData" class="mb-6">
    <template #header>
      <div class="flex items-center gap-2 p-4 pb-0">
        <i class="pi pi-exclamation-triangle text-orange-500"></i>
        <h3 class="text-lg font-semibold">Data Completeness by Column</h3>
      </div>
    </template>
    
    <template #content>
      <div class="completeness-grid">
        <div 
          v-for="(missingInfo, column) in overview.missing_data_summary" 
          :key="column"
          class="bg-gray-50 p-3 rounded-lg"
        >
          <div class="flex justify-between items-center mb-2">
            <span class="font-medium text-gray-900">{{ formatColumnName(column) }}</span>
            <Badge 
              :value="`${missingInfo.missing_percentage}%`" 
              :severity="getMissingSeverity(missingInfo.missing_percentage)"
            />
          </div>
          
          <div class="space-y-1">
            <div class="flex justify-between text-sm">
              <span class="text-gray-600">Missing:</span>
              <span class="font-medium">{{ missingInfo.missing_count.toLocaleString() }}</span>
            </div>
            
            <!-- Progress bar for completeness -->
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div 
                class="h-2 rounded-full transition-all duration-300"
                :class="getProgressBarColor(missingInfo.missing_percentage)"
                :style="`width: ${100 - missingInfo.missing_percentage}%`"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </Card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import Card from 'primevue/card'
import Badge from 'primevue/badge'
import type { AnalysisOverview } from '@/services/api'

interface Props {
  overview: AnalysisOverview
}

const props = defineProps<Props>()

// Computed properties
const hasMissingData = computed(() => {
  return props.overview.missing_data_summary && 
         Object.keys(props.overview.missing_data_summary).length > 0
})

// Methods
const getCompletenessColor = () => {
  const rate = props.overview.data_completeness?.completeness_rate || 0
  if (rate >= 80) return 'text-green-600'
  if (rate >= 60) return 'text-yellow-600'
  return 'text-red-600'
}

const getCompletenessIconColor = () => {
  const rate = props.overview.data_completeness?.completeness_rate || 0
  if (rate >= 80) return 'text-green-500'
  if (rate >= 60) return 'text-yellow-500'
  return 'text-red-500'
}

const formatColumnName = (column: string) => {
  // Convert snake_case to readable format
  return column
    .replace(/_/g, ' ')
    .replace(/\b\w/g, l => l.toUpperCase())
}

const getMissingSeverity = (percentage: number): "success" | "warning" | "danger" | "info" => {
  if (percentage < 10) return 'success'
  if (percentage < 30) return 'info'  
  if (percentage < 60) return 'warning'
  return 'danger'
}

const getProgressBarColor = (missingPercentage: number) => {
  const completeness = 100 - missingPercentage
  if (completeness >= 80) return 'bg-green-500'
  if (completeness >= 60) return 'bg-yellow-500'
  return 'bg-red-500'
}
</script>

<style scoped>
.overview-card {
  min-height: 140px;
  width: 100%;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.overview-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
}

.overview-card :deep(.p-card-content) {
  padding: 1.5rem;
}

/* Full width grid layout */
.overview-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
  width: 100%;
  margin-bottom: 2rem;
}

@media (min-width: 640px) {
  .overview-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .overview-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

/* Data completeness grid layout */
.completeness-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
  width: 100%;
}

@media (min-width: 768px) {
  .completeness-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1200px) {
  .completeness-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (min-width: 1600px) {
  .completeness-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}
</style>