---
title: 'Prompt Triage System for Humanoid Robotics'
description: 'System for routing queries to appropriate specialized agents'
---

# Prompt Triage System for Humanoid Robotics

## Overview

The prompt triage system categorizes incoming queries and routes them to the most appropriate specialized agent based on the content and intent of the user's request.

## Triage Categories

### 1. ROS Expert Agent
**Keywords**: ros, ros2, nodes, topics, services, actions, publishers, subscribers, packages, rclpy, roslaunch, roscore, colcon, ament, messages, parameters, tf, transforms

**Queries to route**: 
- "How do I create a ROS 2 publisher?"
- "Explain the difference between ROS 1 and ROS 2"
- "How do I use services in ROS 2?"
- "What is the lifecycle of a ROS node?"

### 2. Gazebo Expert Agent
**Keywords**: gazebo, simulation, physics, world, sdf, urdf, sensors, plugins, models, collision, visual, dynamics, joints, contacts

**Queries to route**:
- "How do I configure physics parameters in Gazebo?"
- "Create a custom world model for Gazebo"
- "Add sensors to my robot model in simulation"
- "Configure collision detection for my robot"

### 3. Isaac Expert Agent
**Keywords**: isaac, nvidia, sim, ai, perception, navigation, vision, slam, vlam, synthetic, data, training, learning, deep learning

**Queries to route**:
- "How do I set up Isaac Sim for robot learning?"
- "Configure perception systems in Isaac Sim"
- "Generate synthetic training data with Isaac Sim"
- "Implement vision-based navigation in Isaac"

### 4. VLA Expert Agent
**Keywords**: vision, language, action, vla, whisper, audio, speech, nlp, multimodal, llm, ai, cognitive, planning, perception

**Queries to route**:
- "How do I implement voice-to-action pipelines?"
- "Create cognitive planning for natural language"
- "Connect LLM with ROS actions"
- "Implement multimodal perception"

## Triage Algorithm

### Primary Classification
1. Extract keywords from the query
2. Match against category-specific keywords
3. Calculate confidence scores for each match
4. Route to agent with highest confidence score

### Secondary Classification (for mixed queries)
If a query contains keywords from multiple categories, use secondary classification:
1. Determine primary intent
2. Route to most relevant agent
3. Include context for other relevant agents

## Implementation

### Keyword-Based Classification

```python
import re
from typing import List, Dict, Optional

class PromptTriage:
    """
    Classifies prompts and routes them to appropriate specialized agents
    """
    
    def __init__(self):
        self.classifiers = {
            'ros': {
                'keywords': [
                    'ros', 'ros2', 'node', 'topic', 'service', 'action', 'publisher', 
                    'subscriber', 'package', 'rclpy', 'rclcpp', 'launch', 'ament', 
                    'cmake', 'messages', 'parameters', 'tf', 'transforms', 'colcon',
                    'workspace', 'rosbag', 'rviz', 'urdf'
                ],
                'regex': r'.*\b(ros\s*2?|node|topic|service|action|publisher|subscriber|package)\b.*',
                'weight': 1.0
            },
            'gazebo': {
                'keywords': [
                    'gazebo', 'simulation', 'physics', 'world', 'sdf', 'urdf',
                    'sensor', 'plugin', 'model', 'collision', 'visual', 'dynamics',
                    'ode', 'bullet', 'simbody', 'rendering', 'environment', 'actors',
                    'ground', 'light', 'camera', 'lidar', 'imu'
                ],
                'regex': r'.*\b(gazebo|simulation|physics|world|sdf|collision)\b.*',
                'weight': 1.0
            },
            'isaac': {
                'keywords': [
                    'isaac', 'nvidia', 'sim', 'perception', 'navigation', 'vision',
                    'slam', 'vlam', 'synthetic', 'data', 'training', 'learning',
                    'deep learning', 'ai', 'reinforcement', 'rl', 'computer vision',
                    'simulation', 'robotics', 'framework', 'simulation environment'
                ],
                'regex': r'.*\b(isaac|nvidia|sim|perception|navigation|vision)\b.*',
                'weight': 1.0
            },
            'vla': {
                'keywords': [
                    'vision', 'language', 'action', 'vla', 'whisper', 'audio',
                    'speech', 'nlp', 'multimodal', 'llm', 'ai', 'cognitive',
                    'planning', 'perception', 'natural language', 'understanding',
                    'gpt', 'chatgpt', 'openai', 'translation', 'reasoning'
                ],
                'regex': r'.*\b(vision|language|action|vla|whisper|speech|nlp)\b.*',
                'weight': 1.0
            }
        }
    
    def classify_prompt(self, prompt: str) -> Optional[str]:
        """
        Classify a prompt and return the expert agent category
        """
        scores = {agent: 0 for agent in self.classifiers.keys()}
        
        prompt_lower = prompt.lower()
        
        # Calculate keyword match scores
        for agent, config in self.classifiers.items():
            for keyword in config['keywords']:
                if keyword in prompt_lower:
                    scores[agent] += 1
        
        # Calculate regex match scores
        for agent, config in self.classifiers.items():
            if re.match(config['regex'], prompt_lower, re.IGNORECASE):
                scores[agent] += config['weight']
        
        # Find highest scoring agent
        best_agent = max(scores, key=scores.get)
        best_score = scores[best_agent]
        
        # Check if score is significant enough to make a classification
        if best_score > 0:
            return best_agent
        else:
            return 'general'  # No clear classification, route to general
    
    def route_query(self, query: str) -> Dict[str, str]:
        """
        Route a query to the appropriate agent with confidence score
        """
        agent = self.classify_prompt(query)
        
        return {
            'agent': agent,
            'query': query,
            'confidence': 'high' if agent != 'general' else 'low'
        }

# Example usage
if __name__ == "__main__":
    triage = PromptTriage()
    
    test_queries = [
        "How do I create a ROS 2 publisher?",
        "How do I configure physics in Gazebo?",
        "How do I set up Isaac Sim for perception?",
        "How do I implement voice-to-action using Whisper?"
    ]
    
    for query in test_queries:
        result = triage.route_query(query)
        print(f"Query: '{query}' -> Agent: {result['agent']}, Confidence: {result['confidence']}")
```

### Fallback Mechanisms

If triage fails to identify a clear category:
1. Route to general expert agent
2. Implement knowledge base search
3. Return list of potentially relevant agents
4. Ask user for clarification

## Integration with Pipeline

The triage system should be the first step in the query processing pipeline:
1. Query received
2. Prompt triage determines agent
3. Query routed to appropriate specialized agent
4. Response aggregated and returned to user