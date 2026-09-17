"""Tests para tc_calculator.py"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, datetime
from tc_calculator import TCCalculator


def test_calcular_tc_promedio_mensual():
    """Test que el cálculo de TC promedio devuelva resultados."""
    from datetime import datetime
    tc_calc = TCCalculator()
    
    # Un mes específico
    resultado = tc_calc.calcular_tc_promedio_mensual(
        moneda_codigo=2225,  # USD
        fecha_desde=date(2025, 7, 1),
        fecha_hasta=date(2025, 7, 31)
    )
    
    assert len(resultado) == 1
    # La clave es datetime, no date
    assert datetime(2025, 7, 1) in resultado
    assert resultado[datetime(2025, 7, 1)] > 0


def test_tc_rango_multiples_meses():
    """Test con rango de varios meses."""
    tc_calc = TCCalculator()
    
    resultado = tc_calc.calcular_tc_promedio_mensual(
        moneda_codigo=2225,
        fecha_desde=date(2025, 7, 1),
        fecha_hasta=date(2025, 12, 31)
    )
    
    # Debe haber al menos 1 mes (puede haber más si hay datos)
    assert len(resultado) >= 1
    
    # Todos los valores deben ser positivos
    for fecha, tc in resultado.items():
        assert tc > 0, f"TC negativo o cero para {fecha}"


def test_tc_claves_son_datetime():
    """Test que las claves del resultado sean datetime."""
    tc_calc = TCCalculator()
    
    resultado = tc_calc.calcular_tc_promedio_mensual(
        moneda_codigo=2225,
        fecha_desde=date(2025, 7, 1),
        fecha_hasta=date(2025, 7, 31)
    )
    
    for fecha in resultado.keys():
        assert isinstance(fecha, datetime), f"Clave {fecha} no es datetime"


def test_tc_moneda_invalida():
    """Test con código de moneda inexistente."""
    tc_calc = TCCalculator()
    
    resultado = tc_calc.calcular_tc_promedio_mensual(
        moneda_codigo=99999,  # No existe
        fecha_desde=date(2025, 7, 1),
        fecha_hasta=date(2025, 7, 31)
    )
    
    # Debe devolver vacío o sin errores
    assert isinstance(resultado, dict)


if __name__ == "__main__":
    test_calcular_tc_promedio_mensual()
    print("[OK] test_calcular_tc_promedio_mensual")
    
    test_tc_rango_multiples_meses()
    print("[OK] test_tc_rango_multiples_meses")
    
    test_tc_claves_son_datetime()
    print("[OK] test_tc_claves_son_datetime")
    
    test_tc_moneda_invalida()
    print("[OK] test_tc_moneda_invalida")
    
    print("\nTodos los tests de TC pasaron!")
