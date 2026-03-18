---
name: ui-prototyper
description: Diseña interfaces de usuario, diagramas de navegación y prototipos textuales (wireframes ASCII) para análisis funcional. Usar cuando se necesite generar las secciones 10, 11 y 12 de un análisis funcional.
---

# UI Prototyper

Genera especificaciones de interfaces, navegación y wireframes textuales.

## Modos

| Modo | Secciones a generar |
|------|---------------------|
| **Completo** | 10, 11, 12 |
| **Prototipo** | 10, 11 (omitir sección 12) |

## Prerrequisitos

- `analisis/05_historias_usuario.md` (HUs)
- `analisis/03_requerimientos_funcionales.md` (RFs)
- `analisis/02_actores_y_roles.md` (actores para navegación)

## Sección 10: Interfaces de Usuario

Especificar pantallas inferidas de las HUs, agrupadas por contexto:

```markdown
## 10. Interfaces de Usuario

### 10.x. <Agrupación>

| Pantalla (ID) | Tipo | Descripción general y Componentes Clave | Roles con acceso | Historia(s) de Usuario |
| :------------ | :--- | :-------------------------------------- | :--------------- | :--------------------- |
| **P-001: Nombre** | Formulario/Lista/Dashboard | Descripción. Componentes: campo1, campo2, botón1 | Actor1, Actor2 | HU-001, HU-002 |
```

### Convención de IDs
IDs consecutivos: P-001, P-002...

### Tipos de pantalla

- Formulario, Lista, Dashboard, Detalle, Modal, Wizard

Guardar como: `analisis/10_interfaces_usuario.md`

## Sección 11: Diagramas de Navegación

Modelar flujo de pantallas por actor/contexto basándose en las pantallas de la Sección 10:

```markdown
## 11. Diagramas de Navegación

### 11.x. <Contexto/Actor>

` ` `mermaid
graph TD
    A[Pantalla Inicio] --> B[Panel Principal]
    B --> C[Sección 1]
    B --> D[Sección 2]
    C --> C1(Detalle)
` ` `
```

### Convenciones

- `[texto]` - Pantalla principal
- `(texto)` - Subpantalla/modal
- Agrupar por actor (Cliente, Operador, Admin)
- Referenciar IDs de pantallas de Sección 10

Guardar como: `analisis/11_diagramas_navegacion.md`

## Sección 12: Prototipo de Interfaz

### ⚠️ REGLA CRÍTICA: Cobertura 100% de Pantallas

**OBLIGATORIO** generar un wireframe por CADA pantalla definida en Sección 10.

- Si Sección 10 tiene 53 pantallas → Sección 12 debe tener 53 wireframes
- **PROHIBIDO** omitir pantallas por ser "similares" o "repetitivas"
- **PROHIBIDO** detenerse antes de completar todas las pantallas
- Cada pantalla P-XXX de Sección 10 debe tener su wireframe P-XXX en Sección 12

Crear wireframe textual (ASCII) por cada pantalla de la Sección 10:

```markdown
## 12. Prototipo de Interfaz

### P-XXX: <Nombre>

` ` `
+-------------------------------------------+
| [Logo]              [Usuario] [Cerrar]    |
|-------------------------------------------|
| TÍTULO DE LA PANTALLA                     |
|                                           |
| Campo 1:    [_________________________]   |
| Campo 2:    [_________________________]   |
|                                           |
| [ ] Opción checkbox                       |
|                                           |
|     [ Cancelar ]    [ Guardar ]           |
+-------------------------------------------+
` ` `
```

### Elementos wireframe

- `[___]` - Campo de texto
- `[ ]` - Checkbox
- `( )` - Radio button
- `[v]` - Dropdown
- `[ Texto ]` - Botón
- `|---|` - Separador/tabla

Guardar como: `analisis/12_prototipos_interfaz.md`

## Reglas

- Generar secciones en orden: 10 → 11 → 12
- Cada pantalla de Sección 10 debe aparecer en diagrama de navegación (Sección 11)
- **OBLIGATORIO: Cada pantalla de Sección 10 debe tener wireframe en Sección 12 (cobertura 100%)**
- Componentes deben reflejar los RFs asociados
- Indicar claramente roles con acceso
- **En modo prototipo: omitir sección 12**
- **NO incluir resúmenes, conclusiones ni secciones adicionales al final del documento**

### Validación Obligatoria Antes de Finalizar

1. Contar pantallas en `10_interfaces_usuario.md` (buscar patrón `P-XXX`)
2. Contar wireframes en `12_prototipos_interfaz.md` (buscar patrón `P-XXX`)
3. **Si cantidad de wireframes < cantidad de pantallas → CONTINUAR generando los faltantes**
4. Solo reportar completado cuando: Wireframes == Pantallas

## Escritura Incremental (Documentos Extensos)

**CRÍTICO**: Para evitar errores de límite de output, generar archivos de forma INCREMENTAL:

### Proceso para `12_prototipos_interfaz.md`
1. **PRIMERO**: Leer `10_interfaces_usuario.md` y contar TODAS las pantallas (P-001 a P-XXX)
2. Crear archivo con encabezado: `## 12. Prototipo de Interfaz`
3. Generar y escribir 5-10 wireframes a la vez
4. Append siguiente bloque usando `replace_string_in_file`
5. **REPETIR hasta cubrir TODAS las pantallas de Sección 10**
6. **NO detenerse** hasta que cantidad de wireframes == cantidad de pantallas
7. **NO acumular todo en memoria**

### ⚠️ Señales de Alerta (CONTINUAR, NO DETENER)
Si durante la generación:
- Has generado 26 wireframes pero hay 53 pantallas → **CONTINUAR con las 27 restantes**
- Sientes que las pantallas son "similares" → **IGUAL generar wireframe individual para cada una**
- El documento se está haciendo largo → **CONTINUAR hasta completar todas**

### Proceso para `10_interfaces_usuario.md` y `11_diagramas_navegacion.md`
1. Crear archivo con encabezado
2. Agregar contenido por agrupación/contexto
3. Máximo 15 pantallas por operación de escritura

### Respuesta del Skill
Al finalizar, reportar solo:
```
Archivo 10_interfaces_usuario.md generado: X pantallas
Archivo 11_diagramas_navegacion.md generado: Y diagramas
Archivo 12_prototipos_interfaz.md generado: Z wireframes
Validación cobertura: ✅ X pantallas = Z wireframes
```

⚠️ **Si X ≠ Z, NO finalizar. Continuar generando wireframes faltantes.**

**NO devolver el contenido completo de los archivos.**
