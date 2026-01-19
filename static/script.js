// ================== Theme Toggle ==================
function toggleTheme() {
    const html = document.documentElement;
    const themeIcon = document.getElementById('themeIcon');
    const currentTheme = html.getAttribute('data-theme');

    if (currentTheme === 'light') {
        html.removeAttribute('data-theme');
        themeIcon.textContent = '🌙';
        localStorage.setItem('theme', 'dark');
        showToast('🌙 Chế độ tối', 'info');
    } else {
        html.setAttribute('data-theme', 'light');
        themeIcon.textContent = '☀️';
        localStorage.setItem('theme', 'light');
        showToast('☀️ Chế độ sáng', 'info');
    }
}

// Load saved theme on page load
(function loadTheme() {
    const savedTheme = localStorage.getItem('theme');
    const themeIcon = document.getElementById('themeIcon');

    if (savedTheme === 'light') {
        document.documentElement.setAttribute('data-theme', 'light');
        if (themeIcon) themeIcon.textContent = '☀️';
    }
})();

// ================== Socket.IO Setup ==================
const socket = io();

// ================== Clipboard & Input ==================
async function pasteFromClipboard() {
    try {
        const text = await navigator.clipboard.readText();
        urlInput.value = text;
        showToast('✅ Đã dán từ Clipboard', 'success');
        urlInput.focus();
    } catch (err) {
        showToast('❌ Không thể truy cập Clipboard', 'error');
    }
}

function clearInput() {
    urlInput.value = '';
    showToast('🗑 Đã xóa nội dung', 'info');
    urlInput.focus();
}

function startQueueDownload() {
    socket.emit('start_queue_download');
    // Switch to status view if needed, or show toast
    showToast('🚀 Đang bắt đầu tải hàng đợi...', 'info');
}

// ================== State ==================
let queue = [];
let isDownloading = false;
let allHistory = [];
let currentFilter = 'all';

// ================== DOM Elements ==================
const urlInput = document.getElementById('url');
const formatSelect = document.getElementById('format');
const qualitySelect = document.getElementById('quality');
const addQueueBtn = document.getElementById('addQueueBtn');
const downloadBtn = document.getElementById('downloadBtn');
const btnText = document.getElementById('btnText');
const queueList = document.getElementById('queueList');
const queueCount = document.getElementById('queueBadge'); // Fixed: was 'queueCount' which doesn't exist
const clearQueueBtn = document.getElementById('clearQueueBtn');
const progressContainer = document.getElementById('progressContainer');
const statusText = document.getElementById('status');
const percentText = document.getElementById('percent');
const progressBar = document.getElementById('progressBar');
const videoTitle = document.getElementById('videoTitle');
const videoPreview = document.getElementById('videoPreview');

// ================== Socket Events ==================
socket.on('connect', () => {
    console.log('✅ Connected to server');
});

socket.on('connected', (data) => {
    console.log('🚀 Server ready:', data);
    updateHistoryBadge();
});

// --- Queue Events ---
socket.on('queue_updated', (data) => {
    queue = data.queue;
    renderQueue();
});

socket.on('download_started', (data) => {
    isDownloading = true;
    updateButtons();
    progressContainer.style.display = 'block';
    statusText.textContent = 'Đang phân tích video...';
    percentText.textContent = '0%';
    progressBar.style.width = '0%';
    downloadBtn.classList.add('downloading');
});

socket.on('status', (data) => {
    statusText.textContent = data.msg || 'Đang xử lý...';
    if (data.percent) {
        percentText.textContent = data.percent;
    }
});

socket.on('info', (data) => {
    if (data.title) {
        videoTitle.textContent = `🎬 ${data.title}`;
        videoTitle.style.display = 'block';
    }
});

socket.on('progress', (data) => {
    if (data.percent) {
        percentText.textContent = data.percent;
        const percentNum = parseFloat(data.percent);
        progressBar.style.width = `${percentNum}%`;
    }
    if (data.msg) {
        statusText.textContent = data.msg;
    }
});

socket.on('queue_item_progress', (data) => {
    const item = document.querySelector(`[data-id="${data.id}"] .queue-item-progress`);
    if (item) {
        item.textContent = data.percent;
    }
});

socket.on('done', (data) => {
    statusText.textContent = data.msg || '✅ Tải hoàn tất!';
    percentText.textContent = '100%';
    progressBar.style.width = '100%';

    // Celebrate animation
    progressBar.style.background = 'linear-gradient(135deg, #10b981, #059669)';

    // Refresh history badge
    setTimeout(updateHistoryBadge, 1000);

    setTimeout(() => {
        if (queue.filter(q => q.status === 'pending').length === 0) {
            isDownloading = false;
            updateButtons();
            downloadBtn.classList.remove('downloading');
            progressBar.style.background = '';
        }
    }, 2000);
});

socket.on('error', (data) => {
    statusText.textContent = `❌ ${data.msg}`;
    progressBar.style.width = '0%';
    progressBar.style.background = 'linear-gradient(135deg, #ef4444, #dc2626)';
});

socket.on('all_downloads_complete', () => {
    isDownloading = false;
    updateButtons();
    downloadBtn.classList.remove('downloading');
    statusText.textContent = '🎉 Đã tải xong tất cả video!';
    showToast('🎉 Đã tải xong tất cả video!', 'success');

    // Reset progress bar color after some time
    setTimeout(() => {
        progressBar.style.background = '';
        // Hide progress container when all done
        setTimeout(() => {
            progressContainer.style.display = 'none';
        }, 2000);
    }, 3000);

    // Refresh history if active
    if (document.getElementById('historyTab').classList.contains('active')) {
        loadHistory();
    }
});

socket.on('item_completed', (data) => {
    if (data.success) {
        showToast(`✅ Đã tải xong: ${data.title}`, 'success');
    } else {
        showToast(`❌ Lỗi tải: ${data.title}`, 'error');
    }
});

socket.on("video_info", (data) => {
    displayVideoPreview(data);
});

// ================== Queue Functions ==================
function parseUrls(text) {
    // Handle both Windows (\r\n) and Unix (\n) line endings
    return text.split(/\r?\n/)
        .map(url => url.trim())
        .filter(url => url.length > 0 && (url.startsWith('http://') || url.startsWith('https://')));
}

function addToQueue() {
    const text = urlInput.value.trim();
    if (!text) {
        showToast('⚠️ Vui lòng nhập ít nhất 1 URL!', 'warning');
        shakeElement(urlInput);
        return;
    }

    const urls = parseUrls(text);
    if (urls.length === 0) {
        showToast('❌ Không tìm thấy URL hợp lệ!', 'error');
        shakeElement(urlInput);
        return;
    }

    const format = formatSelect.value;
    const quality = qualitySelect.value;

    socket.emit('add_to_queue', {
        urls: urls,
        format: format,
        quality: quality
    });

    // Clear input with animation
    urlInput.value = '';
    showToast(`✅ Đã thêm ${urls.length} video vào hàng đợi!`, 'success');

    // Animate the add button
    addQueueBtn.style.transform = 'scale(0.95)';
    setTimeout(() => {
        addQueueBtn.style.transform = '';
    }, 150);
}

function removeFromQueue(id) {
    socket.emit('remove_from_queue', { id: id });
}

function clearQueue() {
    if (queue.length === 0) return;
    if (confirm('🗑️ Bạn có chắc muốn xóa tất cả video khỏi hàng đợi?')) {
        socket.emit('clear_queue');
        showToast('🗑️ Đã xóa tất cả video khỏi hàng đợi', 'info');
    }
}

function startDownload() {
    if (queue.length === 0) {
        const text = urlInput.value.trim();
        if (text) {
            const urls = parseUrls(text);
            if (urls.length > 0) {
                const format = formatSelect.value;
                const quality = qualitySelect.value;
                socket.emit('add_to_queue', { urls: urls, format: format, quality: quality });
                urlInput.value = '';
                setTimeout(() => {
                    socket.emit('start_queue_download');
                }, 300);
                return;
            }
        }
        showToast('⚠️ Hàng đợi trống! Thêm video trước.', 'warning');
        return;
    }

    socket.emit('start_queue_download');
}

function renderQueue() {
    // Animate count change
    const oldCount = parseInt(queueCount.textContent);
    const newCount = queue.length;

    if (oldCount !== newCount) {
        queueCount.style.animation = 'none';
        setTimeout(() => {
            queueCount.style.animation = 'countPop 0.3s ease';
        }, 10);
    }

    queueCount.textContent = newCount.toString();
    const queueBadge = document.getElementById('queueBadge');
    if (queueBadge) queueBadge.textContent = newCount.toString();

    if (queue.length === 0) {
        queueList.innerHTML = `
            <div class="queue-empty">
                <div class="queue-empty-icon">📭</div>
                <div>Hàng đợi trống</div>
                <div style="font-size: 0.8rem; margin-top: 4px; opacity: 0.7;">Thêm video để bắt đầu tải</div>
            </div>
        `;
        return;
    }

    queueList.innerHTML = queue.map((item, index) => `
        <div class="queue-item ${item.status}" data-id="${item.id}" style="animation-delay: ${index * 0.05}s">
            <div class="queue-item-status"></div>
            <div class="queue-item-info">
                <div class="queue-item-title">${item.title || 'Đang lấy thông tin...'}</div>
                <div class="queue-item-url">${truncateUrl(item.url)}</div>
            </div>
            <div class="queue-item-progress">${item.progress || ''}</div>
            ${item.status === 'pending' ? `
                <button class="queue-item-remove" onclick="removeFromQueue('${item.id}')" title="Xóa khỏi hàng đợi">×</button>
            ` : ''}
        </div>
    `).join('');
}

function truncateUrl(url) {
    if (url.length > 50) {
        return url.substring(0, 47) + '...';
    }
    return url;
}

function updateButtons() {
    downloadBtn.disabled = isDownloading;
    addQueueBtn.disabled = isDownloading;

    if (isDownloading) {
        btnText.innerHTML = `<span class="loading-dots"><span></span><span></span><span></span></span> ĐANG TẢI`;
    } else {
        btnText.innerHTML = '⬇️ TẢI XUỐNG';
    }
}

// ================== Preview Functions ==================
let pendingPreviews = 0;
let previewResults = [];

function previewVideo() {
    const urls = parseUrls(urlInput.value.trim());

    if (urls.length === 0) {
        showToast("⚠️ Vui lòng nhập URL video!", 'warning');
        return;
    }

    // Reset and show loading state
    const previewContainer = document.getElementById('videoPreviewContainer');
    const previewList = document.getElementById('videoPreviewList');
    const previewCount = document.getElementById('previewCount');

    previewResults = [];
    pendingPreviews = urls.length;
    previewList.innerHTML = '<div class="preview-loading">🔍 Đang lấy thông tin ' + urls.length + ' video...</div>';
    previewContainer.style.display = 'block';
    previewCount.textContent = `0/${urls.length} video`;

    // Fetch info for ALL URLs
    urls.forEach((url, index) => {
        socket.emit("get_video_info", { url, index });
    });

    showToast(`🔍 Đang lấy thông tin ${urls.length} video...`, 'info');
}

function displayVideoPreview(data) {
    const previewContainer = document.getElementById('videoPreviewContainer');
    const previewList = document.getElementById('videoPreviewList');
    const previewCount = document.getElementById('previewCount');

    // Store the result
    previewResults.push(data);
    pendingPreviews--;

    // Clear loading message on first result
    if (previewResults.length === 1) {
        previewList.innerHTML = '';
    }

    // Create a preview card for this video
    const card = document.createElement('div');
    card.className = 'video-preview-card';

    const thumbnailHtml = data.thumbnail
        ? `<img src="${data.thumbnail}" alt="Thumbnail" class="preview-thumbnail" onerror="this.style.display='none'">`
        : '<div class="preview-thumbnail-placeholder">🎬</div>';

    const formatsHtml = (data.formats && data.formats.length > 0)
        ? data.formats.map(f => `<span class="format-badge">${f.quality} (${f.filesize})</span>`).join('')
        : '';

    card.innerHTML = `
        ${thumbnailHtml}
        <div class="preview-card-info">
            <h4 class="preview-card-title">${data.title || 'Unknown'}</h4>
            <div class="preview-card-meta">
                <span>📱 ${data.platform || 'Unknown'}</span>
                <span>⏱️ ${data.duration || 'N/A'}</span>
                <span>👁️ ${data.view_count || 'N/A'}</span>
            </div>
            <div class="preview-card-formats">${formatsHtml}</div>
        </div>
    `;

    previewList.appendChild(card);

    // Update count
    const totalUrls = previewResults.length + pendingPreviews;
    previewCount.textContent = `${previewResults.length}/${totalUrls} video`;

    // Show toast when all done
    if (pendingPreviews === 0) {
        showToast(`✅ Đã lấy thông tin ${previewResults.length} video!`, 'success');
    }
}

function closeAllPreviews() {
    const previewContainer = document.getElementById('videoPreviewContainer');
    previewContainer.style.display = 'none';
    previewResults = [];
    pendingPreviews = 0;
}


// ================== History Functions ==================
// ================== History Functions ==================
function switchTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    document.querySelectorAll('.nav-item').forEach(btn => {
        btn.classList.remove('active');
    });

    document.getElementById(tabName + 'Tab').classList.add('active');

    // Update active nav item
    const navItems = document.querySelectorAll('.nav-item');
    if (tabName === 'download') navItems[0].classList.add('active');
    if (tabName === 'queue') navItems[1].classList.add('active');
    if (tabName === 'history') navItems[2].classList.add('active');

    if (tabName === 'history') {
        loadHistory();
    }
}

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

async function updateHistoryBadge() {
    try {
        const response = await fetch('/api/history');
        const history = await response.json();
        allHistory = history;
        const badge = document.getElementById('historyBadge');
        if (badge) {
            badge.textContent = history.length;
        }
    } catch (e) { console.log("Badge update failed", e); }
}

async function copyUrl(url) {
    try {
        await navigator.clipboard.writeText(url);
        showToast('✅ Đã copy URL vào clipboard!', 'success');
    } catch (err) {
        showToast('❌ Không thể copy URL', 'error');
    }
}

async function deleteHistoryItem(id) {
    if (!confirm('Bạn có chắc muốn xóa mục này?')) return;

    try {
        await fetch(`/api/delete/${id}`, { method: 'DELETE' });
        showToast('✅ Đã xóa!', 'success');
        loadHistory();
    } catch (error) {
        showToast('❌ Lỗi khi xóa', 'error');
    }
}

async function clearHistoryRecord() {
    if (!confirm('⚠️ Bạn có chắc muốn xóa toàn bộ lịch sử?')) return;

    try {
        await fetch('/api/clear-history', { method: 'POST' });
        showToast('✅ Đã xóa toàn bộ lịch sử', 'success');
        loadHistory();
    } catch (error) {
        showToast('❌ Lỗi khi xóa', 'error');
    }
}

// ================== Search & Filter for History ==================
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

function filterHistory(filter) {
    currentFilter = filter;

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

        showToast('✅ Đã export lịch sử thành công!', 'success');
    } catch (error) {
        showToast('❌ Lỗi khi export', 'error');
    }
}

// ================== Toast Notifications ==================
function showToast(message, type = 'info') {
    // Remove existing toasts
    const existingToast = document.querySelector('.toast');
    if (existingToast) {
        existingToast.remove();
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 24px;
        left: 50%;
        transform: translateX(-50%) translateY(100px);
        padding: 14px 24px;
        background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : type === 'warning' ? '#f59e0b' : '#6366f1'};
        color: white;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.9rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        z-index: 9999;
        transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    `;

    document.body.appendChild(toast);

    // Animate in
    requestAnimationFrame(() => {
        toast.style.transform = 'translateX(-50%) translateY(0)';
    });

    // Animate out and remove
    setTimeout(() => {
        toast.style.transform = 'translateX(-50%) translateY(100px)';
        setTimeout(() => toast.remove(), 400);
    }, 3000);
}

// ================== Shake Animation ==================
function shakeElement(element) {
    element.style.animation = 'shake 0.5s ease';
    setTimeout(() => {
        element.style.animation = '';
    }, 500);
}

// Add shake keyframes
const style = document.createElement('style');
style.textContent = `
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        20% { transform: translateX(-8px); }
        40% { transform: translateX(8px); }
        60% { transform: translateX(-4px); }
        80% { transform: translateX(4px); }
    }
`;
document.head.appendChild(style);

// ================== Keyboard Shortcuts ==================
urlInput.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'Enter') {
        // Ctrl+Enter: Add to queue
        e.preventDefault();
        addToQueue();
    } else if (e.key === 'Enter' && !e.ctrlKey && !e.shiftKey) {
        // Enter (without modifiers): Download immediately
        // Shift+Enter allows normal line break in textarea
        e.preventDefault();
        startDownload();
    }
});

// ================== Focus Effects ==================
urlInput.addEventListener('focus', () => {
    urlInput.parentElement.style.transform = 'scale(1.01)';
});

urlInput.addEventListener('blur', () => {
    urlInput.parentElement.style.transform = 'scale(1)';
});

// ================== Initial Render ==================
renderQueue();

// ================== Welcome Message ==================
setTimeout(() => {
    showToast('👋 Chào mừng! Paste URLs và bắt đầu tải video.', 'info');
}, 1000);


