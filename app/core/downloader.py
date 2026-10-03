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

        formats_dict = {}
        
        for f in info.get('formats', []):
            vcodec = f.get('vcodec')
            acodec = f.get('acodec')
            
            # Controlliamo se il formato contiene video, audio, o entrambi
            has_video = (vcodec != 'none' and vcodec is not None)
            has_audio = (acodec != 'none' and acodec is not None)
            
            if not has_video and not has_audio:
                continue # Saltiamo formati strani come immagini o storyboard

            height = f.get('height')
            
            # Determiniamo la categoria del formato
            if not has_video and has_audio:
                res_key = "Audio Only"
                # Per l'audio, diciamo a yt-dlp di scaricare solo questo ID
                download_expr = f.get('format_id')
                ext = f.get('ext', 'm4a') # Spesso l'audio nativo è m4a o webm
            elif height:
                res_key = f"{height}p"
                # Se il video non ha l'audio integrato, creiamo un'espressione
                # che ordini a yt-dlp di scaricare il video + il miglior audio disponibile
                if not has_audio:
                    download_expr = f"{f.get('format_id')}+bestaudio/best"
                else:
                    download_expr = f.get('format_id')
                ext = f.get('ext', 'mp4')
            else:
                res_key = "Standard"
                download_expr = f.get('format_id')
                ext = f.get('ext', 'mp4')

            fmt = FormatOption(
                format_id=download_expr, 
                resolution=res_key,
                ext=ext,
                filesize_approx=f.get('filesize') or f.get('filesize_approx') or 0,
                has_video=has_video,
                has_audio=has_audio
            )
            
            # yt-dlp elenca i formati dal peggiore al migliore.
            # Sovrascrivendo la chiave nel dizionario, teniamo solo il migliore per ogni risoluzione.
            formats_dict[res_key] = fmt

        # Riordiniamo la lista per presentarla all'utente dalla qualità più bassa alla più alta
        ordered_keys = [
            "Audio Only", "144p", "240p", "360p", "480p", 
            "720p", "1080p", "1440p", "2160p", "Standard"
        ]
        
        formats = [formats_dict[k] for k in ordered_keys if k in formats_dict]
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
        """Downloads the video using the specified format expression to the chosen directory."""
        
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

        download_format = 'bestvideo+bestaudio/best' if format_id == 'best' else format_id

        # --- NOVITÀ: Calcoliamo il percorso assoluto esatto della cartella bin ---
        # __file__ è questo file (app/core/downloader.py)
        # Saliamo di tre cartelle per arrivare alla root del progetto, poi aggiungiamo 'bin'
        current_file_path = os.path.abspath(__file__)
        core_dir = os.path.dirname(current_file_path)
        app_dir = os.path.dirname(core_dir)
        project_root = os.path.dirname(app_dir)
        ffmpeg_absolute_path = os.path.join(project_root, 'bin')

        ydl_opts = {
            'format': download_format,
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
            progress_callback(DownloadProgress(status="error", percentage=0, speed_str="", eta_str="", error_message=str(e)))
            return False
