# -*- coding: utf-8 -*-
"""GARD [01.09.2026, R108]: pragul de încadrare ca mijloc fix are o SINGURĂ sursă.

**Cum arăta.** Aceeași valoare stătea în trei locuri, cu trei adevăruri diferite:

  `COTE["plafon_mijloc_fix"]`      canonic   data **01.01.2026 — greșită**   citit de **nimeni**
  `obiecte_inventar.PRAG_NOU`      copie     data 25.02.2026, corectă        citit
  `mijloace_fixe_import_api`       copie     **fără dată**                   citit, la avertisment

*O lege aplicată în trei locuri produce, la următoarea modificare, cifra validă și falsă: două se
actualizează, a treia nu, și nimic nu se aprinde. Iar canonicul necitit e configurația cea mai
proastă — se poate strica fără ca cineva să observe, fiindcă nimeni nu se sprijină pe el.* Data
canonicului **era** greșită, exact așa.

**CE FACE IMPOSIBIL:**
  1. o a doua definiție a pragului, oriunde în afara registrului;
  2. întoarcerea la un prag **fără dată** — cel care spunea „sub plafon 5000" și pentru bunuri
     intrate când plafonul era 2.500;
  3. ca valoarea canonică să rămână fără consumatori — starea în care s-a putut strica în tăcere.

**CE NU FACE, declarat:** nu verifică dacă pragul e *corect* — asta o fac citirea la sursă și
`test_vigoare_articole_registru`. Verifică doar că e **unul singur**.
"""
import ast
import datetime
import io
import os
import sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAD not in sys.path:
    sys.path.insert(0, _RAD)

from core import obiecte_inventar as oi  # noqa: E402
from core.common import COTE  # noqa: E402

#: Modulele care ATING pragul. Nici unul n-are voie să-l redefinească.
CONSUMATORI = ("core/obiecte_inventar.py", "core/mijloace_fixe_import_api.py")


def _valori_prag():
    return {float(v) for _d, v, _t in COTE["plafon_mijloc_fix"]}


def _constante_de_modul(cale):
    """[(nume, valoare, linie)] — constante de modul cu valoare numerică."""
    arb = ast.parse(io.open(cale, encoding="utf-8").read())
    out = []
    for n in arb.body:
        if not isinstance(n, ast.Assign):
            continue
        v = n.value
        val = None
        if isinstance(v, ast.Constant) and isinstance(v.value, (int, float)) \
           and not isinstance(v.value, bool):
            val = float(v.value)
        elif isinstance(v, ast.Call) and getattr(getattr(v, "func", None), "id", "") == "Decimal" \
                and v.args and isinstance(v.args[0], ast.Constant):
            try:
                val = float(v.args[0].value)
            except (TypeError, ValueError):
                val = None
        if val is None:
            continue
        for t in n.targets:
            if getattr(t, "id", None):
                out.append((t.id, val, n.lineno))
    return out


# ── SURSA E UNA SINGURĂ ────────────────────────────────────────────────────────────────────────

def test_niciun_consumator_nu_redefineste_pragul():
    """Pe **AST**, nu pe text: o valoare scrisă ca `5000`, `5000.0` sau `Decimal("5000")` e aceeași
    valoare, iar un test pe șiruri ar vedea trei lucruri diferite."""
    valori = _valori_prag()
    assert valori, "[anti-vacuu] registrul n-are nicio valoare pentru `plafon_mijloc_fix`"
    rele = []
    for rel in CONSUMATORI:
        for nume, val, ln in _constante_de_modul(os.path.join(_RAD, rel)):
            if val in valori:
                rele.append("  %s:%d `%s` = %s" % (rel, ln, nume, val))
    assert not rele, (
        "pragul de mijloc fix e redefinit în afara registrului:%s%s%s"
        "Sursa unică e `COTE['plafon_mijloc_fix']`, citită prin `obiecte_inventar.prag_mf(la_data)`. "
        "O a doua copie se desincronizează la prima modificare de lege — și exact așa canonicul a "
        "ajuns cu data greșită, necitit de nimeni." % (chr(10), chr(10).join(rele), chr(10)))


def test_valoarea_canonica_ARE_consumatori():
    """Starea în care pragul s-a putut strica în tăcere: nimic nu-l citea. Se cere ca graful de
    dependențe să vadă cel puțin o funcție care îl atinge — altfel `reverificare` îl clasează
    `NECUNOSCUT` pe consecință, adică *nu se poate spune ce strică o valoare expirată*."""
    from core import dependenti_act as da
    d = da.dependenti(tip="OUG", nr=8, an=2026, art="28") or {}
    fn = d.get("functii") or []
    assert fn, (
        "`plafon_mijloc_fix` n-are niciun consumator în graf. O valoare fiscală pe care n-o citește "
        "nimeni se poate strica fără ca nimic să se aprindă — și s-a stricat: data ei era 01.01.2026 "
        "în loc de 25.02.2026, iar consumatorii își duplicaseră cifra.")
    # Pe STRUCTURĂ, nu pe subșir: intrările au forma `modul.py::functie`, deci se compară MULȚIMEA
    # de module. Prima formă era `any("obiecte_inventar" in f for f in fn)` — un `in` pe text, care
    # a urcat clichetul 50 la 1223 și a picat poarta. *Făcut de mine, în gardul unei unificări.*
    module = {f.split("::")[0] for f in fn}
    assert module >= {"obiecte_inventar.py"}, (
        "poarta unică `obiecte_inventar.prag_mf` nu mai apare printre consumatori: %s"
        % sorted(module))


# ── PRAGUL E DEPENDENT DE DATĂ ─────────────────────────────────────────────────────────────────

def test_pragul_se_schimba_la_DATA_din_lege():
    """Confruntare între registru și data citită la sursă. Marcajul din forma consolidată a Codului
    fiscal spune `(la 25-02-2026, Litera b), Alineatul (2), Articolul 28 ...)`. Un prag fără dată —
    forma dinainte din modulul de import — dădea 5.000 și pentru bunurile intrate în ianuarie."""
    from decimal import Decimal
    assert oi.prag_mf(datetime.date(2026, 2, 24)) == Decimal("2500")
    assert oi.prag_mf(datetime.date(2026, 2, 25)) == Decimal("5000")
    assert oi.prag_mf(datetime.date(2026, 2, 26)) == Decimal("5000")


def test_CALIBRARE_incadrarea_se_schimba_cu_pragul():
    """Direcția care contează pentru contabil: un bun de 3.000 lei e mijloc fix înainte de 25.02.2026
    și obiect de inventar după. Dacă asta nu se schimbă, pragul nu e folosit nicăieri."""
    assert oi.e_obiect_inventar(3000, datetime.date(2026, 2, 24)) is False
    assert oi.e_obiect_inventar(3000, datetime.date(2026, 2, 25)) is True


# ── NECUNOSCUTUL SE POATE NUMI ─────────────────────────────────────────────────────────────────

def test_necunoscutul_se_poate_NUMI_nu_doar_mosteni():
    """Pentru date anterioare primei valori din registru (01.01.2015) răspunsul e **moștenit**, nu
    verificat la sursă — un mijloc fix intrat în 2008 avea alt prag (1.800 lei, HG 105/2007), care nu
    e în registru. Comportamentul se păstrează, dar necunoașterea devine **exprimabilă**: fără asta,
    importul ar scrie „sub plafon" cu aceeași încredere ca pentru un an verificat."""
    assert oi.prag_mf_cunoscut(datetime.date(2026, 2, 24)) is True
    assert oi.prag_mf_cunoscut(datetime.date(2008, 1, 1)) is False
    from decimal import Decimal
    assert oi.prag_mf(datetime.date(2008, 1, 1)) == Decimal("2500"), (
        "comportamentul pentru date vechi s-a schimbat — forma dinainte întorcea cea mai veche "
        "valoare cunoscută, iar unificarea nu avea voie s-o schimbe pe furiș")


def test_ANTI_VACUU_registrul_chiar_are_doua_praguri():
    """Dacă registrul ar avea o singură intrare, toate testele de mai sus ar compara 5000 cu 5000 și
    n-ar discrimina nimic."""
    assert len(COTE["plafon_mijloc_fix"]) >= 2, (
        "[anti-vacuu] registrul are %d intrări pentru `plafon_mijloc_fix` — probele de dată n-ar "
        "putea deosebi nimic" % len(COTE["plafon_mijloc_fix"]))
