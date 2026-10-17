# -*- coding: utf-8 -*-
"""GARD — varianta (a), decizia Costin 13.10.2026 (verbatim în DECIZII): „Aplicația propune, la cererea contabilului, nota de închidere la
31.12: clasele 6/7 → 121 și regularizarea TVA 4426/4427 → 4423/4424. Nota apare ca propunere și intră în evidență numai după ce
contabilul o validează (R36).” + deficiența 242 (retestul 13.10.2026): „Afișează deodată toate motivele de oprire, fiecare cu acțiunea
lui, ca să le poată rezolva contabilul dintr-o singură trecere.”

TEMEI: OMFP 1802/2014 — contul 121 („În creditul contului 121 … la sfârșitul perioadei, soldul creditor al conturilor din clasa 7 (701 la
786)”; „În debitul … soldul debitor al conturilor de cheltuieli (601 la 698)”); contul 4423 („diferențele rezultate la finele perioadei
între taxa pe valoarea adăugată colectată mai mare (4427) și taxa pe valoarea adăugată deductibilă (4426)”); contul 4424 (invers); contul
4426 („sumele compensate la sfârșitul perioadei din taxa pe valoarea adăugată colectată (4427)”).
Schemă efemeră din `tenant_template.sql`, ROLLBACK."""
import datetime
import re
from decimal import Decimal as D

import pytest
from psycopg2.extras import RealDictCursor

from core import bilant as b, bilant_api as ba, db as _db, inchidere_an as ia, jurnal_api, motor, tenant_provisioning as _tp

_SCHEMA = "ztest_inchidere_an"


def _linii(note):
    return [(n["debit"], n["credit"], n["suma"]) for n in note]


def _nr_curent(cur, an):
    """(id, Nr. crt.) al notelor anului, cum le numerotează Registrul jurnal (`repo_contabilitate.jurnal_pe_an`)."""
    cur.execute("SELECT id, ROW_NUMBER() OVER (ORDER BY data, id) FROM inregistrari WHERE date_trunc('year', data) = %s",
                ("%d-01-01" % an,))
    return [tuple(r.values()) if isinstance(r, dict) else tuple(r) for r in cur.fetchall()]


def test_regularizarea_tva_compenseaza_si_trece_diferenta_in_4423_sau_4424():
    """Colectată 1.050 > deductibilă 300: 4427 = 4426 300, 4427 = 4423 750; deductibilă mai mare: 4424 = 4426; pe analitice, în ordine;
    un sold pe latura nefirească nu se atinge. MUTAȚIE: diferența colectată trecută în 4424 -> pică."""
    assert _linii(motor.regularizare_tva({"4427": (0, D(1050)), "4426": (D(300), 0)})) == [
        ("4427", "4426", D("300.00")), ("4427", "4423", D("750.00"))]
    assert _linii(motor.regularizare_tva({"4427.01": (0, D(100)), "4427.02": (0, D(50)), "4426": (D(400), 0)})) == [
        ("4427.01", "4426", D("100.00")), ("4427.02", "4426", D("50.00")), ("4424", "4426", D("250.00"))]
    assert motor.regularizare_tva({"4427": (D(10), 0), "4426": (0, D(5))}) == []


def test_inchiderea_din_solduri_lasa_clasele_6_7_fara_sold():
    """Fiecare cont 6 / 7 cu soldul lui: venitul cu sold creditor -> 7xx = 121, cheltuiala -> 121 = 6xx, 709 (debitor) -> 121 = 709,
    609 (creditor) -> 609 = 121; după aplicarea notelor, clasele 6 / 7 nu mai au sold, iar 121 = rezultatul. MUTAȚIE: latura inversată
    la soldul creditor -> pică."""
    s = {"704": (0, D(1000)), "709": (D(100), 0), "628": (D(200), 0), "609": (0, D(20)), "5121": (D(5), 0)}
    note = motor.inchidere_din_solduri(s)
    dupa = dict((k, D(v[0]) - D(v[1])) for k, v in s.items())
    dupa["121"] = D(0)
    for n in note:
        dupa[n["debit"]] = dupa.get(n["debit"], D(0)) + n["suma"]
        dupa[n["credit"]] = dupa.get(n["credit"], D(0)) - n["suma"]
    assert {k: v for k, v in dupa.items() if k[:1] in "67" and v} == {} and dupa["121"] == D(-720), dupa   # profit 720: 121 creditor


@pytest.fixture
def cur():
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as c:
                c.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                c.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                c.execute("SET search_path TO %s, public" % _SCHEMA)
                c.execute("INSERT INTO firma_profil (id, nume, cui) VALUES (1, 'PROBA SRL', '14399840') ON CONFLICT (id) DO NOTHING")
                c.execute("UPDATE firma_profil SET data_infiintare = '2025-01-10' WHERE id = 1")
                yield c
        finally:
            conn.rollback()


def _nota(c, zi, debit, credit, suma):
    c.execute("INSERT INTO inregistrari (data, status, sursa, descriere) VALUES (%s, 'validata', 't', 'Probă') RETURNING id", (zi,))
    c.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, %s, %s, %s)",
              (c.fetchone()["id"], debit, credit, suma))


def _anul(c):
    """Primul exercițiu (2025): capital 1.000; vânzare 1.000 + TVA 210; servicii 200 + TVA 42; încasări și plăți."""
    for d, cr, s in (("5121", "1012", 1000), ("4111", "704", 1000), ("4111", "4427", 210), ("628", "401", 200), ("4426", "401", 42),
                     ("5121", "4111", 1210), ("401", "5121", 242)):
        _nota(c, datetime.date(2025, 6, 30), d, cr, D(s))


def test_propunerea_e_ciorna_si_intra_in_evidenta_numai_dupa_validare(cur):
    """Propunerea la 31.12.2025: două note CIORNĂ (`sursa='inchidere_an'`, document intern „Notă de calcul”) — regularizarea TVA (4427 =
    4426 42, 4427 = 4423 168) și închiderea (704 = 121 1.000, 121 = 628 200); rezultatul 800. Cât sunt ciorne, bilanțul se oprește tot
    („Notele de închidere propuse așteaptă validarea”, 244); după validare (jurnalul), bilanțul se generează: F10 rd.43 = 800, iar 4423 (168) e datorie (rd.13). O nouă
    cerere înlocuiește o ciornă nevalidată (același document), iar după validare nu mai are ce închide. MUTAȚII: notele scrise
    `validata` -> pică (R36); regularizarea TVA scoasă -> 4427 rămâne fără loc -> pică."""
    _anul(cur)
    r = ia.propune(cur, _SCHEMA, 2025)
    assert [(n["descriere"], n["linii"]) for n in r["note"]] == [
        ("Regularizarea TVA la 31.12.2025", [("4427", "4426", "42.00"), ("4427", "4423", "168.00")]),
        ("Închiderea conturilor de venituri și cheltuieli în 121 la 31.12.2025", [("121", "628", "200.00"), ("704", "121", "1000.00")])], r
    assert r["rezultat"] == D(800) and all(re.match(r"Notă de calcul nr \d+ din 31\.12\.2025$", n["document"] or "") for n in r["note"]), r
    cur.execute("SELECT DISTINCT status, sursa FROM inregistrari WHERE id = ANY(%s)", ([n["id"] for n in r["note"]],))
    assert [tuple(x.values()) for x in cur.fetchall()] == [("ciorna", "inchidere_an")]
    with pytest.raises(b.BilantOprit, match=r"^Notele de închidere propuse așteaptă validarea: "):     # [244] ciornele nu sunt evidență
        ba.coloanele(cur, _SCHEMA, "s1005", 2025, [])
    r2 = ia.propune(cur, _SCHEMA, 2025)                                    # o nouă cerere: ciornele se înlocuiesc
    assert r2["inlocuite"] == [n["id"] for n in r["note"]] and [n["document"] for n in r2["note"]] == [n["document"] for n in r["note"]]
    for n in r2["note"]:
        assert jurnal_api.valideaza(cur.connection, _SCHEMA, n["id"]) == {"ok": True}
    _f10p, f10c, _f20p, _f30p = ba.coloanele(cur, _SCHEMA, "s1005", 2025, [])
    assert (f10c[43], f10c[13]) == (800, 168), f10c
    assert ia.propune(cur, _SCHEMA, 2025)["nimic"] is True


def test_def_242_toate_motivele_de_oprire_deodata(cur):
    """242 (retestul Costin 13.10.2026): „Bilanț F2 2026, S1005: apare numai motivul «închide clasele 6/7 în 121». Soldurile 401 D 500,
    4427 C 1.050 și 581 C 1.000 … nu se mai văd. Afișează deodată toate motivele de oprire, fiecare cu acțiunea lui”. Cauza: verificarea
    6 / 7 oprea generarea înaintea celei a soldurilor fără loc. Acum: un refuz cu toate motivele anului — clasele 6 / 7 (cu suma), soldurile
    fără loc (cu acțiunea fiecăruia) și rulajele pe care F20 nu le poate depune (741 sintetic) — numerotate; anii de închis pentru butonul
    propunerii. MUTAȚIE: refuzul la primul motiv (ca înainte) -> pică."""
    for d, cr, s in (("5121", "1012", 1000), ("401", "5121", 500), ("4111", "4427", 1050), ("5121", "581", 1000), ("4111", "704", 800),
                     ("5121", "741", 50)):
        _nota(cur, datetime.date(2025, 6, 30), d, cr, D(s))
    with pytest.raises(b.BilantOprit) as e:
        ba.coloanele(cur, _SCHEMA, "s1005", 2025, [])
    m = str(e.value)
    assert m.startswith("Bilanțul pe 2025 nu se poate genera — 3 motive; rezolvă-le pe toate, apoi generează din nou."), m
    assert re.findall(r"^(\d)\. ([^:]+):", m, re.M) == [("1", "Clasele 6 / 7"), ("2", "Soldurile de la 31.12 de mai jos nu au loc în bilanț"),
                                                       ("3", "Rulajele anului")], m
    assert re.findall(r"• (\d+) sold (debitor|creditor) ([\d.,]+) — ", m) == [("401", "debitor", "500,00"), ("4427", "creditor", "1.050,00"),
                                                                              ("581", "creditor", "1.000,00")], m
    assert re.findall(r"Rezultatul de închis: (profit [\d.,]+ lei)", m) == ["profit 850,00 lei"], m
    assert re.findall(r"^3\. Rulajele anului: contul (\d+) e folosit sintetic", m, re.M) == ["741"], m
    assert e.value.ani_inchidere == [2025], e.value.ani_inchidere


# ── proba rutei, pe HTTP, până în cifra declarației (clichetul `test_rute_probate`: rutele care scriu în tabele de declarație) ──────
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


_SCH_HTTP = "ztest_inchidere_an_http"


@pytest.fixture
def lume_http(monkeypatch):
    import contextlib
    from core import auth_api
    _db.init_pool()
    p = _db.pool()
    conn = p.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO public.accounting_firms (nume) VALUES ('ZTEST INCHIDERE AN') RETURNING id")
            firm = cur.fetchone()[0]
            cur.execute("INSERT INTO public.users (email,password_hash,nume,prenume,rol,accounting_firm_id,activ) VALUES "
                        "('ztest_inchidere_an@invalid','x','N','N','admin_firma',%s,true) RETURNING id", (firm,))
            uid = cur.fetchone()[0]
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH_HTTP)
            cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), _SCH_HTTP))
            cur.execute("SET search_path TO public")
            cur.execute("INSERT INTO public.tenants (schema_name,nume,cui,accounting_firm_id,activ) VALUES (%s,'TENANT INCHIDERE','14399840',%s,true) "
                        "RETURNING id", (_SCH_HTTP, firm))
            tid = cur.fetchone()[0]
            cur.execute("INSERT INTO public.user_tenants (user_id,tenant_id) VALUES (%s,%s)", (uid, tid))
            cur.execute('INSERT INTO "%s".firma_profil (id, nume, cui, data_infiintare) VALUES (1, \'PROBA SRL\', \'14399840\', '
                        "'2025-01-10') ON CONFLICT (id) DO UPDATE SET data_infiintare = EXCLUDED.data_infiintare" % _SCH_HTTP)
            for d, cr, s in (("5121", "1012", 1000), ("4111", "704", 1000), ("4111", "4427", 210), ("628", "401", 200), ("4426", "401", 42)):
                cur.execute('INSERT INTO "%s".inregistrari (data, status, sursa, descriere) VALUES (\'2025-06-30\', \'validata\', \'t\', '
                            "'Probă') RETURNING id" % _SCH_HTTP)
                cur.execute('INSERT INTO "%s".inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%%s,%%s,%%s,%%s)'
                            % _SCH_HTTP, (cur.fetchone()[0], d, cr, D(s)))

        @contextlib.contextmanager
        def _fake(schema=None):
            with conn.cursor() as c:
                c.execute('SET search_path TO "%s", public' % schema if schema else "SET search_path TO public")
            yield _ConnProxy(conn)

        monkeypatch.setattr(_db, "get_conn", _fake)
        yield {"tid": tid, "conn": conn,
               "tok": auth_api.emite_token({"id": uid, "rol": "admin_firma", "accounting_firm_id": firm})}
    finally:
        with conn.cursor() as c:
            c.execute("SET search_path TO public")
            c.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH_HTTP)
        conn.rollback()
        p.putconn(conn)


def _sold(lume, cont):
    with lume["conn"].cursor(cursor_factory=RealDictCursor) as cur:
        s = ba.sold_la(cur, _SCH_HTTP, datetime.date(2025, 12, 31)) or {}
    d, c = s.get(cont, (D(0), D(0)))
    return D(c) - D(d)


def test_ruta_propunerii_pana_in_rulajul_declaratiei(lume_http):
    """`POST /tenants/{id}/bilant-inchidere-propunere` prin HTTP: scrie notele CIORNĂ — rulajul lui 121 și al lui 4423 (din care se ridică
    D406 / bilanțul) rămâne ZERO până la validare; după validarea notelor (ruta jurnalului), 121 = 800 (creditor) și 4423 = 168. MUTAȚIE:
    notele scrise `validata` -> soldul nu mai e zero înainte de validare -> pică."""
    import main
    from fastapi.testclient import TestClient
    cl = TestClient(main.app)
    h = {"Authorization": "Bearer " + lume_http["tok"]}
    r = cl.post("/tenants/%d/bilant-inchidere-propunere?an=2025" % lume_http["tid"], json={}, headers=h)
    assert r.status_code == 200 and len(r.json()["note"]) == 2, (r.status_code, r.text[:300])
    assert (_sold(lume_http, "121"), _sold(lume_http, "4423")) == (D(0), D(0))
    for n in r.json()["note"]:
        rv = cl.post("/tenants/%d/jurnal/%d/valideaza" % (lume_http["tid"], n["id"]), json={}, headers=h)
        assert rv.status_code == 200, rv.text[:200]
    assert (_sold(lume_http, "121"), _sold(lume_http, "4423")) == (D(800), D(168))


# ── 243, 244 (retestul Costin 13.10.2026, comanda 14.10 pct.2, verbatim în DECIZII) ───────────────────────────────────────────────────
def _ciorna_inchidere(c, an, linii):
    """O ciornă de închidere scrisă direct (ca cele două de pe F2 din producție, propuse la 13.10 pe 31.12.2026)."""
    c.execute("INSERT INTO inregistrari (data, status, sursa, descriere, document_ref) VALUES (%s, 'ciorna', %s, %s, %s) RETURNING id",
              (datetime.date(an, 12, 31), ia.SURSA, ia.DESCRIERE_INCHIDERE % an, "Notă de calcul nr 1 din 31.12.%d" % an))
    nid = c.fetchone()["id"]
    for d, cr, s in linii:
        c.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, %s, %s, %s)", (nid, d, cr, s))
    return nid


def test_def_243_anul_neincheiat_nu_se_propune_si_nu_se_valideaza(cur):
    """243: „nota de închidere se poate propune pentru un an neîncheiat; operațiunile ulterioare o fac greșită, iar după validare nu se mai
    corectează. Fie permiți propunerea numai după 31.12, fie avertizezi și recalculezi înainte de validare. Alege varianta mai sigură.”
    Aleasă: numai după 31.12. Anul curent (neîncheiat): propunerea se refuză cu motivul; o ciornă de închidere deja scrisă pe 31.12 a
    anului curent (cazul F2) nu se validează; bilanțul nu oferă propunerea, spune de ce. MUTAȚIE: `an_incheiat` întors mereu True -> pică."""
    an = datetime.date.today().year
    for d, cr, s in (("4111", "704", 1000), ("628", "401", 200)):
        _nota(cur, datetime.date(an, 3, 10), d, cr, D(s))
    with pytest.raises(ValueError, match=r"^Nota de închidere pe %d se propune după 31\.12\.%d: " % (an, an)):
        ia.propune(cur, _SCHEMA, an)
    nid = _ciorna_inchidere(cur, an, [("704", "121", D(1000)), ("121", "628", D(200))])
    r = jurnal_api.valideaza(cur.connection, _SCHEMA, nid)
    assert r.get("cod") == "INCHIDERE_NEVALIDABILA" and r["eroare"].startswith(   # [258] Nr. crt. din jurnal, nu id-ul
        "Nota de închidere din 31.12.%d nu se validează înainte de 31.12.%d: până la sfârșitul anului"   # [302] ciorna n-are nr.
        % (an, an)), r
    cur.execute("SELECT status FROM inregistrari WHERE id = %s", (nid,))
    assert cur.fetchone()["status"] == "ciorna"
    with pytest.raises(b.BilantOprit) as e:
        ba.coloanele(cur, _SCHEMA, "s1005", an, [])
    assert "Anul %d nu s-a încheiat: se validează numai după 31.12.%d" % (an, an) in str(e.value), str(e.value)
    assert (e.value.ani_inchidere, [p["incheiat"] for p in e.value.propuse]) == ([], [False])


def test_def_243_nota_care_nu_mai_corespunde_soldurilor_nu_se_valideaza(cur):
    """243, același drum după 31.12: propunerea pe 2025, apoi o vânzare din noiembrie 2025 validată târziu (500). Nota de închidere 6 / 7
    nu se mai validează („nu mai corespunde soldurilor”), regularizarea TVA — încă a soldurilor — da; bilanțul spune că notele propuse nu
    mai corespund și oferă propunerea din nou; după ea și validare: profitul 1.300 în bilanț. MUTAȚIE: `corespunde` întors mereu True
    -> pică."""
    _anul(cur)
    r = ia.propune(cur, _SCHEMA, 2025)
    tva, inch = r["note"]
    _nota(cur, datetime.date(2025, 11, 30), "4111", "704", D(500))
    assert ia.ciorne(cur, _SCHEMA, 2025)["la_zi"] is False
    rv = jurnal_api.valideaza(cur.connection, _SCHEMA, inch["id"])
    assert rv.get("eroare", "").startswith("Nota de închidere din 31.12.2025 nu mai corespunde soldurilor de la 31.12.2025"
                                           ), rv   # [258] cum o numește Registrul jurnal, nu id-ul; [302] ciorna n-are număr
    assert jurnal_api.valideaza(cur.connection, _SCHEMA, tva["id"]) == {"ok": True}
    with pytest.raises(b.BilantOprit) as e:
        ba.coloanele(cur, _SCHEMA, "s1005", 2025, [])
    assert ([(p["an"], p["la_zi"], p["incheiat"]) for p in e.value.propuse], e.value.ani_inchidere) == ([(2025, False, True)], [2025]), \
        e.value                                                                # textul de pe ecran îl verifică e2e-ul 243
    r2 = ia.propune(cur, _SCHEMA, 2025)
    assert [n["linii"] for n in r2["note"]] == [[("121", "628", "200.00"), ("704", "121", "1500.00")]], r2
    assert jurnal_api.valideaza(cur.connection, _SCHEMA, r2["note"][0]["id"]) == {"ok": True}
    _f10p, f10c, _f20p, _f30p = ba.coloanele(cur, _SCHEMA, "s1005", 2025, [])
    assert f10c[43] == 1300, f10c


def test_def_244_dupa_propunere_motivul_e_validarea_notelor(cur):
    """244: „după propunere, mesajul roșu din Bilanț spune în continuare «închide clasele 6/7 în 121». Trebuie «Notele de închidere propuse
    așteaptă validarea», cu link direct spre ele, deschis pe luna lor.” Refuzul spune notele și luna (decembrie 2025) și le poartă (ecranul
    face din ele legătura spre Registrul jurnal); nu mai oferă propunerea (notele sunt la zi). MUTAȚIE: `propuse` nepasat din
    `bilant_api` -> pică."""
    _anul(cur)
    r = ia.propune(cur, _SCHEMA, 2025)
    with pytest.raises(b.BilantOprit) as e:
        ba.coloanele(cur, _SCHEMA, "s1005", 2025, [])
    m = str(e.value)
    # [258] notele numite cum le arată Registrul jurnal („nr. crt. N din 31.12.2025”, numerotarea `jurnal_pe_an`), nu prin id-ul intern
    # [302] notele propuse sunt ciorne: n-au număr până la validare
    assert m == ("Notele de închidere propuse așteaptă validarea: Regularizarea TVA la 31.12.2025 — nota din 31.12.2025; "
                 "Închiderea conturilor de venituri și cheltuieli în 121 la 31.12.2025 — nota din 31.12.2025. Se validează în "
                 "Registrul jurnal, luna decembrie 2025; apoi generează bilanțul."), m
    assert [(p["an"], p["luna"], [n["id"] for n in p["note"]], p["la_zi"]) for p in e.value.propuse] == [
        (2025, 12, [n["id"] for n in r["note"]], True)]
    assert e.value.ani_inchidere == [] and "închide clasele 6/7" not in m
