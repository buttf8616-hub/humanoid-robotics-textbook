/**
 * Content Validation Script
 * Validates generated content against syllabus requirements and technical accuracy
 */

const fs = require('fs').promises;
const path = require('path');
const axios = require('axios'); // For Context7 MCP API calls

/**
 * Validates content against syllabus requirements
 * @param {string} content - The content to validate
 * @param {Object} syllabusTopic - The corresponding syllabus topic
 * @param {Array} verificationSources - List of approved verification sources
 * @returns {Object} Validation result with compliance score and issues
 */
async function validateContent(content, syllabusTopic, verificationSources = []) {
  const validationReport = {
    isValid: true,
    complianceScore: 0,
    validationReport: '',
    issues: [],
    verifiedSources: [],
    complianceStatus: 'unknown',
    validationDate: new Date().toISOString()
  };

  // Check if content covers the main topic title
  const titleCoverage = checkTitleCoverage(content, syllabusTopic.title);
  if (!titleCoverage) {
    validationReport.issues.push({
      type: 'content-mismatch',
      severity: 'high',
      description: `Content does not adequately cover the main topic: ${syllabusTopic.title}`,
      suggestedFix: `Ensure the content directly addresses the topic title: ${syllabusTopic.title}`
    });
    validationReport.isValid = false;
  }

  // Check if content addresses learning objectives
  const objectivesCoverage = checkLearningObjectivesCoverage(content, syllabusTopic.learningObjectives);
  if (objectivesCoverage < 0.7) { // Require at least 70% coverage
    validationReport.issues.push({
      type: 'completeness',
      severity: 'medium',
      description: `Content covers only ${Math.round(objectivesCoverage * 100)}% of learning objectives`,
      suggestedFix: `Expand content to cover all learning objectives: ${syllabusTopic.learningObjectives.join(', ')}`
    });
    if (objectivesCoverage < 0.5) {
      validationReport.isValid = false; // Mark as invalid if less than 50% coverage
    }
  }

  // Check for proper structure and formatting
  const structureValid = checkContentStructure(content);
  if (!structureValid) {
    validationReport.issues.push({
      type: 'formatting',
      severity: 'medium',
      description: 'Content does not follow proper MDX/Markdown structure',
      suggestedFix: 'Ensure content has proper headings, paragraphs, and formatting'
    });
  }

  // Perform Context7 MCP verification for technical accuracy
  const mcpVerificationResult = await verifyContentWithMCP(content, syllabusTopic.title, verificationSources);
  validationReport.verifiedSources = mcpVerificationResult.verifiedSources;
  validationReport.mcpComplianceScore = mcpVerificationResult.confidenceScore;

  // Adjust overall compliance score based on MCP verification
  if (mcpVerificationResult.confidenceScore < 70) {
    validationReport.issues.push({
      type: 'source-verification',
      severity: 'high',
      description: `Content has low verification confidence (${mcpVerificationResult.confidenceScore}%) against official documentation sources`,
      suggestedFix: 'Ensure content is grounded in official documentation sources accessed via Context7 MCP'
    });
    if (mcpVerificationResult.confidenceScore < 50) {
      validationReport.isValid = false; // Mark as invalid if verification confidence is too low
    }
  }

  // Calculate compliance score based on various factors including MCP verification
  validationReport.complianceScore = calculateComplianceScore(
    titleCoverage,
    objectivesCoverage,
    structureValid,
    content.length > 100, // Basic content length check
    mcpVerificationResult.confidenceScore // Include MCP verification score
  );

  // Determine compliance status based on score
  if (validationReport.complianceScore >= 90) {
    validationReport.complianceStatus = 'excellent';
  } else if (validationReport.complianceScore >= 75) {
    validationReport.complianceStatus = 'good';
  } else if (validationReport.complianceScore >= 50) {
    validationReport.complianceStatus = 'partial';
  } else {
    validationReport.complianceStatus = 'poor';
  }

  // Update overall validity based on compliance score
  if (validationReport.complianceScore < 50) {
    validationReport.isValid = false;
  }

  validationReport.validationReport = generateValidationReport(
    validationReport.complianceScore,
    validationReport.issues,
    syllabusTopic.title
  );

  return validationReport;
}

/**
 * Checks if content covers the main title
 */
function checkTitleCoverage(content, title) {
  // Simple check: see if title or significant parts of it appear in content
  const normalizedTitle = title.toLowerCase().replace(/[^a-z0-9 ]/g, '');
  const normalizedContent = content.toLowerCase().replace(/[^a-z0-9 ]/g, '');

  // Split title into words (excluding common stop words) and check coverage
  const titleWords = normalizedTitle.split(/\s+/).filter(word =>
    word.length > 3 && !['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all'].includes(word)
  );

  const coveredWords = titleWords.filter(word => normalizedContent.includes(word));
  return coveredWords.length / titleWords.length >= 0.5; // At least 50% of significant words should appear
}

/**
 * Checks if content covers learning objectives
 */
function checkLearningObjectivesCoverage(content, objectives) {
  if (!objectives || objectives.length === 0) return 1; // If no objectives, consider fully covered

  const normalizedContent = content.toLowerCase();
  let coveredCount = 0;

  for (const objective of objectives) {
    // Check if objective keywords appear in content
    const objectiveKeywords = objective.toLowerCase()
      .replace(/[^a-z0-9 ]/g, '')
      .split(/\s+/)
      .filter(word => word.length > 3);

    const coveredKeywords = objectiveKeywords.filter(keyword =>
      normalizedContent.includes(keyword)
    );

    if (coveredKeywords.length / objectiveKeywords.length >= 0.5) {
      coveredCount++; // At least 50% keyword coverage for this objective
    }
  }

  return coveredCount / objectives.length;
}

/**
 * Checks if content follows proper structure
 */
function checkContentStructure(content) {
  // Check for basic MDX/Markdown structure elements
  const hasHeadings = /#{1,6}\s/.test(content); // Check for any headings
  const hasParagraphs = /\n\s*\n/.test(content); // Check for paragraph breaks
  const hasStructure = hasHeadings || hasParagraphs;

  return hasStructure;
}

/**
 * Calculates overall compliance score
 */
function calculateComplianceScore(titleCoverage, objectivesCoverage, structureValid, adequateLength, mcpVerificationScore = 70) {
  let score = 0;

  // Title coverage: up to 20 points
  score += titleCoverage ? 20 : 0;

  // Objectives coverage: up to 30 points
  score += objectivesCoverage * 30;

  // Structure: up to 15 points
  score += structureValid ? 15 : 0;

  // Length: up to 5 points
  score += adequateLength ? 5 : 0;

  // MCP verification contributes up to 30 points (30% of total)
  score += (mcpVerificationScore / 100) * 30;

  return Math.round(score);
}

/**
 * Generates a human-readable validation report
 */
function generateValidationReport(score, issues, topicTitle) {
  let report = `Validation report for topic: "${topicTitle}"\n`;
  report += `Compliance Score: ${score}/100\n\n`;

  if (issues.length === 0) {
    report += "✓ No issues found. Content meets all requirements.\n";
  } else {
    report += `Found ${issues.length} issue(s):\n`;
    for (let i = 0; i < issues.length; i++) {
      const issue = issues[i];
      report += `  ${i + 1}. [${issue.severity.toUpperCase()}] ${issue.type}: ${issue.description}\n`;
    }
  }

  return report;
}

/**
 * Validates an entire book directory against syllabus requirements
 */
async function validateBookContent(bookDir, syllabusTopics) {
  const results = {
    overallComplianceScore: 0,
    totalChapters: 0,
    validatedChapters: 0,
    chapterResults: [],
    summaryReport: ''
  };

  // Find all MDX/MD files in the book directory
  const files = await findAllContentFiles(bookDir);

  for (const file of files) {
    const content = await fs.readFile(file, 'utf8');

    // Try to match file to a syllabus topic based on filename or frontmatter
    const topic = findMatchingTopic(file, syllabusTopics);

    if (topic) {
      const validation = await validateContent(content, topic);
      results.chapterResults.push({
        file: file,
        topicId: topic.id,
        ...validation
      });
      results.validatedChapters++;
    }
  }

  // Calculate overall compliance
  if (results.validatedChapters > 0) {
    const totalScore = results.chapterResults.reduce((sum, result) => sum + result.complianceScore, 0);
    results.overallComplianceScore = Math.round(totalScore / results.validatedChapters);
  }

  results.totalChapters = syllabusTopics.length;
  results.summaryReport = generateBookValidationSummary(results);

  return results;
}

/**
 * Finds all MDX/MD files in a directory recursively
 */
async function findAllContentFiles(dir) {
  const files = [];
  const items = await fs.readdir(dir, { withFileTypes: true });

  for (const item of items) {
    if (item.isDirectory()) {
      const subDirFiles = await findAllContentFiles(path.join(dir, item.name));
      files.push(...subDirFiles);
    } else if (item.name.endsWith('.mdx') || item.name.endsWith('.md')) {
      files.push(path.join(dir, item.name));
    }
  }

  return files;
}

/**
 * Finds the matching syllabus topic for a content file
 */
function findMatchingTopic(filePath, syllabusTopics) {
  const fileName = path.basename(filePath, path.extname(filePath));

  // First, try to match by ID (most reliable)
  for (const topic of syllabusTopics) {
    if (topic.id === fileName) {
      return topic;
    }
  }

  // If no ID match, try to match by title (remove special chars and compare)
  for (const topic of syllabusTopics) {
    const normalizedTopicTitle = topic.title.toLowerCase().replace(/[^a-z0-9]/g, '');
    const normalizedFileName = fileName.toLowerCase().replace(/[^a-z0-9]/g, '');

    if (normalizedTopicTitle.includes(normalizedFileName) ||
        normalizedFileName.includes(normalizedTopicTitle)) {
      return topic;
    }
  }

  return null; // No matching topic found
}

/**
 * Generates a summary report for book validation
 */
function generateBookValidationSummary(results) {
  return `Book Validation Summary:
  - Total Chapters in Syllabus: ${results.totalChapters}
  - Chapters Validated: ${results.validatedChapters}
  - Overall Compliance Score: ${results.overallComplianceScore}/100
  - Status: ${results.overallComplianceScore >= 75 ? 'PASS' :
             results.overallComplianceScore >= 50 ? 'PARTIAL' : 'FAIL'}
  `;
}

// Command line interface
if (require.main === module) {
  const args = process.argv.slice(2);

  if (args.length < 1) {
    console.error('Usage: node validate-content.js <content-file> [syllabus-topic-file]');
    process.exit(1);
  }

  const contentFile = args[0];
  const syllabusFile = args[1];

  (async () => {
    try {
      const content = await fs.readFile(contentFile, 'utf8');

      if (syllabusFile) {
        // Validate against specific syllabus topic
        const syllabusData = JSON.parse(await fs.readFile(syllabusFile, 'utf8'));
        const validation = await validateContent(content, syllabusData);
        console.log(JSON.stringify(validation, null, 2));
      } else {
        // Just check basic structure
        const basicValidation = {
          isValid: checkContentStructure(content),
          complianceScore: 0,
          validationReport: 'Basic structure check only - no syllabus provided',
          issues: [],
          verifiedSources: [],
          complianceStatus: 'unknown',
          validationDate: new Date().toISOString()
        };
        console.log(JSON.stringify(basicValidation, null, 2));
      }
    } catch (error) {
      console.error('Error validating content:', error.message);
      process.exit(1);
    }
  })();
}

/**
 * Mock Context7 MCP verification function
 * In a real implementation, this would connect to the Context7 MCP API
 * to verify content against official documentation sources
 */
async function verifyContentWithMCP(content, topicTitle, verificationSources = []) {
  // In a real implementation, this would make API calls to Context7 MCP
  // For this mock implementation, we'll simulate the verification process

  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 100));

  // Calculate a simulated confidence score based on content quality indicators
  const contentLength = content.length;
  const hasCodeBlocks = /```[\s\S]*?```/.test(content);
  const hasHeadings = /^#+\s/m.test(content);
  const hasLinks = /\[.*\]\(.*\)/.test(content);

  // Base confidence on content characteristics
  let confidenceScore = 50; // Base score

  if (contentLength > 500) confidenceScore += 20; // Longer, more detailed content
  if (hasCodeBlocks) confidenceScore += 10; // Technical content often has code
  if (hasHeadings) confidenceScore += 10; // Proper structure
  if (hasLinks) confidenceScore += 10; // References to sources

  // Cap at 100%
  confidenceScore = Math.min(confidenceScore, 100);

  // Determine which sources to mark as verified (simulated)
  const availableSources = [
    'official-docusaurus-docs',
    'ros2-documentation',
    'gazebo-simulation-guide',
    'nvidia-isaac-manual',
    'unity-robotics-docs',
    'technical-writer-reference'
  ];

  const verifiedSources = verificationSources.length > 0
    ? verificationSources
    : availableSources.slice(0, Math.min(2, availableSources.length));

  return {
    isVerified: confidenceScore >= 70,
    verifiedSources,
    confidenceScore,
    verificationDate: new Date().toISOString(),
    topic: topicTitle
  };
}

module.exports = {
  validateContent,
  validateBookContent,
  checkTitleCoverage,
  checkLearningObjectivesCoverage,
  checkContentStructure,
  verifyContentWithMCP
};