import os
import subprocess
from typing import List, Dict, Any

class VCS:
    """
    A high-level wrapper for Version Control System operations.

    This class provides a unified interface for interacting with different VCS,
    with a primary focus on Git. It uses subprocesses to execute Git commands,
    allowing it to work without requiring a specific Python Git library.
    """

    def __init__(self, repo_path: str):
        """
        Initializes the VCS handler for a specific repository path.

        Args:
            repo_path (str): The path to the local Git repository.
        """
        self.repo_path = os.path.abspath(repo_path)

    def _run_git_command(self, command: List[str]) -> str:
        """
        Runs a Git command using subprocess and returns the output.

        Args:
            command (List[str]): A list of strings representing the Git command and its arguments.

        Returns:
            str: The stdout of the command.

        Raises:
            subprocess.CalledProcessError: If the command returns a non-zero exit code.
        """
        full_command = ['git'] + command
        try:
            result = subprocess.run(
                full_command,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except FileNotFoundError:
            raise RuntimeError("Git is not installed or not in the system's PATH.")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Git command failed: {e.stderr.strip()}")

    def init(self) -> str:
        """
        Initializes a new Git repository in the specified directory.

        Returns:
            str: The output of the `git init` command.
        """
        if os.path.exists(os.path.join(self.repo_path, '.git')):
            return "Git repository already initialized."
        return self._run_git_command(['init'])

    def add(self, files: List[str] = ['.']) -> str:
        """
        Adds specified files to the staging area.

        Args:
            files (List[str]): A list of file paths to add. Defaults to all files ('.').

        Returns:
            str: The output of the `git add` command.
        """
        return self._run_git_command(['add'] + files)

    def commit(self, message: str) -> str:
        """
        Commits the staged changes with a given message.

        Args:
            message (str): The commit message.

        Returns:
            str: The output of the `git commit` command.
        """
        if not message:
            raise ValueError("Commit message cannot be empty.")
        return self._run_git_command(['commit', '-m', message])

    def status(self) -> str:
        """
        Returns the status of the working tree.

        Returns:
            str: The output of the `git status` command.
        """
        return self._run_git_command(['status'])

    def get_log(self, max_count: int = 5) -> List[Dict[str, str]]:
        """
        Retrieves a list of recent commit logs.

        Args:
            max_count (int): The maximum number of log entries to retrieve.

        Returns:
            List[Dict[str, str]]: A list of dictionaries, where each dictionary
                                  represents a commit and contains keys like 'hash',
                                  'author', 'date', and 'message'.
        """
        log_format = '%H%n%an%n%ad%n%s'
        log_output = self._run_git_command(['log', f'--max-count={max_count}', f'--format={log_format}'])

        commits = []
        if not log_output:
            return commits

        entries = log_output.split('\n\n')
        for entry in entries:
            lines = entry.strip().split('\n')
            if len(lines) == 4:
                commit = {
                    'hash': lines[0],
                    'author': lines[1],
                    'date': lines[2],
                    'message': lines[3]
                }
                commits.append(commit)
        return commits

# This section demonstrates how the VCS class can be used.
if __name__ == '__main__':
    # Create a temporary project directory for testing
    test_repo_path = 'devos_vcs_test_project'
    if os.path.exists(test_repo_path):
        import shutil
        shutil.rmtree(test_repo_path)
    os.makedirs(test_repo_path, exist_ok=True)

    try:
        # Initialize the VCS
        print("--- Initializing a new Git repository ---")
        vcs = VCS(test_repo_path)
        print(vcs.init())

        # Create some files
        with open(os.path.join(test_repo_path, 'README.md'), 'w') as f:
            f.write("# My Awesome Project\n")
        with open(os.path.join(test_repo_path, 'main.c'), 'w') as f:
            f.write("// My C code\n")

        # Add and commit the files
        print("\n--- Adding files and making first commit ---")
        print(vcs.add())
        print(vcs.commit("Initial commit"))

        # Check the status
        print("\n--- Checking repository status ---")
        print(vcs.status())

        # Modify a file and commit again
        with open(os.path.join(test_repo_path, 'README.md'), 'a') as f:
            f.write("\n\n- Added a new feature.")

        print("\n--- Adding modified file and making second commit ---")
        print(vcs.add(['README.md']))
        print(vcs.commit("Update README with new feature"))

        # Get the commit log
        print("\n--- Retrieving the commit log ---")
        logs = vcs.get_log(max_count=2)
        for log in logs:
            print(f"Commit: {log['hash'][:7]}")
            print(f"Author: {log['author']}")
            print(f"Date:   {log['date']}")
            print(f"Message: {log['message']}\n")

    finally:
        # Clean up the temporary directory
        if os.path.exists(test_repo_path):
            import shutil
            shutil.rmtree(test_repo_path)
            print("Cleaned up test repository.")
