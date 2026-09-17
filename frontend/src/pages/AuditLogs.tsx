import { useEffect, useState } from 'react'
import { auditAPI } from '../services/api'

export default function AuditLogs() {
  const [logs, setLogs] = useState<any[]>([])

  useEffect(() => { loadLogs() }, [])

  const loadLogs = async () => {
    try {
      const res = await auditAPI.list({ limit: 100 })
      setLogs(res.data)
    } catch (e) { console.error(e) }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Audit Logs</h1>
        <p className="text-sm text-gray-600">Investigator actions • Security & compliance</p>
      </div>

      <div className="bg-white border rounded-lg overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left px-3 py-2">Timestamp</th>
              <th className="text-left px-3 py-2">User</th>
              <th className="text-left px-3 py-2">Action</th>
              <th className="text-left px-3 py-2">Resource</th>
              <th className="text-left px-3 py-2">Details</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <tr key={log.id} className="border-b hover:bg-gray-50">
                <td className="px-3 py-2 text-xs">{new Date(log.timestamp).toLocaleString()}</td>
                <td className="px-3 py-2">{log.username}</td>
                <td className="px-3 py-2"><span className="px-2 py-0.5 bg-blue-100 text-blue-800 rounded-full text-xs">{log.action}</span></td>
                <td className="px-3 py-2">{log.resource_type} {log.resource_id ? `#${log.resource_id}` : ''}</td>
                <td className="px-3 py-2 text-xs text-gray-600 truncate max-w-xs">{log.details}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
