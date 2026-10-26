# -*- coding: utf-8 -*-
"""Lotul 13 (comanda Costin 13.1), salarizarea, pașii contabilului pe aplicația din index, pe baza de TEST: 671 (pontajul arată concediul
medical din certificat; regula unică), 672 (tichetul de masă la un salariat existent, „+ masă”), 677 (statul compact, fereastra
salariatului, compoziția pe trei coloane cu aceleași cifre), 678 (pontajul = calendar), 679 (suma orelor suplimentare calculată), 673 /
675 / 676 (fereastră nouă pentru fiecare acțiune; același set de butoane; listele scurte = butoane), 670 b (excedentul de diurnă în stat și
D112), C174 (E3_8 cu tichetele, D112 fără erori).

Date de pornire: fiecare test își face firma sintetică și salariatul pe ruta salariaților (`e2e_lot11_s9._firma_cu_salariat`); certificatul
medical și tichetul pe rutele aplicației. Excepția declarată: excedentul de diurnă (670 b) îl scrie decontul final al subagentului
operațiunilor (`core.diurna_salariat.adauga_excedent`, integrat de sesiunea principală) — aici rândul lui se scrie cu aceeași funcție,
în locul decontului. CNP-urile au cifra de control calculată (`e2e_bloc_b._cnp`)."""
import datetime
from decimal import ROUND_HALF_UP, Decimal

import pytest

from conftest import _scoate_firmele_e2e, sql
from e2e_bloc_d import LUNA_TRECUTA, PATRON, _api
from e2e_bloc_d import _stat as _stat_luna
from e2e_lot11_s9 import _d112_xml, _firma_cu_salariat, _singurul, _un
from e2e_lot13_sal_ajutor import _F, alege, buton, coloane, deschide_salariat, inchide, text_compozitie


def _zile_lucratoare(de, pana):
    st, r = _api(PATRON, "GET", "/util/zile-lucratoare?start=%s&end=%s" % (de.isoformat(), pana.isoformat()))
    assert st == 200, (st, r)
    return int(r["zile"])


def _ultima_zi(d):
    return (d.replace(day=28) + datetime.timedelta(days=4)).replace(day=1) - datetime.timedelta(days=1)


def _marti_miercuri_joi():
    """Prima marți a lunii trecute + miercurea și joia ei (trei zile lucrătoare, fără sărbătoare legală)."""
    d = LUNA_TRECUTA.replace(day=1)
    while True:
        while d.weekday() != 1:
            d += datetime.timedelta(days=1)
        if _zile_lucratoare(d, d + datetime.timedelta(days=2)) == 3:
            return [d, d + datetime.timedelta(days=1), d + datetime.timedelta(days=2)]
        d += datetime.timedelta(days=7)


def _certificat(f, de, pana, zile):
    st, r = _api(PATRON, "POST", "/tenants/%d/salariati/%d/concedii" % (f["tenant_id"], f["salariat_id"]), {
        "serie": "CCMAM", "numar": "1234567", "cod": "01", "data_acordare": de.isoformat(), "data_inceput": de.isoformat(),
        "data_sfarsit": pana.isoformat(), "zile_cm": zile, "venituri_6_luni": 30000, "zile_6_luni": 125, "este_continuare": False,
        "spitalizare": False, "program_national": False, "an": de.year, "luna": de.month})
    assert st == 200 and r.get("ok"), (st, r)


def _stat_api(f):
    st, r = _api(PATRON, "GET", "/tenants/%d/stat-plata?an=%d&luna=%d" % (f["tenant_id"], LUNA_TRECUTA.year, LUNA_TRECUTA.month))
    assert st == 200, (st, r)
    return {x["id"]: x for x in r["stat"]}


@pytest.fixture
def firma_sal():
    f = _firma_cu_salariat("L13S")
    try:
        yield f
    finally:
        _scoate_firmele_e2e(f["tenant_id"])


# ── 671 + 678: pontajul = calendar; concediul medical vine marcat din certificat ─────────────────────────────────────────────────
def test_def_671_pontajul_arata_concediul_medical_din_certificat(patron, firma_sal):
    """671. Pașii: certificat cod 01, marți–joi din luna trecută -> statul lunii trecute: rândul salariatului „N−3 din N” zile lucrate și
    semnul „CM” -> fereastra salariatului -> „Pontaj”: cele trei zile sunt „concediu medical”, inactive, cu motivul (certificatul CCMAM
    1234567); restul „prezent”; regula „ce schimbă pontajul” e aceeași frază ca în statul de plată (`pontaj.REGULA_PONTAJ`). Înainte:
    zilele certificatului apăreau „prezent” (22 prezență, 0 concediu), iar textele se contraziceau."""
    from core import pontaj
    zile = _marti_miercuri_joi()
    _certificat(firma_sal, zile[0], zile[-1], 3)
    nzl = _zile_lucratoare(LUNA_TRECUTA.replace(day=1), _ultima_zi(LUNA_TRECUTA))
    pg = patron.pg
    _stat_luna(patron, firma_sal, luni_inapoi=1)
    rand = pg.locator(_F + "#sp-tabel tbody tr.sp-rand").first
    txt = " ".join(rand.inner_text().split())
    assert ("%d din %d" % (nzl - 3, nzl)) in txt and "CM" in txt, txt
    deschide_salariat(patron)
    buton(patron, "pontaj")
    pg.wait_for_selector(_F + "#pj-calendar", timeout=20000)
    for z in zile:
        cel = pg.locator(_F + "#pj-calendar button[data-zi='%s']" % z.isoformat())
        assert cel.is_disabled() and "concediu medical" in cel.inner_text(), cel.inner_text()
        assert "CCMAM 1234567" in cel.get_attribute("title"), cel.get_attribute("title")
    assert pontaj.REGULA_PONTAJ in patron.fereastra()
    sumar = " ".join(pg.inner_text(_F + ".cf-sumar").split())
    assert ("%d zile de prezență" % (nzl - 3)) in sumar and "3 zile de concediu medical" in sumar, sumar
    patron.captura("pontajul_cu_concediul_medical")
    # pe o zi a certificatului nu se poate marca altceva (serverul refuză oricum: `pontaj.seteaza`)
    st, r = _api(PATRON, "PUT", "/tenants/%d/salariati/%d/pontaj" % (firma_sal["tenant_id"], firma_sal["salariat_id"]),
                 {"zi": zile[1].isoformat(), "stare": "concediu_odihna"})
    assert st == 422 and "certificat" in str(r), (st, r)


def test_def_678_pontajul_e_calendar_si_se_apasa_doar_zilele_altfel(patron, firma_sal):
    """678. Pașii: fereastra salariatului -> „Pontaj”: un calendar luni–vineri pe săptămâni, fără liste derulante; implicit „prezent”;
    „Marchează ca: concediu de odihnă” -> apăs o zi -> ziua devine „concediu de odihnă” (rândul în pontaj) -> o apăs din nou -> „prezent”.
    Înainte: 22 de liste derulante, cu derulare."""
    pg = patron.pg
    _stat_luna(patron, firma_sal, luni_inapoi=1)
    deschide_salariat(patron)
    buton(patron, "pontaj")
    pg.wait_for_selector(_F + "#pj-calendar", timeout=20000)
    capete = [x.strip() for x in pg.locator(_F + "#pj-calendar thead th").all_inner_texts()]
    assert capete == ["Luni", "Marți", "Miercuri", "Joi", "Vineri"], capete
    # [676] nicio listă derulantă: fiecare listă scurtă e sursa butoanelor alăturate (mecanismul comun, `select.alegere-sursa`)
    assert pg.locator(_F + "select:not(.alegere-sursa)").count() == 0 and pg.locator(_F + ".alegere-butoane").count() > 0
    zi = _marti_miercuri_joi()[0].isoformat()
    cel = _F + "#pj-calendar button[data-zi='%s']" % zi
    assert "prezent" in pg.inner_text(cel)
    alege(patron, "pj-marcaj", "concediu_odihna")
    pg.click(cel)
    pg.wait_for_function("(s) => (document.querySelector(s) || {innerText: ''}).innerText.includes('concediu de odihnă')", arg=cel,
                         timeout=20000)
    patron.captura("ziua_marcata")
    assert sql('SELECT stare FROM "%s".pontaj WHERE zi = %%s' % firma_sal["schema"], (zi,)) == [("concediu_odihna",)]
    pg.click(cel)
    pg.wait_for_function("(s) => (document.querySelector(s) || {innerText: ''}).innerText.includes('prezent')", arg=cel, timeout=20000)
    assert sql('SELECT count(*) FROM "%s".pontaj' % firma_sal["schema"]) == [(0,)]


# ── 672 + 675: „+ masă” ────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_672_tichetul_de_masa_se_pune_la_salariatul_existent(patron, firma_sal):
    """672. Pașii: salariatul existent (fără tichete) -> fereastra lui -> „+ masă” (lângă „+ vacanță”) -> 40 -> „Salvează” -> confirmarea
    în fereastra salariatului, „Din ce se calculează”: „Tichet de masă 40,00 lei pe zi lucrată”; fișa are 40. Înainte: câmpul exista
    numai la „Salariat nou”."""
    pg = patron.pg
    _stat_luna(patron, firma_sal, luni_inapoi=1)
    deschide_salariat(patron)
    chei = pg.eval_on_selector_all(_F + "#ss-butoane button", "bs => bs.map(b => Object.keys(b.dataset).find(k => k !== 'nume' && k !== 'actiune'))")
    assert chei[chei.index("masa") + 1] == "vac", chei
    buton(patron, "masa")
    pg.wait_for_selector(_F + "#masa-input", timeout=20000)
    pg.fill(_F + "#masa-input", "40")
    pg.click(_F + "#masa-save")
    pg.wait_for_selector(_F + "#ss-msg.msg-ok", timeout=30000)
    assert "tichete de masă de 40,00 lei pe zi lucrată" in pg.inner_text(_F + "#ss-msg"), pg.inner_text(_F + "#ss-msg")
    assert "40,00 lei pe zi lucrată" in pg.inner_text(_F + "#ss-calcul")
    patron.captura("tichetul_pus")
    assert sql('SELECT tichet_masa_valoare FROM "%s".salariati' % firma_sal["schema"]) == [(Decimal("40"),)]


# ── 677: statul compact, fereastra salariatului, compoziția pe trei coloane ─────────────────────────────────────────────────────────
def test_def_677_statul_compact_si_compozitia_pe_trei_coloane(patron, firma_sal):
    """677. Pașii: certificat cod 01 (3 zile) -> statul lunii trecute: tabelul (Salariat, Zile lucrate, Brut, Net de plată, Cost angajator,
    Semnele lunii), rândul de total, căutarea deasupra -> rândul -> fereastra salariatului: Venituri / Rețineri / Rezultat; indemnizația CM
    o singură dată, cu brut și net; fără „Zile de concediu medical: 3”; veniturile în bani − reținerile = netul de plată, aceleași cifre ca
    statul (ruta). Înainte: carduri unul sub altul, compoziția pliată sub „▸ Compoziția netului”."""
    zile = _marti_miercuri_joi()
    _certificat(firma_sal, zile[0], zile[-1], 3)
    s = _stat_api(firma_sal)[firma_sal["salariat_id"]]
    pg = patron.pg
    _stat_luna(patron, firma_sal, luni_inapoi=1)
    capete = [" ".join(x.split()) for x in pg.locator(_F + "#sp-tabel thead th").all_inner_texts()]
    assert capete == ["Salariat", "Zile lucrate", "Brut", "Net de plată", "Cost angajator", "Semnele lunii"], capete
    total = " ".join(pg.inner_text(_F + "#sp-tabel tfoot").split())
    assert total.startswith("Total · 1 salariat") and ("%s" % _ro(s["net_de_plata"])) in total, total
    pg.fill(_F + "#sp-cauta", "nimeni")
    assert pg.locator(_F + "#sp-tabel tbody tr.sp-rand:visible").count() == 0
    pg.fill(_F + "#sp-cauta", "popescu")
    assert pg.locator(_F + "#sp-tabel tbody tr.sp-rand:visible").count() == 1
    patron.captura("statul_compact")
    deschide_salariat(patron)
    c = coloane(patron)
    q = lambda v: Decimal(str(v)).quantize(Decimal("0.01"))   # noqa: E731
    assert q(c["Venituri în bani"][0]) - q(c["Total rețineri"][0]) == q(s["net_de_plata"]), c
    assert c["Net de plată"][0] == s["net_de_plata"] and c["Indemnizație concediu medical"] == [s["cm_brut"], s["cm_net"]], (c, s)
    assert c["CAS (25%)"][0] == s["cas"] and c["reținut din indemnizație: CAS (25%)"][0] == s["cm_cas"], c
    t = text_compozitie(patron)
    assert "Zile de concediu medical" not in t and t.count("Indemnizație concediu medical") == 1, t
    assert ("%d zile lucrate din" % (s["zile_lucratoare_luna"] - 3)) in t, t
    assert [x.strip() for x in pg.locator(_F + "#ss-compozitie thead th:first-child").all_inner_texts()] == ["Venituri", "Rețineri", "Rezultat"]
    patron.captura("fereastra_salariatului")


def _ro(v):
    return "{:,.2f}".format(Decimal(str(v))).replace(",", "X").replace(".", ",").replace("X", ".")


# ── 673 / 675 / 676: aceleași butoane, fereastră nouă, liste scurte = butoane ─────────────────────────────────────────────────────
def test_def_675_acelasi_set_de_butoane_si_fereastra_noua_pentru_fiecare_actiune(patron, firma_sal):
    """673 / 675 / 676. Pașii: al doilea salariat -> fereastra fiecăruia: aceleași butoane, în aceeași ordine; „De verificat” inactiv cu
    motivul; „Salariu” se deschide într-o fereastră nouă (traseul arată fereastra salariatului), iar „Date de calcul” n-are liste derulante
    scurte (Da / Nu, norma = butoane alăturate, nimic ales fără valoare salvată)."""
    st, r = _api(PATRON, "POST", "/tenants/%d/salariati" % firma_sal["tenant_id"], {
        "nume": "Ionescu", "prenume": "Vasile", "cnp": __import__("e2e_bloc_b")._cnp("186020240123"), "data_angajare": "2026-01-05",
        "tip_norma": "intreaga", "ore_zi": 8, "salariu_brut": 6000, "persoane_intretinere": 0, "scutit_contrib_minim": False,
        "functie_baza": True, "cor": "331302"})
    assert st == 200, (st, r)
    pg = patron.pg
    _stat_luna(patron, firma_sal, luni_inapoi=1)
    seturi = []
    for nume in ("Popescu", "Ionescu"):
        deschide_salariat(patron, nume)
        seturi.append(pg.eval_on_selector_all(_F + "#ss-butoane button", "bs => bs.map(b => b.textContent.replace(/[✓⚠]/g, '').trim())"))
        verif = pg.locator(_F + "#ss-butoane [data-verif]")
        # [675] inactiv cu motivul (`atributeInactiv`, DS cap.1): rămâne focusabil, motivul la trecerea cu mouse-ul
        assert verif.get_attribute("aria-disabled") == "true" and verif.get_attribute("title"), verif.get_attribute("title")
        inchide(patron)
    assert seturi[0] == seturi[1] and seturi[0][6:11] == ["+ masă", "+ vacanță", "+ cadou", "+ cultural", "+ creșă"], seturi
    deschide_salariat(patron, "Popescu")
    buton(patron, "salariu")
    pg.wait_for_selector(_F + "#salariu-input", timeout=20000)
    assert "Popescu" in pg.inner_text(_F + ".fereastra-fir"), pg.inner_text(_F + ".fereastra-fir")
    inchide(patron)
    buton(patron, "calcul")
    pg.wait_for_selector(_F + ".alegere-butoane:has(+ #ed-fbaza)", timeout=20000)
    # [676] nicio listă derulantă: fiecare listă scurtă e sursa butoanelor alăturate (mecanismul comun, `select.alegere-sursa`)
    assert pg.locator(_F + "select:not(.alegere-sursa)").count() == 0 and pg.locator(_F + ".alegere-butoane").count() > 0
    pg.wait_for_function("() => document.querySelector('.fereastra:last-of-type #ed-fbaza').value === 'true'", timeout=20000)
    assert pg.get_attribute(_F + ".alegere-butoane:has(+ #ed-fbaza) button[data-valoare='true']", "aria-checked") == "true"
    patron.captura("date_de_calcul")


# ── 679: suma orelor suplimentare se calculează ─────────────────────────────────────────────────────────────────────────────────────
def test_def_679_suma_orelor_suplimentare_se_calculeaza(patron, firma_sal):
    """679. Pașii: fereastra salariatului -> „Prime, sporuri, ore supl.” -> „Ore suplimentare”: se cer orele și sporul (etichete întregi,
    nu texte tăiate), suma nu se cere -> 10 ore, 75% -> „Adaugă”: rândul arată „10 ore × <tarif> lei × 175%” și suma = 5.000 / (zile
    lucrătoare × 8) × 10 × 1,75, la ban (Codul muncii art.123 alin.(1)-(2))."""
    nzl = _zile_lucratoare(LUNA_TRECUTA.replace(day=1), _ultima_zi(LUNA_TRECUTA))
    asteptat = (Decimal(5000) / Decimal(nzl * 8) * 10 * Decimal("1.75")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    pg = patron.pg
    _stat_luna(patron, firma_sal, luni_inapoi=1)
    deschide_salariat(patron)
    buton(patron, "elem")
    pg.wait_for_selector(_F + ".alegere-butoane:has(+ #el-tip)", timeout=20000)
    alege(patron, "el-tip", "ore_suplimentare")
    assert pg.locator(_F + "#el-suma").is_visible() is False
    assert pg.inner_text(_F + "#el-ore-camp .camp-eticheta").startswith("Orele suplimentare")
    assert pg.inner_text(_F + "#el-spor-camp .camp-eticheta").startswith("Sporul din contract (%)")
    pg.fill(_F + "#el-denumire", "ore suplimentare")
    pg.fill(_F + "#el-ore", "10")
    pg.fill(_F + "#el-spor", "75")
    pg.click(_F + "#el-adauga")
    pg.wait_for_selector(_F + "#el-tabel", timeout=30000)
    rand = " ".join(pg.inner_text(_F + "#el-tabel tbody tr").split())
    patron.captura("orele_calculate")
    assert "10 ore ×" in rand and "× 175%" in rand and (_ro(asteptat) + " lei") in rand, (rand, asteptat)
    assert sql('SELECT suma, spor_procent FROM "%s".elemente_salariale' % firma_sal["schema"]) == [(asteptat, Decimal("75.00"))]


# ── 670 b: excedentul de diurnă în stat și în D112 ──────────────────────────────────────────────────────────────────────────────────
def test_def_670_b_excedentul_de_diurna_e_venit_salarial(patron, firma_sal):
    """670 (b). Pașii: decontul final lasă 300 lei excedent de diurnă pe luna trecută (`diurna_salariat.adauga_excedent`, apelat de
    decont) -> statul: brut 5.300, fereastra salariatului: „Excedent de diurnă · plătit prin decont, impozabil” -> Declarații -> D112:
    „fără erori”, E3_8 = 5.300, E3_59 = E3_52 = 300 (OPANAF 605/2026 anexa 2, E.3 rândul 8.2.1), B4_7 = 5.300 (CF art.139 alin.(1) lit.j)."""
    from conftest import _db
    from core import diurna_salariat as ds
    with _db().get_conn() as conn, conn.cursor() as cur:
        ds.adauga_excedent(cur, firma_sal["schema"], firma_sal["salariat_id"], LUNA_TRECUTA.year, LUNA_TRECUTA.month, Decimal("300"),
                           "e2e:decont:1", "decont final, deplasare internă")
    pg = patron.pg
    _stat_luna(patron, firma_sal, luni_inapoi=1)
    rand = " ".join(pg.locator(_F + "#sp-tabel tbody tr.sp-rand").first.inner_text().split())
    assert "5.300,00" in rand, rand
    deschide_salariat(patron)
    assert coloane(patron)["Excedent de diurnă"][0] == 300
    assert "plătit prin decont, impozabil" in text_compozitie(patron)
    patron.captura("excedentul_in_stat")
    a = _singurul(_d112_xml(patron, firma_sal))
    e3, b4 = _un(a, "asiguratE3"), _un(a, "asiguratB4")
    assert (e3["E3_8"], e3["E3_59"], e3["E3_52"], b4["B4_7"]) == ("5300", "300", "300", "5300"), (e3, b4)


# ── C174: E3_8 cuprinde tichetele de masă ──────────────────────────────────────────────────────────────────────────────────────────
def test_def_c174_e3_8_cuprinde_tichetele_de_masa(patron, firma_sal):
    """C174 (decizia Costin 13.1 pct.4: „verifică la sursă, în instrucțiunile D112 în vigoare, dacă tichetele de masă intră în E3_8”).
    OPANAF 605/2026 anexa 2, E.3: „Rândul 8 «Total venit brut, din care:»”, cu „Rândul 8.3.1 «Contravaloarea tichetelor de masă»”. Pașii:
    tichet 40 lei, pontaj confirmat -> Declarații -> D112 pe luna trecută: „fără erori”, E3_8 = E1_1 = salariul + tichetele, E3_10 =
    tichetele. Înainte: E3_8 = salariul, fără tichete."""
    nzl = _zile_lucratoare(LUNA_TRECUTA.replace(day=1), _ultima_zi(LUNA_TRECUTA))
    tid, sid = firma_sal["tenant_id"], firma_sal["salariat_id"]
    assert _api(PATRON, "PUT", "/tenants/%d/salariati/%d" % (tid, sid), {"tichet_masa_valoare": 40})[0] == 200
    st, r = _api(PATRON, "POST", "/tenants/%d/pontaj/confirma" % tid, {"an": LUNA_TRECUTA.year, "luna": LUNA_TRECUTA.month})
    assert st == 200, (st, r)
    a = _singurul(_d112_xml(patron, firma_sal))
    e3, e1 = _un(a, "asiguratE3"), _un(a, "asiguratE1")
    assert (int(e3["E3_10"]), int(e3["E3_8"]), int(e1["E1_1"])) == (40 * nzl, 5000 + 40 * nzl, 5000 + 40 * nzl), (e3, e1)
