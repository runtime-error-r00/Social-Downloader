import os
import yt_dlp
from typing import Callable, Optional
from app.models.domain import VideoMetadata, FormatOption, Provider, DownloadProgress
from app.core.provider_detector import ProviderDetector

class DownloadEngine:
    def analyze(self, url: str) -> VideoMetadata:
        """Extracts metadata from the URL without downloading the video."""
        ydl_opts = {
            'extract_flat': False,
            'download': False,
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            # Bypass YouTube blocks by spoofing the client
            'extractor_args': {'youtube': ['player_client=android,web']}
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        # Parse available formats (filtering for standard usable formats)
        formats = []
        for f in info.get('formats', []):
            if f.get('vcodec') != 'none' or f.get('acodec') != 'none':
                fmt = FormatOption(
                    format_id=f.get('format_id', ''),
                    resolution=f.get('format_note') or f.get('resolution') or 'Audio Only',
                    ext=f.get('ext', ''),
                    filesize_approx=f.get('filesize') or f.get('filesize_approx') or 0,
                    has_video=f.get('vcodec') != 'none',
                    has_audio=f.get('acodec') != 'none'
                )
                formats.append(fmt)

        formats = formats[-5:] # Grab the last 5 (usually the highest quality ones)
        provider = ProviderDetector.detect(url)

        return VideoMetadata(
            url=url,
            title=info.get('title', 'Unknown Title'),
            duration=info.get('duration', 0),
            thumbnail_url=info.get('thumbnail', ''),
            provider=provider,
            uploader=info.get('uploader', 'Unknown Uploader'),
            available_formats=formats
        )

    def download(self, url: str, format_id: str, output_dir: str, progress_callback: Callable[[DownloadProgress], None]) -> bool:
        """Downloads the video using the specified format ID to the chosen directory."""
        
        os.makedirs(output_dir, exist_ok=True)
        
        def yt_dlp_hook(d):
            if d['status'] == 'downloading':
                percentage_str = d.get('_percent_str', '0%').replace('\x1b[0;94m', '').replace('\x1b[0m', '').strip('%')
                try:
                    percentage = float(percentage_str)
                except ValueError:
                    percentage = 0.0

                progress = DownloadProgress(
                    status="downloading",
                    percentage=percentage,
                    speed_str=d.get('_speed_str', 'N/A').replace('\x1b[0;92m', '').replace('\x1b[0m', ''),
                    eta_str=d.get('_eta_str', 'N/A').replace('\x1b[0;93m', '').replace('\x1b[0m', '')
                )
                progress_callback(progress)
            elif d['status'] == 'finished':
                progress_callback(DownloadProgress(status="finished", percentage=100.0, speed_str="0", eta_str="00:00"))

        # Intelligently request audio alongside the requested video format
        if format_id == 'best':
            download_format = 'bestvideo+bestaudio/best'
        else:
            download_format = f"{format_id}+bestaudio/best"

        ydl_opts = {
            'format': download_format,
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'), 
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            'progress_hooks': [yt_dlp_hook],
            # Bypass YouTube blocks by spoofing the client
            'extractor_args': {'youtube': ['player_client=android,web']}
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            return True
        except Exception as e:
            progress_callback(DownloadProgress(status="error", percentage=0, speed_str="", eta_str="", error_message=str(e)))
            return False