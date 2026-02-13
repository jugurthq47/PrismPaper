import os
import shutil
import time
import concurrent.futures
from PyQt6.QtCore import QThread, pyqtSignal, QMutex, QWaitCondition
from core import dominant_color, classify_color

class SortWorker(QThread):
    progress = pyqtSignal(int)
    counter_update = pyqtSignal(int, int) 
    finished = pyqtSignal()
    status_msg = pyqtSignal(str)

    def __init__(self, input_dir, output_dir, copy_mode, files_list, target_colors):
        super().__init__()
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.copy_mode = copy_mode
        self.files_list = files_list
        self.target_colors = target_colors 
        self._running = True
        self._paused = False
        self._mutex = QMutex()
        self._wait_condition = QWaitCondition()

    def process_single_file(self, f):
        if not self._running: return None

        self._mutex.lock()
        if self._paused:
            self._mutex.unlock()
            while self._paused and self._running:
                time.sleep(0.1)
        else:
            self._mutex.unlock()

        src = os.path.join(self.input_dir, f)
        color = dominant_color(src)
        folder_name = classify_color(color)

        if "All Colors" not in self.target_colors and folder_name not in self.target_colors:
            return False 

        dst_dir = os.path.join(self.output_dir, folder_name)
        os.makedirs(dst_dir, exist_ok=True)
        
        try:
            dst_file = os.path.join(dst_dir, f)
            if self.copy_mode:
                shutil.copy2(src, dst_file)
            else:
                shutil.move(src, dst_file)
            return True
        except Exception as e:
            print(f"Error {f}: {e}")
            return False

    def run(self):
        total = len(self.files_list)
        processed_count = 0
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(self.process_single_file, self.files_list)
            
            for result in results:
                if not self._running: 
                    executor.shutdown(wait=False)
                    break
                
                processed_count += 1
                self.progress.emit(int(processed_count / total * 100))
                self.counter_update.emit(processed_count, total)

        self.finished.emit()

    def pause(self):
        self._mutex.lock()
        self._paused = True
        self._mutex.unlock()
        self.status_msg.emit("Paused")

    def resume(self):
        self._mutex.lock()
        self._paused = False
        self._mutex.unlock()
        self.status_msg.emit("Processing...")

    def stop(self):
        self._running = False
        self.resume()