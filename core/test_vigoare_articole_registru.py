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
    ("CF", "84^1"): datetime.date(2026, 1, 1),  # [3d] masurat la sursa 29.09.2026: forma din Legea 239/2025, alin.(3)/(5) in vigoare de la 01.01.2026
    ("CF", "97"): datetime.date(2018, 1, 1),
    # [lot 19, 02.10.2026] masurate la sursa cu scripts/vigoare_articol.py pe formele din corpus:
    ("CF", "500^2"): datetime.date(2026, 1, 1),        # lit.a)-b) modificate de Legea 239/2025 pct.51, in vigoare 01.01.2026
    ("Legea 296/2023", "III"): None,                     # actul modificator: articolul fara marcaj de modificare
    ("CF", "138"): None,
    ("CF", "156"): None,
    ("CF", "220^3"): None,
    ("CF", "282"): datetime.date(2026, 3, 1),
    ("CF", "291"): datetime.date(2025, 8, 1),
    ("OUG 89/2025", "III"): None,
    ("OUG 156/2024", "LXVI"): datetime.date(2025, 1, 10),
    ("Legea 201/2025", "I"): None,
    # CITIT LA SURSĂ 01.09.2026, dar NU de instrument — de mine, actul întreg (2.899 de caractere,
    # șase articole). Art. 1 nu poartă niciun marcaj: e un ordin nou, publicat 05.11.2025, nemodificat.
    # INSTRUMENTUL NU CONFIRMĂ, și dezacordul se scrie aici în loc să fie neted: `vigoare_articol.py`
    # răspunde `REFUZ … 0 titluri de articol`, fiindcă `_TITLURI_NUMARATE` cere cuvântul „Articolul",
    # iar Monitorul Oficial scrie „Art. 1. —". Deci ORICE formă de MO e ciot prin construcție, pentru
    # toate articolele ei. Refuzul e în direcția sigură (nu inventează un „STABIL"), dar motivul pe
    # care îl dă e fals — v. R111.
    ("Ordin 1604/2025", "1"): None,
    # [R1, 10.10.2026] constantele ancorate au intrat în registru (`common.ancoreaza` scrie în COTE) — articolele lor, măsurate la
    # sursă cu `scripts/vigoare_articol.py` pe formele din corpus (CF amprenta 2393786755c97dc5, Legea 70/2015 661b016484f74b52,
    # Legea 165/2018 52dde38076983b91, OUG 24/2026 2f502e5f0d81ed0f); data = cel mai recent marcaj „modificat la” din articol:
    ("CF", "18^1"): datetime.date(2026, 2, 25),        # alin.(5) modificat la 25-02-2026
    ("CF", "64"): datetime.date(2018, 3, 23),          # alin.(1) modificat la 23-03-2018
    ("CF", "69^2"): None,
    ("CF", "72^1"): datetime.date(2018, 3, 23),        # capitolul II^1 completat (OUG 18/2018) la 23-03-2018
    ("CF", "77"): datetime.date(2023, 1, 1),           # articolul modificat (OG 16/2022 pct.40) la 01-01-2023
    ("CF", "84"): datetime.date(2026, 1, 1),           # alin.(1) și (3) modificate la 01-01-2026
    ("CF", "100"): None,
    ("CF", "110"): datetime.date(2025, 8, 1),          # alin.(2), (2^2) modificate la 01-08-2025
    ("CF", "111"): datetime.date(2024, 12, 5),         # lit.d modificată la 05-12-2024
    ("CF", "118"): datetime.date(2025, 1, 1),          # lit.b modificată la 01-01-2025
    ("CF", "119"): datetime.date(2024, 1, 1),          # alin.(2), (3) modificate la 01-01-2024
    ("CF", "331"): datetime.date(2023, 1, 1),          # lit.e teza introductivă modificată la 01-01-2023
    ("Legea 70/2015", "3"): datetime.date(2023, 12, 15),   # lit.e modificată la 15-12-2023
    ("Legea 70/2015", "4"): datetime.date(2023, 12, 15),   # alin.(1), (4) modificate la 15-12-2023
    ("Legea 70/2015", "4^2"): datetime.date(2023, 12, 15), # alin.(1) modificat la 15-12-2023
    ("Legea 165/2018", "19"): None,
    ("OUG 24/2026", "2"): None,
}

# Un `Temei` care citează un act MODIFICATOR plus un număr de articol al Codului fiscal se citește ca
# «CF art. N, așa cum l-a modificat actul». Aceleași două câmpuri poartă lucruri din acte diferite —
# observație de modelare, scrisă în CONFORMITATE la 50.
#
# MULȚIMEA NU MAI E SCRISĂ AICI (31.08.2026). Trăia în două locuri — aici și, implicit, în capul
# celui care scria următorul instrument —, iar al doilea n-a știut de ea: `scan_pereche_act_articol`
# a luat perechile literal și a raportat șase defecte de date care nu existau. *O convenție ținută
# în două locuri se desparte în tăcere.* Acum e una singură, importată.
from core import scan_pereche_act_articol as S  # noqa: E402


def _cheie(t):
    """DELEGAT, nu reimplementat (01.09.2026, R111). Mulțimea fusese mutată într-un singur loc pe
    31.08 tocmai ca o convenție să nu se despartă în tăcere — dar **regula** care o folosea rămăsese
    scrisă de două ori, iar clauza lui 291 s-a despărțit exact pe jumătatea nemutată. Acum se cheamă
    funcția, nu se copiază corpul ei."""
    return S.cheie_articol(getattr(t, "tip", None), getattr(t, "nr", None),
                           getattr(t, "an", None), getattr(t, "art", None))


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
