#!/usr/bin/env node

/**
 * Clean build script to remove TypeScript build cache files
 * This prevents Docker cache mount conflicts with tsconfig.tsbuildinfo
 */

const fs = require('fs');
const path = require('path');

const filesToClean = [
  'tsconfig.tsbuildinfo',
  '.next/cache',
  'node_modules/.cache'
];

console.log('🧹 Cleaning build cache files...');

filesToClean.forEach(file => {
  const filePath = path.resolve(file);
  
  try {
    if (fs.existsSync(filePath)) {
      if (fs.statSync(filePath).isDirectory()) {
        fs.rmSync(filePath, { recursive: true, force: true });
        console.log(`✅ Removed directory: ${file}`);
      } else {
        fs.unlinkSync(filePath);
        console.log(`✅ Removed file: ${file}`);
      }
    } else {
      console.log(`ℹ️  File/directory not found: ${file}`);
    }
  } catch (error) {
    console.warn(`⚠️  Could not remove ${file}: ${error.message}`);
  }
});

console.log('🎉 Build cache cleanup complete!');
