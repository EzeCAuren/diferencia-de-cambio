"""Tests para tc_calculator.py"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, datetime
from unittest.mock import patch, MagicMock
from tc_calculator import TCCalculator
from bcu_client import BCUResponse, ExchangeRate


def _mock_bcu_response(*args, **kwargs):
    """Respuesta mock del BCU para testing sin red."""
    rates = [
        ExchangeRate(fecha=date(2025, 7, 1), moneda_id=2225, compra=39.5, venta=40.5),
        ExchangeRate(fecha=date(2025, 7, 2), moneda_id=2225, compra=39.6, venta=40.6),
        ExchangeRate(fecha=date(2025, 7, 3), moneda_id=2225, compra=39.7, venta=40.7),
    ]
    return BCUResponse(success=True, rates=rates, message="3 cotizaciones")


def test_calcular_tc_promedio_mensual():
    """Test que el cálculo de TC promedio devuelva resultados (mocked)."""
    tc_calc = TCCalculator()
    
    with patch.object(tc_calc.bcu_client, 'get_exchange_rates', side_effect=_mock_bcu_response):
        resultado = tc_calc.calcular_tc_promedio_mensual(
            moneda_codigo=2225,
            fecha_desde=date(2025, 7, 1),
            fecha_hasta=date(2025, 7, 31)
        )
    
    assert len(resultado) == 1
    assert datetime(2025, 7, 1) in resultado
    # Promedio de venta: (40.5 + 40.6 + 40.7) / 3 = 40.6
    assert abs(resultado[datetime(2025, 7, 1)] - 40.6) < 0.01


def test_tc_rango_multiples_meses():
    """Test con rango de varios meses (mocked)."""
    tc_calc = TCCalculator()
    
    rates = [
        ExchangeRate(fecha=date(2025, 7, 1), moneda_id=2225, compra=39.5, venta=40.5),
        ExchangeRate(fecha=date(2025, 8, 1), moneda_id=2225, compra=40.0, venta=41.0),
        ExchangeRate(fecha=date(2025, 9, 1), moneda_id=2225, compra=40.5, venta=41.5),
    ]
    
    with patch.object(tc_calc.bcu_client, 'get_exchange_rates', return_value=BCUResponse(success=True, rates=rates)):
        resultado = tc_calc.calcular_tc_promedio_mensual(
            moneda_codigo=2225,
            fecha_desde=date(2025, 7, 1),
            fecha_hasta=date(2025, 9, 30)
        )
    
    assert len(resultado) == 3
    for fecha, tc in resultado.items():
        assert tc > 0, f"TC negativo o cero para {fecha}"


def test_tc_claves_son_datetime():
    """Test que las claves del resultado sean datetime."""
    tc_calc = TCCalculator()
    
    rates = [ExchangeRate(fecha=date(2025, 7, 1), moneda_id=2225, compra=39.5, venta=40.5)]
    
    with patch.object(tc_calc.bcu_client, 'get_exchange_rates', return_value=BCUResponse(success=True, rates=rates)):
        resultado = tc_calc.calcular_tc_promedio_mensual(
            moneda_codigo=2225,
            fecha_desde=date(2025, 7, 1),
            fecha_hasta=date(2025, 7, 31)
        )
    
    for fecha in resultado.keys():
        assert isinstance(fecha, datetime), f"Clave {fecha} no es datetime"


def test_tc_moneda_invalida():
    """Test con código de moneda inexistente (mocked, devuelve vacío)."""
    tc_calc = TCCalculator()
    
    with patch.object(tc_calc.bcu_client, 'get_exchange_rates', return_value=BCUResponse(success=False, rates=[], message="Moneda no encontrada")):
        resultado = tc_calc.calcular_tc_promedio_mensual(
            moneda_codigo=99999,
            fecha_desde=date(2025, 7, 1),
            fecha_hasta=date(2025, 7, 31)
        )
    
    assert isinstance(resultado, dict)
    assert len(resultado) == 0


def test_tc_cache():
    """Test que el cache funcione (segunda llamada no llama al API)."""
    tc_calc = TCCalculator()
    
    with patch.object(tc_calc.bcu_client, 'get_exchange_rates', side_effect=_mock_bcu_response) as mock:
        # Primera llamada - llama al API
        resultado1 = tc_calc.calcular_tc_promedio_mensual(
            moneda_codigo=2225,
            fecha_desde=date(2025, 7, 1),
            fecha_hasta=date(2025, 7, 31)
        )
        # Segunda llamada - usa cache
        resultado2 = tc_calc.calcular_tc_promedio_mensual(
            moneda_codigo=2225,
            fecha_desde=date(2025, 7, 1),
            fecha_hasta=date(2025, 7, 31)
        )
    
    # Solo debe haber llamado al API una vez (la segunda usa cache)
    assert mock.call_count == 1
    assert resultado1 == resultado2


if __name__ == "__main__":
    test_calcular_tc_promedio_mensual()
    print("[OK] test_calcular_tc_promedio_mensual")
    
    test_tc_rango_multiples_meses()
    print("[OK] test_tc_rango_multiples_meses")
    
    test_tc_claves_son_datetime()
    print("[OK] test_tc_claves_son_datetime")
    
    test_tc_moneda_invalida()
    print("[OK] test_tc_moneda_invalida")
    
    test_tc_cache()
    print("[OK] test_tc_cache")
    
    print("\nTodos los tests de TC pasaron!")
