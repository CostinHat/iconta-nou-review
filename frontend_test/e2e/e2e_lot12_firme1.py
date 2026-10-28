# -*- coding: utf-8 -*-
"""Lotul 12, comanda Costin 12.1 (verbatim în DECIZII), pachetul firme1 — Bancă, Casă, Raport Z, NIR, Închidere lună.

  479 (grav) — Bancă: „Linie dublă importată; notă 5121=5121 propusă.”
  478 — Bancă: „Extras .xlsx valid refuzat.”
  480 — Bancă: „Încasare cu cod TVA străin și «factura F1A7» în descriere rămâne fără potrivire automată.”
  489 — Bancă: „Ecranul nu spune că acceptă și MT940.” (fost N3)
  481 (grav) — Casă ← Raport Z: „Numerarul din Z nu intră în registrul de casă.”
  456 (a) — Casă: chitanța se emite și pentru încasarea în numerar fără factură (avansul), cu seria firmei și PDF.
  483 (grav) — Închidere lună: „Deblocarea lunii imposibilă: fără câmp de motiv.”
  473 — Raport Z: „La firmă de comerț: «mâncare», «alcool, sucuri», «Consum pe rețetă».”
  474 — Raport Z: „Z validat cu descărcare parțială din stoc, fără avertisment.”
  476 (grav) — NIR: „TVA transport cu factură pe 4428 în loc de 4426.”

Pașii contabilului pe aplicația din index, pe baza de TEST, pe o firmă NOUĂ de test (`firma_e2e` + `pregateste_firma`: SRL de comerț, CAEN
4711, plătitor de TVA, stoc cantitativ-valoric, seria chitanțelor E2ECH). DATE DE PORNIRE scrise direct, declarate la fiecare test: rândul
învățat înainte de reparație (479), luna blocată (483), o rețetă la firma de comerț (473), NIR-ul pe ruta formularului (476). Clientul
DANTE INTERNATIONAL SA, CUI 14399840; codurile de TVA străine ATU13585627 / DE136695976 — cifra de control verificată.

Temei: OMFP 1802/2014 (funcțiunea contului 512; 4426; 408), CF art.299 alin.(1) lit.a, CF art.291 alin.(2) lit.n, OMFP 2634/2015 anexa 2
(Registrul de casă 14-4-7A, Chitanța 14-4-1) — citate în testele pytest ale pachetului (`core/test_lot12_firme1_*.py`)."""
import datetime as _dt
import io
import time

import pytest

from conftest import sql
from e2e_bloc_a import AZI, _api, _card, _ok, articol_in_stoc, emite_api, pregateste_firma

_AT = "ATU13585627"


def _bani(v):
    s = "%.2f" % float(v)
    i, z = s.split(".")
    return "{:,}".format(int(i)).replace(",", ".") + "," + z


def _luna_trecuta():
    p = AZI.replace(day=1) - _dt.timedelta(days=1)
    return p.year, p.month


def _banca(e, firma):
    e.firma(firma["nume"])
    _card(e, "banca", "#bk-fisier")


def _incarca(pg, nume, mime, octeti):
    pg.evaluate("() => { const m = document.querySelector('#bk-mesaj'); if (m) m.innerHTML = ''; }")
    pg.set_input_files("#bk-fisier", {"name": nume, "mimeType": mime, "buffer": octeti})
    pg.wait_for_function("() => { const t = document.querySelector('#bk-mesaj').innerText; return t && !t.includes('Se cite'); }",
                         timeout=30000)
    return pg.inner_text("#bk-mesaj")


def _lista_cu(pg, text):
    """Lista liniilor DUPĂ ce a ajuns pe ecran rândul cu `text`. Ecranul scrie mesajul importului, apoi recere lista (`incarca()`,
    neașteptat): citită imediat după mesaj, lista e încă cea dinainte de import (prins la rularea din 23.10.2026, 251: lista avea numai
    liniile testelor anterioare). Firma e una pe fișier, deci rândurile testelor de dinainte sunt și ele în listă."""
    pg.locator("#bk-lista tbody.tn-nota", has_text=text).first.wait_for(timeout=20000)
    return pg.inner_text("#bk-lista")


def _mt940(zi, suma, descriere, ref="NONREF"):
    d = zi.strftime("%y%m%d")
    return (":20:E2E%s\n:25:RO49AAAA1B31007593840000\n:28C:00010/001\n:60F:C%sRON1000,00\n:61:%s%sC%sNTRF%s\n:86:%s\n:62F:C%sRON%s\n" % (
        d, d, d, zi.strftime("%m%d"), ("%.2f" % suma).replace(".", ","), ref, descriere, d,
        ("%.2f" % (1000 + suma)).replace(".", ","))).encode("utf-8")


# ── 489 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _text_din_card(pg, card, sel):
    """[lotul 14, 687] Ce stă într-un card-rezumat al ferestrei (fereastra lui): deschide cardul, citește elementul, se întoarce la fereastra de dedesubt."""
    pg.click("[data-card='%s']" % card)
    pg.wait_for_selector(".fereastra:last-of-type " + sel, timeout=20000)
    text = pg.inner_text(".fereastra:last-of-type " + sel)
    pg.click(".fereastra:last-of-type .nav-sageata.nav-inapoi")
    pg.wait_for_selector("#bk-fisier", timeout=20000)
    return text


def test_def_489_ecranul_banca_spune_ca_accepta_mt940(patron, firma_e2e):
    """489. Pașii: firma -> „Bancă”: ecranul spune, pe bănci, formatele acceptate — MT940 (.sta, .940, .txt), ING, alt tabel — iar fereastra
    de alegere a fișierului primește și fișierele MT940."""
    pregateste_firma(patron, firma_e2e)
    _banca(patron, firma_e2e)
    pg = patron.pg
    formate = _text_din_card(pg, "formate", "#bk-formate")   # [lotul 14, 687] formatele stau în cardul lor
    patron.captura("formatele")
    assert "MT940" in formate and ".sta" in formate and ".940" in formate, formate
    acc = pg.get_attribute("#bk-fisier", "accept")
    assert all(x in acc for x in (".sta", ".940", ".txt", ".xlsx", ".csv")), acc


# ── 479 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_479_extrasul_in_tabel_dupa_mt940_nu_dubleaza_linia_si_nu_propune_5121_5121(patron, firma_e2e):
    """479. Pașii lui Costin: „Bancă” -> extrasul MT940 al zilei (încasarea de 479,00 lei, cu contul băncii) -> apoi extrasul aceleiași zile
    în tabel (CSV, fără cont), cu aceeași încasare. Date de pornire: rândul învățat înainte de reparație pe contul băncii (5121) pentru
    descrierea încasării (așa învăța validarea încasării: „debitul primei linii”). Înainte: a doua linie, la contat, cu „Contează
    5121=5121”. Acum: mesajul spune că linia pare deja importată și e pusă deoparte; rândul ei e „Ignorată”, cu motivul și «readu»;
    nicăieri „5121=5121”."""
    pregateste_firma(patron, firma_e2e)
    s = firma_e2e["schema"]
    desc = "Incasare CLIENT E2E479 contravaloare marfa"
    from core import ai_incredere as _ai
    # date-de-pornire: rândul învățat de codul de dinainte de reparație (5121 pentru descrierea încasării — „debitul primei linii”)
    sql('INSERT INTO "%s".ai_corectii (context, cont_propus, cont_final, corectat) VALUES (%%s, %%s, %%s, false)' % s,
        (_ai.normalizeaza(desc), "5121", "5121"))
    zi = AZI - _dt.timedelta(days=1)
    _banca(patron, firma_e2e)
    pg = patron.pg
    m1 = _incarca(pg, "extras_e2e479_%d.sta" % time.time(), "text/plain", _mt940(zi, 479.0, desc))
    assert "1 linie importată" in m1, m1
    csv = ("Data;Detalii;Debit;Credit\n%s;%s;;479,00\n" % (zi.strftime("%d.%m.%Y"), desc)).encode("utf-8")
    m2 = _incarca(pg, "extras_e2e479_%d.csv" % time.time(), "text/csv", csv)
    patron.captura("dublura_pusa_deoparte")
    assert "1 linie pare deja importată din alt extras" in m2 and "pusă deoparte, ca «Ignorată»" in m2, m2
    pg.wait_for_function("() => document.querySelectorAll('#bk-lista tbody.tn-nota').length >= 2", timeout=20000)
    lista = pg.inner_text("#bk-lista")
    assert "5121=5121" not in lista and "5121 = 5121" not in lista, lista
    # [lotul 13, 624] linia pusă deoparte stă grupată, în tabelul „Linii puse deoparte”; motivul și „Readu” sunt în detaliul ei (clic pe rând)
    rand = pg.locator("#bk-deoparte tbody.tn-nota", has_text=desc)
    assert rand.count() == 1, lista
    rand.locator(".tn-deschide").click()
    t = " ".join(rand.inner_text().split())
    assert "Ignorată" in t and "pare aceeași mișcare" in t and "Readu" in t and "+479,00" in t, t
    # nota propusă are și suma, modulul și versiunea regulilor (`core/banca._nota`): aici contează perechea de conturi
    assert sql("SELECT status, nota_propusa->>'debit', nota_propusa->>'credit' FROM \"%s\".extras_linii WHERE suma = 479 ORDER BY id" % s) == [
        ("nou", "5121", "4111"), ("ignorat", None, None)]


# ── 478 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_478_extrasul_xlsx_cu_date_excel_se_importa(patron, firma_e2e):
    """478. Pașii: „Bancă” -> extrasul .xlsx (antet Data / Detalii / Debit / Credit; data scrisă de Excel ca dată, sumele numere). Înainte:
    „nu s-a putut citi extrasul: Nu s-au găsit tranzacții în extras.” Acum: 2 linii importate, cu data și suma lor pe rânduri."""
    from openpyxl import Workbook
    pregateste_firma(patron, firma_e2e)
    zi = AZI - _dt.timedelta(days=2)
    wb = Workbook()
    ws = wb.active
    for r in (["Extras de cont E2E478"], ["Data", "Detalii", "Debit", "Credit"],
              [_dt.datetime(zi.year, zi.month, zi.day), "Incasare E2E478 client", None, 478.25],
              [_dt.datetime(zi.year, zi.month, zi.day), "Comision E2E478", 4.78, None]):
        ws.append(r)
    b = io.BytesIO()
    wb.save(b)
    _banca(patron, firma_e2e)
    pg = patron.pg
    m = _incarca(pg, "extras_e2e478_%d.xlsx" % time.time(),
                 "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", b.getvalue())
    patron.captura("xlsx_importat")
    assert "2 linii importate" in m and "nu s-a putut citi" not in m, m
    lista = _lista_cu(pg, "Comision E2E478")
    # [lotul 13, 624] tabelul de note: suma în coloana „Suma (lei)”, cu semnul, pe rândul liniei (data · suma · descrierea)
    zr = zi.strftime("%d.%m.%Y")
    assert ("%s\t+478,25\tIncasare E2E478 client" % zr) in lista and ("%s\t−4,78\tComision E2E478" % zr) in lista, lista   # AZI-dat-de-test


# ── 480 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_480_incasarea_cu_cod_tva_strain_si_numarul_facturii_se_potriveste(patron, firma_e2e):
    """480. Pașii: factura emisă (2 × 150 + TVA = 363,00 lei) -> „Bancă” -> extrasul cu încasarea de 363,00 lei, descrierea „… ATU13585627
    factura <seria><numărul>” (codul de TVA al altui stat, numărul facturii lipit de serie). Înainte: „● Fără potrivire” (fără CUI
    românesc în descriere). Acum: „● Potrivire exactă” pe factura ei, cu „Contează”."""
    pregateste_firma(patron, firma_e2e)
    f = emite_api(patron, firma_e2e)
    s = firma_e2e["schema"]
    total = sql('SELECT COALESCE(total_lei, total) FROM "%s".facturi WHERE id = %%s' % s, (f["factura_id"],))[0][0]
    csv = ("Data;Detalii;Debit;Credit\n%s;Incasare GMBH %s factura %s;;%s\n" % (
        AZI.strftime("%d.%m.%Y"), _AT, f["numar"], ("%.2f" % total).replace(".", ","))).encode("utf-8")
    _banca(patron, firma_e2e)
    pg = patron.pg
    _incarca(pg, "extras_e2e480_%d.csv" % time.time(), "text/csv", csv)
    rand = pg.locator("#bk-lista tbody.tn-nota", has_text=_AT)
    rand.wait_for(timeout=20000)
    rand.locator(".tn-deschide").click()   # [lotul 13, 624] motivul potrivirii e în detaliul liniei
    t = " ".join(rand.inner_text().split())
    patron.captura("potrivire_dupa_numar")
    assert "Potrivire exactă" in t and "numărul facturii din descriere" in t, t
    assert rand.locator("[data-cont]").count() == 1, t


# ── 481 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_481_numerarul_din_z_intra_in_registrul_de_casa(patron, firma_e2e):
    """481. Pașii: „Raport Z” -> data de azi, casa 8000000481, Z nr. 0481, total 21% 181,00, numerar 150,00, card 31,00, 4 bonuri ->
    „Generează notă” -> înapoi -> „Casă”: registrul lunii are rândul raportului Z, +150,00 lei (numai numerarul), iar soldul final îl
    cuprinde."""
    pregateste_firma(patron, firma_e2e)
    patron.firma(firma_e2e["nume"])
    pg = patron.pg
    _card(patron, "raportz", "#z-salveaza")
    for sel, v in (("#z-data", AZI.isoformat()), ("#z-nui", "8000000481"), ("#z-nr", "0481"), ("#z-21", "181"), ("#z-num", "150"),
                   ("#z-card", "31"), ("#z-bonuri", "4")):
        pg.fill(sel, v)
    pg.click("#z-salveaza")
    pg.wait_for_function("() => document.querySelector('#z-rezultat').innerText.includes('5311')", timeout=30000)
    pg.click(".nav-sageata.nav-inapoi")
    _card(patron, "casa", "#c-sold-final")
    pg.wait_for_timeout(500)
    rand = pg.locator(".fereastra:last-of-type tbody.tn-nota", has_text="0481")
    t = rand.first.inner_text()
    patron.captura("registrul_cu_z")
    # OMFP 2634/2015 14-4-1: raportul Z e documentul încasărilor zilnice în numerar -> rând în registrul de casă (14-4-7A)
    assert "150,00" in t and "notă din raportul Z" in t, t
    # firma nouă n-are altă mișcare de casă: soldul final e numerarul Z-ului
    assert pg.inner_text("#c-sold-final").startswith(_bani(150)), pg.inner_text("#c-sold-final")


# ── 456 (a) ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_456_avansul_de_la_client_in_numerar_primeste_chitanta(patron, firma_e2e):
    """456 (a). Pașii: „Casă” -> „+ Dispoziție nouă”: încasare de la client, 456,00 lei, CUI-ul clientului, fără factură -> „Adaugă”.
    Mesajul spune „Chitanța E2ECH nr. … a fost emisă”; rândul are documentul chitanței și „PDF chitanță”, fără „fără chitanță”."""
    pregateste_firma(patron, firma_e2e)
    s = firma_e2e["schema"]
    patron.firma(firma_e2e["nume"])
    pg = patron.pg
    _card(patron, "casa", "#c-toggle")
    pg.click("#c-toggle")
    pg.fill("#c-data", AZI.isoformat())
    pg.select_option("#c-cat", "incasare_client")
    pg.fill("#c-suma", "456")
    pg.fill("#c-cui", "14399840")
    pg.dispatch_event("#c-campuri", "change")
    pg.wait_for_timeout(800)
    pg.click("#c-adauga")
    pg.wait_for_function("() => [...document.querySelectorAll('.fereastra')].pop().innerText.includes('a fost emisă')", timeout=30000)
    text = patron.fereastra()
    patron.captura("chitanta_avans")
    (serie, nr), = sql('SELECT serie, numar FROM "%s".chitante WHERE factura_id IS NULL AND suma = 456' % s)
    assert serie == "E2ECH" and ("Chitanța %s" % serie) in text, text
    rand = pg.locator(".fereastra:last-of-type tbody.tn-nota", has_text="%s-%s" % (serie, nr))
    t = rand.first.inner_text()
    # [lotul 13, 675] „PDF chitanță” e pe fiecare rând (în detaliu); activ numai unde chitanța există
    assert "fără chitanță" not in t and rand.first.locator("[data-chpdf]:not([aria-disabled='true'])").count() == 1, t


# ── 483 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_483_deblocarea_lunii_cere_motivul_si_se_face(patron, firma_e2e):
    """483. Pașii: „Închidere lună” -> „← luna” (luna trecută, blocată — date de pornire) -> „Deblochează luna”: sub buton apare câmpul
    „Motivul deblocării lunii …” -> „Deblochează luna” fără motiv -> lângă câmp „Scrie motivul deblocării” -> motivul scris ->
    „Deblochează luna” -> „Luna … e deblocată. Motivul („…”) e în istoricul perioadei.”; starea „Luna e deschisă”, butonul „Blochează
    luna”; în istoric: redeschisă, cu motivul. Înainte: cererea pleca fără motiv și serverul o refuza mereu."""
    pregateste_firma(patron, firma_e2e)
    s = firma_e2e["schema"]
    an, luna = _luna_trecuta()
    # date-de-pornire: luna trecută blocată (proba e deblocarea); ciornele testelor de dinainte (479) o pot opri la poarta închiderii
    sql('INSERT INTO "%s".perioade_blocate (an, luna) VALUES (%%s, %%s) ON CONFLICT DO NOTHING' % s, (an, luna))
    patron.firma(firma_e2e["nume"])
    pg = patron.pg
    _card(patron, "inchidere", "#il-prev")
    pg.click("#il-prev")
    pg.wait_for_function("() => (document.querySelector('#il-lock') || {}).textContent === 'Deblochează luna'", timeout=25000)
    pg.click("#il-lock")
    pg.wait_for_selector("#bl-motiv", timeout=10000)
    pg.click("#bl-deblocheaza")
    pg.wait_for_selector('.msg-eroare[data-camp="bl-motiv"]', timeout=10000)
    assert "Scrie motivul deblocării" in pg.inner_text('.msg-eroare[data-camp="bl-motiv"]')
    assert sql('SELECT count(*) FROM "%s".perioade_blocate WHERE an = %%s AND luna = %%s' % s, (an, luna)) == [(1,)]
    patron.captura("motivul_cerut")
    motiv = "corectez factura E2E483, înregistrată cu altă dată"
    pg.fill("#bl-motiv", motiv)
    pg.click("#bl-deblocheaza")
    pg.wait_for_function("() => (document.querySelector('#il-mesaj') || {}).innerText && "
                         "document.querySelector('#il-mesaj').innerText.includes('e deblocată')", timeout=25000)
    patron.captura("luna_deblocata")
    assert motiv in pg.inner_text("#il-mesaj")
    assert pg.inner_text("#il-lock") == "Blochează luna" and "Luna e deschisă" in pg.inner_text("#il-stare-perioada")
    assert sql('SELECT count(*) FROM "%s".perioade_blocate WHERE an = %%s AND luna = %%s' % s, (an, luna)) == [(0,)]
    ist = _ok(_api(patron, "GET", "/tenants/%d/perioade-blocate/istoric?an=%d&luna=%d" % (firma_e2e["tenant_id"], an, luna)), "istoric")
    assert motiv in str(ist), ist


# ── 473 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_473_z_la_comert_cotele_neutre_chiar_cu_retete(patron, firma_e2e):
    """473. Pașii: firma de comerț (CAEN 4711) care are o rețetă (adăugată pe ruta ecranului Rețete, cu un ingredient) -> „Raport Z”: „Total 11%”,
    „Total 21%”, fără „(mâncare)” / „(alcool, sucuri)” (CF art.291 alin.(2) lit.n descrie restaurantul, nu comerțul). Apoi CAEN 5610
    (restaurant): etichetele apar."""
    pregateste_firma(patron, firma_e2e)
    art = articol_in_stoc(patron, firma_e2e)
    _ok(_api(patron, "POST", "/tenants/%d/retete" % firma_e2e["tenant_id"],
             {"denumire": "Reteta E2E473", "pret_fara_tva": 10, "linii": [{"articol_id": art, "cantitate": 1}]}), "rețeta")
    patron.firma(firma_e2e["nume"])
    pg = patron.pg
    _card(patron, "raportz", "#z-salveaza")
    e11, e21 = pg.inner_text("#z-et-11"), pg.inner_text("#z-et-21")
    patron.captura("comert_cote_neutre")
    assert (e11.strip(), e21.strip()) == ("Total 11%", "Total 21%"), (e11, e21)
    pregateste_firma(patron, firma_e2e, caen="5610")
    patron.firma(firma_e2e["nume"])
    _card(patron, "raportz", "#z-salveaza")
    assert "mâncare" in pg.inner_text("#z-et-11") and "alcool, sucuri" in pg.inner_text("#z-et-21")
    pregateste_firma(patron, firma_e2e)   # înapoi la comerț, pentru testele de după


# ── 474 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_474_z_descarcat_partial_cere_confirmarea_cu_cifrele(patron, firma_e2e):
    """474. Pașii: Z de 242,00 lei (21%), numerar -> „Raport Z”, la Z: articolul din stoc, 1 bucată -> „Ieșire pe articol” -> „Validează
    raportul Z”: înainte de validare, caseta spune „Ai descărcat din stoc 1 ieșire la cost 12,50 lei, pentru vânzări de 200,00 lei fără TVA
    pe acest Z (adaos 1500%)…” și cere „Da, validează raportul Z”; „Renunță” lasă Z-ul nevalidat; confirmat -> „e validat”."""
    pregateste_firma(patron, firma_e2e)
    tid, s = firma_e2e["tenant_id"], firma_e2e["schema"]
    art = articol_in_stoc(patron, firma_e2e)
    r = _ok(_api(patron, "POST", "/tenants/%d/horeca/raport-z" % tid, {"data": AZI.isoformat(), "nui": "8000000474", "nr_raport": "0474",
                                                                       "nr_bonuri": 2, "total_11": 0, "total_21": 242, "numerar": 242,
                                                                       "card": 0}), "raport Z")
    zid = r["nota_id"]
    patron.firma(firma_e2e["nume"])
    pg = patron.pg
    _card(patron, "raportz", "#z-salveaza")
    pg.wait_for_selector("#zd-art-%d" % zid, timeout=25000)
    pg.select_option("#zd-art-%d" % zid, str(art))
    pg.fill("#zd-cant-%d" % zid, "1")
    pg.click(".zd-iesire[data-z='%d']" % zid)
    pg.wait_for_selector("#zd-val-%d" % zid, timeout=25000)
    pg.click("#zd-val-%d" % zid)
    pg.wait_for_selector("#caseta-atentie-activa #ca-ok", timeout=10000)
    caseta = pg.inner_text("#caseta-atentie-activa")
    patron.captura("confirmarea_cu_cifrele")
    assert "Ai descărcat din stoc 1 ieșire la cost 12,50 lei, pentru vânzări de 200,00 lei fără TVA pe acest Z" in caseta, caseta
    assert "dacă au mai ieșit și alte articole, descarcă-le înainte de validare" in caseta, caseta
    pg.click("#caseta-atentie-activa #ca-nu")
    assert sql('SELECT status FROM "%s".inregistrari WHERE id = %%s' % s, (zid,)) == [("ciorna",)]
    pg.click("#zd-val-%d" % zid)
    pg.click("#caseta-atentie-activa #ca-ok")
    pg.wait_for_function("() => document.querySelector('#z-descarcare').innerText.includes('e validat')", timeout=25000)
    assert sql('SELECT status FROM "%s".inregistrari WHERE id = %%s' % s, (zid,)) == [("validata",)]


# ── 476 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_476_tva_transportului_facturat_e_pe_4426(patron, firma_e2e):
    """476. Pașii: NIR fără factura mărfii (factura furnizorului nesosită), 10 × 50 lei, transport 100 lei cu factura transportatorului
    (cont 401), TVA transport 21% — pe ruta formularului „Salvează NIR” (date de pornire) -> „Stocuri” -> „Deschide NIR-ul”: notele
    NIR-ului au 4426 = 401 · 21,00 (TVA-ul transportului facturat), marfa 4428.01 = 408 · 105,00; niciun 4428.01 = 401."""
    pregateste_firma(patron, firma_e2e)
    tid = firma_e2e["tenant_id"]
    r = _ok(_api(patron, "POST", "/tenants/%d/stocuri/nir" % tid, {
        "numar": "E2E476", "data": AZI.isoformat(), "furnizor": "DANTE INTERNATIONAL SA", "cui": "14399840",
        "linii": [{"denumire": "Marfa E2E476", "articol_nou": True, "cantitate": 10, "pret_achizitie": 50, "cota_tva": 21}],
        "transport": 100, "cota_tva_transport": 21, "cont_transport": "401", "factura_sosita": False}), "NIR")
    assert "eroare" not in r, r
    patron.firma(firma_e2e["nume"])
    pg = patron.pg
    _card(patron, "stocuri", "[data-card='nir']")
    # [lotul 14, 687] NIR-urile lunii stau în cardul „NIR-urile lunii”: contabilul îl deschide, apoi apasă „Deschide NIR-ul”
    pg.click("[data-card='nir']")
    pg.wait_for_selector(".fereastra:last-of-type .nir-deschide", timeout=25000)
    pg.locator(".nir-deschide[data-numar='E2E476']").click()
    pg.wait_for_selector("#nir-detaliu-linii", timeout=25000)
    text = patron.fereastra()
    patron.captura("notele_nir")
    linii = [ln.split("\t") for ln in text.splitlines() if "\t" in ln]
    perechi = {(l[1].strip(), l[2].strip(), l[3].strip()) for l in linii if len(l) >= 4}
    assert ("4426", "401", "21,00") in perechi and ("4428.01", "408", "105,00") in perechi, text
    assert not any(d == "4428.01" and c == "401" for d, c, _s in perechi), text


# ── generatoarele fișierelor pentru dovada pe firmele de test (`frontend_test/dovada/dovezi_lot12_firme1.json`, pasul „incarca”) ────
def fisier_xlsx_478(zi_iso):
    """Extrasul .xlsx al dovezii 478: data ca dată Excel, sumele ca numere (două mișcări mici, evident de probă)."""
    from openpyxl import Workbook
    zi = _dt.date.fromisoformat(zi_iso)
    wb = Workbook()
    ws = wb.active
    for r in (["Data", "Detalii", "Debit", "Credit"], [_dt.datetime(zi.year, zi.month, zi.day), "Proba 478 incasare xlsx", None, 4.78],
              [_dt.datetime(zi.year, zi.month, zi.day), "Proba 478 comision xlsx", 0.47, None]):
        ws.append(r)
    b = io.BytesIO()
    wb.save(b)
    return b.getvalue()


def fisier_csv_480(zi_iso, numar_factura, suma):
    """Extrasul CSV al dovezii 480: încasarea cu codul de TVA străin și numărul facturii în descriere."""
    zi = _dt.date.fromisoformat(zi_iso)
    return ("Data;Detalii;Debit;Credit\n%s;Proba 480 incasare %s factura %s;;%s\n" % (
        zi.strftime("%d.%m.%Y"), _AT, numar_factura, str(suma).replace(".", ","))).encode("utf-8")


# ── C118 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
AMEF_F1 = "/home/costin/ghid_incoming/lot12_fisiere_proba/F1_raport_Z_AMEF_2026-10-22.xml"


def test_def_c118_z_importat_din_amef_pe_luna_trecuta_se_descarca_din_ecran(patron, firma_e2e):
    """C118 (găsită de pachetul pilot). Pașii: „Raport Z” -> „Import fișier AMEF” cu raportul Z real al F1 (lot12_fisiere_proba), mutat pe
    luna trecută (date de pornire: numai data din identificatorii mesajului). Înainte: secțiunea „Descărcarea mărfii vândute” rămânea pe
    luna curentă, fără Z-ul importat — nu se putea descărca, deci nici valida (stoc cantitativ-valoric). Acum: secțiunea trece pe luna
    Z-ului, cu rândul lui și câmpurile descărcării."""
    pregateste_firma(patron, firma_e2e)
    an, luna = _luna_trecuta()
    xml = open(AMEF_F1, encoding="utf-8").read()
    assert "20261022" in xml, "fișierul de probă s-a schimbat"
    xml = xml.replace("20261022", "%04d%02d22" % (an, luna))
    patron.firma(firma_e2e["nume"])
    pg = patron.pg
    _card(patron, "raportz", "#z-salveaza")
    pg.set_input_files("#z-amef", {"name": "Z_AMEF_c118.xml", "mimeType": "application/xml", "buffer": xml.encode("utf-8")})
    pg.wait_for_function("() => document.querySelector('#z-amef-msg').innerText.includes('Importat')", timeout=30000)
    eticheta = "%02d/%04d" % (luna, an)
    pg.wait_for_function("(e) => (document.querySelector('#z-descarcare') || {}).innerText && "
                         "document.querySelector('#z-descarcare').innerText.includes(e) && "
                         "document.querySelectorAll('#z-descarcare [data-z]').length > 0", arg=eticheta, timeout=30000)
    patron.captura("descarcarea_pe_luna_z")
    # Z-ul importat, după data lui: firma e una pe fișier, iar `rapoarte_z_amef` are și Z-urile din formular ale testelor 481 / 474
    # (`repo_contabilitate.adauga_z_amef`, „același rând pe ambele rute”)
    (zid,), = sql('SELECT i.id FROM "%s".inregistrari i JOIN "%s".rapoarte_z_amef z ON z.inregistrare_id = i.id WHERE i.data = %%s' % (
        firma_e2e["schema"], firma_e2e["schema"]), (_dt.date(an, luna, 22),))
    assert pg.locator("#zd-art-%d" % zid).count() == 1 and pg.locator(".zd-iesire[data-z='%d']" % zid).count() == 1


# ── 251 (clasa, extrasul bancar) / C121 ──────────────────────────────────────────────────────────────────────────────────────────
def test_def_251_extrasul_csv_windows_1250_pastreaza_diacriticele(patron, firma_e2e):
    """251 (clasa, pe Bancă). Pașii: „Bancă” -> extrasul CSV salvat din Excel în Windows-1250, cu „Încasare Ştefănescu şi fiii”. Înainte:
    „�ncasare �tef�nescu”. Acum: descrierea rândului e cea din fișier."""
    pregateste_firma(patron, firma_e2e)
    zi = AZI - _dt.timedelta(days=3)
    csv = ("Data;Detalii;Suma\n%s;Încasare Ştefănescu şi fiii E2E251;251,00\n" % zi.strftime("%d.%m.%Y")).encode("cp1250")
    _banca(patron, firma_e2e)
    pg = patron.pg
    m = _incarca(pg, "extras_e2e251_%d.csv" % time.time(), "text/csv", csv)
    assert "1 linie importată" in m, m
    lista = _lista_cu(pg, "E2E251")
    patron.captura("diacritice_pastrate")
    assert "Încasare Ştefănescu şi fiii E2E251" in lista and "�" not in lista, lista


def test_def_c121_extrasul_altui_cont_cere_confirmarea_inainte_de_import(patron, firma_e2e):
    """C121 (găsită de pachetul migr). Pașii: „Bancă” -> extrasul MT940 al contului RO66BACX0000001234567890, iar contul firmei (Date
    firmă) e RO49AAAA1B31007593840000. Înainte: liniile intrau fără întrebare. Acum: avertismentul galben numește ambele conturi și nimic
    nu e scris; „Da, e extrasul acestei firme” -> liniile intră."""
    pregateste_firma(patron, firma_e2e)
    s = firma_e2e["schema"]
    zi = AZI - _dt.timedelta(days=4)
    mt = _mt940(zi, 121.0, "Incasare E2EC121").replace(b"RO49AAAA1B31007593840000", b"RO66BACX0000001234567890")
    _banca(patron, firma_e2e)
    pg = patron.pg
    m = _incarca(pg, "extras_e2ec121_%d.sta" % time.time(), "text/plain", mt)
    assert "RO66BACX0000001234567890" in m and "RO49AAAA1B31007593840000" in m, m
    pg.wait_for_selector("#caseta-atentie-activa #ca-ok", timeout=10000)
    patron.captura("cere_confirmarea")
    assert pg.inner_text("#caseta-atentie-activa #ca-ok") == "Da, e extrasul acestei firme"
    assert sql('SELECT count(*) FROM "%s".extras_linii WHERE suma = 121' % s) == [(0,)]
    pg.click("#caseta-atentie-activa #ca-ok")
    pg.wait_for_function("() => document.querySelector('#bk-mesaj').innerText.includes('linie importată')", timeout=30000)
    assert sql('SELECT count(*) FROM "%s".extras_linii WHERE suma = 121' % s) == [(1,)]


def fisier_csv_251(zi_iso):
    """Extrasul CSV al dovezii 251, în Windows-1250 (literele cu sedilă — virgula de dedesubt nu există în Windows-1250)."""
    zi = _dt.date.fromisoformat(zi_iso)
    return ("Data;Detalii;Suma\n%s;Proba 251 Încasare Ştefănescu şi fiii;2,51\n" % zi.strftime("%d.%m.%Y")).encode("cp1250")
