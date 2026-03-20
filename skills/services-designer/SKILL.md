---
name: services-designer
description: Genera especificación de servicios para un MVP. Soporta dos modos&#58; (A) full-stack React+Java (frontend mock/backend + contratos API REST) y (B) SAP (SAPUI5 + ABAP OData V2/V4). Usar cuando se necesite crear design/03_data_services.md. Requiere design/01 y design/02 (o design/02_abap_data_model.md en modo SAP).
---

# Services Designer

Genera especificación de servicios para MVP full-stack o SAP.

## Modo de Operación

Determinar el modo **antes de comenzar** inspeccionando los ficheros de diseño disponibles:

| Modo | Indicadores | Fichero de salida |
|------|-------------|-------------------|
| **A – Full-stack** (React + Java) | Existe `design/02_data_model.md` o stack Java/React en `design/01_technical_design.md` | `design/03_data_services.md` |
| **B – SAP** (SAPUI5 + ABAP + OData) | Existe `design/02_abap_data_model.md` o stack SAP/UI5/OData en `design/01_technical_design.md` | `design/03_odata_services.md` |

Si ambos existen (proyecto híbrido), generar ambos ficheros y indicarlo al usuario.

## Objetivo del Skill

**Modo A – Full-stack:**
- Definir contratos de servicios consistentes para:
   - Frontend en modo **mock** (por defecto)
   - Frontend en modo **backend** (consumo de API REST)
   - Backend (endpoints REST) a alto nivel
- Evitar duplicar el modelo de datos: entidades, atributos y enums se referencian desde `design/02_data_model.md`.
- Estandarizar paginación, filtros, ordenamiento, autenticación/autorización y modelo de error.

**Modo B – SAP:**
- Definir contratos de servicios OData (V2 via SEGW o V4 via RAP) para cada EntitySet expuesto.
- Documentar EntitySets, NavigationProperties, FunctionImports (V2) / Actions y Functions (V4 RAP).
- Especificar el consumo desde SAPUI5 usando `sap.ui.model.odata.v2.ODataModel` o `sap.ui.model.odata.v4.ODataModel`.
- Evitar duplicar el modelo ABAP: entidades y tablas se referencian desde `design/02_abap_data_model.md`.
- Estandarizar parámetros OData (`$filter`, `$top`, `$skip`, `$orderby`, `$expand`), autorización SAP y modelo de error OData.

## Prerrequisitos

### Modo A – Full-stack (React + Java)

Imprescindibles:
- `design/01_technical_design.md` - Módulos + rutas UI + endpoints (alto nivel)
- `design/02_data_model.md` - Modelo de datos con entidades
- `analisis/03_requerimientos_funcionales.md` - RFs con operaciones
- `analisis/10_interfaces_usuario.md` - Pantallas con acciones de usuario

Recomendados:
- `analisis/05_historias_usuario.md` - HUs con acciones
- `analisis/06_casos_uso.md` - Casos de uso (mejoran nombres de endpoints/casos)
- `analisis/08_integraciones.md` - Integraciones externas (WordAid, SAP, SSO)
- `analisis/09_diagramas_estados.md` - Estados/transiciones (validaciones y restricciones por estado)
- `analisis/12_prototipos_interfaz.md` - Acciones de UI no evidentes (botones "Probar/Validar/Restaurar", confirmaciones)

### Modo B – SAP (SAPUI5 + ABAP + OData)

Imprescindibles:
- `design/01_technical_design.md` - Paquetes SAP + rutas UI (manifest.json routes) + EntitySets (alto nivel)
- `design/02_abap_data_model.md` - Modelo ABAP con tablas DDIC, CDS Views y objetos RAP/SEGW
- `analisis/03_requerimientos_funcionales.md` - RFs con operaciones
- `analisis/10_interfaces_usuario.md` - Pantallas SAPUI5 con acciones de usuario

Recomendados:
- `analisis/05_historias_usuario.md` - HUs con acciones
- `analisis/06_casos_uso.md` - Casos de uso (mejoran nombres de EntitySets/FunctionImports)
- `analisis/08_integraciones.md` - Integraciones externas (BAPIs, RFC, sistemas externos)
- `analisis/09_diagramas_estados.md` - Estados/transiciones (validaciones por estado en ABAP)
- `analisis/12_prototipos_interfaz.md` - Acciones SAPUI5 no evidentes (botones, confirmaciones MessageBox)

## Estructura de Salida

Generar los ficheros de servicios según el modo detectado (`design/03_data_services.md` para Modo A, `design/03_odata_services.md` para Modo B):

**Convenciones globales Modo A – Full-stack (agregar al inicio del documento antes del catálogo):**
- Modo dual frontend:
   - Por defecto: `mock`
   - Conmutación: `VITE_USE_MOCK=false` y `VITE_API_BASE_URL`
- Latencia mock: `setTimeout(500ms)` para todos los métodos mock (salvo que se indique lo contrario).
- Modelo de error (texto, no TS): `code`, `message`, `details` opcional, `correlationId` opcional.
- Wrapper backend (recomendado en este repo): `ApiResponse<T>` con campos `{ success, message, data }`.
  - Si se usa, reflejarlo en "Notas del contrato" para que Frontend implemente el unwrap de `.data` y el manejo de error coherente.
- Listados: preferir retorno paginado `{ items, total, page, pageSize }` cuando aplique.
- Ordenamiento: `sortBy`, `sortDir` (`asc|desc`) cuando aplique.
- Convención de filtros por fecha: usar sufijos `Desde/Hasta` con el campo (p.ej. `fechaEmisionDesde`, `fechaEmisionHasta`).

**Convenciones globales Modo B – SAP OData (agregar al inicio del documento antes del catálogo):**
- Protocolo: OData V2 (SEGW) o V4 (RAP) según `design/01_technical_design.md`.
- URL base: `/sap/opu/odata/<namespace>/<SERVICIO>/` (V2) o `/sap/opu/odata4/<namespace>/<SERVICIO>/` (V4).
- Autenticación: SAP Logon / SSO (SAML2); en ABAP usar `AUTHORITY-CHECK OBJECT '...'` antes de ejecutar lógica de negocio. No usar JWT salvo indicación explícita en el análisis.
- Modo mock SAPUI5: usar `sap.ui.core.util.MockServer` con ficheros `metadata.xml` + fixtures JSON en `webapp/localService/mockdata/`. Activar controlado por parámetro de arranque (`?mock=true`); la UI no cambia.
- Paginación OData: `$top` / `$skip` (V2) o `$top` / `$skip` + `$count=true` (V4). No usar wrapper de paginación propio.
- Filtros: parámetros `$filter` con operadores OData (`eq`, `ne`, `gt`, `ge`, `lt`, `le`, `substringof` en V2 / `contains` en V4, `startswith`).
- Ordenamiento: `$orderby=<campo> asc|desc`.
- Expansión de navegación: `$expand=<NavigationProperty>` para cargar entidades relacionadas en una sola llamada.
- Modelo de error OData: `{ "error": { "code": "...", "message": { "lang": "es", "value": "..." }, "innererror": {...} } }`. Documentar los códigos de error ABAP que DPC_EXT puede devolver en "Notas del contrato".
- FunctionImports (V2) / Actions y Functions (V4 RAP): verbo `POST` para acciones con efecto secundario; verbo `GET` para funciones de solo lectura.
- Nombres: EntitySets en PascalCase con sufijo `Set` (ej. `PedidoSet`), NavigationProperties en PascalCase, FunctionImport/Action en PascalCase (ej. `ValidarPedido`, `AnularDocumento`).

### 1. Catálogo de Servicios

**Modo A:**

| Servicio | Entidad Principal | Módulo | Descripción |
|----------|-------------------|--------|-------------|
| UsuarioService | Usuario | auth | Gestión de usuarios del sistema |
| EmbarqueService | Embarque | seguimiento-embarques | Gestión de embarques de importación |

**Modo B:**

| Servicio OData | Versión | EntitySet Principal | Paquete SAP | Descripción |
|----------------|---------|---------------------|-------------|-------------|
| ZGW_MM_PEDIDO | V2 (SEGW) | PedidoSet | ZMM | Gestión de cabeceras de pedido |
| ZGW_MM_PEDIDO | V2 (SEGW) | PedidoPosSet | ZMM | Gestión de posiciones de pedido |

### 2. Detalle por Servicio

**Modo A** — Para cada servicio:

```markdown
### UsuarioService

**Entidad:** Usuario

#### Métodos

| Método | Descripción | Entrada | Salida |
|--------|-------------|---------|--------|
| getAll | Lista todos los usuarios | filters?: UsuarioFilters | Usuario[] |
| getById | Obtiene usuario por ID | id: string | Usuario |
| create | Crea nuevo usuario | data: UsuarioCreate | Usuario |
| update | Actualiza usuario | id: string, data: UsuarioUpdate | Usuario |
| delete | Elimina usuario | id: string | void |

#### API REST (modo backend)

Tabla de endpoints para este servicio (evitar usar columna “Método” aquí para no confundir con la tabla de métodos anterior):

| HTTP | Path | Caso de uso / Recurso | Auth | Notas |
|------|------|------------------------|------|-------|
| GET | /api/usuarios | Listado | Protegido | Paginación/filtros |
| GET | /api/usuarios/{id} | Detalle | Protegido | |

#### Implementación de Frontend (modelo dual)

- **Mock:** existe `...ServiceMock` con datos estáticos y latencia.
- **Backend:** existe `...Service` que consume los endpoints anteriores.
- La UI no cambia: conmutación global por `VITE_USE_MOCK`.

**Notas del contrato (si aplica):**
- Indicar validaciones relevantes (p.ej. “si estado != BORRADOR no permite delete”).
- Indicar efectos colaterales esperados (p.ej. “create genera Historial/Alerta”).

#### Filtros (si aplica)
| Filtro | Tipo | Descripción |
|--------|------|-------------|
| estado | string | Filtrar por estado |
| busqueda | string | Búsqueda por nombre/email |

#### Datos Mock
- Cantidad: 10 registros ficticios
- Variedad: diferentes estados, roles
```

---

**Modo B** — Para cada servicio OData, usar esta plantilla:

```markdown
### ZGW_<MODULO>_<NOMBRE> (OData V2 / SEGW  ó  OData V4 / RAP)

**Paquete SAP:** Z<MODULO>
**URL base:** `/sap/opu/odata/sap/ZGW_<MODULO>_<NOMBRE>/`
**Autorización SAP:** `AUTHORITY-CHECK OBJECT 'Z_<MOD>_<OBJ>'`
**ABAP – Clase DPC_EXT:** `ZCL_<MODULO>_DPC_EXT`
**ABAP – Clase MPC_EXT:** `ZCL_<MODULO>_MPC_EXT`

#### EntitySets

| EntitySet | CDS View / Tabla DDIC | Descripción |
|-----------|----------------------|-------------|
| <Entidad>Set | Z<MOD>_R_<NOMBRE> / Z<MOD>_T_<NOMBRE> | Descripción funcional |

#### Operaciones por EntitySet

| EntitySet | HTTP | OData Operation | Descripción | Auth Object / ACTVT | Notas |
|-----------|------|-----------------|-------------|---------------------|-------|
| <Entidad>Set | GET | GetEntitySet | Listado con $filter/$top/$skip | Z_<MOD>_OBJ / 03 | Soporta $expand si aplica |
| <Entidad>Set | GET | GetEntity | Detalle por clave | Z_<MOD>_OBJ / 03 | |
| <Entidad>Set | POST | CreateEntity | Crear | Z_<MOD>_OBJ / 01 | |
| <Entidad>Set | PUT/MERGE | UpdateEntity | Actualizar | Z_<MOD>_OBJ / 02 | MERGE para actualización parcial |
| <Entidad>Set | DELETE | DeleteEntity | Eliminar | Z_<MOD>_OBJ / 06 | Solo si estado lo permite |

#### FunctionImports (V2) / Actions y Functions (V4 RAP)

| Nombre | HTTP | Descripción | Parámetros de entrada | Retorno | Notas |
|--------|------|-------------|----------------------|---------|-------|
| <NombreAccion> | POST | Descripción de la acción | Param1: Edm.String, ... | <Entidad> o void | Condiciones de uso |

#### NavigationProperties

| Desde | Hacia | Cardinalidad | Descripción |
|-------|-------|--------------|-------------|
| <EntidadPadreSet> | <EntidadHijaSet> | 1:N | Descripción relación |

#### Implementación SAPUI5 (modelo dual)

- **Mock (MockServer):** `webapp/localService/metadata.xml` + fixtures JSON en `webapp/localService/mockdata/<Entidad>Set.json`.
  - Activar en `webapp/test/mockServer.js`; `Component.js` detecta parámetro `?mock=true`.
- **Backend (ODataModel):** `sap.ui.model.odata.v2.ODataModel` configurado en `manifest.json` con `serviceUrl: /sap/opu/odata/sap/ZGW_<MODULO>_<NOMBRE>/`.
  - La UI no cambia entre modos.

**Notas del contrato (si aplica):**
- Indicar validaciones en ABAP (p.ej. "si estado != BORRADOR no permite DELETE").
- Indicar efectos colaterales (p.ej. "CreateEntity genera entrada en Z<MODULO>_T_AUDIT").
- Documentar códigos de error OData que DPC_EXT puede devolver.

#### Filtros $filter soportados (si aplica)
| Campo OData | Tipo Edm | Operadores soportados | Descripción |
|-------------|----------|-----------------------|-------------|
| <Campo> | Edm.String / Edm.DateTime / Edm.Boolean | eq, ne, substringof, ge, le | Descripción |

#### Datos Mock (MockServer)
- Cantidad: 10 registros ficticios por EntitySet
- Variedad: diferentes estados y combinaciones relevantes para los RFs
```

### 3. Matriz Servicio-RF

**Modo A:**

| Servicio | Método | RF Asociado | Descripción RF |
|----------|--------|-------------|----------------|
| EmbarqueService | registrarDesdeShippingPlan | RF-001 | Registro automático de contratos desde shipping plans |
| EmbarqueService | consultarNaviera | RF-002 | Consulta automática a navieras |

**Modo B:**

| Servicio OData | EntitySet / FunctionImport | RF Asociado | Descripción RF |
|----------------|---------------------------|-------------|----------------|
| ZGW_MM_PEDIDO | PedidoSet (CreateEntity) | RF-001 | Registro de pedido personalizado |
| ZGW_MM_PEDIDO | ValidarPedido (FunctionImport) | RF-002 | Validación previa al envío |

## Convenciones de Métodos / Operaciones

### Modo A – Full-stack

| Operación | Método Estándar | Patrón |
|-----------|-----------------|--------|
| Listar | getAll | Retorna array, acepta filtros |
| Obtener | getById | Recibe ID, retorna uno |
| Crear | create | Recibe data, retorna creado |
| Actualizar | update | Recibe ID + data, retorna actualizado |
| Eliminar | delete | Recibe ID, retorna void |
| Buscar | search | Recibe query, retorna array |

**Consistencia y no-redundancia (CRÍTICO):**
- No repetir atributos de entidades ni valores de enums: referenciar `design/02_data_model.md`.
- Los nombres de filtros deben coincidir entre la fila de `getAll/search` y la sección "Filtros (si aplica)".
- Evitar `fechaDesde/fechaHasta` genéricos; usar el nombre del campo.

### Modo B – SAP OData

| Operación OData | HTTP | Patrón |
|----------------|------|--------|
| Query (listar) | GET | `<EntitySet>?$filter=...&$top=N&$skip=M&$orderby=...&$expand=...` |
| Read (detalle) | GET | `<EntitySet>('<clave>')` |
| Create | POST | `<EntitySet>` con body JSON |
| Update (completo) | PUT | `<EntitySet>('<clave>')` con body JSON |
| Update (parcial) | MERGE/PATCH | `<EntitySet>('<clave>')` con delta |
| Delete | DELETE | `<EntitySet>('<clave>')` |
| FunctionImport / Action | POST/GET | `/<Nombre>?Param1=val1&...` |

**Consistencia y no-redundancia (CRÍTICO):**
- No repetir atributos ABAP ni dominios DDIC: referenciar `design/02_abap_data_model.md`.
- Los campos `$filter` deben coincidir con los campos reales expuestos en la CDS Projection View.
- No inventar EntitySets que no tengan tabla DDIC o CDS View correspondiente.
- Los FunctionImports / Actions deben tener trazabilidad con RFs o CUs concretos.

## Proceso

### Modo A – Full-stack

1. Leer modelo de datos `design/02_data_model.md` (entidades)
2. Crear un servicio por entidad principal
3. Definir métodos CRUD básicos
4. Añadir métodos específicos según RFs, CUs y prototipos (OBLIGATORIO):
   - Acciones no-CRUD derivadas de prototipos (p.ej. `validate`, `testAccess`, `restoreDefaults`, `inUseInfo`)
   - Validaciones/confirmaciones derivadas de flujos alternativos
   - Restricciones por estado (si aplica por diagramas de estados)
5. Documentar parámetros de entrada/salida
6. Guardar `design/03_data_services.md`

### Modo B – SAP OData

1. Leer `design/02_abap_data_model.md` e identificar tablas DDIC y CDS Views/RAP por entidad
2. Agrupar EntitySets por proyecto SEGW / servicio RAP (no al crear uno por entidad)
3. Para cada entidad, definir el EntitySet y sus operaciones CRUD con los objetos de autorización correspondientes
4. Añadir NavigationProperties a partir de las relaciones del modelo ABAP
5. Añadir FunctionImports / Actions / Functions derivados de RFs, CUs y prototipos (OBLIGATORIO):
   - Acciones no-CRUD: validaciones, transiciones de estado, cálculos, llamadas a BAPIs/RFC
   - Restricciones por estado (cruzar con `analisis/09_diagramas_estados.md`)
6. Documentar parámetros Edm.*, autorización SAP y notas de contrato por EntitySet/FunctionImport
7. Guardar `design/03_odata_services.md`

## Restricciones

### Modo A
- NO generar código TypeScript
- Describir tipos de forma textual
- Referenciar entidades del modelo de datos (`design/02_data_model.md`)
- NO fijar un mecanismo de auth si el análisis define SSO (documentar "SSO/JWT según integración")

### Modo B
- NO generar código ABAP (responsabilidad del skill `abap-code-generator`)
- Describir tipos usando Edm.* (`Edm.String`, `Edm.Int32`, `Edm.DateTime`, `Edm.Boolean`, `Edm.Decimal`)
- Referenciar EntitySets y CDS Views del modelo ABAP (`design/02_abap_data_model.md`)
- NO inventar EntitySets sin respaldo en tablas DDIC o CDS Views del modelo ABAP
- NO usar patrones REST propios (wrapper `ApiResponse`, `VITE_USE_MOCK`, etc.); respetar el estándar OData
- NO confundir FunctionImport (V2) con Action/Function (V4 RAP); indicar siempre la versión OData usada

## Escritura Incremental (Documentos Extensos)

**CRÍTICO**: Para evitar errores de límite de output, generar archivo de forma INCREMENTAL en ambos modos:

### Proceso de Escritura (Modo A)

1. **Crear archivo** con encabezado y sección 1 (catálogo de servicios)
2. **Agregar servicios al catálogo** usando `replace_string_in_file` (máx. 10 por operación)
3. **Agregar detalle de cada servicio** (append al final, 3-5 servicios a la vez)
4. **Agregar matriz Servicio-RF** al final

### Proceso de Escritura (Modo B)

1. **Crear archivo** con encabezado, convenciones OData y sección 1 (catálogo de servicios OData)
2. **Agregar servicios al catálogo**: filas de la tabla de servicios OData (máx. 10 por operación)
3. **Agregar detalle de cada servicio OData** (append al final, 2-3 servicios a la vez con EntitySets, operaciones, FunctionImports, NavigationProperties)
4. **Agregar matriz Servicio-RF** al final

### Respuesta del Skill

**NO devolver contenido completo** del archivo. Solo confirmar:

**Modo A:**
```
Archivo design/03_data_services.md generado:
- Servicios: X
- Métodos totales: Y
```

**Modo B:**
```
Archivo design/03_odata_services.md generado:
- Servicios OData: X
- EntitySets: Y
- FunctionImports/Actions: Z
```

## Output

**Modo A:**
```
Archivo design/03_data_services.md generado:
- Servicios: X
- Métodos totales: Y
```

**Modo B:**
```
Archivo design/03_odata_services.md generado:
- Servicios OData: X
- EntitySets: Y
- FunctionImports/Actions: Z
```
