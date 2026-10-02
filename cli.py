import sys
import os
from pathlib import Path
from app.core.downloader import DownloadEngine
from app.core.provider_detector import ProviderDetector
from app.models.domain import DownloadProgress

def progress_handler(progress: DownloadProgress):
    if progress.status == "downloading":
        sys.stdout.write(f"\rDownloading... {progress.percentage:.1f}% | Speed: {progress.speed_str} | ETA: {progress.eta_str}")
        sys.stdout.flush()
    elif progress.status == "finished":
        print("\n\nDownload completed successfully!")
    elif progress.status == "error":
        print(f"\n\nError during download: {progress.error_message}")

def main():
    print("=== Video Downloader CLI (Phase 1) ===")
    url = input("Paste a video URL: ").strip()

    if not url:
        print("URL cannot be empty.")
        return

    # 1. Detect Provider
    provider = ProviderDetector.detect(url)
    print(f"\n[INFO] Detected Provider: {provider.name}")

    engine = DownloadEngine()

    # 2. Analyze URL
    print("[INFO] Analyzing URL (fetching metadata)...")
    try:
        metadata = engine.analyze(url)
    except Exception as e:
        print(f"[ERROR] Failed to analyze URL: {e}")
        return

    # 3. Display Metadata
    print("\n--- Video Info ---")
    print(f"Title:    {metadata.title}")
    print(f"Uploader: {metadata.uploader}")
    print(f"Duration: {metadata.duration} seconds")
    
    print("\n--- Available Formats ---")
    for i, fmt in enumerate(metadata.available_formats):
        mb_size = fmt.filesize_approx / (1024 * 1024) if fmt.filesize_approx else 0
        video_flag = "V" if fmt.has_video else "-"
        audio_flag = "A" if fmt.has_audio else "-"
        print(f"[{i}] {fmt.resolution} ({fmt.ext}) - {mb_size:.1f} MB [{video_flag}/{audio_flag}] (ID: {fmt.format_id})")

    # 4. User Selection (Format)
    print("\nSelect a format index to download, or type 'best' for default best quality:")
    choice = input("Choice: ").strip()

    if choice.lower() == 'best':
        format_id = 'best' 
    else:
        try:
            idx = int(choice)
            format_id = metadata.available_formats[idx].format_id
        except (ValueError, IndexError):
            print("Invalid selection. Exiting.")
            return

    # 5. User Selection (Folder)
    default_downloads_folder = str(Path.home() / "Downloads")
    print(f"\nWhere do you want to save the video?")
    print(f"Press Enter to use default: {default_downloads_folder}")
    
    user_folder = input("Folder path: ").strip()
    
    # If the user just presses Enter, use the default folder
    output_dir = user_folder if user_folder else default_downloads_folder

    # 6. Download
    print(f"\n[INFO] Starting download (Format: {format_id}) to {output_dir}...")
    engine.download(url, format_id, output_dir, progress_handler)

if __name__ == "__main__":
    main()