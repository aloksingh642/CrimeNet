import { useEffect, useState } from 'react'
import { graphAPI } from '../services/api'
import GraphViewer from '../components/GraphViewer'
import { Search, Network, Route } from 'lucide-react'

export default function GraphExplorer() {
  const [graphData, setGraphData] = useState<any>({ nodes: [], edges: [], stats: {} })
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({ node_type: '', relationship_type: '', limit: 300 })
  const [selectedNode, setSelectedNode] = useState<any>(null)
  const [selectedEdge, setSelectedEdge] = useState<any>(null)
  const [pathSearch, setPathSearch] = useState({ source: '', target: '' })
  const [pathResult, setPathResult] = useState<any>(null)

  useEffect(() => {
    loadGraph()
  }, [])

  const loadGraph = async () => {
    setLoading(true)
    try {
      const params: any = { limit: filters.limit }
      if (filters.node_type) params.node_type = filters.node_type
      if (filters.relationship_type) params.relationship_type = filters.relationship_type
      const res = await graphAPI.get(params)
      setGraphData(res.data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const handlePathSearch = async () => {
    if (!pathSearch.source || !pathSearch.target) return
    try {
      const res = await graphAPI.path(pathSearch.source, pathSearch.target)
      setPathResult(res.data)
    } catch (e) {
      console.error(e)
    }
  }

  const handleNodeClick = (node: any) => {
    setSelectedNode(node)
    setSelectedEdge(null)
  }

  const handleEdgeClick = (edge: any) => {
    setSelectedEdge(edge)
    setSelectedNode(null)
  }

  if (loading) return <div className="p-6">Loading graph... This may take a moment for 500+ entities.</div>

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Graph Explorer</h1>
          <p className="text-sm text-gray-600">Interactive network visualization • {graphData.nodes.length} nodes • {graphData.edges.length} edges</p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg border p-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <select
            value={filters.node_type}
            onChange={(e) => setFilters({ ...filters, node_type: e.target.value })}
            className="px-3 py-2 border rounded-lg text-sm"
          >
            <option value="">All Node Types</option>
            <option value="Person">Person</option>
            <option value="Phone">Phone</option>
            <option value="Vehicle">Vehicle</option>
            <option value="Location">Location</option>
            <option value="Organization">Organization</option>
          </select>
          <select
            value={filters.relationship_type}
            onChange={(e) => setFilters({ ...filters, relationship_type: e.target.value })}
            className="px-3 py-2 border rounded-lg text-sm"
          >
            <option value="">All Relationships</option>
            <option value="CALLED">CALLED</option>
            <option value="OWNS">OWNS</option>
            <option value="TRANSFERRED_TO">TRANSFERRED_TO</option>
            <option value="COMMUNICATED_WITH">COMMUNICATED_WITH</option>
            <option value="FINANCIAL_LINK">FINANCIAL_LINK</option>
          </select>
          <select
            value={filters.limit}
            onChange={(e) => setFilters({ ...filters, limit: parseInt(e.target.value) })}
            className="px-3 py-2 border rounded-lg text-sm"
          >
            <option value={100}>100 nodes</option>
            <option value={200}>200 nodes</option>
            <option value={300}>300 nodes</option>
            <option value={500}>500 nodes</option>
          </select>
          <button onClick={loadGraph} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm">
            Apply Filters
          </button>
        </div>

        {/* Path Search */}
        <div className="mt-4 p-3 bg-gray-50 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <Route className="h-4 w-4" />
            <span className="text-sm font-medium">Shortest Path Analysis</span>
          </div>
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="Source (e.g., person_1 or phone number)"
              value={pathSearch.source}
              onChange={(e) => setPathSearch({ ...pathSearch, source: e.target.value })}
              className="flex-1 px-3 py-2 border rounded-lg text-sm"
            />
            <input
              type="text"
              placeholder="Target (e.g., person_2)"
              value={pathSearch.target}
              onChange={(e) => setPathSearch({ ...pathSearch, target: e.target.value })}
              className="flex-1 px-3 py-2 border rounded-lg text-sm"
            />
            <button onClick={handlePathSearch} className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm hover:bg-green-700">
              Find Path
            </button>
          </div>
          {pathResult && (
            <div className="mt-3 p-3 bg-white border rounded">
              <p className="text-sm font-medium">Path Result: {pathResult.length} hops</p>
              <div className="mt-2 flex flex-wrap gap-2">
                {pathResult.nodes?.map((node: any, idx: number) => (
                  <span key={idx} className="text-xs">
                    {node.label} {idx < pathResult.nodes.length - 1 ? ' → ' : ''}
                  </span>
                ))}
              </div>
              {pathResult.nodes?.length === 0 && <p className="text-sm text-gray-500">No path found between these entities</p>}
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 bg-white rounded-lg border p-4">
          <GraphViewer data={graphData} onNodeClick={handleNodeClick} onEdgeClick={handleEdgeClick} height="600px" />
        </div>

        <div className="space-y-4">
          {/* Node Details */}
          {selectedNode && (
            <div className="bg-white rounded-lg border p-4">
              <h3 className="font-semibold mb-3">Node Details</h3>
              <div className="space-y-2 text-sm">
                <div><span className="text-gray-600">ID:</span> {selectedNode.id}</div>
                <div><span className="text-gray-600">Label:</span> {selectedNode.fullLabel || selectedNode.label}</div>
                <div><span className="text-gray-600">Type:</span> <span className="px-2 py-0.5 bg-blue-100 text-blue-800 rounded-full text-xs">{selectedNode.type}</span></div>
                <div className="pt-2 border-t">
                  <p className="font-medium mb-1">Properties:</p>
                  <pre className="text-xs bg-gray-50 p-2 rounded overflow-auto max-h-64">
                    {JSON.stringify(selectedNode, null, 2)}
                  </pre>
                </div>
                <div className="pt-2">
                  <p className="text-xs text-gray-500">Evidence-backed relationship. Click to view supporting evidence in Evidence Explorer.</p>
                </div>
              </div>
            </div>
          )}

          {/* Edge Details */}
          {selectedEdge && (
            <div className="bg-white rounded-lg border p-4">
              <h3 className="font-semibold mb-3">Relationship Details</h3>
              <div className="space-y-2 text-sm">
                <div><span className="text-gray-600">Type:</span> {selectedEdge.type}</div>
                <div><span className="text-gray-600">From:</span> {selectedEdge.source}</div>
                <div><span className="text-gray-600">To:</span> {selectedEdge.target}</div>
                <div className="pt-2 border-t">
                  <p className="font-medium mb-1">Metadata:</p>
                  <pre className="text-xs bg-gray-50 p-2 rounded overflow-auto">
                    {JSON.stringify(selectedEdge, null, 2)}
                  </pre>
                </div>
              </div>
            </div>
          )}

          {/* Graph Stats */}
          <div className="bg-white rounded-lg border p-4">
            <h3 className="font-semibold mb-3">Graph Statistics</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between"><span>Nodes:</span><span className="font-medium">{graphData.stats.node_count}</span></div>
              <div className="flex justify-between"><span>Edges:</span><span className="font-medium">{graphData.stats.edge_count}</span></div>
              <div className="pt-2 text-xs text-gray-500">
                <p>• Zoom with mouse wheel</p>
                <p>• Drag to pan</p>
                <p>• Click node to inspect</p>
                <p>• Use filters to focus analysis</p>
              </div>
            </div>
          </div>

          {/* Explainability */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="font-medium text-blue-900 text-sm mb-2">Investigator Guidance</h4>
            <p className="text-xs text-blue-800">
              Every relationship shows evidence. High connectivity does NOT mean criminality - it indicates network position requiring review.
              Always check Evidence Explorer for supporting records.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
