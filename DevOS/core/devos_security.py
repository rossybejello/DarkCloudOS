# devos_security.py
SECURITY_RESOURCES = {
    "web": {
        "owasp": "https://owasp.org/www-project-top-ten/",
        "csp": "https://content-security-policy.com/",
        "headers": "https://securityheaders.com/"
    },
    "os": {
        "hardening": "https://github.com/trimstray/linux-hardening-checklist",
        "selinux": "https://selinuxproject.org/",
        "apparmor": "https://apparmor.net/"
    }
}

def generate_security_policy(framework):
    policies = {
        "react": "Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'",
        "flutter": "Permissions-Policy: camera=(), geolocation=()",
        "kotlin": "android:usesCleartextTraffic='false'"
    }
    return policies.get(framework, "")