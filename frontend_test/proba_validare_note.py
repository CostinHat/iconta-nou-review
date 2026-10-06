# -*- coding: utf-8 -*-
"""PROBA în browser — validarea notelor prin coadă (comanda Costin 06.10.2026, răspunsul la §6 din LOT_06_10, pct.1),
pe baza de TEST (8011).

Asistentul (numai „Poate pregăti”, ca Ana) scrie nota de salarii din statul de plată; statul arată unde e nota; cabinetul
(validatorul) vede contorul „pregătite” / „de validat”, notificarea, nota în „De validat”, conținutul ei, și o validează;
Activitate cabinet arată evenimentele. SCRIE în baza de test (nota + elementul din coadă + notificările) — lanțul care o
rulează le șterge după (`--curata`).

    PYTHONPATH=.:frontend_test ./venv/bin/python frontend_test/proba_validare_note.py --asistent asistent@prisma-cont.test \
        --validator patron@prisma-cont.test --iesire /tmp/.../vn_dupa.json
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from playwright.sync_api import sync_playwright  # noqa: E402

from proba_asistent_drepturi import _pagina, _sesiune  # noqa: E402


def _axe(pg):
    """axe-core cu DETALIUL încălcărilor (regula + primele noduri), nu doar numărul — ca o încălcare să se poată repara."""
    import axe_scan  # noqa: E402
    viol, _t = axe_scan.scaneaza(pg)
    return {"violari": len(viol), "reguli": sorted({v.get("id") for v in viol}),
            "detaliu": [{"regula": v.get("id"), "noduri": v.get("exemple")} for v in viol]}


def _texte(pg, sel):
    return pg.eval_on_selector_all(sel, "els => els.filter(e => e.offsetParent !== null).map(e => e.innerText.trim()).filter(Boolean)")


def _desktop(pg, baza):
    pg.goto(baza + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".asi-arbore, .cab-grila", timeout=20000)
    pg.wait_for_timeout(800)


def _stat(pg, baza, firma, pasi_inapoi):
    _desktop(pg, baza)
    pg.click(".asi-nod[data-nod='firme']") if pg.query_selector(".asi-nod[data-nod='firme']") else None
    pg.wait_for_selector("#firme-lista .firme-rand, #firme-lista .firme-gol", timeout=15000)
    pg.locator("#firme-lista button.firme-rand", has_text=re.compile(firma)).first.click()
    pg.wait_for_selector("#fa-salariati", timeout=15000)
    pg.click("#fa-salariati")
    pg.wait_for_selector("#sp-contare", timeout=20000)
    for _ in range(pasi_inapoi):
        pg.click("#sp-prev")
        pg.wait_for_selector("#sp-contare", timeout=20000)
        pg.wait_for_timeout(500)
    with pg.expect_response(lambda x: "/salarii-contare/propunere" in x.url, timeout=60000):
        pg.click("#sp-contare")
    pg.wait_for_timeout(600)


def _sinteza_zilei(pg, baza):
    """Fereastra „Sinteza zilei” a cabinetului (cardul `brief`): contoarele „pregatite” / „de validat” / Activitate."""
    _desktop(pg, baza)
    pg.evaluate("""() => { const s = document.querySelector(".cab-card-sinteza[data-cheie='brief']");
                            (s && s.closest('.cab-card') || {click(){}}).click(); }""")
    pg.wait_for_selector(".sa-cifra", timeout=20000)
    pg.wait_for_timeout(700)


def proba(pw, baza, asistent, validator, firma, pasi_inapoi, iesire):
    r = {}
    # ---- 1) asistentul scrie nota de salarii
    b, pg, cereri, erori = _pagina(pw, _sesiune(asistent))
    _stat(pg, baza, firma, pasi_inapoi)
    r["inainte_de_scriere"] = _texte(pg, "#sp-contare-zona p")
    if not pg.query_selector("#sp-contare-scrie"):
        raise SystemExit("luna aleasă are deja nota de salarii — alege alta (--pasi-inapoi)")
    with pg.expect_response(lambda x: re.search(r"/salarii-contare\?", x.url) is not None, timeout=60000) as rr:
        pg.click("#sp-contare-scrie")
    r["scriere_status"] = rr.value.status
    pg.wait_for_selector("#sp-contare-zona .tip-micut, #sp-contare-zona .caseta-atentie", timeout=30000)
    pg.wait_for_timeout(1200)
    r["stat_dupa_scriere"] = _texte(pg, "#sp-contare-zona p")
    pg.screenshot(path=iesire + "_stat_asistent.png", full_page=True)
    r["stat_axe"] = _axe(pg)
    r["cereri_asistent"] = cereri
    r["erori_asistent"] = erori
    b.close()
    # ---- 2) validatorul: contoare, „De validat”, conținutul notei, validarea
    b, pg, cereri, erori = _pagina(pw, _sesiune(validator))
    _sinteza_zilei(pg, baza)
    r["contoare_cabinet"] = _texte(pg, ".sa-cifra")
    pg.screenshot(path=iesire + "_sinteza.png", full_page=True)
    pg.click(".sa-cifra[data-ecran='validat']")
    pg.wait_for_selector("#val-note .val-card, #val-deValidat .stare-goala, #val-deValidat .val-card, #val-deDepus .val-card", timeout=20000)
    pg.wait_for_timeout(700)
    r["note_de_validat"] = _texte(pg, "#val-note .val-card")
    pg.screenshot(path=iesire + "_de_validat.png", full_page=True)
    r["de_validat_axe"] = _axe(pg)
    card = pg.locator("#val-note .val-card", has_text=re.compile("Stat de plată|stat de plat", re.I)).first
    r["nota_in_coada"] = card.count() > 0
    if not r["nota_in_coada"]:
        # forma de dinainte: nota pregătită de asistent nu ajunge la cabinet — se consemnează, proba se oprește aici
        r["cereri_validator"] = cereri
        r["erori_validator"] = erori
        b.close()
        return r
    card.locator(".val-vezi-nota").click()
    pg.wait_for_selector(".fd-tabel", timeout=15000)
    pg.wait_for_timeout(500)
    r["continut_nota"] = _texte(pg, ".fd-tabel tbody tr")[:12]
    pg.screenshot(path=iesire + "_nota.png", full_page=True)
    r["nota_axe"] = _axe(pg)
    # lista se redeschide de la zero (fereastra „Vezi nota” stă peste ea)
    _sinteza_zilei(pg, baza)
    pg.click(".sa-cifra[data-ecran='validat']")
    pg.wait_for_selector("#val-note .val-card", timeout=20000)
    pg.wait_for_timeout(500)
    card = pg.locator("#val-note .val-card", has_text=re.compile("Stat de plată|stat de plat", re.I)).first
    with pg.expect_response(lambda x: re.search(r"/coada/\d+/aproba", x.url) is not None, timeout=60000) as ra:
        card.locator(".val-aproba").click()
        if pg.query_selector("#caseta-atentie-activa #ca-ok"):
            pg.click("#caseta-atentie-activa #ca-ok")
    r["aprobare_status"] = ra.value.status
    pg.wait_for_timeout(1500)
    r["note_dupa_validare"] = _texte(pg, "#val-note .val-card")
    _sinteza_zilei(pg, baza)
    r["contoare_dupa"] = _texte(pg, ".sa-cifra")
    pg.click(".sa-cifra[data-ecran='activitate']")
    pg.wait_for_selector(".ac-tabel", timeout=20000)
    pg.wait_for_timeout(700)
    r["activitate"] = _texte(pg, ".ac-rand")[:6]
    pg.screenshot(path=iesire + "_activitate.png", full_page=True)
    r["activitate_axe"] = _axe(pg)
    r["cereri_validator"] = cereri
    r["erori_validator"] = erori
    b.close()
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baza", default=os.environ.get("PROBA_BAZA", "http://127.0.0.1:8011"))
    ap.add_argument("--asistent", required=True)
    ap.add_argument("--validator", required=True)
    ap.add_argument("--firma", default="Panificatie")
    ap.add_argument("--pasi-inapoi", type=int, default=7)
    ap.add_argument("--iesire", required=True)
    a = ap.parse_args()
    with sync_playwright() as pw:
        r = proba(pw, a.baza, a.asistent, a.validator, a.firma, a.pasi_inapoi, a.iesire.replace(".json", ""))
    json.dump(r, open(a.iesire, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    for k in ("stat_dupa_scriere", "nota_in_coada", "contoare_cabinet", "note_de_validat", "continut_nota", "aprobare_status",
              "note_dupa_validare", "contoare_dupa", "activitate"):
        print(k, json.dumps(r.get(k), ensure_ascii=False)[:700])


if __name__ == "__main__":
    main()
