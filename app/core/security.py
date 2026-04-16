import re
import base64
from typing import Tuple
from app.core.config import config

class SecurityGuard:
    def __init__(self):
        # Common patterns for prompt injection and jailbreaking
        self.injection_patterns = [
            r"ignore previous instructions",
            r"ignore all previous rules",
            r"you are now a",
            r"new role:",
            r"disregard all",
            r"system prompt:",
            r"tell me a joke",
            r"DAN",
            r"jailbreak",
            r"act as",
            r"stay in character",
            r"developer mode",
            r"bypass code",
        ]

    def is_injection_attempt(self, text: str) -> bool:
        text_lower = text.lower()
        for pattern in self.injection_patterns:
            if re.search(pattern, text_lower):
                return True
        return False

    def check_query(self, query: str) -> Tuple[bool, str]:
        """
        Returns (is_safe, reason)
        """
        # 1. Direct Scan
        if self.is_injection_attempt(query):
            return False, config.INJECTION_MESSAGE
        
        # 2. Encoded Attack Scan (Detect Base64 patterns)
        # Looking for common Base64 length strings (> 8 chars) that look like encoded text
        b64_matches = re.findall(r'[A-Za-z0-9+/]{8,}=*', query)
        for match in b64_matches:
            try:
                decoded = base64.b64decode(match).decode('utf-8')
                if self.is_injection_attempt(decoded):
                    return False, f"{config.INJECTION_MESSAGE} (Encoded payload match)"
            except Exception:
                continue # Not valid UTF-8 base64, ignore
                
        return True, ""
