/**
 * API Testing Script
 * Tests API endpoints with sample data
 */

const axios = require('axios');

// Configuration
const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:3000';

/**
 * Test the generate-book endpoint
 */
async function testGenerateBookEndpoint() {
  console.log('Testing /api/generate-book endpoint...');

  try {
    // Sample syllabus data
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
        }
      ]
    };

    const response = await axios.post(`${API_BASE_URL}/api/generate-book`, sampleSyllabus, {
      headers: {
        'Content-Type': 'application/json'
      }
    });

    console.log('✓ /api/generate-book test passed');
    console.log('Response:', JSON.stringify(response.data, null, 2));
    return true;
  } catch (error) {
    console.error('✗ /api/generate-book test failed:', error.response?.data || error.message);
    return false;
  }
}

/**
 * Test the validate-content endpoint
 */
async function testValidateContentEndpoint() {
  console.log('\nTesting /api/validate-content endpoint...');

  try {
    // Sample content and syllabus topic for validation
    const sampleContent = `# Getting Started with Docusaurus

Docusaurus is a modern static website generator that helps create documentation sites.

## Key Benefits

- Easy to use
- Highly customizable
- Great performance

## Common Use Cases

Docusaurus is perfect for project documentation, product guides, and educational content.`;

    const sampleSyllabusTopic = {
      id: "intro-docusaurus",
      title: "Getting Started with Docusaurus",
      learningObjectives: [
        "Understand what Docusaurus is",
        "Learn the benefits of using Docusaurus",
        "Identify common use cases"
      ]
    };

    const response = await axios.post(`${API_BASE_URL}/api/validate-content`, {
      content: sampleContent,
      syllabusTopics: [sampleSyllabusTopic],
      verificationSources: ["official-docusaurus-docs"]
    }, {
      headers: {
        'Content-Type': 'application/json'
      }
    });

    console.log('✓ /api/validate-content test passed');
    console.log('Response:', JSON.stringify(response.data, null, 2));
    return true;
  } catch (error) {
    console.error('✗ /api/validate-content test failed:', error.response?.data || error.message);
    return false;
  }
}

/**
 * Test the health endpoint
 */
async function testHealthEndpoint() {
  console.log('\nTesting /health endpoint...');

  try {
    const response = await axios.get(`${API_BASE_URL}/health`);

    console.log('✓ /health test passed');
    console.log('Response:', JSON.stringify(response.data, null, 2));
    return true;
  } catch (error) {
    console.error('✗ /health test failed:', error.message);
    return false;
  }
}

/**
 * Test the API spec endpoint
 */
async function testSpecEndpoint() {
  console.log('\nTesting /api/spec endpoint...');

  try {
    const response = await axios.get(`${API_BASE_URL}/api/spec`);

    console.log('✓ /api/spec test passed');
    console.log('Response has', Object.keys(response.data).length, 'top-level properties');
    return true;
  } catch (error) {
    console.error('✗ /api/spec test failed:', error.message);
    return false;
  }
}

/**
 * Run all tests
 */
async function runAllTests() {
  console.log('Starting API tests...\n');

  const tests = [
    { name: 'Health Endpoint', fn: testHealthEndpoint },
    { name: 'API Spec Endpoint', fn: testSpecEndpoint },
    { name: 'Generate Book Endpoint', fn: testGenerateBookEndpoint },
    { name: 'Validate Content Endpoint', fn: testValidateContentEndpoint }
  ];

  const results = [];

  for (const test of tests) {
    console.log(`\n--- Running ${test.name} ---`);
    const passed = await test.fn();
    results.push({ name: test.name, passed });
  }

  // Summary
  console.log('\n--- Test Summary ---');
  const passedTests = results.filter(r => r.passed).length;
  const totalTests = results.length;

  console.log(`Tests passed: ${passedTests}/${totalTests}`);

  if (passedTests === totalTests) {
    console.log('✓ All API tests passed!');
    return true;
  } else {
    console.log(`✗ ${totalTests - passedTests} test(s) failed.`);
    return false;
  }
}

// Run tests if this file is executed directly
if (require.main === module) {
  // Check if server is running first
  console.log(`Testing API endpoints at: ${API_BASE_URL}`);

  runAllTests()
    .then(success => {
      process.exit(success ? 0 : 1);
    })
    .catch(error => {
      console.error('Test execution failed:', error);
      process.exit(1);
    });
}

module.exports = {
  testGenerateBookEndpoint,
  testValidateContentEndpoint,
  testHealthEndpoint,
  testSpecEndpoint,
  runAllTests
};