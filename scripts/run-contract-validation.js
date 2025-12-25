#!/usr/bin/env node

/**
 * Script to run API contract validation
 */

const { performComprehensiveValidation } = require('./validate-api-contracts');

async function runValidation() {
  const baseUrl = process.argv[2] || 'http://localhost:3000';

  console.log(`Starting API contract validation at: ${baseUrl}\n`);

  try {
    const results = await performComprehensiveValidation(baseUrl);

    console.log('API Contract Validation Results:');
    console.log('===============================');
    console.log(results.summary);

    if (results.overallCompliance < 90) {
      console.log('\n⚠️  Warning: API compliance is below 90% threshold');
      process.exit(1);  // Fail if below threshold
    } else {
      console.log('\n✅ API contracts validation passed');
      process.exit(0);
    }
  } catch (error) {
    console.error('Error during API contract validation:', error.message);
    process.exit(1);
  }
}

runValidation();