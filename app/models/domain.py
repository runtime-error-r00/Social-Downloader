from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional

class Provider(Enum):
    YOUTUBE = auto()
    INSTAGRAM = auto()
    TIKTOK = auto()
    X = auto()
    UNKNOWN = auto()

@dataclass
class FormatOption:
    format_id: str
    resolution: str
    ext: str
    filesize_approx: int
    has_video: bool
    has_audio: bool

@dataclass
class VideoMetadata:
    url: str
    title: str
    duration: int
    thumbnail_url: str  # Ensure this is spelled correctly with an 'm'
    provider: Provider
    uploader: str
    available_formats: List[FormatOption]

@dataclass
class DownloadProgress:
    status: str
    percentage: float
    speed_str: str
    eta_str: str
    error_message: Optional[str] = None