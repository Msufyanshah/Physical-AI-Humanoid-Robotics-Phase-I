---
title: 'Exercise Set 2 - The Digital Twin (Gazebo & Unity)'
description: 'Hands-on exercises for Module 2 covering simulation environments'
---

# Exercise Set 2: The Digital Twin (Gazebo & Unity)

## Learning Objectives

After completing these exercises, you will be able to:
- Configure realistic Gazebo simulation environments for humanoid robots
- Implement Unity visualization for robot systems
- Simulate and validate various sensor types (LiDAR, IMU, cameras)
- Integrate Unity with ROS 2 communication systems
- Optimize simulation performance and accuracy
- Create interactive interfaces for robot control
- Test and validate simulation-to-reality transfer

## Exercise 1: Complete Gazebo World with Physics and Sensors

Create a complete indoor environment with realistic physics and sensor configurations for humanoid robot testing.

### Instructions

1. Create a Gazebo world file with:
   - Indoor environment with doors, furniture, and obstacles
   - Realistic physics parameters for humanoid locomotion
   - Multiple sensor types (LiDAR, IMU, camera) properly mounted on the robot
   - Appropriate lighting and visual properties

2. Configure the humanoid robot model with:
   - Proper mass distribution and inertial parameters
   - Joint limits matching the real robot
   - Sensor placement realistic to the robot design
   - Collision and visual properties

3. Test the simulation to ensure:
   - Physics behaves realistically
   - Sensors provide meaningful data
   - Robot can navigate and interact safely

### Solution

#### 1. Complete world description (my_humanoid_world.sdf)

```xml
<?xml version="1.0"?>
<sdf version="1.7">
  <world name="humanoid_indoor_world">
    <!-- Include standard models -->
    <include>
      <uri>model://ground_plane</uri>
    </include>
    
    <include>
      <uri>model://sun</uri>
    </include>
    
    <!-- Physics engine configuration -->
    <physics name="humanoid_physics" type="ode">
      <max_step_size>0.001</max_step_size>  <!-- High fidelity for balance -->
      <real_time_factor>1</real_time_factor>
      <real_time_update_rate>1000</real_time_update_rate>
      <gravity>0 0 -9.8</gravity>
      
      <ode>
        <solver>
          <type>quick</type>
          <iters>200</iters>  <!-- More iterations for stability -->
          <sor>1.2</sor>
        </solver>
        <constraints>
          <cfm>0.000001</cfm>  <!-- Constraint force mixing -->
          <erp>0.1</erp>      <!-- Error reduction parameter -->
          <contact_max_correcting_vel>100.0</contact_max_correcting_vel>
          <contact_surface_layer>0.001</contact_surface_layer>
        </constraints>
      </ode>
    </physics>
    
    <!-- Indoor environment -->
    <!-- Outer walls -->
    <model name="outer_walls">
      <pose>0 0 1.5 0 0 0</pose>
      <static>true</static>
      <link name="walls_link">
        <collision name="north_wall_collision">
          <pose>0 4 1.5 0 0 0</pose>
          <geometry>
            <box><size>8 0.1 3</size></box>
          </geometry>
        </collision>
        <collision name="south_wall_collision">
          <pose>0 -4 1.5 0 0 0</pose>
          <geometry>
            <box><size>8 0.1 3</size></box>
          </geometry>
        </collision>
        <collision name="east_wall_collision">
          <pose>4 0 1.5 0 0 1.5707</pose>
          <geometry>
            <box><size>8 0.1 3</size></box>
          </geometry>
        </collision>
        <collision name="west_wall_collision">
          <pose>-4 0 1.5 0 0 1.5707</pose>
          <geometry>
            <box><size>8 0.1 3</size></box>
          </geometry>
        </collision>
        
        <visual name="north_wall_visual">
          <pose>0 4 1.5 0 0 0</pose>
          <geometry>
            <box><size>8 0.1 3</size></box>
          </geometry>
          <material>
            <ambient>0.8 0.8 0.8 1</ambient>
            <diffuse>0.8 0.8 0.8 1</diffuse>
          </material>
        </visual>
        <visual name="south_wall_visual">
          <pose>0 -4 1.5 0 0 0</pose>
          <geometry>
            <box><size>8 0.1 3</size></box>
          </geometry>
          <material>
            <ambient>0.8 0.8 0.8 1</ambient>
            <diffuse>0.8 0.8 0.8 1</diffuse>
          </material>
        </visual>
        <visual name="east_wall_visual">
          <pose>4 0 1.5 0 0 1.5707</pose>
          <geometry>
            <box><size>8 0.1 3</size></box>
          </geometry>
          <material>
            <ambient>0.8 0.8 0.8 1</ambient>
            <diffuse>0.8 0.8 0.8 1</diffuse>
          </material>
        </visual>
        <visual name="west_wall_visual">
          <pose>-4 0 1.5 0 0 1.5707</pose>
          <geometry>
            <box><size>8 0.1 3</size></box>
          </geometry>
          <material>
            <ambient>0.8 0.8 0.8 1</ambient>
            <diffuse>0.8 0.8 0.8 1</diffuse>
          </material>
        </visual>
        
        <inertial>
          <mass>10000.0</mass>
          <inertia>
            <ixx>1e9</ixx>
            <ixy>0</ixy>
            <ixz>0</ixz>
            <iyy>1e9</iyy>
            <iyz>0</iyz>
            <izz>1e9</izz>
          </inertia>
        </inertial>
      </link>
    </model>
    
    <!-- Doorway obstacle -->
    <model name="doorway">
      <pose>0 0 0.7 0 0 0</pose>
      <static>true</static>
      <link name="frame">
        <collision name="collision">
          <geometry>
            <box><size>0.2 3 1.4</size></box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box><size>0.2 3 1.4</size></box>
          </geometry>
          <material>
            <ambient>0.4 0.2 0.0 1</ambient>
            <diffuse>0.4 0.2 0.0 1</diffuse>
          </material>
        </visual>
        <inertial>
          <mass>100.0</mass>
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
    
    <!-- Furniture -->
    <!-- Table with objects -->
    <model name="table_with_objects">
      <pose>-2 2 0 0 0 0</pose>
      <static>true</static>
      
      <!-- Table -->
      <link name="table_top">
        <collision name="collision">
          <geometry>
            <box><size>1.0 0.6 0.05</size></box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box><size>1.0 0.6 0.05</size></box>
          </geometry>
          <material>
            <ambient>0.6 0.4 0.2 1</ambient>
            <diffuse>0.6 0.4 0.2 1</diffuse>
          </material>
        </visual>
        <inertial>
          <mass>10.0</mass>
          <inertia>
            <ixx>0.5</ixx>
            <ixy>0</ixy>
            <ixz>0</ixz>
            <iyy>0.5</iyy>
            <iyz>0</iyz>
            <izz>0.5</izz>
          </inertia>
        </inertial>
      </link>
      
      <!-- Table legs -->
      <link name="leg1">
        <pose>-0.4 -0.25 0.4 0 0 0</pose>
        <collision name="collision">
          <geometry>
            <cylinder><radius>0.03</radius><length>0.8</length></cylinder>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <cylinder><radius>0.03</radius><length>0.8</length></cylinder>
          </geometry>
          <material>
            <ambient>0.5 0.5 0.5 1</ambient>
            <diffuse>0.5 0.5 0.5 1</diffuse>
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
            <izz>0.001</izz>
          </inertia>
        </inertial>
      </link>
      <!-- Add more legs similarly -->
      
      <!-- Joint connecting leg to table -->
      <joint name="table_leg1_joint" type="fixed">
        <parent>table_top</parent>
        <child>leg1</child>
        <pose>-0.4 -0.25 -0.4 0 0 0</pose>
      </joint>
      
      <!-- Objects on table -->
      <model name="book">
        <pose>-2.2 2.1 0.4 0 0 0.5</pose>
        <link name="book_link">
          <collision name="collision">
            <geometry>
              <box><size>0.2 0.15 0.02</size></box>
            </geometry>
          </collision>
          <visual name="visual">
            <geometry>
              <box><size>0.2 0.15 0.02</size></box>
            </geometry>
            <material>
              <ambient>1 0.8 0.8 1</ambient>
              <diffuse>1 0.8 0.8 1</diffuse>
            </material>
          </visual>
          <inertial>
            <mass>0.2</mass>
            <inertia>
              <ixx>0.001</ixx>
              <ixy>0</ixy>
              <ixz>0</ixz>
              <iyy>0.001</iyy>
              <iyz>0</iyz>
              <izz>0.001</izz>
          </inertia>
        </link>
      </model>
      
      <model name="cup">
        <pose>-1.8 1.9 0.4 0 0 0</pose>
        <link name="cup_link">
          <collision name="collision">
            <geometry>
              <cylinder><radius>0.04</radius><length>0.1</length></cylinder>
            </geometry>
          </collision>
          <visual name="visual">
            <geometry>
              <cylinder><radius>0.04</radius><length>0.1</length></cylinder>
            </geometry>
            <material>
              <ambient>0.8 0.8 1 1</ambient>
              <diffuse>0.8 0.8 1 1</diffuse>
            </material>
          </visual>
          <inertial>
            <mass>0.1</mass>
            <inertia>
              <ixx>0.0001</ixx>
              <ixy>0</ixy>
              <ixz>0</ixz>
              <iyy>0.0001</iyy>
              <iyz>0</iyz>
              <izz>0.0002</izz>
            </inertia>
          </inertial>
        </link>
      </model>
    </model>
    
    <!-- Lighting -->
    <light name="overhead_light" type="point">
      <pose>0 0 3 0 0 0</pose>
      <diffuse>0.8 0.8 0.8 1</diffuse>
      <specular>0.8 0.8 0.8 1</specular>
      <attenuation>
        <range>10</range>
        <constant>0.5</constant>
        <linear>0.1</linear>
        <quadratic>0.05</quadratic>
      </attenuation>
    </light>
  </world>
</sdf>
```

#### 2. Robot model with sensors (humanoid_robot.sdf)

```xml
<?xml version="1.0"?>
<sdf version="1.7">
  <model name="humanoid_robot_advanced">
    <pose>0 0 0.85 0 0 0</pose>  <!-- Start at appropriate height for humanoid -->
    
    <!-- Base link (pelvis/torso) -->
    <link name="base_link">
      <pose>0 0 0.85 0 0 0</pose>
      <inertial>
        <mass>10.0</mass>
        <pose>0 0 0 0 0 0</pose>
        <inertia>
          <ixx>0.8</ixx>
          <ixy>0</ixy>
          <ixz>0</ixz>
          <iyy>0.8</iyy>
          <iyz>0</iyz>
          <izz>0.5</izz>
        </inertia>
      </inertial>
      
      <collision name="base_collision">
        <pose>0 0 0 0 0 0</pose>
        <geometry>
          <box><size>0.3 0.25 0.4</size></box>
        </geometry>
      </collision>
      
      <visual name="base_visual">
        <pose>0 0 0 0 0 0</pose>
        <geometry>
          <box><size>0.3 0.25 0.4</size></box>
        </geometry>
        <material>
          <ambient>0.5 0.5 1.0 1</ambient>
          <diffuse>0.5 0.5 1.0 1</diffuse>
        </material>
      </visual>
    </link>
    
    <!-- Torso -->
    <link name="torso">
      <pose>0 0 0.25 0 0 0</pose>
      <inertial>
        <mass>5.0</mass>
        <pose>0 0 0.15 0 0 0</pose>
        <inertia>
          <ixx>0.3</ixx>
          <ixy>0</ixy>
          <ixz>0</ixz>
          <iyy>0.3</iyy>
          <iyz>0</iyz>
          <izz>0.2</izz>
        </inertia>
      </inertial>
      
      <collision name="torso_collision">
        <pose>0 0 0.15 0 0 0</pose>
        <geometry>
          <box><size>0.25 0.2 0.3</size></box>
        </geometry>
      </collision>
      
      <visual name="torso_visual">
        <pose>0 0 0.15 0 0 0</pose>
        <geometry>
          <box><size>0.25 0.2 0.3</size></box>
        </geometry>
        <material>
          <ambient>0.7 0.7 1.0 1</ambient>
          <diffuse>0.7 0.7 1.0 1</diffuse>
        </material>
      </visual>
    </link>
    
    <joint name="torso_joint" type="fixed">
      <parent>base_link</parent>
      <child>torso</child>
      <pose>0 0 0.25 0 0 0</pose>
    </joint>
    
    <!-- Head with sensors -->
    <link name="head">
      <pose>0 0 0.3 0 0 0</pose>
      <inertial>
        <mass>2.0</mass>
        <pose>0 0 0.05 0 0 0</pose>
        <inertia>
          <ixx>0.02</ixx>
          <ixy>0</ixy>
          <ixz>0</ixz>
          <iyy>0.02</iyy>
          <iyz>0</iyz>
          <izz>0.02</izz>
        </inertia>
      </inertial>
      
      <collision name="head_collision">
        <geometry>
          <sphere><radius>0.1</radius></sphere>
        </geometry>
      </collision>
      
      <visual name="head_visual">
        <geometry>
          <sphere><radius>0.1</radius></sphere>
        </geometry>
        <material>
          <ambient>0.9 0.9 0.9 1</ambient>
          <diffuse>0.9 0.9 0.9 1</diffuse>
        </material>
      </visual>
    </link>
    
    <joint name="neck_joint" type="revolute">
      <parent>torso</parent>
      <child>head</child>
      <pose>0 0 0.45 0 0 0</pose>
      <axis>
        <xyz>0 1 0</xyz>
        <limit>
          <lower>-0.785</lower>  <!-- -45 degrees -->
          <upper>0.785</upper>   <!-- 45 degrees -->
          <effort>20</effort>
          <velocity>1.0</velocity>
        </limit>
        <dynamics>
          <damping>1.0</damping>
          <friction>0.1</friction>
        </dynamics>
      </axis>
    </joint>
    
    <!-- Camera sensor in head -->
    <sensor name="head_camera" type="camera">
      <pose>0.1 0 0.05 0 0 0</pose>
      <camera name="head_camera">
        <horizontal_fov>1.047</horizontal_fov>  <!-- 60 degrees -->
        <image>
          <width>640</width>
          <height>480</height>
          <format>R8G8B8</format>
        </image>
        <clip>
          <near>0.1</near>
          <far>10</far>
        </clip>
      </camera>
      <always_on>true</always_on>
      <update_rate>30</update_rate>
      <visualize>true</visualize>
      
      <plugin name="camera_controller" filename="libgazebo_ros_camera.so">
        <ros>
          <namespace>/camera</namespace>
          <remapping>~/image_raw:=image</remapping>
          <remapping>~/camera_info:=camera_info</remapping>
        </ros>
        <frame_name>head_camera_frame</frame_name>
        <topic_name>image</topic_name>
      </plugin>
    </sensor>
    
    <!-- IMU in torso -->
    <sensor name="imu_sensor" type="imu">
      <pose>0 0 0.1 0 0 0</pose>
      <always_on>true</always_on>
      <update_rate>100</update_rate>
      <imu>
        <angular_velocity>
          <x>
            <noise type="gaussian">
              <mean>0.0</mean>
              <stddev>0.02</stddev>
              <bias_mean>0.0</bias_mean>
              <bias_stddev>0.005</bias_stddev>
            </noise>
          </x>
          <y>
            <noise type="gaussian">
              <mean>0.0</mean>
              <stddev>0.02</stddev>
              <bias_mean>0.0</bias_mean>
              <bias_stddev>0.005</bias_stddev>
            </noise>
          </y>
          <z>
            <noise type="gaussian">
              <mean>0.0</mean>
              <stddev>0.02</stddev>
              <bias_mean>0.0</bias_mean>
              <bias_stddev>0.005</bias_stddev>
            </noise>
          </z>
        </angular_velocity>
        <linear_acceleration>
          <x>
            <noise type="gaussian">
              <mean>0.0</mean>
              <stddev>0.017</stddev>
              <bias_mean>0.0</bias_mean>
              <bias_stddev>0.005</bias_stddev>
            </noise>
          </x>
          <y>
            <noise type="gaussian">
              <mean>0.0</mean>
              <stddev>0.017</stddev>
              <bias_mean>0.0</bias_mean>
              <bias_stddev>0.005</bias_stddev>
            </noise>
          </y>
          <z>
            <noise type="gaussian">
              <mean>0.0</mean>
              <stddev>0.017</stddev>
              <bias_mean>0.0</bias_mean>
              <bias_stddev>0.005</bias_stddev>
            </noise>
          </z>
        </linear_acceleration>
      </imu>
      
      <plugin name="imu_plugin" filename="libgazebo_ros_imu.so">
        <ros>
          <namespace>/imu</namespace>
          <remapping>~/out:=data</remapping>
        </ros>
        <frame_name>torso_imu_frame</frame_name>
        <body_name>torso</body_name>
        <update_rate>100</update_rate>
      </plugin>
    </sensor>
    
    <!-- 2D LiDAR on head -->
    <sensor name="head_lidar" type="ray">
      <pose>0.05 0 0.08 0 0 0</pose>
      <ray>
        <scan>
          <horizontal>
            <samples>720</samples>
            <resolution>1</resolution>
            <min_angle>-3.14159</min_angle>  <!-- -π -->
            <max_angle>3.14159</max_angle>   <!-- π -->
          </horizontal>
        </scan>
        <range>
          <min>0.1</min>
          <max>10</max>
          <resolution>0.01</resolution>
        </range>
      </ray>
      <always_on>true</always_on>
      <update_rate>10</update_rate>
      <visualize>true</visualize>
      
      <plugin name="lidar_plugin" filename="libgazebo_ros_laser.so">
        <ros>
          <namespace>/laser</namespace>
          <remapping>~/out:=scan</remapping>
        </ros>
        <frame_name>head_lidar_frame</frame_name>
        <topic_name>scan</topic_name>
        <radiation_type>infrared</radiation_type>
      </plugin>
    </sensor>
    
    <!-- Left Arm -->
    <link name="left_shoulder">
      <pose>0.05 0.15 0.25 0 0 0</pose>
      <inertial>
        <mass>1.5</mass>
        <pose>0 0 -0.05 0 0 0</pose>
        <inertia>
          <ixx>0.01</ixx>
          <ixy>0</ixy>
          <ixz>0</ixz>
          <iyy>0.01</iyy>
          <iyz>0</iyz>
          <izz>0.005</izz>
        </inertia>
      </inertial>
      
      <collision name="collision">
        <geometry>
          <cylinder><radius>0.05</radius><length>0.1</length></cylinder>
        </geometry>
      </collision>
      
      <visual name="visual">
        <geometry>
          <cylinder><radius>0.05</radius><length>0.1</length></cylinder>
        </geometry>
        <material>
          <ambient>1 0.5 0.5 1</ambient>
          <diffuse>1 0.5 0.5 1</diffuse>
        </material>
      </visual>
    </link>
    
    <joint name="left_shoulder_yaw" type="revolute">
      <parent>torso</parent>
      <child>left_shoulder</child>
      <pose>0.05 0.15 0.25 0 0 0</pose>
      <axis>
        <xyz>0 0 1</xyz>
        <limit>
          <lower>-1.57</lower>
          <upper>1.57</upper>
          <effort>50</effort>
          <velocity>2.0</velocity>
        </limit>
        <dynamics>
          <damping>2.0</damping>
          <friction>0.2</friction>
        </dynamics>
      </axis>
    </joint>
    
    <!-- Add more joints and links for complete humanoid -->
  </model>
</sdf>
```

### Hints

- Use realistic mass distributions matching actual robot parameters
- Properly configure collision and visual meshes for performance
- Verify sensor parameters match real hardware capabilities
- Test physics stability with multiple simultaneous movements

## Exercise 2: Unity Integration with ROS Communication

Implement Unity integration with real-time ROS communication for robot visualization and control.

### Instructions

1. Create Unity scripts to connect to ROS using TCP connector
2. Implement a visualization system for the humanoid robot
3. Create sensor visualization for LiDAR, camera, and IMU
4. Implement a control interface for sending commands to the robot
5. Test communication between Unity and ROS

### Solution

#### 1. Unity ROS Connection Manager (already in previous chapter)

#### 2. Humanoid Robot Controller in Unity

```csharp
// HumanoidRobotController.cs
using UnityEngine;
using System.Collections;
using System.Collections.Generic;

public class HumanoidRobotController : MonoBehaviour
{
    [Header("Joint Configuration")]
    public List<JointConfig> jointConfigs = new List<JointConfig>();
    
    [System.Serializable]
    public class JointConfig
    {
        public string jointName;  // Name as it appears in ROS
        public Transform jointTransform;  // Corresponding Unity transform
        public JointType jointType;  // Revolute or Prismatic
        public float minAngle = -90f;  // In degrees
        public float maxAngle = 90f;   // In degrees
        public float multiplier = 1f;  // Multiplier for position values
    }
    
    public enum JointType
    {
        Revolute,
        Prismatic
    }
    
    // Joint state received from ROS
    private Dictionary<string, float> jointPositions = new Dictionary<string, float>();
    
    void Start()
    {
        // Initialize dictionaries for joint positions
        foreach(var config in jointConfigs)
        {
            jointPositions[config.jointName] = 0f;
        }
    }
    
    void Update()
    {
        // Update joint positions based on received data
        UpdateRobotJoints();
        
        // Handle manual control via keyboard or other input
        HandleManualControl();
    }
    
    public void UpdateJointPositions(Dictionary<string, float> newPositions)
    {
        // Update internal joint positions from ROS data
        lock(jointPositions)  // Thread-safe update
        {
            foreach(var position in newPositions)
            {
                if(jointPositions.ContainsKey(position.Key))
                {
                    jointPositions[position.Key] = position.Value;
                }
            }
        }
    }
    
    void UpdateRobotJoints()
    {
        // Update each joint's pose based on current position
        foreach(var config in jointConfigs)
        {
            if(jointPositions.ContainsKey(config.jointName))
            {
                float position = jointPositions[config.jointName];
                
                switch(config.jointType)
                {
                    case JointType.Revolute:
                        // Apply rotation to the joint transform
                        // Assuming rotation around local Z-axis
                        float clampedAngle = Mathf.Clamp(position * Mathf.Rad2Deg, config.minAngle, config.maxAngle);
                        config.jointTransform.localRotation = Quaternion.Euler(0, 0, clampedAngle);
                        break;
                    case JointType.Prismatic:
                        // Apply translation to the joint transform
                        // Assuming translation along local Z-axis
                        float clampedTrans = Mathf.Clamp(position * config.multiplier, config.minAngle/100, config.maxAngle/100);
                        Vector3 currentPos = config.jointTransform.localPosition;
                        config.jointTransform.localPosition = new Vector3(currentPos.x, currentPos.y, clampedTrans);
                        break;
                }
            }
        }
    }
    
    void HandleManualControl()
    {
        // Handle manual control if no ROS data is coming in
        if(Input.GetKey(KeyCode.UpArrow))
        {
            // Send command to move forward via ROS
            // This would call a method in the ROS connection manager
        }
        if(Input.GetKey(KeyCode.DownArrow))
        {
            // Send command to move backward via ROS
        }
        if(Input.GetKey(KeyCode.LeftArrow))
        {
            // Send command to turn left via ROS
        }
        if(Input.GetKey(KeyCode.RightArrow))
        {
            // Send command to turn right via ROS
        }
    }
    
    public void SetJointPosition(string jointName, float position)
    {
        if(jointPositions.ContainsKey(jointName))
        {
            jointPositions[jointName] = position;
        }
    }
    
    public float GetJointPosition(string jointName)
    {
        if(jointPositions.ContainsKey(jointName))
        {
            return jointPositions[jointName];
        }
        return 0f;
    }
}
```

#### 3. Sensor Visualization in Unity

```csharp
// SensorVisualizer.cs
using UnityEngine;
using System.Collections.Generic;

public class SensorVisualizer : MonoBehaviour
{
    [Header("Sensor Configuration")]
    public List<SensorConfig> sensorConfigs = new List<SensorConfig>();
    
    [System.Serializable]
    public class SensorConfig
    {
        public string sensorName;
        public SensorType sensorType;
        public Transform mountPoint;
        public GameObject visualizationPrefab;
        public Color visualizationColor = Color.blue;
        public float updateRate = 10f;
    }
    
    public enum SensorType
    {
        LiDAR,
        Camera,
        IMU,
        DepthCamera,
        ForceTorque,
        GPS
    }
    
    private Dictionary<string, GameObject> visualizations = new Dictionary<string, GameObject>();
    private Dictionary<string, float> lastUpdateTimes = new Dictionary<string, float>();
    
    void Start()
    {
        InitializeVisualizations();
    }
    
    void InitializeVisualizations()
    {
        foreach(var config in sensorConfigs)
        {
            switch(config.sensorType)
            {
                case SensorType.LiDAR:
                    CreateLiDARVisualization(config);
                    break;
                case SensorType.Camera:
                    CreateCameraVisualization(config);
                    break;
                case SensorType.IMU:
                    CreateIMUVIsualization(config);
                    break;
                // Add other sensor types as needed
            }
        }
    }
    
    void CreateLiDARVisualization(SensorConfig config)
    {
        // Create multiple ray visualizers for LiDAR
        GameObject lidarVisual = new GameObject($"{config.sensorName}_LiDAR_Visualization");
        lidarVisual.transform.SetParent(config.mountPoint, false);
        
        // Create visualization rays using LineRenderer
        int rayCount = 360;  // Typical for 360-degree LiDAR
        float angleIncrement = 2 * Mathf.PI / rayCount;
        
        for(int i = 0; i < rayCount; i++)
        {
            GameObject rayGO = new GameObject($"Ray_{i}");
            rayGO.transform.SetParent(lidarVisual.transform, false);
            
            LineRenderer lr = rayGO.AddComponent<LineRenderer>();
            lr.material = new Material(Shader.Find("Unlit/Color"));
            lr.material.color = config.visualizationColor;
            lr.startWidth = 0.01f;
            lr.endWidth = 0.01f;
            lr.positionCount = 2;
            
            // Start at mount point
            lr.SetPosition(0, config.mountPoint.position);
            // End at default position (will be updated with real data)
            float angle = i * angleIncrement;
            Vector3 direction = new Vector3(Mathf.Cos(angle), 0, Mathf.Sin(angle));
            lr.SetPosition(1, config.mountPoint.position + direction * 0.1f);
        }
        
        visualizations[config.sensorName] = lidarVisual;
        lastUpdateTimes[config.sensorName] = 0f;
    }
    
    void CreateCameraVisualization(SensorConfig config)
    {
        // Create camera frustum visualization
        GameObject cameraVisual = GameObject.CreatePrimitive(PrimitiveType.Quad);
        cameraVisual.name = $"{config.sensorName}_Camera_Visualization";
        cameraVisual.transform.SetParent(config.mountPoint, false);
        cameraVisual.transform.localPosition = Vector3.forward * 0.1f; // Offset slightly forward
        cameraVisual.transform.localScale = Vector3.one * 0.05f; // Size of the visualization
        
        // Apply color
        var rend = cameraVisual.GetComponent<Renderer>();
        rend.material = new Material(Shader.Find("Unlit/Color"));
        rend.material.color = config.visualizationColor;
        
        visualizations[config.sensorName] = cameraVisual;
        
        // Destroy primitive collider as we don't need it for visualization
        DestroyImmediate(cameraVisual.GetComponent<BoxCollider>());
    }
    
    void CreateIMUVIsualization(SensorConfig config)
    {
        // Create orientation indicator (arrow showing current orientation)
        GameObject imuVisual = new GameObject($"{config.sensorName}_IMU_Visualization");
        imuVisual.transform.SetParent(config.mountPoint, false);
        
        // Visualize orientation with a directional arrow
        GameObject arrowGO = new GameObject("Orientation_Arrow");
        arrowGO.transform.SetParent(imuVisual.transform, false);
        
        LineRenderer lr = arrowGO.AddComponent<LineRenderer>();
        lr.material = new Material(Shader.Find("Unlit/Color"));
        lr.material.color = config.visualizationColor;
        lr.startWidth = 0.02f;
        lr.endWidth = 0.02f;
        lr.positionCount = 2;
        
        // Start at the IMU position
        lr.SetPosition(0, config.mountPoint.position);
        // End pointing forward initially (will be updated with orientation data)
        lr.SetPosition(1, config.mountPoint.position + config.mountPoint.forward * 0.3f);
        
        visualizations[config.sensorName] = imuVisual;
        lastUpdateTimes[config.sensorName] = 0f;
    }
    
    void Update()
    {
        UpdateVisualizations();
    }
    
    void UpdateVisualizations()
    {
        float currentTime = Time.time;
        
        foreach(var config in sensorConfigs)
        {
            // Update at the sensor's specified rate
            if(currentTime - lastUpdateTimes[config.sensorName] >= 1f/config.updateRate)
            {
                switch(config.sensorType)
                {
                    case SensorType.LiDAR:
                        UpdateLiDARVisualization(config, currentTime);
                        break;
                    case SensorType.IMU:
                        UpdateIMUVIsualization(config, currentTime);
                        break;
                    case SensorType.Camera:
                        UpdateCameraVisualization(config, currentTime);
                        break;
                }
                
                lastUpdateTimes[config.sensorName] = currentTime;
            }
        }
    }
    
    void UpdateLiDARVisualization(SensorConfig config, float updateTime)
    {
        // In real implementation, this would receive actual LiDAR data from ROS
        // For demo purposes, we'll create a simple pattern
        GameObject lidarGO = visualizations[config.sensorName];
        
        for(int i = 0; i < lidarGO.transform.childCount; i++)
        {
            Transform rayTransform = lidarGO.transform.GetChild(i);
            LineRenderer lr = rayTransform.GetComponent<LineRenderer>();
            
            if(lr != null)
            {
                // For this demo, create a simple radial pattern with some variation
                float angle = 2 * Mathf.PI * i / lidarGO.transform.childCount;
                // Add some variation based on time to simulate changing environment
                float distance = 2f + Mathf.Sin(updateTime + angle) * 0.5f;
                
                Vector3 direction = new Vector3(Mathf.Cos(angle), 0, Mathf.Sin(angle));
                Vector3 endPosition = config.mountPoint.position + direction * distance;
                
                lr.SetPosition(0, config.mountPoint.position);
                lr.SetPosition(1, endPosition);
            }
        }
    }
    
    void UpdateIMUVIsualization(SensorConfig config, float updateTime)
    {
        // In real implementation, this would receive actual IMU data
        // For demo, simulate orientation change
        GameObject imuGO = visualizations[config.sensorName];
        
        // Simulate gradual orientation change
        Vector3 orientationVector = new Vector3(
            Mathf.Sin(updateTime * 0.5f) * 0.5f,  // X oscillation
            0,                                  // No Y component
            1f + Mathf.Cos(updateTime * 0.5f) * 0.3f   // Z component (forward direction with slight variation)
        );
        
        Transform arrowTransform = imuGO.transform.GetChild(0);
        LineRenderer lr = arrowTransform.GetComponent<LineRenderer>();
        
        if(lr != null)
        {
            lr.SetPosition(0, config.mountPoint.position);
            lr.SetPosition(1, config.mountPoint.position + orientationVector.normalized * 0.3f);
        }
    }
    
    void UpdateCameraVisualization(SensorConfig config, float updateTime)
    {
        // Update camera visualization if needed
        // (e.g., show FOV, update texture if available)
    }
    
    // Methods to update visualization with real sensor data from ROS
    public void UpdateLiDARData(string sensorName, float[] ranges, float angleMin, float angleIncrement)
    {
        if(!visualizations.ContainsKey(sensorName)) return;
        
        GameObject lidarGO = visualizations[sensorName];
        
        for(int i = 0; i < Mathf.Min(ranges.Length, lidarGO.transform.childCount); i++)
        {
            Transform rayTransform = lidarGO.transform.GetChild(i);
            LineRenderer lr = rayTransform.GetComponent<LineRenderer>();
            
            if(lr != null && ranges[i] > 0 && ranges[i] < 10)  // Valid range within 10m
            {
                float angle = angleMin + i * angleIncrement;
                Vector3 direction = new Vector3(Mathf.Cos(angle), 0, Mathf.Sin(angle));
                Vector3 endPosition = config.mountPoint.position + direction * ranges[i];
                
                lr.SetPosition(0, config.mountPoint.position);
                lr.SetPosition(1, endPosition);
            }
        }
    }
    
    public void UpdateIMUData(string sensorName, float[] orientationQuat)
    {
        if(!visualizations.ContainsKey(sensorName)) return;
        
        GameObject imuGO = visualizations[sensorName];
        
        if(orientationQuat.Length >= 4)
        {
            Quaternion orientation = new Quaternion(
                orientationQuat[0],
                orientationQuat[1],
                orientationQuat[2],
                orientationQuat[3]
            );
            
            Transform arrowTransform = imuGO.transform.GetChild(0);
            LineRenderer lr = arrowTransform.GetComponent<LineRenderer>();
            
            if(lr != null)
            {
                Vector3 forwardDirection = orientation * Vector3.forward;
                lr.SetPosition(0, config.mountPoint.position);
                lr.SetPosition(1, config.mountPoint.position + forwardDirection * 0.3f);
            }
        }
    }
}
```

### Hints

- Use efficient rendering techniques for sensor visualization
- Implement proper data synchronization between ROS and Unity
- Optimize for real-time visualization performance
- Consider using Unity's Job System for performance-critical visualization

## Exercise 3: System Integration and Validation

Integrate all components and validate the complete humanoid simulation pipeline.

### Instructions

1. Connect Gazebo simulation with Unity visualization
2. Implement sensor fusion between simulated sensors
3. Create validation tests for the complete system
4. Test robot autonomy pipeline with sample scenarios
5. Optimize system performance and stability

### Solution

#### 1. Integration Launch File

```xml
<!-- launch/humanoid_complete_simulation.launch.py -->
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    # Launch arguments
    use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation time if true'
    )
    
    robot_model = DeclareLaunchArgument(
        'robot_model',
        default_value='humanoid_robot_advanced',
        description='Robot model to load in simulation'
    )
    
    world_file = DeclareLaunchArgument(
        'world_file',
        default_value='my_humanoid_world',
        description='World file to load'
    )
    
    # Include Gazebo launch
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('gazebo_ros'),
                'launch',
                'gazebo.launch.py'
            ])
        ]),
        launch_arguments={
            'world': PathJoinSubstitution([
                FindPackageShare('my_humanoid_gazebo'),
                'worlds',
                LaunchConfiguration('world_file')
            ]),
            'verbose': 'true'
        }.items()
    )
    
    # Robot spawn node
    spawn_robot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', LaunchConfiguration('robot_model'),
            '-file', PathJoinSubstitution([
                FindPackageShare('my_humanoid_description'),
                'models',
                LaunchConfiguration('robot_model'),
                'model.sdf'
            ]),
            '-x', '0', '-y', '0', '-z', '0.85'
        ],
        output='screen'
    )
    
    # Robot state publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': PathJoinSubstitution([
                FindPackageShare('my_humanoid_description'),
                'urdf',
                'humanoid.urdf'
            ]),
            'use_sim_time': LaunchConfiguration('use_sim_time')
        }]
    )
    
    # Joint state publisher
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}]
    )
    
    # Our custom modules
    perception_node = Node(
        package='my_humanoid_perception',
        executable='perception_node',
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        output='screen'
    )
    
    planning_node = Node(
        package='my_humanoid_planning',
        executable='planning_node',
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        output='screen'
    )
    
    control_node = Node(
        package='my_humanoid_control',
        executable='control_node',
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        output='screen'
    )
    
    # Unity bridge node (if using a custom ROS-Unity bridge)
    unity_bridge = Node(
        package='my_unity_bridge',
        executable='unity_ros_bridge',
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        output='screen'
    )
    
    return LaunchDescription([
        use_sim_time_arg,
        robot_model_arg,
        world_file_arg,
        
        gazebo_launch,
        spawn_entity,
        robot_state_publisher,
        joint_state_publisher,
        perception_node,
        planning_node,
        control_node,
        unity_bridge
    ])
```

#### 2. Validation Test Scripts

```python
# validation_tests.py
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState, LaserScan, Imu
from geometry_msgs.msg import Twist, Pose
from nav_msgs.msg import Odometry
from std_msgs.msg import Float64MultiArray
import time
import numpy as np
import matplotlib.pyplot as plt


class SystemValidator(Node):
    """Node to validate the complete humanoid system"""
    
    def __init__(self):
        super().__init__('system_validator')
        
        self.joint_states = None
        self.lidar_data = None
        self.imu_data = None
        self.odom_data = None
        
        # Subscriptions
        self.joint_state_sub = self.create_subscription(
            JointState, '/joint_states', self.joint_state_callback, 10
        )
        
        self.lidar_sub = self.create_subscription(
            LaserScan, '/scan', self.lidar_callback, 10
        )
        
        self.imu_sub = self.create_subscription(
            Imu, '/imu/data', self.imu_callback, 10
        )
        
        self.odom_sub = self.create_subscription(
            Odometry, '/odom', self.odom_callback, 10
        )
        
        # Test parameters
        self.test_start_time = None
        self.test_duration = 30  # seconds
        
        # Test results
        self.test_results = {
            'joint_states_received': 0,
            'lidar_scans_received': 0,
            'imu_messages_received': 0,
            'odometry_messages_received': 0,
            'data_consistency': True,
            'system_stability': True
        }
        
        self.get_logger().info("System validator initialized")
    
    def joint_state_callback(self, msg):
        """Process joint state messages"""
        self.joint_states = msg
        self.test_results['joint_states_received'] += 1
        
        # Validate joint state data
        if len(msg.position) != len(msg.name):
            self.get_logger().warn("Joint state position/name length mismatch")
            self.test_results['data_consistency'] = False
    
    def lidar_callback(self, msg):
        """Process LiDAR messages"""
        self.lidar_data = msg
        self.test_results['lidar_scans_received'] += 1
        
        # Validate LiDAR data
        if len(msg.ranges) == 0:
            self.get_logger().warn("Received LiDAR message with no ranges")
            self.test_results['data_consistency'] = False
    
    def imu_callback(self, msg):
        """Process IMU messages"""
        self.imu_data = msg
        self.test_results['imu_messages_received'] += 1
    
    def odom_callback(self, msg):
        """Process odometry messages"""
        self.odom_data = msg
        self.test_results['odometry_messages_received'] += 1
        
        # Check for stability in position (for stationary test)
        pos = msg.pose.pose.position
        position_magnitude = np.sqrt(pos.x**2 + pos.y**2 + pos.z**2)
        
        if position_magnitude > 10.0:  # If robot is moving unexpectedly far
            self.test_results['system_stability'] = False
            self.get_logger().warn(f"Robot appears unstable: position = ({pos.x}, {pos.y}, {pos.z})")
    
    def run_system_validation(self):
        """Run the complete system validation test"""
        self.get_logger().info("Starting system validation test")
        self.test_start_time = time.time()
        
        # Run test for specified duration
        while time.time() - self.test_start_time < self.test_duration:
            rclpy.spin_once(self, timeout_sec=0.1)
            
            # Log progress every 5 seconds
            elapsed = time.time() - self.test_start_time
            if int(elapsed) % 5 == 0:
                self.get_logger().info(f"Test progress: {elapsed:.1f}/{self.test_duration}s")
        
        # Generate final results
        self.generate_validation_report()
    
    def generate_validation_report(self):
        """Generate and save validation report"""
        report = f"""
        SYSTEM VALIDATION REPORT
        ======================
        Test Duration: {self.test_duration}s
        
        Data Reception:
        - Joint States: {self.test_results['joint_states_received']} messages
        - LiDAR Scans: {self.test_results['lidar_scans_received']} messages  
        - IMU Messages: {self.test_results['imu_messages_received']} messages
        - Odometry Messages: {self.test_results['odometry_messages_received']} messages
        
        Data Consistency: {'PASS' if self.test_results['data_consistency'] else 'FAIL'}
        System Stability: {'PASS' if self.test_results['system_stability'] else 'FAIL'}
        
        Recommendations:
        - {'Data streams working correctly' if self.test_results['data_consistency'] else 'Check sensor configurations for consistency issues'}
        - {'System is stable during test' if self.test_results['system_stability'] else 'Investigate stability issues'}
        """
        
        # Save report to file
        with open('/tmp/system_validation_report.txt', 'w') as f:
            f.write(report)
        
        self.get_logger().info(f"Validation report saved to /tmp/system_validation_report.txt")
        self.get_logger().info(report)


def main(args=None):
    rclpy.init(args=args)
    validator = SystemValidator()
    
    try:
        validator.run_system_validation()
    except KeyboardInterrupt:
        validator.get_logger().info("Validation test interrupted")
    finally:
        validator.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

#### 3. Performance Optimization Script

```python
# performance_optimizer.py
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from builtin_interfaces.msg import Time
import time
import psutil
import GPUtil
from collections import deque
import statistics


class PerformanceOptimizer(Node):
    """Node to monitor and optimize system performance"""
    
    def __init__(self):
        super().__init__('performance_optimizer')
        
        self.metrics_sub = self.create_subscription(
            String, '/performance_metrics', self.metrics_callback, 10
        )
        
        self.advice_pub = self.create_publisher(String, '/performance_advice', 10)
        
        # Metrics history
        self.cpu_history = deque(maxlen=100)
        self.memory_history = deque(maxlen=100)
        self.processing_times = deque(maxlen=100)
        
        # Performance thresholds
        self.cpu_threshold = 80  # percent
        self.memory_threshold = 85  # percent
        self.processing_time_threshold = 0.05  # seconds (20Hz rate)
        
        # Timer for performance analysis
        self.analysis_timer = self.create_timer(2.0, self.analyze_performance)
        
        self.get_logger().info("Performance optimizer initialized")
    
    def metrics_callback(self, msg):
        """Process performance metrics from various system components"""
        try:
            metrics = eval(msg.data)  # In practice, use json.loads for safety
            
            # Store metrics
            if 'cpu_percent' in metrics:
                self.cpu_history.append(metrics['cpu_percent'])
            
            if 'memory_percent' in metrics:
                self.memory_history.append(metrics['memory_percent'])
            
            if 'processing_time' in metrics:
                self.processing_times.append(metrics['processing_time'])
                
        except Exception as e:
            self.get_logger().error(f"Error parsing performance metrics: {e}")
    
    def analyze_performance(self):
        """Analyze collected performance metrics and provide optimization advice"""
        advice_msg = String()
        advice = []
        
        # Check CPU usage
        if self.cpu_history:
            avg_cpu = statistics.mean(self.cpu_history)
            peak_cpu = max(self.cpu_history)
            
            if peak_cpu > self.cpu_threshold:
                advice.append(f"High CPU usage detected (peak: {peak_cpu}%, avg: {avg_cpu:.1f}%). "
                             "Consider reducing sensor update rates or simplifying perception algorithms.")
        
        # Check memory usage
        if self.memory_history:
            avg_mem = statistics.mean(self.memory_history)
            peak_mem = max(self.memory_history)
            
            if peak_mem > self.memory_threshold:
                advice.append(f"High memory usage detected (peak: {peak_mem}%, avg: {avg_mem:.1f}%). "
                             "Consider optimizing data structures or implementing memory pooling.")
        
        # Check processing times
        if self.processing_times:
            avg_time = statistics.mean(self.processing_times)
            max_time = max(self.processing_times)
            
            if max_time > self.processing_time_threshold:
                advice.append(f"High processing times detected (max: {max_time*1000:.1f}ms). "
                             "Consider increasing update periods or optimizing algorithms.")
        
        # If no specific issues but system seems generally stressed
        if not advice and len(self.cpu_history) > 0:
            avg_cpu = statistics.mean(self.cpu_history)
            if avg_cpu > 70:  # High but not critical
                advice.append(f"Moderate system load (avg CPU: {avg_cpu:.1f}%). "
                             "Monitor for potential performance issues during complex tasks.")
        
        if advice:
            advice_msg.data = "PERFORMANCE ADVICE: " + " ".join(advice)
            self.advice_pub.publish(advice_msg)
            self.get_logger().warn(advice_msg.data)
        else:
            # Log system status regularly
            if self.cpu_history:
                avg_cpu = statistics.mean(self.cpu_history)
                self.get_logger().info(f"System performance OK (CPU: {avg_cpu:.1f}%)")
    
    def get_system_resources(self) -> dict:
        """Get current system resources"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'timestamp': self.get_clock().now().nanoseconds / 1e9
        }


def main(args=None):
    rclpy.init(args=args)
    optimizer = PerformanceOptimizer()
    
    try:
        rclpy.spin(optimizer)
    except KeyboardInterrupt:
        optimizer.get_logger().info("Performance optimizer shutting down...")
    finally:
        optimizer.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### Hints

- Thoroughly test integration between all modules
- Use systematic validation approaches to verify functionality
- Monitor performance and optimize bottlenecks
- Implement proper error handling and recovery
- Validate sensor fusion accuracy
- Test autonomy pipeline with realistic scenarios

## Chapter Summary

This exercise set covered the complete integration of the humanoid robot simulation system combining Gazebo physics simulation, Unity visualization, sensor modeling, and ROS 2 communication. We implemented:

1. **Complete Gazebo Environment**: Indoor world with realistic physics and humanoid model
2. **Unity Integration**: Visualization of robot and sensor data with real-time updates
3. **System Validation**: Approaches to validate the complete integrated system
4. **Performance Optimization**: Techniques to maintain real-time operation

These components work together to create a comprehensive simulation environment that enables development and testing of humanoid robot systems before deployment on physical robots.

## Checklist

- [ ] Implement complete Gazebo simulation with humanoid robot
- [ ] Integrate realistic physics parameters for humanoid behavior
- [ ] Configure and validate multiple sensor types (LiDAR, IMU, cameras)
- [ ] Connect Unity for advanced visualization and control
- [ ] Validate system performance under various conditions
- [ ] Create robust error handling and recovery procedures
- [ ] Test integration between all system components
- [ ] Optimize simulation for real-time operation

## References

- [Gazebo Sensor Plugins Documentation](http://gazebosim.org/tutorials/?tut=ros2_sensor_tutorial)
- [Unity Robotics Repository](https://github.com/Unity-Technologies/Unity-Robotics-Hub)
- [ROS 2 Integration Best Practices](https://design.ros2.org/articles/ROS2_Integration.html)
- [Simulation Testing for Robotics](https://ieeexplore.ieee.org/document/9100015)
- [Humanoid Robot Simulation Guidelines](https://link.springer.com/chapter/10.1007/978-3-030-50140-0_12)