---
name: ui-builder
description: Genera vistas y fragmentos SAPUI5 desde especificaciones de interfaz y backlog. Usa el patrón MVC con XMLViews, controladores JS y modelos JSON/OData siguiendo las convenciones del proyecto.
---

# UI Builder

Genera UI SAPUI5 (vistas XML + fragmentos + controladores JS) desde backlog y especificaciones funcionales.

## Cuándo usar

- Ya existe documentación funcional del módulo con sección "Pantallas" o "Vistas"
- Ya existen modelos y servicios del módulo

## Parámetros

- `module` (string, requerido): nombre del módulo
- `views` (string[], opcional): vistas específicas a generar
- `incremental` (boolean): máximo 3 vistas por invocación. Default: `true`

## Prerrequisitos

- Documentación funcional del módulo - Sección "Pantallas"
- `webapp/manifest.json` - Configuración de rutas y modelos
- `webapp/controller/App.controller.js` - Controlador base del que heredan los demás
- `webapp/model/` - Modelos del módulo (si existen)
- `webapp/i18n/i18n.properties` - Literales de texto

## Patrones de Vista Disponibles

Usar el patrón **solo cuando el tipo de pantalla corresponda**. Para pantallas que no encajen, implementar directamente con controles SAPUI5.

| Patrón | Usar cuando | Indicadores |
|--------|-------------|-------------|
| Lista con tabla | Listados con tabla, filtros, búsqueda | "lista", "búsqueda", "tabla" |
| Detalle de entidad | Visualización de entidad con secciones | "detalle", "consulta", "tabs" |
| Formulario | Formularios de crear/editar | "crear", "editar", "formulario" |

Para dashboards, reportes, configuraciones u otras pantallas especiales: **no forzar patrón**.

## Controles Habituales

Seleccionar controles SAPUI5 apropiados según el caso de uso:

- `sap.m.Table`, `sap.m.Column`, `sap.m.ColumnListItem` — Tablas responsivas
- `sap.m.List`, `sap.m.StandardListItem` — Listas simples
- `sap.m.SearchField`, `sap.m.Input`, `sap.m.Select`, `sap.m.DatePicker` — Filtros y entradas
- `sap.m.Panel`, `sap.m.VBox`, `sap.m.HBox` — Contenedores y layout
- `sap.m.Button`, `sap.m.OverflowToolbar` — Acciones
- `sap.m.BusyIndicator`, `sap.m.MessageStrip` — Estados (cargando / error)
- `sap.ui.layout.form.SimpleForm` — Formularios
- `sap.uxap.ObjectPageLayout` — Páginas de detalle complejas

## Convención `data-testid` (FUENTE CANONICAL)

Usar como única fuente de verdad:
- `.githubTailormade/skills/ui-builder/references/testids.md`

Obligatorio añadir `data-testid` al menos a: contenedor de página, tablas, filtros/inputs/selects principales, botones de acción, formularios/diálogos.

En SAPUI5 se añade mediante `customData` en la vista XML con `writeToDom="true"`. Declarar el namespace en `<mvc:View>` y usar la sintaxis abreviada en cada control:

```xml
<mvc:View
    xmlns:data="http://schemas.sap.com/sapui5/extension/sap.ui.core.CustomData/1"
    ...>

    <Button text="{i18n>save}" press=".onPressSave" data:testid="modulo-btn-save"/>
```

## Proceso

1. Leer documentación funcional sección "Pantallas"
2. Identificar tipo de cada pantalla
3. Seleccionar patrón o implementación directa
4. Generar vista XML con:
   - Namespace `xmlns:data` para `data-testid`
   - `data-testid` en elementos críticos (ver reglas mínimas en `testids.md`)
   - Binding de modelo declarativo (sin lógica en la vista)
   - Todos los textos visibles vía i18n
5. Generar controlador JS con:
   - Herencia de `App.controller` (ver convención en `copilot-instructions.md`)
   - JSDoc en todas las funciones (ver `jsdoc.instructions.md`)
   - Inicialización de controles y modelos en `onInit`
   - Gestión de estados: loading (`BusyIndicator`), error (`MessageStrip`), vacío (texto informativo)
6. Generar fragmentos XML si la pantalla requiere diálogos o paneles reutilizables
7. Añadir ruta y target en `webapp/manifest.json` si no existe
8. Añadir literales nuevos en `webapp/i18n/i18n.properties`
9. Escribir vistas en `webapp/view/` y controladores en `webapp/controller/`

## Reglas

- Seguir convenciones de nomenclatura del proyecto (`nomenclatura.instructions.md`)
- Usar siempre i18n para todos los textos visibles; nunca texto literal en la vista
- Usar `this.getOwnerComponent().getRouter().navTo()` para navegación entre vistas
- Actualizar propiedades de modelo con `setProperty()`; nunca con `refresh()` innecesario
- Identificar controles en `onInit` por posición/metadata (`getAggregation`, `getMetadata().getName()`), no por ID global
- **NO** duplicar lógica que ya exista en `App.controller`; centralizar ahí los métodos comunes
- **NO** sobrescribir estilos CSS de SAP; usar clases estándar (`sapUiSmallMargin`, `sapUiResponsiveContentPadding`, etc.) siempre que sea posible
- **NO** usar `alert` / `confirm` del navegador; usar `sap.m.MessageBox` o `sap.m.MessageToast`
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
