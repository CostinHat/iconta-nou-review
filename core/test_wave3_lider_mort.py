# -*- coding: utf-8 -*-
"""P6 valul 3 — un lider mort iese din registru acum, nu peste un sfert de ora.

CE S-A MASURAT PE PRODUCTIE (12.09.2026, de doua ori). `instante` isi retrage mortii de pe gazda
proprie — `retrage_mortii_de_pe_gazda`, adaugata in aceeasi zi dupa ce bratul four-way raportase un
proces mort ca viu. `instante_lider` n-avea perechea. Deci dupa fiecare repornire lease-ul ramanea
pe PID-ul mort pana la EXPIRARE: 900 s in care munca de fundal nu se facea deloc. Masurat:
`metrici_sanatate` n-a primit niciun rand intre 14:36 si 14:49, iar liderul citit din baza era un
proces care nu mai exista.

SI PROZA NU SE POTRIVEA CU PURTAREA. Comentariul de langa `LEASE_SEC` spune «destul de scurt cat un
lider mort sa fie inlocuit intr-un ciclu» — ciclul e 300 s, inlocuirea era la 900 s. Reparatia nu
scurteaza niciun termen ca sa iasa cifra: pe gazda proprie moartea nu se ghiceste, o stie sistemul
de operare. Termenul de 900 s ramane, si ramane singurul raspuns pentru un lider de pe ALTA gazda.

CE PROBEAZA FISIERUL: liderul viu NU e retras (altfel conducerea s-ar schimba la fiecare ciclu) ·
cel mort E retras · dupa retragere alt worker preia · exact unul preia, si cand se ingramadesc mai
multi · liderul de pe alta gazda nu se atinge (limita declarata) · si RED-proof: fara retragere,
preluarea NU e posibila — adica exact purtarea de pe `94d655a8`.
"""
from __future__ import annotations

import ast
import io
import json
import os
import subprocess
import sys
import tempfile
import time

import pytest

RADACINA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RADACINA)

from core import db as _db  # noqa: E402
from core import instante as _inst  # noqa: E402


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn() as c:
            _inst.aplica_ddl(c)
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")

ROL = "ztest_lider_mort"
GAZDA_STRAINA = "ztest-alta-gazda"


def _curata():
    with _db.get_conn() as c, c.cursor() as cur:
        cur.execute("DELETE FROM public.instante_lider WHERE rol = %s", (ROL,))


def _pune_lease(pid, gazda=None, sec=900):
    """Aseaza un lease pentru `pid`, direct — probele au nevoie de un detinator ales de ele."""
    gazda = gazda or _inst.eu()[0]
    with _db.get_conn() as c, c.cursor() as cur:
        cur.execute("DELETE FROM public.instante_lider WHERE rol = %s", (ROL,))
        cur.execute("INSERT INTO public.instante_lider (rol, gazda, pid, expira_la) "
                    "VALUES (%s, %s, %s, now() + make_interval(secs => %s))",
                    (ROL, gazda, pid, sec))


def _detinator():
    with _db.get_conn() as c, c.cursor() as cur:
        cur.execute("SELECT gazda, pid FROM public.instante_lider WHERE rol = %s", (ROL,))
        r = cur.fetchone()
        return (r[0], r[1]) if r else None


COPIL = r'''
import json, os, sys, time
sys.path.insert(0, %(rad)r)
from core import db, instante as I
db.init_pool()
rol, retrage = sys.argv[1], sys.argv[2] == "cu_retragere"
pornire, ramane = float(sys.argv[3]), float(sys.argv[4])
while time.time() < pornire:      # bariera: intrecerea incepe pentru toti in aceeasi clipa
    time.sleep(0.002)
out = {"pid": os.getpid()}
with db.get_conn() as c:
    if retrage:
        out["scos"] = I.retrage_liderul_mort(c, rol)
    out["lider"] = I.cere_lider(c, rol)
print("__REZULTAT__" + json.dumps(out), flush=True)
time.sleep(ramane)                # ramane VIU cat tine intrecerea celorlalti
'''


def _copil(retrage="cu_retragere", cati=1, ramane=0.0):
    """`ramane` > 0 il tine in viata dupa ce si-a cerut dreptul.

    [12.09.2026] Adaugat dupa ce prima forma a probei „patru deodata" a picat cu DOUA castigatoare
    — pe drept: copiii mureau imediat, deci al doilea gasea un lider REAL mort si il retragea
    corect. Hamul nu realiza premisa pe care o afirma numele probei. *O proba care nu-si produce
    propria conditie masoara altceva decat scrie pe ea.*
    """
    cale = os.path.join(tempfile.gettempdir(), "iconta_w3_lider.py")
    with io.open(cale, "w", encoding="utf-8") as f:
        f.write(COPIL % {"rad": RADACINA})
    pornire = time.time() + 1.0
    proc = [subprocess.Popen([sys.executable, cale, ROL, retrage, str(pornire), str(ramane)],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                             cwd=RADACINA, env=dict(os.environ)) for _ in range(cati)]
    rez = []
    for p in proc:
        out, err = p.communicate(timeout=180)
        linii = [x for x in out.splitlines() if x.startswith("__REZULTAT__")]
        if not linii:
            raise AssertionError("copilul n-a raportat: %s | %s" % (out[-400:], err[-1200:]))
        rez.append(json.loads(linii[-1][len("__REZULTAT__"):]))
    return rez if cati > 1 else rez[0]


def _pid_mort():
    """Un PID care sigur nu mai exista: un proces pornit si asteptat pana la capat (deci NU zombi —
    un zombi ar raspunde la `os.kill(pid, 0)` si proba ar masura altceva decat crede)."""
    p = subprocess.Popen([sys.executable, "-c", "pass"])
    p.wait(timeout=30)
    assert not _inst.traieste(p.pid), "PID-ul reciclat prea repede; proba n-ar masura moartea"
    return p.pid


# ============================================================
#  1. Cine se retrage si cine nu
# ============================================================
def test_liderul_VIU_nu_e_retras():
    """Daca s-ar retrage si cei vii, conducerea s-ar schimba la fiecare ciclu — iar continuitatea
    masuratorilor e chiar motivul pentru care lease-ul se REINNOIESTE, nu se realege."""
    _curata()
    try:
        _pune_lease(os.getpid())
        with _db.get_conn() as c:
            assert _inst.retrage_liderul_mort(c, ROL) is None
        assert _detinator() == (_inst.eu()[0], os.getpid()), "un lider viu a fost retras"
        # si consecinta care conteaza: un strain care retrage INAINTE de a cere tot nu ia conducerea
        strain = _copil("cu_retragere")
        assert strain["scos"] is None and strain["lider"] is False, (
            "retragerea a devenit o poarta prin care conducerea se ia de la un lider VIU: %s"
            % strain)
    finally:
        _curata()


def test_liderul_MORT_de_pe_gazda_asta_e_retras():
    _curata()
    try:
        mort = _pid_mort()
        _pune_lease(mort)
        with _db.get_conn() as c:
            assert _inst.retrage_liderul_mort(c, ROL) == mort
        assert _detinator() is None, "lease-ul mortului a ramas in tabela"
    finally:
        _curata()


def test_liderul_de_pe_ALTA_gazda_NU_se_atinge():
    """Limita declarata, nu o scapare: pe o gazda straina nu se poate intreba sistemul de operare
    daca PID-ul traieste, deci acolo expirarea ramane singurul raspuns."""
    _curata()
    try:
        _pune_lease(_pid_mort(), gazda=GAZDA_STRAINA)
        with _db.get_conn() as c:
            assert _inst.retrage_liderul_mort(c, ROL) is None
        assert _detinator()[0] == GAZDA_STRAINA, "s-a atins lease-ul altei gazde"
    finally:
        _curata()


# ============================================================
#  2. Preluarea — si RED-proof-ul purtarii de pe 94d655a8
# ============================================================
def test_dupa_retragere_alt_worker_devine_lider():
    """Criteriul cerut: fereastra fara lider tine cat un CICLU, nu cat lease-ul."""
    _curata()
    try:
        _pune_lease(_pid_mort(), sec=900)      # lease valabil inca 15 minute, pe un mort
        r = _copil("cu_retragere")
        assert r["scos"] is not None, "copilul n-a gasit niciun lider mort de retras"
        assert r["lider"] is True, "preluarea n-a reusit desi liderul era mort"
        assert _detinator() == (_inst.eu()[0], r["pid"])
    finally:
        _curata()


def test_RED_fara_retragere_lease_ul_mort_BLOCHEAZA_preluarea():
    """Purtarea de pe `94d655a8`, pinata ca sa se vada ce s-a schimbat.

    Acelasi lease mort, acelasi proces care cere conducerea — dar fara pasul de retragere. Raspunsul
    e `False`: nimeni nu preia, si asa raman 900 de secunde fara munca de fundal. Daca intr-o zi
    proba asta incepe sa treaca fara sa fi schimbat nimeni nimic, inseamna ca `cere_lider` si-a
    schimbat contractul pe furis.
    """
    _curata()
    try:
        _pune_lease(_pid_mort(), sec=900)
        r = _copil("fara_retragere")
        assert r["lider"] is False, (
            "preluarea a reusit FARA retragere — atunci fereastra de 900 s masurata pe productie "
            "avea alta cauza decat cea reparata aici")
        assert _detinator()[1] != r["pid"]
    finally:
        _curata()


def test_exact_UN_lider_dupa_preluare_cand_se_ingramadesc_patru():
    """Retragerea nu are voie sa deschida o poarta prin care sa intre mai multi deodata: patru
    procese care retrag si cer in ACEEASI clipa, un singur castigator.

    Cei patru pornesc pe o bariera de ceas si raman in viata dupa ce si-au cerut dreptul — altfel
    proba n-ar masura o intrecere, ci o insiruire de preluari corecte de la un lider care intre timp
    chiar murise (asa a picat prima ei forma, si avea dreptate).
    """
    _curata()
    try:
        _pune_lease(_pid_mort(), sec=900)
        rez = _copil("cu_retragere", cati=4, ramane=2.0)
        assert len({r["pid"] for r in rez}) == 4, "n-au fost patru procese distincte"
        castigatori = [r for r in rez if r["lider"]]
        assert len(castigatori) == 1, (
            "au castigat %d din 4 — retragerea a spart unicitatea liderului" % len(castigatori))
        with _db.get_conn() as c, c.cursor() as cur:
            cur.execute("SELECT count(*) FROM public.instante_lider WHERE rol = %s", (ROL,))
            assert cur.fetchone()[0] == 1, "doua lease-uri active pe acelasi rol"
    finally:
        _curata()


# ============================================================
#  3. Retragerea e CHEMATA din ciclul de sanatate
# ============================================================
def test_ciclul_de_sanatate_retrage_INAINTE_de_a_cere_conducerea():
    """O functie care exista si nu e chemata nu repara nimic. Si ordinea conteaza: retragerea DUPA
    cerere ar lasa fereastra neschimbata inca un ciclu."""
    with io.open(os.path.join(RADACINA, "main.py"), encoding="utf-8") as f:
        arbore = ast.parse(f.read())
    corp = None
    for nod in ast.walk(arbore):
        if isinstance(nod, ast.FunctionDef) and nod.name == "_ciclu_sanatate":
            corp = nod
    assert corp is not None, "n-am gasit `_ciclu_sanatate` — proba ar trece in gol"
    nume = [x.func.attr for x in ast.walk(corp)
            if isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute)]
    # multime, nu `in` — v. nota din `test_wave3_serializare_pornire.py` (METODA §23)
    assert set(nume) >= {"retrage_liderul_mort", "cere_lider"}, (
        "ciclul de sanatate nu retrage liderul mort inainte de a cere conducerea: %s" % nume)
    assert nume.index("retrage_liderul_mort") < nume.index("cere_lider"), (
        "retragerea se face DUPA ce se cere conducerea — cu un ciclu prea tarziu")
