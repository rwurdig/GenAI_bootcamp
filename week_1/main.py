"""
Simple LLM Application using Groq API
Week 1 - Core functionality with chatbot identity
Supports both Groq models (Llama) and OpenAI models (GPT-5 family)
"""
from groq import Groq
from openai import OpenAI
from appconfig import env_config

class LLMApp:

    def __init__(self, api_key=None, model="llama-3.3-70b-versatile", chatbot_name="Thoth", default_system_prompt=None):
        """
        Initialize the LLM application
        
        Args:
            api_key: Groq API key (if None, reads from GROQ_API_KEY or OPENAI_API_KEY env var)
            model: Model to use for completions
            chatbot_name: Name/identity for the chatbot (default: "Thoth")
            default_system_prompt: Default system prompt if user doesn't provide one
            conversation_history: List of conversations in a session
        """

        self.model = model
        self.chatbot_name = chatbot_name
        self.default_system_prompt = default_system_prompt
        self.conversation_history = []
        
        # Determine provider based on model name
        if model.startswith("gpt-"):
            self.provider = "openai"
            self.api_key = api_key or env_config.openai_api_key
            if not self.api_key:
                raise ValueError("OpenAI API key must be provided or set in `OPENAI_API_KEY` environment variable")
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.provider = "groq"
            self.api_key = api_key or env_config.groq_api_key
            if not self.api_key:
                raise ValueError("Groq API key must be provided or set in `GROQ_API_KEY` environment variable")
            self.client = Groq(api_key=self.api_key)

    def chat(self, user_message, system_prompt=None, temperature=0.5, max_tokens=1024):
        """
        Send a message and get a response
        
        Args:
            user_message: The user's message
            system_prompt: Optional system prompt to set context
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
            
        Returns:
            The assistant's response text
        """
        messages = []

        # Build complete system prompt combining chatbot name with system prompt
        if system_prompt:
            complete_prompt = f"Your name is {self.chatbot_name}. {system_prompt}"
        elif self.default_system_prompt:
            complete_prompt = f"Your name is {self.chatbot_name}. {self.default_system_prompt}"
        else:
            complete_prompt = f"Your name is {self.chatbot_name}. You are a helpful, knowledgeable, and friendly AI assistant."
        
        # Add system prompt
        messages.append(
            {
                "role": "system",
                "content": complete_prompt
            }
        )

        # Add conversation history
        if self.conversation_history:
            messages.extend(self.conversation_history)
        
        # Add current user's message
        messages.append(
            {
                "role": "user",
                "content": f"{user_message}"
            }
        )

        # Make LLM call based on provider
        if self.provider == "openai":
            # For GPT-5 models, use max_completion_tokens
            if self.model.startswith("gpt-5"):
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_completion_tokens=max_tokens,
                )
            else:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
        else:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        # Extract response text
        assistant_message = response.choices[0].message.content

        # Update conversation history
        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": assistant_message})

        return assistant_message
    
    def clear_history(self):
        """Clear the conversation history"""
        self.conversation_history = []
    
    def get_history(self):
        """Get the current conversation history"""
        return self.conversation_history


if __name__=="__main__":
    # Initialize the app
    app = LLMApp(
        model="llama-3.3-70b-versatile",
        chatbot_name="Thoth",
        default_system_prompt="You are a helpful AI assistant focused on providing clear and accurate information."
    )
    
    print(f"\nConnected to {app.provider.upper()}! Chatbot name: {app.chatbot_name}")
    print("Type 'exit' to quit\n")
    
    while True:
        message = input("What do you want to ask: ")
        
        if message.lower() in ['exit', 'quit', 'bye']:
            print(f"\n{app.chatbot_name}: Goodbye!")
            break
            
        response = app.chat(message)
        print(f"\n{app.chatbot_name} Response: {response}\n")






