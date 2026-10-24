# -*- coding: utf-8 -*-
"""Lotul 12, comanda Costin 12.1 — subagentul PROD: partenerii firmei (461), nomenclatorul de produse (471, 472), mijloacele fixe (162).

Pașii contabilului pe aplicația din index, pe baza de TEST, pe o firmă NOUĂ (`firma_noua`, Date firmă pe drumul ecranului —
`e2e_bloc_e._completeaza`). DATE DE PORNIRE fără ecran (declarate, regula lui 429): documentele partenerilor (factura emisă și cea primită cu
notele lor validate, încasarea în numerar, nota manuală cu partenerul pe linie) și NIR-ul vechi al articolului (scris înainte de 415, fără
produs în nomenclator) se scriu în schema firmei, cum le-au lăsat drumurile aplicației; fișa clientului, pe ruta ecranului Clienți (POST).
Răspunsul ANAF e servit de plasă (`e2e_lot11_p2._anaf`), modelul cotei e simulat (`conftest.ai_pregateste`). CUI-urile 14399840 / 2864518
au cifra de control verificată (algoritmul din CLAUDE.md). Cotele TVA se citesc din registru (`cote_tva.cote_regim`, CF art.291 alin.(1)
și (2)), nu se scriu din memorie. Mutațiile: frontend_test/e2e/mut_lot12_prod.json.

Cardul „Parteneri” din fereastra firmei (`#fa-parteneri`) e în `static/js/ecrane/firme.js` (al pachetului firme1): textul lui e cerut în
raportul pachetului PROD."""
import datetime as _dt
import re

import pytest

from conftest import _db, ai_pregateste, ai_prompturi, firma_noua, sql
from e2e_bloc_a import _api, _ok
from e2e_bloc_d import PATRON, _api as _api_cont
from e2e_bloc_e import _mf, _mijloace
from e2e_lot11_p2 import _anaf

AZI = _dt.date.today()   # AZI-dat-de-test: documentele de pornire sunt de azi, după data preluării firmei noi (luna creării)


@pytest.fixture(scope="module")
def firma_pr():
    from e2e_bloc_e import _completeaza
    for f in firma_noua():
        yield _completeaza(f, "cantitativ_valoric")


def _cote():
    from core import cote_tva
    return cote_tva.cote_regim()


def _nota(s, data, status, linii, factura_id=None, numar=None, descriere="nota"):
    """Nota și rândurile ei într-o SINGURĂ tranzacție, ca drumurile aplicației: regula de fond din bază (`regula_linii_nota`) nu lasă
    rânduri adăugate unei note validate într-o tranzacție anterioară — nota validată se scrie întreagă, odată."""
    with _db().get_conn() as conn, conn.cursor() as cur:
        # date-de-pornire: nota validată a unui document de pornire, scrisă întreagă într-o tranzacție (regula_linii_nota) — antetul
        cur.execute('INSERT INTO "%s".inregistrari (data, numar, descriere, sursa, status, factura_id) VALUES (%%s, %%s, %%s, %%s, %%s, %%s) '
                    'RETURNING id' % s, (data, numar, descriere, "manual", status, factura_id))
        nid = cur.fetchone()[0]
        for d, c, suma, *p in linii:
            # date-de-pornire: rândurile aceleiași note, cu partenerul pe linie
            cur.execute('INSERT INTO "%s".inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma, partener_cui, partener_nume) '
                        'VALUES (%%s, %%s, %%s, %%s, %%s, %%s)' % s, (nid, d, c, suma, p[0] if p else None, p[1] if len(p) > 1 else None))
        conn.commit()
    return nid


@pytest.fixture(scope="module")
def parteneri_pr(firma_pr):
    """Documentele partenerilor (date de pornire, vezi antetul): DANTE (fișa „DANTE SRL” — numele vechi; factura emisă F 1 de 1.210 lei
    cu nota 4111 = 707 / 4427 validată; încasarea în numerar de 500 lei cu nota 5311 = 4111 validată) și ALTEX (factura primită A-77 de
    242 lei cu nota 601 / 4426 = 401 validată; nota manuală 401 = 5121 de 42 lei cu partenerul scris pe linie „RO2864518”)."""
    s = firma_pr["schema"]
    st, r = _api_cont(PATRON, "POST", "/tenants/%d/clienti" % firma_pr["tenant_id"],   # fișa, pe ruta ecranului Clienți (antetul)
                      {"nume": "DANTE SRL", "cui": "14399840", "oras": "București", "judet": "B"})
    assert st == 200, (st, r)
    # date-de-pornire: factura emisă F 1 pe numele de la ANAF, lângă fișa cu numele vechi „DANTE SRL” — documentul partenerului; ecranul probat e Parteneri
    f1 = sql('INSERT INTO "%s".facturi (numar, serie, data_emitere, directie, tip, tert_nume, tert_cui, total, tva) VALUES '
             "('1', 'F', %%s, 'emisa', 'factura', 'DANTE INTERNATIONAL SA', '14399840', 1210, 210) RETURNING id" % s, (AZI,))[0][0]
    _nota(s, AZI, "validata", [("4111", "707", 1000), ("4111", "4427", 210)], factura_id=f1)
    nc = _nota(s, AZI, "validata", [("5311", "4111", 500)], descriere="încasare F 1")
    # date-de-pornire: încasarea în numerar a facturii F 1 (CH 1), legată de nota ei de mai sus — documentul partenerului
    sql('INSERT INTO "%s".casa_operatiuni (data, tip, categorie, document, partener, cui, suma, inregistrare_id) VALUES '
        "(%%s, 'incasare', 'incasare_client', 'CH 1', 'DANTE INTERNATIONAL SA', '14399840', 500, %%s)" % s, (AZI, nc))
    # date-de-pornire: factura primită A-77 de la ALTEX, cu nota ei validată — documentul furnizorului; ecranul probat e Parteneri
    f2 = sql('INSERT INTO "%s".facturi (numar, data_emitere, directie, tip, tert_nume, tert_cui, total, tva) VALUES '
             "('A-77', %%s, 'primita', 'factura', 'ALTEX ROMANIA SRL', '2864518', 242, 42) RETURNING id" % s, (AZI,))[0][0]
    _nota(s, AZI, "validata", [("601", "401", 200), ("4426", "401", 42)], factura_id=f2)
    _nota(s, AZI, "validata", [("401", "5121", 42, "RO2864518", "Altex Romania")], numar="77", descriere="plată parțială A-77")
    return firma_pr


def _parteneri(patron, f):
    patron.firma(f["nume"])
    patron.pg.click("#fa-parteneri")
    patron.pg.wait_for_selector("#pt-tabel", timeout=30000)


def _fisa(patron, cheie):
    pg = patron.pg
    pg.click("#pt-fisa-" + cheie)
    pg.wait_for_selector(".fereastra:last-of-type #pp-rezumat", timeout=30000)


def _txt(pg, sel):
    return " ".join(pg.inner_text(".fereastra:last-of-type " + sel).split())


def _sold_pe_coloane(pg):
    """Tabelul `#pp-sold` al fișei partenerului (`clienti_ecran.js`, `randSold`: Cont | Denumire | Sold debitor | Sold creditor), citit
    pe CELULE, cu coloana luată din antet: {cont: (denumire, sold debitor, sold creditor)}. Textul lipit al rândului („4111 Clienți 710,00”)
    nu spune pe ce coloană stă suma — o sumă mutată pe partea cealaltă (semnul inversat) dă același text."""
    r = pg.evaluate("() => { const t = document.querySelector('.fereastra:last-of-type #pp-sold'); "
                    "const n = (e) => (e.innerText || '').replace(/\\s+/g, ' ').trim(); "
                    "return {antet: [...t.querySelectorAll('thead th')].map(n), "
                    "randuri: [...t.querySelectorAll('tbody tr')].map((tr) => [...tr.querySelectorAll('td')].map(n))}; }")
    i_cont, i_den = r["antet"].index("Cont"), r["antet"].index("Denumire")
    i_deb, i_cre = r["antet"].index("Sold debitor"), r["antet"].index("Sold creditor")
    assert len(r["antet"]) == 4 and all(len(x) == 4 for x in r["randuri"]), r
    return {x[i_cont]: (x[i_den], x[i_deb], x[i_cre]) for x in r["randuri"]}


# ── 461 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_461_lista_partenerilor_din_toate_documentele_cu_cautare(patron, parteneri_pr):
    """461. Pașii: fereastra firmei -> „Parteneri”: DANTE (cu fișa „DANTE SRL”, factura emisă și încasarea în numerar) și ALTEX (factura
    primită și nota manuală cu „RO2864518” pe linie — același partener, nu doi), fiecare cu rolul și numărul documentelor -> „altex” în
    căutare: rămâne numai ALTEX, „1 din 2 parteneri” -> „14399840”: rămâne numai DANTE."""
    _parteneri(patron, parteneri_pr)
    pg = patron.pg
    t = _txt(pg, "#pt-tabel")
    assert "DANTE SRL 14399840 client 2 da Fișa partenerului" in t, t
    assert "ALTEX ROMANIA SRL 2864518 furnizor 2 — Fișa partenerului" in t, t
    assert t.count("Fișa partenerului") == 2, t
    patron.captura("lista")
    pg.fill("#pt-cauta", "altex")
    assert pg.locator("tr[data-cheie='cui-14399840']").is_hidden() and pg.locator("tr[data-cheie='cui-2864518']").is_visible()
    assert _txt(pg, "#pt-numar") == "1 din 2 parteneri"
    patron.captura("cautare_nume")
    pg.fill("#pt-cauta", "14399840")
    assert pg.locator("tr[data-cheie='cui-14399840']").is_visible() and pg.locator("tr[data-cheie='cui-2864518']").is_hidden()


def test_def_461_fisa_partenerului_date_anaf_documente_si_sold(patron, parteneri_pr):
    """461. Pașii: „Parteneri” -> „Fișa partenerului” la DANTE: datele din fișa de client (București, B), documentele (factura emisă F 1 de
    1.210,00 lei, încasarea în numerar CH 1 de 500,00 lei), soldul din contabilitate pe 4111 Clienți: 710,00 debitor (1.210 − 500, notele
    validate, ca balanța) -> „Verifică la ANAF”: „La ANAF: «DANTE INTERNATIONAL SA» · plătitor de TVA” și, numele din fișă fiind altul,
    „Actualizează fișa cu numele de la ANAF” -> clic: fișa are numele de la ANAF (444). ALTEX: soldul pe 401 Furnizori 200,00 creditor
    (242 − 42), cu nota manuală printre documente."""
    _anaf()
    s = parteneri_pr["schema"]
    _parteneri(patron, parteneri_pr)
    _fisa(patron, "cui-14399840")
    pg = patron.pg
    antet = _txt(pg, "#pp-rezumat")
    assert "DANTE SRL" in antet and "Cod fiscal: 14399840 · client" in antet, antet
    assert "Fișa de client: DANTE SRL București, B" in _txt(pg, ".pf-lista"), _txt(pg, ".pf-lista")
    docs = _txt(pg, "#pp-documente")
    assert re.search(r"Factură emisă F 1 1\.210,00 lei", docs) and "Încasare în numerar CH 1 500,00 lei" in docs, docs
    # soldul pe coloana lui: 4111 debitor 710,00 (1.210 − 500), coloana creditoare goală; niciun alt cont al partenerului
    assert _sold_pe_coloane(pg) == {"4111": ("Clienți", "710,00", "")}, _sold_pe_coloane(pg)
    patron.captura("fisa_dante")
    with pg.expect_response(lambda r: "/verifica-cui/" in r.url, timeout=30000):
        pg.click("#pp-anaf")
    pg.wait_for_selector("#pp-anaf-aplica", timeout=20000)
    st = _txt(pg, "#pp-anaf-stare")
    assert "La ANAF: „DANTE INTERNATIONAL SA” · plătitor de TVA" in st, st
    patron.captura("anaf_diferit")
    pg.click("#pp-anaf-aplica")
    pg.wait_for_function("() => (document.querySelector('#pp-mesaj') || {innerText: ''}).innerText.includes('numele de la ANAF')",
                         timeout=30000)
    assert sql('SELECT nume FROM "%s".clienti WHERE cui = %%s' % s, ("14399840",)) == [("DANTE INTERNATIONAL SA",)]
    assert "DANTE INTERNATIONAL SA" in _txt(pg, "#pp-rezumat")
    patron.captura("anaf_actualizat")
    # furnizorul: soldul pe 401, nota manuală cu partenerul pe linie printre documente
    _parteneri(patron, parteneri_pr)
    _fisa(patron, "cui-2864518")
    docs = _txt(pg, "#pp-documente")
    assert "Notă contabilă nr 77 · plată parțială A-77 42,00 lei" in docs and "Factură primită A-77 242,00 lei" in docs, docs
    # 401 creditor 200,00 (242 − 42), coloana debitoare goală
    assert _sold_pe_coloane(pg) == {"401": ("Furnizori", "", "200,00")}, _sold_pe_coloane(pg)
    assert "Partenerul n-are fișă" in _txt(pg, "#pp-fara-fisa")
    patron.captura("fisa_altex")


# ── 471 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_471_articolul_din_nir_vine_cu_cota_propusa_si_justificarea_fara_nume_interne(patron, firma_pr):
    """471. Pașii: un articol din NIR-ul vechi (NIR nr 3, rândul cu cota redusă, fără produs în nomenclator — scris înainte de 415) și unul
    fără NIR -> fereastra firmei -> Produse: rândul din NIR spune „Cota propusă: 11%, de pe rândul din NIR nr 3 din …”, cu „Alege cota
    propusă”; rândul fără NIR spune cota propusă automat, cu justificarea modelului FĂRĂ „EXCEPTII_21” (promptul nu-l mai conține) -> lista
    nu vine aleasă (cota o alege omul) -> „Alege cota propusă” -> „Salvează cota” -> „Cota 11% salvată”, produsul în nomenclator cu 11."""
    std, red = _cote()
    s, tid = firma_pr["schema"], firma_pr["tenant_id"]
    # date-de-pornire: articolul NIR-ului vechi, scris înainte de 415 fără produs în nomenclator (codul de azi îl leagă de produs)
    aid = sql('INSERT INTO "%s".articole (denumire, um) VALUES (%%s, %%s) RETURNING id' % s, ("Marfa B E2E 471", "buc"))[0][0]
    # date-de-pornire: al doilea articol al probei, fără NIR și fără produs în nomenclator, ca înainte de 415
    bid = sql('INSERT INTO "%s".articole (denumire, um) VALUES (%%s, %%s) RETURNING id' % s, ("Ciocolata E2E 471", "buc"))[0][0]
    # date-de-pornire: NIR-ul vechi nr 3 al articolului de mai sus, scris înainte de 415
    nid = sql('INSERT INTO "%s".nir (numar, data) VALUES (%%s, %%s) RETURNING id' % s, ("3", AZI))[0][0]
    # date-de-pornire: rândul NIR-ului vechi, cu cota redusă
    sql('INSERT INTO "%s".nir_linii (nir_id, denumire, cantitate, pret_achizitie, pret_vanzare, cota_tva) VALUES (%%s, %%s, 2, 10, 12, %%s)'
        % s, (nid, "Marfa B E2E 471", red))
    ai_pregateste('{"cota": %d, "categorie": "standard", "tip": "marfa", "justificare": "Ciocolata e in EXCEPTII_21 (zahar adaugat).", '
                  '"incredere": "mare"}' % std)
    patron.firma(firma_pr["nume"])
    pg = patron.pg
    pg.click("#fa-produse")
    pg.wait_for_selector("#pr-propunere-alege-s%d" % aid, timeout=25000)
    pg.wait_for_selector("#pr-propunere-alege-s%d" % bid, timeout=25000)
    t = " ".join(pg.inner_text("#pr-rand-s%d" % aid).split())
    assert ("Cota propusă: %d%%, de pe rândul din NIR nr 3 din %s." % (red, AZI.strftime("%d.%m.%Y"))) in t, t   # AZI-dat-de-test
    tb = " ".join(pg.inner_text("#pr-rand-s%d" % bid).split())
    assert ("Cota propusă automat: %d%% — Ciocolata e in excepțiile de la cota redusă (zahar adaugat)." % std) in tb, tb
    assert "EXCEPTII_21" not in patron.fereastra()
    pr = ai_prompturi()
    assert pr and "EXCEPTII_21" not in pr[-1]["sistem"] and "bauturilor alcoolice" in pr[-1]["sistem"], pr[-1]["sistem"][:600]
    assert pg.input_value("#pr-cota-s%d" % aid) == ""   # propunerea nu vine aleasă
    patron.captura("propuneri")
    pg.click("#pr-propunere-alege-s%d" % aid)
    assert pg.input_value("#pr-cota-s%d" % aid) == str(red)
    pg.click("#pr-cota-salveaza-s%d" % aid)
    pg.wait_for_function("() => (document.querySelector('#pr-mesaj') || {}).innerText && "
                         "document.querySelector('#pr-mesaj').innerText.includes('e acum în nomenclator')", timeout=20000)
    patron.captura("salvata")
    assert sql('SELECT cota_tva::int FROM "%s".produse WHERE denumire = %%s' % s, ("Marfa B E2E 471",)) == [(red,)]
    assert tid


# ── 472 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_472_cota_salvata_se_corecteaza_pe_rand_si_corectura_e_consemnata(patron, firma_pr):
    """472. Pașii: produsul „Carte tehnica E2E 472” salvat cu cota standard -> Produse -> „Corectează cota” pe rândul lui -> cota redusă
    (CF art.291 alin.(2) lit.g): cărțile) -> „Salvează cota” -> „Cota corectată: … din 21% în 11%. Facturile emise rămân cu cota lor …
    Corectura e consemnată” -> rândul arată „TVA 11%” și „cota corectată pe …: 21% → 11% (consemnată)”; în jurnalul cotei: 21 -> 11,
    utilizatorul contabilului."""
    std, red = _cote()
    s, tid = firma_pr["schema"], firma_pr["tenant_id"]
    pid = _ok(_api(patron, "POST", "/tenants/%d/produse" % tid, {"denumire": "Carte tehnica E2E 472", "um": "buc", "cota_tva": std,
                                                                "confirmat": True}), "produsul")["id"]
    patron.firma(firma_pr["nume"])
    pg = patron.pg
    pg.click("#fa-produse")
    pg.wait_for_selector("#pr-corecteaza-%d" % pid, timeout=25000)
    assert pg.locator("#pr-corectura-%d" % pid).is_hidden()   # nimic deschis singur
    pg.click("#pr-corecteaza-%d" % pid)
    pg.select_option("#pr-cota-%d" % pid, str(red))
    patron.captura("corectura_deschisa")
    pg.click("#pr-corectura-salveaza-%d" % pid)
    pg.wait_for_function("() => (document.querySelector('#pr-mesaj') || {}).innerText && "
                         "document.querySelector('#pr-mesaj').innerText.includes('Cota corectată')", timeout=20000)
    msg = " ".join(pg.inner_text("#pr-mesaj").split())
    assert ("Cota corectată: Carte tehnica E2E 472, din %d%% în %d%%." % (std, red)) in msg and "Corectura e consemnată" in msg, msg
    rand = " ".join(pg.locator(".pr-rand", has_text="Carte tehnica E2E 472").first.inner_text().split())
    assert ("TVA %d%%" % red) in rand and ("%d%% → %d%% (consemnată)" % (std, red)) in rand, rand
    patron.captura("corectata")
    uid = sql("SELECT id FROM public.users WHERE email = 'patron@prisma-cont.test'")[0][0]
    assert sql('SELECT cota_veche::int, cota_noua::int, user_id FROM "%s".produse_cota_jurnal WHERE produs_id = %%s' % s, (pid,)) == [
        (std, red, uid)]
    assert sql('SELECT cota_tva::int FROM "%s".produse WHERE id = %%s' % s, (pid,)) == [(red,)]


# ── 162 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_162_pif_intreg_si_actiunile_in_vedere_la_1700(patron, firma_pr):
    """162 (cazul întreg al lui Costin: „derulare laterală la ~1700 px, PIF tăiat, acțiuni ascunse”; derularea laterală o păzește
    `e2e_bloc_e.test_def_162_*`). Pașii: ecran de 1700 px -> Mijloace fixe: data PIF se vede întreagă (celula n-o taie) -> „Acțiuni”:
    „Casează”, valoarea justă, „Reevaluează” și „C&D” stau în fereastră, în vedere pe lățime."""
    pg = patron.pg
    pg.set_viewport_size({"width": 1700, "height": 1000})
    _mf(firma_pr, "MF162B", "12000", 24, "2026-01-10")
    _mijloace(patron, firma_pr)
    rand = pg.locator(".fereastra:last-of-type table.fd-tabel tbody tr", has_text="MF162B").first
    pif = rand.locator("td", has_text="10.01.2026").first
    m = pif.evaluate("(td) => { const z = td.closest('.fereastra-corp').getBoundingClientRect(); const r = td.getBoundingClientRect();"
                     " return {text: td.innerText.trim(), sw: td.scrollWidth, cw: td.clientWidth, st: r.left >= z.left, dr: r.right <= z.right}; }")
    assert m["text"] == "10.01.2026" and m["sw"] <= m["cw"] and m["st"] and m["dr"], m
    rand.locator("details.dec-xml > summary").click()
    vazute = rand.evaluate("(tr) => { const z = tr.closest('.fereastra-corp').getBoundingClientRect();"
                           " return [...tr.querySelectorAll('details.dec-xml button, details.dec-xml input')].map((b) => {"
                           " const r = b.getBoundingClientRect(); return [b.innerText || b.getAttribute('aria-label'),"
                           " r.width > 0 && r.left >= z.left && r.right <= z.right]; }); }")
    patron.captura("actiuni")
    assert len(vazute) == 4 and all(ok for _t, ok in vazute), vazute
