# LLM Module

This module provides a standardized interface for integrating Large Language Models (LLMs) into the Data2Paper application.

## Structure

- [LLMInterface.py](file:///c%3A/Users/21652/Desktop/LlmProjects/FullStack/Data2Paper/Backend/src/llm/LLMInterface.py): Abstract interface that all LLM providers must implement
- [LLMEnums.py](file:///c%3A/Users/21652/Desktop/LlmProjects/FullStack/Data2Paper/Backend/src/llm/LLMEnums.py): Common enumerations used across LLM providers
- [GeminiProvider.py](file:///c%3A/Users/21652/Desktop/LlmProjects/FullStack/Data2Paper/Backend/src/llm/GeminiProvider.py): Implementation for Google's Gemini AI service
- [test_gemini.py](file:///c%3A/Users/21652/Desktop/LlmProjects/FullStack/Data2Paper/Backend/src/llm/test_gemini.py): Test script for verifying Gemini integration

## Usage

### Setting up Gemini Provider

1. Obtain a Gemini API key from [Google AI Studio](https://aistudio.google.com/)
2. Set the API key as an environment variable:
   ```bash
   export GEMINI_API_KEY=your_api_key_here
   ```

3. Use the provider in your code:
   ```python
   from llm.GeminiProvider import GeminiProvider
   import os
   
   # Initialize the provider
   api_key = os.getenv("GEMINI_API_KEY")
   provider = GeminiProvider(api_key=api_key)
   
   # Set the generation model
   provider.set_generation_model("gemini-pro")
   
   # Generate text
   response = provider.generate_text("Write a summary of AI benefits")
   print(response)
   ```

## Extending with Other LLMs

To add support for other LLMs:

1. Create a new provider class that inherits from [LLMInterface](file:///c%3A/Users/21652/Desktop/LlmProjects/FullStack/Data2Paper/Backend/src/llm/LLMInterface.py#L7-L21)
2. Implement the required methods:
   - [set_generation_model()](file:///c%3A/Users/21652/Desktop/LlmProjects/FullStack/Data2Paper/Backend/src/llm/GeminiProvider.py#L35-L36)
   - [generate_text()](file:///c%3A/Users/21652/Desktop/LlmProjects/FullStack/Data2Paper/Backend/src/llm/GeminiProvider.py#L53-L104)
   - [construct_prompt()](file:///c%3A/Users/21652/Desktop/LlmProjects/FullStack/Data2Paper/Backend/src/llm/GeminiProvider.py#L118-L121)

3. Follow the same pattern as [GeminiProvider.py](file:///c%3A/Users/21652/Desktop/LlmProjects/FullStack/Data2Paper/Backend/src/llm/GeminiProvider.py)