#!/usr/bin/env node

/**
 * Syllabus Parser
 * Parses syllabus input to identify topics and structure
 */

const fs = require('fs').promises;
const path = require('path');

/**
 * Parses syllabus input from JSON file
 * @param {string} syllabusPath - Path to the syllabus JSON file
 * @returns {Object} Parsed syllabus with validation
 */
async function parseSyllabus(syllabusPath) {
  try {
    // Read the syllabus file
    const syllabusContent = await fs.readFile(syllabusPath, 'utf8');
    const syllabus = JSON.parse(syllabusContent);

    // Validate the syllabus structure
    const validation = validateSyllabus(syllabus);

    if (!validation.isValid) {
      throw new Error(`Syllabus validation failed: ${validation.errors.join(', ')}`);
    }

    // Normalize the syllabus data
    const normalizedSyllabus = normalizeSyllabus(syllabus);

    return {
      isValid: true,
      syllabus: normalizedSyllabus,
      stats: getStats(normalizedSyllabus),
      validation: validation
    };
  } catch (error) {
    return {
      isValid: false,
      error: error.message,
      syllabus: null
    };
  }
}

/**
 * Validates the syllabus structure
 * @param {Object} syllabus - Raw syllabus object
 * @returns {Object} Validation result
 */
function validateSyllabus(syllabus) {
  const errors = [];

  // Validate required fields at top level
  if (!syllabus.title || typeof syllabus.title !== 'string') {
    errors.push('Missing or invalid title');
  }

  if (!syllabus.description || typeof syllabus.description !== 'string') {
    errors.push('Missing or invalid description');
  }

  if (!syllabus.topics || !Array.isArray(syllabus.topics)) {
    errors.push('Missing or invalid topics array');
  } else {
    // Validate each topic
    syllabus.topics.forEach((topic, index) => {
      if (!topic.id || typeof topic.id !== 'string') {
        errors.push(`Topic ${index}: Missing or invalid id`);
      }

      if (!topic.title || typeof topic.title !== 'string') {
        errors.push(`Topic ${index}: Missing or invalid title`);
      }

      if (!topic.description || typeof topic.description !== 'string') {
        errors.push(`Topic ${index}: Missing or invalid description`);
      }

      if (!topic.learningObjectives || !Array.isArray(topic.learningObjectives)) {
        errors.push(`Topic ${index}: Missing or invalid learningObjectives`);
      } else if (topic.learningObjectives.length === 0) {
        errors.push(`Topic ${index}: learningObjectives array is empty`);
      }

      if (topic.prerequisites && !Array.isArray(topic.prerequisites)) {
        errors.push(`Topic ${index}: prerequisites must be an array`);
      }
    });
  }

  return {
    isValid: errors.length === 0,
    errors: errors
  };
}

/**
 * Normalizes syllabus data to ensure consistent structure
 * @param {Object} syllabus - Raw syllabus object
 * @returns {Object} Normalized syllabus
 */
function normalizeSyllabus(syllabus) {
  const normalized = { ...syllabus };

  // Normalize topics
  normalized.topics = syllabus.topics.map(topic => ({
    id: topic.id.trim(),
    title: topic.title.trim(),
    description: topic.description.trim(),
    learningObjectives: Array.isArray(topic.learningObjectives)
      ? topic.learningObjectives.map(obj => obj.trim())
      : [],
    category: topic.category || 'Uncategorized',
    prerequisites: Array.isArray(topic.prerequisites)
      ? topic.prerequisites.map(p => p.trim())
      : [],
    position: topic.position || 0 // Will be set later based on dependencies
  }));

  return normalized;
}

/**
 * Gets statistics about the syllabus
 * @param {Object} syllabus - Normalized syllabus
 * @returns {Object} Statistics
 */
function getStats(syllabus) {
  return {
    topicCount: syllabus.topics.length,
    categories: [...new Set(syllabus.topics.map(t => t.category))],
    categoryCount: new Set(syllabus.topics.map(t => t.category)).size,
    totalLearningObjectives: syllabus.topics.reduce((sum, topic) => sum + topic.learningObjectives.length, 0),
    hasPrerequisites: syllabus.topics.some(t => t.prerequisites.length > 0)
  };
}

/**
 * Resolves topic dependencies and sets positions
 * @param {Object} syllabus - Normalized syllabus
 * @returns {Object} Syllabus with resolved positions
 */
function resolveDependencies(syllabus) {
  const result = { ...syllabus };
  const topics = [...syllabus.topics];
  const resolved = [];
  const unresolved = [...topics];
  const positions = new Map();

  // Simple dependency resolution - topics with prerequisites come after their prerequisites
  while (unresolved.length > 0) {
    let resolvedInThisIteration = false;

    for (let i = 0; i < unresolved.length; i++) {
      const topic = unresolved[i];
      const allPrereqsResolved = topic.prerequisites.every(prereq =>
        resolved.some(r => r.id === prereq) || positions.has(prereq)
      );

      if (allPrereqsResolved) {
        resolved.push(topic);
        positions.set(topic.id, resolved.length - 1);
        unresolved.splice(i, 1);
        resolvedInThisIteration = true;
        i--; // Adjust index after removal
      }
    }

    // If no topics were resolved in this iteration, we have a circular dependency
    if (!resolvedInThisIteration) {
      throw new Error(`Circular dependency detected: ${unresolved.map(t => t.id).join(', ')}`);
    }
  }

  // Update positions in the topics
  result.topics = resolved.map((topic, index) => ({
    ...topic,
    position: index
  }));

  return result;
}

// Command line interface
if (require.main === module) {
  const args = process.argv.slice(2);
  const syllabusPath = args[0] || './sample-syllabus.json';

  (async () => {
    console.log(`Parsing syllabus from: ${syllabusPath}\n`);

    const result = await parseSyllabus(syllabusPath);

    if (result.isValid) {
      console.log('✅ Syllabus parsed successfully!\n');

      console.log('Syllabus Information:');
      console.log(`Title: ${result.syllabus.title}`);
      console.log(`Description: ${result.syllabus.description}`);
      console.log(`Topics: ${result.stats.topicCount}`);
      console.log(`Categories: ${result.stats.categoryCount}`);
      console.log(`Total Learning Objectives: ${result.stats.totalLearningObjectives}`);
      console.log(`Has Prerequisites: ${result.stats.hasPrerequisites ? 'Yes' : 'No'}`);

      console.log('\nCategories:', result.stats.categories.join(', '));

      console.log('\nTopics:');
      result.syllabus.topics.forEach(topic => {
        console.log(`  - ${topic.position + 1}. ${topic.title} (${topic.id}) [${topic.category}]`);
        console.log(`    Prerequisites: ${topic.prerequisites.length > 0 ? topic.prerequisites.join(', ') : 'None'}`);
        console.log(`    Learning Objectives: ${topic.learningObjectives.length}`);
      });

      // Try to resolve dependencies
      try {
        const resolvedSyllabus = resolveDependencies(result.syllabus);
        console.log('\n✅ Dependencies resolved successfully!');
        console.log('Topics in learning order:');
        resolvedSyllabus.topics.forEach(topic => {
          console.log(`  - ${topic.position + 1}. ${topic.title}`);
        });
      } catch (error) {
        console.error(`\n❌ Dependency resolution failed: ${error.message}`);
      }
    } else {
      console.error(`❌ Syllabus parsing failed: ${result.error}`);
      process.exit(1);
    }
  })();
}

module.exports = {
  parseSyllabus,
  validateSyllabus,
  normalizeSyllabus,
  getStats,
  resolveDependencies
};
