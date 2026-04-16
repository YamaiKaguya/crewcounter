import importlib
import shutil
import subprocess
import sys

packages = [
    "fastapi",
    "uvicorn",
    "PIL",
    "multipart",
    "pytesseract",
    "cv2",
]

def check_module(name, import_name=None):
    import_name = import_name or name
    try:
        mod = importlib.import_module(import_name)
        version = getattr(mod, "__version__", "installed")
        return f"{name}: OK ({version})"
    except Exception as e:
        return f"{name}: MISSING / ERROR ({e})"

print("=== Python ===")
print(sys.version)

print("\n=== Packages ===")
print(check_module("fastapi"))
print(check_module("uvicorn"))
print(check_module("Pillow", "PIL"))
print(check_module("python-multipart", "multipart"))
print(check_module("pytesseract"))
print(check_module("opencv-python", "cv2"))

print("\n=== External tools ===")
tesseract_path = shutil.which("tesseract")
print(f"Tesseract command: {'FOUND at ' + tesseract_path if tesseract_path else 'NOT FOUND'}")

print("\n=== pytesseract test ===")
try:
    import pytesseract
    if tesseract_path:
        print("pytesseract can likely use system tesseract.")
    else:
        print("pytesseract is installed, but tesseract.exe path may need to be set manually.")
except Exception as e:
    print(f"pytesseract test failed: {e}")

print("\n=== Uvicorn test ===")
try:
    import uvicorn
    print("uvicorn: OK")
except Exception as e:
    print(f"uvicorn: ERROR ({e})")