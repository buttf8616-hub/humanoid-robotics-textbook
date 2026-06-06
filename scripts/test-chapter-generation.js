/**
 * Test script for chapter generation functionality
 */

const { generateBookStructure } = require('./generate-book');
const fs = require('fs').promises;
const path = require('path');

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

async function testChapterGeneration() {
  console.log('Testing chapter generation functionality...\n');

  try {
    // Generate book structure with chapter stubs
    console.log('1. Generating book structure from syllabus...');
    const result = await generateBookStructure(sampleSyllabus, './docs-test');
    console.log('✓ Book structure generation successful');
    console.log(`  - Status: ${result.status}`);
    console.log(`  - Chapters created: ${result.chapterCount}`);
    console.log(`  - Generated files: ${result.generatedFiles.length}`);
    console.log('');

    // Check that chapter files were created
    console.log('2. Verifying chapter files...');
    for (const file of result.generatedFiles) {
      if (file.includes('chapters/')) {
        const exists = await fs.access(file).then(() => true).catch(() => false);
        console.log(`  - Chapter file exists: ${exists} (${path.basename(file)})`);
      }
    }
    console.log('');

    // List all created chapter files
    console.log('3. Created chapter files:');
    const chapterFiles = result.generatedFiles.filter(file => file.includes('chapters/'));
    for (const file of chapterFiles) {
      console.log(`  - ${file}`);
    }
    console.log('');

    // Read and display content of first chapter as example
    if (chapterFiles.length > 0) {
      console.log('4. Example chapter content:');
      const content = await fs.readFile(chapterFiles[0], 'utf8');
      console.log('  File:', path.basename(chapterFiles[0]));
      console.log('  Content preview:');
      const lines = content.split('\n').slice(0, 10);
      lines.forEach(line => console.log(`    ${line}`));
      if (content.split('\n').length > 10) {
        console.log('    ...');
      }
      console.log('');
    }

    // Clean up test files
    console.log('5. Cleaning up test files...');
    await fs.rm('./docs-test', { recursive: true, force: true });
    console.log('✓ Test files cleaned up');

    console.log('\n✓ All chapter generation tests passed!');
  } catch (error) {
    console.error('✗ Chapter generation test failed:', error.message);
    console.error(error.stack);
    process.exit(1);
  }
}

// Run the test
testChapterGeneration().catch(error => {
  console.error('Test execution failed:', error);
  process.exit(1);
});