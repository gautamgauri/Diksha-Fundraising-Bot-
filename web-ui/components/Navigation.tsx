import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/router'
import { signOut } from 'next-auth/react'
import { 
  HomeIcon, 
  UsersIcon, 
  DocumentTextIcon, 
  ClipboardDocumentListIcon,
  Cog6ToothIcon,
  Bars3Icon,
  XMarkIcon,
  UserCircleIcon,
  BellIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline'
import { User } from '@/types'
import NotificationSystem from './NotificationSystem'

interface NavigationProps {
  user: User | undefined
  loading?: boolean
  notificationCount?: number
}

// Role hierarchy for access control
const ROLE_HIERARCHY = {
  viewer: 0,
  fundraising: 1,
  admin: 2
} as const

// Navigation items with role requirements
const navigation = [
  { 
    name: 'Pipeline', 
    href: '/', 
    icon: HomeIcon, 
    requiredRole: 'viewer' as const,
    description: 'Manage donor pipeline and track relationships'
  },
  { 
    name: 'Donors', 
    href: '/donors', 
    icon: UsersIcon, 
    requiredRole: 'viewer' as const,
    description: 'Browse and search donor profiles'
  },
  { 
    name: 'Templates', 
    href: '/templates', 
    icon: DocumentTextIcon, 
    requiredRole: 'fundraising' as const,
    description: 'Manage email templates and documents'
  },
  { 
    name: 'Activity Log', 
    href: '/activity', 
    icon: ClipboardDocumentListIcon, 
    requiredRole: 'fundraising' as const,
    description: 'Track user actions and system activity'
  },
  { 
    name: 'Analytics', 
    href: '/analytics', 
    icon: ChartBarIcon, 
    requiredRole: 'fundraising' as const,
    description: 'View fundraising metrics and reports'
  },
]

const adminNavigation = [
  { 
    name: 'User Management', 
    href: '/admin/users', 
    icon: UsersIcon, 
    requiredRole: 'admin' as const,
    description: 'Manage user accounts and permissions'
  },
  { 
    name: 'Settings', 
    href: '/admin/settings', 
    icon: Cog6ToothIcon, 
    requiredRole: 'admin' as const,
    description: 'Configure system settings and integrations'
  },
]

export default function Navigation({ user, loading = false, notificationCount = 0 }: NavigationProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const router = useRouter()

  // Role-based access control helper
  const canAccess = (requiredRole: keyof typeof ROLE_HIERARCHY): boolean => {
    if (!user) return false
    return ROLE_HIERARCHY[user.role as keyof typeof ROLE_HIERARCHY] >= ROLE_HIERARCHY[requiredRole]
  }

  // Filter navigation based on user role
  const accessibleNavigation = navigation.filter(item => canAccess(item.requiredRole))
  const accessibleAdminNavigation = adminNavigation.filter(item => canAccess(item.requiredRole))
  const allNavigation = [...accessibleNavigation, ...accessibleAdminNavigation]

  const handleSignOut = () => {
    signOut({ callbackUrl: '/auth/signin' })
  }

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <Link href="/" className="text-xl font-bold text-primary-600">
                Funding Bot
              </Link>
            </div>
            <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
              {allNavigation.map((item) => {
                const isActive = router.pathname === item.href
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${
                      isActive
                        ? 'border-primary-500 text-gray-900'
                        : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                    }`}
                  >
                    <item.icon className="h-4 w-4 mr-2" />
                    {item.name}
                  </Link>
                )
              })}
            </div>
          </div>

          {/* User menu */}
          <div className="hidden sm:ml-6 sm:flex sm:items-center">
            <div className="ml-3 relative">
              <div className="flex items-center space-x-4">
                {/* Notifications */}
                <NotificationSystem userId={user?.id} />
                
                {/* User info */}
                <div className="flex items-center space-x-2">
                  <UserCircleIcon className="h-6 w-6 text-gray-400" />
                  <div className="text-sm">
                    {loading ? (
                      <div className="animate-pulse">
                        <div className="h-4 bg-gray-200 rounded w-20 mb-1"></div>
                        <div className="h-3 bg-gray-200 rounded w-16"></div>
                      </div>
                    ) : (
                      <>
                        <div className="font-medium text-gray-900">{user?.name}</div>
                        <div className="text-gray-500 capitalize">{user?.role}</div>
                      </>
                    )}
                  </div>
                </div>
                
                <button
                  onClick={handleSignOut}
                  className="text-gray-500 hover:text-gray-700 text-sm font-medium"
                >
                  Sign out
                </button>
              </div>
            </div>
          </div>

          {/* Mobile menu button */}
          <div className="sm:hidden flex items-center">
            <button
              type="button"
              className="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              <span className="sr-only">Open main menu</span>
              {mobileMenuOpen ? (
                <XMarkIcon className="block h-6 w-6" />
              ) : (
                <Bars3Icon className="block h-6 w-6" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      {mobileMenuOpen && (
        <div className="sm:hidden">
          <div className="pt-2 pb-3 space-y-1">
            {allNavigation.map((item) => {
              const isActive = router.pathname === item.href
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`block pl-3 pr-4 py-2 border-l-4 text-base font-medium ${
                    isActive
                      ? 'bg-primary-50 border-primary-500 text-primary-700'
                      : 'border-transparent text-gray-500 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-700'
                  }`}
                  onClick={() => setMobileMenuOpen(false)}
                >
                  <div className="flex items-center">
                    <item.icon className="h-5 w-5 mr-3" />
                    {item.name}
                  </div>
                </Link>
              )
            })}
          </div>
          <div className="pt-4 pb-3 border-t border-gray-200">
            <div className="flex items-center px-4">
              <UserCircleIcon className="h-8 w-8 text-gray-400" />
              <div className="ml-3">
                {loading ? (
                  <div className="animate-pulse">
                    <div className="h-4 bg-gray-200 rounded w-24 mb-2"></div>
                    <div className="h-3 bg-gray-200 rounded w-16"></div>
                  </div>
                ) : (
                  <>
                    <div className="text-base font-medium text-gray-800">{user?.name}</div>
                    <div className="text-sm font-medium text-gray-500 capitalize">{user?.role}</div>
                  </>
                )}
              </div>
            </div>
            <div className="mt-3 px-2">
              <button
                onClick={handleSignOut}
                className="block px-3 py-2 rounded-md text-base font-medium text-gray-500 hover:text-gray-800 hover:bg-gray-100"
              >
                Sign out
              </button>
            </div>
          </div>
        </div>
      )}
    </nav>
  )
}
