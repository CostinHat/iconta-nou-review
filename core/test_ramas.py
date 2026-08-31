# -*- coding: utf-8 -*-
"""GARDĂ anti-vacuu pe lista derivată a ce a rămas de făcut.

Instrumentul citește șase surse cu șase formate. **Un format care se schimbă îl face să întoarcă
zero pe acea sursă — și zero se citește ca «terminat».** S-a întâmplat la prima rulare, pe
instrumente: parserul căuta un tabel, roadmapul le ține ca listă, iar rezultatul, `0`, ar fi însemnat
că din cele 11 nu mai e nimic de construit.

Garda asta nu verifică dacă lista e completă — nu poate. Verifică doar că **fiecare sursă produce
ceva**, fiindcă o sursă mută e nedistinsă de una goală.
"""
import pytest

from scripts import scan_ramas as s


@pytest.fixture(scope="module")
def randuri():
    return s.tot()


def test_fiecare_sursa_produce_ceva(randuri):
    """Miezul. O sursă care întoarce zero e ori terminată, ori mută — și cele două arată identic."""
    pe_fel = {f: sum(1 for x in randuri if x["fel"] == f) for f in s.FELURI}
    mute = [f for f, n in pe_fel.items() if n == 0]
    assert not mute, (
        "surse care nu mai produc niciun rând: %s. Ori chiar s-a terminat tot acolo — și atunci se "
        "scrie, cu data —, ori formatul fișierului s-a schimbat și parserul a orbit. A doua variantă "
        "s-a întâmplat deja o dată, pe INSTRUMENT: un zero care se citea «gata»." % mute)


def test_fiecare_rand_isi_poarta_SURSA(randuri):
    """Costin: «cu sursă pe fiecare rând». Un rând fără sursă nu se poate verifica la loc."""
    fara = [x["ce"][:40] for x in randuri if not x.get("sursa")]
    assert not fara, "rânduri fără sursă: %s" % fara


def test_clichetele_au_dimensiune_RECALCULATA_nu_citita(randuri):
    """Singurele rânduri cu dimensiune sigură sunt cele care se recalculează. Dacă vreunul ajunge
    `?` sau «EROARE», lista și-a pierdut singura parte probată."""
    cl = [x for x in randuri if x["fel"] == "CLICHET"]
    assert len(cl) >= 3, "prea puține clichete vii: %d" % len(cl)
    rele = [x for x in cl if not x["dimensiune"].isdigit()]
    assert not rele, (
        "clichete fără cifră recalculată: %s" % [(x["cod"], x["dimensiune"]) for x in rele])


def test_nomenclatorul_felurilor_e_INCHIS(randuri):
    assert {x["fel"] for x in randuri} <= set(s.FELURI)


def test_divergentele_se_masoara_chiar_daca_ies_zero(randuri):
    """Zero divergențe e un rezultat, nu o absență de măsurătoare — dar numai dacă potrivirea chiar
    a rulat pe ceva. Se cere ca instrumentul să aibă cu ce compara."""
    assert len(s.SINONIME) >= 3, "lista de sinonime s-a golit — potrivirea n-are cu ce lucra"
    s.divergente(randuri)  # nu trebuie să ridice
