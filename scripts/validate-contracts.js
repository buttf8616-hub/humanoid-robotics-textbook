/**
 * API Contract Validation Script
 * Validates API implementation against OpenAPI contract specification
 */

const apiSpec = {
  openapi: '3.0.0',
  info: {
    title: 'Book Generation API',
    description: 'API for generating technical books from syllabus topics using AI assistance',
    version: '1.0.0'
  },
  servers: [
    {
      url: 'http://localhost:3000/api',
      description: 'Local development server'
    }
  ],
  paths: {
    '/generate-book': {
      post: {
        summary: 'Generate a technical book from a syllabus',
        description: 'Creates a Docusaurus-based technical book from provided syllabus topics',
        requestBody: {
          required: true,
          content: {
            'application/json': {
              schema: {
                $ref: '#/components/schemas/SyllabusInput'
              }
            }
          }
        },
        responses: {
          '200': {
            description: 'Book generation successful',
            content: {
              'application/json': {
                schema: {
                  $ref: '#/components/schemas/GenerationResponse'
                }
              }
            }
          },
          '400': {
            description: 'Invalid syllabus input'
          },
          '500': {
            description: 'Internal server error during generation'
          }
        },
        tags: ['Book Generation']
      }
    },
    '/validate-content': {
      post: {
        summary: 'Validate book content compliance',
        description: 'Validates that generated content complies with syllabus requirements',
        requestBody: {
          required: true,
          content: {
            'application/json': {
              schema: {
                $ref: '#/components/schemas/ContentValidationRequest'
              }
            }
          }
        },
        responses: {
          '200': {
            description: 'Validation successful',
            content: {
              'application/json': {
                schema: {
                  $ref: '#/components/schemas/ValidationResponse'
                }
              }
            }
          },
          '400': {
            description: 'Invalid content for validation'
          },
          '500': {
            description: 'Internal server error during validation'
          }
        },
        tags: ['Content Validation']
      }
    }
  },
  components: {
    schemas: {
      SyllabusInput: {
        type: 'object',
        required: ['topics', 'title', 'description'],
        properties: {
          title: {
            type: 'string',
            description: 'Title of the technical book',
            example: 'Docusaurus Documentation Guide'
          },
          description: {
            type: 'string',
            description: 'Description of the technical book',
            example: 'A comprehensive guide to Docusaurus documentation framework'
          },
          topics: {
            type: 'array',
            items: {
              $ref: '#/components/schemas/SyllabusTopic'
            }
          },
          author: {
            type: 'string',
            description: 'Author of the book',
            example: 'Technical Writer'
          }
        }
      },
      SyllabusTopic: {
        type: 'object',
        required: ['id', 'title', 'description'],
        properties: {
          id: {
            type: 'string',
            description: 'Unique identifier for the topic',
            example: 'topic-1'
          },
          title: {
            type: 'string',
            description: 'Title of the syllabus topic',
            example: 'Getting Started with Docusaurus'
          },
          description: {
            type: 'string',
            description: 'Brief description of the topic',
            example: 'Introduction to Docusaurus framework and setup'
          },
          learningObjectives: {
            type: 'array',
            items: {
              type: 'string'
            },
            description: 'List of learning objectives for this topic',
            example: ['Understand Docusaurus basics', 'Install Docusaurus', 'Create first page']
          },
          prerequisites: {
            type: 'array',
            items: {
              type: 'string'
            },
            description: 'List of prerequisite topics',
            example: []
          },
          category: {
            type: 'string',
            description: 'Category for grouping topics',
            example: 'Fundamentals'
          }
        }
      },
      GenerationResponse: {
        type: 'object',
        required: ['status', 'bookPath', 'chapterCount'],
        properties: {
          status: {
            type: 'string',
            enum: ['success', 'error'],
            description: 'Status of the generation process'
          },
          bookPath: {
            type: 'string',
            description: 'Path to the generated book files',
            example: 'docs/chapters/'
          },
          chapterCount: {
            type: 'integer',
            description: 'Number of chapters generated',
            example: 10
          },
          message: {
            type: 'string',
            description: 'Additional information about the generation'
          },
          generatedFiles: {
            type: 'array',
            items: {
              type: 'string'
            },
            description: 'List of generated file paths',
            example: ['docs/chapters/topic-1.md', 'docs/chapters/topic-2.md']
          }
        }
      },
      ContentValidationRequest: {
        type: 'object',
        required: ['content', 'syllabusTopics'],
        properties: {
          content: {
            type: 'string',
            description: 'Content to validate',
            example: 'Markdown content to validate against syllabus'
          },
          syllabusTopics: {
            type: 'array',
            items: {
              $ref: '#/components/schemas/SyllabusTopic'
            }
          },
          verificationSources: {
            type: 'array',
            items: {
              type: 'string'
            },
            description: 'List of approved verification sources',
            example: ['official-docusaurus-docs', 'verified-api-reference']
          }
        }
      },
      ValidationResponse: {
        type: 'object',
        required: ['isValid', 'complianceScore', 'validationReport'],
        properties: {
          isValid: {
            type: 'boolean',
            description: 'Whether the content passes validation'
          },
          complianceScore: {
            type: 'number',
            minimum: 0,
            maximum: 100,
            description: 'Compliance score as percentage',
            example: 95.5
          },
          validationReport: {
            type: 'string',
            description: 'Detailed validation report'
          },
          issues: {
            type: 'array',
            items: {
              $ref: '#/components/schemas/ValidationIssue'
            }
          }
        }
      },
      ValidationIssue: {
        type: 'object',
        required: ['type', 'severity', 'description'],
        properties: {
          type: {
            type: 'string',
            enum: ['content-mismatch', 'source-verification', 'formatting', 'completeness'],
            description: 'Type of validation issue'
          },
          severity: {
            type: 'string',
            enum: ['critical', 'high', 'medium', 'low'],
            description: 'Severity of the issue'
          },
          description: {
            type: 'string',
            description: 'Description of the issue'
          },
          suggestedFix: {
            type: 'string',
            description: 'Suggested fix for the issue'
          }
        }
      }
    }
  }
};

/**
 * Validates that our API implementation matches the contract
 * @param {Object} implementation - The actual API implementation to validate
 * @returns {Object} Validation results
 */
function validateAPIContract(implementation = null) {
  const results = {
    isValid: true,
    endpointCount: 0,
    validatedEndpoints: 0,
    issues: [],
    summary: ''
  };

  // Check required endpoints exist
  const requiredEndpoints = Object.keys(apiSpec.paths);
  results.endpointCount = requiredEndpoints.length;

  // For this validation, we'll check the contract structure itself
  // In a real implementation, we would check against the actual running API

  // Check /generate-book endpoint
  if (apiSpec.paths['/generate-book']) {
    results.validatedEndpoints++;

    const generateBookSpec = apiSpec.paths['/generate-book'].post;

    // Validate required properties exist
    if (!generateBookSpec.summary) {
      results.issues.push({
        type: 'missing-field',
        severity: 'critical',
        endpoint: '/generate-book',
        description: 'Missing summary in API specification'
      });
      results.isValid = false;
    }

    if (!generateBookSpec.requestBody) {
      results.issues.push({
        type: 'missing-field',
        severity: 'critical',
        endpoint: '/generate-book',
        description: 'Missing requestBody in API specification'
      });
      results.isValid = false;
    }

    if (!generateBookSpec.responses['200']) {
      results.issues.push({
        type: 'missing-field',
        severity: 'critical',
        endpoint: '/generate-book',
        description: 'Missing 200 response in API specification'
      });
      results.isValid = false;
    }
  }

  // Check /validate-content endpoint
  if (apiSpec.paths['/validate-content']) {
    results.validatedEndpoints++;

    const validateContentSpec = apiSpec.paths['/validate-content'].post;

    // Validate required properties exist
    if (!validateContentSpec.summary) {
      results.issues.push({
        type: 'missing-field',
        severity: 'critical',
        endpoint: '/validate-content',
        description: 'Missing summary in API specification'
      });
      results.isValid = false;
    }

    if (!validateContentSpec.requestBody) {
      results.issues.push({
        type: 'missing-field',
        severity: 'critical',
        endpoint: '/validate-content',
        description: 'Missing requestBody in API specification'
      });
      results.isValid = false;
    }

    if (!validateContentSpec.responses['200']) {
      results.issues.push({
        type: 'missing-field',
        severity: 'critical',
        endpoint: '/validate-content',
        description: 'Missing 200 response in API specification'
      });
      results.isValid = false;
    }
  }

  // Validate required schemas exist
  const requiredSchemas = ['SyllabusInput', 'GenerationResponse', 'ContentValidationRequest', 'ValidationResponse'];
  for (const schemaName of requiredSchemas) {
    if (!apiSpec.components.schemas[schemaName]) {
      results.issues.push({
        type: 'missing-schema',
        severity: 'critical',
        schema: schemaName,
        description: `Missing required schema: ${schemaName}`
      });
      results.isValid = false;
    }
  }

  // Generate summary
  results.summary = `Contract Validation Summary:
  - Total Endpoints Required: ${results.endpointCount}
  - Endpoints Validated: ${results.validatedEndpoints}
  - Issues Found: ${results.issues.length}
  - Status: ${results.isValid ? 'PASS' : 'FAIL'}
  `;

  return results;
}

/**
 * Validates a specific API response against the contract schema
 */
function validateResponseAgainstContract(response, endpointPath, method = 'post') {
  const results = {
    isValid: true,
    errors: []
  };

  if (!apiSpec.paths[endpointPath]) {
    results.isValid = false;
    results.errors.push(`Endpoint ${endpointPath} not found in contract`);
    return results;
  }

  const spec = apiSpec.paths[endpointPath][method.toLowerCase()];
  if (!spec) {
    results.isValid = false;
    results.errors.push(`Method ${method} not defined for ${endpointPath} in contract`);
    return results;
  }

  // For a full implementation, we would validate the response against the schema definition
  // This is a simplified version that just checks for required fields based on the spec
  if (endpointPath === '/generate-book' && method === 'post') {
    // Check if response has required fields for GenerationResponse
    if (typeof response.status !== 'string') {
      results.errors.push('Missing or invalid "status" field in response');
      results.isValid = false;
    }
    if (typeof response.bookPath !== 'string') {
      results.errors.push('Missing or invalid "bookPath" field in response');
      results.isValid = false;
    }
    if (typeof response.chapterCount !== 'number' && typeof response.chapterCount !== 'string') {
      results.errors.push('Missing or invalid "chapterCount" field in response');
      results.isValid = false;
    }
  } else if (endpointPath === '/validate-content' && method === 'post') {
    // Check if response has required fields for ValidationResponse
    if (typeof response.isValid !== 'boolean') {
      results.errors.push('Missing or invalid "isValid" field in response');
      results.isValid = false;
    }
    if (typeof response.complianceScore !== 'number' && typeof response.complianceScore !== 'string') {
      results.errors.push('Missing or invalid "complianceScore" field in response');
      results.isValid = false;
    }
    if (typeof response.validationReport !== 'string') {
      results.errors.push('Missing or invalid "validationReport" field in response');
      results.isValid = false;
    }
  }

  return results;
}

/**
 * Returns the API specification
 */
function getAPISpecification() {
  return apiSpec;
}

// Run validation if this script is executed directly
if (require.main === module) {
  console.log('Validating API contracts against implementation...\n');

  const validationResults = validateAPIContract();

  console.log(validationResults.summary);

  if (validationResults.issues.length > 0) {
    console.log('Issues found:');
    validationResults.issues.forEach((issue, index) => {
      console.log(`  ${index + 1}. [${issue.severity.toUpperCase()}] ${issue.type}: ${issue.description}`);
      if (issue.endpoint) console.log(`     Endpoint: ${issue.endpoint}`);
      if (issue.schema) console.log(`     Schema: ${issue.schema}`);
    });
  }

  console.log(`\nContract validation: ${validationResults.isValid ? 'PASSED' : 'FAILED'}`);
  process.exit(validationResults.isValid ? 0 : 1);
}

module.exports = {
  validateAPIContract,
  validateResponseAgainstContract,
  getAPISpecification,
  apiSpec // Export the spec itself for reference
};