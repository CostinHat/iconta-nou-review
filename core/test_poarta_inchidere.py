# -*- coding: utf-8 -*-
"""GARDA porții de închidere a perioadei — R58, partea care lipsea.

DE CE EXISTĂ. Condiția de deblocare a lui R58 spunea, cu vorbele ei: *„Ce NU e păzit încă, și se
spune: nu există un test care să asertez că poarta refuză — azi e o probă funcțională, nu un
clichet."* Reparația fusese construită pe 26.08 și probată **o dată**, pe o schemă efemeră. O
reparație probată o dată nu e o reparație păzită: o revenire la `INSERT`-ul de dinainte n-ar fi picat
nimic.

CE FACE IMPOSIBIL:
  * ca poarta să închidă o lună care are **note** rămase în ciornă;
  * ca poarta să închidă o lună care are **facturi** neîncheiate — `ciorna` sau `de_recunoscut`
    (starea de la R91). *Clasa asta n-avea cum să fie acoperită de verificarea din 26.08: a doua
    stare a apărut azi;*
  * ca refuzul să fie o eroare brută în loc de o afirmație tipată care **numește ce blochează**;
  * ca redeschiderea să se producă fără motiv;
  * ca ea să nu lase urmă.

CALIBRAREA E ÎN AMBELE DIRECȚII (METODA §22): o lună **curată** se închide. Fără direcția asta, o
poartă care ar refuza întotdeauna ar trece toate testele de mai sus și ar bloca munca zilnică.
"""
import io

import pytest
from fastapi import HTTPException

import main
from core import db as _db
from core import tenant_provisioning as _tp

_SCH = "efemer_poarta_inchidere"
_CTX = {"uid": 7, "rol": "admin_firma"}


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


_DB = _db_ok()
pytestmark = pytest.mark.skipif(not _DB, reason="DB indisponibil")


@pytest.fixture()
def conn(monkeypatch):
    _db.init_pool()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
            cur.execute(_tp.parametrizeaza_template(
                io.open("tenant_template.sql", encoding="utf-8").read(), _SCH))
            cur.execute("SET search_path TO %s, public" % _SCH)
            cur.execute("""INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, email,
                           telefon, caen, declarant_nume, declarant_prenume, declarant_functie,
                           platitor_tva)
                           VALUES (1,'POARTA SRL','RO14399840','Str 1','Buc','B','e@x.ro','0722',
                                   '4690','P','I','ADMIN', true)""")
        c.commit()
    monkeypatch.setattr(main.auth_api, "schema_tenant", lambda c, uid, tid: _SCH)
    monkeypatch.setattr(main.auth_api, "schema_tenant_citire", lambda c, uid, tid: _SCH)
    with _db.get_conn(_SCH) as c:
        yield c
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
        c.commit()


def _nota(conn, status="ciorna", data="2026-06-10"):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO inregistrari (data, descriere, sursa, status) "
                    "VALUES (%s,'x','manual',%s) RETURNING id", (data, status))
        nid = cur.fetchone()[0]
        cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma)"
                    " VALUES (%s,'6021','401',100)", (nid,))
    conn.commit()
    return nid


def _factura(conn, status, data="2026-06-10"):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO facturi (numar, data_emitere, directie, status, total, tva) "
                    "VALUES ('P1',%s,'emisa',%s,1210,210) RETURNING id", (data, status))
        fid = cur.fetchone()[0]
    conn.commit()
    return fid


def _inchide():
    return main.perioada_blocheaza(1, 2026, 6, _CTX)


def _blocata(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM perioade_blocate WHERE an=2026 AND luna=6")
        return cur.fetchone()[0] == 1


# ═══════════════════════════════════════════════ poarta REFUZĂ
def test_o_luna_cu_nota_in_ciorna_nu_se_inchide(conn):
    _nota(conn)
    with pytest.raises(HTTPException) as e:
        _inchide()
    assert e.value.status_code == 422
    assert e.value.detail["cod"] == "PERIOADA_NU_SE_POATE_INCHIDE"
    assert e.value.detail["ciorne"] == 1
    assert not _blocata(conn), "perioada s-a închis deși refuzul s-a produs"


def test_o_luna_cu_factura_in_CIORNA_nu_se_inchide(conn):
    """Clasa adăugată azi (PPP1): poarta vedea doar notele."""
    _factura(conn, "ciorna")
    with pytest.raises(HTTPException) as e:
        _inchide()
    assert e.value.detail["facturi"] == 1
    assert e.value.detail["ciorne"] == 0, "e o factură, nu o notă — refuzul spune care"
    assert not _blocata(conn)


def test_o_luna_cu_factura_DE_RECUNOSCUT_nu_se_inchide(conn):
    """Starea introdusă azi la R91. După închidere, `recunoaste` ar refuza pe lună închisă, deci
    documentul ar rămâne pe veci fără evidență — exact pierderea pe care o apără poarta."""
    _factura(conn, "de_recunoscut")
    with pytest.raises(HTTPException) as e:
        _inchide()
    assert e.value.detail["facturi"] == 1
    assert not _blocata(conn)


def test_refuzul_e_o_afirmatie_TIPATA_care_numeste_ce_blocheaza(conn):
    """Nu o eroare brută: `fel` din nomenclator, cu `unde` și `regula`, plus motivele una câte una."""
    _nota(conn)
    _factura(conn, "de_recunoscut")
    with pytest.raises(HTTPException) as e:
        _inchide()
    d = e.value.detail
    assert d["fel"] == "neconformitate"
    assert d["tip"] == "inchidere_perioada"
    assert d["unde"] and d["regula"] and d["motiv"]
    assert len(d["motive"]) == 2, "fiecare cauză își are rândul ei, nu una singură care le adună"


# ═══════════════════════════════════════════════ CALIBRARE: o lună curată se închide
def test_o_luna_CURATA_se_inchide(conn):
    """Direcția inversă, fără de care o poartă care refuză mereu ar trece tot ce e mai sus."""
    _nota(conn, status="validata")
    _factura(conn, "emisa")
    assert _inchide() == {"blocat": "06/2026"}
    assert _blocata(conn)


def test_o_nota_din_ALTA_luna_nu_blocheaza(conn):
    """Domeniul e luna cerută, nu toată evidența."""
    _nota(conn, data="2026-05-10")
    _factura(conn, "de_recunoscut", data="2026-07-10")
    assert _inchide() == {"blocat": "06/2026"}


# ═══════════════════════════════════════════════ redeschiderea: motiv + urmă
def test_redeschiderea_fara_motiv_se_refuza(conn):
    _nota(conn, status="validata")
    _inchide()
    with pytest.raises(HTTPException) as e:
        main.perioada_deblocheaza(1, 2026, 6, "", _CTX)
    assert e.value.status_code == 422
    assert e.value.detail["cod"] == "REDESCHIDERE_FARA_MOTIV"
    assert _blocata(conn), "perioada rămâne închisă când redeschiderea e refuzată"


def test_redeschiderea_cu_motiv_lasa_URMA_cu_cele_doua_acte(conn):
    _nota(conn, status="validata")
    _inchide()
    main.perioada_deblocheaza(1, 2026, 6, "corecție cerută de client", _CTX)
    assert not _blocata(conn)
    ist = main.perioade_istoric(1, 2026, 6, _CTX)["istoric"]
    assert [x["actiune"] for x in ist] == ["inchisa", "redeschisa"], ist
    assert ist[1]["motiv"] == "corecție cerută de client"
    assert ist[1]["cine_id"] == 7 and ist[1]["cand"]


def test_dupa_redeschidere_luna_se_poate_inchide_din_nou(conn):
    """Urma se adaugă, nu se rescrie: a doua închidere e un al treilea act, nu o suprascriere."""
    _nota(conn, status="validata")
    _inchide()
    main.perioada_deblocheaza(1, 2026, 6, "motiv", _CTX)
    _inchide()
    ist = main.perioade_istoric(1, 2026, 6, _CTX)["istoric"]
    assert [x["actiune"] for x in ist] == ["inchisa", "redeschisa", "inchisa"], ist


# ═══════════════════════════════════════════════ ANTI-VACUU pe fixtură
def test_fixtura_chiar_produce_starile_pe_care_le_masoara(conn):
    """Fără el, o fixtură care n-ar insera nimic ar face „0 ciorne" adevărat și toate refuzurile de
    mai sus ar fi despre o lume goală."""
    _nota(conn)
    _factura(conn, "de_recunoscut")
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM inregistrari WHERE status='ciorna'")
        assert cur.fetchone()[0] == 1
        cur.execute("SELECT COUNT(*) FROM facturi WHERE status='de_recunoscut'")
        assert cur.fetchone()[0] == 1
