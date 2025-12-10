---
id: 1
title: Create Book Constitution
stage: constitution
date: 2025-12-10
surface: agent
model: Qwen
feature: ai-book-creation
branch: main
user: User
command: /sp.constitution
labels: ["constitution", "spec-driven", "docusaurus"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - null
---

## Prompt

```
$ARGUMENTS
```

Project: AI/Spec-Driven Technical Book Creation using Docusaurus

Core Principles

Technical Accuracy: All explanations, diagrams, and examples must be validated through reputable, verifiable sources (official documentation, academic papers, standards, or authoritative technical blogs).

Clarity for Learning: Writing must be accessible for learners with basic web development or AI background (beginner–intermediate).

Structured Progression: The book must progress from fundamentals → intermediate → practical implementation → deployment.

Consistency in Terminology: Maintain consistent technical vocabulary, definitions, and notation throughout the book.

Open-Source Transparency: Every code block, configuration, and setup step must be reproducible.

Spec-Driven Workflow: All content must be built, refined, and validated through Spec-Kit Plus workflows using clear specs, tasks, iterations, and reviews.

Tool-Integrated Writing: Use Claude Code (or other AI coding assistants) only for assistance—final content must meet human-level clarity and correctness standards.

Key Writing Standards

Factual claims: Must be supported with authoritative sources.

Citation format:

Web sources → inline reference with link

Academic or official documentation → APA or IEEE style

Documentation preference:

Priority to official documentation (e.g., Docusaurus, GitHub Pages, Node.js, React documentation).

Secondary: high-quality technical blogs, books, academic publications.

Code quality:

All code must be tested and runnable.

Provide version numbers (Node, npm, Docusaurus version, etc.).

Style:

Simple, clear, instructor-style explanation.

Use diagrams, bullet lists, tables where helpful.

Readability level:

Flesch-Kincaid grade 8–12 (beginner-friendly but not oversimplified).

Structural Requirements

The book must include:

Introduction to AI/Spec-Driven Development

Using Spec-Kit Plus for Book Writing

Working with Claude Code/ Qwen/ Gemini 

Introduction to Docusaurus

Step-by-Step Guide: Setting Up the Book

Deploying to GitHub Pages

Best Practices & Troubleshooting

Glossary, Resources & Further Reading

Each chapter must:

Start with learning objectives

End with a summary and checklist

Include reproducible code blocks

Provide at least one hands-on exercise or example

Constraints

Book word count: 8,000–15,000 words total

Book format:

Docusaurus site with Markdown files

Fully deployable on GitHub Pages

Media constraints:

Images/SVGs must be open-source or AI-generated with attribution

Plagiarism:

0% tolerance (rephrasing required when using external ideas)

Versioning:

Maintain version control using git

Document each major version change

Success Criteria

Book builds successfully on local and GitHub Pages.

All chapters follow spec-driven workflow (task → content → review → refine).

No factual errors, all technical instructions work when tested.

Each concept is explained with clarity, examples, and illustrations.

All sources are cited, and no plagiarized text exists.

Code blocks run correctly in a fresh environment.

The book is helpful, educational, and easy to navigate.

## Response snapshot

The constitution for the AI/Spec-Driven Technical Book Creation project has been successfully created at `.specify/memory/constitution.md`. The new constitution includes all the specified principles and requirements:

- Technical Accuracy
- Clarity for Learning  
- Structured Progression
- Consistency in Terminology
- Open-Source Transparency
- Spec-Driven Workflow
- Tool-Integrated Writing

The document also details writing standards, structural requirements, constraints, success criteria, and governance procedures. A Sync Impact Report was included at the top of the file, and the version was set to 1.0.0 with today's date as both the ratification and last amended date.

## Outcome

- ✅ Impact: Created comprehensive project constitution for AI/Spec-Driven Technical Book Creation
- 🧪 Tests: N/A 
- 📁 Files: Updated .specify/memory/constitution.md with all required principles
- 🔁 Next prompts: Continue with spec, plan, and task creation for the book project
- 🧠 Reflection: All core principles and requirements from user input were successfully incorporated into the constitution file

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): Standard constitution creation
- Next experiment (smallest change to try): Begin creating book specifications based on constitution