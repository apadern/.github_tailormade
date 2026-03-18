---
name: user-stories-generator
description: Genera Historias de Usuario (HU) y Casos de Uso (CU) con trazabilidad 1:1 desde requerimientos funcionales sintetizados. Usar cuando se necesite generar las secciones 5-6 de un análisis funcional.
---

# User Stories Generator

Genera HUs y CUs exhaustivos a partir de RFs sintetizados.

## Modos

| Modo | Secciones a generar |
|------|--------------------||
| **Completo** | 5, 6 |
| **Prototipo** | 5 (omitir sección 6) |

## Prerrequisitos

- `analisis/03_requerimientos_funcionales.md` (RFs sintetizados)
- `analisis/02_actores_y_roles.md` (actores para HUs)

## Sección 5: Historias de Usuario

Generar una HU por cada RF, organizada por módulo:

```markdown
## 5. Historias de Usuario

### 5.x Módulo: <Nombre>

#### **HU-xxx: <Título>**
**Como** <actor>
**Quiero** <necesidad>
**Para** <valor>

**Criterios de aceptación:**
- [ ] ...
- [ ] ...

**ID Requerimientos relacionados:** RF-xxx, RF-yyy
```

### Reglas HUs

- IDs consecutivos: HU-001, HU-002...
- Cada HU debe mapear al menos un RF (trazabilidad)
- Criterios de aceptación específicos y verificables
- Guardar como: `analisis/05_historias_usuario.md`

## Sección 6: Casos de Uso

### ⚠️ REGLA CRÍTICA: Relación 1:1 ESTRICTA entre CU y HU

**PROHIBIDO** agrupar múltiples HUs en un solo CU. Cada HU debe tener su propio CU individual.

❌ **INCORRECTO** (agrupación prohibida):
```markdown
#### CU-25: Generación de reportes (Jefe de Compras)
* **ID HU Asociada:** HU-066, HU-067, HU-068, HU-069
```

✅ **CORRECTO** (1:1 estricto):
```markdown
#### CU-66: Generación de reporte de importaciones por período (Jefe de Compras)
* **ID HU Asociada:** HU-066

#### CU-67: Generación de reporte de costos por importación (Analista de Costos)
* **ID HU Asociada:** HU-067

#### CU-68: Exportación de reportes a Excel y PDF (Jefe de Compras)
* **ID HU Asociada:** HU-068

#### CU-69: Programación de envío automático de reportes (Jefe de Compras)
* **ID HU Asociada:** HU-069
```

### Formato de Caso de Uso

Generar **exactamente UN CU por cada HU**:

```markdown
## 6. Casos de Uso

### 6.x Módulo: <Nombre>

#### CU-xxx: <Título específico> (<Actor>)
* **ID HU Asociada:** HU-xxx (SOLO UNA)
* **Descripción:** <párrafo describiendo el caso específico>
* **Actor Principal:** <actor>
* **Actores Secundarios:** <lista o "Ninguno">
* **Precondiciones:**
    * <items específicos para este caso>
* **Flujo Principal:**
    1) ...
    2) ...
    (mínimo 5 pasos detallados)
* **Flujos Alternativos:**
    * FA1: ...
* **Postcondiciones:**
    * <items>
```

### Reglas CUs

- **OBLIGATORIO: Relación 1:1 - Cada CU tiene exactamente UNA HU asociada**
- **OBLIGATORIO: El número de CUs debe ser IGUAL al número de HUs**
- IDs consecutivos: CU-001, CU-002... (mismo número que la HU correspondiente cuando sea posible)
- El título del CU debe ser específico para la funcionalidad de esa HU individual
- Incluir flujos alternativos basados en RBs y DCs aplicables a ESE caso específico
- Si una HU parece "pequeña", el CU debe detallar igualmente su flujo completo
- Guardar como: `analisis/06_casos_uso.md`
- **En modo prototipo: omitir esta sección**

### Validación Antes de Finalizar

Verificar que:
1. Cantidad de CUs == Cantidad de HUs
2. Cada CU tiene **exactamente UNA** HU en "ID HU Asociada"
3. No hay comas ni múltiples HU-xxx en ningún campo "ID HU Asociada"

## Reglas Generales

- Actualizar `debug.md` con conteo de HUs y CUs por módulo
- **NO incluir resúmenes, conclusiones ni secciones adicionales al final del documento**

## Escritura Incremental (Documentos Extensos)

**CRÍTICO**: Para evitar errores de límite de output, generar archivos de forma INCREMENTAL:

### Proceso para `05_historias_usuario.md`
1. Crear archivo con encabezado: `## 5. Historias de Usuario`
2. Por cada módulo: agregar sección con `replace_string_in_file` (append al final)
3. Máximo 10 HUs por operación de escritura
4. **Contar HUs generadas** para validar contra CUs

### Proceso para `06_casos_uso.md`
1. Crear archivo con encabezado: `## 6. Casos de Uso`
2. Generar y escribir 5-10 CUs a la vez
3. **CADA CU debe tener UNA SOLA HU - NUNCA agrupar**
4. Append siguiente bloque hasta completar TODAS las HUs
5. **NO acumular todo en memoria**
6. **Verificar al final: Cantidad CUs == Cantidad HUs**

### ⚠️ Señales de Alerta (DETENER y CORREGIR)
Si durante la generación detectas que:
- Estás asignando múltiples HUs a un CU → **PARAR, dividir en CUs individuales**
- El número de CU no coincide con el de HU → **PARAR, generar los CUs faltantes**
- Estás "resumiendo" varias funcionalidades en un CU → **PARAR, crear CU individual por HU**

### Respuesta del Skill
Al finalizar, reportar solo:
```
Archivo 05_historias_usuario.md generado: X HUs en Y módulos
Archivo 06_casos_uso.md generado: Z CUs
Validación 1:1: ✅ X HUs = Z CUs
```
**NO devolver el contenido completo del archivo.**
