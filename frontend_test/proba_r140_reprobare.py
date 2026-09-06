# -*- coding: utf-8 -*-
"""REPROBARE R140 — cele OPT refuzuri ale registrului de partidă simplă, toate opt.

DE CE EXISTĂ. R140 a fost reparată în lotul 12 și reprobată atunci pe **unul** din opt, apăsând
«Adaugă (ciornă)» pe formular invalid. Comanda de azi cere reprobarea **tuturor celor opt**. Ele
nu se pot declanșa toate din ecran: `tip`, `metoda` și `categorie` sunt `<select>`-uri (nu pot lua
o valoare nevalidă), iar `valuta` **nu are câmp în formular**. Deci proba are două straturi, și se
spune care e care:
  * **ECRAN** — cele trei accesibile din formular (suma, data, explicația): se apasă butonul real
    și se citește ce apare în `#r-mesaj`.
  * **RUTĂ** — toate opt, prin `POST /tenants/{id}/rip/operatiuni` chemat **din pagina
    autentificată** (`fetch` în contextul filei), deci pe același drum, cu aceeași sesiune.
`_valideaza` e singura poartă a rutei, iar ruta e singura cale de scriere: nu există al treilea drum.

CALIBRARE ÎN CEALALTĂ DIRECȚIE: o operațiune **validă** trece (altfel proba ar spune „opt refuzuri"
despre un registru care refuză tot). Ce scrie se șterge **prin ruta aplicației**, iar numărul de
rânduri se citește din bază înainte și după — *o sondă „de citire" scrie până n-o dovedești.*

Rulare (instanță proaspătă, cod nou):
    PROBA_BAZA=http://127.0.0.1:8011 ./venv/bin/python frontend_test/proba_r140_reprobare.py
"""
import json
import os
import sys

_H = os.path.dirname(os.path.abspath(__file__))
_R = os.path.abspath(os.path.join(_H, ".."))
sys.path.insert(0, os.path.join(_R, "frontend_test", "vizual"))
sys.path.insert(0, _H)
sys.path.insert(0, _R)

from playwright.sync_api import sync_playwright  # noqa: E402
import w_auth  # noqa: E402
import nav_ecrane  # noqa: E402
from core import db  # noqa: E402

SCHEMA_PFA = "tenant_048"

# Cele OPT ramuri ale lui `core/rip_api._valideaza`, in ordinea din cod. Fiecare corp e valid in
# tot afara de UN lucru — altfel proba n-ar sti pe care ramura a cazut.
BAZA_OK = {"data_operatiune": "2026-09-01", "tip": "incasare", "categorie": "activitate",
           "suma": 100, "metoda": "numerar", "explicatie": "Proba reprobare R140"}


def _corp(**mod):
    c = dict(BAZA_OK)
    c.update(mod)
    return {k: v for k, v in c.items() if v is not None}


CAZURI = [
    ("1. tip",            _corp(tip="altceva")),
    ("2. metoda",         _corp(metoda="cec")),
    ("3. suma",           _corp(suma=0)),
    ("4. data",           _corp(data_operatiune="")),
    ("5. explicatie",     _corp(explicatie="   ")),
    ("6. categorie",      _corp(categorie="chirii")),
    ("7. deductibilitate", _corp(tip="plata", categorie="cheltuiala_deductibila",
                                deductibilitate=None)),
    ("8. valuta",         _corp(valuta="EUR", suma_valuta=None, curs_valutar=None)),
]

JS_FETCH = """
async ([tid, corp]) => {
  const r = await fetch(`/tenants/${tid}/rip/operatiuni`, {
    method: "POST",
    // Tokenul e cel pe care il pune `w_auth` in sessionStorage si pe care `api.js` il trimite
    // la fiecare cerere: proba merge pe acelasi drum, nu pe unul ocolit.
    headers: {"Content-Type": "application/json",
              "Authorization": "Bearer " + sessionStorage.getItem("iconta_token")},
    body: JSON.stringify(corp),
  });
  let d = null;
  try { d = await r.json(); } catch (e) { d = null; }
  return {status: r.status, corp: d};
}
"""

JS_DELETE = """
async ([tid, oid]) => {
  const r = await fetch(`/tenants/${tid}/rip/operatiuni/${oid}`, {
    method: "DELETE",
    headers: {"Authorization": "Bearer " + sessionStorage.getItem("iconta_token")}});
  return r.status;
}
"""


def _randuri(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM %s.rip_operatiuni" % SCHEMA_PFA)
        return cur.fetchone()[0]


def _tenant_id(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM public.tenants WHERE schema_name=%s", (SCHEMA_PFA,))
        r = cur.fetchone()
    assert r, "firma de partida simpla (%s) lipseste" % SCHEMA_PFA
    return r[0]


def _mesaj_ecran(pg):
    try:
        return (pg.locator("#r-mesaj").inner_text() or "").strip().replace("\n", " ")
    except Exception:  # noqa: BLE001
        return ""


def main():
    db.init_pool()
    conn = db.get_conn().__enter__()
    tid = _tenant_id(conn)
    inainte = _randuri(conn)
    print("firma: %s (tenant %d) · randuri INAINTE: %d" % (SCHEMA_PFA, tid, inainte))

    rez = {"baza": w_auth.BAZA, "tenant": tid, "randuri_inainte": inainte,
           "ecran": [], "ruta": [], "valid": None}

    with sync_playwright() as p:
        b, pg = w_auth.new_page(p, nav_ecrane.CONT_TEST)   # contul cabinetului de TEST (4163), al carui e firma PFA
        nav_ecrane.ecran_rip_pfa(pg)

        # ── STRATUL 1: ECRAN. Cele trei accesibile din formular. ─────────────
        pg.click("#r-toggle")
        pg.wait_for_timeout(300)
        ECRAN = [
            ("3. suma", {"#r-data": "2026-09-01", "#r-suma": "", "#r-expl": "Proba R140"}),
            ("4. data", {"#r-data": "", "#r-suma": "100", "#r-expl": "Proba R140"}),
            ("5. explicatie", {"#r-data": "2026-09-01", "#r-suma": "100", "#r-expl": ""}),
        ]
        for (nume, campuri) in ECRAN:
            for sel, val in campuri.items():
                pg.fill(sel, val)
            pg.click("#r-adauga")
            pg.wait_for_timeout(700)
            m = _mesaj_ecran(pg)
            rez["ecran"].append({"caz": nume, "mesaj": m})
            print("  ECRAN %-16s -> %s" % (nume, m[:110]))

        # ── STRATUL 2: RUTA. Toate opt, pe drumul aplicatiei. ────────────────
        for (nume, corp) in CAZURI:
            r = pg.evaluate(JS_FETCH, [tid, corp])
            det = (r.get("corp") or {}).get("detail") or (r.get("corp") or {}).get("mesaj")
            rez["ruta"].append({"caz": nume, "status": r["status"], "mesaj": det})
            print("  RUTA  %-16s %s -> %s" % (nume, r["status"], str(det)[:100]))

        # ── CALIBRARE: una VALIDA trebuie sa treaca, si se sterge dupa. ──────
        r = pg.evaluate(JS_FETCH, [tid, BAZA_OK])
        rez["valid"] = {"status": r["status"], "corp": r.get("corp")}
        print("  VALID  status=%s corp=%s" % (r["status"], r.get("corp")))
        oid = (r.get("corp") or {}).get("id")
        if oid:
            st = pg.evaluate(JS_DELETE, [tid, oid])
            rez["valid"]["sters_status"] = st
            print("  STERS  op %s -> status %s" % (oid, st))
        b.close()

    dupa = _randuri(conn)
    rez["randuri_dupa"] = dupa
    print("randuri DUPA: %d (delta %+d)" % (dupa, dupa - inainte))
    with open(os.path.join(_H, "proba_r140_reprobare.json"), "w", encoding="utf-8") as f:
        json.dump(rez, f, ensure_ascii=False, indent=1)

    # verdictele probei
    assert dupa == inainte, "proba a lasat %d randuri in registru" % (dupa - inainte)
    assert all(x["status"] == 400 for x in rez["ruta"]), "un caz nu a fost refuzat"
    assert all(x["mesaj"] for x in rez["ruta"]), "un refuz a venit fara mesaj"
    assert rez["valid"]["status"] == 200, "operatiunea VALIDA nu a trecut - refuzul e prea larg"
    print("\nOK: 8/8 refuzate cu mesaj, 1 valida acceptata, registru neschimbat.")


main()
