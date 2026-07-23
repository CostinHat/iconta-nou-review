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


# ---------- T4: edge decembrie — perioadele anului urmator se genereaza (an+1) ----------

def test_termene_decembrie_15_cross_an_prin_perioada_curenta():
    """15.12 -> fereastra [15.12.2026, 13.02.2027]: perioada dec-2026 (termen ian-2027) apare;
    perioada ian-2027 (termen 25.02) e in AFARA -> inca niciun an 2027."""
    out = termene_api.termene_firma(V_TVA_LUNAR, are_salariati=False, depuse=set(),
                                    azi=datetime.date(2026, 12, 15))
    assert any(d["tip"] == "d300" and d["an"] == 2026 and d["luna"] == 12 for d in out)
    assert all(d["an"] <= 2026 for d in out)


def test_termene_decembrie_28_trage_perioada_an_nou():
    """28.12 -> fereastra [28.12.2026, 26.02.2027]: perioada ian-2027 (D300 termen 25.02.2027) INTRA
    -> dovada ca perioadele an+1 se genereaza (bug-ul vechi an=azi.year le rata)."""
    out = termene_api.termene_firma(V_TVA_LUNAR, are_salariati=False, depuse=set(),
                                    azi=datetime.date(2026, 12, 28))
    assert any(d["tip"] == "d300" and d["an"] == 2027 and d["luna"] == 1 for d in out)


# ---------- D390 pe FAPT lunar (termene, privire inainte: afisam pe incertitudine) ----------
# Cost asimetric: un termen ascuns care se materializeaza = amenda -> inainte afisam pe incertitudine.

_V_IC = {"regim_fiscal": "profit", "platitor_tva": True, "tip_decont": "lunar",
         "operatiuni_ic": True, "partida_simpla": False}

def test_termene_d390_luna_deschisa_se_afiseaza():
    """Luna DESCHISA (fapt None) -> D390 se AFISEAZA in termene (nu putem exclude operatiuni pana la final)."""
    azi = datetime.date(2026, 7, 23)
    fapt = lambda a, m: None if (a, m) == (2026, 7) else False   # iulie deschisa; iunie inchisa fara IC
    out = termene_api.termene_firma(_V_IC, are_salariati=False, depuse=set(), azi=azi, d390_fapt=fapt)
    d390_luni = {(d["an"], d["luna"]) for d in out if d["tip"] == "d390"}
    assert (2026, 7) in d390_luni          # deschisa -> afisata (incertitudine)
    assert (2026, 6) not in d390_luni      # inchisa fara operatiuni -> nu apare (nu e scadenta)

def test_termene_d390_luna_inchisa_cu_operatiuni_apare():
    azi = datetime.date(2026, 7, 23)
    fapt = lambda a, m: True if (a, m) == (2026, 6) else (None if (a, m) == (2026, 7) else False)
    out = termene_api.termene_firma(_V_IC, are_salariati=False, depuse=set(), azi=azi, d390_fapt=fapt)
    d390_luni = {(d["an"], d["luna"]) for d in out if d["tip"] == "d390"}
    assert (2026, 6) in d390_luni          # inchisa cu operatiuni -> datorata

def test_termene_d390_fara_fapt_pe_bifa():
    # d390_fapt=None -> bifa decide (compat); D390 pe lunile din fereastra
    azi = datetime.date(2026, 7, 23)
    out = termene_api.termene_firma(_V_IC, are_salariati=False, depuse=set(), azi=azi)
    assert any(d["tip"] == "d390" for d in out)


# ---------- §4: marginirea la inregistrarea TVA (inchide asimetria cu semaforul) ----------

def test_termene_marginire_inregistrare_tva_in_fereastra():
    """Firma inregistrata TVA in interiorul ferestrei -> perioadele DINAINTE de inregistrare nu apar
    (motorul margineste D300/D394/D406 la data ANAF, ca semaforul). Vezi §4 / DECIZII 23.07 B1."""
    azi = datetime.date(2026, 7, 23)                       # fereastra [23.07, 21.09]
    v = {"regim_fiscal": "profit", "platitor_tva": True, "tip_decont": "lunar",
         "operatiuni_ic": False, "partida_simpla": False,
         "tva_data_inceput": datetime.date(2026, 8, 1)}    # inregistrata TVA de la 01.08.2026
    d300 = {(d["an"], d["luna"]) for d in
            termene_api.termene_firma(v, False, set(), azi) if d["tip"] == "d300"}
    # fara margine: iunie (termen 27.07) ar aparea
    d300_nemarginit = {(d["an"], d["luna"]) for d in
                       termene_api.termene_firma({**v, "tva_data_inceput": None}, False, set(), azi)
                       if d["tip"] == "d300"}
    assert (2026, 6) in d300_nemarginit    # fara margine iunie apare
    assert (2026, 6) not in d300           # cu inreg. 01.08 -> iunie (dinainte) dispare
    assert (2026, 7) not in d300           # iulie tot dinainte de inregistrare -> dispare


def test_termene_d390_fapt_primeaza_peste_flag_false():
    """Item 1 in termene: luna inchisa cu operatiuni (fapt True) -> D390 apare desi operatiuni_ic=False."""
    azi = datetime.date(2026, 7, 23)
    v = {"regim_fiscal": "profit", "platitor_tva": True, "tip_decont": "lunar",
         "operatiuni_ic": False, "partida_simpla": False}
    fapt = lambda a, m: True if (a, m) == (2026, 6) else (None if (a, m) == (2026, 7) else False)
    out = termene_api.termene_firma(v, False, set(), azi, d390_fapt=fapt)
    assert (2026, 6) in {(d["an"], d["luna"]) for d in out if d["tip"] == "d390"}
