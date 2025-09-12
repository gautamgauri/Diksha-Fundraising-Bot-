import { NextApiRequest, NextApiResponse } from 'next'

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  const healthCheck = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    environment: process.env.NODE_ENV,
    version: process.env.npm_package_version || '1.0.0',
    services: {
      database: process.env.DATABASE_URL ? 'configured' : 'not_configured',
      auth: process.env.NEXTAUTH_SECRET ? 'configured' : 'not_configured',
      backend: process.env.BACKEND_API_URL ? 'configured' : 'not_configured',
    }
  }

  // Check if critical services are configured
  const criticalServices = ['database', 'auth']
  const missingServices = criticalServices.filter(
    service => healthCheck.services[service as keyof typeof healthCheck.services] === 'not_configured'
  )

  if (missingServices.length > 0) {
    return res.status(503).json({
      ...healthCheck,
      status: 'degraded',
      message: `Missing critical services: ${missingServices.join(', ')}`
    })
  }

  res.status(200).json(healthCheck)
}


