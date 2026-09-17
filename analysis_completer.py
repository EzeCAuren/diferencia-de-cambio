"""
Completador de Hoja de Análisis
"""

from config import (
    HOJA_ANALISIS,
    COLUMNA_CUENTA,
    COLUMNAS_MENSUALES,
    COLUMNA_TOTAL,
    FILA_INICIO_CUENTAS,
    MARCADOR_INICIO_CUENTAS,
    FILAS_A_IGNORAR,
    ETIQUETAS_FILAS
)


class AnalysisCompleter:
    """Completa la hoja de Análisis con los datos calculados"""

    def __init__(self, wb):
        """
        Inicializa el completador.
        
        Args:
            wb: Libro de Excel
        """
        self.wb = wb
        try:
            self.hoja = wb.sheets[HOJA_ANALISIS]
        except Exception:
            raise Exception(f"No se encontró la hoja '{HOJA_ANALISIS}'")

    def _detectar_fila_inicio_cuentas(self):
        """
        Detecta la fila donde empiezan las cuentas a analizar.
        Busca "Cuentas" (plural) en la columna C.
        
        Returns:
            int: Número de fila donde empiezan los datos
        """
        
        for fila in range(1, 50):
            try:
                valor = self.hoja[f"{COLUMNA_CUENTA}{fila}"].value
                if valor and str(valor).strip().upper() in MARCADOR_INICIO_CUENTAS:
                    return fila + 1  # La siguiente fila tiene los datos
            except Exception:
                continue
        
        # Si no encuentra, usar la constante por defecto
        return FILA_INICIO_CUENTAS

    def completar_importes_mensuales(self, saldos_por_cuenta, meses_disponibles):
        """
        Completa las columnas F-Q con los saldos acumulados mensuales.
        
        Args:
            saldos_por_cuenta: {cuenta: {fecha: saldo}}
            meses_disponibles: Lista de fechas (primer día de cada mes)
        """
        fila = self._detectar_fila_inicio_cuentas()
        print(f"  Completando importes desde fila {fila}")
        
        while True:
            try:
                celda_cuenta = self.hoja[f"{COLUMNA_CUENTA}{fila}"]
                valor_cuenta = celda_cuenta.value
                
                if valor_cuenta is None or str(valor_cuenta).strip() == "":
                    break
                
                cuenta_str = str(valor_cuenta).strip()
                
                # Ignorar filas de totales
                if cuenta_str.upper() in FILAS_A_IGNORAR:
                    fila += 1
                    continue
                
                # Obtener saldos para esta cuenta
                saldos_cuenta = saldos_por_cuenta.get(cuenta_str, {})
                
                # Completar cada columna mensual
                for i, mes_fecha in enumerate(meses_disponibles):
                    if i < len(COLUMNAS_MENSUALES):
                        columna = COLUMNAS_MENSUALES[i]
                        saldo = saldos_cuenta.get(mes_fecha, 0)
                        self.hoja[f"{columna}{fila}"].value = saldo
                
                fila += 1
                
            except Exception as e:
                print(f"Error en fila {fila}: {e}")
                break
        
        print("Importes mensuales completados")

    def completar_tc_promedio(self, tc_por_mes, meses_disponibles):
        """
        Completa la fila de TC promedio mensual.
        
        Args:
            tc_por_mes: {fecha: tc_promedio}
            meses_disponibles: Lista de fechas (primer día de cada mes)
        """
        filas = self._detectar_filas_totales()
        fila_tc = filas.get("TC")
        
        if not fila_tc:
            print("  No se encontró la fila de TC")
            return
        
        print(f"  TC en fila {fila_tc}")
        
        for i, mes_fecha in enumerate(meses_disponibles):
            if i < len(COLUMNAS_MENSUALES):
                columna = COLUMNAS_MENSUALES[i]
                tc = tc_por_mes.get(mes_fecha, 0)
                self.hoja[f"{columna}{fila_tc}"].value = tc
        
        print("TC promedio mensual completado")

    def completar_total_por_fila(self, fila_inicio, fila_fin):
        """
        Completa la columna de Total para un rango de filas.
        
        Args:
            fila_inicio: Primera fila de datos
            fila_fin: Última fila de datos
        """
        for fila in range(fila_inicio, fila_fin + 1):
            try:
                # Sumar las columnas mensuales
                suma = 0
                for columna in COLUMNAS_MENSUALES:
                    valor = self.hoja[f"{columna}{fila}"].value
                    if valor is not None:
                        try:
                            suma += float(valor)
                        except (ValueError, TypeError):
                            pass
                
                self.hoja[f"{COLUMNA_TOTAL}{fila}"].value = suma
                
            except Exception as e:
                print(f"Error calculando total fila {fila}: {e}")

    def _detectar_filas_totales(self):
        """
        Detecta las filas de TOTAL ACTIVO, TOTAL PASIVO, etc.
        Usa las funciones de detección definidas en ETIQUETAS_FILAS.
        
        Returns:
            dict: {tipo_fila: numero_fila}
        """
        filas = {}
        
        for fila in range(1, 50):
            try:
                valor = self.hoja[f"{COLUMNA_CUENTA}{fila}"].value
                if valor:
                    valor_upper = str(valor).strip().upper()
                    # Quitar tildes para comparar
                    valor_normalizado = valor_upper.replace("Ó", "O").replace("Ú", "U")
                    
                    # Usar las funciones de detección de config
                    for clave, detector in ETIQUETAS_FILAS.items():
                        if detector(valor_normalizado):
                            filas[clave] = fila
                            break
            except Exception:
                continue
        
        return filas

    def completar_totales_seccion(self):
        """
        Completa los totales de activos, pasivos y posición neta.
        """
        filas = self._detectar_filas_totales()
        
        fila_inicio_cuentas = self._detectar_fila_inicio_cuentas()
        fila_total_activo = filas.get("TOTAL_ACTIVO")
        fila_total_pasivo = filas.get("TOTAL_PASIVO")
        
        if not fila_total_activo or not fila_total_pasivo:
            print("  No se encontraron filas de totales")
            return
        
        print(f"  Total Activo en fila {fila_total_activo}, Total Pasivo en fila {fila_total_pasivo}")
        
        # Total Activo (desde fila inicio hasta fila total activo - 1)
        self.completar_total_por_fila(fila_inicio_cuentas, fila_total_activo - 1)
        
        # Total Pasivo (desde fila total activo + 1 hasta fila total pasivo - 1)
        self.completar_total_por_fila(fila_total_activo + 1, fila_total_pasivo - 1)
        
        print("Totales de sección completados")

    def calcular_posicion_neta_uy(self):
        """
        Calcula la posición neta en UY$ (Activo - Pasivo).
        """
        try:
            filas = self._detectar_filas_totales()
            fila_total_activo = filas.get("TOTAL_ACTIVO")
            fila_total_pasivo = filas.get("TOTAL_PASIVO")
            fila_posicion = filas.get("POSICION_NETA_UY")
            
            if not fila_total_activo or not fila_total_pasivo or not fila_posicion:
                print("  No se encontraron las filas requeridas para posición neta")
                return
            
            total_activo = self.hoja[f"{COLUMNA_TOTAL}{fila_total_activo}"].value or 0
            total_pasivo = self.hoja[f"{COLUMNA_TOTAL}{fila_total_pasivo}"].value or 0
            
            posicion_neta = float(total_activo) - float(total_pasivo)
            
            # Completar para cada mes
            for columna in COLUMNAS_MENSUALES:
                activo_mes = self.hoja[f"{columna}{fila_total_activo}"].value or 0
                pasivo_mes = self.hoja[f"{columna}{fila_total_pasivo}"].value or 0
                posicion_mes = float(activo_mes) - float(pasivo_mes)
                self.hoja[f"{columna}{fila_posicion}"].value = posicion_mes
            
            # Total
            self.hoja[f"{COLUMNA_TOTAL}{fila_posicion}"].value = posicion_neta
            
            print(f"Posición neta UY$ calculada: {posicion_neta}")
            
        except Exception as e:
            print(f"Error calculando posición neta UY$: {e}")

    def calcular_posicion_neta_usd(self):
        """
        Calcula la posición neta en USD (Posición UY / TC promedio).
        """
        try:
            filas = self._detectar_filas_totales()
            fila_posicion_uy = filas.get("POSICION_NETA_UY")
            fila_tc = filas.get("TC")
            fila_posicion_usd = filas.get("POSICION_NETA_USD")
            
            if not fila_posicion_uy or not fila_tc or not fila_posicion_usd:
                print("  No se encontraron las filas requeridas para posición USD")
                return
            
            for columna in COLUMNAS_MENSUALES:
                posicion_uy = self.hoja[f"{columna}{fila_posicion_uy}"].value or 0
                tc = self.hoja[f"{columna}{fila_tc}"].value or 0
                
                if tc and tc != 0:
                    posicion_usd = float(posicion_uy) / float(tc)
                else:
                    posicion_usd = 0
                
                self.hoja[f"{columna}{fila_posicion_usd}"].value = posicion_usd
            
            print("Posición neta USD calculada")
            
        except Exception as e:
            print(f"Error calculando posición USD: {e}")

    def calcular_posicion_neta_mc_prom(self):
        """
        Calcula la posición neta acumulada en moneda base.
        """
        try:
            filas = self._detectar_filas_totales()
            fila_posicion_usd = filas.get("POSICION_NETA_USD")
            fila_posicion_mc = filas.get("POSICION_NETA_MC_PROM")
            
            if not fila_posicion_usd or not fila_posicion_mc:
                print("  No se encontraron las filas requeridas para posición MC Prom")
                return
            
            acumulado = 0
            
            for columna in COLUMNAS_MENSUALES:
                posicion_usd = self.hoja[f"{columna}{fila_posicion_usd}"].value or 0
                acumulado += float(posicion_usd)
                self.hoja[f"{columna}{fila_posicion_mc}"].value = acumulado
            
            print("Posición neta acumulada calculada")
            
        except Exception as e:
            print(f"Error calculando posición neta acumulada: {e}")

    def calcular_diferencia_cambio(self, saldo_empresa_usd):
        """
        Calcula la diferencia de cambio (Posición calculada - Saldo empresa).
        
        Args:
            saldo_empresa_usd: Saldo registrado por la empresa en USD
        """
        try:
            filas = self._detectar_filas_totales()
            fila_posicion_usd = filas.get("POSICION_NETA_USD")
            fila_diferencia = filas.get("DIFERENCIA")
            
            if not fila_posicion_usd or not fila_diferencia:
                print("  No se encontraron las filas requeridas para diferencia")
                return
            
            for columna in COLUMNAS_MENSUALES:
                posicion_usd = self.hoja[f"{columna}{fila_posicion_usd}"].value or 0
                diferencia = float(posicion_usd) - float(saldo_empresa_usd)
                self.hoja[f"{columna}{fila_diferencia}"].value = diferencia
            
            print("Diferencia de cambio calculada")
            
        except Exception as e:
            print(f"Error calculando diferencia de cambio: {e}")

    def completar_todos_los_calculos(self, saldos_por_cuenta, tc_por_mes, meses_disponibles, saldo_empresa_usd=0):
        """
        Ejecuta todos los cálculos en orden.
        
        Args:
            saldos_por_cuenta: {cuenta: {fecha: saldo}}
            tc_por_mes: {fecha: tc_promedio}
            meses_disponibles: Lista de fechas
            saldo_empresa_usd: Saldo registrado por la empresa
        """
        print("Iniciando completado de análisis...")
        
        # 1. Completar importes mensuales
        self.completar_importes_mensuales(saldos_por_cuenta, meses_disponibles)
        
        # 2. Completar TC promedio
        self.completar_tc_promedio(tc_por_mes, meses_disponibles)
        
        # 3. Completar totales
        self.completar_totales_seccion()
        
        # 4. Calcular posición neta UY$
        self.calcular_posicion_neta_uy()
        
        # 5. Calcular posición neta USD
        self.calcular_posicion_neta_usd()
        
        # 6. Calcular posición neta acumulada
        self.calcular_posicion_neta_mc_prom()
        
        # 7. Calcular diferencia de cambio
        self.calcular_diferencia_cambio(saldo_empresa_usd)
        
        print("Análisis completado exitosamente")
