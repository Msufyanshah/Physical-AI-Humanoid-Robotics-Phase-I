---
title: 'Exercise Set 3 - The AI-Robot Brain (NVIDIA Isaac)'
description: 'Hands-on exercises for Module 3 on Isaac Sim, perception, and AI planning'
---

# Exercise Set 3: The AI-Robot Brain (NVIDIA Isaac)

## Learning Objectives

After completing these exercises, you will be able to:
- Configure and run NVIDIA Isaac Sim for complex robotics scenarios
- Implement perception systems combining vision and robotics
- Apply AI techniques for robot manipulation and locomotion planning
- Integrate sensing, planning, and control in a complete robotic system
- Evaluate and validate AI-powered robotic behaviors
- Optimize simulation and real-time performance

## Exercise 1: Isaac Sim Scene Creation with Perception Sensors

Create an Isaac Sim scene with realistic lighting, textures, and a robot equipped with RGB and depth cameras, then generate synthetic data.

### Instructions

1. Create a new Isaac Sim scene containing:
   - A humanoid robot (use existing model or create simple one)
   - Furniture and objects for manipulation
   - Dynamic lighting conditions

2. Add perception sensors to the robot:
   - RGB camera with 640x480 resolution
   - Depth camera with appropriate parameters
   - IMU sensor

3. Implement a data capture pipeline that:
   - Captures synchronized RGB and depth images
   - Records pose information for each frame
   - Saves data in standard formats

4. Add scene randomization to increase data diversity

### Solution

First, create the scene setup script (scene_setup.py):

```python
import omni
from omni.isaac.core import World
from omni.isaac.core.utils.stage import add_reference_to_stage
from omni.isaac.core.utils.nucleus import get_assets_root_path
from omni.isaac.core.utils.prims import get_prim_at_path, create_primitive
from omni.isaac.core.utils.rotations import euler_angles_to_quat
from omni.isaac.sensor import Camera
import carb
import numpy as np
import cv2
import os


class IsaacSimScene:
    def __init__(self):
        self.world = World(stage_units_in_meters=1.0)
        self.camera = None
        self.depth_camera = None
        
        # Get assets root
        self.assets_root = get_assets_root_path()
        if self.assets_root is None:
            carb.log_error("Could not find Isaac Sim assets path")
            return
            
    def create_environment(self):
        """Create a indoor environment with furniture"""
        # Create ground plane
        create_primitive(
            prim_path="/World/ground",
            primitive_props={"size": 10.0},
            prim_type="Plane",
            position=np.array([0, 0, 0]),
            orientation=euler_angles_to_quat(np.array([0, 0, 0]))
        )
        
        # Load a simple robot onto the scene
        robot_asset_path = self.assets_root + "/Isaac/Robots/Turtlebot/turtlebot3_standalone.usd"
        add_reference_to_stage(usd_path=robot_asset_path, prim_path="/World/Robot")
        
        # Create a table
        create_primitive(
            prim_path="/World/table",
            primitive_props={"size": 0.8},
            prim_type="Cube",
            position=np.array([1.0, 0, 0.4]),
            orientation=euler_angles_to_quat(np.array([0, 0, 0]))
        )
        
        # Add objects on the table
        for i in range(3):
            color = [(i+1)%3, (i+2)%3, (i+3)%3]  # Different colors
            create_primitive(
                prim_path=f"/World/Object_{i}",
                primitive_props={"radius": 0.1},
                prim_type="Sphere",
                position=np.array([1.0 - 0.2*i, 0.2, 0.55]),
                orientation=euler_angles_to_quat(np.array([0, 0, 0])),
                color=np.array(color)
            )
        
        # Add lighting
        create_primitive(
            prim_path="/World/DomeLight",
            prim_type="DomeLight",
            position=np.array([0, 0, 0]),
            attributes={"color": (0.75, 0.75, 0.75), "intensity": 3000}
        )
    
    def setup_cameras(self):
        """Add RGB and depth cameras to the robot"""
        # Add RGB camera
        self.camera = Camera(
            prim_path="/World/Robot/base_link/camera",
            frequency=30,
            resolution=(640, 480)
        )
        
        self.world.scene.add(self.camera)
        
        # Add depth camera (we'll use the same camera with depth attachment)
        self.depth_camera = Camera(
            prim_path="/World/Robot/base_link/depth_camera",
            frequency=30,
            resolution=(640, 480)
        )
        
        self.world.scene.add(self.depth_camera)
    
    def capture_data(self, frame_number, output_dir="synthetic_data"):
        """Capture synchronized RGB and depth data"""
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Capture RGB image
        rgb_data = self.camera.get_rgb()
        rgb_filename = f"{output_dir}/rgb_{frame_number:04d}.png"
        cv2.imwrite(rgb_filename, cv2.cvtColor(rgb_data, cv2.COLOR_RGB2BGR))
        
        # Capture depth data
        depth_data = self.depth_camera.get_depth()
        depth_filename = f"{output_dir}/depth_{frame_number:04d}.png"
        
        # Convert depth to 16-bit PNG for better precision
        depth_scaled = (depth_data * 1000).astype(np.uint16)  # Scale to mm for better precision
        cv2.imwrite(depth_filename, depth_scaled)
        
        # Get robot pose for this frame
        robot = self.world.scene.get_object("Robot")
        if robot:
            position, orientation = robot.get_world_pose()
            
            # Save pose information
            pose_filename = f"{output_dir}/pose_{frame_number:04d}.txt"
            with open(pose_filename, 'w') as f:
                f.write(f"position: {position[0]} {position[1]} {position[2]}\n")
                f.write(f"orientation: {orientation[0]} {orientation[1]} {orientation[2]} {orientation[3]}\n")
        
        carb.log_info(f"Captured frame {frame_number:04d}")
    
    def run_simulation(self, num_frames=100):
        """Run the simulation and capture data"""
        self.world.reset()
        
        for i in range(num_frames):
            # Step the world
            self.world.step(render=True)
            
            # Periodically move robot to capture different views
            if self.world.current_step_index % 100 == 0:
                # Move robot forward slightly
                robot = self.world.scene.get_object("Robot")
                if robot:
                    pos, ori = robot.get_world_pose()
                    robot.set_world_pose(position=np.array([pos[0]+0.01, pos[1], pos[2]], dtype=np.float32))
            
            # Capture data every N steps
            if self.world.current_step_index % 10 == 0:
                self.capture_data(self.world.current_step_index // 10)


# Usage
def main():
    # Initialize Isaac Sim
    scene = IsaacSimScene()
    
    # Setup the environment
    scene.create_environment()
    scene.setup_cameras()
    
    # Run simulation and capture data
    scene.run_simulation(num_frames=500)  # Run for 500 steps
    
    carb.log_info("Data capture completed!")


if __name__ == "__main__":
    main()
```

### Hints

- Use USD materials for realistic textures
- Consider camera exposure settings for synthetic data quality
- Implement scene randomization to diversify training data
- Save data in formats compatible with standard ML pipelines

## Exercise 2: Deep Learning-Based Object Grasping

Implement a grasp planning system that uses AI to determine the best grasp point on an object.

### Instructions

1. Create a deep learning model for grasp detection:
   - Take RGB-D images as input
   - Output grasp quality and angle at each pixel
   - Use a U-Net or similar architecture

2. Implement data collection in Isaac Sim:
   - Generate diverse objects and lighting conditions
   - Record successful and failed grasps
   - Create labeled training data

3. Deploy the model to predict grasps:
   - Process camera images from robot
   - Select highest-scoring grasp
   - Execute grasp and evaluate success

4. Integrate with robot control:
   - Convert 2D grasp prediction to 3D world coordinates
   - Plan trajectory to grasp location
   - Execute grasp maneuver

### Solution

First, create the grasp detection model (grasp_detector.py):

```python
import torch
import torch.nn as nn
import torch.nn.functional as F


class GraspDetector(nn.Module):
    def __init__(self, input_channels=4):  # RGB + depth
        super(GraspDetector, self).__init__()
        
        # Encoder (downsampling path)
        self.enc1 = self.double_conv(input_channels, 32)
        self.pool1 = nn.MaxPool2d(2)
        
        self.enc2 = self.double_conv(32, 64)
        self.pool2 = nn.MaxPool2d(2)
        
        self.enc3 = self.double_conv(64, 128)
        self.pool3 = nn.MaxPool2d(2)
        
        self.enc4 = self.double_conv(128, 256)
        self.pool4 = nn.MaxPool2d(2)
        
        # Bottleneck
        self.bottleneck = self.double_conv(256, 512)
        
        # Decoder (upsampling path)
        self.upconv4 = nn.ConvTranspose2d(512, 256, 2, stride=2)
        self.dec4 = self.double_conv(512, 256)
        
        self.upconv3 = nn.ConvTranspose2d(256, 128, 2, stride=2)
        self.dec3 = self.double_conv(256, 128)
        
        self.upconv2 = nn.ConvTranspose2d(128, 64, 2, stride=2)
        self.dec2 = self.double_conv(128, 64)
        
        self.upconv1 = nn.ConvTranspose2d(64, 32, 2, stride=2)
        self.dec1 = self.double_conv(64, 32)
        
        # Output heads
        self.quality_head = nn.Conv2d(32, 1, 1)
        self.angle_head = nn.Conv2d(32, 1, 1)
        
    def double_conv(self, in_channels, out_channels):
        return nn.Sequential(
            nn.Conv2d(in_channels, out_channels, 3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, 3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )
    
    def forward(self, x):
        # Encoder
        enc1 = self.enc1(x)  # 32 channels
        enc2 = self.enc2(self.pool1(enc1))  # 64 channels
        enc3 = self.enc3(self.pool2(enc2))  # 128 channels
        enc4 = self.enc4(self.pool3(enc3))  # 256 channels
        
        bottleneck = self.bottleneck(self.pool4(enc4))  # 512 channels
        
        # Decoder
        dec4 = self.upconv4(bottleneck)  # 256 channels
        dec4 = torch.cat((dec4, enc4), dim=1)  # 256 + 256 = 512 channels
        dec4 = self.dec4(dec4)  # 256 channels
        
        dec3 = self.upconv3(dec4)  # 128 channels
        dec3 = torch.cat((dec3, enc3), dim=1)  # 128 + 128 = 256 channels
        dec3 = self.dec3(dec3)  # 128 channels
        
        dec2 = self.upconv2(dec3)  # 64 channels
        dec2 = torch.cat((dec2, enc2), dim=1)  # 64 + 64 = 128 channels
        dec2 = self.dec2(dec2)  # 64 channels
        
        dec1 = self.upconv1(dec2)  # 32 channels
        dec1 = torch.cat((dec1, enc1), dim=1)  # 32 + 32 = 64 channels
        dec1 = self.dec1(dec1)  # 32 channels
        
        # Output heads
        quality = torch.sigmoid(self.quality_head(dec1))  # Grasp quality [0,1]
        angle = torch.tanh(self.angle_head(dec1)) * torch.pi  # Grasp angle [-π, π]
        
        return quality, angle


class GraspPlanningNode:
    def __init__(self):
        # Initialize the grasp detector model
        self.model = GraspDetector(input_channels=4)  # RGB + depth
        # Load pre-trained weights (in practice)
        # self.model.load_state_dict(torch.load('grasp_model.pth'))
        self.model.eval()
        
        # Device
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        
        # Camera parameters (in practice, from calibration)
        self.fx = 554.25469  # Focal length x
        self.fy = 554.25469  # Focal length y
        self.cx = 320.0      # Principal point x
        self.cy = 240.0      # Principal point y
    
    def preprocess_input(self, rgb_image, depth_image):
        """Preprocess RGB and depth images for the network"""
        # Resize images to network input size
        input_size = (480, 640)  # Height, Width
        rgb_resized = cv2.resize(rgb_image, (input_size[1], input_size[0]))  # (Width, Height)
        depth_resized = cv2.resize(depth_image, (input_size[1], input_size[0]))
        
        # Normalize RGB image
        rgb_normalized = rgb_resized.astype(np.float32) / 255.0
        
        # Normalize depth image (assuming max depth of 5 meters)
        depth_normalized = depth_resized.astype(np.float32) / 5.0
        
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
    
    def find_best_grasp(self, quality_map, angle_map):
        """Find the best grasp from quality and angle maps"""
        # Convert to numpy for processing
        if isinstance(quality_map, torch.Tensor):
            quality_map = quality_map.squeeze().cpu().numpy()
            angle_map = angle_map.squeeze().cpu().numpy()
        
        # Find the location with highest grasp quality
        best_y, best_x = np.unravel_index(np.argmax(quality_map), quality_map.shape)
        
        # Get the corresponding angle
        best_angle = angle_map[best_y, best_x]
        
        # Calculate world coordinates using depth
        # For now, return image coordinates and angle
        return {
            'x': int(best_x),
            'y': int(best_y),
            'angle': float(best_angle),
            'quality': float(quality_map[best_y, best_x]),
            'center_offset_x': (best_x - quality_map.shape[1]/2) / quality_map.shape[1],  # Normalized offset
            'center_offset_y': (best_y - quality_map.shape[0]/2) / quality_map.shape[0]   # Normalized offset
        }
    
    def image_to_world(self, u, v, depth):
        """Convert image coordinates to world coordinates"""
        # Convert pixel coordinates to camera coordinates
        x_cam = (u - self.cx) * depth / self.fx
        y_cam = (v - self.cy) * depth / self.fy
        
        # In practice, you'd also need to transform from camera to world frame
        # This requires camera extrinsic parameters
        # For now, just return camera frame coordinates
        return np.array([x_cam, y_cam, depth])
    
    def predict_grasp(self, rgb_image, depth_image):
        """Predict the best grasp for a given RGB-D image"""
        # Preprocess input
        input_tensor = self.preprocess_input(rgb_image, depth_image)
        
        # Run inference
        with torch.no_grad():
            quality_pred, angle_pred = self.model(input_tensor)
        
        # Find the best grasp
        best_grasp = self.find_best_grasp(quality_pred, angle_pred)
        
        # Get depth at grasp location
        grasp_depth = depth_image[int(best_grasp['y']), int(best_grasp['x'])] if (
            0 <= best_grasp['y'] < depth_image.shape[0] and 
            0 <= best_grasp['x'] < depth_image.shape[1]
        ) else 1.0  # Default depth if out of bounds
        
        # Convert to world coordinates
        world_coords = self.image_to_world(
            best_grasp['x'], 
            best_grasp['y'], 
            grasp_depth
        )
        
        best_grasp['world_position'] = world_coords
        best_grasp['depth'] = grasp_depth
        
        return best_grasp


def main():
    # Initialize
    grasp_planner = GraspPlanningNode()
    
    # Load sample images (in practice, from robot camera)
    # For demo purposes:
    rgb_sample = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    depth_sample = np.random.rand(480, 640).astype(np.float32) * 2.0 + 0.5  # 0.5-2.5m range
    
    # Predict grasp
    best_grasp = grasp_planner.predict_grasp(rgb_sample, depth_sample)
    
    print(f"Best Grasp: Position={best_grasp['world_position']}, Quality={best_grasp['quality']:.3f}, Angle={best_grasp['angle']:.3f}rad")
    
    return best_grasp
```

Then create the ROS 2 integration (grasp_integration.py):

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Pose, Point, Quaternion
from std_msgs.msg import Float32
from cv_bridge import CvBridge
import numpy as np
import cv2
from grasp_detector import GraspPlanningNode


class GraspROSNode(Node):
    def __init__(self):
        super().__init__('grasp_ros_node')
        
        # Initialize components
        self.bridge = CvBridge()
        self.grasp_planner = GraspPlanningNode()
        
        # Current sensor data
        self.rgb_image = None
        self.depth_image = None
        
        # Subscribers
        self.rgb_sub = self.create_subscription(
            Image, '/camera/rgb/image_raw', self.rgb_callback, 10
        )
        self.depth_sub = self.create_subscription(
            Image, '/camera/depth/image_raw', self.depth_callback, 10
        )
        
        # Publishers
        self.grasp_pose_pub = self.create_publisher(Pose, '/best_grasp_pose', 10)
        self.grasp_quality_pub = self.create_publisher(Float32, '/grasp_quality', 10)
        
        # Timer for grasp planning
        self.grasp_timer = self.create_timer(1.0, self.plan_grasp)
        
        self.get_logger().info("Grasp ROS Node initialized")
    
    def rgb_callback(self, msg):
        """Process RGB image"""
        try:
            self.rgb_image = self.bridge.imgmsg_to_cv2(msg, 'rgb8')
        except Exception as e:
            self.get_logger().error(f"Error converting RGB image: {e}")
    
    def depth_callback(self, msg):
        """Process depth image"""
        try:
            self.depth_image = self.bridge.imgmsg_to_cv2(msg, '32FC1')
        except Exception as e:
            self.get_logger().error(f"Error converting depth image: {e}")
    
    def plan_grasp(self):
        """Plan a grasp when both images are available"""
        if self.rgb_image is None or self.depth_image is None:
            self.get_logger().warn("Waiting for both RGB and depth images")
            return
        
        try:
            # Plan grasp
            grasp = self.grasp_planner.predict_grasp(self.rgb_image, self.depth_image)
            
            if grasp['quality'] > 0.5:  # Only publish high-quality grasps
                # Create pose message
                pose_msg = Pose()
                pose_msg.position.x = float(grasp['world_position'][0])
                pose_msg.position.y = float(grasp['world_position'][1])
                pose_msg.position.z = float(grasp['world_position'][2])
                
                # Convert angle to quaternion (simplified - only rotation around Z)
                angle = grasp['angle']
                pose_msg.orientation.z = np.sin(angle / 2.0)
                pose_msg.orientation.w = np.cos(angle / 2.0)
                
                # Publish pose
                self.grasp_pose_pub.publish(pose_msg)
                
                # Publish quality
                quality_msg = Float32()
                quality_msg.data = float(grasp['quality'])
                self.grasp_quality_pub.publish(quality_msg)
                
                self.get_logger().info(
                    f"Published grasp: Pos({pose_msg.position.x:.3f}, {pose_msg.position.y:.3f}, {pose_msg.position.z:.3f}), "
                    f"Quality: {quality_msg.data:.3f}, Angle: {angle:.3f}rad"
                )
            else:
                self.get_logger().warn(f"Low quality grasp found: {grasp['quality']:.3f}")
                
        except Exception as e:
            self.get_logger().error(f"Error planning grasp: {e}")


def main(args=None):
    rclpy.init(args=args)
    node = GraspROSNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### Hints

- Use data augmentation to improve model generalization
- Consider the physical constraints of your robot gripper
- Implement grasp verification to avoid false positives
- Evaluate on real robot once validated in simulation

## Exercise 3: Bipedal Walking with MPC Controller

Create a model predictive controller for bipedal walking that maintains balance while stepping.

### Instructions

1. Implement an LIPM (Linear Inverted Pendulum Model) for bipedal balance:
   - Calculate Zero Moment Point (ZMP)
   - Plan center of mass trajectory
   - Account for foot placement constraints

2. Design an MPC controller:
   - Predict future states over a horizon
   - Optimize for balance and trajectory tracking
   - Consider torque and stepping constraints

3. Simulate the walking controller:
   - Implement in Isaac Sim or Gazebo
   - Test on different terrains
   - Evaluate stability metrics

4. Integrate with perception for adaptive walking:
   - Detect terrain changes
   - Adjust gait parameters accordingly
   - Handle obstacles dynamically

### Solution

First, create the LIPM and MPC components (bipedal_controller.py):

```python
import numpy as np
from scipy.optimize import minimize
import cvxpy as cp


class LinearInvertedPendulumModel:
    def __init__(self, height=0.8, gravity=9.81):
        self.height = height
        self.gravity = gravity
        self.omega = np.sqrt(gravity / height)
        
        # Current state: [com_x, com_y, com_dx, com_dy]
        self.state = np.zeros(4)
        
    def compute_zmp(self, com_pos, com_vel):
        """Compute Zero Moment Point from CoM position and velocity"""
        zmp_x = com_pos[0] - (com_pos[2] / self.gravity) * com_vel[0]
        zmp_y = com_pos[1] - (com_pos[2] / self.gravity) * com_vel[1]
        return np.array([zmp_x, zmp_y])
    
    def dynamics_step(self, com_pos, com_vel, zmp, dt):
        """Step the LIPM dynamics forward in time"""
        # Linear Inverted Pendulum Model equations
        com_acc = self.omega**2 * (com_pos[:2] - zmp)
        
        # Integrate velocity and position
        com_vel[:2] += com_acc * dt
        com_pos[:2] += com_vel[:2] * dt
        
        # Z stays constant in LIPM
        # Update state
        self.state[:2] = com_pos[:2]  # x, y
        self.state[2:] = com_vel[:2]  # dx, dy
        
        return com_pos, com_vel


class BipedalMPCController:
    def __init__(self, com_height=0.8, dt=0.01, horizon=50):
        self.lipm = LinearInvertedPendulumModel(height=com_height)
        self.dt = dt
        self.horizon = horizon  # Prediction horizon
        
        # Walking parameters
        self.step_length = 0.3  # 30 cm step
        self.step_width = 0.2   # 20 cm step width
        self.step_duration = 1.0  # 1 second per step
        
        # Foot positions (left foot, right foot)
        self.left_foot_pos = np.array([0.0, self.step_width/2, 0.0])
        self.right_foot_pos = np.array([0.0, -self.step_width/2, 0.0])
        self.support_foot = 'left'  # Which foot is supporting now
        
        # MPC weights
        self.Q = np.diag([10.0, 10.0, 1.0, 1.0])  # State cost (x, y, dx, dy)
        self.R = np.diag([0.1, 0.1])  # Control cost (zmp_x, zmp_y)
        self.Q_terminal = np.diag([100.0, 100.0, 10.0, 10.0])  # Terminal cost
    
    def predict_trajectory(self, current_state, zmp_sequence):
        """Predict CoM trajectory given ZMP sequence"""
        predicted_states = []
        current_com_pos = current_state[:2].copy()
        current_com_vel = current_state[2:].copy()
        
        for zmp in zmp_sequence:
            # Update CoM using LIPM
            com_acc = self.lipm.omega**2 * (current_com_pos - zmp)
            current_com_vel += com_acc * self.dt
            current_com_pos += current_com_vel * self.dt
            
            # Store state
            state = np.concatenate([current_com_pos, current_com_vel])
            predicted_states.append(state.copy())
        
        return np.array(predicted_states)
    
    def mpc_optimization(self, current_state, desired_trajectory):
        """Solve MPC optimization problem"""
        # Optimization variables: ZMP sequence for the horizon
        zmp_vars = cp.Variable((self.horizon, 2))
        
        # Cost function components
        total_cost = 0
        
        # Predict state evolution
        state = current_state.copy()
        for i in range(self.horizon):
            # Dynamics: x_next = A*x + B*u
            com_acc = self.lipm.omega**2 * (state[:2] - zmp_vars[i])
            next_state = state.copy()
            next_state[:2] += state[2:] * self.dt  # Position update
            next_state[2:] += com_acc * self.dt   # Velocity update
            
            # State cost: ||state - desired_state||_Q^2
            if i < len(desired_trajectory):
                state_error = next_state - desired_trajectory[i]
            else:
                # If beyond trajectory, stay at last known position
                state_error = next_state - desired_trajectory[-1]
            
            total_cost += cp.quad_form(state_error, self.Q)
            
            # Control cost: ||zmp||_R^2
            total_cost += cp.quad_form(zmp_vars[i], self.R)
            
            # Update state for next iteration
            state = next_state
        
        # Terminal cost
        terminal_state_error = state - desired_trajectory[-1]
        total_cost += cp.quad_form(terminal_state_error, self.Q_terminal)
        
        # Constraints
        constraints = []
        
        # Reasonable ZMP bounds (relative to support foot)
        support_pos = self.left_foot_pos if self.support_foot == 'left' else self.right_foot_pos
        zmp_x_min, zmp_x_max = support_pos[0] - 0.1, support_pos[0] + 0.1
        zmp_y_min, zmp_y_max = support_pos[1] - 0.1, support_pos[1] + 0.1
        
        for i in range(self.horizon):
            constraints.extend([
                zmp_vars[i, 0] >= zmp_x_min,
                zmp_vars[i, 0] <= zmp_x_max,
                zmp_vars[i, 1] >= zmp_y_min,
                zmp_vars[i, 1] <= zmp_y_max
            ])
        
        # Solve optimization problem
        prob = cp.Problem(cp.Minimize(total_cost), constraints)
        prob.solve(verbose=False)
        
        if prob.status not in ["optimal", "optimal_inaccurate"]:
            print(f"MPC optimization failed: {prob.status}")
            return None
        
        # Return optimal ZMP sequence
        return zmp_vars.value
    
    def generate_desired_trajectory(self, walk_direction, num_steps=10):
        """Generate desired walking trajectory"""
        # Simple straight-line walking trajectory
        dx, dy = walk_direction
        step_interval = self.step_duration / self.dt  # Steps in simulation time
        
        trajectory = []
        base_x, base_y = 0.0, 0.0
        
        for i in range(self.horizon):
            t = i * self.dt
            # Interpolate between steps
            step_num = int(t / self.step_duration)
            
            if self.support_foot == 'left':
                # Currently left foot is supporting, moving right foot
                x = base_x + dx * step_num * self.step_length
                y = base_y + dy * step_num * self.step_width
            else:
                # Currently right foot is supporting, moving left foot
                x = base_x + dx * step_num * self.step_length
                y = base_y + dy * step_num * self.step_width
            
            # Add smooth transitions between steps
            step_progress = (t % self.step_duration) / self.step_duration
            if step_progress < 0.5:  # First half of step - stay put
                pos_x = x
                pos_y = y
            else:  # Second half - prepare for next step
                pos_x = x + dx * self.step_length * step_progress
                pos_y = y + dy * self.step_width * step_progress
            
            # Velocity (derivative of position)
            vel_x = dx * self.step_length / self.step_duration if step_progress >= 0.5 else 0
            vel_y = dy * self.step_width / self.step_duration if step_progress >= 0.5 else 0
            
            # State = [pos_x, pos_y, vel_x, vel_y]
            state = np.array([pos_x, pos_y, vel_x, vel_y])
            trajectory.append(state)
        
        return np.array(trajectory)
    
    def compute_control(self, current_state, walk_direction):
        """Compute control ZMP given current state and desired direction"""
        # Generate desired trajectory based on walking direction
        desired_traj = self.generate_desired_trajectory(walk_direction, num_steps=self.horizon)
        
        # Solve MPC problem
        optimal_zmps = self.mpc_optimization(current_state, desired_traj)
        
        if optimal_zmps is not None:
            # Return first control action
            return optimal_zmps[0]
        else:
            # Fallback: use current ZMP
            zmp = self.lipm.compute_zmp(current_state[:2], current_state[2:])
            return zmp


class BipedalWalkNode:
    def __init__(self):
        # Initialize MPC controller
        self.mpc_controller = BipedalMPCController(com_height=0.85)
        
        # Robot state (CoM position and velocity)
        self.com_state = np.array([0.0, 0.0, 0.0, 0.0])  # [x, y, dx, dy]
        
        # Walking direction (normalized)
        self.walk_direction = np.array([1.0, 0.0])  # Moving forward initially
        
        # Timer for control loop
        self.walk_timer = self.create_timer(0.01, self.walk_control_loop)  # 100 Hz
    
    def walk_control_loop(self):
        """Main walking control loop"""
        # Compute desired ZMP using MPC
        desired_zmp = self.mpc_controller.compute_control(self.com_state, self.walk_direction)
        
        if desired_zmp is not None:
            # Apply control using LIPM dynamics
            com_acc = self.mpc_controller.lipm.omega**2 * (self.com_state[:2] - desired_zmp)
            
            # Update state
            self.com_state[2:] += com_acc * self.mpc_controller.dt  # Update velocity
            self.com_state[:2] += self.com_state[2:] * self.mpc_controller.dt  # Update position
            
            # Log walking progress
            self.get_logger().info(f"Walking: Pos({self.com_state[0]:.3f}, {self.com_state[1]:.3f}), Vel({self.com_state[2]:.3f}, {self.com_state[3]:.3f})")
            
            # Update support foot based on walking pattern
            current_time = self.get_clock().now().nanoseconds / 1e9
            step_phase = (current_time / self.mpc_controller.step_duration) % 2
            if step_phase < 1:
                self.mpc_controller.support_foot = 'left'
            else:
                self.mpc_controller.support_foot = 'right'


def main(args=None):
    rclpy.init(args=args)
    walk_node = BipedalWalkNode()
    
    try:
        rclpy.spin(walk_node)
    except KeyboardInterrupt:
        pass
    finally:
        walk_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### Hints

- Start with a simple balancing task before adding walking
- Monitor ZMP error to assess balance quality
- Consider foot rotation and placement for turning maneuvers
- Implement recovery behaviors to handle disturbances

## Chapter Summary

These exercises demonstrated key concepts in AI-powered robotics:
- Creating synthetic training data with Isaac Sim
- Implementing deep learning for robot perception and manipulation
- Developing control systems for complex behaviors like bipedal walking
- Integrating perception, planning, and control for complete robotic systems

## Checklist

- [ ] Create Isaac Sim scene with perception sensors
- [ ] Implement deep learning grasp planning system
- [ ] Deploy model for real-time inference
- [ ] Design MPC controller for bipedal walking
- [ ] Integrate perception for adaptive behaviors
- [ ] Validate algorithms in simulation
- [ ] Test on physical robot (when available)

## References

- [NVIDIA Isaac Sim Documentation](https://docs.omniverse.nvidia.com/isaacsim/latest/index.html)
- [ROS 2 Navigation2 Tutorials](https://navigation.ros.org/tutorials/)
- [Deep Reinforcement Learning for Robotics](https://arxiv.org/abs/1804.00495)
- [Model Predictive Control for Robotics](https://ieeexplore.ieee.org/document/8794269)