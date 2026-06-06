/**
 * API Server for Book Generation and Content Validation
 * Implements API endpoints per contract specification
 */

const express = require('express');
const fs = require('fs').promises;
const path = require('path');
const { generateBookStructure } = require('./generate-book');
const { validateContent, validateBookContent } = require('./validate-content');
const { parseSyllabus, normalizeSyllabus } = require('./parse-syllabus');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Enable CORS for all routes
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization');
  if (req.method === 'OPTIONS') {
    res.sendStatus(200);
  } else {
    next();
  }
});

/**
 * POST /generate-book
 * Creates a Docusaurus-based technical book from provided syllabus topics
 */
app.post('/api/generate-book', async (req, res) => {
  try {
    const { title, description, topics, author } = req.body;

    // Validate required fields
    if (!topics || !Array.isArray(topics) || topics.length === 0) {
      return res.status(400).json({
        error: 'Invalid syllabus input: topics array is required',
        status: 'error'
      });
    }

    // Normalize and validate syllabus
    const syllabusInput = { title, description, topics, author };
    const normalizedSyllabus = normalizeSyllabus(syllabusInput);
    const parsedTopics = parseSyllabus(normalizedSyllabus);

    // Generate book structure
    const outputDir = './docs';
    const result = await generateBookStructure(normalizedSyllabus, outputDir);

    res.status(200).json(result);
  } catch (error) {
    console.error('Error in /api/generate-book:', error);
    res.status(500).json({
      status: 'error',
      message: error.message
    });
  }
});

/**
 * POST /validate-content
 * Validates that generated content complies with syllabus requirements
 */
app.post('/api/validate-content', async (req, res) => {
  try {
    const { content, syllabusTopics, verificationSources } = req.body;

    // Validate required fields
    if (typeof content !== 'string' || !Array.isArray(syllabusTopics)) {
      return res.status(400).json({
        error: 'Invalid request: content string and syllabusTopics array are required',
        isValid: false
      });
    }

    // For now, validate against the first topic in the list
    // In a real implementation, we'd need to determine which topic this content corresponds to
    const syllabusTopic = syllabusTopics[0] || {
      id: 'default-topic',
      title: 'Default Topic',
      learningObjectives: [],
      description: 'Default topic for validation'
    };

    const result = await validateContent(content, syllabusTopic, verificationSources);

    res.status(200).json(result);
  } catch (error) {
    console.error('Error in /api/validate-content:', error);
    res.status(500).json({
      isValid: false,
      error: error.message
    });
  }
});

/**
 * GET /health
 * Health check endpoint
 */
app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    service: 'Book Generation API'
  });
});

/**
 * GET /api/spec
 * Returns the API specification
 */
app.get('/api/spec', (req, res) => {
  // Return the OpenAPI spec that was defined in the contracts
  const spec = {
    openapi: '3.0.0',
    info: {
      title: 'Book Generation API',
      description: 'API for generating technical books from syllabus topics using AI assistance',
      version: '1.0.0'
    },
    paths: {
      '/api/generate-book': {
        post: {
          summary: 'Generate a technical book from a syllabus',
          description: 'Creates a Docusaurus-based technical book from provided syllabus topics'
        }
      },
      '/api/validate-content': {
        post: {
          summary: 'Validate book content compliance',
          description: 'Validates that generated content complies with syllabus requirements'
        }
      }
    }
  };

  res.status(200).json(spec);
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({
    error: 'Something went wrong!',
    message: err.message
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    error: 'Route not found',
    path: req.originalUrl
  });
});

// Start server if this file is run directly
if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`Book Generation API server running on port ${PORT}`);
    console.log(`Health check: http://localhost:${PORT}/health`);
    console.log(`API spec: http://localhost:${PORT}/api/spec`);
  });
}

module.exports = app;