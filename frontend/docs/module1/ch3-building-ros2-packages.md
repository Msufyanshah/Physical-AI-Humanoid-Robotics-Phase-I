---
title: 'Chapter 3 - Building ROS 2 Packages in Python'
description: 'Learn to build ROS 2 packages using Python for humanoid robotics applications'
---

# Chapter 3: Building ROS 2 Packages in Python

## Learning Objectives

After reading this chapter, you will be able to:
- Structure ROS 2 Python packages following best practices
- Create custom message and service definitions
- Implement nodes with proper lifecycle management
- Use ROS 2 parameters and configuration
- Implement action servers and clients for humanoid tasks
- Design reusable Python modules for robotics applications

## Introduction

ROS 2 packages provide the organizational structure for robotics code. This chapter focuses on building effective Python packages for humanoid robotics applications. We'll cover the essential patterns for organizing code, handling parameters, creating custom message types, and implementing the different communication paradigms (topics, services, actions).

## ROS 2 Package Structure

### Standard Layout

A proper ROS 2 Python package should follow this structure:

```text
my_robot_package/
├── CMakeLists.txt
├── package.xml
├── setup.py
├── setup.cfg
├── my_robot_package/
│   ├── __init__.py
│   ├── main_node.py
│   ├── auxiliary_nodes/
│   │   ├── perception_node.py
│   │   └── controller_node.py
│   ├── utilities/
│   │   ├── math_utils.py
│   │   └── transforms.py
│   └── config/
│       ├── default_params.yaml
│       └── simulation_params.yaml
├── launch/
│   ├── main_launch.py
│   └── sim_launch.py
├── test/
│   ├── test_main.py
│   └── test_utilities.py
└── resource/
    └── my_robot_package
```

### Creating a Package

To create a new Python package:

```bash
ros2 pkg create --build-type ament_python my_humanoid_controller
```

This creates the basic structure with proper configuration files.

## Creating Custom Message Types

ROS 2 standard message types might not cover humanoid-specific data, so we need to create custom messages:

### 1. Define the Message

Create the message definition file in `msg/HumanoidJointState.msg`:

```text
# Custom message for humanoid joint states
string name
float64[] positions
float64[] velocities
float64[] efforts
float64[] desired_positions
float64[] desired_velocities
bool[] is_safe
```

### 2. Update package.xml

Add dependencies for message generation:

```xml
<depend>builtin_interfaces</depend>
<depend>std_msgs</depend>
<build_depend>rosidl_default_generators</build_depend>
<exec_depend>rosidl_default_runtime</exec_depend>
<member_of_group>rosidl_interface_packages</member_of_group>
```

### 3. Update setup.py

```python
from setuptools import setup
import os
from glob import glob

package_name = 'my_humanoid_controller'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Include all launch files
        (os.path.join('share', package_name, 'launch'), glob('launch/*launch.[pxy][yma]*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='your.email@example.com',
    description='Humanoid controller package',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'humanoid_controller = my_humanoid_controller.main_node:main',
        ],
    },
    # For custom messages
    packages=find_packages(exclude=['test']),
    package_data={
        'my_humanoid_controller': ['*.yaml']
    },
    # Message generation
    rosidl_generate_interfaces=True,
    rosidl_interfaces=glob('msg/*.msg'),
)
```

## Custom Service Definitions

For humanoid robots, we may need custom services. Define in `srv/BalanceRequest.srv`:

```text
# BalanceRequest.srv
# Request humanoid robot to maintain balance
float64 target_orientation_x  # Target orientation (quaternion)
float64 target_orientation_y
float64 target_orientation_z
float64 target_orientation_w
float64 max_deviation  # Maximum allowed deviation from target
---
# Response
bool success
float64 actual_orientation_x
float64 actual_orientation_y
float64 actual_orientation_z
float64 actual_orientation_w
string message
```

## Node Implementation Patterns

### Basic Node Pattern

```python
# main_node.py
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from geometry_msgs.msg import Twist
from my_humanoid_controller.msg import HumanoidJointState
from my_humanoid_controller.srv import BalanceRequest
from std_msgs.msg import Float64MultiArray
import numpy as np


class HumanoidControllerNode(Node):
    def __init__(self):
        super().__init__('humanoid_controller')
        
        # Declare parameters with defaults
        self.declare_parameter('control_frequency', 100)
        self.declare_parameter('max_linear_velocity', 0.5)
        self.declare_parameter('max_angular_velocity', 0.5)
        self.declare_parameter('robot_name', 'humanoid_robot')
        
        # Get parameter values
        self.control_frequency = self.get_parameter('control_frequency').value
        self.max_lin_vel = self.get_parameter('max_linear_velocity').value
        self.max_ang_vel = self.get_parameter('max_angular_velocity').value
        self.robot_name = self.get_parameter('robot_name').value
        
        # Create subscribers
        self.joint_state_sub = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_state_callback,
            10
        )
        
        self.cmd_vel_sub = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_vel_callback,
            10
        )
        
        # Create publishers
        self.joint_cmd_pub = self.create_publisher(
            HumanoidJointState,
            '/joint_commands',
            10
        )
        
        self.status_pub = self.create_publisher(
            Float64MultiArray,
            '/robot_status',
            10
        )
        
        # Create services
        self.balance_srv = self.create_service(
            BalanceRequest,
            '/request_balance',
            self.balance_request_callback
        )
        
        # Create timers
        self.control_timer = self.create_timer(
            1.0/self.control_frequency,
            self.control_loop
        )
        
        # Robot state
        self.current_joint_state = None
        self.current_cmd_vel = None
        self.balance_target = None
        
        self.get_logger().info(f'Humanoid Controller Node initialized for {self.robot_name}')

    def joint_state_callback(self, msg: JointState):
        """Callback for joint state messages"""
        self.current_joint_state = {
            'names': msg.name,
            'positions': msg.position,
            'velocities': msg.velocity,
            'efforts': msg.effort
        }
        self.get_logger().debug('Received joint state update')

    def cmd_vel_callback(self, msg: Twist):
        """Callback for velocity commands"""
        # Limit velocities based on parameters
        lin_x = max(-self.max_lin_vel, min(self.max_lin_vel, msg.linear.x))
        ang_z = max(-self.max_ang_vel, min(self.max_ang_vel, msg.angular.z))
        
        self.current_cmd_vel = {
            'linear': {'x': lin_x, 'y': msg.linear.y, 'z': msg.linear.z},
            'angular': {'x': msg.angular.x, 'y': msg.angular.y, 'z': ang_z}
        }
        self.get_logger().debug(f'Received cmd_vel: linear.x={lin_x}, angular.z={ang_z}')

    def control_loop(self):
        """Main control loop"""
        if self.current_cmd_vel and self.current_joint_state:
            # Process commands and generate joint commands
            joint_commands = self.compute_joint_commands()
            
            if joint_commands:
                # Publish joint commands
                cmd_msg = HumanoidJointState()
                cmd_msg.name = self.robot_name
                cmd_msg.positions = joint_commands['positions']
                cmd_msg.velocities = joint_commands['velocities']
                cmd_msg.desired_positions = joint_commands['desired_positions']
                cmd_msg.is_safe = joint_commands['is_safe']
                
                self.joint_cmd_pub.publish(cmd_msg)
                
                # Publish status
                status_msg = Float64MultiArray()
                status_msg.data = [
                    joint_commands['balance_score'],
                    joint_commands['energy_consumption'],
                    joint_commands['control_effort']
                ]
                self.status_pub.publish(status_msg)

    def compute_joint_commands(self):
        """Compute joint commands based on current state and desired motion"""
        try:
            # Implement humanoid-specific inverse kinematics and control logic
            # This is a simplified example - in practice, would be much more complex
            
            commands = {
                'positions': [],
                'velocities': [],
                'desired_positions': [],
                'is_safe': [],
                'balance_score': 0.0,
                'energy_consumption': 0.0,
                'control_effort': 0.0
            }
            
            # Example calculation for walking gait
            time_now = self.get_clock().now().nanoseconds * 1e-9  # Convert to seconds
            
            # Generate sinusoidal patterns for walking gait
            for i, joint_name in enumerate(self.current_joint_state['names']):
                if 'hip' in joint_name:
                    # Hip joints for walking
                    amplitude = 0.1
                    frequency = 1.0  # 1 Hz
                    offset = i * 0.1  # Phase offset
                    
                    desired_pos = amplitude * np.sin(2 * np.pi * frequency * time_now + offset)
                    commands['desired_positions'].append(desired_pos)
                elif 'knee' in joint_name:
                    # Knee joints following hip pattern
                    amplitude = 0.05
                    frequency = 1.0
                    offset = i * 0.1 + np.pi/2  # 90 degree phase shift
                    
                    desired_pos = amplitude * np.sin(2 * np.pi * frequency * time_now + offset)
                    commands['desired_positions'].append(desired_pos)
                else:
                    # Other joints maintain neutral position
                    commands['desired_positions'].append(0.0)
                
                # Set other command parameters
                commands['positions'].append(self.current_joint_state['positions'][i])
                commands['velocities'].append(0.0)
                commands['is_safe'].append(True)
            
            # Calculate balance and performance metrics
            commands['balance_score'] = np.random.uniform(0.7, 1.0)  # Simulated
            commands['energy_consumption'] = np.random.uniform(0.1, 0.5)  # Simulated
            commands['control_effort'] = np.random.uniform(0.2, 0.8)  # Simulated
            
            return commands
            
        except Exception as e:
            self.get_logger().error(f'Error computing joint commands: {e}')
            return None

    def balance_request_callback(self, request, response):
        """Handle balance request service calls"""
        try:
            # Implement balance control logic
            self.balance_target = {
                'orientation': [
                    request.target_orientation_x,
                    request.target_orientation_y,
                    request.target_orientation_z,
                    request.target_orientation_w
                ],
                'max_deviation': request.max_deviation
            }
            
            # Execute balance control
            success, actual_orientation, message = self.execute_balance_control(
                self.balance_target
            )
            
            response.success = success
            response.actual_orientation_x = actual_orientation[0]
            response.actual_orientation_y = actual_orientation[1]
            response.actual_orientation_z = actual_orientation[2]
            response.actual_orientation_w = actual_orientation[3]
            response.message = message
            
            self.get_logger().info(f'Balance request: {"SUCCESS" if success else "FAILED"}')
            
            return response
            
        except Exception as e:
            self.get_logger().error(f'Error in balance request callback: {e}')
            response.success = False
            response.message = f'Internal error: {str(e)}'
            return response

    def execute_balance_control(self, balance_target):
        """Execute balance control with the humanoid robot"""
        # In a real implementation, this would run balance control algorithms
        # For simulation, return a successful result
        import random
        
        # Simulate balance control execution
        # This would involve complex balance control algorithms in practice
        time.sleep(0.1)  # Simulate processing time
        
        # Return success with current orientation (simulated)
        return True, [0.0, 0.0, 0.0, 1.0], "Balance control executed successfully"


def main(args=None):
    rclpy.init(args=args)
    
    controller_node = HumanoidControllerNode()
    
    try:
        rclpy.spin(controller_node)
    except KeyboardInterrupt:
        controller_node.get_logger().info('Humanoid Controller stopped by user')
    finally:
        controller_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Parameter Management

### YAML Configuration Files

Create `config/default_params.yaml`:

```yaml
/**:
  ros__parameters:
    control_frequency: 100
    max_linear_velocity: 0.5
    max_angular_velocity: 0.5
    robot_name: "humanoid_robot"
    balance_parameters:
      kp: 10.0
      ki: 0.1
      kd: 0.05
      max_correction: 0.1
    walking_parameters:
      step_height: 0.05
      step_length: 0.3
      step_frequency: 1.0
      foot_clearance: 0.02
    safety_limits:
      max_torque: 100.0
      max_velocity: 2.0
      temperature_threshold: 70.0
```

### Parameter Handling in Nodes

```python
# parameters_example.py
import rclpy
from rclpy.node import Node
from rclpy.exceptions import ParameterExceptions
from rcl_interfaces.msg import ParameterDescriptor, ParameterType


class ParameterizedHumanoidNode(Node):
    def __init__(self):
        super().__init__('parameterized_humanoid')
        
        # Declare parameters with descriptions and constraints
        self.declare_parameter(
            'walking.gait_type',
            'dynamic_walking',
            ParameterDescriptor(
                description='Type of walking gait: dynamic_walking, static_walk, or balance_only',
                type=ParameterType.PARAMETER_STRING
            )
        )
        
        self.declare_parameter(
            'walking.step_length',
            0.3,
            ParameterDescriptor(
                description='Step length in meters',
                type=ParameterType.PARAMETER_DOUBLE,
                floating_point_range=[0.1, 0.8]
            )
        )
        
        self.declare_parameter(
            'walking.step_height',
            0.05,
            ParameterDescriptor(
                description='Step height in meters',
                type=ParameterType.PARAMETER_DOUBLE,
                floating_point_range=[0.02, 0.15]
            )
        )
        
        self.declare_parameter(
            'balance.stability_threshold',
            0.01,
            ParameterDescriptor(
                description='Threshold for balance stability',
                type=ParameterType.PARAMETER_DOUBLE,
                floating_point_range=[0.001, 0.1]
            )
        )
        
        # Set up parameter change callback
        self.set_parameters_callback(self.parameters_callback)
        
        # Initialize with current parameters
        self.update_parameters()
        
        self.param_update_timer = self.create_timer(1.0, self.check_param_changes)
        
        self.get_logger().info('Parameterized Humanoid Node initialized with dynamic parameters')
    
    def parameters_callback(self, params):
        """Handle parameter updates"""
        for param in params:
            self.get_logger().info(f'Parameter {param.name} changed to {param.value}')
        
        # Update internal state based on new parameters
        self.update_parameters()
        
        return SetParametersResult(successful=True)
    
    def update_parameters(self):
        """Update internal state based on current parameters"""
        try:
            self.gait_type = self.get_parameter('walking.gait_type').value
            self.step_length = self.get_parameter('walking.step_length').value
            self.step_height = self.get_parameter('walking.step_height').value
            self.stability_threshold = self.get_parameter('balance.stability_threshold').value
            
            self.get_logger().info(f'Updated parameters: gait={self.gait_type}, '
                                 f'step length={self.step_length}m, '
                                 f'step height={self.step_height}m')
        except Exception as e:
            self.get_logger().error(f'Error updating parameters: {e}')
    
    def check_param_changes(self):
        """Regular check for parameter changes (backup mechanism)"""
        # This could be used for nodes that need frequent parameter checking
        pass


def main(args=None):
    rclpy.init(args=args)
    param_node = ParameterizedHumanoidNode()
    
    try:
        rclpy.spin(param_node)
    except KeyboardInterrupt:
        pass
    finally:
        param_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Action Implementation for Humanoid Tasks

### Custom Action Definitions

Define in `action/WalkGoal.action`:

```text
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

### Action Server

```python
# action_server.py
import rclpy
from rclpy.action import ActionServer, GoalResponse, CancelResponse
from rclpy.node import Node
from my_humanoid_controller.action import WalkGoal
from my_humanoid_controller.msg import HumanoidJointState
import threading
import time


class WalkActionServer(Node):
    def __init__(self):
        super().__init__('walk_action_server')
        
        # Create action server
        self._action_server = ActionServer(
            self,
            WalkGoal,
            'walk_to_goal',
            self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback
        )
        
        # Publishers and subscribers for walking
        self.joint_cmd_pub = self.create_publisher(
            HumanoidJointState,
            '/joint_commands',
            10
        )
        
        # Walking state
        self.is_walking = False
        self.current_distance = 0.0
        
        self.get_logger().info('Walk Action Server initialized')

    def goal_callback(self, goal_request):
        """Accept or reject goal requests"""
        self.get_logger().info(f'Received walk goal: {goal_request.distance}m at {goal_request.speed}m/s')
        
        # Check if the robot is busy - reject if already walking
        if self.is_walking:
            self.get_logger().warn('Rejecting walk goal: robot is already walking')
            return GoalResponse.REJECT
        
        # Accept the goal
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        """Handle goal cancellation"""
        self.get_logger().info('Received cancellation request for walk goal')
        return CancelResponse.ACCEPT

    def execute_callback(self, goal_handle):
        """Execute the walk action"""
        self.get_logger().info('Executing walk goal...')
        
        result = WalkGoal.Result()
        feedback = WalkGoal.Feedback()
        
        goal = goal_handle.request
        
        # Validate inputs
        if goal.distance <= 0 or goal.speed <= 0:
            result.success = False
            result.message = "Invalid goal: distance and speed must be positive"
            goal_handle.abort()
            return result
        
        # Start walking
        self.is_walking = True
        self.current_distance = 0.0
        
        try:
            # Perform the walking motion (simplified - in practice, much more complex)
            step_size = 0.1  # 10cm per step
            time_per_step = step_size / goal.speed  # Time for each step at given speed
            
            steps_needed = int(goal.distance / step_size)
            
            for i in range(steps_needed):
                if goal_handle.is_cancel_requested:
                    goal_handle.canceled()
                    result.success = False
                    result.message = "Goal canceled"
                    self.is_walking = False
                    return result
                
                # Update distance traveled
                self.current_distance = min(goal.distance, (i + 1) * step_size)
                
                # Generate walking motion for this step
                self.execute_step(goal.gait_type)
                
                # Publish feedback
                feedback.distance_traveled = self.current_distance
                feedback.speed_actual = goal.speed
                feedback.status = f"Walking: {self.current_distance:.2f}/{goal.distance:.2f}m"
                feedback.is_safe = True  # Assuming safe operation
                
                goal_handle.publish_feedback(feedback)
                
                # Sleep for appropriate time to maintain speed
                time.sleep(time_per_step)
            
            # Walking completed
            result.success = True
            result.actual_distance = self.current_distance
            result.message = f"Successfully walked {self.current_distance:.2f} meters"
            
            goal_handle.succeed()
            self.is_walking = False
            
            return result
            
        except Exception as e:
            self.get_logger().error(f'Error executing walk action: {e}')
            result.success = False
            result.message = f"Error during walk: {str(e)}"
            goal_handle.abort()
            self.is_walking = False
            return result

    def execute_step(self, gait_type):
        """Execute a single walking step"""
        # In practice, this would implement complex walking algorithms
        # For this example, we'll generate simple joint commands
        import math
        
        # Generate sinusoidal walking gait pattern
        current_time = time.time() * 10  # Speed up the pattern
        
        # Create joint commands for a step
        joint_state = HumanoidJointState()
        joint_state.name = "humanoid_robot"
        joint_state.positions = []
        joint_state.velocities = []
        joint_state.desired_positions = []
        joint_state.is_safe = []
        
        # Generate walking pattern for different joints
        joints = [
            "left_hip_pitch", "left_hip_roll", "left_hip_yaw",
            "left_knee", "left_ankle_pitch", "left_ankle_roll",
            "right_hip_pitch", "right_hip_roll", "right_hip_yaw",
            "right_knee", "right_ankle_pitch", "right_ankle_roll"
        ]
        
        for i, joint in enumerate(joints):
            # Different patterns for different joints based on gait type
            if 'hip' in joint:
                if 'pitch' in joint:
                    # Hip pitch for forward motion
                    pattern = math.sin(current_time * 0.5) * 0.2 if gait_type == "dynamic_walking" else 0.1
                elif 'roll' in joint:
                    # Hip roll for balance
                    pattern = math.sin(current_time * 0.3) * 0.05
                else:
                    # Hip yaw for turning (simplified as zero for straight walk)
                    pattern = 0.0
            elif 'knee' in joint:
                # Knee bending during step
                pattern = math.sin(current_time * 0.5) * 0.3 if gait_type == "dynamic_walking" else 0.15
            else:  # ankle joints
                # Ankle adjustment for balance
                pattern = math.sin(current_time * 0.4) * 0.05
            
            joint_state.positions.append(0.0)  # Current position (would come from joint states)
            joint_state.desired_positions.append(pattern)  # Desired position
            joint_state.velocities.append(0.0)  # Desired velocity
            joint_state.is_safe.append(True)  # Safety flag
        
        self.joint_cmd_pub.publish(joint_state)


def main(args=None):
    rclpy.init(args=args)
    action_server = WalkActionServer()
    
    try:
        rclpy.spin(action_server)
    except KeyboardInterrupt:
        pass
    finally:
        action_server.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### Action Client

```python
# action_client.py
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from my_humanoid_controller.action import WalkGoal


class WalkActionClient(Node):
    def __init__(self):
        super().__init__('walk_action_client')
        
        # Create action client
        self._action_client = ActionClient(
            self,
            WalkGoal,
            'walk_to_goal'
        )
        
        self.get_logger().info('Walk Action Client initialized')

    def send_walk_goal(self, distance, speed, gait_type='dynamic_walking'):
        """Send a walk goal to the action server"""
        goal_msg = WalkGoal.Goal()
        goal_msg.distance = distance
        goal_msg.speed = speed
        goal_msg.gait_type = gait_type
        
        self.get_logger().info(f'Waiting for action server...')
        self._action_client.wait_for_server()
        
        self.get_logger().info(f'Sending walk goal: {distance}m at {speed}m/s using {gait_type}')
        
        # Send goal and get future
        send_goal_future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )
        
        # Add done callback to handle the response
        send_goal_future.add_done_callback(self.goal_response_callback)
        
        return send_goal_future

    def goal_response_callback(self, future):
        """Handle goal response"""
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected')
            return

        self.get_logger().info('Goal accepted')
        
        # Get result using async approach
        get_result_future = goal_handle.get_result_async()
        get_result_future.add_done_callback(self.get_result_callback)

    def feedback_callback(self, feedback_msg):
        """Handle feedback during action execution"""
        feedback = feedback_msg.feedback
        self.get_logger().info(f'Feedback: {feedback.status}')

    def get_result_callback(self, future):
        """Handle action result"""
        result = future.result().result
        self.get_logger().info(f'Result: success={result.success}, message="{result.message}"')


def main(args=None):
    rclpy.init(args=args)
    action_client = WalkActionClient()
    
    # Send a sample walk goal
    future = action_client.send_walk_goal(1.5, 0.3, 'dynamic_walking')
    
    try:
        rclpy.spin_until_future_complete(action_client, future)
    except KeyboardInterrupt:
        pass
    finally:
        action_client.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Launch Files for Coordination

### Python Launch Files

Create `launch/humanoid_system_launch.py`:

```python
# humanoid_system_launch.py
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node, SetParameter
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Declare launch arguments
    simulation_arg = DeclareLaunchArgument(
        'use_sim',
        default_value='false',
        description='Use simulation mode'
    )
    
    robot_name_arg = DeclareLaunchArgument(
        'robot_name',
        default_value='humanoid_robot',
        description='Name of the robot'
    )
    
    # Get launch configurations
    use_sim = LaunchConfiguration('use_sim')
    robot_name = LaunchConfiguration('robot_name')
    
    # Parameters file path
    params_file = PathJoinSubstitution([
        FindPackageShare('my_humanoid_controller'),
        'config',
        'default_params.yaml'
    ])
    
    # Main controller node
    humanoid_controller = Node(
        package='my_humanoid_controller',
        executable='humanoid_controller',
        name='humanoid_controller',
        parameters=[
            params_file,
            {'robot_name': robot_name}
        ],
        remappings=[
            ('/joint_states', '/joint_states'),
            ('/cmd_vel', '/cmd_vel'),
            ('/joint_commands', '/joint_group_position_controller/commands'),
        ],
        output='screen'
    )
    
    # Action server node
    walk_action_server = Node(
        package='my_humanoid_controller',
        executable='walk_action_server',
        name='walk_action_server',
        parameters=[params_file],
        output='screen'
    )
    
    # Conditional launch of simulation if requested
    sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            FindPackageShare('my_humanoid_controller'),
            '/launch/sim_launch.py'
        ]),
        condition=IfCondition(use_sim)
    )
    
    # Return launch description
    return LaunchDescription([
        simulation_arg,
        robot_name_arg,
        humanoid_controller,
        walk_action_server,
        sim_launch
    ])
```

## Testing and Validation

### Unit Tests

Create `test/test_humanoid_controller.py`:

```python
import unittest
import rclpy
from rclpy.executors import SingleThreadedExecutor
from std_msgs.msg import String
from sensor_msgs.msg import JointState
from geometry_msgs.msg import Twist
from my_humanoid_controller.main_node import HumanoidControllerNode


class TestHumanoidController(unittest.TestCase):
    """Test the Humanoid Controller Node"""
    
    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def setUp(self):
        self.node = HumanoidControllerNode()
        self.executor = SingleThreadedExecutor()
        self.executor.add_node(self.node)

    def tearDown(self):
        self.node.destroy_node()

    def test_node_initialization(self):
        """Test that node initializes correctly"""
        self.assertIsNotNone(self.node)
        self.assertEqual(self.node.get_parameter('robot_name').value, 'humanoid_robot')

    def test_parameter_update(self):
        """Test parameter updating functionality"""
        new_name = 'updated_robot'
        self.node.set_parameters([rclpy.Parameter('robot_name', value=new_name)])
        
        # Allow time for parameter update
        self.executor.spin_once(timeout_sec=0.1)
        
        self.assertEqual(self.node.get_parameter('robot_name').value, new_name)

    def test_joint_state_callback(self):
        """Test joint state callback functionality"""
        # Create a mock joint state message
        joint_msg = JointState()
        joint_msg.name = ['joint1', 'joint2', 'joint3']
        joint_msg.position = [0.1, 0.2, 0.3]
        joint_msg.velocity = [0.0, 0.0, 0.0]
        joint_msg.effort = [0.0, 0.0, 0.0]
        
        # Call the callback directly
        self.node.joint_state_callback(joint_msg)
        
        # Check that the joint state was updated
        self.assertIsNotNone(self.node.current_joint_state)
        self.assertEqual(len(self.node.current_joint_state['names']), 3)

    def test_cmd_vel_callback(self):
        """Test velocity command callback"""
        # Create a mock velocity command
        cmd_msg = Twist()
        cmd_msg.linear.x = 0.5
        cmd_msg.angular.z = 0.2
        
        # Call the callback directly
        self.node.cmd_vel_callback(cmd_msg)
        
        # Check that the command was updated
        self.assertIsNotNone(self.node.current_cmd_vel)
        self.assertAlmostEqual(self.node.current_cmd_vel['linear']['x'], 0.5)
        self.assertAlmostEqual(self.node.current_cmd_vel['angular']['z'], 0.2)


def test_compute_joint_commands(self):
    """Test joint command computation"""
    # Create a mock joint state
    joint_msg = JointState()
    joint_msg.name = ['hip_yaw', 'knee', 'shoulder']
    joint_msg.position = [0.0, 0.0, 0.0]
    joint_msg.velocity = [0.0, 0.0, 0.0]
    joint_msg.effort = [0.0, 0.0, 0.0]
    
    self.node.joint_state_callback(joint_msg)
    
    # Set a command velocity
    cmd_msg = Twist()
    cmd_msg.linear.x = 0.3
    cmd_msg.angular.z = 0.1
    self.node.cmd_vel_callback(cmd_msg)
    
    # Test command computation
    commands = self.node.compute_joint_commands()
    self.assertIsNotNone(commands)
    self.assertEqual(len(commands['desired_positions']), 3)


if __name__ == '__main__':
    unittest.main()
```

## Chapter Summary

This chapter provided a comprehensive look at building effective ROS 2 packages in Python for humanoid robotics. We covered the standard package structure, custom message and service definitions, node implementation patterns, parameter management, and action implementation for complex humanoid tasks.

We examined how to create robust, parameterized nodes that can adapt to different scenarios and how to implement action-based interfaces for complex behaviors like walking. The examples showed how to structure code for modularity, maintainability, and reusability in robotic applications.

## Checklist

- [ ] Structure ROS 2 Python packages following best practices
- [ ] Create custom message and service definitions
- [ ] Implement nodes with proper lifecycle management
- [ ] Use ROS 2 parameters and configuration effectively
- [ ] Implement action servers and clients for complex tasks
- [ ] Design reusable Python modules for robotics applications
- [ ] Create proper launch files for system coordination
- [ ] Write unit tests for robot components

## Exercises

### Exercise 1: Package Creation

Create a complete ROS 2 package for a simple humanoid behavior like head tracking.

#### Solution

1. Use `ros2 pkg create --build-type ament_python` to create the package
2. Add custom message definitions for head tracking goals
3. Implement a node that controls head movement
4. Add parameters for sensitivity and tracking limits
5. Create a launch file to start the system

#### Hints

- Follow the standard package structure
- Use appropriate message types for head pose control
- Consider safety limits for neck joint movement
- Add proper logging and error handling

### Exercise 2: Action Implementation

Implement an action server for a humanoid manipulation task (e.g., reaching and grasping).

#### Solution

1. Define a custom action for manipulation tasks
2. Implement the action server with proper goal handling
3. Create a state machine for the manipulation process
4. Handle feedback, results, and cancellation properly

#### Hints

- Think about the different states in a manipulation action
- Consider sensor feedback during execution
- Implement appropriate safety checks
- Use proper error handling and recovery

## References

- [ROS 2 Python Package Creation Guide](https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Creating-Your-First-ROS2-Package.html)
- [ROS 2 Actions in Python](https://docs.ros.org/en/humble/Tutorials/Actions/Creating-an-Action.html)
- [Parameter Management in ROS 2](https://docs.ros.org/en/humble/Tutorials/Parameters/Understanding-ROS2-Parameters.html)
- [ROS 2 Launch Files Guide](https://docs.ros.org/en/humble/Tutorials/Intermediate/Launch/Creating-Launch-Files.html)
- [Python Interface Development for ROS](https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Single-Python-Node-Multiple-Callbacks.html)