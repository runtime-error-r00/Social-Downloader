import re
from app.models.domain import Provider

class ProviderDetector:
    PATTERNS = {
        Provider.YOUTUBE: re.compile(r'(?:https?://)?(?:www\.)?(?:youtube\.com|youtu\.be)/.+'),
        Provider.INSTAGRAM: re.compile(r'(?:https?://)?(?:www\.)?instagram\.com/.+'),
        Provider.TIKTOK: re.compile(r'(?:https?://)?(?:www\.)?(?:tiktok\.com|vm\.tiktok\.com)/.+'),
        Provider.X: re.compile(r'(?:https?://)?(?:www\.)?(?:twitter\.com|x\.com)/.+')
    }

    @classmethod
    def detect(cls, url:str) -> Provider:
        for provider, pattern in cls.PATTERNS.items():
            if pattern.match(url):
                return provider
        return Provider.UNKNOWN