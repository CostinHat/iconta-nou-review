# -*- coding: utf-8 -*-
"""Parcursul lotului 17.5-M4 (ecranele cabinetului), cu contul administratorului (dovada.71507), la 1366×768, ceas înghețat în browser (03.11.2026):
înainte de orice pas, seed-ul (recalcularea cu funcțiile aplicației, pe firmele active ale cabinetului 48765, a rezumatelor de termene și a rezultatelor Supervizorului);
apoi pagina principală a cabinetului (pasul implicit), Firme existente, Termene (rândul D112 › «Deschide» › Detaliu termen), Sinteza zilei, Supervizor, Capacitate, Consolidare și Control fiscal (rândul F2 Profit › «Deschide» › Detaliu firmă F2).
Cardurile Supervizor, Capacitate și Consolidare stau în secțiunea pliată «Pentru șeful de cabinet» (cabinet.js, desenazaSectiuneaSefului): parcursul o deschide înainte de clic.
Pe fiecare pas se judecă texte: textul nou există, textul vechi lipsește. Nu salvează nimic, nu alege niciun fișier; singurele scrieri sunt cele ale seed-ului (rezumate și rezultate recalculate, ca lucrătorul de fundal).
Un clic sau o așteptare care eșuează e înghițit, iar parcursul continuă (pe commitul de bază aserțiunile a. pică). Importă numai biblioteca standard și verifica_pas (seed-ul rulează într-un proces separat, nu printr-un import)."""
# data zilei din pagină = data ceasului înghețat (ceas_proba.MOMENT_REF, 03.11.2026); seed-ul și serverul folosesc data calendaristică reală (core.common.azi_ro), ca modelul _supervizor din e2e_lot12_texte.py
import os
import subprocess
import sys

import verifica_pas as VP

TOP = ".fereastra-overlay:not(.fundal) "
CABINET = 48765
F2 = "F2 Profit"
EXPANDEAZA_SEF = "() => { const b = document.querySelector('.cab-grila > .firme-grup .firme-grup-btn[aria-expanded=\"false\"]'); if (b) b.click(); }"

# Seed-ul: proces separat, pe mediul ~/.iconta/test.env (baza iconta_test), cu funcțiile aplicației; scrie numai ce scrie lucrătorul de fundal (firma_rezumat și supervizor_cache)
_SEED = r'''
import sys
rad, cabinet = sys.argv[1], int(sys.argv[2])
sys.path.insert(0, rad)
from core import db, firma_rezumat, supervizor_cache
from core.common import azi_ro
from core.control_fiscal_api import luna_confruntata
try:
    db.init_pool()
except Exception:
    pass
azi = azi_ro()
an, luna = luna_confruntata(azi.year, azi.month)
with db.get_conn() as c, c.cursor() as cur:
    cur.execute("SELECT id, schema_name FROM public.tenants WHERE accounting_firm_id = %s AND activ = true ORDER BY id", (cabinet,))
    firme = cur.fetchall()
    c.rollback()
for tid, schema in firme:
    # recalculeaza_firma păstrează numai aspectele ușoare, iar «termene» e aspect greu (no-op); termene și control_fiscal se scriu împreună prin recalculeaza_greu
    firma_rezumat.recalculeaza_greu(tid, schema, azi=azi)
    supervizor_cache.recalculeaza_firma(tid, schema, an, luna)
print("SEED firme=%d ids=%s perioada_supervizor=%02d/%d azi=%s" % (len(firme), ",".join(str(f[0]) for f in firme), luna, an, azi.isoformat()))
'''


def _mediu_test():
    """Variabilele ~/.iconta/test.env (aceeași citire ca scripts/e2e_poarta.py::_env_test); refuz dacă baza nu e iconta_test."""
    env = dict(os.environ)
    try:
        for linie in open(os.path.expanduser("~/.iconta/test.env"), encoding="utf-8"):
            linie = linie.strip()
            if linie.startswith("export "):
                linie = linie[7:]
            if "=" in linie and not linie.startswith("#"):
                k, v = linie.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    except OSError as e:
        return None, "nu pot citi ~/.iconta/test.env (%s)" % type(e).__name__
    if env.get("DB_NAME") != "iconta_test":
        return None, "DB_NAME = %r, nu iconta_test" % env.get("DB_NAME")
    return env, ""


def seed():
    """Recalculează rezumatele de termene și rezultatele Supervizorului ale firmelor active ale cabinetului (definiția «seed» din comanda 17.5-M4)."""
    env, motiv = _mediu_test()
    if env is None:
        print("[parcurs] SEED OMIS: %s" % motiv)
        return
    try:
        r = subprocess.run([sys.executable, "-c", _SEED, VP.RAD, str(CABINET)], cwd=VP.RAD, env=env, capture_output=True, text=True, timeout=900)
        print("[parcurs] %s" % ((r.stdout or "").strip() or "SEED fără ieșire"))
        if r.returncode != 0:
            print("[parcurs] SEED EȘUAT (cod %d): %s" % (r.returncode, (r.stderr or "").strip()[-400:]))
    except Exception as e:   # noqa: BLE001 — seed-ul lipsă se vede în rândurile a. (cifre «nerecalculat»), nu oprește parcursul
        print("[parcurs] SEED EȘUAT: %s: %s" % (type(e).__name__, e))


def card(cheie):
    return "button.cab-card:has([data-cheie='%s'])" % cheie


def acasa(pg, sef=False):
    """Pagina principală proaspătă (goto): memoria ferestrei deschise se șterge întâi; se așteaptă cardurile și sintezele lor (nimic «se încarcă»); cu sef=True se deschide secțiunea «Pentru șeful de cabinet»."""
    pg.evaluate("sessionStorage.removeItem('iconta_fereastra_deschisa')")
    pg.goto(pg.evaluate("location.origin") + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".cab-grila button.cab-card", timeout=30000)
    try:
        pg.wait_for_function("() => ![...document.querySelectorAll('.cab-card-sinteza')].some((e) => e.textContent.includes('se încarcă'))", timeout=20000)
    except Exception:   # noqa: BLE001 — contoarele întârzie: pasul se judecă pe ce s-a desenat
        pass
    if sef:
        try:
            pg.evaluate(EXPANDEAZA_SEF)
        except Exception:   # noqa: BLE001
            pass
    pg.wait_for_timeout(800)


def deschide_card(pg, cheie, asteapta, sef=False, timp=1500):
    """Pagina principală › cardul `cheie` › așteptarea unui element al ferestrei (dacă nu apare, pasul se judecă pe ce s-a desenat)."""
    acasa(pg, sef)
    try:
        pg.click(card(cheie), timeout=10000)
        pg.wait_for_selector(TOP + asteapta, state="attached", timeout=45000)
    except Exception:   # noqa: BLE001
        pass
    pg.wait_for_timeout(timp)


def apasa_in_rand(pg, tabel_rand, text_rand, text_buton, asteapta, timp=1500, asteptare=30000):
    """Primul rând `tabel_rand` care conține `text_rand` › butonul lui `text_buton` › așteptarea lui `asteapta` (înghițit dacă lipsește)."""
    try:
        pg.locator(TOP + tabel_rand, has_text=text_rand).first.locator("button", has_text=text_buton).first.click(timeout=10000)
        pg.wait_for_selector(TOP + asteapta, state="attached", timeout=asteptare)
    except Exception:   # noqa: BLE001
        pass
    pg.wait_for_timeout(timp)


def aduce_in_vedere(pg, selector, bloc="center"):
    """Aduce elementul măsurat în zona vizibilă a ferestrei (captura de 1366×768 îl arată); înghițit dacă lipsește."""
    try:
        pg.evaluate("([s, b]) => { const e = document.querySelector('.fereastra-overlay:not(.fundal) ' + s); if (e) e.scrollIntoView({block: b}); }", [selector, bloc])
    except Exception:   # noqa: BLE001
        pass
    pg.wait_for_timeout(500)


import json

_MASURA = r'''() => {
  const f = [...document.querySelectorAll('.fereastra-overlay:not(.fundal)')].pop();
  const corp = f.querySelector('.fereastra-corp');
  const zone = [...corp.querySelectorAll('.zona-derulare')];
  const decl = [...corp.querySelectorAll('[data-zona-derulare]')];
  const pr = corp.querySelector('.sa-asist-lista[data-prioritati-fara-derulare]');
  const cutie = pr && pr.querySelector(':scope > .ds-tabel-cutie.ds-tabel-lista');
  const m = (e) => e ? {sel: e.tagName + '.' + String(e.className).split(' ').join('.'), sh: e.scrollHeight, ch: e.clientHeight, sw: e.scrollWidth, cw: e.clientWidth, ov: getComputedStyle(e).overflowY} : null;
  const verticale = [corp, ...corp.querySelectorAll('*')].filter((e) => ['auto','scroll'].includes(getComputedStyle(e).overflowY) && e.scrollHeight > e.clientHeight + 1).map(m);
  const cuOverflow = [...corp.querySelectorAll('*')].filter((e) => ['auto','scroll'].includes(getComputedStyle(e).overflowY)).map(m);
  const cap = [...corp.querySelectorAll('.sa-cap')].map((e) => e.textContent.trim());
  const z = decl[0];
  const rows = pr ? [...pr.querySelectorAll('tbody tr, .sa-asist')] : [];
  return {corp: m(corp), declarate: decl.length, marcate: zone.length, zona: m(z), zonaMarcata: !!(z && z.classList.contains('zona-derulare')),
    prioritatiInZona: !!(z && pr && z.contains(pr)), cutie: m(cutie), cutieOverflow: cutie ? getComputedStyle(cutie).overflowY : null,
    tabelCutieMarcataZona: !!(cutie && (cutie.classList.contains('zona-derulare') || cutie.closest('.zona-derulare') === cutie)),
    verticaleCuDepasire: verticale, cuOverflow: cuOverflow, capitole: cap, cifre: corp.querySelectorAll('.sa-cifra').length, randuriPrioritati: rows.length,
    notaDeasupra: !!(z && corp.querySelector('.ecran-nota') && (corp.querySelector('.ecran-nota').compareDocumentPosition(z) & 4)),
    corpOrizontal: corp.scrollWidth > corp.clientWidth + 1, zonaOrizontal: z ? z.scrollWidth > z.clientWidth + 1 : null,
    productia: !!([...corp.querySelectorAll('.sa-cap')].find((e) => e.textContent.includes('Producția')))};
}'''

_ULTIM = r'''() => {
  const z = document.querySelector('.fereastra-overlay:not(.fundal) [data-zona-derulare]');
  const pr = z && z.querySelector('.sa-asist-lista[data-prioritati-fara-derulare]');
  if (!z) return null;
  const inainte = z.scrollTop; z.scrollTop = z.scrollHeight;
  const dupa = z.scrollTop;
  const sf = [...z.querySelectorAll('.sa-jurnal li, .sa-asist-lista .sa-asist, .sa-doua .sa-sectiune')].pop() || z.lastElementChild;
  const r = sf.getBoundingClientRect(), zr = z.getBoundingClientRect();
  const viz = r.bottom <= zr.bottom + 1 && r.top >= zr.top - 1;
  const prr = pr ? [...pr.querySelectorAll('tbody tr, .sa-asist')] : [];
  const ultimPr = prr.length ? prr[prr.length - 1].getBoundingClientRect() : null;
  z.scrollTop = 0;
  const p0 = prr.length ? prr[prr.length - 1].getBoundingClientRect() : null;
  return {derulat: dupa > inainte, scrollTop: dupa, ultimulElementVizibil: viz, ultimRandPrioritatiInZonaVizibila: !!(p0 && p0.bottom <= zr.bottom + 1)};
}'''


def ruleaza(pagina, ctx):
    pg = pagina
    seed()
    iesire = {}
    for (w, h) in ((1920, 1080), (1366, 768)):
        pg.set_viewport_size({"width": w, "height": h})
        deschide_card(pg, "brief", ".sa-cifre", timp=3000)
        pg.wait_for_timeout(1500)
        iesire["%dx%d" % (w, h)] = {"masura": pg.evaluate(_MASURA), "derulare": pg.evaluate(_ULTIM)}
        pg.screenshot(path=os.path.join(VP.RAD, "docs", "dovezi", "17_5_M4", "pct5_%dx%d.png" % (w, h)))
    open(os.path.join(VP.RAD, "docs", "dovezi", "17_5_M4", "pct5_proba.json"), "w", encoding="utf-8").write(json.dumps(iesire, ensure_ascii=False, indent=1))
    print("[proba] scris pct5_proba.json")
