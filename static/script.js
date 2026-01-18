// Initialize Socket.IO
const socket = io({
    transports: ['polling', 'websocket']
});

// DOM Elements - Download Tab
const urlInput = document.getElementById("url");
const formatSelect = document.getElementById("format");
const qualitySelect = document.getElementById("quality");
const qualityGroup = document.getElementById("qualityGroup");
const downloadBtn = document.getElementById("downloadBtn");
const btnText = document.getElementById("btnText");
const progressContainer = document.getElementById("progressContainer");
const statusText = document.getElementById("status");
const percentText = document.getElementById("percent");
const progressBar = document.getElementById("progressBar");
const videoTitleText = document.getElementById("videoTitle");
const speedText = document.getElementById("speed");
const downloadedText = document.getElementById("downloaded");
const totalText = document.getElementById("total");
const videoPreview = document.getElementById("videoPreview");

let isDownloading = false;
let allHistory = [];
let currentFilter = 'all';

// ==================== THEME MANAGEMENT ====================
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    const icon = document.getElementById('themeIcon');
    icon.textContent = newTheme === 'dark' ? '☀️' : '🌙';
}

// Load saved theme
const savedTheme = localStorage.getItem('theme') || 'light';
document.documentElement.setAttribute('data-theme', savedTheme);
document.getElementById('themeIcon').textContent = savedTheme === 'dark' ? '☀️' : '🌙';

// ==================== TAB MANAGEMENT ====================
function switchTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    document.getElementById(tabName + 'Tab').classList.add('active');
    event.target.closest('.tab-btn').classList.add('active');
    
    if (tabName === 'history') {
        loadHistory();
    }
}

// ==================== CLIPBOARD FEATURES ====================
async function pasteFromClipboard() {
    try {
        const text = await navigator.clipboard.readText();
        if (text && (text.startsWith('http://') || text.startsWith('https://'))) {
            urlInput.value = text;
            urlInput.focus();
            
            // Show notification
            showNotification('✅ Đã dán từ clipboard!', 'success');
        } else {
            showNotification('⚠️ Clipboard không chứa URL hợp lệ', 'warning');
        }
    } catch (err) {
        showNotification('❌ Không thể đọc clipboard. Vui lòng dán thủ công (Ctrl+V)', 'error');
    }
}

function clearInput() {
    urlInput.value = '';
    urlInput.focus();
    videoPreview.style.display = 'none';
}

// ==================== NOTIFICATION SYSTEM ====================
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        padding: 15px 25px;
        background: ${type === 'success' ? '#48bb78' : type === 'error' ? '#f56565' : '#ffc107'};
        color: white;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        z-index: 9999;
        animation: slideInRight 0.3s ease-out;
        font-weight: 600;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add CSS animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(400px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(400px); opacity: 0; }
    }
`;
document.head.appendChild(style);

// ==================== KEYBOARD SHORTCUTS ====================
document.addEventListener('keydown', (e) => {
    // Ctrl + V: Paste from clipboard
    if (e.ctrlKey && e.key === 'v' && document.activeElement !== urlInput) {
        e.preventDefault();
        pasteFromClipboard();
    }
    
    // Ctrl + K: Clear input
    if (e.ctrlKey && e.key === 'k') {
        e.preventDefault();
        clearInput();
    }
    
    // Enter: Download (if URL input is focused)
    if (e.key === 'Enter' && document.activeElement === urlInput && !isDownloading) {
        startDownload();
    }
});

// ==================== FORMAT CHANGE HANDLER ====================
formatSelect.addEventListener('change', () => {
    qualityGroup.style.display = formatSelect.value === 'mp4' ? 'block' : 'none';
});

// ==================== SOCKET EVENTS ====================
socket.on("connect", () => {
    console.log("✅ Connected to server! Socket ID:", socket.id);
});

socket.on("status", (data) => {
    showProgress();
    statusText.textContent = data.msg;
    if (data.percent) {
        updatePercent(data.percent);
    }
});

socket.on("info", (data) => {
    if (data.title) {
        videoTitleText.innerHTML = `🎬 <strong>${data.title}</strong>`;
        videoTitleText.style.display = "block";
    }
    if (data.msg) {
        statusText.textContent = data.msg;
    }
});

socket.on("progress", (data) => {
    showProgress();
    
    if (data.status === "downloading") {
        statusText.textContent = "⚡ Đang tải xuống...";
    } else if (data.status === "processing") {
        statusText.textContent = data.msg || "🔄 Đang xử lý...";
    }
    
    if (data.percent) updatePercent(data.percent);
    if (data.speed) speedText.textContent = data.speed;
    if (data.downloaded) downloadedText.textContent = data.downloaded;
    if (data.total) totalText.textContent = data.total;
});

socket.on("done", (data) => {
    isDownloading = false;
    enableButton();
    
    statusText.textContent = "✅ Tải thành công!";
    updatePercent("100%");
    
    showNotification(`✅ Tải thành công! ${data.file_size}`, 'success');
    
    setTimeout(() => {
        // Update history badge
        updateHistoryBadge();
    }, 500);
});

socket.on("error", (data) => {
    isDownloading = false;
    enableButton();
    showError(data.msg);
});

socket.on("video_info", (data) => {
    displayVideoPreview(data);
});

// ==================== PREVIEW VIDEO ====================
function previewVideo() {
    const url = urlInput.value.trim();
    
    if (!url) {
        showNotification("⚠️ Vui lòng nhập URL video!", 'warning');
        return;
    }
    
    videoPreview.style.display = 'none';
    statusText.textContent = "🔍 Đang lấy thông tin video...";
    showProgress();
    
    socket.emit("get_video_info", { url });
}

function displayVideoPreview(data) {
    hideProgress();
    videoPreview.style.display = 'block';
    
    const thumbnail = document.getElementById('previewThumbnail');
    if (data.thumbnail) {
        thumbnail.src = data.thumbnail;
        thumbnail.style.display = 'block';
        thumbnail.onerror = function() {
            this.style.display = 'none';
        };
    } else {
        thumbnail.style.display = 'none';
    }
    
    document.getElementById('previewTitle').textContent = data.title;
    document.getElementById('previewPlatform').textContent = `📱 ${data.platform}`;
    document.getElementById('previewDuration').textContent = `⏱️ ${data.duration}`;
    document.getElementById('previewViews').textContent = `👁️ ${data.view_count}`;
    
    const formatsDiv = document.getElementById('previewFormats');
    formatsDiv.innerHTML = '';
    
    if (data.formats && data.formats.length > 0) {
        data.formats.forEach(format => {
            const badge = document.createElement('div');
            badge.className = 'format-badge';
            badge.textContent = `${format.quality} (${format.filesize})`;
            formatsDiv.appendChild(badge);
        });
    }
}

// ==================== DOWNLOAD FUNCTIONS ====================
function startDownload() {
    const url = urlInput.value.trim();
    const format = formatSelect.value;
    const quality = qualitySelect.value;
    
    if (!url) {
        showNotification("⚠️ Vui lòng nhập URL video!", 'warning');
        urlInput.focus();
        return;
    }
    
    if (!url.startsWith("http://") && !url.startsWith("https://")) {
        showNotification("⚠️ URL không hợp lệ!", 'warning');
        urlInput.focus();
        return;
    }
    
    resetProgress();
    showProgress();
    disableButton();
    
    isDownloading = true;
    socket.emit("start_download", { url, format, quality });
}

function showProgress() {
    progressContainer.style.display = "block";
}

function hideProgress() {
    progressContainer.style.display = "none";
}

function resetProgress() {
    statusText.textContent = "⏳ Đang chuẩn bị...";
    percentText.textContent = "0%";
    progressBar.style.width = "0%";
    videoTitleText.textContent = "";
    videoTitleText.style.display = "none";
    speedText.textContent = "--";
    downloadedText.textContent = "--";
    totalText.textContent = "--";
}

function updatePercent(percentStr) {
    percentText.textContent = percentStr;
    const percentNum = parseFloat(percentStr.replace("%", ""));
    
    if (!isNaN(percentNum)) {
        const clampedPercent = Math.min(Math.max(percentNum, 0), 100);
        progressBar.style.width = clampedPercent + "%";
    }
}

function showError(message) {
    showProgress();
    statusText.textContent = "❌ Lỗi";
    videoTitleText.textContent = message;
    videoTitleText.style.display = "block";
    videoTitleText.style.background = "#ffe0e0";
    videoTitleText.style.borderLeft = "4px solid #dc3545";
    videoTitleText.style.color = "#dc3545";
    
    showNotification("❌ " + message, 'error');
}

function disableButton() {
    downloadBtn.disabled = true;
    btnText.textContent = "⏳ ĐANG TẢI...";
    downloadBtn.style.opacity = "0.6";
}

function enableButton() {
    downloadBtn.disabled = false;
    btnText.textContent = "⬇️ TẢI XUỐNG";
    downloadBtn.style.opacity = "1";
}

// ==================== HISTORY FUNCTIONS ====================
async function loadHistory() {
    const historyList = document.getElementById('historyList');
    historyList.innerHTML = '<div class="loading">⏳ Đang tải lịch sử...</div>';
    
    try {
        const response = await fetch('/api/history');
        allHistory = await response.json();
        
        updateHistoryBadge();
        displayHistory(allHistory);
        
    } catch (error) {
        historyList.innerHTML = '<div class="loading">❌ Lỗi khi tải lịch sử</div>';
        console.error('Error loading history:', error);
    }
}

function displayHistory(history) {
    const historyList = document.getElementById('historyList');
    
    if (history.length === 0) {
        historyList.innerHTML = '<div class="loading">📭 Chưa có lịch sử tải xuống</div>';
        return;
    }
    
    historyList.innerHTML = '';
    
    history.forEach(item => {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'history-item';
        
        const statusIcon = item.status === 'success' ? '✅' : '❌';
        
        itemDiv.innerHTML = `
            <div class="history-icon">${item.platform_icon}</div>
            <div class="history-info">
                <h3>${statusIcon} ${item.title || 'Unknown'}</h3>
                <div class="history-meta">
                    <span>📱 ${item.platform || 'Unknown'}</span>
                    <span>📦 ${item.format || 'N/A'}</span>
                    <span>💾 ${item.file_size}</span>
                    <span>⏱️ ${item.duration || 'N/A'}</span>
                </div>
                <div class="history-date">
                    📅 ${new Date(item.download_date).toLocaleString('vi-VN')}
                </div>
                ${item.error_msg ? `<div style="color: #f56565; margin-top: 8px;">⚠️ ${item.error_msg}</div>` : ''}
            </div>
            <div class="history-actions">
                ${item.status === 'success' ? `<button class="copy-btn" onclick="copyUrl('${item.url}')">📋 Copy URL</button>` : ''}
                <button class="delete-btn" onclick="deleteHistoryItem(${item.id})">🗑️ Xóa</button>
            </div>
        `;
        
        historyList.appendChild(itemDiv);
    });
}

function updateHistoryBadge() {
    const badge = document.getElementById('historyBadge');
    if (badge && allHistory) {
        badge.textContent = allHistory.length;
    }
}

async function copyUrl(url) {
    try {
        await navigator.clipboard.writeText(url);
        showNotification('✅ Đã copy URL vào clipboard!', 'success');
    } catch (err) {
        showNotification('❌ Không thể copy URL', 'error');
    }
}

async function deleteHistoryItem(id) {
    if (!confirm('Bạn có chắc muốn xóa mục này?')) return;
    
    try {
        await fetch(`/api/delete/${id}`, { method: 'DELETE' });
        showNotification('✅ Đã xóa!', 'success');
        loadHistory();
    } catch (error) {
        showNotification('❌ Lỗi khi xóa', 'error');
    }
}

async function clearHistory() {
    if (!confirm('⚠️ Bạn có chắc muốn xóa toàn bộ lịch sử?')) return;
    
    try {
        await fetch('/api/clear-history', { method: 'POST' });
        showNotification('✅ Đã xóa toàn bộ lịch sử', 'success');
        loadHistory();
    } catch (error) {
        showNotification('❌ Lỗi khi xóa', 'error');
    }
}

// ==================== SEARCH FUNCTION ====================
let searchTimeout;
async function searchHistory(query) {
    clearTimeout(searchTimeout);
    
    if (!query.trim()) {
        displayHistory(allHistory);
        return;
    }
    
    searchTimeout = setTimeout(async () => {
        try {
            const response = await fetch(`/api/search-history?q=${encodeURIComponent(query)}`);
            const results = await response.json();
            displayHistory(results);
        } catch (error) {
            console.error('Search error:', error);
        }
    }, 300);
}

// ==================== FILTER FUNCTION ====================
function filterHistory(filter) {
    currentFilter = filter;
    
    // Update active button
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    let filtered = allHistory;
    
    if (filter === 'success') {
        filtered = allHistory.filter(item => item.status === 'success');
    } else if (filter === 'failed') {
        filtered = allHistory.filter(item => item.status === 'failed');
    } else if (filter === 'mp4') {
        filtered = allHistory.filter(item => item.format === 'mp4');
    } else if (filter === 'mp3') {
        filtered = allHistory.filter(item => item.format === 'mp3');
    }
    
    displayHistory(filtered);
}

// ==================== EXPORT FUNCTION ====================
async function exportHistory() {
    try {
        const response = await fetch('/api/export-history');
        const data = await response.json();
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `download-history-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        showNotification('✅ Đã export lịch sử thành công!', 'success');
    } catch (error) {
        showNotification('❌ Lỗi khi export', 'error');
    }
}

// ==================== EVENT LISTENERS ====================
urlInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter" && !isDownloading) {
        startDownload();
    }
});

// Auto-load history count on page load
updateHistoryBadge();

console.log("✅ Script loaded successfully");