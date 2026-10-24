# -*- coding: utf-8 -*-
"""Lotul 12, comanda Costin 12.1 (verbatim în DECIZII „Comanda 12.1”), pachetul „start”: cabinetul NOU, creat de la zero, pe drumul
omului — „Înregistrează cabinetul tău” (înregistrarea liberă, cu verificarea anti-roboți și linkul de confirmare din email), intrarea în
cont, „Înainte de a începe”, pagina principală cu „Primii pași” — și clientul din portal, la prima intrare.

  * 321 (grav) — rotița derulează pagina principală sub cardurile „Primii pași”, la 1366×768, 1280×720, 1920×1080 și pe telefon
    (comanda 12.1 pct.3: „321 și 322: dovada pe un cabinet nou, creat de la zero”);
  * 322 — „Lucrez singur” pe pasul făcut nu se mai arată;
  * 561 — clientul din portal: „Salvează numărul” salvează numărul (în bază), apoi intră în portal;
  * 596 — „Înainte de a începe” încape pe ecran, „Continuă” se vede mereu, refuzul numărului stă lângă buton și lângă câmp, cu mărimea
    mesajelor de eroare (DS cap.6 v2.93 / v2.99); cardul 1 din „Primii pași” încape (pașii pliați în „Cum se face”, DS cap.6 v2.95);
  * 269 / 490 — salutul numește omul cu numele scris la înregistrare, întreg („Salut, Test 253”, „Salut, Contabil B”);
  * 320 / comanda 12.1 pct.6 — „Primii pași” pas cu pas, fiecare pas făcut în ecranul lui: cardul lui devine verde (marginea `--verde`,
    bifa), celelalte nu; toate făcute -> cardurile dispar; „?” le arată pe toate, verzi.

DATE DE PORNIRE fără ecran (declarate): comutatorul înregistrării pe „liberă” (setarea superadminului, `mod_inregistrare`, refăcută la
final); conectarea SPV a pasului 2 — conectarea reală cere certificatul digital și ANAF (`/anaf/oauth/callback`), deci tokenul SPV al
cabinetului se scrie în bază ([EXTERN]), ca în `e2e_lot72_cont.py::test_def_319_*`; răspunsul ANAF la CUI-ul firmei e al simulatorului
plasei (`ICONTA_ANAF_SIMULAT`). CUI-ul firmei are cifra de control verificată (`conftest.cui_cu_control`). Cabinetele, conturile, firmele și
clientul de probă se scot la final. Temei: N/A — reguli de produs (CLAUDE.md §9)."""
import contextlib
import re
import secrets
import time

import pytest

from conftest import BAZA, GARDA_DESCHIDERI, LAT, INALT, Ecran, _scoate_firmele_e2e, cui_cu_control, firma_noua, sql
from curatenie import PREFIX_FIRMA
from e2e_invitatii import _client_nou, mod_inregistrare
from e2e_inregistrare_libera import _asteapta_turnstile, _scrisori

PAROLA = secrets.token_urlsafe(12) + "!Aa1"   # generată la rulare (garda secretelor din git)
TELEFON = "0700 000 412"                     # sintetic: prefixul 07 și cifre de umplutură, nu al cuiva
TELEFON_SALVAT = "+40700000412"
REZOLUTII = ((1366, 768), (1280, 720), (1920, 1080), (393, 851))   # laptop, laptop mic, birou, telefon (comanda 12.1 pct.3 / brief)
_CARD = "#inceput-carduri .inceput-card[data-card='%s']"


# ── cabinetul nou, creat de la zero ─────────────────────────────────────────────────────────────────────────────────────────────
def _scoate_cabinetul(email, cabinet):
    def tabele(col):
        return [r[0] for r in sql("SELECT c.table_name FROM information_schema.columns c JOIN information_schema.tables t "
                                  "ON t.table_schema = c.table_schema AND t.table_name = c.table_name AND t.table_type = 'BASE TABLE' "
                                  "WHERE c.table_schema = 'public' AND c.column_name = %s AND c.table_name NOT IN ('users', "
                                  "'accounting_firms', 'tenants')", (col,))]
    fids = [r[0] for r in sql("SELECT id FROM public.accounting_firms WHERE nume = %s", (cabinet,))]
    for fid in fids:
        for (tid,) in sql("SELECT id FROM public.tenants WHERE accounting_firm_id = %s", (fid,)):
            _scoate_firmele_e2e(tid)
    uids = [r[0] for r in sql("SELECT id FROM public.users WHERE email = %s OR accounting_firm_id = ANY(%s)", (email, fids or [0]))]
    sql("DELETE FROM public.inregistrari_in_asteptare WHERE email = %s", (email,))
    sql("DELETE FROM public.acord_termeni WHERE email = %s", (email,))
    if uids:
        for t in tabele("user_id"):
            sql('DELETE FROM public."%s" WHERE user_id = ANY(%%s)' % t, (uids,))
        sql("DELETE FROM public.users WHERE id = ANY(%s)", (uids,))
    if fids:
        for t in tabele("accounting_firm_id"):
            sql('DELETE FROM public."%s" WHERE accounting_firm_id = ANY(%%s)' % t, (fids,))
        sql("DELETE FROM public.accounting_firms WHERE id = ANY(%s)", (fids,))


class Cabinet:
    """Cabinetul nou, cu pagina administratorului lui (Ecran) — după „Înregistrează cabinetul tău”, confirmare și intrarea în cont."""

    def __init__(self, ctx, e, email, cabinet):
        self.ctx, self.e, self.pg, self.email, self.cabinet = ctx, e, e.pg, email, cabinet

    @property
    def firm_id(self):
        return sql("SELECT id FROM public.accounting_firms WHERE nume = %s", (self.cabinet,))[0][0]


@pytest.fixture()
def cabinet_de_la_zero(browser, request):
    """Fabrica: `cabinet_de_la_zero(nume_admin)` -> `Cabinet` oprit la „Înainte de a începe”. Pașii vizitatorului: pagina publică ->
    „Acces” -> „Client nou” -> „Înregistrează cabinetul tău”: denumirea, numele, emailul, parola de două ori, termenii, verificarea
    anti-roboți -> „Creează cont” -> linkul din email -> „Intră în cont” -> parola -> „Înainte de a începe”. Totul se scoate la final."""
    era = mod_inregistrare("libera")
    facute = []

    def fa(nume_admin="Ionescu Maria", latime=LAT, inaltime=INALT):
        semn = "%d%02d" % (int(time.time() * 1000) % 100000000, len(facute))
        email = "e2e.l12start.%s@exemplu.ro" % semn
        cabinet = "E2E Cabinet Nou L12 %s" % semn
        sql("DELETE FROM public.cereri_ritm WHERE cheie IN ('inregistrare_ip', 'inregistrare_email', 'confirmare_ip')")  # o rulare = mai multe
        ctx = browser.new_context(viewport={"width": latime, "height": inaltime})
        ctx.add_init_script(GARDA_DESCHIDERI)
        e = Ecran(ctx.new_page(), request.node.name)
        facute.append((ctx, e, email, cabinet))
        vp = e.pg
        _client_nou(vp, BAZA + "/")
        vp.wait_for_selector("#reg-email", timeout=10000)
        vp.fill("#reg-cabinet", cabinet)
        vp.fill("#reg-nume-admin", nume_admin)
        vp.fill("#reg-email", email)
        vp.fill("#reg-parola", PAROLA)
        vp.fill("#reg-parola2", PAROLA)
        vp.check("#reg-termeni")
        _asteapta_turnstile(vp)
        vp.click("#reg-buton")
        vp.wait_for_selector("#reg-verifica", timeout=20000)
        (scrisoare,) = _scrisori(email)
        tok = re.search(r"#confirmare=([\w-]+)", scrisoare["html"]).group(1)
        vp.goto("about:blank")
        vp.goto(BAZA + "/#confirmare=" + tok, wait_until="domcontentloaded")
        vp.wait_for_selector("#conf-rezultat.caseta-info", timeout=20000)
        vp.click("#conf-intra")
        vp.fill("#login-parola", PAROLA)
        vp.click("#login-buton")
        vp.wait_for_selector("#prima-intrare #not-tipuri .not-grup", timeout=30000)
        return Cabinet(ctx, e, email, cabinet)

    try:
        yield fa
    finally:
        for ctx, e, email, cabinet in facute:
            erori, rele, singure = list(e.erori), list(e.cereri_rele), list(e.deschideri_singure)
            with contextlib.suppress(Exception):
                ctx.close()
            _scoate_cabinetul(email, cabinet)
            assert not erori, "erori JavaScript pe ecran: %s" % erori[:3]
            assert not rele, "cereri cu răspuns 5xx: %s" % rele[:3]
            assert not singure, "[325] s-a deschis ceva fără clicul omului: %s" % singure[:5]
        mod_inregistrare(era or "invitatie")


# ── „Înainte de a începe” ──────────────────────────────────────────────────────────────────────────────────────────────────────
def _in_ecran(pg, sel):
    """Elementul e întreg în ecran (fereastra browserului)."""
    return pg.evaluate("(s) => { const r = document.querySelector(s).getBoundingClientRect(); return r.top >= 0 && r.left >= 0 && "
                       "r.bottom <= innerHeight && r.right <= innerWidth && r.height > 0; }", sel)


def _roteste(pg, sel, pas, de=15):
    """Rotița mouse-ului deasupra elementului `sel`, de `de` ori (pas pozitiv = în jos)."""
    bb = pg.locator(sel).bounding_box()
    pg.mouse.move(bb["x"] + bb["width"] / 2, bb["y"] + min(bb["height"] / 2, 200))
    for _ in range(de):
        pg.mouse.wheel(0, pas)
        pg.wait_for_timeout(80)
    pg.wait_for_timeout(300)


def _salveaza_numarul(pg, numar):
    pg.fill("#not-telefon", numar)
    pg.click("#not-salveaza-telefon")


def treci_prima_intrare(pg):
    """„Înainte de a începe”: numărul -> „Salvează numărul” -> „Salvează” (alegerile din oficiu) -> „Continuă în aplicație”; apoi
    prezentarea de bun venit (prima logare) se închide din X."""
    _salveaza_numarul(pg, TELEFON)
    pg.wait_for_function("(t) => document.querySelector('#not-stare-telefon').innerText.includes(t)", arg=TELEFON_SALVAT, timeout=15000)
    pg.click("#not-salveaza-canal")
    pg.wait_for_function("() => !document.querySelector('#pi-continua').disabled", timeout=15000)
    pg.click("#pi-continua")
    pg.wait_for_selector(".cab-grila", timeout=30000)
    with contextlib.suppress(Exception):
        pg.wait_for_selector(".bun-venit-overlay .dialog-x", timeout=8000)
        pg.click(".bun-venit-overlay .dialog-x")
        pg.wait_for_selector(".bun-venit-overlay", state="detached", timeout=8000)


def test_def_596_inainte_de_a_incepe_incape_pe_ecran_iar_refuzul_numarului_sta_langa_buton(cabinet_de_la_zero):
    """596. „Aceeași pagină, la cabinet nou: iese din ecran; motivul lui «NU s-a salvat» e scris mărunt, sub ecran; cardurile «Primii pași»
    au prea mult text (cardul 1 e tăiat).”
    Pașii administratorului cabinetului NOU, pe un laptop (1366×768): „Înainte de a începe” e o fereastră întreagă în ecran, cu
    „Continuă în aplicație” și rândul „ce mai lipsește” jos, în ecran, cât se derulează lista; numărul „722” -> „Salvează numărul” ->
    refuzul („Numărul nu e un număr de telefon …”) lângă câmp și în caseta „NU s-a salvat.” chiar sub buton, în ecran, cu mărimea
    mesajelor de eroare (DS cap.6 v2.93: „lângă butonul apăsat”; v2.99: „în casetă și lângă câmp”) -> numărul bun -> „Numărul … a fost
    salvat”, în bază +40700000412; rândul de jos spune pasul care a rămas -> „Salvează” -> „Continuă” -> pagina principală: cardul 1 din
    „Primii pași” încape între antet și marginea de jos, cu pașii pliați în „Cum se face”. Pe telefon (393×851): „Continuă” în ecran."""
    from core import uc_cont_notificari as U
    cab = cabinet_de_la_zero(latime=1366, inaltime=768)
    pg, e = cab.pg, cab.e
    assert _in_ecran(pg, "#prima-intrare"), "fereastra iese din ecran"
    assert _in_ecran(pg, "#pi-continua") and _in_ecran(pg, "#pi-motiv")
    assert "„Salvează numărul”" in pg.inner_text("#pi-motiv")
    corp = "#prima-intrare .fereastra-corp"
    assert pg.evaluate("(s) => { const c = document.querySelector(s); return c.scrollHeight > c.clientHeight; }", corp), \
        "cazul nu se reproduce: lista încape fără derulare la 1366×768"
    _roteste(pg, corp, 300)                                                # rotița pe listă, până jos
    assert pg.evaluate("(s) => document.querySelector(s).scrollTop", corp) > 0, "rotița nu derulează lista"
    assert _in_ecran(pg, "#pi-continua") and _in_ecran(pg, "#not-salveaza-canal"), "jos: „Continuă” sau „Salvează” în afara ecranului"
    e.captura("jos")
    _roteste(pg, corp, -300)                                               # înapoi sus, la telefon
    _salveaza_numarul(pg, "722")
    pg.wait_for_selector('.msg-eroare[data-camp="not-telefon"]', timeout=15000)
    pg.wait_for_selector(".refuz-salvare", timeout=15000)
    pg.wait_for_timeout(500)                                               # derularea adusă de mesaj (aduInVedere) s-a oprit
    e.captura("refuz")
    assert pg.inner_text('.msg-eroare[data-camp="not-telefon"]') == U.MESAJ_TELEFON_INVALID
    assert _in_ecran(pg, '.msg-eroare[data-camp="not-telefon"]') and _in_ecran(pg, ".refuz-salvare"), "refuzul nu e în ecran"
    caseta = " ".join(pg.inner_text(".refuz-salvare").split())
    assert caseta.startswith("NU s-a salvat.") and U.MESAJ_TELEFON_INVALID in caseta, caseta
    dist = pg.evaluate("() => document.querySelector('.refuz-salvare').getBoundingClientRect().top - "
                       "document.querySelector('#not-salveaza-telefon').getBoundingClientRect().bottom")
    assert 0 <= dist <= 40, "caseta „NU s-a salvat.” nu stă chiar sub „Salvează numărul” (la %s px)" % dist
    marimi = pg.evaluate("() => [getComputedStyle(document.querySelector('.refuz-salvare')).fontSize, "
                         "getComputedStyle(document.querySelector('.msg-eroare[data-camp=\"not-telefon\"]')).fontSize]")
    assert marimi[0] == marimi[1], marimi                                  # mărimea mesajelor de eroare (DS cap.6, `--text-mic`)
    assert sql("SELECT telefon FROM public.users WHERE email = %s", (cab.email,)) == [(None,)]
    _salveaza_numarul(pg, TELEFON)
    pg.wait_for_function("(t) => document.querySelector('#not-stare-telefon').innerText.includes(t)", arg=TELEFON_SALVAT, timeout=15000)
    pg.wait_for_function("() => document.body.innerText.includes('a fost salvat')", timeout=15000)
    assert pg.locator(".refuz-salvare").count() == 0, "refuzul vechi a rămas după salvare"
    assert sql("SELECT telefon FROM public.users WHERE email = %s", (cab.email,)) == [(TELEFON_SALVAT,)]
    pg.wait_for_function("(t) => document.querySelector('#pi-motiv').innerText.includes(t)", arg="Mai rămâne un pas", timeout=15000)
    e.captura("numar_salvat")
    pg.set_viewport_size({"width": 393, "height": 851})
    pg.wait_for_timeout(300)
    assert _in_ecran(pg, "#pi-continua"), "pe telefon „Continuă” iese din ecran"
    e.captura("telefon")
    pg.set_viewport_size({"width": 1366, "height": 768})
    pg.click("#not-salveaza-canal")
    pg.wait_for_function("() => !document.querySelector('#pi-continua').disabled", timeout=15000)
    pg.click("#pi-continua")
    pg.wait_for_selector(".cab-grila", timeout=30000)
    with contextlib.suppress(Exception):
        pg.wait_for_selector(".bun-venit-overlay .dialog-x", timeout=8000)
        pg.click(".bun-venit-overlay .dialog-x")
    pg.wait_for_selector(_CARD % "preluare", timeout=30000)
    assert pg.locator(_CARD % "preluare" + " details.dec-xml[open]").count() == 0, "„Cum se face” vine deschis"
    loc = pg.evaluate("(s) => { const c = document.querySelector(s).getBoundingClientRect(); "
                      "const a = document.querySelector('.bara-antet').getBoundingClientRect(); return [c.height, innerHeight - a.height]; }",
                      _CARD % "preluare")
    assert loc[0] <= loc[1], "cardul 1 e mai înalt decât ecranul de sub antet (%s px > %s px): e tăiat" % tuple(loc)
    e.captura("primii_pasi")


# ── 561 — clientul din portal ──────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture(scope="module")
def firma_561():
    for f in firma_noua():
        yield f


def _scoate_contul(email):
    uids = [r[0] for r in sql("SELECT id FROM public.users WHERE email = %s", (email,))]
    if not uids:
        return
    for (tabel,) in sql("SELECT c.table_name FROM information_schema.columns c JOIN information_schema.tables t ON t.table_schema = "
                        "c.table_schema AND t.table_name = c.table_name AND t.table_type = 'BASE TABLE' WHERE c.table_schema = "
                        "'public' AND c.column_name = 'user_id' AND c.table_name <> 'users'"):
        sql('DELETE FROM public."%s" WHERE user_id = ANY(%%s)' % tabel, (uids,))
    sql("DELETE FROM public.users WHERE id = ANY(%s)", (uids,))


def test_def_561_clientul_salveaza_numarul_si_intra_in_portal(patron, firma_561, browser, request):
    """561. „Portal client, «Înainte de a începe»: «Salvează numărul» nu salvează niciun număr, deci clientul nu poate intra în portal;
    pagina nu derulează.”
    Pașii: contabilul-șef -> firma -> „Acces client” -> „Invită client nou” -> emailul și numele -> „Trimite invitația” -> clientul
    deschide linkul din email, pe laptop (1366×768) -> „Înainte de a începe”: fereastra în ecran, lista derulează, „Continuă” jos, în
    ecran -> numărul -> „Salvează numărul”: „Numărul … a fost salvat”, iar în bază +40700000412 -> „Salvează” -> „Continuă în aplicație” ->
    portalul firmei („Portal Client”). În bază: telefonul, alegerile salvate, prima intrare făcută."""
    email = "e2e.l12.561.%d@exemplu.ro" % (int(time.time() * 1000) % 100000000)
    _scoate_contul(email)
    pg = patron.pg
    try:
        patron.firma(firma_561["nume"])
        pg.click("#fa-acces")
        pg.wait_for_selector(".fereastra:last-of-type #ac-btn-invita", timeout=20000)
        pg.click(".fereastra:last-of-type #ac-btn-invita")
        pg.wait_for_selector("#ac-email", timeout=10000)
        pg.fill("#ac-email", email)
        pg.fill("#ac-nume", "Client Probă 561")
        pg.click("#ac-btn")
        pg.wait_for_function("(m) => document.body.innerText.includes(m)", arg=email, timeout=20000)
        patron.captura("invitatie")
        (m,) = [x for x in _scrisori(email) if "portal" in x["subiect"].lower()][-1:]
        tok = re.search(r"#magic=([\w-]+)", m["html"]).group(1)
        ctx = browser.new_context(viewport={"width": 1366, "height": 768})
        ctx.add_init_script(GARDA_DESCHIDERI)
        c = Ecran(ctx.new_page(), request.node.name + "_client")
        try:
            cp = c.pg
            cp.goto(BAZA + "/#magic=" + tok, wait_until="domcontentloaded")
            cp.wait_for_selector("#prima-intrare #not-tipuri .not-grup", timeout=30000)
            assert _in_ecran(cp, "#prima-intrare") and _in_ecran(cp, "#pi-continua"), "fereastra sau „Continuă” iese din ecran"
            c.captura("prima_intrare")
            _salveaza_numarul(cp, TELEFON)
            cp.wait_for_function("() => document.body.innerText.includes('a fost salvat')", timeout=15000)
            cp.wait_for_function("(t) => document.querySelector('#not-stare-telefon').innerText.includes(t)", arg=TELEFON_SALVAT,
                                 timeout=15000)
            assert sql("SELECT telefon FROM public.users WHERE email = %s", (email,)) == [(TELEFON_SALVAT,)]
            c.captura("numar_salvat")
            cp.click("#not-salveaza-canal")
            cp.wait_for_function("() => !document.querySelector('#pi-continua').disabled", timeout=15000)
            assert _in_ecran(cp, "#pi-continua")
            cp.click("#pi-continua")
            cp.wait_for_selector(".cab-salut-sub", timeout=30000)
            assert cp.inner_text(".cab-salut-sub").strip() == "Portal Client"
            assert firma_561["nume"] in cp.inner_text(".cab-salut-nume")
            c.captura("portal")
            r = sql("SELECT telefon, notificari_salvate_la IS NOT NULL, rol FROM public.users WHERE email = %s", (email,))
            assert r == [(TELEFON_SALVAT, True, "client")], r
            assert not c.erori and not c.cereri_rele and not c.deschideri_singure, (c.erori, c.cereri_rele, c.deschideri_singure)
        finally:
            ctx.close()
    finally:
        _scoate_contul(email)


# ── 321 / 322 — pagina principală a cabinetului nou ──────────────────────────────────────────────────────────────────────────────
def test_def_321_rotita_deruleaza_pagina_cabinetului_nou_la_rezolutiile_uzuale(cabinet_de_la_zero):
    """321 (grav). „Cardurile «Primii pași» blochează derularea: rotița nu derulează pagina, la «De depus» / «Firme» se ajunge doar cu Tab
    sau micșorare.” Pe un cabinet NOU, creat de la zero (comanda 12.1 pct.3), cu cele trei carduri nefăcute.
    Pașii: înregistrarea, prima intrare -> pagina principală; la 1366×768, 1280×720, 1920×1080 și 393×851: rotița pe cardurile
    „Primii pași” -> pagina coboară până când cardul „Firme” e întreg în ecran (iar „De validat” / „De depus” a trecut pe sub antet sau e
    în ecran)."""
    cab = cabinet_de_la_zero()
    pg, e = cab.pg, cab.e
    treci_prima_intrare(pg)
    firme = "button.cab-card:has([data-cheie='firme'])"
    for lat, inalt in REZOLUTII:
        pg.set_viewport_size({"width": lat, "height": inalt})
        e.acasa()
        pg.wait_for_selector(_CARD % "preluare", timeout=30000)
        assert pg.locator("#inceput-carduri .inceput-card").count() == 3
        assert pg.evaluate("() => document.querySelector('.desktop').scrollTop") == 0
        bb = pg.locator(_CARD % "preluare").bounding_box()
        pg.mouse.move(bb["x"] + bb["width"] / 2, min(bb["y"] + 40, inalt - 10))
        for _ in range(25):
            if _in_ecran(pg, firme):
                break
            pg.mouse.wheel(0, 300)
            pg.wait_for_timeout(120)
        e.captura("%dx%d" % (lat, inalt))
        assert _in_ecran(pg, firme), "la %d×%d rotița nu aduce „Firme” în ecran" % (lat, inalt)
        if pg.evaluate("() => { const d = document.querySelector('.desktop'); return d.scrollHeight > d.clientHeight; }"):
            assert pg.evaluate("() => document.querySelector('.desktop').scrollTop") > 0, "la %d×%d pagina nu s-a mișcat" % (lat, inalt)


def test_def_322_lucrez_singur_pe_cabinetul_nou_bifeaza_pasul_si_dispare(cabinet_de_la_zero):
    """322. „Primii pași: «Lucrez singur» pe pas bifat nu face nimic.” Pe un cabinet NOU, creat de la zero (comanda 12.1 pct.3).
    Pașii: înregistrarea, prima intrare -> pasul 3 („Adaugă echipa”) are „Deschide Asistenți” și „Lucrez singur” -> „Lucrez singur” ->
    pasul 3 e verde, „Lucrez singur” nu mai e pe card, „Deschide Asistenți” rămâne; după reîncărcare, la fel."""
    cab = cabinet_de_la_zero()
    pg, e = cab.pg, cab.e
    treci_prima_intrare(pg)
    card = _CARD % "echipa"
    pg.wait_for_selector(card + " [data-inceput='lucrez_singur']", timeout=30000)
    assert not _verde(pg, "echipa")
    e.captura("inainte")
    pg.click(card + " [data-inceput='lucrez_singur']")
    pg.wait_for_function("(s) => document.querySelector(s).classList.contains('inceput-facut')", arg=card, timeout=20000)
    for _ in range(2):
        assert _verde(pg, "echipa")
        assert pg.locator(card + " [data-inceput='lucrez_singur']").count() == 0, "„Lucrez singur” încă pe pasul făcut"
        assert pg.locator(card + " [data-inceput='asistenti']").count() == 1, "butonul spre Asistenți a dispărut"
        e.captura("facut")
        e.acasa()
        pg.wait_for_selector(card, timeout=30000)
    assert sql("SELECT lucreaza_singur_la IS NOT NULL FROM public.accounting_firms WHERE id = %s", (cab.firm_id,)) == [(True,)]


# ── 269 / 490 — salutul ──────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_269_salutul_cabinetului_nou_numeste_omul_cu_numele_scris(cabinet_de_la_zero):
    """269. „Salutul ia ultimul cuvânt din nume («Salut, 253»)” — aceeași clasă cu 490. Toate saluturile (pagina principală a ambelor
    roluri, Panou Admin, mesajul de la logare, emailurile) trec prin `numeDeSalut` (salut.js) / `nume_de_salut` (core/common.py):
    prenumele numai dacă a fost scris separat, altfel numele întreg. Pașii: „Înregistrează cabinetul tău” cu numele „Test 253” -> prima
    intrare -> pagina principală: „Salut, Test 253”; în bază numele întreg, fără prenume tăiat din el."""
    cab = cabinet_de_la_zero(nume_admin="Test 253")
    pg = cab.pg
    treci_prima_intrare(pg)
    pg.wait_for_selector("h1.cab-salut-nume", timeout=30000)
    cab.e.captura()
    assert pg.inner_text("h1.cab-salut-nume").strip() == "Salut, Test 253"
    assert sql("SELECT nume, prenume FROM public.users WHERE email = %s", (cab.email,)) == [("Test 253", None)]


def test_def_490_salutul_nu_e_ultima_litera_din_nume(cabinet_de_la_zero):
    """490 (fost N4). „«Salut, B» pe pagina cabinetului.” Cazul văzut: un cont fără prenume, cu numele terminat într-o literă („Contabil
    B”) -> salutul era „Salut, B”. Pașii: „Înregistrează cabinetul tău” cu numele „Contabil B” -> prima intrare -> pagina principală:
    „Salut, Contabil B”, nu „Salut, B”."""
    cab = cabinet_de_la_zero(nume_admin="Contabil B")
    pg = cab.pg
    treci_prima_intrare(pg)
    pg.wait_for_selector("h1.cab-salut-nume", timeout=30000)
    cab.e.captura()
    t = pg.inner_text("h1.cab-salut-nume").strip()
    assert t == "Salut, Contabil B" and t != "Salut, B", t


# ── 320 / comanda 12.1 pct.6 — „Primii pași” pas cu pas ──────────────────────────────────────────────────────────────────────────
def _verde(pg, cheie):
    """Cardul e „făcut”: clasa, bifa și marginea stângă în culoarea `--verde` (comparată cu `--verde` calculat pe pagină)."""
    return pg.evaluate("""(s) => { const c = document.querySelector(s); if (!c) return false;
        const p = document.createElement('span'); p.style.color = 'var(--verde)'; document.body.appendChild(p);
        const verde = getComputedStyle(p).color; p.remove();
        return c.classList.contains('inceput-facut') && !!c.querySelector('.inceput-bifa')
            && getComputedStyle(c).borderLeftColor === verde; }""", _CARD % cheie)


def _starea(pg):
    pg.wait_for_selector("#inceput-carduri .inceput-card", timeout=30000)
    return {k: _verde(pg, k) for k in ("preluare", "anaf", "echipa")}


def _balanta_csv(firma):
    """Balanța de verificare în forma exportului SAGA (antet pe două rânduri, „Solduri finale”), cu numele firmei în antet: capitalul
    1.000 lei vărsat în casă — 1012 creditor, 5311 debitor."""
    r = [["Balanță de verificare analitică"], [firma], ["Perioada: 01.09.2026 - 30.09.2026"],
         ["Simbol cont", "Denumirea contului", "Solduri finale", ""], ["", "", "Debit", "Credit"],
         ["1012", "Capital subscris vărsat", 0, 1000], ["5311", "Casa în lei", 1000, 0], ["TOTAL", "", 1000, 1000]]
    return "\n".join(";".join(str(c) for c in x) for x in r).encode("utf-8")


def test_def_320_primii_pasi_pe_cabinetul_nou_pas_cu_pas_verzi_dispar_si_raman_in_ajutor(cabinet_de_la_zero):
    """320 + comanda 12.1 pct.6: „fiecare card devine verde la pasul lui, toate dispar când sunt gata și rămân accesibile din «?»”.
    Pașii administratorului unui cabinet NOU, fiecare pas în ecranul lui:
      0. după prima intrare: trei carduri, niciunul verde (pasul 2 cere și certificatul SPV);
      1. pasul 3: „Lucrez singur” -> numai „Adaugă echipa” e verde;
      2. pasul 1: Firme -> „+ Adaugă firmă” (CUI, tipul) -> firma -> „Import date” -> „Solduri inițiale” -> balanța -> „Salvează” -> pasul 1
         NU e verde (lipsește auditul) -> Control fiscal -> firma -> „Rulează auditul de preluare” -> pasul 1 verde, pasul 2 nu;
      3. pasul 2: certificatul conectat (date de pornire, vezi antetul) -> toate trei verzi -> cardurile dispar de pe pagina principală;
      4. „?” (Prezentarea aplicației) -> „Primii pași”: cele trei carduri, verzi, de citit (fără butoane)."""
    from e2e_bloc_d import _control_firma
    from e2e_pozitii_validate import _anaf_pune
    cab = cabinet_de_la_zero()
    pg, e = cab.pg, cab.e
    treci_prima_intrare(pg)
    e.acasa()
    assert _starea(pg) == {"preluare": False, "anaf": False, "echipa": False}, _starea(pg)
    assert pg.inner_text("#inceput-carduri .inceput-cap").strip() == "Primii pași"
    e.captura("0_niciunul")
    # pasul 3
    pg.click(_CARD % "echipa" + " [data-inceput='lucrez_singur']")
    pg.wait_for_function("(s) => document.querySelector(s).classList.contains('inceput-facut')", arg=_CARD % "echipa", timeout=20000)
    assert _starea(pg) == {"preluare": False, "anaf": False, "echipa": True}, _starea(pg)
    e.captura("1_echipa")
    # pasul 1: firma, balanța, auditul
    cui = cui_cu_control(96000000 + int(time.time()) % 999999)
    den = "%s L12 Start %s SRL" % (PREFIX_FIRMA, cui)
    _anaf_pune(cui, {"denumire": den, "platitor_tva": False, "cod_caen": "6920", "adresa": "Str. Probei nr. 12, București",
                     "nr_reg_com": "J40/1212/2020", "data_inregistrare": "2020-01-15", "inactiv": False, "tva_la_incasare": False})
    from e2e_bloc_a import _deschide_firme
    _deschide_firme(e)
    pg.click("#firme-adauga")
    pg.wait_for_selector("#fn-cui", timeout=10000)
    pg.fill("#fn-cui", cui)
    pg.wait_for_function("() => (document.querySelector('#fn-cui-info') || {textContent: ''}).textContent.startsWith('Din ANAF')",
                         timeout=30000)
    pg.select_option("#fn-tip", "srl")
    pg.click("#fn-salveaza")
    pg.wait_for_function("() => document.body.innerText.includes('a fost creată și apare în listă')", timeout=60000)
    e.acasa()
    assert _starea(pg) == {"preluare": False, "anaf": False, "echipa": True}, _starea(pg)
    e.firma(den)
    pg.click("#fa-import")
    pg.wait_for_selector(".mig-frand", timeout=20000)
    pg.locator(".mig-frand", has_text="Solduri ini").first.click()
    pg.wait_for_selector("#mig-file", state="attached", timeout=10000)
    pg.set_input_files("#mig-file", files=[{"name": "balanta_saga.csv", "mimeType": "text/csv", "buffer": _balanta_csv(den)}])
    pg.wait_for_selector("#mig-salveaza-sold", timeout=30000)
    if pg.query_selector("#mig-data-bal"):
        pg.fill("#mig-data-bal", "2026-09-30")
    pg.click("#mig-salveaza-sold")
    pg.wait_for_function("() => /conturi salvate/.test(document.body.innerText) || !!document.querySelector('#ca-ok')", timeout=30000)
    if pg.query_selector("#ca-ok"):                                         # o întrebare de confirmare a importului: „da”
        pg.click("#ca-ok")
        pg.wait_for_function("() => /conturi salvate/.test(document.body.innerText)", timeout=30000)
    e.captura("2_balanta")
    tid, schema = sql("SELECT id, schema_name FROM public.tenants WHERE cui = %s AND accounting_firm_id = %s", (cui, cab.firm_id))[0]
    assert sql('SELECT count(*) FROM "%s".solduri_initiale' % schema)[0][0] == 2
    e.acasa()
    assert _starea(pg) == {"preluare": False, "anaf": False, "echipa": True}, "balanța fără audit a bifat pasul 1: %s" % _starea(pg)
    _control_firma(e, {"nume": den})
    pg.click(".fereastra:last-of-type #cf-audit-run")
    pg.wait_for_function("() => { const b = document.querySelector('.fereastra:last-of-type #cf-audit-run'); return b && !b.disabled && "
                         "b.textContent === 'Rerulează auditul'; }", timeout=60000)
    e.captura("3_audit")
    e.acasa()
    assert _starea(pg) == {"preluare": True, "anaf": False, "echipa": True}, _starea(pg)
    e.captura("4_preluare")
    # pasul 2: certificatul SPV (date de pornire — conectarea reală cere certificatul și ANAF); notificările s-au salvat la prima intrare
    from core import spv_conector as sc
    sql("INSERT INTO public.spv_token (accounting_firm_id, serial_certificat, access_token, refresh_token, access_expira, refresh_expira, "
        "activ) VALUES (%s, 'E2E-L12-START', %s, %s, now() + interval '30 days', now() + interval '300 days', true)",
        (cab.firm_id, sc.cripteaza("x.e30.y"), sc.cripteaza("r")))
    e.acasa()
    pg.wait_for_timeout(1500)
    assert pg.locator("#inceput-carduri .inceput-card").count() == 0, "toate făcute: cardurile trebuiau să dispară"
    assert pg.eval_on_selector("#inceput-carduri", "z => z.hidden") is True
    e.captura("5_toate_disparute")
    pg.click("#nav-ghid")
    pg.wait_for_selector("#ans-inceput .inceput-card", timeout=20000)
    carduri = pg.eval_on_selector_all("#ans-inceput .inceput-card", "cs => cs.map((c) => [c.dataset.card, c.classList.contains('inceput-facut'), "
                                      "c.querySelectorAll('button[data-inceput]').length])")
    assert carduri == [["preluare", True, 0], ["anaf", True, 0], ["echipa", True, 0]], carduri
    e.captura("6_in_ajutor")
    assert tid


# ── clasa lui 561 / 596: fereastra „Înregistrează cabinetul tău” ────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("lat,inalt", [(1366, 768), (1280, 720)])
def test_def_c111_inregistrarea_cabinetului_incape_pe_ecran(browser, request, lat, inalt):
    """Clasa lui 561 / 596 („pagina nu derulează”, „iese din ecran”), găsită la cabinetul creat de la zero (numărul C îl dă sesiunea
    principală): fereastra „Înregistrează cabinetul tău” (`.acces-modal`, fără `max-height`, sub `html, body { overflow-y: hidden }`) e
    mai înaltă decât ecranul unui laptop, iar „Creează cont” iese din ecran, fără derulare. Pașii vizitatorului: pagina publică -> „Acces”
    -> „Client nou” -> formularul: fereastra întreagă în ecran SAU derulează ea însăși până la „Creează cont”."""
    era = mod_inregistrare("libera")
    ctx = browser.new_context(viewport={"width": lat, "height": inalt})
    e = Ecran(ctx.new_page(), request.node.name)
    try:
        vp = e.pg
        _client_nou(vp, BAZA + "/")
        vp.wait_for_selector("#reg-buton", state="attached", timeout=10000)
        e.captura("formular")
        _roteste(vp, ".acces-modal", 300)                                  # rotița pe formular, până la „Creează cont”
        assert _in_ecran(vp, "#reg-buton"), "„Creează cont” nu se poate aduce în ecran la %d×%d" % (lat, inalt)
        assert _in_ecran(vp, "#reg-cabinet") or vp.evaluate("() => document.querySelector('.acces-modal').scrollHeight > "
                                                            "document.querySelector('.acces-modal').clientHeight"), "începutul formularului e tăiat"
    finally:
        ctx.close()
        mod_inregistrare(era or "invitatie")
