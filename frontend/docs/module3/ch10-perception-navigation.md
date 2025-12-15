---
title: 'Chapter 10 - Perception: VSLAM, Navigation, Object Detection'
description: 'Advanced perception systems for humanoid robots using VSLAM and object detection'
---

# Chapter 10: Perception: VSLAM, Navigation, Object Detection

## Learning Objectives

After reading this chapter, you will be able to:
- Implement Visual Simultaneous Localization and Mapping (VSLAM) systems
- Configure and tune navigation stacks for humanoid robots
- Develop object detection and recognition systems for robotics
- Integrate perception systems with higher-level planning
- Optimize perception pipelines for real-time performance
- Handle perceptual uncertainty in robot decision-making
- Validate perception system accuracy against ground truth
- Design perception-action loops for closed-loop control

## Introduction

Perception systems are fundamental to autonomous humanoid robots, enabling them to understand and navigate their environment. This chapter covers advanced perception techniques including Visual SLAM (VSLAM) for localization and mapping, navigation systems for path planning and obstacle avoidance, and object detection for scene understanding. These systems work together to provide the robot with awareness of its surroundings and the ability to interact with objects.

## Visual SLAM (VSLAM) for Humanoid Robots

### VSLAM Fundamentals

Visual SLAM (Simultaneous Localization and Mapping) systems allow robots to build a map of an unknown environment while simultaneously determining their location within that map, using only visual sensors like cameras.

Key components of VSLAM:
1. **Feature Detection**: Identifying distinctive points in images
2. **Feature Tracking**: Matching features between consecutive frames
3. **Pose Estimation**: Calculating camera/robot motion
4. **Mapping**: Building and maintaining the environmental map
5. **Loop Closure**: Detecting revisited locations to correct drift

### VSLAM Approaches

#### Feature-Based VSLAM
- Extracts and tracks distinctive visual features
- Examples: ORB-SLAM, LSD-SLAM, SVO
- Advantages: Good for textured environments, well-understood
- Disadvantages: Fails in low-texture environments

#### Direct VSLAM
- Uses raw pixel intensities directly
- Examples: DTAM, LSD-SLAM
- Advantages: Works in low-texture environments
- Disadvantages: Computationally intensive, sensitive to lighting

### Implementing ORB-SLAM in Isaac Sim

```python
# vslam_system.py
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry
from cv_bridge import CvBridge
import cv2
import numpy as np
from typing import List, Dict, Any, Optional
import threading
import time
from scipy.spatial.transform import Rotation as R


class VSLAMNode(Node):
    """VSLAM node for humanoid robot visual localization and mapping"""
    
    def __init__(self):
        super().__init__('vslam_node')
        
        # CV Bridge for image conversion
        self.bridge = CvBridge()
        
        # Initialize ORB detector
        self.orb = cv2.ORB_create(nfeatures=2000)
        self.bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        
        # Camera parameters
        self.camera_matrix = None
        self.distortion_coefficients = None
        self.camera_info_received = False
        
        # Tracking variables
        self.prev_frame = None
        self.prev_kp = None
        self.prev_desc = None
        self.current_position = np.array([0, 0, 0], dtype=np.float32)
        self.current_orientation = np.array([0, 0, 0, 1], dtype=np.float32)  # Quaternion
        self.keyframes = []
        self.map_points = {}  # 3D points in the map
        self.frame_id = 0
        
        # Publishers and subscribers
        self.image_sub = self.create_subscription(
            Image,
            '/camera/rgb/image_raw',
            self.image_callback,
            10
        )
        
        self.camera_info_sub = self.create_subscription(
            CameraInfo,
            '/camera/camera_info',
            self.camera_info_callback,
            10
        )
        
        self.pose_pub = self.create_publisher(PoseStamped, '/vslam/pose', 10)
        self.odom_pub = self.create_publisher(Odometry, '/vslam/odometry', 10)
        self.map_pub = self.create_publisher(PointCloud2, '/vslam/map_points', 10)
        
        # SLAM parameters
        self.declare_parameter('max_translation_threshold', 0.5)  # meters
        self.declare_parameter('max_rotation_threshold', 0.2)    # radians
        self.declare_parameter('min_features_for_tracking', 20)
        
        self.translation_threshold = self.get_parameter('max_translation_threshold').value
        self.rotation_threshold = self.get_parameter('max_rotation_threshold').value
        self.min_features_for_tracking = self.get_parameter('min_features_for_tracking').value
        
        # Threading for performance
        self.processing_lock = threading.Lock()
        
        self.get_logger().info("VSLAM node initialized")
    
    def camera_info_callback(self, msg):
        """Process camera calibration parameters"""
        if not self.camera_info_received:
            self.camera_matrix = np.array(msg.k).reshape(3, 3)
            self.distortion_coefficients = np.array(msg.d)
            self.camera_info_received = True
            self.get_logger().info("Camera parameters received")
    
    def image_callback(self, msg):
        """Process incoming camera images for VSLAM"""
        if not self.camera_info_received:
            # Can't process images without camera calibration
            return
        
        try:
            # Convert ROS image to OpenCV
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f"Error converting image: {e}")
            return
        
        # Process frame with VSLAM
        with self.processing_lock:
            self.process_frame(cv_image, msg.header.stamp)
    
    def process_frame(self, frame: np.ndarray, timestamp):
        """Process a single frame for VSLAM"""
        # Detect and compute features
        kp = self.orb.detect(frame, None)
        kp, desc = self.orb.compute(frame, kp)
        
        if desc is None or len(kp) < self.min_features_for_tracking:
            self.get_logger().warn(f"Insufficient features detected: {len(kp) if kp else 0}")
            return
        
        if self.prev_desc is not None and self.prev_kp is not None:
            # Match features with previous frame
            matches = self.bf.match(self.prev_desc, desc)
            matches = sorted(matches, key=lambda x: x.distance)
            
            # Keep only good matches
            good_matches = matches[:max(len(matches)//2, 100)]
            
            if len(good_matches) >= 10:  # Minimum matches to continue
                # Extract matched keypoints
                prev_pts = np.float32([self.prev_kp[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
                curr_pts = np.float32([kp[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
                
                # Estimate essential matrix and compute motion
                E, mask = cv2.findEssentialMat(
                    curr_pts, 
                    prev_pts, 
                    self.camera_matrix, 
                    cv2.RANSAC, 
                    threshold=1.0
                )
                
                if E is not None:
                    # Recover pose from essential matrix
                    _, R, t, mask = cv2.recoverPose(E, curr_pts, prev_pts, self.camera_matrix)
                    
                    # Convert rotation matrix to quaternion
                    quat = self.rotation_matrix_to_quaternion(R)
                    
                    # Check for significant motion to decide if this frame is a keyframe
                    translation_norm = np.linalg.norm(t)
                    rotation_angle = np.arccos(np.clip((np.trace(R) - 1) / 2, -1, 1))
                    
                    is_keyframe = (translation_norm > self.translation_threshold or 
                                  rotation_angle > self.rotation_threshold)
                    
                    if is_keyframe:
                        # Update robot pose
                        self.update_robot_pose(t, quat)
                        
                        # Add keyframe to map
                        self.add_keyframe(frame, kp, desc, timestamp)
                        
                        # Try triangulation for new map points (simplified)
                        self.triangulate_points(prev_pts, curr_pts, R, t)
                        
                        # Publish pose and odometry
                        self.publish_pose_and_odom(timestamp)
        
        # Store current frame as previous for next iteration
        self.prev_frame = frame
        self.prev_kp = kp
        self.prev_desc = desc
        self.frame_id += 1
    
    def rotation_matrix_to_quaternion(self, R):
        """Convert 3x3 rotation matrix to quaternion"""
        # Using scipy for more robust conversion
        r = R.from_matrix(R)
        return r.as_quat()
    
    def update_robot_pose(self, translation: np.ndarray, rotation_quat: np.ndarray):
        """Update robot pose based on relative motion"""
        # Integrate translation
        self.current_position += translation.flatten()
        
        # Integrate rotation
        prev_rot = R.from_quat(self.current_orientation)
        curr_rot = R.from_quat(rotation_quat)
        integrated_rot = prev_rot * curr_rot
        self.current_orientation = integrated_rot.as_quat()
    
    def add_keyframe(self, frame: np.ndarray, kp: List[cv2.KeyPoint], 
                     desc: np.ndarray, timestamp):
        """Add a keyframe to the map"""
        keyframe = {
            'frame_id': self.frame_id,
            'timestamp': timestamp,
            'image': frame.copy(),
            'keypoints': kp,
            'descriptors': desc,
            'position': self.current_position.copy(),
            'orientation': self.current_orientation.copy()
        }
        
        self.keyframes.append(keyframe)
        self.get_logger().info(f"Added keyframe #{len(self.keyframes)} at position: "
                              f"({self.current_position[0]:.2f}, {self.current_position[1]:.2f}, {self.current_position[2]:.2f})")
    
    def triangulate_points(self, prev_pts: np.ndarray, curr_pts: np.ndarray, 
                          R: np.ndarray, t: np.ndarray):
        """Triangulate 3D points from matched features"""
        # This is a simplified approach - in practice would need more sophisticated triangulation
        # with proper camera pose tracking
        
        # For demonstration, we'll create simple 3D points
        # In real implementation, would use triangulation based on camera motion
        if len(prev_pts) >= 4 and len(curr_pts) >= 4:
            # Triangulation requires camera pose differences
            # For now, just add some random points to simulate map building
            for i in range(min(len(prev_pts), 10)):  # Add up to 10 points per frame
                x = self.current_position[0] + np.random.normal(0, 2)
                y = self.current_position[1] + np.random.normal(0, 2)
                z = self.current_position[2] + np.random.normal(0, 1)
                
                point_id = f"point_{self.frame_id}_{i}"
                self.map_points[point_id] = (x, y, z)
    
    def publish_pose_and_odom(self, timestamp):
        """Publish robot pose and odometry messages"""
        
        # Publish PoseStamped
        pose_msg = PoseStamped()
        pose_msg.header.stamp = timestamp
        pose_msg.header.frame_id = 'map'
        pose_msg.pose.position.x = float(self.current_position[0])
        pose_msg.pose.position.y = float(self.current_position[1])
        pose_msg.pose.position.z = float(self.current_position[2])
        pose_msg.pose.orientation.x = float(self.current_orientation[0])
        pose_msg.pose.orientation.y = float(self.current_orientation[1])
        pose_msg.pose.orientation.z = float(self.current_orientation[2])
        pose_msg.pose.orientation.w = float(self.current_orientation[3])
        
        self.pose_pub.publish(pose_msg)
        
        # Publish Odometry
        odom_msg = Odometry()
        odom_msg.header.stamp = timestamp
        odom_msg.header.frame_id = 'map'
        odom_msg.child_frame_id = 'base_link'
        odom_msg.pose.pose = pose_msg.pose
        
        # Add covariance (placeholder values)
        odom_msg.pose.covariance = [0.0] * 36  # Identity-like diagonal matrix would be better
        for i in range(6):
            odom_msg.pose.covariance[i*6 + i] = 0.01  # Position uncertainty
        
        self.odom_pub.publish(odom_msg)
    
    def publish_map(self):
        """Publish current map as point cloud"""
        # This would need proper point cloud generation
        # For now, just log the number of points
        self.get_logger().info(f"Current map has {len(self.map_points)} 3D points")


class NavigationNode(Node):
    """Navigation node implementing path planning and obstacle avoidance"""
    
    def __init__(self):
        super().__init__('navigation_node')
        
        # Navigation parameters
        self.declare_parameter('path_resolution', 0.1)  # meters
        self.declare_parameter('inflation_radius', 0.3)  # meters
        self.declare_parameter('planner_frequency', 5.0)  # Hz
        self.declare_parameter('controller_frequency', 20.0)  # Hz
        self.declare_parameter('max_velocity_linear', 0.5)  # m/s
        self.declare_parameter('max_velocity_angular', 0.5)  # rad/s
        
        self.path_resolution = self.get_parameter('path_resolution').value
        self.inflation_radius = self.get_parameter('inflation_radius').value
        self.planner_frequency = self.get_parameter('planner_frequency').value
        self.controller_frequency = self.get_parameter('controller_frequency').value
        self.max_linear_vel = self.get_parameter('max_velocity_linear').value
        self.max_angular_vel = self.get_parameter('max_velocity_angular').value
        
        # Robot state
        self.current_pose = None
        self.current_velocity = None
        self.goal_pose = None
        self.current_path = []
        self.path_index = 0
        
        # Subscribers
        self.pose_sub = self.create_subscription(
            PoseStamped, '/amcl_pose', self.pose_callback, 10
        )
        
        self.goal_sub = self.create_subscription(
            PoseStamped, '/move_base_simple/goal', self.goal_callback, 10
        )
        
        self.lidar_sub = self.create_subscription(
            LaserScan, '/scan', self.lidar_callback, 10
        )
        
        # Publishers
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.path_pub = self.create_publisher(Path, '/navigation/path', 10)
        self.local_costmap_pub = self.create_publisher(OccupancyGrid, '/local_costmap/costmap', 10)
        
        # Timers for planning and control
        self.planner_timer = self.create_timer(
            1.0/self.planner_frequency, 
            self.path_planning
        )
        
        self.controller_timer = self.create_timer(
            1.0/self.controller_frequency,
            self.motion_control
        )
        
        self.get_logger().info("Navigation node initialized")
    
    def pose_callback(self, msg):
        """Update robot's current pose"""
        self.current_pose = msg.pose
    
    def goal_callback(self, msg):
        """Handle navigation goal"""
        self.goal_pose = msg.pose
        self.get_logger().info(f"New navigation goal received: ({msg.pose.position.x:.2f}, {msg.pose.position.y:.2f})")
    
    def lidar_callback(self, msg):
        """Process LiDAR data for obstacle detection"""
        # Update local costmap based on LiDAR readings
        self.update_local_costmap(msg)
    
    def update_local_costmap(self, lidar_msg):
        """Update local costmap based on sensor data"""
        # This is a simplified local costmap implementation
        # In practice, would use more sophisticated costmap implementation
        ranges = lidar_msg.ranges
        angle_min = lidar_msg.angle_min
        angle_increment = lidar_msg.angle_increment
        
        # Create costmap based on LiDAR data
        # For this example, we'll just publish an empty message as placeholder
        costmap_msg = OccupancyGrid()
        costmap_msg.header.stamp = lidar_msg.header.stamp
        costmap_msg.header.frame_id = 'base_link'  # Robot-centered map
        costmap_msg.info.resolution = 0.1  # 10cm per cell
        costmap_msg.info.width = 100  # 100 cells wide
        costmap_msg.info.height = 100  # 100 cells tall
        
        # Center the robot
        costmap_msg.info.origin.position.x = -5.0  # 5m left of robot
        costmap_msg.info.origin.position.y = -5.0  # 5m behind robot
        
        # Generate costmap data (simplified with only empty space)
        costmap_msg.data = [0] * (costmap_msg.info.width * costmap_msg.info.height)  # All free space
        
        # Mark obstacles based on LiDAR data
        for i, range_val in enumerate(ranges):
            if not np.isinf(range_val) and not np.isnan(range_val) and range_val < 2.0:  # Within 2m
                angle = angle_min + i * angle_increment
                x_world = range_val * np.cos(angle)
                y_world = range_val * np.sin(angle)
                
                # Convert to costmap indices
                x_idx = int((x_world - costmap_msg.info.origin.position.x) / costmap_msg.info.resolution)
                y_idx = int((y_world - costmap_msg.info.origin.position.y) / costmap_msg.info.resolution)
                
                if (0 <= x_idx < costmap_msg.info.width and 
                    0 <= y_idx < costmap_msg.info.height):
                    idx = y_idx * costmap_msg.info.width + x_idx
                    costmap_msg.data[idx] = 100  # Mark as obstacle
        
        self.local_costmap_pub.publish(costmap_msg)
    
    def path_planning(self):
        """Plan path from current pose to goal pose"""
        if not self.current_pose or not self.goal_pose:
            return
        
        # In practice, this would call a path planner like A*, Dijkstra, or RRT
        # For this example, we'll create a simple straight-line path
        start_pos = self.current_pose.position
        goal_pos = self.goal_pose.position
        
        dx = goal_pos.x - start_pos.x
        dy = goal_pos.y - start_pos.y
        distance = np.sqrt(dx*dx + dy*dy)
        
        if distance < 0.1:  # Close enough to goal
            self.get_logger().info("Reached goal position!")
            # Publish zero velocity to stop
            stop_cmd = Twist()
            self.cmd_vel_pub.publish(stop_cmd)
            self.current_path = []
            return
        
        # Create simple path points along the line
        num_points = int(distance / self.path_resolution)
        self.current_path = []
        
        for i in range(num_points+1):
            t = i / num_points if num_points > 0 else 0
            point = PoseStamped()
            point.header.stamp = self.get_clock().now().to_msg()
            point.header.frame_id = 'map'
            point.pose.position.x = start_pos.x + t * dx
            point.pose.position.y = start_pos.y + t * dy
            point.pose.position.z = start_pos.z  # Maintain same height
            
            # Point robot toward goal direction
            goal_angle = np.arctan2(dy, dx)
            quat = R.from_euler('z', goal_angle).as_quat()
            point.pose.orientation.x = quat[0]
            point.pose.orientation.y = quat[1]
            point.pose.orientation.z = quat[2]
            point.pose.orientation.w = quat[3]
            
            self.current_path.append(point)
        
        # Publish the path for visualization
        path_msg = Path()
        path_msg.header.stamp = self.get_clock().now().to_msg()
        path_msg.header.frame_id = 'map'
        path_msg.poses = self.current_path
        
        self.path_pub.publish(path_msg)
        self.path_index = 0  # Reset to beginning of path
    
    def motion_control(self):
        """Control robot motion along planned path"""
        if not self.current_path or self.path_index >= len(self.current_path):
            return
        
        # Get next waypoint
        target_pose = self.current_path[self.path_index].pose
        current_pos = self.current_pose.position
        
        # Calculate distance to waypoint
        dx = target_pose.position.x - current_pos.x
        dy = target_pose.position.y - current_pos.y
        distance_to_waypoint = np.sqrt(dx*dx + dy*dy)
        
        # Check if we're close enough to current waypoint
        if distance_to_waypoint < 0.3:  # 30cm threshold
            self.path_index += 1
            if self.path_index >= len(self.current_path):
                self.get_logger().info("Reached end of path!")
                # Stop robot
                stop_cmd = Twist()
                self.cmd_vel_pub.publish(stop_cmd)
                return
        
        # Calculate velocity command to reach waypoint
        cmd_vel = self.calculate_velocity_to_waypoint(target_pose)
        self.cmd_vel_pub.publish(cmd_vel)
    
    def calculate_velocity_to_waypoint(self, target_pose):
        """Calculate velocity command to reach target waypoint"""
        cmd = Twist()
        
        current_pos = self.current_pose.position
        
        # Calculate distance and angle to target
        dx = target_pose.position.x - current_pos.x
        dy = target_pose.position.y - current_pos.y
        distance = np.sqrt(dx*dx + dy*dy)
        
        # Calculate desired heading
        desired_heading = np.arctan2(dy, dx)
        
        # Get current heading
        current_orientation = self.current_pose.orientation
        current_euler = self.quaternion_to_euler(current_orientation)
        current_heading = current_euler[2]
        
        # Calculate heading error
        heading_error = desired_heading - current_heading
        
        # Normalize angle
        while heading_error > np.pi:
            heading_error -= 2*np.pi
        while heading_error < -np.pi:
            heading_error += 2*np.pi
        
        # PID-like control for heading
        k_angular = 1.0
        cmd.angular.z = max(-self.max_angular_vel, min(self.max_angular_vel, k_angular * heading_error))
        
        # Calculate linear velocity based on distance and heading error
        if abs(heading_error) < 0.5:  # Only move forward if roughly aligned
            cmd.linear.x = min(self.max_linear_vel, distance * 0.5)  # Scale with distance
        else:
            cmd.linear.x = 0.0  # Wait to turn first
        
        # Adjust for obstacles in local costmap
        # In practice, this would check the local costmap for obstacles in the path
        # For this example, we'll just add a simple check
        
        return cmd
    
    def quaternion_to_euler(self, quat):
        """Convert quaternion to euler angles"""
        # Convert quaternion to rotation matrix, then to euler angles
        r = R.from_quat([quat.x, quat.y, quat.z, quat.w])
        return r.as_euler('xyz')