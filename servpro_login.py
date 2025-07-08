"""
SERVPRO login script with exact element IDs and popup handling
"""

import time
import os
import tempfile
import shutil
import zipfile
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoAlertPresentException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys

def get_chrome_version():
    """Get the installed Chrome version"""
    import subprocess
    import re
    
    try:
        # Try to get Chrome version from registry
        result = subprocess.run([
            'reg', 'query', 
            'HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon', 
            '/v', 'version'
        ], capture_output=True, text=True, shell=True)
        
        if result.returncode == 0:
            version_match = re.search(r'version\s+REG_SZ\s+(\d+\.\d+\.\d+\.\d+)', result.stdout)
            if version_match:
                return version_match.group(1)
    except:
        pass
    
    try:
        # Alternative method - check Chrome executable
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        result = subprocess.run([chrome_path, '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', result.stdout)
            if version_match:
                return version_match.group(1)
    except:
        pass
    
    # Fallback to known version
    return "137.0.7151.122"

def download_chromedriver():
    """Download ChromeDriver manually from Google's official site"""
    try:
        print("Downloading ChromeDriver manually...")
        
        # Get the actual Chrome version
        chrome_version = get_chrome_version()
        print(f"Detected Chrome version: {chrome_version}")
        
        # Extract major version (e.g., 137 from 137.0.7151.122)
        major_version = chrome_version.split('.')[0]
        print(f"Chrome major version: {major_version}")
        
        # Get the ChromeDriver for your Chrome version
        api_url = "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"
        response = requests.get(api_url, timeout=10)
        data = response.json()
        
        # Find compatible ChromeDriver version (same major version)
        chromedriver_url = None
        compatible_version = None
        versions = data.get('versions', [])
        
        # Sort versions in descending order to get the latest compatible version
        sorted_versions = sorted(versions, key=lambda x: [int(v) for v in x.get('version', '0.0.0.0').split('.')], reverse=True)
        
        for version_info in sorted_versions:
            version = version_info.get('version', '')
            if version.startswith(major_version + '.'):
                downloads = version_info.get('downloads', {})
                chromedriver_downloads = downloads.get('chromedriver', [])
                
                for download in chromedriver_downloads:
                    if download.get('platform') == 'win64':
                        chromedriver_url = download.get('url')
                        compatible_version = version
                        break
                    elif download.get('platform') == 'win32':
                        chromedriver_url = download.get('url')
                        compatible_version = version
                        break
                
                if chromedriver_url:
                    break
        
        # If no compatible version found, try some fallback logic
        if not chromedriver_url:
            print(f"No ChromeDriver found for Chrome {major_version}, trying closest available versions...")
            
            # Try versions close to our major version
            for offset in [-1, 1, -2, 2]:
                target_major = str(int(major_version) + offset)
                print(f"Trying major version {target_major}...")
                
                for version_info in sorted_versions:
                    version = version_info.get('version', '')
                    if version.startswith(target_major + '.'):
                        downloads = version_info.get('downloads', {})
            chromedriver_downloads = downloads.get('chromedriver', [])
            
            for download in chromedriver_downloads:
                if download.get('platform') == 'win64':
                    chromedriver_url = download.get('url')
                    compatible_version = version
                    break
                elif download.get('platform') == 'win32':
                    chromedriver_url = download.get('url')
                    compatible_version = version
                    break
                
                if chromedriver_url:
                    break
        
        if not chromedriver_url:
            raise Exception("Could not find compatible ChromeDriver download URL")
        
        print(f"Found compatible ChromeDriver version: {compatible_version}")
        print(f"Downloading from: {chromedriver_url}")
        
        # Download the zip file
        response = requests.get(chromedriver_url, timeout=30)
        response.raise_for_status()
        
        # Create download directory
        download_dir = os.path.join(os.getcwd(), "chromedriver_download")
        os.makedirs(download_dir, exist_ok=True)
        
        # Clean up old downloads
        if os.path.exists(download_dir):
            shutil.rmtree(download_dir)
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
                    print(f"ChromeDriver {compatible_version} downloaded to: {chromedriver_path}")
                    return chromedriver_path
        
        raise Exception("Could not find chromedriver.exe in downloaded files")
        
    except Exception as e:
        print(f"Manual download failed: {e}")
        return None

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--enable-unsafe-swiftshader")
    chrome_options.add_argument("--window-size=1920x1080")
    
    # SSL and security related options to fix handshake errors
    chrome_options.add_argument("--ignore-ssl-errors")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--ignore-certificate-errors-spki-list")
    chrome_options.add_argument("--ignore-certificate-errors-skip-list")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    
    # chrome_options.add_argument("--headless")
    
    # Check if we already have a compatible chromedriver
    download_dir = os.path.join(os.getcwd(), "chromedriver_download")
    existing_chromedriver = None
    
    for root, dirs, files in os.walk(download_dir) if os.path.exists(download_dir) else []:
        for file in files:
            if file == "chromedriver.exe":
                existing_chromedriver = os.path.join(root, file)
                break
        if existing_chromedriver:
            break
    
    # Try existing chromedriver first
    if existing_chromedriver and os.path.exists(existing_chromedriver):
        print(f"Trying existing ChromeDriver: {existing_chromedriver}")
        try:
            service = Service(existing_chromedriver)
            driver = webdriver.Chrome(service=service, options=chrome_options)
            print("Successfully using existing ChromeDriver")
            return driver
        except Exception as e:
            print(f"Existing ChromeDriver failed: {e}")
            print("Will try to download a new one...")
    
    # Try manual download
    try:
        driver_path = download_chromedriver()
        if driver_path and os.path.exists(driver_path):
            print("Using newly downloaded ChromeDriver")
            service = Service(driver_path)
            return webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        print(f"Manual download failed: {e}")
    
    # Fallback to ChromeDriverManager
    print("Trying ChromeDriverManager as fallback...")
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        print(f"ChromeDriverManager also failed: {e}")
        raise Exception(f"All ChromeDriver methods failed. Please check your Chrome browser version and try again.")

def fill_job_creation_form(driver, form_data):
    """
    Fill the SERVPRO job creation form with provided data
    
    Args:
        driver: Selenium WebDriver instance
        form_data: Dictionary containing form data based on JSON schema
    """
    wait = WebDriverWait(driver, 10)
    
    print("🎯 Starting form filling process...")
    
    try:
        # Wait for form to be fully loaded
        print("⏳ Waiting for form to load...")
        time.sleep(3)
        
        # Fill General Information Section
        if 'generalInformation' in form_data:
            print("📝 Filling General Information...")
            fill_general_information(driver, wait, form_data['generalInformation'])
        
        # Fill Customer Information Section
        if 'customerInformation' in form_data:
            print("👤 Filling Customer Information...")
            fill_customer_information(driver, wait, form_data['customerInformation'])
        
        # Fill Job Address Information Section
        if 'jobAddressInformation' in form_data:
            print("🏠 Filling Job Address Information...")
            fill_job_address_information(driver, wait, form_data['jobAddressInformation'])
        
        # Fill Internal Participants Section
        if 'internalParticipants' in form_data:
            print("👥 Filling Internal Participants...")
            fill_internal_participants(driver, wait, form_data['internalParticipants'])
        
        # Fill External Participants Section
        if 'externalParticipants' in form_data:
            print("🤝 Filling External Participants...")
            fill_external_participants(driver, wait, form_data['externalParticipants'])
        
        # Fill Policy Information Section
        if 'policyInformation' in form_data:
            print("📋 Filling Policy Information...")
            fill_policy_information(driver, wait, form_data['policyInformation'])
        
        # Fill Division Section (Services)
        if 'division' in form_data:
            print("🔧 Filling Division/Services...")
            fill_division_services(driver, wait, form_data['division'])
        
        print("✅ Form filling completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during form filling: {str(e)}")
        raise

def fill_text_field(driver, wait, field_id, value, field_name=""):
    """Fill a text field by ID"""
    if not value:
        return
        
    try:
        # Try different methods to find and fill the field
        selectors_to_try = [
            (By.ID, field_id),
            (By.NAME, field_id),
            (By.XPATH, f"//input[@id='{field_id}']"),
            (By.XPATH, f"//textarea[@id='{field_id}']"),
        ]
        
        for selector_type, selector_value in selectors_to_try:
            try:
                field = wait.until(EC.presence_of_element_located((selector_type, selector_value)))
                if field.is_displayed() and field.is_enabled():
                    field.clear()
                    field.send_keys(value)
                    print(f"✅ Filled {field_name or field_id}: {value}")
                    return True
            except:
                continue
        
        # Try Telerik RadTextBox method
        try:
            script = f"$find('{field_id}').set_value('{value}');"
            driver.execute_script(script)
            print(f"✅ Filled {field_name or field_id} (Telerik): {value}")
            return True
        except:
            pass
            
        print(f"⚠️ Could not find/fill field: {field_name or field_id}")
        return False
        
    except Exception as e:
        print(f"❌ Error filling {field_name or field_id}: {str(e)}")
        return False

def fill_dropdown_field(driver, wait, field_id, value, field_name=""):
    """Fill a dropdown field by ID"""
    if not value:
        return
        
    try:
        # Try regular HTML select
        try:
            select_element = wait.until(EC.presence_of_element_located((By.ID, field_id)))
            if select_element.tag_name.lower() == 'select':
                select = Select(select_element)
                # Try by visible text first
                try:
                    select.select_by_visible_text(value)
                    print(f"✅ Selected {field_name or field_id}: {value}")
                    return True
                except:
                    # Try by value
                    try:
                        select.select_by_value(value)
                        print(f"✅ Selected {field_name or field_id}: {value}")
                        return True
                    except:
                        pass
        except:
            pass
        
        # Try Telerik RadComboBox/RadDropDownList
        try:
            # Method 1: Using Telerik API
            script = f"$find('{field_id}').set_text('{value}');"
            driver.execute_script(script)
            print(f"✅ Selected {field_name or field_id} (Telerik): {value}")
            return True
        except:
            pass
        
        try:
            # Method 2: Click and select
            dropdown = driver.find_element(By.ID, field_id)
            dropdown.click()
            time.sleep(1)
            
            # Look for dropdown items
            dropdown_items = driver.find_elements(By.XPATH, f"//li[contains(text(), '{value}')]")
            for item in dropdown_items:
                if item.is_displayed():
                    item.click()
                    print(f"✅ Selected {field_name or field_id}: {value}")
                    return True
        except:
            pass
            
        print(f"⚠️ Could not find/select dropdown: {field_name or field_id}")
        return False
        
    except Exception as e:
        print(f"❌ Error selecting {field_name or field_id}: {str(e)}")
        return False

def fill_checkbox_field(driver, wait, field_id, checked, field_name=""):
    """Fill a checkbox field by ID"""
    try:
        checkbox = wait.until(EC.presence_of_element_located((By.ID, field_id)))
        current_state = checkbox.is_selected()
        
        if current_state != checked:
            checkbox.click()
            print(f"✅ {'Checked' if checked else 'Unchecked'} {field_name or field_id}")
        else:
            print(f"✅ {field_name or field_id} already in correct state")
        return True
        
    except Exception as e:
        print(f"❌ Error with checkbox {field_name or field_id}: {str(e)}")
        return False

def fill_telerik_text_field(driver, wait, field_id, value, field_name=""):
    """Fill a Telerik RadTextBox field"""
    if not value:
        return False
        
    try:
        print(f"    🔧 Attempting to fill Telerik text field: {field_name}")
        
        # Method 1: Try direct input element interaction
        try:
            field = wait.until(EC.presence_of_element_located((By.ID, field_id)))
            if field.is_displayed() and field.is_enabled():
                # Clear the field first
                field.clear()
                time.sleep(0.5)
                # Send the value
                field.send_keys(value)
                print(f"✅ Filled Telerik text field {field_name}: {value}")
                return True
        except Exception as e:
            print(f"    ⚠️ Direct input method failed: {str(e)}")
        
        # Method 2: Try JavaScript with Telerik API
        try:
            # Remove the '_Input' suffix to get the base control ID
            base_id = field_id.replace('_Input', '')
            script = f"$find('{base_id}').set_value('{value}');"
            driver.execute_script(script)
            print(f"✅ Filled Telerik text field {field_name} (JavaScript): {value}")
            return True
        except Exception as e:
            print(f"    ⚠️ Telerik API method failed: {str(e)}")
        
        # Method 3: Try JavaScript direct value assignment
        try:
            script = f"document.getElementById('{field_id}').value = '{value}';"
            driver.execute_script(script)
            print(f"✅ Filled Telerik text field {field_name} (Direct JS): {value}")
            return True
        except Exception as e:
            print(f"    ⚠️ Direct JS method failed: {str(e)}")
            
        print(f"❌ Could not fill Telerik text field: {field_name}")
        return False
        
    except Exception as e:
        print(f"❌ Error filling Telerik text field {field_name}: {str(e)}")
        return False

def fill_telerik_dropdown_field(driver, wait, field_id, value, field_name=""):
    """Fill a Telerik RadComboBox dropdown field"""
    if not value:
        return False
        
    try:
        print(f"    🔧 Attempting to fill Telerik dropdown: {field_name}")
        
        # Method 1: Try Telerik RadComboBox API
        try:
            # Remove the '_Input' suffix to get the base control ID
            base_id = field_id.replace('_Input', '')
            script = f"$find('{base_id}').set_text('{value}');"
            driver.execute_script(script)
            time.sleep(1)
            print(f"✅ Selected Telerik dropdown {field_name} (API): {value}")
            return True
        except Exception as e:
            print(f"    ⚠️ Telerik API method failed: {str(e)}")
        
        # Method 2: Try clicking and selecting from dropdown
        try:
            # Click the input field to open dropdown
            input_field = wait.until(EC.element_to_be_clickable((By.ID, field_id)))
            input_field.click()
            time.sleep(1)
            
            # Look for dropdown items containing the value
            dropdown_items = driver.find_elements(By.XPATH, f"//li[contains(text(), '{value}')]")
            for item in dropdown_items:
                if item.is_displayed():
                    item.click()
                    print(f"✅ Selected Telerik dropdown {field_name} (Click): {value}")
                    return True
            
            # Try alternative dropdown item selectors
            dropdown_items = driver.find_elements(By.XPATH, f"//li[@class='rcbItem' and contains(text(), '{value}')]")
            for item in dropdown_items:
                if item.is_displayed():
                    item.click()
                    print(f"✅ Selected Telerik dropdown {field_name} (rcbItem): {value}")
                    return True
                    
        except Exception as e:
            print(f"    ⚠️ Click method failed: {str(e)}")
        
        # Method 3: Try direct input value setting
        try:
            input_field = driver.find_element(By.ID, field_id)
            driver.execute_script(f"arguments[0].value = '{value}';", input_field)
            print(f"✅ Set Telerik dropdown {field_name} (Direct): {value}")
            return True
        except Exception as e:
            print(f"    ⚠️ Direct method failed: {str(e)}")
            
        print(f"❌ Could not fill Telerik dropdown: {field_name}")
        return False
        
    except Exception as e:
        print(f"❌ Error filling Telerik dropdown {field_name}: {str(e)}")
        return False

def fill_telerik_date_field(driver, wait, field_id, date_value, field_name=""):
    """Fill a Telerik RadDatePicker field"""
    if not date_value:
        return False
        
    try:
        print(f"    🔧 Attempting to fill Telerik date field: {field_name}")
        
        # Method 1: Try Telerik RadDatePicker API
        try:
            # Get the base control ID (remove _dateInput suffix)
            base_id = field_id.replace('_dateInput', '')
            script = f"$find('{base_id}').set_value(new Date('{date_value}'));"
            driver.execute_script(script)
            print(f"✅ Set Telerik date {field_name} (API): {date_value}")
            return True
        except Exception as e:
            print(f"    ⚠️ Telerik API method failed: {str(e)}")
        
        # Method 2: Try direct input field interaction
        try:
            date_field = wait.until(EC.presence_of_element_located((By.ID, field_id)))
            if date_field.is_displayed() and date_field.is_enabled():
                date_field.clear()
                time.sleep(0.5)
                date_field.send_keys(date_value)
                print(f"✅ Set Telerik date {field_name} (Direct): {date_value}")
                return True
        except Exception as e:
            print(f"    ⚠️ Direct input method failed: {str(e)}")
        
        # Method 3: Try JavaScript direct value assignment
        try:
            script = f"document.getElementById('{field_id}').value = '{date_value}';"
            driver.execute_script(script)
            print(f"✅ Set Telerik date {field_name} (JS): {date_value}")
            return True
        except Exception as e:
            print(f"    ⚠️ JS method failed: {str(e)}")
            
        print(f"❌ Could not fill Telerik date field: {field_name}")
        return False
        
    except Exception as e:
        print(f"❌ Error filling Telerik date {field_name}: {str(e)}")
        return False

def fill_date_field(driver, wait, field_id, date_value, field_name=""):
    """Fill a date field by ID"""
    if not date_value:
        return
        
    try:
        # Try Telerik RadDatePicker
        try:
            script = f"$find('{field_id}').set_value('{date_value}');"
            driver.execute_script(script)
            print(f"✅ Set date {field_name or field_id} (Telerik): {date_value}")
            return True
        except:
            pass
        
        # Try regular date input
        try:
            date_field = wait.until(EC.presence_of_element_located((By.ID, field_id)))
            date_field.clear()
            date_field.send_keys(date_value)
            print(f"✅ Set date {field_name or field_id}: {date_value}")
            return True
        except:
            pass
            
        print(f"⚠️ Could not find/fill date field: {field_name or field_id}")
        return False
        
    except Exception as e:
        print(f"❌ Error filling date {field_name or field_id}: {str(e)}")
        return False

def fill_general_information(driver, wait, data):
    """Fill the General Information section"""
    print("🎯 Filling General Information section with correct field IDs...")
    
    # CORRECT Field mappings based on actual HTML source code
    field_mappings = {
        'receivedBy': 'ctl00_ContentPlaceHolder1_JobParentInformation_GenaralInfo_comboBox_ReceivedBy_Input',
        'jobName': 'ctl00_ContentPlaceHolder1_JobParentInformation_GenaralInfo_JobNameRadTextBox',
        'reportedBy': 'ctl00_ContentPlaceHolder1_JobParentInformation_GenaralInfo_DropDown_ReportedBY_Input',
        'referredBy': 'ctl00_ContentPlaceHolder1_JobParentInformation_GenaralInfo_DropDown_ReferredBy_Input',
        'jobSize': 'ctl00_ContentPlaceHolder1_JobParentInformation_GenaralInfo_JobSizeComboBox_Input',
        'officeName': 'ctl00_ContentPlaceHolder1_JobParentInformation_GenaralInfo_comboBoxOffice_Input',
        'dateOfLoss': 'ctl00_ContentPlaceHolder1_JobParentInformation_GenaralInfo_DatePicker_DateOffLoss_dateInput',
        'lossCategory': 'ctl00_ContentPlaceHolder1_JobParentInformation_GenaralInfo_comboBox_LossCategory_Input',
        'environmentalCode': 'ctl00_ContentPlaceHolder1_JobParentInformation_GenaralInfo_comboBoxEnvironmentalCode_Input',
        'catReference': 'ctl00_ContentPlaceHolder1_JobParentInformation_GenaralInfo_RadComboBox_Catastrophe_Input',
        'priority': 'ctl00_ContentPlaceHolder1_JobParentInformation_GenaralInfo_comboBoxPriority_Input',
        'lossType': 'ctl00_ContentPlaceHolder1_JobParentInformation_GenaralInfo_comboBox_LossType_Input',
        'secondaryLossType': 'ctl00_ContentPlaceHolder1_JobParentInformation_GenaralInfo_comboBox_SecondryLossType_Input',
        'sourceOfLoss': 'ctl00_ContentPlaceHolder1_JobParentInformation_GenaralInfo_SourceOfLossComboBox_Input'
    }
    
    for field_name, field_id in field_mappings.items():
        if field_name in data and data[field_name]:
            value = data[field_name]
            print(f"  🔍 Processing field: {field_name} = {value}")
            
            if field_name == 'dateOfLoss':
                fill_telerik_date_field(driver, wait, field_id, value, field_name)
            elif field_name in ['reportedBy', 'jobSize', 'officeName', 'lossCategory', 'environmentalCode', 'catReference', 'priority', 'lossType', 'secondaryLossType', 'sourceOfLoss']:
                fill_telerik_dropdown_field(driver, wait, field_id, value, field_name)
            elif field_name == 'jobName':
                fill_telerik_text_field(driver, wait, field_id, value, field_name)
            else:
                fill_text_field(driver, wait, field_id, value, field_name)

def fill_customer_information(driver, wait, data):
    """Fill the Customer Information section"""
    print("🎯 Filling Customer Information section with correct field IDs...")
    
    # Handle customer type radio buttons
    if 'customerType' in data:
        customer_type = data['customerType']
        if customer_type == 'Individual':
            radio_id = 'ctl00_ContentPlaceHolder1_JobParentInformation_RadioButton_IndividualCustomer'
        else:
            radio_id = 'ctl00_ContentPlaceHolder1_JobParentInformation_RadioButton_CompanyCustomer'
        
        try:
            radio_button = wait.until(EC.element_to_be_clickable((By.ID, radio_id)))
            radio_button.click()
            print(f"✅ Selected customer type: {customer_type}")
            time.sleep(1)  # Wait for form to update
        except Exception as e:
            print(f"❌ Error selecting customer type: {str(e)}")
    
    # CORRECT Field mappings based on actual HTML source code for Individual Customer
    field_mappings = {
        'customer': 'ctl00_ContentPlaceHolder1_JobParentInformation_DropDown_Customer_Input',
        'title': 'ctl00_ContentPlaceHolder1_JobParentInformation_ctl17_TitleDropDownTree',
        'firstName': 'ctl00_ContentPlaceHolder1_JobParentInformation_TextBox_FirstName',
        'lastName': 'ctl00_ContentPlaceHolder1_JobParentInformation_TextBox_LastName',
        'email': 'ctl00_ContentPlaceHolder1_JobParentInformation_TextBox_Email',
        'secondaryEmail': 'ctl00_ContentPlaceHolder1_JobParentInformation_TextBox_SecondaryEmail',
        'address': 'ctl00_ContentPlaceHolder1_JobParentInformation_TextBox_Address_Input',
        'zipCode': 'ctl00_ContentPlaceHolder1_JobParentInformation_TextBox_Zip',
        'city': 'ctl00_ContentPlaceHolder1_JobParentInformation_TextBox_City',
        'countyRegion': 'ctl00_ContentPlaceHolder1_JobParentInformation_comboBox_CustomerCounty_Input',
        'country': 'ctl00_ContentPlaceHolder1_JobParentInformation_DropDown_Country_Input',
        'stateProvince': 'ctl00_ContentPlaceHolder1_JobParentInformation_DropDown_State_Input'
    }
    
    # Handle "Same as Job Address" checkbox
    if 'isSameAsJobAddress' in data and data['isSameAsJobAddress']:
        fill_checkbox_field(driver, wait, 'ctl00_ContentPlaceHolder1_JobParentInformation_CheckBox_SameAsIndividualLossAddress', 
                           data['isSameAsJobAddress'], 'Same as Job Address')
    
    for field_name, field_id in field_mappings.items():
        if field_name in data and data[field_name]:
            value = data[field_name]
            print(f"  🔍 Processing Customer field: {field_name} = {value}")
            
            if field_name == 'title':
                # Handle title dropdown tree (complex control)
                fill_telerik_dropdown_field(driver, wait, field_id, value, field_name)
            elif field_name in ['customer', 'countyRegion', 'country', 'stateProvince']:
                fill_telerik_dropdown_field(driver, wait, field_id, value, field_name)
            elif field_name == 'address':
                # Handle RadSearchBox for address
                fill_telerik_text_field(driver, wait, field_id, value, field_name)
            elif field_name in ['firstName', 'lastName', 'email', 'secondaryEmail', 'zipCode', 'city']:
                fill_telerik_text_field(driver, wait, field_id, value, field_name)
    
    # Handle phone numbers with correct IDs
    if 'mainPhoneNumber' in data:
        phone_data = data['mainPhoneNumber']
        if 'number' in phone_data and phone_data['number']:
            fill_text_field(driver, wait, 'ctl00_ContentPlaceHolder1_JobParentInformation_TextBox_MainPhone', 
                          phone_data['number'], 'Main Phone')
        if 'extension' in phone_data and phone_data['extension']:
            fill_text_field(driver, wait, 'ctl00_ContentPlaceHolder1_JobParentInformation_TextBox_MainPhoneExt', 
                          phone_data['extension'], 'Main Phone Extension')
        if 'type' in phone_data and phone_data['type']:
            # Handle phone type dropdown if needed
            pass

def fill_job_address_information(driver, wait, data):
    """Fill the Job Address Information section"""
    print("🎯 Filling Job Address Information section with correct field IDs...")
    
    # Handle "Same as Customer Address" checkbox
    if 'isSameAsCustomerAddress' in data and data['isSameAsCustomerAddress']:
        fill_checkbox_field(driver, wait, 'ctl00_ContentPlaceHolder1_JobParentInformation_CheckBox_SameIndividualAddress', 
                           data['isSameAsCustomerAddress'], 'Same as Customer Address')
    
    # CORRECT Field mappings based on actual HTML source code for Job Address Information
    field_mappings = {
        'firstName': 'ctl00_ContentPlaceHolder1_JobParentInformation_TextBox_FirstNameLoss',
        'lastName': 'ctl00_ContentPlaceHolder1_JobParentInformation_TextBox_LastNameLoss',
        'address': 'ctl00_ContentPlaceHolder1_JobParentInformation_TextBox_AddressLoss_Input',
        'zipCode': 'ctl00_ContentPlaceHolder1_JobParentInformation_TextBox_ZipLoss',
        'city': 'ctl00_ContentPlaceHolder1_JobParentInformation_TextBox_CityLoss',
        'countyRegion': 'ctl00_ContentPlaceHolder1_JobParentInformation_comboBox_CustomerLossCounty_Input',
        'country': 'ctl00_ContentPlaceHolder1_JobParentInformation_DropDown_CountryLoss_Input',
        'stateProvince': 'ctl00_ContentPlaceHolder1_JobParentInformation_DropDown_StateLoss_Input'
    }
    
    for field_name, field_id in field_mappings.items():
        if field_name in data and data[field_name]:
            value = data[field_name]
            print(f"  🔍 Processing Job Address field: {field_name} = {value}")
            
            if field_name in ['countyRegion', 'country', 'stateProvince']:
                fill_telerik_dropdown_field(driver, wait, field_id, value, f"Loss {field_name}")
            elif field_name == 'address':
                # Handle RadSearchBox for address
                fill_telerik_text_field(driver, wait, field_id, value, f"Loss {field_name}")
            else:
                # Handle text fields
                fill_telerik_text_field(driver, wait, field_id, value, f"Loss {field_name}")
    
    # Handle phone numbers for Job Address
    if 'mainPhoneNumber' in data:
        phone_data = data['mainPhoneNumber']
        if 'number' in phone_data and phone_data['number']:
            fill_text_field(driver, wait, 'ctl00_ContentPlaceHolder1_JobParentInformation_TextBox_MainPhoneLoss', 
                          phone_data['number'], 'Job Address Main Phone')
        if 'extension' in phone_data and phone_data['extension']:
            fill_text_field(driver, wait, 'ctl00_ContentPlaceHolder1_JobParentInformation_TextBox_MainPhoneLossExtension', 
                          phone_data['extension'], 'Job Address Main Phone Extension')

def fill_internal_participants(driver, wait, data):
    """Fill the Internal Participants section"""
    print("🎯 Filling Internal Participants section with correct field IDs...")
    
    # CORRECT Field mappings based on actual HTML source code
    field_mappings = {
        'estimator': 'ctl00_ContentPlaceHolder1_JobParentInformation_InternalParticpantsControl_InternalParticipantsList_ctl00_EstimatorComboBox_Input',
        'coordinator': 'ctl00_ContentPlaceHolder1_JobParentInformation_InternalParticpantsControl_InternalParticipantsList_ctl01_EstimatorComboBox_Input',
        'supervisor': 'ctl00_ContentPlaceHolder1_JobParentInformation_InternalParticpantsControl_InternalParticipantsList_ctl02_EstimatorComboBox_Input',
        'foreman': 'ctl00_ContentPlaceHolder1_JobParentInformation_InternalParticpantsControl_InternalParticipantsList_ctl03_EstimatorComboBox_Input',
        'accounting': 'ctl00_ContentPlaceHolder1_JobParentInformation_InternalParticpantsControl_InternalParticipantsList_ctl04_EstimatorComboBox_Input',
        'marketing': 'ctl00_ContentPlaceHolder1_JobParentInformation_InternalParticpantsControl_InternalParticipantsList_ctl05_EstimatorComboBox_Input',
        'dispatcher': 'ctl00_ContentPlaceHolder1_JobParentInformation_InternalParticpantsControl_InternalParticipantsList_ctl06_EstimatorComboBox_Input',
        'naAdministrator': 'ctl00_ContentPlaceHolder1_JobParentInformation_InternalParticpantsControl_InternalParticipantsList_ctl07_EstimatorComboBox_Input',
        'naFieldAccountsManager': 'ctl00_ContentPlaceHolder1_JobParentInformation_InternalParticpantsControl_InternalParticipantsList_ctl08_EstimatorComboBox_Input'
    }
    
    for field_name, field_id in field_mappings.items():
        if field_name in data and data[field_name]:
            value = data[field_name]
            print(f"  🔍 Processing Internal Participant field: {field_name} = {value}")
            # All fields are Telerik RadComboBox controls
            fill_telerik_dropdown_field(driver, wait, field_id, value, field_name)

def fill_external_participants(driver, wait, data):
    """Fill the External Participants section"""
    field_mappings = {
        'brokerAgent': 'ctl00_ContentPlaceHolder1_JobParentInformation_ExternalParticipants_ComboBox_BrokerAgent',
        'brokerAgentContact': 'ctl00_ContentPlaceHolder1_JobParentInformation_ExternalParticipants_ComboBox_BrokerAgentContact',
        'insuranceCarrier': 'ctl00_ContentPlaceHolder1_JobParentInformation_ExternalParticipants_ComboBox_InsuranceCarrier',
        'primaryAdjuster': 'ctl00_ContentPlaceHolder1_JobParentInformation_ExternalParticipants_ComboBox_PrimaryAdjuster',
        'primaryFieldAdjuster': 'ctl00_ContentPlaceHolder1_JobParentInformation_ExternalParticipants_ComboBox_PrimaryFieldAdjuster',
        'propertyManagement': 'ctl00_ContentPlaceHolder1_JobParentInformation_ExternalParticipants_ComboBox_PropertyManagement',
        'propertyManagementContact': 'ctl00_ContentPlaceHolder1_JobParentInformation_ExternalParticipants_ComboBox_PropertyManagementContact',
        'contractorCompany': 'ctl00_ContentPlaceHolder1_JobParentInformation_ExternalParticipants_ComboBox_ContractorCompany',
        'contractorContact': 'ctl00_ContentPlaceHolder1_JobParentInformation_ExternalParticipants_ComboBox_ContractorContact'
    }
    
    for field_name, field_id in field_mappings.items():
        if field_name in data and data[field_name]:
            fill_dropdown_field(driver, wait, field_id, data[field_name], field_name)

def fill_policy_information(driver, wait, data):
    """Fill the Policy Information section"""
    field_mappings = {
        'claimNumber': 'ctl00_ContentPlaceHolder1_JobParentInformation_TextBox_ClaimNumber',
        'fileNumber': 'ctl00_ContentPlaceHolder1_JobParentInformation_TextBox_FileNumber',
        'policyNumber': 'ctl00_ContentPlaceHolder1_JobParentInformation_TextBox_PolicyNumber',
        'yearBuilt': 'ctl00_ContentPlaceHolder1_JobParentInformation_TextBox_YearBuilt'
    }
    
    for field_name, field_id in field_mappings.items():
        if field_name in data and data[field_name]:
            value = str(data[field_name])
            fill_text_field(driver, wait, field_id, value, field_name)
    
    # Handle date fields
    date_mappings = {
        'policyStartDate': 'ctl00_ContentPlaceHolder1_JobParentInformation_DatePicker_PolicyStartDate',
        'policyExpirationDate': 'ctl00_ContentPlaceHolder1_JobParentInformation_DatePicker_PolicyExpirationDate'
    }
    
    for field_name, field_id in date_mappings.items():
        if field_name in data and data[field_name]:
            fill_date_field(driver, wait, field_id, data[field_name], field_name)

def fill_division_services(driver, wait, data):
    """Fill the Division/Services section"""
    if 'servicesSelected' in data:
        services = data['servicesSelected']
        
        # Handle checkbox list for services
        try:
            checkbox_list = driver.find_element(By.ID, 'ctl00_ContentPlaceHolder1_JobParentInformation_CheckBoxList_Division')
            checkboxes = checkbox_list.find_elements(By.TAG_NAME, 'input')
            
            for checkbox in checkboxes:
                label_element = checkbox.find_element(By.XPATH, "../label")
                label_text = label_element.text.strip()
                
                if label_text in services:
                    if not checkbox.is_selected():
                        checkbox.click()
                        print(f"✅ Selected service: {label_text}")
                        
        except Exception as e:
            print(f"❌ Error selecting services: {str(e)}")

def fill_general_information_only(driver, form_data):
    """
    Fill only the General Information section for testing purposes
    
    Args:
        driver: Selenium WebDriver instance
        form_data: Dictionary containing form data
    """
    wait = WebDriverWait(driver, 10)
    
    print("🎯 Starting General Information section test...")
    
    try:
        # Wait for form to be fully loaded
        print("⏳ Waiting for form to load...")
        time.sleep(3)
        
        # Fill only General Information Section
        if 'generalInformation' in form_data:
            print("📝 Testing General Information section...")
            fill_general_information(driver, wait, form_data['generalInformation'])
        else:
            print("❌ No general information data found in form data")
        
        print("✅ General Information section test completed!")
        
    except Exception as e:
        print(f"❌ Error during General Information test: {str(e)}")
        raise

def fill_customer_and_job_address_only(driver, form_data):
    """
    Fill only the Customer Information and Job Address Information sections for testing purposes
    
    Args:
        driver: Selenium WebDriver instance
        form_data: Dictionary containing form data
    """
    wait = WebDriverWait(driver, 10)
    
    print("🎯 Starting Customer Information and Job Address Information section test...")
    
    try:
        # Wait for form to be fully loaded
        print("⏳ Waiting for form to load...")
        time.sleep(3)
        
        # Fill Customer Information Section
        if 'customerInformation' in form_data:
            print("📝 Testing Customer Information section...")
            fill_customer_information(driver, wait, form_data['customerInformation'])
            
            # Small delay between sections
            time.sleep(2)
        else:
            print("❌ No customer information data found in form data")
        
        # Fill Job Address Information Section
        if 'jobAddressInformation' in form_data:
            print("📝 Testing Job Address Information section...")
            fill_job_address_information(driver, wait, form_data['jobAddressInformation'])
        else:
            print("❌ No job address information data found in form data")
        
        print("✅ Customer Information and Job Address Information section test completed!")
        
    except Exception as e:
        print(f"❌ Error during Customer/Job Address test: {str(e)}")
        raise

def fill_internal_participants_only(driver, form_data):
    """
    Fill only the Internal Participants section for testing purposes
    
    Args:
        driver: Selenium WebDriver instance
        form_data: Dictionary containing form data
    """
    wait = WebDriverWait(driver, 10)
    
    print("🎯 Starting Internal Participants section test...")
    
    try:
        # Wait for form to be fully loaded
        print("⏳ Waiting for form to load...")
        time.sleep(3)
        
        # Fill Internal Participants Section
        if 'internalParticipants' in form_data:
            print("📝 Testing Internal Participants section...")
            fill_internal_participants(driver, wait, form_data['internalParticipants'])
        else:
            print("❌ No internal participants data found in form data")
        
        print("✅ Internal Participants section test completed!")
        
    except Exception as e:
        print(f"❌ Error during Internal Participants test: {str(e)}")
        raise

def create_sample_form_data():
    """
    Create sample form data based on the JSON schema
    You can modify this data or load it from an external JSON file
    """
    return {
        "generalInformation": {
            "receivedBy": "Kyle McDougall",
            "jobName": "Smith, John - Water Damage",
            "reportedBy": "Property Owner",
            "referredBy": "Lewis, A.D.",
            "jobSize": "Medium",
            "officeName": "SPSC, LLC",
            "dateOfLoss": "12/15/2024",
            "lossCategory": "Residential",
            "environmentalCode": "Mitigation",
            "catReference": "",
            "priority": "High",
            "lossType": "General Repairs",
            "secondaryLossType": "Mold",
            "sourceOfLoss": "Pipe Break"
        },
        "customerInformation": {
            "customerType": "Individual",
            "isSameAsJobAddress": False,
            "customer": "",
            "title": "Mr.",
            "firstName": "John",
            "lastName": "Smith",
            "email": "john.smith@email.com",
            "secondaryEmail": "john.alt@email.com",
            "address": "123 Main Street",
            "zipCode": "30309",
            "city": "Atlanta",
            "countyRegion": "Fulton County",
            "country": "USA",
            "stateProvince": "Georgia",
            "mainPhoneNumber": {
                "number": "1-404-555-1234",
                "extension": "",
                "type": "Mobile"
            }
        },
        "jobAddressInformation": {
            "isSameAsCustomerAddress": False,
            "firstName": "John",
            "lastName": "Smith",
            "address": "456 Loss Address Street",
            "zipCode": "30309",
            "city": "Atlanta",
            "countyRegion": "Fulton County",
            "country": "USA",
            "stateProvince": "Georgia",
            "mainPhoneNumber": {
                "number": "1-404-555-5678",
                "extension": "",
                "type": "Home"
            }
        },
        "internalParticipants": {
            "estimator": "Kyle McDougall",
            "coordinator": "Sarah Johnson",
            "supervisor": "Mike Wilson",
            "foreman": "Tom Rodriguez",
            "accounting": "Lisa Chen",
            "Marketing": "Adams, Sherri",
            "Dispatcher": "Adams, Sherri",
            "NA Administrator": "Adams, Sherri",
            "NA Field Accounts Manager": "Adams, Sherri"
        },
        "externalParticipants": {
            "brokerAgent": "",
            "brokerAgentContact": "",
            "insuranceCarrier": "State Farm",
            "primaryAdjuster": "Mark Davis",
            "primaryFieldAdjuster": "",
            "propertyManagement": "",
            "propertyManagementContact": "",
            "contractorCompany": "",
            "contractorContact": "",
            "independentAdjustingFirm": "",
            "independentAdjusterContact": "",
            "publicAdjustingFirm": "",
            "publicAdjusterContact": "",
            "primaryMortgage": "",
            "secondaryMortgage": "",
            "tpaCompany": "",
            "tpa": "",
            "billToCompany": "",
            "billToContact": "",
            "secondaryContact": "",
            "businessContact": ""
        },
        "policyInformation": {
            "claimNumber": "SF-2024-12345",
            "fileNumber": "FILE-001",
            "policyNumber": "POL-987654321",
            "yearBuilt": 1995,
            "policyStartDate": "01/01/2024",
            "policyExpirationDate": "01/01/2025"
        },
        "division": {
            "servicesSelected": [
                "Water Damage Restoration",
                "Structural Drying",
                "Mold Remediation"
            ]
        }
    }

def load_form_data_from_json(json_file_path):
    """
    Load form data from a JSON file
    
    Args:
        json_file_path: Path to the JSON file containing form data
    
    Returns:
        Dictionary containing form data
    """
    import json
    
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
        print(f"✅ Loaded form data from {json_file_path}")
        return data
    except FileNotFoundError:
        print(f"❌ JSON file not found: {json_file_path}")
        print("Using sample data instead...")
        return create_sample_form_data()
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON file: {str(e)}")
        print("Using sample data instead...")
        return create_sample_form_data()
    except Exception as e:
        print(f"❌ Error loading JSON file: {str(e)}")
        print("Using sample data instead...")
        return create_sample_form_data()

def servpro_login():
    """Login to SERVPRO using exact element IDs and handle popups"""
    
    # Credentials
    login_url = "https://servpro.ngsapps.net/Enterprise/Module/User/Login.aspx"
    job_creation_url = "https://servpro.ngsapps.net/Enterprise/Module/Job/CreateJob.aspx"
    username = "kymcdougall"
    password = "SERVYpro123#"
    company_id = "43513"
    
    print(f"Using credentials - Username: {username}, Company ID: {company_id}")
    
    # Initialize Chrome WebDriver
    print("Initializing browser...")
    driver = setup_driver()
    driver.maximize_window()
    wait = WebDriverWait(driver, 10)
    
    try:
        # Navigate to login page
        print("Navigating to login URL...")
        driver.get(login_url)
        print("Waiting for page to load...")
        time.sleep(2)  # Increased wait time to ensure page loads
        
        # Print the page title to confirm we're on the right page
        print(f"Page title: {driver.title}")
        
        # All fields are on the same page - fill them all and then submit
        print("\nFilling out the login form (all fields on same page)...")
        
        # STEP 1: Find and enter Company ID
        print("\nLooking for Company ID field...")
        try:
            # Try multiple possible selectors for Company ID field
            company_field = None
            selectors = [
                (By.ID, "txtCompanyID"),
                (By.NAME, "CompanyID"),
                (By.XPATH, "//input[@placeholder='Company ID']"),
                (By.XPATH, "//input[contains(@id, 'Company')]"),
                (By.XPATH, "//input[@type='text'][1]")  # First text input as fallback
            ]
            
            for selector_type, selector_value in selectors:
                try:
                    company_field = wait.until(EC.presence_of_element_located((selector_type, selector_value)))
                    print(f"Found company ID field using {selector_type}: {selector_value}")
                    break
                except:
                    continue
            
            if company_field:
                company_field.clear()
                company_field.send_keys(company_id)
                print(f"Entered company ID: {company_id}")
            else:
                raise Exception("Could not find Company ID field")
                
        except Exception as e:
            print(f"Error with company ID field: {str(e)}")
            raise
        
        # STEP 2: Find and enter Username
        print("\nLooking for Username field...")
        try:
            # Try multiple possible selectors for Username field
            username_field = None
            selectors = [
                (By.ID, "txtUserName"),
                (By.ID, "txtUsername"),
                (By.NAME, "UserName"),
                (By.NAME, "Username"),
                (By.XPATH, "//input[@placeholder='User Name']"),
                (By.XPATH, "//input[contains(@id, 'User')]"),
                (By.XPATH, "//input[@type='text'][2]")  # Second text input as fallback
            ]
            
            for selector_type, selector_value in selectors:
                try:
                    username_field = wait.until(EC.presence_of_element_located((selector_type, selector_value)))
                    print(f"Found username field using {selector_type}: {selector_value}")
                    break
                except:
                    continue
            
            if username_field:
                username_field.clear()
                username_field.send_keys(username)
                print(f"Entered username: {username}")
            else:
                raise Exception("Could not find Username field")
                
        except Exception as e:
            print(f"Error with username field: {str(e)}")
            raise
        
        # STEP 3: Find and enter Password
        print("\nLooking for Password field...")
        try:
            # Try multiple possible selectors for Password field
            password_field = None
            selectors = [
                (By.ID, "txtPassword"),
                (By.NAME, "Password"),
                (By.XPATH, "//input[@placeholder='Password']"),
                (By.XPATH, "//input[contains(@id, 'Password')]"),
                (By.XPATH, "//input[@type='password']")
            ]
            
            password_field = None
            for selector_type, selector_value in selectors:
                try:
                    password_field = wait.until(EC.presence_of_element_located((selector_type, selector_value)))
                    print(f"Found password field using {selector_type}: {selector_value}")
                    break
                except:
                    continue
            
            if password_field:
                password_field.clear()
                password_field.send_keys(password)
                print("Entered password")
            else:
                raise Exception("Could not find Password field")
                
        except Exception as e:
            print(f"Error with password field: {str(e)}")
            raise
        
        # STEP 4: Find and click Login/Submit button
        print("\nLooking for Login/Submit button...")
        try:
            # Try multiple possible selectors for the submit button
            login_button = None
            selectors = [
                (By.ID, "btnLogin"),
                (By.XPATH, "//input[@value='Login']"),
                (By.XPATH, "//button[contains(text(), 'Login')]"),
                (By.XPATH, "//input[@type='submit']"),
                (By.XPATH, "//button[@type='submit']"),
                (By.XPATH, "//input[contains(@value, 'Log')]"),
                (By.XPATH, "//button[contains(@class, 'btn')]")
            ]
            
            for selector_type, selector_value in selectors:
                try:
                    login_button = wait.until(EC.element_to_be_clickable((selector_type, selector_value)))
                    print(f"Found login button using {selector_type}: {selector_value}")
                    break
                except:
                    continue
            
            if login_button:
                login_button.click()
                print("Clicked Login button")
            else:
                raise Exception("Could not find Login button")
                
        except Exception as e:
            print(f"Error with login button: {str(e)}")
            raise
        
        # Wait for login to complete
        print("\nWaiting for login to complete...")
        time.sleep(5)  # Increased wait time
        
        # Check if login was successful
        current_url = driver.current_url
        print(f"Current URL after login: {current_url}")
        
        # Better login success detection - check for post-login URLs
        login_successful = False
        success_indicators = [
            "uPostLogin.aspx",  # Post-login page
            "Default.aspx",     # Dashboard
            "Home.aspx",        # Home page
            "Main.aspx"         # Main page
        ]
        
        for indicator in success_indicators:
            if indicator in current_url:
                login_successful = True
                break
        
        # Also check if we're NOT on the actual login page
        if not login_successful and "/User/Login.aspx" not in current_url:
            login_successful = True
        
        print(f"Login successful: {login_successful}")
        
        if login_successful:
            print("✅ Login successful!")
            
            # Handle sequential popups that appear after login
            print("\n🔍 Handling post-login popups (expecting 2 sequential popups)...")
            
            # Handle alerts first
            try:
                alert = driver.switch_to.alert
                alert_text = alert.text
                print(f"⚠️ Alert found: {alert_text}")
                alert.dismiss()
                print("✅ Alert dismissed")
                time.sleep(1)
            except NoAlertPresentException:
                print("✅ No alert present")
            
            # Handle multiple popups that appear sequentially
            max_popup_attempts = 5  # Try to handle up to 5 popups
            
            for attempt in range(max_popup_attempts):
                print(f"\n🔍 Popup handling attempt {attempt + 1}/{max_popup_attempts}...")
                
                popup_found = False
                
                # Comprehensive popup selectors
                popup_selectors = [
                    "//div[contains(@class, 'modal') and contains(@style, 'display: block')]",
                    "//div[contains(@class, 'modal') and not(contains(@style, 'display: none'))]",
                    "//div[contains(@class, 'popup')]",
                    "//div[contains(@class, 'dialog')]",
                    "//div[contains(@class, 'overlay')]",
                    "//*[@id='fe068648-9018-90c3-4d38-d203bd76795d']",
                    "//*[@id='b0c2df4f-24fe-e545-2fa8-b6b19f9ae171']",
                    "//div[@role='dialog']",
                    "//div[contains(@class, 'ui-dialog')]",
                    "//div[contains(@id, 'popup')]",
                    "//div[contains(@id, 'modal')]"
                ]
                
                # Try each selector to find visible popups
                for selector in popup_selectors:
                    try:
                        popups = driver.find_elements(By.XPATH, selector)
                        for popup in popups:
                            if popup.is_displayed():
                                popup_found = True
                                print(f"📋 Found visible popup/modal (attempt {attempt + 1})")
                    
                                # Extended close button selectors
                                close_selectors = [
                                    ".//button[contains(@class, 'close')]",
                                    ".//button[contains(@aria-label, 'Close')]",
                                    ".//button[contains(@aria-label, 'close')]",
                                    ".//button[contains(text(), 'Close')]",
                                    ".//button[contains(text(), 'close')]",
                                    ".//button[contains(text(), 'Cancel')]",
                                    ".//button[contains(text(), 'cancel')]",
                                    ".//button[contains(text(), '×')]",
                                    ".//button[contains(text(), 'X')]",
                                    ".//span[contains(@class, 'close')]",
                                    ".//a[contains(@class, 'close')]",
                                    ".//i[contains(@class, 'close')]",
                                    ".//button[contains(@onclick, 'close')]",
                                    ".//input[@type='button' and contains(@value, 'Close')]",
                                    ".//input[@type='button' and contains(@value, 'Cancel')]",
                                    ".//button[@type='button']",  # Generic button as last resort
                                ]
                                
                                closed = False
                                for close_selector in close_selectors:
                                    try:
                                        close_buttons = popup.find_elements(By.XPATH, close_selector)
                                        for close_button in close_buttons:
                                            if close_button.is_displayed() and close_button.is_enabled():
                                                close_button.click()
                                                print(f"✅ Closed popup using: {close_selector}")
                                                time.sleep(2)  # Wait longer for popup to close
                                                closed = True
                                                break
                                        if closed:
                                            break
                                    except Exception as e:
                                        continue
                                
                                # If no close button worked, try JavaScript methods
                                if not closed:
                                    try:
                                        # Try clicking the popup itself (sometimes works)
                                        driver.execute_script("arguments[0].click();", popup)
                                        print("✅ Clicked popup element")
                                        time.sleep(1)
                                        closed = True
                                        break
                                    except:
                                        continue
                                
                                if not closed:
                                    try:
                                        # Hide with JavaScript
                                        driver.execute_script("arguments[0].style.display = 'none';", popup)
                                        print("✅ Hidden popup using JavaScript")
                                        time.sleep(1)
                                        closed = True
                                    except:
                                        continue
                                
                                if not closed:
                                    try:
                                        # Remove element completely
                                        driver.execute_script("arguments[0].remove();", popup)
                                        print("✅ Removed popup element")
                                        time.sleep(1)
                                        closed = True
                                    except:
                                        pass
                                
                                if closed:
                                    break
                        
                        if popup_found:
                            break
                    except:
                        continue
                
                # If no popup found in this attempt, break the loop
                if not popup_found:
                    print(f"✅ No more popups found after attempt {attempt + 1}")
                    break
                
                # Wait a bit before checking for the next popup
                time.sleep(2)
            
            # Final cleanup - press ESC multiple times and try other methods
            print("\n🧹 Final popup cleanup...")
            try:
                from selenium.webdriver.common.keys import Keys
                body = driver.find_element(By.TAG_NAME, 'body')
                for i in range(3):
                    body.send_keys(Keys.ESCAPE)
                    time.sleep(0.5)
                print("✅ Pressed ESC key multiple times")
            except:
                pass
            
            # Try to dismiss any remaining overlays
            try:
                overlay_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'overlay') or contains(@class, 'backdrop')]")
                for overlay in overlay_elements:
                    if overlay.is_displayed():
                        driver.execute_script("arguments[0].style.display = 'none';", overlay)
                print("✅ Hidden any remaining overlays")
            except:
                pass
            
            # Navigate to job creation page
            print(f"\n🎯 Navigating to Job Creation page...")
            print(f"Target URL: {job_creation_url}")
            
            # Try multiple navigation methods
            navigation_success = False
            
            # Method 1: Direct navigation using get()
            try:
                driver.get(job_creation_url)
                time.sleep(3)
                if "CreateJob.aspx" in driver.current_url:
                    navigation_success = True
                    print("✅ Successfully navigated using driver.get()")
            except Exception as e:
                print(f"⚠️ Navigation with driver.get() failed: {e}")
            
            # Method 2: JavaScript redirect if direct navigation didn't work
            if not navigation_success:
                try:
                    driver.execute_script(f"window.location.href = '{job_creation_url}';")
                    time.sleep(3)
                    if "CreateJob.aspx" in driver.current_url:
                        navigation_success = True
                        print("✅ Successfully navigated using JavaScript redirect")
                except Exception as e:
                    print(f"⚠️ JavaScript redirect failed: {e}")
            
            # Method 3: Try opening in new tab if still not successful
            if not navigation_success:
                try:
                    driver.execute_script(f"window.open('{job_creation_url}', '_blank');")
                    time.sleep(2)
                    # Switch to the new tab
                    driver.switch_to.window(driver.window_handles[-1])
                    time.sleep(3)
                    if "CreateJob.aspx" in driver.current_url:
                        navigation_success = True
                        print("✅ Successfully navigated by opening in new tab")
                except Exception as e:
                    print(f"⚠️ New tab navigation failed: {e}")
            
            # Verify final page
            final_url = driver.current_url
            final_title = driver.title
            
            print(f"\n📍 Final Navigation Results:")
            print(f"Current URL: {final_url}")
            print(f"Page Title: {final_title}")
            
            if "CreateJob.aspx" in final_url or "CreateJob" in final_title:
                print("🎉 SUCCESS! Successfully reached the Job Creation page!")
                
                # Ask user if they want to fill the form automatically
                fill_form = input("\n🤖 Do you want to fill the form automatically? (y/n): ").lower().strip()
                
                if fill_form == 'y' or fill_form == 'yes':
                    # Ask for filling preference
                    fill_choice = input("\n📋 Choose filling option:\n1. Fill entire form\n2. Fill only General Information (for testing)\n3. Fill only Customer Information and Job Address Information (for testing)\n4. Fill only Internal Participants (for testing)\nEnter choice (1, 2, 3, or 4): ").strip()
                    
                    # Ask for data source
                    data_source = input("\n📋 Choose data source:\n1. Sample data\n2. Load from JSON file\nEnter choice (1 or 2): ").strip()
                    
                    if data_source == '2':
                        json_file = input("📁 Enter JSON file path (or press Enter for 'form_data.json'): ").strip()
                        if not json_file:
                            json_file = 'form_data.json'
                        form_data = load_form_data_from_json(json_file)
                    else:
                        print("📝 Using sample data...")
                        form_data = create_sample_form_data()
                    
                    try:
                        if fill_choice == '2':
                            print("\n🎯 Testing General Information section only...")
                            fill_general_information_only(driver, form_data)
                        elif fill_choice == '3':
                            print("\n🎯 Testing Customer Information and Job Address Information sections...")
                            fill_customer_and_job_address_only(driver, form_data)
                        elif fill_choice == '4':
                            print("\n🎯 Testing Internal Participants section only...")
                            fill_internal_participants_only(driver, form_data)
                        else:
                            fill_job_creation_form(driver, form_data)
                        print("\n🎉 Form filled successfully!")
                    except Exception as e:
                        print(f"❌ Error filling form: {str(e)}")
                        print("You can still fill the form manually.")
                
            elif navigation_success:
                print("✅ Navigation completed (may need manual verification)")
            else:
                print("⚠️ Could not automatically navigate to Job Creation page")
                print("You may need to manually navigate to the page")
        else:
            print("❌ Still on login page. Login may not have been successful.")
        
        print("\nBrowser is now open for you to interact with.")
        print("Press Enter when done to close the browser...")
        input()
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        print("Closing browser...")
        driver.quit()

if __name__ == "__main__":
    servpro_login() 


