---
name: ui5-code-generator
description: Genera código SAP UI5 (modelos, servicios, estado y lógica de control en JavaScript) desde especificaciones de diseño. Automatiza la implementación técnica interna del módulo sin incluir UI, routing ni E2E.
---

# UI5 Code Generator

Genera código JavaScript para SAP UI5 desde especificaciones de diseño técnico.

## Alcance del Skill

Este skill cubre exclusivamente la **implementación técnica interna del módulo**:

- Base técnica
- Modelo de datos
- Servicios
- Estado
- Controladores y lógica
- Testing técnico

Quedan fuera de alcance:
- UI (views XML, fragments)
- Routing / sidebar
- E2E (pantalla, API, MOCK)
- Quality gate frontend
- Entrega

## Fases de Implementación

| Fase | Descripción | Output principal |
|------|-------------|------------------|
| 1. Base técnica del módulo | Setup técnico del módulo | Estructura + configuración |
| 2. Modelo de datos | Definición de entidades y modelos | `model/*.js` |
| 3. Servicios | Integración backend / mock | `services/*.js` |
| 4. Estado y lógica interna | Gestión de estado con `JSONModel` | `model/viewModel.js` |
| 5. Controladores y utilidades | Lógica de interacción y reglas funcionales | `controller/*.controller.js`, `util/*.js` |
| 6. Testing técnico | Tests unitarios y de integración técnica | `test/*.js` |

## Modos de Operación

| Modo | Entrada | Salida |
|------|---------|--------|
| models | `backlog/XX_[modulo].md` (primaria) + `design/02_data_model.md` (acelerador) | `webapp/modules/[moduleName]/model/*.js` |
| services | `backlog/XX_[modulo].md` (primaria) + `design/03_data_services.md` (acelerador) | `webapp/modules/[moduleName]/services/*.js` |
| state | `backlog/XX_[modulo].md` (primaria) + models/services | `webapp/modules/[moduleName]/model/viewModel.js` |
| controllers | `backlog/XX_[modulo].md` (primaria) + models/services | `webapp/modules/[moduleName]/controller/*.controller.js` + `util/*.js` |
| all | `backlog/XX_[modulo].md` (primaria) + `design/02` + `design/03` (opcionales) | Todos los anteriores |

## Fuente de verdad (IMPORTANTE)

- **Fuente primaria obligatoria:** `backlog/XX_[modulo].md`
- `design/02_data_model.md` y `design/03_data_services.md` son **aceleradores opcionales** y no sustituyen el backlog.

## Normalización del módulo (OBLIGATORIO)

- `moduleName`: PascalCase para carpetas y artefactos UI5 (ej: `MaestroPosiciones`)
- `modulePath`: `webapp/modules/[moduleName]/...`
- Mantener convención SAP UI5 por capas: `model`, `services`, `controller`, `util`, `test`

## Parámetros opcionales

- `minMockRecords` (number): mínimo de registros mock a generar por entidad/servicio.
  - Default: `10`
- `allowUpdatePlaceholders` (boolean): permite actualizar archivos existentes vacíos o placeholder.
  - Default: `true`
- `useOwnerComponentModel` (boolean): usar el modelo OData registrado en `OwnerComponent`.
  - Default: `true`
- `generateFormatter` (boolean): genera `util/formatters.js` si hay transformaciones de presentación.
  - Default: `true`
- `includeFiltersInViewModel` (boolean): añade estructura `filters` al `viewModel`.
  - Default: `true`

## Prerrequisitos

Fuente primaria (OBLIGATORIO):
- `backlog/XX_[modulo].md` - Backlog del módulo siguiendo el template detallado.

Aceleradores (OPCIONAL):
- `design/02_data_model.md` - Modelo de datos con entidades
- `design/03_data_services.md` - Especificación de servicios

Infra (OBLIGATORIO):
- Estructura base del módulo ya creada
- Proyecto SAP UI5 operativo

## Estructura generada

```text
webapp/
  modules/
    [moduleName]/
      model/
        models.js
        viewModel.js
      services/
        [Entidad]Service.js
        [Entidad]ServiceMock.js
      controller/
        [Entidad].controller.js
      util/
        formatters.js
        helpers.js
        constants.js
      test/
        [Entidad].test.js
```

## Fase 1: Base técnica del módulo

Preparar la base técnica del módulo SAP UI5 para poder desarrollar su lógica desacoplada de la UI final.

### Output

- estructura de carpetas del módulo
- configuración base de modelos
- integración mínima con `Component.js` o contexto del módulo
- utilidades de inicialización si aplican

### Ejemplo

```javascript
sap.ui.define([
  "sap/ui/model/json/JSONModel"
], function (JSONModel) {
  "use strict";

  return {
    createBaseModel: function () {
      return new JSONModel({
        busy: false,
        error: null
      });
    }
  };
});
```

## Fase 2: Modelo de datos

Transforma cada entidad del modelo de datos en estructuras consumibles por SAP UI5.

### Regla

En SAP UI5 con JavaScript no se generan tipos TypeScript. La salida debe centrarse en:

- estructuras base de datos
- catálogos y constantes de dominio
- funciones de normalización
- shape inicial de modelos JSON

### Transformación

| Modelo de Datos | UI5 JavaScript |
|-----------------|----------------|
| string | string |
| number | number |
| boolean | boolean |
| date | `Date` o string normalizada |
| enum | objeto constante |
| array | Array |

### Ejemplo

```javascript
sap.ui.define([], function () {
  "use strict";

  const EstadoUsuario = {
    ACTIVO: "ACTIVO",
    INACTIVO: "INACTIVO",
    PENDIENTE: "PENDIENTE"
  };

  return {
    EstadoUsuario: EstadoUsuario,

    createUsuarioModelData: function () {
      return {
        id: "",
        nombre: "",
        email: "",
        estado: EstadoUsuario.PENDIENTE,
        fechaCreacion: null
      };
    }
  };
});
```

## Fase 3: Servicios

Genera modo dual **Mock + API**.

### Selección de implementación (OBLIGATORIO)

Patrón **"controller/model elige servicio"**:

- El controlador importa `Service` y `ServiceMock`.
- La selección depende de una constante/configuración del proyecto.
- No generar facade adicional.

### Contrato estándar

- Soporte para modo mock y modo backend
- En modo backend, reutilizar el modelo OData del `OwnerComponent` cuando aplique
- Encapsular `read`, `create`, `update`, `remove` o llamadas REST equivalentes
- Gestionar errores técnicos y transformarlos en mensajes manejables por controlador

### Archivos generados por entidad

- `webapp/modules/[moduleName]/services/[Entidad]ServiceMock.js`
- `webapp/modules/[moduleName]/services/[Entidad]Service.js`

### Ejemplo Mock

```javascript
sap.ui.define([], function () {
  "use strict";

  const delay = function (ms) {
    return new Promise(function (resolve) {
      setTimeout(resolve, ms || 500);
    });
  };

  const mockUsuarios = [
    { id: "1", nombre: "Juan Pérez", email: "juan@example.com", estado: "ACTIVO" },
    { id: "2", nombre: "María García", email: "maria@example.com", estado: "PENDIENTE" }
  ];

  return {
    getAll: async function (filters) {
      await delay(500);
      let result = mockUsuarios.slice();

      if (filters && filters.estado) {
        result = result.filter(function (item) {
          return item.estado === filters.estado;
        });
      }

      return result;
    },

    getById: async function (id) {
      await delay(500);
      return mockUsuarios.find(function (item) {
        return item.id === id;
      });
    }
  };
});
```

### Ejemplo API

```javascript
sap.ui.define([], function () {
  "use strict";

  return {
    getAll: function (oModel, sEntitySet, oFilters) {
      return new Promise(function (resolve, reject) {
        oModel.read(sEntitySet, {
          filters: oFilters || [],
          success: function (oData) {
            resolve(oData.results || []);
          },
          error: function (oError) {
            reject(oError);
          }
        });
      });
    }
  };
});
```

## Fase 4: Estado y lógica interna

Genera el estado del módulo usando `JSONModel`.

### Regla

En UI5, el equivalente al store de React/Zustand es un `JSONModel` local/global.

### Salida

- `viewModel.js`
- estado inicial del módulo
- flags funcionales (`busy`, `error`, `editMode`, `selectedId`, etc.)
- filtros y contexto funcional

### Ejemplo

```javascript
sap.ui.define([
  "sap/ui/model/json/JSONModel"
], function (JSONModel) {
  "use strict";

  return {
    createViewModel: function () {
      return new JSONModel({
        usuarios: [],
        usuarioSeleccionado: null,
        busy: false,
        error: null,
        editMode: false,
        filters: {
          busqueda: "",
          estado: ""
        }
      });
    }
  };
});
```

## Fase 5: Controladores y utilidades

Genera la lógica de control del módulo y sus utilidades reutilizables.

### Incluye

- controladores por entidad o caso de uso
- handlers de eventos
- carga inicial de datos
- lógica de orquestación entre servicios y modelos
- formatters
- helpers
- constantes del dominio
- reglas de habilitación/visibilidad derivadas del estado

### Ejemplo Controller

```javascript
sap.ui.define([
  "sap/ui/core/mvc/Controller",
  "../services/UsuarioService",
  "../services/UsuarioServiceMock"
], function (Controller, UsuarioService, UsuarioServiceMock) {
  "use strict";

  const USE_MOCK = true;
  const activeService = USE_MOCK ? UsuarioServiceMock : UsuarioService;

  return Controller.extend("app.modules.MaestroPosiciones.controller.Usuario", {
    onInit: function () {
      this._loadUsuarios();
    },

    _loadUsuarios: async function () {
      const oViewModel = this.getView().getModel("view");
      oViewModel.setProperty("/busy", true);
      oViewModel.setProperty("/error", null);

      try {
        const aUsuarios = await activeService.getAll(oViewModel.getProperty("/filters"));
        oViewModel.setProperty("/usuarios", aUsuarios);
      } catch (e) {
        oViewModel.setProperty("/error", "Error al cargar usuarios");
      } finally {
        oViewModel.setProperty("/busy", false);
      }
    }
  });
});
```

### Ejemplo Formatter

```javascript
sap.ui.define([], function () {
  "use strict";

  return {
    formatEstadoText: function (sEstado) {
      if (!sEstado) {
        return "";
      }

      return sEstado.charAt(0) + sEstado.slice(1).toLowerCase();
    }
  };
});
```

## Fase 6: Testing técnico

Genera pruebas técnicas de nivel unitario y de integración interna.

### Alcance

- servicios mock
- helpers
- formatters
- lógica aislable de controladores
- transformaciones de datos

### Ejemplo

```javascript
QUnit.module("UsuarioServiceMock", function () {
  QUnit.test("getAll devuelve datos", async function (assert) {
    const data = await UsuarioServiceMock.getAll();
    assert.ok(data.length > 0, "Debe devolver datos mock");
  });
});
```

## Proceso

1. Recibir módulo y modo de generación
2. Leer backlog y aceleradores de diseño
3. Filtrar entidades/servicios del módulo
4. Generar base técnica del módulo
5. Generar modelos y constantes
6. Generar servicios mock y API
7. Generar `viewModel`
8. Generar controladores y utilidades
9. Generar tests técnicos
10. Guardar en rutas correspondientes

## Reglas de Transformación

### Convenciones de nombres

| Elemento | Convención |
|----------|------------|
| Módulos | PascalCase (`MaestroPosiciones`) |
| Servicios | PascalCase + `Service` (`UsuarioService`) |
| Servicios mock | PascalCase + `ServiceMock` |
| Controladores | `[Entidad].controller.js` |
| Utilidades | `formatters.js`, `helpers.js`, `constants.js` |
| Models | `models.js`, `viewModel.js` |
| Tests | `[Entidad].test.js` |

## Restricciones

- Permitido actualizar archivos placeholder/vacíos si `allowUpdatePlaceholders=true`
- No reestructurar UI ni módulos ajenos
- Generar al menos `minMockRecords` registros mock con variedad
- Incluir delay de 500ms en servicios mock
- Seguir estructura estándar del módulo
- NO generar XML Views
- NO generar routing
- NO generar navegación global
- NO generar E2E
- NO incluir quality gate ni entrega

## Recomendaciones de compatibilidad con backlogs

- Si el backlog define campos o contratos no detallados, no inventar reglas funcionales complejas: dejar comentarios `TODO` para completar manualmente.
- Si el backlog pide filtros, reflejarlos en `viewModel` y en la firma de `getAll`.
- Si el backlog pide catálogos, generarlos como constantes reutilizables.
- Si el backlog pide validaciones, implementarlas como helpers o lógica aislable, no embebidas en la vista.

## Output

```text
Código generado para módulo [nombre]:
- Base técnica: webapp/modules/[moduleName]/
- Models: webapp/modules/[moduleName]/model/
- Services: webapp/modules/[moduleName]/services/
- Controllers: webapp/modules/[moduleName]/controller/
- Utils: webapp/modules/[moduleName]/util/
- Tests: webapp/modules/[moduleName]/test/
```
