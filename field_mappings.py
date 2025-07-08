"""
Field mappings for the form automation
Maps JSON schema fields to form element IDs/selectors
"""

# General Information Fields
GENERAL_INFO_FIELDS = {
    "receivedBy": "ctl00_ContentPlaceHolder1_JobParentInformation_GenaralInfo_comboBox_ReceivedBy_Input",
    "jobName": "ctl00_ContentPlaceHolder1_JobParentInformation_GenaralInfo_JobNameRadTextBox",
    "reportedBy": "ctl00_ContentPlaceHolder1_JobParentInformation_GenaralInfo_DropDown_ReportedBY_Input",
    "referredBy": "ctl00_ContentPlaceHolder1_JobParentInformation_GenaralInfo_DropDown_ReferredBy_Input",
    "jobSize": "ctl00_ContentPlaceHolder1_JobParentInformation_GenaralInfo_JobSizeComboBox_Input",
    "officeName": "ctl00_ContentPlaceHolder1_JobParentInformation_GenaralInfo_comboBoxOffice_Input",
    "dateOfLoss": "ctl00_ContentPlaceHolder1_JobParentInformation_GenaralInfo_DatePicker_DateOffLoss_dateInput",
    "lossCategory": "ctl00_ContentPlaceHolder1_JobParentInformation_GenaralInfo_comboBox_LossCategory_Input",
    "environmentalCode": "ctl00_ContentPlaceHolder1_JobParentInformation_GenaralInfo_comboBoxEnvironmentalCode_Input",
    "catReference": "ctl00_ContentPlaceHolder1_JobParentInformation_GenaralInfo_RadComboBox_Catastrophe_Input",
    "priority": "ctl00_ContentPlaceHolder1_JobParentInformation_GenaralInfo_comboBoxPriority_Input",
    "lossType": "ctl00_ContentPlaceHolder1_JobParentInformation_GenaralInfo_comboBox_LossType_Input",
    "secondaryLossType": "ctl00_ContentPlaceHolder1_JobParentInformation_GenaralInfo_comboBox_SecondryLossType_Input",
    "sourceOfLoss": "ctl00_ContentPlaceHolder1_JobParentInformation_GenaralInfo_SourceOfLossComboBox_Input"
}

# Customer Information Fields
CUSTOMER_INFO_FIELDS = {
    "customerType": {
        "Individual": "ctl00_ContentPlaceHolder1_JobParentInformation_RadioButton_IndividualCustomer",
        "Company": "ctl00_ContentPlaceHolder1_JobParentInformation_RadioButton_CompanyCustomer"
    },
    "customer": "ctl00_ContentPlaceHolder1_JobParentInformation_DropDown_Customer_Input",
    "title": "ctl00_ContentPlaceHolder1_JobParentInformation_ctl17_TitleDropDownTree",
    "firstName": "ctl00_ContentPlaceHolder1_JobParentInformation_TextBox_FirstName",
    "lastName": "ctl00_ContentPlaceHolder1_JobParentInformation_TextBox_LastName",
    "email": "ctl00_ContentPlaceHolder1_JobParentInformation_TextBox_Email",
    "secondaryEmail": "ctl00_ContentPlaceHolder1_JobParentInformation_TextBox_SecondaryEmail",
    "address": "ctl00_ContentPlaceHolder1_JobParentInformation_TextBox_Address_Input",
    "zipCode": "ctl00_ContentPlaceHolder1_JobParentInformation_TextBox_Zip",
    "city": "ctl00_ContentPlaceHolder1_JobParentInformation_TextBox_City",
    "countyRegion": "ctl00_ContentPlaceHolder1_JobParentInformation_comboBox_CustomerCounty_Input",
    "country": "ctl00_ContentPlaceHolder1_JobParentInformation_DropDown_Country_Input",
    "stateProvince": "ctl00_ContentPlaceHolder1_JobParentInformation_DropDown_State_Input"
}

# Phone Number Fields
PHONE_FIELDS = {
    "mainPhoneNumber": {
        "number": "ctl00_ContentPlaceHolder1_JobParentInformation_TextBox_MainPhone",
        "type": {
            "Business": "ctl00_ContentPlaceHolder1_JobParentInformation_DropDown_BusinessPhone_Input",
            "Mobile": "ctl00_ContentPlaceHolder1_JobParentInformation_DropDown_MobilePhone_Input",
            "Home": "ctl00_ContentPlaceHolder1_JobParentInformation_DropDown_HomePhone_Input",
            "Fax": "ctl00_ContentPlaceHolder1_JobParentInformation_DropDown_FaxPhone_Input",
            "Other": "ctl00_ContentPlaceHolder1_JobParentInformation_DropDown_OtherPhone_Input"
        }
    }
}

# Job Address Fields
JOB_ADDRESS_FIELDS = {
    "isSameAsCustomerAddress": "ctl00_ContentPlaceHolder1_JobParentInformation_CheckBox_SameAsIndividualLossAddress",
    "firstName": "ctl00_ContentPlaceHolder1_JobParentInformation_TextBox_JobAddressFirstName",
    "lastName": "ctl00_ContentPlaceHolder1_JobParentInformation_TextBox_JobAddressLastName",
    "address": "ctl00_ContentPlaceHolder1_JobParentInformation_TextBox_AddressLoss_Input",
    "zipCode": "ctl00_ContentPlaceHolder1_JobParentInformation_TextBox_JobAddressZip",
    "city": "ctl00_ContentPlaceHolder1_JobParentInformation_TextBox_JobAddressCity",
    "countyRegion": "ctl00_ContentPlaceHolder1_JobParentInformation_comboBox_JobAddressCounty_Input",
    "country": "ctl00_ContentPlaceHolder1_JobParentInformation_DropDown_JobAddressCountry_Input",
    "stateProvince": "ctl00_ContentPlaceHolder1_JobParentInformation_DropDown_JobAddressState_Input"
}

# Internal Participants Fields
INTERNAL_PARTICIPANTS_FIELDS = {
    "estimator": "ctl00_ContentPlaceHolder1_JobParentInformation_EstimatorDropDown_Input",
    "coordinator": "ctl00_ContentPlaceHolder1_JobParentInformation_CoordinatorDropDown_Input",
    "supervisor": "ctl00_ContentPlaceHolder1_JobParentInformation_SupervisorDropDown_Input",
    "foreman": "ctl00_ContentPlaceHolder1_JobParentInformation_ForemanDropDown_Input",
    "accounting": "ctl00_ContentPlaceHolder1_JobParentInformation_AccountingDropDown_Input",
    "marketing": "ctl00_ContentPlaceHolder1_JobParentInformation_MarketingDropDown_Input",
    "dispatcher": "ctl00_ContentPlaceHolder1_JobParentInformation_DispatcherDropDown_Input",
    "naAdministrator": "ctl00_ContentPlaceHolder1_JobParentInformation_NAAdministratorDropDown_Input",
    "naFieldAccountsManager": "ctl00_ContentPlaceHolder1_JobParentInformation_NAFieldAccountsManagerDropDown_Input"
}

# External Participants Fields
EXTERNAL_PARTICIPANTS_FIELDS = {
    "brokerAgent": "ctl00_ContentPlaceHolder1_JobParentInformation_BrokerAgentDropDown_Input",
    "brokerAgentContact": "ctl00_ContentPlaceHolder1_JobParentInformation_BrokerAgentContactDropDown_Input",
    "insuranceCarrier": "ctl00_ContentPlaceHolder1_JobParentInformation_InsuranceCarrierDropDown_Input",
    "primaryAdjuster": "ctl00_ContentPlaceHolder1_JobParentInformation_PrimaryAdjusterDropDown_Input",
    "primaryFieldAdjuster": "ctl00_ContentPlaceHolder1_JobParentInformation_PrimaryFieldAdjusterDropDown_Input",
    "propertyManagement": "ctl00_ContentPlaceHolder1_JobParentInformation_PropertyManagementDropDown_Input",
    "propertyManagementContact": "ctl00_ContentPlaceHolder1_JobParentInformation_PropertyManagementContactDropDown_Input",
    "contractorCompany": "ctl00_ContentPlaceHolder1_JobParentInformation_ContractorCompanyDropDown_Input",
    "contractorContact": "ctl00_ContentPlaceHolder1_JobParentInformation_ContractorContactDropDown_Input",
    "independentAdjustingFirm": "ctl00_ContentPlaceHolder1_JobParentInformation_IndependentAdjustingFirmDropDown_Input",
    "independentAdjusterContact": "ctl00_ContentPlaceHolder1_JobParentInformation_IndependentAdjusterContactDropDown_Input",
    "publicAdjustingFirm": "ctl00_ContentPlaceHolder1_JobParentInformation_PublicAdjustingFirmDropDown_Input",
    "publicAdjusterContact": "ctl00_ContentPlaceHolder1_JobParentInformation_PublicAdjusterContactDropDown_Input",
    "primaryMortgage": "ctl00_ContentPlaceHolder1_JobParentInformation_PrimaryMortgageDropDown_Input",
    "secondaryMortgage": "ctl00_ContentPlaceHolder1_JobParentInformation_SecondaryMortgageDropDown_Input",
    "tpaCompany": "ctl00_ContentPlaceHolder1_JobParentInformation_TPACompanyDropDown_Input",
    "tpa": "ctl00_ContentPlaceHolder1_JobParentInformation_TPADropDown_Input",
    "billToCompany": "ctl00_ContentPlaceHolder1_JobParentInformation_BillToCompanyDropDown_Input",
    "billToContact": "ctl00_ContentPlaceHolder1_JobParentInformation_BillToContactDropDown_Input",
    "secondaryContact": "ctl00_ContentPlaceHolder1_JobParentInformation_SecondaryContactDropDown_Input",
    "businessContact": "ctl00_ContentPlaceHolder1_JobParentInformation_BusinessContactDropDown_Input"
}

# Policy Information Fields
POLICY_INFO_FIELDS = {
    "claimNumber": "ctl00_ContentPlaceHolder1_JobParentInformation_TextBox_ClaimNumber",
    "fileNumber": "ctl00_ContentPlaceHolder1_JobParentInformation_TextBox_FileNumber",
    "policyNumber": "ctl00_ContentPlaceHolder1_JobParentInformation_TextBox_PolicyNumber",
    "yearBuilt": "ctl00_ContentPlaceHolder1_JobParentInformation_TextBox_YearBuilt",
    "policyStartDate": "ctl00_ContentPlaceHolder1_JobParentInformation_DatePicker_PolicyStartDate_dateInput",
    "policyExpirationDate": "ctl00_ContentPlaceHolder1_JobParentInformation_DatePicker_PolicyExpirationDate_dateInput"
}

# Division Fields
DIVISION_FIELDS = {
    "servicesSelected": {
        "Temporary repairs": "ctl00_ContentPlaceHolder1_JobParentInformation_CheckBox_TemporaryRepairs",
        "Water Mitigation": "ctl00_ContentPlaceHolder1_JobParentInformation_CheckBox_WaterMitigation",
        "Reconstruction": "ctl00_ContentPlaceHolder1_JobParentInformation_CheckBox_Reconstruction",
        "Structure": "ctl00_ContentPlaceHolder1_JobParentInformation_CheckBox_Structure",
        "Contents": "ctl00_ContentPlaceHolder1_JobParentInformation_CheckBox_Contents",
        "Roofing": "ctl00_ContentPlaceHolder1_JobParentInformation_CheckBox_Roofing",
        "General Cleaning": "ctl00_ContentPlaceHolder1_JobParentInformation_CheckBox_GeneralCleaning",
        "Mold": "ctl00_ContentPlaceHolder1_JobParentInformation_CheckBox_Mold"
    }
}

# Payment Services Fields
PAYMENT_SERVICES_FIELDS = {
    "deductibleRequired": "ctl00_ContentPlaceHolder1_JobParentInformation_DropDown_DeductibleRequired_Input",
    "amount": "ctl00_ContentPlaceHolder1_JobParentInformation_TextBox_Amount",
    "collectWhen": "ctl00_ContentPlaceHolder1_JobParentInformation_DropDown_CollectWhen_Input",
    "dwellingLimits": "ctl00_ContentPlaceHolder1_JobParentInformation_textBox_Dwelling",
    "contentsLimits": "ctl00_ContentPlaceHolder1_JobParentInformation_textBox_Contents",
    "otherStructuresLimits": "ctl00_ContentPlaceHolder1_JobParentInformation_textBox_OtherStructures",
    "selfPay": "ctl00_ContentPlaceHolder1_JobParentInformation_CheckBox_SelfPay"
}

# Loss Description & Special Instruction Fields
LOSS_DESCRIPTION_FIELDS = {
    "lossDescription": "ctl00_ContentPlaceHolder1_JobParentInformation_TextBox_LossDescription",
    "specialInstructions": "ctl00_ContentPlaceHolder1_JobParentInformation_TextBox_SpecialInstructions",
    "roomsAffected": "ctl00_ContentPlaceHolder1_JobParentInformation_ListBox_RoomsAffected"
}

# Save Button
SAVE_BUTTON = "ctl00_ContentPlaceHolder1_JobParentInformation_Button_SaveAndGoToSlideBoardBottom"

# All field mappings combined
ALL_FIELD_MAPPINGS = {
    "generalInformation": GENERAL_INFO_FIELDS,
    "customerInformation": CUSTOMER_INFO_FIELDS,
    "phoneFields": PHONE_FIELDS,
    "jobAddressInformation": JOB_ADDRESS_FIELDS,
    "internalParticipants": INTERNAL_PARTICIPANTS_FIELDS,
    "externalParticipants": EXTERNAL_PARTICIPANTS_FIELDS,
    "policyInformation": POLICY_INFO_FIELDS,
    "division": DIVISION_FIELDS,
    "paymentServices": PAYMENT_SERVICES_FIELDS,
    "lossDescriptionAndSpecialInstruction": LOSS_DESCRIPTION_FIELDS
} 