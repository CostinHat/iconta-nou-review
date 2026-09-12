# -*- coding: utf-8 -*-
"""P6 valul 3 — blocajul de pornire chiar APARA sectiunea critica, nu doar exista.

DE CE EXISTA FISIERUL ASTA, si ce n-a putut vedea proba de dinaintea lui. Pe 12.09.2026, la prima
pornire reala cu doi workeri, unul a murit la fiecare repornire (patru din patru) cu
`psycopg2.errors.InternalError_: tuple concurrently updated`, in `main.py:196` ->
`supervizor_cache.aplica_ddl`. Suita era VERDE, si a ramas verde: `test_wave3_instante.py::
test_blocajul_de_pornire_serializeaza_si_se_elibereaza_singur` proba functia `blocaj_pornire`
IZOLAT — iar acolo ea chiar serializeaza. *O poarta care intreaba daca functia merge nu poate afla
ca cineva ii ia blocajul din mana trei linii mai jos.*

Si exact asta se intampla: `main.py` lua blocajul, iar apelul urmator — `migrare_api.asigura_tabel`
— se termina cu `conn.commit()`. `pg_advisory_xact_lock` e legat de TRANZACTIE; commitul o incheie,
deci blocajul murea inainte sa apere ceva. Masurat pe productie: in toata pornirea, blocajul nu
aparea NICIODATA in `pg_locks` (esantion la 0,15 s), desi interogarea era calibrata pe un lacat
luat dinadins.

CE PROBEAZA FISIERUL, si in ce ordine de la ieftin la scump:
  · STRUCTURAL — blocajul e chiar PRIMA operatie din sectiune · `asigura_tabel` e chemat fara
    commit · sectiunea se incheie cu `confirma_blocaj`. Trei aserțiuni care ar fi picat pe
    `94d655a8`, unde ordinea era alta si ultimele doua nu existau.
  · MECANIC, DETERMINIST — un `commit` in mijloc ELIBEREAZA blocajul (forma de dinainte), iar
    `comite=False` nu-l elibereaza. Asta e cauza, pinata in ambele directii.
  · MECANIC, PE PROCESE — doi workeri care ruleaza ADEVARATA secventa de pornire simultan, de mai
    multe ori, fara nicio cursa. Aceeasi forma care, cu commitul in mijloc, pica jumatate din cazuri.
  · SI GARDA INSASI POATE DEVENI ROSIE — `confirma_blocaj` ridica atunci cand blocajul s-a pierdut.
    Fara proba asta, gardul ar putea fi un `pass` si nimeni n-ar sti.

CALIBRAREA HAMULUI, masurata 12.09.2026 inainte de a-l crede: acelasi ham, cu forma de pe
`94d655a8` (`asigura_tabel` care comite), a produs **10 curse din 20**, toate cu exact eroarea din
productie — `InternalError_: tuple concurrently updated`. Cu forma reparata: **0 din 20**. Deci
verdele de mai jos nu inseamna «cei doi copii nu s-au intalnit», inseamna «s-au intalnit si n-au
mai avut de ce sa se calce».
"""
from __future__ import annotations

import ast
import io
import json
import os
import subprocess
import sys
import tempfile

import pytest

RADACINA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RADACINA)

from core import db as _db  # noqa: E402
from core import instante as _inst  # noqa: E402
from core import migrare_api as _migrare  # noqa: E402
from core import stare_partajata as _sp  # noqa: E402
from core import supervizor_cache as _sc  # noqa: E402


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn() as c:
            _inst.aplica_ddl(c)
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


# ============================================================
#  1. STRUCTURAL — forma sectiunii critice din `main.lifespan`
# ============================================================
def _blocul_critic():
    """Blocul `with db.get_conn() as conn:` din `lifespan` care contine blocajul de pornire.

    Se cauta dupa CONTINUT, nu dupa pozitie: un bloc gasit dupa numarul liniei ar minti la prima
    inserare de cod. `None` daca nu exista — iar probele cer explicit sa nu fie `None`, ca sa nu
    treaca in gol daca `lifespan` se redenumeste.
    """
    with io.open(os.path.join(RADACINA, "main.py"), encoding="utf-8") as f:
        arbore = ast.parse(f.read())
    for nod in ast.walk(arbore):
        if not isinstance(nod, (ast.FunctionDef, ast.AsyncFunctionDef)) or nod.name != "lifespan":
            continue
        for sub in ast.walk(nod):
            if isinstance(sub, ast.With) and any(
                    _e_apel(x, "blocaj_pornire") for x in ast.walk(sub)):
                return sub
    return None


def _e_apel(nod, nume):
    return (isinstance(nod, ast.Call) and isinstance(nod.func, ast.Attribute)
            and nod.func.attr == nume)


def _apeluri(bloc):
    """Numele apelurilor din CORPUL blocului, in ordine (doar nivelul de sus)."""
    nume = []
    for instr in bloc.body:
        if isinstance(instr, ast.Expr) and isinstance(instr.value, ast.Call):
            f = instr.value.func
            if isinstance(f, ast.Attribute):
                nume.append(f.attr)
        elif isinstance(instr, ast.Assign) and isinstance(instr.value, ast.Call):
            f = instr.value.func
            if isinstance(f, ast.Attribute):
                nume.append(f.attr)
    return nume


def test_blocajul_e_PRIMA_operatie_din_sectiunea_critica():
    """Nu «pe undeva la inceput»: PRIMA. Pe `94d655a8` era a doua, dupa `_instante.aplica_ddl` —
    si tocmai «a doua» a facut posibil ca linia urmatoare sa i-o ia inainte."""
    bloc = _blocul_critic()
    assert bloc is not None, "n-am gasit blocul critic din `lifespan` — proba ar trece in gol"
    prima = bloc.body[0]
    assert isinstance(prima, ast.Expr) and _e_apel(prima.value, "blocaj_pornire"), (
        "prima operatie din sectiunea critica nu e blocajul, ci: %s"
        % ast.dump(prima)[:200])


def test_asigura_tabel_e_chemat_FARA_commit_pe_calea_de_pornire():
    """`asigura_tabel` comite implicit — si acel commit a ucis blocajul. Pe calea de pornire se
    cere EXPLICIT sa nu comita; daca cineva scoate argumentul, proba asta pica."""
    bloc = _blocul_critic()
    assert bloc is not None
    apeluri = [x for x in ast.walk(bloc) if _e_apel(x, "asigura_tabel")]
    assert len(apeluri) == 1, "asteptam exact un apel `asigura_tabel` in sectiune, sunt %d" % len(apeluri)
    chei = {k.arg: getattr(k.value, "value", None) for k in apeluri[0].keywords}
    assert chei.get("comite") is False, (
        "`asigura_tabel` e chemat cu %s — un commit aici elibereaza blocajul de pornire" % chei)


def test_sectiunea_critica_se_incheie_cu_DOVADA_blocajului():
    """Ultima intrebare a sectiunii: mai e blocajul al meu? Si se pune INAINTE de inregistrare —
    un proces n-are voie sa intre in registru ca 'pornit corect' daca instalarea n-a fost aparata."""
    bloc = _blocul_critic()
    assert bloc is not None
    nume = _apeluri(bloc)
    # operatorul de multime, nu `in`: un `in` pe container se transforma tacut in sub-sir daca
    # dreapta devine vreodata un sir, si arata identic. `>=` crapa in loc sa treaca (METODA §23).
    assert set(nume) >= {"confirma_blocaj", "inregistreaza"}, (
        "sectiunea critica nu cere dovada blocajului la capat, sau nu mai are inregistrarea "
        "(a doua ar face proba sa treaca in gol): %s" % nume)
    assert nume.index("confirma_blocaj") < nume.index("inregistreaza"), (
        "dovada blocajului se cere DUPA inregistrare — adica prea tarziu")


# ============================================================
#  2. MECANIC, DETERMINIST — cauza, pinata in ambele directii
# ============================================================
def test_un_commit_in_mijloc_ELIBEREAZA_blocajul():
    """RED-PROOF al defectului de pe `94d655a8`, fara nicio cursa: forma de atunci.

    Se ia blocajul, apoi se cheama `asigura_tabel` EXACT cum era chemat atunci (cu commit). Dupa
    apel, blocajul nu mai e al nostru. Proba asta, scrisa inainte de 12.09.2026, ar fi aratat
    defectul fara sa fie nevoie de doi workeri si fara noroc de sincronizare.
    """
    _db.init_pool()
    pool = _db.pool()
    conn = pool.getconn()
    try:
        _inst.blocaj_pornire(conn)
        assert _inst.blocaj_tinut(conn) is True, "blocajul nu s-a luat deloc"
        _migrare.asigura_tabel(conn)                      # forma de pe 94d655a8: comite
        assert _inst.blocaj_tinut(conn) is False, (
            "un `commit` in mijlocul sectiunii n-a eliberat blocajul — atunci explicatia "
            "defectului din productie e alta, si proba asta nu mai are obiect")
    finally:
        conn.rollback()
        pool.putconn(conn)


def test_cu_comite_False_blocajul_RAMANE_tinut():
    """Cealalta directie a aceleiasi masuratori: reparatia chiar schimba ce trebuia."""
    _db.init_pool()
    pool = _db.pool()
    conn = pool.getconn()
    try:
        _inst.blocaj_pornire(conn)
        _migrare.asigura_tabel(conn, comite=False)
        assert _inst.blocaj_tinut(conn) is True, "blocajul s-a pierdut desi nu s-a comis nimic"
        _sc.aplica_ddl(conn)
        _sp.aplica_ddl(conn)
        _inst.aplica_ddl(conn)
        assert _inst.blocaj_tinut(conn) is True, (
            "blocajul s-a pierdut in timpul instalarii — un apel de pe drum comite")
        _inst.confirma_blocaj(conn)                       # nu trebuie sa ridice
    finally:
        conn.rollback()
        pool.putconn(conn)


def test_confirma_blocaj_RIDICA_atunci_cand_blocajul_s_a_pierdut():
    """Mutatia gardului insusi: daca `confirma_blocaj` ar fi un `pass`, proba asta pica.

    Fara ea, am avea un gard despre care nu se stie daca poate deveni rosu — adica tocmai clasa de
    defect pe care o repara commitul asta.
    """
    _db.init_pool()
    pool = _db.pool()
    conn = pool.getconn()
    try:
        _inst.blocaj_pornire(conn)
        conn.commit()                                     # tranzactia se incheie: blocajul pleaca
        with pytest.raises(_inst.BlocajPierdut):
            _inst.confirma_blocaj(conn)
    finally:
        conn.rollback()
        pool.putconn(conn)


def test_blocajul_se_elibereaza_la_ROLLBACK_si_nu_ramane_nimic():
    """Un worker care pica la mijloc nu are voie sa lase poarta incuiata pentru ceilalti."""
    _db.init_pool()
    pool = _db.pool()
    conn = pool.getconn()
    try:
        _inst.blocaj_pornire(conn)
        assert _inst.blocaj_tinut(conn) is True
        conn.rollback()
        assert _inst.blocaj_tinut(conn) is False, "rollback-ul n-a eliberat blocajul"
    finally:
        pool.putconn(conn)
    with _db.get_conn() as c, c.cursor() as cur:          # si nici pentru nimeni altcineva
        cur.execute("SELECT count(*) FROM pg_locks WHERE locktype = 'advisory' "
                    "  AND classid = %s AND objid = %s",
                    (_inst.CHEIE_PORNIRE >> 32, _inst.CHEIE_PORNIRE & 0xFFFFFFFF))
        assert cur.fetchone()[0] == 0, "a ramas un blocaj de pornire dupa terminare"


# ============================================================
#  3. MECANIC, PE PROCESE — secventa reala, doi workeri, de mai multe ori
# ============================================================
COPIL = r'''
import json, os, sys
sys.path.insert(0, %(rad)r)
from core import db, instante as I, migrare_api, stare_partajata as SP, supervizor_cache as SC
db.init_pool()
comite = sys.argv[1] == "cu_commit"
out = {"pid": os.getpid(), "ok": True, "eroare": None, "blocaj_la_capat": None}
pool = db.pool(); conn = pool.getconn()
try:
    I.blocaj_pornire(conn)                 # ordinea REPARATA: blocajul, primul
    I.aplica_ddl(conn)
    migrare_api.asigura_tabel(conn, comite=comite)
    SC.aplica_ddl(conn)                    # aici murea workerul al doilea, pe productie
    SP.aplica_ddl(conn)
    out["blocaj_la_capat"] = I.blocaj_tinut(conn)
    conn.commit()
except Exception as e:
    conn.rollback()
    out["ok"] = False
    out["eroare"] = "%%s: %%s" %% (type(e).__name__, str(e).strip().splitlines()[0])
finally:
    pool.putconn(conn)
print("__REZULTAT__" + json.dumps(out), flush=True)
'''


def _copii(varianta, cati=2):
    cale = os.path.join(tempfile.gettempdir(), "iconta_w3_pornire.py")
    with io.open(cale, "w", encoding="utf-8") as f:
        f.write(COPIL % {"rad": RADACINA})
    proc = [subprocess.Popen([sys.executable, cale, varianta], stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, text=True, cwd=RADACINA,
                             env=dict(os.environ))
            for _ in range(cati)]
    rez = []
    for p in proc:
        out, err = p.communicate(timeout=180)
        linii = [x for x in out.splitlines() if x.startswith("__REZULTAT__")]
        if not linii:
            raise AssertionError("copilul n-a raportat: %s | %s" % (out[-400:], err[-1200:]))
        rez.append(json.loads(linii[-1][len("__REZULTAT__"):]))
    return rez


def test_doi_workeri_concurenti_NU_mai_produc_cursa():
    """Secventa REALA de pornire, doua procese deodata, de cinci ori.

    Pe productie, forma de dinainte omora un worker la fiecare repornire — patru din patru — iar
    aceeasi forma masurata in baza de test a picat de 10 ori din 20. Aici se cere zero, si se cere
    si ca fiecare sa iasa din sectiune cu blocajul inca in mana: «n-a picat» singur ar putea
    insemna doar ca nu s-au intalnit.
    """
    for runda in range(5):
        rez = _copii("fara_commit")
        assert len({r["pid"] for r in rez}) == 2, "n-au fost doua procese distincte"
        rele = [r for r in rez if not r["ok"]]
        assert not rele, "runda %d: %s" % (runda, [r["eroare"] for r in rele])
        assert all(r["blocaj_la_capat"] is True for r in rez), (
            "runda %d: un worker a ajuns la capatul sectiunii FARA blocaj: %s" % (runda, rez))


def test_hamul_probei_de_mai_sus_POATE_deveni_rosu():
    """Mutatia hamului pe propriul lui mod de esec (METODA §22).

    O proba verde care n-a fost aratata niciodata rosie nu spune daca masoara ceva. Aici se ruleaza
    ACELASI ham cu forma de pe `94d655a8` si se cere partea DETERMINISTA a diferentei: cu commit in
    mijloc, niciun copil nu mai ajunge la capatul sectiunii cu blocajul in mana. Cursa propriu-zisa
    apare in jumatate din runde (masurat: 10 din 20) — pe ea n-o asertez, ca proba sa nu depinda de
    noroc; dar cauza ei, da.
    """
    rez = _copii("cu_commit")
    assert len(rez) == 2
    assert all(r["blocaj_la_capat"] is not True for r in rez), (
        "cu `commit` in mijloc, blocajul apare inca tinut la capat — atunci hamul nu vede "
        "diferenta pe care o masoara proba de mai sus: %s" % rez)
