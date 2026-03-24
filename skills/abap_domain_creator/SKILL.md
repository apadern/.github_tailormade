---
name: abap_domain_creator
description: Create an ABAP Domain in SAP
---

# How to use
When asked to create an ABAP domain (Dominio DDIC).

## Steps

1. **Create the domain** using `abap_createobject` with `objtype` = `DOMA/DD`
   - **MUST include a description** in the `description` parameter (max 60 characters)
   - The `parentName` is the package (e.g. `$TMP`, `ZFI`, `ZMM`, ...)
   - Example: name=`ZFI_D_INVTYPE`, description=`Tipo de factura`, parentName=`$TMP`

2. **Search for the created object** using `abap_search` (type `DOMA/DD`) to get the exact file URI
   - File path format: `adt://system_name/%24TMP/Dictionary/Domains/OBJECT_NAME.doma.xml`
   - For non-$TMP packages: `adt://system_name/System Library/PACKAGE_NAME/Dictionary/Domains/OBJECT_NAME.doma.xml`

3. **Read the generated XML file** using `read_file` to inspect the initial (empty) content

4. **Lock the object** using `abap_lock` before making any modifications
   - Input: the file URI obtained in step 2

5. **Modify the XML structure** using `multi_replace_string_in_file` to set all required fields **in a single call**:
   - **`adtcore:description`** attribute in the root `<doma:domain>` element — **🚨 MANDATORY**: if missing, activation will fail. Check after creation and add it if absent. **Max 60 characters.**
   - **`<doma:datatype>`**: Set the base type (e.g. `CHAR`, `NUMC`, `DATS`, `TIMS`, `DEC`, `INT4`, `INT2`, `CURR`, `QUAN`)
   - **`<doma:length>` (in `typeInformation`)**: 6-digit zero-padded length (e.g. `000002`)
   - **`<doma:length>` (in `outputInformation`)**: same value as above
   - **`<doma:fixValues>`**: Replace empty `<doma:fixValues/>` with individual `<doma:fixValue>` entries if fixed values are needed (see structure below)

6. **Activate the object** using `abap_activate`
   - Use the encoded file URI: `adt://system/%24TMP/Dictionary/Domains/OBJECT_NAME.doma.xml`
   - ⚠️ If activation fails with "Data type ' ' does not exist", double-check `adtcore:description` is present and `<doma:datatype>` is not empty

7. **Unlock the object** using `abap_unlock` — always do this even if a previous step failed

---

## Fixed Values structure

When no fixed values are needed, the element should remain as:
```xml
<doma:fixValues/>
```

When fixed values are required, replace it with:
```xml
<doma:fixValues>
  <doma:fixValue>
    <doma:position>0001</doma:position>
    <doma:low>VALUE1</doma:low>
    <doma:high/>
    <doma:text>Description 1</doma:text>
  </doma:fixValue>
  <doma:fixValue>
    <doma:position>0002</doma:position>
    <doma:low>VALUE2</doma:low>
    <doma:high/>
    <doma:text>Description 2</doma:text>
  </doma:fixValue>
</doma:fixValues>
```

> **Note on position values**: use 4-digit zero-padded sequential numbers (`0001`, `0002`, `0003`, ...).
> **Note on `<doma:high/>`**: leave empty unless the domain uses ranges.
> **Note on text**: use the language of the system (masterLanguage). Accented characters are supported (UTF-8).

---

## Example XML reference

Below is a complete, activated domain XML for reference:

```xml
<?xml version="1.0" encoding="utf-8"?>
<doma:domain
  adtcore:responsible="USER"
  adtcore:masterLanguage="EN"
  adtcore:masterSystem="S4B"
  adtcore:abapLanguageVersion="0"
  adtcore:name="ZTMP_D_INVTYPE"
  adtcore:type="DOMA/DD"
  adtcore:description="Tipo de factura"
  adtcore:language="EN"
  xmlns:doma="http://www.sap.com/dictionary/domain"
  xmlns:adtcore="http://www.sap.com/adt/core">

  <adtcore:packageRef adtcore:uri="/sap/bc/adt/packages/%24tmp"
    adtcore:type="DEVC/K" adtcore:name="$TMP"/>

  <doma:content>
    <doma:typeInformation>
      <doma:datatype>CHAR</doma:datatype>
      <doma:length>000002</doma:length>
      <doma:decimals>000000</doma:decimals>
    </doma:typeInformation>
    <doma:outputInformation>
      <doma:length>000002</doma:length>
      <doma:style>00</doma:style>
      <doma:conversionExit/>
      <doma:signExists>false</doma:signExists>
      <doma:lowercase>false</doma:lowercase>
      <doma:ampmFormat>false</doma:ampmFormat>
    </doma:outputInformation>
    <doma:valueInformation>
      <doma:valueTableRef/>
      <doma:appendExists>false</doma:appendExists>
      <doma:fixValues>
        <doma:fixValue>
          <doma:position>0001</doma:position>
          <doma:low>E</doma:low>
          <doma:high/>
          <doma:text>Estándar</doma:text>
        </doma:fixValue>
        <doma:fixValue>
          <doma:position>0002</doma:position>
          <doma:low>A</doma:low>
          <doma:high/>
          <doma:text>Abono</doma:text>
        </doma:fixValue>
        <doma:fixValue>
          <doma:position>0003</doma:position>
          <doma:low>AN</doma:low>
          <doma:high/>
          <doma:text>Anticipo</doma:text>
        </doma:fixValue>
        <doma:fixValue>
          <doma:position>0004</doma:position>
          <doma:low>HI</doma:low>
          <doma:high/>
          <doma:text>Hito contractual</doma:text>
        </doma:fixValue>
      </doma:fixValues>
    </doma:valueInformation>
  </doma:content>
</doma:domain>
```

---

## Common data types reference

| ABAP Type | Description                       | Example length |
|-----------|-----------------------------------|----------------|
| `CHAR`    | Character string                  | 000001–001333  |
| `NUMC`    | Numeric text (digits only)        | 000001–000255  |
| `DATS`    | Date (YYYYMMDD)                   | 000008         |
| `TIMS`    | Time (HHMMSS)                     | 000006         |
| `DEC`     | Packed decimal                    | 000001–000031  |
| `INT4`    | 4-byte integer                    | 000010         |
| `INT2`    | 2-byte integer                    | 000005         |
| `CURR`    | Currency amount (use with CUKY)   | 000013         |
| `QUAN`    | Quantity (use with UNIT)          | 000013         |
| `CLNT`    | Client (= CHAR 3, fixed)          | 000003         |
| `LANG`    | Language key (= CHAR 1)           | 000001         |

---

## Activation error troubleshooting

| Error message                            | Cause & fix                                                                                   |
|------------------------------------------|-----------------------------------------------------------------------------------------------|
| `Data type ' ' does not exist`           | `<doma:datatype>` is empty or `adtcore:description` is missing — add both before retrying    |
| `Not an ABAP object`                     | Wrong URL format passed to `abap_activate` — use the file URI `adt://.../.doma.xml`          |
| `Object locked by another user`          | Call `abap_unlock` first, or wait for the lock to expire                                      |
