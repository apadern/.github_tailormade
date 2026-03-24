# Estructura Base del Backend ABAP (SAP)

Esta referencia define la **plantilla de estructura** y convenciones mínimas para el backend ABAP del MVP en entorno SAP.

## Árbol de Paquetes (Backend ABAP)

En ABAP los objetos se organizan en una **jerarquía de paquetes Z** en el repositorio SAP. Hay un paquete raíz por aplicación y sub-paquetes por módulo y capa. Esta estructura debe declararse explícitamente en `design/01_technical_design.md` (sección "ABAP Package Hierarchy") para que el agente `ABAP_DEV` la implemente.

```
Z<MODULO>/                               # Paquete único del módulo
│
├── DDIC (SE11)
│   ├── Z<MODULO>_T_<NOMBRE>             # Tabla transparente por entidad de negocio
│   ├── Z<MODULO>_S_<NOMBRE>             # Estructura flat de entidad
│   └── Z<MODULO>_TT_<NOMBRE>            # Tipo de tabla interna
│
├── Clases ABAP (SE24)
│   ├── ZCL_<MODULO>_<NOMBRE>            # Data Access Object por entidad

│
├── Interfaces ABAP (SE24)
│   ├── ZIF_<MODULO>_<NOMBRE>            # Contrato del servicio
│
├── OData / SEGW (si aplica Fiori/SAPUI5)
│   ├── ZGW_<MODULO>_NOMBRE              # Proyecto SEGW (nombre técnico del servicio)
│   ├── ZCL_<MODULO>_DPC_EXT             # Data Provider Extension (CRUD handlers)
│   └── ZCL_<MODULO>_MPC_EXT             # Model Provider Extension (metadatos)
│
├── RFC / Function Group (si aplica)
│   ├── Z<MODULO>_<NOMBRE>_FG            # Function Group contenedor
│   └── Z<MODULO>_<NOMBRE>_<OPERACION>   # Function Modules (GET / CREATE / UPDATE / DELETE)
│
└── Tests ABAP Unit
    └── ZCL_<MODULO>_<NOMBRE>_TEST       # Data Access Object por entidad
```

## Capas (alto nivel)

- **OData/RFC**: Punto de entrada externo. Delega en la capa de servicio. No contiene lógica de negocio.
- **Service (`ZCL_<MODULO>_*_SRV`)**: Orquestación de casos de uso, reglas de negocio, validaciones. Consume DAOs vía interfaz.
- **DDIC**: Tablas transparentes, estructuras y tipos de tabla. Base de persistencia.
- **Utilidades**: Logging (SLG1), excepciones y helpers sin dependencias de negocio.

## Convenciones de Nombrado

| Tipo de objeto        | Patrón                               | Ejemplo                          |
|-----------------------|--------------------------------------|----------------------------------|
| Proyecto SEGW         | `ZGW_<MODULO>_<NOMBRE>`              | `ZGW_FI_PEDIDO`                  |
| Data Provider (OData) | `ZCL_<MODULO>_DPC_EXT`               | `ZCL_FI_DPC_EXT`                 |
| Model Provider (OData)| `ZCL_<MODULO>_MPC_EXT`               | `ZCL_FI_MPC_EXT`                 |
| Function Group (RFC)  | `Z<MODULO>_<NOMBRE>_FG`              | `ZFI_PEDIDO_FG`                  |
| Clase de servicio     | `ZCL_<MODULO>_<NOMBRE>`              | `ZCL_FI_PEDIDO_SRV`              |
| Interfaz de servicio  | `ZIF_<MODULO>_<NOMBRE>`              | `ZIF_FI_PEDIDO_SRV`              |
| Clase DAO             | `ZCL_<MODULO>_<NOMBRE>`              | `ZCL_FI_PEDIDO_DAO`              |
| Clase de excepción    | `ZCX_<MODULO>_<NOMBRE>`              | `ZCX_FI_PEDIDO`                  |
| Tabla transparente    | `Z<MODULO>_T_<NOMBRE>`               | `ZFI_T_PEDIDO`                   |
| Estructura DDIC       | `Z<MODULO>_S_<NOMBRE>`               | `ZFI_S_PEDIDO`                   |
| Tipo tabla DDIC       | `Z<MODULO>_TT_<NOMBRE>`              | `ZFI_TT_PEDIDO`                  |

> **Nota:** `<MODULO>` es el identificador corto del módulo funcional (máx. 8 caracteres para respetar límites de nombres ABAP).

## Convenciones de Desarrollo

- **ABAP moderno (ABAP Objects)**: Usar clases e interfaces; evitar programación procedural excepto en Function Modules expuestos por RFC.
- **Inyección de dependencias**: Los servicios reciben sus DAOs (y otros colaboradores) vía constructor o método setter usando interfaces (`ZIF_*`), facilitando la sustitución por mocks en tests ABAP Unit.
- **Excepciones de clase**: Preferir excepciones basadas en `CX_STATIC_CHECK` o `CX_NO_CHECK` (clase propia `ZCX_<MODULO>_*`). Evitar `RAISE EXCEPTION TYPE CX_SY_*` genéricas.
- **Autorización**: Todo método de servicio expuesto externamente debe realizar `AUTHORITY-CHECK OBJECT '...'` antes de ejecutar lógica de negocio.
- **Logging**: Usar `ZCL_<MODULO>_LOGGER` (wrapper de SLG1) para trazas de error y auditoría. No usar `MESSAGE ... INTO ...` directamente en servicios.
- **Transacciones / LUW**: Gestionar `COMMIT WORK` y `ROLLBACK WORK` únicamente en la capa de servicio o en el punto de entrada (DPC_EXT / FM), nunca dentro de DAOs.
- **Select For Update**: Usar `SELECT ... FOR UPDATE` en operaciones de escritura concurrente; documentar locks lógicos con `ENQUEUE`/`DEQUEUE` cuando aplique.
- **No filtrar por lógica SAP estándar**: Los DAOs acceden solo a tablas Z del proyecto. Las tablas estándar SAP se consumen desde la capa de servicio usando APIs SAP (BAPIs, métodos de clases SAP estándar) o bien a través de módulos de función estándar.

## Patrón OData (Fiori / SAPUI5)

```
ZGW_<MODULO>_<NOMBRE> (SEGW) → ZCL_<MODULO>_MPC_EXT (metadatos)
                              → ZCL_<MODULO>_DPC_EXT (handlers)
                                    ↓
                         ZCL_<MODULO>_<NOMBRE>   (lógica de negocio)
                                    ↓
                         ZCL_<MODULO>_<NOMBRE>   (acceso a datos)
                                    ↓
                         Tablas DDIC: Z<MODULO>_T_<NOMBRE>
```

- Cada EntitySet expuesto en OData corresponde a un método `<ENTITYSET>_GET_ENTITYSET`, `_GET_ENTITY`, `_CREATE_ENTITY`, `_UPDATE_ENTITY`, `_DELETE_ENTITY` en la clase `ZCL_<MODULO>_DPC_EXT`.
- Los handlers DPC_EXT **no** contienen lógica de negocio: delegan al servicio correspondiente.
- Activar el servicio en `/IWFND/MAINT_SERVICE`.

## Auditoría

- Toda operación de escritura (crear/modificar/eliminar) debe registrar una entrada en `Z<MODULO>_T_AUDIT` con: `MANDT`, `UNAME`, `DATUM`, `UZEIT`, `TABNAME`, `ACTION` (C/U/D), `OBJ_KEY` y `CHANGE_JSON`.
- Usar `ZCL_<MODULO>_LOGGER` para delegar el registro y mantener consistencia.

## Reglas de Consistencia (Diseño)

- Un **módulo funcional** del análisis corresponde a un paquete `Z<MODULO>` con sus clases de servicio, DAO y objetos DDIC propios.
- Evitar acceso directo a tablas desde la capa OData/RFC; siempre pasar por la capa de servicio.
- Un módulo no debe usar directamente clases DAO de otro módulo; la comunicación entre módulos ocurre a nivel de servicio usando interfaces.
- Los objetos DDIC se definen una sola vez dentro del paquete `Z<MODULO>`; nunca duplicar estructuras.
