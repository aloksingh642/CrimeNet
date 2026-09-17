import { useEffect, useState } from 'react'
import { reportsAPI, casesAPI } from '../services/api'

export default function Reports() {
  const [cases, setCases] = useState<any[]>([])
  const [selectedCase, setSelectedCase] = useState<number | null>(null)
  const [report, setReport] = useState<any>(null)

  useEffect(() => { loadCases() }, [])

  const loadCases = async () => {
    try {
      const res = await casesAPI.list()
      setCases(res.data)
    } catch (e) { console.error(e) }
  }

  const generateReport = async (caseId: number) => {
    try {
      const res = await reportsAPI.caseReport(caseId)
      setReport(res.data)
      setSelectedCase(caseId)
    } catch (e) { console.error(e) }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Investigation Reports</h1>
        <p className="text-sm text-gray-600">Evidence-backed case summaries • DEMO / SYNTHETIC DATA</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white border rounded-lg p-4">
          <h3 className="font-semibold mb-3">Select Case</h3>
          <div className="space-y-2">
            {cases.map((c) => (
              <button key={c.id} onClick={() => generateReport(c.id)} className={`w-full text-left p-3 border rounded-lg hover:bg-gray-50 ${selectedCase === c.id ? 'border-blue-500 bg-blue-50' : ''}`}>
                <p className="font-medium text-sm">{c.case_number}</p>
                <p className="text-xs text-gray-600">{c.title}</p>
              </button>
            ))}
          </div>
        </div>

        <div className="lg:col-span-2 bg-white border rounded-lg p-6">
          {!report ? (
            <div className="text-center py-12 text-gray-500">
              <p>Select a case to generate report</p>
              <p className="text-xs mt-2">Report includes network stats, communities, anomalies, evidence</p>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="border-b pb-4">
                <h2 className="text-xl font-bold">{report.case.title}</h2>
                <p className="text-sm text-gray-600">{report.case.case_number} • {report.case.status}</p>
                <p className="text-xs mt-2 px-2 py-1 bg-amber-100 text-amber-800 rounded inline-block">{report.classification}</p>
              </div>

              <div>
                <h3 className="font-semibold">Executive Summary</h3>
                <p className="text-sm mt-1">{report.executive_summary}</p>
              </div>

              <div>
                <h3 className="font-semibold">Network Statistics</h3>
                <div className="grid grid-cols-2 gap-2 mt-2 text-sm">
                  <div className="bg-gray-50 p-2 rounded">Entities: {report.network_statistics.total_entities}</div>
                  <div className="bg-gray-50 p-2 rounded">Relationships: {report.network_statistics.total_relationships}</div>
                  <div className="bg-gray-50 p-2 rounded">Density: {report.network_statistics.density}</div>
                  <div className="bg-gray-50 p-2 rounded">Communities: {report.network_statistics.communities_detected}</div>
                </div>
              </div>

              <div>
                <h3 className="font-semibold">Most Connected Entities</h3>
                <div className="space-y-1 mt-2">
                  {report.most_connected?.slice(0, 5).map((ent: any, idx: number) => (
                    <div key={idx} className="text-sm p-2 bg-gray-50 rounded flex justify-between">
                      <span>{ent.label} ({ent.type})</span><span className="font-mono">{ent.score}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="font-semibold">Detected Patterns</h3>
                <div className="space-y-2 mt-2">
                  {report.detected_patterns?.slice(0, 3).map((pat: any, idx: number) => (
                    <div key={idx} className="text-sm border-l-4 border-amber-400 bg-amber-50 p-2 rounded-r">
                      <p className="font-medium">{pat.title}</p>
                      <p className="text-xs">{pat.description}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded p-3">
                <p className="text-xs text-blue-800"><strong>Disclaimer:</strong> {report.disclaimer}</p>
              </div>

              <div className="text-xs text-gray-500 pt-4 border-t">
                Generated at {new Date(report.generated_at).toLocaleString()} by {report.generated_by}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
