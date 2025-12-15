---
title: 'Exercise Set 1 - The Robotic Nervous System (ROS 2)'
description: 'Practical exercises to reinforce ROS 2 concepts for humanoid robotics'
---

# Exercise Set 1: The Robotic Nervous System (ROS 2)

## Learning Objectives

After completing these exercises, you will be able to:
- Create and organize ROS 2 packages for humanoid robotics
- Implement and test ROS 2 nodes with proper lifecycle management
- Design message types for humanoid-specific communication
- Implement topics, services, and actions for robotic tasks
- Use parameters for configuring robotic behavior
- Debug and troubleshoot ROS 2 systems
- Create launch files to coordinate multiple nodes
- Integrate with simulation and hardware

## Exercise 1: Humanoid Robot Package Structure

### Problem Statement
Create a proper ROS 2 package structure for a humanoid robot controller with appropriate message types and service definitions.

### Instructions
1. Create a new ROS 2 package named `humanoid_robot_control`
2. Define custom message types for:
   - Joint commands with safety limits
   - Balance state with center of mass information
   - Humanoid status with pose and joint information
3. Define service types for:
   - Walking control (start, stop, adjust parameters)
   - Balance adjustment
4. Set up proper CMakeLists.txt and package.xml files
5. Create a basic node skeleton

### Solution

#### 1. Create the Package
```bash
# Create the package
ros2 pkg create --build-type ament_python humanoid_robot_control --dependencies rclpy std_msgs geometry_msgs sensor_msgs builtin_interfaces
```

#### 2. Create Message Definitions
Create `msg/HumanoidJointCommand.msg`:
```
# Joint commands with safety constraints
string[] names
float64[] positions
float64[] velocities
float64[] efforts
bool[] safety_flags
float64[] position_limits_lower
float64[] position_limits_upper
```

Create `msg/BalanceState.msg`:
```
# Balance state information
geometry_msgs/Vector3 center_of_mass
geometry_msgs/Vector3 zero_moment_point
geometry_msgs/Quaternion orientation
float64[] stability_margin
bool is_balanced
```

Create `msg/HumanoidStatus.msg`:
```
# Comprehensive humanoid status
Header header
geometry_msgs/Pose current_pose
sensor_msgs/JointState joint_state
BalanceState balance_state
float64 battery_level
bool[] joint_limits_exceeded
string[] active_alerts
```

#### 3. Create Service Definitions
Create `srv/WalkingControl.srv`:
```
# Walking control service
string command  # "start", "stop", "adjust_params"
float64 step_frequency
float64 step_height
float64 step_length
---
bool success
string message
float64 actual_speed
```

#### 4. Package.xml
```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>humanoid_robot_control</name>
  <version>0.0.1</version>
  <description>Package for controlling humanoid robot systems</description>
  <maintainer email="support@humanoid.com">Humanoid Team</maintainer>
  <license>Apache License 2.0</license>

  <exec_depend>rclpy</exec_depend>
  <exec_depend>std_msgs</exec_depend>
  <exec_depend>geometry_msgs</exec_depend>
  <exec_depend>sensor_msgs</exec_depend>

  <member_of_group>rosidl_interface_packages</member_of_group>

  <export>
    <build_type>ament_python</build_type>
  </export>
</package>
```

#### 5. CMakeLists.txt
```cmake
cmake_minimum_required(VERSION 3.8)
project(humanoid_robot_control)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclpy REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)

# Add message dependencies
find_package(rosidl_default_generators REQUIRED)
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/HumanoidJointCommand.msg"
  "msg/BalanceState.msg" 
  "msg/HumanoidStatus.msg"
  "srv/WalkingControl.srv"
  DEPENDENCIES geometry_msgs sensor_msgs builtin_interfaces
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
```

#### 6. Basic Node Implementation
Create `humanoid_robot_control/balance_controller.py`:
```python
import rclpy
from rclpy.node import Node
from humanoid_robot_control.msg import BalanceState, HumanoidStatus
from humanoid_robot_control.srv import WalkingControl
from sensor_msgs.msg import JointState
from geometry_msgs.msg import Twist, Pose
import math


class BalanceController(Node):
    """Humanoid balance controller node"""
    
    def __init__(self):
        super().__init__('balance_controller')
        
        # Declare parameters with defaults
        self.declare_parameter('control_frequency', 200)
        self.declare_parameter('stability_threshold', 0.05)
        self.declare_parameter('center_of_pressure_limit', 0.1)
        
        self.control_frequency = self.get_parameter('control_frequency').value
        self.stability_threshold = self.get_parameter('stability_threshold').value
        self.cop_limit = self.get_parameter('center_of_pressure_limit').value
        
        # Publishers
        self.balance_state_pub = self.create_publisher(BalanceState, 'balance_state', 10)
        self.cmd_vel_pub = self.create_publisher(Twist, 'base_velocity_control', 10)
        self.joint_cmd_pub = self.create_publisher(JointState, 'joint_commands', 10)
        
        # Subscribers
        self.joint_state_sub = self.create_subscription(
            JointState, 'joint_states', self.joint_state_callback, 10
        )
        
        self.imu_sub = self.create_subscription(
            Imu, 'imu/data', self.imu_callback, 10
        )
        
        # Services
        self.walking_control_srv = self.create_service(
            WalkingControl, 'walking_control', self.walking_control_callback
        )
        
        # Timers
        self.balance_timer = self.create_timer(
            1.0/self.control_frequency, self.balance_control_loop
        )
        
        # Internal state
        self.current_joint_state = None
        self.current_imu_data = None
        self.is_walking = False
        self.walking_params = {
            'frequency': 1.0,
            'step_height': 0.05,
            'step_length': 0.3
        }
        
        self.get_logger().info("Balance controller initialized")
    
    def joint_state_callback(self, msg):
        """Process joint state messages"""
        self.current_joint_state = msg
        self.update_balance_state()
    
    def imu_callback(self, msg):
        """Process IMU messages"""
        self.current_imu_data = msg
        self.update_balance_state()
    
    def update_balance_state(self):
        """Update internal balance state based on sensor inputs"""
        if self.current_joint_state and self.current_imu_data:
            # Calculate center of mass based on joint positions and model
            # For simplicity, using placeholder calculation
            balance_msg = BalanceState()
            balance_msg.center_of_mass.x = 0.0
            balance_msg.center_of_mass.y = 0.0
            balance_msg.center_of_mass.z = 0.85  # Approx height
            
            # Calculate orientation from IMU
            balance_msg.orientation = self.current_imu_data.orientation
            
            # Calculate ZMP (simplified)
            # In a real system, this would be more complex involving dynamics
            balance_msg.zero_moment_point.x = 0.0  # Placeholder
            balance_msg.zero_moment_point.y = 0.0  # Placeholder
            
            # Estimate stability
            # Simple calculation based on orientation
            roll = self.get_euler_from_quaternion(
                self.current_imu_data.orientation.x,
                self.current_imu_data.orientation.y,
                self.current_imu_data.orientation.z,
                self.current_imu_data.orientation.w
            )[0]
            
            pitch = self.get_euler_from_quaternion(...)[1]  # Similar for pitch
            
            balance_msg.stability_margin = [abs(roll), abs(pitch)]
            balance_msg.is_balanced = abs(roll) < self.stability_threshold and abs(pitch) < self.stability_threshold
            
            # Publish balance state
            self.balance_state_pub.publish(balance_msg)
    
    def balance_control_loop(self):
        """Main balance control loop"""
        if self.current_imu_data and self.current_joint_state:
            balance_msg = self.calculate_balance_correction()
            
            if balance_msg.is_balanced:
                # Publish small corrective motion if needed
                cmd_vel = Twist()
                # Calculate corrective motion based on ZMP error
                self.cmd_vel_pub.publish(cmd_vel)
            else:
                # Implement recovery behavior
                self.recover_balance()
    
    def walking_control_callback(self, request, response):
        """Handle walking control requests"""
        if request.command == "start":
            self.is_walking = True
            self.walking_params['frequency'] = request.step_frequency
            self.walking_params['step_height'] = request.step_height
            self.walking_params['step_length'] = request.step_length
            
            response.success = True
            response.message = "Walking started"
            response.actual_speed = request.step_frequency * request.step_length
        elif request.command == "stop":
            self.is_walking = False
            
            response.success = True
            response.message = "Walking stopped"
            response.actual_speed = 0.0
        elif request.command == "adjust_params":
            self.walking_params['frequency'] = request.step_frequency
            self.walking_params['step_height'] = request.step_height
            self.walking_params['step_length'] = request.step_length
            
            response.success = True
            response.message = "Walking parameters adjusted"
            response.actual_speed = request.step_frequency * request.step_length
        else:
            response.success = False
            response.message = f"Unknown command: {request.command}"
            response.actual_speed = 0.0
        
        return response
    
    def recover_balance(self):
        """Implement balance recovery behavior"""
        self.get_logger().warn("Implementing balance recovery...")
        # In a real implementation, this would call recovery algorithms
        
        # For this exercise, just send a corrective command
        cmd_vel = Twist()
        cmd_vel.linear.x = 0.0
        cmd_vel.angular.z = 0.1  # Small corrective turn
        self.cmd_vel_pub.publish(cmd_vel)
    
    def calculate_balance_correction(self):
        """Calculate balance correction based on current state"""
        balance_msg = BalanceState()
        # Implement balance calculation logic
        return balance_msg
    
    def get_euler_from_quaternion(self, x, y, z, w):
        """Convert quaternion to Euler angles"""
        import math
        # Roll (x-axis rotation)
        sinr_cosp = 2 * (w * x + y * z)
        cosr_cosp = 1 - 2 * (x * x + y * y)
        roll = math.atan2(sinr_cosp, cosr_cosp)

        # Pitch (y-axis rotation)
        sinp = 2 * (w * y - z * x)
        if abs(sinp) >= 1:
            pitch = math.copysign(math.pi / 2, sinp)  # Use 90 degrees if out of range
        else:
            pitch = math.asin(sinp)

        # Yaw (z-axis rotation)
        siny_cosp = 2 * (w * z + x * y)
        cosy_cosp = 1 - 2 * (y * y + z * z)
        yaw = math.atan2(siny_cosp, cosy_cosp)

        return roll, pitch, yaw


def main(args=None):
    rclpy.init(args=args)
    node = BalanceController()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Balance controller shutting down...")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### Hints
- Follow ROS 2 naming conventions for packages, topics, and services
- Use proper data structures from standard message types
- Implement parameter validation and error handling
- Consider safety when designing message types

## Exercise 2: Communication Patterns for Humanoid Robots

### Problem Statement
Implement different communication patterns for coordinating humanoid robot subsystems, including action-based walking control and service-based manipulation.

### Instructions
1. Create action definitions for walking and manipulation tasks
2. Implement action servers for:
   - Walking with feedback on progress
   - Object manipulation with intermediate steps
3. Create action clients to test the servers
4. Implement a coordination node that uses both actions and services
5. Test error handling and recovery in action execution

### Solution

#### 1. Action Definitions
Create `action/Walking.action`:
```
# Goal definition
float64 distance  # Distance to walk in meters
float64 speed     # Walking speed in m/s
string gait_type  # Type of gait to use (e.g., "dynamic", "static", "cautious")

---
# Result definition
bool success
float64 actual_distance
string message

---
# Feedback definition
float64 distance_traveled
float64 speed_actual
string status
bool is_safe
```

Create `action/Manipulation.action`:
```
# Goal definition
string object_name
string target_location
string grasp_type  # "pinch", "power", "precision"

---
# Result definition
bool success
string message
geometry_msgs/Pose final_pose

---
# Feedback definition
string current_stage  # "approaching", "grasping", "lifting", "transporting", "placing"
geometry_msgs/Pose object_pose
float64 progress_percentage
bool is_safe
```

#### 2. Walking Action Server
Create `humanoid_robot_control/walking_action_server.py`:
```python
import rclpy
from rclpy.action import ActionServer, GoalResponse, CancelResponse
from rclpy.node import Node
from humanoid_robot_control.action import Walking
from humanoid_robot_control.msg import BalanceState
import time
import threading


class WalkingActionServer(Node):
    def __init__(self):
        super().__init__('walking_action_server')
        
        self._action_server = ActionServer(
            self,
            Walking,
            'walk_to_goal',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback
        )
        
        # Balance state subscription to monitor safety during walking
        self.balance_sub = self.create_subscription(
            BalanceState, 'balance_state', self.balance_callback, 10
        )
        
        self.current_balance = None
        self.is_walking = False
        self.get_logger().info("Walking action server initialized")
    
    def balance_callback(self, msg):
        """Update current balance state"""
        self.current_balance = msg
    
    def goal_callback(self, goal_request):
        """Accept or reject goals based on robot state"""
        self.get_logger().info(f"Received walking goal: {goal_request.distance}m at {goal_request.speed}m/s")
        
        # Only accept goals if robot is balanced and not already walking
        if self.is_walking:
            self.get_logger().warn("Rejecting walking goal: robot is already walking")
            return GoalResponse.REJECT
        
        if self.current_balance and not self.current_balance.is_balanced:
            self.get_logger().warn("Rejecting walking goal: robot is not balanced")
            return GoalResponse.REJECT
        
        return GoalResponse.ACCEPT
    
    def cancel_callback(self, goal_handle):
        """Handle goal cancellation"""
        self.get_logger().info("Received cancellation request for walking goal")
        return CancelResponse.ACCEPT
    
    async def execute_callback(self, goal_handle):
        """Execute the walking action"""
        self.get_logger().info("Executing walking goal...")
        
        goal = goal_handle.request
        feedback_msg = Walking.Feedback()
        result = Walking.Result()
        
        # Validate inputs
        if goal.distance <= 0 or goal.speed <= 0:
            result.success = False
            result.message = "Invalid goal: distance and speed must be positive"
            goal_handle.abort()
            return result
        
        # Start walking
        self.is_walking = True
        distance_travelled = 0.0
        step_size = 0.1  # 10cm per step
        time_per_step = step_size / goal.speed
        
        steps_needed = int(goal.distance / step_size)
        step_count = 0
        
        try:
            for step in range(steps_needed):
                # Check for cancellation request
                if goal_handle.is_cancel_requested:
                    result.success = False
                    result.message = "Goal canceled"
                    goal_handle.canceled()
                    self.is_walking = False
                    return result
                
                # Check if balance is lost during walking
                if self.current_balance and not self.current_balance.is_balanced:
                    self.get_logger().error("Balance lost during walking, stopping execution")
                    result.success = False
                    result.message = "Balance lost, walking stopped for safety"
                    goal_handle.abort()
                    self.is_walking = False
                    return result
                
                # Update distance traveled
                distance_travelled = min(goal.distance, (step + 1) * step_size)
                
                # Publish feedback
                feedback_msg.distance_traveled = distance_travelled
                feedback_msg.speed_actual = goal.speed
                feedback_msg.status = f"Progress: {distance_travelled:.2f}/{goal.distance:.2f}m"
                feedback_msg.is_safe = bool(self.current_balance.is_balanced if self.current_balance else True)
                
                goal_handle.publish_feedback(feedback_msg)
                
                # Simulate step execution
                time.sleep(time_per_step)
                step_count += 1
            
            # Walking completed successfully
            result.success = True
            result.actual_distance = distance_travelled
            result.message = f"Successfully walked {distance_travelled:.2f} meters"
            goal_handle.succeed()
            
            self.get_logger().info(f"Walking completed: {distance_travelled:.2f} meters")
            
        except Exception as e:
            self.get_logger().error(f"Error during walking execution: {e}")
            result.success = False
            result.message = f"Error during execution: {str(e)}"
            goal_handle.abort()
        finally:
            self.is_walking = False
        
        return result


def main(args=None):
    rclpy.init(args=args)
    server = WalkingActionServer()
    
    try:
        rclpy.spin(server)
    except KeyboardInterrupt:
        server.get_logger().info("Walking action server shutting down...")
    finally:
        server.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

#### 3. Manipulation Action Server
Create `humanoid_robot_control/manipulation_action_server.py`:
```python
import rclpy
from rclpy.action import ActionServer
from rclpy.node import Node
from humanoid_robot_control.action import Manipulation
from humanoid_robot_control.msg import HumanoidStatus
from geometry_msgs.msg import Pose
import time


class ManipulationActionServer(Node):
    def __init__(self):
        super().__init__('manipulation_action_server')
        
        self._action_server = ActionServer(
            self,
            Manipulation,
            'manipulate_object',
            execute_callback=self.execute_callback
        )
        
        # Robot status subscription
        self.status_sub = self.create_subscription(
            HumanoidStatus, 'robot_status', self.status_callback, 10
        )
        
        self.current_status = None
        self.is_manipulating = False
        
        self.get_logger().info("Manipulation action server initialized")
    
    def status_callback(self, msg):
        """Update current robot status"""
        self.current_status = msg
    
    async def execute_callback(self, goal_handle):
        """Execute the manipulation action"""
        self.get_logger().info(f"Executing manipulation: {goal_handle.request.object_name} to {goal_handle.request.target_location}")
        
        goal = goal_handle.request
        feedback_msg = Manipulation.Feedback()
        result = Manipulation.Result()
        
        self.is_manipulating = True
        
        try:
            # Stage 1: Approach object
            feedback_msg.current_stage = "approaching"
            feedback_msg.progress_percentage = 25.0
            feedback_msg.is_safe = True
            goal_handle.publish_feedback(feedback_msg)
            
            # Simulate approaching
            time.sleep(2.0)
            
            # Stage 2: Grasp object
            feedback_msg.current_stage = "grasping"
            feedback_msg.progress_percentage = 50.0
            goal_handle.publish_feedback(feedback_msg)
            
            # Simulate grasping
            time.sleep(1.5)
            
            # Stage 3: Lift object
            feedback_msg.current_stage = "lifting"
            feedback_msg.progress_percentage = 75.0
            goal_handle.publish_feedback(feedback_msg)
            
            # Simulate lifting
            time.sleep(1.0)
            
            # Stage 4: Transport object
            feedback_msg.current_stage = "transporting"
            feedback_msg.progress_percentage = 90.0
            goal_handle.publish_feedback(feedback_msg)
            
            # Simulate transport
            time.sleep(2.0)
            
            # Stage 5: Place object
            feedback_msg.current_stage = "placing"
            feedback_msg.progress_percentage = 95.0
            goal_handle.publish_feedback(feedback_msg)
            
            # Simulate placing
            time.sleep(1.5)
            
            # Finalize
            result.success = True
            result.message = f"Successfully manipulated {goal.object_name} to {goal.target_location}"
            result.final_pose = Pose()  # In practice, would be the final object pose
            goal_handle.succeed()
            
            self.get_logger().info(f"Manipulation completed: {goal.object_name}")
            
        except Exception as e:
            self.get_logger().error(f"Error during manipulation: {e}")
            result.success = False
            result.message = f"Error during execution: {str(e)}"
            result.final_pose = Pose()
            goal_handle.abort()
        finally:
            self.is_manipulating = False
        
        return result


def main(args=None):
    rclpy.init(args=args)
    server = ManipulationActionServer()
    
    try:
        rclpy.spin(server)
    except KeyboardInterrupt:
        server.get_logger().info("Manipulation action server shutting down...")
    finally:
        server.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### Hints
- Use actions for long-running tasks with feedback
- Use services for simple request-response interactions
- Implement proper state management in action servers
- Consider safety checks during long-running operations

## Exercise 3: Coordination and Launch Systems

### Problem Statement
Create a coordination node that manages multiple humanoid subsystems and launch files to start the complete system.

### Instructions
1. Create a main coordinator node that orchestrates walking and manipulation tasks
2. Implement task scheduling with dependency management
3. Create launch files for different operational modes
4. Add monitoring and recovery capabilities to the coordinator
5. Test the complete system with integrated launch

### Solution

#### 1. Coordinator Node
Create `humanoid_robot_control/coordinator.py`:
```python
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from humanoid_robot_control.action import Walking, Manipulation
from humanoid_robot_control.msg import HumanoidStatus, BalanceState
from std_msgs.msg import String
import time
from typing import List, Dict, Any


class HumanoidCoordinator(Node):
    """Main coordinator for humanoid robot operations"""
    
    def __init__(self):
        super().__init__('humanoid_coordinator')
        
        # Action clients
        self.walking_client = ActionClient(self, Walking, 'walk_to_goal')
        self.manipulation_client = ActionClient(self, Manipulation, 'manipulate_object')
        
        # Subscriptions
        self.status_sub = self.create_subscription(
            HumanoidStatus, 'robot_status', self.status_callback, 10
        )
        
        self.balance_sub = self.create_subscription(
            BalanceState, 'balance_state', self.balance_callback, 10
        )
        
        self.command_sub = self.create_subscription(
            String, 'high_level_commands', self.command_callback, 10
        )
        
        # Internal state
        self.current_status = None
        self.current_balance = None
        self.active_goals = {}
        
        # Timer for periodic coordination
        self.coordination_timer = self.create_timer(0.1, self.coordination_loop)
        
        self.get_logger().info("Humanoid coordinator initialized")
    
    def status_callback(self, msg):
        """Update robot status"""
        self.current_status = msg
    
    def balance_callback(self, msg):
        """Update balance state"""
        self.current_balance = msg
    
    def command_callback(self, msg):
        """Process high-level commands"""
        try:
            command = eval(msg.data)  # In practice, use json.loads for safety
            self.get_logger().info(f"Received command: {command['type']}")
            
            if command['type'] == 'fetch_and_carry':
                self.execute_fetch_and_carry(command)
            elif command['type'] == 'navigate_to_location':
                self.execute_navigation(command)
            elif command['type'] == 'inspect_object':
                self.execute_inspection(command)
            else:
                self.get_logger().warn(f"Unknown command type: {command['type']}")
        except Exception as e:
            self.get_logger().error(f"Error processing command: {e}")
    
    def execute_fetch_and_carry(self, command):
        """Execute fetch and carry task"""
        object_name = command['object']
        destination = command['destination']
        
        self.get_logger().info(f"Starting fetch and carry for {object_name} to {destination}")
        
        # First navigate to object location
        if 'object_location' in command:
            nav_goal = Walking.Goal()
            nav_goal.distance = self.calculate_distance_to_object(command['object_location'])
            nav_goal.speed = 0.3
            nav_goal.gait_type = 'dynamic'
            
            self.send_walking_goal(nav_goal, 'navigate_to_object')
        
        # Then perform manipulation once we're at the object
        # This would be done in a callback when navigation completes
    
    def calculate_distance_to_object(self, object_location: Dict[str, float]) -> float:
        """Calculate distance to object from current position"""
        if self.current_status:
            robot_pos = self.current_status.current_pose.position
            dx = robot_pos.x - object_location.get('x', 0)
            dy = robot_pos.y - object_location.get('y', 0)
            dz = robot_pos.z - object_location.get('z', 0)
            return (dx**2 + dy**2 + dz**2)**0.5
        else:
            return 1.0  # Default distance if position unknown
    
    def send_walking_goal(self, goal, goal_id):
        """Send walking goal to action server"""
        if not self.walking_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error("Walking action server not available")
            return False
        
        send_goal_future = self.walking_client.send_goal_async(
            goal,
            feedback_callback=self.walking_feedback_callback
        )
        
        send_goal_future.add_done_callback(
            lambda future: self.walking_goal_response_callback(future, goal_id)
        )
        
        self.active_goals[goal_id] = send_goal_future
        return True
    
    def walking_goal_response_callback(self, future, goal_id):
        """Handle walking goal response"""
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info(f'Walking goal {goal_id} rejected')
            return
        
        self.get_logger().info(f'Walking goal {goal_id} accepted')
        
        get_result_future = goal_handle.get_result_async()
        get_result_future.add_done_callback(
            lambda future: self.walking_result_callback(future, goal_id)
        )
    
    def walking_feedback_callback(self, feedback_msg):
        """Handle walking action feedback"""
        self.get_logger().info(
            f'Walking feedback: {feedback_msg.feedback.status}, '
            f'Distance: {feedback_msg.feedback.distance_traveled:.2f}m'
        )
    
    def walking_result_callback(self, future, goal_id):
        """Handle walking action result"""
        result = future.result().result
        self.get_logger().info(f'Walking result for {goal_id}: {result.success}')
        
        # Remove from active goals
        if goal_id in self.active_goals:
            del self.active_goals[goal_id]
        
        # If this was part of a larger task, continue with next step
        if goal_id == 'navigate_to_object':
            # Continue with manipulation
            self.perform_manipulation_step()
    
    def perform_manipulation_step(self):
        """Perform the manipulation step of fetch and carry"""
        # Create manipulation goal
        manipulation_goal = Manipulation.Goal()
        manipulation_goal.object_name = "test_object"  # Placeholder
        manipulation_goal.target_location = "destination"  # Placeholder
        manipulation_goal.grasp_type = "precision"
        
        self.send_manipulation_goal(manipulation_goal, 'manipulate_object')
    
    def send_manipulation_goal(self, goal, goal_id):
        """Send manipulation goal to action server"""
        if not self.manipulation_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error("Manipulation action server not available")
            return False
        
        send_goal_future = self.manipulation_client.send_goal_async(
            goal,
            feedback_callback=self.manipulation_feedback_callback
        )
        
        send_goal_future.add_done_callback(
            lambda future: self.manipulation_goal_response_callback(future, goal_id)
        )
        
        self.active_goals[goal_id] = send_goal_future
        return True
    
    def coordination_loop(self):
        """Main coordination loop"""
        # Monitor system status
        if self.current_balance:
            if not self.current_balance.is_balanced:
                self.get_logger().warn("Robot is not balanced, checking for active walking tasks")
                # Could implement automatic stopping of walking tasks if robot loses balance
        
        # Monitor active goals
        for goal_id in list(self.active_goals.keys()):
            # Check if goal is still active
            # In practice, track goal status more thoroughly
            pass
    
    def manipulation_feedback_callback(self, feedback_msg):
        """Handle manipulation action feedback"""
        self.get_logger().info(
            f'Manipulation feedback: {feedback_msg.feedback.current_stage}, '
            f'Progress: {feedback_msg.feedback.progress_percentage:.1f}%'
        )
    
    def manipulation_result_callback(self, future, goal_id):
        """Handle manipulation action result"""
        result = future.result().result
        self.get_logger().info(f'Manipulation result for {goal_id}: {result.success}')
        
        # Remove from active goals
        if goal_id in self.active_goals:
            del self.active_goals[goal_id]


def main(args=None):
    rclpy.init(args=args)
    coordinator = HumanoidCoordinator()
    
    try:
        rclpy.spin(coordinator)
    except KeyboardInterrupt:
        coordinator.get_logger().info("Humanoid coordinator shutting down...")
    finally:
        coordinator.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

#### 2. Launch File
Create `launch/humanoid_system.launch.py`:
```python
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    # Declare launch arguments
    namespace_arg = DeclareLaunchArgument(
        'namespace',
        default_value='humanoid',
        description='Namespace for the robot nodes'
    )
    
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation time if true'
    )
    
    # Get launch configurations
    namespace = LaunchConfiguration('namespace')
    use_sim_time = LaunchConfiguration('use_sim_time')
    
    # Balance controller node
    balance_controller = Node(
        package='humanoid_robot_control',
        executable='balance_controller',
        name='balance_controller',
        namespace=namespace,
        parameters=[{
            'use_sim_time': use_sim_time,
            'control_frequency': 200,
            'stability_threshold': 0.05,
            'cop_limit': 0.1
        }],
        output='screen'
    )
    
    # Walking action server
    walking_server = Node(
        package='humanoid_robot_control',
        executable='walking_action_server',
        name='walking_action_server',
        namespace=namespace,
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )
    
    # Manipulation action server
    manipulation_server = Node(
        package='humanoid_robot_control',
        executable='manipulation_action_server',
        name='manipulation_action_server',
        namespace=namespace,
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )
    
    # Coordinator node
    coordinator = Node(
        package='humanoid_robot_control',
        executable='coordinator',
        name='humanoid_coordinator',
        namespace=namespace,
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )
    
    # Timer to start nodes in sequence for proper initialization
    return LaunchDescription([
        namespace_arg,
        use_sim_time_arg,
        
        # Start balance controller first
        balance_controller,
        
        # Start action servers after a delay
        TimerAction(
            period=2.0,
            actions=[walking_server]
        ),
        
        TimerAction(
            period=2.5,
            actions=[manipulation_server]
        ),
        
        # Start coordinator last
        TimerAction(
            period=3.0,
            actions=[coordinator]
        )
    ])
```

### Hints
- Use launch files to coordinate multiple nodes
- Implement proper startup sequences with timing
- Add monitoring and recovery to the coordinator
- Test with both simulated and physical robots

## Chapter Summary

This exercise set provided hands-on experience with creating a complete humanoid robot ROS 2 system, including:
- Proper package structure with custom messages and services
- Different communication patterns (topics, services, actions)
- Coordination between multiple subsystems
- Launch systems for integrated operation
- Error handling and safety considerations

## Checklist

- [ ] Create proper ROS 2 package structure for humanoid robot
- [ ] Define custom message types for humanoid-specific communication
- [ ] Implement service definitions for robot control
- [ ] Create action definitions for long-running tasks
- [ ] Build action servers with feedback and result
- [ ] Develop action clients for testing
- [ ] Implement coordination node for task management
- [ ] Create launch files for system startup
- [ ] Add safety checks and error handling
- [ ] Test complete system integration

## References

- [ROS 2 Actions Documentation](https://docs.ros.org/en/humble/Tutorials/Actions/Understanding-ROS2-Actions.html)
- [ROS 2 Services and Clients](https://docs.ros.org/en/humble/Tutorials/Services/Understanding-ROS2-Services.html)
- [ROS 2 Launch Files Guide](https://docs.ros.org/en/humble/Tutorials/Intermediate/Launch/Creating-Launch-Files.html)
- [ROS 2 Best Practices](https://docs.ros.org/en/humble/The-ROS2-Project/Contributing/Code-Style-Language-Versions.html)
- [Humanoid Robotics with ROS](https://ieeexplore.ieee.org/document/8357932)