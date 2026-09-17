import { useEffect, useState } from 'react'
import { documentsAPI } from '../services/api'

export default function Documents() {
  const [docs, setDocs] = useState<any[]>([])
  const [newDoc, setNewDoc] = useState({ title: '', text: '', document_type: 'FIR' })
  const [processing, setProcessing] = useState<any>(null)

  useEffect(() => { loadDocs() }, [])

  const loadDocs = async () => {
    try {
      const res = await documentsAPI.list()
      setDocs(res.data)
    } catch (e) { console.error(e) }
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await documentsAPI.create(newDoc)
      setNewDoc({ title: '', text: '', document_type: 'FIR' })
      loadDocs()
    } catch (e) { console.error(e) }
  }

  const handleProcess = async (id: number) => {
    try {
      const res = await documentsAPI.process(id)
      setProcessing(res.data)
    } catch (e) { console.error(e) }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Document Processing</h1>
        <p className="text-sm text-gray-600">NLP entity extraction • DEMO / SYNTHETIC DATA</p>
      </div>

      <div className="bg-white border rounded-lg p-4">
        <h3 className="font-semibold mb-3">Upload / Create Document</h3>
        <form onSubmit={handleCreate} className="space-y-3">
          <input type="text" placeholder="Title" value={newDoc.title} onChange={(e) => setNewDoc({ ...newDoc, title: e.target.value })} className="w-full px-3 py-2 border rounded-lg" required />
          <select value={newDoc.document_type} onChange={(e) => setNewDoc({ ...newDoc, document_type: e.target.value })} className="w-full px-3 py-2 border rounded-lg">
            <option>FIR</option><option>Intelligence Report</option><option>Surveillance</option><option>Financial Report</option>
          </select>
          <textarea placeholder="Document text (e.g., 'Rahul Sharma was seen near Central Market with Amit Verma. Vehicle HR26AB1234 observed.')" value={newDoc.text} onChange={(e) => setNewDoc({ ...newDoc, text: e.target.value })} className="w-full px-3 py-2 border rounded-lg" rows={4} required />
          <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded-lg">Create Document</button>
        </form>
      </div>

      {processing && (
        <div className="bg-white border rounded-lg p-4">
          <h3 className="font-semibold mb-3">NLP Extraction Result</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="font-medium">Entities:</p>
              <pre className="bg-gray-50 p-2 rounded text-xs mt-1 overflow-auto max-h-64">{JSON.stringify(processing.entities, null, 2)}</pre>
            </div>
            <div>
              <p className="font-medium">Relationships:</p>
              <pre className="bg-gray-50 p-2 rounded text-xs mt-1 overflow-auto max-h-64">{JSON.stringify(processing.relationships, null, 2)}</pre>
            </div>
          </div>
        </div>
      )}

      <div className="bg-white border rounded-lg p-4">
        <h3 className="font-semibold mb-3">Documents ({docs.length})</h3>
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {docs.slice(0, 20).map((doc) => (
            <div key={doc.id} className="border rounded p-3 flex justify-between items-start">
              <div className="flex-1">
                <p className="font-medium text-sm">{doc.title}</p>
                <p className="text-xs text-gray-600 mt-1">{doc.text.substring(0, 150)}...</p>
                <p className="text-xs text-gray-500 mt-1">{doc.document_type} • {new Date(doc.uploaded_at).toLocaleDateString()} • {doc.processing_status}</p>
              </div>
              <button onClick={() => handleProcess(doc.id)} className="ml-3 px-3 py-1 bg-green-600 text-white text-xs rounded">Process NLP</button>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
