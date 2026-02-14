import os
import time
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFileDialog, QProgressBar, QMessageBox, QCheckBox, QComboBox
)
from PyQt6.QtGui import QAction, QIcon 
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from utils import HAS_ICONS
if HAS_ICONS:
    import qtawesome as qta

from ui.widgets import DragDropLabel, StayOpenMenu
from workers import SortWorker, auto_low_power_mode

class PrismPaperGUI(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("PrismPaper Logic") 
        self.setWindowOpacity(0.0)
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(800)
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.fade_anim.start()

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

      
        io_layout = QHBoxLayout()
        io_layout.setSpacing(25)

        input_layout = QVBoxLayout()
        self.input_box = DragDropLabel("Drop Input Folder", "fa5s.folder-open")
        self.input_button = QPushButton(" Browse Input")
        input_layout.addWidget(self.input_box)
        input_layout.addWidget(self.input_button)

        output_layout = QVBoxLayout()
        self.output_box = DragDropLabel("Drop Output Folder", "fa5s.folder-plus")
        self.output_button = QPushButton(" Browse Output")
        output_layout.addWidget(self.output_box)
        output_layout.addWidget(self.output_button)

        io_layout.addLayout(input_layout)
        io_layout.addLayout(output_layout)
        main_layout.addLayout(io_layout)

      
        settings_layout = QHBoxLayout()
        self.copy_checkbox = QCheckBox(" Copy files (Safest option)")
        self.copy_checkbox.setChecked(True)
        settings_layout.addWidget(self.copy_checkbox)
        
        # Performance mode selector
        mode_label = QLabel("Mode:")
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Auto", "Performance", "Low Power"])
        self.mode_combo.setToolTip("Auto: Detects based on system resources\nPerformance: Maximum speed\nLow Power: Minimal resource usage")
        settings_layout.addWidget(mode_label)
        settings_layout.addWidget(self.mode_combo)

        # Accuracy selector (affects sample size / clustering parameters)
        acc_label = QLabel("Accuracy:")
        self.accuracy_combo = QComboBox()
        self.accuracy_combo.addItems(["Normal", "High", "Low"])
        self.accuracy_combo.setToolTip("Normal: balanced speed/accuracy\nHigh: better accuracy, slower\nLow: faster, less accurate")
        settings_layout.addWidget(acc_label)
        settings_layout.addWidget(self.accuracy_combo)
        settings_layout.addStretch()

        self.color_btn = QPushButton("All Colors")
        self.color_btn.setFixedWidth(120)
        
        self.color_menu = StayOpenMenu(self)
        self.setup_color_menu()
        self.color_btn.setMenu(self.color_menu)
        
        settings_layout.addWidget(self.color_btn)
        main_layout.addLayout(settings_layout)

       
        button_layout = QHBoxLayout()
        self.btn_start = QPushButton(" Start")
        self.btn_pause = QPushButton(" Pause")
        self.btn_stop = QPushButton(" Stop")
        self.btn_pause.setEnabled(False)
        self.btn_stop.setEnabled(False)
        
        button_layout.addWidget(self.btn_start)
        button_layout.addWidget(self.btn_pause)
        button_layout.addWidget(self.btn_stop)
        main_layout.addLayout(button_layout)

      
        self.progress = QProgressBar()
        self.progress.setFixedHeight(6)
        self.progress.setTextVisible(False)
        self.status_label = QLabel("Please select input and output folders.")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stats_label = QLabel("")
        self.stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(self.progress)
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(self.stats_label)

        self.setLayout(main_layout)
        self.apply_styles()
        self.connect_signals()

       
        self.input_dir = ""
        self.output_dir = ""
        self.worker = None
        self.is_paused = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer_display)
        self.start_time = None
        self.pause_timestamp = None
        self.total_files_count = 0
        self.processed_files_count = 0

    def setup_color_menu(self):
        self.color_options = ["Red", "Orange", "Yellow", "Green", "Cyan", "Blue", "Purple", "Pink", "Black", "White", "Gray", "Mixed"]
        self.all_colors_action = QAction("All Colors", self)
        self.all_colors_action.setCheckable(True)
        self.all_colors_action.setChecked(True)
        self.all_colors_action.triggered.connect(self.on_all_colors_toggled)
        self.color_menu.addAction(self.all_colors_action)
        self.color_menu.addSeparator()
        
        self.color_actions = []
        for color in self.color_options:
            action = QAction(color, self)
            action.setCheckable(True)
            action.triggered.connect(self.on_color_toggled)
            self.color_menu.addAction(action)
            self.color_actions.append(action)

    def apply_styles(self):
        if HAS_ICONS:
            self.input_button.setIcon(qta.icon('fa5s.search', color='white'))
            self.output_button.setIcon(qta.icon('fa5s.save', color='white'))
            self.btn_start.setIcon(qta.icon('fa5s.play', color='white'))
            self.btn_pause.setIcon(qta.icon('fa5s.pause', color='white'))
            self.btn_stop.setIcon(qta.icon('fa5s.stop', color='white'))
            self.copy_checkbox.setIcon(qta.icon('fa5s.copy', color='#aaa'))

        self.setStyleSheet("""
            QWidget { background-color: transparent; color: #f0f0f0; font-family: 'Segoe UI', sans-serif; }
            QPushButton { background-color: #333; color: white; border: 1px solid #444; border-radius: 6px; padding: 10px; font-weight: 600; font-size: 10pt; }
            QPushButton:hover { background-color: #444; border: 1px solid #555; }
            QPushButton:pressed { background-color: #222; }
            QPushButton:disabled { background-color: #222; color: #555; border: 1px solid #333; }
            QPushButton[text*="Start"] { background-color: #3a86ff; border: none; }
            QPushButton[text*="Start"]:hover { background-color: #266dd1; }
            QPushButton[text*="Stop"] { background-color: #e63946; border: none; }
            QPushButton[text*="Stop"]:hover { background-color: #c92a37; }
            QCheckBox { spacing: 8px; color: #aaa; }
            QComboBox { background-color: #333; color: #f0f0f0; border: 1px solid #444; border-radius: 6px; padding: 5px 10px; font-size: 10pt; }
            QComboBox:hover { background-color: #444; border: 1px solid #555; }
            QComboBox::drop-down { border: none; }
            QComboBox::down-arrow { image: none; }
            QComboBox QAbstractItemView { background-color: #2d2d2d; color: #f0f0f0; border: 1px solid #444; selection-background-color: #3a86ff; }
            QProgressBar { border: none; background-color: #333; border-radius: 3px; }
            QProgressBar::chunk { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3a86ff, stop:1 #80bfff); border-radius: 3px; }
            QMenu { background-color: #2d2d2d; color: #f0f0f0; border: 1px solid #444; }
            QMenu::item:selected { background-color: #3a86ff; }
        """)
        self.color_btn.setStyleSheet("""
            QPushButton { background-color: #333; color: #f0f0f0; border: 1px solid #444; border-radius: 5px; padding: 5px; padding-left: 10px; text-align: left; }
            QPushButton::menu-indicator { image: none; }
        """)
        self.status_label.setStyleSheet("color: #aaa; font-size: 10pt; margin-top: 5px; font-weight: bold;")
        self.stats_label.setStyleSheet("color: #777; font-size: 9pt; margin-top: 2px;")

    def connect_signals(self):
        self.input_button.clicked.connect(self.select_input)
        self.output_button.clicked.connect(self.select_output)
        self.input_box.folder_changed.connect(self.set_input_folder)
        self.output_box.folder_changed.connect(self.set_output_folder)
        self.btn_start.clicked.connect(self.start_sorting)
        self.btn_pause.clicked.connect(self.toggle_pause)
        self.btn_stop.clicked.connect(self.cancel_sorting)

    def on_all_colors_toggled(self, checked):
        if checked:
            for action in self.color_actions:
                action.blockSignals(True)
                action.setChecked(False)
                action.blockSignals(False)
            self.color_btn.setText("All Colors")
        else:
            if not any(a.isChecked() for a in self.color_actions):
                self.all_colors_action.blockSignals(True)
                self.all_colors_action.setChecked(True)
                self.all_colors_action.blockSignals(False)

    def on_color_toggled(self, checked):
        self.all_colors_action.blockSignals(True)
        self.all_colors_action.setChecked(False)
        self.all_colors_action.blockSignals(False)
        selected = [a.text() for a in self.color_actions if a.isChecked()]
        if not selected:
            self.all_colors_action.setChecked(True)
            self.color_btn.setText("All Colors")
        elif len(selected) <= 2:
            self.color_btn.setText(", ".join(selected))
        else:
            self.color_btn.setText(f"{len(selected)} colors")

    def get_selected_colors(self):
        if self.all_colors_action.isChecked():
            return ["All Colors"]
        return [a.text() for a in self.color_actions if a.isChecked()]

    def check_folders_ready(self):
        if self.input_dir and self.output_dir:
            self.status_label.setText("Ready to process")
            self.status_label.setStyleSheet("color: #4caf50; font-size: 10pt; margin-top: 5px; font-weight: bold;")
        else:
            self.status_label.setText("Please select input and output folders.")
            self.status_label.setStyleSheet("color: #aaa; font-size: 10pt; margin-top: 5px; font-weight: bold;")

    def select_input(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Input Folder")
        if folder: self.set_input_folder(folder)

    def select_output(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder: self.set_output_folder(folder)

    def set_input_folder(self, folder):
        self.input_dir = folder
        self.input_box.setText(f"\n\n{os.path.basename(folder)}")
        self.input_box.has_content = True
        self.input_box.setStyleSheet(self.input_box.success_style)
        self.check_folders_ready()

    def set_output_folder(self, folder):
        self.output_dir = folder
        self.output_box.setText(f"\n\n{os.path.basename(folder)}")
        self.output_box.has_content = True
        self.output_box.setStyleSheet(self.output_box.success_style)
        self.check_folders_ready()

    def start_sorting(self):
        if not self.input_dir or not self.output_dir:
            QMessageBox.warning(self, "Missing Info", "Please select both folders.")
            return
        
        self.status_label.setText("Scanning files...")
        QApplication.processEvents()
        files_list = [f for f in os.listdir(self.input_dir) if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))]
        self.total_files_count = len(files_list)
        self.processed_files_count = 0
        
        if self.total_files_count == 0:
             QMessageBox.warning(self, "No Files", "No supported images found in input folder.")
             self.check_folders_ready()
             return

        self.btn_start.setEnabled(False)
        self.input_button.setEnabled(False)
        self.output_button.setEnabled(False)
        self.btn_pause.setEnabled(True)
        self.btn_stop.setEnabled(True)
        self.is_paused = False
        self.update_pause_btn_text()
        self.status_label.setText("Processing...")
        self.status_label.setStyleSheet("color: #3a86ff; font-size: 10pt; margin-top: 5px; font-weight: bold;")

        self.start_time = time.time()
        self.pause_timestamp = None
        self.timer.start(1000)

        copy_mode = self.copy_checkbox.isChecked()
        target_colors = self.get_selected_colors()
        
      
        mode_selection = self.mode_combo.currentText()
        if mode_selection == "Auto":
            low_power = None 
        elif mode_selection == "Low Power":
            low_power = True
        else:
            low_power = False

        # Build accuracy settings from dropdown
        acc = self.accuracy_combo.currentText() if hasattr(self, 'accuracy_combo') else 'Normal'
        if acc == 'High':
            accuracy_settings = { 'sample_size': 100, 'n_clusters': 5, 'n_init': 3, 'max_iter': 200, 's_threshold': 0.20, 'v_threshold': 0.20 }
        elif acc == 'Low':
            accuracy_settings = { 'sample_size': 30, 'n_clusters': 2, 'n_init': 1, 'max_iter': 50, 's_threshold': 0.15, 'v_threshold': 0.15 }
        else:
            accuracy_settings = { 'sample_size': 50, 'n_clusters': 3, 'n_init': 1, 'max_iter': 100, 's_threshold': 0.25, 'v_threshold': 0.25 }

        self.worker = SortWorker(self.input_dir, self.output_dir, copy_mode, files_list, target_colors, low_power_mode=low_power, accuracy_settings=accuracy_settings)
        self.worker.progress.connect(self.progress.setValue)
        self.worker.counter_update.connect(self.update_counter_vars)
        self.worker.status_msg.connect(self.update_status_label)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def update_timer_display(self):
        if self.start_time is None or self.is_paused: return
        elapsed = time.time() - self.start_time
        m, s = divmod(int(elapsed), 60)
        elapsed_str = f"{m:02d}:{s:02d}"
        
        remaining_str = "--:--"
        if self.processed_files_count > 0 and elapsed > 0:
            rate = self.processed_files_count / elapsed
            remaining_items = self.total_files_count - self.processed_files_count
            if rate > 0:
                rm, rs = divmod(int(remaining_items / rate), 60)
                remaining_str = f"{rm:02d}:{rs:02d}"

        self.stats_label.setText(f"Processed: {self.processed_files_count} / {self.total_files_count}  |  Elapsed: {elapsed_str}  |  Remaining: {remaining_str}")

    def toggle_pause(self):
        if not self.worker: return
        if self.is_paused:
            self.start_time += (time.time() - self.pause_timestamp)
            self.worker.resume()
            self.timer.start()
            self.is_paused = False
        else:
            self.timer.stop()
            self.pause_timestamp = time.time()
            self.worker.pause()
            self.is_paused = True
        self.update_pause_btn_text()

    def update_pause_btn_text(self):
        txt = " Resume" if self.is_paused else " Pause"
        icon_name = 'fa5s.play' if self.is_paused else 'fa5s.pause'
        self.btn_pause.setText(txt)
        if HAS_ICONS:
            self.btn_pause.setIcon(qta.icon(icon_name, color='white'))

    def cancel_sorting(self):
        if self.worker:
            self.worker.stop()
            self.status_label.setText("Stopping...")
            self.status_label.setStyleSheet("color: #e63946; font-size: 10pt; margin-top: 5px; font-weight: bold;")

    def update_counter_vars(self, processed, total):
        self.processed_files_count = processed
        self.total_files_count = total 

    def update_status_label(self, msg):
        self.status_label.setText(msg)
        color = "#e63946" if msg == "Paused" else "#3a86ff"
        self.status_label.setStyleSheet(f"color: {color}; font-size: 10pt; margin-top: 5px; font-weight: bold;")

    def on_finished(self):
        self.timer.stop()
        self.btn_start.setEnabled(True)
        self.input_button.setEnabled(True)
        self.output_button.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self.btn_stop.setEnabled(False)
        self.is_paused = False
        self.update_pause_btn_text()
        QMessageBox.information(self, "Done", "Sorting complete or stopped!")
        self.status_label.setText("Complete")
        self.status_label.setStyleSheet("color: #4caf50; font-size: 10pt; margin-top: 5px; font-weight: bold;")
        self.progress.setValue(0)