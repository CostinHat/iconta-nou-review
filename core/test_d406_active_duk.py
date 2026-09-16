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
    # cont 2131 = echipamente (lit.b) -> lin/deg/accel permise; superaccel cere PIF in 2026 (alin.8^1)
    pif = date(2026, 12, 20) if met == "superaccelerata" else date(2025, 12, 20)
    return {"cod": "MF-%s" % met[:4].upper(), "denumire": "Demo %s" % met,
            "valoare": 100000, "rezidual": 0, "dnf_luni": 60, "data_pif": pif,
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


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_apreciere_nenula_e_DUK_valida():
    """[R59] `AppreciationForPeriod` era literalul `0.00` de cand exista generatorul.

    Reparatia lui R59 il face sa poarte apreciere reala — deci afirmatia „structura ramane valida"
    nu se mai poate presupune, se cere ARBITRULUI. *Validatorul e judecatorul final; adiacenta din
    bytecode m-a mintit deja o data, la D100.*
    """
    _db.init_pool()
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SET search_path TO %s, public" % _SCHEMA)
            prof = d406.pull(conn, _SCHEMA, 2026, 12)
            prof = prof[0] if isinstance(prof, tuple) else prof
        conn.rollback()

    reevaluat = dict(_mf("liniara"), cod="MF-REEV-R59", valoare=3500,
                     data_pif=date(2025, 1, 15),
                     reevaluari=[{"data": date(2026, 3, 20), "valoare_bruta_veche": 3000,
                                  "amortizare_eliminata": 700, "valoare_justa": 3500}])
    xml = d406_active.xml_d406_anual_active(prof, [reevaluat], 2026)

    # Pe ELEMENTE, nu pe siruri: fara verificarea asta proba ar putea valida cu DUK un fisier in
    # care campul masurat nici nu e emis — verde despre altceva. (METODA §23)
    import xml.etree.ElementTree as ET
    ns = "{mfp:anaf:dgti:d406:declaratie:v1}"
    val = ET.fromstring(xml).find(".//%sValuation" % ns)
    assert val is not None, "fisierul anual n-are <Valuation> — structura s-a schimbat, nu cifra"
    camp = {e.tag.split("}")[-1]: (e.text or "") for e in val}
    assert camp["AppreciationForPeriod"] == "500.00", \
        "aprecierea nu ajunge in XML — proba ar valida un fisier fara campul masurat"
    assert camp["AcquisitionAndProductionCostsBegin"] == "3000.00"
    assert camp["AcquisitionAndProductionCostsEnd"] == "3500.00"

    v = duk.valideaza(xml, "d406", an=2026, luna=12, timeout=240)
    if v.get("stare") == "gri":
        pytest.skip("validator SAF-T indisponibil: %s" % v.get("temei"))
    assert v.get("stare") == "valid", "DUK nu e valid pe apreciere nenula: %s" % v
