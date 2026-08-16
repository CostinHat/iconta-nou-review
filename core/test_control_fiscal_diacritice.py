# -*- coding: utf-8 -*-
"""core/test_control_fiscal_diacritice.py — GARD: mesajele de VERDICT ale controlului fiscal
au diacritice si NU scurg nume interne de camp catre utilizator.

DE CE EXISTA SEPARAT de gardul canonic de diacritice (core/test_diacritice_afisate.py):
  Gardul canonic recunoaste text user-facing prin ROL sintactic — `detail` de HTTPException,
  valori de dict sub chei de afisare (mesaj/eroare/cauza/motiv/...), corpuri de exceptii business.
  Mesajele de verdict din control_fiscal_api.py NU stau in aceste roluri: sunt argumente
  POZITIONALE catre emitentii `gri()`/`neaplic()`/`neaplic_luna()`/`emite_tva()`, valori din
  dict-ul de constante `_NEAP_FORMA_SIMPLA` (chei "d100"/"d101"/"d406", nu chei de afisare) si
  RETURN-uri de string din builderul `_existenta_fapt`. Deci gardul canonic le SCANEAZA (fisierul
  e in `core/*.py`) dar NU le vede ca user-facing -> punct orb.

PUNCT ORB DOVEDIT 17.08.2026 (audit vizual tenant_004, ecranul Control fiscal):
  "Platitor de TVA necompletat - nu pot sti daca datorezi D300." si
  "necunoscut declarat: ... completati data inceperii TVA (platitor_tva_anaf_inceput) in vectorul
  fiscal." — proza romaneasca FARA diacritice, plus numele coloanei din baza (`platitor_tva_anaf_inceput`)
  aratat contabilului in loc de label-ul UI „Data inregistrarii in scopuri de TVA".

TEMEI: DS cap.1 („Textele afisate folosesc diacritice romanesti complete; codul/comentariile/
markerii — fara diacritice") + Regula 14 pct.4 (numele intern de camp aratat utilizatorului = defect).

CRITERIU (mai TARE decat flag() canonic — aici stim ca fiecare mesaj de verdict e o fraza RO):
  fiecare sir-proza (are spatiu) emis ca verdict TREBUIE:
    (1) sa contina cel putin o diacritica (a/a/i/s/t);
    (2) sa NU contina un identificator snake_case (nume intern de camp/coloana din baza).
"""
import ast
import os
import re

import pytest

from core.test_diacritice_afisate import _DIAC   # sursa unica pentru setul de diacritice

_FISIER = "core/control_fiscal_api.py"
_EMITENTI = {"gri", "neaplic", "neaplic_luna", "emite_tva"}
_DICTE_MESAJ = {"_NEAP_FORMA_SIMPLA"}
_VARS_MESAJ = {"cauza_r", "cauza", "motiv", "mesaj"}   # variabile-mesaj date apoi unui emitent
# nume intern scurs: identificator cu 2+ segmente legate cu _ (platitor_tva_anaf_inceput, tva_data_inceput)
_SNAKE = re.compile(r"[a-z]{2,}(?:_[a-z0-9]{2,}){1,}")
_BASELINE = set()   # sir de verdict lasat ASCII cu motiv; gol = clichet la 0


def _proza(v):
    return isinstance(v, str) and " " in v.strip() and any(c.islower() for c in v)


def _e_container(node):
    return isinstance(node, (ast.Dict, ast.List, ast.Tuple, ast.Set))


def _mesaje_verdict():
    """[(linie, text)] — sirurile-proza emise ca verdict:
       args ale emitentilor + valori din dictele de mesaje + return-uri de string (nu de container)."""
    if not os.path.exists(_FISIER):
        return None
    tree = ast.parse(open(_FISIER, encoding="utf-8").read())
    out = []

    def _cules(nod):
        for sub in ast.walk(nod):
            if isinstance(sub, ast.Constant) and _proza(sub.value):
                out.append((sub.lineno, sub.value))

    for n in ast.walk(tree):
        # 1) argumente ale emitentilor de verdict
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in _EMITENTI:
            for a in n.args:
                _cules(a)
        # 2) dictele de constante-mesaj (_NEAP_FORMA_SIMPLA): valori-proza;
        #    + variabile-mesaj (cauza_r/cauza/motiv/mesaj) date ulterior unui emitent
        if isinstance(n, ast.Assign):
            nume = {t.id for t in n.targets if isinstance(t, ast.Name)}
            if nume & _DICTE_MESAJ and isinstance(n.value, ast.Dict):
                for v in n.value.values:
                    _cules(v)
            if nume & _VARS_MESAJ and not _e_container(n.value):
                _cules(n.value)
        # 3) return-uri care intorc UN STRING (nu un container) — builderii de mesaj (_existenta_fapt)
        if isinstance(n, ast.Return) and n.value is not None and not _e_container(n.value):
            _cules(n.value)
    return out


def test_autotest_criteriu_are_dinti():
    """Dinti: ASCII fara diacritice PICA; corect + label uman TREC."""
    assert not any(c in _DIAC for c in "Platitor de TVA necompletat"), "sample ASCII n-are diacritice"
    assert _SNAKE.search("(platitor_tva_anaf_inceput)"), "snake_case trebuie prins"
    assert any(c in _DIAC for c in "Plătitor de TVA necompletat"), "sample corect are diacritice"
    assert not _SNAKE.search("Data înregistrării în scopuri de TVA"), "label uman NU e snake_case"


def test_mesaje_verdict_control_fiscal_au_diacritice_si_fara_nume_intern():
    mesaje = _mesaje_verdict()
    if mesaje is None:
        pytest.skip("%s absent (rulare in afara radacinii)" % _FISIER)
    assert mesaje, "niciun mesaj de verdict colectat — colectorul e rupt (ar masca regresii)"
    fara_diac = [(ln, s) for ln, s in mesaje
                 if s not in _BASELINE and not any(c in _DIAC for c in s)]
    scurgeri = [(ln, s, _SNAKE.search(s).group()) for ln, s in mesaje if _SNAKE.search(s)]
    raport = ""
    if fara_diac:
        raport += ("\nMesaj(e) de verdict FARA diacritice (DS cap.1 — text pe ecran cu diacritice; "
                   "codul/markerii ASCII):\n" +
                   "\n".join("  %s:%d  %r" % (_FISIER, ln, s) for ln, s in fara_diac))
    if scurgeri:
        raport += ("\nNume intern de camp scurs utilizatorului (Regula 14 pct.4 — foloseste label-ul UI):\n" +
                   "\n".join("  %s:%d  %r  <- %s" % (_FISIER, ln, s, nm) for ln, s, nm in scurgeri))
    assert not (fara_diac or scurgeri), raport
