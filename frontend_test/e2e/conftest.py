# -*- coding: utf-8 -*-
"""Testele de capăt la capăt ale deficiențelor (DEFICIENTE.md, comanda Costin 09.10.2026 pct.8): pașii contabilului, în browser, pe
aplicația pornită de `scripts/e2e_poarta.py` din ce se comite, pe baza de TEST. Fiecare test se numește `test_def_<nr>_<ce>` — numărul
din DEFICIENTE.md — și lasă o captură `<nr>_<ce>.png` în `E2E_CAPTURI`. Datele puse de un test se scot în același test (`curata`).
"""
import datetime as _dt
import json
import os
import sys

import pytest

BAZA = os.environ.get("PROBA_BAZA", "http://127.0.0.1:8019")
CAPTURI = os.environ.get("E2E_CAPTURI", "/tmp/e2e_capturi")
LAT, INALT = 1700, 1000


def zile_de_acum(inceput):
    """[13.10.2026 — plasa a trecut de miezul nopții: testul 167 compara „Generată la 13.10.2026 00:01” cu AZI = 12.10.2026, fixat la
    importul modulului] „Azi” al unui lucru pe care aplicația îl datează ACUM (data implicită a unui ecran, momentul generării, jurnalul)
    = ziua de la importul testului SAU ziua de acum, dacă rularea a trecut între timp de miezul nopții. Un AZI fixat la import se compară
    singur numai cu date pe care testul însuși le-a dat aplicației (marcate `# AZI-dat-de-test`); gard `core/test_e2e_azi_acum.py`."""
    return sorted({inceput, _dt.date.today()})


def _db():
    from core import db
    try:
        db.init_pool()
    except Exception:  # noqa: BLE001 — deja inițializat
        pass
    return db


def sesiune(email):
    """Scriptul care pune tokenul unui cont de TEST în sessionStorage (pe drumul aplicației: `sesiune_pentru_user`)."""
    from core import auth_api
    db = _db()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM public.users WHERE email=%s", (email,))
            u = cur.fetchone()
        s = auth_api.sesiune_pentru_user(conn, u[0]) if u else None
        conn.rollback()
    assert s and s.get("ok"), "contul de test %s nu e disponibil" % email
    return ("sessionStorage.setItem('iconta_token'," + json.dumps(s["token"]) + ");"
            "sessionStorage.setItem('iconta_user'," + json.dumps(json.dumps(s["user"])) + ");")


def sql(q, p=()):
    """Interogare pe baza de TEST, comisă (pregătirea / curățenia datelor unui test)."""
    db = _db()
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute(q, p)
        r = cur.fetchall() if cur.description else None
        c.commit()
    return r


def nr_crt(schema, nid):
    """[258] Cum vede contabilul nota `nid` în Registrul jurnal: „nr. crt. N din ZZ.LL.AAAA” — numărul curent pe anul notei, după
    (data, id), orice stare (aceeași numerotare ca `repo_contabilitate.jurnal_pe_an`), calculat AICI, independent de `eticheta_nota`."""
    nr, data = sql('SELECT x.nr, x.data FROM (SELECT i.id, i.data, ROW_NUMBER() OVER (ORDER BY i.data, i.id) AS nr FROM "%s".inregistrari i '
                   'JOIN "%s".inregistrari n ON n.id = %%s AND date_trunc(\'year\', i.data) = date_trunc(\'year\', n.data)) x '
                   'WHERE x.id = %%s' % (schema, schema), (nid, nid))[0]
    return "nr. crt. %d din %s" % (nr, data.strftime("%d.%m.%Y"))


@pytest.fixture(scope="session")
def browser():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True)
        yield b
        b.close()


class Ecran:
    """O pagină cu un cont logat + ce a observat (erori JS, cereri eșuate) + captura numită după deficiență."""

    def __init__(self, pg, nume_test):
        self.pg, self.erori, self.cereri_rele = pg, [], []
        self.nume = nume_test[len("test_def_"):] if nume_test.startswith("test_def_") else nume_test
        pg.on("pageerror", lambda e: self.erori.append(str(e)))
        pg.on("response", lambda r: self.cereri_rele.append((r.status, r.url)) if r.status >= 500 else None)

    def acasa(self):
        self.pg.goto(BAZA + "/", wait_until="domcontentloaded")
        self.pg.wait_for_selector(".cab-grila, .cab-card", timeout=30000)
        self.pg.wait_for_timeout(500)

    def firma(self, nume="Comert Micro TVA"):
        self.acasa()
        self.pg.click("button.cab-card:has([data-cheie='firme'])")
        self.pg.wait_for_timeout(600)
        if self.pg.query_selector("#opt-existente"):
            self.pg.click("#opt-existente")
        self.pg.wait_for_selector("#firme-lista button.firme-rand", timeout=20000)
        self.pg.locator("#firme-lista button.firme-rand", has_text=nume).first.click()
        self.pg.wait_for_selector("#fa-facturi", timeout=20000)

    def fereastra(self):
        """Textul ferestrei din față (ce citește contabilul)."""
        return self.pg.evaluate("() => { const f = [...document.querySelectorAll('.fereastra')].pop(); "
                                "return f ? f.innerText : document.body.innerText; }")

    def captura(self, sufix="", intreaga=False):
        os.makedirs(CAPTURI, exist_ok=True)
        cale = os.path.join(CAPTURI, "%s%s.png" % (self.nume, ("_" + sufix) if sufix else ""))
        self.pg.screenshot(path=cale, full_page=intreaga)
        return cale


def _ecran(browser, request, email):
    ctx = browser.new_context(viewport={"width": LAT, "height": INALT})
    ctx.add_init_script(sesiune(email))
    e = Ecran(ctx.new_page(), request.node.name)
    yield e
    erori, rele = list(e.erori), list(e.cereri_rele)
    ctx.close()
    assert not erori, "erori JavaScript pe ecran: %s" % erori[:3]
    assert not rele, "cereri cu răspuns 5xx: %s" % rele[:3]


@pytest.fixture()
def patron(browser, request):
    """Contabilul-șef al cabinetului de test (Cabinet Contabil Prisma SRL)."""
    yield from _ecran(browser, request, "patron@prisma-cont.test")


@pytest.fixture()
def asistent(browser, request):
    """Asistentul cabinetului de test („Poate pregăti”)."""
    yield from _ecran(browser, request, "asistent@prisma-cont.test")


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def ai_pregateste(*raspunsuri):
    """[comanda Costin 09.10.2026 pct.7, AI simulat în plasă] Răspunsurile pe care „modelul” le dă, în ordine, aplicației de probă
    (`core.ai_client`, `ICONTA_AI_SIMULAT`, pus de `scripts/e2e_poarta.py`); jurnalul prompturilor se golește. Întoarce directorul."""
    import json
    d = os.environ["ICONTA_AI_SIMULAT"]
    json.dump(list(raspunsuri), open(os.path.join(d, "raspunsuri.json"), "w", encoding="utf-8"), ensure_ascii=False)
    if os.path.exists(os.path.join(d, "prompturi.jsonl")):
        os.remove(os.path.join(d, "prompturi.jsonl"))
    return d


def ai_prompturi():
    """Ce a primit „modelul” de la ultima `ai_pregateste`, în ordine."""
    import json
    cale = os.path.join(os.environ["ICONTA_AI_SIMULAT"], "prompturi.jsonl")
    return [json.loads(x) for x in open(cale, encoding="utf-8")] if os.path.exists(cale) else []


def cui_cu_control(baza8):
    """CUI valid din 8 cifre de bază + cifra de control (algoritmul oficial, CLAUDE.md „Date de test”) — verificat, nu inventat."""
    from core.tenant_provisioning import cui_valid
    ch = [7, 5, 3, 2, 1, 7, 5, 3, 2]
    corp = str(baza8).rjust(9, "0")
    r = sum(int(corp[i]) * ch[i] for i in range(9)) * 10 % 11
    cui = str(baza8) + str(0 if r == 10 else r)
    assert cui_valid(cui), cui
    return cui


from curatenie import PREFIX_FIRMA  # noqa: E402


def _scoate_firmele_e2e(tenant_id=None):
    """Firma sintetică a rulării (`tenant_id`), sau — fără argument — resturile rulărilor întrerupte mai vechi de 3 ore (rulările în
    paralel nu-și șterg firmele una alteia). Ștergerea e `curatenie.scoate` (o definiție, folosită și de rulator după oprire)."""
    import curatenie
    db = _db()
    with db.get_conn() as c, c.cursor() as cur:
        if tenant_id is not None:
            cur.execute("SELECT id, schema_name FROM public.tenants WHERE id = %s AND nume LIKE %s", (tenant_id, PREFIX_FIRMA + "%"))
        else:
            cur.execute("SELECT id, schema_name FROM public.tenants WHERE nume LIKE %s AND creat_la < now() - interval '3 hours'",
                        (PREFIX_FIRMA + "%",))
        firme = cur.fetchall()
    os.makedirs(os.path.dirname(curatenie.registru_firme()), exist_ok=True)
    with open(curatenie.registru_firme(), "a") as f:          # și orice firmă scoasă aici (inclusiv cele create într-un fișier de
        f.writelines("%s %s\n" % (t, sc) for t, sc in firme)  # teste) se mai scoate o dată după oprirea aplicației
    curatenie.scoate(db, firme)


def alege_perioada(pg, an, luna=None, trim=None, zona=""):
    """Pasul 1 al Declarațiilor: anul și perioada, după selectorul pe care îl arată aplicația pentru firma și tipul alese — luna, sau
    trimestrul ei când declarația e trimestrială (D406 la neplătitor, deficiența C2). Cerută o perioadă și fără niciun selector, pică:
    altfel s-ar genera în tăcere perioada implicită a ecranului, nu cea cerută (prins 10.10.2026: test_def_136 cerea 09/2026 și a primit
    T4). Singurul loc din plasă care alege perioada — `core/test_e2e_perioada.py`."""
    pg.fill(zona + "#dec-an", str(an))
    pg.dispatch_event(zona + "#dec-an", "change")
    if luna is None and trim is None:
        return
    if luna is not None and pg.locator(zona + "#dec-luna").count():
        pg.select_option(zona + "#dec-luna", str(luna))
    elif pg.locator(zona + "#dec-trim").count():
        pg.select_option(zona + "#dec-trim", str(trim or (luna - 1) // 3 + 1))
    else:
        raise AssertionError("perioada cerută (luna %s, trim %s) fără selector pe ecran" % (luna, trim))


def firma_noua(tip_firma="srl"):
    """O firmă NOUĂ a cabinetului de test, creată pe drumul aplicației (`provision_tenant`, cu `tip_firma` — „pfa” pentru partida
    simplă) și trecută în registrul de curățenie: {tenant_id, schema, nume, cabinet_id}. Generator: cine o cere o scoate la final
    (`_scoate_firmele_e2e(tenant_id)`)."""
    import io as _io
    import time as _t
    from core import tenant_provisioning as tp
    db = _db()
    nume = "%s %d %s" % (PREFIX_FIRMA, int(_t.time() * 1000) % 10000000, "PFA" if tip_firma == "pfa" else "SRL")
    rad = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sql_t = _io.open(os.path.join(rad, "tenant_template.sql"), encoding="utf-8").read()
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute("SELECT id, accounting_firm_id FROM public.users WHERE email = 'patron@prisma-cont.test'")
        uid, cab = cur.fetchone()
        r = tp.provision_tenant(c, nume, cui_cu_control(90000000 + int(_t.time() * 1000) % 9000000), cab, uid, sql_t, tip_firma=tip_firma)
        c.commit()
    import curatenie
    os.makedirs(os.path.dirname(curatenie.registru_firme()), exist_ok=True)
    with open(curatenie.registru_firme(), "a") as f:          # rulatorul o scoate încă o dată după oprirea aplicației
        f.write("%s %s\n" % (r["tenant_id"], r["schema_name"]))
    try:
        yield {"tenant_id": r["tenant_id"], "schema": r["schema_name"], "nume": nume, "cabinet_id": cab}
    finally:
        _scoate_firmele_e2e(r["tenant_id"])


@pytest.fixture(scope="module")
def firma_e2e():
    """{tenant_id, schema, nume, cabinet_id}: o firmă NOUĂ a cabinetului de test (`firma_noua`), scoasă la final. Testele care scriu
    date scriu aici, nu pe firmele de test comune. UNA PE FIȘIER (09.10.2026, prins la prima rulare integrală a plasei): o firmă pe
    toată rularea lăsa un bloc să moștenească starea altuia (seria de facturi dusă la 9 de blocul C refuza „numărul de start 1” al
    blocului E) — fiecare fișier își are firma lui, ca atunci când e rulat singur."""
    _scoate_firmele_e2e()
    yield from firma_noua()


CONTURI_COMUNE = ("patron@prisma-cont.test", "asistent@prisma-cont.test")
_DREPTURI = ("poate_pregati", "poate_valida", "poate_depune")


@pytest.fixture(scope="session")
def _drepturi_initiale():
    """Drepturile conturilor comune, citite o dată la începutul rulării."""
    r = sql("SELECT email, %s FROM public.users WHERE email = ANY(%%s)" % ", ".join(_DREPTURI), (list(CONTURI_COMUNE),))
    return {x[0]: x[1:] for x in r}


@pytest.fixture(scope="module", autouse=True)
def _drepturi_comune_neschimbate(_drepturi_initiale):
    """[09.10.2026, prins la rularea integrală] Unele teste comută temporar drepturile contului comun de asistent; fiecare FIȘIER
    pornește și se termină cu drepturile de la începutul rulării, ca rezultatul să nu depindă de ordinea fișierelor."""
    def pune():
        for email, val in _drepturi_initiale.items():
            sql("UPDATE public.users SET %s WHERE email = %%s" % ", ".join("%s = %%s" % d for d in _DREPTURI), (*val, email))
    pune()
    yield
    pune()
