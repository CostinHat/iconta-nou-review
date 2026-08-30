# -*- coding: utf-8 -*-
"""
core/test_d301_reconciliere.py — gardul A DOUA CALE D301 (10.08.2026).

Apara:
  - NON-TAUTOLOGIA caii 2 vs generator (probata STATIC pe AST: fara cod comun).
  - ca reconcilierea PICA (anti-mort "clasa D301 moarta"):
      * MUTATIE prin ROLLBACK: o operatiune stearsa din agregare -> divergenta;
      * SEMANTIC T7: o operatiune in RON cu curs!=1 face generatorul sa emita
        baza SUPRAEVALUATA (val_valuta x curs), pe care DUK o accepta; calea 2
        (regula corecta RON=>curs 1) o prinde end-to-end prin genereaza().
  - ca pe date corecte NU produce alarma falsa (baseline pe schema efemera).
  - BASELINE REAL (BETA/tenant_014) reconcileaza SI e DUK-valid.
  - limitele declarate: curs valuta (non-RON) partajat de ambele cai = NEACOPERIT,
    nu alarma falsa.
"""
import io
import pytest

from core.common import Perioada
from core import d301 as _d301
from core import d301_reconciliere as _rec
from core.d301_reconciliere import reconciliaza, verifica_reconciliere, ReconciliereD301


# ============================================================
#  1. NON-TAUTOLOGIE — probata STATIC: calea 2 nu atinge agregarea generatorului.
# ============================================================
def test_non_tautologie_calea2_nu_importa_agregarea_generatorului():
    """Gardul e valid doar daca cele doua cai NU impart codul de agregare/rotunjire. Probam MECANIC
    (pe AST, nu pe text - ca sa nu se prinda pe propriul docstring) ca modulul caii 2:
      - NU importa modulul core.d301;
      - NU foloseste nicaieri (nume sau atribut) calcul_d301 / calc_baza / _r0 / pull.
    Altfel un bug comun ar trece nevazut de ambele cai = tautologie."""
    import ast
    tree = ast.parse(io.open(_rec.__file__, encoding="utf-8").read())
    module_e = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom) and n.module:
            module_e.add(n.module)
        elif isinstance(n, ast.Import):
            for a in n.names:
                module_e.add(a.name)
    assert "core.d301" not in module_e, "NON-TAUTOLOGIE: calea 2 importa modulul generatorului"
    folosite = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} \
             | {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    for interzis in ("calcul_d301", "calc_baza", "_r0", "pull"):
        assert interzis not in folosite, "NON-TAUTOLOGIE incalcata: calea 2 foloseste '%s'" % interzis
    # dependentele permise: rotunjirea vine din decimal, autonom fata de calea 1
    assert "decimal" in module_e


# ============================================================
#  Fixtura DB: firma neinregistrata TVA normal, schema efemera.
#   luna 8 (BASELINE curat): op EUR 1000@4.97 tip1 (tva200) + op EUR 500@5.00 tip2 (tva100).
#   luna 7 (SEMANTIC T7):    op RON 1000@curs5 tip1 -> generatorul umfla baza la 5000.
# ============================================================
from core import db as _db, tenant_provisioning as _tp
_SCHEMA = "test_d301_recon"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


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
                    "INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, caen, banca, iban, "
                    "regim_fiscal, platitor_tva, tip_decont, tva_la_incasare,declarant_nume,declarant_prenume,declarant_functie) "
                    "VALUES (1,'RECON D301 SRL','14399840','Str Test 1','Bucuresti','B','4711','BCR',"
                    "'RO49AAAA1B31007593840000','real',false,'L',false,'Popescu','Ion','ADMINISTRATOR')")
                # luna 8 BASELINE (reconciliaza): valuta EUR, curs stocat folosit de ambele cai
                cur.execute("INSERT INTO d301_operatiuni (an, luna, tip, nr_doc, data_doc, val_valuta, tip_valuta, curs, tva) "
                            "VALUES (2026,8,1,'AIC-1','2026-08-05',1000,'EUR',4.97,200)")   # baza=4970
                cur.execute("INSERT INTO d301_operatiuni (an, luna, tip, nr_doc, data_doc, val_valuta, tip_valuta, curs, tva) "
                            "VALUES (2026,8,2,'TRA-1','2026-08-06',500,'EUR',5.00,100)")    # baza=2500, mij_transp
                # luna 7 SEMANTIC T7: RON cu curs!=1 -> generatorul emite baza=round(1000x5)=5000 (umflata 5x)
                cur.execute("INSERT INTO d301_operatiuni (an, luna, tip, nr_doc, data_doc, val_valuta, tip_valuta, curs, tva) "
                            "VALUES (2026,7,1,'RON-1','2026-07-05',1000,'RON',5,0)")
            yield conn
        finally:
            conn.rollback()


# ============================================================
#  2. BASELINE efemer: pe date corecte, genereaza() (cu POARTA wired) trece.
# ============================================================
@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_reconciliere_curata_pe_date_corecte_si_genereaza_trece(conn_recon):
    """PROBA FUNCTIONALA: pe date valuta corecte, genereaza() (are POARTA a-doua-cale wired) trece,
    iar reconciliaza() NU raporteaza nicio divergenta."""
    per = Perioada(2026, luna=8)
    xml, res = _d301.genereaza(conn_recon, _SCHEMA, per)   # daca gardul da fals-pozitiv -> AICI crapa
    assert res.totaluri[1] == (4970, 200)
    assert res.totaluri[2] == (2500, 100)
    assert res.total_plata_a == 4970 + 200 + 2500 + 100
    rap = reconciliaza(conn_recon, per, res)
    assert rap["acoperit"] is True
    assert rap["divergente"] == [], "alarma falsa pe date corecte: %s" % rap["divergente"]
    assert "<declaratie301" in xml


# ============================================================
#  3a. ANTI-MORT (MUTATIE prin ROLLBACK): operatiune stearsa din agregare -> PICA.
# ============================================================
@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_mutatie_operatiune_pierduta_din_agregare_pica(conn_recon):
    """Generatorul a vazut ambele operatiuni (res). Injectam divergenta STERGAND op tip=2 din
    tabela (in tranzactie, rollback la final): calea 2 reinterogheaza si nu o mai vede -> sectiunea 2
    a generatorului (2500/100) nu se reconciliaza cu cale2 (0/0). RIDICA, numind AMBELE valori."""
    per = Perioada(2026, luna=8)
    _, res = _d301.genereaza(conn_recon, _SCHEMA, per)
    with conn_recon.cursor() as cur:
        cur.execute("DELETE FROM d301_operatiuni WHERE luna=8 AND tip=2")   # <- mutatie via ROLLBACK
    with pytest.raises(ReconciliereD301) as ei:
        verifica_reconciliere(conn_recon, per, res)
    msg = str(ei.value)
    assert "baza2" in msg and "generator=2500" in msg and "cale2=0" in msg, msg   # ambele valori


# ============================================================
#  3b. ANTI-MORT (SEMANTIC T7): RON cu curs!=1 -> baza generatorului supraevaluata -> PICA.
#      Proba END-TO-END: genereaza() insasi ridica (POARTA wired), pe DATE REALE (fara a atinge res).
# ============================================================
@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_semantic_ron_curs_diferit_de_1_baza_supraevaluata_pica(conn_recon):
    """Operatiune in RON cu curs=5 stocat: calc_baza (generator) emite round(1000x5)=5000 - baza
    umflata 5x, pe care DUK o ACCEPTA (totalPlata_A ramane coerent). Calea 2 aplica regula corecta
    (RON => curs 1) -> baza=1000. genereaza() (POARTA wired) trebuie sa RIDICE, numind 5000 vs 1000."""
    per = Perioada(2026, luna=7)
    with pytest.raises(ReconciliereD301) as ei:
        _d301.genereaza(conn_recon, _SCHEMA, per)
    msg = str(ei.value)
    assert "generator=5000" in msg and "cale2=1000" in msg, msg
    assert "baza1" in msg, msg


# ============================================================
#  4. LIMITA DECLARATA: cursul VALUTA (non-RON) e partajat de ambele cai -> NEACOPERIT, nu alarma.
# ============================================================
@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_limita_curs_valuta_partajat_nu_produce_alarma_falsa(conn_recon):
    """Calea 2 NU are sursa independenta de curs BNR: pentru valuta citeste ACELASI curs stocat ca
    generatorul. Un curs EUR 'gresit' dar >0 (aici 9.99) e folosit identic de ambele cai -> zero
    divergenta (limita 2 declarata). Nu e catch, dar nici alarma falsa."""
    per = Perioada(2026, luna=8)
    with conn_recon.cursor() as cur:
        cur.execute("UPDATE d301_operatiuni SET curs=9.99 WHERE luna=8 AND tip=1")
    xml, res = _d301.genereaza(conn_recon, _SCHEMA, per)
    rap = reconciliaza(conn_recon, per, res)
    assert rap["divergente"] == [], "curs valuta partajat NU trebuie sa produca divergenta: %s" % rap["divergente"]


# [decuplat tura 30] testul 'baseline real BETA (tenant_014)' a fost ELIMINAT: cupla la o firma
# PERSISTENTA (test_teste_decuplate). Reconcilierea-fara-alarma-falsa e probata pe schema efemera
# (testele de mai sus); DUK-valid pe BETA e acoperit de rularea DUK combinata din consolidare.