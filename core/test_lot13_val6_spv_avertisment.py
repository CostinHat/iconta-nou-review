# -*- coding: utf-8 -*-
"""[lotul 13, deficiența 696 — a lui Code] `efactura_trimitere.trimite` încărca factura în SPV și când dreptul certificatului pe CUI-ul
firmei era „neverificat” / „neconfirmat” (`spv_conector.acoperire_cui`), fără să spună nimic; se oprea numai pe „fără drept”. ANAF răspunde la
încărcare (nu e pierdere tăcută), deci NU se refuză: trimiterea continuă, iar răspunsul poartă `avertisment` (arătat lângă buton de ecranul
„Trimite în SPV”). Acoperit: fără avertisment. Fără drept: tot refuz (poarta 1b, `test_spv_lot6`).

Temei: N/A — comportament de produs (ARHITECTURA_SPV.md: dreptul pe CUI se află empiric, la citire; ANAF nu dă lista CUI-urilor unui
certificat). Fără DB: citirile și scrierea rândului sunt înlocuite; poarta, avertismentul și încărcarea rulează pe codul lor."""
import contextlib

import pytest

from core import efactura_trimitere as et


class _Raspuns:
    status_code, text = 200, "<ok/>"


class _Conn:
    def cursor(self, *a, **k):
        return self

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, *a):
        pass

    def fetchone(self):
        return ("RO55229657",)


@pytest.fixture()
def trimitere(monkeypatch):
    incarcari = []
    monkeypatch.setattr(et.db, "get_conn", lambda *a, **k: contextlib.nullcontext(_Conn()))
    monkeypatch.setattr(et.spv_conector, "ia_token_activ", lambda c, p: {"id": 1})
    monkeypatch.setattr(et, "refuz_din_efactura", lambda *a: None)
    monkeypatch.setattr(et, "incarca_factura", lambda *a: ({"tert_tara": "RO"}, [], {}, {}))
    monkeypatch.setattr(et, "completeaza_client_ro", lambda c: c)
    monkeypatch.setattr(et._ef, "genereaza_xml", lambda *a: "<Invoice/>")
    monkeypatch.setattr(et._ef, "valideaza", lambda xml: (True, []))
    monkeypatch.setattr(et._ef, "_parse_upload", lambda t: (0, "4242", []))
    monkeypatch.setattr(et._ef, "upload_ubl", lambda *a, **k: incarcari.append(a) or _Raspuns())
    monkeypatch.setattr(et._repo, "trimitere_in_curs", lambda *a: None)
    monkeypatch.setattr(et._repo, "trimitere_vie", lambda *a: None)
    monkeypatch.setattr(et._repo, "insereaza_trimitere_pregatita", lambda *a: (7,))
    monkeypatch.setattr(et._repo, "rezultatul_trimiterii", lambda *a: None)
    return incarcari


def _stare(monkeypatch, **kw):
    monkeypatch.setattr(et.spv_conector, "stare_firma", lambda c, p, cui: dict({"are_drept": None}, **kw))


@pytest.mark.parametrize("acoperire", ["neverificat", "neconfirmat"])
def test_dreptul_neconfirmat_trimite_cu_avertisment(trimitere, monkeypatch, acoperire):
    _stare(monkeypatch, acoperire=acoperire)
    r = et.trimite("tenant_x", 5, "P")
    print("696", acoperire, "->", r["stare"], "|", r.get("avertisment"))
    assert r["stare"] == "incarcat" and len(trimitere) == 1, (r, trimitere)   # a plecat la ANAF
    assert r["avertisment"] == et.AVERTISMENT_ACOPERIRE[acoperire] and et.AVERTISMENT_ACOPERIRE[acoperire].count("Setări cont › Conectare SPV") == 1, r


def test_dreptul_confirmat_trimite_fara_avertisment(trimitere, monkeypatch):
    _stare(monkeypatch, acoperire="acoperit", are_drept=True)
    r = et.trimite("tenant_x", 5, "P")
    assert r["stare"] == "incarcat" and "avertisment" not in r and len(trimitere) == 1, r


def test_fara_drept_ramane_refuz(trimitere, monkeypatch):
    _stare(monkeypatch, acoperire="neacoperit", are_drept=False, mesaj="M")
    assert et.trimite("tenant_x", 5, "P") == {"stare": "fara_drept", "mesaj": "M"} and trimitere == []


def test_avertismentul_ajunge_in_raspunsul_rutei(trimitere, monkeypatch):
    """Ruta (`uc_tenants.factura_trimite_spv`) întoarce cheia pe nume: ecranul citește `r.avertisment`."""
    import re
    src = open(et.__file__.replace("efactura_trimitere.py", "uc_tenants.py"), encoding="utf-8").read()
    assert re.search(r'"avertisment": r\.get\("avertisment"\)', src)


def test_factura_recurenta_trimisa_cu_avertisment_anunta_contabilul(monkeypatch):
    """Drumul al doilea al lui `trimite` (cronul facturilor recurente, 680) n-are ecran lângă un buton: avertismentul ajunge în clopoțel; o
    trimitere fără avertisment rămâne tăcută, ca înainte. MUTAȚIE: condiția `or avertisment` scoasă din `_trimite_spv` -> pică."""
    from core import facturi_recurente as fr, notificari_termene as nt, spv_conector as sc
    anunturi = []
    monkeypatch.setattr(fr._obs if hasattr(fr, "_obs") else et._obs, "esec_secundar", lambda *a: None)
    monkeypatch.setattr("core.db.get_conn", lambda *a, **k: contextlib.nullcontext(_Conn()))
    monkeypatch.setattr(sc, "principal_pentru_schema", lambda conn, schema: "P")
    monkeypatch.setattr(nt, "notifica_pe_conexiune", lambda conn, schema, tip, f: anunturi.append(f("Ana")))
    sablon, rand = {"id": 1, "tert_nume": "Client SRL"}, {"factura_id": 5, "numar": "F1-7"}
    monkeypatch.setattr(et, "trimite", lambda *a, **k: {"stare": "incarcat", "avertisment": et.AVERTISMENT_ACOPERIRE["neverificat"]})
    assert fr._trimite_spv("tenant_x", sablon, rand, None) == "incarcat"
    assert anunturi == ["Ana: factura recurentă F1-7 pentru Client SRL a plecat în SPV. " + et.AVERTISMENT_ACOPERIRE["neverificat"]], anunturi
    anunturi.clear()
    monkeypatch.setattr(et, "trimite", lambda *a, **k: {"stare": "incarcat"})
    assert fr._trimite_spv("tenant_x", sablon, rand, None) == "incarcat" and anunturi == []
