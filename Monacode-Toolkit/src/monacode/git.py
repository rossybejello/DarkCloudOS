import os
import sys
import shutil
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional

from git import Repo, GitCommandError


PLUGIN_INTERFACE_VERSION = "1.0.0"


class GitManager:
    """
    Repository scaffolding and plugin framework utilities.
    """

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = Path(base_dir or os.getcwd())

    def init_repo(self, name: str, template_dir: Optional[str] = None) -> None:
        """
        Initialize a new git repo named `name` under base_dir.
        If template_dir is provided, copy files before git init.
        """
        target = self.base_dir / name
        if target.exists():
            raise FileExistsError(f"Directory '{target}' already exists.")
        target.mkdir(parents=True)
        if template_dir:
            src = Path(template_dir)
            shutil.copytree(src, target, dirs_exist_ok=True)
        Repo.init(str(target))
        print(f"Repository initialized at {target}")

    def clone_repo(self, url: str, dest: Optional[str] = None) -> Repo:
        """
        Clone remote repo URL into dest (or into a folder named after the repo).
        """
        dest_path = self.base_dir / (dest or Path(url).stem)
        try:
            repo = Repo.clone_from(url, str(dest_path))
            print(f"Cloned {url} to {dest_path}")
            return repo
        except GitCommandError as e:
            print(f"Clone failed: {e}")
            sys.exit(1)

    def commit_all(self, repo_path: Optional[str] = None, message: str = "Update") -> None:
        """
        Stage and commit all changes with a given commit message.
        """
        repo = Repo(str(self.base_dir if repo_path is None else Path(repo_path)))
        repo.git.add("--all")
        repo.index.commit(message)
        print(f"Committed all changes in {repo.working_tree_dir}")

    def current_branch(self, repo_path: Optional[str] = None) -> str:
        """
        Return current branch name of the repo.
        """
        repo = Repo(str(self.base_dir if repo_path is None else Path(repo_path)))
        return repo.active_branch.name


class PluginManager:
    """
    Generate, validate, and load plugins conforming to our ABI.
    Each plugin is a folder containing:
      - plugin.py implementing `interface_version` and `run(...)`
      - metadata.json to describe it
    """

    def __init__(self, plugins_dir: Optional[str] = None):
        self.plugins_dir = Path(plugins_dir or (Path.home() / ".monacode" / "plugins"))
        self.plugins_dir.mkdir(parents=True, exist_ok=True)

    def generate_plugin_template(self, name: str) -> None:
        """
        Scaffold a new plugin skeleton under plugins_dir/name/.
        """
        dest = self.plugins_dir / name
        if dest.exists():
            raise FileExistsError(f"Plugin '{name}' already exists.")
        dest.mkdir()
        # Write plugin.py
        plugin_py = dest / "plugin.py"
        plugin_py.write_text(f"""\
INTERFACE_VERSION = "{PLUGIN_INTERFACE_VERSION}"

def run(input_data):
    \"\"\"
    input_data: dict, return any serializable result.
    \"\"\"
    print("Hello from plugin: {name}")
    return {{}}
""")
        # Write metadata.json
        metadata = dest / "metadata.json"
        metadata.write_text(
            '{\n'
            f'  "name": "{name}",\n'
            '  "description": "A Monacode toolkit plugin",\n'
            f'  "interface_version": "{PLUGIN_INTERFACE_VERSION}"\n'
            '}'
        )
        print(f"Plugin template '{name}' created at {dest}")

    def list_plugins(self) -> List[str]:
        """
        Return all plugin folder names in plugins_dir.
        """
        return [p.name for p in self.plugins_dir.iterdir() if p.is_dir()]

    def validate_plugin(self, name: str) -> bool:
        """
        Check plugin metadata and interface version compatibility.
        Returns True if valid, else raises.
        """
        plugin_path = self.plugins_dir / name
        meta_path = plugin_path / "metadata.json"
        if not meta_path.exists():
            raise FileNotFoundError(f"No metadata.json for plugin '{name}'.")
        import json
        meta = json.loads(meta_path.read_text())
        if meta.get("interface_version") != PLUGIN_INTERFACE_VERSION:
            raise RuntimeError(
                f"Plugin '{name}' uses interface {meta.get('interface_version')}, "
                f"requires {PLUGIN_INTERFACE_VERSION}."
            )
        # Check plugin.py defines INTERFACE_VERSION and run()
        module_path = plugin_path / "plugin.py"
        if not module_path.exists():
            raise FileNotFoundError(f"No plugin.py in '{name}'.")
        spec = importlib.util.spec_from_file_location(name, str(module_path))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore
        if getattr(mod, "INTERFACE_VERSION", None) != PLUGIN_INTERFACE_VERSION:
            raise RuntimeError(f"Plugin '{name}' INTERFACE_VERSION mismatch.")
        if not callable(getattr(mod, "run", None)):
            raise RuntimeError(f"Plugin '{name}' has no callable run().")
        return True

    def load_plugin(self, name: str):
        """
        Dynamically import and return the plugin module.
        """
        self.validate_plugin(name)
        path = self.plugins_dir / name / "plugin.py"
        spec = importlib.util.spec_from_file_location(name, str(path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore
        return module
