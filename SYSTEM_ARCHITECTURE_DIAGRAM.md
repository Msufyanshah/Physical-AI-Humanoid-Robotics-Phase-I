# Physical AI & Humanoid Robotics: Complete System Architecture

## Root Directory Structure
```
Physical-AI-Humanoid-Robotics-Phase-I/
├── .env
├── .gitignore
├── FINAL_PROJECT_STATUS.md
├── IMPLEMENTATION_STATUS.md
├── IMPLEMENTATION_SUMMARY.md
├── PROJECT_COMPLETION_SUMMARY.md
├── QWEN.md
├── README.md
├── start_system.bat
├── .git/...
├── .github/
│   ├── ISSUE_TEMPLATE/
│   └── workflows/
├── .qwen/
├── .specify/
├── backend/
│   ├── __pycache__/...
│   ├── requirements.txt
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── rag_endpoints.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── entities.py
│   │   │   └── database.py
│   │   ├── rag/
│   │   │   ├── __init__.py
│   │   │   ├── embedding_service.py
│   │   │   ├── chat_service.py
│   │   │   ├── retrieval_service.py
│   │   │   └── vector_store_service.py
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── chat_service.py
│   │       ├── embedding_service.py
│   │       ├── error_handling.py
│   │       ├── retrieval_service.py
│   │       ├── vector_store_service.py
│   │       └── perception_system.py
│   └── tests/
│       ├── __init__.py
│       └── test_main.py
├── frontend/
│   ├── .gitignore
│   ├── README.md
│   ├── package.json
│   ├── docusaurus.config.ts
│   ├── sidebars.ts
│   ├── tsconfig.json
│   ├── .docusaurus/
│   ├── build/
│   ├── docs/
│   │   ├── intro.md
│   │   ├── module1/
│   │   │   ├── ch1-intro-physical-ai.md
│   │   │   ├── ch2-ros2-architecture.md
│   │   │   ├── ch3-building-ros2-packages.md
│   │   │   ├── ch4-urdf-robot-description.md
│   │   │   └── exercise-set1.md
│   │   ├── module2/
│   │   │   ├── ch5-gazebo-simulation.md
│   │   │   ├── ch6-physics-collision-simulation.md
│   │   │   ├── ch7-sensor-simulation.md
│   │   │   ├── ch8-unity-integration.md
│   │   │   └── exercise-set2.md
│   │   ├── module3/
│   │   │   ├── ch9-isaac-sim-setup.md
│   │   │   ├── ch10-perception-navigation.md
│   │   │   ├── ch11-ai-manipulation-planning.md
│   │   │   └── exercise-set3.md
│   │   └── module4/
│   │       ├── ch12-voice-action-pipelines.md
│   │       ├── ch13-cognitive-planning.md
│   │       ├── ch14-capstone-autonomous-humanoid.md
│   │       ├── ch15-course-conclusion.md
│   │       ├── ch7-sensor-fusion.md
│   │       ├── ch7-vla-expert-agent.md
│   │       ├── ch8-triage-expert.md
│   │       └── exercise-set4.md
│   ├── src/
│   │   ├── css/
│   │   │   └── custom.css
│   │   └── pages/
│   │       └── index.tsx
│   └── static/
│       └── img/
│           ├── logo.svg
│           └── undraw_docusaurus_mountain.svg
├── history/
│   └── prompts/
│       ├── 1-book-rag-chatbot/
│       │   ├── 1-project-complete-full-implementation-of-humanoid-robotics-system.green.prompt.md
│       │   ├── 2-technical-validation-of-robotic-architecture.green.prompt.md
│       │   ├── 3-advanced-robotics-implementation.green.prompt.md
│       │   ├── 4-robotics-system-integration.green.prompt.md
│       │   └── 6-project-complete-full-implementation-of-humanoid-robotics-system.green.prompt.md
│       ├── constitution/
│       │   └── 1-system-architecture-implementation.constitution.prompt.md
│       └── general/
│           └── 1-project-initialization.general.prompt.md
├── scripts/
│   ├── validate_word_count.py
│   └── ...
├── specs/
│   └── 1-book-rag-chatbot/
│       ├── agent-context.md
│       ├── checklists/
│       │   └── requirements.md
│       ├── contracts/
│       │   └── openapi.yaml
│       ├── data-model.md
│       ├── plan.md
│       ├── quickstart.md
│       ├── prompts/
│       │   ├── v0/ [BEGINNER-SAFE PROMPTS]
│       │   │   ├── triage.md ................ > Triage Agent (v0) - Simple routing
│       │   │   ├── ros.md ................... > ROS 2 Expert Agent (v0) - Beginner-friendly
│       │   │   ├── gazebo.md ................ > Gazebo Expert Agent (v0) - Beginner-friendly
│       │   │   ├── isaac.md ................. > Isaac Expert Agent (v0) - Beginner-friendly
│       │   │   └── vla.md ................... > VLA Expert Agent (v0) - Beginner-friendly
│       │   └── v1/ [EXPERT AUTHENTIC PROMPTS]
│       │       ├── triage.md ................ > Triage Agent (v1) - Routing controller
│       │       ├── ros.md ................... > ROS 2 Expert Agent (v1) - Architecture expert
│       │       ├── gazebo.md ................ > Gazebo Expert Agent (v1) - Simulation expert
│       │       ├── isaac.md ................. > Isaac Expert Agent (v1) - AI learning expert
│       │       └── vla.md ................... > VLA Expert Agent (v1) - Vision-Language-Action expert
│       ├── research.md
│       ├── templates/
│       │   └── CHAPTER_TEMPLATE.md
│       └── tasks.md
└── PROJECT_COMPLETION_CERTIFICATE.md
```

## Detailed Prompt Structure (v0 vs v1)

### v0 - Beginner-Safe Prompts
```
specs/1-book-rag-chatbot/prompts/v0/
├── triage.md
│   ├── title: "Triage Agent (v0)"
│   ├── description: "Simple routing for humanoid robotics queries"
│   ├── role: "Simple routing assistant"
│   ├── scope: "Basic query routing"
│   └── boundaries: "Beginner-safe responses only"
├── ros.md
│   ├── title: "ROS 2 Expert Agent (v0)"
│   ├── description: "Beginner-friendly guide for ROS 2"
│   ├── role: "Helpful ROS 2 assistant"
│   ├── scope: "Basic concepts and architecture"
│   └── boundaries: "No complex code listings"
├── gazebo.md
│   ├── title: "Gazebo Expert Agent (v0)"
│   ├── description: "Beginner-friendly guide for Gazebo simulation"
│   ├── role: "Helpful Gazebo simulation assistant"
│   ├── scope: "Basic simulation concepts"
│   └── boundaries: "Simple explanations only"
├── isaac.md
│   ├── title: "Isaac Expert Agent (v0)"
│   ├── description: "Beginner-friendly guide for Isaac Sim and AI"
│   ├── role: "Helpful Isaac Sim and robotics AI assistant"
│   ├── scope: "Basic AI and simulation concepts"
│   └── boundaries: "No complex simulator details"
└── vla.md
    ├── title: "VLA Expert Agent (v0)"
    ├── description: "Beginner-friendly guide for Vision-Language-Action systems"
    ├── role: "Helpful VLA assistant"
    ├── scope: "Basic vision-language-action concepts"
    └── boundaries: "No complex ROS or simulator code"
```

### v1 - Expert Authenticated Prompts
```
specs/1-book-rag-chatbot/prompts/v1/
├── triage.md
│   ├── title: "Triage Agent (v1)"
│   ├── description: "Routes user queries to the correct humanoid robotics expert agent"
│   ├── role: "Routing controller"
│   ├── scope: "Precise query routing"
│   └── boundaries: "Expert-level routing logic"
├── ros.md
│   ├── title: "ROS 2 Expert Agent (v1)"
│   ├── description: "Architecture and usage expert for ROS 2 in humanoid robotics"
│   ├── role: "ROS 2 expert"
│   ├── scope: "Advanced architecture concepts"
│   └── boundaries: "No simulation physics details"
├── gazebo.md
│   ├── title: "Gazebo Expert Agent (v1)"
│   ├── description: "Conceptual expert for Gazebo-based humanoid simulation"
│   ├── role: "Gazebo simulation expert"
│   ├── scope: "Advanced simulation concepts"
│   └── boundaries: "No full SDF/URDF files unless asked"
├── isaac.md
│   ├── title: "Isaac Expert Agent (v1)"
│   ├── description: "AI and simulation learning expert for humanoid robotics"
│   ├── role: "Isaac Sim and robotics AI expert"
│   ├── scope: "Advanced AI training workflows"
│   └── boundaries: "No Gazebo physics tuning"
└── vla.md
    ├── title: "VLA Expert Agent (v1)"
    ├── description: "Vision–Language–Action cognition expert for humanoid robotics"
    ├── role: "VLA systems expert"
    ├── scope: "Advanced cognitive planning"
    └── boundaries: "No ROS nodes or simulation configs"
```

## Backend System Architecture
```
backend/
├── src/
│   ├── main.py .................. > FastAPI application entry point
│   ├── api/
│   │   └── rag_endpoints.py ..... > RAG system API endpoints
│   ├── models/
│   │   ├── entities.py .......... > Data models for the system
│   │   └── database.py .......... > Database configuration
│   ├── rag/
│   │   ├── embedding_service.py . > Text embedding service
│   │   ├── chat_service.py ...... > Chat response generation
│   │   ├── retrieval_service.py . > Content retrieval service
│   │   └── vector_store_service . > Qdrant vector database service
│   └── services/
│       ├── chat_service.py ...... > High-level chat interactions
│       ├── embedding_service.py . > High-level embedding operations
│       ├── error_handling.py .... > System error recovery
│       ├── perception_system.py . > Robot perception components
│       ├── retrieval_service.py . > High-level retrieval operations
│       └── vector_store_service . > High-level vector operations
```

## Frontend Documentation Structure
```
frontend/docs/
├── module1/ ..................... > The Robotic Nervous System (ROS 2)
│   ├── ch1-intro-physical-ai.md . > Introduction to Physical AI
│   ├── ch2-ros2-architecture.md . > ROS 2 Architecture
│   ├── ch3-building-ros2-packages.md > Building ROS 2 Packages
│   ├── ch4-urdf-robot-description.md > URDF Robot Description
│   └── exercise-set1.md ......... > Module 1 Exercises
├── module2/ ..................... > The Digital Twin (Gazebo & Unity)
│   ├── ch5-gazebo-simulation.md . > Gazebo Simulation
│   ├── ch6-physics-collision-simulation.md > Physics Simulation
│   ├── ch7-sensor-simulation.md . > Sensor Simulation
│   ├── ch8-unity-integration.md . > Unity Integration
│   └── exercise-set2.md ......... > Module 2 Exercises
├── module3/ ..................... > The AI-Robot Brain (NVIDIA Isaac)
│   ├── ch9-isaac-sim-setup.md ... > Isaac Sim Setup
│   ├── ch10-perception-navigation.md > Perception and Navigation
│   ├── ch11-ai-manipulation-planning.md > AI Manipulation Planning
│   └── exercise-set3.md ......... > Module 3 Exercises
└── module4/ ..................... > Vision-Language-Action (VLA)
    ├── ch12-voice-action-pipelines.md > Voice-to-Action Pipelines
    ├── ch13-cognitive-planning.md . > Cognitive Planning
    ├── ch14-capstone-autonomous-humanoid.md > Capstone Autonomous System
    ├── ch15-course-conclusion.md . > Course Conclusion
    ├── ch7-sensor-fusion.md ..... > Sensor Fusion (additional)
    ├── ch7-vla-expert-agent.md ... > VLA Expert Agent (additional)
    ├── ch8-triage-expert.md ..... > Triage Expert (additional)
    └── exercise-set4.md ......... > Module 4 Exercises
```

## Key Relationships & Dependencies

### v0-v1 Relationship
- v0: Beginner-safe, simplified prompts with clear boundaries
- v1: Expert-level, comprehensive prompts with advanced capabilities
- Both versions share the same routing and coordination logic
- v0 emphasizes safety and simplicity; v1 emphasizes power and precision

### System Integration Points
- RAG System: Connects v0/v1 expert agents to book content
- Triage System: Routes queries to appropriate expert agents
- ROS Integration: Enables real-world robot control
- Simulation: Provides testing and validation environment
- VLA System: Connects language to robot actions

### Architecture Pattern: Multi-Agent Coordination
```
[User Query] → [Triage Agent] → [Selected Expert Agent] 
                                ↓
                         [Specialized Response]
                                ↓
                         [Aggregated Response]
```