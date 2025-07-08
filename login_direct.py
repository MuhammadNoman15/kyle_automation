"""
Direct login script for SERVPRO
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def login_direct():
    """Direct login to SERVPRO with specific field targeting"""
    
    # Credentials
    login_url = "https://servpro.ngsapps.net/Enterprise/Module/User/Login.aspx"
    username = "kymcdougall"
    password = "SERVYpro123#"
    company_id = "43513"
    
    print(f"Using credentials - Username: {username}, Company ID: {company_id}")
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--ignore-ssl-errors")
    chrome_options.add_argument("--no-sandbox")
    
    # Initialize Chrome WebDriver
    print("Initializing browser...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.maximize_window()
    
    try:
        # Navigate to login page
        print("Navigating to login URL...")
        driver.get(login_url)
        time.sleep(3)
        
        # STEP 1: Enter Company ID
        print("Entering company ID...")
        # Try to find the company ID field - this is a text input field
        company_field = driver.find_element(By.CSS_SELECTOR, "input#txtCompanyID")
        company_field.clear()
        company_field.send_keys(company_id)
        print(f"Entered company ID: {company_id}")
        
        # Click Next button
        print("Clicking Next button...")
        next_button = driver.find_element(By.CSS_SELECTOR, "input#btnNext")
        next_button.click()
        time.sleep(3)
        
        # STEP 2: Enter Username and Password
        print("Entering username and password...")
        username_field = driver.find_element(By.CSS_SELECTOR, "input#txtUsername")
        username_field.clear()
        username_field.send_keys(username)
        print(f"Entered username: {username}")
        
        password_field = driver.find_element(By.CSS_SELECTOR, "input#txtPassword")
        password_field.clear()
        password_field.send_keys(password)
        print("Entered password")
        
        # Click Login button
        print("Clicking Login button...")
        login_button = driver.find_element(By.CSS_SELECTOR, "input#btnLogin")
        login_button.click()
        
        # Wait for login to complete
        print("Waiting for login to complete...")
        time.sleep(5)
        
        print("\nLogin process completed.")
        print("Browser is now open for you to interact with.")
        print("Press Enter when done to close the browser...")
        input()
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        print("Closing browser...")
        driver.quit()

if __name__ == "__main__":
    login_direct() 