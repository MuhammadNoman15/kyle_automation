# SERVPRO API Automation

A REST API service that automates the SERVPRO job creation form filling process. This API accepts JSON data and automatically fills the entire form without any interactive prompts.

## 🚀 Features

- **Non-interactive**: No user prompts - just send JSON and get results
- **Complete form filling**: Fills all sections of the SERVPRO job creation form
- **Individual & Company customers**: Supports both customer types
- **Automatic browser handling**: Manages Chrome browser lifecycle automatically
- **Error handling**: Comprehensive error handling and validation
- **Interactive documentation**: Swagger/OpenAPI docs with testing interface

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

#### 1. Health Check
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

#### 2. Fill Form (Main Endpoint)
```
POST /fill-form
```
Fills the SERVPRO form with uploaded JSON file.

**Request Type:**
```
Content-Type: multipart/form-data
```

**Request Body:**
Form data with file upload containing JSON data (see examples below)

**Response (Success):**
```json
{
    "success": true,
    "message": "Form filled successfully",
    "customer_type": "Individual",
    "job_name": "Smith, John - Water Damage"
}
```

**Response (Error):**
```json
{
    "success": false,
    "error": "Error description"
}
```

#### 3. API Documentation
```
GET /docs/
```
Interactive Swagger/OpenAPI documentation with request/response models and testing interface.

## 📝 Example Usage

### Quick Start Example

1. **Prepare your JSON file** (use provided examples):
   ```bash
   # Individual customer
   ls form_data_individual_example.json
   
   # Company customer  
   ls form_data_company_example.json
   ```

2. **Upload JSON file to API**:
   ```bash
   curl -X POST http://localhost:5000/fill-form \
     -F "file=@example_individual_request.json"
   ```

3. **Expected response**:
   ```json
   {
     "success": true,
     "message": "Form filled successfully",
     "customer_type": "Individual",
     "job_name": "Smith, John - Water Damage"
   }
   ```

### Using cURL

#### Upload JSON files
```bash
# Individual customer (upload JSON file)
curl -X POST http://localhost:5000/fill-form \
  -F "file=@example_individual_request.json"

# Company customer (upload JSON file)  
curl -X POST http://localhost:5000/fill-form \
  -F "file=@example_company_request.json"
```

**Important:** 
- `-F "file=@filename"` = Upload JSON file (multipart/form-data)
- The API **only accepts** .json file uploads, **not raw JSON text**
- File must have .json extension
- Content-Type is automatically set to multipart/form-data by curl

#### Check API documentation:
```bash
# Open in browser: http://localhost:5000/docs/
curl http://localhost:5000/health
```

### Using Python requests

```python
import requests

# Upload JSON file to API
with open('example_individual_request.json', 'rb') as f:
    files = {'file': ('example_individual_request.json', f, 'application/json')}
    response = requests.post('http://localhost:5000/fill-form', files=files)

# Check response
if response.status_code == 200:
    result = response.json()
    if result['success']:
        print("✅ Form filled successfully!")
        print(f"Job: {result['job_name']}")
        print(f"Customer Type: {result['customer_type']}")
    else:
        print(f"❌ Error: {result['error']}")
else:
    print(f"❌ HTTP Error: {response.status_code}")
```

### Using JavaScript/Node.js

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

// Create form data for file upload
const form = new FormData();
form.append('file', fs.createReadStream('example_individual_request.json'));

// Upload file
axios.post('http://localhost:5000/fill-form', form, {
    headers: {
        ...form.getHeaders()
    }
})
.then(response => {
    if (response.data.success) {
        console.log('✅ Form filled successfully!');
        console.log(`Job: ${response.data.job_name}`);
        console.log(`Customer Type: ${response.data.customer_type}`);
    } else {
        console.log(`❌ Error: ${response.data.error}`);
    }
})
.catch(error => {
    console.log(`❌ Request failed: ${error.message}`);
});
```

## 📊 JSON Data Structure

### Required Fields

The JSON request must include at minimum:
- `generalInformation` object with basic job details
- `customerInformation` object with customer type and details

### Customer Types

#### Individual Customer
- Set `customerInformation.customerType` to `"Individual"`
- Use individual-specific fields (firstName, lastName, etc.)
- See `example_individual_request.json` for complete structure

#### Company Customer
- Set `customerInformation.customerType` to `"Company"`
- Use company-specific fields (companyName, companyAddress, etc.)
- See `example_company_request.json` for complete structure

### Complete Form Sections

1. **generalInformation**: Job details, dates, categories
2. **customerInformation**: Customer details (Individual or Company)
3. **jobAddressInformation**: Job site address information
4. **internalParticipants**: SERVPRO team members
5. **externalParticipants**: External contacts and companies
6. **policyInformation**: Insurance policy details
7. **division**: Services to be provided
8. **paymentServices**: Payment and billing information
9. **lossDescriptionSection**: Loss description and affected rooms

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

3. **Form filling errors**
   - Validate JSON structure against examples
   - Check for missing required fields
   - Ensure data values match expected formats

4. **API server not starting**
   - Check if port 5000 is available
   - Install all required dependencies
   - Check Python version compatibility

### Debug Mode

The API runs in debug mode by default. Check console output for detailed error messages.

### Log Messages

The API provides detailed console logging:
- 🌐 Browser operations
- 🔐 Login process
- 📝 Form filling progress
- ✅ Success indicators
- ❌ Error details

## 📄 Example Files

- `example_individual_example.json` - Complete Individual customer example
- `example_company_example.json` - Complete Company customer example
- `requirements.txt` - Python dependencies


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

## 🎯 API Testing

Test the API step by step:

1. **Start the API**: `python servpro_api.py`
2. **Health Check**: `curl http://localhost:5000/health`
3. **View Documentation**: Open `http://localhost:5000/docs/` in your browser
4. **Test with Examples**: Use the provided JSON example files
5. **Use Your Data**: Replace with your actual form data

The API automatically handles browser lifecycle, so each request is independent and complete. 