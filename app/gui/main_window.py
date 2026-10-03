import os
from pathlib import Path
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QLineEdit, QPushButton, QLabel, QComboBox, QProgressBar, 
                               QGroupBox, QFileDialog, QMessageBox)
from PySide6.QtCore import Qt
from app.gui.workers import AnalyzeWorker, DownloadWorker
from app.models.domain import DownloadProgress

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Downloader")
        self.setMinimumSize(600, 450)
        
        # Application state
        self.current_metadata = None
        self.download_dir = str(Path.home() / "Downloads")
        
        # Thread references
        self.analyze_worker = None
        self.download_worker = None

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 1. URL Input Section
        url_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste video URL here (e.g., YouTube, TikTok, Instagram)...")
        self.url_input.setMinimumHeight(30)
        self.analyze_btn = QPushButton("Analyze")
        self.analyze_btn.setMinimumHeight(30)
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.analyze_btn)
        main_layout.addLayout(url_layout)

        # 2. Metadata Section
        meta_group = QGroupBox("Video Information")
        meta_group.setMinimumHeight(120)
        meta_layout = QVBoxLayout(meta_group)
        
        top_meta_layout = QHBoxLayout()
        self.provider_label = QLabel("Provider: waiting...")
        self.duration_label = QLabel("Duration: waiting...")
        
        top_meta_layout.addWidget(self.provider_label)
        top_meta_layout.addStretch()
        top_meta_layout.addWidget(self.duration_label)
        
        self.title_label = QLabel("Title: waiting...")
        self.title_label.setWordWrap(True)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 11pt; color: #a6e3a1; padding-top: 5px;")
        
        meta_layout.addLayout(top_meta_layout)
        meta_layout.addWidget(self.title_label, stretch=1)
        
        main_layout.addWidget(meta_group)

        # 3. Options Section (Quality and Destination)
        options_group = QGroupBox("Download Options")
        options_layout = QHBoxLayout(options_group)
        
        self.format_combo = QComboBox()
        self.format_combo.addItem("Analyze a video first...")
        self.format_combo.setEnabled(False)
        self.format_combo.setMinimumHeight(30)
        
        self.folder_btn = QPushButton("Choose Destination Folder...")
        self.folder_btn.setMinimumHeight(30)
        self.folder_label = QLabel(f"Save to: {self.download_dir}")
        self.folder_label.setStyleSheet("color: gray; font-size: 11px;")
        
        options_layout.addWidget(QLabel("Quality:"))
        options_layout.addWidget(self.format_combo, stretch=1)
        options_layout.addWidget(self.folder_btn)
        
        main_layout.addWidget(options_group)
        main_layout.addWidget(self.folder_label)

        main_layout.addStretch()

        # 4. Download and Progress Section
        self.status_label = QLabel("Ready.")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        
        self.download_btn = QPushButton("Download Video")
        self.download_btn.setObjectName("download_btn")
        self.download_btn.setEnabled(False)
        self.download_btn.setMinimumHeight(40)
        self.download_btn.setStyleSheet("font-weight: bold; font-size: 14px;")

        main_layout.addWidget(self.status_label)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.download_btn)

    def _connect_signals(self):
        """Connect UI buttons to their respective functions."""
        self.analyze_btn.clicked.connect(self.start_analysis)
        self.folder_btn.clicked.connect(self.choose_folder)
        self.download_btn.clicked.connect(self.start_download)

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Download Directory", self.download_dir)
        if folder:
            self.download_dir = folder
            self.folder_label.setText(f"Save to: {self.download_dir}")

    def start_analysis(self):
        url = self.url_input.text().strip()
        if not url:
            return

        self.download_btn.setText("Download Video")
        self.analyze_btn.setEnabled(False)
        self.download_btn.setEnabled(False)
        self.status_label.setText("Analyzing URL...")
        
        # Clear previous metadata
        self.provider_label.setText("Provider: waiting...")
        self.title_label.setText("Title: waiting...")
        self.duration_label.setText("Duration: waiting...")
        self.format_combo.clear()

        # Start the background worker
        self.analyze_worker = AnalyzeWorker(url)
        self.analyze_worker.finished_signal.connect(self.on_analysis_finished)
        self.analyze_worker.error_signal.connect(self.on_analysis_error)
        self.analyze_worker.start()

    def on_analysis_finished(self, metadata):
        self.current_metadata = metadata
        self.analyze_btn.setEnabled(True)
        self.status_label.setText("Analysis complete. Ready to download.")

        # Update UI with metadata
        self.provider_label.setText(f"Provider: {metadata.provider.name}")
        self.title_label.setText(f"Title: {metadata.title}")
        
        minutes, seconds = divmod(metadata.duration, 60)
        self.duration_label.setText(f"Duration: {minutes}:{seconds:02d}")

        # Populate the combo box
        self.format_combo.setEnabled(True)
        for fmt in metadata.available_formats:
            # Show resolution and extension, e.g., "1080p (mp4)"
            self.format_combo.addItem(f"{fmt.resolution} ({fmt.ext})", userData=fmt.format_id)

        self.download_btn.setEnabled(True)

    def on_analysis_error(self, error_msg):
        self.analyze_btn.setEnabled(True)
        self.status_label.setText("Error analyzing URL.")
        QMessageBox.critical(self, "Error", f"Failed to analyze URL:\n{error_msg}")

    def start_download(self):
        if self.download_btn.text() == "Download a new link":
            self.url_input.clear()
            self.url_input.setFocus()
            self.download_btn.setText("Download Video")
            self.download_btn.setEnabled(False)
            self.progress_bar.setValue(0)
            self.status_label.setText("Ready.")
            self.provider_label.setText("Provider: waiting...")
            self.title_label.setText("Title: waiting...")
            self.duration_label.setText("Duration: waiting...")
            self.format_combo.clear()
            self.format_combo.addItem("Analyze a video first...")
            self.format_combo.setEnabled(False)
            self.current_metadata = None
            return

        if not self.current_metadata:
            return

        url = self.current_metadata.url
        format_id = self.format_combo.currentData() 

        self.analyze_btn.setEnabled(False)
        self.download_btn.setEnabled(False)
        self.format_combo.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Starting download...")

        # Start the background worker
        self.download_worker = DownloadWorker(url, format_id, self.download_dir)
        self.download_worker.progress_signal.connect(self.update_progress)
        self.download_worker.finished_signal.connect(self.on_download_finished)
        self.download_worker.start()

    def update_progress(self, progress: DownloadProgress):
        if progress.status == "downloading":
            self.progress_bar.setValue(int(progress.percentage))
            self.status_label.setText(f"Downloading... {progress.speed_str} (ETA: {progress.eta_str})")
        elif progress.status == "error":
            self.status_label.setText("Download error.")
            QMessageBox.critical(self, "Download Error", f"An error occurred:\n{progress.error_message}")

    def on_download_finished(self, success):
        self.analyze_btn.setEnabled(True)
        self.download_btn.setEnabled(True)
        self.format_combo.setEnabled(True)
        
        if success:
            self.progress_bar.setValue(100)
            self.status_label.setText("Download completed successfully!")
            self.download_btn.setText("Download a new link")
            QMessageBox.information(self, "Success", "Video downloaded successfully!")