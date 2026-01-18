"""
LLM Service Module

This module provides interface for interacting with Google Gemini LLM.
It also integrates web search capabilities via SerpAPI.

Key Features:
- Google Gemini support
- Web search integration
- Configurable parameters (temperature, model selection)
- Automatic API key management from environment

Usage:
    llm_service = LLMService()
    response = await llm_service.generate_response(
        query="What is AI?",
        model="gemini",
        temperature=0.7
    )
"""

import google.generativeai as genai
from typing import Dict, Any, Optional, List
import httpx
from app.core.config import settings

class LLMService:
    def __init__(self):
        # Initialize Google Gemini
        if settings.GOOGLE_API_KEY:
            genai.configure(api_key=settings.GOOGLE_API_KEY)
        else:
            raise ValueError("GOOGLE_API_KEY is required")
        
        # List available models on initialization
        try:
            print("Checking available Gemini models...")
            for model in genai.list_models():
                if 'generateContent' in model.supported_generation_methods:
                    print(f"Available model: {model.name}")
        except Exception as e:
            print(f"Could not list models: {e}")

    async def generate_response(
        self,
        query: str,
        context: Optional[str] = None,
        custom_prompt: Optional[str] = None,
        model: str = "gemini",
        model_name: Optional[str] = None,
        use_web_search: bool = False,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Generate response using Google Gemini LLM"""
        
        # Web search is disabled (SerpAPI commented out)
        # Uncomment web_search method and SERPAPI_KEY in config.py to enable
        # web_context = ""
        # if use_web_search:
        #     web_results = await self.web_search(query)
        #     web_context = self._format_web_results(web_results)

        # Build the prompt
        system_prompt = custom_prompt or "You are a helpful AI assistant."
        
        user_message = query
        if context:
            user_message = f"Context: {context}\n\nQuestion: {query}"
        # if web_context:
        #     user_message = f"{user_message}\n\nWeb Search Results: {web_context}"

        # Generate response using Gemini
        return await self._generate_gemini_response(
            system_prompt, user_message, model_name or "models/gemini-2.5-flash", temperature
        )

    async def _generate_gemini_response(
        self, system_prompt: str, user_message: str, model: str, temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Generate response using Google Gemini"""
        try:
            # List of actual available models (from test_gemini.py output)
            models_to_try = [
                "models/gemini-2.5-flash",      # Fastest, recommended
                "models/gemini-2.5-pro",        # Most capable
                "models/gemini-2.0-flash",      # Alternative fast
                "models/gemini-2.0-flash-001",  # Stable version
                model,  # Try the requested model
            ]
            
            last_error = None
            for model_name in models_to_try:
                try:
                    print(f"Attempting to use model: {model_name}")
                    
                    # Combine system prompt and user message for Gemini
                    full_prompt = f"{system_prompt}\n\n{user_message}"
                    
                    # Use the simpler API without complex configuration
                    model_instance = genai.GenerativeModel(model_name)
                    response = model_instance.generate_content(full_prompt)
                    
                    # Check if response has text
                    if response.text:
                        print(f"✅ Success with model: {model_name}")
                        return {
                            "response": response.text,
                            "model": model_name,
                            "provider": "gemini"
                        }
                    else:
                        print(f"❌ No text in response from {model_name}")
                        continue
                    
                except Exception as e:
                    last_error = e
                    print(f"❌ Failed with {model_name}: {str(e)}")
                    continue
            
            # If all attempts failed
            raise Exception(f"All model attempts failed. Last error: {str(last_error)}")
            
        except Exception as e:
            print(f"Gemini API error: {str(e)}")
            raise Exception(f"Gemini API error: {str(e)}")

    # WEB SEARCH METHODS - COMMENTED OUT (SerpAPI not configured)
    # Uncomment these methods and add SERPAPI_KEY to config.py to enable web search
    
    # async def web_search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
    #     """Perform web search using SerpAPI"""
    #     if not settings.SERPAPI_KEY or settings.SERPAPI_KEY == "your_serpapi_key_here":
    #         print("SerpAPI key not configured, skipping web search")
    #         return []
    #
    #     try:
    #         async with httpx.AsyncClient() as client:
    #             params = {
    #                 "engine": "google",
    #                 "q": query,
    #                 "api_key": settings.SERPAPI_KEY,
    #                 "num": num_results
    #             }
    #             
    #             response = await client.get(
    #                 "https://serpapi.com/search",
    #                 params=params,
    #                 timeout=10.0
    #             )
    #             
    #             if response.status_code == 200:
    #                 data = response.json()
    #                 results = []
    #                 
    #                 for result in data.get("organic_results", []):
    #                     results.append({
    #                         "title": result.get("title", ""),
    #                         "snippet": result.get("snippet", ""),
    #                         "link": result.get("link", "")
    #                     })
    #                 
    #                 return results
    #             elif response.status_code == 401:
    #                 print(f"SerpAPI authentication failed - invalid API key")
    #                 return []
    #             else:
    #                 print(f"SerpAPI error: {response.status_code}")
    #                 return []
    #                 
    #     except Exception as e:
    #         print(f"Web search error: {str(e)}")
    #         return []
    #
    # def _format_web_results(self, results: List[Dict[str, Any]]) -> str:
    #     """Format web search results for context"""
    #     if not results:
    #         return ""
    #     
    #     formatted = "Web Search Results:\n"
    #     for i, result in enumerate(results, 1):
    #         formatted += f"{i}. {result['title']}\n"
    #         formatted += f"   {result['snippet']}\n"
    #         formatted += f"   Source: {result['link']}\n\n"
    #     
    #     return formatted

    def get_available_models(self) -> Dict[str, List[str]]:
        """Get list of available models"""
        return {
            "gemini": [
                "models/gemini-2.5-flash",
                "models/gemini-2.5-pro",
                "models/gemini-2.0-flash"
            ]
        }