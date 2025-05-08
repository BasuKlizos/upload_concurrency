import os
import sys

def pdftotext_exe_path() -> str:
    default_paths = {
        "linux": "/usr/bin/pdftotext",
        "win32": r"C:\Program Files\xpdf-tools\bin64\pdftotext.exe",
    }

    exe = default_paths.get(sys.platform, "")

    if not os.path.isfile(exe):
        raise FileNotFoundError("pdftotext executable/binary not found at the default path. Please install it or configure the correct path.")
    
    return exe