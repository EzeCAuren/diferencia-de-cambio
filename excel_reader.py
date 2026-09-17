"""
Lector de datos desde Excel
"""

import xlwings as xw
import pandas as pd
from datetime import datetime

from config import (
    HOJA_MAYORES,
    HOJA_ANALISIS,
    HOJA_CONFIG_MONEDAS,
    COLUMNA_CUENTA,
    FILA_INICIO_CUENTAS,
    MARCADOR_INICIO_CUENTAS,
    FILAS_A_IGNORAR,
    PALABRAS_CLAVE_MAYORES,
    MONEDAS_BCU,
    MONEDA_BASE_POR_DEFECTO
)


class ExcelReader:
    """Lee datos desde el libro de Excel activo"""

    def __init__(self, wb=None):
        """
        Inicializa el lector.
        
        Si no se pasa un libro, usa el libro activo.
        """
        if wb is None:
            app = xw.apps.active
            if app is None:
                raise Exception("No hay ninguna aplicación de Excel abierta")
            self.wb = app.books.active
        else:
            self.wb = wb

    def leer_cuentas_analisis(self):
        """
        Lee los códigos de cuenta de la hoja de Análisis.
        Detecta automáticamente dónde empiezan las cuentas a analizar.
        
        Returns:
            list: Lista de códigos de cuenta (strings)
            
        Raises:
            Exception: Si no se encuentra la hoja o no hay cuentas
        """
        try:
            hoja = self.wb.sheets[HOJA_ANALISIS]
        except Exception:
            raise Exception(f"No se encontró la hoja '{HOJA_ANALISIS}'")

        # Buscar la fila donde empiezan las cuentas a analizar
        # IMPORTANTE: Buscar "Cuentas" (plural), NO "Cuenta" (singular)
        # Porque "Cuenta" es el encabezado de la tabla de resultados
        
        fila_inicio = None
        for fila in range(1, 50):  # Buscar en las primeras 50 filas
            try:
                valor = hoja[f"{COLUMNA_CUENTA}{fila}"].value
                if valor and str(valor).strip().upper() in MARCADOR_INICIO_CUENTAS:
                    fila_inicio = fila + 1  # La siguiente fila tiene los datos
                    break
            except Exception:
                continue
        
        # Si no encuentra, usar la constante por defecto
        if fila_inicio is None:
            fila_inicio = FILA_INICIO_CUENTAS
            print(f"  Usando fila por defecto: {fila_inicio}")
        else:
            print(f"  Cuentas a analizar comienzan en fila: {fila_inicio}")

        cuentas = []
        fila = fila_inicio

        while True:
            try:
                celda_cuenta = hoja[f"{COLUMNA_CUENTA}{fila}"]
                valor = celda_cuenta.value

                if valor is None or str(valor).strip() == "":
                    break

                cuenta_str = str(valor).strip()
                
                # Ignorar filas de totales y otras filas especiales
                if cuenta_str.upper() in FILAS_A_IGNORAR:
                    fila += 1
                    continue

                cuentas.append(cuenta_str)
                fila += 1

            except Exception:
                break

        if not cuentas:
            raise Exception("No hay cuentas para analizar en la hoja de Análisis")

        print(f"Se encontraron {len(cuentas)} cuentas en la hoja de Análisis")
        return cuentas

    def leer_mayores(self):
        """
        Lee la hoja de Mayores y retorna un DataFrame.
        Detecta automáticamente las columnas sin depender del formato.
        
        Returns:
            pd.DataFrame: DataFrame con los mayores
            
        Raises:
            Exception: Si no se encuentra la hoja o no hay datos
        """
        try:
            hoja = self.wb.sheets[HOJA_MAYORES]
        except Exception:
            raise Exception(f"No se encontró la hoja '{HOJA_MAYORES}'")

        # Buscar la fila de encabezados buscando palabras clave
        
        fila_encabezados = None
        mapping_columnas = {}  # {nombre_estandar: indice_columna}
        
        for fila in range(1, 30):  # Buscar en las primeras 30 filas
            try:
                # Leer toda la fila
                valores_fila = []
                for col in range(1, 30):
                    try:
                        col_letter = self._get_column_letter(col)
                        valor = hoja[f"{col_letter}{fila}"].value
                        valores_fila.append(str(valor).strip().upper() if valor else "")
                    except Exception:
                        valores_fila.append("")
                
                # Buscar si esta fila contiene encabezados
                for idx, valor in enumerate(valores_fila):
                    for nombre_col, detector in PALABRAS_CLAVE_MAYORES.items():
                        if callable(detector):
                            # Función lambda para匹配 complejo (detección compleja)
                            if detector(valor):
                                mapping_columnas[nombre_col] = idx
                                if nombre_col in ("Cuenta", "Fecha"):
                                    fila_encabezados = fila
                        elif isinstance(detector, list):
                            # Lista de palabras clave
                            if any(palabra in valor for palabra in detector):
                                mapping_columnas[nombre_col] = idx
                                if nombre_col in ("Cuenta", "Fecha"):
                                    fila_encabezados = fila
                
                # Si encontramos al menos cuenta y fecha, es válido
                if "Cuenta" in mapping_columnas and "Fecha" in mapping_columnas:
                    break
                else:
                    mapping_columnas = {}
                    fila_encabezados = None
                    
            except Exception:
                continue

        if fila_encabezados is None:
            raise Exception("No se pudieron detectar los encabezados en la hoja de Mayores")

        print(f"  Encabezados detectados en fila {fila_encabezados}")
        print(f"  Columnas encontradas: {list(mapping_columnas.keys())}")

        # Obtener última fila con datos
        ultima_fila = hoja.used_range.last_cell.row
        print(f"  Última fila detectada: {ultima_fila}")

        # Leer datos usando range completo (más rápido)
        rango_datos = hoja.range(
            f"{self._get_column_letter(mapping_columnas['Cuenta'] + 1)}{fila_encabezados + 1}:{self._get_column_letter(max(mapping_columnas.values()) + 1)}{ultima_fila}"
        )
        
        # Obtener valores de una vez
        valores = rango_datos.value
        
        if valores is None:
            raise Exception("No se encontraron datos en la hoja de Mayores")
        
        # Procesar valores
        datos = []
        for fila_vals in valores:
            # Verificar si la fila tiene datos
            if fila_vals is None or all(v is None for v in fila_vals):
                continue
            
            fila_datos = {}
            for nombre_col, idx_col in mapping_columnas.items():
                # Ajustar índice porque el rango empieza desde la columna de cuenta
                idx_rel = idx_col - mapping_columnas['Cuenta']
                if 0 <= idx_rel < len(fila_vals):
                    fila_datos[nombre_col] = fila_vals[idx_rel]
                else:
                    fila_datos[nombre_col] = None
            
            # Solo agregar si tiene cuenta
            if fila_datos.get("Cuenta") is not None and str(fila_datos["Cuenta"]).strip() != "":
                datos.append(fila_datos)

        if not datos:
            raise Exception("No se encontraron datos en la hoja de Mayores")

        # Crear DataFrame
        df = pd.DataFrame(datos)

        # Asegurar que la columna de cuenta sea string
        if "Cuenta" in df.columns:
            df["Cuenta"] = df["Cuenta"].astype(str).str.strip()

        # Convertir fechas
        if "Fecha" in df.columns:
            df["Fecha"] = pd.to_datetime(df["Fecha"], errors='coerce')

        # Asegurar que las columnas numéricas sean numéricas
        for col in ["Debe $", "Haber $", "Saldo $", "Debe USD", "Haber USD", "Saldo USD"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        print(f"Se leyeron {len(df)} movimientos de la hoja de Mayores")
        return df

    def _get_column_letter(self, col_num):
        """
        Convierte un número de columna a letra (1=A, 2=B, ..., 27=AA, etc.)
        """
        result = ""
        while col_num > 0:
            col_num, remainder = divmod(col_num - 1, 26)
            result = chr(65 + remainder) + result
        return result

    def leer_configuracion_monedas(self):
        """
        Lee la configuración de monedas desde Excel.
        
        Si no existe la hoja, retorna la configuración por defecto (USD).
        
        Returns:
            list: Lista de diccionarios con configuración de monedas
        """
        try:
            hoja = self.wb.sheets[HOJA_CONFIG_MONEDAS]
        except Exception:
            # Si no existe la hoja, usar configuración por defecto
            print("Usando configuración por defecto: USD")
            return [{
                "moneda": "USD",
                "codigo_bcu": MONEDAS_BCU["USD"],
                "simbolo": "U$S",
                "moneda_base": True
            }]

        config = []
        fila = 2  # Empezar después del encabezado

        while True:
            try:
                moneda = hoja[f"A{fila}"].value
                if moneda is None or str(moneda).strip() == "":
                    break

                codigo_bcu = hoja[f"B{fila}"].value
                simbolo = hoja[f"C{fila}"].value
                moneda_base = hoja[f"D{fila}"].value

                # Normalizar tildes para comparar
                moneda_base_upper = str(moneda_base).strip().upper() if moneda_base else ""
                moneda_base_normalizado = (
                    moneda_base_upper
                    .replace("Í", "I").replace("Ó", "O")
                    .replace("Ú", "U").replace("Á", "A")
                    .replace("É", "E")
                )
                
                config.append({
                    "moneda": str(moneda).strip(),
                    "codigo_bcu": int(codigo_bcu) if codigo_bcu else MONEDAS_BCU.get(str(moneda).strip(), 2225),
                    "simbolo": str(simbolo).strip() if simbolo else str(moneda).strip(),
                    "moneda_base": moneda_base_normalizado == "SI"
                })

                fila += 1

            except Exception:
                break

        if not config:
            # Si no se pudo leer, usar USD por defecto
            return [{
                "moneda": "USD",
                "codigo_bcu": MONEDAS_BCU["USD"],
                "simbolo": "U$S",
                "moneda_base": True
            }]

        print(f"Se cargaron {len(config)} monedas desde la configuración")
        return config

    def obtener_info_cliente(self):
        """
        Obtiene información del cliente desde la hoja de Análisis.
        
        Returns:
            dict: Información del cliente
        """
        try:
            hoja = self.wb.sheets[HOJA_ANALISIS]
            
            cliente = hoja["B2"].value or ""
            fecha_auditoria = hoja["B4"].value or ""
            
            return {
                "cliente": str(cliente).strip(),
                "fecha_auditoria": str(fecha_auditoria).strip()
            }
            
        except Exception:
            return {
                "cliente": "",
                "fecha_auditoria": ""
            }

    def obtener_saldo_empresa_usd(self):
        """
        Obtiene el saldo de la empresa en USD desde la hoja de Análisis.
        
        Busca en la celda B3 (debajo del nombre del cliente, arriba de fecha).
        Si no encuentra o está vacío, retorna 0.
        
        Returns:
            float: Saldo de la empresa en USD
        """
        try:
            hoja = self.wb.sheets[HOJA_ANALISIS]
            valor = hoja["B3"].value
            
            if valor is None or str(valor).strip() == "":
                return 0.0
            
            return float(valor)
            
        except Exception:
            return 0.0

    def existe_hoja(self, nombre_hoja):
        """
        Verifica si existe una hoja en el libro.
        
        Args:
            nombre_hoja: Nombre de la hoja a buscar
            
        Returns:
            bool: True si existe, False si no
        """
        try:
            self.wb.sheets[nombre_hoja]
            return True
        except Exception:
            return False
