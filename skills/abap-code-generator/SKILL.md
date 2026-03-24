---
name: abap-code-generator
description: Genera código ABAP en el sistema SAP S/4HANA para integración con SAPUI5/Fiori. Cubre clases ABAP, módulos de función, CDS Views, proyectos OData V2 (SEGW), RAP (RESTful Application Programming Model) y la integración ABAP↔SAPUI5. Úsalo cuando se necesite crear o modificar objetos ABAP en el sistema, exponer servicios OData/REST, o construir la capa backend para aplicaciones SAPUI5/Fiori.
---

# ABAP Code Generator

Genera y modifica objetos ABAP en el sistema SAP usando las herramientas `abap_*`.

## Reglas fundamentales (SIEMPRE aplicar)

1. **Verificar antes de crear.** Usar `abap_search` para comprobar si el objeto ya existe.
2. **Lock → Edit → Unlock.** Toda modificación sigue el ciclo: `abap_lock` → `abap_setsourcecode` → `abap_unlock`.
3. **Activar siempre.** Llamar `abap_activate` al finalizar cada objeto.
4. **Verificar sintaxis.** Tras generar código, ejecutar `abap_syntaxcheckcode` antes de activar.
5. **Convenciones de nombres.** Respetar las convenciones Z*/Y* del cliente, prefijo del paquete indicado.
6. **No sobre-ingeniería.** Generar solo lo solicitado. No añadir lógica extra ni objetos adicionales no pedidos.

## Herramientas disponibles

| Herramienta | Cuándo usarla |
|---|---|
| `abap_search` | Buscar objetos existentes por nombre/tipo |
| `abap_getsourcecode` | Leer código fuente actual de un objeto |
| `abap_setsourcecode` | Escribir/actualizar código fuente |
| `abap_lock` | Bloquear objeto antes de editar |
| `abap_unlock` | Desbloquear tras terminar edición |
| `abap_activate` | Activar objeto(s) en el sistema |
| `abap_syntaxcheckcode` | Verificar sintaxis antes de activar |
| `abap_openobject` | Obtener URI navegable al objeto |
| `abap_createobject` | Crear objeto nuevo en el sistema |
| `abap_getstructure` | Consultar estructura/diccionario de datos |
| `abap_gettable` | Consultar tabla de base de datos |
| `abap_gettypeinfo` | Obtener información de tipo ABAP |
| `abap_transportinfo` | Consultar/asignar órdenes de transporte |
| `abap_getsapuser` | Obtener usuario activo en el sistema |
| `abap_unit` | Ejecutar unit tests ABAP |
| `abap_usagereferences` | Buscar usos de un objeto |

## Modos de operación

| Modo | Descripción | Ver referencia |
|---|---|---|
| `clase` | Clase ABAP (OO) | [Modo: Clase](#modo-clase) |
| `fm` | Módulo de función | [Modo: FM](#modo-fm) |
| `cds` | CDS View (DDIC/RAP) | [cds-rap.md](references/cds-rap.md) |
| `odata-v2` | Proyecto OData V2 via SEGW | [odata-v2.md](references/odata-v2.md) |
| `rap` | RAP Business Object (OData V4) | [cds-rap.md](references/cds-rap.md) |
| `ui5-integration` | Conexión SAPUI5↔OData/RAP | [ui5-integration.md](references/ui5-integration.md) |

---

## Modo: Clase

### Flujo

1. `abap_search` — verificar que no existe.
2. `abap_createobject` con tipo `CLAS/OC`.
3. Generar definición y implementación por separado con `abap_setsourcecode`.
4. Activar con `abap_activate`.

### Plantilla mínima

```abap
CLASS zcl_<nombre> DEFINITION
  PUBLIC FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    METHODS: constructor,
             <metodo> RETURNING VALUE(rv_result) TYPE <tipo>.

  PRIVATE SECTION.
    DATA: ...

ENDCLASS.

CLASS zcl_<nombre> IMPLEMENTATION.

  METHOD constructor.
    ...
  ENDMETHOD.

  METHOD <metodo>.
    ...
  ENDMETHOD.

ENDCLASS.
```

### Convenciones de nombres

- Clases: `ZCL_<PAQUETE>_<NOMBRE>`
- Interfaces: `ZIF_<PAQUETE>_<NOMBRE>`
- Exception classes: `ZCX_<PAQUETE>_<NOMBRE>`

---

## Modo: FM (Módulo de Función)

### Flujo

1. Verificar grupo de funciones (`FUGR`) existente con `abap_search`.
2. Si no existe el grupo: `abap_createobject` tipo `FUGR/F`.
3. Crear FM dentro del grupo: `abap_createobject` tipo `FUNC`.
4. `abap_lock` → `abap_setsourcecode` → `abap_syntaxcheckcode` → `abap_activate`.

### Plantilla mínima

```abap
FUNCTION z<nombre_fm>.
*"----------------------------------------------------------------------
*"*"Interfaz local:
*"  IMPORTING
*"     VALUE(iv_param) TYPE <tipo>
*"  EXPORTING
*"     VALUE(ev_result) TYPE <tipo>
*"  EXCEPTIONS
*"     error_generico
*"----------------------------------------------------------------------

  " Lógica
  ev_result = iv_param.

ENDFUNCTION.
```

---

## Flujo de integración ABAP ↔ SAPUI5

> Para integración completa, leer referencias en orden:
> 1. `references/odata-v2.md` → proyecto SEGW y servicio OData
> 2. `references/cds-rap.md` → CDS Views y RAP para OData V4
> 3. `references/ui5-integration.md` → consumo desde SAPUI5

```
Datos SAP (tablas/BAPIs)
        │
        ▼
CDS View / ABAP Class (capa de acceso a datos)
        │
        ▼
OData Service (SEGW para V2 / RAP para V4)
        │
        ▼
SAPUI5 App (ODataModel V2 / V4)
```

---

## Guardrails anti-errores

| Error frecuente | Causa | Solución |
|---|---|---|
| `OBJECT_NOT_FOUND` al activar | El objeto padre no está activo | Activar el contenedor primero (DEVC, FUGR) |
| `NAME_ALREADY_EXISTS` | Objeto duplicado | Usar `abap_search` antes de crear |
| Sintaxis OK pero semántica falla | Tipo incompatible | Verificar con `abap_gettypeinfo` / `abap_getstructure` |
| Transporte requerido | Sistema productivo/QA | Obtener orden con `abap_transportinfo` |
| RFC/BAPI firma incorrecta | Interfaz desconocida | Leer FM existente con `abap_getsourcecode` antes de llamarlo |

---

## Orden de activación recomendado

Cuando se crean varios objetos relacionados, activar en este orden para evitar dependencias rotas:

1. Paquetes / Dominios / Elementos de datos / Estructuras DDIC
2. Interfaces ABAP
3. Clases abstractas / base
4. Clases concretas / implementaciones
5. Grupos de funciones → Módulos de función
6. Programas / Reports
7. CDS Views (de más básica a más derivada)
8. Servicios OData / RAP Business Objects
