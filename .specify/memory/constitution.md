<!-- SYNC IMPACT REPORT
Version change: N/A (initial version) → 1.0.0
Modified principles: N/A
Added sections: All principles and sections (initial constitution)
Removed sections: N/A
Templates requiring updates:
- .specify/templates/plan-template.md: ⚠ pending
- .specify/templates/spec-template.md: ⚠ pending
- .specify/templates/tasks-template.md: ⚠ pending
- .specify/commands/sp.constitution.md: ⚠ pending
Follow-up TODOs: None
-->
# AI/Spec-Driven Technical Book Creation Constitution

## Core Principles

### I. Spec-First Development
All book structure, chapters, workflows, and content must originate from explicit specifications: /sp.constitution, /sp.specify, /sp.plan, /sp.tasks. No documentation content may exist without a corresponding specification.

### II. AI-Assisted, Human-Directed
Claude Code is used to draft, refactor, summarize, and validate content. Human intent, specifications, and acceptance criteria always override AI-generated output.

### III. Source-Grounded Content
All technical explanations must be grounded in official Docusaurus documentation and verified references accessed via Context7 MCP. Hallucinated, speculative, or unverified information is strictly prohibited.

### IV. Modular & Maintainable Documentation
The book must follow Docusaurus best practices: clear sidebar-based navigation, modular Markdown / MDX files, logical chapter separation, consistent formatting and tone.

### V. Reproducibility & Transparency
Any developer should be able to clone the repository, review the specs, regenerate the book, and build and redeploy the site using the same workflow.

### VI. Test-First (NON-NEGOTIABLE)
TDD mandatory: Tests written → User approved → Tests fail → Then implement; Red-Green-Refactor cycle strictly enforced for all code components and book generation processes.

## Additional Constraints

Technology stack requirements: Docusaurus framework, Markdown/MDX content format, GitHub Pages deployment, Context7 MCP for verified documentation sources, Spec-Kit Plus for specifications.

Deployment policies: All changes must be validated through automated checks before merging. Public deployment to GitHub Pages requires successful build validation.

## Development Workflow

Code review requirements: All PRs must verify compliance with specifications and constitution principles. Changes to book content must include appropriate acceptance criteria validation.

Quality gates: All technical content must be source-grounded, specifications must be updated when implementing new features, and Prompt History Records (PHRs) must be created for all significant development activities.

## Governance

The constitution supersedes all other practices. Amendments require documentation, approval, and migration plan when applicable. All PRs/reviews must verify compliance with constitution principles.

**Version**: 1.0.0 | **Ratified**: 2025-12-24 | **Last Amended**: 2025-12-24