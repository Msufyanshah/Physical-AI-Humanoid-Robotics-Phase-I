---
title: 'Chapter 9 - Isaac Sim Setup & Synthetic Data Generation'
description: 'Setting up NVIDIA Isaac Sim for advanced robotics simulation and synthetic data generation'
---

# Chapter 9: Isaac Sim Setup & Synthetic Data Generation

## Learning Objectives

After reading this chapter, you will be able to:
- Install and configure NVIDIA Isaac Sim for robotics simulation
- Understand Isaac Sim architecture and its integration with robotics frameworks
- Set up physically accurate simulation environments for humanoid robots
- Generate synthetic training data using Isaac Sim's advanced capabilities
- Configure sensors and perception systems in Isaac Sim
- Integrate Isaac Sim with ROS 2 and other robotics frameworks
- Optimize simulation for performance and realism
- Validate synthetic data quality for robotics applications

## Introduction

NVIDIA Isaac Sim is a comprehensive robotics simulation environment built on the NVIDIA Omniverse platform. It offers high-fidelity physics simulation, photorealistic rendering through RTX technology, and advanced tools specifically designed for AI training and synthetic data generation. This chapter covers setting up Isaac Sim for humanoid robotics applications and leveraging its capabilities for generating synthetic training data.

## Isaac Sim Architecture & Capabilities

### Core Architecture

Isaac Sim is built on the following technologies:

1. **NVIDIA Omniverse**: Platform for real-time collaboration and simulation
2. **USD (Universal Scene Description)**: Scene representation and composition
3. **PhysX Physics Engine**: NVIDIA's advanced physics simulation
4. **RTX Ray Tracing**: Photorealistic rendering engine
5. **Isaac Extensions**: Robotics-specific tools and capabilities

### Key Capabilities

- **High-Fidelity Physics**: Accurate simulation of robot dynamics and interactions
- **Photorealistic Rendering**: RTX ray-tracing for realistic visual data
- **Synthetic Data Generation**: Tools for creating labeled training datasets
- **AI-Ready Environment**: Integration with NVIDIA AI frameworks
- **ROS/ROS 2 Compatibility**: Built-in robotics middleware support

## Isaac Sim Installation and Setup

### System Requirements

To run Isaac Sim effectively, you need:

- **GPU**: NVIDIA GPU with RT Cores (RTX series recommended)
- **VRAM**: 8GB+ for complex scenes (16GB+ recommended)
- **CPU**: Multi-core processor (Intel i7 or AMD Ryzen equivalent)
- **RAM**: 32GB+ for complex simulations
- **OS**: Ubuntu 20.04 LTS or Windows 10/11

### Installation Methods

Isaac Sim can be installed in several ways:

#### Method 1: Omniverse Launcher (Recommended)
```bash
# Download Omniverse Launcher from NVIDIA Developer Zone
# Install Isaac Sim through the launcher
```

#### Method 2: Docker Installation
```bash
# Pull Isaac Sim Docker image
docker pull nvcr.io/nvidia/isaac-sim:latest

# Run Isaac Sim container
docker run --gpus all -it --rm \
  --network=host \
  --env "ACCEPT_EULA=Y" \
  --env "ISAACSIM_LICENSE_FILE=/data/isaacsim.lic" \
  --volume $PWD:/workspace \
  --volume /tmp/.X11-unix:/tmp/.X11-unix:rw \
  --env "DISPLAY=:0" \
  --env "QT_X11_NO_MITSHM=1" \
  --privileged \
  nvcr.io/nvidia/isaac-sim:latest
```

### Initial Configuration

After installation, configure Isaac Sim for optimal humanoid simulation:

```python
# config_isaac_sim.py
import omni
from omni.isaac.core import World
from omni.isaac.core.utils.stage import add_reference_to_stage
from omni.isaac.core.utils.nucleus import get_assets_root_path
from omni.isaac.core.utils.prims import get_prim_at_path
import carb


def setup_isaac_sim_environment():
    """Setup Isaac Sim environment with optimal parameters for humanoid simulation"""
    
    # Enable real-time physics and rendering
    carb.settings.get_settings().set_bool("/app/runLoops/main/render", True)
    carb.settings.get_settings().set_bool("/app/runLoops/main/rateLimitEnabled", False)
    
    # Set physics parameters for humanoid dynamics
    carb.settings.get_settings().set_int("/physics/solvers/defaultSolverVelocityIterations", 8)  # Increased for stability
    carb.settings.get_settings().set_int("/physics/solvers/defaultSolverPositionIterations", 4)  # Increased for stability
    carb.settings.get_settings().set_float("/physics/metrics/solverFrequency", 60.0)  # 60Hz solver
    carb.settings.get_settings().set_float("/physics/metrics/subSteps", 2)  # 2 substeps for better accuracy
    
    # Rendering settings
    carb.settings.get_settings().set_int("/renderton/lightCache/updateInterval", 1)
    carb.settings.get_settings().set_float("/persistent/omnihydra/phxProxyEnable", True)
    
    print("Isaac Sim environment configured for humanoid simulation")


def initialize_humanoid_world(reset=True):
    """Initialize the humanoid world with appropriate parameters"""
    
    # Create world instance with proper units
    world = World(
        stage_units_in_meters=1.0,
        physics_dt=1.0/60.0,  # 60Hz physics update
        rendering_dt=1.0/30.0  # 30Hz rendering update
    )
    
    if reset:
        world.reset()
    
    # Get assets root path
    assets_root_path = get_assets_root_path()
    if assets_root_path is None:
        carb.log_error("Could not find Isaac Sim assets path")
        return None
    
    print(f"Isaac Sim assets path: {assets_root_path}")
    return world


# Example of setting up simulation parameters
def configure_simulation():
    """Configure simulation for optimal humanoid performance"""
    # Enable GPU dynamics if available
    carb.settings.get_settings().set_bool("/physics/physxScene/gpuDynamics", True)
    carb.settings.get_settings().set_bool("/physics/physxScene/gpuCollision", True)
    
    # Configure contact reporting
    carb.settings.get_settings().set_int("/physics/physxScene/maxNumContactHeaders", 4096)
    carb.settings.get_settings().set_int("/physics/physxScene/maxNumContactReports", 4096)
    
    # Configure joint and articulation parameters
    # For humanoid robots, stable joint simulation is critical
    carb.settings.get_settings().set_float("/physics/physxScene/jointLinearTolerance", 0.001)
    carb.settings.get_settings().set_float("/physics/physxScene/jointAngularTolerance", 0.01)
    
    print("Simulation configured with humanoid-appropriate parameters")
```

## Creating a Humanoid Robot in Isaac Sim

### USD Robot Representation

Isaac Sim uses USD (Universal Scene Description) for robot representation. Here's a simplified humanoid model:

```python
# humanoid_robot.py
import omni
from omni.isaac.core import World
from omni.isaac.core.robots import Robot
from omni.isaac.core.utils.nucleus import get_assets_root_path
from omni.isaac.core.utils.stage import add_reference_to_stage
from omni.isaac.core.utils.prims import create_primitive, get_prim_at_path
from omni.isaac.core.articulations import ArticulationView
from omni.isaac.core.utils.stage import get_current_stage
from pxr import UsdGeom, Gf, UsdPhysics, PhysxSchema
import numpy as np


class HumanoidRobot(Robot):
    """Custom humanoid robot class for Isaac Sim"""
    
    def __init__(
        self,
        prim_path: str,
        name: str = "humanoid_robot",
        usd_path: str = None,
        position: np.ndarray = np.array([0.0, 0.0, 0.0]),
        orientation: np.ndarray = np.array([0.0, 0.0, 0.0, 1.0]),
    ) -> None:
        """Initialize the humanoid robot"""
        
        # If no USD path provided, create a simple robot model
        self._default_usd_path = usd_path
        self._position = position
        self._orientation = orientation
        
        super().__init__(
            prim_path=prim_path,
            name=name,
            usd_path=usd_path,
            position=position,
            orientation=orientation,
        )
    
    def initialize_robot(self, world: World):
        """Initialize robot in the simulation world"""
        
        # Add the robot to the scene
        self.robot = world.scene.add(
            Robot(
                prim_path=self.prim_path,
                name=self.name,
                usd_path=self._default_usd_path or self.create_simple_humanoid_usd(),
                position=self._position,
                orientation=self._orientation
            )
        )
        
    def create_simple_humanoid_usd(self):
        """Create a simple humanoid USD representation programmatically"""
        
        stage = get_current_stage()
        
        # Define humanoid joints and links
        humanoid_parts = {
            "base_link": {"position": [0, 0, 0.85], "size": [0.3, 0.25, 0.4]},
            "torso": {"position": [0, 0, 1.1], "size": [0.25, 0.2, 0.6]},
            "head": {"position": [0, 0, 1.6], "size": [0.15, 0.15, 0.15]},
            "left_upper_arm": {"position": [0.15, 0.15, 1.3], "size": [0.08, 0.08, 0.3]},
            "left_lower_arm": {"position": [0.15, 0.15, 1.0], "size": [0.06, 0.06, 0.25]},
            "right_upper_arm": {"position": [0.15, -0.15, 1.3], "size": [0.08, 0.08, 0.3]},
            "right_lower_arm": {"position": [0.15, -0.15, 1.0], "size": [0.06, 0.06, 0.25]},
            "left_thigh": {"position": [0, 0.05, 0.5], "size": [0.08, 0.08, 0.4]},
            "left_calf": {"position": [0, 0.05, 0.1], "size": [0.07, 0.07, 0.4]},
            "left_foot": {"position": [0, 0.05, -0.1], "size": [0.15, 0.07, 0.06]},
            "right_thigh": {"position": [0, -0.05, 0.5], "size": [0.08, 0.08, 0.4]},
            "right_calf": {"position": [0, -0.05, 0.1], "size": [0.07, 0.07, 0.4]},
            "right_foot": {"position": [0, -0.05, -0.1], "size": [0.15, 0.07, 0.06]}
        }
        
        # Create the base link
        create_primitive(
            prim_path=self.prim_path + "/base_link",
            prim_type="Capsule",
            position=humanoid_parts["base_link"]["position"],
            scale=humanoid_parts["base_link"]["size"],
            orientation=Gf.Quatf(self._orientation[3], self._orientation[0], self._orientation[1], self._orientation[2])
        )
        
        # Create all other parts using capsules for efficient collision
        for part_name, part_props in humanoid_parts.items():
            if part_name != "base_link":  # Skip base_link since we already created it
                create_primitive(
                    prim_path=self.prim_path + "/" + part_name,
                    prim_type="Capsule",
                    position=part_props["position"],
                    scale=part_props["size"]
                )
        
        # Add mass and inertia properties to each part
        self.add_inertial_properties()
        
        # Add articulation joints
        self.add_articulation_joints()
        
        print(f"Created simple humanoid model at {self.prim_path}")
    
    def add_inertial_properties(self):
        """Add mass and inertia properties to the robot links"""
        # Define reasonable masses for humanoid robot parts
        link_masses = {
            "base_link": 5.0,     # Pelvis
            "torso": 3.0,         # Torso
            "head": 1.5,          # Head
            "left_upper_arm": 0.8, "right_upper_arm": 0.8,  # Arms
            "left_lower_arm": 0.6, "right_lower_arm": 0.6,
            "left_thigh": 2.0, "right_thigh": 2.0,  # Legs
            "left_calf": 1.5, "right_calf": 1.5,
            "left_foot": 0.5, "right_foot": 0.5
        }
        
        # Apply mass and inertia to each part
        for link_name, mass in link_masses.items():
            link_prim = get_prim_at_path(self.prim_path + "/" + link_name)
            
            # Add mass property
            UsdPhysics.MassAPI.Apply(link_prim)
            mass_api = UsdPhysics.MassAPI.Get(link_prim.GetPrim(), "physics:mass")
            if mass_api:
                mass_api.GetMassAttr().Set(mass)
    
    def add_articulation_joints(self):
        """Add articulation joints to connect robot parts"""
        # In a full implementation, this would create actual ArticulationJoint prims
        # For this chapter, we'll focus on the concepts instead of full implementation
        pass


def load_humanoid_robot(world: World, robot_name: str = "my_humanoid", position: list = [0, 0, 0.85]):
    """Load a humanoid robot into the simulation"""
    
    # Option 1: Use existing NVIDIA Isaac assets
    assets_root_path = get_assets_root_path()
    if assets_root_path:
        # Try to load a humanoid robot if available in assets
        humanoid_asset_path = assets_root_path + "/Isaac/Robots/Franka/franka_alt_fingers.usd"
        
        # If you have a specific humanoid model, replace the path
        # For this example, we'll create a simple one
        robot = HumanoidRobot(
            prim_path="/World/" + robot_name,
            name=robot_name,
            position=np.array(position),
            orientation=np.array([0.0, 0.0, 0.0, 1.0])
        )
        
        robot.initialize_robot(world)
        return robot
    
    # Option 2: Create a simple robot model if no assets are available
    else:
        robot = HumanoidRobot(
            prim_path="/World/" + robot_name,
            name=robot_name,
            position=np.array(position),
            orientation=np.array([0.0, 0.0, 0.0, 1.0])
        )
        
        robot.initialize_robot(world)
        return robot
```

## Environment Setup for Humanoid Training

### Creating Complex Environments

```python
# environment_setup.py
import omni
from omni.isaac.core.utils.stage import add_reference_to_stage
from omni.isaac.core.utils.nucleus import get_assets_root_path
from omni.isaac.core.utils.prims import create_primitive
from pxr import Gf, UsdGeom
import carb
import numpy as np


class HumanoidTrainingEnvironment:
    """Class to create and manage training environments for humanoid robots"""
    
    def __init__(self, world):
        self.world = world
        self.assets_root_path = get_assets_root_path()
    
    def create_indoor_office_environment(self):
        """Create a complex indoor office environment for humanoid training"""
        
        # Create ground plane
        create_primitive(
            prim_path="/World/ground_plane",
            prim_type="Plane",
            scale=np.array([20.0, 20.0, 1.0]),
            position=np.array([0.0, 0.0, 0.0]),
            orientation=np.array([0.0, 0.0, 0.0, 1.0])
        )
        
        # Create walls
        self.create_room_walls()
        
        # Add furniture (tables, chairs)
        self.add_furniture()
        
        # Add obstacles and navigation elements
        self.add_obstacles()
        
        # Add lighting
        self.add_lighting()
        
        print("Indoor office environment created for humanoid training")
    
    def create_room_walls(self):
        """Create walls for the environment"""
        wall_thickness = 0.1
        wall_height = 2.5
        room_size = 10  # 10m x 10m room
        
        # North wall
        create_primitive(
            prim_path="/World/north_wall",
            prim_type="Box",
            position=np.array([0, room_size/2, wall_height/2]),
            scale=np.array([room_size, wall_thickness, wall_height])
        )
        
        # South wall
        create_primitive(
            prim_path="/World/south_wall",
            prim_type="Box",
            position=np.array([0, -room_size/2, wall_height/2]),
            scale=np.array([room_size, wall_thickness, wall_height])
        )
        
        # East wall
        create_primitive(
            prim_path="/World/east_wall",
            prim_type="Box",
            position=np.array([room_size/2, 0, wall_height/2]),
            scale=np.array([wall_thickness, room_size, wall_height])
        )
        
        # West wall
        create_primitive(
            prim_path="/World/west_wall",
            prim_type="Box",
            position=np.array([-room_size/2, 0, wall_height/2]),
            scale=np.array([wall_thickness, room_size, wall_height])
        )
    
    def add_furniture(self):
        """Add furniture to the environment"""
        
        # Add multiple tables
        for i in range(3):
            # Position tables differently
            table_position = np.array([-3 + i*3, 2.0, 0.4])
            create_primitive(
                prim_path=f"/World/table_{i}",
                prim_type="Cylinder",
                position=table_position,
                scale=np.array([0.4, 0.4, 0.8])
            )
            
            # Add objects on tables
            create_primitive(
                prim_path=f"/World/object_{i}",
                prim_type="Sphere",
                position=table_position + np.array([0, 0, 0.5]),
                scale=np.array([0.05, 0.05, 0.05])
            )
        
        # Add chairs
        chair_positions = [
            [-2.5, 2.5, 0.2],
            [-2.5, 1.5, 0.2],
            [0.5, 2.5, 0.2],
            [0.5, 1.5, 0.2],
            [3.5, 2.5, 0.2],
            [3.5, 1.5, 0.2]
        ]
        
        for i, pos in enumerate(chair_positions):
            create_primitive(
                prim_path=f"/World/chair_{i}",
                prim_type="Cylinder",
                position=pos,
                scale=np.array([0.15, 0.15, 0.4])
            )
    
    def add_obstacles(self):
        """Add various obstacles for navigation challenges"""
        
        # Create obstacles of different shapes and sizes
        obstacle_configs = [
            {"type": "box", "position": [-3, -3, 0.2], "scale": [0.5, 0.5, 0.4]},
            {"type": "sphere", "position": [2, -4, 0.3], "scale": [0.3, 0.3, 0.3]},
            {"type": "capsule", "position": [4, 3, 0.4], "scale": [0.2, 0.2, 0.8]}
        ]
        
        for i, config in enumerate(obstacle_configs):
            create_primitive(
                prim_path=f"/World/obstacle_{i}",
                prim_type=config["type"].capitalize(),
                position=config["position"],
                scale=config["scale"]
            )
    
    def add_lighting(self):
        """Add lighting to the environment"""
        
        # Create dome light (like sun light)
        from omni.isaac.core.utils.prims import create_prim
        
        create_prim(
            prim_path="/World/DomeLight",
            prim_type="DomeLight",
            position=np.array([0, 0, 0]),
            attributes={
                "color": (0.8, 0.8, 0.8),
                "intensity": 500
            }
        )
        
        # Add spotlights for more realistic illumination
        create_prim(
            prim_path="/World/SpotLight",
            prim_type="DistantLight",
            position=np.array([5, 5, 10]),
            attributes={
                "color": (1.0, 1.0, 1.0),
                "intensity": 1000
            }
        )
    
    def create_diverse_scenarios(self):
        """Create diverse training scenarios with varying complexity"""
        
        # Scenario 1: Simple corridor
        self.create_corridor_scenario()
        
        # Scenario 2: Complex room with furniture
        self.create_complex_office_scenario()
        
        # Scenario 3: Outdoor environment
        self.create_outdoor_scenario()
    
    def create_corridor_scenario(self):
        """Create a simple corridor environment"""
        
        # Create corridor (two parallel walls)
        create_primitive(
            prim_path="/World/corridor_left_wall",
            prim_type="Box",
            position=np.array([-1.5, 0, 1]),
            scale=np.array([10, 0.1, 2])
        )
        
        create_primitive(
            prim_path="/World/corridor_right_wall",
            prim_type="Box",
            position=np.array([1.5, 0, 1]),
            scale=np.array([10, 0.1, 2])
        )
        
        # Add occasional obstacles in the corridor
        for i in range(5):
            if i % 2 == 0:  # Only add obstacles at some positions
                create_primitive(
                    prim_path=f"/World/corridor_obstacle_{i}",
                    prim_type="Box",
                    position=np.array([0, i*2 - 4, 0.5]),
                    scale=np.array([0.5, 0.5, 1])
                )
    
    def create_complex_office_scenario(self):
        """Create a more complex office environment with cubicles"""
        
        # Create cubicle walls
        for row in range(3):
            for col in range(3):
                x_pos = col * 2.5 - 2.5
                y_pos = row * 2.5 - 2.5
                
                # Create cubicle partition
                create_primitive(
                    prim_path=f"/World/cubicle_wall_{row}_{col}_1",
                    prim_type="Box",
                    position=np.array([x_pos, y_pos + 1.25, 1]),
                    scale=np.array([2.5, 0.05, 2])
                )
                
                create_primitive(
                    prim_path=f"/World/cubicle_wall_{row}_{col}_2",
                    prim_type="Box",
                    position=np.array([x_pos + 1.25, y_pos, 1]),
                    scale=np.array([0.05, 2.5, 2])
                )
    
    def create_outdoor_scenario(self):
        """Create an outdoor environment with terrain variations"""
        
        # Create uneven terrain
        # In practice, this would use heightfield or complex mesh terrain
        # For this example, we'll create a simple outdoor environment
        
        # Ground plane with texture
        create_primitive(
            prim_path="/World/outdoor_ground",
            prim_type="Plane",
            position=np.array([0, 0, 0]),
            scale=np.array([20, 20, 1])
        )
        
        # Add some outdoor elements like trees, benches
        create_primitive(
            prim_path="/World/tree_1",
            prim_type="Cylinder",
            position=np.array([5, 5, 0.5]),
            scale=np.array([0.3, 0.3, 3])
        )
        
        # Add some rocks or terrain features
        rock_positions = [
            [-4, -4, 0.1],
            [-2, 3, 0.15],
            [4, -2, 0.12]
        ]
        
        for i, pos in enumerate(rock_positions):
            create_primitive(
                prim_path=f"/World/rock_{i}",
                prim_type="Sphere",
                position=pos,
                scale=np.array([0.15, 0.15, 0.15])
            )
    
    def randomize_environment(self, seed=None):
        """Randomize elements in the environment for diverse training data"""
        
        if seed:
            np.random.seed(seed)
        
        # Randomize object positions slightly
        for i in range(5):  # For the first 5 objects
            obj_path = f"/World/object_{i}"
            obj_prim = get_prim_at_path(obj_path)
            if obj_prim:
                # Get current position
                current_pos_attr = obj_prim.GetAttribute("xformOp:translate")
                current_pos = current_pos_attr.Get()
                
                # Add small random offset
                random_offset = np.random.uniform(-0.2, 0.2, 3)
                new_pos = [current_pos[j] + random_offset[j] for j in range(3)]
                
                # Update position
                current_pos_attr.Set(new_pos)
        
        print("Environment randomized for diverse training scenarios")


def setup_environment():
    """Main function to set up a humanoid training environment"""
    
    # Initialize Isaac Sim
    world = initialize_humanoid_world()
    if not world:
        print("Failed to initialize Isaac Sim world")
        return
    
    # Create environment
    env = HumanoidTrainingEnvironment(world)
    env.create_indoor_office_environment()
    
    # Randomize environment for training diversity
    env.randomize_environment(seed=42)
    
    print("Humanoid training environment created and ready for simulation")
    
    return world, env
```

## Sensor Integration in Isaac Sim

### Advanced Sensor Configuration

```python
# sensor_integration.py
import omni
from omni.isaac.core.sensors import ImuSensor, CameraSensor, LidarRtx
from omni.isaac.synthetic_utils import plot
from omni.isaac.core.utils.prims import get_prim_at_path
from omni.isaac.core.utils.stage import add_reference_to_stage
from omni.isaac.core.utils.nucleus import get_assets_root_path
from omni.isaac.core.utils.rotations import euler_angles_to_quat
from omni.isaac.core import World
import numpy as np
import carb


class HumanoidSensorSystem:
    """Advanced sensor system for humanoid robots in Isaac Sim"""
    
    def __init__(self, robot_prim_path: str):
        self.robot_prim_path = robot_prim_path
        self.sensors = {}
        
    def add_head_camera(self):
        """Add a camera to the robot's head for perception"""
        
        # Calculate head position (assuming head is a child of torso)
        head_position = [0.0, 0.0, 0.15]  # Offset from robot's origin
        
        # Create camera sensor
        camera = CameraSensor(
            prim_path=self.robot_prim_path + "/head_camera",
            frequency=30,  # 30 Hz
            resolution=(640, 480),  # Resolution
            position=head_position,
            orientation=euler_angles_to_quat(np.array([0, 0, 0]))  # Looking forward
        )
        
        self.sensors['head_camera'] = camera
        print("Head camera added to robot")
        
        return camera
    
    def add_imu_sensors(self):
        """Add IMU sensors to critical locations on the robot"""
        
        # Add IMU to torso (for balance detection)
        torso_imu = ImuSensor(
            prim_path=self.robot_prim_path + "/torso_imu",
            position=np.array([0.0, 0.0, 0.0]),  # At center of torso
            frequency=100  # High frequency for balance control
        )
        
        self.sensors['torso_imu'] = torso_imu
        print("Torso IMU added to robot")
        
        # Add IMU to head (for orientation)
        head_imu = ImuSensor(
            prim_path=self.robot_prim_path + "/head_imu",
            position=np.array([0.0, 0.0, 0.15]),  # At head level
            frequency=100
        )
        
        self.sensors['head_imu'] = head_imu
        print("Head IMU added to robot")
        
        # Add IMUs to feet for contact detection
        left_foot_imu = ImuSensor(
            prim_path=self.robot_prim_path + "/left_foot_imu",
            position=np.array([0.0, 0.08, -0.05]),  # On left foot link
            frequency=100
        )
        
        right_foot_imu = ImuSensor(
            prim_path=self.robot_prim_path + "/right_foot_imu",
            position=np.array([0.0, -0.08, -0.05]),  # On right foot link
            frequency=100
        )
        
        self.sensors['left_foot_imu'] = left_foot_imu
        self.sensors['right_foot_imu'] = right_foot_imu
        print("Foot IMUs added to robot for contact detection")
        
        return [torso_imu, head_imu, left_foot_imu, right_foot_imu]
    
    def add_lidar_sensor(self):
        """Add 3D LiDAR sensor to the robot"""
        
        # Position LiDAR on robot's head
        lidar_position = [0.1, 0.0, 0.15]  # Slightly forward and up from head center
        
        # Configure LiDAR parameters
        lidar_params = {
            "rotation_frequency": 20,  # 20 Hz
            "channels": 16,  # 16 beam height
            "points_per_channel": 1000,
            "horizontal_fov": 360,
            "vertical_fov": 30,
            "range": 25.0,
        }
        
        lidar = LidarRtx(
            prim_path=self.robot_prim_path + "/head_lidar",
            sensor_period=1.0 / lidar_params["rotation_frequency"],
            points_per_channel=lidar_params["points_per_channel"],
            horizontal_fov=lidar_params["horizontal_fov"],
            vertical_fov=lidar_params["vertical_fov"],
            vertical_resolution=lidar_params["channels"],
            range_threshold=lidar_params["range"],
            position=lidar_position,
            orientation=euler_angles_to_quat(np.array([0, 0, 0]))
        )
        
        # Configure noise model for realism
        lidar_config = carb.dictionary.acquire(carb.dictionary.get_path())
        lidar_config.set_string("type", "RotaryLidar")
        lidar_config.set_float("rotation_frequency", lidar_params["rotation_frequency"])
        lidar_config.set_float("range", lidar_params["range"])
        
        self.sensors['head_lidar'] = lidar
        print("Head LiDAR added to robot")
        
        return lidar
    
    def add_force_torque_sensors(self):
        """Add force/torque sensors to robot joints for manipulation"""
        
        # In practice, FT sensors would be added to joint articulations
        # For this example, we'll create the concept
        
        ft_sensors = []
        
        # Add FT sensors to wrists for manipulation
        left_wrist_ft = self.create_force_torque_sensor(
            "/World/LeftWristForceTorqueSensor",
            self.robot_prim_path + "/left_lower_arm",  # Attach to end effector
            np.array([0, 0, -0.15])  # Position at wrist
        )
        
        right_wrist_ft = self.create_force_torque_sensor(
            "/World/RightWristForceTorqueSensor",
            self.robot_prim_path + "/right_lower_arm",  # Attach to end effector
            np.array([0, 0, -0.15])  # Position at wrist
        )
        
        if left_wrist_ft:
            self.sensors['left_wrist_ft'] = left_wrist_ft
            ft_sensors.append(left_wrist_ft)
        
        if right_wrist_ft:
            self.sensors['right_wrist_ft'] = right_wrist_ft
            ft_sensors.append(right_wrist_ft)
        
        print("Force/torque sensors added to robot wrists")
        return ft_sensors
    
    def create_force_torque_sensor(self, prim_path, attach_to, position):
        """Create a force/torque sensor (conceptual in Isaac Sim)"""
        # Isaac Sim doesn't have built-in FT sensors, but this is how you'd implement it
        # Would require custom extension or joint force monitoring
        
        print(f"Added conceptual force/torque sensor at {prim_path}")
        return {
            "prim_path": prim_path,
            "attach_to": attach_to,
            "position": position
        }
    
    def configure_sensor_noise_models(self):
        """Configure realistic noise models for sensors"""
        
        # In a real implementation, this would set noise parameters for each sensor
        # We'll define the concept here
        
        sensor_noise_models = {
            "head_camera": {
                "type": "gaussian",
                "stddev": 0.01,  # Pixel noise
                "bias": 0.0
            },
            "torso_imu": {
                "angular_velocity": {"mean": 0.0, "stddev": 0.01},  # 0.01 rad/s noise
                "linear_acceleration": {"mean": 0.0, "stddev": 0.017},  # 0.017 m/s² noise
            },
            "lidar": {
                "range_stddev": 0.01,  # 1cm range noise
                "angular_stddev": 0.001  # 0.001 rad angular noise
            }
        }
        
        print("Sensor noise models configured for realistic simulation")
        return sensor_noise_models
    
    def get_sensor_data(self, sensor_name):
        """Get data from a specific sensor"""
        if sensor_name not in self.sensors:
            print(f"Sensor {sensor_name} not found")
            return None
        
        sensor = self.sensors[sensor_name]
        
        if hasattr(sensor, 'get_current_frame'):
            # For sensor objects with get_current_frame method
            return sensor.get_current_frame()
        else:
            # For conceptual sensors
            print(f"Getting conceptual data for {sensor_name}")
            return {"timestamp": carb.events.acquire("carb.events.clock").get_current_time(), "data": "placeholder"}
    
    def get_all_sensor_data(self):
        """Get data from all active sensors"""
        sensor_data = {}
        
        for name, sensor in self.sensors.items():
            data = self.get_sensor_data(name)
            if data:
                sensor_data[name] = data
        
        return sensor_data


def setup_sensors_for_robot(robot_prim_path: str):
    """Set up complete sensor system for a humanoid robot"""
    
    sensor_system = HumanoidSensorSystem(robot_prim_path)
    
    # Add all required sensors
    camera = sensor_system.add_head_camera()
    imus = sensor_system.add_imu_sensors()
    lidar = sensor_system.add_lidar_sensor()
    fts = sensor_system.add_force_torque_sensors()
    
    # Configure noise models
    noise_models = sensor_system.configure_sensor_noise_models()
    
    print(f"Complete sensor system set up with {len(sensor_system.sensors)} sensors")
    
    return sensor_system
```

## Synthetic Data Generation Pipeline

### Data Generation for Machine Learning

```python
# synthetic_data_generator.py
import omni
from omni.isaac.synthetic_utils import synthetic_data_generation as sdg
from omni.isaac.synthetic_utils import plot
from omni.isaac.core import World
from omni.isaac.core.utils.stage import add_reference_to_stage
from omni.isaac.core.utils.nucleus import get_assets_root_path
from PIL import Image
import numpy as np
import json
import os
import cv2
from typing import List, Dict, Any
import carb


class SyntheticDataGenerator:
    """System for generating synthetic training data for humanoid robotics"""
    
    def __init__(self, world: World, output_dir: str = "./synthetic_data"):
        self.world = world
        self.output_dir = output_dir
        self.frame_counter = 0
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(f"{output_dir}/images", exist_ok=True)
        os.makedirs(f"{output_dir}/labels", exist_ok=True)
        os.makedirs(f"{output_dir}/depth", exist_ok=True)
        os.makedirs(f"{output_dir}/annotations", exist_ok=True)
        
        self.annotation_data = []
    
    def generate_camera_data(self, camera_sensor, frame_number: int) -> Dict[str, Any]:
        """Generate synthetic camera data with annotations"""
        
        # Get RGB image
        rgb_data = camera_sensor.get_rgb()
        
        # Get depth data
        depth_data = camera_sensor.get_depth()
        
        # Get segmentation data (if available)
        try:
            seg_data = camera_sensor.get_segmentation()
        except:
            seg_data = None
        
        # Save image data
        img_path = f"{self.output_dir}/images/frame_{frame_number:06d}.png"
        Image.fromarray(rgb_data).save(img_path)
        
        # Save depth data
        depth_path = f"{self.output_dir}/depth/depth_{frame_number:06d}.png"
        depth_img = Image.fromarray((depth_data * 1000).astype(np.uint16))  # Scale to 16-bit
        depth_img.save(depth_path)
        
        # Create annotation with robot state
        annotation = {
            "frame_id": frame_number,
            "image_path": img_path,
            "depth_path": depth_path,
            "timestamp": carb.events.acquire("carb.events.clock").get_current_time(),
            "robot_state": self.get_robot_state_annotation(),
            "camera_intrinsics": self.get_camera_intrinsics(camera_sensor),
            "objects_in_scene": self.get_scene_objects()
        }
        
        if seg_data is not None:
            seg_path = f"{self.output_dir}/labels/seg_{frame_number:06d}.png"
            Image.fromarray(seg_data.astype(np.uint16)).save(seg_path)
            annotation["segmentation_path"] = seg_path
        
        return annotation
    
    def get_robot_state_annotation(self):
        """Get robot state for annotation"""
        # In a real implementation, this would get the robot's position, orientation, joint states
        # For this example, we'll return a placeholder
        return {
            "position": {"x": 0.0, "y": 0.0, "z": 0.85},
            "orientation": {"qw": 1.0, "qx": 0.0, "qy": 0.0, "qz": 0.0},
            "joint_states": {"placeholder": True}  # Would contain actual joint positions
        }
    
    def get_camera_intrinsics(self, camera_sensor):
        """Get camera intrinsic parameters"""
        # Would return actual camera parameters from Isaac Sim
        return {
            "fx": 320.0,  # Focal length x
            "fy": 320.0,  # Focal length y
            "cx": 320.0,  # Principal point x
            "cy": 240.0,  # Principal point y
            "width": 640,  # Image width
            "height": 480  # Image height
        }
    
    def get_scene_objects(self):
        """Get information about objects in the scene"""
        # In a real implementation, this would extract object positions from the scene
        # For this example, we'll return a placeholder
        return [
            {
                "name": "table_0",
                "position": {"x": -3.0, "y": 2.0, "z": 0.4},
                "dimensions": {"width": 0.8, "depth": 0.6, "height": 0.8},
                "visible": True
            },
            {
                "name": "chair_0",
                "position": {"x": -2.5, "y": 2.5, "z": 0.2},
                "dimensions": {"width": 0.3, "depth": 0.3, "height": 0.4},
                "visible": True
            }
        ]
    
    def generate_lidar_data(self, lidar_sensor, frame_number: int) -> Dict[str, Any]:
        """Generate synthetic LiDAR data"""
        
        # Get LiDAR scan data
        lidar_data = lidar_sensor.get_point_cloud()
        
        # Process point cloud data
        if lidar_data is not None:
            # Save point cloud as JSON (could also save as PCD or other format)
            pointcloud_data = {
                "frame_id": frame_number,
                "points": lidar_data.tolist(),  # Convert to list for JSON serialization
                "timestamp": carb.events.acquire("carb.events.clock").get_current_time(),
                "sensor_pose": self.get_sensor_pose(lidar_sensor)
            }
            
            # Save point cloud data
            pc_path = f"{self.output_dir}/lidar/lidar_{frame_number:06d}.json"
            with open(pc_path, 'w') as f:
                json.dump(pointcloud_data, f)
            
            return pointcloud_data
    
    def get_sensor_pose(self, sensor):
        """Get the pose of a sensor in the world"""
        # In a real implementation, this would get the actual sensor pose from USD
        # For this example, return a placeholder
        return {
            "position": {"x": 0.1, "y": 0.0, "z": 0.95},
            "orientation": {"qw": 1.0, "qx": 0.0, "qy": 0.0, "qz": 0.0}
        }
    
    def generate_robot_trajectory_data(self, robot, frame_number: int) -> Dict[str, Any]:
        """Generate robot trajectory data"""
        
        try:
            # Get robot position and orientation
            pos, rot = robot.get_world_pose()
            
            # Get robot velocity
            lin_vel, ang_vel = robot.get_linear_velocity(), robot.get_angular_velocity()
            
            # Get joint states if robot has joints
            joint_positions = []  # In practice, get actual joint positions
            joint_velocities = []  # In practice, get actual joint velocities
            
            trajectory_data = {
                "frame_id": frame_number,
                "position": {"x": pos[0], "y": pos[1], "z": pos[2]},
                "rotation": {"qx": rot[0], "qy": rot[1], "qz": rot[2], "qw": rot[3]},
                "linear_velocity": {"x": lin_vel[0], "y": lin_vel[1], "z": lin_vel[2]},
                "angular_velocity": {"x": ang_vel[0], "y": ang_vel[1], "z": ang_vel[2]},
                "joint_positions": joint_positions,
                "joint_velocities": joint_velocities,
                "timestamp": carb.events.acquire("carb.events.clock").get_current_time()
            }
            
            return trajectory_data
            
        except Exception as e:
            carb.log_warn(f"Could not get robot trajectory data: {e}")
            return None
    
    def run_data_generation_cycle(self, sensor_system, robot, cycles: int = 100):
        """Run a complete data generation cycle"""
        
        print(f"Starting synthetic data generation for {cycles} frames...")
        
        for i in range(cycles):
            # Step the world
            self.world.step(render=True)
            
            # Generate data from all sensors
            frame_annotations = {}
            
            # For each sensor in the system
            for sensor_name, sensor in sensor_system.sensors.items():
                if "camera" in sensor_name:
                    annotation = self.generate_camera_data(sensor, self.frame_counter)
                    frame_annotations[sensor_name] = annotation
                elif "lidar" in sensor_name:
                    annotation = self.generate_lidar_data(sensor, self.frame_counter)
                    frame_annotations[sensor_name] = annotation
            
            # Generate robot state data
            if robot:
                robot_data = self.generate_robot_trajectory_data(robot, self.frame_counter)
                if robot_data:
                    frame_annotations["robot_state"] = robot_data
            
            # Add frame annotation to collection
            self.annotation_data.append(frame_annotations)
            
            # Increment frame counter
            self.frame_counter += 1
            
            if i % 10 == 0:  # Log progress every 10 frames
                carb.log_info(f"Generated {i+1}/{cycles} frames")
        
        # Save annotations
        self.save_annotations()
        
        print(f"Synthetic data generation completed! Generated {self.frame_counter} frames")
    
    def save_annotations(self):
        """Save all annotations to JSON file"""
        
        annotation_path = f"{self.output_dir}/annotations.json"
        with open(annotation_path, 'w') as f:
            json.dump(self.annotation_data, f, indent=2)
        
        print(f"Annotations saved to {annotation_path}")
        print(f"Total frames captured: {len(self.annotation_data)}")


def generate_synthetic_training_data():
    """Run complete synthetic data generation pipeline"""
    
    # Initialize Isaac Sim world
    world = initialize_humanoid_world()
    if not world:
        print("Failed to initialize Isaac Sim world")
        return
    
    # Set up environment
    env = HumanoidTrainingEnvironment(world)
    env.create_indoor_office_environment()
    
    # Load a humanoid robot
    robot = load_humanoid_robot(world, "training_humanoid", [0, 0, 0.85])
    
    # Set up sensors for the robot
    sensor_system = setup_sensors_for_robot("/World/training_humanoid")
    
    # Wait for world to settle
    for i in range(100):
        world.step(render=True)
    
    # Create synthetic data generator
    generator = SyntheticDataGenerator(world, "./synthetic_data_humanoid")
    
    # Run data generation
    generator.run_data_generation_cycle(sensor_system, robot, cycles=50)  # Generate 50 frames
    
    # Clean up
    carb.log_info("Synthetic data generation complete!")
    
    return generator


# Example usage
if __name__ == "__main__":
    generator = generate_synthetic_training_data()