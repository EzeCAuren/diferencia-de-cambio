"""Tests para config.py - Constantes y configuración"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    HOJA_MAYORES,
    HOJA_ANALISIS,
    HOJA_TABLA_DINAMICA,
    COLUMNA_CUENTA,
    COLUMNAS_MENSUALES,
    COLUMNA_TOTAL,
    FILA_INICIO_CUENTAS,
    MARCADOR_INICIO_CUENTAS,
    FILAS_A_IGNORAR,
    ETIQUETAS_FILAS,
    PALABRAS_CLAVE_MAYORES,
    MONEDAS_BCU,
    MONEDA_BASE_POR_DEFECTO,
    MESES,
)


def test_hojas_definidas():
    """Test que todas las hojas estén definidas."""
    assert HOJA_MAYORES == "Mayores"
    assert HOJA_ANALISIS == "1701.1 - Análisis"
    assert HOJA_TABLA_DINAMICA == "Tabla Dinamica Valores"


def test_columnas_analisis():
    """Test de columnas de análisis."""
    assert COLUMNA_CUENTA == "C"
    assert COLUMNA_TOTAL == "R"
    assert len(COLUMNAS_MENSUALES) == 12  # 12 meses


def test_marcador_inicio():
    """Test del marcador de inicio de cuentas."""
    assert isinstance(MARCADOR_INICIO_CUENTAS, list)
    assert "CUENTAS" in MARCADOR_INICIO_CUENTAS


def test_filas_a_ignorar():
    """Test de filas a ignorar."""
    assert isinstance(FILAS_A_IGNORAR, list)
    assert "TOTAL" in FILAS_A_IGNORAR
    assert "TOTAL ACTIVO" in FILAS_A_IGNORAR


def test_etiquetas_filas():
    """Test de etiquetas de filas - deben ser diccionario con funciones."""
    assert isinstance(ETIQUETAS_FILAS, dict)
    assert "TOTAL_ACTIVO" in ETIQUETAS_FILAS
    assert "TC" in ETIQUETAS_FILAS
    
    # Cada valor debe ser callable
    for clave, detector in ETIQUETAS_FILAS.items():
        assert callable(detector), f"Detector de {clave} no es callable"


def test_etiquetas_filas_funciones():
    """Test que las funciones de detección funcionen."""
    # TOTAL ACTIVO
    assert ETIQUETAS_FILAS["TOTAL_ACTIVO"]("TOTAL ACTIVO") == True
    assert ETIQUETAS_FILAS["TOTAL_ACTIVO"]("TOTAL PASIVO") == False
    
    # TC
    assert ETIQUETAS_FILAS["TC"]("TC") == True
    assert ETIQUETAS_FILAS["TC"]("TASA") == False
    
    # POSICION_NETA_UY
    assert ETIQUETAS_FILAS["POSICION_NETA_UY"]("POSICION NETA UY$") == True
    assert ETIQUETAS_FILAS["POSICION_NETA_UY"]("POSICION NETA USD") == False


def test_monedas_bcu():
    """Test de monedas BCU."""
    assert isinstance(MONEDAS_BCU, dict)
    assert "USD" in MONEDAS_BCU
    assert "EUR" in MONEDAS_BCU
    assert MONEDAS_BCU["USD"] == 2225


def test_meses():
    """Test de meses para tabla dinámica."""
    assert isinstance(MESES, list)
    assert len(MESES) == 12
    assert MESES[0] == "Jul"  # Empieza en julio


if __name__ == "__main__":
    test_hojas_definidas()
    print("[OK] test_hojas_definidas")
    
    test_columnas_analisis()
    print("[OK] test_columnas_analisis")
    
    test_marcador_inicio()
    print("[OK] test_marcador_inicio")
    
    test_filas_a_ignorar()
    print("[OK] test_filas_a_ignorar")
    
    test_etiquetas_filas()
    print("[OK] test_etiquetas_filas")
    
    test_etiquetas_filas_funciones()
    print("[OK] test_etiquetas_filas_funciones")
    
    test_monedas_bcu()
    print("[OK] test_monedas_bcu")
    
    test_meses()
    print("[OK] test_meses")
    
    print("\nTodos los tests de config pasaron!")
