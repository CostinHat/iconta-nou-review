# -*- coding: utf-8 -*-
"""
core/test_d394_reconciliere.py — gardul A DOUA CALE D394 (05.08.2026, campanie pas 2/6).

Acelasi tipar ca D300. Apara:
  - NON-TAUTOLOGIA caii 2 (probata pe AST: nu foloseste agregarea generatorului d394).
  - ca reconcilierea PICA pe clasele de bug de agregare (MUTATIE): livrare pierduta /
    livrare clasificata la achizitii / semn inversat.
  - ca pe date corecte NU produce alarma falsa (proba functionala pe schema efemera).
  - limita: operatiunile manuale = NEACOPERIT, nu alarma.
"""
import io
import pytest

from core.common import Perioada
from core import d394 as _d394
from core import d394_reconciliere as _rec
from core.d394_reconciliere import reconciliaza, verifica_reconciliere, ReconciliereD394


# ============================================================
#  1. NON-TAUTOLOGIE — pe AST: calea 2 nu atinge agregarea generatorului d394.
# ============================================================
def test_non_tautologie_calea2_nu_importa_agregarea_d394():
    import ast
    tree = ast.parse(io.open(_rec.__file__, encoding="utf-8").read())
    module_e = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom) and n.module:
            module_e.add(n.module)
        elif isinstance(n, ast.Import):
            for a in n.names:
                module_e.add(a.name)
    assert "core.d394" not in module_e, "NON-TAUTOLOGIE: calea 2 importa generatorul d394"
    folosite = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} \
             | {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    for interzis in ("calcul_d394", "_int", "pull"):
        assert interzis not in folosite, "NON-TAUTOLOGIE incalcata: calea 2 foloseste '%s'" % interzis


# ============================================================
#  Fixtura DB: firma RO. F1 emisa 1000@21% + F2 emisa 500@11% (livrari L);
#  F3 primita 800@21% de la furnizor RO platitor (achizitie A).
# ============================================================
from core import db as _db, tenant_provisioning as _tp
_SCHEMA = "test_d394_recon"


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
                cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,"
                            "telefon,platitor_tva,tip_decont,declarant_nume,declarant_prenume,declarant_functie) VALUES (1,'PROBA SRL','14399840','Str 1','Buc',"
                            "'B','6202','BCR','RO49RNCB0000000000000001','0700000000',true,'L','Popescu','Ion','ADMINISTRATOR')")
                # F1 emisa 1000 @ 21% (livrare)
                cur.execute("INSERT INTO facturi (numar,data_emitere,directie,tert_cui,tert_nume,total,tva,"
                            "taxare_inversa) VALUES ('F1','2026-06-05','emisa','RO14399840','CLIENT',1210,210,false) RETURNING id")
                f1 = cur.fetchone()[0]
                cur.execute("INSERT INTO factura_linii (factura_id,descriere,um,cantitate,pret_unitar,cota_tva) "
                            "VALUES (%s,'marfa','buc',1,1000,21)", (f1,))
                # F2 emisa 500 @ 11% (livrare)
                cur.execute("INSERT INTO facturi (numar,data_emitere,directie,tert_cui,tert_nume,total,tva,"
                            "taxare_inversa) VALUES ('F2','2026-06-07','emisa','RO14399840','CLIENT',555,55,false) RETURNING id")
                f2 = cur.fetchone()[0]
                cur.execute("INSERT INTO factura_linii (factura_id,descriere,um,cantitate,pret_unitar,cota_tva) "
                            "VALUES (%s,'servicii','buc',1,500,11)", (f2,))
                # F3 primita 800 @ 21% de la furnizor RO platitor (achizitie)
                cur.execute("INSERT INTO facturi (numar,data_emitere,directie,tert_cui,tert_nume,tert_platitor_tva,"
                            "total,tva,taxare_inversa) VALUES ('F3','2026-06-09','primita','RO14399840','FURNIZOR',true,968,168,false) RETURNING id")
                f3 = cur.fetchone()[0]
                cur.execute("INSERT INTO factura_linii (factura_id,descriere,um,cantitate,pret_unitar,cota_tva) "
                            "VALUES (%s,'consumabile','buc',1,800,21)", (f3,))
            yield conn
        finally:
            conn.rollback()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_reconciliere_curata_si_genereaza_trece(conn_recon):
    """PROBA FUNCTIONALA: pe date corecte, genereaza() (cu POARTA a-doua-cale wired) trece,
    iar reconciliaza() NU raporteaza divergente."""
    per = Perioada(2026, luna=6)
    xml, res = _d394.genereaza(conn_recon, _SCHEMA, per)   # daca gardul da fals-pozitiv -> AICI crapa
    assert (res.rezumat2[21]["bazaL"], res.rezumat2[21]["tvaL"]) == (1000, 210)
    assert (res.rezumat2[21]["bazaA"], res.rezumat2[21]["tvaA"]) == (800, 168)
    assert (res.rezumat2[11]["bazaL"], res.rezumat2[11]["tvaL"]) == (500, 55)
    rap = reconciliaza(conn_recon, per, res)
    assert rap["acoperit"] is True
    assert rap["divergente"] == [], "alarma falsa pe date corecte: %s" % rap["divergente"]
    assert "declaratie394" in xml


# ---- MUTATIE: clasele de bug de agregare -> reconcilierea PICA ----

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_mutatie_livrare_pierduta_pica(conn_recon):
    """Generatorul 'pierde' livrarea 21% (bazaL/tvaL -> 0). Calea 2 o vede in liniile brute."""
    per = Perioada(2026, luna=6)
    _, res = _d394.genereaza(conn_recon, _SCHEMA, per)
    res.rezumat2[21]["bazaL"] = 0; res.rezumat2[21]["tvaL"] = 0   # <- mutatie
    with pytest.raises(ReconciliereD394) as ei:
        verifica_reconciliere(conn_recon, per, res)
    msg = str(ei.value)
    assert "cota 21% tvaL" in msg and "generator=0" in msg and "cale2=210" in msg, msg


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_mutatie_livrare_clasificata_la_achizitii_pica(conn_recon):
    """Generatorul pune livrarea 21% pe achizitii (L->A). Ambele campuri diverg."""
    per = Perioada(2026, luna=6)
    _, res = _d394.genereaza(conn_recon, _SCHEMA, per)
    res.rezumat2[21]["bazaA"] += res.rezumat2[21]["bazaL"]
    res.rezumat2[21]["tvaA"] += res.rezumat2[21]["tvaL"]
    res.rezumat2[21]["bazaL"] = 0; res.rezumat2[21]["tvaL"] = 0
    with pytest.raises(ReconciliereD394) as ei:
        verifica_reconciliere(conn_recon, per, res)
    msg = str(ei.value)
    assert "tvaL" in msg and "tvaA" in msg, msg


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_mutatie_semn_inversat_pica(conn_recon):
    """Generatorul inverseaza semnul TVA achizitii. Calea 2 il are pozitiv."""
    per = Perioada(2026, luna=6)
    _, res = _d394.genereaza(conn_recon, _SCHEMA, per)
    res.rezumat2[21]["tvaA"] = -res.rezumat2[21]["tvaA"]   # <- mutatie
    with pytest.raises(ReconciliereD394) as ei:
        verifica_reconciliere(conn_recon, per, res)
    msg = str(ei.value)
    assert "cota 21% tvaA" in msg and "generator=-168" in msg and "cale2=168" in msg, msg


# ============================================================
#  Limita: operatiunile manuale = NEACOPERIT (nu alarma falsa).
# ============================================================
@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_operatiuni_manuale_neacoperit_fara_alarma(conn_recon):
    """manual['operatiuni'] nevid -> calea 2 nu poate reconstrui din facturi -> NEACOPERIT,
    zero divergente (chiar daca rezumat2 e mutat aberant)."""
    per = Perioada(2026, luna=6)
    _, res = _d394.genereaza(conn_recon, _SCHEMA, per)
    res.rezumat2[21]["tvaL"] = 999999   # valoare aberanta care NU trebuie sa alarmeze
    rap = reconciliaza(conn_recon, per, res,
                       manual={"operatiuni": [{"tip": "AI", "cota": 21, "baza": 100, "tva": 21}]})
    assert rap["acoperit"] is False and rap["divergente"] == []
    assert rap["neacoperit"]["fel"] == "necunoastere"
    assert "manual" in rap["neacoperit"]["motiv"]
    assert rap["neacoperit"]["domeniu_de"], "necunoasterea nu spune pe ce perioada nu poate"
