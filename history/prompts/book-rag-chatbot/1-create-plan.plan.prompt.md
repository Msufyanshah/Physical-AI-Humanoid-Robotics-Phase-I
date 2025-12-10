---
id: 1
title: Create Plan
stage: plan
date: 2025-12-10
surface: agent
model: Qwen
feature: book-rag-chatbot
branch: 1-book-rag-chatbot
user: User
command: /sp.plan
labels: ["plan", "book", "rag", "chatbot", "architecture"]
links:
  spec: specs/1-book-rag-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/1-book-rag-chatbot/plan.md
 - specs/1-book-rag-chatbot/research.md
 - specs/1-book-rag-chatbot/data-model.md
 - specs/1-book-rag-chatbot/contracts/openapi.yaml
 - specs/1-book-rag-chatbot/quickstart.md
 - specs/1-book-rag-chatbot/agent-context.md
tests:
 - null
---

## Prompt

```
$ARGUMENTS
```

Goal:
Create a full technical book on “Physical AI & Humanoid Robotics” using Docusaurus, driven by Spec-Kit Plus workflows, and integrate a fully functional RAG chatbot using OpenAI Agents/ChatKit, FastAPI, Neon Postgres, and Qdrant Cloud.

Outputs:
- Architecture sketch
- Section & chapter structure
- Research approach
- Quality validation plan
- Decision documentation
- Testing/validation strategy

------------------------------------
ARCHITECTURE SKETCH (High-Level)
------------------------------------

System Architecture (Book + RAG):

1. **Book Layer (Frontend: Docusaurus)**
   - Markdown-based chapters for 4 Modules
   - React components for:
     • “Ask the Book Chatbot” widget
     • Content personalization button
     • Urdu translation trigger
   - GitHub Pages deployment pipeline
   - Client-side selection → send selected text to backend

2. **RAG Backend Layer (FastAPI)**
   - Endpoints:
     /ask-general
     /ask-selected
     /embed-chunk
     /auth (optional BetterAuth)
     /personalize-content
     /translate-urdu
   - Runs inference using OpenAI Agents/ChatKit SDK
   - Retrieves embeddings from Qdrant vectordb
   - Stores user profile in Neon Postgres

3. **Data Layer**
   - **Qdrant Cloud Free Tier** → vector store for embeddings
   - **Neon Postgres** → structured DB storing:
     • user accounts
     • user backgrounds
     • personalization choices
     • chatbot logs (optional)

4. **Spec-Kit Plus Workflow Layer**
   - /sp.specify → Book specification (already created)
   - /sp.plan → Architecture + outline (this file)
   - /sp.task → Generation tasks for each chapter
   - /sp.review → Human/AI review cycles
   - /sp.iterate → Refinement until quality threshold met

5. **Reusable Intelligence (Bonus Feature)**
   - Claude Code Subagents:
     • “ROS Expert”
     • “Gazebo/Unity Simulation Expert”
     • “Isaac Sim Expert”
     • “VLA/Voice-to-Action Expert”
   - Agent Skills:
     • file-search
     • code-generation
     • ROS troubleshooting helper
     • diagram generator

------------------------------------
SECTION STRUCTURE (Book Outline)
------------------------------------

Book Title:  
**“Physical AI & Humanoid Robotics: From Sensors to Embodied Intelligence”**

Total: 4 Modules → 12–16 chapters

Module 1: The Robotic Nervous System (ROS 2)
- Ch1: Introduction to Physical AI & Embodied Intelligence
- Ch2: ROS 2 Architecture, Nodes, Topics, Services, Actions
- Ch3: Building ROS 2 Packages in Python
- Ch4: URDF & Robot Description for Humanoids
- Exercise Set #1

Module 2: The Digital Twin (Gazebo & Unity)
- Ch5: Gazebo Simulation Fundamentals
- Ch6: Physics, Gravity, and Collision Simulation
- Ch7: Sensor Simulation (LiDAR, IMU, Depth Cameras)
- Ch8: Unity Integration for Robot Visualization
- Exercise Set #2

Module 3: The AI-Robot Brain (NVIDIA Isaac)
- Ch9: Isaac Sim Setup & Synthetic Data Generation
- Ch10: Perception: VSLAM, Navigation, Object Detection
- Ch11: AI-Powered Manipulation & Bipedal Planning
- Exercise Set #3

Module 4: Vision-Language-Action (VLA)
- Ch12: Voice-to-Action Pipelines (Whisper + LLMs)
- Ch13: Cognitive Planning: Natural Language → ROS Actions
- Ch14: Capstone: Autonomous Humanoid Pipeline
- Exercise Set #4

Appendices:
- Glossary of Robotics Terms
- ROS 2 Quick Commands
- Hardware Requirements
- RAG Chatbot API Reference
- Troubleshooting Guide

------------------------------------
RESEARCH APPROACH
------------------------------------

Use “research-concurrent writing”:
- Perform micro-research during each section development.
- For technical content:
  • ROS 2 → Official docs, REP standards  
  • Gazebo → Simulation docs, sensor references  
  • Isaac → NVIDIA official SDK + RL papers  
  • VLA → OpenAI, Stanford papers on language-conditioned robotics
- Use APA citation style.
- Prefer:
  • IEEE, ACM, Springer robotics papers  
  • Official documentation  
  • High-authority sources (NASA, NVIDIA, ROS.org)

Sources must be:
- Within 10 years (for academic claims)
- Clear, authoritative, reproducible

------------------------------------
QUALITY VALIDATION
------------------------------------

1. Content Quality
   - Technical accuracy validated against official documentation.
   - Each chapter passes:
     • Accuracy check  
     • Completeness check  
     • Reproducibility check  
     • Clarity test (FK8–12 readability)  
     • Example code execution test  

2. RAG Functionality Validation
   - Chatbot answers must be:
     • grounded only in book text  
     • correct  
     • reproducible  
     • cite the matched paragraph  

3. Documentation Quality
   - Each chapter has:
     • Learning objectives  
     • Summary checklist  
     • Step-by-step examples  
     • Exercises + solutions  

------------------------------------
DECISIONS NEEDING DOCUMENTATION
------------------------------------

1. **Choice: RAG stack**
   - Options:
     A) LangChain + custom backend  
     B) OpenAI ChatKit SDK + FastAPI (Chosen)  
     C) Direct OpenAI API no vectordb  
   - Reason: Hackathon requires OpenAI Agents/ChatKit.

2. **Vector DB Selection**
   - Options: Pinecone, Weaviate, Qdrant  
   - Chosen: Qdrant Cloud Free Tier (required by hackathon)

3. **Auth System**
   - Using BetterAuth for signup/signin  
   - Optional bonus, but supports personalization

4. **Frontend**
   - Docusaurus v3 because:
     • React-based  
     • easy GitHub Pages deployment  
     • supports translation plugins  
     • can embed chatbot widget  

5. **Reusable Intelligence Strategy**
   - Subagents created per domain (ROS, Gazebo, Isaac, VLA)
   - Each subagent handles its own chapter generation

------------------------------------
TESTING STRATEGY
------------------------------------

Testing = validation against success criteria.

✔ **Book Validation**
- Build locally without errors
- Deployed GitHub Pages preview loads all sections
- All links, images, code blocks render
- Exercises validated by running commands in sample environment
- No hallucinated APIs or code

✔ **RAG Chatbot Validation**
- Run test suite of 50 questions:
  • 25 general questions  
  • 25 “selected text only” questions  
- Confirm chatbot never uses information outside the book
- Evaluate:
  • grounding accuracy  
  • citation correctness  
  • hallucination rate < 2%  

✔ **Personalization (Bonus)**
- Test content changes according to user profile (hardware level, OS, experience)
- Ensure Urdu translation loads properly via button

✔ **Performance Tests**
- Embedding latency < 500ms
- Chat response < 2 seconds (cold start excluded)

------------------------------------
PHASES
------------------------------------

PHASE 1 — Research  
PHASE 2 — Foundation (chapter scaffolding + code outlines)  
PHASE 3 — Analysis (connecting modules, diagrams, examples)  
PHASE 4 — Synthesis (final writing, editing, citations, RAG build)  
PHASE 5 — Deployment (Docusaurus + RAG backend + testing)

## Response snapshot

Successfully completed the implementation planning for the Physical AI & Humanoid Robotics technical book with integrated RAG chatbot. The following artifacts were created:

1. Implementation Plan (plan.md): Detailed technical context, architecture, and structure
2. Research Document (research.md): Addresses all technology decisions and research approach
3. Data Model (data-model.md): Defines all entities, attributes, relationships and validation rules
4. API Contracts (contracts/openapi.yaml): Complete OpenAPI specification for backend services
5. Quickstart Guide (quickstart.md): Comprehensive guide to set up and run the system
6. Agent Context (agent-context.md): Technologies and concepts added to agent knowledge

The plan covers all required components including:
- Frontend Docusaurus book with 4 modules (ROS 2, Gazebo, Isaac Sim, VLA)
- Backend RAG services with OpenAI ChatKit integration
- Database layer with Neon Postgres and Qdrant vector store
- Authentication with BetterAuth
- Personalization and translation features
- Comprehensive testing and validation strategy

All constitution principles have been addressed in the design, and the architecture follows the required technology stack.

## Outcome

- ✅ Impact: Complete implementation plan with all required design artifacts
- 🧪 Tests: N/A
- 📁 Files: Created all required planning artifacts in specs/1-book-rag-chatbot/
- 🔁 Next prompts: Ready for task generation with `/sp.tasks`
- 🧠 Reflection: Plan addresses all requirements from the original request with appropriate technical detail

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): Standard planning workflow
- Next experiment (smallest change to try): Generate tasks with `/sp.tasks`