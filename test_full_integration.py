import sys
import os

# Add paths
project_root = os.path.abspath('.')
backend_path = os.path.join(project_root, 'backend')
src_path = os.path.join(backend_path, 'src')

sys.path.insert(0, project_root)
sys.path.insert(0, backend_path)
sys.path.insert(0, src_path)

print(f"[SUCCESS] Added to path: {project_root}, {backend_path}, {src_path}")

# Change to the backend directory for imports
os.chdir(backend_path)

try:
    # Test the import in the same way as the chat service would
    from src.rag.agent_adapter import run_agent
    print("[SUCCESS] Successfully imported run_agent from src.rag.agent_adapter")
    
    # Now test creating the ChatService
    print("\n[TEST] Creating ChatService instance...")
    
    # Add the chatkit path to import ChatService
    chatkit_path = os.path.join(project_root, 'chatkit')
    sys.path.insert(0, chatkit_path)
    
    from chat import ChatService
    print("[SUCCESS] Successfully imported ChatService from chatkit")
    
    # Create an instance
    chat_service = ChatService()
    print(f"[SUCCESS] ChatService created with workflow ID: {chat_service.workflow_id}")
    
    # Test that the _get_agent_adapter method works
    adapter_func = chat_service._get_agent_adapter()
    print(f"[SUCCESS] Successfully loaded agent adapter: {adapter_func.__name__ if hasattr(adapter_func, '__name__') else 'function'}")
    
    print("\n[SUCCESS] Chatkit integration is working correctly!")
    print(f"[SUCCESS] Available agents: {chat_service.available_agents}")
    
except Exception as e:
    print(f"[ERROR] Error in full integration test: {e}")
    import traceback
    traceback.print_exc()