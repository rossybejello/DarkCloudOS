import yaml

class CICDGenerator:
    TEMPLATES = {
        "github": {
            "basic": """
name: CI
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Build
      run: |
        npm install
        npm run build
            """,
            "security": """
name: Security Scan
on: [push]
jobs:
  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Dependency Check
      uses: dependency-check/Dependency-Check_Action@main
      with:
        project: 'your-project'
        scan: '**/*.js'
            """
        },
        "gitlab": {
            "basic": """
image: node:14
stages:
  - build
build:
  stage: build
  script:
    - npm install
    - npm run build
            """
        }
    }

    def generate_pipeline(self, provider, template_type="basic"):
        return self.TEMPLATES.get(provider, {}).get(template_type, "")
    
    def save_pipeline_file(self, provider, path):
        content = self.generate_pipeline(provider)
        with open(path, 'w') as f:
            if provider == "github":
                f.write(content)
            elif provider == "gitlab":
                f.write(content)
        return f"Created {provider} pipeline at {path}"