# Modes And Artifacts

Usar esta referencia para decidir que construir en cada modo de abap-services-designer.

## Orden recomendado

1. `catalog`
2. `contracts`
3. `operations`
4. `auth`
5. `filters-errors`
6. `ui5-consumption`

---

## Modo `catalog`

Entradas:

- `design/01_technical_design.md`
- `design/02_abap_data_model.md`
- RFs

Salida:

- secciones 1 y 2 del documento

Incluye:

- convencion de URL y protocolo OData (V2/V4) por modulo
- catalogo de servicios con CDS Service Definition / SEGW proyecto
- modulo, version OData y descripcion breve de cada servicio

---

## Modo `contracts`

Entradas:

- `design/02_abap_data_model.md`
- RFs
- interfaces UI5

Salida:

- seccion 3 del documento

Incluye:

- EntitySets por servicio, incluyendo CDS View o entidad SEGW origen
- operaciones CRUD habilitadas por EntitySet
- Associations y NavigationProperties
- campos clave por EntitySet
- notas de contrato: restricciones por estado, side effects

---

## Modo `operations`

Entradas:

- RFs
- casos de uso
- diagramas de estado

Salida:

- parte de seccion 3 (bloque FunctionImports/Actions) y seccion 4

Incluye para cada operacion:

**V2 - FunctionImport SEGW:**
  - nombre, metodo HTTP (GET/POST)
  - parametros de entrada (nombre, tipo ABAP, obligatorio)
  - tipo de retorno (EntityType o primitivo)
  - descripcion de logica de negocio
  - errores esperados

**V4 - RAP Action / Function:**
  - nombre, tipo (action para side effects / function para lectura)
  - bound (asociada a instancia) o unbound (nivel servicio)
  - parametros de entrada y salida
  - precondiciones de estado
  - descripcion de logica de negocio
  - errores esperados

---

## Modo `auth`

Entradas:

- `design/02_abap_data_model.md`
- actores y roles del analisis
- backlog si existe

Salida:

- seccion 5 del documento

Incluye:

- objeto de autorizacion ABAP por servicio y operacion
- campo ACTVT y valores permitidos (01 crear, 02 cambiar, 03 visualizar, 06 borrar)
- campos adicionales del objeto si aplica (por sociedad, tipo de documento, etc.)
- roles IAM o perfiles de autorizacion asociados
- nota sobre AUTHORITY-CHECK en DPC_EXT o Behavior Implementation

---

## Modo `filters-errors`

Entradas:

- interfaces UI5
- RFs
- diagramas de estado

Salida:

- seccion 6 del documento

Incluye:

- parametros `$filter` habilitados por EntitySet con campos y operadores soportados
- profundidad maxima de `$expand` por EntitySet
- limites de `$top` sugeridos
- `$orderby` por defecto si el contrato depende de ello
- codigos de error OData funcionales: codigo Z, mensaje, HTTP status, contexto
- distincion entre error de validacion negocio, autorizacion, conflicto de estado y error tecnico

---

## Modo `ui5-consumption`

Entradas:

- borrador de `design/03_abap_services.md` (secciones anteriores)
- interfaces UI5 (`analisis/10`)

Salida:

- seccion 7 del documento

Incluye por servicio / EntitySet:

- entrada en `manifest.json` seccion `sap.app.dataSources` (nombre, uri, tipo ODataV2/V4)
- entrada en `manifest.json` seccion `sap.ui5.models` (tipo de modelo, dataSource, settings)
- patron de binding de lista: `items="{/FacturaSet}"`
- patron de binding de detalle: `bindElement("/FacturaSet(Bukrs='0001',Belnr='...')")`
- llamada a FunctionImport (V2): `oModel.callFunction("/ValidarFactura", { method: "POST", urlParameters: {...} })`
- llamada a Action (V4): `oModel.bindContext("/ZFACT_SRV.ValidarFactura(...)")` o accion bound en `oContext.execute()`
- manejo de error OData: `sap.ui.model.odata.v2.ODataModel` mensajes via `sap.m.MessageBox`, MessageManager
- manejo de error OData V4: `oModel.attachMessageChange`, `sap.m.MessageView`
