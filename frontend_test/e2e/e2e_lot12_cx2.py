# -*- coding: utf-8 -*-
"""Lotul 12, pachetul `cx2` — testele de capăt la capăt care lipseau pentru numerele găsite de Code în lot (declarații, Control fiscal,
Supervizor, salarii, stoc) și pentru trei explicații din cod. Pașii contabilului pe aplicația din index, pe baza de TEST, fiecare pe o firmă
NOUĂ de test (`firma_noua`), scoasă la final.

  C134 D112: rândul 4 „Total fond de salarii brute” cuprinde și indemnizația CM suportată de angajator.
  C141 D407 nu mai primește termenul ghicit „25.07 / 25.01”: în coadă stă perioada, nu o dată.
  C142 D406: clientul unei facturi a perioadei, lipsă din nomenclatorul nevid de parteneri, apare în MasterFiles.
  C148 Mesajul perioadei indisponibile spune data ca ZZ.LL.AAAA, fără „decizie de dezvoltator”.
  C149 D177 / D107: clicul pe „+ adaugă” / „Regenerează” după scrierea unei sume nu se mai pierde (D603: numai garda statică).
  C130 Lucrătorul Supervizorului e chemat de tura de 5 minute a `firma_rezumat`.
  C147 Rezultatul Supervizorului poartă versiunea regulilor: cel calculat cu regulile vechi nu rămâne „curent”.
  C131 Reconcilierea declarațiilor față de documente se arată în Control fiscal, câte un rând pe declarație.
  C146 Refuzul ștergerii notei unui Z din Registrul jurnal trimite la cardul „Raport Z” și la butonul lui.
  491  (explicație, fără schimbare de cod) O constatare urcă firma cel mult la galben; roșul vine numai dintr-o restanță.
  497  (explicație, fără schimbare de cod) Restanța = obligație cu termenul trecut, nedepusă, nemarcată, de la luna preluării.
  C126 TVA-ul transportului facturat (4428.01 = 401) nu rămâne pe 4428.01 după legarea facturii mărfii; NIR-ul vechi trece pe 4426.
  C138 NIR „fără factură” cu transportul pe factura mărfii e propus la validarea facturii (costul complet = netul facturii).
  153  NIR-urile „fără factură” scrise pe 401 / 4426 primesc nota de refacere pe 408 / 4428.01.
  C108 Ciorna „salariat nou” e a utilizatorului care o scrie (cheia pe utilizator + firmă, în browser și pe server).

DATE DE PORNIRE scrise direct, declarate la fiecare instrucțiune (`# date-de-pornire:`): rezultatul Supervizorului lăsat de codul de dinainte
(C147), rândurile NIR-ului cum le scria codul de dinainte de reparație (C126 vechi, 153). Restul intră pe rutele ecranelor. CUI-urile:
DANTE INTERNATIONAL SA 14399840, ALTEX ROMANIA SRL 2864518, 1590082, 13548146 — cifra de control verificată.

Temeiurile, citate unde se aplică (antetul fiecărei părți de mai jos, cu fișierul din cod care le citează): OPANAF 605/2026 anexa 2
secțiunea B (C134), CPF art.61^2 alin.(2) (C141), OPANAF 1783/2021 anexa 3 pct.11 (C142), CF art.299 alin.(1) lit.a și OMFP 1802/2014
pct.69 (C126, C138, 153); N/A temei fiscal la C148, C149, C130, C147, C131, C146, 491, 497, C108 (reguli de ecran / de calcul ale aplicației).
Mutațiile: `mut_lot12_cx2.json`; dovezile pe copia firmelor de test: `frontend_test/dovada/dovezi_lot12_cx2.json`."""
import contextlib
import datetime as _dt
import os
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from decimal import Decimal

import pytest

from conftest import (GARDA_DESCHIDERI, INALT, LAT, Ecran, _db, _ecran, _scoate_firmele_e2e, firma_noua, perioada_incheiata, sesiune,
                      sql)
from e2e_bloc_a import AZI, _api, _card, _ok, cont_asistent, pregateste_firma
from e2e_bloc_b import _cnp, _deschide_rand, _nota_jn
from e2e_bloc_d import PATRON, _firma_noua
from e2e_bloc_d import _api as _api_cont
from e2e_comanda_1010 import _lista_control
from e2e_lot11_s9 import _F, _d112_xml, _firma_cu_salariat, _singurul, _un
from e2e_lot12_ctrl import _factura_validata
from e2e_lot12_ctrl_d112 import _certificat_01
from e2e_lot12_decl import IBAN, _factura, _pasul2, _xml
from e2e_lot12_decl import _profil as _a_profil_decl
from e2e_lot12_zsterge import _xml_amef
from e2e_pilot_luna import _ubl


# ═══ Declarații: C134, C141, C142, C148, C149 (D177 și D107). Dovezi fără test nou: C119, 493 (dovezi_lot12_cx2.json). ═══
# Temeiuri (citate din repo, nu din memorie):
#   C134 — OPANAF 605/2026 anexa 2, secțiunea B, rândul 4 „Total fond de salarii brute” (citatul în core/d112.py:841-847).
#   C141 — CPF art.61^2 alin.(2): „termenele-limită ale raportării se aprobă prin ordin comun …” (core/scadente.py:143-147,
#          `TEMEI_FARA_TERMEN`); ordinul comun ANAF–ASF nu e în corpus, deci D407 n-are termen.
#   C142 — OPANAF 1783/2021 anexa 3 pct.11 și pct.27; d406_schema_anaf.xlsx „2. MasterFiles” MF.C.1 (core/d406.py:403-411).
#   C148 — N/A temei fiscal: forma datei pentru om (DESIGN_SYSTEM cap.4, `pdf_util.data_ro`, core/common.py:944-948).
#   C149 — N/A temei fiscal: comportamentul formularului (garda statică core/test_lot12_decl_rerandare_camp.py).



_A_Z = ".fereastra:last-of-type "
_A_NS406 = "{mfp:anaf:dgti:d406:declaratie:v1}"


# ── C134 — D112: B_brutSalarii cuprinde și indemnizația CM plătită de angajator ─────────────────────────────────────────────────
@pytest.fixture
def firma_cx2a_c134():
    f = _firma_cu_salariat("L12M", salariu_brut=6000)
    try:
        yield f
    finally:
        _scoate_firmele_e2e(f["tenant_id"])


def test_def_c134_d112_fondul_de_salarii_brute_cuprinde_indemnizatia_cm_a_angajatorului(patron, firma_cx2a_c134):
    """C134. Pașii: salariat cu 6.000 lei -> statul lunii trecute -> „Concediu” -> „+ Certificat nou”: cod 01, INIȚIAL, 1–9 ale lunii
    trecute -> „Calculează și salvează” -> Declarații -> D112 pe luna trecută -> DUKIntegrator „fără erori” -> „Vezi XML-ul generat”:
    rândul 4 „Total fond de salarii brute” (`angajatorB/@B_brutSalarii`) = salariul realizat (B2_5) + indemnizația suportată de angajator
    (Σ D_20) = baza CAM (`angajatorC4/@C4_baza`). Înainte: rândul 4 lua numai salariul (`sum_bazac`), fără partea angajatorului din CM.
    Temei: OPANAF 605/2026 anexa 2, secțiunea B, rândul 4 — „suma câştigurilor brute realizate … precum şi sumele suportate de angajator,
    primele 5 zile de incapacitate temporară de muncă” (citat în core/d112.py)."""
    _certificat_01(patron, firma_cx2a_c134, 9, "1341")
    st = _d112_xml(patron, firma_cx2a_c134)   # cere „fără erori” la DUKIntegrator
    a = _singurul(st)
    b2 = _un(a, "asiguratB2")
    d20 = sum(int(x["D_20"]) for x in a.get("asiguratD", []))
    b = _un(st["_angajator"], "angajatorB")
    c4 = _un(st["_angajator"], "angajatorC4")
    patron.captura("d112_randul_4")
    assert d20 > 0, a.get("asiguratD")   # certificatul are zile suportate de angajator: altfel testul n-ar deosebi nimic
    # OPANAF 605/2026 anexa 2, secțiunea B rândul 4: câștigurile brute + sumele suportate de angajator pentru concediile medicale
    assert int(b["B_brutSalarii"]) == int(b2["B2_5"]) + d20, (b, b2, d20)
    assert int(b["B_brutSalarii"]) == int(c4["C4_baza"]), (b, c4)   # aceeași sumă ca baza CAM (o singură sursă, 482)


# ── C141 — D407 fără termenul ghicit „25.07 / 25.01” ──────────────────────────────────────────────────────────────────────────
#: D407 a unei instituții raportoare (tipDoc 2, lista persoanelor), forma validă pe DUKIntegrator din core/test_declaratii_lot5_duk.py;
#: CIF-urile au cifra de control verificată (13548146 cu algoritmul CUI, 1800101221144 cu algoritmul CNP)
_A_D407_MANUAL = {"tip_doc": 2, "luna": 6, "d_rec": 0, "cif": "13548146", "den": "Banca Test SA", "adresa": "Str Test 1",
                  "localitate": "Bucuresti", "judet": 40, "tara_rap": "RO", "forma_j": "SA", "nume": "Popescu Ion", "functia": "Director",
                  "persoane": [{"den_d": "Ionescu Maria", "cif_d": "1800101221144", "isin": "US0378331005", "simbol": "AAPL",
                                "cantitatea": "10", "tip_instrument": 1, "den_emitent": "Apple Inc", "adresa_d": "New York"}]}


@pytest.fixture
def firma_cx2a():
    for f in firma_noua():
        yield f


def test_def_c141_d407_in_coada_fara_termen_ghicit(patron, firma_cx2a):
    """C141. Pașii: D407 pe semestrul I (luna 6) trimisă în coadă pe ruta „Trimite în coadă →” (`POST /coada`; ecranul Declarații n-are
    formularul D407 — datele instituției raportoare vin în `manual`, ca de la API) -> pagina principală -> „De depus”: cardul D407 arată la
    „termen (scadență):” perioada de raportare („luna 06 2026”), nu o dată. Înainte: ramura implicită a termenelor îi dădea „ziua 25 a lunii
    următoare” (27.07.2026, după mutarea la zi lucrătoare), o dată pe care niciun act din corpus n-o stabilește. Temei: CPF art.61^2
    alin.(2) — termenele D407 „se aprobă prin ordin comun al președintelui Agenției Naționale de Administrare Fiscală și al președintelui
    Autorității de Supraveghere Financiară” (ordinul nu e în corpus: fără zi ghicită)."""
    tid = firma_cx2a["tenant_id"]
    azi = _dt.date.today()
    an = azi.year if azi.month > 6 else azi.year - 1      # cel mai recent semestru I încheiat (luna 6)
    r = _ok(_api(patron, "POST", "/coada", {"tenant_id": tid, "tip": "d407", "an": an, "luna": 6, "manual": _A_D407_MANUAL}), "coada D407")
    cid, per = sql("SELECT id, perioada FROM public.declaratii_coada WHERE tenant_id = %s AND tip = 'd407' ORDER BY id DESC LIMIT 1", (tid,))[0]
    assert r.get("ok") is not False and r.get("coada_id") in (None, cid), (r, cid)
    # CPF art.61^2 alin.(2): fără ordinul comun în corpus, coada poartă perioada de raportare, nu un termen (`coada_api.adauga`)
    assert re.fullmatch(r"\d{2}\.\d{2}\.\d{4}", per) is None, per
    assert per == "luna 06 %d" % an, per
    pg = patron.pg
    patron.acasa()
    pg.click("button.cab-card:has([data-cheie='validat'])")
    card = ".val-card[data-coada-ids='%d']" % cid
    pg.wait_for_selector(card, timeout=30000)
    patron.captura("de_depus_d407")
    termen = " ".join(pg.inner_text(card + " .val-termen").split())
    assert termen.endswith(per) and re.search(r"\d{2}\.\d{2}\.\d{4}", termen) is None, termen


# ── C142 — D406: clientul unei facturi a perioadei, lipsă din nomenclatorul NEVID, apare în MasterFiles ───────────────────────────
def test_def_c142_d406_clientul_facturii_lipsa_din_nomenclator_apare_in_masterfiles(patron, firma_cx2a):
    """C142. Pașii: Clienți are un client (ALTEX ROMANIA SRL, Voluntari); în luna trecută firma are o factură către ALTEX și una către
    DANTE INTERNATIONAL SA (București pe factură), care nu e în Clienți -> Declarații -> D406, luna trecută -> Continuă -> „Vezi XML-ul
    generat”: în MasterFiles → Customers apar AMÂNDOI (CustomerID 002864518 și 0014399840), fiecare CustomerID al unei facturi din
    SalesInvoices e în Customers, iar validatorul ANAF spune „fără erori”. Înainte: cu nomenclatorul nevid, partenerii facturilor nu se mai
    adăugau (completarea din facturi pornea numai pe nomenclator gol), deci DANTE lipsea din MasterFiles.
    Temei: OPANAF 1783/2021 anexa 3 pct.11 (toate informațiile aferente perioadei de raportat); d406_schema_anaf.xlsx, „2. MasterFiles”,
    MF.C.1 Customer (citate în core/d406.py, `parteneri_perioadei_master`). CUI-urile 2864518 și 14399840 au cifra de control verificată."""
    tid = firma_cx2a["tenant_id"]
    _a_profil_decl(patron, firma_cx2a)
    # nomenclatorul de clienți nevid: ALTEX, pe ruta fișei clientului (Clienți -> „+ Client nou”)
    _ok(_api(patron, "POST", "/tenants/%d/clienti" % tid, {"nume": "ALTEX ROMANIA SRL", "cui": "2864518", "oras": "Voluntari"}), "client ALTEX")
    p = perioada_incheiata("lunar")
    zi = p.inceput.replace(day=10).isoformat()
    _factura(firma_cx2a, "E142", "1", zi, "emisa", "RO2864518", "ALTEX ROMANIA SRL", [(100, 21)], oras="Voluntari")
    _factura(firma_cx2a, "E142", "2", zi, "emisa", "RO14399840", "DANTE INTERNATIONAL SA", [(200, 21)], oras="București")
    pg = _pasul2(patron, firma_cx2a, "d406", p.an, p.luna)
    patron.captura("d406_masterfiles")
    xml = _xml(pg)
    assert xml, patron.fereastra()[:3000]
    rad = ET.fromstring(xml.encode("utf-8"))
    master = {c.findtext(_A_NS406 + "CustomerID") for c in rad.iter(_A_NS406 + "Customer")}
    pe_facturi = {i.findtext("%sCustomerInfo/%sCustomerID" % (_A_NS406, _A_NS406)) for i in rad.iter(_A_NS406 + "Invoice")}
    # OPANAF 1783/2021 anexa 3 pct.11 + MF.C.1: clientul facturii perioadei e în MasterFiles, și când nomenclatorul nu-l are
    assert master >= {"002864518", "0014399840"}, master
    assert pe_facturi and pe_facturi <= master, (pe_facturi, master)
    assert pg.locator(_A_Z + ".dec-eroare").count() == 0 and pg.locator(_A_Z + ".dec-ok").count() == 1, patron.fereastra()[:3000]   # DUK D406


# ── C148 — mesajul perioadei indisponibile, cu data ZZ.LL.AAAA și fără „decizie de dezvoltator” ─────────────────────────────────
#: [C148] luna în care statul de plată nu se mai poate calcula: înaintea primei valori a salariului minim din registrul de parametri
#: fiscali (`common.COTE["salariu_minim"]`, citit din cod, nu scris aici)
def _a_prima_luna_salariu_minim():
    from core import common
    return min(x[0] for x in common.COTE["salariu_minim"])


@pytest.fixture
def firma_cx2a_c148():
    """Firmă cu un salariat angajat înaintea primei valori a salariului minim din registru (pe ruta „+ Salariat nou”), fără lună de
    preluare: statul lunilor de dinainte se poate cere din ecran."""
    f = _firma_noua("L12I")
    try:
        prima = _a_prima_luna_salariu_minim()
        ang = (prima.replace(day=1) - _dt.timedelta(days=1)).replace(month=1, day=8)
        st, r = _api_cont(PATRON, "POST", "/tenants/%d/salariati" % f["tenant_id"],
                              {"nume": "Popescu", "prenume": "Ion", "cnp": _cnp("185010140123"), "data_angajare": ang.isoformat(),
                               "tip_norma": "intreaga", "ore_zi": 8, "salariu_brut": 5000, "persoane_intretinere": 0,
                               "scutit_contrib_minim": False, "functie_baza": True, "cor": "331302"})
        assert st == 200, (st, r)
        yield f
    finally:
        _scoate_firmele_e2e(f["tenant_id"])


def test_def_c148_perioada_indisponibila_spune_data_ca_zz_ll_aaaa(patron, firma_cx2a_c148):
    """C148. Pașii: firma cu un salariat FĂRĂ tichete de masă, angajat în anul dinaintea primei valori a salariului minim din registru ->
    Salariați -> statul de plată -> „← luna”, lună cu lună: fiecare lună se calculează până la 01/2025, iar 12/2024 (luna dinaintea primei
    valori, 01.01.2025) e refuzată — ecranul nu mai are „← luna” și spune „Nu s-a putut încărca statul de plată. Calculul pentru 01.12.2024
    nu se poate face: valoarea „…” nu e definită înainte de 01.01.2025 …” — datele ca ZZ.LL.AAAA, nicio dată ISO, refuz de perioadă (423),
    nu eroare de server. Mesajul e chiar textul pentru om al refuzului din cod (`common.cota` -> `PerioadaIndisponibila` fără gol ->
    `perioada.text_exceptie`). Înainte: „2024-12-01 nu poate fi calculată … (decizie de dezvoltator)”. (Golul plafonului tichetului de masă,
    10/2025, nu e pe drumul ăsta: salariatul fără tichete nu cere plafonul — C159.) N/A temei fiscal (forma datei pentru om, DS cap.4)."""
    from core import common, perioada
    from core.pdf_util import data_ro
    pg = patron.pg
    prima = _a_prima_luna_salariu_minim()
    tinta = (prima.replace(day=1) - _dt.timedelta(days=1)).replace(day=1)   # luna dinaintea primei valori a salariului minim
    azi = _dt.date.today()
    luna = azi.replace(day=1)
    patron.firma(firma_cx2a_c148["nume"])
    pg.click("#fa-salariati")
    pg.wait_for_selector(_F + "#sp-tabel tbody tr.sp-rand", timeout=30000)
    stare = None
    while luna > tinta:
        prev = pg.inner_text(_F + ".pf-intro")
        luna = (luna - _dt.timedelta(days=1)).replace(day=1)
        cale = "/stat-plata?an=%d&luna=%d" % (luna.year, luna.month)
        with pg.expect_response(lambda r, c=cale: c in r.url, timeout=60000) as rr:
            pg.click(_F + "#sp-prev")
        stare = rr.value.status
        if stare != 200:
            break
        pg.wait_for_function("(p) => { const f = [...document.querySelectorAll('.fereastra')].pop(); const i = f.querySelector('.pf-intro');"
                             " return i && i.innerText !== p && !!f.querySelector('#sp-tabel tbody tr.sp-rand'); }", arg=prev, timeout=30000)
    # statul se calculează pe fiecare lună de la 01.01.2025 încoace, iar luna dinainte e refuzată ca perioadă indisponibilă (423)
    assert (data_ro(luna), stare) == (data_ro(tinta), 423), (data_ro(luna), stare)
    pg.wait_for_function("() => { const f = [...document.querySelectorAll('.fereastra')].pop();"
                         " return !f.querySelector('#sp-prev') && !!f.querySelector('p.ecran-nota') && !f.querySelector('#sp-tabel'); }",
                         timeout=30000)
    pg.wait_for_timeout(300)
    nota = " ".join(pg.inner_text(_F + "p.ecran-nota").split())
    patron.captura("stat_luna_indisponibila")
    # refuzurile pe care codul le dă pentru luna aceea: cotele registrului fără valoare înainte de prima lor valoare (ramura fără gol)
    asteptate = []
    for n in common.COTE:
        try:
            common.cota(n, luna)
        except common.PerioadaIndisponibila as e:
            if e.gol is None:
                asteptate.append(" ".join(perioada.text_exceptie(e).split()))
    assert asteptate and any(nota.endswith(t) for t in asteptate), (nota, asteptate)
    assert re.search(r"\d{4}-\d{2}-\d{2}", nota) is None, nota                                   # nicio dată ISO
    assert {data_ro(tinta), data_ro(prima)} <= set(re.findall(r"\b\d{2}\.\d{2}\.\d{4}\b", nota)), nota   # ZZ.LL.AAAA


# ── C159 — golul din registrul de parametri fiscali: statul din 10/2025 fără tichete se calculează, cu tichete se oprește motivat ─────────
#: [C159] luna golului declarat al plafonului tichetului de masă, citită din registru (`COTE["tichet_masa_plafon"]`: valoarea cu `data_out`
#: și succesorul ei), nu scrisă aici: prima lună de după `data_out`
def _a_luna_golului_tichetului():
    from core import common
    _din, _v, temei = [x for x in common.COTE["tichet_masa_plafon"] if getattr(x[2], "data_out", None)][0]
    return (temei.data_out + _dt.timedelta(days=1)).replace(day=1)


def _a_salariat_c159(firma, nume, tichet):
    """Un salariat pe ruta ecranului „+ Salariat nou” (`POST /tenants/{id}/salariati`), angajat la începutul anului golului."""
    st, r = _api_cont(PATRON, "POST", "/tenants/%d/salariati" % firma["tenant_id"],
                      {"nume": nume, "prenume": "Ion", "cnp": _cnp("185010140123" if not tichet else "286020240123"),
                       "data_angajare": _a_luna_golului_tichetului().replace(month=1, day=6).isoformat(), "tip_norma": "intreaga",
                       "ore_zi": 8, "salariu_brut": 5000, "persoane_intretinere": 0, "scutit_contrib_minim": False, "functie_baza": True,
                       "cor": "331302", "tichet_masa_valoare": tichet})
    assert st == 200, (st, r)


def _a_stat_pana_la(patron, firma, tinta):
    """Salariați -> statul de plată -> „← luna” până la luna `tinta`; -> codul răspunsului pentru `tinta` (200 = statul calculat). Se
    oprește la primul răspuns care nu e 200 (refuzul șterge „← luna” de pe ecran)."""
    pg = patron.pg
    patron.firma(firma["nume"])
    pg.click("#fa-salariati")
    pg.wait_for_selector(_F + "#sp-tabel tbody tr.sp-rand", timeout=30000)
    luna, stare = _dt.date.today().replace(day=1), None
    while luna > tinta:
        prev = pg.inner_text(_F + ".pf-intro")
        luna = (luna - _dt.timedelta(days=1)).replace(day=1)
        cale = "/stat-plata?an=%d&luna=%d" % (luna.year, luna.month)
        with pg.expect_response(lambda r, c=cale: c in r.url, timeout=60000) as rr:
            pg.click(_F + "#sp-prev")
        stare = rr.value.status
        if stare != 200:
            break
        pg.wait_for_function("(p) => { const f = [...document.querySelectorAll('.fereastra')].pop(); const i = f.querySelector('.pf-intro');"
                             " return i && i.innerText !== p && !!f.querySelector('#sp-tabel tbody tr.sp-rand'); }", arg=prev, timeout=30000)
    return luna, stare


@pytest.fixture
def firma_cx2a_c159():
    f = _firma_noua("L12G")
    try:
        yield f
    finally:
        _scoate_firmele_e2e(f["tenant_id"])


def test_def_c159_statul_din_10_2025_se_calculeaza_fara_tichete_si_se_opreste_motivat_cu_tichete(patron, firma_cx2a_c159):
    """C159. Pașii: firmă nouă cu un salariat FĂRĂ tichete de masă -> Salariați -> statul de plată -> „← luna” până la 10/2025 (luna
    golului din registru: plafonul tichetului de masă e verificat la sursă până la 30.09.2025 și din nou de la 01.11.2025): statul lunii se
    calculează (un rând, nicio eroare de server). Apoi „+ Salariat nou” cu tichet de masă de 40 lei și „Confirmă pontajul lunii” 10/2025
    (fără pontaj confirmat tichetele nu intră în calcul) -> statul de plată din 10/2025: ecranul arată blocajul motivat al golului —
    refuz de perioadă (423), nu 500 — cu textul pentru om al refuzului din cod (`common.cota` -> `PerioadaIndisponibila` cu `gol` ->
    `perioada.text_exceptie`): numele valorii pentru om (`ETICHETE_COTE`), datele ZZ.LL.AAAA, fără cheia tehnică, fără eticheta
    `PERIOADA_BLOCATA`, fără dată ISO. Statul se calculează pe FIRMĂ: salariatul cu tichete oprește tot statul lunii (și rândul celui fără
    tichete). Înainte: 500 pentru orice firmă cu salariați, cu „tichet_masa_plafon: … Completează valoarea valabilă în registru.”
    N/A temei fiscal (golul e al registrului; plafonul și temeiul lui: `COTE["tichet_masa_plafon"]`)."""
    from core import common, perioada
    from core.pdf_util import data_ro
    f = firma_cx2a_c159
    pg = patron.pg
    gol = _a_luna_golului_tichetului()
    _a_salariat_c159(f, "Fara Tichete", 0)
    luna, stare = _a_stat_pana_la(patron, f, gol)
    patron.captura("fara_tichete_10_2025_calculat")
    assert (data_ro(luna), stare) == (data_ro(gol), 200), (data_ro(luna), stare)    # golul nu oprește firma care nu dă tichete
    assert pg.locator(_F + "#sp-tabel tbody tr.sp-rand").count() == 1
    # al doilea salariat, cu tichete, și pontajul lunii confirmat (butonul „Confirmă pontajul lunii”, aceeași rută)
    _a_salariat_c159(f, "Cu Tichete", 40)
    st, r = _api_cont(PATRON, "POST", "/tenants/%d/pontaj/confirma" % f["tenant_id"], {"an": gol.year, "luna": gol.month})
    assert st == 200, (st, r)
    luna, stare = _a_stat_pana_la(patron, f, gol)
    assert (data_ro(luna), stare) == (data_ro(gol), 423), (data_ro(luna), stare)    # refuz de perioadă, nu eroare de server
    pg.wait_for_function("() => { const f = [...document.querySelectorAll('.fereastra')].pop();"
                         " return !f.querySelector('#sp-prev') && !!f.querySelector('p.ecran-nota') && !f.querySelector('#sp-tabel'); }",
                         timeout=30000)
    pg.wait_for_timeout(300)
    nota = " ".join(pg.inner_text(_F + "p.ecran-nota").split())
    patron.captura("cu_tichete_10_2025_blocaj_motivat")
    try:
        common.cota("tichet_masa_plafon", gol)
        raise AssertionError("registrul nu mai are golul din %s" % data_ro(gol))   # anti-vacuu: golul chiar există
    except common.PerioadaIndisponibila as e:
        refuz = e
    assert refuz.nume == "tichet_masa_plafon" and refuz.gol and refuz.gol[0] < gol < refuz.gol[1], (refuz.nume, refuz.gol)   # ramura golului
    asteptat = " ".join(perioada.text_exceptie(refuz).split())
    assert nota.endswith(asteptat), (nota, asteptat)
    assert common.ETICHETE_COTE[refuz.nume] in nota and refuz.nume not in nota and perioada.ETICHETA.rstrip(":") not in nota, nota
    assert re.search(r"\d{4}-\d{2}-\d{2}", nota) is None, nota                                   # nicio dată ISO
    assert {data_ro(gol), data_ro(refuz.gol[0]), data_ro(refuz.gol[1])} <= set(re.findall(r"\b\d{2}\.\d{2}\.\d{4}\b", nota)), nota


# ── C149 — D177 / D107: clicul pe „+ adaugă” / „Regenerează” după scrierea unei sume nu se pierde ──────────────────────────────────
@pytest.fixture
def firma_cx2a_profit():
    for f in firma_noua():
        yield f


def test_def_c149_d177_adauga_dupa_suma_ramasa_merge_din_primul_clic(patron, firma_cx2a_profit):
    """C149 (D177). Pașii: Declarații -> D177, anul trecut -> Continuă -> „Suma maximă” 1.000 -> beneficiarul (sponsorizare, CUI 1590082,
    ASOCIATIA PROBA, IBAN, 500 lei, contract, acord „Da”) -> scrie „Rămasă de redirecționat” 500 și apasă DIRECT „+ adaugă”, o singură
    dată: beneficiarul apare în listă (un rând, cu „șterge”), iar totalurile spun suma rămasă. Înainte: ieșirea din câmp re-desena tot
    formularul, butonul apăsat era înlocuit între apăsare și ridicare, clicul se pierdea și câmpurile beneficiarului se goleau."""
    _a_profil_decl(patron, firma_cx2a_profit)
    pg = _pasul2(patron, firma_cx2a_profit, "d177", perioada_incheiata("anual").an)
    z = _A_Z
    pg.wait_for_selector(z + "#d177-smax", timeout=60000)
    pg.fill(z + "#d177-smax", "1000")
    pg.press(z + "#d177-smax", "Tab")
    pg.select_option(z + "#d177-tip", "1")
    pg.fill(z + "#d177-cui", "1590082")
    pg.fill(z + "#d177-den", "ASOCIATIA PROBA")
    pg.fill(z + "#d177-iban", IBAN)
    pg.fill(z + "#d177-suma", "500")
    pg.fill(z + "#d177-contract", "1/10.01.2025")
    pg.select_option(z + "#d177-acord", "true")
    pg.fill(z + "#d177-srest", "500")      # focusul rămâne în câmp: „change” vine abia la apăsarea butonului, ca la contabil
    pg.click(z + "#d177-add")              # O SINGURĂ apăsare
    pg.wait_for_timeout(800)
    patron.captura("d177_beneficiar_adaugat")
    assert pg.locator(z + "#dec-d177-form .dec-d177-del").count() == 1, patron.fereastra()[:2000]
    assert pg.input_value(z + "#d177-srest") == "500"


def test_def_c149_d107_regenereaza_dupa_suma_neindividualizata_merge_din_primul_clic(patron, firma_cx2a_profit):
    """C149 (D107). Pașii: Declarații -> D107, anul trecut -> Continuă -> un beneficiar (ASOCIATIA PROBA, CUI 1590082, adresa, 100 lei
    acordați) -> „+ adaugă” -> „Anexă — beneficiari neindividualizați” -> scrie „Suma dedusă neindividualizați” 50 și apasă DIRECT
    „Regenerează D107”, o singură dată: cererea de generare pleacă, cu suma scrisă (50) în datele declarației. Înainte: ieșirea din câmp
    re-desena formularul (anexa se închidea, butonul se muta), iar clicul pe „Regenerează” se pierdea."""
    _a_profil_decl(patron, firma_cx2a_profit)
    pg = _pasul2(patron, firma_cx2a_profit, "d107", perioada_incheiata("anual").an)
    z = _A_Z
    pg.wait_for_selector(z + "#d107-den", timeout=60000)
    pg.fill(z + "#d107-den", "ASOCIATIA PROBA")
    pg.fill(z + "#d107-cif", "1590082")
    pg.fill(z + "#d107-adr", "Str. Probei 9, Cluj-Napoca")
    pg.fill(z + "#d107-val1", "100")
    pg.click(z + "#d107-add")
    pg.wait_for_selector(z + "#dec-d107-form .dec-d107-del", timeout=20000)
    pg.locator(z + "#dec-d107-form details details > summary").first.click()   # anexa neindividualizaților (închisă implicit)
    pg.fill(z + "#d107-val3ni", "50")      # focusul rămâne în câmp
    with pg.expect_request(lambda r: r.method == "POST" and r.url.endswith("/declaratii/d107/valideaza"), timeout=20000) as rq:
        pg.click(z + "#d107-regen")        # O SINGURĂ apăsare
    patron.captura("d107_regenerata")
    manual = rq.value.post_data_json["manual"]
    assert (str(manual["val3_ni"]), [str(b["val1"]) for b in manual["beneficiari"]]) == ("50", ["100"]), manual


# ═══ Supervizor, Control fiscal, Registru jurnal: C130, C147, C131, C146, 491, 497 (+ generatorul
# dovezii C118, `fisier_amef_c118`).
#   C130 — lucrătorul Supervizorului e chemat de tura de 5 minute (crontab: `python3 -m core.firma_rezumat`, `core/firma_rezumat.py:1571-1586`).
#   C147 — rezultatul păstrat poartă versiunea regulilor (`core/supervizor_cache.py:66-76`, `citeste` :217, `de_recalculat` :241).
#   C131 — reconcilierea declarațiilor cu documentele, rând pe declarație, în Control fiscal (`static/js/ecrane/control_verdict.js:217-241`).
#   C146 — refuzul ștergerii notei unui Z trimite la „Raport Z: «Șterge raportul Z»” (`core/note_derivate.py:37`).
#   491  — o constatare urcă firma cel mult la galben (`core/common.py:317-320`, deficiența 220, decizia Costin 10.10.2026: „Roșu înseamnă
#          termen depășit.”); fără schimbare de cod în lotul 12.
#   497  — restanța = obligație cu termenul trecut, nedepusă, nemarcată, de la luna preluării (`core/control_fiscal_api.py:840-870`,
#          `separa_inainte_de_preluare` :160); fără schimbare de cod în lotul 12.
# Temei: N/A pentru toate șase — reguli de ecran / de calcul ale aplicației, nicio valoare fiscală nouă. La 497 termenul D112 vine din
#   răspunsul aplicației (`core/scadente.py`, cu temeiul citat acolo) și se compară numai cu ziua de azi.



_B_AZI = _dt.date.today()
_B_F = ".fereastra:last-of-type "
_B_RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _b_luna_inapoi(n, zi=None):
    """Prima zi a lunii de acum `n` luni (0 = luna curentă)."""
    d = (zi or _B_AZI).replace(day=1)
    for _ in range(n):
        d = (d - _dt.timedelta(days=1)).replace(day=1)
    return d


def _b_salariat(firma, **extra):
    """Un salariat (5.000 lei, normă întreagă, angajat 05.01.2026) pe ruta ecranului „+ Salariat nou” (`POST /tenants/{id}/salariati`)."""
    corp = {"nume": "Popescu", "prenume": "Ion", "cnp": _cnp("185010140123"), "data_angajare": "2026-01-05", "tip_norma": "intreaga",
            "ore_zi": 8, "salariu_brut": 5000, "persoane_intretinere": 0, "scutit_contrib_minim": False, "functie_baza": True,
            "cor": "331302", **extra}
    st, r = _api_cont(PATRON, "POST", "/tenants/%d/salariati" % firma["tenant_id"], corp)
    assert st == 200, (st, r)


def _b_luna_preluarii(patron, firma, luna):
    _ok(_api(patron, "POST", "/tenants/%d/firma-profil/date" % firma["tenant_id"], {"luna_preluare": luna.strftime("%Y-%m")}),
        "luna preluării")


def _b_control(patron, firma):
    """Fereastra firmei -> Control fiscal (cardul `#fa-control`)."""
    patron.firma(firma["nume"])
    _card(patron, "control", _B_F + ".cf-grup-titlu")
    patron.pg.wait_for_timeout(600)


def _b_detaliu(patron, firma):
    """Răspunsul rutei pe care o citește fereastra Control fiscal a firmei (`GET /control-fiscal/{id}`)."""
    return _ok(_api(patron, "GET", "/control-fiscal/%d" % firma["tenant_id"]), "Control fiscal")


# ── Supervizorul: tura lucrătorului și rândul firmei ─────────────────────────────────────────────────────────────────────────────
def _b_tura_lucratorului():
    """Tura de 5 minute, exact cum o pornește cronul (crontab: `cd <aplicație> && python3 -m core.firma_rezumat`), pe baza de TEST și cu
    codul probat (rădăcina copiei, mediul plasei). Pe instanța plasei cronul nu rulează; aici e pasul pe care îl face ceasul."""
    r = subprocess.run([sys.executable, "-m", "core.firma_rezumat"], cwd=_B_RAD, env=dict(os.environ), capture_output=True, text=True,
                       timeout=900)
    assert r.returncode == 0, (r.stdout + r.stderr)[-2000:]
    m = re.search(r"supervizor_invalidate=(\d+) supervizor_recalculate=(\d+)", r.stdout)
    assert m and "supervizor_eroare=" not in r.stdout, r.stdout[-2000:]
    return int(m.group(1)), int(m.group(2))


def _b_luna_supervizorului():
    """Luna evaluată de Supervizor (ultima lună încheiată, `control_fiscal_api.luna_confruntata`, aceeași în ecran și în lucrător)."""
    from core.common import azi_ro
    from core.control_fiscal_api import luna_confruntata
    azi = azi_ro()
    return luna_confruntata(azi.year, azi.month)


def _b_rand_supervizor(patron, firma):
    """Rândul firmei în răspunsul rutei ecranului Supervizor (`GET /supervizor`)."""
    r = _ok(_api(patron, "GET", "/supervizor"), "Supervizor")
    (rand,) = [f for f in r["firme"] if f["tenant_id"] == firma["tenant_id"]]
    return rand


def _b_ecran_supervizor(patron):
    """Cabinet -> cardul „Supervizor” -> ecranul lui, încărcat."""
    patron.acasa()
    patron.pg.click("button.cab-card:has([data-cheie='supervizor'])")
    patron.pg.wait_for_selector(_B_F + ".sv-antet", timeout=60000)


def _b_neverificate_cu(patron, firma, eroare):
    """Câte rânduri din blocul „Firme pe care verificarea nu a rulat” numesc firma ȘI poartă cauza `eroare` (textul vine din răspunsul
    serverului, nu din test)."""
    return patron.pg.locator(_B_F + ".sv-firma--neverif .cf-incr-rand", has_text=firma["nume"]).filter(has_text=eroare).count()


@pytest.fixture()
def firma_cx2b_sv():
    """Firmă nouă, cu Date firmă și vectorul fiscal (pe rutele ecranelor; scrierea în `firma_profil` ridică și contorul Supervizorului)."""
    for f in firma_noua():
        yield f


# ── C130 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_c130_tura_de_5_minute_calculeaza_supervizorul(patron, firma_cx2b_sv):
    """C130. Pașii: firmă nouă (Date firmă, vectorul fiscal) -> Supervizor (din cabinet): firma stă la „Firme pe care verificarea nu a rulat”,
    cu cauza „rezultatul nu a fost calculat încă …” -> trece tura de 5 minute a cronului (`python3 -m core.firma_rezumat`) -> Supervizor din
    nou: rândul acela nu mai e; rezultatul firmei e calculat („curent”), pe luna evaluată. Înainte: lucrătorul Supervizorului
    (`supervizor_cache.recalculeaza_lot`) nu-l chema nimeni, deci orice firmă rămânea „necalculată”."""
    from core import supervizor
    from core import supervizor_cache as sc
    f = firma_cx2b_sv
    pregateste_firma(patron, f, platitor=False)
    an, luna = _b_luna_supervizorului()
    inainte = _b_rand_supervizor(patron, f)
    assert inainte["prospetime"]["stare"] == sc.LIPSESTE, inainte["prospetime"]                    # anti-vacuu: încă necalculată
    assert inainte["neverificat"]["felul_neverificarii"] == supervizor.NECALCULAT, inainte["neverificat"]
    cauza = inainte["neverificat"]["eroare"]
    _b_ecran_supervizor(patron)
    assert _b_neverificate_cu(patron, f, cauza) == 1
    patron.captura("inainte_de_tura")
    _invalidate, recalculate = _b_tura_lucratorului()
    assert recalculate >= 1, (_invalidate, recalculate)
    dupa = _b_rand_supervizor(patron, f)
    assert dupa["prospetime"]["stare"] == sc.CURENT, dupa["prospetime"]
    assert (dupa["neverificat"] or {}).get("felul_neverificarii") != supervizor.NECALCULAT, dupa["neverificat"]
    assert sql("SELECT count(*) FROM public.supervizor_rezultat WHERE tenant_id = %s AND an = %s AND luna = %s",
               (f["tenant_id"], an, luna)) == [(1,)]
    _b_ecran_supervizor(patron)
    patron.captura("dupa_tura")
    assert _b_neverificate_cu(patron, f, cauza) == 0


# ── C147 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
#: cauza din rezultatul păstrat de codul DE DINAINTE de reparație (date de pornire): o regulă care atunci se oprea, reparată între timp
_B_CAUZA_VECHE = "regula Supervizorului din versiunea de dinainte de lotul 12 s-a oprit (rezultat păstrat, probă C147)"


def test_def_c147_rezultatul_calculat_cu_regulile_vechi_nu_ramane_curent(patron, firma_cx2b_sv):
    """C147. Pașii: firma are în Supervizor un rezultat păstrat de codul de dinainte de reparație (fără versiunea regulilor, cum îl scria
    `supervizor_cache.scrie_rezultat` până la lotul 12), calculat pe datele de acum ale firmei — nicio scriere de atunci: Supervizor (din
    cabinet) îl arată la „Firme pe care verificarea nu a rulat”, cu cauza lui veche, iar starea lui e „invalidat”, nu „curent” -> trece tura
    de 5 minute -> Supervizor: rezultatul e recalculat cu regulile de acum („curent”, cu versiunea regulilor), iar cauza veche nu mai apare.
    Înainte: rezultatul se invalida numai la o scriere de date, deci o reparație de regulă sau de text nu ajungea la o firmă fără scrieri
    noi, iar rezultatul vechi rămânea „curent” oricât."""
    import json
    from core import supervizor
    from core import supervizor_cache as sc
    f = firma_cx2b_sv
    pregateste_firma(patron, f, platitor=False)
    an, luna = _b_luna_supervizorului()
    ((v,),) = sql("SELECT versiune FROM public.supervizor_sursa WHERE tenant_id = %s", (f["tenant_id"],)) or [(None,)]
    assert v, "anti-vacuu: Date firmă a ridicat contorul Supervizorului"
    vechi = {"tenant_id": f["tenant_id"], "constatari": [], "de_confirmat": 0, "rezultat": supervizor.NEVERIFICAT,
             "neverificat": supervizor._neverificat({"nume": f["nume"], "schema": f["schema"]}, _B_CAUZA_VECHE, supervizor.EXCEPTIE)}
    # date-de-pornire: rezultatul pe care îl lăsa codul de dinainte de reparație (fără `versiune_reguli`), pe versiunea de acum a datelor
    sql("INSERT INTO public.supervizor_rezultat (tenant_id, an, luna, rezultat, versiune_sursa, calculat_la) VALUES (%s, %s, %s, %s::jsonb, "
        "%s, now()) ON CONFLICT (tenant_id, an, luna) DO UPDATE SET rezultat = EXCLUDED.rezultat, versiune_sursa = EXCLUDED.versiune_sursa",
        (f["tenant_id"], an, luna, json.dumps(vechi, ensure_ascii=False), v))   # upsert-ok: rândul derivat al firmei sintetice
    inainte = _b_rand_supervizor(patron, f)
    assert inainte["prospetime"]["versiune_sursa"] == inainte["prospetime"]["versiune_curenta"], inainte["prospetime"]   # nicio scriere
    assert inainte["prospetime"]["stare"] == sc.INVALIDAT, inainte["prospetime"]
    _b_ecran_supervizor(patron)
    assert _b_neverificate_cu(patron, f, _B_CAUZA_VECHE) == 1          # anti-vacuu: rezultatul vechi chiar e pe ecran
    # rezultatul vechi e ETICHETAT pe ecran (nu arată ca unul curent): marcajul stării lui, pe rândul firmei
    assert patron.pg.locator(".sv-firma--neverif .cf-incr-rand", has_text=f["nume"]).locator("[data-prospetime='invalidat']").count() == 1
    patron.captura("rezultat_vechi")
    _b_tura_lucratorului()
    dupa = _b_rand_supervizor(patron, f)
    assert dupa["prospetime"]["stare"] == sc.CURENT, dupa["prospetime"]
    assert (dupa["neverificat"] or {}).get("eroare") != _B_CAUZA_VECHE, dupa["neverificat"]
    ((ver,),) = sql("SELECT rezultat->>'versiune_reguli' FROM public.supervizor_rezultat WHERE tenant_id = %s AND an = %s AND luna = %s",
                    (f["tenant_id"], an, luna))
    assert ver == sc.VERSIUNE_REGULI, ver
    _b_ecran_supervizor(patron)
    patron.captura("recalculat")
    assert _b_neverificate_cu(patron, f, _B_CAUZA_VECHE) == 0
    # recalculat: nicio etichetă de rezultat vechi pe firma lui
    assert patron.pg.locator(".sv-firma, .sv-firma--neverif .cf-incr-rand", has_text=f["nume"]).locator("[data-prospetime='invalidat']").count() == 0


# ── C131 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _b_cu_nume(c):
    """Rândul reconcilierii cum îl scrie ecranul: numele declarației în față, dacă mesajul nu începe deja cu el (`cuNume`)."""
    m = c.get("mesaj") or ""
    return m if not c.get("eticheta") or m.startswith(c["eticheta"]) else "%s: %s" % (c["eticheta"], m)


def test_def_c131_fiecare_declaratie_datorata_are_randul_reconcilierii_cu_numele_ei(patron, firma_cx2b_sv):
    """C131. Pașii: firmă plătitoare de TVA lunar, cu o factură emisă și contată în luna trecută și un salariat (deci D300 și D112
    datorate pe luna trecută) -> fereastra firmei -> Control fiscal -> «Declarație vs contabilitate»: sub „Declarațiile recalculate din
    documente” stă câte un rând pentru FIECARE declarație reconciliată de server, în ordinea lui, fiecare începând cu numele declarației
    („D300 (decont TVA): …”, „D112 …: …”). Înainte: reconcilierea (D300 / D394 / D390 / D301 / D112 / D406 / D100 / D101 / D205) se
    calcula și nu se arăta deloc."""
    f = firma_cx2b_sv
    pregateste_firma(patron, f, platitor=True, regim_fiscal="micro")
    _b_salariat(f)
    _factura_validata(f, "E2EC131-1", _b_luna_inapoi(1).replace(day=10))
    d = _b_detaliu(patron, f)
    recon = (d.get("reconciliere_surse") or {}).get("constatari") or []
    etichete = [c.get("eticheta") or "" for c in recon]
    assert len(recon) >= 2 and len(set(etichete)) == len(etichete), etichete            # anti-vacuu: mai multe declarații, distincte
    assert {e.split()[0] for e in etichete} >= {"D300", "D112"}, etichete
    _b_control(patron, f)
    pg = patron.pg
    pg.wait_for_selector(_B_F + "#cf-incrucisat", timeout=60000)
    pg.locator(_B_F + "#cf-incrucisat").scroll_into_view_if_needed()
    patron.captura("reconcilierea_pe_declaratii")
    # rândurile reconcilierii sunt ultimele rânduri ale secțiunii (`reconBloc`, după constatările confruntării)
    capete = pg.eval_on_selector_all(_B_F + "#cf-incrucisat .cf-incr-rand .cf-incr-cap",
                                     "es => es.map(e => e.innerText.replace(/\\s+/g, ' ').trim())")
    assert capete[-len(recon):] == [" ".join(_b_cu_nume(c).split()) for c in recon], (capete, recon)


# ── C146 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture()
def firma_cx2b_z():
    for f in firma_noua():
        yield f


def test_def_c146_refuzul_stergerii_notei_z_trimite_la_raport_z(patron, firma_cx2b_z):
    """C146. Pașii: „Raport Z” -> „Import fișier AMEF” (Z nr. 1461, 231,00 lei): rândul Z-ului are „Șterge raportul Z” -> Registru jurnal ->
    nota Z-ului (ciornă): fără „Șterge” și fără „Editează”, iar sub ea motivul trimite la cardul care chiar există, „Raport Z”, și la butonul
    lui, «Șterge raportul Z»; ștergerea cerută din jurnal (aceeași rută ca butonul) e refuzată cu același text, iar nota rămâne. Înainte:
    „… — în Casa de marcat: raportul Z.” (nu există niciun ecran „Casa de marcat”)."""
    f = firma_cx2b_z
    pregateste_firma(patron, f)
    patron.firma(f["nume"])
    pg = patron.pg
    titlu_card = " ".join(pg.inner_text("#fa-raportz .firme-optiune-titlu").split())
    _card(patron, "raportz", "#z-salveaza")
    pg.set_input_files("#z-amef", {"name": "Z_AMEF_c146.xml", "mimeType": "application/xml", "buffer": _xml_amef("1461")})
    pg.wait_for_function("() => document.querySelector('#z-amef-msg').innerText.includes('Importat')", timeout=30000)
    ((zid,),) = sql('SELECT id FROM "%s".inregistrari WHERE numar = %%s' % f["schema"], ("Z-8000000001-1461",))
    pg.wait_for_selector("#zd-sterge-%d" % zid, timeout=20000)
    buton = " ".join(pg.inner_text("#zd-sterge-%d" % zid).split())
    assert buton and titlu_card, (buton, titlu_card)
    patron.firma(f["nume"])
    # [lotul 12, 617] rândul notei în tabelul de note; motivul notei derivate și „Editează” / „Șterge” stau în detaliul rândului, deschis
    _card(patron, "jurnal", "tbody.tn-nota[data-nota-id='%d']" % zid)
    rand = _deschide_rand(patron, _nota_jn(patron, zid))
    motiv = " ".join(rand.locator(".jn-derivata").inner_text().split())
    patron.captura("motivul_din_jurnal")
    # [lotul 13, 675] „Editează” / „Șterge” stau la locul lor, inactive, cu motivul: niciunul activ
    assert rand.locator('[data-del]:not([aria-disabled="true"])').count() == 0 and rand.locator('[data-edit]:not([aria-disabled="true"])').count() == 0
    # motivul e chiar textul pe care îl citește contabilul: se compară cu ce ARATĂ aplicația pe drumul numit (titlul cardului și eticheta
    # butonului, citite de pe ecran), nu cu o constantă din cod — o mutație a textului din cod ar trece o comparație cu codul însuși
    assert ("în %s:" % titlu_card) in motiv and ("«%s»" % buton) in motiv, (motiv, titlu_card, buton)
    r = _api(patron, "DELETE", "/tenants/%d/jurnal/%d" % (f["tenant_id"], zid))
    det = (r["json"] or {}).get("detail")
    mesaj = det if isinstance(det, str) else (det or {}).get("mesaj")
    assert 400 <= r["status"] < 500 and " ".join(str(mesaj).split()) == motiv, r
    assert sql('SELECT count(*) FROM "%s".inregistrari WHERE id = %%s' % f["schema"], (zid,)) == [(1,)]


# ── 491 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture()
def firma_cx2b_sal():
    """Firmă nouă cu un salariat; luna preluării = luna curentă, deci nicio declarație nu are termenul trecut (fără restanțe)."""
    f = _firma_noua("L12B491")
    try:
        yield f
    finally:
        _scoate_firmele_e2e(f["tenant_id"])


def _b_rosii_in_afara_restantelor(pg):
    """Elementele marcate ROȘU în fereastra Control fiscal a firmei, în afara grupului „Restanțe” și a antetului (aceeași citire ca
    `e2e_comanda_1010.test_def_220`)."""
    return pg.evaluate("""() => {
      const f = [...document.querySelectorAll('.fereastra')].pop();
      const titlu = [...f.querySelectorAll('.cf-grup-titlu')].find((t) => /^restanțe/i.test(t.innerText.trim()));
      const grup = titlu ? titlu.nextElementSibling : null;
      const rosu = (e) => /cf-rosu|pct-rosu|cf-termen-rosu/.test(e.className || '') || /#ff8a80|rosu-semafor/.test(e.getAttribute('style') || '');
      return [...f.querySelectorAll('*')].filter((e) => rosu(e) && e !== titlu && !(grup && grup.contains(e)) && !e.closest('.mig-intro'))
        .map((e) => (e.className || e.tagName) + ': ' + (e.parentElement.innerText || '').slice(0, 80)); }""")


def test_def_491_constatarea_salarii_nedeclarate_urca_firma_cel_mult_la_galben(patron, firma_cx2b_sal):
    """491 (explicație din cod, fără schimbare). „Alertele au urcat de la 3 la 4 după statul F5”: statul face D112 datorat, iar D112 față
    de rulajul validat al conturilor de salarii dă constatarea roșie „Salarii nedeclarate”; pe 06.10 o constatare roșie urca firma la roșu,
    deci în cifra „alerte”. De la 10.10 (220, „Roșu înseamnă termen depășit.”) o constatare urcă firma CEL MULT la galben. Pașii: firmă cu
    un salariat, statul lunii trecute necontat, nicio restanță (luna preluării = luna curentă) -> Control fiscal: constatarea D112 din
    «Declarație vs contabilitate» e roșie pe server, dar firma e „galben” (antet și listă), iar în fereastră nimic nu e roșu în afara
    restanțelor (care lipsesc)."""
    from core import uc_comun
    f = firma_cx2b_sal
    pregateste_firma(patron, f, platitor=False)
    _b_salariat(f)
    _b_luna_preluarii(patron, f, _b_luna_inapoi(0))
    d = _b_detaliu(patron, f)
    assert not d["lipsa"], d["lipsa"]                                                            # fără restanțe: roșul n-are de unde veni
    d112 = (d.get("verificari_contabile") or {}).get("d112_incrucisat") or {}
    assert d112.get("stare") == "rosu", d112                                                     # anti-vacuu: constatarea e roșie
    etichete_d112 = set(uc_comun.ETICHETE_INCRUCISAT["d112_incrucisat"])
    assert [c["stare"] for c in d["contabil"] if c.get("eticheta") in etichete_d112] == ["rosu"], d["contabil"]
    assert d["stare"] == "galben", d["stare"]
    _b_control(patron, f)
    pg = patron.pg
    pg.wait_for_selector(_B_F + "#cf-incrucisat", timeout=60000)
    patron.captura("detaliu_fara_rosu")
    assert _b_rosii_in_afara_restantelor(pg) == []
    randuri = [r for r in _lista_control(patron) if f["nume"] in r["nume"]]
    patron.captura("lista_control_fiscal")
    assert len(randuri) == 1 and not re.search(r"#ff8a80|rosu-semafor", randuri[0]["dot"] or ""), randuri


# ── 497 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _b_cheie(e):
    return "%s-%s-%s" % (e["tip"], e["an"], e["luna"])


def test_def_497_restanta_e_obligatia_cu_termenul_trecut_nedepusa_nemarcata_de_la_preluare(patron, firma_cx2b_sal):
    """497 (explicație din cod, fără schimbare). O restanță = o obligație din vectorul fiscal cu termenul trecut, nedepusă prin iConta.eu și
    nemarcată „depusă în afara iConta.eu”, pe o perioadă de la luna preluării încolo. Pașii: firmă cu un salariat (D112 datorat lunar),
    luna preluării = acum două luni -> Control fiscal: (1) fiecare rând din «Restanțe» are termenul trecut; D112 pe luna preluării (termen pe
    25 ale lunii trecute) e acolo; (2) D112 pe luna dinaintea preluării NU e la «Restanțe», ci în «Înainte de preluare în iConta.eu»; (3)
    pe rândul D112 al lunii preluării: „Marchează depusă în afara iConta.eu” -> data (termenul) -> „Salvează”: rândul iese din «Restanțe» și
    trece la «La zi», marcat (cu „Anulează marcarea”)."""
    from core.common import azi_ro
    f = firma_cx2b_sal
    pregateste_firma(patron, f, platitor=False)
    _b_salariat(f)
    prel = _b_luna_inapoi(2)
    _b_luna_preluarii(patron, f, prel)
    azi = azi_ro()
    d = _b_detaliu(patron, f)
    assert d["lipsa"] and all(_dt.date.fromisoformat(e["termen"]) < azi for e in d["lipsa"]), d["lipsa"]       # (1) termen trecut
    (rest,) = [e for e in d["lipsa"] if e["tip"].lower() == "d112" and (e["an"], e["luna"]) == (prel.year, prel.month)]
    inainte = _b_luna_inapoi(1, prel)
    assert [e for e in d["inainte_de_preluare"] if e["tip"].lower() == "d112" and (e["an"], e["luna"]) == (inainte.year, inainte.month)]
    assert not [e for e in d["lipsa"] if (e["an"], e.get("luna") or 12) < (prel.year, prel.month)], d["lipsa"]   # (2) nimic dinainte
    _b_control(patron, f)
    pg = patron.pg
    restante = _B_F + ".cf-grup-titlu.cf-rosu + .cf-decl "
    rand = restante + ".cf-decl-item[data-cheie='%s']" % _b_cheie(rest)
    pg.wait_for_selector(rand, timeout=30000)
    # [lotul 13, 674] rândurile grupului „Înainte de preluare” stau în șablonul ferestrei lui (deschisă de buton)
    assert pg.evaluate("(s) => !!document.querySelector('.fereastra:last-of-type template.cf-inainte-sablon')?.content.querySelector(s)",
                       ".cf-decl-item[data-cheie='d112-%d-%d']" % (inainte.year, inainte.month))
    assert pg.locator(restante + ".cf-decl-item[data-cheie='d112-%d-%d']" % (inainte.year, inainte.month)).count() == 0
    patron.captura("restantele")
    pg.click(rand + " .cf-extern-btn")
    pg.fill(rand + " .cf-extern-form input[type=date]", rest["termen"])
    pg.click(rand + " .cf-extern-salveaza")
    marcat = _B_F + ".cf-decl-item[data-cheie='%s'] .cf-extern-anuleaza" % _b_cheie(rest)
    pg.wait_for_selector(marcat, timeout=30000)
    patron.captura("marcata_depusa_in_afara")
    assert pg.locator(rand).count() == 0                                                                   # (3) nu mai e restanță
    assert pg.locator(_B_F + ".cf-grup-titlu.cf-verde + .cf-decl .cf-decl-item[data-cheie='%s']" % _b_cheie(rest)).count() == 1
    d2 = _b_detaliu(patron, f)
    assert _b_cheie(rest) not in {_b_cheie(e) for e in d2["lipsa"]}, d2["lipsa"]
    assert _b_cheie(rest) in {_b_cheie(e) for e in d2["confirmate"]}, d2["confirmate"]


# ── C118: fișierul dovezii pe copia F3 (`frontend_test/dovada/dovezi_lot12_cx2.json`) ─────────────────────────────────────────────────
def fisier_amef_c118(data_iso="2026-08-22"):
    """Raportul Z al casei 8000000001 pe o lună trecută (implicit 22.08.2026), cu un număr nou la fiecare rulare (copia poate fi rulată
    de mai multe ori: Z-ul e unic pe casă și număr). Aceeași formă ca `e2e_lot12_zsterge._xml_amef` (OPANAF 146/2018, secțiunea II.7)."""
    zi = _dt.date.fromisoformat(data_iso)
    nr = "%04d" % (int(time.time()) % 10000)
    idr = "8000000001%s1930%s%s" % (zi.strftime("%Y%m%d"), "%02d" % (int(time.time()) % 60), nr)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<msj idM="%s">\n  <rB idR="%s" nrAv="0" nrB="12" totB="231.00" totTva="40.09" '
            'totTaxe="0.00" totNet="0.00" monRef="RON">\n    <pl tipP="3" valPl="200.00" monPl="RON"/>\n'
            '    <pl tipP="1" valPl="31.00" monPl="RON"/>\n    <coteZ cota="21" valOp="231.00" tva="40.09"/>\n  </rB>\n</msj>\n'
            % (idr, idr)).encode("utf-8")


# ═══ NIR / stoc și ciorna „salariat nou”:
#   C126 — TVA-ul transportului facturat (datoria pe 401) nu mai rămâne pe 4428.01 după legarea facturii mărfii; NIR-ul vechi (4428.01 =
#          401) trece pe 4426 prin migrarea publicării. Temei: CF art.299 alin.(1) lit.a și OMFP 1802/2014, funcțiunea contului 4426
#          (citate în `core/stocuri.py:83-89`, `stocuri.cont_tva_transport`).
#   C138 — NIR „fără factură” cu transportul facturat de același furnizor pe factura mărfii: la validarea facturii aplicația propune NIR-ul
#          (costul complet = netul facturii). Temei: OMFP 1802/2014 pct.69 (`core/nir_legare.py:16`, `nir_legare.TEMEI`) și CF art.299
#          alin.(1) lit.a (`core/nir_legare.py:25`, nota facturii 4426 = 4428.01).
#   153  — NIR-urile „fără factură” scrise în forma veche (371 = 401, 4426 = 401) primesc nota de refacere (stornarea în roșu de pe 401 și
#          forma nouă 371 = 408, 4428.01 = 408). Temei: OMFP 1802/2014 pct.69 (`core/nir_legare.py:16`; docstringul
#          `core/migrare_retest_0810.py:8-12`, pct.4).
#   C108 — ciorna „salariat nou” e a utilizatorului care o scrie (cheia pe utilizator + firmă, în browser și pe server). N/A temei fiscal —
#          regulă de produs (CLAUDE.md §9; clasa deficienței 65).
# DATE DE PORNIRE fără ecran: NIR-urile pe ruta formularului „Salvează NIR” (`POST stocuri/nir`, ca 476); rândurile NIR-ului rescrise
# cum le scria codul de DINAINTE de reparație (C126 vechi, 153), apoi migrarea publicării chemată ca la publicare (ca `e2e_lot12_firme2`
# la C133 / C127). Furnizorul: DANTE INTERNATIONAL SA, CUI 14399840 (cifra de control verificată).



_C_DANTE = {"cui": "14399840", "nume": "DANTE INTERNATIONAL SA"}
_C_PATRON = "patron@prisma-cont.test"
_c_ecran_cont = contextlib.contextmanager(_ecran)


@pytest.fixture()
def firma_cx2c(patron):
    """O firmă NOUĂ pe test (SRL de comerț, plătitor de TVA, stoc cantitativ-valoric — `pregateste_firma`): fiecare test își are NIR-urile
    lui nelegate de la DANTE, ca propunerea NIR-ului (singurul cu costul facturii) să nu depindă de alt test."""
    for f in firma_noua():
        pregateste_firma(patron, f)
        try:
            yield f
        finally:
            sql("DELETE FROM public.ciorne_formular WHERE tenant_id = %s", (f["tenant_id"],))


def _c_suma(t):
    """Suma cum o scrie ecranul (`bani`: 1.234,56, cu minus) -> Decimal."""
    return Decimal(t.strip().replace(".", "").replace(",", ".").replace("−", "-"))


def _c_nir(patron, f, numar, cantitate, pret, transport=0, cont_transport=None):
    """NIR „fără factură” (factura furnizorului nesosită), pe ruta formularului „Salvează NIR”; întoarce (id, notele)."""
    corp = {"numar": numar, "data": AZI.isoformat(), "furnizor": _C_DANTE["nume"], "cui": _C_DANTE["cui"], "factura_sosita": False,
            "linii": [{"denumire": "Marfa %s" % numar, "articol_nou": True, "cantitate": cantitate, "pret_achizitie": pret, "cota_tva": 21}]}
    if transport:
        corp.update({"transport": transport, "cota_tva_transport": 21, "cont_transport": cont_transport})
    r = _ok(_api(patron, "POST", "/tenants/%d/stocuri/nir" % f["tenant_id"], corp), "NIR")
    assert "eroare" not in r, r
    nid, ids = sql('SELECT id, inregistrari_ids FROM "%s".nir WHERE numar = %%s' % f["schema"], (numar,))[0]
    return nid, [int(i) for i in ids]


def _c_note_nir_pe_ecran(patron, f, nir_id):
    """Stocuri -> „Deschide NIR-ul: articolele și notele” -> tabelul „Notele NIR-ului”: [(debit, credit, suma)], citite din celule."""
    patron.firma(f["nume"])
    pg = patron.pg
    _card(patron, "stocuri", ".nir-deschide")
    pg.click(".nir-deschide[data-nir='%d']" % nir_id)
    pg.wait_for_selector("#nir-detaliu-linii", timeout=25000)
    randuri = pg.eval_on_selector_all("#nir-detaliu-linii ~ table.fd-tabel tbody tr",
                                      "rs => rs.map(r => [...r.cells].map(c => c.innerText.trim()))")
    return [(r[1], r[2], _c_suma(r[3])) for r in randuri if len(r) >= 4]


def _c_sold(randuri, cont):
    """Debit − credit pe `cont` (sintetic sau analitic, exact) peste rândurile (debit, credit, suma)."""
    return sum((s for d, _c, s in randuri if d == cont), Decimal(0)) - sum((s for _d, c, s in randuri if c == cont), Decimal(0))


def _c_factura_marfii(patron, f, numar, linii):
    """Facturi -> „Facturi primite” -> „Importă XML UBL” (factura DANTE: `linii` = [(denumire, cantitate, preț)], 21%) -> factura -> contul
    371 -> „Validează” -> confirmarea -> caseta „NIR-ul acestei livrări”. Întoarce (valoarea aleasă în `#nir-legat`, opțiunile)."""
    pg = patron.pg
    cifre = "".join(c for c in sql('SELECT cui FROM "%s".firma_profil WHERE id = 1' % f["schema"])[0][0] if c.isdigit())
    xml = _ubl(numar, AZI, _C_DANTE, f["nume"], cifre, linii)
    patron.firma(f["nume"])
    _card(patron, "facturi", "#fac-primite")
    pg.click("#fac-primite")
    pg.wait_for_selector("#fp-xml", state="attached", timeout=20000)
    pg.set_input_files("#fp-xml", {"name": "%s.xml" % numar, "mimeType": "text/xml", "buffer": xml.encode("utf-8")})
    pg.wait_for_selector(".fac-primita-btn:has-text('%s')" % numar, timeout=40000)
    pg.locator(".fac-primita-btn", has_text=numar).first.click()
    pg.wait_for_selector("#pr-cont", timeout=20000)
    pg.fill("#pr-cont", "371")
    pg.click("#pr-valideaza")
    pg.click("#ca-ok")
    pg.wait_for_selector(".fereastra:last-of-type #nir-legat", timeout=30000)
    ales = pg.eval_on_selector(".fereastra:last-of-type #nir-legat", "s => s.value")
    opt = pg.eval_on_selector_all(".fereastra:last-of-type #nir-legat option", "os => os.map(o => o.value)")
    return ales, opt


def _c_leaga(patron):
    """„Leagă de NIR-ul ales” -> (eventualele confirmări) -> „Validată.”"""
    pg = patron.pg
    pg.click(".fereastra:last-of-type #nir-leaga")
    pg.wait_for_function("() => { const o = document.querySelector('#caseta-atentie-activa #ca-ok'); if (o) { o.click(); return false; }"
                         " return (document.querySelector('#pr-zona') || {innerText: ''}).innerText.includes('Validată'); }", timeout=60000)


def _c_note_facturii(f, numar):
    fid = sql('SELECT id FROM "%s".facturi WHERE numar = %%s AND directie = \'primita\'' % f["schema"], (numar,))[0][0]
    return fid, [(d, c, Decimal(str(s))) for d, c, s in sql(
        'SELECT l.cont_debit, l.cont_credit, l.suma FROM "%s".inregistrari i JOIN "%s".inregistrari_linii l ON l.inregistrare_id = i.id '
        "WHERE i.factura_id = %%s ORDER BY l.id" % (f["schema"], f["schema"]), (fid,))]


# ── C126 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_c126_tva_transportului_facturat_nu_ramane_pe_4428_dupa_legarea_facturii(patron, firma_cx2c):
    """C126. Pașii: NIR fără factura mărfii de la DANTE, 10 × 50 lei, transport 100 lei cu factura transportatorului (cont 401), TVA
    transport 21% -> Stocuri -> NIR-ul: TVA-ul transportului e 4426 = 401 · 21,00 -> vine factura mărfii (XML: 10 × 50, TVA 105) ->
    „Validează” pe 371: NIR-ul propus -> „Leagă”: pe notele NIR-ului (citite pe ecran) și ale facturii, 4428.01 se închide (sold 0), iar 4426 are tot TVA-ul
    deductibil, 105 + 21 = 126,00. Înainte: transportul ieșea 4428.01 = 401, iar legarea muta numai 4428.01 = 408 — rămâneau 21,00 pe
    4428.01."""
    f = firma_cx2c
    nr = "C126-%d" % (time.time() % 100000)
    nir_id, _note = _c_nir(patron, f, nr, 10, 50, transport=100, cont_transport="401")
    _c_note_nir_pe_ecran(patron, f, nir_id)       # rândul 4426 = 401 al transportului îl păzește 476 (e2e_lot12_firme1); aici, legarea
    patron.captura("notele_nir")
    ales, _opt = _c_factura_marfii(patron, f, "F" + nr, [("Marfa %s" % nr, 10, Decimal("50"))])
    assert ales == str(nir_id), (ales, _opt)                        # costul NIR-ului fără accesorii (500) = netul facturii
    patron.captura("nir_propus")
    _c_leaga(patron)
    patron.captura("legata")
    fid, pe_factura = _c_note_facturii(f, "F" + nr)
    assert sql('SELECT factura_id FROM "%s".nir WHERE id = %%s' % f["schema"], (nir_id,)) == [(fid,)]
    toate = _c_note_nir_pe_ecran(patron, f, nir_id) + pe_factura
    patron.captura("nir_dupa_legare")
    assert _c_sold(toate, "4428.01") == 0, toate                    # TVA-ul neexigibil se închide cu factura (nimic rămas pe 4428.01)
    assert sum((s for d, _c, s in toate if d == "4426"), Decimal(0)) == Decimal("126.00"), toate   # 105 (marfa) + 21 (transportul)


def test_def_c126_vechi_nir_cu_tva_transportului_pe_4428_trece_pe_4426(patron, firma_cx2c):
    """C126, NIR-ul de dinainte de reparație: TVA-ul transportului facturat scris 4428.01 = 401 pe nota CIORNĂ a NIR-ului (cum îl scria
    codul de dinainte de 476). Pașii: migrarea publicării (`migrare_nir_tva_transport.aplica`) -> Stocuri -> NIR-ul: rândul e 4426 = 401 ·
    21,00, niciun 4428.01 = 401 -> factura mărfii -> „Leagă”: 4428.01 se închide (sold 0)."""
    from core import migrare_nir_tva_transport as mig
    f, s = firma_cx2c, firma_cx2c["schema"]
    nr = "C126V-%d" % (time.time() % 100000)
    nir_id, note = _c_nir(patron, f, nr, 10, 40, transport=50, cont_transport="401")
    # date-de-pornire: rândul TVA-ului transportului cum îl scria codul de dinainte de 476 (contul TVA-ului mărfii, 4428.01 = 401)
    sql('UPDATE "%s".inregistrari_linii SET cont_debit = \'4428.01\' WHERE inregistrare_id = ANY(%%s) AND cont_debit = \'4426\' '
        "AND cont_credit = '401'" % s, (note,))
    with _db().get_conn() as c:
        rez = mig.aplica(c, s)
        c.commit()
    assert rez["ciorne"] == 1 and not rez["blocate"], rez
    pe_nir = _c_note_nir_pe_ecran(patron, f, nir_id)
    patron.captura("vechi_nir_dupa_migrare")
    assert ("4426", "401", Decimal("10.50")) in pe_nir and not [x for x in pe_nir if x[:2] == ("4428.01", "401")], pe_nir
    ales, _opt = _c_factura_marfii(patron, f, "F" + nr, [("Marfa %s" % nr, 10, Decimal("40"))])
    assert ales == str(nir_id), (ales, _opt)
    _c_leaga(patron)
    _fid, pe_factura = _c_note_facturii(f, "F" + nr)
    toate = pe_nir + pe_factura
    patron.captura("vechi_legata")
    assert _c_sold(toate, "4428.01") == 0, toate                    # 84 (marfa) intră și iese; transportul nu mai e acolo


# ── C138 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_c138_nir_cu_transportul_pe_factura_marfii_e_propus_la_validare(patron, firma_cx2c):
    """C138. Pașii: NIR fără factură de la DANTE, 10 × 50 lei, transport 100 lei pe aceeași factură a furnizorului (contul transportului
    gol = al furnizorului mărfii, 408), TVA transport 21% -> vine factura DANTE (XML: marfa 10 × 50 + transport 100, net 600, TVA 126) ->
    „Validează” pe 371: caseta „NIR-ul acestei livrări” are NIR-ul ales din date („— propus”: costul complet 600 = netul facturii) ->
    „Leagă”: nota facturii 408 = 401 · 726,00 și 4426 = 4428.01 · 126,00, fără 371 = 401. Înainte: „Niciun NIR nu are costul facturii”
    (netul comparat numai cu costul fără transport, 500), nimic ales."""
    f = firma_cx2c
    nr = "C138-%d" % (time.time() % 100000)
    nir_id, _note = _c_nir(patron, f, nr, 10, 50, transport=100)
    ales, opt = _c_factura_marfii(patron, f, "F" + nr, [("Marfa %s" % nr, 10, Decimal("50")), ("Transport marfa", 1, Decimal("100"))])
    patron.captura("nir_propus")
    assert ales == str(nir_id) and "" not in opt, (ales, opt)      # propunerea: fără „— alege —”, NIR-ul livrării ales
    _c_leaga(patron)
    patron.captura("legata")
    _fid, pe_factura = _c_note_facturii(f, "F" + nr)
    # nir_legare.note_factura_legata: 408 = 401 (costul 600 + TVA-ul din NIR 126), 4426 = 4428.01 (CF art.299 alin.(1) lit.a)
    assert sorted(pe_factura) == [("408", "401", Decimal("726.00")), ("4426", "4428.01", Decimal("126.00"))], pe_factura


# ── 153 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_153_nir_fara_factura_in_forma_veche_se_reface_pe_408_si_4428(patron, firma_cx2c):
    """153 (F1, NIR 1 și 2 rămase pe 401/4426). Pașii: NIR fără factură de la DANTE, 10 × 50 lei: azi notele lui sunt 371 = 408 · 500,00 și
    4428.01 = 408 · 105,00 (forma nouă) -> același NIR cu notele în forma de DINAINTE de 08.10 (371 = 401, 4426 = 401) -> migrarea
    publicării (`migrare_retest_0810.refa_nir_forma_veche`) -> Stocuri -> NIR-ul: nota de refacere stornează în roșu 401 / 4426 și scrie
    forma nouă, deci pe NIR rămân 371 = 408 · 500,00 și 4428.01 = 408 · 105,00, iar 401 și 4426 se anulează (sold 0)."""
    from core import migrare_retest_0810 as mig
    f, s = firma_cx2c, firma_cx2c["schema"]
    nr = "N153-%d" % (time.time() % 100000)
    nir_id, note = _c_nir(patron, f, nr, 10, 50)
    acum = _c_note_nir_pe_ecran(patron, f, nir_id)
    patron.captura("forma_noua")
    assert sorted(acum) == [("371", "408", Decimal("500.00")), ("4428.01", "408", Decimal("105.00"))], acum
    # date-de-pornire: notele NIR-ului rescrise în forma de dinainte de 08.10 (371 = 401, 4426 = 401), ca NIR 1 / 2 ale F1
    sql('UPDATE "%s".inregistrari_linii SET cont_credit = \'401\' WHERE inregistrare_id = ANY(%%s) AND cont_credit = \'408\'' % s, (note,))
    # date-de-pornire: TVA-ul aceluiași NIR vechi, deductibil (4426), cum îl scria forma de dinainte de 08.10
    sql('UPDATE "%s".inregistrari_linii SET cont_debit = \'4426\' WHERE inregistrare_id = ANY(%%s) AND cont_debit = \'4428.01\'' % s, (note,))
    with _db().get_conn() as c:
        refaceri = mig.refa_nir_forma_veche(c, s)
        c.commit()
    assert [r[0] for r in refaceri if r[2]] == [nir_id], refaceri
    dupa = _c_note_nir_pe_ecran(patron, f, nir_id)
    patron.captura("vechi_refacut")
    assert len(dupa) == 6, dupa                                     # 2 rânduri vechi + nota de refacere (4 rânduri)
    assert (_c_sold(dupa, "401"), _c_sold(dupa, "4426")) == (0, 0), dupa
    assert (_c_sold(dupa, "408"), _c_sold(dupa, "4428.01"), _c_sold(dupa, "371")) == (Decimal("-605.00"), Decimal("105.00"),
                                                                                       Decimal("500.00")), dupa


# ── C108 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _c_e_ciorna(r, metoda):
    """Cererea ciornei „salariat nou” (`/tenants/{id}/ciorne-formular/salariat_nou`), cu metoda dată."""
    return r.request.method == metoda and r.url.split("?")[0].endswith("/ciorne-formular/salariat_nou")


def _c_salariat_nou(e, f):
    e.firma(f["nume"])
    _card(e, "salariati", "#sp-salariat-nou")
    with e.pg.expect_response(lambda r: _c_e_ciorna(r, "GET"), timeout=20000) as rr:
        e.pg.click("#sp-salariat-nou")
    e.pg.wait_for_selector("#sn-salveaza", timeout=20000)
    e.pg.wait_for_timeout(600)       # ciorna de pe server reface formularul după răspuns (`ciornaFormular().gata`)
    return rr.value.json()


@contextlib.contextmanager
def _c_pagina(ctx, email, nume):
    """O pagină în contextul dat (același browser: aceeași stocare locală), cu sesiunea contului `email` — cu verificările plasei."""
    pg = ctx.new_page()
    pg.add_init_script(sesiune(email))
    e = Ecran(pg, nume)
    yield e
    assert not e.erori, "erori JavaScript pe ecran: %s" % e.erori[:3]
    assert not e.cereri_rele, "cereri cu răspuns 5xx: %s" % e.cereri_rele[:3]
    assert not e.deschideri_singure, "[325] s-a deschis ceva fără clicul omului: %s" % e.deschideri_singure[:5]


def test_def_c108_ciorna_netrimisa_a_patronului_nu_apare_la_asistent_in_acelasi_browser(browser, request, firma_cx2c):
    """C108. Pașii: în ACELAȘI browser, contabilul-șef începe „+ Salariat nou” (numele „PATRON C108”), iar ciorna lui rămâne netrimisă
    (serverul nu se poate atinge: copia stă în browser) -> asistentul firmei, în alt tab al aceluiași browser -> Salariați -> „+ Salariat
    nou”: formularul e gol (numele nescris); copia contabilului-șef rămâne în browser, pe cheia lui. Înainte: cheia ciornei era numai pe
    firmă, deci asistentul primea formularul contabilului-șef."""
    f = firma_cx2c
    uid_patron = sql("SELECT id FROM public.users WHERE email = %s", (_C_PATRON,))[0][0]
    with cont_asistent(firme=(f["tenant_id"],), eticheta="c108") as asist:
        ctx = browser.new_context(viewport={"width": LAT, "height": INALT})
        ctx.add_init_script(GARDA_DESCHIDERI)
        try:
            with _c_pagina(ctx, _C_PATRON, request.node.name) as p:
                # serverul nu primește ciorna (o rețea căzută): copia rămâne în browser, netrimisă
                p.pg.route("**/ciorne-formular/salariat_nou", lambda r: r.abort() if r.request.method == "PUT" else r.continue_())
                _c_salariat_nou(p, f)
                p.pg.fill("#sn-nume", "PATRON C108")
                p.pg.dispatch_event("#sn-nume", "input")
                p.pg.wait_for_timeout(1500)
                p.captura("patron_netrimisa")
            with _c_pagina(ctx, asist["email"], request.node.name + "_asistent") as a:
                raspuns = _c_salariat_nou(a, f)
                a.captura("asistent_formular_gol")
                assert a.pg.input_value("#sn-nume") == "", a.pg.input_value("#sn-nume")   # ciorna altuia nu ajunge la el
                assert raspuns == {"ciorna": None}, raspuns
                copii = a.pg.evaluate("() => Object.keys(localStorage).filter(k => k.startsWith('iconta_ciorna_salariat:'))"
                                      ".map(k => [k, JSON.parse(localStorage.getItem(k)).campuri['sn-nume'] || ''])")
                assert ["iconta_ciorna_salariat:%d:u%d" % (f["tenant_id"], uid_patron), "PATRON C108"] in copii, copii
                assert not [k for k, v in copii if k.endswith(":u%d" % asist["id"]) and v], copii
        finally:
            ctx.close()
            sql("DELETE FROM public.ciorne_formular WHERE tenant_id = %s", (f["tenant_id"],))


def test_def_c108_ciorna_de_pe_server_e_a_utilizatorului_care_a_scris_o(patron, browser, request, firma_cx2c):
    """C108, pe server. Pașii: contabilul-șef începe „+ Salariat nou” (numele „SERVER C108”) -> ciorna lui ajunge pe server -> asistentul
    firmei, pe alt calculator -> Salariați -> „+ Salariat nou”: serverul nu-i dă nicio ciornă, formularul e gol; ciorna contabilului-șef
    rămâne a lui."""
    f = firma_cx2c
    uid_patron = sql("SELECT id FROM public.users WHERE email = %s", (_C_PATRON,))[0][0]
    pg = patron.pg
    _c_salariat_nou(patron, f)
    with pg.expect_response(lambda r: _c_e_ciorna(r, "PUT"), timeout=15000):
        pg.fill("#sn-nume", "SERVER C108")
        pg.dispatch_event("#sn-nume", "input")
    pg.wait_for_timeout(800)
    patron.captura("patron_pe_server")
    pe_server = sql("SELECT user_id, continut FROM public.ciorne_formular WHERE tenant_id = %s AND formular = 'salariat_nou'", (f["tenant_id"],))
    assert [(u, c["campuri"]["sn-nume"]) for u, c in pe_server] == [(uid_patron, "SERVER C108")], pe_server
    with cont_asistent(firme=(f["tenant_id"],), eticheta="c108s") as asist:
        with _c_ecran_cont(browser, request, asist["email"]) as a:
            raspuns = _c_salariat_nou(a, f)
            a.captura("asistent_alt_calculator")
            assert raspuns == {"ciorna": None}, raspuns
            assert a.pg.input_value("#sn-nume") == "", a.pg.input_value("#sn-nume")
        assert sql("SELECT user_id FROM public.ciorne_formular WHERE tenant_id = %s AND formular = 'salariat_nou'", (f["tenant_id"],)) == \
            [(uid_patron,)]
        sql("DELETE FROM public.ciorne_formular WHERE tenant_id = %s", (f["tenant_id"],))
