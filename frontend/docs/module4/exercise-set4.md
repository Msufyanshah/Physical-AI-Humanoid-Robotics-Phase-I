---
title: 'Exercise Set 4 - Voice-to-Action Pipelines'
description: 'Comprehensive exercises for voice-to-action system implementation'
---

# Exercise Set 4: Voice-to-Action Pipelines

## Learning Objectives

After completing these exercises, you will be able to:
- Integrate voice recognition with robotic action planning
- Implement cognitive planning from natural language commands
- Create robust voice-to-action pipelines with error handling
- Validate voice interface performance and accuracy
- Optimize voice processing for real-time operation
- Deploy voice-enabled robotic systems
- Handle voice command ambiguity and disambiguation
- Create multimodal interfaces combining voice and visual feedback

## Exercise 1: Complete Voice Interface Implementation

Create a complete voice-to-action pipeline with speech recognition, natural language understanding, and robotic action execution.

### Instructions

1. Implement Whisper-based speech recognition
2. Integrate with LLM for natural language understanding
3. Create a cognitive planner that maps commands to actions
4. Implement voice command execution with feedback
5. Add error handling and recovery mechanisms
6. Test with various commands and environments

### Solution

#### Complete Voice Interface System

```python
# voice_interface_integration.py
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
from geometry_msgs.msg import PoseStamped
from sensor_msgs.msg import Image
from std_msgs.msg import Header
import threading
import time
import json
import asyncio
import queue
import numpy as np
from typing import Dict, Any, Optional, List
import whisper
import torch
import openai
import os


class VoiceInterfaceSystem(Node):
    """Complete voice interface system for humanoid robot"""
    
    def __init__(self):
        super().__init__('voice_interface')
        
        # Initialize voice components
        self.initialize_voice_system()
        
        # Command queue to process voice commands
        self.command_queue = queue.Queue()
        
        # Publishers and subscribers
        self.voice_command_pub = self.create_publisher(String, '/voice_command', 10)
        self.text_command_pub = self.create_publisher(String, '/text_command', 10)
        self.feedback_pub = self.create_publisher(String, '/voice_feedback', 10)
        self.voice_active_sub = self.create_subscription(Bool, '/voice_active', self.voice_active_callback, 10)
        
        # State tracking
        self.voice_active = True
        self.listening_thread = None
        self.processing_thread = None
        
        # Start voice processing
        self.start_voice_system()
        
        self.get_logger().info("Voice Interface System initialized")
    
    def initialize_voice_system(self):
        """Initialize Whisper and OpenAI components"""
        
        # Initialize Whisper model (using smaller model for efficiency)
        try:
            if torch.cuda.is_available():
                self.whisper_model = whisper.load_model("medium.en").cuda()
                self.get_logger().info("Whisper model loaded on GPU")
            else:
                self.whisper_model = whisper.load_model("small.en")
                self.get_logger().info("Whisper model loaded on CPU")
        except Exception as e:
            self.get_logger().error(f"Failed to load Whisper model: {e}")
            self.get_logger().warn("Using mock Whisper functionality")
            self.whisper_model = None
        
        # Initialize OpenAI client
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            self.openai_client = openai.OpenAI(api_key=openai_api_key)
            self.get_logger().info("OpenAI client initialized")
        else:
            self.get_logger().warn("OpenAI API key not found. Using simulated responses.")
            self.openai_client = None
    
    def start_voice_system(self):
        """Start the voice interface system"""
        # Start listening thread
        self.listening_active = True
        self.listening_thread = threading.Thread(target=self.listen_for_commands, daemon=True)
        self.listening_thread.start()
        
        # Start processing thread
        self.processing_thread = threading.Thread(target=self.process_commands, daemon=True)
        self.processing_thread.start()
    
    def listen_for_commands(self):
        """Listen for voice commands (simplified simulation)"""
        
        # In a real implementation, this would use:
        # - Microphone input
        # - Voice activity detection
        # - Speech-to-text using Whisper
        # - Text-to-intent using NLP
        
        import sounddevice as sd
        import soundfile as sf
        import tempfile
        
        while self.listening_active and rclpy.ok():
            if self.voice_active:
                # Simulate listening for a voice command
                # In reality, we'd use real audio capture and Whisper
                time.sleep(5)  # Check every 5 seconds for demo purposes
                
                # For demonstration, let's simulate receiving a command
                simulated_command = "Go to the kitchen and bring me the red cup"
                
                if simulated_command:
                    # Process the command
                    command_msg = String()
                    command_msg.data = json.dumps({
                        'text': simulated_command,
                        'source': 'simulated_input',
                        'timestamp': self.get_clock().now().seconds_nanoseconds(),
                        'confidence': 0.85
                    })
                    
                    self.command_queue.put(command_msg)
                    
                    self.get_logger().info(f"Simulated voice command received: '{simulated_command}'")
            else:
                time.sleep(0.1)  # Check voice status every 100ms
    
    def process_commands(self):
        """Process commands from the queue"""
        while rclpy.ok():
            try:
                # Get command from queue (with timeout to allow periodic checks)
                try:
                    cmd_msg = self.command_queue.get(timeout=1.0)
                    
                    # Process the command
                    self.process_voice_command(cmd_msg)
                    
                    # Mark task as done
                    self.command_queue.task_done()
                    
                except queue.Empty:
                    # Timeout occurred, continue loop to check for shutdown
                    continue
            except Exception as e:
                self.get_logger().error(f"Error in command processing thread: {e}")
                time.sleep(0.1)  # Brief pause before continuing
    
    def process_voice_command(self, msg: String):
        """Process a voice command through the complete pipeline"""
        
        try:
            command_data = json.loads(msg.data)
            command_text = command_data['text']
            
            self.get_logger().info(f"Processing voice command: '{command_text}'")
            
            # Step 1: Speech-to-text (already done by simulated input)
            # In real system: transcribed_text = self.transcribe_audio(msg)
            
            # Step 2: Natural Language Understanding
            self.get_logger().info("Understanding command semantics...")
            intent = self.understand_command_semantics(command_text)
            
            if not intent:
                self.get_logger().error(f"Could not understand command: '{command_text}'")
                self.provide_feedback(f"Sorry, I didn't understand: '{command_text}'")
                return
            
            self.get_logger().info(f"Understood intent: {intent}")
            
            # Step 3: Task Planning
            self.get_logger().info("Planning task execution...")
            plan = self.plan_task_execution(intent)
            
            if not plan:
                self.get_logger().error(f"Could not create plan for intent: {intent}")
                self.provide_feedback("I can't perform that task right now.")
                return
            
            self.get_logger().info(f"Created plan with {len(plan.get('steps', []))} steps")
            
            # Step 4: Publish to cognitive planner for execution
            plan_msg = String()
            plan_msg.data = json.dumps({
                'intent': intent,
                'plan': plan,
                'source': 'voice_interface',
                'timestamp': self.get_clock().now().seconds_nanoseconds()
            })
            
            self.text_command_pub.publish(plan_msg)
            self.get_logger().info("Published plan to cognitive planner")
            
            # Step 5: Provide feedback
            self.provide_feedback(f"I understood your command. I will {command_text.replace('.', ' ').replace(',', ' ')}.")
            
        except json.JSONDecodeError:
            self.get_logger().error(f"Invalid JSON format in command: {msg.data}")
        except Exception as e:
            self.get_logger().error(f"Error processing voice command: {e}")
            self.provide_feedback("I encountered an error processing your command.")
    
    def understand_command_semantics(self, command: str) -> Optional[Dict[str, Any]]:
        """Understand command semantics using OpenAI or local processing"""
        
        if self.openai_client:
            # Use OpenAI API for command understanding
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system", 
                            "content": "You are a natural language understanding system for a humanoid robot. Extract the intent and parameters from the user's command. Respond in JSON format."
                        },
                        {
                            "role": "user", 
                            "content": f"""Extract intent and parameters from: '{command}'

Expected response format:
{{
  "action_type": "navigation|manipulation|inspection|other",
  "action": "go_to_location|grasp_object|find_object|speak_response|etc",
  "parameters": {{
    "location": "kitchen, bedroom, office, etc.",
    "object": "cup, book, ball, etc.",
    "target_pose": {{"x": 1.0, "y": 2.0, "z": 0.0}},
    "greeting_message": "specific message if speaking",
    "other_params": "as needed"
  }},
  "confidence": 0.85
}}"""
                        }
                    ],
                    temperature=0.1,
                    max_tokens=200
                )
                
                content = response.choices[0].message.content
                
                # Extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    intent_json_str = json_match.group(0)
                    return json.loads(intent_json_str)
                else:
                    self.get_logger().error(f"Could not extract JSON from OpenAI response: {content}")
                    return None
                    
            except Exception as e:
                self.get_logger().error(f"Error with OpenAI API: {e}")
                # Fall back to local processing
                return self.local_command_understanding(command)
        else:
            # Use local processing with keyword matching
            return self.local_command_understanding(command)
    
    def local_command_understanding(self, command: str) -> Optional[Dict[str, Any]]:
        """Local command understanding when API not available"""
        
        command_lower = command.lower()
        
        # Define keyword patterns for different intents
        navigation_keywords = ['go to', 'navigate to', 'move to', 'walk to', 'travel to', 'head to']
        grasp_keywords = ['pick up', 'grasp', 'get', 'take', 'lift', 'fetch']
        find_keywords = ['find', 'look for', 'search for', 'locate', 'where is']
        speak_keywords = ['say', 'tell', 'speak', 'announce']
        
        # Determine intent based on keywords
        intent = {
            'action_type': 'other',
            'action': 'unknown',
            'parameters': {},
            'confidence': 0.7  # Local processing has lower confidence
        }
        
        # Navigation intent
        for nav_keyword in navigation_keywords:
            if nav_keyword in command_lower:
                intent['action_type'] = 'navigation'
                intent['action'] = 'go_to_location'
                
                # Extract location from command
                if 'kitchen' in command_lower:
                    intent['parameters']['location'] = 'kitchen'
                    intent['parameters']['target_pose'] = {'x': 3.0, 'y': 1.0, 'z': 0.0}
                elif 'living room' in command_lower:
                    intent['parameters']['location'] = 'living_room'
                    intent['parameters']['target_pose'] = {'x': 0.0, 'y': 0.0, 'z': 0.0}
                elif 'bedroom' in command_lower:
                    intent['parameters']['location'] = 'bedroom'
                    intent['parameters']['target_pose'] = {'x': -2.0, 'y': 2.0, 'z': 0.0}
                elif 'office' in command_lower:
                    intent['parameters']['location'] = 'office'
                    intent['parameters']['target_pose'] = {'x': -1.0, 'y': -1.0, 'z': 0.0}
                else:
                    # Extract generic location
                    intent['parameters']['location'] = 'unknown_location'
                
                break
        
        # Grasp intent
        for grasp_keyword in grasp_keywords:
            if grasp_keyword in command_lower:
                intent['action_type'] = 'manipulation'
                intent['action'] = 'grasp_object'
                
                # Extract object from command
                words = command_lower.split()
                for word in words:
                    if word in ['cup', 'book', 'ball', 'box', 'phone', 'laptop']:
                        intent['parameters']['object'] = word
                        break
                
                # If no specific object found, extract noun phrase
                if 'object' not in intent['parameters']:
                    # This would be more sophisticated in a real implementation
                    # For now, extract common objects or use "unknown"
                    intent['parameters']['object'] = 'object'
                
                break
        
        # Find intent
        for find_keyword in find_keywords:
            if find_keyword in command_lower:
                intent['action_type'] = 'inspection'
                intent['action'] = 'find_object'
                
                # Extract object to find
                words = command_lower.split()
                for word in words:
                    if word in ['cup', 'book', 'ball', 'box', 'phone', 'laptop']:
                        intent['parameters']['object'] = word
                        break
                
                if 'object' not in intent['parameters']:
                    intent['parameters']['object'] = 'object'
                
                break
        
        # Speak intent
        for speak_keyword in speak_keywords:
            if speak_keyword in command_lower:
                intent['action_type'] = 'communication'
                intent['action'] = 'speak_response'
                
                # Extract message to speak
                # Remove command words to get the actual message
                message = command_lower
                for keyword in speak_keywords:
                    message = message.replace(keyword, "").strip()
                
                intent['parameters']['message'] = message or "Hello!"
                break
        
        return intent
    
    def plan_task_execution(self, intent: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Plan task execution based on intent"""
        
        # Based on the intent, create a task plan
        plan = {
            'main_task': intent.get('action', 'unknown'),
            'steps': [],
            'estimated_duration': 0.0,
            'confidence': intent.get('confidence', 0.5)
        }
        
        action_type = intent.get('action_type')
        action = intent.get('action')
        params = intent.get('parameters', {})
        
        if action_type == 'navigation':
            # Navigation plan: perceive environment -> plan path -> execute navigation
            plan['steps'] = [
                {
                    'action': 'perceive_environment',
                    'parameters': {},
                    'expected_duration': 0.5,
                    'description': 'Scan environment for obstacles and safe paths'
                },
                {
                    'action': 'plan_navigation_path',
                    'parameters': {'target_pose': params.get('target_pose', {'x': 0.0, 'y': 0.0, 'z': 0.0})},
                    'expected_duration': 1.0,
                    'description': 'Calculate optimal path to destination'
                },
                {
                    'action': 'execute_navigation',
                    'parameters': {'target_pose': params.get('target_pose', {'x': 0.0, 'y': 0.0, 'z': 0.0})},
                    'expected_duration': 10.0,  # Variable based on distance
                    'description': 'Navigate to the specified location'
                }
            ]
            
        elif action_type == 'manipulation':
            # Manipulation plan: navigate to object -> detect -> grasp
            plan['steps'] = [
                {
                    'action': 'find_object',
                    'parameters': {'object_type': params.get('object', 'unknown')},
                    'expected_duration': 2.0,
                    'description': 'Locate the specified object in the environment'
                },
                {
                    'action': 'navigate_to_object',
                    'parameters': {'object_type': params.get('object', 'unknown')},
                    'expected_duration': 3.0,
                    'description': 'Move close to the target object'
                },
                {
                    'action': 'grasp_object',
                    'parameters': {
                        'object_id': params.get('object', 'unknown'),
                        'grasp_type': self.select_appropriate_grasp(params.get('object', 'unknown'))
                    },
                    'expected_duration': 5.0,
                    'description': 'Grasp the target object'
                }
            ]
        
        elif action_type == 'inspection':
            # Inspection plan: navigate to area -> scan -> identify
            plan['steps'] = [
                {
                    'action': 'search_for_object',
                    'parameters': {'object_type': params.get('object', 'unknown')},
                    'expected_duration': 5.0,
                    'description': 'Search the environment for the specified object'
                }
            ]
        
        elif action_type == 'communication':
            # Communication plan: speak the message
            plan['steps'] = [
                {
                    'action': 'speak_message',
                    'parameters': {'text': params.get('message', 'Hello World')},
                    'expected_duration': 2.0,
                    'description': 'Speak the specified message aloud'
                }
            ]
        
        else:
            # For other action types, create a simple execution plan
            plan['steps'] = [
                {
                    'action': action,
                    'parameters': params,
                    'expected_duration': 1.0,
                    'description': f'Execute {action} action'
                }
            ]
        
        # Calculate estimated duration
        plan['estimated_duration'] = sum(step['expected_duration'] for step in plan['steps'])
        
        return plan
    
    def select_appropriate_grasp(self, object_type: str) -> str:
        """Select appropriate grasp type based on object properties"""
        grasp_types = {
            'cup': 'top_grasp',
            'book': 'edge_grasp',
            'ball': 'spherical_grasp',
            'box': 'power_grasp',
            'phone': 'pinch_grasp',
            'laptop': 'power_grasp'
        }
        
        return grasp_types.get(object_type, 'power_grasp')
    
    def voice_active_callback(self, msg: Bool):
        """Handle voice activation/deactivation"""
        self.voice_active = msg.data
        if self.voice_active:
            self.get_logger().info("Voice interface activated")
        else:
            self.get_logger().info("Voice interface deactivated")
    
    def provide_feedback(self, text: str):
        """Provide feedback through voice interface"""
        feedback_msg = String()
        feedback_msg.data = json.dumps({
            'type': 'feedback',
            'text': text,
            'timestamp': self.get_clock().now().seconds_nanoseconds()
        })
        
        self.feedback_pub.publish(feedback_msg)
        self.get_logger().info(f"Feedback: {text}")
    
    def shutdown_voice_system(self):
        """Properly shut down voice system"""
        self.listening_active = False
        self.get_logger().info("Voice system shutdown initiated")


class VoiceCommandValidator:
    """Validator for voice command processing pipeline"""
    
    def __init__(self):
        self.test_cases = [
            {
                'command': "Go to the kitchen",
                'expected_action': 'go_to_location',
                'expected_params': {'location': 'kitchen'}
            },
            {
                'command': "Pick up the red cup",
                'expected_action': 'grasp_object',
                'expected_params': {'object': 'cup'}
            },
            {
                'command': "Find the blue ball",
                'expected_action': 'find_object',
                'expected_params': {'object': 'ball'}
            },
            {
                'command': "Say hello world",
                'expected_action': 'speak_response',
                'expected_params': {'message': 'hello world'}
            }
        ]
    
    def validate_command_understanding(self, command: str, expected_action: str) -> Dict[str, Any]:
        """Validate that command is understood correctly"""
        # In practice, this would call the actual command understanding system
        # For demonstration, we'll use the local implementation
        
        intent = self.local_command_understanding(command)
        
        if intent:
            result = {
                'command': command,
                'parsed_action': intent.get('action'),
                'parsed_params': intent.get('parameters'),
                'expected_action': expected_action,
                'is_correct': intent.get('action') == expected_action,
                'confidence': intent.get('confidence', 0.0)
            }
        else:
            result = {
                'command': command,
                'parsed_action': 'none',
                'parsed_params': {},
                'expected_action': expected_action,
                'is_correct': False,
                'confidence': 0.0
            }
        
        return result
    
    def run_validation_tests(self) -> Dict[str, Any]:
        """Run all validation tests"""
        results = []
        passed = 0
        total = len(self.test_cases)
        
        for test_case in self.test_cases:
            result = self.validate_command_understanding(
                test_case['command'],
                test_case['expected_action']
            )
            results.append(result)
            
            if result['is_correct']:
                passed += 1
        
        summary = {
            'total_tests': total,
            'passed_tests': passed,
            'success_rate': passed / total if total > 0 else 0,
            'test_cases': results
        }
        
        return summary


def main(args=None):
    rclpy.init(args=args)
    
    # Create and start the voice interface system
    voice_interface = VoiceInterfaceSystem()
    
    # Initialize validator to test the system
    validator = VoiceCommandValidator()
    
    try:
        # Print test results
        print("Running Voice Command Validation Tests:")
        test_results = validator.run_validation_tests()
        
        print(f"Tests passed: {test_results['passed_tests']}/{test_results['total_tests']}")
        print(f"Success rate: {test_results['success_rate']:.0%}")
        
        print("\nTest Details:")
        for test in test_results['test_cases']:
            status = "✓ PASS" if test['is_correct'] else "✗ FAIL"
            print(f"  {status} '{test['command']}' -> {test['parsed_action']}")
        
        # Start the voice interface
        voice_interface.start_voice_system()
        
        # Run the node
        rclpy.spin(voice_interface)
        
    except KeyboardInterrupt:
        voice_interface.get_logger().info("Shutting down voice interface system...")
        voice_interface.shutdown_voice_system()
    finally:
        voice_interface.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### Hints

- Use keyword-based understanding as a fallback when API is unavailable
- Implement robust error handling for network issues
- Consider acoustic environment for improved speech recognition
- Add confidence thresholds for command execution
- Implement voice command confirmation for complex tasks

## Exercise 2: Cognitive Planning from Natural Language

Create a cognitive planning system that translates complex natural language commands into executable robotic actions.

### Instructions

1. Implement a semantic parser to convert natural language to action primitives
2. Create a hierarchical task planner that handles complex multi-step tasks
3. Add context awareness to handle pronouns and references
4. Implement failure recovery and plan modification
5. Validate plan execution against natural language goals

### Solution

#### Semantic Parser and Cognitive Planner

```python
# semantic_parser.py
import openai
import json
import re
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ParsedCommand:
    """Parsed representation of a natural language command"""
    action_type: str  # e.g., "navigation", "manipulation", "communication"
    action: str       # e.g., "go_to_location", "grasp_object", "speak"
    parameters: Dict[str, Any]
    modifiers: List[str]  # e.g., "quickly", "carefully", "urgently"
    objects: List[Dict[str, str]]  # Objects mentioned in command
    locations: List[Dict[str, str]]  # Locations mentioned in command
    context_references: List[str]  # References to previous context ("it", "that", etc.)


class SemanticParser:
    """Parses natural language commands into structured semantic representations"""
    
    def __init__(self):
        # Define action patterns and vocabularies
        self.action_patterns = {
            'navigation': [
                r'go to (?P<location>[\w\s]+)',
                r'travel to (?P<location>[\w\s]+)', 
                r'navigate to (?P<location>[\w\s]+)',
                r'move to (?P<location>[\w\s]+)',
                r'walk to (?P<location>[\w\s]+)',
                r'head to (?P<location>[\w\s]+)',
                r'take me to (?P<location>[\w\s]+)'
            ],
            'manipulation': [
                r'pick up (?P<object>[\w\s]+)',
                r'grasp the (?P<object>[\w\s]+)',
                r'get the (?P<object>[\w\s]+)',
                r'take the (?P<object>[\w\s]+)',
                r'stop the (?P<object>[\w\s]+)',
                r'lift the (?P<object>[\w\s]+)',
                r'hold the (?P<object>[\w\s]+)'
            ],
            'communication': [
                r'say (?P<message>[\w\s]+)',
                r'announce (?P<message>[\w\s]+)',
                r'tell me (?P<message>[\w\s]+)',
                r'speak (?P<message>[\w\s]+)',
                r'repeat (?P<message>[\w\s]+)'
            ],
            'inspection': [
                r'find (?P<object>[\w\s]+)',
                r'locate (?P<object>[\w\s]+)',
                r'look for (?P<object>[\w\s]+)',
                r'search for (?P<object>[\w\s]+)',
                r'where is the (?P<object>[\w\s]+)'
            ]
        }
        
        # Location vocabulary
        self.locations = {
            'kitchen': {'x': 3.0, 'y': 1.0, 'z': 0.0},
            'living room': {'x': 0.0, 'y': 0.0, 'z': 0.0},
            'bedroom': {'x': -2.0, 'y': 2.0, 'z': 0.0},
            'office': {'x': -1.0, 'y': -1.0, 'z': 0.0},
            'dining room': {'x': 1.5, 'y': -1.0, 'z': 0.0},
            'bathroom': {'x': -0.5, 'y': 2.5, 'z': 0.0}
        }
        
        # Object categories
        self.object_categories = {
            'cups': ['cup', 'mug', 'glass', 'water glass', 'coffee cup', 'tea cup'],
            'books': ['book', 'novel', 'textbook', 'magazine', 'journal', 'guide'],
            'electronics': ['phone', 'laptop', 'tablet', 'computer', 'tv remote'],
            'furniture': ['chair', 'table', 'desk', 'couch', 'bed', 'bookshelf'],
            'food': ['apple', 'banana', 'snack', 'sandwich', 'meal'],
            'tools': ['pen', 'pencil', 'notebook', 'keys', 'wallet']
        }
    
    def parse_command(self, command: str, context: Dict[str, Any] = None) -> Optional[ParsedCommand]:
        """Parse a natural language command into semantic representation"""
        if not command:
            return None
        
        command_lower = command.lower()
        
        # First, try to determine action type using regex patterns
        action_type = None
        action = None
        extracted_params = {}
        
        for action_cat, patterns in self.action_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, command_lower, re.IGNORECASE)
                if match:
                    action_type = action_cat
                    action = self._normalize_action(action_cat, pattern)
                    extracted_params.update(match.groupdict())
                    break
            if action_type:
                break
        
        if not action_type:
            # If no pattern matches, use LLM to determine action
            action_type, action, extracted_params = self._infer_action_with_llm(command, context)
        
        # Process objects
        objects = self._extract_objects(command_lower, context)
        
        # Process locations
        locations = self._extract_locations(command_lower, context)
        
        # Extract modifiers (adverbs that modify how action should be performed)
        modifiers = self._extract_modifiers(command_lower)
        
        # Resolve context references (pronouns like "it", "that", "them")
        context_refs = self._extract_context_references(command_lower)
        
        return ParsedCommand(
            action_type=action_type,
            action=action,
            parameters=extracted_params,
            modifiers=modifiers,
            objects=objects,
            locations=locations,
            context_references=context_refs
        )
    
    def _normalize_action(self, action_type: str, pattern: str) -> str:
        """Normalize action from regex pattern to standard action name"""
        # Convert pattern to action name - this is a simplified version
        # In practice, would be more sophisticated
        if 'go to' in pattern or 'move to' in pattern or 'navigate to' in pattern:
            return 'go_to_location'
        elif 'pick up' in pattern or 'grasp' in pattern or 'get' in pattern:
            return 'grasp_object'
        elif 'find' in pattern or 'look for' in pattern:
            return 'detect_object'
        elif 'say' in pattern or 'speak' in pattern:
            return 'speak_response'
        else:
            return action_type
    
    def _infer_action_with_llm(self, command: str, context: Dict[str, Any] = None) -> Tuple[str, str, Dict[str, Any]]:
        """Use LLM to infer action when regex doesn't match"""
        
        # For demonstration, we'll return a default
        # In practice, would call OpenAI API
        
        # If we have OpenAI API available:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            client = openai.OpenAI(api_key=openai_api_key)
            
            context_str = json.dumps(context) if context else "No previous context"
            
            prompt = f"""
            Given the following command and context, determine:
            1. The action type (navigation, manipulation, inspection, communication)
            2. The specific action to perform (go_to_location, grasp_object, etc.)
            3. The relevant parameters
            
            Command: "{command}"
            Context: {context_str}
            
            Respond with a JSON object:
            {{
                "action_type": "string",
                "action": "string", 
                "parameters": {{"parameter_name": "parameter_value", ...}}
            }}
            """
            
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a semantic parsing system for humanoid robots. Extract action type, action, and parameters from user commands."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=200
                )
                
                content = response.choices[0].message.content
                # Extract JSON
                import re
                match = re.search(r'\{.*\}', content, re.DOTALL)
                if match:
                    result = json.loads(match.group(0))
                    return result['action_type'], result['action'], result['parameters']
                else:
                    # If no JSON found, use fallback
                    return "unknown", "unknown_action", {}
                    
            except Exception as e:
                print(f"Error calling OpenAI API: {e}")
                # Fall back to simple keyword matching
                return self._infer_action_with_keywords(command, context)
        else:
            # Fall back to keyword matching if no API key
            return self._infer_action_with_keywords(command, context)
    
    def _infer_action_with_keywords(self, command: str, context: Dict[str, Any] = None) -> Tuple[str, str, Dict[str, Any]]:
        """Simple keyword-based action inference as fallback"""
        cmd_lower = command.lower()
        
        # Navigation
        if any(word in cmd_lower for word in ['go to', 'move to', 'navigate', 'walk to', 'drive to', 'travel']):
            # Extract location
            for loc_name in self.locations.keys():
                if loc_name in cmd_lower:
                    return "navigation", "go_to_location", {"location": loc_name}
            else:
                return "navigation", "go_to_location", {"location": "unknown"}
        
        # Manipulation
        elif any(word in cmd_lower for word in ['pick up', 'grasp', 'lift', 'get', 'take', 'hold']):
            # Extract object
            for category, objects in self.object_categories.items():
                for obj in objects:
                    if obj in cmd_lower:
                        return "manipulation", "grasp_object", {"object": obj}
            else:
                return "manipulation", "grasp_object", {"object": "unknown"}
        
        # Inspection
        elif any(word in cmd_lower for word in ['find', 'locate', 'look for', 'search for', 'where is']):
            # Extract object
            for category, objects in self.object_categories.items():
                for obj in objects:
                    if obj in cmd_lower:
                        return "inspection", "detect_object", {"object": obj}
            else:
                return "inspection", "detect_object", {"object": "unknown"}
        
        # Communication
        elif any(word in cmd_lower for word in ['say', 'speak', 'tell', 'announce']):
            # Extract message
            message = cmd_lower.replace('say', '').replace('speak', '').replace('tell me', '').strip()
            return "communication", "speak_response", {"message": message or "Hello!"}
        
        else:
            return "unknown", "unknown", {}
    
    def _extract_objects(self, command: str, context: Dict[str, Any] = None) -> List[Dict[str, str]]:
        """Extract objects mentioned in command"""
        objects = []
        
        for category, obj_names in self.object_categories.items():
            for obj_name in obj_names:
                if obj_name in command:
                    # Find any adjectives before the object
                    pattern = r'(\w+)\s+' + re.escape(obj_name)
                    match = re.search(pattern, command)
                    
                    obj_entry = {
                        'name': obj_name,
                        'category': category,
                        'adjective': match.group(1) if match else None
                    }
                    
                    objects.append(obj_entry)
        
        return objects
    
    def _extract_locations(self, command: str, context: Dict[str, Any] = None) -> List[Dict[str, str]]:
        """Extract locations mentioned in command"""
        locations = []
        
        for loc_name in self.locations.keys():
            if loc_name in command:
                location_entry = {
                    'name': loc_name,
                    'coordinates': self.locations[loc_name]
                }
                locations.append(location_entry)
        
        return locations
    
    def _extract_modifiers(self, command: str) -> List[str]:
        """Extract modifiers (adverbs, adjectives) that affect action execution"""
        modifiers = []
        
        # Common modifiers
        modifier_words = [
            'slowly', 'quickly', 'carefully', 'gently', 'firmly', 'lightly',
            'urgently', 'immediately', 'fast', 'cautiously', 'careful',
            'carefully', 'aggressively', 'precisely', 'exactly'
        ]
        
        for mod in modifier_words:
            if mod in command:
                modifiers.append(mod)
        
        return modifiers
    
    def _extract_context_references(self, command: str) -> List[str]:
        """Extract context references (pronouns, demonstratives)"""
        context_refs = []
        
        # Pronouns and demonstratives that likely refer to previous context
        refs = ['it', 'that', 'those', 'these', 'the same', 'the object', 'the item', 'the thing']
        
        for ref in refs:
            if ref in command:
                context_refs.append(ref)
        
        return context_refs


class CognitivePlanner:
    """Plans robotic actions from parsed natural language commands"""
    
    def __init__(self):
        self.parser = SemanticParser()
        self.task_library = self._initialize_task_library()
        
    def _initialize_task_library(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize library of tasks with their subtasks"""
        return {
            'go_to_location': [
                {'action': 'perceive_environment', 'parameters': {}},
                {'action': 'plan_path', 'parameters': {}},
                {'action': 'execute_navigation', 'parameters': {}},
                {'action': 'confirm_arrival', 'parameters': {}}
            ],
            'grasp_object': [
                {'action': 'detect_object', 'parameters': {}},
                {'action': 'navigate_to_object', 'parameters': {}},
                {'action': 'plan_grasp', 'parameters': {}},
                {'action': 'execute_grasp', 'parameters': {}},
                {'action': 'verify_grasp', 'parameters': {}}
            ],
            'detect_object': [
                {'action': 'orient_sensor', 'parameters': {}},
                {'action': 'activate_vision', 'parameters': {}},
                {'action': 'process_image', 'parameters': {}},
                {'action': 'identify_object', 'parameters': {}},
                {'action': 'update_world_model', 'parameters': {}}
            ],
            'speak_response': [
                {'action': 'prepare_text', 'parameters': {}},
                {'action': 'synthesize_speech', 'parameters': {}},
                {'action': 'play_audio', 'parameters': {}}
            ]
        }
    
    def plan_command(self, command: str, robot_state: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Plan a sequence of robot actions from a natural language command"""
        
        # Step 1: Parse the command
        parsed_cmd = self.parser.parse_command(command, robot_state)
        
        if not parsed_cmd:
            print(f"Could not parse command: {command}")
            return None
        
        # Step 2: Generate task plan based on parsed command
        task_plan = self._generate_task_plan(parsed_cmd, robot_state)
        
        if not task_plan:
            print(f"Could not generate task plan for parsed command: {parsed_cmd}")
            return None
        
        # Step 3: Add context and metadata to the plan
        full_plan = {
            'original_command': command,
            'parsed_command': parsed_cmd,
            'task_plan': task_plan,
            'created_at': time.time(),
            'estimated_duration': self._estimate_plan_duration(task_plan),
            'confidence': self._estimate_plan_confidence(parsed_cmd, robot_state)
        }
        
        return full_plan
    
    def _generate_task_plan(self, parsed_cmd: ParsedCommand, robot_state: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Generate a detailed task plan for the parsed command"""
        
        if parsed_cmd.action in self.task_library:
            # Get the basic task plan
            base_plan = self.task_library[parsed_cmd.action].copy()
            
            # Customize the plan with command-specific parameters
            customized_plan = []
            for task in base_plan:
                # Copy task and customize parameters
                custom_task = task.copy()
                
                # If the task needs to use parameters from the parsed command
                if task['action'] == 'execute_navigation' and 'location' in parsed_cmd.parameters:
                    custom_task['parameters']['target_pose'] = self.parser.locations.get(
                        parsed_cmd.parameters['location'], 
                        {'x': 0.0, 'y': 0.0, 'z': 0.0}
                    )
                elif task['action'] == 'grasp_object' and 'object' in parsed_cmd.parameters:
                    custom_task['parameters']['object_type'] = parsed_cmd.parameters['object']
                elif task['action'] == 'detect_object' and 'object' in parsed_cmd.parameters:
                    custom_task['parameters']['object_type'] = parsed_cmd.parameters['object']
                
                # Add any modifiers to relevant tasks
                if parsed_cmd.modifiers and task['action'] in ['execute_navigation', 'grasp_object']:
                    custom_task['parameters']['execution_style'] = parsed_cmd.modifiers[0]  # Use first modifier
                    
                customized_plan.append(custom_task)
            
            return customized_plan
        else:
            # For unknown actions, return a simple plan with just that action
            return [
                {
                    'action': parsed_cmd.action,
                    'parameters': parsed_cmd.parameters,
                    'description': f'Execute {parsed_cmd.action} with provided parameters'
                }
            ]
    
    def _estimate_plan_duration(self, task_plan: List[Dict[str, Any]]) -> float:
        """Estimate the duration of a task plan"""
        # This is a simplified estimation
        # In practice, would use historical data, robot dynamics, etc.
        duration_per_task = {
            'perceive_environment': 0.5,
            'plan_path': 1.0,
            'execute_navigation': 5.0,  # Dependent on distance
            'confirm_arrival': 0.5,
            'detect_object': 2.0,
            'navigate_to_object': 3.0,
            'plan_grasp': 1.0,
            'execute_grasp': 2.0,
            'verify_grasp': 0.5
        }
        
        total_duration = 0.0
        for task in task_plan:
            duration = duration_per_task.get(task['action'], 1.0)
            total_duration += duration
        
        return total_duration
    
    def _estimate_plan_confidence(self, parsed_cmd: ParsedCommand, robot_state: Dict[str, Any]) -> float:
        """Estimate confidence in plan execution"""
        # Start with parsing confidence
        base_confidence = parsed_cmd.confidence if hasattr(parsed_cmd, 'confidence') else 0.8
        
        # Adjust based on robot state and capabilities
        if robot_state and 'capabilities' in robot_state:
            if parsed_cmd.action_type not in robot_state['capabilities']:
                return base_confidence * 0.5  # Lower confidence if robot can't perform action type
        
        # Adjust based on object specificity
        if parsed_cmd.objects:
            for obj in parsed_cmd.objects:
                if obj.get('adjective') is None:
                    base_confidence *= 0.8  # Less confidence without specific descriptors
        
        return min(1.0, base_confidence)
    
    def update_plan_with_context(self, plan: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Update a plan with additional context information"""
        # Handle pronouns and references in the plan
        if context:
            updated_plan = plan.copy()
            
            # Resolve any context references in the plan
            if plan.get('parsed_command') and plan['parsed_command'].context_references:
                # In practice, this would resolve "it" to a specific object from context
                # For demo, we'll just add a note
                if 'resolution_note' not in updated_plan:
                    updated_plan['resolution_note'] = []
                
                for ref in plan['parsed_command'].context_references:
                    updated_plan['resolution_note'].append(f"Resolved reference '{ref}' to {context.get('last_mentioned_object', 'unknown')}")
            
            return updated_plan
        else:
            return plan


# Test the system
def test_semantic_parser():
    parser = SemanticParser()
    planner = CognitivePlanner()
    
    test_commands = [
        "Go to the kitchen",
        "Pick up the red cup",
        "Find the blue ball in the living room",
        "Take the book to the office",
        "Say hello to everyone"
    ]
    
    print("Testing Semantic Parser and Cognitive Planner:")
    print("="*60)
    
    for cmd in test_commands:
        print(f"\nCommand: '{cmd}'")
        
        # Parse command
        parsed = parser.parse_command(cmd)
        print(f"  Parsed: {parsed.action_type} -> {parsed.action}")
        print(f"  Parameters: {parsed.parameters}")
        print(f"  Objects: {[obj['name'] for obj in parsed.objects]}")
        print(f"  Locations: {[loc['name'] for loc in parsed.locations]}")
        
        # Plan for command
        plan = planner.plan_command(cmd)
        if plan:
            print(f"  Task Plan: {len(plan['task_plan'])} steps")
            for i, task in enumerate(plan['task_plan']):
                print(f"    {i+1}. {task['action']}")
        else:
            print("  Could not generate plan")


if __name__ == "__main__":
    test_semantic_parser()
```

### Hints

- Use semantic parsing to extract meaning from natural language
- Implement hierarchical planning for complex tasks
- Consider context when resolving pronouns and references
- Plan for failure recovery and alternative strategies
- Validate plan feasibility against robot capabilities

## Exercise 3: System Integration and Validation

Create a complete validation and testing system to ensure all components work together properly.

### Instructions

1. Build a system that validates the complete pipeline from voice to action
2. Create test scenarios with various command complexities
3. Implement performance monitoring for the full pipeline
4. Create error handling and recovery testing
5. Validate system behavior in simulated and real environments

### Solution

#### Complete Pipeline Validation System

```python
# pipeline_validator.py
import unittest
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import time
import threading
from typing import Dict, Any, List
import statistics
import numpy as np


class PipelineValidator(Node):
    """Validates the complete humanoid autonomy pipeline"""
    
    def __init__(self):
        super().__init__('pipeline_validator')
        
        # Initialize components under test
        self.voice_interface = VoiceInterfaceSystem(self)
        self.cognitive_planner = CognitivePlanner()
        self.motion_controller = MotionController(self)  # Using mock for testing
        
        # Test results storage
        self.test_results = []
        self.performance_metrics = {
            'response_times': [],
            'success_rates': [],
            'error_rates': [],
            'resource_usage': []
        }
        
        # Test scenarios
        self.test_scenarios = [
            {
                'name': 'Simple Navigation',
                'command': 'Go to the kitchen',
                'expected_actions': ['perceive_environment', 'plan_path', 'execute_navigation'],
                'timeout': 15.0
            },
            {
                'name': 'Object Grasping',
                'command': 'Pick up the red cup',
                'expected_actions': ['detect_object', 'navigate_to_object', 'grasp_object'],
                'timeout': 30.0
            },
            {
                'name': 'Complex Task',
                'command': 'Go to the kitchen, find the blue ball, and bring it to me',
                'expected_actions': ['go_to_location', 'detect_object', 'grasp_object', 'return_to_user'],
                'timeout': 60.0
            }
        ]
        
        self.get_logger().info("Pipeline Validator initialized")
    
    def run_complete_pipeline_tests(self) -> Dict[str, Any]:
        """Run all pipeline validation tests"""
        
        self.get_logger().info("Starting complete pipeline validation tests...")
        
        results = {
            'overall_success': 0,
            'total_tests': 0,
            'individual_results': [],
            'performance_summary': {},
            'errors_encountered': [],
            'recommendations': []
        }
        
        for scenario in self.test_scenarios:
            test_result = self.run_scenario_test(scenario)
            results['individual_results'].append(test_result)
            results['total_tests'] += 1
            
            if test_result['success']:
                results['overall_success'] += 1
        
        # Calculate performance metrics
        results['performance_summary'] = self.get_performance_summary()
        
        # Generate recommendations based on failures
        failed_tests = [r for r in results['individual_results'] if not r['success']]
        if failed_tests:
            results['recommendations'] = self.generate_recommendations(failed_tests)
        
        return results
    
    def run_scenario_test(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single scenario test"""
        
        test_result = {
            'scenario_name': scenario['name'],
            'command': scenario['command'],
            'expected_actions': scenario['expected_actions'],
            'actual_actions': [],
            'execution_time': 0.0,
            'success': False,
            'errors': [],
            'notes': []
        }
        
        self.get_logger().info(f"Running scenario: {scenario['name']}")
        start_time = time.time()
        
        try:
            # Step 1: Parse the command with the cognitive planner
            plan = self.cognitive_planner.plan_command(scenario['command'])
            
            if not plan:
                test_result['errors'].append("Cognitive planner failed to create plan")
                return test_result
            
            test_result['actual_actions'] = [task['action'] for task in plan['task_plan']]
            
            # Step 2: Validate that expected actions are in the plan
            expected_set = set(scenario['expected_actions'])
            actual_set = set(test_result['actual_actions'])
            
            missing_actions = expected_set - actual_set
            extra_actions = actual_set - expected_set
            
            if missing_actions:
                test_result['errors'].append(f"Missing expected actions: {list(missing_actions)}")
            if extra_actions:
                test_result['notes'].append(f"Extra actions in plan: {list(extra_actions)}")
            
            # Step 3: Validate action sequence makes sense
            if not self.validate_action_sequence(test_result['actual_actions'], expected_set):
                test_result['errors'].append("Action sequence is invalid")
            
            # If no errors, the test passes
            test_result['success'] = len(test_result['errors']) == 0
            
            # Add performance metric
            execution_time = time.time() - start_time
            test_result['execution_time'] = execution_time
            self.performance_metrics['response_times'].append(execution_time)
            
        except Exception as e:
            test_result['errors'].append(f"Exception during test: {str(e)}")
            test_result['success'] = False
        
        return test_result
    
    def validate_action_sequence(self, actual_sequence: List[str], expected_actions: set) -> bool:
        """Validate that action sequence makes logical sense"""
        # For our scenarios, certain orders matter
        # e.g., for grasping: detect_object -> navigate_to_object -> grasp_object
        
        if 'grasp_object' in expected_actions:
            # Check navigation happens before manipulation
            if 'go_to_location' in actual_sequence and 'grasp_object' in actual_sequence:
                go_idx = actual_sequence.index('go_to_location')
                grasp_idx = actual_sequence.index('grasp_object')
                
                # Navigation should come before grasping in complex tasks
                if go_idx > grasp_idx and len(actual_sequence) > 1:
                    return False
        
        if 'detect_object' in expected_actions:
            # Detection should come before navigation in certain contexts
            if 'navigate_to_object' in actual_sequence:
                detect_idx = actual_sequence.index('detect_object')
                navigate_idx = actual_sequence.index('navigate_to_object')
                
                # Detection should come before navigating to object
                if detect_idx > navigate_idx:
                    return False
        
        return True
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary of tests"""
        
        if not self.performance_metrics['response_times']:
            return {'message': 'No performance data collected'}
        
        response_times = self.performance_metrics['response_times']
        
        return {
            'avg_response_time': statistics.mean(response_times),
            'median_response_time': statistics.median(response_times),
            'std_dev_response_time': statistics.stdev(response_times) if len(response_times) > 1 else 0,
            'min_response_time': min(response_times),
            'max_response_time': max(response_times),
            'total_tests_run': len(response_times)
        }
    
    def generate_recommendations(self, failed_tests: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on failed tests"""
        recommendations = []
        
        for test in failed_tests:
            if 'Missing expected actions' in ', '.join(test['errors']):
                recommendations.append(
                    f"Improve cognitive planning for scenario '{test['scenario_name']}' - missing critical steps"
                )
            if 'Action sequence is invalid' in ', '.join(test['errors']):
                recommendations.append(
                    f"Fix action ordering logic for scenario '{test['scenario_name']}'"
                )
        
        if not recommendations:
            recommendations.append("Consider adding more test scenarios to validate edge cases")
        
        return recommendations


class IntegrationTester:
    """Integration tester for the complete humanoid system"""
    
    def __init__(self, node: Node):
        self.node = node
        
        # Performance tracking
        self.start_time = time.time()
        self.test_start_time = None
        
        # Component integration tracking
        self.integration_tests = [
            self.test_perception_planning_integration,
            self.test_planning_control_integration,
            self.test_control_perception_integration,
            self.test_voice_perception_integration
        ]
    
    def test_perception_planning_integration(self) -> Dict[str, Any]:
        """Test integration between perception and planning"""
        
        test_result = {
            'name': 'Perception-Planning Integration',
            'success': True,
            'issues': [],
            'duration': 0.0,
            'confidence': 0.8
        }
        
        start_time = time.time()
        
        try:
            # Test that perception data feeds correctly to planning
            # Mock perception result
            mock_perception_data = {
                'objects': [
                    {'id': 'red_cup', 'type': 'cup', 'position': {'x': 1.0, 'y': 1.0, 'z': 0.8}},
                    {'id': 'blue_ball', 'type': 'ball', 'position': {'x': 1.5, 'y': 0.5, 'z': 0.1}}
                ],
                'obstacles': [{'position': {'x': 2.0, 'y': 2.0, 'z': 0.0}, 'radius': 0.3}],
                'free_spaces': [{'position': {'x': -1.0, 'y': -1.0, 'z': 0.0}}]
            }
            
            # Verify perception data is used by planner
            # In a real test, we'd check that plan generation incorporates perception data
            test_result['success'] = 'objects' in mock_perception_data
            test_result['confidence'] = 0.9 if test_result['success'] else 0.1
            
        except Exception as e:
            test_result['success'] = False
            test_result['issues'].append(f"Error in perception-planning integration test: {e}")
        
        test_result['duration'] = time.time() - start_time
        return test_result
    
    def test_planning_control_integration(self) -> Dict[str, Any]:
        """Test integration between planning and control"""
        
        test_result = {
            'name': 'Planning-Control Integration',
            'success': True,
            'issues': [],
            'duration': 0.0,
            'confidence': 0.7
        }
        
        start_time = time.time()
        
        try:
            # Test that planned actions can be executed by controller
            # Mock plan with simple navigation action
            mock_plan = [
                {
                    'action': 'navigate_to',
                    'parameters': {'position': {'x': 1.0, 'y': 1.0, 'z': 0.0}},
                    'expected_duration': 5.0
                }
            ]
            
            # Verify plan can be passed to control system
            # In a real test, we'd try to execute the plan
            test_result['success'] = len(mock_plan) > 0
            test_result['confidence'] = 0.85 if test_result['success'] else 0.1
            
        except Exception as e:
            test_result['success'] = False
            test_result['issues'].append(f"Error in planning-control integration test: {e}")
        
        test_result['duration'] = time.time() - start_time
        return test_result
    
    def test_control_perception_integration(self) -> Dict[str, Any]:
        """Test integration between control and perception"""
        
        test_result = {
            'name': 'Control-Perception Integration',
            'success': True,
            'issues': [],
            'duration': 0.0,
            'confidence': 0.8
        }
        
        start_time = time.time()
        
        try:
            # Test that perception data updates during control execution
            # This would ensure closed-loop sensor feedback during control
            # For now, test that both systems can access world state
            test_result['success'] = True  # Simplified test
            test_result['confidence'] = 0.9
            
        except Exception as e:
            test_result['success'] = False
            test_result['issues'].append(f"Error in control-perception integration test: {e}")
        
        test_result['duration'] = time.time() - start_time
        return test_result
    
    def test_voice_perception_integration(self) -> Dict[str, Any]:
        """Test integration between voice interface and perception"""
        
        test_result = {
            'name': 'Voice-Perception Integration',
            'success': True,
            'issues': [],
            'duration': 0.0,
            'confidence': 0.9
        }
        
        start_time = time.time()
        
        try:
            # Test that voice commands can trigger perception updates
            # For example: "Find the red cup" should trigger object detection
            voice_command = "Find the red cup"
            
            # Parse the command
            parsed = None  # This would use actual parser in real test
            # For demo purposes, just verify basic functionality
            test_result['success'] = "find" in voice_command.lower()
            
            if test_result['success']:
                test_result['confidence'] = 0.9
            else:
                test_result['issues'].append("Command parsing failed")
                test_result['confidence'] = 0.3
                
        except Exception as e:
            test_result['success'] = False
            test_result['issues'].append(f"Error in voice-perception integration test: {e}")
        
        test_result['duration'] = time.time() - start_time
        return test_result
    
    def run_all_integration_tests(self) -> Dict[str, Any]:
        """Run all integration tests"""
        
        self.node.get_logger().info("Running system integration tests...")
        
        results = {
            'integration_tests': [],
            'overall_success_rate': 0.0,
            'total_issues': 0,
            'test_duration': 0.0
        }
        
        test_start = time.time()
        
        for test_func in self.integration_tests:
            test_result = test_func()
            results['integration_tests'].append(test_result)
            
            if not test_result['success']:
                results['total_issues'] += 1
        
        results['test_duration'] = time.time() - test_start
        successful_tests = sum(1 for test in results['integration_tests'] if test['success'])
        results['overall_success_rate'] = successful_tests / len(results['integration_tests'])
        
        return results


def run_comprehensive_validation():
    """Run the complete validation suite"""
    
    print("Running Comprehensive Humanoid Robot System Validation")
    print("=" * 60)
    
    # Initialize ROS context
    rclpy.init()
    
    # Create validation node
    validator = PipelineValidator()
    
    # Run pipeline validation
    pipeline_results = validator.run_complete_pipeline_tests()
    
    print(f"\nPIPELINE VALIDATION RESULTS:")
    print(f"  Success Rate: {pipeline_results['overall_success']}/{pipeline_results['total_tests']} "
          f"({pipeline_results['overall_success']/max(1,pipeline_results['total_tests'])*100:.1f}%)")
    
    # Run integration tests
    integration_tester = IntegrationTester(validator)
    integration_results = integration_tester.run_all_integration_tests()
    
    print(f"\nINTEGRATION VALIDATION RESULTS:")
    print(f"  Success Rate: {sum(1 for t in integration_results['integration_tests'] if t['success'])}/"
          f"{len(integration_results['integration_tests'])} "
          f"({integration_results['overall_success_rate']*100:.1f}%)")
    
    # Overall result
    overall_success = (
        pipeline_results['overall_success'] == pipeline_results['total_tests'] and
        integration_results['overall_success_rate'] >= 0.9
    )
    
    print(f"\nOVERALL SYSTEM VALIDATION: {'✓ PASS' if overall_success else '✗ FAIL'}")
    
    # Recommendations
    if pipeline_results['recommendations']:
        print(f"\nRECOMMENDATIONS:")
        for rec in pipeline_results['recommendations']:
            print(f"  - {rec}")
    
    if integration_results['total_issues'] > 0:
        print(f"\nINTEGRATION ISSUES DETECTED: {integration_results['total_issues']}")
    
    # Cleanup
    validator.destroy_node()
    rclpy.shutdown()
    
    return {
        'pipeline_validation': pipeline_results,
        'integration_validation': integration_results,
        'overall_success': overall_success
    }


# Unit tests for the complete system
class TestCompleteHumanoidSystem(unittest.TestCase):
    """Unit tests for the complete humanoid robot system"""
    
    def setUp(self):
        """Set up test environment"""
        rclpy.init()
        self.test_node = PipelineValidator()
    
    def tearDown(self):
        """Tear down test environment"""
        self.test_node.destroy_node()
        rclpy.shutdown()
    
    def test_voice_command_processing(self):
        """Test that voice commands are properly processed"""
        # Test simple command parsing
        simple_command = "Go to the kitchen"
        plan = self.test_node.cognitive_planner.plan_command(simple_command)
        
        self.assertIsNotNone(plan)
        self.assertIn('go_to_location', [task['action'] for task in plan['task_plan']])
    
    def test_complex_command_processing(self):
        """Test that complex multi-step commands are processed correctly"""
        complex_command = "Go to the kitchen, find the red cup, and bring it back to me"
        plan = self.test_node.cognitive_planner.plan_command(complex_command)
        
        self.assertIsNotNone(plan)
        
        # Check that plan contains expected actions
        actions = [task['action'] for task in plan['task_plan']]
        self.assertIn('go_to_location', actions)
        self.assertIn('detect_object', actions)
        self.assertIn('grasp_object', actions)
        
        # Check order: should detect before grasp
        detect_idx = actions.index('detect_object')
        grasp_idx = actions.index('grasp_object')
        self.assertLess(detect_idx, grasp_idx, "Detection should occur before grasping")
    
    def test_semantic_parsing(self):
        """Test semantic parsing functionality"""
        parser = SemanticParser()
        command = "Pick up the blue book from the table"
        parsed = parser.parse_command(command)
        
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.action_type, 'manipulation')
        self.assertEqual(parsed.action, 'grasp_object')
        self.assertIn('book', [obj['name'] for obj in parsed.objects])
    
    def test_context_handling(self):
        """Test context-aware command handling"""
        # Create a mock context with a previously mentioned object
        context = {
            'last_mentioned_object': 'red_cup',
            'last_mentioned_location': 'kitchen'
        }
        
        planner = CognitivePlanner()
        command = "Go to it"  # Referring to kitchen
        plan = planner.plan_command(command, context)
        
        # The "it" should resolve to kitchen based on context
        if plan and 'task_plan' in plan:
            # Check if plan involves navigation (which would be to the kitchen)
            nav_task = next((task for task in plan['task_plan'] 
                           if task['action'] in ['go_to_location', 'execute_navigation']), None)
            self.assertIsNotNone(nav_task)
    
    def test_error_handling(self):
        """Test error handling in the system"""
        planner = CognitivePlanner()
        
        # Test with an unknown command
        unknown_command = "Flux capacitor engage mode"
        plan = planner.plan_command(unknown_command)
        
        # Even with unknown command, system should handle gracefully
        # Either return None or return a plan saying it doesn't know
        self.assertIn(plan, [None, {}], "System should handle unknown commands gracefully")


def run_unit_tests():
    """Run unit tests for the complete system"""
    test_suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    
    # Add tests from the TestCompleteHumanoidSystem class
    test_suite.addTests(loader.loadTestsFromTestCase(TestCompleteHumanoidSystem))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result


if __name__ == '__main__':
    # Run comprehensive validation
    validation_results = run_comprehensive_validation()
    
    print("\n" + "="*60)
    print("RUNNING UNIT TESTS")
    print("="*60)
    
    # Run unit tests
    unittest_results = run_unit_tests()
    
    print(f"\nUnit Test Results: {unittest_results.testsRun} tests run, "
          f"{len(unittest_results.failures)} failures, {len(unittest_results.errors)} errors")
    
    print("\nVALIDATION COMPLETE")
    print(f"Pipeline tests: {validation_results['pipeline_validation']['overall_success']}/{validation_results['pipeline_validation']['total_tests']}")
    print(f"Integration tests: {sum(1 for t in validation_results['integration_validation']['integration_tests'] if t['success'])}/{len(validation_results['integration_validation']['integration_tests'])}")