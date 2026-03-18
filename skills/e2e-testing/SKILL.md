---
name: e2e-testing
description: Genera tests E2E Playwright por pantalla.
---

# E2E Testing (Playwright)

Este skill se usa para **crear/actualizar** el spec E2E de **una pantalla**.

## Inputs (obligatorios)

- Backlog del módulo: `backlog/XX_modulo.md`
  - Fuente para **qué** PF hay que implementar por pantalla (sección `Tests E2E > Tests por PF`).
- Detalle de pruebas funcionales: `analisis/13_pruebas_funcionales.md`
  - Fuente para el **detalle** de cada PF (criterios y resultado esperado).
- `moduleSlug` (kebab-case).
- `screenId` (ej. `P-052`) y `routePath` absoluto (ej. `/configuracion/mascaras`).
- Lista final de `data-testid` de la pantalla (salida del paso UI).

## Output

- `frontend/src/tests/e2e/{moduleSlug}/p-XXX-[pantalla].spec.ts`
  - Debe contener:
    - `Preflight: render de pantalla`
    - 1 test por PF (por ejemplo `PF-269: ...`)

## Flujo de trabajo (OBLIGATORIO)

1) Identificar los PF a implementar para la pantalla
- En `backlog/XX_modulo.md`, localizar la sección `Tests E2E > Tests por PF`.
- Filtrar por `Pantalla P-XXX` (la pantalla objetivo).
- Obtener la lista de IDs `PF-###` que deben existir en el spec de esa pantalla.

2) Extraer el detalle de cada PF
- En `analisis/13_pruebas_funcionales.md`, localizar cada `PF-###` y usar:
  - “Criterios de Aceptación”
  - “Resultado Esperado”
- Si hay discrepancia de texto entre backlog y análisis, la prioridad es:
  1) El **ID PF** (lo que hay que cubrir).
  2) El **detalle** de `analisis/13_pruebas_funcionales.md` para implementar pasos/aseveraciones.

3) Implementar el spec Playwright
- Crear/actualizar `frontend/src/tests/e2e/{moduleSlug}/p-XXX-[pantalla].spec.ts`.
- Estructura mínima:
  - `seedAdminSession()` (o el actor requerido por el PF si no es admin).
  - `openScreen()` a `routePath` y assert del `page` testid.
  - Test `Preflight: render de pantalla`.
  - Un `test('PF-###: ...')` por cada PF requerido.

4) Resolver dependencias del test (sin dejar pendientes)
- Si falta un `data-testid`, añadirlo inmediatamente en la UI (no dejar TODOs).
- Si falta data para cubrir PF en modo mock, añadirla en `frontend/src/modules/{moduleSlug}/services/*ServiceMock.ts`.

## Reglas (OBLIGATORIO)

- El spec se organiza por PF:
  - `test('PF-###: ...', ...)` (no por HU).
- Cada PF debe tener al menos 1 verificación clara del “Resultado Esperado”.
- Selectores:
  - `page.getByTestId()` por defecto.
  - `page.getByRole()` cuando sea más estable/semántico (celdas, opciones, botones con nombre visible).
- Si un PF crea datos (alta/edición), usar valores únicos (por ejemplo `Date.now()`) para evitar colisiones.
- Evitar dependencias entre tests: cada PF debe poder correr aislado.
- **CSRF (API mode)**: el login UI ya obtiene `/csrf` y guarda el token en memoria; no hacer handling manual en los specs salvo que se haga requests directos fuera de la UI.

## Robustez ante variaciones (anti-flakiness)

Aplicar estas reglas cuando el UI/resultado pueda variar sin cambiar la semántica:

- Variaciones de formato (p.ej. OCR/barcodes): preferir aserciones por patrón (regex) o por “contiene” en vez de igualdad exacta.
  - Ejemplo: `expect(text).toMatch(/Code\\s*(39|128)/i)` cuando el formato puede ser `Code 39` o `Code 128`.
- Estados transitorios (p.ej. `PENDIENTE`): esperar a un estado estable antes de asertar resultado final.
  - Usar `expect.poll(...)` o reintentos acotados en vez de `waitForTimeout()` largos.
- Cuando no haya un “outcome” único estable, usar fallback de visibilidad/estado de pantalla:
  - Confirmar que la pantalla siguió navegable y que el mensaje/alerta esperado aparece (o el alternativo válido del flujo).

## Convención `data-testid` (OBLIGATORIO)

Fuente única de verdad:
- `.github/skills/ui-builder/references/testids.md`

## Shadcn/UI (crítico)

### Select

- Nunca usar `page.selectOption()` (no es `<select>`).
- Nunca `SelectItem value=""`; para “Todos” usar sentinel (p. ej. `all`) y mapear.

Patrón recomendado (ya usado en specs del repo):

```ts
await page.getByTestId('{moduleSlug}-select-{campo}').click();
await page.getByRole('option', { name: '{Etiqueta}', exact: true }).click();
await page.waitForTimeout(300);
```

## Plantilla recomendada (alineada con el repo)

```ts
import { test, expect, type Page } from '@playwright/test';

const seedAdminSession = async (page: Page) => {
  await page.goto('/login', { waitUntil: 'domcontentloaded' });
  await expect(page.getByTestId('auth-page-login')).toBeVisible({ timeout: 10000 });
  await page.getByTestId('auth-input-username').fill('admin');
  await page.getByTestId('auth-input-password').fill('admin123');
  await page.getByTestId('auth-btn-login').click();
  await page.waitForFunction(() => Boolean(localStorage.getItem('app_auth')), { timeout: 15000 });
  await expect(page.getByTestId('auth-page-login')).toBeHidden({ timeout: 15000 });
  await page.waitForTimeout(500);
};

const openScreen = async (page: Page) => {
  await page.goto('{routePath}', { waitUntil: 'domcontentloaded' });
  await expect(page.getByTestId('{moduleSlug}-page-{pantalla}')).toBeVisible({ timeout: 10000 });
  await page.waitForTimeout(500);
};

const selectOption = async (page: Page, triggerTestId: string, label: string) => {
  await page.getByTestId(triggerTestId).click();
  await page.getByRole('option', { name: label, exact: true }).click();
  await page.waitForTimeout(300);
};

test.describe('{screenId}: {Pantalla}', () => {
  test('Preflight: render de pantalla', async ({ page }) => {
    await seedAdminSession(page);
    await openScreen(page);
    await expect(page.getByTestId('{moduleSlug}-page-{pantalla}')).toBeVisible({ timeout: 10000 });
  });

  test.beforeEach(async ({ page }) => {
    await seedAdminSession(page);
    await openScreen(page);
  });

  test('PF-XXX: {Nombre PF}', async ({ page }) => {
    // Pasos basados en analisis/13_pruebas_funcionales.md
    // Aserciones basadas en “Resultado Esperado”
    await expect(page.getByTestId('{moduleSlug}-alert-{algo}')).toBeVisible({ timeout: 10000 });
  });
});
```

## Errores comunes (rápido)

| Error | Solución |
|---|---|
| `Element is not a <select> element` | Usar click trigger + `getByRole('option')` (no `page.selectOption()`) |
| `A <Select.Item /> must have a value prop that is not an empty string` | Usar sentinel (`all`) y mapear en lógica |
| `Test timeout exceeded` | Aumentar timeouts (`{ timeout: 10000 }`) y añadir esperas cortas tras acciones |
| Elementos no encontrados | Añadir `data-testid` faltante o esperar render (`toBeVisible({ timeout: 10000 })`) |

## Datos mock

Si la pantalla no renderiza o no permite cubrir PF en modo mock:
- Añadir/ajustar datos en `frontend/src/modules/{moduleSlug}/services/*ServiceMock.ts`.
- Mantener el shape consistente con el API real (campos relevantes).

### Regla de determinismo (CRÍTICO)

Si un PF/E2E depende de registros concretos (IDs específicos, estados, combinaciones de campos), el mock debe ser determinista:
- Crear un dataset estable (por ejemplo un array o mapa por `id`) que incluya explícitamente esos casos.
- Evitar placeholders “genéricos” que cambien los asserts (p.ej. estados por defecto como `PENDIENTE`) salvo que el PF lo requiera.
- Mantener la paridad mock/API en los campos usados por la UI y por los asserts del spec.
