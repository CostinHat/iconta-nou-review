# -*- coding: utf-8 -*-
"""Lotul 12, comanda Costin 12.1 — pachetul „decl” (declarațiile): 486, C48, 485, C19, 185, 493, pe aplicația din index, pe baza de TEST,
pe firme NOI (`firma_noua`).

DATE DE PORNIRE fără ecran (declarate): facturile, partenerii și nota de avans se scriu direct în schema firmei noi (SQL), ca la
`e2e_lot10_d406.py` (C69) — ecranul probat e Declarații, nu emiterea. CUI-uri cu cifra de control verificată (algoritmul din CLAUDE.md,
`core/test_lot12_decl_486_d406.py::test_fixtura_e_valida`): 2864518, 1590082; partenerii străini au coduri de TVA sintetice (DE / US),
clasificate după prefix. IBAN sintetic RO59BTRLRONCRT0C69TEST01, cifra de control mod-97 verificată (`salariati_api.iban_valid`).

Temeiuri (citate pe linia aserțiunii): OPANAF 1783/2021 anexa 3 pct.11 și pct.27 (486); OPANAF 2194/2025 anexa 2 lit.E / F pct.10 (C19) și
secțiunea a 2-a pct.5 (185); CF art.42 alin.(4) (493, D177)."""
import pytest

from conftest import alege_perioada, alege_tipul, firma_noua, sql
from e2e_bloc_a import _api, _card, _ok, _profil as _profil_bloc_a, pregateste_firma
from e2e_bloc_d import _nota_validata

IBAN = "RO59BTRLRONCRT0C69TEST01"


@pytest.fixture()
def firma_decl():
    for f in firma_noua():
        yield f


def _profil(patron, firma, regim="profit"):
    """Date firmă complete pentru D394 / D406 (localitate, telefon, IBAN, declarant), plătitor de TVA lunar."""
    pregateste_firma(patron, firma, platitor=True, regim_fiscal=regim)
    p = _profil_bloc_a(firma)   # pe ruta ecranului Date firmă, ca `pregateste_firma`
    p.update({"adresa": "Str. Probei 9", "oras": "Cluj-Napoca", "judet": "CJ", "banca": "BT", "iban": IBAN, "telefon": "0264111222",
              "declarant_nume": "POPESCU", "declarant_prenume": "ION", "declarant_functie": "ADMINISTRATOR"})
    _ok(_api(patron, "POST", "/tenants/%d/firma-profil/date" % firma["tenant_id"], p), "Date firmă")


def _factura(firma, serie, numar, data, directie, cui, nume, linii, oras=None, axa=None):
    s = firma["schema"]
    total = sum(b * (100 + c) / 100 for b, c in linii)
    tva = sum(b * c / 100 for b, c in linii)
    # partenerii probei: din UE, din afara UE, persoană fizică fără localitate, cu axa IC; ecranul probat e Declarații
    # date-de-pornire: factura cu seria / numărul probei — formularul de emitere numerotează singur, pe seria firmei
    fid = sql('INSERT INTO "%s".facturi (serie, numar, data_emitere, directie, total, tva, tert_cui, tert_nume, tert_oras, status, axa_ic, '
              'taxare_inversa) VALUES (%%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, false) RETURNING id' % s,
              (serie, numar, data, directie, total, tva, cui, nume, oras, directie, axa))[0][0]
    for b, c in linii:
        # date-de-pornire: liniile facturii de pornire de mai sus
        sql('INSERT INTO "%s".factura_linii (factura_id, descriere, um, cantitate, pret_unitar, cota_tva) VALUES (%%s, %%s, %%s, 1, %%s, %%s)'
            % s, (fid, "Marfa", "buc", b, c))
    return fid


def _pasul2(patron, firma, tip, an, luna=None):
    """Firma -> Declarații -> tipul -> perioada -> „Continuă →” -> pasul 2 (rezultatul sau refuzul)."""
    pg = patron.pg
    patron.firma(firma["nume"])
    _card(patron, "declaratii", "#dec-tip")
    alege_tipul(pg, tip, zona=".fereastra:last-of-type ")
    alege_perioada(pg, an, luna, zona=".fereastra:last-of-type ")
    pg.click(".fereastra:last-of-type #dec-continua")
    pg.wait_for_function("() => { const f = [...document.querySelectorAll('.fereastra')].pop(); return f && (f.innerText.includes("
                         "'Pasul 2 din 3') && (!!f.querySelector('.dec-ok, .dec-avert, .dec-eroare, .caseta-eroare, #dec-trimite, "
                         "details.dec-xml'))); }", timeout=120000)
    return pg


def _xml(pg):
    loc = pg.locator(".fereastra:last-of-type details.dec-xml:has(summary:text('Vezi XML-ul generat')) pre")
    return loc.text_content() if loc.count() else ""


def _validat_duk(pg):
    return pg.inner_text(".fereastra:last-of-type .dec-ok") if pg.locator(".fereastra:last-of-type .dec-ok").count() else ""


def test_def_486_d406_septembrie_nu_e_oprit_de_partenerul_din_octombrie(patron, firma_decl):
    """486. Pașii: firma are în septembrie o vânzare către ALTEX (localitatea pe factură), iar în octombrie un client nou, persoană fizică
    fără localitate (în Clienți și pe factura lui din octombrie) -> Declarații -> D406, 09/2026 -> Continuă: XML-ul se generează și trece
    validatorul ANAF; clientul din octombrie nu apare și nu oprește luna (până la 486: „lipsește localitatea pentru … POPA ELENA”)."""
    s = firma_decl["schema"]
    _profil(patron, firma_decl)
    # date-de-pornire: partenerii facturilor de pornire, între ei persoana fizică fără localitate (starea pe care o apără 486)
    sql('INSERT INTO "%s".clienti (nume, cui, oras) VALUES (%%s, %%s, %%s), (%%s, NULL, NULL)' % s,
        ("ALTEX ROMANIA SRL", "2864518", "Voluntari", "POPA ELENA"))
    _factura(firma_decl, "E486", "1", "2026-09-10", "emisa", "RO2864518", "ALTEX ROMANIA SRL", [(100, 21)], oras="Voluntari")
    _factura(firma_decl, "E486", "2", "2026-10-05", "emisa", "", "POPA ELENA", [(50, 21)])
    pg = _pasul2(patron, firma_decl, "d406", 2026, 9)
    patron.captura("d406_septembrie")
    assert not pg.locator(".fereastra:last-of-type .dec-eroare").count(), pg.inner_text(".fereastra:last-of-type .dec-eroare")
    xml = _xml(pg)
    assert "<Name>ALTEX ROMANIA SRL</Name>" in xml   # OPANAF 1783/2021 anexa 3 pct.11: datele perioadei de raportat
    assert "POPA ELENA" not in xml and "lipsește localitatea" not in pg.inner_text(".fereastra:last-of-type")
    assert "Validat cu DUKIntegrator" in _validat_duk(pg), pg.inner_text(".fereastra:last-of-type")   # DUK D406 — judecătorul


def test_def_c48_d406_cu_avansul_pe_4092_trece_validatorul(patron, firma_decl):
    """C48 în D406. Pașii: o notă validată 4092 = 5121 (avans plătit pentru servicii) în 06/2026 -> Declarații -> D406, 06/2026 ->
    Continuă: conturile 4092 / 4093 / 4094 sunt în planul declarat, tranzacția pe 4092 e în jurnal, iar validatorul ANAF spune „fără erori”."""
    _profil(patron, firma_decl)
    _nota_validata(firma_decl, "2026-06-10", "4092", "5121", 1500, "Avans servicii consultanta")   # Registrul jurnal: notă + „Validează”
    pg = _pasul2(patron, firma_decl, "d406", 2026, 6)
    patron.captura("d406_4092")
    xml = _xml(pg)
    for cont in ("4092", "4093", "4094"):
        assert "<AccountID>%s</AccountID>" % cont in xml, cont   # d406_nomenclatoare_anaf.properties, plan_conturi_bal_soc_com
    assert "Validat cu DUKIntegrator" in _validat_duk(pg), pg.inner_text(".fereastra:last-of-type")


def test_def_485_sageata_inapoi_din_pasul_2_duce_la_alegerea_declaratiei(patron, firma_decl):
    """485. Pașii: fereastra firmei -> Declarații -> D406 -> Continuă (pasul 2) -> săgeata înapoi: se întoarce la pasul 1 al Declarațiilor
    (alegerea tipului și a perioadei), nu la fereastra firmei; a doua săgeată înapoi duce la fereastra firmei."""
    pg = _pasul2(patron, firma_decl, "d406", 2026, 9)
    patron.captura("pasul2")
    pg.click(".fereastra:last-of-type .nav-inapoi")
    pg.wait_for_function("() => { const f = [...document.querySelectorAll('.fereastra')].pop(); return f && f.innerText.includes("
                         "'Pasul 1 din 3'); }", timeout=30000)
    patron.captura("inapoi_pasul1")
    assert pg.locator(".fereastra:last-of-type #dec-tip").count() == 1 and pg.locator(".fereastra:last-of-type #fa-declaratii").count() == 0
    pg.click(".fereastra:last-of-type .nav-inapoi")
    pg.wait_for_selector(".fereastra:last-of-type #fa-declaratii", timeout=30000)


def test_def_c19_d394_sectiunile_e_f(patron, firma_decl):
    """C19. Pașii: în 06/2026 firma emite o livrare intracomunitară (DE, fără TVA), un export (US, fără TVA), o prestare taxată în România
    către un client din US, și primește un serviciu de la un furnizor din US (axa „servicii”) -> Declarații -> D394, 06/2026 -> Continuă:
    în D394 intră prestarea taxată (L) și serviciul primit (C, cu TVA-ul la beneficiar); livrarea intracomunitară și exportul sunt numite
    ca neincluse; validatorul ANAF spune „fără erori”."""
    _profil(patron, firma_decl)
    _factura(firma_decl, "E19", "1", "2026-06-10", "emisa", "DE123456789", "KUNDE GMBH", [(1000, 0)])
    _factura(firma_decl, "E19", "2", "2026-06-11", "emisa", "US123456789", "CLIENT INC", [(2000, 0)])
    _factura(firma_decl, "E19", "3", "2026-06-12", "emisa", "US123456789", "CLIENT INC", [(500, 21)])
    _factura(firma_decl, None, "FS1", "2026-06-15", "primita", "US987654321", "SUPPLIER INC", [(1000, 0)], axa="servicii")
    pg = _pasul2(patron, firma_decl, "d394", 2026, 6)
    patron.captura("d394_e_f")
    xml = _xml(pg)
    # OPANAF 2194/2025 anexa 2 lit.F pct.10 + pct.8–9: serviciul primit cu beneficiarul obligat la plată (CF art.307 alin.(2))
    assert 'tip="C" tip_partener="4" cota="21"' in xml and 'denP="SUPPLIER INC"' in xml, xml[:3000]
    assert 'tip="L" tip_partener="4" cota="21"' in xml
    assert 'tip_partener="3"' not in xml and 'tip="LS"' not in xml   # lit.E pct.10: nu se declară ce intră în D390; lit.F: nici exportul
    ecran = pg.inner_text(".fereastra:last-of-type")
    assert "fără TVA către parteneri din UE nu intră în D394" in ecran and "fără TVA către parteneri din afara UE nu intră în D394" in ecran
    assert "Validat cu DUKIntegrator" in _validat_duk(pg), ecran


def test_def_185_d394_factura_cu_doua_cote_se_numara_la_tva_ul_cel_mai_mare(patron, firma_decl):
    """185 / 131. Pașii: factura emisă în 06/2026 cu 100 lei la 21% (TVA 21) și 1.000 lei la 11% (TVA 110) -> Declarații -> D394, 06/2026:
    factura se numără o dată, pe 11% (TVA-ul cel mai mare), iar pe 21% are 0 facturi; „Rezumat” o spune; validatorul ANAF o acceptă."""
    _profil(patron, firma_decl)
    _factura(firma_decl, "E185", "1", "2026-06-10", "emisa", "RO2864518", "ALTEX ROMANIA SRL", [(100, 21), (1000, 11)])
    pg = _pasul2(patron, firma_decl, "d394", 2026, 6)
    patron.captura("d394_doua_cote")
    xml = _xml(pg)
    # OPANAF 2194/2025 anexa 2 secțiunea a 2-a pct.5: „valoarea 1 în dreptul operaţiunii cu valoarea cea mai mare a TVA”
    assert 'cota="11" cuiP="2864518" denP="ALTEX ROMANIA SRL" nrFact="1"' in xml and 'cota="21" cuiP="2864518" denP="ALTEX ROMANIA SRL" nrFact="0"' in xml, xml[:3000]
    assert "la cota cu TVA-ul cel mai mare (11%); la 21% apare cu 0 facturi" in pg.inner_text(".fereastra:last-of-type")
    assert "Validat cu DUKIntegrator" in _validat_duk(pg)


def test_def_493_d177_intra_in_coada_cu_termenul_de_depunere(patron, firma_decl):
    """493. Pașii: Declarații -> D177 (anuală), anul 2025 -> Continuă -> formularul: perioada 01.01–31.12.2025, sumele, un beneficiar
    (sponsorizare, CUI 1590082, IBAN, contract, acord „Da”) -> „+ adaugă” -> „Regenerează D177” -> „Trimite în coadă →” -> De depus: cardul
    D177 arată „termen (scadență): 25.06.2026” (CF art.42 alin.(4) -> alin.(1); până la 493: „anul 2025”)."""
    tid = firma_decl["tenant_id"]
    _profil(patron, firma_decl)
    pg = _pasul2(patron, firma_decl, "d177", 2025)
    z = ".fereastra:last-of-type "
    pg.wait_for_selector(z + "#d177-smax", timeout=60000)
    # ca un contabil: scrie suma și iese din câmp (Tab) — „change” vine la ieșire, nu trimis de test cât câmpul are focusul
    pg.fill(z + "#d177-smax", "1000"); pg.press(z + "#d177-smax", "Tab")
    pg.fill(z + "#d177-srest", "500"); pg.press(z + "#d177-srest", "Tab")
    pg.select_option(z + "#d177-tip", "1")
    pg.fill(z + "#d177-cui", "1590082")
    pg.fill(z + "#d177-den", "ASOCIATIA PROBA")
    pg.fill(z + "#d177-iban", IBAN)
    pg.fill(z + "#d177-suma", "500")
    pg.fill(z + "#d177-contract", "1/10.01.2025")
    pg.select_option(z + "#d177-acord", "true")
    pg.click(z + "#d177-add")
    pg.click(z + "#d177-regen")
    pg.wait_for_selector(z + "#dec-trimite", timeout=120000)
    pg.click(z + "#dec-trimite")
    pg.wait_for_function("() => document.body.innerText.includes('Trimisă în coad')", timeout=90000)
    cid, per = sql("SELECT id, perioada FROM public.declaratii_coada WHERE tenant_id = %s AND tip = 'd177' ORDER BY id DESC LIMIT 1", (tid,))[0]
    assert per == "25.06.2026", per   # CF art.42 alin.(4): „până la termenele de depunere a declarației anuale de impozit pe profit”
    patron.acasa()
    pg.click("button.cab-card:has([data-cheie='validat'])")
    card = ".val-card[data-coada-ids='%d']" % cid
    pg.wait_for_selector(card, timeout=30000)
    patron.captura("de_depus_termen")
    assert "termen (scadență): 25.06.2026" in pg.inner_text(card), pg.inner_text(card)


def test_def_c119_d100_micro_baza_fara_tva_ul_din_raportul_z(patron, firma_decl):
    """C119 (găsită de pachetul `pilot`). Pașii: microîntreprindere cu un Raport Z validat în 08/2026 — nota lui: 5311 = 707 5.826,00 și
    707 = 4427 126,00 (forma scrisă de aplicație la „Raport Z”) -> Declarații -> D100, T3/2026 -> Continuă: „Rezumat” arată contul 707 cu
    5.700,00 lei și „Baza impozabilă: 5.700,00 lei × cota 1% = cod 121: 57 lei” (până la C119: 5.826 -> 58), iar validatorul ANAF o acceptă.
    Temei: CF art.53 alin.(1) — baza = veniturile; CF art.51 alin.(1) — 1%."""
    s = firma_decl["schema"]
    _profil(patron, firma_decl, regim="micro")
    # date-de-pornire: Z-ul din 31.08.2026 cu 5.826,00 brut și numai 126,00 TVA — formularul „Raport Z” (cote 11% / 21%) nu dă perechea asta
    nid = sql('INSERT INTO "%s".inregistrari (data, descriere, document_ref, status, sursa) VALUES (%%s, %%s, %%s, %%s, %%s) RETURNING id' % s,
              ("2026-08-31", "Raport Z 1", "Raport Z 1", "ciorna", "raport_z"))[0][0]
    # date-de-pornire: rândurile aceluiași Z (5311 = 707 brutul, 707 = 4427 TVA-ul), în forma pe care o scrie „Raport Z”
    sql('INSERT INTO "%s".inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%%s, %%s, %%s, %%s), (%%s, %%s, %%s, %%s)' % s,
        (nid, "5311", "707", 5826, nid, "707", "4427", 126))
    # date-de-pornire: validarea aceluiași Z (ciornă -> rânduri -> validată), ca după „Validează raportul Z”
    sql('UPDATE "%s".inregistrari SET status = \'validata\' WHERE id = %%s' % s, (nid,))   # ciornă -> rânduri -> validată (regula_linii_nota)
    pg = _pasul2(patron, firma_decl, "d100", 2026, 9)
    patron.captura("d100_micro_z")
    t = " ".join(pg.inner_text(".fereastra:last-of-type").split())
    assert "cont 707: 5.700,00 lei" in t and "Baza impozabilă: 5.700,00 lei × cota 1% = cod 121: 57 lei" in t, t[:3000]   # CF art.53 alin.(1)
    assert "Validat cu DUKIntegrator" in _validat_duk(pg), t[:3000]
