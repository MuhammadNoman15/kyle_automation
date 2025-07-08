# SERVPRO Form Filling Automation Guide

## Overview

The `servpro_login.py` script now includes comprehensive form-filling functionality that can automatically populate the SERVPRO job creation form with data from JSON files or sample data.

## Features

### ✅ **Supported Form Elements**
- **Text Fields**: Names, addresses, phone numbers, emails, etc.
- **Dropdown Fields**: States, countries, loss types, priorities, etc.
- **Checkbox Fields**: Service selections, same-address options
- **Date Fields**: Date of loss, policy dates
- **Radio Buttons**: Customer type (Individual/Company)
- **Telerik Controls**: RadTextBox, RadComboBox, RadDatePicker

### ✅ **Form Sections Covered**
1. **General Information** (Job details, loss information)
2. **Customer Information** (Contact details, addresses)
3. **Job Address Information** (Loss location)
4. **Internal Participants** (Staff assignments)
5. **External Participants** (Insurance, adjusters)
6. **Policy Information** (Claims, policy details)
7. **Division/Services** (Service selections)

## Usage

### 1. **Basic Usage with Sample Data**
```bash
python servpro_login.py
```
- Login automatically
- When prompted, choose `y` to fill form
- Choose `1` for sample data
- Form will be filled automatically

### 2. **Using Custom JSON Data**
```bash
python servpro_login.py
```
- Login automatically
- When prompted, choose `y` to fill form
- Choose `2` to load from JSON file
- Provide path to your JSON file (or use default `form_data.json`)

### 3. **JSON File Structure**

Use `form_data_example.json` as a template. The structure follows this pattern:

```json
{
  "generalInformation": {
    "receivedBy": "Kyle McDougall",
    "jobName": "Smith, John",
    "reportedBy": "Property Owner",
    "dateOfLoss": "12/15/2024",
    "lossCategory": "Residential",
    "environmentalCode": "Select Mitigation",
    "priority": "High",
    "lossType": "Water",
    "secondaryLossType": "Pipe",
    "sourceOfLoss": "Pipe Break"
  },
  "customerInformation": {
    "customerType": "Individual",
    "firstName": "John",
    "lastName": "Smith",
    "email": "john.smith@email.com",
    "address": "123 Main Street",
    "zipCode": "30309",
    "city": "Atlanta",
    "stateProvince": "Georgia",
    "mainPhoneNumber": {
      "number": "1-404-555-1234",
      "type": "Mobile"
    }
  }
  // ... more sections
}
```

## Field Mappings

### **General Information Fields**
| JSON Field | Form Field ID | Type |
|------------|---------------|------|
| `receivedBy` | `TextBox_ReceivedBy` | Text |
| `jobName` | `TextBox_JobName` | Text |
| `reportedBy` | `DropDown_ReportedBy` | Dropdown |
| `dateOfLoss` | `DatePicker_DateOfLoss` | Date |
| `lossCategory` | `DropDown_LossCategory` | Dropdown |
| `priority` | `DropDown_Priority` | Dropdown |
| `lossType` | `DropDown_LossType` | Dropdown |

### **Customer Information Fields**
| JSON Field | Form Field ID | Type |
|------------|---------------|------|
| `customerType` | `RadioButton_IndividualCustomer/CompanyCustomer` | Radio |
| `firstName` | `TextBox_FirstName` | Text |
| `lastName` | `TextBox_LastName` | Text |
| `email` | `TextBox_Email` | Text |
| `address` | `TextBox_Address` | Text |
| `zipCode` | `TextBox_ZIP` | Text |
| `city` | `TextBox_City` | Text |
| `stateProvince` | `DropDown_State` | Dropdown |

## Customization

### **Creating Your Own JSON Data**
1. Copy `form_data_example.json` to `my_data.json`
2. Modify the values to match your specific job details
3. Run the script and choose option 2 to load from JSON
4. Provide the path to `my_data.json`

### **Programmatic Usage**
You can also use the form-filling functions programmatically:

```python
from servpro_login import fill_job_creation_form, load_form_data_from_json

# Load your data
form_data = load_form_data_from_json('my_custom_data.json')

# Assuming you have a driver instance and are on the job creation page
fill_job_creation_form(driver, form_data)
```

## Error Handling

The script includes robust error handling:
- **Missing Fields**: Warnings logged, script continues
- **Invalid JSON**: Falls back to sample data
- **Field Not Found**: Tries multiple selector strategies
- **Telerik Controls**: Uses JavaScript API for complex controls

## Tips & Best Practices

### ✅ **Data Validation**
- Ensure phone numbers follow format: `1-XXX-XXX-XXXX`
- Use proper date format: `MM/DD/YYYY`
- Job names should be: `LastName, FirstName`

### ✅ **Dropdown Values**
Make sure dropdown values match exactly what appears in the form:
- **Loss Categories**: "Residential", "Commercial", "Multi-Family", "Government"
- **Priority**: "Low", "Medium", "High"
- **Phone Types**: "Business", "Mobile", "Home", "Fax", "Other"

### ✅ **Services Selection**
Services in the `division.servicesSelected` array should match the exact text in the form checkboxes.

## Troubleshooting

### **Common Issues**

1. **Field Not Found**
   - Check if field ID exists in the form
   - Try using browser developer tools to inspect elements
   - Some fields may have different IDs based on form state

2. **Dropdown Not Selecting**
   - Verify the exact text matches what's in the dropdown
   - Some dropdowns use values instead of visible text

3. **Date Fields Not Working**
   - Ensure date format is MM/DD/YYYY
   - Some date fields may require different formats

4. **Telerik Controls Issues**
   - Make sure the page is fully loaded before filling
   - Telerik controls require JavaScript to be enabled

### **Debug Mode**
The script provides detailed logging for each field operation:
- ✅ Success messages for filled fields
- ⚠️ Warning messages for skipped fields
- ❌ Error messages for failed operations

## Support

If you encounter issues:
1. Check the console output for specific error messages
2. Verify your JSON file structure matches the example
3. Ensure all required fields have values
4. Test with sample data first to isolate issues

## Files Structure

```
kyle-automation/
├── servpro_login.py           # Main script with form filling
├── form_data_example.json     # Example JSON template
├── FORM_FILLING_GUIDE.md      # This guide
├── form-source-code.txt       # Form structure reference
└── json.txt                   # JSON schema reference
``` 