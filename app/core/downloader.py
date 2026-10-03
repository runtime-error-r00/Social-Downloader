import os
import sys
import yt_dlp
from app.models.domain import VideoMetadata, FormatOption, DownloadProgress

class DownloadEngine:
    def analyze(self, url: str) -> VideoMetadata:
        """Extracts metadata from the URL without downloading the video."""
        ydl_opts = {
            'extract_flat': False,
            'download': False,
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            # Manteniamo solo il trucco per bypassare i limiti di velocità di YouTube
            'extractor_args': {'youtube': ['player_client=android,web']}
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        formats_dict = {}
        
        # Logica flessibile per gestire i formati strani di Twitter e Instagram
        for f in info.get('formats', []):
            vcodec = f.get('vcodec')
            acodec = f.get('acodec')
            ext = f.get('ext', 'mp4')
            
            is_audio_only = (vcodec == 'none')
            is_video_only = (acodec == 'none')
            
            if is_audio_only and is_video_only:
                continue 

            height = f.get('height')
            format_id = f.get('format_id', 'best')
            
            if is_audio_only:
                res_key = "Audio Only"
                download_expr = format_id
            elif height:
                res_key = f"{height}p"
                download_expr = f"{format_id}+bestaudio/best" if is_video_only else format_id
            else:
                # Fallback se la piattaforma non fornisce l'altezza esatta
                res_str = str(f.get('resolution', ''))
                if 'x' in res_str:
                    try:
                        h = res_str.split('x')[1]
                        res_key = f"{h}p"
                    except:
                        res_key = "Standard"
                else:
                    res_key = "Standard"
                    
                download_expr = format_id

            fmt = FormatOption(
                format_id=download_expr, 
                resolution=res_key,
                ext=ext,
                filesize_approx=f.get('filesize') or f.get('filesize_approx') or 0,
                has_video=not is_audio_only,
                has_audio=not is_video_only
            )
            formats_dict[res_key] = fmt

        ordered_keys = [
            "Audio Only", "144p", "240p", "360p", "480p", 
            "720p", "1080p", "1440p", "2160p", "Standard"
        ]
        
        parsed_formats = [formats_dict[k] for k in ordered_keys if k in formats_dict]
        
        # L'opzione 'Auto' è vitale per scaricare da Twitter e Instagram senza errori
        best_fmt = FormatOption(
            format_id="best",
            resolution="Best Quality (Auto)",
            ext="mp4",
            filesize_approx=0,
            has_video=True,
            has_audio=True
        )
        parsed_formats.insert(0, best_fmt) 

        class DynamicProvider:
            def __init__(self, name):
                self.name = name.upper()

        extractor_name = info.get('extractor', 'UNKNOWN')
        provider = DynamicProvider(extractor_name)

        raw_duration = info.get('duration')
        safe_duration = int(raw_duration) if raw_duration else 0

        return VideoMetadata(
            url=url,
            title=info.get('title', 'Unknown Title'),
            duration=safe_duration,
            thumbnail_url=info.get('thumbnail', ''),
            provider=provider,
            uploader=info.get('uploader', 'Unknown Uploader'),
            available_formats=parsed_formats
        )

    def download(self, url: str, format_id: str, output_dir: str, progress_callback) -> bool:
        def yt_dlp_hook(d):
            if d['status'] == 'downloading':
                total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                downloaded_bytes = d.get('downloaded_bytes', 0)
                percentage = (downloaded_bytes / total_bytes * 100) if total_bytes > 0 else 0
                speed = d.get('speed', 0)
                eta = d.get('eta', 0)
                
                speed_mb = speed / 1024 / 1024 if speed else 0
                speed_str = f"{speed_mb:.2f} MB/s"
                eta_str = f"{eta}s" if eta else "Unknown"

                progress = DownloadProgress(
                    status="downloading",
                    percentage=percentage,
                    speed_str=speed_str,
                    eta_str=eta_str
                )
                progress_callback(progress)

        if getattr(sys, 'frozen', False):
            project_root = sys._MEIPASS
        else:
            current_file_path = os.path.abspath(__file__)
            core_dir = os.path.dirname(current_file_path)
            app_dir = os.path.dirname(core_dir)
            project_root = os.path.dirname(app_dir)

        ffmpeg_absolute_path = os.path.join(project_root, 'bin')

        ydl_opts = {
            'format': format_id,
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'), 
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            'progress_hooks': [yt_dlp_hook],
            'extractor_args': {'youtube': ['player_client=android,web']},
            'merge_output_format': 'mp4',
            'ffmpeg_location': ffmpeg_absolute_path,
            'restrictfilenames': True 
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            return True
        except Exception as e:
            progress_callback(DownloadProgress(status="error", error_message=str(e)))
            return False