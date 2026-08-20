# -*- coding: utf-8 -*-
"""core/test_d390_checksum_manual.py — GARD: checksum-ul VIES se aplica pe TOATE liniile D390,
nu doar pe cele derivate din facturi.

Audit tenant_006 (20.08.2026), frontul I2. `checksum_vies` era chemat DOAR de `_facturi_ic`
(latura auto). Bucla liniilor MANUALE din `calcul_d390` verifica doar lungimea codO (>12), nu si
cifra de control -> o operatiune introdusa in ecranul D390 sau derivata din D301 intra in
declaratie cu un cod TVA nevalidat, iar contabilul afla abia din respingerea de la DUK regula R24.1.
Cele doua cai de intrare (factura / manual+D301) tratau acelasi camp cu doua masuri.

Caracterul e NEBLOCANT, identic cu latura auto (vezi docstringul lui `d390.valideaza`): o
operatiune obligatorie raportata cu cod invalid e mai buna decat una disparuta tacit; partenerul
e NUMIT, iar DUK decide. Gardul verifica si asta - un checksum invalid NU trebuie sa blocheze
emiterea.
"""
from decimal import Decimal

from core.d390 import calcul_d390, valideaza


def _prof(**kw):
    p = {"cui": "14399840", "nume": "ACHIZITII IC NEPLATITOR SRL",
         "adresa": "Str. Test 1", "telefon": "0212345678"}
    p.update(kw)
    return p


def _linie(cod, tip="A", tara="DE", den="FURNIZOR DE", baza=52261):
    return {"tip": tip, "tara": tara, "cod": cod, "den": den, "baza": baza}


def _cat(res, categorie):
    return [d for d in getattr(res, "diag", []) if d["categorie"] == categorie]


def test_cod_invalid_pe_linie_manuala_e_diagnosticat():
    """DE136695975 = seed-ul valid cu ultima cifra stricata (cifra de control MOD 11,10)."""
    res = calcul_d390(_prof(), 2026, 6, [], manual=[_linie("136695975")])
    ch = _cat(res, "checksum")
    assert ch, ("linie manuala cu cod TVA invalid nu produce niciun diagnostic - contabilul afla "
                "abia din respingerea de la DUK regula R24.1")
    assert ch[0]["cod"] == "136695975" and ch[0]["tara"] == "DE"
    assert any("136695975" in a and "invalid" in a.lower() for a in res.avertismente), \
        "partenerul nu e NUMIT in avertismente: %r" % (res.avertismente,)


def test_cod_valid_pe_linie_manuala_nu_produce_zgomot():
    """Linia reala a lui tenant_006 (iunie 2026): DE136695976, cod A, baza 52.261 - DUK-valida."""
    res = calcul_d390(_prof(), 2026, 6, [], manual=[_linie("136695976")])
    assert not _cat(res, "checksum"), "fals pozitiv pe un cod TVA corect: %r" % (res.diag,)
    assert res.nr_opi == 1 and res.rezumat["A"] == 52261


def test_codo_gol_pe_tip_A_nu_e_raportat_ca_invalid():
    """A si S pot omite legal codO (vezi `valideaza`) - lipsa nu e greseala de cifra de control."""
    res = calcul_d390(_prof(), 2026, 6, [], manual=[_linie("", den="FURNIZOR FARA COD")])
    assert not _cat(res, "checksum"), "codO gol raportat ca cod invalid: %r" % (res.diag,)


def test_checksum_invalid_ramane_NEBLOCANT():
    """Simetric cu latura auto: se emite si se NUMESTE partenerul; blocarea ar face operatiunea
    obligatorie sa dispara din declaratie."""
    res = calcul_d390(_prof(), 2026, 6, [], manual=[_linie("136695975")])
    erori = valideaza(res)
    assert not [e for e in erori if "cifra de control" in e or "R24.1" in e], \
        "checksum-ul a devenit blocant: %r" % (erori,)


def test_cod_invalid_intra_pe_ambele_cai_cu_acelasi_verdict():
    """Aceeasi operatiune, o data ca factura si o data ca linie manuala -> acelasi diagnostic.
    Asimetria dintre cele doua cai a fost defectul."""
    fact = [{"cui": "DE136695975", "nume": "FURNIZOR DE", "directie": "primita",
             "total": Decimal("52261"), "tva": Decimal("0")}]
    r_auto = calcul_d390(_prof(), 2026, 6, fact)
    r_man = calcul_d390(_prof(), 2026, 6, [], manual=[_linie("136695975")])
    assert bool(_cat(r_auto, "checksum")) == bool(_cat(r_man, "checksum")) is True, \
        "calea manuala si calea prin factura dau verdicte diferite pe acelasi cod TVA"
