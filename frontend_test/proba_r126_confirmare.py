# -*- coding: utf-8 -*-
"""PROBA R126 + R82/instanta — depunerea se incheie VIZIBIL, pe amandoua drumurile.

DECIZIA lui Costin (02.09.2026), varianta (a): *„confirmarea sta unde se ia decizia, cu depunerea
oprita si constatarea in fata."* Proba parcurge traseul REAL, pe portofoliu, si il masoara in
AMANDOUA directiile — cum cere regula 3 din `PLAN_LUCRU.md`:

  NU : cu motivele goale, ecranul REFUZA, marcheaza campurile vinovate si NU depune nimic.
  DA : cu motivele scrise, depunerea trece si confirmarile raman SCRISE in baza, cu autor.

Subiectul e construit pe `tenant_014` (cabinetul de test 4163, al contului de proba) — nu pe
cabinetul lui Costin. Vezi scenariul din commitul care aduce proba.

Ce NU probeaza, declarat: nu verifica textul constatarii (aia e a randorului unic din
`control_verdict.randA`, gardat separat) si nu masoara ce se intampla la mai mult de doua
constatari — populatia construita are exact doua.
"""
import datetime
import json
import os
import urllib.error
import urllib.request

from playwright.sync_api import sync_playwright

CFG = {}
for ln in open(os.path.expanduser("~/.iconta/fe_test.env")):
    ln = ln.strip()
    if "=" in ln and not ln.startswith("#"):
        k, v = ln.split("=", 1)
        CFG[k] = v
BAZA = os.environ.get("PROBE_BAZA") or CFG.get("FE_TEST_BAZA", "http://127.0.0.1:8010")
OUT = os.path.dirname(os.path.abspath(__file__))
TENANT = 8397          # BETA PROFIT SRL, cabinetul de test 4163
NUME_FIRMA = "BETA PROFIT"
AN, TRIM = 2025, 3     # D100 T3/2025 — rectificativa cu ACEEASI suma: depunerea ei nu misca perechea


def api(path, method="GET", body=None, tok=None):
    data = json.dumps(body).encode() if body is not None else None
    h = {"Content-Type": "application/json"}
    if tok:
        h["Authorization"] = "Bearer " + tok
    req = urllib.request.Request(BAZA + path, data=data, headers=h, method=method)
    try:
        return json.load(urllib.request.urlopen(req, timeout=90))
    except urllib.error.HTTPError as e:
        return {"_http": e.code, "_body": e.read().decode("utf-8", "ignore")}


d = api("/auth/login", "POST", {"email": CFG["FE_TEST_EMAIL"], "parola": CFG["FE_TEST_PAROLA"]})
TOK, USER = d["token"], d["user"]
print("LOGIN uid=%s cabinet=%s" % (USER.get("id"), USER.get("firm")))

# patru-ochi: OFF pentru ca itemul `la_senior` sa poarte butonul „Confirma depunerea".
# Starea de dinainte se RESTAUREAZA la final — o proba care lasa o politica schimbata otraveste
# tot ce ruleaza dupa ea.
_po = api("/eu/patru-ochi", tok=TOK) or {}
PO_INITIAL = bool(_po.get("activ"))
if PO_INITIAL:
    api("/eu/patru-ochi", "POST", {"activ": False}, TOK)

# RESETUL SUBIECTULUI PROPRIU. O confirmare acopera (firma, perioada, tip, AMPRENTA), iar amprenta
# e a CIFRELOR — deci dupa o rulare reusita aceleasi cifre sunt deja confirmate si poarta n-ar mai
# cere nimic: a doua rulare ar trece pe langa exact ce probeaza, si ar trece VERDE. *Un test care
# se autoinvalideaza la a doua rulare e mai rau decat unul care lipseste.*
# Se sterg NUMAI randurile subiectului acestei probe — firma ei, anul ei, luna ei, pe cabinetul de
# test. Nu e curatenie generala: e resetul unei fixturi pe care proba insasi a scris-o.
import psycopg2
_DBURL = None
for _ln in open(os.path.expanduser("~/.iconta/db.env")):
    _ln = _ln.strip()
    if _ln.startswith("DATABASE_URL="):
        _DBURL = _ln.split("=", 1)[1]
_cx = psycopg2.connect(_DBURL); _cx.autocommit = True


def reset_confirmari(eticheta):
    with _cx.cursor() as _cur:
        _cur.execute("DELETE FROM public.supervizor_confirmari WHERE tenant_id=%s AND an=%s AND luna=%s",
                     (TENANT, AN, TRIM * 3))
        print("reset confirmari (%s): %d" % (eticheta, _cur.rowcount))


reset_confirmari("start")

# Elementul de apasat: se refoloseste cel activ, daca exista; altfel se creeaza pe calea rutei.
coada = (api("/coada", tok=TOK) or {}).get("coada") or []
activ = [c for c in coada if c.get("tenant_id") == TENANT and c.get("tip") == "d100"
         and c.get("stare") in ("la_senior", "aprobata")]
if activ:
    ELEM = activ[0]["id"]
    print("elementul de coada exista deja: %s" % ELEM)
else:
    r = api("/coada", "POST", {"tenant_id": TENANT, "tip": "d100", "an": AN, "trim": TRIM}, TOK)
    assert r.get("ok"), "n-am putut crea elementul de coada: %r" % r
    ELEM = r["coada_id"]
    print("element de coada creat: %s" % ELEM)

INIT = ('sessionStorage.setItem("iconta_token",' + json.dumps(TOK) + ');'
        'sessionStorage.setItem("iconta_user",' + json.dumps(json.dumps(USER)) + ');')


def sc(pg, n):
    p = os.path.join(OUT, n)
    pg.screenshot(path=p, full_page=True)
    print("screenshot:", p)


def deschide_coada(pg):
    pg.goto(BAZA + "/", wait_until="networkidle")
    pg.wait_for_selector(".cab-card", timeout=25000)
    pg.wait_for_timeout(900)
    pg.click('.cab-card:has(.cab-card-sinteza[data-cheie="validat"])')
    pg.wait_for_selector(".val-card", timeout=15000)
    pg.wait_for_timeout(500)


def cardul_probei(pg):
    """Indexul cardului firmei probei, citit din DOM — nu presupus ca e primul."""
    subs = pg.eval_on_selector_all(".val-sub", "els=>els.map(e=>e.innerText)")
    for i, s in enumerate(subs):
        if NUME_FIRMA.lower() in (s or "").lower():
            return i
    raise AssertionError("nu gasesc cardul firmei %r in coada: %r" % (NUME_FIRMA, subs))


try:
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        ctx = b.new_context(viewport={"width": 1250, "height": 2000})
        ctx.add_init_script(INIT)
        pg = ctx.new_page()
        # Erorile care conteaza sunt cele de EXECUTIE (`pageerror`). Din consola se sare linia pe
        # care browserul o scrie pentru orice raspuns non-2xx — iar 409-ul de aici e chiar
        # raspunsul PROIECTAT al portii, nu un defect. *Un filtru pe „error" fara distinctia asta
        # ar face proba sa cada exact pe comportamentul pe care il probeaza.*
        erori_js = []
        pg.on("pageerror", lambda e: erori_js.append("pageerror: " + str(e)))
        pg.on("console", lambda m: erori_js.append("consola: " + m.text)
              if (m.type == "error" and "Failed to load resource" not in m.text) else None)

        deschide_coada(pg)
        idx = cardul_probei(pg)
        sc(pg, "r126_1_coada.png")

        # ── pasul 1: „Confirma depunerea" -> dialogul cu indexul SPV ──────────────────────────
        pg.query_selector_all(".val-depune")[idx].click()
        pg.wait_for_selector("#dlg-input", timeout=10000)
        pg.wait_for_timeout(300)
        sc(pg, "r126_2_dialog_spv.png")
        pg.click("#dlg-ok")

        # ── pasul 2: 409 -> pasul de confirmare, in ACEEASI fereastra ─────────────────────────
        pg.wait_for_selector(".val-conf-item", timeout=20000)
        pg.wait_for_timeout(400)
        n_const = len(pg.query_selector_all(".val-conf-item"))
        avert = pg.eval_on_selector(".caseta-atentie .ca-mesaj", "e=>e.innerText")
        temeiuri = pg.eval_on_selector_all(".val-conf-item .cf-incr-temei", "els=>els.map(e=>e.innerText.trim())")
        etichete = pg.eval_on_selector_all(".val-conf-item label", "els=>els.map(e=>e.getAttribute('for'))")
        campuri = pg.eval_on_selector_all(".val-conf-motiv", "els=>els.map(e=>e.id)")
        print("PAS CONFIRMARE -> constatari:", n_const)
        print("  avertisment:", (avert or "")[:120])
        print("  temeiuri prezente:", [len(t) > 40 for t in temeiuri])
        print("  etichete/campuri:", etichete, campuri)
        sc(pg, "r126_3_pas_confirmare.png")

        assert n_const == 2, "asteptam 2 constatari CERTE pe subiectul construit, sunt %d" % n_const
        assert all(len(t) > 40 for t in temeiuri), "o constatare a ajuns pe ecran FARA temei: %r" % temeiuri
        assert etichete == campuri, "eticheta nu e legata de campul ei (for != id): %r vs %r" % (etichete, campuri)

        # ── DIRECTIA „NU": motive goale -> refuz, campuri marcate, NIMIC depus ────────────────
        pg.click("#val-conf-ok")
        pg.wait_for_timeout(700)
        er = pg.eval_on_selector("#val-conf-eroare", "e=>e.innerText.trim()")
        invalide = len(pg.query_selector_all(".val-conf-motiv.camp-invalid"))
        pe_camp = len(pg.query_selector_all('.msg-eroare[data-camp]'))
        inca_acolo = len(pg.query_selector_all(".val-conf-item"))
        print("GOL -> eroare=%r · campuri marcate=%d · mesaje pe camp=%d · pasul inca deschis=%s"
              % (er, invalide, pe_camp, inca_acolo == 2))
        sc(pg, "r126_4_gol_refuzat.png")
        assert er, "cu motivele goale ecranul n-a spus nimic"
        assert invalide == 2 and pe_camp == 2, "campurile vinovate nu sunt marcate (%d/%d)" % (invalide, pe_camp)
        assert inca_acolo == 2, "pasul s-a inchis desi n-a depus nimic"

        st = api("/coada", tok=TOK)
        stare_dupa_gol = [c["stare"] for c in (st.get("coada") or []) if c["id"] == ELEM]
        print("  starea elementului dupa refuz:", stare_dupa_gol)
        assert stare_dupa_gol and stare_dupa_gol[0] != "depusa", "a depus desi motivele erau goale!"

        # ── axe pe pasul de confirmare (desktop) ─────────────────────────────────────────────
        pg.evaluate(open(os.path.join(OUT, "vizual", "axe.min.js"), encoding="utf-8").read())
        axe_res = pg.evaluate("""async () => {
          const r = await axe.run('.fereastra-corp', {runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa']}, resultTypes:['violations']});
          const C=new Set(['color-contrast','color-contrast-enhanced']);
          const L=new Set(['label','select-name','aria-input-field-name','button-name','link-name','input-button-name','form-field-multiple-labels']);
          let contrast=0,label=0,alte=[];
          for (const v of r.violations){ if(C.has(v.id))contrast+=v.nodes.length; else if(L.has(v.id))label+=v.nodes.length; else alte.push(v.id+':'+v.nodes.length); }
          return {contrast, label, alte};
        }""")
        print("AXE pas confirmare ->", axe_res)
        assert axe_res["contrast"] == 0 and axe_res["label"] == 0, "axe: %r" % axe_res

        tinte = pg.evaluate("""() => Array.from(document.querySelectorAll('.fereastra-corp button'))
            .map(b=>({t:b.innerText.trim(), h:Math.round(b.getBoundingClientRect().height)}))
            .filter(x=>x.h > 0 && x.h < 24)""")
        print("tinte de atingere sub 24px:", tinte)
        assert not tinte, "tinte de atingere sub 24px (AA 2.5.8): %r" % tinte

        # ── DIRECTIA „DA": motive scrise -> depune, confirmarile raman SCRISE ─────────────────
        MOTIVE = ["rectificativa pe randul 50 pleaca saptamana asta; termenul D100 e azi",
                  "nota de impozit pe 691 se inregistreaza la inchiderea anului"]
        for i, m in enumerate(MOTIVE):
            pg.fill("#val-conf-%d" % i, m)
        sc(pg, "r126_5_motive_scrise.png")
        pg.click("#val-conf-ok")
        # [DS cap.27 / E2] Confirmarea actului sta in PASUL in care s-a petrecut, nu in lista de sub
        # el: forma dinainte o scria dupa `nav.inapoi()`, iar re-randarea o stergea. Proba asta a
        # gasit-o goala — de-aia aserttiunea e pe caseta din pas.
        pg.wait_for_selector(".caseta-info .ci-mesaj", timeout=25000)
        msg = pg.eval_on_selector(".caseta-info .ci-mesaj", "e=>e.innerText.trim()")
        print("DUPA DEPUNERE -> confirmare=%r" % msg[:160])
        sc(pg, "r126_6_confirmat_depus.png")
        assert msg, "actul s-a incheiat in tacere (DS cap.27 / E2): demontarea ferestrei nu e confirmare"
        # numeste ENTITATEA si CONSECINTA, nu doar „gata"
        assert NUME_FIRMA.lower() in msg.lower(), "confirmarea nu numeste firma: %r" % msg
        assert "depus" in msg.lower() and "confirmat" in msg.lower(),             "confirmarea nu numeste consecinta (depusa + constatari confirmate): %r" % msg
        assert pg.query_selector("#val-conf-gata"), "confirmarea n-are iesire — omul ramane blocat in pas"
        pg.click("#val-conf-gata")
        pg.wait_for_selector(".val-card, .stare-goala", timeout=25000)
        pg.wait_for_timeout(600)

        assert not erori_js, "erori JS in consola: %r" % erori_js[:3]

        # ── mobil (Pixel 5): pasul trebuie randat fara revarsare orizontala ───────────────────
        mob = b.new_context(viewport={"width": 393, "height": 851}, device_scale_factor=2.75,
                            is_mobile=True, has_touch=True)
        mob.add_init_script(INIT)
        mp = mob.new_page()
        # ── A DOUA APASARE [defect gasit apasand, 02.09] ─────────────────────────────────────
        # Secventa REALA a lui Costin, masurata in uvicorn.log pe elementul 8052:
        #   POST /aproba -> 200 · POST /depune -> 409 · (a doua apasare) POST /aproba -> 409
        # Elementul ramanea `aprobata`, iar a doua apasare murea inainte sa ajunga la depunere.
        # Acum inlantuirea a iesit din client: se trimite UN act, si aprobarea vine DUPA poarta.
        reset_confirmari("inainte de a doua apasare")
        r4 = api("/coada", "POST", {"tenant_id": TENANT, "tip": "d100", "an": AN, "trim": TRIM}, TOK)
        assert r4.get("ok"), "n-am putut pregati proba celei de-a doua apasari: %r" % r4
        elem2 = r4["coada_id"]

        def _stare(eid):
            st = api("/coada", tok=TOK) or {}
            return next((c["stare"] for c in (st.get("coada") or []) if c["id"] == eid), None)

        for tura in (1, 2):
            deschide_coada(pg)
            pg.query_selector_all(".val-depune")[cardul_probei(pg)].click()
            pg.wait_for_selector("#dlg-input", timeout=10000)
            pg.click("#dlg-ok")
            pg.wait_for_selector(".val-conf-item", timeout=20000)
            n = len(pg.query_selector_all(".val-conf-item"))
            st = _stare(elem2)
            print("APASAREA %d -> pasul s-a deschis cu %d constatari · starea elementului: %s"
                  % (tura, n, st))
            assert n == 2, "apasarea %d n-a deschis pasul de confirmare" % tura
            assert st == "la_senior", (
                "apasarea %d a lasat elementul in %r — un refuz al portii nu are voie sa mute "
                "starea: din `aprobata` nu se mai poate RESPINGE" % (tura, st))
            pg.click("#val-conf-renunt")     # abandon, exact ca in secventa reala
            pg.wait_for_timeout(400)
        sc(pg, "r126_9_a_doua_apasare.png")

        # ── DRUMUL FARA CONSTATARI [R82/instanta, decizia lui Costin 02.09] ──────────────────
        # *„acelasi buton nu poate sa se incheie vizibil pe un drum si tacut pe celalalt, iar
        # drumul tacut e cel obisnuit."* Firma asta (ALFA MICRO) n-are D101 depus, deci perechile
        # raspund GRI, nu rosu — poarta nu cere nimic si depunerea trece direct.
        r3 = api("/coada", "POST", {"tenant_id": 8396, "tip": "d300", "an": 2026, "luna": 8}, TOK)
        assert r3.get("ok") or r3.get("_http") == 409, "n-am putut pregati depunerea simpla: %r" % r3
        deschide_coada(pg)
        subs = pg.eval_on_selector_all(".val-sub", "els=>els.map(e=>e.innerText)")
        i_alfa = next(i for i, s in enumerate(subs) if "ALFA MICRO" in (s or ""))
        pg.query_selector_all(".val-depune")[i_alfa].click()
        pg.wait_for_selector("#dlg-input", timeout=10000)
        pg.click("#dlg-ok")
        pg.wait_for_selector(".caseta-info .ci-mesaj", timeout=25000)
        simplu = pg.eval_on_selector(".caseta-info .ci-mesaj", "e=>e.innerText.strip()"
                                     if False else "e=>e.innerText.trim()")
        fara_pas = len(pg.query_selector_all(".val-conf-item"))
        print("DEPUNERE SIMPLA -> confirmare=%r · constatari pe drum=%d" % (simplu[:120], fara_pas))
        sc(pg, "r126_8_depunere_simpla.png")
        assert fara_pas == 0, "drumul simplu n-ar fi trebuit sa aiba pas de constatari"
        assert simplu and "depus" in simplu.lower(),             "depunerea FARA constatari s-a incheiat in tacere: %r" % simplu
        assert "ALFA MICRO" in simplu, "confirmarea nu numeste firma: %r" % simplu
        assert "confirmat" not in simplu.lower(),             "caseta vorbeste despre constatari confirmate desi n-a fost niciuna: %r" % simplu
        assert pg.query_selector("#val-conf-gata"), "confirmarea n-are iesire"
        pg.click("#val-conf-gata")
        pg.wait_for_selector(".val-card, .stare-goala", timeout=25000)

        # acelasi motiv ca la start: legul de desktop tocmai a confirmat cifrele, iar amprenta nu
        # s-a schimbat — fara reset, poarta n-ar mai avea ce cere pe telefon.
        reset_confirmari("inainte de mobil")
        # Elementul poate exista deja: legul de mai sus abandoneaza de doua ori, deliberat, iar
        # `ux_coada_activa` nu lasa o a doua intrare ACTIVA pe aceeasi perioada. Refolosirea e
        # raspunsul corect — proba mobila are nevoie de un element, nu de unul nou.
        r2 = api("/coada", "POST", {"tenant_id": TENANT, "tip": "d100", "an": AN, "trim": TRIM}, TOK)
        assert r2.get("ok") or r2.get("_http") == 409,             "n-am putut pregati elementul pentru proba mobila: %r" % r2
        deschide_coada(mp)
        mp.query_selector_all(".val-depune")[cardul_probei(mp)].click()
        mp.wait_for_selector("#dlg-input", timeout=10000)
        mp.click("#dlg-ok")
        mp.wait_for_selector(".val-conf-item", timeout=20000)
        mp.wait_for_timeout(400)
        body_w = mp.evaluate("() => document.body.scrollWidth")
        print("MOBIL Pixel5 -> body scrollWidth:", body_w)
        mp.screenshot(path=os.path.join(OUT, "r126_7_mobil.png"), full_page=True)
        assert body_w <= 400, "revarsare orizontala pe telefon (body=%s)" % body_w
        # elementul mobil ramane in coada, neconfirmat — nu depune nimic pe drumul asta
finally:
    _cx.close()
    if PO_INITIAL:
        api("/eu/patru-ochi", "POST", {"activ": True}, TOK)
        print("patru-ochi restaurat la ACTIV")

print("PROBA R126 OK: refuzul cu motive goale marcheaza campurile si nu depune; cu motivele scrise "
      "depune si confirmarile raman scrise; depunerea FARA constatari se incheie cu aceeasi caseta, "
      "fara sa vorbeasca despre confirmari; axe curat; mobil fara revarsare.")
print("RULAT LA:", datetime.datetime.now().isoformat(timespec="seconds"))
