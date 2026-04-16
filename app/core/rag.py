import time
from typing import Dict, Any
from app.services.vector_store import VectorStoreService
from app.services.llm_service import LLMService
from app.core.security import SecurityGuard
from app.core.config import config

class RAGPipeline:
    def __init__(self):
        self.vector_store = VectorStoreService()
        self.llm = LLMService()
        self.security = SecurityGuard()

    async def run(self, query: str) -> Dict[str, Any]:
        start_time = time.time()
        
        try:
            # 1. Security Check (Injection)
            is_safe, reason = self.security.check_query(query)
            if not is_safe:
                return {
                    "answer": reason,
                    "status": "blocked",
                    "latency": time.time() - start_time
                }

            # 2. Retrieval
            try:
                search_results = self.vector_store.search(query, n_results=5)
            except Exception as e:
                return {
                    "answer": "The retrieval system is momentarily unavailable. Please try again.",
                    "status": "error",
                    "latency": time.time() - start_time
                }
            
            # 3. Domain Boundary Check (using distance score)
            # If distance is too high (>1.0), it is likely out of domain.
            if not search_results or search_results[0]["score"] > 1.0: 
                is_relevant = await self.llm.check_domain_relevance(query)
                if not is_relevant:
                    return {
                        "answer": config.REJECTION_MESSAGE,
                        "status": "out_of_domain",
                        "latency": time.time() - start_time
                    }

            # 4. Context Preparation with Filtering and Highlighting
            # Only keep chunks from the most relevant source if a clear keyword is found
            keywords_to_sources = {
                "customer": "customers.txt",
                "payment intent": "payment_intents.txt",
                "charge": "charges.txt",
                "refund": "refunds.txt",
                "webhook": "webhooks.txt",
                "error": "errors.txt",
                "payment method": "payments.txt"
            }
            
            filtered_results = search_results
            for kw, source in keywords_to_sources.items():
                if kw in query.lower():
                    # Prioritize chunks from the specific source
                    filtered_results = [r for r in search_results if r["metadata"]["source"] == source]
                    # If no chunks from that source, fallback to all results
                    if not filtered_results:
                        filtered_results = search_results
                    break
            
            context = "\n\n".join([r["content"] for r in filtered_results])
            
            # Highlighting the endpoint to force model attention
            # (Adding simple regex or string replacement for common endpoint patterns)
            import re
            context = re.sub(r'(POST|GET|PATCH|DELETE) (/v1/\w+)', r'>>> \1 \2 <<<', context)
            
            print(f"DEBUG - FILTERED CONTEXT FOR '{query}':\n{context}\n{'-'*50}")
            
            # 5. Generation
            answer = await self.llm.generate_response(query, context)
            
            return {
                "answer": answer,
                "context_used": list(set([r["metadata"]["source"] for r in search_results])), # Unique sources
                "status": "success",
                "latency": time.time() - start_time
            }
        except Exception as e:
             return {
                "answer": f"A system error occurred: {str(e)}",
                "status": "error",
                "latency": time.time() - start_time
            }
