# -*- coding: utf-8 -*-
"""[Regula 4 + Regula 6] TEST-GARDA: NICIO restanta fara premisa demonstrabila.

Motorul (control_fiscal_api) NU are voie sa emita un verdict de RESTANTA (lipsa) pe o perioada in care nu se
poate DEMONSTRA din date premisa obligatiei. Cand premisa e:
  - demonstrabil ABSENTA (luna inainte de o data de inregistrare TVA CUNOSCUTA) -> suprimare (nu apare deloc);
  - NECUNOSCUTA (platitor fara data TVA; an fara existenta/activitate demonstrabila) -> GRI "necunoscut
    declarat" cu motiv, NU restanta.

Acopera cele trei bug-uri reparate:
  A. platitor TVA cu tva_data_inceput NULL -> D300/D394/D406 restante pe trecut necunoscut = GRI, nu lipsa.
  B. D406 marginit ca D300/D394 (respecta data de inregistrare TVA cunoscuta).
  C. D100/D101/D406(neplatitor) pe un an fara existenta/activitate demonstrabila = GRI, nu restanta.

Doua paturi de teste: PURE (vectori sintetici, fara DB) pentru A/B; DB (firma grea tenant_017) pentru toate.
"""
import os
import datetime
import calendar
from datetime import date
import pytest

from core import control_fiscal_api as cf

AZI = date(2026, 8, 15)


# ============================================================
#  PUR (fara DB) — A + B pe vectori sintetici
# ============================================================
def test_A_platitor_fara_data_tva_gri_nu_restanta():
    """A: platitor cu tip_decont dar FARA tva_data_inceput -> nicio restanta D300/D394/D406; in loc, GRI
    'necunoscut declarat' per declaratie (nu pot demonstra de cand e inregistrata)."""
    v = {"platitor_tva": True, "tip_decont": "lunar", "regim_fiscal": "profit",
         "operatiuni_ic": False, "partida_simpla": False, "tva_data_inceput": None}
    rez = cf.declaratii_datorate(v, are_salariati=False, azi=AZI)
    lipsa, _, _, _ = cf._clasifica(rez["datorate"], {}, AZI)
    for t in ("d300", "d394", "d406"):
        assert not any(d["tip"] == t for d in lipsa), "%s emis ca restanta fara data TVA" % t
        gri_t = [n for n in rez["neclar"] if n["tip"] == t]
        assert gri_t, "%s fara GRI necunoscut" % t
        assert any("necunoscut declarat" in (n.get("motiv") or "") for n in gri_t), t


def test_B_D406_marginit_ca_d300_d394():
    """B: D406 respecta data de inregistrare TVA (marginit): lunile INAINTE de data cunoscuta sunt suprimate;
    de la data incolo D300/D394/D406 sunt datorate identic (aceeasi margine)."""
    v = {"platitor_tva": True, "tip_decont": "lunar", "regim_fiscal": "profit",
         "operatiuni_ic": False, "partida_simpla": False, "tva_data_inceput": "2026-05-01"}
    rez = cf.declaratii_datorate(v, are_salariati=False, azi=AZI)
    for t in ("d300", "d394", "d406"):
        luni = [(d["an"], d["luna"]) for d in rez["datorate"] if d["tip"] == t]
        assert luni, "%s nu emite nimic desi are data TVA" % t
        assert all((a, m) >= (2026, 5) for (a, m) in luni), "%s emis inainte de inreg TVA: %s" % (t, luni)


def test_B_D406_neplatitor_ramane_trimestrial():
    """Regresie: fix B (marginit la platitor) NU atinge neplatitorul -> D406 trimestrial neschimbat."""
    v = {"platitor_tva": False, "regim_fiscal": "micro", "operatiuni_ic": False,
         "partida_simpla": False, "tva_data_inceput": None}
    rez = cf.declaratii_datorate(v, are_salariati=False, azi=AZI)
    assert any(d["tip"] == "d406" for d in rez["datorate"])


# ============================================================
#  DB (firma grea tenant_017) — audit inline al premiselor
# ============================================================
def _incarca_db_env():
    cale = os.path.expanduser("~/.iconta/db.env")
    if not os.path.exists(cale):
        return False
    for l in open(cale, encoding="utf-8"):
        l = l.strip()
        if l and not l.startswith("#") and "=" in l:
            k, val = l.split("=", 1)
            os.environ.setdefault(k.strip(), val.strip().strip('"').strip("'"))
    return True


def _ultima_zi(an, luna):
    return date(an, luna, calendar.monthrange(an, luna)[1])


def _tva_inreg(vector):
    t = vector.get("tva_inceput")
    if hasattr(t, "year"):
        return t
    if isinstance(t, str) and len(t) >= 10:
        return date.fromisoformat(t[:10])
    return None


@pytest.mark.parametrize("cui_grea", ["98765438"])
def test_firma_grea_nicio_restanta_nesustinuta(cui_grea):
    """Regula 6: pe firma grea (toate cazurile grele intr-un an), FIECARE verdict de restanta emis de motor
    are premisa demonstrabila din date. Reproduce criteriul auditului per tip de declaratie."""
    if not _incarca_db_env():
        pytest.skip("fara db.env local")
    try:
        from core import db, control_incrucisat as ci, d390
        db.init_pool()
    except Exception as e:
        pytest.skip("fara DB: %s" % e)

    with db.get_conn() as cpub:
        with cpub.cursor() as c:
            c.execute("SELECT id, schema_name FROM public.tenants WHERE cui=%s ORDER BY id DESC LIMIT 1", (cui_grea,))
            r = c.fetchone()
    if not r:
        pytest.skip("firma grea (cui=%s) neseeduita" % cui_grea)
    tid, schema = r

    with db.get_conn(schema) as cs, db.get_conn() as cpub:
        with cs.cursor() as c:
            c.execute("SELECT platitor_tva, platitor_tva_anaf_inceput FROM firma_profil LIMIT 1")
            pr = c.fetchone()
        vector = {"platitor_tva": pr[0], "tva_inceput": pr[1]}
        ev = cf.evalueaza_firma(cs, cpub, tid, schema, azi=AZI, cu_reconciliere=False)

        plat = vector["platitor_tva"]
        tvi = _tva_inreg(vector)
        nesustinute = []
        for it in ev["lipsa"]:
            tip, an, luna = it["tip"], it["an"], it["luna"]
            if tip in ("d300", "d394") or (tip == "d406" and plat is True):
                ok = tvi is not None and tvi <= _ultima_zi(an, luna)
            elif tip in ("d100", "d101") or (tip == "d406" and plat is not True):
                ok = ci.existenta_firma_an(cs, schema, an)
            elif tip == "d112":
                ok = ci.are_salariat_activ_luna(cs, schema, an, luna)
            elif tip == "d390":
                ok = bool(d390.d390_are_operatiuni(cs, schema, an, luna, AZI))
            else:
                ok = True   # d205/d301 emise DOAR pe fapt (au premisa prin constructie)
            if not ok:
                nesustinute.append((tip, an, luna, it.get("perioada")))

        assert nesustinute == [], "restante nesustinute ramase: %s" % nesustinute
        # si: cel putin un verdict GRI "necunoscut declarat" trebuie sa apara (D100 T4-2025 fara activitate 2025)
        assert any("necunoscut declarat" in (n.get("motiv") or "") for n in ev["neclar"]), \
            "asteptam macar un GRI 'necunoscut declarat' pe firma grea"
