import { Link, useLocation, useNavigate } from 'react-router-dom'
import { cn } from '../utils/cn'
import { 
  LayoutDashboard, 
  Briefcase, 
  Users, 
  Network, 
  BarChart3, 
  Clock, 
  FileText, 
  Shield, 
  Search,
  LogOut,
  Map,
  AlertTriangle,
  FileBarChart
} from 'lucide-react'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Cases', href: '/cases', icon: Briefcase },
  { name: 'Entities', href: '/entities', icon: Users },
  { name: 'Graph Explorer', href: '/graph', icon: Network },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'Timeline', href: '/timeline', icon: Clock },
  { name: 'Evidence', href: '/evidence', icon: Shield },
  { name: 'Documents', href: '/documents', icon: FileText },
  { name: 'Findings', href: '/findings', icon: AlertTriangle },
  { name: 'Reports', href: '/reports', icon: FileBarChart },
  { name: 'Audit Logs', href: '/audit-logs', icon: Search },
]

export default function Layout({ children }: { children: React.ReactNode }) {
  const location = useLocation()
  const navigate = useNavigate()
  const user = JSON.parse(localStorage.getItem('user') || '{}')

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex">
      {/* Sidebar */}
      <div className="w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <h1 className="text-xl font-bold text-gray-900 dark:text-white">CrimeNet</h1>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Intelligence Platform</p>
          <div className="mt-2 px-2 py-1 bg-amber-100 dark:bg-amber-900/30 text-amber-800 dark:text-amber-200 text-xs rounded font-medium">
            DEMO / SYNTHETIC DATA
          </div>
        </div>
        
        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          {navigation.map((item) => {
            const isActive = location.pathname.startsWith(item.href)
            return (
              <Link
                key={item.name}
                to={item.href}
                className={cn(
                  "flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors",
                  isActive
                    ? "bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-200"
                    : "text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                )}
              >
                <item.icon className="mr-3 h-5 w-5" />
                {item.name}
              </Link>
            )
          })}
        </nav>

        <div className="p-4 border-t border-gray-200 dark:border-gray-700">
          <div className="flex items-center mb-3">
            <div className="h-8 w-8 rounded-full bg-blue-600 flex items-center justify-center text-white text-sm font-medium">
              {user.username?.[0]?.toUpperCase() || 'U'}
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-900 dark:text-white">{user.full_name || user.username}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">{user.role}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center w-full px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md"
          >
            <LogOut className="mr-3 h-4 w-4" />
            Logout
          </button>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
        <footer className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 px-6 py-3">
          <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
            CrimeNet Intelligence — Investigator Assistance Platform | DEMO / SYNTHETIC DATA | Analytical findings require human verification
          </p>
        </footer>
      </div>
    </div>
  )
}
