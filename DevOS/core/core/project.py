import os
import json
import time
from typing import Dict, Any

class Project:
    """
    Manages the structure, configuration, and state of a single development project.

    This class handles the creation, loading, and saving of project metadata.
    """

    def __init__(self, name: str, base_path: str):
        """
        Initializes a new Project instance.

        Args:
            name (str): The name of the project.
            base_path (str): The base directory where the project will be created or loaded from.
        """
        self.name = name
        self.base_path = base_path
        self.path = os.path.join(base_path, name)
        self.config_file = os.path.join(self.path, '.devos_project.json')
        self.metadata = {}

    def create(self, template: str = 'basic'):
        """
        Creates a new project directory and a configuration file.

        Args:
            template (str): The name of the project template to use.
                            Currently, only 'basic' is supported.
        """
        try:
            # Create the main project directory if it doesn't exist
            os.makedirs(self.path, exist_ok=True)

            # Define and create a basic file structure
            file_structure = {
                'basic': ['src/', 'docs/', '.gitignore']
            }

            for item in file_structure.get(template, []):
                full_path = os.path.join(self.path, item)
                if item.endswith('/'):
                    os.makedirs(full_path, exist_ok=True)
                else:
                    with open(full_path, 'w') as f:
                        f.write(f"# This is the {item} for the {self.name} project\n")

            # Create the project metadata file
            self.metadata = {
                'name': self.name,
                'created_at': time.time(),
                'version': '0.1.0',
                'description': f"A new DevOS project: {self.name}",
                'template': template,
                'status': 'active'
            }

            self.save()
            print(f"Successfully created new project '{self.name}' at {self.path} from '{template}' template.")

        except OSError as e:
            print(f"Error creating project '{self.name}': {e}")
            raise

    def load(self) -> bool:
        """
        Loads an existing project from its configuration file.

        Returns:
            bool: True if the project was loaded successfully, False otherwise.
        """
        if not os.path.exists(self.config_file):
            print(f"Error: Project configuration file not found at {self.config_file}")
            return False

        try:
            with open(self.config_file, 'r') as f:
                self.metadata = json.load(f)

            # Verify the loaded project name matches
            if self.metadata.get('name') != self.name:
                print(f"Warning: Loaded project name '{self.metadata.get('name')}' "
                      f"does not match expected name '{self.name}'.")

            print(f"Successfully loaded project '{self.name}'.")
            return True

        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading project file: {e}")
            return False

    def save(self):
        """
        Saves the current project's metadata to its configuration file.
        """
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.metadata, f, indent=4)
            print(f"Project '{self.name}' metadata saved.")
        except IOError as e:
            print(f"Error saving project metadata: {e}")
            raise

    def get_info(self) -> Dict[str, Any]:
        """
        Returns the project's metadata.

        Returns:
            Dict[str, Any]: A dictionary containing the project's metadata.
        """
        return self.metadata

# Example of how to use the Project class
if __name__ == '__main__':
    # Define a base path for testing
    test_base_path = 'devos_projects'
    project_name = 'MyAwesomeOS'

    # Clean up previous test run if it exists
    if os.path.exists(os.path.join(test_base_path, project_name)):
        import shutil
        shutil.rmtree(os.path.join(test_base_path, project_name))

    # Create a new project
    print("--- Creating a new project ---")
    my_project = Project(project_name, test_base_path)
    my_project.create()

    # Modify some metadata
    my_project.metadata['description'] = "An operating system built with DevOS."
    my_project.save()

    # Load the project
    print("\n--- Loading the project ---")
    loaded_project = Project(project_name, test_base_path)
    if loaded_project.load():
        print(f"Project Info: {json.dumps(loaded_project.get_info(), indent=2)}")

    # Clean up after the test run
    print("\n--- Cleaning up test project ---")
    shutil.rmtree(os.path.join(test_base_path, project_name))
    print("Test project deleted.")
