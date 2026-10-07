# -*- coding: utf-8 -*-
"""GARD STRUCTURAL — cei trei apelanți care calculează salariul LUNII (statul de plată, D112, nota de salarii) trec
`calcul_salariu` ACELEAȘI intrări (retest Costin 07.10 seara, S1).

Clasa: un parametru adăugat la calcul și trecut numai de unii apelanți face fluturașul, declarația și nota să difere pentru
același salariat (R34, R86 — „a doua socoteală”). Găsită măsurând la S1: statul nu trecea `cadou_taxabil`, nota nu trecea
`functie_baza` (implicit True). Testul compară MULȚIMEA cuvintelor-cheie din cele trei apeluri: un parametru nou trecut într-un
singur loc îl pică. MUTAȚIE: `elemente_variabile=` scos din `stat_plata_api` -> pică.
"""
import ast
import io

APELANTI = ("core/stat_plata_api.py", "core/d112.py", "core/salarii_contare.py")


def _chei(cale):
    arbore = ast.parse(io.open(cale, encoding="utf-8").read())
    apeluri = [n for n in ast.walk(arbore) if isinstance(n, ast.Call) and getattr(n.func, "attr", None) == "calcul_salariu"]
    assert len(apeluri) == 1, "%s: %d apeluri calcul_salariu (așteptat 1)" % (cale, len(apeluri))
    return {k.arg for k in apeluri[0].keywords}


def test_cei_trei_apelanti_ai_lunii_trec_aceleasi_intrari():
    chei = {c: _chei(c) for c in APELANTI}
    toate = set().union(*chei.values())
    lipsa = {c: sorted(toate - k) for c, k in chei.items() if toate - k}
    assert not lipsa, "intrări trecute numai de unii apelanți: %r" % lipsa
    assert {"elemente_variabile", "venit_cm", "cadou_taxabil", "functie_baza"} <= toate
