# -*- coding: utf-8 -*-
"""Lotul 11 — subagentul S9: C89, C90, C91 (găsite de Code la 453, DEFICIENTE.md). Pașii contabilului pe aplicația din index, pe baza
de TEST: statul lunii trecute (ecranul Salariați), „Compoziția netului”, fluturașul, Declarații -> D112 -> DUKIntegrator -> „Vezi XML-ul
generat”.

Date de pornire: fiecare test își face firma sintetică (`_firma_noua`, drumul `provision_tenant` al aplicației) și salariatul pe ruta
salariaților (`POST /tenants/{id}/salariati`), ca fixtura `firma_sal`. Certificatele de concediu medical (C89, C92) se introduc pe ecranul
„Concediu medical” (din rândul statului), cu formularul lui. Nicio inserare directă în bază.

CNP-urile au cifra de control calculată cu algoritmul din CLAUDE.md (`e2e_bloc_b._cnp`)."""
import re

import pytest

from conftest import _scoate_firmele_e2e, sql
from e2e_bloc_b import _cnp
from e2e_bloc_d import LUNA_TRECUTA, PATRON, _api, _firma_noua, _genereaza
from e2e_bloc_d import _stat as _stat_luna
from e2e_lot11_a453 import _pdf_fluturas
from e2e_lot13_sal_ajutor import alege

_F = ".fereastra:last-of-type "


def _firma_cu_salariat(sufix, **salariat):
    """Firmă sintetică + un salariat adăugat pe ruta salariaților (cum îl adaugă ecranul „+ Salariat nou”)."""
    f = _firma_noua(sufix)
    corp = {"nume": "Popescu", "prenume": "Ion", "cnp": _cnp("185010140123"), "data_angajare": "2026-01-05", "tip_norma": "intreaga",
            "ore_zi": 8, "salariu_brut": 5000, "persoane_intretinere": 0, "scutit_contrib_minim": False, "functie_baza": True,
            "cor": "331302", **salariat}
    st, r = _api(PATRON, "POST", "/tenants/%d/salariati" % f["tenant_id"], corp)
    assert st == 200, (st, r)
    f["salariat_id"] = r.get("id") or r.get("salariat_id")
    st, r = _api(PATRON, "POST", "/tenants/%d/firma-profil/date" % f["tenant_id"], {"luna_preluare": LUNA_TRECUTA.strftime("%Y-%m")})
    assert st == 200 and r.get("ok") is not False, (st, r)
    return f


@pytest.fixture
def firma_c91():
    f = _firma_cu_salariat("S9D", tip_norma="partiala", ore_zi=4, salariu_brut=1000, persoane_intretinere=4)
    try:
        yield f
    finally:
        _scoate_firmele_e2e(f["tenant_id"])


@pytest.fixture
def firma_c90():
    f = _firma_cu_salariat("S9F", functie_baza=False, persoane_intretinere=2)
    try:
        yield f
    finally:
        _scoate_firmele_e2e(f["tenant_id"])


@pytest.fixture
def firma_c93():
    """Salariatul la salariul minim al lunii trecute (normă întreagă, funcția de bază): primește suma netaxabilă (OUG 89/2025 art.III)."""
    from core.common import cota, salariu_minim_luna
    sm = int(salariu_minim_luna(LUNA_TRECUTA)[0])
    fac = int(cota("facilitate_salariu_minim", LUNA_TRECUTA)[0])
    f = _firma_cu_salariat("S9T", salariu_brut=sm)
    f["sm"], f["fac"] = sm, fac
    try:
        yield f
    finally:
        _scoate_firmele_e2e(f["tenant_id"])


@pytest.fixture
def firma_c89():
    f = _firma_cu_salariat("S9C")
    try:
        yield f
    finally:
        _scoate_firmele_e2e(f["tenant_id"])


def _salariat_deschis(patron):
    """[lotul 13, 677] fereastra salariatului (deschisă din rândul statului, dacă nu e deja în față)."""
    from e2e_lot13_sal_ajutor import deschide_salariat
    if not patron.pg.locator(_F + "#ss-butoane").count():
        deschide_salariat(patron)


def _concedii(patron):
    """Fereastra salariatului -> „Concediu medical” (fereastra certificatelor)."""
    from e2e_lot13_sal_ajutor import buton
    _salariat_deschis(patron)
    buton(patron, "cm")


def _compozitie(patron):
    """[lotul 13, 677] Compoziția netului din fereastra salariatului: {etichetă: (valoare, net)}, citită din rândurile celor trei coloane."""
    from e2e_lot13_sal_ajutor import coloane
    _salariat_deschis(patron)
    return coloane(patron)


_NS = "{mfp:anaf:dgti:declaratie_unica:declaratie:v7}"
_XML_GENERAT = _F + "details.dec-xml:has(summary:text('Vezi XML-ul generat'))"   # forma din e2e_bloc_e (D406)


def _d112_xml(patron, firma):
    """Declarații -> D112 pe luna trecută -> pasul 2: „fără erori” la DUKIntegrator -> „Vezi XML-ul generat” -> XML-ul PARSAT
    (ElementTree): {"_angajator": {secțiune: [atribute]}, cnpAsig: {secțiune: [atribute]}}. Pe pasul 2 sunt două `details.dec-xml`
    („Din ce e făcută declarația” e primul): se deschide cel cu titlul „Vezi XML-ul generat”, nu primul găsit."""
    import xml.etree.ElementTree as ET
    pg = patron.pg
    _genereaza(patron, firma, "d112", LUNA_TRECUTA.year, LUNA_TRECUTA.month)
    ok = pg.locator(_F + ".dec-ok")
    assert ok.count() == 1 and "fără erori" in ok.inner_text(), patron.fereastra()[:3000]
    pg.click(_XML_GENERAT + " summary", timeout=20000)
    xml = pg.locator(_XML_GENERAT + " pre.dec-xml-pre").text_content()
    patron.captura("d112_xml")
    rad = ET.fromstring(xml.encode("utf-8"))

    def _sectiuni(el):
        out = {}
        for c in el:
            out.setdefault(c.tag.replace(_NS, ""), []).append(dict(c.attrib))
        return out
    st = {"_angajator": _sectiuni(rad.find(_NS + "angajator"))}
    for a in rad.findall(_NS + "asigurat"):
        st[a.get("cnpAsig")] = _sectiuni(a)
    return st


def _un(sectiuni, nume):
    """Secțiunea `nume`, care trebuie să apară exact o dată (lipsa ei pică, nu trece)."""
    lista = sectiuni.get(nume, [])
    assert len(lista) == 1, (nume, sorted(sectiuni), lista)
    return lista[0]


def _singurul(st):
    """Secțiunile singurului asigurat al declarației (firma de probă are un salariat)."""
    cnp = [k for k in st if k != "_angajator"]
    assert len(cnp) == 1, cnp
    return st[cnp[0]]


def _bani_net(patron, eticheta):
    """Netul de pe rândul `eticheta` al compoziției (rândul indemnizației CM: brut și net pe același rând)."""
    from decimal import Decimal
    return Decimal(str(_compozitie(patron)[eticheta][1]))


def _int(el, *atribute):
    return [int(el[a]) for a in atribute]


def _bani(text):
    """„1.234,56” -> Decimal("1234.56")."""
    from decimal import Decimal
    return Decimal(text.replace(".", "").replace(",", "."))


def _randuri_compozitie(comp):
    """Rândurile compoziției netului, ca {etichetă: sumă}: din fereastra salariatului (dict, `_compozitie`) sau dintr-un text
    („etichetă<TAB>sumă lei” pe rând)."""
    from decimal import Decimal
    if isinstance(comp, dict):
        return {k: Decimal(str(v[0])) for k, v in comp.items() if v[0] is not None}
    out = {}
    for linie in comp.splitlines():
        m = re.fullmatch(r"\s*(.+?)\t(-?[\d.]+,\d\d) lei\s*", linie)
        if m:
            out[m.group(1).strip()] = _bani(m.group(2))
    return out


# ── C91 — deducerea personală în limita venitului net ───────────────────────────────────────────────────────────────────────────
_ETICHETA_DEDUCERE = "în calculul impozitului, scade baza (nu se reține): deducere personală"   # stat_plata_api.compozitie_fluturas


def test_def_c91_deducerea_plafonata_la_venitul_net(patron, firma_c91):
    """C91. Pașii: salariat cu normă parțială (4 ore), 1.000 lei brut, 4 persoane în întreținere -> Salariați -> statul lunii trecute ->
    „Compoziția netului”: „… deducere personală 650,00 lei” = venitul net 1.000 − 250 (CAS) − 100 (CASS), nu 1.946,00 (45% din salariul
    minim, calculat întreg) -> „Fluturaș”: aceeași deducere, 650,00 -> Declarații -> D112 pe luna trecută: „fără erori” la DUKIntegrator,
    iar XML-ul declară deducerea acordată 650 (E3_12 / E3_121 / E1_4 / E1_41), baza 0 și impozitul 0 (E3_14 / E3_15). Înainte: 1.946 pe
    ecran, pe fluturaș și în D112, cu baza tot 0.
    Temeiul: CF art.77 alin.(2) — „se acordă în limita venitului impozabil lunar realizat”; OPANAF 605/2026 anexa 1.2, D112 E.1 rândul 4."""
    _stat_luna(patron, firma_c91, luni_inapoi=1)
    comp = _compozitie(patron)
    patron.captura("compozitia_netului")
    # [deficiența 411] rândul deducerii stă sub impozit: „în calculul impozitului, scade baza (nu se reține): deducere personală”
    r = _randuri_compozitie(comp)
    assert r.get(_ETICHETA_DEDUCERE) == _bani("650,00"), (r, comp)
    text = _pdf_fluturas(patron)
    patron.captura("fluturas")
    assert re.search(r"deducere personală\s+650,00\b", text), text[:1500]   # fluturașul tipărește aceleași rânduri (compozitie_fluturas)
    a = _singurul(_d112_xml(patron, firma_c91))
    assert _int(_un(a, "asiguratE3"), "E3_12", "E3_121", "E3_122", "E3_14", "E3_15") == [650, 650, 0, 0, 0], a
    assert _int(_un(a, "asiguratE1"), "E1_4", "E1_41", "E1_6", "E1_7") == [650, 650, 0, 0], a


# ── C90 — salariatul fără funcție de bază: E3_3 = 2, secțiunea E2 ───────────────────────────────────────────────────────────────
def test_def_c90_fara_functie_de_baza_declarat_cu_e3_3_doi(patron, firma_c90):
    """C90. Pașii: salariat cu 5.000 lei brut, „Funcția de bază la acest angajator: Nu”, 2 persoane în întreținere -> Salariați -> statul
    lunii trecute: impozit 325,00 (10% × (5.000 − 1.750), fără deducere — CF art.77 alin.(1), art.78 alin.(2) lit.b) -> Declarații -> D112
    pe luna trecută: „fără erori” la DUKIntegrator, iar XML-ul declară venitul în afara funcției de bază: E3_3 = 2, secțiunea E2 (E2_1
    5.000, E2_2 1.750, E2_3 3.250, E2_4 325), fără secțiunea E1, cu persoanele și deducerea 0 (E3_11 / E3_12). Înainte: E3_3 = 1 și E1
    pentru orice salariat.
    Temeiul: structura D112, E3_3 — „=1, pentru functia de baza / =2, pentru venit in afara functiei de baza”; E2 = Σ E3 „pentru E3_3=2”."""
    pg = patron.pg
    _stat_luna(patron, firma_c90, luni_inapoi=1)
    comp = _randuri_compozitie(_compozitie(patron))   # [lotul 13, 677] fereastra salariatului
    patron.captura("stat")
    assert comp["Impozit pe venit"] == _bani("325,00"), comp
    a = _singurul(_d112_xml(patron, firma_c90))
    assert len(a.get("asiguratE1", [])) == 0, a
    assert _int(_un(a, "asiguratE3"), "E3_3", "E3_11", "E3_12", "E3_14", "E3_15") == [2, 0, 0, 3250, 325], a
    assert _int(_un(a, "asiguratE2"), "E2_1", "E2_2", "E2_3", "E2_4") == [5000, 1750, 3250, 325], a


# ── C89 / C92 — certificatul cod 10, introdus pe ecranul „Concediu medical” ─────────────────────────────────────────────────────
_VEN6, _ZILE6 = 30000, 125          # media 240,00 lei/zi


def _propunerea_zilelor(pg, zile):
    """[C102] După „Sfârșit”, ecranul propune zilele lucrătoare (cerere asincronă). Pasul următor așteaptă propunerea, cum o vede
    contabilul înainte să scrie în câmp: un `fill` peste un răspuns care sosește între selectare și tastare lipea cifrele („1010 zile”,
    poarta 2 a lotului 11)."""
    pg.wait_for_function("(z) => document.querySelector(%r).value === z" % (_F + "#cm-zile"), arg=str(zile), timeout=20000)


def _formular_cod10(patron, firma):
    """Statul lunii trecute -> „Concediu” pe rândul salariatului -> „+ Certificat nou” -> certificat cod 10, 1–14 ale lunii trecute, media
    240,00 lei/zi, venitul realizat = baza − 499,59 (indemnizația 499,59, sub plafonul de 25%). Întoarce numărul zilelor lucrătoare."""
    pg = patron.pg
    di, ds = LUNA_TRECUTA, LUNA_TRECUTA.replace(day=14)
    st, r = _api(PATRON, "GET", "/util/zile-lucratoare?start=%s&end=%s" % (di.isoformat(), ds.isoformat()))
    assert st == 200, (st, r)
    zile = int(r["zile"])
    assert zile >= 9, zile          # Bmax = 25% × 240 × zile >= 540 > 499,59: indemnizația nu e plafonată
    _stat_luna(patron, firma, luni_inapoi=1)
    _concedii(patron)   # [lotul 13] fereastra salariatului -> „Concediu medical”
    pg.wait_for_selector(_F + "#cm-nou", timeout=20000)
    pg.click(_F + "#cm-nou")
    pg.wait_for_selector(_F + "#cm-calc", timeout=20000)
    pg.fill(_F + "#cm-serie", "AB")
    pg.fill(_F + "#cm-numar", "9001")
    pg.select_option(_F + "#cm-cod", "10")
    pg.fill(_F + "#cm-venit", "%.2f" % (240 * zile - 499.59))
    pg.fill(_F + "#cm-acord", di.isoformat())
    pg.fill(_F + "#cm-inceput", di.isoformat())
    pg.fill(_F + "#cm-sfarsit", ds.isoformat())
    _propunerea_zilelor(pg, zile)
    pg.fill(_F + "#cm-zile", str(zile))   # aceeași cifră ca propunerea ecranului (zilele lucrătoare dintre cele două date)
    for sel in ("#cm-continuare", "#cm-spital", "#cm-program-national"):
        alege(patron, sel.lstrip("#"), "false")   # [lotul 13, 676] Da / Nu = butoane
    pg.fill(_F + "#cm-ven6", str(_VEN6))
    pg.fill(_F + "#cm-zile6", str(_ZILE6))
    return zile


def _salveaza_certificat(patron):
    pg = patron.pg
    pg.click(_F + "#cm-calc")
    pg.wait_for_selector(_F + "#cm-rezultat .panou", timeout=30000)
    patron.captura("certificat_salvat")
    return pg.inner_text(_F + ".pf-lista")


def test_def_c89_indemnizatia_cm_rotunjita_la_sursa(patron, firma_c89):
    """C89. Pașii: Salariați -> statul lunii trecute -> „Concediu” -> „+ Certificat nou”: cod 10 (reducerea timpului de muncă cu 1/4),
    1–14 ale lunii trecute, numărul avizului medicului expert, media 240,00 lei/zi (30.000 lei / 125 de zile), venitul realizat = baza −
    499,59 -> „Calculează și salvează”: indemnizația 499,59, rotunjită la 500 -> lista certificatelor: „indemnizație brută 500,00 lei” ->
    lista: „indemnizație brută 500,00 lei · net 292,00 lei” -> statul lunii trecute, „Compoziția netului”: „Indemnizație CM (netă)” =
    500 − reținerile declarate pe indemnizație (D112: CAS + CASS + impozit ale salariatului − cele din salariu) -> Declarații -> D112: „fără
    erori”, iar D_20 + D_21 = 500. Înainte: 499,59 stocat și pe ecran (net 292,59), 500 în D112.
    Temeiul: Normele OUG 158/2005 (Ordinul MS 15/2018 / CNAS 1.311/2017) art.63 Exemplul nr.1 — „Ci = 2.499,59 lei - 1.875 lei = 624,59
    lei, rotunjit la 625 lei conform legii”."""
    pg = patron.pg
    _formular_cod10(patron, firma_c89)
    pg.fill(_F + "#cm-urgenta", "4321")
    lista = _salveaza_certificat(patron)
    # rândul certificatului: „… · indemnizație brută 500,00 lei · net 292,00 lei” (500 − 125 CAS − 50 CASS − 33 impozit)
    cert = re.findall(r"indemnizație brută ([\d.]+,\d\d) lei · net ([\d.]+,\d\d) lei", lista)
    assert [(_bani(b), _bani(n)) for b, n in cert] == [(_bani("500,00"), _bani("292,00"))], lista
    _stat_luna(patron, firma_c89, luni_inapoi=1)
    comp = _randuri_compozitie(_compozitie(patron))
    patron.captura("compozitia_netului")
    a = _singurul(_d112_xml(patron, firma_c89))
    d, b4, e3 = _un(a, "asiguratD"), _un(a, "asiguratB4"), _un(a, "asiguratE3")
    assert (d["D_9"], int(d["D_20"]) + int(d["D_21"])) == ("10", 500), d
    # Statul arată indemnizația cu reținerile DECLARATE (`stat_plata_api.stat_final`, comanda Costin 06.10.2026 pct.2: „421 se soldează la
    # ban și în lunile cu concediu medical”): reținerile CM = totalul declarat al salariatului (B4_8 CAS + B4_6 CASS + E3_15 impozit) −
    # reținerile din salariu (rândurile CAS / CASS / impozit ale compoziției); netul CM = indemnizația declarată (D_20 + D_21) − ele.
    # [lotul 13, 677] reținerile stau în coloana „Rețineri” (pozitive); indemnizația o dată, cu brutul și netul pe același rând
    ret_sal = comp["CAS (25%)"] + comp["CASS (10%)"] + comp["Impozit pe venit"]
    ret_cm = int(b4["B4_8"]) + int(b4["B4_6"]) + int(e3["E3_15"]) - ret_sal
    assert _bani_net(patron, "Indemnizație concediu medical") == 500 - ret_cm, (comp, b4, e3)
    assert comp["Net de plată"] == comp["Venituri în bani"] - comp["Total rețineri"], comp


def test_def_c92_cod10_cere_avizul_medicului_expert(patron, firma_c89):
    """C92. Pașii: Salariați -> statul lunii trecute -> „Concediu” -> „+ Certificat nou” -> cod 10: apare câmpul „Numărul avizului medicului
    expert” (marcat obligatoriu, cu ajutorul „Obligatoriu la codul 10: îl cere D112 (D_13).”) -> „Calculează și salvează” fără aviz: refuzul
    lângă câmp și în caseta „NU s-a salvat.”, nimic salvat -> cu avizul 4321: salvat -> Declarații -> D112 pe luna trecută: „fără erori”,
    iar certificatul are D_13 = 4321. Înainte: câmpul apărea numai la codul 06, deci D112 cu un certificat cod 10 era respins de DUK
    (regula S102: „daca D_9 = '10' atunci D_13 … trebuie completat”).
    Temeiul: structura D112, D_13 — „D_13#null pentru D_9 = 10 … Pentru reducerea cu 1/4 a duratei normale de lucru se completeaza
    numarul avizului medicului expert”."""
    pg = patron.pg
    _formular_cod10(patron, firma_c89)
    assert pg.is_visible(_F + "#cm-urgenta"), "câmpul avizului nu apare la codul 10"
    et = pg.inner_text(_F + "#cm-urgenta-eticheta")
    assert et.startswith("Numărul avizului medicului expert") and pg.locator(_F + "#cm-urgenta-eticheta .oblig").count() == 1, et
    assert pg.inner_text(_F + "#cm-urgenta-ajutor").strip() == "Obligatoriu la codul 10: îl cere D112 (D_13)."
    pg.click(_F + "#cm-calc")
    pg.wait_for_selector(_F + '.msg-eroare[data-camp="cm-urgenta"]', timeout=20000)
    patron.captura("fara_aviz")
    assert "numărul avizului medicului expert" in pg.inner_text(_F + '.msg-eroare[data-camp="cm-urgenta"]')
    assert pg.get_attribute(_F + "#cm-urgenta", "aria-invalid") == "true"
    caseta = pg.inner_text(_F + ".refuz-salvare")
    assert "NU s-a salvat" in caseta and "avizului" in caseta, caseta
    assert not sql('SELECT 1 FROM "%s".concedii_medicale' % firma_c89["schema"])
    pg.fill(_F + "#cm-urgenta", "4321")
    _salveaza_certificat(patron)
    assert sql('SELECT cod, cod_urgenta FROM "%s".concedii_medicale' % firma_c89["schema"]) == [("10", 4321)]
    d = _un(_singurul(_d112_xml(patron, firma_c89)), "asiguratD")
    assert (d["D_9"], d.get("D_13")) == ("10", "4321"), d


def test_def_c102_propunerea_zilelor_nu_inlocuieste_ce_a_scris_contabilul(patron, firma_c89):
    """C102 (găsită de Code la poarta 2 a lotului 11). Pașii: Salariați -> statul lunii trecute -> „Concediu” -> „+ Certificat nou” ->
    „Început” 1, „Sfârșit” 7, apoi „Sfârșit” 14: ecranul cere de două ori zilele lucrătoare; răspunsul pentru 1–7 sosește DUPĂ cel pentru
    1–14 -> „Zile lucrătoare CM” rămâne cifra pentru 1–14. Apoi „Sfârșit” 10 și contabilul scrie 3 zile înainte de răspuns -> câmpul rămâne
    3. Înainte: orice răspuns sosit după `await` scria peste câmp (cifra veche, sau peste ce tastase contabilul; în poartă: „1010 zile”).
    Răspunsurile se țin pe loc (`page.route`) și se eliberează în ordinea care producea defectul."""
    pg = patron.pg
    di = LUNA_TRECUTA
    zile = {}
    for zi in (7, 10, 14):
        st, r = _api(PATRON, "GET", "/util/zile-lucratoare?start=%s&end=%s" % (di.isoformat(), di.replace(day=zi).isoformat()))
        assert st == 200, (st, r)
        zile[zi] = str(r["zile"])
    assert zile[7] != zile[14] and zile[10] != "3", zile
    _stat_luna(patron, firma_c89, luni_inapoi=1)
    _concedii(patron)   # [lotul 13] fereastra salariatului -> „Concediu medical”
    pg.wait_for_selector(_F + "#cm-nou", timeout=20000)
    pg.click(_F + "#cm-nou")
    pg.wait_for_selector(_F + "#cm-calc", timeout=20000)
    tinute = []
    pg.route("**/util/zile-lucratoare*", lambda route: tinute.append(route))

    def asteapta_cereri(n):
        for _ in range(100):
            if len(tinute) >= n:
                return
            pg.wait_for_timeout(100)
        raise AssertionError("ecranul n-a cerut zilele lucrătoare (%d cereri din %d)" % (len(tinute), n))

    def elibereaza(i):
        with pg.expect_response(lambda r: "/util/zile-lucratoare" in r.url):
            tinute[i].continue_()
        pg.wait_for_timeout(300)        # handlerul ecranului rulează după răspuns

    valoare = lambda: pg.input_value(_F + "#cm-zile")   # noqa: E731
    pg.fill(_F + "#cm-inceput", di.isoformat())
    pg.fill(_F + "#cm-sfarsit", di.replace(day=7).isoformat())
    asteapta_cereri(1)
    pg.fill(_F + "#cm-sfarsit", di.replace(day=14).isoformat())
    asteapta_cereri(2)
    elibereaza(1)
    assert valoare() == zile[14], (valoare(), zile)
    elibereaza(0)                       # răspunsul vechi (1–7) sosește ultimul
    assert valoare() == zile[14], "răspunsul pentru 1–7, sosit ultimul, a înlocuit zilele pentru 1–14: %r (%s)" % (valoare(), zile)
    pg.fill(_F + "#cm-sfarsit", di.replace(day=10).isoformat())
    asteapta_cereri(3)
    pg.fill(_F + "#cm-zile", "3")       # contabilul scrie zilele înainte de răspuns
    elibereaza(2)
    patron.captura("zile_scrise")
    assert valoare() == "3", "propunerea întârziată a înlocuit zilele scrise de contabil: %r (%s)" % (valoare(), zile)
    pg.unroute("**/util/zile-lucratoare*")
    pg.click(_F + "#cm-renunta")


# ── C93 — beneficiarul sumei netaxabile: tipul de asigurat 1.11.2 (51) ────────────────────────────────────────────────────────────
def test_def_c93_beneficiarul_facilitatii_declarat_cu_tipul_51(patron, firma_c93):
    """C93. Pașii: salariat cu normă întreagă, funcția de bază, salariul = salariul minim al lunii trecute -> Declarații -> D112 pe luna
    trecută: „fără erori”, iar XML-ul îl declară cu tipul de asigurat 1.11.2 (B1_1 = E3_2 = 51), suma netaxabilă pe rândurile ei (B2_5S =
    B4_7S = suma scăzută din bază), câștigul brut realizat (B2_5C = B4_7C = salariul) și C1_11 = baza + suma netaxabilă. Înainte: tipul 1
    (B1_1 = E3_2 = 1), fără B2_5S / B4_7S, C1_11 = numai baza.
    Temeiul: OPANAF 605/2026 anexa 2, B.1 rândul 1 — „beneficiar al prevederilor art. III alin. (1) din O.U.G. nr. 89/2025 […] se va
    alege tipul de asigurat 1.11.2”; structura D112, „B2_5C= B2_5+ B2_5S pt.B1_1=51”, „C1_11= … ΣB2_5 + … ΣB2_5S”."""
    sm, fac = firma_c93["sm"], firma_c93["fac"]
    st = _d112_xml(patron, firma_c93)
    a = _singurul(st)
    b1, b2, b4, e3 = (_un(a, x) for x in ("asiguratB1", "asiguratB2", "asiguratB4", "asiguratE3"))
    assert _int(b1, "B1_1") + _int(e3, "E3_2", "E3_3") == [51, 51, 1], (b1, e3)
    assert _int(b2, "B2_5", "B2_5S", "B2_5C") == [sm - fac, fac, sm], b2
    assert _int(b4, "B4_7", "B4_7S", "B4_7C") == [sm - fac, fac, sm], b4
    assert _int(_un(st["_angajator"], "angajatorC1"), "C1_11", "C1_T1") == [sm, sm], st["_angajator"]


# ── C94 — venitul lunii: E3_4 = „P”, fără perioada „altă lună” ──────────────────────────────────────────────────────────────────
def test_def_c94_venitul_lunii_cu_e3_4_p(patron, firma_c90):
    """C94. Pașii: Declarații -> D112 pe luna trecută: „fără erori”, iar secțiunea E3 a salariatului poartă E3_4 = „P” (venit din perioada
    de raportare), fără E3_5 / E3_6. Înainte: E3_4 = „A” (venit din altă perioadă), cu E3_5 = E3_6 = luna raportată.
    Temeiul: OPANAF 605/2026 anexa 2, E.3 rândul 4 — „"P" - se utilizează pentru veniturile realizate în perioada de raportare”; rândurile
    5-6 „Se completează doar dacă la rândul 4 […] a fost utilizată opţiunea "A"”."""
    e3 = _un(_singurul(_d112_xml(patron, firma_c90)), "asiguratE3")
    assert (e3["E3_4"], set(e3) & {"E3_5", "E3_6"}) == ("P", set()), e3


# ── C96 — norma parțială: B1_3 = Pn, orele lucrate cu orele contractului ─────────────────────────────────────────────────────────
@pytest.fixture
def firma_c96():
    """Doi salariați adăugați pe ruta salariaților: normă parțială de 4 ore (2.500 lei) și normă întreagă (5.000 lei)."""
    f = _firma_cu_salariat("S9N", tip_norma="partiala", ore_zi=4, salariu_brut=2500)
    try:
        st, r = _api(PATRON, "POST", "/tenants/%d/salariati" % f["tenant_id"],
                     {"nume": "Ionescu", "prenume": "Ana", "cnp": _cnp("286020340123"), "data_angajare": "2026-01-05",
                      "tip_norma": "intreaga", "ore_zi": 8, "salariu_brut": 5000, "persoane_intretinere": 0,
                      "scutit_contrib_minim": False, "functie_baza": True, "cor": "331302"})
        assert st == 200, (st, r)
        yield f
    finally:
        _scoate_firmele_e2e(f["tenant_id"])


def test_def_c96_norma_partiala_declarata_cu_orele_ei(patron, firma_c96):
    """C96. Pașii: doi salariați — „Tip normă: parțială”, 4 ore pe zi, și „întreagă”, 8 ore -> Declarații -> D112 pe luna trecută: „fără
    erori” la DUKIntegrator, iar XML-ul declară salariatul cu normă parțială cu tipul de contract P4 (B1_3), programul locului de muncă 8
    (B1_4) și orele lucrate = zilele lucrătoare × 4 (B1_6); cel cu normă întreagă: N, 8, zilele × 8. Înainte: „N” pentru amândoi, iar orele
    lucrate cu 8 ore pe zi și la normă parțială.
    Temeiul: OPANAF 605/2026 anexa 2, B.1 rândul 3 — „se completează cu N (norma întreagă 6, 7, 8) sau Pn (parţial P1, P2, ..., P7)”;
    structura D112, „daca B1_3= ‘Pi ‘atunci B1_6 <= NZL* i”."""
    import calendar
    ultima = LUNA_TRECUTA.replace(day=calendar.monthrange(LUNA_TRECUTA.year, LUNA_TRECUTA.month)[1])
    st, r = _api(PATRON, "GET", "/util/zile-lucratoare?start=%s&end=%s" % (LUNA_TRECUTA.isoformat(), ultima.isoformat()))
    assert st == 200, (st, r)
    nzl = int(r["zile"])
    st = _d112_xml(patron, firma_c96)
    assert sorted(k for k in st if k != "_angajator") == sorted([_cnp("185010140123"), _cnp("286020340123")]), sorted(st)
    p, n = _un(st[_cnp("185010140123")], "asiguratB1"), _un(st[_cnp("286020340123")], "asiguratB1")
    assert (p["B1_3"], int(p["B1_4"]), int(p["B1_6"])) == ("P4", 8, nzl * 4), p
    assert (n["B1_3"], int(n["B1_4"]), int(n["B1_6"])) == ("N", 8, nzl * 8), n


# ── C99 — contribuția minimă în luna cu concediu medical: aceeași cifră pe stat, pe fluturaș și în D112 ─────────────────────────────
_ETICHETA_SUPRATAXA = "Suprataxă part-time (CAS + CASS pe podeaua salariului minim), plătită de angajator"   # compozitie_fluturas


@pytest.fixture
def firma_c99():
    f = _firma_cu_salariat("S9M", tip_norma="partiala", ore_zi=4, salariu_brut=2000)
    try:
        yield f
    finally:
        _scoate_firmele_e2e(f["tenant_id"])


def test_def_c99_suprataxa_in_luna_cu_cm_aceeasi_pe_stat_fluturas_si_d112(patron, firma_c99):
    """C99. Pașii: salariat cu normă parțială (4 ore, 2.000 lei) -> statul lunii trecute -> „Concediu” -> „+ Certificat nou”: cod 01, 1–10
    ale lunii trecute -> „Calculează și salvează” -> statul lunii trecute, „Compoziția netului”: rândul „Suprataxă part-time …” ->
    „Fluturaș”: aceeași sumă -> Declarații -> D112 pe luna trecută: „fără erori”, suma limită B4_7P = ROUND((salariul minim − suma
    netaxabilă) × zilele lucrate fără CM (B4_1) / zilele lucrătoare ale lunii) și diferența suportată de angajator B4_8D + B4_6D = suprataxa
    de pe stat și de pe fluturaș. Înainte: statul socotea podeaua și pe zilele de concediu medical (suprataxă mai mare decât în D112).
    Temeiul: CF art.146 alin.(5^6) — „corespunzător numărului zilelor lucrătoare din lună în care contractul a fost activ”; Legea 53/2003
    art.50 lit.b) — contractul „se suspendă de drept” pe durata concediului pentru incapacitate temporară de muncă."""
    import calendar
    from core.common import cota, salariu_minim_luna
    pg = patron.pg
    di, ds = LUNA_TRECUTA, LUNA_TRECUTA.replace(day=10)
    st, r = _api(PATRON, "GET", "/util/zile-lucratoare?start=%s&end=%s" % (di.isoformat(), ds.isoformat()))
    assert st == 200, (st, r)
    zile_cm = int(r["zile"])
    ultima = LUNA_TRECUTA.replace(day=calendar.monthrange(LUNA_TRECUTA.year, LUNA_TRECUTA.month)[1])
    st, r = _api(PATRON, "GET", "/util/zile-lucratoare?start=%s&end=%s" % (LUNA_TRECUTA.isoformat(), ultima.isoformat()))
    assert st == 200, (st, r)
    nzl = int(r["zile"])
    _stat_luna(patron, firma_c99, luni_inapoi=1)
    _concedii(patron)   # [lotul 13] fereastra salariatului -> „Concediu medical”
    pg.wait_for_selector(_F + "#cm-nou", timeout=20000)
    pg.click(_F + "#cm-nou")
    pg.wait_for_selector(_F + "#cm-calc", timeout=20000)
    pg.fill(_F + "#cm-serie", "AB")
    pg.fill(_F + "#cm-numar", "9902")
    pg.select_option(_F + "#cm-cod", "01")
    pg.fill(_F + "#cm-acord", di.isoformat())
    pg.fill(_F + "#cm-inceput", di.isoformat())
    pg.fill(_F + "#cm-sfarsit", ds.isoformat())
    _propunerea_zilelor(pg, zile_cm)
    pg.fill(_F + "#cm-zile", str(zile_cm))
    for sel in ("#cm-continuare", "#cm-spital", "#cm-program-national"):
        alege(patron, sel.lstrip("#"), "false")   # [lotul 13, 676] Da / Nu = butoane
    pg.fill(_F + "#cm-ven6", "12000")
    pg.fill(_F + "#cm-zile6", "125")
    _salveaza_certificat(patron)
    _stat_luna(patron, firma_c99, luni_inapoi=1)
    comp = _randuri_compozitie(_compozitie(patron))
    patron.captura("compozitia_netului")
    supra = comp.get(_ETICHETA_SUPRATAXA)
    assert supra is not None and supra > 0, comp
    text = _pdf_fluturas(patron)
    patron.captura("fluturas")
    m = re.findall(r"podeaua\s+salariului\s+minim\),\s+plătită\s+de\s+angajator:\s+([\d.]+,\d\d)", text)
    assert [_bani(x) for x in m] == [supra], text[:2000]
    b4 = _un(_singurul(_d112_xml(patron, firma_c99)), "asiguratB4")
    sm = int(salariu_minim_luna(LUNA_TRECUTA)[0])
    fac = int(cota("facilitate_salariu_minim", LUNA_TRECUTA)[0])
    zile_activ = nzl - zile_cm                     # zilele lucrătoare în care contractul a fost activ (fără CM)
    assert int(b4["B4_1"]) == zile_activ, b4
    from decimal import ROUND_HALF_UP, Decimal
    podea = int((Decimal(sm - fac) * zile_activ / nzl).quantize(Decimal("1"), rounding=ROUND_HALF_UP))   # structura: ROUND(sm*zile_PT/NZL)
    assert int(b4["B4_7P"]) == podea, (b4, podea)
    assert int(b4["B4_8D"]) + int(b4["B4_6D"]) == supra, (b4, supra)
