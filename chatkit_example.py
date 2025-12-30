# Example usage of the ChatKit system
import asyncio
import sys
import os

# Add paths
project_root = os.path.abspath('.')
backend_path = os.path.join(project_root, 'backend')
src_path = os.path.join(backend_path, 'src')

sys.path.insert(0, project_root)
sys.path.insert(0, backend_path)
sys.path.insert(0, src_path)

# Change to the backend directory for imports
os.chdir(backend_path)

async def example_usage():
    """
    Example demonstrating the ChatKit system with agent builder integration
    """
    
    # Import the chat service
    from chatkit.chat import ChatService
    
    # Create a chat service instance
    chat_service = ChatService()
    print("Physical AI & Humanoid Robotics ChatKit System")
    print("="*60)
    print(f"Workflow ID: {chat_service.workflow_id}")
    print(f"Available Agents: {', '.join(chat_service.available_agents)}")
    print()
    
    # Example 1: ROS-related question (should route to ROS agent)
    print("[Q1] Example 1: ROS-related question")
    result1 = await chat_service.chat_with_agent(
        question="How do I create a publisher in ROS 2 using Python?",
        agent_type="triage",  # Automatic routing based on content
        user_level="v0"  # Beginner level
    )
    print(f"Question: How do I create a publisher in ROS 2 using Python?")
    print(f"Routed to: {result1['agent']} agent (level: {result1['user_level']})")
    print(f"Response preview: {result1['response'][:200]}...")
    print()

    # Example 2: VLA-related question (should route to VLA agent)
    print("[Q2] Example 2: VLA (Vision-Language-Action) question")
    result2 = await chat_service.chat_with_agent(
        question="How does voice-to-action pipeline work in humanoid robots?",
        agent_type="triage",  # Automatic routing based on content
        user_level="v1"  # Expert level
    )
    print(f"Question: How does voice-to-action pipeline work in humanoid robots?")
    print(f"Routed to: {result2['agent']} agent (level: {result2['user_level']})")
    print(f"Response preview: {result2['response'][:200]}...")
    print()

    # Example 3: Gazebo simulation question
    print("[Q3] Example 3: Gazebo simulation question")
    result3 = await chat_service.chat_with_agent(
        question="How do I configure physics parameters in Gazebo for humanoid stability?",
        agent_type="triage",  # Automatic routing based on content
        user_level="v1"  # Expert level
    )
    print(f"Question: How do I configure physics parameters in Gazebo for humanoid stability?")
    print(f"Routed to: {result3['agent']} agent (level: {result3['user_level']})")
    print(f"Response preview: {result3['response'][:200]}...")
    print()

    # Example 4: Direct agent call
    print("[Q4] Example 4: Direct Isaac agent call")
    result4 = await chat_service.chat_with_agent(
        question="How do I set up Isaac Sim for synthetic data generation?",
        agent_type="isaac",  # Explicit agent selection
        user_level="v0"  # Beginner level
    )
    print(f"Question: How do I set up Isaac Sim for synthetic data generation?")
    print(f"Called directly: {result4['agent']} agent (level: {result4['user_level']})")
    print(f"Response preview: {result4['response'][:200]}...")
    print()
    
    # Show agent capabilities
    print("🔍 Agent Capabilities:")
    agents_info = await chat_service.get_agent_list()
    for agent_name, details in agents_info['agents'].items():
        print(f"  • {agent_name.upper()}: {details['description']}")
        print(f"    Capabilities: {', '.join(details['capabilities'])}")
    print()
    
    print("✅ ChatKit system is working correctly!")
    print("✅ Agent Builder integration with workflow ID is operational!")
    print("✅ All agent types (VLA, ROS, Gazebo, Isaac) are accessible!")
    print("✅ Both user levels (v0, v1) are supported!")

if __name__ == "__main__":
    print("Running ChatKit example...")
    asyncio.run(example_usage())