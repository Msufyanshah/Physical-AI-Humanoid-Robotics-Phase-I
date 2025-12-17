"""
Mock agent builder runners for the Physical AI & Humanoid Robotics system
This is a placeholder implementation that would be replaced by actual agents in a real system
"""

class MockRunner:
    """Mock runner to simulate agent builder functionality"""
    
    def __init__(self, name, description=""):
        self.name = name
        self.description = description
    
    def run(self, input):
        """Mock run method that returns a mock result"""
        # Create a mock result object with output_text attribute
        class MockResult:
            def __init__(self, text):
                self.output_text = text
        
        # If this is the triage runner, determine agent based on input
        if self.name == "triage":
            inp = input.get("input", "") if isinstance(input, dict) else input
            # Simple keyword-based triage for demonstration
            inp_lower = inp.lower()
            if any(word in inp_lower for word in ["ros", "node", "topic", "service", "action"]):
                return MockResult("ros")
            elif any(word in inp_lower for word in ["gazebo", "simulation", "physics", "world"]):
                return MockResult("gazebo")
            elif any(word in inp_lower for word in ["isaac", "ai", "learning", "perception"]):
                return MockResult("isaac")
            elif any(word in inp_lower for word in ["vision", "language", "action", "voice", "speech"]):
                return MockResult("vla")
            else:
                return MockResult("triage")  # default to triage if uncertain
        
        # For other agents, return a mock response based on the input
        inp = input.get("input", "") if isinstance(input, dict) else input
        return MockResult(f"Mock response from {self.name} agent for: {inp}")


# Create singleton instances for each agent
triage_runner = MockRunner("triage", "Triage agent to route queries to appropriate specialist")
ros_runner = MockRunner("ros", "ROS 2 expert agent")
gazebo_runner = MockRunner("gazebo", "Gazebo simulation expert agent")
isaac_runner = MockRunner("isaac", "Isaac Sim and AI expert agent")
vla_runner = MockRunner("vla", "Vision-Language-Action expert agent")

AGENT_RUNNERS = {
    "ros": ros_runner,
    "gazebo": gazebo_runner,
    "isaac": isaac_runner,
    "vla": vla_runner,
}
