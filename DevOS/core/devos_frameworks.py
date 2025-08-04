# devos_frameworks.py
FRAMEWORK_RESOURCES = {
    "react": {
        "docs": "https://react.dev/learn",
        "security": "https://react-security.dev/",
        "os_integration": "https://github.com/neutralinojs/neutralinojs-react"
    },
    "flutter": {
        "docs": "https://docs.flutter.dev/",
        "desktop": "https://docs.flutter.dev/desktop",
        "os_embedding": "https://pub.dev/packages/embedder"
    },
    "kotlin": {
        "compose": "https://developer.android.com/jetpack/compose",
        "native": "https://kotlinlang.org/docs/native-overview.html",
        "security": "https://kotlinlang.org/docs/security.html"
    }
}

def get_framework_resources(framework):
    return FRAMEWORK_RESOURCES.get(framework.lower(), {})