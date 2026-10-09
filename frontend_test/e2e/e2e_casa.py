# -*- coding: utf-8 -*-
"""Casă — deficiențele din DEFICIENTE.md probate în browser, pe firma sintetică a rulării (`firma_e2e`)."""
import datetime as _dt

from conftest import sql


def _operatiune_cu_nota_validata(firma, suma="1250.00"):
    """O încasare de la client pe drumul aplicației (`casa_api.adauga`: operațiunea + nota ciornă), apoi nota validată."""
    from core import casa_api, db
    s = firma["schema"]
    with db.get_conn() as c:
        r = casa_api.adauga(c, s, {"data": _dt.date.today().isoformat(), "tip": "incasare", "categorie": "incasare_client",
                                   "suma": suma, "partener": "Client Proba E2E SRL", "document": "CH E2E 1"})
        c.commit()
    assert "eroare" not in r, r
    sql('UPDATE "%s".inregistrari SET status = \'validata\' WHERE id = %%s' % s, (r["inregistrare_id"],))
    return r["id"], r["inregistrare_id"]


def test_def_174_operatiunea_cu_nota_validata_se_storneaza_nu_se_sterge(patron, firma_e2e):
    """174. Casă: operațiune cu notă validată are buton „Șterge”.
    Pașii contabilului: deschide firma -> Casă -> pe operațiunea cu nota validată caută acțiunea. Trebuie „Stornează” (nu „Șterge”);
    după stornare, registrul arată operațiunea inversă (−1.250,00 lei), iar nota în roșu e o ciornă care trece prin validare."""
    oid, iid = _operatiune_cu_nota_validata(firma_e2e)
    pg = patron.pg
    patron.firma(firma_e2e["nume"])
    pg.click("#fa-casa")
    pg.wait_for_selector(".fereastra:last-of-type [data-storno='%s']" % oid, timeout=20000)
    assert pg.locator(".fereastra:last-of-type [data-del='%s']" % oid).count() == 0, "operațiunea cu notă validată are „Șterge”"
    assert "1.250,00" in patron.fereastra()
    patron.captura("inainte")
    pg.click(".fereastra:last-of-type [data-storno='%s']" % oid)
    pg.click("#ca-ok")
    pg.wait_for_function("() => [...document.querySelectorAll('.fereastra')].pop().innerText.includes('−1.250,00')",
                         timeout=20000)
    patron.captura("dupa")
    st = sql('SELECT o.suma::text, i.status FROM "%s".casa_operatiuni o JOIN "%s".inregistrari i ON i.id = o.inregistrare_id '
             "WHERE o.storno_de = %%s" % (firma_e2e["schema"], firma_e2e["schema"]), (oid,))
    assert st == [("-1250.00", "ciorna")], st
    assert pg.locator(".fereastra:last-of-type [data-storno='%s']" % oid).count() == 0, "operațiunea stornată se poate storna din nou"
