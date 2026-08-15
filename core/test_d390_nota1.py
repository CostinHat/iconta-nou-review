# -*- coding: utf-8 -*-
"""GARD D390 (16.08.2026, campanie rețeta D300, pas 2/8) — trei remedieri:

(1) NOTA 1 (OPANAF 394/2017 anexa2 instructiuni:189-201): "Pentru achiziţii intracomunitare de bunuri
    taxabile în România, în cazul în care furnizorul nu comunică un cod valabil de TVA, dar bunurile
    sunt transportate de pe teritoriul unui stat membru ... achiziţia se declară: Ţara = statul membru;
    Cod operator = nu se va înscrie nimic; Tipul operaţiunii = A". COD VECHI: calea auto excludea
    partenerul fără cod (n-are câmp de țară), iar calea manuală RESPINGEA tip A (doar P/S/T/R) ->
    operaţiune obligatorie pierdută. FIX: manual_adauga accepta tip A cu cod GOL (A nu e in _CU_COD_OBLIG),
    tara obligatorie; build_xml omite codO gol pentru A -> <operatie tip="A" tara="DE" denO=.. baza=../>
    valid DUK; reconcilierea a-doua-cale include deja latura manuala (orice tip) -> fara divergenta falsa.

(2) DECLARANT FABRICAT TACUT (regula 4): build_xml emitea tacit nume/functie declarant = "ADMINISTRATOR".
    FIX: implicitul ramane (DUK cere campul) DAR e ANUNTAT prin avertisment.

(3) EXIGIBILITATE la ACHIZITII (GAP proba): fereastra art.284 "ziua 15" era probata doar pe livrari
    (emisa). Aici pe directie='primita': factura furnizor emisa tarziu + fapt anterior -> mutata pe
    luna exigibilitatii.

Aserturi/markere ASCII. UE partener DE811569869 (cod valid VIES).
"""
import pytest
from decimal import Decimal

from core import d390
from core.d390 import calcul_d390, build_xml
from core import d390_clasificare_api as _capi


def _prof(**kw):
    p = {"cui": "RO14399840", "nume": "PROBA SRL", "adresa": "Str 1", "oras": "Buc", "judet": "B",
         "declarant_nume": "POPESCU", "declarant_prenume": "ION", "declarant_functie": "ADMINISTRATOR"}
    p.update(kw)
    return p


# ============================================================
#  (2) declarant fabricat -> avertisment (PUR)
# ============================================================
def test_declarant_lipsa_avertisment_nu_tacut():
    """Profil fara declarant -> nume/functie emise implicit 'ADMINISTRATOR' DAR cu avertisment.
    RED pre-fix: 'ADMINISTRATOR' emis tacit."""
    prof = _prof(declarant_nume=None, declarant_prenume=None, declarant_functie=None)
    f = [{"cui": "DE811569869", "nume": "PARTENER DE", "directie": "emisa", "total": 1000, "tva": 0}]
    res = calcul_d390(prof, 2026, 6, f)
    xml = build_xml(res)
    assert 'nume_declar="ADMINISTRATOR"' in xml, "implicitul inca emis (DUK cere campul)"
    assert any("declarantul (nume/functie) lipseste" in a for a in res.avertismente), \
        "implicitul declarant trebuie ANUNTAT"


def test_declarant_prezent_fara_avertisment():
    """CONTROL: profil cu declarant complet -> niciun avertisment de implicit."""
    f = [{"cui": "DE811569869", "nume": "PARTENER DE", "directie": "emisa", "total": 1000, "tva": 0}]
    res = calcul_d390(_prof(), 2026, 6, f)
    build_xml(res)
    assert not any("emis implicit" in a for a in res.avertismente)


# ============================================================
#  DB: NOTA 1 + exigibilitate achizitii
# ============================================================
from core import db as _db, tenant_provisioning as _tp
_SCHEMA = "test_d390_nota1"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def conn():
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(_tp.parametrizeaza_template(
                    open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                cur.execute("SET search_path TO %s, public" % _SCHEMA)
                cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,telefon,"
                            "declarant_nume,declarant_prenume,declarant_functie,platitor_tva,tip_decont) "
                            "VALUES (1,'PROBA SRL','14399840','Str 1','Buc','B','0700000000',"
                            "'POPESCU','ION','ADMINISTRATOR',true,'L')")
            c.commit()
            yield c
        finally:
            c.rollback()


def _tip_A_backend(conn):
    return _capi.manual_adauga(conn, _SCHEMA, 2026, 6, "A", "DE", "", "FURNIZOR DE FARA COD", 5000)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_manual_adauga_accepta_tip_A_nota1(conn):
    """manual_adauga acepta tip A cu COD GOL (NOTA 1). RED pre-fix: tip A respins ('trebuie P/S/T/R')."""
    r = _tip_A_backend(conn)
    assert r.get("ok"), "tip A (NOTA 1) trebuie acceptat pe calea manuala; primit %r" % r


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_manual_adauga_tip_necunoscut_inca_respins(conn):
    """CONTROL: un tip in afara (A,P,S,T,R) ramane respins (nu s-a deschis poarta la orice)."""
    r = _capi.manual_adauga(conn, _SCHEMA, 2026, 6, "X", "DE", "", "Y", 100)
    assert not r.get("ok") and any(e["camp"] == "tip" for e in r.get("erori_campuri", []))


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_manual_adauga_tip_A_cere_tara_UE(conn):
    """NOTA 1 cere Ţara = stat membru UE (cod gol e ok, dar tara nu): tara invalida -> eroare pe camp tara."""
    r = _capi.manual_adauga(conn, _SCHEMA, 2026, 6, "A", "XX", "", "Y", 100)
    assert not r.get("ok") and any(e["camp"] == "tara" for e in r.get("erori_campuri", []))


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_nota1_genereaza_operatie_A_fara_cod(conn):
    """Manual A (NOTA 1, cod gol) -> genereaza emite <operatie tip='A' tara='DE' ... FARA codO>,
    reconcilierea a-doua-cale trece (include latura manuala). RED pre-fix: A neintroductibil."""
    assert _tip_A_backend(conn).get("ok")
    xml, res = d390.genereaza(conn, _SCHEMA, 2026, 6)   # daca reconcilierea da fals-pozitiv -> crapa AICI
    assert '<operatie tip="A" tara="DE"' in xml, "operatiunea A NOTA 1 trebuie emisa"
    # codO absent (nu ' codO=' pe linia operatiunii A)
    op_line = [l for l in xml.splitlines() if '<operatie tip="A"' in l][0]
    assert "codO=" not in op_line, "codO trebuie OMIS pentru A NOTA 1 (nu vid): %r" % op_line
    assert res.rezumat.get("A") == 5000 or res.ops, "baza A in rezumat"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_nota1_duk_valid(conn):
    """Proba DUK: D390 cu operatiune A NOTA 1 (cod gol) e valid la DUKIntegrator."""
    from core import duk
    if not duk.poate_valida("d390"):
        pytest.skip("DUK d390 indisponibil")
    assert _tip_A_backend(conn).get("ok")
    xml, _res = d390.genereaza(conn, _SCHEMA, 2026, 6)
    rez = duk.valideaza(xml, "d390", an=2026, luna=6)
    assert rez["stare"] == "valid", "D390 NOTA 1 trebuie DUK-valid; rez=%r" % rez


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_exigibilitate_achizitie_primita_ziua15(conn):
    """GAP proba: fereastra art.284 'ziua 15' se aplica si ACHIZITIILOR (primita), nu doar livrarilor.
    Factura furnizor PRIMITA emisa tarziu (20 aug) + fapt generator iunie -> deadline 15.07 ->
    exigibilitate IULIE (mutata din august). RED (daca regula ar fi doar pe emisa): ar aparea in august."""
    with conn.cursor() as cur:
        cur.execute("INSERT INTO facturi (numar,data_emitere,data_faptului_generator,directie,tert_cui,"
                    "tert_nume,total,tva) VALUES ('FA','2026-08-20','2026-06-10','primita','DE811569869',"
                    "'FURNIZOR DE',2000,0)")
    conn.commit()
    _p, fact_iul = d390.pull(conn, _SCHEMA, 2026, 7)
    _p, fact_aug = d390.pull(conn, _SCHEMA, 2026, 8)
    tot_iul = [int(round(float(f["total"]))) for f in fact_iul]
    tot_aug = [int(round(float(f["total"]))) for f in fact_aug]
    assert 2000 in tot_iul, "achizitia primita trebuie mutata pe luna exigibilitatii (iulie): %r" % tot_iul
    assert 2000 not in tot_aug, "achizitia NU mai apare in august (luna emiterii): %r" % tot_aug
