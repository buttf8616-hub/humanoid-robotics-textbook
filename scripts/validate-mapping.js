#!/usr/bin/env node

/**
 * Mapping Validator
 * Validates one-to-one mapping between syllabus topics and chapter files
 */

const fs = require('fs').promises;
const path = require('path');
const { parseSyllabus } = require('./parse-syllabus');

/**
 * Validates the mapping between syllabus topics and chapter files
 * @param {Object} syllabus - Parsed syllabus object
 * @param {string} chaptersDir - Directory containing chapter files
 * @returns {Object} Validation results
 */
async function validateMapping(syllabus, chaptersDir = './docs/chapters') {
  try {
    // Get all chapter files
    const chapterFiles = await getChapterFiles(chaptersDir);
    
    // Create maps for validation
    const topicIds = new Set(syllabus.topics.map(t => t.id));
    const chapterIds = new Set(chapterFiles.map(f => path.parse(f).name));
    
    // Find mismatches
    const missingChapters = [...topicIds].filter(id => !chapterIds.has(id));
    const extraChapters = [...chapterIds].filter(id => !topicIds.has(id));
    
    // Check for duplicates
    const duplicateTopics = findDuplicates(syllabus.topics, 'id');
    const duplicateFiles = findDuplicates(chapterFiles.map(f => path.parse(f).name));
    
    const isValid = missingChapters.length === 0 && 
                   extraChapters.length === 0 && 
                   duplicateTopics.length === 0 && 
                   duplicateFiles.length === 0;
    
    return {
      isValid,
      mapping: {
        topicCount: syllabus.topics.length,
        chapterCount: chapterFiles.length,
        topicIds: [...topicIds],
        chapterIds: [...chapterIds]
      },
      issues: {
        missingChapters,
        extraChapters,
        duplicateTopics,
        duplicateFiles
      },
      stats: {
        hasMissingChapters: missingChapters.length > 0,
        hasExtraChapters: extraChapters.length > 0,
        hasDuplicateTopics: duplicateTopics.length > 0,
        hasDuplicateFiles: duplicateFiles.length > 0
      }
    };
  } catch (error) {
    return {
      isValid: false,
      error: error.message,
      mapping: null,
      issues: null,
      stats: null
    };
  }
}

/**
 * Gets all chapter files from the chapters directory recursively
 * @param {string} dir - Directory to scan
 * @returns {Array} Array of file paths
 */
async function getChapterFiles(dir) {
  const entries = await fs.readdir(dir, { withFileTypes: true });
  let files = [];
  
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    
    if (entry.isDirectory()) {
      // Recursively scan subdirectories (like category directories)
      const subDirFiles = await getChapterFiles(fullPath);
      files = files.concat(subDirFiles);
    } else if (entry.name.endsWith('.mdx')) {
      files.push(fullPath);
    }
  }
  
  return files;
}

/**
 * Finds duplicate values in an array or array of objects
 * @param {Array} arr - Array to check for duplicates
 * @param {string} key - Key to check if array contains objects
 * @returns {Array} Array of duplicate values
 */
function findDuplicates(arr, key = null) {
  const counts = new Map();
  const duplicates = [];
  
  for (const item of arr) {
    const value = key ? item[key] : item;
    const count = counts.get(value) || 0;
    counts.set(value, count + 1);
  }
  
  for (const [value, count] of counts) {
    if (count > 1) {
      duplicates.push(value);
    }
  }
  
  return duplicates;
}

// Command line interface
if (require.main === module) {
  const args = process.argv.slice(2);
  const syllabusPath = args[0] || './sample-syllabus.json';
  const chaptersDir = args[1] || './docs/chapters';

  (async () => {
    console.log(`Validating mapping between syllabus and chapters...`);
    console.log(`Syllabus: ${syllabusPath}`);
    console.log(`Chapters directory: ${chaptersDir}\n`);

    // Parse the syllabus
    const parseResult = await parseSyllabus(syllabusPath);

    if (!parseResult.isValid) {
      console.error(`❌ Syllabus parsing failed: ${parseResult.error}`);
      process.exit(1);
    }

    // Validate mapping
    const result = await validateMapping(parseResult.syllabus, chaptersDir);

    if (result.isValid) {
      console.log('✅ Mapping validation passed!');
      console.log(`Topics: ${result.mapping.topicCount}, Chapters: ${result.mapping.chapterCount}`);
      console.log('Each syllabus topic has a corresponding chapter file.');
    } else {
      console.log('❌ Mapping validation failed!');
      
      if (result.issues.missingChapters.length > 0) {
        console.log(`Missing chapters for topics: ${result.issues.missingChapters.join(', ')}`);
      }
      
      if (result.issues.extraChapters.length > 0) {
        console.log(`Extra chapters (no corresponding topic): ${result.issues.extraChapters.join(', ')}`);
      }
      
      if (result.issues.duplicateTopics.length > 0) {
        console.log(`Duplicate topic IDs: ${result.issues.duplicateTopics.join(', ')}`);
      }
      
      if (result.issues.duplicateFiles.length > 0) {
        console.log(`Duplicate chapter files: ${result.issues.duplicateFiles.join(', ')}`);
      }
      
      process.exit(1);
    }
  })();
}

module.exports = {
  validateMapping,
  getChapterFiles,
  findDuplicates
};
