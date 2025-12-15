---
title: 'Exercise Set 3 - The AI-Robot Brain (NVIDIA Isaac)'
description: 'Hands-on exercises for Module 3 - Isaac Sim, perception, and AI planning'
---

# Exercise Set 3: The AI-Robot Brain (NVIDIA Isaac)

## Learning Objectives

After completing these exercises, you will be able to:
- Configure and use Isaac Sim for humanoid robot simulation
- Implement perception systems that integrate vision and other sensors
- Design AI-powered manipulation and planning systems
- Create integrated perception-action loops for humanoid tasks
- Evaluate and optimize AI-based robot behaviors
- Develop and test cognitive planning algorithms
- Validate sensor simulation accuracy and effectiveness
- Troubleshoot complex integrated robot systems

## Exercise 1: Isaac Sim Environment with Complex Scenarios

Create a complex simulation environment in Isaac Sim with multiple objects and realistic physics for humanoid robot tasks.

### Instructions

1. Create an Isaac Sim world with:
   - Multiple rooms with different flooring materials
   - Various objects with different physical properties
   - Humanoid-friendly furniture (tables at appropriate heights)
   - Dynamic lighting conditions
   - Multiple levels (stairs or ramps)

2. Configure the physics parameters appropriately for humanoid robot dynamics.

3. Implement collision detection and response for different surface types.

4. Verify that the simulation is stable and realistic for humanoid operation.

### Solution

#### 1. Create the Isaac Sim scene with USD files

```python
# isaac_sim_setup.py
import omni
from omni.isaac.core import World
from omni.isaac.core.utils.stage import add_reference_to_stage
from omni.isaac.core.utils.nucleus import get_assets_root_path
from omni.isaac.core.utils.prims import create_primitive
from omni.isaac.core.utils.rotations import euler_angles_to_quat
import numpy as np


def create_complex_humanoid_environment():
    """
    Create a complex environment with multiple rooms and objects
    for humanoid robot training and testing
    """
    
    # Get the world instance
    world = World(stage_units_in_meters=1.0)
    
    # Get assets root for standard models
    assets_root = get_assets_root_path()
    
    # Create the environment
    create_rooms_with_doors()
    create_furniture()
    create_objects_with_various_materials()
    create_stairs_or_ramps()
    create_lighting()
    
    # Configure physics
    configure_physics_params()
    
    return world


def create_rooms_with_doors():
    """
    Create multiple interconnected rooms with doors
    """
    room_size = 4.0  # 4m x 4m rooms
    wall_thickness = 0.2
    wall_height = 2.5
    
    # Create outer walls for main room
    create_primitive(
        prim_path="/World/main_room/north_wall",
        prim_type="Cube",
        position=np.array([0, room_size/2, wall_height/2]),
        scale=np.array([room_size, wall_thickness, wall_height])
    )
    
    create_primitive(
        prim_path="/World/main_room/south_wall",
        prim_type="Cube",
        position=np.array([0, -room_size/2, wall_height/2]),
        scale=np.array([room_size, wall_thickness, wall_height])
    )
    
    create_primitive(
        prim_path="/World/main_room/east_wall",
        prim_type="Cube", 
        position=np.array([room_size/2, 0, wall_height/2]),
        scale=np.array([wall_thickness, room_size, wall_height])
    )
    
    create_primitive(
        prim_path="/World/main_room/west_wall",
        prim_type="Cube",
        position=np.array([-room_size/2, 0, wall_height/2]),
        scale=np.array([wall_thickness, room_size, wall_height])
    )
    
    # Create door opening in south wall
    # (We'll place a door that can be opened/closed)
    create_door(
        position=np.array([0, -room_size/2, 1.0]),  # Centered on south wall, at human height
        width=0.8,
        height=2.0
    )


def create_furniture():
    """
    Create humanoid-friendly furniture
    """
    # Living room table
    create_primitive(
        prim_path="/World/furniture/living_room_table",
        prim_type="Cylinder",
        position=np.array([1.0, 0.5, 0.4]),
        scale=np.array([0.6, 0.6, 0.8]),
        color=np.array([0.6, 0.4, 0.2])
    )
    
    # Kitchen counter (higher for humanoid manipulation practice)
    create_primitive(
        prim_path="/World/furniture/kitchen_counter",
        prim_type="Cube",
        position=np.array([-2.0, -1.0, 0.9]),
        scale=np.array([1.5, 0.6, 1.8]),  # Counter height around 90-100cm for humanoid
        color=np.array([0.8, 0.8, 0.8])
    )
    
    # Chair for interaction practice
    create_primitive(
        prim_path="/World/furniture/chair",
        prim_type="Cylinder",
        position=np.array([1.5, 0.0, 0.25]),
        scale=np.array([0.3, 0.3, 0.5]),
        color=np.array([0.5, 0.5, 0.5])
    )


def create_objects_with_various_materials():
    """
    Create various objects with different physical properties
    """
    
    # Different objects with unique properties
    objects = [
        # Wood block - medium mass, low friction
        {
            "name": "wood_block",
            "position": np.array([1.0, 0.7, 0.45]),
            "type": "Box",
            "scale": np.array([0.1, 0.1, 0.1]),
            "color": np.array([0.6, 0.4, 0.2]),
            "mass": 0.2,
            "friction": 0.3
        },
        # Metal cylinder - high mass, medium friction
        {
            "name": "metal_cylinder",
            "position": np.array([1.2, 0.7, 0.45]),
            "type": "Cylinder",
            "scale": np.array([0.05, 0.05, 0.15]),
            "color": np.array([0.5, 0.5, 0.7]),
            "mass": 0.5,
            "friction": 0.6
        },
        # Plastic sphere - low mass, high friction
        {
            "name": "plastic_sphere",
            "position": np.array([1.4, 0.7, 0.45]),
            "type": "Sphere",
            "scale": np.array([0.05, 0.05, 0.05]),
            "color": np.array([0.8, 0.2, 0.2]),
            "mass": 0.1,
            "friction": 0.8
        },
        # Paper box - very light, high friction
        {
            "name": "paper_box",
            "position": np.array([1.1, 0.8, 0.5]),
            "type": "Box",
            "scale": np.array([0.1, 0.08, 0.05]),
            "color": np.array([0.9, 0.9, 0.9]),
            "mass": 0.05,
            "friction": 0.9
        }
    ]
    
    for obj_data in objects:
        create_primitive(
            prim_path=f"/World/objects/{obj_data['name']}",
            prim_type=obj_data["type"],
            position=obj_data["position"],
            scale=obj_data["scale"],
            color=obj_data["color"]
        )
        
        # Add specific properties like mass and friction would require more advanced prim configuration


def create_stairs_or_ramps():
    """
    Create stairs or ramps to test humanoid locomotion
    """
    # Create a simple staircase
    stair_height = 0.17  # 17cm typical stair height
    stair_depth = 0.28   # 28cm typical stair depth
    stair_width = 1.0    # 1m wide stairs
    
    for i in range(5):  # Create 5 steps
        create_primitive(
            prim_path=f"/World/stairs/step_{i}",
            prim_type="Cube",
            position=np.array([0, -2.0 + i*stair_depth, i*stair_height]),
            scale=np.array([stair_width, stair_depth, stair_height]),
            color=np.array([0.4, 0.4, 0.4])
        )


def create_lighting():
    """
    Create dynamic lighting in the environment
    """
    # Create dome light for ambient lighting
    from omni.isaac.core.utils.prims import create_prim
    
    create_prim(
        prim_path="/World/Light/DomeLight",
        prim_type="DomeLight",
        position=np.array([0, 0, 10]),
        attributes={"color": (0.8, 0.8, 0.8), "intensity": 3000}
    )
    
    # Add a few spotlights for more directed lighting
    create_prim(
        prim_path="/World/Light/SpotLight1",
        prim_type="SpotLight",
        position=np.array([2, 2, 3]),
        attributes={"color": (1.0, 1.0, 1.0), "intensity": 1500}
    )


def configure_physics_params():
    """
    Configure physics parameters appropriate for humanoid simulation
    """
    # In Isaac Sim, we access the physics scene through the simulation context
    omni.physx.acquire_physx_interface().get_physics_simulator().set_timestep(1.0/60.0)  # 60Hz physics


def create_door(position, width, height):
    """
    Create a door that can be opened and closed
    """
    # Create door as a dynamic object with appropriate joint
    door_path = "/World/door/main_door"
    
    # Create door frame
    create_primitive(
        prim_path=door_path + "_frame",
        prim_type="Cube",
        position=position,
        scale=np.array([width + 0.1, 0.1, height + 0.1]),
        color=np.array([0.5, 0.3, 0.1])
    )
    
    # Create door panel (rotating part)
    door_panel_pos = position.copy()
    door_panel_pos[1] += (width/2 + 0.05)  # Offset to attach to frame
    
    create_primitive(
        prim_path=door_path + "_panel",
        prim_type="Cube",
        position=door_panel_pos,
        scale=np.array([width, 0.05, height]),
        color=np.array([0.6, 0.4, 0.2])
    )


# Run the environment creation
if __name__ == "__main__":
    world = create_complex_humanoid_environment()
    print("Complex humanoid environment created successfully!")
    
    # Reset the world to initialize physics
    world.reset()
    
    # Run the simulation for a few steps
    for i in range(100):
        world.step(render=True)
        if i % 50 == 0:
            print(f"Simulation step: {i}")
    
    print("Environment validation completed!")
```

#### 2. Validate Physics Parameters

```python
# physics_validator.py
import numpy as np
from scipy.spatial.transform import Rotation as R
from typing import Dict, Any, List


class PhysicsValidator:
    """
    Validates physics parameters for humanoid robot simulation
    """
    
    def __init__(self):
        self.validation_checks = [
            self.check_gravity_setting,
            self.check_robot_mass_settings,
            self.check_collision_properties,
            self.check_friction_coefficients,
            self.check_joint_limits,
            self.check_balance_stability
        ]
    
    def check_gravity_setting(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check that gravity is correctly set
        """
        expected_gravity = np.array([0, 0, -9.81])
        actual_gravity = world_state.get('gravity', np.array([0, 0, 0]))
        
        gravity_match = np.allclose(actual_gravity, expected_gravity, atol=0.01)
        
        return {
            'test_name': 'gravity_setting',
            'passed': gravity_match,
            'expected': expected_gravity,
            'actual': actual_gravity,
            'message': 'Gravity setting' + (' matches' if gravity_match else ' does not match') + ' expected value'
        }
    
    def check_robot_mass_distribution(self, robot_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check that robot mass distribution is realistic for humanoid
        """
        # Check total mass
        total_mass = robot_state.get('total_mass', 0)
        mass_acceptable = 30 <= total_mass <= 100  # 30-100 kg for humanoid robot
        
        # Check individual link masses
        link_masses = robot_state.get('link_masses', {})
        link_mass_errors = []
        
        for link_name, mass in link_masses.items():
            if mass < 0.1:  # Too light for physical robot
                link_mass_errors.append(f"Link {link_name} mass too low: {mass}kg")
            elif mass > 10:  # Possibly too heavy for small link
                link_mass_errors.append(f"Link {link_name} mass possibly too high: {mass}kg")
        
        return {
            'test_name': 'robot_mass_distribution',
            'passed': mass_acceptable and len(link_mass_errors) == 0,
            'total_mass': total_mass,
            'link_mass_issues': link_mass_errors,
            'message': f'Total robot mass ({total_mass}kg) is acceptable' if mass_acceptable else f'Total robot mass ({total_mass}kg) is outside acceptable range (30-100kg)'
        }
    
    def check_collision_properties(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check that collision properties are properly set
        """
        collision_objects = world_state.get('collision_objects', [])
        issues = []
        
        for obj in collision_objects:
            if not obj.get('collision_enabled', True):
                issues.append(f"Object {obj['name']} has collision disabled")
            
            if not obj.get('contact_reporting', False):
                issues.append(f"Object {obj['name']} has contact reporting disabled")
        
        return {
            'test_name': 'collision_properties',
            'passed': len(issues) == 0,
            'issues': issues,
            'message': 'All collision properties are properly set' if len(issues) == 0 else f'Found {len(issues)} collision property issues'
        }
    
    def check_friction_coefficients(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check that friction coefficients are realistic
        """
        surfaces = world_state.get('surfaces', {})
        issues = []
        
        # Typical friction coefficients for humanoid environments
        expected_ranges = {
            'floor_tile': (0.4, 0.8),
            'wood_floor': (0.3, 0.6),
            'carpet': (0.4, 1.0),
            'table_surface': (0.3, 0.7)
        }
        
        for surf_name, properties in surfaces.items():
            coeff = properties.get('friction', 0)
            if surf_name in expected_ranges:
                min_val, max_val = expected_ranges[surf_name]
                if not (min_val <= coeff <= max_val):
                    issues.append(
                        f"Surface {surf_name} has friction {coeff}, expected range {min_val}-{max_val}"
                    )
        
        return {
            'test_name': 'friction_coefficients',
            'passed': len(issues) == 0,
            'issues': issues,
            'message': 'Friction coefficients are within expected ranges' if len(issues) == 0 else f'Found {len(issues)} friction coefficient issues'
        }
    
    def check_joint_limits(self, robot_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check that joint limits are appropriate for humanoid
        """
        joints = robot_state.get('joints', {})
        issues = []
        
        # Define expected limits for humanoid joints
        expected_limits = {
            'hip_pitch': (-1.57, 1.57),      # -90 to 90 degrees 
            'hip_roll': (-0.785, 0.785),    # -45 to 45 degrees
            'hip_yaw': (-0.785, 0.785),    # -45 to 45 degrees
            'knee': (0, 2.356),            # 0 to 135 degrees (flexion only)
            'ankle_pitch': (-0.523, 0.523), # -30 to 30 degrees
            'ankle_roll': (-0.785, 0.785)  # -45 to 45 degrees
        }
        
        for joint_name, properties in joints.items():
            limits = properties.get('limits', {})
            lower = limits.get('lower', 0)
            upper = limits.get('upper', 0)
            
            if joint_name in expected_limits:
                exp_lower, exp_upper = expected_limits[joint_name]
                if not (abs(lower - exp_lower) < 0.5 and abs(upper - exp_upper) < 0.5):
                    issues.append(
                        f"Joint {joint_name} limits ({lower:.2f}, {upper:.2f}) differ significantly "
                        f"from expected ({exp_lower:.2f}, {exp_upper:.2f})"
                    )
        
        return {
            'test_name': 'joint_limits',
            'passed': len(issues) == 0,
            'issues': issues,
            'message': f'Joint limits appropriate' if len(issues) == 0 else f'Found {len(issues)} joint limit issues'
        }
    
    def run_validation(self, simulation_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Run all validation checks on the simulation state
        """
        world_state = simulation_state.get('world', {})
        robot_state = simulation_state.get('robot', {})
        
        results = []
        
        for check in self.validation_checks:
            try:
                result = check(world_state, robot_state) if 'robot_state' in check.__code__.co_varnames else check(world_state)
                results.append(result)
            except Exception as e:
                results.append({
                    'test_name': check.__name__,
                    'passed': False,
                    'error': str(e),
                    'message': f'Validation check {check.__name__} failed with error: {e}'
                })
        
        return results
    
    def generate_validation_report(self, validation_results: List[Dict[str, Any]]) -> str:
        """
        Generate a human-readable validation report
        """
        passed_count = sum(1 for result in validation_results if result.get('passed', False))
        total_count = len(validation_results)
        
        report = f"PHYSICS VALIDATION REPORT\n"
        report += f"{'='*30}\n"
        report += f"Results: {passed_count}/{total_count} checks passed\n\n"
        
        for result in validation_results:
            status = "✓ PASS" if result.get('passed', False) else "✗ FAIL"
            report += f"{status} {result['test_name']}: {result['message']}\n"
            
            if result.get('issues'):
                for issue in result['issues']:
                    report += f"    - {issue}\n"
            elif result.get('error'):
                report += f"    Error: {result['error']}\n"
        
        report += f"\nRecommendations for failed checks:\n"
        if passed_count < total_count:
            report += "- Review and adjust physics parameters as indicated in failures\n"
            report += "- Consider re-running validation after adjustments\n"
            report += "- Verify robot model URDF/SDF definition\n"
        else:
            report += "All validation checks passed! Physics parameters are appropriate for humanoid simulation."
        
        return report


# Example usage
def validate_simulation_physics():
    # Sample simulation state (in practice, this would come from the Isaac Sim environment)
    sample_state = {
        'world': {
            'gravity': np.array([0, 0, -9.81]),
            'surfaces': {
                'floor_tile': {'friction': 0.6},
                'wood_floor': {'friction': 0.4},
                'table_surface': {'friction': 0.5}
            },
            'collision_objects': [
                {'name': 'robot', 'collision_enabled': True, 'contact_reporting': True},
                {'name': 'object1', 'collision_enabled': True, 'contact_reporting': True}
            ]
        },
        'robot': {
            'total_mass': 45.0,
            'link_masses': {
                'pelvis': 5.0,
                'torso': 8.0,
                'head': 2.0,
                'left_hip': 1.5,
                'left_knee': 1.2,
                'left_ankle': 0.8
            },
            'joints': {
                'left_hip_pitch': {'limits': {'lower': -1.55, 'upper': 1.55}},
                'left_hip_roll': {'limits': {'lower': -0.75, 'upper': 0.75}},
                'left_knee': {'limits': {'lower': 0.0, 'upper': 2.3}},
                'left_ankle_pitch': {'limits': {'lower': -0.5, 'upper': 0.5}}
            }
        }
    }
    
    validator = PhysicsValidator()
    results = validator.run_validation(sample_state)
    report = validator.generate_validation_report(results)
    
    print(report)
    
    return results


if __name__ == "__main__":
    validation_results = validate_simulation_physics()
```

### Hints

- Verify physics parameters match human-like values
- Test simulation stability with various robot poses
- Check collision detection across different surface types
- Validate joint limits prevent damage and ensure realistic motion

## Exercise 2: Integrating Isaac Sim with Perception System

Connect Isaac Sim with the perception system to enable realistic sensor simulation.

### Instructions

1. Configure Isaac Sim to export sensor data (RGB, depth, IMU, LiDAR).
2. Implement sensor data processing pipelines.
3. Validate sensor data accuracy and realism.
4. Integrate perception with action planning systems.
5. Test the complete perception-action loop.

### Solution

#### 1. Isaac Sim Sensor Configuration

```python
# isaac_sim_sensors.py
from omni.isaac.core import World
from omni.isaac.core.utils.stage import add_reference_to_stage
from omni.isaac.core.utils.nucleus import get_assets_root_path
from omni.isaac.sensor import Camera, IMUSensor, ContactSensor
from omni.isaac.range_sensor import LidarRtx
import carb
import numpy as np


class HumanoidSensorSetup:
    """
    Sets up sensors for humanoid robot in Isaac Sim
    """
    
    def __init__(self, world: World):
        self.world = world
        self.sensors = {}
        
    def setup_cameras(self, robot_prim_path: str):
        """
        Set up RGB and depth cameras on the robot
        """
        # Head camera for vision-based perception
        head_camera = self.world.scene.add(
            Camera(
                prim_path=robot_prim_path + "/head_camera",
                name="head_camera",
                position=np.array([0.1, 0.0, 0.15]),  # Slightly forward and up from head
                frequency=30,  # 30 Hz
                resolution=(640, 480)
            )
        )
        
        # Add depth camera functionality
        head_depth_camera = self.world.scene.add(
            Camera(
                prim_path=robot_prim_path + "/head_depth_camera",
                name="head_depth_camera",
                position=np.array([0.1, 0.05, 0.15]),  # Slightly offset from RGB camera
                frequency=30,
                resolution=(640, 480),
                translation=np.array([0.1, 0.05, 0.15])
            )
        )
        
        # Enable depth data on the depth camera
        head_depth_camera.add_ground_truth_to_frame()
        
        self.sensors['head_rgb'] = head_camera
        self.sensors['head_depth'] = head_depth_camera
        
        print("Cameras configured successfully")
    
    def setup_imu(self, robot_prim_path: str):
        """
        Set up IMU sensors on the robot
        """
        # Add IMU to torso for balance sensing
        torso_imu = IMUSensor(
            prim_path=robot_prim_path + "/torso_imu",
            name="torso_imu",
            position=np.array([0.0, 0.0, 0.3]),  # In torso area
            frequency=100,  # High frequency for balance control (100Hz)
            orientation=np.array([1.0, 0.0, 0.0, 0.0])  # Identity quaternion
        )
        
        self.world.scene.add(torso_imu)
        self.sensors['torso_imu'] = torso_imu
        
        # Add IMU to head for orientation
        head_imu = IMUSensor(
            prim_path=robot_prim_path + "/head_imu",
            name="head_imu",
            position=np.array([0.0, 0.0, 0.15]),  # In head area
            frequency=50,  # 50Hz for head orientation
            orientation=np.array([1.0, 0.0, 0.0, 0.0])
        )
        
        self.world.scene.add(head_imu)
        self.sensors['head_imu'] = head_imu
        
        print("IMU sensors configured successfully")
    
    def setup_lidar(self, robot_prim_path: str):
        """
        Set up LiDAR sensor on the robot
        """
        # Create LiDAR sensor on robot head
        lidar = LidarRtx(
            prim_path=robot_prim_path + "/head_lidar",
            name="head_lidar",
            translation=np.array([0.15, 0.0, 0.2]),  # On top of head
            rotation=np.array([0.0, 0.0, 0.0]),
            # LiDAR parameters
            configuration={
                "rotation_frequency": 20,
                "channels": 16,  # 16 channels for 3D scanning
                "points_per_channel": 1800,
                "horizontal_fov": 360,  # Full 360 degree scan
                "vertical_fov": 30,  # 30 degree vertical spread
                "range": 25.0,  # 25m max range
                "min_range": 0.1,  # 10cm min range
            },
            # Advanced settings for humanoid navigation
            physics_material_path=robot_prim_path + "/lidar_material",
            visible=True
        )
        
        self.world.scene.add(lidar)
        self.sensors['head_lidar'] = lidar
        
        print("LiDAR sensor configured successfully")
    
    def setup_contact_sensors(self, robot_prim_path: str):
        """
        Set up contact sensors for detecting physical interactions
        """
        # Add contact sensors to feet for walking detection
        left_foot_contact = ContactSensor(
            prim_path=robot_prim_path + "/left_foot_contact",
            name="left_foot_contact",
            position=np.array([0.0, 0.08, -0.05]),  # Bottom of left foot
            contact_filters=["ground", "floor"],
            frequency=60
        )
        
        self.world.scene.add(left_foot_contact)
        self.sensors['left_foot_contact'] = left_foot_contact
        
        right_foot_contact = ContactSensor(
            prim_path=robot_prim_path + "/right_foot_contact",
            name="right_foot_contact", 
            position=np.array([0.0, -0.08, -0.05]),  # Bottom of right foot
            contact_filters=["ground", "floor"],
            frequency=60
        )
        
        self.world.scene.add(right_foot_contact)
        self.sensors['right_foot_contact'] = right_foot_contact
        
        # Add contact sensors to hands for manipulation
        left_hand_contact = ContactSensor(
            prim_path=robot_prim_path + "/left_hand_contact",
            name="left_hand_contact",
            position=np.array([0.0, 0.0, 0.0]),  # In the hand
            contact_filters=["object", "graspable"],
            frequency=60
        )
        
        self.world.scene.add(left_hand_contact)
        self.sensors['left_hand_contact'] = left_hand_contact
        
        print("Contact sensors configured successfully")
    
    def setup_sensors_for_humanoid(self, robot_prim_path: str = "/World/Robot"):
        """
        Set up all sensors for the humanoid robot
        """
        self.setup_cameras(robot_prim_path)
        self.setup_imu(robot_prim_path)
        self.setup_lidar(robot_prim_path)
        self.setup_contact_sensors(robot_prim_path)
        
        return self.sensors