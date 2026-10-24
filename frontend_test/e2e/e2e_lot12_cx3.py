# -*- coding: utf-8 -*-
"""Lotul 12, pachetul cx3: testele de capăt la capăt pentru C110, C122 și C45.

  · C110 — prestarea intracomunitară din Operațiuni (`uc_tenants.vanzare_ic`) poartă regimul de TVA al firmei: pe un neplătitor înregistrat
    art.317 (forma firmei de test F3) factura e fără TVA, linia nu primește categoria plătitorului, iar PDF-ul spune regimul special
    (CF art.310 alin.(10) lit.b; CF art.317 alin.(1) lit.b — înregistrarea pentru serviciile cu locul în alt stat membru).
  · C122 — amintirea scadenței către clientul firmei (jobul zilnic `notificari_scadenta`, pe firma probei): subiectul și corpul spun starea
    facturii exact ca Scadențarul (cu diacritice), data scadenței ZZ.LL.AAAA și suma în forma aplicației (DS cap.4, cap.7).
    Emailul nu are ecran: se citește din cutia poștală de test a aplicației de probă (`ICONTA_EMAIL_CUTIE`, `observare._in_cutia_de_test`).
  · C45 — chitanța de dinainte de lotul 6 (nota ei validată, fără `factura_id`) stinge factura și la Bancă: „Alege facturile” nu mai oferă
    factura încasată, iar nota validată rămâne neatinsă (OMFP 1802/2014 pct.69: nota validată nu se modifică).

Pașii pe aplicația din index, pe baza de TEST, pe firme NOI de test (`firma_noua`), pregătite pe drumul ecranelor (`pregateste_firma`).
VIES e servit de plasă (`<ICONTA_ANAF_SIMULAT>/vies.json`, codul DE811907980 al probei R187 / C78). `sql` citește; singurele scrieri
SQL sunt datele de pornire marcate (chitanța veche a lui C45, scrisă cum o scria codul de dinainte de reparație)."""
import datetime as _dt
import glob
import json
import os
import time

import pytest

from conftest import firma_noua, sql

COD_CLIENT_IC = "DE811907980"
_F = ".fereastra:last-of-type "


@pytest.fixture()
def firma_cx3():
    for f in firma_noua():
        yield f


# ── C110 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _neplatitor_art317(patron, f):
    """Date firmă (stoc global-valoric: serviciile n-au articol) + vectorul fiscal al unui neplătitor înregistrat art.317 cu operațiuni
    intracomunitare — aceleași rute ca ecranele „Date firmă” și „Vector fiscal”."""
    from e2e_bloc_a import _api, _ok, _profil, pregateste_firma
    pregateste_firma(patron, f, platitor=False)
    tid = f["tenant_id"]
    p = _profil(f, platitor=False)
    p["metoda_stoc"] = "global_valoric"
    _ok(_api(patron, "POST", "/tenants/%d/firma-profil/date" % tid, p), "Date firmă (stoc global-valoric)")
    _ok(_api(patron, "POST", "/tenants/%d/vector" % tid, {"regim_fiscal": "micro", "platitor_tva": False, "tip_decont": None,
                                                         "operatiuni_ic": True, "inreg_art317": True, "tva_data_inceput": None}),
        "vector fiscal (neplătitor, înregistrat art.317)")
    d = os.environ.get("ICONTA_ANAF_SIMULAT")
    if d:   # VIES pe plasă: răspunsul „valid” al clientului german
        os.makedirs(d, exist_ok=True)
        cale = os.path.join(d, "vies.json")
        vies = json.load(open(cale, encoding="utf-8")) if os.path.exists(cale) else {}
        vies[COD_CLIENT_IC] = {"valid": True, "nume": "KUNDE E2E GMBH", "adresa": "Berlin", "eroare": None}
        with open(cale, "w", encoding="utf-8") as fo:
            json.dump(vies, fo, ensure_ascii=False)


def test_def_c110_prestarea_ic_a_neplatitorului_art317_poarta_regimul_firmei(patron, firma_cx3):
    """C110. Pașii: firmă neplătitoare de TVA, înregistrată art.317 -> Operațiuni speciale -> „Livrare/prestare intracomunitară” ->
    Servicii, 1.000 lei, client DE811907980 (VIES valid), cont 704 -> „Generează nota” -> confirmarea -> Facturi -> „Istoric facturi” ->
    factura nouă: linia 0% fără categoria plătitorului (`.fd-categorie` lipsă), PDF-ul cu mențiunea neplătitorului
    (`factura_pdf.MENTIUNE_NEPLATITOR`); în bază, linia are categoria `categorii_tva.NEPLATITOR` și axa „servicii” (D390 cod P).
    MUTAȚIA (`mut_lot12_cx3.json`): `creeaza_factura` pune categoria după „plătitor” în loc de regimul citit din profil -> ROȘU (drumul pe
    care regimul firmei ajunge pe factura prestării; vezi raportul C110 pentru de ce parametrul reparat nu are efect vizibil singur)."""
    from core import categorii_tva, factura_pdf
    from e2e_bloc_a import AZI, _deschide_factura, _pdf_ok, _pdf_text
    f = firma_cx3
    s = f["schema"]
    _neplatitor_art317(patron, f)
    inainte = {r[0] for r in sql('SELECT id FROM "%s".facturi' % s)}
    patron.firma(f["nume"])
    pg = patron.pg
    pg.click("#fa-operatiuni")
    pg.wait_for_selector("[data-op]", timeout=20000)
    pg.locator("button[data-op='vanzare_ic']").click()
    pg.wait_for_selector("#op-trimite", timeout=10000)
    pg.fill("#op-data", AZI.isoformat())
    pg.fill("#op-valoare", "1000")
    pg.fill("#op-cod_tva_client", COD_CLIENT_IC)
    pg.select_option("#op-tip", "servicii")
    pg.fill("#op-cont_venit", "704")
    pg.fill("#op-descriere", "Consultanta IC E2E C110")
    pg.click("#op-trimite")
    pg.wait_for_selector("#op-mesaj .caseta-ok", timeout=30000)
    patron.captura("confirmarea")
    noi = [r[0] for r in sql('SELECT id FROM "%s".facturi ORDER BY id' % s) if r[0] not in inainte]
    assert len(noi) == 1, noi
    fid = noi[0]
    # CF art.310 alin.(10) lit.b: neplătitorul „nu are voie să menționeze taxa pe factură” -> linia 0%, categoria regimului special (O)
    assert sql('SELECT categorie_tva, cota_tva::text FROM "%s".factura_linii WHERE factura_id = %%s' % s, (fid,)) == [
        (categorii_tva.NEPLATITOR["cod"], "0.00")]
    # CF art.325 alin.(1) lit.c: prestarea art.278 alin.(2) a înregistratului art.317 intră în D390 — axa „servicii” de pe document (P)
    assert sql('SELECT axa_ic, tert_tara FROM "%s".facturi WHERE id = %%s' % s, (fid,)) == [("servicii", "DE")]
    _deschide_factura(patron, f, fid)
    patron.captura("factura")
    assert pg.locator(".fd-categorie").count() == 0, "linia neplătitorului poartă o categorie de plătitor"
    with pg.expect_response(lambda r: r.url.endswith("/facturi/%s/pdf" % fid), timeout=30000) as rr:
        pg.click("#fd-pdf")
    text, _titlu = _pdf_text(_pdf_ok(patron, rr))
    assert " ".join(factura_pdf.MENTIUNE_NEPLATITOR.split()) in text, text[-600:]


# ── C122 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _emailurile(cutie, catre, inainte):
    out = []
    for cale in sorted(set(glob.glob(os.path.join(cutie, "*.json"))) - inainte):
        e = json.load(open(cale, encoding="utf-8"))
        if e.get("catre") == catre:
            out.append(e)
    return out


def test_def_c122_amintirea_scadentei_spune_starea_ca_scadentarul(patron, firma_cx3):
    """C122. Pașii: Date firmă cu emailul firmei (adresa de răspuns) -> clientul cu email -> factura emisă cu scadența peste 3 zile ->
    Facturi -> Scadențar -> bifa „Trimite automat notificări de plată clienților” -> jobul zilnic al amintirilor, pe firmă
    (`notificari_scadenta.emite_pentru_firma`, ce rulează cronul de la 08:00) -> emailul din cutia de test: subiectul și corpul spun starea
    facturii exact ca rândul ei din Scadențar („scade în 3 zile”, cu diacritice), data scadenței în forma aplicației (`pdf_util.data_ro`,
    ZZ.LL.AAAA — nu ISO) și suma în forma aplicației (`pdf_util.bani`). Înainte: „Factura X - scade in 3 zile”, data 2026-10-27.
    MUTAȚIA (`mut_lot12_cx3.json`): `_eticheta` întoarce textul vechi, fără diacritice -> subiectul nu mai spune ce spune Scadențarul -> ROȘU."""
    from conftest import _db
    from core import notificari_scadenta
    from core.pdf_util import bani, data_ro
    from e2e_bloc_a import CLIENT, PRODUS, _api, _card, _ok, _profil, pregateste_firma
    f = firma_cx3
    tid = f["tenant_id"]
    pregateste_firma(patron, f)
    p = _profil(f)
    p["email"] = "firma.c122.%d@prisma-cont.test" % tid
    _ok(_api(patron, "POST", "/tenants/%d/firma-profil/date" % tid, p), "Date firmă (emailul firmei)")
    email_client = "client.c122.%d@prisma-cont.test" % tid
    cid = _ok(_api(patron, "POST", "/tenants/%d/clienti" % tid, {"nume": CLIENT["#em-nume"], "cui": CLIENT["#em-cui"],
                                                                "adresa": CLIENT["#em-adresa"], "email": email_client}), "client")["client_id"]
    azi = _dt.date.today()
    scadenta = azi + _dt.timedelta(days=3)
    fac = _ok(_api(patron, "POST", "/tenants/%d/facturi/emite" % tid, {
        "linii": [{"descriere": PRODUS, "cantitate": 2, "um": "ora", "pret_unitar": 150.0, "cota_tva": 21, "cota_propusa": 21,
                   "articol_id": None}],
        "client_id": cid, "tert_nume": CLIENT["#em-nume"], "tert_cui": CLIENT["#em-cui"], "tert_adresa": CLIENT["#em-adresa"],
        "moneda": "RON", "tert_tara": "RO", "tip_operatiune": "normal", "bon_fiscal_nr": None, "bon_fiscal_data": None,
        "data_emitere": azi.isoformat(), "data_scadenta": scadenta.isoformat(), "tip": "factura"}), "emitere")
    patron.firma(f["nume"])
    pg = patron.pg
    _card(patron, "facturi", "#fac-scadentar")
    pg.click("#fac-scadentar")
    pg.wait_for_selector("#sc-optin", timeout=25000)
    pg.check("#sc-optin")
    # notificările active: rândul facturii primește supapa „nu notifica” (numai cu bifa pusă, `scadentarEcran`)
    pg.wait_for_selector("#sc-lista [data-stop='%s']" % fac["factura_id"], timeout=20000)
    rand = pg.locator("#sc-lista .sc-fact-btn[data-id='%s'] .pf-frand-sub" % fac["factura_id"])
    patron.captura("scadentar")
    starea_pe_ecran = " ".join(rand.inner_text().split()).split(" · ")[0]
    assert starea_pe_ecran, rand.inner_text()
    cutie = os.environ["ICONTA_EMAIL_CUTIE"]
    inainte = set(glob.glob(os.path.join(cutie, "*.json")))
    _db()
    rez = notificari_scadenta.emite_pentru_firma(f["schema"])
    assert rez["trimise"] == 1, rez
    gasite = []
    for _ in range(20):
        gasite = _emailurile(cutie, email_client, inainte)
        if gasite:
            break
        time.sleep(0.5)
    assert len(gasite) == 1, gasite
    m = gasite[0]
    numar, stare = m["subiect"].rsplit(" — ", 1)
    assert stare == starea_pe_ecran, (m["subiect"], starea_pe_ecran)
    assert numar.endswith(" " + fac["numar"]), (m["subiect"], fac["numar"])
    corp = " ".join(m["html"].split())
    assert starea_pe_ecran in corp, corp
    assert data_ro(scadenta) in corp and scadenta.isoformat() not in corp, corp
    assert bani(fac["total"]) in corp, (bani(fac["total"]), corp)   # suma în forma aplicației (1.234,56), nu „363.0”


# ── C45 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_c45_chitanta_de_dinainte_stinge_factura_si_la_banca(patron, firma_cx3):
    """C45. Pașii: factura emisă (363,00 lei) încasată cu o chitanță de dinainte de lotul 6 (nota ei 5311 = 4111, validată, fără legătura
    `factura_id` — forma scrisă atunci; date de pornire) -> Bancă -> extrasul cu o încasare de 363,00 de la același client -> „Alege
    facturile” pe linie: factura încasată cu chitanță NU e printre facturile deschise; factura arată „încasată”; nota validată a chitanței
    are tot `factura_id` gol (OMFP 1802/2014 pct.69: nota validată nu se modifică — forma dintâi a migrării `migrare_casa_avans` o
    modifica). MUTAȚIA (`mut_lot12_cx3.json`): ramura chitanței scoasă din `compensari_api.nota_stinge_factura` -> factura apare deschisă
    la Bancă -> ROȘU."""
    from e2e_bloc_a import AZI, CLIENT, _card, _deschide_factura, emite_api, pregateste_firma
    f = firma_cx3
    s = f["schema"]
    pregateste_firma(patron, f)
    fac = emite_api(patron, f)
    fid, total = fac["factura_id"], fac["total"]
    zi = AZI.isoformat()
    # date-de-pornire: nota chitanței de dinainte de lotul 6, fără factura_id (codul de atunci nu-l punea); ciornă întâi (regula_linii_nota)
    nid = sql('INSERT INTO "%s".inregistrari (data, descriere, sursa, status, document_ref) VALUES (%%s, %%s, %%s, %%s, %%s) RETURNING id'
              % s, (zi, "Chitanță E2ECH 1", "casa", "ciorna", "E2ECH 1"))[0][0]
    # date-de-pornire: rândul notei chitanței vechi (5311 = 4111, toată factura)
    sql('INSERT INTO "%s".inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%%s, %%s, %%s, %%s)' % s,
        (nid, "5311", "4111", total))
    # date-de-pornire: nota chitanței vechi validată (ciornă -> rânduri -> validată), cum a rămas pe firmele dinainte de lotul 6
    sql('UPDATE "%s".inregistrari SET status = \'validata\' WHERE id = %%s' % s, (nid,))
    # date-de-pornire: chitanța veche, legată de factură și de nota ei (`chitante.factura_id`, `chitante.inregistrare_id`)
    sql('INSERT INTO "%s".chitante (serie, numar, data, factura_id, client_nume, client_cui, suma, inregistrare_id, anulata) '
        "VALUES ('E2ECH', 1, %%s, %%s, %%s, %%s, %%s, %%s, false)" % s, (zi, fid, CLIENT["#em-nume"], CLIENT["#em-cui"], total, nid))
    patron.firma(f["nume"])
    pg = patron.pg
    _card(patron, "banca", "#bk-fisier")
    detalii = "Incasare %s %s E2E C45" % (fac["numar"], CLIENT["#em-nume"])
    extras = "Data;Detalii;Suma\n%s;%s;%s\n" % (AZI.strftime("%d.%m.%Y"), detalii, ("%.2f" % float(total)).replace(".", ","))
    pg.set_input_files("#bk-fisier", {"name": "extras_e2e_c45_%d.csv" % time.time(), "mimeType": "text/csv",
                                      "buffer": extras.encode("utf-8")})
    # o singură linie: confirmarea spune „1 linie importată” (`cate`), deci se așteaptă rândul liniei în listă, nu un cuvânt din mesaj
    rand = pg.locator("#bk-lista .pf-frand", has_text=detalii).first
    rand.wait_for(timeout=30000)
    rand.locator("[data-alege]").first.click()
    pg.wait_for_selector("#bk-mesaj .stare-goala, #bk-mesaj input[data-fid]", timeout=20000)
    patron.captura("banca_alege_facturile")
    assert pg.locator("#bk-mesaj input[data-fid='%s']" % fid).count() == 0, "factura încasată cu chitanța veche e oferită deschisă"
    _deschide_factura(patron, f, fid)
    patron.captura("factura_incasata")
    assert pg.locator(_F + ".fd-stare.fd-stare-verde").count() >= 1
    assert sql('SELECT factura_id, status FROM "%s".inregistrari WHERE id = %%s' % s, (nid,)) == [(None, "validata")]
