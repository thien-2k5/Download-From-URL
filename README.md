# 📥 Video Downloader Pro

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

**Web application chuyên nghiệp cho phép tải video/audio từ 1000+ nền tảng với giao diện hiện đại và tính năng nâng cao**

[Tính năng](#-tính-năng-chính) • [Cài đặt](#-cài-đặt) • [Hướng dẫn](#-hướng-dẫn-sử-dụng) • [Demo](#-demo-screenshots) • [FAQ](#-câu-hỏi-thường-gặp)

</div>

---

## 🌟 Tính năng chính

### 🎬 Download Features
- ✅ **Multi-platform Support**: Tải từ YouTube, Facebook, Instagram, TikTok, Twitter và **1000+ nền tảng**
- ✅ **Quality Selection**: Chọn chất lượng video từ 480p đến 4K (2160p)
- ✅ **Format Options**: MP4 (video), MP3 (audio 320kbps), hoặc tự động
- ✅ **Real-time Progress**: Hiển thị tiến trình tải với tốc độ và thời gian còn lại
- ✅ **Batch Information**: Xem trước thông tin video trước khi tải

### 💾 Data Management
- ✅ **Download History**: Lưu trữ lịch sử tải xuống với SQLite database
- ✅ **Smart Search**: Tìm kiếm nhanh trong lịch sử theo tên, platform, URL
- ✅ **Advanced Filters**: Lọc theo trạng thái (success/failed) và định dạng (MP4/MP3)
- ✅ **Export Data**: Xuất lịch sử thành file JSON để backup

### 🎨 User Experience
- ✅ **Modern UI**: Giao diện đẹp với animations mượt mà
- ✅ **Dark Mode**: Chế độ tối bảo vệ mắt, lưu preference
- ✅ **Responsive Design**: Tối ưu cho cả desktop và mobile
- ✅ **Clipboard Integration**: Paste URL trực tiếp từ clipboard
- ✅ **Keyboard Shortcuts**: Phím tắt tăng tốc workflow
- ✅ **Toast Notifications**: Thông báo đẹp mắt, không làm phiền

### ⚡ Technical Features
- ✅ **WebSocket Real-time**: Cập nhật tiến trình không cần reload
- ✅ **Cross-platform**: Hoạt động trên Windows, macOS, Linux
- ✅ **Unicode Support**: Xử lý tên video tiếng Việt và các ngôn ngữ khác
- ✅ **Auto Port Detection**: Tự động tìm port khả dụng (hữu ích cho macOS)
- ✅ **Error Handling**: Xử lý lỗi thông minh với thông báo dễ hiểu

---

## 📋 Yêu cầu hệ thống

### Phần mềm cần thiết
- **Python**: 3.8 trở lên
- **FFmpeg**: Để xử lý video/audio (bắt buộc)
- **pip**: Python package manager

### Kiểm tra Python version
```bash
python --version
# hoặc
python3 --version
```

### Kiểm tra pip
```bash
pip --version
# hoặc
python -m pip --version
```

---

## 🚀 Cài đặt

### Bước 1: Cài đặt FFmpeg

FFmpeg là công cụ bắt buộc để xử lý video/audio. Chọn hướng dẫn phù hợp với hệ điều hành của bạn:

<details>
<summary><b>🪟 Windows</b></summary>

#### Phương án 1: Sử dụng winget (Khuyến nghị - Windows 10/11)
```bash
winget install ffmpeg
```

#### Phương án 2: Tải thủ công
1. Truy cập: https://github.com/BtbN/FFmpeg-Builds/releases
2. Tải file: `ffmpeg-master-latest-win64-gpl.zip`
3. Giải nén vào thư mục (VD: `C:\ffmpeg`)
4. Thêm vào PATH:
   - Mở **System Properties** → **Environment Variables**
   - Trong **System Variables**, tìm **Path** → **Edit**
   - **New** → Dán đường dẫn: `C:\ffmpeg\bin`
   - **OK** để lưu

#### Kiểm tra cài đặt
```bash
ffmpeg -version
```

</details>

<details>
<summary><b>🍎 macOS</b></summary>

#### Sử dụng Homebrew (Khuyến nghị)
```bash
# Cài đặt Homebrew nếu chưa có
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Cài đặt FFmpeg
brew install ffmpeg
```

#### Kiểm tra cài đặt
```bash
ffmpeg -version
```

**Lưu ý macOS:** Port 5000 thường bị chiếm bởi AirPlay Receiver. App sẽ tự động chọn port khác (5001, 5002...).

</details>

<details>
<summary><b>🐧 Linux</b></summary>

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install ffmpeg
```

#### Fedora/RHEL/CentOS
```bash
sudo dnf install ffmpeg
```

#### Arch Linux
```bash
sudo pacman -S ffmpeg
```

#### Kiểm tra cài đặt
```bash
ffmpeg -version
```

</details>

---

### Bước 2: Clone hoặc tải project

```bash
# Clone từ Git
git clone https://github.com/your-username/video-downloader-pro.git
cd video-downloader-pro

# Hoặc tải ZIP và giải nén
```

---

### Bước 3: Tạo môi trường ảo (Khuyến nghị)

Môi trường ảo giúp cách ly dependencies, tránh xung đột với các project khác.

<details>
<summary><b>🪟 Windows</b></summary>

```bash
# Tạo môi trường ảo
python -m venv venv

# Kích hoạt
venv\Scripts\activate

# Khi thấy (venv) ở đầu dòng lệnh là thành công
```

</details>

<details>
<summary><b>🍎 macOS / 🐧 Linux</b></summary>

```bash
# Tạo môi trường ảo
python3 -m venv venv

# Kích hoạt
source venv/bin/activate

# Khi thấy (venv) ở đầu dòng lệnh là thành công
```

</details>

---

### Bước 4: Cài đặt Python dependencies

```bash
pip install -r requirements.txt
```

**Dependencies chính:**
- `Flask` - Web framework
- `Flask-SocketIO` - WebSocket support
- `yt-dlp` - Video downloader core
- `requests` - HTTP library

---

### Bước 5: Chạy ứng dụng

<details>
<summary><b>🪟 Windows</b></summary>

```bash
python app.py
```

</details>

<details>
<summary><b>🍎 macOS / 🐧 Linux</b></summary>

```bash
python3 app.py
```

</details>

**Kết quả mong đợi:**
```
==================================================
Server running at: http://127.0.0.1:5000
Download directory: /path/to/downloads
Database: /path/to/downloads.db
==================================================

[Browser] Opened http://127.0.0.1:5000
```

Trình duyệt sẽ tự động mở. Nếu không, mở thủ công: http://127.0.0.1:5000

---

## 📖 Hướng dẫn sử dụng

### 1️⃣ Tải video cơ bản

1. **Copy URL** video từ YouTube, TikTok, Facebook...
2. **Paste URL** vào ô nhập (hoặc nhấn nút "📋 Paste từ Clipboard")
3. **Chọn định dạng:**
   - 🎬 **MP4**: Video full HD (có hình + âm thanh)
   - 🎵 **MP3**: Chỉ âm thanh 320kbps
   - ✨ **Tự động**: Chất lượng tốt nhất
4. **Chọn chất lượng** (nếu chọn MP4):
   - 🔥 4K (2160p)
   - 💎 2K (1440p)
   - ✨ Full HD (1080p)
   - 📺 HD (720p)
   - 📱 SD (480p)
5. **Nhấn "⬇️ TẢI XUỐNG"**
6. **Theo dõi tiến trình** real-time
7. **File tải về** nằm trong thư mục `downloads/`

---

### 2️⃣ Preview video (Xem trước)

**Mục đích:** Xem thông tin video trước khi quyết định tải

1. Paste URL vào ô nhập
2. Nhấn nút **"🔍 Preview"**
3. Xem thông tin:
   - Tiêu đề video
   - Thời lượng
   - Lượt xem
   - Nền tảng
   - Các chất lượng có sẵn

---

### 3️⃣ Quản lý lịch sử

#### Xem lịch sử
- Chuyển sang tab **"📋 History"**
- Xem danh sách video đã tải (thành công & thất bại)

#### Tìm kiếm
- Nhập từ khóa vào thanh search
- Tìm theo: tên video, platform, URL

#### Lọc dữ liệu
- **Tất cả**: Hiển thị toàn bộ
- **✅ Thành công**: Chỉ video tải thành công
- **❌ Thất bại**: Chỉ video thất bại
- **🎬 MP4**: Chỉ video
- **🎵 MP3**: Chỉ audio

#### Export lịch sử
- Nhấn nút **"📤 Export JSON"**
- File sẽ được tải về với tên: `download-history-YYYY-MM-DD.json`

#### Copy URL
- Với mỗi video thành công, nhấn **"📋 Copy URL"** để tải lại

#### Xóa lịch sử
- **Xóa 1 item**: Nhấn nút 🗑️ bên cạnh video
- **Xóa tất cả**: Nhấn nút "🗑️ Xóa tất cả" ở góc trên

---

### 4️⃣ Phím tắt hữu ích

| Phím tắt | Chức năng |
|----------|-----------|
| `Ctrl + V` | Paste URL từ clipboard |
| `Enter` | Bắt đầu tải (khi focus ở ô input) |
| `Ctrl + K` | Xóa ô nhập URL |

---

### 5️⃣ Dark Mode

- Nhấn biểu tượng **🌙/☀️** ở góc trên bên phải
- Preference được lưu tự động
- Tất cả charts và UI tự động adapt

---

## 📁 Cấu trúc Project

```
video-downloader-pro/
│
├── app.py                    # Flask backend + WebSocket + Database
├── requirements.txt          # Python dependencies
├── README.md                # Tài liệu này
├── downloads.db             # SQLite database (tự động tạo)
│
├── templates/
│   └── index.html           # Frontend HTML
│
├── static/
│   ├── style.css            # Styling with Dark Mode
│   └── script.js            # WebSocket client + UI logic
│
└── downloads/               # Thư mục chứa video đã tải
    ├── video1.mp4
    ├── audio1.mp3
    └── ...
```

---

## 🔧 Cấu hình nâng cao

### Thay đổi port server

Trong `app.py`, dòng cuối:

```python
if __name__ == "__main__":
    port = 5000  # Đổi thành port khác (VD: 8080)
```

### Thay đổi thư mục tải về

Trong `app.py`, dòng 13:

```python
DOWNLOAD_DIR = "downloads"  # Đổi thành đường dẫn mong muốn
```

### Giới hạn chất lượng video mặc định

Trong `app.py`, tìm `format_string` và chỉnh sửa:

```python
# Giới hạn tối đa 1080p
format_string = "bestvideo[height<=1080]..."

# Giới hạn tối đa 720p
format_string = "bestvideo[height<=720]..."
```

### Thêm User-Agent tùy chỉnh

Trong `app.py`, phần `common_opts`:

```python
"user_agent": "Your Custom User Agent String"
```

---

## 🌐 Danh sách nền tảng hỗ trợ

### 🔥 Popular Platforms
- ✅ YouTube (videos, playlists, shorts)
- ✅ Facebook (videos, reels)
- ✅ Instagram (posts, reels, stories, IGTV)
- ✅ TikTok (videos)
- ✅ Twitter/X (videos)
- ✅ Reddit (videos)
- ✅ Vimeo
- ✅ Dailymotion
- ✅ Twitch (clips, VODs)

### 🎵 Music & Audio
- SoundCloud
- Bandcamp
- Mixcloud
- Audiomack

### 📺 Video Platforms
- Bilibili
- Niconico
- Vevo
- 9GAG

### 📱 Social Media
- LinkedIn (videos)
- Pinterest (videos)
- Snapchat (stories)

### 🎓 Education
- Coursera
- Udemy
- Khan Academy

**Và 1000+ nền tảng khác** nhờ thư viện `yt-dlp`

Danh sách đầy đủ: https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md

---

## 🎯 Demo Screenshots

### 1. Giao diện chính - Light Mode
```
┌────────────────────────────────────────────────┐
│           📥 Video Downloader Pro              │
│  Hỗ trợ: YouTube, Facebook, Instagram...      │
├────────────────────────────────────────────────┤
│  [📋 Paste]  [🗑️ Xóa]                         │
│  ┌──────────────────────────┐  [🔍 Preview]   │
│  │ Paste URL here...        │                  │
│  └──────────────────────────┘                  │
│                                                 │
│  Định dạng: [MP4 ▼]                           │
│  Chất lượng: [1080p ▼]                        │
│                                                 │
│          [⬇️ TẢI XUỐNG]                        │
└────────────────────────────────────────────────┘
```

### 2. Đang tải xuống
```
┌────────────────────────────────────────────────┐
│  ⚡ Đang tải xuống...              87.3%       │
│  ████████████████░░░░                          │
│                                                 │
│  Tốc độ: 5.2 MB/s | Đã tải: 45.6 MB           │
│  🎬 Amazing Video Title Here                   │
└────────────────────────────────────────────────┘
```

### 3. Lịch sử tải
```
┌────────────────────────────────────────────────┐
│  📋 Lịch sử tải xuống        [📤Export] [🗑️]  │
│  [🔍 Tìm kiếm...]                              │
│  [Tất cả] [✅Success] [❌Failed] [🎬MP4] [🎵MP3]│
├────────────────────────────────────────────────┤
│  📺  ✅ Video Title                            │
│       📱YouTube  📦MP4  💾45.6MB  ⏱️5:30      │
│       📅 2024-01-19 10:30    [📋Copy] [🗑️]    │
└────────────────────────────────────────────────┘
```

---

## ⚠️ Lưu ý quan trọng

### ⚖️ Bản quyền
- **Tôn trọng bản quyền** khi tải video
- Chỉ tải video bạn có quyền hoặc cho mục đích cá nhân
- Không sử dụng cho mục đích thương mại trái phép

### 🔒 Giới hạn
- ❌ **Video riêng tư**: Không thể tải
- ❌ **Video yêu cầu login**: Không hỗ trợ
- ❌ **Video có DRM**: Bị bảo vệ, không tải được
- ❌ **Live streams**: Không hỗ trợ (chỉ VODs)

### 📡 Kết nối
- Cần **kết nối internet ổn định**
- Tốc độ tải phụ thuộc vào:
  - Băng thông internet
  - Server của nền tảng
  - Kích thước file

---

## 🐛 Xử lý lỗi thường gặp

### ❌ "FFmpeg not found"
**Nguyên nhân:** FFmpeg chưa được cài đặt hoặc không có trong PATH

**Giải pháp:**
1. Cài đặt FFmpeg theo hướng dẫn [ở trên](#bước-1-cài-đặt-ffmpeg)
2. Khởi động lại terminal/command prompt
3. Kiểm tra: `ffmpeg -version`

---

### ❌ "Video unavailable"
**Nguyên nhân:** Video đã bị xóa, private, hoặc bị giới hạn khu vực

**Giải pháp:**
- Kiểm tra URL có đúng không
- Thử mở video trên trình duyệt
- Thử video khác

---

### ❌ "Sign in to confirm your age"
**Nguyên nhân:** Video yêu cầu xác nhận tuổi/đăng nhập

**Giải pháp:**
- App không hỗ trợ video yêu cầu login
- Thử video khác

---

### ❌ "Private video"
**Nguyên nhân:** Video ở chế độ riêng tư

**Giải pháp:**
- Không thể tải video private
- Liên hệ chủ video để public

---

### ❌ "HTTP Error 403: Forbidden"
**Nguyên nhân:** Server từ chối truy cập

**Giải pháp:**
- Nền tảng có thể chặn bot/downloader
- Thử lại sau vài phút
- Thử video khác từ nền tảng đó

---

### ❌ Port 5000 đã được sử dụng (macOS)
**Nguyên nhân:** AirPlay Receiver chiếm port 5000

**Giải pháp:**
- App tự động chọn port khác (5001, 5002...)
- Xem port trong terminal khi chạy app
- Hoặc tắt AirPlay Receiver:
  ```
  System Preferences → Sharing → AirPlay Receiver → Off
  ```

---

### ❌ "Module not found"
**Nguyên nhân:** Chưa cài dependencies

**Giải pháp:**
```bash
pip install -r requirements.txt
```

---

### ❌ Database error
**Nguyên nhân:** File database bị lỗi

**Giải pháp:**
1. Backup file `downloads.db` (nếu cần)
2. Xóa file `downloads.db`
3. Khởi động lại app (sẽ tạo database mới)

---

### ❌ WebSocket connection failed
**Nguyên nhân:** Firewall chặn hoặc port bị chiếm

**Giải pháp:**
1. Tắt tạm firewall/antivirus
2. Đổi port trong `app.py`
3. Kiểm tra không có app nào khác dùng port

---

## 🔍 Troubleshooting Commands

### Kiểm tra Python
```bash
python --version
python3 --version
which python
which python3
```

### Kiểm tra pip
```bash
pip --version
pip list
```

### Kiểm tra FFmpeg
```bash
ffmpeg -version
which ffmpeg  # Mac/Linux
where ffmpeg  # Windows
```

### Kiểm tra dependencies
```bash
pip show flask
pip show yt-dlp
pip show flask-socketio
```

### Xem log chi tiết
Khi chạy app, xem terminal để thấy log đầy đủ

---

## 📊 Database Schema

App sử dụng SQLite để lưu lịch sử:

```sql
CREATE TABLE downloads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    url TEXT,
    platform TEXT,
    format TEXT,
    file_size INTEGER,
    duration TEXT,
    filename TEXT,
    status TEXT,
    download_date TIMESTAMP,
    error_msg TEXT
);
```

**Truy vấn database:**
```bash
sqlite3 downloads.db "SELECT * FROM downloads;"
```

---

## 🚀 Performance Tips

### Tăng tốc độ tải
1. **Kết nối internet nhanh**: Yếu tố quan trọng nhất
2. **Chọn chất lượng thấp hơn**: 720p thay vì 1080p
3. **Tải MP3**: Nhanh hơn nhiều so với video

### Tiết kiệm dung lượng
1. **Chọn 720p/480p**: Thay vì 1080p/4K
2. **Tải MP3**: Chỉ 3-10 MB thay vì 50-500 MB

### Quản lý lịch sử
1. **Export thường xuyên**: Backup dữ liệu
2. **Xóa lịch sử cũ**: Giữ database nhẹ

---

## 🛠️ Development

### Tech Stack
- **Backend**: Flask + Flask-SocketIO
- **Frontend**: Vanilla JavaScript + CSS3
- **Database**: SQLite
- **Video Processing**: yt-dlp + FFmpeg
- **Real-time**: WebSocket

### Project Dependencies
```
Flask==3.0.0
Flask-SocketIO==5.3.5
yt-dlp==2024.1.7
requests==2.31.0
python-socketio==5.10.0
```

### API Endpoints

#### REST API
- `GET /` - Main page
- `GET /api/history` - Get download history
- `GET /api/search-history?q=query` - Search history
- `GET /api/export-history` - Export as JSON
- `DELETE /api/delete/<id>` - Delete record
- `POST /api/clear-history` - Clear all history

#### WebSocket Events
- `connect` - Client connected
- `disconnect` - Client disconnected
- `get_video_info` - Preview video info
- `start_download` - Start download
- `status` - Download status update
- `progress` - Progress update
- `info` - Video information
- `done` - Download completed
- `error` - Error occurred

---

## 📚 Resources

### Documentation
- [yt-dlp Documentation](https://github.com/yt-dlp/yt-dlp)
- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Socket.IO Documentation](https://socket.io/docs/)

### Related Projects
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Video downloader core
- [FFmpeg](https://ffmpeg.org/) - Media processing
- [Flask-SocketIO](https://flask-socketio.readthedocs.io/) - WebSocket support

---

## 🤝 Contributing

Contributions are welcome! Đóng góp của bạn giúp project tốt hơn.

### Cách đóng góp
1. Fork project
2. Tạo branch mới: `git checkout -b feature/AmazingFeature`
3. Commit changes: `git commit -m 'Add AmazingFeature'`
4. Push to branch: `git push origin feature/AmazingFeature`
5. Mở Pull Request

### Báo lỗi
- Mở [Issue](https://github.com/your-username/video-downloader-pro/issues)
- Mô tả chi tiết lỗi
- Kèm screenshot nếu có
- Ghi rõ hệ điều hành

---

## 📝 Changelog

### Version 2.0.0 (2024-01-19)
- ✨ Thêm Download History với SQLite
- ✨ Thêm Smart Search & Advanced Filters
- ✨ Thêm Export History (JSON)
- ✨ Thêm Dark Mode với preference
- ✨ Thêm Clipboard Integration
- ✨ Thêm Keyboard Shortcuts
- ✨ Thêm Toast Notifications
- ✨ Thêm Video Preview
- ✨ Thêm Quality Selection
- 🐛 Fix Instagram thumbnail preview
- 🔧 Tối ưu UI/UX
- 📚 Cập nhật documentation

### Version 1.0.0 (2024-01-01)
- 🎉 Initial release
- ✅ Basic download functionality
- ✅ Real-time progress
- ✅ Multi-platform support

---

## 📄 License

MIT License

Copyright (c) 2024 Video Downloader Pro

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## 🙏 Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Powerful video downloader
- [FFmpeg](https://ffmpeg.org/) - Video processing powerhouse
- [Flask](https://flask.palletsprojects.com/) - Lightweight web framework
- [Socket.IO](https://socket.io/) - Real-time communication

---

## 📧 Contact & Support

- **GitHub Issues**: [Report bugs](https://github.com/your-username/video-downloader-pro/issues)
- **Discussions**: [Ask questions](https://github.com/your-username/video-downloader-pro/discussions)
- **Email**: your.email@example.com

---

<div align="center">

**⭐ Nếu project hữu ích, hãy cho 1 star nhé! ⭐**

Made with ❤️ by [Your Name]

[⬆ Back to top](#-video-downloader-pro)

</div>