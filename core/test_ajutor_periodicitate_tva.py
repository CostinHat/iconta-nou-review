# -*- coding: utf-8 -*-
"""GARD [06.09.2026, cerut de Costin]: aceeași alegere, pusă în două ecrane, poartă ACELAȘI criteriu.

**Ce s-a măsurat, la R167.** Periodicitatea decontului de TVA se cere în două locuri —
`migrare.js` (la preluarea firmei) și `date_firma.js` (la editarea vectorului fiscal). Criteriul
legal, art. 322, era scris **într-unul singur**. Omul care alege din al doilea ecran alege fără să
vadă regula după care se alege.

**De ce un gard, și nu doar o copiere.** „Verbatim" ținut de mână se erodează: cineva rescurtează
un text, altcineva îl rescrie „mai clar", iar cele două ecrane încep să spună lucruri diferite
despre aceeași normă — și nimic nu cade. Aici cade.

**CUM COMPARĂ, și de ce așa.** Textele se extrag prin **ancore de câmp**, nu căutând conținutul lor:
un gard care caută chiar textul pe care îl păzește trece dintr-un motiv străin (METODA §23). În
`migrare.js` ancora e eticheta «Periodicitate decont TVA», iar textul e primul `.camp-ajutor` de
după ea; în `date_firma.js` e valoarea `aj` a intrării `tip_decont` din tabelul `VECTOR`.
Comparația e pe textul **randat** — spațiile se normalizează, fiindcă unul trăiește într-un template
literal pe trei rânduri și celălalt într-un șir de o linie, iar HTML colapsează oricum spațiile.

**CE NU FACE, declarat:** nu verifică dacă textul e ADEVĂRAT. Că art. 322 spune ce spune textul e
treaba lui `core/test_c7_periodicitate_trimestriala.py::test_temeiul_citat_se_rezolva_in_corpus`,
care confruntă citarea cu corpusul. Aici se păzește doar că **cele două ecrane nu diverg**.

**Și o limită care e deja o restanță:** textul poartă cifra `100.000 euro`, care **n-are cheie în
registrul de cote** — interdicția 1, instanța consemnată pe `migrare.js`. Gardul ăsta face ca acum
cifra să trăiască în **două** locuri care nu pot diverge între ele; nu o face verificabilă. Rămâne
ce scrie în `CONFORMITATE.md`: ori cheia intră în registru, ori textul pierde cifra.
"""
import io
import os
import re

import pytest

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MIGRARE = "static/js/ecrane/migrare.js"
DATE_FIRMA = "static/js/ecrane/date_firma.js"

#: Ancora din `migrare.js`: eticheta câmpului. Dacă se schimbă, gardul PICĂ la extragere — n-are
#: voie să treacă verde raportând „nu l-am găsit, deci nu diferă".
_ANCORA_MIGRARE = "Periodicitate decont TVA"
_SPAN_AJUTOR = re.compile(r'<span class="camp-ajutor">(.*?)</span>', re.S)
#: Ancora din `date_firma.js`: intrarea `tip_decont` din tabelul `VECTOR`, apoi valoarea ei `aj`.
_INTRARE_TIP_DECONT = re.compile(r'\{\s*k:\s*"tip_decont".*?\}\s*,', re.S)
_AJ = re.compile(r'aj:\s*"((?:[^"\\]|\\.)*)"', re.S)


def _sursa(rel):
    return io.open(os.path.join(RAD, rel), encoding="utf-8").read()


def _decode_js(s):
    """`\\uXXXX` -> caracter, ca diacriticele scrise cu escape să conteze drept diacritice."""
    return re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), s)


def _randat(s):
    """Textul cum ajunge pe ecran: escape-urile decodate, spațiile colapsate."""
    return re.sub(r"\s+", " ", _decode_js(s)).strip()


def ajutorul_din_migrare():
    s = _sursa(MIGRARE)
    i = s.find(_ANCORA_MIGRARE)
    assert i > 0, ("ancora %r nu mai există în %s — eticheta câmpului s-a schimbat, iar gardul nu "
                   "mai știe pe ce compară" % (_ANCORA_MIGRARE, MIGRARE))
    m = _SPAN_AJUTOR.search(s, i)
    assert m, "nu există `.camp-ajutor` după eticheta periodicității în %s" % MIGRARE
    return _randat(m.group(1))


def ajutorul_din_date_firma():
    s = _sursa(DATE_FIRMA)
    m = _INTRARE_TIP_DECONT.search(s)
    assert m, "intrarea `tip_decont` nu mai există în tabelul VECTOR din %s" % DATE_FIRMA
    a = _AJ.search(m.group(0))
    assert a, "intrarea `tip_decont` din %s n-are `aj:` — câmpul a rămas fără criteriu" % DATE_FIRMA
    return _randat(a.group(1))


# ── MIEZUL ─────────────────────────────────────────────────────────────────────────────────────

def test_cele_doua_ecrane_spun_acelasi_criteriu():
    """Egalitate, nu apartenență: un `in` ar trece și dacă unul l-ar rezuma pe celălalt."""
    a, b = ajutorul_din_migrare(), ajutorul_din_date_firma()
    assert a == b, (
        "criteriul periodicității TVA diferă între ecrane — aceeași alegere, două reguli:\n"
        "  migrare.js   : %r\n  date_firma.js: %r" % (a, b))


# ── ANTI-VACUU ─────────────────────────────────────────────────────────────────────────────────

def test_ANTI_VACUU_textele_chiar_exista_si_citeaza_articolul():
    """Egalitatea de mai sus ar trece și pe două șiruri GOALE, sau pe două texte fără niciun temei.

    Se cere lungime și **exact două** citări ale articolului — alin. (1) pentru lună, alin. (2)
    pentru trimestru. `count()`, nu `in`: se cere numărul, nu prezența (METODA §23)."""
    a = ajutorul_din_migrare()
    assert len(a) > 120, "textul de ajutor e prea scurt ca să poarte criteriul: %r" % a
    assert a.count("art. 322") == 2, (
        "textul citează art. 322 de %d ori, nu de 2 (alin. 1 = luna, alin. 2 = trimestrul): %r"
        % (a.count("art. 322"), a))
    assert ajutorul_din_date_firma().count("art. 322") == 2


def test_CALIBRARE_comparatia_chiar_ar_pica():
    """Direcția inversă: normalizarea nu are voie să facă totul egal cu totul."""
    assert _randat("Lunar   (regula,\n  art. 322)") == "Lunar (regula, art. 322)"
    assert _randat("Lunar (regula, art. 322)") != _randat("Lunar (regula, art. 323)")
    assert _randat("Declara\\u021bii") == "Declarații", "escape-urile nu se decodează"


def test_CALIBRARE_extragerea_pica_daca_ancora_dispare(tmp_path, monkeypatch):
    """Un extractor care întoarce `""` pe ancoră lipsă ar face gardul să treacă verde despre o
    lume pe care n-o vede. Se cere să CRAPE."""
    monkeypatch.setattr("core.test_ajutor_periodicitate_tva._ANCORA_MIGRARE", "ancoră inexistentă")
    with pytest.raises(AssertionError):
        ajutorul_din_migrare()
