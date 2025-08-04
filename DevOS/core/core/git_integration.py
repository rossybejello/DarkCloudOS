# core/git_integration.py
# This component handles all interactions with Git version control.

import subprocess
import logging
from typing import Dict, Any, List

# --- DevOS Component: GitIntegration ---
class GitIntegration:
    """
    A class to interact with Git for version control.
    It uses subprocess to execute Git commands and provides robust error handling.
    """
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self._is_git_repo = self._check_if_git_repo()

    def _execute_git_command(self, command: List[str]) -> Dict[str, Any]:
        """
        Executes a git command using subprocess and handles errors.
        Returns a dictionary with success status and output/error messages.
        """
        # Check if the command should run inside a repo or not (e.g., git init)
        if command[0] != "init" and not self._is_git_repo:
            return {"success": False, "error": "Not a Git repository."}

        try:
            full_command = ["git", "-C", self.repo_path] + command
            result = subprocess.run(
                full_command,
                check=True,
                capture_output=True,
                text=True,
                timeout=30 # Prevent long-running processes
            )
            return {
                'success': True,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        except subprocess.CalledProcessError as e:
            error_message = e.stderr.strip() or e.stdout.strip()
            return {
                'success': False,
                'error': f"Git command failed: {error_message}"
            }
        except FileNotFoundError:
            return {'success': False, 'error': 'Git command not found. Is Git installed and in your PATH?'}
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Git command timed out.'}

    def _check_if_git_repo(self) -> bool:
        """Checks if the given path is a Git repository."""
        result = self._execute_git_command(["rev-parse", "--is-inside-work-tree"])
        return result.get('success') and "true" in result.get('stdout', '').strip().lower()

    def init_repo(self) -> Dict[str, Any]:
        """Initializes a new Git repository."""
        if self._is_git_repo:
            return {"success": False, "error": "Already a Git repository."}
        result = self._execute_git_command(["init"])
        if result['success']:
            self._is_git_repo = True
        return result

    def status(self) -> Dict[str, Any]:
        """Shows the status of the repository."""
        return self._execute_git_command(["status"])

    def add(self, files: List[str]) -> Dict[str, Any]:
        """Adds files to the staging area."""
        return self._execute_git_command(["add"] + files)

    def commit(self, message: str) -> Dict[str, Any]:
        """Commits changes with a message."""
        return self._execute_git_command(["commit", "-m", message])

    def push(self, remote: str = "origin", branch: str = "main") -> Dict[str, Any]:
        """Pushes committed changes to a remote repository."""
        return self._execute_git_command(["push", remote, branch])

