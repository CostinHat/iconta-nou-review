# uz: apasa.py <eticheta> — apasă o dată fiecare acțiune din rând pe ecranele martor (Plan de conturi, Clienți, Casă, Produse), pe 8019; scrie cererile trimise
import sys, os, json, subprocess, importlib.util, re
RAD = os.path.expanduser("~/iconta_lot17_5")
sys.path.insert(0, RAD + "/scripts"); sys.path.insert(0, RAD)
import sesiune_test
from playwright.sync_api import sync_playwright
from core import ceas_proba
spec = importlib.util.spec_from_file_location("parcurs_lot", RAD + "/docs/dovezi/17_5/parcurs_17_5.py")
P = importlib.util.module_from_spec(spec); spec.loader.exec_module(P)
TOP = P.TOP
ETICHETA = sys.argv[1]
SALVEAZA_IN = sys.argv[2]

def restaureaza():
    r = subprocess.run(["sh", "scripts/baza_test.sh", "restaureaza"], cwd=os.environ.get("RADACINA_BAZA", RAD), capture_output=True, text=True)
    return "restaurat" in (r.stdout + r.stderr)

def main():
    sc = sesiune_test.sesiune("dovada.71507@sesiuneab.test")
    out = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        def nou():
            c = b.new_context(viewport={"width": 1366, "height": 768}); c.clock.set_fixed_time(ceas_proba.MOMENT_REF); c.add_init_script(sc)
            pg = c.new_page(); reqs = []
            def cer(r):
                u = re.sub(r"^https?://[^/]+", "", r.url)
                if r.method != "GET" or "verifica-cui" in u:
                    if "/api/eveniment" in u or "eveniment-public" in u: return
                    reqs.append("%s %s %s" % (r.method, u.split("?")[0], (r.post_data or "")[:200]))
            pg.on("request", cer)
            pg.goto("http://127.0.0.1:8019/", wait_until="load", timeout=30000)
            return c, pg, reqs
        def apasa(pg, css, confirm):
            btn = pg.locator(css).first
            btn.wait_for(state="attached", timeout=15000)
            det = btn.locator("xpath=ancestor::details[1]")
            if det.count():
                det.locator("summary").click()
            if btn.get_attribute("aria-disabled") == "true" or btn.is_disabled():
                raise Exception("INACTIV: %s" % (btn.get_attribute("data-motiv-inactiv") or btn.get_attribute("title") or "fără motiv")[:90])
            btn.click(timeout=10000)
            if confirm:
                try: pg.click("#ca-ok", timeout=4000)
                except Exception: pass
            pg.wait_for_timeout(2500)
        def caz(nume, deschide, css, confirm, distructiv, pre=None):
            if distructiv: restaureaza()
            c, pg, reqs = nou()
            try:
                deschide(pg)
                if pre: pre(pg)
                apasa(pg, css, confirm)
                r = "; ".join(reqs) or "(nicio cerere de scriere)"
            except Exception as e:
                r = ("%s (cereri: %s)" % (str(e).splitlines()[0][:140], "; ".join(reqs) or "niciuna")) if str(e).startswith("INACTIV") else "EROARE %s: %s" % (type(e).__name__, str(e).splitlines()[0][:120])
            out.append("%s | %s" % (nume, r)); print(out[-1], flush=True); c.close()
        T = TOP
        caz("Plan de conturi · Adaugă analitic (sintetic)", P.ecran_plan, T + "#pcf-lista [data-analitic]:not([aria-disabled='true'])", False, False)
        caz("Plan de conturi · Șterge", P.ecran_plan, T + "#pcf-lista [data-sterge]:not([aria-disabled='true'])", True, True)
        caz("Clienți · Verifică la ANAF", P.ecran_clienti, T + "#cl-tabel .fisa-anaf:not([aria-disabled='true'])", False, False)
        def edit_cl(pg):
            i = pg.locator(T + "#cl-tabel input[id^='cl-oras-']").first; i.fill("Cluj-Napoca"); pg.wait_for_timeout(500)
        caz("Clienți · Salvează (după modificarea localității)", P.ecran_clienti, T + "#cl-tabel button[id^='cl-salveaza-']:not([disabled])", False, True, edit_cl)
        caz("Clienți · Șterge", P.ecran_clienti, T + "#cl-tabel button[id^='cl-sterge-']", True, True)
        caz("Casă · Stornează", P.ecran_casa, T + "#c-tabel [data-storno]", True, True)
        caz("Casă · Șterge", P.ecran_casa, T + "#c-tabel [data-del]", True, True)
        def corecteaza(pg):
            pg.locator(T + "#pr-lista .pr-corecteaza").first.click(); pg.wait_for_timeout(400)
            s = pg.locator(T + "#pr-lista select[id^='pr-cota-']:visible").first
            o = s.locator("option").all(); vals = [x.get_attribute("value") for x in o if x.get_attribute("value")]
            s.select_option(vals[0]); pg.wait_for_timeout(300)
        caz("Produse · Salvează cota (după Corectează cota)", P.ecran_produse, T + "#pr-lista .pr-corectura-salveaza", True, True, corecteaza)
        caz("Produse · Șterge", P.ecran_produse, T + "#pr-lista .pr-sterge", True, True)
        b.close()
    open(SALVEAZA_IN, "w", encoding="utf-8").write("\n".join(out) + "\n")

main()
