import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || ''

const api = axios.create({
  baseURL: API_URL || undefined,
  headers: {
    'Content-Type': 'application/json',
  }
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api

// API functions
export const authAPI = {
  login: (username: string, password: string) => api.post('/api/auth/login', { username, password }),
  me: () => api.get('/api/auth/me'),
}

export const casesAPI = {
  list: () => api.get('/api/cases'),
  get: (id: number) => api.get(`/api/cases/${id}`),
  create: (data: any) => api.post('/api/cases', data),
  update: (id: number, data: any) => api.put(`/api/cases/${id}`, data),
}

export const entitiesAPI = {
  search: (q: string, type?: string) => api.get('/api/entities/search', { params: { q, entity_type: type } }),
  getPerson: (id: number) => api.get(`/api/entities/person/${id}`),
  stats: () => api.get('/api/entities/stats'),
  listPersons: (skip = 0, limit = 50) => api.get('/api/entities/persons', { params: { skip, limit } }),
}

export const graphAPI = {
  get: (params?: any) => api.get('/api/graph', { params }),
  path: (source: string, target: string) => api.get('/api/graph/path', { params: { source, target } }),
  neighbors: (nodeId: string, depth = 1) => api.get(`/api/graph/neighbors/${nodeId}`, { params: { depth } }),
  rebuild: () => api.post('/api/graph/rebuild'),
}

export const analyticsAPI = {
  centrality: () => api.get('/api/analytics/centrality'),
  communities: () => api.get('/api/analytics/communities'),
  anomalies: () => api.get('/api/analytics/anomalies'),
  overview: () => api.get('/api/analytics/overview'),
}

export const documentsAPI = {
  list: () => api.get('/api/documents'),
  create: (data: any) => api.post('/api/documents', data),
  process: (id: number) => api.post(`/api/documents/${id}/process`),
  get: (id: number) => api.get(`/api/documents/${id}`),
}

export const timelineAPI = {
  get: (params?: any) => api.get('/api/timeline', { params }),
}

export const findingsAPI = {
  list: () => api.get('/api/findings'),
  anomalies: () => api.get('/api/findings/anomalies'),
  review: (id: number, action: string) => api.post(`/api/findings/${id}/review`, null, { params: { action } }),
  generate: () => api.post('/api/findings/generate'),
}

export const reportsAPI = {
  caseReport: (caseId: number) => api.get(`/api/reports/case/${caseId}`),
  overview: () => api.get('/api/reports/overview'),
}

export const auditAPI = {
  list: (params?: any) => api.get('/api/audit-logs', { params }),
}

export const dashboardAPI = {
  get: () => api.get('/api/dashboard'),
}
