# -*- coding: utf-8 -*-
"""Ultimele PATRU rute cu clichet fiscal, probate pana in cifra declaratiei.

DE UNDE. `PREDARE_LANT.md` 0Z, lucrarea 3. Primele patru au primit proba in
`core/test_rute_stoc_pana_in_declaratie.py`; astea sunt cele ramase, si sunt cele care „cer fiecare
alta lume":

  POST /tenants/{id}/banca/reconciliere/{linie_id}/conteaza   — o linie de extras bancar
  POST /tenants/{id}/bonuri/{bon_id}/stinge                   — o chitanta de verificat
  POST /tenants/{id}/retete/descarca                          — o reteta cu ingrediente in stoc
  POST /migrare/importa                                       — un cabinet si un CUI

ACEEASI REGULA CA LA PRIMELE PATRU: proba merge pana in RANDUL DECLARATIEI, nu pana la `200`; iar
intre apasare si citire se VALIDEAZA nota, fiindca ciorna nu e evidenta. Si se masoara starea
INTERMEDIARA: inainte de validare, rulajul e ZERO. Fara capatul ala, o ruta care ar scrie direct
`validata` ar trece la fel de verde, iar poarta patru-ochi ar disparea fara sa spuna nimeni nimic.

`POST /migrare/importa` e ALTFEL, si se scrie de ce: ea nu scrie in schema unei firme — CREEAZA
firma. Deci „cifra declaratiei" pentru ea inseamna altceva: schema nascuta chiar poarta tabelele din
care se ridica declaratiile. Iar a doua ei directie e un REFUZ TIPAT: un CUI deja in portofoliu se
respinge cu `cod='deja_exista'`, nu cu o propozitie — codul spune el insusi de ce conteaza:
*„pana azi ecranul numara duplicatele potrivind PROZA … deci o reformulare a textului ar fi spus
tacit «0 firme erau deja in portofoliu» despre un import in care erau"*.

LUMEA: firma efemera din `tenant_template.sql`, o singura tranzactie anulata la final.
"""
from __future__ import annotations

import contextlib
import json
from decimal import Decimal

import pytest

from core import db as _db

SCH = "ztest_rute_3b"
AN, LUNA = 2026, 4
ZI = "%d-%02d-12" % (AN, LUNA)

CANT_INTRARE = Decimal("20")
PRET_INTRARE = Decimal("5.00")            # CMP 5,00
VAL_INTRARE = CANT_INTRARE * PRET_INTRARE  # 100,00
SUMA_EXTRAS = Decimal("250.00")
SUMA_CHITANTA = Decimal("70.00")
CUI_NOU = "95141537"                      # CUI real, cifra de control verificata
CUI_EXISTENT = "14399840"                 # cel al firmei din fixtura


class _ConnProxy:
    def __init__(self, real):
        object.__setattr__(self, "_real", real)

    def __getattr__(self, n):
        return getattr(self._real, n)

    def commit(self):
        pass

    def rollback(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def lume(monkeypatch):
    from core import auth_api, tenant_provisioning as _tp
    from core import uc_comun as _uc_comun
    _db.init_pool()
    p = _db.pool()
    conn = p.getconn()
    sablon = open("tenant_template.sql", encoding="utf-8").read()
    # SINGURUL lucru pe care `rollback` NU-l intoarce: o SECVENTA. `migrare/importa` creeaza o firma,
    # deci consuma `public.tenant_schema_seq`, iar contorul ei e o cifra PINATA in blocul generat din
    # `PREDARE_LANT.md` (masoara reciclarea numelor de schema — R79). Fara restaurare, proba asta ar
    # muta cifra cu +1 la FIECARE rulare a suitei, si ar inrosi poarta altcuiva maine.
    # *Aceeasi clasa cu „fixturi pe tabele partajate" din CLAUDE.md, pe obiectul care se uita cel mai
    # usor: cel care supravietuieste tranzactiei.*
    with conn.cursor() as c:
        c.execute("SELECT last_value, is_called FROM public.tenant_schema_seq")
        _seq_inainte = c.fetchone()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO public.accounting_firms (nume) VALUES ('ZTEST RUTE 3B') RETURNING id")
            firm = cur.fetchone()[0]
            cur.execute("INSERT INTO public.users (email,password_hash,nume,prenume,rol,"
                        "accounting_firm_id,activ) VALUES "
                        "('ztest_rute_3b@invalid','x','N','N','admin_firma',%s,true) RETURNING id",
                        (firm,))
            uid = cur.fetchone()[0]
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tp.parametrizeaza_template(sablon, SCH))
            cur.execute("SET search_path TO public")
            cur.execute("INSERT INTO public.tenants (schema_name,nume,cui,accounting_firm_id,activ) "
                        "VALUES (%s,'TENANT RUTE 3B',%s,%s,true) RETURNING id",
                        (SCH, CUI_EXISTENT, firm))
            tid = cur.fetchone()[0]
            cur.execute("INSERT INTO public.user_tenants (user_id,tenant_id) VALUES (%s,%s)",
                        (uid, tid))

            # ── lumea: articol cu stoc, reteta, linie de extras, chitanta ──────────────
            cur.execute('INSERT INTO "%s".articole (denumire, um, cont_stoc, cont_cheltuiala) '
                        "VALUES ('Faina proba','kg','301','601') RETURNING id" % SCH)
            aid = cur.fetchone()[0]
            cur.execute('INSERT INTO "%s".miscari_stoc (articol_id, data, tip, cantitate, '
                        "pret_unitar, valoare, document) "
                        "VALUES (%%s,%%s,'intrare',%%s,%%s,%%s,'NIR-3b')" % SCH,
                        (aid, "%d-%02d-01" % (AN, LUNA), CANT_INTRARE, PRET_INTRARE, VAL_INTRARE))
            cur.execute('INSERT INTO "%s".retete (denumire, pret_fara_tva) '
                        "VALUES ('Paine proba', 10) RETURNING id" % SCH)
            rid = cur.fetchone()[0]
            cur.execute('INSERT INTO "%s".retete_linii (reteta_id, articol_id, cantitate) '
                        "VALUES (%%s,%%s,%%s)" % SCH, (rid, aid, Decimal("0.500")))
            cur.execute('INSERT INTO "%s".extras_linii (data, descriere, suma, tip, status, '
                        "nota_propusa) VALUES (%%s,'Incasare client proba',%%s,'incasare','nou',%%s) "
                        "RETURNING id" % SCH,
                        (ZI, SUMA_EXTRAS, json.dumps({"debit": "5121", "credit": "4111",
                                                      "suma": str(SUMA_EXTRAS)})))
            lid = cur.fetchone()[0]
            cur.execute('INSERT INTO "%s".bonuri (comerciant, cui, data, total, tip, status) '
                        "VALUES ('FURNIZOR PROBA','14399840',%%s,%%s,'chitanta','de_verificat') "
                        "RETURNING id" % SCH, (ZI, SUMA_CHITANTA))
            bid = cur.fetchone()[0]

        @contextlib.contextmanager
        def _fake(schema=None):
            with conn.cursor() as c:
                c.execute('SET search_path TO "%s", public' % schema if schema
                          else "SET search_path TO public")
            yield _ConnProxy(conn)

        monkeypatch.setattr(_db, "get_conn", _fake)
        # Sablonul e citit la PORNIREA aplicatiei; sub TestClient poate lipsi. Se pune explicit, ca
        # `migrare/importa` sa refuze din alt motiv decat „template indisponibil".
        monkeypatch.setattr(_uc_comun, "_TENANT_TEMPLATE", sablon)
        # ANAF nu se cheama dintr-o proba: reteaua n-are ce cauta in suita, iar un esec de retea ar
        # arata ca un defect al rutei.
        monkeypatch.setattr(_tp, "date_din_anaf", lambda cui: {})
        monkeypatch.setattr(_tp, "precompleteaza_din_anaf",
                            lambda conn, schema, date, seteaza_nume=True: None)
        yield {"tid": tid, "firm": firm, "conn": conn, "aid": aid, "rid": rid, "lid": lid,
               "bid": bid, "schema": SCH,
               "tok": auth_api.emite_token({"id": uid, "rol": "admin_firma",
                                            "accounting_firm_id": firm})}
    finally:
        with conn.cursor() as c:
            c.execute("SET search_path TO public")
            c.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        # Schema creata de `migrare/importa` NU se sterge aici pe nume: e o schema al carei nume nu-l
        # stiu dinainte, iar `rollback`-ul o ia oricum — DDL-ul e tranzactional in Postgres, si tot
        # ce s-a scris sta pe ACEEASI conexiune.
        conn.rollback()
        # ... dar secventa NU se intoarce la rollback. Se pune inapoi explicit, pe alta conexiune,
        # DUPA rollback — altfel restaurarea ar fi ea insasi anulata.
        with _db.pool().getconn() as c2:
            try:
                with c2.cursor() as cc:
                    cc.execute("SELECT setval('public.tenant_schema_seq', %s, %s)", _seq_inainte)
                c2.commit()
            finally:
                _db.pool().putconn(c2)
        p.putconn(conn)


def _client():
    import main
    from fastapi.testclient import TestClient
    return TestClient(main.app)


def _H(lume):
    return {"Authorization": "Bearer " + lume["tok"]}


def _rulaj(lume, cont):
    from core import control_incrucisat as _ci
    return _ci.rulaje_luna(_ConnProxy(lume["conn"]), SCH, AN, LUNA, [cont])[cont]


def _valideaza_notele(lume, cl):
    with lume["conn"].cursor() as cur:
        cur.execute("SELECT id FROM \"%s\".inregistrari WHERE status='ciorna' ORDER BY id" % SCH)
        ids = [r[0] for r in cur.fetchall()]
    for i in ids:
        r = cl.post("/tenants/%d/jurnal/%d/valideaza" % (lume["tid"], i), json={}, headers=_H(lume))
        assert r.status_code == 200, (i, r.status_code, r.text[:200])
    return len(ids)


# ─────────────────────────── banca / reconciliere / conteaza ───────────────────────────

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_LINIA_DE_EXTRAS_contata_ajunge_in_rulajul_bancii(lume):
    """`POST /tenants/{id}/banca/reconciliere/{linie_id}/conteaza` — incasare 250,00.

    Linia poarta o notă propusa (`5121 = 4111`), deci contarea o foloseste. Se verifica AMANDOUA
    conturile SI trecerea liniei pe `contat`: un rulaj corect peste o linie ramasa `nou` ar
    insemna ca aceeasi incasare se poate conta a doua oara.
    """
    cl = _client()
    r = cl.post("/tenants/%d/banca/reconciliere/%d/conteaza" % (lume["tid"], lume["lid"]),
                json={}, headers=_H(lume))
    assert r.status_code == 200, r.text[:300]

    assert _rulaj(lume, "5121")["debit"] == Decimal("0"), "ciorna a ajuns deja in declaratie"
    assert _valideaza_notele(lume, cl) == 1
    assert _rulaj(lume, "5121")["debit"] == SUMA_EXTRAS
    assert _rulaj(lume, "4111")["credit"] == SUMA_EXTRAS
    with lume["conn"].cursor() as cur:
        cur.execute('SELECT status FROM "%s".extras_linii WHERE id=%%s' % SCH, (lume["lid"],))
        assert cur.fetchone()[0] == "contat"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_A_DOUA_contare_a_aceleiasi_linii_se_REFUZA(lume):
    """Directia cealalta: aceeasi incasare nu se poate conta de doua ori. Fara proba asta,
    idempotenta ar fi o intentie scrisa in cod, nu o proprietate masurata."""
    cl = _client()
    assert cl.post("/tenants/%d/banca/reconciliere/%d/conteaza" % (lume["tid"], lume["lid"]),
                   json={}, headers=_H(lume)).status_code == 200
    r2 = cl.post("/tenants/%d/banca/reconciliere/%d/conteaza" % (lume["tid"], lume["lid"]),
                 json={}, headers=_H(lume))
    assert r2.status_code == 400, (r2.status_code, r2.text[:200])
    with lume["conn"].cursor() as cur:
        cur.execute("SELECT count(*) FROM \"%s\".inregistrari WHERE sursa='banca'" % SCH)
        assert cur.fetchone()[0] == 1, "a doua contare a produs inca o nota"


# ─────────────────────────── bonuri / stinge ───────────────────────────

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_CHITANTA_stinsa_ajunge_in_rulajul_casei(lume):
    """`POST /tenants/{id}/bonuri/{bon_id}/stinge` — plata furnizor 70,00 prin registrul de casa.

    Nota e `401 = 5311` (`casa_api.CONTURI['plata_furnizor']`). Se verifica si ca s-a nascut
    operatiunea de casa: o notă fara operatiune ar lasa registrul de casa si contabilitatea sa spuna
    lucruri diferite despre aceeasi plata.
    """
    cl = _client()
    r = cl.post("/tenants/%d/bonuri/%d/stinge" % (lume["tid"], lume["bid"]),
                json={"data": ZI, "suma": float(SUMA_CHITANTA), "partener": "FURNIZOR PROBA",
                      "cui": "14399840"}, headers=_H(lume))
    assert r.status_code == 200, r.text[:300]
    assert r.json()["ok"] is True and r.json()["nota_id"], r.json()

    assert _rulaj(lume, "401")["debit"] == Decimal("0")
    assert _valideaza_notele(lume, cl) == 1
    assert _rulaj(lume, "401")["debit"] == SUMA_CHITANTA
    assert _rulaj(lume, "5311")["credit"] == SUMA_CHITANTA
    with lume["conn"].cursor() as cur:
        cur.execute("SELECT categorie, suma FROM \"%s\".casa_operatiuni" % SCH)
        assert cur.fetchall() == [("plata_furnizor", SUMA_CHITANTA)]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_un_BON_care_nu_e_chitanta_se_REFUZA(lume):
    """A doua directie, pe poarta de tip: registrul de casa nu stinge un bon de magazin."""
    cl = _client()
    with lume["conn"].cursor() as cur:
        cur.execute('UPDATE "%s".bonuri SET tip=%%s WHERE id=%%s' % SCH, ("bon", lume["bid"]))
    r = cl.post("/tenants/%d/bonuri/%d/stinge" % (lume["tid"], lume["bid"]),
                json={"data": ZI, "suma": float(SUMA_CHITANTA)}, headers=_H(lume))
    assert r.status_code == 400, (r.status_code, r.text[:200])
    with lume["conn"].cursor() as cur:
        cur.execute("SELECT count(*) FROM \"%s\".casa_operatiuni" % SCH)
        assert cur.fetchone()[0] == 0


# ─────────────────────────── retete / descarca ───────────────────────────

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_CONSUMUL_DE_RETETA_ajunge_in_rulajul_cheltuielii(lume):
    """`POST /tenants/{id}/retete/descarca` — 10 portii x 0,500 kg la CMP 5,00 = 25,00.

    Nota e cumulata pe pereche de conturi (`601 = 301`), iar stocul scade cu 5 kg. Se verifica
    AMANDOUA: o notă corecta peste un stoc neatins ar insemna ca ingredientul s-a cheltuit de doua ori.
    """
    cl = _client()
    r = cl.post("/tenants/%d/retete/descarca" % lume["tid"],
                json={"reteta_id": lume["rid"], "portii": 10, "data": ZI}, headers=_H(lume))
    assert r.status_code == 200, r.text[:300]

    assert _rulaj(lume, "601")["debit"] == Decimal("0")
    assert _valideaza_notele(lume, cl) == 1
    assert _rulaj(lume, "601")["debit"] == Decimal("25.00")
    assert _rulaj(lume, "301")["credit"] == Decimal("25.00")
    with lume["conn"].cursor() as cur:
        cur.execute("SELECT COALESCE(SUM(CASE WHEN tip='intrare' THEN cantitate ELSE -cantitate END),0) "
                    'FROM "%s".miscari_stoc WHERE articol_id=%%s' % SCH, (lume["aid"],))
        assert Decimal(str(cur.fetchone()[0])) == CANT_INTRARE - Decimal("5.000")


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_o_RETETA_peste_stocul_existent_se_REFUZA(lume):
    """A doua directie: 100 de portii cer 50 kg, iar in stoc sunt 20.

    Se cere sa EXISTE un motiv si sa nu ramana nicio urma — nu un anumit CUVANT in mesaj. Calitatea
    formularii are gardile ei (diacritice, limbaj, `interactiune_scan`); o aserțiune pe text scrisa
    aici ar pazi formularea de langa lucru, nu lucrul. *Poarta a respins exact forma asta in lotul
    dinainte; lectia se aplica din prima, nu dupa a doua respingere.*
    """
    cl = _client()
    r = cl.post("/tenants/%d/retete/descarca" % lume["tid"],
                json={"reteta_id": lume["rid"], "portii": 100, "data": ZI}, headers=_H(lume))
    assert r.status_code == 422, (r.status_code, r.text[:200])
    assert (r.json().get("detail") or "").strip(), "refuz fara niciun motiv scris"
    with lume["conn"].cursor() as cur:
        cur.execute("SELECT count(*) FROM \"%s\".inregistrari" % SCH)
        assert cur.fetchone()[0] == 0, "un refuz a lasat totusi o nota"
        cur.execute("SELECT count(*) FROM \"%s\".miscari_stoc WHERE tip='iesire'" % SCH)
        assert cur.fetchone()[0] == 0, "un refuz a scos totusi din stoc"


# ─────────────────────────── migrare / importa ───────────────────────────

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_IMPORTUL_creeaza_o_firma_cu_tabelele_din_care_se_ridica_declaratiile(lume):
    """`POST /migrare/importa` — singura din cele opt care nu scrie intr-o firma, ci CREEAZA una.

    Deci „ajunge in declaratie" inseamna, pentru ea, ca schema nascuta chiar poarta tabelele din
    care se ridica declaratiile. Se cer pe nume, nu „exista niste tabele": o schema pe jumatate
    creata ar trece o numaratoare.
    """
    cl = _client()
    r = cl.post("/migrare/importa",
                json={"firme": [{"cui": CUI_NOU, "denumire": "FIRMA IMPORTATA PROBA"}]},
                headers=_H(lume))
    assert r.status_code == 200, r.text[:300]
    corp = r.json()
    assert corp["total"] == 1 and not corp["erori"], corp
    tid_nou = corp["creat"][0]["tenant_id"]

    with lume["conn"].cursor() as cur:
        cur.execute("SET search_path TO public")
        cur.execute("SELECT schema_name, cui FROM public.tenants WHERE id=%s", (tid_nou,))
        schema_noua, cui = cur.fetchone()
        assert cui and cui.endswith(CUI_NOU[-6:]), cui
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema=%s",
                    (schema_noua,))
        tabele = {t[0] for t in cur.fetchall()}
    cerute = {"facturi", "factura_linii", "inregistrari", "inregistrari_linii", "mijloace_fixe",
              "miscari_stoc", "articole", "salariati", "reevaluari"}
    assert tabele >= cerute, "lipsesc din schema nouă: %s" % sorted(cerute - tabele)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_un_CUI_deja_in_portofoliu_se_respinge_TIPAT(lume):
    """A doua directie, si codul spune singur de ce conteaza: *„pana azi ecranul numara duplicatele
    potrivind PROZA … deci o reformulare a textului ar fi spus tacit «0 firme erau deja in
    portofoliu» despre un import in care erau"*. Deci se aseartă pe COD, nu pe mesaj.

    Codul sta sub cheia **`regula`**, nu `cod` — si nu e un amanunt: `migrare_api.respinge` isi
    scrie in docstring chiar ciocnirea de vocabular care a dus acolo (*„pana azi cheia «motiv» purta
    CODUL in importuri si TEXTUL in afirmatii — acelasi nume, doua intelesuri"*). Prima forma a
    probei astea a cerut `cod`; asteptarea era a mea.
    """
    cl = _client()
    r = cl.post("/migrare/importa",
                json={"firme": [{"cui": CUI_EXISTENT, "denumire": "TENANT RUTE 3B"}]},
                headers=_H(lume))
    assert r.status_code == 200, r.text[:300]
    corp = r.json()
    assert corp["total"] == 0 and len(corp["erori"]) == 1, corp
    assert corp["erori"][0]["regula"] == "deja_exista", corp["erori"][0]
    # si textul pentru om exista, si e ACELASI cu `mesaj` — contractul scris in `respinge`
    assert corp["erori"][0]["motiv"] == corp["erori"][0]["mesaj"], corp["erori"][0]


# ─────────────────────────── anti-vacuu ───────────────────────────

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_ANTI_VACUU_lumea_chiar_e_pregatita(lume):
    """Fiecare proba de mai sus ar trece pe zerouri egale daca lumea n-ar exista."""
    with lume["conn"].cursor() as cur:
        for tabel, cate in (("articole", 1), ("retete", 1), ("retete_linii", 1),
                            ("extras_linii", 1), ("bonuri", 1), ("inregistrari", 0)):
            cur.execute('SELECT count(*) FROM "%s".%s' % (SCH, tabel))
            assert cur.fetchone()[0] == cate, tabel
        cur.execute("SELECT COALESCE(SUM(cantitate),0) FROM \"%s\".miscari_stoc WHERE tip='intrare'" % SCH)
        assert Decimal(str(cur.fetchone()[0])) == CANT_INTRARE
