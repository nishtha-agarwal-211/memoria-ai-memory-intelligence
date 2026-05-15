"""
LLM Service for the AI Memory Intelligence System.

Handles communication with OpenAI-compatible LLM APIs.
Supports both streaming (SSE) and non-streaming responses.
Injects compressed memory context into the system prompt.

If no API key is configured, falls back to a mock mode that
generates intelligent-sounding responses for demo purposes.
"""
import asyncio
import json
import time
from openai import AsyncOpenAI
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# ── System prompt template with memory injection ──
SYSTEM_PROMPT_TEMPLATE = """You are an advanced AI assistant with an intelligent memory system. You have access to relevant memories about the user that were retrieved from your memory engine.

RETRIEVED MEMORIES:
{memory_context}

INSTRUCTIONS:
- Use the retrieved memories to provide personalized, context-aware responses
- Reference specific memories when relevant (e.g., "Based on what I remember about your preferences...")
- Be conversational, helpful, and demonstrate that you truly understand the user
- If memories conflict, prefer more recent information
- Don't fabricate memories — only reference what's provided above
- If no memories are relevant, respond naturally without forcing memory references

You are not just answering questions — you are demonstrating intelligent memory-augmented AI."""


class LLMService:
    """Manages LLM interactions with memory-augmented prompts."""

    def __init__(self):
        self.client: AsyncOpenAI | None = None
        self.model = settings.openai_model
        self.is_mock = False

    def initialize(self):
        """Initialize the OpenAI client."""
        api_key = settings.openai_api_key

        if not api_key or api_key == "sk-mock-key" or api_key.startswith("sk-your"):
            logger.warning("No valid OpenAI API key found — using MOCK mode")
            self.is_mock = True
            return

        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=settings.openai_base_url,
        )
        logger.info(f"LLM client initialized (model: {self.model})")

    async def generate_response(
        self,
        user_message: str,
        memory_context: str,
        conversation_history: list[dict] | None = None,
    ) -> dict:
        """
        Generate a non-streaming LLM response with memory context.
        
        Returns:
            {"response": str, "tokens_used": int, "latency_ms": float}
        """
        start = time.time()

        if self.is_mock:
            response = await self._mock_response(user_message, memory_context)
            elapsed = (time.time() - start) * 1000
            return {
                "response": response,
                "tokens_used": len(response.split()) * 2,  # Rough estimate
                "latency_ms": round(elapsed, 1),
            }

        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            memory_context=memory_context if memory_context else "No relevant memories found."
        )

        messages = [{"role": "system", "content": system_prompt}]

        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history[-6:])  # Last 3 exchanges

        messages.append({"role": "user", "content": user_message})

        try:
            completion = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
            )
            response = completion.choices[0].message.content
            tokens = completion.usage.total_tokens if completion.usage else 0
            elapsed = (time.time() - start) * 1000

            return {
                "response": response,
                "tokens_used": tokens,
                "latency_ms": round(elapsed, 1),
            }
        except Exception as e:
            logger.error(f"LLM API error: {e}")
            fallback = await self._mock_response(user_message, memory_context)
            elapsed = (time.time() - start) * 1000
            return {
                "response": fallback,
                "tokens_used": 0,
                "latency_ms": round(elapsed, 1),
            }

    async def generate_stream(
        self,
        user_message: str,
        memory_context: str,
        conversation_history: list[dict] | None = None,
    ):
        """
        Generate a streaming LLM response for SSE.
        Yields chunks of text as they arrive.
        """
        if self.is_mock:
            async for chunk in self._mock_stream(user_message, memory_context):
                yield chunk
            return

        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            memory_context=memory_context if memory_context else "No relevant memories found."
        )

        messages = [{"role": "system", "content": system_prompt}]
        if conversation_history:
            messages.extend(conversation_history[-6:])
        messages.append({"role": "user", "content": user_message})

        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
                stream=True,
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"LLM streaming error: {e}")
            async for chunk in self._mock_stream(user_message, memory_context):
                yield chunk

    async def _mock_response(self, user_message: str, memory_context: str) -> str:
        """Generate a mock response that demonstrates memory awareness."""
        await asyncio.sleep(0.5)  # Simulate latency

        if memory_context and memory_context.strip():
            # Parse some memory content for the response
            memories = [line.strip("- ").strip() for line in memory_context.split("\n") if line.startswith("- ")]
            if memories:
                mem_refs = memories[:2]
                return (
                    f"Based on what I know about you, I can see that: "
                    f"**{mem_refs[0]}**. "
                    f"{'I also recall that **' + mem_refs[1] + '**. ' if len(mem_refs) > 1 else ''}"
                    f"\n\nRegarding your question about '{user_message[:80]}' — "
                    f"I've cross-referenced this with {len(memories)} relevant memories from my memory engine. "
                    f"This allows me to give you a more personalized and context-aware response.\n\n"
                    f"My memory intelligence system scored these memories using a hybrid ranking approach "
                    f"combining semantic similarity, recency, importance, and your past feedback. "
                    f"The right panel shows exactly why each memory was selected.\n\n"
                    f"*This is a demo response from the mock LLM. Connect an OpenAI API key for real responses.*"
                )

        return (
            f"I received your message: '{user_message[:100]}'\n\n"
            f"Currently, I don't have any relevant memories stored about this topic. "
            f"You can add memories using the memory panel on the left, and I'll use them "
            f"to provide more personalized responses.\n\n"
            f"Try storing some preferences, facts about yourself, or context about what "
            f"you're working on. My memory engine will automatically retrieve the most "
            f"relevant memories for each conversation.\n\n"
            f"*This is a demo response from the mock LLM. Connect an OpenAI API key for real responses.*"
        )

    async def _mock_stream(self, user_message: str, memory_context: str):
        """Streaming version of mock response — yields word by word."""
        full_response = await self._mock_response(user_message, memory_context)
        words = full_response.split(" ")

        for i, word in enumerate(words):
            separator = " " if i > 0 else ""
            yield separator + word
            await asyncio.sleep(0.03)  # Simulate streaming delay


# Singleton instance
llm_service = LLMService()
