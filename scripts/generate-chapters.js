#!/usr/bin/env node

/**
 * Chapter Generator
 * Generates chapter stubs in docs/chapters/ for each syllabus topic
 */

const fs = require('fs').promises;
const path = require('path');
const { parseSyllabus, resolveDependencies } = require('./parse-syllabus');

/**
 * Generates chapter files from parsed syllabus
 * @param {Object} syllabus - Parsed syllabus object
 * @param {string} outputDir - Output directory for chapters
 * @returns {Object} Generation results
 */
async function generateChapters(syllabus, outputDir = './docs/chapters') {
  try {
    // Ensure output directory exists
    await fs.mkdir(outputDir, { recursive: true });

    // Resolve dependencies to get proper order
    const resolvedSyllabus = resolveDependencies(syllabus);
    
    // Generate chapter files
    const generatedFiles = [];
    
    for (const topic of resolvedSyllabus.topics) {
      const fileName = `${topic.id}.mdx`;
      const filePath = path.join(outputDir, fileName);
      
      // Create MDX content with proper frontmatter
      const chapterContent = generateChapterContent(topic);
      
      await fs.writeFile(filePath, chapterContent);
      generatedFiles.push(filePath);
      
      console.log(`✅ Generated chapter: ${filePath}`);
    }
    
    return {
      success: true,
      generatedFiles,
      count: generatedFiles.length,
      syllabus: resolvedSyllabus
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
      generatedFiles: []
    };
  }
}

/**
 * Generates MDX content for a chapter
 * @param {Object} topic - Topic object
 * @returns {string} MDX content
 */
function generateChapterContent(topic) {
  const frontmatter = {
    title: topic.title,
    description: topic.description,
    hide_table_of_contents: false,
    keywords: [topic.title, ...topic.learningObjectives.slice(0, 3)],
    sidebar_position: topic.position + 1
  };

  // Convert frontmatter to YAML format
  const frontmatterStr = Object.entries(frontmatter)
    .map(([key, value]) => {
      if (Array.isArray(value)) {
        return `${key}: [${value.map(v => `"${v}"`).join(', ')}]`;
      } else if (typeof value === 'string') {
        return `${key}: "${value}"`;
      } else {
        return `${key}: ${value}`;
      }
    })
    .join('\n');

  // Create learning objectives as a list
  const learningObjectives = topic.learningObjectives
    .map(obj => `- ${obj}`)
    .join('\n');

  return `---
${frontmatterStr}
---

# ${topic.title}

${topic.description}

## Learning Objectives

${learningObjectives}

## Introduction

This chapter covers the fundamentals of ${topic.title.toLowerCase()}. It builds upon the concepts introduced in previous chapters and prepares you for the topics covered in subsequent chapters.

## Content

[Content for ${topic.title} will be generated here based on AI-assisted content generation]

## Summary

In this chapter, you learned about ${topic.title.toLowerCase()} and its importance in Physical AI and Humanoid Robotics. The concepts covered here will be essential for understanding more advanced topics in the following chapters.

## Exercises

1. [Exercise related to ${topic.title}]
2. [Practical application of concepts learned]
3. [Problem-solving using ${topic.title} principles]
`;
}

// Command line interface
if (require.main === module) {
  const args = process.argv.slice(2);
  const syllabusPath = args[0] || './sample-syllabus.json';
  const outputDir = args[1] || './docs/chapters';

  (async () => {
    console.log(`Generating chapters from syllabus: ${syllabusPath}`);
    console.log(`Output directory: ${outputDir}\n`);

    // Parse the syllabus first
    const parseResult = await parseSyllabus(syllabusPath);

    if (!parseResult.isValid) {
      console.error(`❌ Syllabus parsing failed: ${parseResult.error}`);
      process.exit(1);
    }

    // Generate chapters
    const result = await generateChapters(parseResult.syllabus, outputDir);

    if (result.success) {
      console.log(`\n✅ Successfully generated ${result.count} chapter files:`);
      result.generatedFiles.forEach(file => console.log(`  - ${file}`));
    } else {
      console.error(`❌ Chapter generation failed: ${result.error}`);
      process.exit(1);
    }
  })();
}

module.exports = {
  generateChapters,
  generateChapterContent
};
