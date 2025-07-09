# SERVPRO Job Creation Form Automation

This script automates the login process and form filling for SERVPRO's job creation system using Selenium WebDriver.

## Features

- **Automated Login**: Handles SERVPRO login with proper popup management
- **Form Automation**: Fills all 9 sections of the job creation form
- **Dual Customer Support**: Supports both Individual and Company customer types
- **Telerik Controls**: Properly handles Telerik RadTextBox, RadComboBox, RadDatePicker, and RadMaskedTextBox controls
- **Phone Number Formatting**: Automatic phone number formatting for masked fields
- **Room Selection**: Handles dual RadListBox controls for room selection
- **Comprehensive Testing**: Individual section testing options

## Requirements

Install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

Run the main script:

```bash
python servpro_login.py
```

### Form Data Options

You can provide form data in three ways:

1. **Sample Data** (built-in)
   - Individual Customer sample data
   - Company Customer sample data

2. **JSON Files** (recommended)
   - Use the provided example files as templates
   - Modify the data to match your requirements

3. **Custom JSON** 
   - Create your own JSON file following the schema

## Example JSON Files

### Individual Customer Format
Use `form_data_individual_example.json` as a template for individual customers:

```json
{
  "customerInformation": {
    "customerType": "Individual",
    "firstName": "John",
    "lastName": "Smith",
    "mainPhoneNumber": {
      "number": "1-404-555-1234",
      "extension": ""
    }
  },
  "jobAddressInformation": {
    "customerType": "Individual",
    "firstName": "John",
    "lastName": "Smith"
  }
}
```

### Company Customer Format
Use `form_data_company_example.json` as a template for company customers:

```json
{
  "customerInformation": {
    "customerType": "Company",
    "companyName": "TechCorp Industries LLC",
    "companyMainPhoneNumber": {
      "number": "1-404-555-7000",
      "extension": "150"
    }
  },
  "jobAddressInformation": {
    "customerType": "Company",
    "companyJobAddress": "2000 Business Park Avenue",
    "companyContactSelection": {
      "existingContact": "Jennifer Martinez"
    }
  }
}
```

## Form Sections

The automation covers all major form sections:

1. **General Information**: Job details, dates, categories
2. **Customer Information**: Customer data (Individual vs Company)
3. **Job Address Information**: Loss location details
4. **Internal Participants**: SERVPRO team members
5. **External Participants**: Insurance contacts, adjusters
6. **Policy Information**: Insurance policy details
7. **Division/Services**: Service selections
8. **Payment Services**: Billing and payment information
9. **Loss Description**: Description and room selection

## Testing Options

The script provides individual section testing:

1. Fill entire form
2. General Information only
3. Customer Information and Job Address only
4. Internal Participants only
5. External Participants only
6. Policy Information only
7. Division/Services only
8. Payment Services only
9. Loss Description & Special Instruction only

## Key Features

### Customer Type Support
- **Individual Customer**: Uses standard customer fields
- **Company Customer**: Uses company-specific fields with TR_CompanyCustomer section

### Phone Number Handling
- Automatic formatting for Telerik RadMaskedTextBox fields
- Supports various phone number formats
- Handles extensions properly

### Room Selection
- Dual RadListBox interface for room affected selection
- Supports transferring rooms from source to chosen list
- Multiple room selection support

## Error Handling

The script includes comprehensive error handling:
- SSL/TLS certificate issues
- Popup management (multiple sequential popups)
- Field identification with multiple selector strategies
- Graceful fallbacks for different form states

## Files

- `servpro_login.py` - Main automation script
- `form_data_individual_example.json` - Individual customer template
- `form_data_company_example.json` - Company customer template
- `requirements.txt` - Python dependencies
- `FORM_FILLING_GUIDE.md` - Detailed field mapping guide

## Browser Requirements

- Google Chrome browser
- ChromeDriver (automatically downloaded)
- Internet connection for SERVPRO access

## Support

For issues or questions:
1. Check the form field IDs in `FORM_FILLING_GUIDE.md`
2. Verify your JSON data format against the examples
3. Ensure Chrome browser is up to date 