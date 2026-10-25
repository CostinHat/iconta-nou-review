# -*- coding: utf-8 -*-
"""Lotul 12, comanda Costin 12.2 pct.1 (verbatim în DECIZII „Comanda 12.2”), pachetul stoc2 — deficiența 409.1:
„F1, 05.10: cinci note 607=371 (8 +100; 30 și 32 stornări ale lui 8; 31 și 33 ieșiri pe Factura 2). Net corect, dar nota 8 e stornată de
două ori, ieșirea e dublată, titlul notei 30 e stricat. Cerut: o stornare, o ieșire, titlu corect.”

Notele 30–33 n-au mișcare de stoc și n-au autor: sunt reparația 409 rulată de două ori pe datele F1 (publicarea lotului 9 și a lotului 10),
nu un drum al aplicației — în aplicație o mișcare de stoc se stornează o singură dată (`miscari_stoc_anuleaza_uq`, `refuza_dublura` în
`stocuri_cv_api.retur_la_stornare` / `stocuri_anulare.storneaza`), iar titlurile stornărilor nu se compun peste un titlu de stornare
(casa refuză stornarea unei stornări, borderoul și factura la fel). Datele existente: `scripts/stoc2_409_1_dubluri_corectie.py`, numai cu
aprobarea lui Costin. Testul reface starea F1 pe o schemă efemeră (date din 2099) și o repară; ROLLBACK la final.
Temei: OMFP 1802/2014 pct.69 (stornarea „prin corectarea cu semnul minus a operațiunii inițiale”) — o operațiune se stornează o dată."""
import importlib.util
import io
import os
from decimal import Decimal as D

import pytest

from core import db as _db
from core import tenant_provisioning as _tp

SCH = "efemer_l12_stoc2_409"
ZI = "2099-10-05"
RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:  # noqa: BLE001
        return False


@pytest.fixture()
def tx():
    if not _db_ok():
        pytest.skip("DB indisponibil")
    p = _db.pool()
    conn = p.getconn()
    cur = conn.cursor()
    cur.execute("RESET iconta.utilizator")   # notele reparației vechi n-au autor
    cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
    cur.execute(_tp.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), SCH))
    # CUI 14399840 (DANTE INTERNATIONAL SA) — cifra de control verificată
    cur.execute("INSERT INTO %s.firma_profil (id, nume, cui, metoda_stoc) VALUES (1, 'F1 409 SRL', '14399840', 'cantitativ_valoric')" % SCH)
    cur.execute('SET LOCAL search_path TO "%s", public' % SCH)   # pe tranzacție: pleacă la rollback, nu rămâne în pool (lotul 10, 430)
    try:
        yield conn, cur
    finally:
        conn.rollback()
        p.putconn(conn)


def _mod():
    spec = importlib.util.spec_from_file_location("stoc2_409_1", os.path.join(RAD, "scripts", "stoc2_409_1_dubluri_corectie.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _iesire_validata(conn, cur, denumire, numar):
    """Nota inițială: ieșirea din stoc la factura `numar` (cu mișcarea ei, legată de factură), validată — nr. crt. 8 pe F1 („Iesire stoc
    Marfa A x2.000”, Factura 2). -> (id-ul notei, descrierea ei, documentul facturii)."""
    from core import eticheta_nota as et, jurnal_api as j, stocuri_cv_api as cv
    a = cv.intrare(conn, SCH, {"denumire": denumire, "um": "buc", "cantitate": 10, "pret_unitar": 50, "data": "2099-10-01",
                               "document": "NIR 409"})
    cur.execute("INSERT INTO facturi (numar, data_emitere, directie, total, tva, tert_nume, tert_cui, status) VALUES "
                "(%s, %s, 'emisa', 121, 21, 'Client Test SRL', '', 'emisa') RETURNING id", (numar, ZI))
    fid = cur.fetchone()[0]
    # ca `descarca_factura`: documentul e factura, cum o vede omul (pe F1 nota 105 a rămas cu „Factura #48”, scrisă înainte de 409 și
    # validată atunci — validarea de azi ar refuza-o ca depășită, deci aici nota inițială e scrisă cu regula de acum)
    r = cv.iesire(conn, SCH, {"articol_id": a["articol_id"], "data": ZI, "cantitate": 2, "document": et.factura(cur, SCH, fid)},
                  factura_id=fid)
    assert j.valideaza(conn, SCH, r["inregistrare_id"]) == {"ok": True}
    cur.execute("SELECT descriere FROM inregistrari WHERE id = %s", (r["inregistrare_id"],))
    return r["inregistrare_id"], cur.fetchone()[0], et.factura(cur, SCH, fid)


def _corectie(conn, cur, descriere, document, suma):
    """O notă a reparației vechi: sursa „stocuri”, fără mișcare, fără autor, validată (cum au scris-o scripturile loturilor 9 și 10)."""
    from core import jurnal_api as j
    cur.execute("INSERT INTO inregistrari (data, descriere, sursa, status, document_ref) VALUES (%s, %s, 'stocuri', 'ciorna', %s) "
                "RETURNING id", (ZI, descriere, document))
    nid = cur.fetchone()[0]
    cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, '607', '371', %s)", (nid, suma))
    assert j.valideaza(conn, SCH, nid) == {"ok": True}
    return nid


def _note(cur):
    cur.execute("SELECT i.id, r.nr_curent, i.descriere FROM inregistrari i LEFT JOIN registru_jurnal_numere r ON r.inregistrare_id = i.id "
                "ORDER BY i.id")
    return cur.fetchall()


def _sold_607(cur):
    cur.execute("SELECT COALESCE(sum(l.suma), 0) FROM inregistrari_linii l JOIN inregistrari i ON i.id = l.inregistrare_id "
                "WHERE i.status = 'validata' AND l.cont_debit = '607'")
    return D(str(cur.fetchone()[0]))


def test_def_409_1_corectia_dublata_se_scoate_iar_stornarea_ramasa_are_titlul_corect(tx):
    """F1, 05.10: nr. 8 (+100), 30 și 32 (stornări, −100), 31 și 33 (ieșiri pe Factura 2, +100). După reparație: 8, o stornare (30, cu
    titlul „Stornare: nota nr. crt. 1 din 05.10.2099 (<descrierea notei 8>) — descărcarea facturii, scrisă fără document”), o ieșire (31);
    32 și 33 scoase, cu numerele lor; soldul 607 neschimbat. Altă ieșire din aceeași zi, de aceeași valoare, cu O SINGURĂ corecție (care
    o numește pe ea) nu se atinge — corecțiile se leagă de nota pe care o numesc, nu de dată și sumă. Regulile
    de fond ale bazei sunt din nou active după reparație. A doua rulare: nimic.
    MUTAȚIE: în `dubluri`, `len(stornari) < 2` -> `len(stornari) < 3` -> corecția dublată rămâne -> pică."""
    conn, cur = tx
    o, o_descr, f2 = _iesire_validata(conn, cur, "Marfa A", "2")
    s1 = _corectie(conn, cur, "Stornare: n (descărcarea facturii, scrisă fără document)ota nr. crt. 1 din 05.10.2099",
                   "Nota nr. crt. 1 din 05.10.2099", "-100")
    r1 = _corectie(conn, cur, "Ieșire stoc Marfa A × 2 buc", f2, "100")
    s2 = _corectie(conn, cur, "Stornare: nota din 05.10.2099 (%s) — descărcarea facturii, scrisă fără document" % o_descr,
                   "Nota din 05.10.2099", "-100")
    r2 = _corectie(conn, cur, "Ieșire stoc Marfa A × 2 buc", f2, "100")
    # altă ieșire din aceeași zi, de aceeași valoare, cu O SINGURĂ corecție (stornare + înlocuire, care o numesc pe ea): rămâne
    o2, o2_descr, f3 = _iesire_validata(conn, cur, "Marfa C", "3")
    s3 = _corectie(conn, cur, "Stornare: nota din 05.10.2099 (%s)" % o2_descr, "Nota din 05.10.2099", "-100")
    r3 = _corectie(conn, cur, o2_descr, f3, "100")
    inainte = dict((i, nr) for i, nr, _d in _note(cur))
    sold = _sold_607(cur)
    m = _mod()
    rez = m.repara(conn, SCH)
    assert [(g["original"], g["stornari"], g["inlocuiri"], g["de_scos"]) for g in rez] == [(o, [s1, s2], [r1, r2], [s2, r2])], rez
    note = _note(cur)
    assert [i for i, _nr, _d in note] == [o, s1, r1, o2, s3, r3]
    # numerele din Registrul-jurnal rămân pe notele păstrate (deficiența 302: numărul unei note validate nu se mută)
    assert {i: nr for i, nr, _d in note} == {i: inainte[i] for i in (o, s1, r1, o2, s3, r3)}
    assert dict((i, d) for i, _nr, d in note)[s1] == (
        "Stornare: nota nr. crt. %d din 05.10.2099 (%s) — descărcarea facturii, scrisă fără document" % (inainte[o], o_descr))
    assert _sold_607(cur) == sold
    # regulile de fond, din nou active: nota validată nu se mai modifică
    cur.execute("SELECT tgname, tgenabled FROM pg_trigger WHERE tgname IN ('trg_regula_nota', 'trg_regula_linii_nota') "
                "AND tgrelid IN (%s::regclass, %s::regclass) ORDER BY 1", ("%s.inregistrari" % SCH, "%s.inregistrari_linii" % SCH))
    assert cur.fetchall() == [("trg_regula_linii_nota", "O"), ("trg_regula_nota", "O")]
    assert m.repara(conn, SCH) == []
