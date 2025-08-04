import os
import json
import yaml
import base64
import getpass
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv, set_key, find_dotenv
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class EnvManager:
    """
    Load, read, write environment variables from a .env file under ~/.monacode/.
    """

    def __init__(self, env_filename: str = ".env"):
        self.home = Path.home() / ".monacode"
        self.home.mkdir(parents=True, exist_ok=True)
        self.env_path = self.home / env_filename
        if not self.env_path.exists():
            # Copy example or create empty
            example = Path(__file__).parents[2] / ".env.example"
            if example.exists():
                self.env_path.write_text(example.read_text())
            else:
                self.env_path.write_text("")
        load_dotenv(dotenv_path=self.env_path)

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Retrieve an environment variable, or default if missing.
        """
        return os.getenv(key, default)

    def set(self, key: str, value: str) -> None:
        """
        Persist an environment variable into the .env file.
        """
        set_key(str(self.env_path), key, value)

    def all(self) -> Dict[str, str]:
        """
        Return all loaded environment variables (only those in .env).
        """
        data = {}
        for line in self.env_path.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                data[k.strip()] = v.strip()
        return data


class ConfigLoader:
    """
    Simple YAML config loader. Looks for config.yml under ~/.monacode/.
    """

    def __init__(self, filename: str = "config.yml"):
        self.home = Path.home() / ".monacode"
        self.filepath = self.home / filename

    def load(self) -> Dict[str, Any]:
        """
        Load YAML into a dict; returns empty dict if missing.
        """
        if not self.filepath.exists():
            return {}
        with open(self.filepath, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def save(self, data: Dict[str, Any]) -> None:
        """
        Overwrite config file with provided dict.
        """
        with open(self.filepath, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f)


class VaultError(Exception):
    pass


class VaultManager:
    """
    Encrypted secret vault using password-derived Fernet key.
    Stores `salt.bin` and `vault.dat` under ~/.monacode/vault/.
    """

    SALT_FILE = "salt.bin"
    DATA_FILE = "vault.dat"
    ITERATIONS = 390_000

    def __init__(self):
        self.home = Path.home() / ".monacode" / "vault"
        self.home.mkdir(parents=True, exist_ok=True)
        self.salt_path = self.home / self.SALT_FILE
        self.data_path = self.home / self.DATA_FILE

    def _derive_key(self, password: bytes, salt: bytes) -> bytes:
        """
        PBKDF2-HMAC-SHA256 derivation; returns base64-encoded 32-byte key.
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=self.ITERATIONS,
        )
        key = kdf.derive(password)
        return base64.urlsafe_b64encode(key)

    def _load_salt(self) -> bytes:
        """
        Create or load a random salt (16 bytes).
        """
        if not self.salt_path.exists():
            salt = os.urandom(16)
            with open(self.salt_path, "wb") as f:
                f.write(salt)
            return salt

        return self.salt_path.read_bytes()

    def _get_fernet(self, password: Optional[str] = None) -> Fernet:
        """
        Build a Fernet instance from password; prompts if none provided.
        """
        pwd = password.encode("utf-8") if password else getpass.getpass("Vault password: ").encode("utf-8")
        salt = self._load_salt()
        key = self._derive_key(pwd, salt)
        return Fernet(key)

    def _load_store(self, fernet: Fernet) -> Dict[str, str]:
        """
        Decrypt and parse JSON store. Returns empty dict if no data file.
        """
        if not self.data_path.exists():
            return {}

        token = self.data_path.read_bytes()
        try:
            plaintext = fernet.decrypt(token)
            return json.loads(plaintext.decode("utf-8"))
        except Exception as e:
            raise VaultError("Failed to decrypt vault: possibly wrong password.") from e

    def _save_store(self, fernet: Fernet, store: Dict[str, str]) -> None:
        """
        Serialize store to JSON, encrypt, and write to disk.
        """
        plaintext = json.dumps(store, indent=2).encode("utf-8")
        token = fernet.encrypt(plaintext)
        with open(self.data_path, "wb") as f:
            f.write(token)

    def add_secret(self, key: str, secret: str, password: Optional[str] = None) -> None:
        """
        Insert or update a secret in the vault.
        """
        fernet = self._get_fernet(password)
        store = self._load_store(fernet)
        store[key] = secret
        self._save_store(fernet, store)
        print(f"Secret '{key}' saved.")

    def get_secret(self, key: str, password: Optional[str] = None) -> str:
        """
        Retrieve a secret by key; raises if missing.
        """
        fernet = self._get_fernet(password)
        store = self._load_store(fernet)
        try:
            return store[key]
        except KeyError:
            raise VaultError(f"Secret '{key}' not found in vault.")

    def list_keys(self, password: Optional[str] = None) -> None:
        """
        Print all stored secret keys.
        """
        fernet = self._get_fernet(password)
        store = self._load_store(fernet)
        for k in store:
            print(k)

