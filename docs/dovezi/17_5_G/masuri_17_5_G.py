# -*- coding: utf-8 -*-
"""Măsurile lotului 17.5-G pe 8019 (pct.4.2 și 4.4): aceeași sesiune (dovada.71507), același ceas (MOMENT_REF) și aceeași firmă (F1 Comert Stoc)
ca testul arhitectului, a cărui logică de deschidere o refolosește pe nume, fără să-l copieze.
Uz: JWT_SECRET=... python docs/dovezi/17_5_G/masuri_17_5_G.py <1366|603> <fișier de ieșire>
  1366: textul de îndrumare față de câmp pe cele patru ferestre + rânduri „Conturi” goale + bara de jos cu nimic bifat + rândul F1 din Control fiscal
   603: textul de îndrumare față de câmp pe cele patru ferestre (viewport 603×590)"""
import importlib.util
import os
import sys

RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(RAD, "scripts"))
sys.path.insert(0, RAD)


def _modul_test():
    # testul importă „conftest” din directorul e2e (nu cel din rădăcină): îl încărc întâi și îl pun în sys.modules
    # mediul de test (baza iconta_test) îl pune conftest-ul din rădăcină la import, ca sub pytest
    rc = importlib.util.spec_from_file_location("conftest_radacina", os.path.join(RAD, "conftest.py"))
    importlib.util.module_from_spec(rc)
    rc.loader.exec_module(importlib.util.module_from_spec(rc))
    sys.path.insert(0, os.path.join(RAD, "frontend_test", "e2e"))   # „curatenie” din e2e, nu cel din scripts/
    cf = importlib.util.spec_from_file_location("conftest", os.path.join(RAD, "frontend_test", "e2e", "conftest.py"))
    mc = importlib.util.module_from_spec(cf)
    sys.modules["conftest"] = mc
    cf.loader.exec_module(mc)
    spec = importlib.util.spec_from_file_location("e2e_de_validat_17_5_G", os.path.join(RAD, "frontend_test", "e2e", "e2e_de_validat_17_5_G.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _cauta(t, pg, parcurs, card, camp, prev):
    TOP = t.TOP
    if not t._card(pg, parcurs, t.F1, card):
        return None
    try:
        pg.wait_for_selector(TOP + camp, timeout=15000)
    except Exception:   # noqa: BLE001
        for _ in range(3):
            try:
                pg.click(TOP + prev, timeout=5000)
                pg.wait_for_selector(TOP + camp, timeout=8000)
                break
            except Exception:   # noqa: BLE001
                continue
    pg.wait_for_timeout(1000)
    return pg.evaluate(t.JS_CAUTARE, camp)


def _linie(nume, m):
    if not m:
        return "%s: câmpul lipsește" % nume
    return "%s: text de îndrumare %d px, câmp %.0f px, %s; «%s»" % (nume, m["text"], m["camp"], "ÎNTREG" if m["text"] <= m["camp"] else "TĂIAT", m["placeholder"])


def main(lat, iesire):
    from playwright.sync_api import sync_playwright
    from core import ceas_proba
    t = _modul_test()
    parcurs = t._incarca_parcurs_17_1()
    inalt = {1366: 768, 603: 590}[lat]
    linii = ["comanda: python docs/dovezi/17_5_G/masuri_17_5_G.py %d %s" % (lat, os.path.basename(iesire)), "viewport: %d×%d, ceas %s" % (lat, inalt, ceas_proba.MOMENT_REF)]
    with sync_playwright() as pw:
        br = pw.chromium.launch(headless=True)
        b = br.new_context(viewport={"width": lat, "height": inalt})
        b.clock.set_fixed_time(ceas_proba.MOMENT_REF)
        b.add_init_script(t.sesiune(t.ADMIN))
        pg = b.new_page()
        pg.goto(t.BAZA + "/", wait_until="load", timeout=30000)
        tenant_id = None
        if lat == 1366:
            try:
                with pg.expect_response(lambda r: t.URL_CIORNE.match(r.url) is not None and r.request.method == "GET", timeout=30000) as rc:
                    deschis = t._de_validat(pg)
                fr = (rc.value.json() or {}).get("firme") or []
                tenant_id = fr[0]["tenant_id"] if fr else None
            except Exception:   # noqa: BLE001
                deschis = t._de_validat(pg)
            if deschis:
                r = pg.evaluate(t.JS_CONTURI)
                linii.append("De validat, coloana «Conturi» goală: %d din %d rânduri" % (len([x for x in r if not x["text"]]), len(r)))
            else:
                linii.append("De validat, coloana «Conturi»: fereastra nu s-a deschis")
            p2 = b.new_page()
            p2.route(t.URL_COADA, t._json_route(t._note_fictive(tenant_id if tenant_id is not None else 0)))
            try:
                if t._de_validat(p2) and p2.locator(t.TOP + "#val-aproba-selectate").count():
                    m = p2.locator(t.TOP + ".fj-motiv")
                    linii.append("bara de jos cu nimic bifat (două note fictive): «%s»" % (t._norm(m.first.inner_text()) if m.count() else ""))
                else:
                    linii.append("bara de jos: «Validează selectate» lipsește")
            finally:
                p2.close()
        masuri = [("Casă", _cauta(t, pg, parcurs, "#fa-casa", "#c-cauta", "#c-prev")),
                  ("Bancă", _cauta(t, pg, parcurs, "#fa-banca", "#bk-cauta", "#bk-prev")),
                  ("Registru jurnal", _cauta(t, pg, parcurs, "#fa-jurnal", "#jn-cauta", "#j-prev"))]
        masuri.append(("De validat", pg.evaluate(t.JS_CAUTARE, "#val-cauta") if t._de_validat(pg) else None))
        linii += [_linie(n, m) for n, m in masuri]
        if lat == 1366:
            try:
                t._acasa(pg)
                pg.click("button.cab-card:has([data-cheie='control'])", timeout=10000)
                pg.wait_for_selector(t.TOP + "#cf-lista tbody tr", timeout=60000)
                pg.wait_for_timeout(1500)
                r = pg.locator(t.TOP + "#cf-lista tbody tr", has_text=t.F1)
                linii.append("Control fiscal, rândul F1: «%s»" % (t._norm(r.first.inner_text()) if r.count() else "lipsește"))
            except Exception as e:   # noqa: BLE001
                linii.append("Control fiscal: nu s-a deschis (%s)" % str(e)[:100])
        b.close()
        br.close()
    with open(iesire, "w", encoding="utf-8") as f:
        f.write("\n".join(linii) + "\n")
    print("\n".join(linii))


if __name__ == "__main__":
    main(int(sys.argv[1]), sys.argv[2])
