# -*- coding: utf-8 -*-
"""GARD [27.08.2026]: o decizie cerută de mai multe ori nu mai poate arăta ca cerută o dată.

DE UNDE VINE, și e o întrebare a lui Costin pusă de două ori în aceeași tură: *„dacă ți-am dat-o
de două ori și tot apare ca deschisă, verifică de ce nu ajunge la restanță."*

RĂSPUNSUL, măsurat: **contorul care ar face bucla vizibilă nu e folosit.** Din restanțele DESCHISE
deblocate de **DECIZIE**, **19 au `reluări: 0`** deși registrul s-a mișcat sub ele — R9 de **133**
de commituri, R18 de **122**, R26 de **90**. Câmpul există, garda lui există
(`test_trei_reluari_fara_rezultat_cer_rescrierea_conditiei`, care sare la ≥3), dar contorul nu urcă
niciodată — deci garda aia n-a putut să se aprindă **nici măcar o dată**.

ȘI PARTEA CARE E MAI RĂU DECÂT OMISIUNEA: clasa era **deja găsită și scrisă** în `CONFORMITATE.md`
— *„contorul de reluări e 0 pe TOATE cele 25 de restanțe […] regula era scrisă și nepăzită, deci
se citea ca respectată. Reaprinderea n-a funcționat niciodată."* A fost constatată, consemnată, și
lăsată ca **disciplină**. A rămas 0 pe 69 din 76.

CE FACE IMPOSIBIL: ca o restanță NOUĂ deblocată de decizie să treacă pragul de commituri cu
contorul pe zero. Cele 19 de azi stau într-o **fotografie**, ca poarta să nu fie retroactivă —
aceeași formă ca la R70 și R74.

CE NU FACE, declarat:
  - **nu numără de câte ori am cerut eu.** Numără câte commituri de registru a supraviețuit
    restanța — un **proxy**, nu măsura. O decizie cerută de trei ori într-o zi, într-un singur
    commit, nu se vede de aici.
  - **nu știe dacă răspunsul a fost dat.** Dacă Costin decide și eu nu scriu, garda tace: din
    afară, „n-a răspuns" și „n-am scris" arată la fel. Aia rămâne pe disciplină, și se spune.
  - **nu coboară clichetul singură.** Când o restanță primește contor, iese din mulțime, iar a
    doua direcție cere scoaterea ei din fotografie — deliberat.
"""
import os
import subprocess

import pytest

from core import test_conformitate as _tc

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Peste câte commituri de registru o decizie necerută-din-nou devine o buclă tăcută.
# 5 nu e ales din gust: sub el stau doar restanțele deschise în ultimele două zile, adică cele
# pentru care încă n-a existat ocazia unei reluări.
_PRAG_COMMITURI = 5

# FOTOGRAFIE la 27.08.2026 — nu o listă de vinovați. Fiecare intrare iese când primește contor.
_NENUMARATE = {
    # R34 a iesit pe 28.08.2026: decizia a fost DATA (sursa e D112) si contorul a urcat la 1.
    "R9", "R18", "R26", "R36", "R38", "R39", "R45", "R47",
    "R54", "R58", "R59", "R63", "R64", "R66", "R67", "R68", "R70", "R73",
}


def _commituri_de_la(commit):
    r = subprocess.run(["git", "-C", _RAD, "rev-list", "--count", "%s..HEAD" % commit,
                        "--", "CONFORMITATE.md"], capture_output=True, text=True)
    return int((r.stdout or "0").strip() or 0)


@pytest.fixture(scope="module")
def buclele():
    """{cod} — restanțe DESCHISE + DECIZIE, cu `reluări: 0`, peste prag."""
    out = set()
    for cod, (_titlu, corp) in _tc._restante().items():
        if not (_tc._camp(corp, "stare") or "").strip().startswith("DESCHIS"):
            continue
        if (_tc._camp(corp, "cine deblochează") or "").strip() != "DECIZIE":
            continue
        if int((_tc._camp(corp, "reluări") or "0").strip("* ") or 0) != 0:
            continue
        c = (_tc._camp(corp, "deschisă pe commit") or "").strip("`*— ")
        if c and _commituri_de_la(c) >= _PRAG_COMMITURI:
            out.add(cod)
    return out


def test_ANTI_VACUU_chiar_se_citesc_restantele(buclele):
    assert len(_tc._restante()) > 40, "cititorul de restanțe s-a rupt"
    assert _commituri_de_la("HEAD~1") >= 0, "numărătoarea de commituri nu funcționează"


def test_nicio_decizie_NOUA_nu_ramane_pe_zero(buclele):
    noi = sorted(buclele - _NENUMARATE, key=lambda x: int(x[1:]))
    assert not noi, (
        "restanțe deblocate de DECIZIE care au trecut de %d commituri cu `reluări: 0`: %s\n"
        "Dacă decizia a fost cerută din nou, urcă `reluări`. Dacă a fost dată, scrie-o în "
        "restanță ȘI în DECIZII.md. Un contor pe zero face o buclă de trei luni să arate ca o "
        "cerere de-o zi — R9 stă așa de 133 de commituri." % (_PRAG_COMMITURI, noi))


def test_fotografia_nu_pastreaza_morti(buclele):
    """A doua direcție: o restanță care a primit contor (sau s-a închis) iese din fotografie."""
    iesite = sorted(_NENUMARATE - buclele, key=lambda x: int(x[1:]))
    assert not iesite, (
        "intrări din fotografie care nu mai sunt buclă tăcută: %s — scoate-le din `_NENUMARATE`. "
        "(Dacă tocmai ai urcat contorul sau ai închis restanța: ăsta e mesajul care ți-o cere.)"
        % iesite)


def test_CALIBRARE_o_restanta_cu_contor_NU_e_bucla():
    """Direcția «acuză pe nedrept»: R33 are `reluări: 1` și 78 de commituri — nu intră în clasă."""
    corp = _tc._restante()["R33"][1]
    assert int((_tc._camp(corp, "reluări") or "0").strip("* ")) >= 1
    assert "R33" not in _NENUMARATE, "o restanță cu contor a ajuns în fotografia buclelor tăcute"


def test_CALIBRARE_pragul_lasa_afara_restantele_proaspete(buclele):
    """Cealaltă direcție: o restanță deschisă azi n-are cum să fi fost reluată."""
    proaspete = []
    for cod, (_t, corp) in _tc._restante().items():
        c = (_tc._camp(corp, "deschisă pe commit") or "").strip("`*— ")
        if c and _commituri_de_la(c) < _PRAG_COMMITURI:
            proaspete.append(cod)
    assert not (set(proaspete) & buclele), (
        "restanțe proaspete raportate ca buclă: %s" % sorted(set(proaspete) & buclele))
