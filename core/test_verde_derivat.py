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

[P13b, 28.09.2026] ACEASTA LIMITA E INCHISA: scanul pe tot `static/js` exista acum
(`scripts/scan_p13_eticheta_verdict.py::scaneaza_verdict_pozitiv`), gardat de
`test_niciun_verdict_pozitiv_din_contoare_sau_fallback` de mai jos. Clasa „verdict pozitiv
ales din contoare/fallback" e prinsa MECANIC, nu doar pe fisier+forma.
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
    # [05.10.2026] DS cap.8 v2.70: o cifră e TEXT, deci tokenii de text (--rosu, --galben-text), nu cei de semafor (contrast
    # sub 4,5:1). Forma CONDIȚIONATĂ — pe care o calibrează testul — e aceeași; s-a schimbat doar tokenul.
    assert 't.respinse ? "var(--rosu)" : null' in t, \
        "cabinet.js: fratele conditionat `respinse` a disparut — calibrarea nu mai tine"
    assert 't.in_asteptare ? "var(--galben-text)" : null' in t, \
        "cabinet.js: fratele conditionat `in_asteptare` a disparut"
    c = _citeste("capacitate.js")
    assert 'cab.de_validat ? "var(--galben-text)" : null' in c, \
        "capacitate.js: fratele conditionat `de_validat` a disparut"


def test_verdele_din_semafor_card_atarna_de_verde_explicit():
    """[P13b, 28.09.2026 — RECLASIFICARE arhitect] Forma veche a acestui test afirma ca verdele din
    `semafor.js` e LEGITIM „cand toate numaratorile sunt zero" (`if (!active.length)`). Arhitectul a
    rasturnat presupunerea: rosu=galben=0 NU inseamna verificat — ignora `sumar.gri` (firme al caror
    rezumat lipseste/e invechit, produs de uc_control_fiscal) si trateaza un sumar ABSENT (`{}`) ca
    verde. Asta e 27+31 cu stare falsa activa. Clasa corecta: pozitivul apare DOAR dintr-un `verde`
    explicit primit de la backend; altfel „nu se poate verifica"."""
    t = _citeste("semafor.js", minim=400)
    assert "const active = perechi.filter" in t, \
        "semafor.js: numaratorile negative nu mai sunt filtrate — forma s-a rupt"
    assert re.search(r"if\s*\(\s*\(verde\s*\|\|\s*0\)\s*>\s*0\s*&&\s*mesajOk\s*\)", t), \
        "semafor.js: verdele pozitiv nu mai e gardat pe `verde` explicit — poate reaparea pe zero/absenta"
    assert "nu se poate verifica" in t, \
        "semafor.js: ramura de absenta (\"nu se poate verifica\") a disparut — absenta ar redeveni verde"
    assert not re.search(r"if\s*\(!active\.length\)\s*\{\s*return[^\n]*pct-verde", t), \
        "semafor.js: verdele reapare direct pe `!active.length` — clasa reparata a regresat"


# ── P13b: gard pe CLASA (scan pe tot static/js), inchide limita declarata in antet ──
import sys as _sys  # noqa: E402
_sys.path.insert(0, os.path.join(RAD, "scripts"))
import scan_p13_eticheta_verdict as _scan  # noqa: E402


def test_niciun_verdict_pozitiv_din_contoare_sau_fallback():
    """[P13b] Clasa: in tot `static/js`, un TEXT-VERDICT pozitiv (la zi / fara probleme / in regula)
    apare DOAR gardat de o stare pozitiva explicita (`=== \"verde\"` / camp `verde`/`ok`), niciodata
    din absenta rosului/galbenului, din zero sau dintr-un fallback. Scanul deriva mecanic; BAD = gol."""
    bad, _good = _scan.scaneaza_verdict_pozitiv()
    assert bad == [], "verdict pozitiv ales din contoare/fallback (P13b):\n" + "\n".join(
        "  %s:%d  %s" % (f, i, s) for f, i, s in bad)


def test_ANTI_VACUU_scanul_vede_cazul_derivat_corect():
    """Anti-vacuu (interdictia 76): daca detectorul n-ar parsa nimic, BAD ar fi gol degeaba. Dovada ca
    vede: firme.js deriva verdictul din flag-ul EXPLICIT `ok` -> trebuie in GOOD, niciodata in BAD.
    (Ancora era control.js:47 „totul la zi" pana in P13c; atunci textul a fost centralizat in verdict.js
    si nu mai e literal in control.js, deci scanul nu-l mai clasifica acolo.)"""
    bad, good = _scan.scaneaza_verdict_pozitiv()
    good_firme = [s for f, i, s in good if f.endswith("firme.js")]
    assert good_firme, "scanul nu vede firme.js in GOOD - detector vacuu (nu parseaza nimic)"
    assert not any(f.endswith("firme.js") for f, i, _s in bad), \
        "scanul a prins gresit firme.js in BAD - calibrarea negativa (verdict din flag ok) a cazut"
