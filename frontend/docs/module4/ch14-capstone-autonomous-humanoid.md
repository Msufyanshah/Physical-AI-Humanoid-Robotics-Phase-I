---
title: 'Chapter 14 - Capstone: Autonomous Humanoid Pipeline'
description: 'Complete pipeline for autonomous humanoid robot control with all components integrated'
---

# Chapter 14: Capstone: Autonomous Humanoid Pipeline

## Learning Objectives

After reading this chapter, you will be able to:
- Integrate all previous modules into a complete, functioning humanoid autonomy pipeline
- Implement robust error handling and recovery mechanisms across all components
- Design and implement a cohesive system architecture connecting perception, planning, and action
- Optimize the complete system for real-time performance
- Validate the integrated system against required specifications
- Implement comprehensive testing procedures for the complete system
- Deploy and operate the full humanoid robot system
- Plan for system maintenance and future enhancements

## Introduction

The capstone chapter integrates all the components developed throughout the course into a complete autonomous humanoid robot pipeline. This pipeline enables natural language interaction with a humanoid robot that can perceive its environment, plan complex multi-step tasks, and execute physical actions in the real world. The system represents the culmination of our journey through Physical AI and Humanoid Robotics.

## Complete System Architecture

### High-Level System Design

The complete autonomy pipeline consists of multiple interconnected layers:

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                  USER INTERFACE                                                 │
│                                    (Voice Commands, Mobile App, Physical Gestures)                              │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                            NATURAL LANGUAGE UNDERSTANDING                                        │
│                          (Speech Recognition, Intent Classification, Context Management)                      │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                  COGNITIVE PLANNING                                             │
│              (Task Decomposition, Path Planning, Manipulation Planning, Multi-Step Coordination)                │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                   PERCEPTION SYSTEM                                               │
│               (Vision Processing, LiDAR, IMU, Audio Processing, Sensor Fusion, State Estimation)              │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                MOTION CONTROL SYSTEM                                              │
│                  (Whole-Body Control, Balance Control, Trajectory Generation, Joint Control)                   │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                    HARDWARE LAYER                                                 │
│                                 (Motors, Sensors, Electronics, Mechanical Components)                          │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

This architecture enables seamless operation from high-level commands ("Go to the kitchen and bring me the red cup") to low-level motor commands.

### Component Integration

The key to successful integration lies in proper interface design between components:

1. **Message Passing**: Using ROS 2 topics and services for communication
2. **State Synchronization**: Maintaining consistent world and robot state across modules
3. **Timing Coordination**: Ensuring real-time performance with appropriate update rates
4. **Error Propagation**: Proper handling and communication of failures between modules

## Implementation of the Complete Pipeline

### Main System Orchestrator

```python
# system_orchestrator.py
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped
from sensor_msgs.msg import JointState
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
import threading
import time
import json
from enum import Enum
from typing import Dict, Any, Optional, List
import asyncio
import logging


class SystemState(Enum):
    """Enumeration of system operational states"""
    IDLE = "idle"
    LISTENING = "listening"
    UNDERSTANDING = "understanding_command"
    PLANNING = "planning_task"
    EXECUTING = "executing_plan"
    MONITORING = "monitoring_execution"
    SAFETY_INTERVENTION = "safety_intervention"
    EMERGENCY_STOP = "emergency_stop"
    RECOVERY = "recovery_mode"


class HumanoidSystemOrchestrator(Node):
    """Main orchestrator for the complete humanoid robot autonomy system"""
    
    def __init__(self):
        super().__init__('humanoid_system_orchestrator')
        
        # Initialize state
        self.system_state = SystemState.IDLE
        self.active_plan = None
        self.current_intent = None
        self.robot_state = {
            'position': {'x': 0.0, 'y': 0.0, 'z': 0.0},
            'orientation': {'x': 0.0, 'y': 0.0, 'z': 0.0, 'w': 1.0},
            'joints': {},
            'battery_level': 1.0,
            'safety_status': 'nominal'
        }
        self.world_model = {}
        
        # Initialize components
        self.initialize_components()
        
        # Create publishers and subscribers
        self.status_publisher = self.create_publisher(String, '/system_status', 10)
        self.command_subscriber = self.create_subscription(String, '/high_level_commands', self.command_callback, 10)
        self.state_subscriber = self.create_subscription(Odometry, '/odom', self.state_callback, 10)
        self.joint_subscriber = self.create_subscription(JointState, '/joint_states', self.joint_callback, 10)
        
        # Create service clients
        self.setup_service_clients()
        
        # Create timers for system monitoring and state updates
        self.status_timer = self.create_timer(1.0, self.publish_status)
        self.monitor_timer = self.create_timer(0.1, self.monitor_system_state)
        
        self.get_logger().info("Humanoid System Orchestrator initialized")
    
    def initialize_components(self):
        """Initialize all system components"""
        try:
            from src.modules.perception import PerceptionSystem
            from src.modules.planning import CognitivePlanner
            from src.modules.control import MotionController
            from src.modules.communication import VoiceInterface
            
            self.perception_system = PerceptionSystem(self)
            self.cognitive_planner = CognitivePlanner(self)
            self.motion_controller = MotionController(self)
            self.voice_interface = VoiceInterface(self)
            
            self.get_logger().info("All system components initialized successfully")
            
        except ImportError as e:
            self.get_logger().error(f"Failed to import system components: {e}")
            self.get_logger().info("Using mock components for demonstration")
            
            # Create mock components for demonstration
            self.perception_system = MockPerceptionSystem(self)
            self.cognitive_planner = MockCognitivePlanner(self)
            self.motion_controller = MockMotionController(self)
            self.voice_interface = MockVoiceInterface(self)
    
    def setup_service_clients(self):
        """Set up service clients for various system services"""
        # This would include clients for navigation, manipulation, etc.
        # For now, just placeholder
        pass
    
    def command_callback(self, msg: String):
        """Process high-level commands from user interface"""
        try:
            # Parse command message
            command_data = json.loads(msg.data)
            command_text = command_data.get('command', '')
            source = command_data.get('source', 'unknown')
            priority = command_data.get('priority', 'normal')
            
            self.get_logger().info(f"Received {priority} priority command from {source}: '{command_text}'")
            
            # Update system state
            self.system_state = SystemState.UNDERSTANDING
            self.publish_status()
            
            # Process command through the full pipeline
            success = self.process_command_through_pipeline(command_text, priority)
            
            if success:
                self.get_logger().info(f"Command '{command_text}' completed successfully")
            else:
                self.get_logger().error(f"Command '{command_text}' failed to execute")
                
        except json.JSONDecodeError:
            self.get_logger().error(f"Invalid JSON in command: {msg.data}")
        except Exception as e:
            self.get_logger().error(f"Error processing command: {e}")
    
    def process_command_through_pipeline(self, command: str, priority: str = 'normal') -> bool:
        """Process a command through the complete autonomy pipeline"""
        try:
            # Step 1: Natural Language Understanding
            self.system_state = SystemState.UNDERSTANDING
            self.get_logger().info(f"Understanding command: {command}")
            
            intent = self.cognitive_planner.understand_command(command, self.get_world_context())
            if not intent or intent.confidence < 0.5:
                self.get_logger().error(f"Could not understand command: {command}")
                self.voice_interface.speak("I didn't understand that command. Could you please rephrase it?")
                return False
            
            self.current_intent = intent
            self.get_logger().info(f"Understood intent: {intent.action_type} with confidence {intent.confidence}")
            
            # Step 2: Task Planning
            self.system_state = SystemState.PLANNING
            self.get_logger().info(f"Planning task for intent: {intent.action_type}")
            
            plan = self.cognitive_planner.plan_task(intent, self.get_world_context())
            if not plan:
                self.get_logger().error(f"Could not generate plan for intent: {intent.action_type}")
                self.voice_interface.speak("I can't perform that task right now.")
                return False
            
            self.active_plan = plan
            self.get_logger().info(f"Generated plan with {len(plan.steps)} steps")
            
            # Step 3: Plan Execution
            self.system_state = SystemState.EXECUTING
            self.get_logger().info("Beginning plan execution")
            
            success = self.execute_plan_with_monitoring(plan)
            
            # Step 4: Result Reporting
            if success:
                self.voice_interface.speak("Task completed successfully!")
                self.get_logger().info("Task completed successfully")
            else:
                self.voice_interface.speak("I couldn't complete that task. Is there something else I can do?")
                self.get_logger().error("Task execution failed")
            
            # Clear active plan and intent
            self.active_plan = None
            self.current_intent = None
            
            # Return to IDLE state
            self.system_state = SystemState.IDLE
            
            return success
            
        except Exception as e:
            self.get_logger().error(f"Error in command pipeline: {e}")
            self.voice_interface.speak("I encountered an error processing your command.")
            self.system_state = SystemState.EMERGENCY_STOP
            return False
    
    def get_world_context(self) -> Dict[str, Any]:
        """Get current world and robot state for planning"""
        return {
            'robot_state': self.robot_state,
            'world_model': self.world_model,
            'environment_map': self.perception_system.get_environment_map() if hasattr(self.perception_system, 'get_environment_map') else {},
            'current_time': self.get_clock().now().nanoseconds / 1e9
        }
    
    def execute_plan_with_monitoring(self, plan: Dict[str, Any]) -> bool:
        """Execute plan while monitoring for failures and safety issues"""
        for step_idx, step in enumerate(plan['steps']):
            self.get_logger().info(f"Executing step {step_idx+1}/{len(plan['steps'])}: {step['action']}")
            
            # Check for safety issues before executing each step
            if not self.check_pre_execution_safety(step):
                self.get_logger().error(f"Safety check failed for step {step_idx+1}, aborting plan")
                return False
            
            # Execute the step
            step_success = self.execute_single_step(step)
            
            if not step_success:
                self.get_logger().error(f"Step {step_idx+1} failed: {step['action']}")
                
                # Attempt recovery
                recovery_success = self.attempt_step_recovery(step, step_idx, plan)
                
                if not recovery_success:
                    self.get_logger().error("Recovery failed, aborting plan")
                    return False
            
            # Update world model based on step execution
            self.update_world_model_from_step_result(step, step_success)
            
            # Check for safety issues after executing step
            if not self.check_post_execution_safety():
                self.get_logger().warn("Safety issue detected after step execution")
                return False
        
        # Plan completed successfully
        return True
    
    def execute_single_step(self, step: Dict[str, Any]) -> bool:
        """Execute a single step in the plan"""
        action_type = step['action']
        parameters = step.get('parameters', {})
        
        try:
            if action_type == 'navigate_to_location':
                return self.motion_controller.navigate_to(
                    x=parameters.get('x', 0.0),
                    y=parameters.get('y', 0.0),
                    z=parameters.get('z', 0.0)
                )
            elif action_type == 'grasp_object':
                return self.motion_controller.grasp_object(
                    object_type=parameters.get('object_type', 'unknown'),
                    position=parameters.get('position')
                )
            elif action_type == 'release_object':
                return self.motion_controller.release_object()
            elif action_type == 'detect_object':
                return self.perception_system.detect_object(
                    object_type=parameters.get('object_type', 'unknown')
                )
            elif action_type == 'turn_in_place':
                return self.motion_controller.turn_to_angle(
                    angle=parameters.get('angle', 0.0),
                    direction=parameters.get('direction', 'relative')
                )
            elif action_type == 'speak_response':
                self.voice_interface.speak(parameters.get('text', 'Task completed'))
                return True  # Speaking always succeeds
            else:
                self.get_logger().warn(f"Unknown action type: {action_type}")
                return False
                
        except Exception as e:
            self.get_logger().error(f"Error executing action {action_type}: {e}")
            return False
    
    def check_pre_execution_safety(self, step: Dict[str, Any]) -> bool:
        """Check safety conditions before executing a step"""
        # Check battery level
        if self.robot_state['battery_level'] &lt; 0.15:
            self.get_logger().warn("Low battery level (<15%), stopping operation")
            return False
        
        # Check for obstacles in navigation path
        if step['action'] == 'navigate_to_location':
            path_clear = self.check_navigation_path_clear(step.get('parameters', {}))
            if not path_clear:
                self.get_logger().warn("Navigation path has obstacles, stopping operation")
                return False
        
        # Check joint limits before manipulation
        if step['action'] in ['grasp_object', 'manipulate_object']:
            within_limits = self.check_manipulation_feasibility(step.get('parameters', {}))
            if not within_limits:
                self.get_logger().warn("Manipulation would exceed joint limits")
                return False
        
        return True
    
    def check_navigation_path_clear(self, params: Dict[str, Any]) -> bool:
        """Check if navigation path is clear of obstacles"""
        # In a real system, this would check the path against the map
        # For this implementation, return True
        return True
    
    def check_manipulation_feasibility(self, params: Dict[str, Any]) -> bool:
        """Check if manipulation is feasible given current state"""
        # Check if manipulation would exceed joint limits
        # In a real system, this would involve inverse kinematics
        return True
    
    def check_post_execution_safety(self) -> bool:
        """Check safety conditions after executing a step"""
        # Check if robot is in a safe configuration
        # Check if robot fell or lost balance
        # Check if joints are still within safe limits
        
        # For this example, return True (assume safe)
        return True
    
    def attempt_step_recovery(self, failed_step: Dict[str, Any], step_idx: int, plan: Dict[str, Any]) -> bool:
        """Attempt to recover from a failed step"""
        action_type = failed_step['action']
        
        if action_type == 'navigate_to':
            # Try alternative path or adjust parameters
            return self.motion_controller.attempt_navigation_recovery(failed_step)
        elif action_type == 'grasp_object':
            # Try different grasp approach or position
            return self.motion_controller.attempt_grasp_recovery(failed_step)
        elif action_type == 'detect_object':
            # Try different viewpoint or increase detection range
            return self.perception_system.attempt_detection_recovery(failed_step)
        else:
            # For other failures, try a simple retry
            self.get_logger().info(f"Retrying step: {action_type}")
            return self.execute_single_step(failed_step)
    
    def state_callback(self, msg: Odometry):
        """Update robot state from odometry"""
        pose = msg.pose.pose
        twist = msg.twist.twist
        
        self.robot_state['position'] = {
            'x': pose.position.x,
            'y': pose.position.y,
            'z': pose.position.z
        }
        
        self.robot_state['orientation'] = {
            'x': pose.orientation.x,
            'y': pose.orientation.y,
            'z': pose.orientation.z,
            'w': pose.orientation.w
        }
    
    def joint_callback(self, msg: JointState):
        """Update joint state"""
        for i, name in enumerate(msg.name):
            if i &lt; len(msg.position):
                self.robot_state['joints'][name] = {
                    'position': msg.position[i],
                    'velocity': msg.velocity[i] if i &lt; len(msg.velocity) else 0.0,
                    'effort': msg.effort[i] if i &lt; len(msg.effort) else 0.0
                }
    
    def monitor_system_state(self):
        """Monitor system state for issues"""
        if self.system_state != SystemState.IDLE:
            # Monitor active processes
            if self.system_state == SystemState.EXECUTING and self.active_plan:
                progress = self.get_plan_progress()
                if progress < 0:  # Error in progress calculation
                    self.get_logger().error("Plan execution progress error, stopping")
                    self.system_state = SystemState.EMERGENCY_STOP
                    self.motion_controller.emergency_stop()
            elif self.system_state in [SystemState.SAFETY_INTERVENTION, SystemState.EMERGENCY_STOP]:
                # System is in an unsafe state, stay there until resolved
                self.get_logger().warn(f"System in {self.system_state.value} state")
    
    def get_plan_progress(self) -> float:
        """Get current plan execution progress"""
        if not self.active_plan:
            return -1  # No active plan
        
        total_steps = len(self.active_plan.get('steps', []))
        if total_steps == 0:
            return 1.0  # No steps means complete
        
        # In a real implementation, this would track which steps have been completed
        # For now, return a placeholder based on time
        return 0.5  # Placeholder
    
    def publish_status(self):
        """Publish system status"""
        status_msg = String()
        status_data = {
            'state': self.system_state.value,
            'active_plan': bool(self.active_plan),
            'battery_level': self.robot_state['battery_level'],
            'safety_status': self.robot_state['safety_status'],
            'current_intent': self.current_intent.action_type if self.current_intent else None,
            'timestamp': self.get_clock().now().seconds_nanoseconds()
        }
        status_msg.data = json.dumps(status_data)
        self.status_publisher.publish(status_msg)
    
    def emergency_stop_procedure(self):
        """Execute emergency stop procedure"""
        self.get_logger().warn("Emergency stop procedure initiated!")
        
        # Stop all motion
        self.motion_controller.emergency_stop()
        
        # Publish emergency status
        emergency_status = String()
        emergency_status.data = json.dumps({
            'state': 'emergency_stop',
            'reason': 'manual_emergency_stop',
            'timestamp': self.get_clock().now().seconds_nanoseconds()
        })
        self.status_publisher.publish(emergency_status)
        
        # Update system state
        self.system_state = SystemState.EMERGENCY_STOP
    
    def update_world_model_from_step_result(self, step: Dict[str, Any], success: bool):
        """Update world model based on step execution result"""
        # Update the world model with results from step execution
        # For example, if we successfully grasped an object, update object state
        # If we navigated to a location, update robot position in world model
        pass
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health metrics"""
        return {
            'system_state': self.system_state.value,
            'uptime': (self.get_clock().now().nanoseconds / 1e9) - self.start_time,
            'total_commands_processed': self.total_commands_processed,
            'success_rate': self.successful_commands / max(1, self.total_commands_processed),
            'components_health': {
                'perception': self.perception_system.health_check() if hasattr(self, 'perception_system') else 'unknown',
                'planning': self.cognitive_planner.health_check() if hasattr(self, 'cognitive_planner') else 'unknown',
                'control': self.motion_controller.health_check() if hasattr(self, 'motion_controller') else 'unknown',
                'communication': self.voice_interface.health_check() if hasattr(self, 'voice_interface') else 'unknown'
            }
        }

# ROS 2 entry point
def main(args=None):
    rclpy.init(args=args)
    
    orchestrator = HumanoidSystemOrchestrator()
    
    try:
        # Run the system
        rclpy.spin(orchestrator)
    except KeyboardInterrupt:
        orchestrator.get_logger().info("System orchestrator shutting down...")
    finally:
        # Cleanup
        orchestrator.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Performance Optimization

### Real-Time Performance Considerations

For the complete system to operate in real-time, optimization is critical:

```python
# performance_optimizer.py
import time
import threading
from collections import deque
import numpy as np
import psutil
import GPUtil
from dataclasses import dataclass
from typing import Dict, Any, Callable, Optional


@dataclass
class PerformanceMetrics:
    """Container for performance metrics"""
    processing_time: float
    cpu_usage: float
    memory_usage: float
    timestamp: float
    component: str


class SystemPerformanceOptimizer:
    """Class to optimize the performance of the complete humanoid system"""
    
    def __init__(self, node):
        self.node = node
        self.metrics_history = {
            'perception': deque(maxlen=50),
            'planning': deque(maxlen=50),
            'control': deque(maxlen=50),
            'communication': deque(maxlen=50)
        }
        
        self.target_frequencies = {
            'perception': 30,  # Hz
            'planning': 10,   # Hz
            'control': 100,   # Hz for reactive control
            'communication': 10  # Hz for command processing
        }
        
        self.adaptation_callbacks = {
            'perception': self.adapt_perception_frequency,
            'planning': self.adapt_planning_frequency,
            'control': self.adapt_control_frequency,
            'communication': self.adapt_communication_frequency
        }
        
        # Performance monitoring timer
        self.performance_timer = self.node.create_timer(2.0, self.monitor_performance)
        
        self.node.get_logger().info("System Performance Optimizer initialized")
    
    def monitor_performance(self):
        """Monitor system performance and adjust as needed"""
        
        # Get system metrics
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent
        
        # Get GPU usage if available
        gpu_percent = 0
        gpus = GPUtil.getGPUs()
        if gpus:
            gpu_percent = gpus[0].load * 100
        
        # Calculate average processing times
        avg_processing_times = {}
        for component, metrics in self.metrics_history.items():
            if metrics:
                times = [m.processing_time for m in metrics]
                avg_processing_times[component] = sum(times) / len(times)
            else:
                avg_processing_times[component] = 0
        
        # Log performance metrics
        performance_summary = {
            'cpu_usage': cpu_percent,
            'memory_usage': memory_percent,
            'gpu_usage': gpu_percent,
            'avg_processing_times': avg_processing_times
        }
        
        self.node.get_logger().info(f"Performance: {performance_summary}")
        
        # Check if components are running within their time budgets
        for component, avg_time in avg_processing_times.items():
            target_freq = self.target_frequencies[component]
            time_budget = 1.0 / target_freq  # Time budget per cycle in seconds
            
            if avg_time > time_budget * 0.8:  # Using 80% of time budget
                self.node.get_logger().warn(f"{component} is exceeding performance budget: {avg_time:.3f}s > {time_budget * 0.8:.3f}s")
                
                # Call adaptation callback to reduce computational load
                if component in self.adaptation_callbacks:
                    self.adaptation_callbacks[component]()
    
    def record_component_performance(self, component: str, start_time: float, end_time: float):
        """Record performance metrics for a component"""
        metric = PerformanceMetrics(
            processing_time=end_time - start_time,
            cpu_usage=psutil.cpu_percent(),
            memory_usage=psutil.virtual_memory().percent,
            timestamp=time.time(),
            component=component
        )
        self.metrics_history[component].append(metric)
    
    def adapt_perception_frequency(self):
        """Adapt perception system to reduce computational load"""
        # This might reduce the frequency of perception processing
        # or simplify the perception algorithms
        self.node.get_logger().warn("Adapting perception system for performance")
        
        # Example: Reduce perception frequency temporarily
        # Or enable a fast perception mode that skips some processing
        pass
    
    def adapt_planning_frequency(self):
        """Adapt planning system to reduce computational load"""
        self.node.get_logger().warn("Adapting planning system for performance")
        
        # Example: Use faster but less optimal planning algorithm
        # Or use simpler motion models
        pass
    
    def adapt_control_frequency(self):
        """Adapt control system to reduce computational load"""
        self.node.get_logger().warn("Adapting control system for performance")
        
        # Example: Reduce controller complexity
        # Or use predictive control with longer prediction horizons to reduce computation
        pass
    
    def adapt_communication_frequency(self):
        """Adapt communication system to reduce computational load"""
        self.node.get_logger().warn("Adapting communication system for performance")
        
        # Example: Reduce voice processing frequency if needed
        # Or aggregate multiple commands before processing
        pass


class PerceptionOptimizer:
    """Specific optimizer for the perception system"""
    
    def __init__(self, perception_system):
        self.perception_system = perception_system
        self.optimization_levels = ['low', 'medium', 'high']  # Performance vs. accuracy trade-offs
        self.current_level = 'medium'
        
    def optimize_for_performance(self):
        """Optimize perception pipeline for performance"""
        if self.current_level == 'high':
            # Switch to medium optimization level
            self.current_level = 'medium'
            self.apply_performance_optimizations()
        elif self.current_level == 'medium':
            # Switch to low optimization level (more aggressive optimization)
            self.current_level = 'low'
            self.apply_aggressive_optimizations()
    
    def apply_performance_optimizations(self):
        """Apply moderate performance optimizations"""
        # Reduce image resolution
        self.perception_system.set_camera_resolution('medium')
        
        # Use faster but less accurate detection models
        self.perception_system.use_fast_detection_models()
        
        # Increase detection thresholds to reduce processing
        self.perception_system.set_detection_threshold(0.6)  # Previously 0.7
    
    def apply_aggressive_optimizations(self):
        """Apply aggressive performance optimizations"""
        # Further reduce image resolution
        self.perception_system.set_camera_resolution('low')
        
        # Skip some perception steps
        self.perception_system.skip_3d_processing = True
        
        # Increase detection thresholds significantly
        self.perception_system.set_detection_threshold(0.8)
        
        # Reduce processing frequency
        self.perception_system.set_processing_frequency(10)  # Down from 30Hz


class PlanningOptimizer:
    """Specific optimizer for the planning system"""
    
    def __init__(self, planning_system):
        self.planning_system = planning_system
        self.optimization_mode = 'balanced'  # 'accuracy', 'speed', or 'balanced'
    
    def optimize_for_real_time(self):
        """Optimize planning for real-time execution"""
        if self.optimization_mode == 'balanced':
            self.optimization_mode = 'speed'
            self.apply_speed_optimizations()
        elif self.optimization_mode == 'speed':
            # Already optimized for speed, nothing more to do
            pass
    
    def apply_speed_optimizations(self):
        """Apply optimizations that prioritize speed over accuracy"""
        # Use greedy planning instead of optimal planning
        self.planning_system.use_greedy_planner = True
        
        # Reduce planning horizon
        self.planning_system.planning_horizon = 20  # Reduced from default
        
        # Use simplified world model for planning
        self.planning_system.use_simplified_model = True


class ControlOptimizer:
    """Specific optimizer for the control system"""
    
    def __init__(self, control_system):
        self.control_system = control_system
    
    def optimize_control_performance(self):
        """Optimize control system for performance"""
        # Use simpler control laws
        self.control_system.use_pd_only = True  # Skip more complex control terms
        
        # Reduce control frequency if safe to do so
        # (only for non-critical controllers)
        if self.control_system.is_non_critical():
            self.control_system.set_frequency(50)  # Reduced from 100Hz
