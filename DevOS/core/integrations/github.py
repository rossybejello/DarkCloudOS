from github import Github
from core.auth_manager import AuthManager
from core.error_handler import ErrorHandler

class GitHubIntegration:
    def __init__(self, application):
        self.app = application
        self.auth = application.auth_manager
        self.error_handler = ErrorHandler()
        self.client = None
        
    def connect(self):
        """Connect to GitHub"""
        credentials = self.auth.get_credentials("github")
        if not credentials or "access_token" not in credentials:
            return False
            
        try:
            self.client = Github(credentials["access_token"])
            return True
        except Exception as e:
            self.error_handler.handle(e, "github_connect")
            return False
            
    def create_repository(self, name, description="", private=False):
        """Create a new repository"""
        if not self.client:
            if not self.connect():
                return False
                
        try:
            user = self.client.get_user()
            repo = user.create_repo(name, description=description, private=private)
            return repo.clone_url
        except Exception as e:
            self.error_handler.handle(e, "github_create_repo")
            return False
            
    def push_project(self, local_path, repo_url):
        """Push local project to GitHub repository"""
        # This would actually use git commands
        return f"Project pushed to {repo_url}"