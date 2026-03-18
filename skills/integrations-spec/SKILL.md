---
name: integrations-spec
description: Documenta integraciones con sistemas externos (APIs, servicios, ERPs). Usar cuando se necesite generar la sección 8 de un análisis funcional.
---

# Integrations Spec

Documenta integraciones internas y externas del sistema.

## Modos

| Modo | Acción |
|------|--------|
| **Completo** | Generar sección 8 |
| **Prototipo** | **Omitir completamente** |

## Prerrequisitos

- `requisitos.md` (contiene INTs e integraciones en RFs)
- `analisis/03_requerimientos_funcionales.md` (RFs que implican integraciones)

## Sección 8: Integraciones con Otros Sistemas

Identificar las integraciones mencionadas en INTs y RFs. **Usar formato de tabla única sin subsecciones adicionales:**

```markdown
## 8. Integraciones con Otros Sistemas

| Sistema | Tipo de Integración | Propósito | Tecnología / Protocolo |
| :------ | :------------------ | :-------- | :--------------------- |
| **ERP Empresarial (ERPEX)** | API / Servicio (Salida) | **Contabilización de Facturación:** <br> - Informar sobre facturación de servicios. <br> - Gestionar facturas a entidades. | HTTPS / JSON |
| **Servicio Fiscal Nacional (SFN)** | Servicio (Vía ERPEX) | **Cumplimiento Fiscal:** <br> - Garantizar notificación de facturas al SFN conforme normativa. | HTTPS / XML |
```

### Formato del Propósito

Usar formato estructurado con título en negrita y lista de viñetas:
```
**Título:** <br> - Detalle 1. <br> - Detalle 2.
```

### Tipos de integración

- **API (Entrada)** - Sistema recibe datos
- **API (Salida)** - Sistema envía datos
- **API / Servicio (Bidireccional)** - Comunicación en ambos sentidos
- **Servicio (Vía X)** - Integración indirecta a través de otro sistema
- **Batch/Fichero** - Intercambio por archivos

Guardar como: `analisis/08_integraciones.md`

## Reglas

- **Usar SOLO tabla única** - NO crear subsecciones por sistema ni tablas separadas
- Incluir todas las integraciones identificadas en formato conciso
- Especificar dirección del flujo de datos
- Indicar protocolo cuando esté disponible
- **NO incluir resúmenes, conclusiones ni secciones adicionales al final del documento**
