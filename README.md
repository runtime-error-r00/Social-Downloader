# Social Downloader

A clean, modern, and open-source desktop application to download videos and audio from various social platforms (YouTube, Instagram, X). 

**The Philosophy:** I was tired of searching for sketchy online downloaders filled with ads, pop-ups, and daily limits just to save a simple video. So, I built my own. It just works.

## Features
* **Universal URL Detection:** Just paste the link. The app automatically detects the provider.
* **Format Selection:** Choose exactly what you want (e.g., 1080p, 720p, or Audio Only).
* **High-Quality Merging:** Automatically merges separated video and audio streams using an embedded FFmpeg build.
* **Modern UI:** Built with PySide6 (Qt) featuring a clean, responsive Dark Mode interface.
* **Standalone:** No need to install Python or mess with the command line. Just run the `.exe`.

## Download & Usage (For Regular Users)
1. Go to the **[Releases](../../releases)** tab on the right side of this GitHub page.
2. Download the latest `SocialDownloader.zip` file for Windows.
3. Extract the folder and run `SocialDownloader.exe`.
4. Paste a link, wait for the analysis, select your quality, and click Download!

## Development Setup (For Developers)
If you want to build the project from source or contribute:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/runtime-error-r00/Social-Downloader.git
   cd social-downloader
   ```

2. **Create a virtual environment & install dependencies:**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Install Local FFmpeg (Required for development):**
   * Download a static Windows build of `ffmpeg.exe` (GPL static).
   * Create a `bin/` directory in the root of the project.
   * Place `ffmpeg.exe` inside the `bin/` folder.

4. **Run the app:**
   ```bash
   python -m app.main
   ```

## Building the .exe
To compile the standalone Windows executable yourself, ensure your virtual environment is active and run:
```bash
pip install pyinstaller
pyinstaller --name "SocialDownloader" --windowed --add-data "bin/ffmpeg.exe;bin" app/main.py
```
The output will be generated in the `dist/` folder.

## Disclaimer / Responsible Use
This application relies on `yt-dlp` for media extraction. It is intended strictly for downloading content that you are legally authorized to download (e.g., your own videos, public domain content, or under fair use). The creator assumes no responsibility for how this tool is used or for any copyright infringements committed by the user. Do not use this software to bypass technical protections or DRM.
