import { NextApiRequest, NextApiResponse } from 'next'
import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  try {
    // Check database connectivity
    await prisma.$queryRaw`SELECT 1`
    
    // Check backend API connectivity
    const backendUrl = process.env.BACKEND_API_URL || process.env.NEXT_PUBLIC_BACKEND_API_URL
    let backendStatus = 'unknown'
    
    if (backendUrl) {
      try {
        const response = await fetch(`${backendUrl}/health`, { 
          method: 'GET',
          timeout: 5000 
        })
        backendStatus = response.ok ? 'healthy' : 'unhealthy'
      } catch (error) {
        backendStatus = 'unreachable'
      }
    }

    const health = {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      version: process.env.npm_package_version || '1.0.0',
      environment: process.env.NODE_ENV,
      services: {
        database: 'healthy',
        backend: backendStatus,
      },
      uptime: process.uptime(),
      memory: {
        used: Math.round(process.memoryUsage().heapUsed / 1024 / 1024),
        total: Math.round(process.memoryUsage().heapTotal / 1024 / 1024),
      }
    }

    // Return 503 if any critical service is down
    if (backendStatus === 'unreachable') {
      return res.status(503).json({ ...health, status: 'degraded' })
    }

    res.status(200).json(health)
  } catch (error) {
    console.error('Health check failed:', error)
    res.status(503).json({
      status: 'unhealthy',
      timestamp: new Date().toISOString(),
      error: 'Database connection failed'
    })
  } finally {
    await prisma.$disconnect()
  }
}

