"""
Abstract interface for LLM providers
"""
from abc import ABC, abstractmethod
from typing import List, Union

class LLMInterface(ABC):
    
    @abstractmethod
    def set_generation_model(self, model_id: str):
        """Set the generation model to use"""
        pass
    
    @abstractmethod
    def generate_text(self, prompt: str, chat_history: list = None, 
                      max_output_tokens: int = None, temperature: float = None):
        """Generate text using the LLM"""
        pass
    
    @abstractmethod
    def construct_prompt(self, prompt: str, role: str):
        """Construct a prompt with the specified role"""
        pass