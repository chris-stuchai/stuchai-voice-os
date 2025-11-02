"""
LLM Router module.

Handles LLM interactions with multiple providers (OpenAI, local, LM Studio).
"""

import logging
from typing import Optional, List, Dict
import httpx
import openai
import json
from openai import AsyncOpenAI

from shared.config import settings

logger = logging.getLogger(__name__)


class LLMRouter:
    """
    LLM Router for managing LLM interactions.
    
    Supports multiple providers:
    - OpenAI (GPT models)
    - Local models (via LM Studio or direct)
    - Anthropic (Claude)
    """
    
    def __init__(
        self,
        provider: str = "openai",
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        system_message: Optional[str] = None
    ):
        """
        Initialize LLM router.
        
        Args:
            provider: LLM provider ("openai", "local", "anthropic")
            model: Model identifier
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            system_message: System prompt/instructions
        """
        self.provider = provider or settings.LLM_PROVIDER
        self.model = model or settings.LLM_MODEL
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.system_message = system_message or self._default_system_message()
        
        if self.provider == "openai":
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        elif self.provider == "local":
            self.client = httpx.AsyncClient(base_url=settings.LM_STUDIO_URL)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
    
    def _default_system_message(self) -> str:
        """Default system message for Stella voice."""
        return """You are Stella, a calm, intelligent, executive property assistant. 
You speak clearly, take action fast, and sound like a human operations manager.
Your tone is professional, concise, reassuring, and solution-oriented.
Always be helpful, efficient, and focused on solving problems."""
    
    async def generate_response(
        self,
        user_message: str,
        agent_id: int,
        session_id: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None,
        mcp_enabled: bool = True
    ) -> str:
        """
        Generate LLM response to user message.
        
        Args:
            user_message: User's input message
            agent_id: Agent ID for context
            session_id: Session ID for conversation tracking
            conversation_history: Previous messages in conversation
            mcp_enabled: Whether to enable MCP tool calling
            
        Returns:
            str: LLM response
        """
        if self.provider == "openai":
            return await self._generate_openai(user_message, conversation_history, mcp_enabled)
        elif self.provider == "local":
            return await self._generate_local(user_message, conversation_history)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    async def _generate_openai(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict]] = None,
        mcp_enabled: bool = True
    ) -> str:
        """
        Generate response using OpenAI API with optional MCP tool calling.
        
        Args:
            user_message: User message
            conversation_history: Previous messages
            mcp_enabled: Whether to enable MCP tool calling
            
        Returns:
            str: Generated response
        """
        messages = []
        
        # Add system message
        messages.append({
            "role": "system",
            "content": self.system_message
        })
        
        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Get MCP tools if enabled
        tools = None
        if mcp_enabled:
            try:
                from server.agent.mcp_client import get_mcp_client
                mcp_client = get_mcp_client()
                await mcp_client.initialize()
                mcp_tools = await mcp_client.list_tools()
                
                if mcp_tools:
                    # Convert MCP tools to OpenAI function format
                    tools = []
                    for tool in mcp_tools:
                        tools.append({
                            "type": "function",
                            "function": {
                                "name": tool.get("name", ""),
                                "description": tool.get("description", ""),
                                "parameters": tool.get("parameters", {})
                            }
                        })
            except Exception as e:
                logger.warning(f"Failed to load MCP tools: {e}")
                tools = None
        
        try:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }
            
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"
            
            response = await self.client.chat.completions.create(**kwargs)
            
            message = response.choices[0].message
            
            # Handle tool calls
            if message.tool_calls:
                # Execute tool calls
                tool_results = []
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    
                    try:
                        from server.agent.mcp_client import get_mcp_client
                        mcp_client = get_mcp_client()
                        tool_result = await mcp_client.call_tool(tool_name, tool_args)
                        tool_results.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": tool_name,
                            "content": json.dumps(tool_result)
                        })
                    except Exception as e:
                        logger.error(f"Tool execution error: {e}")
                        tool_results.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": tool_name,
                            "content": json.dumps({"error": str(e)})
                        })
                
                # Add tool results and get final response
                messages.append(message)
                messages.extend(tool_results)
                
                final_response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                return final_response.choices[0].message.content
            
            return message.content
        
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    async def _generate_local(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> str:
        """
        Generate response using local LLM (LM Studio).
        
        Args:
            user_message: User message
            conversation_history: Previous messages
            
        Returns:
            str: Generated response
        """
        messages = []
        
        # Add system message
        messages.append({
            "role": "system",
            "content": self.system_message
        })
        
        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        try:
            response = await self.client.post(
                "/v1/chat/completions",
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens
                }
            )
            response.raise_for_status()
            data = response.json()
            
            return data["choices"][0]["message"]["content"]
        
        except Exception as e:
            logger.error(f"Local LLM API error: {e}")
            raise

