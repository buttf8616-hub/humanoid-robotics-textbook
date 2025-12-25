#!/usr/bin/env node

/**
 * ROS 2 Content Validator
 * Validates chapter content against official ROS 2 documentation sources
 */

const fs = require('fs').promises;
const path = require('path');

/**
 * Validates ROS 2 content against official documentation
 * @param {string} chapterPath - Path to the chapter file
 * @returns {Object} Validation results
 */
async function validateROS2Content(chapterPath) {
  try {
    const content = await fs.readFile(chapterPath, 'utf8');
    
    // Define ROS 2 validation criteria based on official documentation
    const validationCriteria = {
      nodes: {
        keywords: ['rclpy', 'Node', 'create_publisher', 'create_subscription', 'create_service', 'create_client'],
        requiredPatterns: [
          /class\s+\w+\(Node\)/,  // Node class inheritance
          /rclpy\.init/,          // rclpy initialization
          /rclpy\.spin/           // rclpy spin
        ],
        weight: 1.0
      },
      topics: {
        keywords: ['publisher', 'subscription', 'msg', 'std_msgs', 'sensor_msgs'],
        requiredPatterns: [
          /create_publisher\(/,     // Publisher creation
          /create_subscription\(/,  // Subscription creation
          /\.publish\(/
        ],
        weight: 1.0
      },
      services: {
        keywords: ['service', 'srv', 'example_interfaces', 'request', 'response'],
        requiredPatterns: [
          /create_service\(/,  // Service creation
          /call_async/,       // Service call
          /wait_for_service/   // Service availability check
        ],
        weight: 0.8
      },
      actions: {
        keywords: ['action', 'ActionClient', 'ActionServer', 'action_msgs'],
        requiredPatterns: [
          /ActionClient/,     // Action client
          /ActionServer/,     // Action server
          /SendGoalRequest/   // Goal request
        ],
        weight: 0.7
      },
      rclpy: {
        keywords: ['rclpy', 'node', 'timer', 'callback'],
        requiredPatterns: [
          /rclpy\.init/,
          /rclpy\.spin/,
          /rclpy\.shutdown/
        ],
        weight: 1.0
      },
      urdf: {
        keywords: ['URDF', 'robot', 'link', 'joint', 'visual', 'collision'],
        requiredPatterns: [
          /<robot/,
          /<link/,
          /<joint/,
          /<visual/,
          /<collision/
        ],
        weight: 0.9
      },
      launch: {
        keywords: ['launch', 'LaunchDescription', 'Node', 'ros2 launch'],
        requiredPatterns: [
          /LaunchDescription/,
          /Node\(/  // launch_ros.actions.Node
        ],
        weight: 0.7
      }
    };

    // Check content against criteria
    const results = {};
    let totalScore = 0;
    let maxPossibleScore = 0;

    for (const [category, criteria] of Object.entries(validationCriteria)) {
      const foundKeywords = [];
      const satisfiedPatterns = [];
      
      // Check keywords
      for (const keyword of criteria.keywords) {
        if (content.toLowerCase().includes(keyword.toLowerCase())) {
          foundKeywords.push(keyword);
        }
      }
      
      // Check patterns
      for (const pattern of criteria.requiredPatterns) {
        if (pattern.test(content)) {
          satisfiedPatterns.push(pattern.toString());
        }
      }
      
      const keywordScore = foundKeywords.length / criteria.keywords.length;
      const patternScore = satisfiedPatterns.length / criteria.requiredPatterns.length;
      const categoryScore = (keywordScore + patternScore) / 2;
      
      results[category] = {
        score: categoryScore,
        foundKeywords,
        missingKeywords: criteria.keywords.filter(k => !foundKeywords.includes(k)),
        satisfiedPatterns,
        missingPatterns: criteria.requiredPatterns.filter(p => !satisfiedPatterns.includes(p.toString())),
        weight: criteria.weight
      };
      
      totalScore += categoryScore * criteria.weight;
      maxPossibleScore += 1.0 * criteria.weight;
    }

    const overallCompliance = maxPossibleScore > 0 ? (totalScore / maxPossibleScore) * 100 : 0;

    return {
      isValid: overallCompliance >= 80, // 80% threshold
      overallCompliance: Math.round(overallCompliance * 100) / 100,
      results,
      totalScore,
      maxPossibleScore
    };
  } catch (error) {
    return {
      isValid: false,
      error: error.message,
      overallCompliance: 0,
      results: {},
      totalScore: 0,
      maxPossibleScore: 0
    };
  }
}

// Command line interface
if (require.main === module) {
  const args = process.argv.slice(2);
  const chapterPath = args[0] || './docs/chapters/robotics-systems/ros2-fundamentals.mdx';

  (async () => {
    console.log(`Validating ROS 2 content against official documentation: ${chapterPath}\n`);

    const result = await validateROS2Content(chapterPath);

    if (result.isValid) {
      console.log(`✅ Content validation passed!`);
      console.log(`Overall Compliance: ${result.overallCompliance}%`);
      console.log(`Threshold: 80% (PASS)\n`);
    } else {
      console.log(`❌ Content validation failed!`);
      console.log(`Overall Compliance: ${result.overallCompliance}%`);
      console.log(`Threshold: 80% (FAIL)\n`);
    }

    console.log('Detailed Results by Category:');
    for (const [category, data] of Object.entries(result.results)) {
      console.log(`\n${category.toUpperCase()}:`);
      console.log(`  Score: ${(data.score * 100).toFixed(1)}%`);
      console.log(`  Weight: ${data.weight}`);
      console.log(`  Found keywords: ${data.foundKeywords.length}/${data.foundKeywords.length + data.missingKeywords.length}`);
      console.log(`  Satisfied patterns: ${data.satisfiedPatterns.length}/${data.satisfiedPatterns.length + data.missingPatterns.length}`);
      
      if (data.missingKeywords.length > 0) {
        console.log(`  Missing keywords: ${data.missingKeywords.join(', ')}`);
      }
      
      if (data.missingPatterns.length > 0) {
        console.log(`  Missing patterns: ${data.missingPatterns.map(p => p.replace(/\/(.+)\//, '$1')).join(', ')}`);
      }
    }
  })();
}

module.exports = {
  validateROS2Content
};
