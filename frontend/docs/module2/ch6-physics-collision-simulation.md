---
title: 'Chapter 6 - Physics, Gravity, and Collision Simulation'
description: 'Advanced physics simulation for humanoid robots in Gazebo'
---

# Chapter 6: Physics, Gravity, and Collision Simulation

## Learning Objectives

After reading this chapter, you will be able to:
- Configure realistic physics parameters for humanoid robots
- Understand collision detection and response mechanisms
- Implement proper gravity simulation for different environments
- Model complex interactions like contacts and friction
- Optimize physics simulation for real-time performance
- Debug physics-related issues in simulation
- Validate physical behavior against real-world expectations
- Handle edge cases like balance and stability in simulation

## Introduction

Physics simulation is the backbone of realistic robot simulation. For humanoid robots, accurately modeling physics is essential for developing controllers, testing behaviors, and understanding how robots will behave in the real world. This chapter covers the physics engine configuration, collision systems, and how to achieve realistic simulation of physical interactions that humanoid robots experience.

## Physics Engine Fundamentals

### Understanding Physics Simulation

Physics simulation in Gazebo involves several systems working together:

1. **Collision Detection**: Identifying when objects intersect
2. **Contact Calculation**: Determining response forces at contact points
3. **Dynamics Integration**: Updating positions and velocities based on forces
4. **Constraint Solving**: Maintaining joint and contact constraints

### Core Physics Parameters

The physics engine in Gazebo has several key parameters that affect simulation realism:

```xml
<physics name="default_physics" type="ode">
  <!-- Time stepping parameters -->
  <max_step_size>0.001</max_step_size>  <!-- Simulation step size (seconds) -->
  <real_time_factor>1</real_time_factor>  <!-- Real-time simulation factor -->
  <real_time_update_rate>1000</real_time_update_rate>  <!-- Updates per sec -->
  
  <!-- Gravity -->
  <gravity>0 0 -9.8</gravity>  <!-- Earth gravity: 9.8 m/s^2 downward -->
  
  <!-- Physics engine specific parameters -->
  <ode>
    <solver>
      <type>quick</type>  <!-- Type of solver (quick, PGS, etc.) -->
      <iters>100</iters>  <!-- Number of iterations for constraint solving -->
      <sor>1.3</sor>      <!-- Successive over-relaxation parameter -->
    </solver>
    <constraints>
      <cfm>0.0</cfm>  <!-- Constraint force mixing parameter -->
      <erp>0.2</erp>  <!-- Error reduction parameter (0-1) -->
      <!-- Maximum correcting velocity for contacts -->
      <contact_max_correcting_vel>100.0</contact_max_correcting_vel>
      <!-- Contact surface layer thickness -->
      <contact_surface_layer>0.001</contact_surface_layer>
    </constraints>
  </ode>
</physics>
```

### Time Step Considerations

The simulation time step is critical for stability:

- **Smaller time steps**: More accurate but computationally expensive
- **Larger time steps**: Faster but potentially unstable
- **Recommended**: 0.001s (1ms) for precise humanoid simulation
- **Maximum**: 0.01s (10ms) for real-time performance

```xml
<!-- For precise humanoid control (e.g., balance) -->
<max_step_size>0.001</max_step_size>
<real_time_update_rate>1000</real_time_update_rate>

<!-- For faster simulation with less precision -->
<max_step_size>0.01</max_step_size>
<real_time_update_rate>100</real_time_update_rate>
```

## Collision Detection Systems

### Types of Collisions

Gazebo supports different collision detection methods:

1. **Surface-based**: Contacts between surfaces
2. **Ray-based**: Ray intersections for sensor simulation
3. **Point-based**: Discrete point contacts

### Collision Properties

Properly configured collision properties are essential for realistic simulation:

```xml
<!-- Example collision configuration -->
<collision name="collision">
  <geometry>
    <box>
      <size>0.2 0.1 0.3</size>
    </box>
  </geometry>
  
  <!-- Surface properties -->
  <surface>
    <friction>
      <ode>
        <mu>0.5</mu>      <!-- Static friction coefficient -->
        <mu2>0.4</mu2>    <!-- Dynamic friction coefficient -->
        <fdir1>1 0 0</fdir1>  <!-- Direction of friction -->
        <slip1>0.0</slip1>    <!-- Primary slip coefficient -->
        <slip2>0.0</slip2>    <!-- Secondary slip coefficient -->
      </ode>
    </friction>
    
    <bounce>
      <restitution_coefficient>0.1</restitution_coefficient>
      <threshold>100000.0</threshold>
    </bounce>
    
    <contact>
      <ode>
        <soft_erp>0.2</soft_erp>              <!-- Contact error reduction -->
        <soft_cfm>0.000001</soft_cfm>         <!-- Contact constraint force mixing -->
        <kp>1000000000000.0</kp>              <!-- Contact stiffness -->
        <kd>1000000000000.0</kd>              <!-- Contact damping -->
        <max_vel>100.0</max_vel>              <!-- Maximum contact correction velocity -->
        <min_depth>0.001</min_depth>          <!-- Penetration depth tolerance -->
        <max_contacts>20</max_contacts>        <!-- Maximum contacts per collision -->
      </ode>
    </contact>
  </surface>
</collision>
```

### Collision Geometry Selection

Choosing the right collision geometry is important for both accuracy and performance:

```xml
<!-- For simple objects, use basic primitives -->
<collision name="simple_collision">
  <geometry>
    <cylinder>
      <radius>0.1</radius>
      <length>0.3</length>
    </cylinder>
  </geometry>
</collision>

<!-- For complex shapes, use convex hull decomposition -->
<collision name="complex_collision">
  <geometry>
    <mesh>
      <uri>file://meshes/complex_part.stl</uri>
      <scale>1.0 1.0 1.0</scale>
    </mesh>
  </geometry>
</collision>

<!-- For performance, use simplified collision meshes -->
<collision name="simplified_collision">
  <geometry>
    <mesh>
      <uri>file://meshes/complex_part_simple_collision.stl</uri>
      <scale>1.0 1.0 1.0</scale>
    </mesh>
  </geometry>
</collision>
```

## Gravity Configuration

### Gravity in Different Environments

While Earth's gravity is approximately 9.8 m/s², different environments may require different gravitational settings:

```xml
<!-- Standard Earth gravity -->
<gravity>0 0 -9.8</gravity>

<!-- Moon gravity (~1/6 of Earth) -->
<gravity>0 0 -1.62</gravity>

<!-- Mars gravity -->
<gravity>0 0 -3.71</gravity>

<!-- Zero gravity (for space simulation) -->
<gravity>0 0 0</gravity>

<!-- Custom gravity vector (for simulation of accelerating frames) -->
<gravity>0 -9.8 0</gravity>  <!-- Horizontal gravity -->
```

### Gravity Considerations for Humanoid Robots

Gravity is particularly important for humanoid robots because:

1. **Balance Control**: Critical for maintaining upright posture
2. **Locomotion**: Affects walking dynamics and gait stability
3. **Manipulation**: Influences how objects behave during manipulation
4. **Energy Consumption**: Affects required actuator forces

```xml
<!-- Advanced gravity configuration for humanoid testing -->
<world name="humanoid_test_world">
  <include>
    <uri>model://ground_plane</uri>
  </include>
  
  <gravity>0 0 -9.8</gravity>  <!-- Standard Earth gravity -->
  
  <physics name="humanoid_physics" type="ode">
    <max_step_size>0.001</max_step_size>
    <real_time_factor>1</real_time_factor>
    <real_time_update_rate>1000</real_time_update_rate>
    
    <ode>
      <solver>
        <type>quick</type>
        <iters>100</iters>
        <sor>1.3</sor>
      </solver>
      <constraints>
        <cfm>0.000001</cfm>
        <erp>0.2</erp>
        <contact_max_correcting_vel>100.0</contact_max_correcting_vel>
        <contact_surface_layer>0.001</contact_surface_layer>
      </constraints>
    </ode>
  </physics>
  
  <!-- Add humanoid robot model here -->
  <include>
    <uri>model://humanoid_robot</uri>
  </include>
</world>
```

## Joint Dynamics and Constraints

### Joint Limit Configuration

Proper joint limits prevent damage and ensure realistic movement:

```xml
<joint name="knee_joint" type="revolute">
  <parent>tibia</parent>
  <child>fibula</child>
  <axis>
    <xyz>0 1 0</xyz>  <!-- Rotation about Y axis -->
    <limit>
      <lower>0.0</lower>      <!-- Fully extended -->
      <upper>2.5</upper>      <!-- Fully bent (143 degrees) -->
      <effort>200.0</effort>  <!-- Maximum torque in N*m -->
      <velocity>3.0</velocity> <!-- Maximum velocity in rad/s -->
    </limit>
    <dynamics>
      <damping>1.0</damping>    <!-- Damping coefficient -->
      <friction>0.5</friction>  <!-- Static friction -->
    </dynamics>
  </axis>
</joint>
```

### Joint Safety Margins

For humanoid robots, it's important to implement safety margins:

```xml
<!-- Soft joint limits to prevent harsh stops -->
<joint name="hip_pitch" type="revolute">
  <parent>pelvis</parent>
  <child>femur</child>
  <axis>
    <xyz>1 0 0</xyz>
    <limit>
      <lower>-1.0</lower>  <!-- Lower hard limit -->
      <upper>0.8</upper>   <!-- Upper hard limit -->
      <effort>300.0</effort>
      <velocity>2.0</velocity>
    </limit>
    <safety_controller>
      <k_position>10</k_position>    <!-- Position gain -->
      <k_velocity>1</k_velocity>     <!-- Velocity gain -->
      <soft_lower_limit>-0.9</soft_lower_limit>  <!-- Soft limit before hard limit -->
      <soft_upper_limit>0.7</soft_upper_limit>   <!-- Soft limit before hard limit -->
    </safety_controller>
    <dynamics>
      <damping>2.0</damping>
      <friction>1.0</friction>
    </dynamics>
  </axis>
</joint>
```

## Collision Handling and Contact Simulation

### Contact Properties

Contacts between surfaces are critical for humanoid robots, especially for walking and manipulation:

```xml
<link name="foot_link">
  <collision name="foot_collision">
    <geometry>
      <box>
        <size>0.15 0.08 0.01</size>  <!-- Flat foot for stability -->
      </box>
    </geometry>
    
    <surface>
      <friction>
        <ode>
          <mu>0.8</mu>  <!-- High friction for stable standing/walking -->
          <mu2>0.8</mu2>
        </ode>
      </friction>
      <contact>
        <ode>
          <soft_erp>0.8</soft_erp>      <!-- Strong contact correction -->
          <soft_cfm>0.0001</soft_cfm>   <!-- Low constraint mixing -->
          <kp>1e+6</kp>                 <!-- High stiffness for firm contact -->
          <kd>1e+4</kd>                 <!-- Medium damping -->
          <max_vel>100.0</max_vel>
          <min_depth>0.001</min_depth>
        </ode>
      </contact>
    </surface>
  </collision>
</link>
```

### Preventing Undesirable Contacts

Sometimes we want to prevent contacts between certain parts:

```xml
<!-- Disable self-collision between adjacent links -->
<joint name="adjacent_joint" type="revolute">
  <parent>link1</parent>
  <child>link2</child>
  <!-- Joint definition -->
  <axis>
    <xyz>0 0 1</xyz>
    <limit>
      <lower>-1.57</lower>
      <upper>1.57</upper>
      <effort>100</effort>
      <velocity>1.0</velocity>
    </limit>
  </axis>
  
  <!-- Don't generate contacts between adjacent links -->
  <disable_collisions>
    <collision1>link1_collision</collision1>
    <collision2>link2_collision</collision2>
    <condition>Adjacent</condition>
  </disable_collisions>
</joint>
```

## Inertial Properties for Humanoid Robots

### Mass Distribution

Accurate inertial properties are crucial for humanoid balance:

```xml
<link name="torso">
  <inertial>
    <mass>5.0</mass>
    <origin xyz="0 0 0.2" rpy="0 0 0"/>
    <inertia>
      <ixx>0.2</ixx>
      <ixy>0.0</ixy>
      <ixz>0.0</ixz>
      <iyy>0.2</iyy>
      <iyz>0.0</iyz>
      <izz>0.1</izz>
    </inertia>
  </inertial>
  
  <!-- Visual and collision properties -->
  <visual name="torso_visual">
    <geometry>
      <box size="0.2 0.2 0.4"/>
    </geometry>
    <material name="grey"/>
  </visual>
  
  <collision name="torso_collision">
    <geometry>
      <box size="0.2 0.2 0.4"/>
    </geometry>
  </collision>
</link>
```

### Center of Mass Considerations

For humanoid robots, center of mass location is critical for stability:

```xml
<!-- Head link with high center of mass -->
<link name="head">
  <inertial>
    <mass>1.0</mass>
    <origin xyz="0 0 0.05" rpy="0 0 0"/>  <!-- CoM slightly above center -->
    <inertia>
      <ixx>0.003</ixx>  <!-- Moments of inertia for spherical approximation -->
      <ixy>0.0</ixy>
      <ixz>0.0</ixz>
      <iyy>0.003</iyy>
      <iyz>0.0</iyz>
      <izz>0.003</izz>
    </inertia>
  </inertial>
</link>

<!-- Pelvis link with low center of mass -->
<link name="pelvis">
  <inertial>
    <mass>6.0</mass>
    <origin xyz="0 0 -0.05" rpy="0 0 0"/>  <!-- CoM slightly below center -->
    <inertia>
      <ixx>0.3</ixx>
      <ixy>0.0</ixy>
      <ixz>0.0</ixz>
      <iyy>0.3</iyy>
      <iyz>0.0</iyz>
      <izz>0.2</izz>
    </inertia>
  </inertial>
</link>
```

## Advanced Physics Configurations

### Custom Physics for Special Scenarios

For specific robot behaviors, custom physics configurations may be needed:

```xml
<!-- Physics for walking simulation -->
<physics name="walking_physics" type="ode">
  <max_step_size>0.001</max_step_size>
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
      <cfm>1e-5</cfm>  <!-- Very low constraint force mixing -->
      <erp>0.1</erp>   <!-- Error reduction for tight constraints -->
      <contact_max_correcting_vel>50.0</contact_max_correcting_vel>
      <contact_surface_layer>0.0005</contact_surface_layer>  <!-- Thin layer for precision -->
    </constraints>
  </ode>
</physics>

<!-- Physics for manipulation simulation -->
<physics name="manipulation_physics" type="ode">
  <max_step_size>0.0005</max_step_size>  <!-- Smaller steps for precision -->
  <real_time_factor>0.5</real_time_factor>  <!-- Slower than real-time for accuracy -->
  <real_time_update_rate>2000</real_time_update_rate>
  <gravity>0 0 -9.8</gravity>
  
  <ode>
    <solver>
      <type>quick</type>
      <iters>300</iters>  <!-- Even more iterations for contact precision -->
      <sor>1.2</sor>
    </solver>
    <constraints>
      <cfm>1e-6</cfm>  <!-- Extremely low constraint force mixing -->
      <erp>0.05</erp>  <!-- Aggressive error correction -->
      <contact_max_correcting_vel>10.0</contact_max_correcting_vel>  <!-- Lower for precision -->
      <contact_surface_layer>0.0001</contact_surface_layer>  <!-- Very thin layer -->
    </constraints>
  </ode>
</physics>
```

## Performance Optimization

### Physics Optimization Strategies

For real-time humanoid simulation with complex physics:

1. **Tune Solver Parameters**: Balance between accuracy and speed
2. **Use Appropriate Collision Geometries**: Simplify where possible
3. **Adjust Update Rates**: Match to real sensor/controller rates
4. **Limit Physics Complexities**: Reduce unnecessary computations

```python
# PhysicsOptimizer class to manage different optimization scenarios
class PhysicsOptimizer:
    def __init__(self, gazebo_client):
        self.gazebo_client = gazebo_client
        
        # Different configurations for different scenarios
        self.configurations = {
            'realtime_default': {
                'max_step_size': 0.001,
                'real_time_factor': 1.0,
                'real_time_update_rate': 1000,
                'ode_solver_iters': 100,
                'ode_cfm': 0.000001,
                'ode_erp': 0.2
            },
            'balance_simulation': {
                'max_step_size': 0.0005,
                'real_time_factor': 0.7,
                'real_time_update_rate': 2000,
                'ode_solver_iters': 200,
                'ode_cfm': 0.0000005,
                'ode_erp': 0.1
            },
            'manipulation_simulation': {
                'max_step_size': 0.0002,
                'real_time_factor': 0.5,
                'real_time_update_rate': 5000,
                'ode_solver_iters': 300,
                'ode_cfm': 0.0000001,
                'ode_erp': 0.05
            }
        }
    
    def switch_configuration(self, config_name: str):
        """Switch to a different physics configuration"""
        if config_name not in self.configurations:
            raise ValueError(f"Unknown configuration: {config_name}")
        
        config = self.configurations[config_name]
        
        physics_msg = Physics()
        physics_msg.max_step_size = config['max_step_size']
        physics_msg.real_time_factor = config['real_time_factor']
        physics_msg.real_time_update_rate = config['real_time_update_rate']
        
        # Set ODE-specific parameters if using ODE physics
        physics_msg.ode_config.solver_iterations = config['ode_solver_iters']
        physics_msg.ode_config.contact_surface_layer = config['ode_cfm']
        physics_msg.ode_config.contact_erp = config['ode_erp']
        
        # Apply the physics configuration
        self.gazebo_client.set_physics(physics_msg)
        print(f"Switched to {config_name} physics configuration")
    
    def optimize_for_scenario(self, scenario: str):
        """Optimize physics based on scenario"""
        if scenario == 'walking':
            self.switch_configuration('balance_simulation')
        elif scenario == 'manipulation':
            self.switch_configuration('manipulation_simulation')
        elif scenario == 'exploration':
            self.switch_configuration('realtime_default')
        else:
            print(f"Unknown scenario: {scenario}")