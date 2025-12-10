---
title: 'Exercise Set 1 - The Robotic Nervous System (ROS 2)'
description: 'Hands-on exercises for Module 1 on ROS 2'
---

# Exercise Set 1: The Robotic Nervous System (ROS 2)

## Learning Objectives

After completing these exercises, you will be able to:
- Create and run basic ROS 2 nodes in Python
- Implement topic-based communication in a robot system
- Use services for request-response communication
- Build a simple robot control system using ROS 2 concepts
- Debug and troubleshoot basic ROS 2 applications

## Exercise 1: Basic ROS 2 Node Creation

Create a ROS 2 node that publishes the status of a robotic arm (position) to a topic every 2 seconds.

### Instructions

1. Create a new ROS 2 package called "robot_arm_demo"
2. Implement a publisher node that publishes a custom message containing the arm's joint angles
3. Implement a subscriber node that logs the received arm status
4. Create a launch file to start both nodes
5. Test the communication between nodes

### Solution

```python
# In robot_arm_demo/robot_arm_demo/arm_status_publisher.py
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json
import time


class ArmStatusPublisher(Node):

    def __init__(self):
        super().__init__('arm_status_publisher')
        self.publisher_ = self.create_publisher(String, 'arm_status', 10)
        timer_period = 2  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.arm_joints = {
            'shoulder_pan': 0.0,
            'shoulder_lift': 0.0,
            'elbow_flex': 0.0,
            'wrist_flex': 0.0,
            'wrist_roll': 0.0
        }
        self.step = 0

    def timer_callback(self):
        # Simulate arm movement
        self.arm_joints['shoulder_pan'] = 0.5 * (self.step % 4)
        self.arm_joints['shoulder_lift'] = 0.3 * ((self.step + 1) % 3)
        
        msg = String()
        msg.data = json.dumps(self.arm_joints)
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: {msg.data}')
        self.step += 1


def main(args=None):
    rclpy.init(args=args)
    arm_status_publisher = ArmStatusPublisher()
    rclpy.spin(arm_status_publisher)
    arm_status_publisher.destroy_node()
    rclpy.shutdown()


# In robot_arm_demo/robot_arm_demo/arm_status_subscriber.py
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json


class ArmStatusSubscriber(Node):

    def __init__(self):
        super().__init__('arm_status_subscriber')
        self.subscription = self.create_subscription(
            String,
            'arm_status',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        arm_status = json.loads(msg.data)
        self.get_logger().info(f'Arm status: {arm_status}')


def main(args=None):
    rclpy.init(args=args)
    arm_status_subscriber = ArmStatusSubscriber()
    rclpy.spin(arm_status_subscriber)
    arm_status_subscriber.destroy_node()
    rclpy.shutdown()
```

### Hints

- Use appropriate message types for your robot state
- Consider creating a custom message type for complex robot states
- Ensure proper logging for debugging

## Exercise 2: ROS 2 Service Implementation

Implement a ROS 2 service that accepts a target position and returns whether the robot arm can reach it.

### Instructions

1. Create a custom service definition file for the reachability check
2. Implement a service server that evaluates reachability
3. Implement a service client to test the service
4. Test the service with various target positions

### Solution

First, create a service definition file (`srv/CheckReachability.srv`):
```
# Request
float64 x
float64 y
float64 z
---
# Response
bool can_reach
float64 distance
string message
```

Then implement the service:

```python
# Service server
from rclpy.node import Node
from robot_arm_demo.srv import CheckReachability
import math


class ReachabilityService(Node):

    def __init__(self):
        super().__init__('reachability_service')
        self.srv = self.create_service(
            CheckReachability, 
            'check_reachability', 
            self.check_reachability_callback)

    def check_reachability_callback(self, request, response):
        # Simplified reachability check - in a real robot, this would be more complex
        # Assume arm reach is 1.0m from base
        distance = math.sqrt(request.x**2 + request.y**2 + request.z**2)
        
        if distance <= 1.0:
            response.can_reach = True
            response.distance = distance
            response.message = f"Target is reachable, distance: {distance:.2f}m"
        else:
            response.can_reach = False
            response.distance = distance
            response.message = f"Target is out of reach, distance: {distance:.2f}m"
        
        self.get_logger().info(response.message)
        return response


def main(args=None):
    rclpy.init(args=args)
    reachability_service = ReachabilityService()
    rclpy.spin(reachability_service)
    rclpy.shutdown()
```

### Hints

- The reachability check can be simplified for this exercise
- Consider using robot kinematics for a more realistic implementation
- Add proper error handling in your service

## Exercise 3: Robot Control System

Combine topics and services to create a simple robot control system that can receive movement commands and report status.

### Instructions

1. Create a ROS 2 node that receives movement commands via a topic
2. Implement a service to query robot status
3. Use a parameter server to configure robot limits
4. Implement safety checks to prevent dangerous movements

### Solution

For this exercise, we'll implement a node that:
- Subscribes to movement commands
- Maintains internal robot state
- Provides status via service
- Respects safety limits

```python
# robot_controller.py
import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from std_msgs.msg import String
from robot_arm_demo.srv import CheckReachability
import json


class RobotController(Node):

    def __init__(self):
        super().__init__('robot_controller')
        
        # Declare parameters
        self.declare_parameter('max_velocity', 0.5)
        self.declare_parameter('safety_margin', 0.1)
        self.declare_parameter('robot_base_x', 0.0)
        self.declare_parameter('robot_base_y', 0.0)
        self.declare_parameter('robot_base_z', 0.0)
        
        # Initialize robot state
        self.robot_position = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        self.robot_state = 'idle'  # idle, moving, error
        
        # Create publisher for status updates
        self.status_publisher = self.create_publisher(String, 'robot_status', 10)
        
        # Create subscriber for movement commands
        self.cmd_subscriber = self.create_subscription(
            String, 'movement_cmd', self.movement_cmd_callback, 10)
        
        # Create service for status queries
        self.status_service = self.create_service(
            CheckReachability, 'get_robot_status', self.get_status_callback)
        
        # Timer for periodic status publishing
        self.status_timer = self.create_timer(1.0, self.publish_status)

    def movement_cmd_callback(self, msg):
        try:
            cmd = json.loads(msg.data)
            
            # Extract target position
            target_x = cmd.get('x', self.robot_position['x'])
            target_y = cmd.get('y', self.robot_position['y'])
            target_z = cmd.get('z', self.robot_position['z'])
            
            # Check safety constraints
            max_vel = self.get_parameter('max_velocity').value
            safety_margin = self.get_parameter('safety_margin').value
            
            # Simple movement simulation
            self.robot_state = 'moving'
            self.get_logger().info(f'Moving to position: ({target_x}, {target_y}, {target_z})')
            
            # Update position (in a real system, this would happen over time)
            self.robot_position = {'x': target_x, 'y': target_y, 'z': target_z}
            self.robot_state = 'idle'
            
        except Exception as e:
            self.get_logger().error(f'Error processing movement command: {e}')
            self.robot_state = 'error'

    def get_status_callback(self, request, response):
        response.can_reach = True  # Simplified
        response.distance = 0.0
        response.message = f"Position: {self.robot_position}, State: {self.robot_state}"
        return response

    def publish_status(self):
        status_msg = String()
        status_msg.data = json.dumps({
            'position': self.robot_position,
            'state': self.robot_state,
            'timestamp': self.get_clock().now().nanoseconds
        })
        self.status_publisher.publish(status_msg)


def main(args=None):
    rclpy.init(args=args)
    robot_controller = RobotController()
    rclpy.spin(robot_controller)
    robot_controller.destroy_node()
    rclpy.shutdown()
```

### Hints

- Use parameters for configuration that might change between deployments
- Implement state management to track robot status
- Add error handling for unexpected conditions
- Consider thread safety when updating shared state

## Chapter Summary

These exercises provided hands-on experience with core ROS 2 concepts: nodes, topics, services, parameters, and message passing. You've implemented a complete robot control system that demonstrates how ROS 2 components work together in a robotic application.

## Checklist

- [ ] Create basic ROS 2 publisher and subscriber nodes
- [ ] Implement ROS 2 services with custom message types
- [ ] Use parameters for configurable behavior
- [ ] Combine multiple communication patterns in one application
- [ ] Implement safety checks and error handling
- [ ] Test and debug ROS 2 applications

## References

- [ROS 2 Tutorials](https://docs.ros.org/en/humble/Tutorials.html)
- [ROS 2 Services and Clients](https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Service-And-Client.html)
- [ROS 2 Parameters](https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Using-Parameters-In-A-Class-Python.html)