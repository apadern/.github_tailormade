---
name: abap-test-generator
description: Genera ABAP Unit Tests (AUnit) por capas (unit con CL_ABAP_TESTDOUBLE, capa DB con CL_OSQL_TEST_ENVIRONMENT, integración con datos reales). Úsalo en la fase de tests ABAP o para corregir fallos típicos (inyección de dependencias, test doubles, aserciones de OSQL).
---

# ABAP Test Generator

Generar tests ABAP siguiendo una estrategia por capas para minimizar acoplamiento y garantizar tests rápidos y deterministas.

## Principio clave (OBLIGATORIO)

Separar los tests por intención:

1. **Unit (Método/Lógica pura)**: lógica de negocio sin acceso a BD. Todas las dependencias mockeadas con `CL_ABAP_TESTDOUBLE`. Sin acceso a tablas SAP.
2. **DB (OSQL Test Double)**: tests de capa de acceso a datos usando `CL_OSQL_TEST_ENVIRONMENT` para inyectar datos de prueba sin tocar la BD real.
3. **Integration**: tests con acceso real al sistema (BD activa, BAPIs, RFCs). Solo cuando exista requisito explícito.

No mezclar capas (ej: lógica de negocio + SELECT reales en el mismo test).

## Modos

- `unit`: genera solo tests de métodos con `CL_ABAP_TESTDOUBLE` (sin BD).
- `db`: genera solo tests de capa de datos con `CL_OSQL_TEST_ENVIRONMENT`.
- `integration`: genera solo tests de integración con BD/RFC real.
- `all`: genera todo lo anterior.

## Entradas esperadas

- `backlog/XX_[modulo].md` (fuente principal de casos a cubrir)
- Código existente:
  - Clase bajo prueba: `ZCL_<PAQUETE>_<NOMBRE>` (leer con `abap_getsourcecode`)
  - Interfaces que implementa: `ZIF_<PAQUETE>_<NOMBRE>` (para crear test doubles)
  - Estructuras/tipos DDIC relevantes (leer con `abap_getstructure`)

## Salidas

Los tests ABAP se ubican como **clases locales de prueba** dentro del include de test de la clase bajo prueba.

- Buscar o crear el include de test: `<NOMBRE_CLASE>.testclasses` (tipo `CLAS/OC`, sección `testclasses`)
- Flujo de escritura: `abap_lock` → `abap_setsourcecode` (sección `testclasses`) → `abap_syntaxcheckcode` → `abap_activate`
- Ejecutar con: `abap_unit` sobre la clase bajo prueba

## Estructura de test class (plantilla base)

```abap
"! @testing ZCL_<PAQUETE>_<NOMBRE>
CLASS ltc_<nombre> DEFINITION FINAL FOR TESTING
  RISK LEVEL HARMLESS
  DURATION SHORT.

  PRIVATE SECTION.
    DATA: mo_cut TYPE REF TO zcl_<paquete>_<nombre>.  " cut = Class Under Test

    METHODS:
      setup,
      teardown,
      <test_method> FOR TESTING.
ENDCLASS.

CLASS ltc_<nombre> IMPLEMENTATION.

  METHOD setup.
    mo_cut = NEW zcl_<paquete>_<nombre>( ).
  ENDMETHOD.

  METHOD teardown.
    CLEAR mo_cut.
  ENDMETHOD.

  METHOD <test_method>.
    " Arrange
    DATA(lv_input) = 'valor'.
    " Act
    DATA(lv_result) = mo_cut-><metodo>( lv_input ).
    " Assert
    cl_abap_unit_assert=>assert_equals(
      act = lv_result
      exp = 'esperado'
      msg = '<test_method>: resultado inesperado' ).
  ENDMETHOD.

ENDCLASS.
```

## Reglas de generación (anti-errores)

### A) Inyección de dependencias (CRÍTICO)

Para poder mockear dependencias, la clase bajo prueba **debe recibirlas por constructor o setter**. Si no las tiene, añadirlas antes de generar los tests.

Patrón recomendado:

```abap
" Definición: parámetro opcional para inyección en tests
METHODS constructor
  IMPORTING io_dependency TYPE REF TO zif_<paquete>_<dep> OPTIONAL.
```

En el test, inyectar el doble:

```abap
METHOD setup.
  mo_mock_dep = CAST zif_<paquete>_<dep>(
    cl_abap_testdouble=>create( 'ZIF_<PAQUETE>_<DEP>' ) ).
  mo_cut = NEW zcl_<paquete>_<nombre>( io_dependency = mo_mock_dep ).
ENDMETHOD.
```

### B) Test doubles de clases/interfaces (`CL_ABAP_TESTDOUBLE`)

Usar cuando la clase bajo prueba llama a otras clases/interfaces.

```abap
" Crear double (en setup)
mo_double = CAST zif_mi_interfaz(
  cl_abap_testdouble=>create( 'ZIF_MI_INTERFAZ' ) ).

" Configurar comportamiento esperado
cl_abap_testdouble=>configure_call( mo_double )->returning( lv_valor ).
mo_double->mi_metodo( iv_param = 'entrada' ).

" Verificar llamadas (opcional)
cl_abap_testdouble=>verify_expectations( mo_double ).
```

### C) Test doubles de BD (`CL_OSQL_TEST_ENVIRONMENT`)

Usar cuando la clase ejecuta `SELECT` sobre tablas SAP. Evita acceso a BD real.

```abap
CLASS ltc_db DEFINITION FINAL FOR TESTING
  RISK LEVEL HARMLESS DURATION SHORT.
  PRIVATE SECTION.
    DATA: mo_cut  TYPE REF TO zcl_<paquete>_<nombre>,
          mo_osql TYPE REF TO if_osql_test_environment.
ENDCLASS.

CLASS ltc_db IMPLEMENTATION.
  METHOD setup.
    mo_osql = cl_osql_test_environment=>create(
      i_dependency_list = VALUE #( ( '<TABLA_SAP>' ) ) ).
    mo_cut = NEW zcl_<paquete>_<nombre>( ).
  ENDMETHOD.

  METHOD teardown.
    mo_osql->destroy( ).
  ENDMETHOD.

  METHOD <test_db_method> FOR TESTING.
    " Arrange: inyectar datos de prueba en la tabla mockeada
    mo_osql->insert_test_data( VALUE <TABLA_SAP>( ... ) ).
    " Act
    DATA(lt_result) = mo_cut->leer_datos( ).
    " Assert
    cl_abap_unit_assert=>assert_not_initial(
      act = lt_result
      msg = 'Debe retornar registros' ).
  ENDMETHOD.
ENDCLASS.
```

### D) Niveles de riesgo y duración (OBLIGATORIO)

| Tipo de test | `RISK LEVEL` | `DURATION` |
|---|---|---|
| Unit (sin BD) | `HARMLESS` | `SHORT` |
| DB (OSQL mock) | `HARMLESS` | `SHORT` |
| Integración (BD real) | `DANGEROUS` | `MEDIUM` |
| RFC / BAPI real | `CRITICAL` | `LONG` |

### E) Aserciones disponibles (`CL_ABAP_UNIT_ASSERT`)

```abap
cl_abap_unit_assert=>assert_equals(     act = ...  exp = ...  msg = '...' ).
cl_abap_unit_assert=>assert_not_equals( act = ...  exp = ...  msg = '...' ).
cl_abap_unit_assert=>assert_initial(    act = ...             msg = '...' ).
cl_abap_unit_assert=>assert_not_initial( act = ...            msg = '...' ).
cl_abap_unit_assert=>assert_true(       act = ...             msg = '...' ).
cl_abap_unit_assert=>assert_false(      act = ...             msg = '...' ).
cl_abap_unit_assert=>assert_bound(      act = ...             msg = '...' ).
cl_abap_unit_assert=>assert_not_bound(  act = ...             msg = '...' ).
cl_abap_unit_assert=>fail(              msg = '...' ).
```

### F) FRIENDS — acceso a atributos privados (solo si imprescindible)

Si un atributo privado necesita verificarse directamente en el test, usar la adición `FRIENDS`:

```abap
CLASS zcl_<paquete>_<nombre> DEFINITION ... .
  " Añadir al final de la definición de la clase bajo prueba:
  ...
  PRIVATE SECTION.
    FRIENDS ltc_<nombre>.
ENDCLASS.
```

Preferir siempre verificar comportamiento observable (retornos, excepciones) sobre estado interno.

### G) Excepciones esperadas

Para validar que un método lanza excepción correcta:

```abap
METHOD test_excepcion FOR TESTING.
  TRY.
    mo_cut->metodo_que_falla( ).
    cl_abap_unit_assert=>fail( msg = 'Debería haber lanzado excepción' ).
  CATCH zcx_<paquete>_<excepcion> INTO DATA(lx_ex).
    cl_abap_unit_assert=>assert_not_initial(
      act = lx_ex->get_text( ) msg = 'Mensaje de excepción vacío' ).
  ENDTRY.
ENDMETHOD.
```

## Flujo de escritura en el sistema (OBLIGATORIO)

1. Leer clase bajo prueba: `abap_getsourcecode` (sección `testclasses` para ver tests existentes).
2. Preparar código del include de test completo (no parcial).
3. `abap_lock` sobre la clase bajo prueba.
4. `abap_setsourcecode` con sección `testclasses`.
5. `abap_syntaxcheckcode` — corregir errores antes de continuar.
6. `abap_activate`.
7. `abap_unit` para ejecutar y verificar resultados.

## Checklist de calidad (antes de finalizar)

- Tests compilan sin errores de sintaxis (`abap_syntaxcheckcode` OK).
- Tests unit no contienen `SELECT` ni llamadas a RFC/BAPI reales.
- Tests DB usan `CL_OSQL_TEST_ENVIRONMENT` y hacen `destroy()` en `teardown`.
- Cada test tiene nombre descriptivo en inglés o español que describe el escenario.
- Cada test tiene exactamente **un** `assert_*` principal (pueden tener secundarios de guardia).
- Tests de integración marcados con `RISK LEVEL DANGEROUS` como mínimo.
- Método `setup` inicializa el objeto bajo prueba limpio.
- Método `teardown` limpia recursos (especialmente `CL_OSQL_TEST_ENVIRONMENT`).

## Ejecución sugerida

```
abap_unit → clase ZCL_<PAQUETE>_<NOMBRE>
```

Los resultados muestran tests pasados/fallados con nombre de método y mensaje de aserción.
