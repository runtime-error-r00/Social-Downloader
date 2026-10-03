from PySide6.QtCore import QThread, Signal
from app.core.downloader import DownloadEngine
from app.models.domain import VideoMetadata, DownloadProgress

class AnalyzeWorker(QThread):
    """Runs the URL analysis in a background thread to prevent UI freezing."""
    finished_signal = Signal(VideoMetadata)
    error_signal = Signal(str)

    def __init__(self, url: str):
        super().__init__()
        self.url = url
        self.engine = DownloadEngine()

    def run(self):
        try:
            metadata = self.engine.analyze(self.url)
            self.finished_signal.emit(metadata)
        except Exception as e:
            self.error_signal.emit(str(e))


class DownloadWorker(QThread):
    """Runs the video download in a background thread and emits progress."""
    progress_signal = Signal(DownloadProgress)
    finished_signal = Signal(bool)

    def __init__(self, url: str, format_id: str, output_dir: str):
        super().__init__()
        self.url = url
        self.format_id = format_id
        self.output_dir = output_dir
        self.engine = DownloadEngine()

    def run(self):
        # We define a callback to catch the engine's progress and emit it to the GUI
        def progress_callback(progress: DownloadProgress):
            self.progress_signal.emit(progress)
            
        success = self.engine.download(self.url, self.format_id, self.output_dir, progress_callback)
        self.finished_signal.emit(success)