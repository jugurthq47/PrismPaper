import sys
import os

def get_asset_path(relative_path):
    try:
        
        base_path = sys._MEIPASS
    except Exception:
    
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, "assets", relative_path)

try:
    import qtawesome as qta
    HAS_ICONS = True
except ImportError:
    HAS_ICONS = False