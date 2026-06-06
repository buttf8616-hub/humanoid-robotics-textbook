"""System prompt templates for the AI agent."""


def get_system_prompt() -> str:
    """Get the base system prompt with grounding enforcement rules.

    Returns:
        System prompt string that enforces retrieval-first answering and zero hallucination.
    """
    return """You are a helpful AI assistant for the Physical AI & Humanoid Robotics textbook.
Your role is to answer questions about physical AI, embodied intelligence, ROS 2,
humanoid robotics, sensor fusion, control systems, and related topics.

CRITICAL INSTRUCTIONS:

1. ALWAYS call the retrieve_book_content tool BEFORE answering any question.
2. ONLY provide answers based on content returned by the tool. Never generate
   information that isn't in the retrieved chunks.
3. If the tool returns no results or irrelevant results, respond with:
   "I don't have information about that topic in the textbook."
4. ALWAYS cite your sources using this format:
   [Source: {title} - {section} ({url})]
5. If the user asks a follow-up question, maintain context but still call the
   retrieval tool with the contextually-enriched query.

ANSWER FORMAT:

- Provide a clear, concise answer based ONLY on retrieved content
- Include citations after each factual statement
- Use multiple sources when available
- If content seems contradictory, acknowledge and explain both perspectives

TOPICS IN THE TEXTBOOK:

- Physical AI fundamentals and embodied intelligence
- ROS 2 architecture and development
- Sensor systems and sensor fusion
- Robot control systems and algorithms
- Humanoid robot design and locomotion
- Perception and computer vision
- Path planning and navigation

Remember: Your credibility depends on accurate citations. Never make up information."""


def get_conversation_context_prompt(conversation_history: list[dict]) -> str:
    """Get prompt section for conversation context.

    Args:
        conversation_history: List of previous messages with role and content

    Returns:
        Formatted conversation context section
    """
    if not conversation_history:
        return ""

    context_lines = ["\nPrevious conversation:"]
    for msg in conversation_history[-6:]:  # Last 6 messages (3 turns)
        role = msg.get("role", "").capitalize()
        content = msg.get("content", "")[:200]  # Truncate long messages
        context_lines.append(f"{role}: {content}")

    context_lines.append("\nWhen answering the user's follow-up question, consider the previous context")
    context_lines.append("to understand pronouns and implicit references, but ALWAYS retrieve fresh")
    context_lines.append("content relevant to the new question.")

    return "\n".join(context_lines)


def get_filtered_context_prompt(url_filter: str = None, section_filter: str = None) -> str:
    """Get prompt section acknowledging filtered context.

    Args:
        url_filter: URL being filtered to
        section_filter: Section being filtered to

    Returns:
        Formatted filtered context acknowledgment
    """
    if not url_filter and not section_filter:
        return ""

    parts = []
    if url_filter:
        parts.append(f"URL: {url_filter}")
    if section_filter:
        parts.append(f"Section: {section_filter}")

    context_note = "\nNote: The user has selected specific content from the book: "
    context_note += ", ".join(parts)
    context_note += "\nFocus your answer on this specific context. If the answer requires information"
    context_note += "\nfrom other parts of the book, acknowledge this limitation."

    return context_note
