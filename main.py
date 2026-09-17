"""
Procedimiento 1701 - Diferencia de Cambio
Punto de entrada principal

Uso:
    1. Abrir Excel con los datos del cliente
    2. Completar la hoja de Análisis (1701.1 - Análisis) con:
       - Nombre del cliente
       - Fecha de auditoría
       - Códigos de cuenta (columna C)
       - Nombre/detalle de cuenta (columna D)
       - Saldo cierre anterior (columna E)
    3. Ejecutar este script: python main.py
    4. La herramienta completará automáticamente:
       - Importes mensuales (columnas F-Q)
       - TC promedio mensual
       - Fórmulas de posición neta y diferencia
       - Tabla dinámica en nueva pestaña
"""

import sys
import os

# Agregar directorio padre al path para encontrar los módulos
directorio_actual = os.path.dirname(os.path.abspath(__file__))
directorio_padre = os.path.dirname(directorio_actual)
sys.path.insert(0, directorio_padre)

# También agregar directorio actual por si se ejecuta desde ahí
sys.path.insert(0, directorio_actual)

from excel_reader import ExcelReader
from mayors_processor import MayorsProcessor
from tc_calculator import TCCalculator
from analysis_completer import AnalysisCompleter
from pivot_table import PivotTableCreator
from config import (
    MENSAJE_PROCESO_EXITOSO,
    MENSAJE_ERROR_LECTURA
)


def main():
    """Función principal del Procedimiento 1701"""
    
    print("=" * 60)
    print("Procedimiento 1701 - Diferencia de Cambio")
    print("=" * 60)
    
    try:
        # ==========================================
        # PASO 1: Leer datos del Excel
        # ==========================================
        print("\n[PASO 1] Leyendo datos del Excel...")
        
        reader = ExcelReader()
        
        # Leer cuentas de la hoja de Análisis
        cuentas = reader.leer_cuentas_analisis()
        print(f"  Cuentas encontradas: {len(cuentas)}")
        
        # Leer información del cliente
        info_cliente = reader.obtener_info_cliente()
        print(f"  Cliente: {info_cliente.get('cliente', 'No especificado')}")
        print(f"  Fecha auditoría: {info_cliente.get('fecha_auditoria', 'No especificada')}")
        
        # Leer configuración de monedas
        config_monedas = reader.leer_configuracion_monedas()
        print(f"  Monedas configuradas: {len(config_monedas)}")
        
        # ==========================================
        # PASO 2: Procesar Mayores
        # ==========================================
        print("\n[PASO 2] Procesando Mayores...")
        
        # Leer mayores
        df_mayores = reader.leer_mayores()
        
        # Crear procesador y filtrar por cuentas
        processor = MayorsProcessor(df_mayores)
        processor_filtrado = processor.filtrar_por_cuentas(cuentas)
        
        # Acumular saldos mensuales
        saldos_por_cuenta = processor_filtrado.obtener_saldos_por_cuenta_y_mes()
        print(f"  Saldos calculados para {len(saldos_por_cuenta)} cuentas")
        
        # Obtener meses disponibles
        todos_los_meses = set()
        for cuenta, meses in saldos_por_cuenta.items():
            todos_los_meses.update(meses.keys())
        
        meses_disponibles = sorted(list(todos_los_meses))
        print(f"  Meses disponibles: {len(meses_disponibles)}")
        
        # ==========================================
        # PASO 3: Calcular TC Promedio (desde API del BCU)
        # ==========================================
        print("\n[PASO 3] Calculando TC Promedio Mensual desde API del BCU...")
        
        # Crear calculadora (usa la API del BCU)
        tc_calc = TCCalculator()
        
        # Determinar rango de fechas desde los Mayores
        fecha_min, fecha_max = processor_filtrado.obtener_periodo_minimo_maximo()
        
        if fecha_min is None or fecha_max is None:
            print("  No se pudieron determinar las fechas de los Mayores")
            return False
        
        print(f"  Período: {fecha_min.strftime('%d/%m/%Y')} - {fecha_max.strftime('%d/%m/%Y')}")
        
        # Calcular TC promedio mensual (para USD por defecto)
        codigo_usd = config_monedas[0].get("codigo_bcu", 2225) if config_monedas else 2225
        
        tc_por_mes = tc_calc.calcular_tc_promedio_mensual(
            moneda_codigo=codigo_usd,
            fecha_desde=fecha_min.date() if hasattr(fecha_min, 'date') else fecha_min,
            fecha_hasta=fecha_max.date() if hasattr(fecha_max, 'date') else fecha_max
        )
        print(f"  TC promedio calculado para {len(tc_por_mes)} meses")
        
        # ==========================================
        # PASO 4: Completar Hoja de Análisis
        # ==========================================
        print("\n[PASO 4] Completando Hoja de Análisis...")
        
        # Crear completador
        completer = AnalysisCompleter(reader.wb)
        
        # Obtener saldo de la empresa desde la hoja de Análisis
        saldo_empresa_usd = reader.obtener_saldo_empresa_usd()
        print(f"  Saldo empresa USD: {saldo_empresa_usd}")
        
        # Completar todos los cálculos
        completer.completar_todos_los_calculos(
            saldos_por_cuenta,
            tc_por_mes,
            meses_disponibles,
            saldo_empresa_usd
        )
        
        # ==========================================
        # PASO 5: Crear Tabla Dinámica
        # ==========================================
        print("\n[PASO 5] Creando Tabla Dinámica...")
        
        # Crear tabla dinámica
        pivot_creator = PivotTableCreator(reader.wb)
        hoja_pivot = pivot_creator.crear_tabla_dinamica(
            saldos_por_cuenta,
            tc_por_mes,
            meses_disponibles,
            info_cliente
        )
        
        # Formatear tabla
        pivot_creator.formatear_tabla(hoja_pivot, len(meses_disponibles))
        
        # ==========================================
        # PASO 6: Resumen Final
        # ==========================================
        print("\n" + "=" * 60)
        print(MENSAJE_PROCESO_EXITOSO)
        print("=" * 60)
        
        print(f"\nResumen:")
        print(f"  - Cuentas procesadas: {len(cuentas)}")
        print(f"  - Meses procesados: {len(meses_disponibles)}")
        print(f"  - Monedas: {len(config_monedas)}")
        print(f"\nSe completaron:")
        print(f"  - Importes mensuales en hoja de Análisis")
        print(f"  - TC promedio mensual")
        print(f"  - Fórmulas de posición neta y diferencia")
        print(f"  - Tabla dinámica en hoja '{hoja_pivot.name}'")
        
        return True
        
    except Exception as e:
        print(f"\nError: {e}")
        print(f"\n{MENSAJE_ERROR_LECTURA}")
        return False


if __name__ == "__main__":
    # Ejecutar principal
    success = main()
    
    if not success:
        sys.exit(1)
