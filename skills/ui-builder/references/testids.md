# Convención canonical de `data-testid`

Este documento es la **fuente única de verdad** para la convención `data-testid` usada por:
- UI Builder
- E2E Testing

## Principios

- Prefijo obligatorio por módulo: `moduleSlug`.
- Formato general: `moduleSlug-<tipo>-<nombre>`.
- `moduleSlug` debe ir en **kebab-case** (ej: `maestro-posiciones`).
- `tipo` debe ser uno de los listados abajo (no inventar nuevos sin necesidad).
- `nombre` en kebab-case, descriptivo, estable (evitar IDs dinámicos).

## Tipos soportados

| Tipo | Uso | Ejemplo |
|------|-----|---------|
| `page` | Contenedor raíz de la vista (`sap.m.Page` o primer contenedor) | `maestro-posiciones-page-listado` |
| `table` | Tablas/listados (`sap.m.Table`, `sap.m.List`) | `maestro-posiciones-table-posiciones` |
| `filter` | Controles de filtros (`sap.m.Input`, `sap.m.Select` en modo filtro) | `maestro-posiciones-filter-departamento` |
| `input` | Inputs clave en formularios (no son filtros) | `maestro-posiciones-input-codigo` |
| `select` | `sap.m.Select` fuera de filtros | `maestro-posiciones-select-estado` |
| `btn` | Botones de acción (`sap.m.Button`) | `maestro-posiciones-btn-crear` |
| `form` | Formulario principal (`sap.ui.layout.form.SimpleForm`, etc.) | `maestro-posiciones-form-posicion` |
| `dialog` | Diálogo/fragmento modal (`sap.m.Dialog`) | `maestro-posiciones-dialog-editar` |
| `alert` | Mensajes de estado/errores (`sap.m.MessageStrip`) | `maestro-posiciones-alert-error` |
| `kpi` | Indicadores/tiles (`sap.m.GenericTile`) | `maestro-posiciones-kpi-total` |

## Reglas mínimas por pantalla

Obligatorio añadir `data-testid` al menos a:
- `page` (siempre)
- `table` (si hay listado)
- `filter`/`select`/`input` (filtros principales)
- `btn` (acciones principales: crear/guardar/exportar)
- `form` (si hay alta/edición)
- `dialog` (si hay modales)

## Cómo añadir `data-testid` en SAPUI5

Declarar el namespace `data` en `<mvc:View>` y usar la sintaxis abreviada en cada control:

```xml
<mvc:View
    xmlns:mvc="sap.ui.core.mvc"
    xmlns:data="http://schemas.sap.com/sapui5/extension/sap.ui.core.CustomData/1"
    ...>

    <Button text="{i18n>create}" press=".onPressCreate" data:testid="maestro-posiciones-btn-crear"/>
    <Table data:testid="maestro-posiciones-table-posiciones">
        ...
    </Table>
```

La propiedad `writeToDom="true"` se aplica automáticamente con la sintaxis abreviada `data:key="value"`.

## Nota OPA5 / Selenium

- Para tests OPA5 nativos de SAPUI5 se puede combinar el `data-testid` con matchers de propiedad (`sap.ui.test.matchers.PropertyStrictEquals`) para mayor robustez.
- Para Selenium/WebdriverIO usar el selector CSS: `[data-testid="maestro-posiciones-btn-crear"]`.
- En `sap.m.Select`, interactuar con el control completo (no con el `<select>` nativo interno); localizar por `data-testid` y disparar el evento de la librería de tests.

## Normalización del módulo (recordatorio)

- `moduleSlug`: kebab-case para rutas y `data-testid`.
- Ejemplo: `maestro-posiciones`.
