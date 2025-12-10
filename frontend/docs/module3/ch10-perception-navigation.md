---
title: 'Chapter 10 - Perception: VSLAM, Navigation, Object Detection'
description: 'Advanced perception techniques for robotics using visual SLAM, navigation, and object detection'
---

# Chapter 10: Perception: VSLAM, Navigation, Object Detection

## Learning Objectives

After reading this chapter, you will be able to:
- Understand the principles of Visual SLAM (VSLAM) and its role in robotics
- Implement and configure VSLAM systems for robot localization and mapping
- Set up navigation systems for path planning and obstacle avoidance
- Apply object detection techniques for scene understanding
- Integrate perception systems with robot control frameworks
- Evaluate and validate perception system performance
- Optimize perception algorithms for real-time operation

## Introduction

Perception is the cornerstone of autonomous robotics, enabling robots to understand and interact with their environment. This chapter focuses on three critical perception capabilities: Visual Simultaneous Localization and Mapping (VSLAM) for environment mapping and robot localization, navigation systems for path planning and obstacle avoidance, and object detection for scene understanding. Together, these capabilities form the foundation of a robot's ability to operate autonomously in unstructured environments.

## Visual SLAM (VSLAM) Fundamentals

### What is VSLAM?

Visual SLAM (Simultaneous Localization and Mapping) is a technique that allows robots to construct a map of an unknown environment while simultaneously determining their position within that map, using visual sensors such as cameras. Unlike traditional SLAM that relies on LiDAR, VSLAM uses visual features extracted from camera images.

### Key Components of VSLAM

1. **Feature Detection**: Identifying distinctive points in images
2. **Feature Matching**: Matching features between frames
3. **Pose Estimation**: Calculating camera/robot motion
4. **Mapping**: Building a map of the environment
5. **Loop Closure**: Detecting revisited locations to correct drift

### VSLAM Approaches

#### 1. Feature-based VSLAM
- Extracts and tracks distinctive features (corners, edges)
- Examples: ORB-SLAM, SVO, LSD-SLAM
- Advantages: Good for textured environments
- Disadvantages: Fails in textureless areas

#### 2. Direct VSLAM
- Uses pixel intensity information directly
- Examples: DTAM, LSD-SLAM
- Advantages: Works in low-texture environments
- Disadvantages: Computationally intensive, sensitive to lighting

#### 3. Semi-Direct VSLAM
- Combines feature-based and direct approaches
- Example: SVO, DSVO
- Advantages: Balances accuracy and efficiency

### Implementing ORB-SLAM in ROS 2

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from geometry_msgs.msg import PoseStamped
from cv_bridge import CvBridge
import cv2
import numpy as np
from collections import deque


class ORBSLAMNode(Node):
    def __init__(self):
        super().__init__('orb_slam_node')
        
        # Initialize CV bridge
        self.bridge = CvBridge()
        
        # Initialize ORB detector
        self.orb = cv2.ORB_create(nfeatures=2000)
        self.bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        
        # Camera parameters
        self.camera_matrix = None
        self.dist_coeffs = None
        
        # Tracking variables
        self.prev_frame = None
        self.prev_kp = None
        self.prev_desc = None
        self.position = np.array([0, 0, 0], dtype=np.float32)
        self.orientation = np.array([0, 0, 0, 1], dtype=np.float32)  # Quaternion
        
        # Map and trajectory storage
        self.map_points = {}  # 3D points in the map
        self.trajectory = deque(maxlen=1000)  # Robot trajectory
        
        # Create subscribers
        self.image_sub = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )
        
        self.camera_info_sub = self.create_subscription(
            CameraInfo,
            '/camera/camera_info',
            self.camera_info_callback,
            10
        )
        
        # Create publishers
        self.pose_pub = self.create_publisher(PoseStamped, '/orb_slam/pose', 10)
        self.trajectory_pub = self.create_publisher(Path, '/orb_slam/trajectory', 10)

    def camera_info_callback(self, msg):
        """Process camera calibration parameters"""
        if self.camera_matrix is not None:
            return  # Already initialized
            
        self.camera_matrix = np.array(msg.k).reshape(3, 3)
        self.dist_coeffs = np.array(msg.d)

    def preprocess_image(self, image):
        """Preprocess image for feature detection"""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
            
        # Apply histogram equalization for better feature detection
        gray = cv2.equalizeHist(gray)
        
        return gray

    def estimate_motion(self, curr_frame, curr_kp, curr_desc):
        """Estimate motion between current and previous frames"""
        if self.prev_desc is None:
            # First frame, no motion
            return np.eye(4, dtype=np.float32)
        
        # Match features between frames
        matches = self.bf.match(self.prev_desc, curr_desc)
        matches = sorted(matches, key=lambda x: x.distance)
        
        # Keep only good matches (top 50%)
        good_matches = matches[:len(matches)//2]
        
        if len(good_matches) < 10:
            self.get_logger().warn(f"Not enough matches: {len(good_matches)}")
            return np.eye(4, dtype=np.float32)
        
        # Extract matched keypoints
        prev_pts = np.float32([self.prev_kp[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        curr_pts = np.float32([curr_kp[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        
        # Estimate essential matrix
        E, mask = cv2.findEssentialMat(
            curr_pts, 
            prev_pts, 
            self.camera_matrix, 
            cv2.RANSAC, 
            threshold=1.0
        )
        
        if E is None or len(E) == 0:
            return np.eye(4, dtype=np.float32)
        
        # Decompose essential matrix to get rotation and translation
        _, R, t, _ = cv2.recoverPose(E, curr_pts, prev_pts, self.camera_matrix)
        
        # Create transformation matrix
        T = np.eye(4, dtype=np.float32)
        T[:3, :3] = R
        T[:3, 3] = t.flatten()
        
        return T

    def image_callback(self, msg):
        """Process incoming image and perform SLAM"""
        if self.camera_matrix is None:
            self.get_logger().warn("Camera parameters not received yet")
            return
            
        # Convert ROS image to OpenCV
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
        except Exception as e:
            self.get_logger().error(f"Failed to convert image: {e}")
            return
        
        # Preprocess image
        gray = self.preprocess_image(cv_image)
        
        # Detect and compute features
        kp = self.orb.detect(gray, None)
        kp, desc = self.orb.compute(gray, kp)
        
        if desc is None:
            self.get_logger().warn("No features found in current frame")
            return
        
        # Estimate motion
        T = self.estimate_motion(gray, kp, desc)
        
        # Update position and orientation
        self.position += T[:3, 3]
        rotation_matrix = T[:3, :3]
        # Convert rotation matrix to quaternion (simplified)
        # In practice, you'd want to properly integrate rotations
        self.orientation = self.rotation_matrix_to_quaternion(rotation_matrix)
        
        # Store current frame as previous for next iteration
        self.prev_frame = gray
        self.prev_kp = kp
        self.prev_desc = desc
        
        # Update trajectory
        self.trajectory.append(self.position.copy())
        
        # Publish pose
        pose_msg = PoseStamped()
        pose_msg.header.stamp = msg.header.stamp
        pose_msg.header.frame_id = "map"
        pose_msg.pose.position.x = float(self.position[0])
        pose_msg.pose.position.y = float(self.position[1])
        pose_msg.pose.position.z = float(self.position[2])
        pose_msg.pose.orientation.x = float(self.orientation[0])
        pose_msg.pose.orientation.y = float(self.orientation[1])
        pose_msg.pose.orientation.z = float(self.orientation[2])
        pose_msg.pose.orientation.w = float(self.orientation[3])
        
        self.pose_pub.publish(pose_msg)
        
        self.get_logger().info(f'SLAM Pose: x={self.position[0]:.2f}, y={self.position[1]:.2f}, z={self.position[2]:.2f}')

    def rotation_matrix_to_quaternion(self, R):
        """Convert rotation matrix to quaternion"""
        # This is a simplified conversion - in practice use scipy.spatial.transform.Rotation
        trace = np.trace(R)
        if trace > 0:
            s = np.sqrt(trace + 1.0) * 2  # s = 4 * qw
            qw = 0.25 * s
            qx = (R[2, 1] - R[1, 2]) / s
            qy = (R[0, 2] - R[2, 0]) / s
            qz = (R[1, 0] - R[0, 1]) / s
        else:
            if R[0, 0] > R[1, 1] and R[0, 0] > R[2, 2]:
                s = np.sqrt(1.0 + R[0, 0] - R[1, 1] - R[2, 2]) * 2
                qw = (R[2, 1] - R[1, 2]) / s
                qx = 0.25 * s
                qy = (R[0, 1] + R[1, 0]) / s
                qz = (R[0, 2] + R[2, 0]) / s
            elif R[1, 1] > R[2, 2]:
                s = np.sqrt(1.0 + R[1, 1] - R[0, 0] - R[2, 2]) * 2
                qw = (R[0, 2] - R[2, 0]) / s
                qx = (R[0, 1] + R[1, 0]) / s
                qy = 0.25 * s
                qz = (R[1, 2] + R[2, 1]) / s
            else:
                s = np.sqrt(1.0 + R[2, 2] - R[0, 0] - R[1, 1]) * 2
                qw = (R[1, 0] - R[0, 1]) / s
                qx = (R[0, 2] + R[2, 0]) / s
                qy = (R[1, 2] + R[2, 1]) / s
                qz = 0.25 * s
        
        # Normalize quaternion
        norm = np.sqrt(qw*qw + qx*qx + qy*qy + qz*qz)
        return np.array([qx/norm, qy/norm, qz/norm, qw/norm])


def main(args=None):
    rclpy.init(args=args)
    orb_slam_node = ORBSLAMNode()
    
    try:
        rclpy.spin(orb_slam_node)
    except KeyboardInterrupt:
        pass
    finally:
        orb_slam_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Navigation System Fundamentals

### Navigation Stack Architecture

The ROS navigation stack typically consists of:

1. **Global Planner**: Long-term path planning
2. **Local Planner**: Short-term obstacle avoidance
3. **Controller**: Low-level robot control
4. **Costmap**: Obstacle representation
5. **Transform System**: Coordinate frame management

### Costmap Configuration

```yaml
# costmap_common_params.yaml
map_type: costmap
origin_z: 0.0
z_resolution: 1
z_voxels: 2

obstacle_range: 2.5
raytrace_range: 3.0

publish_voxel_map: false
transform_tolerance: 0.5
meter_scoring: true

# Obstacle marking parameters
obstacle_layer:
  enabled: true
  obstacle_range: 2.5
  raytrace_range: 3.0
  inflation_radius: 0.55
  track_unknown_space: false
  combination_method: 1
  observation_sources: laser_scan
  laser_scan:
    data_type: LaserScan
    topic: /laser_scan
    marking: true
    clearing: true
    obstacle_range: 2.5
    raytrace_range: 3.0

# Inflation layer
inflation_layer:
  enabled: true
  cost_scaling_factor: 10.0
  inflation_radius: 0.55

# Static layer
static_layer:
  enabled: true
```

### Navigation Implementation

```python
import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid, Path
from geometry_msgs.msg import PoseStamped, Point
from sensor_msgs.msg import LaserScan
from tf2_ros import TransformListener, Buffer
from tf2_geometry_msgs import do_transform_pose
import tf2_py as tf2
import numpy as np
from scipy.spatial import KDTree
import math


class RobotNavigator(Node):
    def __init__(self):
        super().__init__('robot_navigator')
        
        # Initialize navigation components
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        
        # Robot state
        self.robot_pose = None
        self.laser_data = None
        self.costmap = None
        
        # Navigation targets
        self.goal = None
        self.path = None
        self.current_waypoint_index = 0
        
        # Create subscribers
        self.laser_sub = self.create_subscription(
            LaserScan,
            '/laser_scan',
            self.laser_callback,
            10
        )
        
        self.map_sub = self.create_subscription(
            OccupancyGrid,
            '/map',
            self.map_callback,
            10
        )
        
        self.goal_sub = self.create_subscription(
            PoseStamped,
            '/move_base_simple/goal',
            self.goal_callback,
            10
        )
        
        # Create publishers
        self.path_pub = self.create_publisher(Path, '/navigation/path', 10)
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # Navigation timer
        self.nav_timer = self.create_timer(0.1, self.navigation_callback)
    
    def laser_callback(self, msg):
        """Process laser scan data"""
        self.laser_data = msg
        
        # Update local costmap based on laser data
        self.update_local_costmap()
    
    def map_callback(self, msg):
        """Process map data"""
        self.costmap = msg
        self.get_logger().info("Received map with resolution: {:.2f}".format(msg.info.resolution))
    
    def goal_callback(self, msg):
        """Process navigation goal"""
        self.goal = msg.pose
        self.get_logger().info(f"Navigation goal received: ({msg.pose.position.x:.2f}, {msg.pose.position.y:.2f})")
        
        # Plan path to goal
        self.plan_path()
    
    def get_robot_pose(self):
        """Get current robot pose from TF"""
        try:
            transform = self.tf_buffer.lookup_transform(
                'map',  # target frame
                'base_link',  # source frame
                rclpy.time.Time(),  # time (0 = latest available)
                rclpy.duration.Duration(seconds=1.0)  # timeout
            )
            
            # Convert transform to pose
            pose = PoseStamped()
            pose.header.frame_id = 'map'
            pose.pose.position.x = transform.transform.translation.x
            pose.pose.position.y = transform.transform.translation.y
            pose.pose.position.z = transform.transform.translation.z
            pose.pose.orientation = transform.transform.rotation
            
            return pose, True
        except (tf2.LookupException, tf2.ConnectivityException, tf2.ExtrapolationException) as e:
            self.get_logger().warn(f"Could not get transform: {e}")
            return None, False
    
    def plan_path(self):
        """Plan path to goal using A* or other algorithm"""
        if self.costmap is None or self.goal is None:
            return
        
        # Simplified path planning using grid-based approach
        # In practice, use nav2's planners
        
        start_pose, success = self.get_robot_pose()
        if not success:
            self.get_logger().warn("Could not get robot pose for path planning")
            return
        
        # Extract map info
        width = self.costmap.info.width
        height = self.costmap.info.height
        resolution = self.costmap.info.resolution
        origin_x = self.costmap.info.origin.position.x
        origin_y = self.costmap.info.origin.position.y
        
        # Convert real-world coordinates to map grid coordinates
        start_x = int((start_pose.pose.position.x - origin_x) / resolution)
        start_y = int((start_pose.pose.position.y - origin_y) / resolution)
        goal_x = int((self.goal.position.x - origin_x) / resolution)
        goal_y = int((self.goal.position.y - origin_y) / resolution)
        
        # Check if coordinates are within map bounds
        if (0 <= start_x < width and 0 <= start_y < height and
            0 <= goal_x < width and 0 <= goal_y < height):
            
            # Simple straight-line path for demonstration
            # In practice, implement proper path planning (A*, Dijkstra, etc.)
            path = self.simple_path_planning(start_x, start_y, goal_x, goal_y)
            
            # Convert grid path back to world coordinates
            world_path = Path()
            world_path.header.frame_id = 'map'
            world_path.header.stamp = self.get_clock().now().to_msg()
            
            for grid_x, grid_y in path:
                world_x = grid_x * resolution + origin_x
                world_y = grid_y * resolution + origin_y
                
                pose = PoseStamped()
                pose.header.frame_id = 'map'
                pose.pose.position.x = world_x
                pose.pose.position.y = world_y
                pose.pose.position.z = 0.0
                pose.pose.orientation.w = 1.0  # No rotation
                
                world_path.poses.append(pose)
            
            self.path = world_path
            self.path_pub.publish(world_path)
            self.get_logger().info(f"Path planned with {len(world_path.poses)} waypoints")
        else:
            self.get_logger().warn("Goal or start pose outside map bounds")
    
    def simple_path_planning(self, start_x, start_y, goal_x, goal_y):
        """Simple grid path planning (replace with A* for real applications)"""
        path = []
        
        # Simple straight line (Manhattan distance path)
        dx = goal_x - start_x
        dy = goal_y - start_y
        
        steps = max(abs(dx), abs(dy))
        
        if steps > 0:
            x_step = dx / steps
            y_step = dy / steps
            
            for i in range(steps + 1):
                x = int(start_x + i * x_step)
                y = int(start_y + i * y_step)
                
                # Check if this cell is free (value < 50 means traversable)
                grid_index = y * self.costmap.info.width + x
                if grid_index < len(self.costmap.data) and self.costmap.data[grid_index] < 50:
                    path.append((x, y))
                else:
                    self.get_logger().warn(f"Path blocked at ({x}, {y})")
                    break  # Stop if blocked
        
        return path
    
    def navigation_callback(self):
        """Main navigation loop"""
        if self.path is None or len(self.path.poses) == 0:
            return
        
        # Get current robot pose
        robot_pose, success = self.get_robot_pose()
        if not success:
            return
        
        # Determine next waypoint
        if self.current_waypoint_index < len(self.path.poses):
            target_pose = self.path.poses[self.current_waypoint_index]
            
            # Calculate distance to waypoint
            dx = target_pose.pose.position.x - robot_pose.pose.position.x
            dy = target_pose.pose.position.y - robot_pose.pose.position.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            # Check if close enough to current waypoint
            if distance < 0.5:  # 50cm threshold
                self.current_waypoint_index += 1
                if self.current_waypoint_index >= len(self.path.poses):
                    self.get_logger().info("Reached goal!")
                    return  # Reached goal
            
            # If still have waypoints, navigate to next one
            if self.current_waypoint_index < len(self.path.poses):
                self.navigate_to_waypoint(robot_pose, target_pose.pose)
    
    def navigate_to_waypoint(self, robot_pose, target_pose):
        """Navigate to a specific waypoint"""
        # Calculate direction to target
        dx = target_pose.position.x - robot_pose.pose.position.x
        dy = target_pose.position.y - robot_pose.pose.position.y
        
        # Calculate target angle
        target_angle = math.atan2(dy, dx)
        
        # Get robot's current orientation
        current_angle = self.get_yaw(robot_pose.pose.orientation)
        
        # Calculate angle difference
        angle_diff = target_angle - current_angle
        
        # Normalize angle difference
        while angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        while angle_diff < -math.pi:
            angle_diff += 2 * math.pi
        
        # Create velocity command
        twist = Twist()
        
        # PID-like control for rotation
        if abs(angle_diff) > 0.1:  # 0.1 rad = ~5.7 degrees
            twist.angular.z = 0.5 * angle_diff  # Rotate toward target
        else:
            # Move forward
            dist_to_target = math.sqrt(dx*dx + dy*dy)
            twist.linear.x = min(0.5, dist_to_target)  # Cap speed
            twist.angular.z = 0.0  # No rotation needed
        
        # Check for obstacles using laser data
        if self.laser_data and self.avoid_obstacles():
            # Emergency stop or obstacle avoidance
            twist.linear.x = 0.0
            twist.angular.z = 0.3  # Turn to avoid obstacle
        
        # Publish command
        self.cmd_pub.publish(twist)
    
    def avoid_obstacles(self):
        """Check laser data for obstacles and return True if obstacle detected"""
        if self.laser_data is None:
            return False
        
        # Check for obstacles within 1m in front of robot
        min_distance = float('inf')
        
        # Look at front 30-degree sector
        start_idx = int(len(self.laser_data.ranges) * 0.45)  # 135 deg / 360 deg
        end_idx = int(len(self.laser_data.ranges) * 0.55)    # 180 deg / 360 deg
        
        for i in range(start_idx, end_idx):
            if i < len(self.laser_data.ranges) and self.laser_data.ranges[i] < min_distance:
                min_distance = self.laser_data.ranges[i]
        
        # Return True if obstacle is close
        return min_distance < 0.8
    
    def get_yaw(self, quaternion):
        """Extract yaw angle from quaternion"""
        siny_cosp = 2 * (quaternion.w * quaternion.z + quaternion.x * quaternion.y)
        cosy_cosp = 1 - 2 * (quaternion.y * quaternion.y + quaternion.z * quaternion.z)
        return math.atan2(siny_cosp, cosy_cosp)


def main(args=None):
    rclpy.init(args=args)
    navigator = RobotNavigator()
    
    try:
        rclpy.spin(navigator)
    except KeyboardInterrupt:
        pass
    finally:
        navigator.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Object Detection for Robotics

### Object Detection Fundamentals

Object detection in robotics involves identifying and localizing objects in the robot's environment. Common approaches include:

1. **Traditional Computer Vision**: Feature-based detection (Haar cascades, HOG)
2. **Deep Learning**: CNN-based detection (YOLO, SSD, Faster R-CNN)
3. **3D Detection**: Combining depth and RGB data for 3D object localization

### Deep Learning Object Detection

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from vision_msgs.msg import Detection2DArray, Detection2D, ObjectHypothesisWithPose
from cv_bridge import CvBridge
import cv2
import numpy as np


class ObjectDetectionNode(Node):
    def __init__(self):
        super().__init__('object_detection')
        
        # Initialize CV bridge
        self.bridge = CvBridge()
        
        # Load YOLO model
        self.model_config = '/path/to/yolov4.cfg'
        self.model_weights = '/path/to/yolov4.weights'
        self.model_classes = '/path/to/coco.names'
        
        try:
            self.net = cv2.dnn.readNet(self.model_weights, self.model_config)
            self.layer_names = self.net.getLayerNames()
            self.output_layers = [self.layer_names[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]
            
            # Load class names
            with open(self.model_classes, 'r') as f:
                self.classes = [line.strip() for line in f.readlines()]
                
            self.get_logger().info(f"Loaded YOLO model with {len(self.classes)} classes")
        except Exception as e:
            self.get_logger().error(f"Failed to load YOLO model: {e}")
            self.net = None
        
        # Camera info
        self.camera_matrix = None
        self.dist_coeffs = None
        
        # Subscribers and publishers
        self.image_sub = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )
        
        self.camera_info_sub = self.create_subscription(
            CameraInfo,
            '/camera/camera_info',
            self.camera_info_callback,
            10
        )
        
        self.detection_pub = self.create_publisher(Detection2DArray, '/object_detections', 10)
    
    def camera_info_callback(self, msg):
        """Process camera calibration parameters"""
        self.camera_matrix = np.array(msg.k).reshape(3, 3)
        self.dist_coeffs = np.array(msg.d)
    
    def detect_objects(self, image):
        """Perform object detection on image"""
        if self.net is None:
            return []
        
        height, width, channels = image.shape
        
        # Prepare image for detection
        blob = cv2.dnn.blobFromImage(image, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        self.net.setInput(blob)
        outs = self.net.forward(self.output_layers)
        
        # Process detection results
        class_ids = []
        confidences = []
        boxes = []
        
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                
                if confidence > 0.5:  # Confidence threshold
                    # Object found
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    
                    # Rectangle coordinates
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)
        
        # Apply non-maximum suppression to eliminate duplicate detections
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
        
        detections = []
        if len(indexes) > 0:
            for i in indexes.flatten():
                x, y, w, h = boxes[i]
                
                # Create detection message
                detection = Detection2D()
                detection.header.stamp = self.get_clock().now().to_msg()
                detection.header.frame_id = 'camera_link'  # Assuming camera frame
                
                # Bounding box in image coordinates
                detection.bbox.center.x = x + w/2
                detection.bbox.center.y = y + h/2
                detection.bbox.size_x = w
                detection.bbox.size_y = h
                
                # Object classification
                hypothesis = ObjectHypothesisWithPose()
                hypothesis.id = str(class_ids[i])
                hypothesis.score = confidences[i]
                # In a real implementation, you'd also include 3D pose estimation
                detection.results.append(hypothesis)
                
                detections.append(detection)
        
        return detections
    
    def image_callback(self, msg):
        """Process incoming image for object detection"""
        if self.net is None:
            return
        
        try:
            # Convert ROS image to OpenCV
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f"Failed to convert image: {e}")
            return
        
        # Perform object detection
        detections = self.detect_objects(cv_image)
        
        # Create and publish detection array
        detection_array = Detection2DArray()
        detection_array.header = msg.header
        detection_array.detections = detections
        
        self.detection_pub.publish(detection_array)
        
        # Log detection results
        if detections:
            for detection in detections:
                class_id = int(detection.results[0].id)
                confidence = detection.results[0].score
                class_name = self.classes[class_id] if class_id < len(self.classes) else "unknown"
                self.get_logger().info(f"Detected {class_name} with confidence {confidence:.2f}")
    
    def get_3d_position(self, bbox_2d, depth_image):
        """Estimate 3D position of detected object using depth information"""
        # Extract bounding box center
        center_x = int(bbox_2d.center.x)
        center_y = int(bbox_2d.center.y)
        
        # Get depth at center of bounding box
        if center_y < depth_image.shape[0] and center_x < depth_image.shape[1]:
            depth = depth_image[center_y, center_x]
            
            if depth > 0:  # Valid depth
                # Convert 2D pixel coordinate to 3D world coordinate
                # This requires camera intrinsic parameters
                x_3d = (center_x - self.camera_matrix[0, 2]) * depth / self.camera_matrix[0, 0]
                y_3d = (center_y - self.camera_matrix[1, 2]) * depth / self.camera_matrix[1, 1]
                
                return np.array([x_3d, y_3d, depth])
        
        return None


def main(args=None):
    rclpy.init(args=args)
    detection_node = ObjectDetectionNode()
    
    try:
        rclpy.spin(detection_node)
    except KeyboardInterrupt:
        pass
    finally:
        detection_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Perception System Integration

### Sensor Fusion for Robust Perception

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, LaserScan, PointCloud2, CameraInfo
from geometry_msgs.msg import PoseStamped
from visualization_msgs.msg import MarkerArray, Marker
from tf2_ros import TransformListener, Buffer
import numpy as np
import cv2
from scipy.spatial.transform import Rotation as R


class IntegratedPerceptionNode(Node):
    def __init__(self):
        super().__init__('integrated_perception')
        
        # Initialize perception components
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        
        # Sensor data storage
        self.image = None
        self.depth_image = None
        self.laser_data = None
        self.camera_info = None
        
        # Object tracking
        self.tracked_objects = {}
        self.next_object_id = 0
        
        # Subscribers
        self.image_sub = self.create_subscription(Image, '/camera/rgb/image_raw', self.image_callback, 10)
        self.depth_sub = self.create_subscription(Image, '/camera/depth/image_raw', self.depth_callback, 10)
        self.laser_sub = self.create_subscription(LaserScan, '/laser_scan', self.laser_callback, 10)
        self.camera_info_sub = self.create_subscription(CameraInfo, '/camera/rgb/camera_info', self.camera_info_callback, 10)
        self.detection_sub = self.create_subscription(Detection2DArray, '/object_detections', self.detection_callback, 10)
        
        # Publishers
        self.marker_pub = self.create_publisher(MarkerArray, '/perception/markers', 10)
        self.fused_objects_pub = self.create_publisher(MarkerArray, '/perception/fused_objects', 10)
        
        # Timer for processing
        self.process_timer = self.create_timer(0.1, self.process_perception)
    
    def image_callback(self, msg):
        """Handle RGB image"""
        try:
            self.image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f"Error processing image: {e}")
    
    def depth_callback(self, msg):
        """Handle depth image"""
        try:
            self.depth_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
        except Exception as e:
            self.get_logger().error(f"Error processing depth image: {e}")
    
    def laser_callback(self, msg):
        """Handle laser scan"""
        self.laser_data = msg
    
    def camera_info_callback(self, msg):
        """Handle camera info"""
        self.camera_info = msg
    
    def detection_callback(self, msg):
        """Handle object detections from neural network"""
        # Integrate with existing tracking
        for detection in msg.detections:
            # Convert 2D detection to 3D using depth
            if self.depth_image is not None and self.camera_info is not None:
                # Get 3D position
                center_x = int(detection.bbox.center.x)
                center_y = int(detection.bbox.center.y)
                
                # Get depth at detection center
                depth = self.depth_image[center_y, center_x] if (center_y < self.depth_image.shape[0] and 
                                                               center_x < self.depth_image.shape[1]) else 0
                
                if depth > 0:
                    # Convert to 3D using camera parameters
                    fx = self.camera_info.k[0]  # Focal length x
                    fy = self.camera_info.k[4]  # Focal length y
                    cx = self.camera_info.k[2]  # Principal point x
                    cy = self.camera_info.k[5]  # Principal point y
                    
                    x_3d = (center_x - cx) * depth / fx
                    y_3d = (center_y - cy) * depth / fy
                    z_3d = depth
                    
                    # Create 3D object
                    obj_3d = {
                        'position': np.array([x_3d, y_3d, z_3d]),
                        'bbox': detection.bbox,
                        'class': detection.results[0].id,
                        'confidence': detection.results[0].score,
                        'timestamp': msg.header.stamp
                    }
                    
                    # Update tracked objects
                    self.update_tracked_objects(obj_3d)
    
    def update_tracked_objects(self, new_object):
        """Update tracked objects with new detection"""
        # Simple tracking by finding closest existing object
        min_distance = float('inf')
        closest_id = None
        
        for obj_id, tracked_obj in self.tracked_objects.items():
            # Calculate distance to new detection
            pos1 = tracked_obj['position']
            pos2 = new_object['position']
            distance = np.linalg.norm(pos1 - pos2)
            
            if distance < min_distance and distance < 0.5:  # Threshold for association
                min_distance = distance
                closest_id = obj_id
        
        if closest_id is not None:
            # Update existing object
            self.tracked_objects[closest_id]['position'] = new_object['position']
            self.tracked_objects[closest_id]['last_detection'] = self.get_clock().now()
        else:
            # Create new tracked object
            self.tracked_objects[self.next_object_id] = {
                'id': self.next_object_id,
                'position': new_object['position'],
                'class': new_object['class'],
                'confidence': new_object['confidence'],
                'last_detection': self.get_clock().now()
            }
            self.next_object_id += 1
    
    def process_perception(self):
        """Main perception processing loop"""
        # Publish visualization markers
        self.publish_markers()
    
    def publish_markers(self):
        """Publish visualization markers for detected objects"""
        marker_array = MarkerArray()
        
        for obj_id, obj in self.tracked_objects.items():
            # Object marker
            marker = Marker()
            marker.header.frame_id = 'base_link'  # Or appropriate frame
            marker.header.stamp = self.get_clock().now().to_msg()
            marker.ns = 'objects'
            marker.id = obj_id
            marker.type = Marker.SPHERE
            marker.action = Marker.ADD
            
            marker.pose.position.x = float(obj['position'][0])
            marker.pose.position.y = float(obj['position'][1])
            marker.pose.position.z = float(obj['position'][2])
            marker.pose.orientation.w = 1.0
            
            marker.scale.x = 0.2  # Sphere diameter
            marker.scale.y = 0.2
            marker.scale.z = 0.2
            
            # Color based on object class
            if obj['class'] == '0':  # Person
                marker.color.r = 1.0
                marker.color.g = 0.0
                marker.color.b = 0.0
            elif obj['class'] == '1':  # Chair
                marker.color.r = 0.0
                marker.color.g = 1.0
                marker.color.b = 0.0
            else:  # Other
                marker.color.r = 0.0
                marker.color.g = 0.0
                marker.color.b = 1.0
            
            marker.color.a = 0.7  # Alpha
            
            marker_array.markers.append(marker)
        
        self.fused_objects_pub.publish(marker_array)


def main(args=None):
    rclpy.init(args=args)
    perception_node = IntegratedPerceptionNode()
    
    try:
        rclpy.spin(perception_node)
    except KeyboardInterrupt:
        pass
    finally:
        perception_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Performance Evaluation and Validation

### Accuracy Metrics

For evaluating perception systems, consider:

1. **VSLAM**: Drift, map accuracy, feature tracking quality
2. **Navigation**: Path optimality, obstacle avoidance, goal reaching success
3. **Object Detection**: Precision, recall, mAP (mean Average Precision)

### Validation Framework

```python
# perception_validator.py
import numpy as np
from scipy.spatial.distance import cdist


class PerceptionValidator:
    def __init__(self):
        self.ground_truth_poses = []
        self.estimated_poses = []
        self.detection_results = []
        self.ground_truth_detections = []
    
    def validate_vslam(self, estimated_trajectory, ground_truth_trajectory):
        """Validate VSLAM accuracy"""
        if len(estimated_trajectory) != len(ground_truth_trajectory):
            self.get_logger().warn("Trajectory lengths don't match")
            return None
        
        errors = []
        for est, gt in zip(estimated_trajectory, ground_truth_trajectory):
            position_error = np.linalg.norm(est[:3] - gt[:3])
            errors.append(position_error)
        
        rmse = np.sqrt(np.mean(np.square(errors)))
        max_error = np.max(errors)
        mean_error = np.mean(errors)
        
        return {
            'rmse': rmse,
            'max_error': max_error,
            'mean_error': mean_error,
            'std_error': np.std(errors)
        }
    
    def validate_detection(self, detections, ground_truths, iou_threshold=0.5):
        """Validate object detection performance"""
        # Calculate IoU for each detection-ground truth pair
        ious = np.zeros((len(detections), len(ground_truths)))
        
        for i, det in enumerate(detections):
            for j, gt in enumerate(ground_truths):
                ious[i, j] = self.calculate_iou(det, gt)
        
        # Find valid matches (IoU > threshold)
        matches = np.where(ious >= iou_threshold)
        
        # Calculate precision and recall
        true_positives = len(matches[0])
        false_positives = len(detections) - true_positives
        false_negatives = len(ground_truths) - true_positives
        
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score,
            'true_positives': true_positives,
            'false_positives': false_positives,
            'false_negatives': false_negatives
        }
    
    def calculate_iou(self, box1, box2):
        """Calculate Intersection over Union for two bounding boxes"""
        # Box format: [x1, y1, x2, y2]
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])
        
        # Calculate intersection area
        intersection_area = max(0, x2 - x1) * max(0, y2 - y1)
        
        # Calculate union area
        box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
        box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
        union_area = box1_area + box2_area - intersection_area
        
        # Calculate IoU
        iou = intersection_area / union_area if union_area > 0 else 0
        return iou


# Example usage
validator = PerceptionValidator()
vslam_metrics = validator.validate_vslam(estimated_path, ground_truth_path)
print(f"VSLAM RMSE: {vslam_metrics['rmse']:.2f}m")

detection_metrics = validator.validate_detection(detections, ground_truths)
print(f"Detection Precision: {detection_metrics['precision']:.2f}, Recall: {detection_metrics['recall']:.2f}")
```

## Chapter Summary

This chapter covered advanced perception techniques for robotics, including Visual SLAM for environment mapping and robot localization, navigation systems for path planning and obstacle avoidance, and object detection for scene understanding. We explored implementation details for each component, showed how they can be integrated, and discussed validation approaches. These perception capabilities are crucial for building autonomous robots that can operate in unstructured environments.

## Checklist

- [ ] Implement VSLAM system for robot localization and mapping
- [ ] Set up navigation system with global and local planners
- [ ] Apply object detection for environment understanding
- [ ] Integrate perception components into unified framework
- [ ] Validate perception system performance with appropriate metrics
- [ ] Optimize algorithms for real-time operation

## Exercises

### Exercise 1: VSLAM Implementation

Implement a simple VSLAM system that can map a room and localize the robot within it.

#### Solution

1. Set up camera and IMU sensors in your robot
2. Implement feature detection and tracking
3. Create map of environment features
4. Estimate robot pose relative to map
5. Test with known trajectory

#### Hints

- Start with a simple scene (few distinctive features)
- Use ORB features for robust detection
- Implement loop closure detection to reduce drift

### Exercise 2: Object Detection Integration

Integrate object detection with robot navigation to avoid detected obstacles.

#### Solution

1. Set up camera and run object detection
2. Identify obstacles in the environment
3. Update costmap with detected obstacles
4. Replan navigation path to avoid obstacles
5. Test in simulation and real environment

#### Hints

- Consider false positives in your obstacle avoidance logic
- Fuse 2D detections with depth information for 3D positions
- Ensure real-time performance for navigation

## References

- [Visual SLAM Review: State of the Art and Future Challenges](https://arxiv.org/abs/1606.05830)
- [ROS Navigation Stack Tutorials](http://wiki.ros.org/navigation/Tutorials)
- [YOLO: Real-Time Object Detection](https://pjreddie.com/darknet/yolo/)
- [Computer Vision Metrics by Scott Krig](https://link.springer.com/book/10.1007/978-1-4302-5930-5)