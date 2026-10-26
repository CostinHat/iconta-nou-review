# -*- coding: utf-8 -*-
"""Lotul 12 — pachetul ctrl, partea D112 / salarii: C97 (pensionarul, B1_2), 43 (proratarea la certificatul inițial cu zi de diminuare),
69 (pragul contribuției minime la normă parțială, validat de DUKIntegrator fără atenționare), 482 (luna cu concediu medical: baza CAM,
deducerea personală, reținerile din indemnizație pe ecran). Pașii contabilului pe aplicația din index, pe baza de TEST: statul lunii
trecute (ecranul Salariați), „Compoziția netului”, certificatul pe ecranul „Concediu medical”, Declarații -> D112 -> DUKIntegrator ->
„Vezi XML-ul generat”.

Date de pornire: fiecare test își face firma sintetică și salariatul pe ruta salariaților (`POST /tenants/{id}/salariati`, ca
`e2e_lot11_s9._firma_cu_salariat`). Motivul exceptării (C97) se trimite pe aceeași rută: ecranul salariatului nu are încă alegerea
motivului (schimbare cerută pachetului care deține `firme.js`). Certificatele se introduc pe ecranul „Concediu medical”. CNP-urile au
cifra de control calculată (`e2e_bloc_b._cnp`)."""
import calendar
from decimal import ROUND_HALF_UP, Decimal

import pytest

from conftest import _scoate_firmele_e2e
from e2e_bloc_b import _cnp
from e2e_bloc_d import LUNA_TRECUTA, PATRON, _api
from e2e_bloc_d import _stat as _stat_luna
from e2e_lot13_sal_ajutor import alege
from e2e_lot11_s9 import (_F, _bani_net, _concedii, _compozitie, _d112_xml, _firma_cu_salariat, _int, _propunerea_zilelor, _randuri_compozitie,
                          _salveaza_certificat, _singurul, _un)


def _zile_lucratoare(de, pana):
    st, r = _api(PATRON, "GET", "/util/zile-lucratoare?start=%s&end=%s" % (de.isoformat(), pana.isoformat()))
    assert st == 200, (st, r)
    return int(r["zile"])


def _nzl():
    return _zile_lucratoare(LUNA_TRECUTA, LUNA_TRECUTA.replace(day=calendar.monthrange(LUNA_TRECUTA.year, LUNA_TRECUTA.month)[1]))


def _leu(x):
    return int(Decimal(str(x)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _certificat_01(patron, firma, zi_sfarsit, numar):
    """Statul lunii trecute -> „Concediu” pe rândul salariatului -> „+ Certificat nou”: cod 01 (boală obișnuită), INIȚIAL, din prima zi
    a lunii trecute până la `zi_sfarsit`, media 240 lei/zi (30.000 lei / 125 de zile) -> „Calculează și salvează”. Întoarce zilele
    lucrătoare ale certificatului."""
    pg = patron.pg
    di, ds = LUNA_TRECUTA, LUNA_TRECUTA.replace(day=zi_sfarsit)
    zile = _zile_lucratoare(di, ds)
    _stat_luna(patron, firma, luni_inapoi=1)
    _concedii(patron)   # [lotul 13] fereastra salariatului -> „Concediu medical”
    pg.wait_for_selector(_F + "#cm-nou", timeout=20000)
    pg.click(_F + "#cm-nou")
    pg.wait_for_selector(_F + "#cm-calc", timeout=20000)
    pg.fill(_F + "#cm-serie", "AB")
    pg.fill(_F + "#cm-numar", numar)
    pg.select_option(_F + "#cm-cod", "01")
    pg.fill(_F + "#cm-acord", di.isoformat())
    pg.fill(_F + "#cm-inceput", di.isoformat())
    pg.fill(_F + "#cm-sfarsit", ds.isoformat())
    _propunerea_zilelor(pg, zile)
    pg.fill(_F + "#cm-zile", str(zile))
    for sel in ("#cm-continuare", "#cm-spital", "#cm-program-national"):
        alege(patron, sel.lstrip("#"), "false")   # [lotul 13, 676] Da / Nu = butoane
    pg.fill(_F + "#cm-ven6", "30000")
    pg.fill(_F + "#cm-zile6", "125")
    _salveaza_certificat(patron)
    return zile


def _d112_xml_cu_atentionarea_s38_3(patron, firma):
    """Ca `e2e_lot11_s9._d112_xml`, dar la pensionar DUKIntegrator J27.0.6 dă o singură atenționare, S38.3 („Baza Indemnizatie SOMAJ = 0
    si Ore lucrate efectiv in luna > 0”): validatorul își calculează `baza_AJS` din B1_2 înainte de a-l citi din XML (bytecode
    `d112validator/v33/AsiguratB1`, offset 1543 față de 2021). Se cere: nicio eroare, iar atenționarea e numai S38.3."""
    import re
    import xml.etree.ElementTree as ET
    from e2e_bloc_d import _genereaza
    from e2e_lot11_s9 import _NS, _XML_GENERAT
    pg = patron.pg
    _genereaza(patron, firma, "d112", LUNA_TRECUTA.year, LUNA_TRECUTA.month)
    assert pg.locator(_F + ".dec-eroare").count() == 0, patron.fereastra()[:3000]
    avert = pg.locator(_F + ".dec-avert:has-text('a semnalat atenționări')")
    assert avert.count() == 1, patron.fereastra()[:3000]
    assert set(re.findall(r"regula: (S[\d.]+)", avert.inner_text())) == {"S38.3"}, avert.inner_text()
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


# ── C97 — pensionarul pentru limită de vârstă, declarat cu B1_2 = 1 ─────────────────────────────────────────────────────────────
@pytest.fixture
def firma_c97():
    """Pensionarul (scutit de contribuția minimă, motivul 4) și un salariat obișnuit."""
    f = _firma_cu_salariat("L12P", scutit_contrib_minim=True, motiv_exceptare=4, cnp=_cnp("150030341001"))
    try:
        st, r = _api(PATRON, "POST", "/tenants/%d/salariati" % f["tenant_id"],
                     {"nume": "Ionescu", "prenume": "Ana", "cnp": _cnp("286020340123"), "data_angajare": "2026-01-05",
                      "tip_norma": "intreaga", "ore_zi": 8, "salariu_brut": 5000, "persoane_intretinere": 0,
                      "scutit_contrib_minim": False, "functie_baza": True, "cor": "331302"})
        assert st == 200, (st, r)
        yield f
    finally:
        _scoate_firmele_e2e(f["tenant_id"])


def test_def_c97_pensionarul_declarat_cu_b1_2(patron, firma_c97):
    """C97. Pașii: salariat scutit de contribuția minimă cu motivul 4 („pensionari pentru limită de vârstă”) și un salariat obișnuit ->
    Declarații -> D112 pe luna trecută: fără erori la DUKIntegrator (numai atenționarea S38.3, din defectul validatorului), iar XML-ul
    declară pensionarul cu B1_2 = 1, fără bază de șomaj
    (B1_10 = 0, B4_3 = 0), iar „Număr de asigurați șomaj” (B_cnp) = 1. Înainte: B1_2 = 0 pentru oricine, bază de șomaj pe pensionar,
    B_cnp = 2. Temeiul: OPANAF 605/2026 anexa 2, B.1 rândul 2 — „se completează cu "1" în cazul asiguraţilor care au şi statutul de
    pensionar”; structura D112, „baza_AJS=true daca asigSO=1 si B1_2=0”, „daca baza_AJS = false atunci B1_10=0”."""
    st = _d112_xml_cu_atentionarea_s38_3(patron, firma_c97)
    p, n = st[_cnp("150030341001")], st[_cnp("286020340123")]
    b1, b4 = _un(p, "asiguratB1"), _un(p, "asiguratB4")
    assert (b1["B1_2"], int(b1["B1_10"]), int(b4["B4_3"])) == ("1", 0, 0), (b1, b4)
    assert _un(n, "asiguratB1")["B1_2"] == "0", n
    assert int(_un(st["_angajator"], "angajatorB")["B_cnp"]) == 1, st["_angajator"]


# ── 43 — proratarea pe zilele certificatului inițial, cu ziua de diminuare ──────────────────────────────────────────────────────
@pytest.fixture
def firma_43():
    f = _firma_cu_salariat("L12D", salariu_brut=6000)
    try:
        yield f
    finally:
        _scoate_firmele_e2e(f["tenant_id"])


def test_def_43_proratare_pe_zilele_certificatului_initial_cu_zi_de_diminuare(patron, firma_43):
    """43. Pașii: salariat cu 6.000 lei -> statul lunii trecute -> „Concediu” -> „+ Certificat nou”: cod 01, INIȚIAL, 1–7 ale lunii
    trecute -> „Calculează și salvează” -> Declarații -> D112: „fără erori”, zilele lucrate B1_15 = zilele lucrătoare ale lunii − zilele
    certificatului (ziua de diminuare e zi de concediu, nu zi lucrată), salariul realizat B2_5 = 6.000 × B1_15 / zilele lunii (la leu),
    iar zilele plătite (D_14 + D_15) = zilele certificatului − 1. „Compoziția netului” arată aceleași zile de concediu medical. Înainte:
    salariul se prorata pe zilele PLĂTITE, deci ziua de diminuare apărea lucrată. Temeiul: OUG 91/2025 art.II alin.(1) (indemnizația se
    calculează „prin diminuarea cu o zi”); structura D112 D_14/D_15 („se va scădea 1 zi (prima zi)”)."""
    zile = _certificat_01(patron, firma_43, 7, "4301")
    nzl = _nzl()
    _stat_luna(patron, firma_43, luni_inapoi=1)
    comp = _compozitie(patron)
    patron.captura("compozitia_netului")
    # [lotul 13, 677] fără rândul „Zile de concediu medical: N” fără sumă: zilele stau pe rândul indemnizației, cu brutul și netul ei
    from e2e_lot13_sal_ajutor import text_compozitie
    t = text_compozitie(patron)
    assert "Zile de concediu medical" not in t and ("Indemnizație concediu medical · %d zile" % zile) in " ".join(t.split()), t
    assert ("%d zile lucrate din %d" % (nzl - zile, nzl)) in t, t
    a = _singurul(_d112_xml(patron, firma_43))
    b1, b2, d = _un(a, "asiguratB1"), _un(a, "asiguratB2"), _un(a, "asiguratD")
    assert int(b1["B1_15"]) == nzl - zile, (b1, nzl, zile)
    assert int(b2["B2_5"]) == _leu(Decimal(6000) * (nzl - zile) / nzl), (b2, nzl, zile)
    assert int(d["D_14"]) + int(d["D_15"]) == zile - 1, d


# ── 69 — pragul contribuției minime la normă parțială, fără atenționarea validatorului ──────────────────────────────────────────
@pytest.fixture
def firma_69():
    f = _firma_cu_salariat("L12T", tip_norma="partiala", ore_zi=4, salariu_brut=2000)
    try:
        yield f
    finally:
        _scoate_firmele_e2e(f["tenant_id"])


def test_def_69_pragul_part_time_validat_fara_atentionare(patron, firma_69):
    """69. Pașii: salariat cu normă parțială (4 ore, 2.000 lei, sub salariul minim) -> Declarații -> D112 pe luna trecută: DUKIntegrator
    „fără erori” (nicio atenționare: vechiul validator J27.0.1 semnala SP1B4_1 „B4_5P diferit de suma calculata”), iar suma limită B4_5P =
    B4_7P = salariul minim al lunii − suma netaxabilă (OUG 89/2025 art.III alin.(5)), pe toată luna. Temeiul: CF art.146 alin.(5^6); OUG
    89/2025 art.III alin.(5) lit.b „pentru veniturile aferente perioadei 1 iulie-31 decembrie 2026, cu suma de 200 lei lunar”."""
    from core.common import cota, salariu_minim_luna
    prag = int(salariu_minim_luna(LUNA_TRECUTA)[0]) - int(cota("facilitate_salariu_minim", LUNA_TRECUTA)[0])
    b4 = _un(_singurul(_d112_xml(patron, firma_69)), "asiguratB4")   # _d112_xml cere „fără erori” (fără atenționare)
    assert "a semnalat atenționări" not in patron.fereastra(), patron.fereastra()[:2000]
    assert _int(b4, "B4_5P", "B4_7P") == [prag, prag], b4


# ── 482 — luna cu concediu medical: baza CAM, reținerile din indemnizație pe ecran ───────────────────────────────────────────────
@pytest.fixture
def firma_482():
    f = _firma_cu_salariat("L12C", salariu_brut=6000)
    try:
        yield f
    finally:
        _scoate_firmele_e2e(f["tenant_id"])


def test_def_482_cam_si_retinerile_din_indemnizatie(patron, firma_482):
    """482. Pașii: salariat cu 6.000 lei -> statul lunii trecute -> „Concediu” -> „+ Certificat nou”: cod 01, 1–9 ale lunii trecute ->
    „Calculează și salvează” -> statul, „Compoziția netului”: sub „Indemnizație CM (netă)” stau brutul indemnizației și reținerile din ea —
    CAS, CASS, impozit —, iar brutul minus reținerile = netul -> rândul CAM al compoziției = CAM-ul declarat -> Declarații -> D112: „fără
    erori”, baza CAM a salariatului (B1_5 = B4_14 = C4_baza) = salariul realizat (B2_5) + indemnizația suportată de angajator (Σ D_20),
    iar C4_ct = ROUND(C4_baza × 2,25%). Înainte: compoziția arăta numai netul indemnizației, iar baza CAM lăsa afară partea angajatorului.
    Temeiul: CF art.220^4 alin.(1) + art.76 alin.(1) („inclusiv indemnizațiile pentru incapacitate temporară de muncă”), art.220^5 (se
    exceptează numai partea FNUASS), OUG 158/2005 art.12 lit.A; OPANAF 605/2026 anexa 2, secțiunea B rândul 4."""
    _certificat_01(patron, firma_482, 9, "4821")
    _stat_luna(patron, firma_482, luni_inapoi=1)
    comp = _randuri_compozitie(_compozitie(patron))
    patron.captura("compozitia_netului")
    # [lotul 13, 677] indemnizația o dată: brutul în valoarea rândului, netul pe același rând; reținerile ei în coloana „Rețineri”
    brut = comp["Indemnizație concediu medical"]
    ret = [comp["reținut din indemnizație: CAS (25%)"], comp["reținut din indemnizație: CASS (10%)"],
           comp["reținut din indemnizație: impozit pe venit"]]
    assert all(x > 0 for x in ret[:2]), comp
    assert brut - sum(ret) == _bani_net(patron, "Indemnizație concediu medical"), comp
    cam_stat = comp["CAM — contribuția asiguratorie pentru muncă (2,25%), plătită de angajator"]
    st = _d112_xml(patron, firma_482)
    a = _singurul(st)
    b1, b2, b4 = _un(a, "asiguratB1"), _un(a, "asiguratB2"), _un(a, "asiguratB4")
    d20 = sum(int(x["D_20"]) for x in a.get("asiguratD", []))
    assert d20 > 0, a.get("asiguratD")
    assert int(b1["B1_5"]) == int(b4["B4_14"]) == int(b2["B2_5"]) + d20, (b1, b2, b4, d20)
    c4 = _un(st["_angajator"], "angajatorC4")
    assert int(c4["C4_baza"]) == int(b1["B1_5"]), c4
    assert int(c4["C4_ct"]) == _leu(Decimal(c4["C4_baza"]) * Decimal("0.0225")), c4
    assert cam_stat == int(c4["C4_ct"]), (cam_stat, c4)
    # reținerile din indemnizație + cele din salariu = cele declarate (CAS B4_8 + CASS B4_6 + impozit E3_15 ale salariatului);
    # [lotul 13, 677] în coloana „Rețineri” sumele sunt pozitive (înainte compoziția le arăta cu minus)
    ret_sal = comp["CAS (25%)"] + comp["CASS (10%)"] + comp["Impozit pe venit"]
    e3 = _un(a, "asiguratE3")
    assert sum(ret) + ret_sal == int(b4["B4_8"]) + int(b4["B4_6"]) + int(e3["E3_15"]), (ret, b4, e3, comp)
