# Quickstart Guide: Physical AI & Humanoid Robotics Book Generation

## Prerequisites

- Node.js (LTS version recommended)
- npm or yarn package manager
- Access to Claude Code for AI assistance
- Access to Context7 MCP for robotics documentation verification

## Setup

1. **Initialize Docusaurus Project**
   ```bash
   npx create-docusaurus@latest website classic
   cd website
   ```

2. **Install Additional Dependencies**
   ```bash
   npm install --save-dev @docusaurus/module-type-aliases @docusaurus/types
   ```

3. **Project Structure Setup**
   Create the following directory structure:
   ```
   docs/
   ├── intro.md
   ├── chapters/            # Generated from syllabus topics
   │   ├── intro-physical-ai.md
   │   ├── ros2-fundamentals.mdx
   │   ├── simulation-environments.mdx
   │   ├── nvidia-isaac.mdx
   │   ├── vision-language-action.mdx
   │   └── capstone-project.mdx
   ├── _category_.json      # Navigation structure
   └── sidebar.js           # Sidebar configuration
   src/
   ├── components/          # Custom Docusaurus components
   ├── pages/              # Additional pages if needed
   └── css/                # Custom styles
   scripts/                 # Build and generation scripts
   ```

## Basic Workflow

### 1. Prepare Syllabus Input
- Organize your Physical AI & Humanoid Robotics syllabus topics in a structured format
- Identify learning objectives for each robotics topic
- Note any prerequisite relationships between robotics modules

### 2. Generate Book Structure
- Create chapter stubs in `docs/chapters/` for each syllabus topic
- Set up navigation in `sidebar.js` or `_category_.json`
- Ensure proper hierarchy and ordering following the syllabus progression

### 3. Generate Content with AI Assistance
- Use Claude Code to generate robotics-specific content for each chapter
- Ensure content is grounded in official robotics documentation (Context7 MCP)
- Validate content accuracy against verified robotics sources (ROS 2, Gazebo, NVIDIA Isaac, etc.)

### 4. Build and Preview
```bash
npm run start
```
This will start the development server and open the documentation site in your browser.

### 5. Validate Content Compliance
- Run validation scripts to check syllabus-topic mapping
- Verify robotics content accuracy against official documentation sources
- Ensure all constitution principles are followed

## Key Scripts

### Book Generation Script
```bash
node scripts/generate-book.js --syllabus path/to/physical-ai-syllabus.json
```

### Content Validation Script
```bash
node scripts/validate-content.js --docs docs/ --robotics-frameworks ros2,gazebo,nvidia-isaac
```

## Configuration

### Docusaurus Configuration
Update `docusaurus.config.js` with:
- Site metadata (title, tagline, URL)
- Navigation configuration
- Theme customization
- Plugin configurations

### Navigation Setup
Configure `docs/sidebar.js` or `docs/_category_.json` to define:
- Chapter ordering following the Physical AI syllabus
- Category groupings (Fundamentals, Simulation, AI, etc.)
- Navigation hierarchy

## Robotics Framework Integration

### ROS 2 Content
- Focus on nodes, topics, services, and rclpy agents
- Include URDF examples for humanoid robot modeling
- Provide practical examples for robot control

### Simulation Platforms (Gazebo/Unity)
- Cover physics simulation, collisions, and dynamics
- Include sensor simulation (LiDAR, cameras, IMUs)
- Provide high-fidelity environment examples

### NVIDIA Isaac
- Cover Isaac Sim for synthetic data generation
- Include Isaac ROS acceleration examples
- Provide VSLAM and Nav2 navigation examples

### Vision-Language-Action
- Include voice-to-action pipeline examples
- Cover OpenAI Whisper for speech input
- Provide LLM-based cognitive planning examples

## Deployment

### Local Build
```bash
npm run build
```

### GitHub Pages Deployment
1. Configure GitHub Actions workflow
2. Set up deployment settings in repository
3. Push to main branch to trigger deployment