import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton, QSizeGrip
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap
from utils import get_asset_path, HAS_ICONS
if HAS_ICONS:
    import qtawesome as qta

class CustomTitleBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)
        self.parent_window = parent
        self.click_pos = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 15, 0)
        layout.setSpacing(10)

        self.icon_label = QLabel()
        icon_path = get_asset_path("icon.ico")
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            self.icon_label.setPixmap(pixmap.scaled(18, 18, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        elif HAS_ICONS:
            self.icon_label.setPixmap(qta.icon('fa5s.layer-group', color='#3a86ff').pixmap(18, 18))
        layout.addWidget(self.icon_label)

        self.title_label = QLabel("PrismPaper")
        self.title_label.setStyleSheet("color: #e0e0e0; font-weight: bold; font-family: 'Segoe UI'; font-size: 12px;")
        layout.addWidget(self.title_label)
        layout.addStretch() 

       
        self.btn_min = self.create_nav_btn("min", "#444")
        self.btn_close = self.create_nav_btn("close", "#e63946")
        layout.addWidget(self.btn_min)
        layout.addWidget(self.btn_close)

        self.btn_min.clicked.connect(self.parent_window.showMinimized)
        self.btn_close.clicked.connect(self.parent_window.close)

    def create_nav_btn(self, btn_type, hover_color):
        btn = QPushButton()
        btn.setFixedSize(30, 30)
        icon_map = {"min": "fa5s.minus", "close": "fa5s.times"}
        if HAS_ICONS:
            btn.setIcon(qta.icon(icon_map[btn_type], color='#bbb'))
        btn.setStyleSheet(f"QPushButton {{ background: transparent; border: none; border-radius: 5px; }} QPushButton:hover {{ background-color: {hover_color}; }}")
        return btn

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.click_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.click_pos is not None:
            current_pos = event.globalPosition().toPoint()
            delta = current_pos - self.click_pos
            self.parent_window.move(self.parent_window.pos() + delta)
            self.click_pos = current_pos

    def mouseReleaseEvent(self, event):
        self.click_pos = None

class ModernWindow(QWidget):
    def __init__(self, content_widget):
        super().__init__()
        self.setWindowTitle("PrismPaper") 
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("background-color: #1e1e1e;")
        self.resize(750, 480)

        icon_path = get_asset_path("icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.frame = QFrame()
        self.frame.setObjectName("mainFrame")
        self.frame.setStyleSheet("""
            QFrame#mainFrame {
                background-color: #1e1e1e;
                border: 1px solid #333;
                border-radius: 0px; 
            }
        """)

        self.frame_layout = QVBoxLayout(self.frame)
        self.frame_layout.setContentsMargins(0, 0, 0, 0)
        self.frame_layout.setSpacing(0)

        self.title_bar = CustomTitleBar(self)
        self.frame_layout.addWidget(self.title_bar)
        self.frame_layout.addWidget(content_widget)
        
        self.layout.addWidget(self.frame)