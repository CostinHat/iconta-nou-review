"""F179 pe schema efemeră a bazei native de test. Transportul SPV este local simulat."""

from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4
from zipfile import ZipFile

import pytest
from psycopg2 import sql
from core import db, efactura_send, spv_conector, spv_receive, tenant_provisioning

CUI = "55229657"


@pytest.fixture
def schema_q10():
    db.init_pool()
    schema = "ztest_q10_" + uuid4().hex[:16]
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT current_database()")
        assert cur.fetchone()[0] == "iconta_test", "Schema Q10 cere iconta_test"
        cur.execute(
            tenant_provisioning.parametrizeaza_template(
                Path("tenant_template.sql").read_text(), schema
            )
        )
    try:
        yield schema
    finally:
        with db.get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema))
            )


def arhiva_ubl(beneficiar):
    xml = f"""<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
    xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
    xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
    <cbc:ID>Q10-1</cbc:ID><cbc:IssueDate>2026-11-25</cbc:IssueDate><cbc:DocumentCurrencyCode>RON</cbc:DocumentCurrencyCode>
    <cac:AccountingSupplierParty><cac:Party><cac:PartyLegalEntity><cbc:RegistrationName>Furnizor probă</cbc:RegistrationName>
    <cbc:CompanyID>12345674</cbc:CompanyID></cac:PartyLegalEntity></cac:Party></cac:AccountingSupplierParty>
    <cac:AccountingCustomerParty><cac:Party><cac:PartyLegalEntity><cbc:RegistrationName>Beneficiar probă</cbc:RegistrationName>
    <cbc:CompanyID>{beneficiar}</cbc:CompanyID></cac:PartyLegalEntity></cac:Party></cac:AccountingCustomerParty>
    <cac:LegalMonetaryTotal><cbc:TaxInclusiveAmount currencyID="RON">1.00</cbc:TaxInclusiveAmount></cac:LegalMonetaryTotal>
    <cac:InvoiceLine><cbc:ID>1</cbc:ID><cbc:InvoicedQuantity unitCode="C62">1</cbc:InvoicedQuantity>
    <cbc:LineExtensionAmount currencyID="RON">1.00</cbc:LineExtensionAmount><cac:Item><cbc:Name>Serviciu probă</cbc:Name></cac:Item>
    <cac:Price><cbc:PriceAmount currencyID="RON">1.00</cbc:PriceAmount></cac:Price></cac:InvoiceLine></Invoice>"""
    buffer = BytesIO()
    with ZipFile(buffer, "w") as arhiva:
        arhiva.writestr("factura.xml", xml.encode())
    return buffer.getvalue()


@pytest.mark.parametrize(
    "beneficiar,acceptat", [(CUI, True), ("403000015", False), ("", False)]
)
def test_f179_identitate_si_reincercare(schema_q10, monkeypatch, beneficiar, acceptat):
    payload = arhiva_ubl(beneficiar)
    monkeypatch.setattr(
        efactura_send,
        "descarca",
        lambda *args, **kwargs: SimpleNamespace(status_code=200, content=payload),
    )
    msg = {
        "id": "9100000001",
        "id_solicitare": "90001",
        "tip": "FACTURA PRIMITA",
        "cif_emitent": "12345674",
    }
    st = spv_receive._stat_nou()
    for _ in range(2):
        spv_receive.importa_mesaj(
            schema_q10, spv_conector.principal_firm(1), CUI, msg, st
        )
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            sql.SQL(
                "SELECT status,cif_beneficiar,factura_id FROM {}.efactura_primite WHERE id_mesaj_anaf=%s"
            ).format(sql.Identifier(schema_q10)),
            (msg["id"],),
        )
        randuri = cur.fetchall()
    assert randuri == ([("ciorna", CUI, None)] if acceptat else [])
