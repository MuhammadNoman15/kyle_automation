# SERVPRO Automation Project

## Project Overview
This project implements a web automation solution for SERVPRO's online platform. The automation handles login and form filling based on provided JSON data.

## Components Created

### 1. Form Automation Library
- **form_automation.py**: Core class for Selenium-based automation
  - Handles form field detection and filling
  - Supports various form elements (text fields, dropdowns, checkboxes, etc.)
  - Includes error handling and logging

### 2. Login Scripts
- **servpro_login.py**: Script to automate login to SERVPRO and navigate to job creation form
  - Uses exact element IDs for reliable field detection
  - Handles popup dismissal
  - Redirects to job creation page after successful login

### 3. Other Scripts
- **simple_login.py**: Simplified login script
- **direct_login.py**: Alternative approach using JavaScript execution
- **xpath_login.py**: Script using XPath selectors with page inspection
- **final_login.py**: Enhanced script with multiple element location strategies
- **run_test.py**: Basic test script

### 4. API Components
- **main.py**: FastAPI application with endpoints for form automation
- **field_mappings.py**: Maps JSON schema fields to form element IDs

## Credentials
- **Company ID**: 43513
- **Username**: kymcdougall
- **Password**: SERVYpro123#
- **Login URL**: https://servpro.ngsapps.net/Enterprise/Module/User/Login.aspx
- **Job Creation URL**: https://servpro.ngsapps.net/Enterprise/Module/Job/CreateJob.aspx

## Key Features
1. **Automated Login**: Handles multi-step login process with company ID, username, and password
2. **Form Navigation**: Automatically navigates to the job creation form
3. **Popup Handling**: Detects and dismisses popups that appear after login
4. **Robust Element Detection**: Uses multiple strategies to find form elements
5. **Error Handling**: Graceful error handling with detailed logging
6. **Flexible Form Filling**: Based on JSON schema for dynamic form filling

## Technical Challenges Addressed
1. **Element Detection**: Used various strategies (ID, name, XPath, CSS selectors) to find elements
2. **Popup Handling**: Implemented methods to handle alerts and modal dialogs
3. **Page Navigation**: Used both standard navigation and JavaScript execution for redirection
4. **Error Recovery**: Implemented fallback mechanisms when primary approaches fail

## Next Steps
1. Complete form filling implementation for the job creation form
2. Enhance error handling and reporting
3. Implement validation of form submission results
4. Add support for additional form types and workflows 