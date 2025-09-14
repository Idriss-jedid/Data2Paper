from llm.LLMInterface import LLMInterface
from llm.LLMEnums import GeminiEnums, DocumentTypeEnum
import google.generativeai as genai
import logging
from typing import List, Union


class GeminiProvider(LLMInterface):

    def __init__(self, api_key: str,
                       default_input_max_characters: int = 1000,
                       default_generation_max_output_tokens: int = 1000,
                       default_generation_temperature: float = 0.1):
        
        self.api_key = api_key

        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature

        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None

        try:
            genai.configure(api_key=self.api_key)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Gemini client: {e}")

        self.enums = GeminiEnums
        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int = None):
        """
        Sets embedding model and optional size.
        If size is None, will attempt to infer it later from API response.
        """
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    def process_text(self, text: str):
        return text[:self.default_input_max_characters].strip()

    def generate_text(self, prompt: str, chat_history: list = None, 
                      max_output_tokens: int = None, temperature: float = None):

        if not self.generation_model_id:
            self.logger.error("Generation model for Gemini was not set")
            return None
        
        max_output_tokens = max_output_tokens or self.default_generation_max_output_tokens
        temperature = temperature or self.default_generation_temperature

        # Initialize chat history if not provided
        if chat_history is None:
            chat_history = []
            
        chat_history.append(self.construct_prompt(prompt=prompt, role=GeminiEnums.USER.value))

        try:
            # Convert chat history to the format expected by Gemini
            history = []
            for msg in chat_history[:-1]:  # All messages except the last one
                history.append({
                    "role": msg["role"],
                    "parts": [{"text": msg["text"]}]
                })
            
            # Initialize the model
            model = genai.GenerativeModel(self.generation_model_id)
            
            # Start chat with history
            chat = model.start_chat(history=history)
            
            # Send the latest message
            response = chat.send_message(
                chat_history[-1]["text"],  # The last message (current prompt)
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_output_tokens,
                    temperature=temperature
                )
            )
            
        except Exception as e:
            self.logger.error(f"Error calling Gemini API: {e}")
            return None

        if not response or not response.text:
            self.logger.error("Error while generating text with Gemini")
            return None
        
        return response.text

    def embed_text(self, text: Union[str, List[str]], document_type: str = None):
        """
        Create embeddings for text(s) using Gemini.
        Returns: list of embedding vectors (each is a list of floats).
        """
        # As per your request, we're not implementing embedding functionality
        self.logger.warning("Embedding functionality is not implemented in this version")
        return None
    
    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "text": prompt,
        }