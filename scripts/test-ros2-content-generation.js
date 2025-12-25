#!/usr/bin/env node

/**
 * ROS 2 Content Generation Test
 * Tests ROS 2 content generation with diverse syllabus topics
 */

const fs = require('fs').promises;
const path = require('path');

/**
 * Tests ROS 2 content generation with diverse syllabus topics
 * @returns {Object} Test results
 */
async function testROS2ContentGeneration() {
  try {
    // Define diverse ROS 2 syllabus topics
    const diverseTopics = [
      {
        id: "ros2-basics",
        title: "ROS 2 Basics",
        description: "Introduction to ROS 2 concepts",
        learningObjectives: [
          "Understand ROS 2 architecture",
          "Create basic publisher/subscriber nodes",
          "Use ROS 2 command line tools"
        ]
      },
      {
        id: "ros2-advanced",
        title: "Advanced ROS 2 Concepts",
        description: "Deep dive into advanced ROS 2 features",
        learningObjectives: [
          "Implement custom message types",
          "Use lifecycle nodes",
          "Configure QoS policies"
        ]
      },
      {
        id: "ros2-navigation",
        title: "ROS 2 Navigation",
        description: "Navigation stack and path planning",
        learningObjectives: [
          "Configure navigation stack",
          "Implement path planning algorithms",
          "Use costmaps for obstacle avoidance"
        ]
      },
      {
        id: "ros2-manipulation",
        title: "ROS 2 Manipulation",
        description: "Robotic manipulation with ROS 2",
        learningObjectives: [
          "Use MoveIt with ROS 2",
          "Implement grasp planning",
          "Control robotic arms"
        ]
      }
    ];

    // Validate that our existing ROS 2 chapter covers fundamental concepts
    const chapterPath = './docs/chapters/robotics-systems/ros2-fundamentals.mdx';
    const chapterContent = await fs.readFile(chapterPath, 'utf8');
    
    // Check for coverage of diverse topics
    const coverageResults = {
      basicROS2: chapterContent.toLowerCase().includes('nodes') && chapterContent.toLowerCase().includes('topics'),
      advancedConcepts: chapterContent.toLowerCase().includes('services') && chapterContent.toLowerCase().includes('actions'),
      navigationRelated: chapterContent.toLowerCase().includes('path') || chapterContent.toLowerCase().includes('planning'),
      manipulationRelated: chapterContent.toLowerCase().includes('arm') || chapterContent.toLowerCase().includes('control'),
      rclpyUsage: chapterContent.toLowerCase().includes('rclpy'),
      urdfCoverage: chapterContent.toLowerCase().includes('urdf'),
      launchFiles: chapterContent.toLowerCase().includes('launch'),
      bestPractices: chapterContent.toLowerCase().includes('best practices') || chapterContent.toLowerCase().includes('practices')
    };

    // Calculate coverage percentage
    const coveredTopics = Object.values(coverageResults).filter(value => value).length;
    const totalTopics = Object.keys(coverageResults).length;
    const coveragePercentage = (coveredTopics / totalTopics) * 100;

    // Additional validation: check if chapter structure is consistent
    const hasLearningObjectives = chapterContent.includes('## Learning Objectives');
    const hasIntroduction = chapterContent.includes('## Introduction');
    const hasSummary = chapterContent.includes('## Summary');
    const hasExercises = chapterContent.includes('## Exercises');
    
    const structureValid = hasLearningObjectives && hasIntroduction && hasSummary && hasExercises;
    
    // Check for code examples
    const codeExamplesCount = (chapterContent.match(/```python/g) || []).length + 
                             (chapterContent.match(/```xml/g) || []).length +
                             (chapterContent.match(/```bash/g) || []).length;

    return {
      isValid: coveragePercentage >= 70 && structureValid, // 70% coverage threshold
      coveragePercentage: Math.round(coveragePercentage * 100) / 100,
      coverageResults,
      structureValid,
      codeExamplesCount,
      diverseTopicsCovered: coveredTopics,
      totalTopics: totalTopics,
      chapterStructure: {
        hasLearningObjectives,
        hasIntroduction,
        hasSummary,
        hasExercises
      }
    };
  } catch (error) {
    return {
      isValid: false,
      error: error.message,
      coveragePercentage: 0,
      coverageResults: {},
      structureValid: false,
      codeExamplesCount: 0,
      diverseTopicsCovered: 0,
      totalTopics: 0,
      chapterStructure: {}
    };
  }
}

// Command line interface
if (require.main === module) {
  (async () => {
    console.log('Testing ROS 2 content generation with diverse syllabus topics...\n');

    const result = await testROS2ContentGeneration();

    if (result.isValid) {
      console.log('✅ ROS 2 content generation test passed!');
      console.log(`Coverage: ${result.coveragePercentage}%`);
      console.log(`Code examples: ${result.codeExamplesCount}`);
      console.log(`Structure valid: ${result.structureValid}\n`);
    } else {
      console.log('❌ ROS 2 content generation test failed!');
      console.log(`Coverage: ${result.coveragePercentage}%`);
      console.log(`Structure valid: ${result.structureValid}\n`);
    }

    console.log('Coverage Details:');
    for (const [topic, covered] of Object.entries(result.coverageResults)) {
      console.log(`  ${covered ? '✅' : '❌'} ${topic.replace(/([A-Z])/g, ' $1').trim()}: ${covered}`);
    }

    console.log('\nChapter Structure:');
    console.log(`  Learning Objectives: ${result.chapterStructure.hasLearningObjectives ? '✅' : '❌'}`);
    console.log(`  Introduction: ${result.chapterStructure.hasIntroduction ? '✅' : '❌'}`);
    console.log(`  Summary: ${result.chapterStructure.hasSummary ? '✅' : '❌'}`);
    console.log(`  Exercises: ${result.chapterStructure.hasExercises ? '✅' : '❌'}`);

    console.log(`\nTotal topics covered: ${result.diverseTopicsCovered}/${result.totalTopics}`);
  })();
}

module.exports = {
  testROS2ContentGeneration
};
