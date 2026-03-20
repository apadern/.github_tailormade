---
name: e2e-testing
description: Genera tests E2E con OPA5 (SAPUI5) por pantalla para validar carga de vista, interacción con controles, navegación y validación de estados.
---

# E2E Testing — SAPUI5 (OPA5)

Crear pruebas automáticas por pantalla para validar que cada vista del módulo carga correctamente, muestra los controles esperados y permite ejecutar los flujos básicos.

**Framework principal**: OPA5 (`sap/ui/test/Opa5`) — integrado en SAPUI5/QUnit.  
**Alternativa**: wdi5 (WebdriverIO + SAPUI5) si el proyecto lo tiene configurado.

> **Exclusiones**: no incluye validación integral extremo a extremo del módulo completo; no incluye pruebas de rendimiento; no incluye cobertura exhaustiva de casos negativos salvo los definidos en alcance.

---

## Inputs (obligatorios)

- Backlog del módulo: `backlog/XX_modulo.md`
  - Fuente para **qué** PF hay que implementar por pantalla (sección `Tests E2E > Tests por PF`).
- Detalle de pruebas funcionales: `docs/analisis/13_pruebas_funcionales.md`
  - Fuente para el **detalle** de cada PF (criterios y resultado esperado).
- `moduleSlug` (kebab-case, ej. `facturas`).
- `screenId` (ej. `P-052`) y `viewName` de la vista SAPUI5 (ej. `Facturas`).
- `routeHash` — hash de navegación (ej. `#/facturas`).
- IDs de controles relevantes de la vista (del XML view correspondiente).

---

## Output (estructura de ficheros)

```
webapp/test/integration/
  {Feature}Journey.js          ← nuevo Journey por pantalla/funcionalidad
  pages/
    {ViewName}.js              ← Page Object para la vista
  AllJourneys.js               ← actualizar para incluir el nuevo Journey
```

Cada Journey debe contener:
- `opaTest("Preflight: carga de vista", ...)` — verifica que la vista se renderiza.
- Un `opaTest("PF-###: ...", ...)` por cada PF requerido.

---

## Flujo de trabajo (OBLIGATORIO)

### 1) Identificar los PF a implementar para la pantalla
- En `backlog/XX_modulo.md`, localizar la sección `Tests E2E > Tests por PF`.
- Filtrar por `Pantalla P-XXX` (la pantalla objetivo).
- Obtener la lista de IDs `PF-###` que deben existir en el Journey de esa pantalla.

### 2) Extraer el detalle de cada PF
- En `docs/analisis/13_pruebas_funcionales.md`, localizar cada `PF-###` y usar:
  - "Criterios de Aceptación"
  - "Resultado Esperado"
- Prioridad ante discrepancias: primero el **ID PF**, luego el detalle del análisis.

### 3) Crear/actualizar el Page Object (`pages/{ViewName}.js`)
- Implementar en `actions` los métodos de interacción (pulsar botón, introducir texto, seleccionar ítem).
- Implementar en `assertions` los métodos de verificación (vista visible, control presente, mensaje mostrado).
- Referenciar controles por `id` + `viewName` siempre que sea posible.

### 4) Crear el Journey (`{Feature}Journey.js`)
- Importar el Page Object de la vista y cualquier otro necesario para la navegación.
- Usar `Given.iStartMyApp()` para iniciar la aplicación.
- Usar `When` para acciones y `Then` para aserciones.
- Añadir `Then.iTeardownMyApp()` al final del último test del Journey.

### 5) Registrar en `AllJourneys.js`
- Añadir el nuevo Journey al `sap.ui.define` del fichero `AllJourneys.js`.

### 6) Resolver dependencias sin dejar pendientes
- Si un control carece de `id` estable en el XML view, añadirlo antes de continuar.
- Si se requieren datos mock, inyectarlos en el modelo JSON o en el fixture del componente.

## Reglas (OBLIGATORIO)

- Los tests se organizan por PF: `opaTest("PF-###: ...", ...)` (no por HU).
- Cada PF debe tener al menos 1 aserción clara del "Resultado Esperado".
- **Selectores** (por orden de preferencia):
  1. `id` + `viewName` — más estable y explícito.
  2. `controlType` + `properties` — cuando no hay ID fiable.
  3. `bindingPath` — para controles ligados a modelos OData/JSON.
- Usar `autoWait: true` en la configuración global (activo en `AllJourneys.js`).
- Evitar dependencias entre tests: cada `opaTest` debe poder correr de forma aislada.
- No usar `setTimeout` fijos; confiar en el mecanismo de polling de OPA5.

## Robustez ante variaciones (anti-flakiness)

- **Estados transitorios** (p. ej. `Pendiente`): asertar sobre el estado estable final, o verificar el mensaje de transición con `waitFor` + `properties`.
- **Textos dinámicos**: usar `matchers` como `sap/ui/test/matchers/PropertyStrictEquals` o comparar con la clave i18n resuelta, no con texto hardcoded.
- **Tablas/listas con datos variables**: verificar que el agregado `items` tenga longitud ≥ 1, no una longitud exacta salvo que el fixture sea determinista.
- **Diálogos y NavContainer**: esperar con `waitFor` + `controlType: "sap.m.Dialog"` o `"sap.m.Page"` en lugar de delays.

## Patrones OPA5 por tipo de control

### Verificar que una vista está visible

```javascript
this.waitFor({
    id: "page",
    viewName: "{ViewName}",
    success: function () {
        Opa5.assert.ok(true, "La vista {ViewName} está visible");
    },
    errorMessage: "No se encontró la vista {ViewName}"
});
```

### Pulsar un botón

```javascript
iClickTheButton: function (sButtonId) {
    return this.waitFor({
        id: sButtonId,
        viewName: "{ViewName}",
        actions: new Press(),
        errorMessage: "No se encontró el botón " + sButtonId
    });
}
```

### Introducir texto en un Input

```javascript
iEnterTextInField: function (sInputId, sText) {
    return this.waitFor({
        id: sInputId,
        viewName: "{ViewName}",
        actions: new EnterText({ text: sText }),
        errorMessage: "No se encontró el campo " + sInputId
    });
}
```

### Seleccionar ítem en un sap.m.Select

```javascript
iSelectOption: function (sSelectId, sKey) {
    return this.waitFor({
        id: sSelectId,
        viewName: "{ViewName}",
        actions: new Press(),
        success: function () {
            this.waitFor({
                controlType: "sap.ui.core.Item",
                matchers: new PropertyStrictEquals({ name: "key", value: sKey }),
                actions: new Press(),
                errorMessage: "No se encontró la opción con key " + sKey
            });
        },
        errorMessage: "No se encontró el Select " + sSelectId
    });
}
```

### Verificar texto en un control

```javascript
iShouldSeeText: function (sControlId, sExpectedText) {
    return this.waitFor({
        id: sControlId,
        viewName: "{ViewName}",
        matchers: new PropertyStrictEquals({ name: "text", value: sExpectedText }),
        success: function () {
            Opa5.assert.ok(true, "Texto '" + sExpectedText + "' visible en " + sControlId);
        },
        errorMessage: "Texto esperado no encontrado en " + sControlId
    });
}
```

### Verificar que una tabla tiene filas

```javascript
iShouldSeeTableWithItems: function (sTableId) {
    return this.waitFor({
        id: sTableId,
        viewName: "{ViewName}",
        matchers: new AggregationFilled({ name: "items" }),
        success: function () {
            Opa5.assert.ok(true, "La tabla " + sTableId + " tiene filas");
        },
        errorMessage: "La tabla " + sTableId + " no tiene filas"
    });
}
```

---

## Plantilla Journey (`{Feature}Journey.js`)

```javascript
/*global QUnit*/
sap.ui.define([
    "sap/ui/test/opaQunit",
    "./pages/{ViewName}"
], function (opaTest) {
    "use strict";

    QUnit.module("{screenId}: {Nombre Pantalla}");

    opaTest("Preflight: carga de vista", function (Given, When, Then) {
        Given.iStartMyApp({ hash: "{routeHash}" });

        Then.on{ViewName}Page.iShouldSeeThe{ViewName}View();

        Then.iTeardownMyApp();
    });

    opaTest("PF-XXX: {Nombre PF}", function (Given, When, Then) {
        Given.iStartMyApp({ hash: "{routeHash}" });

        // Pasos basados en docs/analisis/13_pruebas_funcionales.md
        When.on{ViewName}Page.iClickTheButton("{buttonId}");

        // Aserciones basadas en "Resultado Esperado"
        Then.on{ViewName}Page.iShouldSeeText("{controlId}", "{textoEsperado}");

        Then.iTeardownMyApp();
    });
});
```

---

## Plantilla Page Object (`pages/{ViewName}.js`)

```javascript
sap.ui.define([
    "sap/ui/test/Opa5",
    "sap/ui/test/actions/Press",
    "sap/ui/test/actions/EnterText",
    "sap/ui/test/matchers/PropertyStrictEquals",
    "sap/ui/test/matchers/AggregationFilled"
], function (Opa5, Press, EnterText, PropertyStrictEquals, AggregationFilled) {
    "use strict";

    var sViewName = "{ViewName}";

    Opa5.createPageObjects({
        on{ViewName}Page: {

            actions: {

                iClickTheButton: function (sButtonId) {
                    return this.waitFor({
                        id: sButtonId,
                        viewName: sViewName,
                        actions: new Press(),
                        errorMessage: "No se encontró el botón " + sButtonId
                    });
                },

                iEnterTextInField: function (sInputId, sText) {
                    return this.waitFor({
                        id: sInputId,
                        viewName: sViewName,
                        actions: new EnterText({ text: sText }),
                        errorMessage: "No se encontró el campo " + sInputId
                    });
                }

            },

            assertions: {

                iShouldSeeThe{ViewName}View: function () {
                    return this.waitFor({
                        id: "page",
                        viewName: sViewName,
                        success: function () {
                            Opa5.assert.ok(true, "La vista " + sViewName + " está visible");
                        },
                        errorMessage: "No se encontró la vista " + sViewName
                    });
                },

                iShouldSeeText: function (sControlId, sExpectedText) {
                    return this.waitFor({
                        id: sControlId,
                        viewName: sViewName,
                        matchers: new PropertyStrictEquals({ name: "text", value: sExpectedText }),
                        success: function () {
                            Opa5.assert.ok(true, "Texto '" + sExpectedText + "' visible");
                        },
                        errorMessage: "Texto '" + sExpectedText + "' no encontrado en " + sControlId
                    });
                },

                iShouldSeeTableWithItems: function (sTableId) {
                    return this.waitFor({
                        id: sTableId,
                        viewName: sViewName,
                        matchers: new AggregationFilled({ name: "items" }),
                        success: function () {
                            Opa5.assert.ok(true, "La tabla " + sTableId + " tiene filas");
                        },
                        errorMessage: "La tabla " + sTableId + " está vacía"
                    });
                }

            }
        }
    });
});
```

---

## Errores comunes (rápido)

| Error | Solución |
|---|---|
| `Control with ID not found` | Verificar que el ID existe en el XML view y que `viewName` es correcto |
| `Timeout waiting for control` | Activar `autoWait: true` en `Opa5.extendConfig` o aumentar `timeout` en `waitFor` |
| `Cannot read properties of undefined` en `success` | El control existe pero la propiedad esperada no — revisar el nombre de la propiedad |
| `AggregationFilled` falla en tabla vacía | El fixture de datos no carga — revisar el modelo JSON/OData mock |
| `Press` no abre el Select | El control es `sap.m.ComboBox` o `sap.m.MultiComboBox`; ajustar la acción según el tipo |
| Journey no se ejecuta | Verificar que está importado en `AllJourneys.js` |

## Datos mock / fixtures

Si la vista no renderiza datos o no permite cubrir un PF:
- Para **modelos JSON**: añadir los datos en el modelo definido en `Component.js` o en `models.js`.
- Para **OData mock**: añadir entidades en la carpeta `localService/mockdata/` (ficheros JSON por EntitySet).
- Mantener shape consistente con el servicio real (mismos campos usados por la UI y por los asserts).

### Regla de determinismo (CRÍTICO)

Si un PF depende de registros concretos (IDs específicos, estados, combinaciones de campos), el mock debe ser determinista:
- Crear un dataset estable con los casos necesarios explícitamente definidos.
- Evitar datos generados aleatoriamente que cambien los asserts entre ejecuciones.
- Mantener la paridad mock/servicio real en los campos usados por la UI y por las aserciones del Journey.
