# -*- coding: utf-8 -*-
"""GARD [28.08.2026]: inventarul gărzilor din `GARZI.md` nu poate rămâne în urma codului.

DE UNDE VINE. Registrul gardurilor a stat **șase zile** fără nicio intrare, în timp ce au intrat 80
de gărzi. Un registru cu șase zile în urmă se citește ca **complet** — aceeași clasă cu §14 din
METODA, aplicată chiar registrului care ține evidența regulilor păzite. Decizia lui Costin, 28.08:
*„rămâne viu, nu se îngheață."*

CE FACE IMPOSIBIL: o gardă nouă care intră fără să apară în inventar · o gardă ștearsă care rămâne
scrisă acolo · un bloc editat cu mâna, care ar arăta la fel de credibil ca unul generat.

CE NU FACE, declarat: **nu judecă dacă garda e bună.** Partea narativă a registrului — de ce s-a
construit, ce instanță a produs-o — rămâne a omului și **nu** e păzită de aici. Iar dacă cineva
adaugă o gardă și regenerează blocul fără să scrie nimic narativ, poarta trece: mecanismul apără
completitudinea listei, nu bogăția registrului.
"""
import io
import os
import sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_RAD, "scripts"))

import scan_garzi_inventar as sg  # noqa: E402

_DOC = os.path.join(_RAD, "GARZI.md")


def _text():
    return io.open(_DOC, encoding="utf-8").read()


def test_blocul_din_GARZI_e_identic_cu_ce_genereaza_instrumentul():
    """doc↔cod, caracter cu caracter. Regenerare:
    `./venv/bin/python scripts/scan_garzi_inventar.py --md`, rescris între marcaje."""
    doc = _text()
    assert sg.MARCA_START in doc and sg.MARCA_STOP in doc, (
        "GARZI.md n-are marcajele inventarului generat — a fost șters?")
    a = doc.index(sg.MARCA_START)
    b = doc.index(sg.MARCA_STOP) + len(sg.MARCA_STOP)
    din_doc, generat = doc[a:b], sg.redare_md()
    if din_doc != generat:
        ld, lg = din_doc.split(chr(10)), generat.split(chr(10))
        prima = next((i for i in range(max(len(ld), len(lg)))
                      if (ld[i] if i < len(ld) else None) != (lg[i] if i < len(lg) else None)), 0)
        raise AssertionError(
            "inventarul din GARZI.md diferă de ce generează scan_garzi_inventar.py --md, "
            "prima diferență la linia %d:%s  doc:     %r%s  generat: %r%s"
            "Regenerează: ./venv/bin/python scripts/scan_garzi_inventar.py --md"
            % (prima + 1, chr(10), ld[prima] if prima < len(ld) else "(lipsește)", chr(10),
               lg[prima] if prima < len(lg) else "(lipsește)", chr(10)))


def test_ANTI_VACUU_instrumentul_chiar_vede_garzile():
    inv = sg.inventar()
    assert len(inv) > 300, "doar %d gărzi văzute — s-a rupt calea" % len(inv)
    cai = {c for c, _d, _a in inv}
    assert cai >= {"core/test_garzi_inventar.py", "scripts/scan_garzi_inventar.py"}, (
        "instrumentul nu se vede nici pe sine — atunci nu vede nici restul")


def test_fara_docstring_nu_creste():
    """Clichet pe lipsă. Un fișier fără docstring de modul intră în inventar cu `—`: lista rămâne
    completă, dar afirmația lipsește. Cifra nu are voie să crească — o gardă nouă își spune ce
    păzește, altfel inventarul devine o listă de nume."""
    fara = sorted(c for c, _d, a in sg.inventar() if a == "—")
    assert len(fara) <= 12, (
        "gărzi fără docstring de modul: %d (clichetul e 12).\n  %s\n"
        "O gardă nouă își scrie prima frază — ce face imposibil." % (len(fara), "\n  ".join(fara)))
    assert len(fara) >= 12, (
        "au rămas doar %d fără docstring — coboară clichetul, ca următoarea creștere să fie prinsă "
        "de la cifra reală" % len(fara))
