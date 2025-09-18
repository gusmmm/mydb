import axios from 'axios'

const API_BASE_URL = 'http://localhost:8001'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Dashboard Statistics Interfaces
export interface DatabaseStatistics {
  doentes: number
  internamentos: number
  agentesInfecciosos: number
  tiposAcidente: number
  agentesQueimadura: number
  mecanismosQueimadura: number
  origensDestino: number
}

export interface RecentActivity {
  recentDoentes: number
  recentInternamentos: number
  lastWeekAdmissions: number
}

export interface AgenteInfeccioso {
  id: number
  nome: string
  tipo_agente: string
  codigo_snomedct?: string | null
  subtipo_agent?: string | null
}

export interface AgenteInfecciosoCreate {
  nome: string
  tipo_agente: string
  codigo_snomedct?: string | null
  subtipo_agent?: string | null
}

export interface AgenteInfecciosoUpdate {
  nome?: string
  tipo_agente?: string
  codigo_snomedct?: string | null
  subtipo_agent?: string | null
}

// Patient (Doente) Interfaces
export interface Doente {
  id: number
  nome: string
  numero_processo: number
  data_nascimento: string | null
  sexo: 'M' | 'F'
  morada: string
  created_at?: string
  last_modified?: string
}

export interface DoenteCreate {
  nome: string
  numero_processo: number
  data_nascimento?: string | null
  sexo: 'M' | 'F'
  morada: string
}

export interface DoenteUpdate {
  nome?: string
  numero_processo?: number
  data_nascimento?: string | null
  sexo?: 'M' | 'F'
  morada?: string
}

// Internamento (Hospitalization) Interfaces
export interface Internamento {
  id: number
  numero_internamento: number
  doente_id: number
  data_entrada: string
  data_alta?: string | null
  data_queimadura?: string | null
  origem_entrada?: number | null
  destino_alta?: number | null
  ASCQ_total: number
  lesao_inalatoria: 'SIM' | 'NAO' | 'SUSPEITA'
  mecanismo_queimadura?: number | null
  agente_queimadura?: number | null
  tipo_acidente?: number | null
  incendio_florestal?: boolean | null
  contexto_violento?: 'SIM' | 'NAO' | 'SUSPEITA' | null
  suicidio_tentativa?: boolean | null
  fogueira_queda?: boolean | null
  lareira_queda?: boolean | null
  escarotomias_entrada?: boolean | null
  intubacao_OT?: 'SIM' | 'NAO' | 'OUTRO' | null
  VMI_dias?: number | null
  VNI?: boolean | null
  created_at?: string
  last_modified?: string
}

export interface InternamentoCreate {
  numero_internamento: number
  doente_id: number
  data_entrada: string
  data_alta?: string | null
  data_queimadura?: string | null
  origem_entrada?: number | null
  destino_alta?: number | null
  ASCQ_total: number
  lesao_inalatoria: 'SIM' | 'NAO' | 'SUSPEITA'
  mecanismo_queimadura?: number | null
  agente_queimadura?: number | null
  tipo_acidente?: number | null
  incendio_florestal?: boolean | null
  contexto_violento?: 'SIM' | 'NAO' | 'SUSPEITA' | null
  suicidio_tentativa?: boolean | null
  fogueira_queda?: boolean | null
  lareira_queda?: boolean | null
  escarotomias_entrada?: boolean | null
  intubacao_OT?: 'SIM' | 'NAO' | 'OUTRO' | null
  VMI_dias?: number | null
  VNI?: boolean | null
}

export interface InternamentoUpdate {
  numero_internamento?: number
  doente_id?: number
  data_entrada?: string
  data_alta?: string | null
  data_queimadura?: string | null
  origem_entrada?: number | null
  destino_alta?: number | null
  ASCQ_total?: number
  lesao_inalatoria?: 'SIM' | 'NAO' | 'SUSPEITA'
  mecanismo_queimadura?: number | null
  agente_queimadura?: number | null
  tipo_acidente?: number | null
  incendio_florestal?: boolean | null
  contexto_violento?: 'SIM' | 'NAO' | 'SUSPEITA' | null
  suicidio_tentativa?: boolean | null
  fogueira_queda?: boolean | null
  lareira_queda?: boolean | null
  escarotomias_entrada?: boolean | null
  intubacao_OT?: 'SIM' | 'NAO' | 'OUTRO' | null
  VMI_dias?: number | null
  VNI?: boolean | null
}

export const agenteInfecciosoService = {
  // Get all infectious agents
  async getAll(): Promise<AgenteInfeccioso[]> {
    const response = await api.get('/agentes_infecciosos')
    return response.data
  },

  // Get infectious agent by ID
  async getById(id: number): Promise<AgenteInfeccioso> {
    const response = await api.get(`/agentes_infecciosos/${id}`)
    return response.data
  },

  // Create new infectious agent
  async create(agente: AgenteInfecciosoCreate): Promise<AgenteInfeccioso> {
    const response = await api.post('/agentes_infecciosos', agente)
    return response.data
  },

  // Update infectious agent
  async update(id: number, agente: AgenteInfecciosoUpdate): Promise<AgenteInfeccioso> {
    const response = await api.patch(`/agentes_infecciosos/${id}`, agente)
    return response.data
  },

  // Delete infectious agent
  async delete(id: number): Promise<void> {
    await api.delete(`/agentes_infecciosos/${id}`)
  },
}

// Patient (Doente) Service
export const doenteService = {
  // Get all patients
  async getAll(): Promise<Doente[]> {
    const response = await api.get('/doentes')
    return response.data
  },

  // Get patient by ID
  async getById(id: number): Promise<Doente> {
    const response = await api.get(`/doentes/${id}`)
    return response.data
  },

  // Get patient by numero_processo
  async getByNumeroProcesso(numeroProcesso: number): Promise<Doente> {
    const response = await api.get(`/doentes/numero_processo/${numeroProcesso}`)
    return response.data
  },

  // Create new patient
  async create(doente: DoenteCreate): Promise<Doente> {
    const response = await api.post('/doentes', doente)
    return response.data
  },

  // Update patient (PUT - full update)
  async update(id: number, doente: DoenteCreate): Promise<Doente> {
    const response = await api.put(`/doentes/${id}`, doente)
    return response.data
  },

  // Partial update patient (PATCH)
  async partialUpdate(id: number, doente: DoenteUpdate): Promise<Doente> {
    const response = await api.patch(`/doentes/${id}`, doente)
    return response.data
  },

  // Delete patient
  async delete(id: number): Promise<void> {
    await api.delete(`/doentes/${id}`)
  },
}

// Internamento (Hospitalization) Service
export const internamentoService = {
  // Get all hospitalizations
  async getAll(): Promise<Internamento[]> {
    const response = await api.get('/internamentos')
    return response.data
  },

  // Get hospitalization by ID
  async getById(id: number): Promise<Internamento> {
    const response = await api.get(`/internamentos/${id}`)
    return response.data
  },

  // Get hospitalization by numero_internamento
  async getByNumero(numeroInternamento: number): Promise<Internamento> {
    const response = await api.get(`/internamentos/${numeroInternamento}`)
    return response.data
  },

  // Create new hospitalization
  async create(internamento: InternamentoCreate): Promise<Internamento> {
    const response = await api.post('/internamentos', internamento)
    return response.data
  },

  // Update hospitalization (PUT - full update)
  async update(id: number, internamento: InternamentoCreate): Promise<Internamento> {
    const response = await api.put(`/internamentos/${id}`, internamento)
    return response.data
  },

  // Partial update hospitalization (PATCH)
  async partialUpdate(id: number, internamento: InternamentoUpdate): Promise<Internamento> {
    const response = await api.patch(`/internamentos/${id}`, internamento)
    return response.data
  },

  // Delete hospitalization
  async delete(id: number): Promise<void> {
    await api.delete(`/internamentos/${id}`)
  },
}

// Dashboard Statistics Service
export const dashboardService = {
  // Get database statistics
  async getStatistics(): Promise<DatabaseStatistics> {
    try {
      const [
        doentesResponse,
        internamentosResponse,
        agentesResponse,
        tiposAcidenteResponse,
        agentesQueimaduraResponse,
        mecanismosQueimaduraResponse,
        origensDestinoResponse
      ] = await Promise.all([
        api.get('/doentes'),
        api.get('/internamentos'),
        api.get('/agentes_infecciosos'),
        api.get('/tipos_acidente'),
        api.get('/agentes_queimadura'),
        api.get('/mecanismos_queimadura'),
        api.get('/origens_destino')
      ])

      return {
        doentes: doentesResponse.data.length,
        internamentos: internamentosResponse.data.length,
        agentesInfecciosos: agentesResponse.data.length,
        tiposAcidente: tiposAcidenteResponse.data.length,
        agentesQueimadura: agentesQueimaduraResponse.data.length,
        mecanismosQueimadura: mecanismosQueimaduraResponse.data.length,
        origensDestino: origensDestinoResponse.data.length,
      }
    } catch (error) {
      console.error('Error fetching dashboard statistics:', error)
      throw error
    }
  },

  // Get recent activity (simplified for now)
  async getRecentActivity(): Promise<RecentActivity> {
    try {
      const [doentesResponse, internamentosResponse] = await Promise.all([
        api.get('/doentes'),
        api.get('/internamentos')
      ])

      // For now, we'll calculate simple statistics
      // In a real app, the backend would provide filtered data
      const doentes = doentesResponse.data
      const internamentos = internamentosResponse.data

      return {
        recentDoentes: doentes.length, // Placeholder - would filter by recent
        recentInternamentos: internamentos.length, // Placeholder - would filter by recent  
        lastWeekAdmissions: internamentos.length, // Placeholder - would filter by last week
      }
    } catch (error) {
      console.error('Error fetching recent activity:', error)
      throw error
    }
  }
}

export default api