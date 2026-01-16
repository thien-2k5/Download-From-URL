from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import yt_dlp
import threading
import os
import webbrowser
import socket
import time
import re

app = Flask(__name__)
app.config["SECRET_KEY"] = "youtube-downloader-secret-2026"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# ================== SETUP ==================
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ================== ENCODING HELPER ==================
def safe_print(message):
    """
    Safely print messages with Unicode characters across all platforms
    """
    try:
        print(message)
    except UnicodeEncodeError:
        # Fallback to ASCII-safe printing
        try:
            print(message.encode('ascii', 'ignore').decode('ascii'))
        except:
            print("[Message contains special characters]")

# ================== FFMPEG SETUP ==================
# Add FFmpeg to PATH if installed via winget on Windows
import glob
if os.name == 'nt':  # Windows only
    winget_path = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WinGet", "Packages")
    if os.path.exists(winget_path):
        ffmpeg_dirs = glob.glob(os.path.join(winget_path, "Gyan.FFmpeg*", "ffmpeg-*", "bin"))
        if ffmpeg_dirs:
            os.environ["PATH"] = ffmpeg_dirs[0] + os.pathsep + os.environ.get("PATH", "")
            safe_print(f"[FFmpeg] Added to PATH: {ffmpeg_dirs[0]}")
# For Mac/Linux, FFmpeg should be in system PATH after 'brew install ffmpeg' or 'apt install ffmpeg'

# ================== ROUTES ==================
@app.route("/")
def index():
    return render_template("index.html")

# ================== SOCKET ==================
@socketio.on("connect")
def handle_connect():
    print("Client connected")
    emit("connected", {"status": "ready"})

@socketio.on("disconnect")
def handle_disconnect():
    print("Client disconnected")

@socketio.on("start_download")
def start_download(data):
    safe_print(f"\n[EVENT] Received start_download")
    safe_print(f"[DATA] {data}")
    
    url = data.get("url", "").strip()
    fmt = data.get("format", "auto")
    
    safe_print(f"[URL] {url}")
    safe_print(f"[FORMAT] {fmt}\n")
    
    if not url:
        socketio.emit("error", {"msg": "Vui lòng nhập URL!"})
        return
    
    # Emit starting status
    socketio.emit("status", {"msg": "Đang phân tích video...", "percent": "0%"})
    
    # Track download progress for multiple files (video + audio)
    download_info = {
        'current_file': 1,
        'total_files': 2,  # Usually video + audio
        'file_progress': {}
    }
    
    def progress_hook(d):
        try:
            status = d.get("status")
            
            if status == "downloading":
                # Extract progress information
                downloaded_bytes = d.get("downloaded_bytes", 0)
                total_bytes = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
                
                # Calculate percentage
                if total_bytes > 0:
                    file_percent = (downloaded_bytes / total_bytes) * 100
                    
                    # Get filename to track which file is downloading
                    filename = d.get("filename", "")
                    
                    # Store progress for this file
                    download_info['file_progress'][filename] = file_percent
                    
                    # Calculate overall progress if downloading multiple files
                    if len(download_info['file_progress']) > 0:
                        avg_progress = sum(download_info['file_progress'].values()) / download_info['total_files']
                        overall_percent = min(avg_progress, 100)
                    else:
                        overall_percent = file_percent
                    
                    # Emit progress update
                    socketio.emit("progress", {
                        "percent": f"{overall_percent:.1f}%",
                        "status": "downloading"
                    })
                    
                    safe_print(f"[Progress] {overall_percent:.1f}%")
                
            elif status == "finished":
                filename = d.get("filename", "")
                file_path = d.get("filename", "")
                download_info['file_progress'][file_path] = 100
                
                socketio.emit("progress", {
                    "percent": "100%",
                    "status": "processing",
                    "msg": "Đang xử lý video..."
                })
                
                safe_print(f"[Finished] {filename}")
                
        except Exception as e:
            safe_print(f"Progress hook error: {e}")

    # ================== FORMAT OPTIONS ==================
    if fmt == "mp3":
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "320"
            }],
            "progress_hooks": [progress_hook],
            "noplaylist": True,
            "quiet": False,
            "no_warnings": False,
            "noprogress": False,
        }
        download_info['total_files'] = 1  # Only audio
        
    elif fmt == "mp4":
        ydl_opts = {
            "format": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
            "merge_output_format": "mp4",
            "outtmpl": f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
            "progress_hooks": [progress_hook],
            "noplaylist": True,
            "quiet": False,
            "no_warnings": False,
            "noprogress": False,
        }
        
    else:  # auto
        ydl_opts = {
            "format": "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
            "merge_output_format": "mp4",
            "outtmpl": f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
            "progress_hooks": [progress_hook],
            "noplaylist": True,
            "quiet": False,
            "no_warnings": False,
            "noprogress": False,
        }

    def run_download():
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Get video info first
                socketio.emit("status", {"msg": "Đang lấy thông tin video...", "percent": "0%"})
                
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Unknown')
                duration = info.get('duration', 0)
                
                # Format duration
                duration_str = f"{duration // 60}:{duration % 60:02d}" if duration else "N/A"
                
                socketio.emit("info", {
                    "title": title,
                    "duration": duration_str,
                    "msg": f"Bắt đầu tải: {title}"
                })
                
                safe_print(f"\n{'='*60}")
                safe_print(f"Downloading: {title}")
                safe_print(f"{'='*60}\n")
                
                # Start download
                socketio.emit("status", {"msg": "Đang tải xuống...", "percent": "0%"})
                ydl.download([url])
                
            # Success
            socketio.emit("done", {
                "msg": "✅ Tải hoàn tất! File đã được lưu vào thư mục 'downloads'",
                "percent": "100%"
            })
            
            safe_print(f"\n{'='*60}")
            safe_print(f"Completed: {title}")
            safe_print(f"Saved to: {os.path.abspath(DOWNLOAD_DIR)}")
            safe_print(f"{'='*60}\n")
            
        except Exception as e:
            error_msg = str(e)
            
            # Simplify common error messages
            if "Video unavailable" in error_msg:
                error_msg = "Video không khả dụng hoặc đã bị xóa"
            elif "Private video" in error_msg:
                error_msg = "Video ở chế độ riêng tư"
            elif "Sign in" in error_msg:
                error_msg = "Video yêu cầu đăng nhập"
            elif "HTTP Error 403" in error_msg:
                error_msg = "Không có quyền truy cập video này"
            elif "HTTP Error 404" in error_msg:
                error_msg = "Không tìm thấy video"
            
            socketio.emit("error", {"msg": f"Loi: {error_msg}"})
            safe_print(f"\nError: {error_msg}\n")

    # Run in separate thread
    threading.Thread(target=run_download, daemon=True).start()

# ================== AUTO OPEN BROWSER ==================
def open_browser(port):
    """
    Open browser in a cross-platform way
    """
    time.sleep(1.5)
    url = f"http://127.0.0.1:{port}"
    try:
        webbrowser.open(url)
        safe_print(f"[Browser] Opened {url}")
    except Exception as e:
        safe_print(f"[Browser] Could not open automatically. Please visit: {url}")
        safe_print(f"[Browser] Error: {e}")

# ================== MAIN ==================
if __name__ == "__main__":
    port = 5000
    
    # Find available port (important for macOS where port 5000 may be used by AirPlay)
    while True:
        try:
            sock = socket.socket()
            sock.bind(("127.0.0.1", port))
            sock.close()
            break
        except OSError:
            port += 1
            if port > 5010:  # Safety limit
                print("Error: Cannot find available port!")
                exit(1)
    
    safe_print(f"\n{'='*50}")
    safe_print(f"Server running at: http://127.0.0.1:{port}")
    safe_print(f"Download directory: {os.path.abspath(DOWNLOAD_DIR)}")
    safe_print(f"{'='*50}\n")
    
    # Open browser automatically
    threading.Timer(0.5, open_browser, args=(port,)).start()
    
    # Run server with threading
    socketio.run(app, host="127.0.0.1", port=port, debug=False, allow_unsafe_werkzeug=True)