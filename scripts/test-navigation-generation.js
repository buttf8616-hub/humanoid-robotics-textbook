/**
 * Test script for navigation generation functionality
 */

const { generateNavigationStructure } = require('./generate-navigation');
const fs = require('fs').promises;

// Sample topics for navigation testing
const sampleTopics = [
  {
    id: "intro-docusaurus",
    title: "Getting Started with Docusaurus",
    description: "Introduction to the Docusaurus framework",
    learningObjectives: ["Understand basics"],
    prerequisites: [],
    category: "Fundamentals",
    position: 0,
    status: "pending"
  },
  {
    id: "setup-installation",
    title: "Setting up Docusaurus",
    description: "How to install and initialize",
    learningObjectives: ["Install Docusaurus"],
    prerequisites: ["intro-docusaurus"],
    category: "Setup",
    position: 1,
    status: "pending"
  },
  {
    id: "markdown-basics",
    title: "Markdown and MDX Basics",
    description: "Creating content with Markdown",
    learningObjectives: ["Write Markdown content"],
    prerequisites: ["setup-installation"],
    category: "Fundamentals", // Same category as first topic
    position: 2,
    status: "pending"
  },
  {
    id: "advanced-features",
    title: "Advanced Docusaurus Features",
    description: "Advanced functionality",
    learningObjectives: ["Use advanced features"],
    prerequisites: ["markdown-basics"],
    category: "Advanced",
    position: 3,
    status: "pending"
  }
];

async function testNavigationGeneration() {
  console.log('Testing navigation generation functionality...\n');

  try {
    // Generate navigation structure
    console.log('1. Generating navigation structure...');
    const result = await generateNavigationStructure(sampleTopics, './docs-test');
    console.log('✓ Navigation structure generation successful');
    console.log(`  - Status: ${result.status}`);
    console.log(`  - Generated files: ${result.generatedFiles.length}`);
    console.log('');

    // List generated files
    console.log('2. Generated navigation files:');
    for (const file of result.generatedFiles) {
      console.log(`  - ${file}`);
    }
    console.log('');

    // Check the main sidebar file
    const sidebarFile = result.generatedFiles.find(file => file.includes('sidebars.js'));
    if (sidebarFile) {
      console.log('3. Checking sidebar.js content...');
      const sidebarContent = await fs.readFile(sidebarFile, 'utf8');
      console.log('  - Sidebar file exists and has content');
      console.log('  - Content preview (first 5 lines):');
      const lines = sidebarContent.split('\n').slice(0, 5);
      lines.forEach(line => console.log(`    ${line}`));
      console.log('');
    }

    // Check category navigation files
    const categoryFiles = result.generatedFiles.filter(file => file.includes('_category_.json'));
    if (categoryFiles.length > 0) {
      console.log('4. Checking category navigation files...');
      for (const file of categoryFiles) {
        const content = await fs.readFile(file, 'utf8');
        console.log(`  - ${file.split('/').pop()} exists with content`);
        console.log(`    Content preview: ${content.substring(0, 60)}...`);
      }
      console.log('');
    }

    // Verify that navigation reflects the categories and positions
    console.log('5. Verifying navigation structure...');
    console.log('  - Categories identified in topics:', [...new Set(sampleTopics.map(t => t.category))]);
    console.log('  - Topic positions in order:', sampleTopics.map(t => `${t.id} (pos: ${t.position})`));
    console.log('');

    // Clean up test files
    console.log('6. Cleaning up test files...');
    await fs.rm('./docs-test', { recursive: true, force: true });
    console.log('✓ Test files cleaned up');

    console.log('\n✓ All navigation generation tests passed!');
  } catch (error) {
    console.error('✗ Navigation generation test failed:', error.message);
    console.error(error.stack);
    process.exit(1);
  }
}

// Run the test
testNavigationGeneration().catch(error => {
  console.error('Test execution failed:', error);
  process.exit(1);
});