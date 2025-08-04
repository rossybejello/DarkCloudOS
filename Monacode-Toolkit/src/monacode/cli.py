import sys
import json
import click
from pathlib import Path

from .utils import EnvManager, ConfigLoader, VaultManager
from .llm import LLMManager
from .git import GitManager, PluginManager
from .updater import Updater, UpdateError


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(prog_name="monacode", version="0.3.0")
def cli():
    """Monacode Toolkit – AI/LLM-powered code editor, file explorer, terminal, vault & installers."""
    pass


#
# ENVIRONMENT COMMANDS
#
@cli.group()
def env():
    """Manage environment variables in ~/.monacode/.env."""
    pass


@env.command("list")
def env_list():
    """List all variables in .env."""
    mgr = EnvManager()
    for k, v in mgr.all().items():
        click.echo(f"{k}={v}")


@env.command("get")
@click.argument("key")
@click.argument("default", required=False)
def env_get(key, default):
    """Get ENV value (or default)."""
    mgr = EnvManager()
    val = mgr.get(key, default)
    click.echo(val if val is not None else "")


@env.command("set")
@click.argument("key")
@click.argument("value")
def env_set(key, value):
    """Set ENV variable and persist."""
    mgr = EnvManager()
    mgr.set(key, value)
    click.echo(f"Set {key}={value}")


#
# CONFIG COMMANDS
#
@cli.group()
def config():
    """Load/save YAML config in ~/.monacode/config.yml."""
    pass


@config.command("show")
def config_show():
    """Show current config."""
    cfg = ConfigLoader().load()
    click.echo(json.dumps(cfg, indent=2))


@config.command("save")
@click.argument("key")
@click.argument("value")
def config_save(key, value):
    """Save a key/value to config.yml."""
    loader = ConfigLoader()
    data = loader.load()
    data[key] = value
    loader.save(data)
    click.echo(f"Config saved: {key}={value}")


#
# VAULT COMMANDS
#
@cli.group()
def vault():
    """Encrypted vault for storing sensitive secrets."""
    pass


@vault.command("add")
@click.argument("key")
@click.argument("secret", required=False)
@click.option("--password", "-p", help="Vault password (overrides prompt)")
def vault_add(key, secret, password):
    """Add or update secret in vault."""
    vm = VaultManager()
    if secret is None:
        secret = click.prompt("Secret value", hide_input=True)
    vm.add_secret(key, secret, password)


@vault.command("get")
@click.argument("key")
@click.option("--password", "-p", help="Vault password (overrides prompt)")
def vault_get(key, password):
    """Retrieve secret from vault."""
    vm = VaultManager()
    try:
        secret = vm.get_secret(key, password)
        click.echo(secret)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@vault.command("list")
@click.option("--password", "-p", help="Vault password (overrides prompt)")
def vault_list(password):
    """List secret keys."""
    vm = VaultManager()
    try:
        vm.list_keys(password)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


#
# LLM COMMANDS
#
@cli.group()
def llm():
    """Interact with multiple LLM backends."""
    pass


@llm.command("list-engines")
def llm_list_engines():
    """List available LLM engines."""
    lm = LLMManager()
    engines = lm.list_engines()
    for name, desc in engines.items():
        click.echo(f"{name}: {desc}")


@llm.command("generate")
@click.argument("prompt", nargs=-1, required=True)
@click.option("--engine", "-e", help="Engine to use")
@click.option("--output", "-o", type=click.Path(), help="Save output to file")
@click.option("--raw/--no-raw", default=False, help="Print raw JSON response")
@click.option("--param", "-P", multiple=True, type=str,
              help="Extra key=val params passed to LLM (can repeat)")
def llm_generate(prompt, engine, output, raw, param):
    """Generate text from LLM. PROMPT may be multiple words."""
    text = " ".join(prompt)
    extra = {}
    for p in param:
        if "=" in p:
            k, v = p.split("=", 1)
            extra[k] = v
    lm = LLMManager()
    try:
        result = lm.generate(text, engine=engine, **extra)
    except Exception as e:
        click.echo(f"LLM error: {e}", err=True)
        sys.exit(1)

    if raw:
        click.echo(json.dumps({"result": result}, indent=2))
    else:
        click.echo(result)

    if output:
        Path(output).write_text(result)
        click.echo(f"Saved to {output}")


#
# PLUGIN COMMANDS
#
@cli.group()
def plugin():
    """Manage Monacode plugins."""
    pass


@plugin.command("create")
@click.argument("name")
def plugin_create(name):
    """Scaffold a new plugin."""
    pm = PluginManager()
    try:
        pm.generate_plugin_template(name)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@plugin.command("list")
def plugin_list():
    """List installed plugins."""
    pm = PluginManager()
    for name in pm.list_plugins():
        click.echo(name)


@plugin.command("run")
@click.argument("name")
@click.argument("data", required=False)
def plugin_run(name, data):
    """Run a plugin with optional JSON DATA."""
    pm = PluginManager()
    try:
        mod = pm.load_plugin(name)
    except Exception as e:
        click.echo(f"Load error: {e}", err=True)
        sys.exit(1)

    payload = {}
    if data:
        try:
            payload = json.loads(data)
        except json.JSONDecodeError:
            click.echo("DATA must be valid JSON", err=True)
            sys.exit(1)

    try:
        result = mod.run(payload)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Execution error: {e}", err=True)
        sys.exit(1)


#
# GIT COMMANDS
#
@cli.group()
def git():
    """High-level Git operations & repo scaffolding."""
    pass


@git.command("init")
@click.argument("name")
@click.option("--template", "-t", help="Directory to use as template")
def git_init(name, template):
    """Initialize a new Git repository."""
    gm = GitManager()
    try:
        gm.init_repo(name, template)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@git.command("clone")
@click.argument("url")
@click.option("--dest", "-d", help="Destination folder name")
def git_clone(url, dest):
    """Clone a remote repository."""
    gm = GitManager()
    gm.clone_repo(url, dest)


@git.command("commit")
@click.option("--path", "-p", help="Repo path (defaults to cwd)")
@click.option("--message", "-m", default="Update", help="Commit message")
def git_commit(path, message):
    """Stage and commit all changes."""
    gm = GitManager()
    try:
        gm.commit_all(path, message)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@git.command("branch")
@click.option("--path", "-p", help="Repo path (defaults to cwd)")
def git_branch(path):
    """Show current branch."""
    gm = GitManager()
    try:
        branch = gm.current_branch(path)
        click.echo(branch)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


#
# UPDATE COMMANDS
#
@cli.group()
def update():
    """Self-update Monacode Toolkit via PyPI or GitHub."""
    pass


@update.command("pypi")
def update_pypi():
    """Update via PyPI."""
    up = Updater()
    try:
        up.update_via_pypi()
    except Exception as e:
        click.echo(f"Update error: {e}", err=True)
        sys.exit(1)


@update.command("github")
@click.option("--dir", "-d", "target_dir", help="Directory to overwrite (defaults to install path)")
def update_github(target_dir):
    """Update via GitHub Releases."""
    up = Updater()
    try:
        up.update_via_github(target_dir)
    except Exception as e:
        click.echo(f"Update error: {e}", err=True)
        sys.exit(1)


@update.command("auto")
def update_auto():
    """Auto-select update method (env MONACODE_UPDATE_METHOD)."""
    up = Updater()
    try:
        up.choose_update()
    except UpdateError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
