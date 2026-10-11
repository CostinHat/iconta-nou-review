# -*- coding: utf-8 -*-
"""GĂRZI R2b — amprenta fiecărui apel de generator din suită (`scripts/amprente_suita.py`, comanda Costin 08.10.2026, verbatim în DECIZII;
pasul R2b din TESTE.md). Lista emițătoarelor e completă și derivată din sursă, învelișul nu schimbă rezultatul, amprenta e cea normalizată
a R2a, iar pluginul consemnează pe testul care a chemat — și numai când e cerut."""
import json
import os
import re
import subprocess
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAD, "scripts"))

import amprente_suita as A  # noqa: E402


def test_emitatoarele_sunt_toate_generatoarele_de_declaratii():
    """Fiecare modul la care trimite dispecerul declarațiilor (`declaratii_api`: `<modul>.genereaza`, bilanțul prin `bilant_api` ->
    `bilant.xml_s1005`) are un emițător în listă. MUTAȚIE: `d300` pus în `NU_EMIT` -> pică; scanul restrâns la numele `build_xml` -> pică
    pe bilanț."""
    em = A.emitatoare()
    assert len(em) >= 50, len(em)                                          # anti-vacuu
    module = {m for m, _ in em}
    src = open(os.path.join(RAD, "core", "declaratii_api.py"), encoding="utf-8").read()
    dispecer = set(re.findall(r"return (d\d+[a-z_]*)\.genereaza\(", src))
    assert len(dispecer) >= 30, dispecer                                   # anti-vacuu: dispecerul e citit
    lipsa = sorted(m for m in dispecer if "core." + m not in module)
    assert lipsa == [], lipsa
    assert ("core.bilant", "xml_s1005") in em
    assert ("core.amef_import", "extrage_xml") not in em                   # cititorul AMEF nu e generator


def test_invelisul_intoarce_acelasi_rezultat_si_consemneaza_amprenta_normalizata():
    """Două generări care diferă numai prin data generării: aceeași amprentă, cea a R2a; consemnată pe testul curent, în ordine.
    MUTAȚIE: amprenta pe XML-ul brut -> pică; rezultatul neîntors -> pică."""
    x1 = '<?xml version="1.0"?><D300 data_generare="2026-10-10 10:00" R9_1="100"/>'
    x2 = '<?xml version="1.0"?><D300 data_generare="2026-10-11 09:00" R9_1="100"/>'
    f = A.inveleste(lambda x: x, "core.dx.build_xml")
    vechi = dict(A.STARE)
    A.STARE.update(test="t::unu", apeluri={})
    try:
        assert f(x1) == x1 and f(x2.encode()) == x2.encode()
        assert A.STARE["apeluri"] == {"t::unu": [["core.dx.build_xml", A._amprenta(x1)], ["core.dx.build_xml", A._amprenta(x1)]]}
        assert f(123) == 123 and A.STARE["apeluri"]["t::unu"][-1] == ["core.dx.build_xml", "tip:int"]
    finally:
        A.STARE.clear()
        A.STARE.update(vechi)


def test_pluginul_consemneaza_pe_test_numai_cand_e_cerut(tmp_path):
    """Cap-coadă, într-un pytest separat: cu `-p amprente_suita` și variabila, apelul unui emițător real (REGES `_msg`, importat pe nume)
    ajunge în artefact pe nodul testului; fără variabilă, nimic nu e învelit și nu se scrie nimic. MUTAȚIE: `activeaza` care nu mai
    pune învelișul pe modul -> pică; testul curent nesetat la `setup` -> pică."""
    t = tmp_path / "test_unul.py"
    t.write_text("from core.reges_client import _msg\n\ndef test_x():\n    assert _msg('T', '<H/>', '<C/>').startswith('<?xml')\n")
    iesire = tmp_path / "a.json"
    env = {k: v for k, v in os.environ.items() if k != A.VAR}       # suita poate rula ea însăși sub plugin: variabila nu se moștenește
    env.update(PYTHONPATH=os.path.join(RAD, "scripts"), PYTHONDONTWRITEBYTECODE="1")
    cmd = [sys.executable, "-m", "pytest", "-q", "-p", "amprente_suita", "-p", "no:cacheprovider", str(t), "--rootdir", str(tmp_path)]
    r = subprocess.run(cmd, cwd=RAD, env=dict(env, ICONTA_AMPRENTE_SUITA=str(iesire)), capture_output=True, text=True, timeout=600)
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
    d = json.load(open(iesire, encoding="utf-8"))
    (nod, apeluri), = d["teste"].items()
    assert nod.endswith("test_unul.py::test_x") and [a[0] for a in apeluri] == ["core.reges_client._msg"], d["teste"]
    assert len(d["emitatoare"]) == len(A.emitatoare())
    os.remove(iesire)
    r = subprocess.run(cmd, cwd=RAD, env=env, capture_output=True, text=True, timeout=600)
    assert r.returncode == 0 and not iesire.exists() and "[amprente_suita]" not in r.stdout, r.stdout[-2000:]


def test_compararea_numeste_fiecare_test_diferit():
    """MUTAȚIE: testele care lipsesc într-una din rulări ignorate -> pică."""
    a = {"teste": {"t1": [["f", "a"]], "t2": [["f", "b"]]}}
    b = {"teste": {"t1": [["f", "a"]], "t2": [["f", "c"]], "t3": [["f", "d"]]}}
    assert A.compara(a, b) == [("t2", [["f", "b"]], [["f", "c"]]), ("t3", None, [["f", "d"]])]
    assert A.compara(a, a) == []


def test_mesajul_reges_are_aceeasi_amprenta_la_fiecare_trimitere(monkeypatch):
    """Antetul REGES poartă `uuid4` și ora trimiterii: două mesaje cu același corp au aceeași amprentă, un corp diferit alta (măsurat la
    R2b: singurele 3 amprente instabile între două rulări). Ora are precizie de o secundă — aici e forțată să difere la fiecare citire,
    altfel testul n-ar vedea `Timestamp` / `DataConsemnare`. MUTAȚIE: oricare din `MessageId` / `SessionId` / `Timestamp` /
    `DataConsemnare` scos din `_VOLATIL` -> pică."""
    from core import reges_client as R
    ore = ("2026-10-11T07:00:%02d.000Z" % i for i in range(60))
    monkeypatch.setattr(R, "_acum", lambda: next(ore))
    c = {"numar": "12", "data_contract": "2026-07-01", "data_inceput": "2026-07-06", "salariu": 4500, "cor": "251204"}
    ref = "0b7d9c4e-1f2a-4b3c-9d8e-7f6a5b4c3d2e"
    m1, m2 = (R.mesaj_adaugare_contract(c, ref, "a", "u") for _ in range(2))
    assert m1 != m2 and A.amprenta(m1) == A.amprenta(m2)
    assert A.amprenta(m1) != A.amprenta(R.mesaj_adaugare_contract(dict(c, salariu=4501), ref, "a", "u"))


def test_verdictul_e_pe_amprentele_distincte_nu_pe_testul_care_le_consemneaza():
    """Aceleași ieșiri mutate între teste (fixture de modul, recalculare condiționată) -> aceleași; o ieșire nouă sau dispărută -> numită.
    MUTAȚIE: amprentele numai-după ignorate -> pică."""
    a = {"teste": {"t1": [["f", "x"], ["g", "y"]], "t2": []}}
    mutat = {"teste": {"t2": [["f", "x"], ["g", "y"], ["f", "x"]]}}
    assert A.compara_distincte(a, mutat) == ([], [])
    assert A.compara(a, mutat) != []                                  # pe test se vede, dar nu e verdict
    nou = {"teste": {"t1": [["f", "x"], ["g", "z"]]}}
    assert A.compara_distincte(a, nou) == ([("g", "y")], [("g", "z")])
