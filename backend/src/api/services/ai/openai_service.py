"""
Azure OpenAI service wrapper.
Supports both real Azure OpenAI and mock mode for local development.
"""

from typing import Dict, Any, List, Optional
import json
import logging
from openai import AsyncAzureOpenAI, AsyncOpenAI

from src.api.config import settings

logger = logging.getLogger(__name__)


class OpenAIService:
    """
    Azure OpenAI service wrapper with mock mode support.

    In mock mode (USE_MOCK_OPENAI=true), returns predefined responses.
    In production mode, uses actual Azure OpenAI service.
    """

    def __init__(self):
        """Initialize OpenAI service based on configuration."""
        self.use_mock = settings.USE_MOCK_OPENAI
        self.client = None

        if not self.use_mock:
            # Real Azure OpenAI client
            self.client = AsyncAzureOpenAI(
                api_key=settings.AZURE_OPENAI_API_KEY,
                api_version="2024-02-15-preview",
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
            )
            logger.info("Azure OpenAI client initialized")
        else:
            logger.info("Using mock OpenAI service for local development")

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        response_format: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Generate chat completion.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name (gpt-4, gpt-4o, etc.)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
            response_format: Optional response format (e.g., {"type": "json_object"})

        Returns:
            dict: Response with 'content' and 'usage' keys

        Example:
            >>> messages = [
            ...     {"role": "system", "content": "You are a medical assistant"},
            ...     {"role": "user", "content": "What causes headaches?"}
            ... ]
            >>> response = await openai_service.chat_completion(messages)
            >>> print(response['content'])
        """
        if self.use_mock:
            return self._mock_chat_completion(messages, response_format)

        try:
            kwargs = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }

            if response_format:
                kwargs["response_format"] = response_format

            response = await self.client.chat.completions.create(**kwargs)

            return {
                "content": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "model": response.model,
                "finish_reason": response.choices[0].finish_reason
            }

        except Exception as e:
            logger.error(f"Error calling Azure OpenAI: {e}")
            raise

    def _mock_chat_completion(
        self,
        messages: List[Dict[str, str]],
        response_format: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Mock chat completion for local development.

        Args:
            messages: List of messages
            response_format: Response format specification

        Returns:
            dict: Mock response
        """
        user_message = next((m['content'] for m in messages if m['role'] == 'user'), '')
        system_message = next((m['content'] for m in messages if m['role'] == 'system'), '')

        # Detect intent from user message and system message
        user_lower = user_message.lower()
        system_lower = system_message.lower()

        # Mock questionnaire generation (check system message for "questionnaire generator")
        if 'questionnaire generator' in system_lower or ('generate' in user_lower and 'questions' in user_lower):
            mock_content = {
                "questions": [
                    {
                        "id": "q1",
                        "type": "scale",
                        "question": "On a scale of 1-10, how severe is your headache?",
                        "options": list(range(1, 11)),
                        "required": True
                    },
                    {
                        "id": "q2",
                        "type": "select",
                        "question": "When did your symptoms start?",
                        "options": ["Less than 24 hours ago", "1-3 days ago", "4-7 days ago", "More than a week ago"],
                        "required": True
                    },
                    {
                        "id": "q3",
                        "type": "multiselect",
                        "question": "Which of the following symptoms are you experiencing?",
                        "options": ["Fever", "Chills", "Body aches", "Fatigue", "Nausea", "Cough"],
                        "required": False
                    },
                    {
                        "id": "q4",
                        "type": "text",
                        "question": "Have you taken any medications? If yes, please list them.",
                        "required": False
                    }
                ]
            }
        # Mock symptom analysis response
        elif 'symptom' in user_lower or 'analyze' in user_lower:
            mock_content = {
                "urgency": "moderate",
                "severity": "moderate",
                "triage_level": 3,
                "chief_complaint": "Headache and fever",
                "summary": "Patient presents with headache and fever. Symptoms suggest possible viral infection or flu. Recommend monitoring temperature and rest.",
                "possible_conditions": [
                    "Viral infection",
                    "Influenza",
                    "Common cold"
                ],
                "recommendations": [
                    "Monitor temperature regularly",
                    "Stay hydrated",
                    "Get adequate rest",
                    "Consider over-the-counter pain relief",
                    "Seek medical attention if symptoms worsen"
                ],
                "red_flags": [
                    "Temperature above 103°F (39.4°C)",
                    "Severe headache with neck stiffness",
                    "Difficulty breathing",
                    "Persistent vomiting"
                ],
                "follow_up": "Schedule appointment if symptoms persist beyond 3-5 days"
            }
        # Generic medical response
        else:
            mock_content = {
                "response": "This is a mock response from the OpenAI service. In production, this would be a real AI-generated medical analysis.",
                "note": "Mock mode is enabled for local development"
            }

        # Return as JSON if format specified
        if response_format and response_format.get("type") == "json_object":
            content = json.dumps(mock_content, indent=2)
        else:
            content = json.dumps(mock_content, indent=2) if isinstance(mock_content, dict) else str(mock_content)

        logger.debug(f"Mock OpenAI response generated for: {user_message[:50]}...")

        return {
            "content": content,
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 200,
                "total_tokens": 300
            },
            "model": "mock-gpt-4o",
            "finish_reason": "stop"
        }

    async def analyze_medical_text(
        self,
        text: str,
        system_prompt: str = "You are a medical AI assistant specializing in symptom analysis."
    ) -> str:
        """
        Analyze medical text with a specific system prompt.

        Args:
            text: Text to analyze
            system_prompt: System prompt for context

        Returns:
            str: Analysis result
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]

        response = await self.chat_completion(messages)
        return response['content']


# Global service instance
openai_service = OpenAIService()
