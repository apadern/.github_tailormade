# Estructura Base del Frontend SAPUI5

Esta referencia define la **plantilla de estructura** y convenciones mínimas para la capa frontend de un MVP SAP con **SAPUI5 (XMLViews + Controllers + manifest.json)**.

## Árbol de Directorios (webapp)

```
webapp/
├── Component.js                        # Componente raíz: inicializa modelo dual mock/OData
├── index.html                          # Entry point (desarrollo local / BTP launchpad)
├── manifest.json                       # Descriptor: routing, modelos, i18n, dependencias SAPUI5
│
├── controller/
│   ├── App.controller.js               # Controlador raíz (navegación global, mensajes)
│   └── <Modulo>/                       # Subcarpeta por módulo funcional
│       ├── List.controller.js          # Controlador de vista de listado
│       ├── Detail.controller.js        # Controlador de vista de detalle
│       └── Create.controller.js        # Controlador de formulario (creación/edición)
│
├── view/
│   ├── App.view.xml                    # Vista raíz (NavContainer / ShellBar)
│   └── <Modulo>/                       # Subcarpeta por módulo funcional
│       ├── List.view.xml               # Vista de listado (FilterBar + Table/SmartTable)
│       ├── Detail.view.xml             # Vista de detalle (ObjectHeader + sections)
│       └── Create.view.xml             # Vista de formulario (SimpleForm / SmartForm)
│
├── fragment/                           # Fragmentos XML reutilizables
│   └── <Modulo>/
│       ├── ConfirmDialog.fragment.xml  # Diálogo de confirmación
│       └── ErrorDialog.fragment.xml   # Diálogo de error estándar
│
├── model/
│   └── models.js                       # Fábrica de modelos: ODataModel V4 o JSONModel mock
│
├── localService/                       # Datos mock y servidor simulado (modo mock)
│   ├── mockserver.js                   # Inicialización sap.ui.core.util.MockServer
│   ├── metadata.xml                    # Metadatos OData (EDMX, refleja el servicio CAP)
│   └── mockdata/
│       └── <EntitySet>.json            # Array de datos mock por EntitySet OData
│
├── i18n/
│   └── i18n.properties                 # Textos internacionalizables (clave=valor)
│
├── css/
│   └── style.css                       # Estilos personalizados (mínimos; preferir temas SAPUI5)
│
└── test/
    ├── testsuite.qunit.html
    ├── testsuite.qunit.js
    ├── unit/
    │   ├── AllTests.js
    │   └── controller/
    │       └── <Modulo>/<Nombre>.controller.js  # Tests unitarios de controllers
    └── integration/
        ├── AllJourneys.js
        ├── opaTests.qunit.html
        └── journeys/
            └── <Modulo>Journey.js              # OPA5 journey por módulo
```

## Módulos Funcionales

Cada módulo funcional (agrupación de RFs coherentes) se implementa como subcarpeta dentro de `view/` y `controller/`. El nombre del módulo en kebab-case se usa en los patrones de ruta del `manifest.json`.

| Módulo (ejemplo) | Descripción | Vistas típicas |
|------------------|-------------|----------------|
| `gestion-facturas` | Ciclo de vida de facturas | List, Detail, Create |
| `gestion-incidencias` | Alta y seguimiento de incidencias | List, Detail, Create |
| `admin-usuarios` | Administración de usuarios y roles ABAP | List, Detail |
| `auditoria` | Consulta de logs SLG1 | List |

> Añadir o eliminar módulos según los RFs del proyecto. El nombre del módulo en `view/` y `controller/` debe coincidir exactamente con el usado en los `patterns` del `manifest.json`.

## Convenciones de Nombrado

| Tipo de artefacto | Convención | Ejemplo |
|-------------------|------------|---------|
| Módulo (carpeta) | kebab-case | `gestion-facturas/` |
| Vista XML | PascalCase + sufijo funcional | `List.view.xml`, `Detail.view.xml` |
| Controlador JS | Mismo nombre que vista | `List.controller.js` |
| Fragmento XML | PascalCase + `Fragment` | `ConfirmDialog.fragment.xml` |
| Ruta manifest | PascalCase + prefijo `Route` | `RouteFacturasList` |
| Target manifest | PascalCase + sufijo `Target` | `FacturasListTarget` |
| Nombre técnico vista (target) | PascalCase relativo a `viewPath` | `gestion-facturas.List` |
| ID de control reutilizable | camelCase único por vista | `facturaTable`, `filterBar` |
| Clave i18n | camelCase por contexto | `title.facturas.list` |

## Plantillas de Vista Disponibles

| Tipo de vista | Controles SAPUI5 principales | Cuándo usarla |
|---------------|------------------------------|----------------|
| **Listado** (`List.view.xml`) | `sap.ui.comp.smartfilterbar.SmartFilterBar` + `sap.m.Table` o `sap.ui.table.Table` | Visualización y filtrado de colecciones |
| **Detalle** (`Detail.view.xml`) | `sap.m.ObjectHeader` + `sap.uxap.ObjectPageLayout` con secciones | Visualización de una entidad con sus relaciones |
| **Formulario** (`Create.view.xml`) | `sap.ui.layout.form.SimpleForm` o `sap.ui.comp.smartform.SmartForm` | Creación o edición de una entidad |

## Routing en manifest.json (sap.ui5)

```json
"routing": {
  "config": {
    "routerClass": "sap.m.routing.Router",
    "viewType": "XML",
    "viewPath": "<namespace>.view",
    "controlId": "app",
    "controlAggregation": "pages",
    "bypassed": { "target": "notFound" }
  },
  "routes": [
    {
      "name": "RouteFacturasList",
      "pattern": "facturas",
      "target": "FacturasListTarget"
    },
    {
      "name": "RouteFacturasDetail",
      "pattern": "facturas/{facturaId}",
      "target": "FacturasDetailTarget"
    }
  ],
  "targets": {
    "FacturasListTarget": {
      "viewName": "gestion-facturas.List",
      "viewLevel": 1
    },
    "FacturasDetailTarget": {
      "viewName": "gestion-facturas.Detail",
      "viewLevel": 2
    }
  }
}
```

**Reglas:**
- `pattern` usa kebab-case coherente con el nombre del módulo.
- Los parámetros de ruta (p.ej. `{facturaId}`) se corresponden con la clave del EntitySet OData.
- `viewLevel` sigue el orden de navegación (listado = 1, detalle = 2, formulario = 3).

## Modo Dual Mock / OData Real

El frontend soporta dos modos de ejecución sin cambiar vistas ni controllers:

| Modo | Descripción | Activación |
|------|-------------|------------|
| **mock** (por defecto) | `MockServer` sirve datos desde `localService/mockdata/*.json` | `index.html` carga `localService/mockserver.js` antes del bootstrap |
| **realOData** | `sap.ui.model.odata.v4.ODataModel` apunta al servicio CAP | Eliminar o deshabilitar la carga del mockserver; configurar `serviceUrl` en `manifest.json` |

**Selector único de modo en `Component.js`:**

```javascript
// Component.js — fragmento ilustrativo
init: function () {
    var bMock = new URLSearchParams(window.location.search).get("responderType") !== "realOData";
    if (bMock) {
        // Arranca MockServer antes de que el modelo OData haga peticiones
        sap.ui.require(["<namespace>/localService/mockserver"], function (MockServer) {
            MockServer.init();
        });
    }
    UIComponent.prototype.init.apply(this, arguments);
    this.getRouter().initialize();
}
```

**Reglas del modelo dual:**
- Los controllers y vistas **no leen el modo directamente**; todo binding va contra el modelo OData registrado en `manifest.json` (sea real o mock).
- `localService/metadata.xml` debe reflejar fielmente el EDMX del servicio CAP para que los bindings sean idénticos en ambos modos.
- Los archivos `localService/mockdata/<EntitySet>.json` deben tener el mismo nombre que el EntitySet definido en el EDMX.

## Patrón de Controller (MVC)

```javascript
// webapp/controller/<Modulo>/List.controller.js
sap.ui.define([
    "sap/ui/core/mvc/Controller",
    "sap/ui/model/Filter",
    "sap/ui/model/FilterOperator",
    "sap/m/MessageToast"
], function (Controller, Filter, FilterOperator, MessageToast) {
    "use strict";

    return Controller.extend("<namespace>.controller.<Modulo>.List", {

        onInit: function () {
            // Inicialización: binding de ruta, modelo de vista local si es necesario
            this.getOwnerComponent().getRouter()
                .getRoute("Route<Modulo>List")
                .attachPatternMatched(this._onRouteMatched, this);
        },

        _onRouteMatched: function () {
            // Refrescar binding o aplicar filtros iniciales
        },

        onSearch: function (oEvent) {
            var sQuery = oEvent.getParameter("query");
            var oFilter = sQuery
                ? new Filter("NombreCampo", FilterOperator.Contains, sQuery)
                : null;
            this.byId("tablaId").getBinding("items").filter(oFilter ? [oFilter] : []);
        },

        onNavToDetail: function (oEvent) {
            var sId = oEvent.getSource().getBindingContext().getProperty("ID");
            this.getOwnerComponent().getRouter().navTo("Route<Modulo>Detail", { id: sId });
        }
    });
});
```

**Reglas de los controllers:**
- No acceden directamente a datos mock; todo pasa por el modelo vinculado (binding OData o JSONModel).
- No realizan llamadas `fetch` / `jQuery.ajax` directas salvo funciones/acciones OData (vía `callFunction` / `invoke`).
- Los fragmentos de diálogo se cargan bajo demanda con `Fragment.load(...)` y se destruyen en `onExit`.

## Controles SAPUI5 Recomendados por Caso de Uso

| Caso de uso | Control principal | Librería |
|-------------|-------------------|---------|
| Listado con filtros simples | `sap.m.List` + `sap.m.SearchField` | `sap.m` |
| Listado con filtros avanzados | `sap.ui.comp.smartfilterbar.SmartFilterBar` + `sap.ui.table.Table` | `sap.ui.comp` |
| Detalle de entidad | `sap.uxap.ObjectPageLayout` | `sap.uxap` |
| Formulario de edición | `sap.ui.layout.form.SimpleForm` | `sap.ui.layout` |
| Diálogo de confirmación | `sap.m.Dialog` (fragment reutilizable) | `sap.m` |
| Mensajes de error/éxito | `sap.m.MessageToast` / `sap.m.MessageBox` | `sap.m` |
| Indicador de estado | `sap.m.ObjectStatus` / `sap.m.MessageStrip` | `sap.m` |
| Navegación lateral | `sap.m.SideNavigation` + `sap.m.NavContainer` | `sap.m` |

## Stack Tecnológico

| Categoría | Tecnología | Notas |
|-----------|------------|-------|
| Framework UI | SAPUI5 / OpenUI5 | Versión alineada con el sistema SAP destino (≥ 1.108 LTS recomendado) |
| Paradigma | MVC (XMLViews + Controllers JS) | JavaScript ES6+ o TypeScript (opcional con UI5 Tooling) |
| Routing | `sap.m.routing.Router` vía `manifest.json` | Basado en hash (`#`) por defecto |
| Modelo (producción) | `sap.ui.model.odata.v4.ODataModel` | Apunta al servicio CAP OData V4 |
| Modelo (mock) | `sap.ui.model.json.JSONModel` + `sap.ui.core.util.MockServer` | Datos en `localService/mockdata/*.json` |
| Modelos de vista | `sap.ui.model.json.JSONModel` | Estado local de vista (p.ej. flags de edición, listas auxiliares) |
| Internacionalización | `sap.ui.model.resource.ResourceModel` | Fichero `i18n/i18n.properties` |
| Build / despliegue | UI5 Tooling (`@ui5/cli`) | `ui5.yaml` define namespace, librerías y destino BTP/Launchpad |
| Testing unitario | QUnit + `sap.ui.test.utils` | Bajo `test/unit/` |
| Testing E2E | OPA5 (`sap.ui.test.Opa5`) | Journeys bajo `test/integration/journeys/` |
