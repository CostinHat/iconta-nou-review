# -*- coding: utf-8 -*-
"""O eticheta de pe fluturas nu are voie sa numeasca un lucru si sa arate altul.

GARDA construita odata cu reparatia de prag 1 din 22.08.2026: randul "Deducere personala" tiparea
`deducere['total']`, care include si deducerile SUPLIMENTARE (CF art.77 alin.(4^1) tineri sub 26,
alin.(4^2) copii scolarizati). Pe un tanar la salariul minim din iulie 2026: eticheta zicea
"Deducere personala", cifra era 1.513,75, iar deducerea personala e 865,00.

CE APARA garda, dincolo de instanta: ca deducerile din calcul si randurile de pe hartie sa ramana in
corespondenta 1:1 pe NUME. Daca legea mai adauga o deducere si calculul o intoarce, dar hartia n-o
numeste, garda cade — nu asteapta sa observe cineva.
"""
import datetime

import pytest

from core import common as cmn
from core import salarizare
from core import stat_plata_api as sp

LA = datetime.date(2026, 7, 15)


def _brut_minim():
    v = cmn.salariu_minim_luna(LA)
    return float(v[0] if isinstance(v, tuple) else v)


def _rand_ca_din_stat(**kw):
    """Randul asa cum il produce `stat_plata` — cu componentele, nu doar totalul."""
    c = salarizare.calcul_salariu(_brut_minim(), la_data=LA, **kw)
    d = c["deducere"]
    return {"deducere": float(d["total"]), "deducere_baza": float(d["baza"]),
            "deducere_tineri": float(d["tineri"]), "deducere_copii": float(d["copii"])}


CAZURI = [
    ("obisnuit", {}),
    ("tanar sub 26", {"sub_26": True}),
    ("copii scolarizati", {"copii_scoala": 2, "declaratie_copii": True}),
    ("tanar + copii", {"sub_26": True, "copii_scoala": 2, "declaratie_copii": True}),
    ("persoana in intretinere", {"persoane": 1}),
]


@pytest.mark.parametrize("nume,kw", CAZURI, ids=[c[0] for c in CAZURI])
def test_deducerea_personala_arata_exact_deducerea_personala(nume, kw):
    """Randul care se numeste «Deducere personala» poarta deducerea de baza, nu totalul."""
    r = _rand_ca_din_stat(**kw)
    randuri = sp.randuri_deducere(r)
    pers = [v for et, v in randuri if et == "Deducere personala"]
    assert pers, "%s: niciun rand «Deducere personala» (randuri: %r)" % (nume, randuri)
    assert abs(pers[0] - r["deducere_baza"]) < 0.005, (
        "%s: randul «Deducere personala» arata %.2f, dar deducerea personala e %.2f"
        % (nume, pers[0], r["deducere_baza"]))


@pytest.mark.parametrize("nume,kw", CAZURI, ids=[c[0] for c in CAZURI])
def test_niciun_leu_de_deducere_nu_se_pierde(nume, kw):
    """Suma randurilor tiparite = totalul din calcul. Numirea nu are voie sa piarda bani."""
    r = _rand_ca_din_stat(**kw)
    s = sum(v for _et, v in sp.randuri_deducere(r))
    assert abs(s - r["deducere"]) < 0.005, (
        "%s: randurile insumeaza %.2f, totalul din calcul e %.2f" % (nume, s, r["deducere"]))


def test_suplimentarele_sunt_numite_cand_se_acorda():
    """Cand deducerea suplimentara e acordata, ea are RANDUL EI, cu numele ei."""
    r = _rand_ca_din_stat(sub_26=True, copii_scoala=2, declaratie_copii=True)
    assert r["deducere_tineri"] > 0 and r["deducere_copii"] > 0, (
        "cazul de calibrare nu mai produce deduceri suplimentare: %r" % r)
    etichete = [et for et, _v in sp.randuri_deducere(r)]
    assert any("tineri" in e for e in etichete), "deducerea pentru tineri nu e numita: %r" % etichete
    assert any("copii" in e for e in etichete), "deducerea pentru copii nu e numita: %r" % etichete


def test_fiecare_componenta_din_calcul_are_unde_sa_ajunga():
    """ANTI-VACUU + anti-imbatranire: fiecare componenta nenula a deducerii ajunge pe hartie.

    Daca legea adauga o a patra deducere si `calcul_salariu` o intoarce, dar `randuri_deducere` n-o
    numeste, testul cade aici — nu asteapta sa observe cineva o eticheta gresita."""
    c = salarizare.calcul_salariu(_brut_minim(), la_data=LA, sub_26=True, copii_scoala=2,
                                  declaratie_copii=True, persoane=1)
    comp = {k: float(v) for k, v in c["deducere"].items() if k != "total"}
    assert comp, "deducerea nu mai e desfacuta in componente — garda ar fi vida"
    r = {"deducere": float(c["deducere"]["total"])}
    r.update({"deducere_" + k: v for k, v in comp.items()})
    tiparit = sum(v for _et, v in sp.randuri_deducere(r))
    assert abs(tiparit - sum(comp.values())) < 0.005, (
        "componente in calcul: %r (suma %.2f), tiparit %.2f — o componenta nu ajunge pe hartie"
        % (comp, sum(comp.values()), tiparit))


def test_exemplar_vechi_nu_pretinde_ca_totalul_e_deducerea_personala():
    """Un exemplar inghetat fara componente isi spune pe nume, nu imprumuta eticheta gresita."""
    randuri = sp.randuri_deducere({"deducere": 1513.75})
    assert len(randuri) == 1
    et, val = randuri[0]
    assert et != "Deducere personala", "eticheta falsa a supravietuit pe exemplarele vechi"
    assert "suplimentare" in et and abs(val - 1513.75) < 0.005
