# -*- coding: utf-8 -*-
"""GARDA retestului Costin din 08.10.2026 dimineața + completarea lui (verbatim în DECIZII 08.10.2026), pe backend:

  pct.1  statul schimbat cu o ciornă nevalidată pentru aceeași lună: contabilizarea o ÎNLOCUIEȘTE cu nota din statul de acum;
         „nu rămâne niciodată o ciornă cu alte sume decât statul afișat” (aceeași amprentă -> rămâne; validată -> neatinsă).
  pct.3  refacerea unui document respins ÎNAINTEA lui S3 își găsește respingerea (elementele vechi primesc `payload.doc`).
  compl. pct.1  starea de încasare a facturii: încasată / parțial / neîncasată, din chitanțe + plățile legate + `platita_la`.
(pct.2 — CAM pe salariat — e în `test_s1_elemente_salariale.py`, pe fixtura statului; pct.4–6 și compl. pct.2 — ecrane — în
`test_refuz_spre_ecran.py`, `test_buton_blocat_structura.py` și proba de browser.)

Schemă efemeră din `tenant_template.sql`, ștearsă la ieșire; tabelele partajate numai în tranzacție anulată, perioada 2099.
"""
import io
from decimal import Decimal

import pytest

from core import db as _db
from core import tenant_provisioning as _tp

SCH = "efemer_retest_0810"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


@pytest.fixture()
def conn():
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tp.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), SCH))
            cur.execute("INSERT INTO %s.firma_profil (id, nume, cui, platitor_tva) VALUES (1, 'RETEST SRL', 'RO14399840', true)" % SCH)
            cur.execute("UPDATE %s.firma_profil SET forma_juridica = 'SRL', capital_subscris = 200" % SCH)
        c.commit()
    try:
        with _db.get_conn(SCH) as c:
            yield c
    finally:
        with _db.get_conn() as c:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            c.commit()


# ── pct.1 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _propunere(suma):
    return {"document_ref": "SAL 10/2099", "note": [{"debit": "641", "credit": "421", "suma": Decimal(suma)}], "total": Decimal(suma),
            "divergente": []}


def _note_stat(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT i.id, i.status, l.suma::text FROM inregistrari i JOIN inregistrari_linii l ON l.inregistrare_id = i.id "
                    "WHERE i.numar = 'SAL 10/2099' ORDER BY i.id")
        return cur.fetchall()


def test_ciorna_cu_alte_sume_se_inlocuieste_cu_nota_statului_de_acum(conn, monkeypatch):
    """„când statul se schimbă și există o ciornă nevalidată pentru aceeași lună, contabilizarea o înlocuiește cu nota din statul de
    acum”. MUTAȚIE: ramura `ciorna_nevalidata` scoasă din `salarii_contare_scrie` (întoarce DEJA_CONTATA) -> ciorna veche rămâne
    -> pică."""
    from core import uc_tenants as uc, uc_comun, salarii_contare as sc, common
    import datetime as _d
    monkeypatch.setattr(common, "azi_ro", lambda: _d.date(2100, 1, 10))   # [deficiența 216] 10/2099 trebuie să fie o lună încheiată
    with conn.cursor() as cur:   # ciorna #1 de pe producție: scrisă din statul de dinainte, ziua 28, fără autor
        cur.execute("INSERT INTO inregistrari (data, numar, descriere, sursa, status) VALUES ('2099-10-28', 'SAL 10/2099', "
                    "'Stat de plata 10/2099', 'salarii', 'ciorna') RETURNING id")
        vechi = cur.fetchone()[0]
        cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, '641', '421', 100)",
                    (vechi,))
    conn.commit()
    monkeypatch.setattr(uc_comun, "_schema_cabinet_sau_404", lambda ctx, tid: SCH)
    monkeypatch.setattr(sc, "propunere", lambda c, s, an, luna: _propunere("150.00"))
    p = uc.salarii_contare_propunere(1, 2099, 10, {"uid": 1})
    assert (p["nota_id"], p["ciorna_alte_sume"]) == (vechi, True)          # ecranul o spune și oferă înlocuirea
    r = uc.salarii_contare_scrie(1, 2099, 10, {"uid": 1})
    assert (r["cod"], r["nota_inlocuita"]) == ("CIORNA_INLOCUITA", vechi)
    assert [(s, x) for _i, s, x in _note_stat(conn)] == [("ciorna", "150.00")]   # ciorna veche a ieșit
    # aceeași amprentă: nimic nu se rescrie, iar ecranul nu mai cere înlocuirea
    r2 = uc.salarii_contare_scrie(1, 2099, 10, {"uid": 1})
    assert (r2["cod"], r2["nota_id"]) == ("DEJA_CONTATA", r["nota_id"])
    assert uc.salarii_contare_propunere(1, 2099, 10, {"uid": 1})["ciorna_alte_sume"] is False
    # nota VALIDATĂ nu se atinge, oricât s-ar schimba statul
    with conn.cursor() as cur:
        cur.execute("UPDATE inregistrari SET status = 'validata' WHERE id = %s", (r["nota_id"],))
    conn.commit()
    monkeypatch.setattr(sc, "propunere", lambda c, s, an, luna: _propunere("175.00"))
    assert uc.salarii_contare_scrie(1, 2099, 10, {"uid": 1})["cod"] == "DEJA_CONTATA"
    assert [(s, x) for _i, s, x in _note_stat(conn)] == [("validata", "150.00")]


# ── compl. pct.1 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _factura(conn, numar, directie="emisa"):
    from core import facturi_api as fa
    r = fa.creeaza_factura(conn, numar, "2099-10-07", directie, [{"descriere": "Servicii", "cantitate": 1, "pret_unitar": 200,
                           "cota_tva": 21}], tert_nume="CLIENT", tert_cui="RO14399840")
    return r["factura_id"] if isinstance(r, dict) else r


def _stare(conn, fid):
    from core import facturi_api as fa
    s = fa.detalii_factura(conn, fid)["stare_incasare"]
    lista = {f["id"]: f["stare_incasare"] for f in fa.lista_facturi(conn, an=2099, luna=10)}
    assert lista[fid] == s                 # o singură definiție, pentru listă și detaliu
    return (s["stare"], s["incasat"], s["total"])


def test_starea_de_incasare_din_chitante_plati_si_marcajul_integral(conn):
    """„starea de încasare (încasată / parțial / neîncasată) trebuie să fie vizibilă pe factură și în lista «Istoric facturi»”.
    MUTAȚIE: plățile legate de factură scoase din `_cu_stare_incasare` -> rămâne „partial” după extras -> pică."""
    fid = _factura(conn, "FE1")
    assert _stare(conn, fid) == ("neincasata", "0.00", "242.00")
    with conn.cursor() as cur:
        cur.execute("INSERT INTO chitante (serie, numar, data, factura_id, client_nume, suma, anulata) VALUES "
                    "('ZC', 1, '2099-10-08', %s, 'CLIENT', 100, false)", (fid,))
    assert _stare(conn, fid) == ("partial", "100.00", "242.00")
    with conn.cursor() as cur:   # restul, prin bancă: nota de plată legată de factură (reconcilierea)
        cur.execute("INSERT INTO inregistrari (data, descriere, sursa, status, factura_id) VALUES ('2099-10-09', 'Incasare', 'banca', "
                    "'ciorna', %s) RETURNING id", (fid,))
        cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, '5121', '4111', 142)",
                    (cur.fetchone()[0],))
    assert _stare(conn, fid) == ("incasata", "242.00", "242.00")
    # marcajul integral (chitanța integrală, bonul stins) și la factura primită (401 pe debit)
    fp = _factura(conn, "FP1", "primita")
    assert _stare(conn, fp)[0] == "neincasata"
    with conn.cursor() as cur:
        cur.execute("UPDATE facturi SET platita_la = now() WHERE id = %s", (fp,))
    assert _stare(conn, fp) == ("incasata", "242.00", "242.00")


# ── pct.3 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture()
def tx():
    p = _db.pool()
    c = p.getconn()
    cur = c.cursor()
    cur.execute("SELECT id, accounting_firm_id FROM public.users WHERE accounting_firm_id IS NOT NULL ORDER BY id LIMIT 1")
    uid, cab = cur.fetchone()
    cur.execute("INSERT INTO public.tenants (schema_name, nume, accounting_firm_id) VALUES ('zt_retest_0810', 'ZT retest', %s) "
                "RETURNING id", (cab,))
    try:
        yield c, cur, cur.fetchone()[0], cab, uid
    finally:
        c.rollback()
        p.putconn(c)


def test_documentul_refacut_isi_gaseste_respingerea_dinaintea_lui_s3(tx):
    """NIR 1 (F1) a fost respins pe 07.10, înainte ca elementele să poarte `doc`; NIR-ul refăcut nu arăta „retrimis după respingere”.
    MUTAȚIE: `doc_in_coada` necheamat -> `retrimisa` întoarce None -> pică."""
    import psycopg2.extras as _E
    from core import coada_api as c, migrare_decizii_0810 as m
    conn, cur, tid, cab, uid = tx
    vechi = {"inregistrare_id": 10, "grup": "nir-1", "sursa": "stocuri", "document_ref": "NIR nr 1 din 07.10.2099"}   # fără `doc`
    cur.execute("INSERT INTO public.declaratii_coada (cabinet_id, tenant_id, tip, fel, perioada, stare, payload, hash, motiv_respingere, "
                "respins_la) VALUES (%s, %s, 'nota', 'nota', 'nota-10', 'respinsa', %s, 'h', 'logica veche', now()) RETURNING id",
                (cab, tid, _E.Json(vechi)))
    nou = {"inregistrare_id": 20, "grup": "nir-3", "doc": "nir-3", "doc_anterior": "nir-1", "amprenta": "a"}
    cur.execute("INSERT INTO public.declaratii_coada (cabinet_id, tenant_id, tip, fel, perioada, stare, payload, hash) VALUES "
                "(%s, %s, 'nota', 'nota', 'nota-20', 'la_senior', %s, 'h') RETURNING id", (cab, tid, _E.Json(nou)))
    membri = [(cur.fetchone()[0], nou)]
    assert c.retrimisa(cur, tid, membri) is None                          # defectul, măsurat pe producție
    assert {"nir-1"} <= {d for _i, d in m.doc_in_coada(conn)}            # elementul vechi și-a primit documentul
    assert c.retrimisa(cur, tid, membri) == {"motiv_respingere": "logica veche", "la": c.retrimisa(cur, tid, membri)["la"],
                                             "schimbata": None}           # respingerea veche n-avea amprentă: „nu se poate compara”


# ── U1 (al patrulea mesaj + completarea): poarta TVA declarație <-> balanță ─────────────────────────────────────────────────
def _verificare(*constatari):
    return {"stare": "rosu" if any(c["stare"] == "rosu" for c in constatari) else "verde", "constatari": list(constatari)}


def test_poarta_tva_refuza_diferenta_pe_4427_4426_si_numai_acolo(monkeypatch):
    """„dacă rândurile de TVA colectată și deductibilă ale D300 nu se potrivesc cu rulajele 4427 și 4426 ale lunii (toleranță:
    rotunjirea la leu), «Trimite în coadă» e blocat și se afișează diferența pe conturi”. Comparația e `verifica_tva` (toleranța 1
    leu); poarta citește numai perechile 4427 / 4426. MUTAȚIE: filtrul `CONTURI_TVA_POARTA` scos -> diferența pe 4423 blochează -> pică."""
    from decimal import Decimal as D
    from core import uc_coada as uq, control_incrucisat as ci
    ded = {"stare": "rosu", "cont": "4426", "rand": "R27_2", "eticheta": "TVA deductibilă", "declarat": D("0"),
           "contabil": D("241.50"), "diferenta": D("-241.50")}
    col = {"stare": "verde", "cont": "4427", "rand": "R17_2", "eticheta": "TVA colectată", "declarat": D("1180"),
           "contabil": D("1180.00"), "diferenta": D("0")}
    rez = {"stare": "rosu", "eticheta": "TVA de plată (rezultat decont)", "declarat": D("1180"), "contabil": D("938.50"),
           "diferenta": D("241.50")}   # perechea rezultatului (4423) nu poartă `cont` de poartă
    monkeypatch.setattr(uq.db, "get_conn", lambda schema=None: __import__("contextlib").nullcontext(None))
    monkeypatch.setattr(ci, "verifica_tva", lambda conn, s, an, luna: _verificare(col, ded, rez))
    r = uq.poarta_tva_balanta("tenant_x", 2026, 10)
    assert (r["cod"], [(d["cont"], d["declarat"], d["contabil"], d["diferenta"]) for d in r["diferente"]]) == (
        "TVA_DIFERA_DE_BALANTA", [("4426", "0.00", "241.50", "-241.50")])
    monkeypatch.setattr(ci, "verifica_tva", lambda conn, s, an, luna: _verificare(col, rez))
    assert uq.poarta_tva_balanta("tenant_x", 2026, 10) is None
    assert uq.poarta_tva_balanta("tenant_x", 2026, None, trim=None) is None


def test_coada_cere_poarta_pentru_toate_declaratiile_de_tva(monkeypatch):
    """„se aplică tuturor declarațiilor de TVA: D300, D394, D390”; celelalte nu trec prin ea. MUTAȚIE: apelul porții scos din
    `coada_adauga` -> d394 intră -> pică."""
    import types
    from core import uc_coada as uq, uc_comun, declaratii_api, erori
    assert uq.DECLARATII_TVA == ("d300", "d394", "d390")
    chemat = []
    monkeypatch.setattr(uc_comun, "_are_permisiune", lambda ctx, p: True)
    monkeypatch.setattr(uc_comun, "_schema_sau_404", lambda ctx, tid: "tenant_x")
    monkeypatch.setattr(declaratii_api, "genereaza", lambda c, s, tip, body: ("<x/>", []))
    monkeypatch.setattr(uq.db, "get_conn", lambda schema=None: __import__("contextlib").nullcontext(None))
    monkeypatch.setattr(uq, "poarta_tva_balanta", lambda s, an, luna, trim=None: chemat.append(an) or {"cod": uq.COD_TVA_BALANTA,
                                                                                                    "mesaj": "m", "diferente": []})
    monkeypatch.setattr(uq, "ciorne_in_perioada", lambda s, an, luna: 0)   # fără ciorne: diferența blochează (R36)
    for tip in ("d300", "d394", "d390"):
        d = types.SimpleNamespace(tip=tip, tenant_id=1, an=2099, luna=10, trim=None, motiv_trecere=None,
                                  model_dump=lambda **k: {"tip": tip, "an": 2099, "luna": 10})
        with pytest.raises(erori.DateInvalide) as e:
            uq.coada_adauga(d, {"uid": 1, "firm": 1})
        assert e.value.detaliu["cod"] == "TVA_DIFERA_DE_BALANTA"
    assert len(chemat) == 3
