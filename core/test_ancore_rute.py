# -*- coding: utf-8 -*-
"""GARD [R80, 27.08.2026]: clasa de rute despre care detectorul din R70 nu poate afirma nimic
nu mai creste in tacere.

DE UNDE VINE. Am mutat un buton de pe `PUT /tenants/{id}` pe `POST /tenants/{id}/nume-ales`.
Ruta veche a ramas cu **zero** apelanti in `static/`. Gardul R70 — construit exact pentru clasa
„ruta fara apelant" — n-a raportat-o: singura ei ancora literala e `tenants`, care apare de 235
de ori in JS. Deci pentru ea, detectorul raspunde intotdeauna „are apelant".

CE FACE IMPOSIBIL: o ruta noua a carei ancora nu o identifica intra fara sa se stie. Nu o
interzice — o **numara**. Cine adauga a 52-a coboara clichetul deliberat, sau ii da o cale mai
specifica.

CE NU FACE, declarat: **nu spune care rute chiar n-au apelant.** Spune despre care dintre ele
detectorul e mut. Iar clichetul e o FOTOGRAFIE, nu o tinta: 51 la 27.08.2026, pe pragul de 40.

DE CE NU REPAR DETECTORUL IN LOC SA-L MASOR. Fiindca a patra regula e deja „cea mai putin
gresita, nu cea corecta" (scris in R70), iar a cincea ar cere sa stiu cum compune fiecare ecran
calea la rulare. Masuratoarea e ieftina si onesta; repararea e o campanie, si are nevoie de
decizia lui Costin.
"""
import os
import sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RAD)
sys.path.insert(0, os.path.join(_RAD, "scripts"))

_CLICHET = 51          # masurat 27.08.2026, pe pragul de 40
_PRAG = 40


def _masoara():
    from scan_ancore_rute import masoara
    return masoara(_PRAG)


def test_clasa_oarba_nu_creste():
    _rute, _js, orbi, _vazute = _masoara()
    assert len(orbi) <= _CLICHET, (
        "rute despre care detectorul de apelanti nu poate afirma nimic: %d, clichetul e %d.\n"
        "Ruta noua are o ancora care nu o identifica (ex. o cale de forma `/tenants/{id}`, unde\n"
        "singurul cuvant literal apare peste tot). Ori dai o cale mai specifica, ori cobori\n"
        "clichetul deliberat si scrii de ce.\n  %s"
        % (len(orbi), _CLICHET,
           "\n  ".join("%s %s (ancora %r x%d)" % (m, c, a, f)
                       for m, c, f, a in sorted(orbi, key=lambda x: x[1])[:8])))


def test_clichetul_nu_pastreaza_morti():
    """A doua directie. Daca a scazut, se coboara deliberat — altfel cifra ramane o amintire."""
    _rute, _js, orbi, _vazute = _masoara()
    assert len(orbi) >= _CLICHET, (
        "clasa a scazut de la %d la %d — coboara `_CLICHET` in fisierul asta, ca urmatoarea "
        "crestere sa fie prinsa de la cifra reala, nu de la una veche" % (_CLICHET, len(orbi)))


def test_ANTI_VACUU_masuratoarea_chiar_vede():
    rute, js, orbi, vazute = _masoara()
    assert len(rute) > 300, "doar %d rute — s-ar masura in gol" % len(rute)
    assert js.count("tenants") > 100, (
        "textul JS nu contine nici macar `tenants` — prima versiune a masuratorii sparsese sirul "
        "in caractere si raporta 1 in loc de 51, adica exact greseala comoda")
    assert vazute, "toate rutele ies oarbe — pragul n-ar imparti nimic"
    assert orbi, "nicio ruta oarba — dar cazul cunoscut de mai jos e una"


def test_cazul_cunoscut_e_in_clasa():
    """Calibrare pe instanta care a produs gardul: daca nu mai e in clasa, masuratoarea s-a rupt
    sau ruta a primit o cale mai specifica — si atunci se citeste, nu se ignora."""
    _rute, _js, orbi, _vazute = _masoara()
    cai = {(m, c) for m, c, _f, _a in orbi}
    assert ("PUT", "/tenants/{tenant_id}") in cai, (
        "`PUT /tenants/{tenant_id}` nu mai e in clasa oarba. Daca i s-a dat o cale mai specifica, "
        "bine — coboara clichetul. Daca nu, masuratoarea nu mai masoara ce credea.")
