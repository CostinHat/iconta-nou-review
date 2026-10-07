# -*- coding: utf-8 -*-
"""PROBA în browser — cele 33 de chei opționale fără câmp, regula DS cap.17 (comanda Costin 07.10.2026), pe baza de TEST (8011).

Ca cabinetul, pe Constructii Profit Trim (09/2026, lună deschisă), în Operațiuni speciale:

  INVENTAR  Pentru fiecare formular atins și fiecare opțiune a fiecărui select din el: câmpurile vizibile (etichetă, fel, obligatoriu,
            ce e preselectat). Înainte/după — aici se vede ce cheie a intrat în ecran și că niciuna nu vine preselectată.
  DRUMURI   Cu efect în notă (liniile citite din bază):
            - Credite › Plată rată 1.000 + dobândă 200 + comision 50, dobânda NEangajată: înainte, dobânda și comisionul nu se pot da;
            - Aur › Monedă (an 1915, preț 1.000, valoarea aurului 800): înainte, „preț și valoare aur obligatorii pentru monedă”;
            - Turism › agenția ca intermediar, comision 300 cu TVA inclus: înainte, regimul nu se putea alege;
            - Decont › calculul plafonului de diurnă (externă, 35 EUR, curs 5): înainte, calculul nu exista în ecran;
            - Bacșiș › distribuire în numerar: înainte, sursa era ascunsă la distribuire -> 462 = 5121 (bancă), tăcut.
  VIZUAL    axe + lățime de telefon (393px) pe fiecare formular atins.

SCRIE note ciornă în baza de test; `curata()` le șterge după reperele de la pornire.

    PYTHONPATH=.:frontend_test:frontend_test/vizual ./venv/bin/python frontend_test/proba_chei_optionale.py --iesire /tmp/…/x.json
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vizual"))

from playwright.sync_api import sync_playwright  # noqa: E402

from axe_scan import scaneaza  # noqa: E402
from core import db  # noqa: E402
from proba_c1_c2_c7 import CAB, firma, pagina  # noqa: E402

FIRMA = (4840, "tenant_005", "Constructii Profit Trim SRL")
FORMULARE = ["leasing", "credit", "asociati", "avans", "reevaluare", "provizion", "productie", "inventariere", "tva_incasare",
             "marja_turism", "neinregistrat", "aur", "decont_valuta", "achizitie_ic", "vanzare_ic", "export_ec", "decont", "bacsis",
             "sponsorizare", "subventie", "chirie", "sgr", "ong", "lichidare"]


def repere():
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute('select coalesce(max(id),0) from "%s".inregistrari' % FIRMA[1]); i = cur.fetchone()[0]
        cur.execute("select coalesce(max(id),0) from public.declaratii_coada"); q = cur.fetchone()[0]
        cur.execute("select coalesce(max(id),0) from public.notificari"); n = cur.fetchone()[0]
        c.rollback()
    return {"inreg": i, "coada": q, "notif": n}


def linii_noi(rp, dupa):
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute('select i.id, l.cont_debit, l.cont_credit, l.suma::text from "%s".inregistrari i join "%s".inregistrari_linii l '
                    'on l.inregistrare_id = i.id where i.id > %%s order by i.id, l.id' % (FIRMA[1], FIRMA[1]), (dupa,))
        r = [list(x) for x in cur.fetchall()]; c.rollback()
    return r


def ultima(rp):
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute('select coalesce(max(id),0) from "%s".inregistrari' % FIRMA[1]); x = cur.fetchone()[0]; c.rollback()
    return x


def curata(rp):
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute('delete from "%s".inregistrari where id > %%s' % FIRMA[1], (rp["inreg"],))
        cur.execute("delete from public.declaratii_coada where id > %s", (rp["coada"],))
        cur.execute("delete from public.notificari where id > %s", (rp["notif"],))
        c.commit()
    return "curatat"


def deschide(pg, cheie):
    firma(pg, FIRMA[2]); pg.click("#fa-operatiuni"); pg.wait_for_selector("[data-op]", timeout=20000)
    pg.click("[data-op='%s']" % cheie); pg.wait_for_selector("#op-trimite", timeout=15000); pg.wait_for_timeout(300)


VIZIBILE = """() => [...document.querySelectorAll('.fereastra-corp .camp')].filter(c => c.offsetParent).map(c => {
  const e = c.querySelector('input,select'); const l = c.querySelector('label');
  return {id: e ? e.id : null, tip: e ? (e.tagName === 'SELECT' ? 'select' : e.type) : null,
          eticheta: l ? l.innerText.trim() : '', ales: e && e.tagName === 'SELECT' ? (e.options[e.selectedIndex] || {}).textContent : null};
})"""


def inventar(pg, cheie):
    deschide(pg, cheie)
    out = {"implicit": pg.evaluate(VIZIBILE)}
    selecturi = pg.evaluate("() => [...document.querySelectorAll('.fereastra-corp select[id^=op-]')].filter(s => !s.classList.contains('op-mijloc-fix')).map(s => [s.id, [...s.options].map(o => o.value).filter(v => v)])")
    for sid, valori in selecturi:
        for v in valori:
            el = pg.query_selector("#" + sid)
            if not el or not el.is_visible():
                continue
            pg.select_option("#" + sid, v); pg.wait_for_timeout(120)
            out["%s=%s" % (sid, v)] = pg.evaluate(VIZIBILE)
    return out


def completeaza(pg, valori):
    """Completează ce se poate; întoarce ce NU s-a putut da (câmp absent/ascuns sau opțiune lipsă) — chiar constatarea „înainte”."""
    lipsa = []
    for k, v in valori:
        el = pg.query_selector("#op-%s" % k)
        if el is None or not el.is_visible():
            lipsa.append(k)
            continue
        if el.evaluate("e => e.tagName") == "SELECT":
            if v not in el.evaluate("e => [...e.options].map(o => o.value)"):
                lipsa.append("%s=%s" % (k, v))
                continue
            pg.select_option("#op-%s" % k, v)
        else:
            pg.fill("#op-%s" % k, v)
        pg.wait_for_timeout(120)
    return lipsa


def drum(pg, cap, rp, nume, cheie, valori, multi=None):
    deschide(pg, cheie)
    inainte = ultima(rp)
    lipsa = completeaza(pg, valori)
    if multi:
        for k, v in multi:
            el = pg.query_selector("#m0-%s" % k)
            if el:
                pg.fill("#m0-%s" % k, v)
    pg.click("#op-trimite"); pg.wait_for_timeout(3000)
    pg.screenshot(path=os.path.join(cap, "drum_%s.png" % nume), full_page=True)
    return {"nu_s_a_putut_da": lipsa, "ecran": pg.evaluate("() => (document.querySelector('#op-mesaj') || {}).innerText || ''")[:600],
            "linii_in_baza": linii_noi(rp, inainte)}


def proba(pw, cap, rp, r):
    b, pg, er = pagina(pw, CAB)
    r["inventar"] = {}
    r["vizual"] = {}
    for cheie in FORMULARE:
        r["inventar"][cheie] = inventar(pg, cheie)
        pg.screenshot(path=os.path.join(cap, "form_%s.png" % cheie), full_page=True)
        viol, _t = scaneaza(pg)
        pg.set_viewport_size({"width": 393, "height": 851}); pg.wait_for_timeout(250)
        rev = pg.evaluate("() => document.documentElement.scrollWidth > window.innerWidth")
        pg.set_viewport_size({"width": 1366, "height": 900})
        r["vizual"][cheie] = {"axe_reguli": len(viol), "axe_noduri": sum(v["n"] for v in viol), "revarsare_x_393": rev}
    d = "2026-09-15"
    r["drum_credit_plata"] = drum(pg, cap, rp, "credit_plata", "credit", [
        ("data", d), ("operatie", "plata"), ("tip", "lung"), ("rata", "1000"), ("dobanda", "200"), ("comision", "50"),
        ("dobanda_angajata", "false")])
    r["drum_aur_moneda"] = drum(pg, cap, rp, "aur_moneda", "aur", [
        ("data", d), ("tip", "moneda"), ("puritate", "916"), ("an_emisie", "1915"), ("pret_unitar", "1000"), ("valoare_aur", "800"),
        ("suma", "1000"), ("calitate_client", "PF"), ("client_identificare", "Ion Popescu, CI RX123456"), ("optiune_taxare", "false")])
    r["drum_turism_intermediar"] = drum(pg, cap, rp, "turism_intermediar", "marja_turism", [
        ("data", d), ("calitate_client", "PF"), ("intermediar", "true"), ("comision", "300"), ("tva_inclus", "true"), ("cota", "21")])
    r["drum_decont_plafon"] = drum(pg, cap, rp, "decont_plafon", "decont", [
        ("data", d), ("fel", "plafon"), ("diurna_pe_zi", "100"), ("zile", "3"), ("salariu_baza", "6000"), ("zile_lucratoare", "21"),
        ("deplasare", "externa"), ("diurna_bugetara", "35"), ("curs", "5")])
    r["drum_turism_normal"] = drum(pg, cap, rp, "turism_normal", "marja_turism", [
        ("data", d), ("calitate_client", "PJ"), ("intermediar", "false"), ("optiune_normal", "true"), ("locuri", "RO"), ("cota", "21")],
        multi=[("descriere", "Cazare Brașov"), ("baza", "1000"), ("cota", "21")])
    # vizibilitatea în LANȚ: „Cui se impută” apare numai la Minus + Imputabil: Da; rămâne ascuns când operația devine Plus
    deschide(pg, "inventariere")
    lant = {}
    completeaza(pg, [("operatie", "minus"), ("imputabil", "true")])
    lant["minus_imputabil_da"] = bool(pg.query_selector("#op-vinovat")) and pg.is_visible("#op-vinovat")
    completeaza(pg, [("operatie", "plus")])
    lant["dupa_plus"] = bool(pg.query_selector("#op-vinovat")) and pg.is_visible("#op-vinovat")
    r["lant_inventariere_vinovat"] = lant
    r["drum_bacsis_numerar"] = drum(pg, cap, rp, "bacsis_numerar", "bacsis", [
        ("data", d), ("fel", "distribuire"), ("suma", "500"), ("sursa_distribuire", "numerar")])
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
        if k not in ("inventar",):
            print(k, json.dumps(v, ensure_ascii=False, default=str)[:700])


if __name__ == "__main__":
    main()
