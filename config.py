import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
QUIZ_MODE = os.getenv("QUIZ_MODE", "word_to_definition")