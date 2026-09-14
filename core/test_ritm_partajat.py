# -*- coding: utf-8 -*-
"""E1 — ritmul se numără O SINGURĂ DATĂ, pe amândouă procesele, și nu se golește la repornire.

CE ERA ÎNAINTE, măsurat pe `6b9ba2da` înainte de reparație: trei dicționare la nivel de modul —
`main._reset_rate`, `main._cui_rate`, `core.uc_comun._magic_rate` — iar limitatorul care le folosea
își scria premisa în docstring: *„in-memory, **single worker**"*. Premisa murise la **P6 valul 3**,
când unitatea a primit `Environment=WEB_CONCURRENCY=2`:

  · cu două procese, fiecare cu dicționarul lui, **pragul efectiv era dublu**;
  · contoarele se goleau la fiecare repornire, deci la fiecare publicare;
  · iar `main.py:1563-1566` curăța doar IP-ul care cerea atunci, deci dicționarul creștea nemărginit,
    cheiat pe o valoare venită din antetul cererii.

Aceeași clasă fusese deja recunoscută și reparată alături: blocarea la autentificare a trecut în
bază pe 12.09 (`main.py:1274` scrie măsurătoarea: *„cinci eșecuri pe A, `blocat=False` pe B"*).
E1 aplică același tipar pe cele trei limitatoare.

CE PĂZEȘTE FIȘIERUL ĂSTA, în ordinea în care contează:
  1. `RATE_LIMIT_IN_PROCES = 0` — structural, pe AST. Un dicționar de modul folosit iar ca stare de
     ritm, sau un limitator chemat cu un OBIECT în loc de numele limitatorului, pică.
  2. **Global între procese** — două procese REALE, nu două obiecte în același interpretor.
  3. **Supraviețuiește repornirii** — un proces nou vede ce a numărat unul care nu mai există.
  4. **Paritate**: pragurile (5 și 10), fereastra (900 s) și răspunsul (`429`, același text).
  5. **Cursa e scoasă din construcție**, nu micșorată: opt fire simultane trec exact cinci.
  6. **Fail-closed**: la bază căzută se ridică, nu se răspunde „nu e prea des".
"""
from __future__ import annotations

import ast
import io
import json
import os
import re
import subprocess
import sys
import threading

import pytest

RADACINA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RADACINA not in sys.path:
    sys.path.insert(0, RADACINA)

from core import db as _db  # noqa: E402
from core import stare_partajata as _sp  # noqa: E402

CHEIE_PROBA = "ztest_e1_ritm"
IP_PROBA = "203.0.113.7"          # TEST-NET-3, RFC 5737 — nu poate fi un IP real de client


# ============================================================
#  1. RATE_LIMIT_IN_PROCES — structural, pe AST
# ============================================================
def _fisiere_aplicatie():
    out = [os.path.join(RADACINA, "main.py")]
    cdir = os.path.join(RADACINA, "core")
    for f in sorted(os.listdir(cdir)):
        if f.endswith(".py") and not f.startswith(("test_", "scan_")):
            out.append(os.path.join(cdir, f))
    return out


def stari_de_ritm_in_proces(surse=None):
    """[(fișier, linia, ce)] — stare de ritm ținută în memoria procesului.

    Două forme, fiindcă defectul le poate lua pe amândouă:
      · un dicționar de modul al cărui nume vorbește despre ritm (`*_rate`, `*_ritm`);
      · un apel de limitare care primește un OBIECT în loc de numele limitatorului — adică un
        depozit pasat, adică iar o stare în proces, oricum s-ar numi.
    """
    out = []
    for cale, text in (surse or [(c, io.open(c, encoding="utf-8", errors="ignore").read())
                                 for c in _fisiere_aplicatie()]):
        try:
            arb = ast.parse(text)
        except SyntaxError:
            continue
        rel = os.path.relpath(cale, RADACINA) if os.path.isabs(cale) else cale
        for n in arb.body:
            if not isinstance(n, ast.Assign) or not isinstance(n.value, ast.Dict):
                continue
            if n.value.keys:
                continue
            for t in n.targets:
                if isinstance(t, ast.Name) and re.search(r"rate|ritm", t.id, re.I):
                    out.append((rel, n.lineno, "dicționar de modul `%s = {}`" % t.id))
        for x in ast.walk(arb):
            if not isinstance(x, ast.Call) or not x.args:
                continue
            nume = getattr(x.func, "id", None) or getattr(x.func, "attr", None)
            if nume != "_rate_limit_email":
                continue
            if not isinstance(x.args[0], ast.Constant):
                out.append((rel, x.lineno, "limitator chemat cu un OBIECT: %s"
                            % ast.unparse(x.args[0])))
    return out


def test_RATE_LIMIT_IN_PROCES_e_zero():
    """Criteriul de ieșire al lui E1, scris ca cifră."""
    gasite = stari_de_ritm_in_proces()
    assert not gasite, (
        "stare de ritm în memoria procesului (%d) — cu doi lucrători, pragul se dublează și se "
        "golește la repornire:\n  %s"
        % (len(gasite), "\n  ".join("%s:%d  %s" % g for g in gasite)))


def test_CALIBRARE_detectorul_vede_amandoua_formele():
    """Pe univers FABRICAT, în ambele direcții — altfel «0» ar putea însemna că nu știe să caute."""
    rau = [("zt_fals.py", "_cui_rate = {}\n\ndef f(request):\n"
                          "    _rate_limit_email(_cui_rate, request)\n")]
    gasite = stari_de_ritm_in_proces(rau)
    feluri = {g[2].split(":")[0].split("`")[0].strip() for g in gasite}
    assert len(gasite) == 2, "detectorul a găsit %d din 2 forme: %s" % (len(gasite), gasite)
    assert len(feluri) == 2, "cele două forme nu se disting: %s" % feluri

    bun = [("zt_bun.py", 'def f(request):\n    _rate_limit_email("magic_link", request)\n')]
    assert not stari_de_ritm_in_proces(bun), "forma CORECTĂ e raportată ca defect"


# ============================================================
#  De aici în jos: probe pe bază
# ============================================================
def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn() as c:
            _sp.aplica_ddl(c)
        return True
    except Exception:
        return False


_CU_BAZA = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


def _curata(cheie=CHEIE_PROBA, ip=None):
    with _db.get_conn() as c, c.cursor() as cur:
        if ip:
            cur.execute("DELETE FROM public.cereri_ritm WHERE cheie = %s AND ip = %s", (cheie, ip))
        else:
            cur.execute("DELETE FROM public.cereri_ritm WHERE cheie = %s", (cheie,))


@pytest.fixture
def curat():
    _curata()
    yield
    _curata()


# ── 2+3. procese reale: global între ele, și supraviețuiește repornirii ──────────────────────
COPIL = r'''
import json, os, sys
sys.path.insert(0, %(rad)r)
from core import db
db.init_pool()
from core import stare_partajata as sp
cheie, ip, n, maxreq = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
raspunsuri = []
for _ in range(n):
    with db.get_conn() as c:
        raspunsuri.append(sp.ritm_incape(c, cheie, ip, maxreq=maxreq))
with db.get_conn() as c:
    vazute = sp.cereri_in_fereastra(c, cheie, ip)
print("__REZULTAT__" + json.dumps({"pid": os.getpid(), "incape": raspunsuri, "vazute": vazute}))
''' % {"rad": RADACINA}


def _copil(cheie, ip, n, maxreq=_sp.PRAG_RITM):
    cale = os.path.join(RADACINA, ".lant_tmp_e1_copil.py")
    with open(cale, "w") as f:
        f.write(COPIL)
    try:
        r = subprocess.run([sys.executable, cale, cheie, ip, str(n), str(maxreq)],
                           capture_output=True, text=True, cwd=RADACINA,
                           env=dict(os.environ), timeout=180)
        linii = [x for x in r.stdout.splitlines() if x.startswith("__REZULTAT__")]
        if not linii:
            raise AssertionError("procesul-copil n-a raportat nimic.\nstdout: %s\nstderr: %s"
                                 % (r.stdout[-800:], r.stderr[-1500:]))
        return json.loads(linii[-1][len("__REZULTAT__"):])
    finally:
        if os.path.exists(cale):
            os.remove(cale)


@_CU_BAZA
def test_A_ritmul_numarat_de_un_proces_e_vazut_de_celalalt(curat):
    """Criteriul cerut: numărarea e GLOBALĂ între cei doi lucrători.

    Forma dinainte ar fi trecut proba asta cu 5 pe A **și** 5 pe B — exact dublarea pragului."""
    a = _copil(CHEIE_PROBA, IP_PROBA, _sp.PRAG_RITM)
    assert a["incape"] == [True] * _sp.PRAG_RITM, (
        "procesul A trebuia să admită %d cereri, a dat %s" % (_sp.PRAG_RITM, a["incape"]))

    b = _copil(CHEIE_PROBA, IP_PROBA, 1)
    assert b["pid"] != a["pid"], "cele două probe au rulat în același proces"
    assert b["incape"] == [False], (
        "procesul B a admis cererea a %d-a — nu vede ce a numărat A, deci starea e încă în "
        "memoria unui proces" % (_sp.PRAG_RITM + 1))
    assert b["vazute"] == _sp.PRAG_RITM, (
        "B vede %d cereri, nu %d — s-a pierdut sau s-a adăugat un rând"
        % (b["vazute"], _sp.PRAG_RITM))


@_CU_BAZA
def test_B_numaratoarea_supravietuieste_disparitiei_procesului(curat):
    """«Nu se resetează la deploy». Procesul care a numărat **nu mai există** când se întreabă."""
    a = _copil(CHEIE_PROBA, IP_PROBA, 3)
    assert a["incape"] == [True, True, True]
    # procesul a murit; nimic din memoria lui n-a rămas. Un al treilea proces continuă numărătoarea.
    b = _copil(CHEIE_PROBA, IP_PROBA, 3)
    assert b["pid"] != a["pid"]
    assert b["incape"] == [True, True, False], (
        "după trei cereri într-un proces mort, al doilea proces a admis %s — numărătoarea a "
        "repornit de la zero" % b["incape"])


COPIL_HTTP = r'''
import json, os, sys
sys.path.insert(0, %(rad)r)
from core import db
db.init_pool()                       # pool propriu, FARA `lifespan` -> fara bucle de fundal
import main
from fastapi.testclient import TestClient
cl = TestClient(main.app)            # fara `with`: lifespan NU ruleaza

n = int(sys.argv[1])
coduri, texte = [], []
for _ in range(n):
    r = cl.post("/public/magic-link", json={"email": "ztest_e1_inexistent@invalid"})
    coduri.append(r.status_code)
    if r.status_code == 429:
        texte.append((r.json() or {}).get("detail"))
print("__REZULTAT__" + json.dumps({"pid": os.getpid(), "coduri": coduri, "texte": texte}))
''' % {"rad": RADACINA}


def _copil_http(n):
    cale = os.path.join(RADACINA, ".lant_tmp_e1_http.py")
    with open(cale, "w") as f:
        f.write(COPIL_HTTP)
    try:
        r = subprocess.run([sys.executable, cale, str(n)], capture_output=True, text=True,
                           cwd=RADACINA, env=dict(os.environ), timeout=300)
        linii = [x for x in r.stdout.splitlines() if x.startswith("__REZULTAT__")]
        if not linii:
            raise AssertionError("procesul-copil n-a raportat nimic.\nstdout: %s\nstderr: %s"
                                 % (r.stdout[-800:], r.stderr[-1500:]))
        return json.loads(linii[-1][len("__REZULTAT__"):])
    finally:
        if os.path.exists(cale):
            os.remove(cale)


@_CU_BAZA
def test_A2_pe_RUTA_intreaga_al_saselea_apel_cade_in_PROCESUL_CELALALT():
    """Aceeași afirmație ca `test_A`, dar pe calea reală: rută → gardă → bază, în două procese.

    Proba de mai sus arată că *mecanismul* numără global. Asta arată că **ruta îl folosește** — și
    verifică, în același timp, contractul HTTP: `429` cu textul de dinainte. Forma din memorie ar fi
    răspuns `200` aici, fiindcă al doilea proces pornea cu dicționarul gol."""
    _curata(cheie="magic_link", ip="testclient")
    try:
        a = _copil_http(_sp.PRAG_RITM)
        assert a["coduri"] == [200] * _sp.PRAG_RITM, (
            "procesul A a răspuns %s; primele %d cereri trebuiau admise"
            % (a["coduri"], _sp.PRAG_RITM))

        b = _copil_http(1)
        assert b["pid"] != a["pid"], "cele două procese sunt de fapt unul singur"
        assert b["coduri"] == [429], (
            "procesul B a răspuns %s în loc de 429 — nu vede ce a numărat A" % b["coduri"])
        assert b["texte"] == ["Prea multe cereri. Încearcă din nou peste câteva minute."], (
            "textul refuzului s-a schimbat: %s" % b["texte"])
    finally:
        _curata(cheie="magic_link", ip="testclient")


# ── 4. paritate: praguri, fereastră, răspuns ────────────────────────────────────────────────
@_CU_BAZA
def test_C_pragul_si_fereastra_sunt_CELE_DE_DINAINTE(curat):
    """5 la 900 s, iar `/public/verifica-cui` cu pragul lui, 10. Cifrele nu s-au atins."""
    assert (_sp.PRAG_RITM, _sp.FEREASTRA_RITM_SEC) == (5, 900)
    with _db.get_conn() as c:
        admise = [_sp.ritm_incape(c, CHEIE_PROBA, IP_PROBA) for _ in range(7)]
    assert admise == [True] * 5 + [False, False], admise

    _curata(ip=IP_PROBA)
    with _db.get_conn() as c:
        admise10 = [_sp.ritm_incape(c, CHEIE_PROBA, IP_PROBA, maxreq=10) for _ in range(12)]
    assert admise10 == [True] * 10 + [False, False], admise10


@_CU_BAZA
def test_C_cererea_REFUZATA_nu_se_numara(curat):
    """Ca în memorie: a șasea e refuzată și **nu** se scrie. Altfel pragul ar deveni «a șasea de
    când am început să număr», iar fereastra nu s-ar mai goli niciodată sub presiune."""
    with _db.get_conn() as c:
        for _ in range(9):
            _sp.ritm_incape(c, CHEIE_PROBA, IP_PROBA)
        assert _sp.cereri_in_fereastra(c, CHEIE_PROBA, IP_PROBA) == _sp.PRAG_RITM


def test_C_mesajul_de_refuz_e_neschimbat():
    """Contractul HTTP: același cod și același text — citite ca STRUCTURĂ din `_rate_limit_email`.

    Nu ca șir căutat în fișier: un `"..." in sursa` ar trece și pe o potrivire din proza unui
    comentariu, și ar rata un mesaj mutat într-o constantă. Aici se ia nodul `raise`."""
    arb = ast.parse(io.open(os.path.join(RADACINA, "main.py"), encoding="utf-8").read())
    fn = next((n for n in arb.body
               if isinstance(n, ast.FunctionDef) and n.name == "_rate_limit_email"), None)
    assert fn is not None, "`_rate_limit_email` a dispărut din `main.py`"
    refuzuri = [x.exc for x in ast.walk(fn)
                if isinstance(x, ast.Raise) and isinstance(x.exc, ast.Call)
                and getattr(x.exc.func, "id", None) == "HTTPException"]
    assert len(refuzuri) == 1, "aștept exact un refuz în limitator, am găsit %d" % len(refuzuri)
    cod, mesaj = refuzuri[0].args[0], refuzuri[0].args[1]
    assert isinstance(cod, ast.Constant) and cod.value == 429, ast.dump(cod)
    assert isinstance(mesaj, ast.Constant) and mesaj.value == (
        "Prea multe cereri. Încearcă din nou peste câteva minute."), ast.dump(mesaj)


# ── 5. expirarea ────────────────────────────────────────────────────────────────────────────
@_CU_BAZA
def test_D_ce_a_iesit_din_fereastra_nu_mai_contribuie(curat):
    with _db.get_conn() as c:
        for _ in range(_sp.PRAG_RITM):
            _sp.ritm_incape(c, CHEIE_PROBA, IP_PROBA)
        with c.cursor() as cur:      # le împing în trecut, dincolo de fereastră
            cur.execute("UPDATE public.cereri_ritm SET la = now() - interval '20 minutes' "
                        " WHERE cheie = %s AND ip = %s", (CHEIE_PROBA, IP_PROBA))
        assert _sp.cereri_in_fereastra(c, CHEIE_PROBA, IP_PROBA) == 0
        assert _sp.ritm_incape(c, CHEIE_PROBA, IP_PROBA) is True


@_CU_BAZA
def test_D_expirarea_e_si_MARGINITA_nu_doar_filtrata(curat):
    """Defectul D2 din audit: forma din memorie nu uita niciodată un IP. Aici, orice scriere
    șterge TOATE rândurile ieșite din fereastră — ca la `login_esec`."""
    vechi = "198.51.100.%d"
    try:
        with _db.get_conn() as c:
            with c.cursor() as cur:
                for i in range(20):
                    cur.execute("INSERT INTO public.cereri_ritm (cheie, ip, la) "
                                "VALUES (%s, %s, now() - interval '30 minutes')",
                                (CHEIE_PROBA, vechi % i))
                cur.execute("SELECT count(*) FROM public.cereri_ritm WHERE cheie = %s",
                            (CHEIE_PROBA,))
                assert cur.fetchone()[0] == 20
            _sp.ritm_incape(c, CHEIE_PROBA, IP_PROBA)      # o singură scriere, alt IP
            with c.cursor() as cur:
                cur.execute("SELECT count(*) FROM public.cereri_ritm WHERE cheie = %s",
                            (CHEIE_PROBA,))
                ramase = cur.fetchone()[0]
        assert ramase == 1, ("după o scriere au rămas %d rânduri; cele 20 expirate trebuiau "
                             "șterse, nu doar ignorate la citire" % ramase)
    finally:
        _curata()


# ── 6. cursa ────────────────────────────────────────────────────────────────────────────────
@_CU_BAZA
def test_E_din_opt_fire_simultane_trec_exact_cinci(curat):
    """Cursa e SCOASĂ din construcție, nu micșorată.

    Fără blocajul consultativ pe `(cheie, ip)`, două cereri simultane pot număra amândouă 4 și pot
    trece amândouă de prag — sub `READ COMMITTED`, fiecare instrucțiune își ia propriul instantaneu.
    Cu el, cererile aceluiași IP se serializează; două IP-uri diferite nu se așteaptă."""
    k = 8
    rez, erori = [], []
    porneste = threading.Event()

    def fir():
        porneste.wait()
        try:
            with _db.get_conn() as c:
                rez.append(_sp.ritm_incape(c, CHEIE_PROBA, IP_PROBA))
        except Exception as e:      # noqa: BLE001 — orice eroare de fir e rezultat, nu tăcere
            erori.append(repr(e))

    fire = [threading.Thread(target=fir) for _ in range(k)]
    for f in fire:
        f.start()
    porneste.set()
    for f in fire:
        f.join(timeout=60)

    assert not erori, "fire căzute: %s" % erori[:3]
    assert len(rez) == k, "doar %d din %d fire au raportat" % (len(rez), k)
    assert sum(rez) == _sp.PRAG_RITM, (
        "au trecut %d cereri din %d simultane, cu pragul %d — cursa n-a fost scoasă"
        % (sum(rez), k, _sp.PRAG_RITM))
    with _db.get_conn() as c:
        assert _sp.cereri_in_fereastra(c, CHEIE_PROBA, IP_PROBA) == _sp.PRAG_RITM


# ── 7. fail-closed ──────────────────────────────────────────────────────────────────────────
class _BazaCazuta(Exception):
    pass


class _ConnCrapata:
    def cursor(self, *a, **k):
        raise _BazaCazuta("baza e jos")


def test_F_la_baza_cazuta_RIDICA_nu_raspunde_ca_nu_e_prea_des():
    """Doctrina modulului, aceeași ca la `login_blocat`: un refuz de a răspunde n-are voie să
    devină «nu e prea des». Ar transforma o bază căzută într-o poartă deschisă."""
    with pytest.raises(_BazaCazuta):
        _sp.ritm_incape(_ConnCrapata(), CHEIE_PROBA, IP_PROBA)
