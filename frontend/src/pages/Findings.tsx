import { useEffect, useState } from 'react'
import { findingsAPI } from '../services/api'

export default function Findings() {
  const [anomalies, setAnomalies] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadAnomalies()
  }, [])

  const loadAnomalies = async () => {
    try {
      const res = await findingsAPI.anomalies()
      setAnomalies(res.data.anomalies || res.data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const handleAction = async (id: number, action: string) => {
    try {
      await findingsAPI.review(id, action)
      loadAnomalies()
    } catch (e) {
      console.error(e)
    }
  }

  if (loading) return <div>Loading findings...</div>

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Pattern Detection & Anomalies</h1>
          <p className="text-sm text-gray-600">Explainable AI findings requiring investigator review • DEMO / SYNTHETIC DATA</p>
        </div>
        <button onClick={() => findingsAPI.generate().then(loadAnomalies)} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm">
          Generate Findings
        </button>
      </div>

      <div className="grid gap-4">
        {anomalies.map((anomaly: any, idx: number) => (
          <div key={idx} className="bg-white border rounded-lg p-4 border-l-4 border-l-amber-400">
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <h3 className="font-semibold">{anomaly.title}</h3>
                  <span className={`text-xs px-2 py-0.5 rounded-full ${anomaly.severity === 'HIGH' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'}`}>
                    {anomaly.severity}
                  </span>
                  <span className="text-xs text-gray-500">Confidence: {(anomaly.confidence * 100).toFixed(0)}%</span>
                </div>
                <p className="text-sm text-gray-700 mt-2">{anomaly.description}</p>
                
                <div className="mt-3 bg-gray-50 rounded p-3">
                  <p className="text-xs font-medium mb-2">Explainable Evidence:</p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
                    <div><span className="font-medium">WHAT:</span> {anomaly.evidence?.what || anomaly.finding_type}</div>
                    <div><span className="font-medium">WHY:</span> {anomaly.evidence?.why || 'Statistical threshold exceeded'}</div>
                    <div><span className="font-medium">WHEN:</span> {anomaly.evidence?.when || 'Recent period'}</div>
                    <div><span className="font-medium">WHO:</span> {anomaly.entities_involved?.join(', ') || anomaly.evidence?.entities?.join(', ')}</div>
                  </div>
                  {anomaly.evidence && (
                    <details className="mt-2">
                      <summary className="text-xs text-blue-600 cursor-pointer">View full evidence</summary>
                      <pre className="text-xs mt-2 bg-white p-2 rounded overflow-auto">{JSON.stringify(anomaly.evidence, null, 2)}</pre>
                    </details>
                  )}
                </div>

                <div className="mt-3 flex gap-2">
                  <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded">{anomaly.finding_type}</span>
                  {anomaly.entities_involved?.slice(0, 3).map((ent: string, i: number) => (
                    <span key={i} className="text-xs px-2 py-1 bg-gray-100 rounded">{ent}</span>
                  ))}
                </div>
              </div>
            </div>

            <div className="mt-4 flex gap-2">
              <button onClick={() => handleAction(anomaly.id || idx, 'save')} className="px-3 py-1 bg-green-600 text-white text-xs rounded hover:bg-green-700">
                Save to Case
              </button>
              <button onClick={() => handleAction(anomaly.id || idx, 'reviewed')} className="px-3 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700">
                Mark Reviewed
              </button>
              <button onClick={() => handleAction(anomaly.id || idx, 'dismiss')} className="px-3 py-1 bg-gray-200 text-gray-700 text-xs rounded hover:bg-gray-300">
                False Positive
              </button>
            </div>

            <div className="mt-3 text-xs text-gray-500 italic">
              Note: This is an analytical pattern requiring human verification. Not proof of criminal activity. Investigator must review supporting evidence.
            </div>
          </div>
        ))}
      </div>

      {anomalies.length === 0 && (
        <div className="text-center py-12 bg-white border rounded-lg">
          <p className="text-gray-500">No anomalies detected yet.</p>
          <button onClick={() => findingsAPI.generate().then(loadAnomalies)} className="mt-3 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm">
            Run Detection
          </button>
        </div>
      )}
    </div>
  )
}
