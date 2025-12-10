---
title: 'Chapter 3 - Building ROS 2 Packages in Python'
description: 'Learn how to create ROS 2 packages using Python'
---

# Chapter 3: Building ROS 2 Packages in Python

## Learning Objectives

After reading this chapter, you will be able to:
- Create a new ROS 2 package using Python
- Understand the structure of a ROS 2 package
- Implement ROS 2 nodes using Python
- Work with ROS 2 messages, services, and actions in Python
- Build and run your ROS 2 Python packages

## Introduction

This chapter covers how to create and build ROS 2 packages specifically using Python. Python is one of the most accessible languages for ROS 2 development and is widely used for prototyping and scripting tasks. We'll explore the structure of ROS 2 packages and how to implement nodes, topics, services, and actions using Python.

## ROS 2 Package Structure

A ROS 2 package follows a standard structure:

```
my_robot_package/
├── CMakeLists.txt
├── package.xml
├── setup.cfg
├── setup.py
├── resource/
│   └── my_robot_package
├── my_robot_package/
│   ├── __init__.py
│   └── my_node.py
├── launch/
│   └── my_launch_file.py
├── test/
└── scripts/
```

### Key Components

- `package.xml`: Contains package metadata
- `setup.py`: Python package configuration
- `setup.cfg`: Installation configuration
- `my_robot_package/`: Main Python module directory
- `launch/`: Launch files to start nodes
- `test/`: Unit and integration tests

## Creating a ROS 2 Package

### Using ros2 pkg create

To create a new ROS 2 package for Python development:

```bash
ros2 pkg create --build-type ament_python my_robot_controller
```

This command creates the basic structure for a Python-based ROS 2 package. You can also add dependencies during creation:

```bash
ros2 pkg create --build-type ament_python --dependencies rclpy std_msgs sensor_msgs my_robot_controller
```

## Python Node Implementation

### Basic Node Structure

```python
#!/usr/bin/env python3

"""
Example of a ROS 2 Python node
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class MinimalPublisher(Node):

    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, 'topic', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        msg = String()
        msg.data = f'Hello World: {self.i}'
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: "{msg.data}"')
        self.i += 1


def main(args=None):
    rclpy.init(args=args)

    minimal_publisher = MinimalPublisher()

    rclpy.spin(minimal_publisher)

    # Destroy the node explicitly
    minimal_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

**Execution Notes**: Save this as `my_robot_package/my_node.py` within your package directory.
**Expected Output**: Node will publish a message every 0.5 seconds until interrupted.

### Node Components Explained

- **Node inheritance**: Your class inherits from `rclpy.node.Node`
- **Publisher**: Allows publishing messages to topics
- **Timer**: Executes callbacks at regular intervals
- **Logger**: Provides logging functionality
- **Spin**: Keeps the node running and processes callbacks

## Working with Messages

### Creating Custom Messages

To create your own message types, create a `msg` directory in your package and define message files with the `.msg` extension:

```
msg/
├── MyCustomMessage.msg
```

Example `MyCustomMessage.msg`:
```
string name
int32 id
float64 value
bool is_active
```

After creating custom messages, you must update your `package.xml` and `setup.py` accordingly.

### Using Built-in Messages

ROS 2 provides many built-in message types:

```python
from std_msgs.msg import String, Int32, Float64
from sensor_msgs.msg import LaserScan, Image, CameraInfo
from geometry_msgs.msg import Twist, Pose, Point
from nav_msgs.msg import Odometry
```

## Services in Python

### Service Server

```python
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts


class MinimalService(Node):

    def __init__(self):
        super().__init__('minimal_service')
        self.srv = self.create_service(AddTwoInts, 'add_two_ints', self.add_two_ints_callback)

    def add_two_ints_callback(self, request, response):
        response.sum = request.a + request.b
        self.get_logger().info(f'Returning {request.a} + {request.b} = {response.sum}')
        return response
```

### Service Client

```python
import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts


class MinimalClient(Node):

    def __init__(self):
        super().__init__('minimal_client')
        self.cli = self.create_client(AddTwoInts, 'add_two_ints')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service not available, waiting again...')
        self.req = AddTwoInts.Request()

    def send_request(self, a, b):
        self.req.a = a
        self.req.b = b
        future = self.cli.call_async(self.req)
        rclpy.spin_until_future_complete(self, future)
        return future.result()
```

## Actions in Python

### Action Server

```python
from rclpy.action import ActionServer
from rclpy.node import Node
from example_interfaces.action import Fibonacci


class FibonacciActionServer(Node):

    def __init__(self):
        super().__init__('fibonacci_action_server')
        self._action_server = ActionServer(
            self,
            Fibonacci,
            'fibonacci',
            self.execute_callback)

    def execute_callback(self, goal_handle):
        self.get_logger().info('Executing goal...')
        
        feedback_msg = Fibonacci.Feedback()
        feedback_msg.sequence = [0, 1]
        
        for i in range(1, goal_handle.request.order):
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.get_logger().info('Goal canceled')
                result = Fibonacci.Result()
                result.sequence = feedback_msg.sequence
                return result
            
            feedback_msg.sequence.append(
                feedback_msg.sequence[i] + feedback_msg.sequence[i-1])
            
            goal_handle.publish_feedback(feedback_msg)
            time.sleep(1)
        
        goal_handle.succeed()
        result = Fibonacci.Result()
        result.sequence = feedback_msg.sequence
        self.get_logger().info('Goal succeeded')
        return result
```

### Action Client

```python
from rclpy.action import ActionClient
from rclpy.node import Node
from example_interfaces.action import Fibonacci


class FibonacciActionClient(Node):

    def __init__(self):
        super().__init__('fibonacci_action_client')
        self._action_client = ActionClient(
            self,
            Fibonacci,
            'fibonacci')

    def send_goal(self, order):
        goal_msg = Fibonacci.Goal()
        goal_msg.order = order

        self._action_client.wait_for_server()
        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback)
        
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected')
            return

        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        self.get_logger().info(f'Received feedback: {feedback.sequence}')

    def get_result_callback(self, future):
        result = future.result().result
        self.get_logger().info(f'Result: {result.sequence}')
        rclpy.shutdown()
```

## Package Configuration

### setup.py

For Python packages, you need a `setup.py` file to define how your package should be installed:

```python
from setuptools import setup
import os
from glob import glob

package_name = 'my_robot_package'

setup(
    name=package_name,
    version='0.0.0',
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
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'my_node = my_robot_package.my_node:main',
        ],
    },
)
```

## Launch Files

### Python Launch Files

Launch files in ROS 2 can also be written in Python:

```python
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='my_robot_package',
            executable='my_node',
            name='minimal_publisher',
            output='screen'
        )
    ])
```

## Testing Python Nodes

### Unit Tests

Python nodes can be tested using standard Python testing tools like pytest:

```python
import pytest
import rclpy
from my_robot_package.my_node import MinimalPublisher


def test_node_creation():
    rclpy.init()
    node = MinimalPublisher()
    assert node is not None
    node.destroy_node()
    rclpy.shutdown()
```

## Best Practices

1. **Use Type Hints**: Python type hints improve code readability and catch errors early
2. **Proper Error Handling**: Handle exceptions gracefully
3. **Logging**: Use the built-in logger for debugging and monitoring
4. **Configuration**: Use parameters for configurable behaviors
5. **Resource Management**: Always clean up resources when shutting down

## Chapter Summary

This chapter covered the fundamentals of creating and building ROS 2 packages using Python. We learned about the standard package structure, how to create nodes, work with messages, services, and actions, configure packages properly, and write launch files. Python provides an accessible and powerful way to develop ROS 2 applications.

## Checklist

- [ ] Create new ROS 2 packages using Python
- [ ] Understand the structure of a ROS 2 package
- [ ] Implement ROS 2 nodes using Python
- [ ] Work with ROS 2 messages, services, and actions in Python
- [ ] Build and run your ROS 2 Python packages

## Exercises

### Exercise 1: Package Creation

Create a new ROS 2 package called "robot_sensor_publisher" that publishes sensor data using Python.

#### Solution

1. Create the package:
```bash
ros2 pkg create --build-type ament_python robot_sensor_publisher
```

2. Implement a node that publishes sensor data.

#### Hints

- Use appropriate message types for sensor data
- Structure your package according to ROS 2 conventions
- Add logging for debugging

### Exercise 2: Service Implementation

Create a service in your package that processes sensor data and returns a response.

#### Solution

1. Define the service interface
2. Implement the service server
3. Create a client to test the service

#### Hints

- Use example_interfaces or create custom service interfaces
- Handle potential errors in the service

## References

- [ROS 2 Python Developer Guide](https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Creating-Your-First-ROS2-Package.html)
- [ROS 2 Python API Documentation](https://docs.ros2.org/latest/api/rclpy/)
- [Writing a simple publisher and subscriber (Python)](https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Publisher-And-Subscriber.html)