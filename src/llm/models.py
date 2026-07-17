"""
Model schemas and utilities for LLM providers.
"""

from typing import List, Dict, Any, Optional, Literal, Union
from pydantic import BaseModel, Field, model_validator


class ModelInfo(BaseModel):
    """
    Information about an LLM model.
    """

    id: str  # Model ID with provider prefix (e.g., "openrouter/model-name")
    provider: Literal["openai", "openrouter"]
    source: Optional[str] = None  # Original source for OpenRouter models
    owned_by: str = "unknown"
    original_id: Optional[str] = None  # Original model ID without provider prefix

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to a dictionary.
        """
        return {
            "id": self.id,
            "provider": self.provider,
            "source": self.source,
            "owned_by": self.owned_by,
            "original_id": self.original_id,
        }


class ModelPermission(BaseModel):
    """
    Model permission information (OpenAI API compatible).
    """

    id: str
    object: str = "model_permission"
    created: int = 0
    allow_create_engine: bool = False
    allow_sampling: bool = True
    allow_logprobs: bool = True
    allow_search_indices: bool = False
    allow_view: bool = True
    allow_fine_tuning: bool = False
    organization: str = "*"
    group: Optional[str] = None
    is_blocking: bool = False


class ModelCard(BaseModel):
    """
    Model card information (OpenAI API compatible).
    """

    id: str
    object: str = "model"
    created: int = 0
    owned_by: str
    root: Optional[str] = None
    parent: Optional[str] = None
    permission: List[ModelPermission] = Field(
        default_factory=lambda: [ModelPermission(id="default_permission")]
    )

    # Additional fields for internal tracking
    provider: str
    source: Optional[str] = None


class ModelList(BaseModel):
    """
    List of models (OpenAI API compatible).
    """

    object: str = "list"
    data: List[ModelCard]


class ChatMessage(BaseModel):
    """
    Chat message (OpenAI API compatible).
    """

    role: Literal["system", "user", "assistant", "tool"]
    content: Optional[str] = ""  # Make content optional with default empty string
    name: Optional[str] = None
    tool_call_id: Optional[str] = None

    class Config:
        # Allow extra fields to be more permissive with client requests
        extra = "allow"


class ChatCompletionRequest(BaseModel):
    """
    Chat completion request (OpenAI API compatible).
    """

    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    stream: Optional[bool] = False
    stop: Optional[Union[str, List[str]]] = None
    max_tokens: Optional[int] = None
    presence_penalty: Optional[float] = 0.0
    frequency_penalty: Optional[float] = 0.0
    logit_bias: Optional[Dict[str, float]] = None
    user: Optional[str] = None
    tool_choice: Optional[Union[str, Dict[str, Any]]] = (
        None  # "none", "auto", or a specific tool
    )
    # Prompt caching options
    use_prompt_cache: Optional[bool] = None  # None means use the default setting
    force_cache_miss: Optional[bool] = (
        False  # Force a cache miss even if cache is enabled
    )

    class Config:
        # Allow extra fields to be more permissive with client requests
        extra = "allow"

    @model_validator(mode="before")
    @classmethod
    def validate_messages(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize the messages field.
        """
        if not isinstance(data, dict):
            return data

        # Handle case where messages might not be in the expected format
        if "messages" in data:
            messages = data["messages"]

            # If messages is not a list, convert it to a list with a single message
            if not isinstance(messages, list):
                data["messages"] = [{"role": "user", "content": str(messages)}]
                return data

            # If messages is a list but not in the expected format, try to normalize
            normalized_messages = []
            for msg in messages:
                if isinstance(msg, dict):
                    # Ensure role is present
                    if "role" not in msg:
                        msg["role"] = "user"

                    # Ensure content is a string
                    if "content" in msg and not isinstance(msg["content"], str):
                        msg["content"] = str(msg["content"])
                    elif "content" not in msg:
                        msg["content"] = ""

                    normalized_messages.append(msg)
                else:
                    # If message is not a dict, convert it to a user message
                    normalized_messages.append({"role": "user", "content": str(msg)})

            data["messages"] = normalized_messages

        return data


class ToolCallFunction(BaseModel):
    """
    Tool call function information (OpenAI API compatible).
    """

    name: str
    arguments: str


class ToolCall(BaseModel):
    """
    Tool call information (OpenAI API compatible).
    """

    id: str
    type: Literal["function"] = "function"
    function: ToolCallFunction


class ChatCompletionChoiceMessage(BaseModel):
    """
    Chat completion choice message (OpenAI API compatible).
    """

    role: Literal["assistant"]
    content: Optional[str] = None
    # Structured function-calling field
    function_call: Optional[ToolCallFunction] = None
    # Legacy tool_calls field (if needed)
    tool_calls: Optional[List[ToolCall]] = None


class ChatCompletionChoice(BaseModel):
    """
    Chat completion choice (OpenAI API compatible).
    """

    index: int
    message: ChatCompletionChoiceMessage
    finish_reason: Optional[
        Literal["stop", "length", "tool_calls", "content_filter"]
    ] = "stop"


class ChatCompletionUsage(BaseModel):
    """
    Chat completion usage information (OpenAI API compatible).
    """

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletion(BaseModel):
    """
    Chat completion response (OpenAI API compatible).
    """

    id: str
    object: Literal["chat.completion"] = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: Optional[ChatCompletionUsage] = None
