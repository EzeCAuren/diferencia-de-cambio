# Diferencia de Cambio - Procedimiento 1701

Herramienta de auditoría para el procedimiento 1701 (Diferencia de Cambio). Lee datos de un Excel y completa automáticamente los análisis de tipo de cambio.

## Qué hace

1. **Lee cuentas** de la hoja de Análisis (detecta automáticamente dónde empiezan)
2. **Procesa Mayores** con detección automática de columnas (no depende del formato)
3. **Obtiene TC promedio** del BCU vía API en tiempo real
4. **Completa la hoja de Análisis** con saldos mensuales, TC, posición neta y diferencia
5. **Crea tabla dinámica** en nueva pestaña

## Requisitos

- Python 3.10+
- Excel abierto con los datos del cliente
- Conexión a internet (para API del BCU)

## Instalación

```bash
pip install xlwings pandas requests
```

## Uso

1. Abrir el Excel del cliente
2. Completar la hoja `1701.1 - Análisis` con:
   - Nombre del cliente (fila 2)
   - Fecha de auditoría (fila 4)
   - Códigos de cuenta (columna C, después de "Cuentas")
   - Nombre/detalle de cuenta (columna D)
   - Saldo cierre anterior (columna E)
3. Ejecutar:

```bash
python main.py
```

## Estructura

```
diferencia_cambio/
├── main.py              # Punto de entrada
├── config.py            # Constantes y configuración
├── excel_reader.py      # Lectura de datos desde Excel
├── mayors_processor.py  # Filtrado y acumulación de saldos
├── tc_calculator.py     # Cálculo de TC promedio (API BCU)
├── bcu_client.py        # Cliente SOAP del BCU
├── analysis_completer.py # Completado de hoja de Análisis
└── pivot_table.py       # Creación de tabla dinámica
```

## API del BCU

Obtiene cotizaciones oficiales del Banco Central del Uruguay:
- **Endpoint**: `https://cotizaciones.bcu.gub.uy/wscotizaciones/servlet/awsbcucotizaciones`
- **Monedas**: USD (2225), EUR (978), BRL (986), GBP (826), CHF (756)

## Formato de Mayores

La herramienta detecta automáticamente las columnas de la hoja Mayores. Busca palabras clave como:
- Cuenta, CTA, CÓDIGO
- Fecha, DATE
- Debe, Haber, Saldo
- USD

No depende de un formato fijo.
