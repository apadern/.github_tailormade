---
name: abap_bapi
description: 'Skill for finding and using ABAP BAPI (Business Application Programming Interface) definitions and code templates.'
---

## Purpose

- Provide guidance for finding BAPI definitions and generating proper BAPI calls in ABAP code.
- Access comprehensive BAPI templates from a centralized reference file organized alphabetically.

## Critical Rules

- **Use bapis_index.json first**: Always search for BAPIs in the index file before accessing BAPIS.md
- **IMPORTANT**: Since files are in the ABAP virtual filesystem (adt://), tools like `grep_search` DO NOT WORK. Always use `read_file` directly.
- BAPIs are standard SAP function modules - always call them with `CALL FUNCTION`.
- Always commit changes with `COMMIT WORK` after modifying BAPIs (unless explicitly using test mode).
- Check the `RETURN` parameter (typically table of type BAPIRET2) for error handling.

## BAPI Reference Files Location

The BAPI reference files are stored in:

```
.github/skills/abap_bapi/examples/bapis_index.json  (INDEX - Search here first!)
.github/skills/abap_bapi/examples/BAPIS.md          (Full definitions)
```

**Full ADT URI format**:
```
adt://[SYSTEM_NAME]/.github/skills/abap_bapi/examples/bapis_index.json
adt://[SYSTEM_NAME]/.github/skills/abap_bapi/examples/BAPIS.md
```

**Note**: Replace `[SYSTEM_NAME]` with your actual ABAP system name (e.g., `laboratorio_s4b_150`, `S4HANA_DEV`, etc.). The system name can be found in any adt:// URI in your workspace.

## Index Structure (bapis_index.json)

The index is a JSON array with entries like:
```json
{
  "name": "BAPI_USER_CREATE",
  "start_line": 12345,
  "end_line": 12380,
  "module": "BC-SEC (Security)",
  "description_es": "Crear usuario",
  "target_es": "Usuario SAP"
}
```

- **name**: BAPI function module name
- **start_line**: Line where BAPI template starts in BAPIS.md
- **end_line**: Line where BAPI template ends in BAPIS.md
- **module**: SAP module
- **description_es**: Spanish description
- **target_es**: Target object in Spanish

## Workflow to Use a BAPI

**Prerequisites**: Determine your ABAP system name from any adt:// URI in your workspace. For example, from `adt://laboratorio_s4b_150/...` the system name is `laboratorio_s4b_150`.

### 1. Search BAPI in the Index (bapis_index.json)

**CRITICAL FIRST STEP**: Always search the index file first. It's a JSON array with all available BAPIs.

**Step 1.1**: Read the entire index file (it's a JSON, much smaller than BAPIS.md):

```
read_file(
  filePath: "adt://[SYSTEM_NAME]/.github/skills/abap_bapi/examples/bapis_index.json",
  startLine: 1,
  endLine: 50000  // Read full file
)
```

**Step 1.2**: Parse the JSON and search for your BAPI by name. For example, to find "BAPI_USER_CREATE":
- Parse the JSON array
- Find the object where `"name": "BAPI_USER_CREATE"`
- Extract the `start_line` and `end_line` values

**Example search logic**:
```
If searching for "BAPI_PO_CREATE":
  1. Read bapis_index.json
  2. Search for object with "name": "BAPI_PO_CREATE"
  3. Found: {
       "name": "BAPI_PO_CREATE",
       "start_line": 15230,
       "end_line": 15298,
       ...
     }
  4. Note: start_line=15230, end_line=15298
```

**If BAPI NOT found in index**: 
- The BAPI might not be in the reference file
- Try searching SAP system directly (transaction SE37)
- Check if it's a custom function module (Z* or Y*)

### 2. Read the BAPI Template from BAPIS.md

Once you have `start_line` and `end_line` from the index, read the exact section from BAPIS.md:

```
read_file(
  filePath: "adt://[SYSTEM_NAME]/.github/skills/abap_bapi/examples/BAPIS.md",
  startLine: <start_line_from_index>,
  endLine: <end_line_from_index>
)
```

**Example**:
```
read_file(
  filePath: "adt://laboratorio_s4b_150/.github/skills/abap_bapi/examples/BAPIS.md",
  startLine: 15230,
  endLine: 15298
)
```

**Note**: This gives you the EXACT template for the BAPI without needing to search through thousands of lines.

### 3. Implement the BAPI Call

Based on the template found, implement the BAPI with proper:
- Parameter declarations (using correct data types)
- CALL FUNCTION statement
- Error handling (check RETURN table)
- COMMIT WORK (if needed)

### 4. Standard BAPI Implementation Pattern

```abap
" Declare parameters
DATA: lt_return TYPE STANDARD TABLE OF bapiret2,
      ls_return TYPE bapiret2.

" Declare input/output structures
DATA: ls_input  TYPE <bapi_input_structure>,
      ls_output TYPE <bapi_output_structure>.

" Populate input data
ls_input-field1 = 'value1'.
ls_input-field2 = 'value2'.

" Call the BAPI
CALL FUNCTION '<BAPI_NAME>'
  EXPORTING
    input_parameter  = ls_input
  IMPORTING
    output_parameter = ls_output
  TABLES
    return           = lt_return.

" Check for errors
LOOP AT lt_return INTO ls_return WHERE type CA 'EA'.
  " Handle error
  MESSAGE ls_return-message TYPE ls_return-type.
ENDLOOP.

" Commit if successful
IF sy-subrc = 0.
  CALL FUNCTION 'BAPI_TRANSACTION_COMMIT'
    EXPORTING
      wait = 'X'.
ENDIF.
```

## BAPI Template Structure in BAPIS.md

Each BAPI entry follows this format:

```markdown
### Example ABAP code template for BAPI <BAPI_NAME>. :

*DATA PARAMETER1 TYPE <TYPE>.
*DATA PARAMETER2 TYPE <TYPE>.
*DATA RETURN     TYPE STANDARD TABLE OF BAPIRET2.

CALL FUNCTION '<BAPI_NAME>'
  EXPORTING
    parameter1 = parameter1
* IMPORTING
*   PARAMETER2 = PARAMETER2
* TABLES
*   RETURN     = RETURN
          .
```

**Notes:**
- Commented lines (with `*`) indicate optional parameters
- Active lines are mandatory/commonly used parameters
- Data type declarations are provided for reference

## Common BAPI Categories

The reference files contain BAPIs for various SAP modules. Here are examples of common ones:

- **User Management**: BAPI_USER_*, BAPI_IDENTITY_*
- **Material Management**: BAPI_MATERIAL_*
- **Sales & Distribution**: BAPI_SALESORDER_*, BAPI_CUSTOMER_*
- **Financial Accounting**: BAPI_ACC_*, BAPI_COSTCENTER_*
- **Purchase Ordering**: BAPI_PO_*
- **Production Planning**: BAPI_PRODORD_*
- **Asset Management**: BAPI_ASSET_*
- **HR/Payroll**: BAPI_EMPLOYEE_*, BAPI_PAYROLL_*

**Important**: When searching for a BAPI category:
1. Read bapis_index.json completely
2. Search for BAPIs starting with the prefix (e.g., "BAPI_PO" for purchase orders)
3. The index includes `module`, `description_es`, and `target_es` fields to help identify the right BAPI
4. Use the `start_line` and `end_line` to read the exact template

## Step-by-Step Example Workflow

**Scenario**: You need to create a purchase order using BAPI_PO_CREATE1

**Complete workflow**:

```
Step 1: Read the index
--------
Tool: read_file
Path: adt://laboratorio_s4b_150/.github/skills/abap_bapi/examples/bapis_index.json
Lines: 1 to 50000

Step 2: Search in the returned JSON
--------
Find object where: name === "BAPI_PO_CREATE1"
Result example:
{
  "name": "BAPI_PO_CREATE1",
  "start_line": 21045,
  "end_line": 21134,
  "module": "MM-PUR (Purchasing)",
  "description_es": "Crear pedido",
  "target_es": "Purchase Order"
}

Step 3: Read the BAPI template
--------
Tool: read_file
Path: adt://laboratorio_s4b_150/.github/skills/abap_bapi/examples/BAPIS.md
Lines: 21045 to 21134

Step 4: Analyze the template
--------
Review the CALL FUNCTION structure:
- EXPORTING parameters (inputs)
- IMPORTING parameters (outputs)
- TABLES parameters (usually RETURN table)
- Data types needed

Step 5: Implement in your ABAP code
--------
Copy and adapt the template with:
- Proper data declarations
- Error handling (check RETURN table)
- COMMIT or ROLLBACK
```

## Best Practices

**0. ALWAYS use bapis_index.json first**: 
   - Never try to manually search through BAPIS.md
   - The index provides instant lookup with exact line numbers
   - This saves time and avoids reading thousands of unnecessary lines

1. **Always handle errors**: Check the RETURN table for messages with type 'E' (Error) or 'A' (Abort).

2. **Use COMMIT or ROLLBACK**: 
   ```abap
   " Commit on success
   CALL FUNCTION 'BAPI_TRANSACTION_COMMIT'
     EXPORTING
       wait = 'X'.
   
   " Rollback on error
   CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.
   ```

3. **Test mode**: Many BAPIs support a TESTRUN parameter for validation without changing data.

4. **Use proper data types**: Always use the data types specified in the BAPI template (e.g., BAPIRET2 for return messages).

5. **Authorization checks**: BAPIs perform standard SAP authorization checks - ensure the user has proper permissions.

## Example: Using BAPI_USER_CREATE

**Step 1**: Search in bapis_index.json
```
1. Read the index file:
   read_file("adt://laboratorio_s4b_150/.github/skills/abap_bapi/examples/bapis_index.json", 1, 50000)
   
2. Search for "BAPI_USER_CREATE" in the JSON array

3. Find the entry (example):
   {
     "name": "BAPI_USER_CREATE",
     "start_line": 28456,
     "end_line": 28512,
     "module": "BC-SEC (Security)",
     "description_es": "Crear usuario",
     "target_es": "Usuario SAP"
   }
```

**Step 2**: Read the exact template from BAPIS.md
```
read_file("adt://laboratorio_s4b_150/.github/skills/abap_bapi/examples/BAPIS.md", 28456, 28512)
```

**Step 3**: Implement with error handling
```abap
DATA: lt_return  TYPE STANDARD TABLE OF bapiret2,
      ls_address TYPE bapiaddr3,
      ls_password TYPE bapipwd,
      lv_username TYPE bapibname-bapibname.

" Populate user data
ls_address-firstname = 'John'.
ls_address-lastname = 'Doe'.
ls_address-e_mail = 'john.doe@example.com'.

" Set initial password
ls_password-bapipwd = 'InitialPass123'.

" Call BAPI to create user
CALL FUNCTION 'BAPI_USER_CREATE'
  EXPORTING
    username = 'JDOE'
    address  = ls_address
    password = ls_password
  TABLES
    return   = lt_return.

" Check for errors
READ TABLE lt_return WITH KEY type = 'E' TRANSPORTING NO FIELDS.
IF sy-subrc = 0.
  " Error occurred
  LOOP AT lt_return INTO DATA(ls_return) WHERE type CA 'EA'.
    WRITE: / ls_return-message.
  ENDLOOP.
  " Rollback
  CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.
ELSE.
  " Success - commit
  CALL FUNCTION 'BAPI_TRANSACTION_COMMIT'
    EXPORTING
      wait = 'X'.
  WRITE: / 'User created successfully'.
ENDIF.
```

## Troubleshooting

### BAPI Not Found in bapis_index.json
- Check spelling (BAPIs are case-sensitive, usually all uppercase)
- Verify you're using the exact function module name (e.g., "BAPI_USER_CREATE" not "BAPI_CREATE_USER")
- The BAPI might not be in the reference files - search SAP system directly using transaction SE37
- Consider if it's a custom function module (Z* or Y*) rather than standard BAPI
- Remember: The index contains thousands of BAPIs, but not every SAP function module

### Index File Read Error
- Verify the system name in the adt:// URI is correct
- Ensure the full path is: `adt://[SYSTEM_NAME]/.github/skills/abap_bapi/examples/bapis_index.json`
- The file might be very large (30,000+ lines) - use a high endLine value (e.g., 50,000)

### Invalid start_line/end_line Values
- Always use the exact values from the JSON index
- Don't add or subtract from these values
- If the template looks incomplete, the index might be outdated

### BAPI Template Not in BAPIS.md
- This should NOT happen if you use start_line and end_line from the index correctly
- If it does happen, the index might be out of sync with BAPIS.md
- Try reading a slightly larger range (e.g., add ±10 lines)
- Report the issue so the index can be regenerated

### Parameter Type Errors
- Always use the exact data types from the BAPI signature
- Use `TYPE` not `LIKE` for parameter declarations
- Check if parameter is mandatory (not commented in template)

### RETURN Table Shows Errors
- Type 'E' = Error (operation failed)
- Type 'W' = Warning (operation succeeded with warnings)
- Type 'I' = Information
- Type 'S' = Success
- Type 'A' = Abort (critical error)

## Additional Resources

- **Transaction SE37**: Function Builder - view complete BAPI documentation
- **Transaction BAPI**: BAPI Explorer - browse BAPIs by Business Objects
- **BAPI_TRANSACTION_COMMIT**: Always call after successful BAPI execution
- **BAPI_TRANSACTION_ROLLBACK**: Call on error to undo changes
