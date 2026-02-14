import os
import shutil
import concurrent.futures
import multiprocessing
import psutil
from PyQt6.QtCore import QThread, pyqtSignal, QMutex, QWaitCondition
from core import dominant_color, classify_color

# --------------------- PROCESS WORKER ---------------------
def process_file_worker(args):
    """Runs in a separate process"""
    input_dir, output_dir, copy_mode, target_colors, filename, accuracy_settings = args
    src = os.path.join(input_dir, filename)

    try:
        color = dominant_color(src, **(accuracy_settings or {}))
    except TypeError:
        color = dominant_color(src)

    folder_name = classify_color(color)

    if "All Colors" not in target_colors and folder_name not in target_colors:
        return (filename, False, None)

    dst_dir = os.path.join(output_dir, folder_name)
    os.makedirs(dst_dir, exist_ok=True)

    try:
        dst_file = os.path.join(dst_dir, filename)
        if copy_mode:
            shutil.copy2(src, dst_file)
        else:
            shutil.move(src, dst_file)
        return (filename, True, folder_name)
    except Exception as e:
        return (filename, False, str(e))


# --------------------- LOW POWER AUTO-DETECT ---------------------
def auto_low_power_mode():
    cpu_count = multiprocessing.cpu_count()
    ram_gb = psutil.virtual_memory().total / (1024**3)

    if cpu_count <= 2:
        return True
    if ram_gb <= 4:
        return True
    battery = psutil.sensors_battery()
    if battery and not battery.power_plugged:
        return True

    return False


# --------------------- SORT WORKER THREAD ---------------------
class SortWorker(QThread):
    progress = pyqtSignal(int)
    counter_update = pyqtSignal(int, int)
    finished = pyqtSignal()
    status_msg = pyqtSignal(str)

    def __init__(
        self,
        input_dir,
        output_dir,
        copy_mode,
        files_list,
        target_colors,
        low_power_mode=None,
        accuracy_settings=None,
    ):
        super().__init__()
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.copy_mode = copy_mode
        self.files_list = files_list
        self.target_colors = target_colors

        # Auto-detect low-power if not explicitly set
        self.low_power_mode = (
            auto_low_power_mode() if low_power_mode is None else low_power_mode
        )

        self.accuracy_settings = accuracy_settings or {}

        self._running = True
        self._paused = False
        self._mutex = QMutex()
        self._wait_condition = QWaitCondition()

    # ---------- CONTROL ----------
    def pause(self):
        self._mutex.lock()
        self._paused = True
        self._mutex.unlock()
        self.status_msg.emit("Paused")

    def resume(self):
        self._mutex.lock()
        self._paused = False
        self._wait_condition.wakeAll()
        self._mutex.unlock()
        self.status_msg.emit("Processing...")

    def stop(self):
        self._running = False
        self.resume()

    def _wait_if_paused(self):
        self._mutex.lock()
        while self._paused and self._running:
            self._wait_condition.wait(self._mutex)
        self._mutex.unlock()

    # ---------- THREAD RUN ----------
    def run(self):
        total = len(self.files_list)
        processed = 0

        if total == 0:
            self.finished.emit()
            return

        cpu_count = multiprocessing.cpu_count()
        max_workers = 1 if self.low_power_mode else max(1, min(cpu_count - 1, 4))
        chunk_size = 10 if self.low_power_mode else 25

        self.status_msg.emit(
            f"Mode: {'Low Power' if self.low_power_mode else 'Performance'} | Workers: {max_workers}"
        )

        args_iter = (
            (self.input_dir, self.output_dir, self.copy_mode, self.target_colors, f, self.accuracy_settings)
            for f in self.files_list
        )

        try:
            with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
                futures = []

                for args in args_iter:
                    if not self._running:
                        break
                    futures.append(executor.submit(process_file_worker, args))

                    if len(futures) >= chunk_size:
                        processed += self._process_futures(futures, total, processed)
                        futures.clear()

                # Process any remaining futures
                if futures:
                    processed += self._process_futures(futures, total, processed)

        except Exception as e:
            self.status_msg.emit(f"Worker error: {e}")

        self.finished.emit()

    # ---------- HELPER ----------
    def _process_futures(self, futures, total, processed):
        processed_count = 0
        for future in concurrent.futures.as_completed(futures):
            if not self._running:
                break

            self._wait_if_paused()

            try:
                _, success, _ = future.result()
            except Exception:
                success = False

            processed += 1
            processed_count += 1
            self.progress.emit(int(processed / total * 100))
            self.counter_update.emit(processed, total)

        return processed_count


# --------------------- PYINSTALLER FREEZE SUPPORT ---------------------
# In your main script, add:
# if __name__ == "__main__":
#     multiprocessing.freeze_support()
