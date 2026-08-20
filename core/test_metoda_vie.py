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


def test_fisierele_numite_de_metoda_exista():
    """Miezul. Căile citate cu backtick în document trebuie să existe pe disc."""
    cai = sorted(set(re.findall(r"`((?:core|frontend_test|static)/[\w/]+\.(?:py|js))`", _text())))
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
