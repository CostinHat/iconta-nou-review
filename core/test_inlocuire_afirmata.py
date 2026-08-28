# -*- coding: utf-8 -*-
"""GARD [YY/METODA §28, 28.08.2026]: o inlocuire de text intr-un document AFIRMA ca a gasit potrivirea.

DE UNDE VINE, cu instanta: `str.replace` nu se plange cand nu potriveste nimic - intoarce textul
neatins. Un script de peticit care nu verifica tipareste „OK" peste o modificare care nu s-a produs,
iar documentul ramane in forma VECHE, care de acum arata curenta. S-a intamplat de TREI ori pe
tabelul de restante din `PREDARE_LANT.md`, in trei ture consecutive.

CE PAZESTE: `scripts/inlocuieste.py` - unealta pe care regula o arata - trebuie sa RIDICE pe fiecare
din cele patru feluri de ratare. Daca verificarile ei ar fi scoase, regula ar deveni proza.

ASERTIUNILE DE AICI SE UITA LA DATE, NU LA MESAJ: `InlocuireRatata` poarta `motiv`, `gasite` si
`cerute`. Prima forma a gardului cauta siruri in mesajul exceptiei si a fost oprita de clichetul 50
la prima rulare a suitei - pe drept: ar fi pazit FORMULAREA, nu comportamentul, iar o rescriere a
mesajului ar fi trecut verde peste o unealta stricata.

CE NU FACE, si e masurat, nu presupus: NU pune un clichet pe „instrumente care inlocuiesc fara sa
verifice", fiindca in repo NU EXISTA niciunul. Masurat pe fisierele urmarite de git (fara `venv/`):
sase functii cheama `.replace`/`.sub` si scriu un fisier in acelasi loc, si toate sase sunt
formatari de sir sau transformari de continut (`core/duk.py` taie un mesaj de eroare, `main.py`
construieste raspunsuri, `portal_legislativ` curata HTML, `versioneaza_assets` face `re.sub` cu
raportare de erori) - **niciuna nu peticeste un document pe o ancora**. Clasa traieste in
scripturile de patch de fiecare tura, care nu sunt urmarite de git. *Un clichet peste un domeniu gol
ar fi chiar tiparul pe care il combat: un verde care nu poate deveni rosu.*
"""
import io
import os
import sys

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_RAD, "scripts"))

from inlocuieste import InlocuireRatata, inlocuieste, intre_marcaje  # noqa: E402

START, STOP = "<!-- x:start -->", "<!-- x:stop -->"


def _doc(tmp_path, text):
    c = tmp_path / "doc.md"
    io.open(str(c), "wb").write(text.encode("utf-8"))
    return str(c)


def test_ancora_care_NU_se_potriveste_RIDICA(tmp_path):
    """Instanta care a produs regula: documentul s-a schimbat sub script."""
    c = _doc(tmp_path, "un rând nou\n")
    with pytest.raises(InlocuireRatata) as e:
        inlocuieste(c, "un rând VECHI", "altceva")
    assert (e.value.motiv, e.value.gasite, e.value.cerute) == ("fara_potrivire", 0, 1), (
        "excepția nu poartă felul ratării ca DATE: %r" % ((e.value.motiv, e.value.gasite),))
    assert io.open(c, encoding="utf-8").read() == "un rând nou\n", "documentul a fost atins"


def test_ancora_AMBIGUA_RIDICA(tmp_path):
    """A doua ratare: ancora prinde mai mult decât credeai. `replace` le-ar schimba pe toate."""
    c = _doc(tmp_path, "da\nda\n")
    with pytest.raises(InlocuireRatata) as e:
        inlocuieste(c, "da", "nu")
    assert (e.value.motiv, e.value.gasite) == ("ambigua", 2)
    assert io.open(c, encoding="utf-8").read() == "da\nda\n"


def test_de_cate_ori_CERUT_explicit_trece(tmp_path):
    """Calibrare: cine chiar vrea două înlocuiri o spune, și atunci merge."""
    c = _doc(tmp_path, "da\nda\n")
    assert inlocuieste(c, "da", "nu", de_cate_ori=2) == 2
    assert io.open(c, encoding="utf-8").read() == "nu\nnu\n"


def test_inlocuirea_care_nu_schimba_nimic_RIDICA(tmp_path):
    """A treia ratare, cea mai tăcută: `vechi == nou`. Trece verde și nu face nimic."""
    c = _doc(tmp_path, "text\n")
    with pytest.raises(InlocuireRatata):
        inlocuieste(c, "text", "text")


def test_CRLF_RIDICA(tmp_path):
    """A patra: un patch rulat pe stație trece fișierul la CRLF în tăcere (regulă operațională
    veche, aici pe gardă)."""
    c = _doc(tmp_path, "a\r\nb\r\n")
    with pytest.raises(InlocuireRatata) as e:
        inlocuieste(c, "a", "z")
    assert e.value.motiv == "crlf", "felul ratarii nu e purtat ca data: %r" % e.value.motiv


def test_bloc_generat_fara_marcaje_RIDICA(tmp_path):
    """Perechea pentru generatoare: un bloc care nu-și mai găsește locul ar trece peste, iar
    documentul ar rămâne pe generația veche — exact clasa doc↔cod."""
    c = _doc(tmp_path, "fără marcaje\n")
    with pytest.raises(InlocuireRatata):
        intre_marcaje(c, START, STOP, START + "\nnou\n" + STOP)


def test_bloc_generat_se_rescrie_intre_marcaje(tmp_path):
    """Calibrarea pozitivă: cu marcajele la locul lor, blocul se schimbă și restul rămâne."""
    c = _doc(tmp_path, "înainte\n" + START + "\nvechi\n" + STOP + "\ndupă\n")
    intre_marcaje(c, START, STOP, START + "\nnou\n" + STOP)
    t = io.open(c, encoding="utf-8").read()
    assert "nou" in t and "vechi" not in t
    assert t.startswith("înainte\n") and t.endswith("\ndupă\n"), "a atins și textul din jur"


def test_marcaj_DUBLAT_RIDICA(tmp_path):
    """Două blocuri generate în același document: care dintre ele se rescrie? Niciunul, până se
    lămurește — altfel unul dintre ele rămâne vechi și arată curent."""
    c = _doc(tmp_path, START + "\na\n" + STOP + "\n" + START + "\nb\n" + STOP + "\n")
    with pytest.raises(InlocuireRatata):
        intre_marcaje(c, START, STOP, START + "\nnou\n" + STOP)
