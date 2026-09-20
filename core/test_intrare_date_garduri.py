# -*- coding: utf-8 -*-
"""GARZI cat.1 (Intrare date) — RATCHET: idempotenta importurilor + banii nu ajung NULL, verificate MECANIC.

GARZI.md linia 69-70 cerea, ca LIPSA: „gard care cere NOT NULL pe fiecare coloana de bani si cheie
naturala unica pe fiecare tabel de import. Idempotenta importurilor nu e verificata mecanic." Sub-lotul 1
(decizia Costin 20.09) adauga constrangerile pe schema; gardul asta le APARA sa nu se erodeze:

  1. o coloana de bani (numeric, cu nume din `BANI`) nullable si NEdeclarata in `NULLABLE_OK` -> PICA.
     (Un camp de bani lipsa -> NULL -> 0 tacut e chiar esecul cat.1.)
  2. un tabel de import declarat FARA cheie naturala UNIQUE si NEdeclarat in `FARA_CHEIE_OK` -> PICA.
     (Fara cheie, reimportul dubleaza — clasa C5, generalizata.)

Referinta = schema efemera din tenant_template.sql (ce primeste un tenant NOU), nu un tenant care
poate fi driftat. Whitelist-urile sunt DECLARATE cu motiv, si gardul verifica si ca fiecare intrare de
whitelist e reala (fara whitelist stale). Idempotenta e probata FUNCTIONAL: constrangerea chiar respinge
un duplicat / un NULL."""
import io
import pytest

from core import db as _db
from core import tenant_provisioning as _tprov

_SCH = "efemer_intrare_date_garduri"

# Nume care fac dintr-o coloana numeric una de BANI (aceeasi lista folosita la investigatie).
BANI = ("suma", "valoare", "total", "pret", "tva", "baza", "salariu", "cost", "plata", "incasare",
        "debit", "credit", "curs", "impozit", "cas", "cass", "cam", "venit", "cheltuiala", "marja",
        "avans", "rest", "dobanda", "penalitate", "comision", "brut", "net", "cotizatie", "deducere",
        "diurna", "amount", "sold")

# (A+B au fost puse NOT NULL.) (C) LEGITIM nullable — declarate cu motiv. Gardul cere ca fiecare sa fie
# chiar o coloana de bani nullable existenta (fara whitelist stale).
NULLABLE_OK = {
    ("facturi", "curs_bnr"): "curs BNR doar pe facturi in valuta; RON -> NULL (A1)",
    ("facturi", "total_lei"): "echivalent lei doar pe valuta; RON -> NULL",
    ("facturi", "tva_lei"): "echivalent lei doar pe valuta; RON -> NULL",
    ("d301_operatiuni", "curs"): "curs valutar; operatiune RON -> NULL",
    ("rip_operatiuni", "curs_valutar"): "curs valutar; RON -> NULL",
    ("rip_operatiuni", "suma_valuta"): "suma in valuta; operatiune RON -> NULL",
    ("concedii_medicale", "venituri_6_luni"): "baza pe 6 luni absenta/necalculata (NULL-uri reale)",
    ("miscari_stoc", "pret_unitar"): "miscarea poarta `valoare` (total); pret unitar optional (iesire/inventar il lasa NULL)",
    ("salariati", "salariu_brut"): "baza poate fi LEGITIM lipsa -> semnalata, nu tacuta (GARZI cat.1)",
    ("registre_art321", "valoare"): "lit. f) (bunuri_primite) NU cere valoare — NOT NULL ar bloca o inscriere legala",
}

# Tabele de import (entitati, nu linii-copil): fiecare cere o cheie naturala UNIQUE.
IMPORT_TABLES = ("efactura_primite", "extras_import", "solduri_initiale", "solduri_parteneri",
                 "asociati", "clienti", "furnizori", "state_plata", "articole", "produse",
                 "mijloace_fixe", "salariati", "registratura", "pontaj")

# Tabele de import DECLARATE fara cheie naturala, cu motiv (whitelist ratchet).
FARA_CHEIE_OK = {
    "produse": "fara camp de cod (nici cod, nici barcode) — decizie de schema deschisa",
    "mijloace_fixe": "sub-lotul 2 — duplicat real de cod in tenant_003, dupa curatare primeste UNIQUE(cod)",
}


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


_DB = _db_ok()
pytestmark = pytest.mark.skipif(not _DB, reason="DB indisponibil")


@pytest.fixture(scope="module")
def ref():
    """Schema efemera din template = referinta (ce primeste un tenant NOU). ROLLBACK la iesire."""
    _db.init_pool()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
            cur.execute(_tprov.parametrizeaza_template(
                io.open("tenant_template.sql", encoding="utf-8").read(), _SCH))
        c.commit()
    yield _SCH
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
        c.commit()


def _coloane_bani_nullable(cur, schema):
    cur.execute("""SELECT table_name, column_name FROM information_schema.columns
                   WHERE table_schema=%s AND data_type='numeric' AND is_nullable='YES'
                   ORDER BY table_name, column_name""", (schema,))
    return [(t, c) for t, c in cur.fetchall() if any(k in c.lower() for k in BANI)]


def _tabele_cu_cheie_naturala(cur, schema):
    """Tabelele cu o cheie naturala: fie o constrangere UNIQUE, fie un PRIMARY KEY care NU e doar
    surogatul `id` (un PK compus/de business, ex. pontaj(salariat_id, zi), conteaza ca cheie naturala)."""
    cur.execute("""SELECT tc.table_name, tc.constraint_type,
                          string_agg(kcu.column_name, ',' ORDER BY kcu.ordinal_position) AS cols
                   FROM information_schema.table_constraints tc
                   JOIN information_schema.key_column_usage kcu
                     ON tc.constraint_name=kcu.constraint_name AND tc.table_schema=kcu.table_schema
                   WHERE tc.table_schema=%s AND tc.constraint_type IN ('UNIQUE','PRIMARY KEY')
                   GROUP BY tc.table_name, tc.constraint_type, tc.constraint_name""", (schema,))
    out = set()
    for t, typ, cols in cur.fetchall():
        if typ == "UNIQUE":
            out.add(t)
        elif typ == "PRIMARY KEY" and cols != "id":  # PK natural (compus/de business), nu surogatul id
            out.add(t)
    return out


# ── (1) nicio coloana de bani nullable in afara whitelist-ului ──
def test_nicio_coloana_de_bani_nullable_nedeclarata(ref):
    with _db.get_conn() as c, c.cursor() as cur:
        nullable = _coloane_bani_nullable(cur, ref)
    rele = [(t, col) for t, col in nullable if (t, col) not in NULLABLE_OK]
    assert not rele, (
        "coloane de bani NULLABLE nedeclarate (camp lipsa -> NULL -> 0 tacut, esecul cat.1): %s.\n"
        "Ori pun NOT NULL (migrare_intrare_date_garduri), ori le declar in NULLABLE_OK cu motiv." % rele)


def test_whitelist_nullable_nu_e_stale(ref):
    """Fiecare intrare NULLABLE_OK e chiar o coloana de bani nullable existenta — altfel whitelist stale
    ar ascunde ca s-a pus deja NOT NULL (si gardul ar trece degeaba pe o exceptie moarta)."""
    with _db.get_conn() as c, c.cursor() as cur:
        nullable = set(_coloane_bani_nullable(cur, ref))
    stale = [k for k in NULLABLE_OK if k not in nullable]
    assert not stale, "NULLABLE_OK stale (coloana nu mai e nullable sau nu exista): %s" % stale


# ── (2) fiecare tabel de import are cheie naturala UNIQUE (sau e declarat fara) ──
def test_fiecare_tabel_de_import_are_cheie_naturala(ref):
    with _db.get_conn() as c, c.cursor() as cur:
        cu_uniq = _tabele_cu_cheie_naturala(cur, ref)
    lipsa = [t for t in IMPORT_TABLES if t not in cu_uniq and t not in FARA_CHEIE_OK]
    assert not lipsa, (
        "tabele de import FARA cheie naturala UNIQUE (reimport -> dublare, clasa C5): %s.\n"
        "Ori adaug UNIQUE (migrare_intrare_date_garduri), ori declar in FARA_CHEIE_OK cu motiv." % lipsa)


def test_whitelist_fara_cheie_nu_e_stale(ref):
    """Un tabel declarat FARA_CHEIE_OK dar care ARE deja UNIQUE = whitelist stale (s-a rezolvat, dar
    exceptia a ramas si ar ascunde urmatoarea regresie)."""
    with _db.get_conn() as c, c.cursor() as cur:
        cu_uniq = _tabele_cu_cheie_naturala(cur, ref)
    stale = [t for t in FARA_CHEIE_OK if t in cu_uniq]
    assert not stale, "FARA_CHEIE_OK stale (tabelul are deja UNIQUE): %s" % stale


# ── FUNCTIONAL + MUTATIE: constrangerea chiar respinge duplicatul / NULL-ul ──
def test_unique_respinge_duplicatul_functional(ref):
    """Non-tautologie: gardul de mai sus vede constrangerea; asta arata ca ea CHIAR blocheaza."""
    import psycopg2
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute(f"INSERT INTO {ref}.clienti (nume, cui) VALUES ('A','RO123')")
            with pytest.raises(psycopg2.errors.UniqueViolation):
                cur.execute(f"INSERT INTO {ref}.clienti (nume, cui) VALUES ('B','RO123')")
        c.rollback()
    # NULL-uri multiple pe cui raman permise (PF fara CUI)
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute(f"INSERT INTO {ref}.clienti (nume, cui) VALUES ('C',NULL)")
            cur.execute(f"INSERT INTO {ref}.clienti (nume, cui) VALUES ('D',NULL)")  # nu pica
        c.rollback()


def test_not_null_respinge_nullul_functional(ref):
    import psycopg2
    with _db.get_conn() as c:
        with c.cursor() as cur:
            with pytest.raises(psycopg2.errors.NotNullViolation):
                cur.execute(f"INSERT INTO {ref}.bonuri (total) VALUES (NULL)")
        c.rollback()
