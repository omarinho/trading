import os
import sys
import urllib.request
import subprocess
import platform

def download_ta_lib():
    # Get Python version
    python_version = f"{sys.version_info.major}{sys.version_info.minor}"
    
    # Get system architecture
    is_64bits = sys.maxsize > 2**32
    arch = "win_amd64" if is_64bits else "win32"
    
    # Construct download URL
    url = f"https://download.lfd.uci.edu/pythonlibs/archived/TA_Lib‑0.4.28‑cp{python_version}‑cp{python_version}‑{arch}.whl"
    
    # Download the wheel
    print(f"Downloading TA-Lib wheel from {url}")
    urllib.request.urlretrieve(url, "TA_Lib.whl")
    
    # Install the wheel
    print("Installing TA-Lib wheel...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "TA_Lib.whl"])
    
    # Clean up
    os.remove("TA_Lib.whl")
    print("TA-Lib installation completed!")

if __name__ == "__main__":
    download_ta_lib() 