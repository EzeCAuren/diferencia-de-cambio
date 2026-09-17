"""Tests para bcu_client.py"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date
from bcu_client import BCUClient, ExchangeRate, BCUResponse, _build_soap_request, _parse_xml_rates


def test_exchange_rate_dataclass():
    """Test del dataclass ExchangeRate."""
    er = ExchangeRate(
        fecha=date(2025, 7, 1),
        moneda_id=2225,
        compra=39.5,
        venta=40.5
    )
    
    assert er.fecha == date(2025, 7, 1)
    assert er.moneda_id == 2225
    assert er.compra == 39.5
    assert er.venta == 40.5


def test_bcu_response_dataclass():
    """Test del dataclass BCUResponse."""
    # Response exitoso
    resp_ok = BCUResponse(
        success=True,
        rates=[],
        message="OK"
    )
    assert resp_ok.success == True
    
    # Response con error
    resp_err = BCUResponse(
        success=False,
        rates=[],
        message="Error"
    )
    assert resp_err.success == False


def test_build_soap_request():
    """Test que el request SOAP se genere correctamente."""
    xml = _build_soap_request(2225, "2025-07-01", "2025-07-31")
    
    assert "2225" in xml
    assert "2025-07-01" in xml
    assert "2025-07-31" in xml
    assert "soapenv:Envelope" in xml


def test_parse_xml_rates():
    """Test del parseo de XML con datos de ejemplo."""
    xml_ejemplo = """<?xml version="1.0" encoding="utf-8"?>
    <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Body>
    <datoscotizaciones>
    <datoscotizaciones.dato>
    <Fecha>2025-07-01</Fecha>
    <TCC>39.5</TCC>
    <TCV>40.5</TCV>
    </datoscotizaciones.dato>
    <datoscotizaciones.dato>
    <Fecha>2025-07-02</Fecha>
    <TCC>39.6</TCC>
    <TCV>40.6</TCV>
    </datoscotizaciones.dato>
    </datoscotizaciones>
    </soap:Body>
    </soap:Envelope>"""
    
    rates = _parse_xml_rates(xml_ejemplo, moneda_id=2225)
    
    assert len(rates) == 2
    assert rates[0].fecha == date(2025, 7, 1)
    assert rates[0].compra == 39.5
    assert rates[0].venta == 40.5
    assert rates[1].fecha == date(2025, 7, 2)


def test_parse_xml_rates_vacio():
    """Test con XML vacío o sin datos."""
    xml_vacio = """<?xml version="1.0" encoding="utf-8"?>
    <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Body>
    <datoscotizaciones>
    </datoscotizaciones>
    </soap:Body>
    </soap:Envelope>"""
    
    rates = _parse_xml_rates(xml_vacio, moneda_id=2225)
    assert len(rates) == 0


if __name__ == "__main__":
    test_exchange_rate_dataclass()
    print("[OK] test_exchange_rate_dataclass")
    
    test_bcu_response_dataclass()
    print("[OK] test_bcu_response_dataclass")
    
    test_build_soap_request()
    print("[OK] test_build_soap_request")
    
    test_parse_xml_rates()
    print("[OK] test_parse_xml_rates")
    
    test_parse_xml_rates_vacio()
    print("[OK] test_parse_xml_rates_vacio")
    
    print("\nTodos los tests de BCU pasaron!")
