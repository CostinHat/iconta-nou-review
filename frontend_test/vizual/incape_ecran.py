# -*- coding: utf-8 -*-
"""[lotul 14, 687 — clasă] FIECARE FEREASTRĂ DE LUCRU ÎNCAPE PE UN ECRAN, la 1920 × 1080 și la 1366 × 768 (comanda Costin 14.1, verbatim:
„fiecare fereastră de lucru încape pe un singur ecran, fără derulare, la 1920 × 1080 și la 1366 × 768; dacă nu încape, se reorganizează
(coloane, file, carduri pliate pentru secundar, lățimea întreagă), nu se micșorează scrisul. Excepție: tabelele lungi (registre, balanțe)
— se derulează doar tabelul, titlul, filtrele și acțiunile rămân fixe. Verificatorul face captura la ambele rezoluții și blochează lotul la
orice derulare.”).

Parcurge ecranele din `nav_ecrane` (ECRANE + ECRANE_CAMPANIE + ECRANE_CABINET), fiecare la ambele rezoluții, și măsoară pe fereastra de
deasupra: corpul ei (`.fereastra-corp`) derulează (scrollHeight > clientHeight)? Cât din derulare e al unui TABEL (un descendent cu
`overflow-y:auto|scroll` care e el însuși cel ce derulează — excepția) și cât e al ferestrei? Captură a ferestrei la fiecare rezoluție.

Ieșire: `incape_ecran.json` (cu `ui_hash`), capturile în `<iesire>`. Exit 1 dacă există o fereastră care derulează în afara excepției.
Uz (aplicația de probă pe 8019, baza de test):  PROBA_BAZA=http://127.0.0.1:8019 python frontend_test/vizual/incape_ecran.py [--doar=a,b] [<iesire>]
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.sync_api import sync_playwright  # noqa: E402

import nav_ecrane  # noqa: E402
import w_auth  # noqa: E402

REZOLUTII = [(1920, 1080), (1366, 768)]
ARTEFACT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "incape_ecran.json")
VERDICTE_RELE = ("deruleaza", "deruleaza-cutie", "zona-ingusta")

#: măsoară fereastra de deasupra. `derulare_tabel` = suma depășirilor ale cutiilor-tabel care derulează ele (excepția), `depasire` =
#: cât trece corpul ferestrei peste înălțimea lui vizibilă, `bara_pagina` = pagina însăși derulează.
JS_MASOARA = """() => {
  const fer = [...document.querySelectorAll('.fereastra')].filter(f => f.offsetParent !== null || getComputedStyle(f).position === 'fixed').pop();
  const corp = fer && fer.querySelector('.fereastra-corp');
  const r = {fereastra: !!fer, vw: innerWidth, vh: innerHeight};
  const doc = document.scrollingElement;
  r.bara_pagina = doc.scrollHeight - doc.clientHeight;
  const desk = document.querySelector('.desktop');
  r.bara_desktop = desk ? desk.scrollHeight - desk.clientHeight : 0;
  if (!corp) return r;
  r.depasire = corp.scrollHeight - corp.clientHeight;
  r.corp_h = corp.clientHeight;
  r.fer_h = fer.getBoundingClientRect().height;
  r.lateral = corp.scrollWidth - corp.clientWidth;
  const cutii = [];
  for (const e of corp.querySelectorAll('*')) {
    const s = getComputedStyle(e);
    if ((s.overflowY === 'auto' || s.overflowY === 'scroll') && e.scrollHeight > e.clientHeight + 1 && e.clientHeight > 0) {
      cutii.push({tag: e.tagName.toLowerCase(), cls: (e.className || '').toString().slice(0, 40), id: e.id || '',
                  tabel: !!e.querySelector('table') || e.tagName === 'TABLE' || e.classList.contains('zona-derulare'), depasire: e.scrollHeight - e.clientHeight});
    }
  }
  r.cutii = cutii;
  const zona = corp.querySelector('.zona-derulare');
  if (zona) { r.zona_h = zona.clientHeight; r.zona_cont = zona.scrollHeight; r.zona_depasire = zona.scrollHeight - zona.clientHeight; }
  r.titlu = (fer.querySelector('h1,h2,.fereastra-titlu') || {}).innerText || '';
  return r;
}"""


def masoara(pg):
    return pg.evaluate(JS_MASOARA)


def verdict(m):
    """OK / DERULEAZĂ / FĂRĂ-FEREASTRĂ, după regula 687: derularea ferestrei în afara unui tabel lung e defect."""
    if not m.get("fereastra"):
        return "fara-fereastra"
    cutii_tabel = [c for c in m.get("cutii", []) if c["tabel"]]
    # fereastra derulează ea (corpul) -> defect, afară de cazul în care depășirea vine numai dintr-un tabel care derulează el însuși
    if m.get("depasire", 0) > 1 or m.get("lateral", 0) > 1 or m.get("bara_pagina", 0) > 1:
        return "deruleaza"
    if [c for c in m.get("cutii", []) if not c["tabel"]]:
        return "deruleaza-cutie"
    # tabelul lung derulează în zona lui, dar lăsat fără loc (explicații și casete deasupra) nu mai e „datele sub titlu”: zona are cel puțin
    # 30% din înălțimea ferestrei, sau tot conținutul ei
    if m.get("zona_h") is not None and m["zona_depasire"] > 1 and m["zona_h"] < 0.3 * m.get("fer_h", 0):
        return "zona-ingusta"
    return "ok-tabel" if (cutii_tabel or m.get("zona_h") is not None) else "ok"


def alege(doar):
    ecrane = [(n, w_auth.EMAIL_IMPLICIT, f) for n, f in nav_ecrane.ECRANE + nav_ecrane.ECRANE_CAMPANIE]
    ecrane += list(nav_ecrane.ECRANE_CABINET)
    return [e for e in ecrane if not doar or e[0] in doar]


def scan(doar=None, iesire="/tmp/incape_ecran"):
    """Fiecare ecran se deschide O DATĂ, la 1920 × 1080, se măsoară, apoi aceeași pagină se micșorează la 1366 × 768 și se măsoară din nou
    (ordinea lată -> îngustă: treptele `fer-strans` / `fer-rupt` ale navigatorului se adaugă, nu se scot, deci starea de la 1366 e cea a unei
    deschideri directe la 1366)."""
    os.makedirs(iesire, exist_ok=True)
    rez = {}
    ecrane = alege(doar)
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True)
        for nume, cont, nav in ecrane:
            rez[nume] = {}
            w0, h0 = REZOLUTII[0]
            ctx = b.new_context(viewport={"width": w0, "height": h0})
            ctx.add_init_script(w_auth.INIT if cont == w_auth.EMAIL_IMPLICIT else w_auth.init_pentru(cont))
            pg = ctx.new_page()
            try:
                nav(pg)
            except Exception as e:  # noqa: BLE001
                for (w, h) in REZOLUTII:
                    rez[nume]["%dx%d" % (w, h)] = {"verdict": "eroare", "eroare": str(e)[:160]}
                ctx.close()
                print("%-28s EROARE %s" % (nume, str(e)[:100]), flush=True)
                continue
            for (w, h) in REZOLUTII:
                try:
                    pg.set_viewport_size({"width": w, "height": h})
                    pg.wait_for_timeout(700)
                    m = masoara(pg)
                    m["verdict"] = verdict(m)
                    pg.screenshot(path=os.path.join(iesire, "%s_%dx%d.png" % (nume, w, h)))
                except Exception as e:  # noqa: BLE001
                    m = {"verdict": "eroare", "eroare": str(e)[:160]}
                rez[nume]["%dx%d" % (w, h)] = m
            ctx.close()
            print("%-28s %s" % (nume, " | ".join("%s:%s(%s)" % (k, v["verdict"], v.get("depasire", "-")) for k, v in rez[nume].items())), flush=True)
        b.close()
    return rez


def main(argv):
    doar = [x for a in argv if a.startswith("--doar=") for x in a.split("=", 1)[1].split(",")]
    rest = [a for a in argv if not a.startswith("--")]
    rez = scan(doar, rest[0] if rest else "/tmp/incape_ecran")
    rau = [n for n, d in rez.items() if any(v["verdict"] in VERDICTE_RELE for v in d.values())]
    if not doar:
        from acoperire_hash import ui_hash
        with open(ARTEFACT, "w", encoding="utf-8") as f:
            json.dump({"ui_hash": ui_hash(), "rezolutii": ["%dx%d" % r for r in REZOLUTII], "ecrane": rez}, f, ensure_ascii=False, indent=1)
    print("\nferestre care derulează: %d din %d" % (len(rau), len(rez)))
    return 1 if rau else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
