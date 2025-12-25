#!/usr/bin/env node

/**
 * Syllabus-to-Book Generation Test
 * Tests the complete syllabus-to-book generation process with sample input
 */

const { parseSyllabus, resolveDependencies } = require('./parse-syllabus');
const { generateChapters } = require('./generate-chapters');
const { generateNavigation } = require('./generate-navigation');
const { validateMapping } = require('./validate-mapping');

/**
 * Tests the complete syllabus-to-book generation process
 * @param {string} syllabusPath - Path to the syllabus file
 * @param {string} outputDir - Output directory for generated book
 * @returns {Object} Test results
 */
async function testSyllabusToBookGeneration(syllabusPath, outputDir = './docs/chapters') {
  const testResults = {
    testName: 'Syllabus-to-Book Generation Test',
    timestamp: new Date().toISOString(),
    passed: true,
    results: [],
    errors: []
  };

  try {
    // Step 1: Parse syllabus
    console.log('Step 1: Parsing syllabus...');
    const parseResult = await parseSyllabus(syllabusPath);
    
    if (!parseResult.isValid) {
      throw new Error(`Syllabus parsing failed: ${parseResult.error}`);
    }
    
    testResults.results.push({
      step: 'Parse syllabus',
      status: 'PASS',
      details: `Parsed ${parseResult.stats.topicCount} topics`
    });
    
    console.log('✅ Syllabus parsed successfully\n');

    // Step 2: Resolve dependencies
    console.log('Step 2: Resolving topic dependencies...');
    const resolvedSyllabus = resolveDependencies(parseResult.syllabus);
    
    testResults.results.push({
      step: 'Resolve dependencies',
      status: 'PASS',
      details: `Resolved dependencies for ${resolvedSyllabus.topics.length} topics`
    });
    
    console.log('✅ Dependencies resolved successfully\n');

    // Step 3: Generate chapters
    console.log('Step 3: Generating chapter files...');
    const chapterResult = await generateChapters(resolvedSyllabus, outputDir);
    
    if (!chapterResult.success) {
      throw new Error(`Chapter generation failed: ${chapterResult.error}`);
    }
    
    testResults.results.push({
      step: 'Generate chapters',
      status: 'PASS',
      details: `Generated ${chapterResult.count} chapter files`
    });
    
    console.log('✅ Chapters generated successfully\n');

    // Step 4: Generate navigation
    console.log('Step 4: Generating navigation structure...');
    const navResult = await generateNavigation(resolvedSyllabus, outputDir);
    
    if (!navResult.success) {
      throw new Error(`Navigation generation failed: ${navResult.error}`);
    }
    
    testResults.results.push({
      step: 'Generate navigation',
      status: 'PASS',
      details: `Generated navigation for ${navResult.categoryCount} categories`
    });
    
    console.log('✅ Navigation structure generated successfully\n');

    // Step 5: Validate mapping
    console.log('Step 5: Validating topic-to-chapter mapping...');
    const mappingResult = await validateMapping(resolvedSyllabus, outputDir);
    
    if (!mappingResult.isValid) {
      throw new Error(`Mapping validation failed: ${JSON.stringify(mappingResult.issues, null, 2)}`);
    }
    
    testResults.results.push({
      step: 'Validate mapping',
      status: 'PASS',
      details: 'One-to-one mapping validated successfully'
    });
    
    console.log('✅ Mapping validation passed\n');

    // Step 6: Final verification
    console.log('Step 6: Final verification...');
    const finalStats = {
      totalTopics: resolvedSyllabus.topics.length,
      totalChapters: chapterResult.count,
      totalCategories: navResult.categoryCount,
      hasPrerequisites: resolvedSyllabus.topics.some(t => t.prerequisites.length > 0)
    };

    testResults.results.push({
      step: 'Final verification',
      status: 'PASS',
      details: `Final stats: ${JSON.stringify(finalStats, null, 2)}`
    });

    console.log('✅ Final verification passed\n');

    testResults.summary = {
      totalSteps: testResults.results.length,
      passedSteps: testResults.results.filter(r => r.status === 'PASS').length,
      failedSteps: testResults.results.filter(r => r.status === 'FAIL').length,
      overallStatus: 'PASS',
      stats: finalStats
    };

  } catch (error) {
    testResults.passed = false;
    testResults.errors.push(error.message);
    
    testResults.summary = {
      totalSteps: testResults.results.length + 1,
      passedSteps: testResults.results.filter(r => r.status === 'PASS').length,
      failedSteps: testResults.results.filter(r => r.status === 'FAIL').length + 1,
      overallStatus: 'FAIL',
      error: error.message
    };
  }

  return testResults;
}

// Command line interface
if (require.main === module) {
  const args = process.argv.slice(2);
  const syllabusPath = args[0] || './sample-syllabus.json';
  const outputDir = args[1] || './docs/chapters';

  (async () => {
    console.log(`Running Syllabus-to-Book Generation Test`);
    console.log(`Syllabus: ${syllabusPath}`);
    console.log(`Output directory: ${outputDir}\n`);

    const results = await testSyllabusToBookGeneration(syllabusPath, outputDir);

    console.log('='.repeat(60));
    console.log('TEST RESULTS');
    console.log('='.repeat(60));
    
    if (results.passed) {
      console.log('🎉 ALL TESTS PASSED!');
      console.log(`Overall Status: ${results.summary.overallStatus}`);
      console.log(`Steps Passed: ${results.summary.passedSteps}/${results.summary.totalSteps}`);
      console.log(`Topics Processed: ${results.summary.stats.totalTopics}`);
      console.log(`Chapters Generated: ${results.summary.stats.totalChapters}`);
      console.log(`Categories Created: ${results.summary.stats.totalCategories}`);
    } else {
      console.log('❌ TESTS FAILED!');
      console.log(`Overall Status: ${results.summary.overallStatus}`);
      console.log(`Steps Passed: ${results.summary.passedSteps}/${results.summary.totalSteps}`);
      console.log(`Error: ${results.summary.error}`);
    }

    console.log('\nDetailed Results:');
    results.results.forEach((result, index) => {
      console.log(`${index + 1}. ${result.step}: ${result.status}`);
      console.log(`   Details: ${result.details}`);
    });

    if (results.errors.length > 0) {
      console.log('\nErrors:');
      results.errors.forEach(error => console.log(`- ${error}`));
    }

    process.exit(results.passed ? 0 : 1);
  })();
}

module.exports = {
  testSyllabusToBookGeneration
};
