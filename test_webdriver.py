"""
Simple test script to verify WebDriver setup works correctly
"""

import time
import os
import shutil
import zipfile
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def clear_webdriver_cache():
    """Clear webdriver manager cache to force fresh download"""
    try:
        import tempfile
        cache_dir = os.path.join(tempfile.gettempdir(), ".wdm")
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
            print("Cleared webdriver cache")
        return True
    except Exception as e:
        print(f"Warning: Could not clear cache: {e}")
        return False

def get_chrome_version():
    """Get Chrome version from Windows registry"""
    try:
        import subprocess
        # Try multiple registry locations
        registry_paths = [
            'HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon',
            'HKEY_LOCAL_MACHINE\\SOFTWARE\\Google\\Chrome\\BLBeacon',
            'HKEY_LOCAL_MACHINE\\SOFTWARE\\WOW6432Node\\Google\\Chrome\\BLBeacon'
        ]
        
        for path in registry_paths:
            try:
                result = subprocess.check_output([
                    'reg', 'query', path, '/v', 'version'
                ], shell=True, stderr=subprocess.DEVNULL).decode('utf-8').strip()
                version = result.split()[-1]
                print(f"Found Chrome version: {version}")
                return version
            except:
                continue
        
        print("Could not detect Chrome version from registry")
        return None
    except Exception as e:
        print(f"Error detecting Chrome version: {e}")
        return None

def download_chromedriver_manually(version=None):
    """Manually download ChromeDriver from Google's official site"""
    try:
        print("Attempting manual ChromeDriver download...")
        
        if not version:
            version = get_chrome_version()
        
        if version:
            # Get major version (e.g., "137" from "137.0.7151.122")
            major_version = version.split('.')[0]
        else:
            major_version = "120"  # fallback to a stable version
        
        # ChromeDriver download URL format changed for newer versions
        if int(major_version) >= 115:
            # New Chrome for Testing endpoints
            api_url = f"https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"
            response = requests.get(api_url, timeout=10)
            data = response.json()
            
            # Find the chromedriver download URL for Windows
            chromedriver_url = None
            channels = data.get('channels', {})
            stable = channels.get('Stable', {})
            downloads = stable.get('downloads', {})
            chromedriver_downloads = downloads.get('chromedriver', [])
            
            for download in chromedriver_downloads:
                if download.get('platform') == 'win64':
                    chromedriver_url = download.get('url')
                    break
                elif download.get('platform') == 'win32':
                    chromedriver_url = download.get('url')
                    break
        else:
            # Old format for older versions
            chromedriver_url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{major_version}"
            response = requests.get(chromedriver_url, timeout=10)
            exact_version = response.text.strip()
            chromedriver_url = f"https://chromedriver.storage.googleapis.com/{exact_version}/chromedriver_win32.zip"
        
        if not chromedriver_url:
            print("Could not find ChromeDriver download URL")
            return None
        
        print(f"Downloading ChromeDriver from: {chromedriver_url}")
        
        # Download the zip file
        response = requests.get(chromedriver_url, timeout=30)
        response.raise_for_status()
        
        # Create download directory
        download_dir = os.path.join(os.getcwd(), "chromedriver_manual")
        os.makedirs(download_dir, exist_ok=True)
        
        zip_path = os.path.join(download_dir, "chromedriver.zip")
        with open(zip_path, 'wb') as f:
            f.write(response.content)
        
        # Extract the zip file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(download_dir)
        
        # Find the chromedriver.exe file
        for root, dirs, files in os.walk(download_dir):
            for file in files:
                if file == "chromedriver.exe":
                    chromedriver_path = os.path.join(root, file)
                    print(f"Successfully downloaded ChromeDriver to: {chromedriver_path}")
                    return chromedriver_path
        
        print("Could not find chromedriver.exe in downloaded files")
        return None
        
    except Exception as e:
        print(f"Manual download failed: {e}")
        return None

def setup_chrome_driver():
    """Setup Chrome driver with multiple fallback options"""
    chrome_options = Options()
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--ignore-ssl-errors")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    
    print("Setting up Chrome WebDriver...")
    
    # Method 1: Try manual download first
    try:
        print("Attempting method 1: Manual ChromeDriver download...")
        driver_path = download_chromedriver_manually()
        if driver_path and os.path.exists(driver_path):
            service = Service(driver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
            print("✓ Successfully initialized Chrome driver (Method 1 - Manual)")
            return driver
        else:
            print("✗ Manual download did not produce valid driver")
    except Exception as e:
        print(f"✗ Method 1 failed: {e}")
    
    # Method 2: Try clearing cache and downloading fresh driver
    try:
        print("Attempting method 2: Fresh driver download with webdriver-manager...")
        clear_webdriver_cache()
        
        driver_manager = ChromeDriverManager()
        driver_path = driver_manager.install()
        print(f"Driver installed at: {driver_path}")
        
        # Check if the path actually points to chromedriver.exe
        if not driver_path.endswith('chromedriver.exe'):
            # Try to find the actual chromedriver.exe in the directory
            driver_dir = os.path.dirname(driver_path)
            for root, dirs, files in os.walk(driver_dir):
                for file in files:
                    if file == "chromedriver.exe":
                        driver_path = os.path.join(root, file)
                        print(f"Found actual chromedriver.exe at: {driver_path}")
                        break
        
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("✓ Successfully initialized Chrome driver (Method 2)")
        return driver
        
    except Exception as e:
        print(f"✗ Method 2 failed: {e}")
    
    # Method 3: Try without webdriver-manager (using system Chrome driver)
    try:
        print("Attempting method 3: System Chrome driver...")
        # Try common Chrome driver locations
        common_paths = [
            "C:\\Program Files\\Google\\Chrome\\Application\\chromedriver.exe",
            "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chromedriver.exe",
            "chromedriver.exe",  # Current directory
            "./chromedriver.exe",
            "./chromedriver_manual/chromedriver.exe"  # Our manual download location
        ]
        
        for driver_path in common_paths:
            if os.path.exists(driver_path):
                print(f"Found Chrome driver at: {driver_path}")
                service = Service(driver_path)
                driver = webdriver.Chrome(service=service, options=chrome_options)
                print("✓ Successfully initialized Chrome driver (Method 3)")
                return driver
        
        print("No system Chrome driver found in common locations")
        
    except Exception as e:
        print(f"✗ Method 3 failed: {e}")
    
    # Method 4: Try with different Chrome options (minimal)
    try:
        print("Attempting method 4: Minimal Chrome options...")
        minimal_options = Options()
        minimal_options.add_argument("--no-sandbox")
        minimal_options.add_argument("--disable-dev-shm-usage")
        
        clear_webdriver_cache()
        driver_path = ChromeDriverManager().install()
        
        # Fix path if needed
        if not driver_path.endswith('chromedriver.exe'):
            driver_dir = os.path.dirname(driver_path)
            for root, dirs, files in os.walk(driver_dir):
                for file in files:
                    if file == "chromedriver.exe":
                        driver_path = os.path.join(root, file)
                        break
        
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=minimal_options)
        print("✓ Successfully initialized Chrome driver (Method 4)")
        return driver
        
    except Exception as e:
        print(f"✗ Method 4 failed: {e}")
    
    raise Exception("All WebDriver initialization methods failed. Please check your Chrome installation and try running as administrator.")

def test_webdriver():
    """Test WebDriver initialization and basic functionality"""
    print("="*50)
    print("Testing WebDriver Setup")
    print("="*50)
    
    try:
        # Initialize driver
        driver = setup_chrome_driver()
        print("\n✓ WebDriver initialized successfully!")
        
        # Test basic functionality
        print("\nTesting basic functionality...")
        driver.get("https://www.google.com")
        print(f"✓ Successfully navigated to Google")
        print(f"✓ Page title: {driver.title}")
        
        # Test that we can find elements
        search_box = driver.find_element("name", "q")
        print("✓ Successfully found search box element")
        
        # Close browser
        time.sleep(2)
        driver.quit()
        print("✓ Successfully closed browser")
        
        print("\n" + "="*50)
        print("🎉 WebDriver test PASSED! Your setup is working correctly.")
        print("You can now run your servpro_login.py script.")
        print("="*50)
        
    except Exception as e:
        print(f"\n❌ WebDriver test FAILED: {e}")
        print("\nTroubleshooting suggestions:")
        print("1. Make sure Google Chrome is installed")
        print("2. Try running PowerShell as Administrator")
        print("3. Check if antivirus is blocking the download")
        print("4. Try updating Chrome to the latest version")
        print("5. Clear your browser cache and temporary files")
        print("6. Manually download ChromeDriver from https://chromedriver.chromium.org/")

if __name__ == "__main__":
    test_webdriver() 