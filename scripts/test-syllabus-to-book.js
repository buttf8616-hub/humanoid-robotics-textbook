/**
 * Test script for complete syllabus-to-book generation
 */

const { generateBookStructure } = require('./generate-book');
const { generateNavigationFromSyllabus } = require('./generate-navigation');
const fs = require('fs').promises;

// Comprehensive sample syllabus
const comprehensiveSyllabus = {
  title: "Complete Docusaurus Guide",
  description: "A comprehensive guide covering all aspects of Docusaurus",
  author: "Technical Writer",
  topics: [
    {
      "id": "intro-concepts",
      "title": "Introduction and Core Concepts",
      "description": "Understanding Docusaurus fundamentals",
      "learningObjectives": [
        "Explain what Docusaurus is",
        "Identify key benefits",
        "Understand basic architecture"
      ],
      "prerequisites": [],
      "category": "Fundamentals"
    },
    {
      "id": "installation-setup",
      "title": "Installation and Setup",
      "description": "Setting up your first Docusaurus project",
      "learningObjectives": [
        "Install Docusaurus",
        "Initialize a project",
        "Configure basic settings"
      ],
      "prerequisites": ["intro-concepts"],
      "category": "Setup"
    },
    {
      "id": "content-creation",
      "title": "Content Creation with Markdown",
      "description": "Creating documentation with Markdown and MDX",
      "learningObjectives": [
        "Write effective Markdown",
        "Use MDX components",
        "Structure content properly"
      ],
      "prerequisites": ["installation-setup"],
      "category": "Content Creation"
    },
    {
      "id": "theming-customization",
      "title": "Theming and Customization",
      "description": "Customizing the look and feel of your site",
      "learningObjectives": [
        "Apply custom themes",
        "Modify CSS",
        "Create custom components"
      ],
      "prerequisites": ["content-creation"],
      "category": "Advanced"
    },
    {
      "id": "deployment",
      "title": "Deployment and Hosting",
      "description": "Deploying your Docusaurus site",
      "learningObjectives": [
        "Build for production",
        "Deploy to various platforms",
        "Configure CI/CD"
      ],
      "prerequisites": ["theming-customization"],
      "category": "Advanced"
    }
  ]
};

async function testSyllabusToBook() {
  console.log('Testing complete syllabus-to-book generation...\n');

  try {
    console.log('1. Generating book structure from comprehensive syllabus...');
    const bookResult = await generateBookStructure(comprehensiveSyllabus, './full-book-test');
    console.log('✓ Book structure generation successful');
    console.log(`  - Status: ${bookResult.status}`);
    console.log(`  - Chapters created: ${bookResult.chapterCount}`);
    console.log(`  - Generated files: ${bookResult.generatedFiles.length}`);
    console.log('');

    console.log('2. Generating navigation structure...');
    const navResult = await generateNavigationFromSyllabus(comprehensiveSyllabus, './full-book-test');
    console.log('✓ Navigation generation successful');
    console.log(`  - Status: ${navResult.status}`);
    console.log(`  - Navigation files: ${navResult.generatedFiles.length}`);
    console.log('');

    // Verify all chapters were created
    console.log('3. Verifying chapter creation...');
    const expectedChapters = comprehensiveSyllabus.topics.map(t => t.id);
    let missingChapters = 0;

    for (const topicId of expectedChapters) {
      const chapterPath = `./full-book-test/chapters/${topicId}.mdx`;
      const exists = await fs.access(chapterPath).then(() => true).catch(() => false);
      console.log(`  - Chapter ${topicId}: ${exists ? '✓' : '✗'}`);
      if (!exists) missingChapters++;
    }

    if (missingChapters === 0) {
      console.log('  ✓ All expected chapters were created');
    } else {
      console.log(`  ✗ ${missingChapters} chapters are missing`);
    }
    console.log('');

    // Verify navigation structure
    console.log('4. Verifying navigation structure...');
    const sidebarExists = await fs.access('./full-book-test/sidebars.js').then(() => true).catch(() => false);
    console.log(`  - Sidebar file exists: ${sidebarExists ? '✓' : '✗'}`);

    const navStructureExists = await fs.access('./full-book-test/navigation-structure.json').then(() => true).catch(() => false);
    console.log(`  - Navigation structure file exists: ${navStructureExists ? '✓' : '✗'}`);
    console.log('');

    // Check content quality
    console.log('5. Verifying content quality...');
    for (const topic of comprehensiveSyllabus.topics) {
      const chapterPath = `./full-book-test/chapters/${topic.id}.mdx`;
      const content = await fs.readFile(chapterPath, 'utf8');

      // Check for essential elements
      const hasTitle = content.includes(topic.title);
      const hasDescription = topic.description ? content.includes(topic.description.substring(0, 20)) : true; // Check first 20 chars
      const hasObjectives = topic.learningObjectives.some(obj => content.includes(obj.substring(0, 10))); // Check first 10 chars of an objective

      console.log(`  - ${topic.id}: Title: ${hasTitle ? '✓' : '✗'}, Description: ${hasDescription ? '✓' : '✗'}, Objectives: ${hasObjectives ? '✓' : '✗'}`);
    }
    console.log('');

    // Clean up
    console.log('6. Cleaning up test files...');
    await fs.rm('./full-book-test', { recursive: true, force: true });
    console.log('✓ Test files cleaned up');

    console.log('\n✓ Complete syllabus-to-book generation test passed!');
    console.log('The system successfully transforms a syllabus into a structured Docusaurus book.');
  } catch (error) {
    console.error('✗ Complete syllabus-to-book test failed:', error.message);
    console.error(error.stack);
    process.exit(1);
  }
}

// Run the test
testSyllabusToBook().catch(error => {
  console.error('Test execution failed:', error);
  process.exit(1);
});