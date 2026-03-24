# Plan Maestro de Migración SDD: React/Java -> UI5/CAP

## 1. Propósito del documento

Este plan define **cómo migrar la metodología actual sin alterar su flujo operativo**.  
La migración es **tecnológica** (React/Java -> UI5/CAP), no metodológica.

### 1.1 Objetivo principal

Mantener idénticos:

- Flujo de agentes.
- Fases de ejecución.
- Quality gates bloqueantes.
- Trazabilidad RF -> HU -> CU -> Pantalla -> PF.
- Granularidad atómica del backlog.

Y sustituir únicamente:

- Artefactos técnicos, convenciones y prompts acoplados a React/Spring.

---

## 2. Invariantes no negociables (paridad metodológica)

## 2.1 Flujo MVP (debe quedar igual)

1. `Requirements_Extractor`
2. `Functional_Analyst`
3. `MVP_Design`
4. Agente backend (hoy `Backend_DEV`, futuro equivalente CAP)
5. Agente frontend (hoy `Frontend_DEV`, futuro equivalente UI5)

## 2.2 Flujo CR (debe quedar igual)

- `CR_Planner` en rama paralela.
- Backlog CR como entrada a implementación backend/frontend por módulo.

## 2.3 Gates (deben quedar igual)

- Política bloqueante por errores.
- Corrección iterativa hasta verde.
- Gates de backlog (`XX_1..XX_8`) mantenidos en nombre y semántica.

## 2.4 Definición de “migración válida”

La migración solo se considera válida si:

- No cambia el orden de fases.
- No disminuye cobertura de trazabilidad.
- No elimina checks bloqueantes.
- Mantiene granularidad de tareas al mismo nivel o mayor.

---

## 3. Inventario oficial (cobertura 52/52)

## 3.1 Agentes (6)

1. `.github/agents/Requirements_Extractor.agent.md`
2. `.github/agents/Functional_Analyst.agent.md`
3. `.github/agents/MVP_Design.agent.md`
4. `.github/agents/Backend_DEV.agent.md`
5. `.github/agents/Frontend_DEV.agent.md`
6. `.github/agents/CR_Planner.md`

## 3.2 Skills (`SKILL.md`) (22)

1. `.github/skills/backend-code-generator/SKILL.md`
2. `.github/skills/backend-test-generator/SKILL.md`
3. `.github/skills/backlog-planner/SKILL.md`
4. `.github/skills/bpmn-diagrams/SKILL.md`
5. `.github/skills/change-request-generator/SKILL.md`
6. `.github/skills/data-modeler/SKILL.md`
7. `.github/skills/doc-assembler/SKILL.md`
8. `.github/skills/ui5-test-generator/SKILL.md`
9. `.github/skills/frontend-code-generator/SKILL.md`
10. `.github/skills/functional-testing/SKILL.md`
11. `.github/skills/image-analyzer/SKILL.md`
12. `.github/skills/integrations-spec/SKILL.md`
13. `.github/skills/mermaid-diagrams/SKILL.md`
14. `.github/skills/requirements-synthesizer/SKILL.md`
15. `.github/skills/services-designer/SKILL.md`
16. `.github/skills/skill-creator/SKILL.md`
17. `.github/skills/technical-designer/SKILL.md`
18. `.github/skills/text-extractor/SKILL.md`
19. `.github/skills/traceability-validator/SKILL.md`
20. `.github/skills/ui-builder/SKILL.md`
21. `.github/skills/ui-prototyper/SKILL.md`
22. `.github/skills/user-stories-generator/SKILL.md`

## 3.3 Scripts (16)

1. `.github/skills/traceability-validator/scripts/valida_trazabilidad.py`
2. `.github/skills/text-extractor/scripts/extractor_de_requisitos.py`
3. `.github/skills/technical-designer/scripts/validate_warning_justifications.py`
4. `.github/skills/technical-designer/scripts/validate_design.py`
5. `.github/skills/skill-creator/scripts/init_skill.py`
6. `.github/skills/skill-creator/scripts/quick_validate.py`
7. `.github/skills/skill-creator/scripts/package_skill.py`
8. `.github/skills/doc-assembler/scripts/md2docx.py`
9. `.github/skills/backlog-planner/scripts/valida_integridad_diseno.py`
10. `.github/skills/backlog-planner/scripts/valida_completitud_hu.py`
11. `.github/skills/backlog-planner/scripts/valida_navegacion_backlog.py`
12. `.github/skills/backlog-planner/scripts/valida_completitud_funcional.py`
13. `.github/skills/backlog-planner/scripts/valida_pf_en_e2e.py`
14. `.github/skills/backlog-planner/scripts/valida_quality_gates_backlog.py`
15. `.github/skills/bpmn-diagrams/scripts/validate_bpmn.py`
16. `.github/skills/bpmn-diagrams/scripts/fix_bpmn_outputs.py`

## 3.4 Referencias y assets (8)

1. `.github/skills/skill-creator/references/workflows.md`
2. `.github/skills/skill-creator/references/output-patterns.md`
3. `.github/skills/ui-builder/references/testids.md`
4. `.github/skills/bpmn-diagrams/references/template.bpmn`
5. `.github/skills/change-request-generator/assets/cr_template.md`
6. `.github/skills/backlog-planner/references/backlog-template.detallado.md`
7. `.github/skills/technical-designer/references/frontend-template-structure.md`
8. `.github/skills/technical-designer/references/backend-template-structure.md`

---

## 4. Estrategia de migración (sin alterar flujo)

## 4.1 Regla general de decisión por archivo

- **KEEP**: se conserva tal cual (solo limpieza de wording opcional).
- **REFACTOR**: se conserva el archivo, se ajustan reglas/contenido para UI5/CAP.
- **REPLACE**: se crea equivalente UI5/CAP y se mantiene legacy temporal hasta paridad.

## 4.2 Orden técnico obligatorio

1. Referencias de arquitectura objetivo.
2. Skills de diseño (`technical-designer`, `data-modeler`, `services-designer`).
3. Plantilla y skill de backlog.
4. Scripts de validación backlog/diseño.
5. Agentes de implementación y generadores de código/tests.
6. Pilotos y deprecación progresiva.

---

## 5. Roadmap por fases (ejecución)

## Fase 0 - Decisiones bloqueantes

- [ ] Definir CAP runtime objetivo (Node o Java).
- [ ] Definir enfoque UI5 (freestyle, FE, mixto).
- [ ] Definir framework de pruebas UI5 (OPA5 / wdi5 / Playwright adaptado).
- [ ] Registrar decisiones en ADR (`design/adr/ADR-STACK-UI5-CAP.md`).

**Salida obligatoria:** ADR aprobado.

## Fase 1 - Diseño y backlog stack-agnósticos

- [ ] Migrar `technical-designer` y sus referencias de estructura.
- [ ] Migrar `data-modeler` a semántica CDS/CAP.
- [ ] Migrar `services-designer` a contratos UI5/CAP.
- [ ] Migrar `backlog-planner` + `backlog-template.detallado.md` a tareas UI5/CAP.
- [ ] Adaptar validadores de diseño/backlog para nuevas convenciones.

**Salida obligatoria:** backlog de ejemplo sin términos React/Spring.

## Fase 2 - Implementación equivalente UI5/CAP

- [ ] Crear agente backend equivalente CAP.
- [ ] Crear agente frontend equivalente UI5.
- [ ] Crear skills de generación código/tests UI5/CAP.
- [ ] Mantener agentes/skills legacy en coexistencia temporal.

**Salida obligatoria:** módulo piloto implementable con agentes nuevos.

## Fase 3 - Conexión orquestación global

- [ ] Ajustar `MVP_Design.agent.md` a skills/artefactos nuevos.
- [ ] Ajustar `CR_Planner.md` a discovery/catálogos UI5/CAP.
- [ ] Ajustar documentación operativa (`README.md`, `workflow_mvp.md`).

**Salida obligatoria:** flujo documentado de punta a punta para UI5/CAP.

## Fase 4 - Validación real

- [ ] Ejecutar 1 módulo MVP completo en UI5/CAP.
- [ ] Ejecutar 1 CR completo en UI5/CAP.
- [ ] Corregir gaps y repetir hasta estabilidad.

**Salida obligatoria:** dos ejecuciones completas en verde.

## Fase 5 - Industrialización

- [ ] Definir owners y versionado de metodología.
- [ ] Crear smoke suite de framework.
- [ ] Activar bitácora de errores como requisito operativo.

**Salida obligatoria:** operación continua gobernada.

---

## 6. Catálogo detallado 52/52 (acción por archivo)

## 6.1 Agentes (6)

| Archivo | Estado | Acciones atómicas | Dependencias | Criterio de aceptación |
|---|---|---|---|---|
| `.github/agents/Requirements_Extractor.agent.md` | KEEP | Revisar neutralidad de ejemplos (sin stack hardcoded). | Ninguna | Sigue generando `requisitos.md` + `imagenes.md` por bloques de 5 imágenes. |
| `.github/agents/Functional_Analyst.agent.md` | KEEP | Mantener fases 1-14 y reglas HU/CU/wireframes/trazabilidad. | Ninguna | Genera `analisis/01..14` con mismas reglas de cobertura. |
| `.github/agents/MVP_Design.agent.md` | REFACTOR | Reemplazar llamadas y ejemplos React/Spring por UI5/CAP; mantener fases y gates actuales. | Skills diseño/backlog migrados | Conserva secuencia y gates `XX_1..XX_8` sin cambios funcionales. |
| `.github/agents/Backend_DEV.agent.md` | REPLACE | Crear equivalente CAP con pasos espejo (init -> implementación -> tests -> contrato). | Skills backend CAP | Implementación por módulo + tests verdes + contrato para frontend. |
| `.github/agents/Frontend_DEV.agent.md` | REPLACE | Crear equivalente UI5 con pasos espejo por pantalla, navegación, pruebas y quality gate final. | Skills frontend UI5 | Misma cadencia por pantalla y doble validación (mock/real). |
| `.github/agents/CR_Planner.md` | REFACTOR | Ajustar prompts discovery de repo y ejemplos de tareas para UI5/CAP; preservar flujo CR. | Plantilla backlog UI5/CAP | CR backlog generado con misma granularidad y trazabilidad. |

## 6.2 Skills SKILL.md (22)

| Archivo | Estado | Acciones atómicas | Dependencias | Criterio de aceptación |
|---|---|---|---|---|
| `.github/skills/text-extractor/SKILL.md` | KEEP | Sin cambio funcional. | Ninguna | Extracción igual. |
| `.github/skills/image-analyzer/SKILL.md` | KEEP | Sin cambio funcional. | Ninguna | Análisis de imágenes igual. |
| `.github/skills/requirements-synthesizer/SKILL.md` | KEEP | Sin cambio funcional. | Ninguna | Secciones 1-4 igual. |
| `.github/skills/user-stories-generator/SKILL.md` | KEEP | Sin cambio funcional. | Ninguna | HU/CU 1:1 preservado. |
| `.github/skills/mermaid-diagrams/SKILL.md` | KEEP | Sin cambio funcional. | Ninguna | Secciones 7/9 igual. |
| `.github/skills/bpmn-diagrams/SKILL.md` | KEEP | Sin cambio funcional. | Ninguna | BPMN válido igual. |
| `.github/skills/integrations-spec/SKILL.md` | KEEP | Sin cambio funcional. | Ninguna | Sección 8 igual. |
| `.github/skills/functional-testing/SKILL.md` | KEEP | Sin cambio funcional. | Ninguna | Sección 13 igual. |
| `.github/skills/traceability-validator/SKILL.md` | KEEP | Sin cambio funcional, mantener criterios de cierre. | Ninguna | Error=0 obligatorio se mantiene. |
| `.github/skills/doc-assembler/SKILL.md` | KEEP | Sin cambio funcional. | Ninguna | Consolidación docx igual. |
| `.github/skills/change-request-generator/SKILL.md` | REFACTOR | Actualizar ejemplos técnicos a UI5/CAP. | CR planner | Sigue generando CR con plantilla estándar. |
| `.github/skills/skill-creator/SKILL.md` | KEEP | Opcional: neutralizar ejemplos React-first. | Ninguna | Sigue siendo guía válida de skills. |
| `.github/skills/technical-designer/SKILL.md` | REPLACE | Crear versión UI5/CAP manteniendo estructura de salida y trazabilidad. | Referencias UI5/CAP | `design/01` conserva estructura y calidad. |
| `.github/skills/services-designer/SKILL.md` | REFACTOR | Sustituir convenciones `VITE_*` por configuración UI5/CAP y OData/servicios equivalentes. | Technical + data modeler | `design/03` sin términos legacy y con misma estructura. |
| `.github/skills/data-modeler/SKILL.md` | REFACTOR | Incorporar mapeo CDS y convenciones CAP. | Technical designer | `design/02` apto para CAP. |
| `.github/skills/backlog-planner/SKILL.md` | REFACTOR | Reescribir reglas de tareas backend/frontend a CAP/UI5 manteniendo gates y granularidad. | Template backlog + scripts | Backlog UI5/CAP con misma profundidad. |
| `.github/skills/frontend-code-generator/SKILL.md` | REPLACE | Sustituir por generador UI5 equivalente. | Services-designer | Generación frontend UI5 por módulo. |
| `.github/skills/ui-builder/SKILL.md` | REPLACE | Sustituir por builder UI5 (views/controllers/fragments). | Testids UI5 | Construcción de pantalla UI5 estable. |
| `.github/skills/ui5-test-generator/SKILL.md` | REPLACE | Sustituir por pruebas UI5 (OPA5/wdi5 o decisión ADR). | Testids UI5 | Test por PF por pantalla en UI5. |
| `.github/skills/backend-code-generator/SKILL.md` | REPLACE | Sustituir por generador CAP (db/srv/handlers). | Data/services designer | Generación backend CAP por módulo. |
| `.github/skills/backend-test-generator/SKILL.md` | REPLACE | Sustituir por tests CAP por capas. | CAP code-gen | Suites de test CAP equivalentes. |
| `.github/skills/ui-prototyper/SKILL.md` | KEEP | Sin cambio funcional. | Ninguna | Secciones 10-12 igual. |

## 6.3 Scripts (16)

| Archivo | Estado | Acciones atómicas | Dependencias | Criterio de aceptación |
|---|---|---|---|---|
| `.github/skills/text-extractor/scripts/extractor_de_requisitos.py` | KEEP | Sin cambios funcionales (opcional ampliar diccionario). | Ninguna | Resultado igual. |
| `.github/skills/doc-assembler/scripts/md2docx.py` | KEEP | Sin cambios funcionales. | Ninguna | DOCX generado sin regresión. |
| `.github/skills/traceability-validator/scripts/valida_trazabilidad.py` | KEEP | Mantener parser y métricas; ajustar labels solo si fuese estrictamente necesario. | Ninguna | Cobertura y severidades iguales. |
| `.github/skills/technical-designer/scripts/validate_design.py` | REFACTOR | Ajustar checks hardcoded de React/Spring a UI5/CAP. | technical-designer nuevo | Reporte `check-design.md` equivalente. |
| `.github/skills/technical-designer/scripts/validate_warning_justifications.py` | REFACTOR | Ajustar categorías si cambian warnings de diseño. | validate_design actualizado | Justificación 1:1 sigue obligatoria. |
| `.github/skills/backlog-planner/scripts/valida_integridad_diseno.py` | REFACTOR | Ajustar parsing de entidades/servicios/rutas/endpoints a convenciones UI5/CAP. | design 01-03 nuevos | Detección de faltantes sin falsos positivos legacy. |
| `.github/skills/backlog-planner/scripts/valida_navegacion_backlog.py` | REFACTOR | Ajustar heurística menú/rutas para UI5 (`manifest`, navegación app). | backlog template nuevo | Métricas rutas/menu siguen funcionando. |
| `.github/skills/backlog-planner/scripts/valida_pf_en_e2e.py` | REFACTOR | Ajustar nombres de sección de pruebas UI5 si cambia terminología. | backlog template nuevo | PF faltantes detectados correctamente. |
| `.github/skills/backlog-planner/scripts/valida_completitud_hu.py` | REFACTOR | Hacer configurables nombres de secciones tecnológicas. | backlog template nuevo | Mantiene control HU por backend/frontend/tests. |
| `.github/skills/backlog-planner/scripts/valida_completitud_funcional.py` | KEEP | Sin cambio funcional. | Ninguna | Cobertura funcional se mantiene. |
| `.github/skills/backlog-planner/scripts/valida_quality_gates_backlog.py` | KEEP | Mantener íntegro para preservar contrato de gates. | Ninguna | Gates `XX_1..XX_8` sin variación. |
| `.github/skills/bpmn-diagrams/scripts/validate_bpmn.py` | KEEP | Sin cambios. | Ninguna | Valida BPMN igual. |
| `.github/skills/bpmn-diagrams/scripts/fix_bpmn_outputs.py` | KEEP | Sin cambios. | Ninguna | Corrige BPMN igual. |
| `.github/skills/skill-creator/scripts/init_skill.py` | REFACTOR | Sustituir ejemplos de boilerplate React por ejemplos neutrales/UI5/CAP. | skill-creator docs | Scaffolding no sesgado. |
| `.github/skills/skill-creator/scripts/quick_validate.py` | KEEP | Sin cambios. | Ninguna | Validación de frontmatter intacta. |
| `.github/skills/skill-creator/scripts/package_skill.py` | KEEP | Sin cambios. | Ninguna | Empaquetado intacto. |

## 6.4 Referencias y assets (8)

| Archivo | Estado | Acciones atómicas | Dependencias | Criterio de aceptación |
|---|---|---|---|---|
| `.github/skills/skill-creator/references/workflows.md` | KEEP | Sin cambios. | Ninguna | Referencia vigente. |
| `.github/skills/skill-creator/references/output-patterns.md` | KEEP | Sin cambios. | Ninguna | Referencia vigente. |
| `.github/skills/ui-builder/references/testids.md` | REPLACE | Crear convención equivalente para UI5 (IDs/locators estables). | ui5-e2e-testing | Selectores estables para pruebas UI5. |
| `.github/skills/bpmn-diagrams/references/template.bpmn` | KEEP | Sin cambios. | Ninguna | Reutilizable sin impacto. |
| `.github/skills/change-request-generator/assets/cr_template.md` | KEEP | Sin cambios. | Ninguna | Plantilla CR intacta. |
| `.github/skills/backlog-planner/references/backlog-template.detallado.md` | REPLACE | Reescribir 1:1 en estructura para tareas UI5/CAP. | backlog-planner | Backlog conserva formato y granularidad. |
| `.github/skills/technical-designer/references/frontend-template-structure.md` | REPLACE | Reescribir a estructura UI5 (webapp/manifest/views/controllers). | technical-designer | Referencia frontend alineada a UI5. |
| `.github/skills/technical-designer/references/backend-template-structure.md` | REPLACE | Reescribir a estructura CAP (`db/srv/app/test`). | technical-designer | Referencia backend alineada a CAP. |

---

## 7. Nuevos artefactos a crear (mínimo)

## 7.1 Agentes

- `.github/agents/UI5_DEV.agent.md`
- `.github/agents/CAP_DEV.agent.md`

## 7.2 Skills

- `.github/skills/ui5-code-generator/SKILL.md`
- `.github/skills/ui5-builder/SKILL.md`
- `.github/skills/ui5-e2e-testing/SKILL.md`
- `.github/skills/cap-code-generator/SKILL.md`
- `.github/skills/cap-test-generator/SKILL.md`

## 7.3 Referencias

- `.github/skills/ui5-builder/references/testids-ui5.md`
- `.github/skills/backlog-planner/references/backlog-template.ui5-cap.detallado.md` (opcional si no se sobreescribe el actual)

---

## 8. Legacy transitorio (coexistencia controlada)

Mantener temporalmente hasta validar 2 ejecuciones completas MVP+CR en UI5/CAP:

- `.github/agents/Frontend_DEV.agent.md`
- `.github/agents/Backend_DEV.agent.md`
- `.github/skills/frontend-code-generator/SKILL.md`
- `.github/skills/ui-builder/SKILL.md`
- `.github/skills/ui5-test-generator/SKILL.md`
- `.github/skills/backend-code-generator/SKILL.md`
- `.github/skills/backend-test-generator/SKILL.md`
- Referencias legacy React/Spring en `technical-designer/references/*` (hasta cutover).

---

## 9. Secuencia de implementación en 10 pasos (obligatoria)

1. Definir ADR de stack UI5/CAP.
2. Reescribir referencias de arquitectura (`frontend-template-structure`, `backend-template-structure`).
3. Migrar `technical-designer` + `validate_design`.
4. Migrar `data-modeler` y `services-designer`.
5. Reescribir plantilla de backlog detallado UI5/CAP.
6. Adaptar scripts de validación de backlog.
7. Migrar `backlog-planner` manteniendo gates.
8. Crear agentes y skills CAP.
9. Crear agentes y skills UI5 + pruebas UI5.
10. Ejecutar piloto MVP + CR y deprecar legacy.

---

## 10. Riesgos principales y mitigación

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Cambiar flujo sin querer al crear agentes nuevos | Alto | Copiar estructura de fases 1:1 y validar checklist de paridad. |
| Rotura de gates por scripts hardcoded | Alto | Migrar primero template + validadores antes de agentes DEV. |
| Falsos positivos en integridad/navegación | Medio | Parametrizar labels/secciones en scripts y probar con módulo piloto. |
| Pérdida de granularidad de backlog | Alto | Mantener formato plantilla original, solo cambiando artefactos técnicos. |
| Ambigüedad CAP Node vs Java | Alto | ADR bloqueante en Fase 0. |
| Inestabilidad de pruebas UI5 | Medio-Alto | Estándar único de testing y guía de selectores estables. |
| Deriva documental | Alto | Checklist de revisión de docs en cada PR metodológico. |
| Coexistencia prolongada legacy/nuevo | Medio | Criterio de retiro explícito (2 ejecuciones completas verdes). |
| Contrato API inconsistente en transición | Medio | Normalizar en `services-designer` y validar en pilotos. |
| Sobrecarga de cambios simultáneos | Medio | Ejecutar por lotes en orden obligatorio de este plan. |

---

## 11. Definition of Done de la migración

La migración queda cerrada cuando:

- [ ] Existe carril UI5/CAP completo y operativo.
- [ ] Se mantiene secuencia de flujo original.
- [ ] Se mantienen quality gates y bloqueo por error.
- [ ] Se mantiene trazabilidad completa y validada.
- [ ] Se ejecutan con éxito 1 módulo MVP y 1 CR en UI5/CAP.
- [ ] La documentación operativa está actualizada y consistente.

---

## 12. Checklist de ejecución inmediata (primer lote)

## Lote 1 (documental y validación)

- [ ] Reescribir:
  - `.github/skills/technical-designer/references/frontend-template-structure.md`
  - `.github/skills/technical-designer/references/backend-template-structure.md`
  - `.github/skills/backlog-planner/references/backlog-template.detallado.md`
- [ ] Migrar:
  - `.github/skills/technical-designer/SKILL.md`
  - `.github/skills/services-designer/SKILL.md`
  - `.github/skills/data-modeler/SKILL.md`
  - `.github/skills/backlog-planner/SKILL.md`
- [ ] Ajustar scripts:
  - `validate_design.py`
  - `valida_integridad_diseno.py`
  - `valida_navegacion_backlog.py`
  - `valida_completitud_hu.py`
  - `valida_pf_en_e2e.py`

## Lote 2 (implementación)

- [ ] Crear `CAP_DEV.agent.md` + skills CAP.
- [ ] Crear `UI5_DEV.agent.md` + skills UI5.
- [ ] Crear guía de selectores UI5 (`testids-ui5.md`).

## Lote 3 (pilotos y corte)

- [ ] Piloto MVP completo.
- [ ] Piloto CR completo.
- [ ] Deprecación controlada de legacy.

---

## 13. Nota final de coherencia

Este documento está diseñado para evitar mezcla de iteraciones:  
- primero define invariantes,  
- luego roadmap,  
- luego catálogo 52/52,  
- y finalmente ejecución por lotes.  

Si una tarea no respeta el flujo original o los gates existentes, debe rechazarse aunque sea técnicamente correcta.
