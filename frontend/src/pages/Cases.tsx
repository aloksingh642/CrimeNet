import { useEffect, useState } from 'react'
import { casesAPI } from '../services/api'
import { Link } from 'react-router-dom'
import { Plus, Search } from 'lucide-react'

export default function Cases() {
  const [cases, setCases] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreate, setShowCreate] = useState(false)
  const [newCase, setNewCase] = useState({ title: '', description: '', priority: 'MEDIUM' })

  useEffect(() => {
    loadCases()
  }, [])

  const loadCases = async () => {
    try {
      const res = await casesAPI.list()
      setCases(res.data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await casesAPI.create(newCase)
      setShowCreate(false)
      setNewCase({ title: '', description: '', priority: 'MEDIUM' })
      loadCases()
    } catch (e) {
      console.error(e)
    }
  }

  if (loading) return <div>Loading cases...</div>

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Case Management</h1>
          <p className="text-sm text-gray-600 mt-1">DEMO / SYNTHETIC DATA - Investigation cases</p>
        </div>
        <button onClick={() => setShowCreate(true)} className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          <Plus className="h-4 w-4 mr-2" /> New Case
        </button>
      </div>

      {showCreate && (
        <div className="bg-white border rounded-lg p-4">
          <h3 className="font-semibold mb-3">Create New Case</h3>
          <form onSubmit={handleCreate} className="space-y-3">
            <input
              type="text"
              placeholder="Case Title"
              value={newCase.title}
              onChange={(e) => setNewCase({ ...newCase, title: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg"
              required
            />
            <textarea
              placeholder="Description"
              value={newCase.description}
              onChange={(e) => setNewCase({ ...newCase, description: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg"
              rows={3}
            />
            <select
              value={newCase.priority}
              onChange={(e) => setNewCase({ ...newCase, priority: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg"
            >
              <option value="LOW">Low Priority</option>
              <option value="MEDIUM">Medium Priority</option>
              <option value="HIGH">High Priority</option>
            </select>
            <div className="flex gap-2">
              <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded-lg">Create</button>
              <button type="button" onClick={() => setShowCreate(false)} className="px-4 py-2 bg-gray-200 rounded-lg">Cancel</button>
            </div>
          </form>
        </div>
      )}

      <div className="bg-white rounded-lg border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Case Number</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Title</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Status</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Priority</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Investigator</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Created</th>
              </tr>
            </thead>
            <tbody>
              {cases.map((c) => (
                <tr key={c.id} className="border-b hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm font-mono">
                    <Link to={`/cases/${c.id}`} className="text-blue-600 hover:underline">{c.case_number}</Link>
                  </td>
                  <td className="px-4 py-3 text-sm">
                    <Link to={`/cases/${c.id}`} className="font-medium hover:text-blue-600">{c.title}</Link>
                    <p className="text-xs text-gray-500 truncate max-w-xs">{c.description}</p>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      c.status === 'OPEN' ? 'bg-green-100 text-green-800' :
                      c.status === 'IN_PROGRESS' ? 'bg-blue-100 text-blue-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>{c.status}</span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      c.priority === 'HIGH' ? 'bg-red-100 text-red-800' :
                      c.priority === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>{c.priority}</span>
                  </td>
                  <td className="px-4 py-3 text-sm">{c.investigator_name}</td>
                  <td className="px-4 py-3 text-sm text-gray-500">{new Date(c.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {cases.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <p>No cases found. Create a new case to get started.</p>
          <p className="text-sm mt-2">Demo includes pre-generated cases like CASE-2026-001</p>
        </div>
      )}
    </div>
  )
}
