/**
 * API Contract Validation Script
 * Validates API implementation against OpenAPI contract specification
 */

const axios = require('axios');
const fs = require('fs').promises;
const yaml = require('js-yaml');

/**
 * Validates API implementation against contract specification
 * @param {string} baseUrl - Base URL of the running API server
 * @returns {Object} Validation results with compliance report
 */
async function validateApiContracts(baseUrl = 'http://localhost:3000') {
  const validationResults = {
    isValid: true,
    complianceScore: 0,
    validationReport: '',
    issues: [],
    endpointsValidated: 0,
    endpointsPassed: 0,
    validationDate: new Date().toISOString()
  };

  // Expected endpoints from the contract
  const expectedEndpoints = {
    '/api/generate-book': {
      methods: ['POST'],
      requiredFields: ['topics', 'title', 'description']
    },
    '/api/validate-content': {
      methods: ['POST'],
      requiredFields: ['content', 'syllabusTopics']
    },
    '/health': {
      methods: ['GET']
    },
    '/api/spec': {
      methods: ['GET']
    }
  };

  // Test each endpoint
  for (const [path, spec] of Object.entries(expectedEndpoints)) {
    validationResults.endpointsValidated++;

    try {
      // Test GET endpoints
      if (spec.methods.includes('GET')) {
        const response = await axios.get(`${baseUrl}${path}`);

        if (response.status !== 200) {
          validationResults.issues.push({
            type: 'response-validation',
            severity: 'high',
            endpoint: path,
            method: 'GET',
            description: `Expected 200 status, got ${response.status}`,
            suggestedFix: `Check implementation of ${path} endpoint`
          });
          validationResults.isValid = false;
          continue;
        }
      }

      // Test POST endpoints
      if (spec.methods.includes('POST')) {
        let testData = {};

        if (path === '/api/generate-book') {
          testData = {
            title: 'Test Book',
            description: 'Test Description',
            topics: [
              {
                id: 'test-topic',
                title: 'Test Topic',
                description: 'Test Description',
                learningObjectives: ['Learn something']
              }
            ]
          };
        } else if (path === '/api/validate-content') {
          testData = {
            content: '# Test Content\nThis is test content.',
            syllabusTopics: [
              {
                id: 'test-topic',
                title: 'Test Topic',
                learningObjectives: ['Learn something']
              }
            ]
          };
        }

        const response = await axios.post(`${baseUrl}${path}`, testData);

        if (response.status !== 200) {
          validationResults.issues.push({
            type: 'response-validation',
            severity: 'high',
            endpoint: path,
            method: 'POST',
            description: `Expected 200 status for ${path}, got ${response.status}`,
            suggestedFix: `Check implementation of ${path} endpoint`
          });
          validationResults.isValid = false;
          continue;
        }

        // Validate response structure based on contract
        const isValidResponse = validateResponseStructure(response.data, path);
        if (!isValidResponse.isValid) {
          validationResults.issues.push({
            type: 'response-structure',
            severity: 'medium',
            endpoint: path,
            method: 'POST',
            description: `Response structure mismatch: ${isValidResponse.issues.join(', ')}`,
            suggestedFix: `Align response structure with API contract for ${path}`
          });
          validationResults.isValid = false;
        }
      }

      validationResults.endpointsPassed++;
    } catch (error) {
      validationResults.issues.push({
        type: 'endpoint-unreachable',
        severity: 'critical',
        endpoint: path,
        description: `Error accessing ${path}: ${error.message}`,
        suggestedFix: `Verify that the endpoint is implemented and server is running`
      });
      validationResults.isValid = false;
    }
  }

  // Calculate compliance score
  validationResults.complianceScore = Math.round((validationResults.endpointsPassed / validationResults.endpointsValidated) * 100);

  // Generate validation report
  validationResults.validationReport = `
API Contract Validation Report:
- Endpoints validated: ${validationResults.endpointsValidated}
- Endpoints passed: ${validationResults.endpointsPassed}
- Compliance Score: ${validationResults.complianceScore}%
- Issues found: ${validationResults.issues.length}
${validationResults.issues.length > 0 ?
  '\nIssues:\n' + validationResults.issues.map(issue => `  - ${issue.description}`).join('\n') :
  '\nNo issues found.'
}`;

  return validationResults;
}

/**
 * Validates response structure against contract specification
 */
function validateResponseStructure(responseData, endpointPath) {
  const result = {
    isValid: true,
    issues: []
  };

  if (endpointPath === '/api/generate-book') {
    // Validate generate-book response structure
    const requiredFields = ['status', 'bookPath', 'chapterCount', 'message'];
    for (const field of requiredFields) {
      if (!(field in responseData)) {
        result.isValid = false;
        result.issues.push(`Missing required field: ${field}`);
      }
    }
  } else if (endpointPath === '/api/validate-content') {
    // Validate validate-content response structure
    const requiredFields = ['isValid', 'complianceScore', 'validationReport', 'issues'];
    for (const field of requiredFields) {
      if (!(field in responseData)) {
        result.isValid = false;
        result.issues.push(`Missing required field: ${field}`);
      }
    }
  } else if (endpointPath === '/health') {
    // Validate health response structure
    const requiredFields = ['status', 'timestamp', 'service'];
    for (const field of requiredFields) {
      if (!(field in responseData)) {
        result.isValid = false;
        result.issues.push(`Missing required field: ${field}`);
      }
    }
  } else if (endpointPath === '/api/spec') {
    // Validate spec response structure
    const requiredFields = ['openapi', 'info', 'paths'];
    for (const field of requiredFields) {
      if (!(field in responseData)) {
        result.isValid = false;
        result.issues.push(`Missing required field: ${field}`);
      }
    }
  }

  return result;
}

/**
 * Validates the API specification itself
 */
async function validateApiSpec(specFilePath = '../specs/002-physical-ai-robotics-book/contracts/book-generation-api.yaml') {
  const validationResults = {
    isValid: true,
    issues: [],
    specCompliance: 0
  };

  try {
    // Read and parse the YAML spec file
    const specContent = await fs.readFile(specFilePath, 'utf8');
    const spec = yaml.load(specContent);

    // Define required spec fields
    const requiredSpecFields = ['openapi', 'info', 'paths'];

    // Check for required OpenAPI fields
    for (const field of requiredSpecFields) {
      if (!(field in spec)) {
        validationResults.issues.push({
          type: 'spec-validation',
          severity: 'critical',
          description: `Missing required spec field: ${field}`,
          suggestedFix: `Add ${field} to the API specification`
        });
        validationResults.isValid = false;
      }
    }

    // Validate paths exist and have proper structure
    if (spec.paths) {
      const expectedPaths = ['/api/generate-book', '/api/validate-content', '/health', '/api/spec'];

      for (const expectedPath of expectedPaths) {
        if (!spec.paths[expectedPath]) {
          validationResults.issues.push({
            type: 'spec-validation',
            severity: 'critical',
            description: `Missing expected path in spec: ${expectedPath}`,
            suggestedFix: `Add ${expectedPath} to the API specification`
          });
          validationResults.isValid = false;
        }
      }
    }

    // Calculate spec compliance
    validationResults.specCompliance = Math.round(
      ((requiredSpecFields.length - validationResults.issues.filter(issue => issue.type.includes('spec')).length) / requiredSpecFields.length) * 100
    );
  } catch (error) {
    validationResults.issues.push({
      type: 'spec-load-error',
      severity: 'critical',
      description: `Could not load API spec from ${specFilePath}: ${error.message}`,
      suggestedFix: `Verify that the spec file exists and is valid YAML`
    });
    validationResults.isValid = false;
  }

  return validationResults;
}

/**
 * Performs comprehensive API contract validation
 */
async function performComprehensiveValidation(apiBaseUrl = 'http://localhost:3000') {
  const results = {
    apiImplementation: null,
    apiSpec: null,
    overallCompliance: 0,
    summary: ''
  };

  // Validate API implementation
  results.apiImplementation = await validateApiContracts(apiBaseUrl);

  // Validate API specification
  results.apiSpec = await validateApiSpec();

  // Calculate overall compliance
  results.overallCompliance = Math.round(
    (results.apiImplementation.complianceScore + results.apiSpec.specCompliance) / 2
  );

  // Generate summary
  results.summary = `
API Contract Validation Summary:
- API Implementation Compliance: ${results.apiImplementation.complianceScore}%
- API Specification Compliance: ${results.apiSpec.specCompliance}%
- Overall Compliance: ${results.overallCompliance}%
- Implementation Issues: ${results.apiImplementation.issues.length}
- Specification Issues: ${results.apiSpec.issues.length}
- Status: ${results.overallCompliance >= 90 ? 'EXCELLENT' :
              results.overallCompliance >= 75 ? 'GOOD' :
              results.overallCompliance >= 50 ? 'FAIR' : 'POOR'}
  `;

  return results;
}

// Command line interface
if (require.main === module) {
  const args = process.argv.slice(2);
  const baseUrl = args[0] || 'http://localhost:3000';

  console.log(`Validating API contracts at: ${baseUrl}\n`);

  (async () => {
    try {
      const results = await performComprehensiveValidation(baseUrl);

      console.log(results.summary);
      console.log('\nDetailed Results:');
      console.log('==================');
      console.log('API Implementation Validation:');
      console.log(JSON.stringify(results.apiImplementation, null, 2));

      console.log('\nAPI Specification Validation:');
      console.log(JSON.stringify(results.apiSpec, null, 2));

      // Exit with error code if compliance is below threshold
      if (results.overallCompliance < 75) {
        console.error('\n⚠️  WARNING: API compliance is below 75% threshold');
        process.exit(1);
      } else if (results.overallCompliance < 90) {
        console.warn('\n⚠️  WARNING: API compliance is below 90% threshold');
      } else {
        console.log('\n✅ API contracts validation passed');
      }
    } catch (error) {
      console.error('Error during API contract validation:', error.message);
      process.exit(1);
    }
  })();
}

module.exports = {
  validateApiContracts,
  validateResponseStructure,
  validateApiSpec,
  performComprehensiveValidation
};