# Implementation Plan: AI/Spec-Driven Technical Book + Integrated RAG Chatbot

**Branch**: `1-book-rag-chatbot` | **Date**: 2025-12-10 | **Spec**: [link to spec]
**Input**: Feature specification from `/specs/1-book-rag-chatbot/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Create a comprehensive technical book on Physical AI & Humanoid Robotics with 4 modules covering ROS 2, Gazebo, Isaac Sim, and VLA systems. The book will be built using Docusaurus and deployed on GitHub Pages, with an integrated RAG chatbot using OpenAI Agents/ChatKit, FastAPI, Neon Postgres, and Qdrant Cloud. The content will be generated using Spec-Kit Plus workflows with a focus on technical accuracy, reproducible examples, and structured learning progression.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.11, JavaScript/TypeScript for Docusaurus, Node.js 18+
**Primary Dependencies**: Docusaurus v3, FastAPI, OpenAI Agents/ChatKit SDK, Neon Postgres, Qdrant Cloud
**Storage**: PostgreSQL for user data (Neon), Vector DB for embeddings (Qdrant), Markdown files for content
**Testing**: pytest for backend, Jest for frontend components, manual validation for book content
**Target Platform**: GitHub Pages (frontend), Cloud deployment (backend API)
**Project Type**: Web application with static documentation site
**Performance Goals**: <2s chat response time, 95% uptime, 100 concurrent users support
**Constraints**: Book word count 8,000–15,000 words, deployment on GitHub Pages, images open-source or AI-generated
**Scale/Scope**: 4 modules, 12–16 chapters, 4-module book with exercises and code examples

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Based on the constitution file:
- Technical Accuracy: All content must be validated against authoritative sources
- Clarity for Learning: Content must be accessible to beginners-intermediate learners
- Structured Progression: Content must follow logical flow from fundamentals to advanced topics
- Consistency in Terminology: Maintain consistent technical vocabulary throughout
- Open-Source Transparency: All code examples must be reproducible in clean environment
- Spec-Driven Workflow: Use Spec-Kit Plus workflow for systematic development
- Tool-Integrated Writing: Use AI tools as assistance while maintaining human-level standards

## Project Structure

### Documentation (this feature)

```text
specs/1-book-rag-chatbot/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# Option 1: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   ├── api/
│   └── main.py
└── tests/

frontend/  # Docusaurus book
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
├── docs/    # Book content
│   ├── module1/
│   ├── module2/
│   ├── module3/
│   └── module4/
├── static/
└── docusaurus.config.js

# RAG Integration Components
├── backend/
│   ├── rag/
│   │   ├── embedding_service.py
│   │   ├── chat_service.py
│   │   └── retrieval_service.py
│   └── auth/
│       ├── user_service.py
│       └── better_auth_integration.py
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── ChatWidget/
    │   │   ├── Personalization/
    │   │   └── Translation/
    │   └── services/
    │       ├── chatAPI.js
    │       └── authService.js
    └── docs/
        ├── module1/
        ├── module2/
        ├── module3/
        └── module4/
```

**Structure Decision**: Single project with backend API and frontend Docusaurus site. The backend handles RAG functionality, authentication, and personalization, while the frontend serves the book content and provides the UI components for chatbot interaction, personalization, and translation.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |