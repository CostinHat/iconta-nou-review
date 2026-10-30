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


Perioada = __import__("collections").namedtuple("Perioada", "an luna trim inceput sfarsit")


def perioada_incheiata(periodicitate="lunar", azi=None):
    """[lotul 10, deficiența 383 — comanda Costin 10.2 pct.1: „O declarație pe o perioadă neîncheiată se refuză la generare, cu motivul
    scris, la toate declarațiile.”] Cea mai recentă perioadă ÎNCHEIATĂ după periodicitatea declarației („lunar” / „trimestrial” /
    „anual”): luna trecută, trimestrul trecut, anul trecut — aceeași regulă ca perioada propusă de ecranul Declarații când nimic nu e
    scadent (`static/js/ecrane/declaratii.js::perioadaImplicita`) și ca refuzul serverului (`coada_api.perioada_neincheiata`). Granițele:
    în ianuarie luna trecută e 12/anul trecut; în prima lună a unui trimestru, trimestrul trecut e cel dinainte (în ianuarie T4/anul
    trecut). -> `Perioada(an, luna, trim, inceput, sfarsit)`: `luna` numai la lunar, `trim` numai la trimestrial (altfel None); `inceput` /
    `sfarsit` = prima / ultima zi a perioadei — documentele de probă se datează între ele (`inceput.replace(day=n)` la lunar).
    Un test care pune documentele în perioada asta și generează pe ea descrie pașii contabilului pe o perioadă pe care aplicația o
    generează. Calculată o dată, la importul testului: o rulare care trece peste miezul nopții (și peste o lună) o găsește tot încheiată."""
    import calendar
    a = azi or _dt.date.today()
    if periodicitate == "anual":
        return Perioada(a.year - 1, None, None, _dt.date(a.year - 1, 1, 1), _dt.date(a.year - 1, 12, 31))
    if periodicitate == "trimestrial":
        t = (a.month - 1) // 3                      # trimestrele încheiate în anul de azi: 0 în T1 -> T4 al anului trecut
        an, trim = (a.year, t) if t else (a.year - 1, 4)
        return Perioada(an, None, trim, _dt.date(an, trim * 3 - 2, 1), _dt.date(an, trim * 3, calendar.monthrange(an, trim * 3)[1]))
    if periodicitate != "lunar":
        raise ValueError("periodicitate necunoscută: %r" % (periodicitate,))
    sf = a.replace(day=1) - _dt.timedelta(days=1)
    return Perioada(sf.year, sf.month, None, sf.replace(day=1), sf)


def _db():
    from core import db
    try:
        db.init_pool()
    except Exception:  # noqa: BLE001 — deja inițializat
        pass
    return db


#: [deficiența 320] numărul de telefon al conturilor de TEST (sintetic: prefixul +40 și cifre de umplutură, nu al cuiva)
TELEFON_TEST = "+40700000000"


def sesiune(email, prima_intrare=False):
    """Scriptul care pune tokenul unui cont de TEST în sessionStorage (pe drumul aplicației: `sesiune_pentru_user`).
    [320] Contul de test a trecut de prima intrare (telefonul și notificările salvate), ca pașii testului să înceapă pe pagina principală;
    `prima_intrare=True` lasă contul cum e (testul primei intrări)."""
    from core import auth_api
    db = _db()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM public.users WHERE email=%s", (email,))
            u = cur.fetchone()
            if u and not prima_intrare:
                cur.execute("UPDATE public.users SET telefon = COALESCE(telefon, %s), notificari_salvate_la = COALESCE(notificari_salvate_la, "
                            "now()) WHERE id = %s", (TELEFON_TEST, u[0]))
                conn.commit()
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
    """[258] Cum vede contabilul nota `nid` în Registrul jurnal: „nr. crt. N din ZZ.LL.AAAA”. [302, 17.10.2026] numărul e cel PĂSTRAT,
    dat la validare (`registru_jurnal_numere`), citit AICI, independent de `eticheta_nota`; nota nevalidată n-are număr: „din ZZ.LL.AAAA”."""
    nr, data, stare = sql('SELECT r.nr_curent, i.data, i.status FROM "%s".inregistrari i LEFT JOIN "%s".registru_jurnal_numere r '
                          'ON r.inregistrare_id = i.id WHERE i.id = %%s' % (schema, schema), (nid,))[0]
    if nr is None:
        return "din %s" % data.strftime("%d.%m.%Y")
    return "nr. crt. %d din %s" % (nr, data.strftime("%d.%m.%Y"))


@pytest.fixture(autouse=True)
def _fara_ciorne_ramase():
    """[495, lotul 12] Ciornele formularelor stau pe server, pe utilizator + firmă: fiecare test pornește fără ciornele conturilor de test
    (înainte, fiecare test pornea cu un browser gol, deci fără ciornă)."""
    if sql("SELECT to_regclass('public.ciorne_formular') IS NOT NULL")[0][0]:
        sql("DELETE FROM public.ciorne_formular c USING public.users u WHERE u.id = c.user_id AND u.email LIKE %s", ("%@prisma-cont.test",))
    yield


@pytest.fixture(scope="session")
def browser():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True)
        yield b
        b.close()


def text_din_card(pg, zona):
    """[lotul 14, 687] Textul serverului dintr-un card-rezumat al importului (`#mig-inlocuire`, `#mig-firma-fisier`): deschide cardul din `zona`, citește
    `<zona>-text` (textul și clasa lui), se întoarce la previzualizare. -> (text, clasă)."""
    pg.click(zona + " [data-card]")
    pg.wait_for_selector(".fereastra:last-of-type " + zona + "-text", timeout=15000)
    el = pg.locator(".fereastra:last-of-type " + zona + "-text")
    rez = (el.inner_text(), el.get_attribute("class"))
    pg.click(".fereastra:last-of-type .nav-sageata.nav-inapoi")
    pg.wait_for_selector(zona + " [data-card]", timeout=15000)
    return rez


from file_ui import _cu_filele_aratate  # noqa: E402,F401 — [lotul 14, 687] filele apăsate ca omul (definiția e în file_ui.py)


class Ecran:
    """O pagină cu un cont logat + ce a observat (erori JS, cereri eșuate) + captura numită după deficiență."""

    def __init__(self, pg, nume_test):
        self.pg, self.erori, self.cereri_rele = pg, [], []
        _cu_filele_aratate(pg)   # [lotul 14, 687] câmpurile din file ascunse își arată fila
        self.nume = nume_test[len("test_def_"):] if nume_test.startswith("test_def_") else nume_test
        pg.on("pageerror", lambda e: self.erori.append(str(e)))
        self.deschideri_singure = []   # [325] notate de GARDA_DESCHIDERI
        pg.on("console", lambda m: self.deschideri_singure.append(m.text[6:]) if m.text.startswith("[325] ") else None)
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


#: [deficiența 325, comanda Costin 8.1 pct.2, 18.10.2026, verbatim în DECIZII] „nicio listă, fereastră, formular sau card nu se deschide
#: fără clicul utilizatorului. Pune-o ca gardă, ca să nu mai revină.” Garda stă în FIECARE ecran al plasei (toate testele `_ecran`) și
#: notează (pe consolă, strânse de `Ecran`):
#:   - orice focus pus din cod pe o listă (`<select>`): focusul îi deschide lista pe telefon / cu tastatura (cauza lui 325, `#dec-tip`);
#:     focusul dat de om (clic, Tab) nu trece prin `HTMLElement.prototype.focus`, deci nu se notează;
#:   - orice `showPicker()` (deschide lista / calendarul din cod);
#:   - orice fereastră (`role=dialog`, `.fereastra-overlay`) apărută ÎNAINTEA primului gest al omului pe pagină
#:     (`navigator.userActivation.hasBeenActive`), afară de cele pe care aplicația le deschide singură prin decizie: bun venit,
#:     anunțul iConta, reautentificarea (`data-deschidere="aplicatie"`) și linkul dintr-o notificare (`#deschide=`, omul a apăsat linkul).
#: Testul pică la final cu lista lor. LIMITA: o fereastră deschisă din cod DUPĂ un prim gest al omului nu se prinde (fără ceas de
#: activare, care ar da alarme false la cererile lente); formularele / cardurile care se desfac în pagină se prind numai prin testele lor.
GARDA_DESCHIDERI = r"""
(() => {
  // pe consolă (prefixul [325]): `Ecran` le strânge peste navigări (o listă din pagină s-ar pierde la fiecare `goto`)
  const note = { push: (t) => console.warn("[325] " + t) };
  const id = (el) => el.tagName.toLowerCase() + (el.id ? "#" + el.id : "") + (el.name ? "[name=" + el.name + "]" : "");
  const focusVechi = HTMLElement.prototype.focus;
  HTMLElement.prototype.focus = function (...a) {
    if (this instanceof HTMLSelectElement) note.push("focus din cod pe lista " + id(this));
    return focusVechi.apply(this, a);
  };
  for (const C of [HTMLSelectElement, HTMLInputElement]) {
    if (C.prototype.showPicker) {
      const vechi = C.prototype.showPicker;
      C.prototype.showPicker = function (...a) { note.push("showPicker pe " + id(this)); return vechi.apply(this, a); };
    }
  }
  const dinLink = /^#deschide=/.test(location.hash);
  const verifica = (el) => {
    if (!(el instanceof Element) || dinLink || (navigator.userActivation && navigator.userActivation.hasBeenActive)) return;
    const f = el.matches('[role="dialog"], .fereastra-overlay') ? el : el.querySelector('[role="dialog"], .fereastra-overlay');
    if (f && !f.closest('[data-deschidere="aplicatie"]') && !f.querySelector('[data-deschidere="aplicatie"]'))
      note.push("fereastră deschisă fără clic: " + (f.getAttribute("aria-label") || f.className || f.tagName));
  };
  new MutationObserver((ms) => ms.forEach((m) => m.addedNodes.forEach(verifica)))
    .observe(document, { childList: true, subtree: true });
})();
"""


def _ecran(browser, request, email):
    ctx = browser.new_context(viewport={"width": LAT, "height": INALT})
    ctx.add_init_script(sesiune(email))
    ctx.add_init_script(GARDA_DESCHIDERI)
    e = Ecran(ctx.new_page(), request.node.name)
    yield e
    erori, rele, singure = list(e.erori), list(e.cereri_rele), list(e.deschideri_singure)
    ctx.close()
    assert not erori, "erori JavaScript pe ecran: %s" % erori[:3]
    assert not rele, "cereri cu răspuns 5xx: %s" % rele[:3]
    assert not singure, "[325] s-a deschis ceva fără clicul omului: %s" % singure[:5]


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


#: [deficiența 381, comanda Costin 8.2] nota manuală pe 401 / 4111 cere partenerul la introducere (`jurnal_api._linii_valide`)
PARTENER_PROBA = "PARTENER PROBA SRL"


def linie_nota(debit, credit, suma):
    """O linie de notă manuală, cu partenerul scris când unul din conturi e de terți (401 / 4111, cu sau fără analitic)."""
    linie = {"debit": debit, "credit": credit, "suma": suma}
    if any(str(c).split(".")[0] in ("401", "4111") for c in (debit, credit)):
        linie["partener_nume"] = PARTENER_PROBA
    return linie


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
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # frontend_test/: ajutătoarele comune plasei și uneltelor
from declaratie_tip import alege_tipul  # noqa: E402,F401 — tipul declarației se alege numai prin el (core/test_e2e_perioada.py)


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


@pytest.fixture()
def firma_horeca():
    """O firmă NOUĂ cu CAEN 5610 (restaurante — în lista HoReCa din CF, `core.horeca.CODURI`): Rețete se oferă numai firmelor HoReCa
    (371, lotul 9). Aici, nu într-un fișier de teste: o cer mai multe fișiere (`e2e_lot91`, `e2e_lot82`), iar importul între ele e circular."""
    for f in firma_noua():
        sql('UPDATE "%s".firma_profil SET caen = %%s WHERE id = 1' % f["schema"], ("5610",))
        yield f


CONTURI_COMUNE = ("patron@prisma-cont.test", "asistent@prisma-cont.test")
_DREPTURI = ("poate_pregati", "poate_valida", "poate_depune")


@pytest.fixture(scope="session")
def _drepturi_initiale():
    """Drepturile conturilor comune, citite o dată la începutul rulării."""
    r = sql("SELECT email, %s FROM public.users WHERE email = ANY(%%s)" % ", ".join(_DREPTURI), (list(CONTURI_COMUNE),))
    return {x[0]: x[1:] for x in r}


@pytest.fixture(scope="module", autouse=True)
def _anaf_simulat_numai_baza():
    """[lotul 11, prins la plasa din 22.10.2026] Răspunsurile ANAF pregătite de un test (`<ICONTA_ANAF_SIMULAT>/anaf.json`, 444 / 459)
    rămâneau pentru fișierele de după: DANTE cu denumirea testului și fără localitate -> D406 refuzat în e2e_lot82 / e2e_lot91, numai când
    rulau după ele. Fiecare FIȘIER pornește și se termină cu baza simulatorului (`anaf_baza.json`, răspunsurile reale), ca drepturile."""
    def scoate():
        d = os.environ.get("ICONTA_ANAF_SIMULAT")
        if d and os.path.exists(os.path.join(d, "anaf.json")):
            os.remove(os.path.join(d, "anaf.json"))
    scoate()
    yield
    scoate()


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


# [30.10.2026, comanda 15.G] marcajul global de sărire (scripts/poarta.env): același mecanism ca în conftest.py de la rădăcină
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "scripts"))
import poarta_sare as _sare  # noqa: E402


def pytest_ignore_collect(collection_path, config):
    if _sare.sare_fisier(str(collection_path)):
        return True
    return None
