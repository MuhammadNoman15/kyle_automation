# SERVPRO API Automation

A REST API service that automates the SERVPRO job creation form filling process. This API accepts raw JSON data in the request body and automatically fills the entire form without any interactive prompts, then extracts the job details from SERVPRO.

## 🚀 Features

- **Non-interactive**: No user prompts - just send JSON and get results
- **Complete form filling**: Fills all sections of the SERVPRO job creation form
- **Individual & Company customers**: Supports both customer types
- **Automatic browser handling**: Manages Chrome browser lifecycle automatically
- **Job creation & extraction**: Automatically clicks "Save & Go to Slideboard" and extracts job number/ID
- **Error handling**: Comprehensive error handling and validation with detailed messages
- **Interactive documentation**: Swagger/OpenAPI docs with testing interface
- **Raw JSON input**: Send JSON data directly in request body

## 📋 Requirements

- Python 3.7+
- Chrome browser installed
- Internet connection
- SERVPRO account credentials (configured in the script)

## 🛠️ Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements_api.txt
   ```

3. **Ensure Chrome browser is installed** (the script will automatically download compatible ChromeDriver)

## 🎯 Usage

### Starting the API Server

```bash
python servpro_api.py
```

The API will start on `http://localhost:5000`

### Available Endpoints

#### 1. Welcome Page
```
GET /
```
Returns API information and available endpoints.

**Response:**
```json
{
    "message": "Welcome to SERVPRO Automation API",
    "version": "1.0",
    "status": "running",
    "endpoints": {
        "health_check": "GET /health",
        "fill_form": "POST /fill-form (send JSON data)",
        "documentation": "GET /docs/"
    },
    "usage": "Send JSON data to /fill-form endpoint to automate SERVPRO form filling"
}
```

#### 2. Health Check
```
GET /health
```
Returns API status.

**Response:**
```json
{
    "status": "healthy",
    "message": "SERVPRO API is running"
}
```

#### 3. Fill Form (Main Endpoint)
```
POST /fill-form
```
Fills the SERVPRO form with raw JSON data sent in request body, creates the job, and extracts job details.

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
Raw JSON object containing complete SERVPRO form data structure

**Response (Success):**
```json
{
    "success": true,
    "message": "Form filled and job created successfully",
    "customer_type": "Individual",
    "job_name": "Smith, John - Water Damage",
    "job_number": "ATL-01812-TMP",
    "job_id": "10228947"
}
```

**Response (Error):**
```json
{
    "success": false,
    "error": "Missing required section: 'division'. Please include the division section with servicesSelected array containing at least one service. Example: {'division': {'servicesSelected': ['Water Mitigation', 'Structure']}}"
}
```

#### 4. API Documentation
```
GET /docs/
```
Interactive Swagger/OpenAPI documentation with request/response models and testing interface.

## 📝 Example Usage

### Quick Start Example

1. **Prepare your JSON data** (use provided examples):
   ```bash
   # Individual customer template
   cat form_data_individual_example.json
   
   # Company customer template
   cat form_data_company_example.json
   ```

2. **Send JSON data to API**:
   ```bash
   curl -X POST http://localhost:5000/fill-form \
     -H "Content-Type: application/json" \
     -d @form_data_individual_example.json
   ```

3. **Expected response**:
   ```json
   {
     "success": true,
     "message": "Form filled and job created successfully",
     "customer_type": "Individual",
     "job_name": "Smith, John - Water Damage",
     "job_number": "ATL-01812-TMP",
     "job_id": "10228947"
   }
   ```

### Using cURL

#### Send JSON data from file
```bash
# Individual customer (load JSON from file)
curl -X POST http://localhost:5000/fill-form \
  -H "Content-Type: application/json" \
  -d @form_data_individual_example.json

# Company customer (load JSON from file)  
curl -X POST http://localhost:5000/fill-form \
  -H "Content-Type: application/json" \
  -d @form_data_company_example.json
```

#### Send JSON data inline
```bash
# Send raw JSON data directly
curl -X POST http://localhost:5000/fill-form \
  -H "Content-Type: application/json" \
  -d '{
    "generalInformation": {
      "officeName": "SPSC, LLC",
      "lossCategory": "Residential",
      "jobName": "Test Job"
    },
    "customerInformation": {
      "customerType": "Individual",
      "firstName": "John",
      "lastName": "Smith",
      "address": "123 Main Street",
      "zipCode": "30309",
      "city": "Atlanta",
      "countyRegion": "Fulton County",
      "country": "USA",
      "stateProvince": "Georgia",
      "mainPhoneNumber": {
        "number": "1-404-555-1234",
        "type": "Mobile"
      }
    },
    "division": {
      "servicesSelected": [
        "Water Mitigation",
        "Structure"
      ]
    }
  }'
```

**Important:** 
- Use `-H "Content-Type: application/json"` header
- Use `-d @filename` to load JSON from file OR `-d 'raw json'` for inline JSON
- The API accepts **only raw JSON data**, **not file uploads**
- **Division section is mandatory** with at least one service selected

#### Check API status:
```bash
# Health check
curl http://localhost:5000/health

# Welcome page
curl http://localhost:5000/
```

### Using Python requests

```python
import requests
import json

# Method 1: Load JSON from file
with open('form_data_individual_example.json', 'r') as f:
    form_data = json.load(f)

response = requests.post(
    'http://localhost:5000/fill-form',
    headers={'Content-Type': 'application/json'},
    json=form_data
)

# Method 2: Send JSON data directly
form_data = {
    "generalInformation": {
        "officeName": "SPSC, LLC",
        "lossCategory": "Residential",
        "jobName": "Test Job"
    },
    "customerInformation": {
        "customerType": "Individual",
        "firstName": "John",
        "lastName": "Smith",
        "address": "123 Main Street",
        "zipCode": "30309",
        "city": "Atlanta",
        "countyRegion": "Fulton County",
        "country": "USA",
        "stateProvince": "Georgia",
        "mainPhoneNumber": {
            "number": "1-404-555-1234",
            "type": "Mobile"
        }
    },
    "division": {
        "servicesSelected": [
            "Water Mitigation",
            "Structure"
        ]
    }
}

response = requests.post(
    'http://localhost:5000/fill-form',
    headers={'Content-Type': 'application/json'},
    json=form_data
)

# Check response
if response.status_code == 200:
    result = response.json()
    if result['success']:
        print("✅ Form filled and job created successfully!")
        print(f"Job: {result['job_name']}")
        print(f"Customer Type: {result['customer_type']}")
        print(f"Job Number: {result.get('job_number', 'N/A')}")
        print(f"Job ID: {result.get('job_id', 'N/A')}")
    else:
        print(f"❌ Error: {result['error']}")
else:
    print(f"❌ HTTP Error: {response.status_code}")
```

### Using JavaScript/Node.js

```javascript
const axios = require('axios');
const fs = require('fs');

// Method 1: Load JSON from file
const formData = JSON.parse(fs.readFileSync('form_data_individual_example.json', 'utf8'));

axios.post('http://localhost:5000/fill-form', formData, {
    headers: {
        'Content-Type': 'application/json'
    }
})
.then(response => {
    if (response.data.success) {
        console.log('✅ Form filled and job created successfully!');
        console.log(`Job: ${response.data.job_name}`);
        console.log(`Customer Type: ${response.data.customer_type}`);
        console.log(`Job Number: ${response.data.job_number || 'N/A'}`);
        console.log(`Job ID: ${response.data.job_id || 'N/A'}`);
    } else {
        console.log(`❌ Error: ${response.data.error}`);
    }
})
.catch(error => {
    console.log(`❌ Request failed: ${error.message}`);
});

// Method 2: Send JSON data directly
const formData2 = {
    generalInformation: {
        officeName: "SPSC, LLC",
        lossCategory: "Residential",
        jobName: "Test Job"
    },
    customerInformation: {
        customerType: "Individual",
        firstName: "John",
        lastName: "Smith",
        address: "123 Main Street",
        zipCode: "30309",
        city: "Atlanta",
        countyRegion: "Fulton County",
        country: "USA",
        stateProvince: "Georgia",
        mainPhoneNumber: {
            number: "1-404-555-1234",
            type: "Mobile"
        }
    },
    division: {
        servicesSelected: [
            "Water Mitigation",
            "Structure"
        ]
    }
};

axios.post('http://localhost:5000/fill-form', formData2, {
    headers: {
        'Content-Type': 'application/json'
    }
})
.then(response => {
    console.log('Response:', response.data);
});
```

## 📊 JSON Data Structure

### Required Fields

The JSON request must include at minimum:
- `generalInformation` object with mandatory fields:
  - `officeName` (required)
  - `lossCategory` (required)
- `customerInformation` object with mandatory customer details based on type
- `division` object with `servicesSelected` array (at least one service required)

### Customer Types

#### Individual Customer
- Set `customerInformation.customerType` to `"Individual"`
- **Required fields**: `firstName`, `lastName`, `address`, `zipCode`, `city`, `countyRegion`, `country`, `stateProvince`, `mainPhoneNumber`
- See `form_data_individual_example.json` for complete structure

#### Company Customer
- Set `customerInformation.customerType` to `"Company"`
- **Required fields**: `companyName`, `companyAddress`, `companyZipCode`, `companyCity`, `companyCountyRegion`, `companyCountry`, `companyStateProvince`, `companyMainPhoneNumber`
- See `form_data_company_example.json` for complete structure

### Complete Form Sections

1. **generalInformation**: Job details, dates, categories
2. **customerInformation**: Customer details (Individual or Company)
3. **jobAddressInformation**: Job site address information
4. **internalParticipants**: SERVPRO team members
5. **externalParticipants**: External contacts and companies
6. **policyInformation**: Insurance policy details
7. **division**: Services to be provided (REQUIRED)
8. **paymentServices**: Payment and billing information
9. **lossDescriptionSection**: Loss description and affected rooms

### Mandatory Fields Validation

The API validates mandatory fields marked with red asterisks in the SERVPRO form:

**General Information (Required):**
- `officeName`
- `lossCategory`

**Individual Customer (Required):**
- `firstName`, `lastName`
- `address`, `zipCode`, `city`, `countyRegion`, `country`, `stateProvince`
- `mainPhoneNumber.number`

**Company Customer (Required):**
- `companyName`
- `companyAddress`, `companyZipCode`, `companyCity`, `companyCountyRegion`, `companyCountry`, `companyStateProvince`
- `companyMainPhoneNumber.number`

**Division Services (Required):**
- `division.servicesSelected` - Array of selected services (at least one required)
- Available services: "Temporary Repairs", "Water Mitigation", "Reconstruction", "Structure", "Contents", "Roofing", "Negotiated Work Reconstruction", "DRT - Water", "DRT - Mold", "DRT - Reconstruction", "DRT - Misc", "DRT - Fire", "General Cleaning", "Mold"

### Division Section Format

The division section is **mandatory** and must use the `servicesSelected` array format:

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

**Available Services:**
- "Temporary Repairs"
- "Water Mitigation" 
- "Reconstruction"
- "Structure"
- "Contents"
- "Roofing"
- "Negotiated Work Reconstruction"
- "DRT - Water"
- "DRT - Mold"
- "DRT - Reconstruction"
- "DRT - Misc"
- "DRT - Fire"
- "General Cleaning"
- "Mold"

## 🔄 Complete Process Flow

The API performs the following automated steps:

1. **Validates JSON data** - Checks all mandatory fields and division services
2. **Opens browser instance** - Initializes Chrome with automatic ChromeDriver download
3. **Logs into SERVPRO** - Uses configured credentials to access the system
4. **Navigates to job creation form** - Goes to the job creation page
5. **Fills all form sections** - Populates form with provided JSON data
6. **Clicks "Save & Go to Slideboard"** - Submits the form and redirects to slideboard
7. **Extracts job details** - Gets job number and job ID from the slideboard URL
8. **Waits 5 seconds** - Allows time to see the result before cleanup
9. **Closes browser** - Cleans up resources
10. **Returns response** - Provides success status with job details or error message

## 🧪 Testing Validation

### Test Case 1: Missing Division Section
```json
{
  "generalInformation": {
    "officeName": "SPSC, LLC",
    "lossCategory": "Residential"
  },
  "customerInformation": {
    "customerType": "Individual",
    "firstName": "John",
    "lastName": "Smith",
    "address": "123 Main Street",
    "zipCode": "30309",
    "city": "Atlanta",
    "countyRegion": "Fulton County",
    "country": "USA",
    "stateProvince": "Georgia",
    "mainPhoneNumber": {
      "number": "1-404-555-1234"
    }
  }
}
```
**Expected Error:** "Missing required section: 'division'. Please include the division section with servicesSelected array containing at least one service."

### Test Case 2: Empty Division Services
```json
{
  "generalInformation": {
    "officeName": "SPSC, LLC",
    "lossCategory": "Residential"
  },
  "customerInformation": {
    "customerType": "Individual",
    "firstName": "John",
    "lastName": "Smith",
    "address": "123 Main Street",
    "zipCode": "30309",
    "city": "Atlanta",
    "countyRegion": "Fulton County",
    "country": "USA",
    "stateProvince": "Georgia",
    "mainPhoneNumber": {
      "number": "1-404-555-1234"
    }
  },
  "division": {
    "servicesSelected": []
  }
}
```
**Expected Error:** "At least one Division service must be selected. Please add services to the servicesSelected array."

### Test Case 3: Valid Request
```json
{
  "generalInformation": {
    "officeName": "SPSC, LLC",
    "lossCategory": "Residential",
    "jobName": "Test Job - Water Damage"
  },
  "customerInformation": {
    "customerType": "Individual",
    "firstName": "John",
    "lastName": "Smith",
    "address": "123 Main Street",
    "zipCode": "30309",
    "city": "Atlanta",
    "countyRegion": "Fulton County",
    "country": "USA",
    "stateProvince": "Georgia",
    "mainPhoneNumber": {
      "number": "1-404-555-1234"
    }
  },
  "division": {
    "servicesSelected": [
      "Water Mitigation",
      "Structure"
    ]
  }
}
```
**Expected Success Response:**
```json
{
  "success": true,
  "message": "Form filled and job created successfully",
  "customer_type": "Individual",
  "job_name": "Test Job - Water Damage",
  "job_number": "ATL-01812-TMP",
  "job_id": "10228947"
}
```

## 🔧 Configuration

### Credentials
The API uses hardcoded credentials in `servpro_api.py`. To change them, modify:

```python
# In the login_to_servpro method
username = "your_username"
password = "your_password"
company_id = "your_company_id"
```

### Browser Options
Chrome browser options can be modified in the `setup_driver()` function imported from `servpro_login.py`.

## 🐛 Troubleshooting

### Common Issues

1. **Chrome/ChromeDriver compatibility**
   - The script automatically downloads compatible ChromeDriver
   - Ensure Chrome browser is installed and up to date

2. **Login failures**
   - Verify credentials in the script
   - Check SERVPRO website accessibility
   - Ensure no VPN/firewall blocking access

3. **JSON validation errors**
   - Validate JSON structure against examples
   - Check for missing required fields (especially division section)
   - Ensure data values match expected formats
   - Verify Content-Type header is set to application/json

4. **Division validation errors**
   - Ensure division section is present
   - Check that servicesSelected array has at least one service
   - Use exact service names from the available list

5. **API server not starting**
   - Check if port 5000 is available
   - Install all required dependencies
   - Check Python version compatibility

6. **"Method Not Allowed" error**
   - Ensure you're using POST method for /fill-form
   - Verify URL is correct (http://localhost:5000/fill-form)

7. **Content-Type errors**
   - Always include header: `Content-Type: application/json`
   - Don't use multipart/form-data (old file upload method)

8. **Submit button not working**
   - Check terminal logs for detailed button click attempts
   - Verify form was filled completely before submit
   - Look for any validation errors on the SERVPRO page

### Debug Mode

The API runs in debug mode by default. Check console output for detailed error messages including:

- 🔍 JSON validation results
- 🌐 Browser operations
- 🔐 Login process
- 📝 Form filling progress
- 🖱️ Button click attempts
- 📄 URL changes and redirects
- ✅ Success indicators
- ❌ Error details

### Enhanced Error Messages

The API provides specific error messages for different validation failures:

- **Missing sections**: Tells you exactly which section is missing
- **Empty fields**: Identifies which required fields are empty
- **Division errors**: Provides available service options
- **Format errors**: Shows correct JSON structure examples

## 📄 Example Files

- `form_data_individual_example.json` - Complete Individual customer example with division
- `form_data_company_example.json` - Complete Company customer example with division
- `requirements_api.txt` - Python dependencies

## 🔒 Security Notes

- Credentials are stored in plain text in the script
- The API runs without authentication - secure your deployment
- Browser automation may leave traces - ensure compliance with usage policies
- Consider running in isolated environment for production use

## 🚀 Deployment

For production deployment:

1. **Environment Variables**: Move credentials to environment variables
2. **Authentication**: Add API authentication (API keys, OAuth, etc.)
3. **Logging**: Implement proper logging framework
4. **Error Handling**: Enhanced error handling and monitoring
5. **Docker**: Consider containerization for easier deployment
6. **HTTPS**: Use HTTPS in production
7. **Rate Limiting**: Implement rate limiting to prevent abuse

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review console logs for error details
3. Verify JSON structure against examples
4. Test with sample data first
5. Use the interactive Swagger documentation at `/docs/`
6. Ensure division section is properly formatted

## 🎯 API Testing

Test the API step by step:

1. **Start the API**: `python servpro_api.py`
2. **Health Check**: `curl http://localhost:5000/health`
3. **View Documentation**: Open `http://localhost:5000/docs/` in your browser
4. **Test Validation**: Try the test cases above to see error messages
5. **Test with Valid Data**: 
   ```bash
   curl -X POST http://localhost:5000/fill-form \
     -H "Content-Type: application/json" \
     -d @form_data_individual_example.json
   ```
6. **Check Job Details**: Verify you receive job_number and job_id in response

## 🎨 Interactive Testing

The best way to test the API is using the Swagger UI:

1. Open `http://localhost:5000/docs/` in your browser
2. Click on "POST /fill-form" endpoint
3. Click "Try it out"
4. Enter your JSON data in the request body (ensure division section is included)
5. Click "Execute" to test

The Swagger UI provides:
- ✅ Empty input fields (no sample data)
- ✅ Interactive JSON editor
- ✅ Real-time validation
- ✅ Response preview with job details
- ✅ Clear error messages for validation failures

## 🎉 Success Response

When everything works correctly, you'll receive:

```json
{
  "success": true,
  "message": "Form filled and job created successfully",
  "customer_type": "Individual",
  "job_name": "Smith, John - Water Damage",
  "job_number": "ATL-01812-TMP",
  "job_id": "10228947"
}
```

The `job_number` and `job_id` are extracted from the SERVPRO slideboard URL after successful form submission and can be used for tracking and reference in your systems.

The API automatically handles the complete workflow from validation to job creation, providing a seamless automation experience for SERVPRO form processing. 