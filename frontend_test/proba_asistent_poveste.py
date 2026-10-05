# -*- coding: utf-8 -*-
"""PROBA în browser — testarea ca asistent (2), comanda Costin 05.10.2026: povestea lunii, drepturile arătate, Asistenți,
iconițe, Pachete.

Rulează pe baza de TEST (8011). Bifele asistentului le pune lanțul care o rulează; proba doar citește ce vede.
Scrie în bază DOAR la generarea cu AI? Nu: `POST /genereaza` întoarce textul fără să-l salveze. Proba nu apasă „Salvează”,
„Aprobă” sau „Trimite” — verifică doar dacă se văd și ce spun.

    PYTHONPATH=.:frontend_test ./venv/bin/python frontend_test/proba_asistent_poveste.py --faza dupa --drepturi pregatire \
        --asistent asistent@prisma-cont.test --admin patron@prisma-cont.test --iesire /tmp/.../dupa_pregatire.json
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from playwright.sync_api import sync_playwright  # noqa: E402

from proba_asistent_drepturi import _axe, _pagina, _sesiune  # noqa: E402

# sinonimele pe care comanda le numește greșite (venituri ≠ încasări ≠ câștig)
_TERMENI_GRESITI = re.compile(r"(?i)încas|incas|câștig|castig|bani intrați|cifr[ăa] de afaceri")


def _viz(pg, sel):
    return pg.eval_on_selector_all(sel, "els => els.filter(e => e.offsetParent !== null).length")


def _texte(pg, sel):
    return pg.eval_on_selector_all(sel, "els => els.filter(e => e.offsetParent !== null).map(e => e.innerText.trim()).filter(Boolean)")


def _desktop(pg, baza):
    pg.goto(baza + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".asi-arbore, .cab-grila", timeout=20000)
    pg.wait_for_timeout(700)


def proba_asistent(pw, baza, asistent, firma, drepturi, iesire, cu_ai, an=None, luna=None):
    r = {"drepturi": drepturi}
    b, pg, cereri, erori = _pagina(pw, _sesiune(asistent))
    _desktop(pg, baza)
    # pct.5: iconița „Raportează” — în meniul din stânga și pe card
    r["iconita_raporteaza"] = {
        "meniu_stanga_path": pg.eval_on_selector(".asi-nod[data-nod='raport'] svg", "s => s.innerHTML.length") if pg.query_selector(".asi-nod[data-nod='raport']") else None,
        "card_path": pg.evaluate("""() => { const s = document.querySelector(".cab-card-sinteza[data-cheie='raport']");
            const c = s && s.closest('.cab-card'); const g = c && c.querySelector('svg'); return g ? g.innerHTML.length : null; }"""),
    }
    pg.click(".asi-nod[data-nod='pachete']")
    pg.wait_for_selector("#pac-firma", timeout=15000)
    pg.wait_for_timeout(500)
    # pct.6: câte controale pentru alegerea firmei
    r["alegere_firma"] = {"camp_cautare": _viz(pg, "#pac-cauta"), "lista": _viz(pg, "#pac-firma"),
                          "controale_firma": pg.eval_on_selector_all(".dec-form label.camp:first-child input, .dec-form label.camp:first-child select",
                                                                     "els => els.filter(e => e.offsetParent !== null).length")}
    pg.screenshot(path=iesire + "_pachete_alegere_%s.png" % drepturi, full_page=True)
    r["axe_alegere"] = _axe(pg)
    val = pg.evaluate("(f) => { const o = [...document.querySelectorAll('#pac-firma option')].find(x => x.textContent.includes(f)); return o ? o.value : null; }", firma)
    pg.select_option("#pac-firma", value=val)
    if an:
        pg.fill("#pac-an", str(an)); pg.dispatch_event("#pac-an", "change")
    if luna:
        pg.select_option("#pac-luna", value=str(luna))
    pg.click("#pac-continua")
    pg.wait_for_selector("#pac-deschide", timeout=20000)
    pg.wait_for_timeout(500)
    r["rezumat"] = _texte(pg, ".pac-rez-rand")
    pg.click("#pac-deschide")
    pg.wait_for_selector(".pacm", timeout=10000)
    pg.wait_for_timeout(900)
    # pct.2 + 3: ce butoane se văd și ce explică fereastra
    r["fereastra"] = {"genereaza": _viz(pg, "#pacm-gen"), "salveaza": _viz(pg, "#pacm-salveaza"),
                      "aproba": _viz(pg, "#pacm-aproba"), "trimite": _viz(pg, "#pacm-trimite"),
                      "trimite_activ": pg.eval_on_selector("#pacm-trimite", "e => !e.disabled && e.offsetParent !== null"),
                      "motiv_drepturi": _texte(pg, ".pacm .drept-motiv"),
                      "texte_stare": _texte(pg, ".pacm .pacm-stare, .pacm .pacm-motiv-trimite")}
    # pct.7: „Vezi ca email” cu povestea GOALĂ
    pg.fill("#pacm-text", "")
    pg.dispatch_event("#pacm-text", "input")
    pg.wait_for_timeout(300)
    r["goala"] = {"trimite_activ": pg.eval_on_selector("#pacm-trimite", "e => !e.disabled && e.offsetParent !== null"),
                  "motiv_trimite": _texte(pg, ".pacm .pacm-motiv-trimite")}
    pg.click("#pacm-vezi")
    pg.wait_for_timeout(2500)
    txt = pg.eval_on_selector("#pacm-preview", "e => e.innerText")
    r["goala"]["previzualizare"] = txt[:600]
    r["goala"]["previzualizare_are_cifre"] = bool(re.search(r"(?i)venituri", txt))
    pg.screenshot(path=iesire + "_vezi_email_gol_%s.png" % drepturi, full_page=True)
    r["goala"]["axe"] = _axe(pg)
    pg.click("#pacm-vezi")
    pg.wait_for_timeout(300)
    # pct.1: termenii textului generat (doar unde generarea e permisă)
    if cu_ai and r["fereastra"]["genereaza"]:
        with pg.expect_response(lambda x: "/genereaza" in x.url, timeout=90000) as rr:
            pg.click("#pacm-gen")
        d = rr.value.json()
        text = d.get("text") or ""
        sume = sorted(set(re.findall(r"\d[\d.\s]*(?:,\d+)?(?=\s*(?:de\s+)?lei)", text)))
        r["ai"] = {"ok": d.get("ok"), "cod": d.get("cod"), "text": text, "termeni_gresiti": sorted(set(m.group(0).lower() for m in _TERMENI_GRESITI.finditer(text))),
                   "sume_in_text": [s.strip() for s in sume], "abateri_server": d.get("abateri"),
                   "rezumat_server": {k: (d.get("rezumat") or {}).get(k) for k in ("venituri", "cheltuieli", "rezultat", "tip")}}
        pg.wait_for_timeout(800)
        r["ai"]["avertisment_ecran"] = _texte(pg, ".pacm .pacm-abateri")
    pg.click("#pacm-x")
    pg.wait_for_timeout(300)
    # pct.3 pe ALT ecran cu acțiuni ascunse: registrul jurnal al firmei
    _desktop(pg, baza)
    pg.click(".asi-nod[data-nod='firme']")
    pg.wait_for_selector("#firme-lista .firme-rand, #firme-lista .firme-gol", timeout=15000)
    pg.wait_for_timeout(500)
    pg.locator("#firme-lista button.firme-rand", has_text=re.compile(firma)).first.click()
    pg.wait_for_selector("#fa-jurnal", timeout=15000)
    pg.click("#fa-jurnal")
    pg.wait_for_selector("#j-prev", timeout=15000)
    pg.wait_for_timeout(1200)
    r["jurnal"] = {"nota_noua": _viz(pg, "#j-nota-noua"), "motiv_drepturi": _texte(pg, ".fereastra-corp .drept-motiv")}
    pg.screenshot(path=iesire + "_jurnal_%s.png" % drepturi, full_page=True)
    r["jurnal"]["axe"] = _axe(pg)
    r["cereri_scriere"] = cereri
    r["erori_consola"] = erori
    b.close()
    return r


def proba_admin(pw, baza, admin, iesire):
    """pct.4: rândul administratorului din Asistenți și editarea lui."""
    r = {}
    b, pg, cereri, erori = _pagina(pw, _sesiune(admin))
    _desktop(pg, baza)
    pg.evaluate("""() => { const s = document.querySelector(".cab-card-sinteza[data-cheie='asistenti']");
                            (s && s.closest('.cab-card') || {click(){}}).click(); }""")
    pg.wait_for_selector(".val-card", timeout=15000)
    pg.wait_for_timeout(700)
    r["rand_admin"] = pg.evaluate("""() => { const c = [...document.querySelectorAll('.val-card')].find(x => /administrator/.test(x.innerText));
        return c ? {rol: c.querySelector('.asi-rol').innerText, drepturi: c.querySelector('.asi-perms').innerText} : null; }""")
    pg.screenshot(path=iesire + "_asistenti_admin.png", full_page=True)
    r["axe_lista"] = _axe(pg)
    pg.evaluate("""() => { const c = [...document.querySelectorAll('.val-card')].find(x => /administrator/.test(x.innerText));
        c.querySelector('[data-act="edit"]').click(); }""")
    pg.wait_for_selector("#asi-salveaza, .asi-sectiune-titlu", timeout=15000)
    pg.wait_for_timeout(700)
    r["editare_admin"] = {"bife_drepturi": pg.eval_on_selector_all("[data-perm]", "e => e.filter(x => x.offsetParent !== null).length"),
                          "text": pg.eval_on_selector(".fereastra-corp", "e => e.innerText")[:400]}
    pg.screenshot(path=iesire + "_asistenti_admin_editare.png", full_page=True)
    r["axe_editare"] = _axe(pg)
    r["cereri_scriere"] = cereri
    r["erori_consola"] = erori
    b.close()
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baza", default=os.environ.get("PROBA_BAZA", "http://127.0.0.1:8011"))
    ap.add_argument("--asistent", required=True)
    ap.add_argument("--admin", required=True)
    ap.add_argument("--firma", default="Coafor")
    ap.add_argument("--an", type=int, default=2026)
    ap.add_argument("--luna", type=int, default=8)
    ap.add_argument("--drepturi", choices=("pregatire", "fara", "validare"), required=True)
    ap.add_argument("--cu-ai", action="store_true")
    ap.add_argument("--iesire", required=True)
    a = ap.parse_args()
    baza_iesire = a.iesire[:-5] if a.iesire.endswith(".json") else a.iesire
    with sync_playwright() as pw:
        r = {"asistent": proba_asistent(pw, a.baza, a.asistent, a.firma, a.drepturi, baza_iesire, a.cu_ai, a.an, a.luna)}
        if a.drepturi == "pregatire":
            r["admin"] = proba_admin(pw, a.baza, a.admin, baza_iesire)
    json.dump(r, open(a.iesire, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(r, ensure_ascii=False, indent=1)[:4000])


if __name__ == "__main__":
    main()
