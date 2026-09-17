"""
Configuración del Procedimiento 1701 - Diferencia de Cambio
"""

# ==========================================
# NOMBRES DE HOJAS
# ==========================================

HOJA_MAYORES = "Mayores"
HOJA_ANALISIS = "1701.1 - Análisis"
HOJA_TABLA_DINAMICA = "Tabla Dinamica Valores"
HOJA_CONFIG_MONEDAS = "Config Monedas"

# ==========================================
# COLUMNAS DE LA HOJA ANÁLISIS
# ==========================================

COLUMNA_CUENTA = "C"           # Código de cuenta
COLUMNA_DETALLE = "D"          # Nombre/detalle de cuenta
COLUMNA_SALDO_CIERRE = "E"     # Saldo cierre anterior
COLUMNAS_MENSUALES = ["F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q"]
COLUMNA_TOTAL = "R"

# ==========================================
# DETECCIÓN AUTOMÁTICA DE FILAS
# ==========================================

# Palabras clave para detectar dónde empiezan las cuentas (plural = tabla de análisis)
MARCADOR_INICIO_CUENTAS = ["CUENTAS"]

# Fila de fallback si no se detecta automáticamente
FILA_INICIO_CUENTAS = 9

# Fila de encabezado de la tabla de resultados (singular = tabla resumen)
MARCADOR_TABLA_RESULTADOS = ["CUENTA"]

# Filas que se ignoran al leer cuentas
FILAS_A_IGNORAR = ["TOTAL", "TOTAL ACTIVO", "TOTAL PASIVO"]

# Mapeo de etiquetas de fila a claves internas
# Cada entrada: (clave_interna, función_de_detección)
ETIQUETAS_FILAS = {
    "TOTAL_ACTIVO": lambda t: t == "TOTAL ACTIVO",
    "TOTAL_PASIVO": lambda t: t == "TOTAL PASIVO",
    "POSICION_NETA_UY": lambda t: t.startswith("POSICION NETA") and "UY" in t,
    "POSICION_NETA_USD": lambda t: t.startswith("POSICION NETA") and "USD" in t,
    "POSICION_NETA_MC_PROM": lambda t: t.startswith("POSICION NETA") and "MC" in t,
    "TC": lambda t: t.startswith("TC"),
    "DIFERENCIA": lambda t: "DIFERENCIA" in t and "CAMBIO" in t,
}

# ==========================================
# COLUMNAS DE LA HOJA MAYORES
# ==========================================

COLUMNA_MAYOR_CUENTA = "Cuenta"
COLUMNA_MAYOR_FECHA = "Fecha"
COLUMNA_MAYOR_CONCEPTO = "Concepto"
COLUMNA_MAYOR_DEBE_UY = "Debe $"
COLUMNA_MAYOR_HABER_UY = "Haber $"
COLUMNA_MAYOR_SALDO_UY = "Saldo $"
COLUMNA_MAYOR_DEBE_USD = "Debe USD"
COLUMNA_MAYOR_HABER_USD = "Haber USD"
COLUMNA_MAYOR_NETO_USD = "Neto USD"
COLUMNA_MAYOR_SALDO_USD = "Saldo USD"

# Palabras clave para detectar columnas en Mayores
PALABRAS_CLAVE_MAYORES = {
    "Cuenta": ["CUENTA", "CTA", "CODIGO", "COD", "NRO CUENTA"],
    "Fecha": ["FECHA", "DATE", "FCH"],
    "Debe $": ["DEBE", "DEBITO", "DEB"],
    "Haber $": ["HABER", "CREDITO", "HAB"],
    "Saldo $": lambda v: "SALDO" in v and "$" in v and "USD" not in v,
    "Debe USD": lambda v: "DEBE" in v and "USD" in v,
    "Haber USD": lambda v: "HABER" in v and "USD" in v,
    "Saldo USD": lambda v: "SALDO" in v and "USD" in v,
    "Concepto": ["CONCEPTO", "DETALLE", "DESCRIPCION"],
}

# ==========================================
# CONFIGURACIÓN DE MONEDAS
# ==========================================

# Monedas disponibles en el BCU
MONEDAS_BCU = {
    "USD": 2225,    # Dólar Americano
    "EUR": 978,     # Euro
    "BRL": 986,     # Real Brasileño
    "GBP": 826,     # Libra Esterlina
    "CHF": 756,     # Franco Suizo
}

# Moneda base por defecto
MONEDA_BASE_POR_DEFECTO = "USD"

# ==========================================
# CONFIGURACIÓN DE ANÁLISIS
# ==========================================

# Nombres de meses para tabla dinámica
MESES = ["Jul", "Ago", "Sep", "Oct", "Nov", "Dic", "Ene", "Feb", "Mar", "Abr", "May", "Jun"]

# ==========================================
# MENSAJES
# ==========================================

MENSAJE_NO_CUENTAS = "No hay cuentas para analizar en la hoja de Análisis"
MENSAJE_NO_MAYORES = "No se encontró la hoja de Mayores"
MENSAJE_PROCESO_EXITOSO = "Proceso finalizado exitosamente"
MENSAJE_ERROR_LECTURA = "Error al leer datos del Excel"
