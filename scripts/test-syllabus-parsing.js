/**
 * Test script for syllabus parsing functionality
 */

const { parseSyllabus, normalizeSyllabus } = require('./parse-syllabus');

// Sample syllabus data for testing
const sampleSyllabus = {
  title: "Introduction to Docusaurus",
  description: "A comprehensive guide to getting started with Docusaurus",
  author: "Technical Writer",
  topics: [
    {
      "id": "intro-docusaurus",
      "title": "Getting Started with Docusaurus",
      "description": "Introduction to the Docusaurus framework and its core concepts",
      "learningObjectives": [
        "Understand what Docusaurus is",
        "Learn the benefits of using Docusaurus",
        "Identify common use cases"
      ],
      "prerequisites": [],
      "category": "Fundamentals"
    },
    {
      "id": "setup-installation",
      "title": "Setting up Docusaurus",
      "description": "How to install and initialize a Docusaurus project",
      "learningObjectives": [
        "Install Docusaurus using npm",
        "Initialize a new Docusaurus project",
        "Understand the project structure"
      ],
      "prerequisites": ["intro-docusaurus"],
      "category": "Setup"
    }
  ]
};

console.log('Testing syllabus parsing functionality...\n');

try {
  // Test normalization
  console.log('1. Testing syllabus normalization...');
  const normalized = normalizeSyllabus(sampleSyllabus);
  console.log('✓ Normalization successful');
  console.log(`  - Title: ${normalized.title}`);
  console.log(`  - Number of topics: ${normalized.topics.length}\n`);

  // Test parsing
  console.log('2. Testing syllabus parsing...');
  const parsed = parseSyllabus(normalized);
  console.log('✓ Parsing successful');
  console.log(`  - Number of parsed topics: ${parsed.length}`);

  // Display parsed topic information
  parsed.forEach((topic, index) => {
    console.log(`  Topic ${index + 1}:`);
    console.log(`    - ID: ${topic.id}`);
    console.log(`    - Title: ${topic.title}`);
    console.log(`    - Category: ${topic.category}`);
    console.log(`    - Position: ${topic.position}`);
    console.log(`    - Learning Objectives: ${topic.learningObjectives.length}`);
    console.log(`    - Prerequisites: ${topic.prerequisites.length}`);
    console.log('');
  });

  console.log('✓ All syllabus parsing tests passed!');
} catch (error) {
  console.error('✗ Syllabus parsing test failed:', error.message);
  process.exit(1);
}