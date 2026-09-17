"""Tests para mayors_processor.py"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from datetime import datetime
from mayors_processor import MayorsProcessor


def test_filtrar_por_cuentas():
    """Test que el filtrado por cuentas funcione correctamente."""
    # Crear datos de prueba
    data = {
        "Cuenta": ["11111", "11111", "22222", "11111", "33333"],
        "Fecha": [
            datetime(2025, 7, 1),
            datetime(2025, 8, 1),
            datetime(2025, 7, 15),
            datetime(2025, 9, 1),
            datetime(2025, 7, 20),
        ],
        "Concepto": ["Mov1", "Mov2", "Mov3", "Mov4", "Mov5"],
        "Debe $": [1000, 500, 200, 300, 100],
        "Haber $": [0, 0, 0, 0, 0],
        "Saldo $": [1000, 1500, 200, 1800, 100],
    }
    df = pd.DataFrame(data)
    
    processor = MayorsProcessor(df)
    filtrado = processor.filtrar_por_cuentas(["11111", "33333"])
    
    # Debe quedar 4 movimientos (3 de 11111 + 1 de 33333)
    assert len(filtrado.df_mayores) == 4
    assert set(filtrado.df_mayores["Cuenta"].unique()) == {"11111", "33333"}


def test_acumular_saldos_mensuales_activo():
    """Test acumulación de saldos para cuentas de ACTIVO (1xxx)."""
    data = {
        "Cuenta": ["11111", "11111", "11111"],
        "Fecha": [
            datetime(2025, 7, 5),
            datetime(2025, 7, 15),
            datetime(2025, 8, 10),
        ],
        "Concepto": ["Mov1", "Mov2", "Mov3"],
        "Debe $": [1000, 500, 200],
        "Haber $": [0, 0, 0],
        "Saldo $": [1000, 1500, 1700],
    }
    df = pd.DataFrame(data)
    
    processor = MayorsProcessor(df)
    saldos = processor.obtener_saldos_por_cuenta_y_mes()
    
    # Cuenta 11111 debe tener 2 meses
    assert "11111" in saldos
    assert len(saldos["11111"]) == 2
    
    # Activo: movimiento = Debe - Haber
    # Julio: (1000-0) + (500-0) = 1500
    julio = datetime(2025, 7, 1)
    assert saldos["11111"][julio] == 1500
    
    # Agosto: 1500 + (200-0) = 1700
    agosto = datetime(2025, 8, 1)
    assert saldos["11111"][agosto] == 1700


def test_acumular_saldos_mensuales_pasivo():
    """Test acumulación de saldos para cuentas de PASIVO (2xxx)."""
    data = {
        "Cuenta": ["21100", "21100", "21100"],
        "Fecha": [
            datetime(2025, 7, 5),
            datetime(2025, 7, 15),
            datetime(2025, 8, 10),
        ],
        "Concepto": ["Prov1", "Prov2", "Prov3"],
        "Debe $": [0, 0, 100],
        "Haber $": [500, 300, 0],
        "Saldo $": [500, 800, 700],
    }
    df = pd.DataFrame(data)
    
    processor = MayorsProcessor(df)
    saldos = processor.obtener_saldos_por_cuenta_y_mes()
    
    assert "21100" in saldos
    assert len(saldos["21100"]) == 2
    
    # Pasivo: movimiento = Haber - Debe
    # Julio: (500-0) + (300-0) = 800
    julio = datetime(2025, 7, 1)
    assert saldos["21100"][julio] == 800
    
    # Agosto: 800 + (0-100) = 700
    agosto = datetime(2025, 8, 1)
    assert saldos["21100"][agosto] == 700


def test_es_cuenta_pasivo():
    """Test de detección de tipo de cuenta."""
    # Pasivo
    assert MayorsProcessor._es_cuenta_pasivo("21100") == True
    assert MayorsProcessor._es_cuenta_pasivo("21100.01") == True
    assert MayorsProcessor._es_cuenta_pasivo("29999") == True
    
    # Activo
    assert MayorsProcessor._es_cuenta_pasivo("11111") == False
    assert MayorsProcessor._es_cuenta_pasivo("11100.05") == False
    assert MayorsProcessor._es_cuenta_pasivo("33333") == False
    assert MayorsProcessor._es_cuenta_pasivo("4305") == False


def test_mixto_activo_pasivo():
    """Test con cuentas mixtas: activo y pasivo juntas."""
    data = {
        "Cuenta": ["11111", "11111", "21100", "21100"],
        "Fecha": [
            datetime(2025, 7, 5),
            datetime(2025, 8, 10),
            datetime(2025, 7, 10),
            datetime(2025, 8, 15),
        ],
        "Concepto": ["Act1", "Act2", "Pas1", "Pas2"],
        "Debe $": [1000, 500, 0, 200],
        "Haber $": [0, 0, 800, 0],
        "Saldo $": [1000, 1500, 800, 600],
    }
    df = pd.DataFrame(data)
    
    processor = MayorsProcessor(df)
    saldos = processor.obtener_saldos_por_cuenta_y_mes()
    
    julio = datetime(2025, 7, 1)
    agosto = datetime(2025, 8, 1)
    
    # Activo 11111: Debe - Haber
    assert saldos["11111"][julio] == 1000
    assert saldos["11111"][agosto] == 1500
    
    # Pasivo 21100: Haber - Debe
    assert saldos["21100"][julio] == 800
    assert saldos["21100"][agosto] == 600


def test_acumular_saldos_con_nan():
    """Test que los NaN se manejen correctamente."""
    data = {
        "Cuenta": ["11111", "11111"],
        "Fecha": [datetime(2025, 7, 5), datetime(2025, 7, 15)],
        "Concepto": ["Mov1", "Mov2"],
        "Debe $": [1000, float('nan')],  # NaN en Debe
        "Haber $": [float('nan'), 0],    # NaN en Haber
        "Saldo $": [1000, 1000],
    }
    df = pd.DataFrame(data)
    
    processor = MayorsProcessor(df)
    saldos = processor.obtener_saldos_por_cuenta_y_mes()
    
    # Debe manejar NaN sin errores
    assert "11111" in saldos
    julio = datetime(2025, 7, 1)
    # 1000 + 0 = 1000 (NaN se convierte en 0)
    assert saldos["11111"][julio] == 1000


def test_obtener_periodo_minimo_maximo():
    """Test que se obtengan las fechas min y max correctamente."""
    data = {
        "Cuenta": ["11111", "11111"],
        "Fecha": [datetime(2025, 7, 5), datetime(2025, 12, 20)],
        "Concepto": ["Mov1", "Mov2"],
        "Debe $": [1000, 500],
        "Haber $": [0, 0],
        "Saldo $": [1000, 1500],
    }
    df = pd.DataFrame(data)
    
    processor = MayorsProcessor(df)
    fecha_min, fecha_max = processor.obtener_periodo_minimo_maximo()
    
    assert fecha_min == datetime(2025, 7, 5)
    assert fecha_max == datetime(2025, 12, 20)


def test_df_vacio():
    """Test con DataFrame vacío."""
    df = pd.DataFrame(columns=["Cuenta", "Fecha", "Concepto", "Debe $", "Haber $", "Saldo $"])
    
    processor = MayorsProcessor(df)
    saldos = processor.obtener_saldos_por_cuenta_y_mes()
    
    assert saldos == {}
    
    fecha_min, fecha_max = processor.obtener_periodo_minimo_maximo()
    assert fecha_min is None
    assert fecha_max is None


if __name__ == "__main__":
    test_filtrar_por_cuentas()
    print("[OK] test_filtrar_por_cuentas")
    
    test_acumular_saldos_mensuales_activo()
    print("[OK] test_acumular_saldos_mensuales_activo")
    
    test_acumular_saldos_mensuales_pasivo()
    print("[OK] test_acumular_saldos_mensuales_pasivo")
    
    test_es_cuenta_pasivo()
    print("[OK] test_es_cuenta_pasivo")
    
    test_mixto_activo_pasivo()
    print("[OK] test_mixto_activo_pasivo")
    
    test_acumular_saldos_con_nan()
    print("[OK] test_acumular_saldos_con_nan")
    
    test_obtener_periodo_minimo_maximo()
    print("[OK] test_obtener_periodo_minimo_maximo")
    
    test_df_vacio()
    print("[OK] test_df_vacio")
    
    print("\nTodos los tests pasaron!")
