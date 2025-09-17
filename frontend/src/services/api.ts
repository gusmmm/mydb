import axios from 'axios'

const API_BASE_URL = 'http://localhost:8001'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

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

export default api