import { useEffect, useState } from 'react'
import { entitiesAPI } from '../services/api'
import { Search } from 'lucide-react'

export default function Entities() {
  const [search, setSearch] = useState('')
  const [results, setResults] = useState<any>(null)
  const [persons, setPersons] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadPersons()
  }, [])

  const loadPersons = async () => {
    try {
      const res = await entitiesAPI.listPersons(0, 50)
      setPersons(res.data)
    } catch (e) {
      console.error(e)
    }
  }

  const handleSearch = async () => {
    if (!search.trim()) return
    setLoading(true)
    try {
      const res = await entitiesAPI.search(search)
      setResults(res.data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Entity Explorer</h1>
        <p className="text-sm text-gray-600">Search across persons, phones, vehicles, organizations, locations</p>
      </div>

      <div className="bg-white border rounded-lg p-4">
        <div className="flex gap-2">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search entities (e.g., Rahul Sharma, phone number, vehicle...)"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              className="w-full pl-10 pr-3 py-2 border rounded-lg"
            />
          </div>
          <button onClick={handleSearch} disabled={loading} className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50">
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </div>

      {results && (
        <div className="bg-white border rounded-lg p-4">
          <h3 className="font-semibold mb-3">Search Results for "{results.query}" - {results.total} found</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(results.results).map(([type, items]: any) => (
              items.length > 0 && (
                <div key={type} className="border rounded p-3">
                  <h4 className="font-medium capitalize mb-2">{type} ({items.length})</h4>
                  <div className="space-y-1">
                    {items.slice(0, 5).map((item: any, idx: number) => (
                      <div key={idx} className="text-sm p-2 bg-gray-50 rounded">
                        <p className="font-medium">{item.name || item.phone_number || item.registration_number || item.incident_number}</p>
                        <p className="text-xs text-gray-500">{item.type} • {item.occupation || item.owner_name || item.incident_type || ''}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )
            ))}
          </div>
        </div>
      )}

      <div className="bg-white border rounded-lg p-4">
        <h3 className="font-semibold mb-3">All Persons (Sample 50)</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="text-left px-3 py-2">Name</th>
                <th className="text-left px-3 py-2">Occupation</th>
                <th className="text-left px-3 py-2">Community</th>
                <th className="text-left px-3 py-2">Centrality</th>
                <th className="text-left px-3 py-2">Status</th>
              </tr>
            </thead>
            <tbody>
              {persons.map((p) => (
                <tr key={p.id} className="border-b hover:bg-gray-50">
                  <td className="px-3 py-2 font-medium">{p.name}</td>
                  <td className="px-3 py-2">{p.occupation}</td>
                  <td className="px-3 py-2">Cluster {p.community_id}</td>
                  <td className="px-3 py-2 font-mono text-xs">{p.degree_centrality?.toFixed(3) || '0.000'}</td>
                  <td className="px-3 py-2">
                    <span className="text-xs px-2 py-0.5 bg-yellow-100 text-yellow-800 rounded-full">{p.risk_review_status}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
