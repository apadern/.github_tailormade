#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys
import os
import argparse
from datetime import datetime
from collections import defaultdict

sys.dont_write_bytecode = True

def _is_markdown_table_separator(line: str) -> bool:
    line = line.strip()
    if '|' not in line or '-' not in line:
        return False
    # Se considera separador si (quitando pipes/dashes/colons/espacios) no queda nada
    remainder = re.sub(r'[\|\-:\s]', '', line)
    return len(remainder) == 0


def _parse_markdown_table_from_lines(lines, header_pattern=None, table_index=0):
    """Parsea una tabla markdown desde una lista de líneas."""
    table_data = []
    headers = []
    in_target_table = False
    found_tables = 0

    for i, raw_line in enumerate(lines):
        line = raw_line.strip()

        # Detectar inicio de tabla: línea con pipes seguida de línea separadora
        if "|" in line and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if _is_markdown_table_separator(next_line):
                if header_pattern and header_pattern.lower() not in line.lower():
                    continue
                if found_tables < table_index:
                    found_tables += 1
                    continue

                headers = [h.strip().lower() for h in line.split('|') if h.strip()]
                in_target_table = True
                continue

        if in_target_table:
            if _is_markdown_table_separator(line):
                continue

            # Fin de tabla (línea vacía o sin pipes)
            if not line or "|" not in line:
                if table_data:
                    break
                continue

            # Parsear fila
            raw_cols = line.split('|')
            clean_cols = []
            for c in raw_cols:
                cleaned = c.strip()
                cleaned = re.sub(r'\*\*(.*?)\*\*', r'\1', cleaned)
                cleaned = re.sub(r'\*(.*?)\*', r'\1', cleaned)
                # Limpiar backticks de código inline
                cleaned = cleaned.strip('`')
                clean_cols.append(cleaned)

            if clean_cols and clean_cols[0] == "":
                clean_cols.pop(0)
            if clean_cols and clean_cols[-1] == "":
                clean_cols.pop()

            row_dict = {}
            for h_idx, header in enumerate(headers):
                if h_idx < len(clean_cols):
                    row_dict[header] = clean_cols[h_idx]

            if row_dict:
                table_data.append(row_dict)

    return table_data if table_data else None


def _find_markdown_section_lines(full_text: str, name: str):
    """Encuentra la sección de un item (servicio/entidad) por heading que contenga el nombre.

    Soporta headings tipo '#### 3.1.1 UsuarioService' o '#### Usuario'.
    Retorna líneas de la sección (sin incluir la línea del heading) o None.
    """
    lines = full_text.splitlines()
    # Buscar un heading de nivel 3-6 que contenga el nombre como palabra
    # Nota: al usar f-strings, las llaves del cuantificador deben escaparse: #{{3,6}}
    name_re = re.compile(rf'^(?P<hashes>#{{3,6}})\s+.*\b{re.escape(name)}\b\s*$', re.IGNORECASE)
    heading_re = re.compile(r'^(?P<hashes>#{{3,6}})\s+')

    for idx, line in enumerate(lines):
        m = name_re.match(line.strip())
        if not m:
            continue

        level = len(m.group('hashes'))
        start = idx + 1
        end = len(lines)

        for j in range(start, len(lines)):
            hm = heading_re.match(lines[j].strip())
            if not hm:
                continue
            next_level = len(hm.group('hashes'))
            if next_level <= level:
                end = j
                break

        return lines[start:end]

    return None


def _extract_rf_codes_with_ranges(text: str) -> set:
    """Extrae RF-XXX del texto, incluyendo rangos tipo 'RF-001 a RF-006'."""
    direct = set(re.findall(r'\b(RF-\d{3})\b', text))

    # Rangos: RF-001 a RF-006 / RF-001 - RF-006 / RF-001 al RF-006 / RF-001 hasta RF-006
    range_re = re.compile(
        r'\bRF-(\d{1,3})\s*(?:a|al|hasta|\-|–|—)\s*RF-(\d{1,3})\b',
        re.IGNORECASE,
    )
    for m in range_re.finditer(text):
        start = int(m.group(1))
        end = int(m.group(2))
        if start <= 0 or end <= 0:
            continue
        lo, hi = (start, end) if start <= end else (end, start)
        for n in range(lo, hi + 1):
            direct.add(f"RF-{n:03d}")

    return direct

class ValidationReport:
    """Gestiona el reporte de validación en formato markdown"""
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []
        self.metrics = {}
        
    def add_error(self, category, message):
        self.errors.append({"category": category, "message": message})
    
    def add_warning(self, category, message):
        self.warnings.append({"category": category, "message": message})
    
    def add_info(self, category, message):
        self.info.append({"category": category, "message": message})
    
    def add_metric(self, key, value):
        self.metrics[key] = value
    
    def generate_markdown(self):
        """Genera reporte en formato markdown"""
        md = []
        md.append("# 🔍 Reporte de Validación de Diseño Técnico")
        md.append(f"\n**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        md.append(f"\n**Estado:** {'✅ VÁLIDO' if len(self.errors) == 0 else '❌ ERRORES ENCONTRADOS'}")
        
        # Métricas
        md.append("\n## 📊 Métricas del Diseño")
        md.append("\n| Métrica | Valor |")
        md.append("|---------|-------|")
        for key, value in sorted(self.metrics.items()):
            md.append(f"| {key} | {value} |")
        
        # Resumen
        md.append("\n## 📋 Resumen de Validaciones")
        md.append(f"\n- ❌ **Errores Críticos:** {len(self.errors)}")
        md.append(f"- Warnings: {len(self.warnings)}")
        md.append(f"- ℹ️  **Información:** {len(self.info)}")
        
        # Errores críticos
        if self.errors:
            md.append("\n## ❌ Errores Críticos")
            current_cat = None
            for err in self.errors:
                if err['category'] != current_cat:
                    current_cat = err['category']
                    md.append(f"\n### {current_cat}")
                md.append(f"- {err['message']}")
        
        # Advertencias
        if self.warnings:
            md.append("\n## Warnings")
            current_cat = None
            for warn in self.warnings:
                if warn['category'] != current_cat:
                    current_cat = warn['category']
                    md.append(f"\n### {current_cat}")
                md.append(f"- {warn['message']}")
        
        # Información
        if self.info:
            md.append("\n## ℹ️  Información Adicional")
            current_cat = None
            for inf in self.info:
                if inf['category'] != current_cat:
                    current_cat = inf['category']
                    md.append(f"\n### {current_cat}")
                md.append(f"- {inf['message']}")
        
        # Conclusión
        md.append("\n## 🎯 Conclusión")
        if len(self.errors) == 0:
            md.append("\n✅ **El diseño técnico es coherente y está listo para implementación.**")
        else:
            md.append(f"\n❌ **Se encontraron {len(self.errors)} errores críticos que deben corregirse antes de continuar.**")
        
        return "\n".join(md)

def parse_markdown_table(file_path, header_pattern=None, table_index=0):
    """
    Parsea una tabla markdown buscando un patrón en el header.
    Retorna una lista de diccionarios donde las claves son las columnas (lowercase).
    """
    if not os.path.exists(file_path):
        return None

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    return _parse_markdown_table_from_lines(lines, header_pattern=header_pattern, table_index=table_index)

def extract_requirements(file_path):
    """Extrae requisitos funcionales del análisis"""
    if not os.path.exists(file_path):
        return []
    
    requirements = []
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        # Buscar patrones RF-XXX
        matches = re.findall(r'\b(RF-\d+)\b', content)
        requirements = list(set(matches))
    
    return requirements

def extract_user_stories(file_path):
    """Extrae historias de usuario del análisis"""
    if not os.path.exists(file_path):
        return []
    
    stories = []
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        # Buscar patrones HU-XXX
        matches = re.findall(r'\b(HU-\d+)\b', content)
        stories = list(set(matches))
    
    return stories

def parse_traceability_matrix(file_path):
    """Extrae la matriz de trazabilidad con RF -> HU -> Pantallas"""
    if not os.path.exists(file_path):
        return {}
    
    traceability = {}
    
    # Leer tabla de trazabilidad
    matriz_data = parse_markdown_table(file_path, "Requisito")
    
    if not matriz_data:
        return {}
    
    req_key = next((k for k in matriz_data[0].keys() if 'requisito' in k), None)
    hu_key = next((k for k in matriz_data[0].keys() if 'historia' in k or 'usuario' in k), None)
    pant_key = next((k for k in matriz_data[0].keys() if 'pantalla' in k), None)
    
    if not req_key:
        return {}
    
    for row in matriz_data:
        req_text = row.get(req_key, '')
        
        # Extraer código RF
        rf_match = re.search(r'\b(RF-\d+)\b', req_text)
        if not rf_match:
            continue
        
        rf_code = rf_match.group(1)
        
        # Extraer HUs asociadas
        hus = []
        if hu_key and hu_key in row:
            hu_text = row[hu_key]
            hus = re.findall(r'\b(HU-\d+)\b', hu_text)
        
        # Extraer Pantallas asociadas
        pantallas = []
        if pant_key and pant_key in row:
            pant_text = row[pant_key]
            pantallas = re.findall(r'\b(P-\d+)\b', pant_text)
        
        traceability[rf_code] = {
            'hus': hus,
            'pantallas': pantallas
        }
    
    return traceability

def extract_references_from_file(file_path, patterns):
    """Extrae referencias (RF, P-XXX) de un archivo"""
    if not os.path.exists(file_path):
        return {'RF': set(), 'P': set()}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    references = {
        'RF': _extract_rf_codes_with_ranges(content),
        'P': set(re.findall(r'\b(P-\d+)\b', content))
    }
    
    return references

def parse_entity_details(file_path, entity_name):
    """Extrae atributos de una entidad del modelo de datos"""
    if not os.path.exists(file_path):
        return {"attributes": []}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    section_lines = _find_markdown_section_lines(content, entity_name)
    if not section_lines:
        return {"attributes": []}

    # La tabla de atributos suele empezar con header 'Campo'
    table = _parse_markdown_table_from_lines(section_lines, header_pattern="Campo", table_index=0)
    if not table:
        # Fallback: intentar cualquier tabla
        table = _parse_markdown_table_from_lines(section_lines, header_pattern=None, table_index=0)
    if not table:
        return {"attributes": []}

    # Elegir columna que represente el nombre del campo/atributo
    candidate_keys = list(table[0].keys())
    field_key = next((k for k in candidate_keys if 'campo' in k or 'atributo' in k), None)
    if not field_key:
        # fallback: primera columna
        field_key = candidate_keys[0] if candidate_keys else None
    if not field_key:
        return {"attributes": []}

    attributes = []
    for row in table:
        v = (row.get(field_key) or '').strip()
        if v:
            attributes.append(v)

    return {"attributes": sorted(set(attributes))}

def parse_relations_matrix(file_path):
    """Extrae la matriz de relaciones entre entidades"""
    if not os.path.exists(file_path):
        return []
    
    # Buscar la tabla de Matriz de Relaciones
    relations_data = parse_markdown_table(file_path, "Entidad Origen")
    
    if not relations_data:
        return []
    
    # Extraer relaciones estructuradas
    relations = []
    origen_key = next((k for k in relations_data[0].keys() if 'origen' in k), None)
    destino_key = next((k for k in relations_data[0].keys() if 'destino' in k), None)
    
    if origen_key and destino_key:
        for row in relations_data:
            relations.append({
                'origen': row[origen_key],
                'destino': row[destino_key],
                'relacion': row.get(next((k for k in row.keys() if 'relación' in k or 'relacion' in k), ''), ''),
                'cardinalidad': row.get(next((k for k in row.keys() if 'cardinalidad' in k), ''), '')
            })
    
    return relations

def extract_service_methods(file_path, service_names):
    """Extrae los métodos de cada servicio del archivo 03_data_services.md"""
    if not os.path.exists(file_path):
        return {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    service_methods = {}
    
    for service_name in service_names:
        section_lines = _find_markdown_section_lines(content, service_name)
        if not section_lines:
            service_methods[service_name] = []
            continue

        methods_table = _parse_markdown_table_from_lines(section_lines, header_pattern="Método", table_index=0)
        if not methods_table:
            service_methods[service_name] = []
            continue

        method_key = next((k for k in methods_table[0].keys() if 'método' in k or 'metodo' in k), None)
        if not method_key:
            # fallback: primera columna
            keys = list(methods_table[0].keys())
            method_key = keys[0] if keys else None
        if not method_key:
            service_methods[service_name] = []
            continue

        methods = []
        for row in methods_table:
            raw = (row.get(method_key) or '').strip()
            if not raw:
                continue
            # quitar backticks para normalizar
            raw = raw.strip('`').strip()
            methods.append(raw)

        service_methods[service_name] = methods
    
    return service_methods


def extract_service_entities(file_path, service_names):
    """Extrae entidades (principal y secundarias) por servicio desde design/03_data_services.md.

    Busca líneas del tipo:
    - **Entidad:** Posicion
    - **Entidades:** Usuario, Sesion
    """
    if not os.path.exists(file_path):
        return {}

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # En el markdown suele aparecer el ':' dentro del bold: '**Entidades:** ...'
    # pero aceptamos también la variante con ':' fuera del bold.
    entity_re = re.compile(
        r'^\*\*Entidad(?:es)?\s*:?\*\*\s*:?(?P<list>.+?)\s*$',
        re.IGNORECASE,
    )
    service_entities = {}

    for service_name in service_names:
        section_lines = _find_markdown_section_lines(content, service_name)
        if not section_lines:
            service_entities[service_name] = []
            continue

        entities = []
        # Normalmente está en la cabecera del servicio (primeras líneas)
        for raw in section_lines[:40]:
            line = raw.strip()
            m = entity_re.match(line)
            if not m:
                continue

            raw_list = m.group('list')
            raw_list = raw_list.strip().strip('`').strip()
            # Separadores típicos: coma y/o ' y '
            parts = re.split(r',|\s+y\s+|\s+e\s+', raw_list)
            for p in parts:
                name = p.strip().strip('`').strip()
                name = re.sub(r'^[\-\*\s]+', '', name)
                name = re.sub(r'[\.;:]+$', '', name)
                if name:
                    entities.append(name)

        service_entities[service_name] = sorted(set(entities))

    return service_entities


def parse_api_endpoints_from_design01(file_path: str):
    """Extrae endpoints API (si existen) desde design/01_technical_design.md.

    Espera una tabla con columnas similares a:
    | Método | Endpoint | ... | Módulo | ... |
    """
    table = parse_markdown_table(file_path, "Endpoint")
    if not table:
        return []

    endpoint_key = next((k for k in table[0].keys() if 'endpoint' in k), None)
    module_key = next((k for k in table[0].keys() if 'módulo' in k or 'modulo' in k), None)
    if not endpoint_key or not module_key:
        return []

    http_key = next((k for k in table[0].keys() if 'método' in k or 'metodo' in k or k.strip() == 'http'), None)
    security_key = next((k for k in table[0].keys() if 'seguridad' in k or 'auth' in k), None)

    endpoints = []
    for row in table:
        ep = (row.get(endpoint_key) or '').strip()
        # Normalizar posibles formatos markdown/quotes para evitar falsos positivos
        # Ej: ` /api/auth/login ` o "`/api/auth/login`"
        ep = ep.strip().strip('"\'')
        ep = ep.strip().strip('`').strip()
        mod = (row.get(module_key) or '').strip()
        if not ep or not mod:
            continue
        endpoints.append({
            'endpoint': ep,
            'module': mod,
            'http': (row.get(http_key) or '').strip() if http_key else '',
            'security': (row.get(security_key) or '').strip() if security_key else '',
        })

    return endpoints

def validate_design(output_file):
    """Función principal de validación"""
    report = ValidationReport()
    
    # Rutas de archivos
    base_path = "design"
    analisis_path = "analisis"
    
    f01 = os.path.join(base_path, "01_technical_design.md")
    f02 = os.path.join(base_path, "02_data_model.md")
    f03 = os.path.join(base_path, "03_data_services.md")
    f_rf = os.path.join(analisis_path, "03_requerimientos_funcionales.md")
    f_hu = os.path.join(analisis_path, "05_historias_usuario.md")
    
    print("🔍 Iniciando validación del diseño técnico...")
    
    # ========== CARGAR DATOS ==========
    
    # 1. Leer Módulos de 01
    print(f"\n📖 Leyendo {f01}...")
    modules_data = parse_markdown_table(f01, "Módulo")
    valid_modules = []
    module_descriptions = {}
    
    if not modules_data:
        report.add_error("Estructura", f"No se pudieron leer módulos de {f01}")
    else:
        mod_key = next((k for k in modules_data[0].keys() if 'módulo' in k), None)
        desc_key = next((k for k in modules_data[0].keys() if 'descripción' in k or 'descripcion' in k), None)
        
        if not mod_key:
            report.add_error("Estructura", f"No se encontró columna 'Módulo' en {f01}")
        else:
            for m in modules_data:
                mod_name = m[mod_key]
                valid_modules.append(mod_name)
                if desc_key and desc_key in m:
                    module_descriptions[mod_name] = m[desc_key]
            
            print(f"  OK {len(valid_modules)} módulos encontrados")
            report.add_metric("Total Módulos", len(valid_modules))

    # 1b. Leer Endpoints API (opcional) de 01
    api_endpoints = parse_api_endpoints_from_design01(f01)
    if api_endpoints:
        report.add_metric("Endpoints API (design/01)", len(api_endpoints))
    else:
        report.add_info("Estructura", "No se detectó tabla de endpoints API en design/01 (opcional)")

    # 2. Leer Entidades de 02
    print(f"\n📖 Leyendo {f02}...")
    entities_data = parse_markdown_table(f02, "Entidad")
    valid_entities = []
    entity_to_module = {}
    entity_details = {}
    
    if not entities_data:
        report.add_error("Estructura", f"No se pudieron leer entidades de {f02}")
    else:
        ent_key = next((k for k in entities_data[0].keys() if 'entidad' in k), None)
        mod_key_02 = next((k for k in entities_data[0].keys() if 'módulo' in k), None)
        
        if not ent_key or not mod_key_02:
            report.add_error("Estructura", f"Faltan columnas 'Entidad' o 'Módulo' en {f02}")
        else:
            for row in entities_data:
                entity = row[ent_key]
                module = row[mod_key_02]
                valid_entities.append(entity)
                entity_to_module[entity] = module
                
                # Extraer detalles de la entidad
                entity_details[entity] = parse_entity_details(f02, entity)
            
            print(f"  OK {len(valid_entities)} entidades encontradas")
            report.add_metric("Total Entidades", len(valid_entities))
    
    # 2b. Leer Matriz de Relaciones
    print(f"\n📖 Leyendo matriz de relaciones de {f02}...")
    relations_matrix = parse_relations_matrix(f02)
    if relations_matrix:
        print(f"  OK {len(relations_matrix)} relaciones encontradas")
        report.add_metric("Total Relaciones", len(relations_matrix))
    else:
        report.add_warning("Estructura", f"No se pudo leer matriz de relaciones de {f02}")

    # 3. Leer Servicios de 03
    print(f"\n📖 Leyendo {f03}...")
    services_data = parse_markdown_table(f03, "Servicio")
    valid_services = []
    service_to_entity = {}
    service_methods = {}  # serviceName -> [methods]
    service_entities = {}  # serviceName -> [entities]
    service_section_texts = {}  # serviceName -> full markdown section text
    
    if not services_data:
        report.add_error("Estructura", f"No se pudieron leer servicios de {f03}")
    else:
        svc_key = next((k for k in services_data[0].keys() if 'servicio' in k), None)
        ent_key_03 = next((k for k in services_data[0].keys() if 'entidad' in k), None)
        
        if not svc_key or not ent_key_03:
            report.add_error("Estructura", f"Faltan columnas 'Servicio' o 'Entidad' en {f03}")
        else:
            for row in services_data:
                service = row[svc_key]
                entity_ref = row[ent_key_03]
                valid_services.append(service)
                service_to_entity[service] = entity_ref
            
            print(f"  OK {len(valid_services)} servicios encontrados")
            report.add_metric("Total Servicios", len(valid_services))
            
            # Extraer métodos de cada servicio
            print(f"  ⚙️  Extrayendo métodos de servicios...")
            service_methods = extract_service_methods(f03, valid_services)
            total_methods = sum(len(methods) for methods in service_methods.values())
            print(f"  OK {total_methods} métodos encontrados")
            report.add_metric("Total Métodos", total_methods)

            # Extraer entidades (incluye secundarias declaradas en el detalle)
            service_entities = extract_service_entities(f03, valid_services)

            # Cachear el texto completo de cada sección de servicio para detectar entidades
            # que aparecen en tablas de métodos, tipos de salida, notas, etc.
            try:
                with open(f03, 'r', encoding='utf-8') as f:
                    _services_md = f.read()
                for svc_name in valid_services:
                    sec = _find_markdown_section_lines(_services_md, svc_name)
                    if sec:
                        service_section_texts[svc_name] = "\n".join(sec)
            except Exception:
                service_section_texts = {}

    # 4. Leer Requisitos Funcionales
    print(f"\n📖 Leyendo {f_rf}...")
    requirements = extract_requirements(f_rf)
    if requirements:
        print(f"  OK {len(requirements)} requisitos funcionales encontrados")
        report.add_metric("Total RF", len(requirements))
    else:
        report.add_warning("Trazabilidad", f"No se encontraron requisitos funcionales en {f_rf}")

    # 5. Leer Historias de Usuario
    print(f"\n📖 Leyendo {f_hu}...")
    user_stories = extract_user_stories(f_hu)
    if user_stories:
        print(f"  OK {len(user_stories)} historias de usuario encontradas")
        report.add_metric("Total HU", len(user_stories))
    else:
        report.add_warning("Trazabilidad", f"No se encontraron historias de usuario en {f_hu}")
    
    # 6. Leer Matriz de Trazabilidad
    f_traz = os.path.join(analisis_path, "14_matriz_trazabilidad.md")
    print(f"\n📖 Leyendo {f_traz}...")
    traceability_matrix = parse_traceability_matrix(f_traz)
    
    if traceability_matrix:
        print(f"  OK Matriz de trazabilidad con {len(traceability_matrix)} requisitos")
        report.add_metric("RF en Matriz", len(traceability_matrix))
        
        # Extraer todas las HU y Pantallas de la matriz
        all_hus_in_matrix = set()
        all_pantallas_in_matrix = set()
        for rf_data in traceability_matrix.values():
            all_hus_in_matrix.update(rf_data['hus'])
            all_pantallas_in_matrix.update(rf_data['pantallas'])
        
        report.add_metric("HU en Matriz", len(all_hus_in_matrix))
        report.add_metric("Pantallas en Matriz", len(all_pantallas_in_matrix))
    else:
        report.add_warning("Trazabilidad", f"No se pudo leer matriz de trazabilidad de {f_traz}")
        all_hus_in_matrix = set()
        all_pantallas_in_matrix = set()
    
    # 7. Extraer referencias de archivos de diseño
    print(f"\n📖 Extrayendo referencias de archivos de diseño...")
    refs_01 = extract_references_from_file(f01, ['RF', 'P'])
    refs_02 = extract_references_from_file(f02, ['RF', 'P'])
    refs_03 = extract_references_from_file(f03, ['RF', 'P'])
    
    # Consolidar referencias
    all_rf_refs = refs_01['RF'] | refs_02['RF'] | refs_03['RF']
    all_p_refs = refs_01['P'] | refs_02['P'] | refs_03['P']
    
    print("  OK Referencias encontradas:")
    print(f"    - RF: {len(all_rf_refs)} referencias")
    print(f"    - Pantallas: {len(all_p_refs)} referencias")
    
    report.add_metric("RF referenciados en diseño", len(all_rf_refs))
    report.add_metric("Pantallas referenciadas en diseño", len(all_p_refs))

    # ========== VALIDACIONES ==========
    
    print("\n🔍 Ejecutando validaciones...\n")
    
    # VALIDACIÓN 1: Unicidad de Módulos
    print(">> Validación de unicidad de módulos...")
    seen_modules = set()
    for mod in valid_modules:
        if mod in seen_modules:
            report.add_error("Unicidad", f"Módulo duplicado: '{mod}'")
        seen_modules.add(mod)
    
    # VALIDACIÓN 2: Unicidad de Entidades
    print(">> Validación de unicidad de entidades...")
    seen_entities = set()
    for ent in valid_entities:
        if ent in seen_entities:
            report.add_error("Unicidad", f"Entidad duplicada: '{ent}'")
        seen_entities.add(ent)
    
    # VALIDACIÓN 3: Unicidad de Servicios
    print(">> Validación de unicidad de servicios...")
    seen_services = set()
    for svc in valid_services:
        if svc in seen_services:
            report.add_error("Unicidad", f"Servicio duplicado: '{svc}'")
        seen_services.add(svc)
    
    # VALIDACIÓN 4: Entidades asignadas a módulos existentes
    print(">> Validación de coherencia entidad-módulo...")
    for entity, module in entity_to_module.items():
        if module not in valid_modules:
            report.add_error("Coherencia Estructural", 
                           f"Entidad '{entity}' asignada a módulo inexistente '{module}'")
    
    # VALIDACIÓN 5: Servicios vinculados a entidades existentes
    print(">> Validación de coherencia servicio-entidad...")
    for service, entity in service_to_entity.items():
        # Omitir si la entidad es N/A o - (servicios de agregación sin entidad principal)
        entity_norm = entity.strip().upper()
        if entity_norm not in ('N/A', '-', '') and entity not in valid_entities:
            report.add_error("Coherencia Estructural", 
                           f"Servicio '{service}' referencia entidad inexistente '{entity}'")
    
    # VALIDACIÓN 6: Relaciones entre entidades
    print(">> Validación de relaciones entre entidades...")
    for rel in relations_matrix:
        origen = rel['origen']
        destino = rel['destino']
        
        # Verificar que ambas entidades existen
        if origen not in valid_entities:
            report.add_error("Relaciones", 
                           f"Relación con entidad origen inexistente '{origen}' -> '{destino}'")
        
        if destino not in valid_entities:
            report.add_error("Relaciones", 
                           f"Relación '{origen}' -> entidad destino inexistente '{destino}'")
    
    # VALIDACIÓN 7: Cobertura - Módulos sin entidades
    print(">> Validación de cobertura módulo-entidad...")
    modules_with_entities = set(entity_to_module.values())
    for mod in valid_modules:
        if mod not in modules_with_entities:
            report.add_error("Cobertura", f"Módulo '{mod}' no tiene entidades asignadas")
    
    # VALIDACIÓN 8: Cobertura - Entidades sin servicios
    print(">> Validación de cobertura entidad-servicio...")
    entities_with_services = set()
    for entity in service_to_entity.values():
        if entity and entity.strip():
            entities_with_services.add(entity)
    for ents in service_entities.values():
        entities_with_services.update(ents)
    # También considerar entidades mencionadas dentro del detalle del servicio
    if service_section_texts and valid_entities:
        for entity_name in valid_entities:
            entity_re = re.compile(rf'\b{re.escape(entity_name)}\b')
            if any(entity_re.search(txt) for txt in service_section_texts.values()):
                entities_with_services.add(entity_name)
    for ent in valid_entities:
        if ent not in entities_with_services:
            report.add_error("Cobertura", f"Entidad '{ent}' no tiene servicios definidos")
    
    # VALIDACIÓN 9: Servicios CRUD básicos
    print(">> Validación de servicios CRUD...")
    entity_operations = defaultdict(set)
    
    # Analizar métodos de cada servicio
    for service_name, methods in service_methods.items():
        entity = service_to_entity.get(service_name, "")
        
        for method in methods:
            method_lower = method.lower()
            
            # Detectar operación READ
            if any(x in method_lower for x in ['get', 'obtener', 'listar', 'consultar', 'buscar', 'search']):
                entity_operations[entity].add('READ')
            
            # Detectar operación CREATE
            if any(x in method_lower for x in ['create', 'crear', 'add', 'agregar', 'nuevo', 'registrar', 'insert']):
                entity_operations[entity].add('CREATE')
            
            # Detectar operación UPDATE
            if any(x in method_lower for x in ['update', 'actualizar', 'modificar', 'edit', 'cambiar']):
                entity_operations[entity].add('UPDATE')
            
            # Detectar operación DELETE
            if any(x in method_lower for x in ['delete', 'eliminar', 'borrar', 'remove', 'quitar']):
                entity_operations[entity].add('DELETE')
    
    # Verificar cobertura CRUD por entidad
    for entity in valid_entities:
        operations = entity_operations.get(entity, set())
        missing = {'CREATE', 'READ', 'UPDATE', 'DELETE'} - operations
        if missing:
            report.add_warning("Servicios CRUD", 
                             f"Entidad '{entity}' no tiene operaciones: {', '.join(sorted(missing))}")
    
    # Métrica de cobertura CRUD
    entities_with_full_crud = sum(1 for ops in entity_operations.values() if len(ops) == 4)
    crud_coverage = (entities_with_full_crud / len(valid_entities) * 100) if valid_entities else 0
    report.add_metric("Cobertura CRUD completo (%)", f"{crud_coverage:.1f}%")

    # VALIDACIÓN 9b: Endpoints API referencian módulos existentes y convención /api
    if api_endpoints:
        print(">> Validación de endpoints API (design/01)...")
        for e in api_endpoints:
            if e['module'] not in valid_modules:
                report.add_error(
                    "Coherencia Estructural",
                    f"Endpoint '{e['endpoint']}' referencia módulo inexistente '{e['module']}'",
                )
            if not e['endpoint'].startswith('/api'):
                report.add_warning(
                    "Convenciones API",
                    f"Endpoint '{e['endpoint']}' no usa prefijo '/api'",
                )
    
    # VALIDACIÓN 10: Atributos en entidades
    print(">> Validación de atributos en entidades...")
    for entity, details in entity_details.items():
        if not details['attributes']:
            report.add_error("Atributos", f"Entidad '{entity}' no tiene atributos definidos")
        else:
            # Verificar atributos básicos recomendados
            attrs_lower = [a.lower() for a in details['attributes']]
            if not any('id' in a for a in attrs_lower):
                report.add_warning("Atributos", f"Entidad '{entity}' no tiene atributo ID")
    
    # VALIDACIÓN 11: Trazabilidad con análisis funcional
    print(">> Validación de trazabilidad con análisis...")
    if requirements:
        # Buscar referencias a RF en diseño técnico
        design_content = ""
        for f in [f01, f02, f03]:
            if os.path.exists(f):
                with open(f, 'r', encoding='utf-8') as file:
                    design_content += file.read()
        
        rf_in_design = _extract_rf_codes_with_ranges(design_content)
        uncovered_rf = set(requirements) - rf_in_design
        
        if uncovered_rf:
            report.add_warning("Trazabilidad", 
                             f"{len(uncovered_rf)} requisitos sin trazabilidad en diseño: {', '.join(sorted(uncovered_rf)[:5])}{'...' if len(uncovered_rf) > 5 else ''}")
        
        coverage_pct = (len(rf_in_design) / len(requirements) * 100) if requirements else 0
        report.add_metric("Cobertura RF (%)", f"{coverage_pct:.1f}%")
    
    # VALIDACIÓN 12: Coherencia RF referenciados vs matriz de trazabilidad
    print(">> Validación de coherencia con matriz de trazabilidad...")
    if traceability_matrix:
        valid_rf_in_matrix = set(traceability_matrix.keys())
        
        # RF referenciados que no existen en la matriz
        invalid_rf_refs = all_rf_refs - valid_rf_in_matrix
        if invalid_rf_refs:
            for rf in sorted(invalid_rf_refs):
                report.add_error("Trazabilidad - RF", 
                               f"Diseño referencia '{rf}' que no existe en matriz de trazabilidad")
        
        # Pantallas referenciadas que no existen en la matriz
        invalid_p_refs = all_p_refs - all_pantallas_in_matrix
        if invalid_p_refs:
            for p in sorted(invalid_p_refs)[:10]:  # Limitar a 10
                report.add_warning("Trazabilidad - Pantallas", 
                                 f"Diseño referencia '{p}' que no existe en matriz de trazabilidad")
            if len(invalid_p_refs) > 10:
                report.add_warning("Trazabilidad - Pantallas", 
                                 f"... y {len(invalid_p_refs) - 10} pantallas más sin trazabilidad")
    
    # VALIDACIÓN 13: HU y RF en análisis deben estar en matriz
    print(">> Validación de completitud de matriz de trazabilidad...")
    if traceability_matrix:
        valid_rf_in_matrix = set(traceability_matrix.keys())
        
        # RF definidos en análisis que no están en la matriz
        rf_not_in_matrix = set(requirements) - valid_rf_in_matrix
        if rf_not_in_matrix:
            report.add_warning("Completitud Matriz", 
                             f"{len(rf_not_in_matrix)} RF sin entrada en matriz: {', '.join(sorted(rf_not_in_matrix)[:5])}{'...' if len(rf_not_in_matrix) > 5 else ''}")
        
        # HU definidas en análisis que no están en la matriz
        hu_not_in_matrix = set(user_stories) - all_hus_in_matrix
        if hu_not_in_matrix:
            report.add_warning("Completitud Matriz", 
                             f"{len(hu_not_in_matrix)} HU sin entrada en matriz: {', '.join(sorted(hu_not_in_matrix)[:5])}{'...' if len(hu_not_in_matrix) > 5 else ''}")
    
    # Métricas adicionales
    report.add_metric("Entidades/Módulo (promedio)", 
                     f"{len(valid_entities)/len(valid_modules):.1f}" if valid_modules else "0")
    report.add_metric("Servicios/Entidad (promedio)", 
                     f"{len(valid_services)/len(valid_entities):.1f}" if valid_entities else "0")
    
    # ========== GENERAR REPORTE ==========
    
    print(f"\n📝 Generando reporte en {output_file}...")
    
    markdown_content = report.generate_markdown()
    
    # Crear directorio si no existe
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    # Resumen en consola
    print("\n" + "="*60)
    print("📊 RESUMEN DE VALIDACIÓN")
    print("="*60)
    print(f"❌ Errores Críticos: {len(report.errors)}")
    print(f"Warnings: {len(report.warnings)}")
    print(f"ℹ️  Información: {len(report.info)}")
    print(f"\nReporte generado: {output_file}")
    print("="*60)
    
    return len(report.errors) == 0

def main():
    parser = argparse.ArgumentParser(
        description='Valida coherencia y trazabilidad del diseño técnico'
    )
    parser.add_argument(
        '--output', '-o',
        default=os.path.join('.', 'design', 'check-design.md'),
        help='Ruta del archivo de salida (default: ./design/check-design.md)'
    )
    
    args = parser.parse_args()
    
    if not os.path.exists("design"):
        print("❌ Carpeta 'design/' no encontrada.")
        sys.exit(1)
    
    success = validate_design(args.output)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
