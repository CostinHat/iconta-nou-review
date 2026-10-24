# -*- coding: utf-8 -*-
"""306 — factura către un client din UE (comanda Costin 17.10.2026 7.2, verbatim în DECIZII): „detaliul facturii arată doar «0%», fără
categoria TVA; pe PDF clientul UE are «CUI:» în loc de «Cod TVA:», iar adresa e fără țară.”

Temei: CF art.319 alin.(20) lit.f — pe factură, „denumirea/numele și adresa beneficiarului [...] precum și codul de înregistrare în scopuri
de TVA” al lui; la clientul din alt stat membru, codul de TVA dat de statul lui (cu prefixul statului).
"""
import io
import re

from core import factura_pdf as fp


def test_306_clientul_ue_are_cod_tva_cu_prefixul_statului_si_tara_in_adresa():
    """MUTAȚII: ramura `t != "RO"` scoasă din `cod_fiscal_pe_factura` -> „CUI” / „RO…” -> pică; țara scoasă din `adresa_tert` -> pică."""
    assert fp.cod_fiscal_pe_factura("IE9999999ZZ", None, "IE") == ("Cod TVA", "IE9999999ZZ")   # cod sintetic, evident nereal
    assert fp.cod_fiscal_pe_factura("IE9999999ZZ", True, "IE") == ("Cod TVA", "IE9999999ZZ"), "nu RO + cifre"
    assert fp.cod_fiscal_pe_factura("14399840", True, "RO") == ("Cod TVA", "RO14399840")
    assert fp.cod_fiscal_pe_factura("14399840", False) == ("CIF", "14399840")
    assert fp.adresa_tert("1 Grand Canal Square", "Dublin", None, "IE") == "1 Grand Canal Square, Dublin, Irlanda"
    assert fp.adresa_tert("Str. X 1", "Cluj-Napoca", "Cluj", "RO") == "Str. X 1, Cluj-Napoca, Cluj", "clientul român: fără țară"


def test_306_numele_tarilor_sunt_cele_din_emitere():
    """Paritatea cu lista din „Emite factură” (aceleași coduri și nume)."""
    # [lotul 12, C160] lista țărilor stă în `tari_partener.js` (sursa unică a emiterii și a șablonului recurent)
    js = io.open("static/js/ecrane/tari_partener.js", encoding="utf-8").read()
    a = js.index("export const TARI_UE_JS")
    corp = js[a:js.index("export function optiuniTara", a)]
    din_js = dict(re.findall(r'([A-Z]{2}):"([^"]+)"', corp))
    assert din_js == fp.TARI_NUME
