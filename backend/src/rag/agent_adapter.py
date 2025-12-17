from .prompt_loader import load_prompt


def run_agent(
    agent_runner,
    agent_name: str,
    question: str,
    user_level: str,
    ):
    """
    Execute an Agent Builder runner using the correct prompt version
    """

    system_prompt = load_prompt(
        agent_name=agent_name,
        user_level=user_level,
    )

    # Prepare the input for the agent runner
    # The agent runner expects a single input parameter (the question)
    # but we also need to incorporate the system prompt

    # In this implementation, we'll pass the prompt and question together
    full_input = f"{system_prompt}\n\nQuestion: {question}"

    result = agent_runner.run(input=full_input)

    return result.output_text