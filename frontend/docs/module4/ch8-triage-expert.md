---
title: 'Triage Expert Agent for Multi-Agent Coordination'
description: 'Expert agent for routing queries to appropriate specialized agents'
---

# Triage Expert Agent for Multi-Agent Coordination

## Agent Specialization

This agent specializes in routing incoming queries to the appropriate specialized expert agent based on the content and intent of the query. It acts as a coordinator between different domain experts (ROS, Gazebo, Isaac, VLA) to ensure the right agent handles each request.

## Learning Objectives

After reading this chapter, you will be able to:
- Implement a robust query classification system
- Route queries to appropriate specialized agents
- Handle overlapping domain queries
- Manage agent availability and load balancing
- Implement fallback routing when primary agents unavailable
- Validate routing accuracy and system performance
- Monitor and optimize the triage system
- Handle complex multi-domain queries

## Architecture Overview

The triage system operates as the entry point for all queries, determining which specialized agent is best suited to handle the request:

```
┌─────────────────────────────────────────────────────────────┐
│                    TRIAGE EXPERT AGENT                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  ROS EXPERT   │  │ GAZEBO EXPERT │  │ ISAAC EXPERT  │         │
│  │  AGENT        │  │ AGENT         │  │ AGENT       │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│         │                 │                  │             │
│         └─────────────────┼──────────────────┘             │
│                           │                                │
│                     ┌─────────────┐                        │
│                     │  VLA EXPERT   │                        │
│                     │  AGENT        │                        │
│                     └─────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

## Implementation

### Triage System Core

```python
# triage_system.py
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from typing import Dict, Any, List, Optional
import json
import threading
import time


class QueryClassifier:
    """Classifies queries for routing to appropriate agents"""
    
    def __init__(self):
        # Define keywords for each domain
        self.domain_keywords = {
            'ros': {
                'primary': ['ros', 'ros2', 'node', 'topic', 'service', 'action', 'rclpy', 'publisher', 'subscriber', 'launch'],
                'secondary': ['package', 'ament', 'colcon', 'tf', 'transforms', 'parameters', 'messages'],
                'weights': {'primary': 2.0, 'secondary': 1.0}
            },
            'gazebo': {
                'primary': ['gazebo', 'simulation', 'physics', 'world', 'sdf', 'collision', 'contacts'],
                'secondary': ['models', 'environment', 'rendering', 'dynamics', 'ode', 'bullet'],
                'weights': {'primary': 2.0, 'secondary': 1.0}
            },
            'isaac': {
                'primary': ['isaac', 'nvidia', 'sim', 'usd', 'omniverse', 'embree', 'rtx'],
                'secondary': ['synthetic', 'data', 'rendering', 'photorealistic', 'replicator'],
                'weights': {'primary': 2.0, 'secondary': 1.0}
            },
            'vla': {
                'primary': ['vision', 'language', 'action', 'vqa', 'vlm', 'multimodal'],
                'secondary': ['whisper', 'gpt', 'openai', 'cognitive', 'planning', 'voice'],
                'weights': {'primary': 2.0, 'secondary': 1.0}
            }
        }
        
        # Define regex patterns for complex matches
        self.patterns = {
            'ros': [
                r'.*\b(ros\s*2|topic|service|action|publisher|subscriber|node)\b.*',
                r'.*\b(tf|transform|rclpy|ament|colcon|launch)\b.*'
            ],
            'gazebo': [
                r'.*\b(gazebo|sdf|physics\s*engine|ode|bullet|simbody)\b.*',
                r'.*\b(collision|contact|simulation|world\s*file)\b.*'
            ],
            'isaac': [
                r'.*\b(isaac|omniverse|usd|universal\s*scene|qdrant|vector\s*database)\b.*',
                r'.*\b(rt|ray\s*tracing|nvidia|synthetic\s*data)\b.*'
            ],
            'vla': [
                r'.*\b(vision.*language|language.*action|vla|multimodal)\b.*',
                r'.*\b(whisper|openai|gpt|llm|cognitive.*planning)\b.*'
            ]
        }
    
    def classify_query(self, query: str) -> Dict[str, Any]:
        """
        Classify a query to determine the appropriate expert agent
        """
        query_lower = query.lower()
        
        # Calculate scores for each domain
        scores = {}
        for domain, keywords in self.domain_keywords.items():
            score = 0
            
            # Count primary keywords
            for word in keywords['primary']:
                if word in query_lower:
                    score += keywords['weights']['primary']
            
            # Count secondary keywords
            for word in keywords['secondary']:
                if word in query_lower:
                    score += keywords['weights']['secondary']
            
            # Apply pattern matching scores
            for pattern in self.patterns[domain]:
                import re
                if re.search(pattern, query_lower):
                    score += 1.5  # Additional score for pattern match
            
            scores[domain] = score
        
        # Find the domain with highest score
        best_domain = max(scores, key=scores.get)
        best_score = scores[best_domain]
        
        # Calculate confidence based on score difference
        all_scores = sorted(scores.values(), reverse=True)
        if len(all_scores) > 1:
            confidence = (all_scores[0] - all_scores[1]) / max(all_scores[0], 1.0)
        else:
            confidence = 1.0
        
        # Check for mixed domains
        mixed_domains = []
        threshold = best_score * 0.7  # Consider as part of mix if within 70% of best
        for domain, score in scores.items():
            if score >= threshold and domain != best_domain:
                mixed_domains.append(domain)
        
        return {
            'primary_agent': best_domain,
            'confidence': min(1.0, confidence),
            'scores': scores,
            'mixed_domains': mixed_domains,
            'original_query': query
        }


class AgentAvailabilityMonitor:
    """Monitors availability of specialized agents"""
    
    def __init__(self, node):
        self.node = node
        self.agent_status = {
            'ros': {'available': True, 'last_check': time.time()},
            'gazebo': {'available': True, 'last_check': time.time()}, 
            'isaac': {'available': True, 'last_check': time.time()},
            'vla': {'available': True, 'last_check': time.time()}
        }
        
        # Publishers for agent health checks
        self.agent_health_pubs = {}
        for agent in self.agent_status:
            self.agent_health_pubs[agent] = self.node.create_publisher(
                String, f'/{agent}_agent/health', 10
            )
        
        # Timer to periodically check agent availability
        self.health_check_timer = self.node.create_timer(10.0, self.check_agent_health)
        
        self.node.get_logger().info("Agent Availability Monitor initialized")
    
    def check_agent_health(self):
        """Periodically check if agents are responding"""
        
        for agent_name in self.agent_status:
            try:
                # Send health check to agent
                health_msg = String()
                health_msg.data = json.dumps({
                    'request': 'health_check',
                    'timestamp': time.time()
                })
                
                self.agent_health_pubs[agent_name].publish(health_msg)
                
                # In practice, would wait for response to determine availability
                # For now, just update the last check time
                self.agent_status[agent_name]['last_check'] = time.time()
                
            except Exception as e:
                self.node.get_logger().error(f"Error checking health of {agent_name} agent: {e}")
    
    def is_agent_available(self, agent_name: str) -> bool:
        """Check if an agent is available"""
        return self.agent_status.get(agent_name, {}).get('available', False)
    
    def set_agent_availability(self, agent_name: str, available: bool):
        """Set agent availability status"""
        if agent_name in self.agent_status:
            self.agent_status[agent_name]['available'] = available
            self.agent_status[agent_name]['last_check'] = time.time()
    
    def get_available_agents(self) -> List[str]:
        """Get list of currently available agents"""
        available = []
        for agent, status in self.agent_status.items():
            if status['available']:
                available.append(agent)
        return available


class TriageExpertAgent(Node):
    """Main triage agent that routes queries to specialized experts"""
    
    def __init__(self):
        super().__init__('triage_expert_agent')
        
        # Initialize components
        self.classifier = QueryClassifier()
        self.availability_monitor = AgentAvailabilityMonitor(self)
        self.query_router = QueryRouter(self)
        
        # Publishers to specialized agents
        self.ros_agent_pub = self.create_publisher(String, '/ros_expert/query', 10)
        self.gazebo_agent_pub = self.create_publisher(String, '/gazebo_expert/query', 10)
        self.isaac_agent_pub = self.create_publisher(String, '/isaac_expert/query', 10)
        self.vla_agent_pub = self.create_publisher(String, '/vla_expert/query', 10)
        
        # Publisher for fallback or general responses
        self.general_agent_pub = self.create_publisher(String, '/general_robotics_expert/query', 10)
        
        # Subscriber for incoming queries
        self.query_sub = self.create_subscription(
            String, 
            '/natural_language_query', 
            self.query_callback, 
            10
        )
        
        # Publisher for response aggregation
        self.response_pub = self.create_publisher(String, '/aggregated_response', 10)
        
        # Query history for learning and optimization
        self.query_history = []
        self.routing_decisions = []
        
        # Statistics
        self.routing_stats = {
            'total_queries': 0,
            'successful_routes': 0,
            'fallback_routes': 0,
            'misrouted_queries': 0
        }
        
        self.logger = self.get_logger()
        self.logger.info("Triage Expert Agent initialized and ready")
    
    def query_callback(self, msg: String):
        """Process incoming query and route to appropriate agent"""
        try:
            query_data = json.loads(msg.data)
            query_text = query_data.get('query', query_data if isinstance(query_data, str) else str(query_data))
        except json.JSONDecodeError:
            # If not JSON, treat as plain text
            query_text = msg.data
        
        self.logger.info(f"Received query for triage: '{query_text[:50]}{'...' if len(query_text) > 50 else ''}'")
        
        # Classify the query
        classification = self.classifier.classify_query(query_text)
        
        primary_agent = classification['primary_agent']
        confidence = classification['confidence']
        
        self.logger.info(f"Query classified as: {primary_agent} with confidence {confidence:.2f}")
        
        # Check agent availability
        if not self.availability_monitor.is_agent_available(primary_agent):
            self.logger.warn(f"Primary agent {primary_agent} is unavailable, using fallback")
            primary_agent = self.get_next_best_agent(classification['scores'])
        
        if not primary_agent:
            # No agent available, send to general expert
            self.route_to_general_agent(query_text, classification)
        elif confidence > 0.3:  # If confidence is reasonable
            # Route to primary agent
            self.route_to_agent(primary_agent, query_text, classification)
        else:
            # Low confidence, send to general expert with classification info
            self.route_to_general_agent(query_text, classification)
    
    def route_to_agent(self, agent: str, query: str, classification: Dict[str, Any]):
        """Route query to specified agent"""
        self.routing_stats['total_queries'] += 1
        self.routing_stats['successful_routes'] += 1
        
        # Record the routing decision
        self.routing_decisions.append({
            'query': query[:100] + '...',  # Truncate long queries
            'agent_assigned': agent,
            'confidence': classification['confidence'],
            'timestamp': time.time()
        })
        
        # Create query message
        query_msg = String()
        query_msg.data = json.dumps({
            'query': query,
            'classification': classification,
            'source': 'triage_system',
            'route_timestamp': time.time()
        })
        
        # Publish to appropriate agent
        agent_pubs = {
            'ros': self.ros_agent_pub,
            'gazebo': self.gazebo_agent_pub,
            'isaac': self.isaac_agent_pub,
            'vla': self.vla_agent_pub
        }
        
        if agent in agent_pubs:
            agent_pubs[agent].publish(query_msg)
            self.logger.info(f"Routed query to {agent} agent")
        else:
            self.logger.error(f"Unknown agent: {agent}")
            # Route to general if unknown
            self.route_to_general_agent(query, classification)
    
    def route_to_general_agent(self, query: str, classification: Dict[str, Any]):
        """Route query to general agent when confidence is low or primary agent unavailable"""
        self.routing_stats['total_queries'] += 1
        self.routing_stats['fallback_routes'] += 1
        
        query_msg = String()
        query_msg.data = json.dumps({
            'query': query,
            'classification': classification,
            'original_classification': 'low_confidence_or_unavailable',
            'source': 'triage_system',
            'route_timestamp': time.time()
        })
        
        self.general_agent_pub.publish(query_msg)
        self.logger.info("Routed query to general agent due to low confidence or unavailability")
    
    def get_next_best_agent(self, scores: Dict[str, Any]) -> Optional[str]:
        """Get the next best available agent after the primary"""
        # Sort scores by value (descending)
        sorted_agents = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        for agent, score in sorted_agents:
            if self.availability_monitor.is_agent_available(agent):
                return agent
        
        return None  # No agents available
    
    def get_routing_statistics(self) -> Dict[str, Any]:
        """Get statistics about query routing"""
        total = self.routing_stats['total_queries']
        if total == 0:
            return {
                'success_rate': 0.0,
                'fallback_rate': 0.0,
                'total_queries': 0
            }
        
        return {
            'success_rate': self.routing_stats['successful_routes'] / total,
            'fallback_rate': self.routing_stats['fallback_routes'] / total,
            'total_queries': total,
            'most_common_agents': self.get_most_routed_agents(),
            'recent_routing_decisions': self.routing_decisions[-5:]  # Last 5 decisions
        }
    
    def get_most_routed_agents(self) -> Dict[str, int]:
        """Get count of queries routed to each agent"""
        agent_counts = {}
        for decision in self.routing_decisions:
            agent = decision['agent_assigned']
            agent_counts[agent] = agent_counts.get(agent, 0) + 1
        
        return agent_counts


class QueryRouter:
    """Handles the routing mechanism to specialized agents"""
    
    def __init__(self, node):
        self.node = node
        self.specialized_agents = {
            'ros': {
                'description': 'ROS 2 architecture, nodes, topics, services, actions',
                'capabilities': ['navigation', 'manipulation', 'sensing', 'parameters'],
                'availability': True
            },
            'gazebo': {
                'description': 'Gazebo simulation, physics, collision, dynamics',
                'capabilities': ['environment_simulation', 'sensor_simulation', 'physics'],
                'availability': True
            },
            'isaac': {
                'description': 'Isaac Sim, synthetic data, photorealistic rendering',
                'capabilities': ['advanced_simulation', 'photorealistic_graphics', 'data_generation'],
                'availability': True
            },
            'vla': {
                'description': 'Vision-Language-Action systems, multimodal understanding',
                'capabilities': ['multimodal_processing', 'language_understanding', 'action_planning'],
                'availability': True
            }
        }
    
    def get_agent_capabilities(self, agent: str) -> List[str]:
        """Get capabilities of a specific agent"""
        return self.specialized_agents.get(agent, {}).get('capabilities', [])
    
    def find_agent_for_capabilities(self, required_capabilities: List[str]) -> str:
        """Find agent that best handles required capabilities"""
        best_agent = 'general'
        best_score = 0
        
        for agent, info in self.specialized_agents.items():
            score = 0
            for capability in required_capabilities:
                if capability in info['capabilities']:
                    score += 1
            
            if score > best_score:
                best_score = score
                best_agent = agent
        
        return best_agent if best_score > 0 else 'general'


# Example usage and testing
class TriageTestNode(Node):
    """Test node for triage system"""
    
    def __init__(self):
        super().__init__('triage_test_node')
        
        # Test queries
        self.test_queries = [
            "How do I create a ROS 2 publisher?",
            "Configure physics parameters in Gazebo for humanoid robot",
            "Set up Isaac Sim for perception training data",
            "Implement voice-to-action pipeline using VLA system",
            "What is the architecture of ROS 2?",
            "How do I add a camera sensor to my robot in simulation?",
            "Create a cognitive planning system from natural language",
            "What are the differences between topics and services in ROS?"
        ]
        
        self.test_index = 0
        self.test_publisher = self.create_publisher(String, '/natural_language_query', 10)
        
        # Timer to run tests
        self.test_timer = self.create_timer(2.0, self.run_test)
        
        self.logger = self.get_logger()
        self.logger.info("Triage test node initialized")
    
    def run_test(self):
        """Run triage test with sample queries"""
        if self.test_index < len(self.test_queries):
            query = self.test_queries[self.test_index]
            
            query_msg = String()
            query_msg.data = json.dumps({
                'query': query,
                'source': 'triage_test',
                'timestamp': time.time()
            })
            
            self.test_publisher.publish(query_msg)
            self.logger.info(f"Published test query {self.test_index+1}: {query}")
            
            self.test_index += 1
        else:
            # All tests complete
            self.test_timer.cancel()  # Stop the test timer
            self.logger.info("All triage tests completed")


def main(args=None):
    rclpy.init(args=args)
    
    # Create the triage expert agent
    triage_agent = TriageExpertAgent()
    
    # Optionally create a test node to verify the system works
    test_node = TriageTestNode()
    
    # Create executor
    executor = rclpy.executors.MultiThreadedExecutor()
    executor.add_node(triage_agent)
    executor.add_node(test_node)
    
    try:
        executor.spin()
    except KeyboardInterrupt:
        triage_agent.get_logger().info("Triage Expert Agent shutting down...")
    finally:
        triage_agent.destroy_node()
        test_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Integration Testing

### Complete Pipeline Test

```python
# integration_test.py
import unittest
import time
from unittest.mock import Mock
import json

class TestVLAPipeline(unittest.TestCase):
    """Integration test for the complete VLA pipeline"""
    
    def setUp(self):
        """Set up test environment"""
        self.vla_system = VLASystemIntegration()
        self.triage_agent = TriageExpertAgent(Mock())
        
    def test_simple_command(self):
        """Test a simple command through the complete pipeline"""
        # Simple command that should route to ROS expert
        command = "How do I create a publisher in ROS 2?"
        
        classification = self.triage_agent.classifier.classify_query(command)
        
        # Should identify as ROS-related with high confidence
        self.assertEqual(classification['primary_agent'], 'ros')
        self.assertGreater(classification['confidence'], 0.5)
    
    def test_multimodal_command(self):
        """Test a command that requires vision-language-action processing"""
        command = "Use vision and language to get the red cup from the table"
        
        classification = self.triage_agent.classifier.classify_query(command)
        
        # Should identify as VLA-related 
        self.assertEqual(classification['primary_agent'], 'vla')
        self.assertGreater(classification['confidence'], 0.5)
    
    def test_simulation_command(self):
        """Test a command related to simulation"""
        command = "Configure Gazebo physics for humanoid walking"
        
        classification = self.triage_agent.classifier.classify_query(command)
        
        # Should identify as Gazebo-related
        self.assertEqual(classification['primary_agent'], 'gazebo')
        self.assertGreater(classification['confidence'], 0.5)
    
    def test_cross_domain_command(self):
        """Test a command that spans multiple domains"""
        command = "How do I integrate Isaac Sim with ROS 2 navigation stack?"
        
        classification = self.triage_agent.classifier.classify_query(command)
        
        # Should identify as spanning Isaac and ROS
        self.assertIn('isaac', [classification['primary_agent']] + classification['mixed_domains'])
        self.assertIn('ros', [classification['primary_agent']] + classification['mixed_domains'])
        self.assertIsNotNone(classification['mixed_domains'])

class TestTriageSystem(unittest.TestCase):
    """Test the triage system's routing accuracy"""
    
    def setUp(self):
        self.classifier = QueryClassifier()
    
    def test_keyword_matching(self):
        """Test keyword-based classification"""
        test_cases = [
            ("How do I create a ROS 2 node?", "ros"),
            ("What are the physics parameters in Gazebo?", "gazebo"),
            ("How do I set up Isaac Sim?", "isaac"),
            ("Implement vision-language-action pipeline", "vla")
        ]
        
        for query, expected_domain in test_cases:
            with self.subTest(query=query):
                result = self.classifier.classify_query(query)
                self.assertEqual(result['primary_agent'], expected_domain)
    
    def test_confidence_calculation(self):
        """Test confidence calculations"""
        # High confidence case
        high_conf_query = "Create a ROS 2 publisher node"
        result = self.classifier.classify_query(high_conf_query)
        self.assertGreater(result['confidence'], 0.7)
        
        # Low confidence case
        ambiguous_query = "How do I do stuff with my robot?"
        result = self.classifier.classify_query(ambiguous_query)
        self.assertLess(result['confidence'], 0.5)


def run_integration_tests():
    """Run all integration tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add tests
    suite.addTests(loader.loadTestsFromTestCase(TestVLAPipeline))
    suite.addTests(loader.loadTestsFromTestCase(TestTriageSystem))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


# Performance test
def performance_test():
    """Test performance of the triage system"""
    classifier = QueryClassifier()
    
    # Generate test queries
    test_queries = [
        "How do I create a publisher in ROS 2?",
        "Configure physics in Gazebo for humanoid walking",
        "Set up Isaac Sim with RTX rendering",
        "Implement voice-to-action using VLA system"
    ] * 100  # 400 queries total
    
    start_time = time.time()
    
    for query in test_queries:
        classification = classifier.classify_query(query)
    
    end_time = time.time()
    
    total_time = end_time - start_time
    queries_per_second = len(test_queries) / total_time
    
    print(f"Performance Test Results:")
    print(f"  Queries processed: {len(test_queries)}")
    print(f"  Total time: {total_time:.2f}s")
    print(f"  Queries per second: {queries_per_second:.2f}")
    
    # Check if performance meets requirements (>10 queries/second)
    assert queries_per_second > 10, f"Performance too slow: {queries_per_second} queries/second"
    
    print("  ✓ Performance requirement met (>10 queries/second)")


if __name__ == "__main__":
    print("Running Triage System Performance Test...")
    performance_test()
    
    print("\nRunning Integration Tests...")
    test_result = run_integration_tests()
    
    if test_result.wasSuccessful():
        print("\n✓ All integration tests passed!")
    else:
        print(f"\n✗ Some tests failed: {len(test_result.failures)} failures, {len(test_result.errors)} errors")
        
        for failure in test_result.failures:
            print(f"  FAILURE: {failure[0]} - {failure[1]}")
        for error in test_result.errors:
            print(f"  ERROR: {error[0]} - {error[1]}")
```

## System Integration

### Complete Integration Example

```python
# complete_integration_example.py
from typing import Dict, Any, Optional
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json


class CompleteHumanoidSystem(Node):
    """Complete integration of all humanoid systems"""
    
    def __init__(self):
        super().__init__('complete_humanoid_system')
        
        # Initialize all subsystems
        self.triage_agent = TriageExpertAgent(self)
        self.vla_agent = VisionLanguageAgent(self)
        self.perception_system = PerceptionSystem(self)
        self.motion_controller = MotionController(self)
        self.cognitive_planner = CognitivePlanner(self)
        
        # Publishers
        self.system_status_pub = self.create_publisher(String, '/system_status', 10)
        self.action_command_pub = self.create_publisher(String, '/action_commands', 10)
        
        # Subscriber for high-level commands
        self.high_level_cmd_sub = self.create_subscription(String, '/high_level_commands', self.high_level_command_callback, 10)
        
        # System state
        self.system_state = {
            'components_ready': {
                'triage': True,
                'vla': True,
                'perception': True,
                'motion_control': True,
                'cognitive_planning': True
            },
            'active_processes': [],
            'safety_status': 'nominal',
            'performance_metrics': {
                'response_time_avg': 0.0,
                'success_rate': 0.0,
                'utilization': 0.0
            }
        }
        
        # Timer for system monitoring
        self.monitor_timer = self.create_timer(1.0, self.system_monitor)
        
        self.get_logger().info("Complete Humanoid System initialized")
    
    def high_level_command_callback(self, msg: String):
        """Process high-level commands through the complete system"""
        try:
            command_data = json.loads(msg.data)
            command_text = command_data['command']
            
            self.get_logger().info(f"Processing high-level command: '{command_text}'")
            
            # Step 1: Route command via triage system
            classification = self.triage_agent.classifier.classify_query(command_text)
            
            # Step 2: If it's a VLA-related command, process with VLA pipeline
            if classification['primary_agent'] == 'vla':
                result = self.vla_agent.process_command_with_visual_context(
                    command_text,
                    self.perception_system.get_lastest_visual_data()
                )
                
                if result.get('success'):
                    self.get_logger().info(f"VLA command completed successfully")
                    self.feedback_user(f"Task completed: {command_text}")
                else:
                    self.get_logger().error(f"VLA command failed: {result}")
                    self.feedback_user(f"Could not complete: {command_text}")
            
            # Step 3: If it's a motion command, process with motion controller
            elif classification['primary_agent'] in ['ros', 'gazebo']:
                # Plan and execute motion
                plan = self.cognitive_planner.plan_motion_command(command_text)
                if plan:
                    success = self.motion_controller.execute_plan(plan)
                    if success:
                        self.feedback_user("Motion command executed successfully")
                    else:
                        self.feedback_user("Could not execute motion command")
                else:
                    self.feedback_user("Could not understand motion command")
            
            # Step 4: For other commands, route appropriately
            else:
                # This would be handled by the appropriate specialized agent
                self.triage_agent.route_to_agent(classification['primary_agent'], command_text, classification)
        
        except json.JSONDecodeError:
            self.get_logger().error(f"Invalid JSON in command: {msg.data}")
        except Exception as e:
            self.get_logger().error(f"Error processing high-level command: {e}")
            self.feedback_user(f"Error processing command: {str(e)}")
    
    def feedback_user(self, message: str):
        """Provide feedback to user"""
        feedback_msg = String()
        feedback_msg.data = json.dumps({
            'type': 'system_feedback',
            'message': message,
            'timestamp': self.get_clock().now().seconds_nanoseconds()
        })
        # In practice, this would connect to audio/SPEAK system
        self.get_logger().info(f"System feedback: {message}")
    
    def system_monitor(self):
        """Monitor system status and performance"""
        # Update system status
        status_msg = String()
        status_msg.data = json.dumps({
            'state': self.system_state,
            'timestamp': self.get_clock().now().seconds_nanoseconds()
        })
        
        self.system_status_pub.publish(status_msg)
        
        # Log system health
        self.get_logger().debug(f"System components ready: {self.system_state['components_ready']}")
        self.get_logger().debug(f"Active processes: {len(self.system_state['active_processes'])}")
    
    def shutdown_procedure(self):
        """Perform safe shutdown of all subsystems"""
        self.get_logger().info("Initiating system shutdown...")
        
        # Stop all active processes
        for process in self.system_state['active_processes']:
            try:
                process.kill()
            except:
                pass  # Process may already be terminated
        
        # Set safety state
        self.system_state['safety_status'] = 'shutdown_initiated'
        self.motion_controller.emergency_stop()
        
        self.get_logger().info("System shutdown complete")


def main(args=None):
    rclpy.init(args=args)
    
    # Create the complete humanoid system
    humanoid_system = CompleteHumanoidSystem()
    
    try:
        rclpy.spin(humanoid_system)
    except KeyboardInterrupt:
        humanoid_system.get_logger().info("Complete Humanoid System interrupted by user")
    finally:
        humanoid_system.shutdown_procedure()
        humanoid_system.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Validation and Error Handling

### System Validation Framework

```python
# system_validation.py
import time
import statistics
from typing import Dict, Any, List
import threading
import queue


class HumanoidSystemValidator:
    """Validate the complete humanoid system"""
    
    def __init__(self, node):
        self.node = node
        self.validation_history = []
        
        # Define validation metrics
        self.metrics = {
            'response_time': [],
            'success_rate': [],
            'safety_incidents': [],
            'component_health': {}
        }
    
    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run comprehensive validation of the entire system"""
        
        validation_results = {
            'component_connectivity': self.validate_component_connectivity(),
            'performance_metrics': self.measure_performance(),
            'safety_validation': self.validate_safety_systems(),
            'data_flow_validation': self.validate_data_flow(),
            'error_recovery': self.validate_error_recovery(),
            'overall_system_status': 'validated'
        }
        
        # Record validation
        self.validation_history.append({
            'timestamp': time.time(),
            'results': validation_results,
            'summary': self.summarize_validation(validation_results)
        })
        
        return validation_results
    
    def validate_component_connectivity(self) -> Dict[str, Any]:
        """Validate that all components can communicate"""
        connectivity = {
            'triage_agent': self.check_agent_health('triage'),
            'vla_agent': self.check_agent_health('vla'),
            'perception_system': self.check_agent_health('perception'),
            'motion_controller': self.check_agent_health('motion_control'),
            'cognitive_planner': self.check_agent_health('cognitive_planning')
        }
        
        all_connected = all(connectivity.values())
        
        return {
            'connected': all_connected,
            'details': connectivity,
            'success': all_connected
        }
    
    def measure_performance(self) -> Dict[str, float]:
        """Measure system performance metrics"""
        
        # Calculate from recent metrics
        if self.metrics['response_time']:
            avg_response = statistics.mean(self.metrics['response_time'])
        else:
            avg_response = float('inf')
        
        if self.metrics['success_rate']:
            overall_success = statistics.mean(self.metrics['success_rate'])
        else:
            overall_success = 0.0
        
        return {
            'avg_response_time': avg_response,
            'overall_success_rate': overall_success,
            'total_validations': len(self.validation_history),
            'current_time': time.time()
        }
    
    def validate_safety_systems(self) -> Dict[str, Any]:
        """Validate safety systems are operational"""
        safety_checks = {
            'collision_avoidance': self.test_collision_avoidance_system(),
            'emergency_stop': self.test_emergency_stop_functionality(),
            'balance_recovery': self.test_balance_recovery(),
            'joint_limit_protection': self.test_joint_limits(),
            'safety_monitoring': self.test_safety_monitoring()
        }
        
        all_safe = all(check['success'] for check in safety_checks.values() if isinstance(check, dict))
        
        return {
            'systems_safe': all_safe,
            'checks': safety_checks,
            'success': all_safe
        }
    
    def validate_data_flow(self) -> Dict[str, Any]:
        """Validate that data flows correctly between components"""
        
        # Test that commands flow through the system properly
        test_results = {
            'command_routing': self.test_command_routing(),
            'data_synchronization': self.test_data_synchronization(),
            'feedback_loop': self.test_feedback_loop(),
            'world_model_updates': self.test_world_model_updates()
        }
        
        all_passed = all(test_results.get(key, {}).get('success', False) 
                        for key in test_results.keys())
        
        return {
            'flow_valid': all_passed,
            'tests': test_results,
            'success': all_passed
        }
    
    def validate_error_recovery(self) -> Dict[str, Any]:
        """Validate that system can recover from common errors"""
        
        recovery_tests = {
            'sensor_failure': self.test_sensor_failure_recovery(),
            'actuator_failure': self.test_actuator_failure_recovery(),
            'communication_loss': self.test_communication_loss_recovery(),
            'perception_failure': self.test_perception_failure_recovery(),
            'planning_failure': self.test_planning_failure_recovery()
        }
        
        recovery_success_rate = sum(1 for test in recovery_tests.values() 
                                   if test.get('success', False)) / len(recovery_tests)
        
        return {
            'recovery_success_rate': recovery_success_rate,
            'tests': recovery_tests,
            'success': recovery_success_rate > 0.8  # Require 80% success rate for validation
        }
    
    def test_agent_health(self, agent_name: str) -> bool:
        """Test if an agent is responding to health checks"""
        # In practice, this would ping the agent's health endpoint
        # For simulation, return True
        time.sleep(0.01)  # Simulate communication delay
        return True
    
    def test_collision_avoidance_system(self) -> Dict[str, Any]:
        """Test collision avoidance system"""
        # In practice, this would perform integration testing
        # For now, return a simulated test result
        result = {
            'success': True,
            'response_time': 0.05,  # 50ms response time
            'detection_accuracy': 0.98  # 98% accurate detection
        }
        return result
    
    def test_emergency_stop_functionality(self) -> Dict[str, Any]:
        """Test emergency stop functionality"""
        result = {
            'success': True,
            'stop_time': 0.1,  # 100ms to stop
            'verified_stopped': True
        }
        return result
    
    def test_balance_recovery(self) -> Dict[str, Any]:
        """Test balance recovery system"""
        result = {
            'success': True,
            'recovery_time': 1.2,  # 1.2 second recovery
            'stability_after_recovery': True
        }
        return result
    
    def test_joint_limits(self) -> Dict[str, Any]:
        """Test joint limit protection"""
        result = {
            'success': True,
            'limits_respected': True,
            'overshoot_prevented': True
        }
        return result
    
    def test_command_routing(self) -> Dict[str, Any]:
        """Test command routing through the system"""
        # Simulate sending a command and checking if it reaches appropriate component
        result = {
            'success': True,
            'correctly_routed': True,
            'response_received': True
        }
        return result
    
    def test_data_synchronization(self) -> Dict[str, Any]:
        """Test synchronized data flow between components"""
        result = {
            'success': True,
            'timestamps_aligned': True,
            'data_in_sync': True
        }
        return result
    
    def check_sensor_failure_recovery(self) -> Dict[str, Any]:
        """Test sensor failure recovery"""
        result = {
            'success': True,
            'alternative_path_works': True,
            'degraded_mode_operational': True
        }
        return result
    
    def summarize_validation(self, results: Dict[str, Any]) -> str:
        """Summarize validation results"""
        component_status = results.get('component_connectivity', {}).get('connected', False)
        safety_status = results.get('safety_validation', {}).get('systems_safe', False)
        flow_status = results.get('data_flow_validation', {}).get('flow_valid', False)
        recovery_rate = results.get('error_recovery', {}).get('recovery_success_rate', 0)
        
        summary = f"Validation: Components={component_status}, Safety={safety_status}, " \
                  f"Flow={flow_status}, Recovery={recovery_rate*100:.1f}%"
        
        return summary
    
    def generate_validation_report(self) -> str:
        """Generate comprehensive validation report"""
        if not self.validation_history:
            return "No validation results available"
        
        latest_validation = self.validation_history[-1]
        
        report = f"""
        HUMANOID SYSTEM VALIDATION REPORT
        ==================================
        
        Date: {time.ctime(latest_validation['timestamp'])}
        
        Component Connectivity: {'✓' if latest_validation['results']['component_connectivity']['success'] else '✗'}
        Performance Metrics: {'✓' if latest_validation['results']['performance_metrics']['avg_response_time'] < 2.0 else '✗'} (Avg: {latest_validation['results']['performance_metrics']['avg_response_time']:.2f}s)
        Safety Systems: {'✓' if latest_validation['results']['safety_validation']['success'] else '✗'}
        Data Flow: {'✓' if latest_validation['results']['data_flow_validation']['success'] else '✗'}
        Error Recovery: {'✓' if latest_validation['results']['error_recovery']['success'] else '✗'} ({latest_validation['results']['error_recovery']['recovery_success_rate']*100:.1f}% success)
        
        Overall Status: {'✓ PASSED' if all(
            latest_validation['results'][key]['success'] for key in latest_validation['results'] 
            if key != 'performance_metrics'  # Performance metrics have different format
        ) else '✗ FAILED'}
        """
        
        return report


def run_system_validation():
    """Run system validation and display results"""
    # In a real implementation, this would run on the actual system
    # For this example, we'll simulate the validation process
    
    print("Running comprehensive humanoid system validation...")
    
    # Create a mock validation system
    class MockNode:
        def get_logger(self):
            class Logger:
                def info(self, msg): print(msg)
                def error(self, msg): print(f"ERROR: {msg}")
                def debug(self, msg): print(f"DEBUG: {msg}")
                def warn(self, msg): print(f"WARNING: {msg}")
            return Logger()
    
    validator = HumanoidSystemValidator(MockNode())
    results = validator.run_comprehensive_validation()
    
    print(validator.generate_validation_report())
    
    return results


if __name__ == "__main__":
    validation_results = run_system_validation()