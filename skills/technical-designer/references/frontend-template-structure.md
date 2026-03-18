# Estructura Base del Frontend (React)

Esta referencia define la **plantilla de estructura** y convenciones mínimas para el frontend Web del MVP.

## Árbol de Directorios (Frontend)

```
frontend/
├── .env
├── .gitignore
├── components.json                 # Configuración Shadcn/UI
├── eslint.config.js
├── index.html
├── package.json
├── package-lock.json
├── playwright.config.ts            # Configuración Playwright
├── postcss.config.js
├── tailwind.config.ts
├── tsconfig.json
├── tsconfig.app.json
├── tsconfig.node.json
├── vite.config.ts                  # Alias: @ -> src/
├── public/
└── src/
  ├── App.tsx                     # Componente raíz (monta router)
  ├── main.tsx                    # Entry point
  ├── app/
  │   ├── router.tsx              # Rutas (React Router) + AuthGuard
  │   └── layout/
  │       ├── AppLayout.tsx
  │       ├── Header.tsx
  │       ├── Sidebar.tsx
  │       └── components/
  │           └── sidebar/
  │               └── MenuItem.tsx
  ├── components/
  │   └── ui/                     # Componentes Shadcn/UI (primitivos)
  ├── shared/
  │   ├── index.ts                # Barrel exports
  │   ├── components/             # Componentes reutilizables de UI/negocio
  │   ├── templates/              # Plantillas de página (List/Detail/Form)
  │   ├── hooks/
  │   │   └── useAuth.ts
  │   └── utils/
  │       ├── authHeaders.ts
  │       ├── fileUtils.ts
  │       ├── formatters.ts
  │       ├── serviceMode.ts      # SERVICE_MODE + API_BASE_URL
  │       └── validators.ts
  ├── modules/                    # Módulos funcionales (feature-based)
  │   ├── auth/
  │   │   ├── types.ts
  │   │   ├── components/         # AuthGuard/LoginForm
  │   │   ├── pages/              # LoginPage
  │   │   └── services/           # authService + authServiceMock
  │   ├── admin-usuarios/
  │   │   ├── types.ts
  │   │   ├── components/         # formularios/filtros/selección permisos
  │   │   ├── pages/              # list/create/detail/edit (usuarios y roles)
  │   │   ├── services/           # *Service + *ServiceMock (users/roles/permisos)
  │   │   └── store/              # stores del módulo (user/role/permission)
  │   ├── auditoria/
  │   │   ├── types.ts
  │   │   ├── components/         # AuditFiltersBar / AuditTable
  │   │   ├── pages/              # AuditLogPage
  │   │   ├── services/           # auditService + auditServiceMock
  │   │   └── store/              # auditStore
  │   └── [nuevo-modulo]/
  │       ├── types.ts
  │       ├── components/
  │       ├── pages/
  │       ├── services/           # service + serviceMock
  │       └── store/              # opcional, si el módulo lo requiere
  ├── store/
  │   └── authStore.ts            # Zustand store global (sesión)
  ├── hooks/
  │   └── use-toast.ts
  ├── lib/
  │   └── utils.ts
  ├── styles/
  │   └── globals.css
  └── tests/
    └── e2e/                   # Playwright specs
```

## Módulos incluidos en el Template

| Módulo | Descripción |
|--------|-------------|
| auth | Autenticación y login (guard + formulario + servicios mock/backend) |
| admin-usuarios | Administración de usuarios, roles y permisos |
| auditoria | Consulta de logs de actividad y cambios del sistema |

## Convenciones de Nombrado

| Tipo | Convención | Ejemplo |
|------|------------|---------|
| Módulo | kebab-case | `gestion-usuarios` |
| Componente | PascalCase | `UserTable.tsx` |
| Servicio | camelCase + Service | `usuarioService.ts` |
| Store | camelCase + Store | `authStore.ts` |
| Página | PascalCase + Page | `UserListPage.tsx` |
| Tipo/Interface | PascalCase | `Usuario`, `UsuarioFilters` |

## Plantillas de Página Disponibles

| Plantilla | Uso | Componentes internos |
|-----------|-----|---------------------|
| ListPageTemplate | Listados con filtros y tabla | SearchHeader, FilterCard, DataTable, Pagination |
| DetailPageTemplate | Vista de detalle de entidad | PageHeader, DetailCard, DataSection, DataField |
| FormPageTemplate | Formularios de creación/edición | PageHeader, Card con campos |

## Componentes Compartidos (shared/components)

| Componente | Propósito |
|------------|-----------|
| ActionButtons | Botones de acción (Editar, Eliminar, etc.) |
| DataField | Campo de datos con label |
| DataSection | Sección agrupada de campos |
| DataTable | Tabla de datos con columnas configurables |
| DetailCard | Tarjeta para vista de detalle |
| EmptyState | Estado vacío para listas |
| ErrorAlert | Alerta de error |
| FilterCard | Panel de filtros colapsable |
| LoadingState | Indicador de carga |
| PageHeader | Cabecera de página con título y acciones |
| Pagination | Paginación de tablas |
| SearchHeader | Barra de búsqueda |
| StatusBadge | Badge de estado con colores |
| TabBadge | Badge para pestañas con contador |

## Patrón de Servicio Mock

```typescript
// Estructura estándar para servicios mock
const DELAY_MS = 500;
const delay = (ms: number = DELAY_MS) => new Promise(resolve => setTimeout(resolve, ms));

export const nombreService = {
  async getAll(filters?: Filters): Promise<Entidad[]> {
    await delay();
    // Filtrar datos mock según filters
    return mockData;
  },
  
  async getById(id: string): Promise<Entidad | undefined> {
    await delay();
    return mockData.find(item => item.id === id);
  },
  
  async create(data: EntidadCreate): Promise<Entidad> {
    await delay();
    const nuevo = { ...data, id: generateId() };
    mockData.push(nuevo);
    return nuevo;
  },
  
  async update(id: string, data: EntidadUpdate): Promise<Entidad> {
    await delay();
    // Actualizar en mockData
    return updated;
  },
  
  async delete(id: string): Promise<void> {
    await delay();
    // Eliminar de mockData
  }
};
```

## Persistencia

- **Zustand con persist**: Solo para `authStore` (sesión en localStorage)
- **Datos de negocio**: En memoria, se resetean al recargar
- **Datos mock**: Arrays estáticos en cada servicio

## Modo Dual de Servicios (Mock vs Backend)

El frontend debe soportar dos modos de ejecución:

- **Mock (por defecto)**: servicios con datos estáticos y latencia simulada.
- **Backend**: servicios que consumen el API REST (por defecto `http://localhost:8080/api`, configurable).

Convención de conmutación (documental):

- `VITE_USE_MOCK=true|false` (env var única, preferida)
  - `true` (default): usa servicios mock
  - `false`: usa servicios backend
- `VITE_API_BASE_URL=http://localhost:8080/api` (solo si se usa modo backend)

Implementación en el template:

- Selector centralizado: `src/shared/utils/serviceMode.ts`
- Convención de servicios por feature: `algoService.ts` + `algoServiceMock.ts`

## Stack Tecnológico

| Categoría | Tecnología | Versión |
|-----------|------------|---------|
| Framework | React | 19.x |
| Build | Vite | 6.x |
| Lenguaje | TypeScript | Strict |
| Estilos | Tailwind CSS | 4.x |
| Componentes UI | Shadcn/UI + Radix | Latest |
| Estado | Zustand | 5.x |
| Routing | React Router | 7.x |
| Gráficos | Recharts | 3.x |
| Fechas | date-fns | 4.x |
| Iconos | Lucide React | Latest |
