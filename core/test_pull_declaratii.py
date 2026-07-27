# -*- coding: utf-8 -*-
"""Teste pe pull() — granita COD <-> BAZA DE DATE pentru generatoarele de declaratii.

DE CE (27.07.2026): cele ~175 de teste pe generatoare sunt PURE - cheama calcul_dXXX()
si build_xml() cu fixturi in memorie. Niciunul nu cheama pull(). Dar pull() e exact locul
unde au trait TOATE defectele gasite in iulie:
  - d406.pull citea `cont/debit/credit` in loc de `cont_debit/cont_credit/suma`
    -> GeneralLedgerEntries mereu gol, pentru ORICE firma, sub un `except: pass`;
  - d406.pull cerea coloane inexistente pe facturi -> 0 facturi in SourceDocuments,
    desi existau 5 reale;
  - toate mascate, deci XML valid structural si gol. DUK nu poate prinde asta.

Un test pur nu atinge schema. Cand cineva redenumeste o coloana, testele raman verzi si
declaratia iese goala. Aceste teste sunt puntea care lipsea.

CUM: schema TEMPORARA construita din tenant_template.sql intr-o tranzactie cu ROLLBACK -
acelasi tipar ca `core/audit_schema.auditeaza` (referinta temporara, zero mutatie). NU se
ating tenantii reali, NU se scrie nimic definitiv.

DOUA CLASE DE TESTE:
  A. pull() VEDE datele care exista (daca ar citi coloane gresite, n-ar vedea nimic);
  B. pull() CRAPA ZGOMOTOS cand schema nu se potriveste (mutatie: redenumesc o coloana).
Clasa B e cea care ar fi prins bug-urile din iulie.

LIMITA DECLARATA: pe `SELECT *`, garda de coloane (common.cere_coloane) verifica randurile
CITITE - deci pe o tabela GOALA nu are ce verifica si trece. O coloana disparuta pe o firma
fara salariati nu se semnaleaza. Corect ca mecanism (fara randuri nu ai ce controla), dar
inseamna ca acoperirea depinde de existenta datelor. De aceea fiecare test de mutatie isi
SEAMANA datele intai.
"""
import pytest

from core import db, tenant_provisioning as tp

SCHEMA_T = "ztest_pull"


def _db_ok():
    try:
        db.init_pool()
        with db.get_conn():
            return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


@pytest.fixture
def schema():
    """Schema temporara din template, populata minimal. ROLLBACK garantat la final."""
    db.init_pool()
    with db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA_T)
                cur.execute(tp.parametrizeaza_template(
                    open("tenant_template.sql", encoding="utf-8").read(), SCHEMA_T))
                cur.execute("SET search_path TO %s, public" % SCHEMA_T)
                cur.execute(
                    "INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, caen, "
                    "platitor_tva, tip_decont) VALUES "
                    "(1, 'PROBA SRL', '14399840', 'Str. Test 1', 'Bucuresti', 'B', '6202', true, 'L') "
                    "ON CONFLICT (id) DO UPDATE SET nume=EXCLUDED.nume, cui=EXCLUDED.cui")
            yield conn
        finally:
            conn.rollback()


def _factura(conn, **kw):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO facturi (numar, data_emitere, directie, tert_cui, tert_nume, "
            "total, tva, taxare_inversa) VALUES (%s,%s,%s,%s,%s,%s,%s,false) RETURNING id",
            (kw.get("numar", "1"), kw.get("data", "2026-06-15"), kw.get("directie", "emisa"),
             kw.get("cui", "RO14399840"), kw.get("nume", "CLIENT SRL"),
             kw.get("total", 1210), kw.get("tva", 210)))
        fid = cur.fetchone()[0]
        cur.execute(
            "INSERT INTO factura_linii (factura_id, descriere, um, cantitate, pret_unitar, cota_tva) "
            "VALUES (%s,'Serviciu','buc',1,%s,%s)",
            (fid, kw.get("total", 1210) - kw.get("tva", 210), kw.get("cota", 21)))
    return fid


# ============================================================
#  A. pull() VEDE ce exista
# ============================================================
def test_d300_pull_vede_factura_emisa(schema):
    from core import d300
    _factura(schema, total=1210, tva=210)
    prof, facturi = d300.pull(schema, SCHEMA_T, 2026, 6)
    assert prof and prof.get("cui") == "14399840", "profilul firmei nu e citit"
    assert len(facturi) == 1, "factura reala nu ajunge in pull (coloane gresite?)"
    assert float(facturi[0]["tva"]) == 210.0


def test_d300_pull_nu_ia_facturi_din_alta_luna(schema):
    from core import d300
    _factura(schema, data="2026-05-15")
    _, facturi = d300.pull(schema, SCHEMA_T, 2026, 6)
    assert facturi == [], "fereastra de luna nu filtreaza"


def test_d394_pull_vede_factura(schema):
    from core import d394
    _factura(schema)
    rez = d394.pull(schema, SCHEMA_T, 2026, 6)
    assert rez is not None
    text = repr(rez)
    assert "14399840" in text or "CLIENT SRL" in text, "d394.pull nu vede factura reala"


def test_d112_pull_vede_salariatul(schema):
    from core import d112
    with schema.cursor() as cur:
        cur.execute(
            "INSERT INTO salariati (nume, prenume, cnp, data_angajare, salariu_brut, "
            "activ, ore_zi, part_time) VALUES "
            "('POPESCU','ION','1900101410011','2026-01-01',5000,true,8,false)")
    prof, sal = d112.pull(schema, SCHEMA_T, 2026, 6)
    assert prof.get("cui") == "14399840"
    assert len(sal) == 1, "salariatul activ nu ajunge in pull"
    assert sal[0]["nume"] == "POPESCU"


def test_d112_pull_ignora_salariatul_inactiv(schema):
    from core import d112
    with schema.cursor() as cur:
        cur.execute(
            "INSERT INTO salariati (nume, prenume, cnp, data_angajare, salariu_brut, "
            "activ, ore_zi, part_time) VALUES "
            "('DEMISIONAT','X','1900101410011','2026-01-01',5000,false,8,false)")
    _, sal = d112.pull(schema, SCHEMA_T, 2026, 6)
    assert sal == [], "salariatii inactivi nu trebuie sa intre in D112"


def test_d301_pull_vede_operatiunea(schema):
    from core import d301
    with schema.cursor() as cur:
        cur.execute(
            "INSERT INTO d301_operatiuni (an, luna, tip, nr_doc, data_doc, val_valuta, "
            "tip_valuta, curs, tva) VALUES (2026,6,5,'F1','2026-06-10',100,'EUR',4.97,105)")
    prof, ops = d301.pull(schema, SCHEMA_T, 2026, 6)
    assert prof.get("cui") == "14399840"
    assert len(ops) == 1, "operatiunea D301 nu ajunge in pull"


# ============================================================
#  B. pull() CRAPA ZGOMOTOS pe schema nepotrivita (clasa iulie 2026)
# ============================================================
def _seamana_salariat(conn):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO salariati (nume, prenume, cnp, data_angajare, salariu_brut, "
            "activ, ore_zi, part_time) VALUES "
            "('POPESCU','ION','1900101410011','2026-01-01',5000,true,8,false)")


def _seamana_d301(conn):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO d301_operatiuni (an, luna, tip, nr_doc, data_doc, val_valuta, "
            "tip_valuta, curs, tva) VALUES (2026,6,5,'F1','2026-06-10',100,'EUR',4.97,105)")


@pytest.mark.parametrize("modul,tabela,coloana,seamana", [
    ("d300", "facturi", "tva", _factura),
    ("d300", "firma_profil", "tip_decont", None),
    ("d112", "salariati", "salariu_brut", _seamana_salariat),
    ("d301", "d301_operatiuni", "curs", _seamana_d301),
])
def test_pull_crapa_zgomotos_cand_coloana_lipseste(schema, modul, tabela, coloana, seamana):
    """Mutatie: redenumesc o coloana pe care pull() o cere. Trebuie EROARE, nu lista goala.

    Asta e testul care ar fi prins bug-urile din iulie: acolo query-ul crapa, masca il
    inghitea, iar generatorul primea zero randuri si scotea o declaratie valida si goala.

    DATELE SE SEAMANA INTAI, si asta conteaza: garda `common.cere_coloane` verifica randurile
    CITITE, deci pe o tabela GOALA nu are ce verifica si trece. Limita reala a gardei, nu doar
    a testului - prima versiune a acestui test picase exact asa (tabela salariati era goala).
    """
    import importlib
    m = importlib.import_module("core.%s" % modul)
    if seamana:
        seamana(schema)
    with schema.cursor() as cur:
        cur.execute("ALTER TABLE %s.%s RENAME COLUMN %s TO %s_x"
                    % (SCHEMA_T, tabela, coloana, coloana))
    with pytest.raises(Exception) as e:
        m.pull(schema, SCHEMA_T, 2026, 6)
    mesaj = str(e.value).lower()
    assert coloana in mesaj or "does not exist" in mesaj or "exista" in mesaj, \
        "eroarea nu spune ce lipseste: %s" % str(e.value)[:150]


def test_pull_nu_inghite_tabela_lipsa(schema):
    """Aceeasi clasa, la nivel de tabela."""
    from core import d300
    with schema.cursor() as cur:
        cur.execute("ALTER TABLE %s.facturi RENAME TO facturi_x" % SCHEMA_T)
    with pytest.raises(Exception):
        d300.pull(schema, SCHEMA_T, 2026, 6)


def test_schema_temporara_chiar_dispare():
    """Garda pe test: schema de proba NU trebuie sa ramana in baza dupa rulare."""
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM information_schema.schemata WHERE schema_name=%s",
                        (SCHEMA_T,))
            assert cur.fetchone() is None, \
                "schema %s a ramas in baza - ROLLBACK-ul n-a functionat" % SCHEMA_T
        conn.rollback()
