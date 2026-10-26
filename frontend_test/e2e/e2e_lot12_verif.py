# -*- coding: utf-8 -*-
"""Lotul 12, comanda Costin 12.1 (verbatim în DECIZII „Comanda 12.1”), pachetul `verif` — DOVADA numerelor închise prin echivalență
(pct.14) și a deficiențelor C declarate rezolvate numai în raport (pct.13), acolo unde testul de capăt la capăt existent NU reface pașii
descriși la numărul acesta. Nu se schimbă cod de aplicație: testele refac pașii contabilului pe aplicația din index, pe baza de TEST.

  * 135 — „Plan de conturi: conținea 731–738.” Costin a văzut conturile pe o firmă EXISTENTĂ (F1, decizia V3 din 08.10.2026), nu pe una
    nouă: testul existent (`e2e_bloc_d.py::test_def_135_planul_de_conturi_fara_731_738`) probează numai șablonul firmei noi. Aici: o firmă
    al cărei plan are 731–738 ca șablonul vechi -> migrarea care le scoate (`core/migrare_retest_0810.scoate_conturi_73x`, rulată la
    publicare) -> Plan de conturi, caută „73”: contul nefolosit a dispărut, iar cel folosit pe o notă rămâne, marcat „în afara planului
    legal al normei firmei” (decizia Costin 08.10.2026 V3: „un cont care nu e în planul legal nu se poate crea sau folosi fără
    avertisment”).
  * C43 — D300: serviciile către un client din AFARA UE intrau și la rd.3.1 (numai serviciile către clienți stabiliți în UE). Rândul
    n-avea test de capăt la capăt (numai `core/test_274b_…::test_c43_…`): aici D300 generat pe ecran, cu un client din Irlanda și unul
    din Statele Unite, validat cu DUKIntegrator.
  * C60 — Casă: registrul pornea de la zero în fiecare lună. Testul existent (`e2e_lot92.py::test_def_c60_…`) reface numai nota lunii
    trecute; aici și soldul de PRELUARE (balanța de deschidere), cealaltă jumătate a descrierii.
  * 280 — „Salarii: CAM 112,50 afișat 112 și 158,52 afișat 159.” (stare: nu se aplică). Rândul n-are test: aici, pe ecran, cazul exact al
    lui Costin (F5 10/2026: Ionescu 5.000 lei -> 112,50; Popescu -> 158,5x): cartelele arată 112 și 159, iar suma lor e CAM-ul declarat
    în D112 (271), nu 272 cât ar da rotunjirea fiecăreia.

DATE DE PORNIRE fără ecran (declarate, regula lui 429): la 135, conturile șablonului vechi și nota pe 734 se scriu direct în baza de test
(niciun ecran nu mai poate crea planul vechi), iar migrarea se cheamă cum o cheamă publicarea; la 280, salariații intră pe ruta
salariaților (`POST /tenants/{id}/salariati`, ca `e2e_lot11_s9._firma_cu_salariat`). CNP-urile au cifra de control calculată
(`e2e_bloc_b._cnp`)."""
import datetime as _dt
from decimal import ROUND_HALF_UP, Decimal

import pytest

from conftest import _db, _scoate_firmele_e2e, firma_noua, perioada_incheiata, sql
from e2e_bloc_a import PRODUS, _ok, pregateste_firma
from e2e_bloc_a import _api as _api_e
from e2e_bloc_a import _card as _card_firma
from e2e_bloc_b import _cnp
from e2e_bloc_d import PATRON, _api, _deschide
from e2e_bloc_e import _nota
from e2e_pozitii_validate import _atr, _pas2, _valideaza_notele
from e2e_bloc_d import _stat as _stat_luna
from e2e_lot11_s9 import _F, _d112_xml, _firma_cu_salariat, _randuri_compozitie, _un

AZI = _dt.date.today()

# ── 135 — firma veche cu 731–738 în plan ─────────────────────────────────────────────────────────────────────────────────────────
#: exact conturile semănate de șablonul vechi (`core/migrare_retest_0810.CONTURI_73X`), scrise aici din registrul deciziei V3
#: („Planul de conturi al F1 conține 731, 732, 733, 734, 736, 738”), nu importate din codul probat
CONTURI_VECHI = ("731", "732", "733", "734", "736", "738")
MARCAJ_AFARA = "în afara planului legal al normei firmei"


@pytest.fixture
def firma_135():
    for f in firma_noua():
        yield f


def test_def_135_firma_veche_cu_731_738_ramane_fara_ele_dupa_migrare(patron, firma_135):
    """135. Pașii: o firmă creată pe șablonul vechi (planul ei are 731, 732, 733, 734, 736, 738 — conturile entităților fără scop
    patrimonial, OMFP 3103/2017), cu o notă pe 734 -> publicarea rulează migrarea `migrare_retest_0810` -> contabilul deschide firma ->
    Plan de conturi -> caută „73”: 731, 732, 733, 736, 738 nu mai sunt; 734, folosit pe notă, rămâne (o notă nu-și pierde contul) și poartă
    „folosit în note · în afara planului legal al normei firmei”. Temei: OMFP 1802/2014 pct.594 — planul de conturi al societăților nu are
    clasa 73x (aceasta e a OMFP 3103/2017); decizia Costin 08.10.2026 V3 pentru contul rămas."""
    s = firma_135["schema"]
    for c in CONTURI_VECHI:
        # date-de-pornire: conturile 73x ale șablonului vechi (OMFP 3103/2017), cum le avea planul unei firme create înainte de migrare
        sql('INSERT INTO "%s".plan_conturi (simbol, denumire) VALUES (%%s, %%s) ON CONFLICT (simbol) DO NOTHING' % s,
            (c, "Cont %s din șablonul vechi" % c))
    # date-de-pornire: nota veche pe 734, scrisă cât contul era în planul firmei (șablonul vechi); migrarea trebuie s-o păstreze
    nid = sql('INSERT INTO "%s".inregistrari (data, descriere, sursa, status) VALUES (CURRENT_DATE, %%s, \'manual\', \'ciorna\') '
              'RETURNING id' % s, ("Notă veche pe 734 (D135)",))[0][0]
    # date-de-pornire: rândul notei vechi 5311 = 734 de mai sus
    sql('INSERT INTO "%s".inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%%s, \'5311\', \'734\', 10)' % s, (nid,))
    from core import migrare_retest_0810 as mig
    db = _db()
    with db.get_conn() as c:
        rez = mig.scoate_conturi_73x(c, s)
        c.commit()
    pg = patron.pg
    patron.firma(firma_135["nume"])
    _deschide(patron, "#fa-planconturi", "Plan de conturi")
    pg.wait_for_selector(_F + ".pf-frand[data-simbol='722']", timeout=20000)
    pg.fill(_F + "#pcf-cauta", "73")
    pg.wait_for_function("() => { const f = [...document.querySelectorAll('.fereastra')].pop();"
                         " return f && !f.querySelector(\".pf-frand[data-simbol='722']\"); }", timeout=10000)
    simboluri = pg.eval_on_selector_all(_F + "#pcf-lista .pf-frand[data-simbol]", "els => els.map(e => e.dataset.simbol)")
    rand_734 = pg.inner_text(_F + "#pcf-lista .pf-frand[data-simbol='734']") if "734" in simboluri else ""
    patron.captura("plan_dupa_migrare")
    assert rez and sorted(rez["scoase"]) == ["731", "732", "733", "736", "738"], rez
    ramase = [x for x in simboluri if x in CONTURI_VECHI]
    assert ramase == ["734"], simboluri
    assert "folosit în note" in rand_734 and MARCAJ_AFARA in rand_734, rand_734


# ── 280 — CAM pe cartele = CAM-ul declarat ──────────────────────────────────────────────────────────────────────────────────────
#: CF art.220^3 alin.(1) „Cota contribuției asiguratorii pentru muncă este de 2,25%.” (anaf_surse/cod_fiscal_227_2015_consolidat.txt)
COTA_CAM = Decimal("0.0225")
ETICHETA_CAM = "CAM — contribuția asiguratorie pentru muncă (2,25%), plătită de angajator"   # stat_plata_api.compozitie_fluturas
BRUT_IONESCU, BRUT_POPESCU = 5000, 7045   # 112,50 și 158,5125: aceeași pereche de fracțiuni ca la F5 10/2026 (112,50 și 158,52)


@pytest.fixture
def firma_280():
    f = _firma_cu_salariat("V280", nume="Ionescu", prenume="Vasile", salariu_brut=BRUT_IONESCU)
    try:
        corp = {"nume": "Popescu", "prenume": "Elena", "cnp": _cnp("285010140124"), "data_angajare": "2026-01-05", "tip_norma": "intreaga",
                "ore_zi": 8, "salariu_brut": BRUT_POPESCU, "persoane_intretinere": 0, "scutit_contrib_minim": False,
                "functie_baza": True, "cor": "331302"}
        st, r = _api(PATRON, "POST", "/tenants/%d/salariati" % f["tenant_id"], corp)
        assert st == 200, (st, r)
        yield f
    finally:
        _scoate_firmele_e2e(f["tenant_id"])


def _cam_pe_cartela(patron, nume):
    """Statul afișat -> rândul salariatului -> „Compoziția netului”: rândul CAM (lei)."""
    # [lotul 13, 677] fereastra salariatului, coloana „Rezultat”; înapoi la stat pentru salariatul următor
    from e2e_lot13_sal_ajutor import coloane, deschide_salariat, inchide
    deschide_salariat(patron, nume)
    comp = _randuri_compozitie(coloane(patron))
    inchide(patron)
    assert ETICHETA_CAM in comp, comp
    return comp[ETICHETA_CAM]


def test_def_280_cam_pe_cartele_insumeaza_cam_ul_declarat(patron, firma_280):
    """280. Pașii: doi salariați cu normă întreagă, toată luna trecută: Ionescu Vasile 5.000 lei (CAM 112,50) și Popescu Elena 7.045 lei
    (CAM 158,51) -> Salariați -> statul lunii trecute -> „Compoziția netului” la fiecare: CAM 112,00 la Ionescu și 159,00 la Popescu
    (partea întreagă fiecăruia, iar leul rămas până la total merge la fracțiunea mai mare) -> Declarații -> D112 pe luna trecută: „fără
    erori”, CAM-ul declarat C4_ct = 271 = 112 + 159. Rotunjirea fiecărei cartele (113 + 159 = 272) ar da o sumă diferită de declarație și
    de notă. Temei: CF art.220^3 alin.(1) (cota 2,25%); D112 declară CAM-ul o dată, pe total (OPANAF 605/2026 anexa 2, secțiunea C4);
    împărțirea pe cartele e INTERPRETARE CU TEMEI (decizia Costin 06.10.2026 pct.11, `stat_plata_api._imparte_cam`)."""
    _stat_luna(patron, firma_280, luni_inapoi=1)
    cam_i = _cam_pe_cartela(patron, "Ionescu")
    cam_p = _cam_pe_cartela(patron, "Popescu")
    patron.captura("cartelele")
    brute = [Decimal(BRUT_IONESCU) * COTA_CAM, Decimal(BRUT_POPESCU) * COTA_CAM]
    total = int(sum(brute).quantize(Decimal("1"), rounding=ROUND_HALF_UP))   # Decimal + ROUND_HALF_UP (CLAUDE.md §10)
    assert total == 271, brute
    assert (cam_i, cam_p) == (Decimal("112.00"), Decimal("159.00")), (cam_i, cam_p)
    st = _d112_xml(patron, firma_280)
    c4 = _un(st["_angajator"], "angajatorC4")
    assert int(c4["C4_ct"]) == total == int(cam_i + cam_p), (c4, cam_i, cam_p)


# ── C43 — D300 rd.3.1: numai serviciile către clienți stabiliți în UE ──────────────────────────────────────────────────────────
@pytest.fixture()
def firma_c43():
    """O firmă NOUĂ numai pentru C43 (rd.3 / rd.3.1 nu au voie să vadă facturile altui test pe aceeași lună)."""
    for f in firma_noua():
        yield f


def _emite_serviciu_extern(e, firma, client, pret, zi):
    """DATE DE PORNIRE (declarate): factura de servicii cu locul prestării în afara României (cota 0, categoria „serviciu_extern”), pe
    ruta formularului „Emite factură” (`POST facturi/emite`, payload-ul ecranului, aceeași sesiune) — drumul pe ecran al aceleiași facturi
    e probat de `e2e_pozitii_validate.py::test_pozitie_f252_…`; aici se probează declarația."""
    corp = dict(client, linii=[{"descriere": PRODUS, "cantitate": 1, "um": "buc", "pret_unitar": pret, "cota_tva": 0, "cota_propusa": 0,
                                "articol_id": None, "categorie_tva": "serviciu_extern"}],
                moneda="RON", tip_operatiune="normal", bon_fiscal_nr=None, bon_fiscal_data=None, data_emitere=zi.isoformat(),
                data_scadenta=(zi + _dt.timedelta(days=30)).isoformat(), tip="factura")
    return _ok(_api_e(e, "POST", "/tenants/%d/facturi/emite" % firma["tenant_id"], corp), "factura %s" % client["tert_tara"])


#: Clientul din UE (Irlanda) și cel din afara UE (Statele Unite). Codurile fiscale străine nu au cifra de control românească
#: (`cere_cod_partener` cere numai un cod nevid); nu sunt CUI-uri românești.
CLIENT_IE = {"tert_nume": "Client Irlanda C43 Ltd", "tert_cui": "IE9999999ZZ", "tert_adresa": "1 Grand Canal Square", "tert_oras": "Dublin",
             "tert_tara": "IE"}
CLIENT_US = {"tert_nume": "Client Statele Unite C43 Inc", "tert_cui": "US123456789", "tert_adresa": "1 Market Street",
             "tert_oras": "San Francisco", "tert_tara": "US"}


def test_def_c43_serviciul_catre_client_din_afara_ue_numai_la_rd3(patron, firma_c43):
    """C43. D300: prestările de servicii către clienți din AFARA UE intrau și la rd.3.1, care cuprinde numai serviciile „prestate către
    persoane impozabile nestabilite în România, dar stabilite în Uniunea Europeană” (OPANAF 174/2026, instrucțiunile rd.3.1).
    Pașii: firma plătitoare lunar -> în luna încheiată, o factură de servicii 1.000,00 către clientul din Irlanda și una de 500,00 către
    clientul din Statele Unite, ambele 0% „serviciu_extern” (date de pornire pe ruta formularului, vezi `_emite_serviciu_extern`) -> notele
    lor validate (ruta butonului „Validează”) -> Declarații -> D300 -> luna -> „Continuă”: validat cu DUKIntegrator, fără erori; „Vezi
    XML-ul generat”: rd.3 (R3_1) = 1.500 (amândouă: locul prestării în afara României), rd.3.1 (R3_1_1) = 1.000 (numai clientul din UE),
    niciuna la rd.9 (21%). Înainte: R3_1_1 = 1.500."""
    f = firma_c43
    pregateste_firma(patron, f, platitor=True, regim_fiscal="profit")
    L = perioada_incheiata("lunar")
    zi = L.inceput.replace(day=12)
    ie = _emite_serviciu_extern(patron, f, CLIENT_IE, 1000.0, zi)
    us = _emite_serviciu_extern(patron, f, CLIENT_US, 500.0, zi)
    tari = dict(sql('SELECT id, tert_tara FROM "%s".facturi WHERE id = ANY(%%s)' % f["schema"], ([ie["factura_id"], us["factura_id"]],)))
    assert tari == {ie["factura_id"]: "IE", us["factura_id"]: "US"}, tari
    _valideaza_notele(patron, f, L.inceput, L.sfarsit)
    xml = _pas2(patron, f, "d300", L.an, luna=L.luna)
    patron.captura("d300_rd3_rd31")
    # CF art.278 alin.(2): locul prestării serviciilor către o persoană impozabilă e la beneficiar (ambii clienți: în afara României) ->
    # D300 rd.3 = 1.000 + 500; rd.3.1 = numai serviciile către clienții stabiliți în UE (OPANAF 174/2026, instrucțiunile rd.3.1) = 1.000
    assert (_atr(xml, "R3_1"), _atr(xml, "R3_1_1"), _atr(xml, "R9_1")) == ("1500", "1000", None), xml[:3000]


# ── C60 — registrul de casă pornește de la soldul de preluare ───────────────────────────────────────────────────────────────────
@pytest.fixture(scope="module")
def firma_verif_c60():
    for f in firma_noua():
        yield f


def test_def_c60_registrul_de_casa_porneste_de_la_preluare_si_de_la_notele_lunii_trecute(patron, firma_verif_c60):
    """C60 (găsită de Code la 406, lotul 9.2): „Registrul de casă pornea de la zero în fiecare lună: soldul de preluare și notele lunilor
    trecute nu intrau în soldul lunii”. Testul existent (`e2e_lot92.py::test_def_c60_…`) reface numai a doua jumătate (nota lunii trecute);
    soldul de PRELUARE nu-l reface niciun test al lui C60 (îl atinge numai `e2e_pilot_luna.py::test_pilot_25_…`, pe poziția F015).
    Pașii: firmă cu balanța de deschidere la sfârșitul lunii de dinaintea lunii trecute, 5311 debitor 1.250,00 (date de pornire: rândul
    în `solduri_initiale`, ca după importul balanței — `e2e_import_saga.py` probează importul pe ecran) + în luna trecută o ridicare de
    numerar 5311 = 581 de 300,00, validată -> Casă (luna curentă): „sold la început 1.550,00 lei” (preluarea + nota lunii trecute),
    „sold final 1.550,00 lei” -> „← luna” (luna trecută): „sold la început 1.250,00 lei” (soldul de preluare), „sold final 1.550,00 lei”.
    Temei: OMFP 2634/2015 anexa 2, Registrul de casă (cod 14-4-7A): „document de stabilire, la sfârșitul fiecărei zile, a soldului de
    casă” — soldul zilei pornește din soldul zilei de dinainte, nu din zero la început de lună."""
    f = firma_verif_c60
    pregateste_firma(patron, f)
    luna_trecuta = (AZI.replace(day=1) - _dt.timedelta(days=1)).replace(day=1)
    preluare = luna_trecuta - _dt.timedelta(days=1)          # ultima zi a lunii de dinaintea lunii trecute
    # date-de-pornire: rândul balanței de deschidere 5311, ca după importul balanței (importul pe ecran: e2e_import_saga.py)
    sql('INSERT INTO "%s".solduri_initiale (cont, sold_debitor, sold_creditor, data_referinta) VALUES (\'5311\', 1250, 0, %%s)'
        % f["schema"], (preluare,))
    _nota(f, luna_trecuta.replace(day=10).isoformat(), [{"debit": "5311", "credit": "581", "suma": 300}], "Ridicare C60 preluare",
          valideaza=True, document_ref="Cec C60P")
    patron.firma(f["nume"])
    _card_firma(patron, "casa", "#c-toggle")
    pg = patron.pg
    pg.wait_for_selector("#c-sold-inceput", timeout=20000)
    patron.captura("luna_curenta")
    assert pg.inner_text("#c-sold-inceput").strip() == "1.550,00 lei", pg.inner_text("#c-sold-inceput")
    assert pg.inner_text("#c-sold-final").strip() == "1.550,00 lei", pg.inner_text("#c-sold-final")
    pg.click("#c-prev")
    pg.wait_for_function("() => (document.querySelector('#c-sold-inceput') || {}).textContent === '1.250,00 lei'", timeout=20000)
    patron.captura("luna_trecuta")
    assert pg.inner_text("#c-sold-final").strip() == "1.550,00 lei", pg.inner_text("#c-sold-final")
