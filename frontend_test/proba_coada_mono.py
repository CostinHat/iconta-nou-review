# -*- coding: utf-8 -*-
"""Proba randare reala pentru #2 (coada vizibila mono-utilizator), #3 (perioada declarata + termen), #4 (text DUKIntegrator).
Ecran principal -> card coada -> ecranul cozii -> depunere; toggle patru-ochi ON/OFF; generare d300 -> text validare.
Curata la final intrarile create."""
import os, json, urllib.request, datetime
from playwright.sync_api import sync_playwright

CFG = {}
for ln in open(os.path.expanduser("~/.iconta/fe_test.env")):
    ln = ln.strip()
    if "=" in ln and not ln.startswith("#"):
        k, v = ln.split("=", 1); CFG[k] = v
BAZA = os.environ.get("PROBE_BAZA") or CFG.get("FE_TEST_BAZA", "http://127.0.0.1:8010")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)))
TENANT = 8396  # ALFA MICRO
RUN_START = datetime.datetime.now()

def api(path, method="GET", body=None, tok=None):
    data = json.dumps(body).encode() if body is not None else None
    h = {"Content-Type": "application/json"}
    if tok: h["Authorization"] = "Bearer " + tok
    req = urllib.request.Request(BAZA + path, data=data, headers=h, method=method)
    try:
        return json.load(urllib.request.urlopen(req, timeout=25))
    except urllib.error.HTTPError as e:
        return {"_http": e.code, "_body": e.read().decode("utf-8", "ignore")}

# --- login ---
d = api("/auth/login", "POST", {"email": CFG["FE_TEST_EMAIL"], "parola": CFG["FE_TEST_PAROLA"]})
TOK, USER = d["token"], d["user"]
print("LOGIN rol=%s" % USER.get("rol"))

# --- setup: patru-ochi OFF + creaza intrari in coada ---
api("/eu/patru-ochi", "POST", {"activ": False}, TOK)
created_coada_ids = []
r_lunar = api("/coada", "POST", {"tenant_id": TENANT, "tip": "d300", "an": 2026, "luna": 8}, TOK)
print("POST coada lunar ->", r_lunar)
if r_lunar.get("ok"): created_coada_ids.append(r_lunar["coada_id"])

# item trimestrial (pentru proba formatului "trim. III 2026") — insert SQL controlat
import psycopg2, psycopg2.extras as _E, hashlib
DBURL = None
for ln in open(os.path.expanduser("~/.iconta/db.env")):
    ln = ln.strip()
    if ln.startswith("DATABASE_URL="): DBURL = ln.split("=", 1)[1]
conn = psycopg2.connect(DBURL); conn.autocommit = True
payload_trim = {"xml": "<DECL_TRIM/>", "_an": 2026, "_luna": None, "_trim": 3,
                "avertismente": [], "note_rezultat": [], "randuri": None}
hsh = hashlib.sha256(("probatrim" + RUN_START.isoformat()).encode()).hexdigest()
with conn.cursor() as cur:
    cur.execute(
        "INSERT INTO public.declaratii_coada (cabinet_id, tenant_id, tip, perioada, stare, payload, hash, creat_de, creat_de_id) "
        "VALUES (%s,%s,%s,%s,'la_senior',%s,%s,%s,%s) RETURNING id",
        (4163, TENANT, "d300", "26.10.2026", _E.Json(payload_trim),
         hsh, str(USER["id"]), USER["id"]))
    trim_id = cur.fetchone()[0]
created_coada_ids.append(trim_id)
print("SQL insert trimestrial coada_id=%s" % trim_id)

INIT = ('sessionStorage.setItem("iconta_token",' + json.dumps(TOK) + ');'
        'sessionStorage.setItem("iconta_user",' + json.dumps(json.dumps(USER)) + ');')

def sc(pg, n):
    p = os.path.join(OUT, n); pg.screenshot(path=p, full_page=True); print("screenshot:", p)

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    ctx = b.new_context(viewport={"width": 1200, "height": 1700}); ctx.add_init_script(INIT)
    pg = ctx.new_page()

    # ============ #2 patru-ochi OFF: dashboard -> card "De depus" ============
    pg.goto(BAZA + "/", wait_until="networkidle")
    pg.wait_for_selector(".cab-card", timeout=25000); pg.wait_for_timeout(1200)
    tit_off = pg.eval_on_selector('.cab-card:has(.cab-card-sinteza[data-cheie="validat"]) .cab-card-titlu', "e=>e.innerText")
    sin_off = pg.eval_on_selector('.cab-card-sinteza[data-cheie="validat"]', "e=>e.innerText")
    print('CARD OFF -> titlu=%r sinteza=%r' % (tit_off, sin_off))
    sc(pg, "coada_mono_1_dashboard_OFF.png")

    # click cardul -> ecranul cozii
    pg.click('.cab-card:has(.cab-card-sinteza[data-cheie="validat"])')
    pg.wait_for_selector(".val-card", timeout=15000); pg.wait_for_timeout(500)
    grup = pg.eval_on_selector(".cf-grup-titlu", "e=>e.innerText")
    titluri = pg.eval_on_selector_all(".val-titlu", "els=>els.map(e=>e.innerText)")
    termene = pg.eval_on_selector_all(".val-termen", "els=>els.map(e=>e.innerText)")
    butoane = pg.eval_on_selector_all(".val-depune", "els=>els.map(e=>e.innerText)")
    print("COADA grup=%r" % grup)
    print("COADA titluri=%r" % titluri)
    print("COADA termene=%r" % termene)
    print("COADA butoane depune=%r" % butoane)
    sc(pg, "coada_mono_2_ecran_coada.png")

    # ============ #2 depunere end-to-end pe itemul trimestrial ============
    # gaseste cardul cu D300 · trim. III 2026 si apasa Confirma depunerea
    idx = None
    for i, t in enumerate(titluri):
        if "trim" in t.lower():
            idx = i; break
    if idx is None: idx = 0
    dep_btns = pg.query_selector_all(".val-depune")
    dep_btns[idx].click()
    pg.wait_for_selector("#dlg-input", timeout=8000); pg.wait_for_timeout(300)
    sc(pg, "coada_mono_3_dialog_depunere.png")
    pg.click("#dlg-ok")  # depune fara index SPV -> aproba+depune inlantuit
    pg.wait_for_timeout(2500)
    # reincarca ecranul cozii
    titluri2 = pg.eval_on_selector_all(".val-titlu", "els=>els.map(e=>e.innerText)")
    print("COADA dupa depunere titluri=%r" % titluri2)
    sc(pg, "coada_mono_4_dupa_depunere.png")

    # ============ #2 patru-ochi ON: dashboard -> card "De validat" ============
    api("/eu/patru-ochi", "POST", {"activ": True}, TOK)
    pg.goto(BAZA + "/", wait_until="networkidle")
    pg.wait_for_selector(".cab-card", timeout=25000); pg.wait_for_timeout(1200)
    tit_on = pg.eval_on_selector('.cab-card:has(.cab-card-sinteza[data-cheie="validat"]) .cab-card-titlu', "e=>e.innerText")
    sin_on = pg.eval_on_selector('.cab-card-sinteza[data-cheie="validat"]', "e=>e.innerText")
    print('CARD ON -> titlu=%r sinteza=%r' % (tit_on, sin_on))
    sc(pg, "coada_mono_5_dashboard_ON.png")

    # ============ #4 text DUKIntegrator la generare d300 valida ============
    pg.goto(BAZA + "/", wait_until="networkidle")
    pg.wait_for_selector(".cab-card", timeout=25000); pg.wait_for_timeout(600)
    card = pg.query_selector('.cab-card:has(.cab-card-sinteza[data-cheie="declaratii"])')
    if card:
        card.click()
    else:
        pg.get_by_text("Firme", exact=True).first.click(timeout=8000); pg.wait_for_timeout(400)
        pg.get_by_text("Firme existente", exact=False).first.click(timeout=8000)
        pg.wait_for_selector("button.firme-rand", timeout=10000)
        pg.get_by_text("ALFA MICRO", exact=False).first.click(timeout=8000)
        pg.wait_for_selector("#fa-declaratii", timeout=10000); pg.click("#fa-declaratii")
    pg.wait_for_selector("#dec-tip", timeout=15000); pg.wait_for_timeout(400)
    if pg.query_selector("#dec-firma"):
        pg.select_option("#dec-firma", str(TENANT)); pg.wait_for_timeout(1000)
    pg.wait_for_selector('#dec-tip option[value="d300"]', timeout=8000, state="attached")
    pg.select_option("#dec-tip", "d300"); pg.wait_for_timeout(600)
    if pg.query_selector("#dec-an"):
        pg.fill("#dec-an", "2026"); pg.dispatch_event("#dec-an", "change")
    if pg.query_selector("#dec-luna"):
        pg.select_option("#dec-luna", "7")  # iulie 2026 (evita conflictul cu intrarile de test)
    pg.wait_for_timeout(300)
    pg.wait_for_selector("#dec-continua:not([disabled])", timeout=6000)
    pg.click("#dec-continua")
    pg.wait_for_selector(".dec-ok, .dec-eroare, .dec-avert", timeout=30000); pg.wait_for_timeout(800)
    blk = pg.eval_on_selector(".dec-ok, .dec-eroare, .dec-avert", "e=>e.className+' :: '+e.innerText")
    print("BLOC ANAF #4 =>", repr(blk))
    sc(pg, "coada_mono_6_text_dukintegrator.png")

    b.close()

# --- cleanup: patru-ochi OFF (stare initiala) + sterge intrarile create ---
api("/eu/patru-ochi", "POST", {"activ": False}, TOK)
with conn.cursor() as cur:
    if created_coada_ids:
        cur.execute("DELETE FROM public.declaratii_coada WHERE id = ANY(%s)", (created_coada_ids,))
        print("cleanup coada sterse ids=%s" % created_coada_ids)
    cur.execute("DELETE FROM public.declaratii_depuse WHERE tenant_id=%s AND tip='d300' AND data_depunere >= %s",
                (TENANT, RUN_START))
    print("cleanup depuse randuri sterse=%s" % cur.rowcount)
conn.close()
print("DONE")
