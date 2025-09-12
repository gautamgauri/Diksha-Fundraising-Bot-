#!/usr/bin/env node

const { execSync } = require('child_process')
const fs = require('fs')
const path = require('path')

async function createBackup() {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
  const backupFile = `backup-${timestamp}.sql`
  
  try {
    console.log('Creating database backup...')
    
    // Create backup using pg_dump
    const command = `pg_dump "${process.env.DATABASE_URL}" > ${backupFile}`
    execSync(command, { stdio: 'inherit' })
    
    console.log(`Backup created: ${backupFile}`)
    
    // Compress backup
    const compressedFile = `${backupFile}.gz`
    execSync(`gzip ${backupFile}`, { stdio: 'inherit' })
    
    console.log(`Backup compressed: ${compressedFile}`)
    
    // Upload to cloud storage (example with AWS S3)
    if (process.env.AWS_ACCESS_KEY_ID && process.env.AWS_SECRET_ACCESS_KEY) {
      const s3Command = `aws s3 cp ${compressedFile} s3://${process.env.S3_BACKUP_BUCKET}/database-backups/`
      execSync(s3Command, { stdio: 'inherit' })
      console.log('Backup uploaded to S3')
      
      // Clean up local file
      fs.unlinkSync(compressedFile)
    }
    
    console.log('Backup completed successfully')
  } catch (error) {
    console.error('Backup failed:', error.message)
    process.exit(1)
  }
}

// Run backup if called directly
if (require.main === module) {
  createBackup()
}

module.exports = { createBackup }




