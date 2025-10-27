import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

class EnvConfig():

    def __init__(self):
        # Load API keys from environment
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

# instantiate environment vars
env_config = EnvConfig()

