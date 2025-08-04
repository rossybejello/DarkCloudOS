import openai
import os

class AIDevelopmentAssistant:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        openai.api_key = self.api_key
    
    def generate_code(self, prompt, language="python"):
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"You are an expert {language} developer"},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message['content']
    
    def explain_code(self, code_snippet):
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a code explanation assistant"},
                {"role": "user", "content": f"Explain this code:\n\n{code_snippet}"}
            ]
        )
        return response.choices[0].message['content']
    
    def find_security_issues(self, code):
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a security expert"},
                {"role": "user", "content": f"Find security vulnerabilities in this code:\n\n{code}"}
            ]
        )
        return response.choices[0].message['content']