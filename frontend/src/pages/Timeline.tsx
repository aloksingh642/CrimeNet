import { useEffect, useState } from 'react'
import { timelineAPI } from '../services/api'

export default function Timeline() {
  const [events, setEvents] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('')

  useEffect(() => {
    loadTimeline()
  }, [])

  const loadTimeline = async () => {
    try {
      const res = await timelineAPI.get({ limit: 100, event_type: filter || undefined })
      setEvents(res.data.events)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadTimeline()
  }, [filter])

  if (loading) return <div>Loading timeline...</div>

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Investigation Timeline</h1>
        <p className="text-sm text-gray-600">Chronological view of incidents, communications, transactions, documents</p>
      </div>

      <div className="bg-white border rounded-lg p-4">
        <div className="flex gap-2">
          <select value={filter} onChange={(e) => setFilter(e.target.value)} className="px-3 py-2 border rounded-lg text-sm">
            <option value="">All Events</option>
            <option value="INCIDENT">Incidents</option>
            <option value="COMMUNICATION">Communications</option>
            <option value="TRANSACTION">Transactions</option>
            <option value="DOCUMENT">Documents</option>
          </select>
          <button onClick={loadTimeline} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm">Refresh</button>
        </div>
      </div>

      <div className="bg-white border rounded-lg p-4">
        <div className="relative">
          <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200"></div>
          <div className="space-y-4">
            {events.map((event, idx) => (
              <div key={idx} className="relative flex gap-4">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-xs z-10 ${
                  event.event_type === 'INCIDENT' ? 'bg-red-500' :
                  event.event_type === 'COMMUNICATION' ? 'bg-green-500' :
                  event.event_type === 'TRANSACTION' ? 'bg-blue-500' : 'bg-gray-500'
                }`}>
                  {event.event_type[0]}
                </div>
                <div className="flex-1 pb-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-medium text-sm">{event.title}</p>
                      <p className="text-xs text-gray-600 mt-1">{event.description}</p>
                      {event.entities && event.entities.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-2">
                          {event.entities.map((ent: string, i: number) => (
                            <span key={i} className="text-xs px-2 py-0.5 bg-gray-100 rounded">{ent}</span>
                          ))}
                        </div>
                      )}
                    </div>
                    <span className="text-xs text-gray-500 whitespace-nowrap ml-4">
                      {new Date(event.timestamp).toLocaleString()}
                    </span>
                  </div>
                  {event.location && <p className="text-xs text-gray-500 mt-1">📍 {event.location}</p>}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {events.length === 0 && <div className="text-center py-8 text-gray-500">No events found</div>}
    </div>
  )
}
