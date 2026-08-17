# -*- coding: utf-8 -*-
"""core/test_mesaje_fara_camp_intern.py — GARD: mesaj user-facing FĂRĂ nume intern de câmp.

CRITERIUL (CLAUDE.md Regula 14 pct.4): sunt DEFECT „numele intern al câmpului sau valorile
din bază arătate utilizatorului". Contabilul nu trebuie să vadă în mesajul de eroare un
identificator snake_case de coloană/câmp (`tip_decont`, `regim_fiscal`, `cont_stoc_nou`,
`zi_emitere`, `firma_profil`) — trebuie eticheta umană („Periodicitate decont TVA",
„Regim fiscal", „Contul de stoc nou", „Ziua emiterii").

Gardul REFOLOSEȘTE extracția din test_diacritice_afisate._candidati() — aceleași șiruri
USER-FACING prin ROL SINTACTIC (HTTPException detail; valoarea unei chei de afișare din dict:
mesaj/eroare/detail/...; corpul unei excepții de business). NU se uită la log/assert/docstring
și sare fișierele test_*.py — la fel ca gardul de diacritice.

SEMNAL: un token snake_case = literă mică urmată de ≥1 segment `_<litere/cifre>`. Proza
românească nu folosește underscore; un astfel de token într-un mesaj afișat e aproape sigur
nume de câmp/coloană intern. Codurile (cheia „cod") nu intră (nu-s în _DISPLAY_KEYS).

BASELINE: gol. La 2026-08-17, după reparație (vector_fiscal_api ×3, facturi_recurente,
stocuri_cv_api), suita e la 0. Orice mesaj NOU care scapă un nume de câmp va PICA gardul.
Excepție reală (un identificator care e legitim ÎN mesaj, ex. o coloană din fișierul propriu
al utilizatorului) se adaugă EXPLICIT în _BASELINE cu motiv — nu se relaxează criteriul.
"""
import glob
import re

import pytest

from core.test_diacritice_afisate import _candidati

# token snake_case: literă mică, apoi cel puțin un segment `_<alnum>`
_SNAKE = re.compile(r"\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b")

# excepții reale: temei-DIAGNOSTIC afișat pe calea except->ROȘU a unui BUG DE COD (nu flux normal
# de contabil). Aici numele simbolului/fișierului de test e semnal DELIBERAT pentru dezvoltatorul
# care triază semnalul roșu; `mesaj`-ul alăturat e deja uman. Vezi control_fiscal_api.py:621 și
# control_incrucisat.py:1264 (contractul reconcilierii: recalculul NU ridică). Restul = clichet la 0.
_BASELINE = {
    "Puntea control_incrucisat.reconciliaza_declaratii a ridicat; contractul ei e să nu ridice."
    " Un except->gri ar ascunde ruptura ca verdict permanent gri.",
    "Contractul reconciliere: recalculul (reconciliaza) NU ridică; dacă ridică, e derivă de"
    " semnătură / bug de cod. Un except->gri l-ar ascunde ca verdict permanent gri - vezi"
    " core/test_control_incrucisat_wiring.py.",
}


def _camp_intern(s):
    """Token-ii snake_case dintr-un MESAJ AFIȘAT (proză). Un șir fără spațiu e un
    identificator/cheie structurală (ex. cheia unui dict de răspuns), NU text pe ecran —
    nu se flaghează. Contează doar numele de câmp scăpat în proza afișată."""
    if " " not in s.strip():
        return []
    return _SNAKE.findall(s)


def _flagate():
    out = []
    for fn, ln, s in _candidati():
        if s in _BASELINE:
            continue
        toks = _camp_intern(s)
        if toks:
            out.append((fn, ln, s, toks))
    return out


def test_autotest_criteriu_are_dinti():
    """Dinți: mesaj cu nume de câmp snake_case PICĂ; proză umană / cod / o vorbă TREC."""
    # TREBUIE flagate:
    assert _camp_intern("tip_decont trebuie să fie 'lunar' sau 'trimestrial'")
    assert _camp_intern("cont_stoc_nou lipsă")
    assert _camp_intern("regim_fiscal invalid")
    # NU trebuie flagate:
    assert not _camp_intern("Periodicitate decont TVA: alege Lunar sau Trimestrial (obligatoriu)."), \
        "eticheta umană, fără underscore"
    assert not _camp_intern("Ziua emiterii trebuie să fie între 1 și 28."), "proză umană"
    assert not _camp_intern("D300 nu se poate genera pe perioadă zero"), "cod, nu snake_case"
    assert not _camp_intern("art. 322 alin. 2"), "referință legală, fără underscore"


def test_niciun_mesaj_user_facing_cu_nume_intern_de_camp():
    if not glob.glob("core/*.py"):
        pytest.skip("core/*.py absent (rulare în afara rădăcinii)")
    fl = _flagate()
    raport = "\n".join("  %s:%d  %r  <- nume intern de câmp: [%s]" % (fn, ln, s, ",".join(t))
                       for fn, ln, s, t in fl)
    assert not fl, (
        "Mesaj(e) USER-FACING cu nume intern de câmp (snake_case). Contabilul vede eticheta "
        "umană, nu numele coloanei (Regula 14 pct.4). Înlocuiește cu eticheta din UI:\n" + raport)
