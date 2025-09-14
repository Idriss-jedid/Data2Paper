"""
Test script for GeminiProvider
"""
import os
from llm.GeminiProvider import GeminiProvider

def test_gemini_provider():
    # Get API key from environment variable
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY environment variable not set")
        return
    
    # Initialize the provider
    provider = GeminiProvider(api_key=api_key)
    
    # Set the generation model
    provider.set_generation_model("gemini-pro")
    
    # Test text generation
    prompt = "Write a brief summary of the benefits of using AI for report generation."
    response = provider.generate_text(prompt)
    
    if response:
        print("Generated text:")
        print(response)
    else:
        print("Failed to generate text")

if __name__ == "__main__":
    test_gemini_provider()