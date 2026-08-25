# -*- coding: utf-8 -*-
"""UNEALTA 3 — comparatia de capturi intre versiuni (echivalent toHaveScreenshot).
API-ul Python sync n-are toHaveScreenshot (e fixture pytest-playwright JS); il implementam
cu PIL: baseline PNG per ecran + diff pixel-cu-pixel la rularea urmatoare.

Doua moduri:
  (implicit) STABILESTE: capteaza fiecare ecran de DOUA ori in aceeasi rulare ->
             self-diff = masura de FLAKINESS (cat de determinist e ecranul). Salveaza
             baseline/<ecran>.png. Daca self-diff e mare, baseline-ul ar fi zgomotos ->
             se propune prag / mascare, nu se impune tacut.
  ATENTIE, cele doua moduri raspund la INTREBARI DIFERITE si se confunda usor:
    implicit -> „e ecranul STABIL de la o captura la alta?" (zgomot de randare)
    --compare -> „s-a SCHIMBAT ecranul fata de referinta?" (regresie vizuala)
  Un „STABIL" din modul implicit NU spune nimic despre schimbare. Baseline-urile NU sunt
  urmarite in git (decizia lui Costin, 26.08.2026): sunt referinte locale, regenerabile.

  --compare  COMPARA: captura curenta vs baseline/<ecran>.png -> pixeli diferiti + %,
             salveaza diff_<ecran>.png la depasire. Asa iese o schimbare vizuala
             neintentionata singura la tura urmatoare.

Determinism: viewport fix + animatii/tranzitii oprite (add_style_tag). Toleranta pe canal
= 16 (ignora antialiasing). NU repara nimic.
"""
import os, sys, json
from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright
from w_auth import INIT
from nav_ecrane import ECRANE

HERE = os.path.dirname(os.path.abspath(__file__))
BDIR = os.path.join(HERE, "baseline")
os.makedirs(BDIR, exist_ok=True)
VIEWPORT = {"width": 1280, "height": 1800}
STOP_ANIM = ("*,*::before,*::after{animation:none!important;transition:none!important;"
             "caret-color:transparent!important}")
TOL = 16  # toleranta per canal (antialiasing)


def difera(a_path, b_path):
    """Returneaza (pixeli_diferiti, total, procent, dim_egala)."""
    a = Image.open(a_path).convert("RGB")
    b = Image.open(b_path).convert("RGB")
    if a.size != b.size:
        return (max(a.size[0]*a.size[1], b.size[0]*b.size[1]), a.size[0]*a.size[1], 100.0, False)
    diff = ImageChops.difference(a, b)
    # binarizeaza pe toleranta: orice canal peste TOL = pixel diferit; numara prin histograma (rapid)
    gray = diff.convert("L").point(lambda p: 255 if p > TOL else 0)
    bbox_pixels = gray.histogram()[255]
    total = a.size[0] * a.size[1]
    return (bbox_pixels, total, 100.0 * bbox_pixels / total, True)


def capteaza(pg, nav, dest):
    nav(pg)
    pg.add_style_tag(content=STOP_ANIM)
    pg.wait_for_timeout(400)
    pg.screenshot(path=dest, full_page=True)


def main():
    compara = "--compare" in sys.argv
    rez = []
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True)
        for nume, nav in ECRANE:
            r = {"ecran": nume}
            try:
                base = os.path.join(BDIR, nume + ".png")
                if compara:
                    cur = os.path.join(HERE, "cur_%s.png" % nume)
                    ctx = b.new_context(viewport=VIEWPORT); ctx.add_init_script(INIT)
                    capteaza(ctx.new_page(), nav, cur); ctx.close()
                    if not os.path.exists(base):
                        r["stare"] = "FARA-BASELINE"
                    else:
                        d, tot, pct, egal = difera(base, cur)
                        r.update(pixeli_dif=d, procent=round(pct, 4), dim_egala=egal)
                        r["stare"] = "SCHIMBAT" if pct > 0.05 else "identic"
                        if pct > 0.05:
                            Image.open(cur)  # (loc pentru diff vizual daca se doreste)
                else:
                    # STABILESTE + self-diff (doua capturi)
                    c1 = os.path.join(HERE, "b1_%s.png" % nume)
                    c2 = os.path.join(HERE, "b2_%s.png" % nume)
                    for dest in (c1, c2):
                        ctx = b.new_context(viewport=VIEWPORT); ctx.add_init_script(INIT)
                        capteaza(ctx.new_page(), nav, dest); ctx.close()
                    d, tot, pct, egal = difera(c1, c2)
                    r.update(self_pixeli_dif=d, self_procent=round(pct, 4), dim_egala=egal)
                    r["flakiness"] = ("STABIL" if pct < 0.02 else
                                      "USOR" if pct < 0.2 else "ZGOMOTOS")
                    # baseline = prima captura. Se SPUNE daca exista una inainte: „STABIL"
                    # singur se citeste ca „am comparat cu referinta si nu s-a schimbat", desi e
                    # self-diff intre doua capturi din aceeasi rulare. (Costin, 26.08.2026: „azi
                    # absenta ar da vid, iar vidul arata ca stabilitate".)
                    r["referinta"] = "RESCRISA" if os.path.exists(base) else "NOUA"
                    Image.open(c1).save(base)
                    r["baseline"] = os.path.relpath(base, HERE)
                    sz = Image.open(base).size
                    r["dim"] = "%dx%d" % sz
                r["ok"] = True
            except Exception as e:
                r["ok"] = False; r["error"] = str(e).splitlines()[0][:140]
            rez.append(r)
        b.close()

    titlu = "COMPARA vs baseline" if compara else "STABILESTE baseline + self-diff (flakiness)"
    linii = ["=== RAPORT baseline capturi — %s ===" % titlu, ""]
    if compara:
        linii.append("%-22s %10s %9s %10s" % ("ECRAN", "STARE", "PIXELI", "PROCENT"))
        for r in rez:
            if not r.get("ok"): linii.append("%-22s EROARE %s" % (r["ecran"], r.get("error"))); continue
            linii.append("%-22s %10s %9s %10s" % (
                r["ecran"], r.get("stare", "?"), r.get("pixeli_dif", "-"),
                ("%.4f%%" % r["procent"]) if "procent" in r else "-"))
    else:
        linii.append("ATENTIE: FLAKINESS e self-diff intre DOUA capturi din ACEEASI rulare —")
        linii.append("NU e o comparatie cu referinta de dinainte. Pentru aia: --compare.")
        linii.append("")
        linii.append("%-22s %10s %10s %11s %9s %10s"
                     % ("ECRAN", "DIM", "REFERINTA", "FLAKINESS", "PIXELI", "PROCENT"))
        for r in rez:
            if not r.get("ok"): linii.append("%-22s EROARE %s" % (r["ecran"], r.get("error"))); continue
            linii.append("%-22s %10s %10s %11s %9d %9.4f%%" % (
                r["ecran"], r.get("dim", "?"), r.get("referinta", "?"), r.get("flakiness", "?"),
                r.get("self_pixeli_dif", 0), r.get("self_procent", 0.0)))
    txt = "\n".join(linii)
    open(os.path.join(HERE, "raport_baseline.txt"), "w", encoding="utf-8").write(txt)
    print(txt)
    open(os.path.join(HERE, "raport_baseline.json"), "w", encoding="utf-8").write(
        json.dumps(rez, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
