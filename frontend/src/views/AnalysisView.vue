<template>
  <div class="analysis-container">
    <!-- Header -->
    <div class="flex justify-between items-center mb-8 w-full">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">BD_doentes Analysis</h1>
        <p class="text-gray-600 mt-2">
          Comprehensive statistical analysis and visualization of burn unit data
        </p>
      </div>
      <div class="flex gap-3">
        <Button 
          @click="refreshAnalysis" 
          :loading="loading"
          icon="pi pi-refresh"
          label="Refresh"
          class="p-button-outlined"
        />
        <Button 
          @click="exportReport" 
          :loading="exporting"
          icon="pi pi-download"
          label="Export Report"
          class="p-button-success"
        />
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading && !analysisData" class="text-center py-12">
      <ProgressSpinner />
      <p class="mt-4 text-gray-600">Loading analysis data...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="text-center py-12">
      <i class="pi pi-exclamation-triangle text-red-500 text-4xl mb-4"></i>
      <h3 class="text-xl font-semibold text-gray-900 mb-2">Analysis Error</h3>
      <p class="text-gray-600 mb-4">{{ error }}</p>
      <Button @click="loadAnalysis" label="Retry" icon="pi pi-refresh" />
    </div>

    <!-- Analysis Content -->
    <div v-else-if="analysisData" class="space-y-8">
      <!-- Overview Cards -->
      <AnalysisOverviewCards :overview="analysisData.overview" />

      <!-- Tabs for Different Analysis Sections -->
      <TabView class="analysis-tabs">
        <TabPanel header="Demographics">
          <DemographicsAnalysis :demographics="analysisData.demographics" />
        </TabPanel>
        
        <TabPanel header="Temporal Patterns">
          <TemporalAnalysis :temporal="analysisData.temporal_patterns" />
        </TabPanel>
        
        <TabPanel header="Burn Severity">
          <BurnSeverityAnalysis :burnSeverity="analysisData.burn_severity" />
        </TabPanel>
        
        <TabPanel header="Etiology">
          <EtiologyAnalysis :etiology="analysisData.etiology" />
        </TabPanel>
        
        <TabPanel header="Outcomes">
          <OutcomesAnalysis :outcomes="analysisData.outcomes" />
        </TabPanel>
        
        <TabPanel header="Data Quality">
          <DataQualityAnalysis :overview="analysisData.overview" />
        </TabPanel>
      </TabView>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { analysisService, type ComprehensiveAnalysis } from '@/services/api'
import Button from 'primevue/button'
import ProgressSpinner from 'primevue/progressspinner'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import { useToast } from 'primevue/usetoast'

import AnalysisOverviewCards from '@/components/analysis/AnalysisOverviewCards.vue'
import DemographicsAnalysis from '@/components/analysis/DemographicsAnalysis.vue'
import TemporalAnalysis from '@/components/analysis/TemporalAnalysis.vue'
import BurnSeverityAnalysis from '@/components/analysis/BurnSeverityAnalysis.vue'
import EtiologyAnalysis from '@/components/analysis/EtiologyAnalysis.vue'
import OutcomesAnalysis from '@/components/analysis/OutcomesAnalysis.vue'
import DataQualityAnalysis from '@/components/analysis/DataQualityAnalysis.vue'

const toast = useToast()

// Reactive data
const loading = ref(false)
const exporting = ref(false)
const error = ref<string | null>(null)
const analysisData = ref<ComprehensiveAnalysis | null>(null)

// Methods
const loadAnalysis = async () => {
  loading.value = true
  error.value = null
  
  try {
    analysisData.value = await analysisService.getComprehensive()
    
    toast.add({
      severity: 'success',
      summary: 'Analysis Loaded',
      detail: 'Statistical analysis completed successfully',
      life: 3000
    })
  } catch (err) {
    console.error('Error loading analysis:', err)
    error.value = err instanceof Error ? err.message : 'Unknown error occurred'
    
    toast.add({
      severity: 'error',
      summary: 'Analysis Error',
      detail: 'Failed to load statistical analysis',
      life: 5000
    })
  } finally {
    loading.value = false
  }
}

const refreshAnalysis = async () => {
  await loadAnalysis()
}

const exportReport = async () => {
  if (!analysisData.value) return
  
  exporting.value = true
  
  try {
    // Create a comprehensive report as JSON
    const reportData = {
      ...analysisData.value,
      export_timestamp: new Date().toISOString(),
      export_version: '1.0'
    }
    
    // Create and download JSON file
    const blob = new Blob([JSON.stringify(reportData, null, 2)], { 
      type: 'application/json' 
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `bd_doentes_analysis_${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    
    toast.add({
      severity: 'success',
      summary: 'Report Exported',
      detail: 'Analysis report downloaded successfully',
      life: 3000
    })
  } catch (err) {
    console.error('Error exporting report:', err)
    
    toast.add({
      severity: 'error',
      summary: 'Export Error',
      detail: 'Failed to export analysis report',
      life: 5000
    })
  } finally {
    exporting.value = false
  }
}

// Lifecycle
onMounted(() => {
  loadAnalysis()
})
</script>

<style scoped>
.analysis-container {
  width: 100%;
  min-width: 100%;
  min-height: 100vh;
  padding: 2rem;
  margin: 0;
  background-color: #f8fafc;
}

.analysis-tabs :deep(.p-tabview-panels) {
  padding: 2rem 0;
}

.analysis-tabs :deep(.p-tabview-nav) {
  margin-bottom: 1rem;
}

@media (max-width: 768px) {
  .analysis-container {
    padding: 1rem;
  }
  
  .analysis-tabs :deep(.p-tabview-panels) {
    padding: 1rem 0;
  }
}
</style>