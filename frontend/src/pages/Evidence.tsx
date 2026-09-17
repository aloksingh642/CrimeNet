import { useState } from 'react'
import api from '../services/api'

export default function Evidence() {
  const [source, setSource] = useState('')
  const [target, setTarget] = useState('')
  const [evidence, setEvidence] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const searchEvidence = async () => {
    if (!source || !target) return
    setLoading(true)
    try {
      const res = await api.get(`/api/evidence/relationship/${source}/${target}`)
      setEvidence(res.data)
    } catch (e) { console.error(e) }
    finally { setLoading(false) }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Evidence Explorer</h1>
        <p className="text-sm text-gray-600">Trace every relationship back to source evidence • Explainable AI</p>
      </div>

      <div className="bg-white border rounded-lg p-4">
        <h3 className="font-semibold mb-3">Find Supporting Evidence</h3>
        <div className="flex gap-2">
          <input type="text" placeholder="Source entity (e.g., Rahul Sharma or phone)" value={source} onChange={(e) => setSource(e.target.value)} className="flex-1 px-3 py-2 border rounded-lg" />
          <input type="text" placeholder="Target entity" value={target} onChange={(e) => setTarget(e.target.value)} className="flex-1 px-3 py-2 border rounded-lg" />
          <button onClick={searchEvidence} disabled={loading} className="px-6 py-2 bg-blue-600 text-white rounded-lg disabled:opacity-50">
            {loading ? 'Searching...' : 'Search Evidence'}
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-2">Example: Search "Rahul" and "Amit" to see communications, shared locations, vehicles</p>
      </div>

      {evidence && (
        <div className="bg-white border rounded-lg p-4">
          <h3 className="font-semibold mb-3">Evidence for: {evidence.source} → {evidence.target} ({evidence.total} records)</h3>
          <div className="space-y-3">
            {evidence.evidences.map((ev: any, idx: number) => (
              <div key={idx} className="border rounded-lg p-3">
                <div className="flex justify-between">
                  <span className="font-medium text-sm">{ev.title}</span>
                  <span className="text-xs px-2 py-0.5 bg-green-100 text-green-800 rounded">{ev.confidence} Confidence</span>
                </div>
                <p className="text-sm text-gray-600 mt-1">{ev.content}</p>
                <p className="text-xs text-gray-500 mt-1">{ev.timestamp ? new Date(ev.timestamp).toLocaleString() : ''} • Type: {ev.type}</p>
              </div>
            ))}
          </div>
          {evidence.evidences.length === 0 && <p className="text-sm text-gray-500">No direct evidence found. Try broader search terms.</p>}
        </div>
      )}

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="font-medium text-blue-900 text-sm">Evidence Principle</h4>
        <p className="text-xs text-blue-800 mt-1">
          Every analytical relationship must be traceable to source evidence: communication records, transactions, vehicle sightings, location overlaps, document mentions.
          Never create relationship without evidence_id where possible.
        </p>
      </div>
    </div>
  )
}
