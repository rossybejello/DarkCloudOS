import openai
import os
import re
import logging
from core.knowledge_base import KnowledgeBase

class AIAssistant:
    CAPABILITIES = [
        "code_generation",
        "code_explanation",
        "bug_fixing",
        "documentation",
        "optimization",
        "security_audit"
    ]
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.knowledge_base = KnowledgeBase()
        self.logger = logging.getLogger('AIAssistant')
        
    def generate_code(self, prompt, language="python", context=None):
        """Generate code based on natural language prompt"""
        system_prompt = f"You are an expert {language} developer. Generate clean, efficient code."
        return self._query(system_prompt, prompt, context)
    
    def explain_code(self, code):
        """Explain what the code does"""
        system_prompt = "You are a code explanation assistant. Explain the code clearly and concisely."
        return self._query(system_prompt, f"Explain this code:\n\n{code}")
    
    def fix_bugs(self, code, error_message=None):
        """Fix bugs in the given code"""
        system_prompt = "You are a debugging assistant. Fix the bugs in the provided code."
        prompt = f"Fix the bugs in this code:\n\n{code}"
        if error_message:
            prompt += f"\n\nError message: {error_message}"
        return self._query(system_prompt, prompt)
    
    def generate_documentation(self, code, style="docstring"):
        """Generate documentation for code"""
        system_prompt = "You are a documentation assistant. Generate professional documentation."
        prompt = f"Generate {style} documentation for this code:\n\n{code}"
        return self._query(system_prompt, prompt)
    
    def optimize_code(self, code):
        """Optimize code for performance"""
        system_prompt = "You are a performance optimization assistant. Optimize the code for speed and efficiency."
        return self._query(system_prompt, f"Optimize this code:\n\n{code}")
    
    def security_audit(self, code):
        """Find security vulnerabilities in code"""
        system_prompt = "You are a security auditor. Identify security vulnerabilities in the provided code."
        prompt = f"Perform a security audit on this code:\n\n{code}"
        return self._query(system_prompt, prompt)
    
    def _query(self, system_prompt, user_prompt, context=None):
        """Send query to AI model"""
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # Add context if provided
            if context:
                messages.append({"role": "assistant", "content": context})
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=messages,
                max_tokens=1500,
                temperature=0.7
            )
            
            return response.choices[0].message['content']
        except Exception as e:
            self.logger.error(f"AI query failed: {str(e)}")
            return "AI service unavailable. Please check your API key and network connection."
    
    def integrate_knowledge(self, response):
        """Enrich AI response with knowledge base content"""
        # Extract key concepts
        concepts = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', response)
        
        # Get knowledge for each concept
        enriched = response
        for concept in set(concepts):
            resource = self.knowledge_base.get_resource("concepts", concept)
            if resource:
                enriched += f"\n\n**Knowledge: {concept}**\n{resource['content'][:200]}..."
                
        return enriched