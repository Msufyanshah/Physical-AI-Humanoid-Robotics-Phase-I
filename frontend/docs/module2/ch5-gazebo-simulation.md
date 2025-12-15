---
title: 'Chapter 5 - Gazebo Simulation Fundamentals'
description: 'Fundamentals of Gazebo simulation for robotics development'
---

# Chapter 5: Gazebo Simulation Fundamentals

## Learning Objectives

After reading this chapter, you will be able to:
- Understand the architecture and capabilities of Gazebo simulator
- Create and configure basic simulation environments
- Model robot kinematics and dynamics for simulation
- Implement sensors in Gazebo with realistic parameters
- Integrate Gazebo with ROS 2 for robot development
- Test and validate robot behaviors in simulation

## Introduction

Gazebo is a powerful 3D simulation environment that plays a crucial role in robotics development. It provides realistic physics simulation, high-quality graphics, and various sensor models that enable developers to test and validate their robots before deploying to the real world. This chapter covers the fundamentals of Gazebo simulation relevant to humanoid robotics development.

## Gazebo Architecture and Components

### Core Components

Gazebo consists of several key components that work together to create realistic robotic simulations:

1. **Physics Engine**: Handles collision detection, contacts, and dynamics simulation
2. **Rendering Engine**: Provides 3D visualization with realistic lighting and shading
3. **Sensor System**: Simulates various robot sensors with realistic noise models
4. **GUI Interface**: Allows real-time visualization and interaction with the simulation
5. **Plugin Architecture**: Extends Gazebo's functionality with custom behaviors

### Simulation Loop

Gazebo operates in a continuous simulation loop:

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│                 │    │              │    │                 │
│   World State   │───▶│  Physics     │───▶│   World State   │
│     Update      │    │  Simulation  │    │     Update      │
│                 │    │              │    │                 │
└─────────────────┘    └──────────────┘    └─────────────────┘
        ▲                                           │
        │                                           ▼
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│                 │    │              │    │                 │
│   Sensor        │◀───│  Rendering   │◀───│   Actuator      │
│   Simulation    │    │              │    │   Commands      │
│                 │    │              │    │                 │
└─────────────────┘    └──────────────┘    └─────────────────┘
```

## Creating Simulation Worlds

### World File Structure

Gazebo worlds are defined using SDF (Simulation Description Format), an XML-based format:

```xml
<?xml version="1.0" ?>
<sdf version="1.7">
  <world name="my_world">
    <!-- Include models from the model database -->
    <include>
      <uri>model://ground_plane</uri>
    </include>
    
    <include>
      <uri>model://sun</uri>
    </include>
    
    <!-- Define custom models -->
    <model name="my_robot">
      <!-- Model definition -->
    </model>
    
    <!-- Physics parameters -->
    <physics name="default_physics" type="ode">
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1</real_time_factor>
      <real_time_update_rate>1000</real_time_update_rate>
    </physics>
  </world>
</sdf>
```

### Ground Plane and Environment

The ground plane is usually the first thing defined in a simulation world:

```xml
<model name="ground_plane">
  <static>true</static>
  <link name="link">
    <collision name="collision">
      <geometry>
        <plane>
          <normal>0 0 1</normal>
          <size>100 100</size>
        </plane>
      </geometry>
      <surface>
        <friction>
          <ode>
            <mu>1.0</mu>
            <mu2>1.0</mu2>
          </ode>
        </friction>
        <contact>
          <ode/>
        </contact>
        <bounce/>
      </surface>
    </collision>
    <visual name="visual">
      <cast_shadows>false</cast_shadows>
      <geometry>
        <plane>
          <normal>0 0 1</normal>
          <size>100 100</size>
        </plane>
      </geometry>
      <material>
        <script>
          <uri>file://media/materials/scripts/gazebo.material</uri>
          <name>Gazebo/Grass</name>
        </script>
      </material>
    </visual>
  </link>
</model>
```

## Robot Model Definition (SDF/URDF)

### SDF vs URDF

While URDF is more commonly used with ROS, Gazebo uses SDF (Simulation Description Format) internally. However, you can include URDF files directly in Gazebo worlds:

```xml
<model name="my_humanoid_robot">
  <include>
    <uri>file://path/to/my_robot.urdf</uri>
  </include>
</model>
```

Or define the model directly in SDF:

```xml
<model name="simple_humanoid">
  <pose>0 0 1 0 0 0</pose>
  <link name="torso">
    <pose>0 0 0.5 0 0 0</pose>
    <collision name="collision">
      <geometry>
        <box>
          <size>0.3 0.2 0.5</size>
        </box>
      </geometry>
    </collision>
    <visual name="visual">
      <geometry>
        <box>
          <size>0.3 0.2 0.5</size>
        </box>
      </geometry>
      <material>
        <ambient>0.8 0.8 0.8 1</ambient>
        <diffuse>0.8 0.8 0.8 1</diffuse>
      </material>
    </visual>
    <inertial>
      <mass>10.0</mass>
      <inertia>
        <ixx>0.4</ixx>
        <ixy>0</ixy>
        <ixz>0</ixz>
        <iyy>0.4</iyy>
        <iyz>0</iyz>
        <izz>0.4</izz>
      </inertia>
    </inertial>
  </link>
  
  <link name="head">
    <pose>0 0 0.35 0 0 0</pose>
    <collision name="collision">
      <geometry>
        <sphere>
          <radius>0.1</radius>
        </sphere>
      </geometry>
    </collision>
    <visual name="visual">
      <geometry>
        <sphere>
          <radius>0.1</radius>
        </sphere>
      </geometry>
      <material>
        <ambient>0.8 0.8 0.8 1</ambient>
        <diffuse>0.8 0.8 0.8 1</diffuse>
      </material>
    </visual>
    <inertial>
      <mass>2.0</mass>
      <inertia>
        <ixx>0.04</ixx>
        <ixy>0</ixy>
        <ixz>0</ixz>
        <iyy>0.04</iyy>
        <iyz>0</iyz>
        <izz>0.04</izz>
      </inertia>
    </inertial>
  </link>
  
  <joint name="neck_joint" type="revolute">
    <parent>torso</parent>
    <child>head</child>
    <pose>0 0 0.5 0 0 0</pose>
    <axis>
      <xyz>0 0 1</xyz>
      <limit>
        <lower>-0.5</lower>
        <upper>0.5</upper>
        <effort>100</effort>
        <velocity>1</velocity>
      </limit>
    </axis>
  </joint>
</model>
```

## Physics Configuration

### Choosing Physics Engines

Gazebo supports multiple physics engines:

1. **ODE (Open Dynamics Engine)**: Default, good for general cases
2. **Bullet**: Better for complex collision scenarios
3. **Simbody**: Detailed multibody dynamics

```xml
<physics name="ode_physics" default="0" type="ode">
  <max_step_size>0.001</max_step_size>
  <real_time_factor>1</real_time_factor>
  <real_time_update_rate>1000</real_time_update_rate>
  <gravity>0 0 -9.8</gravity>
  <ode>
    <solver>
      <type>quick</type>
      <iters>10</iters>
      <sor>1.3</sor>
    </solver>
    <constraints>
      <cfm>0.0</cfm>
      <erp>0.2</erp>
      <contact_max_correcting_vel>100.0</contact_max_correcting_vel>
      <contact_surface_layer>0.001</contact_surface_layer>
    </constraints>
  </ode>
</physics>
```

### Joint Dynamics

Properly configuring joint dynamics is crucial for realistic humanoid simulation:

```xml
<joint name="hip_joint" type="revolute">
  <parent>torsolink>
  <child>thigh_link</child>
  <axis>
    <xyz>0 1 0</xyz>
    <limit>
      <lower>-1.57</lower>
      <upper>1.57</upper>
      <effort>200</effort>  <!-- N*m for revolute joints -->
      <velocity>2.0</velocity>  <!-- rad/s -->
    </limit>
    <dynamics>
      <damping>1.0</damping>    <!-- Damping coefficient -->
      <friction>0.1</friction>  <!-- Static friction -->
      <spring_reference>0</spring_reference>
      <spring_stiffness>0</spring_stiffness>
    </dynamics>
  </axis>
</joint>
```

## Sensor Integration

### Camera Sensors

For humanoid robots, cameras are essential for perception:

```xml
<sensor name="head_camera" type="camera">
  <always_on>1</always_on>
  <update_rate>30</update_rate>
  <camera name="head_camera">
    <horizontal_fov>1.047</horizontal_fov> <!-- 60 degrees -->
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
  <plugin name="camera_controller" filename="libgazebo_ros_camera.so">
    <ros>
      <namespace>/camera</namespace>
      <remapping>~/image_raw:=image</remapping>
      <remapping>~/camera_info:=camera_info</remapping>
    </ros>
    <camera_name>head_camera</camera_name>
    <frame_name>head_camera_frame</frame_name>
    <hack_baseline>0.07</hack_baseline>
    <distortion_k1>0.0</distortion_k1>
    <distortion_k2>0.0</distortion_k2>
    <distortion_k3>0.0</distortion_k3>
    <distortion_t1>0.0</distortion_t1>
    <distortion_t2>0.0</distortion_t2>
  </plugin>
</sensor>
```

### IMU Sensors

Inertial Measurement Units are crucial for balance control in humanoid robots:

```xml
<sensor name="imu_sensor" type="imu">
  <always_on>true</always_on>
  <update_rate>100</update_rate>
  <pose>0.1 0 0.2 0 0 0</pose>  <!-- Position in the robot -->
  <plugin name="imu_plugin" filename="libgazebo_ros_imu.so">
    <ros>
      <namespace>/imu</namespace>
      <remapping>~/out:=data</remapping>
    </ros>
    <topic>/imu/data</topic>
    <body_name>torso</body_name>
    <update_rate>100</update_rate>
    <gaussian_noise>0.001</gaussian_noise>  <!-- Noise parameter -->
    <xyz_offset>0 0 0</xyz_offset>
    <rpy_offset>0 0 0</rpy_offset>
  </plugin>
</sensor>
```

### Force/Torque Sensors

For manipulation tasks, force/torque sensors are important:

```xml
<sensor name="ft_sensor" type="force_torque">
  <always_on>true</always_on>
  <update_rate>100</update_rate>
  <force_torque>
    <frame>child</frame>  <!-- or parent, sensor, or world -->
    <measure_direction>child_to_parent</measure_direction>
  </force_torque>
  <plugin name="ft_plugin" filename="libgazebo_ros_ft_sensor.so">
    <ros>
      <namespace>/ft_sensor</namespace>
      <remapping>~/wrench:=wrench</remapping>
    </ros>
    <frame_name>sensor_frame</frame_name>
    <topic>ft_sensor</topic>
  </plugin>
</sensor>
```

## ROS 2 Integration

### Gazebo ROS Packages

The Gazebo-ROS integration is facilitated by the gazebo_ros_pkgs:

- `gazebo_ros`: Core ROS interface to Gazebo
- `gazebo_plugins`: Various plugin implementations
- `gazebo_dev`: Development files

### Launching Gazebo with ROS 2

To launch Gazebo with ROS 2 integration:

```xml
<!-- In a launch file (XML) -->
<launch>
  <include file="$(find-pkg-share gazebo_ros)/launch/gzserver.launch.py">
    <arg name="world" value="my_world.sdf"/>
    <arg name="verbose" value="false"/>
  </include>

  <include file="$(find-pkg-share gazebo_ros)/launch/gzclient.launch.py"/>
  
  <node pkg="robot_state_publisher" exec="robot_state_publisher" name="robot_state_publisher">
    <param name="robot_description" value="...urdf_content..."/>
  </node>
</launch>
```

Or in Python:

```python
# Launch file in Python
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Launch Gazebo
    gzserver_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('gazebo_ros'),
                'launch',
                'gzserver.launch.py'
            ])
        ]),
        launch_arguments={
            'world': PathJoinSubstitution([FindPackageShare('my_robot_gazebo'), 'worlds', 'my_world.sdf']),
            'verbose': 'false'
        }.items()
    )

    gzclient_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('gazebo_ros'),
                'launch',
                'gzclient.launch.py'
            ])
        ])
    )

    # Robot state publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        parameters=[{
            'robot_description': open('path/to/robot.urdf').read()
        }]
    )

    return LaunchDescription([
        gzserver_launch,
        gzclient_launch,
        robot_state_publisher
    ])
```

## Controllers and Actuators

### Joint State Publisher

The joint state publisher provides real-time information about joint positions and velocities:

```xml
<plugin name="joint_state_publisher" filename="libgazebo_ros_joint_state_publisher.so">
  <ros>
    <namespace>/robot</namespace>
    <remapping>~/out:=joint_states</remapping>
  </ros>
  <update_rate>30</update_rate>
  <joint_name>joint1</joint_name>
  <joint_name>joint2</joint_name>
  <!-- Add all joints you want to publish -->
</plugin>
```

### Joint Position Controllers

For controlling joint positions in simulation:

```xml
<plugin name="position_controller" filename="libgazebo_ros_joint_position.so">
  <command_topic>position_commands</command_topic>
  <state_topic>feedback_states</state_topic>
  <joint_name>my_joint</joint_name>
  <update_rate>100</update_rate>
  <ros>
    <namespace>/my_namespace</namespace>
  </ros>
</plugin>
```

## Simulation Best Practices

### 1. Realistic Parameters

Always use realistic physical parameters:

```xml
<!-- Good: Realistic mass based on actual robot -->
<mass>1.5</mass>

<!-- Good: Reasonable friction coefficients -->
<friction>
  <ode>
    <mu>0.7</mu>  <!-- Rubber on concrete -->
    <mu2>0.7</mu2>
  </ode>
</friction>

<!-- Good: Appropriate joint limits -->
<limit>
  <lower>-1.57</lower>  <!-- -90 degrees in radians -->
  <upper>1.57</upper>   <!-- 90 degrees in radians -->
  <effort>100</effort> <!-- Appropriate for the joint -->
  <velocity>2.0</velocity>
</limit>
```

### 2. Proper Scaling

Ensure consistent units (SI units - meters, kilograms, seconds):

```xml
<!-- Correct: Using meters -->
<size>0.3 0.2 0.5</size>  <!-- 30cm x 20cm x 50cm box -->

<!-- Incorrect: Mixing units -->
<size>30 20 50</size>     <!-- This would be 30m x 20m x 50m! -->
```

### 3. Sensor Noise Models

Use appropriate noise models to match real sensors:

```xml
<sensor name="lidar" type="gpu_lidar">
  <!-- ... other parameters ... -->
  <noise>
    <type>gaussian</type>
    <mean>0.0</mean>
    <stddev>0.01</stddev>  <!-- 1cm standard deviation -->
  </noise>
</sensor>
```

## Debugging Simulation Issues

### Common Problems and Solutions

1. **Robot Falls Through Ground**:
   - Check that `<static>` tag is not set to true for robot models
   - Verify `<inertial>` sections are properly defined
   - Ensure collision geometries are positioned correctly

2. **Joints Don't Move Properly**:
   - Check joint limits in URDF/SDF
   - Verify joint controllers are properly configured
   - Ensure joint names match between URDF and controller configs

3. **Sensors Return Invalid Data**:
   - Check sensor configuration in SDF
   - Verify plugin parameters
   - Ensure sensor frame names are correct

```bash
# Useful Gazebo debugging commands
gz topic -l  # List available topics
gz topic -i /gazebo/resource_markers  # Information about a topic
gz service -l  # List available services
```

## Performance Optimization

### Simulation Performance Tips

1. **Reduce Physics Update Rate**: If detailed physics isn't required, reduce `max_step_size`
2. **Minimize Complex Geometries**: Use simpler collision geometries than visual geometries
3. **Limit Sensor Update Rates**: Match to real sensor capabilities (often lower than simulation can provide)
4. **Disable Unnecessary Rendering**: For headless simulation

```xml
<!-- Optimized physics settings for performance -->
<physics name="fast_physics" type="ode">
  <max_step_size>0.01</max_step_size>  <!-- Larger step = faster but less accurate -->
  <real_time_factor>2</real_time_factor>  <!-- Can run 2x faster than real-time -->
  <real_time_update_rate>100</real_time_update_rate>  <!-- 100Hz physics updates -->
</physics>
```

## Chapter Summary

This chapter covered the fundamentals of Gazebo simulation for robotics, particularly for humanoid robots. We explored the architecture and components, world creation, physics configuration, sensor integration, and ROS 2 integration. Proper configuration of these elements is essential for effective robot simulation and testing before real-world deployment.

## Checklist

- [ ] Create Gazebo world files with appropriate environments
- [ ] Define robot models with proper kinematics and dynamics
- [ ] Configure physics parameters for realistic simulation
- [ ] Integrate sensors with appropriate noise models
- [ ] Connect Gazebo with ROS 2 for control
- [ ] Optimize simulation performance for development
- [ ] Validate simulation behavior matches expectations

## Exercises

### Exercise 1: Simple Robot in Gazebo

Create a simple robot model and configure it to work with Gazebo.

#### Solution

1. Create a basic URDF or SDF model with a few links and joints
2. Add collision and visual properties
3. Include in a Gazebo world file
4. Launch and test the simulation

#### Hints

- Start simple with a single body and one joint
- Use basic shapes (boxes, cylinders, spheres) for collision
- Add a joint controller to move the joint
- Validate physics by applying forces and observing response

### Exercise 2: Sensor Integration

Add a camera and IMU sensor to a robot model and verify they work correctly.

#### Solution

1. Add sensor definitions to your robot model
2. Include appropriate plugins for ROS 2 communication
3. Launch simulation with RViz to visualize sensor data
4. Verify sensor data streams correctly

#### Hints

- Check sensor frame names match in RViz
- Use Rviz2 to visualize camera images and IMU data
- Verify sensor update rates match real hardware
- Include appropriate noise models

## References

- [Gazebo Documentation](http://gazebosim.org/documentation/)
- [Gazebo-ROS Integration](http://gazebosim.org/tutorials?tut=ros2_overview)
- [SDF Specification](http://sdformat.org/specification)
- [ROS 2 with Gazebo](https://github.com/ros-simulation/gazebo_ros_pkgs)
- [Robotics Simulation: A Survey by K. Pathak](https://www.cs.cmu.edu/~kiranb/papers/Pathak2010Simulation.pdf)