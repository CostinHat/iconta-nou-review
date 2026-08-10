# -*- coding: utf-8 -*-
"""
core/test_d390_reconciliere.py — gardul A DOUA CALE D390 (10.08.2026).

Apara:
  - NON-TAUTOLOGIA caii 2 vs generator (probata STATIC pe AST: nu importa core.d390, nu-i
    foloseste agregarea/rotunjirea).
  - ANTI-MORT: reconcilierea PICA pe divergenta reala sursa<->declaratie (aggregation-loss):
    (a) o factura IC scapata din sursa (DELETE in tranzactie + ROLLBACK) fata de declaratia
        deja generata; (b) generatorul pierde o operatiune din rezumat.
  - ca pe date corecte NU produce alarma falsa (schema efemera + baseline ALFA/DELTA reale).
  - DUK-valid pe baseline (ALFA/DELTA), poarta wired in genereaza nu strica emiterea.
"""
import io
import pytest

from core import d390 as _d390
from core import d390_reconciliere as _rec
from core.d390_reconciliere import reconciliaza, verifica_reconciliere, ReconciliereD390


# ============================================================
#  1. NON-TAUTOLOGIE — probata STATIC: calea 2 nu atinge agregarea generatorului.
# ============================================================
def test_non_tautologie_calea2_nu_importa_agregarea_generatorului():
    """Gardul e valid doar daca cele doua cai NU impart codul de agregare. Probam MECANIC (pe AST,
    nu pe text - ca sa nu se prinda pe propriul docstring):
      - NU importa modulul core.d390;
      - NU foloseste nicaieri (nume/atribut) functiile de agregare/rotunjire ale generatorului
        (calcul_d390 / _facturi_ic / operatiuni_auto / _int / numar_fiscal / pull)."""
    import ast
    tree = ast.parse(io.open(_rec.__file__, encoding="utf-8").read())
    module_e = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom) and n.module:
            module_e.add(n.module)
        elif isinstance(n, ast.Import):
            for a in n.names:
                module_e.add(a.name)
    assert "core.d390" not in module_e, "NON-TAUTOLOGIE: calea 2 importa modulul generatorului"
    folosite = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} \
             | {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    for interzis in ("calcul_d390", "_facturi_ic", "operatiuni_auto", "_int", "numar_fiscal", "pull"):
        assert interzis not in folosite, "NON-TAUTOLOGIE incalcata: calea 2 foloseste '%s'" % interzis
    # rotunjirea vine din decimal (autonom fata de core.numere/d390)
    assert "decimal" in module_e


# ============================================================
#  Fixtura DB: firma platitoare, lunar, luna 8. Facturi IC:
#    F1 emisa DE (baza 2000 -> L) ; F2 primita FR (baza 1500 -> A) ; F3 emisa RO (domestic, EXCLUS).
# ============================================================
from core import db as _db, tenant_provisioning as _tp
_SCHEMA = "test_d390_recon"


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
                    "regim_fiscal, platitor_tva, tip_decont, tva_la_incasare) "
                    "VALUES (1,'RECON390 SRL','14399840','Str Test 1','Bucuresti','B','4711','BCR',"
                    "'RO49AAAA1B31007593840000','real',true,'L',false)")
                # F1 emisa DE, IC livrare (reverse charge -> tva 0), baza 2000 -> L
                cur.execute("INSERT INTO facturi (numar, data_emitere, total, tva, directie, tert_nume, tert_cui) "
                            "VALUES ('F1','2026-08-05',2000,0,'emisa','ALPHA GMBH','DE136695976') RETURNING id")
                # F2 primita FR, IC achizitie, baza 1500 -> A
                cur.execute("INSERT INTO facturi (numar, data_emitere, total, tva, directie, tert_nume, tert_cui) "
                            "VALUES ('F2','2026-08-10',1500,0,'primita','BETA SARL','FR40303265045') RETURNING id")
                # F3 emisa RO domestic -> EXCLUS din D390 (nu e IC)
                cur.execute("INSERT INTO facturi (numar, data_emitere, total, tva, directie, tert_nume, tert_cui) "
                            "VALUES ('F3','2026-08-12',5000,950,'emisa','GAMA SRL','RO14399840')")
            yield conn
        finally:
            conn.rollback()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_reconciliere_curata_pe_date_corecte_si_genereaza_trece(conn_recon):
    """PROBA FUNCTIONALA: pe date corecte genereaza() (cu poarta a-doua-cale wired) trece, iar
    reconciliaza() NU raporteaza nicio divergenta (partenerul RO e exclus corect din ambele cai)."""
    xml, res = _d390.genereaza(conn_recon, _SCHEMA, 2026, 8)   # daca gardul da fals-pozitiv -> AICI crapa
    assert res.rezumat["L"] == 2000 and res.rezumat["A"] == 1500
    assert res.nr_opi == 2
    rap = reconciliaza(conn_recon, _SCHEMA, 2026, 8, res)
    assert rap["acoperit"] is True
    assert rap["divergente"] == [], "alarma falsa pe date corecte: %s" % rap["divergente"]
    assert "<declaratie390" in xml


# ---- ANTI-MORT (MUTATIE): divergenta reala sursa<->declaratie -> reconcilierea PICA ----

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_mutatie_sursa_pierde_factura_pica_via_rollback(conn_recon):
    """Declaratia se genereaza cu F1 (DE, L=2000). Apoi F1 dispare din SURSA (DELETE in tranzactie,
    anulat de ROLLBACK-ul fixturii). Recalculul independent vede L=0, dar declaratia inca declara
    2000 -> divergenta sursa<->declaratie -> RAISE care numeste AMBELE valori."""
    _, res = _d390.genereaza(conn_recon, _SCHEMA, 2026, 8)
    with conn_recon.cursor() as cur:
        cur.execute("DELETE FROM %s.facturi WHERE numar = 'F1'" % _SCHEMA)   # <- IC dropped from source
    with pytest.raises(ReconciliereD390) as ei:
        verifica_reconciliere(conn_recon, _SCHEMA, 2026, 8, res)
    msg = str(ei.value)
    assert "bazaL" in msg and "generator=2000" in msg and "cale2=0" in msg, msg
    assert "nrOPI" in msg   # operatiunea pierduta apare si in numarul de operatiuni


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_mutatie_generator_pierde_operatiune_din_rezumat_pica(conn_recon):
    """Generatorul 'pierde' achizitia FR (A) din rezumat (nr_opi decrementat). Calea 2 o vede in
    facturi -> divergenta pe bazaA + nrOPI + totaluri, cu AMBELE valori numite."""
    _, res = _d390.genereaza(conn_recon, _SCHEMA, 2026, 8)
    res.rezumat["A"] = 0                 # <- mutatie: operatiune pierduta din agregare
    res.nr_opi -= 1
    res.total_baza -= 1500
    res.total_plata_a -= 1501
    with pytest.raises(ReconciliereD390) as ei:
        verifica_reconciliere(conn_recon, _SCHEMA, 2026, 8, res)
    msg = str(ei.value)
    assert "bazaA" in msg and "generator=0" in msg and "cale2=1500" in msg, msg


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_mutatie_baza_pe_tip_gresit_pica(conn_recon):
    """Generatorul muta baza livrarii de pe L pe T (triangulatie) - bucket gresit. Ambele tipuri
    diverg fata de recalculul independent (care are L=2000, T=0)."""
    _, res = _d390.genereaza(conn_recon, _SCHEMA, 2026, 8)
    res.rezumat["T"] = res.rezumat["L"]
    res.rezumat["L"] = 0                 # <- mutatie: baza pe tip gresit (L->T)
    with pytest.raises(ReconciliereD390) as ei:
        verifica_reconciliere(conn_recon, _SCHEMA, 2026, 8, res)
    msg = str(ei.value)
    assert "bazaL" in msg and "bazaT" in msg, msg


# ============================================================
#  BASELINE real: ALFA (tenant_013) / DELTA (tenant_016) reconciliaza + DUK-valid.
# ============================================================
_BASELINE = [("tenant_013", 2026, 8), ("tenant_016", 2026, 8)]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
@pytest.mark.parametrize("schema,an,luna", _BASELINE)
def test_baseline_reconciliaza_curat_si_duk_valid(schema, an, luna):
    """Pe firmele reale (4163) declaratia se genereaza (poarta a-doua-cale trece), reconciliaza
    fara divergente, si e DUK-valida."""
    from core import duk
    with _db.get_conn(schema) as conn:
        xml, res = _d390.genereaza(conn, schema, an, luna)
        rap = reconciliaza(conn, schema, an, luna, res)
        assert rap["divergente"] == [], "%s: divergente pe baseline: %s" % (schema, rap["divergente"])
        v = duk.valideaza(xml, "d390", an=an, luna=luna, timeout=110)
        assert v.get("stare") == "valid", "%s: DUK nu e valid: %s" % (schema, v)
