---
name: abap_data_element_creator
description: Create a ABAP Data Element in SAP
---

# How to use
When asked to create a data element.

## Steps
1. **Create the data element** using `abap_createObject` with objtype `DTEL/DE` - **MUST include a description** in the `description` parameter
2. **Read the generated XML file** by opening the file in the editor:
   - Path format: `adt://system_name/System Library/PACKAGE_NAME/Dictionary/Data Elements/OBJECT_NAME.dtel.xml`
   - Example: `adt://laboratorio_s4b_150/System Library/ZFI/Dictionary/Data Elements/ZMO_E_STREET.dtel.xml`
3. **Modify the XML structure** using `replace_string_in_file` ensuring ALL required fields are properly set:
   - **🚨 MANDATORY - NEVER SKIP**: The `adtcore:description="description text"` attribute in the `<blue:wbobj>` element is ABSOLUTELY REQUIRED for activation. WITHOUT THIS ATTRIBUTE, THE ACTIVATION WILL FAIL. Always verify this attribute exists and has a meaningful value before attempting activation.
   - Set `typeKind` to `predefinedAbapType` (not "domain")
   - Set appropriate `dataType` (CHAR, NUMC, DATS, TIMS, DEC, INT4, etc.)
   - Set correct `dataTypeLength` (6 digits with leading zeros, e.g., `000030` for 30 characters)
   - Set `dataTypeDecimals` to `000000` (or appropriate value for numeric types)
   - Define all four field labels with meaningful text:
     - `shortFieldLabel` (max 10 chars)
     - `mediumFieldLabel` (max 20 chars)
     - `longFieldLabel` (max 40 chars)
     - `headingFieldLabel` (max 55 chars)
4. **Save the file** - changes are automatically saved when using `replace_string_in_file`
5. **Verify the description attribute** - Before activation, ALWAYS check that `adtcore:description` exists in the `<blue:wbobj>` tag
6. **Activate the object** using `abap_activate`:
   - `objectName`: The data element name (e.g., "ZMO_E_STREET")
   - `objectUrl`: The ADT URL path (e.g., "/sap/bc/adt/ddic/dataelements/zmo_e_street")

## Example XML Structure

Below is an example of a properly configured Data Element XML file:

```xml
<blue:wbobj xmlns:blue="http://www.sap.com/wbobj/dictionary/dtel" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:responsible="USER_NAME" adtcore:masterLanguage="EN" adtcore:masterSystem="SYSTEM_ID" adtcore:abapLanguageVersion="0" adtcore:name="ZFI_E_TYPE" adtcore:type="DTEL/DE" adtcore:description="description" adtcore:language="EN">
<adtcore:packageRef adtcore:name="$TMP" adtcore:type="DEVC/K"/>
<dtel:dataElement xmlns:dtel="http://www.sap.com/adt/dictionary/dataelements">
<dtel:typeKind>predefinedAbapType</dtel:typeKind>
<dtel:typeName/>
<dtel:dataType>CHAR</dtel:dataType>
<dtel:dataTypeLength>000010</dtel:dataTypeLength>
<dtel:dataTypeDecimals>000000</dtel:dataTypeDecimals>
<dtel:shortFieldLabel>Type</dtel:shortFieldLabel>
<dtel:shortFieldLength>10</dtel:shortFieldLength>
<dtel:shortFieldMaxLength>10</dtel:shortFieldMaxLength>
<dtel:mediumFieldLabel>Type</dtel:mediumFieldLabel>
<dtel:mediumFieldLength>20</dtel:mediumFieldLength>
<dtel:mediumFieldMaxLength>20</dtel:mediumFieldMaxLength>
<dtel:longFieldLabel>Type</dtel:longFieldLabel>
<dtel:longFieldLength>30</dtel:longFieldLength>
<dtel:longFieldMaxLength>40</dtel:longFieldMaxLength>
<dtel:headingFieldLabel>Type</dtel:headingFieldLabel>
<dtel:headingFieldLength>40</dtel:headingFieldLength>
<dtel:headingFieldMaxLength>55</dtel:headingFieldMaxLength>
<dtel:searchHelp/>
<dtel:searchHelpParameter/>
<dtel:setGetParameter/>
<dtel:defaultComponentName/>
<dtel:deactivateInputHistory>false</dtel:deactivateInputHistory>
<dtel:changeDocument>false</dtel:changeDocument>
<dtel:leftToRightDirection>false</dtel:leftToRightDirection>
<dtel:deactivateBIDIFiltering>false</dtel:deactivateBIDIFiltering>
</dtel:dataElement>
</blue:wbobj>
```
