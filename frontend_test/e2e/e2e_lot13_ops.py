# -*- coding: utf-8 -*-
"""Lotul 13 (comanda Costin 13.1), pachetul `ops`: testele de capăt la capăt ale operațiunilor speciale, mijloacelor fixe și regimurilor de TVA.

Fiecare test reface pașii contabilului pe ecran (Operațiuni speciale / Mijloace fixe), verifică ce scrie ecranul ȘI cifrele din bază și lasă
capturi. Pașii rulează pe aplicația din index, pe baza de TEST, pe firme NOI (`firma_noua`, scoase la final), pregătite pe drumul ecranelor
(`pregateste_firma`). Datele de PORNIRE care nu sunt ale pasului probat se scriu direct (declarat, la fiecare test): o notă validată (avansul,
creditul, soldul de pornire), mijlocul fix din registru, factura în valută contată. ANAF și VIES sunt ale plasei (`ICONTA_ANAF_SIMULAT`):
ANAF răspunde „negăsit” la orice CUI fără răspuns pregătit; VIES din `vies.json`.

Mutațiile care fac fiecare test ROȘU: `mut_lot13_ops.json`."""
import json
import os

import pytest

from conftest import firma_noua, sql, zile_de_acum
from e2e_bloc_a import AZI, _api, _ok, pregateste_firma

D = AZI.isoformat()
_F = ".fereastra:last-of-type "


def _cnp(baza12):
    """CNP de test cu cifra de control verificată (algoritmul oficial, CLAUDE.md)."""
    ch = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]
    s = sum(int(baza12[i]) * ch[i] for i in range(12)) % 11
    return baza12 + str(1 if s == 10 else s)


@pytest.fixture()
def firma_ops(patron):
    for f in firma_noua():
        pregateste_firma(patron, f, regim_fiscal="profit")
        yield f


def _op(patron, f, cheie):
    patron.firma(f["nume"])
    pg = patron.pg
    pg.click("#fa-operatiuni")
    pg.wait_for_selector("button[data-op='%s']" % cheie, timeout=25000)
    pg.click("button[data-op='%s']" % cheie)
    pg.wait_for_selector("#op-trimite", timeout=20000)
    return pg


def _completeaza(pg, campuri):
    """[(câmp, valoare)] în ordine: selecturile se aleg (după ce opțiunea apare — listele încărcate de la server), restul se scriu."""
    for c, v in campuri:
        sel = "#op-%s" % c
        if pg.eval_on_selector(sel, "e => e.tagName") == "SELECT":
            pg.wait_for_function("([s, v]) => [...document.querySelector(s).options].some((o) => o.value === String(v))", arg=[sel, str(v)],
                                 timeout=20000)
            pg.select_option(sel, str(v))
        else:
            pg.fill(sel, str(v))
        pg.dispatch_event(sel, "change")


def _genereaza(pg):
    pg.click("#op-trimite")
    pg.wait_for_selector("#op-mesaj [data-dupa-generare], #op-mesaj.msg-eroare", timeout=40000)
    return " ".join(pg.inner_text("#op-mesaj").split())


def _ultima(f):
    return sql('SELECT coalesce(max(id), 0) FROM "%s".inregistrari' % f["schema"])[0][0]


def _note_noi(f, ultima):
    return [r[0] for r in sql('SELECT id FROM "%s".inregistrari WHERE id > %%s ORDER BY id' % f["schema"], (ultima,))]


def _linii(f, nid):
    return [tuple(r) for r in sql('SELECT cont_debit, cont_credit, suma::text, partener_nume FROM "%s".inregistrari_linii '
                                  'WHERE inregistrare_id = %%s ORDER BY id' % f["schema"], (nid,))]


def _nota_validata(f, data, linii, partener=(None, None), descriere="Date de pornire E2E lot 13", mijloc_fix_id=None, factura_id=None):
    """DATE DE PORNIRE (declarat): o notă VALIDATĂ cu rândurile [(debit, credit, suma)] — soldul pe care îl stinge pasul probat."""
    s = f["schema"]
    # ciornă -> rânduri (cu activul lor, `mf_linii`) -> validată: rândurile unei note validate nu se mai scriu (`trg_regula_linii_nota`)
    # date-de-pornire: nota validată a pasului anterior (soldul pe care îl stinge pasul probat), declarată în docstringul helperului
    (nid,) = sql('INSERT INTO "%s".inregistrari (data, descriere, sursa, status, document_ref) VALUES (%%s, %%s, %%s, %%s, %%s) RETURNING id' % s,
                 (data, descriere, "facturi" if factura_id else "operatiuni", "ciorna", "Document E2E"))[0]
    if factura_id:
        # date-de-pornire: contarea facturii de pornire, legată de ea înainte de validare (nota validată nu se mai modifică)
        sql('UPDATE "%s".inregistrari SET factura_id = %%s WHERE id = %%s' % s, (factura_id, nid))
    for d, c, x in linii:
        # date-de-pornire: rândurile aceleiași note de pornire, scrise în ciornă (rândurile notei validate nu se mai scriu)
        (lid,) = sql('INSERT INTO "%s".inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma, partener_cui, partener_nume) '
                     'VALUES (%%s, %%s, %%s, %%s, %%s, %%s) RETURNING id' % s, (nid, d, c, x, partener[0], partener[1]))[0]
        if mijloc_fix_id:
            # date-de-pornire: activul rândului de pornire (`mf_linii`), cum îl scrie aplicația la amortizare
            sql('INSERT INTO "%s".mf_linii (linie_id, mijloc_fix_id) VALUES (%%s, %%s)' % s, (lid, mijloc_fix_id))
    # date-de-pornire: validarea notei de pornire, ca după „Validează” din Registrul jurnal
    sql('UPDATE "%s".inregistrari SET status = \'validata\' WHERE id = %%s' % s, (nid,))
    return nid


def _valideaza(patron, f, nid):
    return _ok(_api(patron, "POST", "/tenants/%d/jurnal/%d/valideaza" % (f["tenant_id"], nid)), "validarea notei")


def _salariat(patron, f, nume="Ionescu", prenume="Vasile", baza12="185010140001", salariu=6000):
    r = _ok(_api(patron, "POST", "/tenants/%d/salariati" % f["tenant_id"],
                 {"nume": nume, "prenume": prenume, "cnp": _cnp(baza12), "data_angajare": "2026-01-05", "tip_norma": "intreaga",
                  "ore_zi": 8, "salariu_brut": salariu, "persoane_intretinere": 0, "scutit_contrib_minim": False,
                  "functie_baza": True, "cor": "331302"}), "salariatul")
    return r.get("id") or r.get("salariat_id"), _cnp(baza12)


def _mf(f, cod, valoare, luni, pif, cont="2131", cont_am="2813"):
    """DATE DE PORNIRE: mijlocul fix în registru, pe scrierea din care îl adaugă aplicația (`repo_mijloace_fixe.adauga_cu_reevaluare`)."""
    from decimal import Decimal
    from core import db, repo_mijloace_fixe
    with db.get_conn(f["schema"]) as c:
        with c.cursor() as cur:
            r = repo_mijloace_fixe.adauga_cu_reevaluare(cur, f["schema"], cod, "Utilaj lot13 %s" % cod, cont, cont_am,
                                                        Decimal(valoare), Decimal(0), luni, pif, "liniara")
        c.commit()
    return r[0]


def _registru(patron, f):
    patron.firma(f["nume"])
    patron.pg.click("#fa-mijloace")
    patron.pg.wait_for_selector(_F + "table.fd-tabel tbody tr", timeout=30000)


def _rand_mf(pg, cod):
    return pg.locator(_F + "table.fd-tabel tbody tr", has_text="Utilaj lot13 %s" % cod).first


# ── 670 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_670_decontul_pe_salariat_cu_plafonul_diurnei_si_cota_fiecarei_cheltuieli(patron, firma_ops):
    """670. Proba lui Costin: decont final, Casa, avans 1.000, diurnă 300, transport 200, cazare 400 — înainte, cu o singură cotă 21:
    625 = 542 900; 4426 = 542 126; 542 = 5311 26, fără salariat, fără zile, cu cota precompletată. Pașii: salariatul Ionescu Vasile (salariu
    6.000) cu avansul 542 = 5311 1.000 validat -> Operațiuni speciale -> „Decont deplasare / diurnă” -> Decont final, salariatul din listă,
    Casa, avansul 1.000, diurna 300 în țară 3 zile, transport 200 la 21%, cazare 400 la 11% -> „Generează nota”: 625 = 542 900, 4426 = 542 86
    (42 + 44), 5311 = 542 14, toate pe salariat; caseta spune diurna neimpozabilă 172,50 (2,5 × 23 lei × 3 zile, CF art.76 alin.(2) lit.k)
    și partea peste plafon (127,50) care intră în statul de plată al lunii. Formularul pornește fără nicio cotă scrisă, iar transportul și
    cazarea nu sunt obligatorii.
    MUTAȚIA: `deconturi.nota_decont` ia cota transportului și pentru cazare -> 4426 = 542 84 -> ROȘU."""
    f = firma_ops
    sid, cnp = _salariat(patron, f)
    _nota_validata(f, AZI.replace(day=1).isoformat(), [("542", "5311", 1000)], (cnp, "Ionescu Vasile"))
    pg = _op(patron, f, "decont")
    _completeaza(pg, [("data", D), ("fel", "decont")])
    for c in ("cota_transport", "cota_cazare"):
        assert pg.input_value("#op-%s" % c) == "" and (pg.get_attribute("#op-%s" % c, "placeholder") or "") == "", c   # 670 d / 504
    assert "*" not in pg.inner_text(".camp:has(#op-transport) .camp-eticheta")   # transportul nu e obligatoriu
    _completeaza(pg, [("salariat_id", sid), ("sursa", "casa"), ("avans", "1000"), ("diurna", "300"), ("deplasare", "interna"),
                      ("zile", "3"), ("transport", "200"), ("cota_transport", "21"), ("cazare", "400"), ("cota_cazare", "11")])
    patron.captura("formular")
    ultima = _ultima(f)
    m = _genereaza(pg)
    patron.captura("confirmarea")
    assert "msg-eroare" not in (pg.get_attribute("#op-mesaj", "class") or ""), m
    (nid,) = _note_noi(f, ultima)
    assert _linii(f, nid) == [("625", "542", "900.00", "Ionescu Vasile"), ("4426", "542", "86.00", "Ionescu Vasile"),
                              ("5311", "542", "14.00", "Ionescu Vasile")]
    assert "diurnă neimpozabilă 172,50 lei" in m and "peste plafon 127,50 lei" in m, m
    assert pg.locator("#op-mesaj [data-dupa-generare]").count() == 1 and pg.locator("#op-mesaj [data-dupa-generare] #op-deschide-nota").count() == 1


# ── 524 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_524_plata_ratei_cu_creditul_numai_in_ciorna_se_refuza(patron, firma_ops):
    """524. Proba lui Costin: „cu creditul și dobânda doar ciorne (1621 și 1682 zero) a generat 1621 = 5121 5.000 și 1682 = 5121 500”.
    Pașii: primirea creditului 5121 = 1621 5.000 în CIORNĂ -> Credite bancare -> Plată rată, peste 1 an, rata 5.000 -> „Generează nota”:
    refuzul spune soldul creditor 0,00 al lui 1621 și numește ciorna care l-ar crea („valideaz-o întâi”); nicio notă. După validarea primirii,
    aceeași plată se generează (1621 = 5121 5.000), iar întrebarea „Dobânda a fost înregistrată deja pe 666” nu mai există.
    MUTAȚIA: `ops_sold.cere_sold` nu mai refuză -> nota cu sold invers se scrie -> ROȘU."""
    f = firma_ops
    s = f["schema"]
    # date-de-pornire: creditul primit numai în ciornă — starea pe care o refuză plata ratei (524)
    (nid0,) = sql('INSERT INTO "%s".inregistrari (data, descriere, sursa, status, document_ref) VALUES (%%s, %%s, %%s, %%s, %%s) RETURNING id' % s,
                  (AZI.replace(day=1).isoformat(), "Primire credit E2E 524", "operatiuni", "ciorna", "Contract credit E2E"))[0]
    # date-de-pornire: rândul aceleiași ciorne a creditului
    sql('INSERT INTO "%s".inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%%s, %%s, %%s, %%s)' % s,
        (nid0, "5121", "1621", 5000))
    pg = _op(patron, f, "credit")
    assert pg.locator("#op-dobanda_angajata").count() == 0
    _completeaza(pg, [("data", D), ("operatie", "plata"), ("tip", "lung"), ("rata", "5000"), ("dobanda", "0"), ("comision", "0")])
    ultima = _ultima(f)
    m = _genereaza(pg)
    patron.captura("refuz")
    assert "contul 1621" in m and "sold creditor 0,00 lei" in m and "valideaz-o întâi" in m, m
    assert _note_noi(f, ultima) == []
    _valideaza(patron, f, nid0)
    pg = _op(patron, f, "credit")
    _completeaza(pg, [("data", D), ("operatie", "plata"), ("tip", "lung"), ("rata", "5000"), ("dobanda", "0"), ("comision", "0")])
    _genereaza(pg)
    patron.captura("dupa_validare")
    (nid,) = _note_noi(f, ultima)
    assert _linii(f, nid) == [("1621", "5121", "5000.00", None)]


def test_def_524_decontarea_in_valuta_pe_factura_de_origine(patron, firma_ops):
    """524. Proba lui Costin (F3): „încasarea a 5.000 EUR (5124 = 4111 24.750, 5124 = 765 1.935) se generează fără creanță în valută”.
    Pașii: fără nicio factură în valută deschisă, lista facturilor e goală -> DATE DE PORNIRE: factura emisă F13V nr. 1 de 5.000 EUR la
    cursul 4,95, contată prin notă validată (4111 = 704 24.750) -> Decontare în valută -> Încasare creanță: factura se alege din listă (rămas
    5.000 EUR, cursul de evidență 4,95 „cursul facturii”), suma 6.000 se refuză (peste soldul rămas), 2.000 EUR se decontează la cursul BNR al
    zilei: 5124 = 4111 9.900 (cursul de evidență, cu clientul pe rând) + diferența de curs.
    MUTAȚIA: `ops_valuta.facturi_deschise` nu scade decontările -> după prima decontare lista arată tot 5.000 -> ROȘU."""
    f = firma_ops
    s = f["schema"]
    pg = _op(patron, f, "decont_valuta")
    _completeaza(pg, [("data", D), ("tip", "creanta")])
    pg.wait_for_function("() => (document.querySelector('#op-factura_id') || {innerText: ''}).innerText.includes('Nicio factură emisă')", timeout=20000)
    patron.captura("fara_factura")
    # date-de-pornire: factura emisă în EUR din care provine creanța în valută (524) — emiterea în valută nu e pasul probat
    (fid,) = sql('INSERT INTO "%s".facturi (serie, numar, data_emitere, directie, moneda, total, total_lei, curs_bnr, tert_nume, tert_cui, '
                 'tert_tara) VALUES (%%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s) RETURNING id' % s,
                 ("F13V", "1", AZI.replace(day=1).isoformat(), "emisa", "EUR", 5000, 24750, 4.95, "Client IE E2E", "IE6388047V", "IE"))[0]
    _nota_validata(f, AZI.replace(day=1).isoformat(), [("4111", "704", 24750)], factura_id=fid)
    pg = _op(patron, f, "decont_valuta")
    _completeaza(pg, [("data", D), ("tip", "creanta")])
    pg.wait_for_function("(id) => [...document.querySelectorAll('#op-factura_id option')].some((o) => o.value === String(id))", arg=fid, timeout=20000)
    eticheta = pg.eval_on_selector("#op-factura_id", "(s, id) => [...s.options].find((o) => o.value === String(id)).textContent", fid)
    assert "rămas 5.000,00 EUR" in eticheta and "curs de evidență 4,95" in eticheta, eticheta
    _completeaza(pg, [("factura_id", fid), ("valoare_valuta", "6000"), ("cont_banca", "5124")])
    m = _genereaza(pg)
    assert "depășește soldul rămas" in m, m
    ultima = _ultima(f)
    _completeaza(pg, [("valoare_valuta", "2000")])
    m = _genereaza(pg)
    patron.captura("decontarea")
    (nid,) = _note_noi(f, ultima)
    linii = _linii(f, nid)
    assert linii[0] == ("5124", "4111", "9900.00", "Client IE E2E"), linii
    pg = _op(patron, f, "decont_valuta")
    _completeaza(pg, [("data", D), ("tip", "creanta")])
    pg.wait_for_function("(id) => [...document.querySelectorAll('#op-factura_id option')].some((o) => o.value === String(id))", arg=fid, timeout=20000)
    eticheta = pg.eval_on_selector("#op-factura_id", "(s, id) => [...s.options].find((o) => o.value === String(id)).textContent", fid)
    assert "rămas 3.000,00 EUR" in eticheta, eticheta   # soldul facturii scade cu decontarea legată de ea (ciorna se vede după validare)


# ── 518 / 519 / 522 / 517 ──────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_518_519_522_casarea_pe_activ_in_fereastra_ei(patron, firma_ops):
    """518 / 519 / 522. Pașii: MF-A (6.000 lei, 60 de luni, PIF 10.01.2026, rata 100) și MF-B (3.600 lei, PIF în luna curentă) pe același
    cont 2813; amortizarea lui MF-A pe 02/2026 validată pe activ (100) -> Mijloace fixe: „Înregistrat pe activ” 100 la MF-A și 0 la MF-B (522:
    înainte, contul întreg stătea la activul rămas singur) -> „Casează” MF-A -> fereastra casării: data -> „Generează nota de casare”: refuzul
    numește lunile lipsă și suma lor (518: înainte nota debita 2813 cu toată amortizarea calculată) -> DATE DE PORNIRE: lunile 03…luna trecută
    înregistrate pe activ -> casarea: luna casării pe 6811, 2813 = 2131 cu toată amortizarea, restul pe 6583, documentul „Proces-verbal de
    casare”; registrul arată „casarea e în ciornă” (519: nu „casat”) -> ciorna ștearsă din Registrul jurnal -> MF-A e iar „activ”.
    MUTAȚIA: triggerul / registrul: `mf_registru.registru` ia starea din `activ`, fără nota în așteptare -> „activ” în loc de „casarea e în
    ciornă” -> ROȘU."""
    f = firma_ops
    s = f["schema"]
    ma = _mf(f, "MFA", "6000", 60, "2026-01-10")
    _mf(f, "MFB", "3600", 36, AZI.replace(day=1).isoformat())
    _nota_validata(f, "2026-02-28", [("6811", "2813", 100)], mijloc_fix_id=ma)
    _registru(patron, f)
    pg = patron.pg
    assert "100,00" in _rand_mf(pg, "MFA").inner_text() and "0,00" in _rand_mf(pg, "MFB").locator("td").nth(6).inner_text()
    patron.captura("inregistrat_pe_activ")
    _rand_mf(pg, "MFA").locator("[data-caseaza]").click()
    pg.wait_for_selector(_F + "#mf-f-data", timeout=20000)
    pg.fill(_F + "#mf-f-data", D)
    pg.click(_F + "#mf-f-genereaza")
    pg.wait_for_selector(_F + "#mf-f-mesaj.msg-eroare, " + _F + "#mf-f-mesaj .msg-eroare", timeout=30000)
    m = " ".join(pg.inner_text(_F + "#mf-f-mesaj").split())
    patron.captura("refuz_luni_lipsa")
    assert "lipsesc" in m and "6811" in m and "Înregistrează lunile lipsă" in m, m
    for luna in range(3, AZI.month):
        _nota_validata(f, "2026-%02d-28" % luna, [("6811", "2813", 100)], mijloc_fix_id=ma)
    ultima = _ultima(f)
    pg.click(_F + "#mf-f-genereaza")
    pg.wait_for_selector(_F + "#mf-f-mesaj .caseta-ok", timeout=30000)
    patron.captura("nota_casarii")
    (nid,) = _note_noi(f, ultima)
    linii = [x[:3] for x in _linii(f, nid)]
    assert linii[0] == ("6811", "2813", "100.00") and sum(float(x[2]) for x in linii if x[1] == "2131") == 6000, linii
    assert sql('SELECT document_ref FROM "%s".inregistrari WHERE id = %%s' % s, (nid,))[0][0].startswith("Proces-verbal de casare nr ")
    _registru(patron, f)
    assert "casarea e în ciorna" in _rand_mf(pg, "MFA").locator(".mf-stare").inner_text()
    patron.captura("casare_in_asteptare")
    _ok(_api(patron, "DELETE", "/tenants/%d/jurnal/%d" % (f["tenant_id"], nid)), "ștergerea ciornei")
    _registru(patron, f)
    assert _rand_mf(pg, "MFA").locator(".mf-stare").inner_text().strip() == "activ"
    patron.captura("dupa_stergere")


def test_def_517_lunile_lipsa_din_randul_activului(patron, firma_ops):
    """517. „Registrul arată lunile neînregistrate, dar nu oferă acțiunea de a le înregistra.” Pașii: MF-L (1.200 lei, 12 luni, PIF
    10.01.2026) fără nicio amortizare înregistrată -> Mijloace fixe: rândul are „Înregistrează lunile lipsă (N)” -> apăsat: caseta verde cu
    câte o notă pe lună (ciorne 6811 = 2813 100, pe activ); registrul arată lunile „în ciornă, de validat”.
    MUTAȚIA: butonul nu mai cheamă generarea (`data-lipsa` fără handler) -> nicio notă -> ROȘU."""
    f = firma_ops
    ml = _mf(f, "MFL", "1200", 12, "2026-01-10")
    _registru(patron, f)
    pg = patron.pg
    b = _rand_mf(pg, "MFL").locator("[data-lipsa]")
    assert b.is_enabled() and "Înregistrează lunile lipsă (" in b.inner_text()
    ultima = _ultima(f)
    b.click()
    pg.wait_for_selector(_F + "#mf-mesaj .caseta-ok", timeout=60000)
    patron.captura("generate")
    noi = _note_noi(f, ultima)
    # 02 … luna trecută, o notă pe lună — luna în care aplicația generează ACUM (rularea poate trece de miezul nopții)
    assert len(noi) in {z.month - 2 for z in zile_de_acum(AZI)}, noi
    assert all(sql('SELECT count(*) FROM "%s".inregistrari_linii l JOIN "%s".mf_linii ml ON ml.linie_id = l.id WHERE l.inregistrare_id = %%s '
                   'AND ml.mijloc_fix_id = %%s AND l.cont_debit = %%s' % (f["schema"], f["schema"]), (n, ml, "6811"))[0][0] == 1 for n in noi)
    assert "în ciornă, de validat" in _rand_mf(pg, "MFL").inner_text()


# ── 521 / 519 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_521_519_plusul_de_mijloc_fix_cu_catalog_intra_in_registru_la_validare(patron, firma_ops):
    """521 / 519 / 504. Pașii: Inventariere anuală -> Plus mijloc fix: conturile pornesc goale, „Cont amortizare” nu se mai cere (îl dă
    contul activului), codul din catalog arată plaja (2.2.9: 2–4 ani, HG 2139/2004) -> durata 12 luni se refuză lângă câmp -> 36 de luni: nota 2131 = 4754
    6.000; numărul de inventar e MF-001 (nu „MF-PLUS”); registrul arată activul „intră la validarea notei” -> nota validată -> „activ”.
    MUTAȚIA: `_verifica_catalog` nu mai refuză durata din afara plajei -> nota cu 12 luni se scrie -> ROȘU."""
    f = firma_ops
    pg = _op(patron, f, "inventariere")
    _completeaza(pg, [("data", D), ("operatie", "plus_mf")])
    assert pg.input_value("#op-cont_imobilizare") == "" and pg.locator("#op-cont_amortizare").count() == 0
    _completeaza(pg, [("valoare", "6000"), ("denumire", "Laptop găsit la inventar"), ("cont_imobilizare", "2131"), ("cod_catalog", "2.2.9")])
    pg.wait_for_function("() => (document.querySelector('#op-cod_catalog-stare') || {innerText: ''}).innerText.includes('între 24 și 48')", timeout=20000)
    _completeaza(pg, [("dnf_luni", "12"), ("data_pif", D), ("metoda", "liniara"), ("destinatie_cd", "false")])
    ultima = _ultima(f)
    _genereaza(pg)
    pg.wait_for_selector('.msg-eroare[data-camp="op-dnf_luni"]', timeout=20000)
    patron.captura("durata_refuzata")
    assert _note_noi(f, ultima) == []
    _completeaza(pg, [("dnf_luni", "36")])
    m = _genereaza(pg)
    patron.captura("nota_plus")
    (nid,) = _note_noi(f, ultima)
    assert [x[:3] for x in _linii(f, nid)] == [("2131", "4754", "6000.00")]
    assert "Numărul de inventar: MF-001" in m, m
    _registru(patron, f)
    rand = pg.locator(_F + "table.fd-tabel tbody tr", has_text="Laptop găsit la inventar").first
    assert "intră la validarea notei" in rand.locator(".mf-stare").inner_text()
    _valideaza(patron, f, nid)
    _registru(patron, f)
    rand = pg.locator(_F + "table.fd-tabel tbody tr", has_text="Laptop găsit la inventar").first
    assert rand.locator(".mf-stare").inner_text().strip() == "activ"
    patron.captura("activ_dupa_validare")


# ── 523 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_523_bunul_primit_in_leasing_intra_in_registru(patron, firma_ops):
    """523 / 507 / 506. Pașii: Leasing -> Primire bun (financiar): locatorul (CUI + denumirea), bunul „Autoturism leasing”, capital 60.000,
    dobânda totală 9.000, cont 2133, cod 2.3.2.1.1, 60 de luni, PIF, liniar -> nota 2133 = 167 60.000 cu locatorul pe 167; dobânda pe 8051
    în afara bilanțului (o singură parte, fără 891, nu în rândurile notei); bunul în registrul mijloacelor fixe (activ la validarea notei).
    MUTAȚIA: primirea nu mai înscrie activul (`mf_reg = None`) -> registrul n-are bunul -> ROȘU."""
    f = firma_ops
    s = f["schema"]
    pg = _op(patron, f, "leasing")
    _completeaza(pg, [("data", D), ("tip", "primire"), ("locator_cui", "18765430"), ("locator_nume", "Leasing Proba IFN SA"),
                      ("denumire", "Autoturism leasing"), ("valoare_capital", "60000"), ("dobanda_totala", "9000"),
                      ("cont_imobilizare", "2133"), ("cod_catalog", "2.3.2.1.1"), ("dnf_luni", "60"), ("data_pif", D), ("metoda", "liniara")])
    ultima = _ultima(f)
    m = _genereaza(pg)
    patron.captura("primirea")
    (nid,) = _note_noi(f, ultima)
    assert _linii(f, nid) == [("2133", "167", "60000.00", "Leasing Proba IFN SA")], _linii(f, nid)   # 506: locatorul pe 167
    assert "8051 debit 9.000,00 lei (în afara bilanțului)" in m, m
    assert sql('SELECT cont, sens, suma::text FROM "%s".evidenta_extrabilant WHERE inregistrare_id = %%s' % s, (nid,)) == [("8051", "D", "9000.00")]
    assert sql('SELECT count(*) FROM "%s".inregistrari_linii WHERE cont_credit = %%s OR cont_debit = %%s' % s, ("891", "891"))[0][0] == 0
    assert sql('SELECT cod_catalog, dnf_luni FROM "%s".mijloace_fixe WHERE denumire = %%s' % s, ("Autoturism leasing",)) == [("2.3.2.1.1", 60)]


# ── 530 / 531 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_530_refacturarea_utilitatilor_fara_461(patron, firma_ops):
    """530. Proba lui Costin: total 1.000, refacturat 400, cota 21 -> înainte 605 = 401 600, 4426 = 401 126, 461 = 401 484 și 4111 = 708 400,
    4111 = 4427 84 (chiriașul datora de două ori, 84 lei TVA plătită în plus). Pașii: Chirii / comodat / refacturări -> Refacturare
    utilități: furnizorul și chiriașul (CUI + denumire), factura UT-1, total 1.000, partea 400, cota 21 -> două note: factura furnizorului
    întreagă 605 = 401 1.000, 4426 = 401 210 (cu furnizorul) și factura emisă chiriașului 4111 = 708 400, 4111 = 4427 84; fără 461.
    MUTAȚIA: `comodat_chirii.nota_refacturare` trece partea chiriașului pe 461 -> ROȘU."""
    f = firma_ops
    pg = _op(patron, f, "chirie")
    _completeaza(pg, [("data", D), ("fel", "refacturare"), ("furnizor_cui", "31654471"), ("furnizor_nume", "Utilitati Proba SA"),
                      ("client_cui", "18765430"), ("client_nume", "Chirias Proba SRL"), ("numar", "UT-1"), ("total_factura", "1000"),
                      ("parte_refacturata", "400"), ("cota", "21")])
    ultima = _ultima(f)
    m = _genereaza(pg)
    patron.captura("refacturarea")
    noi = _note_noi(f, ultima)
    assert len(noi) == 2, (noi, m)
    assert [x[:3] for x in _linii(f, noi[0])] == [("605", "401", "1000.00"), ("4426", "401", "210.00")]
    assert sorted(x[:3] for x in _linii(f, noi[1])) == [("4111", "4427", "84.00"), ("4111", "708", "400.00")]
    assert sql('SELECT count(*) FROM "%s".inregistrari_linii WHERE cont_debit = %%s' % f["schema"], ("461",))[0][0] == 0


def test_def_531_chiria_unui_imobil_fara_optiune_e_scutita(patron, firma_ops):
    """531. Pașii: Chirie încasată: chiriașul, chiria 2.000, bun imobil, opțiune de taxare: Nu -> factura emisă cu linia 0%, categoria
    „Scutit fără drept de deducere (art.292)” (D300 rd.15), nota 4111 = 706 2.000; caseta spune regimul (art. 292 alin. (2) lit. e)).
    MUTAȚIA: `nota_chirie` taxează chiria imobilului fără opțiune -> cota cerută -> refuz / 4427 -> ROȘU."""
    f = firma_ops
    pg = _op(patron, f, "chirie")
    _completeaza(pg, [("data", D), ("fel", "chirie_incasata"), ("client_cui", "18765430"), ("client_nume", "Chirias Proba SRL"),
                      ("chirie", "2000"), ("tip_bun", "imobil"), ("optiune_taxare", "false")])
    ultima = _ultima(f)
    m = _genereaza(pg)
    patron.captura("chiria_scutita")
    (nid,) = _note_noi(f, ultima)
    assert [x[:3] for x in _linii(f, nid)] == [("4111", "706", "2000.00")]
    assert "scutită fără drept de deducere" in m, m
    fid = sql('SELECT factura_id FROM "%s".inregistrari WHERE id = %%s' % f["schema"], (nid,))[0][0]
    assert sql('SELECT cota_tva::text, categorie_tva FROM "%s".factura_linii WHERE factura_id = %%s' % f["schema"], (fid,)) == [
        ("0.00", "scutit_fara_drept")]


# ── 544 / 550 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_544_taxarea_inversa_cere_furnizorul_platitor_la_anaf(patron, firma_ops):
    """544. „Cu «Furnizor plătitor TVA: Nu» s-a aplicat taxarea inversă […] calitatea de plătitor se verifică la ANAF din CUI, nu se
    întreabă de mână.” Pașii: Taxare inversă internă: formularul nu mai are „Furnizor plătitor TVA” -> CUI-ul 31654471 (ANAF-ul plasei nu-l
    găsește) -> „Generează nota”: refuzul lângă CUI („nu e găsit la ANAF: taxarea inversă cere un furnizor înregistrat în scopuri de TVA”),
    nicio notă, nicio factură.
    MUTAȚIA: `_platitor_tva_strict` întoarce „plătitor” fără ANAF -> nota se scrie -> ROȘU."""
    f = firma_ops
    pg = _op(patron, f, "taxare_inversa")
    assert pg.locator("#op-furnizor_platitor_tva").count() == 0
    _completeaza(pg, [("data", D), ("furnizor_cui", "31654471"), ("furnizor_nume", "Deseuri Proba SRL"), ("numar", "TI-1"),
                      ("categorie", "deseuri"), ("valoare", "30000"), ("cont_destinatie", "371"), ("cota", "21")])
    ultima = _ultima(f)
    m = _genereaza(pg)
    patron.captura("refuz_anaf")
    assert "nu e găsit la ANAF" in m, m
    assert _note_noi(f, ultima) == []


def test_def_550_vies_indisponibil_nu_e_cod_invalid(patron, firma_ops):
    """550. Proba lui Costin: pentru IE6388047V aplicația a spus „codul … e invalid în VIES — facturează cu TVA românesc”, deși VIES răspundea
    „Serviciu indisponibil în statul membru”. Pașii: VIES (al plasei) răspunde MS_UNAVAILABLE -> Livrare/prestare intracomunitară ->
    Servicii, codul IE6388047V: sub câmp „VIES n-a putut verifica acum codul: serviciul statului membru e indisponibil … Nu înseamnă că
    codul e invalid” (nu „Cod TVA invalid”) -> „Generează nota”: refuzul spune la fel (reîncercare), nicio notă.
    MUTAȚIA: `intracomunitar.stare_vies` socotește orice eroare „invalid” -> „Cod TVA invalid în VIES” -> ROȘU."""
    d = os.environ.get("ICONTA_ANAF_SIMULAT")
    if d:
        os.makedirs(d, exist_ok=True)
        cale = os.path.join(d, "vies.json")
        vies = json.load(open(cale, encoding="utf-8")) if os.path.exists(cale) else {}
        vies["IE6388047V"] = {"valid": False, "nume": "", "adresa": "", "eroare": "MS_UNAVAILABLE"}
        with open(cale, "w", encoding="utf-8") as fo:
            json.dump(vies, fo, ensure_ascii=False)
    f = firma_ops
    pg = _op(patron, f, "vanzare_ic")
    _completeaza(pg, [("data", D), ("tip", "servicii"), ("valoare", "1000"), ("cod_tva_client", "IE6388047V"), ("cont_venit", "704")])
    pg.wait_for_function("() => (document.querySelector('#op-cod_tva_client-vies') || {innerText: ''}).innerText.includes('VIES n-a putut verifica')",
                         timeout=30000)
    t = pg.inner_text("#op-cod_tva_client-vies")
    patron.captura("vies_indisponibil")
    assert "Nu înseamnă că codul e invalid" in t and "invalid în VIES" not in t, t
    ultima = _ultima(f)
    m = _genereaza(pg)
    assert "serviciul statului membru (IE) e indisponibil" in m and _note_noi(f, ultima) == [], m


# ── 504 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_504_niciun_camp_precompletat_sau_cu_text_gri(patron, firma_ops):
    """504. „Câmpurile nu au voie să arate valori gri sau precompletate care induc în eroare (ex.: Cota TVA arată «21» gri […]; la Ajustare
    stocuri contul vine precompletat cu 397). Câmpul rămâne gol.” Pașii: fiecare formular din Operațiuni speciale, cu ramura fiecărui
    câmp aleasă: niciun câmp text / număr nu are valoare sau text gri (placeholder); contul de ajustare a stocurilor e o listă 391–398 fără
    nimic ales.
    MUTAȚIA: motorul pune iar sugestia ca text gri (`placeholder`) pe câmpurile numerice -> ROȘU."""
    f = firma_ops
    pg = _op(patron, f, "provizion")
    _completeaza(pg, [("fel", "stoc")])
    assert pg.eval_on_selector("#op-cont_ajustare", "e => [e.tagName, e.value, [...e.options].map((o) => o.value).filter(Boolean)]") == [
        "SELECT", "", ["391", "392", "393", "394", "395", "396", "397", "398"]]
    patron.captura("cont_ajustare")
    rele = []
    for cheie in ("leasing", "avans", "inventariere", "taxare_inversa", "achizitie_ic", "import_ec", "chirie", "decont", "lichidare"):
        pg = _op(patron, f, cheie)
        rele += pg.evaluate("(k) => [...document.querySelectorAll('.grila-campuri input')].filter((e) => e.type !== 'date'"
                            " && (e.value || e.placeholder)).map((e) => k + ':' + e.id + '=' + (e.value || e.placeholder))", cheie)
    patron.captura("formulare")
    assert rele == [], rele


# ── 511 / 512 / 513 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_511_512_ajustarea_creantei_pe_factura_cu_partea_nedeductibila(patron, firma_ops):
    """511 / 512 / 513. Pașii: o factură emisă de 1.210 lei (scadența trecută: DATE DE PORNIRE, scadența mutată cu 300 de zile în urmă) ->
    Provizioane și ajustări -> Ajustare creanțe — constituire: factura se alege din lista celor neîncasate („sold 1.210,00 lei · 300 zile de la
    scadență”), suma și zilele nu se mai scriu -> nota 6814 = 491 1.210; caseta: deductibil 363 (30%, CF art.26 alin.(1) lit.c)),
    nedeductibil 847, care intră în ajustările fiscale ale anului (D101 rd.29), legată de notă. Provizioanele au și 1515 / 1517.
    MUTAȚIA: partea nedeductibilă nu mai intră în ajustări (`_aj.adauga` scos) -> ROȘU."""
    from e2e_bloc_a import emite_api
    f = firma_ops
    fid = emite_api(patron, f)["factura_id"]
    # date-de-pornire: scadența facturii cu 300 de zile în urmă (zilele de la scadență ale ajustării, 511) — timpul nu se poate aștepta în probă
    sql('UPDATE "%s".facturi SET data_scadenta = %%s WHERE id = %%s' % f["schema"], ((AZI - __import__("datetime").timedelta(days=300)).isoformat(), fid))
    pg = _op(patron, f, "provizion")
    _completeaza(pg, [("data", D), ("fel", "provizion")])
    assert {"1515", "1517"} <= {x[x.find("(") + 1:x.find(")")] for x in pg.eval_on_selector("#op-tip", "e => [...e.options].map((o) => o.textContent)")}
    _completeaza(pg, [("fel", "creanta")])
    pg.wait_for_function("(id) => [...document.querySelectorAll('#op-factura_id option')].some((o) => o.value === String(id))", arg=fid, timeout=20000)
    sold = sql('SELECT total FROM "%s".facturi WHERE id = %%s' % f["schema"], (fid,))[0][0]
    _completeaza(pg, [("factura_id", fid), ("garantata", "false"), ("afiliata", "false"), ("faliment", "false")])
    ultima = _ultima(f)
    m = _genereaza(pg)
    patron.captura("ajustarea")
    (nid,) = _note_noi(f, ultima)
    assert [x[:3] for x in _linii(f, nid)] == [("6814", "491", "%.2f" % sold)]
    aj = sql('SELECT rand, suma FROM "%s".ajustari_fiscale WHERE inregistrare_id = %%s' % f["schema"], (nid,))
    assert aj and aj[0][0] == "P29" and abs(float(aj[0][1]) - float(sold) * 0.7) < 0.02, aj
    assert "nedeductibil" in m, m


# ── 505 / 507 / 508 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_505_507_508_obiectul_de_inventar_ales_din_registru(patron, firma_ops):
    """505 / 506 / 507 / 508. Pașii: Obiecte de inventar -> Achiziție: „Valoare fără TVA” 350, cota 21, furnizorul și factura OI-1 -> nota
    303 = 401 / 4426 = 401 cu furnizorul, documentul „Factura OI-1” (nu „Notă de calcul”) -> nota validată -> Dare în folosință: obiectul se
    alege din registru (valoarea vine de la el) -> nota 603 = 303 350, iar 8035 debit 350 stă în afara bilanțului (fără 891, nu în rândurile
    notei) -> nota validată -> Scoatere din folosință: obiectul ales -> „Înregistrat în afara bilanțului”: 8035 credit 350, procesul-verbal.
    MUTAȚIA: darea în folosință scrie iar 8035 = 891 în notă (`nota_dare_folosinta`) -> ROȘU."""
    f = firma_ops
    s = f["schema"]
    pg = _op(patron, f, "obiect_inv")
    _completeaza(pg, [("data", D), ("operatie", "achizitie")])
    assert "Valoare fără TVA" in pg.inner_text(".camp:has(#op-valoare) .camp-eticheta")
    _completeaza(pg, [("denumire", "Scaun birou E2E"), ("valoare", "350"), ("cota", "21"), ("furnizor_cui", "31654471"),
                      ("furnizor_nume", "Mobila Proba SRL"), ("numar", "OI-1"), ("durata_sub_1_an", "false")])
    ultima = _ultima(f)
    _genereaza(pg)
    (n1,) = _note_noi(f, ultima)
    assert _linii(f, n1) == [("303", "401", "350.00", "Mobila Proba SRL"), ("4426", "401", "73.50", "Mobila Proba SRL")]
    assert sql('SELECT document_ref FROM "%s".inregistrari WHERE id = %%s' % s, (n1,))[0][0].startswith("Factura nr OI-1")
    _valideaza(patron, f, n1)
    (oid,) = sql('SELECT id FROM "%s".obiecte_inventar WHERE denumire = %%s' % s, ("Scaun birou E2E",))[0]
    pg = _op(patron, f, "obiect_inv")
    _completeaza(pg, [("data", D), ("operatie", "dare_folosinta"), ("obiect_id", oid)])
    ultima = _ultima(f)
    m = _genereaza(pg)
    patron.captura("dare_in_folosinta")
    (n2,) = _note_noi(f, ultima)
    assert [x[:3] for x in _linii(f, n2)] == [("603", "303", "350.00")]
    assert "8035 debit 350,00 lei (în afara bilanțului)" in m, m
    _valideaza(patron, f, n2)
    pg = _op(patron, f, "obiect_inv")
    _completeaza(pg, [("data", D), ("operatie", "scoatere"), ("obiect_id", oid)])
    m = _genereaza(pg)
    patron.captura("scoatere")
    assert "Înregistrat în afara bilanțului" in m and "8035 credit 350,00 lei" in m and "Proces-verbal de scoatere din folosință" in m, m
    assert sql('SELECT sens FROM "%s".evidenta_extrabilant WHERE obiect_id = %%s ORDER BY id' % s, (oid,)) == [("D",), ("C",)]


# ── 520 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_520_minusul_intreaba_daca_lipsa_e_dovedita_si_imputa_salariatul(patron, firma_ops):
    """520. „Întrebarea «Bunul lipsă era asigurat sau a fost distrus» nu e criteriul legal: art. 304 alin. (2) scutește de ajustarea TVA doar
    bunurile distruse, pierdute sau furate, dovedite […]. La imputare către salariat nu se alege salariatul.” Pașii: Inventariere anuală ->
    Minus: întrebarea e „Lipsa e dovedită ca distrugere, pierdere sau furt” -> Da fără document: refuz lângă „Documentul doveditor” -> Nu,
    imputabil salariatului ales din listă -> nota 607 = 371, 4282 = 7581 pe salariat, 635 = 4426.
    MUTAȚIA: documentul nu se mai cere la lipsa dovedită -> nota se scrie -> ROȘU."""
    f = firma_ops
    sid, _cnp_s = _salariat(patron, f, "Popa", "Ana", "290031240002", 5000)
    pg = _op(patron, f, "inventariere")
    _completeaza(pg, [("data", D), ("operatie", "minus")])
    assert "Lipsa e dovedită ca distrugere, pierdere sau furt" in pg.inner_text(".camp:has(#op-lipsa_dovedita) .camp-eticheta")
    assert pg.locator("#op-asigurat_sau_distrus").count() == 0
    _completeaza(pg, [("valoare", "1000"), ("cont_stoc", "371"), ("cota", "21"), ("imputabil", "false"), ("lipsa_dovedita", "true")])
    ultima = _ultima(f)
    pg.click("#op-trimite")   # documentul doveditor e obligatoriu pe ramura „Da”: refuzul vine lângă câmp, nu în caseta de după generare
    pg.wait_for_selector('.msg-eroare[data-camp="op-document_lipsa"], #op-mesaj.msg-eroare', timeout=20000)
    patron.captura("fara_document")
    assert _note_noi(f, ultima) == []
    _completeaza(pg, [("lipsa_dovedita", "false"), ("imputabil", "true"), ("valoare_imputare", "1200"), ("vinovat", "salariat"),
                      ("salariat_id", sid)])
    _genereaza(pg)
    patron.captura("imputat")
    (nid,) = _note_noi(f, ultima)
    assert _linii(f, nid) == [("607", "371", "1000.00", None), ("4282", "7581", "1200.00", "Popa Ana"), ("635", "4426", "210.00", None)]


# ── 527 / 533 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_527_533_dividendul_si_partajul_din_soldurile_pe_asociati(patron, firma_ops):
    """527 / 533. Pașii: DATE DE PORNIRE: soldurile preluate 1012 = 200 C și 117 = 14.600 C (fără analitic, ca F2), asociații Pop Ion 60% și
    Pop Maria 40% (Date firmă -> Asociați) -> Lichidare -> Partaj către asociați: capitalul, rezervele și profitul nu se mai scriu, vin din
    solduri, iar nota are câte un rând pe asociat (1012 = 456 120 / 80, 117 = 456 8.760 / 5.840, impozitul 10% pe câștig: 876 / 584 —
    CF art.97 alin.(5)) -> Decontări asociați -> Dividend 1.000: nota reclasifică 117 = 1171 și repartizează din 1171 (527).
    MUTAȚIA: partajul ia iar capitalul din cerere (`_partaj_lichidare` ocolit) -> refuz „Lipsește câmpul” -> ROȘU."""
    f = firma_ops
    s = f["schema"]
    # date-de-pornire: soldurile preluate pe 117 / 1012 ale firmei (profitul nerepartizat al F2, 527 / 533), ca la migrare
    sql('INSERT INTO "%s".solduri_initiale (cont, denumire, sold_debitor, sold_creditor, data_referinta) VALUES (%%s, %%s, 0, %%s, %%s), '
        '(%%s, %%s, 0, %%s, %%s)' % s, ("1012", "Capital subscris vărsat", 200, "2025-12-31", "117", "Rezultatul reportat", 14600, "2025-12-31"))
    _ok(_api(patron, "POST", "/tenants/%d/asociati" % f["tenant_id"],
             {"randuri": [{"nume": "Pop Ion", "cnp": _cnp("180010140001"), "cota": 60}, {"nume": "Pop Maria", "cnp": _cnp("280010140002"), "cota": 40}]}),
        "asociații")
    pg = _op(patron, f, "lichidare")
    _completeaza(pg, [("data", D), ("operatie", "partaj")])
    assert pg.locator("#op-capital_social").count() == 0
    ultima = _ultima(f)
    _genereaza(pg)
    patron.captura("partajul")
    (nid,) = _note_noi(f, ultima)
    linii = _linii(f, nid)
    assert ("1012", "456", "120.00", "Pop Ion") in linii and ("117", "456", "5840.00", "Pop Maria") in linii, linii
    assert ("456", "446", "876.00", "Pop Ion") in linii and ("456", "446", "584.00", "Pop Maria") in linii, linii
    # 527: dividendul din profitul preluat pe 117 se repartizează din 1171, după reclasificarea din aceeași notă
    pg = _op(patron, f, "asociati")
    _completeaza(pg, [("data", D), ("operatie", "dividend"), ("brut", "1000"), ("numar_hotarare", "AGA-527"), ("data_hotarare", D),
                      ("interimar", "0"), ("cu_plata", "false")])
    ultima = _ultima(f)
    _genereaza(pg)
    patron.captura("dividendul")
    (nd,) = _note_noi(f, ultima)
    ld = [x[:3] for x in _linii(f, nd)]
    assert ld[0] == ("117", "1171", "1000.00") and {d for d, c, _s in ld if c == "457"} == {"1171"}, ld


# ── 528 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_528_subventia_pe_activ_se_reia_odata_cu_amortizarea(patron, firma_ops):
    """528. Pașii: MF-S (60.000 lei, 60 de luni, PIF 10.01.2026, rata 1.000) -> Subvenții -> Investiții, la dreptul de a primi, 30.000, pe
    MF-S ales din registru -> nota 445 = 4751 30.000 pe activ -> validată -> „Generează amortizarea” lunii trecute (ruta Registrului jurnal):
    nota SUBV a lunii 4751 = 7584 500 (1.000 × 30.000 / 60.000), pe activ — fără nimic scris de mână.
    MUTAȚIA: `_reluare_subventii` nu mai e chemată de amortizarea lunii -> nicio notă SUBV -> ROȘU."""
    f = firma_ops
    s = f["schema"]
    mid = _mf(f, "MFS", "60000", 60, "2026-01-10")
    pg = _op(patron, f, "subventie")
    assert pg.eval_on_selector("#op-fel", "e => [...e.options].map((o) => o.value)") == ["", "exploatare", "investitii"]
    _completeaza(pg, [("data", D), ("fel", "investitii"), ("suma", "30000"), ("moment", "drept"), ("mijloc_fix_id", mid)])
    ultima = _ultima(f)
    _genereaza(pg)
    patron.captura("subventia")
    (nid,) = _note_noi(f, ultima)
    _valideaza(patron, f, nid)
    an, luna = (AZI.year, AZI.month - 1) if AZI.month > 1 else (AZI.year - 1, 12)
    r = _ok(_api(patron, "POST", "/tenants/%d/amortizare?an=%d&luna=%d" % (f["tenant_id"], an, luna)), "amortizarea lunii")
    assert r.get("reluare_subventii"), r
    assert sql('SELECT l.cont_debit, l.cont_credit, l.suma::text, ml.mijloc_fix_id FROM "%s".inregistrari i JOIN "%s".inregistrari_linii l '
               'ON l.inregistrare_id = i.id JOIN "%s".mf_linii ml ON ml.linie_id = l.id WHERE i.numar = %%s' % (s, s, s),
               ("SUBV-%d-%02d" % (an, luna),)) == [("4751", "7584", "500.00", mid)]


# ── 529 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_529_mesajul_dispare_la_schimbarea_operatiei_si_numeste_nota(patron, firma_ops):
    """529. „La Chirii / comodat / refacturări mesajul nu afișează nota […]; la schimbarea operației mesajul vechi rămâne pe ecran.” Pașii:
    Chirie plătită de la persoană fizică 1.000 -> caseta verde numește nota și conturile ei (612 = 462) -> alt „Fel” -> caseta dispare.
    MUTAȚIA: golirea mesajului la schimbarea primului select scoasă -> caseta rămâne -> ROȘU."""
    f = firma_ops
    pg = _op(patron, f, "chirie")
    _completeaza(pg, [("data", D), ("fel", "chirie_platita"), ("furnizor_cui", _cnp("170010140003")), ("furnizor_nume", "Proprietar PF"),
                      ("chirie", "1000"), ("proprietar", "pf")])
    m = _genereaza(pg)
    patron.captura("nota_chiriei")
    assert "612 = 462" in m and "Notă generată" in m, m
    _completeaza(pg, [("fel", "comodat")])
    assert pg.inner_text("#op-mesaj").strip() == ""


# ── 532 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_532_sponsorizarea_duce_cheltuiala_in_d101(patron, firma_ops):
    """532. Pașii: Sponsorizare: beneficiarul (CUI + denumire), 5.000, contract, înscris în Registrul entităților: Da — cifra de afaceri și
    impozitul nu se mai cer -> nota 6582 = 401 cu beneficiarul; caseta spune plafonul (0,75% din cifra de afaceri a anului și 20% din
    impozit, calculat de D101 la nivelul anului); cheltuiala intră în ajustările anului pe rândul 27 al D101, legată de notă.
    MUTAȚIA: ajustarea P27 scoasă din `nota_sponsorizare_ep` -> ROȘU."""
    f = firma_ops
    pg = _op(patron, f, "sponsorizare")
    assert pg.locator("#op-cifra_afaceri").count() == 0 and pg.locator("#op-impozit_profit").count() == 0
    _completeaza(pg, [("data", D), ("suma", "5000"), ("beneficiar_cui", "18765430"), ("beneficiar_nume", "Asociatia Proba"),
                      ("mod", "contract"), ("beneficiar_in_registru", "true")])
    ultima = _ultima(f)
    m = _genereaza(pg)
    patron.captura("sponsorizarea")
    (nid,) = _note_noi(f, ultima)
    assert _linii(f, nid) == [("6582", "401", "5000.00", "Asociatia Proba")]
    assert sql('SELECT rand, suma::text FROM "%s".ajustari_fiscale WHERE inregistrare_id = %%s' % f["schema"], (nid,)) == [("P27", "5000.00")]
    assert "D101" in m and "0,75%" in m, m


# ── 537 / 552 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_537_achizitia_intracomunitara_in_moneda_facturii(patron, firma_ops):
    """537. Pașii: Achiziție intracomunitară: moneda EUR din listă, 1.000 EUR, cursul BNR al zilei exigibilității îl ia aplicația (DATE DE
    PORNIRE: cursul în cache-ul BNR al bazei de test, 5,0000) -> factura primită în EUR, cu cursul; nota 371 = 401 5.000 lei; D301 cu
    valoarea în valută și codul furnizorului fără prefixul dublat (539).
    MUTAȚIA: cursul ignorat (`curs = 1`) -> 371 = 401 1.000 -> ROȘU."""
    import datetime as _dt
    from core import scadente as _sc
    for k in range(1, 8):
        z = AZI - _dt.timedelta(days=k)
        if not _sc.e_zi_lucratoare(z):   # [lotul 13, fact] BNR nu comunică în zilele nelucrătoare: un rând pe sâmbătă / duminică trecea drept
            continue                     # „cel mai nou curs” și ascundea golul din `e2e_lot11_a460` (cache-ul public e comun)
        # date-de-pornire: cursul BNR al zilei, în afara plasei (ANAF / BNR simulate)
        sql("INSERT INTO public.curs_bnr_zilnic (data, moneda, curs, luat_la) VALUES (%s, 'EUR', 5.0000, now()) ON CONFLICT DO NOTHING",
            (z.isoformat(),))
    f = firma_ops
    s = f["schema"]
    pg = _op(patron, f, "achizitie_ic")
    _completeaza(pg, [("data", D), ("moneda", "EUR"), ("valoare", "1000"), ("cod_tva_furnizor", "DE123456789"), ("numar", "AIC-537"),
                      ("cont_destinatie", "371"), ("tip", "bunuri"), ("cota", "21"), ("data_faptului_generator", D)])
    ultima = _ultima(f)
    m = _genereaza(pg)
    patron.captura("aic_eur")
    nid = _note_noi(f, ultima)[-1]
    linii = [x[:3] for x in _linii(f, nid)]
    curs = float(sql("SELECT curs FROM public.curs_bnr_zilnic WHERE moneda = 'EUR' AND data < %s ORDER BY data DESC LIMIT 1", (D,))[0][0])
    assert linii[0] == ("371", "401", "%.2f" % (1000 * curs)), (linii, m)
    assert sql('SELECT moneda FROM "%s".facturi WHERE numar = %%s' % s, ("AIC-537",)) == [("EUR",)]
    assert sql('SELECT partener_cod, tip_valuta FROM "%s".d301_operatiuni WHERE nr_doc = %%s' % s, ("AIC-537",)) == [("123456789", "EUR")]


def test_def_552_importul_cere_dvi_si_furnizorul(patron, firma_ops):
    """552. Pașii: Import extracomunitar: numărul DVI, furnizorul extern, valoarea vamală 10.000 lei, taxa vamală 10%, accesorii 500, cota 21,
    TVA plătită în vamă -> nota cu documentul „DVI nr …”, furnizorul pe 401, iar caseta spune că accesoriile intră în baza TVA și costul lor
    vine prin factura transportatorului.
    MUTAȚIA: documentul DVI scos (`document_ref` nescris) -> nota cu „Notă de calcul” -> ROȘU."""
    f = firma_ops
    pg = _op(patron, f, "import_ec")
    _completeaza(pg, [("data", D), ("numar_dvi", "DVI-552"), ("furnizor_nume", "Supplier China Ltd"), ("valoare_vamala", "10000"),
                      ("cont_destinatie", "371"), ("procent_taxa_vamala", "10"), ("accize", "0"), ("accesorii", "500"), ("cota", "21"),
                      ("certificat_amanare", "false")])
    ultima = _ultima(f)
    m = _genereaza(pg)
    patron.captura("importul")
    (nid,) = _note_noi(f, ultima)
    assert sql('SELECT document_ref FROM "%s".inregistrari WHERE id = %%s' % f["schema"], (nid,))[0][0].startswith("DVI nr DVI-552")
    assert ("371", "401", "10000.00", "Supplier China Ltd") in _linii(f, nid)
    assert "factura transportatorului" in m, m


# ── 541 / 549 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_541_nota_tva_la_incasare_nu_exigibilizeaza_peste_4428(patron, firma_ops):
    """541. „Nota manuală «TVA la încasare» generează 4428 = 4427 fără verificarea soldului.” Pașii: TVA la încasare -> Încasare de la
    client, 1.210 cu TVA, cota 21, faptul generator -> fără TVA neexigibil pe 4428: refuzul spune că nota ar lăsa 4428 cu sold invers; nicio
    notă.
    MUTAȚIA: `cere_sold_4428` nu mai refuză -> nota 4428 = 4427 se scrie -> ROȘU."""
    f = firma_ops
    pg = _op(patron, f, "tva_incasare")
    _completeaza(pg, [("data", D), ("sens", "incasare"), ("suma_incasata", "1210"), ("data_fapt_generator", D), ("ramura_291_5", "fapt_generator"),
                      ("cota", "21")])
    ultima = _ultima(f)
    m = _genereaza(pg)
    patron.captura("refuz_4428")
    assert "4428 cu sold invers" in m, m
    assert _note_noi(f, ultima) == []


def test_def_549_agricultorul_neinscris_achizitie_fara_compensatie(patron, firma_ops):
    """549. „Cu agricultorul neînscris în registru, aplicația refuză toată achiziția; cumpărarea e legală, doar compensația nu se deduce.”
    Pașii: Achiziție de la agricultor: agricultorul (CNP + nume), 10.000, cont 301 (gol până îl scrii), în registru: Nu -> nota 301 = 401
    10.000 cu agricultorul, fără 4426, iar caseta spune că nu se aplică compensația.
    MUTAȚIA: neînscrisul refuzat din nou (`achizitie_de_la_agricultor`) -> ROȘU."""
    f = firma_ops
    pg = _op(patron, f, "agricultor_achizitie")
    assert pg.input_value("#op-cont_cheltuiala") == ""
    _completeaza(pg, [("data", D), ("agricultor_cui", _cnp("160010140004")), ("agricultor_nume", "Ion Agricultor"), ("valoare", "10000"),
                      ("cont_cheltuiala", "301"), ("agricultor_in_registru", "false")])
    ultima = _ultima(f)
    m = _genereaza(pg)
    patron.captura("agricultor_neinscris")
    (nid,) = _note_noi(f, ultima)
    assert _linii(f, nid) == [("301", "401", "10000.00", "Ion Agricultor")]
    assert "fără compensație" in m, m


# ── 510 / 548 / 551 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _stoc_pe_articol(f):
    """DATE DE PORNIRE (declarat): firma ține stocul cantitativ-valoric (Date firmă › metoda de stoc) — nu e pasul probat."""
    # date-de-pornire: metoda de stoc a firmei (Date firmă), declarată — nu e pasul probat
    sql('UPDATE "%s".firma_profil SET metoda_stoc = %%s' % f["schema"], ("cantitativ_valoric",))


def _marfa_in_stoc(f, denumire, cant, pret):
    """DATE DE PORNIRE (declarat): bunul în fișa de magazie (marfă, 371), ca după NIR — scrierea aplicației (`stocuri_cv_api.intrare`)."""
    from core import db, stocuri_cv_api
    with db.get_conn(f["schema"]) as c:
        stocuri_cv_api.intrare(c, f["schema"], {"denumire": denumire, "um": "buc", "cont_stoc": "371", "cont_cheltuiala": "607",
                                                "data": D, "cantitate": cant, "pret_unitar": pret, "document": "NIR E2E"})
        c.commit()


def test_def_510_productia_intra_in_stoc_si_se_vinde_pe_factura(patron, firma_ops):
    """510. Costin: „Obținerea nu cere produs, cantitate, gestiune; la vânzare costul standard ieșit și coeficientul 348 se introduc de mână.”
    Pașii: Producție › Obținere: produsul nou „Masa E2E” (buc), 10 bucăți la costul standard 100, costul efectiv 1.100, gestiunea „Magazia
    PF” -> nota 345 = 711 1.000 + 348 = 711 100 cu Bonul de predare, intrarea în fișa de magazie legată de notă; nota validată din
    Registrul jurnal; Producție › Vânzare: 4 bucăți la 150, cota 21, clientul -> factura emisă (4111 = 701 600 + 4427 126), descărcarea
    711 = 345 400 și diferențele 711 = 348 40 (K = 100 / 1.000, OMFP 1802/2014 pct.286 alin.(4)); niciun cost sau coeficient scris de mână.
    MUTAȚIA: coeficientul socotit fără diferențele intrărilor (`dif_intrari` = 0) -> nicio notă a diferențelor -> ROȘU."""
    f = firma_ops
    _stoc_pe_articol(f)
    pg = _op(patron, f, "productie")
    _completeaza(pg, [("data", D), ("operatie", "obtinere"), ("produs", "Masa E2E"), ("um", "buc"), ("cantitate", "10"),
                      ("cost_standard", "100"), ("cost_efectiv", "1100"), ("gestiune", "Magazia PF")])
    assert "Produs nou" in pg.inner_text("#op-produs-stare")
    ultima = _ultima(f)
    m = _genereaza(pg)
    patron.captura("obtinerea")
    (nid,) = _note_noi(f, ultima)
    assert [x[:3] for x in _linii(f, nid)] == [("345", "711", "1000.00"), ("348", "711", "100.00")], m
    assert sql('SELECT document_ref FROM "%s".inregistrari WHERE id = %%s' % f["schema"], (nid,))[0][0].startswith("Bon de predare")
    assert sql('SELECT m.cantitate::text, m.locatie FROM "%s".miscari_stoc m WHERE m.inregistrare_id = %%s' % f["schema"], (nid,)) == [
        ("10.000", "Magazia PF")]
    _valideaza(patron, f, nid)
    pg = _op(patron, f, "productie")
    _completeaza(pg, [("data", D), ("operatie", "vanzare"), ("produs", "Masa E2E"), ("cantitate", "4"), ("pret_vanzare", "150"),
                      ("cota", "21"), ("client_cui", "18765430"), ("client_nume", "Mobila Client SRL")])
    pg.wait_for_function("() => (document.querySelector('#op-produs-stare') || {innerText: ''}).innerText.includes('în stoc 10')", timeout=20000)
    ultima = _ultima(f)
    m = _genereaza(pg)
    patron.captura("vanzarea")
    noi = _note_noi(f, ultima)
    linii = sorted(x[:3] for n in noi for x in _linii(f, n))
    assert linii == sorted([("4111", "701", "600.00"), ("4111", "4427", "126.00"), ("711", "345", "400.00"), ("711", "348", "40.00")]), (linii, m)
    assert sql('SELECT directie, tert_nume FROM "%s".facturi ORDER BY id DESC LIMIT 1' % f["schema"]) == [("emisa", "Mobila Client SRL")]


def test_def_548_marja_si_aurul_ies_din_stoc_cu_clientul(patron, firma_ops):
    """548. Costin: „Vânzarea nu descarcă bunul din gestiune (607 = 371 / costul aurului) și nu cere clientul […] Prețul de cumpărare se
    scrie de mână în loc să vină din bunul aflat în stoc.” Pașii: bunul „Ceas E2E” în stoc la 300; Vânzare regim marjă: bunul din listă (sub
    câmp „în stoc 1 buc · CMP 300,00 lei”), prețul 510, cota 21, clientul „Ion Pop”, documentul -> 4111 = 707 473,55 + 4111 = 4427 36,45 pe
    client și 607 = 371 300 (ieșirea la CMP); jurnalul marjei arată prețul de cumpărare 300. Apoi aurul: „Lingou E2E” în stoc la 30.000,
    livrare scutită 33.000 către o persoană fizică -> 4111 = 707 33.000 pe client, 607 = 371 30.000.
    MUTAȚIA: ieșirea din stoc scoasă din vânzarea în regim de marjă (prețul de cumpărare din cerere) -> ROȘU."""
    f = firma_ops
    _stoc_pe_articol(f)
    _marfa_in_stoc(f, "Ceas E2E", 1, 300)
    pg = _op(patron, f, "marja")
    _completeaza(pg, [("data", D), ("articol", "Ceas E2E"), ("cantitate", "1"), ("pret_vanzare", "510"), ("cota", "21"),
                      ("client_nume", "Ion Pop"), ("document", "Factura nr 5 din azi")])
    pg.wait_for_function("() => (document.querySelector('#op-articol-stare') || {innerText: ''}).innerText.includes('CMP 300,00')", timeout=20000)
    ultima = _ultima(f)
    m = _genereaza(pg)
    patron.captura("marja")
    noi = _note_noi(f, ultima)
    linii = sorted(x for n in noi for x in _linii(f, n))
    assert linii == sorted([("4111", "707", "473.55", "Ion Pop"), ("4111", "4427", "36.45", "Ion Pop"), ("607", "371", "300.00", None)]), (linii, m)
    j = _ok(_api(patron, "GET", "/tenants/%d/jurnal-marja?tip=secondhand&luna=%s" % (f["tenant_id"], D[:7])), "jurnalul marjei")
    assert [(n["cost"], n["tva"]) for n in j["note"]] == [("300.00", "36.45")], j
    _marfa_in_stoc(f, "Lingou E2E", 1, 30000)
    pg = _op(patron, f, "aur")
    _completeaza(pg, [("data", D), ("articol", "Lingou E2E"), ("cantitate", "1"), ("tip", "lingou"), ("puritate", "999"), ("suma", "33000"),
                      ("calitate_client", "PF"), ("client_nume", "Ion Pop"), ("client_identificare", _cnp("185010140001")),
                      ("document", "Factura nr 6 din azi")])
    ultima = _ultima(f)
    m = _genereaza(pg)
    patron.captura("aur")
    noi = _note_noi(f, ultima)
    linii = sorted(x for n in noi for x in _linii(f, n))
    assert linii == sorted([("4111", "707", "33000.00", "Ion Pop"), ("607", "371", "30000.00", None)]), (linii, m)


def test_def_551_548_marja_fara_metoda_de_stoc_trimite_in_date_firma(patron, firma_ops):
    """551 (partea Operațiunilor): „Inconsecvent: vânzarea în regim de marjă și cea de aur au trecut fără metoda de stoc.” Pașii: firma fără
    metoda de stoc declarată -> Vânzare regim marjă, completat -> refuzul metodei de stoc, cu butonul „Deschide Date firmă”; nicio notă.
    MUTAȚIA: cererea metodei de stoc scoasă din vânzarea în regim de marjă -> nota trece fără metodă -> ROȘU."""
    f = firma_ops
    # date-de-pornire: metoda de stoc nedeclarată — starea pe care o refuză vânzarea (551)
    sql('UPDATE "%s".firma_profil SET metoda_stoc = NULL' % f["schema"])   # DATE DE PORNIRE (declarat): metoda nedeclarată
    pg = _op(patron, f, "marja")
    _completeaza(pg, [("data", D), ("articol", "Ceas E2E"), ("cantitate", "1"), ("pret_vanzare", "510"), ("cota", "21"),
                      ("client_nume", "Ion Pop"), ("document", "BF 1")])
    ultima = _ultima(f)
    m = _genereaza(pg)
    pg.wait_for_selector("[data-ecran-destinatie='date_firma']", timeout=20000)
    patron.captura("refuz_metoda")
    assert "metoda de stoc" in m and _note_noi(f, ultima) == [], m
