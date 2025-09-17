import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { 
  agenteInfecciosoService, 
  type AgenteInfeccioso, 
  type AgenteInfecciosoCreate,
  type AgenteInfecciosoUpdate
} from '@/services/api'

export const useAgenteInfecciosoStore = defineStore('agenteInfeccioso', () => {
  // State
  const agentes = ref<AgenteInfeccioso[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const totalAgentes = computed(() => agentes.value.length)
  const agentesPorTipo = computed(() => {
    return agentes.value.reduce((acc, agente) => {
      const tipo = agente.tipo_agente
      acc[tipo] = (acc[tipo] || 0) + 1
      return acc
    }, {} as Record<string, number>)
  })

  // Actions
  const fetchAgentes = async () => {
    loading.value = true
    error.value = null
    try {
      agentes.value = await agenteInfecciosoService.getAll()
    } catch (err) {
      error.value = 'Failed to fetch infectious agents'
      console.error('Error fetching agentes:', err)
    } finally {
      loading.value = false
    }
  }

  const createAgente = async (agente: AgenteInfecciosoCreate) => {
    loading.value = true
    error.value = null
    try {
      const newAgente = await agenteInfecciosoService.create(agente)
      agentes.value.push(newAgente)
      return newAgente
    } catch (err) {
      error.value = 'Failed to create infectious agent'
      console.error('Error creating agente:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateAgente = async (id: number, updates: AgenteInfecciosoUpdate) => {
    loading.value = true
    error.value = null
    try {
      const updatedAgente = await agenteInfecciosoService.update(id, updates)
      const index = agentes.value.findIndex(a => a.id === id)
      if (index !== -1) {
        agentes.value[index] = updatedAgente
      }
      return updatedAgente
    } catch (err) {
      error.value = 'Failed to update infectious agent'
      console.error('Error updating agente:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteAgente = async (id: number) => {
    loading.value = true
    error.value = null
    try {
      await agenteInfecciosoService.delete(id)
      agentes.value = agentes.value.filter(a => a.id !== id)
    } catch (err) {
      error.value = 'Failed to delete infectious agent'
      console.error('Error deleting agente:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const getAgenteById = (id: number) => {
    return agentes.value.find(a => a.id === id)
  }

  const clearError = () => {
    error.value = null
  }

  return {
    // State
    agentes,
    loading,
    error,
    // Getters
    totalAgentes,
    agentesPorTipo,
    // Actions
    fetchAgentes,
    createAgente,
    updateAgente,
    deleteAgente,
    getAgenteById,
    clearError,
  }
})