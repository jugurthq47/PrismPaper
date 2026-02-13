import os
from PyQt6.QtWidgets import QLabel, QMenu
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from utils import HAS_ICONS
if HAS_ICONS:
    import qtawesome as qta

class StayOpenMenu(QMenu):
    def mouseReleaseEvent(self, e):
        action = self.actionAt(e.pos())
        if action and action.isCheckable():
            action.trigger()
            e.accept()
        else:
            super().mouseReleaseEvent(e)

class DragDropLabel(QLabel):
    folder_changed = pyqtSignal(str)

    def __init__(self, text="Drop folder here", icon_name='fa5s.folder'):
        super().__init__()
        self.default_text = text
        self.setText(text)
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumHeight(100)
        self.has_content = False 
        
        if HAS_ICONS:
            self.icon_pixmap = qta.icon(icon_name, color='#888').pixmap(32, 32)
            self.setPixmap(self.icon_pixmap)
            self.setText(f"\n\n{text}")

        self.default_style = """
            QLabel {
                background-color: #333;
                color: #aaa;
                border: 2px dashed #555;
                border-radius: 12px;
                font-size: 11pt;
                font-weight: bold;
            }
        """
        self.active_style = """
            QLabel {
                background-color: #3a3a3a;
                color: #3a86ff;
                border: 2px dashed #3a86ff;
                border-radius: 12px;
                font-size: 11pt;
                font-weight: bold;
            }
        """
        self.success_style = """
            QLabel {
                background-color: #2d4a2d;
                color: #4caf50;
                border: 2px solid #4caf50;
                border-radius: 12px;
                font-size: 15pt;
                padding-bottom : 23px;
            }
        """
        self.setStyleSheet(self.default_style)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            self.setStyleSheet(self.active_style)
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        if self.has_content:
            self.setStyleSheet(self.success_style)
        else:
            self.setStyleSheet(self.default_style)

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            folder = urls[0].toLocalFile()
            if os.path.isdir(folder):
                self.setText(f"\n\n{os.path.basename(folder)}")
                self.folder_changed.emit(folder)
                self.setStyleSheet(self.success_style)
                self.has_content = True
            else:
                if self.has_content:
                    self.setStyleSheet(self.success_style)
                else:
                    self.setStyleSheet(self.default_style)