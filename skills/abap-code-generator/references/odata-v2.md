# OData V2 con SAP Gateway (SEGW)

Guía para crear y exponer servicios OData V2 desde ABAP usando la transacción SEGW.

## Estructura de un proyecto SEGW

```
Proyecto SEGW (ZGW_<NOMBRE>)
├── Data Model
│   ├── Entity Types        ← Equivalen a entidades (tablas/CDS)
│   ├── Associations        ← Relaciones 1:N, N:M entre entity types
│   └── Entity Sets         ← Colecciones (ListXxx, XxxSet)
├── Service Implementation  ← Clase ABAP generada: ZCL_<NOMBRE>_DPC_EXT
└── Runtime Artifacts       ← AutoGenerados; NO editar directamente
```

## Flujo de creación (paso a paso)

### 1. Crear el proyecto en SEGW

Usar `abap_createobject` con tipo `IWSV` o, si el sistema lo soporta, guiar al usuario a SEGW manualmente y luego trabajar sobre la clase generada.

### 2. Definir Entity Types

Cada Entity Type mapea a un objeto de negocio SAP. Atributos mínimos:

```
Entity Type: SalesOrder
Key properties: SalesOrderId (Edm.String, length:10)
Properties:
  - CustomerName  (Edm.String)
  - NetAmount     (Edm.Decimal, precision:16, scale:2)
  - CreatedAt     (Edm.DateTime)
  - Status        (Edm.String, length:1)
```

### 3. Implementar la clase DPC_EXT

SEGW genera automáticamente:
- `ZCL_<NOMBRE>_MPC` — Model Provider Class (NO editar)
- `ZCL_<NOMBRE>_DPC` — Data Provider Class (NO editar)
- `ZCL_<NOMBRE>_MPC_EXT` — Extensión del modelo (editar si se añaden navegaciones)
- `ZCL_<NOMBRE>_DPC_EXT` — **Aquí va toda la lógica.** Redefinir métodos.

### 4. Métodos a redefinir en DPC_EXT

| Operación OData | Método a redefinir en DPC_EXT |
|---|---|
| GET lista | `<ENTITYSET>_GET_ENTITYSET` |
| GET entidad | `<ENTITYSET>_GET_ENTITY` |
| POST (crear) | `<ENTITYSET>_CREATE_ENTITY` |
| PUT/PATCH (actualizar) | `<ENTITYSET>_UPDATE_ENTITY` |
| DELETE | `<ENTITYSET>_DELETE_ENTITY` |
| Function Import | `/<NOMBRE_FI>_FI_FUNC_IMPORT` |

### 5. Plantilla: GET_ENTITYSET (lectura de lista)

```abap
METHOD salesorderset_get_entityset.

  DATA: lt_orders TYPE TABLE OF zsalesorder,
        ls_order  TYPE zsalesorder,
        ls_entity TYPE bapi_epm_so_header.

  " Leer datos de la tabla/BAPI/CDS
  SELECT * FROM zsalesorder
    INTO TABLE @lt_orders
    UP TO 100 ROWS.

  " Mapear a entity type OData
  LOOP AT lt_orders INTO ls_order.
    APPEND INITIAL LINE TO et_entityset ASSIGNING FIELD-SYMBOL(<ls_result>).
    <ls_result>-salesorderid  = ls_order-vbeln.
    <ls_result>-customername  = ls_order-kunnr.
    <ls_result>-netamount     = ls_order-netwr.
    <ls_result>-createdat     = ls_order-erdat.
    <ls_result>-status        = ls_order-status.
  ENDLOOP.

ENDMETHOD.
```

### 6. Plantilla: CREATE_ENTITY

```abap
METHOD salesorderset_create_entity.

  DATA: ls_input  TYPE zcl_<nombre>_mpc=>ts_salesorder,
        ls_result TYPE zcl_<nombre>_mpc=>ts_salesorder.

  " Leer datos de entrada del request
  io_data_provider->read_entry_data( IMPORTING es_data = ls_input ).

  " Validar
  IF ls_input-customername IS INITIAL.
    RAISE EXCEPTION TYPE /iwbep/cx_mgw_busi_exception
      EXPORTING
        textid  = /iwbep/cx_mgw_busi_exception=>business_error
        message = 'CustomerName es obligatorio'.
  ENDIF.

  " Persistir (BAPI / INSERT directo)
  CALL FUNCTION 'BAPI_SALESORDER_CREATEFROMDAT2'
    EXPORTING
      ...

  er_entity = ls_result.

ENDMETHOD.
```

## Registro y activación del servicio

Después de generar los artefactos en SEGW:

1. **SEGW → Generate → generar artefactos de runtime.**
2. Ejecutar transacción `/IWFND/MAINT_SERVICE`:
   - Añadir servicio → buscar nombre técnico `Z<NOMBRE>_SRV`.
   - Asignar a Gateway Hub.
3. Test en `/IWFND/GW_CLIENT` o navegador: `http://<host>/sap/opu/odata/sap/Z<NOMBRE>_SRV/`.

## Manejo de errores (OBLIGATORIO)

Usar siempre las excepciones Gateway estándar:

```abap
" Error de negocio (400)
RAISE EXCEPTION TYPE /iwbep/cx_mgw_busi_exception
  EXPORTING
    textid  = /iwbep/cx_mgw_busi_exception=>business_error
    message = 'Mensaje de error'.

" No encontrado (404)
RAISE EXCEPTION TYPE /iwbep/cx_mgw_busi_exception
  EXPORTING
    textid  = /iwbep/cx_mgw_busi_exception=>resource_not_found.

" Error técnico (500)
RAISE EXCEPTION TYPE /iwbep/cx_mgw_tech_exception
  EXPORTING
    textid = /iwbep/cx_mgw_tech_exception=>server_error.
```

## Function Imports

Permiten exponer operaciones que no son CRUD estándar (búsquedas complejas, acciones de negocio).

### Definir en SEGW

```
Function Import: CalculateDiscount
HTTP Method: POST
Return Type: DiscountResult (Entity Type)
Parameters:
  - OrderId (Edm.String, In)
  - Percentage (Edm.Decimal, In)
```

### Implementar en DPC_EXT

```abap
METHOD /iwbep/if_mgw_appl_srv_runtime~execute_action.

  CASE iv_action_name.
    WHEN 'CalculateDiscount'.
      DATA: lv_order_id   TYPE string,
            lv_percentage TYPE p DECIMALS 2.

      " Leer parámetros
      io_parameter_provider->get_data_provider( )->read_entry_data(
        IMPORTING es_data = DATA(ls_params) ).

      lv_order_id   = ls_params-orderid.
      lv_percentage = ls_params-percentage.

      " Lógica de negocio
      " ...

      " Respuesta
      copy_data_to_ref(
        EXPORTING is_data = ls_result
        CHANGING  cr_data = ro_data_provider ).

  ENDCASE.

ENDMETHOD.
```

## Filtros y paginación ($filter, $top, $skip)

```abap
METHOD salesorderset_get_entityset.

  " Leer opciones OData del request
  DATA(lo_filter) = io_tech_request_context->get_filter( ).
  DATA(lt_filter_select) = lo_filter->get_filter_select_options( ).

  " Paginación
  DATA(lv_top)  = io_tech_request_context->get_top( ).
  DATA(lv_skip) = io_tech_request_context->get_skip( ).

  " Mapear filtros a SELECT WHERE
  " (usar /iwbep/cl_sbnd_dynamic_query para filtros dinámicos)

ENDMETHOD.
```

## Convenciones de nombres

| Objeto | Patrón |
|---|---|
| Proyecto SEGW | `ZGW_<MODULO>` |
| Entity Type | PascalCase singular: `SalesOrder` |
| Entity Set | PascalCase plural: `SalesOrderSet` |
| Association | `A_<Origen>_To_<Destino>` |
| Function Import | PascalCase verbo+nombre: `CalculateDiscount` |
| DPC_EXT class | Autogenerada: `ZCL_<PROYECTO>_DPC_EXT` |
