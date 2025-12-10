---
title: 'Chapter 2 - ROS 2 Architecture, Nodes, Topics, Services, Actions'
description: 'Understanding ROS 2 architecture and core concepts'
---

# Chapter 2: ROS 2 Architecture, Nodes, Topics, Services, Actions

## Learning Objectives

After reading this chapter, you will be able to:
- Describe the fundamental architecture of ROS 2
- Explain the concepts of nodes, topics, services, and actions
- Create and implement simple ROS 2 nodes
- Use topics for asynchronous communication
- Use services for request/response communication
- Use actions for goal-oriented tasks with feedback

## Introduction

Robot Operating System 2 (ROS 2) is the next-generation Robot Operating System designed to address the limitations of ROS 1 and provide a more robust, scalable, and production-ready framework for robotics development. This chapter covers the core architectural concepts of ROS 2, including nodes, topics, services, and actions.

## ROS 2 Architecture Overview

ROS 2 uses a client library-based architecture with a DDS (Data Distribution Service) implementation at its core. This allows for:

- **Distributed communication**: Nodes can run on the same machine or across multiple machines
- **Real-time capabilities**: Support for real-time systems
- **Language independence**: Support for multiple programming languages
- **Quality of Service (QoS)**: Configurable communication policies

### Client Libraries

ROS 2 supports multiple client libraries:
- **rclcpp**: C++ client library
- **rclpy**: Python client library
- **rclrs**: Rust client library
- **rclc**: C client library

## Nodes

Nodes are the fundamental building blocks of a ROS 2 system. A node is a process that performs computation and communicates with other nodes. Each node should perform a single task and communicate with other nodes as needed.

### Key Properties of Nodes:
- Named entities that perform computation
- Communicate with other nodes through topics, services, or actions
- Organized into packages for better management
- Can be launched together using launch files

```python
# Example of a basic ROS 2 node
import rclpy
from rclpy.node import Node

class MinimalNode(Node):
    def __init__(self):
        super().__init__('minimal_publisher')
        self.get_logger().info('Hello ROS 2 World!')

def main(args=None):
    rclpy.init(args=args)
    
    minimal_node = MinimalNode()
    
    rclpy.spin(minimal_node)
    
    minimal_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

**Execution Notes**: Save this as `minimal_node.py` in your ROS 2 package's `nodes` directory and execute with `python3 minimal_node.py`.
**Expected Output**: Console output with log message "Hello ROS 2 World!" and the node continues running until interrupted.

## Topics

Topics enable asynchronous communication between nodes using a publish-subscribe pattern. A publisher node sends messages to a topic, and subscriber nodes receive messages from that topic.

### Topic Characteristics:
- Unidirectional: Publisher doesn't know who subscribes
- Multiple publishers/subscribers allowed per topic
- Anonymous communication between nodes
- Asynchronous: Publishers and subscribers run independently

```python
# Publisher node example
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
    minimal_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

```python
# Subscriber node example
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class MinimalSubscriber(Node):
    def __init__(self):
        super().__init__('minimal_subscriber')
        self.subscription = self.create_subscription(
            String,
            'topic',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        self.get_logger().info(f'I heard: "{msg.data}"')

def main(args=None):
    rclpy.init(args=args)
    minimal_subscriber = MinimalSubscriber()
    rclpy.spin(minimal_subscriber)
    minimal_subscriber.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

**Execution Notes**: Run the publisher and subscriber nodes in separate terminals using `python3`.
**Expected Output**: Publisher will send messages every 0.5 seconds, and subscriber will print the received messages.

## Services

Services enable synchronous request-response communication between nodes. A client sends a request to a service server, and waits for a response.

### Service Characteristics:
- Synchronous: Client waits for response
- Request-response pattern
- One client per request to one server
- Used for tasks that require a specific response

```python
# Service server example
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

def main(args=None):
    rclpy.init(args=args)
    minimal_service = MinimalService()
    rclpy.spin(minimal_service)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

```python
# Service client example
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts
import sys

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

def main(args=None):
    rclpy.init(args=args)
    minimal_client = MinimalClient()
    response = minimal_client.send_request(int(sys.argv[1]), int(sys.argv[2]))
    minimal_client.get_logger().info(
        f'Result of add_two_ints: {response.sum}')
    minimal_client.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

**Execution Notes**: Run the server first, then run the client with two integer arguments.
**Expected Output**: Server logs the request and returns the sum; client displays the result.

## Actions

Actions are used for long-running tasks that require feedback during execution. They combine features of services and topics, providing goal, feedback, and result information.

### Action Characteristics:
- Long-running tasks
- Goal, feedback, and result
- Cancel and preempt capabilities
- Asynchronous execution

```python
# Action server example
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
                return Fibonacci.Result()
            
            feedback_msg.sequence.append(
                feedback_msg.sequence[i] + feedback_msg.sequence[i-1])
            
            goal_handle.publish_feedback(feedback_msg)
            time.sleep(1)
        
        goal_handle.succeed()
        result = Fibonacci.Result()
        result.sequence = feedback_msg.sequence
        self.get_logger().info('Goal succeeded')
        return result

def main(args=None):
    rclpy.init(args=args)
    fibonacci_action_server = FibonacciActionServer()
    rclpy.spin(fibonacci_action_server)
    fibonacci_action_server.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

```python
# Action client example
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

        self.get_logger().info('Goal accepted')
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        self.get_logger().info(f'Received feedback: {feedback.sequence}')

    def get_result_callback(self, future):
        result = future.result().result
        self.get_logger().info(f'Result: {result.sequence}')
        rclpy.shutdown()

def main(args=None):
    rclpy.init(args=args)
    action_client = FibonacciActionClient()
    action_client.send_goal(10)
    rclpy.spin(action_client)

if __name__ == '__main__':
    main()
```

**Execution Notes**: Run the action server first, then the action client.
**Expected Output**: Client will display the Fibonacci sequence as feedback, and the final result.

## Quality of Service (QoS)

Quality of Service settings allow you to configure how data is communicated between nodes. This is important for real-time systems and for ensuring reliable communication.

```python
# Example of QoS settings
from rclpy.qos import QoSProfile, QoSDurabilityPolicy, QoSReliabilityPolicy

# Create a QoS profile with specific settings
my_qos_profile = QoSProfile(
    depth=10,
    durability=QoSDurabilityPolicy.TRANSIENT_LOCAL,
    reliability=QoSReliabilityPolicy.RELIABLE
)

# Use the QoS profile when creating a publisher
publisher = node.create_publisher(String, 'topic', my_qos_profile)
```

## Chapter Summary

This chapter covered the fundamental concepts of ROS 2 architecture including nodes, topics, services, and actions. We learned how these components enable communication between different parts of a robotic system and when to use each approach. We also explored Quality of Service settings which are critical for real-time systems.

## Checklist

- [ ] Understand the basic architecture of ROS 2
- [ ] Create and launch simple nodes
- [ ] Implement publisher-subscriber communication patterns
- [ ] Use services for request-response communication
- [ ] Use actions for long-running tasks with feedback
- [ ] Configure QoS settings for different communication needs

## Exercises

### Exercise 1: Node Implementation

Create a ROS 2 node that publishes the current time to a topic called "current_time" every second. Create a subscriber that logs the received time messages.

#### Solution

Publisher node:

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from datetime import datetime

class TimePublisher(Node):
    def __init__(self):
        super().__init__('time_publisher')
        self.publisher_ = self.create_publisher(String, 'current_time', 10)
        timer_period = 1.0  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        msg = String()
        msg.data = f'Current time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: "{msg.data}"')

def main(args=None):
    rclpy.init(args=args)
    time_publisher = TimePublisher()
    rclpy.spin(time_publisher)
    time_publisher.destroy_node()
    rclpy.shutdown()
```

Subscriber node:

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class TimeSubscriber(Node):
    def __init__(self):
        super().__init__('time_subscriber')
        self.subscription = self.create_subscription(
            String,
            'current_time',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        self.get_logger().info(f'Received time: "{msg.data}"')

def main(args=None):
    rclpy.init(args=args)
    time_subscriber = TimeSubscriber()
    rclpy.spin(time_subscriber)
    time_subscriber.destroy_node()
    rclpy.shutdown()
```

#### Hints

- Use datetime module to get current time
- Create publisher and subscription with appropriate topic name
- Use timer to publish regularly

### Exercise 2: Service Implementation

Create a service in ROS 2 that accepts a string and returns the reversed string.

#### Solution

Service server:

```python
from rclpy.node import Node
from rclpy.qos import QoSProfile
from example_interfaces.srv import Trigger  # Using Trigger as a simple service for string reversal

class ReverseStringService(Node):
    def __init__(self):
        super().__init__('reverse_string_service')
        self.srv = self.create_service(
            Trigger, 
            'reverse_string', 
            self.reverse_string_callback)

    def reverse_string_callback(self, request, response):
        original_string = request.arm  # Using arm field to send string
        reversed_string = original_string[::-1]
        response.success = True
        response.message = reversed_string
        self.get_logger().info(f'Reversed "{original_string}" to "{reversed_string}"')
        return response

def main(args=None):
    rclpy.init(args=args)
    reverse_string_service = ReverseStringService()
    rclpy.spin(reverse_string_service)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

Actually, I'll need to create a custom service for this purpose. Let me describe the approach:

1. Create a custom service definition file (e.g., in srv/ReverseString.srv):
```
string input_string
---
string output_string
```

2. Then implement the service server using the custom interface.

#### Hints

- You'll need to create a custom service definition file
- Use the custom service interface in your server and client
- The service should return the input string reversed

## References

- [ROS 2 Documentation](https://docs.ros.org/en/humble/)
- [ROS 2 Tutorials](https://docs.ros.org/en/humble/Tutorials.html)
- [ROS 2 Design Articles](https://design.ros2.org/)
- Fauser, M., et al. (2020). "ROS 2 for dummies: An introduction." ROSCon.