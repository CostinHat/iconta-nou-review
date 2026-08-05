# -*- coding: utf-8 -*-
"""
core/test_d406_reconciliere.py — gardul A DOUA CALE D406/SAF-T (05.08.2026, campanie pas 4/6).

Apara:
  - NON-TAUTOLOGIA (AST): calea 2 nu foloseste d406.pull/construieste.
  - reconcilierea PICA pe: suma alterata la un cont / GeneralLedgerEntries GOL (bug-ul istoric) /
    dezechilibru al dublei partide (MUTATIE).
  - pe date corecte NU alarma falsa (proba functionala pe schema efemera).
"""
import io
import ast
import pytest

from core import d406 as _d406
from core import d406_reconciliere as _rec
from core.d406_reconciliere import reconciliaza, verifica_reconciliere, ReconciliereD406


# ============================================================
#  1. NON-TAUTOLOGIE (AST).
# ============================================================
def test_non_tautologie_calea2_nu_foloseste_generatorul_d406():
    tree = ast.parse(io.open(_rec.__file__, encoding="utf-8").read())
    module_e = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom) and n.module:
            module_e.add(n.module)
        elif isinstance(n, ast.Import):
            for a in n.names:
                module_e.add(a.name)
    assert "core.d406" not in module_e, "calea 2 importa generatorul d406"
    folosite = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} \
             | {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    for interzis in ("construieste", "pull", "_generalledger"):
        assert interzis not in folosite, "calea 2 foloseste '%s'" % interzis


# ============================================================
#  Fixtura DB: firma + 3 note contabile VALIDATE, echilibrate.
#  N1 4111/707 1000 (vanzare) ; N2 5121/4111 600 (incasare) ; N3 371/401 400 (achizitie).
# ============================================================
from core import db as _db, tenant_provisioning as _tp
_SCHEMA = "test_d406_recon"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


def _nota(cur, data, desc, cd, cc, suma):
    cur.execute("INSERT INTO inregistrari (data, descriere, status) VALUES (%s,%s,'validata') RETURNING id",
                (data, desc))
    nid = cur.fetchone()[0]
    cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) "
                "VALUES (%s,%s,%s,%s)", (nid, cd, cc, suma))
    return nid


@pytest.fixture
def conn_recon():
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(_tp.parametrizeaza_template(
                    open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                cur.execute("SET search_path TO %s, public" % _SCHEMA)
                cur.execute(
                    "INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,"
                    "declarant_nume,declarant_prenume,declarant_functie,platitor_tva,tip_decont,regim_fiscal) "
                    "VALUES (1,'TEST SRL','14399840','Str 1','Bucuresti','B','6920','BCR',"
                    "'RO49BCRA0000000000000000','POP','ION','EXPERT CONTABIL',true,'L','real')")
                _nota(cur, '2026-06-05', 'Vanzare', '4111', '707', 1000)
                _nota(cur, '2026-06-10', 'Incasare', '5121', '4111', 600)
                _nota(cur, '2026-06-12', 'Achizitie', '371', '401', 400)
            yield conn
        finally:
            conn.rollback()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_reconciliere_curata_si_genereaza_trece(conn_recon):
    """PROBA FUNCTIONALA: genereaza() (cu POARTA wired) trece; reconciliaza NU raporteaza nimic."""
    xml, res = _d406.genereaza(conn_recon, _SCHEMA, 2026, 6)   # daca gardul da fals-pozitiv -> AICI crapa
    rap = reconciliaza(conn_recon, _SCHEMA, 2026, 6, res)
    assert rap["divergente"] == [], "alarma falsa: %s" % rap["divergente"]
    assert rap["dezechilibru"] is None
    assert "declaratie" in xml.lower()


# ---- MUTATIE ----

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_mutatie_suma_alterata_pica(conn_recon):
    """Emisia altereaza debitul unui cont -> nu se mai leaga de rulajul independent."""
    _xml, res = _d406.genereaza(conn_recon, _SCHEMA, 2026, 6)
    # gaseste linia debit pe 4111 (nota N1) si o strica
    for n in res.note:
        for l in n.linii:
            if l.cont == "4111" and l.debit:
                l.debit = l.debit + 9999
    with pytest.raises(ReconciliereD406) as ei:
        verifica_reconciliere(conn_recon, _SCHEMA, 2026, 6, res)
    msg = str(ei.value)
    assert "cont 4111 debit" in msg and "cale2=1000.00" in msg, msg


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_mutatie_general_ledger_gol_pica(conn_recon):
    """Bug ISTORIC (16.07): GeneralLedgerEntries ramanea GOL tacit. Calea 2 gaseste notele in DB."""
    _xml, res = _d406.genereaza(conn_recon, _SCHEMA, 2026, 6)
    res.note = []   # <- mutatie: emisie goala
    with pytest.raises(ReconciliereD406) as ei:
        verifica_reconciliere(conn_recon, _SCHEMA, 2026, 6, res)
    msg = str(ei.value)
    assert "cont 4111" in msg and "saft=0.00" in msg, msg


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_mutatie_dezechilibru_dubla_partida_pica(conn_recon):
    """Emisia scoate o linie de credit -> Σdebit != Σcredit."""
    _xml, res = _d406.genereaza(conn_recon, _SCHEMA, 2026, 6)
    # scot prima linie de credit gasita -> dezechilibru
    gasit = False
    for n in res.note:
        for i, l in enumerate(list(n.linii)):
            if l.credit and not gasit:
                n.linii.remove(l); gasit = True
                break
        if gasit:
            break
    with pytest.raises(ReconciliereD406) as ei:
        verifica_reconciliere(conn_recon, _SCHEMA, 2026, 6, res)
    assert "DEZECHILIBRU dubla partida" in str(ei.value), str(ei.value)
