import NextAuth, { NextAuthOptions } from 'next-auth'
import GoogleProvider from 'next-auth/providers/google'
import { PrismaAdapter } from '@next-auth/prisma-adapter'
import { PrismaClient } from '@prisma/client'
import { Role } from '@prisma/client'

const prisma = new PrismaClient()

export const authOptions: NextAuthOptions = {
  adapter: PrismaAdapter(prisma),
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
      authorization: {
        params: {
          prompt: "consent",
          access_type: "offline",
          response_type: "code"
        }
      }
    }),
  ],
  callbacks: {
    async signIn({ user, account, profile }) {
      // Only allow users from your organization domain
      const allowedDomains = process.env.ALLOWED_EMAIL_DOMAINS?.split(',') || ['dikshafoundation.org']
      const userDomain = user.email?.split('@')[1]
      
      if (!userDomain || !allowedDomains.includes(userDomain)) {
        console.log(`Sign in blocked for domain: ${userDomain}`)
        return false
      }
      
      return true
    },
    async session({ session, user }) {
      // Add user role and ID to session
      if (session.user) {
        session.user.id = user.id
        session.user.role = user.role as Role
        session.user.lastLoginAt = user.lastLoginAt?.toISOString()
      }
      return session
    },
    async jwt({ token, user, account }) {
      // Update last login time
      if (user) {
        await prisma.user.update({
          where: { id: user.id },
          data: { lastLoginAt: new Date() }
        })
      }
      return token
    }
  },
  pages: {
    signIn: '/auth/signin',
    error: '/auth/error',
  },
  session: {
    strategy: 'database',
    maxAge: 30 * 24 * 60 * 60, // 30 days
  },
  events: {
    async signIn({ user, account, profile, isNewUser }) {
      console.log(`User ${user.email} signed in${isNewUser ? ' (new user)' : ''}`)
    },
    async signOut({ session, token }) {
      console.log(`User signed out`)
    }
  },
  debug: process.env.NODE_ENV === 'development',
}

export default NextAuth(authOptions)