# -*- coding: utf-8 -*-
"""GARDĂ: codurile de concediu medical vin din registru, nu dintr-o listă scrisă în JS. (22.08.2026)

DE CE. `static/js/ecrane/flux_concediu.js` avea 18 coduri scrise de mână, cu procentele lipite în
etichetă. Consecința nu era teoretică: **codurile 11, 91 și 92 nu se puteau alege din interfață**, deși
există în nomenclator cu temei și aplicația le acceptă — adică ecranul **bloca un contabil să introducă
un cod legal**. Iar procentele erau valori fiscale scrise în JS (interdicția 1).

DECIZIA (Costin, D3): denumirea din nomenclator, procentul din registru, pe data certificatului;
eticheta se compune la randare; niciuna din cele două nu se scrie în JS.

CE FACE IMPOSIBIL: o listă de coduri scrisă din nou în JS · un procent scris în JS · pierderea
codurilor care nu erau în lista veche · ruperea legăturii cu variantele DATATE ale art. 17(1).
"""
import datetime as _d
import io
import os
import re

from core import coduri_cm_api, nomenclator_cm

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JS = os.path.join(RAD, "static", "js", "ecrane", "flux_concediu.js")


def _js():
    return io.open(JS, encoding="utf-8").read()


def test_ecranul_nu_mai_are_lista_scrisa_de_mana():
    t = _js()
    assert not re.search(r"const\s+CM_CODURI\s*=\s*\[", t), (
        "lista de coduri a reapărut scrisă în JS — se cere de la `/tenants/{id}/concedii/coduri`")
    assert "coduriCM(" in t, "ecranul nu mai cere lista de la server"
    assert "optiuniCM(" in t, "ecranul nu mai compune eticheta la randare"


def test_niciun_procent_scris_in_ecran():
    """Un procent în JS e o valoare fiscală în afara registrului (interdicția 1)."""
    t = _js()
    proza = set()
    for m in re.finditer(r"^\s*//.*$", t, re.M):
        proza.add(m.group(0))
    rele = []
    for i, ln in enumerate(t.splitlines(), 1):
        if ln in proza or ln.lstrip().startswith("//"):
            continue
        if re.search(r"\b(55|65|75|80|85|100)\s*%", ln):
            rele.append("  %d: %s" % (i, ln.strip()[:100]))
    assert not rele, "procente scrise în ecran:\n" + "\n".join(rele)


def test_toate_codurile_nomenclatorului_ajung_pe_ecran():
    """Lista veche omitea 11, 91, 92 — coduri legale, acceptate de aplicație."""
    din_api = {c["cod"] for c in coduri_cm_api.optiuni(_d.date(2026, 8, 22))}
    din_nomenclator = set(nomenclator_cm.CODURI)
    lipsa = sorted(din_nomenclator - din_api)
    assert not lipsa, "coduri din nomenclator care nu ajung pe ecran: %s" % lipsa
    for cod in ("11", "91", "92"):
        assert cod in din_api, "codul %s, care lipsea din lista scrisă de mână, tot nu ajunge" % cod


def test_procentul_urmeaza_DATA_certificatului():
    """Proba că procentul vine din registrul DATAT, nu dintr-un șir: art. 17(1) are două forme —
    75% uniform până la 01.08.2025, 55/65/75 progresiv după. Dacă eticheta nu se schimbă cu data,
    înseamnă că cineva a lipit-o la loc."""
    post = {c["cod"]: c["procent_text"] for c in coduri_cm_api.optiuni(_d.date(2026, 8, 22))}
    pre = {c["cod"]: c["procent_text"] for c in coduri_cm_api.optiuni(_d.date(2025, 3, 1))}
    assert post["01"] != pre["01"], (
        "codul 01 arată același procent înainte și după Legea 141/2025 (%r vs %r) — "
        "eticheta nu mai urmează registrul" % (pre["01"], post["01"]))
    assert "55" in post["01"] and post["01"] == "55/65/75%"
    assert pre["01"] == "75%"
    assert post["08"] == pre["08"] == "85%", "codurile neatinse de L141 n-ar trebui să se miște"


def test_codul_fara_procent_nu_inventeaza_unul():
    """Cod 10 (reducere de timp de muncă) n-are procent, ci formula art. 19."""
    o = {c["cod"]: c["procent_text"] for c in coduri_cm_api.optiuni(_d.date(2026, 8, 22))}
    assert o["10"] is None, "codul 10 a primit un procent, deși are formulă proprie (art. 19)"
