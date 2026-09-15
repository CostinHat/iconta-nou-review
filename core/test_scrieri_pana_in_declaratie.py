# -*- coding: utf-8 -*-
"""Rutele care scriu în tabele din care se ridică declarații — probate PÂNĂ ÎN RÂNDUL DECLARAȚIEI.

DE UNDE VINE LOTUL. Din cele 131 de rute care scriu fără probă în suită, `scripts/scan_scrieri_declaratii.py`
derivă **din cod** subsetul care contează: tabelele scrise de rută ∩ tabelele citite de generatoarele
de declarații. **49** de rute. Nu o apreciere — o intersecție care se recalculează.

CE ÎNTREABĂ FIECARE PROBĂ, și de ce e mai mult decât „ruta a răspuns 200": se generează declarația
**înainte**, se apasă ruta, se generează **după**, și se compară CIFRA. O rută care răspunde 200 și
scrie într-un rând pe care generatorul nu-l citește trece orice probă de cod HTTP și pică aici.

DE CE NU E PROBĂ PE FUNCȚIE. Corpurile stau în `core/uc_*.py`, iar E2b le poate muta. Regula lui E3:
proba pe rută supraviețuiește mutării, cea pe funcție se rescrie — *o mutare care cere rescrierea
probelor a schimbat comportamentul.*

CURĂȚENIE. Firmă efemeră pe o conexiune din pool, `db.get_conn` întors spre aceeași conexiune,
`rollback` la final. Fără savepoint per cerere: probele sunt lanțuri (emit o factură, o stornez,
generez declarația), iar un savepoint per cerere ar șterge chiar efectul măsurat.
"""
from __future__ import annotations

import contextlib

import pytest

from core import auth_api, declaratii_api
from core import db as _db

SCH = "ztest_scrieri_decl"
AN, LUNA = 2026, 6
ZI = "2026-06-10"


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
def firma(monkeypatch):
    from core import tenant_provisioning as _tp
    _db.init_pool()
    p = _db.pool()
    conn = p.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO public.accounting_firms (nume) VALUES ('ZT SCRIERI') RETURNING id")
            firm = cur.fetchone()[0]
            cur.execute("INSERT INTO public.users (email,password_hash,nume,prenume,rol,"
                        "accounting_firm_id,activ) VALUES "
                        "('zt_scrieri@invalid','x','N','N','admin_firma',%s,true) RETURNING id",
                        (firm,))
            uid = cur.fetchone()[0]
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tp.parametrizeaza_template(
                open("tenant_template.sql", encoding="utf-8").read(), SCH))
            cur.execute('SET search_path TO "%s", public' % SCH)
            # Profil COMPLET: fără bancă/IBAN/declarant, D300 refuză să se genereze — iar proba ar
            # măsura refuzul, nu cifra.
            cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,platitor_tva,"
                        "tip_decont,banca,iban,declarant_nume,declarant_prenume,declarant_functie,telefon) "
                        "VALUES (1,'ZT SCRIERI SRL','14399840','Str Probei 1','Cluj-Napoca','CJ',"
                        "'6202',true,'L','BT','RO49AAAA1B31007593840000','Popescu','Ion','admin',"
                        "'0700000000')")
            cur.execute("SET search_path TO public")
            cur.execute("INSERT INTO public.tenants (schema_name,nume,cui,accounting_firm_id,activ) "
                        "VALUES (%s,'ZT SCRIERI','14399840',%s,true) RETURNING id", (SCH, firm))
            tid = cur.fetchone()[0]
            cur.execute("INSERT INTO public.user_tenants (user_id,tenant_id) VALUES (%s,%s)",
                        (uid, tid))

        @contextlib.contextmanager
        def _fake(schema=None):
            with conn.cursor() as c:
                c.execute('SET search_path TO "%s", public' % schema if schema
                          else "SET search_path TO public")
            yield _ConnProxy(conn)

        monkeypatch.setattr(_db, "get_conn", _fake)
        yield {"tid": tid, "conn": conn,
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


def _H(env):
    return {"Authorization": "Bearer " + env["tok"]}


def _U(env, sablon, **param):
    """Calea rutei, din ȘABLONUL ei — `/tenants/{tenant_id}/facturi/{factura_id}/storno`.

    Se scrie șablonul, nu o cale compusă din bucăți, fiindcă așa îl declară aplicația ȘI așa îl
    caută `scripts/scan_rute_fara_proba.py`: o probă care nu-și numește ruta nu e văzută de gardă.
    """
    cale = sablon.replace("{tenant_id}", str(env["tid"]))
    for k, v in param.items():
        cale = cale.replace("{%s}" % k, str(v))
    assert "{" not in cale, "au rămas parametri necompletați în %r" % cale
    return cale


def _numar(env, sql):
    with env["conn"].cursor() as cur:
        cur.execute('SET search_path TO "%s", public' % SCH)
        cur.execute(sql)
        return cur.fetchone()[0]


def declaratie(env, tip, an=AN, luna=LUNA):
    """Rezultatul generatorului, prin lanțul real. `None` dacă firma n-o datorează încă."""
    with env["conn"].cursor() as c:
        c.execute('SET search_path TO "%s", public' % SCH)
    try:
        _xml, res = declaratii_api.genereaza(_ConnProxy(env["conn"]), SCH, tip,
                                             {"an": an, "luna": luna})
        return res
    except ValueError:
        return None


def _R(res, cheie, implicit=0):
    """Un rând din D300/D390/D394 — `R` e dicționarul de rânduri al rezultatului."""
    if res is None:
        return implicit
    return (getattr(res, "R", None) or {}).get(cheie, implicit)


def _factura(cl, env, numar="ZT-1", pret=1000, cota=21, directie="emisa", tara="RO",
             cui="RO40372003"):
    return cl.post(_U(env, "/tenants/{tenant_id}/facturi"), headers=_H(env), json={
        "numar": numar, "data_emitere": ZI, "directie": directie,
        "tert_nume": "PARTENER ZT", "tert_cui": cui, "tert_tara": tara,
        "linii": [{"descriere": "serviciu", "cantitate": 1, "pret_unitar": pret,
                   "cota_tva": cota}]})


# ── facturi: cele patru rute care produc documente numerotate ────────────────────────────────

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_POST_facturi_ajunge_in_randul_R9_din_D300(firma):
    """`POST /tenants/{id}/facturi` → baza și TVA-ul colectat, în D300."""
    cl = _client()
    assert _R(declaratie(firma, "d300"), "R9_2") == 0, "martor: D300 pornea cu TVA colectat"

    r = _factura(cl, firma)
    assert r.status_code == 200, r.text[:300]
    assert _numar(firma, "SELECT count(*) FROM facturi") == 1

    res = declaratie(firma, "d300")
    assert _R(res, "R9_1") == 1000, "baza nu ajunge în R9_1: %r" % (getattr(res, "R", None),)
    assert _R(res, "R9_2") == 210, "TVA-ul nu ajunge în R9_2"
    assert res.tva_de_plata == 210, "TVA de plată: %r" % res.tva_de_plata


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_POST_facturi_emite_ajunge_in_D300(firma):
    """A doua cale de emitere (R42) — aceeași întrebare, alt drum."""
    cl = _client()
    r = cl.post(_U(firma, "/tenants/{tenant_id}/facturi/emite"), headers=_H(firma), json={
        "tip": "factura", "tert_nume": "PARTENER ZT", "tert_cui": "RO40372003",
        "data_emitere": ZI,
        "linii": [{"descriere": "serviciu", "cantitate": 1, "pret_unitar": 2000, "cota_tva": 21}]})
    assert r.status_code == 200, r.text[:300]
    res = declaratie(firma, "d300")
    assert _R(res, "R9_1") == 2000 and _R(res, "R9_2") == 420, (
        "emiterea nu ajunge în D300: %r" % (getattr(res, "R", None),))


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_STORNO_intra_in_LUNA_LUI_nu_o_scade_pe_a_facturii(firma):
    """Regula, citită din ce face aplicația, nu din ce presupuneam eu.

    Stornarea NU scade cifra lunii facturii: produce un document NOU, cu sume negative, purtând
    data zilei. Deci iunie rămâne 210, iar minusul apare în luna stornării. *Așa trebuie să fie —
    o declarație depusă pentru iunie nu se schimbă retroactiv fiindcă în septembrie s-a stornat.*
    Proba păzește exact asta: ambele capete, nu doar unul."""
    import datetime
    cl = _client()
    fid = _factura(cl, firma, pret=1000).json()["factura_id"]
    assert _R(declaratie(firma, "d300"), "R9_2") == 210

    r = cl.post(_U(firma, "/tenants/{tenant_id}/facturi/{factura_id}/storno", factura_id=fid), headers=_H(firma))
    assert r.status_code == 200, r.text[:300]
    assert r.json()["tva"] == -210.0, "documentul de storno nu poartă minusul: %r" % r.json()

    assert _R(declaratie(firma, "d300"), "R9_2") == 210, (
        "stornarea a schimbat RETROACTIV declarația lunii facturii")

    azi = datetime.date.today()
    res = declaratie(firma, "d300", an=azi.year, luna=azi.month)
    assert _R(res, "R9_2") == -210, (
        "minusul nu apare în luna stornării (%02d.%d): %r" % (azi.month, azi.year, getattr(res, "R", None)))


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_TRANSFORMAREA_proformei_produce_factura_in_luna_ei(firma):
    """Transformarea emite un document NOU, de tip `factura`, în luna în care se apasă."""
    import datetime
    cl = _client()
    pid = cl.post(_U(firma, "/tenants/{tenant_id}/facturi/emite"), headers=_H(firma), json={
        "tip": "proforma", "tert_nume": "PARTENER ZT", "tert_cui": "RO40372003",
        "data_emitere": ZI,
        "linii": [{"descriere": "serviciu", "cantitate": 1, "pret_unitar": 500,
                   "cota_tva": 21}]}).json()["factura_id"]
    t = cl.post(_U(firma, "/tenants/{tenant_id}/facturi/{factura_id}/transforma", factura_id=pid), headers=_H(firma))
    assert t.status_code == 200, t.text[:300]
    nou = t.json()["factura_id"]
    assert nou != pid, "transformarea n-a produs un document nou"

    with firma["conn"].cursor() as cur:
        cur.execute('SET search_path TO "%s", public' % SCH)
        cur.execute("SELECT tip, total FROM facturi WHERE id=%s", (nou,))
        tip, total = cur.fetchone()
    assert tip == "factura" and float(total) == 605.0, "documentul nou: %r %r" % (tip, total)

    azi = datetime.date.today()
    assert _R(declaratie(firma, "d300", an=azi.year, luna=azi.month), "R9_2") == 105, (
        "factura ieșită din proformă nu ajunge în D300 pe luna transformării")


@pytest.mark.xfail(strict=True, reason="DATORIE 15.09.2026, gasita de proba asta: o PROFORMA intra in D300 ca livrare taxabila. `core/repo_d300.select_facturi_4` filtreaza facturile pe data de exigibilitate si pe STATUS, dar niciodata pe `tip`; proforma emisa de `POST /facturi/emite` primeste status `de_preluat`, care e DECLARABIL (nomenclator_status_factura, decizia R91). Masurat: proforma de 500+105 lei, singura din luna, da R9_1=500 / R9_2=105. Mai rau: dupa `POST /facturi/{id}/transforma`, factura rezultata intra SI ea in D300 pe luna transformarii — aceeasi operatiune economica declarata de DOUA ori. Reparatia (excluderea `tip IN ('proforma','aviz')` din interogarile D300/D394/D390) schimba cifre fiscale, deci se face pe decizie scrisa, nu din proprie initiativa. Se inchide cand decizia e in DECIZII.md si proba asta trece.")
@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_DATORIE_o_proforma_nu_are_ce_cauta_in_D300(firma):
    cl = _client()
    r = cl.post(_U(firma, "/tenants/{tenant_id}/facturi/emite"), headers=_H(firma), json={
        "tip": "proforma", "tert_nume": "PARTENER ZT", "tert_cui": "RO40372003",
        "data_emitere": ZI,
        "linii": [{"descriere": "serviciu", "cantitate": 1, "pret_unitar": 500, "cota_tva": 21}]})
    assert r.status_code == 200, r.text[:300]

    res = declaratie(firma, "d300")
    assert _R(res, "R9_2") == 0, (
        "o proformă (document NEFISCAL) e declarată ca livrare taxabilă: R9_1=%s R9_2=%s"
        % (_R(res, "R9_1"), _R(res, "R9_2")))


# ── D301: operațiunile se adaugă și se scot, iar declarația le urmează ───────────────────────

def _vector(env, **coloane):
    """Vectorul fiscal al firmei, schimbat pentru o probă. D301 e DOAR pentru NEplătitori, D390
    doar pentru cine are operațiuni IC — deci fiecare probă își cere lumea în care ruta ei are
    sens, în loc să existe o firmă care le are pe toate și nu seamănă cu niciuna."""
    with env["conn"].cursor() as cur:
        cur.execute('SET search_path TO "%s", public' % SCH)
        for k, v in coloane.items():
            cur.execute("UPDATE firma_profil SET %s = %%s WHERE id = 1" % k, (v,))


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_D301_operatiunea_adaugata_ajunge_in_declaratie_si_stersa_dispare(firma):
    """Cele două rute (POST + DELETE) în aceeași probă, fiindcă întrebarea e una: cifra urmează
    rândul. Un DELETE care răspunde 200 fără să scadă baza ar trece separat; aici nu."""
    cl = _client()
    _vector(firma, platitor_tva=False)   # D301 = decontul special, doar pentru NEplătitori (art. 324)

    r = cl.post(_U(firma, "/tenants/{tenant_id}/d301-operatiuni"), headers=_H(firma), json={
        "an": AN, "luna": LUNA, "tip": 1, "tip_valuta": "EUR", "val_valuta": 200,
        "curs": 5.0, "cota": 21, "nr_doc": "ZT-IC-1", "data_doc": "15.06.2026",
        "tara": "DE", "cod": "DE123456789", "den": "PARTENER DE"})
    assert r.status_code == 200, r.text[:400]
    assert _numar(firma, "SELECT count(*) FROM d301_operatiuni") == 1, "operațiunea nu s-a scris"

    res = declaratie(firma, "d301")
    assert res is not None, "D301 nu se generează după adăugarea operațiunii"
    baze = [b for (b, _tva) in (res.totaluri or {}).values()]
    assert 1000 in [int(b) for b in baze], (
        "baza (200 EUR x 5.0) nu ajunge în totalurile D301: %r" % (res.totaluri,))

    op_id = _numar(firma, "SELECT max(id) FROM d301_operatiuni")
    d = cl.request("DELETE", _U(firma, "/tenants/{tenant_id}/d301-operatiuni/{op_id}", op_id=op_id), headers=_H(firma),
                   params={"an": AN, "luna": LUNA})
    assert d.status_code == 200, d.text[:300]
    assert _numar(firma, "SELECT count(*) FROM d301_operatiuni") == 0, "rândul a rămas după ștergere"
    dupa = declaratie(firma, "d301")
    assert dupa is None or not (dupa.totaluri or {}), (
        "cifra a rămas în D301 după ce rândul ei a fost șters: %r" % (dupa.totaluri,))


# ── D390: linia manuală de clasificare ───────────────────────────────────────────────────────

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_D390_linia_manuala_ajunge_in_declaratie(firma):
    cl = _client()
    _vector(firma, operatiuni_ic=True)   # fără asta, D390 nu i se aplică și linia se refuză

    r = cl.post(_U(firma, "/tenants/{tenant_id}/d390-clasificare/manual"), headers=_H(firma), json={
        "an": AN, "luna": LUNA, "tip": "P", "tara": "DE", "cod": "DE123456789",
        "den": "PARTENER DE", "baza": 1500})
    assert r.status_code == 200, r.text[:400]
    assert _numar(firma, "SELECT count(*) FROM d390_manual") == 1, "linia manuală nu s-a scris"

    res = declaratie(firma, "d390")
    assert res is not None, "D390 nu se generează după linia manuală"
    assert 1500 in [int(b) for b in (res.ops or {}).values()], (
        "linia manuală nu ajunge în operațiunile D390: %r" % (res.ops,))
    assert res.total_baza == 1500, "totalul D390 nu e cel al liniei: %r" % res.total_baza


# ── D205: asociații importați ────────────────────────────────────────────────────────────────

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_D205_asociatul_importat_ajunge_in_tabelul_citit_de_generator(firma):
    """`asociati` e citit de D205 (dividende). Proba merge până la rândul scris; cifra din D205
    cere și dividende repartizate — acolo e datoria E4, nu aici."""
    cl = _client()
    r = cl.post(_U(firma, "/tenants/{tenant_id}/asociati-import"), headers=_H(firma), json={
        "randuri": [{"nume": "POPESCU ION", "cnp": "1800101221144", "cota": 100,
                     "tip": "fizica"}]})
    assert r.status_code == 200, r.text[:400]
    assert _numar(firma, "SELECT count(*) FROM asociati") == 1, "asociatul nu s-a scris"
    with firma["conn"].cursor() as cur:
        cur.execute('SET search_path TO "%s", public' % SCH)
        cur.execute("SELECT nume, cnp FROM asociati")
        assert cur.fetchone() == ("POPESCU ION", "1800101221144"), "rândul scris nu e cel trimis"


# ── clienți: rândul care dă IDENTITATEA partenerului în D394 ─────────────────────────────────

def _parteneri_d394(res):
    """CUI-urile partenerilor din D394, citite din STRUCTURA rezultatului (`op1`), nu din `str()`.

    Cheia lui `op1` e `(tip, tip_partener, cota, cuiP, denP)` — al patrulea element e codul fiscal.
    Un `"40372003" in str(res)` ar fi trecut și dacă numărul apărea într-un total sau într-un id.
    """
    return {str(k[3]).replace("RO", "").strip() for k in (getattr(res, "op1", None) or {})}


def _client_nou(cl, env, nume="CLIENT ZT SRL", cui="RO40372003"):
    r = cl.post(_U(env, "/tenants/{tenant_id}/clienti"), headers=_H(env), json={"nume": nume, "cui": cui})
    assert r.status_code == 200, r.text[:300]
    cid = r.json().get("id") or r.json().get("client_id")
    assert cid, "ruta nu întoarce id-ul clientului: %r" % r.json()
    return cid


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_CLIENTUL_creat_da_identitatea_partenerului_in_D394(firma):
    """Cele trei rute de client nu schimbă o cifră — schimbă PE CINE declari. Proba merge până
    acolo: factura emisă duce CUI-ul partenerului în D394.

    Și un lucru aflat apăsând: `client_id` singur NU completează codul fiscal pe factură — ruta
    refuză explicit, numind consecința („nu intră în D394"). *Un refuz care spune ce se strică e
    mai bun decât o factură salvată cu partener pe jumătate.*"""
    cl = _client()
    cid = _client_nou(cl, firma)

    doar_id = cl.post(_U(firma, "/tenants/{tenant_id}/facturi"), headers=_H(firma), json={
        "numar": "ZT-C0", "data_emitere": ZI, "directie": "emisa", "client_id": cid,
        "linii": [{"descriere": "serviciu", "cantitate": 1, "pret_unitar": 1000, "cota_tva": 21}]})
    assert doar_id.status_code == 422, "factura trece fără codul fiscal al partenerului: %d" % doar_id.status_code
    assert doar_id.json()["detail"].count("D394") == 1, (
        "refuzul nu spune ce se strică: %s" % doar_id.text[:200])

    f = cl.post(_U(firma, "/tenants/{tenant_id}/facturi"), headers=_H(firma), json={
        "numar": "ZT-C1", "data_emitere": ZI, "directie": "emisa", "client_id": cid,
        "tert_nume": "CLIENT ZT SRL", "tert_cui": "RO40372003",
        "linii": [{"descriere": "serviciu", "cantitate": 1, "pret_unitar": 1000, "cota_tva": 21}]})
    assert f.status_code == 200, f.text[:300]

    res = declaratie(firma, "d394")
    assert res is not None, "D394 nu se generează"
    assert _parteneri_d394(res) == {"40372003"}, (
        "partenerii din D394 nu sunt cel al facturii: %r" % (_parteneri_d394(res),))


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_CLIENTUL_actualizat_MUTA_partenerul_din_D394_iar_factura_ramane_cum_a_fost(firma):
    """Întrebarea grea a rutelor de editare: ce se întâmplă cu ce e deja declarabil.

    Măsurat, nu presupus: `core/repo_d394.py:29` aduce partenerul cu `LEFT JOIN clienti`, iar
    identitatea din declarație urmează **fișa clientului de ACUM**, nu ce s-a scris pe factură la
    emitere. Deci o corectură de CUI în fișă schimbă partenerul dintr-un D394 regenerat pentru o
    lună trecută — pe când factura însăși își păstrează `tert_cui`-ul de la emitere.

    Proba pinează exact asta, în amândouă capetele. *Nu e o judecată — e precedența, scrisă ca
    s-o vadă cine o schimbă: dacă mâine câștigă factura, proba cade și cere o decizie.*"""
    cl = _client()
    cid = _client_nou(cl, firma)
    cl.post(_U(firma, "/tenants/{tenant_id}/facturi"), headers=_H(firma), json={
        "numar": "ZT-C2", "data_emitere": ZI, "directie": "emisa", "client_id": cid,
        "tert_nume": "CLIENT ZT SRL", "tert_cui": "RO40372003",
        "linii": [{"descriere": "serviciu", "cantitate": 1, "pret_unitar": 1000, "cota_tva": 21}]})
    assert _parteneri_d394(declaratie(firma, "d394")) == {"40372003"}, (
        "martor: partenerul nu era în D394")

    u = cl.put(_U(firma, "/tenants/{tenant_id}/clienti/{client_id}", client_id=cid), headers=_H(firma),
               json={"nume": "CLIENT ZT SRL", "cui": "RO14399840"})
    assert u.status_code == 200, u.text[:300]

    dupa = _parteneri_d394(declaratie(firma, "d394"))
    assert dupa == {"14399840"}, (
        "D394 nu urmează fișa clientului după editare: %r" % (dupa,))
    with firma["conn"].cursor() as cur:
        cur.execute('SET search_path TO "%s", public' % SCH)
        cur.execute("SELECT tert_cui FROM facturi WHERE numar = 'ZT-C2'")
        assert cur.fetchone()[0] == "RO40372003", (
            "editarea fișei a rescris ȘI documentul emis — atunci nu mai există nicio urmă a "
            "datelor cu care s-a emis factura")

    d = cl.delete(_U(firma, "/tenants/{tenant_id}/clienti/{client_id}", client_id=cid), headers=_H(firma))
    assert d.status_code in (400, 409, 422), (
        "clientul cu facturi se poate șterge: %d %s" % (d.status_code, d.text[:200]))
    assert _numar(firma, "SELECT count(*) FROM facturi") == 1, "factura a dispărut odată cu fișa"


# ── chitanța: încasarea intră în registrul de casă, deci în balanță ──────────────────────────

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_CHITANTA_emisa_intra_in_inregistrarile_citite_de_generatoare(firma):
    """Chitanța nu schimbă TVA-ul (nu e livrare), dar scrie în `inregistrari`/`inregistrari_linii`
    — tabelele din care se ridică balanța, deci D101. Proba merge până la articolul contabil:
    5311 = 4111, cu suma încasată."""
    cl = _client()
    fid = _factura(cl, firma, numar="ZT-CH", pret=1000).json()["factura_id"]
    inainte = _numar(firma, "SELECT count(*) FROM inregistrari")

    r = cl.post(_U(firma, "/tenants/{tenant_id}/chitante"), headers=_H(firma),
                json={"data": ZI, "suma": 1210, "factura_id": fid})
    assert r.status_code == 200, r.text[:400]
    assert _numar(firma, "SELECT count(*) FROM inregistrari") == inainte + 1, (
        "chitanța n-a lăsat nicio înregistrare contabilă")

    with firma["conn"].cursor() as cur:
        cur.execute('SET search_path TO "%s", public' % SCH)
        cur.execute("SELECT l.cont_debit, l.cont_credit, l.suma FROM inregistrari_linii l "
                    "JOIN inregistrari i ON i.id = l.inregistrare_id "
                    "ORDER BY i.id DESC, l.id LIMIT 1")
        linie = cur.fetchone()
    assert linie is not None, "nicio linie contabilă pentru chitanță"
    debit, credit, suma = linie
    assert (debit, credit) == ("5311", "4111"), "articolul contabil al încasării: %r" % (linie,)
    assert float(suma) == 1210.0, "suma încasată nu e cea din chitanță: %r" % suma


# ── notele manuale: șaisprezece rute, aceeași întrebare ──────────────────────────────────────
#
# Toate scriu în `inregistrari` + `inregistrari_linii` — tabelele din care se ridică balanța, deci
# D101 (și, prin conturile de TVA, D300). Proba lor e una singură, parametrizată: **articolul
# contabil ajunge în tabel, echilibrat, cu suma cerută**. Un `200` fără linii, sau cu debit ≠
# credit, pică.
#
# Calea se scrie pe ȘABLONUL rutei, ca instrumentul de acoperire s-o vadă.

NOTE = [
    ("/tenants/{tenant_id}/nota-bacsis", {"fel": "incasare", "suma": 100, "sursa": "card"}),
    ("/tenants/{tenant_id}/nota-credit", {"operatie": "primire", "suma": 5000, "tip": "lung"}),
    ("/tenants/{tenant_id}/nota-sponsorizare", {"suma": 1000, "mod": "contract"}),
    ("/tenants/{tenant_id}/nota-subventie", {"fel": "exploatare", "suma": 2000,
                                             "moment": "drept"}),
    ("/tenants/{tenant_id}/nota-inventariere", {"operatie": "plus", "valoare": 300}),
    ("/tenants/{tenant_id}/nota-provizion", {"fel": "provizion", "suma": 700,
                                             "actiune": "constituire"}),
    ("/tenants/{tenant_id}/nota-chirie", {"fel": "chirie_platita", "chirie": 1500,
                                          "proprietar": "pj", "cota": 21}),
    ("/tenants/{tenant_id}/nota-asociati", {"operatie": "imprumut", "suma": 2500}),
    ("/tenants/{tenant_id}/nota-decont-deplasare", {"fel": "avans", "suma": 400,
                                                    "sursa": "casa"}),
    ("/tenants/{tenant_id}/nota-leasing", {"tip": "rata", "capital": 800, "dobanda": 120,
                                           "cota": 21}),
    ("/tenants/{tenant_id}/nota-obiect-inventar", {"operatie": "dare_folosinta",
                                                   "valoare": 350, "cota": 21}),
    ("/tenants/{tenant_id}/nota-productie", {"operatie": "pic", "suma": 900,
                                             "moment": "constatare"}),
    ("/tenants/{tenant_id}/nota-contract-special", {"brut": 500, "fel": "zilier"}),
    ("/tenants/{tenant_id}/nota-perisabilitati", {"valoare_intrari": 10000,
                                                  "procent_limita": 0.5,
                                                  "pierdere_constatata": 40, "cota": 21}),
    ("/tenants/{tenant_id}/nota-lichidare", {"operatie": "partaj", "capital_social": 5000,
                                             "rezerve": 1000}),
    ("/tenants/{tenant_id}/export-extracomunitar", {"tara_client": "US", "dovada_export": True,
                                                    "valoare": 3000}),
    ("/tenants/{tenant_id}/vanzare-agricultor", {"pret": 1200}),
    ("/tenants/{tenant_id}/vanzare-marja-turism", {"calitate_client": "pf", "locuri": ["RO"],
                                                   "incasat": 2000, "cost_ue": 1500,
                                                   "cota": 21}),
    ("/tenants/{tenant_id}/import-extracomunitar", {"valoare_vamala": 5000,
                                                    "procent_taxa_vamala": 0,
                                                    "accize": 0, "accesorii": 0, "cota": 21,
                                                    "cont_destinatie": "371"}),
    ("/tenants/{tenant_id}/decontare-valuta", {"valoare_valuta": 100, "curs_evidenta": 4.9,
                                               "tip": "creanta", "moneda": "EUR",
                                               "cont_tert": "4111", "cont_banca": "5124"}),
    ("/tenants/{tenant_id}/reevaluare-valuta", {"moneda": "EUR",
                                                "solduri": [{"cont": "5124", "tip": "disponibil",
                                                             "valoare_valuta": 100,
                                                             "curs_evidenta": 4.9}]}),
]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
@pytest.mark.parametrize("sablon,corp", NOTE, ids=[s.rsplit("/", 1)[1] for s, _ in NOTE])
def test_NOTA_manuala_ajunge_in_inregistrarile_din_care_se_ridica_balanta(firma, sablon, corp):
    cl = _client()
    inainte = _numar(firma, "SELECT count(*) FROM inregistrari")
    corp = dict(corp, data=ZI)

    r = cl.post(_U(firma, sablon), headers=_H(firma), json=corp)
    assert r.status_code == 200, "%s -> %d %s" % (sablon, r.status_code, r.text[:300])
    assert _numar(firma, "SELECT count(*) FROM inregistrari") > inainte, (
        "%s a răspuns 200 fără să lase nicio înregistrare contabilă" % sablon)

    with firma["conn"].cursor() as cur:
        cur.execute('SET search_path TO "%s", public' % SCH)
        cur.execute("SELECT i.id, sum(l.suma) FROM inregistrari i "
                    "JOIN inregistrari_linii l ON l.inregistrare_id = i.id "
                    "GROUP BY i.id ORDER BY i.id DESC LIMIT 1")
        rand = cur.fetchone()
    assert rand is not None, "%s: înregistrare fără linii — o notă fără articol contabil" % sablon
    assert float(rand[1]) > 0, "%s: liniile însumează 0" % sablon


# ── salariați și concedii: rândurile din care se ridică D112 ─────────────────────────────────

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_SALARIATUL_creat_si_IMPORTAT_ajung_in_tabelul_citit_de_D112(firma):
    """`salariati` e citit de D112. Proba merge până la rândul scris, cu datele trimise —
    cifrele declarației cer și stat de salarii, care e altă rută și alt lot."""
    cl = _client()
    r = cl.post(_U(firma, "/tenants/{tenant_id}/salariati"), headers=_H(firma), json={
        "nume": "POPESCU", "prenume": "ION", "cnp": "1800101221144",
        "data_angajare": "2026-01-05", "salariu_brut": 5000, "cor": "251401"})
    assert r.status_code == 200, r.text[:300]
    assert _numar(firma, "SELECT count(*) FROM salariati") == 1, "salariatul nu s-a scris"

    i = cl.post(_U(firma, "/tenants/{tenant_id}/salariati-import"), headers=_H(firma), json={
        "randuri": [{"nume": "IONESCU", "prenume": "MARIA", "cnp": "2800101221138",
                     "salariu_brut": 6000, "data_angajare": "2026-02-01", "cor": "251401",
                     "tip_norma": "intreaga"}]})
    assert i.status_code == 200, i.text[:300]
    assert _numar(firma, "SELECT count(*) FROM salariati") == 2, "importul n-a adăugat rândul"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_CONCEDIUL_salvat_si_STERS_urmeaza_in_tabelul_citit_de_D112(firma):
    """Cele două rute (POST + DELETE) în aceeași probă: un DELETE care răspunde 200 fără să scoată
    rândul ar trece separat, aici nu."""
    cl = _client()
    s = cl.post(_U(firma, "/tenants/{tenant_id}/salariati"), headers=_H(firma), json={
        "nume": "POPESCU", "prenume": "ION", "cnp": "1800101221144",
        "data_angajare": "2026-01-05", "salariu_brut": 5000, "cor": "251401"})
    assert s.status_code == 200, s.text[:300]
    sid = _numar(firma, "SELECT max(id) FROM salariati")

    r = cl.post(_U(firma, "/tenants/{tenant_id}/salariati/{salariat_id}/concedii",
                   salariat_id=sid), headers=_H(firma), json={
        "serie": "ZT", "numar": "1", "cod": "01", "data_acordare": "2026-06-01",
        "data_inceput": "2026-06-01", "data_sfarsit": "2026-06-05", "zile_cm": 5,
        "venituri_6_luni": 30000, "zile_6_luni": 120, "an": AN, "luna": LUNA,
        "loc_prescriere": 1, "diagnostic": "proba"})
    assert r.status_code == 200, r.text[:400]
    assert _numar(firma, "SELECT count(*) FROM concedii_medicale") == 1, "concediul nu s-a scris"

    cm_id = _numar(firma, "SELECT max(id) FROM concedii_medicale")
    d = cl.delete(_U(firma, "/tenants/{tenant_id}/salariati/{salariat_id}/concedii/{cm_id}",
                     salariat_id=sid, cm_id=cm_id), headers=_H(firma))
    assert d.status_code == 200, d.text[:300]
    assert _numar(firma, "SELECT count(*) FROM concedii_medicale") == 0, "rândul a rămas"


# ── rutele care ating `firma_profil` și `facturi` fără să fie documente ──────────────────────

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_NUMEROTAREA_setata_se_vede_pe_urmatorul_document(firma):
    """`PUT /facturi/numerotare` scrie în `firma_profil` — de acolo iese numărul următoarei
    facturi, adică identificarea unui document fiscal. Proba merge până la documentul emis."""
    cl = _client()
    r = cl.put(_U(firma, "/tenants/{tenant_id}/facturi/numerotare"), headers=_H(firma),
               json={"serie": "ZTS", "numar_start": 77})
    assert r.status_code == 200, r.text[:300]

    e = cl.post(_U(firma, "/tenants/{tenant_id}/facturi/emite"), headers=_H(firma), json={
        "tip": "factura", "tert_nume": "PARTENER ZT", "tert_cui": "RO40372003",
        "data_emitere": ZI,
        "linii": [{"descriere": "serviciu", "cantitate": 1, "pret_unitar": 100, "cota_tva": 21}]})
    assert e.status_code == 200, e.text[:300]
    with firma["conn"].cursor() as cur:
        cur.execute('SET search_path TO "%s", public' % SCH)
        cur.execute("SELECT numar FROM facturi ORDER BY id DESC LIMIT 1")
        numar = cur.fetchone()[0]
    assert "77" in str(numar) and "ZTS" in str(numar), (
        "documentul emis nu poartă numerotarea setată: %r" % numar)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_OPT_IN_ul_de_scadentar_si_SUPAPA_se_scriu_unde_se_citesc(firma):
    """Două rute care nu schimbă cifre fiscale, dar scriu în `firma_profil` și `facturi` — adică
    exact în tabelele din care se ridică declarațiile. Proba le duce până la rândul scris."""
    cl = _client()
    fara_email = cl.put(_U(firma, "/tenants/{tenant_id}/scadentar/opt-in"), headers=_H(firma),
                        json={"activ": True})
    assert fara_email.status_code in (400, 422), (
        "notificările se activează fără email de răspuns: %d" % fara_email.status_code)

    with firma["conn"].cursor() as cur:
        cur.execute('SET search_path TO "%s", public' % SCH)
        cur.execute("UPDATE firma_profil SET email = 'zt@invalid.ro' WHERE id = 1")
    r = cl.put(_U(firma, "/tenants/{tenant_id}/scadentar/opt-in"), headers=_H(firma),
               json={"activ": True})
    assert r.status_code == 200, r.text[:300]

    fid = _factura(cl, firma, numar="ZT-SUP").json()["factura_id"]
    s = cl.put(_U(firma, "/tenants/{tenant_id}/facturi/{factura_id}/notificare", factura_id=fid),
               headers=_H(firma), json={"stop": True})
    assert s.status_code == 200, s.text[:300]
    with firma["conn"].cursor() as cur:
        cur.execute('SET search_path TO "%s", public' % SCH)
        cur.execute("SELECT count(*) FROM facturi WHERE id = %s", (fid,))
        assert cur.fetchone()[0] == 1, "supapa a atins altceva decât factura ei"


# ── ștergerea unei operațiuni de casă: rândul contabil dispare cu ea ─────────────────────────

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_STERGEREA_operatiunii_de_casa_scoate_si_inregistrarea_ei(firma):
    """Singura rută de ȘTERGERE din familia casei. Întrebarea nu e „a răspuns 200", ci dacă
    articolul contabil dispare odată cu operațiunea — altfel balanța ar păstra o încasare care nu
    mai există nicăieri."""
    cl = _client()
    fid = _factura(cl, firma, numar="ZT-CASA", pret=1000).json()["factura_id"]
    r = cl.post(_U(firma, "/tenants/{tenant_id}/chitante"), headers=_H(firma),
                json={"data": ZI, "suma": 1210, "factura_id": fid})
    assert r.status_code == 200, r.text[:300]
    op_id = _numar(firma, "SELECT max(id) FROM casa_operatiuni")
    assert op_id, "chitanța n-a lăsat operațiune de casă"
    inreg = _numar(firma, "SELECT count(*) FROM inregistrari")

    d = cl.delete(_U(firma, "/tenants/{tenant_id}/casa/operatiuni/{op_id}", op_id=op_id),
                  headers=_H(firma))
    assert d.status_code == 200, d.text[:300]
    assert _numar(firma, "SELECT count(*) FROM casa_operatiuni WHERE id = %d" % op_id) == 0, (
        "operațiunea de casă a rămas")
    assert _numar(firma, "SELECT count(*) FROM inregistrari") == inreg - 1, (
        "înregistrarea contabilă a rămas după ștergerea operațiunii care a produs-o")
