# -*- coding: utf-8 -*-
"""GĂRZI R1 — registrul unic de parametri fiscali (`common.COTE`), comanda Costin 08.10.2026 (verbatim în DECIZII).

pct.1: „Registrul existent COTE devine acest registru (se extinde, nu se face unul paralel); mecanismul `ancoreaza` se pliază pe el.”
Fiecare intrare: valoarea, temeiul, perioada (de la / până la) și starea (propus / verificat / aprobat, cu cine și când).
pct.4: „în registru intră doar propunerile cu verdictul APROB din fișierul de verificare al arhitectului”.
pct.7: exportul integral, în formatul `verif_temeiuri.json`; „până la verdict, starea intrărilor rămâne «propus»”.
"""
import ast
import io
import json
import os
import subprocess
import sys
from datetime import date
from decimal import Decimal

import pytest

from core import common
from core import registru_fiscal as rf

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: Câmpurile unei intrări din fișierul de verificare al arhitectului (`verif_temeiuri.json`, 01.10.2026), citite din el pe 10.10.2026:
#: parametru, unde_in_cod, folosire_in_iconta, verdict, temei_final, atom, verbatim, valabilitate.
CAMPURI_VERIFICARE = {"parametru", "unde_in_cod", "folosire_in_iconta", "verdict", "temei_final", "atom", "verbatim", "valabilitate"}


def _nume_ancorate_in_sursa():
    """Numele date lui `ancoreaza(...)` în sursa fiecărui modul care ancorează (din AST, primul argument literal)."""
    out = set()
    for m in common.module_care_ancoreaza() + ["common"]:
        arb = ast.parse(io.open(os.path.join(RAD, "core", m + ".py"), encoding="utf-8").read())
        nume = {"ancoreaza"} | {a.asname for n in ast.walk(arb) if isinstance(n, ast.ImportFrom)
                                for a in n.names if a.name == "ancoreaza" and a.asname}
        for n in ast.walk(arb):
            if (isinstance(n, ast.Call) and getattr(n.func, "attr", getattr(n.func, "id", None)) in nume and n.args
                    and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str)):
                out.add(n.args[0].value)
    return out


def test_un_singur_registru_fiecare_constanta_ancorata_e_intrare_in_COTE():
    """„se extinde, nu se face unul paralel”: fiecare `ancoreaza("<modul>.<NUME>", …)` din cod e o intrare în `COTE`, cu data de la
    care e valabilă; al doilea dicționar (`CONSTANTE_ANCORATE`, până la 10.10.2026) nu mai există.
    MUTAȚIE: `ancoreaza` întoarce valoarea fără `COTE[nume] = …` -> pică."""
    assert not hasattr(common, "CONSTANTE_ANCORATE"), "al doilea dicționar a revenit"
    din_sursa = _nume_ancorate_in_sursa()
    cote = common.registru_complet()
    assert len(din_sursa) >= 30, din_sursa                         # măsurat 10.10.2026: 32
    lipsa = sorted(din_sursa - set(cote))
    assert not lipsa, "ancorate în cod, absente din registru: %s" % lipsa
    for k in din_sursa:
        (din, valoare, temei), = cote[k]
        assert isinstance(din, date) and din == temei.data_in, k
        assert getattr(sys.modules["core." + k.split(".")[0]], k.split(".", 1)[1]) == valoare, k


def test_registrul_e_complet_si_intr_un_interpretor_proaspat():
    """Constantele ancorate intră la importul modulului lor: un cititor al registrului întreg nu are voie să depindă de cine a importat
    ce înaintea lui. Interpretor PROASPĂT (în suită, `conftest` a încărcat deja tot). MUTAȚIE: `registru_complet` fără importuri ->
    în interpretorul proaspăt registrul are numai `common.PLAFON_CRESA_BAZA` -> pică."""
    cod = ("from core import common\n"
           "c = common.registru_complet()\n"
           "print(sum(1 for k in c if '.' in k))\n")
    r = subprocess.run([sys.executable, "-c", cod], cwd=RAD, capture_output=True, text=True, timeout=300)
    assert r.stdout.split() == [str(len(_nume_ancorate_in_sursa()))], (r.stdout, r.stderr[-800:])


def test_starea_se_deriva_aprobat_verificat_propus():
    """aprobat = verdictul APROB al arhitectului (cine și când din verdict); verificat = citat confirmat la sursă, cu cine și când;
    propus = orice altceva. MUTAȚIE: verdictul ignorat în `stare` -> intrarea aprobată iese „verificat” -> pică."""
    t_ver = common.Temei("CF", art="1", data_in="2020-01-01", text_citat="x", verificat_la="2026-10-01", de_cine="Code/Costin")
    t_fara = common.Temei("CF", art="1", data_in="2020-01-01", text_citat="x")
    ver = {rf.parametru("k", date(2020, 1, 1)): {"verdict": "APROB", "de_cine": "arhitect", "data": "2026-10-09"}}
    assert rf.stare("k", date(2020, 1, 1), t_ver, ver) == {"stare": "aprobat", "de_cine": "arhitect", "la": "2026-10-09"}
    assert rf.stare("k", date(2020, 1, 1), t_ver, {}) == {"stare": "verificat", "de_cine": "Code/Costin", "la": "2026-10-01"}
    assert rf.stare("k", date(2020, 1, 1), t_fara, {}) == {"stare": "propus", "de_cine": None, "la": None}
    assert rf.stare("k", date(2021, 1, 1), t_ver, ver)["stare"] == "verificat"     # verdictul e pe intrare (cheie + dată)


def test_numai_verdictul_APROB_intra_si_numai_din_fisierul_dat(tmp_path):
    """pct.4: CORECTEAZA / RESPINGE / lipsă nu aprobă nimic. MUTAȚIE: filtrul `verdict == APROB` scos -> CORECTEAZA aprobă -> pică."""
    f = tmp_path / "verdicte.json"
    f.write_text(json.dumps({"data": "2026-10-09", "de_cine": "arhitect", "temeiuri": [
        {"parametru": "COTE/a@2020-01-01", "verdict": "APROB"},
        {"parametru": "COTE/b@2020-01-01", "verdict": "CORECTEAZA"},
        {"parametru": "COTE/c@2020-01-01", "verdict": "RESPINGE"},
        {"parametru": "COTE/d@2020-01-01"}]}), encoding="utf-8")
    assert rf.verdicte(str(f)) == {"COTE/a@2020-01-01": {"verdict": "APROB", "de_cine": "arhitect", "data": "2026-10-09"}}
    assert rf.verdicte(str(tmp_path / "lipsa.json")) == {}


def test_exportul_are_forma_fisierului_de_verificare_si_tot_registrul():
    """pct.7: tot registrul, într-un fișier, în formatul `verif_temeiuri.json`, cu verdictul gol de completat; până la verdict, starea
    e „propus” sau „verificat”, niciodată „aprobat”. MUTAȚIE: constantele ancorate lăsate afară din export -> pică pe număr."""
    d = rf.exporta(ver={})
    cote = common.registru_complet()
    assert len(d["temeiuri"]) == sum(len(v) for v in cote.values())
    for t in d["temeiuri"]:
        assert CAMPURI_VERIFICARE <= set(t), set(CAMPURI_VERIFICARE) - set(t)
        assert t["verdict"] is None and t["stare"] in ("propus", "verificat"), t["parametru"]
        assert t["folosire_in_iconta"], "intrare fără etichetă: %s" % t["parametru"]
    pe_param = {t["parametru"]: t for t in d["temeiuri"]}
    pf = pe_param["COTE/casa.PLAFON_PF@2023-12-15"]
    assert pf["valoare"] == str(Decimal("10000")) and pf["unde_in_cod"].startswith("core/casa.py PLAFON_PF")
    assert pf["valabilitate"] == "2023-12-15 – în vigoare"
    # o cheie cu istoric: predecesorul are „până la” derivat din succesor (ziua dinaintea lui)
    tva = sorted((t for t in d["temeiuri"] if t["parametru"].startswith("COTE/tva_standard@")), key=lambda t: t["parametru"])
    assert len(tva) >= 2 and not tva[-2]["valabilitate"].endswith("în vigoare") and tva[-1]["valabilitate"].endswith("în vigoare")
    assert d["sumar"]["aprobat"] == 0 and sum(d["sumar"].values()) == len(d["temeiuri"])


@pytest.mark.parametrize("nume", sorted(k for k in common.registru_complet() if "." in k))
def test_constanta_ancorata_se_citeste_prin_cota_dupa_data(nume):
    """O intrare ancorată e o intrare ca oricare: `cota(nume, data)` o întoarce de la `data_in` încoace și refuză înainte (perioadă
    nedocumentată), ca la cheile istorice."""
    din, valoare, _t = common.COTE[nume][0]
    assert common.cota(nume, din)[0] == valoare
    with pytest.raises(common.PerioadaIndisponibila):
        common.cota(nume, date.fromordinal(din.toordinal() - 1))
