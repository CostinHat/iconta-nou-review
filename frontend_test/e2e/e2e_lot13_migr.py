# -*- coding: utf-8 -*-
"""Lotul 13, comanda Costin 13.1 (verbatim în DECIZII „Comanda 13.1”), pachetul `migr` — preluarea firmei (Migrare cabinet, „Import date”,
soldurile inițiale, partenerii, articolele, auditul de preluare) și stingerea soldurilor preluate în prima lună.

Pașii contabilului pe aplicația din index, pe baza de TEST, pe firme NOI (`conftest.firma_noua`). Cifrele sunt ale firmei F7 Preluare Test
SRL din retestul lui Costin (24–25.10.2026): balanța la 30.09.2026 — 1012 C 200, 117 C 14.000, 371 D 4.200, 401 C 3.000, 4111 D 2.500,
5121 D 10.000, 5311 D 500 (debit = credit = 17.200); partenerii 4111: Alfa 1.500 + Beta 1.000 (401 refuzat); articolele: 10 × 150 +
20 × 80 + 5 × 200 = 4.100. Datele de pornire puse altfel decât din ecran (pe rutele aplicației, aceeași sesiune — `e2e_bloc_a._api`; sau
`sql` când ecranul pasului e chiar cel probat în alt test) sunt numite pe linia lor. CUI-urile: sintetice, cu cifra de control verificată
(`conftest.cui_cu_control`).
TEMEI: N/A — reguli de produs (comanda 13.1; CLAUDE.md §9), cu excepțiile citate pe linie: 585 (Codul muncii art.164 alin.(6), HG 146/2026
art.1), 586 (CF art.43 alin.(2)), 588 (CF art.28 alin.(2) lit.b) în forma OUG 8/2026 art.6 pct.7, OUG 8/2026 art.10 alin.(2)), 669 (OMFP
1802/2014 pct.130: soldurile de deschidere — de aceea factura preluată se stinge, nu se contează).
Mutațiile: `frontend_test/e2e/mut_lot13_migr.json`. Dovezile pe firmele de test: `frontend_test/dovada/dovezi_lot13_migr.json`."""
import datetime as _dt

import pytest
from e2e_lot12_migr import alege_analitic_117

from conftest import cui_cu_control, firma_noua, sql, text_din_card
from e2e_bloc_a import _api, _card, _ok, pregateste_firma
from e2e_import_saga import _incarca, _pas

DATA = "2026-09-30"
BALANTA_F7 = (("1012", 0, 200), ("117", 0, 14000), ("371", 4200, 0), ("401", 0, 3000), ("4111", 2500, 0), ("5121", 10000, 0), ("5311", 500, 0))
ALFA = (cui_cu_control(40130001), "CLIENT ALFA E2E L13 SRL")
BETA = (cui_cu_control(40130002), "CLIENT BETA E2E L13 SRL")
FURNIZOR = (cui_cu_control(40130003), "FURNIZOR E2E L13 SRL")
_F = ".fereastra:last-of-type "


def _txt(pg, sel):
    return " ".join(pg.inner_text(sel).split())


def _balanta_api(patron, f, randuri=BALANTA_F7, metoda="cantitativ_valoric"):
    """Date de pornire: balanța de deschidere la 30.09.2026, pe ruta „Solduri inițiale” (ecranul ei e probat în test_def_664)."""
    _ok(_api(patron, "POST", "/tenants/%d/solduri" % f["tenant_id"], {
        "data_referinta": DATA, "metoda_stoc": metoda,
        "randuri": [{"cont": c, "debit": d, "credit": cr} for c, d, cr in randuri]}), "balanța de deschidere")


def _parteneri_api(patron, f, randuri):
    """Date de pornire: soldurile pe parteneri, pe ruta „Solduri parteneri” (ecranul ei e probat în test_def_666 / test_def_582)."""
    return _ok(_api(patron, "POST", "/tenants/%d/parteneri" % f["tenant_id"], {
        "data_referinta": DATA, "randuri": [{"cont": c, "cui": cui, "denumire": den, "debit": d, "credit": cr} for c, cui, den, d, cr in randuri]}),
        "soldurile pe parteneri")


def _rezumat_parteneri(f):
    """Date de pornire: rezumatul „parteneri” al firmei, calculat cum îl calculează tura de 5 minute a cronului
    (`firma_rezumat.recalculeaza_firma`). Lista „Solduri parteneri” citește modelul: fără rezumat, firma e „încă necunoscută” (P3 val B,
    corect — un necunoscut nu se arată ca „nu e cazul”), iar o firmă abia creată nu-l are."""
    from core import firma_rezumat as fr
    fr.recalculeaza_firma(f["tenant_id"], f["schema"], aspecte=["parteneri"])


def _parteneri_f7(patron, f):
    _parteneri_api(patron, f, (("4111",) + ALFA + (1500, 0), ("4111",) + BETA + (1000, 0)))


def _migrare(patron):
    """Pagina principală -> Firme -> „Migrare cabinet” (meniul pașilor)."""
    pg = patron.pg
    patron.acasa()
    pg.click("button.cab-card:has([data-cheie='firme'])")
    pg.click("#opt-migrare")
    pg.wait_for_selector("#mig-meniu .mig-op", timeout=20000)


def _pas_meniu(pg, titlu):
    return pg.locator("#mig-meniu .mig-op", has_text=titlu).first


@pytest.fixture()
def firma():
    """O firmă NOUĂ pentru fiecare test (fiecare test își pune datele: rulează și singur, ca în mutații)."""
    for f in firma_noua():
        yield f


# ── 662 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_662_firma_noua_se_deschide_cu_incepe_preluarea(patron, firma):
    """662: „O firmă abia creată, fără solduri, se deschide pe «Zilnic» (facturi, salarii); preluarea nu apare nicăieri. Firma nouă trebuie
    să deschidă cu «Începe preluarea».” Pașii: Firme -> firma nouă -> sus, deasupra grupurilor de carduri: „Firma e nouă în iConta.eu: nu
    are încă nimic adus …” și butonul principal „Începe preluarea” (nimic nu se deschide singur) -> „Începe preluarea” -> „Import date”
    al firmei: „Solduri inițiale” obligatoriu, „Solduri parteneri” nu e cazul (fără balanță).
    MUTAȚIA: zona preluării nu se mai desenează -> ROȘU."""
    pg = patron.pg
    patron.firma(firma["nume"])
    pg.wait_for_selector("#firma-preluare #fa-preluare", timeout=30000)
    patron.captura("fereastra_firmei")
    assert _txt(pg, "#fa-preluare") == "Începe preluarea"
    assert _txt(pg, "#firma-preluare .ca-mesaj").startswith("Firma e nouă în iConta.eu: nu are încă nimic adus din programul vechi")
    # deasupra primului grup („Zilnic”): zona preluării vine înaintea cardurilor în fereastră
    assert pg.evaluate("() => { const z = document.querySelector('#firma-preluare'), g = document.querySelector('.firme-grup');"
                       " return !!(z && g && (z.compareDocumentPosition(g) & Node.DOCUMENT_POSITION_FOLLOWING)); }")
    pg.click("#fa-preluare")
    pg.wait_for_selector("#mig-pasi .mig-frand[data-strat='solduri'] [data-stare-pas]", timeout=20000)
    patron.captura("import_date")
    assert pg.get_attribute("#mig-pasi .mig-frand[data-strat='solduri'] [data-stare-pas]", "data-stare-pas") == "obligatoriu"
    assert pg.get_attribute("#mig-pasi .mig-frand[data-strat='solduri_parteneri'] [data-stare-pas]", "data-stare-pas") == "nu_e_cazul"


# ── 664 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
BALANTA_CSV = ("cont;denumire;sold debitor;sold creditor\n" + "".join("%s;Cont %s;%s;%s\n" % (c, c, d, cr) for c, d, cr in BALANTA_F7)).encode()


def test_def_664_salvarea_balantei_numeste_pasii_urmatori(patron, firma):
    """664: „După salvare, 371 = 4.200 la cantitativ-valoric (CMP) rămâne fără articole și cantități […]; 401/4111 rămân totaluri fără
    trimitere la parteneri. Salvarea trebuie să ducă la pașii următori necesari.” Pașii: Import date -> „Solduri inițiale” -> balanța F7
    -> data 30.09.2026 -> metoda „cantitativ-valoric” -> „Salvează soldurile” -> confirmarea: „7 conturi salvate …” și „Pașii următori
    necesari pentru <firmă>:” cu „Solduri parteneri — De defalcat pe parteneri: 401 (creditor 3.000,00 lei în balanță) — partenerii dau
    0,00 lei; 4111 (debitor 2.500,00 lei în balanță) — partenerii dau 0,00 lei.” și „Articole și stoc inițial — … 371 …”; în listă, cei
    doi pași „obligatoriu”.
    MUTAȚIA: salvarea revine fără pașii următori -> ROȘU."""
    pg = patron.pg
    _pas(patron, firma, "Solduri ini")
    _incarca(patron, "balanta_f7.csv", BALANTA_CSV, "#mig-salveaza-sold")
    pg.fill("#mig-data-bal", DATA)
    pg.select_option("#mig-metoda-stoc", "cantitativ_valoric")
    alege_analitic_117(pg)
    pg.click("#mig-salveaza-sold")
    pg.wait_for_function("() => document.body.innerText.includes('Pașii următori necesari pentru')", timeout=30000)
    t = " ".join(patron.fereastra().split())
    patron.captura("pasii_urmatori")
    assert "7 conturi salvate, cu soldurile la 30.09.2026." in t, t[:2000]
    assert ("Solduri parteneri — De defalcat pe parteneri: 401 (creditor 3.000,00 lei în balanță) — partenerii dau 0,00 lei; 4111 "
            "(debitor 2.500,00 lei în balanță) — partenerii dau 0,00 lei.") in t, t[:3000]
    assert "Articole și stoc inițial — Articolele cu stocul inițial trebuie să dea soldul conturilor de stoc din balanță — 371" in t, t[:3000]
    for strat in ("solduri_parteneri", "articole"):
        assert pg.get_attribute(".mig-frand[data-strat='%s'] [data-stare-pas]" % strat, "data-stare-pas") == "obligatoriu", strat


def test_def_664_salvarea_din_pasul_deschis_direct_numeste_pasii_urmatori(patron, firma):
    """664 pe drumul lui 663: cu firma în lucru, pasul din „Migrare cabinet” se deschide direct pe ea, într-o fereastră nouă; salvarea o
    închide (`nav.inapoiPas()` fără pas pe traseu) și revine în meniul „Migrare cabinet”, care trebuie să arate confirmarea, pașii următori
    și starea nouă a pasului. Pașii: firma în lucru -> Firme -> „Migrare cabinet” -> „Solduri inițiale” (direct importul firmei, cu „Altă
    firmă”) -> balanța F7 -> data 30.09.2026 -> metoda „cantitativ-valoric” -> „Salvează soldurile” -> înapoi în meniu: „7 conturi salvate …”,
    „Pașii următori necesari pentru <firmă>:” cu „Solduri parteneri — … 401 …”, iar „Solduri inițiale” e „gata”.
    MUTAȚIA: meniul Migrare cabinet nu mai arată mesajul salvării -> ROȘU."""
    pg = patron.pg
    patron.firma(firma["nume"])                      # firma în lucru
    _migrare(patron)
    pg.wait_for_selector("#mig-firma-lucru", timeout=20000)
    _pas_meniu(pg, "Solduri inițiale").click()
    pg.wait_for_selector(_F + "#mig-alta-firma", timeout=20000)
    pg.set_input_files(_F + "#mig-file", files=[{"name": "balanta_f7.csv", "mimeType": "text/csv", "buffer": BALANTA_CSV}])
    pg.wait_for_selector(_F + "#mig-salveaza-sold", timeout=20000)
    pg.fill(_F + "#mig-data-bal", DATA)
    pg.select_option(_F + "#mig-metoda-stoc", "cantitativ_valoric")
    pg.click(_F + "#mig-salveaza-sold")
    pg.wait_for_function("() => { const f = [...document.querySelectorAll('.fereastra')].pop();"
                         " return !!f && !!f.querySelector('#mig-firma-lucru') && f.innerText.includes('Pașii următori necesari pentru'); }",
                         timeout=30000)                                    # înapoi în meniul Migrare cabinet, cu mesajul
    t = _txt(pg, ".fereastra:last-of-type")
    patron.captura("pasii_urmatori_direct")
    assert "7 conturi salvate, cu soldurile la 30.09.2026." in t, t[:2000]
    assert "Pașii următori necesari pentru %s:" % firma["nume"] in t, t[:2000]
    assert "Solduri parteneri — De defalcat pe parteneri: 401 (creditor 3.000,00 lei în balanță)" in t, t[:3000]
    pg.wait_for_function("() => { const r = [...document.querySelectorAll('#mig-meniu .mig-op')].find((x) => x.innerText.includes('Solduri inițiale'));"
                         " const b = r && r.querySelector('[data-stare-pas]'); return !!b && b.dataset.starePas === 'gata'; }", timeout=20000)


# ── 663 + 668 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_663_migrare_cabinet_arata_starea_firmei_in_lucru(patron, firma):
    """663: „Stările pașilor sunt pe cabinet, nu pe firma în lucru: după salvarea soldurilor F7, «Solduri inițiale» rămâne «obligatoriu»;
    «Vector fiscal» arată «gata», deși pentru F7 nu s-a citit nimic.” Pașii: firma (balanța F7 și partenerii pe 4111 adusi pe rute) e
    deschisă (firma în lucru) -> pagina principală -> Firme -> „Migrare cabinet”: sus „Starea pașilor e a firmei în lucru, <firmă>”;
    „Solduri inițiale” gata, „Vector fiscal” obligatoriu (nimic citit), „Solduri parteneri” obligatoriu (401), „Articole și stoc inițial”
    obligatoriu (371) -> „Articole și stoc inițial”: se deschide direct importul firmei, cu „Altă firmă” (668: nu se mai cere firma).
    MUTAȚIA: meniul ignoră firma în lucru (stările cabinetului) -> ROȘU."""
    pg = patron.pg
    _balanta_api(patron, firma)
    _parteneri_f7(patron, firma)
    patron.firma(firma["nume"])                      # firma în lucru
    _migrare(patron)
    pg.wait_for_selector("#mig-firma-lucru", timeout=20000)
    patron.captura("meniu_firma_in_lucru")
    assert firma["nume"] in _txt(pg, "#mig-firma-lucru")
    stari = {t: _pas_meniu(pg, t).locator("[data-stare-pas]").get_attribute("data-stare-pas")
             for t in ("Solduri inițiale", "Vector fiscal", "Solduri parteneri", "Articole și stoc inițial")}
    assert stari == {"Solduri inițiale": "gata", "Vector fiscal": "obligatoriu", "Solduri parteneri": "obligatoriu",
                     "Articole și stoc inițial": "obligatoriu"}, stari
    assert "401 (creditor 3.000,00 lei în balanță)" in _pas_meniu(pg, "Solduri parteneri").inner_text()
    _pas_meniu(pg, "Articole și stoc inițial").click()
    pg.wait_for_selector(_F + "#mig-file", state="attached", timeout=20000)
    assert pg.locator(_F + "#mig-alta-firma").count() == 1 and firma["nume"] in _txt(pg, _F + ".mig-intro")
    patron.captura("articole_direct")


def test_def_668_articolele_nepotrivite_cu_371_nu_intra_iar_lista_are_stari(patron, firma):
    """668: „Fișele (3 articole, 4.100 lei) față de 371 din balanță (4.200) […] «Importă articolele» importă fără oprire […] Aceeași regulă
    ca la parteneri: contul care nu se potrivește nu intră. Lista de firme de aici nu are stări […]; observația «607 dedus din 371» repetată
    pe fiecare rând.” Pașii: Import date -> „Articole și stoc inițial” -> 3 articole (4.100) -> caseta „Față de balanța de deschidere …
    rândurile contului care nu se potrivește nu intră”: „371: stoc inițial 4.100,00 lei · balanță 4.200,00 lei · în stoc inițial lipsesc
    100,00 lei”; cele trei rânduri respinse, butonul inactiv; „607 dedus din 371” o singură dată -> Migrare cabinet -> „Articole și stoc
    inițial” -> „Altă firmă”: lista firmelor, cu starea pasului pe fiecare (firma: „obligatoriu”).
    MUTAȚIA: rândurile contului nepotrivit nu se mai resping -> ROȘU."""
    pg = patron.pg
    _balanta_api(patron, firma)
    _pas(patron, firma, "Articole")
    csv = ("denumire;um;cantitate;pret;cont stoc\nMarfa X Test;buc;10;150;371\nMarfa Y Test;kg;20;80;371\nMarfa Z Test;buc;5;200;371\n").encode()
    _incarca(patron, "articole_f7.csv", csv, "#mig-importa")
    t = " ".join(patron.fereastra().split())
    patron.captura("nepotrivit")
    assert "rândurile contului care nu se potrivește nu intră" in _txt(pg, "#mig-reconciliere")
    assert "371: stoc inițial 4.100,00 lei · balanță 4.200,00 lei · în stoc inițial lipsesc 100,00 lei" in _txt(pg, "#mig-reconciliere")
    assert pg.locator(".mig-prev tbody tr.mig-prev-respins:not(.mig-prev-motive)").count() == 3
    assert pg.is_disabled("#mig-importa")
    assert t.count("dedus din contul de stoc") <= 1, t[:3000]   # nu pe fiecare rând (rândurile respinse arată numai refuzul)
    assert sql('SELECT count(*) FROM "%s".articole' % firma["schema"]) == [(0,)]
    patron.firma(firma["nume"])
    _migrare(patron)
    _pas_meniu(pg, "Articole și stoc inițial").click()
    pg.wait_for_selector(_F + "#mig-alta-firma", timeout=20000)
    pg.click(_F + "#mig-alta-firma")
    pg.wait_for_selector(_F + "#mig-firme .mig-frand", timeout=20000)
    rand = pg.locator(_F + "#mig-firme .mig-frand", has_text=firma["nume"]).first
    patron.captura("lista_cu_stari")
    assert rand.locator("[data-stare-pas]").get_attribute("data-stare-pas") == "obligatoriu"


# ── 665 + 666 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_665_contul_nedefalcat_tine_pasul_deschis(patron, firma):
    """665: „F7 apare «✓ gata, 2 parteneri importați», deși 401 (3.000) a fost refuzat și a rămas nedefalcat. Verificarea de la «Am terminat
    soldurile pe parteneri» numește doar F5 și omite F7.” Pașii: balanța F7, partenerii numai pe 4111 -> Migrare cabinet -> „Solduri
    parteneri”: rândul firmei „de completat”, „2 parteneri importați · nedefalcat: 401 (creditor 3.000,00 lei în balanță) — partenerii dau
    0,00 lei”; „Am terminat soldurile pe parteneri” inactiv, iar motivul numește firma și 401.
    MUTAȚIA: rândul ignoră conturile nedefalcate (gata cu orice parteneri) -> ROȘU."""
    pg = patron.pg
    _balanta_api(patron, firma)
    _parteneri_f7(patron, firma)
    _migrare(patron)
    _pas_meniu(pg, "Solduri parteneri").click()
    pg.wait_for_selector("#mig-finalizeaza", timeout=20000)
    rand = pg.locator(".mig-frand", has_text=firma["nume"]).first
    rand.wait_for(timeout=20000)
    r = " ".join(rand.inner_text().split())
    patron.captura("lista_parteneri")
    assert "de completat" in r and "2 parteneri importați · nedefalcat: 401 (creditor 3.000,00 lei în balanță) — partenerii dau 0,00 lei" in r, r
    assert pg.is_disabled("#mig-finalizeaza")
    m = _txt(pg, "#mig-fin-motiv")
    assert firma["nume"] in m and "401 (creditor 3.000,00 lei în balanță)" in m, m


def test_def_666_firma_fara_solduri_nu_e_cazul_iar_contul_potrivit_sta_separat(patron, firma):
    """666: „Firma fără solduri (FISCALOS) apare «de încărcat» în loc de «nu e cazul»; contul care se potrivește (4111) stă în caseta roșie
    cu eroarea; mesajul pentru 401 se repetă identic pe fiecare rând.” Pașii: (a) firma fără balanță -> Migrare cabinet -> „Solduri
    parteneri”: rândul ei „nu e cazul”; (b) aceeași firmă cu balanța F7 -> Import date -> „Solduri parteneri” -> fișierul cu 4111 Alfa 1.500 +
    Beta 1.000 și 401 Furnizor 1.000 (balanța: 3.000) -> 4111 în nota „se potrivesc (4111)”, 401 singur în caseta de atenție; pe rândul
    401 motivul scurt „nu intră: pe contul 401 …”, iar lista refuzurilor îl spune o dată.
    MUTAȚIA: conturile potrivite și nepotrivite din nou în aceeași casetă -> ROȘU."""
    pg = patron.pg
    _rezumat_parteneri(firma)                        # date de pornire: tura de 5 minute a cronului (firma nouă n-are încă rezumatul)
    _migrare(patron)
    _pas_meniu(pg, "Solduri parteneri").click()
    rand = pg.locator(".mig-frand", has_text=firma["nume"]).first
    rand.wait_for(timeout=20000)
    patron.captura("nu_e_cazul")
    assert "nu e cazul" in rand.inner_text(), rand.inner_text()
    _balanta_api(patron, firma)
    _pas(patron, firma, "Solduri parteneri")
    csv = ("cont;cui;denumire;sold debitor;sold creditor\n4111;%s;%s;1500;0\n4111;%s;%s;1000;0\n401;%s;%s;0;1000\n"
           % (ALFA + BETA + FURNIZOR)).encode()
    _incarca(patron, "parteneri_f7.csv", csv, "#mig-salveaza-part")
    patron.captura("confruntare")
    assert "se potrivesc (4111)" in _txt(pg, "#mig-coer-cont summary")
    nep = _txt(pg, "#mig-coer-nepotrivit")
    assert "401" in nep and "4111" not in nep, nep
    motiv = _txt(pg, '.mig-prev tbody tr.mig-prev-motive[data-rand="4"]')
    assert motiv == "nu intră: contul 401 nu se potrivește cu soldul lui (cifrele, deasupra tabelului)", motiv
    assert _txt(pg, "#mig-refuzuri").count("pe 401, partenerii din fișier dau creditor 1.000,00 lei") == 1


# ── 667 + 581 + 624 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_667_rezumatul_lipit_al_balantei_e_mic_si_nu_acopera_tabelul(patron, firma):
    """667: „Tabelul are derulare proprie și capul acoperă primele rânduri (clasa 285); textul explicativ și avertismentul sunt paragrafe
    lungi”. Pașii: Import date -> „Solduri inițiale” (explicația lungă pliată în „Ce se citește din balanță”) -> balanța fără rulaje ->
    rezumatul lipit sus are numai titlul, totalurile și banda (avertismentul rulajelor e în pagină, deasupra tabelului) și ocupă mai puțin de
    o cincime din fereastră; primul rând al tabelului se vede sub el.
    MUTAȚIA: avertismentul rulajelor și nota balanței înapoi în rezumatul lipit -> ROȘU."""
    pg = patron.pg
    _pas(patron, firma, "Solduri ini")
    assert pg.locator("details#mig-cum-balanta").count() == 1 and not pg.eval_on_selector("details#mig-cum-balanta", "d => d.open")
    _incarca(patron, "balanta_f7.csv", BALANTA_CSV, "#mig-salveaza-sold")
    patron.captura("previzualizare")
    assert pg.locator(".rezumat-fix #mig-rulaje, .rezumat-fix .caseta-info, .rezumat-fix details").count() == 0
    h = pg.evaluate("() => { const r = document.querySelector('.rezumat-fix').getBoundingClientRect(); "
                    "const f = document.querySelector('.fereastra:last-of-type').getBoundingClientRect(); return r.height / f.height; }")
    assert h < 0.2, h
    pg.locator(".mig-prev tbody tr").first.scroll_into_view_if_needed()
    acoperit = pg.evaluate("() => { const r = document.querySelector('.rezumat-fix').getBoundingClientRect(); "
                           "const t = document.querySelector('.mig-prev tbody tr').getBoundingClientRect(); return t.top < r.bottom - 1; }")
    assert not acoperit


def test_def_581_refuzurile_in_pagina_si_banda_cu_filtre(patron, firma):
    """581: „casetele roșii fixe strâng tabelul rândurilor într-o bară albă și acoperă câmpul de dată la derulare […] Etichetele «1 rând cu
    observație» nu se pot apăsa.” Pașii: Import date -> „Solduri parteneri” (fără balanță) -> fișierul cu un CUI greșit -> caseta
    refuzurilor e în pagină (deasupra tabelului), nu în bara lipită jos -> „1 rând respins — nu intră” (buton) -> tabelul arată numai rândul
    respins -> încă o apăsare: toate rândurile.
    MUTAȚIA: caseta refuzurilor înapoi în bara de jos -> ROȘU."""
    pg = patron.pg
    _balanta_api(patron, firma, (("4111", 100, 0), ("1012", 0, 100)))   # partenerul bun dă soldul lui 4111 (346): numai CUI-ul greșit e respins
    _pas(patron, firma, "Solduri parteneri")
    csv = ("cont;cui;denumire;sold debitor;sold creditor\n4111;%s;%s;100;0\n4111;14837429;CUI GRESIT SRL;50;0\n" % ALFA).encode()
    _incarca(patron, "parteneri_581.csv", csv, "#mig-salveaza-part")
    patron.captura("refuzuri")
    assert pg.locator(".bara-fixa #mig-refuzuri").count() == 0 and pg.locator("#mig-refuzuri").count() == 1
    assert pg.evaluate("() => { const c = document.querySelector('#mig-refuzuri'), t = document.querySelector('.mig-prev-cutie');"
                       " return !!(c.compareDocumentPosition(t) & Node.DOCUMENT_POSITION_FOLLOWING); }")
    pg.click("[data-filtru-stare='respins']")
    vizibile = pg.eval_on_selector_all(".mig-prev tbody tr:not(.mig-prev-motive)", "rs => rs.filter((r) => !r.hidden).map((r) => r.dataset.rand)")
    patron.captura("filtru_respinse")
    assert vizibile == ["3"], vizibile
    pg.click("[data-filtru-stare='respins']")
    assert pg.eval_on_selector_all(".mig-prev tbody tr:not(.mig-prev-motive)", "rs => rs.filter((r) => !r.hidden).length") == 2


def test_def_624_observatiile_la_clic_si_respinsele_grupate(patron, firma):
    """624 (clasă: ecrane cu liste — importuri și audit): „observații la clic; respinsele grupate”. Pașii: balanța F7 (371 D 4.200) -> Import
    date -> „Articole și stoc inițial” -> cele trei articole F7 (4.100) -> caseta refuzurilor spune motivul o singură dată, cu toate rândurile
    lui: „rândurile 2, 3, 4: nu intră: articolele de pe contul 371 dau 4.100,00 lei …”; banda „3 rânduri respinse — nu intră” e buton.
    MUTAȚIA: lista refuzurilor negrupată (un rând pe fiecare refuz) -> ROȘU."""
    pg = patron.pg
    _balanta_api(patron, firma)
    _pas(patron, firma, "Articole")
    csv = ("denumire;um;cantitate;pret;cont stoc\nMarfa X Test;buc;10;150;371\nMarfa Y Test;kg;20;80;371\nMarfa Z Test;buc;5;200;371\n").encode()
    _incarca(patron, "articole_624.csv", csv, "#mig-importa")
    patron.captura("grupate")
    lista = pg.eval_on_selector_all("#mig-refuzuri li", "ls => ls.map((l) => l.innerText.replace(/\\s+/g, ' ').trim())")
    assert lista == ["rândurile 2, 3, 4: nu intră: articolele de pe contul 371 dau 4.100,00 lei, iar balanța de deschidere are 4.200,00 lei "
                     "(diferență 100,00 lei)"], lista
    assert pg.locator("button[data-filtru-stare='respins']").count() == 1


# ── 669 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_669_soldul_preluat_al_clientului_se_incaseaza_din_casa(patron, firma):
    """669: „Client Alfa Test SRL are 1.500 lei pe 4111 din soldurile pe parteneri preluate, dar la încasare aplicația spune «Nicio factură
    emisă neîncasată pentru acest CUI» și tratează suma ca avans […] Aceeași verificare la plata către furnizor și la potrivirea extrasului
    bancar.” Pașii: balanța F7 cu 401 pe furnizor, partenerii pe 4111 și 401 -> Casă -> „+ Dispoziție nouă” -> încasare de la client,
    1.500,00, CUI-ul lui Alfa: „Factura încasată” oferă „Sold la 30.09.2026 · <Alfa> · rămas 1.500,00 lei” -> bifată -> „Adaugă”: nota
    5311 = 4111 1.500,00, legată de documentul preluat (nu avans, fără 419 / 4427) -> plata furnizorului 1.000: „Sold la 30.09.2026 ·
    <Furnizor>”, nota 401 = 5311 -> Bancă: potrivirea oferă soldul preluat al lui Beta (1.000).
    MUTAȚIA: facturile deschise fără documentele preluate -> „Nicio factură emisă neîncasată” -> ROȘU."""
    pg = patron.pg
    s = firma["schema"]
    pregateste_firma(patron, firma)
    _balanta_api(patron, firma, (("1012", 0, 200), ("117", 0, 12000), ("371", 4200, 0), ("401", 0, 1000), ("4111", 2500, 0),
                                 ("5121", 6000, 0), ("5311", 500, 0)))
    _parteneri_api(patron, firma, (("4111",) + ALFA + (1500, 0), ("4111",) + BETA + (1000, 0), ("401",) + FURNIZOR + (0, 1000)))
    doc = {r[1]: r[0] for r in sql('SELECT id, tert_cui FROM "%s".facturi WHERE tip = \'preluata\'' % s)}
    ziua = _dt.date(2026, 10, 5).isoformat()
    for cat, suma, (cui, nume), sens in (("incasare_client", "1500", ALFA, ("5311", "4111")), ("plata_furnizor", "1000", FURNIZOR, ("401", "5311"))):
        patron.firma(firma["nume"])
        _card(patron, "casa", "#c-toggle")
        pg.click("#c-toggle")
        pg.fill("#c-data", ziua)
        pg.select_option("#c-cat", cat)
        pg.fill("#c-suma", suma)
        pg.fill("#c-cui", cui)
        pg.dispatch_event("#c-campuri", "change")
        pg.wait_for_selector("#c-facturi [data-cf='%d']" % doc[cui], timeout=30000)
        oferta = " ".join(pg.inner_text("#c-facturi").split())
        patron.captura("casa_" + cat)
        assert "Sold la 30.09.2026" in oferta and nume in oferta and "rămas %s,00 lei" % ("1.500" if suma == "1500" else "1.000") in oferta, oferta
        assert "Nicio factură" not in oferta
        pg.check("#c-facturi [data-cf='%d']" % doc[cui])
        pg.click("#c-adauga")
        pg.wait_for_function("() => document.body.innerText.includes('Dispoziția a fost salvată')", timeout=30000)
        linii = sql('SELECT l.cont_debit, l.cont_credit, l.suma::text FROM "%s".inregistrari i JOIN "%s".inregistrari_linii l '
                    "ON l.inregistrare_id = i.id WHERE i.factura_id = %%s" % (s, s), (doc[cui],))
        # OMFP 1802/2014: încasarea creanței preluate stinge 4111 (5311 = 4111); plata datoriei preluate stinge 401 (401 = 5311) — fără avans
        assert [(d.split(".")[0], c.split(".")[0], v) for d, c, v in linii] == [sens + ("%s.00" % suma,)], linii
    r = _ok(_api(patron, "GET", "/tenants/%d/banca/reconciliere/facturi-deschise" % firma["tenant_id"]), "documentele deschise")
    beta = [x for x in r.get("facturi", []) if str(x.get("tert_cui") or "").endswith(BETA[0])]
    assert len(beta) == 1 and beta[0]["directie"] == "emisa" and float(beta[0]["sold"]) == 1000.0, r


# ── 580 + 584 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_580_import_date_arata_ce_s_a_adus_deja(patron, firma):
    """580: „Lista straturilor și fiecare ecran de import nu arată ce s-a adus deja; că F6 are balanță la 30.09.2026 (16 conturi) afli abia
    după ce încarci un fișier.” Pașii: firma cu balanța F7 -> Import date: rândul „Solduri inițiale” spune „balanța la 30.09.2026: 7 conturi”,
    „gata” -> „Solduri inițiale”: înainte de orice fișier, „Există deja: balanța la 30.09.2026: 7 conturi. Un fișier nou înlocuiește
    balanța de deschidere (după confirmare, …)”.
    MUTAȚIA: ecranul importului nu mai spune ce există -> ROȘU."""
    pg = patron.pg
    _balanta_api(patron, firma)
    patron.firma(firma["nume"])
    pg.click("#fa-import")
    pg.wait_for_selector(".mig-frand[data-strat='solduri'] [data-stare-pas]", timeout=20000)
    rand = " ".join(pg.locator(".mig-frand[data-strat='solduri']").inner_text().split())
    patron.captura("lista")
    assert "balanța la 30.09.2026: 7 conturi" in rand and "gata" in rand, rand
    pg.locator(".mig-frand", has_text="Solduri ini").first.click()
    pg.wait_for_selector("#mig-exista", timeout=20000)
    patron.captura("ecran_import")
    assert _txt(pg, "#mig-exista").startswith("Există deja: balanța la 30.09.2026: 7 conturi. Un fișier nou înlocuiește balanța de deschidere")


def test_def_584_salariati_si_istoric_spun_ce_exista_si_ce_face_importul(patron, firma):
    """584: „Salariați, Istoric declarații: nu spun ce există deja (F6: 3 salariați, 45 declarații) și dacă importul adaugă, dublează sau
    înlocuiește”. Pașii: Import date -> „Salariați” (firmă fără salariați): „Nu e nimic adus încă la acest pas. Importul adaugă salariații
    noi și actualizează fișele celor cu același CNP …” -> „Istoric declarații”: „… Un fișier nou înlocuiește istoricul preluat (după
    confirmare); declarațiile depuse prin iConta.eu rămân.”
    MUTAȚIA: comportamentul importului nu se mai spune -> ROȘU."""
    pg = patron.pg
    _pas(patron, firma, "Salaria")
    pg.wait_for_selector("#mig-exista", timeout=20000)
    patron.captura("salariati")
    assert _txt(pg, "#mig-exista") == ("Nu e nimic adus încă la acest pas. Importul adaugă salariații noi și actualizează fișele celor cu același "
                                       "CNP (după confirmare); nu dublează și nu șterge salariații care lipsesc din fișier.")
    _pas(patron, firma, "Istoric declara")
    pg.wait_for_selector("#mig-exista", timeout=20000)
    assert "Un fișier nou înlocuiește istoricul preluat (după confirmare); declarațiile depuse prin iConta.eu rămân." in _txt(pg, "#mig-exista")


# ── 582 + 583 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_582_dublura_si_celelalte_greseli_se_vad_deodata(patron, firma):
    """582: „Verificarea dublurilor oprește tot înainte de celelalte verificări; restul greșelilor apar abia la reîncărcare.” Pașii: Import
    date -> „Solduri parteneri” -> fișierul cu Alfa de două ori pe 4111, un CUI greșit și Beta -> previzualizarea (nu refuzul fișierului):
    rândurile 2 și 3 respinse („apare pe același cont 4111 și pe rândul …”), rândul 4 respins (CUI), rândul 5 intră.
    MUTAȚIA: dublura oprește din nou citirea fișierului -> ROȘU."""
    pg = patron.pg
    _balanta_api(patron, firma, (("4111", 700, 0), ("1012", 0, 700)))   # Beta (700) dă soldul lui 4111: rândul lui intră
    _pas(patron, firma, "Solduri parteneri")
    csv = ("cont;cui;denumire;sold debitor;sold creditor\n4111;%s;%s;500;0\n4111;%s;%s;300;0\n4111;14837429;CUI GRESIT SRL;200;0\n"
           "4111;%s;%s;700;0\n" % (ALFA + ALFA + BETA)).encode()
    _incarca(patron, "parteneri_582.csv", csv, "#mig-salveaza-part")
    patron.captura("deodata")
    stari = dict(pg.eval_on_selector_all(".mig-prev tbody tr:not(.mig-prev-motive)", "rs => rs.map((r) => [r.dataset.rand, r.className])"))
    assert all("mig-prev-respins" in stari[n] for n in ("2", "3", "4")) and "mig-prev-ok" in stari["5"], stari
    assert "apare pe același cont 4111 și pe rândul 3" in _txt(pg, '.mig-prev tr.mig-prev-motive[data-rand="2"]')


def test_def_583_inlocuirea_spune_zero_randuri_valide_din_cate_s_au_citit(patron, firma):
    """583: „Sus «4 parteneri · debit 1.700», în casetă «Fișierul nou: 0 parteneri, debit 0,00»: trebuie «0 rânduri valide din 4».” Pașii:
    firma are deja soldurile pe parteneri (fără balanță) -> Import date -> „Solduri parteneri” -> un fișier cu 4 rânduri, toate cu CUI
    greșit -> sus „4 rânduri citite (0 intră)”, iar caseta înlocuirii: „Fișierul nou: 0 rânduri valide din 4 — nu intră nimic.”
    MUTAȚIA: textul fișierului nou fără numărul rândurilor citite -> ROȘU."""
    pg = patron.pg
    _balanta_api(patron, firma, (("4111", 500, 0), ("1012", 0, 500)))
    _parteneri_api(patron, firma, (("4111",) + ALFA + (500, 0),))   # date de pornire: soldurile existente (ecranul — test_def_666)
    _pas(patron, firma, "Solduri parteneri")
    csv = ("cont;cui;denumire;sold debitor;sold creditor\n" + "".join("4111;1483742%d;GRESIT %d SRL;%d;0\n" % (n, n, 100 * n) for n in (1, 2, 3, 4))).encode()
    _incarca(patron, "parteneri_583.csv", csv, "#mig-salveaza-part")
    patron.captura("zero_din_patru")
    assert "4 rânduri citite (0 intră)" in _txt(pg, ".mig-sold-rezumat")
    assert "Fișierul nou: 0 rânduri valide din 4 — nu intră nimic." in text_din_card(pg, "#mig-inlocuire")[0]   # [lotul 14, 687] textul întreg e în cardul deschis


# ── 585 + 586 + 587 + 588 + 590 ──────────────────────────────────────────────────────────────────────────────────────────────────
def _rand(pg, n):
    return " ".join(" ".join(pg.locator('.mig-prev tbody tr[data-rand="%d"]' % n).all_inner_texts()).split())


def test_def_585_salariul_sub_minim_e_semnalat(patron, firma):
    """585: „3.000 lei brut la normă întreagă (sub minimul de 4.050) intră fără semnal.” Pașii: Import date -> „Salariați” -> un salariat
    cu 3.000 lei brut, normă întreagă -> rândul „intră, cu observație”: „… salariul de bază 3.000,00 lei e sub salariul minim brut 4.325,00
    lei la normă întreagă (Codul muncii art.164 alin.(6)) …” (HG 146/2026 art.1: 4.325 lei de la 01.07.2026).
    MUTAȚIA: semnalul sub minim scos -> ROȘU."""
    pg = patron.pg
    _pas(patron, firma, "Salaria")
    csv = ("nume;prenume;cnp;data angajare;functie;norma;ore;functie de baza;scutit contributie minima;persoane in intretinere;brut;judet;cor\n"
           "POPESCU;ANA;2900215410011;2024-01-15;Contabil;intreaga;8;da;nu;0;3000;B;251401\n").encode()
    _incarca(patron, "salariati_585.csv", csv, "#mig-salveaza-sal")
    r = _rand(pg, 2)
    patron.captura("sub_minim")
    assert "intră, cu observație" in r and ("salariul de bază 3.000,00 lei e sub salariul minim brut 4.325,00 lei la normă întreagă "
                                           "(Codul muncii art.164 alin.(6))") in r, r


def test_def_586_d100_pe_luna_02_spune_cum_e_citita(patron, firma):
    """586: „D100 cu luna 02 intră fără să spună cum a fost citit (lunar, ex. impozit pe dividende, vs trimestrial).” Pașii: Import date ->
    „Istoric declarații” -> D100 pe 02/2026, depusă 20.03.2026 -> rândul „intră, cu observație”: „luna 02 nu încheie un trimestru — rândul e
    citit ca D100 lunară (de exemplu impozitul pe dividende …); dacă era D100 trimestrială …, scrie luna de sfârșit a trimestrului (03 = T1)”
    (CF art.43 alin.(2)).
    MUTAȚIA: semnalul D100 lunare scos -> ROȘU."""
    pg = patron.pg
    _pas(patron, firma, "Istoric declara")
    _incarca(patron, "istoric_586.csv", "tip;an;luna;data depunere;suma de plata\nD100;2026;2;2026-03-20;160\n".encode(), "#mig-salveaza-ist")
    r = _rand(pg, 2)
    patron.captura("d100_lunara")
    assert "intră, cu observație" in r and "luna 02 nu încheie un trimestru — rândul e citit ca D100 lunară" in r, r
    assert "scrie luna de sfârșit a trimestrului (03 = T1)" in r, r


MF_CSV = ("cod;denumire;valoare intrare;data PIF;durata luni;metoda;cont imobilizare;cont amortizare;amortizare cumulata;"
          "valoare reziduala la sfarsitul duratei (de obicei 0)\n"
          "MF1;Utilaj;9000;2025-01-10;60;liniara;2131;2813;1500;6000\n"
          "MF2;Scaun birou;1800;2026-03-10;36;liniara;2131;2813;0;0\n").encode()


def test_def_587_valoarea_reziduala_mare_e_semnalata(patron, firma):
    """587: „Coloana «rezidual» din model se confundă cu «valoarea rămasă» din exporturile vechi; o valoare reziduală mare (2/3 din valoare) nu
    e semnalată; modelul trebuie să spună «valoare reziduală la sfârșitul duratei (de obicei 0)».” Pașii: Import date -> „Mijloace fixe”:
    textul ecranului numește „valoarea reziduală la sfârșitul duratei, de obicei 0 — nu valoarea rămasă” -> registrul cu MF1 (9.000,
    reziduală 6.000) -> rândul „intră, cu observație”: „valoarea reziduală 6.000,00 lei (67% din valoarea de intrare) nu se amortizează”.
    MUTAȚIA: semnalul valorii reziduale scos -> ROȘU."""
    pg = patron.pg
    _pas(patron, firma, "Mijloace")
    assert "valoarea reziduală la sfârșitul duratei, de obicei 0 — nu valoarea rămasă" in _txt(pg, ".mig-intro")
    _incarca(patron, "mf_587.csv", MF_CSV, "#mig-salveaza-mf")
    r = _rand(pg, 2)
    patron.captura("rezidual")
    # OMFP 1802/2014 pct.139 alin.(2): valoarea amortizabilă = costul minus valoarea reziduală
    assert "valoarea reziduală 6.000,00 lei (67% din valoarea de intrare) nu se amortizează" in r, r


def test_def_588_bunul_sub_plafon_nu_intra_ca_mijloc_fix(patron, firma):
    """588: „Bun de 1.800 lei «sub plafonul de mijloc fix de 5.000 lei» intră totuși ca mijloc fix; trebuie propus obiect de inventar.” Pașii:
    Import date -> „Mijloace fixe” -> MF2 Scaun birou 1.800 lei, PIF 10.03.2026 -> rândul „respins — nu intră”: „… sub plafonul de mijloc fix
    de 5.000,00 lei la data intrării 10.03.2026 (CF art.28 alin.(2) lit.b)) — e obiect de inventar …” (OUG 8/2026 art.6 pct.7, aplicat din
    2026 — art.10 alin.(2)); butonul salvează numai rândul bun.
    MUTAȚIA: bunul sub plafon nu se mai respinge -> ROȘU."""
    pg = patron.pg
    _pas(patron, firma, "Mijloace")
    _incarca(patron, "mf_588.csv", MF_CSV, "#mig-salveaza-mf")
    r = _rand(pg, 3)
    patron.captura("sub_plafon")
    assert "respins — nu intră" in r and ("valoarea de intrare 1.800,00 lei e sub plafonul de mijloc fix de 5.000,00 lei la data intrării "
                                          "10.03.2026 (CF art.28 alin.(2) lit.b)) — e obiect de inventar") in r, r
    assert _txt(pg, "#mig-salveaza-mf") == "Salvează rândul bun (mijloace fixe)"


def test_def_590_articolul_dublat_respinge_ambele_randuri(patron, firma):
    """590: „La articol dublat, primul rând intră cu 10 buc (stocul real 13); trebuie respinse ambele până la cumulare, ca la parteneri.”
    Pașii: Import date -> „Articole și stoc inițial” -> „Marfa valida” 10 buc și „Marfa valida” 3 buc, „Alta marfa” 1 buc -> rândurile 2 și
    3 respinse („… adună cantitățile în fișier …”), rândul 4 intră.
    MUTAȚIA: numai a doua apariție respinsă (ca înainte) -> ROȘU."""
    pg = patron.pg
    _pas(patron, firma, "Articole")
    csv = "denumire;um;cantitate;pret;cont stoc\nMarfa valida;buc;10;5;371\nMarfa valida;buc;3;5;371\nAlta marfa;buc;1;5;371\n".encode()
    _incarca(patron, "articole_590.csv", csv, "#mig-importa")
    patron.captura("dublat")
    assert "respins" in _rand(pg, 2) and "respins" in _rand(pg, 3) and "adună cantitățile în fișier" in _rand(pg, 2)
    assert "respins" not in _rand(pg, 4)


# ── 609 + 623 + 251 + 252 (auditul de preluare) ──────────────────────────────────────────────────────────────────────────────────
def _audit(patron, firma):
    """Control fiscal -> firma -> „Rulează auditul de preluare”: textul ultimului audit."""
    from e2e_bloc_d import _control_firma
    pg = patron.pg
    _control_firma(patron, firma)
    pg.wait_for_selector(_F + "#cf-audit-run", timeout=30000)
    pg.click(_F + "#cf-audit-run")
    pg.wait_for_function("() => (document.querySelector('.fereastra:last-of-type #cf-audit-istoric') || {innerText: ''}).innerText"
                         ".includes('audit')", timeout=60000)
    return " ".join(pg.inner_text(_F + "#cf-audit-istoric").split())


def test_def_609_auditul_scrie_soldurile_si_diferentele_fara_minus(patron, firma):
    """609: „Soldurile creditoare și diferențele apar cu minus («401: −9.520,00»), nu ca sold C.” Pașii: balanța cu 2131 D 24.000 și 2813 C
    6.000, fără registrul mijloacelor fixe -> Control fiscal -> auditul de preluare: „Contul 2813 (amortizarea preluată): registrul 0,00 lei,
    balanța creditor 6.000,00 lei — în registru lipsesc 6.000,00 lei față de balanță.” — nicio sumă cu minus.
    MUTAȚIA: diferența scrisă din nou cu semn -> ROȘU."""
    _balanta_api(patron, firma, (("2131", 24000, 0), ("2813", 0, 6000), ("1012", 0, 18000)))
    t = _audit(patron, firma)
    patron.captura("audit")
    assert ("Contul 2813 (amortizarea preluată): registrul 0,00 lei, balanța creditor 6.000,00 lei — în registru lipsesc 6.000,00 lei față "
            "de balanță.") in t, t[:3000]
    assert "-6.000" not in t and "−6.000" not in t and "-24.000" not in t, t[:3000]


def test_def_623_auditul_spune_temeiul_o_singura_data_pe_verificare(patron, firma):
    """623: „Audit de preluare: același paragraf repetat la fiecare rând”. Pașii: balanța cu 4423, 444 și 4315 (datorii fiscale), fără istoricul
    declarațiilor -> auditul: grupul „Neverificat” are constatările istoricului (fiecare sold numit), iar temeiul lor („Un sold de deschidere
    pe un cont de datorie/creanță fiscală …”) apare o singură dată.
    MUTAȚIA: fiecare constatare cu temeiul ei, ca înainte -> ROȘU."""
    pg = patron.pg
    _balanta_api(patron, firma, (("4423", 0, 2940), ("444", 0, 520), ("4315", 0, 2000), ("5121", 5460, 0)))
    t = _audit(patron, firma)
    patron.captura("audit_grupat")
    assert "Sold de deschidere pe 4423 (TVA de plată, 2.940,00 lei) fără D300 în istoricul importat." in t, t[:3000]
    assert "Sold de deschidere pe 444 (impozit pe venituri din salarii, 520,00 lei) fără D112 în istoricul importat." in t
    assert t.count("Un sold de deschidere pe un cont de datorie/creanță fiscală provine dintr-o declarație") == 1, t[:4000]


def test_def_251_auditul_numeste_textele_stricate_de_un_import_vechi(patron, firma):
    """251 (date existente): „un CSV salvat în Windows-1250 strică diacriticele” — citirea e reparată (lotul 12); textele aduse înainte au „�”
    în loc de literă și nu se pot reface din bază. Pașii: soldurile pe parteneri cu denumirea „Br\\ufffdt\\ufffdria Ștefan SRL” (cum o
    scria importul vechi) -> auditul de preluare: „Texte cu litere pierdute la import: soldurile pe parteneri: „Br�t�ria Ștefan SRL”.” cu
    „Încarcă din nou fișierul pasului …”.
    MUTAȚIA: verificarea textelor importate scoasă din audit -> ROȘU."""
    _balanta_api(patron, firma, (("4111", 500, 0), ("1012", 0, 500)))
    _parteneri_api(patron, firma, (("4111", ALFA[0], "Br�t�ria Ștefan SRL", 500, 0),))   # date de pornire: textul vechi, stricat
    t = _audit(patron, firma)
    patron.captura("texte_stricate")
    assert "Texte cu litere pierdute la import: soldurile pe parteneri: „Br�t�ria Ștefan SRL”" in t, t[:3000]
    assert "Încarcă din nou fișierul pasului (Import date): acum se citește întreg, cu diacritice." in t


def test_def_252_tva_din_fisier_sau_calculat_si_marcat_de_verificat(patron, firma):
    """252 (decizia Costin 13.1, verbatim: „la facturile preluate, dacă fișierul are suma TVA, se ia suma din fișier; doar unde lipsește se
    calculează la cota standard, iar factura e marcată «de verificat».”). Pașii: firma aplică TVA la încasare din 01.01.2026 -> Import date ->
    „Solduri parteneri” -> situația pe facturi cu coloana „TVA”: FB-1 1.090 cu TVA 90 (cota 9%), FB-2 1.210 fără TVA -> coloana „TVA din
    rest”: „FB-1: 90,00; FB-2: calculat, de verificat” -> „Salvează partenerii”: „TVA calculat la cota standard …, de verificat: FB-2 (…)”
    -> în evidență FB-1 cu TVA 90,00 nemarcată, FB-2 cu TVA 210,00 (1.210 × 21/121, CF art.291 alin.(1)) marcată -> auditul o numește.
    MUTAȚIA: suma din fișier ignorată (TVA calculat pe toate) -> ROȘU."""
    pg = patron.pg
    s = firma["schema"]
    pregateste_firma(patron, firma)
    # perioada TVA la încasare a firmei, pe drumul aplicației (ruta ecranului Date firmă, `POST tva-incasare` -> `regim_tva_incasare.salveaza`,
    # care scrie perioada și sincronizează indicatorul; ecranul e probat în e2e_lot10_date_firma / e2e_lot11_t)
    _ok(_api(patron, "POST", "/tenants/%d/tva-incasare" % firma["tenant_id"], {"aplica": "da", "de_la": "2026-01-01"}),
        "sistemul TVA la încasare de la 01.01.2026")
    assert sql('SELECT de_la::text, pana_la FROM "%s".tva_incasare_perioade' % s) == [("2026-01-01", None)]
    _balanta_api(patron, firma, (("4111", 2300, 0), ("4428", 0, 300), ("1012", 0, 2000)))
    _pas(patron, firma, "Solduri parteneri")
    csv = ("Cont;Cod fiscal;Denumire;Nr. factură;Data;Scadență;Sumă neachitată;TVA la încasare;TVA\n"
           "4111;RO%s;%s;FB-1;10.09.2026;;1090,00;da;90,00\n4111;RO%s;%s;FB-2;15.09.2026;;1210,00;da;\n" % (BETA + BETA)).encode()
    _incarca(patron, "situatie_252.csv", csv, "#mig-salveaza-part")
    assert "FB-1: 90,00; FB-2: calculat, de verificat" in _rand(pg, 2), _rand(pg, 2)
    patron.captura("previzualizare_tva")
    pg.click("#mig-salveaza-part")
    pg.wait_for_function("() => document.body.innerText.includes('de verificat: FB-2')", timeout=30000)
    patron.captura("salvat_de_verificat")
    tva = {n: (str(v), dv) for n, v, dv in sql('SELECT numar, tva, tva_de_verificat FROM "%s".facturi WHERE tip = \'preluata\'' % s)}
    assert tva == {"FB-1": ("90.00", False), "FB-2": ("210.00", True)}, tva
    t = _audit(patron, firma)
    assert "TVA neexigibil calculat la cota standard (fișierul n-avea suma TVA), de verificat: FB-2" in t, t[:3000]


# ── fișierele dovezilor pe firmele de test (`frontend_test/dovada/dovezi_lot13_migr.json`, pasul „incarca”) ─────────────────────
def fisier_f7_parteneri_dublura():
    """[581, 582, 583, 666 pe F7] Partenerii lui F7 (Alfa 401007106, Beta 401007203 — CUI-urile copiei), cu Alfa de două ori, un CUI greșit
    și Beta: dublura, CUI-ul și confruntarea cu 4111 (2.500) se văd deodată; niciun rând nu intră (nu se salvează nimic)."""
    return ("cont;cui;denumire;sold debitor;sold creditor\n4111;401007106;Client Alfa Test SRL;1500;0\n4111;401007106;Client Alfa Test SRL;300;0\n"
            "4111;14837429;CUI GRESIT SRL;200;0\n4111;401007203;Client Beta Test SRL;1000;0\n").encode("utf-8")


def fisier_f7_articole():
    """[668, 624 pe F7] Cele trei articole ale lui F7, ca în retestul lui Costin (4.100 lei față de 371 = 4.200)."""
    return ("denumire;um;cantitate;pret;cont stoc\nMarfa X Test;buc;10;150;371\nMarfa Y Test;kg;20;80;371\nMarfa Z Test;buc;5;200;371\n").encode("utf-8")


def fisier_f7_balanta():
    """[667 pe F7] Balanța lui F7 la 30.09.2026, cum a încărcat-o Costin (numai solduri finale)."""
    return BALANTA_CSV


def fisier_salariat_sub_minim():
    """[585] Un salariat cu 3.000 lei brut la normă întreagă."""
    return ("nume;prenume;cnp;data angajare;functie;norma;ore;functie de baza;scutit contributie minima;persoane in intretinere;brut;judet;cor\n"
            "POPESCU;ANA;2900215410011;2024-01-15;Contabil;intreaga;8;da;nu;0;3000;B;251401\n").encode("utf-8")


def fisier_d100_luna_02():
    """[586] D100 pe 02/2026."""
    return "tip;an;luna;data depunere;suma de plata\nD100;2026;2;2026-03-20;160\n".encode("utf-8")


def fisier_mijloace():
    """[587, 588] Utilajul cu valoarea reziduală 6.000 din 9.000 și scaunul de 1.800 lei din 10.03.2026."""
    return MF_CSV


def fisier_articol_dublat():
    """[590] „Marfa valida” pe două rânduri (10 + 3 buc)."""
    return "denumire;um;cantitate;pret;cont stoc\nMarfa valida;buc;10;5;371\nMarfa valida;buc;3;5;371\nAlta marfa;buc;1;5;371\n".encode("utf-8")


def fisier_f6_cu_tva():
    """[252 pe F6] Situația partenerilor lui F6 pe facturi, cu coloana „TVA” (suma din restul fiecărei facturi)."""
    return ("Cont;Cod fiscal;Denumire;Nr. factură;Data;Scadență;Sumă neachitată;TVA\n"
            "4111;401006100;Alfa Distribuție SRL;F6-A1;05.09.2026;05.10.2026;5000,00;867,77\n"
            "4111;401006100;Alfa Distribuție SRL;F6-A2;20.09.2026;20.10.2026;2140,00;\n"
            "4111;401006208;Beta Construct SRL;F6-B1;15.09.2026;15.10.2026;4760,00;\n"
            "401;401006305;Gamma Logistic SRL;G-901;10.09.2026;10.10.2026;5950,00;\n"
            "401;401006402;Delta Ambalaje SRL;D-77;25.09.2026;;3570,00;\n").encode("utf-8")


def fisier_extras_c125():
    """[C125 pe F1] Extrasul cu o încasare (+125,00) și o plată (−12,50), azi: încărcat de două ori, al doilea import le spune „găsite
    deja”, fiecare cu sensul ei (încasare / plată) — rândul vine din răspunsul importului (`deja`), unde cheia afirmației scria peste tip."""
    zi = _dt.date.today().strftime("%d.%m.%Y")
    return ("Data;Detalii;Suma\n%s;Incasare dovada C125;125,00\n%s;Plata dovada C125;-12,50\n" % (zi, zi)).encode("utf-8")
