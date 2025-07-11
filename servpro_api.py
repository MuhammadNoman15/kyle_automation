"""
SERVPRO API automation script - REST API endpoint for form filling
"""

from flask import Flask, request, jsonify, render_template_string
from flask_restx import Api, Resource, fields
from werkzeug.datastructures import FileStorage
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
            "fill_form": "POST /fill-form (upload .json file)",
            "documentation": "GET /docs/"
        },
        "usage": "Upload JSON file to /fill-form endpoint to automate SERVPRO form filling"
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
    'receivedBy': fields.String(description='Who received the job', example='Kyle McDougall'),
    'jobName': fields.String(description='Job name', example='Smith, John - Water Damage'),
    'reportedBy': fields.String(description='Who reported the job', example='Property Owner'),
    'referredBy': fields.String(description='Who referred the job', example='Lewis, A.D.'),
    'jobSize': fields.String(description='Size of the job', example='Medium'),
    'officeName': fields.String(description='Office name', example='SPSC, LLC'),
    'dateOfLoss': fields.String(description='Date of loss (MM/DD/YYYY)', example='12/15/2024'),
    'lossCategory': fields.String(description='Category of loss', example='Residential'),
    'environmentalCode': fields.String(description='Environmental code', example='Mitigation'),
    'priority': fields.String(description='Priority level', example='High'),
    'lossType': fields.String(description='Type of loss', example='General Repairs'),
    'secondaryLossType': fields.String(description='Secondary loss type', example='Mold'),
    'sourceOfLoss': fields.String(description='Source of the loss', example='Pipe Break')
})

phone_model = api.model('PhoneNumber', {
    'number': fields.String(description='Phone number with country code', example='1-404-555-1234'),
    'extension': fields.String(description='Phone extension', example=''),
    'type': fields.String(description='Phone type', example='Mobile')
})

customer_info_model = api.model('CustomerInformation', {
    'customerType': fields.String(required=True, description='Customer type', enum=['Individual', 'Company'], example='Individual'),
    'isSameAsJobAddress': fields.Boolean(description='Same as job address', example=False),
    'title': fields.String(description='Customer title (Individual only)', example='Mr.'),
    'firstName': fields.String(description='First name (Individual only)', example='John'),
    'lastName': fields.String(description='Last name (Individual only)', example='Smith'),
    'email': fields.String(description='Email address', example='john.smith@email.com'),
    'address': fields.String(description='Address', example='123 Main Street'),
    'zipCode': fields.String(description='ZIP code', example='30309'),
    'city': fields.String(description='City', example='Atlanta'),
    'countyRegion': fields.String(description='County/Region', example='Fulton County'),
    'country': fields.String(description='Country', example='USA'),
    'stateProvince': fields.String(description='State/Province', example='Georgia'),
    'mainPhoneNumber': fields.Nested(phone_model, description='Main phone number'),
    'companyName': fields.String(description='Company name (Company only)', example='ABC Corporation'),
    'companyEmail': fields.String(description='Company email (Company only)', example='contact@abc.com')
})

job_address_model = api.model('JobAddressInformation', {
    'customerType': fields.String(required=True, description='Customer type', enum=['Individual', 'Company'], example='Individual'),
    'isSameAsCustomerAddress': fields.Boolean(description='Same as customer address', example=False),
    'firstName': fields.String(description='First name (Individual only)', example='John'),
    'lastName': fields.String(description='Last name (Individual only)', example='Smith'),
    'address': fields.String(description='Job site address', example='456 Loss Address Street'),
    'zipCode': fields.String(description='ZIP code', example='30309'),
    'city': fields.String(description='City', example='Atlanta'),
    'countyRegion': fields.String(description='County/Region', example='Fulton County'),
    'country': fields.String(description='Country', example='USA'),
    'stateProvince': fields.String(description='State/Province', example='Georgia'),
    'mainPhoneNumber': fields.Nested(phone_model, description='Main phone number')
})

# File upload parser for Swagger documentation
upload_parser = api.parser()
upload_parser.add_argument('file', location='files', type=FileStorage, required=True, 
                          help='JSON file containing form data (.json extension required)')

success_response_model = api.model('SuccessResponse', {
    'success': fields.Boolean(description='Operation success status', example=True),
    'message': fields.String(description='Success message', example='Form filled successfully'),
    'customer_type': fields.String(description='Customer type processed', example='Individual'),
    'job_name': fields.String(description='Job name processed', example='Smith, John - Water Damage')
})

error_response_model = api.model('ErrorResponse', {
    'success': fields.Boolean(description='Operation success status', example=False),
    'error': fields.String(description='Error message', example='Failed to login to SERVPRO')
})

health_response_model = api.model('HealthResponse', {
    'status': fields.String(description='API health status', example='healthy'),
    'message': fields.String(description='Health status message', example='SERVPRO API is running')
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
    
    def cleanup(self):
        """Clean up browser resources"""
        try:
            if self.driver:
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
    """Validate if JSON has the expected SERVPRO form structure"""
    if not isinstance(data, dict):
        return False, "Invalid JSON format. Expected a JSON object with SERVPRO form structure. Please use form_data_individual_example.json or form_data_company_example.json as templates."
    
    # Check for expected main sections
    expected_sections = [
        'generalInformation',
        'customerInformation'
    ]
    
    # At minimum, we need these two sections
    missing_sections = [section for section in expected_sections if section not in data]
    if missing_sections:
        return False, f"Invalid SERVPRO form format. Missing required sections: {', '.join(missing_sections)}. Please use the correct JSON structure like form_data_individual_example.json."
    
    # Validate generalInformation structure
    general_info = data.get('generalInformation', {})
    if not isinstance(general_info, dict):
        return False, "Invalid format: 'generalInformation' must be an object. Please check form_data_individual_example.json for correct structure."
    
    # Check for some key fields in generalInformation
    general_required_fields = ['jobName', 'receivedBy']
    missing_general_fields = [field for field in general_required_fields if field not in general_info]
    if missing_general_fields:
        return False, f"Invalid format: Missing required fields in 'generalInformation': {', '.join(missing_general_fields)}. Please use form_data_individual_example.json as template."
    
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

@api.route('/fill-form')
class FillForm(Resource):
    @api.doc('fill_form')
    @api.expect(upload_parser)
    def post(self):
        """Fill the SERVPRO job creation form with uploaded JSON file
        
        This endpoint accepts a JSON file upload containing form information and automatically:
        - Opens a browser instance
        - Logs into SERVPRO
        - Navigates to the job creation form
        - Fills all form sections with the data from the uploaded JSON file
        - Closes the browser
        - Returns success/failure status
        
        The process is completely automated and requires no user interaction.
        
        Expected file format: .json file with the complete form data structure.
        Use form_data_individual_example.json or form_data_company_example.json as templates.
        """
        try:
            # Check if file was uploaded
            if 'file' not in request.files:
                return {
                    "success": False,
                    "error": "No file uploaded. Please upload a JSON file with SERVPRO form data (e.g., form_data_individual_example.json)."
                }, 400
            
            file = request.files['file']
            
            # Check if a file was actually selected
            if file.filename == '':
                return {
                    "success": False,
                    "error": "No file selected. Please choose a JSON file with SERVPRO form data."
                }, 400
            
            # Check file extension
            if not file.filename.lower().endswith('.json'):
                return {
                    "success": False,
                    "error": f"Invalid file type '{file.filename}'. Please attach a JSON file with .json extension."
                }, 400
            
            # Read and parse JSON file
            try:
                file_content = file.read().decode('utf-8')
                form_data = json.loads(file_content)
            except json.JSONDecodeError as e:
                return {
                    "success": False,
                    "error": f"Invalid JSON syntax in file '{file.filename}': {str(e)}. Please check your JSON format or use form_data_individual_example.json as template."
                }, 400
            except UnicodeDecodeError:
                return {
                    "success": False,
                    "error": f"File encoding error in '{file.filename}'. Please ensure the file is saved as UTF-8 encoded text."
                }, 400
            
            if not form_data:
                return {
                    "success": False,
                    "error": f"Empty or invalid JSON file '{file.filename}'. Please provide a valid SERVPRO form data file like form_data_individual_example.json."
                }, 400
            
            # Validate JSON format first
            is_format_valid, format_message = validate_json_format(form_data)
            if not is_format_valid:
                return {
                    "success": False,
                    "error": format_message
                }, 400
            
            # Validate form data
            is_valid, validation_message = validate_form_data(form_data)
            if not is_valid:
                return {
                    "success": False,
                    "error": f"Invalid form data: {validation_message}"
                }, 400
            
            print(f"📋 Received form data for customer type: {form_data['customerInformation']['customerType']}")
            
            # Initialize automation
            automation = ServproAutomation()
            
            try:
                # Setup browser
                if not automation.setup_browser():
                    return {
                        "success": False,
                        "error": "Failed to setup browser"
                    }, 500
                
                # Login to SERVPRO
                if not automation.login_to_servpro():
                    return {
                        "success": False,
                        "error": "Failed to login to SERVPRO"
                    }, 500
                
                # Navigate to job creation page
                if not automation.navigate_to_job_creation():
                    return {
                        "success": False,
                        "error": "Failed to navigate to job creation page"
                    }, 500
                
                # Fill the form
                if not automation.fill_form_with_data(form_data):
                    return {
                        "success": False,
                        "error": "Failed to fill the form"
                    }, 500
                
                # Success response
                return {
                    "success": True,
                    "message": "Form filled successfully",
                    "customer_type": form_data['customerInformation']['customerType'],
                    "job_name": form_data.get('generalInformation', {}).get('jobName', 'N/A')
                }
            
            finally:
                # Always cleanup browser resources
                automation.cleanup()
        
        except Exception as e:
            error_details = str(e)
            traceback.print_exc()
            return {
                "success": False,
                "error": f"Unexpected error: {error_details}"
            }, 500



if __name__ == '__main__':
    print("🚀 Starting SERVPRO API...")
    print("📋 Available endpoints:")
    print("   GET  /health - Health check")
    print("   POST /fill-form - Fill SERVPRO form with JSON data")
    print("   GET  /docs/ - Interactive API documentation")
    print("\n🌐 API will be available at:")
    print("   Main API: http://localhost:5000")
    print("   Documentation: http://localhost:5000/docs/")
    print("\n📝 Quick test with JSON file upload:")
    print("   curl -X POST http://localhost:5000/fill-form \\")
    print("     -F 'file=@form_data_individual_example.json'")
    print("\n📖 Upload .json files: form_data_individual_example.json, form_data_company_example.json")
    print("⚠️  Note: File must have .json extension and correct SERVPRO form structure")
    print("🔍 Validation: API will provide detailed error messages for invalid files or formats")
    
    app.run(host='0.0.0.0', port=5000, debug=True) 