import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { casesAPI, reportsAPI } from '../services/api'

export default function CaseDetail() {
  const { id } = useParams()
  const [caseData, setCaseData] = useState<any>(null)
  const [report, setReport] = useState<any>(null)

  useEffect(() => { if (id) loadCase() }, [id])

  const loadCase = async () => {
    try {
      const res = await casesAPI.get(parseInt(id!))
      setCaseData(res.data)
      const repRes = await reportsAPI.caseReport(parseInt(id!))
      setReport(repRes.data)
    } catch (e) { console.error(e) }
  }

  if (!caseData) return <div>Loading case...</div>

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">{caseData.case_number}: {caseData.title}</h1>
        <p className="text-sm text-gray-600">{caseData.description}</p>
        <div className="flex gap-2 mt-2">
          <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded-full">{caseData.status}</span>
          <span className="text-xs px-2 py-1 bg-yellow-100 text-yellow-800 rounded-full">{caseData.priority}</span>
          <span className="text-xs text-gray-500">Investigator: {caseData.investigator_name}</span>
        </div>
      </div>

      {report && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white border rounded-lg p-4">
            <h3 className="font-semibold mb-3">Network Overview</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between"><span>Entities:</span><span className="font-medium">{report.network_statistics.total_entities}</span></div>
              <div className="flex justify-between"><span>Relationships:</span><span className="font-medium">{report.network_statistics.total_relationships}</span></div>
              <div className="flex justify-between"><span>Communities:</span><span className="font-medium">{report.network_statistics.communities_detected}</span></div>
              <div className="flex justify-between"><span>Density:</span><span className="font-medium">{report.network_statistics.density}</span></div>
            </div>
          </div>

          <div className="bg-white border rounded-lg p-4">
            <h3 className="font-semibold mb-3">Most Connected</h3>
            <div className="space-y-2">
              {report.most_connected?.slice(0, 5).map((e: any, idx: number) => (
                <div key={idx} className="text-sm p-2 bg-gray-50 rounded flex justify-between">
                  <span>{e.label}</span><span className="text-xs">{e.score}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="lg:col-span-2 bg-white border rounded-lg p-4">
            <h3 className="font-semibold mb-3">Investigation Workflow</h3>
            <ol className="list-decimal list-inside space-y-1 text-sm text-gray-700">
              <li>Case created with synthetic FIR documents</li>
              <li>NLP extracted entities: persons, locations, vehicles, phones</li>
              <li>Entity resolution identified possible duplicates</li>
              <li>Graph constructed with evidence-backed relationships</li>
              <li>Network metrics calculated: centrality, communities, density</li>
              <li>Anomaly detection flagged unusual patterns</li>
              <li>Investigator reviews evidence in Evidence Explorer</li>
              <li>Findings saved to case and report generated</li>
            </ol>
          </div>
        </div>
      )}

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-sm text-blue-800">
          <strong>Demo Scenario:</strong> This case demonstrates cross-community analysis. The system shows multiple communities with bridge entities,
          communication relationships, financial links, and location overlaps. All data is synthetic and for demonstration only.
        </p>
      </div>
    </div>
  )
}
