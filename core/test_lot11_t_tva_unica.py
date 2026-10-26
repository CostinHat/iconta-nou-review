# -*- coding: utf-8 -*-
"""Lotul 11, decizia Costin 10.3 (verbatim în DECIZII „Comanda 10.3” pct.4): „Rotunjirea TVA: o singură regulă pe toată aplicația, cea
cerută de validatorul e-Factura.” — garda regulii unice (`core/tva_calcul.py`).

Regulile EN 16931 aplicate de validatorul RO e-Factura (artefactele oficiale CEN `ConnectingEurope/eInvoicing-EN16931`,
`ubl/schematron/abstract/EN16931-model.sch`, citat verbatim):
  BR-DEC-23 „The allowed maximum number of decimals for the Invoice line net amount (BT-131) is 2.”
  BR-S-08   „[...] the VAT category taxable amount (BT-116) in a VAT breakdown (BG-23) shall equal the sum of Invoice line net amounts (BT-131)
             [...] where [...] the VAT rate (BT-152 [...]) equals the VAT category rate (BT-119).”
  BR-CO-17  „VAT category tax amount (BT-117) = VAT category taxable amount (BT-116) x (VAT category rate (BT-119) / 100), rounded to two
             decimals.”
  BR-CO-14  „Invoice total VAT amount (BT-110) = Σ VAT category tax amount (BT-117).”

Ce apără: (1) regula; (2) aceeași cifră pe XML-ul e-Factura, pe nota contabilă și pe ecran (oglinda JS, rulată în Node); (3) RATCHET: un
calcul de TVA din cotă scris în afara regulii unice nu poate apărea într-un fișier nou și nu poate crește într-unul vechi — fișierele încă
nemigrate au plafonul de azi (lista de mai jos), cele migrate au 0."""
import glob
import io
import json
import os
import re
import shutil
import subprocess
from decimal import Decimal

import pytest

from core import tva_calcul as _tc

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_D = Decimal


# ── (1) regula ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_tva_pe_cota_rotunjit_o_data_nu_pe_linie():
    # 50 de rânduri 3 × 19,99 la 21%: bază 2.998,50; BR-CO-17 -> 2.998,50 × 21 / 100 = 629,685 -> 629,69 (pe linie ar fi ieșit 629,50)
    t = _tc.totaluri([{"cantitate": 3, "pret_unitar": "19.99", "cota_tva": 21}] * 50)
    assert (t["baza"], t["tva"], t["total"]) == (_D("2998.50"), _D("629.69"), _D("3628.19")), t


def test_valoarea_neta_a_liniei_e_la_ban_br_dec_23():
    # BR-DEC-23: 1,333 × 1,50 = 1,9995 -> 2,00 (nu 1,9995 în bază); TVA 21% din 2,00 = 0,42
    assert _tc.net_linie("1.333", "1.50") == _D("2.00")
    assert _tc.pe_cote([{"cantitate": "1.333", "pret_unitar": "1.50", "cota_tva": 21}]) == {_D(21): (_D("2.00"), _D("0.42"))}


def test_doua_cote_fiecare_rotunjita_si_suma_lor_br_co_14():
    pc = _tc.pe_cote([{"cantitate": 1, "pret_unitar": "0.05", "cota_tva": 21}, {"cantitate": 1, "pret_unitar": "0.05", "cota_tva": 11}])
    # BR-CO-17 pe fiecare cotă: 0,0105 -> 0,01; 0,0055 -> 0,01; BR-CO-14: TVA total 0,02
    assert pc == {_D(21): (_D("0.05"), _D("0.01")), _D(11): (_D("0.05"), _D("0.01"))}


def test_stornarea_rotunjeste_simetric():
    # jumătatea departe de zero (ROUND_HALF_UP pe valoarea absolută, ca `abs()` din schematronul BR-CO-17): -0,0105 -> -0,01
    assert _tc.tva_din_baza("-0.05", 21) == _D("-0.01") and _tc.tva_din_baza("0.05", 21) == _D("0.01")


def test_suta_marita_si_lei_pe_cote():
    assert _tc.tva_din_total(605, 21) == _D("105.00")
    # valută: pe cote, la ban; suma pe cote = TVA-ul documentului în lei (CF art.319 alin.(20) lit.j), diferența pe cota cea mai mare
    pc = {_D(21): (_D("10.00"), _D("2.10")), _D(11): (_D("10.00"), _D("1.10"))}
    lei = _tc.tva_lei_pe_cote(pc, "4.9765")
    assert sum(lei.values()) == _tc.q2(_D("3.20") * _D("4.9765")) == _D("15.92"), lei


# ── (2) aceeași cifră peste tot ─────────────────────────────────────────────────────────────────────────────────────────────────────────
_LINII = [{"descriere": "Servicii", "cantitate": 3, "pret_unitar": "19.99", "cota_tva": 21, "um": "buc"}] * 50 + \
         [{"descriere": "Carte", "cantitate": "1.333", "pret_unitar": "1.50", "cota_tva": 11, "um": "buc"}]


def test_tva_scris_pe_factura_e_regula_unica():
    """`facturi_api.totaluri_din_linii` scrie TVA-ul pe factură (`creeaza_factura`) și îl arată formularul în valută (`previzualizare_lei`)."""
    from core import facturi_api
    t = _tc.totaluri(_LINII)
    assert facturi_api.totaluri_din_linii(_LINII) == {"total": t["total"], "tva": t["tva"]} == {"total": _D("3630.41"), "tva": _D("629.91")}


def test_xml_efactura_are_tva_din_regula_unica():
    from core import efactura_send as _es
    fz = {"nume": "Firma SRL", "cui": "14399840", "platitor_tva": True, "adresa": "Str. A 1", "oras": "Sector 1", "judet": "B", "tara": "RO"}
    cl = {"nume": "Client SRL", "cui": "18547290", "adresa": "Str. B 2", "oras": "Sector 2", "judet": "B", "tara": "RO"}
    xml = _es.genereaza_xml({"serie": "T", "numar": "T1", "data_emitere": "2026-10-21", "moneda": "RON"}, _LINII, fz, cl)
    t = _tc.totaluri(_LINII)
    # BR-CO-14: TaxTotal/TaxAmount = Σ TVA pe cote (629,69 + 0,22)
    assert re.search(r'<cac:TaxTotal>\s*<cbc:TaxAmount currencyID="RON">%s</cbc:TaxAmount>' % t["tva"], xml), xml[:3000]
    assert '<cbc:TaxInclusiveAmount currencyID="RON">%s</cbc:TaxInclusiveAmount>' % t["total"] in xml   # BR-CO-15
    assert t["tva"] == _D("629.91")


def test_nota_contabila_are_tva_din_regula_unica():
    from core import contare_facturi as _cf
    linii = [dict(l, cont="704") for l in _LINII]
    note = _cf._note_pe_cote(linii, _D(1), lambda c, s: ("4111", c, s), lambda s: ("4111", "4427", s))
    tva = {n["suma"] for n in note if n["credit"] == "4427"}
    assert tva == {_D("629.69"), _D("0.22")}, note
    assert sum(n["suma"] for n in note if n["credit"] == "704") == _tc.totaluri(_LINII)["baza"]
    # două conturi de venit pe aceeași cotă: TVA-ul e al COTEI (0,14 × 21% = 0,0294 -> 0,03), nu al fiecărui cont (0,01 + 0,01)
    doua = [{"cont": "704", "cantitate": 1, "pret_unitar": "0.07", "cota_tva": 21}, {"cont": "707", "cantitate": 1, "pret_unitar": "0.07", "cota_tva": 21}]
    note = _cf._note_pe_cote(doua, _D(1), lambda c, s: ("4111", c, s), lambda s: ("4111", "4427", s))
    assert [n["suma"] for n in note if n["credit"] == "4427"] == [_D("0.03")], note


@pytest.mark.skipif(not shutil.which("node"), reason="node lipsește")
def test_oglinda_js_da_aceeasi_cifra_ca_python():
    src = io.open(os.path.join(_RAD, "static", "js", "ecrane", "emitere_ecran.js"), encoding="utf-8").read()
    m = re.search(r"const _BI = BigInt[^\n]*\nfunction _zec\(.*?\nexport function tvaDocument\(linii\) \{.*?\n\}\n", src, re.S)
    assert m, "oglinda JS a regulii (tvaDocument) a dispărut din emitere_ecran.js"
    cazuri = [_LINII, [{"cantitate": 1, "pret_unitar": "0.05", "cota_tva": 21}, {"cantitate": 1, "pret_unitar": "0.05", "cota_tva": 11}],
              [{"cantitate": -2, "pret_unitar": "10.025", "cota_tva": 21}], [{"cantitate": "0.5", "pret_unitar": "0.01", "cota_tva": 9}]]
    js = m.group(0).replace("export function", "function") + "\nconsole.log(JSON.stringify(%s.map((c) => tvaDocument(c))));" % (
        json.dumps([[{k: str(v) for k, v in l.items() if k in ("cantitate", "pret_unitar", "cota_tva")} for l in c] for c in cazuri]))
    r = subprocess.run(["node", "-e", js], capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, r.stderr
    for c, j in zip(cazuri, json.loads(r.stdout)):
        t = _tc.totaluri(c)
        assert (_D(str(j["baza"])).quantize(_D("0.01")), _D(str(j["tva"])).quantize(_D("0.01"))) == (t["baza"], t["tva"]), (c, j, t)


# ── (3) RATCHET: niciun calcul paralel nou ──────────────────────────────────────────────────────────────────────────────────────────────
_PY = re.compile(r"(?:(?:cota|procent)\w*[)\]\"' ]{0,6}\s*/\s*(?:\w*\()?[\"']?100\b)"
                 r"|(?:/\s*\(\s*(?:Decimal\()?[\"']?100[\"']?\)?\s*\+\s*(?:Decimal\()?(?:str\()?\w*cota)")
_JS = re.compile(r"(?:cota\w*[)\] ]{0,4}\s*/\s*100\b)|(?:/\s*\(\s*100\s*\+\s*\w*cota)")
_NU_E_TVA = re.compile(r"pro_?rata|cass|impozit|dobanda|discount|cota_cas|cota_parte|procent_", re.I)

#: plafonul de azi (21.10.2026) al calculelor din cotă scrise în afara `core/tva_calcul.py`. Un fișier migrat iese de aici (0); o cifră
#: poate scădea, niciodată crește; un fișier nou nu are voie. Două feluri:
#:  - NU E TVA (impozit pe dividende / pe venit, cote de impozit): d100_reconciliere, d101, d101g, d114, d212, d216, dividende_curs,
#:    decontari_asociati, cititor_js (comentariu);
#:  - TVA ÎNCĂ NEMIGRAT (de adus pe regula unică; patch-urile sunt în raportul lotului 11, subagentul T): contare_facturi (factura veche fără linii, cota ca fracție), control_incrucisat, avansuri, comodat_chirii, deconturi, import_export, intracomunitar,
#:    inventariere, leasing, lichidare, obiecte_inventar, perisabilitati, productie, sgr, stocuri, stocuri_cv_api, taxare_inversa, tva_marja,
#:    uc_tenants, export_saga, export_winmentor, d301_operatiuni_api, d300, d394, d406, declaratii.js; și CĂILE A DOUA ale reconcilierilor
#:    (d300_reconciliere, d394_reconciliere) — care NU se aduc pe funcția unică: ele recalculează independent PRIN CONSTRUCȚIE
#:    (`test_d300_reconciliere.test_non_tautologie_*`), deci își scriu singure regula.
PLAFON = {
    "core/avansuri.py": 1, "core/cititor_js.py": 1, "core/comodat_chirii.py": 1, "core/contare_facturi.py": 2, "core/control_incrucisat.py": 1, "core/d100_reconciliere.py": 1,
    "core/d101.py": 1, "core/d101g.py": 1, "core/d114.py": 2, "core/d212.py": 1, "core/d216.py": 2, "core/d300.py": 3,
    "core/d300_reconciliere.py": 1, "core/d301_operatiuni_api.py": 2, "core/d394.py": 1, "core/d394_reconciliere.py": 2, "core/d406.py": 2,
    "core/decontari_asociati.py": 1, "core/deconturi.py": 1, "core/dividende_curs.py": 1, "core/export_saga.py": 1,
    "core/export_winmentor.py": 1, "core/import_export.py": 1, "core/intracomunitar.py": 1,
    "core/inventariere.py": 1, "core/leasing.py": 3, "core/lichidare.py": 1, "core/obiecte_inventar.py": 1, "core/perisabilitati.py": 1,
    "core/productie.py": 1, "core/sgr.py": 1, "core/stocuri.py": 4, "core/stocuri_cv_api.py": 0, "core/taxare_inversa.py": 1,
    "core/tva_marja.py": 1, "core/uc_tenants.py": 1, "static/js/ecrane/declaratii.js": 1,
}
#: migrate pe regula unică în lotul 11 — 0 pentru totdeauna
MIGRATE = ("core/facturi_api.py", "core/factura_pdf.py", "core/efactura_send.py", "core/tva_incasare.py", "static/js/ecrane/emitere_ecran.js",
           "static/js/ecrane/facturi_ecran.js")


def _numara():
    c = {}
    for f in glob.glob(os.path.join(_RAD, "core", "*.py")) + [os.path.join(_RAD, "main.py")]:
        b = os.path.basename(f)
        if b.startswith(("test_", "migrare_")) or b == "tva_calcul.py":
            continue
        for ln in io.open(f, encoding="utf-8"):
            s = "" if ln.lstrip().startswith(("\"", "'")) else ln.split("#", 1)[0]
            if _PY.search(s) and not _NU_E_TVA.search(s):
                k = os.path.relpath(f, _RAD)
                c[k] = c.get(k, 0) + 1
    for f in glob.glob(os.path.join(_RAD, "static", "js", "**", "*.js"), recursive=True):
        for ln in io.open(f, encoding="utf-8"):
            if _JS.search(ln.split("//", 1)[0]):
                k = os.path.relpath(f, _RAD)
                c[k] = c.get(k, 0) + 1
    return c


def test_niciun_calcul_de_tva_paralel_nou():
    c = _numara()
    peste = {k: (v, PLAFON.get(k, 0)) for k, v in c.items() if v > PLAFON.get(k, 0)}
    assert not peste, ("Calcul de TVA din cotă în afara regulii unice (core/tva_calcul.py — decizia Costin 10.3: „o singură regulă pe toată "
                       "aplicația, cea cerută de validatorul e-Factura”). Folosește tva_calcul.tva_din_baza / tva_din_total / pe_cote / "
                       "totaluri; fișier: (găsite, plafon) = %s" % peste)
    assert not [k for k in MIGRATE if c.get(k)], [k for k in MIGRATE if c.get(k)]
