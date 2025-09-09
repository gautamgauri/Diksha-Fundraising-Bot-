import Link from 'next/link'
import { useRouter } from 'next/router'
import { ChevronRightIcon, HomeIcon } from '@heroicons/react/24/outline'

interface BreadcrumbItem {
  name: string
  href: string
  current?: boolean
}

interface BreadcrumbsProps {
  items?: BreadcrumbItem[]
  className?: string
}

export default function Breadcrumbs({ items, className = '' }: BreadcrumbsProps) {
  const router = useRouter()
  
  // Auto-generate breadcrumbs from router path if not provided
  const generateBreadcrumbs = (): BreadcrumbItem[] => {
    const pathSegments = router.asPath.split('/').filter(Boolean)
    const breadcrumbs: BreadcrumbItem[] = [
      { name: 'Pipeline', href: '/', current: router.asPath === '/' }
    ]
    
    let currentPath = ''
    pathSegments.forEach((segment, index) => {
      currentPath += `/${segment}`
      const isLast = index === pathSegments.length - 1
      
      // Convert segment to readable name
      let name = segment
      if (segment === 'donor') {
        name = 'Donor Profile'
      } else if (segment === 'templates') {
        name = 'Templates'
      } else if (segment === 'activity') {
        name = 'Activity Log'
      } else if (segment === 'analytics') {
        name = 'Analytics'
      } else if (segment === 'admin') {
        name = 'Admin'
      } else if (segment === 'users') {
        name = 'User Management'
      } else if (segment === 'settings') {
        name = 'Settings'
      } else if (segment.match(/^[a-f0-9-]+$/)) {
        // Likely a UUID or ID - try to get from context
        name = 'Details'
      } else {
        // Capitalize and replace hyphens/underscores
        name = segment.replace(/[-_]/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
      }
      
      breadcrumbs.push({
        name,
        href: currentPath,
        current: isLast
      })
    })
    
    return breadcrumbs
  }
  
  const breadcrumbItems = items || generateBreadcrumbs()
  
  // Don't show breadcrumbs on the home page
  if (breadcrumbItems.length <= 1) {
    return null
  }
  
  return (
    <nav className={`flex ${className}`} aria-label="Breadcrumb">
      <ol className="flex items-center space-x-2">
        {breadcrumbItems.map((item, index) => (
          <li key={item.href} className="flex items-center">
            {index > 0 && (
              <ChevronRightIcon className="h-4 w-4 text-gray-400 mx-2" />
            )}
            
            {item.current ? (
              <span className="text-sm font-medium text-gray-900">
                {item.name}
              </span>
            ) : (
              <Link
                href={item.href}
                className="text-sm font-medium text-gray-500 hover:text-gray-700 flex items-center"
              >
                {index === 0 && <HomeIcon className="h-4 w-4 mr-1" />}
                {item.name}
              </Link>
            )}
          </li>
        ))}
      </ol>
    </nav>
  )
}

// Helper hook for getting breadcrumb context
export function useBreadcrumbs() {
  const router = useRouter()
  
  const getBreadcrumbContext = () => {
    const pathSegments = router.asPath.split('/').filter(Boolean)
    
    return {
      currentPage: pathSegments[pathSegments.length - 1] || 'Pipeline',
      parentPage: pathSegments[pathSegments.length - 2] || null,
      isDetailPage: pathSegments.length > 2,
      isAdminPage: pathSegments.includes('admin'),
      pathDepth: pathSegments.length
    }
  }
  
  return {
    breadcrumbs: getBreadcrumbContext(),
    generateBreadcrumbs: () => {
      const pathSegments = router.asPath.split('/').filter(Boolean)
      const breadcrumbs: BreadcrumbItem[] = [
        { name: 'Pipeline', href: '/', current: router.asPath === '/' }
      ]
      
      let currentPath = ''
      pathSegments.forEach((segment, index) => {
        currentPath += `/${segment}`
        const isLast = index === pathSegments.length - 1
        
        let name = segment
        if (segment === 'donor') {
          name = 'Donor Profile'
        } else if (segment === 'templates') {
          name = 'Templates'
        } else if (segment === 'activity') {
          name = 'Activity Log'
        } else if (segment === 'analytics') {
          name = 'Analytics'
        } else if (segment === 'admin') {
          name = 'Admin'
        } else if (segment === 'users') {
          name = 'User Management'
        } else if (segment === 'settings') {
          name = 'Settings'
        } else if (segment.match(/^[a-f0-9-]+$/)) {
          name = 'Details'
        } else {
          name = segment.replace(/[-_]/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
        }
        
        breadcrumbs.push({
          name,
          href: currentPath,
          current: isLast
        })
      })
      
      return breadcrumbs
    }
  }
}

