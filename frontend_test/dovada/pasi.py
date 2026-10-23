# -*- coding: utf-8 -*-
"""frontend_test/dovada/pasi.py — parcurgerea unei liste de DOVEZI pe ecran (comanda Costin 11.2 pct.3), pentru
`scripts/dovada_firme_test.py --capturi`. Aceleași unelte ca plasa de capăt la capăt (`frontend_test/e2e/conftest.py`: `Ecran` cu erorile
JS și cererile 5xx, deschiderea firmei din cabinet, garda deschiderilor fără clic), dar fără pytest: o dovadă care nu se vede se SCRIE în
`dovezi.json` (ce s-a cerut, ce s-a văzut), nu oprește restul.

Forma unei dovezi (JSON):
  {"nr": "428", "firma": "tenant_9055", "descriere": "...", "pasi": [...], "verifica": [...], "captura": "428_f6_x.png",
   "intreaga": false}
  - `firma`: schema copiei (`tenant_9049` …) sau a sursei (`tenant_049` …); firma se deschide din cabinet, ca în plasă (`Ecran.firma`).
  - `pasi` (în ordine; fiecare un obiect cu O acțiune):
      {"click": CSS, ["text": T], ["daca_exista": true]}   clic pe primul element CSS (cu textul T, dacă e dat); cu `daca_exista`,
                                            un element absent nu e o eroare (ex. „Vezi XML-ul generat” numai când declarația s-a generat)
      {"asteapta": CSS, ["text": T], ["stare": "visible"|"attached"]}
      {"asteapta_text": T}                  textul apare în pagină
      {"completeaza": CSS, "valoare": V} / {"alege": CSS, "valoare": V}
      {"deruleaza": CSS, ["text": T]}       aduce elementul în ecran
      {"pauza": MS}
      {"captura": NUME}                     o captură intermediară
      {"declaratie": TIP, "an": A, ["luna": L], ["trim": T]}   Declarații -> tipul -> perioada -> „Continuă →” -> pasul 2 sau refuzul
                                            (alegerea tipului și a perioadei: `declaratie_tip.alege_tipul`, `conftest.alege_perioada`)
      {"incarca": CSS, "generator": "modul:funcție", ["argumente": [...]], "nume": FIȘIER}   fișierul dat de funcție (octeți), încărcat
                                            în câmpul de fișier — sursa lui e aceeași cu a testelor (ex. balanța SAGA a lui 439)
  - `verifica` (după pași): {"contine": T, ["zona": CSS]}, {"nu_contine": T, ["zona": CSS]}, {"inactiv": CSS, ["text": T]},
      {"activ": CSS, ["text": T]}, {"exista": CSS, ["text": T]}, {"contine_oricare": [T1, T2, …], ["zona": CSS]},
      {"valoare": CSS, "egal": V} (valoarea câmpului, nu textul: cifra scrisă de contabil într-un câmp, C102). Textul se compară cu spațiile normalizate; fără `zona`, pe fereastra
      din față (ce citește contabilul, `Ecran.fereastra`).
  - `posibila_de_la` (ZZZZ-LL-ZZ, opțional): data de la care aplicația poate arăta dovada (ex. o declarație pe o lună neîncheiată, pe
      care aplicația o refuză până la sfârșitul ei — deficiența 383); înainte de ea dovada se parcurge și se scrie ce s-a văzut, cu starea
      „imposibila_azi”, nu „neîndeplinită”.
Rezultatul fiecărei dovezi: {nr, firma, captura, stare (indeplinita / neindeplinita / imposibila_azi), ok, verificari: [{cerut, ok, vazut}],
erori_js, cereri_5xx, eroare_pas, durata_s}.
"""
import datetime as _dt
import json
import os
import sys
import time
import urllib.request

RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#: Acțiunile unui pas și felurile de verificare (forma de mai sus); lista de dovezi e păzită pe ele (`core/test_dovada_firme_test.py`).
PASI = ("click", "asteapta", "asteapta_text", "completeaza", "alege", "deruleaza", "pauza", "captura", "declaratie", "incarca")
VERIFICARI = ("contine", "nu_contine", "contine_oricare", "inactiv", "activ", "exista", "valoare")


def _e2e(baza, capturi):
    """Modulul `conftest` al plasei, cu baza aplicației probate (citită de el la import)."""
    os.environ["PROBA_BAZA"], os.environ["E2E_CAPTURI"] = baza, capturi
    for p in (os.path.join(RAD, "frontend_test", "e2e"), os.path.join(RAD, "frontend_test"), RAD):
        if p not in sys.path:
            sys.path.insert(0, p)
    import conftest
    return conftest


def autentifica(baza, email, parola):
    """Tokenul pe drumul browserului: `POST /auth/login` (aceeași rută ca formularul de intrare)."""
    cer = urllib.request.Request(baza + "/auth/login", data=json.dumps({"email": email, "parola": parola}).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    r = json.loads(urllib.request.urlopen(cer, timeout=30).read().decode())
    return ("sessionStorage.setItem('iconta_token'," + json.dumps(r["token"]) + ");"
            "sessionStorage.setItem('iconta_user'," + json.dumps(json.dumps(r["user"])) + ");")


def _norm(t):
    return " ".join((t or "").split())


def _loc(pg, pas, cheie):
    loc = pg.locator(pas[cheie])
    if pas.get("text"):
        loc = loc.filter(has_text=pas["text"])
    return loc.first


def _pas(e, pas):
    pg = e.pg
    if "click" in pas:
        loc = _loc(pg, pas, "click")
        if pas.get("daca_exista") and not loc.count():
            return
        loc.click(timeout=30000)
        pg.wait_for_timeout(400)
    elif "asteapta" in pas:
        _loc(pg, pas, "asteapta").wait_for(state=pas.get("stare", "visible"), timeout=40000)
    elif "asteapta_text" in pas:
        pg.wait_for_function("(t) => document.body.innerText.replace(/\\s+/g, ' ').includes(t)", arg=_norm(pas["asteapta_text"]),
                             timeout=40000)
    elif "completeaza" in pas:
        pg.fill(pas["completeaza"], str(pas["valoare"]))
        pg.dispatch_event(pas["completeaza"], "change")
    elif "alege" in pas:
        pg.select_option(pas["alege"], str(pas["valoare"]))
    elif "deruleaza" in pas:
        _loc(pg, pas, "deruleaza").scroll_into_view_if_needed(timeout=20000)
    elif "pauza" in pas:
        pg.wait_for_timeout(int(pas["pauza"]))
    elif "captura" in pas:
        pg.screenshot(path=os.path.join(os.environ["E2E_CAPTURI"], pas["captura"]))
    elif "declaratie" in pas:
        import conftest
        from declaratie_tip import alege_tipul
        zona = ".fereastra:last-of-type "
        pg.click("#fa-declaratii")
        pg.wait_for_selector(zona + "#dec-tip", timeout=40000)
        alege_tipul(pg, pas["declaratie"], zona=zona)
        conftest.alege_perioada(pg, pas["an"], pas.get("luna"), pas.get("trim"), zona=zona)
        pg.click(zona + "#dec-continua")
        pg.wait_for_function("() => { const f = [...document.querySelectorAll('.fereastra')].pop(); return f && (f.innerText.includes("
                             "'Pasul 2 din 3') || !!f.querySelector('.dec-eroare, .msg-eroare:not(:empty), .caseta-eroare')); }", timeout=120000)
    elif "incarca" in pas:
        import importlib
        modul, functie = pas["generator"].split(":")
        octeti = getattr(importlib.import_module(modul), functie)(*pas.get("argumente", []))
        pg.set_input_files(pas["incarca"], files=[{"name": pas["nume"], "mimeType": pas.get("tip", "text/csv"), "buffer": octeti}])
    else:
        raise ValueError("pas necunoscut: %r" % (pas,))


def _text(e, zona):
    if zona:
        loc = e.pg.locator(zona)
        return _norm(" ".join(loc.all_inner_texts())) if loc.count() else ""
    return _norm(e.fereastra())


def _decupaj(text, cautat, lat=160):
    i = text.find(cautat)
    if i < 0:
        return text[:400]
    return text[max(0, i - lat): i + len(cautat) + lat]


def _verifica(e, v):
    pg = e.pg
    if "contine_oricare" in v:
        text = _text(e, v.get("zona"))
        gasite = [x for x in v["contine_oricare"] if _norm(x) in text]
        return {"cerut": v, "ok": bool(gasite), "vazut": _decupaj(text, _norm(gasite[0])) if gasite else text[:400]}
    if "contine" in v or "nu_contine" in v:
        cautat = _norm(v.get("contine", v.get("nu_contine")))
        text = _text(e, v.get("zona"))
        gasit = cautat in text
        return {"cerut": v, "ok": gasit if "contine" in v else not gasit, "vazut": _decupaj(text, cautat)}
    if "valoare" in v:
        loc = _loc(pg, v, "valoare")
        if not loc.count():
            return {"cerut": v, "ok": False, "vazut": "elementul nu există pe ecran"}
        val = loc.input_value()
        return {"cerut": v, "ok": val == str(v["egal"]), "vazut": "valoarea câmpului: %r" % val}
    for cheie in ("inactiv", "activ", "exista"):
        if cheie in v:
            loc = _loc(pg, v, cheie)
            if not loc.count():
                return {"cerut": v, "ok": False, "vazut": "elementul nu există pe ecran"}
            info = loc.evaluate("(el) => ({dez: !!(el.disabled || el.getAttribute('aria-disabled') === 'true'), "
                                "text: (el.innerText || el.value || '').trim(), titlu: el.title || '', "
                                "motiv: (el.closest('*') && el.parentElement ? el.parentElement.innerText : '').trim().slice(0, 400)})")
            ok = {"inactiv": info["dez"], "activ": not info["dez"], "exista": True}[cheie]
            return {"cerut": v, "ok": ok, "vazut": "%s | dezactivat=%s | title=%s | lângă: %s" % (
                info["text"][:120], info["dez"], info["titlu"][:200], _norm(info["motiv"])[:300])}
    raise ValueError("verificare necunoscută: %r" % (v,))


def ruleaza(dovezi, baza, email, parola, firme, iesire, lat=1700, inalt=1000):
    """Parcurge dovezile pe aplicația de la `baza`, cu utilizatorul copiei. `firme` = {schema copiei: {nume, sursa, …}}."""
    from playwright.sync_api import sync_playwright
    c = _e2e(baza, iesire)
    sesiune = autentifica(baza, email, parola)
    dupa_sursa = {v["sursa"]: k for k, v in firme.items()}
    rez = []
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True)
        for d in dovezi:
            t0 = time.time()
            schema = d["firma"] if d["firma"] in firme else dupa_sursa.get(d["firma"])
            ctx = b.new_context(viewport={"width": d.get("latime", lat), "height": d.get("inaltime", inalt)})
            ctx.add_init_script(sesiune)
            ctx.add_init_script(c.GARDA_DESCHIDERI)
            e = c.Ecran(ctx.new_page(), "dovada_%s" % d["nr"])
            r = {"nr": d["nr"], "firma": schema, "nume_firma": (firme.get(schema) or {}).get("nume"), "descriere": d.get("descriere"),
                 "captura": os.path.join(iesire, d["captura"]), "verificari": [], "eroare_pas": None}
            try:
                if schema is None:
                    raise ValueError("firma %r nu e în copie" % d["firma"])
                e.firma(firme[schema]["nume"])
                for i, pas in enumerate(d.get("pasi", [])):
                    try:
                        _pas(e, pas)
                    except Exception as ex:  # noqa: BLE001 — pasul care n-a mers se scrie, dovada iese neîndeplinită
                        raise RuntimeError("pasul %d %s: %s" % (i + 1, json.dumps(pas, ensure_ascii=False), str(ex).splitlines()[0]))
                e.pg.wait_for_timeout(int(d.get("pauza_finala", 600)))
                r["verificari"] = [_verifica(e, v) for v in d.get("verifica", [])]
            except Exception as ex:  # noqa: BLE001
                r["eroare_pas"] = str(ex)[:600]
            try:
                e.pg.screenshot(path=r["captura"], full_page=bool(d.get("intreaga")))
            except Exception as ex:  # noqa: BLE001
                r["eroare_captura"] = str(ex)[:300]
            r["erori_js"], r["cereri_5xx"], r["deschideri_fara_clic"] = e.erori[:5], e.cereri_rele[:5], e.deschideri_singure[:5]
            r["ok"] = (not r["eroare_pas"] and all(v["ok"] for v in r["verificari"]) and bool(r["verificari"])
                       and not r["erori_js"] and not r["cereri_5xx"])
            r["stare"] = "indeplinita" if r["ok"] else "neindeplinita"
            if not r["ok"] and d.get("posibila_de_la") and _dt.date.today().isoformat() < d["posibila_de_la"]:
                r["stare"], r["motiv_imposibil"] = "imposibila_azi", "aplicația o poate arăta abia de la %s" % d["posibila_de_la"]
            r["durata_s"] = round(time.time() - t0, 1)
            ctx.close()
            print("[dovada] %-6s %-14s %s (%.1f s)%s" % (d["nr"], schema, {"indeplinita": "ÎNDEPLINITĂ", "neindeplinita": "NEÎNDEPLINITĂ",
                                                                         "imposibila_azi": "IMPOSIBILĂ AZI"}[r["stare"]], r["durata_s"],
                                                        (" — " + r["eroare_pas"][:200]) if r["eroare_pas"] else ""), flush=True)
            for v in r["verificari"]:
                if not v["ok"]:
                    print("          nevăzut: %s | văzut: %s" % (json.dumps(v["cerut"], ensure_ascii=False), v["vazut"][:300]), flush=True)
            rez.append(r)
        b.close()
    return rez
