# -*- coding: utf-8 -*-
"""GARDA V1 — nicio citire SQL în corpul unei rute, și un detector de FEL care poate fi arătat greșit.

CE PĂZEȘTE. `PLAN_HARDENING.md:751` cere ca ruta să nu conțină SQL. V1 a mutat cele **107 citiri**
(106 `SELECT` + un CTE read-only) din `main.py` în treisprezece module de repository. Garda de mai
jos ține cifra la **zero**: o citire nouă scrisă direct în rută pică poarta.

DE CE E NEVOIE DE UN DETECTOR DE FEL, și de ce e el probat aici. Prima măsurătoare a felului SQL a
fost o euristică pe PRIMA LINIE a apelului: dacă `SELECT` nu era pe linia lui `execute`, instrucțiunea
rămânea „nedeterminată". Așa a ieșit cifra **91**, care a stat în două rapoarte ca univers al lui V1.
Cifra adevărată e **107**. *O euristică bună pentru a grupa valuri nu e bună pentru a defini
universul unui val* — iar diferența s-a văzut abia când cineva a cerut cifra pe bune.

Probele de mai jos acoperă fiecare formă care a produs diferența, plus RED-proof-ul euristicii vechi.
"""
from __future__ import annotations

import ast
import os
import sys

RADACINA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RADACINA, "scripts"))
sys.path.insert(0, RADACINA)

import scan_p7_straturi as S  # noqa: E402


def _fel(sql):
    return S.fel_sql(sql)


# ============================================================
#  1. FELUL — fiecare formă care apare în cod
# ============================================================
def test_select_pe_o_linie():
    assert _fel("SELECT 1") == (S.READ, "SELECT")


def test_select_care_incepe_pe_linia_urmatoare():
    """Forma care a produs cifra greșită: cuvântul nu e pe linia lui `execute`."""
    assert _fel("\n                SELECT id FROM t\n                WHERE x=%s\n") == (S.READ, "SELECT")


def test_select_pe_mai_multe_linii_cu_comentariu_sql():
    assert _fel("\n-- de ce\nSELECT a, b\nFROM t\n") == (S.READ, "SELECT")


def test_concatenare_literala():
    """`"SELECT a " "FROM t"` — două literale lipite de parser, nu de noi."""
    assert _fel("SELECT simbol, denumire FROM plan_conturi WHERE simbol ILIKE %s") == (S.READ, "SELECT")


def test_WITH_read_only_e_citire():
    assert _fel("WITH pe_an AS (SELECT id FROM t) SELECT * FROM pe_an") == (S.READ, "WITH_CITIRE")


def test_WITH_care_SCRIE_nu_e_citire():
    """Un CTE poate scrie. Dacă ar fi clasificat după primul cuvânt, o scriere ar intra în V1."""
    assert _fel("WITH x AS (DELETE FROM t RETURNING id) SELECT * FROM x") == (S.WRITE, "WITH_SCRIERE")


def test_scrierile():
    assert _fel("INSERT INTO t VALUES (1)") == (S.WRITE, "INSERT")
    assert _fel("UPDATE t SET a=1") == (S.WRITE, "UPDATE")
    assert _fel("DELETE FROM t WHERE id=%s") == (S.WRITE, "DELETE")


def test_update_construit_dinamic_e_tot_scriere():
    """`f"UPDATE {schema}.facturi SET " + ", ".join(...)`: partea din stânga e literală și spune
    limpede ce operație e. Prefixul ajunge; restul poate rămâne necunoscut."""
    # tabelă inventată dinadins: garda de coloane citește SQL-ul din tot repo-ul, iar o fixtură
    # care imită un tabel real ar fi raportată ca SQL cu coloane inexistente (și a fost, o dată)
    src = 'cur.execute(f"UPDATE {schema}.zt_proba SET " + ", ".join(_sets) + " WHERE id=%s", _vals)'
    n = ast.parse(src).body[0].value
    assert _fel(S.text_sql(n.args[0])) == (S.WRITE, "UPDATE")


def test_controlul_de_tranzactie():
    assert _fel("SAVEPOINT z") == (S.TRANSACTION_CONTROL, "SAVEPOINT")
    assert _fel("RELEASE SAVEPOINT z") == (S.TRANSACTION_CONTROL, "SAVEPOINT")
    assert _fel("ROLLBACK TO SAVEPOINT z") == (S.TRANSACTION_CONTROL, "SAVEPOINT")
    assert _fel("SET LOCAL search_path TO x, public") == (S.TRANSACTION_CONTROL, "SEARCH_PATH")


def test_un_SET_care_nu_e_search_path_ramane_NECUNOSCUT():
    """O clasă întreagă n-are voie să intre pe ușa din dos: doar `search_path` e control declarat."""
    assert _fel("SET statement_timeout = 5000") == (S.UNKNOWN, None)


def test_sql_fara_prefix_literal_e_NECUNOSCUT():
    src = 'cur.execute(construieste_sql(x), (1,))'
    n = ast.parse(src).body[0].value
    assert S.text_sql(n.args[0]) is None
    assert _fel(None) == (S.UNKNOWN, None)


# ============================================================
#  2. RED-PROOF — euristica veche rata exact forma care a produs diferența
# ============================================================
def test_RED_euristica_primei_linii_rata_un_SELECT_real():
    """Predicatul de atunci, scris aici ca să se vadă ce s-a schimbat: se citea doar prima linie.

    Pe forma din cod — apelul deschide un literal pe mai multe linii, iar `SELECT` stă abia pe linia
    următoare — euristica veche nu găsea nimic, iar instrucțiunea intra la „nedeterminat".
    Detectorul nou o citește corect. Dacă proba asta începe să pice, euristica a fost reintrodusă.
    """
    sql = "\n                SELECT ram_procent FROM public.metrici_sanatate\n            "
    prima_linie = sql.splitlines()[0]
    vechi = any(k in prima_linie.lower() for k in ("select", "insert", "update", "delete"))
    assert vechi is False, "premisa RED-proof: euristica veche chiar rata forma asta"
    assert _fel(sql) == (S.READ, "SELECT")


# ============================================================
#  3. CITIREA NU MAI STĂ ÎN RUTĂ — clichetul permanent
# ============================================================
def test_READ_SQL_IN_HTTP_ROUTE_e_zero():
    """Ținta lui V1, ținută pe loc. O citire nouă scrisă direct în rută pică aici."""
    pe_fel = S.d1_pe_fel()
    assert pe_fel[S.READ] == [], (
        "au reapărut citiri SQL în corpul rutelor: %s"
        % [(i.fisier, i.linie, i.cale) for i in pe_fel[S.READ]][:10])


def test_ANTI_VACUUM_detectorul_inca_vede_celelalte_feluri():
    """Zero citiri e o veste bună doar dacă detectorul chiar mai vede ceva. Scrierile și controlul
    de tranzacție au rămas în rute — sunt treaba lui V2 — și se numără."""
    pe_fel = S.d1_pe_fel()
    assert len(pe_fel[S.WRITE]) >= 100, "detectorul nu mai vede scrierile: %d" % len(pe_fel[S.WRITE])
    assert len(pe_fel[S.TRANSACTION_CONTROL]) >= 5
    assert pe_fel[S.UNKNOWN] == [], "instrucțiuni pe care detectorul nu le poate clasifica: %s" % (
        [(i.fisier, i.linie) for i in pe_fel[S.UNKNOWN]])
    assert len(S.rute()) >= 400, "universul rutelor s-a golit"


def test_o_citire_pusa_INAPOI_intr_o_ruta_ar_fi_prinsa():
    """Mutantul cerut: dacă cineva scrie un `SELECT` într-o rută, detectorul îl vede ca READ.

    Se probează pe un fragment sintetic, nu stricând `main.py` — dar pe ACEEAȘI cale de cod prin
    care trece și repo-ul real.
    """
    sursa = '''
@app.get("/proba")
def proba(ctx=None):
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT 1 FROM t WHERE id=%s", (1,))
        return cur.fetchone()
'''
    rute = S.rute_din_arbore(ast.parse(sursa), "proba.py")
    gasite, necunoscute = S.d1_din_rute(rute)
    assert len(gasite) == 1 and necunoscute == []
    assert _fel("SELECT 1 FROM t WHERE id=%s") == (S.READ, "SELECT")


def test_cuvantul_SELECT_pe_un_obiect_care_nu_e_cursor_nu_devine_item():
    """Anti-fals-pozitiv: textul „SELECT" într-un apel care nu e pe un cursor nu intră în D1."""
    sursa = '''
@app.get("/proba")
def proba(ctx=None):
    jurnal.execute("SELECT ceva")
    return {}
'''
    gasite, necunoscute = S.d1_din_rute(S.rute_din_arbore(ast.parse(sursa), "proba.py"))
    assert gasite == [] and len(necunoscute) == 1


# ============================================================
#  4. REPOSITORY-URILE NOI — ce au voie și ce nu
# ============================================================
MODULE_V1 = ("repo_admin", "repo_casa", "repo_contabilitate", "repo_declaratii", "repo_efactura",
             "repo_facturi", "repo_firma_profil", "repo_mijloace_fixe", "repo_portal",
             "repo_salariati", "repo_stocuri", "repo_tenants", "repo_utilizatori")


def _arbore_repo(modul):
    import io
    return ast.parse(io.open(os.path.join(RADACINA, "core", modul + ".py"), encoding="utf-8").read())


def test_repository_urile_NU_deschid_conexiuni_si_NU_comit():
    """Contractul din `PLAN_HARDENING.md:746` plus P4: repository-ul primește cursorul apelantului.

    Un `get_conn` aici ar rupe tranzacția apelantului în două — exact ce P4 a închis.
    """
    interzise = {"get_conn", "commit", "rollback", "HTTPException"}
    rele = []
    for m in MODULE_V1:
        for x in ast.walk(_arbore_repo(m)):
            if isinstance(x, ast.Call):
                f = x.func
                nume = f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else None)
                if nume in interzise:
                    rele.append((m, x.lineno, nume))
    assert rele == [], "repository care depășește stratul: %s" % rele


def test_fiecare_functie_de_repository_primeste_cursorul():
    """Primul parametru e cursorul. Fără asta, funcția și-ar lua singură o conexiune."""
    rele = []
    for m in MODULE_V1:
        for x in ast.walk(_arbore_repo(m)):
            if isinstance(x, ast.FunctionDef):
                if not x.args.args or x.args.args[0].arg != "cur":
                    rele.append((m, x.name))
    assert rele == [], "funcții care nu primesc cursorul apelantului: %s" % rele


def test_repository_urile_sunt_declarate_REPOSITORY_in_registru():
    from core import straturi
    declarate = straturi.module_din_strat(straturi.REPOSITORY)
    lipsa = [m for m in MODULE_V1 if "core/%s.py" % m not in declarate]
    assert lipsa == [], "module de repository nedeclarate în registru: %s" % lipsa
