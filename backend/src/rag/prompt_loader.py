from pathlib import Path

# Calculate the project root by going up from the current file location
CURRENT_FILE_PATH = Path(__file__).resolve()  # Get absolute path of this file
# From Physical-AI-Humanoid-Robotics-Phase-I/backend/src/rag/prompt_loader.py going up 4 levels gets us to project root
# File path: Physical-AI-Humanoid-Robotics-Phase-I/backend/src/rag/prompt_loader.py
# To get to project root: go up 4 levels (rag -> src -> backend -> project_root)
PROJECT_ROOT = CURRENT_FILE_PATH.parent.parent.parent.parent
BASE_PROMPT_DIR = PROJECT_ROOT / "specs" / "1-book-rag-chatbot" / "prompts"


def load_prompt(agent_name: str, user_level: str) -> str:
    """
    Load prompt text based on agent name and user level (v0 / v1)
    """

    if user_level not in {"v0", "v1"}:
        raise ValueError("user_level must be 'v0' or 'v1'")

    prompt_path = BASE_PROMPT_DIR / user_level / f"{agent_name}.md"

    if not prompt_path.exists():
        # Show debug information to help diagnose the issue
        print(f"Looking for prompt at: {prompt_path.absolute()}")
        print(f"Project root: {PROJECT_ROOT}")
        print(f"Prompt base: {BASE_PROMPT_DIR}")
        print(f"Prompt file exists: {prompt_path.exists()}")
        print(f"Prompt base exists: {BASE_PROMPT_DIR.exists()}")

        if BASE_PROMPT_DIR.exists():
            for ver in ["v0", "v1"]:
                ver_path = BASE_PROMPT_DIR / ver
                if ver_path.exists():
                    print(f"Files in {ver}: {list(ver_path.iterdir())}")

        raise FileNotFoundError(f"Prompt not found: {prompt_path}")

    return prompt_path.read_text(encoding="utf-8")
