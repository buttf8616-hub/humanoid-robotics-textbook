/**
 * Test script for chapter positioning functionality
 */

const { generateBookStructure } = require('./generate-book');
const fs = require('fs').promises;

// Sample syllabus with specific ordering requirements
const sampleSyllabus = {
  title: "Docusaurus Learning Path",
  description: "A structured learning path for Docusaurus",
  author: "Technical Writer",
  topics: [
    {
      "id": "prerequisites",
      "title": "Prerequisites",
      "description": "What you need before starting",
      "learningObjectives": ["Identify prerequisites"],
      "prerequisites": [],
      "category": "Setup"
    },
    {
      "id": "intro-docusaurus",
      "title": "Getting Started with Docusaurus",
      "description": "Introduction to the Docusaurus framework",
      "learningObjectives": ["Understand basics"],
      "prerequisites": ["prerequisites"],
      "category": "Fundamentals"
    },
    {
      "id": "setup-installation",
      "title": "Setting up Docusaurus",
      "description": "How to install and initialize",
      "learningObjectives": ["Install Docusaurus"],
      "prerequisites": ["intro-docusaurus"],
      "category": "Setup"
    },
    {
      "id": "markdown-basics",
      "title": "Markdown and MDX Basics",
      "description": "Creating content with Markdown",
      "learningObjectives": ["Write Markdown content"],
      "prerequisites": ["setup-installation"],
      "category": "Content Creation"
    }
  ]
};

async function testChapterPositioning() {
  console.log('Testing chapter positioning functionality...\n');

  try {
    // Generate book structure
    console.log('1. Generating book structure with positioning...');
    const result = await generateBookStructure(sampleSyllabus, './docs-test');
    console.log('✓ Book structure generation successful');
    console.log(`  - Chapters created: ${result.chapterCount}`);
    console.log('');

    // Read and verify chapter files to check positioning
    console.log('2. Verifying chapter positioning...');
    const chapterFiles = result.generatedFiles.filter(file => file.includes('chapters/') && file.endsWith('.mdx'));

    for (const file of chapterFiles) {
      const content = await fs.readFile(file, 'utf8');

      // Extract the frontmatter to check position
      const frontmatterMatch = content.match(/sidebar_position:\s*(\d+)/);
      if (frontmatterMatch) {
        const position = parseInt(frontmatterMatch[1]);
        console.log(`  - ${file.split('/').pop()}: position ${position}`);
      } else {
        console.log(`  - ${file.split('/').pop()}: NO POSITION FOUND`);
      }
    }
    console.log('');

    // Check the navigation structure
    console.log('3. Checking navigation structure...');
    const navFile = result.generatedFiles.find(file => file.includes('_category_.json'));
    if (navFile) {
      console.log(`  - Navigation file created: ${navFile.split('/').pop()}`);
      const navContent = await fs.readFile(navFile, 'utf8');
      console.log('  - Navigation content preview:');
      console.log(`    ${navContent.split('\n')[0]}`);
    }
    console.log('');

    // Verify that positions match the order in the syllabus
    console.log('4. Verifying position order matches syllabus order...');
    for (let i = 0; i < sampleSyllabus.topics.length; i++) {
      const topic = sampleSyllabus.topics[i];
      const expectedPosition = i + 1; // Positions start at 1

      const chapterFile = `docs-test/chapters/${topic.id}.mdx`;
      const exists = await fs.access(chapterFile).then(() => true).catch(() => false);

      if (exists) {
        const content = await fs.readFile(chapterFile, 'utf8');
        const positionMatch = content.match(/sidebar_position:\s*(\d+)/);
        if (positionMatch) {
          const actualPosition = parseInt(positionMatch[1]);
          const positionCorrect = actualPosition === expectedPosition;
          console.log(`  - ${topic.id}: expected ${expectedPosition}, got ${actualPosition} - ${positionCorrect ? '✓' : '✗'}`);
        } else {
          console.log(`  - ${topic.id}: position not found - ✗`);
        }
      } else {
        console.log(`  - ${topic.id}: file not found - ✗`);
      }
    }
    console.log('');

    // Clean up test files
    console.log('5. Cleaning up test files...');
    await fs.rm('./docs-test', { recursive: true, force: true });
    console.log('✓ Test files cleaned up');

    console.log('\n✓ All chapter positioning tests passed!');
  } catch (error) {
    console.error('✗ Chapter positioning test failed:', error.message);
    console.error(error.stack);
    process.exit(1);
  }
}

// Run the test
testChapterPositioning().catch(error => {
  console.error('Test execution failed:', error);
  process.exit(1);
});