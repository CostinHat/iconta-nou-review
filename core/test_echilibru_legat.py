# -*- coding: utf-8 -*-
"""core/test_echilibru_legat.py — GARDA R33 varianta b'' (26.08.2026).

CE FACE IMPOSIBIL:
  1. reintoarcerea ramurii TAUTOLOGICE `BALANTA_INEGALA` (nu se poate produce din intrarea reala);
  2. o ramura a verdictului compus `echilibru` care nu poate deveni ROSIE — fiecare `fel` declarat
     trebuie sa fie PRODUCTIBIL dintr-o intrare de forma pe care o da productia;
  3. pierderea vreunuia din cele trei moduri de esec disjuncte (linie rupta / orfan / solduri);
  4. reintoarcerea orbirii la contul format din SPATII;
  5. rotunjirea unei verificari care N-A RULAT la „in regula" (P6).

CE NU FACE, DECLARAT:
  - nu atinge baza de date: `echilibru_perioada_db` are reader propriu, testat in
    core/test_echilibru_perioada.py. Aici se verifica LOGICA si COMPUNEREA, pe date construite.
  - nu verifica randarea (aia e proba vizuala); verifica doar ca verdictul poarta cifrele din care
    randarea isi poate compune textul.
  - nu spune ca cele trei moduri de esec sunt TOATE modurile posibile — spune ca fiecare dintre
    cele trei declarate e prins.

DE CE E O GARDA PE NON-TAUTOLOGIE, si nu inca un test de comportament: interdictia 19 si R18.
O ramura verde-prin-constructie trece orice test scris pe cazul fericit. Singura proba ca o
ramura VERIFICA ceva e sa existe o intrare care o face ROSIE — iar intrarea trebuie sa aiba
FORMA pe care i-o da productia, nu una construita anume ca sa pice.
"""
import random
from decimal import Decimal

import pytest

from core import common as c
from core import verificatoare as vf
from core import echilibru_perioada as ep


# ---------------------------------------------------------------- ajutoare
def _linie(d, cr, s, iid=1):
    return {"inregistrare_id": iid, "cont_debit": d, "cont_credit": cr, "suma": Decimal(str(s))}


def _bal(linii, si=None):
    """Construieste balanta EXACT cum o construieste main._verificari_contabile."""
    note = [{"debit": l["cont_debit"], "credit": l["cont_credit"], "suma": l["suma"]} for l in linii]
    return vf.balanta(note, si or {})


def _db_rez(linii):
    """Ce ar intoarce echilibru_perioada_db pe liniile astea, fara sa atinga baza."""
    sd, sc, ok = ep.echilibru_perioada(linii)
    orf = ep.orfani(linii, {1})
    return {"an": 2099, "luna": 6, "sigma_debit": sd, "sigma_credit": sc,
            "echilibrat": ok, "diferenta": sd - sc, "orfani": len(orf)}


def _verdict(linii, si=None):
    return ep.verdict_echilibru(_db_rez(linii), vf.verifica_balanta(_bal(linii, si)), "2099-06")


def _feluri(v):
    return {x["fel"] for x in v["constatari"]}


CORECTE = [_linie("401", "5121", 1000), _linie("5121", "411", 500)]


# ---------------------------------------------------------------- 1. tautologia scoasa
def test_codul_tautologic_nu_mai_exista():
    """BALANTA_INEGALA a fost scoasa din registrul de coduri, nu doar din ramura.

    Un cod ramas in CODURI fara producator e o invitatie sa fie rechemat de altcineva, care
    n-ar avea de unde sti ca era tautologic."""
    assert "BALANTA_INEGALA" not in c.CODURI, (
        "BALANTA_INEGALA a reaparut in common.CODURI. Era TAUTOLOGICA pe intrarea reala: "
        "balanta() adauga aceeasi suma pe debit si pe credit, deci totalurile sunt egale prin "
        "constructie (masurat 25.08.2026: 0 din 2000 de seturi aleatoare). Egalitatea Sigma "
        "debit = Sigma credit se verifica in echilibru_perioada, pe liniile brute.")


def test_verifica_balanta_nu_mai_poate_pica_pe_totaluri():
    """Proba prin CONSTRUCTIE ca ramura scoasa chiar era tautologica — pe forma reala de intrare.

    Daca aceasta aserttiune ar pica, inseamna ca exista o intrare care rupe egalitatea
    totalurilor, deci ramura NU era tautologica si scoaterea ei a fost gresita. E calibrarea
    negativa a deciziei insesi."""
    rnd = random.Random(20260826)
    conturi = ["401", "411", "5121", "607", "707", None, "", "   "]
    diferite = 0
    for _ in range(2000):
        linii = [_linie(rnd.choice(conturi), rnd.choice(conturi), rnd.randint(1, 9999))
                 for _ in range(rnd.randint(1, 6))]
        try:
            b = _bal(linii)
        except TypeError:
            continue  # conturi None: sorted() crapa — alt mod de esec, nu asta
        td = sum((v["debit"] for v in b.values()), Decimal(0))
        tc = sum((v["credit"] for v in b.values()), Decimal(0))
        if td != tc:
            diferite += 1
    assert diferite == 0, (
        "%d seturi au produs total_debit != total_credit la iesirea lui balanta() — deci ramura "
        "BALANTA_INEGALA NU era tautologica si trebuie repusa, cu motivul rescris." % diferite)


def test_ramura_ramasa_chiar_poate_deveni_rosie():
    """ANTI-TAUTOLOGIE, cealalta directie: ce a RAMAS din verifica_balanta trebuie sa poata pica.

    Fara aserttiunea asta, scoaterea unei ramuri tautologice ar putea lasa in urma o functie
    care nu mai verifica NIMIC — si care ar trece toate testele de mai jos."""
    p = vf.verifica_balanta(_bal(CORECTE, {"1012": Decimal("5000")}))
    assert not p.get("ok"), "soldurile initiale dezechilibrate NU mai sunt prinse — functia e goala"
    assert p["cod"] == "BALANTA_SI_DEZECHILIBRATA"
    assert vf.verifica_balanta(_bal(CORECTE, {"1012": Decimal("5000"), "5121": Decimal("-5000")}))["ok"]


# ---------------------------------------------------------------- 2. control pozitiv
def test_pe_date_corecte_verdictul_e_verde():
    v = _verdict(CORECTE)
    assert v["ok"] is True and v["constatari"] == [], v


# ---------------------------------------------------------------- 3. cele trei moduri disjuncte
@pytest.mark.parametrize("titlu,linii,si,fel_asteptat", [
    ("linie cu cont_debit gol", [_linie("401", "5121", 1000), _linie("", "411", 500)], None,
     ep.FEL_LEDGER),
    ("linie cu cont_credit gol", [_linie("401", "5121", 1000), _linie("411", "", 500)], None,
     ep.FEL_LEDGER),
    ("linie cu cont din SPATII", [_linie("401", "5121", 1000), _linie("   ", "411", 500)], None,
     ep.FEL_LEDGER),
    ("orfan — inregistrare inexistenta", [_linie("401", "5121", 1000),
                                          _linie("512", "411", 500, iid=999)], None, ep.FEL_ORFANI),
    ("solduri initiale dezechilibrate", CORECTE, {"1012": Decimal("5000")},
     ep.FEL_SOLDURI),
])
def test_fiecare_mod_de_esec_ajunge_in_verdict(titlu, linii, si, fel_asteptat):
    """Tabelul de calibrare din CONFORMITATE R33, ca gard viu.

    Fiecare rand e un mod de esec pe care UNA din cele doua verificari il prinde si cealalta il
    rateaza. Daca vreunul dispare din verdict, s-a pierdut exact ce a facut varianta b'' sa fie
    aleasa in locul lui (b) sau (c)."""
    v = _verdict(linii, si)
    assert v["ok"] is False, "«%s» a trecut ca verde: %r" % (titlu, v)
    assert fel_asteptat in _feluri(v), "«%s» -> asteptam %r, am primit %r" % (titlu, fel_asteptat, _feluri(v))


def test_cele_doua_chiar_sunt_disjuncte():
    """Non-redundanta, masurata — nu declarata.

    Daca una le-ar prinde pe toate, a doua ar fi cu adevarat logica paralela si decizia (b) ar fi
    fost corecta. Aserttiunea asta e ce ar cadea primul daca asa ar deveni."""
    rupt = [_linie("401", "5121", 1000), _linie("", "411", 500)]
    assert not ep.echilibru_perioada(rupt)[2], "echilibru_perioada nu mai vede linia rupta"
    assert vf.verifica_balanta(_bal(rupt))["ok"], (
        "verifica_balanta a inceput sa vada linia rupta — daca e adevarat, disjunctia s-a schimbat "
        "si decizia b'' trebuie remasurata, nu testul relaxat")
    assert vf.verifica_balanta(_bal(CORECTE, {"1012": Decimal("5000")}))["ok"] is False
    assert ep.echilibru_perioada(CORECTE)[2] is True, (
        "echilibru_perioada a inceput sa vada soldurile initiale — idem, se remasoara")


# ---------------------------------------------------------------- 4. spatiile
def test_contul_din_spatii_nu_numara_drept_prezent():
    """Masurat 26.08.2026: 12 locuri din cod scriu contul cu `str(corp.get(...) or "<implicit>")`,
    fara strip — deci spatiile ajung in baza. NOT NULL nu le opreste, un CHECK pe '' nu le-ar
    opri, si pana azi nici verificarea nu le vedea (`if l.get("cont_debit")` e adevarat pe "   ")."""
    assert ep._are_cont("401") is True
    for gol in ("", "   ", "\t", "\n", None):
        assert ep._are_cont(gol) is False, "«%r» numara inca drept cont prezent" % (gol,)


# ---------------------------------------------------------------- 5. necunoscutul nu e verde
def test_o_verificare_care_n_a_rulat_nu_devine_in_regula():
    """P6: verdele AFIRMA. O verificare rupta (motorul a crapat) nu e «in regula»."""
    v = ep.verdict_echilibru({"eroare": "OperationalError: pool epuizat"}, {"ok": True})
    assert v["ok"] is False and ep.FEL_NEVERIFICAT in _feluri(v), v
    v2 = ep.verdict_echilibru(_db_rez(CORECTE), None)
    assert v2["ok"] is False and ep.FEL_NEVERIFICAT in _feluri(v2), v2


# ---------------------------------------------------------------- 6. anti-vacuu
def test_verdictul_poarta_CIFRELE_nu_fraze():
    """DS cap.13: constatarile sunt OBIECTE cu atribute. Dintr-o fraza cifrele nu se compun inapoi,
    iar randarea n-ar putea arata «ce a gasit fiecare»."""
    v = _verdict([_linie("401", "5121", 1000), _linie("", "411", 500)])
    x = [k for k in v["constatari"] if k["fel"] == ep.FEL_LEDGER][0]
    for camp in ("sigma_debit", "sigma_credit", "diferenta"):
        assert camp in x, "constatarea nu poarta %s — randarea n-ar avea ce arata" % camp
    assert x["sigma_debit"] != x["sigma_credit"]


def test_domeniul_nu_e_gol():
    """Anti-vacuu: un gard care ruleaza pe zero cazuri raporteaza favorabil despre o lume pe care
    n-o vede (interdictia 19, aplicata gardului insusi)."""
    assert len(CORECTE) >= 2
    assert _bal(CORECTE), "balanta construita e goala — testele de mai sus n-ar masura nimic"
    assert len(ep.verdict_echilibru(_db_rez([_linie("", "411", 500)]), {"ok": True})["constatari"]) >= 1
