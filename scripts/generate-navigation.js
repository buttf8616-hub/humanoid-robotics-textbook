#!/usr/bin/env node

/**
 * Navigation Generator
 * Generates navigation structure in sidebar with category support
 */

const fs = require('fs').promises;
const path = require('path');

/**
 * Generates navigation structure based on syllabus topics and categories
 * @param {Object} syllabus - Parsed syllabus with resolved dependencies
 * @param {string} outputDir - Output directory for navigation files
 * @returns {Object} Generation results
 */
async function generateNavigation(syllabus, outputDir = './docs/chapters') {
  try {
    // Group topics by category
    const categories = groupTopicsByCategory(syllabus.topics);
    
    // Generate _category_.json for each category
    for (const [categoryName, topics] of Object.entries(categories)) {
      const categoryDir = path.join(outputDir, categoryName.toLowerCase().replace(/\s+/g, '-'));
      
      // Create category directory
      await fs.mkdir(categoryDir, { recursive: true });
      
      // Create category configuration
      const categoryConfig = {
        label: categoryName,
        collapsible: true,
        collapsed: false,
        link: {
          type: 'generated-index',
          title: `${categoryName} Overview`,
          description: `Learn about ${categoryName} in Physical AI & Humanoid Robotics`
        }
      };
      
      const categoryConfigPath = path.join(categoryDir, '_category_.json');
      await fs.writeFile(categoryConfigPath, JSON.stringify(categoryConfig, null, 2));
      console.log(`✅ Generated category config: ${categoryConfigPath}`);
      
      // Move topic files to category directory
      for (const topic of topics) {
        const sourcePath = path.join(outputDir, `${topic.id}.mdx`);
        const targetPath = path.join(categoryDir, `${topic.id}.mdx`);
        
        // Check if source file exists before moving
        try {
          await fs.access(sourcePath);
          await fs.rename(sourcePath, targetPath);
          console.log(`✅ Moved chapter to category: ${targetPath}`);
        } catch (err) {
          // If file doesn't exist in root, it might already be moved or we need to create it in the category
          // Create the file in the category directory
          const { generateChapterContent } = require('./generate-chapters');
          const content = generateChapterContent(topic);
          await fs.writeFile(targetPath, content);
          console.log(`✅ Created chapter in category: ${targetPath}`);
        }
      }
    }
    
    // Generate sidebar configuration
    const sidebarConfig = generateSidebarConfig(categories);
    const sidebarPath = path.join(outputDir, '../sidebar.js');
    await fs.writeFile(sidebarPath, `module.exports = ${JSON.stringify(sidebarConfig, null, 2)};`);
    console.log(`✅ Generated sidebar config: ${sidebarPath}`);
    
    // Update docusaurus.config.js to use the new sidebar
    await updateDocusaurusConfig();
    
    return {
      success: true,
      categories: Object.keys(categories),
      categoryCount: Object.keys(categories).length,
      categoriesData: categories
    };
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Groups topics by category
 * @param {Array} topics - Array of topic objects
 * @returns {Object} Topics grouped by category
 */
function groupTopicsByCategory(topics) {
  const categories = {};
  
  // Sort topics by position to maintain learning progression within categories
  const sortedTopics = [...topics].sort((a, b) => a.position - b.position);
  
  for (const topic of sortedTopics) {
    const category = topic.category;
    if (!categories[category]) {
      categories[category] = [];
    }
    categories[category].push(topic);
  }
  
  return categories;
}

/**
 * Generates sidebar configuration
 * @param {Object} categories - Topics grouped by category
 * @returns {Object} Sidebar configuration
 */
function generateSidebarConfig(categories) {
  const sidebar = {
    chapters: [
      {
        type: 'category',
        label: 'Physical AI & Humanoid Robotics',
        collapsed: false,
        items: []
      }
    ]
  };
  
  // Add categories to sidebar
  for (const [categoryName, topics] of Object.entries(categories)) {
    const categoryItems = topics.map(topic => {
      return {
        type: 'doc',
        id: `chapters/${categoryName.toLowerCase().replace(/\s+/g, '-')}/${topic.id}`,
        label: topic.title
      };
    });
    
    sidebar.chapters[0].items.push({
      type: 'category',
      label: categoryName,
      collapsed: false,
      items: categoryItems
    });
  }
  
  return sidebar;
}

/**
 * Updates docusaurus.config.js to use the new sidebar
 */
async function updateDocusaurusConfig() {
  try {
    const configPath = './docusaurus.config.js';
    let configContent = await fs.readFile(configPath, 'utf8');
    
    // Check if the docs config already includes a custom sidebar
    if (!configContent.includes('sidebar.js')) {
      // Add sidebar path to the docs plugin configuration
      configContent = configContent.replace(
        /(\s*)sidebarPath: require.resolve\('\.\/sidebars\.js'\),?/,
        `\$1sidebarPath: require.resolve('./sidebar.js'),`
      );
      
      // If sidebars.js doesn't exist in the pattern, add it
      if (!configContent.includes('sidebarPath:')) {
        configContent = configContent.replace(
          /(themeConfig:[^}]*)docs:\s*{/,
          `\$1docs: {
          sidebarPath: require.resolve('./sidebar.js'),`
        );
      }
      
      await fs.writeFile(configPath, configContent);
      console.log('✅ Updated docusaurus.config.js to use new sidebar');
    }
  } catch (error) {
    console.warn(`⚠️ Could not update docusaurus.config.js: ${error.message}`);
  }
}

// Command line interface
if (require.main === module) {
  const args = process.argv.slice(2);
  const syllabusPath = args[0] || './sample-syllabus.json';
  const outputDir = args[1] || './docs/chapters';

  (async () => {
    console.log(`Generating navigation structure from syllabus: ${syllabusPath}`);
    console.log(`Output directory: ${outputDir}\n`);

    // Import and parse the syllabus
    const { parseSyllabus, resolveDependencies } = require('./parse-syllabus');
    const parseResult = await parseSyllabus(syllabusPath);

    if (!parseResult.isValid) {
      console.error(`❌ Syllabus parsing failed: ${parseResult.error}`);
      process.exit(1);
    }

    // Resolve dependencies to get proper order
    const resolvedSyllabus = resolveDependencies(parseResult.syllabus);

    // Generate navigation
    const result = await generateNavigation(resolvedSyllabus, outputDir);

    if (result.success) {
      console.log(`\n✅ Successfully generated navigation structure for ${result.categoryCount} categories:`);
      result.categories.forEach(category => console.log(`  - ${category}`));
      
      console.log('\nThe chapters have been organized by category and the sidebar has been updated.');
    } else {
      console.error(`❌ Navigation generation failed: ${result.error}`);
      process.exit(1);
    }
  })();
}

module.exports = {
  generateNavigation,
  groupTopicsByCategory,
  generateSidebarConfig
};
