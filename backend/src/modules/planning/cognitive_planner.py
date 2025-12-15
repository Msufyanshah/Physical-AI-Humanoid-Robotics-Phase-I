---
title: 'Chapter 14 - Capstone: Autonomous Humanoid Pipeline'
description: 'Complete capstone project integrating all modules into an autonomous humanoid robot system'
---

# Chapter 14: Capstone: Autonomous Humanoid Pipeline

## Learning Objectives

After reading this chapter, you will be able to:
- Integrate all modules into a cohesive, functioning humanoid autonomy system
- Design and implement a complete perception-action pipeline
- Create a cognitive planning system that translates natural language to robot actions
- Implement closed-loop control for autonomous operation
- Develop comprehensive testing strategies for integrated systems
- Optimize system performance for real-time operation
- Evaluate and validate the complete autonomous pipeline
- Document and maintain the integrated system

## Introduction

This capstone chapter brings together all the concepts learned in previous modules to create a complete autonomous humanoid robot pipeline. We'll integrate perception (vision, sensing), learning (AI, RL), planning (navigation, manipulation), and control (motion, balance) systems into a unified architecture that enables natural human-robot interaction and autonomous task execution.

## System Architecture Integration

### Complete Pipeline Design

The full autonomous humanoid system integrates these key subsystems:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          HUMAN INTERFACE                                    │
│                        (Voice, Gesture, App)                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                      NATURAL LANGUAGE PROCESSING                           │
│              (Whisper ASR → LLM NLU → Intent Recognition)                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                       COGNITIVE PLANNING                                   │
│              (Task Decomposition → Action Planning → Scheduling)           │
├─────────────────────────────────────────────────────────────────────────────┤
│                      PERCEPTION SYSTEM                                     │
│      (Vision → SLAM → Object Detection → Sensor Fusion)                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                      MOTION PLANNING                                       │
│          (Path Planning → Trajectory Generation → Control)                │
├─────────────────────────────────────────────────────────────────────────────┤
│                       LOCOMOTION CONTROL                                    │
│             (Balance Control → Gait Generation → Walking)                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                      MANIPULATION CONTROL                                   │
│            (IK Solvers → Grasp Planning → End-Effector Control)           │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Component Dependencies and Coordination

The integrated system has the following dependencies:
- Perception provides environment information to planning and control
- Natural language understanding translates human commands to action primitives
- Cognitive planning decomposes complex tasks into executable sequences
- Control systems execute planned actions while monitoring safety
- Communication orchestrates all components in a coordinated fashion

## Implementation of the Complete Pipeline

### Main Coordination Node

```python
# humanoid_pipeline.py
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import Image, JointState, Imu, LaserScan
from geometry_msgs.msg import PoseStamped, Twist
from builtin_interfaces.msg import Duration
import threading
import time
import json
import asyncio
from typing import Dict, Any, Optional, List
from collections import deque


class HumanoidPipeline(Node):
    """Main node coordinating the complete humanoid autonomy pipeline"""
    
    def __init__(self):
        super().__init__('humanoid_pipeline')
        
        # Initialize system components
        self.initialize_components()
        
        # System state
        self.current_state = {
            'mode': 'idle',
            'robot_pose': None,
            'world_model': {},
            'active_intent': None,
            'current_plan': [],
            'plan_step': 0,
            'battery_level': 1.0
        }
        
        # Communication interfaces
        self.setup_communication_interfaces()
        
        # Initialize timers
        self.pipeline_timer = self.create_timer(0.02, self.pipeline_loop)  # 50Hz pipeline execution
        self.perception_timer = self.create_timer(0.1, self.process_perception_data)  # 10Hz perception updates
        self.state_monitor_timer = self.create_timer(1.0, self.monitor_system_state)  # 1Hz state monitoring
        
        self.pipeline_initialized = True
        self.get_logger().info("Humanoid Pipeline initialized and ready")
    
    def initialize_components(self):
        """Initialize all system components"""
        
        # Import and initialize components
        try:
            from modules.perception.perception_system import PerceptionSystem
            from modules.planning.cognitive_planner import CognitivePlanner
            from modules.control.motion_controller import MotionController
            from modules.communication.voice_interface import VoiceInterface
            
            # Initialize all components
            self.perception_system = PerceptionSystem(self)
            self.cognitive_planner = CognitivePlanner(self)
            self.motion_controller = MotionController(self)
            self.voice_interface = VoiceInterface(self)
            
            self.get_logger().info("All system components initialized successfully")
            
        except ImportError as e:
            self.get_logger().error(f"Failed to import components: {e}")
            # In a real system, we'd use graceful degradation to allow partial functionality
            # For this example, we'll create mock components
        
        # If components failed to initialize, create mock ones
        if not hasattr(self, 'perception_system'):
            self.get_logger().warn("Using mock components for demonstration")
            self.perception_system = MockPerceptionSystem(self)
            self.cognitive_planner = MockCognitivePlanner(self)
            self.motion_controller = MockMotionController(self)
            self.voice_interface = MockVoiceInterface(self)
    
    def setup_communication_interfaces(self):
        """Set up publishers, subscribers, and services"""
        
        # Subscribers for all inputs
        self.voice_cmd_sub = self.create_subscription(
            String, '/voice_command', self.voice_command_callback, 10
        )
        
        self.text_cmd_sub = self.create_subscription(
            String, '/text_command', self.text_command_callback, 10
        )
        
        # Perceptual inputs
        self.camera_sub = self.create_subscription(
            Image, '/camera/rgb/image_raw', self.camera_callback, 10
        )
        
        self.lidar_sub = self.create_subscription(
            LaserScan, '/scan', self.lidar_callback, 10
        )
        
        self.imu_sub = self.create_subscription(
            Imu, '/imu/data', self.imu_callback, 10
        )
        
        self.joint_state_sub = self.create_subscription(
            JointState, '/joint_states', self.joint_state_callback, 10
        )
        
        # Publishers for system status and commands
        self.status_pub = self.create_publisher(String, '/system_status', 10)
        self.action_cmd_pub = self.create_publisher(String, '/action_commands', 10)
        self.feedback_pub = self.create_publisher(String, '/pipeline_feedback', 10)
        
        self.get_logger().info("Communication interfaces configured")
    
    def voice_command_callback(self, msg: String):
        """Process voice commands through the complete pipeline"""
        try:
            command_data = json.loads(msg.data)
            command_text = command_data['text']
            confidence = command_data.get('confidence', 1.0)
            
            if confidence > 0.7:  # Process only if confidence is high enough
                self.process_command(command_text, source='voice')
            else:
                self.get_logger().warn(f"Ignoring voice command due to low confidence: {confidence}")
                
        except json.JSONDecodeError:
            # If not JSON, treat as plain text
            self.process_command(msg.data, source='voice')
    
    def text_command_callback(self, msg: String):
        """Process text commands through the pipeline"""
        self.process_command(msg.data, source='text')
    
    def process_command(self, command: str, source: str = 'voice'):
        """Process a high-level command through the complete pipeline"""
        
        self.get_logger().info(f"Processing {source} command: '{command}'")
        
        # Update system state
        self.current_state['mode'] = 'processing_command'
        
        try:
            # Step 1: Natural Language Understanding
            self.get_logger().info("Step 1: Understanding command")
            intent = self.cognitive_planner.understand_command(command, self.current_state)
            
            if not intent:
                self.get_logger().error(f"Could not understand command: {command}")
                self.provide_feedback(f"Sorry, I didn't understand that command.")
                self.current_state['mode'] = 'idle'
                return
            
            self.get_logger().info(f"Recognized intent: {intent['action']} with parameters: {intent['parameters']}")
            
            # Step 2: Task Planning
            self.get_logger().info("Step 2: Planning task")
            plan = self.cognitive_planner.plan_task(intent, self.current_state)
            
            if not plan or not plan.get('steps'):
                self.get_logger().error(f"Could not create plan for intent: {intent}")
                self.provide_feedback(f"Sorry, I cannot perform that task right now.")
                self.current_state['mode'] = 'idle'
                return
            
            # Update system state with the plan
            self.current_state['active_intent'] = intent
            self.current_state['current_plan'] = plan['steps']
            self.current_state['plan_step'] = 0
            self.current_state['mode'] = 'executing_plan'
            
            self.get_logger().info(f"Created plan with {len(plan['steps'])} steps: {[step['action'] for step in plan['steps']]}")
            
            # Provide feedback about the plan
            self.provide_feedback(f"I will {command}. This will take several steps.")
            
        except Exception as e:
            self.get_logger().error(f"Error processing command '{command}': {e}")
            self.provide_feedback("I encountered an error while processing your command.")
            self.current_state['mode'] = 'idle'
    
    def pipeline_loop(self):
        """Main pipeline execution loop"""
        
        if self.current_state['mode'] == 'executing_plan':
            self.execute_current_plan_step()
        elif self.current_state['mode'] == 'waiting_for_confirmation':
            # Handle human confirmation for actions that require it
            pass
        elif self.current_state['mode'] == 'safety_intervention':
            # Handle safety interventions
            self.safety_intervention_procedures()
        elif self.current_state['mode'] == 'idle':
            # Monitor for new commands while idle
            pass
    
    def execute_current_plan_step(self):
        """Execute the current step in the active plan"""
        
        if self.current_state['plan_step'] >= len(self.current_state['current_plan']):
            # Plan completed
            self.get_logger().info("Plan execution completed successfully")
            self.provide_feedback("Task completed successfully!")
            self.current_state['mode'] = 'idle'
            self.current_state['active_intent'] = None
            self.current_state['current_plan'] = []
            self.current_state['plan_step'] = 0
            return
        
        # Get current step
        current_step = self.current_state['current_plan'][self.current_state['plan_step']]
        action_type = current_step['action']
        parameters = current_step.get('parameters', {})
        
        self.get_logger().info(f"Executing step {self.current_state['plan_step']+1}/{len(self.current_state['current_plan'])}: {action_type}")
        
        # Execute the action based on its type
        try:
            success = False
            if action_type == 'navigate_to':
                success = self.motion_controller.navigate_to_location(
                    x=parameters.get('x', 0), 
                    y=parameters.get('y', 0),
                    z=parameters.get('z', 0)
                )
            elif action_type == 'perceive_environment':
                success = self.perception_system.perceive_environment()
            elif action_type == 'detect_object':
                success = self.perception_system.detect_object(
                    object_type=parameters.get('object_type', 'unknown')
                )
            elif action_type == 'grasp_object':
                success = self.motion_controller.grasp_object(
                    object_id=parameters.get('object_id', 'unknown')
                )
            elif action_type == 'release_object':
                success = self.motion_controller.release_object()
            elif action_type == 'manipulate_object':
                success = self.motion_controller.manipulate_object(
                    action=parameters.get('manipulation_action', 'lift'),
                    object_id=parameters.get('object_id', 'unknown')
                )
            elif action_type == 'speak_response':
                self.voice_interface.speak_response(parameters.get('text', 'Task completed'))
                success = True  # Speaking always succeeds
            else:
                self.get_logger().warn(f"Unknown action type: {action_type}")
                success = False
            
            if success:
                # Step completed successfully
                self.current_state['plan_step'] += 1
                
                # Update world model based on action outcome
                self.update_world_model_after_action(current_step)
            else:
                # Action failed
                self.get_logger().error(f"Action '{action_type}' failed to execute")
                
                # Attempt recovery or abort plan
                if self.attempt_action_recovery(current_step):
                    # Recovery successful, continue with same step
                    pass
                else:
                    # Recovery failed, abort plan
                    self.abort_current_plan(f"Action failed: {action_type}")
                    self.provide_feedback("I couldn't complete the task. Something went wrong.")
        
        except Exception as e:
            self.get_logger().error(f"Error executing step {action_type}: {e}")
            self.abort_current_plan(f"Execution error: {str(e)}")
    
    def update_world_model_after_action(self, action: Dict[str, Any]):
        """Update world model based on action execution results"""
        action_type = action['action']
        parameters = action.get('parameters', {})
        
        if action_type == 'grasp_object':
            obj_id = parameters.get('object_id')
            if obj_id:
                # Mark object as being held
                if 'objects' not in self.current_state['world_model']:
                    self.current_state['world_model']['objects'] = {}
                self.current_state['world_model']['objects'][obj_id] = {
                    'grasped': True,
                    'location': 'end_effector'
                }
        
        elif action_type == 'release_object':
            # Find currently held object and update its location
            if 'objects' in self.current_state['world_model']:
                for obj_id, obj_data in self.current_state['world_model']['objects'].items():
                    if obj_data.get('grasped'):
                        obj_data['grasped'] = False
                        obj_data['location'] = self.current_state['robot_pose']  # Release at current location
                        break
    
    def attempt_action_recovery(self, failed_action: Dict[str, Any]) -> bool:
        """Attempt to recover from a failed action"""
        
        action_type = failed_action['action']
        
        if action_type == 'navigate_to':
            # Try alternative path or closer destination
            return self.motion_controller.attempt_navigation_recovery(failed_action)
        
        elif action_type == 'detect_object':
            # Increase detection range, try different viewpoint, or ask for help
            retries = failed_action.get('retry_count', 0)
            if retries < 3:
                # Try again with adjusted parameters
                adjusted_action = failed_action.copy()
                adjusted_action['retry_count'] = retries + 1
                # In implementation, we'd call perception with new parameters
                return True  # For now, indicate recovery is possible
        
        elif action_type == 'grasp_object':
            # Try different grasp approach, adjust position, or use different grasp type
            return self.motion_controller.attempt_grasp_recovery(failed_action)
        
        # For other action types, recovery probably not possible
        return False
    
    def abort_current_plan(self, reason: str):
        """Abort the current plan and return to safe state"""
        self.get_logger().error(f"Aborting current plan: {reason}")
        
        # Clear plan state
        self.current_state['mode'] = 'idle'
        self.current_state['active_intent'] = None
        self.current_state['current_plan'] = []
        self.current_state['plan_step'] = 0
        
        # Return robot to safe position if needed
        self.motion_controller.move_to_safe_position()
    
    def process_perception_data(self):
        """Process all perception data to update world model"""
        # Update the world model with perception data
        perception_data = self.perception_system.get_latest_perceptions()
        
        if perception_data:
            self.current_state['world_model'].update(perception_data)
    
    def monitor_system_state(self):
        """Monitor system health and state"""
        # Check battery level
        if self.current_state['battery_level'] < 0.2:
            self.get_logger().warn("Battery level low, suggesting return to charging station")
            if self.current_state['mode'] == 'idle':
                self.return_to_charging_station()
        
        # Publish system status
        status_msg = String()
        status_msg.data = json.dumps({
            'mode': self.current_state['mode'],
            'plan_progress': f"{self.current_state['plan_step']}/{len(self.current_state['current_plan'])}" if self.current_state.get('current_plan') else "0/0",
            'battery_level': self.current_state['battery_level'],
            'timestamp': self.get_clock().now().seconds_nanoseconds()
        })
        
        self.status_pub.publish(status_msg)
    
    def safety_intervention_procedures(self):
        """Handle safety interventions"""
        # Stop all motion
        self.motion_controller.emergency_stop()
        
        # Assess the situation
        safety_assessment = self.perception_system.assess_safety()
        
        if safety_assessment['is_safe']:
            # Resume normal operation
            self.current_state['mode'] = 'idle'
        else:
            # Stay in safety mode and await human intervention
            self.get_logger().warn(f"Safety issue detected: {safety_assessment['issues']}")
            self.provide_feedback("Safety intervention active. Awaiting instructions.")
    
    def return_to_charging_station(self):
        """Auto-return to charging station when battery is low"""
        self.get_logger().info("Returning to charging station due to low battery")
        
        # Plan navigation to charging station
        charge_station_pos = self.get_charging_station_position()
        if charge_station_pos:
            intent = {
                'action': 'navigate_to',
                'parameters': charge_station_pos
            }
            
            plan = self.cognitive_planner.plan_task(intent, self.current_state)
            if plan:
                self.current_state['current_plan'] = plan['steps']
                self.current_state['plan_step'] = 0
                self.current_state['mode'] = 'executing_plan'
    
    def get_charging_station_position(self) -> Optional[Dict[str, float]]:
        """Get charging station position from world model or map"""
        # In practice, this would query a map or world model
        # For this mock example, return a fixed position
        return {'x': 0.0, 'y': 0.0, 'z': 0.0}
    
    def provide_feedback(self, text: str):
        """Provide feedback to user through voice or other interface"""
        self.get_logger().info(f"Feedback: {text}")
        
        feedback_msg = String()
        feedback_msg.data = json.dumps({
            'type': 'feedback',
            'text': text,
            'timestamp': self.get_clock().now().seconds_nanoseconds()
        })
        
        self.feedback_pub.publish(feedback_msg)


class MockPerceptionSystem:
    """Mock perception system for demonstration"""
    
    def __init__(self, node):
        self.node = node
        self.latest_perceptions = {}
    
    def perceive_environment(self):
        """Perceive the current environment"""
        # Mock perception data
        self.latest_perceptions = {
            'objects_detected': ['table', 'chair', 'cup', 'book'],
            'obstacles': [{'x': 1.5, 'y': 0.5, 'radius': 0.3}],
            'surfaces': [{'type': 'table', 'position': {'x': 1.0, 'y': 1.0, 'z': 0.75}}],
            'timestamp': time.time()
        }
        self.node.get_logger().info(f"Perception updated: {len(self.latest_perceptions.get('objects_detected', []))} objects detected")
        return True
    
    def detect_object(self, object_type: str):
        """Detect a specific object type"""
        # Mock implementation
        if object_type in self.latest_perceptions.get('objects_detected', []):
            return True
        else:
            # Simulate detection if not in cache
            import random
            if random.random() > 0.3:  # 70% success rate
                if 'objects_detected' not in self.latest_perceptions:
                    self.latest_perceptions['objects_detected'] = []
                self.latest_perceptions['objects_detected'].append(object_type)
                return True
        return False
    
    def get_latest_perceptions(self):
        """Get the latest perception data"""
        return self.latest_perceptions.copy()
    
    def assess_safety(self):
        """Assess safety of environment"""
        return {
            'is_safe': True,
            'issues': [],
            'confidence': 0.95
        }


class MockCognitivePlanner:
    """Mock cognitive planner for demonstration"""
    
    def __init__(self, node):
        self.node = node
    
    def understand_command(self, command: str, context: Dict[str, Any]):
        """Understand a natural language command"""
        # This would be replaced with actual NLU implementation
        # For demo purposes, use simple keyword matching
        
        command_lower = command.lower()
        
        if 'navigate' in command_lower or 'go to' in command_lower:
            # Extract target location
            if 'kitchen' in command_lower:
                return {
                    'action': 'navigate_to',
                    'parameters': {'x': 3.0, 'y': 1.0, 'z': 0.0},
                    'confidence': 0.85
                }
            elif 'living room' in command_lower:
                return {
                    'action': 'navigate_to', 
                    'parameters': {'x': 0.0, 'y': 0.0, 'z': 0.0},
                    'confidence': 0.80
                }
            else:
                return {
                    'action': 'navigate_to',
                    'parameters': {'x': 1.0, 'y': 0.0, 'z': 0.0},  # Default forward
                    'confidence': 0.70
                }
        
        elif 'pick up' in command_lower or 'grasp' in command_lower or 'get' in command_lower:
            # Extract object to pick up
            obj_type = self.extract_object_type(command_lower)
            return {
                'action': 'grasp_object',
                'parameters': {'object_type': obj_type},
                'confidence': 0.82
            }
        
        elif 'put down' in command_lower or 'release' in command_lower or 'drop' in command_lower:
            return {
                'action': 'release_object',
                'parameters': {},
                'confidence': 0.88
            }
        
        elif 'find' in command_lower or 'detect' in command_lower or 'look for' in command_lower:
            obj_type = self.extract_object_type(command_lower)
            return {
                'action': 'detect_object',
                'parameters': {'object_type': obj_type},
                'confidence': 0.78
            }
        
        else:
            return None  # Could not understand
    
    def extract_object_type(self, command: str) -> str:
        """Extract object type from command"""
        # Simple keyword extraction
        common_objects = ['cup', 'book', 'chair', 'table', 'ball', 'box', 'phone', 'laptop']
        for obj in common_objects:
            if obj in command:
                return obj
        return 'object'  # Default
    
    def plan_task(self, intent: Dict[str, Any], context: Dict[str, Any]):
        """Plan a task based on intent and context"""
        # This would be replaced with actual planning algorithm
        # For demo, return simple plans based on action type
        
        action_type = intent['action']
        
        if action_type == 'navigate_to':
            # For navigation, just move to the specified location
            return {
                'steps': [
                    {
                        'action': 'perceive_environment',  # Check environment first
                        'parameters': {}
                    },
                    {
                        'action': 'navigate_to',
                        'parameters': intent['parameters']  # Use the parameters from intent
                    }
                ]
            }
        
        elif action_type == 'grasp_object':
            # For grasping, we need to navigate to object, perceive it, then grasp
            return {
                'steps': [
                    {
                        'action': 'perceive_environment',
                        'parameters': {}
                    },
                    {
                        'action': 'detect_object',
                        'parameters': {'object_type': intent['parameters']['object_type']}
                    },
                    {
                        'action': 'navigate_to_object',
                        'parameters': {'object_type': intent['parameters']['object_type']}
                    },
                    {
                        'action': 'grasp_object',
                        'parameters': intent['parameters']
                    }
                ]
            }
        
        elif action_type == 'detect_object':
            return {
                'steps': [
                    {
                        'action': 'perceive_environment',
                        'parameters': {}
                    },
                    {
                        'action': 'detect_object',
                        'parameters': intent['parameters']
                    }
                ]
            }
        
        elif action_type == 'release_object':
            return {
                'steps': [
                    {
                        'action': 'release_object',
                        'parameters': {}
                    }
                ]
            }
        
        else:
            return {'steps': []}  # Unknown action requires no steps


class MockMotionController:
    """Mock motion controller for demonstration"""
    
    def __init__(self, node):
        self.node = node
        self.current_position = [0.0, 0.0, 0.0]  # x, y, z position
    
    def navigate_to_location(self, x: float, y: float, z: float) -> bool:
        """Navigate to a specific location (simulated)"""
        self.node.get_logger().info(f"Simulating navigation to ({x}, {y}, {z})")
        
        # Simulate navigation with occasional failures
        import random
        success = random.random() > 0.1  # 90% success rate
        
        if success:
            # Update position after "navigation"
            self.current_position = [x, y, z]
            self.node.get_logger().info(f"Successfully navigated to ({x}, {y}, {z})")
        else:
            self.node.get_logger().error(f"Failed to navigate to ({x}, {y}, {z})")
        
        return success
    
    def grasp_object(self, object_id: str) -> bool:
        """Grasp an object (simulated)"""
        self.node.get_logger().info(f"Attempting to grasp object: {object_id}")
        
        import random
        success = random.random() > 0.2  # 80% success rate
        self.node.get_logger().info(f"Grasp {'successful' if success else 'failed'} for {object_id}")
        return success
    
    def release_object(self) -> bool:
        """Release held object (simulated)"""
        self.node.get_logger().info("Releasing held object")
        return True
    
    def manipulate_object(self, action: str, object_id: str) -> bool:
        """Manipulate an object (simulated)"""
        self.node.get_logger().info(f"Manipulating {object_id} with action: {action}")
        return True
    
    def move_to_safe_position(self):
        """Move robot to a safe position"""
        self.node.get_logger().info("Moving to safe position")
        # Move to (0, 0, 0.85) which is a typical standing position
        self.current_position = [0.0, 0.0, 0.85]
    
    def emergency_stop(self):
        """Emergency stop all motion"""
        self.node.get_logger().info("Emergency stop commanded")
    
    def attempt_navigation_recovery(self, failed_action: Dict[str, Any]) -> bool:
        """Attempt to recover from navigation failure"""
        self.node.get_logger().info("Attempting navigation recovery")
        return True  # In mock, recovery always succeeds
    
    def attempt_grasp_recovery(self, failed_action: Dict[str, Any]) -> bool:
        """Attempt to recover from grasp failure"""
        self.node.get_logger().info("Attempting grasp recovery")
        return True  # In mock, recovery always succeeds


class MockVoiceInterface:
    """Mock voice interface for demonstration"""
    
    def __init__(self, node):
        self.node = node
    
    def speak_response(self, text: str):
        """Speak a response to the user"""
        self.node.get_logger().info(f"Speaking: {text}")
        return True
    
    def start_listening(self):
        """Start listening for voice commands"""
        self.node.get_logger().info("Voice interface initialized")
        return True


def main(args=None):
    """Main entry point for the humanoid pipeline"""
    rclpy.init(args=args)
    
    pipeline_node = HumanoidPipeline()
    
    try:
        rclpy.spin(pipeline_node)
    except KeyboardInterrupt:
        pipeline_node.get_logger().info("Humanoid pipeline shutting down...")
    finally:
        pipeline_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Cognitive Planning Integration

### Natural Language to Robot Actions Translation

```python
# cognitive_planner.py
from typing import Dict, Any, List, Optional
import json
import logging
import openai
import os
from dataclasses import dataclass


@dataclass
class Intent:
    """Represents an intent extracted from natural language"""
    action_type: str
    parameters: Dict[str, Any]
    confidence: float
    original_command: str


@dataclass
class TaskStep:
    """A single step in a task plan"""
    action: str
    parameters: Dict[str, Any]
    preconditions: List[str]
    effects: List[str]
    priority: int = 0


class CognitivePlanner:
    """Translates natural language commands to robotic action plans"""
    
    def __init__(self, node):
        self.node = node
        self.logger = logging.getLogger(__name__)
        
        # Domain knowledge base
        self.object_knowledge = {
            'cup': {
                'properties': ['drinkable', 'graspable', 'movable'],
                'typical_locations': ['kitchen_counter', 'table', 'cabinet'],
                'grasp_requirements': ['top_grasp', 'no_spill']
            },
            'book': {
                'properties': ['readable', 'graspable', 'movable', 'information_source'],
                'typical_locations': ['shelf', 'table', 'desk'],
                'grasp_requirements': ['edge_grasp', 'horizontal_support']
            },
            'chair': {
                'properties': ['sit_on', 'obstacle', 'large'],
                'typical_locations': ['dining_area', 'desk'],
                'grasp_requirements': ['push_only']
            }
        }
        
        # Action knowledge base
        self.action_knowledge = {
            'navigate_to': {
                'preconditions': ['robot_is_mobile'],
                'effects': ['robot_at_location'],
                'parameters': ['x', 'y', 'z', 'location_name']
            },
            'grasp_object': {
                'preconditions': ['object_in_reach', 'object_graspable'],
                'effects': ['robot_holds_object'],
                'parameters': ['object_id', 'grasp_type']
            },
            'release_object': {
                'preconditions': ['robot_holds_object'],
                'effects': ['object_released'],
                'parameters': ['location']
            },
            'detect_object': {
                'preconditions': ['visual_sensor_active'],
                'effects': ['object_detection_result'],
                'parameters': ['object_type', 'search_area']
            }
        }
    
    def understand_command(self, command: str, context: Dict[str, Any]) -> Optional[Intent]:
        """Use LLM to understand the command"""
        
        prompt = f"""
        You are a natural language understanding system for a humanoid robot.
        Given the user's command, identify the intended action and extract relevant parameters.
        
        Current world knowledge:
        - Robot position: {context.get('robot_pose', 'unknown')}
        - Visible objects: {context.get('world_model', {}).get('objects_detected', [])}
        - Known locations: kitchen, living room, bedroom, office
        
        User command: "{command}"
        
        Respond with a JSON object containing:
        {{
            "action_type": "the specific action the robot should take",
            "parameters": {{"param1": "value1", "param2": "value2"}},
            "confidence": "float between 0.0 and 1.0 indicating how confident you are in your interpretation"
        }}
        
        Choose action from: navigate_to, go_to_location, detect_object, find_object, 
        grasp_object, pick_up, place_down, release_object, manipulate_object, 
        walk_to, move_to, turn_to, speak_response, answer_question
        
        Be as specific as possible with parameters.
        If the command is unclear, set action_type to "unknown" and confidence low.
        """
        
        try:
            # Initialize OpenAI client if available
            if os.getenv("OPENAI_API_KEY"):
                client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a natural language understanding system for a humanoid robot. Identify robot actions from user commands."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,  # Low temperature for more deterministic output
                    max_tokens=256
                )
                
                response_text = response.choices[0].message.content
                
                # Extract JSON from response
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                
                if json_start != -1 and json_end > json_start:
                    json_str = response_text[json_start:json_end]
                    parsed_response = json.loads(json_str)
                    return Intent(**parsed_response, original_command=command)
                else:
                    self.logger.error(f"Could not extract JSON from LLM response: {response_text}")
                    return None
            else:
                # Fallback to keyword-based parsing if no API key is available
                return self.keyword_based_understanding(command)
        
        except Exception as e:
            self.logger.error(f"Error in understand_command: {e}")
            return None
    
    def keyword_based_understanding(self, command: str) -> Optional[Intent]:
        """Fallback understanding method when LLM is not available"""
        command_lower = command.lower()
        
        if any(keyword in command_lower for keyword in ['navigate', 'go to', 'move to', 'walk to']):
            # Extract location information
            if 'kitchen' in command_lower:
                return Intent('navigate_to', {'location_name': 'kitchen', 'x': 3.0, 'y': 1.0, 'z': 0.0}, 0.75, command)
            elif 'living room' in command_lower or 'living' in command_lower:
                return Intent('navigate_to', {'location_name': 'living_room', 'x': 0.0, 'y': 0.0, 'z': 0.0}, 0.75, command)
            elif 'bedroom' in command_lower:
                return Intent('navigate_to', {'location_name': 'bedroom', 'x': -2.0, 'y': 1.5, 'z': 0.0}, 0.75, command)
            elif 'office' in command_lower:
                return Intent('navigate_to', {'location_name': 'office', 'x': -1.0, 'y': -1.0, 'z': 0.0}, 0.75, command)
            else:
                # Could not determine specific location
                return Intent('unknown', {}, 0.3, command)
        
        elif any(keyword in command_lower for keyword in ['pick up', 'grasp', 'get', 'take', 'catch']):
            # Extract object to pick up
            object_type = self.extract_object_type(command_lower)
            return Intent('grasp_object', {'object_type': object_type}, 0.70, command)
        
        elif any(keyword in command_lower for keyword in ['put down', 'release', 'drop', 'place']):
            # Release object command
            return Intent('release_object', {}, 0.85, command)
        
        elif any(keyword in command_lower for keyword in ['find', 'detect', 'locate', 'search for']):
            # Find object command
            object_type = self.extract_object_type(command_lower)
            return Intent('detect_object', {'object_type': object_type}, 0.78, command)
        
        elif any(keyword in command_lower for keyword in ['turn', 'rotate']):
            # Turn command
            if 'left' in command_lower:
                return Intent('turn_to', {'direction': 'left', 'angle': 90}, 0.80, command)
            elif 'right' in command_lower:
                return Intent('turn_to', {'direction': 'right', 'angle': 90}, 0.80, command)
            else:
                return Intent('turn_to', {'direction': 'any', 'angle': 90}, 0.65, command)
        
        else:
            # Could not understand command
            return Intent('unknown', {}, 0.2, command)
    
    def extract_object_type(self, command: str) -> str:
        """Extract object type from command using simple keyword matching"""
        # Known objects in the environment
        known_objects = ['cup', 'book', 'ball', 'chair', 'table', 'box', 'phone', 'laptop', 'pen', 'bottle']
        
        for obj in known_objects:
            if obj in command:
                return obj
        
        # If no known object found, try to infer from context
        if 'something' in command or 'thing' in command:
            return 'object'
        elif 'it' in command:
            return 'target_object'  # Would need to resolve from context in real implementation
        
        return 'unknown_object'
    
    def plan_task(self, intent: Intent, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a task plan based on intent and context"""
        if intent.action_type == 'unknown':
            return None
        
        # Use planning algorithm to create action sequence
        plan = {
            'intent': intent,
            'steps': [],
            'cost': 0.0,
            'estimated_duration': 0.0,
            'success_probability': intent.confidence
        }
        
        if intent.action_type in ['navigate_to', 'go_to_location']:
            plan['steps'] = self.plan_navigation_task(intent, context)
        elif intent.action_type in ['grasp_object', 'pick_up']:
            plan['steps'] = self.plan_grasping_task(intent, context)
        elif intent.action_type in ['release_object', 'place_down']:
            plan['steps'] = self.plan_release_task(intent, context)
        elif intent.action_type in ['detect_object', 'find_object']:
            plan['steps'] = self.plan_detection_task(intent, context)
        elif intent.action_type == 'turn_to':
            plan['steps'] = self.plan_turning_task(intent, context)
        else:
            plan['steps'] = [TaskStep(
                action=intent.action_type,
                parameters=intent.parameters,
                preconditions=[],
                effects=[]
            )]
        
        # Calculate plan metrics
        plan['cost'] = len(plan['steps']) * 10.0  # Simplified cost model
        plan['estimated_duration'] = len(plan['steps']) * 2.0  # 2 seconds per step average
        
        return plan
    
    def plan_navigation_task(self, intent: Intent, context: Dict[str, Any]) -> List[TaskStep]:
        """Plan navigation task"""
        steps = []
        
        # Check current position and target
        current_pos = context.get('robot_pose', {}).get('position', {'x': 0, 'y': 0, 'z': 0})
        target_pos = intent.parameters
        
        # Add perception step to update environment map
        steps.append(TaskStep(
            action='perceive_environment',
            parameters={},
            preconditions=[],
            effects=['environment_map_updated']
        ))
        
        # Add navigation action
        steps.append(TaskStep(
            action='navigate_to',
            parameters=target_pos,
            preconditions=['environment_map_updated'],
            effects=['robot_at_destination']
        ))
        
        return steps
    
    def plan_grasping_task(self, intent: Intent, context: Dict[str, Any]) -> List[TaskStep]:
        """Plan grasping task with multiple steps"""
        steps = []
        
        object_type = intent.parameters.get('object_type', 'unknown')
        
        # Check if object is already known to be in environment
        known_objects = context.get('world_model', {}).get('objects_detected', [])
        
        if object_type not in known_objects:
            # First detect the object if not known
            steps.append(TaskStep(
                action='detect_object',
                parameters={'object_type': object_type},
                preconditions=[],
                effects=['object_position_known']
            ))
        else:
            # Object is already known, can use cached location
            steps.append(TaskStep(
                action='lookup_object_position',
                parameters={'object_type': object_type},
                preconditions=[],
                effects=['object_position_known']
            ))
        
        # Navigate to object
        steps.append(TaskStep(
            action='navigate_to_object',
            parameters={'object_type': object_type},
            preconditions=['object_position_known'],
            effects=['robot_at_object', 'object_in_reach']
        ))
        
        # Grasp the object
        steps.append(TaskStep(
            action='grasp_object',
            parameters={
                'object_type': object_type,
                'grasp_type': self.select_grasp_type(object_type)
            },
            preconditions=['robot_at_object', 'object_in_reach'],
            effects=['object_grasped', 'robot_holds_object']
        ))
        
        return steps
    
    def select_grasp_type(self, object_type: str) -> str:
        """Select appropriate grasp type based on object type"""
        if object_type in ['book', 'plate']:
            return 'edge_grasp'
        elif object_type in ['cup', 'bottle']:
            return 'top_grasp'
        elif object_type in ['ball']:
            return 'spherical_grasp'
        else:
            return 'power_grasp'
    
    def plan_release_task(self, intent: Intent, context: Dict[str, Any]) -> List[TaskStep]:
        """Plan object release task"""
        steps = []
        
        # If location is specified, navigate there first
        location = intent.parameters.get('location')
        if location:
            steps.append(TaskStep(
                action='navigate_to',
                parameters=location,
                preconditions=[],
                effects=['robot_at_release_location']
            ))
        
        # Release the object
        steps.append(TaskStep(
            action='release_object',
            parameters={},
            preconditions=['robot_holds_object'],
            effects=['object_released', 'robot_hands_free']
        ))
        
        return steps
    
    def plan_detection_task(self, intent: Intent, context: Dict[str, Any]) -> List[TaskStep]:
        """Plan object detection task"""
        steps = []
        
        object_type = intent.parameters.get('object_type', 'unknown')
        
        # Perception step
        steps.append(TaskStep(
            action='perceive_environment',
            parameters={},
            preconditions=[],
            effects=['environment_perceived']
        ))
        
        # Object detection step
        steps.append(TaskStep(
            action='detect_object',
            parameters={'object_type': object_type},
            preconditions=['environment_perceived'],
            effects=['object_detected']
        ))
        
        # If object needs to be approached after detection
        if intent.original_command.contains('approach'):
            steps.append(TaskStep(
                action='navigate_to_object',
                parameters={'object_type': object_type},
                preconditions=['object_detected'],
                effects=['robot_near_object']
            ))
        
        return steps
    
    def plan_turning_task(self, intent: Intent, context: Dict[str, Any]) -> List[TaskStep]:
        """Plan turning task"""
        steps = []
        
        steps.append(TaskStep(
            action='turn_in_place',
            parameters=intent.parameters,
            preconditions=[],
            effects=['facing_desired_direction']
        ))
        
        return steps


class TaskExecutor:
    """Executes planned tasks in a controlled manner"""
    
    def __init__(self, node):
        self.node = node
        self.current_task = None
        self.task_queue = []
    
    def execute_plan(self, plan: Dict[str, Any]) -> bool:
        """Execute a complete plan"""
        steps = plan.get('steps', [])
        
        success = True
        for i, step in enumerate(steps):
            self.node.get_logger().info(f"Executing step {i+1}/{len(steps)}: {step.action}")
            
            step_success = self.execute_step(step)
            
            if not step_success:
                self.node.get_logger().error(f"Step {i+1} failed: {step.action}")
                success = False
                break
        
        return success
    
    def execute_step(self, step: TaskStep) -> bool:
        """Execute a single task step"""
        # This method would interface with the actual motion control system
        # For now, simulate execution
        
        action = step.action
        params = step.parameters
        
        self.node.get_logger().info(f"Executing action: {action} with params: {params}")
        
        # Simulate different actions
        if action == 'navigate_to':
            result = self.simulate_navigation(params)
        elif action == 'grasp_object':
            result = self.simulate_grasping(params)
        elif action in ['release_object', 'place_down']:
            result = True  # Simulate success
        elif action == 'detect_object':
            result = self.simulate_detection(params)
        elif action == 'perceive_environment':
            result = self.simulate_perception()
        else:
            # For other actions, simulate success
            import random
            result = random.random() > 0.1  # 90% success rate
        
        return result
    
    def simulate_navigation(self, params: Dict[str, Any]) -> bool:
        """Simulate navigation action"""
        # In a real system, this would interface with navigation stack
        import time
        time.sleep(1.0)  # Simulate navigation time
        
        # 95% success rate for navigation
        import random
        return random.random() > 0.05
    
    def simulate_grasping(self, params: Dict[str, Any]) -> bool:
        """Simulate grasping action"""
        # In a real system, this would interface with manipulation stack
        import time
        time.sleep(1.5)  # Simulate grasp planning and execution time
        
        # Success depends on object type and grasp type
        obj_type = params.get('object_type', 'unknown')
        grasp_type = params.get('grasp_type', 'default')
        
        # Different success rates for different objects
        success_rates = {
            'cup': 0.85,
            'book': 0.80,
            'ball': 0.90,
            'unknown': 0.70
        }
        
        base_success_rate = success_rates.get(obj_type, 0.75)
        
        # 90% success rate for grasping
        import random
        return random.random() < base_success_rate
    
    def simulate_detection(self, params: Dict[str, Any]) -> bool:
        """Simulate object detection"""
        import time
        time.sleep(0.5)  # Simulate processing time
        
        # 95% success rate for detection in simulation
        import random
        return random.random() < 0.95
    
    def simulate_perception(self) -> bool:
        """Simulate perception action"""
        import time
        time.sleep(0.2)  # Simulate perception processing time
        return True  # Perception always succeeds in simulation