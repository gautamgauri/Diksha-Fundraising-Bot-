import { ReactNode, useEffect, useState, Component, ErrorInfo } from 'react'
import { useSession } from 'next-auth/react'
import { useRouter } from 'next/router'
import Navigation from './Navigation'
import LoadingSpinner from './LoadingSpinner'
import Breadcrumbs from './Breadcrumbs'
import { User } from '../types'

// Error Boundary Component
interface ErrorBoundaryState {
  hasError: boolean
  error?: Error
}

class ErrorBoundary extends Component<
  { children: ReactNode; fallback?: ReactNode },
  ErrorBoundaryState
> {
  constructor(props: { children: ReactNode; fallback?: ReactNode }) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Layout Error Boundary caught an error:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
              <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <h3 className="mt-2 text-sm font-medium text-gray-900">Something went wrong</h3>
            <p className="mt-1 text-sm text-gray-500">
              An unexpected error occurred. Please refresh the page.
            </p>
            <div className="mt-6">
              <button
                onClick={() => window.location.reload()}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700"
              >
                Refresh Page
              </button>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

interface LayoutProps {
  children: ReactNode
  requiredRole?: 'viewer' | 'fundraising' | 'admin'
  requiredPermission?: keyof User['permissions']
}

export default function Layout({ children, requiredRole, requiredPermission }: LayoutProps) {
  const { data: session, status } = useSession()
  const router = useRouter()
  const [isRedirecting, setIsRedirecting] = useState(false)
  const [isOnline, setIsOnline] = useState(true)
  const [isPageLoading, setIsPageLoading] = useState(false)

  // Role-based authorization helper
  const hasPermission = (role: 'viewer' | 'fundraising' | 'admin'): boolean => {
    const user = session?.user as User
    if (!user) return false
    
    const roleHierarchy = { viewer: 0, fundraising: 1, admin: 2 }
    return roleHierarchy[user.role] >= roleHierarchy[role]
  }

  // Permission-based authorization helper
  const hasSpecificPermission = (permission: keyof User['permissions']): boolean => {
    const user = session?.user as User
    if (!user) return false
    
    // If permissions object exists, use it
    if (user.permissions) {
      return user.permissions[permission] === true
    }
    
    // Fallback to role-based permissions
    const rolePermissions = {
      viewer: ['canViewPipeline'],
      fundraising: ['canViewPipeline', 'canEditPipeline', 'canSendEmails', 'canManageTemplates'],
      admin: ['canViewPipeline', 'canEditPipeline', 'canSendEmails', 'canManageTemplates', 'canViewLogs', 'canManageUsers']
    }
    
    return rolePermissions[user.role]?.includes(permission) || false
  }

  // Handle authentication redirect with proper flow
  useEffect(() => {
    if (status === 'unauthenticated' && !isRedirecting) {
      setIsRedirecting(true)
      router.replace('/auth/signin')
    }
  }, [status, router, isRedirecting])

  // Handle online/offline detection
  useEffect(() => {
    const handleOnline = () => setIsOnline(true)
    const handleOffline = () => setIsOnline(false)

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    // Set initial state
    setIsOnline(navigator.onLine)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  // Handle page loading states
  useEffect(() => {
    const handleStart = () => setIsPageLoading(true)
    const handleComplete = () => setIsPageLoading(false)

    router.events.on('routeChangeStart', handleStart)
    router.events.on('routeChangeComplete', handleComplete)
    router.events.on('routeChangeError', handleComplete)

    return () => {
      router.events.off('routeChangeStart', handleStart)
      router.events.off('routeChangeComplete', handleComplete)
      router.events.off('routeChangeError', handleComplete)
    }
  }, [router.events])

  // Show loading spinner while checking authentication or redirecting
  if (status === 'loading' || isRedirecting) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  // Don't render anything while redirecting
  if (status === 'unauthenticated') {
    return null
  }

  // Check role-based authorization
  if (requiredRole && !hasPermission(requiredRole)) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
            <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h3 className="mt-2 text-sm font-medium text-gray-900">Access Denied</h3>
          <p className="mt-1 text-sm text-gray-500">
            You don't have permission to access this page. Required role: {requiredRole}
          </p>
        </div>
      </div>
    )
  }

  // Check permission-based authorization
  if (requiredPermission && !hasSpecificPermission(requiredPermission)) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
            <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h3 className="mt-2 text-sm font-medium text-gray-900">Access Denied</h3>
          <p className="mt-1 text-sm text-gray-500">
            You don't have the required permission: {requiredPermission}
          </p>
        </div>
      </div>
    )
  }

  const user = session?.user as User

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-50">
        {/* Offline Indicator */}
        {!isOnline && (
          <div className="bg-red-600 text-white text-center py-2 text-sm">
            <div className="flex items-center justify-center">
              <svg className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 5.636l-12.728 12.728m0-12.728l12.728 12.728" />
              </svg>
              You're currently offline. Some features may not work properly.
            </div>
          </div>
        )}

        {/* Page Loading Indicator */}
        {isPageLoading && (
          <div className="fixed top-0 left-0 right-0 z-50">
            <div className="h-1 bg-primary-600 animate-pulse"></div>
          </div>
        )}

        <header role="banner">
          <Navigation user={user} />
        </header>
        <main 
          role="main" 
          className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8"
          aria-label="Main content"
        >
          {/* Breadcrumbs */}
          <nav 
            role="navigation" 
            aria-label="Breadcrumb" 
            className="mb-6"
          >
            <Breadcrumbs />
          </nav>
          {children}
        </main>
      </div>
    </ErrorBoundary>
  )
}
