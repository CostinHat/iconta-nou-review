# -*- coding: utf-8 -*-
"""Proba DUK pe tenant_013 pentru amortizarea D406/SAF-T pe metoda.

Genereaza raportarea ANUALA de active (HeaderComment='A') pentru tenant_013, cu <Assets>
populat pe fiecare metoda (liniara/degresiva/accelerata/superaccelerata), si o trece prin
validatorul OFICIAL ANAF (DUKIntegrator_AnLunaUI). Inchide latura "probata DUK" a datoriei
MF/D406 (DECIZII.md 13.08.2026). DUK verifica STRUCTURA, nu aritmetica - cifrele sunt pazite
de golden in test_d406_amortizare.py.
"""
from datetime import date

import pytest

from core import db as _db
from core import d406, d406_active, duk

_SCHEMA = "tenant_013"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


def _mf(met):
    return {"cod": "MF-%s" % met[:4].upper(), "denumire": "Demo %s" % met,
            "valoare": 100000, "rezidual": 0, "dnf_luni": 60, "data_pif": date(2025, 12, 20),
            "cont_imobilizare": "2131", "cont_amortizare": "2813", "metoda": met, "activ": True}


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d406_anual_active_toate_metodele_duk_valid():
    """tenant_013: D406 anual cu active pe toate 4 metodele -> DUKIntegrator SAF-T valid."""
    _db.init_pool()
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SET search_path TO %s, public" % _SCHEMA)
            prof = d406.pull(conn, _SCHEMA, 2026, 12)
            prof = prof[0] if isinstance(prof, tuple) else prof
            cur.execute("""SELECT id,cod,denumire,cont_imobilizare,cont_amortizare,valoare,
                                  rezidual,dnf_luni,data_pif,metoda,activ
                           FROM mijloace_fixe WHERE data_pif IS NOT NULL ORDER BY id""")
            cols = [d[0] for d in cur.description]
            reale = [dict(zip(cols, r)) for r in cur.fetchall()]
        conn.rollback()

    lista = reale + [_mf(m) for m in ("liniara", "degresiva", "accelerata", "superaccelerata")]
    xml = d406_active.xml_d406_anual_active(prof, lista, 2026)
    for m in ("liniara", "degresiva", "accelerata", "superaccelerata"):
        assert "<DepreciationMethod>%s</DepreciationMethod>" % m in xml, "metoda %s lipseste din XML" % m

    v = duk.valideaza(xml, "d406", an=2026, luna=12, timeout=180)
    if v.get("stare") == "gri":
        pytest.skip("validator SAF-T indisponibil: %s" % v.get("temei"))
    assert v.get("stare") == "valid", "DUK nu e valid: %s" % v
