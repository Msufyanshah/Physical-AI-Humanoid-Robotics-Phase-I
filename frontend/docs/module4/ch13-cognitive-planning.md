---
title: 'Chapter 13 - Cognitive Planning: Natural Language → ROS Actions'
description: 'Advanced cognitive planning systems that translate natural language commands into sequences of robotic actions'
---

# Chapter 13: Cognitive Planning: Natural Language → ROS Actions

## Learning Objectives

After reading this chapter, you will be able to:
- Design cognitive architectures for NL-to-actions translation
- Implement hierarchical task planning from natural language
- Create symbolic and subsymbolic reasoning systems
- Develop domain ontologies for robotic tasks
- Plan complex multi-step actions from user commands
- Handle ambiguity and uncertainty in natural language
- Validate and verify the correctness of action plans
- Optimize planning algorithms for real-time robotics

## Introduction

Cognitive planning bridges the gap between high-level natural language commands and low-level robotic actions. This chapter explores the challenges of translating human instructions into executable robotic behaviors, covering both symbolic reasoning for planning and subsymbolic methods for handling uncertainty. The goal is to create systems that can understand complex commands like "Clean up the living room by putting books back on the shelf and disposing of waste in the bin" and break them down into a sequence of executable actions.

## Cognitive Architecture for NL-to-Actions

### Hierarchical Cognitive Structure

A cognitive architecture for language-to-actions consists of several layers:

1. **Language Understanding**: Parsing and semantic interpretation
2. **Conceptual Representation**: Mapping linguistic concepts to robot capabilities
3. **Task Planning**: Decomposing tasks into subtasks
4. **Action Sequencing**: Ordering actions based on constraints
5. **Execution Monitoring**: Verifying execution and handling failures

### The SPA (Symbolic-Subsymbolic Architecture)

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Pose, Point
from action_msgs.msg import GoalStatus
from typing import List, Dict, Any, Optional, Tuple
import json
import re
from dataclasses import dataclass


@dataclass
class LinguisticConcept:
    """Representation of a concept extracted from natural language"""
    name: str
    category: str  # object, location, action, property
    attributes: Dict[str, Any]
    confidence: float


@dataclass
class SymbolicAction:
    """Symbolic representation of an action to be executed"""
    action_type: str  # move_to, pick_up, place_down, etc.
    parameters: Dict[str, Any]
    preconditions: List[str]
    effects: List[str]
    priority: int = 0


@dataclass
class TaskPlan:
    """Hierarchical plan representation"""
    main_task: str
    subtasks: List[SymbolicAction]
    dependencies: List[Tuple[str, str]]  # (source_task, dest_task) dependencies
    context: Dict[str, Any]


class CognitiveArchitecture(Node):
    def __init__(self):
        super().__init__('cognitive_architecture')
        
        # Publishers and subscribers
        self.nl_command_sub = self.create_subscription(
            String, '/natural_language_command', self.nl_command_callback, 10
        )
        
        self.action_command_pub = self.create_publisher(
            String, '/robot_action_commands', 10
        )
        
        self.world_state_pub = self.create_publisher(
            String, '/world_state_update', 10
        )
        
        # Components
        self.language_understanding = LanguageUnderstanding()
        self.concept_mapping = ConceptMapper()
        self.task_planner = HierarchicalTaskPlanner()
        self.executor = ActionExecutor()
        
        # Robot capabilities
        self.robot_capabilities = {
            'navigation': True,
            'manipulation': True,
            'grasping': True,
            'detection': True
        }
        
        # Current world state
        self.world_state = {
            'objects': {},
            'locations': {},
            'robot_position': {'x': 0.0, 'y': 0.0, 'z': 0.0},
            'robot_orientation': {'x': 0.0, 'y': 0.0, 'z': 0.0, 'w': 1.0}
        }
        
        self.get_logger().info("Cognitive Architecture initialized")
    
    def nl_command_callback(self, msg: String):
        """Process natural language command"""
        command_text = msg.data
        self.get_logger().info(f"Received NL command: '{command_text}'")
        
        try:
            # Step 1: Language Understanding
            concepts = self.language_understanding.parse_command(command_text)
            
            # Step 2: Concept Mapping
            mapped_concepts = []
            for concept in concepts:
                mapped = self.concept_mapping.map_to_robot_concept(concept, self.world_state)
                if mapped:
                    mapped_concepts.append(mapped)
            
            # Step 3: Task Planning
            if mapped_concepts:
                plan = self.task_planner.generate_plan(
                    mapped_concepts, 
                    self.world_state, 
                    self.robot_capabilities
                )
                
                if plan:
                    # Step 4: Execution
                    success = self.executor.execute_plan(plan)
                    
                    if success:
                        self.get_logger().info(f"Successfully executed plan for command: '{command_text}'")
                    else:
                        self.get_logger().error(f"Failed to execute plan for command: '{command_text}'")
                else:
                    self.get_logger().warn(f"Could not generate plan for command: '{command_text}'")
            else:
                self.get_logger().warn(f"No concepts extracted from command: '{command_text}'")
                
        except Exception as e:
            self.get_logger().error(f"Error processing command '{command_text}': {e}")
    
    def update_world_state(self, update: Dict[str, Any]):
        """Update internal world state representation"""
        for key, value in update.items():
            if key in self.world_state:
                if isinstance(self.world_state[key], dict) and isinstance(value, dict):
                    self.world_state[key].update(value)
                else:
                    self.world_state[key] = value
            else:
                self.world_state[key] = value
        
        # Publish world state update
        state_msg = String()
        state_msg.data = json.dumps(self.world_state)
        self.world_state_pub.publish(state_msg)


class LanguageUnderstanding:
    """Component responsible for parsing natural language commands"""
    
    def __init__(self):
        # Define action verbs and their semantic roles
        self.action_verbs = {
            'move': ['to', 'toward', 'at'],  # move to x
            'go': ['to', 'toward', 'at'],    # go to x
            'pick': ['up', 'grasp', 'take'], # pick up x
            'place': ['down', 'put', 'leave'], # place down x
            'bring': ['to', 'over', 'here'], # bring x to y
            'fetch': [],                      # fetch x
            'clean': ['up', 'off'],          # clean up x
            'find': [],                      # find x
            'search': ['for'],               # search for x
            'turn': ['left', 'right', 'around'], # turn left/right
        }
        
        # Object categories
        self.object_categories = [
            'book', 'cup', 'ball', 'chair', 'table', 
            'box', 'pen', 'phone', 'laptop', 'waste', 'trash'
        ]
        
        # Location phrases
        self.location_phrases = [
            'kitchen', 'living room', 'bedroom', 'office', 
            'shelf', 'bin', 'desk', 'cabinet', 'corner'
        ]
        
        # Spatial relations
        self.spatial_relations = [
            'on', 'in', 'at', 'near', 'beside', 'behind', 'in front of', 'left of', 'right of'
        ]
    
    def parse_command(self, command: str) -> List[LinguisticConcept]:
        """Parse command and extract linguistic concepts"""
        concepts = []
        command_lower = command.lower()
        
        # Extract action concepts
        for verb, prep_list in self.action_verbs.items():
            if verb in command_lower:
                # Create action concept
                action_concept = LinguisticConcept(
                    name=verb,
                    category='action',
                    attributes={'verb': verb, 'prepositions': prep_list},
                    confidence=0.8  # High confidence for explicit verbs
                )
                concepts.append(action_concept)
        
        # Extract object concepts
        for obj in self.object_categories:
            if obj in command_lower:
                # Find context around the object
                pattern = r'(\w+)\s*' + obj  # Look for adjectives before the object
                match = re.search(pattern, command_lower)
                
                attributes = {'object_type': obj}
                if match:
                    # Capture adjective or other descriptors
                    attributes['descriptor'] = match.group(1)
                
                obj_concept = LinguisticConcept(
                    name=obj,
                    category='object',
                    attributes=attributes,
                    confidence=0.7
                )
                concepts.append(obj_concept)
        
        # Extract location concepts
        for loc in self.location_phrases:
            if loc in command_lower:
                loc_concept = LinguisticConcept(
                    name=loc,
                    category='location',
                    attributes={'location_type': loc},
                    confidence=0.7
                )
                concepts.append(loc_concept)
        
        # Extract spatial relations
        for relation in self.spatial_relations:
            if relation in command_lower:
                rel_concept = LinguisticConcept(
                    name=relation,
                    category='spatial_relation',
                    attributes={'relation_type': relation},
                    confidence=0.6
                )
                concepts.append(rel_concept)
        
        return concepts


class ConceptMapper:
    """Maps linguistic concepts to robot concepts/capabilities"""
    
    def __init__(self):
        # Define mappings from linguistic concepts to robot concepts
        self.robot_actions = {
            'move': 'navigate_to_pose',
            'go': 'navigate_to_pose',
            'pick': 'grasp_object',
            'place': 'release_object',
            'bring': 'transport_object',
            'fetch': 'transport_object',
            'clean': 'collect_objects',
            'find': 'detect_object',
            'search': 'detect_object',
            'turn': 'rotate_in_place'
        }
        
        # Location mappings
        self.location_mappings = {
            'kitchen': {'x': 3.0, 'y': 1.0, 'z': 0.0},
            'bedroom': {'x': -2.0, 'y': 2.0, 'z': 0.0},
            'living room': {'x': 0.0, 'y': 0.0, 'z': 0.0},
            'office': {'x': -1.0, 'y': -1.5, 'z': 0.0},
            'shelf': {'x': 1.5, 'y': 0.2, 'z': 0.8},  # Example shelf location
            'bin': {'x': 0.5, 'y': -1.5, 'z': 0.2},  # Example bin location
            'desk': {'x': 1.0, 'y': 0.5, 'z': 0.75}
        }
    
    def map_to_robot_concept(self, linguistic_concept: LinguisticConcept, world_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Map linguistic concept to robot-specific concept"""
        if linguistic_concept.category == 'action':
            # Map to robot action
            robot_action = self.robot_actions.get(linguistic_concept.name)
            if robot_action:
                return {
                    'type': 'robot_action',
                    'action': robot_action,
                    'original_verb': linguistic_concept.name,
                    'confidence': linguistic_concept.confidence
                }
        
        elif linguistic_concept.category == 'location':
            # Map to specific coordinates if known
            location_coords = self.location_mappings.get(linguistic_concept.name.lower())
            if location_coords:
                return {
                    'type': 'location',
                    'coordinates': location_coords,
                    'name': linguistic_concept.name,
                    'confidence': linguistic_concept.confidence
                }
            else:
                # Location not in known mappings, may need to be learned
                return {
                    'type': 'location',
                    'name': linguistic_concept.name,
                    'is_unknown': True,
                    'confidence': linguistic_concept.confidence
                }
        
        elif linguistic_concept.category == 'object':
            # Find object in world state
            obj_name = linguistic_concept.name
            if obj_name in world_state.get('objects', {}):
                obj_info = world_state['objects'][obj_name]
                return {
                    'type': 'object_instance',
                    'name': obj_name,
                    'properties': obj_info.get('properties', {}),
                    'position': obj_info.get('position', {}),
                    'confidence': linguistic_concept.confidence
                }
        
        elif linguistic_concept.category == 'spatial_relation':
            return {
                'type': 'spatial_relation',
                'relation': linguistic_concept.name,
                'confidence': linguistic_concept.confidence
            }
        
        return None


class HierarchicalTaskPlanner:
    """Generates hierarchical plans from concepts and world state"""
    
    def __init__(self):
        self.action_effects = {
            'navigate_to_pose': {
                'adds': ['at_pose'],
                'removes': []  # Remove 'not_at_pose'
            },
            'grasp_object': {
                'adds': ['has_object'],
                'removes': ['object_on_surface']
            },
            'release_object': {
                'adds': ['object_on_surface'],
                'removes': ['has_object']
            },
            'detect_object': {
                'adds': ['object_detected'],
                'removes': ['object_not_detected']
            }
        }
    
    def generate_plan(self, concepts: List[Dict[str, Any]], world_state: Dict[str, Any], 
                     robot_capabilities: Dict[str, bool]) -> Optional[TaskPlan]:
        """Generate a hierarchical task plan from concepts"""
        # This is a simplified planner - in practice, you'd use more sophisticated planning algorithms
        # like HTN (Hierarchical Task Network) or STRIPS
        
        # Identify the main task
        main_action = None
        for concept in concepts:
            if concept['type'] == 'robot_action':
                main_action = concept['action']
                break
        
        if not main_action:
            return None
        
        # Generate subtasks based on action type
        subtasks = []
        dependencies = []
        
        if main_action == 'transport_object':
            # Transport involves: find object -> grasp -> navigate -> release
            required_concepts = [c for c in concepts if c['type'] in ['object_instance', 'location']]
            
            if len(required_concepts) < 2:
                self.get_logger().warn(f"Insufficient concepts for transport task: {required_concepts}")
                return None
            
            # Find object and destination concepts
            obj_concept = next((c for c in required_concepts if c['type'] == 'object_instance'), None)
            dest_concept = next((c for c in required_concepts if c['type'] == 'location' and c.get('coordinates')), None)
            
            if not obj_concept or not dest_concept:
                return None
            
            # Create subtasks
            subtasks = [
                SymbolicAction(
                    action_type='detect_object',
                    parameters={'object_name': obj_concept['name']},
                    preconditions=[],
                    effects=['object_detected']
                ),
                SymbolicAction(
                    action_type='grasp_object',
                    parameters={'object_name': obj_concept['name']},
                    preconditions=['object_detected'],
                    effects=['has_object']
                ),
                SymbolicAction(
                    action_type='navigate_to_pose',
                    parameters={'position': dest_concept['coordinates']},
                    preconditions=['has_object'],
                    effects=['at_destination']
                ),
                SymbolicAction(
                    action_type='release_object',
                    parameters={'object_name': obj_concept['name']},
                    preconditions=['at_destination', 'has_object'],
                    effects=['object_delivered']
                )
            ]
            
            # Define dependencies: detect -> grasp -> navigate -> release
            dependencies = [
                ('detect_object', 'grasp_object'),
                ('grasp_object', 'navigate_to_pose'),
                ('navigate_to_pose', 'release_object')
            ]
        
        elif main_action == 'navigate_to_pose':
            # Simple navigation task
            dest_concept = next((c for c in concepts if c['type'] == 'location' and c.get('coordinates')), None)
            
            if not dest_concept:
                return None
            
            subtasks = [
                SymbolicAction(
                    action_type='navigate_to_pose',
                    parameters={'position': dest_concept['coordinates']},
                    preconditions=[],
                    effects=['at_destination']
                )
            ]
        
        elif main_action == 'collect_objects':
            # Clean up task - find objects -> pick up -> dispose
            # This is more complex and would require iterating over objects
            object_concepts = [c for c in concepts if c['type'] == 'object_instance']
            
            for i, obj_concept in enumerate(object_concepts):
                # Find waste bin or disposal location
                disposal_loc = self.find_disposal_location(world_state)
                
                if disposal_loc:
                    # Create action sequence for this object
                    obj_subtasks = [
                        SymbolicAction(
                            action_type='navigate_to_pose',
                            parameters={'position': obj_concept['position']},
                            preconditions=[f'completed_obj_{i-1}'] if i > 0 else [],
                            effects=[f'at_obj_{i}_location']
                        ),
                        SymbolicAction(
                            action_type='grasp_object',
                            parameters={'object_name': obj_concept['name']},
                            preconditions=[f'at_obj_{i}_location'],
                            effects=[f'has_obj_{i}']
                        ),
                        SymbolicAction(
                            action_type='navigate_to_pose',
                            parameters={'position': disposal_loc},
                            preconditions=[f'has_obj_{i}'],
                            effects=[f'at_disposal_{i}']
                        ),
                        SymbolicAction(
                            action_type='release_object',
                            parameters={'object_name': obj_concept['name']},
                            preconditions=[f'at_disposal_{i}'],
                            effects=[f'disposed_obj_{i}']
                        )
                    ]
                    
                    obj_dependencies = [
                        (f'navigate_to_{i}', f'grasp_{i}'),
                        (f'grasp_{i}', f'navigate_to_disposal_{i}'),
                        (f'navigate_to_disposal_{i}', f'release_{i}')
                    ]
                    
                    if i > 0:
                        obj_dependencies.append((f'disposed_obj_{i-1}', f'navigate_to_{i}'))
                    
                    subtasks.extend(obj_subtasks)
                    dependencies.extend(obj_dependencies)
        
        # Create and return plan
        plan = TaskPlan(
            main_task=main_action,
            subtasks=subtasks,
            dependencies=dependencies,
            context={'original_concepts': concepts}
        )
        
        return plan
    
    def find_disposal_location(self, world_state: Dict[str, Any]) -> Optional[Dict[str, float]]:
        """Find waste bin or disposal location in the world"""
        # In practice, this would look in the world state for disposal locations
        # For now, return a hardcoded disposal location
        return {'x': 0.5, 'y': -1.5, 'z': 0.2}
    
    def get_logger(self):
        """Mock logger for this class"""
        class MockLogger:
            def info(self, msg): print(f"INFO: {msg}")
            def warn(self, msg): print(f"WARN: {msg}")
            def error(self, msg): print(f"ERROR: {msg}")
        return MockLogger()


class ActionExecutor:
    """Executes hierarchical plans"""
    
    def __init__(self):
        # Track execution state
        self.execution_state = {
            'current_task': None,
            'completed_tasks': [],
            'failed_tasks': [],
            'world_state_changes': []
        }
    
    def execute_plan(self, plan: TaskPlan) -> bool:
        """Execute a hierarchical task plan"""
        self.get_logger().info(f"Executing plan: {plan.main_task}")
        
        # Execute subtasks in order respecting dependencies
        successful = True
        
        for i, subtask in enumerate(plan.subtasks):
            # Check preconditions
            all_preconditions_met = self.check_preconditions(subtask.preconditions)
            
            if not all_preconditions_met:
                self.get_logger().warn(f"Preconditions not met for task {i}: {subtask.action_type}")
                successful = False
                break
            
            # Execute the subtask
            task_success = self.execute_subtask(subtask)
            
            if task_success:
                # Update execution state
                self.execution_state['completed_tasks'].append(subtask.action_type)
                
                # Apply effects to state
                for effect in subtask.effects:
                    self.apply_effect(effect)
                
                self.get_logger().info(f"Completed task {i}: {subtask.action_type}")
            else:
                self.get_logger().error(f"Failed to execute task {i}: {subtask.action_type}")
                self.execution_state['failed_tasks'].append(subtask.action_type)
                successful = False
                break
        
        return successful
    
    def check_preconditions(self, preconditions: List[str]) -> bool:
        """Check if preconditions are satisfied"""
        # In practice, this would check the actual world state
        # For now, assume all conditions are met
        return True
    
    def execute_subtask(self, subtask: SymbolicAction) -> bool:
        """Execute a single subtask"""
        # This would interface with actual robot action services
        # For now, just simulate execution
        
        action = subtask.action_type
        params = subtask.parameters
        
        self.get_logger().info(f"Executing action: {action} with params: {params}")
        
        # Simulate different actions
        if action == 'navigate_to_pose':
            return self.simulate_navigation(params['position'])
        elif action == 'grasp_object':
            return self.simulate_grasp(params['object_name'])
        elif action == 'release_object':
            return self.simulate_release(params['object_name'])
        elif action == 'detect_object':
            return self.simulate_detection(params['object_name'])
        else:
            # Unknown action type
            self.get_logger().warn(f"Unknown action type: {action}")
            return False
    
    def simulate_navigation(self, position: Dict[str, float]) -> bool:
        """Simulate navigation to position"""
        # In a real system, this would call navigation services
        self.get_logger().info(f"Navigating to position: {position}")
        # Simulate success
        return True
    
    def simulate_grasp(self, object_name: str) -> bool:
        """Simulate grasping an object"""
        self.get_logger().info(f"Grasping object: {object_name}")
        # Simulate success
        return True
    
    def simulate_release(self, object_name: str) -> bool:
        """Simulate releasing an object"""
        self.get_logger().info(f"Releasing object: {object_name}")
        # Simulate success
        return True
    
    def simulate_detection(self, object_name: str) -> bool:
        """Simulate detecting an object"""
        self.get_logger().info(f"Detecting object: {object_name}")
        # Simulate success
        return True
    
    def apply_effect(self, effect: str):
        """Apply an action effect to the world state"""
        # This would update the internal world model
        self.execution_state['world_state_changes'].append(effect)
    
    def get_logger(self):
        """Mock logger"""
        class MockLogger:
            def info(self, msg): print(f"EXEC INFO: {msg}")
            def warn(self, msg): print(f"EXEC WARN: {msg}")
            def error(self, msg): print(f"EXEC ERROR: {msg}")
        return MockLogger()


def main(args=None):
    rclpy.init(args=args)
    
    # Initialize cognitive architecture
    cognitive_arch = CognitiveArchitecture()
    
    # Example commands to test
    test_commands = [
        "Go to the kitchen",
        "Pick up the red ball",
        "Bring the book to the desk",
        "Clean up the trash"
    ]
    
    # For demonstration, manually publish test commands
    import threading
    import time
    
    def publish_test_commands():
        time.sleep(2)  # Wait for node to be ready
        
        command_pub = cognitive_arch.create_publisher(String, '/natural_language_command', 10)
        
        for cmd in test_commands:
            cmd_msg = String()
            cmd_msg.data = cmd
            command_pub.publish(cmd_msg)
            cognitive_arch.get_logger().info(f"Published test command: '{cmd}'")
            time.sleep(3)  # Wait between commands
    
    # Start publishing test commands in a separate thread
    test_thread = threading.Thread(target=publish_test_commands, daemon=True)
    test_thread.start()
    
    try:
        rclpy.spin(cognitive_arch)
    except KeyboardInterrupt:
        pass
    finally:
        cognitive_arch.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Symbolic Planning Approaches

### Hierarchical Task Networks (HTN)

Hierarchical Task Networks decompose high-level tasks into primitive actions:

```python
# htn_planner.py
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class Task:
    """A task in the HTN hierarchy"""
    name: str
    args: List[Any]
    decomposition: Optional[List['Method']] = None
    is_primitive: bool = False


@dataclass
class Method:
    """Method to decompose a compound task"""
    name: str
    task: Task
    subtasks: List[Task]
    preconditions: List[str]


class HTNPlanner:
    """Hierarchical Task Network planner"""
    
    def __init__(self):
        self.methods = {}  # Maps task names to methods
        self.predicates = set()  # Current state predicates
        self.setup_domain_methods()
    
    def setup_domain_methods(self):
        """Define methods for the robotics domain"""
        # Method to clean a room
        clean_room_method = Method(
            name="clean_room_method",
            task=Task("clean_room", ["room"]),
            subtasks=[
                Task("collect_trash", ["room"]),
                Task("organize_items", ["room"]),
            ],
            preconditions=["room_exists"]
        )
        
        # Method to transport an object
        transport_method = Method(
            name="transport_method",
            task=Task("transport", ["object", "source", "destination"]),
            subtasks=[
                Task("navigate_to", ["source"]),
                Task("pick_up", ["object"]),
                Task("navigate_to", ["destination"]),
                Task("place_down", ["object"])
            ],
            preconditions=["object_exists", "destination_reachable"]
        )
        
        # Method to collect trash
        collect_trash_method = Method(
            name="collect_trash_method",
            task=Task("collect_trash", ["room"]),
            subtasks=[
                Task("find_waste", ["room"]),
                Task("transport", ["waste", "current_location", "disposal_bin"])
            ],
            preconditions=["room_has_trash"]
        )
        
        # Store methods by task name
        self.methods["clean_room"] = [clean_room_method]
        self.methods["transport"] = [transport_method]
        self.methods["collect_trash"] = [collect_trash_method]
    
    def plan(self, goal_task: Task, initial_state: List[str]) -> Optional[List[Task]]:
        """Generate a plan for the goal task"""
        self.predicates = set(initial_state)
        
        # Use HTN planning algorithm to decompose tasks
        return self.decompose_task(goal_task, initial_state)
    
    def decompose_task(self, task: Task, state: List[str]) -> Optional[List[Task]]:
        """Decompose a task using available methods"""
        if task.is_primitive:
            # Return task as-is if it's primitive
            return [task]
        
        # Get applicable methods for this task
        applicable_methods = self.methods.get(task.name, [])
        
        for method in applicable_methods:
            if self.check_preconditions(method.preconditions, state):
                # Decompose the subtasks
                plan = []
                for subtask in method.subtasks:
                    subplan = self.decompose_task(subtask, state)
                    if subplan is None:
                        # This method didn't work, try the next one
                        break
                    plan.extend(subplan)
                else:
                    # All subtasks were successfully decomposed
                    return plan
        
        # No method worked
        return None
    
    def check_preconditions(self, preconditions: List[str], state: List[str]) -> bool:
        """Check if preconditions are satisfied in the current state"""
        return all(pc in state for pc in preconditions)


# Example usage
def example_htn_usage():
    planner = HTNPlanner()
    
    # Define initial state
    initial_state = [
        "room_exists", "room_has_trash", 
        "object_exists", "destination_reachable"
    ]
    
    # Plan to clean the living room
    goal = Task("clean_room", ["living_room"])
    goal.is_primitive = False
    
    plan = planner.plan(goal, initial_state)
    
    if plan:
        print("Plan generated:")
        for i, action in enumerate(plan):
            if action.is_primitive:
                print(f"  {i+1}. {action.name} {action.args}")
    else:
        print("Could not generate plan for goal")


if __name__ == "__main__":
    example_htn_usage()
```

### STRIPS-like Planning

```python
# strips_planner.py
from typing import Set, List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class Operator:
    """STRIPS operator with preconditions and effects"""
    name: str
    preconditions: Set[str]
    add_list: Set[str]  # Facts to add
    delete_list: Set[str]  # Facts to remove
    parameters: List[str]


class STRIPSPlanner:
    """STRIPS-style planner for robotic tasks"""
    
    def __init__(self):
        self.operators = [
            Operator(
                name="navigate_to",
                preconditions={"at(X)", "not_obstructed(X,Y)"},
                add_list={"at(Y)"},
                delete_list={"at(X)"},
                parameters=["X", "Y"]  # from X to Y
            ),
            Operator(
                name="pick_up",
                preconditions={"at(robot)", "at(object)", "is_reachable(object)", "hands_free"},
                add_list={"has(object)"},
                delete_list={"hands_free", "at(object)"},
                parameters=["object"]
            ),
            Operator(
                name="place_down",
                preconditions={"has(object)", "at(location)"},
                add_list={"at(object)", "hands_free"},
                delete_list={"has(object)"},
                parameters=["object", "location"]
            ),
            Operator(
                name="find_object",
                preconditions={"at(robot)", "location_has(object)"},
                add_list={"at(object)"},
                delete_list=set(),
                parameters=["object"]
            )
        ]
    
    def plan(self, initial_state: Set[str], goal_state: Set[str]) -> Optional[List[Tuple[str, List[str]]]]:
        """Generate plan using backward chaining"""
        return self.backward_chain(goal_state, initial_state, [])
    
    def backward_chain(self, 
                      goal_state: Set[str], 
                      current_state: Set[str], 
                      used_operators: List[Tuple[str, List[str]]]) -> Optional[List[Tuple[str, List[str]]]]:
        """Backward chain from goal to initial state"""
        # Check if goal is already satisfied
        if goal_state.issubset(current_state):
            return used_operators
        
        # Find operator that achieves one of the goals
        for op in self.operators:
            # Try to ground the operator to achieve part of the goal
            for assignment in self.find_assignments(op, goal_state):
                # Check if preconditions can be satisfied
                op_instance = self.instantiate_operator(op, assignment)
                
                if op_instance.preconditions.issubset(current_state):
                    # Apply operator
                    new_state = self.apply_operator(current_state, op_instance)
                    
                    # Recursively plan for remaining goals
                    remaining_goals = goal_state - new_state
                    if remaining_goals:  # Still have unmet goals
                        result = self.backward_chain(remaining_goals, new_state, 
                                                     used_operators + [(op.name, assignment)])
                        if result is not None:
                            return result
                    else:
                        # All goals satisfied
                        return used_operators + [(op.name, assignment)]
        
        # Could not satisfy goals
        return None
    
    def find_assignments(self, operator: Operator, goals: Set[str]) -> List[List[str]]:
        """Find parameter assignments that could satisfy part of the goals"""
        # This is a simplified version
        # In practice, you'd use more sophisticated unification
        assignments = []
        
        # Look for goals that match the operator's add list
        for goal in goals:
            for param_idx, param in enumerate(operator.parameters):
                # Try to match goal with operator parameters
                # This is highly simplified - in practice you'd have more complex matching
                pass
        
        return assignments
    
    def instantiate_operator(self, operator: Operator, assignment: List[str]) -> Operator:
        """Create an instance of an operator with specific parameter values"""
        # Substitute parameters with actual values
        preconditions = set()
        add_list = set()
        delete_list = set()
        
        for prec in operator.preconditions:
            substituted_prec = prec
            for i, val in enumerate(assignment):
                substituted_prec = substituted_prec.replace(f"{operator.parameters[i]}", val)
            preconditions.add(substituted_prec)
        
        for add in operator.add_list:
            substituted_add = add
            for i, val in enumerate(assignment):
                substituted_add = substituted_add.replace(f"{operator.parameters[i]}", val)
            add_list.add(substituted_add)
        
        for delete in operator.delete_list:
            substituted_delete = delete
            for i, val in enumerate(assignment):
                substituted_delete = substituted_delete.replace(f"{operator.parameters[i]}", val)
            delete_list.add(substituted_delete)
        
        return Operator(
            name=operator.name,
            preconditions=preconditions,
            add_list=add_list,
            delete_list=delete_list,
            parameters=assignment
        )
    
    def apply_operator(self, state: Set[str], operator: Operator) -> Set[str]:
        """Apply operator to state"""
        new_state = state.copy()
        
        # Remove deleted facts
        new_state -= operator.delete_list
        
        # Add new facts
        new_state |= operator.add_list
        
        return new_state


# Example usage
def example_strips_usage():
    planner = STRIPSPlanner()
    
    # Initial state
    initial = {"at(kitchen)", "at(book)", "is_reachable(book)", "hands_free", "location_has(book)"}
    
    # Goal state
    goal = {"at(desk)", "has(book)"}
    
    plan = planner.plan(initial, goal)
    
    if plan:
        print("Plan found:")
        for i, (action, params) in enumerate(plan):
            print(f"  {i+1}. {action}({', '.join(params)})")
    else:
        print("No plan found")


if __name__ == "__main__":
    example_strips_usage()
```

## Planning with Uncertainty and Contingencies

### Probabilistic Planning

Robotic environments often involve uncertainty, so planning must account for probabilistic outcomes:

```python
# probabilistic_planner.py
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ProbabilisticOperator:
    """Operator with probabilistic effects"""
    name: str
    preconditions: List[str]
    effects: List[Tuple[str, float]]  # (effect, probability)
    cost: float = 1.0


class ProbabilisticPlanner:
    """Planner that considers uncertainty in action outcomes"""
    
    def __init__(self):
        self.operators = [
            ProbabilisticOperator(
                name="grasp_object",
                preconditions=["at_object", "hand_free"],
                effects=[
                    ("object_grasped", 0.95),  # 95% success
                    ("object_dropped", 0.04),  # 4% chance of dropping
                    ("grasp_failed", 0.01)     # 1% complete failure
                ],
                cost=1.0
            ),
            ProbabilisticOperator(
                name="navigate_to_location",
                preconditions=["navigation_enabled"],
                effects=[
                    ("at_destination", 0.90),
                    ("at_partial_path", 0.08),
                    ("navigation_failure", 0.02)
                ],
                cost=2.0
            ),
            ProbabilisticOperator(
                name="find_object",
                preconditions=["in_searchable_area"],
                effects=[
                    ("object_located", 0.80),
                    ("object_not_found", 0.20)
                ],
                cost=3.0
            )
        ]
    
    def calculate_expected_outcome(self, action: ProbabilisticOperator, current_state: Set[str]) -> float:
        """Calculate expected utility of an action"""
        if not all(pc in current_state for pc in action.preconditions):
            return float('-inf')  # Action not applicable
        
        expected_utility = 0.0
        
        for effect, probability in action.effects:
            # Simple utility function - in practice this would be more complex
            if effect.startswith("object_grasped"):
                utility = 10.0  # High utility for grasping
            elif effect.startswith("at_destination"):
                utility = 5.0   # Medium utility for navigation
            elif effect.startswith("object_located"):
                utility = 3.0   # Lower utility for finding
            else:
                utility = -1.0  # Negative for failures
            
            expected_utility += probability * utility - action.cost
        
        return expected_utility
    
    def find_best_action(self, state: Set[str], goal: str) -> Optional[ProbabilisticOperator]:
        """Find action with highest expected utility"""
        best_action = None
        best_expected_utility = float('-inf')
        
        for op in self.operators:
            expected_utility = self.calculate_expected_outcome(op, state)
            
            if expected_utility > best_expected_utility:
                best_expected_utility = expected_utility
                best_action = op
        
        return best_action


# Example usage
def example_probabilistic_planning():
    planner = ProbabilisticPlanner()
    
    # Current state
    state = {"at_object", "hand_free", "navigation_enabled", "in_searchable_area"}
    
    # Find best action to achieve a goal
    best_action = planner.find_best_action(state, "object_grasped")
    
    if best_action:
        print(f"Best action: {best_action.name}")
        print(f"Expected utility: {planner.calculate_expected_outcome(best_action, state):.2f}")
    else:
        print("No suitable action found")


if __name__ == "__main__":
    example_probabilistic_planning()
```

## Multi-Modal Planning

### Integrating Perception and Action Planning

For cognitive planning to be effective, it must integrate multiple sensory modalities:

```python
# multimodal_planning.py
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from vision_msgs.msg import Detection2DArray
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import String
from typing import Dict, Any, Optional
import json


class MultiModalPlannerNode(Node):
    def __init__(self):
        super().__init__('multimodal_planner')
        
        # Publishers and subscribers
        self.image_sub = self.create_subscription(Image, '/camera/rgb/image_raw', self.image_callback, 10)
        self.detection_sub = self.create_subscription(Detection2DArray, '/object_detections', self.detection_callback, 10)
        self.pose_sub = self.create_subscription(PoseStamped, '/robot_pose', self.pose_callback, 10)
        self.command_sub = self.create_subscription(String, '/nl_command', self.command_callback, 10)
        
        self.plan_pub = self.create_publisher(String, '/action_plan', 10)
        self.feedback_pub = self.create_publisher(String, '/planning_feedback', 10)
        
        # Internal state
        self.current_objects = {}  # Detected objects and their states
        self.robot_pose = None
        self.recent_detections = []
        self.planning_context = {}
        
        # Initialize components
        self.cognitive_planner = CognitiveArchitecture()
        
        self.get_logger().info("MultiModal Planner Node initialized")
    
    def image_callback(self, msg):
        """Process camera images"""
        # In practice, you might run additional processing
        # For now, just trigger object detection updates
        pass
    
    def detection_callback(self, msg):
        """Process object detections and update internal state"""
        for detection in msg.detections:
            if detection.results:
                for result in detection.results:
                    object_id = result.id
                    confidence = result.score
                    
                    if confidence > 0.5:  # Only significant detections
                        # Update object state
                        self.update_object_state(
                            object_id,
                            detection.bbox.center.x,
                            detection.bbox.center.y,
                            confidence
                        )
        
        # Keep recent detections to handle tracking
        self.recent_detections.append({
            'timestamp': self.get_clock().now(),
            'detections': msg.detections
        })
        
        # Limit history
        if len(self.recent_detections) > 10:
            self.recent_detections = self.recent_detections[-10:]
    
    def pose_callback(self, msg):
        """Update robot pose"""
        self.robot_pose = {
            'position': {
                'x': msg.pose.position.x,
                'y': msg.pose.position.y, 
                'z': msg.pose.position.z
            },
            'orientation': {
                'x': msg.pose.orientation.x,
                'y': msg.pose.orientation.y,
                'z': msg.pose.orientation.z,
                'w': msg.pose.orientation.w
            }
        }
    
    def update_object_state(self, object_id: str, x: float, y: float, confidence: float):
        """Update internal state for a detected object"""
        if object_id not in self.current_objects:
            self.current_objects[object_id] = {
                'first_seen': self.get_clock().now(),
                'positions': [],
                'confidences': []
            }
        
        self.current_objects[object_id]['positions'].append({'x': x, 'y': y, 'z': 0.0})
        self.current_objects[object_id]['confidences'].append(confidence)
        
        # Keep only recent positions (last 5)
        if len(self.current_objects[object_id]['positions']) > 5:
            self.current_objects[object_id]['positions'] = self.current_objects[object_id]['positions'][-5:]
            self.current_objects[object_id]['confidences'] = self.current_objects[object_id]['confidences'][-5:]
    
    def command_callback(self, msg: String):
        """Process natural language command with multimodal context"""
        command_text = msg.data
        self.get_logger().info(f"Processing multimodal command: '{command_text}'")
        
        # Build multimodal context
        context = self.build_multimodal_context()
        
        try:
            # Process command with context
            plan = self.cognitive_planner.process_command_with_context(
                command_text, 
                context
            )
            
            if plan:
                # Publish the generated plan
                plan_msg = String()
                plan_msg.data = json.dumps({
                    'command': command_text,
                    'plan': plan,
                    'timestamp': self.get_clock().now().seconds_nanoseconds()
                })
                
                self.plan_pub.publish(plan_msg)
                self.get_logger().info(f"Published action plan for command: '{command_text}'")
                
                # Provide feedback
                feedback_msg = String()
                feedback_msg.data = f"Understood command '{command_text}'. Executing plan with {len(plan['subtasks'])} steps."
                self.feedback_pub.publish(feedback_msg)
            else:
                feedback_msg = String()
                feedback_msg.data = f"Could not understand or plan for command: '{command_text}'"
                self.feedback_pub.publish(feedback_msg)
                self.get_logger().warn(f"Could not generate plan for command: '{command_text}'")
                
        except Exception as e:
            self.get_logger().error(f"Error processing command '{command_text}': {e}")
            feedback_msg = String()
            feedback_msg.data = f"Error processing command: {str(e)}"
            self.feedback_pub.publish(feedback_msg)
    
    def build_multimodal_context(self) -> Dict[str, Any]:
        """Build context incorporating visual and spatial information"""
        context = {
            'robot_state': self.robot_pose or {},
            'objects': {},
            'environment_map': {},  # In practice, would come from mapping system
            'recent_interactions': [],  # Recent commands and outcomes
            'sensory_input': {
                'objects_detected': len(self.current_objects),
                'last_detection_time': str(self.recent_detections[-1]['timestamp']) if self.recent_detections else None
            }
        }
        
        # Add object information with confidence and position history
        for obj_id, obj_data in self.current_objects.items():
            avg_pos = self.calculate_average_position(obj_data['positions'])
            avg_conf = sum(obj_data['confidences']) / len(obj_data['confidences'])
            
            context['objects'][obj_id] = {
                'avg_position': avg_pos,
                'avg_confidence': avg_conf,
                'is_graspable': self.is_graspable(obj_id, avg_pos),  # Placeholder
                'object_type': self.infer_object_type(obj_id)  # Placeholder
            }
        
        # Add spatial relationships based on relative positions
        context['spatial_relationships'] = self.calculate_spatial_relationships(context['objects'])
        
        return context
    
    def calculate_average_position(self, positions: List[Dict[str, float]]) -> Dict[str, float]:
        """Calculate average position from recent detections"""
        if not positions:
            return {'x': 0.0, 'y': 0.0, 'z': 0.0}
        
        avg_x = sum(p['x'] for p in positions) / len(positions)
        avg_y = sum(p['y'] for p in positions) / len(positions)
        avg_z = sum(p['z'] for p in positions) / len(positions)
        
        return {'x': avg_x, 'y': avg_y, 'z': avg_z}
    
    def is_graspable(self, object_id: str, position: Dict[str, float]) -> bool:
        """Determine if an object is graspable"""
        # This would involve more sophisticated logic based on:
        # - Object size and shape (from detection)
        # - Robot reach (from robot state)
        # - Object accessibility (from environment map)
        
        # Simplified check: is within reach of robot?
        if self.robot_pose:
            dist_to_robot = np.sqrt(
                (position['x'] - self.robot_pose['position']['x'])**2 +
                (position['y'] - self.robot_pose['position']['y'])**2
            )
            return 0.1 < dist_to_robot < 1.0  # Within 10cm to 1m
        return False
    
    def infer_object_type(self, object_id: str) -> str:
        """Infer object type from detection result (placeholder)"""
        # In practice, this would use the detection result's label
        return "object"
    
    def calculate_spatial_relationships(self, objects: Dict[str, Any]) -> List[Dict[str, str]]:
        """Calculate spatial relationships between objects"""
        relationships = []
        
        for obj1_id, obj1_data in objects.items():
            for obj2_id, obj2_data in objects.items():
                if obj1_id != obj2_id:
                    # Calculate relative position
                    dx = obj2_data['avg_position']['x'] - obj1_data['avg_position']['x']
                    dy = obj2_data['avg_position']['y'] - obj1_data['avg_position']['y']
                    
                    angle = np.arctan2(dy, dx)
                    distance = np.sqrt(dx**2 + dy**2)
                    
                    # Determine spatial relationship
                    if distance < 0.5:  # Less than 50cm apart
                        if abs(np.cos(angle)) > abs(np.sin(angle)):
                            # More horizontal relationship
                            rel = "right_of" if dx > 0 else "left_of"
                        else:
                            # More vertical relationship
                            rel = "above" if dy > 0 else "below"
                        
                        relationships.append({
                            'subject': obj1_id,
                            'relationship': rel,
                            'object': obj2_id,
                            'distance': distance
                        })
        
        return relationships


def main(args=None):
    rclpy.init(args=args)
    node = MultiModalPlannerNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Plan Execution and Monitoring

### Execution Architecture

The execution component monitors plan progress and handles failures:

```python
# execution_monitor.py
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
from action_msgs.msg import GoalStatus
from geometry_msgs.msg import PoseStamped
from sensor_msgs.msg import JointState
import json
from enum import Enum
from typing import Dict, Any, Optional, Callable


class ExecutionStatus(Enum):
    IDLE = "idle"
    EXECUTING = "executing"
    PAUSED = "paused"
    FAILED = "failed"
    COMPLETED = "completed"


class ExecutionMonitor(Node):
    def __init__(self):
        super().__init__('execution_monitor')
        
        # Publishers and subscribers
        self.plan_sub = self.create_subscription(String, '/action_plan', self.plan_callback, 10)
        self.status_pub = self.create_publisher(String, '/execution_status', 10)
        self.action_feedback_sub = self.create_subscription(String, '/action_feedback', self.feedback_callback, 10)
        
        self.cancel_pub = self.create_publisher(Bool, '/execution_cancel', 10)
        self.continue_pub = self.create_publisher(Bool, '/execution_continue', 10)
        
        # Internal state
        self.current_plan = None
        self.current_step = 0
        self.execution_status = ExecutionStatus.IDLE
        self.execution_history = []
        
        # Action execution feedback
        self.action_feedback = {}
        
        # Timer for monitoring
        self.monitor_timer = self.create_timer(0.1, self.monitor_execution)
        
        self.get_logger().info("Execution Monitor initialized")
    
    def plan_callback(self, msg: String):
        """Receive and process new plan"""
        try:
            plan_data = json.loads(msg.data)
            self.receive_plan(plan_data)
        except json.JSONDecodeError:
            self.get_logger().error(f"Invalid JSON in plan message: {msg.data}")
    
    def receive_plan(self, plan_data: Dict[str, Any]):
        """Process incoming plan"""
        self.current_plan = plan_data
        self.current_step = 0
        self.execution_status = ExecutionStatus.EXECUTING
        
        self.get_logger().info(f"Received plan with {len(self.current_plan['plan']['subtasks'])} steps")
        
        # Start execution of first step
        if self.current_plan['plan']['subtasks']:
            self.execute_current_step()
    
    def feedback_callback(self, msg: String):
        """Receive feedback from action execution"""
        try:
            feedback_data = json.loads(msg.data)
            self.process_feedback(feedback_data)
        except json.JSONDecodeError:
            self.get_logger().error(f"Invalid JSON in feedback message: {msg.data}")
    
    def process_feedback(self, feedback_data: Dict[str, Any]):
        """Process feedback from action execution"""
        action_id = feedback_data.get('action_id')
        status = feedback_data.get('status')
        result = feedback_data.get('result')
        
        self.action_feedback[action_id] = {
            'status': status,
            'result': result,
            'timestamp': self.get_clock().now()
        }
        
        # Update execution based on feedback
        if status == 'failed':
            self.handle_action_failure(action_id, result)
        elif status == 'completed':
            self.handle_action_success(action_id, result)
    
    def execute_current_step(self):
        """Execute the current step in the plan"""
        if not self.current_plan or self.current_step >= len(self.current_plan['plan']['subtasks']):
            self.execution_status = ExecutionStatus.COMPLETED
            self.publish_status()
            return
        
        current_action = self.current_plan['plan']['subtasks'][self.current_step]
        action_id = f"action_{self.current_step}_{current_action['action_type']}"
        
        self.get_logger().info(f"Executing step {self.current_step + 1}/{len(self.current_plan['plan']['subtasks'])}: {current_action['action_type']}")
        
        # Send action command for execution
        # In a real system, this would call appropriate action servers/services
        self.publish_action_command(current_action, action_id)
        
        # Wait for feedback or timeout
        self.wait_for_action_feedback(action_id)
    
    def publish_action_command(self, action: Dict[str, Any], action_id: str):
        """Publish command for action execution"""
        command_msg = String()
        command_data = {
            'action_id': action_id,
            'action_type': action['action_type'],
            'parameters': action['parameters'],
            'plan_id': self.current_plan.get('command', 'unknown') if self.current_plan else 'unknown'
        }
        command_msg.data = json.dumps(command_data)
        
        # Publish to appropriate action execution topic
        # This would be specific to the action type
        action_topic = f"/execute_{action['action_type']}"
        pub = self.create_publisher(String, action_topic, 10)
        pub.publish(command_msg)
    
    def wait_for_action_feedback(self, action_id: str):
        """Wait for feedback from action execution"""
        # In practice, you'd have a timeout mechanism
        # For now, we'll check in the monitor timer
        pass
    
    def handle_action_failure(self, action_id: str, result: Any):
        """Handle action failure"""
        self.get_logger().error(f"Action {action_id} failed with result: {result}")
        
        # Determine if we should retry or replan
        if self.should_retry_action(action_id):
            self.retry_action(action_id)
        elif self.should_replan():
            self.trigger_replanning()
        else:
            self.execution_status = ExecutionStatus.FAILED
            self.publish_status()
    
    def handle_action_success(self, action_id: str, result: Any):
        """Handle action success"""
        self.get_logger().info(f"Action {action_id} completed successfully")
        
        # Update execution history
        self.execution_history.append({
            'action_id': action_id,
            'status': 'completed',
            'result': result,
            'timestamp': self.get_clock().now().seconds_nanoseconds()
        })
        
        # Move to next step
        self.current_step += 1
        if self.current_step < len(self.current_plan['plan']['subtasks']):
            self.execute_current_step()
        else:
            self.execution_status = ExecutionStatus.COMPLETED
            self.publish_status()
            self.get_logger().info("Plan execution completed successfully")
    
    def should_retry_action(self, action_id: str) -> bool:
        """Determine if action should be retried"""
        # Check if this action has already been retried
        retry_count = sum(1 for h in self.execution_history if h['action_id'] == action_id)
        return retry_count < 3  # Retry up to 3 times
    
    def retry_action(self, action_id: str):
        """Retry the failed action"""
        self.get_logger().info(f"Retrying action {action_id}")
        # Find the action in the plan and execute it again
        action_idx = int(action_id.split('_')[1])
        action = self.current_plan['plan']['subtasks'][action_idx]
        self.publish_action_command(action, f"{action_id}_retry")
    
    def should_replan(self) -> bool:
        """Determine if we should replan"""
        # For now, simple heuristic: if we've failed repeatedly
        recent_failures = [h for h in self.execution_history[-5:] if h.get('status') == 'failed']
        return len(recent_failures) >= 3
    
    def trigger_replanning(self):
        """Trigger replanning process"""
        self.get_logger().info("Triggering replanning due to repeated failures")
        
        # Publish message to trigger replanning
        # This would typically go to the cognitive architecture
        replan_msg = String()
        replan_data = {
            'reason': 'execution_failure',
            'failed_actions': [h for h in self.execution_history if h.get('status') == 'failed'],
            'current_state': self.get_current_world_state()
        }
        replan_msg.data = json.dumps(replan_data)
        
        # Publish to replanning topic
        replan_pub = self.create_publisher(String, '/replan_request', 10)
        replan_pub.publish(replan_msg)
        
        self.execution_status = ExecutionStatus.FAILED
        self.publish_status()
    
    def get_current_world_state(self) -> Dict[str, Any]:
        """Get current world state for replanning"""
        # This would integrate information from all sensors
        # and the planning context
        return {
            'robot_pose': {},  # Would come from localization
            'objects_detected': [],  # Would come from perception
            'recent_actions': [h for h in self.execution_history[-10:]]  # Recent history
        }
    
    def monitor_execution(self):
        """Timer callback to monitor execution"""
        # Check for timeouts on actions
        # In practice, you'd track action timestamps and check for delays
        
        # Publish current status
        self.publish_status()
    
    def publish_status(self):
        """Publish execution status"""
        status_msg = String()
        status_data = {
            'status': self.execution_status.value,
            'current_step': self.current_step,
            'total_steps': self.current_plan['plan']['subtasks'] if self.current_plan else 0,
            'progress': (self.current_step / len(self.current_plan['plan']['subtasks'])) if self.current_plan and self.current_plan['plan']['subtasks'] else 0,
            'timestamp': self.get_clock().now().seconds_nanoseconds()
        }
        status_msg.data = json.dumps(status_data)
        self.status_pub.publish(status_msg)


def main(args=None):
    rclpy.init(args=args)
    node = ExecutionMonitor()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Verification and Validation

### Plan Validation Techniques

To ensure plans are correct and safe, we need validation techniques:

```python
# plan_validation.py
from typing import Dict, List, Tuple, Set, Any
import networkx as nx


class PlanValidator:
    """Validates plans for correctness, safety, and feasibility"""
    
    def __init__(self):
        # Define robot constraints
        self.constraints = {
            'workspace_limits': {
                'x': (-5.0, 5.0),
                'y': (-5.0, 5.0),
                'z': (0.0, 2.0)
            },
            'joint_limits': {
                'shoulder': (-1.57, 1.57),
                'elbow': (-2.0, 2.0),
                'wrist': (-3.14, 3.14)
            },
            'payload_limits': 2.0,  # kg
            'speed_limits': 1.0  # m/s
        }
        
        # Define safety constraints
        self.safety_constraints = [
            "no_collision_with_obstacles",
            "maintain_base_stability",  # For mobile robots
            "avoid_self_collision",
            "respect_joint_velocity_limits"
        ]
    
    def validate_plan(self, plan: List[Dict[str, Any]], initial_state: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a complete plan"""
        results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'metrics': {
                'total_duration': 0.0,
                'energy_estimate': 0.0,
                'safety_score': 1.0
            }
        }
        
        # Check plan structure
        if not plan:
            results['is_valid'] = False
            results['errors'].append("Empty plan provided")
            return results
        
        # Validate each step
        current_state = initial_state.copy()
        
        for i, step in enumerate(plan):
            step_errors = self.validate_step(step, current_state)
            
            if step_errors:
                results['is_valid'] = False
                for error in step_errors:
                    results['errors'].append(f"Step {i}: {error}")
            else:
                # Update state for next validation
                current_state = self.apply_effects(current_state, step.get('effects', []))
        
        # Check global plan properties
        global_errors = self.validate_global_properties(plan)
        for error in global_errors:
            results['errors'].append(f"Global: {error}")
        
        if results['errors']:
            results['is_valid'] = False
        
        return results
    
    def validate_step(self, step: Dict[str, Any], current_state: Dict[str, Any]) -> List[str]:
        """Validate a single step in the plan"""
        errors = []
        
        action_type = step.get('action_type')
        parameters = step.get('parameters', {})
        
        if action_type == 'navigate_to_pose':
            errors.extend(self.validate_navigation(parameters, current_state))
        elif action_type == 'grasp_object':
            errors.extend(self.validate_grasping(parameters, current_state))
        elif action_type == 'move_arm':
            errors.extend(self.validate_arm_movement(parameters, current_state))
        
        return errors
    
    def validate_navigation(self, params: Dict[str, Any], state: Dict[str, Any]) -> List[str]:
        """Validate navigation action"""
        errors = []
        
        position = params.get('position', {})
        x = position.get('x', 0)
        y = position.get('y', 0)
        z = position.get('z', 0)
        
        # Check workspace limits
        limits = self.constraints['workspace_limits']
        if not (limits['x'][0] <= x <= limits['x'][1]):
            errors.append(f"X coordinate {x} outside workspace limits {limits['x']}")
        if not (limits['y'][0] <= y <= limits['y'][1]):
            errors.append(f"Y coordinate {y} outside workspace limits {limits['y']}")
        if not (limits['z'][0] <= z <= limits['z'][1]):
            errors.append(f"Z coordinate {z} outside workspace limits {limits['z']}")
        
        # Check for obstacles in path (simplified)
        if state.get('map') and self.check_path_for_obstacles(state['map'], state.get('robot_position', {}), position):
            errors.append("Path to destination contains obstacles")
        
        return errors
    
    def validate_grasping(self, params: Dict[str, Any], state: Dict[str, Any]) -> List[str]:
        """Validate grasping action"""
        errors = []
        
        obj_name = params.get('object_name')
        obj_position = params.get('object_position', {})
        
        # Check if object exists
        if obj_name not in state.get('objects', {}):
            errors.append(f"Object {obj_name} does not exist in current state")
        
        # Check if object is reachable
        robot_pos = state.get('robot_position', {'x': 0, 'y': 0, 'z': 0})
        if obj_position:
            dist = self.calculate_distance(robot_pos, obj_position)
            if dist > 1.0:  # 1 meter reach limit
                errors.append(f"Object {obj_name} is out of reach (distance: {dist:.2f}m)")
        
        # Check payload limit if we're planning to grasp
        obj_weight = state.get('objects', {}).get(obj_name, {}).get('weight', 0)
        if obj_weight > self.constraints['payload_limits']:
            errors.append(f"Object {obj_name} weighs {obj_weight}kg, exceeding payload limit of {self.constraints['payload_limits']}kg")
        
        return errors
    
    def validate_arm_movement(self, params: Dict[str, Any], state: Dict[str, Any]) -> List[str]:
        """Validate arm movement action"""
        errors = []
        
        joints = params.get('joint_positions', {})
        
        # Check joint limits
        for joint_name, position in joints.items():
            if joint_name in self.constraints['joint_limits']:
                limits = self.constraints['joint_limits'][joint_name]
                if not (limits[0] <= position <= limits[1]):
                    errors.append(f"Joint {joint_name} position {position} violates limits {limits}")
        
        return errors
    
    def validate_global_properties(self, plan: List[Dict[str, Any]]) -> List[str]:
        """Validate global plan properties"""
        errors = []
        
        # Check for conflicting actions
        action_graph = self.build_action_dependency_graph(plan)
        
        # Detect cycles in dependencies
        try:
            # If there's a cycle, the graph isn't a DAG
            nx.algorithms.dag.topological_sort(action_graph)
        except nx.NetworkXUnfeasible:
            errors.append("Plan contains circular dependencies between actions")
        
        return errors
    
    def build_action_dependency_graph(self, plan: List[Dict[str, Any]]) -> nx.DiGraph:
        """Build dependency graph between actions"""
        G = nx.DiGraph()
        
        for i, action in enumerate(plan):
            action_id = f"action_{i}_{action['action_type']}"
            G.add_node(action_id)
            
            # Add dependencies based on preconditions and effects
            # This is simplified - in practice would be more complex
            for j, prev_action in enumerate(plan[:i]):
                prev_action_id = f"action_{j}_{prev_action['action_type']}"
                
                # If current action's preconditions are satisfied by previous action's effects
                # add an edge
                if self.actions_have_dependency(prev_action, action):
                    G.add_edge(prev_action_id, action_id)
        
        return G
    
    def actions_have_dependency(self, prev_action: Dict[str, Any], curr_action: Dict[str, Any]) -> bool:
        """Check if two actions have a dependency"""
        # Simplified dependency checking
        # In practice, would check preconditions vs effects more rigorously
        prev_effects = set(prev_action.get('effects', []))
        curr_preconditions = set(curr_action.get('preconditions', []))
        
        return bool(prev_effects.intersection(curr_preconditions))
    
    def check_path_for_obstacles(self, map_data: Any, start_pos: Dict[str, Any], end_pos: Dict[str, Any]) -> bool:
        """Check if path between positions has obstacles"""
        # This is a simplified check
        # In practice would implement path planning algorithm
        # like A* or RRT to check for obstacles
        return False  # Assume path is clear for now
    
    def calculate_distance(self, pos1: Dict[str, Any], pos2: Dict[str, Any]) -> float:
        """Calculate Euclidean distance between two positions"""
        dx = pos2.get('x', 0) - pos1.get('x', 0)
        dy = pos2.get('y', 0) - pos1.get('y', 0)
        dz = pos2.get('z', 0) - pos1.get('z', 0)
        
        return (dx**2 + dy**2 + dz**2)**0.5
    
    def apply_effects(self, state: Dict[str, Any], effects: List[str]) -> Dict[str, Any]:
        """Apply action effects to create new state"""
        # This is a simplified state transition
        new_state = state.copy()
        
        # In practice, would have more sophisticated state update logic
        for effect in effects:
            if effect.startswith('at_'):
                obj_name = effect[3:]  # Remove 'at_' prefix
                new_state['robot_position'] = new_state['objects'][obj_name]['position'] if new_state.get('objects', {}).get(obj_name) else {}
            elif effect.startswith('has_'):
                obj_name = effect[4:]  # Remove 'has_' prefix
                held_objects = new_state.get('held_objects', [])
                if obj_name not in held_objects:
                    held_objects.append(obj_name)
                    new_state['held_objects'] = held_objects
        
        return new_state


# Example usage
def example_validation():
    validator = PlanValidator()
    
    # Create a sample plan
    sample_plan = [
        {
            'action_type': 'navigate_to_pose',
            'parameters': {
                'position': {'x': 1.0, 'y': 1.0, 'z': 0.0}
            },
            'preconditions': ['navigation_enabled'],
            'effects': ['at_location_kitchen']
        },
        {
            'action_type': 'grasp_object',
            'parameters': {
                'object_name': 'coffee_cup'
            },
            'preconditions': ['at_location_kitchen', 'object_visible'],
            'effects': ['has_coffee_cup']
        }
    ]
    
    # Initial state
    initial_state = {
        'robot_position': {'x': 0.0, 'y': 0.0, 'z': 0.0},
        'objects': {
            'coffee_cup': {'position': {'x': 1.0, 'y': 1.0, 'z': 0.8}, 'weight': 0.3}
        },
        'navigation_enabled': True,
        'map': {}  # Empty for this example
    }
    
    # Validate the plan
    result = validator.validate_plan(sample_plan, initial_state)
    
    print(f"Plan validation result: {result['is_valid']}")
    if result['errors']:
        print("Errors found:")
        for error in result['errors']:
            print(f"  - {error}")
    else:
        print("Plan is valid!")


if __name__ == "__main__":
    example_validation()
```

## Chapter Summary

This chapter covered cognitive planning that translates natural language commands into sequences of robotic actions. We explored hierarchical cognitive architectures, symbolic planning approaches (HTN, STRIPS), planning under uncertainty, multi-modal integration, execution monitoring, and plan validation techniques. Creating robust NL-to-actions systems requires combining several AI techniques: natural language understanding, symbolic reasoning, probabilistic planning, and execution monitoring.

## Checklist

- [ ] Design hierarchical cognitive architecture
- [ ] Implement HTN or STRIPS planner
- [ ] Handle uncertainty in action outcomes
- [ ] Integrate perception and action planning
- [ ] Implement execution monitoring
- [ ] Validate plans for safety and correctness
- [ ] Test with complex multi-step commands
- [ ] Optimize for real-time performance

## Exercises

### Exercise 1: Basic NL-to-Actions Mapping

Create a simple system that maps basic English commands to robot actions.

#### Solution

1. Implement a command parser that recognizes simple commands
2. Create action mappings for basic operations
3. Generate execution sequences
4. Test with commands like "go to the kitchen" and "pick up the cup"

#### Hints

- Start with simple verb-object-location patterns
- Use keyword spotting for basic understanding
- Implement a finite state machine for action sequencing
- Handle simple error cases gracefully

### Exercise 2: Context-Aware Planning

Extend the system to maintain context across multiple commands.

#### Solution

1. Implement world state tracking
2. Add object reference resolution
3. Maintain spatial relationships
4. Handle follow-up commands appropriately

#### Hints

- Use ROS2 lifecycle to manage state
- Consider time decay for old information
- Implement spatial reasoning for location commands
- Add user feedback mechanisms

## References

- [Planning for Humans in Uncertain Environments](https://www.sciencedirect.com/science/article/pii/S0004370218302217)
- [Hierarchical Task Networks in AI Planning](https://aaai.org/ojs/index.php/AAAI/article/view/4748)
- [Probabilistic Robotics by Thrun, Burgard, Fox](https://mitpress.mit.edu/books/probabilistic-robotics)
- [AI Planning: A Guide to Equilibrium, Expressiveness, and Implementation](https://www.cs.rochester.edu/users/faculty/hanks/aij-plan-survey.pdf)
- [Natural Language Generation in Dialogue Systems](https://aclanthology.org/J00-2003/)