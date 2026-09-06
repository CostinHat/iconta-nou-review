# -*- coding: utf-8 -*-
"""REPROBARE R167 — refuzul de periodicitate TVA își spune temeiul, și numai unde e al lui.

Pe ruta reală (`POST /declaratii/{tip}`), din pagina autentificată, pe firme reale:
  * firmă cu decont **TRIMESTRIAL**, cerere pe lună  → refuz + art. 322 alin. (2)
  * firmă cu decont **LUNAR**, cerere pe trimestru   → refuz + art. 322 alin. (1)
  * **d100** (trimestrial din alt temei) pe aceeași firmă → refuz **fără** art. 322

A treia e jumătate din probă: un temei care apare peste tot nu e un temei, e un ornament.

Nimic nu se scrie — dar nu se PRESUPUNE: amprenta fiecărei scheme (suma rândurilor din toate
tabelele ei) se citește înainte și după. *O sondă „de citire" scrie până n-o dovedești.*
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
from core import db  # noqa: E402

# tenant_003 = «Comert Micro TVA SRL», tip_decont trimestrial · tenant_001 = decont lunar
FIRME = {"trimestrial": "tenant_003", "lunar": "tenant_001"}

JS = """
async ([tip, corp]) => {
  const r = await fetch(`/declaratii/${tip}`, {
    method: "POST",
    headers: {"Content-Type": "application/json",
              "Authorization": "Bearer " + sessionStorage.getItem("iconta_token")},
    body: JSON.stringify(corp)});
  let d = null; try { d = await r.json(); } catch (e) { d = null; }
  return {status: r.status, detail: (d || {}).detail || null};
}
"""


def _tid(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM public.tenants WHERE schema_name=%s", (schema,))
        return cur.fetchone()[0]


def _amprenta(conn, schema):
    """Numarul TOTAL de randuri din schema. Nu se presupune ca ruta „nu scrie": se masoara.
    (`declaratii_depuse` nu exista in schema tenantului — persistarea e in alta parte.)"""
    with conn.cursor() as cur:
        cur.execute("""SELECT table_name FROM information_schema.tables
                       WHERE table_schema=%s AND table_type='BASE TABLE'""", (schema,))
        tabele = [r[0] for r in cur.fetchall()]
        total = 0
        for t in tabele:
            cur.execute('SELECT COUNT(*) FROM "%s"."%s"' % (schema, t))
            total += cur.fetchone()[0]
    return total


def main():
    db.init_pool()
    conn = db.get_conn().__enter__()
    t_trim, t_lun = _tid(conn, FIRME["trimestrial"]), _tid(conn, FIRME["lunar"])
    inainte = {s: _amprenta(conn, s) for s in FIRME.values()}
    print("randuri INAINTE: %s" % inainte)

    CAZURI = [
        ("d300 pe firma TRIMESTRIALA, cerere pe LUNA", "d300",
         {"tenant_id": t_trim, "an": 2026, "luna": 9}, "CF art.322 alin.(2)"),
        ("d300 pe firma LUNARA, cerere pe TRIMESTRU", "d300",
         {"tenant_id": t_lun, "an": 2026, "trim": 3}, "CF art.322 alin.(1)"),
        ("d100 (alt temei) pe firma TRIMESTRIALA, cerere pe LUNA", "d100",
         {"tenant_id": t_trim, "an": 2026, "luna": 9}, None),
    ]

    rez = []
    with sync_playwright() as p:
        b, pg = w_auth.new_page(p)
        pg.goto(w_auth.BAZA + "/", wait_until="domcontentloaded")
        pg.wait_for_timeout(800)
        for (nume, tip, corp, astept) in CAZURI:
            r = pg.evaluate(JS, [tip, corp])
            d = r["detail"] or ""
            rez.append({"caz": nume, "status": r["status"], "mesaj": d, "temei_asteptat": astept})
            print("\n  %s\n    status=%s\n    %s" % (nume, r["status"], d))
        b.close()

    dupa = {s: _amprenta(conn, s) for s in FIRME.values()}
    print("\nranduri DUPA: %s" % dupa)
    with open(os.path.join(_H, "proba_r167_temei_periodicitate.json"), "w", encoding="utf-8") as f:
        json.dump({"baza": w_auth.BAZA, "cazuri": rez,
                   "randuri_inainte": inainte, "randuri_dupa": dupa}, f,
                  ensure_ascii=False, indent=1)

    assert dupa == inainte, "proba a scris ceva"
    for x in rez:
        assert x["status"] == 422, "%s: astept 422, am %s" % (x["caz"], x["status"])
        if x["temei_asteptat"]:
            assert x["mesaj"].endswith(x["temei_asteptat"] + ")") or x["temei_asteptat"] in x["mesaj"], \
                "%s: temeiul %s lipseste" % (x["caz"], x["temei_asteptat"])
        else:
            assert "322" not in x["mesaj"], "%s: art. 322 lipit pe alt temei" % x["caz"]
    print("\nOK: temeiul apare pe setul TVA-decont, si NUMAI pe el.")


main()
