#!/usr/bin/env node

/**
 * Book Structure Generation Script
 * Creates Docusaurus-based technical book structure from parsed syllabus
 */

const fs = require('fs').promises;
const path = require('path');
const { parseSyllabus, validateSyllabus, normalizeSyllabus } = require('./parse-syllabus');

/**
 * Generates book structure from syllabus
 * @param {Object} syllabusInput - The syllabus input object
 * @param {string} outputDir - Output directory for the book
 * @returns {Object} Generation result with file paths and metadata
 */
async function generateBookStructure(syllabusInput, outputDir = './docs') {
  // Normalize and parse the syllabus
  const normalizedSyllabus = normalizeSyllabus(syllabusInput);
  const parsedTopics = parseSyllabus(normalizedSyllabus);
  validateSyllabus(parsedTopics);

  // Ensure output directories exist
  await ensureDirectory(path.join(outputDir, 'chapters'));
  await ensureDirectory(path.join(outputDir, '_category_.json'));

  const generatedFiles = [];

  // Generate chapter files for each topic
  for (const topic of parsedTopics) {
    const chapterPath = path.join(outputDir, 'chapters', `${topic.id}.mdx`);

    // Create MDX content with proper frontmatter
    const chapterContent = createChapterContent(topic);
    await fs.writeFile(chapterPath, chapterContent);
    generatedFiles.push(chapterPath);
  }

  // Generate navigation structure
  const navPath = path.join(outputDir, 'chapters', '_category_.json');
  const navContent = createNavigationStructure(parsedTopics);
  await fs.writeFile(navPath, navContent);
  generatedFiles.push(navPath);

  // Update main docs _category_.json if needed
  const mainNavPath = path.join(outputDir, '_category_.json');
  if (!await fileExists(mainNavPath)) {
    const mainNavContent = createMainNavigation();
    await fs.writeFile(mainNavPath, mainNavContent);
    generatedFiles.push(mainNavPath);
  }

  return {
    status: 'success',
    bookPath: outputDir,
    chapterCount: parsedTopics.length,
    message: `Successfully generated ${parsedTopics.length} chapters`,
    generatedFiles
  };
}

/**
 * Ensures directory exists, creates if it doesn't
 */
async function ensureDirectory(dirPath) {
  try {
    await fs.access(dirPath);
  } catch (error) {
    await fs.mkdir(dirPath, { recursive: true });
  }
}

/**
 * Checks if a file exists
 */
async function fileExists(filePath) {
  try {
    await fs.access(filePath);
    return true;
  } catch (error) {
    return false;
  }
}

/**
 * Creates MDX content for a chapter
 */
function createChapterContent(topic) {
  return `---
id: ${topic.id}
title: ${topic.title}
sidebar_position: ${topic.position + 1}
---

# ${topic.title}

${topic.description}

## Learning Objectives

${topic.learningObjectives.map(obj => `- ${obj}`).join('\\n')}

## Content

<!-- Content for this chapter will be generated using AI assistance -->

## Prerequisites

${topic.prerequisites.length > 0
  ? topic.prerequisites.map(pre => '- ' + pre).join('\\n')
  : 'No prerequisites required for this topic.'}

`;
}

/**
 * Creates navigation structure for chapters
 */
function createNavigationStructure(topics) {
  return JSON.stringify({
    label: "Chapters",
    position: 2,
    link: {
      type: "generated-index",
      description: "Learn about the various topics in this technical book."
    }
  }, null, 2);
}

/**
 * Creates main navigation structure
 */
function createMainNavigation() {
  return JSON.stringify({
    label: "Home",
    position: 1,
    link: {
      type: "generated-index",
      description: "Welcome to the Physical AI & Humanoid Robotics book."
    }
  }, null, 2);
}

// Command line interface
if (require.main === module) {
  const args = process.argv.slice(2);

  if (args.length < 2) {
    console.error('Usage: node generate-book.js <syllabus-file> <output-dir>');
    process.exit(1);
  }

  const syllabusFile = args[0];
  const outputDir = args[1];

  (async () => {
    try {
      const syllabusData = JSON.parse(await fs.readFile(syllabusFile, 'utf8'));
      const result = await generateBookStructure(syllabusData, outputDir);
      console.log(JSON.stringify(result, null, 2));
    } catch (error) {
      console.error('Error generating book structure:', error.message);
      process.exit(1);
    }
  })();
}

module.exports = {
  generateBookStructure,
  createChapterContent,
  createNavigationStructure
};