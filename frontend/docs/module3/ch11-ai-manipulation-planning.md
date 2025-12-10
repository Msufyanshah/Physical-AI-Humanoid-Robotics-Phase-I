---
title: 'Chapter 11 - AI-Powered Manipulation & Bipedal Planning'
description: 'Advanced AI techniques for robot manipulation and bipedal locomotion planning'
---

# Chapter 11: AI-Powered Manipulation & Bipedal Planning

## Learning Objectives

After reading this chapter, you will be able to:
- Understand AI-based approaches for robotic manipulation
- Implement learning-based grasping and manipulation systems
- Develop bipedal walking controllers using AI techniques
- Create motion planning algorithms that incorporate learning
- Integrate perception and action for manipulation tasks
- Evaluate and validate AI-powered manipulation and locomotion
- Optimize AI controllers for real-time robot operation

## Introduction

AI-powered manipulation and bipedal planning represent the frontier of robotics, where artificial intelligence techniques enable robots to perform complex physical tasks with human-like dexterity and adaptability. This chapter explores how deep learning, reinforcement learning, and other AI techniques can be applied to enable robots to grasp objects robustly and walk with stable, adaptive gaits.

## AI-Powered Manipulation

### Traditional vs. AI-Based Manipulation

Traditional robotic manipulation relies on:
- Precise forward and inverse kinematics
- Explicit path planning in configuration space
- Hard-coded grasping strategies
- Deterministic control laws

AI-based manipulation utilizes:
- Learning from experience and demonstration
- Adaptive grasping strategies
- End-to-end learning approaches
- Robust control in uncertain environments

### Deep Learning for Grasping

Deep learning has revolutionized robotic grasping by enabling robots to learn grasping strategies from data:

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, PointCloud2
from geometry_msgs.msg import Pose, Point
from std_msgs.msg import Float64MultiArray
from cv_bridge import CvBridge
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import cv2


class GraspNet(nn.Module):
    def __init__(self, input_channels=3):
        super(GraspNet, self).__init__()
        
        # Convolutional layers for feature extraction
        self.conv1 = nn.Conv2d(input_channels, 32, kernel_size=5, stride=2)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=5, stride=2)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, stride=2)
        
        # Calculate the size of flattened features
        conv_output_size = 128 * 8 * 8  # Assuming input is 128x128
        
        # Fully connected layers for grasp prediction
        self.fc1 = nn.Linear(conv_output_size, 512)
        self.fc2 = nn.Linear(512, 256)
        
        # Output: grasp quality (0-1) and grasp angle (in radians)
        self.fc_quality = nn.Linear(256, 1)
        self.fc_angle = nn.Linear(256, 1)
        
    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = F.relu(self.conv3(x))
        
        x = x.view(x.size(0), -1)  # Flatten
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        
        quality = torch.sigmoid(self.fc_quality(x))  # Grasp quality [0, 1]
        angle = torch.tanh(self.fc_angle(x)) * np.pi  # Grasp angle [-π, π]
        
        return quality, angle


class DeepGraspingNode(Node):
    def __init__(self):
        super().__init__('deep_grasping')
        
        self.bridge = CvBridge()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Load pre-trained grasp network
        self.grasp_net = GraspNet(input_channels=4)  # RGB + depth
        # In practice, you would load a trained model here
        # self.grasp_net.load_state_dict(torch.load('grasp_model.pth'))
        self.grasp_net.to(self.device)
        self.grasp_net.eval()
        
        # Robot state
        self.current_image = None
        self.current_depth = None
        self.camera_matrix = None
        
        # Subscribers
        self.image_sub = self.create_subscription(
            Image,
            '/camera/rgb/image_raw',
            self.image_callback,
            10
        )
        
        self.depth_sub = self.create_subscription(
            Image,
            '/camera/depth/image_raw',
            self.depth_callback,
            10
        )
        
        # Publishers
        self.grasp_candidate_pub = self.create_publisher(
            Float64MultiArray,
            '/grasp_candidates',
            10
        )
        
        # Timer for grasp detection
        self.grasp_timer = self.create_timer(1.0, self.detect_grasps)
    
    def image_callback(self, msg):
        """Process RGB image for grasping"""
        try:
            self.current_image = self.bridge.imgmsg_to_cv2(msg, 'rgb8')
        except Exception as e:
            self.get_logger().error(f"Error processing image: {e}")
    
    def depth_callback(self, msg):
        """Process depth image for grasping"""
        try:
            self.current_depth = self.bridge.imgmsg_to_cv2(msg, 'passthrough')
        except Exception as e:
            self.get_logger().error(f"Error processing depth: {e}")
    
    def preprocess_input(self, rgb_image, depth_image):
        """Preprocess RGB and depth images for the network"""
        # Resize images to network input size
        input_size = (128, 128)
        rgb_resized = cv2.resize(rgb_image, input_size)
        depth_resized = cv2.resize(depth_image, input_size)
        
        # Normalize RGB image
        rgb_normalized = rgb_resized.astype(np.float32) / 255.0
        
        # Normalize depth image (assuming 10 meter max range)
        depth_normalized = depth_resized.astype(np.float32) / 10.0
        
        # Stack RGB and depth
        input_tensor = np.concatenate([
            rgb_normalized,
            np.expand_dims(depth_normalized, axis=2)  # Add channel dimension
        ], axis=2)
        
        # Change to CHW format (channel, height, width)
        input_tensor = np.transpose(input_tensor, (2, 0, 1))
        
        # Add batch dimension
        input_tensor = np.expand_dims(input_tensor, axis=0)
        
        return torch.tensor(input_tensor, dtype=torch.float32).to(self.device)
    
    def detect_grasps(self):
        """Detect potential grasp points using deep network"""
        if self.current_image is None or self.current_depth is None:
            return
        
        # Preprocess input
        input_tensor = self.preprocess_input(self.current_image, self.current_depth)
        
        # Run inference
        with torch.no_grad():
            quality, angle = self.grasp_net(input_tensor)
        
        # Convert to numpy for further processing
        grasp_quality = quality.cpu().numpy()[0, 0]
        grasp_angle = angle.cpu().numpy()[0, 0]
        
        # Publish grasp candidates
        grasp_msg = Float64MultiArray()
        grasp_msg.data = [float(grasp_quality), float(grasp_angle)]
        
        self.grasp_candidate_pub.publish(grasp_msg)
        
        self.get_logger().info(
            f"Grasp detected: quality={grasp_quality:.3f}, angle={grasp_angle:.3f}rad"
        )


def main(args=None):
    rclpy.init(args=args)
    grasping_node = DeepGraspingNode()
    
    try:
        rclpy.spin(grasping_node)
    except KeyboardInterrupt:
        pass
    finally:
        grasping_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### Reinforcement Learning for Manipulation

Reinforcement learning can be used to teach robots complex manipulation skills through trial and error:

```python
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
from collections import deque


class ManipulationActorCritic(nn.Module):
    def __init__(self, state_dim, action_dim, max_action):
        super(ManipulationActorCritic, self).__init__()
        
        # Actor network (policy)
        self.actor = nn.Sequential(
            nn.Linear(state_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 256),
            nn.ReLU(),
            nn.Linear(256, action_dim),
            nn.Tanh()
        )
        
        # Critic network (value function)
        self.critic = nn.Sequential(
            nn.Linear(state_dim + action_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 256),
            nn.ReLU(),
            nn.Linear(256, 1)
        )
        
        self.max_action = max_action

    def forward(self, state, action):
        # Critic forward pass
        sa = torch.cat([state, action], 1)
        q_value = self.critic(sa)
        return q_value

    def get_action(self, state):
        # Actor forward pass
        action = self.actor(state)
        return action * self.max_action


class ManipulationReinforcementLearning:
    def __init__(self, state_dim, action_dim, max_action=1.0):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        self.actor_critic = ManipulationActorCritic(state_dim, action_dim, max_action).to(self.device)
        self.optimizer = optim.Adam(self.actor_critic.parameters(), lr=1e-3)
        
        self.replay_buffer = deque(maxlen=100000)
        self.batch_size = 64
        
    def store_transition(self, state, action, reward, next_state, done):
        """Store experience in replay buffer"""
        self.replay_buffer.append((state, action, reward, next_state, done))
    
    def train(self):
        """Train the actor-critic network"""
        if len(self.replay_buffer) < self.batch_size:
            return
        
        # Sample batch from replay buffer
        batch = random.sample(self.replay_buffer, self.batch_size)
        state_batch, action_batch, reward_batch, next_state_batch, done_batch = map(
            torch.FloatTensor, zip(*batch)
        )
        
        state_batch = state_batch.to(self.device)
        action_batch = action_batch.to(self.device)
        reward_batch = reward_batch.to(self.device).unsqueeze(1)
        next_state_batch = next_state_batch.to(self.device)
        done_batch = done_batch.to(self.device).unsqueeze(1)
        
        # Compute target Q value
        with torch.no_grad():
            next_action = self.actor_critic.get_action(next_state_batch)
            target_q = reward_batch + (1 - done_batch) * 0.99 * self.actor_critic(next_state_batch, next_action)
        
        # Compute current Q value
        current_q = self.actor_critic(state_batch, action_batch)
        
        # Compute critic loss
        critic_loss = nn.MSELoss()(current_q, target_q)
        
        # Compute actor loss
        predicted_action = self.actor_critic.get_action(state_batch)
        actor_loss = -self.actor_critic(state_batch, predicted_action).mean()
        
        # Update networks
        self.optimizer.zero_grad()
        (critic_loss + actor_loss).backward()
        self.optimizer.step()


class RLGraspingNode(Node):
    def __init__(self):
        super().__init__('rl_grasping')
        
        # Initialize RL agent
        # State: [robot_position, object_position, gripper_state, ...]
        # Action: [dx, dy, dz, gripper_width]
        self.rl_agent = ManipulationReinforcementLearning(
            state_dim=10,  # Example: 3D position + 3D orientation + object info
            action_dim=4,  # Move in 3D + gripper control
            max_action=0.1  # Max movement per step (10cm)
        )
        
        # Robot simulation interface
        self.robot_state = None
        self.object_state = None
        self.gripper_state = None
        
        # Episode tracking
        self.episode_step = 0
        self.max_episode_steps = 100
        self.episode_reward = 0.0
        self.is_training = True
        
        # Timer for RL control loop
        self.rl_timer = self.create_timer(0.1, self.rl_control_loop)
    
    def get_robot_state(self):
        """Get current robot state for RL algorithm"""
        # In practice, this would interface with the robot
        # For now, return dummy values
        return np.random.rand(10).astype(np.float32)  # 10-dim state
    
    def execute_action(self, action):
        """Execute RL action on the robot"""
        # Convert action to robot commands
        dx, dy, dz, gripper_cmd = action
        
        # In practice, send commands to robot
        # For now, just log the action
        self.get_logger().info(f"Executing action: [{dx:.3f}, {dy:.3f}, {dz:.3f}, {gripper_cmd:.3f}]")
        
        # Simulate the action (in a real system, this would be done on the actual robot)
        self.robot_state[0] += dx  # Update X position
        self.robot_state[1] += dy  # Update Y position
        self.robot_state[2] += dz  # Update Z position
    
    def calculate_reward(self):
        """Calculate reward based on current state"""
        # In practice, this would be based on the actual task
        # For grasping, reward could be based on:
        # - Distance to object
        # - Gripper position relative to object
        # - Successful grasp detection
        
        # Simple example reward: negative distance to target
        if self.robot_state is not None and self.object_state is not None:
            distance = np.linalg.norm(
                self.robot_state[:3] - self.object_state[:3]
            )
            reward = -distance  # Negative reward for distance
        else:
            reward = 0.0
        
        return reward
    
    def rl_control_loop(self):
        """Main RL control loop"""
        # Get current state
        current_state = self.get_robot_state()
        
        # Get action from RL agent
        state_tensor = torch.FloatTensor(current_state).unsqueeze(0).to(self.rl_agent.device)
        action_tensor = self.rl_agent.actor_critic.get_action(state_tensor)
        action = action_tensor.cpu().numpy()[0]
        
        # Execute action
        self.execute_action(action)
        
        # Calculate reward
        reward = self.calculate_reward()
        self.episode_reward += reward
        
        # Check if episode is done (max steps reached or other termination condition)
        self.episode_step += 1
        done = self.episode_step >= self.max_episode_steps
        
        # Store transition if not in first step
        if hasattr(self, 'previous_state'):
            self.rl_agent.store_transition(
                self.previous_state,
                self.previous_action,
                reward,
                current_state,
                done
            )
            
            # Train the agent
            if self.is_training:
                self.rl_agent.train()
        
        # Store current state and action for next iteration
        self.previous_state = current_state
        self.previous_action = action
        
        if done:
            # Episode finished, reset
            self.get_logger().info(f"Episode finished. Total reward: {self.episode_reward:.3f}")
            self.episode_step = 0
            self.episode_reward = 0.0


def main(args=None):
    rclpy.init(args=args)
    rl_grasping_node = RLGraspingNode()
    
    try:
        rclpy.spin(rl_grasping_node)
    except KeyboardInterrupt:
        pass
    finally:
        rl_grasping_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Bipedal Planning and Control

### Dynamics of Bipedal Locomotion

Bipedal locomotion presents unique challenges due to the underactuated nature of walking (the feet are not powered) and the need to maintain balance while moving:

1. **Zero Moment Point (ZMP)**: Critical for balance control
2. **Capture Point**: Predicts where to place feet to stop
3. **Linear Inverted Pendulum Model (LIPM)**: Simplified model for walking
4. **Foot placement strategies**: Critical for stability

### Model Predictive Control (MPC) for Walking

```python
import numpy as np
from scipy.optimize import minimize
from math import sqrt


class BipedalMPCController:
    def __init__(self, robot_mass=70.0, gravity=9.81, com_height=0.85):
        self.mass = robot_mass
        self.gravity = gravity
        self.com_height = com_height
        self.omega = sqrt(gravity / com_height)  # Natural frequency of inverted pendulum
        
        # Walking parameters
        self.step_length = 0.3  # 30 cm step
        self.step_width = 0.2  # 20 cm step width
        self.step_duration = 1.0  # 1 second per step
        self.dt = 0.01  # 10ms control cycle
        
        # MPC parameters
        self.prediction_horizon = 20  # 20 steps ahead
        self.control_horizon = 5  # 5 control steps
    
    def linear_inverted_pendulum_model(self, x, y, x_dot, y_dot, zmp_x, zmp_y):
        """Update CoM state using Linear Inverted Pendulum Model"""
        com_x_ddot = self.omega**2 * (x - zmp_x)
        com_y_ddot = self.omega**2 * (y - zmp_y)
        
        # Integrate
        x_dot += com_x_ddot * self.dt
        y_dot += com_y_ddot * self.dt
        x += x_dot * self.dt
        y += y_dot * self.dt
        
        return x, y, x_dot, y_dot
    
    def mpc_objective(self, zmp_sequence, current_state, desired_trajectory):
        """Objective function for MPC optimization"""
        # Current state: [com_x, com_y, com_x_dot, com_y_dot]
        x, y, x_dot, y_dot = current_state
        
        total_cost = 0.0
        
        for i in range(self.prediction_horizon):
            zmp_x, zmp_y = zmp_sequence[i*2], zmp_sequence[i*2+1]
            
            # Update state
            x, y, x_dot, y_dot = self.linear_inverted_pendulum_model(
                x, y, x_dot, y_dot, zmp_x, zmp_y
            )
            
            # Cost: deviation from desired trajectory
            desired_x, desired_y = desired_trajectory[i]
            total_cost += (x - desired_x)**2 + (y - desired_y)**2
        
        # Add control effort penalty
        for i in range(self.control_horizon):
            zmp_x, zmp_y = zmp_sequence[i*2], zmp_sequence[i*2+1]
            total_cost += 0.01 * (zmp_x**2 + zmp_y**2)
        
        return total_cost
    
    def plan_step(self, current_com_state, current_support_foot, desired_trajectory):
        """Plan next step using MPC"""
        # Initial ZMP sequence (current ZMP repeated)
        initial_zmp = np.zeros(2 * self.prediction_horizon)
        
        # Optimize ZMP trajectory
        result = minimize(
            self.mpc_objective,
            initial_zmp,
            args=(current_com_state, desired_trajectory),
            method='SLSQP',
            options={'disp': False}
        )
        
        optimal_zmp_sequence = result.x
        
        # Extract next support foot position based on ZMP
        next_zmp_x = optimal_zmp_sequence[0]
        next_zmp_y = optimal_zmp_sequence[1]
        
        # For simple walking, alternate feet
        # In practice, this would consider balance margins and step constraints
        next_support_position = np.array([next_zmp_x, next_zmp_y, 0.0])
        
        return next_support_position, optimal_zmp_sequence


class BipedalWalkingNode(Node):
    def __init__(self):
        super().__init__('bipedal_walking')
        
        # Initialize MPC controller
        self.mpc_controller = BipedalMPCController()
        
        # Robot state
        self.com_state = np.array([0.0, 0.0, 0.0, 0.0])  # [x, y, x_dot, y_dot]
        self.support_foot = np.array([0.0, 0.0, 0.0])  # Left foot position
        self.in_left_support = True  # Which foot is supporting
        
        # Walking trajectory
        self.walk_trajectory = []  # Planned walking path
        self.trajectory_index = 0
        
        # Create publishers for joint commands
        self.left_leg_pub = self.create_publisher(Float64MultiArray, '/left_leg/commands', 10)
        self.right_leg_pub = self.create_publisher(Float64MultiArray, '/right_leg/commands', 10)
        
        # Walking timer
        self.walk_timer = self.create_timer(0.01, self.walk_control_loop)
    
    def generate_walk_trajectory(self, start_pos, steps_count=10):
        """Generate a simple forward walking trajectory"""
        self.walk_trajectory = []
        
        step_length = 0.3  # 30cm per step
        
        for i in range(steps_count):
            # Simple straight line walking
            x = start_pos[0] + (i + 1) * step_length
            y = start_pos[1]  # Stay on same y
            self.walk_trajectory.append([x, y])
        
        self.trajectory_index = 0
    
    def walk_control_loop(self):
        """Main walking control loop"""
        if not self.walk_trajectory:
            # Generate a simple walk forward
            self.generate_walk_trajectory([0.0, 0.0])
            return
        
        if self.trajectory_index >= len(self.walk_trajectory):
            # Reached end of trajectory, stop walking
            self.get_logger().info("Reached end of walking trajectory")
            self.stop_walking()
            return
        
        # Get desired position for the next few steps
        desired_positions = []
        for i in range(min(10, len(self.walk_trajectory) - self.trajectory_index)):
            desired_positions.append(self.walk_trajectory[self.trajectory_index + i])
        
        # Plan next step using MPC
        next_foot_pos, zmp_sequence = self.mpc_controller.plan_step(
            self.com_state,
            self.support_foot,
            desired_positions
        )
        
        # Execute next step
        self.execute_step(next_foot_pos)
        
        # Update which foot is supporting
        self.in_left_support = not self.in_left_support
        self.support_foot = next_foot_pos
        
        # Update trajectory index
        self.trajectory_index += 1
    
    def execute_step(self, target_foot_pos):
        """Execute the planned step using joint control"""
        # In practice, this would convert foot position to joint angles
        # For now, just log the step
        self.get_logger().info(f"Stepping to: [{target_foot_pos[0]:.3f}, {target_foot_pos[1]:.3f}, {target_foot_pos[2]:.3f}]")
        
        # Calculate joint angles for target foot position
        # This would involve inverse kinematics in a real implementation
        left_leg_cmd = Float64MultiArray()
        right_leg_cmd = Float64MultiArray()
        
        # Placeholder joint angles (in practice, calculate from IK)
        if self.in_left_support:
            # Right leg moves to target position
            right_leg_cmd.data = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  # 6 DOF joints
        else:
            # Left leg moves to target position
            left_leg_cmd.data = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  # 6 DOF joints
        
        # Publish commands
        if len(right_leg_cmd.data) > 0:
            self.right_leg_pub.publish(right_leg_cmd)
        if len(left_leg_cmd.data) > 0:
            self.left_leg_pub.publish(left_leg_cmd)
    
    def stop_walking(self):
        """Stop the walking motion"""
        stop_cmd = Float64MultiArray()
        stop_cmd.data = [0.0] * 6  # Zero all joint velocities
        
        self.left_leg_pub.publish(stop_cmd)
        self.right_leg_pub.publish(stop_cmd)


def main(args=None):
    rclpy.init(args=args)
    walking_node = BipedalWalkingNode()
    
    try:
        rclpy.spin(walking_node)
    except KeyboardInterrupt:
        pass
    finally:
        walking_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### Deep Reinforcement Learning for Bipedal Walking

Deep reinforcement learning has shown great success in learning complex bipedal locomotion:

```python
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np


class BipedalPolicyNetwork(nn.Module):
    def __init__(self, state_dim, action_dim):
        super(BipedalPolicyNetwork, self).__init__()
        
        # Shared layers
        self.shared_layers = nn.Sequential(
            nn.Linear(state_dim, 512),
            nn.ReLU(),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU()
        )
        
        # Policy head (actor)
        self.policy_mean = nn.Linear(128, action_dim)
        self.policy_std = nn.Linear(128, action_dim)
        
        # Value head (critic)
        self.value = nn.Linear(128, 1)
    
    def forward(self, state):
        features = self.shared_layers(state)
        
        # Policy (mean and std for continuous action space)
        action_mean = torch.tanh(self.policy_mean(features))  # Actions in [-1, 1]
        action_std = torch.sigmoid(self.policy_std(features)) + 1e-5  # Avoid zero std
        
        # Value
        value = self.value(features)
        
        return action_mean, action_std, value


class PPOAgent:
    def __init__(self, state_dim, action_dim, lr=3e-4, gamma=0.99, eps_clip=0.2):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        self.actor_critic = BipedalPolicyNetwork(state_dim, action_dim).to(self.device)
        self.optimizer = optim.Adam(self.actor_critic.parameters(), lr=lr)
        
        self.gamma = gamma
        self.eps_clip = eps_clip
        self.C_entropy = 0.01  # Entropy coefficient
    
    def get_action(self, state):
        """Get action from policy"""
        state = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        
        action_mean, action_std, value = self.actor_critic(state)
        
        # Sample action from normal distribution
        dist = torch.distributions.Normal(action_mean, action_std)
        action = dist.sample()
        action_log_prob = dist.log_prob(action).sum(dim=1)
        
        return action.cpu().numpy()[0], action_log_prob.cpu().numpy()[0], value.cpu().numpy()[0]
    
    def evaluate(self, state, action):
        """Evaluate state-action pair"""
        action_mean, action_std, value = self.actor_critic(state)
        
        dist = torch.distributions.Normal(action_mean, action_std)
        action_logprobs = dist.log_prob(action).sum(dim=1, keepdim=True)
        dist_entropy = dist.entropy().sum(dim=1).mean()
        
        return action_logprobs, torch.squeeze(value, 1), dist_entropy


class DRLBipedalNode(Node):
    def __init__(self):
        super().__init__('drl_bipedal')
        
        # Initialize RL agent
        # State: [com_pos, com_vel, joint_angles, joint_velocities, external_forces, ...]
        # Action: [torques for each joint]
        self.rl_agent = PPOAgent(
            state_dim=40,  # Example state dimension
            action_dim=12  # Example action dimension (6 joints per leg)
        )
        
        # Robot simulation interface
        self.robot_state = np.zeros(40)  # Placeholder for robot state
        self.action_buffer = []
        
        # Training parameters
        self.episode_reward = 0.0
        self.episode_step = 0
        self.max_episode_steps = 2000
        self.is_training = True
        
        # Timer for RL control
        self.rl_timer = self.create_timer(0.02, self.rl_control_loop)  # 50Hz control
    
    def get_robot_state(self):
        """Get current robot state for RL algorithm"""
        # In practice, this would interface with the physical or simulated robot
        # For now, return a realistic state representation
        
        # Example state components:
        # - Center of mass position and velocity
        # - Joint angles and velocities
        # - IMU readings
        # - Touch sensor data
        # - Previous actions
        
        state = np.zeros(40)
        
        # Fill with some dummy data (in practice, read from robot)
        # CoM position (3) + velocity (3) = 6
        # Joint angles for 12 joints (12) + velocities (12) = 24
        # IMU data (6) + touch sensors (2) + previous actions (2) = 10
        # Total: 6 + 24 + 10 = 40
        
        for i in range(len(state)):
            state[i] = np.random.normal(0, 0.1)  # Small random values
        
        return state
    
    def send_action_to_robot(self, action):
        """Send action to robot"""
        # Convert action to joint torques or positions
        # In practice, this would interface with actual robot controllers
        self.get_logger().info(f"Action sent: [{action[:3]}...]")  # Log first 3 actions
        
        # For demonstration, just update the internal state
        # In real robot, this would send commands to actuators
    
    def calculate_reward(self):
        """Calculate reward for current state"""
        # In practice, this would be based on actual robot performance
        # For bipedal walking, common reward components are:
        # - Forward progress
        # - Upright posture
        # - Energy efficiency
        # - Balance stability
        
        # Example reward calculation (simplified):
        forward_velocity = self.robot_state[3]  # Assuming 4th element is CoM x-velocity
        
        # Reward for moving forward
        forward_reward = max(0, forward_velocity) * 10
        
        # Penalty for falling (if z-position of CoM drops too low)
        com_z = self.robot_state[2]  # Assuming 3rd element is CoM z-position
        fall_penalty = 0 if com_z > 0.5 else -10  # Heavily penalize falling
        
        # Reward for staying upright
        upright_reward = 0  # Simplified - in practice consider IMU angles
        
        # Combine rewards
        total_reward = forward_reward + fall_penalty + upright_reward
        
        return total_reward
    
    def rl_control_loop(self):
        """Main RL control loop"""
        # Get current state
        self.robot_state = self.get_robot_state()
        
        # Get action from policy
        action, action_log_prob, state_value = self.rl_agent.get_action(self.robot_state)
        
        # Execute action
        self.send_action_to_robot(action)
        
        # Calculate reward
        reward = self.calculate_reward()
        self.episode_reward += reward
        
        # Check if episode ended
        self.episode_step += 1
        done = (self.episode_step >= self.max_episode_steps or 
                self.robot_state[2] < 0.3)  # Fall detection
        
        if done:
            self.get_logger().info(f"Episode ended. Total reward: {self.episode_reward:.2f}")
            self.episode_step = 0
            self.episode_reward = 0.0


def main(args=None):
    rclpy.init(args=args)
    bipedal_node = DRLBipedalNode()
    
    try:
        rclpy.spin(bipedal_node)
    except KeyboardInterrupt:
        pass
    finally:
        bipedal_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Integration of Perception and Action

### Perception-Action Loop

For intelligent manipulation, perception and action must be tightly integrated:

```python
# perception_action_integration.py
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, PointCloud2, LaserScan
from geometry_msgs.msg import PoseStamped, Point
from std_msgs.msg import String
from vision_msgs.msg import Detection2DArray
from tf2_ros import TransformListener, Buffer
from collections import deque
import numpy as np
import cv2


class PerceptionActionNode(Node):
    def __init__(self):
        super().__init__('perception_action')
        
        # Initialize TF
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        
        # Perception data
        self.detections = deque(maxlen=10)
        self.point_cloud = None
        self.laser_data = None
        self.camera_pose = None
        
        # Action planning
        self.current_task = "idle"
        self.task_queue = deque()
        self.reach_targets = deque(maxlen=5)
        
        # Subscribers
        self.detection_sub = self.create_subscription(
            Detection2DArray, '/object_detections', 
            self.detection_callback, 10
        )
        
        self.pc_sub = self.create_subscription(
            PointCloud2, '/camera/depth/points',
            self.pointcloud_callback, 10
        )
        
        self.laser_sub = self.create_subscription(
            LaserScan, '/laser_scan',
            self.laser_callback, 10
        )
        
        # Publishers
        self.task_pub = self.create_publisher(String, '/robot_tasks', 10)
        self.reach_pub = self.create_publisher(PoseStamped, '/reach_target', 10)
        
        # Timer for integrated loop
        self.integrated_timer = self.create_timer(0.1, self.integrated_loop)
    
    def detection_callback(self, msg):
        """Process object detections"""
        # Store recent detections
        for detection in msg.detections:
            # Convert 2D detection to 3D using depth information
            if self.camera_pose and self.point_cloud:
                # This is a simplified example - in practice, 
                # you'd use depth from the camera
                target_3d = self.project_2d_detection_to_3d(
                    detection.bbox.center.x,
                    detection.bbox.center.y,
                    detection.bbox.size_x,
                    detection.bbox.size_y
                )
                
                if target_3d is not None:
                    self.reach_targets.append(target_3d)
    
    def project_2d_detection_to_3d(self, x_2d, y_2d, w_2d, h_2d):
        """Project 2D detection to 3D world coordinate"""
        # In practice, you'd use the depth image or point cloud
        # to get the actual 3D position
        
        # Simplified projection using camera intrinsics
        # This is a placeholder implementation
        if self.camera_pose:
            # Calculate 3D position based on detection and depth
            # For now, return a placeholder
            return np.array([x_2d * 0.001, y_2d * 0.001, 1.0])  # Placeholder depth
        
        return None
    
    def pointcloud_callback(self, msg):
        """Process point cloud data"""
        # Convert PointCloud2 to array for processing
        # This is a simplified approach
        self.point_cloud = msg
    
    def laser_callback(self, msg):
        """Process laser data"""
        self.laser_data = msg
    
    def integrated_loop(self):
        """Main integrated perception-action loop"""
        if self.reach_targets:
            # Process the oldest target
            target = self.reach_targets.popleft()
            
            # Check if target is valid and reachable
            if self.is_reachable(target):
                # Publish reach target to robot controller
                pose_msg = PoseStamped()
                pose_msg.header.frame_id = 'map'  # Or appropriate frame
                pose_msg.header.stamp = self.get_clock().now().to_msg()
                pose_msg.pose.position.x = float(target[0])
                pose_msg.pose.position.y = float(target[1])
                pose_msg.pose.position.z = float(target[2])
                pose_msg.pose.orientation.w = 1.0  # No rotation
                
                self.reach_pub.publish(pose_msg)
                
                self.get_logger().info(f"Reaching target: [{target[0]:.3f}, {target[1]:.3f}, {target[2]:.3f}]")
    
    def is_reachable(self, target):
        """Check if target is within robot's reach"""
        # In practice, check robot kinematics and joint limits
        # For now, use a simple distance check
        robot_pos = np.array([0, 0, 1])  # Placeholder robot position
        distance = np.linalg.norm(target - robot_pos)
        
        # Assume robot can reach up to 1 meter away
        return distance < 1.0
    
    def evaluate_task_completion(self):
        """Evaluate if current task is completed"""
        # Check if manipulation action was successful
        # This would involve checking robot state, gripper feedback, etc.
        return False


def main(args=None):
    rclpy.init(args=args)
    perception_action_node = PerceptionActionNode()
    
    try:
        rclpy.spin(perception_action_node)
    except KeyboardInterrupt:
        pass
    finally:
        perception_action_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Performance Evaluation and Validation

### Metrics for AI-Powered Systems

For evaluating AI-powered manipulation and locomotion:

#### Manipulation Metrics:
- **Success Rate**: Percentage of successful grasps/placements
- **Grasp Quality**: Force closure, grasp stability
- **Task Completion Time**: How quickly tasks are completed
- **Energy Efficiency**: Power consumption for tasks

#### Locomotion Metrics:
- **Walking Speed**: Average forward velocity
- **Stability**: Zero moment point (ZMP) variance, fall rate
- **Energy Efficiency**: Cost of transport
- **Adaptability**: Ability to handle terrain variations

### Validation Framework

```python
# validation_framework.py
import numpy as np


class ManipulationValidation:
    def __init__(self):
        self.grasp_successes = []
        self.grasp_attempts = []
        self.task_completion_times = []
        self.trajectory_errors = []
    
    def validate_grasping(self, grasp_positions, successful_grasps):
        """Validate grasping performance"""
        success_rate = np.sum(successful_grasps) / len(successful_grasps) if successful_grasps else 0
        
        # Calculate grasp quality metrics
        if grasp_positions:
            grasp_variance = np.var(grasp_positions, axis=0)  # Variance of grasp positions
        else:
            grasp_variance = np.zeros(3)
        
        return {
            'success_rate': success_rate,
            'grasp_variance': grasp_variance,
            'average_position_error': np.mean(self.trajectory_errors) if self.trajectory_errors else 0
        }
    
    def validate_task_completion(self, task_times):
        """Validate task completion performance"""
        return {
            'avg_completion_time': np.mean(task_times) if task_times else float('inf'),
            'completion_success_rate': len([t for t in task_times if t < 60]) / len(task_times) if task_times else 0,  # Tasks completed under 60s
            'std_completion_time': np.std(task_times) if task_times else 0
        }


class LocomotionValidation:
    def __init__(self):
        self.step_lengths = []
        self.step_times = []
        self.com_stability = []
        self.fall_rates = []
    
    def validate_walking(self, step_data, stability_data, fall_count, total_steps):
        """Validate walking performance"""
        avg_step_length = np.mean(step_data) if step_data else 0
        avg_step_time = np.mean(self.step_times) if self.step_times else 1.0
        avg_com_deviation = np.mean(stability_data) if stability_data else 0
        fall_rate = fall_count / total_steps if total_steps > 0 else 0
        
        return {
            'avg_step_length': avg_step_length,
            'walking_speed': avg_step_length / avg_step_time,
            'balance_stability': avg_com_deviation,
            'fall_rate': fall_rate
        }
    
    def calculate_energy_efficiency(self, force_data, velocity_data):
        """Calculate energy efficiency"""
        # Simplified energy calculation
        # In practice, consider motor currents, joint torques, etc.
        if len(force_data) > 0 and len(velocity_data) > 0:
            # Energy = Force * Velocity (simplified)
            energy = np.sum(np.abs(np.multiply(force_data, velocity_data)))
            return energy
        return 0


# Example usage
manip_validator = ManipulationValidation()
loco_validator = LocomotionValidation()

# Simulate some validation data
grasp_positions = np.random.rand(10, 3) * 0.1  # Small variance in grasp positions
successful_grasps = [True, True, False, True, True, False, True, True, True, True]
manip_metrics = manip_validator.validate_grasping(grasp_positions, successful_grasps)

print(f"Manipulation Success Rate: {manip_metrics['success_rate']:.2f}")
print(f"Grasp Variance: {manip_metrics['grasp_variance']}")
```

## Optimization and Real-Time Considerations

### Performance Optimization Techniques

For real-time AI-powered robot control:

1. **Model Optimization**: Quantization, pruning, distillation
2. **Hardware Acceleration**: GPU, TPU, dedicated inference chips
3. **Efficient Algorithms**: Lightweight models, algorithmic improvements
4. **Control Frequency Management**: Task-based prioritization

### Real-Time Control Architecture

```python
# real_time_control.py
import threading
import time
import numpy as np


class RealTimeBipedalController:
    def __init__(self, control_frequency=500):  # 500 Hz for balance
        self.control_frequency = control_frequency
        self.control_period = 1.0 / control_frequency
        
        # Control threads
        self.balance_thread = threading.Thread(target=self.balance_control_loop)
        self.walk_thread = threading.Thread(target=self.walk_planning_loop)
        self.perception_thread = threading.Thread(target=self.perception_loop)
        
        # Robot state
        self.robot_state = {
            'com': np.zeros(3),
            'com_dot': np.zeros(3),
            'joint_positions': np.zeros(12),
            'joint_velocities': np.zeros(12),
            'imu_data': np.zeros(6)
        }
        
        # Control parameters
        self.balance_gains = {'p': 100, 'd': 10}  # PD controller gains
        self.max_torque = 100  # Nm
        
        # Threading control
        self.running = True
    
    def balance_control_loop(self):
        """High-frequency balance control loop"""
        last_time = time.time()
        
        while self.running:
            current_time = time.time()
            dt = current_time - last_time
            
            if dt >= self.control_period:
                # Perform balance control calculations
                torques = self.compute_balance_torques()
                
                # Apply torques to robot (in practice, send to actuators)
                self.apply_torques(torques)
                
                last_time = current_time
            else:
                # Sleep for remaining time to maintain frequency
                time.sleep(max(0, self.control_period - dt))
    
    def compute_balance_torques(self):
        """Compute balance torques using PD control"""
        # Simple PD control for balance (ZMP-based in practice)
        desired_com = np.array([0.0, 0.0, self.robot_state['com'][2]])  # Keep Z constant
        pos_error = desired_com - self.robot_state['com']
        vel_error = -self.robot_state['com_dot']
        
        # Generate torques based on error
        torques = (self.balance_gains['p'] * pos_error + 
                  self.balance_gains['d'] * vel_error)
        
        # Limit torques
        torques = np.clip(torques, -self.max_torque, self.max_torque)
        
        return torques
    
    def apply_torques(self, torques):
        """Apply computed torques to robot joints"""
        # In practice, this would send commands to joint controllers
        pass
    
    def walk_planning_loop(self):
        """Lower frequency walking pattern planning"""
        planning_frequency = 10  # 10 Hz planning
        planning_period = 1.0 / planning_frequency
        
        last_time = time.time()
        
        while self.running:
            current_time = time.time()
            dt = current_time - last_time
            
            if dt >= planning_period:
                # Plan walking pattern
                self.plan_next_step()
                
                last_time = current_time
            else:
                time.sleep(max(0, planning_period - dt))
    
    def plan_next_step(self):
        """Plan the next walking step"""
        # In practice, this would use MPC, pattern generators, etc.
        pass
    
    def perception_loop(self):
        """Perception processing at appropriate frequency"""
        perception_frequency = 30  # 30 Hz for perception
        perception_period = 1.0 / perception_frequency
        
        last_time = time.time()
        
        while self.running:
            current_time = time.time()
            dt = current_time - last_time
            
            if dt >= perception_period:
                # Process sensor data
                self.process_sensors()
                
                last_time = current_time
            else:
                time.sleep(max(0, perception_period - dt))
    
    def process_sensors(self):
        """Process sensor data for perception"""
        # In practice, this would process camera, LIDAR, etc.
        pass
    
    def start(self):
        """Start all control threads"""
        self.balance_thread.start()
        self.walk_thread.start()
        self.perception_thread.start()
    
    def stop(self):
        """Stop all control threads"""
        self.running = False
        self.balance_thread.join()
        self.walk_thread.join()
        self.perception_thread.join()


# Example usage
if __name__ == "__main__":
    controller = RealTimeBipedalController()
    controller.start()
    
    try:
        # Let it run for some time
        time.sleep(10)
    except KeyboardInterrupt:
        print("Stopping controller...")
    finally:
        controller.stop()
```

## Chapter Summary

This chapter covered advanced AI techniques for robotic manipulation and bipedal locomotion. We explored deep learning and reinforcement learning approaches for grasping and object manipulation, model predictive control and deep RL for bipedal walking, and techniques for integrating perception with action. These AI-powered approaches enable robots to perform complex tasks with greater adaptability and robustness compared to traditional model-based methods.

## Checklist

- [ ] Implement deep learning for robotic grasping
- [ ] Apply reinforcement learning to manipulation tasks
- [ ] Set up MPC for bipedal locomotion control
- [ ] Develop deep RL for walking gaits
- [ ] Integrate perception and action systems
- [ ] Validate AI-powered systems with appropriate metrics
- [ ] Optimize algorithms for real-time operation

## Exercises

### Exercise 1: Grasp Planning with Deep Learning

Create a deep learning system that predicts good grasp positions on objects.

#### Solution

1. Set up a dataset of object images with grasp annotations
2. Implement a CNN for grasp detection
3. Train the network on the dataset
4. Test on new objects in simulation
5. Integrate with robot control system

#### Hints

- Use RGB-D images for richer information
- Consider multiple grasps for each object
- Implement data augmentation for better generalization

### Exercise 2: Stable Walking with MPC

Implement an MPC-based controller for stable bipedal walking.

#### Solution

1. Model the robot as a linear inverted pendulum
2. Implement ZMP-based MPC controller
3. Tune controller parameters for stability
4. Test on simulated humanoid robot
5. Evaluate walking speed and stability

#### Hints

- Consider step timing as well as step placement
- Add constraints for foot placement within support polygon
- Test on various terrain conditions

## References

- [Deep Learning for Robotics by Wurm et al.](https://arxiv.org/abs/1804.00495)
- [Reinforcement Learning in Robotics: A Survey](https://arxiv.org/abs/1509.02650)
- [Model Predictive Control for Bipedal Locomotion](https://ieeexplore.ieee.org/document/7472884)
- [Robot Learning from Demonstration: A Survey](https://www.annualreviews.org/doi/10.1146/annurev-control-061520-015047)