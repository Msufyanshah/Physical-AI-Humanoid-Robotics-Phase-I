---
title: 'Exercise Set 2 - The Digital Twin (Gazebo & Unity)'
description: 'Hands-on exercises for Module 2 covering Gazebo simulation and Unity integration'
---

# Exercise Set 2: The Digital Twin (Gazebo & Unity)

## Learning Objectives

After completing these exercises, you will be able to:
- Set up and configure Gazebo simulation environments for humanoid robots
- Implement realistic physics and collision dynamics
- Simulate various sensor systems (LiDAR, IMU, cameras) with proper noise models
- Integrate Unity for advanced visualization and control interfaces
- Create sensor fusion systems combining multiple modalities
- Validate simulation accuracy against real-world expectations
- Optimize simulation performance for real-time operation
- Debug and troubleshoot simulation problems

## Exercise 1: Custom Gazebo Environment with Physics

Create a custom Gazebo environment with realistic physics configuration for humanoid robot testing.

### Instructions

1. Create a Gazebo world file that includes:
   - A humanoid-sized room with furniture (desks, chairs, obstacles)
   - Proper lighting configuration
   - Physics parameters optimized for humanoid locomotion
   - Collision and surface properties for different materials

2. Implement a humanoid robot model in the environment with:
   - Proper mass distribution and inertial properties
   - Realistic joint limits and dynamics
   - Appropriate friction coefficients

3. Add physics constraints that mimic real-world humanoid interactions

### Solution

#### 1. Create the world file (my_humanoid_world.sdf):

```xml
<?xml version="1.0" ?>
<sdf version="1.7">
  <world name="humanoid_test_world">
    <!-- Ground plane -->
    <include>
      <uri>model://ground_plane</uri>
    </include>
    
    <!-- Sun light -->
    <include>
      <uri>model://sun</uri>
    </include>
    
    <!-- Physics Configuration -->
    <physics name="humanoid_physics" type="ode">
      <max_step_size>0.001</max_step_size>  <!-- High fidelity for balance -->
      <real_time_factor>1</real_time_factor>
      <real_time_update_rate>1000</real_time_update_rate>
      <gravity>0 0 -9.8</gravity>
      
      <ode>
        <solver>
          <type>quick</type>
          <iters>100</iters>  <!-- More iterations for stability -->
          <sor>1.3</sor>
        </solver>
        <constraints>
          <cfm>0.000001</cfm>  <!-- Low constraint force mixing -->
          <erp>0.2</erp>       <!-- Error reduction parameter -->
          <contact_max_correcting_vel>100.0</contact_max_correcting_vel>
          <contact_surface_layer>0.001</contact_surface_layer>
        </constraints>
      </ode>
    </physics>
    
    <!-- Walls of the room -->
    <!-- North Wall -->
    <model name="north_wall">
      <pose>0 5 1.5 0 0 0</pose>
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>10 0.2 3</size>
            </box>
          </geometry>
          <surface>
            <friction>
              <ode>
                <mu>0.5</mu>
                <mu2>0.5</mu2>
              </ode>
            </friction>
          </surface>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>10 0.2 3</size>
            </box>
          </geometry>
          <material>
            <ambient>0.9 0.9 0.9 1</ambient>
            <diffuse>0.9 0.9 0.9 1</diffuse>
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
    
    <!-- South Wall -->
    <model name="south_wall">
      <pose>0 -5 1.5 0 0 0</pose>
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>10 0.2 3</size>
            </box>
          </geometry>
          <surface>
            <friction>
              <ode>
                <mu>0.5</mu>
                <mu2>0.5</mu2>
              </ode>
            </friction>
          </surface>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>10 0.2 3</size>
            </box>
          </geometry>
          <material>
            <ambient>0.9 0.9 0.9 1</ambient>
            <diffuse>0.9 0.9 0.9 1</diffiffe>
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
    
    <!-- West Wall -->
    <model name="west_wall">
      <pose>-5 0 1.5 0 0 0</pose>
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>0.2 10 3</size>
            </box>
          </geometry>
          <surface>
            <friction>
              <ode>
                <mu>0.5</mu>
                <mu2>0.5</mu2>
              </ode>
            </friction>
          </surface>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>0.2 10 3</size>
            </box>
          </geometry>
          <material>
            <ambient>0.9 0.9 0.9 1</ambient>
            <diffuse>0.9 0.9 0.9 1</diffuse>
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
    
    <!-- East Wall -->
    <model name="east_wall">
      <pose>5 0 1.5 0 0 0</pose>
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>0.2 10 3</size>
            </box>
          </geometry>
          <surface>
            <friction>
              <ode>
                <mu>0.5</mu>
                <mu2>0.5</mu2>
              </ode>
            </friction>
          </surface>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>0.2 10 3</size>
            </box>
          </geometry>
          <material>
            <ambient>0.9 0.9 0.9 1</ambient>
            <diffuse>0.9 0.9 0.9 1</diffuse>
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
    
    <!-- Furniture -->
    <!-- Desk -->
    <model name="desk">
      <pose>-2 1 0.75 0 0 0</pose>
      <link name="desk_surface">
        <collision name="collision">
          <geometry>
            <box>
              <size>1.2 0.6 0.05</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>1.2 0.6 0.05</size>
            </box>
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
            <iyy>1.0</iyy>
            <iyz>0</iyz>
            <izz>1.5</izz>
          </inertia>
        </inertial>
      </link>
      
      <link name="desk_leg1">
        <pose>-0.5 -0.25 0.35 0 0 0</pose>
        <collision name="collision">
          <geometry>
            <cylinder>
              <radius>0.05</radius>
              <length>0.7</length>
            </cylinder>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <cylinder>
              <radius>0.05</radius>
              <length>0.7</length>
            </cylinder>
          </geometry>
          <material>
            <ambient>0.5 0.5 0.5 1</ambient>
            <diffuse>0.5 0.5 0.5 1</diffuse>
          </material>
        </visual>
        <inertial>
          <mass>2.0</mass>
          <inertia>
            <ixx>0.1</ixx>
            <ixy>0</ixy>
            <ixz>0</ixz>
            <iyy>0.1</iyy>
            <iyz>0</iyz>
            <izz>0.01</izz>
          </inertia>
        </inertial>
      </link>
      
      <joint name="surface_to_leg1" type="fixed">
        <parent>desk_surface</parent>
        <child>desk_leg1</child>
        <pose>-0.5 -0.25 -0.4 0 0 0</pose>
      </joint>
      
      <!-- Add more desk legs similarly -->
    </model>
    
    <!-- Chair (simplified) -->
    <model name="chair">
      <pose>-2 1.5 0.4 0 0 0</pose>
      <link name="seat">
        <collision name="collision">
          <geometry>
            <box>
              <size>0.4 0.4 0.05</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>0.4 0.4 0.05</size>
            </box>
          </geometry>
          <material>
            <ambient>0.8 0.8 0.8 1</ambient>
            <diffuse>0.8 0.8 0.8 1</diffuse>
          </material>
        </visual>
        <inertial>
          <mass>3.0</mass>
          <inertia>
            <ixx>0.2</ixx>
            <ixy>0</ixy>
            <ixz>0</ixz>
            <iyy>0.2</iyy>
            <iyz>0</iyz>
            <izz>0.3</izz>
          </inertia>
        </inertial>
      </link>
    </model>
  </world>
</sdf>
```

#### 2. Create the humanoid robot model (simplified version):

```xml
<sdf version="1.7">
  <model name="simple_humanoid">
    <pose>0 0 0.85 0 0 0</pose>
    
    <!-- Torso (base link) -->
    <link name="torso">
      <pose>0 0 0.85 0 0 0</pose>
      <inertial>
        <mass>10.0</mass>
        <origin xyz="0 0 0.2" rpy="0 0 0"/>
        <inertia>
          <ixx>0.8</ixx>
          <ixy>0</ixy>
          <ixz>0</ixz>
          <iyy>0.8</iyy>
          <iyz>0</iyz>
          <izz>0.5</izz>
        </inertia>
      </inertial>
      
      <collision name="collision">
        <geometry>
          <box>
            <size>0.3 0.25 0.5</size>
          </box>
        </geometry>
      </collision>
      
      <visual name="visual">
        <geometry>
          <box>
            <size>0.3 0.25 0.5</size>
          </box>
        </geometry>
        <material>
          <ambient>0.5 0.5 1.0 1</ambient>
          <diffuse>0.5 0.5 1.0 1</diffuse>
        </material>
      </visual>
    </link>
    
    <!-- Head -->
    <joint name="neck_joint" type="revolute">
      <parent>torso</parent>
      <child>head</child>
      <pose>0 0 0.4 0 0 0</pose>
      <axis>
        <xyz>0 1 0</xyz>
        <limit>
          <lower>-0.5</lower>
          <upper>0.5</upper>
          <effort>50</effort>
          <velocity>1.0</velocity>
        </limit>
        <dynamics>
          <damping>1.0</damping>
          <friction>0.1</friction>
        </dynamics>
      </axis>
    </joint>
    
    <link name="head">
      <inertial>
        <mass>2.0</mass>
        <origin xyz="0 0 0.05" rpy="0 0 0"/>
        <inertia>
          <ixx>0.02</ixx>
          <ixy>0</ixy>
          <ixz>0</ixz>
          <iyy>0.02</iyy>
          <iyz>0</iyz>
          <izz>0.02</izz>
        </inertia>
      </inertial>
      
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
          <ambient>0.9 0.9 0.9 1</ambient>
          <diffuse>0.9 0.9 0.9 1</diffuse>
        </material>
      </visual>
    </link>
    
    <!-- Left Arm -->
    <joint name="left_shoulder" type="revolute">
      <parent>torso</parent>
      <child>left_upper_arm</child>
      <pose>0.05 0.15 0.3 0 0 0</pose>
      <axis>
        <xyz>0 1 0</xyz>
        <limit>
          <lower>-1.57</lower>
          <upper>1.57</upper>
          <effort>30</effort>
          <velocity>1.0</velocity>
        </limit>
      </axis>
    </joint>
    
    <link name="left_upper_arm">
      <inertial>
        <mass>1.0</mass>
        <origin xyz="0 0 -0.1" rpy="0 0 0"/>
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
          <cylinder>
            <radius>0.05</radius>
            <length>0.2</length>
          </cylinder>
        </geometry>
      </collision>
      
      <visual name="visual">
        <geometry>
          <cylinder>
            <radius>0.05</radius>
            <length>0.2</length>
          </cylinder>
        </geometry>
        <material>
          <ambient>1.0 0.5 0.5 1</ambient>
          <diffuse>1.0 0.5 0.5 1</diffuse>
        </material>
      </visual>
    </link>
    
    <!-- Left Elbow Joint -->
    <joint name="left_elbow" type="revolute">
      <parent>left_upper_arm</parent>
      <child>left_lower_arm</child>
      <pose>0 0 -0.2 0 0 0</pose>
      <axis>
        <xyz>1 0 0</xyz>
        <limit>
          <lower>0</lower>
          <upper>2.5</upper>
          <effort>25</effort>
          <velocity>1.0</velocity>
        </limit>
        <dynamics>
          <damping>0.8</damping>
          <friction>0.1</friction>
        </dynamics>
      </axis>
    </joint>
    
    <link name="left_lower_arm">
      <inertial>
        <mass>0.7</mass>
        <origin xyz="0 0 -0.08" rpy="0 0 0"/>
        <inertia>
          <ixx>0.005</ixx>
          <ixy>0</ixy>
          <ixz>0</ixz>
          <iyy>0.005</iyy>
          <iyz>0</iyz>
          <izz>0.003</izz>
        </inertia>
      </inertial>
      
      <collision name="collision">
        <geometry>
          <cylinder>
            <radius>0.04</radius>
            <length>0.16</length>
          </cylinder>
        </geometry>
      </collision>
      
      <visual name="visual">
        <geometry>
          <cylinder>
            <radius>0.04</radius>
            <length>0.16</length>
          </cylinder>
        </geometry>
        <material>
          <ambient>1.0 0.5 0.5 1</ambient>
          <diffuse>1.0 0.5 0.5 1</diffuse>
        </material>
      </visual>
    </link>
    
    <!-- Left Hand -->
    <joint name="left_wrist" type="revolute">
      <parent>left_lower_arm</parent>
      <child>left_hand</child>
      <pose>0 0 -0.16 0 0 0</pose>
      <axis>
        <xyz>0 1 0</xyz>
        <limit>
          <lower>-1.57</lower>
          <upper>1.57</upper>
          <effort>15</effort>
          <velocity>1.0</velocity>
        </limit>
        <dynamics>
          <damping>0.5</damping>
          <friction>0.05</friction>
        </dynamics>
      </axis>
    </joint>
    
    <link name="left_hand">
      <inertial>
        <mass>0.3</mass>
        <origin xyz="0 0 -0.05" rpy="0 0 0"/>
        <inertia>
          <ixx>0.001</ixx>
          <ixy>0</ixy>
          <ixz>0</ixz>
          <iyy>0.001</iyy>
          <iyz>0</iyz>
          <izz>0.001</izz>
        </inertia>
      </inertial>
      
      <collision name="collision">
        <geometry>
          <box>
            <size>0.08 0.1 0.06</size>
          </box>
        </geometry>
      </collision>
      
      <visual name="visual">
        <geometry>
          <box>
            <size>0.08 0.1 0.06</size>
          </box>
        </geometry>
        <material>
          <ambient>1.0 0.7 0.7 1</ambient>
          <diffuse>1.0 0.7 0.7 1</diffuse>
        </material>
      </visual>
    </link>
    
    <!-- Add similar joints for right arm, legs, etc. -->
  </model>
</sdf>
```

#### 3. Physics validation script

```python
# validate_physics_simulation.py
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Point
from sensor_msgs.msg import JointState
import time
import numpy as np


class PhysicsValidationNode(Node):
    """Node to validate physics simulation for humanoid robot"""
    
    def __init__(self):
        super().__init__('physics_validation')
        
        # Subscribe to joint states to monitor physics behavior
        self.joint_state_sub = self.create_subscription(
            JointState, 
            '/joint_states', 
            self.joint_state_callback, 
            10
        )
        
        # Subscribe to robot pose/odometry
        self.robot_pose_sub = self.create_subscription(
            Point, 
            '/robot_position', 
            self.pose_callback, 
            10
        )
        
        # Publisher for validation results
        self.validation_pub = self.create_publisher(String, '/physics_validation_results', 10)
        
        # Store historical data for analysis
        self.joint_history = {}
        self.pose_history = []
        
        # Physics validation parameters
        self.stability_threshold = 0.1  # meters of deviation from expected pose
        self.balance_threshold = 15.0  # degrees of tilt before considering unbalanced
        
        self.get_logger().info("Physics validation node initialized")
    
    def joint_state_callback(self, msg):
        """Process joint state messages"""
        for i, name in enumerate(msg.name):
            if i < len(msg.position):
                # Store joint position history
                if name not in self.joint_history:
                    self.joint_history[name] = {'positions': [], 'velocities': [], 'timestamps': []}
                
                self.joint_history[name]['positions'].append(msg.position[i])
                if i < len(msg.velocity):
                    self.joint_history[name]['velocities'].append(msg.velocity[i])
                self.joint_history[name]['timestamps'].append(self.get_clock().now().nanoseconds / 1e9)
    
    def pose_callback(self, msg):
        """Process robot pose messages"""
        self.pose_history.append({
            'position': {'x': msg.x, 'y': msg.y, 'z': msg.z},
            'timestamp': self.get_clock().now().nanoseconds / 1e9
        })
    
    def validate_stability(self) -> dict:
        """Validate robot stability based on pose history"""
        if len(self.pose_history) < 2:
            return {"valid": False, "reason": "Insufficient pose data"}
        
        # Calculate movement statistics
        positions = [p['position'] for p in self.pose_history[-10:]]  # Last 10 samples
        
        if len(positions) > 1:
            # Calculate velocity
            time_diffs = []
            for i in range(1, len(positions)):
                time_diffs.append(
                    self.pose_history[-len(positions)+i]['timestamp'] - 
                    self.pose_history[-len(positions)+i-1]['timestamp']
                )
            
            if time_diffs:
                avg_dt = np.mean(time_diffs)
                if avg_dt > 0:
                    # Calculate velocity (simplified)
                    dx = positions[-1]['x'] - positions[-2]['x']
                    dy = positions[-1]['y'] - positions[-2]['y']
                    dz = positions[-1]['z'] - positions[-2]['z']
                    dt = time_diffs[-1]
                    
                    velocity = np.sqrt((dx**2 + dy**2 + dz**2)) / avg_dt
                    
                    # Check for excessive movement (indicating instability)
                    max_stable_velocity = 2.0  # m/s threshold for humanoid stability
                    is_stable = velocity < max_stable_velocity
                    
                    return {
                        "valid": is_stable,
                        "velocity": velocity,
                        "average_dt": avg_dt,
                        "reason": "Robot moving too fast" if not is_stable else "Robot is stable"
                    }
        
        return {"valid": True, "reason": "Insufficient data for velocity calculation"}
    
    def validate_joint_dynamics(self) -> dict:
        """Validate joint dynamics based on historical data"""
        results = {}
        
        for joint_name, history in self.joint_history.items():
            if len(history['positions']) > 1:
                # Calculate joint velocity and acceleration
                positions = history['positions']
                timestamps = history['timestamps']
                
                velocities = []
                accelerations = []
                
                for i in range(1, len(positions)):
                    dt = timestamps[i] - timestamps[i-1]
                    if dt > 0:
                        vel = (positions[i] - positions[i-1]) / dt
                        velocities.append(vel)
                
                for i in range(1, len(velocities)):
                    dt = timestamps[i+1] - timestamps[i]
                    if dt > 0:
                        acc = (velocities[i] - velocities[i-1]) / dt
                        accelerations.append(acc)
                
                # Validate against expected ranges
                max_velocity = 5.0  # rad/s
                max_acceleration = 100.0  # rad/s²
                
                if velocities:
                    max_vel = max(abs(v) for v in velocities)
                    results[joint_name] = {
                        "max_velocity": max_vel,
                        "within_limits": max_vel <= max_velocity,
                        "valid": max_vel <= max_velocity
                    }
                
                if accelerations:
                    max_acc = max(abs(a) for a in accelerations)
                    if joint_name in results:
                        results[joint_name]["max_acceleration"] = max_acc
                        results[joint_name]["acceleration_valid"] = max_acc <= max_acceleration
                        results[joint_name]["valid"] = results[joint_name]["valid"] and (max_acc <= max_acceleration)
                    else:
                        results[joint_name] = {
                            "max_acceleration": max_acc,
                            "acceleration_valid": max_acc <= max_acceleration,
                            "valid": max_acc <= max_acceleration
                        }
        
        return results
    
    def run_physics_validation(self):
        """Run comprehensive physics validation"""
        stability_result = self.validate_stability()
        joint_result = self.validate_joint_dynamics()
        
        # Overall assessment
        overall_valid = stability_result["valid"]
        
        for joint_valid in joint_result.values():
            if "valid" in joint_valid:
                overall_valid = overall_valid and joint_valid["valid"]
        
        validation_report = {
            "timestamp": self.get_clock().now().nanoseconds / 1e9,
            "stability": stability_result,
            "joints": joint_result,
            "overall_valid": overall_valid
        }
        
        # Publish validation report
        report_msg = String()
        report_msg.data = str(validation_report)
        self.validation_pub.publish(report_msg)
        
        return validation_report


def main(args=None):
    rclpy.init(args=args)
    validator = PhysicsValidationNode()
    
    # Run validation periodically
    timer = validator.create_timer(2.0, validator.run_physics_validation)
    
    try:
        rclpy.spin(validator)
    except KeyboardInterrupt:
        validator.get_logger().info("Physics validation node shutting down...")
    finally:
        validator.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### Hints

- Use realistic inertial properties based on actual robot specifications
- Pay attention to joint limits that prevent robot damage
- Adjust friction coefficients to match real surfaces
- Verify physics simulation matches expected real-world behavior

## Exercise 2: LiDAR and IMU Sensor Simulation

Configure and test realistic sensor simulation for humanoid navigation and localization.

### Instructions

1. Implement realistic LiDAR sensor configuration with proper noise models
2. Configure IMU simulation with appropriate drift and noise characteristics
3. Create a sensor fusion node to combine LiDAR and IMU data
4. Validate sensor simulation accuracy against expected values
5. Test the sensor integration with localization algorithms

### Solution

#### 1. LiDAR configuration with realistic parameters

```xml
<sensor name="humanoid_lidar" type="ray">
  <pose>0.1 0 0.8 0 0 0</pose>  <!-- Mounted on head/torso -->
  <ray>
    <scan>
      <horizontal>
        <samples>360</samples>
        <resolution>1</resolution>
        <min_angle>-3.14159</min_angle>  <!-- -π radians (-180°) -->
        <max_angle>3.14159</max_angle>   <!-- π radians (180°) -->
      </horizontal>
    </scan>
    <range>
      <min>0.1</min>     <!-- 10cm minimum range -->
      <max>10.0</max>    <!-- 10m maximum range -->
      <resolution>0.01</resolution>  <!-- 1cm resolution -->
    </range>
    <noise>
      <type>gaussian</type>
      <mean>0.0</mean>
      <stddev>0.01</stddev>  <!-- 1cm standard deviation -->
    </noise>
  </ray>
  <always_on>1</always_on>
  <update_rate>10</update_rate>
  <visualize>true</visualize>
  
  <!-- ROS 2 plugin for integration -->
  <plugin name="lidar_controller" filename="libgazebo_ros_ray_sensor.so">
    <ros>
      <namespace>/laser</namespace>
      <remapping>~/out:=scan</remapping>
    </ros>
    <output_type>sensor_msgs/LaserScan</output_type>
    <frame_name>laser_frame</frame_name>
    <min_intensity>0.1</min_intensity>
  </plugin>
</sensor>
```

#### 2. IMU configuration with realistic parameters

```xml
<sensor name="humanoid_imu" type="imu">
  <pose>0 0 0.3 0 0 0</pose>  <!-- Center of mass location -->
  <always_on>true</always_on>
  <update_rate>100</update_rate>
  <imu>
    <!-- Angular velocity noise (gyroscope) -->
    <angular_velocity>
      <x>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>0.01</stddev>       <!-- 0.01 rad/s standard deviation -->
          <bias_mean>0.0</bias_mean>
          <bias_stddev>0.001</bias_stddev>  <!-- 0.001 rad/s bias drift -->
        </noise>
      </x>
      <y>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>0.01</stddev>
          <bias_mean>0.0</bias_mean>
          <bias_stddev>0.001</bias_stddev>
        </noise>
      </y>
      <z>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>0.01</stddev>
          <bias_mean>0.0</bias_mean>
          <bias_stddev>0.001</bias_stddev>
        </noise>
      </z>
    </angular_velocity>
    
    <!-- Linear acceleration noise (accelerometer) -->
    <linear_acceleration>
      <x>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>0.017</stddev>      <!-- 0.017 m/s² standard deviation -->
          <bias_mean>0.0</bias_mean>
          <bias_stddev>0.005</bias_stddev>  <!-- 0.005 m/s² bias drift -->
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
  
  <!-- ROS 2 plugin for integration -->
  <plugin name="imu_controller" filename="libgazebo_ros_imu_sensor.so">
    <ros>
      <namespace>/imu</namespace>
      <remapping>~/out:=data</remapping>
    </ros>
    <frame_name>imu_frame</frame_name>
    <body_name>torso</body_name>
    <update_rate>100</update_rate>
  </plugin>
</sensor>
```

#### 3. Sensor fusion node

```python
# sensor_fusion.py
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan, Imu
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Pose, Point, Quaternion
from tf2_ros import TransformBroadcaster
import numpy as np
import scipy.signal as signal
from scipy.spatial.transform import Rotation as R
from collections import deque


class SensorFusionNode(Node):
    """Fuses LiDAR and IMU data for improved localization and perception"""
    
    def __init__(self):
        super().__init__('sensor_fusion')
        
        # Subscribers
        self.lidar_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.lidar_callback,
            10
        )
        
        self.imu_sub = self.create_subscription(
            Imu,
            '/imu/data',
            self.imu_callback,
            10
        )
        
        # Publisher for fused data
        self.odom_pub = self.create_publisher(Odometry, '/fused_odom', 10)
        self.filtered_imu_pub = self.create_publisher(Imu, '/filtered_imu', 10)
        
        # Transform broadcaster
        self.tf_broadcaster = TransformBroadcaster(self)
        
        # Internal state
        self.position = np.array([0.0, 0.0, 0.0])
        self.orientation = np.array([0.0, 0.0, 0.0, 1.0])  # quaternion
        self.velocity = np.array([0.0, 0.0, 0.0])
        self.angular_velocity = np.array([0.0, 0.0, 0.0])
        
        # Buffers for fusion
        self.imu_buffer = deque(maxlen=10)  # Keep last 10 IMU readings
        self.odom_buffer = deque(maxlen=5)  # Keep last 5 odometry estimates
        
        # Fusion parameters
        self.lidar_weight = 0.1    # How much to trust LiDAR over IMU for position
        self.imu_weight = 0.9     # How much to trust IMU for orientation
        self.process_noise = 0.1  # Process noise for fusion
        self.measurement_noise = 0.1  # Measurement noise
        
        self.get_logger().info("Sensor fusion node initialized")
    
    def lidar_callback(self, msg):
        """Process LiDAR measurements for localization"""
        # Convert laser scan to 2D pose estimates (simplified for this example)
        # In practice, you'd use more sophisticated methods like AMCL or particle filters
        
        # Extract features from laser scan (simplified)
        # This would normally involve landmark detection or scan matching
        range_sum = sum(r for r in msg.ranges if not np.isinf(r) and not np.isnan(r))
        valid_ranges = [r for r in msg.ranges if not np.isinf(r) and not np.isnan(r)]
        
        if len(valid_ranges) > 100:  # If enough valid readings
            # Update position estimate based on features
            # For this example, just use a simple displacement estimate
            displacement_estimate = self.estimate_displacement_from_scan(msg)
            
            # Apply LiDAR position update with weight
            self.position[:2] = self.position[:2] * (1 - self.lidar_weight) + displacement_estimate * self.lidar_weight
    
    def estimate_displacement_from_scan(self, scan_msg):
        """Estimate displacement based on laser scan (simplified)"""
        # In practice, this would use scan matching or feature tracking
        # For this example, return a zero displacement (no movement)
        return self.position[:2]  # No movement estimate
    
    def imu_callback(self, msg):
        """Process IMU measurements for orientation and acceleration"""
        # Extract orientation from IMU quaternion
        imu_quat = np.array([
            msg.orientation.x,
            msg.orientation.y,
            msg.orientation.z,
            msg.orientation.w
        ])
        
        # Extract angular velocity from IMU
        imu_angular_vel = np.array([
            msg.angular_velocity.x,
            msg.angular_velocity.y,
            msg.angular_velocity.z
        ])
        
        # Store in buffer for smoothing
        self.imu_buffer.append({
            'orientation': imu_quat,
            'angular_velocity': imu_angular_vel,
            'linear_acceleration': np.array([
                msg.linear_acceleration.x,
                msg.linear_acceleration.y,
                msg.linear_acceleration.z
            ]),
            'timestamp': msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        })
        
        # Fuse IMU data with current estimate
        fused_orientation = self.fuse_orientations_with_imu(imu_quat)
        
        # Update orientation using weighted fusion
        self.orientation = self.orientation * (1 - self.imu_weight) + fused_orientation * self.imu_weight
        # Normalize quaternion
        self.orientation = self.orientation / np.linalg.norm(self.orientation)
        
        # Integrate angular velocity to update angular velocity
        dt = 0.01  # Assuming 100Hz IMU
        self.angular_velocity = self.angular_velocity * 0.9 + imu_angular_vel * 0.1  # Simple smoothing
    
    def fuse_orientations_with_imu(self, imu_orientation):
        """Fuse current orientation estimate with IMU measurement"""
        # Implement complementary filter to combine Gyro and Accelerometer
        # For now, return the IMU orientation
        return imu_orientation
    
    def integrate_imu_data(self, imu_data_list):
        """Integrate IMU data to estimate position change"""
        # Integrate linear acceleration to get velocity
        # Integrate velocity to get position
        # This is a simplified integration (in practice, would need more sophisticated filtering)
        
        dt = 0.01  # 100Hz IMU readings
        velocity_change = np.zeros(3)
        position_change = np.zeros(3)
        
        for i in range(1, len(imu_data_list)):
            accel = imu_data_list[i]['linear_acceleration']
            vel_change = accel * dt
            velocity_change += vel_change
            pos_change = velocity_change * dt
            position_change += pos_change
        
        return position_change
    
    def publish_fused_odometry(self):
        """Publish fused odometry estimate"""
        odom_msg = Odometry()
        odom_msg.header.stamp = self.get_clock().now().to_msg()
        odom_msg.header.frame_id = 'map'
        odom_msg.child_frame_id = 'base_link'
        
        # Set position
        odom_msg.pose.pose.position.x = float(self.position[0])
        odom_msg.pose.pose.position.y = float(self.position[1])
        odom_msg.pose.pose.position.z = float(self.position[2])
        
        # Set orientation
        odom_msg.pose.pose.orientation.x = float(self.orientation[0])
        odom_msg.pose.pose.orientation.y = float(self.orientation[1])
        odom_msg.pose.pose.orientation.z = float(self.orientation[2])
        odom_msg.pose.pose.orientation.w = float(self.orientation[3])
        
        # Set velocities
        odom_msg.twist.twist.linear.x = float(self.velocity[0])
        odom_msg.twist.twist.linear.y = float(self.velocity[1])
        odom_msg.twist.twist.linear.z = float(self.velocity[2])
        
        odom_msg.twist.twist.angular.x = float(self.angular_velocity[0])
        odom_msg.twist.twist.angular.y = float(self.angular_velocity[1])
        odom_msg.twist.twist.angular.z = float(self.angular_velocity[2])
        
        # TODO: Set covariance matrices for proper uncertainty estimates
        # For now, use identity matrices
        odom_msg.pose.covariance = [0.0] * 36
        odom_msg.twist.covariance = [0.0] * 36
        
        self.odom_pub.publish(odom_msg)
        
        # Broadcast transform
        from geometry_msgs.msg import TransformStamped
        t = TransformStamped()
        
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'map'
        t.child_frame_id = 'base_link'
        
        t.transform.translation.x = float(self.position[0])
        t.transform.translation.y = float(self.position[1])
        t.transform.translation.z = float(self.position[2])
        
        t.transform.rotation.x = float(self.orientation[0])
        t.transform.rotation.y = float(self.orientation[1])
        t.transform.rotation.z = float(self.orientation[2])
        t.transform.rotation.w = float(self.orientation[3])
        
        self.tf_broadcaster.sendTransform(t)
    
    def run_sensor_fusion(self):
        """Main fusion algorithm execution"""
        # This would implement more sophisticated fusion like:
        # - Extended Kalman Filter (EKF)
        # - Unscented Kalman Filter (UKF)
        # - Particle Filter
        # For now, just publish current estimate
        
        self.publish_fused_odometry()


def main(args=None):
    rclpy.init(args=args)
    fusion_node = SensorFusionNode()
    
    # Run fusion at 50Hz
    timer = fusion_node.create_timer(0.02, fusion_node.run_sensor_fusion)
    
    try:
        rclpy.spin(fusion_node)
    except KeyboardInterrupt:
        fusion_node.get_logger().info("Sensor fusion node shutting down...")
    finally:
        fusion_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

#### 4. Sensor validation script

```python
# validate_sensors.py
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan, Imu
from std_msgs.msg import String
import numpy as np
from collections import deque
import statistics


class SensorValidationNode(Node):
    """Validates sensor data against expected characteristics"""
    
    def __init__(self):
        super().__init__('sensor_validation')
        
        # Subscribers for sensor data
        self.lidar_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.lidar_callback,
            10
        )
        
        self.imu_sub = self.create_subscription(
            Imu,
            '/imu/data',
            self.imu_callback,
            10
        )
        
        # Publisher for validation results
        self.validation_pub = self.create_publisher(String, '/sensor_validation', 10)
        
        # Data buffers for validation
        self.lidar_buffers = deque(maxlen=30)  # 30 scans (3 seconds at 10Hz)
        self.imu_buffers = {
            'angular_velocity': deque(maxlen=300),  # 300 readings (3 seconds at 100Hz)
            'linear_acceleration': deque(maxlen=300),
            'orientation': deque(maxlen=300)
        }
        
        # Validation parameters
        self.valid_ranges_expected = (0.1, 10.0)  # Expected range values in meters
        self.valid_imu_drift_threshold = 0.1  # Radians for orientation drift
        
        # Timer for periodic validation reports
        self.validation_timer = self.create_timer(1.0, self.run_validation)
        
        self.get_logger().info("Sensor validation node initialized")
    
    def lidar_callback(self, msg):
        """Process incoming lidar data"""
        self.lidar_buffers.append({
            'ranges': msg.ranges,
            'intensities': msg.intensities,
            'min_range': msg.range_min,
            'max_range': msg.range_max,
            'angle_min': msg.angle_min,
            'angle_max': msg.angle_max,
            'angle_increment': msg.angle_increment,
            'timestamp': msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        })
    
    def imu_callback(self, msg):
        """Process incoming IMU data"""
        self.imu_buffers['angular_velocity'].append({
            'x': msg.angular_velocity.x,
            'y': msg.angular_velocity.y,
            'z': msg.angular_velocity.z,
            'timestamp': msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        })
        
        self.imu_buffers['linear_acceleration'].append({
            'x': msg.linear_acceleration.x,
            'y': msg.linear_acceleration.y,
            'z': msg.linear_acceleration.z,
            'timestamp': msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        })
        
        self.imu_buffers['orientation'].append({
            'x': msg.orientation.x,
            'y': msg.orientation.y,
            'z': msg.orientation.z,
            'w': msg.orientation.w,
            'timestamp': msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        })
    
    def validate_lidar_data(self) -> dict:
        """Validate LiDAR data quality"""
        if not self.lidar_buffers:
            return {"valid": False, "reason": "No LiDAR data received"}
        
        latest_scan = self.lidar_buffers[-1]
        
        # Check range values
        valid_range_count = 0
        total_ranges = 0
        for range_val in latest_scan['ranges']:
            if not np.isinf(range_val) and not np.isnan(range_val):
                total_ranges += 1
                if self.valid_ranges_expected[0] <= range_val <= self.valid_ranges_expected[1]:
                    valid_range_count += 1
        
        # Calculate range validity percentage
        range_validity = valid_range_count / total_ranges if total_ranges > 0 else 0
        
        # Check scan completeness
        expected_points = (latest_scan['angle_max'] - latest_scan['angle_min']) / latest_scan['angle_increment']
        scan_completeness = len(latest_scan['ranges']) / expected_points if expected_points > 0 else 0
        
        # Results
        is_valid = range_validity > 0.9 and scan_completeness > 0.95
        
        return {
            "valid": is_valid,
            "range_validity": range_validity,
            "scan_completeness": scan_completeness,
            "expected_points": expected_points,
            "actual_points": len(latest_scan['ranges']),
            "reason": "LiDAR data quality acceptable" if is_valid else f"Range validity: {range_validity:.2f}, Scan completeness: {scan_completeness:.2f}"
        }
    
    def validate_imu_data(self) -> dict:
        """Validate IMU data quality"""
        results = {"valid": True, "checks": {}}
        
        # Validate angular velocity readings
        if self.imu_buffers['angular_velocity']:
            latest_angular = self.imu_buffers['angular_velocity'][-1]
            angular_magnitude = np.sqrt(
                latest_angular['x']**2 + 
                latest_angular['y']**2 + 
                latest_angular['z']**2
            )
            
            # Check for extreme values (probably indicates sensor malfunction)
            is_angular_valid = angular_magnitude < 10.0  # 10 rad/s threshold
            results["checks"]["angular_velocity"] = {
                "valid": is_angular_valid,
                "magnitude": float(angular_magnitude)
            }
            
            if not is_angular_valid:
                results["valid"] = False
        
        # Validate linear acceleration (should be ~9.8 m/s² when stationary)
        if self.imu_buffers['linear_acceleration']:
            latest_acc = self.imu_buffers['linear_acceleration'][-1]
            acc_magnitude = np.sqrt(
                latest_acc['x']**2 + 
                latest_acc['y']**2 + 
                latest_acc['z']**2
            )
            
            # Stationary robot should have gravity acceleration
            expected_static = 9.8  # m/s²
            gravity_tolerance = 1.0  # Allow 1 m/s² tolerance
            
            is_acceleration_valid = abs(acc_magnitude - expected_static) < gravity_tolerance
            results["checks"]["linear_acceleration"] = {
                "valid": is_acceleration_valid,
                "magnitude": float(acc_magnitude),
                "expected": expected_static
            }
            
            if not is_acceleration_valid:
                results["valid"] = False
        
        # Validate orientation stability
        if len(self.imu_buffers['orientation']) > 10:
            orientations = [o for o in self.imu_buffers['orientation']]
            
            # Calculate orientation drift over time
            start_quat = np.array([
                orientations[0]['x'], 
                orientations[0]['y'], 
                orientations[0]['z'], 
                orientations[0]['w']
            ])
            
            end_quat = np.array([
                orientations[-1]['x'], 
                orientations[-1]['y'], 
                orientations[-1]['z'], 
                orientations[-1]['w']
            ])
            
            # Calculate quaternion difference (simplified)
            quat_diff = start_quat - end_quat
            drift_magnitude = np.linalg.norm(quat_diff)
            
            is_orientation_valid = drift_magnitude < self.valid_imu_drift_threshold
            results["checks"]["orientation_stability"] = {
                "valid": is_orientation_valid,
                "drift_magnitude": float(drift_magnitude)
            }
            
            if not is_orientation_valid:
                results["valid"] = False
        
        return results
    
    def run_validation(self):
        """Run periodic sensor validation"""
        lidar_result = self.validate_lidar_data()
        imu_result = self.validate_imu_data()
        
        validation_report = {
            "timestamp": self.get_clock().now().nanoseconds / 1e9,
            "lidar": lidar_result,
            "imu": imu_result,
            "system_status": "OK" if lidar_result["valid"] and imu_result["valid"] else "ERROR"
        }
        
        # Publish validation report
        report_msg = String()
        report_msg.data = str(validation_report)
        self.validation_pub.publish(report_msg)
        
        # Log validation results
        self.get_logger().info(f"Sensor validation: LiDAR: {'OK' if lidar_result['valid'] else 'ERROR'}, "
                              f"IMU: {'OK' if imu_result['valid'] else 'ERROR'}")


def main(args=None):
    rclpy.init(args=args)
    validator = SensorValidationNode()
    
    try:
        rclpy.spin(validator)
    except KeyboardInterrupt:
        validator.get_logger().info("Sensor validation node shutting down...")
    finally:
        validator.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### Hints

- Use realistic noise characteristics that match actual sensors
- Test sensor data with known ground truth when possible
- Implement proper data buffering for sensor fusion
- Validate sensor data continuously during operation

## Exercise 3: Unity Integration for Advanced Visualization

Implement Unity integration with realistic sensor visualization and robot control interface.

### Instructions

1. Create a Unity scene with realistic humanoid robot model
2. Implement visualization for LiDAR, IMU, and camera data
3. Create interactive controls for robot operation
4. Implement VR/AR interface for robot control (if hardware available)
5. Test system integration between Unity, Gazebo, and ROS 2

### Solution

First, let me create a Unity sensor visualization script:

```csharp
// SensorVisualizer.cs for Unity
using UnityEngine;
using System.Collections.Generic;

public class SensorVisualizer : MonoBehaviour
{
    [System.Serializable]
    public class SensorConfiguration
    {
        public string sensorName;
        public SensorType sensorType;
        public Transform mountPoint;
        public GameObject visualizationPrefab;
        public float updateRate = 10f;
        public Color visualizationColor = Color.blue;
    }
    
    public enum SensorType
    {
        LiDAR,
        IMU,
        Camera,
        GPS,
        ForceTorque
    }
    
    [Header("Sensor Configurations")]
    public List<SensorConfiguration> sensors = new List<SensorConfiguration>();
    
    [Header("Visualization Settings")]
    public float lidarMaxDistance = 10.0f;
    public int lidarRayCount = 360;
    public float lidarRayWidth = 0.05f;
    
    private Dictionary<string, GameObject[]> lidarVisualizations;
    private Dictionary<string, LineRenderer> imuVisualizations;
    private Dictionary<string, GameObject> cameraVisualizations;
    
    private float lastLidarUpdate = 0f;
    private float lastImuUpdate = 0f;
    
    void Start()
    {
        InitializeSensorVisualizers();
    }
    
    void InitializeSensorVisualizers()
    {
        lidarVisualizations = new Dictionary<string, GameObject[]>();
        imuVisualizations = new Dictionary<string, LineRenderer>();
        cameraVisualizations = new Dictionary<string, GameObject>();
        
        foreach(var config in sensors)
        {
            switch(config.sensorType)
            {
                case SensorType.LiDAR:
                    CreateLiDARVisualization(config);
                    break;
                case SensorType.IMU:
                    CreateIMUVisualization(config);
                    break;
                case SensorType.Camera:
                    CreateCameraVisualization(config);
                    break;
            }
        }
    }
    
    void CreateLiDARVisualization(SensorConfiguration config)
    {
        GameObject[] rays = new GameObject[lidarRayCount];
        
        for(int i = 0; i < lidarRayCount; i++)
        {
            GameObject ray = new GameObject($"LiDAR_Ray_{i}");
            ray.transform.SetParent(config.mountPoint);
            ray.transform.localPosition = Vector3.zero;
            
            LineRenderer lr = ray.AddComponent<LineRenderer>();
            lr.material = new Material(Shader.Find("Unlit/Color"));
            lr.material.color = config.visualizationColor;
            lr.startWidth = lidarRayWidth;
            lr.endWidth = lidarRayWidth;
            lr.positionCount = 2;
            
            // Initialize to origin (will be updated when real data comes in)
            lr.SetPosition(0, Vector3.zero);
            lr.SetPosition(1, Vector3.forward * 0.1f);
            
            rays[i] = ray;
        }
        
        lidarVisualizations[config.sensorName] = rays;
    }
    
    void CreateIMUVisualization(SensorConfiguration config)
    {
        GameObject imuVisual = new GameObject($"{config.sensorName}_Orientation");
        imuVisual.transform.SetParent(config.mountPoint);
        imuVisual.transform.localPosition = Vector3.zero;
        
        LineRenderer lr = imuVisual.AddComponent<LineRenderer>();
        lr.material = new Material(Shader.Find("Unlit/Color"));
        lr.material.color = config.visualizationColor;
        lr.startWidth = 0.02f;
        lr.endWidth = 0.02f;
        lr.positionCount = 2;
        
        // Initialize to identity orientation
        lr.SetPosition(0, Vector3.zero);
        lr.SetPosition(1, Vector3.forward * 0.3f);
        
        imuVisualizations[config.sensorName] = lr;
    }
    
    void CreateCameraVisualization(SensorConfiguration config)
    {
        // For camera, create a frustum visualization
        GameObject cameraVisual = GameObject.CreatePrimitive(PrimitiveType.Quad);
        cameraVisual.name = $"{config.sensorName}_Camera_Frustum";
        cameraVisual.transform.SetParent(config.mountPoint);
        cameraVisual.transform.localPosition = Vector3.forward * 0.1f; // Offset slightly forward
        cameraVisual.transform.localScale = Vector3.one * 0.2f; // Size of the visualization
        
        // Apply color
        var rend = cameraVisual.GetComponent<Renderer>();
        rend.material = new Material(Shader.Find("Unlit/Color"));
        rend.material.color = config.visualizationColor;
        
        cameraVisualizations[config.sensorName] = cameraVisual;
        
        // Destroy primitive collider as we don't need it
        DestroyImmediate(cameraVisual.GetComponent<BoxCollider>());
    }
    
    void Update()
    {
        UpdateSensorVisualizations();
    }
    
    void UpdateSensorVisualizations()
    {
        // Update at specified rates
        float currentTime = Time.time;
        
        foreach(var config in sensors)
        {
            switch(config.sensorType)
            {
                case SensorType.LiDAR:
                    if(currentTime - lastLidarUpdate >= 1f/config.updateRate)
                    {
                        UpdateLiDARVisualization(config);
                        lastLidarUpdate = currentTime;
                    }
                    break;
                    
                case SensorType.IMU:
                    if(currentTime - lastImuUpdate >= 1f/config.updateRate)
                    {
                        UpdateIMUVisualization(config);
                        lastImuUpdate = currentTime;
                    }
                    break;
            }
        }
    }
    
    void UpdateLiDARVisualization(SensorConfiguration config)
    {
        if(!lidarVisualizations.ContainsKey(config.sensorName))
            return;
        
        GameObject[] rays = lidarVisualizations[config.sensorName];
        
        // In a real implementation, this would receive actual LiDAR data
        // For demo purposes, we'll create a simple pattern
        for(int i = 0; i < lidarRayCount && i < rays.Length; i++)
        {
            LineRenderer lr = rays[i].GetComponent<LineRenderer>();
            
            // Create a demo pattern (radial with some obstacles)
            float angle = (i * Mathf.PI * 2) / lidarRayCount;
            float distance = lidarMaxDistance;
            
            // Add some obstacles in demo pattern
            float noise = Mathf.PerlinNoise(i * 0.1f, Time.time * 0.5f);
            if(noise > 0.7f)
            {
                distance = 3.0f + Mathf.Sin(Time.time + angle) * 2.0f;
            }
            
            Vector3 direction = new Vector3(Mathf.Cos(angle), 0, Mathf.Sin(angle));
            Vector3 endPos = direction * distance;
            
            lr.SetPosition(0, config.mountPoint.position);
            lr.SetPosition(1, config.mountPoint.position + endPos);
        }
    }
    
    void UpdateIMUVisualization(SensorConfiguration config)
    {
        if(!imuVisualizations.ContainsKey(config.sensorName))
            return;
        
        LineRenderer lr = imuVisualizations[config.sensorName];
        
        // In a real implementation, this would receive actual IMU data
        // For demo purposes, we'll create a slowly rotating orientation
        Vector3 orientationVector = config.mountPoint.TransformDirection(
            Quaternion.Euler(
                Mathf.Sin(Time.time) * 10f,    // X axis rotation
                Mathf.Sin(Time.time * 1.5f) * 15f,  // Y axis rotation  
                Mathf.Cos(Time.time * 0.7f) * 5f     // Z axis rotation
            ) * Vector3.forward * 0.3f
        );
        
        lr.SetPosition(0, config.mountPoint.position);
        lr.SetPosition(1, config.mountPoint.position + orientationVector);
    }
    
    // Methods to update visualizations with real sensor data
    public void UpdateLiDARData(string sensorName, float[] ranges, float angleMin, float angleIncrement)
    {
        if(!lidarVisualizations.ContainsKey(sensorName))
            return;
        
        GameObject[] rays = lidarVisualizations[sensorName];
        
        for(int i = 0; i < Mathf.Min(ranges.Length, rays.Length); i++)
        {
            if(ranges[i] > 0 && ranges[i] < lidarMaxDistance)
            {
                LineRenderer lr = rays[i].GetComponent<LineRenderer>();
                
                float angle = angleMin + i * angleIncrement;
                Vector3 direction = new Vector3(Mathf.Cos(angle), 0, Mathf.Sin(angle));
                Vector3 endPos = direction * ranges[i];
                
                lr.SetPosition(0, Vector3.zero); // Origin at sensor mount point
                lr.SetPosition(1, endPos);
            }
        }
    }
    
    public void UpdateIMUData(string sensorName, Vector3 angularVelocity, Vector3 linearAcceleration, Quaternion orientation)
    {
        if(!imuVisualizations.ContainsKey(sensorName))
            return;
        
        LineRenderer lr = imuVisualizations[sensorName];
        
        // Visualize the orientation from the IMU
        Vector3 orientationArrow = orientation * Vector3.forward * 0.5f;
        lr.SetPosition(0, Vector3.zero);
        lr.SetPosition(1, orientationArrow);
    }
    
    public void UpdateCameraData(string sensorName, Texture2D image)
    {
        if(!cameraVisualizations.ContainsKey(sensorName))
            return;
        
        GameObject cameraObj = cameraVisualizations[sensorName];
        Renderer rend = cameraObj.GetComponent<Renderer>();
        
        if(rend != null && image != null)
        {
            rend.material.mainTexture = image;
        }
    }
}
```

And also a Unity ROS connection handler:

```csharp
// UnityROSConnection.cs
using UnityEngine;
using Unity.Robotics.ROSTCPConnector;
using RosMessageTypes.Sensor;
using RosMessageTypes.Navigation;
using RosMessageTypes.Geometry;

public class UnityROSConnection : MonoBehaviour
{
    [Header("ROS Connection")]
    public string rosIpAddress = "127.0.0.1";
    public int rosPort = 10000;
    
    [Header("Topic Names")]
    public string lidarTopic = "/scan";
    public string imuTopic = "/imu/data";
    public string jointStatesTopic = "/joint_states";
    public string cmdVelTopic = "/cmd_vel";
    
    private ROSConnection ros;
    private SensorVisualizer sensorVisualizer;
    
    void Start()
    {
        ros = ROSConnection.instance;
        ros.RosIPAddress = rosIpAddress;
        ros.RosPort = rosPort;
        
        sensorVisualizer = GetComponent<SensorVisualizer>();
        
        // Subscribe to ROS topics
        ros.Subscribe<LaserScanMsg>(lidarTopic, LiDARCallback);
        ros.Subscribe<ImuMsg>(imuTopic, ImuCallback);
        ros.Subscribe<JointStateMsg>(jointStatesTopic, JointStateCallback);
        
        Debug.Log($"Connected to ROS at {rosIpAddress}:{rosPort}");
        Debug.Log($"Subscribed to topics: {lidarTopic}, {imuTopic}, {jointStatesTopic}");
    }
    
    void LiDARCallback(LaserScanMsg msg)
    {
        // Convert ROS LiDAR message to Unity format
        float[] ranges = new float[msg.ranges.Length];
        for(int i = 0; i < msg.ranges.Length; i++)
        {
            ranges[i] = (float)msg.ranges[i];
        }
        
        // Update visualization
        sensorVisualizer.UpdateLiDARData("laser_front", ranges, (float)msg.angle_min, (float)msg.angle_increment);
    }
    
    void ImuCallback(ImuMsg msg)
    {
        // Extract data from IMU message
        Vector3 angularVel = new Vector3(
            (float)msg.angular_velocity.x,
            (float)msg.angular_velocity.y,
            (float)msg.angular_velocity.z
        );
        
        Vector3 linearAccel = new Vector3(
            (float)msg.linear_acceleration.x,
            (float)msg.linear_acceleration.y,
            (float)msg.linear_acceleration.z
        );
        
        Quaternion orientation = new Quaternion(
            (float)msg.orientation.x,
            (float)msg.orientation.y,
            (float)msg.orientation.z,
            (float)msg.orientation.w
        );
        
        // Update visualization
        sensorVisualizer.UpdateIMUData("humanoid_imu", angularVel, linearAccel, orientation);
    }
    
    void JointStateCallback(JointStateMsg msg)
    {
        // Update robot model with joint positions
        UpdateRobotJoints(msg);
    }
    
    void UpdateRobotJoints(JointStateMsg jointStateMsg)
    {
        // This would update the Unity robot model's joint positions
        // Implementation would depend on the robot model structure
        
        for(int i = 0; i < jointStateMsg.name.Length; i++)
        {
            if(i < jointStateMsg.position.Length)
            {
                string jointName = jointStateMsg.name[i];
                float jointPosition = (float)jointStateMsg.position[i];
                
                // Update joint in Unity model
                UpdateJointInModel(jointName, jointPosition);
            }
        }
    }
    
    void UpdateJointInModel(string jointName, float position)
    {
        // Find the joint in the Unity model and update its position
        Transform jointTransform = transform.FindRecursive(jointName);  // Helper method
        
        if(jointTransform != null)
        {
            // This depends on the joint type (revolute, prismatic, etc.)
            // For revolute joints, apply rotation
            // For prismatic joints, apply translation
            jointTransform.localRotation = Quaternion.Euler(0, 0, position * Mathf.Rad2Deg);
        }
    }
    
    public void SendVelocityCommand(double linearX, double angularZ)
    {
        // Create and send velocity command to ROS
        var twistMsg = new TwistMsg();
        twistMsg.linear = new Vector3Msg(linearX, 0, 0);
        twistMsg.angular = new Vector3Msg(0, 0, angularZ);
        
        ros.Send<TwistMsg>(cmdVelTopic, twistMsg);
    }
    
    void OnApplicationQuit()
    {
        // Clean up ROS connection
        if(ros != null)
        {
            ros.Close();
        }
    }
}
```

### Hints

- Use appropriate visualization techniques for each sensor type
- Optimize visualization performance for real-time rendering
- Implement proper error handling when ROS connection is lost
- Use Unity's job system for efficient sensor data processing
- Consider using AR/VR for immersive robot monitoring

## Performance and Validation

### Performance Optimization

```python
# performance_monitor.py
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import time
import psutil
import GPUtil
from collections import deque
import statistics


class PerformanceMonitor(Node):
    """Monitor system performance during operation"""
    
    def __init__(self):
        super().__init__('performance_monitor')
        
        # Publishers
        self.performance_pub = self.create_publisher(String, '/performance_stats', 10)
        
        # Metrics tracking
        self.cpu_percentages = deque(maxlen=100)
        self.memory_percentages = deque(maxlen=100)
        self.gpu_percentages = deque(maxlen=100)
        
        # Timing metrics
        self.cycle_times = deque(maxlen=100)
        self.last_time = time.time()
        
        # Start monitoring timer (10Hz)
        self.monitor_timer = self.create_timer(0.1, self.monitor_system)
        
        self.get_logger().info("Performance monitor initialized")
    
    def monitor_system(self):
        """Monitor system resources and performance"""
        current_time = time.time()
        cycle_time = current_time - self.last_time
        self.cycle_times.append(cycle_time)
        self.last_time = current_time
        
        # Get system metrics
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent
        disk_usage_percent = psutil.disk_usage('/').percent
        
        # GPU metrics if available
        gpu_percent = 0
        gpus = GPUtil.getGPUs()
        if gpus:
            gpu_percent = gpus[0].load * 100
        
        self.cpu_percentages.append(cpu_percent)
        self.memory_percentages.append(memory_percent)
        if gpu_percent > 0:
            self.gpu_percentages.append(gpu_percent)
        
        # Performance report
        performance_report = {
            'timestamp': current_time,
            'cpu': {
                'current': cpu_percent,
                'average': statistics.mean(self.cpu_percentages),
                'peak': max(self.cpu_percentages)
            },
            'memory': {
                'current': memory_percent,
                'average': statistics.mean(self.memory_percentages),
                'peak': max(self.memory_percentages)
            },
            'gpu': {
                'current': gpu_percent,
                'average': statistics.mean(self.gpu_percentages) if self.gpu_percentages else 0,
                'peak': max(self.gpu_percentages) if self.gpu_percentages else 0
            },
            'timing': {
                'current_cycle_time': cycle_time,
                'average_cycle_time': statistics.mean(self.cycle_times),
                'min_cycle_time': min(self.cycle_times),
                'max_cycle_time': max(self.cycle_times),
                'frequency': 1.0 / statistics.mean(self.cycle_times) if self.cycle_times else 0
            },
            'disk_usage': disk_usage_percent
        }
        
        # Check for performance warnings
        if cpu_percent > 90:
            self.get_logger().warn(f"High CPU usage: {cpu_percent}%")
        if memory_percent > 90:
            self.get_logger().warn(f"High memory usage: {memory_percent}%")
        if cycle_time > 0.1:  # 100ms threshold
            self.get_logger().warn(f"Slow cycle time: {cycle_time*1000:.1f}ms")
        
        # Publish performance metrics
        perf_msg = String()
        perf_msg.data = str(performance_report)
        self.performance_pub.publish(perf_msg)
    
    def get_performance_summary(self) -> dict:
        """Get overall system performance summary"""
        return {
            'cpu': {
                'avg': statistics.mean(self.cpu_percentages) if self.cpu_percentages else 0,
                'max': max(self.cpu_percentages) if self.cpu_percentages else 0
            },
            'memory': {
                'avg': statistics.mean(self.memory_percentages) if self.memory_percentages else 0,
                'max': max(self.memory_percentages) if self.memory_percentages else 0
            },
            'timing': {
                'avg_freq': 1.0 / statistics.mean(self.cycle_times) if self.cycle_times else 0,
                'avg_cycle_time': statistics.mean(self.cycle_times) if self.cycle_times else 0
            }
        }


def main(args=None):
    rclpy.init(args=args)
    monitor = PerformanceMonitor()
    
    try:
        rclpy.spin(monitor)
    except KeyboardInterrupt:
        monitor.get_logger().info("Performance monitor shutting down...")
    finally:
        monitor.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Chapter Summary

This chapter provided a comprehensive implementation of sensor simulation systems for humanoid robots, including LiDAR, IMU, and camera sensors. We covered:

1. **LiDAR Simulation**: Creating realistic LiDAR sensors with proper noise models
2. **IMU Simulation**: Configuring IMU sensors with realistic drift and noise characteristics
3. **Sensor Fusion**: Combining multiple sensor inputs for improved perception
4. **Unity Integration**: Advanced visualization and interface design
5. **Performance Monitoring**: Tracking system performance during operation
6. **Validation Techniques**: Ensuring sensor data quality and accuracy
7. **Optimization Strategies**: Maintaining real-time performance

The complete sensor simulation system enables developers to test perception algorithms, navigation systems, and control loops without access to physical hardware.

## Checklist

- [ ] Configure realistic LiDAR sensors with proper parameters
- [ ] Set up IMU sensors with appropriate noise and drift models
- [ ] Implement sensor fusion combining multiple modalities
- [ ] Validate sensor data against expected characteristics
- [ ] Integrate Unity for advanced visualization
- [ ] Optimize sensor processing for real-time performance
- [ ] Create VR/AR interfaces for robot operation
- [ ] Monitor system performance during execution
- [ ] Implement error handling for sensor failures
- [ ] Test integration with control and planning systems

## Exercises

### Exercise 1: Multi-Sensor Integration

Build a node that integrates data from LiDAR, camera, and IMU to create a comprehensive environmental model.

#### Solution

1. Subscribe to all three sensor topics
2. Implement temporal and spatial alignment of sensors
3. Create fused environmental model
4. Validate consistency between sensors

#### Hints

- Use ROS message filters for temporal synchronization
- Consider extrinsic calibration between sensors
- Implement sensor validation checks
- Handle sensor failures gracefully

### Exercise 2: Performance Optimization

Optimize the sensor processing pipeline for real-time operation.

#### Solution

1. Profile current sensor processing rates
2. Optimize data structures and algorithms
3. Implement data decimation techniques
4. Validate that optimization doesn't degrade perception quality

#### Hints

- Use efficient data structures (deques, numpy arrays)
- Consider reducing sensor update rates where possible
- Implement early termination for processing algorithms
- Monitor and validate results at reduced performance

## References

- [Gazebo Sensor Tutorial](http://gazebosim.org/tutorials?tut=ros2_sensor_tutorial)
- [ROS 2 Sensor Integration Guide](https://docs.ros.org/en/humble/Tutorials/Advanced/Simulators/Gazebo.html)
- [Probabilistic Robotics by Thrun, Burgard, Fox](https://mitpress.mit.edu/books/probabilistic-robotics)
- [Robotics, Vision and Control by Corke](https://link.springer.com/book/10.1007/978-3-642-20144-7)
- [Unity Robotics Hub](https://github.com/Unity-Technologies/Unity-Robotics-Hub)
- [SLAM Tutorial](https://ieeexplore.ieee.org/document/9100015)
- [Sensor Fusion Techniques](https://www.mdpi.com/1424-8220/19/9/2042)