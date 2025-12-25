# Data Model: Syllabus-Driven Technical Book

## Entities

### Syllabus Topic
- **Definition**: Represents a specific subject or concept from the original syllabus that must be covered in the book
- **Attributes**:
  - id: Unique identifier for the topic
  - title: Display name of the topic
  - description: Brief description of the topic
  - learningObjectives: List of learning objectives for this topic
  - prerequisites: List of prerequisite topics (if any)
  - category: Category or grouping for the topic
  - status: Status of content generation (pending, in-progress, completed, validated)

### Book Chapter
- **Definition**: A structured piece of content in the Docusaurus book that corresponds to one or more syllabus topics
- **Attributes**:
  - id: Unique identifier for the chapter
  - title: Chapter title
  - content: The actual content in Markdown/MDX format
  - syllabusTopicId: Reference to the corresponding syllabus topic
  - position: Order position in the book
  - navigationPath: Path in the navigation structure
  - metadata: Additional metadata (author, creation date, last modified, etc.)
  - validationStatus: Status of content validation

### Navigation Structure
- **Definition**: The organizational hierarchy that defines how chapters are presented to readers
- **Attributes**:
  - id: Unique identifier for the navigation item
  - label: Display label for navigation
  - type: Type of navigation item (category, link, doc)
  - link: Link properties if it's a link type
  - items: List of child navigation items
  - position: Order in the navigation
  - parentId: Reference to parent navigation item (null for root items)

### Content Compliance
- **Definition**: The measure of how well generated content aligns with syllabus requirements
- **Attributes**:
  - id: Unique identifier for the compliance record
  - syllabusTopicId: Reference to the syllabus topic
  - chapterId: Reference to the book chapter
  - complianceScore: Numerical score representing compliance level (0-100)
  - validationReport: Detailed report of validation findings
  - verifiedSources: List of verified documentation sources used
  - complianceStatus: Overall status (pass, fail, partial)
  - validationDate: Date when validation was performed

## Relationships

### Syllabus Topic → Book Chapter
- One-to-One relationship (each syllabus topic maps to exactly one book chapter)
- Enforced by functional requirement FR-002

### Book Chapter → Navigation Structure
- Many-to-One relationship (multiple chapters can belong to the same navigation category)
- Each chapter has exactly one navigation path

### Syllabus Topic → Content Compliance
- One-to-One relationship (each syllabus topic has one compliance record per generated chapter)

## Validation Rules

### From Functional Requirements
- FR-001: Each syllabus topic must map to at least one chapter
- FR-002: Each chapter must map back to exactly one syllabus topic
- FR-003: Chapter content must follow proper Markdown/MDX format
- FR-005: Content must be verifiable against official documentation sources
- FR-006: Consistent formatting must be maintained across all chapters
- FR-008: Proper versioning information must be maintained

### Content Validation
- All content must pass Docusaurus build validation
- Content must reference verified documentation sources (Context7 MCP)
- Content must align with learning objectives of the corresponding syllabus topic
- Content must maintain consistent tone and formatting as specified in requirements