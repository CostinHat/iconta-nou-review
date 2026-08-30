# -*- coding: utf-8 -*-
"""
core/test_d300_reconciliere.py — gardul A DOUA CALE D300 (05.08.2026).

Apara:
  - NON-TAUTOLOGIA calea 2 vs generator (probata STATIC + prin constructie).
  - ca reconcilierea PICA pe cele trei clase de bug de agregare (MUTATIE):
    factura pierduta / cota in bucketul gresit / semn inversat.
  - ca pe date corecte NU produce alarma falsa (proba functionala pe schema efemera).
  - limitele declarate: tva_la_incasare si randurile manuale = NEACOPERIT, nu alarma.
"""
import io
import os
import pytest

from core.common import Perioada
from core import d300 as _d300
from core import d300_reconciliere as _rec
from core.d300_reconciliere import reconciliaza, verifica_reconciliere, ReconciliereD300


# ============================================================
#  1. NON-TAUTOLOGIE — probata STATIC: calea 2 nu atinge agregarea generatorului.
# ============================================================
def test_non_tautologie_calea2_nu_importa_agregarea_generatorului():
    """Gardul e valid doar daca cele doua cai NU impart codul de agregare. Probam MECANIC (pe AST,
    nu pe text - ca sa nu se prinda pe propriul docstring) ca modulul caii 2:
      - NU importa modulul core.d300;
      - NU foloseste nicaieri (nume sau atribut) functiile lui de agregare/rotunjire
        calcul_d300 / _segmente / _int / numar_fiscal.
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
    assert "core.d300" not in module_e, "NON-TAUTOLOGIE: calea 2 importa modulul generatorului"
    folosite = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} \
             | {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    for interzis in ("calcul_d300", "_segmente", "_int", "numar_fiscal", "pull"):
        assert interzis not in folosite, "NON-TAUTOLOGIE incalcata: calea 2 foloseste '%s'" % interzis
    # dependentele permise: rotunjirea vine din decimal, autonom fata de calea 1
    assert "decimal" in module_e


# ============================================================
#  Fixtura DB: firma non-tva_la_incasare, 3 facturi cu linii, luna 6.
#  F1 emisa 1000@21% ; F2 emisa 2000@11% ; F3 primita 500@21%.
# ============================================================
from core import db as _db, tenant_provisioning as _tp
_SCHEMA = "test_d300_recon"


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
                    "VALUES (1,'RECON SRL','14399840','Str Test 1','Bucuresti','B','4711','BCR',"
                    "'RO49AAAA1B31007593840000','real',true,'L',false,'Popescu','Ion','ADMINISTRATOR')")
                # F1 emisa 1000 @ 21%
                cur.execute("INSERT INTO facturi (numar, data_emitere, total, tva, directie) "
                            "VALUES ('F1','2026-06-05',1210,210,'emisa') RETURNING id")
                f1 = cur.fetchone()[0]
                cur.execute("INSERT INTO factura_linii (factura_id, descriere, cantitate, pret_unitar, cota_tva) "
                            "VALUES (%s,'marfa',1,1000,21)", (f1,))
                # F2 emisa 2000 @ 11%
                cur.execute("INSERT INTO facturi (numar, data_emitere, total, tva, directie) "
                            "VALUES ('F2','2026-06-10',2220,220,'emisa') RETURNING id")
                f2 = cur.fetchone()[0]
                cur.execute("INSERT INTO factura_linii (factura_id, descriere, cantitate, pret_unitar, cota_tva) "
                            "VALUES (%s,'servicii',1,2000,11)", (f2,))
                # F3 primita 500 @ 21%
                cur.execute("INSERT INTO facturi (numar, data_emitere, total, tva, directie) "
                            "VALUES ('F3','2026-06-12',605,105,'primita') RETURNING id")
                f3 = cur.fetchone()[0]
                cur.execute("INSERT INTO factura_linii (factura_id, descriere, cantitate, pret_unitar, cota_tva) "
                            "VALUES (%s,'consumabile',1,500,21)", (f3,))
            yield conn
        finally:
            conn.rollback()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_reconciliere_curata_pe_date_corecte_si_genereaza_trece(conn_recon):
    """PROBA FUNCTIONALA: pe date corecte, genereaza() (care are POARTA a-doua-cale wired)
    trece, iar reconciliaza() NU raporteaza nicio divergenta."""
    per = Perioada(2026, luna=6)
    xml, res = _d300.genereaza(conn_recon, _SCHEMA, per)   # daca gardul da fals-pozitiv -> AICI crapa
    # calea 1 (generator): valorile asteptate din facturi
    assert (res.R["R9_1"], res.R["R9_2"]) == (1000, 210)     # colectat 21%
    assert (res.R["R10_1"], res.R["R10_2"]) == (2000, 220)   # colectat 11%
    assert (res.R["R22_1"], res.R["R22_2"]) == (500, 105)    # deductibil 21%
    rap = reconciliaza(conn_recon, per, res)
    assert rap["acoperit"] is True
    assert rap["divergente"] == [], "alarma falsa pe date corecte: %s" % rap["divergente"]
    assert "<declaratie300" in xml


# ---- MUTATIE: cele trei clase de bug de agregare -> reconcilierea PICA ----

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_mutatie_factura_pierduta_din_agregare_pica(conn_recon):
    """Generatorul 'pierde' F1 (21%): R9 devine 0. Calea 2 il vede in liniile brute -> divergenta."""
    per = Perioada(2026, luna=6)
    _, res = _d300.genereaza(conn_recon, _SCHEMA, per)
    res.R.pop("R9_1"); res.R.pop("R9_2")     # <- mutatie: factura pierduta
    with pytest.raises(ReconciliereD300) as ei:
        verifica_reconciliere(conn_recon, per, res)
    msg = str(ei.value)
    assert "R9_2" in msg and "generator=0" in msg and "cale2=210" in msg, msg  # numeste AMBELE valori


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_mutatie_cota_in_bucket_gresit_pica(conn_recon):
    """Generatorul pune colectatul 21% pe randul de 11% (R9->R10). Ambele randuri diverg."""
    per = Perioada(2026, luna=6)
    _, res = _d300.genereaza(conn_recon, _SCHEMA, per)
    # mutatie: mut valorile lui R9 (21%) in R10 (11%) - cota in bucketul gresit
    res.R["R10_1"] = res.R["R10_1"] + res.R["R9_1"]
    res.R["R10_2"] = res.R["R10_2"] + res.R["R9_2"]
    res.R.pop("R9_1"); res.R.pop("R9_2")
    with pytest.raises(ReconciliereD300) as ei:
        verifica_reconciliere(conn_recon, per, res)
    msg = str(ei.value)
    assert "R9_2" in msg and "R10_2" in msg, msg   # ambele randuri strig


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_mutatie_semn_inversat_pica(conn_recon):
    """Generatorul inverseaza semnul deductibilului R22. Calea 2 il are pozitiv -> divergenta."""
    per = Perioada(2026, luna=6)
    _, res = _d300.genereaza(conn_recon, _SCHEMA, per)
    res.R["R22_2"] = -res.R["R22_2"]          # <- mutatie: semn inversat
    with pytest.raises(ReconciliereD300) as ei:
        verifica_reconciliere(conn_recon, per, res)
    msg = str(ei.value)
    assert "R22_2" in msg and "generator=-105" in msg and "cale2=105" in msg, msg


# ============================================================
#  Limitele declarate: NEACOPERIT nu inseamna alarma falsa.
# ============================================================
def test_tva_la_incasare_neacoperit_fara_alarma_falsa():
    """Firma pe tva_la_incasare: exigibilitate pe decontari, nu pe emitere. Recalculul pe
    emitere NU se aplica -> acoperit=False, zero divergente. (Nu atinge DB: iese inainte.)"""
    class _R:  # res minim
        prof = {"tva_la_incasare": True}
        R = {"R9_1": 999999}   # valoare aberanta - NU trebuie sa produca divergenta
    rap = reconciliaza(conn=None, perioada=Perioada(2026, luna=6), res=_R())
    assert rap["acoperit"] is False and rap["divergente"] == []
    # [P8] `motiv` (sir) a devenit `neacoperit` (afirmatie cu domeniul ei) - codul si-a schimbat casa
    assert rap["neacoperit"]["fel"] == "necunoastere"
    assert "TVA la încasare" in rap["neacoperit"]["motiv"]
    assert rap["neacoperit"]["domeniu_de"], "necunoasterea nu spune pe ce perioada nu poate"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_rand_atins_manual_e_sarit_nu_alarma(conn_recon):
    """R23 (deductibil 11%) e si manual-settable in generator. Daca vine prin manual=, calea 2
    il SARE (limita 1) - altfel ar alarma fals ca 'generator!=cale2' pe un rand suprascris manual."""
    per = Perioada(2026, luna=6)
    _, res = _d300.genereaza(conn_recon, _SCHEMA, per)
    res.R["R23_2"] = 12345    # valoare 'manuala' care NU corespunde liniilor brute (dedus 11% = 0 aici)
    res.R["R23_1"] = 99999
    rap = reconciliaza(conn_recon, per, res, manual={"R23_1": 99999, "R23_2": 12345})
    assert "R23_2" in rap["sarite"] and "R23_1" in rap["sarite"]
    assert rap["divergente"] == [], "randul manual nu trebuia sa produca divergenta: %s" % rap["divergente"]
