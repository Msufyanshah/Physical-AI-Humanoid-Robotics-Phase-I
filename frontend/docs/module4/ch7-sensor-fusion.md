---
title: 'Exercise Set 4 - Vision-Language-Action (VLA) Systems'
description: 'Capstone exercises integrating vision, language, and action systems'
---

# Exercise Set 4: Vision-Language-Action (VLA) Systems

## Learning Objectives

After completing these exercises, you will be able to:
- Integrate vision-language-action systems for complete tasks
- Implement advanced perception-action loops for humanoid robots
- Create end-to-end pipelines from natural language to robotic action
- Validate and test complete humanoid autonomy systems
- Optimize performance across the entire VLA pipeline
- Design error handling and recovery for integrated systems
- Deploy and operate complete humanoid robot systems
- Evaluate system performance and identify improvement areas

## Exercise 1: Complete VLA Pipeline Implementation

Create a complete Vision-Language-Action pipeline that processes a complex command from voice to physical action.

### Instructions

1. Implement a complete pipeline that:
   - Takes a voice command: "Go to the kitchen and bring me the red cup from the table"
   - Converts speech to text using Whisper
   - Understands the command using an LLM
   - Plans the multi-step task (navigate, detect object, grasp, return)
   - Executes the plan with proper error handling
   - Monitors execution and provides feedback

2. Integrate all system components:
   - Natural language understanding
   - Task planning
   - Perception (object detection, localization)
   - Navigation
   - Manipulation
   - Execution monitoring

3. Implement proper state management throughout the pipeline.

4. Add error recovery mechanisms for common failure points.

5. Test the complete pipeline with various scenarios.

### Solution Implementation

#### Complete VLA Pipeline

```python
# vla_pipeline_demo.py
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
from geometry_msgs.msg import Pose, Point
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Image, JointState
from builtin_interfaces.msg import Duration
import json
import threading
import asyncio
from typing import Dict, Any, Optional, List


class VLAPipelineDemo(Node):
    """Complete Vision-Language-Action pipeline demonstration"""
    
    def __init__(self):
        super().__init__('vla_pipeline_demo')
        
        # Initialize system components
        self.initialize_pipeline_components()
        
        # Command sequence tracking
        self.command_sequence = [
            {"command": "navigate_to_kitchen", "params": {"location": "kitchen"}},
            {"command": "detect_red_cup", "params": {"object_type": "cup", "color": "red"}},
            {"command": "navigate_to_cup", "params": {"object_id": "red_cup"}},
            {"command": "grasp_cup", "params": {"object_id": "red_cup"}},
            {"command": "return_to_user", "params": {"location": "user_position"}}
        ]
        
        # State tracking
        self.pipeline_state = {
            'is_running': False,
            'current_step': 0,
            'world_state': {},
            'execution_history': []
        }
        
        # Publishers and subscribers
        self.command_pub = self.create_publisher(String, '/high_level_commands', 10)
        self.status_pub = self.create_publisher(String, '/vla_pipeline_status', 10)
        self.feedback_pub = self.create_publisher(String, '/vla_feedback', 10)
        
        # Timer for pipeline execution
        self.pipeline_timer = self.create_timer(0.1, self.pipeline_execution_step)
        
        self.get_logger().info("VLA Pipeline Demo initialized")
    
    def initialize_pipeline_components(self):
        """Initialize all components of the VLA pipeline"""
        try:
            from src.modules.communication.voice_interface import VoiceInterface
            from src.modules.planning.cognitive_planner import CognitivePlanner
            from src.modules.perception.perception_system import PerceptionSystem
            from src.modules.control.motion_controller import MotionController
            
            self.voice_interface = VoiceInterface(self)
            self.cognitive_planner = CognitivePlanner(self)
            self.perception_system = PerceptionSystem(self)
            self.motion_controller = MotionController(self)
            
        except ImportError:
            self.get_logger().warn("Using mock components for VLA pipeline")
            self.voice_interface = MockVoiceInterface(self)
            self.cognitive_planner = MockCognitivePlanner(self)
            self.perception_system = MockPerceptionSystem(self)
            self.motion_controller = MockMotionController(self)
    
    def start_vla_demo(self, command: str = "Go to the kitchen and bring me the red cup from the table"):
        """Start the VLA pipeline demo with a command"""
        self.get_logger().info(f"Starting VLA pipeline demo with command: '{command}'")
        
        # Update pipeline state
        self.pipeline_state['is_running'] = True
        self.pipeline_state['current_step'] = 0
        self.pipeline_state['execution_history'] = []
        
        # Process the command through the full pipeline
        asyncio.run(self.process_command_full_pipeline(command))
    
    async def process_command_full_pipeline(self, command: str):
        """Process a command through the complete VLA pipeline"""
        try:
            # Step 1: Natural Language Understanding (Language component)
            self.get_logger().info("Step 1: Natural Language Understanding")
            self.update_status("Processing natural language command", "language")
            
            intent = self.cognitive_planner.understand_command(command, self.get_world_context())
            if not intent:
                self.get_logger().error(f"Could not understand command: {command}")
                self.provide_feedback(f"Sorry, I didn't understand that command: '{command}'")
                self.pipeline_state['is_running'] = False
                return
            
            self.get_logger().info(f"Identified intent: {intent.action_type}")
            
            # Step 2: Task Planning (Cognitive component)
            self.get_logger().info("Step 2: Task Planning")
            self.update_status("Planning complex task", "planning")
            
            plan = self.cognitive_planner.plan_task(intent, self.get_world_context())
            if not plan:
                self.get_logger().error(f"Could not plan task for intent: {intent.action_type}")
                self.provide_feedback("I cannot perform that task right now.")
                self.pipeline_state['is_running'] = False
                return
            
            self.get_logger().info(f"Generated plan with {len(plan['steps'])} steps")
            
            # Step 3: Execution with Perception Integration (Vision/Action component)
            self.get_logger().info("Step 3: Executing plan with perception integration")
            self.update_status("Executing plan with perception integration", "execution")
            
            success = await self.execute_perception_action_loop(plan)
            
            if success:
                self.get_logger().info("VLA pipeline completed successfully!")
                self.provide_feedback("I've completed the task successfully!")
            else:
                self.get_logger().error("VLA pipeline execution failed")
                self.provide_feedback("I couldn't complete the task. Something went wrong.")
                
        except Exception as e:
            self.get_logger().error(f"Error in VLA pipeline: {e}")
            self.provide_feedback(f"An error occurred: {str(e)}")
        finally:
            self.pipeline_state['is_running'] = False
            self.update_status("VLA pipeline completed", "idle")
    
    async def execute_perception_action_loop(self, plan: Dict[str, Any]) -> bool:
        """Execute the plan with perception-action integration"""
        
        for step_idx, step in enumerate(plan.get('steps', [])):
            self.get_logger().info(f"Executing step {step_idx+1}/{len(plan['steps'])}: {step['action']}")
            
            # Update status
            self.update_status(f"Step {step_idx+1}: {step['action']}", "executing")
            
            # Execute the step
            step_success = await self.execute_single_step_with_perception(step)
            
            # Record execution result
            self.pipeline_state['execution_history'].append({
                'step_index': step_idx,
                'action': step['action'],
                'parameters': step.get('parameters', {}),
                'success': step_success,
                'timestamp': self.get_clock().now().seconds_nanoseconds()
            })
            
            if not step_success:
                self.get_logger().error(f"Step {step_idx+1} failed: {step['action']}")
                
                # Attempt recovery
                recovery_success = await self.attempt_recovery(step, step_idx, plan)
                
                if not recovery_success:
                    return False  # Fail the entire pipeline
            
            # Small delay between steps for safety
            await asyncio.sleep(0.5)
        
        return True  # All steps completed successfully
    
    async def execute_single_step_with_perception(self, step: Dict[str, Any]) -> bool:
        """Execute a single step, integrating perception as needed"""
        action_type = step['action']
        parameters = step.get('parameters', {})
        
        try:
            # Handle perception-dependent actions
            if action_type in ['detect_object', 'find_object', 'locate_object']:
                # Use perception system to find objects
                perception_result = await self.perception_system.detect_and_localize_object(
                    object_type=parameters.get('object_type', 'unknown'),
                    color=parameters.get('color', 'any')
                )
                
                if perception_result:
                    # Update world state with detection results
                    self.update_world_state({
                        'detected_objects': {parameters['object_type']: perception_result}
                    })
                    return True
                else:
                    return False
            
            elif action_type == 'navigate_to':
                # Check if we need perception data for navigation
                if 'object_id' in parameters:
                    # Navigate to detected object
                    obj_pose = self.get_object_position(parameters['object_id'])
                    if obj_pose:
                        success = await self.motion_controller.navigate_to_pose(obj_pose)
                        return success
                    else:
                        self.get_logger().warn(f"Object {parameters['object_id']} not found in world model")
                        return False
                else:
                    # Navigate to specified coordinates
                    success = await self.motion_controller.navigate_to(
                        x=parameters.get('x', 0),
                        y=parameters.get('y', 0),
                        z=parameters.get('z', 0)
                    )
                    return success
            
            elif action_type == 'grasp_object':
                # Grasp a detected object
                obj_data = self.get_object_details(parameters['object_id'])
                if obj_data:
                    success = await self.motion_controller.grasp_object(
                        object_id=parameters['object_id'],
                        grasp_type=self.select_grasp_type(obj_data)
                    )
                    return success
                else:
                    self.get_logger().warn(f"Cannot grasp unknown object: {parameters['object_id']}")
                    return False
            
            elif action_type == 'release_object':
                # Release held object
                return await self.motion_controller.release_object()
            
            else:
                # Execute other actions directly
                return await self.execute_direct_action(step)
        
        except Exception as e:
            self.get_logger().error(f"Error executing step {action_type}: {e}")
            return False
    
    def select_grasp_type(self, object_data: Dict[str, Any]) -> str:
        """Select appropriate grasp type based on object properties"""
        shape = object_data.get('shape', 'unknown')
        size = object_data.get('size', {})
        
        if shape == 'cylinder' and size.get('diameter', 0) < 0.1:
            return 'top_grasp'
        elif shape == 'rectangular':
            return 'edge_grasp'
        elif shape == 'sphere':
            return 'spherical_grasp'
        else:
            return 'power_grasp'
    
    async def attempt_recovery(self, failed_step: Dict[str, Any], step_idx: int, plan: Dict[str, Any]) -> bool:
        """Attempt to recover from a failed step"""
        action_type = failed_step['action']
        
        self.get_logger().warn(f"Attempting recovery for failed step: {action_type}")
        
        if action_type == 'detect_object':
            # Try different viewpoint or increase detection parameters
            return await self.perception_system.recover_detection_failure(failed_step)
        
        elif action_type == 'navigate_to':
            # Try alternative path or different approach
            return await self.motion_controller.recover_navigation_failure(failed_step)
        
        elif action_type == 'grasp_object':
            # Try different grasp approach or re-localize object
            return await self.motion_controller.recover_grasp_failure(failed_step)
        
        else:
            # For other failures, we might need to replan the task
            self.get_logger().info("Replanning remaining tasks due to failure")
            remaining_plan = plan['steps'][step_idx+1:]
            recovery_plan = await self.cognitive_planner.replan_tasks(remaining_plan, self.get_world_context())
            
            if recovery_plan:
                # Execute the recovery plan
                return await self.execute_perception_action_loop(recovery_plan)
            else:
                return False
    
    def update_world_state(self, updates: Dict[str, Any]):
        """Update the world state with new information"""
        self.pipeline_state['world_state'].update(updates)
    
    def get_object_position(self, object_id: str) -> Optional[Dict[str, float]]:
        """Get position of a detected object from world state"""
        obj_data = self.pipeline_state['world_state'].get('detected_objects', {}).get(object_id)
        if obj_data and 'position' in obj_data:
            return obj_data['position']
        
        return None
    
    def get_object_details(self, object_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a detected object"""
        obj_data = self.pipeline_state['world_state'].get('detected_objects', {}).get(object_id)
        return obj_data
    
    def get_world_context(self) -> Dict[str, Any]:
        """Get current world context for planning"""
        return {
            'robot_state': self.get_robot_state(),
            'world_model': self.pipeline_state['world_state'],
            'environment_map': self.get_environment_map(),
            'current_time': self.get_clock().now().seconds_nanoseconds()
        }
    
    def get_robot_state(self) -> Dict[str, Any]:
        """Get current robot state (placeholder)"""
        return {
            'position': {'x': 0.0, 'y': 0.0, 'z': 0.0},
            'orientation': {'x': 0.0, 'y': 0.0, 'z': 0.0, 'w': 1.0},
            'battery_level': 0.85,
            'available_actions': ['navigate', 'grasp', 'release', 'detect']
        }
    
    def get_environment_map(self) -> Dict[str, Any]:
        """Get environment map (placeholder)"""
        return {
            'known_locations': {
                'kitchen': {'x': 3.0, 'y': 1.0, 'z': 0.0},
                'living_room': {'x': 0.0, 'y': 0.0, 'z': 0.0},
                'office': {'x': -1.0, 'y': 1.5, 'z': 0.0}
            },
            'obstacles': [],
            'free_spaces': ['kitchen', 'living_room']
        }
    
    def update_status(self, status: str, stage: str):
        """Update pipeline status"""
        status_msg = String()
        status_data = {
            'status': status,
            'stage': stage,
            'step': self.pipeline_state['current_step'],
            'timestamp': self.get_clock().now().seconds_nanoseconds()
        }
        status_msg.data = json.dumps(status_data)
        self.status_pub.publish(status_msg)
    
    def provide_feedback(self, text: str):
        """Provide feedback to the user"""
        feedback_msg = String()
        feedback_msg.data = json.dumps({
            'type': 'feedback',
            'text': text,
            'timestamp': self.get_clock().now().seconds_nanoseconds()
        })
        self.feedback_pub.publish(feedback_msg)
        
        # Speak feedback if voice system is available
        if hasattr(self, 'voice_interface'):
            self.voice_interface.speak(text)
    
    def execute_direct_action(self, step: Dict[str, Any]) -> bool:
        """Execute a direct action in the system"""
        # This would call the appropriate system component based on the action
        action_type = step['action']
        params = step.get('parameters', {})
        
        if action_type == 'speak':
            text = params.get('text', 'Task completed')
            self.provide_feedback(text)
            return True
        elif action_type == 'wait':
            duration = params.get('duration', 1.0)
            time.sleep(duration)
            return True
        else:
            # For unknown actions, just report success
            self.get_logger().warn(f"Unknown action type: {action_type}")
            return True


class MockVoiceInterface:
    """Mock voice interface for demonstration purposes"""
    
    def __init__(self, node):
        self.node = node
        self.latest_command = None
    
    def start_listening(self):
        """Start listening for voice commands"""
        pass
    
    def get_latest_command(self):
        """Get the latest command (for demonstration)"""
        return self.latest_command
    
    def speak(self, text: str):
        """Speak text to user"""
        self.node.get_logger().info(f"Speaking: {text}")


class MockCognitivePlanner:
    """Mock cognitive planner for demonstration"""
    
    def __init__(self, node):
        self.node = node
    
    def understand_command(self, command: str, context: Dict[str, Any]):
        """Understand a natural language command (mock)"""
        import random
        
        # Simulate understanding with some success rate
        if random.random() > 0.1:  # 90% success rate
            if 'kitchen' in command.lower():
                return MockIntent('navigate_to', {'location': 'kitchen'}, 0.9)
            elif 'red cup' in command.lower():
                return MockIntent('detect_object', {'object_type': 'cup', 'color': 'red'}, 0.85)
            elif 'grasp' in command.lower() or 'pick' in command.lower():
                return MockIntent('grasp_object', {'object_id': 'red cup'}, 0.8)
            elif 'bring' in command.lower() or 'return' in command.lower():
                return MockIntent('navigate_to', {'location': 'user'}, 0.88)
            else:
                return MockIntent('unknown', {}, 0.3)
        else:
            return None
    
    def plan_task(self, intent, context):
        """Plan a task based on intent (mock)"""
        # Create a simple plan based on intent type
        if intent.action_type == 'navigate_to':
            return {
                'steps': [
                    {'action': 'perceive_environment'},
                    {'action': 'plan_path', 'parameters': intent.parameters},
                    {'action': 'execute_navigation', 'parameters': intent.parameters}
                ]
            }
        elif intent.action_type == 'detect_object':
            return {
                'steps': [
                    {'action': 'turn_to', 'parameters': {'angle': 90}},
                    {'action': 'scan_environment'},
                    {'action': 'detect_object', 'parameters': intent.parameters}
                ]
            }
        elif intent.action_type == 'grasp_object':
            return {
                'steps': [
                    {'action': 'perceive_environment'},
                    {'action': 'calculate_grasp_pose', 'parameters': intent.parameters},
                    {'action': 'execute_grasp', 'parameters': intent.parameters}
                ]
            }
        elif intent.action_type == 'unknown':
            return None
        else:
            return {'steps': [{'action': intent.action_type, 'parameters': intent.parameters}]}


class MockPerceptionSystem:
    """Mock perception system for demonstration"""
    
    def __init__(self, node):
        self.node = node
        self.detected_objects = {
            'cup': {'position': {'x': 3.2, 'y': 1.1, 'z': 0.8}, 'color': 'red', 'shape': 'cylinder', 'size': {'diameter': 0.08, 'height': 0.1}}
        }
    
    async def detect_and_localize_object(self, object_type: str, color: str = 'any'):
        """Detect and localize an object (mock)"""
        import random
        time.sleep(0.3)  # Simulate processing time
        
        if random.random() > 0.2:  # 80% success rate
            if object_type in self.detected_objects:
                if color == 'any' or self.detected_objects[object_type].get('color') == color:
                    return self.detected_objects[object_type]
        
        return None
    
    async def recover_detection_failure(self, failed_step):
        """Recover from detection failure"""
        # Try different detection approach
        return await self.detect_and_localize_object(
            failed_step.get('parameters', {}).get('object_type', 'unknown')
        )


class MockMotionController:
    """Mock motion controller for demonstration"""
    
    def __init__(self, node):
        self.node = node
    
    async def navigate_to(self, x: float, y: float, z: float):
        """Navigate to a position (mock)"""
        import time
        import random
        
        time.sleep(1.0)  # Simulate navigation time
        
        # 95% success rate
        return random.random() > 0.05
    
    async def navigate_to_pose(self, pose: Dict[str, float]):
        """Navigate to a pose (mock)"""
        import time
        import random
        
        time.sleep(1.0)  # Simulate navigation time
        
        # 95% success rate
        return random.random() > 0.05
    
    async def grasp_object(self, object_id: str, grasp_type: str):
        """Grasp an object (mock)"""
        import time
        import random
        
        time.sleep(1.5)  # Simulate grasp planning and execution time
        
        # 90% grasp success rate
        return random.random() > 0.1
    
    async def release_object(self):
        """Release the currently held object (mock)"""
        import time
        import random
        
        time.sleep(0.5)  # Simulate release action
        
        # 99% release success rate
        return random.random() > 0.01
    
    async def recover_navigation_failure(self, failed_step):
        """Recover from navigation failure"""
        # Simulate alternative path calculation
        import time
        time.sleep(0.5)
        
        # Try simpler navigation
        return await self.navigate_to(2.0, 1.0, 0.0)
    
    async def recover_grasp_failure(self, failed_step):
        """Recover from grasp failure"""
        # Try different grasp approach
        import time
        time.sleep(0.5)
        
        return await self.grasp_object(failed_step.get('parameters', {}).get('object_id', 'unknown'), 'power_grasp')


class MockIntent:
    """Mock intent class for demonstration"""
    def __init__(self, action_type: str, parameters: Dict[str, Any], confidence: float):
        self.action_type = action_type
        self.parameters = parameters
        self.confidence = confidence


def main(args=None):
    rclpy.init(args=args)
    node = VLAPipelineDemo()
    
    # Start the demo with a sample command
    node.get_logger().info("Starting VLA Pipeline Demo...")
    
    try:
        # For demo purposes, we'll run the pipeline once with a fixed command
        # In a real system, this would be triggered by user interaction
        node.start_vla_demo("Go to the kitchen and bring me the red cup from the table")
        
        # Run for 30 seconds then stop
        import time
        start_time = time.time()
        while time.time() - start_time < 30 and rclpy.ok():
            rclpy.spin_once(node, timeout_sec=0.1)
        
        node.get_logger().info("VLA Pipeline Demo completed")
        
    except KeyboardInterrupt:
        node.get_logger().info("VLA Pipeline Demo interrupted by user")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### Hints

- Start with a simple command and expand the complexity gradually
- Use proper state management to track the robot's situation
- Implement robust error handling at each step of the pipeline
- Test with various failure scenarios to ensure robustness
- Consider the timing requirements for each component in the pipeline

## Exercise 2: Multi-Modal Perception Integration

Implement a system that fuses information from multiple perception modalities to improve robot awareness.

### Instructions

1. Create a multi-modal perception fusion system that combines:
   - Visual data (RGB and depth)
   - LiDAR data
   - IMU data
   - Joint state data

2. Implement a sensor fusion algorithm that:
   - Estimates object positions using multiple sensors
   - Tracks object movement over time
   - Validates sensor consistency
   - Handles sensor failures gracefully

3. Use the fused perception information to:
   - Improve grasp planning accuracy
   - Enhance navigation safety
   - Enable better manipulation planning

4. Test the system with different environmental conditions.

### Solution

#### Multi-Modal Fusion System

```python
# sensor_fusion.py
import numpy as np
import threading
import time
from typing import Dict, Any, List, Optional
from collections import deque
import statistics


class SensorFusionSystem:
    """Multi-modal sensor fusion for humanoid robot perception"""
    
    def __init__(self, node):
        self.node = node
        
        # Data buffers for different sensors
        self.vision_buffer = deque(maxlen=10)  # Last 10 vision measurements
        self.lidar_buffer = deque(maxlen=10)   # Last 10 LiDAR measurements
        self.imu_buffer = deque(maxlen=50)     # More IMU data for stability
        self.joint_buffer = deque(maxlen=10)   # Joint state data
        
        # Object tracking
        self.tracked_objects = {}  # Dictionary of tracked objects
        self.object_trackers = {}  # Tracking algorithms for each object
        
        # Fusion parameters
        self.confidence_weights = {
            'vision': 0.8,   # High confidence in visual detection when good lighting
            'lidar': 0.9,    # Very high confidence in LiDAR for distance
            'joint_state': 0.95,  # Accurate for self-state
            'imu': 0.7      # Good for orientation but prone to drift
        }
        
        # Object properties
        self.object_properties = {
            'cup': {
                'size': [0.08, 0.08, 0.12],  # width, depth, height in meters
                'color': 'red',
                'graspability': 'high',
                'detection_priority': 1
            },
            'book': {
                'size': [0.2, 0.15, 0.02],
                'color': 'black',
                'graspability': 'medium',
                'detection_priority': 2
            },
            'ball': {
                'size': [0.1, 0.1, 0.1],
                'color': 'blue',
                'graspability': 'high',
                'detection_priority': 3
            }
        }
        
        # Initialize fusion algorithm
        self.fusion_algorithm = ProbabilisticFusion(node)
        
        self.node.get_logger().info("Sensor Fusion System initialized")
    
    def update_vision_data(self, vision_data: Dict[str, Any]):
        """Update with new vision data"""
        self.vision_buffer.append({
            'data': vision_data,
            'timestamp': time.time(),
            'confidence': 0.8  # Default confidence
        })
        
        # Process detected objects
        self.process_vision_objects(vision_data.get('objects_detected', []))
    
    def update_lidar_data(self, lidar_data: Dict[str, Any]):
        """Update with new LiDAR data"""
        self.lidar_buffer.append({
            'data': lidar_data,
            'timestamp': time.time(),
            'confidence': 0.9  # Generally high confidence in LiDAR
        })
        
        # Process obstacles and distances
        self.process_lidar_obstacles(lidar_data.get('obstacles', []))
    
    def update_imu_data(self, imu_data: Dict[str, Any]):
        """Update with new IMU data"""
        self.imu_buffer.append({
            'data': imu_data,
            'timestamp': time.time(),
            'confidence': 0.7  # Confidence varies based on drift
        })
        
        # Update robot orientation and balance estimates
        self.update_balance_estimate(imu_data)
    
    def update_joint_data(self, joint_data: Dict[str, Any]):
        """Update with new joint state data"""
        self.joint_buffer.append({
            'data': joint_data,
            'timestamp': time.time(),
            'confidence': 0.95  # Usually very accurate for self-state
        })
        
        # Update robot kinematic state
        self.update_kinematic_state(joint_data)
    
    def process_vision_objects(self, detected_objects: List[Dict[str, Any]]):
        """Process objects detected in vision data"""
        for obj in detected_objects:
            obj_id = obj['id']
            obj_type = obj['type']
            position = obj['position']  # In camera frame
            confidence = obj['confidence']
            
            # Convert camera frame to world frame
            world_pos = self.camera_frame_to_world(position, self.get_robot_camera_pose())
            
            # Update tracked object or create new tracker
            if obj_id in self.tracked_objects:
                # Update existing tracker
                self.object_trackers[obj_id].update_measurement(world_pos, confidence, 'vision')
            else:
                # Create new tracker
                self.create_object_tracker(obj_id, obj_type, world_pos, confidence)
    
    def process_lidar_obstacles(self, obstacles: List[Dict[str, Any]]):
        """Process obstacles from LiDAR data"""
        for obs in obstacles:
            # Obstacles are typically in robot frame, convert to world frame
            world_pos = self.robot_frame_to_world(obs['position'], self.get_robot_pose())
            
            # Update obstacle tracking (similar to object tracking)
            obs_id = f"obstacle_{obs['position']['x']:.1f}_{obs['position']['y']:.1f}"
            
            if obs_id in self.tracked_objects:
                self.object_trackers[obs_id].update_measurement(world_pos, obs['confidence'], 'lidar')
            else:
                # Create new tracker for this obstacle
                self.create_object_tracker(obs_id, 'obstacle', world_pos, obs['confidence'])
    
    def create_object_tracker(self, obj_id: str, obj_type: str, initial_pos: Dict[str, float], confidence: float):
        """Create a new object tracker"""
        # Use Kalman filter for object tracking
        self.object_trackers[obj_id] = KalmanObjectTracker(
            obj_type=obj_type,
            initial_state=[initial_pos['x'], initial_pos['y'], initial_pos['z'], 0, 0, 0],  # [x, y, z, vx, vy, vz]
            initial_uncertainty=0.1
        )
        
        # Initialize with first measurement
        self.object_trackers[obj_id].update_measurement(
            [initial_pos['x'], initial_pos['y'], initial_pos['z']], 
            confidence,
            'initial'
        )
        
        self.tracked_objects[obj_id] = {
            'type': obj_type,
            'last_seen': time.time(),
            'is_graspable': obj_type in ['cup', 'book', 'ball']
        }
    
    def get_fused_world_model(self) -> Dict[str, Any]:
        """Get the fused world model incorporating all sensor modalities"""
        
        # Create fused world model
        world_model = {
            'objects': {},
            'robot_state': self.get_fused_robot_state(),
            'environment_map': self.get_fused_environment_map(),
            'safe_zones': [],
            'navigable_areas': [],
            'obstacles': []
        }
        
        # Fuse object information
        for obj_id, tracker in self.object_trackers.items():
            estimated_state = tracker.get_estimated_state()
            uncertainty = tracker.get_uncertainty()
            
            world_model['objects'][obj_id] = {
                'position': {
                    'x': float(estimated_state[0]),
                    'y': float(estimated_state[1]),
                    'z': float(estimated_state[2])
                },
                'velocity': {
                    'x': float(estimated_state[3]),
                    'y': float(estimated_state[4]),
                    'z': float(estimated_state[5])
                },
                'uncertainty': float(uncertainty),
                'confidence': self.estimate_confidence_from_uncertainty(uncertainty),
                'type': self.tracked_objects[obj_id]['type'],
                'last_seen': self.tracked_objects[obj_id]['last_seen'],
                'is_graspable': self.tracked_objects[obj_id]['is_graspable']
            }
        
        return world_model
    
    def estimate_confidence_from_uncertainty(self, uncertainty: float) -> float:
        """Convert uncertainty to confidence value"""
        # Convert uncertainty to confidence (inverse relationship)
        confidence = 1.0 - min(uncertainty, 0.9)  # Limit to 0.1 minimum confidence
        return max(0.1, confidence)
    
    def get_fused_robot_state(self) -> Dict[str, Any]:
        """Get fused robot state from all modalities"""
        
        # Get the most recent joint state (highest confidence for self-state)
        if self.joint_buffer:
            latest_joints = self.joint_buffer[-1]
            joint_state = latest_joints['data']
        
        # Get fused orientation from IMU
        fused_orientation = self.estimate_robot_orientation()
        
        # Get fused position from multiple sources
        fused_position = self.estimate_robot_position()
        
        return {
            'position': fused_position,
            'orientation': fused_orientation,
            'joints': joint_state,
            'velocity': self.estimate_robot_velocity()
        }
    
    def estimate_robot_orientation(self) -> Dict[str, float]:
        """Estimate robot orientation from IMU and joint data"""
        
        # For now, return the most recent IMU data
        # In practice, would fuse with kinematic estimate from joint states
        if self.imu_buffer:
            latest_imu = self.imu_buffer[-1]['data']
            return {
                'x': latest_imu['x'],
                'y': latest_imu['y'],
                'z': latest_imu['z'],
                'w': latest_imu['w']
            }
        
        return {'x': 0.0, 'y': 0.0, 'z': 0.0, 'w': 1.0}  # Identity quaternion
    
    def estimate_robot_position(self) -> Dict[str, float]:
        """Estimate robot position using odometry and other sensors"""
        
        # In practice, would use sensor fusion to combine:
        # - Wheel odometry integration
        # - Visual odometry
        # - IMU integration for drift correction
        # - Known landmarks for absolute position correction
        
        # For this demo, return placeholder
        return {'x': 0.0, 'y': 0.0, 'z': 0.0}
    
    def estimate_robot_velocity(self) -> Dict[str, float]:
        """Estimate robot velocity from position changes over time"""
        
        # Calculate from position changes
        # For this demo, return placeholder
        return {'x': 0.0, 'y': 0.0, 'z': 0.0}
    
    def get_fused_environment_map(self) -> Dict[str, Any]:
        """Get fused environment map from multiple sensors"""
        
        # In practice, would create a fused map combining:
        # - LiDAR point clouds
        # - Stereo vision depth estimates
        # - Semantic segmentation from cameras
        # - Occupancy grid updates
        
        return {
            'occupied_cells': [],
            'free_cells': [],
            'unknown_cells': [],
            'semantically_annotated': {}
        }
    
    def handle_sensor_failure(self, sensor_type: str):
        """Handle when a sensor fails"""
        self.node.get_logger().warn(f"Sensor failure detected for {sensor_type}, adjusting fusion weights")
        
        # Reduce confidence weight for failed sensor
        if sensor_type in self.confidence_weights:
            # Set to a low but non-zero value
            self.confidence_weights[sensor_type] = max(0.1, self.confidence_weights[sensor_type] * 0.3)
    
    def validate_sensor_consistency(self) -> List[str]:
        """Validate consistency between sensors"""
        issues = []
        
        # Check if different sensors provide conflicting information
        if self.vision_buffer and self.lidar_buffer:
            # Compare object positions from vision and LiDAR
            vision_objects = self.extract_objects_from_buffer(self.vision_buffer)
            lidar_obstacles = self.extract_objects_from_buffer(self.lidar_buffer)
            
            for v_obj in vision_objects:
                for l_obj in lidar_obstacles:
                    # Check if objects that should be the same have significantly different positions
                    dist = self.calculate_distance_between_objects(v_obj, l_obj)
                    if dist < 0.5:  # Close together (likely same object)
                        # Check if positions are consistent (allowing for sensor noise)
                        position_diff = self.calculate_position_difference(v_obj, l_obj)
                        if position_diff > 0.3:  # More than 30cm difference
                            issues.append(f"Inconsistent position for object {v_obj['id']}: "
                                        f"vision {v_obj['position']}, lidar {l_obj['position']}")
        
        return issues
    
    def extract_objects_from_buffer(self, buffer) -> List[Dict[str, Any]]:
        """Extract objects from a sensor buffer"""
        # For demo purposes, return placeholder
        return []
    
    def calculate_distance_between_objects(self, obj1: Dict[str, Any], obj2: Dict[str, Any]) -> float:
        """Calculate distance between two objects"""
        # Placeholder implementation
        return 0.0
    
    def calculate_position_difference(self, pos1: Dict[str, Any], pos2: Dict[str, Any]) -> float:
        """Calculate position difference between two measurements"""
        # Placeholder implementation
        return 0.0

    def camera_frame_to_world(self, camera_pos: Dict[str, float], camera_pose: Dict[str, Any]) -> Dict[str, float]:
        """Convert camera frame position to world frame"""
        # This would use the robot's current pose and camera mounting position
        # For this example, return the position unchanged
        return camera_pos

    def robot_frame_to_world(self, robot_pos: Dict[str, float], robot_pose: Dict[str, Any]) -> Dict[str, float]:
        """Convert robot frame position to world frame"""
        # This would transform from robot's local frame to world frame
        # using the robot's current pose and orientation
        # For this example, return the position unchanged
        return robot_pos

    def get_robot_pose(self) -> Dict[str, Any]:
        """Get current robot pose"""
        # Placeholder implementation
        return {'x': 0.0, 'y': 0.0, 'z': 0.0, 'qx': 0.0, 'qy': 0.0, 'qz': 0.0, 'qw': 1.0}

    def get_robot_camera_pose(self) -> Dict[str, Any]:
        """Get current robot camera pose"""
        # Placeholder implementation
        return {'x': 0.1, 'y': 0.0, 'z': 0.85, 'qx': 0.0, 'qy': 0.0, 'qz': 0.0, 'qw': 1.0}


class KalmanObjectTracker:
    """Simple Kalman filter for object tracking"""
    
    def __init__(self, obj_type: str, initial_state: List[float], initial_uncertainty: float = 0.1):
        self.obj_type = obj_type
        self.state = np.array(initial_state, dtype=float)  # [x, y, z, vx, vy, vz]
        
        # Covariance matrix (uncertainty in state)
        self.covariance = np.eye(len(initial_state)) * initial_uncertainty
        
        # Process noise (uncertainty in motion model)
        self.process_noise = np.eye(len(initial_state)) * 0.1
        
        # Measurement noise based on sensor type
        self.measurement_noise = {
            'vision': 0.05,  # 5cm uncertainty for vision
            'lidar': 0.02,   # 2cm uncertainty for LiDAR
            'sonar': 0.05,   # 5cm uncertainty for sonar
            'touch': 0.01    # 1cm uncertainty for touch
        }
        
    def update_measurement(self, measurement: List[float], confidence: float, sensor_type: str):
        """Update the tracker with a new measurement"""
        
        # Measurement matrix (we observe position directly)
        H = np.array([
            [1, 0, 0, 0, 0, 0],  # x position
            [0, 1, 0, 0, 0, 0],  # y position
            [0, 0, 1, 0, 0, 0]   # z position
        ])
        
        # Measurement noise based on sensor type and confidence
        R = np.eye(3) * self.measurement_noise.get(sensor_type, 0.05) * (1/confidence)
        
        # Convert to measurement vector
        z = np.array(measurement)
        
        # Calculate Kalman gain
        S = H @ self.covariance @ H.T + R
        K = self.covariance @ H.T @ np.linalg.inv(S)
        
        # Update state and covariance
        y = z - H @ self.state[:3]  # Innovation
        self.state[:3] += K[:, :3] @ y
        self.covariance = (np.eye(len(self.state)) - K @ H) @ self.covariance
    
    def predict(self, dt: float):
        """Predict next state based on motion model"""
        
        # Simple motion model: constant velocity
        # State transition matrix (x_new = x + vx*dt, etc.)
        F = np.array([
            [1, 0, 0, dt, 0, 0],  # x = x + vx*dt
            [0, 1, 0, 0, dt, 0],  # y = y + vy*dt
            [0, 0, 1, 0, 0, dt],  # z = z + vz*dt
            [0, 0, 0, 1, 0, 0],  # vx = vx (constant)
            [0, 0, 0, 0, 1, 0],  # vy = vy (constant)
            [0, 0, 0, 0, 0, 1]   # vz = vz (constant)
        ])
        
        # Predict state and covariance
        self.state = F @ self.state
        self.covariance = F @ self.covariance @ F.T + self.process_noise
    
    def get_estimated_state(self) -> np.ndarray:
        """Get the current estimated state"""
        return self.state.copy()
    
    def get_uncertainty(self) -> float:
        """Get the overall uncertainty in the estimate"""
        return np.sqrt(np.trace(self.covariance))