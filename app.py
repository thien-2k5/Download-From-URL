from flask import Flask, render_template, jsonify, request, send_file
from flask_socketio import SocketIO, emit
import yt_dlp
import threading
import os
import webbrowser
import socket
import time
import json
from datetime import datetime
import sqlite3
from pathlib import Path
import re
import requests
from urllib.parse import urlparse

app = Flask(__name__)
app.config["SECRET_KEY"] = "youtube-downloader-secret-2026"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# ================== SETUP ==================
DOWNLOAD_DIR = "downloads"
DB_PATH = "downloads.db"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ================== DATABASE SETUP ==================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS downloads
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT,
                  url TEXT,
                  platform TEXT,
                  format TEXT,
                  file_size INTEGER,
                  duration TEXT,
                  filename TEXT,
                  status TEXT,
                  download_date TIMESTAMP,
                  error_msg TEXT)''')
    conn.commit()
    conn.close()

init_db()

# ================== ENCODING HELPER ==================
def safe_print(message):
    try:
        print(message)
    except UnicodeEncodeError:
        try:
            print(message.encode('ascii', 'ignore').decode('ascii'))
        except:
            print("[Message contains special characters]")

# ================== FFMPEG SETUP ==================
import glob
if os.name == 'nt':
    winget_path = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WinGet", "Packages")
    if os.path.exists(winget_path):
        ffmpeg_dirs = glob.glob(os.path.join(winget_path, "Gyan.FFmpeg*", "ffmpeg-*", "bin"))
        if ffmpeg_dirs:
            os.environ["PATH"] = ffmpeg_dirs[0] + os.pathsep + os.environ.get("PATH", "")
            safe_print(f"[FFmpeg] Added to PATH: {ffmpeg_dirs[0]}")

# ================== HELPER FUNCTIONS ==================
def get_file_size(filepath):
    """Get file size in bytes"""
    try:
        return os.path.getsize(filepath)
    except:
        return 0

def format_file_size(bytes):
    """Convert bytes to human readable format"""
    if bytes == 0:
        return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} TB"

def save_to_db(data):
    """Save download record to database"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO downloads 
                 (title, url, platform, format, file_size, duration, filename, status, download_date, error_msg)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (data.get('title'), data.get('url'), data.get('platform'), data.get('format'),
               data.get('file_size'), data.get('duration'),
               data.get('filename'), data.get('status'), datetime.now(), data.get('error_msg')))
    conn.commit()
    conn.close()

def get_platform_icon(platform):
    """Get emoji icon for platform"""
    platform_lower = platform.lower() if platform else ''
    icons = {
        'youtube': '📺',
        'facebook': '📘',
        'instagram': '📷',
        'tiktok': '🎵',
        'twitter': '🐦',
        'x': '✖️',
        'vimeo': '🎬',
        'twitch': '🎮'
    }
    for key, icon in icons.items():
        if key in platform_lower:
            return icon
    return '🌐'

# ================== ROUTES ==================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/history")
def get_history():
    """Get download history"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''SELECT id, title, url, platform, format, file_size, duration, 
                 filename, status, download_date, error_msg 
                 FROM downloads ORDER BY download_date DESC LIMIT 100''')
    
    rows = c.fetchall()
    conn.close()
    
    history = []
    for row in rows:
        history.append({
            'id': row[0],
            'title': row[1],
            'url': row[2],
            'platform': row[3],
            'platform_icon': get_platform_icon(row[3]),
            'format': row[4],
            'file_size': format_file_size(row[5]) if row[5] else 'N/A',
            'duration': row[6],
            'filename': row[7],
            'status': row[8],
            'download_date': row[9],
            'error_msg': row[10]
        })
    
    return jsonify(history)

@app.route("/api/delete/<int:id>", methods=['DELETE'])
def delete_record(id):
    """Delete a download record"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM downloads WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route("/api/clear-history", methods=['POST'])
def clear_history():
    """Clear all download history"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM downloads")
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route("/api/search-history", methods=['GET'])
def search_history():
    """Search in download history"""
    query = request.args.get('q', '').strip()
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''SELECT id, title, url, platform, format, file_size, duration, 
                 filename, status, download_date, error_msg 
                 FROM downloads 
                 WHERE title LIKE ? OR platform LIKE ? OR url LIKE ?
                 ORDER BY download_date DESC LIMIT 50''',
              (f'%{query}%', f'%{query}%', f'%{query}%'))
    
    rows = c.fetchall()
    conn.close()
    
    results = []
    for row in rows:
        results.append({
            'id': row[0],
            'title': row[1],
            'url': row[2],
            'platform': row[3],
            'platform_icon': get_platform_icon(row[3]),
            'format': row[4],
            'file_size': format_file_size(row[5]) if row[5] else 'N/A',
            'duration': row[6],
            'filename': row[7],
            'status': row[8],
            'download_date': row[9],
            'error_msg': row[10]
        })
    
    return jsonify(results)

@app.route("/api/export-history", methods=['GET'])
def export_history():
    """Export history as JSON"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''SELECT title, url, platform, format, file_size, duration, 
                 filename, status, download_date 
                 FROM downloads ORDER BY download_date DESC''')
    
    rows = c.fetchall()
    conn.close()
    
    export_data = []
    for row in rows:
        export_data.append({
            'title': row[0],
            'url': row[1],
            'platform': row[2],
            'format': row[3],
            'file_size': format_file_size(row[4]) if row[4] else 'N/A',
            'duration': row[5],
            'filename': row[6],
            'status': row[7],
            'download_date': row[8]
        })
    
    return jsonify(export_data)

# ================== SOCKET EVENTS ==================
@socketio.on("connect")
def handle_connect():
    print("Client connected")
    emit("connected", {"status": "ready"})

@socketio.on("disconnect")
def handle_disconnect():
    print("Client disconnected")

@socketio.on("get_video_info")
def get_video_info(data):
    """Get video information without downloading"""
    url = data.get("url", "").strip()
    
    if not url:
        socketio.emit("error", {"msg": "Vui lòng nhập URL!"})
        return
    
    def fetch_info():
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'skip_download': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Get available formats
                formats = []
                if 'formats' in info:
                    seen = set()
                    for f in info['formats']:
                        height = f.get('height')
                        if height and height not in seen and height <= 2160:
                            formats.append({
                                'quality': f"{height}p",
                                'ext': f.get('ext', 'mp4'),
                                'filesize': format_file_size(f.get('filesize', 0)) if f.get('filesize') else 'N/A'
                            })
                            seen.add(height)
                
                formats = sorted(formats, key=lambda x: int(x['quality'].replace('p', '')), reverse=True)
                
                duration = info.get('duration', 0)
                if duration:
                    duration_int = int(duration)
                    duration_str = f"{duration_int // 60}:{duration_int % 60:02d}"
                else:
                    duration_str = "N/A"
                
                # Get thumbnail with fallback
                thumbnail = info.get('thumbnail', '')
                if thumbnail:
                    # Try to verify thumbnail is accessible
                    try:
                        response = requests.head(thumbnail, timeout=2)
                        if response.status_code != 200:
                            thumbnail = ''
                    except:
                        thumbnail = ''
                
                video_info = {
                    'title': info.get('title', 'Unknown'),
                    'thumbnail': thumbnail,
                    'duration': duration_str,
                    'uploader': info.get('uploader', 'Unknown'),
                    'view_count': f"{info.get('view_count', 0):,}" if info.get('view_count') else 'N/A',
                    'platform': info.get('extractor', 'Unknown'),
                    'formats': formats[:6]
                }
                
                socketio.emit("video_info", video_info)
                
        except Exception as e:
            safe_print(f"Preview error: {str(e)}")
            socketio.emit("error", {"msg": f"Không thể lấy thông tin: {str(e)}"})
    
    threading.Thread(target=fetch_info, daemon=True).start()

@socketio.on("start_download")
def start_download(data):
    safe_print(f"\n[EVENT] Received start_download")
    safe_print(f"[DATA] {data}")
    
    url = data.get("url", "").strip()
    fmt = data.get("format", "auto")
    quality = data.get("quality", "best")
    
    if not url:
        socketio.emit("error", {"msg": "Vui lòng nhập URL!"})
        return
    
    socketio.emit("status", {"msg": "Đang phân tích video...", "percent": "0%"})
    
    download_info = {
        'current_file': 1,
        'total_files': 2,
        'file_progress': {},
        'start_time': time.time()
    }
    
    db_record = {
        'url': url,
        'format': fmt,
        'status': 'downloading'
    }
    
    def progress_hook(d):
        try:
            status = d.get("status")
            
            if status == "downloading":
                downloaded_bytes = d.get("downloaded_bytes", 0)
                total_bytes = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
                speed = d.get("speed", 0)
                eta = d.get("eta", 0)
                
                if total_bytes > 0:
                    file_percent = (downloaded_bytes / total_bytes) * 100
                    filename = d.get("filename", "")
                    download_info['file_progress'][filename] = file_percent
                    
                    if len(download_info['file_progress']) > 0:
                        avg_progress = sum(download_info['file_progress'].values()) / download_info['total_files']
                        overall_percent = min(avg_progress, 100)
                    else:
                        overall_percent = file_percent
                    
                    socketio.emit("progress", {
                        "percent": f"{overall_percent:.1f}%",
                        "status": "downloading",
                        "speed": f"{format_file_size(speed)}/s" if speed else "N/A",
                        "eta": f"{int(eta)}s" if eta else "N/A",
                        "downloaded": format_file_size(downloaded_bytes),
                        "total": format_file_size(total_bytes)
                    })
                    
            elif status == "finished":
                socketio.emit("progress", {
                    "percent": "100%",
                    "status": "processing",
                    "msg": "Đang xử lý video..."
                })
                
        except Exception as e:
            safe_print(f"Progress hook error: {e}")

    # Common options WITHOUT thumbnail download
    common_opts = {
        "progress_hooks": [progress_hook],
        "noplaylist": True,
        "quiet": False,
        "no_warnings": False,
        "noprogress": False,
        "nocheckcertificate": True,
        "ignoreerrors": False,
        "no_color": True,
        "writethumbnail": False,  # Don't download thumbnail
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "http_headers": {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        }
    }

    if fmt == "mp3":
        ydl_opts = {
            **common_opts,
            "format": "bestaudio/best",
            "outtmpl": f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "320"
            }],
        }
        download_info['total_files'] = 1
        
    elif fmt == "mp4":
        format_string = f"bestvideo[height<={quality.replace('p', '')}][ext=mp4]+bestaudio[ext=m4a]/best[height<={quality.replace('p', '')}]" if quality != "best" else "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best"
        
        ydl_opts = {
            **common_opts,
            "format": format_string,
            "merge_output_format": "mp4",
            "outtmpl": f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
            "postprocessors": [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
        }
    else:
        ydl_opts = {
            **common_opts,
            "format": "best[ext=mp4]/bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
            "outtmpl": f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
            "postprocessors": [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
        }

    def run_download():
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                socketio.emit("status", {"msg": "Đang lấy thông tin video...", "percent": "0%"})
                
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Unknown')
                duration = info.get('duration', 0)
                platform = info.get('extractor', 'Unknown')
                
                if duration:
                    duration_int = int(duration)
                    duration_str = f"{duration_int // 60}:{duration_int % 60:02d}"
                else:
                    duration_str = "N/A"
                
                db_record['title'] = title
                db_record['platform'] = platform
                db_record['duration'] = duration_str
                
                socketio.emit("info", {
                    "title": title,
                    "duration": duration_str,
                    "platform": platform,
                    "msg": f"Bắt đầu tải: {title}"
                })
                
                safe_print(f"\n{'='*60}")
                safe_print(f"Platform: {platform}")
                safe_print(f"Downloading: {title}")
                safe_print(f"{'='*60}\n")
                
                socketio.emit("status", {"msg": "Đang tải xuống...", "percent": "0%"})
                result = ydl.download([url])
                
                # Get filename
                filename = ydl.prepare_filename(info)
                if fmt == "mp3":
                    filename = filename.rsplit('.', 1)[0] + '.mp3'
                
                file_size = get_file_size(filename)
                
                db_record['filename'] = os.path.basename(filename)
                db_record['file_size'] = file_size
                db_record['status'] = 'success'
                
                save_to_db(db_record)
                
                elapsed_time = int(time.time() - download_info['start_time'])
                
                socketio.emit("done", {
                    "msg": "✅ Tải hoàn tất! File đã được lưu vào thư mục 'downloads'",
                    "percent": "100%",
                    "file_size": format_file_size(file_size),
                    "time_taken": f"{elapsed_time}s"
                })
                
                safe_print(f"\n{'='*60}")
                safe_print(f"Completed: {title}")
                safe_print(f"Size: {format_file_size(file_size)}")
                safe_print(f"Time: {elapsed_time}s")
                safe_print(f"{'='*60}\n")
                
        except Exception as e:
            error_msg = str(e)
            
            if "Video unavailable" in error_msg or "not available" in error_msg:
                error_msg = "Video không khả dụng hoặc đã bị xóa"
            elif "Private video" in error_msg:
                error_msg = "Video ở chế độ riêng tư"
            elif "Sign in" in error_msg or "login" in error_msg.lower():
                error_msg = "Video yêu cầu đăng nhập"
            elif "HTTP Error 403" in error_msg or "Forbidden" in error_msg:
                error_msg = "Không có quyền truy cập"
            elif "HTTP Error 404" in error_msg:
                error_msg = "Không tìm thấy video"
            elif "Unsupported URL" in error_msg:
                error_msg = "Nền tảng chưa được hỗ trợ"
            
            db_record['status'] = 'failed'
            db_record['error_msg'] = error_msg
            save_to_db(db_record)
            
            socketio.emit("error", {"msg": f"Lỗi: {error_msg}"})
            safe_print(f"\nError: {error_msg}\n")

    threading.Thread(target=run_download, daemon=True).start()

# ================== AUTO OPEN BROWSER ==================
def open_browser(port):
    time.sleep(1.5)
    url = f"http://127.0.0.1:{port}"
    try:
        webbrowser.open(url)
        safe_print(f"[Browser] Opened {url}")
    except Exception as e:
        safe_print(f"[Browser] Could not open automatically. Please visit: {url}")

# ================== MAIN ==================
if __name__ == "__main__":
    port = 5000
    
    while True:
        try:
            sock = socket.socket()
            sock.bind(("127.0.0.1", port))
            sock.close()
            break
        except OSError:
            port += 1
            if port > 5010:
                print("Error: Cannot find available port!")
                exit(1)
    
    safe_print(f"\n{'='*50}")
    safe_print(f"Server running at: http://127.0.0.1:{port}")
    safe_print(f"Download directory: {os.path.abspath(DOWNLOAD_DIR)}")
    safe_print(f"Database: {os.path.abspath(DB_PATH)}")
    safe_print(f"{'='*50}\n")
    
    threading.Timer(0.5, open_browser, args=(port,)).start()
    
    socketio.run(app, host="127.0.0.1", port=port, debug=False, allow_unsafe_werkzeug=True)