from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import yt_dlp
import threading
import os
import webbrowser
import socket
import time
import uuid
from urllib.parse import urlparse
import requests
from datetime import datetime
import sqlite3
import json
import re

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
    try:
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
    except Exception as e:
        safe_print(f"[DB] Error saving to database: {e}")

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

# ================== QUEUE STATE ==================
download_queue = []  # List of {id, url, format, status, title, progress, ip, protocol, headers}
is_downloading = False
queue_lock = threading.Lock()

# ================== STATISTICS ==================
server_start_time = datetime.now()
stats = {
    "total_downloads": 0,
    "successful_downloads": 0,
    "failed_downloads": 0,
    "total_bytes": 0,
    "connection_count": 0
}

# ================== ENCODING HELPER ==================
def safe_print(message):
    """
    Safely print messages with Unicode characters across all platforms
    """
    try:
        print(message)
    except UnicodeEncodeError:
        try:
            print(message.encode('ascii', 'ignore').decode('ascii'))
        except:
            print("[Message contains special characters]")

# ================== FFMPEG SETUP ==================
import glob
if os.name == 'nt':  # Windows only
    winget_path = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WinGet", "Packages")
    if os.path.exists(winget_path):
        ffmpeg_dirs = glob.glob(os.path.join(winget_path, "Gyan.FFmpeg*", "ffmpeg-*", "bin"))
        if ffmpeg_dirs:
            os.environ["PATH"] = ffmpeg_dirs[0] + os.pathsep + os.environ.get("PATH", "")
            safe_print(f"[FFmpeg] Added to PATH: {ffmpeg_dirs[0]}")

# ================== NETWORK HELPERS ==================
def resolve_dns(url):
    """Resolve domain name to IP address - demonstrates DNS lookup"""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path.split('/')[0]
        # Remove port if present
        domain = domain.split(':')[0]
        ip = socket.gethostbyname(domain)
        return {
            "domain": domain,
            "ip": ip,
            "protocol": parsed.scheme.upper() or "HTTP"
        }
    except socket.gaierror as e:
        return {"domain": domain, "ip": "Unknown", "protocol": "Unknown", "error": str(e)}
    except Exception as e:
        return {"domain": "Unknown", "ip": "Unknown", "protocol": "Unknown", "error": str(e)}

def get_url_headers(url):
    """Get HTTP response headers from URL - demonstrates HTTP protocol"""
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "url": response.url,
            "is_https": response.url.startswith("https://")
        }
    except requests.exceptions.Timeout:
        return {"error": "Connection timeout", "status_code": 0}
    except requests.exceptions.ConnectionError:
        return {"error": "Connection failed", "status_code": 0}
    except Exception as e:
        return {"error": str(e), "status_code": 0}

# ================== WEB ROUTES ==================
@app.route("/")
def index():
    return render_template("index.html")

# ================== REST API ENDPOINTS ==================
@app.route("/api/queue", methods=["GET"])
def api_get_queue():
    """GET /api/queue - Retrieve download queue (RESTful API)"""
    return jsonify({
        "success": True,
        "queue": download_queue,
        "count": len(download_queue),
        "is_downloading": is_downloading
    })

@app.route("/api/download", methods=["POST"])
def api_add_download():
    """POST /api/download - Add URLs to queue (RESTful API with JSON body)"""
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "Invalid JSON"}), 400
    
    urls = data.get("urls", [])
    fmt = data.get("format", "auto")
    quality = data.get("quality", "best")
    
    if not urls:
        return jsonify({"success": False, "error": "No URLs provided"}), 400
    
    added = []
    for url in urls:
        url = url.strip()
        if not url:
            continue
        
        # Resolve DNS for network info
        dns_info = resolve_dns(url)
        
        item = {
            "id": str(uuid.uuid4()),
            "url": url,
            "format": fmt,
            "quality": quality,
            "status": "pending",
            "title": None,
            "progress": "",
            "ip": dns_info.get("ip", "Unknown"),
            "domain": dns_info.get("domain", "Unknown"),
            "protocol": dns_info.get("protocol", "Unknown")
        }
        
        with queue_lock:
            download_queue.append(item)
        added.append(item)
    
    socketio.emit("queue_updated", {"queue": download_queue})
    
    return jsonify({
        "success": True,
        "added": len(added),
        "items": added
    })

@app.route("/api/queue/<item_id>", methods=["DELETE"])
def api_delete_queue_item(item_id):
    """DELETE /api/queue/{id} - Remove item from queue (RESTful API)"""
    global download_queue
    
    with queue_lock:
        original_len = len(download_queue)
        download_queue = [item for item in download_queue if item["id"] != item_id]
        removed = original_len - len(download_queue)
    
    socketio.emit("queue_updated", {"queue": download_queue})
    
    return jsonify({
        "success": removed > 0,
        "removed": removed
    })

@app.route("/api/status", methods=["GET"])
def api_status():
    """GET /api/status - Server status and statistics (RESTful API)"""
    uptime = datetime.now() - server_start_time
    
    return jsonify({
        "success": True,
        "server": {
            "uptime_seconds": int(uptime.total_seconds()),
            "uptime_formatted": str(uptime).split('.')[0],
            "start_time": server_start_time.isoformat()
        },
        "stats": stats,
        "queue": {
            "count": len(download_queue),
            "is_downloading": is_downloading
        }
    })

@app.route("/api/info", methods=["POST"])
def api_url_info():
    """POST /api/info - Get network info for URL (DNS, headers)"""
    data = request.get_json()
    url = data.get("url", "") if data else ""
    
    if not url:
        return jsonify({"success": False, "error": "No URL provided"}), 400
    
    dns_info = resolve_dns(url)
    headers_info = get_url_headers(url)
    
    return jsonify({
        "success": True,
        "url": url,
        "dns": dns_info,
        "http": headers_info
    })

@app.route("/api/history")
def get_history():
    """Get download history"""
    try:
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
    except Exception as e:
        return jsonify([])

@app.route("/api/delete/<int:id>", methods=['DELETE'])
@app.route("/api/delete/<int:id>", methods=['DELETE'])
def delete_record(id):
    """Delete a download record and the actual file"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # 1. Lấy tên file trước khi xóa record
        c.execute("SELECT filename FROM downloads WHERE id=?", (id,))
        row = c.fetchone()
        
        if row and row[0]:
            filename = row[0]
            # Tạo đường dẫn file đầy đủ
            file_path = os.path.join(DOWNLOAD_DIR, filename)
            
            # Xóa file nếu tồn tại
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    safe_print(f"[FILE] Deleted physical file: {file_path}")
                except Exception as e:
                    safe_print(f"[FILE] Error deleting physical file: {e}")
            else:
                safe_print(f"[FILE] File not found: {file_path}")

        # 2. Xóa record trong DB
        c.execute("DELETE FROM downloads WHERE id=?", (id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        safe_print(f"[DB] Error deleting record: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route("/api/clear-history", methods=['POST'])
def clear_history():
    """Clear all download history"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM downloads")
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route("/api/search-history", methods=['GET'])
def search_history():
    """Search in download history"""
    try:
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
    except Exception as e:
        return jsonify([])

@app.route("/api/export-history", methods=['GET'])
def export_history():
    """Export history as JSON"""
    try:
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
    except Exception as e:
        return jsonify([])

# ================== SOCKET ==================
@socketio.on("connect")
def handle_connect():
    print("Client connected")
    emit("connected", {"status": "ready"})
    # Send current queue state
    emit("queue_updated", {"queue": download_queue})

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

# ================== QUEUE MANAGEMENT ==================
@socketio.on("add_to_queue")
def add_to_queue(data):
    global download_queue
    
    urls = data.get("urls", [])
    fmt = data.get("format", "auto")
    quality = data.get("quality", "best")
    
    safe_print(f"\n[QUEUE] Adding {len(urls)} URLs to queue (Format: {fmt}, Quality: {quality})")
    
    with queue_lock:
        for url in urls:
            url = url.strip()
            if not url:
                continue
                
            # Check if URL already in queue
            if any(item["url"] == url for item in download_queue):
                safe_print(f"[QUEUE] Skipping duplicate: {url}")
                continue
            
            # Resolve DNS for network info
            dns_info = resolve_dns(url)
            safe_print(f"[DNS] {dns_info.get('domain')} -> {dns_info.get('ip')}")
            
            item = {
                "id": str(uuid.uuid4()),
                "url": url,
                "format": fmt,
                "quality": quality,
                "status": "pending",  # pending, downloading, completed, error
                "title": None,
                "progress": "",
                "ip": dns_info.get("ip", "Unknown"),
                "domain": dns_info.get("domain", "Unknown"),
                "protocol": dns_info.get("protocol", "HTTP")
            }
            download_queue.append(item)
            safe_print(f"[QUEUE] Added: {url}")
    
    # Broadcast updated queue to all clients
    socketio.emit("queue_updated", {"queue": download_queue})

@socketio.on("remove_from_queue")
def remove_from_queue(data):
    global download_queue
    
    item_id = data.get("id")
    
    with queue_lock:
        download_queue = [item for item in download_queue if item["id"] != item_id or item["status"] == "downloading"]
    
    socketio.emit("queue_updated", {"queue": download_queue})

@socketio.on("clear_queue")
def clear_queue():
    global download_queue
    
    with queue_lock:
        # Keep only downloading items
        download_queue = [item for item in download_queue if item["status"] == "downloading"]
    
    socketio.emit("queue_updated", {"queue": download_queue})

@socketio.on("start_queue_download")
def start_queue_download():
    global is_downloading
    
    if is_downloading:
        safe_print("[QUEUE] Already downloading")
        return
    
    # Find first pending item
    pending_items = [item for item in download_queue if item["status"] == "pending"]
    if not pending_items:
        socketio.emit("error", {"msg": "Không có video nào trong hàng đợi!"})
        return
    
    is_downloading = True
    socketio.emit("download_started", {})
    
    # Start download in background thread
    threading.Thread(target=process_queue, daemon=True).start()

# ================== DOWNLOAD PROCESSOR ==================
def process_queue():
    global is_downloading, download_queue
    
    while True:
        # Find next pending item
        current_item = None
        with queue_lock:
            for item in download_queue:
                if item["status"] == "pending":
                    current_item = item
                    item["status"] = "downloading"
                    break
        
        if not current_item:
            # No more items to download
            break
        
        # Broadcast queue update
        socketio.emit("queue_updated", {"queue": download_queue})
        
        # Download this item
        success, title = download_single_item(current_item)
        
        # Update status and emit success notification
        with queue_lock:
            for item in download_queue:
                if item["id"] == current_item["id"]:
                    item["status"] = "completed" if success else "error"
                    item["progress"] = "✅" if success else "❌"
                    break
        
        # Update statistics
        stats["total_downloads"] += 1
        if success:
            stats["successful_downloads"] += 1
        else:
            stats["failed_downloads"] += 1
        
        # Broadcast queue update
        socketio.emit("queue_updated", {"queue": download_queue})
        
        # Emit individual item completion notification
        if success:
            socketio.emit("item_completed", {
                "id": current_item["id"],
                "title": title or current_item.get("title", "Video"),
                "success": True
            })
        else:
            socketio.emit("item_completed", {
                "id": current_item["id"],
                "title": title or current_item.get("title", "Video"),
                "success": False
            })
        
        # Auto-remove completed item after delay
        def remove_completed_item(item_id):
            global download_queue
            time.sleep(3)  # Wait 3 seconds before removing
            with queue_lock:
                download_queue = [i for i in download_queue if i["id"] != item_id or i["status"] not in ["completed", "error"]]
            socketio.emit("queue_updated", {"queue": download_queue})
        
        threading.Thread(target=remove_completed_item, args=(current_item["id"],), daemon=True).start()
        
        # Save to database (History)
        try:
            db_record = {
                'title': title or current_item.get("title", "Video"),
                'url': current_item["url"],
                'platform': current_item.get("domain", "Unknown"), # We use domain as platform proxy here, or info['extractor'] if available
                'format': current_item["format"],
                'status': 'success' if success else 'failed',
                'error_msg': None if success else "Download failed",
                'duration': current_item.get("duration", "N/A"),
                'filename': f"{title}.{current_item['format']}" if title else "unknown_file", # Rough estimate
                'file_size': 0 # We might need to get real file size if possible
            }
            
            # Additional info from success
            if success:
                # We can try to get file size
                try:
                   fpath = os.path.join(DOWNLOAD_DIR, f"{title}.mp3" if current_item['format'] == 'mp3' else f"{title}.mp4")
                   if os.path.exists(fpath):
                       db_record['file_size'] = os.path.getsize(fpath)
                       db_record['filename'] = os.path.basename(fpath)
                except:
                    pass
            
            save_to_db(db_record)
        except Exception as e:
            safe_print(f"[DB] Failed to save history: {e}")

        # Small delay between downloads
        time.sleep(1)
    
    is_downloading = False
    socketio.emit("all_downloads_complete", {})
    safe_print("\n[QUEUE] All downloads complete!")

def download_single_item(item):
    """Download a single queue item. Returns (success, title) tuple."""
    
    url = item["url"]
    fmt = item["format"]
    quality = item.get("quality", "best")
    item_id = item["id"]
    
    safe_print(f"\n[DOWNLOAD] Starting: {url}")
    socketio.emit("status", {"msg": "Đang phân tích video...", "percent": "0%"})
    
    def progress_hook(d):
        try:
            status = d.get("status")
            # Debug: log every hook call
            downloaded = d.get("downloaded_bytes", 0)
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            safe_print(f"[HOOK] status={status}, downloaded={downloaded}, total={total}")
            
            if status == "downloading":
                downloaded_bytes = d.get("downloaded_bytes", 0)
                total_bytes = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
                
                if total_bytes > 0:
                    percent = (downloaded_bytes / total_bytes) * 100
                    percent_str = f"{percent:.1f}%"
                    
                    # Debug log
                    safe_print(f"[PROGRESS] {percent_str}")
                    
                    # Update item progress
                    with queue_lock:
                        for queue_item in download_queue:
                            if queue_item["id"] == item_id:
                                queue_item["progress"] = percent_str
                                break
                    
                    # Emit with msg field for frontend compatibility
                    socketio.emit("progress", {
                        "percent": percent_str, 
                        "msg": f"Đang tải xuống... {percent_str}",
                        "status": "downloading"
                    })
                    socketio.emit("queue_item_progress", {"id": item_id, "percent": percent_str})
                    
            elif status == "finished":
                safe_print("[PROGRESS] 100% - Processing...")
                socketio.emit("progress", {"percent": "100%", "msg": "Đang xử lý video...", "status": "processing"})
                
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
    elif fmt == "mp4":
        # Logic adapted from original code to support quality selection
        safe_print(f"[DOWNLOAD] Quality preference: {quality}")
        
        format_string = f"bestvideo[height<={quality.replace('p', '')}][ext=mp4]+bestaudio[ext=m4a]/best[height<={quality.replace('p', '')}]" if quality != "best" else "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best"
        
        ydl_opts = {
            "format": format_string,
            "merge_output_format": "mp4",
            "outtmpl": f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
            "progress_hooks": [progress_hook],
            "noplaylist": True,
            "quiet": False,
            "no_warnings": False,
            "noprogress": False,
             "postprocessors": [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
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

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Get video info first
            socketio.emit("status", {"msg": "Đang lấy thông tin video...", "percent": "0%"})
            
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Unknown')
            duration = info.get('duration', 0)
            platform = info.get('extractor', 'Unknown')
            
            # Update item title and platform info
            with queue_lock:
                for queue_item in download_queue:
                    if queue_item["id"] == item_id:
                        queue_item["title"] = title
                        queue_item["duration"] = f"{int(duration)//60}:{int(duration)%60:02d}" if duration else "N/A"
                        queue_item["platform"] = platform
                        break
            
            # Update item title
            with queue_lock:
                for queue_item in download_queue:
                    if queue_item["id"] == item_id:
                        queue_item["title"] = title
                        break
            
            # Broadcast queue update with title
            socketio.emit("queue_updated", {"queue": download_queue})
            
            # Format duration
            if duration:
                duration_int = int(duration)
                duration_str = f"{duration_int // 60}:{duration_int % 60:02d}"
            else:
                duration_str = "N/A"
                
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
            "msg": f"✅ Đã tải xong: {title}",
            "percent": "100%"
        })
        
        safe_print(f"\n{'='*60}")
        safe_print(f"Completed: {title}")
        safe_print(f"Saved to: {os.path.abspath(DOWNLOAD_DIR)}")
        safe_print(f"{'='*60}\n")
        
        return True, title
        
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
        
        socketio.emit("error", {"msg": f"Lỗi: {error_msg}"})
        safe_print(f"\nError: {error_msg}\n")
        
        return False, None

# ================== LEGACY SINGLE DOWNLOAD (keeping for compatibility) ==================
@socketio.on("start_download")
def start_download(data):
    """Legacy single download - now adds to queue and starts"""
    url = data.get("url", "").strip()
    url = data.get("url", "").strip()
    fmt = data.get("format", "auto")
    quality = data.get("quality", "best")
    
    if not url:
        socketio.emit("error", {"msg": "Vui lòng nhập URL!"})
        return
    
    # Add to queue
    add_to_queue({"urls": [url], "format": fmt, "quality": quality})
    
    # Start queue processing
    start_queue_download()

# ================== AUTO OPEN BROWSER ==================
def open_browser(port):
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
    
    # Find available port
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
    safe_print(f"{'='*50}\n")
    
    # Open browser automatically
    threading.Timer(0.5, open_browser, args=(port,)).start()
    
    # Run server with threading
    socketio.run(app, host="127.0.0.1", port=port, debug=False, allow_unsafe_werkzeug=True)