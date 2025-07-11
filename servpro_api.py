"""
SERVPRO API automation script - REST API endpoint for form filling
"""

from flask import Flask, request, jsonify, render_template_string
from flask_restx import Api, Resource, fields
import json
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
from selenium.webdriver.common.action_chains import ActionChains
import threading
import traceback

# Import all the form filling functions from the original script
from servpro_login import (
    setup_driver, fill_job_creation_form, get_chrome_version, download_chromedriver,
    fill_text_field, fill_dropdown_field, fill_checkbox_field, fill_telerik_text_field,
    fill_telerik_dropdown_field, fill_telerik_date_field, fill_telerik_dropdown_tree_field,
    fill_telerik_masked_phone_field, fill_date_field, fill_general_information,
    fill_customer_information, fill_individual_customer_fields, fill_company_customer_fields,
    fill_job_address_information, fill_individual_job_address_fields, fill_company_job_address_fields,
    fill_internal_participants, fill_external_participants, fill_policy_information,
    fill_division_services, fill_payment_services, fill_loss_description_section
)

app = Flask(__name__)

# Define the welcome route BEFORE Flask-RESTX API initialization
@app.route('/')
def welcome():
    """Welcome page for the root URL"""
    return jsonify({
        "message": "Welcome to SERVPRO Automation API",
        "version": "1.0",
        "status": "running",
        "endpoints": {
            "health_check": "GET /health",
            "fill_form": "POST /fill-form (send JSON data)",
            "documentation": "GET /docs/"
        },
        "usage": "Send JSON data to /fill-form endpoint to automate SERVPRO form filling"
    })

# Initialize Flask-RESTX API after the welcome route
api = Api(
    app, 
    version='1.0', 
    title='SERVPRO Automation API',
    description='REST API for automating SERVPRO job creation form filling',
    doc='/docs/'
)

# Define API models for documentation
general_info_model = api.model('GeneralInformation', {
    'receivedBy': fields.String(description='Who received the job'),
    'jobName': fields.String(description='Job name'),
    'reportedBy': fields.String(description='Who reported the job'),
    'referredBy': fields.String(description='Who referred the job'),
    'jobSize': fields.String(description='Size of the job'),
    'officeName': fields.String(description='Office name (REQUIRED)', required=True),
    'dateOfLoss': fields.String(description='Date of loss (MM/DD/YYYY)'),
    'lossCategory': fields.String(description='Category of loss (REQUIRED)', required=True),
    'environmentalCode': fields.String(description='Environmental code'),
    'priority': fields.String(description='Priority level'),
    'lossType': fields.String(description='Type of loss'),
    'secondaryLossType': fields.String(description='Secondary loss type'),
    'sourceOfLoss': fields.String(description='Source of the loss')
})

phone_model = api.model('PhoneNumber', {
    'number': fields.String(description='Phone number with country code', required=True),
    'extension': fields.String(description='Phone extension'),
    'type': fields.String(description='Phone type')
})

customer_info_model = api.model('CustomerInformation', {
    'customerType': fields.String(required=True, description='Customer type (REQUIRED)', enum=['Individual', 'Company']),
    'isSameAsJobAddress': fields.Boolean(description='Same as job address'),
    'title': fields.String(description='Customer title (Individual only)'),
    'firstName': fields.String(description='First name (Individual only - REQUIRED)', required=True),
    'lastName': fields.String(description='Last name (Individual only - REQUIRED)', required=True),
    'email': fields.String(description='Email address'),
    'address': fields.String(description='Address (REQUIRED)', required=True),
    'zipCode': fields.String(description='ZIP code (REQUIRED)', required=True),
    'city': fields.String(description='City (REQUIRED)', required=True),
    'countyRegion': fields.String(description='County/Region (REQUIRED)', required=True),
    'country': fields.String(description='Country (REQUIRED)', required=True),
    'stateProvince': fields.String(description='State/Province (REQUIRED)', required=True),
    'mainPhoneNumber': fields.Nested(phone_model, description='Main phone number (REQUIRED)', required=True),
    'companyName': fields.String(description='Company name (Company only - REQUIRED when customerType is Company)'),
    'companyEmail': fields.String(description='Company email (Company only)')
})

job_address_model = api.model('JobAddressInformation', {
    'customerType': fields.String(required=True, description='Customer type', enum=['Individual', 'Company']),
    'isSameAsCustomerAddress': fields.Boolean(description='Same as customer address'),
    'firstName': fields.String(description='First name (Individual only)'),
    'lastName': fields.String(description='Last name (Individual only)'),
    'address': fields.String(description='Job site address'),
    'zipCode': fields.String(description='ZIP code'),
    'city': fields.String(description='City'),
    'countyRegion': fields.String(description='County/Region'),
    'country': fields.String(description='Country'),
    'stateProvince': fields.String(description='State/Province'),
    'mainPhoneNumber': fields.Nested(phone_model, description='Main phone number')
})

# JSON body model for Swagger documentation (not used for input display)
form_data_model = api.model('FormData', {
    'generalInformation': fields.Nested(general_info_model, required=True, description='General job information'),
    'customerInformation': fields.Nested(customer_info_model, required=True, description='Customer details'),
    'jobAddressInformation': fields.Nested(job_address_model, description='Job site address information'),
    'internalParticipants': fields.Raw(description='Internal team participants'),
    'externalParticipants': fields.Raw(description='External participants and contacts'),
    'policyInformation': fields.Raw(description='Insurance policy information'),
    'division': fields.Raw(description='Services and divisions (at least one must be selected)'),
    'paymentServices': fields.Raw(description='Payment and billing information'),
    'lossDescriptionSection': fields.Raw(description='Loss description and affected rooms')
})

success_response_model = api.model('SuccessResponse', {
    'success': fields.Boolean(description='Operation success status'),
    'message': fields.String(description='Success message'),
    'customer_type': fields.String(description='Customer type processed'),
    'job_name': fields.String(description='Job name processed'),
    'job_number': fields.String(description='SERVPRO job number from slideboard'),
    'job_id': fields.String(description='SERVPRO job ID from slideboard')
})

error_response_model = api.model('ErrorResponse', {
    'success': fields.Boolean(description='Operation success status'),
    'error': fields.String(description='Error message')
})

health_response_model = api.model('HealthResponse', {
    'status': fields.String(description='API health status'),
    'message': fields.String(description='Health status message')
})

class ServproAutomation:
    def __init__(self):
        self.driver = None
        self.wait = None
        
    def setup_browser(self):
        """Initialize the browser"""
        try:
            print("🌐 Initializing browser...")
            self.driver = setup_driver()
            self.driver.maximize_window()
            self.wait = WebDriverWait(self.driver, 10)
            return True
        except Exception as e:
            print(f"❌ Error setting up browser: {str(e)}")
            return False
    
    def login_to_servpro(self):
        """Login to SERVPRO without interactive prompts"""
        try:
            # Credentials
            login_url = "https://servpro.ngsapps.net/Enterprise/Module/User/Login.aspx"
            username = "kymcdougall"
            password = "SERVYpro123#"
            company_id = "43513"
            
            print(f"🔐 Logging in with credentials - Username: {username}, Company ID: {company_id}")
            
            # Navigate to login page
            print("🌐 Navigating to login URL...")
            self.driver.get(login_url)
            time.sleep(2)
            
            print(f"📄 Page title: {self.driver.title}")
            
            # Fill Company ID
            print("🏢 Filling Company ID...")
            company_selectors = [
                (By.ID, "txtCompanyID"),
                (By.NAME, "CompanyID"),
                (By.XPATH, "//input[@placeholder='Company ID']"),
                (By.XPATH, "//input[contains(@id, 'Company')]"),
                (By.XPATH, "//input[@type='text'][1]")
            ]
            
            company_field = None
            for selector_type, selector_value in company_selectors:
                try:
                    company_field = self.wait.until(EC.presence_of_element_located((selector_type, selector_value)))
                    break
                except:
                    continue
            
            if not company_field:
                raise Exception("Could not find Company ID field")
            
            company_field.clear()
            company_field.send_keys(company_id)
            print(f"✅ Entered company ID: {company_id}")
            
            # Fill Username
            print("👤 Filling Username...")
            username_selectors = [
                (By.ID, "txtUserName"),
                (By.ID, "txtUsername"),
                (By.NAME, "UserName"),
                (By.NAME, "Username"),
                (By.XPATH, "//input[@placeholder='User Name']"),
                (By.XPATH, "//input[contains(@id, 'User')]"),
                (By.XPATH, "//input[@type='text'][2]")
            ]
            
            username_field = None
            for selector_type, selector_value in username_selectors:
                try:
                    username_field = self.wait.until(EC.presence_of_element_located((selector_type, selector_value)))
                    break
                except:
                    continue
            
            if not username_field:
                raise Exception("Could not find Username field")
            
            username_field.clear()
            username_field.send_keys(username)
            print(f"✅ Entered username: {username}")
            
            # Fill Password
            print("🔒 Filling Password...")
            password_selectors = [
                (By.ID, "txtPassword"),
                (By.NAME, "Password"),
                (By.XPATH, "//input[@placeholder='Password']"),
                (By.XPATH, "//input[contains(@id, 'Password')]"),
                (By.XPATH, "//input[@type='password']")
            ]
            
            password_field = None
            for selector_type, selector_value in password_selectors:
                try:
                    password_field = self.wait.until(EC.presence_of_element_located((selector_type, selector_value)))
                    break
                except:
                    continue
            
            if not password_field:
                raise Exception("Could not find Password field")
            
            password_field.clear()
            password_field.send_keys(password)
            print("✅ Entered password")
            
            # Click Login button
            print("🔓 Clicking Login button...")
            login_selectors = [
                (By.ID, "btnLogin"),
                (By.XPATH, "//input[@value='Login']"),
                (By.XPATH, "//button[contains(text(), 'Login')]"),
                (By.XPATH, "//input[@type='submit']"),
                (By.XPATH, "//button[@type='submit']"),
                (By.XPATH, "//input[contains(@value, 'Log')]"),
                (By.XPATH, "//button[contains(@class, 'btn')]")
            ]
            
            login_button = None
            for selector_type, selector_value in login_selectors:
                try:
                    login_button = self.wait.until(EC.element_to_be_clickable((selector_type, selector_value)))
                    break
                except:
                    continue
            
            if not login_button:
                raise Exception("Could not find Login button")
            
            login_button.click()
            print("✅ Clicked Login button")
            
            # Wait for login to complete
            time.sleep(5)
            
            # Check login success
            current_url = self.driver.current_url
            print(f"🔍 Current URL after login: {current_url}")
            
            success_indicators = ["uPostLogin.aspx", "Default.aspx", "Home.aspx", "Main.aspx"]
            login_successful = any(indicator in current_url for indicator in success_indicators) or "/User/Login.aspx" not in current_url
            
            if not login_successful:
                raise Exception("Login was not successful")
            
            print("✅ Login successful!")
            
            # Handle popups
            self.handle_popups()
            
            return True
            
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return False
    
    def handle_popups(self):
        """Handle any popups that appear after login"""
        print("🔍 Handling post-login popups...")
        
        # Handle alerts first
        try:
            alert = self.driver.switch_to.alert
            alert_text = alert.text
            print(f"⚠️ Alert found: {alert_text}")
            alert.dismiss()
            print("✅ Alert dismissed")
            time.sleep(1)
        except NoAlertPresentException:
            print("✅ No alert present")
        
        # Handle modal popups
        max_popup_attempts = 5
        
        for attempt in range(max_popup_attempts):
            print(f"🔍 Popup handling attempt {attempt + 1}/{max_popup_attempts}...")
            
            popup_found = False
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
            
            for selector in popup_selectors:
                try:
                    popups = self.driver.find_elements(By.XPATH, selector)
                    for popup in popups:
                        if popup.is_displayed():
                            popup_found = True
                            print(f"📋 Found visible popup/modal (attempt {attempt + 1})")
                            
                            close_selectors = [
                                ".//button[contains(@class, 'close')]",
                                ".//button[contains(@aria-label, 'Close')]",
                                ".//button[contains(text(), 'Close')]",
                                ".//button[contains(text(), 'Cancel')]",
                                ".//button[contains(text(), '×')]",
                                ".//button[contains(text(), 'X')]",
                                ".//span[contains(@class, 'close')]",
                                ".//a[contains(@class, 'close')]",
                                ".//i[contains(@class, 'close')]",
                                ".//button[contains(@onclick, 'close')]",
                                ".//input[@type='button' and contains(@value, 'Close')]",
                                ".//input[@type='button' and contains(@value, 'Cancel')]",
                                ".//button[@type='button']"
                            ]
                            
                            closed = False
                            for close_selector in close_selectors:
                                try:
                                    close_buttons = popup.find_elements(By.XPATH, close_selector)
                                    for close_button in close_buttons:
                                        if close_button.is_displayed() and close_button.is_enabled():
                                            close_button.click()
                                            print(f"✅ Closed popup using: {close_selector}")
                                            time.sleep(2)
                                            closed = True
                                            break
                                    if closed:
                                        break
                                except:
                                    continue
                            
                            if not closed:
                                try:
                                    self.driver.execute_script("arguments[0].style.display = 'none';", popup)
                                    print("✅ Hidden popup using JavaScript")
                                    closed = True
                                except:
                                    pass
                            
                            if closed:
                                break
                    
                    if popup_found:
                        break
                except:
                    continue
            
            if not popup_found:
                print(f"✅ No more popups found after attempt {attempt + 1}")
                break
            
            time.sleep(2)
        
        # Final cleanup
        try:
            body = self.driver.find_element(By.TAG_NAME, 'body')
            for i in range(3):
                body.send_keys(Keys.ESCAPE)
                time.sleep(0.5)
            print("✅ Pressed ESC key multiple times")
        except:
            pass
    
    def navigate_to_job_creation(self):
        """Navigate to the job creation page"""
        try:
            job_creation_url = "https://servpro.ngsapps.net/Enterprise/Module/Job/CreateJob.aspx"
            print(f"🎯 Navigating to Job Creation page...")
            print(f"Target URL: {job_creation_url}")
            
            # Try direct navigation
            self.driver.get(job_creation_url)
            time.sleep(3)
            
            if "CreateJob.aspx" in self.driver.current_url:
                print("✅ Successfully navigated to Job Creation page")
                return True
            else:
                # Try JavaScript redirect
                self.driver.execute_script(f"window.location.href = '{job_creation_url}';")
                time.sleep(3)
                
                if "CreateJob.aspx" in self.driver.current_url:
                    print("✅ Successfully navigated using JavaScript redirect")
                    return True
                else:
                    print("❌ Could not navigate to Job Creation page")
                    return False
                    
        except Exception as e:
            print(f"❌ Navigation error: {str(e)}")
            return False
    
    def fill_form_with_data(self, form_data):
        """Fill the job creation form with provided data"""
        try:
            print("🎯 Starting form filling process...")
            fill_job_creation_form(self.driver, form_data)
            print("✅ Form filled successfully!")
            return True
        except Exception as e:
            print(f"❌ Error filling form: {str(e)}")
            traceback.print_exc()
            return False
    
    def save_and_go_to_slideboard(self):
        """Click the 'Save & Go to Slideboard' button and extract job details"""
        try:
            print("💾 Looking for 'Save & Go to Slideboard' button...")
            
            # Multiple selectors for the save button
            save_button_selectors = [
                (By.ID, "ctl00_ContentPlaceHolder1_JobParentInformation_Button_SaveAndGoToSlideBoardBottom_input"),
                (By.ID, "ctl00_ContentPlaceHolder1_JobParentInformation_Button_SaveAndGoToSlideBoardBottom"),
                (By.XPATH, "//input[@value='Save & Go to Slideboard']"),
                (By.XPATH, "//input[contains(@value, 'Save') and contains(@value, 'Slideboard')]"),
                (By.XPATH, "//span[contains(@id, 'SaveAndGoToSlideBoard')]//input"),
                (By.XPATH, "//button[contains(text(), 'Save & Go to Slideboard')]"),
                (By.XPATH, "//input[contains(@id, 'SaveAndGoToSlideBoard')]"),
                (By.CSS_SELECTOR, "input[value*='Save'][value*='Slideboard']")
            ]
            
            save_button = None
            for selector_type, selector_value in save_button_selectors:
                try:
                    save_button = self.wait.until(EC.element_to_be_clickable((selector_type, selector_value)))
                    print(f"✅ Found save button using: {selector_type} = {selector_value}")
                    break
                except:
                    continue
            
            if not save_button:
                print("❌ Could not find 'Save & Go to Slideboard' button")
                return None, None
            
            # Scroll to button and click
            self.driver.execute_script("arguments[0].scrollIntoView(true);", save_button)
            time.sleep(1)
            
            print("🖱️ Clicking 'Save & Go to Slideboard' button...")
            try:
                # Try regular click first
                save_button.click()
                print("✅ Button clicked successfully")
            except Exception as click_error:
                print(f"⚠️ Regular click failed: {click_error}")
                try:
                    # Try JavaScript click as backup
                    self.driver.execute_script("arguments[0].click();", save_button)
                    print("✅ JavaScript click succeeded")
                except Exception as js_error:
                    print(f"❌ JavaScript click also failed: {js_error}")
                    return None, None
            
            # Wait for redirect to slideboard page
            print("⏳ Waiting for redirect to slideboard...")
            time.sleep(5)  # Give time for the redirect
            
            # Wait for URL to contain slideboard
            try:
                print("🔍 Checking for URL change...")
                self.wait.until(lambda driver: "jJobSlideBoard.aspx" in driver.current_url)
                print("✅ Successfully redirected to slideboard")
            except Exception as redirect_error:
                print(f"⚠️ Timeout waiting for slideboard redirect: {redirect_error}")
                print("📄 Continuing with current page...")
            
            # Extract job details from URL
            current_url = self.driver.current_url
            print(f"📄 Current URL: {current_url}")
            
            # Check if we're actually on the slideboard page
            if "jJobSlideBoard.aspx" in current_url:
                print("✅ Successfully on slideboard page")
            else:
                print("⚠️ Not on slideboard page - button click may have failed")
                print(f"📄 Current page title: {self.driver.title}")
                # Let's try to find any error messages or alerts
                try:
                    alerts = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'alert') or contains(@class, 'error') or contains(@class, 'message')]")
                    if alerts:
                        for alert in alerts:
                            if alert.is_displayed():
                                print(f"⚠️ Found page message: {alert.text}")
                except:
                    pass
            
            job_number = None
            job_id = None
            
            # Parse URL parameters
            if "?" in current_url:
                url_params = current_url.split("?")[1]
                params = {}
                for param in url_params.split("&"):
                    if "=" in param:
                        key, value = param.split("=", 1)
                        params[key] = value
                
                job_number = params.get("JobNumber")
                job_id = params.get("JobId")
                
                print(f"📋 Extracted Job Number: {job_number}")
                print(f"🆔 Extracted Job ID: {job_id}")
            
            if not job_number or not job_id:
                print("⚠️ Could not extract job details from URL")
            
            return job_number, job_id
            
        except Exception as e:
            print(f"❌ Error saving and going to slideboard: {str(e)}")
            traceback.print_exc()
            return None, None
    
    def cleanup(self):
        """Clean up browser resources"""
        try:
            if self.driver:
                print("⏳ Waiting 5 seconds before closing browser...")
                time.sleep(5)
                print("🧹 Closing browser...")
                self.driver.quit()
        except Exception as e:
            print(f"⚠️ Error during cleanup: {str(e)}")

def validate_form_data(data):
    """Validate the incoming form data"""
    required_sections = ['generalInformation', 'customerInformation']
    
    for section in required_sections:
        if section not in data:
            return False, f"Missing required section: {section}"
    
    # Validate customer information has required type
    if 'customerType' not in data['customerInformation']:
        return False, "Missing customerType in customerInformation"
    
    customer_type = data['customerInformation']['customerType']
    if customer_type not in ['Individual', 'Company']:
        return False, "customerType must be 'Individual' or 'Company'"
    
    return True, "Valid"

def validate_json_format(data):
    """Validate if JSON has the expected SERVPRO form structure with mandatory fields"""
    if not isinstance(data, dict):
        return False, "Invalid JSON format. Expected a JSON object with SERVPRO form structure. Please use the correct structure like form_data_individual_example.json or form_data_company_example.json."
    
    # Check for expected main sections
    expected_sections = [
        'generalInformation',
        'customerInformation',
        'division'
    ]
    
    # At minimum, we need these three sections
    missing_sections = [section for section in expected_sections if section not in data]
    if missing_sections:
        return False, f"Invalid SERVPRO form format. Missing required sections: {', '.join(missing_sections)}. Please use the correct JSON structure like form_data_individual_example.json."
    
    # Validate generalInformation structure
    general_info = data.get('generalInformation', {})
    if not isinstance(general_info, dict):
        return False, "Invalid format: 'generalInformation' must be an object. Please check form_data_individual_example.json for correct structure."
    
    # Check for mandatory fields in General Information (marked with red asterisks in form)
    general_required_fields = ['officeName', 'lossCategory']
    missing_general_fields = []
    for field in general_required_fields:
        if field not in general_info or not general_info.get(field) or str(general_info.get(field)).strip() == '':
            missing_general_fields.append(field)
    
    if missing_general_fields:
        field_names = {
            'officeName': 'Office Name',
            'lossCategory': 'Loss Category'
        }
        readable_fields = [field_names.get(field, field) for field in missing_general_fields]
        return False, f"Invalid format: Missing required values for mandatory fields in 'generalInformation': {', '.join(readable_fields)}. These fields cannot be empty."
    
    # Validate customerInformation structure
    customer_info = data.get('customerInformation', {})
    if not isinstance(customer_info, dict):
        return False, "Invalid format: 'customerInformation' must be an object. Please check form_data_individual_example.json for correct structure."
    
    # Check for customerType field
    if 'customerType' not in customer_info:
        return False, "Invalid format: Missing 'customerType' field in 'customerInformation'. Must be 'Individual' or 'Company'. Please use form_data_individual_example.json as template."
    
    customer_type = customer_info.get('customerType')
    if customer_type not in ['Individual', 'Company']:
        return False, f"Invalid format: 'customerType' must be 'Individual' or 'Company', got '{customer_type}'. Please use form_data_individual_example.json as template."
    
    # Validate mandatory customer fields based on customer type
    if customer_type == 'Individual':
        # Individual Customer mandatory fields (marked with red asterisks)
        individual_required_fields = [
            'firstName', 'lastName', 'address', 'zipCode', 'city', 
            'countyRegion', 'country', 'stateProvince'
        ]
        missing_individual_fields = []
        for field in individual_required_fields:
            if field not in customer_info or not customer_info.get(field) or str(customer_info.get(field)).strip() == '':
                missing_individual_fields.append(field)
        
        # Check main phone number
        if 'mainPhoneNumber' not in customer_info or not customer_info.get('mainPhoneNumber'):
            missing_individual_fields.append('mainPhoneNumber')
        elif isinstance(customer_info.get('mainPhoneNumber'), dict):
            phone_data = customer_info.get('mainPhoneNumber')
            if not phone_data.get('number') or str(phone_data.get('number')).strip() == '':
                missing_individual_fields.append('mainPhoneNumber.number')
        
        if missing_individual_fields:
            field_names = {
                'firstName': 'First Name',
                'lastName': 'Last Name', 
                'address': 'Address',
                'zipCode': 'ZIP/Postal Code',
                'city': 'City',
                'countyRegion': 'County/Region',
                'country': 'Country',
                'stateProvince': 'State/Province',
                'mainPhoneNumber': 'Main Phone Number',
                'mainPhoneNumber.number': 'Main Phone Number'
            }
            readable_fields = [field_names.get(field, field) for field in missing_individual_fields]
            return False, f"Invalid format: Missing required values for mandatory Individual Customer fields: {', '.join(readable_fields)}. These fields cannot be empty."
    
    elif customer_type == 'Company':
        # Company Customer mandatory fields (marked with red asterisks)
        company_required_fields = [
            'companyName', 'companyAddress', 'companyZipCode', 'companyCity',
            'companyCountyRegion', 'companyCountry', 'companyStateProvince'
        ]
        missing_company_fields = []
        for field in company_required_fields:
            if field not in customer_info or not customer_info.get(field) or str(customer_info.get(field)).strip() == '':
                missing_company_fields.append(field)
        
        # Check company main phone number
        if 'companyMainPhoneNumber' not in customer_info or not customer_info.get('companyMainPhoneNumber'):
            missing_company_fields.append('companyMainPhoneNumber')
        elif isinstance(customer_info.get('companyMainPhoneNumber'), dict):
            phone_data = customer_info.get('companyMainPhoneNumber')
            if not phone_data.get('number') or str(phone_data.get('number')).strip() == '':
                missing_company_fields.append('companyMainPhoneNumber.number')
        
        if missing_company_fields:
            field_names = {
                'companyName': 'Company Name',
                'companyAddress': 'Company Address',
                'companyZipCode': 'ZIP/Postal Code',
                'companyCity': 'City',
                'companyCountyRegion': 'County/Region',
                'companyCountry': 'Country',
                'companyStateProvince': 'State/Province',
                'companyMainPhoneNumber': 'Main Phone Number',
                'companyMainPhoneNumber.number': 'Main Phone Number'
            }
            readable_fields = [field_names.get(field, field) for field in missing_company_fields]
            return False, f"Invalid format: Missing required values for mandatory Company Customer fields: {', '.join(readable_fields)}. These fields cannot be empty."
    
    # Validate division section - at least one service must be selected
    if 'division' not in data:
        return False, "Missing required section: 'division'. Please include the division section with servicesSelected array containing at least one service. Example: {'division': {'servicesSelected': ['Water Mitigation', 'Structure']}}"
    
    division_info = data.get('division', {})
    if not isinstance(division_info, dict):
        return False, "Invalid format: 'division' must be an object. Please check form_data_individual_example.json for correct structure."
    
    if not division_info:
        return False, "Empty division section. Please include servicesSelected array with at least one service. Example: {'division': {'servicesSelected': ['Water Mitigation', 'Structure']}}"
    
    # Check for servicesSelected array format
    if 'servicesSelected' not in division_info:
        return False, "Missing required field: 'servicesSelected' in division section. Please include an array of selected services. Example: {'division': {'servicesSelected': ['Water Mitigation', 'Structure', 'Mold']}}"
    
    services_selected = division_info.get('servicesSelected', [])
    if not isinstance(services_selected, list):
        return False, "Invalid format: 'servicesSelected' must be an array of service names. Example: {'division': {'servicesSelected': ['Water Mitigation', 'Structure']}}"
    
    if not services_selected or len(services_selected) == 0:
        available_services = [
            'Temporary Repairs', 'Water Mitigation', 'Reconstruction', 'Structure', 
            'Contents', 'Roofing', 'Negotiated Work Reconstruction', 'DRT - Water', 
            'DRT - Mold', 'DRT - Reconstruction', 'DRT - Misc', 'DRT - Fire', 
            'General Cleaning', 'Mold'
        ]
        return False, f"At least one Division service must be selected. Please add services to the servicesSelected array. Available services: {', '.join(available_services)}. Example: {{'division': {{'servicesSelected': ['Water Mitigation', 'Structure']}}}}"
    
    return True, "Valid format"

@api.route('/health')
class HealthCheck(Resource):
    @api.doc('health_check')
    @api.marshal_with(health_response_model)
    def get(self):
        """Health check endpoint"""
        return {
            "status": "healthy",
            "message": "SERVPRO API is running"
        }

# Simple placeholder model for clean Swagger UI (completely empty input)
simple_json_model = api.model('JsonPayload', {})

@api.route('/fill-form')
class FillForm(Resource):
    @api.doc('fill_form')
    @api.expect(simple_json_model, validate=False)
    def post(self):
        """Fill the SERVPRO job creation form with JSON data
        
        This endpoint accepts raw JSON data in the request body containing complete SERVPRO form information.
        
        **Process:**
        - Opens a browser instance
        - Logs into SERVPRO automatically
        - Navigates to the job creation form
        - Fills all form sections with the provided JSON data
        - Clicks 'Save & Go to Slideboard' button
        - Extracts job number and job ID from the slideboard URL
        - Waits 5 seconds before closing browser
        - Returns success/failure status with job details
        
        **Request Requirements:**
        - Content-Type: application/json
        - Request body: Raw JSON object with complete SERVPRO form structure
        
        **Mandatory Fields:**
        - generalInformation.officeName (required)
        - generalInformation.lossCategory (required)
        - customerInformation.customerType (required: "Individual" or "Company")
        - For Individual: firstName, lastName, address, zipCode, city, countyRegion, country, stateProvince, mainPhoneNumber
        - For Company: companyName, companyAddress, companyZipCode, companyCity, companyCountyRegion, companyCountry, companyStateProvince, companyMainPhoneNumber
        - division.servicesSelected: Array of selected services (at least one required) - Available: "Temporary Repairs", "Water Mitigation", "Reconstruction", "Structure", "Contents", "Roofing", "Negotiated Work Reconstruction", "DRT - Water", "DRT - Mold", "DRT - Reconstruction", "DRT - Misc", "DRT - Fire", "General Cleaning", "Mold"
        
        **Important Notes:**
        - All requests must use Content-Type: application/json
        - Send raw JSON data in request body (not file upload)
        - Division section is mandatory with at least one service selected
        - API returns job_number and job_id after successful form submission
        
        **JSON Structure Sections:**
        - generalInformation: Job details, dates, categories
        - customerInformation: Customer details (Individual or Company)
        - jobAddressInformation: Job site address information
        - internalParticipants: SERVPRO team members
        - externalParticipants: External contacts and companies
        - policyInformation: Insurance policy details
        - division: Services to be provided
        - paymentServices: Payment and billing information
        - lossDescriptionSection: Loss description and affected rooms
        
        **Example Usage:**
        ```bash
        # Using JSON file
        curl -X POST http://localhost:5000/fill-form \\
          -H "Content-Type: application/json" \\
          -d @form_data_individual_example.json
        
        # Using raw JSON data
        curl -X POST http://localhost:5000/fill-form \\
          -H "Content-Type: application/json" \\
          -d '{"generalInformation":{"officeName":"SPSC, LLC","lossCategory":"Residential"},"customerInformation":{"customerType":"Individual","firstName":"John","lastName":"Smith","address":"123 Main St","zipCode":"30309","city":"Atlanta","countyRegion":"Fulton County","country":"USA","stateProvince":"Georgia","mainPhoneNumber":{"number":"1-404-555-1234"}},"division":{"servicesSelected":["Water Mitigation","Structure"]}}'
        ```
        
        **Customer Types:**
        
        Individual Customer - Set customerType to "Individual":
        - Required: firstName, lastName, address, zipCode, city, countyRegion, country, stateProvince, mainPhoneNumber
        - Use form_data_individual_example.json as template
        
        Company Customer - Set customerType to "Company":
        - Required: companyName, companyAddress, companyZipCode, companyCity, companyCountyRegion, companyCountry, companyStateProvince, companyMainPhoneNumber
        - Use form_data_company_example.json as template
        
        **Division Services (Required):**
        At least one service must be selected in the division section using servicesSelected array. Example:
        ```json
        "division": {
            "servicesSelected": [
                "Water Mitigation",
                "Structure", 
                "Mold",
                "Reconstruction"
            ]
        }
        ```
        Available services: "Temporary Repairs", "Water Mitigation", "Reconstruction", "Structure", "Contents", "Roofing", "Negotiated Work Reconstruction", "DRT - Water", "DRT - Mold", "DRT - Reconstruction", "DRT - Misc", "DRT - Fire", "General Cleaning", "Mold"
        
        **Request Format:**
        - Method: POST
        - Content-Type: application/json
        - Body: Raw JSON data (not file upload)
        - Required sections: generalInformation, customerInformation, division
        
        The process is completely automated and requires no user interaction.
        """
        try:
            # Check if JSON data was provided
            if not request.is_json:
                error_response = {
                    "success": False,
                    "error": "Request must be JSON. Please send JSON data with Content-Type: application/json header."
                }
                print(f"❌ Content-Type error, returning: {error_response}")
                return error_response, 400
            
            # Get JSON data from request body
            form_data = request.get_json()
            
            if not form_data:
                error_response = {
                    "success": False,
                    "error": "No JSON data provided. Please send valid SERVPRO form data structure in the request body."
                }
                print(f"❌ No JSON data error, returning: {error_response}")
                return error_response, 400
            
            # Validate JSON format first
            print(f"🔍 Validating JSON format...")
            is_format_valid, format_message = validate_json_format(form_data)
            print(f"📋 Validation result: {is_format_valid}, Message: {format_message}")
            if not is_format_valid:
                print(f"❌ Validation failed: {format_message}")
                error_response = {
                    "success": False,
                    "error": format_message
                }
                print(f"🔧 Returning validation error response: {error_response}")
                return error_response, 400
            
            # Validate form data
            is_valid, validation_message = validate_form_data(form_data)
            if not is_valid:
                error_response = {
                    "success": False,
                    "error": f"Invalid form data: {validation_message}"
                }
                print(f"🔧 Returning form validation error response: {error_response}")
                return error_response, 400
            
            print(f"📋 Received form data for customer type: {form_data['customerInformation']['customerType']}")
            
            # Initialize automation
            automation = ServproAutomation()
            
            try:
                # Setup browser
                if not automation.setup_browser():
                    error_response = {
                        "success": False,
                        "error": "Failed to setup browser"
                    }
                    print(f"🔧 Returning browser setup error: {error_response}")
                    return error_response, 500
                
                # Login to SERVPRO
                if not automation.login_to_servpro():
                    error_response = {
                        "success": False,
                        "error": "Failed to login to SERVPRO"
                    }
                    print(f"🔧 Returning login error: {error_response}")
                    return error_response, 500
                
                # Navigate to job creation page
                if not automation.navigate_to_job_creation():
                    error_response = {
                        "success": False,
                        "error": "Failed to navigate to job creation page"
                    }
                    print(f"🔧 Returning navigation error: {error_response}")
                    return error_response, 500
                
                # Fill the form
                if not automation.fill_form_with_data(form_data):
                    error_response = {
                        "success": False,
                        "error": "Failed to fill the form"
                    }
                    print(f"🔧 Returning form filling error: {error_response}")
                    return error_response, 500
                
                # Save and go to slideboard to get job details
                job_number, job_id = automation.save_and_go_to_slideboard()
                
                # Success response
                response_data = {
                    "success": True,
                    "message": "Form filled and job created successfully",
                    "customer_type": form_data['customerInformation']['customerType'],
                    "job_name": form_data.get('generalInformation', {}).get('jobName', 'N/A')
                }
                
                # Add job details if available
                if job_number:
                    response_data["job_number"] = job_number
                if job_id:
                    response_data["job_id"] = job_id
                
                return response_data
            
            finally:
                # Always cleanup browser resources
                automation.cleanup()
        
        except Exception as e:
            error_details = str(e)
            traceback.print_exc()
            error_response = {
                "success": False,
                "error": f"Unexpected error: {error_details}"
            }
            print(f"🔧 Returning unexpected error response: {error_response}")
            return error_response, 500



if __name__ == '__main__':
    print("🚀 Starting SERVPRO API...")
    print("📋 Available endpoints:")
    print("   GET  / - Welcome message")
    print("   GET  /health - Health check")
    print("   POST /fill-form - Fill SERVPRO form with raw JSON data")
    print("   GET  /docs/ - Interactive API documentation")
    print("\n🌐 API will be available at:")
    print("   Main API: http://localhost:5000")
    print("   Documentation: http://localhost:5000/docs/")
    print("\n📝 Quick test with raw JSON data:")
    print("   curl -X POST http://localhost:5000/fill-form \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d @form_data_individual_example.json")
    print("\n💡 Alternative using inline raw JSON:")
    print("   curl -X POST http://localhost:5000/fill-form \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"generalInformation\":{\"officeName\":\"SPSC, LLC\",\"lossCategory\":\"Residential\"},\"customerInformation\":{\"customerType\":\"Individual\",\"firstName\":\"John\",\"lastName\":\"Smith\",\"address\":\"123 Main St\",\"zipCode\":\"30309\",\"city\":\"Atlanta\",\"countyRegion\":\"Fulton County\",\"country\":\"USA\",\"stateProvince\":\"Georgia\",\"mainPhoneNumber\":{\"number\":\"1-404-555-1234\"}},\"division\":{\"servicesSelected\":[\"Water Mitigation\",\"Structure\"]}}'")
    print("\n📖 JSON templates: form_data_individual_example.json, form_data_company_example.json")
    print("⚠️  Note: Send raw JSON data in request body with Content-Type: application/json")
    print("🔍 Validation: API validates mandatory fields including Division services and provides detailed error messages")
    print("🎯 Swagger UI: Open http://localhost:5000/docs/ to test with interactive interface")
    print("\n💡 Division Section Format Examples:")
    print("   ✅ Correct: {'division': {'servicesSelected': ['Water Mitigation', 'Structure']}}")
    print("   ❌ Wrong:   {'division': {'waterMitigation': true, 'contents': true}}")
    print("   ❌ Empty:   {'division': {}}")
    print("   ❌ Missing: (no division section)")
    
    app.run(host='0.0.0.0', port=5000, debug=True) 