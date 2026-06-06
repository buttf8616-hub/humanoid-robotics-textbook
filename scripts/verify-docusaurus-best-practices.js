#!/usr/bin/env node

/**
 * Docusaurus Best Practices Verifier
 * Verifies generated book structure meets Docusaurus best practices
 */

const fs = require('fs').promises;
const path = require('path');

/**
 * Verifies that the generated book structure meets Docusaurus best practices
 * @param {string} docsDir - Directory containing documentation
 * @returns {Object} Verification results
 */
async function verifyDocusaurusBestPractices(docsDir = './docs') {
  const results = {
    isValid: true,
    issues: [],
    recommendations: [],
    stats: {
      totalFiles: 0,
      mdxFiles: 0,
      categoryFiles: 0,
      totalSize: 0
    }
  };

  try {
    // Check for proper directory structure
    const dirExists = await checkDirectoryStructure(docsDir);
    if (!dirExists.isValid) {
      results.isValid = false;
      results.issues.push(...dirExists.issues);
    }

    // Check for proper file formats
    const fileFormatResults = await checkFileFormats(docsDir);
    if (!fileFormatResults.isValid) {
      results.isValid = false;
      results.issues.push(...fileFormatResults.issues);
    }
    results.stats = { ...results.stats, ...fileFormatResults.stats };

    // Check for proper frontmatter
    const frontmatterResults = await checkFrontmatter(docsDir);
    if (!frontmatterResults.isValid) {
      results.isValid = false;
      results.issues.push(...frontmatterResults.issues);
    }

    // Check for proper navigation setup
    const navResults = await checkNavigationSetup(docsDir);
    if (!navResults.isValid) {
      results.isValid = false;
      results.issues.push(...navResults.issues);
    }
    results.recommendations.push(...navResults.recommendations);

    // Check for proper MDX practices
    const mdxResults = await checkMdxPractices(docsDir);
    if (!mdxResults.isValid) {
      results.isValid = false;
      results.issues.push(...mdxResults.issues);
    }
    results.recommendations.push(...mdxResults.recommendations);

    // Calculate overall compliance score
    const totalChecks = 100; // Estimate of total checks
    const failedChecks = results.issues.length;
    const complianceScore = Math.max(0, Math.min(100, Math.round(((totalChecks - failedChecks) / totalChecks) * 100)));

    results.complianceScore = complianceScore;
    results.bestPracticesMet = complianceScore >= 90;

  } catch (error) {
    results.isValid = false;
    results.issues.push(`Verification error: ${error.message}`);
  }

  return results;
}

/**
 * Checks for proper directory structure
 */
async function checkDirectoryStructure(docsDir) {
  const issues = [];
  const isValid = true; // We'll consider it valid if the directory exists

  try {
    await fs.access(docsDir);
  } catch (error) {
    issues.push(`Docs directory does not exist: ${docsDir}`);
    return { isValid: false, issues };
  }

  return { isValid, issues };
}

/**
 * Checks for proper file formats
 */
async function checkFileFormats(docsDir) {
  const issues = [];
  const recommendations = [];
  const stats = { totalFiles: 0, mdxFiles: 0, categoryFiles: 0, totalSize: 0 };

  try {
    const files = await getAllFiles(docsDir);
    stats.totalFiles = files.length;

    for (const file of files) {
      const ext = path.extname(file).toLowerCase();
      const content = await fs.readFile(file);
      stats.totalSize += content.length;

      if (ext === '.mdx') {
        stats.mdxFiles++;
        
        // Check for proper MDX content
        const contentStr = content.toString();
        if (!contentStr.includes('---')) {
          issues.push(`MDX file missing frontmatter: ${file}`);
        }
      } else if (path.basename(file) === '_category_.json') {
        stats.categoryFiles++;
        
        // Validate category JSON structure
        try {
          const categoryContent = JSON.parse(content.toString());
          if (!categoryContent.label) {
            issues.push(`Category file missing label: ${file}`);
          }
        } catch (e) {
          issues.push(`Invalid JSON in category file: ${file}`);
        }
      } else if (ext === '.md') {
        recommendations.push(`Consider using MDX instead of MD for file: ${file}`);
      }
    }
  } catch (error) {
    issues.push(`Error checking file formats: ${error.message}`);
  }

  return { isValid: issues.length === 0, issues, recommendations, stats };
}

/**
 * Checks for proper frontmatter in MDX files
 */
async function checkFrontmatter(docsDir) {
  const issues = [];
  const recommendations = [];

  try {
    const mdxFiles = await getMdxFiles(docsDir);

    for (const file of mdxFiles) {
      const content = await fs.readFile(file, 'utf8');
      
      // Extract frontmatter
      const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/);
      if (!frontmatterMatch) {
        issues.push(`MDX file missing frontmatter: ${file}`);
        continue;
      }

      const frontmatterStr = frontmatterMatch[1];
      let frontmatter;
      try {
        // Simple YAML parsing (for now, we'll just check for common fields)
        frontmatter = parseFrontmatter(frontmatterStr);
      } catch (e) {
        issues.push(`Invalid frontmatter in file: ${file}`);
        continue;
      }

      // Check for required fields
      if (!frontmatter.title) {
        issues.push(`MDX file missing title in frontmatter: ${file}`);
      }

      // Check for recommended fields
      if (!frontmatter.sidebar_position) {
        recommendations.push(`Consider adding sidebar_position to frontmatter in: ${file}`);
      }

      if (!frontmatter.description) {
        recommendations.push(`Consider adding description to frontmatter in: ${file}`);
      }
    }
  } catch (error) {
    issues.push(`Error checking frontmatter: ${error.message}`);
  }

  return { isValid: issues.length === 0, issues, recommendations };
}

/**
 * Simple frontmatter parser
 */
function parseFrontmatter(frontmatterStr) {
  const lines = frontmatterStr.split('\n');
  const result = {};

  for (const line of lines) {
    const colonIndex = line.indexOf(':');
    if (colonIndex > 0) {
      const key = line.substring(0, colonIndex).trim();
      let value = line.substring(colonIndex + 1).trim();

      // Handle string values in quotes
      if (value.startsWith('"') && value.endsWith('"')) {
        value = value.substring(1, value.length - 1);
      } else if (value.startsWith("'") && value.endsWith("'")) {
        value = value.substring(1, value.length - 1);
      } else if (value === 'true') {
        value = true;
      } else if (value === 'false') {
        value = false;
      } else if (!isNaN(value) && value.trim() !== '') {
        value = Number(value);
      }

      result[key] = value;
    }
  }

  return result;
}

/**
 * Checks for proper navigation setup
 */
async function checkNavigationSetup(docsDir) {
  const issues = [];
  const recommendations = [];

  try {
    // Check for sidebar configuration
    const sidebarPath = path.join(process.cwd(), 'docs', 'sidebar.js');
    try {
      await fs.access(sidebarPath);
    } catch (e) {
      // If sidebar.js doesn't exist in docs, check root
      const rootSidebarPath = path.join(process.cwd(), 'sidebar.js');
      try {
        await fs.access(rootSidebarPath);
      } catch (e2) {
        recommendations.push(`Consider creating a sidebar configuration file`);
      }
    }

    // Check for category files
    const categoryFiles = await getCategoryFiles(docsDir);
    if (categoryFiles.length === 0) {
      recommendations.push(`Consider organizing content with _category_.json files`);
    }

  } catch (error) {
    issues.push(`Error checking navigation setup: ${error.message}`);
  }

  return { isValid: issues.length === 0, issues, recommendations };
}

/**
 * Checks for proper MDX practices
 */
async function checkMdxPractices(docsDir) {
  const issues = [];
  const recommendations = [];

  try {
    const mdxFiles = await getMdxFiles(docsDir);

    for (const file of mdxFiles) {
      const content = await fs.readFile(file, 'utf8');

      // Check for proper heading hierarchy
      const headings = content.match(/^(#{1,6})\s+(.+)$/gm) || [];
      let lastLevel = 0;
      for (const heading of headings) {
        const level = heading.match(/^(#{1,6})/)[0].length;
        if (level > lastLevel + 1 && lastLevel !== 0) {
          recommendations.push(`Improper heading hierarchy in ${file}: H${level} follows H${lastLevel}, consider H${lastLevel + 1}`);
        }
        lastLevel = level;
      }

      // Check for H1 usage (should only have one per document)
      const h1Matches = content.match(/^#\s+(.+)$/gm) || [];
      if (h1Matches.length === 0) {
        recommendations.push(`Consider adding an H1 heading in ${file}`);
      } else if (h1Matches.length > 1) {
        issues.push(`Multiple H1 headings found in ${file}, only one should be present`);
      }

      // Check for proper content structure
      if (content.length < 100) {
        recommendations.push(`Document ${file} is very short, consider adding more content`);
      }
    }
  } catch (error) {
    issues.push(`Error checking MDX practices: ${error.message}`);
  }

  return { isValid: issues.length === 0, issues, recommendations };
}

/**
 * Gets all files in directory recursively
 */
async function getAllFiles(dir) {
  const entries = await fs.readdir(dir, { withFileTypes: true });
  let files = [];

  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);

    if (entry.isDirectory()) {
      const subDirFiles = await getAllFiles(fullPath);
      files = files.concat(subDirFiles);
    } else {
      files.push(fullPath);
    }
  }

  return files;
}

/**
 * Gets all MDX files in directory
 */
async function getMdxFiles(dir) {
  const entries = await fs.readdir(dir, { withFileTypes: true });
  let files = [];

  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);

    if (entry.isDirectory()) {
      const subDirFiles = await getMdxFiles(fullPath);
      files = files.concat(subDirFiles);
    } else if (path.extname(entry.name) === '.mdx') {
      files.push(fullPath);
    }
  }

  return files;
}

/**
 * Gets all category files in directory
 */
async function getCategoryFiles(dir) {
  const entries = await fs.readdir(dir, { withFileTypes: true });
  let files = [];

  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);

    if (entry.isDirectory()) {
      const subDirFiles = await getCategoryFiles(fullPath);
      files = files.concat(subDirFiles);
    } else if (entry.name === '_category_.json') {
      files.push(fullPath);
    }
  }

  return files;
}

// Command line interface
if (require.main === module) {
  const args = process.argv.slice(2);
  const docsDir = args[0] || './docs';

  (async () => {
    console.log(`Verifying Docusaurus best practices for: ${docsDir}\n`);

    const results = await verifyDocusaurusBestPractices(docsDir);

    console.log(`Compliance Score: ${results.complianceScore}%`);
    console.log(`Best Practices Met: ${results.bestPracticesMet ? 'Yes' : 'No'}\n`);

    if (results.issues.length > 0) {
      console.log(`❌ Issues Found (${results.issues.length}):`);
      results.issues.forEach((issue, index) => {
        console.log(`  ${index + 1}. ${issue}`);
      });
      console.log('');
    }

    if (results.recommendations.length > 0) {
      console.log(`💡 Recommendations (${results.recommendations.length}):`);
      results.recommendations.forEach((rec, index) => {
        console.log(`  ${index + 1}. ${rec}`);
      });
      console.log('');
    }

    if (results.issues.length === 0) {
      console.log('✅ All Docusaurus best practices verification passed!');
    } else {
      console.log('⚠️  Some issues were found that should be addressed.');
      process.exit(1);
    }

    console.log('\nStatistics:');
    console.log(`  Total files: ${results.stats.totalFiles}`);
    console.log(`  MDX files: ${results.stats.mdxFiles}`);
    console.log(`  Category files: ${results.stats.categoryFiles}`);
    console.log(`  Total size: ${results.stats.totalSize} bytes`);
  })();
}

module.exports = {
  verifyDocusaurusBestPractices
};
