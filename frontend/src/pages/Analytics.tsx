import { useEffect, useState } from 'react'
import { analyticsAPI } from '../services/api'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export default function Analytics() {
  const [centrality, setCentrality] = useState<any>(null)
  const [communities, setCommunities] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [centRes, commRes] = await Promise.all([
        analyticsAPI.centrality(),
        analyticsAPI.communities()
      ])
      setCentrality(centRes.data)
      setCommunities(commRes.data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div>Loading analytics...</div>

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Network Analytics</h1>
        <p className="text-sm text-gray-600">Explainable graph metrics • DEMO / SYNTHETIC DATA</p>
      </div>

      {/* Density & Components */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white border rounded-lg p-4">
          <p className="text-sm text-gray-600">Network Density</p>
          <p className="text-2xl font-bold">{centrality?.density || 0}</p>
          <p className="text-xs text-gray-500 mt-1">Ratio of actual to possible connections. Higher density indicates tightly connected network.</p>
        </div>
        <div className="bg-white border rounded-lg p-4">
          <p className="text-sm text-gray-600">Connected Components</p>
          <p className="text-2xl font-bold">{centrality?.components || 0}</p>
          <p className="text-xs text-gray-500 mt-1">Number of disconnected subgraphs. More components = more fragmented network.</p>
        </div>
        <div className="bg-white border rounded-lg p-4">
          <p className="text-sm text-gray-600">Analysis Basis</p>
          <p className="text-sm font-medium mt-1">Graph algorithms on synthetic data</p>
          <p className="text-xs text-gray-500 mt-1">Scores are analytical indicators, NOT criminal determinations.</p>
        </div>
      </div>

      {/* Centrality Tabs */}
      <div className="bg-white border rounded-lg p-4">
        <h2 className="text-lg font-semibold mb-4">Centrality Analysis</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <h3 className="font-medium mb-2">Degree Centrality - Most Connected</h3>
            <p className="text-xs text-gray-500 mb-3">Entities with most direct connections. High degree = many observed relationships.</p>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {centrality?.degree?.slice(0, 10).map((item: any, idx: number) => (
                <div key={idx} className="flex justify-between items-center p-2 bg-gray-50 rounded text-sm">
                  <div>
                    <p className="font-medium">{item.label}</p>
                    <p className="text-xs text-gray-500">{item.type} • {item.evidence}</p>
                    <p className="text-xs text-blue-600 mt-1">{item.interpretation}</p>
                  </div>
                  <span className="font-mono text-sm">{item.score.toFixed(3)}</span>
                </div>
              ))}
            </div>
          </div>
          <div>
            <h3 className="font-medium mb-2">Betweenness Centrality - Bridge Positions</h3>
            <p className="text-xs text-gray-500 mb-3">Entities that lie on many shortest paths. High betweenness = potential bridge between communities.</p>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {centrality?.betweenness?.slice(0, 10).map((item: any, idx: number) => (
                <div key={idx} className="flex justify-between items-center p-2 bg-gray-50 rounded text-sm">
                  <div>
                    <p className="font-medium">{item.label}</p>
                    <p className="text-xs text-gray-500">{item.type}</p>
                  </div>
                  <span className="font-mono text-sm">{item.score.toFixed(3)}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
          <div>
            <h3 className="font-medium mb-2">PageRank - Influence</h3>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={centrality?.pagerank?.slice(0, 8)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="label" tick={{ fontSize: 10 }} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="score" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div>
            <h3 className="font-medium mb-2">Closeness Centrality - Reachability</h3>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={centrality?.closeness?.slice(0, 8)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="label" tick={{ fontSize: 10 }} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="score" fill="#10b981" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Communities */}
      <div className="bg-white border rounded-lg p-4">
        <h2 className="text-lg font-semibold mb-4">Community Detection</h2>
        <p className="text-sm text-gray-600 mb-4">Clusters detected via modularity optimization. Each community represents densely connected entities.</p>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {communities?.communities?.map((comm: any) => (
            <div key={comm.id} className="border rounded-lg p-3">
              <div className="flex justify-between items-start">
                <h4 className="font-medium">Community {comm.id + 1}</h4>
                <span className="text-xs px-2 py-0.5 bg-blue-100 text-blue-800 rounded-full">{comm.size} members</span>
              </div>
              <p className="text-xs text-gray-600 mt-2">{comm.description}</p>
              <div className="mt-3">
                <p className="text-xs font-medium">Type Distribution:</p>
                <div className="flex flex-wrap gap-1 mt-1">
                  {Object.entries(comm.type_distribution || {}).map(([type, count]: any) => (
                    <span key={type} className="text-xs px-2 py-0.5 bg-gray-100 rounded">{type}: {count}</span>
                  ))}
                </div>
              </div>
              <div className="mt-2">
                <p className="text-xs font-medium">Central Nodes:</p>
                <p className="text-xs text-gray-600">{comm.central_nodes?.join(', ')}</p>
              </div>
              <div className="mt-2 text-xs text-gray-500">
                Density: {comm.density} • Edges: {comm.edge_count}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
        <h4 className="font-medium text-amber-900 text-sm">Explainable AI Principle</h4>
        <p className="text-xs text-amber-800 mt-1">
          Centrality scores indicate network position, NOT criminality. High connectivity means "requires investigator review" with evidence.
          Every metric includes WHAT was measured, WHY it matters, and supporting evidence.
        </p>
      </div>
    </div>
  )
}
