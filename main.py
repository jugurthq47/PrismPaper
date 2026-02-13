import sys
import os
import time

os.environ["OMP_NUM_THREADS"] = "1" 
os.environ["MKL_NUM_THREADS"] = "1"

from PyQt6.QtWidgets import QApplication
from ui.splash import ModernSplashScreen 
from ui.app_gui import PrismPaperGUI
from ui.window import ModernWindow

if __name__ == "__main__":
    if sys.platform == 'win32':
        import ctypes
        try:
            myappid = 'mycompany.prismpaper.gui.1.0' 
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

    app = QApplication(sys.argv)
    
    splash = ModernSplashScreen()
    splash.show()
    
    splash.smooth_progress(30, duration=0.3)
    splash.smooth_progress(70, duration=0.5)
    splash.smooth_progress(100, duration=0.3)
    
    logic_widget = PrismPaperGUI()
    window = ModernWindow(logic_widget)

    logic_widget = PrismPaperGUI()
    window = ModernWindow(logic_widget)
    
    window.show()
    splash.finish(window) 
    
    sys.exit(app.exec())