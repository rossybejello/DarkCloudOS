import os
import json
import time
import hashlib
from pathlib import Path
from typing import Any, Dict, Optional

import requests
import openai
import anthropic
from huggingface_hub import InferenceClient
from google.cloud import aiplatform
from google.oauth2 import service_account
import deepseek_sdk  # hypothetical official import
import perplexity  # hypothetical official import

from .utils import EnvManager, VaultManager


class CacheManager:
    """
    Simple file‐based JSON cache for LLM responses.
    Each entry: { key: { ts: <epoch>, result: <any> } }
    """

    def __init__(self, ttl: int = 3600):
        self.ttl = ttl
        cache_dir = Path.home() / ".monacode" / "cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = cache_dir / "llm_cache.json"
        if not self.cache_file.exists():
            self.cache_file.write_text(json.dumps({}))

    def _load(self) -> Dict[str, Any]:
        return json.loads(self.cache_file.read_text())

    def _save(self, data: Dict[str, Any]):
        self.cache_file.write_text(json.dumps(data, indent=2))

    def make_key(self, engine: str, prompt: str, params: Dict[str, Any]) -> str:
        raw = json.dumps({"e": engine, "p": prompt, "k": params}, sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        data = self._load()
        entry = data.get(key)
        if not entry:
            return None
        if time.time() - entry["ts"] > self.ttl:
            # expired
            del data[key]
            self._save(data)
            return None
        return entry["result"]

    def set(self, key: str, result: Any):
        data = self._load()
        data[key] = {"ts": time.time(), "result": result}
        self._save(data)


class LLMManager:
    """
    High‐level interface to multiple LLM backends.
    Reads API keys from EnvManager or VaultManager as needed.
    """

    def __init__(self, default_engine: Optional[str] = None):
        self.env = EnvManager()
        self.vault = VaultManager()
        self.cache = CacheManager(ttl=int(self.env.get("LLM_CACHE_TTL", "3600")))
        self.default_engine = default_engine or self.env.get("LLM_DEFAULT", "openai")

        # Initialize clients
        openai.api_key = self.env.get("OPENAI_API_KEY", "")
        self.anthropic_client = anthropic.Client(self.env.get("ANTHROPIC_API_KEY", ""))
        self.hf_client = InferenceClient(token=self.env.get("HUGGINGFACE_API_TOKEN", ""))
        # Vertex AI
        gcp_key = self.env.get("GCP_SERVICE_ACCOUNT_JSON")
        if gcp_key and Path(gcp_key).exists():
            creds = service_account.Credentials.from_service_account_file(gcp_key)
            aiplatform.init(credentials=creds, project=self.env.get("GOOGLE_PROJECT_ID", ""), location=self.env.get("GOOGLE_LOCATION", "us-central1"))
        # DeepSeek & Perplexity use direct API keys via env
        self.deepseek_key = self.env.get("DEEPSEEK_API_KEY", "")
        self.perplexity_key = self.env.get("PERPLEXITY_API_KEY", "")

    def generate(self,
                 prompt: str,
                 engine: Optional[str] = None,
                 **kwargs) -> Any:
        """
        Main entry: generate text from chosen engine.
        Caches identical calls.
        """
        engine = engine or self.default_engine
        key = self.cache.make_key(engine, prompt, kwargs)
        cached = self.cache.get(key)
        if cached is not None:
            return cached

        fn = getattr(self, f"_gen_{engine}", None)
        if not fn:
            raise ValueError(f"Unsupported LLM engine: {engine}")

        result = fn(prompt, **kwargs)
        self.cache.set(key, result)
        return result

    def _gen_openai(self, prompt: str, model: str = "gpt-3.5-turbo", **opts):
        payload = {"model": model, "messages": [{"role": "user", "content": prompt}], **opts}
        resp = openai.ChatCompletion.create(**payload)
        return resp.choices[0].message.content

    def _gen_anthropic(self, prompt: str, model: str = "claude-2", **opts):
        combined = f"{anthropic.HUMAN_PROMPT} {prompt}{anthropic.AI_PROMPT}"
        resp = self.anthropic_client.completions.create(model=model, prompt=combined, **opts)
        return resp.completion

    def _gen_huggingface(self, prompt: str, model: str = "gpt2", **opts):
        resp = self.hf_client.text_generation(model=model, inputs=prompt, **opts)
        return resp.generated_text

    def _gen_vertex(self, prompt: str, endpoint: Optional[str] = None, model: Optional[str] = None, **opts):
        endpoint = endpoint or self.env.get("GOOGLE_ENDPOINT_ID")
        client = aiplatform.gapic.PredictionServiceClient()
        name = client.endpoint_path(self.env.get("GOOGLE_PROJECT_ID"), self.env.get("GOOGLE_LOCATION"), endpoint)
        payload = {"instances": [{"content": prompt}]}
        response = client.predict(name=name, payload=payload, **opts)
        # assume first prediction text field
        return response.predictions[0].get("content") or response.predictions[0]

    def _gen_deepseek(self, prompt: str, **opts):
        ds = deepseek_sdk.Client(api_key=self.deepseek_key)
        resp = ds.query(prompt, **opts)
        return resp.text

    def _gen_perplexity(self, prompt: str, **opts):
        client = perplexity.Client(self.perplexity_key)
        resp = client.ask(prompt, **opts)
        return resp.answer

    def list_engines(self) -> Dict[str, str]:
        """
        Returns available engine names and brief descriptions.
        """
        return {
            "openai": "OpenAI ChatCompletion",
            "anthropic": "Anthropic Claude",
            "huggingface": "Hugging Face text-generation",
            "vertex": "Google Vertex AI",
            "deepseek": "DeepSeek semantic search LLM",
            "perplexity": "Perplexity.ai conversational search",
        }
