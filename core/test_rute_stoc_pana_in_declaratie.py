# -*- coding: utf-8 -*-
"""Patru din cele opt rute cu clichet fiscal, probate PANA IN CIFRA DECLARATIEI.

DE UNDE VINE. `PREDARE_LANT.md` 0Z, lucrarea 3: *„cele 8 rute cu clichet care ating cifre de
declaratie"* — cele opt din cele 88 care scriu fara proba in suita SI ating tabele din care se ridica
declaratii. Predarea spune, tot ea, de ce n-aveau proba: *„fiecare cere o lume pregatita — de-aia
n-au proba, nu din uitare"*. Aici se pregateste lumea aia, o data, pentru patru dintre ele:

  POST /tenants/{id}/stocuri/iesire
  POST /tenants/{id}/stocuri/inventar
  POST /tenants/{id}/stocuri/reclasificare
  POST /tenants/{id}/reevaluare-imobilizare

CE INTREABA, si de ce NU codul HTTP. `core/test_rute_probate.py` spune despre subsetul asta:
*„o ruta de aici greseste intr-un FISIER DEPUS LA ANAF, nu pe un ecran. De-aia probele lui merg pana
in randul declaratiei, nu pana la 200."* Deci fiecare proba de mai jos face trei lucruri, in ordine:

  1. apasa RUTA, prin HTTP, cu jeton real si rol real;
  2. **valideaza nota** pe care ruta o produce — toate trei rutele de stoc scriu CIORNA, iar ciorna
     NU e evidenta: declaratia citeste numai note validate;
  3. citeste cifra din **declaratie** — rulajul contului din `d406`/`control_incrucisat`, adica exact
     sursa din care se ridica `GeneralLedgerEntries`.

CE NU DEMONSTREAZA, declarat: corectitudinea CMP-ului pe metode (aia e `core/test_stocuri_*.py`) si
structura XML a D406 (aia e `core/test_d406*.py`). Aici se probeaza ca efectul rutei **ajunge** acolo.

LUMEA, declarata: firma efemera din `tenant_template.sql`, un articol de marfa cu o intrare de
10 buc x 10,00 lei (CMP 10,00), si un mijloc fix de 6.000 lei pe 60 de luni. Toate scrierile stau
intr-o singura tranzactie, anulata la final — `db.get_conn` e intors spre aceeasi conexiune, tiparul
din `core/test_portal_bon.py`.
"""
from __future__ import annotations

import contextlib
from decimal import Decimal

import pytest

from core import db as _db

SCH = "ztest_rute_stoc"
AN, LUNA = 2026, 3
ZI = "%d-%02d-15" % (AN, LUNA)

# Lumea, in cifre (se refac cu creionul):
CANT_INTRARE = Decimal("10")
PRET_INTRARE = Decimal("10.00")        # CMP = 10,00
VAL_INTRARE = CANT_INTRARE * PRET_INTRARE   # 100,00
MF_VALOARE = Decimal("6000")
MF_DNF = 60


class _ConnProxy:
    """Conexiunea reala, cu `commit`/`rollback` inerte: totul ramane in tranzactia probei."""

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
    _db.init_pool()
    p = _db.pool()
    conn = p.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO public.accounting_firms (nume) VALUES ('ZTEST RUTE STOC') RETURNING id")
            firm = cur.fetchone()[0]
            cur.execute("INSERT INTO public.users (email,password_hash,nume,prenume,rol,"
                        "accounting_firm_id,activ) VALUES "
                        "('ztest_rute_stoc@invalid','x','N','N','admin_firma',%s,true) RETURNING id",
                        (firm,))
            uid = cur.fetchone()[0]
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tp.parametrizeaza_template(
                open("tenant_template.sql", encoding="utf-8").read(), SCH))
            cur.execute("SET search_path TO public")
            cur.execute("INSERT INTO public.tenants (schema_name,nume,cui,accounting_firm_id,activ) "
                        "VALUES (%s,'TENANT RUTE STOC','14399840',%s,true) RETURNING id", (SCH, firm))
            tid = cur.fetchone()[0]
            cur.execute("INSERT INTO public.user_tenants (user_id,tenant_id) VALUES (%s,%s)",
                        (uid, tid))

            # ── lumea pregatita ────────────────────────────────────────────────
            cur.execute('INSERT INTO "%s".articole (denumire, um, cont_stoc, cont_cheltuiala) '
                        "VALUES ('Marfa proba','buc','371','607') RETURNING id" % SCH)
            aid = cur.fetchone()[0]
            cur.execute('INSERT INTO "%s".miscari_stoc (articol_id, data, tip, cantitate, '
                        "pret_unitar, valoare, document) "
                        "VALUES (%%s,%%s,'intrare',%%s,%%s,%%s,'NIR-proba')" % SCH,
                        (aid, "%d-%02d-01" % (AN, LUNA), CANT_INTRARE, PRET_INTRARE, VAL_INTRARE))
            cur.execute('INSERT INTO "%s".mijloace_fixe (cod, denumire, cont_imobilizare, '
                        "cont_amortizare, valoare, rezidual, dnf_luni, data_pif, metoda) "
                        "VALUES ('MF-PROBA','Utilaj proba','2131','2813',%%s,0,%%s,%%s,'liniara') "
                        "RETURNING id" % SCH,
                        (MF_VALOARE, MF_DNF, "%d-01-15" % (AN - 1)))
            mfid = cur.fetchone()[0]

        @contextlib.contextmanager
        def _fake(schema=None):
            with conn.cursor() as c:
                c.execute('SET search_path TO "%s", public' % schema if schema
                          else "SET search_path TO public")
            yield _ConnProxy(conn)

        monkeypatch.setattr(_db, "get_conn", _fake)
        yield {"tid": tid, "conn": conn, "aid": aid, "mfid": mfid, "schema": SCH,
               "tok": auth_api.emite_token({"id": uid, "rol": "admin_firma",
                                            "accounting_firm_id": firm})}
    finally:
        with conn.cursor() as c:
            c.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        conn.rollback()
        p.putconn(conn)


def _client():
    import main
    from fastapi.testclient import TestClient
    return TestClient(main.app)


def _H(lume):
    return {"Authorization": "Bearer " + lume["tok"]}


def _rulaj(lume, cont):
    """Cifra DIN DECLARATIE: rulajul contului pe luna, prin `control_incrucisat.rulaje_luna` —
    sursa unica de rulaje din repo, chiar cea din care se ridica `GeneralLedgerEntries`.

    Citeste DOAR note validate. De-aia fiecare proba valideaza nota inainte de a citi aici: o ciorna
    nu e evidenta, iar o proba care ar citi ciorne ar spune ca efectul a ajuns in declaratie cand el
    de fapt n-a ajuns.
    """
    from core import control_incrucisat as _ci
    r = _ci.rulaje_luna(_ConnProxy(lume["conn"]), SCH, AN, LUNA, [cont])
    return r[cont]


def _valideaza_notele(lume, cl):
    """Valideaza TOATE ciornele firmei, prin ruta aplicatiei. Intoarce cate a validat.

    Prin RUTA, nu prin `UPDATE`: altfel proba ar sari peste chiar poarta care transforma o propunere
    in evidenta — si ar afirma despre declaratie ceva ce aplicatia nu face.
    """
    with lume["conn"].cursor() as cur:
        cur.execute("SELECT id FROM \"%s\".inregistrari WHERE status='ciorna' ORDER BY id" % SCH)
        ids = [r[0] for r in cur.fetchall()]
    for i in ids:
        r = cl.post("/tenants/%d/jurnal/%d/valideaza" % (lume["tid"], i), json={}, headers=_H(lume))
        assert r.status_code == 200, (i, r.status_code, r.text[:200])
    return len(ids)


# ─────────────────────────── stocuri/iesire ───────────────────────────

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_IESIREA_de_stoc_ajunge_in_rulajul_contului_de_cheltuiala(lume):
    """`POST /tenants/{id}/stocuri/iesire` — 3 buc la CMP 10,00 -> nota `607 = 371`, 30,00.

    Se citesc AMANDOUA conturile: numai `607` ar trece si daca stocul nu s-ar fi descarcat.
    """
    cl = _client()
    r = cl.post("/tenants/%d/stocuri/iesire" % lume["tid"],
                json={"articol_id": lume["aid"], "data": ZI, "cantitate": 3,
                      "document": "AVIZ-1"}, headers=_H(lume))
    assert r.status_code == 200, r.text[:300]
    # Pe VALOARE, nu pe sirul ei: ruta intoarce CMP-ul cu patru zecimale (`10.0000`), fiindca asa
    # il tine `miscari_stoc.pret_unitar`. Prima forma a probei astepta `10.00` — asteptarea era a
    # mea, nu a codului.
    assert Decimal(r.json()["cmp"]) == PRET_INTRARE, r.json()
    assert Decimal(r.json()["valoare"]) == Decimal("30.00"), r.json()

    # inainte de validare, declaratia NU vede nimic — ciorna nu e evidenta
    assert _rulaj(lume, "607")["debit"] == Decimal("0")
    assert _valideaza_notele(lume, cl) == 1
    assert _rulaj(lume, "607")["debit"] == Decimal("30.00")
    assert _rulaj(lume, "371")["credit"] == Decimal("30.00")


# ─────────────────────────── stocuri/inventar ───────────────────────────

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_MINUSUL_de_inventar_ajunge_in_rulaj(lume):
    """`POST /tenants/{id}/stocuri/inventar` — faptic 8 fata de scriptic 10 -> minus de 2 buc.

    Temei: OMFP 1802/2014, functiunea conturilor 371/607 (minusul se scoate pe cheltuiala).
    """
    cl = _client()
    r = cl.post("/tenants/%d/stocuri/inventar" % lume["tid"],
                json={"data": ZI, "linii": [{"articol_id": lume["aid"], "faptic": 8}]},
                headers=_H(lume))
    assert r.status_code == 200, r.text[:300]
    assert _valideaza_notele(lume, cl) >= 1
    assert _rulaj(lume, "607")["debit"] == Decimal("20.00"), "minusul de 2 x 10,00 n-a ajuns"
    assert _rulaj(lume, "371")["credit"] == Decimal("20.00")


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_un_inventar_FARA_LINII_se_REFUZA(lume):
    """Directia cealalta, si e o regula scrisa: *„un inventar fara linii nu e o inventariere fara
    diferente — e o inventariere care nu s-a facut"*. Fara proba asta, `200` pe un corp gol ar
    arata identic cu o inventariere curata."""
    cl = _client()
    r = cl.post("/tenants/%d/stocuri/inventar" % lume["tid"], json={"data": ZI, "linii": []},
                headers=_H(lume))
    # 422, nu 400: refuzul vine ca `DateInvalide`, iar harta `main._COD_EROARE` il duce acolo.
    # Asteptarea de 400 era a mea.
    assert r.status_code == 422, (r.status_code, r.text[:200])
    # Se cere sa EXISTE un motiv, nu un anumit CUVANT in el: calitatea mesajului are gardile ei
    # (diacritice, limbaj, `interactiune_scan`), iar un `"inventariere" in mesaj` scris aici ar pazi
    # formularea de langa lucru, nu lucrul — clichetul aserțiunilor pe text l-a si respins.
    assert (r.json().get("detail") or "").strip(), "refuz fara niciun motiv scris"
    with lume["conn"].cursor() as cur:
        cur.execute("SELECT count(*) FROM \"%s\".inregistrari" % SCH)
        assert cur.fetchone()[0] == 0, "un inventar refuzat a lasat totusi o nota"


# ─────────────────────────── stocuri/reclasificare ───────────────────────────

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_RECLASIFICAREA_muta_soldul_intre_conturi_de_stoc(lume):
    """`POST /tenants/{id}/stocuri/reclasificare` — marfa 371 -> materie prima 301.

    Nota mută soldul la CMP (`301 = 371`, 100,00), iar **cantitatea nu se atinge**. Se verifica si
    ca articolul poarta contul nou: fara asta, o nota corecta peste un articol neschimbat ar trece.
    """
    cl = _client()
    r = cl.post("/tenants/%d/stocuri/reclasificare" % lume["tid"],
                json={"articol_id": lume["aid"], "cont_stoc_nou": "301",
                      "cont_cheltuiala_nou": "601", "data": ZI}, headers=_H(lume))
    assert r.status_code == 200, r.text[:300]
    assert _valideaza_notele(lume, cl) == 1
    assert _rulaj(lume, "301")["debit"] == VAL_INTRARE
    assert _rulaj(lume, "371")["credit"] == VAL_INTRARE
    with lume["conn"].cursor() as cur:
        cur.execute('SELECT cont_stoc, cont_cheltuiala FROM "%s".articole WHERE id=%%s' % SCH,
                    (lume["aid"],))
        assert cur.fetchone() == ("301", "601")
        cur.execute("SELECT COALESCE(SUM(CASE WHEN tip='intrare' THEN cantitate ELSE -cantitate END),0) "
                    'FROM "%s".miscari_stoc WHERE articol_id=%%s' % SCH, (lume["aid"],))
        assert Decimal(str(cur.fetchone()[0])) == CANT_INTRARE, "reclasificarea a atins cantitatea"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_RECLASIFICAREA_pe_acelasi_cont_se_REFUZA(lume):
    """A doua directie: contul neschimbat nu e o reclasificare, si nu trebuie sa produca nota."""
    cl = _client()
    r = cl.post("/tenants/%d/stocuri/reclasificare" % lume["tid"],
                json={"articol_id": lume["aid"], "cont_stoc_nou": "371", "data": ZI},
                headers=_H(lume))
    assert r.status_code == 400, r.status_code
    with lume["conn"].cursor() as cur:
        cur.execute("SELECT count(*) FROM \"%s\".inregistrari" % SCH)
        assert cur.fetchone()[0] == 0


# ─────────────────────────── reevaluare-imobilizare ───────────────────────────

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_REEVALUAREA_ajunge_pe_registru_SI_in_rulaj_dupa_validare(lume):
    """`POST /tenants/{id}/reevaluare-imobilizare` — a patra ruta a subsetului.

    E aceeasi afirmatie ca `core/test_reevaluare_registru.py`, dar apasata **prin HTTP**: acolo se
    probeaza use-case-ul si lantul pe schema efemera, aici RUTA. *Clichetul fiscal scade doar cand
    ruta insasi are proba in suita — nu cand o are functia de sub ea.*

    Activ 6.000 / 60 de luni, PIF 15.01.<AN-1>: la 15.03.<AN> au trecut 14 luni x 100,00 = 1.400,00
    amortizare cumulata, deci valoarea neta e 4.600,00. Reevaluat la 5.000 -> diferenta 400,00.
    """
    cl = _client()
    r = cl.post("/tenants/%d/reevaluare-imobilizare" % lume["tid"],
                json={"data": ZI, "operatie": "reevaluare", "mijloc_fix_id": lume["mfid"],
                      "valoare_justa": 5000}, headers=_H(lume))
    assert r.status_code == 200, r.text[:300]
    corp = r.json()
    assert corp["valoare_neta"] == "4600.00", corp
    assert corp["diferenta"] == "400.00", corp
    assert corp["amortizare_eliminata"] == "1400.00", corp

    def _valoare_registru():
        with lume["conn"].cursor() as cur:
            cur.execute('SELECT valoare FROM "%s".mijloace_fixe WHERE id=%%s' % SCH, (lume["mfid"],))
            return Decimal(str(cur.fetchone()[0]))

    assert _valoare_registru() == MF_VALOARE, "ciorna a miscat registrul"
    assert _valideaza_notele(lume, cl) == 1
    assert _valoare_registru() == Decimal("5000")
    # si in evidenta: eliminarea cumulatei (2813 = 2131) plus diferenta (2131 = 105)
    assert _rulaj(lume, "2813")["debit"] == Decimal("1400.00")
    assert _rulaj(lume, "105")["credit"] == Decimal("400.00")


# ─────────────────────────── anti-vacuu pe lumea insasi ───────────────────────────

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_ANTI_VACUU_lumea_chiar_e_pregatita(lume):
    """O lume goala ar face fiecare proba de mai sus sa treaca pe zerouri egale. *O comparatie
    intre doua zerouri nu discrimineaza nimic.*"""
    with lume["conn"].cursor() as cur:
        cur.execute("SELECT count(*) FROM \"%s\".articole" % SCH)
        assert cur.fetchone()[0] == 1
        cur.execute("SELECT count(*) FROM \"%s\".miscari_stoc WHERE tip='intrare'" % SCH)
        assert cur.fetchone()[0] == 1
        cur.execute("SELECT count(*) FROM \"%s\".mijloace_fixe" % SCH)
        assert cur.fetchone()[0] == 1
        cur.execute("SELECT count(*) FROM \"%s\".inregistrari" % SCH)
        assert cur.fetchone()[0] == 0, "lumea porneste cu note — probele n-ar mai masura ce au produs"
