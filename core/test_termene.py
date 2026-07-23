"""
core/test_termene.py — plasa de regresie pentru scadentele viitoare (termene_api).
Pana la 23.07.2026 modulul avea ZERO teste; ecranul Termene reimplementa maparea
"cine ce datoreaza" fara acoperire (vezi CHECKLIST_BROWSER poz. 3). Aici o construim.
"""
import datetime
from core import termene_api
from core import control_fiscal_api

V_TVA_LUNAR = {"regim_fiscal": "profit", "platitor_tva": True, "tip_decont": "lunar",
               "operatiuni_ic": False, "partida_simpla": False}


def _tips(items):
    return {d["tip"] for d in items}


# ---------- T1: firma neevaluata NU dispare tacut (gri cu temei) ----------

def test_portofoliu_propaga_neevaluate():
    """portofoliu returneaza canalul `neevaluate` intact (gri cu temei, doctrina 23.07)."""
    neeval = [{"tenant_id": 7, "nume": "ACME SRL",
               "cauza": "Nu am putut evalua această firmă (OperationalError)."}]
    r = termene_api.portofoliu([], azi=datetime.date(2026, 7, 23), neevaluate=neeval)
    assert r["neevaluate"] == neeval
    assert r["grupuri"] == []           # nicio scadenta reala
    assert r["urmatoarea"] is None


def test_portofoliu_neevaluate_lipsa_default_gol():
    """Fara neevaluate -> lista goala, nu None (shape stabil pentru UI)."""
    r = termene_api.portofoliu([], azi=datetime.date(2026, 7, 23))
    assert r["neevaluate"] == []


# ---------- T2: consolidare — Termene refoloseste motorul unic; nu mai sub-raporteaza ----------

def test_termene_emite_d394_d406_platitor():
    """Corectie de sub-raportare: inainte de consolidare Termene NU emitea D394/D406 deloc."""
    out = termene_api.termene_firma(V_TVA_LUNAR, are_salariati=False, depuse=set(),
                                    azi=datetime.date(2026, 7, 23))
    tips = _tips(out)
    assert "d300" in tips
    assert "d394" in tips
    assert "d406" in tips


def test_termene_emite_d101_profit_in_fereastra():
    """D101 (profit, anual 2025) termen 25.03.2026 -> fereastra [01.02, 02.04] il prinde (venea din motor)."""
    v = {"regim_fiscal": "profit", "platitor_tva": False, "tip_decont": None,
         "operatiuni_ic": False, "partida_simpla": False}
    out = termene_api.termene_firma(v, are_salariati=False, depuse=set(), azi=datetime.date(2026, 2, 1))
    assert any(d["tip"] == "d101" and d["an"] == 2025 for d in out)


def test_termene_respecta_depuse():
    """Depunerea (tip, an, luna) scoate obligatia din Termene (filtru pe cheia canonica lowercase)."""
    out = termene_api.termene_firma(V_TVA_LUNAR, are_salariati=False,
                                    depuse={("d300", 2026, 6)}, azi=datetime.date(2026, 7, 23))
    assert ("d300", 2026, 6) not in {(d["tip"], d["an"], d["luna"]) for d in out}


# ---------- T3: D390 la neplatitor cu IC = gri (neclar), nu scadenta ferma (emergent din T2) ----------

def test_termene_d390_neplatitor_ic_nu_e_scadenta():
    """Termene adopta verdictul semaforului: D390 la neplatitor cu IC e gri (art.317 necunoscut),
    intra in `neclar`, NU in `datorate` -> nu apare ca scadenta ferma. Nu-l fabrica, nu-l reafiseaza."""
    v = {"regim_fiscal": "micro", "platitor_tva": False, "tip_decont": None,
         "operatiuni_ic": True, "partida_simpla": False}
    azi = datetime.date(2026, 7, 23)
    out = termene_api.termene_firma(v, are_salariati=False, depuse=set(), azi=azi)
    assert "d390" not in _tips(out)                         # NU fabricat ca termen ferm
    rez = control_fiscal_api.obligatii_datorate(v, are_salariati=False, azi=azi,
                                                jos=azi, sus_zile=termene_api.ORIZONT_ZILE)
    assert any(n["tip"] == "d390" for n in rez["neclar"])   # e gri in motor (adoptat, nu inventat)


def test_termene_pfa_fara_declaratii_persoana_juridica():
    """PFA (partida simpla) nu primeste D100/D101/D406 in Termene (motorul le pune neaplicabile)."""
    v = {"regim_fiscal": None, "platitor_tva": False, "tip_decont": None,
         "operatiuni_ic": False, "partida_simpla": True}
    out = termene_api.termene_firma(v, are_salariati=False, depuse=set(), azi=datetime.date(2026, 7, 23))
    assert not ({"d100", "d101", "d406"} & _tips(out))
