# Template MVP v1.4

## PASO 0: PREREQUISITOS

### Extensiones VS Code requeridas

| Extensión | Propósito |
|-----------|-----------|
| [ABAP Filesystem (nttdata.vscode-abap-remote-fs)](https://teams.microsoft.com/l/channel/19%3A0af0a09744024ac4af98f66a340b8479%40thread.tacv2/tab%3A%3A53490592-62dd-4ace-a274-adddb196c45d?context=%7B%22channelId%22%3A%2219%3A0af0a09744024ac4af98f66a340b8479%40thread.tacv2%22%7D&tenantId=3048dc87-43f0-4100-9acb-ae1971c79395) | **Requerida para desarrollo ABAP.** Permite editar, activar y gestionar objetos ABAP directamente desde VS Code contra un sistema SAP. Necesaria para el agente `ABAP_DEV`. |

### MCP Servers requeridos

Configurar los siguientes MCP Server en VS Code:

```json
{
	"inputs": [],
	"servers": {
		"chrome-devtools": {
			"command": "npx",
			"args": [
				"-y",
				"chrome-devtools-mcp@latest"
			],
			"type": "stdio"
		},
		"image-extractor": {
			"command": "npx",
			"args": ["mcp-image-extractor@latest"]
		},
		"mcp-abap": {
			"command": "npx",
			"args": ["-y", "mcp-abap@latest"],
			"type": "stdio"
		},
		"mcp-sap-docs": {
			"command": "npx",
			"args": ["-y", "mcp-sap-docs@latest"],
			"type": "stdio"
		}
	}
}
```

| MCP Server | Propósito |
|-----------|-----------|
| `chrome-devtools` | Inspección DOM y captura visual para agentes de UI |
| `image-extractor` | Extracción de texto e imágenes de documentos |
| `mcp-abap` | Documentación y búsqueda de objetos ABAP/SAP. Requerido para el agente `ABAP_DEV` |
| `mcp-sap-docs` | Acceso a documentación oficial SAP (S/4HANA, ABAP, BTP). Requerido para el agente `ABAP_DEV` |


## PASO 1: EXTRAER LOS REQUISITOS DE LA DOCUMENTACIÓN
Ejecutar el agente `Requirements_Extractor` para extraer los requisitos de la documentación. Ejemplo de prompt:

```
Extraer requisitos de "03 - Situaciones administrativas 6.0 (Corregido).pdf" y "Infotipos PSE.docx"
```

* NOTA: Para extraer el texto de las imágenes con OCR se requiere instalar Tesseract https://github.com/UB-Mannheim/tesseract/wiki y actualizar la ruta en el fichero `.github\agents\Requirements_Extractor.agent.md`

Añadir como contexto en el prompt el material funcional del que se disponga, creando una carpeta `/docs/material` dentro de la raíz del proyecto.

## PASO 2: GENERAR EL ANÁLISIS FUNCIONAL 
Ejecutar el agente `Functional_Analyst` para generar el análisis funcional del MVP (carpeta `analisis/`). Ejemplo de prompt:

```
Generar análisis funcional para un sistema que cubra toda la funcionalidad del CRM Comercial.
```

Añadir como contexto en el prompt la carpeta `docs/`.

## PASO 3: GENERAR DISEÑO TÉCNICO Y PLANIFICACIÓN
Ejecutar el agente `MVP_Design.agent` para generar el diseño técnico (`design/01_technical_design.md`), modelo de datos (`design/02_data_model.md`), servicios (`design/03_data_services.md`) y backlog (`backlog/XX_[Nombre_Modulo].md`). Ejemplo de prompt:

```
Generar diseño técnico y planificación.
```

## PASO 4: COLORES Y TIPOGRAFÍA (OPCIONAL) 
Ejecutar el siguiente prompt para personalizar los colores y la tipografía del MVP conforme a la identidad visual del cliente. Ejemplo de prompt:

```
1. Usar Chrome para navegar a https://www.cliente.com/
2. Actualizar el fichero "estilos.md" con los "Background Colours", "Text Colours" y "Typography" obtenidas de la web.
```

## PASO 5: IMPLEMENTAR MVP (BACKEND)
Ejecutar el agente `Backend_DEV` para implementar el backend de los distintos módulos del MVP. Ejemplo de prompt:

```
Implementar módulo de Administración
```

## PASO 6: IMPLEMENTAR MVP (FRONTEND)
Ejecutar el agente `Frontend_DEV` para implementar el frontend de los distintos módulos del MVP. Ejemplo de prompt:

```
Implementar módulo de Administración
```

---

## CHANGE REQUEST

### PASO 1: CREAR CHANGE REQUEST (CR)
Existe un skill creado para facilitar la creación del Change Request. Ejemplo de prompt:

```
Crear CR para un nuevo módulo de gestión de Usuarios, Roles y Permisos
```

### PASO 2: PLANIFICACIÓN DEL CHANGE REQUEST (CR)
Ejecutar el agente `CR_Planner` para generar el backlog del Change Request. Ejemplo de prompt:

```
Planificar CR-001
```

## PASO 3: IMPLEMENTAR CHANGE REQUEST (BACKEND)
Ejecutar el agente `Backend_DEV` para implementar el backend del Change Request. Ejemplo de prompt:

```
Implementar Gestión de Usuarios, Roles y Permisos (CR-001)
```

## PASO 4: IMPLEMENTAR CHANGE REQUEST (FRONTEND)
Ejecutar el agente `Frontend_DEV` para implementar el frontend del Change Request. Ejemplo de prompt:

```
Implementar Gestión de Usuarios, Roles y Permisos (CR-001)
```

**NOTA** Se recomienda utilizar Claude Sonnet 4.5 para ejecutar todos los agentes.
