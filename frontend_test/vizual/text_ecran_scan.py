# -*- coding: utf-8 -*-
"""TEXTUL AFIȘAT pe ecrane, citit din browser și judecat de `core/limba_ecran.py` (comanda Costin 09.10.2026, „Retest 2” pct.2:
„verificarea se face pe ecranul afișat, cu valorile din date și din enumerări, nu pe șirurile din codul sursă”).

Ce parcurge:
  · pe fiecare firmă din FIRME: TOATE cardurile firmei (`#fa-*`, citite din pagină la rulare, nu dintr-o listă scrisă aici);
  · desktopul cabinetului: toate cardurile lui (`button.cab-card`);
  · drumurile adânci: Control fiscal pe firmă, declarațiile generate (D300, D390, D394, D406) pe o perioadă cu date.
Pe fiecare ecran: deschide toate `<details>`, citește nodurile de TEXT vizibile (textul scris, nu cel transformat de CSS — un antet
cu `text-transform: uppercase` nu e o „majusculă de accent”) și opțiunile selecturilor; scrie captura ecranului.
Valorile introduse de om (nume de firme, parteneri, articole, salariați, utilizatori, mijloace fixe) se citesc din bază și se scot din
text înainte de judecată — nu sunt textul aplicației.

Ieșire: `<dir>/text_ecran.json` (ecran -> defecte, cu contextul rândului) + `<dir>/<ecran>.png`; artefactul care se comite e
`frontend_test/vizual/text_ecran.json` (cu `ui_hash`, ca `acoperire_vizuala.json`), păzit de `core/test_text_ecran.py`.
Uz: python text_ecran_scan.py <dir_iesire> [--artefact]"""
import json
import os
import re
import sys

from playwright.sync_api import sync_playwright

import nav_ecrane
import w_auth
from w_auth import BAZA, INIT

RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, RAD)
from core import db  # noqa: E402
from core.limba_ecran import defecte  # noqa: E402

FIRME = ["Comert Micro TVA", "Constructii Profit Trim", "Achizitii IC Neplatitor", "Distributie Profit IC"]
DECLARATII = [("d300", "2026", None, "8"), ("d390", "2026", None, "8"), ("d394", "2026", "3", "8"), ("d406", "2026", "3", "8")]

TEXT_VIZIBIL = """() => {
  const f = [...document.querySelectorAll('.fereastra')].pop() || document.body;
  f.querySelectorAll('details').forEach(d => { d.open = true; });
  const out = [];
  const w = document.createTreeWalker(f, NodeFilter.SHOW_TEXT);
  let n;
  while ((n = w.nextNode())) {
    const p = n.parentElement; if (!p) continue;
    if (['SCRIPT', 'STYLE', 'OPTION', 'TEXTAREA'].includes(p.tagName) || p.closest('pre, code')) continue;   // XML-ul generat e fișierul ANAF, nu text de ecran
    if (p.closest('[hidden]') || p.offsetParent === null && getComputedStyle(p).position !== 'fixed') continue;
    const t = n.nodeValue.replace(/\\s+/g, ' ').trim(); if (t) out.push(t);
  }
  f.querySelectorAll('select option').forEach(o => { const t = o.textContent.trim(); if (t) out.push(t); });
  return out; }"""


def date_excluse():
    db.init_pool()
    out = set()
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute("SELECT nume FROM public.tenants UNION SELECT coalesce(nume,'') || ' ' || coalesce(prenume,'') FROM public.users "
                    "UNION SELECT nume FROM public.users UNION SELECT prenume FROM public.users UNION SELECT nume FROM public.accounting_firms")
        out |= {r[0] for r in cur.fetchall() if r[0]}
        cur.execute("SELECT schema_name FROM public.tenants")
        for (s,) in cur.fetchall():
            for q in ("SELECT tert_nume FROM %s.facturi", "SELECT denumire FROM %s.articole", "SELECT denumire FROM %s.mijloace_fixe",
                      "SELECT nume || ' ' || prenume FROM %s.salariati", "SELECT nume FROM %s.salariati", "SELECT prenume FROM %s.salariati",
                      "SELECT nume FROM %s.firma_profil", "SELECT adresa FROM %s.firma_profil", "SELECT partener FROM %s.casa_operatiuni",
                      "SELECT denumire FROM %s.produse",
                      # numerele documentelor sunt introduse de om sau de numerotarea lui („FIC”, „ZT-0012”), nu textul aplicației;
                      # descrierile notelor NU se scot: le scrie aplicația (notele 121/122, Retest 2 pct.2)
                      "SELECT numar FROM %s.facturi", "SELECT coalesce(serie,'') || numar FROM %s.facturi", "SELECT serie FROM %s.facturi", "SELECT numar FROM %s.inregistrari",
                      "SELECT document FROM %s.casa_operatiuni", "SELECT numar FROM %s.nir",
                      # textul extrasului bancar e al băncii, descrierea notei MANUALE e a contabilului, simbolul contului e un cod
                      # (4428.01 nu e o sumă), iar denumirea unui analitic o scrie omul; denumirile planului general rămân judecate
                      "SELECT descriere FROM %s.extras_linii", "SELECT descriere FROM %s.inregistrari WHERE sursa = 'manual'",
                      "SELECT simbol FROM %s.plan_conturi",
                      "SELECT denumire FROM %s.plan_conturi WHERE simbol ~ '[._/-]'"):
                try:
                    cur.execute("SAVEPOINT s"); cur.execute(q % s)
                    out |= {r[0] for r in cur.fetchall() if r[0]}
                except Exception:  # noqa: BLE001 — tabelul nu există pe schema asta
                    cur.execute("ROLLBACK TO SAVEPOINT s")
        c.rollback()
    return out


def _citeste(pg, cheie, out_dir, excl, rez):
    pg.wait_for_timeout(1500)
    linii = pg.evaluate(TEXT_VIZIBIL)
    gasite = []
    for ln in dict.fromkeys(linii):
        for fel, frag in defecte(ln, excl):
            gasite.append({"fel": fel, "fragment": frag, "rand": ln[:160]})
    nume = re.sub(r"[^a-z0-9_]+", "_", cheie.lower())[:80]
    pg.screenshot(path=os.path.join(out_dir, nume + ".png"), full_page=True)
    rez[cheie] = {"linii": len(linii), "defecte": gasite, "captura": nume + ".png"}
    print("%-60s linii %4d  defecte %d" % (cheie[:60], len(linii), len(gasite)), flush=True)


def main():
    out_dir = sys.argv[1]
    os.makedirs(out_dir, exist_ok=True)
    excl = date_excluse()
    rez = {}
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True)
        ctx = b.new_context(viewport={"width": 1700, "height": 1000})
        ctx.add_init_script(INIT)
        pg = ctx.new_page()
        erori = []
        pg.on("pageerror", lambda e: erori.append(str(e)[:200]))
        # desktopul cabinetului
        pg.goto(BAZA + "/", wait_until="domcontentloaded"); pg.wait_for_selector(".cab-card", timeout=20000)
        cab = pg.eval_on_selector_all("button.cab-card [data-cheie]", "els => els.map(e => e.dataset.cheie)")
        for k in cab:
            try:
                pg.goto(BAZA + "/", wait_until="domcontentloaded"); pg.wait_for_selector(".cab-card", timeout=20000)
                pg.click("button.cab-card:has([data-cheie='%s'])" % k, timeout=8000); pg.wait_for_timeout(2500)
                _citeste(pg, "cabinet/" + k, out_dir, excl, rez)
            except Exception as e:  # noqa: BLE001
                rez["cabinet/" + k] = {"eroare": str(e)[:200]}
        for firma in FIRME:
            try:
                w_auth.deschide_firma(pg, firma)
                carduri = pg.eval_on_selector_all("[id^='fa-']", "els => els.filter(e => e.offsetParent !== null).map(e => e.id)")
            except Exception as e:  # noqa: BLE001
                rez["firma/" + firma] = {"eroare": str(e)[:200]}
                continue
            for fid in carduri:
                cheie = "%s/%s" % (firma, fid)
                try:
                    w_auth.deschide_firma(pg, firma)
                    pg.click("#" + fid, timeout=8000)
                    _citeste(pg, cheie, out_dir, excl, rez)
                except Exception as e:  # noqa: BLE001
                    rez[cheie] = {"eroare": str(e)[:200]}
            for tip, an, trim, luna in DECLARATII:
                cheie = "%s/declaratie_%s" % (firma, tip)
                try:
                    w_auth.deschide_firma(pg, firma)
                    pg.click("#fa-declaratii", timeout=8000); pg.wait_for_timeout(2000)
                    pg.select_option("#dec-tip", tip); pg.wait_for_timeout(800)
                    for sel, v in (("#dec-an", an), ("#dec-trim", trim), ("#dec-luna", luna)):
                        if v and pg.query_selector(sel):
                            try:
                                pg.select_option(sel, v)
                            except Exception:  # noqa: BLE001
                                pass
                    pg.click("#dec-continua", timeout=8000); pg.wait_for_timeout(12000)
                    _citeste(pg, cheie, out_dir, excl, rez)
                except Exception as e:  # noqa: BLE001
                    rez[cheie] = {"eroare": str(e)[:200]}
        rez["_erori_js"] = erori
        b.close()
    total = sum(len(v.get("defecte", [])) for k, v in rez.items() if isinstance(v, dict))
    rez["_total"] = total
    json.dump(rez, open(os.path.join(out_dir, "text_ecran.json"), "w"), ensure_ascii=False, indent=1)
    print("ECRANE %d · DEFECTE %d · ERORI NAVIGARE %d" % (len([k for k in rez if not k.startswith("_")]), total,
                                                        sum(1 for v in rez.values() if isinstance(v, dict) and "eroare" in v)))
    if "--artefact" in sys.argv:
        from acoperire_hash import ui_hash
        from core.limba_ecran import instrument_hash
        art = {"ui_hash": ui_hash(), "instrument_hash": instrument_hash(), "ecrane": sorted(k for k in rez if not k.startswith("_")),
               "total_defecte": total,
               "defecte": {k: v["defecte"] for k, v in rez.items() if isinstance(v, dict) and v.get("defecte")},
               "erori_navigare": {k: v["eroare"] for k, v in rez.items() if isinstance(v, dict) and "eroare" in v}}
        json.dump(art, open(os.path.join(RAD, "frontend_test", "vizual", "text_ecran.json"), "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    nav_ecrane  # noqa: B018 — același loc de adevăr pentru navigare (deschide_firma vine prin w_auth)
    main()
