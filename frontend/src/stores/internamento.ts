import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { 
  internamentoService, 
  type Internamento, 
  type InternamentoCreate,
  type InternamentoUpdate
} from '@/services/api'

export const useInternamentoStore = defineStore('internamento', () => {
  // State
  const internamentos = ref<Internamento[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const totalInternamentos = computed(() => internamentos.value.length)
  const internamentosPorMes = computed(() => {
    return internamentos.value.reduce((acc, internamento) => {
      const mes = new Date(internamento.data_entrada).toISOString().substring(0, 7) // YYYY-MM
      acc[mes] = (acc[mes] || 0) + 1
      return acc
    }, {} as Record<string, number>)
  })

  const internamentosComLesaoInalatoria = computed(() => 
    internamentos.value.filter(i => i.lesao_inalatoria === 'SIM').length
  )

  // Actions
  const normalizeDate = (val: unknown): string | null | undefined => {
    if (val === undefined) return undefined
    if (val === '' || val === null) return null
    if (typeof val === 'string') return val // assume yyyy-mm-dd from inputs
    return undefined
  }

  const normalizeNumber = (val: unknown): number | null | undefined => {
    if (val === undefined) return undefined
    if (val === '' || val === null) return null
    if (typeof val === 'number') return val
    if (typeof val === 'string') {
      const n = Number(val)
      return Number.isNaN(n) ? null : n
    }
    return undefined
  }

  const normalizeBoolean = (val: unknown): boolean | null | undefined => {
    if (val === undefined) return undefined
    if (val === '' || val === null) return null
    if (typeof val === 'boolean') return val
    if (typeof val === 'string') {
      const lower = val.toLowerCase()
      if (lower === 'true') return true
      if (lower === 'false') return false
      return null
    }
    return undefined
  }

  const normalizeEnum = (val: unknown): string | null | undefined => {
    if (val === undefined) return undefined
    if (val === '' || val === null) return null
    if (typeof val === 'string') return val.toUpperCase()
    return undefined
  }

  const normalizeInternamentoUpdate = (updates: InternamentoUpdate): InternamentoUpdate => {
    // Clone to avoid mutating caller state
    const u: InternamentoUpdate = { ...updates }

    // Dates
    if ('data_entrada' in u) u.data_entrada = normalizeDate(u.data_entrada) as any
    if ('data_alta' in u) u.data_alta = normalizeDate(u.data_alta) as any
    if ('data_queimadura' in u) u.data_queimadura = normalizeDate(u.data_queimadura) as any

    // Numbers
    if ('numero_internamento' in u) u.numero_internamento = normalizeNumber(u.numero_internamento) as any
    if ('doente_id' in u) u.doente_id = normalizeNumber(u.doente_id) as any
    if ('origem_entrada' in u) u.origem_entrada = normalizeNumber(u.origem_entrada) as any
    if ('destino_alta' in u) u.destino_alta = normalizeNumber(u.destino_alta) as any
    if ('ASCQ_total' in u) u.ASCQ_total = normalizeNumber(u.ASCQ_total) as any
    if ('mecanismo_queimadura' in u) u.mecanismo_queimadura = normalizeNumber(u.mecanismo_queimadura) as any
    if ('agente_queimadura' in u) u.agente_queimadura = normalizeNumber(u.agente_queimadura) as any
    if ('tipo_acidente' in u) u.tipo_acidente = normalizeNumber(u.tipo_acidente) as any
    if ('VMI_dias' in u) u.VMI_dias = normalizeNumber(u.VMI_dias) as any

    // Booleans
    if ('incendio_florestal' in u) u.incendio_florestal = normalizeBoolean(u.incendio_florestal) as any
    if ('suicidio_tentativa' in u) u.suicidio_tentativa = normalizeBoolean(u.suicidio_tentativa) as any
    if ('fogueira_queda' in u) u.fogueira_queda = normalizeBoolean(u.fogueira_queda) as any
    if ('lareira_queda' in u) u.lareira_queda = normalizeBoolean(u.lareira_queda) as any
    if ('escarotomias_entrada' in u) u.escarotomias_entrada = normalizeBoolean(u.escarotomias_entrada) as any
    if ('VNI' in u) u.VNI = normalizeBoolean(u.VNI) as any

    // Enums (string unions on backend)
    if ('lesao_inalatoria' in u) u.lesao_inalatoria = normalizeEnum(u.lesao_inalatoria) as any
    if ('contexto_violento' in u) u.contexto_violento = normalizeEnum(u.contexto_violento) as any
    if ('intubacao_OT' in u) u.intubacao_OT = normalizeEnum(u.intubacao_OT) as any

    return u
  }

  const fetchInternamentos = async () => {
    loading.value = true
    error.value = null
    try {
      internamentos.value = await internamentoService.getAll()
    } catch (err) {
      error.value = 'Failed to fetch hospitalizations'
      console.error('Error fetching internamentos:', err)
    } finally {
      loading.value = false
    }
  }

  const createInternamento = async (internamento: InternamentoCreate) => {
    loading.value = true
    error.value = null
    try {
      // Light normalization for create as well (dates and numbers)
      const normalized: InternamentoCreate = {
        ...internamento,
        data_entrada: normalizeDate(internamento.data_entrada) as any,
        data_alta: normalizeDate(internamento.data_alta) as any,
        data_queimadura: normalizeDate(internamento.data_queimadura) as any,
        numero_internamento: normalizeNumber(internamento.numero_internamento) as any,
        doente_id: normalizeNumber(internamento.doente_id) as any,
        origem_entrada: normalizeNumber(internamento.origem_entrada) as any,
        destino_alta: normalizeNumber(internamento.destino_alta) as any,
        ASCQ_total: normalizeNumber(internamento.ASCQ_total) as any,
        mecanismo_queimadura: normalizeNumber(internamento.mecanismo_queimadura) as any,
        agente_queimadura: normalizeNumber(internamento.agente_queimadura) as any,
        tipo_acidente: normalizeNumber(internamento.tipo_acidente) as any,
        incendio_florestal: normalizeBoolean(internamento.incendio_florestal) as any,
        suicidio_tentativa: normalizeBoolean(internamento.suicidio_tentativa) as any,
        fogueira_queda: normalizeBoolean(internamento.fogueira_queda) as any,
        lareira_queda: normalizeBoolean(internamento.lareira_queda) as any,
        escarotomias_entrada: normalizeBoolean(internamento.escarotomias_entrada) as any,
        VNI: normalizeBoolean(internamento.VNI) as any,
        lesao_inalatoria: normalizeEnum(internamento.lesao_inalatoria) as any,
        contexto_violento: normalizeEnum(internamento.contexto_violento) as any,
        intubacao_OT: normalizeEnum(internamento.intubacao_OT) as any,
        VMI_dias: normalizeNumber(internamento.VMI_dias) as any,
      }
      const newInternamento = await internamentoService.create(normalized)
      internamentos.value.push(newInternamento)
      return newInternamento
    } catch (err) {
      error.value = 'Failed to create hospitalization'
      console.error('Error creating internamento:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateInternamento = async (id: number, updates: InternamentoUpdate) => {
    loading.value = true
    error.value = null
    try {
      const normalized = normalizeInternamentoUpdate(updates)
      const updatedInternamento = await internamentoService.partialUpdate(id, normalized)
      const index = internamentos.value.findIndex(i => i.id === id)
      if (index !== -1) {
        internamentos.value[index] = updatedInternamento
      }
      return updatedInternamento
    } catch (err) {
      error.value = 'Failed to update hospitalization'
      console.error('Error updating internamento:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteInternamento = async (id: number) => {
    loading.value = true
    error.value = null
    try {
      await internamentoService.delete(id)
      internamentos.value = internamentos.value.filter(i => i.id !== id)
    } catch (err) {
      error.value = 'Failed to delete hospitalization'
      console.error('Error deleting internamento:', err)
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
    internamentos,
    loading,
    error,
    
    // Getters
    totalInternamentos,
    internamentosPorMes,
    internamentosComLesaoInalatoria,
    
    // Actions
    fetchInternamentos,
    createInternamento,
    updateInternamento,
    deleteInternamento,
    clearError
  }
})