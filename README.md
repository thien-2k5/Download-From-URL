# 📥 Video Downloader Pro - Smart & Fast

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

**Web application chuyên nghiệp tải video/audio từ 1000+ nền tảng với giao diện hiện đại**

[Tính năng](#-tính-năng-chính) • [Cài đặt](#-cài-đặt-nhanh) • [Hướng dẫn](#-hướng-dẫn-sử-dụng) • [FAQ](#-xử-lý-lỗi-thường-gặp)

</div>

---

## ✨ Tính năng chính

### 🎬 Download & Quality
- ✅ Tải từ **YouTube, Facebook, Instagram, TikTok, Twitter** và **1000+ nền tảng**
- ✅ Chọn chất lượng: **480p → 4K (2160p)**
- ✅ Định dạng: **MP4 (video)**, **MP3 (audio 320kbps)**, hoặc **Tự động**
- ✅ **Real-time Progress**: Hiển thị tốc độ, % tiến trình, ETA
- ✅ **Video Preview**: Xem thông tin trước khi tải

### 💾 Smart Management
- ✅ **Download History**: Lưu lịch sử với SQLite database
- ✅ **Smart Search**: Tìm kiếm theo tên, platform, URL
- ✅ **Advanced Filters**: Lọc theo status (success/failed), format (MP4/MP3)
- ✅ **Export JSON**: Backup lịch sử dễ dàng

### 🎨 Modern UI/UX
- ✅ **Dark Mode**: Tự động lưu preference
- ✅ **Clipboard Integration**: Paste URL nhanh chóng
- ✅ **Keyboard Shortcuts**: `Ctrl+V`, `Enter`, `Ctrl+K`
- ✅ **Toast Notifications**: Thông báo đẹp, không làm phiền
- ✅ **Responsive**: Hoạt động mượt trên mọi thiết bị

### ⚡ Technical
- ✅ **WebSocket**: Cập nhật real-time không reload
- ✅ **Cross-platform**: Windows, macOS, Linux
- ✅ **Unicode Support**: Xử lý tiếng Việt và đa ngôn ngữ
- ✅ **Auto Port Detection**: Tự động tìm port khả dụng

---

## 📋 Yêu cầu

- **Python 3.8+**
- **FFmpeg** (bắt buộc)

### Kiểm tra nhanh
```bash
python --version    # hoặc python3 --version
ffmpeg -version
```

---

## 🚀 Cài đặt nhanh

### 1️⃣ Cài FFmpeg

<details>
<summary><b>🪟 Windows</b></summary>

```bash
# Sử dụng winget (khuyến nghị)
winget install ffmpeg

# Kiểm tra
ffmpeg -version
```

Hoặc tải từ: https://github.com/BtbN/FFmpeg-Builds/releases

</details>

<details>
<summary><b>🍎 macOS</b></summary>

```bash
# Sử dụng Homebrew
brew install ffmpeg

# Kiểm tra
ffmpeg -version
```

</details>

<details>
<summary><b>🐧 Linux</b></summary>

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# Fedora
sudo dnf install ffmpeg

# Kiểm tra
ffmpeg -version
```

</details>

---

### 2️⃣ Clone Project

```bash
git clone https://github.com/thien-2k5/Download-From-URL.git
cd Download-From-URL
```

---

### 3️⃣ Tạo Virtual Environment (khuyến nghị)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 4️⃣ Cài Dependencies

```bash
pip install -r requirements.txt
```

---

### 5️⃣ Chạy App

**Windows:**
```bash
python app.py
```

**macOS/Linux:**
```bash
python3 app.py
```

🎉 Trình duyệt tự động mở tại: `http://127.0.0.1:5000`

---

## 📖 Hướng dẫn sử dụng

### 🎬 Tải video cơ bản

1. **Copy URL** từ YouTube, TikTok, Facebook...
2. **Paste** vào ô nhập (hoặc nhấn "📋 Paste từ Clipboard")
3. **Chọn định dạng:**
   - 🎬 MP4: Video full HD
   - 🎵 MP3: Chỉ âm thanh
   - ✨ Tự động: Chất lượng tốt nhất
4. **Chọn chất lượng** (nếu chọn MP4): 480p → 4K
5. **Nhấn "⬇️ TẢI XUỐNG"**
6. File lưu trong thư mục `downloads/`

### 🔍 Preview Video

1. Paste URL
2. Nhấn **"🔍 Preview"**
3. Xem: Tiêu đề, thời lượng, lượt xem, chất lượng có sẵn

### 📋 Quản lý lịch sử

- **Xem lịch sử**: Tab "📋 History"
- **Tìm kiếm**: Nhập từ khóa vào thanh search
- **Lọc**: Tất cả / Success / Failed / MP4 / MP3
- **Export**: Nhấn "📤 Export JSON"
- **Copy URL**: Nhấn "📋 Copy URL" để tải lại
- **Xóa**: Xóa từng item hoặc toàn bộ

### ⌨️ Phím tắt

| Phím | Chức năng |
|------|-----------|
| `Ctrl + V` | Paste URL |
| `Enter` | Tải ngay |
| `Shift + Enter` | Xuống dòng (trong textarea) |
| `Ctrl + Enter` | Thêm vào Queue |
| `Ctrl + K` | Xóa input |

### 🌙 Dark Mode

Nhấn icon **🌙/☀️** góc trên phải để toggle

---

## 📁 Cấu trúc Project

```
Download-From-URL/
│
├── app.py                # Flask backend + WebSocket
├── requirements.txt      # Dependencies
├── downloads.db          # SQLite database (auto-created)
│
├── templates/
│   └── index.html       # Frontend
│
├── static/
│   ├── style.css        # UI Styling
│   └── script.js        # Client Logic
│
└── downloads/           # Downloaded files
```

---

## 🌐 Nền tảng hỗ trợ

### 🔥 Popular
YouTube • Facebook • Instagram • TikTok • Twitter/X • Reddit • Vimeo • Dailymotion • Twitch

### 🎵 Music
SoundCloud • Bandcamp • Mixcloud • Audiomack

### 📺 Video
Bilibili • Niconico • Vevo • 9GAG

### 🎓 Education
Coursera • Udemy • Khan Academy

**Và 1000+ nền tảng khác!**

Danh sách đầy đủ: [yt-dlp supported sites](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)

---

##  Xử lý lỗi thường gặp

### ❌ FFmpeg not found

**Giải pháp:**
1. Cài FFmpeg theo [hướng dẫn trên](#1️⃣-cài-ffmpeg)
2. Restart terminal
3. Kiểm tra: `ffmpeg -version`

---

### ❌ Video unavailable

**Nguyên nhân:** Video bị xóa, private, hoặc giới hạn khu vực

**Giải pháp:**
- Kiểm tra URL
- Thử mở video trên trình duyệt
- Thử video khác

---

### ❌ Sign in required / Private video

**Giải pháp:** App không hỗ trợ video yêu cầu login hoặc private

---

### ❌ HTTP Error 403

**Giải pháp:**
- Nền tảng có thể chặn downloader
- Thử lại sau vài phút
- Thử video khác

---

### ❌ Port 5000 đã dùng (macOS)

**Nguyên nhân:** AirPlay Receiver chiếm port

**Giải pháp:** App tự động chọn port khác (xem trong terminal)

---

### ❌ Module not found

**Giải pháp:**
```bash
pip install -r requirements.txt
```

---

### 🔍 Debug Commands

```bash
# Kiểm tra Python
python --version

# Kiểm tra pip
pip --version

# Kiểm tra FFmpeg
ffmpeg -version

# Xem installed packages
pip list

# Kiểm tra dependencies
pip show flask
pip show yt-dlp
```

---

## ⚙️ Cấu hình nâng cao

### Đổi port server

Trong `app.py`:
```python
if __name__ == "__main__":
    port = 5000  # Đổi thành port khác
```

### Đổi thư mục download

Trong `app.py`:
```python
DOWNLOAD_DIR = "downloads"  # Đổi đường dẫn
```

### Giới hạn chất lượng mặc định

Trong `app.py`, tìm `format_string`:
```python
# Giới hạn 1080p
format_string = "bestvideo[height<=1080]..."

# Giới hạn 720p
format_string = "bestvideo[height<=720]..."
```

---

## 🛠️ Tech Stack

- **Backend:** Flask + Flask-SocketIO
- **Frontend:** Vanilla JavaScript + CSS3
- **Database:** SQLite
- **Video Engine:** yt-dlp + FFmpeg
- **Real-time:** WebSocket

---

## 📊 API Reference

### REST Endpoints

- `GET /` - Main page
- `GET /api/history` - Get download history
- `GET /api/search-history?q=query` - Search
- `GET /api/export-history` - Export JSON
- `DELETE /api/delete/<id>` - Delete record
- `POST /api/clear-history` - Clear all

### WebSocket Events

**Client → Server:**
- `get_video_info` - Preview video
- `start_download` - Start download

**Server → Client:**
- `status` - Status update
- `progress` - Progress update
- `info` - Video info
- `done` - Completed
- `error` - Error occurred

---

## ⚠️ Lưu ý

### Bản quyền
-  Tôn trọng bản quyền khi tải
-  Chỉ tải cho mục đích cá nhân
-  Không dùng cho thương mại trái phép

### Giới hạn
- ❌ Video private/login required: Không hỗ trợ
- ❌ Video có DRM: Không tải được
- ❌ Live streams: Chỉ hỗ trợ VODs
- 📡 Cần internet ổn định

---

## 📚 Resources

- [yt-dlp Documentation](https://github.com/yt-dlp/yt-dlp)
- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Socket.IO Documentation](https://socket.io/docs/)

---

## 🤝 Contributing

Contributions welcome! 

1. Fork project
2. Create branch: `git checkout -b feature/AmazingFeature`
3. Commit: `git commit -m 'Add AmazingFeature'`
4. Push: `git push origin feature/AmazingFeature`
5. Open Pull Request

**Báo lỗi:** [GitHub Issues](https://github.com/thien-2k5/Download-From-URL/issues)

---

## 📝 Changelog

### Version 2.0.0 (2024-01-19)
- ✨ Download History với SQLite
- ✨ Smart Search & Filters
- ✨ Export JSON
- ✨ Dark Mode
- ✨ Clipboard Integration
- ✨ Keyboard Shortcuts
- ✨ Toast Notifications
- ✨ Video Preview
- ✨ Quality Selection
- 🐛 Bug fixes & improvements

### Version 2.2.0 (2025-01-20)
- ✨ **Multi-Video Preview**: Hiển thị preview tất cả video khi paste nhiều URLs
- ✨ **Enhanced Shortcuts**: Enter tải ngay, Shift+Enter xuống dòng, Ctrl+Enter thêm queue
- 🐛 Fix `parseUrls()` cho Windows line endings (CRLF)
- 🐛 Fix Queue display không hiện (queueBadge ID)
- 🐛 Fix progress emit cho frontend

### Version 2.1.0 (2025-01-19)
- ✨ **Multi-URL Queue**: Hỗ trợ dán nhiều link và tải hàng loạt
- ✨ **New UI**: Giao diện 3 Tab (Download, Queue, History) hiện đại
- ✨ **RESTful API**: Hỗ trợ API chuẩn cho Queue và Download
- ✨ **Pills Navigation**: Thanh điều hướng dạng viên thuốc
- ✨ **Improved Quality Logic**: Tối ưu hóa chọn định dạng 4K/2K
- ✨ **Network Tools**: DNS Resolver, Header lookup
- 🐛 Fix lỗi UI, cải thiện hiệu năng tải và hiển thị

### Version 1.0.0 (2024-01-01)
- 🎉 Initial release
- ✅ Basic download
- ✅ Real-time progress
- ✅ Multi-platform support

---

## 📄 License

MIT License - Xem file [LICENSE](LICENSE) để biết thêm chi tiết.

---

## 🙏 Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Video downloader core
- [FFmpeg](https://ffmpeg.org/) - Media processing
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Socket.IO](https://socket.io/) - Real-time communication

---

## 📧 Contact

- **GitHub:** [thien-2k5](https://github.com/thien-2k5)
- **Issues:** [Report bugs](https://github.com/thien-2k5/Download-From-URL/issues)
- **Discussions:** [Ask questions](https://github.com/thien-2k5/Download-From-URL/discussions)

---

<div align="center">

**⭐ Nếu project hữu ích, hãy cho 1 star nhé! ⭐**

Made with ❤️ by [thien-2k5](https://github.com/thien-2k5)

</div>