---
id: 1
title: update-project-constitution
stage: constitution
date: 2025-12-24
surface: agent
model: qwen3-coder-plus
feature: none
branch: master
user: Claude Code
command: sp.constitution
labels: ["constitution", "spec", "governance"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - none
---

## Prompt

```text
/sp.constitution

## Project Title
*AI/Spec-Driven Technical Book Creation with Docusaurus*

---

## Purpose & Vision

The purpose of this project is to demonstrate **AI-driven, specification-first book creation** by building a fully documented technical book using **Docusaurus**, authored and structured through **Spec-Kit Plus**, and assisted by **Claude Code**.

The book will be generated, structured, and refined using **verified documentation sources accessed through Context7 MCP**, ensuring accuracy, consistency, and traceability.

The final outcome is a **publicly deployed book on GitHub Pages**, showcasing modern AI-assisted documentation workflows.

---

## Core Principles

1. **Spec-First Development**
   - All book structure, chapters, workflows, and content must originate from explicit specifications:
     - `/sp.constitution`
     - `/sp.specify`
     - `/sp.plan`
     - `/sp.tasks`
   - No documentation content may exist without a corresponding specification.

2. **AI-Assisted, Human-Directed**
   - Claude Code is used to draft, refactor, summarize, and validate content.
   - Human intent, specifications, and acceptance criteria always override AI-generated output.

3. **Source-Grounded Content**
   - All technical explanations must be grounded in:
     - Official Docusaurus documentation
     - Verified references accessed via **Context7 MCP**
   - Hallucinated, speculative, or unverified information is strictly prohibited.

4. **Modular & Maintainable Documentation**
   - The book must follow Docusaurus best practices:
     - Clear sidebar-based navigation
     - Modular Markdown / MDX files
     - Logical chapter separation
     - Consistent formatting and tone

5. **Reproducibility & Transparency**
   - Any developer should be able to:
     - Clone the repository
     - Review the specs
     - Regenerate the book
     - Build and redeploy the site using the same workflow

---

## Scope

### Included

- Docusaurus project initialization and configuration
- Technical book content written in Markdown / MDX
- Sidebar and navigation configuration
- AI-assisted writing and editing via Claude Code
- Specifications authored and managed using Spec-Kit Plus
- Verified documentation references via Context7 MCP
- Deployment to **GitHub Pages**

### Excluded

- Backend services or APIs
- Authentication or user management
- Monetization or paywalls
- Non-Docusaurus documentation frameworks

---

## Architecture Overview

### Tooling Stack

- **Documentation Framework:** Docusaurus
- **Specification Framework:** Spec-Kit Plus
- **AI Assistant:** Claude Code
- **Knowledge Source:** Context7 MCP (Docusaurus documentation)
- **Hosting Platform:** GitHub Pages

---

## Book Structure Standards

- Each chapter must:
  - Correspond to a defined specification
  - Have a clear learning or narrative objective
  - Define acceptance criteria
- Chapters must be organized in a logical progression from foundational concepts to advanced topics.
- The minimum book structure includes:
```

## Response snapshot

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

## Outcome

- ✅ Impact: Created initial project constitution with 6 core principles reflecting AI/Spec-Driven Technical Book Creation with Docusaurus
- 🧪 Tests: none
- 📁 Files: Updated .specify/memory/constitution.md with project-specific principles and governance
- 🔁 Next prompts: /sp.specify to create feature specifications
- 🧠 Reflection: Constitution now properly reflects the project's focus on spec-driven book creation with Docusaurus

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Create initial feature specification