---
name: abap-services-designer
description: "Genera especificacion de servicios OData ABAP (SEGW V2 y RAP V4) a partir del modelo de datos ABAP. Cubre EntitySets, Associations, NavigationProperties, FunctionImports (V2), Actions y Functions (RAP V4), objetos de autorizacion ABAP y contratos de error OData. Usar cuando se necesite crear design/03_abap_services.md a partir de design/01 y design/02_abap_data_model.md, manteniendo consistencia entre el modelo DDIC/CDS y los servicios expuestos."
---

# ABAP Services Designer

Generar especificacion de servicios orientada a SAP ABAP, enfocada en exposicion OData V2 (SEGW) y V4 (RAP), EntitySets, operaciones CRUD, FunctionImports, Actions, Functions, autorizacion ABAP y contratos de error OData.

## Objetivo del skill

- Definir contratos de servicios OData consistentes para implementacion ABAP.
- Derivar servicios expuestos desde `design/02_abap_data_model.md` sin duplicar el modelo de datos.
- Distinguir y documentar correctamente la capa SEGW (OData V2) o RAP (OData V4) segun la decision de diseño de `design/01`.
- Estandarizar EntitySets, Associations, NavigationProperties, FunctionImports/Actions/Functions, parametros OData, autorizacion y modelo de error.
- Dejar el documento listo para implementacion en `SEGW` (transaccion) o en `Behavior Definition/Service Binding` (RAP).

## Prerrequisitos

Imprescindibles:

- `design/01_technical_design.md`
- `design/02_abap_data_model.md`
- `analisis/03_requerimientos_funcionales.md`
- `analisis/10_interfaces_usuario.md`

Recomendados:

- `analisis/05_historias_usuario.md`
- `analisis/06_casos_uso.md`
- `analisis/08_integraciones.md`
- `analisis/09_diagramas_estados.md`
- `analisis/12_prototipos_interfaz.md`
- backlog del modulo si existe

## Fuente de verdad

- Fuente primaria: `design/02_abap_data_model.md` mas RFs, pantallas y diseño tecnico.
- Protocolo OData (V2 o V4) determinado en `design/01_technical_design.md`. Si no esta declarado, inferir: RAP CDS Views root → V4; SEGW proyecto Z → V2. No mezclar patrones para el mismo objeto de negocio.
- Si hay dudas sobre CDS Views, anotaciones OData, RAP Behavior o SEGW, consultar:
  - `mcp_mcp-sap-docs_search`, `mcp_mcp-sap-docs_sap_search_objects`
  - `mcp_mcp-abap_search`

## Modos de operacion

| Modo | Entrada | Salida |
|------|---------|--------|
| catalog | design/01 + design/02 + RFs | catalogo de servicios OData ABAP |
| contracts | design/02 + RFs + interfaces | detalle de EntitySets, operaciones y contratos OData |
| operations | RFs + casos de uso + estados | FunctionImports (V2) / Actions y Functions (V4 RAP) |
| auth | design/02 + actores + backlog si existe | objetos de autorizacion ABAP por operacion |
| filters-errors | interfaces + RFs + estados | parametros OData, paginacion, expand y modelo de error |
| ui5-consumption | design/03 draft + interfaces | patron de consumo SAPUI5 por EntitySet |
| all | todas las anteriores | documento completo `design/03_abap_services.md` |

Ver detalle de secciones, orden y artefactos en [references/mode-artifacts.md](references/mode-artifacts.md).

## Estructura de salida

Generar `design/03_abap_services.md` con:

### 1. Convenciones globales

- Protocolo: OData V2 (SEGW) o V4 (RAP) segun `design/01`
- URL base V2: `/sap/opu/odata/<namespace>/<SERVICE_NAME>/`
- URL base V4: `/sap/opu/odata4/<namespace>/<SERVICE_NAME>/`
- Autenticacion: SAP Logon / SSO (SAML2); en ABAP usar `AUTHORITY-CHECK OBJECT` antes de logica de negocio
- Mock SAPUI5: `sap.ui.core.util.MockServer` con `metadata.xml` + fixtures JSON en `webapp/localService/mockdata/`
- Paginacion OData: `$top` / `$skip` (V2) o `$top` / `$skip` + `$count=true` (V4)
- Filtros: `$filter` con operadores OData (`eq`, `ne`, `gt`, `ge`, `lt`, `le`, `substringof` V2 / `contains` V4)
- Ordenamiento: `$orderby=<campo> asc|desc`
- Expansion: `$expand=<NavigationProperty>` para entidades relacionadas
- Modelo de error OData: `{ "error": { "code": "...", "message": { "lang": "es", "value": "..." }, "innererror": {...} } }`
- Nombres: EntitySets en PascalCase + sufijo `Set` (ej. `FacturaSet`), NavigationProperties en PascalCase, FunctionImport/Action en PascalCase (ej. `ValidarFactura`)

### 2. Catalogo de Servicios

| Servicio ABAP | CDS / SEGW Proyecto | Modulo | Version OData | Descripcion |
|---------------|---------------------|--------|---------------|-------------|
| ZFACT_SRV | Z_FACT_SV_FACTURA (RAP) | Facturacion | V4 | Gestion de facturas |

### 3. Detalle por Servicio

Para cada servicio:

```markdown
### ZFACT_SRV

**CDS Service Definition / SEGW Proyecto:** Z_FACT_SV_FACTURA

**Namespace / Service Binding:** Z_FACT_UI_FACTURA (OData V4) o /sap/opu/odata/sap/ZFACT_SRV (V2)

**EntitySets:**
| EntitySet | CDS View / SEGW Entity | Operaciones | Clave | Descripcion |
|-----------|------------------------|-------------|-------|-------------|
| FacturaSet | Z_FACT_C_FACTURA | C, R, U, D | Bukrs, Lifnr, Bldat | Cabecera de factura |
| FacturaPosSet | Z_FACT_C_FACTURA_POS | R | Bukrs, Lifnr, Bldat, Buzei | Posiciones de factura |

**Associations y NavigationProperties:**
| Nombre | De | A | Cardinalidad | Descripcion |
|--------|----|---|--------------|-------------|
| ToPosiciones | FacturaSet | FacturaPosSet | 1..N | Posiciones de la factura |

**FunctionImports (V2) / Actions y Functions (V4 RAP):**
| Nombre | Tipo | Bound | HTTP | Entrada | Salida | Descripcion |
|--------|------|-------|------|---------|--------|-------------|
| ValidarFactura | Action | si | POST | BelKrs, Belnr | ReturnMessage | Valida datos de cabecera |

**Parametros OData soportados:**
| Parametro | EntitySet | Campos | Notas |
|-----------|-----------|--------|-------|
| $filter | FacturaSet | Bukrs, Lifnr, Bldat | Operadores: eq, ge, le |
| $expand | FacturaSet | ToPosiciones | Profundidad max: 1 |
| $top / $skip | FacturaSet | - | Max $top: 1000 |

**Objetos de autorizacion:**
| Operacion | Objeto Auth | Campo | Valor |
|-----------|-------------|-------|-------|
| CREATE | Z_FACT_AUTH | ACTVT | 01 |
| DISPLAY | Z_FACT_AUTH | ACTVT | 03 |

**Notas del contrato:**
- Restricciones por estado: solo facturas en estado BORRADOR son editables
- Side effects: al ValidarFactura se actualiza el campo ZSTATUS
- Errores documentados: ZFACT_E001 (importe negativo), ZFACT_E002 (proveedor bloqueado)
```

### 4. Matriz Servicio-RF

| Servicio | EntitySet / Operacion | FunctionImport / Action | RF Asociado | Descripcion |
|----------|-----------------------|-------------------------|-------------|-------------|
| ZFACT_SRV | FacturaSet / READ | - | RF-001 | Consulta de facturas |

### 5. Permisos y Objetos de Autorizacion ABAP

| Servicio | Objeto Auth | Campo ACTVT | Roles IAM / Perfiles | Descripcion |
|----------|-------------|-------------|----------------------|-------------|
| ZFACT_SRV | Z_FACT_AUTH | 01,02,03,06 | Z_ROLE_FACTURA | Control de acceso por operacion |

### 6. Parametros OData y Modelo de Error

| Servicio | Parametro / Codigo Error | Definicion |
|----------|--------------------------|------------|
| ZFACT_SRV | `$top` | max 1000 |
| ZFACT_SRV | ZFACT_E001 | importe negativo, HTTP 400 |

### 7. Patron de Consumo SAPUI5

Por cada servicio documentar:
- Tipo de modelo: `sap.ui.model.odata.v2.ODataModel` o `v4.ODataModel`
- URL del servicio en `manifest.json` (seccion `sap.app.dataSources`)
- Binding de EntitySet por vista (`/FacturaSet({Bukrs},{Belnr},{Gjahr})`)
- Llamada a FunctionImport / Action desde controlador
- Manejo de error OData (`messageModel`, `sap.m.MessageBox`)

## Proceso

1. Leer `design/01`, `design/02`, RFs y pantallas.
2. Determinar protocolo OData (V2 SEGW o V4 RAP) por modulo o servicio.
3. Identificar CDS Views (RAP) o entidades SEGW que seran EntitySets.
4. Identificar Associations/NavigationProperties entre entidades.
5. Detectar operaciones de negocio que requieren FunctionImport (V2) o Action/Function (V4).
6. Documentar parametros OData solicitados desde las pantallas SAPUI5.
7. Definir objetos de autorizacion ABAP por operacion.
8. Trazar cada EntitySet y operacion con RFs y casos de uso.
9. Documentar errores OData especificos que DPC_EXT o el Behavior Implementation puede retornar.
10. Generar `design/03_abap_services.md` de forma incremental.

## Guardrails criticos

- No mezclar SEGW y RAP para el mismo objeto de negocio dentro del mismo modulo.
- No exponer tablas DDIC directamente como EntitySets; derivar siempre desde CDS View.
- No usar `GET_ENTITY` / `GET_ENTITYSET` custom (DPC_EXT) cuando RAP Behavior cubre la operacion.
- No omitir `AUTHORITY-CHECK` en operaciones de escritura o datos sensibles.
- No duplicar atributos del modelo de datos; referenciar `design/02_abap_data_model.md`.
- No documentar navegacion profunda sin advertir el impacto de rendimiento en ABAP.
- No usar `action` (V4) para operaciones de solo lectura; usar `function` cuando no hay side effects.

Leer [references/guardrails.md](references/guardrails.md) para anti-patrones, decisiones de diseño y checklist final.

## Restricciones

- No generar codigo ABAP completo (DPC_EXT, Behavior Implementation, CDS texto).
- No definir mock data ni fixtures SAPUI5 fuera de la seccion de patron de consumo.
- No inventar objetos de autorizacion, EntitySets ni FunctionImports fuera del modelo y backlog.
- No duplicar especificaciones ya documentadas en `design/02_abap_data_model.md`.

## Escritura incremental

Para documentos extensos:

1. Crear encabezado, convenciones globales y catalogo.
2. Añadir detalle de servicios en bloques de 2-3 servicios.
3. Añadir matriz servicio-RF.
4. Añadir secciones de autorizacion, filtros, errores y patron SAPUI5.

No devolver el contenido completo del documento en la respuesta final. Solo un resumen cuantitativo.

## Criterio de finalizacion

El trabajo se considera completado cuando:

✅ `design/03_abap_services.md` esta generado  
✅ Cada servicio referencia CDS Views o entidades SEGW del modelo ABAP  
✅ FunctionImports (V2) y Actions/Functions (V4) quedan diferenciados correctamente  
✅ Los objetos de autorizacion ABAP quedan explicitados por operacion  
✅ El patron de consumo SAPUI5 esta documentado por servicio  
✅ La matriz servicio-RF cubre las operaciones relevantes  

## Salida esperada del skill

```
Archivo design/03_abap_services.md generado:
- Servicios: X
- EntitySets: Y
- FunctionImports / Actions: Z
- Objetos de autorizacion: A
- Errores OData documentados: E
```
