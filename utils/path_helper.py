import sys
import os

def get_assets_path():
    if hasattr(sys, '_MEIPASS'):
        # Running from a PyInstaller bundle
        return os.path.join(sys._MEIPASS, 'assets')
    else:
        # Running from source
        return os.path.join(os.path.dirname(__file__), '..', 'assets')
