import { ReactNode, useEffect, useState, Component, ErrorInfo } from 'react'
import { useSession } from 'next-auth/react'
import { useRouter } from 'next/router'
import Navigation from './Navigation'
import NotificationSystem from './NotificationSystem'

interface LayoutProps {
  children: ReactNode
  title?: string
  description?: string
  showNavigation?: boolean
}

interface ErrorBoundaryState {
  hasError: boolean
  error?: Error
}

class ErrorBoundary extends Component<{ children: ReactNode }, ErrorBoundaryState> {
  constructor(props: { children: ReactNode }) {
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
      return (
        <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
          <div className="sm:mx-auto sm:w-full sm:max-w-md">
            <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
              <div className="text-center">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">
                  Something went wrong
                </h2>
                <p className="text-gray-600 mb-6">
                  We're sorry, but something unexpected happened. Please try refreshing the page.
                </p>
                <button
                  onClick={() => window.location.reload()}
                  className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                >
                  Refresh Page
                </button>
              </div>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

export default function Layout({ 
  children, 
  title = 'Funding Bot', 
  description = 'Diksha Foundation Fundraising Management',
  showNavigation = true 
}: LayoutProps) {
  const { data: session, status } = useSession()
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Set page title
    if (title !== 'Funding Bot') {
      document.title = `${title} - Funding Bot`
    } else {
      document.title = 'Funding Bot'
    }

    // Set meta description
    const metaDescription = document.querySelector('meta[name="description"]')
    if (metaDescription) {
      metaDescription.setAttribute('content', description)
    }

    // Handle authentication redirects
    if (status === 'loading') {
      return
    }

    if (status === 'unauthenticated' && router.pathname !== '/auth/signin') {
      router.push('/auth/signin')
      return
    }

    setIsLoading(false)
  }, [session, status, router, title, description])

  if (status === 'loading' || isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  if (status === 'unauthenticated') {
    return null // Will redirect to signin
  }

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-50">
        {showNavigation && <Navigation user={session?.user as any} />}
        
        <main className={showNavigation ? 'pt-16' : ''}>
          {children}
        </main>
        
        <NotificationSystem />
      </div>
    </ErrorBoundary>
  )
}