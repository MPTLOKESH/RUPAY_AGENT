"""
LLM GENERATION MODULE
Handles answer generation using strict RAG prompting:
1. Construct system prompt with retrieved context
2. Send to LLM with low temperature
3. Enforce context-only answers
4. Handle cases with insufficient context
"""

import os
from typing import Dict, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# Import configuration
from core.rag_config import (
    SYSTEM_PROMPT_TEMPLATE,
    NO_CONTEXT_RESPONSE,
    LLM_TEMPERATURE,
    LLM_MAX_TOKENS,
    VERBOSE
)

# Use the same LLM endpoint as the main application
MODEL_URL = "http://183.82.7.228:9532/v1"


class RAGGeneration:
    """
    Handles answer generation with strict RAG prompting.
    Ensures LLM only uses provided context.
    Uses the same OpenAI-compatible LLM endpoint as the main application.
    """
    
    def __init__(self, model_url: Optional[str] = None):
        """
        Initialize the generation pipeline.
        
        Args:
            model_url: Optional custom model URL (uses default if not provided)
        """
        if VERBOSE:
            print("[GENERATION] Initializing LLM Generation Pipeline...")
        
        # Use provided URL or default to main application's endpoint
        endpoint = model_url or MODEL_URL
        
        # Initialize LLM using OpenAI-compatible endpoint (same as main app)
        self.llm = ChatOpenAI(
            model="/model",
            openai_api_base=endpoint,
            openai_api_key="EMPTY",  # No API key needed for custom endpoint
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS
        )
        
        if VERBOSE:
            print(f"[GENERATION] Using LLM endpoint: {endpoint}")
            print(f"[GENERATION] Temperature: {LLM_TEMPERATURE}")
            print("[GENERATION] Generation pipeline ready.")
    
    def create_prompt(self, question: str, context: str) -> str:
        """
        Create the complete prompt with system instructions.
        
        Args:
            question: User question
            context: Retrieved context
            
        Returns:
            Formatted prompt
        """
        # Use template from config
        prompt = SYSTEM_PROMPT_TEMPLATE.format(
            context=context,
            question=question
        )
        
        return prompt
    
    def generate_answer(
        self, 
        question: str, 
        context: str,
        return_prompt: bool = False
    ) -> Dict:
        """
        Generate answer using retrieved context.
        
        Args:
            question: User question
            context: Retrieved context from online retrieval
            return_prompt: Whether to return the full prompt used
            
        Returns:
            Dictionary with answer and metadata
        """
        if VERBOSE:
            print(f"\n[GENERATION] Generating answer for: {question}")
        
        # Handle case with no context
        if not context or context.strip() == "":
            if VERBOSE:
                print("[GENERATION] No context provided, returning fallback response.")
            return {
                'answer': NO_CONTEXT_RESPONSE,
                'has_context': False
            }
        
        # Construct prompt
        prompt = self.create_prompt(question, context)
        
        if VERBOSE:
            print(f"[GENERATION] Prompt length: {len(prompt)} characters")
        
        try:
            # Create messages for LangChain
            messages = [
                SystemMessage(content=prompt)
            ]
            
            # Generate response using LangChain
            response = self.llm.invoke(messages)
            answer = response.content.strip()
            
            if VERBOSE:
                print(f"[GENERATION] Generated answer ({len(answer)} chars)")
            
            result = {
                'answer': answer,
                'has_context': True
            }
            
            if return_prompt:
                result['prompt'] = prompt
            
            return result
            
        except Exception as e:
            if VERBOSE:
                print(f"[GENERATION] Error generating answer: {e}")
            
            return {
                'answer': f"Error generating answer: {str(e)}",
                'has_context': True,
                'error': str(e)
            }
    
    def validate_answer(self, answer: str) -> Dict:
        """
        Validate the generated answer for common issues.
        
        Args:
            answer: Generated answer
            
        Returns:
            Validation results
        """
        issues = []
        
        # Check if answer is too short
        if len(answer) < 10:
            issues.append("Answer is very short")
        
        # Check for phrases indicating the model is using external knowledge
        external_knowledge_phrases = [
            "as far as i know",
            "based on my knowledge",
            "generally speaking",
            "typically",
            "in my experience"
        ]
        
        answer_lower = answer.lower()
        for phrase in external_knowledge_phrases:
            if phrase in answer_lower:
                issues.append(f"Possible external knowledge usage: '{phrase}'")
        
        # Check if it's the no-context response
        is_no_context = answer.strip() == NO_CONTEXT_RESPONSE
        
        return {
            'is_valid': len(issues) == 0,
            'is_no_context_response': is_no_context,
            'issues': issues
        }


def main():
    """Example usage of RAG generation."""
    print("=" * 70)
    print("RAG GENERATION - ANSWER GENERATION PHASE")
    print("=" * 70)
    
    # Initialize generation pipeline
    generator = RAGGeneration()
    
    # Test cases
    test_cases = [
        {
            'question': 'What are the benefits of RuPay?',
            'context': '''[Passage 1]
RuPay is India's own card payment network. It offers several benefits including lower transaction costs for merchants, seamless domestic transactions, and special offers for cardholders. RuPay cards are accepted at all ATMs and POS terminals across India.

[Passage 2]
The key advantages of RuPay include: zero international transaction fees for domestic cards, priority customer support, and integration with government welfare schemes. RuPay also provides enhanced security features.'''
        },
        {
            'question': 'How do I cancel my card?',
            'context': ''  # No context case
        },
        {
            'question': 'What is the transaction limit?',
            'context': '''[Passage 1]
RuPay debit cards have a daily transaction limit of Rs. 50,000 for POS transactions and Rs. 10,000 for ATM withdrawals. Credit cards have limits based on your credit score and bank policies.'''
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'=' * 70}")
        print(f"TEST CASE {i}")
        print(f"{'=' * 70}")
        
        question = test['question']
        context = test['context']
        
        print(f"\nQuestion: {question}")
        print(f"Context provided: {'Yes' if context else 'No'}")
        
        # Generate answer
        result = generator.generate_answer(question, context, return_prompt=False)
        
        print(f"\nAnswer:\n{result['answer']}")
        
        # Validate
        validation = generator.validate_answer(result['answer'])
        print(f"\nValidation:")
        print(f"  Valid: {validation['is_valid']}")
        print(f"  No-context response: {validation['is_no_context_response']}")
        if validation['issues']:
            print(f"  Issues: {', '.join(validation['issues'])}")


if __name__ == "__main__":
    main()
