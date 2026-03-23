---
name: abap_program_creator
description: 'Skill for creating and modifying ABAP programs with file-system based workflow and best practices.'
---

Purpose

- Provide concise, actionable instructions to create and modify ABAP programs using the modern file-system based workflow.

Critical rules (File-System Workflow)

- Always use file-system based tools: `abap_createobject`, `abap_search`, `read_file`, `replace_string_in_file`, `abap_syntaxcheckcode`, `abap_activate`.
- Activation is mandatory: an object must be activated (`abap_activate`) to be usable.
- Use the correct object type when creating objects (programs -> `PROG/P`, includes -> `PROG/I`).
- **DO NOT use deprecated tools**: `abap_getsourcecode`, `abap_setsourcecode`.
- **ALWAYS use lock/unlock**: `abap_lock` before editing, `abap_unlock` after activation (REQUIRED by SAP).

Workflow to create or modify an ABAP program

### For NEW objects with INCLUDES (OBLIGAORY):
1. Create Main Program: `abap_createobject` (objtype=PROG/P, name, description, parentName).
2. Create Include Programs: `abap_createobject` (objtype=PROG/I) for each section:
   - ZPROGRAM_NAME_TOP (Global declarations)
   - ZPROGRAM_NAME_SEL (Selection screen)
   - ZPROGRAM_NAME_CLS (Local class definitions)
   - ZPROGRAM_NAME_EVT (Event blocks)
3. Search Objects: `abap_search` (find main program and includes, get ADT URIs + objSourceUrl).
4. Read Source: `read_file` (read initial content from ADT URIs).
5. Modify Main Program: `replace_string_in_file` (add INCLUDE statements).
6. Modify Each Include: `replace_string_in_file` (add specific code for each section).
7. Syntax Check: `abap_syntaxcheckcode` (check main program and each include).
8. Fix Errors: Repeat steps 6-7 if needed.
9. Activate All: `abap_activate` (activate main program and all includes).
10. Run unit tests (if available): `abap_unit`.

### For EXISTING objects:
1. Search Object: `abap_search` (find it and get ADT URI + objSourceUrl).
2. Read Source: `read_file` (read current content from ADT URI).
3. Modify Code: `replace_string_in_file` (edit the code directly in file).
4. Syntax Check: `abap_syntaxcheckcode` (code=<source>, url=<URI>, objSourceUrl=<path>).
5. Fix Errors: Repeat steps 3-4 if needed.
6. Activate: `abap_activate` (object=<URI>).
7. Run unit tests (if available): `abap_unit`.

Program-specific developer workflow and best practices

- Create a clear program header with description and package.
- Use `SELECT-OPTIONS` for ranges, `PARAMETERS` for single inputs.
- Use modern ABAP SQL with `@` host variables and inline `DATA()` declarations.
- Prefer `CL_SALV_TABLE` for simple ALV; use `CL_GUI_ALV_GRID` only for complex interactive grids.
- Keep changes small and run `abap_syntaxcheckcode` before activation.

Program structure guideline (OBLIGATORY for new programs)

**Best Practice for Automated Creation:**
- Put local class definitions in dedicated section with clear comments
- Keep `START-OF-SELECTION` / `END-OF-SELECTION` minimal and delegate to class methods
- Use clear section markers to separate concerns
- Example high-level layout:
    - Header / metadata
    - SECTION: Global Declarations (TOP)
    - SECTION: Selection Screen (SEL)
    - SECTION: Local Class Definition and Implementation (CLS)
    - SECTION: Event Blocks (EVT)

Naming conventions (programs)

- Program names should start with `Z` or `Y` and be descriptive (e.g., `ZMY_APP_REPORT`).

Key tool usage summary (quick reference)

- `abap_createobject`: create new ABAP objects (use objtype=PROG/P for programs).
- `abap_search`: discover object URIs and objSourceUrl.
- `read_file`: read source code from file system (use ADT URI).
- `replace_string_in_file`: modify ABAP source code in file system.
- `abap_syntaxcheckcode`: validate syntax (requires code, url, objSourceUrl).
- `abap_activate`: activate the object to make changes effective.
- `abap_unit`: run unit tests.
- `abap_transportinfo`: get transport information if needed.

Important Notes

- **File-System Based**: All modifications go through VS Code's file system using `replace_string_in_file`, not server APIs.
- **No Lock/Unlock**: The file-system workflow does not require `abap_lock` or `abap_unlock`.
- **Syntax Check Parameters**: Always include code, url (ADT URI), and objSourceUrl (path from search results).
- **Deprecated Tools**: Never use `abap_getsourcecode` or `abap_setsourcecode`.
- **Locking Required**: Always use `abap_lock` before editing and `abap_unlock` after activation (SAP requirement).
- **Include Programs**: Create separate include programs (PROG/I) for each section (TOP, SEL, CLS, EVT) using `abap_createobject`.
- **Modular Structure**: Organize code with includes for better maintainability: main program contains only INCLUDE statements and each include contains its specific section.
- **Activation**: Each include must be activated individually before activating the main program.
- This skill follows the modern file-system based workflow described in the ABAP Developer Agent instructions.

**Include Naming Convention:**
- `ZPROGRAM_NAME_TOP` - Global Declarations include (PROG/I)
- `ZPROGRAM_NAME_SEL` - Selection Screen include (PROG/I)
- `ZPROGRAM_NAME_CLS` - Local Class Definition and Implementation include (PROG/I)
- `ZPROGRAM_NAME_EVT` - Event Blocks include (PROG/I)
- `ZPROGRAM_NAME_PBO` - PBO Modules (for screen programming if needed)
- `ZPROGRAM_NAME_PAI` - PAI Modules (for screen programming if needed)

### Program Structure

**Recommended Approach: Main Program with Include Programs**

A well-structured ABAP program should have a main program that includes separate include programs for each section:
- 1º Main program with INCLUDE statements
- 2º TOP include: Global Declarations - Tables, types, and global data
- 3º SEL include: Selection Screen - Selection screen parameters
- 4º CLS include: Local Class Definition and Implementation - All class logic
- 5º EVT include: Event Blocks - START-OF-SELECTION, END-OF-SELECTION

```abap
*&---------------------------------------------------------------------*
*& Report ZPROGRAM_NAME
*&---------------------------------------------------------------------*
*& Description: Brief description of what the program does
*&---------------------------------------------------------------------*
REPORT zprogram_name.

INCLUDE zprogram_name_top.    " Global declarations and types
INCLUDE zprogram_name_sel.    " Selection screen
INCLUDE zprogram_name_cls.    " Local class definition and implementation
INCLUDE zprogram_name_evt.    " Event blocks
```

**Include ZPROGRAM_NAME_TOP (PROG/I):**
```abap
*&---------------------------------------------------------------------*
*& Include          ZPROGRAM_NAME_TOP
*&---------------------------------------------------------------------*
*& Global Declarations (TOP)
*&---------------------------------------------------------------------*

*& Tables Declaration
TABLES: ekko.

*& Type Definitions
TYPES: BEGIN OF ty_data,
         field1 TYPE char10,
         field2 TYPE i,
       END OF ty_data.

*& Global Data
DATA: gt_data TYPE STANDARD TABLE OF ty_data.
```

**Include ZPROGRAM_NAME_SEL (PROG/I):**
```abap
*&---------------------------------------------------------------------*
*& Include          ZPROGRAM_NAME_SEL
*&---------------------------------------------------------------------*
*& Selection Screen (SEL)
*&---------------------------------------------------------------------*

SELECTION-SCREEN BEGIN OF BLOCK b1 WITH FRAME TITLE TEXT-001.
  SELECT-OPTIONS: s_ebeln FOR ekko-ebeln OBLIGATORY.
  PARAMETERS: p_test AS CHECKBOX DEFAULT abap_false.
SELECTION-SCREEN END OF BLOCK b1.
```

**Include ZPROGRAM_NAME_CLS (PROG/I):**
```abap
*&---------------------------------------------------------------------*
*& Include          ZPROGRAM_NAME_CLS
*&---------------------------------------------------------------------*
*& Local Class Definition and Implementation (CLS)
*&---------------------------------------------------------------------*

*& Local Class Definition
CLASS lcl_main DEFINITION.
  
  PUBLIC SECTION.
    
    CLASS-METHODS:
      execute,
      display_data,
      validate_input.
  
  PRIVATE SECTION.
    
    CLASS-METHODS:
      fetch_data,
      process_data.

ENDCLASS.

*& Local Class Implementation
CLASS lcl_main IMPLEMENTATION.

  METHOD execute.
    " Main processing logic
    validate_input( ).
    fetch_data( ).
    process_data( ).
    display_data( ).
  ENDMETHOD.

  METHOD validate_input.
    " Input validation logic
  ENDMETHOD.

  METHOD fetch_data.
    " Data retrieval logic
  ENDMETHOD.

  METHOD process_data.
    " Business logic processing
  ENDMETHOD.

  METHOD display_data.
    " ALV or output display logic
  ENDMETHOD.

ENDCLASS.
```

**Include ZPROGRAM_NAME_EVT (PROG/I):**
```abap
*&---------------------------------------------------------------------*
*& Include          ZPROGRAM_NAME_EVT
*&---------------------------------------------------------------------*
*& Event Blocks (EVT)
*&---------------------------------------------------------------------*

START-OF-SELECTION.
  lcl_main=>execute( ).

END-OF-SELECTION.
  " Final processing if needed
```

### Class Structure
Global classes should follow this structure:

```abap
CLASS zcl_class_name DEFINITION
  PUBLIC
  FINAL
  CREATE PRIVATE.

  PUBLIC SECTION.
    " Public methods
    CLASS-METHODS get_instance
      RETURNING VALUE(ro_instance) TYPE REF TO zcl_class_name.
    
    METHODS process_data
      IMPORTING iv_input TYPE string
      RETURNING VALUE(rv_result) TYPE string
      RAISING   cx_static_check.

  PROTECTED SECTION.
    " Protected methods and attributes

  PRIVATE SECTION.
    " Private attributes
    CLASS-DATA go_instance TYPE REF TO zcl_class_name.
    DATA mv_data TYPE string.
    
    " Private methods
    METHODS validate_input
      IMPORTING iv_input TYPE string
      RETURNING VALUE(rv_valid) TYPE abap_bool.
ENDCLASS.

CLASS zcl_class_name IMPLEMENTATION.
  METHOD get_instance.
    IF go_instance IS NOT BOUND.
      CREATE OBJECT go_instance.
    ENDIF.
    ro_instance = go_instance.
  ENDMETHOD.

  METHOD process_data.
    " Implementation
  ENDMETHOD.

  METHOD validate_input.
    " Implementation
  ENDMETHOD.
ENDCLASS.
```

## Selection screen literals for reports

At the end of each `REPORT`, include as comments the values of the selection screen literals used. This helps code review and maintenance (for example, PA_PO   =Purchase Order

PA_REIDA=Received data

PA_RES  =Dossier Message & Result data

PA_RUN  =Full process

PA_RUNF =Force Full process

PA_SANI =Sanity Checks

PA_SD   =Sales & Distribution

PA_TAXR =Tax Recovery

PA_THDA =Transaction History data

PA_TOOL =Tools )

## Text symbols for reports and classes

At the end of each `REPORT` or `CLASS`, include as comments the values program text symbols used. This helps code review and maintenance (for example, 

T01=Selection parameters
@MaxLength:40
T02=Check options

@MaxLength:40
T03=Selection sanity checks options

@MaxLength:40
T04=Check options

@MaxLength:40
T05=Selection FI-CA documents

@MaxLength:40
T06=Selection tools options

@MaxLength:24
T07=Delete options ).
