export interface User {
  id: number
  username: string
  email?: string
  full_name?: string
  role: string
}

export interface Case {
  id: number
  case_number: string
  title: string
  description?: string
  status: string
  priority: string
  investigator_name?: string
  created_at: string
}

export interface GraphNode {
  id: string
  label: string
  type: string
  properties: any
}

export interface GraphEdge {
  id: string
  source: string
  target: string
  type: string
  properties: any
}

export interface GraphData {
  nodes: GraphNode[]
  edges: GraphEdge[]
  stats: any
}

export interface Anomaly {
  id: string
  finding_type: string
  title: string
  description: string
  severity: string
  confidence: number
  evidence: any
  entities_involved: string[]
}
