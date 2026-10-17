# -*- coding: utf-8 -*-
"""314 — povestea lunii aprobată, cu cifrele lunii schimbate după aprobare (comanda Costin 17.10.2026 7.2 pct.7, verbatim în DECIZII):
„povestea aprobată se marchează depășită și Trimite se oprește dacă cifrele lunii s-au schimbat după aprobare.”
Pe `public.pachet_povestea` a bazei de test, cu un tenant sintetic (209914) șters la ieșire. Temei: N/A — regulă de proces.
"""
import pytest

from core import db as _db
from core import pachete_api as pa

TID = 209914


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture()
def cp():
    if not _db_ok():
        pytest.skip("DB indisponibil")
    with _db.get_conn() as c:
        yield c
        c.rollback()


def _rz(venituri):
    return {"venituri": venituri, "cheltuieli": 400.0, "rezultat": venituri - 400.0, "tip": "profit", "declaratii_depuse": ["D300"],
            "email": "client@exemplu.test", "nume_firma": "F"}


def test_314_aprobata_pe_alte_cifre_e_depasita_si_nu_se_trimite(cp, monkeypatch):
    """MUTAȚIE: `out["depasita"] = row["cifre_amprenta"] != amprenta_cifre(rz)` -> `False` -> pică."""
    pa.salveaza_poveste(cp, TID, 2099, 10, "Luna aceasta: venituri 1.000 lei.", status="aprobat", amprenta=pa.amprenta_cifre(_rz(1000.0)))
    assert pa.get_poveste(cp, TID, 2099, 10, rz=_rz(1000.0))["depasita"] is False
    p = pa.get_poveste(cp, TID, 2099, 10, rz=_rz(1300.0))   # o notă validată după aprobare: venituri 1.300
    assert p["depasita"] is True and "depășită" in p["motiv_depasita"], p
    monkeypatch.setattr(pa, "rezumat_luna", lambda cs, cpub, tid, an, luna: _rz(1300.0))
    assert pa.pregateste(None, cp, TID, 2099, 10) == {"ok": False, "cod": "DEPASITA"}
    monkeypatch.setattr(pa, "rezumat_luna", lambda cs, cpub, tid, an, luna: _rz(1000.0))
    assert pa.pregateste(None, cp, TID, 2099, 10)["ok"] is True


def test_314_ciorna_n_are_amprenta_iar_aprobata_fara_amprenta_e_depasita(cp):
    pa.salveaza_poveste(cp, TID, 2099, 11, "Ciornă.", status="ciorna", amprenta="x")
    with cp.cursor() as cur:
        cur.execute("SELECT cifre_amprenta FROM public.pachet_povestea WHERE tenant_id = %s AND an = 2099 AND luna = 11", (TID,))
        assert cur.fetchone()[0] is None
        cur.execute("UPDATE public.pachet_povestea SET status = 'aprobat' WHERE tenant_id = %s AND an = 2099 AND luna = 11", (TID,))
    assert pa.get_poveste(cp, TID, 2099, 11, rz=_rz(1000.0))["depasita"] is True, "aprobată înainte de amprentă: nu se poate ști"
