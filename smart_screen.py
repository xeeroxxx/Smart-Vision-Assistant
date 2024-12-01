import sys
import json
import base64
import warnings
from io import BytesIO
import keyboard
import requests
from PIL import ImageGrab, Image
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QWidget, QLabel
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt5.QtCore import Qt, QPoint, QRect, QTimer, QObject, pyqtSignal

# Suppress deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

class KeyboardHandler(QObject):
    capture_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setup_hotkey()

    def setup_hotkey(self):
        keyboard.on_press_key('c', self.on_hotkey, suppress=True)
        
    def on_hotkey(self, event):
        if keyboard.is_pressed('alt') and keyboard.is_pressed('shift'):
            self.capture_signal.emit()

class ScreenshotOverlay(QWidget):
    def __init__(self, callback):
        super().__init__()
        self.begin = QPoint()
        self.end = QPoint()
        self.is_selecting = False
        self.callback = callback
        self.initUI()

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setWindowState(Qt.WindowFullScreen)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 100);")
        self.setCursor(Qt.CrossCursor)

    def paintEvent(self, event):
        if self.is_selecting:
            brush = QColor(128, 128, 255, 100)
            painter = QPainter(self)
            painter.fillRect(QRect(self.begin, self.end), brush)

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = self.begin
        self.is_selecting = True

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        self.is_selecting = False
        if self.begin and self.end:
            self.hide()
            QTimer.singleShot(100, lambda: self.capture_screen())

    def capture_screen(self):
        if self.begin and self.end:
            x1, y1 = min(self.begin.x(), self.end.x()), min(self.begin.y(), self.end.y())
            x2, y2 = max(self.begin.x(), self.end.x()), max(self.begin.y(), self.end.y())
            screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            self.callback(screenshot)

class SmartScreenAssistant:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.overlay = None
        self.keyboard_handler = KeyboardHandler()
        self.keyboard_handler.capture_signal.connect(self.start_capture)
        self.setup_tray()
        
    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self.app)
        self.tray_icon.setIcon(self.create_icon())
        
        # Create menu
        menu = QMenu()
        capture_action = menu.addAction("Capture (Alt+Shift+C)")
        capture_action.triggered.connect(self.start_capture)
        menu.addSeparator()
        quit_action = menu.addAction("Quit")
        quit_action.triggered.connect(self.cleanup_and_quit)
        
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()
        
        # Show startup notification
        self.tray_icon.showMessage(
            "Smart Screen Assistant",
            "Press Alt+Shift+C to capture and analyze any part of your screen",
            QSystemTrayIcon.Information,
            5000
        )

    def create_icon(self):
        # Create a simple icon
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.blue)
        return QIcon(pixmap)

    def start_capture(self):
        if not self.overlay:
            self.overlay = ScreenshotOverlay(self.process_screenshot)
        self.overlay.show()

    def process_screenshot(self, screenshot):
        try:
            # Convert PIL Image to base64
            buffered = BytesIO()
            screenshot.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()

            # Prepare the request to Ollama
            url = "http://localhost:11434/api/generate"
            payload = {
                "model": "llama3.2-vision",
                "prompt": "What do you see in this image? Please provide a clear and concise description.",
                "images": [img_str],
                "stream": False
            }

            response = requests.post(url, json=payload)
            if response.status_code == 200:
                result = response.json()
                self.show_result(result.get('response', 'No response from model'))
            else:
                self.show_result(f"Error: {response.status_code}")
        except Exception as e:
            self.show_result(f"Error: {str(e)}")

    def show_result(self, text):
        # Copy to clipboard
        clipboard = self.app.clipboard()
        clipboard.setText(text)
        
        # Show notification
        self.tray_icon.showMessage(
            "Smart Screen Assistant",
            f"Analysis copied to clipboard:\n{text[:100]}{'...' if len(text) > 100 else ''}",
            QSystemTrayIcon.Information,
            5000
        )

    def cleanup_and_quit(self):
        keyboard.unhook_all()  # Clean up keyboard hooks
        self.app.quit()

    def run(self):
        try:
            sys.exit(self.app.exec_())
        except KeyboardInterrupt:
            self.cleanup_and_quit()

if __name__ == '__main__':
    assistant = SmartScreenAssistant()
    assistant.run()
