# -*- coding: utf-8 -*-
"""PROBA în browser — C5 și C6 cu generalizarea pe clasă (comanda Costin 07.10.2026), pe baza de TEST (8011).

Reface drumul din parcurgerea din 06.10, ca cabinetul, pe Constructii Profit Trim (09/2026, lună deschisă):

  C5   Operațiuni speciale → „Chirii / comodat / refacturări” → Comodat, primire 1.000 → „Generează nota” → ce spune ecranul
       și câte note s-au scris în bază.
  C6   Operațiuni speciale → „Export extracomunitar (DVE)”: ce fel de câmp e „Dovada export” și ce răspunde la „DVE 123”
       (înainte, câmp text) / la „Da” (după, select). Apoi câmpurile DA/NU din formularele în care serverul citește o bifă
       (provizion › creanță, inventariere › minus, import, perisabilități, decontare în valută, livrare IC): ce se vede, ce e
       preselectat.

Aceeași probă pe codul VECHI (înainte) și NOU (după). SCRIE în baza de test (note ciornă); `curata()` șterge ce a apărut
după reperele de la pornire.

    PYTHONPATH=.:frontend_test ./venv/bin/python frontend_test/proba_c5_c6.py --iesire /tmp/…/c56_dupa.json
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from playwright.sync_api import sync_playwright  # noqa: E402

from core import db  # noqa: E402
from proba_c1_c2_c7 import CAB, firma, pagina  # noqa: E402
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vizual"))
from axe_scan import scaneaza  # noqa: E402

FIRMA = (4840, "tenant_005", "Constructii Profit Trim SRL")
#: formularul -> (select-ul care deschide ramura, valoarea) și bifele pe care serverul le citește pe ea
BIFE = {
    "provizion": (("fel", "creanta"), ["garantata", "afiliata", "faliment", "zile_depasire"]),
    "inventariere": (("operatie", "minus"), ["imputabil", "asigurat_sau_distrus"]),
    "import_ec": (None, ["certificat_amanare"]),
    "perisabilitati": (None, ["degradare_dovedita_distrusa"]),
    "decont_valuta": (None, ["in_lei_cu_clauza"]),
    "vanzare_ic": (("tip", "bunuri"), ["dovada_transport"]),
    "export_ec": (None, ["dovada_export"]),
    "taxare_inversa": (None, ["furnizor_platitor_tva"]),
    "obiect_inv": (("operatie", "achizitie"), ["durata_sub_1_an"]),
}


def repere():
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute('select coalesce(max(id),0) from "%s".inregistrari' % FIRMA[1]); i = cur.fetchone()[0]
        cur.execute("select coalesce(max(id),0) from public.declaratii_coada"); q = cur.fetchone()[0]
        cur.execute("select coalesce(max(id),0) from public.notificari"); n = cur.fetchone()[0]
        c.rollback()
    return {"inreg": i, "coada": q, "notif": n}


def note_noi(rp):
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute('select id, descriere from "%s".inregistrari where id > %%s order by id' % FIRMA[1], (rp["inreg"],))
        r = [list(x) for x in cur.fetchall()]; c.rollback()
    return r


def curata(rp):
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute('delete from "%s".inregistrari where id > %%s' % FIRMA[1], (rp["inreg"],))   # liniile: ON DELETE CASCADE
        cur.execute("delete from public.declaratii_coada where id > %s", (rp["coada"],))
        cur.execute("delete from public.notificari where id > %s", (rp["notif"],))
        c.commit()
    return "curatat"


def deschide(pg, cheie):
    firma(pg, FIRMA[2]); pg.click("#fa-operatiuni"); pg.wait_for_selector("[data-op]", timeout=20000)
    pg.click("[data-op='%s']" % cheie); pg.wait_for_selector("#op-trimite", timeout=15000); pg.wait_for_timeout(400)


def camp(pg, nume):
    el = pg.query_selector("#op-%s" % nume)
    if not el:
        return None
    return pg.evaluate("""(e) => ({tag: e.tagName, tip: e.getAttribute('type'), vizibil: !!(e.offsetParent),
        ales: e.tagName === 'SELECT' ? (e.options[e.selectedIndex] || {}).textContent : null,
        optiuni: e.tagName === 'SELECT' ? [...e.options].map(o => o.textContent.trim()) : null,
        eticheta: (document.querySelector("label[for='" + e.id + "']") || {}).innerText})""", el)


def mesaj(pg):
    return pg.evaluate("() => (document.querySelector('#op-mesaj') || {}).innerText || ''")[:500]


def proba(pw, cap, rp, r):
    b, pg, er = pagina(pw, CAB)
    # C5 — comodat
    deschide(pg, "chirie")
    pg.fill("#op-data", "2026-09-15"); pg.select_option("#op-fel", "comodat"); pg.wait_for_timeout(200)
    pg.fill("#op-valoare", "1000")
    if pg.query_selector("#op-moment"):
        pg.select_option("#op-moment", "primire")
    pg.click("#op-trimite"); pg.wait_for_timeout(3000)
    pg.screenshot(path=os.path.join(cap, "C5_comodat.png"), full_page=True)
    r["C5_ecran"] = mesaj(pg)
    r["C5_note_in_baza"] = note_noi(rp)
    # C6 — export: câmpul și răspunsul
    deschide(pg, "export_ec")
    pg.fill("#op-data", "2026-09-15"); pg.fill("#op-valoare", "5000"); pg.fill("#op-tara_client", "US")
    c = camp(pg, "dovada_export"); r["C6_export_camp"] = c
    if c and c["tag"] == "SELECT":
        pg.select_option("#op-dovada_export", "true")
    elif c:
        pg.fill("#op-dovada_export", "DVE 26ROBV1234567890")
    pg.click("#op-trimite"); pg.wait_for_timeout(3000)
    pg.screenshot(path=os.path.join(cap, "C6_export.png"), full_page=True)
    r["C6_export_ecran"] = mesaj(pg)
    r["C6_export_note"] = len(note_noi(rp)) - len(r["C5_note_in_baza"])
    # C6 — efectul fiscal: ajustarea unei creanțe a unui debitor în faliment (art. 26 alin.(1) lit.j: 100% deductibil). Înainte,
    # bifele nu existau -> serverul punea „nu” -> „deductibil 0%”; după, omul alege „Da” la faliment.
    deschide(pg, "provizion")
    pg.fill("#op-data", "2026-09-15"); pg.select_option("#op-fel", "creanta"); pg.wait_for_timeout(200)
    pg.select_option("#op-actiune", "constituire"); pg.fill("#op-suma", "1000")
    for n, v in (("zile_depasire", "300"), ("garantata", "false"), ("afiliata", "false"), ("faliment", "true")):
        el = pg.query_selector("#op-%s" % n)
        if el and el.evaluate("e => e.tagName") == "SELECT":
            pg.select_option("#op-%s" % n, v)
        elif el:
            pg.fill("#op-%s" % n, v)
    pg.click("#op-trimite"); pg.wait_for_timeout(3000)
    pg.screenshot(path=os.path.join(cap, "C6_provizion_faliment.png"), full_page=True)
    r["C6_provizion_faliment_ecran"] = mesaj(pg)
    r["C6_provizion_faliment_nota"] = [n for n in note_noi(rp) if "creanta" in (n[1] or "").lower()]
    # C6 — clasa: bifele pe fiecare formular
    for cheie, (ramura, bife) in BIFE.items():
        deschide(pg, cheie)
        if ramura:
            pg.select_option("#op-%s" % ramura[0], ramura[1]); pg.wait_for_timeout(200)
        r["C6_%s" % cheie] = {n: camp(pg, n) for n in bife}
        pg.screenshot(path=os.path.join(cap, "C6_%s.png" % cheie), full_page=True)
        # uneltele vizuale pe formularul ATINS (meniul Operațiuni e în axe_scan/mobil_scan, formularele nu): axe + lățime de telefon
        viol, _t = scaneaza(pg)
        pg.set_viewport_size({"width": 393, "height": 851}); pg.wait_for_timeout(300)
        rev = pg.evaluate("() => document.documentElement.scrollWidth > window.innerWidth")
        pg.screenshot(path=os.path.join(cap, "C6_%s_telefon.png" % cheie), full_page=True)
        pg.set_viewport_size({"width": 1366, "height": 900})
        r["vizual_%s" % cheie] = {"axe_reguli": len(viol), "axe_noduri": sum(v["n"] for v in viol), "revarsare_x_393": rev,
                                  "axe": viol}
    # vecinul de tip: puritatea la aurul de investiții
    deschide(pg, "aur")
    r["vecin_puritate"] = camp(pg, "puritate")
    r["erori_consola"] = er
    b.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--iesire", required=True)
    a = ap.parse_args()
    cap = a.iesire.replace(".json", "_capturi"); os.makedirs(cap, exist_ok=True)
    db.init_pool()
    rp = repere(); r = {}
    t0 = time.time()
    try:
        with sync_playwright() as pw:
            proba(pw, cap, rp, r)
    except Exception as e:  # noqa: BLE001
        r["EROARE_PROBA"] = "%s: %s" % (type(e).__name__, str(e).splitlines()[0][:300])
    finally:
        r["curatenie"] = curata(rp); r["durata_s"] = round(time.time() - t0, 1)
        json.dump(r, open(a.iesire, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    for k, v in r.items():
        print(k, json.dumps(v, ensure_ascii=False, default=str)[:700])


if __name__ == "__main__":
    main()
