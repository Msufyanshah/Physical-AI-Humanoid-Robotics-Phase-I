---
title: 'Chapter 11 - AI-Powered Manipulation & Bipedal Planning'
description: 'Using AI for robot manipulation and bipedal locomotion planning'
---

# Chapter 11: AI-Powered Manipulation & Bipedal Planning

## Learning Objectives

After reading this chapter, you will be able to:
- Implement AI-powered grasping and manipulation planning
- Design bipedal locomotion controllers using AI techniques
- Apply machine learning algorithms to improve robot behaviors
- Integrate perception and action planning for manipulation tasks
- Use reinforcement learning for locomotion optimization
- Implement cognitive planning for complex multi-step tasks
- Create adaptive controllers that learn from experience
- Validate AI controllers against safety requirements

## Introduction

AI-powered manipulation and bipedal planning represent the cutting edge of humanoid robotics, where machine learning algorithms enable robots to perform complex physical tasks with human-like dexterity and adaptability. This chapter explores how to leverage artificial intelligence for two critical humanoid robot capabilities: manipulation (grasping, moving, and interacting with objects) and locomotion (bipedal walking and balance).

## AI-Powered Manipulation

### Traditional vs. AI-Based Manipulation Approaches

Traditional manipulation approaches rely on:
- Precise geometric models and forward kinematics
- Hard-coded grasping strategies
- Rule-based grasp selection algorithms
- Deterministic execution paths

AI-powered manipulation approaches utilize:
- Learning from demonstration and experience
- Deep neural networks for grasp prediction
- Reinforcement learning for skill acquisition
- Adaptive behaviors that improve over time

### Deep Learning-Based Grasping

Modern grasp planning systems use deep learning to predict stable grasp configurations:

```python
import rclpy
from rclpy.node import Node
import torch
import torch.nn as nn
import numpy as np
from sensor_msgs.msg import Image, PointCloud2
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Float32MultiArray
from cv_bridge import CvBridge
from scipy.spatial.transform import Rotation as R
import message_filters


class GraspPredictionNetwork(nn.Module):
    """Deep neural network for predicting grasp quality and pose"""
    
    def __init__(self, input_channels=4):  # RGB + depth
        super(GraspPredictionNetwork, self).__init__()
        
        # Feature extraction from RGB-D input
        self.feature_extractor = nn.Sequential(
            # First convolution block
            nn.Conv2d(input_channels, 32, kernel_size=5, padding=2),
            nn.ReLU(),
            nn.MaxPool2d(2),
            
            # Second convolution block
            nn.Conv2d(32, 64, kernel_size=5, padding=2),
            nn.ReLU(),
            nn.MaxPool2d(2),
            
            # Third convolution block
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )
        
        # Calculate the dimension after convolutions
        # With 224x224 input and the above layers: 224/2/2/2 = 28x28 feature map
        # With 128 channels, fc_input_dim = 128 * 28 * 28
        self.fc_input_dim = 128 * 28 * 28  # This needs to be calculated based on actual input size
        
        # Fully connected layers for grasp prediction
        self.grasp_predictor = nn.Sequential(
            nn.Linear(self.fc_input_dim, 512),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Linear(256, 5)  # Output: [quality, x, y, angle, width]
        )
    
    def forward(self, x):
        features = self.feature_extractor(x)
        features = features.view(features.size(0), -1)  # Flatten
        grasp_predictions = self.grasp_predictor(features)
        
        # Sigmoid activation for quality (0-1) and tanh for other outputs
        grasp_qualities = torch.sigmoid(grasp_predictions[:, 0]).unsqueeze(1)
        grasp_params = torch.tanh(grasp_predictions[:, 1:])  # Other parameters
        
        return torch.cat([grasp_qualities, grasp_params], dim=1)


class AIGraspingNode(Node):
    """Node implementing AI-powered grasping"""
    
    def __init__(self):
        super().__init__('ai_grasping_node')
        
        self.bridge = CvBridge()
        
        # Initialize neural network
        self.grasp_model = GraspPredictionNetwork()
        
        # Load pretrained model weights (in practice)
        # self.grasp_model.load_state_dict(torch.load('grasp_model_weights.pth'))
        # self.grasp_model.eval()
        
        # Robot state
        self.robot_joints = {}
        self.object_poses = {}
        self.camera_pose = None
        
        # Subscribers
        self.rgb_sub = message_filters.Subscriber(self, Image, '/camera/rgb/image_raw')
        self.depth_sub = message_filters.Subscriber(self, Image, '/camera/depth/image_raw')
        
        # Use message filters to synchronize RGB and depth images
        self.sync = message_filters.ApproximateTimeSynchronizer(
            [self.rgb_sub, self.depth_sub], queue_size=10, slop=0.1
        )
        self.sync.registerCallback(self.camera_callback)
        
        # Publisher for grasp proposals
        self.grasp_proposals_pub = self.create_publisher(Float32MultiArray, '/grasp_proposals', 10)
        self.best_grasp_pub = self.create_publisher(PoseStamped, '/best_grasp_pose', 10)
        
        self.get_logger().info("AI Grasp Node initialized")
    
    def camera_callback(self, rgb_msg, depth_msg):
        """Process synchronized RGB and depth images"""
        
        try:
            # Convert ROS images to OpenCV
            rgb_image = self.bridge.imgmsg_to_cv2(rgb_msg, desired_encoding='bgr8')
            depth_image = self.bridge.imgmsg_to_cv2(depth_msg, desired_encoding='passthrough')
            
            # Process images for grasp prediction
            grasp_proposals = self.predict_grasps(rgb_image, depth_image)
            
            if grasp_proposals:
                # Find best grasp based on quality score
                best_grasp = max(grasp_proposals, key=lambda x: x['quality'])
                
                # Convert to world coordinates
                world_grasp_pose = self.image_to_world_pose(best_grasp, depth_image)
                
                if world_grasp_pose:
                    # Publish best grasp
                    grasp_pose_msg = PoseStamped()
                    grasp_pose_msg.header.stamp = rgb_msg.header.stamp
                    grasp_pose_msg.header.frame_id = 'map'
                    grasp_pose_msg.pose = world_grasp_pose
                    
                    self.best_grasp_pub.publish(grasp_pose_msg)
                    
                    # Log grasp info
                    self.get_logger().info(
                        f"Best grasp: Quality={best_grasp['quality']:.3f}, "
                        f"Position=({best_grasp['x']:.2f}, {best_grasp['y']:.2f}, {best_grasp['z']:.2f})"
                    )
            
        except Exception as e:
            self.get_logger().error(f"Error in camera callback: {e}")
    
    def predict_grasps(self, rgb_image, depth_image):
        """Predict grasp candidates using the AI model"""
        
        # Preprocess images
        processed_input = self.preprocess_images(rgb_image, depth_image)
        
        if processed_input is None:
            return []
        
        # Run inference
        with torch.no_grad():
            grasp_outputs = self.grasp_model(processed_input)
        
        # Convert neural network outputs to grasp proposals
        grasp_proposals = self.convert_to_grasp_proposals(grasp_outputs)
        
        return grasp_proposals
    
    def preprocess_images(self, rgb_image, depth_image):
        """Preprocess RGB and depth images for the neural network"""
        try:
            # Resize images
            target_size = (224, 224)
            resized_rgb = cv2.resize(rgb_image, target_size)
            resized_depth = cv2.resize(depth_image, target_size)
            
            # Normalize RGB
            rgb_normalized = resized_rgb.astype(np.float32) / 255.0
            
            # Normalize depth (assuming depth in meters with max of 5m)
            depth_normalized = resized_depth.astype(np.float32) / 5.0
            
            # Convert to tensor format (CHW)
            rgb_tensor = torch.tensor(rgb_normalized).permute(2, 0, 1).float()
            depth_tensor = torch.tensor(depth_normalized).unsqueeze(0).float()  # Add channel dimension
            
            # Stack RGB and depth
            input_tensor = torch.cat([rgb_tensor, depth_tensor], dim=0).unsqueeze(0)  # Add batch dimension
            
            return input_tensor
            
        except Exception as e:
            self.get_logger().error(f"Error preprocessing images: {e}")
            return None
    
    def convert_to_grasp_proposals(self, grasp_outputs):
        """Convert neural network outputs to grasp proposals"""
        grasp_proposals = []
        
        # In practice, this would decode the grasp predictions based on the network architecture
        # For this example, we'll return a placeholder implementation
        
        # Extract grasp proposals from the network output
        # Format: [quality, x, y, angle, width] for each proposal
        
        for i in range(grasp_outputs.shape[0]):  # For each batch item
            for j in range(grasp_outputs.shape[1] // 5):  # 5 parameters per grasp
                start_idx = j * 5
                end_idx = start_idx + 5
                grasp_data = grasp_outputs[i, start_idx:end_idx]
                
                grasp_proposal = {
                    'quality': float(grasp_data[0]),  # Quality (0-1)
                    'x': float(grasp_data[1]),       # X position (normalized)
                    'y': float(grasp_data[2]),       # Y position (normalized)
                    'angle': float(grasp_data[3]),   # Grasp angle (normalized to -1,1)
                    'width': float(grasp_data[4])    # Grasp width (normalized)
                }
                
                if grasp_proposal['quality'] > 0.5:  # Only return high-quality grasps
                    grasp_proposals.append(grasp_proposal)
        
        return grasp_proposals
    
    def image_to_world_pose(self, grasp, depth_image):
        """Convert image coordinates to world pose"""
        # This would require camera parameters and transformation matrices
        # For now, return a placeholder implementation
        
        if not self.camera_pose or depth_image is None:
            return None
        
        # Get 3D position from depth at grasp location
        u = int(grasp['x'] * depth_image.shape[1])  # Convert normalized to pixel coordinates
        v = int(grasp['y'] * depth_image.shape[0])
        
        if 0 <= u < depth_image.shape[1] and 0 <= v < depth_image.shape[0]:
            z = depth_image[v, u]  # Depth value at (u,v)
            
            if z > 0:  # Valid depth
                # Convert to 3D position using camera intrinsics
                # This would use actual camera parameters in practice
                x = (u - 320) * z / 554.0  # Placeholder camera parameters
                y = (v - 240) * z / 554.0
                
                # Create pose in camera frame
                pose_in_camera = np.array([x, y, z, 1.0])  # Homogeneous coordinates
                
                # Transform to world frame using camera pose
                # This would use actual transformation matrix
                world_pose = Pose()  # Placeholder
                world_pose.position.x = pose_in_camera[0]
                world_pose.position.y = pose_in_camera[1]
                world_pose.position.z = pose_in_camera[2]
                
                # Set orientation based on grasp angle
                angle = grasp['angle'] * np.pi  # Convert from normalized to radians
                world_pose.orientation = R.from_euler('z', angle).as_quat(canonical=True)
                
                return world_pose
        
        return None


def main(args=None):
    rclpy.init(args=args)
    node = AIGraspingNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("AI Grasping node shutting down...")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Bipedal Locomotion with AI

### Physics-Informed AI Controllers

For bipedal walking, physics-based models and AI controllers work together:

```python
# bipedal_controller.py
import rclpy
from rclpy.node import Node
import numpy as np
from geometry_msgs.msg import Twist, Vector3
from sensor_msgs.msg import JointState, Imu
from std_msgs.msg import Float32MultiArray
from builtin_interfaces.msg import Duration
from scipy.spatial.transform import Rotation as R
import math


class BipedalController(Node):
    """AI-powered bipedal locomotion controller"""
    
    def __init__(self):
        super().__init__('bipedal_controller')
        
        # Walking gait parameters
        self.declare_parameter('step_height', 0.05)  # meters
        self.declare_parameter('step_length', 0.3)   # meters
        self.declare_parameter('step_duration', 1.0)  # seconds
        self.declare_parameter('stance_width', 0.2)  # distance between feet (meters)
        self.declare_parameter('control_frequency', 50)  # Hz
        
        self.step_height = self.get_parameter('step_height').value
        self.step_length = self.get_parameter('step_length').value
        self.step_duration = self.get_parameter('step_duration').value
        self.stance_width = self.get_parameter('stance_width').value
        self.control_frequency = self.get_parameter('control_frequency').value
        
        # Robot state
        self.current_pose = None
        self.current_twist = None
        self.current_joints = {}
        self.imu_data = None
        self.desired_velocity = Twist()  # Commanded velocity
        self.gait_phase = 0.0  # Current phase of gait cycle (0 to 1)
        
        # Robot physical parameters
        self.leg_length = 0.8  # meters (approximate)
        self.com_height = 0.85  # meters (approximate center of mass)
        
        # ZMP (Zero Moment Point) controller
        self.zmp_controller = ZMPController(com_height=self.com_height)
        
        # PID controllers for each joint
        self.joint_pids = self.initialize_joint_pids()
        
        # Subscribers
        self.joint_state_sub = self.create_subscription(
            JointState, '/joint_states', self.joint_state_callback, 10
        )
        
        self.imu_sub = self.create_subscription(
            Imu, '/imu/data', self.imu_callback, 10
        )
        
        self.velocity_cmd_sub = self.create_subscription(
            Twist, '/cmd_vel', self.velocity_cmd_callback, 10
        )
        
        # Publishers
        self.joint_cmd_pub = self.create_publisher(JointState, '/joint_group_position_controller/commands', 10)
        self.com_trajectory_pub = self.create_publisher(Float32MultiArray, '/com_trajectory', 10)
        
        # Control timer
        self.control_timer = self.create_timer(1.0/self.control_frequency, self.control_loop)
        
        self.get_logger().info("Bipedal controller initialized")
    
    def joint_state_callback(self, msg):
        """Update joint state information"""
        for i, name in enumerate(msg.name):
            if i < len(msg.position):
                self.current_joints[name] = {
                    'position': msg.position[i],
                    'velocity': msg.velocity[i] if i < len(msg.velocity) else 0.0,
                    'effort': msg.effort[i] if i < len(msg.effort) else 0.0
                }
    
    def imu_callback(self, msg):
        """Update IMU information"""
        self.imu_data = msg
    
    def velocity_cmd_callback(self, msg):
        """Update desired velocity"""
        self.desired_velocity = msg
    
    def initialize_joint_pids(self):
        """Initialize PID controllers for each joint"""
        # Define PID parameters for different joint types
        pid_params = {
            'hip_yaw': {'p': 100.0, 'i': 1.0, 'd': 10.0},
            'hip_roll': {'p': 80.0, 'i': 0.5, 'd': 8.0},
            'hip_pitch': {'p': 120.0, 'i': 2.0, 'd': 12.0},
            'knee': {'p': 100.0, 'i': 1.0, 'd': 10.0},
            'ankle_pitch': {'p': 60.0, 'i': 0.5, 'd': 6.0},
            'ankle_roll': {'p': 50.0, 'i': 0.3, 'd': 5.0}
        }
        
        pids = {}
        for joint_name, params in pid_params.items():
            pids[joint_name] = {
                'p': params['p'],
                'i': params['i'], 
                'd': params['d'],
                'integral': 0.0,
                'previous_error': 0.0,
                'last_time': self.get_clock().now()
            }
        
        return pids
    
    def control_loop(self):
        """Main bipedal control loop"""
        current_time = self.get_clock().now()
        
        # Update gait phase based on walking command
        if self.desired_velocity.linear.x != 0 or self.desired_velocity.angular.z != 0:
            self.gait_phase = (self.gait_phase + 0.02) % 1.0  # Advance phase based on time
        else:
            # No walking command, hold stance position
            self.publish_stance_position()
            return
        
        # Calculate desired joint positions based on gait
        desired_joints = self.calculate_gait_joint_positions()
        
        # Calculate balance corrections based on IMU and ZMP
        if self.imu_data:
            balance_corrections = self.calculate_balance_control()
            desired_joints = self.apply_balance_corrections(desired_joints, balance_corrections)
        
        # Publish joint commands
        self.publish_joint_commands(desired_joints)
        
        # Publish CoM trajectory for visualization
        self.publish_com_trajectory()
    
    def calculate_gait_joint_positions(self):
        """Calculate joint positions for current gait phase"""
        # Calculate walking gait based on desired velocity and current phase
        desired_positions = {}
        
        # Basic walking pattern - in practice would be much more complex
        # with separate patterns for left and right legs
        
        # Calculate step parameters based on desired velocity
        linear_vel = self.desired_velocity.linear.x
        angular_vel = self.desired_velocity.angular.z
        
        # Convert linear/angular velocity to step parameters
        scaled_step_length = self.step_length if abs(linear_vel) > 0.01 else 0.0
        turn_compensation = angular_vel * 0.1  # Simple turn compensation
        
        # Calculate swing leg trajectory in gait
        phase = self.gait_phase
        
        # Swing leg trajectory - simplified elliptical path
        swing_x_offset = scaled_step_length/2 * math.sin(2 * math.pi * phase)
        swing_z_offset = self.step_height/2 * (1 - math.cos(2 * math.pi * phase))  # Lift leg at mid-swing
        
        # Stance leg - remains on ground during stance phase
        stance_x_offset = -scaled_step_length/2 * math.sin(2 * math.pi * phase)
        stance_z_offset = 0  # Keep on ground
        
        # Apply to specific joints (simplified model)
        # Left leg swing phase is offset from right leg
        left_leg_phase = (phase + 0.5) % 1.0  # Left leg lags right leg by half cycle
        
        # Hip joints (controls leg swing)
        desired_positions['left_hip_pitch'] = self.swing_leg_trajectory(
            left_leg_phase,  # Use phase for left leg
            scaled_step_length,
            self.step_height
        )
        
        desired_positions['right_hip_pitch'] = self.swing_leg_trajectory(
            phase,  # Use phase for right leg
            scaled_step_length,
            self.step_height
        )
        
        # Knee joints (controls leg flexing)
        desired_positions['left_knee'] = self.knee_trajectory(left_leg_phase)
        desired_positions['right_knee'] = self.knee_trajectory(phase) 
        
        # Ankle joints (controls balance and foot placement)
        desired_positions['left_ankle_pitch'] = self.balance_ankle_pitch(left_leg_phase)
        desired_positions['right_ankle_pitch'] = self.balance_ankle_pitch(phase)
        
        # Balance control through hip and ankle roll
        com_offset = self.get_desired_com_offset()
        desired_positions['left_hip_roll'] = com_offset * 0.5  # Distribute COM offset
        desired_positions['right_hip_roll'] = -com_offset * 0.5
        
        return desired_positions
    
    def swing_leg_trajectory(self, gait_phase, step_length, step_height):
        """Calculate the desired hip pitch for a swinging leg"""
        # Simplified trajectory generation
        # In practice, would use inverse kinematics for foot trajectory planning
        
        # Phase from 0 to 1 maps to complete step cycle
        # 0.0-0.5: Stance phase (leg on ground)
        # 0.5-1.0: Swing phase (leg moving forward)
        
        if 0.5 <= gait_phase <= 1.0:  # Swing phase
            # Generate a trajectory that lifts the leg and moves it forward
            swing_progress = (gait_phase - 0.5) * 2  # Map to 0-1 for swing phase
            
            # Sinusoidal trajectory for smooth motion
            x_offset = step_length/2 * math.sin(math.pi * swing_progress)
            z_offset = step_height/2 * (1 - math.cos(math.pi * swing_progress))
            
            # Convert to hip joint angle (simplified)
            return math.atan2(z_offset, x_offset)  # Simplified mapping
        else:  # Stance phase
            # Keep leg straight or slightly bent for stance
            return 0.0  # Simplified stance angle
    
    def knee_trajectory(self, gait_phase):
        """Calculate knee position based on gait phase"""
        # Simplified knee trajectory
        if 0.5 <= gait_phase <= 1.0:  # Swing phase: knee bends to lift foot
            swing_progress = (gait_phase - 0.5) * 2  # Map to 0-1 for swing phase
            
            # Bend knee during first half of swing, straighten during second half
            if swing_progress < 0.5:
                return 0.3 * math.sin(math.pi * swing_progress)  # Bend knee up to 0.3 radians
            else:
                return 0.3 * math.sin(math.pi * (1 - swing_progress))  # Straighten knee
        else:  # Stance phase: keep knee slightly bent for shock absorption
            return 0.1  # Slight knee bend for compliance
    
    def balance_ankle_pitch(self, gait_phase):
        """Calculate ankle pitch for balance based on gait phase"""
        # In real implementation, this would use sensor feedback
        # For this example, use simple gait-based value
        
        # During stance phase, adjust ankle for ground contact
        if 0.0 <= gait_phase < 0.5:
            # Stance phase - adjust for balance
            if self.imu_data:
                # Read orientation from IMU and adjust ankle accordingly
                roll = self.get_roll_from_imu(self.imu_data)
                return -roll * 0.8  # Simple balance correction
            else:
                return 0.0
        else:
            # Swing phase - keep ankle neutral
            return 0.0
    
    def get_roll_from_imu(self, imu_msg):
        """Extract roll angle from IMU quaternion"""
        # Convert quaternion to Euler angles
        rot = R.from_quat([
            imu_msg.orientation.x,
            imu_msg.orientation.y,
            imu_msg.orientation.z,
            imu_msg.orientation.w
        ])
        roll, pitch, yaw = rot.as_euler('xyz')
        return roll
    
    def get_desired_com_offset(self):
        """Get desired COM offset based on walking direction and balance needs"""
        # Calculate desired COM offset based on walking direction
        if self.desired_velocity.angular.z != 0:  # Turning
            # Shift COM toward inside of turn
            turn_direction = 1 if self.desired_velocity.angular.z > 0 else -1
            return turn_direction * 0.05  # 5cm offset for turns
        
        # For forward walking, keep COM centered
        return 0.0
    
    def calculate_balance_control(self):
        """Calculate balance control corrections using IMU and ZMP"""
        if not self.imu_data:
            return {}
        
        # Simple balance controller based on IMU orientation
        rotation = R.from_quat([
            self.imu_data.orientation.x,
            self.imu_data.orientation.y,
            self.imu_data.orientation.z,
            self.imu_data.orientation.w
        ])
        roll, pitch, yaw = rotation.as_euler('xyz')
        
        # Calculate balance corrections
        corrections = {
            'hip_roll': -roll * 1.0,  # Correct for roll orientation
            'ankle_pitch': -pitch * 0.5,  # Correct for pitch
            'ankle_roll': -roll * 0.3  # Additional ankle roll for finer balance
        }
        
        return corrections
    
    def apply_balance_corrections(self, desired_joints, corrections):
        """Apply balance corrections to desired joint positions"""
        corrected_joints = desired_joints.copy()
        
        for joint_name, correction in corrections.items():
            if joint_name in corrected_joints:
                corrected_joints[joint_name] += correction
            else:
                corrected_joints[joint_name] = correction
        
        return corrected_joints
    
    def publish_joint_commands(self, desired_positions):
        """Publish joint position commands to robot"""
        joint_cmd = JointState()
        joint_cmd.header.stamp = self.get_clock().now().to_msg()
        joint_cmd.header.frame_id = 'base_link'
        
        for joint_name, position in desired_positions.items():
            joint_cmd.name.append(joint_name)
            joint_cmd.position.append(position)
            joint_cmd.velocity.append(0.0)  # For position control, set velocity to 0
            joint_cmd.effort.append(0.0)   # For position control, effort is determined by controller
        
        self.joint_cmd_pub.publish(joint_cmd)
    
    def publish_stance_position(self):
        """Publish neutral stance position when not walking"""
        joint_cmd = JointState()
        joint_cmd.header.stamp = self.get_clock().now().to_msg()
        joint_cmd.header.frame_id = 'base_link'
        
        # Neutral standing position
        neutral_positions = {
            'left_hip_pitch': 0.0,
            'right_hip_pitch': 0.0,
            'left_knee': 0.0,
            'right_knee': 0.0,
            'left_ankle_pitch': 0.0,
            'right_ankle_pitch': 0.0,
            'left_hip_roll': 0.0,
            'right_hip_roll': 0.0
        }
        
        for joint_name, position in neutral_positions.items():
            joint_cmd.name.append(joint_name)
            joint_cmd.position.append(position)
            joint_cmd.velocity.append(0.0)
            joint_cmd.effort.append(0.0)
        
        self.joint_cmd_pub.publish(joint_cmd)
    
    def publish_com_trajectory(self):
        """Publish CoM trajectory for visualization"""
        # Calculate CoM position based on current gait
        com_msg = Float32MultiArray()
        com_msg.data = [
            float(self.current_pose.position.x) if self.current_pose else 0.0,
            float(self.current_pose.position.y) if self.current_pose else 0.0,
            float(self.com_height),  # Approximate CoM height
            float(self.gait_phase)   # Current gait phase
        ]
        self.com_trajectory_pub.publish(com_msg)


class ZMPController:
    """Zero Moment Point controller for bipedal balance"""
    
    def __init__(self, com_height=0.85):
        self.com_height = com_height
        self.gravity = 9.81
        
        # Compute the natural frequency of the inverted pendulum
        self.omega = math.sqrt(self.gravity / self.com_height)
        
        # ZMP tracking PID controller
        self.pid_params = {
            'p': 1000.0,  # Proportional gain
            'i': 10.0,    # Integral gain
            'd': 50.0     # Derivative gain
        }
        
        # PID state
        self.integral_error = 0.0
        self.previous_error = 0.0
        self.last_time = time.time()
    
    def compute_desired_zmp(self, com_position, com_velocity, target_com_position):
        """Compute desired ZMP based on CoM state"""
        # Inverted pendulum model: ZMP = CoM position - (CoM height / gravity) * CoM acceleration
        # Simplified for now - just return target position with small offset
        desired_zmp_x = target_com_position[0] - 0.05  # Small forward offset
        desired_zmp_y = target_com_position[1]  # Align with CoM in Y
        
        return np.array([desired_zmp_x, desired_zmp_y])
    
    def compute_balance_correction(self, current_zmp, desired_zmp, com_velocity):
        """Compute correction to maintain balance using ZMP"""
        # Calculate error
        error = desired_zmp - current_zmp
        
        # Time differential
        current_time = time.time()
        dt = current_time - self.last_time if self.last_time else 0.001
        self.last_time = current_time
        
        if dt <= 0:
            dt = 0.001  # Default to 1ms if timing issue
        
        # PID control
        self.integral_error += error * dt
        derivative_error = (error - self.previous_error) / dt if dt != 0 else 0
        
        # Apply PID formula
        correction = (self.pid_params['p'] * error + 
                     self.pid_params['i'] * self.integral_error + 
                     self.pid_params['d'] * derivative_error)
        
        self.previous_error = error
        
        return correction


def main(args=None):
    rclpy.init(args=args)
    node = BipedalController()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Bipedal controller shutting down...")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Reinforcement Learning for Locomotion

### Deep Reinforcement Learning for Walking

Using reinforcement learning to learn bipedal walking patterns:

```python
# rl_locomotion.py
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import random
from collections import deque
import gymnasium as gym


# Actor-Critic network for locomotion
class ActorCritic(nn.Module):
    def __init__(self, state_dim, action_dim, max_action):
        super(ActorCritic, self).__init__()

        # Shared layers
        self.shared_layers = nn.Sequential(
            nn.Linear(state_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 256),
            nn.ReLU()
        )

        # Actor network (policy)
        self.actor_mean = nn.Linear(256, action_dim)
        self.actor_std = nn.Linear(256, action_dim)

        # Critic network (value function)
        self.critic = nn.Linear(256, 1)

        self.max_action = max_action

    def forward(self, state):
        shared_features = self.shared_layers(state)

        # Actor: mean and std for Gaussian policy
        action_mean = torch.tanh(self.actor_mean(shared_features)) * self.max_action
        action_std = F.softplus(self.actor_std(shared_features)) + 1e-5  # Add small value to avoid zero std

        # Critic: state value
        value = self.critic(shared_features)

        return action_mean, action_std, value

    def get_action(self, state):
        """Sample action from the policy"""
        action_mean, action_std, _ = self.forward(state)
        dist = torch.distributions.Normal(action_mean, action_std)
        action = dist.sample()
        log_prob = dist.log_prob(action)
        return action, log_prob


class HindsightExperienceReplay:
    """Implementation of Hindsight Experience Replay for robotics tasks"""
    
    def __init__(self, buffer_size=1000000):
        self.buffer = deque(maxlen=buffer_size)
        self.goal_buffer = deque(maxlen=buffer_size)
    
    def store_experience(self, state, action, reward, next_state, done, goal):
        """Store experience with the original goal"""
        self.buffer.append((state, action, reward, next_state, done, goal))
    
    def sample_batch(self, batch_size, k_future=4):
        """Sample batch with HER (Hindsight Experience Replay)"""
        batch = random.sample(self.buffer, min(batch_size, len(self.buffer)))
        
        # Apply HER by replacing some goals with achieved goals
        her_batch = []
        for state, action, reward, next_state, done, original_goal in batch:
            her_batch.append((state, action, reward, next_state, done, original_goal))
            
            # With probability, replace goal with achieved goal (for HER)
            if random.random() < 0.8 and len(self.buffer) > 10:
                # Get a random achieved goal from the buffer
                random_exp = random.choice(self.buffer)
                random_next_state = random_exp[3]  # next_state from random experience
                her_batch.append((state, action, reward, next_state, done, random_next_state))
        
        return random.sample(her_batch, min(batch_size, len(her_batch)))


class RLWalkingAgent:
    """Reinforcement learning agent for humanoid walking"""
    
    def __init__(self, state_dim, action_dim, lr_actor=1e-4, lr_critic=1e-3):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        self.actor_critic = ActorCritic(state_dim, action_dim, max_action=1.0).to(self.device)
        self.optimizer_actor = optim.Adam(self.actor_critic.actor_mean.parameters(), lr=lr_actor)
        self.optimizer_critic = optim.Adam(self.actor_critic.critic.parameters(), lr=lr_critic)
        
        self.replay_buffer = HindsightExperienceReplay()
        self.gamma = 0.99  # Discount factor
        self.tau = 0.005   # Soft update parameter
        self.batch_size = 64
        
        self.training_steps = 0
        
    def get_action(self, state):
        """Get action from the policy"""
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        action, log_prob = self.actor_critic.get_action(state_tensor)
        return action.cpu().data.numpy().flatten()
    
    def update(self):
        """Update the policy using collected experiences"""
        if len(self.replay_buffer.buffer) < self.batch_size:
            return
        
        # Sample batch from replay buffer
        batch = self.replay_buffer.sample_batch(self.batch_size)
        state_batch, action_batch, reward_batch, next_state_batch, done_batch, goal_batch = zip(*batch)
        
        state_batch = torch.FloatTensor(state_batch).to(self.device)
        action_batch = torch.FloatTensor(action_batch).to(self.device)
        reward_batch = torch.FloatTensor(reward_batch).unsqueeze(1).to(self.device)
        next_state_batch = torch.FloatTensor(next_state_batch).to(self.device)
        done_batch = torch.BoolTensor(done_batch).unsqueeze(1).to(self.device)
        
        # Compute target values
        _, _, next_values = self.actor_critic(next_state_batch)
        target_values = reward_batch + (1 - done_batch.float()) * self.gamma * next_values
        
        # Current values
        _, _, current_values = self.actor_critic(state_batch)
        
        # Critic loss
        critic_loss = F.mse_loss(current_values, target_values.detach())
        
        # Actor loss
        actions, log_probs = self.actor_critic.get_action(state_batch)
        _, _, values = self.actor_critic(state_batch)
        
        advantage = target_values - values.detach()
        actor_loss = -(log_probs * advantage).mean()
        
        # Update networks
        self.optimizer_critic.zero_grad()
        critic_loss.backward()
        self.optimizer_critic.step()
        
        self.optimizer_actor.zero_grad()
        actor_loss.backward()
        self.optimizer_actor.step()
        
        self.training_steps += 1
    
    def train_on_env_data(self, env, episodes=1000):
        """Train the agent on environment data"""
        for episode in range(episodes):
            state, _ = env.reset()
            episode_reward = 0
            done = False
            
            while not done:
                action = self.get_action(state)
                next_state, reward, terminated, truncated, info = env.step(action)
                done = terminated or truncated
                
                # Store experience
                self.replay_buffer.store_experience(state, action, reward, next_state, done, info.get('goal', None))
                
                # Update agent
                self.update()
                
                state = next_state
                episode_reward += reward
            
            if episode % 100 == 0:
                print(f"Episode {episode}, Average Reward: {episode_reward}")


class HumanoidEnv(gym.Env):
    """Gym environment for humanoid robot locomotion"""
    
    def __init__(self):
        super().__init__()
        
        # Define action and observation spaces
        self.action_space = gym.spaces.Box(
            low=-1.0, high=1.0, shape=(18,), dtype=np.float32  # 18 joints for both legs and hips
        )
        
        self.observation_space = gym.spaces.Box(
            low=-np.inf, high=np.inf, shape=(37,), dtype=np.float32  # 37-dim state: pos(3) + rot(4) + vel(6) + joint_pos(12) + joint_vel(12)
        )
        
        # Robot physical parameters
        self.max_episode_steps = 1000
        self.step_count = 0
        self.com_height_threshold = 0.3  # Robot has fallen if CoM height drops below this
        
        # Initialize robot state
        self.reset()
    
    def reset(self, seed=None, options=None):
        """Reset the environment to initial state"""
        super().reset(seed=seed)
        
        # Initialize robot in standing position
        self.robot_state = {
            'position': np.array([0.0, 0.0, 0.85]),  # Standing at origin with CoM at 0.85m
            'rotation': np.array([0.0, 0.0, 0.0, 1.0]),  # No rotation
            'linear_velocity': np.array([0.0, 0.0, 0.0]),
            'angular_velocity': np.array([0.0, 0.0, 0.0]),
            'joint_positions': np.zeros(12),  # 12 joints: 6 per leg
            'joint_velocities': np.zeros(12)
        }
        
        self.step_count = 0
        
        return self.get_observation(), {}
    
    def get_observation(self):
        """Get the current observation from robot state"""
        # Flatten the robot state into a single vector
        obs = np.concatenate([
            self.robot_state['position'],
            self.robot_state['rotation'],
            self.robot_state['linear_velocity'],
            self.robot_state['angular_velocity'],
            self.robot_state['joint_positions'],
            self.robot_state['joint_velocities']
        ])
        
        return obs
    
    def step(self, action):
        """Execute action and return new state"""
        # Apply action to robot simulation
        self.apply_action_to_robot(action)
        
        # Update physics simulation
        self.update_physics()
        
        # Calculate reward
        reward = self.calculate_reward()
        
        # Check termination conditions
        terminated = self.check_termination()
        truncated = self.step_count >= self.max_episode_steps
        
        self.step_count += 1
        
        return self.get_observation(), reward, terminated, truncated, {}
    
    def apply_action_to_robot(self, action):
        """Apply action to robot simulation (simplified)"""
        # In a real implementation, this would interface with the robot simulator
        # For this example, we'll update the joint positions based on the action
        # and update the overall robot state based on simplified physics
        
        # Update joint positions (clipped to reasonable values)
        self.robot_state['joint_positions'] = np.clip(
            self.robot_state['joint_positions'] + action[:12] * 0.1,  # Scale down the action
            -np.pi, np.pi  # Clip to reasonable joint ranges
        )
        
        # Simplified physics: apply forward motion based on leg configuration
        forward_speed = 0.1 * (action[0] + action[1])  # Based on hip actions
        self.robot_state['position'][0] += forward_speed / self.control_frequency  # Increment x position
        
        # Add some variation based on joint configuration to simulate balance effects
        balance_effect = np.sum(np.abs(self.robot_state['joint_positions'])) * 0.001
        self.robot_state['position'][2] -= balance_effect  # Slight CoM height change based on joint positions
    
    def update_physics(self):
        """Update physics simulation (simplified)"""
        # Simplified physics updates
        # In a real implementation, this would run the full physics simulation
        pass
    
    def calculate_reward(self):
        """Calculate reward based on robot state"""
        # Reward components:
        # 1. Forward progress
        # 2. Maintaining balance (CoM height)
        # 3. Energy efficiency (minimize joint efforts)
        # 4. Safety (avoid joint limits)
        
        # Forward progress reward: encourage movement in x direction
        forward_reward = self.robot_state['position'][0] * 10  # 10 points per meter forward
        
        # Balance reward: maintain upright posture
        com_height = self.robot_state['position'][2]
        balance_reward = max(0, com_height - 0.75) * 50  # Encourage keeping CoM above 0.75m
        
        # Energy penalty: discourage excessive joint movement
        energy_penalty = -np.sum(np.abs(self.robot_state['joint_velocities'])) * 0.1
        
        # Joint limit penalty: discourage approaching joint limits
        joint_limit_penalty = -np.sum(
            np.maximum(0, np.abs(self.robot_state['joint_positions']) - (np.pi * 0.9))
        ) * 10  # Heavy penalty when approaching 90% of joint limits
        
        total_reward = forward_reward + balance_reward + energy_penalty + joint_limit_penalty
        return total_reward
    
    def check_termination(self):
        """Check if episode should terminate"""
        # Terminate if robot falls (CoM too low)
        com_height = self.robot_state['position'][2]
        if com_height < self.com_height_threshold:
            return True
        
        # Terminate if robot moves too far in wrong direction
        if self.robot_state['position'][0] < -1.0:  # Moved backwards too much
            return True
        
        return False


def train_bipedal_rl_agent():
    """Train the bipedal walking RL agent"""
    
    # Create environment
    env = HumanoidEnv()
    
    # Create agent
    agent = RLWalkingAgent(
        state_dim=env.observation_space.shape[0],
        action_dim=env.action_space.shape[0]
    )
    
    # Train the agent
    agent.train_on_env_data(env, episodes=5000)
    
    return agent


def main():
    # Train or load a pre-trained agent
    print("Starting RL training for bipedal locomotion...")
    agent = train_bipedal_rl_agent()
    
    print("Training complete! Agent ready for deployment.")
    
    return agent


if __name__ == '__main__':
    trained_agent = main()
```

## Perception-Action Integration

### Integrating Perception with Action Planning

Now, let's connect perception and action through the cognitive planning layer:

```python
# perception_action_integration.py
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, LaserScan, Imu, JointState
from geometry_msgs.msg import PoseStamped, Twist
from std_msgs.msg import String
from cv_bridge import CvBridge
import numpy as np
from typing import List, Dict, Any, Optional
import json


class PerceptionActionIntegrator(Node):
    """Integrates perception and action planning for humanoid robot autonomy"""
    
    def __init__(self):
        super().__init__('perception_action_integrator')
        
        self.bridge = CvBridge()
        
        # Perception data storage
        self.current_image = None
        self.current_lidar = None
        self.current_imu = None
        self.current_joints = {}
        self.current_pose = None
        
        # Action planning state
        self.active_goals = []
        self.current_plan = None
        
        # Subscribers
        self.image_sub = self.create_subscription(
            Image, '/camera/rgb/image_raw', self.image_callback, 10
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
        
        self.pose_sub = self.create_subscription(
            PoseStamped, '/amcl_pose', self.pose_callback, 10
        )
        
        self.high_level_command_sub = self.create_subscription(
            String, '/high_level_command', self.command_callback, 10
        )
        
        # Publishers
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.action_status_pub = self.create_publisher(String, '/action_status', 10)
        self.perception_report_pub = self.create_publisher(String, '/perception_report', 10)
        
        # Timer for integration loop
        self.integration_timer = self.create_timer(0.1, self.integration_loop)  # 10 Hz
        
        self.get_logger().info("Perception-Action Integrator initialized")
    
    def image_callback(self, msg):
        """Process image data"""
        try:
            self.current_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        except Exception as e:
            self.get_logger().error(f"Error converting image: {e}")
    
    def lidar_callback(self, msg):
        """Process LiDAR data"""
        self.current_lidar = msg
    
    def imu_callback(self, msg):
        """Process IMU data"""
        self.current_imu = msg
    
    def joint_state_callback(self, msg):
        """Process joint state data"""
        for i, name in enumerate(msg.name):
            if i < len(msg.position):
                self.current_joints[name] = {
                    'position': msg.position[i],
                    'velocity': msg.velocity[i] if i < len(msg.velocity) else 0.0,
                    'effort': msg.effort[i] if i < len(msg.effort) else 0.0
                }
    
    def pose_callback(self, msg):
        """Process robot pose data"""
        self.current_pose = msg.pose
    
    def command_callback(self, msg):
        """Process high-level commands"""
        try:
            command_data = json.loads(msg.data)
            self.process_high_level_command(command_data)
        except json.JSONDecodeError:
            self.get_logger().warn(f"Invalid JSON in command: {msg.data}")
    
    def process_high_level_command(self, command_data: Dict[str, Any]):
        """Process high-level command using perception data"""
        command_type = command_data.get('type')
        command_params = command_data.get('parameters', {})
        
        if command_type == 'navigate_to_object':
            self.handle_navigate_to_object_command(command_params)
        elif command_type == 'grasp_object':
            self.handle_grasp_object_command(command_params)
        elif command_type == 'inspect_area':
            self.handle_inspect_area_command(command_params)
        else:
            self.get_logger().warn(f"Unknown command type: {command_type}")
    
    def handle_navigate_to_object_command(self, params: Dict[str, Any]):
        """Handle navigate to object command"""
        object_type = params.get('object_type', 'unknown')
        
        self.get_logger().info(f"Requested to navigate to {object_type}")
        
        # Use perception to locate object
        object_pose = self.locate_object_in_environment(object_type)
        
        if object_pose:
            # Plan navigation to object
            nav_plan = self.plan_navigation_to_pose(object_pose)
            
            if nav_plan:
                # Execute plan
                self.execute_navigation_plan(nav_plan)
                
                status_msg = String()
                status_msg.data = json.dumps({
                    'status': 'executing',
                    'action': 'navigation',
                    'target': object_type,
                    'target_pose': object_pose
                })
                
                self.action_status_pub.publish(status_msg)
            else:
                self.get_logger().warn(f"Could not plan navigation to {object_type}")
        else:
            self.get_logger().warn(f"Could not locate {object_type} in environment")
            
            # Could initiate environment search
            self.initiate_object_search(object_type)
    
    def locate_object_in_environment(self, object_type: str) -> Optional[Dict[str, Any]]:
        """Locate an object in the environment using perception"""
        # This would use computer vision to detect objects
        # For now, return a placeholder
        
        # In real implementation, this would:
        # 1. Process current imagery to detect objects
        # 2. Use depth information to get 3D positions
        # 3. Match detected objects to requested type
        
        # For this example, return a fixed position if we're simulating
        if self.current_pose and object_type == 'cup':
            # If object exists in world model (from perception), return its pose
            # This is a simplified example
            return {
                'x': self.current_pose.position.x + 1.0,  # 1m ahead of current pose
                'y': self.current_pose.position.y + 0.5,  # 0.5m to the right
                'z': 0.8  # Height of table
            }
        
        return None
    
    def plan_navigation_to_pose(self, target_pose: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """Plan a path to the target pose"""
        # In practice, this would use a path planning algorithm (A*, RRT, etc.)
        # For this example, return a simple straight-line path
        
        if not self.current_pose:
            return None
        
        # Simple path planning - in practice would be much more complex
        current_pos = self.current_pose.position
        target_pos = [target_pose['x'], target_pose['y'], target_pose['z']]
        
        dx = target_pos[0] - current_pos.x
        dy = target_pos[1] - current_pos.y
        distance = np.sqrt(dx*dx + dy*dy)
        
        # Create path points every 0.5 meters
        path = []
        steps = int(distance / 0.5)
        for i in range(steps + 1):
            t = i / steps if steps > 0 else 0
            point = {
                'x': current_pos.x + t * dx,
                'y': current_pos.y + t * dy,
                'z': current_pos.z  # Maintain same height
            }
            path.append(point)
        
        # Add final point to target
        if steps > 0 or distance > 0.1:  # If distance is significant
            path.append(target_pos)
        
        return path
    
    def execute_navigation_plan(self, plan: List[Dict[str, Any]]):
        """Execute navigation plan"""
        self.get_logger().info(f"Executing navigation plan with {len(plan)} waypoints")
        
        for i, waypoint in enumerate(plan):
            self.get_logger().info(f"Moving to waypoint {i+1}/{len(plan)}: ({waypoint['x']:.2f}, {waypoint['y']:.2f})")
            
            # Move to waypoint
            success = self.move_to_waypoint(waypoint)
            
            if not success:
                self.get_logger().error(f"Failed to reach waypoint {i+1}")
                break
    
    def move_to_waypoint(self, waypoint: Dict[str, Any]) -> bool:
        """Move robot to specified waypoint"""
        # Calculate direction to target
        if not self.current_pose:
            return False
        
        current_pos = self.current_pose.position
        dx = waypoint['x'] - current_pos.x
        dy = waypoint['y'] - current_pos.y
        
        # Calculate distance to target
        target_distance = np.sqrt(dx*dx + dy*dy)
        
        # Create velocity command to move toward target
        cmd = Twist()
        cmd.linear.x = min(0.3, target_distance)  # Scale speed with distance, max 0.3 m/s
        cmd.angular.z = np.arctan2(dy, dx) - self.get_current_yaw()  # Rotate toward target
        
        # Normalize angular velocity
        if cmd.angular.z > np.pi:
            cmd.angular.z -= 2*np.pi
        elif cmd.angular.z < -np.pi:
            cmd.angular.z += 2*np.pi
        
        # Limit angular velocity
        cmd.angular.z = max(-0.5, min(0.5, cmd.angular.z))
        
        # Publish command
        self.cmd_vel_pub.publish(cmd)
        
        # Wait for some time or until close to target (simplified)
        # In real implementation, would use proper trajectory tracking
        import time
        time.sleep(0.2)  # Simulate time to reach position
        
        return target_distance < 0.2  # Return success if within 20cm
    
    def get_current_yaw(self) -> float:
        """Get current yaw angle from robot orientation"""
        if not self.current_pose or not self.current_pose.orientation:
            return 0.0
        
        # Convert quaternion to yaw angle
        q = self.current_pose.orientation
        siny_cosp = 2 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
        yaw = np.arctan2(siny_cosp, cosy_cosp)
        
        return yaw
    
    def handle_grasp_object_command(self, params: Dict[str, Any]):
        """Handle object grasping command"""
        object_id = params.get('object_id')
        
        self.get_logger().info(f"Requested to grasp object: {object_id}")
        
        # Locate object using perception
        object_pose = self.locate_object_in_environment(object_id)
        
        if not object_pose:
            self.get_logger().warn(f"Could not locate object {object_id}")
            return
        
        # Navigate close to object (grasping distance ~0.5m)
        grasp_approach_pose = {
            'x': object_pose['x'] - 0.5,  # 0.5m away from object in x direction
            'y': object_pose['y'],
            'z': object_pose['z']
        }
        
        # Plan and execute approach
        approach_plan = self.plan_navigation_to_pose(grasp_approach_pose)
        if approach_plan:
            self.execute_navigation_plan(approach_plan)
        
        # Perform grasping action - would require more complex control in practice
        self.execute_grasp_action(object_pose)
    
    def execute_grasp_action(self, object_pose: Dict[str, Any]):
        """Execute grasping action"""
        # In a real system, this would:
        # 1. Plan grasp trajectory using arm IK
        # 2. Move arm to grasp position
        # 3. Close gripper
        # 4. Verify grasp success
        
        self.get_logger().info(f"Attempting to grasp object at {object_pose}")
        
        # Publish a status indicating grasp in progress
        status_msg = String()
        status_msg.data = json.dumps({
            'status': 'executing',
            'action': 'grasping',
            'target_pose': object_pose
        })
        self.action_status_pub.publish(status_msg)
    
    def initiate_object_search(self, object_type: str):
        """Initiate environment search for an object"""
        self.get_logger().info(f"Initiating search for {object_type}")
        
        # Plan search behavior (turn in place, move to different viewpoints)
        search_pattern = [
            {'action': 'rotate', 'angle': 90, 'duration': 2.0},
            {'action': 'move', 'direction': 'forward', 'distance': 1.0, 'duration': 3.0},
            {'action': 'rotate', 'angle': -90, 'duration': 2.0},
            {'action': 'move', 'direction': 'forward', 'distance': 1.0, 'duration': 3.0},
            {'action': 'rotate', 'angle': 180, 'duration': 2.0}
        ]
        
        for step in search_pattern:
            self.execute_search_step(step)
            
            # Check if object is found after each step
            object_pose = self.locate_object_in_environment(object_type)
            if object_pose:
                self.get_logger().info(f"Found {object_type} at position {object_pose}")
                
                # Report finding to higher level
                report_msg = String()
                report_msg.data = json.dumps({
                    'event': 'object_found',
                    'object_type': object_type,
                    'position': object_pose
                })
                self.perception_report_pub.publish(report_msg)
                return  # Object found, stop searching
        
        # Object not found after search
        self.get_logger().warn(f"Could not find {object_type} after searching")
        report_msg = String()
        report_msg.data = json.dumps({
            'event': 'object_not_found',
            'object_type': object_type,
            'search_completed': True
        })
        self.perception_report_pub.publish(report_msg)
    
    def execute_search_step(self, step: Dict[str, Any]):
        """Execute a single search pattern step"""
        if step['action'] == 'rotate':
            cmd = Twist()
            cmd.linear.x = 0.0
            cmd.angular.z = np.deg2rad(step['angle']) / step['duration']  # Convert to angular velocity
            
            # Publish rotation command for specified duration
            start_time = time.time()
            while time.time() - start_time < step['duration']:
                self.cmd_vel_pub.publish(cmd)
                time.sleep(0.05)  # 20Hz control
            
            # Stop rotation
            stop_cmd = Twist()
            self.cmd_vel_pub.publish(stop_cmd)
        
        elif step['action'] == 'move':
            cmd = Twist()
            if step['direction'] == 'forward':
                cmd.linear.x = step['distance'] / step['duration']  # Convert to linear velocity
            elif step['direction'] == 'backward':
                cmd.linear.x = -step['distance'] / step['duration']
            
            # Publish movement command for specified duration
            start_time = time.time()
            while time.time() - start_time < step['duration']:
                self.cmd_vel_pub.publish(cmd)
                time.sleep(0.05)  # 20Hz control
            
            # Stop movement
            stop_cmd = Twist()
            self.cmd_vel_pub.publish(stop_cmd)
    
    def integration_loop(self):
        """Main integration loop - coordinate perception and action"""
        # Process sensor data for current state
        if self.current_imu:
            self.check_balance_state()
        
        if self.current_lidar:
            self.update_obstacle_map()
        
        # Monitor active goals
        self.monitor_active_goals()
    
    def check_balance_state(self):
        """Monitor robot balance using IMU data"""
        if not self.current_imu:
            return
        
        # Check orientation from IMU for balance
        q = self.current_imu.orientation
        rot = R.from_quat([q.x, q.y, q.z, q.w])
        roll, pitch, _ = rot.as_euler('xyz')
        
        # If orientation deviates too much from upright, trigger balance response
        max_tilt = np.radians(15)  # 15 degrees max tilt
        if abs(roll) > max_tilt or abs(pitch) > max_tilt:
            self.get_logger().warn(f"Dangerous tilt detected: roll={np.degrees(roll):.1f}°, pitch={np.degrees(pitch):.1f}°")
            # In real system, trigger balance recovery
            self.trigger_balance_recovery()
    
    def trigger_balance_recovery(self):
        """Trigger balance recovery behavior"""
        status_msg = String()
        status_msg.data = json.dumps({
            'status': 'critical',
            'action': 'balance_recovery',
            'reason': 'dangerous_tilt_detected'
        })
        self.action_status_pub.publish(status_msg)
    
    def update_obstacle_map(self):
        """Update obstacle map based on LiDAR data"""
        # Process LiDAR data to identify obstacles
        # In practice, this would build a more sophisticated map
        pass
    
    def monitor_active_goals(self):
        """Monitor progress of active goals"""
        # In practice, monitor if active goals are progressing
        # Handle timeouts and failures
        pass


def main(args=None):
    rclpy.init(args=args)
    node = PerceptionActionIntegrator()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Perception-Action Integrator shutting down...")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Complete System Launch and Validation

### Main Launch File

```python
# launch/humanoid_complete_system.py
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, RegisterEventHandler, TimerAction
from launch.event_handlers import OnProcessExit
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    # Declare launch arguments
    declare_use_sim_time = DeclareLaunchArgument(
        name='use_sim_time',
        default_value='True',
        description='Use simulation time if true'
    )
    
    declare_robot_model = DeclareLaunchArgument(
        name='robot_model',
        default_value='humanoid_robot',
        description='Robot model name'
    )
    
    declare_world_file = DeclareLaunchArgument(
        name='world_file',
        default_value='default.sdf',
        description='World file for Gazebo simulation'
    )
    
    # Get launch configurations
    use_sim_time = LaunchConfiguration('use_sim_time')
    robot_model = LaunchConfiguration('robot_model')
    world_file = LaunchConfiguration('world_file')
    
    # Perception node
    perception_node = Node(
        package='my_humanoid_perception',
        executable='perception_node',
        name='perception_node',
        parameters=[{
            'use_sim_time': use_sim_time
        }],
        output='screen'
    )
    
    # Cognitive planning node
    cognitive_planning_node = Node(
        package='my_humanoid_planning',
        executable='cognitive_planning_node',
        name='cognitive_planning',
        parameters=[{
            'use_sim_time': use_sim_time
        }],
        output='screen'
    )
    
    # Motion control node
    motion_control_node = Node(
        package='my_humanoid_control',
        executable='motion_controller',
        name='motion_controller',
        parameters=[{
            'use_sim_time': use_sim_time,
            'step_height': 0.05,
            'step_length': 0.3,
            'control_frequency': 50
        }],
        output='screen'
    )
    
    # AI grasping node
    ai_grasping_node = Node(
        package='my_humanoid_manipulation',
        executable='ai_grasping_node',
        name='ai_grasping',
        parameters=[{
            'use_sim_time': use_sim_time
        }],
        output='screen'
    )
    
    # Perception-action integrator node
    perception_action_node = Node(
        package='my_humanoid_perception_action',
        executable='perception_action_integrator',
        name='perception_action_integrator',
        parameters=[{
            'use_sim_time': use_sim_time
        }],
        output='screen'
    )
    
    # Voice interface node (if needed)
    voice_interface_node = Node(
        package='my_voice_interface',
        executable='voice_interface_node',
        name='voice_interface',
        parameters=[{
            'use_sim_time': use_sim_time
        }],
        output='screen'
    )
    
    # Define launch order with delays to ensure proper initialization
    delayed_nodes = []
    
    # First, start motion control (needed for other nodes)
    delayed_nodes.append(TimerAction(
        period=2.0,  # Start after 2 seconds
        actions=[motion_control_node]
    ))
    
    # Then perception and planning
    delayed_nodes.append(TimerAction(
        period=3.0,
        actions=[perception_node, cognitive_planning_node]
    ))
    
    # Then AI components
    delayed_nodes.append(TimerAction(
        period=4.0,
        actions=[ai_grasping_node, perception_action_node]
    ))
    
    # Finally, UI components
    delayed_nodes.append(TimerAction(
        period=5.0,
        actions=[voice_interface_node]
    ))
    
    return LaunchDescription([
        declare_use_sim_time,
        declare_robot_model,
        declare_world_file,
        
        # Start some nodes immediately
        # Others with delays to ensure proper initialization
    ] + delayed_nodes)
```

### Validation and Testing Scripts

```python
# validation_and_testing.py
import unittest
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Pose, Twist
import time
import threading


class HumanoidSystemValidator(unittest.TestCase):
    """Validation tests for the complete humanoid system"""
    
    def setUp(self):
        """Setup test environment"""
        rclpy.init()
        self.validator_node = ValidatorNode()
        self.executor = rclpy.executors.SingleThreadedExecutor()
        self.executor.add_node(self.validator_node)
        
        # Start executor in a thread
        self.executor_thread = threading.Thread(target=self.executor.spin, daemon=True)
        self.executor_thread.start()
        
    def tearDown(self):
        """Clean up test environment"""
        self.executor.shutdown()
        self.validator_node.destroy_node()
        rclpy.shutdown()
    
    def test_perception_accuracy(self):
        """Test perception system accuracy"""
        # This would test that perception correctly identifies objects
        # For now, this is a placeholder
        
        # Publish test sensor data
        # Verify perception output matches expected
        self.assertTrue(True, "Placeholder for perception accuracy test")
    
    def test_navigation_accuracy(self):
        """Test navigation system accuracy"""
        # Test that robot navigates to specified locations
        # For now, placeholder
        self.assertTrue(True, "Placeholder for navigation accuracy test")
    
    def test_grasping_success_rate(self):
        """Test grasping success rate"""
        # Test that robot successfully grasps objects
        # For now, placeholder
        self.assertTrue(True, "Placeholder for grasping success test")
    
    def test_balance_stability(self):
        """Test balance stability during locomotion"""
        # Test that robot maintains balance during walking
        # For now, placeholder
        self.assertTrue(True, "Placeholder for balance stability test")
    
    def test_system_integration(self):
        """Test overall system integration"""
        # Test that all components work together
        # For now, placeholder
        self.assertTrue(True, "Placeholder for system integration test")


class ValidatorNode(Node):
    """Node for validating the humanoid system"""
    
    def __init__(self):
        super().__init__('system_validator')
        
        # Publishers and subscribers for validation
        self.status_sub = self.create_subscription(
            String, '/system_status', self.status_callback, 10
        )
        
        self.action_status_sub = self.create_subscription(
            String, '/action_status', self.action_status_callback, 10
        )
        
        # Internal validation tracking
        self.recent_status = ""
        self.action_success_count = 0
        self.action_failure_count = 0
        self.system_errors = []
        
        self.get_logger().info("System validator initialized")
    
    def status_callback(self, msg):
        """Track system status"""
        try:
            status_data = json.loads(msg.data)
            self.recent_status = status_data.get('status', 'unknown')
        except json.JSONDecodeError:
            self.get_logger().warn(f"Invalid status message: {msg.data}")
    
    def action_status_callback(self, msg):
        """Track action status"""
        try:
            action_data = json.loads(msg.data)
            status = action_data.get('status', '')
            
            if status == 'completed':
                self.action_success_count += 1
            elif status in ['failed', 'error']:
                self.action_failure_count += 1
            elif status == 'critical':
                self.system_errors.append(action_data.get('reason', 'unknown'))
        except json.JSONDecodeError:
            self.get_logger().warn(f"Invalid action status message: {msg.data}")
    
    def get_validation_metrics(self) -> Dict[str, Any]:
        """Get current validation metrics"""
        total_actions = self.action_success_count + self.action_failure_count
        success_rate = (self.action_success_count / total_actions) if total_actions > 0 else 0
        
        metrics = {
            'status': self.recent_status,
            'action_success_rate': success_rate,
            'total_actions': total_actions,
            'success_count': self.action_success_count,
            'failure_count': self.action_failure_count,
            'system_errors': len(self.system_errors),
            'recent_errors': self.system_errors[-5:] if self.system_errors else []
        }
        
        return metrics


def run_validation_suite():
    """Run the complete validation suite"""
    print("Running humanoid robot system validation suite...")
    
    # Run unit tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(HumanoidSystemValidator)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Additionally run system-specific validation
    validation_metrics = run_system_validation()
    
    print("\nValidation Results Summary:")
    print(f"  Tests run: {result.testsRun}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Success rate: {validation_metrics['action_success_rate']:.2f}")
    
    return result


def run_system_validation():
    """Run system-level validation"""
    rclpy.init()
    
    validator_node = ValidatorNode()
    executor = rclpy.executors.SingleThreadedExecutor()
    executor.add_node(validator_node)
    
    # Run for 30 seconds to collect metrics
    start_time = time.time()
    while time.time() - start_time < 30:
        executor.spin_once(timeout_sec=1.0)
    
    metrics = validator_node.get_validation_metrics()
    
    validator_node.destroy_node()
    rclpy.shutdown()
    
    return metrics


if __name__ == '__main__':
    validation_result = run_validation_suite()
    print("\nValidation complete!")