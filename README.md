# 📥 Video Downloader - Real-time Progress

Web application cho phép tải video từ nhiều nền tảng khác nhau với hiển thị tiến trình real-time qua WebSocket.

## ✨ Tính năng

- ✅ Tải video từ **YouTube, Facebook, Instagram, TikTok, Twitter** và nhiều nền tảng khác
- ✅ Hiển thị **tiến trình tải real-time** (%, tốc độ, thời gian còn lại)
- ✅ Hỗ trợ tải **video MP4 (1080p)** hoặc **audio MP3 (320kbps)**
- ✅ Giao diện web đẹp, responsive, dễ sử dụng
- ✅ Tự động mở trình duyệt khi khởi động
- ✅ WebSocket để cập nhật tiến trình không cần reload

## 📋 Yêu cầu hệ thống

- **Python 3.8+**
- **FFmpeg** (để xử lý video/audio)

### Cài đặt FFmpeg:

**Windows:**
1. Tải FFmpeg từ: https://ffmpeg.org/download.html
2. Giải nén và thêm vào PATH

**Mac:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

## 🚀 Cài đặt và Chạy

### 1. Clone hoặc tải project

```bash
git clone <repository-url>
cd video-downloader
```

### 2. Tạo môi trường ảo (khuyến nghị)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 4. Chạy ứng dụng

```bash
python app.py
```

Trình duyệt sẽ tự động mở tại: `http://127.0.0.1:5000`

## 📁 Cấu trúc thư mục

```
video-downloader/
│
├── app.py                 # Flask backend với WebSocket
├── requirements.txt       # Python dependencies
├── README.md             # Tài liệu hướng dẫn
│
├── templates/
│   └── index.html        # Giao diện web
│
├── static/
│   ├── style.css         # CSS styling
│   └── script.js         # WebSocket client logic
│
└── downloads/            # Thư mục chứa video đã tải
```

## 🎯 Hướng dẫn sử dụng

1. **Mở ứng dụng** trong trình duyệt (tự động mở sau khi chạy `python app.py`)

2. **Sao chép URL video** từ YouTube, Facebook, Instagram, TikTok, v.v.

3. **Dán URL** vào ô nhập liệu

4. **Chọn định dạng:**
   - 🎬 **Video MP4**: Tải video full HD 1080p (có hình + âm thanh)
   - 🎵 **Audio MP3**: Chỉ tải âm thanh 320kbps
   - ✨ **Tự động**: Tự động chọn định dạng tốt nhất

5. **Nhấn "TẢI XUỐNG"** và theo dõi tiến trình real-time

6. **File đã tải** sẽ nằm trong thư mục `downloads/`

## 🔧 Cấu hình nâng cao

### Thay đổi chất lượng video

Trong `app.py`, dòng 91-92:

```python
# Tải 1080p (mặc định)
"format": "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",

# Tải 720p
"format": "bestvideo[height<=720]+bestaudio/best[height<=720]/best",

# Tải 4K
"format": "bestvideo[height<=2160]+bestaudio/best[height<=2160]/best",
```

### Thay đổi thư mục tải về

Trong `app.py`, dòng 15:

```python
DOWNLOAD_DIR = "downloads"  # Đổi thành đường dẫn mong muốn
```

## 🌐 Các nền tảng hỗ trợ

- YouTube
- Facebook
- Instagram
- TikTok
- Twitter/X
- Vimeo
- Dailymotion
- Reddit
- Twitch
- **Và hơn 1000+ trang web khác** (nhờ yt-dlp)

## ⚠️ Lưu ý

- Tôn trọng bản quyền khi tải video
- Một số video có thể bị hạn chế tải do chính sách của nền tảng
- Video riêng tư hoặc yêu cầu đăng nhập không thể tải được
- Cần kết nối internet ổn định

## 🐛 Xử lý lỗi thường gặp

### Lỗi: "Video unavailable"
- Video đã bị xóa hoặc không khả dụng
- Kiểm tra lại URL

### Lỗi: "FFmpeg not found"
- Chưa cài đặt FFmpeg hoặc chưa thêm vào PATH
- Cài đặt lại FFmpeg theo hướng dẫn ở trên

### Lỗi: "Private video"
- Video ở chế độ riêng tư, không thể tải

### WebSocket không kết nối
- Kiểm tra firewall
- Thử đổi port khác trong `app.py`

## 📝 License

MIT License - Sử dụng tự do cho mục đích học tập và cá nhân.

## 🤝 Đóng góp

Mọi đóng góp đều được hoan nghênh! Tạo issue hoặc pull request.

## 📧 Liên hệ

Nếu có vấn đề hoặc câu hỏi, vui lòng tạo issue trên GitHub.

---

**Enjoy downloading! 🎉**