# -*- coding: utf-8 -*-
"""GARD (20.08.2026): METODA_VERIFICARE.md nu descrie o lume care nu mai există.

DE CE. Un document de metodă îmbătrânește mai tăcut decât codul: nimic nu-l rulează. Cele trei acte au
trăit luni întregi doar într-un docstring, iar restul metodei doar în practică — „ce nu e scris nu se
poate contrazice". Acum e scris; pasul următor e ca scrisul să nu poată minți.

CE PĂZEȘTE. Fiecare fișier pe care metoda îl numește ca exemplu viu (observatorul, harta, comparatorul,
gărzile citate) trebuie să existe. Dacă unul e șters sau redenumit, metoda PICĂ — nu rămâne o pagină care
descrie un instrument dispărut.

CE NU PĂZEȘTE, declarat: că fișierul mai face ce spune metoda că face. Un `test_pastila_gri.py` golit ar
trece pe aici. Asta e treaba propriilor lui teste, nu a gardului ăstuia.
"""
import os
import re

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DOC = os.path.join(_RAD, "METODA_VERIFICARE.md")


def _text():
    with open(_DOC, encoding="utf-8") as f:
        return f.read()


def test_documentul_exista_si_nu_s_a_golit():
    assert os.path.exists(_DOC), "METODA_VERIFICARE.md a dispărut"
    t = _text()
    assert len(t) > 4000, "metoda s-a golit (%d octeți) — a fost trunchiată?" % len(t)


_SCOASE_START = "<!-- CAI-SCOASE:START"
_SCOASE_STOP = "<!-- CAI-SCOASE:STOP"


def _cai_scoase():
    """Căile pe care metoda le numește ca **scoase**, dintr-un bloc DECLARAT, nu ghicite din proză.

    [03.09.2026] O metodă trebuie să poată scrie și de ce a scos un instrument — altfel deciziile de
    arhitectură n-ar avea unde să trăiască. Blocul e structural (delimitatori), nu textual: nu se
    caută cuvântul „scos" prin paragrafe, cum ar cere §23 să NU se facă."""
    t = _text()
    if _SCOASE_START not in t or _SCOASE_STOP not in t:
        return set()
    bloc = t[t.index(_SCOASE_START):t.index(_SCOASE_STOP)]
    return set(re.findall(r"`((?:core|frontend_test|static|scripts)/[\w/]+\.(?:py|js))`", bloc))


def test_caile_declarate_SCOASE_chiar_lipsesc():
    """Direcția opusă, și e chiar rostul blocului: dacă un instrument declarat scos REAPARE, metoda
    minte în celălalt sens — iar minciuna aia e mai greu de văzut decât o cale ruptă."""
    scoase = _cai_scoase()
    reaparute = sorted(c for c in scoase if os.path.exists(os.path.join(_RAD, c)))
    assert not reaparute, (
        "METODA_VERIFICARE.md le declară SCOASE, dar există pe disc:\n  " + "\n  ".join(reaparute)
        + "\n\nOri s-a schimbat decizia (atunci se schimbă metoda ÎNTÂI, acolo unde e scris de ce), "
          "ori cineva a refăcut un mecanism scos deliberat.")


def test_fisierele_numite_de_metoda_exista():
    """Miezul. Căile citate cu backtick în document trebuie să existe pe disc — afară de cele
    declarate SCOASE în blocul `CAI-SCOASE`, care sunt cerute exact invers, mai sus."""
    cai = sorted(set(re.findall(r"`((?:core|frontend_test|static)/[\w/]+\.(?:py|js))`", _text()))
                 - _cai_scoase())
    lipsa = [c for c in cai if not os.path.exists(os.path.join(_RAD, c))]
    assert not lipsa, (
        "METODA_VERIFICARE.md numește fișiere care nu există:\n  " + "\n  ".join(lipsa)
        + "\n\nOri s-au redenumit (actualizează metoda), ori s-au șters (metoda descrie un instrument"
        + " dispărut — și atunci întrebarea e ce a luat locul lui).")


def test_gardul_chiar_vede_caile():
    """Anti-vacuu: dacă regexul se rupe, testul de mai sus trece pe zero căi și nu verifică nimic."""
    cai = set(re.findall(r"`((?:core|frontend_test|static)/[\w/]+\.(?:py|js))`", _text()))
    assert len(cai) >= 5, "metoda pare să nu mai citeze niciun fișier (%d) — regexul s-a rupt?" % len(cai)
    # cele trei acte sunt coloana vertebrală: dacă vreunul lipsește din text, metoda nu mai e metodă
    for cheie in ("frontend_test/vizual/scan_casete.py",
                  "frontend_test/vizual/harta_casete.py",
                  "core/test_harta_casete.py"):
        assert cheie in cai, "cele trei acte nu mai sunt toate numite în metodă: lipsește %s" % cheie
