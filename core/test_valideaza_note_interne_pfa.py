# -*- coding: utf-8 -*-
"""`scripts/valideaza_note_interne_pfa.py` — validarea UNICĂ a ciornelor PFA de dinainte de lotul 9 (decizia Costin 19.10.2026, verbatim în
DECIZII „Închiderea lotului 9: poarta, producția, ciornele PFA vechi”: „Da, o dată, la publicare, cu backup. În raport doar numărul de note
validate și refuzate și motivele, fără nume de firme sau alte date ale cabinetului.”). Pe drumul validării interne (`jurnal_api.
valideaza_interne`, toate regulile); numărătoarea e pe FELUL refuzului (codul), nu pe textul lui (care poartă date, sume, etichete).
Schema efemeră PFA a lui `core/test_pfa_note_interne.py` (fixtura `lume`), tranzacție anulată."""
import os
import sys

from core import jurnal_api
from core.test_pfa_note_interne import SCH, _stari, lume, lume_srl  # noqa: F401 — fixturile schemei efemere

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import valideaza_note_interne_pfa as _v  # noqa: E402


def _ciorne(conn):
    """Trei ciorne vechi (de dinainte de lot, fără autor): una cu document, una fără (R3), o plată din casă fără sold (406)."""
    with conn.cursor() as cur:
        cur.execute("SELECT set_config('iconta.utilizator', '', false)")
    ok = jurnal_api.creeaza(conn, SCH, "Chirie iulie", "2026-07-05",
                            [{"debit": "612", "credit": "401", "suma": 500, "partener_nume": "PARTENER PROBA SRL"}],
                            document_ref="Factura CH 12 din 05.07.2026")["id"]
    fara_doc = jurnal_api.creeaza(conn, SCH, "Fără document", "2026-07-06",
                                  [{"debit": "612", "credit": "401", "suma": 50, "partener_nume": "PARTENER PROBA SRL"}])["id"]
    plata = jurnal_api.creeaza(conn, SCH, "Plată furnizor", "2026-07-07",
                               [{"debit": "401", "credit": "5311", "suma": 200, "partener_nume": "PARTENER PROBA SRL"}],
                               document_ref="Dispoziția de plată 3 din 07.07.2026")["id"]
    return ok, fara_doc, plata


def test_ciornele_vechi_ale_pfa_se_valideaza_iar_refuzurile_se_numara_pe_fel(lume):
    """MUTAȚIA: `cu_cod=True` scos din `valideaza_schema` -> refuzurile fără cod -> numărătoarea pică (ROȘU)."""
    conn, _uid = lume
    ok, fara_doc, plata = _ciorne(conn)
    validate, refuzuri = _v.valideaza_schema(conn, SCH)
    assert _stari(conn, [ok, fara_doc, plata]) == {ok: "validata", fara_doc: "ciorna", plata: "ciorna"}
    # R3 e o regulă din bază (`REGULA_CONTABILA:`), casa sub zero e regula 406 din `valideaza` (`CASA_NEGATIVA`)
    assert (validate, dict(refuzuri)) == (1, {"REGULA_CONTABILA": 1, "CASA_NEGATIVA": 1}), (validate, refuzuri)


def test_la_partida_dubla_nu_se_atinge_nimic(lume_srl):
    conn, _uid = lume_srl
    ok, fara_doc, plata = _ciorne(conn)
    assert _v.valideaza_schema(conn, SCH) is None
    assert set(_stari(conn, [ok, fara_doc, plata]).values()) == {"ciorna"}
