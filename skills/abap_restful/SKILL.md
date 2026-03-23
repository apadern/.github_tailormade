---
name: abap_restful
description: 'Skill for creating RESTful ABAP applications using RAP (RESTful Application Programming Model) with file-system based workflow and best practices.'
---

# Purpose

- Provide comprehensive guidance for creating **COMPLETE** RESTful ABAP applications using the RAP (RESTful Application Programming Model).
- Create **ALL necessary artifacts** in the correct order: CDS views, Behavior Definitions, Behavior Implementations (INCLUDING LOCAL CLASSES!), Service Definitions, Service Bindings, and Metadata Extensions.
- **CRITICAL**: Ensure ALL phases (0-5) are completed sequentially with all objects ACTIVE before moving to the next phase.
- **A partial RAP implementation does NOT work** - all artifacts must be created and activated for a functional OData service.
- **🚨 MOST IMPORTANT**: Do NOT skip Local Classes implementation (Phase 3) or Metadata Extensions (Phase 5) - these are REQUIRED for a functional application!

# Critical Rules (File-System Workflow)

- Always use file-system based tools: `abap_createobject`, `abap_search`, `read_file`, `abap_lock`, `replace_string_in_file`, `abap_syntaxcheckcode`, `abap_activate`, `abap_unlock`.
- **IMPORTANT**: Since files are in the ABAP virtual filesystem (adt://), tools like `grep_search` DO NOT WORK. Always use `read_file` directly.
- Activation is mandatory: all objects must be activated (`abap_activate`) to be usable.
- **CRITICAL - ALWAYS use lock/unlock**: `abap_lock` before editing, `abap_unlock` after activation (REQUIRED by SAP).
- **DO NOT use deprecated tools**: `abap_getsourcecode`, `abap_setsourcecode`.
- RAP follows a strict order of creation and activation.
- **Standard workflow**: Create → Search → Read → Lock → Modify → Syntax Check → Activate → Unlock.
- **CRITICAL - CamelCase naming**: The entity name portion of ALL object names, CDS aliases, BDEF aliases, and service exposure aliases MUST use CamelCase (e.g., `SalesOrder`, NOT `SALESORDER` or `salesorder`). See Naming Conventions section below.

---

# CRITICAL: Complete Phase-by-Phase Implementation

**MANDATORY RULES:**

1. **NEVER skip any phase** - All phases (0-5) must be completed in order
2. **ALL objects in a phase MUST be ACTIVE before moving to the next phase**
   - Phase 0 (Database Tables): Activate tables before creating CDS views
   - Phase 1 (CDS Views): Activate all views before creating BDEF
   - Phase 2 (Behavior Definition): Activate BDEF before creating implementation class
   - Phase 3 (Behavior Implementation): Activate implementation class before creating service definition
   - Phase 4 (Service Exposure): Activate service definition before creating service binding
   - Phase 5 (UI Annotations): Activate metadata extensions as final step

3. **Verify activation success** - After each `abap_activate`, check for errors
4. **Do not proceed if activation fails** - Fix all errors before moving forward
5. **Complete the entire RAP stack** - A partial implementation is not functional

**Phase Dependencies:**
```
Phase 0 (Tables)           →  MUST BE ACTIVE  →  Phase 1 (CDS Views)
Phase 1 (CDS Views)        →  MUST BE ACTIVE  →  Phase 2 (BDEF)
Phase 2 (BDEF)             →  MUST BE ACTIVE  →  Phase 3 (Implementation)
Phase 3 (Implementation)   →  MUST BE ACTIVE  →  Phase 4 (Service)
Phase 4 (Service)          →  MUST BE ACTIVE  →  Phase 5 (UI Annotations)
```

**Why this matters:**
- RAP objects have strict dependencies on each other
- Inactive objects cause compilation errors in dependent objects
- The entire stack must be complete for the OData service to work
- Skipping phases results in a non-functional application

---

# Standard Object Creation Workflow

**For ALL RAP objects, follow this exact sequence:**

```
1. Create Object    → abap_createobject (create the object)
2. Search Object    → abap_search (find it and get URIs)
3. Read Source      → read_file (read initial content)
4. Lock Object      → abap_lock (REQUIRED: lock before editing)
5. Modify Code      → replace_string_in_file (edit the code)
6. Syntax Check     → abap_syntaxcheckcode (validate - for CDS/Classes)
7. Fix Errors       → Repeat steps 5-6 if needed
8. Activate         → abap_activate (make it effective)
9. Unlock Object    → abap_unlock (REQUIRED: release the lock)
```

**Important Notes:**
- Steps 4 (Lock) and 9 (Unlock) are **MANDATORY** for all object modifications
- Step 6 (Syntax Check) is **REQUIRED** for all objects before activation
- Never skip the lock/unlock steps - this is a SAP system requirement
- Always activate objects before moving to dependent objects

# Naming Conventions — CamelCase is MANDATORY

> **This rule applies to every single object, field alias, and entity reference throughout the entire RAP stack.**

## Object Technical Names (used in `abap_createobject` and everywhere else)

The entity name segment of object names **MUST be CamelCase** (PascalCase). The prefix and module use uppercase with underscores; the entity name itself starts with an uppercase letter and uses mixed case:

| ✅ Correct | ❌ Wrong |
|---|---|
| `ZMO_R_SalesOrder` | `ZMO_R_SALESORDER` |
| `ZMO_T_Dossier` | `ZMO_T_DOSSIER` |
| `ZMO_C_PurchaseOrderItem` | `ZMO_C_PURCHASEORDERITEM` |
| `ZMO_BP_SalesOrder` | `ZMO_BP_SALESORDER` |
| `ZMO_SV_SalesOrder_UI` | `ZMO_SV_SALESORDER_UI` |
| `ZMO_UI_SalesOrder_O4` | `ZMO_UI_SALESORDER_O4` |

## Field Aliases in CDS Views

All `as <Alias>` expressions in CDS views **MUST use CamelCase**:

```abap
-- ✅ Correct
key sales_order_id  as SalesOrderId,
    customer_name   as CustomerName,
    created_at      as CreatedAt,

-- ❌ Wrong
key sales_order_id  as SALESORDERID,
    customer_name   as customer_name,
```

## Entity Aliases in BDEF

The `alias` keyword in behavior definitions **MUST use CamelCase**:

```abap
-- ✅ Correct
define behavior for ZMO_R_SalesOrder alias SalesOrder

-- ❌ Wrong
define behavior for ZMO_R_SalesOrder alias SALESORDER
```

## Service Exposure Aliases in SRVD

The `as <EntityName>` in service definitions **MUST use CamelCase**:

```abap
-- ✅ Correct
expose ZMO_C_SalesOrder as SalesOrder;

-- ❌ Wrong
expose ZMO_C_SalesOrder as SALESORDER;
```

---

# RAP Object Types Reference

| Object Type | Code | Description | Example Name | Notes |
|------------|------|-------------|--------------|-------|
| CDS View Root (Data Definition) | DDLS/DF | Root data model | ZMO_R_SalesOrder | |
| CDS View Interface | DDLS/DF | Interface view | ZMO_I_SalesOrder | |
| CDS View Projection | DDLS/DF | Consumption/Projection view | ZMO_C_SalesOrder | |
| Behavior Definition | BDEF/BD | Business logic definition | ZMO_R_SalesOrder | |
| Behavior Implementation | CLAS/OC | Implementation class | ZMO_BP_SalesOrder | |
| Service Definition UI | SRVD/SV | UI Service exposure | ZMO_SV_SalesOrder_UI | |
| Service Definition API | SRVD/SV | API Service exposure | ZMO_SV_SalesOrder_API | |
| Service Binding UI OData V2 | SRVB/SVB | OData V2 UI endpoint (NO draft) | ZMO_UI_SalesOrder_O2 | Select "OData V2 - UI" during creation |
| Service Binding UI OData V4 | SRVB/SVB | OData V4 UI endpoint (WITH draft) | ZMO_UI_SalesOrder_O4 | Select "OData V4 - UI" during creation |
| Service Binding API OData V2 | SRVB/SVB | OData V2 API endpoint | ZMO_API_SalesOrder_O2 | Select "OData V2 - Web API" during creation |
| Service Binding API OData V4 | SRVB/SVB | OData V4 API endpoint | ZMO_API_SalesOrder_O4 | Select "OData V4 - Web API" during creation |
| Metadata Extension | DDLX/EX | UI annotations | ZMO_C_SalesOrder_M | |

# Complete Workflow for Creating RESTful Applications

**MANDATORY: Complete ALL phases in sequence. Each phase must be ACTIVE before proceeding to the next. Do NOT skip any phase.**

## Phase 0: Database Tables (Foundation)

**✅ Checkpoint: Tables must be ACTIVE before creating CDS views (Phase 1)**

### 1. Create Persistent Table (Required)

**Naming:** `Z<module>_T_<Entity>` — Example: `ZMO_T_Dossier`, `ZSD_T_SalesOrder`

```
1. abap_createobject(objtype=TABL/DT, name=Z<MODULE>_T_EntityName, description="Persistent Table", parentName=$PACKAGE$)
2. abap_search(query=Z<MODULE>_T_EntityName, objtype=TABL/DT)
3. read_file(filePath=<ADT_URI>)
4. abap_lock(object=<URI>)
5. replace_string_in_file(filePath=<ADT_URI>, oldString=<template>, newString=<table definition>)
6. abap_activate(object=<URI>)
7. abap_unlock(object=<URI>)
```

**Persistent Table Template:**
```abap
@EndUserText.label : 'Persistent Table for EntityName'
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table z<module>_t_entityname {
  key client       : abap.clnt not null;
  key id           : sysuuid_x16 not null;
  field1           : abap.char(50);
  field2           : abap.char(100);
  created_by       : abp_creation_user;
  created_at       : abp_creation_tstmpl;
  changed_by       : abp_lastchange_user;
  changed_at       : abp_lastchange_tstmpl;
  local_changed_at : abp_locinst_lastchange_tstmpl;
}
```

**Alternative: Traditional Database Table Structure**
```abap
@EndUserText.label : 'Persistent Table for EntityName'
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table z<module>_t_entityname {
  key mandt : mandt not null;
  key id    : sysuuid_x16 not null;
  field1    : abap.char(50);
  field2    : abap.char(100);
  
  // Administrative fields (recommended for RAP)
  @Semantics.user.createdBy : true
  created_by : abp_creation_user;
  
  @Semantics.systemDateTime.createdAt : true
  created_at : abp_creation_tstmpl;
  
  @Semantics.user.lastChangedBy : true
  changed_by : abp_lastchange_user;
  
  @Semantics.systemDateTime.lastChangedAt : true
  changed_at : abp_lastchange_tstmpl;
  
  @Semantics.systemDateTime.localInstanceLastChangedAt : true
  local_changed_at : abp_locinst_lastchange_tstmpl;
}
```

### 2. Create Draft Table (Optional - for Draft-Enabled Scenarios)

**Naming:** `Z<module>_T_<Entity>_D` — Example: `ZMO_T_Dossier_D`

```
1. abap_createobject(objtype=TABL/DT, name=Z<MODULE>_T_EntityName_D, description="Draft Table", parentName=$PACKAGE$)
2. abap_search(query=Z<MODULE>_T_EntityName_D, objtype=TABL/DT)
3. read_file(filePath=<ADT_URI>)
4. abap_lock(object=<URI>)
5. replace_string_in_file(filePath=<ADT_URI>, oldString=<template>, newString=<draft table definition>)
6. abap_activate(object=<URI>)
7. abap_unlock(object=<URI>)
```

**Draft Table Template:**
```abap
@EndUserText.label : 'Draft Table for EntityName'
@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE
@AbapCatalog.tableCategory : #TRANSPARENT
@AbapCatalog.deliveryClass : #A
@AbapCatalog.dataMaintenance : #RESTRICTED
define table z<module>_t_entityname_d {
  key mandt : mandt not null;
  key id    : sysuuid_x16 not null;
  field1    : abap.char(50);
  field2    : abap.char(100);
  
  // Administrative fields
  created_by       : abp_creation_user;
  created_at       : abp_creation_tstmpl;
  changed_by       : abp_lastchange_user;
  changed_at       : abp_lastchange_tstmpl;
  local_changed_at : abp_locinst_lastchange_tstmpl;
  
  // Draft administrative fields (required for draft)
  "%admin"         : include sych_bdl_draft_admin_inc;
}
```

**Important Notes for Tables:**
- Always include client field (`mandt` or `client`) for client-dependent tables
- Use UUID (`sysuuid_x16`) as primary key for RAP applications
- Include administrative fields (created_by, created_at, changed_by, changed_at)
- Add `local_changed_at` for ETag handling in OData
- Draft table name must be persistent table name + `_D` suffix
- Draft table must include `"%admin" : include sych_bdl_draft_admin_inc;` for draft functionality
- Activate tables before creating CDS views

## Phase 1: Data Model (CDS Views)

**✅ Checkpoint: ALL CDS views (Root + Projection) must be ACTIVE before creating BDEF (Phase 2)**

### 1. Create Root CDS View Entity (Base/Root)

**Naming:** `Z<module>_R_<ObjectName>` — Example: `ZMO_R_Dossier`, `ZSD_R_PurchaseOrder`

> **Tip:** For creating CDS views you can use the `abap_cds_creator` skill.

```
1. abap_createobject(objtype=DDLS/DF, name=Z<MODULE>_R_EntityName, description="Root View", parentName=$PACKAGE$)
2. abap_search(query=Z<MODULE>_R_EntityName, objtype=DDLS/DF)
3. read_file(filePath=<ADT_URI>)
4. abap_lock(object=<URI>)
5. replace_string_in_file(filePath=<ADT_URI>, oldString=<template>, newString=<CDS definition>)
6. abap_syntaxcheckcode(code=<source>, url=<URI>, objSourceUrl=<path>)
7. Fix errors (repeat steps 5-6 if needed)
8. abap_activate(object=<URI>)
9. abap_unlock(object=<URI>)
```

**Root View Entity Template:**
```abap
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Root View for EntityName'
define root view entity Z<MODULE>_R_EntityName
  as select from z<module>_t_entityname
{
  key id          as Id,
      field1      as Field1,
      field2      as Field2,
      @Semantics.user.createdBy: true
      created_by  as CreatedBy,
      @Semantics.systemDateTime.createdAt: true
      created_at  as CreatedAt,
      @Semantics.user.lastChangedBy: true
      changed_by  as ChangedBy,
      @Semantics.systemDateTime.lastChangedAt: true
      changed_at  as ChangedAt
}
```

### 2. Create Consumption/Projection CDS View

**Naming:** `Z<module>_C_<ObjectName>` — Example: `ZMO_C_Dossier`, `ZSD_C_SalesOrder`

> **Tip:** For creating CDS views you can use the `abap_cds_creator` skill.

```
1. abap_createobject(objtype=DDLS/DF, name=Z<MODULE>_C_EntityName, description="Consumption View", parentName=$PACKAGE$)
2. abap_search(query=Z<MODULE>_C_EntityName, objtype=DDLS/DF)
3. read_file(filePath=<ADT_URI>)
4. abap_lock(object=<URI>)
5. replace_string_in_file(filePath=<ADT_URI>, oldString=<template>, newString=<CDS definition>)
6. abap_syntaxcheckcode(code=<source>, url=<URI>, objSourceUrl=<path>)
7. Fix errors (repeat steps 5-6 if needed)
8. abap_activate(object=<URI>)
9. abap_unlock(object=<URI>)
```

**Consumption/Projection View Template:**
```abap
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Consumption View for EntityName'
@Metadata.allowExtensions: true
define root view entity Z<MODULE>_C_EntityName
  provider contract transactional_query
  as projection on Z<MODULE>_R_EntityName
{
  key Id,
      Field1,
      Field2,
      CreatedBy,
      CreatedAt,
      ChangedBy,
      ChangedAt
}
```

## Phase 2: Business Logic (Behavior Definition)

**✅ Checkpoint: Behavior Definition (BDEF) must be ACTIVE before creating implementation class (Phase 3)**

### 1. Create Behavior Definition

**Naming:** Same name as the root entity — Example: `ZMO_R_Dossier`

```
1. abap_createobject(objtype=BDEF/BDO, name=Z<MODULE>_R_EntityName, description="Behavior Definition", parentName=$PACKAGE$)
2. abap_search(query=Z<MODULE>_R_EntityName, objtype=BDEF/BDO)
3. read_file(filePath=<ADT_URI>)
4. abap_lock(object=<URI>)
5. replace_string_in_file(filePath=<ADT_URI>, oldString=<template>, newString=<BDEF content>)
6. abap_activate(object=<URI>)
7. abap_unlock(object=<URI>)
```

**Managed Behavior Definition Template:**
```abap
managed implementation in class z<module>_bp_entityname unique;
strict ( 2 );

define behavior for Z<MODULE>_R_EntityName alias EntityName
persistent table z<module>_t_entityname
lock master
authorization master ( instance )
etag master ChangedAt
{
  create;
  update;
  delete;

  field ( readonly )
    Id,
    CreatedBy,
    CreatedAt,
    ChangedBy,
    ChangedAt;

  field ( mandatory )
    Field1;

  determination setDefaultValues on modify { create; }
  validation validateField1 on save { create; field Field1; }

  mapping for z<module>_t_entityname
  {
    Id = id;
    Field1 = field1;
    Field2 = field2;
    CreatedBy = created_by;
    CreatedAt = created_at;
    ChangedBy = changed_by;
    ChangedAt = changed_at;
  }
}
```

**Unmanaged Behavior Definition Template (full control):**
```abap
unmanaged implementation in class z<module>_bp_entityname unique;
strict ( 2 );

define behavior for Z<MODULE>_R_EntityName alias EntityName
lock master
authorization master ( instance )
etag master ChangedAt
{
  create;
  update;
  delete;

  field ( readonly )
    CreatedBy,
    CreatedAt,
    ChangedBy,
    ChangedAt;

  field ( mandatory )
    Field1;
}
```

### 2. Create Projection Behavior Definition

**Naming:** Same name as the projection/consumption entity — Example: `ZMO_C_Dossier`

```
1. abap_createobject(objtype=BDEF/BDO, name=Z<MODULE>_C_EntityName, description="Projection Behavior Definition", parentName=$PACKAGE$)
2. abap_search(query=Z<MODULE>_C_EntityName, objtype=BDEF/BDO)
3. read_file(filePath=<ADT_URI>)
4. abap_lock(object=<URI>)
5. replace_string_in_file(filePath=<ADT_URI>, oldString=<template>, newString=<Projection BDEF content>)
6. abap_activate(object=<URI>)
7. abap_unlock(object=<URI>)
```

**Projection Behavior Definition Template:**
```abap
projection;
strict ( 2 );

define behavior for Z<MODULE>_C_EntityName alias EntityName
{
  use create;
  use update;
  use delete;
}
```

## Phase 3: Behavior Implementation

**✅ Checkpoint: Behavior Implementation class must be ACTIVE before creating service definition (Phase 4)**

**🚨 CRITICAL WARNING: DO NOT SKIP LOCAL CLASSES IMPLEMENTATION 🚨**

If your BDEF includes ANY of the following:
- Determinations (`determination <name> on modify/save`)
- Validations (`validation <name> on save`)
- Actions (`action <name>`)
- Functions (`function <name>`)
- Unmanaged scenario (CRUD operations)

**YOU MUST CREATE LOCAL CLASSES (LHC_*) IN `clas.locals_imp.abap` - THIS IS NOT OPTIONAL!**

**When to Implement Local Classes:**

**IF your Behavior Definition (BDEF) contains ANY of the following:**
- ❌ Determinations: `determination <name> on modify { create; }`
- ❌ Validations: `validation <name> on save { create; field Field1; }`
- ❌ Actions: `action <name>`
- ❌ Functions: `function <name>`
- ❌ Unmanaged scenario: `unmanaged implementation in class ...`

**➡️ YOU MUST IMPLEMENT LOCAL CLASSES (LHC_*) in `clas.locals_imp.abap`**

**Required steps:**
1. Search for `clas.locals_imp.abap` file in the behavior pool class
2. Lock the file (`abap_lock`)
3. Add Local Handler Class (LHC_*) DEFINITION and IMPLEMENTATION
4. Add Local Saver Class (LSC_*) if unmanaged
5. Syntax check the code
6. Activate the main class (activates all includes)
7. Unlock the file (`abap_unlock`)

**⚠️ Skipping this = Runtime errors when determinations/validations are triggered!**

### 1. Create Behavior Implementation Class

**Naming:**
- **Behavior Pool (Global Class):** `Z<module>_BP_<ObjectName>` — Example: `ZMO_BP_Dossier`
- **Local Handler Class (created in Local Types):** `LHC_<ClassDescription>` — Example: `LHC_Dossier`
- **Local Saver Class (created in Local Types, only when needed):** `LSC_<ClassDescription>` — Example: `LSC_Dossier`

**CRITICAL RULES - READ CAREFULLY:**
- The **Local Handler Class (LHC_*)** and **Local Saver Class (LSC_*)** must be created in the **Local Types** section of the behavior pool class, NOT as separate global classes.
- **CRITICAL - File Location**: Both the DEFINITION and IMPLEMENTATION of local classes (LHC_* and LSC_*) must be created in the file **`clas.locals_imp.abap`**. NEVER edit `clas.locals_def.abap` (it's auto-generated).
  - ✅ **Edit this file**: `adt://.../<class_name>/source/main#type=CLAS%2FOC;name=<CLASS_NAME>#with-includes#includes#clas.locals_imp.abap` 
  - ❌ **Never edit**: `clas.locals_def.abap` (auto-generated, will be overwritten)
- The **Local Saver Class (LSC_*)** is **NOT always required**:
  - **Managed scenarios**: LSC_* is NOT needed (framework handles save operations)
  - **Unmanaged scenarios**: LSC_* is required to implement save, cleanup, and adjust_numbers methods
  - Only create LSC_* when you need custom save logic or transaction handling

**🚨 MANDATORY REMINDER: If you have determinations/validations/actions in the BDEF, you MUST complete steps 10-17 below to implement the local classes! 🚨**

**Quick Reference: Which Local Classes to Create**

| Scenario | Global Class (BP_*) | Local Handler (LHC_*) | Local Saver (LSC_*) | Must Create? |
|----------|--------------------|-----------------------|---------------------|--------------|
| **Managed** (basic CRUD only, no custom logic) | ✅ Required (empty) | ❌ Not needed | ❌ Not needed | Global class only |
| **Managed** (with determinations/validations/actions) | ✅ Required (empty) | ✅ **REQUIRED** (in clas.locals_imp.abap) | ❌ Not needed | **YES - MUST CREATE LHC_*!** |
| **Unmanaged** (full control) | ✅ Required (empty) | ✅ **REQUIRED** (in clas.locals_imp.abap) | ✅ **REQUIRED** (in clas.locals_imp.abap) | **YES - MUST CREATE LHC_* and LSC_*!** |

**Examples when Local Handler Class (LHC_*) is MANDATORY:**
```abap
// Example BDEF requiring LHC_* implementation:
define behavior for ZMO_R_Dossier alias Dossier
{
  create;
  update;
  delete;
  
  // ⚠️ These features REQUIRE Local Handler implementation:
  determination setDefaultValues on modify { create; }  // ← Requires LHC_*
  validation validateName on save { create; }           // ← Requires LHC_*
  action approve result [1] $self;                      // ← Requires LHC_*
}
```

**🚨 IF YOUR BDEF LOOKS LIKE THE ABOVE, YOU MUST IMPLEMENT LOCAL CLASSES! 🚨**

```
1. abap_createobject(objtype=CLAS/OC, name=Z<MODULE>_BP_EntityName, description="Behavior Implementation", parentName=$PACKAGE$)
2. abap_search(query=Z<MODULE>_BP_EntityName, objtype=CLAS/OC)
3. read_file(filePath=<ADT_URI>)
4. abap_lock(object=<URI>)
5. replace_string_in_file(filePath=<ADT_URI>, oldString=<template>, newString=<class implementation>)
6. abap_syntaxcheckcode(code=<source>, url=<URI>, objSourceUrl=<path>)
7. Fix errors (repeat steps 5-6 if needed)
8. abap_activate(object=<URI>)
9. abap_unlock(object=<URI>)
```

**🚨 For Local Classes (LHC_*, LSC_*) - MANDATORY Additional Steps (DO NOT SKIP!) 🚨**

**IF YOUR BDEF HAS determinations/validations/actions/functions OR is unmanaged, YOU MUST EXECUTE THESE STEPS:**

```
10. abap_search(query=Z<MODULE>_BP_EntityName/source/main#with-includes#includes#clas.locals_imp.abap)
    → Find the clas.locals_imp.abap file URI
    
11. read_file(filePath=<URI to clas.locals_imp.abap>)
    → Read the current content of local types file
    
12. abap_lock(object=<URI to clas.locals_imp.abap>)
    → MANDATORY: Lock the file before editing
    
13. replace_string_in_file(filePath=<clas.locals_imp.abap URI>, oldString=<template>, newString=<local classes code>)
    → Add LHC_* class DEFINITION and IMPLEMENTATION
    → Add LSC_* class if unmanaged scenario
    
14. abap_syntaxcheckcode(code=<source>, url=<URI>, objSourceUrl=<path>)
    → Validate syntax of local classes
    
15. Fix errors (repeat steps 13-14 if needed)
    → Fix any syntax errors before activation
    
16. abap_activate(object=<URI to main class>) - activates all includes
    → CRITICAL: Activate the main class (activates all includes)
    
17. abap_unlock(object=<URI to clas.locals_imp.abap>)
    → MANDATORY: Unlock the file after activation
```

**⚠️ FAILURE TO COMPLETE STEPS 10-17 WILL RESULT IN A NON-FUNCTIONAL RAP APPLICATION! ⚠️**

**CRITICAL**: When editing local classes, always search for and edit the file with path ending in `clas.locals_imp.abap`. NEVER edit `clas.locals_def.abap`.

**Managed Behavior Implementation Template (No LSC_* needed):**
```abap
CLASS z<module>_bp_entityname DEFINITION
  PUBLIC
  ABSTRACT
  FINAL FOR BEHAVIOR OF z<module>_r_entityname.
ENDCLASS.

CLASS z<module>_bp_entityname IMPLEMENTATION.
ENDCLASS.
```

**Unmanaged Behavior Implementation Template (LSC_* required):**

**Global Class (stored as Z<MODULE>_BP_EntityName):**
```abap
CLASS z<module>_bp_entityname DEFINITION
  PUBLIC
  ABSTRACT
  FINAL FOR BEHAVIOR OF z<module>_r_entityname.

  PUBLIC SECTION.

  PRIVATE SECTION.
ENDCLASS.

CLASS z<module>_bp_entityname IMPLEMENTATION.
ENDCLASS.
```

**Local Types (edit file: clas.locals_imp.abap - NEVER edit clas.locals_def.abap):**
```abap
*"* use this source file for the definition and implementation of
*"* local helper classes, interface definitions and type declarations
*"* IMPORTANT: Both DEFINITION and IMPLEMENTATION must be in clas.locals_imp.abap

CLASS lhc_entityname DEFINITION INHERITING FROM cl_abap_behavior_handler.
  PRIVATE SECTION.
    METHODS create FOR MODIFY
      IMPORTING entities FOR CREATE EntityName.
      
    METHODS update FOR MODIFY
      IMPORTING entities FOR UPDATE EntityName.
      
    METHODS delete FOR MODIFY
      IMPORTING keys FOR DELETE EntityName.
      
    METHODS read FOR READ
      IMPORTING keys FOR READ EntityName RESULT result.
      
    METHODS lock FOR LOCK
      IMPORTING keys FOR LOCK EntityName.
ENDCLASS.

CLASS lhc_entityname IMPLEMENTATION.

  METHOD create.
    " Implementation for CREATE operation
    DATA: lt_entities TYPE TABLE FOR CREATE z<module>_r_entityname.
    
    " Map %cid (content ID) and transfer data
    LOOP AT entities ASSIGNING FIELD-SYMBOL(<entity>).
      " Your custom logic here
      INSERT VALUE #( 
        %cid = <entity>-%cid
        id   = cl_system_uuid=>create_uuid_x16_static( )
        " Map other fields
      ) INTO TABLE lt_entities.
    ENDLOOP.
    
    " Return created entities
    mapped-entityname = CORRESPONDING #( lt_entities ).
  ENDMETHOD.

  METHOD update.
    " Implementation for UPDATE operation
    " Your custom logic here
  ENDMETHOD.

  METHOD delete.
    " Implementation for DELETE operation
    " Your custom logic here
  ENDMETHOD.

  METHOD read.
    " Implementation for READ operation
    " Your custom logic here
  ENDMETHOD.

  METHOD lock.
    " Implementation for LOCK
    " Your custom logic here
  ENDMETHOD.

ENDCLASS.

*----------------------------------------------------------------------*
* Local Saver Class (LSC_*) - REQUIRED for Unmanaged scenarios
*----------------------------------------------------------------------*
CLASS lsc_entityname DEFINITION INHERITING FROM cl_abap_behavior_saver.
  PROTECTED SECTION.
    METHODS save_modified REDEFINITION.
    METHODS cleanup_finalize REDEFINITION.
ENDCLASS.

CLASS lsc_entityname IMPLEMENTATION.

  METHOD save_modified.
    " Persist all changes to database
    IF create-entityname IS NOT INITIAL.
      " INSERT logic here
    ENDIF.
    
    IF update-entityname IS NOT INITIAL.
      " UPDATE logic here
    ENDIF.
    
    IF delete-entityname IS NOT INITIAL.
      " DELETE logic here
    ENDIF.
  ENDMETHOD.

  METHOD cleanup_finalize.
    " Cleanup logic after save or rollback
  ENDMETHOD.

ENDCLASS.
```

**Adding Determinations and Validations (in Local Types):**
```abap
CLASS lhc_entityname DEFINITION INHERITING FROM cl_abap_behavior_handler.
  PRIVATE SECTION.
    METHODS setDefaultValues FOR DETERMINE ON MODIFY
      IMPORTING keys FOR EntityName~setDefaultValues.
      
    METHODS validateField1 FOR VALIDATE ON SAVE
      IMPORTING keys FOR EntityName~validateField1.
ENDCLASS.

CLASS lhc_entityname IMPLEMENTATION.

  METHOD setDefaultValues.
    " Read entity data
    READ ENTITIES OF z<module>_r_entityname IN LOCAL MODE
      ENTITY EntityName
      FIELDS ( Field1 Field2 )
      WITH CORRESPONDING #( keys )
      RESULT DATA(lt_entities).

    " Set default values
    MODIFY ENTITIES OF z<module>_r_entityname IN LOCAL MODE
      ENTITY EntityName
      UPDATE FIELDS ( Field2 )
      WITH VALUE #( FOR entity IN lt_entities
                    ( %tky   = entity-%tky
                      Field2 = 'Default Value' ) ).
  ENDMETHOD.

  METHOD validateField1.
    " Read entity data
    READ ENTITIES OF z<module>_r_entityname IN LOCAL MODE
      ENTITY EntityName
      FIELDS ( Field1 )
      WITH CORRESPONDING #( keys )
      RESULT DATA(lt_entities).

    " Validate
    LOOP AT lt_entities INTO DATA(ls_entity).
      IF ls_entity-Field1 IS INITIAL.
        APPEND VALUE #(
          %tky = ls_entity-%tky
          %msg = new_message_with_text(
            severity = if_abap_behv_message=>severity-error
            text     = 'Field1 is mandatory' )
        ) TO reported-entityname.
        
        APPEND VALUE #( %tky = ls_entity-%tky ) 
          TO failed-entityname.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

ENDCLASS.
```

**Managed Scenario with Determinations/Validations (in Local Types):**

For managed scenarios, you typically only need the Local Handler Class (LHC_*) for determinations, validations, and actions. No Local Saver Class (LSC_*) is needed.

**Global Class:**
```abap
CLASS z<module>_bp_entityname DEFINITION
  PUBLIC
  ABSTRACT
  FINAL FOR BEHAVIOR OF z<module>_r_entityname.
ENDCLASS.

CLASS z<module>_bp_entityname IMPLEMENTATION.
ENDCLASS.
```

**Local Types (edit file: clas.locals_imp.abap - NEVER edit clas.locals_def.abap):**
```abap
*"* use this source file for the definition and implementation of
*"* local helper classes, interface definitions and type declarations
*"* IMPORTANT: Both DEFINITION and IMPLEMENTATION must be in clas.locals_imp.abap

CLASS lhc_entityname DEFINITION INHERITING FROM cl_abap_behavior_handler.
  PRIVATE SECTION.
    METHODS setDefaultValues FOR DETERMINE ON MODIFY
      IMPORTING keys FOR EntityName~setDefaultValues.
      
    METHODS validateField1 FOR VALIDATE ON SAVE
      IMPORTING keys FOR EntityName~validateField1.
ENDCLASS.

CLASS lhc_entityname IMPLEMENTATION.

  METHOD setDefaultValues.
    " Read entity data
    READ ENTITIES OF z<module>_r_entityname IN LOCAL MODE
      ENTITY EntityName
      FIELDS ( Field1 Field2 )
      WITH CORRESPONDING #( keys )
      RESULT DATA(lt_entities).

    " Set default values
    MODIFY ENTITIES OF z<module>_r_entityname IN LOCAL MODE
      ENTITY EntityName
      UPDATE FIELDS ( Field2 )
      WITH VALUE #( FOR entity IN lt_entities
                    ( %tky   = entity-%tky
                      Field2 = 'Default Value' ) ).
  ENDMETHOD.

  METHOD validateField1.
    " Read entity data
    READ ENTITIES OF z<module>_r_entityname IN LOCAL MODE
      ENTITY EntityName
      FIELDS ( Field1 )
      WITH CORRESPONDING #( keys )
      RESULT DATA(lt_entities).

    " Validate
    LOOP AT lt_entities INTO DATA(ls_entity).
      IF ls_entity-Field1 IS INITIAL.
        APPEND VALUE #(
          %tky = ls_entity-%tky
          %msg = new_message_with_text(
            severity = if_abap_behv_message=>severity-error
            text     = 'Field1 is mandatory' )
        ) TO reported-entityname.
        
        APPEND VALUE #( %tky = ls_entity-%tky ) 
          TO failed-entityname.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

ENDCLASS.
```

## Phase 4: Service Exposure

**✅ Checkpoint: Service Definition AND Service Binding must be ACTIVE before creating UI annotations (Phase 5)**

### 1. Create Service Definition

**Naming:** `Z<module>_SV_<ServiceName>_UI` or `Z<module>_SV_<ServiceName>_API` — Example: `ZMO_SV_Dossier_UI`, `ZMO_SV_Dossier_API`

```
1. abap_createobject(objtype=SRVD/SRV, name=Z<MODULE>_SV_EntityName_UI, description="Service Definition", parentName=$PACKAGE$)
2. abap_search(query=Z<MODULE>_SV_EntityName_UI, objtype=SRVD/SV)
3. read_file(filePath=<ADT_URI>)
4. abap_lock(object=<URI>)
5. replace_string_in_file(filePath=<ADT_URI>, oldString=<template>, newString=<service definition>)
6. abap_activate(object=<URI>)
7. abap_unlock(object=<URI>)
```

**Service Definition Template (UI Service):**
```abap
@EndUserText.label: 'Service Definition for EntityName UI'
define service Z<MODULE>_SV_EntityName_UI {
  expose Z<MODULE>_C_EntityName as EntityName;
}
```

**Service Definition Template (API Service):**
```abap
@EndUserText.label: 'Service Definition for EntityName API'
define service Z<MODULE>_SV_EntityName_API {
  expose Z<MODULE>_C_EntityName as EntityName;
}
```

### 2. Create Service Binding

**IMPORTANT:** The system supports both OData V2 and V4. When you create a Service Binding with `abap_createobject(objtype=SRVB/SVB, ...)`, you can either:

**Option A - Programmatic (Recommended for AI agents):** Provide all parameters directly:
- `service`: The Service Definition name
- `bindingtype`: `ODATA` for V2, `ODATA_V4` for V4
- `category`: `0` for UI, `1` for Web API

**Option B - Interactive:** Omit the optional parameters and VS Code will interactively ask you to select:
1. **The binding type**: Choose from:
   - **OData V2 - Web API** (for programmatic API access, NO draft support)
   - **OData V2 - UI** (for Fiori applications, NO draft support)
   - **OData V4 - Web API** (for programmatic API access, WITH draft support)
   - **OData V4 - UI** (for Fiori applications, WITH draft support)
2. **The Service Definition** to bind

**🚨 CRITICAL DECISION RULE: Choose OData Version AND Binding Type 🚨**

**Step 1 — Decide Binding Type (UI vs API):**
- **RESTful UI application** (Fiori app, user-facing): → Select **UI** type (`category=0`, suffix `_UI`)
- **Pure API / backend service** (programmatic access, no UI): → Select **API / Web API** type (`category=1`, suffix `_API`)

**Step 2 — Decide OData Version Based on Draft Support:**
- **✅ BDEF has NO draft** → Use **OData V2** (bindingtype=`ODATA`, suffix `_O2`)
- **✅ BDEF has draft support** → Use **OData V4** (bindingtype=`ODATA_V4`, suffix `_O4`)

**How to check your BDEF for draft support:**
```abap
// ❌ NO DRAFT → Use OData V2
define behavior for Z<MODULE>_R_EntityName alias EntityName
persistent table z<module>_t_entityname
lock master
{
  create;
  update;
  delete;
}

// ✅ WITH DRAFT → Use OData V4
define behavior for Z<MODULE>_R_EntityName alias EntityName
persistent table z<module>_t_entityname
draft table z<module>_t_entityname_d  // ← Draft table = Use V4!
lock master
{
  create;
  update;
  delete;
  
  draft action Edit;      // ← Draft actions = Use V4!
  draft action Activate;
}
```

---

#### Create Service Binding with abap_createobject

**Naming Convention:**
- **OData V2 UI**: `Z<module>_UI_<ServiceName>_O2` — Example: `ZMO_UI_Dossier_O2`
- **OData V2 API**: `Z<module>_API_<ServiceName>_O2` — Example: `ZMO_API_Dossier_O2`
- **OData V4 UI**: `Z<module>_UI_<ServiceName>_O4` — Example: `ZMO_UI_Dossier_O4`
- **OData V4 API**: `Z<module>_API_<ServiceName>_O4` — Example: `ZMO_API_Dossier_O4`

**Workflow (Programmatic - Recommended for AI agents):**
```
1. abap_createobject(
     objtype=SRVB/SVB, 
     name=Z<MODULE>_UI_EntityName_O2, 
     description="Service Binding", 
     parentName=$PACKAGE$,
     service=Z<MODULE>_SV_EntityName_UI,
     bindingtype=ODATA,           // Use "ODATA" for V2, "ODATA_V4" for V4
     category=0                    // Use "0" for UI, "1" for Web API
   )
   
2. The system automatically creates the service binding with the correct configuration
3. abap_activate(object=<URI from search result>)
```

**Workflow (Interactive - Manual selection):**
```
1. abap_createobject(objtype=SRVB/SVB, name=Z<MODULE>_UI_EntityName_O2, description="Service Binding", parentName=$PACKAGE$)
   → VS Code will interactively prompt:
      a) Select binding type:
         - Choose "OData V2 - UI" if NO draft (for Fiori apps)
         - Choose "OData V2 - Web API" if NO draft (for APIs)
         - Choose "OData V4 - UI" if WITH draft (for Fiori apps)
         - Choose "OData V4 - Web API" if WITH draft (for APIs)
      b) Select Service Definition:
         - Choose the service definition created in step 1 (e.g., Z<MODULE>_SV_EntityName_UI)
   
2. The system automatically creates the service binding with the correct configuration
3. abap_activate(object=<URI from search result>)
```

**Parameter Reference:**

| Parameter | Values | Description |
|-----------|--------|-------------|
| `service` | Service Definition name | Name of the Service Definition to bind (e.g., `ZMO_SV_DOSSIER_UI`) |
| `bindingtype` | `ODATA` or `ODATA_V4` | Use `ODATA` for OData V2, `ODATA_V4` for OData V4 |
| `category` | `0` or `1` | Use `0` for UI (Fiori apps), `1` for Web API |

**Note:** When using the programmatic approach, you provide all parameters directly and the system creates the binding without user interaction. When parameters are omitted, VS Code will prompt interactively.

**Selection Guide:**

| BDEF Draft? | Purpose | Select This Option | Naming Suffix | Type |
|-------------|---------|-------------------|---------------|------|
| ❌ NO | Fiori Application | **OData V2 - UI** | `_O2` | ODATA_V2_UI |
| ❌ NO | Programmatic API | **OData V2 - Web API** | `_O2` | ODATA_V2_WEB_API |
| ✅ YES | Fiori Application | **OData V4 - UI** | `_O4` | ODATA_V4_UI |
| ✅ YES | Programmatic API | **OData V4 - Web API** | `_O4` | ODATA_V4_WEB_API |

---

**Service Binding XML Templates (for reference only - auto-generated):**

<details>
<summary>OData V2 UI Template</summary>

```xml
<?xml version="1.0" encoding="utf-8"?>
<ServiceBinding xmlns="http://www.sap.com/adt/servicebinding/model">
  <internalName>Z<MODULE>_UI_EntityName_O2</internalName>
  <version>0001</version>
  <type>ODATA_V2_UI</type>
  <serviceDefinition>Z<MODULE>_SV_EntityName_UI</serviceDefinition>
  <bindingCreated>true</bindingCreated>
</ServiceBinding>
```
</details>

<details>
<summary>OData V2 Web API Template</summary>

```xml
<?xml version="1.0" encoding="utf-8"?>
<ServiceBinding xmlns="http://www.sap.com/adt/servicebinding/model">
  <internalName>Z<MODULE>_API_EntityName_O2</internalName>
  <version>0001</version>
  <type>ODATA_V2_WEB_API</type>
  <serviceDefinition>Z<MODULE>_SV_EntityName_API</serviceDefinition>
  <bindingCreated>true</bindingCreated>
</ServiceBinding>
```
</details>

<details>
<summary>OData V4 UI Template</summary>

```xml
<?xml version="1.0" encoding="utf-8"?>
<ServiceBinding xmlns="http://www.sap.com/adt/servicebinding/model">
  <internalName>Z<MODULE>_UI_EntityName_O4</internalName>
  <version>0001</version>
  <type>ODATA_V4_UI</type>
  <serviceDefinition>Z<MODULE>_SV_EntityName_UI</serviceDefinition>
  <bindingCreated>true</bindingCreated>
</ServiceBinding>
```
</details>

<details>
<summary>OData V4 Web API Template</summary>

```xml
<?xml version="1.0" encoding="utf-8"?>
<ServiceBinding xmlns="http://www.sap.com/adt/servicebinding/model">
  <internalName>Z<MODULE>_API_EntityName_O4</internalName>
  <version>0001</version>
  <type>ODATA_V4_WEB_API</type>
  <serviceDefinition>Z<MODULE>_SV_EntityName_API</serviceDefinition>
  <bindingCreated>true</bindingCreated>
</ServiceBinding>
```

## Phase 5: UI Annotations

**✅ Final Phase: Metadata Extensions must be ACTIVE for complete RAP application**

**🚨 CRITICAL: Metadata Extension is MANDATORY for Fiori UI Applications! 🚨**

Without metadata extensions:
- ❌ Fiori apps will not display correctly
- ❌ List views will be empty or show only raw data
- ❌ Object pages will not have proper facets/sections
- ❌ Search fields will not work properly

**IF YOU ARE CREATING A UI SERVICE (`Z<MODULE>_SV_*_UI`), YOU MUST CREATE METADATA EXTENSION!**

### 1. Create Metadata Extension

**Naming:** Same name as the CDS entity it relates to + `_M` + counter (optional) — Example: `ZMO_C_Dossier_M`, `ZMO_C_Dossier_M2`

> **Tip:** For creating CDS metadata extensions you can use the `abap_cds_creator` skill.

**🚨 DO NOT SKIP THIS STEP IF YOU HAVE A UI SERVICE BINDING! 🚨**

```
1. abap_createobject(objtype=DDLX/EX, name=Z<MODULE>_C_EntityName_M, description="Metadata Extension", parentName=$PACKAGE$)
2. abap_search(query=Z<MODULE>_C_EntityName_M, objtype=DDLX/EX)
3. read_file(filePath=<ADT_URI>)
4. abap_lock(object=<URI>)
5. replace_string_in_file(filePath=<ADT_URI>, oldString=<template>, newString=<metadata extension>)
6. abap_activate(object=<URI>)
7. abap_unlock(object=<URI>)
```

**🏷️ LABELS REMINDER: Do NOT forget to add `@EndUserText.label` AND `label:` in `@UI` annotations for EVERY field! Without labels, columns and form fields show technical names instead of user-friendly text.**

**Metadata Extension Template:**
```abap
@Metadata.layer: #CORE
@UI: {
  headerInfo: {
    typeName: 'Entity',
    typeNamePlural: 'Entities',
    title: { type: #STANDARD, value: 'Id' }
  }
}
annotate view Z<MODULE>_C_EntityName with
{
  @UI.facet: [
    {
      id: 'EntityName',
      purpose: #STANDARD,
      type: #IDENTIFICATION_REFERENCE,
      label: 'Entity Details',
      position: 10
    }
  ]
  
  // 🏷️ Always include @EndUserText.label and label: in every @UI annotation!
  @EndUserText.label: 'ID'
  @UI: {
    lineItem: [ { position: 10, importance: #HIGH, label: 'ID' } ],
    identification: [ { position: 10, label: 'ID' } ]
  }
  Id;
  
  @EndUserText.label: 'Field 1'
  @UI: {
    lineItem: [ { position: 20, importance: #HIGH, label: 'Field 1' } ],
    identification: [ { position: 20, label: 'Field 1' } ]
  }
  Field1;
  
  @EndUserText.label: 'Field 2'
  @UI: {
    lineItem: [ { position: 30, importance: #MEDIUM, label: 'Field 2' } ],
    identification: [ { position: 30, label: 'Field 2' } ]
  }
  Field2;
}
```

# RAP Scenarios and Templates

## Scenario 1: Managed RAP (Recommended for CRUD)

**When to use:**
- Standard CRUD operations
- Framework handles transactions, locking, numbering
- Less code, faster development

**Key Features:**
- Uses `managed` keyword in BDEF
- Framework provides default implementations
- Supports early numbering, late numbering, UUID
- Built-in transaction handling

## Scenario 2: Unmanaged RAP (Full Control)

**When to use:**
- Complex business logic
- Integration with legacy APIs/BAPIs
- Custom transaction handling
- Non-standard data persistence

**Key Features:**
- Uses `unmanaged` keyword in BDEF
- Developer implements all CRUD operations
- Full control over data persistence
- Requires more code

## Scenario 3: Read-Only RAP

**When to use:**
- Analytical applications
- Reporting services
- No data modification required

**BDEF Template:**
```abap
managed implementation in class z<module>_bp_entityname unique;
strict ( 2 );

define behavior for Z<MODULE>_R_EntityName alias EntityName
persistent table z<module>_t_entityname
lock master
authorization master ( instance )
{
  // Only read operations
}
```

# Best Practices

1. **Always use strict mode**: Add `strict ( 2 );` in BDEF for compile-time checks
2. **Enable draft**: For editing scenarios, add draft support in BDEF (requires OData V4!)
3. **Choose correct OData version**: NO draft → OData V2; WITH draft → OData V4
4. **Use semantic annotations**: `@Semantics.user.createdBy`, `@Semantics.amount.currencyCode`
5. **Implement proper authorization**: Use authorization master/dependent declarations
6. **Add validations**: Validate data in behavior implementation before save
7. **Use determinations**: Auto-fill fields, calculate values
8. **Follow SAP naming**: Use consistent prefixes (Z/Y), module codes (MM, SD, FI)
9. **Test incrementally**: Activate and test each phase before moving to next
10. **Use UUIDs for keys**: Prefer `key id as Id` with UUID generation
11. **Document annotations**: Use `@EndUserText.label` for all artifacts
12. **Always implement local classes**: When BDEF has determinations/validations/actions, create LHC_* in clas.locals_imp.abap
13. **Always create metadata extension**: For UI services, metadata extension is mandatory

# Common RAP Features

## Draft Enabling (for Edit Scenarios)

**⚠️ IMPORTANT: When you enable draft, you MUST use OData V4 for the service binding!**

```abap
define behavior for Z<MODULE>_R_EntityName alias EntityName
persistent table z<module>_t_entityname
draft table z<module>_t_entityname_d        // ← Draft table REQUIRES OData V4!
lock master
authorization master ( instance )
etag master ChangedAt
{
  create;
  update;
  delete;
  
  draft action Edit;                        // ← Draft actions REQUIRE OData V4!
  draft action Activate;
  draft action Discard;
  draft action Resume;
  draft determine action Prepare;
}
```

**Service Binding Requirements:**
- ✅ **WITH draft** (as above) → Use OData V4 (SRVB/SVB, _O4, select "OData V4 - UI" or "OData V4 - Web API")
- ✅ **WITHOUT draft** → Use OData V2 (SRVB/SVB, _O2, select "OData V2 - UI" or "OData V2 - Web API")

## Actions (Custom Operations)
```abap
define behavior for Z<MODULE>_R_EntityName alias EntityName
{
  // Static action
  action approve result [1] $self;
  
  // Instance action with parameter
  action setStatus parameter ZD_StatusParam result [1] $self;
  
  // Factory action (creates new instance)
  factory action createFromTemplate [1];
}
```

## Functions (Read-Only Operations)
```abap
define behavior for Z<MODULE>_R_EntityName alias EntityName
{
  function calculateTotal result [1] ZD_TotalResult;
}
```

## Associations (Master-Detail)
```abap
define behavior for Z<MODULE>_R_SalesOrder alias SalesOrder
{
  association _Items { create; }
}

define behavior for Z<MODULE>_R_SalesOrderItem alias SalesOrderItem
{
  update;
  delete;
  
  association _SalesOrder;
}
```

# 📋 COMPLETE WORKFLOW CHECKLIST - FOLLOW THIS RELIGIOUSLY 📋

**Use this checklist for EVERY RAP application you create. Mark each step as done before proceeding.**

## Phase 0: Database Tables ✅
- [ ] Create Persistent Table (`Z<MODULE>_T_<Entity>`)
- [ ] Lock → Edit → Syntax Check → Activate → Unlock
- [ ] If draft-enabled: Create Draft Table (`Z<MODULE>_T_<Entity>_D`)
- [ ] Lock → Edit → Activate → Unlock
- [ ] **Checkpoint: All tables ACTIVE?** ✅

## Phase 1: CDS Views ✅
- [ ] Create Root CDS View (`Z<MODULE>_R_<Entity>`)
- [ ] Lock → Edit → Syntax Check → Activate → Unlock
- [ ] Create Consumption/Projection CDS View (`Z<MODULE>_C_<Entity>`)
- [ ] Lock → Edit → Syntax Check → Activate → Unlock
- [ ] **Checkpoint: All CDS views ACTIVE?** ✅

## Phase 2: Behavior Definition ✅
- [ ] Create Behavior Definition (`Z<MODULE>_R_<Entity>.bdef`)
- [ ] Lock → Edit → Activate → Unlock
- [ ] **Checkpoint: BDEF ACTIVE?** ✅
- [ ] **DECISION POINT**: Does your BDEF contain ANY of these?
  - [ ] `determination <name>`
  - [ ] `validation <name>`
  - [ ] `action <name>`
  - [ ] `function <name>`
  - [ ] `unmanaged implementation`
  - **If YES to ANY → YOU MUST create Local Classes in Phase 3!** 🚨

## Phase 3: Behavior Implementation ✅
- [ ] Create Behavior Pool Class (`Z<MODULE>_BP_<Entity>`)
- [ ] Lock → Edit → Syntax Check → Activate → Unlock
- [ ] **⚠️ CRITICAL DECISION: Did you answer YES to Phase 2 decision point?**
  - **If YES, complete ALL sub-steps below:**
    - [ ] Search for `clas.locals_imp.abap` file
    - [ ] Read current content of `clas.locals_imp.abap`
    - [ ] Lock `clas.locals_imp.abap` file
    - [ ] Create Local Handler Class (LHC_*) DEFINITION
    - [ ] Create Local Handler Class (LHC_*) IMPLEMENTATION
    - [ ] Implement determination methods (if any)
    - [ ] Implement validation methods (if any)
    - [ ] Implement action methods (if any)
    - [ ] If unmanaged: Create Local Saver Class (LSC_*) DEFINITION and IMPLEMENTATION
    - [ ] Syntax check the local classes code
    - [ ] Activate main class (activates all includes)
    - [ ] Unlock `clas.locals_imp.abap` file
  - **If NO, skip to Phase 4**
- [ ] **Checkpoint: Behavior Implementation (including local classes if needed) ACTIVE?** ✅

## Phase 4: Service Exposure ✅
- [ ] Create Service Definition (`Z<MODULE>_SV_<Entity>_UI` or `_API`)
- [ ] Lock → Edit → Activate → Unlock
- [ ] **Create Service Binding with appropriate OData version:**
  - [ ] Use `abap_createobject` with `objtype=SRVB/SVB`
  - [ ] **DECISION: Is this a RESTful UI application (Fiori app)?**
    - **YES (UI app)** → Use type `UI` (`category=0`), name suffix `_UI_*`
    - **NO (pure API/backend)** → Use type `Web API` (`category=1`), name suffix `_API_*`
  - [ ] Name: `Z<MODULE>_UI_<Entity>_O2` (V2 UI) or `Z<MODULE>_UI_<Entity>_O4` (V4 UI) or `Z<MODULE>_API_<Entity>_O2/O4` (API)
  - [ ] When prompted, check your BDEF for draft support:
    - **NO draft** (no `draft table`, no `draft action`) → Select **"OData V2 - UI"** or **"OData V2 - Web API"**
    - **WITH draft** (`draft table` + `draft action Edit`) → Select **"OData V4 - UI"** or **"OData V4 - Web API"**
  - [ ] Select the service definition you created above
- [ ] Activate the service binding
- [ ] **Checkpoint: Service Definition and Service Binding ACTIVE?** ✅
- [ ] **DECISION POINT**: Is this a UI service (`_SV_*_UI` and `_UI_*_O2/O4`)?
  - **If YES → YOU MUST create Metadata Extension in Phase 5!** 🚨
  - **If NO (API only) → Metadata Extension optional**

## Phase 5: UI Annotations ✅
- [ ] **⚠️ CRITICAL: Did you create a UI service in Phase 4?**
  - **If YES, complete ALL sub-steps below:**
    - [ ] Create Metadata Extension (`Z<MODULE>_C_<Entity>_M`)
    - [ ] Lock → Edit → Activate → Unlock
    - [ ] Add `@UI.facet` annotations
    - [ ] Add `@UI.lineItem` annotations for list view
    - [ ] Add `@UI.identification` annotations for object page
    - [ ] Add `@UI.headerInfo` for title
    - [ ] Syntax check the metadata extension
    - [ ] Activate metadata extension
  - **If NO (API only), skip this phase**
- [ ] **Checkpoint: Metadata Extension ACTIVE (if UI service)?** ✅

## Final Verification ✅
- [ ] All objects ACTIVE with no errors
- [ ] Service binding published
- [ ] Open service binding preview → Test OData service
- [ ] If UI: Verify Fiori preview shows data correctly
- [ ] If UI: Verify list view displays fields
- [ ] If UI: Verify object page has proper facets
- [ ] Test CREATE operation (if enabled)
- [ ] Test UPDATE operation (if enabled)
- [ ] Test DELETE operation (if enabled)
- [ ] If you have determinations: Test they execute correctly
- [ ] If you have validations: Test they trigger on save
- [ ] **Final Checkpoint: Everything works end-to-end?** ✅

**🎉 ONLY NOW is the RAP application complete! 🎉**

# Troubleshooting

## Common Issues

1. **"Behavior implementation class not found"**
   - Ensure class name matches: `Z<MODULE>_BP_<EntityName>` (naming convention)
   - Activate behavior definition before creating class

2. **"Entity not exposed in service"**
   - Check service definition includes correct projection view
   - Activate service definition before creating binding
   - Publish service binding in service binding editor

3. **"Field is read-only"**
   - Check BDEF: remove field from `field ( readonly )` section
   - For managed scenario, ensure field is not system-managed

4. **Validation not triggered**
   - Ensure validation is declared in BDEF
   - Check validation timing: `on save` vs `on modify`
   - Verify keys are correctly passed to validation method

5. **Authorization check failed**
   - For development: Use `@AccessControl.authorizationCheck: #NOT_REQUIRED`
   - For production: Implement proper authorization object checks

# Quick Reference: Activation Order

**CRITICAL:** Complete ALL steps in sequence. Each object MUST be ACTIVE before creating the next dependent object. NEVER skip any step.

**IMPORTANT:** For each object, follow the standard workflow: Create → Search → Read → Lock → Modify → Syntax Check → Activate → Unlock.

**MANDATORY SEQUENCE (Complete ALL steps):**

1. ✅ **Persistent Table** - `Z<MODULE>_T_<Entity>` (MUST be active first)
2. ✅ **Draft Table** - `Z<MODULE>_T_<Entity>_D` (if draft-enabled scenario - MUST be active)
3. ✅ **CDS View (Root)** - `Z<MODULE>_R_<Entity>` (MUST be active before Projection)
4. ✅ **CDS View (Consumption/Projection)** - `Z<MODULE>_C_<Entity>` (MUST be active before BDEF)
5. ✅ **Behavior Definition** - `Z<MODULE>_R_<Entity>.bdef` (same as root - MUST be active before implementation)
6. ✅ **Behavior Implementation Class** - `Z<MODULE>_BP_<Entity>` (MUST be active before service definition)
   - 🚨 **CRITICAL SUB-STEP**: If BDEF has determinations/validations/actions/functions:
     - **MUST create Local Handler Class (LHC_*) in clas.locals_imp.abap**
     - **MUST follow steps 10-17 from Phase 3** (search → read → lock → edit → syntax check → activate → unlock)
     - ⚠️ **Skipping local classes = BROKEN APPLICATION!**
7. ✅ **Service Definition** - `Z<MODULE>_SV_<Entity>_UI` or `Z<MODULE>_SV_<Entity>_API` (MUST be active before binding)
8. ✅ **Service Binding** - Use `objtype=SRVB/SVB`, choose based on draft support:
   - **NO Draft** → `Z<MODULE>_UI_<Entity>_O2` (Select "OData V2 - UI" or "OData V2 - Web API")
   - **WITH Draft** → `Z<MODULE>_UI_<Entity>_O4` (Select "OData V4 - UI" or "OData V4 - Web API")
   - (MUST be active and published)
9. ✅ **Metadata Extension** - `Z<MODULE>_C_<Entity>_M` (🚨 MANDATORY for UI services - MUST be active for UI to work)
10. ✅ **Test via Service Binding** preview or Fiori app (verify entire stack works)

**🚨 COMPLETENESS CHECKLIST - VERIFY BEFORE CONSIDERING THE TASK DONE: 🚨**

- [ ] All tables created and ACTIVE
- [ ] All CDS views created and ACTIVE
- [ ] Behavior Definition created and ACTIVE
- [ ] Behavior Implementation global class created and ACTIVE
- [ ] **IF BDEF has determinations/validations/actions: Local classes (LHC_*) created in clas.locals_imp.abap and ACTIVE**
- [ ] Service Definition created and ACTIVE
- [ ] Service Binding created, ACTIVE, and PUBLISHED
- [ ] **IF UI service: Metadata Extension created and ACTIVE**
- [ ] Tested OData service endpoint successfully

**Remember:** 
- Always use `abap_lock` before editing and `abap_unlock` after activation for each object!
- Verify each activation succeeds before moving to the next object
- A partial RAP implementation is NOT functional - ALL objects are required
- **Omitting local classes or metadata extension = INCOMPLETE/BROKEN APPLICATION**
- If activation fails, fix the errors immediately before proceeding

# Additional Resources

- Use examples from existing RAP applications in your system
- Check SAP Help Portal for detailed RAP documentation
- Follow SAP's Clean ABAP guidelines for code quality
- Test OData services using `/sap/bc/adt/businessservices/odatav4/<service>/` endpoint

---

# 🚨 FINAL REMINDER - DO NOT FINISH WITHOUT THESE! 🚨

**Before you report a RAP task as "complete", verify these common omissions:**

## ❌ COMMON MISTAKE #1: Skipping Local Classes
**Symptom**: Runtime error when determinations/validations should trigger
**Check:**
```
Did your BDEF have ANY of these keywords?
- determination
- validation
- action
- function
- unmanaged implementation

If YES: Did you create and activate LHC_* class in clas.locals_imp.abap?
```
**Fix**: Go back to Phase 3, steps 10-17. Create the local classes NOW.

## ❌ COMMON MISTAKE #2: Skipping Metadata Extension
**Symptom**: Fiori app shows empty list or raw data without structure
**Check:**
```
Did you create a UI service binding (Z<MODULE>_UI_*_O4)?

If YES: Did you create and activate Metadata Extension (Z<MODULE>_C_*_M)?
```
**Fix**: Go back to Phase 5. Create the metadata extension NOW.

## ❌ COMMON MISTAKE #3: Wrong OData Version Selection
**Symptom**: Draft functionality doesn't work, or service binding has issues
**Check:**
```
Look at your BDEF - does it have:
- draft table z<module>_t_<entity>_d
- draft action Edit
- draft action Activate

If YES (draft enabled):
  Did you select "OData V4 - UI" or "OData V4 - Web API"?
  Does your service binding name end with _O4?
  
If NO (no draft):
  Did you select "OData V2 - UI" or "OData V2 - Web API"?
  Does your service binding name end with _O2?
```
**Fix**: Delete the incorrect service binding and create the correct one:
1. Use `abap_createobject(objtype=SRVB/SVB, ...)`
2. **NO draft** → Select **"OData V2 - UI"** or **"OData V2 - Web API"**, name with `_O2` suffix
3. **WITH draft** → Select **"OData V4 - UI"** or **"OData V4 - Web API"**, name with `_O4` suffix

## ❌ COMMON MISTAKE #4: Not Testing the Complete Stack
**Symptom**: Objects are "active" but service doesn't work
**Check:**
```
Did you:
- Open the service binding?
- Click "Preview" button?
- Verify the OData service loads?
- Test CREATE/UPDATE/DELETE operations?
- Verify Fiori UI displays correctly (if UI service)?
```
**Fix**: Test thoroughly before reporting completion.

## ✅ SUCCESS CRITERIA
A RAP application is ONLY complete when:
1. ✅ All objects are ACTIVE (no errors in activation)
2. ✅ Service binding is PUBLISHED (not just created)
3. ✅ **Correct OData version used** (V2 for no draft, V4 for draft)
4. ✅ OData service preview works
5. ✅ If BDEF has determinations/validations/actions: LHC_* exists in clas.locals_imp.abap
6. ✅ If UI service: Metadata extension exists and Fiori preview works
7. ✅ All CRUD operations (create/update/delete) work as expected
8. ✅ If you have validations: They trigger and show error messages
9. ✅ If you have determinations: They execute and populate fields
10. ✅ If BDEF has draft: Draft actions (Edit/Activate) work correctly

**DON'T STOP UNTIL ALL CHECKMARKS ARE GREEN!**

---

**Note**: This skill follows modern RAP development practices and the file-system based workflow required by VS Code's ABAP extension.
