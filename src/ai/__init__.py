"""
AI模块初始化
"""
from .ollama_client import OllamaClient
from .matcher import OfferMatcher

__all__ = ["OllamaClient", "OfferMatcher"]
