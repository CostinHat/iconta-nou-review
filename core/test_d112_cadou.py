# -*- coding: utf-8 -*-
"""GARD D112 (16.08.2026, campanie rețeta D300, pas 4/8) — CADOU TAXABIL -> D112 (pierdere tacuta reparata).

CF art.76(4)a (impozit) + art.142 (contributii): cadourile sunt neimpozabile "in masura in care ... nu
depaseste 300 lei" DOAR pentru evenimentele legale (Paste/Craciun/8 martie/1 iunie); excedentul peste 300
(eveniment legal) sau valoarea INTEGRALA (eveniment nelegal) = venit salarial (CAS+CASS+CAM+impozit).

COD VECHI: beneficii_api.cadou_detalii_luna calcula flag-ul 'taxabil', DAR d112.pull() NU tragea cadou
(doar vacanta/cultural/cresa) -> cadou taxabil NU ajungea niciodata in D112 (comentariu d112.py "Cadou
neinclus"). Venit salarial impozabil pierdut tacit.

FIX: cadou_taxabil_luna(suma taxabila per salariat) -> calcul_salariu(cadou_taxabil) -> b_imp (venit salarial
complet, ca exces_vac) -> CAS/CASS/CAM/impozit; emis in E3_73. Reconcilierea NU e afectata (sare angajatii cu
intrari beneficii_lunare via ben_ids).

Aserturi/markere ASCII.
"""
import pytest
from core import beneficii_api as _ben
from core import d112


# ============================================================
#  DB fixture
# ============================================================
from core import db as _db, tenant_provisioning as _tp
_SCHEMA = "test_d112_cadou"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


def _setup(cur, cadouri=()):
    """cadouri: [(eveniment, valoare)] pt salariatul 1."""
    cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
    cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
    cur.execute("SET search_path TO %s, public" % _SCHEMA)
    cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,regim_fiscal,"
                "platitor_tva,tip_decont,declarant_nume,declarant_prenume,declarant_functie) VALUES "
                "(1,'PROBA D112 SRL','14399840','Str 1','Buc','B','6202','BCR','RO49RNCB0000000000000001',"
                "'profit',true,'L','Pop','Ion','administrator')")
    cur.execute("INSERT INTO salariati (cnp,nume,prenume,data_angajare,salariu_brut,ore_zi,judet_casa) "
                "VALUES ('1900101410011','P','I','2024-01-01',5000,8,'B') RETURNING id")
    sid = cur.fetchone()[0]
    for ev, val in cadouri:
        cur.execute("INSERT INTO beneficii_lunare (salariat_id,an,luna,tip,valoare,eveniment) "
                    "VALUES (%s,2026,6,'cadou',%s,%s)", (sid, val, ev))
    return sid


@pytest.fixture
def conn():
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            yield c
        finally:
            c.rollback()


# ============================================================
#  suma taxabila (CF art.76(4)a)
# ============================================================
@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_cadou_taxabil_eveniment_legal_doar_excedentul(conn):
    """Eveniment LEGAL (craciun) 500 lei -> taxabil = 200 (excedent peste 300). 250 -> 0."""
    with conn.cursor() as cur:
        sid = _setup(cur, [("craciun", 500)])
    conn.commit()
    tax = _ben.cadou_taxabil_luna(conn, _SCHEMA, 2026, 6)
    assert tax.get(sid) == 200.0, "excedent 500-300=200; gasit %r" % tax


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_cadou_taxabil_eveniment_legal_sub_plafon_zero(conn):
    """Eveniment LEGAL (paste) 250 lei (<=300) -> neimpozabil, taxabil = 0 (absent din dict)."""
    with conn.cursor() as cur:
        _setup(cur, [("paste", 250)])
    conn.commit()
    assert _ben.cadou_taxabil_luna(conn, _SCHEMA, 2026, 6) == {}, "sub plafon -> nimic taxabil"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_cadou_taxabil_eveniment_nelegal_integral(conn):
    """Eveniment NELEGAL ('altul') 400 lei -> taxabil INTEGRAL = 400 (plafonul 300 e doar pt ocaziile legale)."""
    with conn.cursor() as cur:
        sid = _setup(cur, [("altul", 400)])
    conn.commit()
    assert _ben.cadou_taxabil_luna(conn, _SCHEMA, 2026, 6).get(sid) == 400.0


# ============================================================
#  D112: cadou taxabil in brut + E3_73 + DUK
# ============================================================
@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_cadou_taxabil_ajunge_in_d112_E3_73(conn):
    """Salariat cu cadou nelegal 400 -> D112 emite E3_73="400" (partea taxabila).
    RED pre-fix: d112.pull nu tragea cadou -> E3_73 absent, venit pierdut tacit."""
    with conn.cursor() as cur:
        _setup(cur, [("altul", 400)])
    conn.commit()
    xml, _res = d112.genereaza(conn, _SCHEMA, 2026, 6)
    assert 'E3_73="400"' in xml, "cadou taxabil 400 trebuie emis in E3_73; XML nu-l contine"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_fara_cadou_niciun_E3_73(conn):
    """CONTROL: salariat FARA cadou -> niciun E3_73 (comportament neschimbat)."""
    with conn.cursor() as cur:
        _setup(cur, [])
    conn.commit()
    xml, _res = d112.genereaza(conn, _SCHEMA, 2026, 6)
    assert "E3_73=" not in xml, "fara cadou nu se emite E3_73"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_cadou_creste_brutul_declarat(conn):
    """Cadou taxabil intra in BRUTUL DECLARAT (B1_sal1) - venit salarial, consistent cu contributiile
    (altfel DUK S74 respinge). Brut cu cadou 400 = brut fara cadou + 400."""
    import re
    with conn.cursor() as cur:
        _setup(cur, [])
    conn.commit()
    x0, _ = d112.genereaza(conn, _SCHEMA, 2026, 6)
    with conn.cursor() as cur:
        _setup(cur, [("altul", 400)])
    conn.commit()
    x1, _ = d112.genereaza(conn, _SCHEMA, 2026, 6)
    b0 = int(re.search(r'B1_sal1="(\d+)"', x0).group(1))
    b1 = int(re.search(r'B1_sal1="(\d+)"', x1).group(1))
    assert b1 == b0 + 400, "brutul declarat B1_sal1 trebuie sa creasca cu cadoul taxabil (400): %d vs %d" % (b1, b0)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_cadou_d112_ramane_duk_valid(conn):
    """Proba DUK: D112 cu cadou taxabil (brut majorat + E3_73) e valid la DUKIntegrator."""
    from core import duk
    if not duk.poate_valida("d112"):
        pytest.skip("DUK d112 indisponibil")
    with conn.cursor() as cur:
        _setup(cur, [("altul", 400)])
    conn.commit()
    xml, _res = d112.genereaza(conn, _SCHEMA, 2026, 6)
    rez = duk.valideaza(xml, "d112", an=2026, luna=6)
    assert rez["stare"] == "valid", "D112 cu cadou trebuie DUK-valid; rez=%r" % rez
