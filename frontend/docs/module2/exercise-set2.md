---
title: 'Exercise Set 2 - The Digital Twin (Gazebo & Unity)'
description: 'Hands-on exercises for Module 2 on Gazebo and Unity integration'
---

# Exercise Set 2: The Digital Twin (Gazebo & Unity)

## Learning Objectives

After completing these exercises, you will be able to:
- Create and configure Gazebo worlds with realistic environments
- Implement sensors in simulation with realistic parameters
- Integrate Unity for advanced robot visualization
- Connect simulation environments to ROS 2 systems
- Validate simulation accuracy against real-world expectations
- Optimize simulation performance for complex scenarios

## Exercise 1: Custom Gazebo World with Obstacles

Create a Gazebo world that represents a realistic indoor environment with furniture and obstacles for robot navigation.

### Instructions

1. Create an SDF world file with the following components:
   - Room with walls (4 walls + floor + ceiling)
   - Tables, chairs, and other furniture
   - Randomly placed obstacles
   - Appropriate lighting configuration
2. Add physics parameters for realistic simulation
3. Spawn a simple robot model in the world
4. Test the world in Gazebo

### Solution

```xml
<?xml version="1.0" ?>
<sdf version="1.7">
  <world name="indoor_office">
    <!-- Include standard models -->
    <include>
      <uri>model://ground_plane</uri>
    </include>
    
    <include>
      <uri>model://sun</uri>
    </include>
    
    <!-- Room walls -->
    <!-- North wall -->
    <model name="north_wall">
      <pose>0 5 1.5 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>10 0.2 3</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>10 0.2 3</size>
            </box>
          </geometry>
          <material>
            <ambient>0.8 0.8 0.8 1</ambient>
            <diffuse>0.8 0.8 0.8 1</diffuse>
          </material>
        </visual>
        <inertial>
          <mass>1000.0</mass>
          <inertia>
            <ixx>100</ixx>
            <ixy>0</ixy>
            <ixz>0</ixz>
            <iyy>100</iyy>
            <iyz>0</iyz>
            <izz>100</izz>
          </inertia>
        </inertial>
      </link>
    </model>
    
    <!-- South wall -->
    <model name="south_wall">
      <pose>0 -5 1.5 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>10 0.2 3</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>10 0.2 3</size>
            </box>
          </geometry>
          <material>
            <ambient>0.8 0.8 0.8 1</ambient>
            <diffuse>0.8 0.8 0.8 1</diffuse>
          </material>
        </visual>
        <inertial>
          <mass>1000.0</mass>
          <inertia>
            <ixx>100</ixx>
            <ixy>0</ixy>
            <ixz>0</ixz>
            <iyy>100</iyy>
            <iyz>0</iyz>
            <izz>100</izz>
          </inertia>
        </inertial>
      </link>
    </model>
    
    <!-- West wall -->
    <model name="west_wall">
      <pose>-5 0 1.5 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>0.2 10 3</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>0.2 10 3</size>
            </box>
          </geometry>
          <material>
            <ambient>0.8 0.8 0.8 1</ambient>
            <diffuse>0.8 0.8 0.8 1</diffuse>
          </material>
        </visual>
        <inertial>
          <mass>1000.0</mass>
          <inertia>
            <ixx>100</ixx>
            <ixy>0</ixy>
            <ixz>0</ixz>
            <iyy>100</iyy>
            <iyz>0</iyz>
            <izz>100</izz>
          </inertia>
        </inertial>
      </link>
    </model>
    
    <!-- East wall -->
    <model name="east_wall">
      <pose>5 0 1.5 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>0.2 10 3</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>0.2 10 3</size>
            </box>
          </geometry>
          <material>
            <ambient>0.8 0.8 0.8 1</ambient>
            <diffuse>0.8 0.8 0.8 1</diffuse>
          </material>
        </visual>
        <inertial>
          <mass>1000.0</mass>
          <inertia>
            <ixx>100</ixx>
            <ixy>0</ixy>
            <ixz>0</ixz>
            <iyy>100</iyy>
            <iyz>0</iyz>
            <izz>100</izz>
          </inertia>
        </inertial>
      </link>
    </model>
    
    <!-- Floor -->
    <model name="floor">
      <pose>0 0 0 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>10 10 0.2</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>10 10 0.2</size>
            </box>
          </geometry>
          <material>
            <ambient>0.7 0.7 0.7 1</ambient>
            <diffuse>0.7 0.7 0.7 1</diffuse>
          </material>
        </visual>
        <inertial>
          <mass>10000.0</mass>
          <inertia>
            <ixx>1000</ixx>
            <ixy>0</ixy>
            <ixz>0</ixz>
            <iyy>1000</iyy>
            <iyz>0</iyz>
            <izz>1000</izz>
          </inertia>
        </inertial>
      </link>
    </model>
    
    <!-- Furniture: Table -->
    <model name="table">
      <pose>-2 2 0.4 0 0 0</pose>
      <link name="table_top">
        <collision name="collision">
          <geometry>
            <box>
              <size>1.0 0.6 0.05</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>1.0 0.6 0.05</size>
            </box>
          </geometry>
          <material>
            <ambient>0.5 0.3 0.1 1</ambient>
            <diffuse>0.5 0.3 0.1 1</diffuse>
          </material>
        </visual>
        <inertial>
          <mass>10.0</mass>
          <inertia>
            <ixx>1</ixx>
            <ixy>0</ixy>
            <ixz>0</ixz>
            <iyy>1</iyy>
            <iyz>0</iyz>
            <izz>1</izz>
          </inertia>
        </inertial>
      </link>
      
      <link name="leg1">
        <pose>-0.4 -0.2 0.2 0 0 0</pose>
        <collision name="collision">
          <geometry>
            <box>
              <size>0.05 0.05 0.4</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>0.05 0.05 0.4</size>
            </box>
          </geometry>
          <material>
            <ambient>0.3 0.3 0.3 1</ambient>
            <diffuse>0.3 0.3 0.3 1</diffuse>
          </material>
        </visual>
        <inertial>
          <mass>1.0</mass>
          <inertia>
            <ixx>0.01</ixx>
            <ixy>0</ixy>
            <ixz>0</ixz>
            <iyy>0.01</iyy>
            <iyz>0</iyz>
            <izz>0.01</izz>
          </inertia>
        </inertial>
      </link>
      
      <joint name="top_to_leg1" type="fixed">
        <parent>table_top</parent>
        <child>leg1</child>
        <origin xyz="-0.4 -0.2 -0.2" rpy="0 0 0"/>
      </joint>
    </model>
    
    <!-- Random obstacles -->
    <model name="box1">
      <pose>1 -1 0.5 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>0.5 0.5 1.0</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>0.5 0.5 1.0</size>
            </box>
          </geometry>
          <material>
            <ambient>0.9 0.2 0.2 1</ambient>
            <diffuse>0.9 0.2 0.2 1</diffuse>
          </material>
        </visual>
        <inertial>
          <mass>5.0</mass>
          <inertia>
            <ixx>1</ixx>
            <ixy>0</ixy>
            <ixz>0</ixz>
            <iyy>1</iyy>
            <iyz>0</iyz>
            <izz>1</izz>
          </inertia>
        </inertial>
      </link>
    </model>
    
    <model name="cylinder1">
      <pose>-1 3 0.75 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry>
            <cylinder>
              <radius>0.25</radius>
              <length>1.5</length>
            </cylinder>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <cylinder>
              <radius>0.25</radius>
              <length>1.5</length>
            </cylinder>
          </geometry>
          <material>
            <ambient>0.2 0.2 0.9 1</ambient>
            <diffuse>0.2 0.2 0.9 1</diffuse>
          </material>
        </visual>
        <inertial>
          <mass>5.0</mass>
          <inertia>
            <ixx>1</ixx>
            <ixy>0</ixy>
            <ixz>0</ixz>
            <iyy>1</iyy>
            <iyz>0</iyz>
            <izz>1</izz>
          </inertia>
        </inertial>
      </link>
    </model>
    
    <!-- Physics parameters -->
    <physics name="default_physics" type="ode">
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1</real_time_factor>
      <real_time_update_rate>1000</real_time_update_rate>
      <gravity>0 0 -9.8</gravity>
    </physics>
  </world>
</sdf>
```

To test this world:

1. Save the SDF file as `indoor_office.sdf` in your Gazebo worlds directory
2. Launch Gazebo with your world: `gazebo indoor_office.sdf`
3. Optionally, add a robot to navigate the environment

### Hints

- Use consistent units (meters for distances)
- Set appropriate masses for physical plausibility
- Consider collision detection performance when adding complex objects

## Exercise 2: Multi-Sensor Robot in Gazebo

Create a robot model with multiple sensors (LiDAR, IMU, camera) and implement sensor data processing in ROS 2.

### Instructions

1. Create a robot URDF with:
   - Differential drive base
   - LiDAR sensor (2D or 3D)
   - IMU sensor
   - RGB camera
2. Add appropriate Gazebo plugins for each sensor
3. Implement ROS 2 nodes to process each sensor's data
4. Visualize sensor data in RViz2

### Solution

First, create the robot URDF file (`multi_sensor_robot.urdf`):

```xml
<?xml version="1.0"?>
<robot name="multi_sensor_robot" xmlns:xacro="http://www.ros.org/wiki/xacro">
  
  <!-- Base link -->
  <link name="base_link">
    <inertial>
      <mass value="10.0" />
      <origin xyz="0 0 0.2" />
      <inertia 
        ixx="0.1" ixy="0.0" ixz="0.0"
        iyy="0.1" iyz="0.0"
        izz="0.1" />
    </inertial>
    
    <visual>
      <origin xyz="0 0 0.2" rpy="0 0 0" />
      <geometry>
        <box size="0.8 0.6 0.4" />
      </geometry>
      <material name="blue">
        <color rgba="0 0 1 0.8" />
      </material>
    </visual>
    
    <collision>
      <origin xyz="0 0 0.2" rpy="0 0 0" />
      <geometry>
        <box size="0.8 0.6 0.4" />
      </geometry>
    </collision>
  </link>
  
  <!-- LiDAR link -->
  <link name="laser_link">
    <inertial>
      <mass value="0.1" />
      <origin xyz="0 0 0" />
      <inertia 
        ixx="0.0001" ixy="0.0" ixz="0.0"
        iyy="0.0001" iyz="0.0"
        izz="0.0001" />
    </inertial>
    
    <visual>
      <origin xyz="0 0 0" rpy="0 0 0" />
      <geometry>
        <cylinder radius="0.05" length="0.05" />
      </geometry>
      <material name="black">
        <color rgba="0 0 0 1" />
      </material>
    </visual>
    
    <collision>
      <origin xyz="0 0 0" rpy="0 0 0" />
      <geometry>
        <cylinder radius="0.05" length="0.05" />
      </geometry>
    </collision>
  </link>
  
  <joint name="laser_joint" type="fixed">
    <parent link="base_link" />
    <child link="laser_link" />
    <origin xyz="0.3 0 0.25" rpy="0 0 0" />
  </joint>
  
  <!-- IMU link -->
  <link name="imu_link">
    <inertial>
      <mass value="0.01" />
      <origin xyz="0 0 0" />
      <inertia 
        ixx="0.000001" ixy="0.0" ixz="0.0"
        iyy="0.000001" iyz="0.0"
        izz="0.000001" />
    </inertial>
  </link>
  
  <joint name="imu_joint" type="fixed">
    <parent link="base_link" />
    <child link="imu_link" />
    <origin xyz="0 0 0.2" rpy="0 0 0" />
  </joint>
  
  <!-- Camera link -->
  <link name="camera_link">
    <inertial>
      <mass value="0.1" />
      <origin xyz="0 0 0" />
      <inertia 
        ixx="0.0001" ixy="0.0" ixz="0.0"
        iyy="0.0001" iyz="0.0"
        izz="0.0001" />
    </inertial>
    
    <visual>
      <origin xyz="0 0 0" rpy="0 0 0" />
      <geometry>
        <box size="0.05 0.1 0.05" />
      </geometry>
      <material name="red">
        <color rgba="1 0 0 1" />
      </material>
    </visual>
  </link>
  
  <joint name="camera_joint" type="fixed">
    <parent link="base_link" />
    <child link="camera_link" />
    <origin xyz="0.35 0 0.3" rpy="0 0 0" />
  </joint>
  
  <!-- Gazebo plugins -->
  <gazebo reference="base_link">
    <material>Gazebo/Blue</material>
  </gazebo>
  
  <gazebo reference="laser_link">
    <sensor name="laser_scanner" type="ray">
      <ray>
        <scan>
          <horizontal>
            <samples>720</samples>
            <resolution>1</resolution>
            <min_angle>-1.570796</min_angle>
            <max_angle>1.570796</max_angle>
          </horizontal>
        </scan>
        <range>
          <min>0.1</min>
          <max>30.0</max>
          <resolution>0.01</resolution>
        </range>
      </ray>
      <always_on>1</always_on>
      <update_rate>10</update_rate>
      <visualize>true</visualize>
      <plugin name="laser_controller" filename="libgazebo_ros_ray_sensor.so">
        <ros>
          <namespace>/laser</namespace>
          <remapping>~/out:=scan</remapping>
        </ros>
        <output_type>sensor_msgs/LaserScan</output_type>
      </plugin>
    </sensor>
  </gazebo>
  
  <gazebo reference="imu_link">
    <sensor name="imu_sensor" type="imu">
      <always_on>true</always_on>
      <update_rate>100</update_rate>
      <visualize>false</visualize>
      <topic>imu/data</topic>
      <plugin name="imu_plugin" filename="libgazebo_ros_imu.so">
        <ros>
          <namespace>/imu</namespace>
          <remapping>~/out:=data</remapping>
        </ros>
        <initial_orientation_as_reference>false</initial_orientation_as_reference>
      </plugin>
      <imu>
        <angular_velocity>
          <x>
            <noise type="gaussian">
              <mean>0.0</mean>
              <stddev>0.01</stddev>
            </noise>
          </x>
          <y>
            <noise type="gaussian">
              <mean>0.0</mean>
              <stddev>0.01</stddev>
            </noise>
          </y>
          <z>
            <noise type="gaussian">
              <mean>0.0</mean>
              <stddev>0.01</stddev>
            </noise>
          </z>
        </angular_velocity>
        <linear_acceleration>
          <x>
            <noise type="gaussian">
              <mean>0.0</mean>
              <stddev>0.017</stddev>
            </noise>
          </x>
          <y>
            <noise type="gaussian">
              <mean>0.0</mean>
              <stddev>0.017</stddev>
            </noise>
          </y>
          <z>
            <noise type="gaussian">
              <mean>0.0</mean>
              <stddev>0.017</stddev>
            </noise>
          </z>
        </linear_acceleration>
      </imu>
    </sensor>
  </gazebo>
  
  <gazebo reference="camera_link">
    <sensor name="camera" type="camera">
      <update_rate>30</update_rate>
      <camera name="head">
        <horizontal_fov>1.089</horizontal_fov>
        <image>
          <width>640</width>
          <height>480</height>
          <format>R8G8B8</format>
        </image>
        <clip>
          <near>0.1</near>
          <far>100</far>
        </clip>
      </camera>
      <plugin name="camera_controller" filename="libgazebo_ros_camera.so">
        <ros>
          <namespace>/camera</namespace>
          <remapping>image_raw:=image</remapping>
          <remapping>camera_info:=camera_info</remapping>
        </ros>
      </plugin>
    </sensor>
  </gazebo>
  
  <!-- Differential drive plugin -->
  <gazebo>
    <plugin name="diff_drive" filename="libgazebo_ros_diff_drive.so">
      <ros>
        <namespace>/cmd_vel</namespace>
      </ros>
      <update_rate>100</update_rate>
      <left_joint>left_wheel_joint</left_joint>
      <right_joint>right_wheel_joint</right_joint>
      <wheel_separation>0.4</wheel_separation>
      <wheel_diameter>0.2</wheel_diameter>
      <max_wheel_torque>20</max_wheel_torque>
      <max_wheel_acceleration>10.0</max_wheel_acceleration>
    </plugin>
  </gazebo>
  
</robot>
```

Then, create a ROS 2 node to process sensor data:

```python
# sensor_processor.py
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan, Imu, Image
from cv_bridge import CvBridge
import cv2
import numpy as np


class SensorProcessor(Node):
    def __init__(self):
        super().__init__('sensor_processor')
        self.bridge = CvBridge()
        
        # Create subscribers for all sensors
        self.lidar_subscription = self.create_subscription(
            LaserScan,
            '/laser/scan',
            self.lidar_callback,
            10
        )
        
        self.imu_subscription = self.create_subscription(
            Imu,
            '/imu/data',
            self.imu_callback,
            10
        )
        
        self.camera_subscription = self.create_subscription(
            Image,
            '/camera/image',
            self.camera_callback,
            10
        )
        
        # Track sensor status
        self.lidar_received = False
        self.imu_received = False
        self.camera_received = False
        
        # Timer to check if all sensors are working
        self.timer = self.create_timer(5.0, self.status_check)

    def lidar_callback(self, msg):
        self.get_logger().info(f'LiDAR: {len(msg.ranges)} readings, range: {msg.range_min:.2f} - {msg.range_max:.2f}m')
        self.lidar_received = True

    def imu_callback(self, msg):
        linear_acc = np.array([msg.linear_acceleration.x, msg.linear_acceleration.y, msg.linear_acceleration.z])
        angular_vel = np.array([msg.angular_velocity.x, msg.angular_velocity.y, msg.angular_velocity.z])
        
        self.get_logger().info(f'IMU: Accel={np.linalg.norm(linear_acc):.2f}, Gyro={np.linalg.norm(angular_vel):.2f}')
        self.imu_received = True

    def camera_callback(self, msg):
        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        self.get_logger().info(f'Camera: {cv_image.shape[1]}x{cv_image.shape[0]} image received')
        self.camera_received = True

    def status_check(self):
        status_msg = f"Sensors active - LiDAR: {self.lidar_received}, IMU: {self.imu_received}, Camera: {self.camera_received}"
        self.get_logger().info(status_msg)
        
        # Reset flags after reporting
        self.lidar_received = False
        self.imu_received = False
        self.camera_received = False


def main(args=None):
    rclpy.init(args=args)
    sensor_processor = SensorProcessor()
    
    try:
        rclpy.spin(sensor_processor)
    except KeyboardInterrupt:
        pass
    finally:
        sensor_processor.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### Hints

- Use appropriate noise models for realistic sensor behavior
- Match update rates to real sensor specifications
- Consider computational load when configuring multiple sensors

## Exercise 3: Unity Robot Visualization

Create a Unity scene that visualizes a robot's state based on ROS 2 messages.

### Instructions

1. Set up a Unity project with ROS 2 communication
2. Create a 3D model of a simple robot (differential drive)
3. Implement scripts to update robot pose from ROS 2 messages
4. Visualize sensor data (LiDAR, camera) in the Unity environment

### Solution

First, create a basic robot visualization script for Unity:

```csharp
// RobotVisualizer.cs
using UnityEngine;
using System.Collections.Generic;

public class RobotVisualizer : MonoBehaviour
{
    [Header("Robot Configuration")]
    public Transform baseLink;
    public Transform leftWheel;
    public Transform rightWheel;
    public Transform laserLink;
    public Transform cameraLink;
    
    [Header("Visualization")]
    public GameObject laserBeamPrefab;
    public GameObject cameraFrustum;
    
    private List<GameObject> laserBeams = new List<GameObject>();
    private int beamCount = 720;
    
    // This method would be called from ROS 2 message handling
    public void UpdateRobotPose(float x, float y, float theta)
    {
        baseLink.position = new Vector3(x, 0, y);
        baseLink.rotation = Quaternion.Euler(0, Mathf.Rad2Deg * theta, 0);
    }
    
    public void UpdateRobotWheels(float leftAngle, float rightAngle)
    {
        if(leftWheel != null)
            leftWheel.localRotation = Quaternion.Euler(leftAngle * Mathf.Rad2Deg, 0, 0);
        
        if(rightWheel != null)
            rightWheel.localRotation = Quaternion.Euler(rightAngle * Mathf.Rad2Deg, 0, 0);
    }
    
    public void UpdateLidarData(float[] ranges, float angleMin, float angleIncrement)
    {
        // Clear previous beams
        foreach(GameObject beam in laserBeams)
        {
            if(beam != null)
                GameObject.Destroy(beam);
        }
        laserBeams.Clear();
        
        // Create laser beams based on range data
        for(int i = 0; i < ranges.Length; i++)
        {
            float range = ranges[i];
            if(range > 0.05f && range < 30.0f) // Valid range
            {
                float angle = angleMin + i * angleIncrement;
                
                Vector3 start = laserLink.position;
                Vector3 direction = new Vector3(Mathf.Cos(angle), 0, Mathf.Sin(angle));
                Vector3 end = start + direction * range;
                
                GameObject beam = GameObject.Instantiate(laserBeamPrefab);
                LineRenderer lr = beam.GetComponent<LineRenderer>();
                
                if(lr != null)
                {
                    lr.SetPosition(0, start);
                    lr.SetPosition(1, end);
                }
                
                laserBeams.Add(beam);
            }
        }
    }
    
    public void UpdateCameraImage(Texture2D image)
    {
        if(cameraFrustum != null)
        {
            Renderer renderer = cameraFrustum.GetComponent<Renderer>();
            if(renderer != null)
            {
                renderer.material.mainTexture = image;
            }
        }
    }
}
```

And a simple connection handler for ROS 2:

```csharp
// ROSConnection.cs (Conceptual - actual implementation would require a Unity-ROS bridge)
using System.Collections.Generic;

public class ROSConnection
{
    private Dictionary<string, System.Action<string>> subscribers = new Dictionary<string, System.Action<string>>();
    
    public void Subscribe(string topic, System.Action<string> callback)
    {
        subscribers[topic] = callback;
    }
    
    // This would interface with the actual ROS 2 network layer
    public void Update()
    {
        // Process incoming messages here
    }
}
```

### Hints

- Use Unity's ArticulationBody for more realistic joint simulation
- Consider performance when visualizing large amounts of sensor data
- Use appropriate coordinate transformations between ROS and Unity

## Chapter Summary

These exercises provided hands-on experience with creating realistic simulation environments using Gazebo and Unity. You've learned to create complex Gazebo worlds, integrate multiple sensors in simulation, and visualize robot state in Unity. These skills are essential for developing and testing robotics algorithms in a safe, reproducible environment.

## Checklist

- [ ] Create realistic Gazebo worlds with multiple objects
- [ ] Implement multi-sensor robots in Gazebo
- [ ] Process different types of sensor data in ROS 2
- [ ] Visualize robot state in Unity
- [ ] Integrate Unity and Gazebo for comprehensive simulation
- [ ] Validate simulation accuracy

## References

- [Gazebo Tutorials](http://gazebosim.org/tutorials)
- [ROS 2 with Gazebo](https://docs.ros.org/en/humble/Tutorials/Advanced/Simulators/Gazebo.html)
- [Unity Robotics Hub](https://github.com/Unity-Technologies/ROS-Tutorials)
- [Robotics System Toolbox for MATLAB/Simulink](https://www.mathworks.com/products/robotics.html)