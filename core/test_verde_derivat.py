# -*- coding: utf-8 -*-
"""Verdele de semafor se DERIVĂ; unde nu se poate deriva, semaforul LIPSEȘTE.

  core/test_verde_derivat.py

De ce există (Costin, 24.08.2026): *„Un semafor verde care nu compară nimic spune «am verificat și e
în regulă» — exact P6, verdele care afirmă. Iar contabilul nu are cum să distingă un verde derivat de
unul scris. Absența unui indicator e onestă. Un verde care nu verifică nimic nu e."*

Cele trei instanțe (R30, lărgită 24.08.2026): `cabinet.js` × 2, `capacitate.js` × 1. Niciuna n-a fost
vreodată derivată — instanța 1 vine din commitul rădăcină `cbf24ce` (01.07.2026), celelalte două din
`a6d9c2c0` (13.07.2026), în aceeași zi în care fratele lor condiționat era scris corect un rând mai sus.

LIMITA, DECLARATĂ (interdicția 76 — calibrare pe propriul mod de eșec): gardul e pinuit pe **fișier și
formă**, nu pe **clasă**. Nu vede a patra apariție într-un fișier nou, și nu vede o rescriere care
păstrează sensul dar schimbă textul. Ce l-ar închide e un scan pe tot `static/js/`, care nu există încă
— până atunci cifra „3" e un plafon inferior.
"""
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JS = os.path.join(RAD, "static", "js", "ecrane")


def _citeste(nume, minim=2000):
    """`minim` e PER FIȘIER, nu global.

    Prima formă a gardului avea un prag unic de 2000 și a picat pe `semafor.js` (771 de caractere —
    un helper de 16 rânduri, legitim mic). Adică gardul a eșuat exact pe **propriul** mod de eșec:
    un prag calibrat pe fișierele mari raportează „gol" despre unul mic și sănătos. Pragul rămâne,
    fiindcă închide clasa reală (fișier golit sau redenumit), dar se dă pe măsura fișierului.
    """
    cale = os.path.join(JS, nume)
    assert os.path.exists(cale), "fisier inexistent: %s — gardul masoara o lume pe care n-o vede" % cale
    with open(cale, encoding="utf-8") as f:
        t = f.read()
    assert len(t) > minim, "fisier suspect de scurt (%d < %d): %s — anti-vacuu" % (len(t), minim, nume)
    return t


# ── instanța 1 — verdele care apărea și pe eșecul apelului ────────────────────
def test_cabinet_verdele_de_echipa_nu_mai_apare_pe_esec():
    t = _citeste("cabinet.js")
    assert not re.search(
        r'zona\.innerHTML\s*=\s*randuri\s*\|\|\s*`<span class="cab-stare">'
        r'<span class="cab-pct pct-verde">', t), \
        "cabinet.js: verdele „Echipa activa\" a redevenit neconditionat — apare si cand apelul arunca (P6)"


def test_cabinet_verdele_de_echipa_atarna_de_o_stare_derivata():
    """Nu ajunge să lipsească forma veche: verdele trebuie să depindă de un semnal care spune că
    S-A comparat ceva. Fără aserțiunea asta, gardul ar trece și dacă semaforul ar fi șters cu totul."""
    t = _citeste("cabinet.js")
    assert re.search(r"let\s+derivat\s*=\s*false", t), \
        "cabinet.js: lipseste starea `derivat` — nu se mai poate deosebi „zero real\" de „n-am putut verifica\""
    assert re.search(r"if\s*\(sm\s*&&\s*sm\.ok\)\s*\{\s*\n\s*derivat\s*=\s*true", t), \
        "cabinet.js: `derivat` nu se mai aprinde pe raspunsul valid al semaforului de echipa"
    m = re.search(r"^.*zona\.innerHTML\s*=\s*randuri.*$", t, re.M)
    assert m is not None, "cabinet.js: atribuirea semaforului de echipa a disparut"
    assert "derivat" in m.group(0), \
        "cabinet.js: atribuirea semaforului de echipa nu mai consulta `derivat`"


# ── instanțele 2 și 3 — verde pe zero ─────────────────────────────────────────
def test_cabinet_cifrele_verzi_sunt_conditionate():
    t = _citeste("cabinet.js")
    for camp in ("aprobate", "depuse"):
        assert not re.search(r'cifra\(t\.%s[^)]*?,\s*"var\(--verde\)"\s*\)' % camp, t), \
            "cabinet.js: `%s` picteaza verde neconditionat — `0` iese verde" % camp
        assert re.search(r't\.%s\s*\?\s*"var\(--verde\)"\s*:\s*null' % camp, t), \
            "cabinet.js: `%s` nu mai are forma conditionata" % camp


def test_capacitate_depuse_luna_conditionat():
    t = _citeste("capacitate.js")
    assert not re.search(r'celulaCifra\(cab\.depuse_luna[^)]*?,\s*"var\(--verde\)"\s*\)', t), \
        "capacitate.js: `depuse_luna` picteaza verde neconditionat — `0 depuse` iese verde"
    assert 'cab.depuse_luna ? "var(--verde)" : null' in t, \
        "capacitate.js: `depuse_luna` nu mai are forma conditionata"


# ── calibrare NEGATIVĂ: membri pe care gardul NU trebuie să-i găsească ────────
def test_fratii_deja_corecti_raman_corecti():
    """Cele trei instanțe au trăit lângă forme CORECTE, scrise în aceeași zi. Dacă formele alea
    dispar, aserțiunile de mai sus măsoară alt fișier decât cel pe care au fost calibrate."""
    t = _citeste("cabinet.js")
    assert 't.respinse ? "var(--rosu-semafor)" : null' in t, \
        "cabinet.js: fratele conditionat `respinse` a disparut — calibrarea nu mai tine"
    assert 't.in_asteptare ? "var(--galben)" : null' in t, \
        "cabinet.js: fratele conditionat `in_asteptare` a disparut"
    c = _citeste("capacitate.js")
    assert 'cab.de_validat ? "var(--galben)" : null' in c, \
        "capacitate.js: fratele conditionat `de_validat` a disparut"


def test_verdele_din_semafor_card_ramane_derivat():
    """`semafor.js` are un verde LEGITIM: apare doar când toate numărătorile sunt zero, adică după ce
    s-a comparat ceva. Gardul nu trebuie să-l confunde cu clasa reparată — dacă i-ar cere scoaterea,
    ar cere scoaterea unui verde corect."""
    t = _citeste("semafor.js", minim=400)
    assert "const active = perechi.filter" in t, \
        "semafor.js: verdele nu mai e conditionat de numaratori — a devenit scris"
    assert "if (!active.length)" in t, \
        "semafor.js: conditia care face verdele derivat a disparut"
