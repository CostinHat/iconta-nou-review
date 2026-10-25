# -*- coding: utf-8 -*-
"""Lotul 12, comanda Costin 12.2 pct.10 (verbatim în DECIZII „Comanda 12.2”), pachetul stoc2 — deficiența 619:
„Validarea unui document se face împreună cu notele lui (contare, ieșire din stoc, stornare, retur). Azi: stornarea/returul (−27,50) s-a
validat înaintea documentului stornat, aflat în ciornă, deci 607 e negativ în evidența validată; la F1A nr. 8 și F1A nr. 14 validarea
contării lasă ieșirea de stoc în ciornă.”

CLASA: orice drum care trece o notă a unui document în evidență — Registrul jurnal (`uc_tenants.jurnal_valideaza` ->
`coada_api.valideaza_documentul`), coada „De validat” (`coada_api.aproba`), validarea în masă (`uc_coada.coada_aproba_mai_multe` ->
`aproba`). Căutare: `grep -rn "SET status *= *'validata'" core main.py` — un singur loc scrie starea (`jurnal_api.valideaza`); apelanții
lui: `grep -rn "_jurnal.valideaza" core` și `grep -rn "jurnal_api.valideaza" core`. Două defecte, pe toate drumurile:
  (a) coada valida notele înghețate la intrarea documentului în coadă (`membri_grup`), nu notele documentului de acum;
  (b) stornarea (factura de stornare, returul în stoc) intra în evidență înaintea documentului stornat aflat încă în ciornă.
Plus: „ori toate notele documentului, ori niciuna” depindea de apelant — coada se întorcea cu refuzul fără excepție, deci tranzacția ei
se comitea cu notele validate până la refuz.

Temei: OMFP 1802/2014 pct.69 („Înregistrarea stornării unei operațiuni contabile aferente exercițiului financiar curent se efectuează fie
prin corectarea cu semnul minus a operațiunii inițiale (stornare în roșu), fie prin înregistrarea inversă a acesteia (stornare în negru)”)
— INTERPRETARE CU TEMEI pentru ordine (`coada_api.MESAJ_STORNAT_IN_CIORNA`). Testele rulează într-o singură tranzacție anulată la final
(schemă efemeră din `tenant_template.sql`; rândurile din `public.tenants` / `public.declaratii_coada` se anulează), pe date din 2099."""
import io
from decimal import Decimal as D

import pytest

from core import db as _db
from core import tenant_provisioning as _tp

SCH = "efemer_l12_stoc2_619"
ZI = "2099-10-19"
ARTICOL = "Marfa B 619"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:  # noqa: BLE001 — fără bază, testele se sar
        return False


@pytest.fixture()
def tx():
    if not _db_ok():
        pytest.skip("DB indisponibil")
    p = _db.pool()
    conn = p.getconn()
    cur = conn.cursor()
    cur.execute("SELECT id, accounting_firm_id FROM public.users WHERE email='asistent@prisma-cont.test'")
    r = cur.fetchone()
    if not r:
        p.putconn(conn)
        pytest.skip("utilizatorul de test lipsește")
    asist, cab = r
    cur.execute("SELECT id FROM public.users WHERE accounting_firm_id=%s AND poate_valida AND id<>%s ORDER BY id LIMIT 1", (cab, asist))
    valid = cur.fetchone()[0]
    cur.execute("UPDATE public.users SET poate_pregati=true, poate_valida=false WHERE id=%s", (asist,))
    cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
    cur.execute(_tp.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), SCH))
    # CUI 14399840 (DANTE INTERNATIONAL SA) — cifra de control verificată (algoritmul din CLAUDE.md)
    cur.execute("INSERT INTO %s.firma_profil (id, nume, cui, adresa, oras, judet, caen, platitor_tva, tip_decont) VALUES "
                "(1, 'F1 619 SRL', '14399840', 'Str. Test 1', 'Bucuresti', 'B', '4690', true, 'L')" % SCH)
    cur.execute("UPDATE %s.firma_profil SET forma_juridica = 'SRL', capital_subscris = 200, serie_factura = 'F1A', "
                "metoda_stoc = 'cantitativ_valoric' WHERE id = 1" % SCH)
    cur.execute("INSERT INTO public.tenants (schema_name, nume, accounting_firm_id) VALUES (%s, 'ZT Lot 12 619', %s) RETURNING id",
                (SCH, cab))
    tid = cur.fetchone()[0]
    cur.execute('SET LOCAL search_path TO "%s", public' % SCH)   # pe tranzacție: pleacă la rollback, nu rămâne în pool (lotul 10, 430)
    try:
        yield conn, cur, tid, cab, asist, valid
    finally:
        conn.rollback()
        cur = conn.cursor()
        cur.execute("RESET iconta.utilizator")
        conn.commit()
        p.putconn(conn)


def _ca(cur, uid):
    cur.execute("SELECT set_config('iconta.utilizator', %s, false)", (str(uid),))


def _articol(conn):
    from core import stocuri_cv_api as cv
    r = cv.intrare(conn, SCH, {"denumire": ARTICOL, "um": "buc", "cantitate": 10, "pret_unitar": "27.50", "data": "2099-10-01",
                               "document": "NIR 619"})
    assert "eroare" not in r, r
    return r["articol_id"]


def _factura(conn, aid, iesire=True):
    """Factura emisă cu un articol din stoc, pe drumul emiterii: contarea (scrisă la creare) și, cu `iesire`, ieșirea din stoc
    (`descarca_factura`, „Pleacă marfa acum: Da”). -> (factura_id, contarea, ieșirea)."""
    from core import facturi_api, stocuri_cv_api as cv
    r = facturi_api.emite_factura(conn, [{"descriere": ARTICOL, "articol_id": aid, "cont_venit": "707", "cantitate": 1, "um": "buc",
                                          "pret_unitar": 50, "cota_tva": 21}], data_emitere=ZI, moneda="RON", platitor_tva=True,
                                  tert_nume="DANTE INTERNATIONAL SA", tert_cui="RO14399840")
    fid = r["factura_id"]
    if iesire:
        d = cv.descarca_factura(conn, SCH, fid, ZI)
        assert d["descarcate"] and not d["erori"], d
    return fid, _contare(conn, fid), _iesire(conn, fid)


def _contare(conn, fid):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM inregistrari WHERE factura_id = %s AND sursa = 'facturi' ORDER BY id", (fid,))
        r = [x[0] for x in cur.fetchall()]
    assert len(r) == 1, r
    return r[0]


def _iesire(conn, fid):
    with conn.cursor() as cur:
        cur.execute("SELECT DISTINCT inregistrare_id FROM miscari_stoc WHERE factura_id = %s AND inregistrare_id IS NOT NULL", (fid,))
        r = [x[0] for x in cur.fetchall()]
    return r[0] if r else None


def _stornare_cu_retur(conn, fid):
    """„Stornează” -> „Da, marfa se întoarce” (`facturi_api.storneaza(retur=True)`). -> (storno_id, contarea stornării, returul)."""
    from core import facturi_api
    s = facturi_api.storneaza(conn, fid, retur=True)
    sid = s["factura_id"]
    return sid, _contare(conn, sid), _iesire(conn, sid)


def _stari(cur, ids):
    cur.execute("SELECT id, status FROM inregistrari WHERE id = ANY(%s)", (list(ids),))
    return dict(cur.fetchall())


def _607_validat(cur):
    cur.execute("SELECT COALESCE(sum(l.suma), 0) FROM inregistrari_linii l JOIN inregistrari i ON i.id = l.inregistrare_id "
                "WHERE i.status = 'validata' AND l.cont_debit = '607'")
    return D(str(cur.fetchone()[0]))


# ── (a) coada: notele documentului de acum, nu cele înghețate la intrarea în coadă ─────────────────────────────────────────────
def test_def_619_coada_valideaza_si_iesirea_scrisa_in_afara_cozii(tx):
    """619, „la F1A nr. 8 și F1A nr. 14 validarea contării lasă ieșirea de stoc în ciornă”. Asistentul emite factura (contarea intră în
    coadă), iar ieșirea din stoc a aceleiași facturi o scrie apoi contabilul-șef (ciorna lui nu intră în coadă). „Validează” pe document
    în „De validat” validează și ieșirea: documentul se validează cu toate notele lui.
    MUTAȚIE: în `coada_api.aproba`, `valideaza_documentul(conn, schema_nota, nid)` -> `_jurnal.valideaza(conn, schema_nota, nid)` (notele
    înghețate în coadă) -> ieșirea rămâne ciornă -> pică."""
    from core import coada_api as c, stocuri_cv_api as cv
    conn, cur, tid, cab, asist, valid = tx
    aid = _articol(conn)
    _ca(cur, asist)
    fid, contare, _ = _factura(conn, aid, iesire=False)
    el = c.pune_notele_in_coada(conn, cab, tid, asist)
    assert len(el) == 1, el
    _ca(cur, valid)
    assert cv.descarca_factura(conn, SCH, fid, ZI)["descarcate"]
    iesire = _iesire(conn, fid)
    cur.execute("SELECT count(*) FROM public.declaratii_coada WHERE tenant_id = %s AND perioada = %s", (tid, c.perioada_nota(iesire)))
    assert cur.fetchone()[0] == 0          # ieșirea nu e în coadă: grupul înghețat n-o cuprinde
    r = c.aproba(conn, el[0]["coada_id"], str(valid), aprobat_de_id=valid, cabinet_id_apelant=cab, schema_nota=SCH)
    assert r["ok"], r
    assert _stari(cur, [contare, iesire]) == {contare: "validata", iesire: "validata"}


# ── (b) stornarea nu intră în evidență înaintea documentului stornat ──────────────────────────────────────────────────────────
def _f1_ca_pe_productie(conn, cur):
    """Starea F1 de pe producție (F1A nr. 8 / nr. 9): contarea facturii validată singură (drumul vechi al jurnalului: o notă), ieșirea
    din stoc ciornă; stornarea cu retur scrisă (contarea stornării și returul, ciorne). -> dict cu id-urile."""
    from core import jurnal_api as j
    aid = _articol(conn)
    fid, contare, iesire = _factura(conn, aid)
    assert j.valideaza(conn, SCH, contare) == {"ok": True}        # validarea veche, pe o singură notă
    sid, contare_s, retur = _stornare_cu_retur(conn, fid)
    assert retur and _stari(cur, [iesire, contare_s, retur]) == {iesire: "ciorna", contare_s: "ciorna", retur: "ciorna"}
    return {"fid": fid, "contare": contare, "iesire": iesire, "sid": sid, "contare_s": contare_s, "retur": retur}


def test_def_619_stornarea_nu_se_valideaza_inaintea_facturii_stornate(tx):
    """619, „stornarea/returul (−27,50) s-a validat înaintea documentului stornat, aflat în ciornă, deci 607 e negativ în evidența
    validată”. „Validează” pe retur (Registrul jurnal) se refuză cât ieșirea F1A nr. 8 e ciornă; refuzul numește factura stornată și
    ciorna ei, iar nimic nu se validează (nici returul, nici contarea stornării). După ieșire, stornarea se validează: 607 în evidența
    validată nu e niciodată negativ.
    MUTAȚIE: `refuz_stornare_inaintea_documentului` întoarce mereu None -> returul se validează, 607 validat = −27,50 -> pică."""
    from core import coada_api as c
    conn, cur, tid, cab, asist, valid = tx
    d = _f1_ca_pe_productie(conn, cur)
    r = c.valideaza_documentul(conn, SCH, d["retur"])
    assert r.get("cod") == c.COD_STORNAT_IN_CIORNA, r
    with conn.cursor() as cc:
        from core import eticheta_nota as et
        f8, f9 = et.factura(cc, SCH, d["fid"]), et.factura(cc, SCH, d["sid"])
    # OMFP 1802/2014 pct.69: stornarea corectează operațiunea inițială — refuzul numește documentul stornat și ce e de făcut
    assert r["eroare"].startswith("%s stornează %s, care are încă în ciornă nota din 19.10.2099 (Ieșire stoc %s × 1 buc)." % (f9, f8, ARTICOL)), r["eroare"]
    assert "validează întâi %s, apoi stornarea" % f8 in r["eroare"], r["eroare"]
    assert _stari(cur, [d["retur"], d["contare_s"]]) == {d["retur"]: "ciorna", d["contare_s"]: "ciorna"}
    assert _607_validat(cur) == D("0")
    assert c.valideaza_documentul(conn, SCH, d["iesire"])["ok"]
    assert _607_validat(cur) == D("27.50")
    r = c.valideaza_documentul(conn, SCH, d["retur"])
    assert r["ok"] and sorted(r["validate"]) == sorted([d["retur"], d["contare_s"]]), r
    assert _607_validat(cur) == D("0.00")


def test_def_619_coada_refuza_stornarea_inaintea_facturii_stornate_si_nu_lasa_nimic_validat(tx):
    """619, drumul cozii. Asistentul emite factura cu ieșire și o stornează cu retur: două documente în „De validat”. „Validează” pe
    stornare întâi: refuzul numește factura stornată, iar NIMIC nu intră în evidență (returul, contarea stornării) — elementul rămâne de
    validat. Apoi factura, apoi stornarea: amândouă validate.
    MUTAȚIE: `refuz_stornare_inaintea_documentului` fără documentul stornat (`d = None`) -> elementul stornării se aprobă -> pică."""
    from core import coada_api as c
    conn, cur, tid, cab, asist, valid = tx
    aid = _articol(conn)
    _ca(cur, asist)
    fid, contare, iesire = _factura(conn, aid)
    sid, contare_s, retur = _stornare_cu_retur(conn, fid)
    el = c.pune_notele_in_coada(conn, cab, tid, asist)
    assert len(el) == 2, el
    cur.execute("SELECT id, payload->>'grup' FROM public.declaratii_coada WHERE tenant_id = %s AND stare = 'la_senior' ORDER BY id", (tid,))
    pe_grup = {}
    for i, g in cur.fetchall():
        pe_grup.setdefault(g, i)
    el_f, el_s = pe_grup["factura-%d" % fid], pe_grup["factura-%d" % sid]
    _ca(cur, valid)
    r = c.aproba(conn, el_s, str(valid), aprobat_de_id=valid, cabinet_id_apelant=cab, schema_nota=SCH)
    assert (r["ok"], r["motiv_cod"]) == (False, c.COD_STORNAT_IN_CIORNA), r
    assert set(_stari(cur, [contare, iesire, contare_s, retur]).values()) == {"ciorna"}
    cur.execute("SELECT DISTINCT stare FROM public.declaratii_coada WHERE tenant_id = %s", (tid,))
    assert cur.fetchall() == [("la_senior",)]
    assert c.aproba(conn, el_f, str(valid), aprobat_de_id=valid, cabinet_id_apelant=cab, schema_nota=SCH)["ok"]
    assert c.aproba(conn, el_s, str(valid), aprobat_de_id=valid, cabinet_id_apelant=cab, schema_nota=SCH)["ok"]
    assert set(_stari(cur, [contare, iesire, contare_s, retur]).values()) == {"validata"}
    assert _607_validat(cur) == D("0.00")


def test_def_619_documentul_se_valideaza_tot_sau_deloc_fara_punctul_de_salvare_al_apelantului(tx):
    """„Ori toate notele documentului, ori niciuna” e al validării, nu al apelantului: coada se întoarce cu refuzul fără excepție, deci
    tranzacția ei se comitea cu notele validate până la refuz. Aici: ieșirea fără linii (nu se poate valida) — contarea aceleiași facturi,
    validată prima, se anulează odată cu refuzul.
    MUTAȚIE: `ROLLBACK TO SAVEPOINT valideaza_documentul` scos din ramura refuzului -> contarea rămâne validată -> pică."""
    from core import coada_api as c
    conn, cur, tid, cab, asist, valid = tx
    aid = _articol(conn)
    fid, contare, iesire = _factura(conn, aid)
    cur.execute("DELETE FROM inregistrari_linii WHERE inregistrare_id = %s", (iesire,))
    r = c.valideaza_documentul(conn, SCH, contare)
    assert "a aceluiași document nu se poate valida" in r.get("eroare", ""), r
    assert _stari(cur, [contare, iesire]) == {contare: "ciorna", iesire: "ciorna"}


def test_def_619_validarea_in_masa_valideaza_stornarea_dupa_factura_oricare_ar_fi_ordinea_alegerii(tx):
    """Validarea în masă („Validează selectate”): stornarea aleasă înaintea facturii ei ar fi refuzată (factura e încă ciornă). Ordinea
    validării (`ordinea_validarii`) pune documentele de stornare după celelalte; restul rămâne în ordinea alegerii.
    MUTAȚIE: `ordinea_validarii` întoarce ordinea alegerii -> [stornarea, factura] -> pică."""
    from core import coada_api as c
    conn, cur, tid, cab, asist, valid = tx
    aid = _articol(conn)
    _ca(cur, asist)
    fid, contare, iesire = _factura(conn, aid)
    sid, contare_s, retur = _stornare_cu_retur(conn, fid)
    c.pune_notele_in_coada(conn, cab, tid, asist)
    cur.execute("SELECT payload->>'grup', min(id) FROM public.declaratii_coada WHERE tenant_id = %s GROUP BY 1", (tid,))
    el = dict(cur.fetchall())
    el_f, el_s = el["factura-%d" % fid], el["factura-%d" % sid]
    assert c.ordinea_validarii(conn, [el_s, 999999999, el_f]) == [999999999, el_f, el_s]
    assert c.ordinea_validarii(conn, [el_f, el_s]) == [el_f, el_s]


def test_def_619_validarea_in_masa_merge_in_ordinea_validarii(monkeypatch):
    """`coada_aproba_mai_multe` validează în ordinea dată de `coada_api.ordinea_validarii` (documentele stornate întâi); fiecare element
    trece o singură dată prin porțile aprobării, iar un refuz e întors, numit.
    MUTAȚIE: apelul `coada_api.ordinea_validarii` scos din `coada_aproba_mai_multe` -> ordinea alegerii -> pică."""
    from core import coada_api, erori as _erori, uc_coada, uc_comun
    chemate = []

    def aproba(i, _date, _ctx):
        chemate.append(i)
        if i == 3:
            raise _erori.FaraDrept("nu poți aproba o declarație pe care ai pregătit-o tu însuți")
    monkeypatch.setattr(uc_coada, "coada_aproba", aproba)
    monkeypatch.setattr(uc_comun, "_are_permisiune", lambda ctx, drept: True)
    monkeypatch.setattr(coada_api, "ordinea_validarii", lambda conn, ids: [i for i in ids if i != 2] + [2])   # 2 = o stornare
    r = uc_coada.coada_aproba_mai_multe([2, 3, 1], {"uid": 1, "firm": 1})
    assert chemate == [3, 1, 2] and r["validate"] == [1, 2], (r, chemate)
    assert [(x["id"], x["mesaj"]) for x in r["refuzate"]] == [(3, "nu poți aproba o declarație pe care ai pregătit-o tu însuți")], r


def test_def_619_vechi_documentele_validate_pe_jumatate_se_completeaza_pe_drumul_validarii(tx):
    """Datele existente (F1: F1A nr. 8 — contarea validată, ieșirea ciornă; F1A nr. 9 — returul validat, contarea stornării ciornă;
    F1A nr. 14 — contarea validată, ieșirea ciornă): `scripts/stoc2_619_documente_pe_jumatate.py` validează ciornele rămase ale
    documentelor cu o notă deja validată, pe drumul validării (`valideaza_documentul`: toate regulile ei), documentul stornat înaintea
    stornării. A doua rulare nu mai găsește nimic.
    MUTAȚIE: în script, cheia ordinii `(e_stornare(x[0]), x[0])` -> `(not e_stornare(x[0]), x[0])` (stornarea întâi) -> stornarea e
    refuzată (documentul stornat e încă ciornă) -> pică."""
    import importlib.util
    import os
    from core import jurnal_api as j
    conn, cur, tid, cab, asist, valid = tx
    d = _f1_ca_pe_productie(conn, cur)
    # starea de pe producție: returul validat înaintea ieșirii (drumul vechi, o notă) — exact ce oprește acum `valideaza_documentul`
    assert j.valideaza(conn, SCH, d["retur"]) == {"ok": True}
    assert _607_validat(cur) == D("-27.50")
    rad = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    spec = importlib.util.spec_from_file_location("stoc2_619", os.path.join(rad, "scripts", "stoc2_619_documente_pe_jumatate.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    rez = mod.completeaza(conn, SCH)
    assert rez == {"documente": 2, "validate": 2, "refuzate": []}, rez
    assert set(_stari(cur, set(d.values()) - {d["fid"], d["sid"]}).values()) == {"validata"}
    assert _607_validat(cur) == D("0.00")
    assert mod.completeaza(conn, SCH) == {"documente": 0, "validate": 0, "refuzate": []}
