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


# ── Control fiscal: lista din rezumat față de detaliu (156, 173 — retestul Costin 09.10) ──────────────────────────────────────
def _rezumat_cf(firma, date, epoca):
    """Rândul de rezumat al firmei pentru Control fiscal, scris cu versiunea surselor de acum și epoca dată."""
    from core import db, firma_rezumat as fr
    with db.get_conn() as c:
        v = fr.versiune_aspect(c, firma["tenant_id"], "control_fiscal")
        fr.scrie(c, firma["tenant_id"], "control_fiscal", date, v, epoca=epoca)
        c.commit()


def _rand_cf(e, nume):
    e.acasa()
    e.pg.click("button.cab-card:has([data-cheie='control'])")
    e.pg.wait_for_selector("#cf-lista .mig-frand", timeout=120000)
    return e.pg.evaluate("""(n) => { const r = [...document.querySelectorAll('#cf-lista .mig-frand')].find(x => x.innerText.includes(n));
      return r ? {sub: r.querySelector('.mig-frand-sub').innerText, et: r.querySelector('.cf-stare').innerText.trim()} : null; }""", nume)


def test_def_156_lista_nu_arata_un_rezumat_calculat_de_alt_cod(patron, firma_e2e):
    """156. Control fiscal: „restanță” la „0 restanțe”; „0 de urmărit” vs 5 în detaliu.
    [retestul Costin 09.10, cuvânt cu cuvânt] „F3: lista «5 restanțe · 3 de urmărit», detaliul 3 și 2.” Cauza, din jurnalul producției:
    rezumatul listei fusese calculat de codul de dinainte de publicarea de la 11:01 și rămăsese „curent” (versiunea surselor nu se
    schimbase), iar detaliul calcula cu codul nou. Pașii: rezumatul firmei e calculat de ALT cod (epoca fără amprenta codului de acum)
    și spune „5 restanțe · 3 de urmărit” -> lista nu are voie să arate cifrele lui ca actuale: spune că firma e în recalculare.
    [testul vechi trecea pe defect: verifica doar acordul dintre cifrele aceluiași rezumat]"""
    import datetime as _d
    _rezumat_cf(firma_e2e, {"stare": "rosu", "lipsa": 5, "urmarit": 3, "neclar": 0, "contabil": []}, _d.date.today().isoformat())
    r = _rand_cf(patron, firma_e2e["nume"])
    patron.captura("lista")
    assert r and "5 restanțe" not in r["sub"] and "3 de urmărit" not in r["sub"], r
    assert "în recalculare" in r["sub"], r


def test_def_173_randul_spune_ce_numara_contorul(patron, firma_e2e):
    """173. Control fiscal: contoarele cu două reguli; cifrele raportului nu sunt pe ecran.
    [retestul Costin 09.10, cuvânt cu cuvânt] „«3 nu se pot verifica», lista arată 2.” Calea: o firmă cu restanțe ȘI o verificare
    contabilă care nu se poate face (gri) e numărată la „nu se pot verifica”, dar rândul ei spunea doar „2 restanțe · TVA vs sold
    balanță”. Pașii: rezumatul curent al firmei are 2 restanțe și verificarea „TVA vs sold balanță” gri -> contorul de sus „nu se pot
    verifica” = rândurile care o spun, iar rândul acestei firme o spune."""
    from core import firma_rezumat as fr
    import datetime as _d
    _rezumat_cf(firma_e2e, {"stare": "rosu", "lipsa": 2, "urmarit": 0, "neclar": 0,
                            "contabil": [{"eticheta": "TVA vs sold balanță", "stare": "gri"}]},
                fr.epoca_pentru("control_fiscal", _d.date.today()))
    r = _rand_cf(patron, firma_e2e["nume"])
    d = patron.pg.evaluate("""() => { const f = [...document.querySelectorAll('.fereastra')].pop();
      const p = [...f.querySelectorAll('.cf-sumar .cf-pastila')].map(e => e.innerText.trim()).find(t => t.endsWith('nu se pot verifica'));
      const rr = [...f.querySelectorAll('#cf-lista .mig-frand')].map(x => x.innerText);
      return {contor: parseInt(p, 10), randuri: rr.filter(t => /nu se (poate|pot) verifica|în recalculare/.test(t)).length}; }""")
    patron.captura("lista")
    assert r and "nu se poate verifica" in r["sub"], r
    assert d["contor"] == d["randuri"], d
