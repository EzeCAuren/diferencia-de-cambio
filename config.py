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
# FILAS DE LA HOJA ANÁLISIS
# ==========================================

FILA_INICIO_CUENTAS = 9

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

# Columnas de la tabla dinámica
MESES = ["Jul", "Ago", "Sep", "Oct", "Nov", "Dic", "Ene", "Feb", "Mar", "Abr", "May", "Jun"]

# ==========================================
# MENSAJES
# ==========================================

MENSAJE_NO_CUENTAS = "No hay cuentas para analizar en la hoja de Análisis"
MENSAJE_NO_MAYORES = "No se encontró la hoja de Mayores"
MENSAJE_PROCESO_EXITOSO = "Proceso finalizado exitosamente"
MENSAJE_ERROR_LECTURA = "Error al leer datos del Excel"
