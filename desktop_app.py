"""
VoiceFlow Desktop Application
Embeds Flask server in a PyQt5 desktop application with system tray support
"""

import sys
import os
import threading
import socket
import urllib.request
from pathlib import Path

from PyQt5.QtWidgets import (QApplication, QMainWindow, QSystemTrayIcon, 
                            QMenu, QAction, QMessageBox, QWidget, QVBoxLayout,
                            QPushButton, QLabel, QProgressBar)
from PyQt5.QtCore import Qt, QUrl, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView

# Import Flask app
from app import app as flask_app
from utils.model_manager import get_model_manager


class FlaskThread(threading.Thread):
    """Thread to run Flask server in background"""
    
    def __init__(self, host='127.0.0.1', port=5000):
        super().__init__(daemon=True)
        self.host = host
        self.port = port
        
    def run(self):
        """Start Flask server"""
        print(f"Starting Flask server on {self.host}:{self.port}")
        flask_app.run(
            host=self.host,
            port=self.port,
            debug=False,  # Disable debug in production
            use_reloader=False  # Important: disable reloader in thread
        )


class ModelDownloadSignals(QObject):
    """Signals for model download progress"""
    progress = pyqtSignal(str, int, int, str)  # model_key, current, total, message
    finished = pyqtSignal(str, bool)  # model_key, success


class ModelDownloadWindow(QWidget):
    """Window for downloading AI models"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Download AI Models - VoiceFlow")
        self.setMinimumSize(600, 400)
        
        self.model_manager = get_model_manager()
        self.signals = ModelDownloadSignals()
        
        self._setup_ui()
        self._check_model_status()
        
    def _setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("AI Model Download Manager")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel(
            "VoiceFlow requires three AI models to function offline.\n"
            "These will be downloaded once and cached for future use."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("margin: 10px; color: #666;")
        layout.addWidget(desc)
        
        # Model 1: Whisper
        layout.addWidget(QLabel("\n1. OpenAI Whisper (Speech-to-Text) - ~2GB"))
        self.whisper_progress = QProgressBar()
        self.whisper_status = QLabel("Checking...")
        self.whisper_btn = QPushButton("Download")
        self.whisper_btn.clicked.connect(lambda: self._download_model('whisper'))
        layout.addWidget(self.whisper_progress)
        layout.addWidget(self.whisper_status)
        layout.addWidget(self.whisper_btn)
        
        # Model 2: Kazakh TTS
        layout.addWidget(QLabel("\n2. Kazakh TTS (Text-to-Speech) - ~273MB"))
        self.kazakh_progress = QProgressBar()
        self.kazakh_status = QLabel("Checking...")
        self.kazakh_btn = QPushButton("Download")
        self.kazakh_btn.clicked.connect(lambda: self._download_model('kazakh_tts'))
        layout.addWidget(self.kazakh_progress)
        layout.addWidget(self.kazakh_status)
        layout.addWidget(self.kazakh_btn)
        
        # Model 3: Translator
        layout.addWidget(QLabel("\n3. NLLB Translator - ~800MB"))
        self.translator_progress = QProgressBar()
        self.translator_status = QLabel("Checking...")
        self.translator_btn = QPushButton("Download")
        self.translator_btn.clicked.connect(lambda: self._download_model('translator'))
        layout.addWidget(self.translator_progress)
        layout.addWidget(self.translator_status)
        layout.addWidget(self.translator_btn)
        
        # Download All button
        layout.addWidget(QLabel(""))
        self.download_all_btn = QPushButton("Download All Models")
        self.download_all_btn.setStyleSheet(
            "background-color: #4CAF50; color: white; padding: 10px; font-weight: bold;"
        )
        self.download_all_btn.clicked.connect(self._download_all_models)
        layout.addWidget(self.download_all_btn)
        
        # Continue button (enabled when all downloaded)
        self.continue_btn = QPushButton("Continue to App")
        self.continue_btn.setEnabled(False)
        self.continue_btn.clicked.connect(self.accept)
        layout.addWidget(self.continue_btn)
        
        layout.addStretch()
        self.setLayout(layout)
        
        # Connect signals
        self.signals.progress.connect(self._update_progress)
        self.signals.finished.connect(self._download_finished)
        
    def _check_model_status(self):
        """Check which models are already downloaded"""
        status = self.model_manager.get_download_status()
        
        # Update UI for each model
        self._update_model_status('whisper', status['whisper']['downloaded'])
        self._update_model_status('kazakh_tts', status['kazakh_tts']['downloaded'])
        self._update_model_status('translator', status['translator']['downloaded'])
        
        # Enable continue if all downloaded
        if all(s['downloaded'] for s in status.values()):
            self.continue_btn.setEnabled(True)
            self.download_all_btn.setEnabled(False)
    
    def _update_model_status(self, model_key, downloaded):
        """Update UI for model download status"""
        widgets = self._get_model_widgets(model_key)
        
        if downloaded:
            widgets['status'].setText("✓ Downloaded")
            widgets['status'].setStyleSheet("color: green; font-weight: bold;")
            widgets['btn'].setEnabled(False)
            widgets['btn'].setText("Downloaded")
            widgets['progress'].setValue(100)
        else:
            widgets['status'].setText("Not downloaded")
            widgets['status'].setStyleSheet("color: #666;")
            widgets['btn'].setEnabled(True)
            widgets['progress'].setValue(0)
    
    def _get_model_widgets(self, model_key):
        """Get widgets for a specific model"""
        if model_key == 'whisper':
            return {
                'progress': self.whisper_progress,
                'status': self.whisper_status,
                'btn': self.whisper_btn
            }
        elif model_key == 'kazakh_tts':
            return {
                'progress': self.kazakh_progress,
                'status': self.kazakh_status,
                'btn': self.kazakh_btn
            }
        elif model_key == 'translator':
            return {
                'progress': self.translator_progress,
                'status': self.translator_status,
                'btn': self.translator_btn
            }
    
    def _download_model(self, model_key):
        """Download a single model in background thread"""
        widgets = self._get_model_widgets(model_key)
        widgets['btn'].setEnabled(False)
        widgets['btn'].setText("Downloading...")
        widgets['status'].setText("Preparing download...")
        
        def progress_callback(current, total, message):
            self.signals.progress.emit(model_key, current, total, message)
        
        def download_thread():
            success = self.model_manager.download_model(model_key, progress_callback)
            self.signals.finished.emit(model_key, success)
        
        thread = threading.Thread(target=download_thread, daemon=True)
        thread.start()
    
    def _download_all_models(self):
        """Download all models sequentially"""
        self.download_all_btn.setEnabled(False)
        
        # Check which models need downloading
        status = self.model_manager.get_download_status()
        models_to_download = [k for k, v in status.items() if not v['downloaded']]
        
        if not models_to_download:
            QMessageBox.information(self, "Info", "All models are already downloaded!")
            self.continue_btn.setEnabled(True)
            return
        
        # Download first model (chain will continue in _download_finished)
        self._download_model(models_to_download[0])
    
    def _update_progress(self, model_key, current, total, message):
        """Update progress bar and status (called from signal)"""
        widgets = self._get_model_widgets(model_key)
        
        if total > 0:
            progress_pct = int((current / total) * 100)
            widgets['progress'].setValue(progress_pct)
        
        widgets['status'].setText(message)
    
    def _download_finished(self, model_key, success):
        """Handle download completion (called from signal)"""
        widgets = self._get_model_widgets(model_key)
        
        if success:
            widgets['status'].setText("✓ Downloaded")
            widgets['status'].setStyleSheet("color: green; font-weight: bold;")
            widgets['btn'].setText("Downloaded")
            widgets['progress'].setValue(100)
            
            # Check if all models are now downloaded
            status = self.model_manager.get_download_status()
            if all(s['downloaded'] for s in status.values()):
                self.continue_btn.setEnabled(True)
                self.download_all_btn.setEnabled(False)
                QMessageBox.information(
                    self,
                    "Success",
                    "All models downloaded successfully!\nYou can now use the app offline."
                )
            else:
                # Continue downloading next model if using "Download All"
                models_to_download = [k for k, v in status.items() if not v['downloaded']]
                if models_to_download and not self.download_all_btn.isEnabled():
                    QTimer.singleShot(500, lambda: self._download_model(models_to_download[0]))
        else:
            widgets['status'].setText("Download failed")
            widgets['status'].setStyleSheet("color: red;")
            widgets['btn'].setEnabled(True)
            widgets['btn'].setText("Retry")
            self.download_all_btn.setEnabled(True)
            
            QMessageBox.warning(
                self,
                "Download Failed",
                f"Failed to download {self.model_manager.MODELS[model_key]['name']}.\n"
                "Please check your internet connection and try again."
            )
    
    def accept(self):
        """Close window and continue to main app"""
        self.close()


class VoiceFlowDesktop(QMainWindow):
    """Main desktop application window"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("VoiceFlow - Voice Translation")
        self.setMinimumSize(1024, 768)
        
        # Find available port
        self.port = self._find_free_port()
        self.host = '127.0.0.1'
        self.url = f'http://{self.host}:{self.port}'
        
        # Setup WebView
        self.browser = QWebEngineView()
        self.setCentralWidget(self.browser)
        
        # Setup system tray
        self._setup_system_tray()
        
        # Start Flask server
        self.flask_thread = FlaskThread(self.host, self.port)
        self.flask_thread.start()

        # Wait for server to start, then load page
        self._startup_attempts = 0
        self._startup_timer = QTimer(self)
        self._startup_timer.setInterval(300)
        self._startup_timer.timeout.connect(self._wait_for_server)
        self._startup_timer.start()
        
    def _find_free_port(self, start_port=5000, max_attempts=10):
        """Find an available port"""
        for port in range(start_port, start_port + max_attempts):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind(('127.0.0.1', port))
                sock.close()
                return port
            except OSError:
                continue
        return start_port
    
    def _setup_system_tray(self):
        """Setup system tray icon and menu"""
        # Create tray icon (you can replace with custom icon)
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setToolTip("VoiceFlow")
        
        # Create tray menu
        tray_menu = QMenu()
        
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        hide_action = QAction("Hide", self)
        hide_action.triggered.connect(self.hide)
        tray_menu.addAction(hide_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self._quit_app)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._tray_icon_activated)
        self.tray_icon.show()
    
    def _tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.activateWindow()
    
    def _load_app(self):
        """Load Flask app in browser"""
        print(f"Loading app at {self.url}")
        self.browser.load(QUrl(self.url))

    def _wait_for_server(self):
        """Poll Flask health endpoint before loading UI"""
        self._startup_attempts += 1
        if self._startup_attempts > 40:
            self._startup_timer.stop()
            QMessageBox.critical(
                self,
                'Server Error',
                'VoiceFlow failed to start the local server.\n'
                'Please restart the app. If the issue persists, rebuild with console=True to see errors.'
            )
            return

        try:
            health_url = f"http://{self.host}:{self.port}/health"
            with urllib.request.urlopen(health_url, timeout=0.5) as response:
                if response.status != 200:
                    return
        except Exception:
            return

        self._startup_timer.stop()
        self._load_app()
    
    def _quit_app(self):
        """Quit application"""
        reply = QMessageBox.question(
            self,
            'Quit',
            'Are you sure you want to quit VoiceFlow?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            QApplication.quit()
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.tray_icon.isVisible():
            self.hide()
            event.ignore()
        else:
            event.accept()


def main():
    """Main entry point for desktop app"""
    app = QApplication(sys.argv)
    app.setApplicationName("VoiceFlow")
    
    # Check if models are downloaded
    model_manager = get_model_manager()
    model_manager.bootstrap_bundled_models()
    status = model_manager.get_download_status()

    if not model_manager.has_bundled_models() and not all(s['downloaded'] for s in status.values()):
        QMessageBox.warning(
            None,
            'Models Missing',
            'Required AI models were not found on this PC.\n'
            'If you received an offline bundle, ensure the app folder includes a bundled_models folder.\n'
            'Otherwise, connect to the internet to download models on first launch.'
        )
    
    all_downloaded = all(s['downloaded'] for s in status.values())
    
    if not all_downloaded:
        # Show download window first
        download_window = ModelDownloadWindow()
        download_window.show()
        
        # Wait for download window to close
        while download_window.isVisible():
            app.processEvents()
        
        # Check again if user downloaded models
        status = model_manager.get_download_status()
        if not all(s['downloaded'] for s in status.values()):
            reply = QMessageBox.question(
                None,
                'Continue?',
                'Not all models are downloaded. Some features may not work.\n'
                'Do you want to continue anyway?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                sys.exit(0)
    
    # Start main application
    window = VoiceFlowDesktop()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
