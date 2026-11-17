# -*- coding: utf-8 -*-
"""[17.5-J] Probele nonvizuale ale corecțiilor AC109, AC134, AC135, AC139 (comanda 17.5-J pct.4.5), pe date sintetice create în test:
nu scriu pe firmele de probă și nu cer server. AC109: baza CM propusă (calcul, defalcare, fără state, trecere între ani, tranzacția
deținută de use-case). AC134: precompletarea declarantului D114 (gol -> din Date firmă; valoare existentă -> păstrată).
AC135: D177 neaplicabil numai la micro. AC139: avertismentul IC numără numai facturile fără operațiune D301 legată."""
import inspect
import json
import os
import re
import subprocess

from core import baza_cm, control_fiscal_api as cf, d301, repo_d301, salariati_api, uc_tenants

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOTIV_D177 = ("D177 nu se datorează — Regimul fiscal declară firma pe micro, iar D177 e redirecționarea impozitului pe profit "
              "(redirecționarea de la micro e abrogată din 2024, art. 56 alin. (2^5)). Dacă firma a ieșit din regimul micro, "
              "corectează Regimul fiscal la Date firmă.")


# ---------------------------------------------------------------- AC135
def test_ac135_d177_neaplicabil_la_micro_cu_motivul_exact_si_nu_la_profit():
    """MUTAȚIE: linia `neap.setdefault("d177", …)` scoasă -> micro rămâne fără D177 -> pică."""
    micro = cf.neaplicabile_selector({"tip_firma": "srl", "regim_fiscal": "micro"})
    assert micro["d177"] == MOTIV_D177 and "d101" in micro, micro
    for regim in ("profit", "", None):
        neap = cf.neaplicabile_selector({"tip_firma": "srl", "regim_fiscal": regim})
        assert "d177" not in neap, (regim, neap)


# ---------------------------------------------------------------- AC109
def _stat(brut, cm_zile=0):
    return {"brut": brut, "cm_zile": cm_zile}


def test_ac109_baza_din_recalcul_defalcata_pe_luni_si_insumata_la_total(monkeypatch):
    """Data de început 19.10.2026 -> lunile încheiate aprilie–septembrie 2026; lunile fără stat emis vin din recalcul (sursa se spune pe lună)."""
    luni = baza_cm.luni_anterioare(2026, 10)
    assert luni[0] == (2026, 4) and luni[-1] == (2026, 9)
    recalc = {l: _stat(5000.0) for l in luni}
    monkeypatch.setattr(baza_cm, "culege", lambda conn, schema, sid, l: ({}, recalc))
    import datetime
    r = salariati_api.baza_cm_propusa(object(), "x", 1, datetime.date(2026, 10, 19))
    assert r["venit"] == "30000.00" and r["prima_luna"] == "2026-04-01" and r["ultima_luna"] == "2026-09-01"
    assert [x[2] for x in r["venituri_lunare"]] == ["2026-%02d-01" % m for m in range(4, 10)]
    assert sum(float(x[0]) for x in r["venituri_lunare"]) == 30000.0
    assert sum(x[1] for x in r["venituri_lunare"]) == r["zile"] and r["zile"] > 100
    assert {x["sursa"] for x in r["surse"]} == {"recalculata"}


def test_ac109_stat_emis_castiga_peste_recalcul_si_sursa_se_spune(monkeypatch):
    luni = baza_cm.luni_anterioare(2026, 10)
    emise = {luni[0]: _stat(7000.0)}
    recalc = {l: _stat(5000.0) for l in luni}
    monkeypatch.setattr(baza_cm, "culege", lambda conn, schema, sid, l: (emise, recalc))
    import datetime
    r = salariati_api.baza_cm_propusa(object(), "x", 1, datetime.date(2026, 10, 19))
    assert r["venituri_lunare"][0][0] == "7000.00", r
    assert [x["sursa"] for x in r["surse"]] == ["emisa"] + ["recalculata"] * 5


def test_ac109_perioada_peste_ani_si_luna_in_cm_integral_nu_intra_in_medie(monkeypatch):
    """Data de început februarie 2026 -> august 2025 … ianuarie 2026; o lună integral în CM nu are zile lucrate și nu apare în defalcare."""
    import datetime
    from core import scadente
    luni = baza_cm.luni_anterioare(2026, 2)
    assert luni == [(2025, 8), (2025, 9), (2025, 10), (2025, 11), (2025, 12), (2026, 1)]
    recalc = {l: _stat(4000.0) for l in luni}
    recalc[(2025, 10)] = _stat(0.0, cm_zile=scadente.zile_lucratoare_luna(2025, 10))
    monkeypatch.setattr(baza_cm, "culege", lambda conn, schema, sid, l: ({}, recalc))
    r = salariati_api.baza_cm_propusa(object(), "x", 1, datetime.date(2026, 2, 3))
    assert [x[2] for x in r["venituri_lunare"]] == ["2025-08-01", "2025-09-01", "2025-11-01", "2025-12-01", "2026-01-01"]
    assert r["prima_luna"] == "2025-08-01" and r["ultima_luna"] == "2026-01-01"


def test_ac109_fara_nicio_luna_cu_date_nu_se_propune_nimic(monkeypatch):
    import datetime
    monkeypatch.setattr(baza_cm, "culege", lambda conn, schema, sid, l: ({}, {}))
    assert salariati_api.baza_cm_propusa(object(), "x", 1, datetime.date(2026, 10, 19)) is None


def test_ac109_tranzactia_e_a_use_case_ului_nu_a_rutei():
    """Use-case-ul deschide conexiunea; ruta din main.py nu; `core/baza_cm.py` rămâne neatins (sursa unică) și nu primește funcții noi."""
    import main
    assert "get_conn" in inspect.getsource(uc_tenants.cm_baza_propusa)
    assert "get_conn" not in inspect.getsource(main.cm_baza_propusa)
    assert [n for n in dir(baza_cm) if n.startswith(("propune", "baza_propusa"))] == []


# ---------------------------------------------------------------- AC134
def _precompleteaza_d114(d114, firma_date):
    """Rulează în node exact blocul `_pune114` din declaratii.js::randeazaFormularD114 (extras din sursă), pe datele date."""
    src = open(os.path.join(RAD, "static/js/ecrane/declaratii.js"), encoding="utf-8").read()
    i = src.index("  const _fd = S.firmaDate || {};")
    j = src.index("  const ct = d.contracte || [];", i)
    prog = "const S = {firmaDate: %s}; const d = %s;\n%s\nconsole.log(JSON.stringify(d));" % (json.dumps(firma_date), json.dumps(d114), src[i:j])
    return json.loads(subprocess.run(["node", "-e", prog], capture_output=True, text=True, check=True).stdout)


FIRMA = {"cui": "401002001", "nume": "Comert Stoc SRL", "adresa": "Str. Test 1", "oras": "Cluj-Napoca", "judet": "Cluj"}


def test_ac134_campurile_goale_se_precompleteaza_din_date_firma():
    d = _precompleteaza_d114({"contracte": []}, FIRMA)
    assert d["cif_declarant"] == "401002001" and d["den_declarant"] == "Comert Stoc SRL"
    assert d["adresa_declarant"] == "Str. Test 1, Cluj-Napoca, Cluj"


def test_ac134_valoarea_existenta_nu_se_suprascrie_nici_cu_date_salvate():
    d = _precompleteaza_d114({"cif_declarant": "RO999", "den_declarant": "Alta Denumire", "adresa_declarant": "Adresa mea"}, FIRMA)
    assert (d["cif_declarant"], d["den_declarant"], d["adresa_declarant"]) == ("RO999", "Alta Denumire", "Adresa mea")
    # un câmp gol alături de unul completat: numai golul se completează
    d = _precompleteaza_d114({"cif_declarant": "RO999", "den_declarant": "", "adresa_declarant": "   "}, FIRMA)
    assert d["cif_declarant"] == "RO999" and d["den_declarant"] == "Comert Stoc SRL" and d["adresa_declarant"].startswith("Str. Test 1")


# ---------------------------------------------------------------- AC139
class _Cur:
    def __init__(self, randuri):
        self.randuri = randuri

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class _Conn:
    def cursor(self, **kw):
        return _Cur([])


def _avertismente_d301(monkeypatch, facturi_ic, legate):
    """Rulează `d301.genereaza` pe date sintetice (o operațiune validă, profil complet) și întoarce avertismentele IC ale rezultatului."""
    import datetime
    from core import control_incrucisat
    from core.common import Perioada
    prof = {"nume": "Test SRL", "cui": "401002001", "adresa": "Str. Test 1", "oras": "Cluj", "judet": "Cluj", "banca": "B", "iban": "RO49AAAA1B31007593840000",
            "declarant_nume": "Pop", "declarant_prenume": "Ion", "declarant_functie": "Administrator", "inreg_art317": "1"}
    ops = [{"tip": 1, "nr_doc": "F1", "data_doc": datetime.date(2026, 6, 10), "val_valuta": 1000, "tip_valuta": "EUR", "curs": 5, "tva": 1050}]
    monkeypatch.setattr(d301, "pull", lambda conn, schema, perioada: (prof, ops))
    monkeypatch.setattr(control_incrucisat, "facturi_ic", lambda conn, schema, a, b, cu_servicii=False: {"primita": list(facturi_ic), "emisa": []})
    monkeypatch.setattr(repo_d301, "select_facturi_legate", lambda cur: [{"factura_id": i} for i in legate])
    captat = {}
    real = d301.calcul_d301

    def spion(*a, **k):
        r = real(*a, **k)
        captat["res"] = r
        return r
    monkeypatch.setattr(d301, "calcul_d301", spion)
    try:
        d301.genereaza(_Conn(), "x", Perioada(2026, luna=6))
    except Exception:   # noqa: BLE001 — pașii de după avertisment (validator, reconciliere) nu fac obiectul probei
        pass
    return [a for a in captat["res"].avertismente if "nu automat din facturi" in a]


def _fact(i):
    return {"id": i, "numar": "F%d" % i, "tert_nume": "Furnizor UE", "total": 1000, "tva": 0}


def test_ac139_facturile_legate_de_operatiuni_nu_mai_dau_avertismentul(monkeypatch):
    """MUTAȚIE: filtrul `not in _legate` scos -> avertismentul apare cu 2 achiziții -> pică."""
    assert _avertismente_d301(monkeypatch, [_fact(1), _fact(2)], legate=[1, 2]) == []


def test_ac139_cu_o_factura_nelegata_avertismentul_ramane_cu_numarul_ei(monkeypatch):
    av = _avertismente_d301(monkeypatch, [_fact(1), _fact(2), _fact(3)], legate=[1, 2])
    assert len(av) == 1 and "1 achiziție IC înregistrată" in av[0], av
    av = _avertismente_d301(monkeypatch, [_fact(1), _fact(2)], legate=[])
    assert len(av) == 1 and "2 achiziții IC înregistrate" in av[0], av
