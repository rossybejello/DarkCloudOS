import os
import subprocess

class DocumentationGenerator:
    TOOLS = {
        "python": "pdoc",
        "javascript": "jsdoc",
        "java": "javadoc",
        "csharp": "doxygen"
    }
    
    def generate_docs(self, language, project_path):
        tool = self.TOOLS.get(language.lower())
        if not tool:
            return f"Unsupported language: {language}"
        
        if language == "python":
            cmd = f"pdoc -o docs {project_path}"
        elif language == "javascript":
            cmd = f"jsdoc {project_path} -d docs"
        elif language == "java":
            cmd = f"javadoc -d docs {os.path.join(project_path, 'src', 'main', 'java')}/*.java"
        elif language == "csharp":
            cmd = f"doxygen -g docs/Doxyfile && doxygen docs/Doxyfile"
        
        result = subprocess.run(cmd, shell=True, capture_output=True)
        return result.stdout.decode()
    
    def generate_readme_template(self, project_type):
        templates = {
            "os": "# {project_name}\n\n## Kernel Features\n\n## Building\n\n## Running",
            "react": "# {project_name}\n\n## Setup\n\n## Available Scripts\n\n## Deployment",
            "blockchain": "# {project_name}\n\n## Smart Contracts\n\n## Deployment\n\n## Testing"
        }
        return templates.get(project_type, "# Project Documentation")