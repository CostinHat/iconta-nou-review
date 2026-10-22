# -*- coding: utf-8 -*-
"""284 — D300 / control: refuzul de la „Trimite în coadă” numește notele care explică diferența, iar după validarea lor declarația se
generează din nou și intră singură în coadă (comanda Costin 16.10.2026, completarea 1 la lotul 6, verbatim în DECIZII): „refuzul [...]
numește nota sau notele care explică diferența (aici nr. crt. 21, factura F1A4, 42 lei), cu link spre ele, nu doar «4 note nevalidate».
După validarea notei, declarația se regenerează singură și intră în coadă; depunerea la ANAF rămâne clicul contabilului.”

Temei: N/A — regula porții e decizia Costin 08.10.2026 (U1): R17_2 = rulajul creditor 4427, R27_2 = rulajul debitor 4426, numai note
validate, toleranța 1 leu (`control_incrucisat.compara_tva`). Aici se numește ce lipsește din rulaj, nu se schimbă comparația.
"""
import contextlib
import io
from decimal import Decimal as D

import pytest

from core import db as _db
from core import tenant_provisioning as _tprov

_SCH = "efemer_284"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


_DB = _db_ok()


@pytest.fixture()
def conn():
    if not _DB:
        pytest.skip("DB indisponibil")
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
            cur.execute(_tprov.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), _SCH))
        c.commit()
    with _db.get_conn(_SCH) as c:
        yield c
        c.rollback()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
        c.commit()


def _nota(cur, data, linii, status="ciorna", factura_id=None, descriere="n"):
    cur.execute("INSERT INTO inregistrari (data, descriere, status, factura_id) VALUES (%s,%s,%s,%s) RETURNING id",
                (data, descriere, status, factura_id))
    nid = cur.fetchone()[0]
    for deb, cre, s in linii:
        cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,%s,%s,%s)", (nid, deb, cre, s))
    return nid


def test_284_ciornele_de_pe_4427_se_numesc_cu_nr_crt_documentul_si_suma(conn):
    """MUTAȚIE: filtrul `cont_credit = '4427'` din `ciorne_pe_conturi_tva` -> `cont_debit = '4427'` -> nota nu se mai găsește -> pică."""
    from core import control_incrucisat as ci
    with conn.cursor() as cur:
        cur.execute("INSERT INTO facturi (serie, numar, data_emitere, directie, total, tva, status) VALUES ('F1A','4','2026-10-16','emisa',"
                    "242,42,'emisa') RETURNING id")
        fid = cur.fetchone()[0]
        _nota(cur, "2026-10-01", [("5121", "1012", 100)], status="validata")
        _nota(cur, "2026-10-02", [("6022", "401", 10)])                                      # ciornă care nu atinge TVA-ul
        nid = _nota(cur, "2026-10-16", [("4111", "707", 200), ("4111", "4427", 42)], factura_id=fid)
        _nota(cur, "2026-09-30", [("4111", "4427", 99)])                                     # în afara ferestrei
    constatari = [{"stare": "rosu", "cont": "4427", "diferenta": D("42")}, {"stare": "verde", "cont": "4426", "diferenta": D("0")}]
    ci.ciorne_care_explica(conn, _SCH, "2026-10-01", "2026-11-01", constatari)
    # [302] ciorna n-are număr (se dă la validare): se numește prin data ei, ca în Registrul jurnal
    assert constatari[0]["ciorne"] == [{"nota_id": nid, "nr_curent": None, "eticheta_nota": "din 16.10.2026", "data": "2026-10-16",
                                        "descriere": "n", "document": "Factură F1A nr. 4 din 16.10.2026", "suma": "42.00"}], constatari[0]   # [lotul 11, 443] seria separat de număr
    assert constatari[0]["ciorne_explica"] is True and "ciorne" not in constatari[1]
    constatari = [{"stare": "rosu", "cont": "4427", "diferenta": D("50")}]
    assert ci.ciorne_care_explica(conn, _SCH, "2026-10-01", "2026-11-01", constatari)[0]["ciorne_explica"] is False


def test_284_refuzul_numeste_notele_si_nu_mai_spune_doar_cate(monkeypatch):
    """MUTAȚIE: bucla `for d in numite` scoasă din `poarta_tva_balanta` -> refuzul nu mai numește nota -> pică."""
    from core import uc_coada as uq, control_incrucisat as ci
    nota = {"nota_id": 77, "nr_curent": 21, "data": "2026-10-16", "descriere": "x", "document": "Factură F1A4 din 16.10.2026", "suma": "42.00"}
    col = {"stare": "rosu", "cont": "4427", "rand": "R17_2", "eticheta": "TVA colectată", "declarat": D("42"), "contabil": D("0"),
           "diferenta": D("42"), "ciorne": [nota], "ciorne_explica": True}
    monkeypatch.setattr(uq.db, "get_conn", lambda schema=None: contextlib.nullcontext(None))
    monkeypatch.setattr(ci, "verifica_tva", lambda c, s, an, luna: {"stare": "rosu", "constatari": [col]})
    r = uq.poarta_tva_balanta("tenant_x", 2026, 10)
    assert r["mesaj"].count(r["note"][0]["eticheta"]) == 1, r["mesaj"]   # refuzul numește nota, cu eticheta ei (nr. crt., document, sumă)
    assert "Validatorul ANAF verifică structura" not in r["mesaj"], "notele explică toată diferența: nu se mai trimite la „corectează”"
    assert [n["nota_id"] for n in r["note"]] == [77] and r["note"][0]["eticheta"].startswith("nr. crt. 21")
    blocaj, _ = uq.decizie_poarta(r, [dict(nota, eticheta=uq.eticheta_nota_tva(nota))] * 4)
    assert "notă(e) nevalidată(e)" not in blocaj["mesaj"] and blocaj["ciorne"] == 4


def test_284_asteptarea_se_scrie_o_data_pe_perioada():
    if not _DB:
        pytest.skip("DB indisponibil")
    from core import uc_coada as uq
    cer = uq._CerereSalvata({"tenant_id": 209901, "tip": "d300", "an": 2099, "luna": 10})
    try:
        a1 = uq.asteapta_notele(cer, {"uid": 1, "firm": 209901, "rol": "admin"}, [5, 3, 5])
        a2 = uq.asteapta_notele(cer, {"uid": 1, "firm": 209901, "rol": "admin"}, [6])
        with _db.get_conn() as c:
            with c.cursor() as cur:
                cur.execute("SELECT id, note_ids, rezolvata_la IS NULL, rezultat, cerere FROM public.declaratii_in_asteptare "
                            "WHERE tenant_id = 209901 ORDER BY id")
                rows = cur.fetchall()
        assert [(r[0], r[1], r[2]) for r in rows] == [(a1, [3, 5], False), (a2, [6], True)]
        assert rows[0][3] == {"cod": "INLOCUITA"} and rows[1][4] == {"tenant_id": 209901, "tip": "d300", "an": 2099, "luna": 10}
    finally:
        with _db.get_conn() as c:
            with c.cursor() as cur:
                cur.execute("DELETE FROM public.declaratii_in_asteptare WHERE tenant_id = 209901")
            c.commit()


class _Conn:
    def cursor(self):
        return contextlib.nullcontext(None)

    def commit(self):
        pass

    def rollback(self):
        pass


def test_284_dupa_validarea_notelor_declaratia_intra_singura_in_coada(monkeypatch):
    """MUTAȚIE: `if ramase: continue` -> `if not ramase: continue` -> declarația se reia cu nota încă nevalidată -> pică."""
    from core import uc_coada as uq, repo_declaratii as rd, repo_contabilitate as rc, notificari_api as na, erori
    monkeypatch.setattr(uq.db, "get_conn", lambda schema=None: contextlib.nullcontext(_Conn()))
    monkeypatch.setattr(uq._uc_comun, "_cu_firma", lambda c, t, txt: txt)
    monkeypatch.setattr(rd, "asteptari_deschise", lambda cur, cab: [(1, 9, [5], "efemer")])
    stare = {"ramase": 1, "revendicat": []}
    monkeypatch.setattr(rc, "cate_nevalidate_dintre", lambda cur, ids: stare["ramase"])
    monkeypatch.setattr(rd, "revendica_asteptarea", lambda cur, aid: stare["revendicat"].append(aid) or (
        {"tenant_id": 9, "tip": "d300", "an": 2026, "luna": 10}, 4, "admin", "d300", 2026, 10, None))
    monkeypatch.setattr(rd, "scrie_rezultatul_asteptarii", lambda cur, aid, rez: None)
    notif, chemat = [], []
    monkeypatch.setattr(na, "adauga", lambda c, uid, tip, txt, link=None: notif.append((uid, tip, txt, link)))
    monkeypatch.setattr(uq, "coada_adauga", lambda d, ctx: chemat.append((d.tip, d.luna, ctx["uid"], ctx["firm"])) or {
        "ok": True, "coada_id": 31, "pas_urmator": {"mesaj": "a fost trimisă la validare."}})
    assert uq.reia_declaratiile_in_asteptare(2) == [] and chemat == [] and stare["revendicat"] == [], "nota e încă nevalidată"
    stare["ramase"] = 0
    r = uq.reia_declaratiile_in_asteptare(2)
    assert chemat == [("d300", 10, 4, 2)], "cu cererea și contextul celui care a trimis-o"
    assert r[0]["ok"] and notif == [(4, "declaratie_reluata", "D300 10/2026: notele au fost validate, declarația s-a generat din nou și a "
                                     "fost trimisă la validare.", "validat:31")], notif
    monkeypatch.setattr(uq, "coada_adauga", lambda d, ctx: (_ for _ in ()).throw(erori.DateInvalide({"mesaj": "TVA-ul tot diferă."})))
    r = uq.reia_declaratiile_in_asteptare(2)
    assert r[0]["ok"] is False and notif[-1][2].endswith("tot nu intră în coadă — TVA-ul tot diferă.") and notif[-1][3] is None
