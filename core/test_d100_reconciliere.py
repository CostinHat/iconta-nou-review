# -*- coding: utf-8 -*-
"""core/test_d100_reconciliere.py — gardul A DOUA CALE D100 (pas 4/4 lant reconciliere).

Reconciliaza SURSA -> DECLARATIE: baza impozabila = venituri cont 70x (note validate) x cota
(micro 121 / profit 103), confruntata cu suma_dat a generatorului. Trei probe:
  (a) NON-TAUTOLOGIE: calea 2 NU importa/foloseste d100.calcul_d100/pull.
  (b) ANTI-MORT: injectam o divergenta sursa-vs-declaratie prin ROLLBACK (un venit pe care
      generatorul nu-l are in res) si dovedim ca verifica_reconciliere RIDICA (FIRES).
  (c) BASELINE VALID: micro + profit reconciliaza curat, genereaza (poarta wired) trece.
"""
import io
import ast
import pytest

from core.common import Perioada
from core import d100 as _d100
from core import d100_reconciliere as _rec
from core.d100_reconciliere import reconciliaza, verifica_reconciliere, ReconciliereD100


def test_non_tautologie_calea2_nu_foloseste_generatorul_d100():
    tree = ast.parse(io.open(_rec.__file__, encoding="utf-8").read())
    mods = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom) and n.module:
            mods.add(n.module)
        elif isinstance(n, ast.Import):
            for a in n.names:
                mods.add(a.name)
    assert "core.d100" not in mods, "calea 2 importa generatorul (tautologie)"
    folosite = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} \
             | {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    for interzis in ("calcul_d100", "pull", "_i"):
        assert interzis not in folosite, "calea 2 foloseste '%s' din generator (tautologie)" % interzis


from core import db as _db, tenant_provisioning as _tp
_SCHEMA = "test_d100_recon"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


def _venit(cur, data, suma, cont_credit="707"):
    """Nota de venit validata: cont_credit 70x (venit), cont_debit 4111 (client)."""
    cur.execute("INSERT INTO inregistrari (data, descriere, status) VALUES (%s,'v','validata') RETURNING id", (data,))
    nid = cur.fetchone()[0]
    cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,'4111',%s,%s)",
                (nid, cont_credit, suma))


def _profil(cur, regim):
    cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,platitor_tva,tip_decont,regim_fiscal) "
                "VALUES (1,'TEST SRL','14399840','Str 1','Buc','B','6920',true,'L',%s)", (regim,))


@pytest.fixture
def conn_recon():
    """Schema efemera; regimul se seteaza per-test prin cur (default micro). Rollback la final."""
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                cur.execute("SET search_path TO %s, public" % _SCHEMA)
            yield conn
        finally:
            conn.rollback()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_baseline_micro_reconciliaza_curat_si_genereaza_trece(conn_recon):
    with conn_recon.cursor() as cur:
        _profil(cur, "micro")
        _venit(cur, '2026-08-15', 3000)          # venit 70x in Q3
    xml, res = _d100.genereaza(conn_recon, _SCHEMA, Perioada(2026, trim=3))  # poarta wired -> crapa daca fals-pozitiv
    assert res.obligatii[0].cod_oblig == "121"
    assert res.obligatii[0].suma_dat == 30        # 3000 x 1%
    rap = reconciliaza(conn_recon, Perioada(2026, trim=3), res)
    assert rap["acoperit"] and rap["divergente"] == [], rap
    assert "declaratie100" in xml.lower()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_baseline_profit_reconciliaza_curat(conn_recon):
    with conn_recon.cursor() as cur:
        _profil(cur, "profit")
        _venit(cur, '2026-09-10', 1000)          # venit 70x in Q3
    xml, res = _d100.genereaza(conn_recon, _SCHEMA, Perioada(2026, trim=3))
    assert res.obligatii[0].cod_oblig == "103"
    assert res.obligatii[0].suma_dat == 160       # 1000 x 16%
    rap = reconciliaza(conn_recon, Perioada(2026, trim=3), res)
    assert rap["acoperit"] and rap["divergente"] == [], rap


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_ANTI_MORT_venit_scapat_de_generator_prin_rollback_ridica(conn_recon):
    """Injectam la SURSA (dupa ce res e deja calculat) un venit 70x pe care declaratia nu-l are.
    Calea 2 il recalculeaza din sursa -> baza mai mare -> obligatie mai mare -> RIDICA. Dovada ca
    gardul FIRES pe divergenta sursa-vs-declaratie, nu trece tacut (clasa 'D300 mort'). Rollback."""
    with conn_recon.cursor() as cur:
        _profil(cur, "micro")
        _venit(cur, '2026-08-15', 3000)          # declaratia se cladeste pe 3000 -> suma_dat 30
    xml, res = _d100.genereaza(conn_recon, _SCHEMA, Perioada(2026, trim=3))
    assert res.obligatii[0].suma_dat == 30
    # MUTATIE SURSA (rollback): un venit 70x in aceeasi fereastra, absent din res deja emis.
    with conn_recon.cursor() as cur:
        _venit(cur, '2026-09-20', 5000)          # sursa reala devine 8000 -> cale2 = 80 != 30
    with pytest.raises(ReconciliereD100) as ei:
        verifica_reconciliere(conn_recon, Perioada(2026, trim=3), res)
    msg = str(ei.value)
    assert "generator=30 vs cale2=80" in msg, msg
    assert "cod 121" in msg, msg


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_ANTI_MORT_suma_dat_corupta_ridica(conn_recon):
    """A doua fateta anti-mort: daca suma_dat a generatorului e corupta, calea 2 (baza reala x cota)
    o prinde si numeste ambele valori."""
    with conn_recon.cursor() as cur:
        _profil(cur, "micro")
        _venit(cur, '2026-08-15', 3000)
    xml, res = _d100.genereaza(conn_recon, _SCHEMA, Perioada(2026, trim=3))
    res.obligatii[0].suma_dat = 9999             # mutatie: obligatie gonflata fata de sursa
    with pytest.raises(ReconciliereD100) as ei:
        verifica_reconciliere(conn_recon, Perioada(2026, trim=3), res)
    assert "generator=9999 vs cale2=30" in str(ei.value), str(ei.value)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_regim_in_afara_scopului_e_neacoperit_nu_alarma_falsa(conn_recon):
    """Regim in afara micro/profit -> acoperit=False (limita 3), NU divergenta falsa."""
    with conn_recon.cursor() as cur:
        _profil(cur, "real")                     # nici micro nici profit
        _venit(cur, '2026-08-15', 3000)
    # construim un res minimal fara a trece prin genereaza (care ar refuza regim necunoscut la 70x)
    res = _d100.RezultatD100(an=2026, luna=9, prof={"regim_fiscal": "real"}, obligatii=[], total_plata_a=0)
    rap = reconciliaza(conn_recon, Perioada(2026, trim=3), res)
    assert rap["acoperit"] is False and rap["divergente"] == [], rap
