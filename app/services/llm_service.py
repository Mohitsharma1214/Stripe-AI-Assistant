from openai import AsyncOpenAI
from app.core.config import config
import logging

class LLMService:
    def __init__(self):
        self.api_key = config.OPENROUTER_API_KEY
        # Fallback routing list - Using reliable OpenRouter free models
        self.models = [
            config.OPENROUTER_MODEL, 
            "llama-3.3-70b-versatile",
        ]
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
            default_headers={
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "Stripe AI Assistant",
            }
        )

    async def generate_response(self, prompt: str, context: str) -> str:
        system_instruction = (
            "You are a Stripe API expert assistant.\n\n"

            "Your answers must be based on the provided Context.\n\n"

            "If the Context contains an API endpoint (for example: 'POST /v1/customers' or anything labeled as 'API Endpoint'), "
            "you MUST use it explicitly in your answer.\n"

            "Do NOT ignore endpoints just because they are embedded in text, highlighted with symbols (>>> <<<), or labeled.\n"
            "Do NOT guess based on general knowledge.\n"
            "Only say 'I don't have enough information' if the endpoint is truly missing in the Context.\n\n"

            "Response format (MANDATORY):\n"
            "1. Short explanation\n"
            "2. API endpoint\n"
            "3. Example\n"
            "4. Notes\n"
            )
        
        full_prompt = f"Context:\n{context}\n\nQuestion: {prompt}"
        
        # Multi-model Fallback Strategy
        last_error = None
        for model in self.models:
            try:
                response = await self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": full_prompt}
                    ],
                    max_tokens=1000, # Added to avoid "Insufficient Credits" 402 errors on large models
                    timeout=30.0
                )
                return response.choices[0].message.content
            except Exception as e:
                logging.warning(f"Model {model} failed, trying fallback. Error: {str(e)}")
                last_error = e
                continue
        
        return f"Error: All AI models failed to respond. Last error: {str(last_error)}"

    async def check_domain_relevance(self, query: str) -> bool:
        prompt = (
            f"You are a domain validator for a Stripe documentation bot.\n"
            f"Determine if the user query is specifically about Stripe's API, features, payments, or documentation.\n"
            f"Queries about general cryptocurrency prices (like Bitcoin), general history, or unrelated topics must be marked as 'No'.\n"
            f"Query: \"{query}\"\n"
            f"Answer ONLY 'Yes' or 'No'."
        )
        
        try:
            # Using the first model in the list for domain check
            response = await self.client.chat.completions.create(
                model=self.models[0],
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=5
            )
            answer = response.choices[0].message.content.lower()
            return "yes" in answer
        except Exception as e:
            logging.error(f"Domain Check Error: {str(e)}")
            return False
