# -*- coding: utf-8 -*-
"""Lotul 7, comanda 7.2 (Costin 17.10.2026, verbatim în DECIZII „Comanda 7.2”): declarațiile — 297, 298, 299, 300, 301, 313 — pe aplicația
din index, pe baza de TEST, pe firma nouă a fișierului (`firma_e2e`)."""
import datetime as _dt
import re
import time

from conftest import perioada_incheiata, sql
from e2e_bloc_a import AZI, CLIENT, _api, _ok, emite_api, pregateste_firma

# [lotul 10, deficiența 383 — comanda Costin 10.2 pct.1: „O declarație pe o perioadă neîncheiată se refuză la generare, cu motivul scris,
# la toate declarațiile.”] D300 (firma plătitoare lunar) se generează pe luna ÎNCHEIATĂ cea mai recentă: documentele de probă se datează
# în ea (ZI), iar declarația se cere pe ea (LUNA) — cum lucrează contabilul, după încheierea lunii
LUNA = perioada_incheiata("lunar")
ZI = LUNA.inceput.replace(day=15)
PER = "%02d/%d" % (LUNA.luna, LUNA.an)


def _nota_facturii(firma, fid):
    return [r[0] for r in sql('SELECT id FROM "%s".inregistrari WHERE factura_id = %%s ORDER BY id' % firma["schema"], (fid,))]


def _valideaza_notele(e, firma, fid):
    for nid in _nota_facturii(firma, fid):
        _ok(_api(e, "POST", "/tenants/%d/jurnal/%d/valideaza" % (firma["tenant_id"], nid), {}), "validarea notei")


def _in_coada(e, firma, tip="d300", luna=None, an=None, inlocuieste=None):
    """„Trimite în coadă” pe ruta ecranului (`POST /coada`); perioada implicită = luna încheiată (`LUNA`): pe luna în curs generarea se
    refuză (383, comanda 10.2 pct.1)."""
    corp = {"tenant_id": firma["tenant_id"], "tip": tip, "an": an or LUNA.an, "luna": luna or LUNA.luna}
    if inlocuieste:
        corp["inlocuieste"] = inlocuieste
    return _api(e, "POST", "/coada", corp)


def _curata(firma, peste):
    from e2e_bloc_c import _curata_coada
    _curata_coada(firma["tenant_id"], peste)


def _peste():
    return sql("SELECT COALESCE(max(id), 0) FROM public.declaratii_coada")[0][0]


def _deschide_coada(e, coada_id):
    e.acasa()
    e.pg.click("button.cab-card:has([data-cheie='validat'])")
    e.pg.wait_for_selector(".val-card[data-coada-ids='%d']" % coada_id, timeout=30000)
    return ".val-card[data-coada-ids='%d']" % coada_id


def test_def_297_declaratia_depasita_nu_se_depune_si_se_genereaza_din_nou(patron, firma_e2e):
    """297. D300 din „De depus” nu se regenera și nu se marca depășită după validarea unei note din perioadă; „Confirmă depunerea” rămânea.
    Pașii: o factură cu nota validată -> D300 pe luna încheiată intră în coadă; o a doua factură în aceeași lună, cu nota validată după
    -> pe rândul din coadă: „Declarația e depășită …”, fără „Confirmă depunerea”, cu „Generează din nou”; depunerea trimisă direct e
    refuzată (409, DEPASITA); „Generează din nou” -> declarația nouă intră în coadă, cea veche iese („Înlocuită de declarația generată din
    nou”)."""
    pregateste_firma(patron, firma_e2e)
    peste = _peste()
    try:
        f1 = emite_api(patron, firma_e2e, data_emitere=ZI)
        _valideaza_notele(patron, firma_e2e, f1["factura_id"])
        r = _in_coada(patron, firma_e2e)
        assert r["status"] == 200, r
        cid = r["json"]["coada_id"]
        f2 = emite_api(patron, firma_e2e, data_emitere=ZI)
        _valideaza_notele(patron, firma_e2e, f2["factura_id"])
        rand = _deschide_coada(patron, cid)
        pg = patron.pg
        txt = pg.inner_text(rand)
        patron.captura("depasita")
        assert "Declarația e depășită" in txt and "Generează din nou" in txt, txt
        assert pg.locator(rand + " .val-depune").count() == 0, "„Confirmă depunerea” pe o declarație depășită"
        refuz = _api(patron, "POST", "/coada/%d/depune" % cid, {})
        assert refuz["status"] == 409 and refuz["json"]["detail"]["cod"] == "DEPASITA", refuz
        # pe pagina principală, cardul „De depus” o numește depășită (nu „neverificată, de deschis”): numărul = declarațiile depășite
        # din coada cabinetului, citite din aceeași listă ca a cardului
        coada = _api(patron, "GET", "/coada", None)["json"]
        coada = coada.get("coada", coada) if isinstance(coada, dict) else coada
        depasite = sum(1 for c in coada if c.get("stare") in ("la_senior", "aprobata") and c.get("depasita"))
        patron.acasa()
        pg.wait_for_function("() => /depășit/.test((document.querySelector('[data-cheie=\"validat\"]') || {}).innerText || '')", timeout=60000)
        card = pg.inner_text("[data-cheie='validat']")
        patron.captura("card_depasite")
        assert re.findall(r"(\d+) depășit[ăe], de generat din nou", card) == [str(depasite)] and depasite >= 1, (card, depasite)
        rand = _deschide_coada(patron, cid)
        with pg.expect_response(lambda x: x.url.endswith("/coada/%d/regenereaza" % cid), timeout=120000) as rr:
            pg.click(rand + " .val-regenereaza")
        assert rr.value.status == 200, rr.value.text()[:400]
        nou = rr.value.json()["coada_id"]
        pg.wait_for_selector(".val-card[data-coada-ids='%d']" % nou, timeout=30000)
        patron.captura("generata_din_nou")
        assert "Declarația e depășită" not in pg.inner_text(".val-card[data-coada-ids='%d']" % nou)
        vechi = sql("SELECT stare, motiv_respingere FROM public.declaratii_coada WHERE id = %s", (cid,))[0]
        assert vechi[0] == "respinsa" and vechi[1].startswith("Înlocuită de declarația generată din nou"), vechi
    finally:
        _curata(firma_e2e, peste)


def test_def_298_declaratia_numeste_factura_fara_nota_validata_si_cu_tva_0(patron, firma_e2e):
    """298. D300 cuprindea facturi cu nota nevalidată, iar garda compara doar TVA-ul: o factură cu TVA 0 trecea nesemnalată.
    Pașii: o factură cu linia 0% (scutit fără drept de deducere), nota ei nevalidată -> Declarații -> D300 pe luna încheiată -> trimisă:
    sub confirmare, avertismentul numește factura („Declarația cuprinde 1 factură fără notă validată …: factura …, nota ei e
    ciornă, nevalidată” — formularea din 328); același text pe rândul ei din coadă, cu butonul spre notă."""
    from e2e_bloc_c import _declaratie_pas1, _trimite_si_asteapta
    pregateste_firma(patron, firma_e2e)
    peste = _peste()
    try:
        f = emite_api(patron, firma_e2e, linii=[{"descriere": "Servicii scutite E2E 298", "cantitate": 1, "um": "buc", "pret_unitar": 300.0,
                                                 "cota_tva": 0, "cota_propusa": 0, "articol_id": None, "categorie_tva": "scutit_fara_drept"}],
                     data_emitere=ZI)
        numar = sql('SELECT numar FROM "%s".facturi WHERE id = %%s' % firma_e2e["schema"], (f["factura_id"],))[0][0]
        _declaratie_pas1(patron, firma_e2e["nume"], "d300", LUNA.an, luna=LUNA.luna)
        _trimite_si_asteapta(patron)
        pg = patron.pg
        pg.wait_for_selector("#dec-gata-avert", timeout=30000)
        av = pg.inner_text("#dec-gata-avert")
        patron.captura("avertisment")
        assert "fără notă validată" in av and ("factura %s" % numar) in av and "nota ei e ciornă, nevalidată" in av, av   # [328] „ciornă”, ca în Registrul jurnal
        cid = sql("SELECT max(id) FROM public.declaratii_coada WHERE tenant_id = %s AND tip = 'd300'", (firma_e2e["tenant_id"],))[0][0]
        rand = _deschide_coada(patron, cid)
        assert ("factura %s" % numar) in pg.inner_text(rand + " .val-surse")
        assert pg.locator(rand + " .val-surse-note button").count() >= 1, "nota nevalidată are butonul spre Registrul jurnal"
        patron.captura("coada")
    finally:
        _curata(firma_e2e, peste)


def test_def_299_refuzul_spune_perioada_deschide_si_inlocuieste(patron, firma_e2e):
    """299. Refuzul „există deja o declarație activă d300 pentru perioada 25.11.2026” punea termenul, cu literă mică, fără link și fără
    „Înlocuiește”, iar mesajul dispărea singur; asistentul n-avea lista declarațiilor existente.
    Pașii: D300 pe luna încheiată în coadă -> Declarații: sub alegere, „Declarațiile firmei aflate deja în coadă” (D300 · LL/AAAA, la
    validare / de depus) -> D300 din nou -> „Există deja în coadă o declarație D300 pentru LL/AAAA, pregătită de …”, cu „Deschide declarația
    existentă” și „Înlocuiește”; după 15 secunde mesajul și titlul ferestrei sunt tot acolo -> „Înlocuiește” -> intră, cea veche iese."""
    from e2e_bloc_c import _declaratie_pas1, _deschide
    pregateste_firma(patron, firma_e2e)
    peste = _peste()
    per = PER
    try:
        f = emite_api(patron, firma_e2e, data_emitere=ZI)
        _valideaza_notele(patron, firma_e2e, f["factura_id"])
        r = _in_coada(patron, firma_e2e)
        assert r["status"] == 200, r
        cid = r["json"]["coada_id"]
        pg = patron.pg
        _deschide(patron, firma_e2e["nume"], "declaratii", "#dec-tip")
        pg.wait_for_selector(".dec-existente", timeout=20000)
        ex = pg.inner_text(".dec-existente")
        assert "D300 · " + per in ex, ex
        _declaratie_pas1(patron, firma_e2e["nume"], "d300", LUNA.an, luna=LUNA.luna)
        pg.wait_for_selector("#dec-trimite", timeout=90000)
        pg.click("#dec-trimite")
        pg.wait_for_selector("#coada-deja-inlocuieste", timeout=90000)
        # [lotul 13, 515] textul refuzului îl spune caseta „NU s-a salvat.” de lângă buton (zona lui stă ascunsă cât stă caseta); „Deschide
        # declarația existentă” / „Înlocuiește” stau în rândul de după zonă, vizibile
        from e2e_lot11_g import text_langa_butoane
        m = text_langa_butoane(pg, "#dec-coada-mesaj")["text"]
        assert pg.locator("#dec-coada-mesaj + .coada-actiuni-refuz #coada-deja-deschide").is_visible()
        assert m.startswith("Există deja în coadă o declarație D300 pentru %s, pregătită de " % per) and "25." not in m.split(",")[0], m
        cale = pg.inner_text(".fereastra:last-of-type .fereastra-fir")
        assert cale.strip(), "calea din antet (ferestrele părinte) e pe ecran"
        pg.wait_for_timeout(15000)
        assert text_langa_butoane(pg, "#dec-coada-mesaj")["text"] == m, "mesajul nu dispare singur"
        assert pg.locator("#coada-deja-inlocuieste").is_visible(), "„Înlocuiește” rămâne pe ecran până la alegere"
        assert pg.inner_text(".fereastra:last-of-type .fereastra-fir") == cale, "calea din antet rămâne"
        patron.captura("refuz_cu_drumuri")
        with pg.expect_response(lambda x: x.url.endswith("/coada") and x.request.method == "POST", timeout=120000) as rr:
            pg.click("#coada-deja-inlocuieste")
        assert rr.value.status == 200, rr.value.text()[:300]
        assert sql("SELECT stare FROM public.declaratii_coada WHERE id = %s", (cid,))[0][0] == "respinsa"
        patron.captura("inlocuita")
    finally:
        _curata(firma_e2e, peste)


def test_def_300_d390_datorat_in_luna_deschisa_cu_factura_ic_si_fara_d112_fara_salariati(patron, firma_e2e):
    """300. D390 al lunii lipsea din „Datorate” deși exista o prestare de servicii UE în lună; D112 apărea fără salariați.
    Pașii: o factură de servicii către un client din Irlanda (0%, prestare cu locul în afara României) în luna curentă -> Declarații:
    în „Datorate de firmă” apare D390 pe luna curentă; D112 nu apare (firma n-are salariați)."""
    from e2e_bloc_c import _deschide
    pregateste_firma(patron, firma_e2e)
    from e2e_bloc_a import PRODUS
    corp = {"linii": [{"descriere": PRODUS, "cantitate": 1, "um": "buc", "pret_unitar": 1000.0, "cota_tva": 0,
                       "cota_propusa": 0, "articol_id": None, "categorie_tva": "serviciu_extern"}],
            "tert_nume": "Client Irlanda E2E Ltd", "tert_cui": "IE9999999ZZ", "tert_adresa": "1 Grand Canal Square", "tert_oras": "Dublin",
            "moneda": "RON", "tert_tara": "IE", "tip_operatiune": "normal", "bon_fiscal_nr": None, "bon_fiscal_data": None,
            "data_emitere": AZI.isoformat(), "data_scadenta": (AZI + _dt.timedelta(days=30)).isoformat(), "tip": "factura"}
    _ok(_api(patron, "POST", "/tenants/%d/facturi/emite" % firma_e2e["tenant_id"], corp), "factura IC")
    pg = patron.pg
    _deschide(patron, firma_e2e["nume"], "declaratii", "#dec-tip")
    datorate = pg.eval_on_selector_all("#dec-tip optgroup:first-of-type option", "(os) => os.map((o) => o.textContent)")
    patron.captura("datorate")
    luna = "%02d/%d" % (AZI.month, AZI.year)
    assert any(t.startswith("D390 · " + luna) for t in datorate), datorate   # CF art.325 alin.(1) lit.c — și serviciile IC
    assert not any(t.startswith("D112 · ") for t in datorate), datorate


def test_def_301_alte_declaratii_pliata_fara_cele_ale_persoanelor_fizice(patron, firma_e2e):
    """301. „Alte declarații” cuprindea declarațiile persoanelor fizice (D204, D212, D216, D230; D200, D201, D221, D223 au ieșit din aplicație, 660). Decizia: pliată,
    deschisă la cerere, numai declarațiile pe care un SRL le poate datora.
    Pașii: Declarații pe SRL: selectorul arată numai „Datorate de firmă”; „Arată alte declarații” -> apare grupa „Alte declarații”, fără
    niciuna dintre declarațiile persoanelor fizice."""
    from e2e_bloc_c import _deschide
    pregateste_firma(patron, firma_e2e)
    pg = patron.pg
    _deschide(patron, firma_e2e["nume"], "declaratii", "#dec-tip")
    grupe = pg.eval_on_selector_all("#dec-tip optgroup", "(gs) => gs.map((g) => g.label)")
    if grupe:
        assert grupe[0].startswith("Datorate de firmă (") and "Alte declarații" not in grupe, grupe
        patron.captura("pliata")
        pg.click("#dec-alte")
        pg.wait_for_function("() => [...document.querySelectorAll('#dec-tip optgroup')].some((g) => g.label === 'Alte declarații')",
                             timeout=10000)
    tipuri = pg.eval_on_selector_all("#dec-tip option", "(os) => os.map((o) => o.value)")
    patron.captura("deschisa")
    for t in ("d204", "d212", "d216", "d230"):
        assert t not in tipuri, (t, tipuri)
    assert "d300" in tipuri and "d101" in tipuri, tipuri


def test_def_313_coada_titlul_urmeaza_cardul_renuntarea_fara_motiv_si_notele_numite(patron, firma_e2e):
    """313. Cardul devenea „De depus”, fereastra rămânea „De validat”; la propria declarație „Renunță” deschidea „Respinge declarația” cu
    motiv obligatoriu; butonul era „Trimite în coadă” și pentru cine depune direct; „1 notă(e) nevalidată(e)” nu numea nota.
    Pașii (validarea în doi oprită, administratorul depune): Declarații -> D300: butonul spune „Pune în „De depus” →”; trimisă, cu o notă
    bancară nevalidată în lună: avertismentul o numește („nota din …”), fără „notă(e)”; cardul cozii și fereastra lui au același titlu;
    „Renunță” pe declarația proprie -> „Renunți la declarație”, fără motiv -> declarația iese din coadă."""
    from e2e_bloc_c import _declaratie_pas1
    pregateste_firma(patron, firma_e2e)
    peste = _peste()
    tid, sch = firma_e2e["tenant_id"], firma_e2e["schema"]
    try:
        f = emite_api(patron, firma_e2e, data_emitere=ZI)
        _valideaza_notele(patron, firma_e2e, f["factura_id"])
        nid = sql('INSERT INTO "%s".inregistrari (data, descriere, status, document_ref) VALUES (%%s, \'Comision E2E 313\', \'ciorna\', '
                  '\'EXTRAS E2E 313\') RETURNING id' % sch, (ZI.isoformat(),))[0][0]
        sql('INSERT INTO "%s".inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%%s, \'627\', \'5121\', 100)' % sch,
            (nid,))
        _declaratie_pas1(patron, firma_e2e["nume"], "d300", LUNA.an, luna=LUNA.luna)
        pg = patron.pg
        pg.wait_for_selector("#dec-trimite", timeout=90000)
        pg.wait_for_function("() => (document.querySelector('#dec-trimite') || {}).dataset && document.querySelector('#dec-trimite').dataset.eticheta",
                             timeout=20000)
        assert pg.inner_text("#dec-trimite").strip() == "Pune în „De depus” →", pg.inner_text("#dec-trimite")
        pg.click("#dec-trimite")
        pg.wait_for_selector("#dec-gata-avert", timeout=90000)
        av = pg.inner_text("#dec-gata-avert")
        assert "nota din %s — EXTRAS E2E 313" % ZI.strftime("%d.%m.%Y") in av and "notă(e)" not in av, av   # data notei, dată de test
        patron.captura("notele_numite")
        cid = sql("SELECT max(id) FROM public.declaratii_coada WHERE tenant_id = %s AND tip = 'd300'", (tid,))[0][0]
        patron.acasa()
        card = pg.inner_text("button.cab-card:has([data-cheie='validat']) .cab-card-titlu").strip()
        pg.click("button.cab-card:has([data-cheie='validat'])")
        pg.wait_for_selector(".fereastra:last-of-type #val-titlu", timeout=30000)
        assert pg.inner_text(".fereastra:last-of-type #val-titlu").strip() == card, card
        rand = ".val-card[data-coada-ids='%d']" % cid
        pg.wait_for_selector(rand, timeout=30000)
        pg.click(rand + " .val-respinge")
        pg.wait_for_selector("text=Renunți la declarație", timeout=10000)
        patron.captura("renunta_fara_motiv")
        pg.click("text=Renunță la declarație")
        for _ in range(30):
            if sql("SELECT stare FROM public.declaratii_coada WHERE id = %s", (cid,))[0][0] == "respinsa":
                break
            time.sleep(1)
        assert sql("SELECT stare, motiv_respingere FROM public.declaratii_coada WHERE id = %s", (cid,))[0] == (
            "respinsa", "Retrasă din coadă de cel care a pregătit-o.")
    finally:
        sql('DELETE FROM "%s".inregistrari WHERE descriere = \'Comision E2E 313\' AND status = \'ciorna\'' % sch)
        _curata(firma_e2e, peste)
