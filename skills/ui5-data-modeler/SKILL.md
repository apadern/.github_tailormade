---
name: ui5-data-modeler
description: Genera modelo de datos SAPUI5 (ODataModel V4, JSONModels, ResourceModel, bindings por vista y estructura de mock data) para un MVP. Usar cuando se necesite crear design/02_ui5_data_model.md. No genera vistas XML, controladores, ni componentes Fiori Elements.
---

# UI5 Data Modeler

Genera el modelo de datos de la capa frontend SAPUI5: qué modelos existen, cómo se configuran, qué estructura tienen y cómo se usan en cada vista.

> **OBLIGATORIO — Patrón de desarrollo:**  
> Este skill genera modelos exclusivamente para aplicaciones **freestyle SAPUI5 MVC**  
> (XMLViews + Controllers JS + ODataModel V4 / JSONModel).  
> **Prohibido** incluir anotaciones Fiori Elements (`@UI.LineItem`, `@UI.HeaderInfo`,  
> `@UI.Facets`, `@UI.FieldGroup`, etc.) en ninguna sección del documento generado.  
> **No crear** sección de "Anotaciones Fiori" ni ninguna sección equivalente.

**Alcance:** Exclusivamente la capa de datos del frontend (modelos, bindings, paths, estructuras JSON, mock data).  
**Fuera de alcance:** Vistas XML, controladores, routing, Fiori Elements, SmartControls, anotaciones OData para generación de UI.

---

## Prerrequisitos

Imprescindibles:
- `design/01_technical_design.md` — Módulos, rutas, stack (OData V4/V2, mock mode)
- `design/02_cap_data_model.md` o `design/02_abap_data_model.md` — EntitySets y atributos del backend
- `design/03_odata_services.md` — Servicios OData expuestos, operaciones permitidas, roles

Recomendados:
- `analisis/02_actores_y_roles.md` — Roles XSUAA para el modelo `session`
- `analisis/10_interfaces_usuario.md` — Campos consumidos por cada pantalla
- `analisis/03_requerimientos_funcionales.md` — Datos necesarios por RF

---

## Estructura de Salida

Generar `design/02_ui5_data_model.md` con las siguientes secciones:

---

### 1. Arquitectura de Modelos

#### 1.1 Principios de Modelado

Describir el patrón de modelos adoptado:
- Modo mock vs. real (patrón Mock/Real, `MockServer`, conmutación por URL param o `manifest.json`)
- Separación de responsabilidades entre modelos (global vs. local por vista)
- Naming conventions para IDs de modelo

#### 1.2 Catálogo de Modelos Globales

| ID de Modelo | Tipo UI5 | Alcance | Propietario | Descripción |
|---|---|---|---|---|
| `(default)` | `ODataModel V4` | App global | `Component.js` | Modelo OData principal |
| `i18n` | `ResourceModel` | App global | `Component.js` | Textos internacionalizados |
| `session` | `JSONModel` | App global | `Component.js` | Usuario, rol, permisos |
| `appState` | `JSONModel` | App global | `Component.js` | Estado global: loading, error, mensajes |
| `device` | `JSONModel` | App global | `Component.js` | `sap.ui.Device` — responsive |

Modelos locales (por vista) se documentan en la sección 2.

#### 1.3 Convención de Binding

Documentar los patrones de binding que se utilizarán:

```xml
<!-- Binding relativo sobre contexto OData activo -->
<Text text="{fieldName}" />

<!-- Expression binding -->
<Text text="{= ${status} === 'PAID' ? 'Pagada' : ''}" />

<!-- Binding a modelo nombrado -->
<Button enabled="{session>/roles/isProveedor}" />
<Text text="{appState>/breadcrumb/currentTitle}" />

<!-- Lista OData V4 con parámetros -->
<List items="{
    path: '/EntitySet',
    parameters: {
        $expand: 'relation1,relation2',
        $orderby: 'field desc',
        $top: 50
    }
}" />
```

#### 1.4 EntitySets OData expuestos al frontend

Tabla consolidada de todos los EntitySets que el frontend consume:

| EntitySet OData | Servicio | Rol que accede | Operaciones | $expand disponibles |
|---|---|---|---|---|
| `Entidad1` | `NombreServicio` | RolX | GET(list/detail), POST, PATCH | `rel1`, `rel2` |

#### 1.5 Estructura del Modelo `session`

```json
{
  "userId": "string",
  "displayName": "string",
  "companyName": "string",
  "roles": {
    "isRolA": true,
    "isRolB": false
  },
  "entityId": "uuid"
}
```

---

### 2. Modelo por Vista

Para cada vista/pantalla del módulo documentar:

```markdown
### [N.N] [NombrePantalla] ([ID-Pantalla])

**Ruta:** `RouteNombre` | **Pattern:** `patron` | **View:** `NombreView`
**Roles:** RolA, RolB

#### Modelos activos

| Modelo | Tipo | Binding / Ruta OData | Campos consumidos |
|---|---|---|---|
| `(default)` OData V4 | ODataModel | `/EntitySet` | `campo1`, `campo2`, `campo3` |
| `filters` JSONModel | JSONModel | Filtros activos del panel | campo1, campo2 |
| `ui` JSONModel | JSONModel | Estado UI local | flagA, flagB |

#### Modelo JSON local — `filters`

json
{
  "campo1": null,
  "campo2": "",
  "campo3": []
}


#### Modelo JSON local — `ui`

json
{
  "panelOpen": false,
  "loading": false,
  "selectedKey": ""
}


#### OData Bindings clave

xml
<!-- Binding de lista principal -->
<List items="{path: '/EntitySet', parameters: {$top: 50}}">


#### Acciones OData desde esta vista

| Acción | Tipo | EntitySet / Acción OData | Cuándo |
|---|---|---|---|
| Crear entidad | POST | `/EntitySet` | `onSave` |
| Actualizar estado | PATCH | `/EntitySet(ID)` | `onChangeStatus` |
```

---

### 3. Estructura de Mock Data

Para cada EntitySet, describir la estructura del fichero JSON de mock data:

**Ubicación:** `webapp/localService/mockdata/[EntitySet].json`

```markdown
#### [EntitySet].json

json
{
  "value": [
    {
      "ID": "uuid-001",
      "campo1": "valor",
      "campo2": 100,
      "status": "ENUM_VALUE"
    }
  ]
}

**Registros mínimos recomendados:** N  
**Relaciones a cubrir con mock:** EntitySet A → EntitySet B (expand)
```

---

### 4. Inicialización de Modelos en `Component.js`

Pseudocódigo / estructura de `init()` en `Component.js`:

```javascript
// 1. ODataModel V4 — configurado en manifest.json (dataSources)
// 2. session JSONModel
this.setModel(new JSONModel({
    userId: "",
    displayName: "",
    roles: { isRolA: false }
}), "session");

// 3. appState JSONModel
this.setModel(new JSONModel({
    loading: false,
    error: null,
    breadcrumb: { currentTitle: "" }
}), "appState");

// 4. device JSONModel
this.setModel(new JSONModel(Device), "device");
```

---

### 5. Configuración en `manifest.json`

Extracto relevante de la sección `sap.app.dataSources` y `sap.ui5.models`:

```json
{
  "sap.app": {
    "dataSources": {
      "mainService": {
        "uri": "/odata/v4/NombreServicio/",
        "type": "OData",
        "settings": { "odataVersion": "4.0" }
      }
    }
  },
  "sap.ui5": {
    "models": {
      "": {
        "dataSource": "mainService",
        "settings": {
          "synchronizationMode": "None",
          "operationMode": "Server",
          "autoExpandSelect": false
        }
      },
      "i18n": {
        "type": "sap.ui.model.resource.ResourceModel",
        "settings": { "bundleName": "namespace.i18n.i18n" }
      }
    }
  }
}
```

---

## Proceso

1. Leer `design/03_odata_services.md` → identificar todos los EntitySets y servicios
2. Leer `design/01_technical_design.md` → confirmar patrón mock/real y módulos
3. Leer `analisis/02_actores_y_roles.md` → definir estructura del modelo `session`
4. Recorrer cada pantalla de `analisis/10_interfaces_usuario.md` → identificar campos consumidos
5. Definir catálogo de modelos globales (sección 1)
6. Por cada vista: definir modelos activos + estructuras JSON locales + bindings clave (sección 2)
7. Definir estructura de mock data por EntitySet (sección 3)
8. Documentar inicialización en `Component.js` (sección 4)
9. Documentar extracto de `manifest.json` (sección 5)
10. Guardar `design/02_ui5_data_model.md`

---

## Restricciones

- **Patrón obligatorio:** freestyle SAPUI5 MVC — XMLViews + Controllers JS + ODataModel V4 / JSONModel
- NO generar vistas XML ni fragmentos de interfaz
- NO generar controladores ni lógica de evento
- NO usar Fiori Elements (SmartTable, SmartForm, SmartFilterBar, SmartField, OVP)
- NO generar anotaciones Fiori Elements: `@UI.LineItem`, `@UI.HeaderInfo`, `@UI.Facets`, `@UI.FieldGroup`, `@UI.SelectionField`, ni ninguna otra anotación `@UI.*`
- NO crear sección "Anotaciones Fiori" ni ninguna sección equivalente en el documento generado
- NO generar código TypeScript; solo estructuras JSON y pseudocódigo JavaScript
- Los bindings OData documentados son solo ejemplos de referencia de paths y parámetros, no código de vista

---

## Escritura Incremental (Documentos Extensos)

**CRÍTICO**: Generar el archivo de forma INCREMENTAL para evitar errores de límite de output.

### Proceso de Escritura

1. **Crear archivo** con encabezado y sección 1 (arquitectura + catálogo de modelos globales)
2. **Agregar sección 2** vista a vista (2-3 vistas por operación de append)
3. **Agregar sección 3** (mock data) por bloques de 3-4 EntitySets
4. **Agregar secciones 4 y 5** al final (Component.js y manifest.json)

### Patrón de Append

```markdown
### 2.2 [NombrePantalla] ([ID])

**Ruta:** `RouteNombre` | **Pattern:** `...`
...
```

Luego append siguiente bloque:

```markdown
### 2.3 [NombrePantalla] ([ID])
...
```

### Respuesta del Skill

**NO devolver contenido completo** del archivo. Solo confirmar:

```
Archivo design/02_ui5_data_model.md generado:
- Modelos globales: X
- Vistas documentadas: Y
- EntitySets OData: Z
- Modelos JSON locales: N
```

---

## Output

```
Archivo design/02_ui5_data_model.md generado:
- Modelos globales: X
- Vistas documentadas: Y
- EntitySets OData: Z
- Modelos JSON locales: N
```
