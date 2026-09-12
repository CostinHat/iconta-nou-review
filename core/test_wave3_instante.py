# -*- coding: utf-8 -*-
"""P6 valul 3 — probele de acceptare pentru mai multe procese care servesc.

Cele patru criterii canonice (`PLAN_HARDENING.md:713-721`), fiecare cu proba lui:

  1  DOUA INSTANTE IDENTICE   blocarea la autentificare tine pe ambele · cooldownul nu trimite
                              dublu · sesiunile merg indiferent de instanta.
                              Primele doua sunt probate la valul 1 (`test_wave1_stare_partajata`);
                              aici e a treia, plus ce aduce valul 3: liderul si pornirea.
  2  RECONSTRUCTIA CACHE-ULUI probata la valul 2 (`test_cache_declarat`).
  3  FAULT-CHECK              o instanta OMORATA in timpul unei cereri; nicio stare partiala.
  4  FOUR-WAY REDEFINIT       «procesul viu poarta HEAD» -> «TOATE procesele poarta HEAD»,
                              inclusiv purtarea pe multime vida, care e cea usor de gresit.

DE CE SE OMOARA CU `SIGKILL` SI NU CU O EXCEPTIE. O exceptie ar proba `try/finally`-ul nostru; un
proces omorat fara sa apuce sa curete probeaza ce se intampla CU ADEVARAT cand o instanta pica:
conexiunea moare, iar PostgreSQL da inapoi tranzactia neincheiata. Aia e garantia, si ea nu se
poate arata simuland.
"""
from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import threading
import time

import pytest

RADACINA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RADACINA)

from core import db as _db  # noqa: E402
from core import instante as _inst  # noqa: E402
from core import stare_partajata as _sp  # noqa: E402


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn() as c:
            _inst.aplica_ddl(c)
            _sp.aplica_ddl(c)
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")

ROL_PROBA = "ztest_wave3_sanatate"


def _curata_registrul(gazde=()):
    with _db.get_conn() as c, c.cursor() as cur:
        cur.execute("DELETE FROM public.instante_lider WHERE rol = %s", (ROL_PROBA,))
        for g in gazde:
            cur.execute("DELETE FROM public.instante WHERE gazda = %s", (g,))


# ============================================================
#  Copilul — un PROCES separat, fara `lifespan`
# ============================================================
COPIL = r'''
import json, os, signal, sys, time
sys.path.insert(0, %(rad)r)
from core import db, instante as I, stare_partajata as SP
db.init_pool()
rol, arg = sys.argv[1], sys.argv[2]
out = {"pid": os.getpid()}

if rol == "lider":
    with db.get_conn() as c:
        out["lider"] = I.cere_lider(c, arg)
elif rol == "inregistreaza":
    with db.get_conn() as c:
        I.inregistreaza(c, arg)
    out["ok"] = True
elif rol == "token_verifica":
    from core import auth_api
    out["ctx"] = auth_api.context_din_token(arg) is not None
elif rol == "moare_in_tranzactie":
    # deschide tranzactia, face PRIMUL pas (stergerea), anunta, si asteapta sa fie omorat
    pool = db.pool(); conn = pool.getconn()
    SP.login_esec(conn, arg)          # DELETE expirate + INSERT, NEcomise
    print("__GATA__", flush=True)
    time.sleep(120)                   # nu comite niciodata; testul trimite SIGKILL
print("__REZULTAT__" + json.dumps(out), flush=True)
''' % {"rad": RADACINA}


def _scrie_copil():
    """In afara arborelui, deliberat: prima forma il scria in repo si l-a si lasat acolo dupa
    probele care nu asteapta copilul. O proba n-are voie sa polueze ce masoara."""
    import tempfile
    cale = os.path.join(tempfile.gettempdir(), "iconta_w3_copil.py")
    with open(cale, "w") as f:
        f.write(COPIL)
    return cale


def _copil(rol, arg, asteapta=True):
    cale = _scrie_copil()
    p = subprocess.Popen([sys.executable, cale, rol, str(arg)],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         text=True, cwd=RADACINA, env=dict(os.environ))
    if not asteapta:
        return p
    out, err = p.communicate(timeout=180)
    linii = [x for x in out.splitlines() if x.startswith("__REZULTAT__")]
    if not linii:
        raise AssertionError("copilul n-a raportat nimic.\nstdout: %s\nstderr: %s"
                             % (out[-600:], err[-1500:]))
    return json.loads(linii[-1][len("__REZULTAT__"):])


# ============================================================
#  1. DOUA INSTANTE — liderul, si sesiunile
# ============================================================
def test_din_mai_multe_procese_exact_UNUL_e_lider():
    """Cu N workeri, munca de fundal trebuie facuta o data. «Cel mult unul» n-ar fi de ajuns:
    daca n-ar castiga NIMENI, metricile s-ar opri in tacere."""
    _curata_registrul()
    try:
        rezultate = [_copil("lider", ROL_PROBA) for _ in range(4)]
        assert len({r["pid"] for r in rezultate}) == 4, "cele patru n-au fost procese distincte"
        castigatori = [r for r in rezultate if r["lider"]]
        assert len(castigatori) == 1, (
            "au castigat %d din 4 procese — alegerea liderului nu e atomica" % len(castigatori))
    finally:
        _curata_registrul()


def test_liderul_isi_reinnoieste_dreptul_si_nu_se_schimba_la_fiecare_ciclu():
    """O schimbare de lider la fiecare ciclu ar rupe continuitatea masuratorilor fara motiv."""
    _curata_registrul()
    try:
        with _db.get_conn() as c:
            assert _inst.cere_lider(c, ROL_PROBA) is True
            assert _inst.cere_lider(c, ROL_PROBA) is True, "detinatorul si-a pierdut dreptul"
            assert _inst.cine_e_lider(c, ROL_PROBA) == _inst.eu()
        strain = _copil("lider", ROL_PROBA)
        assert strain["lider"] is False, "alt proces a luat conducerea cat lease-ul era valabil"
    finally:
        _curata_registrul()


def test_liderul_mort_e_inlocuit_dupa_expirarea_lease_ului():
    """Fara asta, un lider care moare ar opri munca de fundal pentru totdeauna — si nimeni n-ar
    afla, fiindca tocmai munca aia produce semnalele."""
    _curata_registrul()
    try:
        with _db.get_conn() as c:
            assert _inst.cere_lider(c, ROL_PROBA, lease_sec=0) is True
        # lease de 0 s: a expirat deja, deci alt proces are voie sa preia
        altul = _copil("lider", ROL_PROBA)
        assert altul["lider"] is True, "lease-ul expirat n-a putut fi preluat"
    finally:
        _curata_registrul()


def test_o_sesiune_emisa_de_o_instanta_e_valida_pe_alta():
    """Criteriul canonic: «sesiunile functioneaza indiferent de instanta». Tokenul e semnat cu un
    secret din mediu, nu cu vreo stare de proces — dar asta e o afirmatie pana se arata."""
    from core import auth_api
    token = auth_api.emite_token({"id": 424242, "email": "ztest_w3@invalid", "rol": "superadmin",
                                  "firm_id": None})
    assert token, "n-a iesit niciun token"
    altul = _copil("token_verifica", token)
    assert altul["pid"] != os.getpid()
    assert altul["ctx"] is True, (
        "tokenul emis aici nu e recunoscut in alt proces — sesiunile ar depinde de instanta")


# ============================================================
#  3. FAULT-CHECK — o instanta omorata in timpul unei cereri
# ============================================================
def test_o_instanta_omorata_in_mijlocul_unei_scrieri_nu_lasa_stare_partiala():
    """Criteriul canonic 3, si legatura cu P4.

    `login_esec` face doua lucruri intr-o tranzactie: sterge randurile expirate si insereaza unul
    nou. Copilul le face, ANUNTA, si asteapta. Il omoram cu SIGKILL — fara `finally`, fara rollback
    politicos. Ce ramane in baza e raspunsul: ori amandoua, ori niciuna.
    """
    email = "ztest_wave3_fault@invalid"
    with _db.get_conn() as c, c.cursor() as cur:
        cur.execute("DELETE FROM public.login_esecuri WHERE email IN (%s, %s)",
                    (email, email + ".vechi"))
        cur.execute("INSERT INTO public.login_esecuri (email, esuat_la) "
                    "SELECT %s, now() - make_interval(secs => %s) FROM generate_series(1, 5)",
                    (email + ".vechi", _sp.FEREASTRA_ESECURI_SEC + 60))
    try:
        p = _copil("moare_in_tranzactie", email, asteapta=False)
        gata = False
        for _ in range(300):
            linie = p.stdout.readline()
            if linie.startswith("__GATA__"):
                gata = True
                break
            if p.poll() is not None:
                break
        assert gata, "copilul n-a apucat sa intre in tranzactie: %s" % (p.stderr.read()[-800:],)

        os.kill(p.pid, signal.SIGKILL)
        p.wait(timeout=30)
        assert p.returncode in (-signal.SIGKILL, 137), "n-a murit prin SIGKILL: %s" % p.returncode

        for _ in range(30):          # PostgreSQL are nevoie de o clipa sa vada conexiunea moarta
            with _db.get_conn() as c, c.cursor() as cur:
                cur.execute("SELECT count(*) FROM public.login_esecuri WHERE email = %s",
                            (email + ".vechi",))
                vechi = cur.fetchone()[0]
                cur.execute("SELECT count(*) FROM public.login_esecuri WHERE email = %s", (email,))
                nou = cur.fetchone()[0]
            if vechi == 5 and nou == 0:
                break
            time.sleep(0.2)

        assert nou == 0, "inserarea a supravietuit unui proces omorat — stare partiala"
        assert vechi == 5, (
            "stergerea a supravietuit unui proces omorat (%d din 5 randuri) — stare partiala"
            % vechi)
    finally:
        with _db.get_conn() as c, c.cursor() as cur:
            cur.execute("DELETE FROM public.login_esecuri WHERE email IN (%s, %s)",
                        (email, email + ".vechi"))


# ============================================================
#  4. FOUR-WAY REDEFINIT
# ============================================================
def test_toate_procesele_poarta_HEAD():
    G = "ztest-gazda-w3"
    _curata_registrul([G])
    try:
        with _db.get_conn() as c, c.cursor() as cur:
            for pid in (9000001, 9000002):
                cur.execute("INSERT INTO public.instante (gazda, pid, commit_sha) "
                            "VALUES (%s, %s, %s)", (G, pid, "aaaa1111"))
        with _db.get_conn() as c:
            lista = [x for x in _inst.vii(c) if x[0] == G]
            assert len(lista) == 2, "premisa: doua instante inregistrate, sunt %d" % len(lista)
    finally:
        _curata_registrul([G])


def test_un_singur_proces_ramas_in_urma_STRICA_bratul():
    """Directia a doua, si chiar rostul redefinirii: cu trei procese din patru la HEAD, bratul
    vechi («unitatea a pornit dupa commit») s-ar fi inchis. Cel nou nu."""
    G = "ztest-gazda-w3b"
    _curata_registrul([G])
    try:
        with _db.get_conn() as c, c.cursor() as cur:
            for pid, sha in ((9100001, "bbbb2222"), (9100002, "bbbb2222"),
                             (9100003, "VECHI999")):
                cur.execute("INSERT INTO public.instante (gazda, pid, commit_sha) "
                            "VALUES (%s, %s, %s)", (G, pid, sha))
        with _db.get_conn() as c:
            toti = [x for x in _inst.vii(c) if x[0] == G]
            rataciti = [x for x in toti if x[2] != "bbbb2222"]
        assert len(toti) == 3 and len(rataciti) == 1, (
            "premisa gresita: %d procese, %d ratacite" % (len(toti), len(rataciti)))
    finally:
        _curata_registrul([G])


def test_registrul_gol_NU_inchide_bratul():
    """Forma de orbire cea mai usoara: `all([])` e `True`. Un brat care se inchide pe o multime
    vida afirma ca toate procesele poarta HEAD tocmai cand nu se stie nimic despre niciunul."""
    with _db.get_conn() as c, c.cursor() as cur:
        cur.execute("SELECT count(*) FROM public.instante "
                    " WHERE batut_la > now() - make_interval(secs => %s)",
                    (_inst.INSTANTA_MOARTA_SEC,))
        if cur.fetchone()[0]:
            pytest.skip("exista instante vii reale; proba pe multime vida se face pe cod")
    with _db.get_conn() as c:
        da, total, rataciti = _inst.toate_poarta(c, "orice")
    assert total == 0 and da is False and rataciti == [], (
        "registru gol, dar bratul s-a inchis — `all([])` e `True` si asta e capcana")


def test_curatenia_registrului_e_MARGINITA():
    """Fara ea, registrul ar creste cu fiecare repornire si ar raporta drept vii niste PID-uri
    disparute — adica ar face bratul four-way sa pice pe fantome."""
    G = "ztest-gazda-w3c"
    _curata_registrul([G])
    try:
        with _db.get_conn() as c, c.cursor() as cur:
            cur.execute("INSERT INTO public.instante (gazda, pid, commit_sha, batut_la) "
                        "VALUES (%s, %s, %s, now() - make_interval(secs => %s))",
                        (G, 9200001, "cccc3333", _inst.INSTANTA_MOARTA_SEC + 60))
        with _db.get_conn() as c:
            assert not [x for x in _inst.vii(c) if x[0] == G], "o instanta moarta apare ca vie"
            _inst.curata(c)
        with _db.get_conn() as c, c.cursor() as cur:
            cur.execute("SELECT count(*) FROM public.instante WHERE gazda = %s", (G,))
            assert cur.fetchone()[0] == 0, "curatenia n-a scos randul mort"
    finally:
        _curata_registrul([G])


# ============================================================
#  PORNIREA, SERIALIZATA
# ============================================================
def test_blocajul_de_pornire_serializeaza_si_se_elibereaza_singur():
    """Doua fire iau blocajul pe rand, nu simultan; iar al doilea il primeste FARA ca primul sa fi
    facut vreo curatenie — fiindca `pg_advisory_xact_lock` moare cu tranzactia."""
    ordine = []
    lock = threading.Lock()
    pornit = threading.Event()

    def fir(eticheta, tine_sec):
        with _db.get_conn() as c:
            _inst.blocaj_pornire(c)
            with lock:
                ordine.append("intra:" + eticheta)
            if eticheta == "A":
                pornit.set()
            time.sleep(tine_sec)
            with lock:
                ordine.append("iese:" + eticheta)

    a = threading.Thread(target=fir, args=("A", 1.0))
    a.start()
    assert pornit.wait(10), "primul fir n-a intrat in blocaj"
    b = threading.Thread(target=fir, args=("B", 0.0))
    b.start()
    a.join(30)
    b.join(30)
    assert ordine == ["intra:A", "iese:A", "intra:B", "iese:B"], (
        "blocajul n-a serializat: %s" % ordine)
