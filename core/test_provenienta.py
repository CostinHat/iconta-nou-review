# -*- coding: utf-8 -*-
"""GARDA: fiecare fisier din corpus isi stie provenienta. (23.08.2026)

DE UNDE VINE. Interdictia 52 raspundea „0 acte modificate dupa aducere, din 177 de
perechi" pe un corpus de 348 de fisiere - o afirmatie despre jumatate. Reactia fireasca,
„se amprenteaza si restul, e mecanic", ar fi fost gresita: 150 sunt text DERIVAT dintr-un
fisier deja amprentat (amprenta lor n-ar adauga nimic), iar 7 sunt NOTE SCRISE DE NOI
(amprenta lor ar raspunde la alta intrebare, pe care git o rezolva). Cifra ar fi crescut
fara ca acoperirea sa creasca - adica exact felul de verde care nu inseamna nimic.

CE FACE IMPOSIBIL:
  · un fisier de corpus fara clasa - nici mecanica, nici declarata;
  · un fisier declarat ADUS sau ADUS_ADNOTAT fara amprenta (chiar gaura lui 52);
  · un artefact GOL nou - un fisier de un octet cu nume de act, care pentru orice
    instrument arata ca „act prezent, nu spune nimic". Opt asemenea exista deja, de pe
    13-14.08, sub clichet declarat;
  · o declaratie ramasa in urma unui fisier care nu mai e pe disc.

CALIBRARE NEGATIVA (interdictia 76): trei dintre teste isi produc singure cazul rau -
un fisier gol nou, un ADUS fara amprenta, o declaratie orfana - si cer ca instrumentul
sa-l ACUZE. Fara ele, testele ar dovedi doar ca instrumentul gaseste ce e curat.
"""
import io
import json
import os
import shutil

import pytest

from core import scan_provenienta as sp

MIN_FISIERE = 300  # anti-vacuu: corpusul avea 348 pe 23.08
GOALE_CLICHET = 0  # 8 -> 0 pe 23.08: cele de pe 13-14.08 au fost STERSE prin decizie (R20).
                   # De acum orice artefact gol din corpus pica poarta, nu doar unul nou.


class _Corpus(object):
    """Corpus minimal de proba. Obiect propriu fiindca `PosixPath` nu primeste atribute."""

    def __init__(self, rad):
        self.cale = str(rad)

    def scrie(self, nume, continut=b"text de act, destul de lung ca sa nu fie gol"):
        io.open(os.path.join(self.cale, nume), "wb").write(continut)

    def amprenteaza(self, nume):
        h = sp.amprenta(os.path.join(self.cale, nume))
        io.open(os.path.join(self.cale, nume + ".sha256"), "w", encoding="utf-8").write(
            "%s  %s\n" % (h, nume))


@pytest.fixture
def corpus_fals(tmp_path):
    c = _Corpus(tmp_path)
    c.scrie("act_adus.pdf")
    c.amprenteaza("act_adus.pdf")
    c.scrie("act_adus.txt")  # derivat din pdf-ul amprentat
    return c


def _declara(c, fisiere=None, goale=None):
    d = {"fisiere": fisiere or {}, "goale_cunoscute": {"lista": goale or []}}
    io.open(os.path.join(c.cale, sp.NUME_DECLARATII), "w", encoding="utf-8").write(
        json.dumps(d, ensure_ascii=False))


# --------------------------------------------------------------- corpusul real

def test_gardul_chiar_vede_corpusul():
    """ANTI-VACUU: daca scanul nu gaseste fisiere, orice afirmatie de mai jos e vida."""
    n = len(sp._fisiere())
    assert n >= MIN_FISIERE, (
        "doar %d fisiere gasite in %s - ori s-a mutat corpusul, ori s-a rupt cautarea. "
        "Un verde pe zero fisiere nu e o afirmatie despre corpus." % (n, sp.CORPUS))


def test_fiecare_fisier_isi_stie_clasa():
    nd = sorted(f for f, (c, _) in sp.clasifica().items() if c == sp.NEDECLARAT)
    assert not nd, (
        "%d fisiere de corpus fara clasa. Un fisier fara provenienta nu poate fi nici "
        "confirmat, nici acuzat - se poate schimba sub noi fara sa se aprinda nimic, "
        "ceea ce e chiar formularea interdictiei 52. Declara-le in %s:\n  %s"
        % (len(nd), sp.NUME_DECLARATII, "\n  ".join(nd)))


def test_un_act_adus_e_amprentat():
    lipsa = sp.adus_fara_amprenta()
    assert not lipsa, (
        "declarate ADUSE, dar fara amprenta: %s. Pentru un act adus, intrebarea lui 52 "
        "- s-a schimbat dupa aducere? - are sens si nu are raspuns." % lipsa)


def test_nicio_declaratie_orfana():
    orf = sp.declaratii_orfane()
    assert not orf, (
        "declaratii pentru fisiere care nu mai sunt pe disc: %s. O declaratie orfana "
        "apara o lume care a plecat." % orf)


def test_niciun_artefact_gol_nou():
    noi = sp.goale_noi()
    assert not noi, (
        "artefacte GOALE nedeclarate: %s. Un fisier de un octet cu nume de act e mai rau "
        "decat unul lipsa: pentru orice instrument arata ca act PREZENT si TACUT, deci "
        "produce o absenta falsa. Daca e intentionat, treci-l in `goale_cunoscute` cu "
        "motivul." % noi)


def test_clichetul_golurilor_nu_creste():
    n = len(sp.goale())
    assert n <= GOALE_CLICHET, (
        "%d artefacte goale, clichetul e %d. Clichet, nu xfail: cifra are voie sa scada, "
        "nu sa creasca." % (n, GOALE_CLICHET))


# ------------------------------------------------- calibrare NEGATIVA (76)

def test_CALIBRARE_un_gol_nou_e_ACUZAT(corpus_fals):
    """Cazul rau, produs anume: fisierul gol trebuie sa fie GASIT, nu ignorat."""
    _declara(corpus_fals)
    corpus_fals.scrie("d999_nou.txt", b"\n")
    noi = sp.goale_noi(corpus_fals.cale)
    assert [f for f, _ in noi] == ["d999_nou.txt"], (
        "un artefact gol NOU n-a fost acuzat: %s. Fara asta, garda ar tace exact pe clasa "
        "pe care a fost construita s-o prinda." % noi)


def test_CALIBRARE_un_gol_DECLARAT_nu_e_acuzat(corpus_fals):
    """Cealalta directie: daca acuza si ce e declarat, garda devine zgomot si moare."""
    corpus_fals.scrie("d999_nou.txt", b"\n")
    _declara(corpus_fals, goale=["d999_nou.txt"])
    assert sp.goale_noi(corpus_fals.cale) == [], (
        "un gol DECLARAT a fost acuzat oricum - garda ar deveni zgomot si s-ar dezactiva")


def test_CALIBRARE_un_ADUS_fara_amprenta_e_ACUZAT(corpus_fals):
    corpus_fals.scrie("hotarare_fara_amprenta.pdf")
    _declara(corpus_fals, fisiere={"hotarare_fara_amprenta.pdf": {"clasa": sp.ADUS}})
    assert sp.adus_fara_amprenta(corpus_fals.cale) == ["hotarare_fara_amprenta.pdf"], (
        "un act declarat ADUS, fara amprenta, n-a fost acuzat - adica exact gaura pe care "
        "interdictia 52 o masoara ar trece neobservata")


def test_CALIBRARE_un_SCRIS_fara_amprenta_NU_e_acuzat(corpus_fals):
    """O nota scrisa de noi n-are de ce sa fie amprentata: intrebarea nu i se aplica."""
    corpus_fals.scrie("nota_proprie.txt")
    _declara(corpus_fals, fisiere={"nota_proprie.txt": {"clasa": sp.SCRIS}})
    assert sp.adus_fara_amprenta(corpus_fals.cale) == [], (
        "o nota SCRISA de noi a fost ceruta amprentata - asta ar umfla acoperirea fara "
        "s-o creasca, fiindcă amprenta ei raspunde la 'nu l-am editat', nu la "
        "'actul s-a schimbat sub noi'")


def test_CALIBRARE_o_declaratie_orfana_e_ACUZATA(corpus_fals):
    _declara(corpus_fals, fisiere={"act_care_a_plecat.pdf": {"clasa": sp.ADUS}})
    assert sp.declaratii_orfane(corpus_fals.cale) == ["act_care_a_plecat.pdf"], (
        "o declaratie pentru un fisier inexistent n-a fost acuzata")


def test_CALIBRARE_derivatul_isi_gaseste_sursa(corpus_fals):
    """Si directia curata: un .txt langa un .pdf amprentat e DERIVAT, nu NEDECLARAT."""
    _declara(corpus_fals)
    cl = sp.clasifica(corpus_fals.cale)
    assert cl["act_adus.txt"][0] == sp.DERIVAT, cl["act_adus.txt"]
    assert cl["act_adus.pdf"][0] == sp.AMPRENTAT, cl["act_adus.pdf"]
