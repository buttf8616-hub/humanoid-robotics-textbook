# Quickstart Guide: Syllabus-Driven Technical Book Generation

## Prerequisites

- Node.js (LTS version recommended)
- npm or yarn package manager
- Access to Claude Code for AI assistance
- Access to Context7 MCP for documentation verification

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
   ├── chapters/
   └── _category_.json
   src/
   ├── components/
   ├── pages/
   └── css/
   scripts/
   ```

## Basic Workflow

### 1. Prepare Syllabus Input
- Organize your syllabus topics in a structured format
- Identify learning objectives for each topic
- Note any prerequisite relationships between topics

### 2. Generate Book Structure
- Create chapter stubs in `docs/chapters/` for each syllabus topic
- Set up navigation in `sidebar.js` or `_category_.json`
- Ensure proper hierarchy and ordering

### 3. Generate Content with AI Assistance
- Use Claude Code to generate content for each chapter
- Ensure content is grounded in official documentation (Context7 MCP)
- Validate content accuracy against verified sources

### 4. Build and Preview
```bash
npm run start
```
This will start the development server and open the documentation site in your browser.

### 5. Validate Content Compliance
- Run validation scripts to check syllabus-topic mapping
- Verify content accuracy against documentation sources
- Ensure all constitution principles are followed

## Key Scripts

### Book Generation Script
```bash
node scripts/generate-book.js --syllabus path/to/syllabus.json
```

### Content Validation Script
```bash
node scripts/validate-content.js --docs docs/
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
- Chapter ordering
- Category groupings
- Navigation hierarchy

## Deployment

### Local Build
```bash
npm run build
```

### GitHub Pages Deployment
1. Configure GitHub Actions workflow
2. Set up deployment settings in repository
3. Push to main branch to trigger deployment