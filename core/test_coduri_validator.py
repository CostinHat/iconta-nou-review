# -*- coding: utf-8 -*-
"""Un cod de validator citat ca temei chiar există în validatorul declarației unde e citat.

DE UNDE VINE. Datoria din 30.07.2026: opt mențiuni fuseseră canonizate la forma `DUK regula <cod>`
— s-a schimbat MARCAJUL, nu s-a verificat conținutul. Verificate la sursă pe 14.09.2026, trei din
opt erau greșite, iar cea mai limpede e și cea mai instructivă: `A91b` era citată ca temei al
rotunjirii în D300 și în D390, dar A91b **nu există** în validatoarele lor (0 potriviri în tot
jarul) — e o regulă din D112, care într-adevăr respinsese rotunjirea bancară, dar acolo.

CE PĂZEȘTE, îngust: un cod citat care nu apare deloc în jarul declarației lui. Nu poate spune că
regula înseamnă ce credem — aia cere rularea validatorului pe un XML mutat deliberat (D100, D119 și
D710 au fost verificate așa în aceeași zi, iar la D100 rularea a contrazis citirea din bytecode: am
crezut R15, validatorul a răspuns R15.1).

MARCA DE FORMULAR. O regulă împrumutată de la alt formular își numește formularul:
`DUK regula A91b (D112)`. Fără marcă, codul se caută acolo unde ar căuta orice cititor — în
validatorul fișierului.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts import scan_coduri_validator as _s  # noqa: E402

# Cele opt care erau aici pe 14.09 — 7 în `core/d402.py` + proba lui, 1 în
# `core/d301_operatiuni_api.py` — au fost scrise atunci ca datorie deschisă, cu propoziția
# „NEVERIFICATĂ încă la rulare". Pe 16.09 s-au verificat, la rulare. Ce a ieșit e mai jos.
# Regula rămâne: scade doar cu VERIFICARE, nu cu ștergerea citării.
#: [16.09.2026] 8 -> 0, si de-aia e scris ca EGALITATE, nu ca plafon: un clichet la zero n-ar mai
#: pazi nimic. Cele opt s-au lamurit PRIN RULARE — XML mutat deliberat, cu mutatia DOVEDITA in
#: fisier inainte de a crede raspunsul —, nu prin citirea constantelor din jar:
#:   * `R50` -> `R29`: validatorul raspunde verbatim „eroare regula: R29: CIF_Rom … trebuie sa fie
#:     unic". Codul era pur si simplu gresit.
#:   * `R34` -> XSD: nu e o „regula" cu cod, e intervalul atributului („eroare atribut:
#:     Impozit_venit: valoarea '-5' nu se incadreaza in intervalul cerut"), adica `IntPoz15SType`,
#:     `minInclusive 0` — confruntat la sursa in `anaf_surse/d402_20160226_xsd_linii.txt`.
#:   * `R14`, `R39`, `R43` -> validatorul NU LE VERIFICA. Toate trei trec `valid` cu valoarea rea IN
#:     fisier. Sunt insa reguli REALE, confruntate verbatim in
#:     `anaf_surse/structuraXML_D402_2022.pdf` — deci verificarile noastre RAMAN; ce era fals era
#:     ATRIBUIREA. *Si deosebirea conteaza: cine citea marcajul de validator putea crede ca el prinde
#:     lipsa. N-o prinde; o prindem noi, inainte de depunere.*
#:   * `R24.1` -> CORECT, confirmat verbatim de validatorul D390 („eroare regula: R24.1: operatorul
#:     codO … trebuie sa respecte algoritmul specific 'IT'"). Ii lipsea doar MARCA DE FORMULAR: e o
#:     regula a lui D390, citata intr-un fisier `d301_*`, iar scanul o cauta in jarul declaratiei
#:     fisierului. Conventia exista deja in antetul de mai sus; acum e aplicata.
PLAFON_NECORELATE = 0


def test_CLICHET_citarile_necorelate_nu_cresc():
    nec, _fara, _disc = _s.confrunta()
    assert len(nec) == PLAFON_NECORELATE, (
        "coduri citate care nu apar în validatorul declarației lor: %d, așteptat %d.\n"
        "  E un CRITERIU, nu un clichet: o citare nouă se confruntă cu validatorul ÎNAINTE de a "
        "intra, iar dacă regula e a altui formular își poartă marca.\n  %s"
        % (len(nec), PLAFON_NECORELATE,
           "\n  ".join("%s:%d  %s (căutat în %s)"
                       % (m["fisier"], m["linia"], m["cod"], "/".join(m["cautat_in"]))
                       for m in nec)))


def test_ANTI_VACUU_scanul_chiar_vede_citarile_si_jarurile():
    """O gardă care caută în locul greșit raportează verde despre o lume pe care n-o vede."""
    m = _s.mentiuni()
    assert len(m) > 200, "doar %d citări găsite — domeniul de căutare s-a rupt" % len(m)
    _nec, _fara, disc = _s.confrunta()
    assert disc > 80, ("doar %d citări au cod de cel puțin 4 caractere — sub atât, prezența într-un "
                       "jar de câțiva MB e coincidență, deci garda n-ar discrimina nimic" % disc)
    assert _s.jar_declaratiei("d112"), "niciun validator instalat — nu există sursă de confruntat"


def test_CALIBRARE_pe_univers_fabricat_in_toate_directiile():
    """Cod inexistent -> prins. Cod real -> tăcut. Marca de formular -> respectată. Proză -> tăcută."""
    rau = [("core/d112.py", "# DUK regula ZZ9997: regula care nu exista nicaieri\n")]
    assert len(_s.confrunta(rau)[0]) == 1, "un cod inexistent în D112Validator nu e raportat"

    bun = [("core/d112.py", "# DUK regula A91b: contributia angajator CAM\n")]
    assert not _s.confrunta(bun)[0], "A91b, care CHIAR e în D112Validator, e raportat ca defect"

    imprumutat = [("core/d300.py", "# DUK regula A91b (D112): dovedit pe alt formular\n")]
    assert not _s.confrunta(imprumutat)[0], (
        "marca de formular e ignorată — o citare corectă împrumutată apare ca defect")

    nemarcat = [("core/d300.py", "# DUK regula A91b: dovedit... dar unde?\n")]
    assert len(_s.confrunta(nemarcat)[0]) == 1, (
        "ACEEAȘI citare, fără marcă, în fișierul lui D300 — trebuie raportată; altfel marca n-ar "
        "însemna nimic")

    proza = [("core/d112.py", "# DUK regula suprafata se aplica la teren\n")]
    assert not _s.confrunta(proza)[0], "un cuvânt fără cifră e numărat drept cod — proză raportată"


def test_cele_TREI_corectii_din_14_09_chiar_sunt_in_arbore():
    """Anti-vacuum pe reparație: fără asta, clichetul ar fi trecut și dacă citările reveneau.

    A91b nu mai e citată nemarcat sub D300/D390; d119 nu mai numește R15 ramura care e R14; d710
    nu mai atribuie lui R17 un refuz care vine din domeniul atributului."""
    nec = {(m["fisier"], m["cod"]) for m in _s.confrunta()[0]}
    for f in ("core/test_d300.py", "core/test_d390.py", "core/d390.py"):
        assert (f, "A91b") not in nec, "%s citează iar A91b fără marca (D112)" % f

    # Pe citarile PARSATE, nu pe textul fisierului: intrebarea e „ce cod e citat in ce fisier",
    # iar aia e o pereche in inventarul instrumentului, nu un sir cautat intr-un alt sir.
    citate = {(m["fisier"], m["cod"]) for m in _s.mentiuni()}
    assert ("core/d119.py", "R14") in citate, (
        "d119 nu mai citeaza R14 — ramura `Suma_dat >= Suma_ded` e R14 la validator "
        "(rulat 14.09.2026), iar eticheta R15 de dinainte era gresita")
    # A treia corecție (d710: refuzul pe `cota` nu vine din R17, ci din domeniul atributului) NU are
    # aici o gardă proprie: R17 rămâne o regulă REALĂ a lui D710, deci nici scanul, nici o pereche
    # (fișier, cod) n-o pot deosebi de citarea corectă. O păzesc garda de citare canonică
    # (`test_temeiuri`) și propoziția din `core/d710.py`. *Se scrie, nu se tace.*
