---
name: abap_cds_creator
description: 'Skill for creating and modifying ABAP CDS views with file-system based workflow and best practices.'
---

Purpose

- Provide concise, actionable instructions to create and modify ABAP CDS (Core Data Services) views using the modern file-system based workflow.

Critical rules (File-System Workflow)

- Always use file-system based tools: `abap_createobject`, `abap_search`, `read_file`, `replace_string_in_file`, `abap_syntaxcheckcode`, `abap_activate`.
- Activation is mandatory: a CDS view must be activated (`abap_activate`) to be usable.
- Use the correct object type when creating CDS views: `DDLS/DF` for Data Definitions.
- **DO NOT use deprecated tools**: `abap_getsourcecode`, `abap_setsourcecode`.
- **ALWAYS use lock/unlock**: `abap_lock` before editing, `abap_unlock` after activation (REQUIRED by SAP).

Workflow to create or modify a CDS view

### For NEW CDS views:
1. Create CDS View: `abap_createobject` (objtype=DDLS/DF, name, description, parentName).
2. Search Object: `abap_search` (find the CDS view, get ADT URI + objSourceUrl).
3. Read Source: `read_file` (read initial content from ADT URI).
4. Modify CDS View: `replace_string_in_file` (add annotations and SELECT statement).
5. Syntax Check: `abap_syntaxcheckcode` (code=<source>, url=<URI>, objSourceUrl=<path>).
6. Fix Errors: Repeat steps 4-5 if needed.
7. Activate: `abap_activate` (object=<URI>).

### For EXISTING CDS views:
1. Search Object: `abap_search` (find it and get ADT URI + objSourceUrl).
2. Read Source: `read_file` (read current content from ADT URI).
3. Modify Code: `replace_string_in_file` (edit the CDS definition directly in file).
4. Syntax Check: `abap_syntaxcheckcode` (code=<source>, url=<URI>, objSourceUrl=<path>).
5. Fix Errors: Repeat steps 3-4 if needed.
6. Activate: `abap_activate` (object=<URI>).

CDS view-specific developer workflow and best practices

- **Prefer `define view entity`** over `define view` whenever possible (modern syntax, no SQL view name needed).
- Always include proper annotations (`@AccessControl`, `@EndUserText`).
- Use descriptive field aliases in English (CamelCase, no underscores).
- Follow SAP naming conventions for CDS views:
  - `ZXX_I_` for Interface/Basic views (e.g., `ZMM_I_PURCHASE_ORDER`)
  - `ZXX_C_` for Consumption/Projection views (e.g., `ZMM_C_PURCHASE_ORDER`)
  - `ZXX_R_` for Root views in Transactional scenarios
  - XX = Module code (MM, SD, FI, etc.)
- Always validate syntax before activation.
- Use `@AccessControl.authorizationCheck: #NOT_REQUIRED` for simple views (adjust as needed for production).

CDS view structure guideline

**Basic CDS View Entity Structure (Recommended):**
```abap
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Descriptive Label'

define view entity ZMM_I_ViewName
  as select from source_table
{
  key field1 as Field1,
      field2 as Field2,
      field3 as Field3
}
```

**CDS View Entity with Associations:**
```abap
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Descriptive Label'

define view entity ZMM_I_ViewName
  as select from source_table as Source
  association [0..1] to related_table as _Related
    on Source.key_field = _Related.key_field
{
  key Source.field1    as Field1,
      Source.field2    as Field2,
      
      // Associations
      _Related
}
```

**CDS View Entity with Joins:**
```abap
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Descriptive Label'

define view entity ZMM_I_ViewName
  as select from table1 as T1
    inner join table2 as T2
      on T1.key_field = T2.key_field
{
  key T1.field1      as Field1,
      T1.field2      as Field2,
      T2.field3      as Field3
}
```

**CDS View Entity with Parameters:**
```abap
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Descriptive Label'

define view entity ZMM_I_ViewName
  with parameters
    P_CompanyCode : bukrs,
    P_Date        : datum
  as select from source_table
{
  key field1 as Field1,
      field2 as Field2
}
where company_code = :P_CompanyCode
  and date_field   = :P_Date
```

**CDS View Entity with Aggregations:**
```abap
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Descriptive Label'

define view entity ZMM_I_ViewName
  as select from source_table
{
  key field1               as Field1,
      field2               as Field2,
      count(*)             as RecordCount,
      sum(amount)          as TotalAmount,
      avg(price)           as AveragePrice
}
group by field1, field2
```

Naming conventions (CDS views)

- **CDS View Names**: 
  - Start with `Z` or `Y`
  - Include module prefix (MM, SD, FI, etc.)
  - Use type indicator: `I` (Interface), `C` (Consumption), `R` (Root)
  - Example: `ZMM_I_PURCHASE_ORDER`, `ZSD_C_SALES_ORDER`

- **SQL View Names** (only for legacy `define view`, max 16 characters):
  - Start with `Z` or `Y`
  - Use abbreviations
  - Example: `ZMM_V_PURORD`, `ZSD_V_SALORD`
  - **Note**: Not needed when using `define view entity`

- **Field Aliases**:
  - Use CamelCase (no underscores)
  - Use meaningful English names
  - Example: `PurchaseOrder`, `CompanyCode`, `VendorName`

Key tool usage summary (quick reference)

- `abap_createobject`: create new CDS views (use objtype=DDLS/DF).
- `abap_search`: discover CDS view URIs and objSourceUrl.
- `read_file`: read CDS definition from file system (use ADT URI).
- `replace_string_in_file`: modify CDS definition in file system.
- `abap_syntaxcheckcode`: validate CDS syntax (requires code, url, objSourceUrl).
- `abap_activate`: activate the CDS view to make it usable.
- `abap_gettable`: query data from activated CDS views.
- `abap_gettypeinfo`: get DDIC type information.

Important Notes

- **File-System Based**: All modifications go through VS Code's file system using `replace_string_in_file`, not server APIs.
- **No Lock/Unlock**: The file-system workflow does not require `abap_lock` or `abap_unlock`.
- **Syntax Check Parameters**: Always include code, url (ADT URI), and objSourceUrl (path from search results).
- **Deprecated Tools**: Never use `abap_getsourcecode` or `abap_setsourcecode`.
- **Locking Required**: Always use `abap_lock` before editing and `abap_unlock` after activation (SAP requirement).
- **Modern Syntax**: Prefer `define view entity` over `define view` (no `@AbapCatalog.sqlViewName` annotation needed).
- **Legacy Syntax**: Only use `define view` when working with older systems or maintaining existing views.
- **Annotations**: Always include essential annotations for proper CDS view behavior.
- This skill follows the modern file-system based workflow described in the ABAP Developer Agent instructions.

## Complete Example: Purchase Orders CDS View

This example demonstrates the complete workflow for creating a CDS view that reads purchase order data.

### Step 1: Create the CDS View Object
```
Tool: abap_createobject
Input:
  - objtype: DDLS/DF
  - name: ZMM_I_PURCHASE_ORDER
  - description: CDS View for Purchase Orders
  - parentName: $TMP (or your package name)
  - url: adt://laboratorio_s4b_150
```

### Step 2: Search for the Created Object
```
Tool: abap_search
Input:
  - name: ZMM_I_PURCHASE_ORDER
  - type: DDLS
  - url: adt://laboratorio_s4b_150
  
Result:
  - ADT URI: adt://laboratorio_s4b_150/%24TMP/Core%20Data%20Services/Data%20Definitions/ZMM_I_PURCHASE_ORDER.ddls.asddls
  - objSourceUrl: /sap/bc/adt/ddic/ddl/sources/zmm_i_purchase_order/source/main
```

### Step 3: Read Initial Content
```
Tool: read_file
Input:
  - filePath: adt://laboratorio_s4b_150/%24TMP/Core%20Data%20Services/Data%20Definitions/ZMM_I_PURCHASE_ORDER.ddls.asddls
  - startLine: 1
  - endLine: 50
```

### Step 4: Modify the CDS View
```
Tool: replace_string_in_file
Input:
  - filePath: adt://laboratorio_s4b_150/%24TMP/Core%20Data%20Services/Data%20Definitions/ZMM_I_PURCHASE_ORDER.ddls.asddls
  - oldString: (empty initial content)
  - newString: (see complete CDS definition below)
```

**Complete CDS View Entity Definition:**
```abap
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Purchase Orders - Header Data'

define view entity ZMM_I_PURCHASE_ORDER
  as select from ekko
{
  key ebeln                  as PurchaseOrder,
      bukrs                  as CompanyCode,
      bstyp                  as PurchasingDocumentCategory,
      bsart                  as PurchasingDocumentType,
      aedat                  as CreatedOn,
      ernam                  as CreatedBy,
      lifnr                  as Vendor,
      ekorg                  as PurchasingOrganization,
      ekgrp                  as PurchasingGroup,
      waers                  as Currency,
      bedat                  as DocumentDate,
      zterm                  as PaymentTerms,
      inco1                  as IncotermsClassification,
      inco2                  as IncotermsTransferLocation,
      kdatb                  as ValidityStartDate,
      kdate                  as ValidityEndDate,
      knumv                  as PricingDocument,
      submi                  as CollectiveNumber,
      statu                  as Status,
      memory                 as IncompleteStatus,
      procstat               as ProcessingStatus
}
```

### Step 5: Syntax Check
```
Tool: abap_syntaxcheckcode
Input:
  - code: (complete CDS definition from step 4)
  - url: adt://laboratorio_s4b_150
  - objSourceUrl: /sap/bc/adt/ddic/ddl/sources/zmm_i_purchase_order/source/main
  
Expected Result: status: success, no errors
```

### Step 6: Activate the CDS View
```
Tool: abap_activate
Input:
  - url: adt://laboratorio_s4b_150/%24TMP/Core%20Data%20Services/Data%20Definitions/ZMM_I_PURCHASE_ORDER.ddls.asddls
  
Expected Result: Activation successful
```

### Usage
Once activated, the CDS view can be used in:
- ABAP programs: `SELECT * FROM zmm_i_purchase_order WHERE ...`
- Other CDS views: `as select from ZMM_I_PURCHASE_ORDER`
- OData services and Fiori applications

## Additional CDS View Examples

### Example: Purchase Order Items (with Association)
```abap
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Purchase Order Items'

define view entity ZMM_I_PURCHASE_ORDER_ITEM
  as select from ekpo as Item
  association [1..1] to ZMM_I_PURCHASE_ORDER as _Header
    on Item.ebeln = _Header.PurchaseOrder
{
  key Item.ebeln          as PurchaseOrder,
  key Item.ebelp          as PurchaseOrderItem,
      Item.matnr          as Material,
      Item.werks          as Plant,
      Item.menge          as OrderQuantity,
      Item.meins          as OrderUnit,
      Item.netpr          as NetPrice,
      Item.peinh          as PriceUnit,
      Item.brtwr          as GrossAmount,
      Item.netwr          as NetAmount,
      
      // Associations
      _Header
}
```

### Example: Vendor Master Data
```abap
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Vendor Master Data'

define view entity ZMM_I_VENDOR
  as select from lfa1
{
  key lifnr               as Vendor,
      name1               as VendorName,
      name2               as VendorName2,
      ort01               as City,
      land1               as Country,
      regio               as Region,
      pstlz               as PostalCode,
      stras               as Street,
      telf1               as Telephone,
      smtp_addr           as EmailAddress
}
```

### Example: Consumption View with Joins
```abap
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Purchase Orders - Complete Data'
@VDM.viewType: #CONSUMPTION

define view entity ZMM_C_PURCHASE_ORDER_COMPLETE
  as select from ZMM_I_PURCHASE_ORDER as Header
    inner join ZMM_I_PURCHASE_ORDER_ITEM as Item
      on Header.PurchaseOrder = Item.PurchaseOrder
    left outer join ZMM_I_VENDOR as Vendor
      on Header.Vendor = Vendor.Vendor
{
  key Header.PurchaseOrder,
  key Item.PurchaseOrderItem,
      Header.CompanyCode,
      Header.DocumentDate,
      Header.Vendor,
      Vendor.VendorName,
      Header.PurchasingOrganization,
      Header.PurchasingGroup,
      Item.Material,
      Item.Plant,
      Item.OrderQuantity,
      Item.OrderUnit,
      Item.NetPrice,
      Item.NetAmount,
      Header.Currency
}
```

## Common Annotations Reference

- `@AbapCatalog.sqlViewName`: SQL view name (max 16 chars, **only for legacy `define view`**, not needed with `define view entity`)
- `@AbapCatalog.compiler.compareFilter`: Enable filter optimization (**deprecated with `define view entity`**)
- `@AbapCatalog.preserveKey`: Preserve key fields (**deprecated with `define view entity`**)
- `@AccessControl.authorizationCheck`: Authorization check behavior
  - `#NOT_REQUIRED`: No authorization check
  - `#CHECK`: Use authorization checks (requires DCL)
  - `#NOT_ALLOWED`: Prevent direct access
- `@EndUserText.label`: User-friendly description
- `@VDM.viewType`: Virtual Data Model type
  - `#BASIC`: Interface view (I)
  - `#COMPOSITE`: Composite view
  - `#CONSUMPTION`: Consumption view (C)
  - `#TRANSACTIONAL`: Transactional view (R)
- `@ObjectModel.representativeKey`: Technical key field
- `@ObjectModel.usageType`: Usage classification
- `@Analytics.dataCategory`: Analytics usage
  - `#DIMENSION`: Dimension data
  - `#FACT`: Fact/transactional data
  - `#CUBE`: Analytical cube

## Best Practices

1. **Prefer `define view entity` over `define view`**: Modern syntax, cleaner code, no SQL view name needed.
2. **Always use meaningful annotations**: They provide metadata for the framework and improve discoverability.
3. **Follow naming conventions strictly**: Use the appropriate prefix (I/C/R) based on the view type.
4. **Use associations instead of joins when possible**: They provide better performance and flexibility.
5. **Keep CDS views focused**: Each view should have a clear, single purpose.
6. **Document complex logic**: Use comments to explain non-obvious calculations or conditions.
7. **Test thoroughly**: Always test your CDS views with real data after activation.
8. **Consider performance**: Be mindful of joins, aggregations, and data volume.
9. **Use parameterized views**: For flexible, reusable views that can filter data dynamically.

---

*This skill describes the file-system based workflow for creating and modifying ABAP CDS views using VS Code and the ABAP FS Remote extension.*
