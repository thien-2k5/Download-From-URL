// Initialize Socket.IO connection
const socket = io({
    transports: ['polling', 'websocket']
});

// DOM Elements
const urlInput = document.getElementById("url");
const formatSelect = document.getElementById("format");
const downloadBtn = document.getElementById("downloadBtn");
const btnText = document.getElementById("btnText");
const progressContainer = document.getElementById("progressContainer");
const statusText = document.getElementById("status");
const percentText = document.getElementById("percent");
const progressBar = document.getElementById("progressBar");
const videoTitleText = document.getElementById("videoTitle");
const speedText = document.getElementById("speed");
const etaText = document.getElementById("eta");
const filenameText = document.getElementById("filename");

let isDownloading = false;

// Socket.IO Events
socket.on("connect", () => {
    console.log("✅ Connected to server! Socket ID:", socket.id);
    statusText.textContent = "Đã kết nối với server";
});

socket.on("connected", (data) => {
    console.log("Server ready:", data.status);
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
        videoTitleText.textContent = `📹 ${data.title}`;
        videoTitleText.style.display = "block";
    }
    if (data.msg) {
        statusText.textContent = data.msg;
    }
});

socket.on("progress", (data) => {
    showProgress();
    
    // Update status
    if (data.status === "downloading") {
        statusText.textContent = "Đang tải xuống...";
        statusText.className = "status-text downloading";
    } else if (data.status === "processing") {
        statusText.textContent = data.msg || "Đang xử lý...";
        statusText.className = "status-text";
    }
    
    // Update percentage
    if (data.percent) {
        updatePercent(data.percent);
    }
    
    // Update speed
    if (data.speed) {
        speedText.textContent = data.speed;
    }
    
    // Update ETA
    if (data.eta) {
        etaText.textContent = data.eta;
    }
    
    // Update filename
    if (data.filename) {
        filenameText.textContent = `📄 ${data.filename}`;
        filenameText.style.display = "block";
    }
});

socket.on("done", (data) => {
    isDownloading = false;
    enableButton();
    
    statusText.textContent = "✅ Tải thành công!";
    statusText.className = "status-text success";
    updatePercent("100%");
    
    // Show success notification
    setTimeout(() => {
        alert("✅ " + data.msg);
    }, 300);
});

socket.on("error", (data) => {
    isDownloading = false;
    enableButton();
    showError(data.msg);
});

// Functions
function startDownload() {
    console.log("🚀 startDownload called");
    const url = urlInput.value.trim();
    const format = formatSelect.value;
    
    console.log("URL:", url);
    console.log("Format:", format);
    console.log("Socket connected:", socket.connected);
    
    if (!url) {
        alert("⚠️ Vui lòng nhập URL video!");
        urlInput.focus();
        return;
    }
    
    // Basic URL validation
    if (!url.startsWith("http://") && !url.startsWith("https://")) {
        alert("⚠️ URL không hợp lệ! Vui lòng nhập URL đầy đủ (bắt đầu bằng http:// hoặc https://)");
        urlInput.focus();
        return;
    }
    
    // Reset UI
    resetProgress();
    showProgress();
    disableButton();
    
    // Start download
    isDownloading = true;
    console.log("📤 Emitting start_download event...");
    socket.emit("start_download", { url, format });
    console.log("✅ Event emitted!");
}

function showProgress() {
    progressContainer.style.display = "block";
}

function hideProgress() {
    progressContainer.style.display = "none";
}

function resetProgress() {
    statusText.textContent = "Đang chuẩn bị...";
    statusText.className = "status-text";
    percentText.textContent = "0%";
    progressBar.style.width = "0%";
    videoTitleText.textContent = "";
    videoTitleText.style.display = "none";
}

function updatePercent(percentStr) {
    percentText.textContent = percentStr;
    
    // Extract number from percentage string
    const percentNum = parseFloat(percentStr.replace("%", ""));
    if (!isNaN(percentNum)) {
        const clampedPercent = Math.min(Math.max(percentNum, 0), 100);
        progressBar.style.width = clampedPercent + "%";
        
        // Change color when complete
        if (clampedPercent >= 100) {
            progressBar.style.background = "linear-gradient(90deg, #28a745 0%, #20c997 100%)";
        } else {
            progressBar.style.background = "linear-gradient(90deg, #667eea 0%, #764ba2 100%)";
        }
    }
}

function showError(message) {
    showProgress();
    statusText.textContent = "❌ Lỗi";
    statusText.className = "status-text error";
    videoTitleText.textContent = message;
    videoTitleText.style.display = "block";
    videoTitleText.style.background = "#ffe0e0";
    videoTitleText.style.borderLeft = "4px solid #dc3545";
    videoTitleText.style.color = "#dc3545";
    
    alert("❌ " + message);
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

// Enter key support
urlInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter" && !isDownloading) {
        startDownload();
    }
});

// Clear input on focus (first time)
let firstFocus = true;
urlInput.addEventListener("focus", () => {
    if (firstFocus && !urlInput.value) {
        firstFocus = false;
    }
});

console.log("✅ Script loaded successfully");