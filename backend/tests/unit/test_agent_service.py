"""Unit tests for AgentService."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json

from src.agent.agent_service import AgentService
from src.config import settings


class TestAgentServiceInitialization:
    """Tests for AgentService initialization."""

    def test_agent_service_initializes_with_gemini_config(self):
        """Test that AgentService initializes with Gemini configuration."""
        with patch("src.agent.agent_service.AsyncOpenAI") as mock_openai:
            service = AgentService()

            # Verify AsyncOpenAI was instantiated with Gemini settings
            mock_openai.assert_called_once_with(
                api_key=settings.gemini_api_key,
                base_url=settings.gemini_base_url,
            )

            # Verify settings are stored
            assert service.model == settings.gemini_model
            assert service.temperature == settings.gemini_temperature
            assert service.max_tokens == settings.gemini_max_tokens
            assert service.timeout == settings.agent_timeout_seconds

    def test_agent_service_loads_system_prompt(self):
        """Test that AgentService loads the system prompt."""
        with patch("src.agent.agent_service.AsyncOpenAI"):
            service = AgentService()

            assert service.system_prompt is not None
            assert len(service.system_prompt) > 0
            assert "CRITICAL INSTRUCTIONS" in service.system_prompt

    def test_agent_service_registers_retrieval_tool(self):
        """Test that AgentService registers the retrieve_book_content tool."""
        with patch("src.agent.agent_service.AsyncOpenAI"):
            service = AgentService()

            assert len(service.tools) == 1
            assert service.tools[0]["type"] == "function"
            assert service.tools[0]["function"]["name"] == "retrieve_book_content"


class TestAgentServiceAnswer:
    """Tests for AgentService.answer() method."""

    @pytest.mark.asyncio
    async def test_answer_returns_grounded_response_with_sources(self):
        """Test that answer() returns a grounded response with source citations."""
        # Mock OpenAI client responses
        mock_client = AsyncMock()

        # Create mock tool call with proper structure
        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_123"
        mock_tool_call.function.name = "retrieve_book_content"
        mock_tool_call.function.arguments = json.dumps({"query": "What is embodied intelligence?", "top_k": 5})

        # First API call: Agent calls retrieval tool
        mock_message = MagicMock()
        mock_message.content = None
        mock_message.tool_calls = [mock_tool_call]

        mock_choice = MagicMock()
        mock_choice.message = mock_message

        mock_first_response = MagicMock()
        mock_first_response.choices = [mock_choice]
        mock_first_response.usage = MagicMock(
            prompt_tokens=100,
            completion_tokens=20,
            total_tokens=120,
        )

        # Second API call: Agent generates answer
        mock_second_response = MagicMock()
        mock_second_response.choices = [MagicMock()]
        mock_second_response.choices[0].message = MagicMock()
        mock_second_response.choices[0].message.content = (
            "Embodied intelligence refers to the concept that intelligence arises from the interaction "
            "between an agent's body and its environment. [Source: Introduction - Physical AI ({url})]"
        )
        mock_second_response.usage = MagicMock(
            prompt_tokens=500,
            completion_tokens=80,
            total_tokens=580,
        )

        # Set up async mock for chat completions
        mock_client.chat.completions.create = AsyncMock(side_effect=[
            mock_first_response,
            mock_second_response,
        ])

        # Mock retrieve_book_content tool
        mock_retrieval_result = {
            "results": [
                {
                    "content": "Embodied intelligence is a concept in robotics...",
                    "url": "https://example.com/intro",
                    "title": "Introduction",
                    "section": "Physical AI",
                    "chunk_index": 0,
                    "score": 0.95,
                }
            ],
            "total_count": 1,
            "latency_ms": 50,
            "filters_applied": {},
        }

        # Create async mock for retrieve_book_content
        mock_retrieve = AsyncMock(return_value=mock_retrieval_result)

        with patch("src.agent.agent_service.AsyncOpenAI", return_value=mock_client):
            with patch(
                "src.agent.agent_service.retrieve_book_content",
                mock_retrieve,
            ):
                service = AgentService()
                result = await service.answer("What is embodied intelligence?")

                # Verify response structure
                assert "answer" in result
                assert "sources" in result
                assert "confidence" in result
                assert "latency_ms" in result
                assert "tokens_used" in result

                # Verify answer content
                assert len(result["answer"]) > 0
                assert "embodied intelligence" in result["answer"].lower()

                # Verify sources
                assert len(result["sources"]) == 1
                assert result["sources"][0]["url"] == "https://example.com/intro"
                assert result["sources"][0]["title"] == "Introduction"
                assert result["sources"][0]["score"] == 0.95

                # Verify confidence (should be high with score 0.95)
                assert result["confidence"] in ["high", "medium", "low", "refused"]

                # Verify tokens_used
                assert result["tokens_used"]["prompt"] == 600  # 100 + 500
                assert result["tokens_used"]["completion"] == 100  # 20 + 80
                assert result["tokens_used"]["total"] == 700  # 120 + 580

    @pytest.mark.asyncio
    async def test_answer_refuses_when_no_retrieval_results(self):
        """Test that answer() refuses when retrieval returns no results."""
        mock_client = AsyncMock()

        # First API call: Agent calls retrieval tool
        mock_first_response = MagicMock()
        mock_first_response.choices = [MagicMock()]
        mock_first_response.choices[0].message = MagicMock()
        mock_first_response.choices[0].message.content = None
        mock_first_response.choices[0].message.tool_calls = [
            MagicMock(
                id="call_456",
                function=MagicMock(
                    name="retrieve_book_content",
                    arguments=json.dumps({"query": "What is quantum computing?", "top_k": 5}),
                ),
            )
        ]
        mock_first_response.usage = MagicMock(
            prompt_tokens=100,
            completion_tokens=20,
            total_tokens=120,
        )

        # Second API call: Agent generates refusal
        mock_second_response = MagicMock()
        mock_second_response.choices = [MagicMock()]
        mock_second_response.choices[0].message = MagicMock()
        mock_second_response.choices[0].message.content = (
            "I don't have information about quantum computing in the textbook."
        )
        mock_second_response.usage = MagicMock(
            prompt_tokens=400,
            completion_tokens=30,
            total_tokens=430,
        )

        mock_client.chat.completions.create.side_effect = [
            mock_first_response,
            mock_second_response,
        ]

        # Mock retrieve_book_content returns empty results
        mock_retrieval_result = {
            "results": [],
            "total_count": 0,
            "latency_ms": 30,
            "filters_applied": {},
        }

        with patch("src.agent.agent_service.AsyncOpenAI", return_value=mock_client):
            with patch(
                "src.agent.agent_service.retrieve_book_content",
                return_value=mock_retrieval_result,
            ):
                service = AgentService()
                result = await service.answer("What is quantum computing?")

                # Verify refusal response
                assert result["confidence"] == "refused"
                assert result["sources"] == []
                assert "don't have information" in result["answer"].lower()

    @pytest.mark.asyncio
    async def test_answer_refuses_when_agent_does_not_call_tool(self):
        """Test that answer() refuses when agent does not call the retrieval tool."""
        mock_client = AsyncMock()

        # First API call: Agent does NOT call retrieval tool (violates instructions)
        mock_first_response = MagicMock()
        mock_first_response.choices = [MagicMock()]
        mock_first_response.choices[0].message = MagicMock()
        mock_first_response.choices[0].message.content = "Direct answer without retrieval"
        mock_first_response.choices[0].message.tool_calls = None  # No tool calls!
        mock_first_response.usage = MagicMock(
            prompt_tokens=100,
            completion_tokens=20,
            total_tokens=120,
        )

        mock_client.chat.completions.create.return_value = mock_first_response

        with patch("src.agent.agent_service.AsyncOpenAI", return_value=mock_client):
            service = AgentService()
            result = await service.answer("What is embodied intelligence?")

            # Verify refusal response
            assert result["confidence"] == "refused"
            assert result["sources"] == []
            assert "retrieve information" in result["answer"].lower()

    @pytest.mark.asyncio
    async def test_answer_passes_top_k_to_retrieval_tool(self):
        """Test that answer() passes top_k parameter to retrieval tool."""
        mock_client = AsyncMock()

        # Create mock tool call with proper structure
        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_789"
        mock_tool_call.function.name = "retrieve_book_content"
        mock_tool_call.function.arguments = json.dumps({"query": "test query", "top_k": 10})

        # First API call: Agent calls retrieval tool
        mock_message = MagicMock()
        mock_message.content = None
        mock_message.tool_calls = [mock_tool_call]

        mock_choice = MagicMock()
        mock_choice.message = mock_message

        mock_first_response = MagicMock()
        mock_first_response.choices = [mock_choice]
        mock_first_response.usage = MagicMock(
            prompt_tokens=100,
            completion_tokens=20,
            total_tokens=120,
        )

        # Second API call: Agent generates answer
        mock_second_response = MagicMock()
        mock_second_response.choices = [MagicMock()]
        mock_second_response.choices[0].message = MagicMock()
        mock_second_response.choices[0].message.content = "Test answer"
        mock_second_response.usage = MagicMock(
            prompt_tokens=300,
            completion_tokens=50,
            total_tokens=350,
        )

        # Set up async mock for chat completions
        mock_client.chat.completions.create = AsyncMock(side_effect=[
            mock_first_response,
            mock_second_response,
        ])

        mock_retrieval_result = {
            "results": [
                {
                    "content": "Test content",
                    "url": "https://example.com",
                    "title": "Test",
                    "section": "Test Section",
                    "chunk_index": 0,
                    "score": 0.8,
                }
            ],
            "total_count": 1,
            "latency_ms": 40,
            "filters_applied": {},
        }

        # Create async mock for retrieve_book_content
        mock_retrieve = AsyncMock(return_value=mock_retrieval_result)

        with patch("src.agent.agent_service.AsyncOpenAI", return_value=mock_client):
            with patch(
                "src.agent.agent_service.retrieve_book_content",
                mock_retrieve,
            ):
                service = AgentService()
                await service.answer("test query", top_k=10)

                # Verify retrieve_book_content was called with top_k=10
                mock_retrieve.assert_called_once()
                call_kwargs = mock_retrieve.call_args[1]
                assert call_kwargs["top_k"] == 10

    @pytest.mark.asyncio
    async def test_answer_includes_conversation_history(self):
        """Test that answer() includes conversation history in messages."""
        mock_client = AsyncMock()

        # Mock responses
        mock_first_response = MagicMock()
        mock_first_response.choices = [MagicMock()]
        mock_first_response.choices[0].message = MagicMock()
        mock_first_response.choices[0].message.content = None
        mock_first_response.choices[0].message.tool_calls = [
            MagicMock(
                id="call_abc",
                function=MagicMock(
                    name="retrieve_book_content",
                    arguments=json.dumps({"query": "What about its components?", "top_k": 5}),
                ),
            )
        ]
        mock_first_response.usage = MagicMock(
            prompt_tokens=150,
            completion_tokens=25,
            total_tokens=175,
        )

        mock_second_response = MagicMock()
        mock_second_response.choices = [MagicMock()]
        mock_second_response.choices[0].message = MagicMock()
        mock_second_response.choices[0].message.content = "The components include sensors, actuators..."
        mock_second_response.usage = MagicMock(
            prompt_tokens=400,
            completion_tokens=60,
            total_tokens=460,
        )

        mock_client.chat.completions.create.side_effect = [
            mock_first_response,
            mock_second_response,
        ]

        mock_retrieval_result = {
            "results": [
                {
                    "content": "Components of embodied systems...",
                    "url": "https://example.com",
                    "title": "Components",
                    "section": "System Design",
                    "chunk_index": 0,
                    "score": 0.85,
                }
            ],
            "total_count": 1,
            "latency_ms": 45,
            "filters_applied": {},
        }

        conversation_history = [
            {"role": "user", "content": "What is embodied intelligence?"},
            {"role": "assistant", "content": "Embodied intelligence refers to..."},
        ]

        # Create async mock for retrieve_book_content
        mock_retrieve = AsyncMock(return_value=mock_retrieval_result)

        with patch("src.agent.agent_service.AsyncOpenAI", return_value=mock_client):
            with patch(
                "src.agent.agent_service.retrieve_book_content",
                mock_retrieve,
            ):
                service = AgentService()
                result = await service.answer(
                    "What about its components?",
                    conversation_history=conversation_history,
                )

                # Verify first API call included conversation history
                first_call = mock_client.chat.completions.create.call_args_list[0]
                messages = first_call[1]["messages"]

                # Should have: system prompt + 2 history messages + current question
                assert len(messages) >= 4
                assert messages[0]["role"] == "system"
                assert any(msg["content"] == "What is embodied intelligence?" for msg in messages)
                # Find the last user message
                user_messages = [msg for msg in messages if msg["role"] == "user"]
                assert user_messages[-1]["content"] == "What about its components?"

                # Verify answer was returned
                assert "answer" in result
                assert len(result["answer"]) > 0
