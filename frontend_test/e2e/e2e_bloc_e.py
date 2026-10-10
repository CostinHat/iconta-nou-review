# -*- coding: utf-8 -*-
"""Blocul E — deficiențele 144–170 din DEFICIENTE.md („08.10 seara — deciziile §1–7 și cele 21 de constatări”), probate în browser.

Două firme sintetice ale rulării, create pe drumul aplicației și scoase la final:
  * `firma` = `firma_e2e` (conftest), stoc CANTITATIV-VALORIC, plătitoare de TVA lunar, micro;
  * `firma_gv` = o a doua firmă a cabinetului de test, stoc GLOBAL-VALORIC (aceleași date fiscale).
Datele se pun pe drumul aplicației: funcțiile din core/ (cele pe care le cheamă rutele) sau cererile HTTP ale ecranului, făcute din
pagina contului logat (`_api`). Lunile sunt împărțite între teste ca să nu se calce (firma: 06/2026 luna preluării, 07/2026 balanța și
401, 08/2026 NIR-urile, 09/2026 luna încheiată curată, 10/2026 facturile emise, chitanța, coada; firma_gv: 2024 bilanțul, 12/2025 →
07/2026 NIR-ul între exerciții, 08/2026 amortizarea și descărcarea).
"""
import datetime as _dt
import io as _io
import json as _json
import os as _os
import re as _re
import subprocess as _sp
import time as _time
from decimal import Decimal

import pytest

from conftest import PREFIX_FIRMA, _ecran, _scoate_firmele_e2e, cui_cu_control, sql

IBAN_PROBA = "RO49AAAA1B31007593840000"   # IBAN-ul exemplu ECBS pentru România (cifrele de control valide)
AZI = _dt.date.today()


# ------------------------------------------------------------------------------------------------ ajutoare comune

def _uid(email="patron@prisma-cont.test"):
    return sql("SELECT id FROM public.users WHERE email = %s", (email,))[0][0]


def _completeaza(f, metoda):
    """Date firmă pe drumul ecranului (`firma_profil_api.salveaza_date` + `vector_fiscal_api.salveaza`): identitate, capital, metoda de
    stoc, seria chitanțelor; plătitoare de TVA, decont lunar, micro, fără operațiuni intracomunitare. Asistentul primește firma."""
    from core import asistenti_api, db, firma_profil_api as fp, vector_fiscal_api as vf
    uid = _uid()
    with db.get_conn(f["schema"]) as c:
        r = fp.salveaza_date(c, {"reg_com": "J40/1234/2020", "caen": "4719", "adresa": "Str. Probei nr. 1", "oras": "București",
                                 "judet": "București", "banca": "Banca Probă", "iban": IBAN_PROBA, "telefon": "0712345678",
                                 "email": "proba@prisma-cont.test", "declarant_nume": "Popescu", "declarant_prenume": "Ion",
                                 "declarant_functie": "Administrator", "forma_juridica": "SRL", "capital_subscris": "200",
                                 "capital_varsat": "200", "metoda_stoc": metoda, "serie_chitanta": "CHE"},
                             tenant_id=f["tenant_id"], user_id=uid)
        assert r.get("ok"), r
        r = vf.salveaza(c, "micro", True, "lunar", False, inreg_art317=False, user_id=uid)
        assert r.get("ok"), r
        c.commit()
    with db.get_conn() as c:
        r = asistenti_api.atribuie_firma(c, f["cabinet_id"], _uid("asistent@prisma-cont.test"), f["tenant_id"])
        assert r.get("ok"), r
        c.commit()
    return f


@pytest.fixture(scope="module")
def firma(firma_e2e):
    return _completeaza(firma_e2e, "cantitativ_valoric")


@pytest.fixture(scope="module")
def firma_gv(firma_e2e):
    """A doua firmă sintetică a rulării, la global-valoric — creată ca `firma_e2e` (`provision_tenant`), scoasă la final."""
    from core import db, tenant_provisioning as tp
    nume = "%s GV %d SRL" % (PREFIX_FIRMA, int(_time.time() * 1000) % 10000000)
    rad = _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
    sql_t = _io.open(_os.path.join(rad, "tenant_template.sql"), encoding="utf-8").read()
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute("SELECT id, accounting_firm_id FROM public.users WHERE email = 'patron@prisma-cont.test'")
        uid, cab = cur.fetchone()
        r = tp.provision_tenant(c, nume, cui_cu_control(80000000 + int(_time.time() * 1000) % 9000000), cab, uid, sql_t)
        c.commit()
    f = {"tenant_id": r["tenant_id"], "schema": r["schema_name"], "nume": nume, "cabinet_id": cab}
    try:
        yield _completeaza(f, "global_valoric")
    finally:
        _scoate_firmele_e2e(r["tenant_id"])


EMAIL_JUNIOR = "junior-bloc-e@prisma-cont.test"


@pytest.fixture(scope="module")
def junior_cont(firma, firma_gv):
    """Un asistent junior al cabinetului de test: «Poate pregăti», FĂRĂ «Poate valida» (contul comun `asistent@` are acum și
    «Poate valida», deci nu mai e utilizatorul fără drept). Creat pe drumul ecranului Asistenți
    (`repo_utilizatori.creeaza_cont_asistent`), cu cele două firme atribuite; scos la final."""
    import secrets
    from core import asistenti_api, db, nucleu, repo_utilizatori
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute("SELECT id FROM public.users WHERE email = %s", (EMAIL_JUNIOR,))
        r = cur.fetchone()
        uid = r[0] if r else repo_utilizatori.creeaza_cont_asistent(cur, EMAIL_JUNIOR, nucleu.hash_parola(secrets.token_urlsafe(16)),
                                                                    "Junior Bloc E", firma["cabinet_id"], True, False)[0]
        cur.execute("UPDATE public.users SET activ = true, poate_pregati = true, poate_valida = false, poate_depune = false, "
                    "bun_venit_vazut_la = now() WHERE id = %s", (uid,))
        c.commit()
    with db.get_conn() as c:
        for f in (firma, firma_gv):
            assert asistenti_api.atribuie_firma(c, f["cabinet_id"], uid, f["tenant_id"]).get("ok")
        c.commit()
    yield uid
    try:
        sql("DELETE FROM public.user_tenants WHERE user_id = %s", (uid,))
        sql("DELETE FROM public.users WHERE id = %s", (uid,))
    except Exception:  # noqa: BLE001 — urme ale contului în alte tabele publice: rămâne inactiv
        sql("UPDATE public.users SET activ = false WHERE id = %s", (uid,))


@pytest.fixture()
def junior(browser, request, junior_cont):
    """Ecranul asistentului junior (fără «Poate valida»)."""
    yield from _ecran(browser, request, EMAIL_JUNIOR)


_JS_API = """async ([m, c, b]) => {
  const t = sessionStorage.getItem('iconta_token');
  const r = await fetch(c, {method: m, headers: {'Content-Type': 'application/json', Authorization: 'Bearer ' + t},
                            body: b == null ? undefined : JSON.stringify(b)});
  let j = null; try { j = await r.json(); } catch (e) {}
  return {status: r.status, json: j};
}"""


def _api(ecran, metoda, cale, corp=None):
    """O cerere HTTP a aplicației, din pagina contului logat (aceleași gărzi, același autor ca pe ecran)."""
    if not ecran.pg.url.startswith("http"):
        ecran.acasa()
    return ecran.pg.evaluate(_JS_API, [metoda, cale, corp])


def _ok(r):
    assert r["status"] < 300, r
    return r["json"]


def _nota(f, data, linii, descriere="Notă de probă E2E", valideaza=False, document_ref="Document probă E2E"):
    """Notă manuală pe drumul Registrului jurnal (`jurnal_api.creeaza`), validată la cerere (`jurnal_api.valideaza`)."""
    from core import db, jurnal_api
    with db.get_conn(f["schema"]) as c:
        r = jurnal_api.creeaza(c, f["schema"], descriere, data, linii, document_ref)
        assert r.get("ok"), r
        if valideaza:
            v = jurnal_api.valideaza(c, f["schema"], r["id"])
            assert v and v.get("ok"), v
        c.commit()
    return r["id"]


def _valideaza_note(f, ids):
    from core import db, jurnal_api
    with db.get_conn(f["schema"]) as c:
        for i in ids:
            v = jurnal_api.valideaza(c, f["schema"], i)
            assert v and v.get("ok"), (i, v)
        c.commit()


def _sterge_note(f, ids):
    """Scoate ciornele puse de test. O notă VALIDATĂ nu se mai șterge (regula de fond din bază: nota validată e imuabilă) — rămâne pe
    firma sintetică, scoasă oricum la finalul rulării; lunile testelor sunt alese ca validatul rămas să nu le atingă."""
    s = f["schema"]
    ids = [i for i in ids if sql('SELECT status FROM "%s".inregistrari WHERE id = %%s' % s, (i,)) != [("validata",)]]
    for nid in ids:
        sql('DELETE FROM "%s".inregistrari_linii WHERE inregistrare_id = %%s' % s, (nid,))
        sql("DELETE FROM public.declaratii_coada WHERE tenant_id = %s AND fel = 'nota' AND perioada = %s", (f["tenant_id"],
                                                                                                         "nota-%d" % nid))
        sql('DELETE FROM "%s".inregistrari WHERE id = %%s' % s, (nid,))


def _ultima():
    return "() => [...document.querySelectorAll('.fereastra')].pop()"


def _asteapta_text(ecran, text, timeout=30000):
    """Așteaptă textul în fereastra din față (ce citește contabilul)."""
    try:
        ecran.pg.wait_for_function("(t) => { const f = [...document.querySelectorAll('.fereastra')].pop(); "
                                   "return !!f && f.innerText.includes(t); }", arg=text, timeout=timeout)
    except Exception:
        ecran.captura("negasit")
        raise AssertionError("pe ecran nu apare %r; fereastra arată: %s" % (text, ecran.fereastra()[-1500:]))


_GATA = {"#il-prev": "() => (document.querySelector('#il-stare-perioada') || {}).textContent && (document.querySelector('#il-controale') || {}).innerText",
         "#j-prev": "() => (document.querySelector('#j-lock') || {}).textContent",
         "#s-prev": "() => { const x = document.querySelector('#s-situatie'); return x && !x.innerText.startsWith('Se încarcă'); }"}


def _la_luna(ecran, buton_inapoi, an, luna):
    """Din luna curentă, înapoi lună cu lună până la `luna/an`, așteptând antetul fiecărei luni („Luna LL/AAAA”) și sfârșitul
    desenării (butoanele se leagă după cererile ecranului; un clic dat înainte s-ar pierde)."""
    cur = AZI.year * 12 + AZI.month - 1
    tinta = an * 12 + luna - 1
    gata = _GATA.get(buton_inapoi)

    def asteapta(c):
        _asteapta_text(ecran, "Luna %02d/%d" % (c % 12 + 1, c // 12))
        if gata:
            ecran.pg.wait_for_function(gata, timeout=60000)
        ecran.pg.wait_for_timeout(300)
    asteapta(cur)
    while cur > tinta:
        cur -= 1
        ecran.pg.click(buton_inapoi)
        asteapta(cur)


def _card(ecran, f, cheie, asteapta):
    ecran.firma(f["nume"])
    ecran.pg.click("#fa-%s" % cheie)
    ecran.pg.wait_for_selector(asteapta, timeout=30000)


def _randuri_jurnal(ecran):
    """Notele din Registrul jurnal de pe ecran: [(text antet, [„D = C · suma”])]."""
    return ecran.pg.evaluate("""() => [...[...document.querySelectorAll('.fereastra')].pop().querySelectorAll('[data-nota-id]')].map((n) =>
        [n.querySelector('.pf-frand-nume').innerText, n.querySelector('.pf-frand-sub').innerHTML.split('<br>').map((x) => x.replace(/<[^>]+>/g, '').trim())])""")


# ------------------------------------------------------------------------------------------------ Date firmă: luna preluării (147, 169)

def _date_firma(ecran, f):
    _card(ecran, f, "datefirma", "#df-luna_preluare")


def _prima_nota(f):
    r = sql('SELECT min(data) FROM "%s".inregistrari' % f["schema"])[0][0]
    return r


def test_def_147_luna_preluarii_editabila_niciodata_dupa_prima_nota(patron, firma):
    """147. Date firmă: „Luna preluării” editabilă, cu propunere, niciodată după prima notă.
    Pașii contabilului: firma are o notă din 06/2026 -> deschide Date firmă -> vede limita „nu poate fi după 06/2026 (prima notă)” ->
    scrie 08/2026 și salvează: refuzul stă lângă câmp și nu se salvează nimic -> scrie 05/2026 și salvează: se salvează, iar
    „Istoricul modificărilor” arată rândul „Luna preluării … 05/2026” (schimbarea se jurnalizează)."""
    nid = _nota(firma, "2026-06-15", [{"debit": "5311", "credit": "1012", "suma": "100.00"}])
    s = firma["schema"]
    try:
        pn = _prima_nota(firma)
        assert pn == _dt.date(2026, 6, 15), pn          # nicio notă mai veche lăsată de alt test
        pg = patron.pg
        _date_firma(patron, firma)
        ajutor = pg.locator("label.camp:has(#df-luna_preluare) .camp-ajutor").inner_text()
        assert "Nu poate fi după 06/2026 (prima notă)" in ajutor, ajutor
        pg.fill("#df-luna_preluare", "2026-08")
        pg.click("#df-salveaza")
        pg.wait_for_selector('.msg-eroare[data-camp="df-luna_preluare"]', timeout=30000)
        refuz = pg.inner_text('.msg-eroare[data-camp="df-luna_preluare"]')
        assert "nu poate fi după luna primei note din jurnal (06/2026)" in refuz, refuz
        pg.locator("#df-luna_preluare").scroll_into_view_if_needed()
        patron.captura("refuz_08_2026")
        assert sql('SELECT luna_preluare FROM "%s".firma_profil WHERE id = 1' % s) == [(None,)]
        pg.fill("#df-luna_preluare", "2026-05")
        pg.click("#df-salveaza")
        _asteapta_text(patron, "Datele firmei au fost salvate")
        assert sql('SELECT luna_preluare FROM "%s".firma_profil WHERE id = 1' % s) == [(_dt.date(2026, 5, 1),)]
        rand = pg.locator("#df-jurnal tr", has_text="Luna preluării").first.inner_text()
        assert "05/2026" in rand, rand
        pg.locator("#df-jurnal").scroll_into_view_if_needed()
        patron.captura("salvata_05_2026_in_istoric")
    finally:
        sql('UPDATE "%s".firma_profil SET luna_preluare = NULL WHERE id = 1' % s)
        _sterge_note(firma, [nid])


def test_def_169_luna_preluarii_arata_propunerea_fara_gol(patron, firma):
    """169. Date firmă: „Luna preluării” cu „---------- ----” și „Gol = propunerea”.
    Pașii contabilului: firma are o notă din 06/2026 și luna preluării nesalvată -> deschide Date firmă: câmpul arată 06/2026 (luna
    efectivă = propunerea), nu „---------- ----”; ajutorul spune „Completată cu propunerea: 06/2026”, fără „Gol = propunerea”."""
    nid = _nota(firma, "2026-06-15", [{"debit": "5311", "credit": "1012", "suma": "100.00"}])
    try:
        assert _prima_nota(firma) == _dt.date(2026, 6, 15)
        pg = patron.pg
        _date_firma(patron, firma)
        assert pg.input_value("#df-luna_preluare") == "2026-06", "câmpul lunii preluării e gol („---------- ----”)"
        ajutor = pg.locator("label.camp:has(#df-luna_preluare) .camp-ajutor").inner_text()
        assert "Completată cu propunerea: 06/2026" in ajutor, ajutor
        assert "Gol = propunerea" not in patron.fereastra()
        pg.locator("#df-luna_preluare").scroll_into_view_if_needed()
        patron.captura("camp_cu_propunerea")
    finally:
        _sterge_note(firma, [nid])


# ------------------------------------------------------------------------------------------------ Închidere lună (160, 161)

def _inchidere(ecran, f):
    _card(ecran, f, "inchidere", "#il-lock")
    ecran.pg.wait_for_function("() => { const z = document.querySelector('#il-controale'); return z && z.innerText.trim().length > 0; }",
                               timeout=60000)


def test_def_160_luna_in_curs_nu_se_inchide_un_singur_loc(patron, firma):
    """160. Închidere lună: luna în curs se putea bloca; buton activ cu blocaje; „Închide luna” în două locuri.
    Pașii contabilului: Închidere lună pe luna curentă -> „Ce oprește închiderea” spune că luna nu s-a încheiat, „Blochează luna” e
    inactiv, evidența facturilor nu are „Închide evidența facturilor” -> trece pe luna trecută (încheiată, fără nimic de rezolvat):
    butonul de blocare e activ și închiderea evidenței e oferită -> deschide Istoric facturi: acolo nu mai e „Închide luna”, doar starea
    și trimiterea la cardul „Închidere lună”."""
    pg = patron.pg
    _inchidere(patron, firma)
    curenta = "%02d/%d" % (AZI.month, AZI.year)
    blocaje = pg.inner_text("#il-controale")
    assert "luna %s nu s-a încheiat" % curenta in blocaje, blocaje
    assert pg.is_disabled("#il-lock"), "„Blochează luna” e activ pe luna în curs, cu blocaje"
    fac = pg.inner_text("#il-facturi")
    assert "nu se poate închide încă" in fac and "luna %s nu s-a încheiat" % curenta in fac, fac
    assert pg.locator("#il-fac-inchide").count() == 0
    patron.captura("luna_in_curs")
    pg.click("#il-prev")
    prec = AZI.replace(day=1) - _dt.timedelta(days=1)
    _asteapta_text(patron, "Luna %02d/%d" % (prec.month, prec.year))
    pg.wait_for_function("() => (document.querySelector('#il-controale') || {}).innerText?.includes('Nimic nu oprește închiderea')",
                         timeout=60000)
    pg.wait_for_selector("#il-fac-inchide", timeout=30000)
    # blocarea se activează după ce sosesc controalele lunii (citite fără să țină ecranul — proba plasei, 58)
    pg.wait_for_function("() => { const b = document.querySelector('#il-lock'); return b && !b.disabled; }", timeout=30000)
    assert pg.inner_text("#il-lock") == "Blochează luna"
    patron.captura("luna_incheiata")
    _card(patron, firma, "facturi", "#fac-istoric")
    pg.click("#fac-istoric")
    _asteapta_text(patron, "Se închide și se redeschide din cardul")
    txt = patron.fereastra()
    assert "Se închide și se redeschide din cardul „Închidere lună” al firmei" in txt, txt[:600]
    assert pg.evaluate("() => [...[...document.querySelectorAll('.fereastra')].pop().querySelectorAll('button')]"
                       ".filter((b) => /Închide (luna|evidența)/.test(b.innerText)).length") == 0
    patron.captura("istoric_facturi_fara_inchidere")


def test_def_220_clicul_pe_evidenta_facturilor_nu_se_pierde_cat_se_citesc_controalele(patron, firma):
    """220. Închidere lună: „Închide evidența facturilor” apare pe ecran, dar un clic dat cât se citesc controalele lunii se pierde.
    [comanda Costin 10.10.2026 pct.8, verbatim: „Un clic al contabilului nu se pierde nicăieri.”] Butonul se lega după cererile
    controalelor și ale blocării lunii (`static/js/ecrane/firme.js`, „Închidere lună”). Cursa se face deterministă: cererea
    controalelor (`/perioade-blocate`) e întârziată 4 s în pagină. Pașii contabilului: Închidere lună -> luna trecută -> apasă
    „Închide evidența facturilor” imediat ce apare, cât controalele încă se încarcă -> caseta de confirmare apare. MUTAȚIE: legarea
    mutată înapoi după `await legaBlocareLuna` -> clicul nu face nimic -> pică (gardul de formă: `core/test_legari_await.py`)."""
    pg = patron.pg
    _inchidere(patron, firma)
    pg.evaluate("""() => { const f = window.fetch; window.fetch = (u, o) => String(u).includes('perioade-blocate')
      ? new Promise((r) => setTimeout(r, 4000)).then(() => f(u, o)) : f(u, o); }""")
    pg.click("#il-prev")
    pg.wait_for_selector("#il-fac-inchide", timeout=30000)
    pg.click("#il-fac-inchide")
    pg.wait_for_selector("#caseta-atentie-activa", timeout=2500)
    assert "Închizi evidența facturilor lunii?" in pg.inner_text("#caseta-atentie-activa")
    assert not pg.inner_text("#il-controale").strip(), "controalele sosiseră deja — clicul nu a fost dat în timpul cererii"
    patron.captura("confirmare_in_timpul_cererii")
    pg.click("#ca-nu")


def test_def_161_semnal_furnizor_cu_sold_debitor(patron, firma):
    """161. Închidere lună: lipsea semnalul pentru furnizor cu sold debitor.
    Pașii contabilului: în 07/2026 s-a plătit un furnizor (401 = 5121, 500 lei) fără factura lui înregistrată -> Închidere lună pe
    07/2026 -> la „Semnale” apare „contul 401 (furnizori) are sold debitor de 500,00 lei la sfârșitul lunii” (semnal, nu blocaj)."""
    nid = _nota(firma, "2026-07-20", [{"debit": "401", "credit": "5121", "suma": "500.00"}], "Plată furnizor fără factură",
                valideaza=True)
    try:
        pg = patron.pg
        _inchidere(patron, firma)
        _la_luna(patron, "#il-prev", 2026, 7)
        pg.wait_for_function("() => (document.querySelector('#il-controale') || {}).innerText?.includes('Semnale')", timeout=60000)
        z = pg.inner_text("#il-controale")
        assert "contul 401 (furnizori) are sold debitor de 500,00 lei la sfârșitul lunii" in z, z
        semnale = pg.inner_text("#il-controale .caseta-info:has(b:text('Semnale'))")
        assert "401" in semnale, semnale
        pg.locator("#il-controale").scroll_into_view_if_needed()
        patron.captura("semnal_401_debitor")
    finally:
        _sterge_note(firma, [nid])


# ------------------------------------------------------------------------------------------------ Balanță (150, 167)

def _balanta(ecran, f, an, luna):
    _card(ecran, f, "balanta", "#b-prev")
    _la_luna(ecran, "#b-prev", an, luna)


def test_def_150_evidenta_e_ce_a_validat_un_om(patron, firma):
    """150. Balanță/porți: R36 — evidența e ce a validat un om.
    Pașii contabilului: în 07/2026 are o notă validată (5311 = 1012, 1.000 lei) și o ciornă (5311 = 1012, 250 lei) -> Balanța pe
    07/2026: 5311 are rulajul lunii 1.000,00 (numai validatul), iar caseta separată spune „1 ciornă nevalidată nu intră în balanță”
    -> Declarații, D300 pe 07/2026, trimisă în coadă: poarta nu blochează, dă doar avertismentul cu ciorna."""
    v = _nota(firma, "2026-07-05", [{"debit": "5311", "credit": "1012", "suma": "1000.00"}], "Aport capital", valideaza=True)
    c = _nota(firma, "2026-07-06", [{"debit": "5311", "credit": "1012", "suma": "250.00"}], "Aport capital — ciornă")
    try:
        pg = patron.pg
        _balanta(patron, firma, 2026, 7)
        pg.wait_for_selector("#b-ciorne", timeout=30000)
        rand = pg.locator("table.fd-tabel tr", has=pg.locator("td:text-is('5311')")).first
        celule = rand.locator("td").all_inner_texts()
        assert celule[6] == "1.000,00" and celule[7] == "0,00", celule   # rulaj lună D / C
        ciorne = pg.inner_text("#b-ciorne")
        assert "1 ciornă nevalidată nu intră în balanță" in ciorne and "(1 în luna asta" in ciorne, ciorne
        patron.captura("balanta_validat_si_ciorna")
        # poarta: D300 07/2026 în coadă — avertisment, nu blocaj
        _card(patron, firma, "declaratii", "#dec-tip")
        pg.select_option("#dec-tip", "d300")
        pg.fill("#dec-an", "2026")
        pg.dispatch_event("#dec-an", "change")
        pg.select_option("#dec-luna", "7")
        pg.click("#dec-continua")
        pg.wait_for_selector("#dec-trimite, #dec-gol-da", timeout=60000)
        pg.click("#dec-gol-da" if pg.locator("#dec-gol-da").count() else "#dec-trimite")
        pg.wait_for_selector(".dec-gata, .caseta-atentie #coada-confirmare", timeout=60000)
        if pg.locator("#coada-confirmare").count():
            pg.fill("#coada-confirmare", "Probă E2E: declarație fără operațiuni în luna de probă.")
            pg.click("#coada-confirma")
            pg.wait_for_selector(".dec-gata", timeout=60000)
        _asteapta_text(patron, "nevalidată")
        txt = patron.fereastra()
        assert "Trimisă în coada de validare" in txt and "În perioadă sunt 1 notă(e) nevalidată(e)" in txt, txt[:800]
        patron.captura("d300_in_coada_cu_avertisment")
    finally:
        sql("DELETE FROM public.declaratii_coada WHERE tenant_id = %s AND fel <> 'nota' AND tip = 'd300'", (firma["tenant_id"],))
        _sterge_note(firma, [v, c])


def test_def_167_pdf_balanta_cu_cui_si_data_in_antet(patron, firma):
    """167. Balanță: PDF fără CUI și dată în antet.
    Pașii contabilului: Balanța pe 09/2026 (o notă validată) -> „Descarcă PDF” -> antetul PDF-ului poartă firma, codul fiscal („Cod
    TVA RO…”, firma e plătitoare) și momentul generării („Generată la ZZ.LL.AAAA hh:mm”)."""
    v = _nota(firma, "2026-09-05", [{"debit": "5311", "credit": "1012", "suma": "300.00"}], "Aport capital", valideaza=True)
    try:
        pg = patron.pg
        _balanta(patron, firma, 2026, 9)
        with pg.expect_download(timeout=60000) as dl:
            pg.click("#b-pdf")
        cale = _os.path.join(_os.environ.get("E2E_CAPTURI", "/tmp"), "167_balanta_09_2026.pdf")
        dl.value.save_as(cale)
        text = _sp.run(["pdftotext", "-layout", cale, "-"], capture_output=True, text=True, check=True).stdout
        cui = sql('SELECT cui FROM "%s".firma_profil WHERE id = 1' % firma["schema"])[0][0]
        cifre = "".join(ch for ch in str(cui) if ch.isdigit())
        assert "Cod TVA RO%s" % cifre in text, text[:600]
        assert _re.search(r"Generată la %s \d{2}:\d{2}" % _re.escape(AZI.strftime("%d.%m.%Y")), text), text[:600]
        patron.captura("balanta_pdf_descarcat")
    finally:
        _sterge_note(firma, [v])


# ------------------------------------------------------------------------------------------------ Plan de conturi (166)

def _plan(ecran, f, cauta):
    _card(ecran, f, "planconturi", "#pcf-cauta")
    ecran.pg.wait_for_selector("#pcf-lista .pf-frand", timeout=30000)
    ecran.pg.fill("#pcf-cauta", cauta)
    ecran.pg.wait_for_function("(q) => [...document.querySelectorAll('#pcf-lista [data-simbol]')].every((e) => e.innerText.toLowerCase().includes(q))"
                               " || !!document.querySelector('#pcf-lista .stare-goala')", arg=cauta.lower(), timeout=30000)
    return ecran.pg.evaluate("() => [...document.querySelectorAll('#pcf-lista [data-simbol]')].map((e) => e.dataset.simbol)")


def test_def_166_conturile_731_738_scoase(patron, firma):
    """166. Plan de conturi: 731–738 scoase din șablon și din firme.
    Pașii contabilului: firma nouă (din șablon) -> Plan de conturi -> caută „73”: niciun cont 731–738 (conturile entităților fără scop
    patrimonial, OMFP 3103/2017), iar 711 e acolo -> aceeași căutare pe o firmă existentă care nu le folosea („Constructii Profit Trim”)."""
    simb = _plan(patron, firma, "73")
    assert not [s for s in simb if s[:3] in ("731", "732", "733", "734", "736", "738")], simb
    assert "711" in _plan(patron, firma, "711")
    _plan(patron, firma, "73")
    patron.captura("firma_noua_fara_731")
    # o firmă existentă care nu le folosește (decizia: se scot numai unde nu sunt folosite — „Comert Micro TVA” are 731 într-o notă)
    simb = _plan(patron, {"nume": "Constructii Profit Trim"}, "73")
    assert not [s for s in simb if s[:3] in ("731", "732", "733", "734", "736", "738")], simb
    assert "711" in _plan(patron, {"nume": "Constructii Profit Trim"}, "711")
    _plan(patron, {"nume": "Constructii Profit Trim"}, "73")
    patron.captura("firma_existenta_fara_731")


# ------------------------------------------------------------------------------------------------ Chitanțe (168)

def test_def_168_nota_chitantei_numeste_chitanta_si_factura(patron, firma, facturi_emise):
    """168. Chitanțe: descrierea notei doar numele clientului.
    Pașii contabilului: factura emisă azi -> din detaliul ei „Emite chitanță” pe tot totalul -> Registrul jurnal pe luna curentă: nota
    chitanței spune felul, chitanța (seria-numărul) și factura stinsă, nu doar numele clientului."""
    pg = patron.pg
    cui = cui_cu_control(31000168)
    fe = _ok(_api(patron, "POST", "/tenants/%d/facturi/emite" % firma["tenant_id"], {
        "tert_nume": "Client Chitanta SRL", "tert_cui": cui, "data_emitere": AZI.isoformat(),
        "linii": [{"descriere": "Servicii probă 168", "cantitate": 1, "pret_unitar": 100, "cota_tva": 21, "cont_venit": "704"}]}))
    fid, nr = fe["factura_id"], fe["numar"]
    _card(patron, firma, "facturi", "#fac-istoric")
    pg.click("#fac-istoric")
    pg.click(".fac-frand-btn[data-id='%s']" % fid)
    pg.click("#fd-chitanta")
    pg.wait_for_selector("#fd-chit-ok")
    pg.click("#fd-chit-ok")
    _asteapta_text(patron, "a fost emisă și înregistrată în Registrul de casă")
    ch = sql('SELECT serie, numar FROM "%s".chitante WHERE factura_id = %%s' % firma["schema"], (fid,))
    assert len(ch) == 1, ch
    eticheta_ch = "%s-%s" % ch[0]
    _card(patron, firma, "jurnal", "#j-prev")
    _asteapta_text(patron, "chitanța " + eticheta_ch)
    nota = [n for n in _randuri_jurnal(patron) if ("chitanța " + eticheta_ch) in n[0]]
    assert len(nota) == 1, _randuri_jurnal(patron)
    antet = nota[0][0]
    assert "contravaloare factura %s din %s" % (nr, AZI.strftime("%d.%m.%Y")) in antet, antet
    assert "Client Chitanta SRL" in antet, antet
    assert any(x.startswith("5311 = 4111") and "121,00" in x for x in nota[0][1]), nota
    pg.locator(".fereastra:last-of-type [data-nota-id]", has_text=eticheta_ch).first.scroll_into_view_if_needed()
    patron.captura("nota_chitantei")


# ------------------------------------------------------------------------------------------------ Coadă (152)

def test_def_152_validarea_mai_multor_note_deodata(patron, junior, firma):
    """152. Coadă: validarea mai multor note deodată.
    Pașii contabilului: asistentul („Poate pregăti”) scrie trei note în luna curentă (intră singure în coadă) -> contabilul-șef
    deschide „De validat”, bifează cele trei note și apasă „Validează selectate (3)” -> confirmarea „Ai validat 3 note.” și cele trei
    note sunt validate în jurnal."""
    tid = firma["tenant_id"]
    ids = []
    for i, suma in enumerate(("10.00", "20.00", "30.00")):
        r = _ok(_api(junior, "POST", "/tenants/%d/jurnal" % tid, {
            "descriere": "Ridicare numerar 152-%d" % i, "data": AZI.replace(day=2).isoformat(), "document_ref": "CEC 152-%d" % i,
            "linii": [{"debit": "5311", "credit": "5121", "suma": suma}]}))
        ids.append(r["id"])
    coada = sql("SELECT id FROM public.declaratii_coada WHERE tenant_id = %s AND fel = 'nota' AND stare = 'la_senior' "
                "AND perioada = ANY(%s) ORDER BY id", (tid, ["nota-%d" % i for i in ids]))
    coada = [x[0] for x in coada]
    assert len(coada) == 3, coada
    pg = patron.pg
    patron.acasa()
    pg.click("button.cab-card:has([data-cheie='validat'])")
    pg.wait_for_selector("#val-aproba-selectate", timeout=30000)
    for cid in coada:
        pg.check(".val-sel[data-nota='%d']" % cid)
    assert pg.inner_text("#val-aproba-selectate") == "Validează selectate (3)"
    patron.captura("trei_bifate")
    pg.click("#val-aproba-selectate")
    _asteapta_text(patron, "Ai validat 3 note.")
    st = sql('SELECT status FROM "%s".inregistrari WHERE id = ANY(%%s)' % firma["schema"], (ids,))
    assert sorted(x[0] for x in st) == ["validata"] * 3, st
    patron.captura("validate_deodata")


# ------------------------------------------------------------------------------------------------ NIR fără factură (144, 146, 153)

def _nir(f, numar, data, furnizor, cui, cantitate, pret, pret_vanzare=None):
    """NIR „fără factură” pe drumul ecranului Stocuri (`stocuri_api.adauga_nir`), cu notele validate."""
    from core import db, stocuri_api
    linie = {"denumire": "Marfa %s" % numar, "cantitate": cantitate, "pret_achizitie": pret, "cota_tva": 21, "um": "buc"}
    if pret_vanzare is None:
        linie["articol_nou"] = True
    else:
        linie["pret_vanzare"] = pret_vanzare
    with db.get_conn(f["schema"]) as c:
        r = stocuri_api.adauga_nir(c, f["schema"], {"numar": numar, "data": data, "furnizor": furnizor, "cui": cui, "linii": [linie]})
        assert "eroare" not in r, r
        c.commit()
    nir = sql('SELECT id, inregistrari_ids FROM "%s".nir WHERE numar = %%s' % f["schema"], (numar,))[0]
    note = nir[1] if isinstance(nir[1], list) else _json.loads(nir[1])
    _valideaza_note(f, note)
    return nir[0], note


def _factura_primita(f, numar, data, furnizor, cui, cantitate, pret):
    from core import db, facturi_api
    with db.get_conn(f["schema"]) as c:
        r = facturi_api.creeaza_factura(c, numar, data, "primita",
                                        [{"descriere": "Marfa", "cantitate": cantitate, "pret_unitar": pret, "cota_tva": 21}],
                                        tert_nume=furnizor, tert_cui="RO" + cui)
        c.commit()
    return r["factura_id"]


def _linii_nota(f, nid):
    return sorted((d, c, str(s)) for d, c, s in sql('SELECT cont_debit, cont_credit, suma FROM "%s".inregistrari_linii '
                                                    'WHERE inregistrare_id = %%s' % f["schema"], (nid,)))


def _conteaza_cu_legare(ecran, f, fid, an, luna, nir_numar):
    """Istoric facturi pe luna facturii -> „Contează” -> caseta „NIR-ul acestei livrări” -> alege NIR-ul -> „Leagă de NIR-ul ales”."""
    pg = ecran.pg
    _card(ecran, f, "facturi", "#fac-istoric")
    pg.click("#fac-istoric")
    _la_luna(ecran, "#fac-prev", an, luna)
    pg.click(".fac-cont[data-cid='%s']" % fid)
    pg.wait_for_selector("#nir-legat", timeout=30000)
    opt = pg.evaluate("() => [...document.querySelectorAll('#nir-legat option')].map((o) => [o.value, o.innerText])")
    ales = [v for v, t in opt if ("NIR nr %s " % nir_numar) in t]
    assert ales, opt
    pg.select_option("#nir-legat", ales[0])
    ecran.captura("caseta_nir")
    pg.click("#nir-leaga")
    pg.wait_for_selector(".fac-frand-btn[data-id='%s'] ~ * .tip-desc, .tip-desc:has-text('ciornă #')" % fid, timeout=60000)
    txt = ecran.fereastra()
    m = _re.search(r"ciornă #(\d+)", txt)
    assert m, txt[:800]
    return int(m.group(1)), opt


def test_def_144_factura_dupa_nir_fara_factura_se_leaga_fara_a_doua_intrare(patron, firma):
    """144. NIR/factură: factura după NIR fără factură se leagă (408 = 401), fără a doua intrare în stoc.
    Pașii contabilului (firmă la cantitativ-valoric): NIR fără factură, 10 buc × 55 lei (marfa intră în fișă) -> vine factura
    furnizorului, aceeași livrare -> Istoric facturi, „Contează”: aplicația propune NIR-ul (același furnizor, același cost) -> „Leagă” ->
    nota facturii e 408 = 401 (665,50), fără 371 = 401 -> Stocuri: articolul are tot 10 buc / 550,00 lei (o singură intrare)."""
    cui = cui_cu_control(32000144)
    nir_id, _ = _nir(firma, "E144", "2026-08-05", "Furnizor 144 SRL", cui, 10, 55)
    fid = _factura_primita(firma, "FF-144", "2026-08-12", "Furnizor 144 SRL", cui, 10, 55)
    nota, opt = _conteaza_cu_legare(patron, firma, fid, 2026, 8, "E144")
    assert any("— propus" in t for v, t in opt if "NIR nr E144 " in t), opt
    linii = _linii_nota(firma, nota)
    assert ("408", "401", "665.50") in linii and not [x for x in linii if x[0] == "371"], linii
    assert sql('SELECT factura_id FROM "%s".nir WHERE id = %%s' % firma["schema"], (nir_id,)) == [(fid,)]
    _card(patron, firma, "stocuri", "#s-situatie-tabel")
    rand = patron.pg.locator("#s-situatie-tabel tr", has_text="Marfa E144").first.locator("td").all_inner_texts()
    assert rand[2] == "10" and rand[4] == "550,00", rand
    intrari = sql('SELECT count(*) FROM "%s".miscari_stoc m JOIN "%s".articole a ON a.id = m.articol_id '
                  "WHERE a.denumire = 'Marfa E144' AND m.tip = 'intrare'" % (firma["schema"], firma["schema"]))
    assert intrari == [(1,)], intrari
    patron.captura("stoc_o_singura_intrare")
    _card(patron, firma, "jurnal", "#j-prev")
    _la_luna(patron, "#j-prev", 2026, 8)
    patron.pg.locator("[data-nota-id='%d']" % nota).scroll_into_view_if_needed()
    sub = patron.pg.inner_text("[data-nota-id='%d'] .pf-frand-sub" % nota)
    assert "408 = 401 · 665,50" in sub and "371 = 401" not in sub, sub
    patron.captura("nota_factura_408_401")


def test_def_146_tva_nir_pe_4428_pana_la_factura_apoi_4426(patron, firma):
    """146. NIR: TVA pe 4428 până la factură, apoi 4426.
    Pașii contabilului: NIR fără factură, 4 buc × 50 lei -> Registrul jurnal: nota NIR-ului are TVA-ul pe 4428.01 = 408 (42,00), nu pe
    4426 -> vine factura și se contează legată de NIR -> nota facturii trece TVA-ul în deductibil: 4426 = 4428.01 (42,00)."""
    cui = cui_cu_control(33000146)
    _nir_id, note_nir = _nir(firma, "E146", "2026-08-06", "Furnizor 146 SRL", cui, 4, 50)
    pg = patron.pg
    _card(patron, firma, "jurnal", "#j-prev")
    _la_luna(patron, "#j-prev", 2026, 8)
    subs = " | ".join(pg.inner_text("[data-nota-id='%d'] .pf-frand-sub" % n) for n in note_nir)
    assert "4428.01 = 408 · 42,00" in subs and "4426 =" not in subs, subs
    pg.locator("[data-nota-id='%d']" % note_nir[0]).scroll_into_view_if_needed()
    patron.captura("nir_tva_pe_4428_01")
    fid = _factura_primita(firma, "FF-146", "2026-08-14", "Furnizor 146 SRL", cui, 4, 50)
    nota, _ = _conteaza_cu_legare(patron, firma, fid, 2026, 8, "E146")
    assert ("4426", "4428.01", "42.00") in _linii_nota(firma, nota)
    _card(patron, firma, "jurnal", "#j-prev")
    _la_luna(patron, "#j-prev", 2026, 8)
    sub = pg.inner_text("[data-nota-id='%d'] .pf-frand-sub" % nota)
    assert "4426 = 4428.01 · 42,00" in sub and "4426 = 401" not in sub, sub
    pg.locator("[data-nota-id='%d']" % nota).scroll_into_view_if_needed()
    patron.captura("factura_4426_din_4428_01")


def test_def_145_nir_din_exercitiul_trecut_se_leaga_cat_408_e_deschis(patron, firma_gv):
    """145. NIR: NIR din exercițiul trecut se leagă cât 408 e deschis.
    Pașii contabilului (global-valoric): NIR fără factură din 12/2025, 10 buc × 55 lei, validat -> factura vine în 07/2026, la 60 lei
    -> „Contează”: NIR-ul din 2025 e printre cele de legat (fără propunere — costul diferă) -> îl alege -> nota facturii, datată în
    07/2026: 408 = 401 (665,50), 4426 = 4428.01 (115,50), diferența de preț 378 = 401 (50,00) și de TVA 4426 = 401 (10,50); notele NIR-ului
    din 2025 rămân neatinse (exercițiul închis nu se modifică)."""
    cui = cui_cu_control(34000145)
    nir_id, note_nir = _nir(firma_gv, "E145", "2025-12-10", "Furnizor 145 SRL", cui, 10, 55, pret_vanzare=80)
    inainte = {n: _linii_nota(firma_gv, n) for n in note_nir}
    fid = _factura_primita(firma_gv, "FF-145", "2026-07-15", "Furnizor 145 SRL", cui, 10, 60)
    nota, opt = _conteaza_cu_legare(patron, firma_gv, fid, 2026, 7, "E145")
    assert not any("— propus" in t for v, t in opt), opt
    linii = _linii_nota(firma_gv, nota)
    for x in (("408", "401", "665.50"), ("4426", "4428.01", "115.50"), ("378", "401", "50.00"), ("4426", "401", "10.50")):
        assert x in linii, linii
    assert sql('SELECT data FROM "%s".inregistrari WHERE id = %%s' % firma_gv["schema"], (nota,)) == [(_dt.date(2026, 7, 15),)]
    assert {n: _linii_nota(firma_gv, n) for n in note_nir} == inainte
    assert sql('SELECT factura_id FROM "%s".nir WHERE id = %%s' % firma_gv["schema"], (nir_id,)) == [(fid,)]
    _card(patron, firma_gv, "jurnal", "#j-prev")
    _la_luna(patron, "#j-prev", 2026, 7)
    sub = patron.pg.inner_text("[data-nota-id='%d'] .pf-frand-sub" % nota)
    assert "408 = 401 · 665,50" in sub and "378 = 401 · 50,00" in sub, sub
    patron.pg.locator("[data-nota-id='%d']" % nota).scroll_into_view_if_needed()
    patron.captura("factura_2026_legata_de_nir_2025")


# ------------------------------------------------------------------------------------------------ Declarații: D406 / D394 (154, 155, 164, 165, 163)

@pytest.fixture(scope="module")
def facturi_emise(firma):
    """Facturile emise în luna curentă pe drumul emiterii: F1A1 (800 la 21%), F1A2 (5.000 la 21% + 800 la 11%), F1A3 (200 la 21%) din
    seria F1A, plus o factură veche fără serie, nr. „2” (`facturi_api.creeaza_factura`, cum intrau înainte de seria obligatorie)."""
    from core import db, facturi_api
    with db.get_conn(firma["schema"]) as c:
        r = facturi_api.seteaza_numerotare(c, serie="F1A", numar_start=1)
        assert r.get("ok"), r
        c.commit()
    cui = cui_cu_control(35000154)
    linii = [[(800, 21)], [(5000, 21), (800, 11)], [(200, 21)]]
    emise = []
    with db.get_conn(firma["schema"]) as c:
        for ls in linii:
            r = facturi_api.emite_factura(c, [{"descriere": "Servicii consultanță %s" % p, "cantitate": 1, "pret_unitar": p,
                                                "cota_tva": q, "cont_venit": "704"} for p, q in ls],
                                          tert_nume="Client D406 SRL", tert_cui=cui, data_emitere=AZI.replace(day=3).isoformat(),
                                          status="emisa")
            assert r.get("ok"), r
            emise.append((r["factura_id"], r["numar"]))
        r = facturi_api.creeaza_factura(c, "2", AZI.replace(day=4).isoformat(), "emisa",
                                        [{"descriere": "Servicii fără serie", "cantitate": 1, "pret_unitar": 300, "cota_tva": 21}],
                                        tert_nume="Client D406 SRL", tert_cui=cui)
        emise.append((r["factura_id"], "2"))
        c.commit()
    return emise


def _declaratie(ecran, f, tip, an, luna):
    pg = ecran.pg
    _card(ecran, f, "declaratii", "#dec-tip")
    pg.select_option("#dec-tip", tip)
    pg.fill("#dec-an", str(an))
    pg.dispatch_event("#dec-an", "change")
    if pg.locator("#dec-luna").count():
        pg.select_option("#dec-luna", str(luna))
    else:
        pg.select_option("#dec-trim", str((luna - 1) // 3 + 1))
    pg.click("#dec-continua")
    pg.wait_for_selector("details.dec-xml summary:text('Vezi XML-ul generat')", timeout=90000)


def _sectiune(ecran, nume):
    """Tabelul unei secțiuni din „Din ce e făcută declarația”: (antete, [[celule]])."""
    return ecran.pg.evaluate("""(n) => { const e = [...document.querySelectorAll('.camp-eticheta')].find((x) => x.innerText.startsWith(n));
        if (!e) return null; const t = e.parentElement.querySelector('table');
        return [[...t.querySelectorAll('th')].map((x) => x.innerText), [...t.querySelectorAll('tbody tr')].map((r) => [...r.querySelectorAll('td')].map((x) => x.innerText))]; }""", nume)


def _deschide_componente(ecran):
    ecran.pg.click("details.dec-xml summary:has-text('Din ce e făcută declarația')")


def test_def_154_d406_liniile_facturilor_cu_suma_lor(patron, firma, facturi_emise):
    """154. D406: liniile facturilor „707 · credit 0,00”.
    Pașii contabilului: facturile lunii emise (F1A1 800 lei; F1A2 5.000 lei la 21% + 800 lei la 11%; F1A3 200 lei) -> Declarații, D406
    pe luna curentă -> „Din ce e făcută declarația”, „Facturi de vânzare”: liniile arată „707 · credit 800,00” / „5.000,00” / „200,00”,
    nu „credit 0,00” -> XML-ul: F1A2 are câte un total pe cotă (bază 5000.00 la 21% și 800.00 la 11%)."""
    pg = patron.pg
    _declaratie(patron, firma, "d406", AZI.year, AZI.month)
    _deschide_componente(patron)
    sec = _sectiune(patron, "Facturi de vânzare")
    assert sec, "secțiunea „Facturi de vânzare” lipsește"
    text = " | ".join(" ".join(r) for r in sec[1])
    for s in ("707 · credit 800,00", "707 · credit 5.000,00", "707 · credit 200,00"):
        assert s in text, text
    assert "credit 0,00" not in text, text
    pg.locator(".camp-eticheta", has_text="Facturi de vânzare").scroll_into_view_if_needed()
    patron.captura("d406_facturi_vanzare")
    xml = pg.locator("details.dec-xml:has(summary:text('Vezi XML-ul generat')) pre").text_content()
    bloc = xml[xml.index("<InvoiceNo>F1A2</InvoiceNo>"):]
    bloc = bloc[:bloc.index("</Invoice>")]
    assert "<TaxBase>5000.00</TaxBase>" in bloc and "<TaxBase>800.00</TaxBase>" in bloc, bloc[-1500:]


def test_def_155_d394_numarul_fara_cifrele_seriei_si_semnal_fara_serie(patron, firma, facturi_emise):
    """155. D394: F1A3 cu nr. 13; lipsea semnalul pentru factură fără serie.
    Pașii contabilului: facturile lunii F1A1–F1A3 și una veche fără serie („2”) -> Declarații, D394 pe luna curentă -> „Serii de facturi
    declarate”: seria F1A de la 1 la 3 (nu 11–13) -> avertismentul „O factură emisă fără serie (nr. 2)”."""
    pg = patron.pg
    _declaratie(patron, firma, "d394", AZI.year, AZI.month)
    _deschide_componente(patron)
    sec = _sectiune(patron, "Serii de facturi declarate")
    assert sec, "secțiunea „Serii de facturi declarate” lipsește"
    nrs = sorted(int(x[0][3:]) for x in sql('SELECT numar FROM "%s".facturi WHERE serie = \'F1A\'' % firma["schema"]))   # „F1A3” -> 3
    f1a = [r for r in sec[1] if "F1A" in r]
    assert f1a and nrs[0] == 1, (sec, nrs)
    assert str(nrs[0]) in f1a[-1] and str(nrs[-1]) in f1a[-1], (f1a, nrs)
    assert "1%d" % nrs[-1] not in f1a[-1] and "1%d" % nrs[0] not in f1a[-1], (f1a, nrs)   # forma veche: cifrele seriei lipite
    pg.locator(".camp-eticheta", has_text="Serii de facturi declarate").scroll_into_view_if_needed()
    patron.captura("d394_serii")
    av = pg.inner_text(".dec-avert:has(.dec-avert-cap:has-text('Avertismente'))")
    assert "O factură emisă fără serie (nr. 2)" in av, av
    pg.locator(".dec-avert:has(.dec-avert-cap:has-text('Avertismente'))").scroll_into_view_if_needed()
    patron.captura("d394_fara_serie")


def _fara_suprapuneri(ecran):
    """Copiii direcți ai corpului ferestrei (DS cap.9 v2.84): conținutul fiecăruia se termină înaintea fratelui următor (nimic nu
    curge peste „Vezi XML-ul generat”, textul de subsol sau „Trimite în coadă”), iar o secțiune pliabilă închisă are doar înălțimea
    titlului ei (fără gol mare). Întoarce lista problemelor, cu dimensiunile măsurate."""
    return ecran.pg.evaluate("""() => {
      const corp = [...document.querySelectorAll('.fereastra')].pop().querySelector('.fereastra-corp');
      const copii = [...corp.children].filter((e) => e.getBoundingClientRect().height > 0);
      const nume = (e) => (e.tagName === 'DETAILS' ? 'details «' + e.querySelector('summary').innerText.slice(0, 30) + '»' : (e.id || e.className || e.tagName));
      const rele = [];
      copii.forEach((e, i) => {
        const r = e.getBoundingClientRect();
        let jos = r.bottom;
        e.querySelectorAll('*').forEach((x) => {
          const d = x.closest('details');
          if (d && !d.open && !x.closest('summary')) return;   // conținutul unei secțiuni pliate nu se vede
          const rx = x.getBoundingClientRect(); if (rx.height > 0) jos = Math.max(jos, rx.bottom); });
        if (e.tagName === 'DETAILS' && !e.open) {
          const s = e.querySelector('summary').getBoundingClientRect().height;
          if (r.height > s + 24) rele.push('gol în ' + nume(e) + ': ' + Math.round(r.height) + 'px față de titlul de ' + Math.round(s) + 'px');
        }
        const u = copii[i + 1];
        if (u && u.getBoundingClientRect().top < jos - 1)
          rele.push(nume(u) + ' acoperit de conținutul lui ' + nume(e) + ' (' + Math.round(jos - u.getBoundingClientRect().top) + 'px)');
      });
      return rele; }""")


def test_def_164_d406_d394_fara_suprapuneri_si_goluri(patron, firma, facturi_emise):
    """164. D406/D394: suprapuneri și spații goale.
    Pașii contabilului: D406 pe luna curentă -> deschide „Din ce e făcută declarația” -> tabelul nu curge peste „Vezi XML-ul generat”,
    peste textul de subsol și peste „Trimite în coadă”, iar între secțiuni nu sunt goluri mari -> la fel pe D394."""
    for tip in ("d406", "d394"):
        _declaratie(patron, firma, tip, AZI.year, AZI.month)
        assert _fara_suprapuneri(patron) == [], tip
        _deschide_componente(patron)
        patron.pg.wait_for_timeout(300)
        probleme = _fara_suprapuneri(patron)
        assert probleme == [], (tip, probleme)
        patron.pg.locator("#dec-trimite").scroll_into_view_if_needed()
        patron.captura("%s_componente_deschise" % tip)


def test_def_165_d406_caseta_rezumat_se_vede(patron, firma, facturi_emise):
    """165. D406: caseta „Rezumat” nu se vedea.
    Pașii contabilului: Declarații, D406 pe luna curentă -> la pasul 2 se vede caseta „Rezumat” cu cifrele declarației."""
    pg = patron.pg
    _declaratie(patron, firma, "d406", AZI.year, AZI.month)
    caseta = pg.locator(".caseta-info:has(.ci-mesaj:text-is('Rezumat'))")
    assert caseta.count() == 1 and caseta.is_visible()
    assert len(caseta.locator("li").all_inner_texts()) >= 1
    caseta.scroll_into_view_if_needed()
    patron.captura("d406_rezumat")


_COD = _re.compile(r"\b(?:[a-z]+_[a-z0-9_]+|NEVERIFICAT\w*|ATENTIE|R\d+_\d+(?:_\d+)?|None|False|True)\b")
_FARA_DIACRITICE = ("apartin", "incrucisat", "ATENTIE", "atentie", "Atentie", "sold initial", "liniara", "varsat")


def _defecte_limba(text):
    gasite = sorted(set(_COD.findall(text)))
    gasite += [w for w in _FARA_DIACRITICE if _re.search(r"\b%s\b" % w, text)]
    return gasite


def test_def_163_texte_fara_limbaj_de_programator(patron, firma, facturi_emise):
    """163. Texte: limbaj de programator, lipsă diacritice, majuscule.
    Pașii contabilului: deschide ecranele în care au apărut (08.10) codurile interne — Control fiscal al firmei, D406 și D394 cu
    componentele deschise, Mijloace fixe, Închidere lună, Date firmă — și citește textul: niciun identificator de cod
    (partener_id, self_billing, R3_1_1, tva_standard, d100_fapt, NEVERIFICAT, False/None) și niciun cuvânt fără diacritice
    din lista retestului („ATENTIE”, „apartin”, „incrucisat”, „sold initial”, „liniara”)."""
    pg = patron.pg
    defecte = {}
    _card(patron, firma, "control", ".cf-stare-mare")
    pg.evaluate("() => document.querySelectorAll('details').forEach((d) => { d.open = true; })")
    defecte["control fiscal"] = _defecte_limba(patron.fereastra())
    patron.captura("control_fiscal")
    for tip in ("d406", "d394"):
        _declaratie(patron, firma, tip, AZI.year, AZI.month)
        pg.evaluate("() => document.querySelectorAll('details.dec-xml').forEach((d) => { if (!d.innerText.includes('<?xml')) d.open = true; })")
        t = pg.evaluate("() => { const f = [...document.querySelectorAll('.fereastra')].pop(); const p = [...f.querySelectorAll('pre.dec-xml-pre')];"
                        " p.forEach((x) => { x.style.display = 'none'; }); const t = f.innerText; p.forEach((x) => { x.style.display = ''; }); return t; }")
        assert "Din ce e făcută declarația" in t, t[:300]   # textul citit e chiar al ecranului declarației
        defecte[tip] = _defecte_limba(t)
        patron.captura(tip)
    for cheie, sel in (("inchidere", "#il-lock"), ("datefirma", "#df-luna_preluare")):
        _card(patron, firma, cheie, sel)
        pg.wait_for_timeout(800)
        defecte[cheie] = _defecte_limba(patron.fereastra())
    assert not any(defecte.values()), defecte


def test_def_184_formatele_pe_declaratii_si_casa(patron, firma, facturi_emise):
    """184. Formate: date ISO, jurnale majuscule, perioade în patru formate, „1 parteneri”, mesaje de respingere lungi.
    [partea rămasă, registrul: „fără test: cere generarea D406/D394 pe o firmă comună (scriere)”; acum pe firma sintetică a rulării]
    Pașii: firma cu facturile emise în luna curentă -> D394 și D406 generate, cu componentele deschise (XML-ul lăsat deoparte) -> Casă:
    textul judecat de aceeași măsură ca ecranele (`core.limba_ecran.defecte`), pe cele patru feluri ale deficienței — nicio dată ISO,
    nicio perioadă în altă formă decât LL/AAAA, T3/2026 sau anul, niciun „1 parteneri”, niciun cuvânt (numele unui jurnal) în
    majuscule. (Respingerea numită scurt: `e2e_bloc_c.py::test_def_91_respingerea_e_confirmata_pe_ecran`.)"""
    from core import limba_ecran
    # notele facturilor validate: D406 are atunci jurnale (GeneralLedgerEntries), deci numele lor ajung pe ecran
    _valideaza_note(firma, [i for (i,) in sql('SELECT id FROM "%s".inregistrari WHERE status = \'ciorna\' AND factura_id IS NOT NULL'
                                              % firma["schema"])])
    pg = patron.pg
    feluri = {"data", "perioada", "acord", "majuscule"}
    gasite = {}
    for tip in ("d394", "d406"):
        _declaratie(patron, firma, tip, AZI.year, AZI.month)
        pg.evaluate("() => document.querySelectorAll('details.dec-xml').forEach((d) => { if (!d.innerText.includes('<?xml')) d.open = true; })")
        t = pg.evaluate("() => { const f = [...document.querySelectorAll('.fereastra')].pop(); const p = [...f.querySelectorAll('pre.dec-xml-pre')];"
                        " p.forEach((x) => { x.style.display = 'none'; }); const t = f.innerText; p.forEach((x) => { x.style.display = ''; }); return t; }")
        assert "Din ce e făcută declarația" in t, t[:300]
        if tip == "d406":
            assert "Jurnal" in t or "jurnal" in t, t[:600]          # jurnalele SAF-T apar pe ecran, numite în cuvinte
        gasite[tip] = [d for d in limba_ecran.defecte(t) if d[0] in feluri]
        patron.captura(tip)
    _card(patron, firma, "casa", "#c-toggle")
    pg.wait_for_timeout(800)
    gasite["casa"] = [d for d in limba_ecran.defecte(patron.fereastra()) if d[0] in feluri]
    assert not any(gasite.values()), gasite


# ------------------------------------------------------------------------------------------------ Control fiscal (148, 156, 157, 158, 159)

@pytest.fixture()
def preluata_07(firma):
    """Luna preluării salvată în Date firmă: 07/2026 (pe drumul ecranului), refăcută la final; marcările scoase."""
    from core import db, firma_profil_api as fp
    with db.get_conn(firma["schema"]) as c:
        r = fp.salveaza_date(c, {"luna_preluare": "2026-07"}, tenant_id=firma["tenant_id"], user_id=_uid())
        assert r.get("ok"), r
        c.commit()
    try:
        yield firma
    finally:
        sql("DELETE FROM public.declaratii_depuse WHERE tenant_id = %s AND sursa IN ('extern', 'contabil_anterior')", (firma["tenant_id"],))
        sql('UPDATE "%s".firma_profil SET luna_preluare = NULL WHERE id = 1' % firma["schema"])


@pytest.fixture()
def preluata_07_fara_activitate():
    """O firmă proprie a testului (`conftest.firma_noua`), completată ca `firma` și preluată în 07/2026, FĂRĂ niciun document în 2026.
    De ce nu `firma`: facturile altor probe din 10/2026 dovedesc existența firmei în 2026, iar atunci D100 T1/T2 2026, fără venituri,
    nu se mai datorează (`control_fiscal_api.d100_fapt`, „fără venituri în trimestru”) — nu mai sunt în grupul „Înainte de preluare”.
    Situația din retest (212) e a anului nedovedit, deci proba îi cere firma ei."""
    from conftest import firma_noua
    from core import db, firma_profil_api as fp
    gen = firma_noua()
    f = _completeaza(next(gen), "cantitativ_valoric")
    try:
        with db.get_conn(f["schema"]) as c:
            r = fp.salveaza_date(c, {"luna_preluare": "2026-07"}, tenant_id=f["tenant_id"], user_id=_uid())
            assert r.get("ok"), r
            c.commit()
        yield f
    finally:
        gen.close()


def _control(ecran, f):
    _card(ecran, f, "control", ".cf-stare-mare")


def test_def_159_marcarea_nu_muta_ecranul_de_pe_rand(patron, preluata_07):
    """159. Control fiscal: marcarea — mesajul rămânea, fereastra sărea, nu se putea modifica/anula.
    [partea rămasă, registrul: „rândul atins urcă cu ~100 px (y 451 -> 351 …)”] Cauza, măsurată: focusul pe câmpul de dată derula
    câmpul în CENTRUL zonei când formularul se deschidea sub marginea de jos (D100 T4/2025, rândul jos pe ecran: 827 -> 352 px).
    Pașii: firma preluată în 07/2026 -> Control fiscal -> „Înainte de preluare” -> rândul D100 T4/2025 adus la marginea de jos ->
    „Marchează depusă în afara iConta.eu”: rândul se mișcă cel mult cât să se vadă formularul, iar câmpul de dată are focusul ->
    data, „Salvează”: rândul rămâne unde era -> „Anulează marcarea”, confirmă: la fel."""
    pg = patron.pg
    _control(patron, preluata_07)
    pg.click("details.cf-inainte > summary")
    rand = ".fereastra:last-of-type [data-cheie='d100-2025-12']"
    pg.wait_for_selector(rand + " .cf-extern-btn", timeout=30000)
    pg.eval_on_selector(rand + " .cf-extern-btn", "e => e.scrollIntoView({block: 'end'})")
    y = lambda: pg.eval_on_selector(rand, "e => Math.round(e.getBoundingClientRect().top)")   # noqa: E731
    y0 = y()
    patron.captura("inainte")
    pg.eval_on_selector(rand + " .cf-extern-btn", "b => b.click()")   # clicul omului, pe loc (clicul Playwright aduce ținta în centru)
    pg.wait_for_selector(rand + " .cf-extern-form input[type=date]", timeout=10000)
    pg.wait_for_timeout(300)
    form = pg.eval_on_selector(rand + " .cf-extern-form", "f => { const c = f.closest('.fereastra-corp').getBoundingClientRect();"
                               " const r = f.getBoundingClientRect(); return {h: Math.round(r.height), jos: Math.round(r.bottom),"
                               " zona: Math.round(c.bottom), focus: document.activeElement === f.querySelector('input[type=date]')}; }")
    y1 = y()
    patron.captura("formular")
    assert form["focus"] and form["jos"] <= form["zona"] + 1, form
    assert y0 - y1 <= form["h"] + 16, "rândul a sărit la deschiderea formularului: %s -> %s px (formularul are %s px)" % (y0, y1, form["h"])
    pg.fill(rand + " .cf-extern-form input[type=date]", "2026-02-20")
    pg.click(rand + " .cf-extern-salveaza")
    pg.wait_for_selector(rand + " .cf-extern-anuleaza", timeout=60000)
    y2 = y()
    assert abs(y2 - y1) <= 4, "rândul a sărit după „Salvează”: %s -> %s px" % (y1, y2)
    pg.click(rand + " .cf-extern-anuleaza")
    # caseta de confirmare apare sub rând; aplicația o aduce în vedere cu derulare minimă (`aduInVedere`, `nearest`, lină) —
    # clicul vine după ce s-a oprit derularea, ca Playwright să nu mai mute el ținta în centru
    pg.wait_for_function("() => { const b = document.querySelector('#ca-ok'); if (!b) return false; const r = b.getBoundingClientRect();"
                         " const c = b.closest('.fereastra-corp').getBoundingClientRect(); const t = Math.round(r.top);"
                         " const ok = r.bottom <= c.bottom + 1 && window._caY === t; window._caY = t; return ok; }", timeout=10000,
                         polling=200)
    caseta = pg.eval_on_selector("#caseta-atentie-activa", "e => Math.round(e.getBoundingClientRect().height)")
    y3 = y()
    assert y1 - y3 <= caseta + 16, "rândul a sărit la „Anulează marcarea”: %s -> %s px (caseta are %s px)" % (y1, y3, caseta)
    pg.click("#ca-ok")
    pg.wait_for_function("(s) => { const r = document.querySelector(s); return r && !r.querySelector('.cf-extern-anuleaza'); }",
                         arg=rand, timeout=60000)
    y4 = y()
    patron.captura("dupa_anulare")
    assert abs(y4 - y3) <= 4, "rândul a sărit după confirmarea anulării: %s -> %s px" % (y3, y4)


def test_def_157_d100_d205_2025_sunt_inainte_de_preluare(patron, preluata_07):
    """157. Control fiscal: D100/D205 2025 la „Nu pot verifica”.
    Pașii contabilului: firma preluată în 07/2026 -> Control fiscal -> D100 și D205 pe 2025 nu mai sunt la „Nu se poate verifica”: stau în
    grupul „Înainte de preluare în iConta.eu”, fiecare cu perioada lui (T1/2025 … T4/2025, 2025) și termenul."""
    pg = patron.pg
    _control(patron, preluata_07)
    neclar = pg.evaluate("() => { const t = [...document.querySelectorAll('.cf-grup-titlu')].find((x) => x.textContent.trim().startsWith('Nu se poate verifica'));"
                         " return t ? t.nextElementSibling.innerText : ''; }")
    assert not _re.search(r"D100[\s\S]{0,40}2025|D205[\s\S]{0,40}2025", neclar), neclar
    pg.click("details.cf-inainte > summary")
    rand = lambda tip, per: pg.locator("details.cf-inainte .cf-decl-item", has=pg.locator(".mig-sold-cont", has_text=tip)).filter(
        has=pg.locator(".cf-perioada", has_text=per))
    for tip, per in (("D100", "T1/2025"), ("D100", "T4/2025"), ("D205", "2025")):
        assert rand(tip, per).count() >= 1, (tip, per, pg.inner_text("details.cf-inainte"))
        assert "termen " in rand(tip, per).first.inner_text()
    rand("D205", "2025").first.scroll_into_view_if_needed()
    patron.captura("d100_d205_2025_inainte_de_preluare")


def test_def_158_grupul_inainte_de_preluare_pliat_cu_marcheaza_toate(patron, preluata_07):
    """158. Control fiscal: grupul „Înainte de preluare” cu 31–32 de butoane; pliat + „Marchează toate”.
    Pașii contabilului: Control fiscal -> grupul „Înainte de preluare” e pliat (butoanele lui nu se văd) -> îl deschide: are „Marchează
    toate ca depuse de contabilul anterior” -> o apasă și confirmă -> rândurile devin „Depusă de contabilul anterior”."""
    pg = patron.pg
    _control(patron, preluata_07)
    grup = pg.locator("details.cf-inainte")
    assert grup.count() == 1 and not grup.evaluate("(d) => d.open"), "grupul nu e pliat"
    assert not pg.locator("details.cf-inainte .cf-extern-btn").first.is_visible()
    patron.captura("pliat")
    pg.click("details.cf-inainte > summary")
    b = pg.locator("details.cf-inainte .cf-anterior-toate")
    assert b.is_visible() and b.inner_text() == "Marchează toate ca depuse de contabilul anterior"
    n = len(_json.loads(b.get_attribute("data-perioade")))
    assert n >= 2
    b.click()
    pg.click("#ca-ok")
    pg.wait_for_function("() => (document.querySelector('details.cf-inainte') || {}).innerText?.includes('Depusă de contabilul anterior')",
                         timeout=60000)
    marcate = sql("SELECT count(*) FROM public.declaratii_depuse WHERE tenant_id = %s AND sursa = 'contabil_anterior'",
                  (preluata_07["tenant_id"],))[0][0]
    assert marcate == n, (marcate, n)
    patron.captura("marcate_toate")


def _marcheaza(pg, cheie):
    pg.wait_for_selector("details.cf-inainte .cf-decl-item", timeout=30000)
    chei = pg.evaluate("() => [...document.querySelectorAll('details.cf-inainte .cf-decl-item')].map((e) => e.dataset.cheie)")
    assert cheie in chei, chei
    item = pg.locator("details.cf-inainte .cf-decl-item[data-cheie='%s']" % cheie)
    item.scroll_into_view_if_needed()
    return item


def test_def_212_inainte_de_preluare_o_explicatie_si_perioadele_impreuna(patron, preluata_07_fara_activitate):
    """212. Control fiscal, „Înainte de preluare”: text la persoana întâi, repetat pe fiecare rând; D100 T1–T2/2026 în alt grup decât
    D406 T1/2026, deși sunt aceeași perioadă.
    Pașii: firma preluată în 07/2026 -> Control fiscal -> „Înainte de preluare”: explicația grupului apare o dată, sub titlu; niciun rând
    n-o repetă și niciun rând nu vorbește la persoana întâi („nu pot …”); D100 T1/2026 și T2/2026 (perioade dinaintea preluării)
    sunt în grupul acesta, nu la „Nu se poate verifica”."""
    pg = patron.pg
    _control(patron, preluata_07_fara_activitate)
    pg.click("details.cf-inainte > summary")
    pg.wait_for_selector("details.cf-inainte .cf-decl-item", timeout=30000)
    g = pg.evaluate("""() => { const d = document.querySelector('details.cf-inainte');
      return {explicatii: [...d.querySelectorAll(':scope > .cf-incr-temei')].map(e => e.innerText),
              randuri: [...d.querySelectorAll('.cf-decl-item')].map(e => ({cheie: e.dataset.cheie, text: e.innerText}))}; }""")
    patron.captura("inainte")
    assert len(g["explicatii"]) == 1 and "nu se numără la restanțe" in g["explicatii"][0], g["explicatii"]
    assert not [r for r in g["randuri"] if "dinaintea preluării" in r["text"] or _re.search(r"(?i)\bnu pot\b", r["text"])], g["randuri"]
    chei = {r["cheie"] for r in g["randuri"]}
    assert {"d100-2026-3", "d100-2026-6"} <= chei, sorted(chei)


def test_def_213_confirmarea_anularii_spune_perioada_randului(patron, preluata_07):
    """213. Confirmarea anulării marcării scrie „D406 03/2026” pentru T1/2026.
    Pașii: firma preluată în 07/2026 -> Control fiscal -> „Înainte de preluare” -> D100 T4/2025 marcată depusă -> „Anulează marcarea”:
    întrebarea spune „Anulezi marcarea D100 T4/2025?” (perioada rândului), nu „D100 12/2025”."""
    pg = patron.pg
    _control(patron, preluata_07)
    pg.click("details.cf-inainte > summary")
    cheie = "d100-2025-12"
    item = _marcheaza(pg, cheie)
    item.locator(".cf-extern-btn").click()
    item.locator(".cf-extern-form input[type=date]").fill("2026-01-20")
    item.locator(".cf-extern-salveaza").click()
    sel = "details.cf-inainte .cf-decl-item[data-cheie='%s']" % cheie
    pg.wait_for_selector(sel + " .cf-extern-anuleaza", timeout=60000)
    pg.click(sel + " .cf-extern-anuleaza")
    pg.wait_for_selector("#caseta-atentie-activa", timeout=10000)
    txt = pg.inner_text("#caseta-atentie-activa")
    patron.captura("confirmare")
    assert "Anulezi marcarea D100 T4/2025?" in txt and "12/2025" not in txt, txt


def test_def_194_randul_marcat_spune_doar_ca_e_depus(patron, preluata_07):
    """194. Control fiscal: rândul marcat „depusă în afara iConta.eu” își păstrează textul „nu pot verifica…” / „necunoscut declarat: nu
    pot demonstra…” (D205, D100 2025); marcarea se vede doar din butoane și din „· recipisă …”.
    Pașii: firma preluată în 07/2026 -> Control fiscal -> „Înainte de preluare” -> D205 2025 și D100 T4/2025: „Marchează depusă în afara
    iConta.eu” (data 20.03.2026 / 20.01.2026) -> rândul spune „Depusă în afara iConta.eu 20.03.2026 …” și nu mai spune „nu pot
    verifica” / „nu pot demonstra” / „necunoscut”."""
    pg = patron.pg
    _control(patron, preluata_07)
    pg.click("details.cf-inainte > summary")
    for cheie, data in (("d205-2025-12", "2026-03-20"), ("d100-2025-12", "2026-01-20")):
        item = _marcheaza(pg, cheie)
        item.locator(".cf-extern-btn").click()
        item.locator(".cf-extern-form input[type=date]").fill(data)
        item.locator(".cf-extern-salveaza").click()
        pg.wait_for_selector("details.cf-inainte .cf-decl-item[data-cheie='%s'] .cf-extern-anuleaza" % cheie, timeout=60000)
        txt = pg.locator("details.cf-inainte .cf-decl-item[data-cheie='%s']" % cheie).inner_text()
        zi = "%s.%s.%s" % (data[8:10], data[5:7], data[:4])
        assert ("Depusă în afara iConta.eu %s" % zi) in txt, txt
        assert not _re.search(r"(?i)nu pot verifica|nu pot demonstra|necunoscut", txt), txt
    patron.captura("marcate")


def test_def_148_recipisa_doar_numar(patron, preluata_07):
    """148. Control fiscal: recipisa doar număr.
    Pașii contabilului: „Marchează depusă în afara iConta.eu” pe D100 T4/2025 -> formularul cere data și „nr. recipisă (opțional)” — un
    număr, fără încărcare de fișier -> salvează cu recipisa „R-148” -> rândul arată „… · recipisă R-148” și se poate anula."""
    pg = patron.pg
    _control(patron, preluata_07)
    pg.click("details.cf-inainte > summary")
    cheie = "d100-2025-12"
    item = _marcheaza(pg, cheie)
    item.locator(".cf-extern-btn").click()
    form = item.locator(".cf-extern-form")
    assert form.locator("input[type=file]").count() == 0
    assert form.locator("input[type=text]").get_attribute("placeholder") == "nr. recipisă (opțional)"
    form.locator("input[type=date]").fill("2026-07-20")
    form.locator("input[type=text]").fill("R-148")
    form.locator(".cf-extern-salveaza").click()
    pg.wait_for_selector("details.cf-inainte .cf-decl-item[data-cheie='%s'] .cf-extern-anuleaza" % cheie, timeout=60000)
    item = pg.locator("details.cf-inainte .cf-decl-item[data-cheie='%s']" % cheie)
    txt = item.inner_text()
    assert "recipisă R-148" in txt and item.locator(".cf-extern-anuleaza").count() == 1, txt
    assert sql("SELECT recipisa FROM public.declaratii_depuse WHERE tenant_id = %s AND tip = 'd100' AND an = 2025 AND luna = 12",
               (preluata_07["tenant_id"],)) == [("R-148",)]
    patron.captura("recipisa_numar")


def test_def_156_contoarele_si_eticheta_pe_fapte(patron):
    """156. Control fiscal: „restanță” la „0 restanțe”; „0 de urmărit” vs 5 în detaliu.
    Pașii contabilului: Control fiscal pe portofoliul cabinetului de test -> orice rând etichetat „restanță” are restanțe numărate
    („N restanțe”); contorul de sus „cu declarații de urmărit” = numărul firmelor cu „N de urmărit” pe rând -> deschide o firmă cu
    declarații de urmărit: grupul „De urmărit (N)” din detaliu are același N ca rândul."""
    pg = patron.pg
    patron.acasa()
    pg.click("button.cab-card:has([data-cheie='control'])")
    pg.wait_for_selector("#cf-lista .mig-frand", timeout=120000)
    randuri = pg.evaluate("() => [...document.querySelectorAll('#cf-lista .mig-frand')].map((r) => ({nume: r.querySelector('.mig-frand-nume').innerText,"
                          " sub: r.querySelector('.mig-frand-sub').innerText, et: r.querySelector('.cf-stare').innerText.trim()}))")
    for r in randuri:
        if r["et"] == "restanță":
            assert _re.search(r"\b[1-9]\d* restanț", r["sub"]), r
    pastile = pg.inner_text(".cf-sumar")
    m = _re.search(r"(\d+) cu declarații de urmărit", pastile)
    cu_urmarit = [r for r in randuri if _re.search(r"\b[1-9]\d* de urmărit", r["sub"])]
    assert m and int(m.group(1)) == len(cu_urmarit), (pastile, [r["nume"] for r in cu_urmarit])
    patron.captura("lista_contoare")
    assert cu_urmarit, "nicio firmă cu declarații de urmărit în portofoliul de test"
    r0 = cu_urmarit[0]
    n = int(_re.search(r"\b([1-9]\d*) de urmărit", r0["sub"]).group(1))
    pg.locator("#cf-lista .mig-frand", has_text=r0["nume"]).first.click()
    pg.wait_for_function("() => [...document.querySelectorAll('.cf-grup-titlu')].some((t) => t.textContent.trim().startsWith('Audit de preluare'))",
                         timeout=120000)   # titlurile grupurilor sunt cu majuscule din CSS: se citește textul, nu randarea
    pg.wait_for_function("() => [...document.querySelectorAll('.cf-grup-titlu')].some((t) => t.textContent.trim().startsWith('De urmărit ('))",
                         timeout=120000)
    titlu = pg.evaluate("() => [...document.querySelectorAll('.cf-grup-titlu')].find((t) => t.textContent.trim().startsWith('De urmărit (')).textContent.trim()")
    assert titlu == "De urmărit (%d)" % n, (titlu, r0)
    patron.captura("detaliu_de_urmarit")


# ------------------------------------------------------------------------------------------------ Mijloace fixe (162, 170, 149)

def _mf(f, cod, valoare, luni, pif, cont="2131", cont_am="2813"):
    """Mijloc fix în registru, pe scrierea din care îl adaugă aplicația (`repo_mijloace_fixe.adauga_cu_reevaluare`)."""
    from core import db, repo_mijloace_fixe
    with db.get_conn(f["schema"]) as c:
        with c.cursor() as cur:
            r = repo_mijloace_fixe.adauga_cu_reevaluare(cur, f["schema"], cod, "Utilaj de probă %s" % cod, cont, cont_am,
                                                        Decimal(valoare), Decimal(0), luni, pif, "liniara")
        c.commit()
    return r[0]


def _mijloace(ecran, f):
    _card(ecran, f, "mijloace", "table.fd-tabel")


def test_def_162_mijloace_fixe_nu_deruleaza_lateral_la_1700(patron, firma_gv):
    """162. Mijloace fixe: derulare laterală la ~1700 px, PIF tăiat, acțiuni ascunse.
    [partea rămasă, registrul: „la fereastra de 1700 px tabelul Mijloace fixe tot derulează lateral: scrollWidth 1743 > clientWidth
    1604 … antetele numerice lungi au white-space: nowrap … (conținutul «neînregistrate: N luni: …» tot nowrap)”] Pașii: ecran de
    1700 px -> firma cu un mijloc fix cu luni neînregistrate -> Mijloace fixe: tabelul încape în fereastră (nicio derulare laterală),
    cu meniul „Acțiuni” închis și deschis; antetul „Amortizat (calculat, până la …)” se rupe pe rânduri, cifrele rămân pe un rând."""
    pg = patron.pg
    pg.set_viewport_size({"width": 1700, "height": 1000})
    _mf(firma_gv, "MF162", "12000", 24, "2026-01-10")
    _mijloace(patron, firma_gv)
    pg.wait_for_selector(".fereastra:last-of-type table.fd-tabel tbody tr", timeout=30000)
    masura = ("() => { const t = [...document.querySelectorAll('.fereastra')].pop().querySelector('table.fd-tabel');"
              " let c = t.parentElement; while (c && c.scrollWidth <= c.clientWidth && c !== document.body) c = c.parentElement;"
              " const z = t.closest('.fereastra-corp'); const th = [...t.querySelectorAll('thead th')];"
              " return {lat: z.scrollWidth, vizibil: z.clientWidth, derulant: c && c !== document.body ? [c.tagName, c.className, c.scrollWidth, c.clientWidth] : null,"
              " antet: th.map(h => [h.innerText.replace(/\\s+/g, ' ').trim().slice(0, 30), Math.round(h.getBoundingClientRect().width)])}; }")
    m = pg.evaluate(masura)
    patron.captura("inchis")
    assert m["lat"] <= m["vizibil"] and m["derulant"] is None, m
    pg.locator(".fereastra:last-of-type table.fd-tabel details.dec-xml > summary").first.click()
    m2 = pg.evaluate(masura)
    patron.captura("actiuni_deschise")
    assert m2["lat"] <= m2["vizibil"] and m2["derulant"] is None, m2


def test_def_170_c_si_d_cere_poate_valida(patron, junior, firma_gv):
    """170. Mijloace fixe: C&D „Poate valida” — lipsea proba pe utilizator fără drept.
    Pașii: asistentul („Poate pregăti”, fără „Poate valida”) deschide Mijloace fixe -> în meniul „Acțiuni” nu are butonul „C&D: da/nu”,
    iar ecranul spune că acțiunea cere dreptul «Poate valida»; cererea directă îi e refuzată (403) -> contabilul-șef are butonul și
    schimbă C&D pe „da”."""
    mid = _mf(firma_gv, "MF170", "3000", 36, "2026-05-10")
    asistent = junior
    pa = asistent.pg
    _mijloace(asistent, firma_gv)
    rand = pa.locator("table.fd-tabel tbody tr", has_text="Utilaj de probă MF170").first
    rand.locator("details summary", has_text="Acțiuni").click()
    assert rand.locator("[data-caseaza]").is_visible()
    assert not rand.locator("[data-cd]").is_visible(), "asistentul fără «Poate valida» vede butonul C&D"
    assert "Poate valida" in asistent.fereastra()
    asistent.captura("asistent_fara_cd")
    r = _api(asistent, "PUT", "/tenants/%d/mijloace-fixe/%d/destinatie-cd" % (firma_gv["tenant_id"], mid), {"destinatie_cd": True})
    assert r["status"] == 403, r
    assert sql('SELECT destinatie_cd FROM "%s".mijloace_fixe WHERE id = %%s' % firma_gv["schema"], (mid,)) == [(False,)]
    pg = patron.pg
    _mijloace(patron, firma_gv)
    rand = pg.locator("table.fd-tabel tbody tr", has_text="Utilaj de probă MF170").first
    rand.locator("details summary", has_text="Acțiuni").click()
    b = rand.locator("[data-cd]")
    assert b.is_visible() and b.inner_text() == "C&D: nu"
    b.click()
    pg.wait_for_function("() => [...document.querySelectorAll('table.fd-tabel tbody tr')].some((r) => r.textContent.includes('Utilaj de probă MF170')"
                         " && r.querySelector('[data-cd]') && r.querySelector('[data-cd]').textContent === 'C&D: da')", timeout=30000)
    assert sql('SELECT destinatie_cd FROM "%s".mijloace_fixe WHERE id = %%s' % firma_gv["schema"], (mid,)) == [(True,)]
    rand = pg.locator("table.fd-tabel tbody tr", has_text="Utilaj de probă MF170").first
    rand.locator("details summary", has_text="Acțiuni").click()
    patron.captura("patron_cd_da")


def _note_amortizare(f, an, luna):
    return sql('SELECT id, status FROM "%s".inregistrari WHERE numar = %%s ORDER BY id' % f["schema"], ("AMORT-%d-%02d" % (an, luna),))


def test_def_214_nota_de_amortizare_ultima_zi_si_documentul_ei(patron, firma):
    """214. Nota de amortizare: datată 28.09 în loc de ultima zi a lunii; „Document justificativ: nederivat”.
    Pașii: firma cu un mijloc fix (PIF 10.05.2026) -> Registrul jurnal, 07/2026 -> „Generează amortizarea”: nota e datată 31.07.2026, iar
    rândul ei arată documentul justificativ (tabloul de amortizare), nu „nederivat” -> o notă de amortizare scrisă de codul vechi
    (06/2026, ziua 28, fără document) arată și ea „Tabloul de amortizare AMORT-2026-06” (derivat la citire, ca registrul)."""
    f = firma
    pg = patron.pg
    _mf(f, "MF214", "6000", 60, "2026-05-10")
    veche = sql('INSERT INTO "%s".inregistrari (data, numar, descriere, sursa, status) VALUES (\'2026-06-28\', \'AMORT-2026-06\', '
                "'Amortizare 06/2026', 'amortizare', 'ciorna') RETURNING id" % f["schema"])[0][0]
    sql('INSERT INTO "%s".inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%%s, \'6811\', \'2813\', 100)'
        % f["schema"], (veche,))
    try:
        _card(patron, f, "jurnal", "#j-amort")
        _la_luna(patron, "#j-prev", 2026, 7)
        pg.click("#j-amort")
        for _ in range(60):
            if _note_amortizare(f, 2026, 7):
                break
            pg.wait_for_timeout(500)
        n = _note_amortizare(f, 2026, 7)
        assert len(n) == 1, n
        assert str(sql('SELECT data FROM "%s".inregistrari WHERE id = %%s' % f["schema"], (n[0][0],))[0][0]) == "2026-07-31"
        pg.wait_for_selector("[data-nota-id='%d']" % n[0][0], timeout=30000)
        rand = pg.inner_text("[data-nota-id='%d']" % n[0][0])
        patron.captura("amortizare_07")
        assert "31.07.2026" in rand and "nederivat" not in rand and "Document justificativ:" in rand, rand
        pg.click("#j-prev")   # o lună înapoi, din 07/2026
        _asteapta_text(patron, "Luna 06/2026")
        pg.wait_for_selector("[data-nota-id='%d']" % veche, timeout=30000)
        rand_v = pg.inner_text("[data-nota-id='%d']" % veche)
        patron.captura("amortizare_veche")
        assert "Document justificativ: Tabloul de amortizare AMORT-2026-06" in rand_v, rand_v
    finally:
        sql('DELETE FROM "%s".inregistrari WHERE id = %%s' % f["schema"], (veche,))


def test_def_215_inchiderea_semnaleaza_amortizarea_lunilor_anterioare(patron, firma_gv):
    """215. Închidere lună: lunile anterioare cu amortizare neînregistrată nu apar ca semnal.
    Pașii: firma cu mijlocul fix MF215 (PIF 10.03.2026, 3.000 lei, 30 de luni -> 100 lei/lună din 04/2026), fără nicio notă de
    amortizare -> Închidere lună -> luna trecută: sub „Semnale” apare „amortizarea lunilor anterioare nu e înregistrată pe contul
    2813: … luni (04–…/2026)”, cu suma după calcul; nu e printre ce oprește închiderea (acolo e numai luna însăși)."""
    f = firma_gv
    pg = patron.pg
    mid = _mf(f, "MF215", "3000", 30, "2026-03-10")
    trecuta = AZI.replace(day=1) - _dt.timedelta(days=1)
    try:
        _card(patron, f, "inchidere", "#il-prev")
        _la_luna(patron, "#il-prev", trecuta.year, trecuta.month)
        pg.wait_for_function("() => { const z = [...document.querySelectorAll('.fereastra')].pop().querySelector('#il-controale');"
                             " return z && z.querySelector('.caseta-info, .caseta-atentie'); }", timeout=90000)
        zona = pg.inner_text(".fereastra:last-of-type #il-controale")
        patron.captura("inchidere")
    finally:
        sql('DELETE FROM "%s".mijloace_fixe WHERE id = %%s' % f["schema"], (mid,))
    semnale = zona.split("Semnale (", 1)[1] if "Semnale (" in zona else ""
    assert "amortizarea lunilor anterioare nu e înregistrată pe contul 2813" in semnale, zona
    # intervalul: începe cel târziu în aprilie (MF215 intră în funcțiune în martie; firma poate avea și active mai vechi, ale altor
    # probe) și se termină în luna dinaintea celei închise
    m = _re.search(r"amortizarea lunilor anterioare[^:]*: \d+ luni \((\d{2})–(\d{2})/(\d{4})\)", semnale)
    assert m and int(m.group(1)) <= 4 and (int(m.group(3)), int(m.group(2))) == ((trecuta.replace(day=1) - _dt.timedelta(days=1)).year,
                                                                                (trecuta.replace(day=1) - _dt.timedelta(days=1)).month), zona
    assert "amortizarea lunilor anterioare" not in zona.split("Semnale (", 1)[0], zona


def test_def_149_amortizarea_ciorna_se_inlocuieste_validata_nu(patron, firma_gv):
    """149. Amortizare/gestiune: ciorna nevalidată se înlocuiește; validatul nu se atinge.
    Partea AMORTIZĂRII (global-valoric, 08/2026): Registrul jurnal, „Generează amortizarea”: o ciornă -> se adaugă un mijloc fix uitat
    și se generează din nou: tot o singură notă, cu suma nouă -> nota se validează -> încă un mijloc fix și încă o generare: refuz, nota
    validată rămâne cum era. (Partea descărcării GV nu e probată aici — motivul e în raportul blocului E.)"""
    f = firma_gv
    pg = patron.pg
    _mf(f, "MF149A", "6000", 60, "2026-05-10")
    _card(patron, f, "jurnal", "#j-amort")
    _la_luna(patron, "#j-prev", 2026, 8)
    def genereaza(n_asteptat_linii=None):
        inainte = _note_amortizare(f, 2026, 8)
        ids0 = [x[0] for x in inainte]
        tot0 = (sql('SELECT sum(suma) FROM "%s".inregistrari_linii WHERE inregistrare_id = %%s' % f["schema"], (ids0[0],))[0][0]
                if ids0 else None)
        pg.click("#j-amort")
        for _ in range(60):   # mesajul „Notă generată” îl șterge redesenarea; se așteaptă nota nouă / suma nouă
            dupa = _note_amortizare(f, 2026, 8)
            if dupa and (not ids0 or [x[0] for x in dupa] != ids0 or sql('SELECT sum(suma) FROM "%s".inregistrari_linii '
                                                                       'WHERE inregistrare_id = %%s' % f["schema"], (dupa[0][0],))[0][0] != tot0):
                break
            pg.wait_for_timeout(500)
        pg.wait_for_function("() => (document.querySelector('#j-lock') || {}).textContent", timeout=30000)
        pg.wait_for_timeout(500)
    genereaza()
    n1 = _note_amortizare(f, 2026, 8)
    assert len(n1) == 1 and n1[0][1] == "ciorna", n1
    assert patron.pg.locator("[data-nota-id='%d']" % n1[0][0]).count() == 1
    total1 = sql('SELECT sum(suma) FROM "%s".inregistrari_linii WHERE inregistrare_id = %%s' % f["schema"], (n1[0][0],))[0][0]
    _mf(f, "MF149B", "1200", 12, "2026-05-20")
    genereaza()
    n2 = _note_amortizare(f, 2026, 8)
    assert len(n2) == 1 and n2[0][1] == "ciorna", n2
    total2 = sql('SELECT sum(suma) FROM "%s".inregistrari_linii WHERE inregistrare_id = %%s' % f["schema"], (n2[0][0],))[0][0]
    assert total2 == total1 + Decimal("100.00"), (total1, total2)      # MF149B: 1.200 lei / 12 luni
    patron.captura("amortizare_ciorna_inlocuita")
    _ok(_api(patron, "POST", "/tenants/%d/jurnal/%d/valideaza" % (f["tenant_id"], n2[0][0]), {}))
    _mf(f, "MF149C", "2400", 24, "2026-05-25")
    pg.click("#j-amort")
    _asteapta_text(patron, "deja generată și validată")
    n3 = _note_amortizare(f, 2026, 8)
    assert n3 == [(n2[0][0], "validata")], n3
    assert sql('SELECT sum(suma) FROM "%s".inregistrari_linii WHERE inregistrare_id = %%s' % f["schema"], (n2[0][0],))[0][0] == total2
    patron.captura("amortizare_validata_neatinsa")


# ------------------------------------------------------------------------------------------------ Bilanț (151)

def _vanzare_validata(f, data, pret):
    """O vânzare de marfă: factura emisă cu venitul pe 707 (`facturi_api.emite_factura`, nota ei automată, sursa „facturi”), nota
    validată — descărcarea citește numai notele validate."""
    from core import db, facturi_api
    with db.get_conn(f["schema"]) as c:   # seria de facturare a firmei (Date firmă), ca la orice emitere
        if not facturi_api.serie_facturi(c):
            assert facturi_api.seteaza_numerotare(c, serie="GV149", numar_start=1)["ok"]
            c.commit()
    with db.get_conn(f["schema"]) as c:
        r = facturi_api.emite_factura(c, [{"descriere": "Marfa vanduta", "cantitate": 1, "pret_unitar": pret, "cota_tva": 21,
                                            "cont_venit": "707"}], tert_nume="Client 149 SRL", tert_cui=cui_cu_control(36000149),
                                      data_emitere=data, status="emisa")
        assert r.get("ok"), r
        c.commit()
    note = [x[0] for x in sql('SELECT id FROM "%s".inregistrari WHERE factura_id = %%s' % f["schema"], (r["factura_id"],))]
    assert note, "factura emisă n-are notă"
    _valideaza_note(f, note)


def _note_descarcare(f, an, luna):
    return sql('SELECT id, status FROM "%s".inregistrari WHERE numar = %%s ORDER BY id' % f["schema"], ("DESC-GV-%d-%02d" % (an, luna),))


def test_def_149_descarcarea_gv_ciorna_se_inlocuieste_validata_nu(patron, firma_gv):
    """149. Amortizare/gestiune: ciorna nevalidată se înlocuiește; validatul nu se atinge.
    [partea rămasă, registrul: „jumătatea DESCĂRCĂRII GV nu se poate proba azi … triggerul regula_nota refuză validarea notei de
    contare a unei facturi”; regula primește acum nota legată de factură] Pașii (global-valoric, 06/2026): NIR validat (10 × 50, preț
    de raft 80) și o vânzare validată (100 lei pe 707) -> Stocuri, 06/2026, „Descarcă gestiunea lunii”: ciorne -> încă o vânzare
    validată și din nou: ciornele de dinainte s-au înlocuit (alte note, aceeași cheie, niciuna rămasă în plus) -> notele se validează
    -> încă o vânzare și din nou: refuz „deja descărcată și validată”, notele validate rămân aceleași."""
    f = firma_gv
    _nir(f, "E149D", "2026-06-03", "Furnizor 149 SRL", cui_cu_control(36000150), 10, 50, pret_vanzare=80)
    _vanzare_validata(f, "2026-06-10", 100)
    pg = patron.pg
    _card(patron, f, "stocuri", "#s-desc")
    _la_luna(patron, "#s-prev", 2026, 6)

    def descarca():
        pg.click("#s-desc")
        pg.click("#ca-ok")
        pg.wait_for_function("() => (document.querySelector('#s-mesaj') || {innerText: ''}).innerText.trim() !== ''", timeout=60000)
        return pg.inner_text("#s-mesaj")
    m1 = descarca()
    n1 = _note_descarcare(f, 2026, 6)
    assert n1 and {s for _i, s in n1} == {"ciorna"}, (m1, n1)
    _vanzare_validata(f, "2026-06-12", 60)
    _card(patron, f, "stocuri", "#s-desc")
    _la_luna(patron, "#s-prev", 2026, 6)
    m2 = descarca()
    n2 = _note_descarcare(f, 2026, 6)
    patron.captura("inlocuita")
    assert len(n2) == len(n1) and {i for i, _s in n2}.isdisjoint({i for i, _s in n1}), (m2, n1, n2)
    _valideaza_note(f, [i for i, _s in n2])
    _vanzare_validata(f, "2026-06-15", 40)
    _card(patron, f, "stocuri", "#s-desc")
    _la_luna(patron, "#s-prev", 2026, 6)
    m3 = descarca()
    patron.captura("validata_refuz")
    assert "deja descărcată și validată" in m3, m3
    assert _note_descarcare(f, 2026, 6) == [(i, "validata") for i, _s in n2]


def _bilant(ecran, f, an, tip):
    """Bilanț -> anul și tipul, după ce ecranul a terminat de încărcat categoria de mărime a anului ales (ca omul care vede ecranul).
    Primul clic pe un buton după asta nu are voie să se piardă: părăsirea câmpului „An” reîncărca o categorie deja încărcată, iar
    fereastra (centrată) se micșora sub cursor — „Descarcă XML” / „Validează” fără nicio cerere (prins de plasă, 151/188)."""
    pg = ecran.pg
    _card(ecran, f, "bilant", "#bl-an")
    pg.fill("#bl-an", str(an))
    pg.dispatch_event("#bl-an", "change")
    pg.wait_for_function("() => { const z = document.querySelector('#bl-categorie'); return z && !z.hasAttribute('aria-busy') && "
                         "z.innerText.trim() !== '' && !z.innerText.includes('Se calculează'); }", timeout=90000)
    pg.select_option("#bl-tip", tip)


def test_def_151_bilant_4428_numai_la_stocuri(patron, firma_gv):
    """151. Bilanț: 4428 (preț de raft) apărea și la datorii; analitic propriu, doar la stocuri rd.05.
    Pașii contabilului (global-valoric): NIR fără factură din 11/2024, 10 buc × 55 lei, preț de raft 80 lei, validat (371 = 800,00;
    378 = 111,16; 4428.02 = 138,84; 408 = 665,50) -> Bilanț anual 2024, S1005, „Descarcă XML” -> rd.05 stocuri = 550 (371 − 378 −
    4428.02), rd.13 datorii = 666 (numai 408): TVA-ul din prețul de raft nu mai apare la datorii."""
    cui = cui_cu_control(37000151)
    _nir(firma_gv, "E151", "2024-11-12", "Furnizor 151 SRL", cui, 10, 55, pret_vanzare=80)
    pg = patron.pg
    _bilant(patron, firma_gv, 2024, "s1005")
    with pg.expect_response(lambda r: "/s1005-xml" in r.url, timeout=90000) as rsp:
        with pg.expect_download(timeout=90000):
            pg.click("#bl-xml")
    xml = rsp.value.json()["xml"]
    a = dict(_re.findall(r'\b(F10_\d{4})="([^"]*)"', xml))
    assert a.get("F10_0052") == "550", a
    assert a.get("F10_0132") == "666", a
    patron.captura("bilant_2024_xml")


def test_def_188_randurile_bilantului_pe_ecran_cu_cifrele_care_se_depun(patron, firma_gv):
    """188. Bilanț: rândurile bilanțului (F10_0052, F10_0132 și restul) apar pe ecranul Bilanț, cu cifrele care se depun, nu doar
    verdictul. Pașii: firma global-valorică cu un NIR validat în 11/2024 -> Bilanț, 2024, S1005 -> „Validează”: sub verdict, tabelul
    „Ce se depune” are rândul 5 (stocuri) și rândul 13 (datorii), iar FIECARE rând de pe ecran poartă exact cifrele din XML-ul care se
    descarcă (an precedent / an curent), fără rânduri în plus sau în minus."""
    cui = cui_cu_control(37000188)
    _nir(firma_gv, "E188", "2024-11-14", "Furnizor 188 SRL", cui, 4, 50, pret_vanzare=70)
    pg = patron.pg
    _bilant(patron, firma_gv, 2024, "s1005")
    pg.click("#bl-val")
    pg.wait_for_selector("#bl-randuri tbody tr", timeout=120000)
    ecran = pg.evaluate("""() => [...document.querySelectorAll('#bl-randuri tbody tr')].map(tr =>
      [...tr.querySelectorAll('td')].map(td => td.innerText.trim()))""")
    patron.captura("bilant_randuri")
    with pg.expect_response(lambda r: "/s1005-xml" in r.url, timeout=90000) as rsp:
        with pg.expect_download(timeout=90000):
            pg.click("#bl-xml")
    xml = rsp.value.json()["xml"]
    din_xml = {}
    for f, r, col, v in _re.findall(r'\b(F\d\d)_(\d{3})([12])="(-?\d+)"', xml):
        din_xml.setdefault((f, int(r)), ["0", "0"])[int(col) - 1] = v
    bani = lambda t: str(int(round(float(t.replace(".", "").replace(",", ".").replace("\u2212", "-") or 0))))
    pe_ecran = {(f, int(r.split()[-1])): (bani(p), bani(c)) for f, r, p, c in ecran}
    din_xml = {k: tuple(v) for k, v in din_xml.items()}
    assert ("F10", 5) in pe_ecran and ("F10", 13) in pe_ecran, ecran
    assert pe_ecran == din_xml, sorted(set(pe_ecran.items()) ^ set(din_xml.items()))
