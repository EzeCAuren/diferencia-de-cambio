"""
Cliente SOAP para cotizaciones del BCU (Banco Central del Uruguay).
Obtiene tipos de cambio oficiales via API publica.
"""

from dataclasses import dataclass
from datetime import date, datetime
import xml.etree.ElementTree as ET

import requests


# Endpoint SOAP del BCU
SOAP_ENDPOINT = (
    "https://cotizaciones.bcu.gub.uy/"
    "wscotizaciones/servlet/"
    "awsbcucotizaciones"
)


@dataclass(slots=True)
class ExchangeRate:
    """Cotizacion diaria de una moneda."""
    fecha: date
    moneda_id: int
    compra: float
    venta: float


@dataclass(slots=True)
class BCUResponse:
    """Respuesta del BCU con lista de cotizaciones."""
    success: bool
    rates: list[ExchangeRate]
    message: str = ""


def _build_soap_request(currency_code: int, date_from: str, date_to: str) -> str:
    """Construye el XML SOAP para la consulta de cotizaciones."""
    return f"""<?xml version="1.0" encoding="utf-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:cot="Cotiza">
<soapenv:Header/>
<soapenv:Body>
<cot:wsbcucotizaciones.Execute>
<cot:Entrada>
<cot:Moneda>
<cot:item>{currency_code}</cot:item>
</cot:Moneda>
<cot:FechaDesde>{date_from}</cot:FechaDesde>
<cot:FechaHasta>{date_to}</cot:FechaHasta>
<cot:Grupo>0</cot:Grupo>
</cot:Entrada>
</cot:wsbcucotizaciones.Execute>
</soapenv:Body>
</soapenv:Envelope>"""


def _parse_xml_rates(xml_text: str, moneda_id: int) -> list[ExchangeRate]:
    """Parsea la respuesta XML del BCU y extrae las cotizaciones."""
    rates = []
    root = ET.fromstring(xml_text)

    for item in root.iter():
        if not item.tag.endswith("datoscotizaciones.dato"):
            continue

        fecha = None
        compra = None
        venta = None

        for child in item:
            tag = child.tag.split("}")[-1]

            if tag == "Fecha":
                if not child.text:
                    continue
                fecha = datetime.strptime(child.text, "%Y-%m-%d").date()
            elif tag == "TCC":
                compra = float(child.text)
            elif tag == "TCV":
                venta = float(child.text)

        if fecha is not None and compra is not None and venta is not None:
            rates.append(ExchangeRate(
                fecha=fecha,
                moneda_id=moneda_id,
                compra=compra,
                venta=venta
            ))

    return rates


class BCUClient:
    """Cliente para obtener cotizaciones del BCU via SOAP."""

    def __init__(self, timeout_seconds: int = 10):
        self.timeout_seconds = timeout_seconds

    def get_exchange_rates(
        self,
        currency_code: int,
        date_from: date,
        date_to: date
    ) -> BCUResponse:
        """
        Obtiene cotizaciones del BCU para un rango de fechas.

        Args:
            currency_code: Codigo de moneda (2225=USD, 978=EUR, etc.)
            date_from: Fecha desde
            date_to: Fecha hasta

        Returns:
            BCUResponse con las cotizaciones o error
        """
        body = _build_soap_request(
            currency_code=currency_code,
            date_from=date_from.isoformat(),
            date_to=date_to.isoformat()
        )

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "Cotizaaction/AWSBCUCOTIZACIONES.Execute"
        }

        try:
            response = requests.post(
                SOAP_ENDPOINT,
                headers=headers,
                data=body.encode("utf-8"),
                timeout=self.timeout_seconds
            )
            response.raise_for_status()

            rates = _parse_xml_rates(response.text, moneda_id=currency_code)

            return BCUResponse(
                success=True,
                rates=rates,
                message=f"{len(rates)} cotizaciones descargadas"
            )

        except Exception as ex:
            return BCUResponse(
                success=False,
                rates=[],
                message=str(ex)
            )
