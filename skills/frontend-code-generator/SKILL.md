---
name: frontend-code-generator
description: Genera código TypeScript (tipos, servicios mock, stores Zustand) desde especificaciones de diseño. Automatiza transformaciones mecánicas del modelo de datos y servicios a código.
---

# Frontend Code Generator

Genera código TypeScript desde especificaciones de diseño técnico.

## Modos de Operación

| Modo | Entrada | Salida |
|------|---------|--------|
| types | backlog/XX_[modulo].md (primaria) + design/02_data_model.md (acelerador) | frontend/src/modules/[moduleSlug]/types.ts |
| services | backlog/XX_[modulo].md (primaria) + design/03_data_services.md (acelerador) | frontend/src/modules/[moduleSlug]/services/[Entidad]Service.ts (+ [Entidad]ServiceMock.ts) |
| store | backlog/XX_[modulo].md (primaria) + types/services | frontend/src/modules/[moduleSlug]/store/[Entidad]Store.ts |
| all | backlog/XX_[modulo].md (primaria) + design/02 + design/03 (opcionales) | Todos los anteriores |

## Fuente de verdad (IMPORTANTE)

- **Fuente primaria obligatoria:** `backlog/XX_[modulo].md`.
- `design/02_data_model.md` y `design/03_data_services.md` son **aceleradores opcionales** (si existen, ayudan a completar constraints/contratos), pero no sustituyen el backlog.

## Normalización del módulo (OBLIGATORIO)

- `moduleSlug`: kebab-case para carpetas FE, rutas y `data-testid` (ej: `maestro-posiciones`).
- Usar `frontend/src/modules/[moduleSlug]/...` como convención.

## Parámetros opcionales (recomendado para backlogs)

- `minMockRecords` (number): mínimo de registros mock a generar por entidad/servicio.
  - Default: `10`
  - Si el backlog exige “20+ / 30+”, ajustar el valor para cumplir el mínimo.
- `allowUpdatePlaceholders` (boolean): permite **actualizar** archivos existentes que estén vacíos/placeholder (p.ej. `types.ts` con TODO).
  - Default: `true`
- `includePagination` (boolean): genera firma/estructura de respuesta para `getAll(filters?)` con paginación cuando esté especificado.
  - Default: `false`
- `softDelete` (boolean): implementa `delete(id)` como soft-delete si el servicio lo especifica.
  - Default: `false`

## Prerrequisitos

Fuente primaria (OBLIGATORIO):
- `backlog/XX_[modulo].md` - Backlog del módulo siguiendo el template detallado.

Aceleradores (OPCIONAL):
- `design/02_data_model.md` - Modelo de datos con entidades
- `design/03_data_services.md` - Especificación de servicios

Infra (OBLIGATORIO):
- Estructura de carpetas del módulo ya creada

## Modo: Types

Transforma cada entidad del modelo de datos en interfaces TypeScript.

### Restricción del repo: NO usar `enum` (CRÍTICO)

Este proyecto compila TypeScript en un modo que prohíbe sintaxis no “erasable” (por ejemplo `enum`).

Regla obligatoria:
- Para enums de dominio, generar **objetos `as const`** + **tipo union derivado**, nunca `export enum`.

### Entrada (design/02_data_model.md)

```markdown
### Usuario

**Atributos:**
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| id | string | Identificador único | Sí |
| nombre | string | Nombre completo | Sí |
| email | string | Correo electrónico | Sí |
| estado | enum | Estado actual | Sí |
| fechaCreacion | date | Fecha de creación | No |

**Enums asociados:**
- EstadoUsuario: ACTIVO, INACTIVO, PENDIENTE
```

### Salida (frontend/src/modules/[moduleSlug]/types.ts)

```typescript
// Enums de dominio (as const + union type; NO usar `enum`)
export const EstadoUsuario = {
  ACTIVO: 'ACTIVO',
  INACTIVO: 'INACTIVO',
  PENDIENTE: 'PENDIENTE',
} as const;
export type EstadoUsuario = (typeof EstadoUsuario)[keyof typeof EstadoUsuario];

// Entidad principal
export interface Usuario {
  id: string;
  nombre: string;
  email: string;
  estado: EstadoUsuario;
  fechaCreacion?: Date;
}

// Tipos auxiliares para operaciones
export type UsuarioCreate = Omit<Usuario, 'id'>;
export type UsuarioUpdate = Partial<UsuarioCreate>;
export interface UsuarioFilters {
  estado?: EstadoUsuario;
  busqueda?: string;
}
```

## Modo: Services

Genera modo dual **Mock + API**.

Selección de implementación (OBLIGATORIO): patrón **"store elige servicio"**.

- El store importa `Service` y `ServiceMock`.
- El store selecciona implementación usando `SERVICE_MODE`.
- `SERVICE_MODE` se deriva de `VITE_USE_MOCK=true|false` (ver `frontend/src/shared/utils/serviceMode.ts`).

Contrato estándar (OBLIGATORIO)

- Env var única: `VITE_USE_MOCK=true|false`
  - `true` (default): usa servicios mock.
  - `false`: usa servicios que consumen backend.
- Base URL backend: `VITE_API_BASE_URL` (default: `http://localhost:8080/api`).

CSRF (OBLIGATORIO en modo API):
- El backend usa CSRF con cookie HttpOnly.
- Antes de llamadas mutating (POST/PUT/PATCH/DELETE), ejecutar `ensureCsrfToken(API_BASE_URL)`.
- En todas las llamadas API, incluir `credentials: 'include'`.
- Incluir `X-XSRF-TOKEN` desde `getCsrfHeaders()` (o `getAuthHeaders` si ya lo integra).

Nota: en este template existe `frontend/src/shared/utils/serviceMode.ts` con `SERVICE_MODE` y `API_BASE_URL`. Reutilizarlo.

Convención de nombres (OBLIGATORIA): usar **PascalCase** para artefactos de módulo (archivos y símbolos exportados principales).

Archivos generados por entidad (mínimo):
- `frontend/src/modules/[moduleSlug]/services/[Entidad]ServiceMock.ts`
- `frontend/src/modules/[moduleSlug]/services/[Entidad]Service.ts` (API client)

Regla para stores: seleccionar servicio dentro del store con `SERVICE_MODE` (no generar Facade).

### Entrada (design/03_data_services.md)

```markdown
### UsuarioService

**Entidad:** Usuario

#### Métodos
| Método | Descripción | Entrada | Salida |
|--------|-------------|---------|--------|
| getAll | Lista todos los usuarios | filters?: UsuarioFilters | Usuario[] |
| getById | Obtiene usuario por ID | id: string | Usuario |
| create | Crea nuevo usuario | data: UsuarioCreate | Usuario |
```

### Salida (frontend/src/modules/[moduleSlug]/services/UsuarioServiceMock.ts y UsuarioService.ts)

```typescript
import { Usuario, UsuarioCreate, UsuarioFilters } from '../types';

// Datos mock
const mockUsuarios: Usuario[] = [
  { id: '1', nombre: 'Juan Pérez', email: 'juan@example.com', estado: 'ACTIVO' },
  { id: '2', nombre: 'María García', email: 'maria@example.com', estado: 'PENDIENTE' },
  // ... 8 registros más con variedad
];

// Simulación de latencia de red
const delay = (ms: number = 500) => new Promise(resolve => setTimeout(resolve, ms));

export const UsuarioService = {
  async getAll(filters?: UsuarioFilters): Promise<Usuario[]> {
    await delay();
    let result = [...mockUsuarios];
    if (filters?.estado) {
      result = result.filter(u => u.estado === filters.estado);
    }
    if (filters?.busqueda) {
      const q = filters.busqueda.toLowerCase();
      result = result.filter(u => 
        u.nombre.toLowerCase().includes(q) || 
        u.email.toLowerCase().includes(q)
      );
    }
    return result;
  },

  async getById(id: string): Promise<Usuario | undefined> {
    await delay();
    return mockUsuarios.find(u => u.id === id);
  },

  async create(data: UsuarioCreate): Promise<Usuario> {
    await delay();
    const nuevo: Usuario = {
      ...data,
      id: String(mockUsuarios.length + 1),
    };
    mockUsuarios.push(nuevo);
    return nuevo;
  },
};

// Facade (ejemplo)
// (No se genera facade; la selección se hace en el store)
```

## Modo: Store

Genera store Zustand con estado y acciones basadas en el servicio.

### Salida (frontend/src/modules/[moduleSlug]/store/UsuarioStore.ts)

```typescript
import { create } from 'zustand';
import { Usuario, UsuarioFilters, UsuarioCreate } from '../types';
import { UsuarioService } from '../services/UsuarioService';
import { UsuarioServiceMock } from '../services/UsuarioServiceMock';
import { SERVICE_MODE } from '@/shared/utils/serviceMode';

const activeUsuarioService = SERVICE_MODE === 'backend' ? UsuarioService : UsuarioServiceMock;

interface UsuarioState {
  // Estado
  usuarios: Usuario[];
  usuarioSeleccionado: Usuario | null;
  isLoading: boolean;
  error: string | null;
  filters: UsuarioFilters;
  
  // Acciones
  fetchUsuarios: () => Promise<void>;
  fetchUsuarioById: (id: string) => Promise<void>;
  createUsuario: (data: UsuarioCreate) => Promise<void>;
  setFilters: (filters: UsuarioFilters) => void;
  clearError: () => void;
}

export const useUsuarioStore = create<UsuarioState>((set, get) => ({
  // Estado inicial
  usuarios: [],
  usuarioSeleccionado: null,
  isLoading: false,
  error: null,
  filters: {},

  // Acciones
  fetchUsuarios: async () => {
    set({ isLoading: true, error: null });
    try {
      const usuarios = await activeUsuarioService.getAll(get().filters);
      set({ usuarios, isLoading: false });
    } catch (error) {
      set({ error: 'Error al cargar usuarios', isLoading: false });
    }
  },

  fetchUsuarioById: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      const usuario = await activeUsuarioService.getById(id);
      set({ usuarioSeleccionado: usuario ?? null, isLoading: false });
    } catch (error) {
      set({ error: 'Error al cargar usuario', isLoading: false });
    }
  },

  createUsuario: async (data: UsuarioCreate) => {
    set({ isLoading: true, error: null });
    try {
      await activeUsuarioService.create(data);
      await get().fetchUsuarios();
    } catch (error) {
      set({ error: 'Error al crear usuario', isLoading: false });
    }
  },

  setFilters: (filters: UsuarioFilters) => {
    set({ filters });
  },

  clearError: () => set({ error: null }),
}));
```

## Proceso

1. Recibir módulo y modo de generación
2. Leer especificaciones de diseño
3. Filtrar entidades/servicios del módulo
4. Generar código según plantillas
5. Guardar en rutas correspondientes

## Reglas de Transformación

### Tipos de Datos

| Modelo de Datos | TypeScript |
|-----------------|------------|
| string | string |
| number | number |
| boolean | boolean |
| date | Date |
| enum | `const` object `as const` + union type derivado |
| array | Type[] |

### Convenciones de Nombres

| Elemento | Convención |
|----------|------------|
| Interfaces | PascalCase (Usuario) |
| Enums (dominio) | `const` en PascalCase (EstadoUsuario) + `type` homónimo |
| Servicios | PascalCase + Service (UsuarioService) |
| Stores | use + PascalCase + Store (useUsuarioStore) |
| Archivos | PascalCase.ts |

## Restricciones

- Permitido actualizar archivos placeholder/vacíos (p.ej. `types.ts` con TODO) si `allowUpdatePlaceholders=true`
- No reestructurar/refactorizar UI ni módulos ajenos
- Generar al menos `minMockRecords` registros mock con variedad
- Incluir delay de 500ms en servicios mock
- Seguir estructura de carpetas estándar
- NO generar componentes UI (eso es tarea del implementador)

## Recomendaciones de compatibilidad con backlogs

- Si el backlog define tipos/DTOs/Filters que no existen en diseño, NO inventar: delegar al implementador completar manualmente.
- Si el backlog pide filtros/paginación, preferir:
  - `filters?: XFilters & { page?: number; pageSize?: number }`
  - o retornar `{ items, total, page, pageSize }` (según convenciones del repo).
- Si el backlog pide soft-delete: agregar `isDeleted?: boolean` o mantener un set de IDs eliminados.

## Output

```
Código generado para módulo [nombre]:
- Types: frontend/src/modules/[moduleSlug]/types.ts
- Services: X archivos
- Stores: Y archivos
```
```
