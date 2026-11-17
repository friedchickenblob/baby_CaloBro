"""Single place that configures the LLM client.

Uses Google's Gemini API through its OpenAI-compatible endpoint, so the rest of
the code can keep using the OpenAI SDK. Override the model with GEMINI_MODEL.
"""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

client = OpenAI(
    api_key=GEMINI_API_KEY or "missing-key",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
