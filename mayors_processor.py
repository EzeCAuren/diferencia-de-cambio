"""
Procesador de Mayores
"""

import pandas as pd
from collections import defaultdict

from config import (
    COLUMNA_MAYOR_CUENTA,
    COLUMNA_MAYOR_FECHA,
    COLUMNA_MAYOR_DEBE_UY,
    COLUMNA_MAYOR_HABER_UY,
    COLUMNA_MAYOR_SALDO_UY
)


class MayorsProcessor:
    """Procesa los mayores para obtener saldos acumulados mensuales"""

    def __init__(self, df_mayores):
        """
        Inicializa el procesador.
        
        Args:
            df_mayores: DataFrame con los mayores
        """
        self.df_mayores = df_mayores

    def filtrar_por_cuentas(self, cuentas):
        """
        Filtra los mayores por lista de cuentas.
        
        Args:
            cuentas: Lista de códigos de cuenta
            
        Returns:
            MayorsProcessor: Nuevo procesador con datos filtrados
        """
        # Asegurar que las cuentas sean strings
        cuentas_str = [str(c).strip() for c in cuentas]
        
        # Filtrar
        df_filtrado = self.df_mayores[
            self.df_mayores[COLUMNA_MAYOR_CUENTA].isin(cuentas_str)
        ].copy()

        print(f"Se filtraron {len(df_filtrado)} movimientos para {len(cuentas_str)} cuentas")
        
        return MayorsProcessor(df_filtrado)

    def acumular_saldos_mensuales(self):
        """
        Acumula saldos mes a mes para cada cuenta.
        
        Returns:
            dict: Diccionario {cuenta: {(mes, anio): saldo_acumulado}}
        """
        if self.df_mayores.empty:
            return {}

        df = self.df_mayores.copy()
        
        # Asegurar que tenemos fechas válidas
        df = df.dropna(subset=[COLUMNA_MAYOR_FECHA])
        
        if df.empty:
            return {}

        # Crear columna de año-mes
        df['anio_mes'] = df[COLUMNA_MAYOR_FECHA].dt.to_period('M')
        
        # Diccionario para almacenar saldos acumulados
        saldos_acumulados = defaultdict(lambda: defaultdict(float))
        
        # Para cada cuenta
        for cuenta in df[COLUMNA_MAYOR_CUENTA].unique():
            df_cuenta = df[df[COLUMNA_MAYOR_CUENTA] == cuenta].copy()
            
            # Ordenar por fecha
            df_cuenta = df_cuenta.sort_values(COLUMNA_MAYOR_FECHA)
            
            # Acumular saldos
            saldo_acumulado = 0
            
            for _, row in df_cuenta.iterrows():
                fecha = row[COLUMNA_MAYOR_FECHA]
                anio_mes = fecha.to_period('M')
                
                # Calcular movimiento del mes
                debe_val = row.get(COLUMNA_MAYOR_DEBE_UY, 0)
                haber_val = row.get(COLUMNA_MAYOR_HABER_UY, 0)
                
                # Manejar NaN correctamente
                debe = 0 if pd.isna(debe_val) else float(debe_val)
                haber = 0 if pd.isna(haber_val) else float(haber_val)
                
                # El saldo es Debe - Haber (para cuentas de activo)
                # Nota: Esto puede variar según el tipo de cuenta
                movimiento = debe - haber
                
                saldo_acumulado += movimiento
                saldos_acumulados[cuenta][anio_mes] = saldo_acumulado

        print(f"Se acumularon saldos para {len(saldos_acumulados)} cuentas")
        return dict(saldos_acumulados)

    def obtener_saldos_por_cuenta_y_mes(self):
        """
        Obtiene saldos organizados por cuenta y mes.
        
        Returns:
            dict: {cuenta: {mes: saldo}}
        """
        saldos = self.acumular_saldos_mensuales()
        
        # Convertir a formato más simple
        resultado = {}
        for cuenta, meses in saldos.items():
            resultado[cuenta] = {}
            for periodo, saldo in meses.items():
                # Usar el primer día del mes como clave
                fecha = periodo.to_timestamp()
                resultado[cuenta][fecha] = saldo
        
        return resultado

    def obtener_periodo_minimo_maximo(self):
        """
        Obtiene el período mínimo y máximo de los datos.
        
        Returns:
            tuple: (fecha_min, fecha_max)
        """
        if self.df_mayores.empty:
            return None, None

        fecha_min = self.df_mayores[COLUMNA_MAYOR_FECHA].min()
        fecha_max = self.df_mayores[COLUMNA_MAYOR_FECHA].max()
        
        return fecha_min, fecha_max
