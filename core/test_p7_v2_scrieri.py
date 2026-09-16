# -*- coding: utf-8 -*-
"""GARDA V2 — nicio scriere și niciun control de tranzacție în corpul unei rute.

CE PĂZEȘTE. După V1, stratul HTTP nu mai citea. V2 a scos și restul: **140 de scrieri** (106 INSERT,
29 UPDATE dintre care unul construit dinamic, 5 DELETE) și **10 instrucțiuni de control de
tranzacție** (6 din familia `SAVEPOINT`, 4 `SET LOCAL search_path`). Cifra ținută aici e zero, pe
toate clasele.

CE **NU** S-A MUTAT, și e important: **proprietatea tranzacției**. Repository-ul primește cursorul
apelantului și nu comite nimic; `core/tranzactie.py` execută instrucțiunile de control pe același
cursor, la același loc în șir. Hotarele `commit`/`rollback` au rămas exact unde erau — contractul P4,
care nu se redeschide aici.

Mutanții ceruți de contract sunt toți mai jos: fiecare formă de scriere și de control, plus dovada
că textul „UPDATE" pe un obiect care nu e cursor nu produce fals pozitiv.
"""
from __future__ import annotations

import ast
import io
import os
import sys

RADACINA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RADACINA, "scripts"))
sys.path.insert(0, RADACINA)

import scan_p7_straturi as S  # noqa: E402
from core import straturi as R  # noqa: E402

MODULE_V2 = ("repo_banca", "tranzactie")


def _in_ruta(sursa):
    """(gasite, necunoscute) pentru un fragment de rută scris de mână."""
    return S.d1_din_rute(S.rute_din_arbore(ast.parse(sursa), "proba.py"))


def _ruta_cu(instructiune):
    return '''
@app.post("/proba")
def proba(ctx=None):
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute(%s)
        return {}
''' % instructiune


# ============================================================
#  1. CLICHETUL — zero pe toate clasele
# ============================================================
def test_WRITE_SQL_IN_HTTP_ROUTE_e_zero():
    pe = S.d1_pe_fel()
    assert pe[S.WRITE] == [], (
        "au reapărut scrieri SQL în corpul rutelor: %s"
        % [(i.fisier, i.linie, i.cale) for i in pe[S.WRITE]][:10])


def test_TRANSACTION_CONTROL_IN_HTTP_ROUTE_e_zero():
    pe = S.d1_pe_fel()
    assert pe[S.TRANSACTION_CONTROL] == [], (
        "au reapărut instrucțiuni de control de tranzacție în rute: %s"
        % [(i.fisier, i.linie) for i in pe[S.TRANSACTION_CONTROL]][:10])


def test_D1_e_zero_pe_toate_clasele_si_UNKNOWN_ramane_zero():
    pe = S.d1_pe_fel()
    assert {k: len(v) for k, v in pe.items()} == {S.READ: 0, S.WRITE: 0,
                                                 S.TRANSACTION_CONTROL: 0, S.UNKNOWN: 0}


# ============================================================
#  2. MUTANȚII — fiecare formă, prinsă
# ============================================================
def test_mutant_INSERT_in_ruta():
    gasite, _ = _in_ruta(_ruta_cu('"INSERT INTO t (a) VALUES (%s)", (1,)'))
    assert len(gasite) == 1
    assert S.fel_sql("INSERT INTO t (a) VALUES (%s)") == (S.WRITE, "INSERT")


def test_mutant_UPDATE_in_ruta():
    gasite, _ = _in_ruta(_ruta_cu('"UPDATE t SET a=%s WHERE id=%s", (1, 2)'))
    assert len(gasite) == 1
    assert S.fel_sql("UPDATE t SET a=%s WHERE id=%s") == (S.WRITE, "UPDATE")


def test_mutant_DELETE_in_ruta():
    gasite, _ = _in_ruta(_ruta_cu('"DELETE FROM t WHERE id=%s", (1,)'))
    assert len(gasite) == 1
    assert S.fel_sql("DELETE FROM t WHERE id=%s") == (S.WRITE, "DELETE")


def test_mutant_CTE_care_SCRIE_in_ruta():
    """Un `WITH` care șterge e o scriere, oricât de citire ar părea la primul cuvânt."""
    sql = "WITH x AS (DELETE FROM t RETURNING id) SELECT * FROM x"
    gasite, _ = _in_ruta(_ruta_cu('"%s"' % sql))
    assert len(gasite) == 1
    assert S.fel_sql(sql) == (S.WRITE, "WITH_SCRIERE")


def test_mutant_SAVEPOINT_in_ruta():
    for sql in ("SAVEPOINT x", "RELEASE SAVEPOINT x", "ROLLBACK TO SAVEPOINT x"):
        gasite, _ = _in_ruta(_ruta_cu('"%s"' % sql))
        assert len(gasite) == 1
        assert S.fel_sql(sql) == (S.TRANSACTION_CONTROL, "SAVEPOINT")


def test_mutant_SET_LOCAL_search_path_in_ruta():
    sql = "SET LOCAL search_path TO x"
    gasite, _ = _in_ruta(_ruta_cu('"%s"' % sql))
    assert len(gasite) == 1
    assert S.fel_sql(sql) == (S.TRANSACTION_CONTROL, "SEARCH_PATH")


def test_scrierea_in_REPOSITORY_e_permisa():
    """Cealaltă direcție: aceeași instrucțiune, într-un modul fără rute, NU e item D1."""
    sursa = '''
def salveaza(cur, a):
    cur.execute("INSERT INTO t (a) VALUES (%s)", (a,))
'''
    assert S.rute_din_arbore(ast.parse(sursa), "core/repo_x.py") == []
    gasite, _ = S.d1_din_rute(S.rute_din_arbore(ast.parse(sursa), "core/repo_x.py"))
    assert gasite == []


def test_textul_UPDATE_pe_un_obiect_care_nu_e_cursor_nu_e_fals_pozitiv():
    gasite, necunoscute = _in_ruta(_ruta_cu('"UPDATE t SET a=1"').replace(
        "cur.execute(", "jurnal.execute("))
    assert gasite == [] and len(necunoscute) == 1


def test_ANTI_VACUUM_detectorul_inca_vede_rutele_si_repository_urile():
    """Zero e o veste bună doar dacă universul are obiecte și instrumentul mai vede ceva."""
    assert len(S.rute()) >= 400, "universul rutelor s-a golit"
    apeluri = _apeluri_catre_repository()
    assert apeluri >= 250, "apelurile către repository au dispărut: %d" % apeluri


# ============================================================
#  3. CONSERVAREA — nimic nu s-a pierdut pe drum
# ============================================================
def _apeluri_catre_repository():
    module = {f[:-3] for f in os.listdir(os.path.join(RADACINA, "core"))
              if f.startswith("repo_") or f == "tranzactie.py"}
    # [P7 · valul use-case] Apelurile catre straturile de sub HTTP stau acum si in
    # `core/uc_*.py`. Conservarea (257) e despre APLICATIE, nu despre un fisier — numarate
    # doar in `main.py` ies 72, adica lipsa a 185 de apeluri care n-au plecat nicaieri.
    from core import scan_sql_efectiv as _ef
    n = 0
    for _cale in _ef.straturi_aplicatie():
        arb = ast.parse(io.open(os.path.join(RADACINA, _cale), encoding="utf-8").read())
        for x in ast.walk(arb):
            if (isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute)
                    and isinstance(x.func.value, ast.Name) and x.func.value.id in module):
                n += 1
    return n


def test_numarul_de_instructiuni_se_conserva():
    """257 de instrucțiuni SQL stăteau în rute înainte de V1 (107 citiri + 150 scrieri/control).
    Acum sunt **258** de APELURI către straturile de sub HTTP — niciuna pierdută, niciuna dublată,
    plus una ADĂUGATĂ deliberat (R187: `vanzare_ic` fixează schema, fiindcă emite o factură).

    *Instrucțiunile din repository sunt mai puține decât apelurile (192), fiindcă 140 de poziții de
    scriere au doar 78 de texte SQL distincte: una singură apare de douăzeci și cinci de ori.*
    """
    # [R187, 16.09.2026] 257 -> 258, cu motivul: `vanzare_ic` a capatat un
    # `tranzactie.fixeaza_schema(cur, schema)`, cerut fiindca `emite_factura` foloseste INSERT
    # NECALIFICAT — aceeasi linie exista deja in `achizitie_ic`, din acelasi motiv. Nu e o
    # instructiune noua de SQL: e un apel de CONTROL, spre `tranzactie.py`, pe care numaratoarea il
    # include. *Clichetul urca fiindca aplicatia face un pas in plus, nu fiindca s-a pierdut ceva.*
    assert _apeluri_catre_repository() == 258


def test_repository_urile_V2_nu_comit_si_nu_deschid_conexiuni():
    """Contractul P4: hotarele tranzacției rămân la apelant."""
    interzise = {"get_conn", "commit", "rollback", "HTTPException"}
    rele = []
    for f in sorted(os.listdir(os.path.join(RADACINA, "core"))):
        if not (f.startswith("repo_") or f == "tranzactie.py"):
            continue
        arb = ast.parse(io.open(os.path.join(RADACINA, "core", f), encoding="utf-8").read())
        for x in ast.walk(arb):
            if isinstance(x, ast.Call):
                fn = x.func
                nume = fn.id if isinstance(fn, ast.Name) else (
                    fn.attr if isinstance(fn, ast.Attribute) else None)
                if nume in interzise:
                    rele.append((f, x.lineno, nume))
    assert rele == [], "strat care depășește contractul: %s" % rele


def test_modulele_V2_sunt_declarate_in_registru():
    # multime, nu `in`: `>=` crapa pe un sir, `in` s-ar transforma tacut in sub-sir (METODA §23)
    assert R.module_din_strat(R.REPOSITORY) >= {"core/repo_banca.py"}
    assert R.module_din_strat(R.USE_CASE) >= {"core/tranzactie.py"}


# ============================================================
#  4. CAZUL DINAMIC (§6)
# ============================================================
def test_DYNAMIC_UPDATE_pastreaza_compunerea_in_apelant():
    """Singura scriere al cărei SQL se compune la rulare.

    Ce se cere: coloanele se aleg în RUTĂ (acolo e decizia contabilului), iar repository-ul le
    primește gata compuse, cu valorile în aceeași ordine. Dacă cineva ar muta compunerea în
    repository, funcția ar primi altceva decât două liste și proba asta ar pica.
    """
    arb = ast.parse(io.open(os.path.join(RADACINA, "core/repo_facturi.py"),
                            encoding="utf-8").read())
    f = [n for n in ast.walk(arb)
         if isinstance(n, ast.FunctionDef) and n.name == "actualizeaza_clasificarea"]
    assert f, "funcția dinamică a dispărut"
    argumente = [a.arg for a in f[0].args.args]
    assert argumente == ["cur", "schema", "bucati_set", "valori"], (
        "semnătura cazului dinamic s-a schimbat: %s" % argumente)
    # Conditia si absenta alegerii de coloane se cer pe STRUCTURA (§23): literalele din
    # argumentul `execute` al functiei, nu o cautare de text in fisier.
    apel = [n for n in ast.walk(f[0])
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
            and n.func.attr == "execute"]
    assert len(apel) == 1, "cazul dinamic are altceva decat o singura executie: %d" % len(apel)
    literale = [n.value for n in ast.walk(apel[0].args[0])
                if isinstance(n, ast.Constant) and isinstance(n.value, str)]
    # Egalitate exacta pe multimea literalelor: spune si ce ramane fix (sablonul + conditia), si
    # ca NIMIC in plus nu s-a strecurat — deci niciun nume de coloana ales aici.
    assert sorted(set(literale)) == [" WHERE id=%s", ", ", ".facturi SET ", "UPDATE "], (
        "sablonul SQL compus s-a schimbat: %s" % sorted(set(literale)))
