import time
from PyQt6.QtWidgets import (
    QSplashScreen, QProgressBar, QVBoxLayout, 
    QLabel, QWidget, QGraphicsDropShadowEffect,
    QApplication 
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap, QColor, QFont
from utils import get_asset_path

class ModernSplashScreen(QSplashScreen):
    def __init__(self):
       
        pixmap = QPixmap(400, 250)
        pixmap.fill(Qt.GlobalColor.transparent)
        super().__init__(pixmap)
        
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
       
        self.container = QWidget(self)
        self.container.setGeometry(0, 0, 400, 250)
        self.container.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                border: 1px solid #333;
                border-radius: 12px;
            }
        """)
        
      
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 5)
        self.container.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self.container)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(20, 20, 20, 20)

       
        self.icon_label = QLabel()
        icon_path = get_asset_path("icon.ico")
       
        logo = QPixmap(icon_path)
        if not logo.isNull():
             self.icon_label.setPixmap(logo.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        layout.addWidget(self.icon_label, alignment=Qt.AlignmentFlag.AlignCenter)

       
        self.title_label = QLabel("PrismPaper")
        self.title_label.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        self.title_label.setStyleSheet("color: #ffffff; border: none;")
        layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignCenter)

       
        self.status_label = QLabel("Initializing...")
        self.status_label.setFont(QFont("Segoe UI", 10))
        self.status_label.setStyleSheet("color: #888; border: none; margin-top: 5px;")
        layout.addWidget(self.status_label, alignment=Qt.AlignmentFlag.AlignCenter)

      
        self.progress = QProgressBar()
        self.progress.setFixedHeight(6)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                background-color: #333;
                border-radius: 3px;
                border: none;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3a86ff, stop:1 #80bfff);
                border-radius: 3px;
            }
        """)
        self.progress.setFixedWidth(250)
        layout.addWidget(self.progress, alignment=Qt.AlignmentFlag.AlignCenter)
        
      
        layout.addSpacing(10)

    def progress_update(self, value, text):
        self.progress.setValue(value)
        self.status_label.setText(text)
        QApplication.processEvents()

    def smooth_progress(self, target_value, duration=0.5):
        current = self.progress.value()
        steps = 30 
        increment = (target_value - current) / steps
        pause = duration / steps

        for _ in range(steps):
            current += increment
            self.progress.setValue(int(current))
            QApplication.processEvents() 
            time.sleep(pause)