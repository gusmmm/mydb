import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { dashboardService, type DatabaseStatistics, type RecentActivity } from '@/services/api'

export const useDashboardStore = defineStore('dashboard', () => {
  // State
  const statistics = ref<DatabaseStatistics>({
    doentes: 0,
    internamentos: 0,
    agentesInfecciosos: 0,
    tiposAcidente: 0,
    agentesQueimadura: 0,
    mecanismosQueimadura: 0,
    origensDestino: 0,
  })
  
  const recentActivity = ref<RecentActivity>({
    recentDoentes: 0,
    recentInternamentos: 0,
    lastWeekAdmissions: 0,
  })
  
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const totalRecords = computed(() => 
    statistics.value.doentes + statistics.value.internamentos
  )
  
  const totalLookupTables = computed(() => 
    statistics.value.agentesInfecciosos + 
    statistics.value.tiposAcidente + 
    statistics.value.agentesQueimadura + 
    statistics.value.mecanismosQueimadura + 
    statistics.value.origensDestino
  )

  const isDatabaseActive = computed(() => totalRecords.value > 0)

  // Actions
  async function fetchStatistics() {
    isLoading.value = true
    error.value = null
    
    try {
      statistics.value = await dashboardService.getStatistics()
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch statistics'
      console.error('Error fetching statistics:', err)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchRecentActivity() {
    try {
      recentActivity.value = await dashboardService.getRecentActivity()
    } catch (err) {
      console.error('Error fetching recent activity:', err)
    }
  }

  async function fetchAllData() {
    await Promise.all([
      fetchStatistics(),
      fetchRecentActivity()
    ])
  }

  function resetStore() {
    statistics.value = {
      doentes: 0,
      internamentos: 0,
      agentesInfecciosos: 0,
      tiposAcidente: 0,
      agentesQueimadura: 0,
      mecanismosQueimadura: 0,
      origensDestino: 0,
    }
    recentActivity.value = {
      recentDoentes: 0,
      recentInternamentos: 0,
      lastWeekAdmissions: 0,
    }
    error.value = null
  }

  return {
    // State
    statistics,
    recentActivity,
    isLoading,
    error,
    
    // Computed
    totalRecords,
    totalLookupTables,
    isDatabaseActive,
    
    // Actions
    fetchStatistics,
    fetchRecentActivity,
    fetchAllData,
    resetStore
  }
})