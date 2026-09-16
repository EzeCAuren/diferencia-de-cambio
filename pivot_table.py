"""
Creador de Tabla Dinámica
"""

from config import (
    HOJA_TABLA_DINAMICA,
    COLUMNAS_MENSUALES,
    COLUMNA_TOTAL,
    MESES
)


class PivotTableCreator:
    """Crea la tabla dinámica en una nueva pestaña"""

    def __init__(self, wb):
        """
        Inicializa el creador.
        
        Args:
            wb: Libro de Excel
        """
        self.wb = wb

    def crear_tabla_dinamica(self, saldos_por_cuenta, tc_por_mes, meses_disponibles, cliente_info=None):
        """
        Crea una nueva pestaña con la tabla dinámica.
        
        Args:
            saldos_por_cuenta: {cuenta: {fecha: saldo}}
            tc_por_mes: {fecha: tc_promedio}
            meses_disponibles: Lista de fechas
            cliente_info: Información del cliente (opcional)
        """
        # Eliminar hoja existente si existe
        try:
            self.wb.sheets[HOJA_TABLA_DINAMICA].delete()
        except Exception:
            pass

        # Crear nueva hoja
        hoja = self.wb.sheets.add(HOJA_TABLA_DINAMICA)

        # Escribir encabezado
        if cliente_info:
            hoja["A1"].value = cliente_info.get("cliente", "")
            hoja["A2"].value = "Tabla Dinámica Valores"
        else:
            hoja["A1"].value = "Tabla Dinámica Valores"

        # Escribir encabezados de columnas
        fila_encabezado = 4
        hoja[f"A{fila_encabezado}"].value = "Nombre Cuentas"
        
        for i, mes_fecha in enumerate(meses_disponibles):
            columna = chr(66 + i) if i < 26 else f"{chr(64 + i // 26)}{chr(66 + i % 26)}"
            mes_nombre = MESES[i] if i < len(MESES) else mes_fecha.strftime("%b")
            hoja[f"{columna}{fila_encabezado}"].value = mes_nombre
        
        # Columna Total
        columna_total = chr(66 + len(meses_disponibles)) if len(meses_disponibles) < 26 else f"{chr(64 + (len(meses_disponibles) + 1) // 26)}{chr(66 + (len(meses_disponibles) + 1) % 26)}"
        hoja[f"{columna_total}{fila_encabezado}"].value = "Total"

        # Escribir datos por cuenta
        fila_datos = fila_encabezado + 1
        totales_por_mes = {i: 0 for i in range(len(meses_disponibles))}
        
        for cuenta, meses in saldos_por_cuenta.items():
            hoja[f"A{fila_datos}"].value = cuenta
            
            total_cuenta = 0
            for i, mes_fecha in enumerate(meses_disponibles):
                columna = chr(66 + i) if i < 26 else f"{chr(64 + i // 26)}{chr(66 + i % 26)}"
                saldo = meses.get(mes_fecha, 0)
                hoja[f"{columna}{fila_datos}"].value = saldo
                total_cuenta += saldo
                totales_por_mes[i] += saldo
            
            # Total de la cuenta
            hoja[f"{columna_total}{fila_datos}"].value = total_cuenta
            
            fila_datos += 1

        # Fila de totales
        fila_totales = fila_datos
        hoja[f"A{fila_totales}"].value = "TOTAL"
        
        for i in range(len(meses_disponibles)):
            columna = chr(66 + i) if i < 26 else f"{chr(64 + i // 26)}{chr(66 + i % 26)}"
            hoja[f"{columna}{fila_totales}"].value = totales_por_mes[i]
        
        # Total general
        total_general = sum(totales_por_mes.values())
        hoja[f"{columna_total}{fila_totales}"].value = total_general

        # Fila de TC promedio
        fila_tc = fila_totales + 2
        hoja[f"A{fila_tc}"].value = "TC Promedio"
        
        for i, mes_fecha in enumerate(meses_disponibles):
            columna = chr(66 + i) if i < 26 else f"{chr(64 + i // 26)}{chr(66 + i % 26)}"
            tc = tc_por_mes.get(mes_fecha, 0)
            hoja[f"{columna}{fila_tc}"].value = tc

        # Fila de posición neta: Activo (cuentas 1xxx) - Pasivo (cuentas 2xxx)
        fila_posicion = fila_tc + 1
        hoja[f"A{fila_posicion}"].value = "Posición Neta"
        
        for i, mes_fecha in enumerate(meses_disponibles):
            columna = chr(66 + i) if i < 26 else f"{chr(64 + i // 26)}{chr(66 + i % 26)}"
            
            # Calcular activo y pasivo por separado
            activo_mes = 0
            pasivo_mes = 0
            
            for cuenta, meses in saldos_por_cuenta.items():
                saldo = meses.get(mes_fecha, 0)
                # Determinar si es activo o pasivo por primer dígito
                cuenta_str = str(cuenta).split('.')[0]  # Quitar decimales si tiene
                if cuenta_str.startswith('1'):
                    activo_mes += saldo
                elif cuenta_str.startswith('2'):
                    pasivo_mes += saldo
            
            posicion_neta = activo_mes - pasivo_mes
            hoja[f"{columna}{fila_posicion}"].value = posicion_neta

        print(f"Tabla dinámica creada en hoja '{HOJA_TABLA_DINAMICA}'")
        return hoja

    def formatear_tabla(self, hoja, num_meses):
        """
        Aplica formato básico a la tabla dinámica.
        
        Args:
            hoja: Hoja de Excel
            num_meses: Número de meses
        """
        try:
            # Formato de encabezados
            ultima_columna = chr(65 + num_meses + 1) if num_meses + 1 < 26 else f"{chr(64 + (num_meses + 2) // 26)}{chr(66 + (num_meses + 1) % 26)}"
            
            # Negrita en encabezados
            hoja[f"A4:{ultima_columna}4"].font.bold = True
            
            # Formato numérico para datos
            for fila in range(5, 50):  # Aproximadamente
                for i in range(num_meses + 1):
                    columna = chr(66 + i) if i < 26 else f"{chr(64 + i // 26)}{chr(66 + i % 26)}"
                    celda = hoja[f"{columna}{fila}"]
                    
                    if celda.value is not None:
                        try:
                            valor = float(celda.value)
                            if abs(valor) > 1000:
                                celda.number_format = '#,##0.00'
                        except (ValueError, TypeError):
                            pass

            print("Formato aplicado a tabla dinámica")
            
        except Exception as e:
            print(f"Error aplicando formato: {e}")
