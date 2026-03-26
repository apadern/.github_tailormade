---
name: technical-designer
description: Genera el diseño técnico para un MVP SAP (SAPUI5 + CAP + ABAP). Usar cuando se necesite crear design/01_technical_design.md con arquitectura modular, rutas UI, entidades OData y objetos ABAP. Requiere análisis funcional previo (carpeta analisis).
---

# Technical Designer

Genera documento de diseño técnico para un MVP SAP con arquitectura de tres capas: **frontend SAPUI5 + middleware CAP + backend ABAP S/4HANA**.

## Objetivo del Skill

- Producir un diseño técnico consistente y accionable para **SAPUI5 + CAP + ABAP**, sin duplicar el detalle del modelo de datos ni de la especificación de servicios/contratos.
- Asegurar coherencia de nombres (módulos/rutas UI/entidades OData/objetos ABAP) y trazabilidad mínima (RF → módulo → rutas UI → entidades OData → objetos ABAP).

## Prerrequisitos

Este skill puede usar cualquier información relevante en `analisis/`.

Imprescindibles (MVP SAP):
- `analisis/01_objetivo_y_alcance.md` - Alcance/no-alcance y objetivos
- `analisis/02_actores_y_roles.md` - Roles/permisos y accesos (UI + OData + ABAP autorización)
- `analisis/03_requerimientos_funcionales.md` - RFs (base para módulos)
- `analisis/10_interfaces_usuario.md` - Pantallas (IDs P-XXX) para mapeo UI→módulo
- `analisis/11_diagramas_navegacion.md` - Flujos y navegación (rutas UI / manifest.json)

Recomendados (mejoran calidad del diseño):
- `analisis/04_requerimientos_tecnicos.md` - Restricciones no funcionales (seguridad, rendimiento, despliegue BTP/S4)
- `analisis/06_casos_uso.md` - Secuencias de casos de uso (derivar acciones OData / FM / BAPI)
- `analisis/07_diagramas_procesos.md` - Procesos (sincronizaciones/envíos, jobs batch ABAP)
- `analisis/08_integraciones.md` - Integraciones externas (SAP estándar, RFC/BAPI, APIs externas)
- `analisis/09_diagramas_estados.md` - Estados/transiciones (derivar acciones OData y autorización ABAP)
- `analisis/12_prototipos_interfaz.md` - Acciones de UI no evidentes (botones, confirmaciones, diálogos)

## Referencias

- Ver [references/UI5-template-structure.md](references/UI5-template-structure.md) para estructura de módulos SAPUI5 (webapp layout, controller/view/model)
- Ver [references/CAP-template-structure.md](references/CAP-template-structure.md) para estructura CAP (srv/, db/, app/, cds namespaces, handlers)
- Ver [references/ABAP-template-structure.md](references/ABAP-template-structure.md) para estructura ABAP (paquetes, DDIC, clases, OData SEGW)


## Stack Tecnológico (Fijo)

Frontend — SAPUI5:
- SAPUI5 (OpenUI5) con XMLViews + Controllers (JavaScript / TypeScript)
- Routing definido en `manifest.json` (sap.ui5 → routing → routes/targets)
- Modelos: `sap.ui.model.odata.v4.ODataModel` (producción) o `sap.ui.model.json.JSONModel` (modo mock local)
- Capa de servicios con modo dual: **mock (por defecto, localService/)** o **OData real** (conmutable por parámetro de arranque)

Middleware — SAP CAP:
- SAP Cloud Application Programming Model (CAP) — Node.js (preferido) o Java
- CDS para definición de modelos y servicios (`.cds`)
- Exposición como OData V4 (protocolo estándar hacia SAPUI5)
- Autenticación/autorización: XSUAA (SAP BTP) con atributos de rol
- Integración con ABAP S/4HANA vía RFC, BAPI, OData ABAP (RAP) o API SAP estándar

Backend — ABAP S/4HANA:
- ABAP Objects (clases, interfaces) en paquetes `Z<MODULO>`
- DDIC: tablas transparentes (`Z<MODULO>_T_*`), estructuras, tipos de tabla
- Exposición externa: Function Modules RFC o proyectos OData SEGW / RAP
- Autorización: `AUTHORITY-CHECK OBJECT` en cada punto de entrada
- Logging: SLG1 / wrapper `ZCL_<MODULO>_LOGGER`

## Estructura de Salida

Generar `design/01_technical_design.md` con exactamente estas 3 secciones:

### 1. Resumen Ejecutivo
Máximo 15 líneas describiendo alcance y enfoque.

**Incluir obligatoriamente (sin crear secciones adicionales):**
- Alcance / no-alcance del MVP (frontend SAPUI5 + middleware CAP + backend ABAP S/4HANA).
- Supuestos del MVP: persistencia en SAP HANA (vía CAP/HDI) o tablas ABAP Z, seguridad mediante XSUAA (BTP) y `AUTHORITY-CHECK` en ABAP, documentación CDS/OData metadata, integraciones con SAP estándar (BAPIs/APIs) si están en alcance.
- Modelo dual frontend: por defecto **frontend-only (mock con localService/)** y opción de conectar al OData CAP real sin cambiar las vistas.
- Referencias cruzadas:
	- El detalle de entidades CDS y tablas ABAP vive en `design/02_data_model.md`.
	- El detalle de entidades OData, acciones/funciones y contratos vive en `design/03_data_services.md`.

### 2. Arquitectura Modular

Usar estructura de [references/UI5-template-structure.md](references/UI5-template-structure.md) para la capa SAPUI5.

Para CAP, respetar la estructura CDS (`srv/`, `db/`, `app/`) del repositorio.

Para ABAP, respetar [references/ABAP-template-structure.md](references/ABAP-template-structure.md) y/o la estructura real de paquetes en el sistema.

Listar módulos identificados de los RFs:

| Módulo | Descripción | RFs Asociados |
|--------|-------------|---------------|
| auth | Autenticación XSUAA y control de sesión | Transversal |
| gestion-usuarios | Gestión de usuarios, roles ABAP y permisos BTP | RF-001, RF-002... |
| auditoria | Consulta de logs SLG1 y auditoría de cambios | RF-AUD... |

**Además, dentro de esta misma sección (como subsecciones o bullets):**
- Capas de arquitectura (alto nivel):
	- **SAPUI5 (Frontend)**: XMLViews → Controllers → ODataModel V4 (o JSONModel mock) → CAP OData service.
	- **CAP (Middleware)**: CDS service definitions → service handlers (Node.js/Java) → ABAP APIs (RFC/BAPI/RAP OData).
	- **ABAP (Backend)**: Function Modules / RAP entities → clases de servicio (`ZCL_*_SRV`) → DAOs (`ZCL_*_DAO`) → DDIC (tablas Z).
- Convenciones transversales (solo enunciadas): prefijos de objeto `Z<MODULO>_`, fechas ISO 8601, paginación OData (`$skip`/`$top`), modelo de errores OData (`error.message`), logging SLG1.
- Convenciones del modelo dual SAPUI5 (solo enunciadas):
		- Modo por defecto: `mock` (datos locales en `localService/mockdata/`).
		- Conmutación: parámetro de URL `?responderType=realOData` o variable en `Component.js` / `manifest.json` (`"mockRequests": false`).
		- El `Component.js` inicializa el modelo: en modo mock usa `sap.ui.core.util.MockServer`; en modo real usa `sap.ui.model.odata.v4.ODataModel` apuntando al servicio CAP.
		- Selector único de modo en `Component.js` o en `model/models.js`; los controllers y vistas no leen directamente el modo.
		- Los controllers no acceden a datos mock directamente; todo pasa por el modelo vinculado (binding OData o JSONModel).
- Reglas de acoplamiento:
	- Las XMLViews no contienen lógica de negocio; solo binding declarativo.
		- Los controllers delegan en el modelo OData/JSON; no hacen llamadas `fetch`/`jQuery.ajax` directas salvo servicios de acción (`callFunction`/`invoke`).
		- CAP handlers no contienen lógica SQL directa contra HANA; delegan en entidades CDS o en llamadas a ABAP.
		- ABAP DAOs acceden solo a tablas Z propias; las tablas estándar SAP se consumen desde la capa de servicio ABAP mediante BAPIs/APIs SAP estándar.
	- Los objetos ABAP expuestos externamente (FM RFC / DPC_EXT) aplican `AUTHORITY-CHECK` antes de cualquier lógica.

### 3. Estructura de Rutas

Mapeo de pantallas a rutas SAPUI5 basado en `11_diagramas_navegacion.md`. Una sola tabla con todas las rutas declaradas en el `manifest.json` (`sap.ui5 → routing → routes`), indicando a qué módulo pertenecen y qué pantalla representan. Plantilla OBLIGATORIA:

```
### Rutas UI (SAPUI5 - manifest.json)

| Nombre de Ruta | Pattern | Target / Vista | Módulo |
|----------------|---------|----------------|--------|
| RouteUsuarios  | usuarios | UsuariosView   | gestion-usuarios |
| RouteDetalle   | usuarios/{id} | DetalleView | gestion-usuarios |
```

**Reglas de consistencia:**
- Los nombres de ruta (`name`) deben ser únicos y usar PascalCase con prefijo `Route`.
- Los `pattern` usan kebab-case, coherentes con el nombre del módulo.
- Evitar duplicar el detalle de pantallas (campos/acciones); eso se deriva de `analisis/10_interfaces_usuario.md`.

Además, incluir el catálogo de entidades y acciones OData del servicio CAP (alto nivel, sin detallar propiedades). Una sola tabla con todos los entity sets y acciones/funciones del servicio, indicando operaciones permitidas, módulo CAP y autorización requerida. Plantilla OBLIGATORIA:

```
### Entidades y Acciones OData (CAP — OData V4)

| EntitySet / Acción | Tipo | Operaciones CRUD / Llamada | Módulo CAP | Autorización ABAP |
|---------------------|------|---------------------------|------------|-------------------|
| Usuarios            | Entity | GET, POST, PATCH, DELETE | usuarios | Z_USUARIOS_DISP |
| Roles               | Entity | GET | usuarios | Z_ROLES_DISP |
| AprobarFactura      | Action (bound) | POST | facturas | Z_FACT_APRO |
```

**Reglas de consistencia (OData/CAP):**
- Los EntitySets siguen PascalCase plural; las acciones/funciones usan verbos en PascalCase.
- El servicio CAP expone la ruta base `/odata/v4/<NombreServicio>/` (definida en el `.cds`).
- Las acciones bound se declaran sobre la entidad a la que pertenecen (`bound to <Entity>`).
- Las operaciones de lectura (GET list/detail) se mapean a `@readonly`; escritura a handlers `on('CREATE')`, `on('UPDATE')`, `on('DELETE')`.
- Declarar explícitamente qué entidades/acciones requieren autorización XSUAA (scope/rol BTP) y qué `AUTHORITY-CHECK` ABAP se invoca en el handler CAP.
- Incluir acciones **no-CRUD** cuando el análisis/prototipo lo implique (p.ej. `Aprobar`, `Rechazar`, `Validar`, `EnviarNotificacion`), sin detallar payload.

## Restricciones

- NO generar código ABAP, CDS, JavaScript ni XML
- NO incluir configuración de herramientas (xs-app.json, mta.yaml, package.json, .cdsrc)
- NO detallar entidades CDS ni tablas ABAP (eso es del skill abap-data-modeler)
- NO detallar entidiades CDS CAP (eso es del skill cap-data-modeler) 
- NO detallar propiedades OData ni contratos de acción (eso es del skill services-designer)
- NO detallar bindings ODataModel V4, estructura de JSONModels, ResourceModel, mock data ni asignación de modelos por vista (eso es del skill ui5-data-modeler)
- NO inventar módulos no presentes en RFs/diagramas; si se requiere un módulo transversal (p.ej. auth/xsuaa), justificarlo como "transversal" y mantenerlo mínimo.

## Proceso

1. Leer `analisis/` (priorizar 01, 02, 03, 10, 11; luego 04, 06, 07, 08, 09, 12)
2. Identificar módulos agrupando RFs (alineados con paquetes ABAP `Z<MODULO>` y CDS namespaces)
3. Mapear rutas SAPUI5 desde diagramas de navegación (`manifest.json` routes/patterns)
4. Proponer entidades OData y acciones CAP por módulo (alto nivel) coherentes con RFs
5. Mapear cada entidad/acción CAP a su objeto ABAP correspondiente (FM RFC / BAPI / RAP entity)
6. Generar `design/01_technical_design.md`

## Reglas para Validación de Diseño (Fase 4)

Cuando se use `scripts/validate_design.py` en validación:

- No se permite cerrar validación con errores críticos > 0.
- Está prohibido justificar errores críticos como "Fase 2", "posterior" o equivalentes.
- Si hay warnings, la justificación debe ser individual por warning en `design/check-design-warnings.md`.
- Para validar justificaciones usar `scripts/validate_warning_justifications.py`.
- Las justificaciones genéricas o por diferimiento a fases futuras deben considerarse inválidas.

## Output

```
Archivo design/01_technical_design.md generado:
- Módulos: X
- Rutas SAPUI5 (manifest.json): Y
- Entidades/Acciones OData (CAP): Z
- Objetos ABAP referenciados: W
```
