# -*- coding: utf-8 -*-
"""GARDĂ pentru interdicția 50 — confirmarea unei valori e ULTERIOARĂ ultimei modificări a articolului.

Testul propriu-zis al interdicției nu e *ce spune articolul*, ci: **o valoare sprijinită pe un articol
modificat DUPĂ ce a fost confirmată ultima oară e o valoare pe care nimeni n-a mai privit-o de când
s-a schimbat temeiul.**

Datele de modificare de mai jos au fost citite **la sursă** pe 23.08.2026 — portalul pentru actele
mici, copia amprentată din corpus pentru Codul fiscal (2.552.897 de caractere, 1.849 de titluri de
articol; portalul nu-l servește ca pagină unică). Ele sunt **măsurători**, nu presupuneri, iar garda
le ține vii: dacă o valoare capătă un `verificat_la` mai vechi, sau dacă apare o valoare pe un articol
nemăsurat, testul o spune.

CE NU FACE: nu merge la sursă la fiecare poartă — ar cere rețea. Compară registrul cu ce s-a măsurat,
iar măsurătoarea se reface când se schimbă corpusul (`test_corpus_amprenta` păzește fișierul).
"""
import datetime

import pytest

from core import common as c

# articol -> ultima modificare, citită la sursă 23.08.2026. None = fără marcaj în corpul articolului.
MODIFICARI = {
    ("CF", "17"): None,
    ("CF", "28"): datetime.date(2026, 2, 25),
    ("CF", "51"): datetime.date(2026, 1, 1),
    ("CF", "78"): datetime.date(2021, 2, 26),
    ("CF", "97"): datetime.date(2018, 1, 1),
    ("CF", "138"): None,
    ("CF", "156"): None,
    ("CF", "220^3"): None,
    ("CF", "282"): datetime.date(2026, 3, 1),
    ("CF", "291"): datetime.date(2025, 8, 1),
    ("OUG 89/2025", "III"): None,
    ("OUG 156/2024", "LXVI"): datetime.date(2025, 1, 10),
    ("Legea 141/2025", "291"): None,
    ("Legea 201/2025", "I"): None,
}

# Un `Temei` care citează un act MODIFICATOR plus un număr de articol al Codului fiscal se citește ca
# «CF art. N, așa cum l-a modificat actul». Aceleași două câmpuri poartă lucruri din acte diferite —
# observație de modelare, scrisă în CONFORMITATE la 50.
_ART_DE_COD_FISCAL = {"97", "28", "282"}


def _cheie(t):
    tip = str(getattr(t, "tip", "") or "")
    art = str(getattr(t, "art", "") or "")
    if tip.upper() in ("CF", "CODUL FISCAL"):
        return ("CF", art)
    if art in _ART_DE_COD_FISCAL or (art == "291" and "227" in str(getattr(t, "nr", ""))):
        return ("CF", art)
    return ("%s %s/%s" % (tip, getattr(t, "nr", None), getattr(t, "an", None)), art)


def _data(v):
    if isinstance(v, datetime.date):
        return v
    if isinstance(v, str):
        try:
            return datetime.date(*map(int, v.split("-")))
        except ValueError:
            return None
    return None


def _perechi():
    out = []
    for cheie, intrari in sorted(c.COTE.items()):
        for it in intrari:
            if not isinstance(it, (list, tuple)) or len(it) < 3:
                continue
            t = it[2]
            if getattr(t, "art", None):
                out.append((cheie, _cheie(t), _data(getattr(t, "verificat_la", None))))
    return out


def test_fiecare_articol_din_registru_e_masurat_la_sursa():
    """ANTI-VACUU. O valoare pe un articol pe care nu l-a văzut nimeni la sursă nu are cum să fie
    verificată — și ar trece tăcut dacă garda ar sări peste ce nu cunoaște."""
    lipsa = sorted({k for _c, k, _v in _perechi() if k not in MODIFICARI})
    assert not lipsa, (
        "articole pe care stau valori din registru, nemăsurate la sursă: %s.\n"
        "Rulează `scripts/vigoare_articol.py <id sau cale> <art>` și adaugă data aici." % lipsa)


def test_confirmarea_e_ulterioara_ultimei_modificari():
    """MIEZUL interdicției 50."""
    rele = []
    for cheie, k, ver in _perechi():
        mod = MODIFICARI.get(k)
        if mod is None:
            continue
        if ver is None or ver < mod:
            rele.append("  %s (%s art.%s): modificat %s, confirmat %s"
                        % (cheie, k[0], k[1], mod, ver))
    assert not rele, ("valori sprijinite pe articole modificate DUPĂ ultima lor confirmare:\n"
                      + "\n".join(rele))


def test_masuratoarea_nu_e_goala():
    """ANTI-VACUU pe garda însăși: dacă registrul se golește, cele de sus trec pe zero rânduri."""
    p = _perechi()
    assert len(p) >= 20, "doar %d perechi valoare-articol în registru — parsarea s-a rupt" % len(p)
    assert len(MODIFICARI) >= 12, "tabelul de modificări s-a golit"


def test_datele_masurate_sunt_plauzibile():
    """O dată de modificare din viitor, sau dinaintea Codului fiscal, ar fi o greșeală de transcriere."""
    azi = datetime.date.today()
    cf = datetime.date(2015, 9, 8)
    rele = [(k, d) for k, d in MODIFICARI.items() if d and not (cf <= d <= azi)]
    assert not rele, "date de modificare implauzibile: %s" % rele
