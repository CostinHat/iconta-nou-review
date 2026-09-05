# -*- coding: utf-8 -*-
"""LOTUL 15 — cele CINCI ecrane al caror formular nu se poate atinge pe drumul generic.

Sonda principala (`proba_ecrane_formular.py`) merge pe deschizatoare gasite DUPA NUME si se
opreste la primul buton apasabil. Ecranele de aici cer altceva, si fiecare spune ce:

  · `bonuri` (#432) — singura lui suprafata de intrare e un FISIER. Sonda principala raspunde
    „a cerut un fisier" si anuleaza selectorul; aici i se da un fisier care nu e ce pretinde.
  · `pachete` (#486) — pasul de alegere are un camp de CAUTARE. Umplut cu santinela, filtreaza
    lista de firme pana o goleste, deci «Continuă →» nu se mai aprinde niciodata. Aici firma se
    alege, si proba merge pana la formularul REAL (`#pacm-text`, in modalul de peste fereastra).
  · `admin_raportari` (#467) — formularul de raspuns se randeaza pe o sesizare DESCHISA, iar
    randul ei nu e un „deschizator" dupa nume.
  · `validat` (#498) — singurul camp al ecranului traieste intr-un dialog care se deschide pe un
    element din coada; fara element in coada, ecranul n-are ce randa.
  · `declaratii` (#438 / #477) — vrajitorul are trei pasi, iar pasul 2 GENEREAZA (secunde, nu
    milisecunde). Sonda principala masura ecranul de asteptare.

Toate probele umplu cu ACEEASI santinela ca sonda principala si noteaza raspunsul VERBATIM.
"""
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_RAD = os.path.abspath(os.path.join(_HERE, "..", ".."))
sys.path.insert(0, os.path.join(_RAD, "frontend_test"))
sys.path.insert(0, _HERE)
sys.path.insert(0, _RAD)

from playwright.sync_api import sync_playwright  # noqa: E402
import w_auth  # noqa: E402
import nav_ecrane  # noqa: E402

INVALID_TEXT = "«»@#$%"
INVALID_NUMAR = "-99999999"
JS_TEXT = "() => (document.body.innerText || '').replace(/\\s+/g, ' ').trim()"
OUT = {}


def _dif(a, b):
    i = 0
    while i < min(len(a), len(b)) and a[i] == b[i]:
        i += 1
    return b[max(0, i - 20):i + 220]


def nota(ecran, pas, t0, t1, extra=None):
    """Ce s-a schimbat pe ecran intre inainte si dupa — verbatim, nu rezumat."""
    d = OUT.setdefault(ecran, [])
    d.append({"pas": pas, "text_nou": t0 != t1,
              "delta": ((t1[len(t0):] if t1.startswith(t0) else "")[:260] or _dif(t0, t1)),
              **(extra or {})})
    print("   %-28s text_nou=%-5s %s" % (pas, t0 != t1, (d[-1]["delta"] or "")[:150]))


# ── bonuri: un fisier care nu e ce pretinde ─────────────────────────────────
def proba_bonuri(pg):
    print("── bonuri (#432): fisier invalid")
    w_auth.deschide_firma(pg)
    pg.click("#fa-bonuri", timeout=8000)
    pg.wait_for_timeout(1600)
    t0 = pg.evaluate(JS_TEXT)
    cale = os.path.join("/tmp", "proba_l15_nu_e_poza.png")
    with open(cale, "wb") as f:
        f.write(b"NU SUNT O POZA. Sunt text, cu extensia unei imagini.\n")
    with pg.expect_file_chooser() as fc:
        pg.get_by_text("Adaugă document", exact=False).first.click(timeout=8000)
    fc.value.set_files(cale)
    pg.wait_for_timeout(4000)
    nota("bonuri", "fisier .png care e text", t0, pg.evaluate(JS_TEXT))


# ── pachete: pana la formularul din modal ───────────────────────────────────
def proba_pachete(pg):
    print("── pachete (#486): pana la «Salvează ciornă»")
    nav_ecrane._card(pg, "pachete")
    pg.wait_for_timeout(800)
    # firma se ALEGE (nu se tasteaza) — casuta de cautare e un filtru, nu o intrare de date
    pg.select_option("#pac-firma", index=1, timeout=8000)
    pg.wait_for_timeout(400)
    t0 = pg.evaluate(JS_TEXT)
    pg.fill("#pac-an", INVALID_NUMAR, timeout=6000)
    pg.wait_for_timeout(600)
    nota("pachete", "an = -99999999 (la completare)", t0, pg.evaluate(JS_TEXT))
    t0 = pg.evaluate(JS_TEXT)
    pg.click("#pac-continua", timeout=8000)
    pg.wait_for_timeout(3500)
    nota("pachete", "«Continuă →» cu anul imposibil", t0, pg.evaluate(JS_TEXT))
    # INVALID intai, VALID dupa (PLAN_LUCRU regula 3): cu anul imposibil ecranul se opreste
    # legitim la refuz, deci formularul REAL — modalul poveștii — se atinge pe un an care exista.
    nav_ecrane._card(pg, "pachete")
    pg.wait_for_timeout(800)
    pg.select_option("#pac-firma", index=1, timeout=8000)
    pg.wait_for_timeout(400)
    pg.click("#pac-continua", timeout=8000)
    pg.wait_for_timeout(6000)
    if not pg.query_selector("#pac-deschide"):
        nota("pachete", "pe an valid, pasul 2 tot nu se deschide", "", pg.evaluate(JS_TEXT))
        return
    pg.click("#pac-deschide", timeout=8000)
    pg.wait_for_timeout(1500)
    # Casuta se GOLESTE intai: modalul se deschide cu ciorna salvata anterior, deci o proba
    # „pe gol" care nu goleste masoara o salvare obisnuita si o citeste ca refuz trecut.
    pg.fill("#pacm-text", "", timeout=6000)
    t0 = pg.evaluate(JS_TEXT)
    pg.click("#pacm-salveaza", timeout=8000)       # poveste GOALA
    pg.wait_for_timeout(1800)
    nota("pachete", "«Salvează ciornă» cu povestea GOALA", t0, pg.evaluate(JS_TEXT))
    t0 = pg.evaluate(JS_TEXT)
    pg.fill("#pacm-text", INVALID_TEXT, timeout=6000)
    pg.click("#pacm-salveaza", timeout=8000)
    pg.wait_for_timeout(2500)
    nota("pachete", "«Salvează ciornă» cu textul santinela", t0, pg.evaluate(JS_TEXT))


# ── admin_raportari: raspunsul pe o sesizare deschisa ───────────────────────
def proba_raportari(pg):
    print("── admin_raportari (#467): raspuns pe sesizare")
    nav_ecrane._card(pg, "raportari")
    pg.wait_for_timeout(1200)
    rand = pg.query_selector(".rap-rand, .mig-frand, .pf-frand")
    if not rand:
        nota("admin_raportari", "lista sesizarilor e goala", "", pg.evaluate(JS_TEXT))
        return
    rand.click()
    pg.wait_for_timeout(1800)
    if not pg.query_selector("#rap-text"):
        nota("admin_raportari", "firul nu randeaza formularul de raspuns", "", pg.evaluate(JS_TEXT))
        return
    t0 = pg.evaluate(JS_TEXT)
    pg.fill("#rap-text", "", timeout=6000)
    pg.get_by_text("Trimite", exact=True).first.click(timeout=8000)
    pg.wait_for_timeout(2000)
    nota("admin_raportari", "«Trimite» cu mesaj GOL", t0, pg.evaluate(JS_TEXT))
    t0 = pg.evaluate(JS_TEXT)
    pg.fill("#rap-text", INVALID_TEXT, timeout=6000)
    pg.get_by_text("Trimite", exact=True).first.click(timeout=8000)
    pg.wait_for_timeout(2000)
    nota("admin_raportari", "«Trimite» cu santinela", t0, pg.evaluate(JS_TEXT))


# ── validat: dialogul de motiv ──────────────────────────────────────────────
def proba_validat(pg):
    print("── validat (#498): dialogul de motiv")
    nav_ecrane._card(pg, "validat")
    pg.wait_for_timeout(1500)
    t = pg.evaluate(JS_TEXT)
    b = pg.query_selector(".val-respinge")
    if not b:
        nota("validat", "coada n-are element pe care sa se deschida dialogul", "", t)
        return
    t0 = t
    b.click()
    pg.wait_for_timeout(1500)
    if not pg.query_selector("#dlg-input"):
        nota("validat", "«Respinge» n-a deschis dialogul de motiv", t0, pg.evaluate(JS_TEXT))
        return
    pg.click("#dlg-ok", timeout=6000)          # motiv GOL
    pg.wait_for_timeout(1200)
    nota("validat", "motiv GOL", t0, pg.evaluate(JS_TEXT))
    t0 = pg.evaluate(JS_TEXT)
    pg.fill("#dlg-input", INVALID_TEXT, timeout=6000)
    pg.click("#dlg-ok", timeout=6000)
    pg.wait_for_timeout(2000)
    nota("validat", "motiv = santinela", t0, pg.evaluate(JS_TEXT))


# ── declaratii: pasul 2 al vrajitorului, asteptat cat ii trebuie ────────────
def proba_declaratii(pg):
    print("── declaratii (#438 / #477): pasul 2, asteptat")
    w_auth.deschide_firma(pg)
    pg.click("#fa-declaratii", timeout=8000)
    pg.wait_for_selector("#dec-tip", timeout=15000)
    pg.wait_for_timeout(800)
    optiuni = pg.eval_on_selector(
        "#dec-tip", "s => Array.from(s.options).map(o => o.value).filter(Boolean)")
    tip = "d710" if "d710" in optiuni else (optiuni[0] if optiuni else None)
    if not tip:
        nota("declaratii", "niciun tip de declaratie in selector", "", pg.evaluate(JS_TEXT))
        return
    pg.select_option("#dec-tip", tip, timeout=8000)
    pg.wait_for_timeout(600)
    t0 = pg.evaluate(JS_TEXT)
    pg.click("#dec-continua", timeout=8000)
    pg.wait_for_timeout(12000)                  # pasul 2 GENEREAZA si valideaza (DUK)
    nota("declaratii", "pasul 2 (tip %s), dupa 12 s" % tip, t0, pg.evaluate(JS_TEXT),
         {"campuri": pg.evaluate("() => document.querySelectorAll('input,textarea,select').length")})
    # Suprafata de intrare a vrajitorului NU e pasul 1 (doua selecturi) si nici pasul 2 in sine:
    # e PANOUL MANUAL pe care pasul 2 il randeaza pentru declaratiile cu completari (d710 aici).
    # Se umple si se apasa, ca sa nu ramana un verdict mostenit de la rutele probate in lotul 1.
    camp = pg.query_selector("#d710-obligatie, [id^='d710-']")
    if not camp:
        nota("declaratii", "panoul manual nu randeaza campuri proprii", "", pg.evaluate(JS_TEXT))
        return
    t0 = pg.evaluate(JS_TEXT)
    for el in pg.query_selector_all(".dec-form input, .dec-form select, #dec-d710-form input"):
        try:
            if (el.get_attribute("type") or "text") == "number":
                el.fill(INVALID_NUMAR)
            else:
                el.fill(INVALID_TEXT)
        except Exception:  # noqa: BLE001
            continue
    pg.wait_for_timeout(600)
    nota("declaratii", "panoul manual d710, la completare", t0, pg.evaluate(JS_TEXT))
    t0 = pg.evaluate(JS_TEXT)
    pg.get_by_text("Adaugă", exact=False).last.click(timeout=8000)
    pg.wait_for_timeout(2500)
    nota("declaratii", "«Adaugă» pe panoul manual d710", t0, pg.evaluate(JS_TEXT))


# ── import: meniul, nu pasii lui ────────────────────────────────────────────
def proba_import(pg):
    """`#fa-import` (#442) e un MENIU de pasi, nu un formular — se masoara, nu se presupune.

    Cei zece pasi ai lui au ecrane proprii, iar patru dintre ele sunt in inventarul portii
    (`import_mijloace_fixe`, `vector_fiscal`, `plan_conturi`, `solduri_parteneri`)."""
    print("── fa-import (#442): meniul de import")
    w_auth.deschide_firma(pg)
    pg.click("#fa-import", timeout=8000)
    pg.wait_for_selector(".mig-frand, .stare-goala", timeout=15000)
    pg.wait_for_timeout(1200)
    n = pg.evaluate("() => document.querySelectorAll('input,textarea,select').length")
    pasi = pg.evaluate("() => document.querySelectorAll('.mig-frand').length")
    nota("import", "meniul: intrari_dom=%d, pasi=%d" % (n, pasi), "", pg.evaluate(JS_TEXT),
         {"intrari_dom": n, "pasi": pasi})


PROBE = [("import", proba_import, w_auth.EMAIL_IMPLICIT),
         ("bonuri", proba_bonuri, w_auth.EMAIL_IMPLICIT),
         ("pachete", proba_pachete, w_auth.EMAIL_IMPLICIT),
         ("validat", proba_validat, w_auth.EMAIL_IMPLICIT),
         ("declaratii", proba_declaratii, w_auth.EMAIL_IMPLICIT),
         ("admin_raportari", proba_raportari, nav_ecrane.CONT_ADMIN)]

if __name__ == "__main__":
    cerute = [x for x in sys.argv[1:] if not x.startswith("-")]
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        for nume, fn, cont in PROBE:
            if cerute and nume not in cerute:
                continue
            ctx = b.new_context(viewport={"width": 1250, "height": 1100})
            ctx.add_init_script(w_auth.init_pentru(cont))
            pg = ctx.new_page()
            erori = []
            pg.on("pageerror", lambda e: erori.append(str(e)))
            try:
                fn(pg)
            except Exception as ex:  # noqa: BLE001
                OUT.setdefault(nume, []).append({"eroare": str(ex)[:300]})
                print("   EROARE: %s" % str(ex)[:200])
            if erori:
                OUT.setdefault(nume, []).append({"erori_js": erori[:3]})
                print("   erori JS: %s" % erori[:2])
            ctx.close()
    with open(os.path.join(_HERE, "proba_lot15_adanc.json"), "w", encoding="utf-8") as f:
        json.dump(OUT, f, ensure_ascii=False, indent=1)
    print("\nartefact: proba_lot15_adanc.json")
