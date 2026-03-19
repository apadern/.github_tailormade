---
name: ui-builder
description: Genera vistas y fragmentos SAPUI5 desde especificaciones de interfaz y backlog. Usa el patrón MVC con XMLViews, controladores JS y modelos JSON/OData siguiendo las convenciones del proyecto.
---

# UI Builder

Genera UI SAPUI5 (vistas XML + fragmentos + controladores JS) desde backlog y especificaciones funcionales.

Implementa las pantallas de un módulo en SAPUI5 (XML Views + Fragments + Controllers JS) a partir del backlog y las especificaciones funcionales del módulo.

## Objetivo

Implementar las pantallas del módulo en SAPUI5 usando **XML Views**, **Fragments**, **Controllers** y controles estándar de `sap.m`, `sap.f` o librerías necesarias. Incluir binding inicial, i18n y estructura visual alineada con el diseño funcional.

## Entregables

- Vistas XML del módulo (`webapp/view/`)
- Controllers asociados (`webapp/controller/`)
- Fragments reutilizables (`webapp/fragments/` o `webapp/view/fragments/`)
- Modelos JSON/OData configurados para la UI (`webapp/model/`)
- Ficheros i18n actualizados (`webapp/i18n/i18n.properties`)
- Estructura del módulo en `webapp/` alineada con `manifest.json`
- Estilos específicos mínimos si aplican (`webapp/css/`)
- Pruebas unitarias básicas de controller/formatter si están contempladas en el backlog (`webapp/test/unit/`)

## Exclusiones

- **No incluye** navegación completa entre pantallas fuera del flujo del módulo
- **No incluye** integración E2E completa
- **No incluye** lógica backend ni ampliaciones de servicios OData/CDS

## Cuándo usar

- Ya existe documentación funcional del módulo con sección "Pantallas" o "Vistas"
- Ya existe diseño técnico (`design/`) con rutas, modelos y contratos de servicio

## Parámetros

- `module` (string, requerido): nombre del módulo en kebab-case (ej: `maestro-posiciones`)
- `views` (string[], opcional): vistas específicas a generar; si se omite, se generan todas las contempladas
- `incremental` (boolean): máximo 3 vistas por invocación. Default: `true`

## Prerrequisitos

- Documentación funcional — sección "Pantallas" / "Interfaces de usuario"
- `webapp/manifest.json` — configuración de rutas, modelos y dependencias
- `webapp/controller/App.controller.js` — controlador base del que heredan los demás
- `webapp/model/` — modelos del módulo (JSON/OData) si ya existen
- `webapp/i18n/i18n.properties` — literales de texto existentes

## Patrones de Vista

Usar el patrón **solo cuando el tipo de pantalla corresponda**. Para pantallas que no encajen, implementar directamente con controles SAPUI5 apropiados.

| Patrón | Usar cuando | Indicadores clave |
|--------|-------------|-------------------|
| Lista con tabla | Listados con tabla, filtros, búsqueda | "lista", "búsqueda", "tabla" |
| Detalle de entidad | Visualización de entidad con secciones | "detalle", "consulta", "tabs" |
| Formulario | Formularios de crear/editar | "crear", "editar", "formulario" |
| Dashboard / KPIs | Indicadores, tiles, resúmenes | "dashboard", "resumen", "kpi" |

Para reportes, configuraciones u otras pantallas especiales: **no forzar patrón**.

## Librerías y Controles SAPUI5

Seleccionar controles de las librerías estándar según el caso de uso. Declarar **únicamente los namespaces necesarios** en `<mvc:View>`.

### `sap.m` — Mobile-first (uso mayoritario)
- `sap.m.Table`, `sap.m.Column`, `sap.m.ColumnListItem` — Tablas responsivas
- `sap.m.List`, `sap.m.StandardListItem`, `sap.m.ObjectListItem` — Listas
- `sap.m.SearchField`, `sap.m.Input`, `sap.m.Select`, `sap.m.DatePicker`, `sap.m.ComboBox` — Filtros y entradas
- `sap.m.Panel`, `sap.m.VBox`, `sap.m.HBox`, `sap.m.FlexBox` — Contenedores y layout
- `sap.m.Button`, `sap.m.OverflowToolbar`, `sap.m.ToolbarSpacer` — Acciones y barra de herramientas
- `sap.m.BusyIndicator`, `sap.m.MessageStrip`, `sap.m.MessageToast`, `sap.m.MessageBox` — Estados y mensajes
- `sap.m.Dialog`, `sap.m.ActionSheet` — Diálogos modales
- `sap.m.GenericTile`, `sap.m.TileContent`, `sap.m.NumericContent` — KPIs y tiles
- `sap.m.Page`, `sap.m.NavContainer`, `sap.m.SplitApp` — Contenedores de navegación

### `sap.f` — Floorplan controls (pantallas complejas)
- `sap.f.DynamicPage`, `sap.f.DynamicPageTitle`, `sap.f.DynamicPageHeader` — Páginas con cabecera colapsable
- `sap.f.GridList`, `sap.f.GridContainer` — Layouts en cuadrícula
- `sap.f.FlexibleColumnLayout` — Layout de 2-3 columnas (master/detail)

### `sap.ui.layout` — Layouts de formulario
- `sap.ui.layout.form.SimpleForm` — Formularios simples
- `sap.ui.layout.form.Form`, `sap.ui.layout.form.FormContainer` — Formularios estructurados
- `sap.ui.layout.Grid`, `sap.ui.layout.GridData` — Grid layout responsive

### `sap.uxap` — Object Page
- `sap.uxap.ObjectPageLayout`, `sap.uxap.ObjectPageSection`, `sap.uxap.ObjectPageSubSection` — Páginas de detalle complejas

## Modelos JSON/OData para la UI

### Modelo JSON (estado local de la vista)
```javascript
// En onInit del controller
var oViewModel = new JSONModel({
    busy: false,
    editable: false,
    itemCount: 0
});
this.getView().setModel(oViewModel, "viewModel");
```

### Binding OData V2 a elemento
```xml
<!-- Binding de elemento (detalle) -->
<mvc:View controllerName="...">
    <Page binding="{/EntitySet('key')}">
        <Text text="{Property}"/>
    </Page>
</mvc:View>
```

### Binding OData V2 a lista
```xml
<Table items="{/EntitySet}">
    <columns>...</columns>
    <items>
        <ColumnListItem>
            <cells><Text text="{Property}"/></cells>
        </ColumnListItem>
    </items>
</Table>
```

## Convención `data-testid` (FUENTE CANONICAL)

Usar como única fuente de verdad el fichero:
- `.github/skills/ui-builder/references/testids.md`

Obligatorio añadir `data-testid` al menos a: contenedor de página, tablas, filtros/inputs/selects principales, botones de acción, formularios y diálogos.

En SAPUI5 se declara el namespace `data` en `<mvc:View>` y se usa la sintaxis abreviada en cada control:

```xml
<mvc:View
    xmlns:mvc="sap.ui.core.mvc"
    xmlns:data="http://schemas.sap.com/sapui5/extension/sap.ui.core.CustomData/1"
    ...>

    <Page data:testid="modulo-page-listado">
        <Table data:testid="modulo-table-entidades">...</Table>
        <Button text="{i18n>create}" press=".onPressCreate" data:testid="modulo-btn-crear"/>
    </Page>
```

La propiedad `writeToDom="true"` se aplica automáticamente con la sintaxis abreviada `data:key="value"`.

## Proceso

1. **Leer** documentación funcional — sección "Pantallas" / "Interfaces de usuario"
2. **Identificar** tipo de cada pantalla y patrones aplicables
3. **Determinar** librerías necesarias (`sap.m`, `sap.f`, `sap.uxap`, `sap.ui.layout`)
4. **Generar Vista XML** (`webapp/view/<NombreVista>.view.xml`) con:
   - Namespace `xmlns:data` para `data-testid`
   - `data-testid` en elementos críticos (ver `testids.md`)
   - Binding declarativo de modelos (sin lógica en la vista)
   - Todos los textos visibles vía `{i18n>clave}`
   - Solo los namespaces XML de las librerías realmente usadas
5. **Generar Controller JS** (`webapp/controller/<NombreVista>.controller.js`) con:
   - Herencia de `App.controller` mediante `sap.ui.define`
   - JSDoc en todas las funciones públicas
   - Inicialización de modelos JSON de vista en `onInit`
   - Suscripción a eventos del router (`onRouteMatched`) si aplica
   - Gestión de estados: cargando (`busy: true`), error (`MessageStrip`), vacío (texto informativo)
6. **Generar Fragments XML** (`webapp/fragments/<NombreFragmento>.fragment.xml`) si la pantalla requiere diálogos, popovers o paneles reutilizables
7. **Actualizar `webapp/manifest.json`**: añadir ruta y target si no existen; declarar dependencias de librerías necesarias en `sap.ui5.dependencies.libs`
8. **Actualizar `webapp/i18n/i18n.properties`**: añadir solo las claves nuevas necesarias
9. **Generar estilos mínimos** en `webapp/css/style.css` solo si los controles estándar no cubren el requisito visual
10. **Generar pruebas unitarias** de controller/formatter en `webapp/test/unit/` si están contempladas en el backlog

## Reglas

- Seguir estrictamente las convenciones de nomenclatura del proyecto
- Usar siempre `{i18n>clave}` para todos los textos visibles; **nunca** texto literal en la vista XML
- Usar `this.getOwnerComponent().getRouter().navTo()` para navegación dentro del flujo del módulo
- Actualizar propiedades de modelo con `oModel.setProperty()`; evitar `refresh()` innecesario
- Referenciar modelos por nombre (`this.getView().getModel("viewModel")`) en vez de ID global de control
- **NO** duplicar lógica que ya exista en `App.controller`; centralizar ahí los métodos comunes
- **NO** sobrescribir estilos CSS de SAP; usar clases estándar (`sapUiSmallMargin`, `sapUiResponsiveContentPadding`, `sapThemeBaseBG`, etc.) siempre que sea posible
- **NO** usar `alert()` / `confirm()` del navegador; usar `sap.m.MessageBox` o `sap.m.MessageToast`
- **NO** implementar navegación fuera del flujo del módulo, lógica backend ni ampliaciones OData/CDS (fuera de alcance de esta fase)
- Formato de vistas: **una línea por control** (excepto `<mvc:View>` que usa una línea por propiedad)
- Tab size 4 en todos los ficheros

### Reglas UI

#### Lista con tabla (búsqueda rápida)

- La búsqueda debe ser case-insensitive y por contiene (substring), no solo prefijo.
  - Si el filtrado es en cliente (JSONModel): usar `sap.ui.model.Filter` con `FilterOperator.Contains` y valor normalizado con `trim()`.
  - Si el filtrado es en backend (ODataModel): enviar el parámetro normalizado y asumir semántica "contiene" en el endpoint.
- La búsqueda se ejecuta al pulsar Enter o el icono de búsqueda (evento `search` del `sap.m.SearchField`).

#### Filtros (panel/toolbar)

- Al cargar la página, inicializar los filtros a su estado vacío en `onInit`.
- En placeholders de filtros, no usar valores de ejemplo; usar descripciones vía i18n.
  - Ej: `placeholder="{i18n>filterCodePlaceholder}"` (nunca un valor literal como `"0049"`).
- En los campos de texto la búsqueda debe ser case-insensitive.
- Los botones del panel de filtros deben llamarse exactamente «Limpiar» y «Buscar» (literales i18n).

#### Tablas

- Cabeceras de columnas mediante literales i18n escritos en MAYÚSCULAS.
- Ordenación por columnas de datos: usar `sortIndicator` en `sap.m.Column` cuando aplique.
- Todas las acciones de fila se representan como botones icono (`sap.m.Button` con propiedad `icon` y `type="Transparent"`).
  - Cada acción debe tener un icono coherente con su función. No reutilizar el mismo icono para acciones distintas.

#### Formularios

- Usar `sap.ui.layout.form.SimpleForm` con `editable="true"` para formularios de edición.
- Validar campos obligatorios en el controlador antes de llamar al servicio.
- Convertir tipos explícitamente si el backend espera tipos específicos (Integer, Float).
  - Campos opcionales vacíos: mapear `""` → `null` / `undefined` para evitar enviar strings vacíos.

## Salida

Confirmar con formato:
```
UI generada para módulo [nombre]:
- Vistas: X (lista de ficheros)
- Controladores: Y (lista de ficheros)
- Fragmentos: Z (lista de ficheros, si aplica)
```
