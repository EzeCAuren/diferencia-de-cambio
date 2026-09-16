"""
Calculadora de Tipo de Cambio Promedio Mensual
Usa la API del BCU para obtener cotizaciones en tiempo real
"""

from datetime import datetime, date, timedelta
from collections import defaultdict

from bcu_client import BCUClient

from config import (
    MONEDAS_BCU,
    MONEDA_BASE_POR_DEFECTO
)


class TCCalculator:
    """Calcula el TC promedio mensual usando la API del BCU"""

    def __init__(self):
        """
        Inicializa la calculadora con cliente BCU.
        """
        self.bcu_client = BCUClient()
        self.cache = {}  # Cache simple en memoria

    def obtener_cotizaciones(self, moneda_codigo, fecha_desde, fecha_hasta):
        """
        Obtiene cotizaciones del BCU para un rango de fechas.
        
        Args:
            moneda_codigo: Código de la moneda en BCU (2225=USD, 978=EUR, etc.)
            fecha_desde: Fecha desde
            fecha_hasta: Fecha hasta
            
        Returns:
            list: Lista de ExchangeRate
        """
        # Verificar cache
        cache_key = (moneda_codigo, fecha_desde, fecha_hasta)
        if cache_key in self.cache:
            print(f"  Usando cotizaciones cacheadas para moneda {moneda_codigo}")
            return self.cache[cache_key]

        print(f"  Descargando cotizaciones del BCU para moneda {moneda_codigo}...")
        
        resultado = self.bcu_client.get_exchange_rates(
            currency_code=moneda_codigo,
            date_from=fecha_desde,
            date_to=fecha_hasta
        )

        if not resultado.success:
            print(f"  Error al obtener cotizaciones: {resultado.message}")
            return []

        # Guardar en cache
        self.cache[cache_key] = resultado.rates
        
        print(f"  Se obtuvieron {len(resultado.rates)} cotizaciones")
        return resultado.rates

    def calcular_tc_promedio_mensual(self, moneda_codigo=None, fecha_desde=None, fecha_hasta=None):
        """
        Calcula el TC promedio de venta por mes usando la API del BCU.
        
        Args:
            moneda_codigo: Código de la moneda en BCU (por defecto USD)
            fecha_desde: Fecha desde (por defecto hace 1 año)
            fecha_hasta: Fecha hasta (por defecto hoy)
            
        Returns:
            dict: {fecha_primer_dia_mes: tc_promedio}
        """
        # Valores por defecto
        if moneda_codigo is None:
            moneda_codigo = MONEDAS_BCU.get(MONEDA_BASE_POR_DEFECTO, 2225)
        
        if fecha_hasta is None:
            fecha_hasta = date.today()
        
        if fecha_desde is None:
            # Por defecto, un año atrás
            fecha_desde = fecha_hasta - timedelta(days=365)

        # Obtener cotizaciones del BCU
        cotizaciones = self.obtener_cotizaciones(
            moneda_codigo, 
            fecha_desde, 
            fecha_hasta
        )

        if not cotizaciones:
            return {}

        # Agrupar por mes y calcular promedio
        tc_por_mes = defaultdict(list)
        
        for cotizacion in cotizaciones:
            # Crear fecha del primer día del mes
            fecha_mes = cotizacion.fecha.replace(day=1)
            tc_por_mes[fecha_mes].append(cotizacion.venta)

        # Calcular promedios
        resultado = {}
        for fecha_mes, ventas in tc_por_mes.items():
            promedio = sum(ventas) / len(ventas)
            # Convertir date a datetime para que coincida con las claves de saldos
            if isinstance(fecha_mes, date) and not isinstance(fecha_mes, datetime):
                fecha_mes = datetime.combine(fecha_mes, datetime.min.time())
            resultado[fecha_mes] = promedio

        print(f"  TC promedio calculado para {len(resultado)} meses")
        return resultado
