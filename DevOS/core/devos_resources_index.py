# devos_resources_index.py
RESOURCE_MAP = {
    "core_os": {
        "linux": "https://wiki.osdev.org/",
        "windows": "https://learn.microsoft.com/en-us/windows/dev-environment/",
        "macos": "https://developer.apple.com/documentation/"
    },
    "web_dev": {
        "react": "https://react.dev/learn",
        "security": "https://web.dev/secure/"
    },
    "mobile": {
        "react_native": "https://reactnative.dev/docs/security",
        "flutter": "https://flutter.dev/security",
        "kotlin": "https://kotlinlang.org/docs/security.html"
    },
    "security": {
        "owasp": "https://owasp.org/",
        "cryptography": "https://cryptography.io/en/latest/"
    }
}

def get_resource(category, key):
    return RESOURCE_MAP.get(category, {}).get(key, "")