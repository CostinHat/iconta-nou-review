# -*- coding: utf-8 -*-
"""GARD [R61, 26.08.2026]: raportul Z nu se poate înregistra de două ori, iar niciuna din cele
două rute nu scrie într-o lună închisă.

De unde vine. Costin a întrebat, la lotul 6, *ce deosebește `horeca/raport-z` de
`horeca/import-amef`*. Deosebirile sunt reale (fișier parsat vs. tastat · ciornă vs. validată),
iar rolul e explicat în cod. Dar **cele două asimetrii care contează mergeau invers decât rolul**:
ruta cu rol scria `validata` direct **fără verificare de duplicat**, iar ruta fără rol era singura
**fără poarta de perioadă închisă**. Un al doilea apel dubla venitul zilei, direct în evidență.

Decizia lui (varianta a): a doua notă se **refuză 409**. Un duplicat nu e o corecție, e o greșeală
de operare. Iar cheia nu e data — e **NUI + numărul raportului**: o firmă cu două case de marcat
are două rapoarte Z legitime în aceeași zi.

CE FACE IMPOSIBIL: o rută de raport Z care scrie în `inregistrari` **înainte** de a fi întrebat
dacă raportul există deja · una care scrie fără poarta de perioadă · o verificare de unicitate
care se uită într-o singură sursă (tastate DA, importate NU — adică jumătate de poartă).

CUM ASERTEAZĂ, fiindcă e chiar întrebarea pe care o pune clichetul 50: **numai pe noduri de AST**
— apeluri, linii, și mulțimea `_SURSE_Z` citită ca literal. Nicăieri, nici măcar la recunoașterea
scrierii, nu se caută un șir într-un text: ordinea se măsoară față de primul `…execute(…)`, care e
un nod, nu o interogare citită ca proză.

CE FACE ACUM ȘI NU FĂCEA [P5 val 1b, 10.09.2026]: **probează pe date că BAZA refuză.** Limita
declarată aici — *„nu probează pe date că baza refuză — e o gardă pe structura rutei, nu o probă
funcțională"* — a fost adevărată până în ziua în care garanția a trebuit să treacă din cod în
date. Ruta `horeca/import-amef` era `async def` fără niciun `await` după citirea fișierului,
deci bucla o rula până la capăt fără s-o întrerupă, iar verificarea „SELECT apoi INSERT" ținea
din **noroc**. Când valul 1 al lui P5 a mutat rutele pe fire, norocul se termina. Secțiunea a
doua a fișierului probează indexul unic parțial care a luat locul lui.

CE NU FACE NICI ACUM: nu spune că totalurile sunt corecte; spune că nota nu se poate dubla.
"""
import ast
import io
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
from core import raport_z as Z  # noqa: E402

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_RUTE = ("horeca_raport_z", "horeca_import_amef")
_GARZI = ("_cere_z_unic", "_cere_luna_deschisa")

# felurile în care lipsa poate arăta — mulțime închisă, ca asertarea să fie pe ele, nu pe frază
ABSENT, DUPA_SCRIERE, FARA_RUTA, FARA_EXECUTIE = (
    "absent", "dupa_scriere", "fara_ruta", "fara_executie")


def _functii(sursa):
    return {n.name: n for n in ast.walk(ast.parse(sursa))
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}


def _linia_primului_apel(fn, nume):
    linii = [n.lineno for n in ast.walk(fn)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == nume]
    return min(linii) if linii else None


def _linia_primei_executii(fn):
    """Linia primului `…execute(…)` din corp, sau None.

    Ancora e un **nod de AST** — un apel al cărui `func` e un atribut numit `execute` — nu un șir
    căutat în SQL. Prima formă a gardului citea textul interogării (*INSERT INTO … inregistrari*),
    ceea ce însemna că singura parte structurală lipsea exact acolo unde clichetul 50 o cere. Pe
    rutele astea cele două coincid: primul `execute` din corp **este** INSERT-ul.

    Afirmația e și mai tare așa: gărzile trebuie să fie înaintea **oricărei** interogări a rutei,
    nu doar înaintea scrierii. Consecința, declarată: dacă vreodată o rută pune un SELECT propriu
    înaintea gărzilor, testul cade — și e corect să cadă, fiindcă atunci poarta n-ar mai fi prima."""
    linii = [n.lineno for n in ast.walk(fn)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
             and n.func.attr == "execute"]
    return min(linii) if linii else None


def _lipsuri(sursa):
    """[(ruta, garda, felul)] — structuri, nu propoziții. Gardul asertează pe ele."""
    fns = _functii(sursa)
    rele = []
    for nume in _RUTE:
        fn = fns.get(nume)
        if fn is None:
            rele.append((nume, None, FARA_RUTA))
            continue
        scriere = _linia_primei_executii(fn)
        if scriere is None:
            rele.append((nume, None, FARA_EXECUTIE))
            continue
        for garda in _GARZI:
            apel = _linia_primului_apel(fn, garda)
            if apel is None:
                rele.append((nume, garda, ABSENT))
            elif apel > scriere:
                rele.append((nume, garda, DUPA_SCRIERE))
    return rele


@pytest.fixture(scope="module")
def sursa():
    return io.open(os.path.join(_RAD, "main.py"), encoding="utf-8").read()


def test_ambele_rute_verifica_unicitatea_si_perioada_INAINTE_de_a_scrie(sursa):
    rele = _lipsuri(sursa)
    assert not rele, (
        "raportul Z se poate înregistra de două ori, sau într-o lună închisă:" + chr(10)
        + chr(10).join("  %s · %s · %s" % r for r in rele))


def test_unicitatea_se_cauta_in_AMANDOUA_sursele(sursa):
    """Cheia e aceeași la ruta tastată și la import. O verificare care s-ar uita într-o singură
    sursă ar lăsa un raport deja importat să fie tastat a doua oară — jumătate de poartă, care
    arată exact ca o poartă întreagă.

    Asertează pe MULȚIMEA `_SURSE_Z`, citită ca literal din AST, nu pe SQL-ul în care e folosită:
    tocmai ca să nu depindă de cum e scris interogarea."""
    arb = ast.parse(sursa)
    legat = None
    for n in ast.walk(arb):
        if isinstance(n, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "_SURSE_Z" for t in n.targets):
            legat = n.value
    assert legat is not None, "`_SURSE_Z` a dispărut din main.py — gardul n-are ce compara"
    # [P5 val 1b] Nu mai e un literal: mulțimea s-a mutat în `core/raport_z.py`, unde stă și
    # indexul care o impune în bază. Două liste scrise separat ar fi putut descrie două lumi, iar
    # poarta din cod și indexul din baza de date ar fi apărat lucruri diferite fără să spună nimeni.
    assert (isinstance(legat, ast.Attribute) and legat.attr == "SURSE"), (
        "`_SURSE_Z` nu mai citește din `raport_z.SURSE`: %s. Dacă se copiază înapoi ca literal, "
        "codul și indexul pot diverge tăcut." % ast.dump(legat)[:120])
    from core import raport_z as _z
    assert set(_z.SURSE) == {"horeca_z", "amef"}, (
        "mulțimea surselor de raport Z s-a schimbat: %s. O sursă scoasă de aici înseamnă că o "
        "notă din ea se poate dubla." % sorted(_z.SURSE))


_FARA_GARDA = chr(10).join([
    "def horeca_import_amef(tenant_id, fisier, ctx=None):",
    "    with db.get_conn() as conn:",
    "        with conn.cursor() as cur:",
    "            cur.execute('INSERT INTO x.inregistrari (data, numar) VALUES (1,2)')",
    "",
    "def horeca_raport_z(tenant_id, rz, ctx=None):",
    "    with db.get_conn() as conn:",
    "        _cere_luna_deschisa(conn, 'x', rz.data)",
    "        with conn.cursor() as cur:",
    "            cur.execute('INSERT INTO x.inregistrari (data, numar) VALUES (1,2)')",
    "            _cere_z_unic(cur, 'x', 'Z-1-2')",
])


def test_CALIBRARE_gardul_prinde_lipsa_apelului_SI_ordinea_gresita():
    """Calibrare negativă pe propriul mod de eșec (interdicția 76), în ambele forme pe care le
    poate lua greșeala: apelul **absent** (prima rută) și apelul prezent, dar **după** scriere
    (a doua). A doua e forma insidioasă — codul conține numele gărzii, deci un gard care ar
    căuta numele în text ar fi trecut verde."""
    assert set(_lipsuri(_FARA_GARDA)) == {
        ("horeca_import_amef", "_cere_z_unic", ABSENT),
        ("horeca_import_amef", "_cere_luna_deschisa", ABSENT),
        ("horeca_raport_z", "_cere_z_unic", DUPA_SCRIERE),
    }, _lipsuri(_FARA_GARDA)


def test_ANTI_VACUU_rutele_chiar_se_gasesc(sursa):
    """Fără asta, o redenumire ar face gardul să treacă pe o mulțime goală."""
    lipsa = set(_RUTE) - set(_functii(sursa))
    assert not lipsa, "rute negăsite în main.py: %s — gardul s-ar uita în gol" % lipsa


# ===========================================================================
#  [P5 val 1b, 10.09.2026] A DOUA SECȚIUNE — garanția a trecut din COD în DATE
#
#  Probele de mai sus spun că ruta ÎNTREABĂ înainte să scrie. Astea spun că, dacă două
#  cereri întreabă în același timp și amândouă primesc «e liber», BAZA refuză a doua.
#  Prima jumătate păzește ordinea, a doua păzește cursa — și niciuna nu e destulă singură.
# ===========================================================================

SCHEMA_PROBA = "proba_z_unic"

_DDL_TABELA = (
    'CREATE TABLE "%s".inregistrari (id serial PRIMARY KEY, data date, '
    "numar varchar(50), sursa text)")


def _template():
    return io.open(os.path.join(_RAD, "tenant_template.sql"), encoding="utf-8").read()


# ═══════════════════════════════════════════════════════════════════════════
#  STRUCTURA — indexul e scris acolo unde firmele NOI îl iau
# ═══════════════════════════════════════════════════════════════════════════

def _despacheteaza_index(text):
    """`{nume, tabela, coloane, surse}` dintr-un `CREATE UNIQUE INDEX` — sau `None`.

    **De ce nu `NUME_INDEX in text`.** Un șir găsit într-un fișier trece și dacă indexul e pe alte
    coloane, pe altă tabelă, sau fără condiția parțială: păzește NUMELE de lângă lucru, nu lucrul.
    Se despachetează în câmpuri și se compară mulțimile — așa se prinde și greșeala pe care forma
    veche n-o putea prinde (METODA §23).
    """
    m = re.search(
        r"CREATE\s+UNIQUE\s+INDEX\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)\s+"
        r'ON\s+([\w."]+)\s*\(([^)]*)\)\s*WHERE\s+([^;]*)',
        text, re.I | re.S)
    if not m:
        return None
    return {
        "nume": m.group(1),
        "tabela": m.group(2).split(".")[-1].strip().strip(chr(34)).lower(),
        "coloane": [c.strip().lower() for c in m.group(3).split(",") if c.strip()],
        "surse": set(re.findall(r"'([^']+)'", m.group(4))),
        # câmpuri derivate: tratarea textului stă AICI, într-un singur loc declarat, ca probele
        # de mai jos să asertheze pe structură, nu pe fragmente de SQL
        "partial": True,                       # regexul cere `WHERE`, deci un rezultat E parțial
        "cere_numar": bool(re.search(r"numar\s+is\s+not\s+null", m.group(4), re.I)),
    }


def test_template_poarta_indexul():
    """O firmă nouă îl primește din `tenant_template.sql`, nu din migrarea de la pornire."""
    ix = _despacheteaza_index(_template())
    assert ix is not None, (
        "în tenant_template.sql nu există niciun `CREATE UNIQUE INDEX ... WHERE ...` — firmele NOI "
        "ar porni fără poartă, iar migrarea de la pornire ar fi singura care le-o pune")
    assert ix["nume"] == Z.NUME_INDEX, "alt nume de index: %r" % ix["nume"]
    assert ix["tabela"] == "inregistrari", "indexul e pe altă tabelă: %r" % ix["tabela"]
    assert ix["coloane"] == ["sursa", "numar"], "alte coloane: %r" % ix["coloane"]
    assert ix["surse"] == set(Z.SURSE), (
        "sursele din template (%s) diferă de cele din cod (%s) — două liste care descriu două "
        "lumi" % (sorted(ix["surse"]), sorted(Z.SURSE)))


def test_template_si_codul_descriu_ACELASI_index():
    """Cele două locuri unde se naște indexul nu pot diverge fără să pice ceva.

    Template-ul îl dă firmelor NOI, `core/raport_z.py` celor existente. Dacă s-ar despărți, jumătate
    din firme ar avea altă poartă decât cealaltă jumătate — și n-ar spune nimeni.
    """
    din_template = _despacheteaza_index(_template())
    din_cod = _despacheteaza_index(Z.sql_index("orice"))
    assert din_cod is not None, "`raport_z.sql_index` nu produce un index despachetabil"
    for camp in ("nume", "tabela", "coloane", "surse"):
        assert din_template[camp] == din_cod[camp], (
            "câmpul %r diferă: template=%r cod=%r"
            % (camp, din_template[camp], din_cod[camp]))


def test_indexul_e_PARTIAL_si_acopera_exact_sursele():
    """Parțial, și pe sursele DECLARATE — nu pe toată tabela.

    Alte surse au voie să repete un număr: o notă manuală și una de bancă pot purta același
    `numar` fără să fie duplicate. Un index total ar fi refuzat evidențe corecte.
    """
    ix = _despacheteaza_index(Z.sql_index("x"))
    assert ix is not None and ix["partial"], (
        "indexul NU e parțial — ar constrânge și sursele care au voie să repete un număr")
    assert ix["surse"] == set(Z.SURSE), (
        "condiția indexului acoperă %s, iar codul declară %s" % (sorted(ix["surse"]),
                                                                sorted(Z.SURSE)))
    assert ix["cere_numar"], "fără condiția pe număr, cheia n-are sens"


def test_multimea_surselor_e_UNA_SINGURA():
    """Poarta din cod și indexul din bază citesc ACEEAȘI listă, nu două scrise separat.

    Două liste ar fi putut descrie două mulțimi diferite, iar codul și baza ar fi apărat lucruri
    diferite fără ca nimic să spună.
    """
    import main as _main
    assert _main._SURSE_Z is Z.SURSE, (
        "`main._SURSE_Z` nu mai E obiectul din `raport_z.SURSE` — s-a copiat în loc să se importe")


def test_pornirea_migreaza_SI_verifica_SI_refuza_la_esec():
    """`lifespan` cheamă migrarea, verifică rezultatul, și ridică dacă rămâne vreun eșec.

    Se citește din AST, nu din text: interesează că apelurile EXISTĂ în funcție și că e un `raise`
    în ramura de eșec — nu că fișierul conține niște cuvinte.
    """
    m = ast.parse(io.open(os.path.join(_RAD, "main.py"), encoding="utf-8").read())
    ls = [n for n in ast.walk(m)
          if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == "lifespan"]
    assert len(ls) == 1, "nu găsesc `lifespan` (sau e definit de mai multe ori)"
    apeluri = set()
    for a in ast.walk(ls[0]):
        if isinstance(a, ast.Call) and isinstance(a.func, ast.Attribute):
            if isinstance(a.func.value, ast.Name) and a.func.value.id == "_raport_z":
                apeluri.add(a.func.attr)
    assert apeluri >= {"migreaza", "verifica"}, (
        "pornirea nu cheamă tot ce trebuie din `raport_z` — lipsesc %s. Migrarea singură nu e "
        "destulă: că `CREATE INDEX` n-a ridicat excepție nu dovedește că indexul există."
        % sorted({"migreaza", "verifica"} - apeluri))
    assert any(isinstance(a, ast.Raise) for a in ast.walk(ls[0])), (
        "`lifespan` n-are niciun `raise` — un eșec de migrare n-ar opri pornirea")


# ═══════════════════════════════════════════════════════════════════════════
#  PURTAREA — indexul chiar MUȘCĂ, pe o schemă adevărată
# ═══════════════════════════════════════════════════════════════════════════

@pytest.fixture()
def schema():
    """O schemă proprie, ștearsă la ieșire ORICE s-ar întâmpla."""
    from core import db
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute('DROP SCHEMA IF EXISTS "%s" CASCADE' % SCHEMA_PROBA)
            cur.execute('CREATE SCHEMA "%s"' % SCHEMA_PROBA)
            cur.execute(_DDL_TABELA % SCHEMA_PROBA)
        conn.commit()
    try:
        yield SCHEMA_PROBA
    finally:
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute('DROP SCHEMA IF EXISTS "%s" CASCADE' % SCHEMA_PROBA)
            conn.commit()


def _insereaza(conn, schema, numar, sursa="amef"):
    with conn.cursor() as cur:
        cur.execute('INSERT INTO "%s".inregistrari (data, numar, sursa) '
                    "VALUES ('2026-07-04', %%s, %%s)" % schema, (numar, sursa))


def test_al_doilea_raport_Z_identic_PICA(schema):
    """PROBA CARE CONTEAZĂ: cu indexul pus, aceeași cheie nu intră de două ori."""
    import psycopg2
    from core import db
    with db.get_conn() as conn:
        Z.aplica_index(conn, schema)
        _insereaza(conn, schema, "Z-8000000001-0042")
        with pytest.raises(psycopg2.errors.UniqueViolation):
            _insereaza(conn, schema, "Z-8000000001-0042")
        conn.rollback()


def test_FARA_index_al_doilea_TRECE(schema):
    """CALIBRAREA NEGATIVĂ, fără de care proba de mai sus n-ar dovedi nimic.

    Dacă al doilea `INSERT` ar pica și fără index — dintr-o cheie primară, dintr-un trigger, din
    orice altceva —, proba precedentă ar fi verde despre altceva decât despre index.
    """
    from core import db
    with db.get_conn() as conn:
        _insereaza(conn, schema, "Z-8000000001-0042")
        _insereaza(conn, schema, "Z-8000000001-0042")   # fără index: trece
        with conn.cursor() as cur:
            cur.execute('SELECT count(*) FROM "%s".inregistrari' % schema)
            assert cur.fetchone()[0] == 2
        conn.rollback()


def test_alta_sursa_are_voie_sa_repete_numarul(schema):
    """Indexul e parțial: o sursă din afara raportului Z nu e constrânsă."""
    from core import db
    with db.get_conn() as conn:
        Z.aplica_index(conn, schema)
        _insereaza(conn, schema, "NC-1", sursa="manual")
        _insereaza(conn, schema, "NC-1", sursa="manual")
        with conn.cursor() as cur:
            cur.execute('SELECT count(*) FROM "%s".inregistrari' % schema)
            assert cur.fetchone()[0] == 2, (
                "indexul constrânge și sursele care au voie să repete un număr")
        conn.rollback()


def test_verificarea_vede_lipsa(schema):
    """`verifica` trebuie să poată spune NU. Altfel «ok» n-ar însemna nimic."""
    from core import db
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_indexes WHERE schemaname = %s AND indexname = %s",
                        (schema, Z.NUME_INDEX))
            assert cur.fetchone() is None, "schema de probă are deja indexul — fixtura e greșită"
        Z.aplica_index(conn, schema)
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_indexes WHERE schemaname = %s AND indexname = %s",
                        (schema, Z.NUME_INDEX))
            assert cur.fetchone() is not None, "indexul nu s-a creat"
        conn.rollback()


def test_migrarea_nu_sterge_niciodata():
    """Decizia scrisă, verificată pe COD: nicio ștergere în calea de migrare.

    Dacă o firmă are deja duplicate, `CREATE UNIQUE INDEX` pică pe ea și migrarea o NUMEȘTE — nu
    alege singură care document rămâne. *Care din două e cel bun se decide de omul care a operat
    casa de marcat, nu de o migrare care își face loc.*
    """
    src = io.open(os.path.join(_RAD, "core", "raport_z.py"), encoding="utf-8").read()
    m = ast.parse(src)
    interzise = ("DELETE", "TRUNCATE", "DROP TABLE", "UPDATE ")
    for n in ast.walk(m):
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            sus = n.value.upper()
            for cuv in interzise:
                assert cuv not in sus or "DROP TABLE" not in sus, (
                    "SQL distructiv în calea de migrare: %r" % n.value[:120])
            assert not sus.strip().startswith(("DELETE", "TRUNCATE", "UPDATE")), (
                "SQL distructiv în calea de migrare: %r" % n.value[:120])


def test_esecul_NUMESTE_firmele_si_duplicatele():
    """Un refuz care nu spune CARE firme și CE chei îl trimite pe om să caute."""
    raport = {"esecuri": [{"tenant_id": 7, "schema": "firma_x",
                           "exceptie": "UniqueViolation: ...",
                           "duplicate": [("amef", "Z-1-0001", 2)]}]}
    # ASERȚIUNE PE TEXT, DELIBERAT, cu motivul lângă ea: subiectul probei ESTE textul care ajunge
    # la om. Nu există structură de asertat — mesajul e ieșirea finală, iar ce contează e că
    # numește firma, cheia și faptul că nu s-a șters nimic. *Aici „structura" ar fi o invenție.*
    comp = Z.componente_esec(raport)
    m = Z.mesaj_esec(raport)
    assert comp["numite"], "componentele mesajului sunt goale — proba n-ar discrimina nimic"
    for valoare in comp["numite"]:
        assert valoare in m, (
            "mesajul de eșec nu poartă %r — omul n-ar ști unde să caute" % valoare)
    assert comp["promisiune"] in m, "mesajul nu spune ce se întâmplă cu duplicatele"
