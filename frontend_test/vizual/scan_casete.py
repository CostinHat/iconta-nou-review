# -*- coding: utf-8 -*-
"""SCANER de casete — observatorul. Produce FAPTE, nu verdicte.

Culege două lucruri despre același ecran, în același moment:
  (a) ce s-a RANDAT   — secțiunile din DOM, cu contorul din titlu și numărul de rânduri;
  (b) ce a VENIT      — payload-ul /control-fiscal/{id}, cu lungimea fiecărei liste.

Nu compară nimic. Comparația e în core/test_harta_casete.py, față de așteptarea scrisă în
frontend_test/vizual/harta_casete.py. Cele trei acte rămân separate deliberat (vezi DECIZII 20.08).

Rulare:  PYTHONPATH=<rad>:<rad>/frontend_test ./venv/bin/python frontend_test/vizual/scan_casete.py [tenant_id]
"""
import json
import os
import re
import sys
import urllib.request

_HERE = os.path.dirname(os.path.abspath(__file__))
_RAD = os.path.abspath(os.path.join(_HERE, "..", ".."))
sys.path.insert(0, _RAD)

from core import db, auth_api  # noqa: E402
import psycopg2.extras as _E  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

BAZA = "http://127.0.0.1:8010"
ARTEFACT = os.path.join(_HERE, "casete_control_fiscal.json")
UTILIZATOR = "patron@prisma-cont.test"

# citeste sectiunile randate: titlu, contorul din titlu, cate randuri are grupul care urmeaza
CITESTE = """() => {
  const norm = (s) => (s || "").replace(/\\s+/g, " ").trim();
  const out = [];
  for (const t of document.querySelectorAll(".fereastra-corp .cf-grup-titlu")) {
    const txt = norm(t.textContent);
    const m = txt.match(/^(.*?)\\s*\\((\\d+)\\)$/);
    // grupul de randuri = urmatorul .cf-decl frate
    let n = null, el = t.nextElementSibling;
    if (el && el.classList.contains("cf-decl")) {
      n = el.querySelectorAll(".cf-decl-item, .cf-incr-rand, .cf-verif").length;
    }
    out.push({titlu: m ? m[1] : txt, contor: m ? Number(m[2]) : null, randuri: n});
  }
  return {sectiuni: out,
          are_gata: !!document.querySelector(".fereastra-corp .mig-gata-titlu"),
          gata_text: norm((document.querySelector(".fereastra-corp .mig-gata-titlu") || {}).textContent)};
}"""


def _token():
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
            cur.execute("SELECT u.*, af.nume AS nume_firma FROM public.users u "
                        "LEFT JOIN public.accounting_firms af ON af.id=u.accounting_firm_id "
                        "WHERE u.email=%s", (UTILIZATOR,))
            u = cur.fetchone()
    if not u:
        raise SystemExit("utilizator %r negasit" % UTILIZATOR)
    u = dict(u)
    tok = auth_api.emite_token(u)
    safe = {k: (v.isoformat() if hasattr(v, "isoformat") else v)
            for k, v in u.items() if k not in ("parola_hash", "parola")}
    return tok, safe


def _payload(tok, tid):
    req = urllib.request.Request(BAZA + "/control-fiscal/%d" % tid,
                                 headers={"Authorization": "Bearer " + tok})
    return json.load(urllib.request.urlopen(req, timeout=90))


def _deschide(pg, nume):
    pg.goto(BAZA + "/", wait_until="networkidle")
    pg.wait_for_selector(".cab-card", timeout=25000); pg.wait_for_timeout(500)
    pg.get_by_text("Firme", exact=True).first.click(timeout=8000); pg.wait_for_timeout(350)
    pg.get_by_text("Firme existente", exact=False).first.click(timeout=8000)
    pg.wait_for_selector("button.firme-rand", timeout=10000)
    pg.get_by_text(nume, exact=False).first.click(timeout=8000)
    pg.wait_for_selector("[id^='fa-']", timeout=10000); pg.wait_for_timeout(250)
    pg.click("#fa-control")
    pg.wait_for_selector(".fereastra-corp .cf-grup-titlu, .fereastra-corp .mig-gata-titlu", timeout=20000)
    pg.wait_for_timeout(1200)


def main():
    tid = int(sys.argv[1]) if len(sys.argv) > 1 else 4784
    tok, user = _token()
    tn = json.load(urllib.request.urlopen(urllib.request.Request(
        BAZA + "/tenants", headers={"Authorization": "Bearer " + tok}), timeout=60))
    firma = next((t for t in tn.get("tenants", []) if t.get("id") == tid), None)
    if not firma:
        raise SystemExit("tenant %d inaccesibil userului %s" % (tid, UTILIZATOR))

    d = _payload(tok, tid)
    init = ('sessionStorage.setItem("iconta_token",' + json.dumps(tok) + ');'
            'sessionStorage.setItem("iconta_user",' + json.dumps(json.dumps(user)) + ');')
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        ctx = b.new_context(viewport={"width": 1300, "height": 2200})
        ctx.add_init_script(init)
        pg = ctx.new_page()
        _deschide(pg, firma.get("nume"))
        randat = pg.evaluate(CITESTE)
        b.close()

    vc = d.get("verificari_contabile") or {}
    art = {
        "tenant_id": tid,
        "firma": firma.get("nume"),
        "schema": firma.get("schema_name"),
        "randat": randat,
        "payload": {
            "stare": d.get("stare"),
            # [R3] cele doua cifre ale pastilei - fara ele constrangerea nu poate rula
            "datorate": d.get("datorate"),
            "depuse": d.get("depuse"),
            "lungimi": {k: len(d.get(k) or []) for k in
                        ("lipsa", "urmarit", "neclar", "neaplicabile", "cu_intarziere", "confirmate",
                         "limite")},
            "contabil_total": len(d.get("contabil") or []) if isinstance(d.get("contabil"), list) else None,
            "contabil_etichete": [c.get("eticheta") for c in (d.get("contabil") or [])
                                  if isinstance(c, dict)],
            "vc_chei_prezente": sorted([k for k, v in vc.items() if v]),
            "vc_cu_constatari": sorted([k for k, v in vc.items()
                                        if isinstance(v, dict) and (v.get("constatari") or [])]),
            # [P3 21.08.2026] Se retine si FELUL, nu doar cheile: constrangerea reala e ca ce cere
            # felul sa fie prezent (campurile urmeaza forma afirmatiei), nu ca exista o cheie anume.
            "randuri_motiv": {
                "neclar": [{"fel": x.get("fel"), "chei": sorted(x.keys())}
                           for x in (d.get("neclar") or [])],
                "neaplicabile": [{"fel": x.get("fel"), "chei": sorted(x.keys())}
                                 for x in (d.get("neaplicabile") or [])],
            },
            "randuri_decl": {
                k: [sorted(x.keys()) for x in (d.get(k) or [])]
                for k in ("lipsa", "urmarit", "cu_intarziere", "confirmate")
            },
            "perechi_tip_perioada": {
                k: [(x.get("tip"), x.get("perioada")) for x in (d.get(k) or [])]
                for k in ("lipsa", "urmarit", "neclar", "neaplicabile", "cu_intarziere", "confirmate")
            },
        },
    }
    with open(ARTEFACT, "w", encoding="utf-8") as f:
        json.dump(art, f, ensure_ascii=False, indent=1, sort_keys=True)
    print("ARTEFACT scris: %s" % ARTEFACT)
    print("  firma: %s (tid %d)" % (art["firma"], tid))
    print("  sectiuni randate: %d -> %s" % (len(randat["sectiuni"]),
                                            ", ".join(s["titlu"] for s in randat["sectiuni"])))
    print("  payload: stare=%s lungimi=%s" % (art["payload"]["stare"], art["payload"]["lungimi"]))


if __name__ == "__main__":
    main()
