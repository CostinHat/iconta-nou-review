# -*- coding: utf-8 -*-
"""GARD [06.09.2026, decizia lui Costin]: calea de plată online e ÎNCHISĂ și nu se redeschide tăcut.

**Decizia, verbatim**: *„Nu se integrează niciun procesator — fluxul real e transfer bancar,
confirmat din extras."* Și: *„R43, partea externă: se închide ca «nu se implementează», nu rămâne
deschisă la nesfârșit. Motivul: funcționalitatea nu corespunde fluxului de lucru real."*

**Ce păzește gardul, în ordinea în care contează:**
  1. **funcțiile refuză** — refuzul stă în `core/plati.py`, într-un singur loc, nu în rute;
  2. **niciun drum din interfață** nu duce acolo: butonul, handlerul lui și zona lui sunt scoase.
     *Un buton scos care lasă în urmă codul care îl ascultă e o cale care se redeschide cu o linie
     de HTML;*
  3. **refuzul numește fluxul REAL** — un „nu se poate" fără „iată cum se face" mută problema la om
     fără să-l ajute;
  4. **nu s-a desfăcut nicio evidență**: `platita_la` NU era al căii ăsteia, iar închiderea n-o
     atinge.

**CE NU PĂZEȘTE, declarat:** că o factură plătită prin bancă ajunge marcată încasată. Azi **nu
ajunge** — v. R174, deschisă chiar de măsurătoarea asta.
"""
import io
import os
import sys

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAD not in sys.path:
    sys.path.insert(0, _RAD)

from core import db as _db  # noqa: E402
from core import plati as _pl  # noqa: E402

_ECRAN = os.path.join(_RAD, "static", "js", "ecrane", "facturi_ecran.js")


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:  # noqa: BLE001
        return False


# ── 1. CALEA E ÎNCHISĂ, ÎNTR-UN SINGUR LOC ─────────────────────────────────────────────────────

def test_comutatorul_e_inchis_si_functiile_refuza():
    """Refuzul stă în modul, nu în rute: sunt două căi către `genereaza_link`, iar o poartă pusă
    doar în rută ar lăsa-o pe cealaltă deschisă."""
    assert _pl.CALEA_ONLINE_ACTIVA is False
    r1 = _pl.genereaza_link(None, "orice", 1, "http://x", tenant_id=1)
    r2 = _pl.confirma_plata(None, "orice", "pl_orice")
    assert r1.get("inchis") is True and r2.get("inchis") is True, (r1, r2)
    assert r1.get("eroare") and r2.get("eroare")


def test_refuzul_NUMESTE_fluxul_real():
    """Un «nu se poate» fără «iată cum se face» mută problema la om fără să-l ajute. Se cere ca
    motivul să numească amândouă capetele fluxului real: banca și extrasul."""
    m = _pl.MOTIV_INCHIS.lower()
    assert m.count("bancar") + m.count("banc") >= 1, _pl.MOTIV_INCHIS
    assert m.count("extras") >= 1, _pl.MOTIV_INCHIS
    assert len(_pl.MOTIV_INCHIS) > 80


def test_functiile_NU_scriu_nimic_cand_refuza():
    """Refuzul primește `conn=None`. Dacă vreuna ar încerca o interogare, ar crăpa — iar asta e
    chiar proba că nu atinge baza: nu se poate scrie printr-o conexiune care nu există."""
    assert _pl.genereaza_link(None, "s", 1, "u", tenant_id=1).get("inchis")
    assert _pl.confirma_plata(None, "s", "r").get("inchis")


# ── 2. NICIUN DRUM DIN INTERFAȚĂ ───────────────────────────────────────────────────────────────

def test_ecranul_nu_mai_are_niciun_drum_catre_plata_online():
    """Butonul, handlerul și zona — toate trei. Se cere NUMĂRUL zero, nu absența unui șir: `count`
    spune «de câte ori», iar zero e o afirmație mai tare decât «nu apare»."""
    src = io.open(_ECRAN, encoding="utf-8").read()
    assert src.count("fd-plata") == 0, "ecranul mai poartă butonul/zona de plată online"
    assert src.count("link-plata") == 0, "ecranul mai cheamă ruta de generare a linkului"


def test_ANTI_VACUU_ecranul_chiar_a_fost_citit():
    """Dacă fișierul s-ar muta, testul de mai sus ar trece pe un șir gol."""
    src = io.open(_ECRAN, encoding="utf-8").read()
    assert len(src) > 20000, "fișierul ecranului e prea mic — s-a citit altceva"
    assert src.count("fd-chitanta") > 0, "ancora de control lipsește — nu citesc ecranul facturii"


# ── 3. NU S-A DESFĂCUT NICIO EVIDENȚĂ ──────────────────────────────────────────────────────────

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_inchiderea_nu_a_atins_nicio_factura():
    """`platita_la` nu era al căii ăsteia. Măsurat la închidere: o singură factură îl poartă, pusă
    de calea CHITANȚEI, fără marcă de simulare; zero linkuri generate vreodată."""
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT schema_name FROM public.tenants ORDER BY id")
            scheme = [r[0] for r in cur.fetchall()]
            mock = ref = 0
            for s in scheme:
                try:
                    cur.execute("SELECT count(*) FILTER (WHERE plata_confirmata_de = 'mock'), "
                                "count(plata_ref) FROM %s.facturi" % s)
                    m, r = cur.fetchone()
                    mock += m
                    ref += r
                except Exception:  # noqa: BLE001
                    conn.rollback()
            cur.execute("SELECT count(*) FROM public.plata_referinte")
            perechi = cur.fetchone()[0]
    assert mock == 0, "%d facturi poartă marcă de SIMULARE — închiderea le-ar lăsa nedeclarate" % mock
    assert ref == 0, "%d facturi poartă un link de plată; calea e închisă, dar linkurile au rămas" % ref
    assert perechi == 0, "%d perechi în public.plata_referinte" % perechi
