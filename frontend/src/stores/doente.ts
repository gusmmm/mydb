import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { 
  doenteService, 
  type Doente, 
  type DoenteCreate,
  type DoenteUpdate
} from '@/services/api'

export const useDoenteStore = defineStore('doente', () => {
  // State
  const doentes = ref<Doente[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const totalDoentes = computed(() => doentes.value.length)
  const doentesPorSexo = computed(() => {
    return doentes.value.reduce((acc, doente) => {
      const sexo = doente.sexo
      acc[sexo] = (acc[sexo] || 0) + 1
      return acc
    }, {} as Record<string, number>)
  })

  // Actions
  const fetchDoentes = async () => {
    loading.value = true
    error.value = null
    try {
      doentes.value = await doenteService.getAll()
    } catch (err) {
      error.value = 'Failed to fetch patients'
      console.error('Error fetching doentes:', err)
    } finally {
      loading.value = false
    }
  }

  const createDoente = async (doente: DoenteCreate) => {
    loading.value = true
    error.value = null
    try {
      const newDoente = await doenteService.create(doente)
      doentes.value.push(newDoente)
      return newDoente
    } catch (err) {
      error.value = 'Failed to create patient'
      console.error('Error creating doente:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateDoente = async (id: number, updates: DoenteUpdate) => {
    loading.value = true
    error.value = null
    try {
      const updatedDoente = await doenteService.partialUpdate(id, updates)
      const index = doentes.value.findIndex(d => d.id === id)
      if (index !== -1) {
        doentes.value[index] = updatedDoente
      }
      return updatedDoente
    } catch (err) {
      error.value = 'Failed to update patient'
      console.error('Error updating doente:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteDoente = async (id: number) => {
    loading.value = true
    error.value = null
    try {
      await doenteService.delete(id)
      doentes.value = doentes.value.filter(d => d.id !== id)
    } catch (err) {
      error.value = 'Failed to delete patient'
      console.error('Error deleting doente:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const clearError = () => {
    error.value = null
  }

  return {
    // State
    doentes,
    loading,
    error,
    // Getters
    totalDoentes,
    doentesPorSexo,
    // Actions
    fetchDoentes,
    createDoente,
    updateDoente,
    deleteDoente,
    clearError
  }
})