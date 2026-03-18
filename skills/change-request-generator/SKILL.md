---
name: change-request-generator
description: Genera un fichero de Change Request (CR) en issues/CR-XXX_*.md usando una plantilla estándar. A partir de una descripción del usuario, completa el detalle del CR; si falta información, pregunta aclaraciones con opciones (A/B/C).
---

# Change Request Generator

Genera un documento Markdown de **Change Request (CR)** en `issues/`.

## Objetivo

- Crear un nuevo fichero `issues/CR-###_<TITULO>.md` con estructura estándar.
- Completar el CR con **detalle accionable** a partir de la descripción del usuario.
- Si falta información imprescindible o hay ambigüedad relevante, **preguntar usando `vscode/askQuestions`** y ofrecer opciones A/B/C (o más si aporta valor).

## Uso de `vscode/askQuestions` (OBLIGATORIO)

Cuando falte información o existan varias interpretaciones plausibles, este skill debe **usar la herramienta** `vscode/askQuestions` (no preguntar “en texto libre” sin tool) para:

- Reducir suposiciones.
- Capturar elecciones de forma estructurada.
- Mantener consistencia de opciones A/B/C.

## Reglas:

- Preguntar **solo lo mínimo imprescindible** para que el CR sea útil.
- Agrupar en **1 llamada** de `vscode/askQuestions` hasta **4 preguntas** relacionadas.
- Cada pregunta debe tener **2–6 opciones**. Marcar una como `recommended` cuando exista una opción claramente estándar.
- Usar `allowFreeformInput: true` solo cuando el usuario probablemente necesite aportar un valor concreto (p.ej. nombre de ruta, roles exactos).
- No continuar con la generación del fichero hasta resolver las preguntas que bloquean el contenido.
- No incluir detalles de implementación o suposiciones en el CR; el CR debe ser un documento de alto nivel, claro y verificable.

Datos mínimos para generar un CR “relleno”:

- Tipo de issue (si no se puede inferir con confianza)
- Resumen (1 línea)
- Descripción detallada (qué y por qué)
- Alcance (lista concreta)
- Criterios de aceptación (lista verificable)

## Recursos del Skill

- Plantilla CR (asset): `assets/cr_template.md`

## Salida esperada

Crear un fichero en `issues/` con nombre:

- Formato recomendado: `issues/CR-###_<Titulo_Corto_Sin_Acentos>.md`
- Regla de slug:
  - Reemplazar espacios por `_`
  - Quitar acentos/ñ (p.ej. `Gestión` → `Gestion`, `Año` → `Ano`)
  - Evitar caracteres especiales

El contenido debe seguir la plantilla y estar **relleno**, no con placeholders.

## Flujo de trabajo

### 1) Recolectar inputs del usuario

A partir del texto del usuario, inferir:

- Tipo de issue (por defecto: `Change / Improvement`)
- Resumen (1 línea)
- Descripción detallada
- Alcance
- Criterios de aceptación

Al finalizar esta fase, ejecutar un **chequeo de completitud**:

- Si alguno de los “datos mínimos” no está presente o es ambiguo → ir a Fase 4 y preguntar con `vscode/askQuestions`.

### 2) Resolver el identificador CR

Buscar ficheros existentes con patrón **CR “de cabecera”** y calcular el siguiente número correlativo.

Regla práctica recomendada al inspeccionar `issues/`:

- Contar solo ficheros que cumplan `CR-###_*.md` (3 dígitos) **y** que NO terminen en `_backlog.md`.
- Si hay colisiones (p.ej. dos ficheros con el mismo `CR-001`), escoger el siguiente número libre.

### 3) Resolver el título del CR

Si el usuario no propone un título claro, inferir un título corto basado en el resumen.

### 4) Preguntas de aclaración (si faltan datos)

Solo preguntar lo mínimo imprescindible para que el CR sea útil.

Cada pregunta debe:

- Indicar qué dato falta y por qué afecta al CR
- Proponer opciones A/B/C (o más si aporta valor)

**Implementación obligatoria:** usar `vscode/askQuestions`.

Guía práctica de preguntas típicas (seleccionar solo las necesarias):

1) **Tipo de issue** (si el usuario no lo deja claro)
  - A) Change / Improvement (default)
  - B) Bugfix
  - C) Spike / Research
2) **Título/Resumen** (si hay varias opciones)
  - A) Título corto orientado a usuario
  - B) Título técnico orientado a componente
  - C) Otro (freeform)
3) **Alcance** (si es demasiado amplio)
  - A) Solo Frontend
  - B) Solo Backend
  - C) Frontend + Backend
4) **Criterios de aceptación** (si no son verificables)
  - A) Aceptación por happy-path + validaciones
  - B) Aceptación por permisos/roles + auditoría
  - C) Otro (freeform)

### 5) Generar el fichero

- Copiar la estructura de `assets/cr_template.md`.
- Sustituir TODOS los placeholders (`{{...}}`) con contenido real.
- Mantener el estilo del ejemplo CR-001:
  - Títulos con `### **...**`
  - Listas con `*` o `-` (consistente dentro del documento)
  - Texto claro, concreto y verificable

## Estándar de salida (para evitar placeholders)

- `{{RESUMEN_CORTO}}` debe ser 1–2 frases, sin contexto interno.
- `{{DESCRIPCION_DETALLADA}}` debe explicar qué se cambia y el motivo.
- `{{ALCANCE_LISTA}}` debe ser una lista con bullets (no un párrafo).
- `{{CRITERIOS_ACEPTACION_LISTA}}` debe ser una lista verificable (idealmente 5–10 ítems cortos).
