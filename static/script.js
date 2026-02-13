// Global variables
let mediaRecorder;
let audioChunks = [];
let isRecording = false;
let recordingTimer;
let recordingStartTime;
let ttsHistory = JSON.parse(localStorage.getItem('ttsHistory')) || [];
let sttHistory = JSON.parse(localStorage.getItem('sttHistory')) || [];

// DOM elements
const ttsSection = document.getElementById('tts-section');
const sttSection = document.getElementById('stt-section');
const ttsModeBtn = document.getElementById('tts-mode-btn');
const sttModeBtn = document.getElementById('stt-mode-btn');
const speakBtn = document.getElementById('speak-btn');
const startRecordingBtn = document.getElementById('start-recording-btn');
const stopRecordingBtn = document.getElementById('stop-recording-btn');
const ttsStatus = document.getElementById('tts-status');
const recordingStatus = document.getElementById('recording-status');
const sttResult = document.getElementById('stt-result');
const clearHistoryBtn = document.getElementById('clear-history-btn');
const ttsHistoryContent = document.getElementById('tts-history');
const sttHistoryContent = document.getElementById('stt-history');

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    setupModeButtons();
    setupTTS();
    setupSTT();
    setupHistory();
    setupUIEnhancements();
    loadHistory();
});

// Mode switching
function setupModeButtons() {
    ttsModeBtn.addEventListener('click', function() {
        showSection('tts');
        setActiveButton(ttsModeBtn);
    });

    sttModeBtn.addEventListener('click', function() {
        showSection('stt');
        setActiveButton(sttModeBtn);
    });
}

function showSection(mode) {
    if (mode === 'tts') {
        ttsSection.classList.add('active');
        sttSection.classList.remove('active');
    } else {
        sttSection.classList.add('active');
        ttsSection.classList.remove('active');
    }
}

function setActiveButton(activeBtn) {
    document.querySelectorAll('.mode-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    activeBtn.classList.add('active');
}

// Text to Speech functionality
function setupTTS() {
    speakBtn.addEventListener('click', function() {
        const text = document.getElementById('tts-text').value.trim();
        const srcLanguage = document.getElementById('tts-src-language').value;
        const tgtLanguage = document.getElementById('tts-language').value;

        if (!text) {
            showStatus(ttsStatus, 'Please enter some text to speak.', 'error');
            return;
        }

        speakText(text, srcLanguage, tgtLanguage);
    });
}

async function speakText(text, srcLanguage, tgtLanguage) {
    try {
        speakBtn.disabled = true;
        
        // Show loading spinner
        const btnText = speakBtn.querySelector('.btn-text');
        const spinner = speakBtn.querySelector('.spinner');
        btnText.style.display = 'none';
        spinner.style.display = 'inline-flex';
        
        showStatus(ttsStatus, 'Generating speech...', 'info');
        
        const gender = document.getElementById('tts-gender').value;

        const response = await fetch('/tts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: text,
                src_language: srcLanguage,
                tgt_language: tgtLanguage,
                gender: gender
            })
        });

        const data = await response.json();

        if (response.ok) {
            let message = 'Speech generated successfully!';
            if (data.voice_used) {
                message += ` (Voice: ${data.voice_used})`;
            }
            if (data.warning) {
                message += ` ⚠️ ${data.warning}`;
            }
            if (data.translated_text && data.translated_text !== text) {
                message += ` | Translated: "${data.translated_text}"`;
            }
            showStatus(ttsStatus, message, 'success');
            
            // Show audio preview if audio_url is available
            if (data.audio_url) {
                showAudioPreview(data.audio_url, data.audio_filename);
            }
            
            // Add to history
            addToTTSHistory({
                originalText: text,
                translatedText: data.translated_text,
                srcLanguage: srcLanguage,
                tgtLanguage: tgtLanguage,
                voice: data.voice_used,
                gender: data.gender_used || 'any',
                timestamp: new Date().toLocaleString(),
                audioUrl: data.audio_url,
                audioFilename: data.audio_filename
            });
        } else {
            showStatus(ttsStatus, data.error || 'Error generating speech', 'error');
        }
    } catch (error) {
        showStatus(ttsStatus, 'Network error: ' + error.message, 'error');
    } finally {
        speakBtn.disabled = false;
        
        // Hide loading spinner
        const btnText = speakBtn.querySelector('.btn-text');
        const spinner = speakBtn.querySelector('.spinner');
        btnText.style.display = 'inline';
        spinner.style.display = 'none';
    }
}

// Show audio preview with player and download button
function showAudioPreview(audioUrl, audioFilename) {
    const audioPreviewContainer = document.getElementById('audio-preview-container');
    const audioPlayer = document.getElementById('audio-player');
    const audioSource = document.getElementById('audio-source');
    const downloadBtn = document.getElementById('download-audio-btn');
    const replayBtn = document.getElementById('replay-audio-btn');
    const audioFilenameLabel = document.getElementById('audio-filename');
    
    // Set audio source
    audioSource.src = audioUrl;
    audioPlayer.load();
    
    // Show preview container
    audioPreviewContainer.style.display = 'block';

    if (audioFilenameLabel) {
        audioFilenameLabel.textContent = audioFilename ? `File: ${audioFilename}` : 'File: tts_audio.wav';
    }
    
    // Setup download button
    downloadBtn.onclick = function() {
        downloadAudio(audioUrl, audioFilename);
    };
    
    // Setup replay button
    replayBtn.onclick = function() {
        audioPlayer.currentTime = 0;
        audioPlayer.play();
    };
    
    // Auto scroll to preview
    audioPreviewContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Download audio file
function downloadAudio(audioUrl, audioFilename) {
    const link = document.createElement('a');
    link.href = audioUrl;
    link.download = audioFilename || 'tts_audio.wav';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Speech to Text functionality
function setupSTT() {
    startRecordingBtn.addEventListener('click', startRecording);
    stopRecordingBtn.addEventListener('click', stopRecording);
}

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
            audio: {
                sampleRate: 16000,
                channelCount: 1,
                echoCancellation: true,
                noiseSuppression: true,
                autoGainControl: true,
                googEchoCancellation: true,
                googAutoGainControl: true,
                googNoiseSuppression: true,
                googHighpassFilter: true
            }
        });
        
        // Select best available audio format for Whisper
        let options = {};
        const preferredTypes = [
            'audio/webm;codecs=opus',
            'audio/webm',
            'audio/ogg;codecs=opus',
            'audio/ogg',
            'audio/wav'
        ];
        for (const type of preferredTypes) {
            if (MediaRecorder.isTypeSupported(type)) {
                options.mimeType = type;
                break;
            }
        }
        
        mediaRecorder = new MediaRecorder(stream, options);
        audioChunks = [];
        
        mediaRecorder.ondataavailable = function(event) {
            audioChunks.push(event.data);
        };
        
        mediaRecorder.onstop = function() {
            const mimeType = mediaRecorder.mimeType || 'audio/wav';
            const audioBlob = new Blob(audioChunks, { type: mimeType });
            sendAudioForRecognition(audioBlob);
        };
        
        mediaRecorder.start();
        isRecording = true;
        
        // Update UI
        startRecordingBtn.disabled = true;
        stopRecordingBtn.disabled = false;
        showStatus(recordingStatus, 'Recording... Speak now!', 'info');
        recordingStatus.classList.add('recording');
        
        // Show recording indicator
        const indicator = document.getElementById('recording-indicator');
        if (indicator) indicator.classList.add('active');
        
        // Start recording timer
        startRecordingTimer();
        
    } catch (error) {
        if (error.name === 'NotAllowedError') {
            showStatus(recordingStatus, 'Microphone access denied. Please allow microphone access and try again.', 'error');
        } else {
            showStatus(recordingStatus, 'Error accessing microphone: ' + error.message, 'error');
        }
    }
}

function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
        isRecording = false;
        
        // Update UI
        startRecordingBtn.disabled = false;
        stopRecordingBtn.disabled = true;
        showStatus(recordingStatus, 'Processing audio...', 'info');
        recordingStatus.classList.remove('recording');
        
        // Hide recording indicator
        const indicator = document.getElementById('recording-indicator');
        if (indicator) indicator.classList.remove('active');
        
        // Stop recording timer
        stopRecordingTimer();
    }
}

async function sendAudioForRecognition(audioBlob) {
    try {
        const language = document.getElementById('stt-language').value;
        const formData = new FormData();
        const mimeType = audioBlob.type || '';
        let ext = 'webm';
        if (mimeType.includes('wav')) {
            ext = 'wav';
        } else if (mimeType.includes('ogg')) {
            ext = 'ogg';
        }
        formData.append('audio', audioBlob, `recording.${ext}`);
        formData.append('language', language);

        const response = await fetch('/stt', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            sttResult.value = data.text;
            showStatus(recordingStatus, 'Speech recognized successfully!', 'success');
            
            // Add to history
            addToSTTHistory({
                recognizedText: data.text,
                language: language,
                timestamp: new Date().toLocaleString()
            });
        } else {
            showStatus(recordingStatus, data.error || 'Error recognizing speech', 'error');
        }
    } catch (error) {
        showStatus(recordingStatus, 'Network error: ' + error.message, 'error');
    }
}

// Utility function to show status messages
function showStatus(element, message, type) {
    element.textContent = message;
    element.className = 'status ' + type;
    
    // Clear status after 5 seconds for success messages
    if (type === 'success') {
        setTimeout(() => {
            element.textContent = '';
            element.className = 'status';
        }, 5000);
    }
}

// History functionality
function setupHistory() {
    // History tab switching
    document.querySelectorAll('.history-tab').forEach(tab => {
        tab.addEventListener('click', function() {
            const targetTab = this.dataset.tab;
            
            // Update active tab
            document.querySelectorAll('.history-tab').forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            // Update active content
            document.querySelectorAll('.history-content').forEach(content => {
                content.classList.remove('active');
            });
            document.getElementById(targetTab).classList.add('active');
        });
    });
    
    // Clear history
    clearHistoryBtn.addEventListener('click', function() {
        if (confirm('Are you sure you want to clear all history?')) {
            ttsHistory = [];
            sttHistory = [];
            localStorage.removeItem('ttsHistory');
            localStorage.removeItem('sttHistory');
            loadHistory();
        }
    });
}

function addToTTSHistory(item) {
    ttsHistory.unshift(item); // Add to beginning
    if (ttsHistory.length > 50) ttsHistory.pop(); // Keep only last 50
    localStorage.setItem('ttsHistory', JSON.stringify(ttsHistory));
    loadTTSHistory();
}

function addToSTTHistory(item) {
    sttHistory.unshift(item); // Add to beginning
    if (sttHistory.length > 50) sttHistory.pop(); // Keep only last 50
    localStorage.setItem('sttHistory', JSON.stringify(sttHistory));
    loadSTTHistory();
}

function loadHistory() {
    loadTTSHistory();
    loadSTTHistory();
}

function loadTTSHistory() {
    ttsHistoryContent.innerHTML = '';
    
    if (ttsHistory.length === 0) {
        ttsHistoryContent.innerHTML = '<p style="text-align: center; color: #6c757d; padding: 20px;">No TTS history yet</p>';
        return;
    }
    
    ttsHistory.forEach((item, index) => {
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        const langDisplay = item.srcLanguage && item.tgtLanguage ? `${item.srcLanguage} → ${item.tgtLanguage}` : (item.language || 'N/A');
        
        let audioButtons = '';
        if (item.audioUrl && item.audioFilename) {
            audioButtons = `
                <div class="history-audio-actions">
                    <button class="play-history-audio-btn" data-audio-url="${item.audioUrl}" data-audio-filename="${item.audioFilename}" title="Play audio">
                        <i class="fas fa-play"></i>
                    </button>
                    <button class="download-history-audio-btn" data-audio-url="${item.audioUrl}" data-audio-filename="${item.audioFilename}" title="Download audio">
                        <i class="fas fa-download"></i>
                    </button>
                </div>
            `;
        }
        
        historyItem.innerHTML = `
            <button class="copy-history-btn" data-index="${index}" data-type="tts" title="Copy text">
                <i class="fas fa-copy"></i> Copy
            </button>
            <div class="history-item-header">
                <span class="history-time">${item.timestamp}</span>
                <span class="history-language">${langDisplay}</span>
            </div>
            <div class="history-text">
                <strong>Original:</strong> ${item.originalText}<br>
                ${item.translatedText !== item.originalText ? `<strong>Translated:</strong> ${item.translatedText}<br>` : ''}
                <small><strong>Voice:</strong> ${item.voice}${item.gender ? ` (${item.gender})` : ''}</small>
            </div>
            ${audioButtons}
        `;
        ttsHistoryContent.appendChild(historyItem);
    });
    
    // Add copy functionality to history items
    document.querySelectorAll('.copy-history-btn[data-type="tts"]').forEach(btn => {
        btn.addEventListener('click', async function() {
            const index = this.dataset.index;
            const item = ttsHistory[index];
            const textToCopy = item.translatedText || item.originalText;
            
            try {
                await navigator.clipboard.writeText(textToCopy);
                this.classList.add('copied');
                this.innerHTML = '<i class="fas fa-check"></i> Copied';
                setTimeout(() => {
                    this.classList.remove('copied');
                    this.innerHTML = '<i class="fas fa-copy"></i> Copy';
                }, 2000);
            } catch (err) {
                console.error('Failed to copy text:', err);
            }
        });
    });
    
    // Add play functionality to history items
    document.querySelectorAll('.play-history-audio-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const audioUrl = this.dataset.audioUrl;
            const audioFilename = this.dataset.audioFilename;
            showAudioPreview(audioUrl, audioFilename);
        });
    });
    
    // Add download functionality to history items
    document.querySelectorAll('.download-history-audio-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const audioUrl = this.dataset.audioUrl;
            const audioFilename = this.dataset.audioFilename;
            downloadAudio(audioUrl, audioFilename);
        });
    });
}

function loadSTTHistory() {
    sttHistoryContent.innerHTML = '';
    
    if (sttHistory.length === 0) {
        sttHistoryContent.innerHTML = '<p style="text-align: center; color: #6c757d; padding: 20px;">No STT history yet</p>';
        return;
    }
    
    sttHistory.forEach((item, index) => {
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        historyItem.innerHTML = `
            <button class="copy-history-btn" data-index="${index}" data-type="stt" title="Copy text">
                <i class="fas fa-copy"></i> Copy
            </button>
            <div class="history-item-header">
                <span class="history-time">${item.timestamp}</span>
                <span class="history-language">${item.language}</span>
            </div>
            <div class="history-text">
                <strong>Recognized:</strong> ${item.recognizedText}
            </div>
        `;
        sttHistoryContent.appendChild(historyItem);
    });
    
    // Add copy functionality to history items
    document.querySelectorAll('.copy-history-btn[data-type="stt"]').forEach(btn => {
        btn.addEventListener('click', async function() {
            const index = this.dataset.index;
            const item = sttHistory[index];
            const textToCopy = item.recognizedText;
            
            try {
                await navigator.clipboard.writeText(textToCopy);
                this.classList.add('copied');
                this.innerHTML = '<i class="fas fa-check"></i> Copied';
                setTimeout(() => {
                    this.classList.remove('copied');
                    this.innerHTML = '<i class="fas fa-copy"></i> Copy';
                }, 2000);
            } catch (err) {
                console.error('Failed to copy:', err);
            }
        });
    });
}

// UI Enhancement Functions
function setupUIEnhancements() {
    setupCharacterCounter();
    setupClearButton();
    setupSampleText();
    setupCopyButtons();
    setupKeyboardShortcuts();
    setupTextareaAutoResize();
    setupRecordingIndicator();
}

// Character counter
function setupCharacterCounter() {
    const ttsText = document.getElementById('tts-text');
    const charCount = document.getElementById('char-count');
    const charCounter = document.querySelector('.char-counter');
    
    ttsText.addEventListener('input', function() {
        const length = this.value.length;
        charCount.textContent = length;
        
        // Add warning colors
        charCounter.classList.remove('warning', 'danger');
        if (length > 900) {
            charCounter.classList.add('danger');
        } else if (length > 750) {
            charCounter.classList.add('warning');
        }
    });
}

// Clear button
function setupClearButton() {
    const clearBtn = document.getElementById('clear-tts-btn');
    const ttsText = document.getElementById('tts-text');
    const charCount = document.getElementById('char-count');
    
    clearBtn.addEventListener('click', function() {
        ttsText.value = '';
        charCount.textContent = '0';
        document.querySelector('.char-counter').classList.remove('warning', 'danger');
        ttsText.focus();
    });
}

// Sample text button
function setupSampleText() {
    const sampleBtn = document.getElementById('sample-text-btn');
    const ttsText = document.getElementById('tts-text');
    
    const samples = [
        "Hello! Welcome to VoiceFlow, your AI-powered speech assistant.",
        "The quick brown fox jumps over the lazy dog.",
        "Technology is best when it brings people together.",
        "Artificial intelligence is transforming the way we communicate.",
        "Good morning! Have a wonderful day ahead."
    ];
    
    sampleBtn.addEventListener('click', function() {
        const randomSample = samples[Math.floor(Math.random() * samples.length)];
        ttsText.value = randomSample;
        ttsText.dispatchEvent(new Event('input'));
        ttsText.focus();
    });
}

// Copy buttons functionality
function setupCopyButtons() {
    // Copy STT result
    const copySTTBtn = document.getElementById('copy-stt-btn');
    const sttResult = document.getElementById('stt-result');
    
    copySTTBtn.addEventListener('click', async function() {
        const text = sttResult.value;
        if (!text) {
            showStatus(recordingStatus, 'No text to copy', 'error');
            return;
        }
        
        try {
            await navigator.clipboard.writeText(text);
            const icon = this.querySelector('i');
            const originalClass = icon.className;
            icon.className = 'fas fa-check';
            setTimeout(() => {
                icon.className = originalClass;
            }, 2000);
            showStatus(recordingStatus, 'Text copied to clipboard!', 'success');
        } catch (err) {
            showStatus(recordingStatus, 'Failed to copy text', 'error');
        }
    });
}

// Keyboard shortcuts
function setupKeyboardShortcuts() {
    const ttsText = document.getElementById('tts-text');
    
    // Ctrl+Enter to speak
    ttsText.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'Enter') {
            e.preventDefault();
            document.getElementById('speak-btn').click();
        }
    });
    
    // Escape to clear
    ttsText.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            e.preventDefault();
            document.getElementById('clear-tts-btn').click();
        }
    });
}

// Auto-resize textarea
function setupTextareaAutoResize() {
    const ttsText = document.getElementById('tts-text');
    
    ttsText.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 300) + 'px';
    });
}

// Recording indicator
function setupRecordingIndicator() {
    // Create recording indicator element
    const recordingControls = document.querySelector('.recording-controls');
    const indicator = document.createElement('div');
    indicator.className = 'recording-indicator';
    indicator.id = 'recording-indicator';
    indicator.innerHTML = '<div class="recording-dot"></div><span id="recording-timer">Recording: 0:00</span>';
    recordingControls.appendChild(indicator);
}

// Recording timer functions
function startRecordingTimer() {
    recordingStartTime = Date.now();
    recordingTimer = setInterval(updateRecordingTimer, 100);
}

function updateRecordingTimer() {
    const elapsed = Date.now() - recordingStartTime;
    const seconds = Math.floor(elapsed / 1000);
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    const timerElement = document.getElementById('recording-timer');
    if (timerElement) {
        timerElement.textContent = `Recording: ${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    }
}

function stopRecordingTimer() {
    if (recordingTimer) {
        clearInterval(recordingTimer);
        recordingTimer = null;
    }
}