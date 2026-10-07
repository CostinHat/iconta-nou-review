# -*- coding: utf-8 -*-
"""PROBA în browser — FAPT_FISCAL_NECERUT în ecranele scrise de mână (comanda Costin 07.10.2026: „Extinde regula la ecranele scrise de
mână, cu clasificarea celor 82”), pe baza de TEST (8011).

INVENTAR  Pe fiecare ecran și formular de declarație atins: toate selecturile vizibile — id/clasă, ce e ales la deschidere, dacă au
          „— alege —”. Înainte/după, pe aceleași drumuri: aici se vede că niciun fapt fiscal nu mai vine ales de ecran.
REFUZ     (numai după) Trimiterea fără alegere se refuză LÂNGĂ câmp: D301 › Adaugă rând, Casă › Adaugă dispoziție, Emitere › Emite.
          Înainte, aceleași butoane trimiteau valorile preselectate — de aceea nu se apasă înainte (ar scrie în bază).
VIZUAL    axe + lățime de telefon (393px) pe fiecare ecran atins.

    PYTHONPATH=.:frontend_test:frontend_test/vizual ./venv/bin/python frontend_test/proba_selecturi_ecrane.py --iesire /tmp/…/x.json [--refuz]
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vizual"))

from playwright.sync_api import sync_playwright  # noqa: E402

from axe_scan import scaneaza  # noqa: E402
from core import db  # noqa: E402
from proba_c1_c2_c7 import CAB, declaratie, firma, pagina  # noqa: E402

F2 = "Constructii Profit Trim SRL"
F1 = "Firma Grea Audit SRL"
F3 = "Distributie Profit IC SRL"
#: declarațiile cu formular manual în pasul 2: (tip, firmă, an, lună)
DECLARATII = [("d390", F3, 2026, 8), ("d301", F1, 2026, 8), ("d710", F1, 2026, "T3"), ("d307", F1, 2026, 8), ("d177", F1, 2025, None),
              ("d200", F1, 2025, None), ("d230", F1, 2025, None), ("d223", F1, 2025, None), ("d208", F1, 2025, None),
              ("d221", F1, 2025, None), ("d603", F1, 2025, None), ("d110", F1, 2026, 8), ("d398", F1, 2026, "T3"),
              ("d318", F1, 2025, None), ("d212", F1, 2025, None), ("d207", F1, 2025, None), ("d300", F1, 2026, 8)]

SELECTURI = """() => [...document.querySelectorAll('.fereastra-corp select')].filter(s => s.offsetParent).map(s => {
  const o = s.options[s.selectedIndex];
  return {sel: s.id || ('.' + [...s.classList].filter(c => c !== 'camp-input').join('.')), ales: o ? o.textContent.trim() : null,
          alege: !!s.querySelector('option[data-alege]') || (o && o.value === '')};
})"""


def instantaneu(pg, cap, nume, r):
    r.setdefault("selecturi", {})[nume] = pg.evaluate(SELECTURI)
    pg.screenshot(path=os.path.join(cap, "%s.png" % nume), full_page=True)
    viol, _t = scaneaza(pg)
    pg.set_viewport_size({"width": 393, "height": 851}); pg.wait_for_timeout(250)
    rev = pg.evaluate("() => document.documentElement.scrollWidth > window.innerWidth")
    pg.set_viewport_size({"width": 1366, "height": 900})
    r.setdefault("vizual", {})[nume] = {"axe_reguli": len(viol), "axe_noduri": sum(v["n"] for v in viol), "revarsare_x_393": rev}


def pas(r, nume, f):
    try:
        f()
    except Exception as e:  # noqa: BLE001 — un ecran care nu se deschide se consemnează, proba continuă
        r.setdefault("nu_s_a_ajuns", {})[nume] = "%s: %s" % (type(e).__name__, str(e).splitlines()[0][:200])


def reper_casa():
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute('select coalesce(max(id),0) from "tenant_005".casa_operatiuni'); a = cur.fetchone()[0]
        cur.execute('select coalesce(max(id),0) from "tenant_005".inregistrari'); b = cur.fetchone()[0]
        cur.execute("select coalesce(max(id),0) from public.declaratii_coada"); q = cur.fetchone()[0]
        c.rollback()
    return a, b, q


def scris_casa(rp):
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute('select categorie, suma::text from "tenant_005".casa_operatiuni where id > %s', (rp[0],)); ops = [list(x) for x in cur.fetchall()]
        cur.execute('select l.cont_debit, l.cont_credit, l.suma::text from "tenant_005".inregistrari i join "tenant_005".inregistrari_linii l '
                    'on l.inregistrare_id = i.id where i.id > %s', (rp[1],)); lin = [list(x) for x in cur.fetchall()]
        c.rollback()
    return {"operatii": ops, "linii_nota": lin}


def curata_casa(rp):
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute('delete from "tenant_005".casa_operatiuni where id > %s', (rp[0],))
        cur.execute('delete from "tenant_005".inregistrari where id > %s', (rp[1],))
        cur.execute("delete from public.declaratii_coada where id > %s", (rp[2],))
        c.commit()


def mesaje(pg):
    return [e.inner_text().strip()[:200] for e in pg.query_selector_all(".fereastra-corp .msg-eroare, .fereastra-corp .msg-avert")][:4]


def proba(pw, cap, refuz, r):
    b, pg, er = pagina(pw, CAB)

    def datefirma():
        firma(pg, F2); pg.click("#fa-datefirma"); pg.wait_for_selector("#df-salveaza", timeout=15000); pg.wait_for_timeout(1200)
        instantaneu(pg, cap, "date_firma", r)
    pas(r, "date_firma", datefirma)

    def emitere():
        firma(pg, F2); pg.click("#fa-facturi", timeout=8000); pg.wait_for_timeout(1400)
        pg.get_by_text("Emite", exact=False).first.click(timeout=8000); pg.wait_for_selector("#em-emite", timeout=15000); pg.wait_for_timeout(1500)
        instantaneu(pg, cap, "emitere", r)
        if refuz:
            # butonul e dezactivat de lipsurile din Date firmă ale firmei de test: se activează în probă ca să se exercite
            # verificarea din handler — refuzul vine ÎNAINTE de orice cerere, deci serverul nu e atins
            dezactivat = pg.evaluate("() => document.querySelector('#em-emite').disabled")
            pg.evaluate("() => { document.querySelector('#em-emite').disabled = false; }")
            pg.click("#em-emite"); pg.wait_for_timeout(1500)
            r["refuz_emitere"] = {"buton_dezactivat_de_lipsuri": dezactivat, "mesaje": mesaje(pg), "campuri_marcate": pg.evaluate(
                "() => [...document.querySelectorAll('.fereastra-corp select.camp-invalid')].map(s => s.id)")}
            pg.screenshot(path=os.path.join(cap, "refuz_emitere.png"), full_page=True)
    pas(r, "emitere", emitere)

    def casa():
        firma(pg, F2); pg.click("#fa-casa"); pg.wait_for_selector("#c-toggle", timeout=15000); pg.click("#c-toggle"); pg.wait_for_timeout(600)
        instantaneu(pg, cap, "casa", r)
        if refuz:
            pg.fill("#c-data", "2026-09-15"); pg.fill("#c-suma", "100"); pg.click("#c-adauga"); pg.wait_for_timeout(1500)
            r["refuz_casa"] = {"mesaje": mesaje(pg)}
            pg.screenshot(path=os.path.join(cap, "refuz_casa.png"), full_page=True)
            # drumul complet: după alegere, dispoziția se scrie (nota ciornă), iar categoria aleasă ajunge în ea
            rp = reper_casa()
            pg.select_option("#c-cat", "incasare_client"); pg.fill("#c-part", "Client Probă SRL"); pg.click("#c-adauga"); pg.wait_for_timeout(2500)
            r["drum_casa"] = {"mesaje": [m for m in mesaje(pg)], "scris": scris_casa(rp)}
            pg.screenshot(path=os.path.join(cap, "drum_casa.png"), full_page=True)
            curata_casa(rp)
    pas(r, "casa", casa)

    def etransport():
        firma(pg, F2); pg.click("#fa-etransport"); pg.wait_for_timeout(2000)
        instantaneu(pg, cap, "etransport", r)
    pas(r, "etransport", etransport)

    def bilant():
        firma(pg, F2); pg.click("#fa-bilant"); pg.wait_for_timeout(2500)
        instantaneu(pg, cap, "bilant", r)
    pas(r, "bilant", bilant)

    def salariati():
        firma(pg, "Panificatie Salarii Speciale SRL"); pg.click("#fa-salariati"); pg.wait_for_timeout(2000)
        instantaneu(pg, cap, "salariati", r)
    pas(r, "salariati", salariati)

    for tip, fir, an, luna in DECLARATII:
        def dec(tip=tip, fir=fir, an=an, luna=luna):
            if isinstance(luna, str):          # trimestrială: „T3”
                firma(pg, fir); pg.click("#fa-declaratii"); pg.wait_for_selector("#dec-tip", timeout=20000); pg.wait_for_timeout(500)
                pg.select_option("#dec-tip", tip); pg.wait_for_timeout(300); pg.fill("#dec-an", str(an))
                pg.select_option("#dec-trim", luna[1:]); pg.click("#dec-continua")
                pg.wait_for_function("() => /Pasul 2/.test(document.querySelector('.fereastra-corp').innerText)", timeout=90000)
                pg.wait_for_timeout(2500)
            else:
                declaratie(pg, fir, tip, an, luna)
            instantaneu(pg, cap, "decl_%s" % tip, r)
            if refuz and tip == "d301" and pg.query_selector("#d301-add"):
                pg.click("#d301-add"); pg.wait_for_timeout(1500)
                r["refuz_d301"] = {"mesaje": mesaje(pg)}
                pg.screenshot(path=os.path.join(cap, "refuz_d301.png"), full_page=True)
        pas(r, "decl_%s" % tip, dec)
    r["erori_consola"] = er
    b.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--iesire", required=True)
    ap.add_argument("--refuz", action="store_true")
    a = ap.parse_args()
    cap = a.iesire.replace(".json", "_capturi"); os.makedirs(cap, exist_ok=True)
    db.init_pool()
    r = {}
    t0 = time.time()
    try:
        with sync_playwright() as pw:
            proba(pw, cap, a.refuz, r)
    except Exception as e:  # noqa: BLE001
        r["EROARE_PROBA"] = "%s: %s" % (type(e).__name__, str(e).splitlines()[0][:300])
    finally:
        r["durata_s"] = round(time.time() - t0, 1)
        json.dump(r, open(a.iesire, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    pre = {k: [s for s in v if not s["alege"]] for k, v in r.get("selecturi", {}).items()}
    print("ecrane:", len(r.get("selecturi", {})), "nu_s_a_ajuns:", r.get("nu_s_a_ajuns"))
    print("selecturi vizibile cu o valoare deja aleasă:", sum(len(v) for v in pre.values()))
    for k, v in pre.items():
        if v:
            print("  %-16s %s" % (k, [(s["sel"], s["ales"]) for s in v][:8]))
    for k in ("refuz_emitere", "refuz_casa", "drum_casa", "refuz_d301", "erori_consola", "EROARE_PROBA", "durata_s"):
        if k in r:
            print(k, json.dumps(r[k], ensure_ascii=False)[:400])


if __name__ == "__main__":
    main()
