---
description: 'ABAP developer Agent'
tools: ['vscode', 'read', 'agent', 'edit', 'search/changes', 'search/fileSearch', 'search/listDirectory', 'search/searchResults', 'search/textSearch', 'search/usages', 'web', 'github.vscode-pull-request-github/issue_fetch', 'github.vscode-pull-request-github/suggest-fix', 'github.vscode-pull-request-github/searchSyntax', 'github.vscode-pull-request-github/doSearch', 'github.vscode-pull-request-github/renderIssues', 'github.vscode-pull-request-github/activePullRequest', 'github.vscode-pull-request-github/openPullRequest', 'nttdata.vscode-abap-remote-fs/abap_unit', 'nttdata.vscode-abap-remote-fs/abap_activate', 'nttdata.vscode-abap-remote-fs/abap_search', 'nttdata.vscode-abap-remote-fs/abap_lock', 'nttdata.vscode-abap-remote-fs/abap_unlock', 'nttdata.vscode-abap-remote-fs/abap_transportinfo', 'nttdata.vscode-abap-remote-fs/abap_createobject', 'nttdata.vscode-abap-remote-fs/abap_gettable', 'nttdata.vscode-abap-remote-fs/abap_getstructure', 'nttdata.vscode-abap-remote-fs/abap_gettypeinfo', 'nttdata.vscode-abap-remote-fs/abap_getsourcecode', 'nttdata.vscode-abap-remote-fs/abap_syntaxcheckcode', 'nttdata.vscode-abap-remote-fs/abap_usagereferences', 'nttdata.vscode-abap-remote-fs/abap_openobject', 'nttdata.vscode-abap-remote-fs/abap_atccheck', 'nttdata.vscode-abap-remote-fs/abap_getsapuser', 'todo']
---
# ABAP FS Remote - AI Agent Instructions

This document contains instructions and workflows for AI agents working with ABAP objects in VS Code using the ABAP FS Remote extension.

## 🚨 FIRST PREMISE - ABAP TOOLS CHECK

**BEFORE STARTING ANY TASK, YOU MUST VERIFY THAT ABAP TOOLS ARE AVAILABLE:**

1. **Load ABAP tools** using `tool_search_tool_regex` with the pattern `abap_activate|abap_search`
   - ABAP tools are **deferred tools** that must be loaded before they can be used
   - The `tool_search_tool_regex` call will return the available ABAP tools and make them immediately usable
   - Once loaded in a session, the tools remain available for subsequent calls

2. **If the search returns ABAP tools**: Proceed with the ABAP development workflow immediately

3. **If no tools are returned on first attempt**:
   - ⚠️ **DO NOT give up immediately** - Try alternative search patterns:
     - Pattern: `abap_` (matches all ABAP tools)
     - Pattern: `activate` or `search` (individual tool names)
   - Try searching **at least 2-3 times** with different patterns before concluding tools are unavailable
   
4. **Only if ALL search attempts fail**:
   - ❌ **STOP EXECUTION**
   - ⚠️ **Notify the user**: "ABAP tools are not available in this environment. These tools are required for the ABAP Developer agent. Please ensure the extension is installed and enabled."
   - 🛑 **DO NOT proceed** with any ABAP-related tasks

**CRITICAL REMINDERS:**
- ABAP tools are deferred and MUST be loaded via `tool_search_tool_regex` before use
- Once a tool appears in search results, it is immediately available to call
- Be persistent - try multiple search patterns before declaring tools unavailable
- This check is MANDATORY at the start of every ABAP work session

This folder is a virtual filesystem used by the ABAP Filesystem extension to allow editing code stored on a server.
CLI tools like grep,ls,find find and others can't operate on these files
most standard search tool won't work either
You're still able to read and write files normally, and to navigate the filesystem, but should do it sparingly as it's rather slow

**CRITICAL** always use tool abap_search to search ABAP code, never use standard tools that operate on the filesystem, like grep, fileSearch or lietDirectory in this folder.

## CRITICAL Tool Rules

### ✅ ALWAYS USE These Tools for ABAP Development workflow:
- **abap_createobject**: Create new ABAP objects (only when creating, not editing)
- **abap_search**: Search for ABAP objects
- **abap_lock**: Lock objects before editing (REQUIRED by SAP)
- **read_file**: Read ABAP source code
- **replace_string_in_file**: Modify ABAP source code
- **abap_syntaxcheckcode**: Validate syntax before activation
- **abap_activate**: Activate objects to make changes effective
- **abap_unlock**: Unlock objects after editing (REQUIRED by SAP)

### ❌ NEVER USE These Tools for ABAP Development workflow:
- **abap_setsourcecode**: Deprecated, use replace_string_in_file instead
- **abap_getsourcecode**: Deprecated, use read_file instead

## Available Skills

When working with specific ABAP object types, specialized skills are available to provide detailed guidance:

- **abap_program_creator**: Use this skill when creating or modifying ABAP programs (PROG/P). This skill provides best practices and step-by-step workflows specific to programs.
- **abap_cds_creator**: Use this skill when creating or modifying ABAP CDS views (DDLS/DF). This skill provides the step-by-step process for creating and configuring CDS views with proper annotations and syntax.
- **abap_data_element_creator**: Use this skill when creating ABAP Data Elements (DTEL/DE). This skill provides the step-by-step process for creating and configuring data elements with proper XML structure.
- **abap_bapi**: Use this skill when you need to find and implement BAPI (Business Application Programming Interface) calls. This skill provides access to BAPI templates and best practices for calling standard SAP function modules.
- **abap_atc_corrector**: Use this skill when fixing ABAP ATC (Test Cockpit) findings. This skill provides systematic instructions to automatically correct ATC issues based on priority levels, following ABAP best practices and file-system based workflow.
- **abap_restful**: Use this skill when creating RESTful ABAP applications using RAP (RESTful Application Programming Model). This skill provides comprehensive guidance for creating all necessary RAP artifacts including database tables, CDS views, behavior definitions, behavior implementations, service definitions, and service bindings for OData V2/V4 services.

Invoke skills by using the @skill syntax or by consulting the `.github/skills/` directory when you need specialized guidance for a specific task.

## MANDATORY: Object Activation

**IMPORTANT — OBJECTS MUST ALWAYS BE ACTIVATED:**

- After creating or modifying an object, **the task is NOT complete until the object has been successfully activated** using `abap_activate`.
- If activation fails, **you MUST** fix the errors following the defined workflow: run `abap_syntaxcheckcode`, apply fixes with `replace_string_in_file` (or create new versions as appropriate), re-validate, and retry `abap_activate` until activation succeeds.
- Do not mark a creation or modification as finished without confirmation of successful activation.
- If you encounter activation errors you cannot resolve, notify the user and document the steps taken and the error messages before proceeding.

This rule is critical: it ensures SAP system integrity and prevents leaving objects in an inconsistent state.

## ABAP Development Workflow

Use this unified workflow for both creating new objects and editing existing ones.

### Quick Reference

```
For NEW objects:
1. Create Object    → abap_createobject (create the object)
2. Search Object    → abap_search (find it and get URIs)
3. Read Source      → read_file (read initial content)
4. Lock Object      → abap_lock (REQUIRED: lock before editing)
5. Modify Code      → replace_string_in_file (edit the code)
6. Syntax Check     → abap_syntaxcheckcode (validate)
7. Fix Errors       → Repeat steps 5-6 if needed
8. Activate         → abap_activate (make it effective)
9. Unlock Object    → abap_unlock (REQUIRED: release the lock)

For EXISTING objects:
1. Search Object    → abap_search (find it and get URIs)
2. Read Source      → read_file (read current content)
3. Lock Object      → abap_lock (REQUIRED: lock before editing)
4. Modify Code      → replace_string_in_file (edit the code)
5. Syntax Check     → abap_syntaxcheckcode (validate)
6. Fix Errors       → Repeat steps 4-5 if needed
7. Activate         → abap_activate (make it effective)
8. Unlock Object    → abap_unlock (REQUIRED: release the lock)
```

### Detailed Step-by-Step Instructions

#### Step 0: Create Object (ONLY for new objects)
```
Tool: abap_createobject
When: Only when creating a NEW object, skip this step for existing objects
Purpose: Create a new ABAP object in the SAP system
Input: objtype, name, description, parentName (package), url
Output: Object created confirmation with URI path
Example: Create a program, class, function group, etc.
Note: After creation, proceed to Step 1 to find and edit it
```

#### Step 1: Find the Object
```
Tool: abap_search
Purpose: Locate the ABAP object and get its ADT URI
Input: Object name, type, or search pattern
Output: Complete ADT URI (e.g., adt://system/sap/bc/adt/programs/programs/z_my_program)
        Also returns links array with "source" link containing objSourceUrl
Important: 
  - The main URI is for read_file: adt://system/sap/bc/adt/...
  - The "source" link is for abap_syntaxcheckcode: /sap/bc/adt/.../source/main
  - Save both URIs for use in subsequent steps
```

#### Step 3: Read Initial Content
```
Tool: read_file
Purpose: Read the automatically generated initial program content
Input: File path from the ADT URI (Step 2)
Output: Initial ABAP source code generated by the system
Important: Use this as the base for your modifications
```

#### Step 4: Lock the Object
```
Tool: abap_lock
Purpose: Lock the object for editing (REQUIRED by SAP)
Input: url (the ADT URI from Step 1)
Output: Lock handle and status
IMPORTANT: This step is MANDATORY before any modifications
Note: Objects must be locked to prevent concurrent editing conflicts
Warning: If you skip this step, changes may fail or cause data inconsistency
```

#### Step 5: Modify the Code
```
Method: Direct file editing with replace_string_in_file
Purpose: Apply the required changes to the source code
Process: Modify the code read in Step 3 using file editing tools
Approach: Make precise, targeted modifications directly in the file
CRITICAL: DO NOT use abap_setsourcecode in this workflow - use replace_string_in_file
Tools: replace_string_in_file, multi_replace_string_in_file
```
Tools: replace_string_in_file, multi_replace_string_in_file
```

#### Step 6: Check Syntax
```
Tool: abap_syntaxcheckcode
Purpose: Validate ABAP syntax before activation
Input: 
  - code: The modified ABAP source code
  - url: The ADT URI of the object (e.g., adt://system/sap/bc/adt/oo/classes/zcl_example)
  - objSourceUrl: The source path (e.g., /sap/bc/adt/oo/classes/zcl_example/source/main)
  
Important: The objSourceUrl must be the path portion only (starting with /sap/bc/adt/...), not the full adt:// URI
Note: You can get the objSourceUrl from the "source" link in the abap_search results
Output: Syntax errors/warnings or success confirmation
Important: Always check syntax before activating
```

#### Step 7: Error Correction Loop
```
If syntax check returns errors:
- Return to Step 5 (modify code)
- Fix the reported syntax issues
- Repeat Step 6 (syntax check)
- Continue until syntax is clean
```

#### Step 8: Activate Object
```
Tool: abap_activate
Purpose: Activate the modified ABAP object to make it executable
Input: Object URI from Step 1
Result: Object activated and ready for use
Important: This makes your changes effective in the system
```

#### Step 9: Unlock the Object
```
Tool: abap_unlock
Purpose: Release the lock on the object (REQUIRED by SAP)
Input: url (the ADT URI from Step 1), immediate (optional, default true)
Output: Unlock status
IMPORTANT: Always unlock objects after completing modifications
Note: Failure to unlock will block other users from editing
Best Practice: Use this in a finally block or always execute even if errors occur
```

### Important Notes

- **Creating vs Editing**: Only difference is Step 0 (abap_createobject) for new objects
- **Always Lock/Unlock**: REQUIRED by SAP to prevent concurrent editing conflicts
- **Lock Before Edit**: Always call abap_lock BEFORE making any modifications
- **Unlock After Done**: Always call abap_unlock AFTER activation, even if errors occur
- **Always use replace_string_in_file**: Never use abap_setsourcecode for code modifications
- **Syntax First**: Always check syntax before activation to avoid server-side errors
- **Error Handling**: If any step fails, review the error and retry with corrections
- **File System Editing**: All modifications go through VS Code's file system, not server APIs
- **⚠️ NEVER USE**: abap_setsourcecode or abap_getsourcecode for this workflow

### Additional Workflows

#### VS Code Editor Workflow (Interactive)
For interactive editing with user involvement:
```
1. abap_search → 2. abap_openobject → 3. Edit in VS Code → 4. abap_syntaxcheckcode → 5. User saves (Ctrl+S) → 6. abap_activate
```
Note: This workflow requires manual user save action.

#### Read-Only Operations
For read-only operations:
```
1. abap_search → 2. read_file
```

### Error Handling

- **Creation Errors** (new objects only): Verify object type, naming conventions, and package existence
- **Syntax Errors**: Use the error correction loop (modify code → syntax check → repeat until clean)
- **Activation Errors**: Check for unresolved references or dependencies
- **Object Not Found**: Retry search or verify object name and type are correct
- **Read Errors**: Ensure the ADT URI is correct and object is accessible
- **Permission Errors**: Verify you have authorization to modify the object or package

## Available Tools:

### ALWAYS USE These Tools:
- **abap_createobject**: Create new ABAP objects (classes, programs, function groups, etc.)
- **abap_search**: Search for ABAP objects (classes, programs, tables, etc.)
- **read_file**: Read file contents from VS Code file system
- **replace_string_in_file**: Edit ABAP source code by replacing text in files
- **abap_syntaxcheckcode**: Validate ABAP code for syntax errors
- **abap_activate**: Activate objects after changes (makes changes effective). Automatically handles related objects: if activation fails due to dependencies, it finds and activates all related inactive objects (siblings with same parent) together. For includes, uses the main program for activation.
- **abap_openobject**: Open ABAP objects in VS Code editor (for interactive editing)
- **abap_unit**: Run ABAP unit tests
- **abap_transportinfo**: Get transport information for recording changes
- **abap_getsapuser**: Get SAP user information from connection configuration (username, client, language)
- **abap_gettable**: Retrieve contents of database tables or CDS views
- **abap_getstructure**: Get complete structure and metadata of ABAP objects
- **abap_gettypeinfo**: Get DDIC type information (tables, structures, data elements)
- **abap_usagereferences**: Find where symbols, methods, or objects are used/referenced

### ⚠️ DEPRECATED - DO NOT USE These Tools:
- **abap_getsourcecode**: ❌ DEPRECATED - Use read_file instead
- **abap_setsourcecode**: ❌ DEPRECATED - Use replace_string_in_file instead

## ABAP Best Practices

### Text Management (CRITICAL)

**❌ NEVER use hardcoded text literals** like `'This is a text'` or `'Esto es un texto'` directly in code.

**✅ ALWAYS use the appropriate text management approach:**

1. **Long Texts or Messages**: Use **Text Symbols**
   ```abap
   " ❌ WRONG:
   WRITE: / 'This is a detailed error message that appears in the output'.
   MESSAGE 'The process has completed successfully' TYPE 'S'.
   
   " ✅ CORRECT - Use text symbols:
   WRITE: / text-001.  " Define text-001 in text elements
   MESSAGE text-msg TYPE 'S'.
   ```

2. **Short Texts (Message Types)**: Use **Constants**
   ```abap
   " ❌ WRONG:
   MESSAGE lv_message TYPE 'E'.
   MESSAGE lv_message TYPE 'S'.
   
   " ✅ CORRECT - Define as constants:
   CONSTANTS:
     lc_msgtype_error   TYPE sy-msgty VALUE 'E',
     lc_msgtype_success TYPE sy-msgty VALUE 'S',
     lc_msgtype_warning TYPE sy-msgty VALUE 'W',
     lc_msgtype_info    TYPE sy-msgty VALUE 'I',    
     lc_abap_true       TYPE abap_bool VALUE abap_true.
   
   MESSAGE lv_message TYPE lc_msgtype_error.
   ```

3. **Single Character Flags**: Use **Constants**
   ```abap
   " ❌ WRONG:
   IF flag = 'X'.
   IF status = 'A'.
   
   " ✅ CORRECT:
   CONSTANTS:     
     lc_status_active TYPE c VALUE 'A'.
   
   IF flag = abap_true.
   IF status = lc_status_active.
   ```

**Rationale:**
- Text symbols enable easy translation to multiple languages
- Constants improve code maintainability and readability
- Centralized text management reduces duplication
- Follows SAP standard development guidelines
- Use abap_true/abap_false for boolean flags instead of 'X' or space

### Database Access (ABAP 7.51+ Modern Syntax)

**✅ ALWAYS use modern ABAP 7.51+ syntax for SELECT statements** with inline declarations and direct target assignments.

```abap
" ❌ WRONG - Old syntax:
DATA: lt_ekko TYPE TABLE OF ekko,
      ls_ekko TYPE ekko.

SELECT * FROM ekko
  INTO TABLE lt_ekko
  WHERE ebeln IN s_ebeln.

SELECT SINGLE * FROM ekko
  INTO CORRESPONDING FIELDS OF ls_ekko
  WHERE ebeln = lv_ebeln.
```

**✅ CORRECT - Modern ABAP 7.51+ syntax:**

```abap
" ✅ Inline declaration with @-escaping for host variables
SELECT * FROM ekko
  WHERE ebeln IN @s_ebeln
  INTO TABLE @DATA(lt_ekko).

" ✅ Single record with inline declaration
SELECT SINGLE * FROM ekko
  WHERE ebeln = @lv_ebeln
  INTO @DATA(ls_ekko).

" ✅ Specific fields with inline declaration
SELECT ebeln, bukrs, bsart
  FROM ekko
  WHERE ebeln IN @s_ebeln
  INTO TABLE @DATA(lt_purchase_orders).

" ✅ JOIN with modern syntax
SELECT p~ebeln, p~bukrs, i~ebelp, i~matnr
  FROM ekko AS p
  INNER JOIN ekpo AS i ON p~ebeln = i~ebeln
  WHERE p~ebeln IN @s_ebeln
  INTO TABLE @DATA(lt_po_items).

" ✅ Aggregate functions
SELECT ebeln, COUNT(*) AS item_count
  FROM ekpo
  WHERE ebeln IN @s_ebeln
  GROUP BY ebeln
  INTO TABLE @DATA(lt_counts).
```

**Key Modern Syntax Rules:**
1. **Use `@` prefix** for all host variables (parameters, variables, constants)
2. **Use inline declarations** with `@DATA(...)` directly in the INTO clause
3. **Avoid INTO TABLE** - use `INTO TABLE @DATA(...)` or `INTO @DATA(...)` for single records
4. **Use field aliases** with `AS` when needed for clarity
5. **Use ABAP CDS views** when available instead of direct database tables
6. **Always specify fields** instead of `SELECT *` when possible for better performance

**Benefits:**
- More concise and readable code
- Reduced variable declarations
- Better performance (compiler optimizations)
- Follows modern ABAP standards (7.51+)
- Required for S/4HANA compatibility

## ABAP Naming Conventions

### General Rules

- **Programs**: Start with `Z` or `Y` (customer namespace), followed by descriptive name (e.g., `ZTEST_VSTUDIO`, `ZMO_DOSSIER_SANITY_CHECKS`).
- **Classes**: Start with `ZCL_` or `YCL_` for global classes (e.g., `ZCL_ALV_DISPLAY`, `ZCL_PURCHASE_ORDER`).
- **Interfaces**: Start with `ZIF_` or `YIF_` (e.g., `ZIF_SANITY_CHECK`).
- **Function Modules**: Start with `Z_` or `Y_` (e.g., `Z_GET_PURCHASE_ORDERS`).
- **Includes**: Use descriptive suffixes like `_TOP` (declarations), `_F01` (forms), `_O01` (PBO modules), `_I01` (PAI modules), `_CL01` (Local classes).
- **CDS Views**: Names must start with `ZXX_Y_Name`, where `XX` is the application/module (for example `FI`, `SD`, `MM`) and `Y` can be `I` for base CDS view entities, `C` for projection/consumption views, and `R` for root views (for example `ZSD_I_Vendors`, `ZFI_I_Accounting`, `ZSD_C_Vendors`, `ZFI_R_AccountingRoot`).

- **Variables**: Use Hungarian notation:
  - `lv_` - Local variable (e.g., `lv_ebeln`, `lv_count`)
  - `gv_` - Global variable (e.g., `gv_bukrs`)
  - `lt_` - Local internal table (e.g., `lt_ekko`, `lt_alv_data`)
  - `gt_` - Global internal table (e.g., `gt_dossier`)
  - `ls_` - Local structure (e.g., `ls_ekpo`, `ls_fieldcat`)
  - `gs_` - Global structure (e.g., `gs_layout`)
  - `lr_` - Local reference (e.g., `lr_alv`, `lr_data`)
  - `gr_` - Global reference (e.g., `gr_container`)
  - `lo_` - Local object (e.g., `lo_dossier`, `lo_alv`)
  - `go_` - Global object (e.g., `go_salv_table`)
  - `gty_t_` - Global table type (e.g., `gty_t_ekpo`)
  - `gty_s_` - Global structure type (e.g., `gty_s_ekpo`)
  - `lty_t_` - Local table type (e.g., `lty_t_data`)
  - `lty_s_` - Local structure type (e.g., `lty_s_data`)

- **Constants**: Start with `lc_` or `gc_` (e.g., `lc_x TYPE c VALUE 'X'`, `gc_max_rows TYPE i VALUE 1000`).
- **Parameters**: Start with `p_` or `pa_` (e.g., `p_bukrs`, `pa_dosid`).
- **Buttons**: Start with `btn_` and should be 8 character max (e.g., `btn_exec`, `btn_reproc`) and use by default 25 character long. 
- **Select-Options**: Start with `s_` (e.g., `s_ebeln`, `s_bukrs`).
- **Local Class Methods**: Use descriptive names without prefix (e.g., `modify_screen`, `data_selection`, `process`).

---

*This document describes the file-system based workflow for AI agents editing ABAP objects. Both workflows use direct file editing with replace_string_in_file.*
