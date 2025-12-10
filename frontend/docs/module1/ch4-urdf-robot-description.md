---
title: 'Chapter 4 - URDF & Robot Description for Humanoids'
description: 'Understanding URDF for robot description, particularly for humanoid robots'
---

# Chapter 4: URDF & Robot Description for Humanoids

## Learning Objectives

After reading this chapter, you will be able to:
- Understand the Unified Robot Description Format (URDF)
- Create URDF files for complex robots, with a focus on humanoid designs
- Work with joints, links, and transforms in URDF
- Import and visualize humanoid robots in simulation environments
- Apply best practices for humanoid robot description

## Introduction

The Unified Robot Description Format (URDF) is an XML-based format used in ROS to describe robot models. It's critical for humanoid robotics as it defines the physical structure, kinematics, and visual/collision properties of robots. This chapter focuses on how to describe humanoid robots using URDF, including the special considerations required for these complex systems.

## URDF Basics

### XML Structure

A URDF file is an XML document with a specific structure:

```xml
<?xml version="1.0"?>
<robot name="my_robot">
  <!-- Links define rigid bodies -->
  <link name="base_link">
    <!-- Inertial properties -->
    <inertial>
      <origin xyz="0 0 0" rpy="0 0 0" />
      <mass value="1.0" />
      <inertia ixx="1.0" ixy="0.0" ixz="0.0" iyy="1.0" iyz="0.0" izz="1.0" />
    </inertial>
    
    <!-- Visual properties (for visualization) -->
    <visual>
      <origin xyz="0 0 0" rpy="0 0 0" />
      <geometry>
        <box size="0.5 0.5 0.5" />
      </geometry>
    </visual>
    
    <!-- Collision properties (for physics simulation) -->
    <collision>
      <origin xyz="0 0 0" rpy="0 0 0" />
      <geometry>
        <box size="0.5 0.5 0.5" />
      </geometry>
    </collision>
  </link>
  
  <!-- Joints define connections between links -->
  <joint name="base_to_wheel" type="continuous">
    <parent link="base_link" />
    <child link="wheel_link" />
    <origin xyz="0.25 0 0" rpy="0 0 0" />
    <axis xyz="0 0 1" />
  </joint>
  
  <link name="wheel_link">
    <visual>
      <origin xyz="0 0 0" rpy="0 0 0" />
      <geometry>
        <cylinder radius="0.1" length="0.05" />
      </geometry>
    </visual>
  </link>
</robot>
```

### Key URDF Elements

- **robot**: Root element containing the entire robot description
- **link**: Represents a rigid body with physical properties
- **joint**: Defines how two links connect and move relative to each other
- **material**: Defines visual appearance properties
- **transmission**: Defines how actuators interact with joints

## Links in URDF

### Link Properties

Links represent rigid bodies in the robot. Each link can have:

1. **Inertial**: Mass, center of mass, and inertia tensor
2. **Visual**: How the link appears in visualizations
3. **Collision**: How the link interacts in physics simulation

### Inertial Properties

```xml
<inertial>
  <origin xyz="0.0 0.0 0.0" rpy="0.0 0.0 0.0" />
  <mass value="0.1" />
  <inertia ixx="0.001" ixy="0.0" ixz="0.0" iyy="0.001" iyz="0.0" izz="0.001" />
</inertial>
```

For complex shapes, you may need to calculate the inertia tensor using CAD tools or approximation formulas.

### Visual and Collision Properties

```xml
<visual>
  <origin xyz="0 0 0" rpy="0 0 0" />
  <geometry>
    <mesh filename="package://my_robot/meshes/link1.dae" scale="1 1 1" />
  </geometry>
  <material name="blue">
    <color rgba="0 0 0.8 1" />
  </material>
</visual>

<collision>
  <origin xyz="0 0 0" rpy="0 0 0" />
  <geometry>
    <mesh filename="package://my_robot/meshes/link1_collision.dae" />
  </geometry>
</collision>
```

## Joints in URDF

### Joint Types

URDF supports several joint types:

1. **revolute**: Rotational joint with limited range
2. **continuous**: Rotational joint without limits
3. **prismatic**: Linear sliding joint with limits
4. **fixed**: No movement (welds two links)
5. **floating**: 6 DOF motion (for base of floating robots)
6. **planar**: Motion on a plane

### Joint Definition

```xml
<joint name="shoulder_joint" type="revolute">
  <parent link="torso" />
  <child link="upper_arm" />
  <origin xyz="0.0 0.2 0.3" rpy="0 0 0" />
  <axis xyz="0 1 0" />
  <limit lower="-1.57" upper="1.57" effort="100" velocity="1.0" />
  <dynamics damping="0.5" friction="0.1" />
</joint>
```

### Joint Parameters

- **origin**: Position and orientation of joint relative to parent link
- **axis**: Axis of rotation or translation
- **limit**: Joint limits (for revolute/prismatic joints)
  - lower/upper: Position limits
  - effort: Maximum effort/torque
  - velocity: Maximum velocity
- **dynamics**: Physical properties
  - damping: Damping coefficient
  - friction: Friction coefficient

## Humanoid-Specific Considerations

### Humanoid Kinematic Structure

A typical humanoid robot has a specific kinematic structure:

```
base_link (pelvis)
├── torso
│   ├── head
│   ├── left_upper_arm
│   │   ├── left_lower_arm
│   │   └── left_hand
│   ├── right_upper_arm
│   │   ├── right_lower_arm
│   │   └── right_hand
│   ├── left_upper_leg
│   │   ├── left_lower_leg
│   │   └── left_foot
│   └── right_upper_leg
│       ├── right_lower_leg
│       └── right_foot
```

### Special Joint Requirements

Humanoids require special attention to:

- **Degrees of Freedom**: Human-like range of motion
- **Joint Limits**: To prevent damage and ensure natural movement
- **Safety**: Limits to prevent collisions and overextension

```xml
<!-- Example shoulder joint with human-like limits -->
<joint name="left_shoulder_pitch" type="revolute">
  <parent link="torso" />
  <child link="left_upper_arm" />
  <origin xyz="0.0 0.15 0.1" rpy="0 0 0" />
  <axis xyz="0 1 0" />
  <limit lower="-2.356" upper="1.571" effort="200" velocity="2.0" />
  <dynamics damping="1.0" friction="0.2" />
</joint>
```

## URDF for Complex Humanoids

### Using Xacro for Readability

Xacro (XML Macros) is a preprocessor that allows you to use variables, macros, and expressions in URDF:

```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="humanoid_robot">

  <!-- Define variables -->
  <xacro:property name="M_PI" value="3.1415926535897931" />
  <xacro:property name="arm_length" value="0.3" />
  <xacro:property name="arm_radius" value="0.05" />
  
  <!-- Define a macro for arms -->
  <xacro:macro name="arm" params="side reflect">
    <link name="${side}_upper_arm">
      <visual>
        <geometry>
          <cylinder length="${arm_length}" radius="${arm_radius}" />
        </geometry>
        <origin xyz="0 0 ${arm_length/2}" rpy="0 0 0" />
      </visual>
      <collision>
        <geometry>
          <cylinder length="${arm_length}" radius="${arm_radius}" />
        </geometry>
        <origin xyz="0 0 ${arm_length/2}" rpy="0 0 0" />
      </collision>
      <inertial>
        <mass value="1.0" />
        <inertia ixx="0.1" ixy="0.0" ixz="0.0" iyy="0.1" iyz="0.0" izz="0.1" />
      </inertial>
    </link>
  </xacro:macro>
  
  <!-- Use the macro -->
  <xacro:arm side="left" reflect="1" />
  <xacro:arm side="right" reflect="-1" />

</robot>
```

### Including External Files

Large robots can be organized into multiple files:

```xml
<!-- Include other URDF files -->
<xacro:include filename="$(find my_robot_description)/urdf/head.urdf.xacro" />
<xacro:include filename="$(find my_robot_description)/urdf/arms.urdf.xacro" />
<xacro:include filename="$(find my_robot_description)/urdf/legs.urdf.xacro" />

<!-- Combine components -->
<link name="base_link" />
<xacro:head prefix="head" parent="base_link" />
<xacro:arms prefix="left" parent="base_link" />
<xacro:arms prefix="right" parent="base_link" />
<xacro:legs prefix="left" parent="base_link" />
<xacro:legs prefix="right" parent="base_link" />
```

## Visualization and Validation

### Checking URDF

You can validate and visualize your URDF using ROS tools:

```bash
# Check for XML syntax errors
check_urdf /path/to/robot.urdf

# Visualize the robot structure
urdf_to_graphiz /path/to/robot.urdf

# Launch with RViz
roslaunch my_robot_description display.launch model:='/path/to/robot.urdf'
```

### Common Issues and Fixes

1. **Missing parent links**: Ensure every child link has a corresponding parent
2. **Floating joints**: Connect all links to a base link
3. **Inertia issues**: Every link needs valid inertial properties
4. **Joint limits**: Set appropriate limits to prevent damage

## Gazebo Integration

### Adding Gazebo-Specific Elements

For simulation in Gazebo, you can add Gazebo-specific elements:

```xml
<!-- Gazebo material -->
<gazebo reference="link_name">
  <material>Gazebo/Blue</material>
</gazebo>

<!-- Gazebo plugin -->
<gazebo>
  <plugin name="robot_state_publisher" filename="libgazebo_ros_robot_state_publisher.so">
    <robotNamespace>/</robotNamespace>
    <updateRate>30.0</updateRate>
  </plugin>
</gazebo>

<!-- Gazebo transmission for actuators -->
<transmission name="tran1">
  <type>transmission_interface/SimpleTransmission</type>
  <joint name="joint1">
    <hardwareInterface>hardware_interface/EffortJointInterface</hardwareInterface>
  </joint>
  <actuator name="motor1">
    <hardwareInterface>hardware_interface/EffortJointInterface</hardwareInterface>
    <mechanicalReduction>1</mechanicalReduction>
  </actuator>
</transmission>
```

## Best Practices for Humanoid URDFs

1. **Modularity**: Organize complex humanoid models into modules (head, torso, arms, legs)
2. **Realistic parameters**: Use realistic mass and inertia values based on actual robot
3. **Consistent naming**: Use consistent naming conventions for links and joints
4. **Documentation**: Comment your URDF for maintainability
5. **Validation**: Regularly validate your URDF to catch errors early

## Chapter Summary

This chapter covered the fundamentals of URDF for describing humanoid robots. We learned about the basic structure of URDF files, how to define links and joints, special considerations for humanoid robots, how to use Xacro for complex descriptions, and how to integrate with simulation environments like Gazebo. Proper robot description is crucial for successful humanoid robotics applications.

## Checklist

- [ ] Understand the structure of URDF files
- [ ] Create links with appropriate inertial, visual, and collision properties
- [ ] Implement various joint types with appropriate limits
- [ ] Use Xacro for complex humanoid descriptions
- [ ] Validate URDF files for correctness
- [ ] Integrate with simulation environments like Gazebo

## Exercises

### Exercise 1: Simple Humanoid Model

Create a simple humanoid model with a torso, head, two arms, and two legs using URDF.

#### Solution

1. Define a base link (torso)
2. Add head, arms, and legs as separate links
3. Connect them with appropriate joints
4. Add visual, collision, and inertial properties

#### Hints

- Use cylindrical shapes for limbs
- Set appropriate joint limits
- Consider the kinematic structure of a humanoid

### Exercise 2: Xacro Implementation

Convert your simple humanoid model to use Xacro for better organization.

#### Solution

1. Create macros for repeated elements (arms, legs)
2. Use variables for consistent dimensions
3. Include separate files for different body parts

#### Hints

- Use macros to avoid repetition
- Parameterize your macros for flexibility
- Organize files logically

## References

- [URDF/XML Documentation](http://wiki.ros.org/urdf/XML)
- [Xacro Documentation](http://wiki.ros.org/xacro)
- [Working with URDF in Gazebo](http://gazebosim.org/tutorials/?tut=ros_urdf)
- [Robotics ABCs: URDF](https://www.clearpathrobotics.com/assets/guides/kinetic/melodic/urdf.html)