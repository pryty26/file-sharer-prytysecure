// DOM Elements
const uploadZone = document.getElementById('uploadZone');
const fileInput = document.getElementById('fileInput');
const browseBtn = document.getElementById('browseBtn');
const uploadProgress = document.getElementById('uploadProgress');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const urlInput = document.getElementById('urlInput');
const downloadBtn = document.getElementById('downloadBtn');
const filesGrid = document.querySelector('.files-grid');
const toast = document.getElementById('toast');
const toastMessage = document.getElementById('toastMessage');

// Sample files data
const sampleFiles = [
    {
        id: 1,
        name: 'Project_Report_2024.pdf',
        type: 'pdf',
        size: '2.4 MB',
        uploaded: '3 days ago',
        icon: 'fas fa-file-pdf'
    },
    {
        id: 2,
        name: 'Design_Mockup_v3.png',
        type: 'image',
        size: '8.7 MB',
        uploaded: '1 week ago',
        icon: 'fas fa-file-image'
    },
    {
        id: 3,
        name: 'Product_Demo.mp4',
        type: 'video',
        size: '156 MB',
        uploaded: '2 weeks ago',
        icon: 'fas fa-file-video'
    },
    {
        id: 4,
        name: 'Source_Code.zip',
        type: 'archive',
        size: '45 MB',
        uploaded: '1 month ago',
        icon: 'fas fa-file-archive'
    }
];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    renderFiles();
    setupEventListeners();
});

// Event Listeners
function setupEventListeners() {
    // Upload zone click
    uploadZone.addEventListener('click', () => {
        fileInput.click();
    });

    // Browse button click
    browseBtn.addEventListener('click', () => {
        fileInput.click();
    });

    // File input change
    fileInput.addEventListener('change', handleFileSelect);

    // Upload zone drag and drop
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.style.borderColor = 'var(--color-accent-primary)';
        uploadZone.style.backgroundColor = 'rgba(16, 163, 127, 0.1)';
    });

    uploadZone.addEventListener('dragleave', () => {
        uploadZone.style.borderColor = 'var(--color-border)';
        uploadZone.style.backgroundColor = 'transparent';
    });

    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.style.borderColor = 'var(--color-border)';
        uploadZone.style.backgroundColor = 'transparent';
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            simulateUpload(files[0]);
        }
    });

    // Download button click
    downloadBtn.addEventListener('click', handleDownload);

    // URL input enter key
    urlInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleDownload();
        }
    });
}

// Handle file selection
function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        simulateUpload(files[0]);
    }
}

// Simulate file upload
function simulateUpload(file) {
    // Show progress bar
    uploadProgress.classList.remove('hidden');
    
    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.random() * 10;
        if (progress > 100) progress = 100;
        
        progressFill.style.width = `${progress}%`;
        progressText.textContent = `Uploading ${file.name}... ${Math.round(progress)}%`;
        
        if (progress === 100) {
            clearInterval(interval);
            
            // Add file to list
            const newFile = {
                id: sampleFiles.length + 1,
                name: file.name,
                type: getFileType(file.name),
                size: formatFileSize(file.size),
                uploaded: 'Just now',
                icon: getFileIcon(file.name)
            };
            
            sampleFiles.unshift(newFile);
            renderFiles();
            
            // Show success message
            setTimeout(() => {
                uploadProgress.classList.add('hidden');
                progressFill.style.width = '0%';
                showToast(`${file.name} uploaded successfully!`);
                fileInput.value = '';
            }, 500);
        }
    }, 200);
}

// Handle download from URL
function handleDownload() {
    const url = urlInput.value.trim();
    
    if (!url) {
        showToast('Please enter a valid URL', 'error');
        return;
    }
    
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
        showToast('Please enter a valid URL starting with http:// or https://', 'error');
        return;
    }
    
    // Simulate download
    showToast('Starting download...');
    
    // Reset input after delay
    setTimeout(() => {
        urlInput.value = '';
        showToast('Download completed!');
    }, 2000);
}

// Render files grid
function renderFiles() {
    filesGrid.innerHTML = '';
    
    sampleFiles.forEach(file => {
        const fileCard = createFileCard(file);
        filesGrid.appendChild(fileCard);
    });
}

// Create file card element
function createFileCard(file) {
    const card = document.createElement('div');
    card.className = 'file-card';
    card.innerHTML = `
        <div class="file-header">
            <i class="${file.icon} file-icon"></i>
            <div class="file-info">
                <h4 class="file-name">${file.name}</h4>
                <p class="file-meta">${file.size} • ${file.uploaded}</p>
            </div>
        </div>
        <div class="file-actions">
            <button class="btn btn-outline btn-sm copy-link" data-id="${file.id}">
                <i class="fas fa-copy"></i> Copy Link
            </button>
            <button class="btn btn-outline btn-sm delete-file" data-id="${file.id}">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    `;
    
    // Add event listeners to buttons
    const copyBtn = card.querySelector('.copy-link');
    const deleteBtn = card.querySelector('.delete-file');
    
    copyBtn.addEventListener('click', () => copyFileLink(file.id));
    deleteBtn.addEventListener('click', () => deleteFile(file.id));
    
    return card;
}

// Copy file link to clipboard
function copyFileLink(fileId) {
    const file = sampleFiles.find(f => f.id === fileId);
    if (file) {
        const link = `https://filedrop.example.com/file/${fileId}`;
        navigator.clipboard.writeText(link)
            .then(() => {
                showToast(`Link copied: ${link}`);
            })
            .catch(() => {
                showToast('Failed to copy link', 'error');
            });
    }
}

// Delete file
function deleteFile(fileId) {
    const index = sampleFiles.findIndex(f => f.id === fileId);
    if (index !== -1) {
        sampleFiles.splice(index, 1);
        renderFiles();
        showToast('File deleted');
    }
}

// Show toast notification
function showToast(message, type = 'success') {
    toastMessage.textContent = message;
    
    // Set icon based on type
    const icon = toast.querySelector('.toast-icon');
    if (type === 'error') {
        icon.className = 'fas fa-exclamation-circle toast-icon';
        icon.style.color = '#ff6b6b';
    } else {
        icon.className = 'fas fa-check-circle toast-icon';
        icon.style.color = 'var(--color-accent-primary)';
    }
    
    toast.classList.remove('hidden');
    
    // Auto hide after 3 seconds
    setTimeout(() => {
        toast.classList.add('hidden');
    }, 3000);
}

// Helper functions
function getFileType(filename) {
    const ext = filename.split('.').pop().toLowerCase();
    if (['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(ext)) return 'image';
    if (['pdf', 'doc', 'docx', 'txt'].includes(ext)) return 'document';
    if (['mp4', 'mov', 'avi', 'mkv'].includes(ext)) return 'video';
    if (['zip', 'rar', '7z'].includes(ext)) return 'archive';
    return 'file';
}

function getFileIcon(filename) {
    const type = getFileType(filename);
    switch (type) {
        case 'image': return 'fas fa-file-image';
        case 'document': return 'fas fa-file-pdf';
        case 'video': return 'fas fa-file-video';
        case 'archive': return 'fas fa-file-archive';
        default: return 'fas fa-file';
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Add some CSS for file cards
const style = document.createElement('style');
style.textContent = `
    .file-card {
        background-color: var(--color-bg-card);
        border: 1px solid var(--color-border);
        border-radius: var(--radius-md);
        padding: var(--spacing-md);
        transition: var(--transition-normal);
        animation: fadeIn 0.5s ease;
    }
    
    .file-card:hover {
        border-color: var(--color-accent-primary);
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
    }
    
    .file-header {
        display: flex;
        align-items: center;
        gap: var(--spacing-sm);
        margin-bottom: var(--spacing-md);
    }
    
    .file-icon {
        font-size: 2rem;
        color: var(--color-accent-primary);
    }
    
    .file-info {
        flex: 1;
    }
    
    .file-name {
        font-size: 0.95rem;
        font-weight: 500;
        margin-bottom: 4px;
        word-break: break-all;
    }
    
    .file-meta {
        font-size: 0.8rem;
        color: var(--color-text-tertiary);
    }
    
    .file-actions {
        display: flex;
        gap: var(--spacing-xs);
    }
    
    .btn-sm {
        padding: 0.5rem 1rem;
        font-size: 0.85rem;
    }
`;
document.head.appendChild(style);