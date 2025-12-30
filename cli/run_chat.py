import asyncio
from chatkit.chat import ChatService


async def main():
    print("Physical AI & Humanoid Robotics Chat Interface")
    print("=" * 50)
    print("Available agents: vla, ros, gazebo, isaac")
    print("User levels: v0 (beginner), v1 (expert)")
    print("Type 'quit' to exit, 'agents' to see capabilities\n")

    chat_service = ChatService()

    while True:
        try:
            user_input = input("\nEnter your question: ").strip()

            if user_input.lower() in {"quit", "exit", "q"}:
                print("Goodbye!")
                break

            if user_input.lower() == "agents":
                agents_info = chat_service.get_agent_list()
                print("\nAvailable Agents:")
                for agent, details in agents_info["agents"].items():
                    print(f"  - {agent}: {details['description']}")
                    print(f"    Capabilities: {', '.join(details['capabilities'])}")
                continue

            if not user_input:
                print("Please enter a question.")
                continue

            user_level = "v0"
            if "v1" in user_input.lower() or "expert" in user_input.lower():
                user_level = "v1"

            print("\nThinking...\n")

            response = chat_service.chat_with_agent(
                question=user_input,
                agent_type="triage",
                user_level=user_level,
            )

            print(f"[{response['agent'].upper()} | {response['user_level'].upper()}]")
            print(response["response"])

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"CLI Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
