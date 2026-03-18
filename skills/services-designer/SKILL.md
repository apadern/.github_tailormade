---
name: services-designer
description: Genera especificación de servicios (frontend mock/backend + contratos API REST) para un MVP full-stack. Usar cuando se necesite crear design/03_data_services.md. Requiere design/01 y design/02.
---

# Services Designer

Genera especificación de servicios para MVP full-stack.

## Objetivo del Skill

- Definir contratos de servicios consistentes para:
   - Frontend en modo **mock** (por defecto)
   - Frontend en modo **backend** (consumo de API)
   - Backend (endpoints REST) a alto nivel
- Evitar duplicar el modelo de datos: entidades, atributos y enums se referencian desde `design/02_data_model.md`.
- Estandarizar paginación, filtros, ordenamiento, autenticación/autorización y modelo de error.

## Prerrequisitos

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

## Estructura de Salida

Generar `design/03_data_services.md` con:

**Convenciones globales (agregar al inicio del documento antes del catálogo, o como subsección corta):**
- Modo dual frontend:
   - Por defecto: `mock`
   - Conmutación: `VITE_USE_MOCK=false` y `VITE_API_BASE_URL`
- Latencia mock: `setTimeout(500ms)` para todos los métodos mock (salvo que se indique lo contrario).
- Modelo de error (texto, no TS): `code`, `message`, `details` opcional, `correlationId` opcional.
- Wrapper backend (recomendado en este repo): `ApiResponse<T>` con campos `{ success, message, data }`.
  - Si se usa, reflejarlo en “Notas del contrato” para que Frontend implemente el unwrap de `.data` y el manejo de error coherente.
- Listados: preferir retorno paginado `{ items, total, page, pageSize }` cuando aplique.
- Ordenamiento: `sortBy`, `sortDir` (`asc|desc`) cuando aplique.
- Convención de filtros por fecha: usar sufijos `Desde/Hasta` con el campo (p.ej. `fechaEmisionDesde`, `fechaEmisionHasta`).

### 1. Catálogo de Servicios

| Servicio | Entidad Principal | Módulo | Descripción |
|----------|-------------------|--------|-------------|
| UsuarioService | Usuario | auth | Gestión de usuarios del sistema |
| EmbarqueService | Embarque | seguimiento-embarques | Gestión de embarques de importación |

### 2. Detalle por Servicio

Para cada servicio:

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

### 3. Matriz Servicio-RF

| Servicio | Método | RF Asociado | Descripción RF |
|----------|--------|-------------|----------------|
| EmbarqueService | registrarDesdeShippingPlan | RF-001 | Registro automático de contratos desde shipping plans |
| EmbarqueService | consultarNaviera | RF-002 | Consulta automática a navieras |

## Convenciones de Métodos

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
- Los nombres de filtros deben coincidir entre la fila de `getAll/search` y la sección “Filtros (si aplica)”.
- Evitar `fechaDesde/fechaHasta` genéricos; usar el nombre del campo.

## Proceso

1. Leer modelo de datos (entidades)
2. Crear un servicio por entidad principal
3. Definir métodos CRUD básicos
4. Añadir métodos específicos según RFs, CUs y prototipos (OBLIGATORIO):
   - Acciones no-CRUD derivadas de prototipos (p.ej. `validate`, `testAccess`, `restoreDefaults`, `inUseInfo`)
   - Validaciones/confirmaciones derivadas de flujos alternativos
   - Restricciones por estado (si aplica por diagramas de estados)
5. Documentar parámetros de entrada/salida
6. Guardar `design/03_data_services.md`

## Restricciones

- NO generar código TypeScript
- Describir tipos de forma textual
- Referenciar entidades del modelo de datos
- NO fijar un mecanismo de auth si el análisis define SSO (documentar “SSO/JWT según integración”)

## Escritura Incremental (Documentos Extensos)

**CRÍTICO**: Para evitar errores de límite de output, generar archivo de forma INCREMENTAL:

### Proceso de Escritura

1. **Crear archivo** con encabezado y sección 1:
   ```markdown
   # Especificación de Servicios
   
   ## 1. Catálogo de Servicios
   
   | Servicio | Entidad Principal | Módulo | Descripción |
   |----------|-------------------|--------|-------------|
   ```

2. **Agregar servicios al catálogo** usando `replace_string_in_file`:
   - Insertar filas en la tabla del catálogo
   - Máximo 10 servicios por operación

3. **Agregar detalle de cada servicio** (append al final):
   - Escribir 3-5 servicios a la vez con sus métodos completos
   - Append siguiente bloque hasta completar todos
   - **NO acumular todo en memoria**

4. **Agregar matriz Servicio-RF** al final:
   - Append sección 3 con tabla de relaciones

### Patrón de Append

```markdown
## 2. Detalle por Servicio

### UsuarioService

**Entidad:** Usuario

#### Métodos
...

### ExpedienteService

**Entidad:** Expediente

#### Métodos
...
```

Luego append siguiente bloque:
```markdown

### DocumentoService

**Entidad:** Documento

#### Métodos
...
```

### Respuesta del Skill

**NO devolver contenido completo** del archivo. Solo confirmar:

```
Archivo design/03_data_services.md generado:
- Servicios: X
- Métodos totales: Y
```

## Output

```
Archivo design/03_data_services.md generado:
- Servicios: X
- Métodos totales: Y
```
