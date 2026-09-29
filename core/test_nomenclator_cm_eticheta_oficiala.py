# -*- coding: utf-8 -*-
"""GARD [3b]: etichetele Nomenclatorului 9 din core/nomenclator_cm.py == lista OFICIALA ANAF.

Confruntare STRUCTURALA (§23): lista se PARSEAZA din anaf_surse/d112_struct_anaf.txt (blocul
'Nomenclator 9'), nu se compara cu un sir hardcodat. Comparatie pe text DEBURAT (fara diacritice,
spatii colapsate): eticheta afisata e diacritizata (garda de diacritice o cere), sursa ANAF e ASCII;
ce se compara e IDENTITATEA tipului de concediu. MUTATIE: revert oricare eticheta (ex. 16='Boală
infectocontagioasă') -> rosu.
"""
import os
import re
import sys
import unicodedata

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAD not in sys.path:
    sys.path.insert(0, _RAD)
from core import nomenclator_cm as ncm  # noqa: E402

_DOC = os.path.join(_RAD, "anaf_surse", "d112_struct_anaf.txt")


def _debura(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().replace("\u2013", "-").replace("\u2014", "-")
    s = re.sub(r"\s*/\s*", "/", s)
    return re.sub(r"\s+", " ", s).strip()


def _curata(txt):
    txt = re.sub(r"\(.*?\)", " ", txt, flags=re.S)
    txt = re.sub(r"\bDin\s+\d{2}/\d{4}\b", " ", txt)
    txt = re.sub(r"\bG\d(?:\.\d)?\b", " ", txt)
    txt = re.sub(r"(?:\s+\d{1,4})+\s*$", " ", txt)
    return _debura(txt)


def _oficial():
    doc = open(_DOC, encoding="utf-8", errors="replace").read()
    m = re.search(r"Nomenclator 9 -.*?(?=Nomenclator 10)", doc, flags=re.S)
    assert m, "blocul Nomenclator 9 nu s-a gasit"
    out, cod, buf = {}, None, []
    for linie in m.group(0).splitlines():
        mc = re.match(r"\s*(\d{2})\s+(\S.*)$", linie)
        if mc:
            if cod is not None:
                out[cod] = _curata(" ".join(buf))
            cod, buf = mc.group(1), [mc.group(2)]
        elif cod is not None:
            buf.append(linie)
    if cod is not None:
        out[cod] = _curata(" ".join(buf))
    return out


def test_etichetele_sunt_cele_oficiale():
    of = _oficial()
    lipsa = [c for c in ncm.CODURI if c not in of]
    assert not lipsa, "coduri fara corespondent in Nomenclator 9 parsat: %s" % lipsa
    assert len(of) >= 20, "parser rupt: doar %d coduri oficiale" % len(of)
    gresite = []
    for cod, d in ncm.CODURI.items():
        if _debura(d["eticheta"]) != of[cod]:
            gresite.append((cod, d["eticheta"], of[cod]))
    assert not gresite, "etichete != Nomenclator 9 (cod, al_nostru, oficial):\n" + "\n".join(
        "  %s: %r != %r" % g for g in gresite)
