# CDS Views y RAP (RESTful Application Programming Model)

Guía para crear CDS Views y Business Objects RAP que exponen OData V4 para SAPUI5/Fiori Elements.

## Arquitectura RAP

| Objeto | Prefijo | Descripción |
|---|---|---|
| Tabla persistente | `Z<MOD>_T_` | Datos persistentes (tabla transparente DDIC) |
| Root CDS View | `Z<MOD>_R_` | SELECT sobre tabla, campos base, asociaciones |
| Projection CDS View | `Z<MOD>_C_` | Expone campos para la UI, `@UI` annotations |
| Behavior Definition | (misma que Root) | CRUD, validaciones, determinaciones, acciones |
| Behavior Implementation | `Z<MOD>_BP_` | Clase global + clases locales `LHC_*` / `LSC_*` |
| Service Definition | `Z<MOD>_SV_` | Expone entidades del servicio |
| Service Binding | `Z<MOD>_UI_` / `Z<MOD>_API_` | Protocolo OData V2/V4, UI o API |
| Metadata Extension | `Z<MOD>_C_..._M` | Anotaciones UI separadas de la CDS |

**Flujo de activación obligatorio (cada fase debe estar ACTIVA antes de la siguiente):**

```
Z<MOD>_T_Entity  (Tabla persistente)
        │ activa antes de ↓
        ▼
Z<MOD>_R_Entity  (Root CDS View)
        │ activa antes de ↓
        ▼
Z<MOD>_C_Entity  (Projection CDS View)
        │ activa antes de ↓
        ▼
BDEF Z<MOD>_R_Entity
        │ activa antes de ↓
        ▼
Z<MOD>_BP_Entity  (Behavior Implementation)
        │ activa antes de ↓
        ▼
Z<MOD>_SV_Entity_UI  (Service Definition)
        │ activa antes de ↓
        ▼
Z<MOD>_UI_Entity_O4  (Service Binding) → Publicar
```

---

## CDS Views

### Tipo: Root (`Z<MOD>_R_`)

Selecciona directamente sobre la tabla persistente. Contiene campos base y asociaciones.

```abap
@AbapCatalog.viewEnhancementCategory: [#NONE]
@AccessControl.authorizationCheck: #NOT_REQUIRED
@EndUserText.label: 'Root View - Pedidos de Venta'
@Metadata.ignorePropagatedAnnotations: true

define root view entity Z<MOD>_R_SalesOrder
  as select from z<mod>_t_salesorder as Header
  association [0..*] to Z<MOD>_R_SalesOrderItem as _Items
    on $projection.SalesOrderId = _Items.SalesOrderId
{
  key Header.id           as SalesOrderId,
      Header.customer_id  as CustomerId,
      Header.net_amount   as NetAmount,
      Header.currency     as Currency,
      Header.created_at   as CreatedAt,
      Header.changed_at   as ChangedAt,

      /* Asociaciones */
      _Items
}
```

### Tipo: Projection (`Z<MOD>_C_`)

Expone los campos de la Root View hacia la UI. Permite `@Metadata.allowExtensions: true` para externalizar anotaciones a un Metadata Extension (`Z<MOD>_C_SalesOrder_M`).

```abap
@EndUserText.label: 'Projection View - Pedidos de Venta'
@AccessControl.authorizationCheck: #NOT_REQUIRED
@Metadata.allowExtensions: true

@Search.searchable: true

define root view entity Z<MOD>_C_SalesOrder
  provider contract transactional_query
  as projection on Z<MOD>_R_SalesOrder
{

  @Search.defaultSearchElement: true
  @UI.lineItem: [{ position: 10 }]
  @UI.identification: [{ position: 10 }]
  key SalesOrderId,

  @UI.lineItem: [{ position: 20 }]
  @ObjectModel.text.element: ['CustomerName']
  CustomerId,

  CustomerName,

  @UI.lineItem: [{ position: 30 }]
  @Semantics.amount.currencyCode: 'Currency'
  NetAmount,

  @Semantics.currencyCode: true
  Currency,

  @UI.lineItem: [{ position: 40 }]
  CreatedAt,

  /* Composición */
  _Items : redirected to composition child Z<MOD>_C_SalesOrderItem
}
```

### Anotaciones UI más usadas

```abap
" Cabecera de página (Fiori Elements)
@UI.headerInfo: { typeName: 'Pedido', typeNamePlural: 'Pedidos',
                  title.value: 'SalesOrderId', description.value: 'CustomerName' }

" Campo en lista y formulario
@UI.lineItem:       [{ position: 10 }]
@UI.identification: [{ position: 10 }]
@UI.selectionField: [{ position: 10 }]

" Faceta en Object Page
@UI.facet: [{ id: 'GeneralInfo', purpose: #STANDARD, type: #IDENTIFICATION_REFERENCE,
              label: 'Información General', position: 10 }]

" Campo de texto de una FK
@ObjectModel.text.element: ['CustomerName']

" Acción en la UI
@UI.lineItem: [{ type: #FOR_ACTION, dataAction: 'approve', label: 'Aprobar' }]
```

---

## Behavior Definition (BDEF)

### Managed (preferido para nuevos desarrollos)

```abap
managed implementation in class z<mod>_bp_salesorder unique;
strict ( 2 );

define behavior for Z<MOD>_R_SalesOrder alias SalesOrder
persistent table z<mod>_t_salesorder
lock master
authorization master ( instance )
etag master ChangedAt
{
  -- Operaciones estándar CRUD
  create;
  update;
  delete;

  -- Campos no editables por el usuario
  field ( readonly ) SalesOrderId, CreatedAt, ChangedAt;

  -- Campo obligatorio
  field ( mandatory ) CustomerId, NetAmount;

  -- Numeración automática de la clave
  determination SetSalesOrderId on modify { create; }

  -- Validaciones
  validation ValidateCustomer on save { create; update; }
  validation ValidateAmount    on save { create; update; }

  -- Acciones de negocio
  action approve result [1] $self;
  action reject  result [1] $self;

  -- Mapping tabla ↔ CDS
  mapping for z<mod>_t_salesorder
  {
    SalesOrderId = id;
    CustomerId   = customer_id;
    NetAmount    = net_amount;
    Currency     = currency;
    CreatedAt    = created_at;
    ChangedAt    = changed_at;
  }

  -- Composición con ítem
  association _Items { create; with draft; }
}

define behavior for Z<MOD>_R_SalesOrderItem alias Item
persistent table z<mod>_t_salesorderitem
lock dependent by _SalesOrder
authorization dependent by _SalesOrder
etag master ChangedAt
{
  update;
  delete;
  field ( readonly ) SalesOrderId, ItemId;

  association _SalesOrder { }
}
```

### Unmanaged (para lógica compleja / integración con BAPIs)

```abap
unmanaged implementation in class z<mod>_bp_salesorder unique;

define behavior for Z<MOD>_R_SalesOrder alias SalesOrder
  lock master
  authorization master ( instance )
{
  create;
  update;
  delete;

  action approve result [1] $self;
}
```

---

## Behavior Implementation (BDEF class)

### Plantilla: clase de implementación

> **CRÍTICO:** Editar siempre el fichero `clas.locals_imp.abap` de la clase BP para las clases locales. Nunca editar `clas.locals_def.abap` (auto-generado).

**Clase global (behavior pool — vacía):**
```abap
CLASS Z<MOD>_BP_SalesOrder DEFINITION
  PUBLIC ABSTRACT FINAL
  FOR BEHAVIOR OF Z<MOD>_R_SalesOrder.
ENDCLASS.

CLASS Z<MOD>_BP_SalesOrder IMPLEMENTATION.
ENDCLASS.
```

**Clases locales en `clas.locals_imp.abap`:**
```abap
" ──────────────────────────────────────────────
" LHC (Local Handler Class) — Managed scenario
" ──────────────────────────────────────────────
CLASS LHC_SalesOrder DEFINITION INHERITING FROM cl_abap_behavior_handler.
  PRIVATE SECTION.
    METHODS:
      " Validaciones
      validatecustomer FOR VALIDATE ON SAVE
        IMPORTING keys FOR SalesOrder~ValidateCustomer,
      validateamount   FOR VALIDATE ON SAVE
        IMPORTING keys FOR SalesOrder~ValidateAmount,
      " Determinaciones
      setsalesorderid  FOR DETERMINE ON MODIFY
        IMPORTING keys FOR SalesOrder~SetSalesOrderId,
      " Acciones
      approve FOR MODIFY
        IMPORTING keys FOR ACTION SalesOrder~approve RESULT result.
ENDCLASS.

CLASS LHC_SalesOrder IMPLEMENTATION.

  METHOD validatecustomer.
    READ ENTITIES OF Z<MOD>_R_SalesOrder IN LOCAL MODE
      ENTITY SalesOrder
      FIELDS ( CustomerId )
      WITH CORRESPONDING #( keys )
      RESULT DATA(lt_orders).

    LOOP AT lt_orders ASSIGNING FIELD-SYMBOL(<order>).
      IF <order>-CustomerId IS INITIAL.
        APPEND VALUE #( %tky = <order>-%tky ) TO failed-SalesOrder.
        APPEND VALUE #( %tky = <order>-%tky
                        %msg = new_message_with_text(
                                 severity = if_abap_behv_message=>severity-error
                                 text     = 'Cliente es obligatorio' ) )
               TO reported-SalesOrder.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

  METHOD setsalesorderid.
    " Para unmanaged: generar UUID o número de rango
    MODIFY ENTITIES OF Z<MOD>_R_SalesOrder IN LOCAL MODE
      ENTITY SalesOrder
      UPDATE FIELDS ( SalesOrderId )
      WITH VALUE #( FOR key IN keys
                    ( %tky        = key-%tky
                      SalesOrderId = cl_system_uuid=>create_uuid_x16_static( ) ) ).
  ENDMETHOD.

  METHOD approve.
    MODIFY ENTITIES OF Z<MOD>_R_SalesOrder IN LOCAL MODE
      ENTITY SalesOrder
      UPDATE FIELDS ( Status )
      WITH VALUE #( FOR key IN keys ( %tky   = key-%tky
                                      Status = 'A' ) )
      REPORTED DATA(lt_reported)
      FAILED   DATA(lt_failed).
    reported = CORRESPONDING #( lt_reported ).
    failed   = CORRESPONDING #( lt_failed ).
  ENDMETHOD.

ENDCLASS.

" ──────────────────────────────────────────────
" LSC (Local Saver Class) — SOLO para Unmanaged
" ──────────────────────────────────────────────
CLASS LSC_SalesOrder DEFINITION INHERITING FROM cl_abap_behavior_saver.
  PROTECTED SECTION.
    METHODS finalize          REDEFINITION.
    METHODS check_before_save REDEFINITION.
    METHODS save              REDEFINITION.
ENDCLASS.

CLASS LSC_SalesOrder IMPLEMENTATION.
  METHOD save.
    " INSERT/UPDATE/DELETE sobre z<mod>_t_salesorder
  ENDMETHOD.
  METHOD finalize.          ENDMETHOD.
  METHOD check_before_save. ENDMETHOD.
ENDCLASS.
```

---

## Service Definition y Service Binding

### Service Definition

Nombre: `Z<MOD>_SV_SalesOrder_UI` | Tipo ADT: `SRVD/SV`

```abap
@EndUserText.label: 'Servicio UI - Pedidos de Venta'
define service Z<MOD>_SV_SalesOrder_UI {
  expose Z<MOD>_C_SalesOrder     as SalesOrder;
  expose Z<MOD>_C_SalesOrderItem as SalesOrderItem;
}
```

### Service Binding

Nombre: `Z<MOD>_UI_SalesOrder_O4` | Tipo ADT: `SRVB/SVB`

```
Name:               Z<MOD>_UI_SalesOrder_O4
Binding Type:       OData V4 - UI
Service Definition: Z<MOD>_SV_SalesOrder_UI
```

Activar → **Publish** en ADT → URL del servicio:
`/sap/opu/odata4/sap/z<mod>_ui_salesorder_o4/srvd/sap/z<mod>_sv_salesorder_ui/0001/`

> Para OData V2 usar tipo `OData V2 - UI` y sufijo `_O2`: `Z<MOD>_UI_SalesOrder_O2`.
> Para exposición como API (sin UI) usar prefijo `Z<MOD>_API_SalesOrder_O4`.

---

## Determinaciones y numeración

```abap
METHOD setsalesorderid.
  " Opción 1: UUID (recomendado para RAP)
  MODIFY ENTITIES OF Z<MOD>_R_SalesOrder IN LOCAL MODE
    ENTITY SalesOrder
    UPDATE FIELDS ( SalesOrderId )
    WITH VALUE #( FOR key IN keys
                  ( %tky        = key-%tky
                    SalesOrderId = cl_system_uuid=>create_uuid_x16_static( ) ) ).

  " Opción 2: Número de rango SAP (si se requiere número legible)
  DATA: lv_number TYPE vbeln_va.
  CALL FUNCTION 'NUMBER_GET_NEXT'
    EXPORTING
      nr_range_nr = '01'
      object      = 'Z_SO_NR'
    IMPORTING
      number      = lv_number.
  MODIFY ENTITIES OF Z<MOD>_R_SalesOrder IN LOCAL MODE
    ENTITY SalesOrder
    UPDATE FIELDS ( SalesOrderId )
    WITH VALUE #( FOR key IN keys ( %tky         = key-%tky
                                    SalesOrderId = lv_number ) ).
ENDMETHOD.
```

---

## Autorizaciones RAP

La lógica de autorización se implementa en la clase `Z<MOD>_BP_SalesOrder` (o en `LHC_SalesOrder`) redefiniendo el método `get_instance_authorizations`:

```abap
" En la BDEF:
authorization master ( instance )

" En LHC_SalesOrder (clas.locals_imp.abap) — añadir método:
METHOD get_instance_authorizations.
  LOOP AT requested_authorizations ASSIGNING FIELD-SYMBOL(<auth>).
    CASE <auth>-%field.
      WHEN if_abap_behv=>field-action-approve.
        " Verificar objeto de autorización
        AUTHORITY-CHECK OBJECT 'Z_SO_AUTH'
          FIELD 'ACTVT' ID '23'. " 23 = Release
        <auth>-%result = COND #( WHEN sy-subrc = 0
                                   THEN if_abap_behv=>auth-allowed
                                   ELSE if_abap_behv=>auth-unauthorized ).
    ENDCASE.
  ENDLOOP.
ENDMETHOD.
```

---

## Convenciones de nombres RAP

| Objeto | Patrón | Tipo ADT | Ejemplo |
|---|---|---|---|
| Tabla persistente | `Z<MOD>_T_<Entidad>` | `TABL/DT` | `ZSD_T_SalesOrder` |
| Tabla draft | `Z<MOD>_T_<Entidad>_D` | `TABL/DT` | `ZSD_T_SalesOrder_D` |
| Root CDS View | `Z<MOD>_R_<Entidad>` | `DDLS/DF` | `ZSD_R_SalesOrder` |
| Projection CDS View | `Z<MOD>_C_<Entidad>` | `DDLS/DF` | `ZSD_C_SalesOrder` |
| Behavior Definition | misma que la Root CDS | `BDEF/BDO` | `ZSD_R_SalesOrder` |
| Behavior Implementation (global) | `Z<MOD>_BP_<Entidad>` | `CLAS/OC` | `ZSD_BP_SalesOrder` |
| Local Handler Class | `LHC_<Entidad>` | (en `clas.locals_imp.abap`) | `LHC_SalesOrder` |
| Local Saver Class (unmanaged) | `LSC_<Entidad>` | (en `clas.locals_imp.abap`) | `LSC_SalesOrder` |
| Service Definition | `Z<MOD>_SV_<Entidad>_UI` | `SRVD/SV` | `ZSD_SV_SalesOrder_UI` |
| Service Binding OData V4 UI | `Z<MOD>_UI_<Entidad>_O4` | `SRVB/SVB` | `ZSD_UI_SalesOrder_O4` |
| Service Binding OData V2 UI | `Z<MOD>_UI_<Entidad>_O2` | `SRVB/SVB` | `ZSD_UI_SalesOrder_O2` |
| Service Binding API | `Z<MOD>_API_<Entidad>_O4` | `SRVB/SVB` | `ZSD_API_SalesOrder_O4` |
| Metadata Extension | `Z<MOD>_C_<Entidad>_M` | `DDLX/EX` | `ZSD_C_SalesOrder_M` |

> **CamelCase obligatorio** en el segmento de entidad: `SalesOrder`, no `SALESORDER` ni `salesorder`.
