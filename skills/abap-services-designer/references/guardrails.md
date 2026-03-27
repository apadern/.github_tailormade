# ABAP Services Design Guardrails

Usar esta referencia para mantener consistencia entre el modelo ABAP (DDIC/CDS) y los servicios OData que se exponen.

## 1. SEGW vs RAP: decision excluyente por objeto de negocio

- Si el backlog o `design/01` especifica RAP → documentar Service Definition (`SRVD`) y Service Binding (`SRVB`). No mezclar con SEGW.
- Si el backlog o `design/01` especifica SEGW → documentar el proyecto SEGW con sus EntityTypes, EntitySets y Associations. No mezclar con RAP.
- Si no esta declarado explicitamente, inferir por el modelo ABAP:
  - CDS View con anotacion `@AbapCatalog.sqlViewName` + `define root view entity` → RAP (V4)
  - Proyecto SEGW existente en el sistema → SEGW (V2)
- Documentar la decision tomada en la seccion de convenciones globales.

No hacer:

- No documentar un EntitySet SEGW y un RAP Action para la misma entidad de negocio.
- No asumir V4 solo porque la CDS View usa SELECT sin verificar si tiene Behavior Definition.

## 2. EntitySets y CDS Views

- Todo EntitySet debe corresponderse con una CDS View del modelo ABAP (`Z<MOD>_C_*` projection view en RAP, o entity type SEGW).
- No exponer tablas DDIC directamente como EntitySets; siempre pasar por CDS View para controlar proyeccion de campos.
- Si una pantalla necesita campos de varias tablas, documentar que la CDS View debe hacer el JOIN (no el frontend).
- Documentar la clave primaria del EntitySet con exactamente los mismos campos que la CDS View root.

No hacer:

- No proponer EntitySets de tablas Z sin la CDS View correspondiente en `design/02`.
- No omitir la clave primaria o documentarla con campos distintos a los del modelo ABAP.

## 3. Associations y NavigationProperties

- Documentar NavigationProperties solo cuando exista relacion modelada en la CDS View (asociacion CDS o SEGW).
- Indicar cardinalidad (1..1 o 1..N) y la clave de navegacion.
- Advertir si `$expand` sobre la NavigationProperty tiene impacto de rendimiento alto (joins con tablas de gran volumen).

No hacer:

- No inventar NavigationProperties no soportadas por el modelo CDS o SEGW.
- No dejar profundidad de `$expand` ilimitada sin justificacion.

## 4. FunctionImports (V2) y Actions/Functions (V4 RAP)

**V2 - FunctionImport:**
- Usar metodo `POST` para operaciones con side effects o mutacion de datos.
- Usar metodo `GET` para consultas, calculos o lecturas especiales sin side effects.
- Documentar nombre del metodo de DPC_EXT que implementara la logica (`<SERVICENAME>_DPC_EXT => <FUNCTIONIMPORT_NAME>`).

**V4 - RAP Action vs Function:**
- Usar `action` cuando hay side effects: cambio de estado, creacion de documentos, envio de mensajes.
- Usar `function` cuando solo hay lectura o calculo sin mutacion de persistencia.
- Documentar si es `bound` (sobre instancia del EntitySet) o `unbound` (a nivel servicio).
- Indicar precondiciones de estado relevantes (ej. "solo ejecutable en estado BORRADOR").

No hacer:

- No usar `action` para operaciones que solo leen datos.
- No dejar FunctionImports o Actions sin trazabilidad a un RF o caso de uso.
- No documentar operaciones custom cuando el CRUD estandar de RAP/SEGW cubre el caso.

## 5. Autorizacion ABAP

- Documentar el objeto de autorizacion ABAP por cada operacion sensible (CREATE, UPDATE, DELETE, y FunctionImports con side effects).
- Indicar los valores esperados del campo ACTVT: 01 (crear), 02 (cambiar), 03 (visualizar), 06 (borrar).
- Si el objeto de autorizacion tiene campos adicionales (sociedad, division, tipo de documento), documentarlos.
- Referenciar el AUTHORITY-CHECK que debe ejecutarse en DPC_EXT o en el Behavior Implementation antes de la logica de negocio.

No hacer:

- No omitir autorizacion en operaciones de escritura aunque sea prototipo.
- No usar el mismo objeto de autorizacion para todas las operaciones sin revisar si SAP tiene objeto estandar aplicable.
- No inventar nombres de objetos de autorizacion sin verificar si existe objeto SAP estandar (`S_BUPA_GRP`, `M_BEST_BSA`, `F_LFA1_BUK`, etc.).

## 6. Parametros OData y volumen

- Documentar `$filter` con campos y operadores soportados por la CDS View (no todos los campos son filtrables por defecto en RAP).
- En RAP: el campo debe tener la anotacion `@Search.searchable: true` o `@Consumption.filter.selectionType` para soportar `$filter`.
- En SEGW: el campo debe estar marcado como "Filterable" en el EntityType.
- Limitar `$top` a un maximo razonable (1000 por defecto para listas operativas; ajustar si hay riesgo de timeout ABAP).
- Documentar orden por defecto si el contrato UI depende de ello.

No hacer:

- No dejar paginacion ilimitada sin advertencia.
- No publicar campos no filtrables sin aclararlo.

## 7. Errores OData y side effects

- Documentar errores funcionales clave con: codigo Z, mensaje descriptivo, HTTP status y contexto de cuando ocurre.
- Distinguir: error de validacion de negocio (400), error de autorizacion (403), conflicto de estado (409), error tecnico ABAP (500).
- Documentar side effects de Actions: cambios de estado, audit logs, envio de IDocs, llamadas RFC/BAPI encadenadas.
- En RAP: los mensajes de error se propagan via `RAISE SHORTDUMP` o `APPEND VALUE #( ... ) TO reported-<entity>`.
- En SEGW DPC_EXT: los errores se lanzan via `RAISE EXCEPTION TYPE /iwbep/cx_mgw_busi_exception`.

No hacer:

- No ocultar side effects relevantes de un FunctionImport o Action.
- No devolver mensajes de error internos de ABAP (dumps o mensajes de clase de mensajes) sin envolverlos en el contrato OData.

## 8. Checklist final

- [ ] Protocolo OData (V2/V4) declarado por modulo sin mezcla
- [ ] Catalogo de servicios completo con CDS Service Definition o Proyecto SEGW
- [ ] Cada EntitySet referencia una CDS View del modelo ABAP
- [ ] Associations y NavigationProperties documentadas con cardinalidad
- [ ] FunctionImports (V2) y Actions/Functions (V4) clasificadas correctamente
- [ ] Objetos de autorizacion ABAP por operacion
- [ ] Parametros $filter, $expand y limites $top explicitados
- [ ] Errores OData relevantes documentados
- [ ] Patron de consumo SAPUI5 por servicio
- [ ] Trazabilidad servicio-RF cubierta
