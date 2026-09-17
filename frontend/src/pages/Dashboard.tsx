import { useEffect, useState } from 'react'
import { dashboardAPI, entitiesAPI } from '../services/api'
import { Link } from 'react-router-dom'
import { Users, Network, FileText, AlertTriangle, Briefcase, MapPin, Phone, Car } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

export default function Dashboard() {
  const [data, setData] = useState<any>(null)
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [dashRes, statsRes] = await Promise.all([
        dashboardAPI.get(),
        entitiesAPI.stats()
      ])
      setData(dashRes.data)
      setStats(statsRes.data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="flex items-center justify-center h-64">Loading dashboard...</div>
  }

  const statCards = [
    { label: 'Active Cases', value: data?.stats?.active_cases || 0, icon: Briefcase, color: 'bg-blue-500' },
    { label: 'Total Entities', value: data?.stats?.entities || 0, icon: Users, color: 'bg-green-500' },
    { label: 'Relationships', value: data?.stats?.relationships || 0, icon: Network, color: 'bg-purple-500' },
    { label: 'Incidents', value: data?.stats?.incidents || 0, icon: FileText, color: 'bg-orange-500' },
    { label: 'Communities', value: data?.stats?.communities || 0, icon: MapPin, color: 'bg-indigo-500' },
    { label: 'Pattern Alerts', value: data?.stats?.anomalies || 0, icon: AlertTriangle, color: 'bg-red-500' },
  ]

  const pieData = stats ? [
    { name: 'Persons', value: stats.persons || 0 },
    { name: 'Phones', value: stats.phones || 0 },
    { name: 'Vehicles', value: stats.vehicles || 0 },
    { name: 'Organizations', value: stats.organizations || 0 },
  ] : []

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6']

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Investigator Dashboard</h1>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">DEMO / SYNTHETIC DATA - Network overview and analytical insights</p>
        </div>
        <div className="text-xs text-gray-500 bg-gray-100 dark:bg-gray-800 px-3 py-1 rounded-full">
          Last updated: {new Date().toLocaleString()}
        </div>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {statCards.map((stat) => (
          <div key={stat.label} className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
            <div className="flex items-center">
              <div className={`p-2 rounded-lg ${stat.color}`}>
                <stat.icon className="h-5 w-5 text-white" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">{stat.label}</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{stat.value}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Most Connected */}
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
          <h2 className="text-lg font-semibold mb-4">Most Connected Entities</h2>
          <div className="space-y-3">
            {data?.centrality?.degree?.slice(0, 5).map((entity: any, idx: number) => (
              <div key={idx} className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-700/50 rounded">
                <div>
                  <p className="font-medium text-sm">{entity.label}</p>
                  <p className="text-xs text-gray-500">{entity.type} • Score: {entity.score}</p>
                </div>
                <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded-full">
                  {entity.interpretation?.split(' - ')[0] || 'Connected'}
                </span>
              </div>
            ))}
          </div>
          <Link to="/analytics" className="text-sm text-blue-600 hover:underline mt-3 inline-block">View detailed analytics →</Link>
        </div>

        {/* Communities */}
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
          <h2 className="text-lg font-semibold mb-4">Detected Communities</h2>
          <div className="space-y-3">
            {data?.communities?.map((comm: any) => (
              <div key={comm.id} className="p-3 border border-gray-200 dark:border-gray-600 rounded-lg">
                <div className="flex justify-between">
                  <span className="font-medium">Cluster {comm.id + 1}</span>
                  <span className="text-xs text-gray-500">{comm.size} entities • {comm.edge_count} links</span>
                </div>
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">{comm.description}</p>
                <div className="mt-2 flex flex-wrap gap-1">
                  {comm.central_nodes?.slice(0, 3).map((node: string, i: number) => (
                    <span key={i} className="text-xs px-2 py-0.5 bg-gray-100 dark:bg-gray-700 rounded">{node}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
          <Link to="/graph" className="text-sm text-blue-600 hover:underline mt-3 inline-block">Explore in Graph →</Link>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Entity Distribution */}
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
          <h2 className="text-lg font-semibold mb-4">Entity Distribution</h2>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie data={pieData} cx="50%" cy="50%" outerRadius={80} dataKey="value" label>
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Recent Anomalies */}
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
          <h2 className="text-lg font-semibold mb-4">Pattern Alerts</h2>
          <div className="space-y-3">
            {data?.anomalies?.slice(0, 4).map((anomaly: any, idx: number) => (
              <div key={idx} className="p-3 border-l-4 border-amber-400 bg-amber-50 dark:bg-amber-900/20 rounded-r">
                <p className="font-medium text-sm">{anomaly.title}</p>
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">{anomaly.description?.substring(0, 100)}...</p>
                <div className="mt-2 flex gap-2">
                  <span className={`text-xs px-2 py-0.5 rounded ${anomaly.severity === 'HIGH' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'}`}>
                    {anomaly.severity}
                  </span>
                  <span className="text-xs text-gray-500">Confidence: {(anomaly.confidence * 100).toFixed(0)}%</span>
                </div>
              </div>
            ))}
          </div>
          <Link to="/findings" className="text-sm text-blue-600 hover:underline mt-3 inline-block">View all patterns →</Link>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
        <p className="text-sm text-blue-800 dark:text-blue-200">
          <strong>Investigator Notice:</strong> This system is an analytical assistance tool. All findings are decision-support outputs and require human verification. 
          The system does NOT automatically declare any person as criminal. Observed relationships and patterns must be reviewed by authorized investigators with supporting evidence.
        </p>
      </div>
    </div>
  )
}
