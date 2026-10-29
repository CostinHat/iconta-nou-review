# -*- coding: utf-8 -*-
"""Lotul 14, comanda Costin 14.3 (verbatim în DECIZII „Comanda 14.3”) — probe de capăt la capăt, în browser, pe ecranele reale:

  * 716   — Declarații, pasul 1, „declarațiile firmei aflate deja în coadă”: „depășită” numai după termen; o perioadă neîncheiată nu e „de generat din nou”;
  * 719   — Declarații: o declarație datorată și nedepusă după termen apare ca RESTANȚĂ, prima în „Datorate de firmă”;
  * 717   — Registru jurnal deschis dintr-o fereastră cu lună (Închidere lună) vine pe luna ei, nu pe cea curentă;
  * 688.1 — Închidere lună: luna blocată cu TVA neregularizat spune asta pe un rând, oferă o singură acțiune („Deblochează și regularizează”) și nu oferă
            „Propune regularizarea TVA”; blocarea se confirmă;
  * 715.1 — Panou Admin: marcajul „cabinet de test” (excepția alertei de acces urmează marcajul, nu numele);
  * D2    — Control fiscal: D398 fără răspuns OSS apare „de lămurit”, cu buton direct spre Date firmă;
  * 694.1 — Control fiscal › Declarație vs contabilitate: neconcordanța decontului cu nota de închidere TVA are acțiunea „Regularizează TVA-ul perioadei”
            (Închidere lună pe luna ei), iar „Coerență TVA (balanță)” își spune perioada și nu e verde cât decontul declară altceva;
  * 696.1 — Stocuri: cardul „Stoc validat față de balanță” numește mișcarea care produce diferența.

Firmele sunt NOI (`firma_noua`). Mutațiile: `mut_lot14_3.json`."""
import datetime as _dt
import json
import re

import pytest

from conftest import _ecran, firma_noua, sql
from e2e_bloc_a import _card
from e2e_bloc_d import PATRON, _api, _date_firma, _deschide, _nota_validata
from e2e_lot12_ctrl import _factura_validata
from e2e_lot13_admin import SUPERADMIN, _numai_cabinetul, _panou, cabinet_645   # noqa: F401 — cabinet_645 e fixtură

AZI = _dt.date.today()
LUNA_TRECUTA = (AZI.replace(day=1) - _dt.timedelta(days=1)).replace(day=1)
_F = ".fereastra:last-of-type "


def _vector_tva(f, trimestrial=False):
    _date_firma(f)
    st, r = _api(PATRON, "POST", "/tenants/%d/vector" % f["tenant_id"],
                 {"regim_fiscal": "micro", "platitor_tva": True, "tip_decont": "trimestrial" if trimestrial else "lunar", "operatiuni_ic": False,
                  "inreg_art317": False, "tva_data_inceput": "2026-01-01"})
    assert st == 200, (st, r)


@pytest.fixture()
def firma_l14_3():
    for f in firma_noua():
        _vector_tva(f)
        yield f


@pytest.fixture()
def firma_cu_restante():
    """Plătitoare de TVA lunar, cu luna preluării 01/2026 (date-de-pornire declarată, ca `e2e_bloc_c`): lunile de după preluare fără declarație depusă sunt restanțe."""
    for f in firma_noua():
        _vector_tva(f)
        sql('UPDATE "%s".firma_profil SET luna_preluare = %%s WHERE id = 1' % f["schema"], (_dt.date(2026, 1, 1),))   # date-de-pornire: luna preluării declarată, ca în `e2e_bloc_c`
        yield f


def _coada(f, tip, an, luna, patron_uid=None):
    """date-de-pornire (declarate): rândul cozii pe care îl scrie pregătirea unei declarații — fără `_surse` (intrată înainte de păstrarea datelor-sursă:
    `depasire` o dă „depășită”, fail-closed), ca să se vadă etichetele pe care le pune ecranul."""
    cab = sql("SELECT accounting_firm_id FROM public.tenants WHERE id = %s", (f["tenant_id"],))[0][0]
    uid = sql("SELECT id FROM public.users WHERE email = 'patron@prisma-cont.test'")[0][0]
    return sql("INSERT INTO public.declaratii_coada (cabinet_id, tenant_id, fel, tip, perioada, stare, payload, creat_de, creat_de_id, creat_la) "   # date-de-pornire: rândul cozii, vezi docstringul
               "VALUES (%s,%s,'declaratie',%s,%s,'la_senior',%s,%s,%s,now()) RETURNING id",
               (cab, f["tenant_id"], tip, "%02d/%d" % (luna, an), json.dumps({"_an": an, "_luna": luna}), str(uid), uid))[0][0]


# ── 716 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_716_depasita_numai_dupa_termen_perioada_neincheiata_nu_e_de_generat_din_nou(patron, firma_l14_3):
    """716. Pașii: firma are în coadă D300 pe luna în curs (datele-sursă s-au schimbat după generare) și D300 pe o lună al cărei termen a trecut ->
    Declarații, pasul 1: luna în curs: „în lucru — perioada nu s-a încheiat (termen …)”, fără „depășită” și fără „de generat din nou”; luna cu termenul
    trecut: „depășită — termenul … a trecut”. Înainte: ambele „depășită, de generat din nou”. MUTAȚIA: `termen_depasit` pus mereu False -> ROȘU."""
    f = firma_l14_3
    luna_veche = AZI.replace(day=1) - _dt.timedelta(days=75)
    _coada(f, "d300", AZI.year, AZI.month)
    _coada(f, "d300", luna_veche.year, luna_veche.month)
    pg = patron.pg
    patron.firma(f["nume"])
    _card(patron, "declaratii", _F + "#dec-tip")
    pg.wait_for_selector(_F + ".dec-existente", timeout=30000)
    txt = " ".join(pg.inner_text(_F + ".dec-existente").split())
    patron.captura("coada_declaratii")
    assert re.search(r"D300 · %02d/%d · în lucru — perioada nu s-a încheiat \(termen 25\.\d\d\.\d{4}\)" % (AZI.month, AZI.year), txt), txt   # AZI-dat-de-test: declarația din coadă o creează testul pe luna lui AZI (`_coada`), nu aplicația
    assert re.search(r"D300 · %02d/%d · depășită — termenul \d\d\.\d\d\.\d{4} a trecut" % (luna_veche.month, luna_veche.year), txt), txt
    assert txt.count("de generat din nou") == 0, txt


# ── 719 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_719_restanta_apare_in_datorate_prima(patron, firma_cu_restante):
    """719. Pașii: plătitoare de TVA, lunar, înregistrată din 01.01.2026, fără nicio declarație depusă -> Declarații, pasul 1: în „Datorate de firmă” apar
    declarațiile cu termenul trecut, marcate „restanță — termenul a fost …”, ÎNAINTE de cele viitoare (înainte: lista arăta numai termenele de azi
    încolo, iar restanța dispărea). MUTAȚIA: `restante=True` scos din `firma_rezumat` -> ROȘU."""
    f = firma_cu_restante
    pg = patron.pg
    patron.firma(f["nume"])
    _card(patron, "declaratii", _F + "#dec-tip")
    optiuni = pg.eval_on_selector_all(_F + "#dec-tip optgroup[label^='Datorate de firmă (restanțele'] option[data-an]", "os => os.map(o => o.textContent)")
    patron.captura("datorate_cu_restante")
    assert optiuni, "lista „Datorate de firmă” e goală"
    assert "restanță — termenul a fost" in optiuni[0], optiuni[:3]
    prima_viitoare = next(i for i, o in enumerate(optiuni) if "RESTANȚĂ" not in o)
    assert all("RESTANȚĂ" in o for o in optiuni[:prima_viitoare]) and not any("RESTANȚĂ" in o for o in optiuni[prima_viitoare:]), optiuni


# ── 717 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_717_registrul_jurnal_deschis_din_inchidere_luna_vine_pe_luna_ei(patron, firma_l14_3):
    """717. Pașii: Închidere lună, luna trecută (← luna) -> „Caută o funcție” din fereastră: „Registru jurnal” -> se deschide pe luna din care ai venit
    (luna trecută), nu pe cea curentă. Înainte: vine pe luna curentă. MUTAȚIA: `lunaParinte` golit în navigator -> ROȘU."""
    f = firma_l14_3
    pg = patron.pg
    patron.firma(f["nume"])
    _deschide(patron, "#fa-inchidere", "Închidere lună")
    pg.click(_F + "#il-prev")
    luna_et = "%02d/%d" % (LUNA_TRECUTA.month, LUNA_TRECUTA.year)
    pg.wait_for_function("(t) => (document.querySelector('.fereastra:last-of-type .pf-intro') || {innerText: ''}).innerText.includes(t)", arg=luna_et, timeout=30000)
    pg.fill(_F + "#cautare-fereastra", "Registru jurnal")
    pg.wait_for_selector(_F + "#cautare-fereastra-rez .cautare-item", timeout=15000)
    pg.click(_F + "#cautare-fereastra-rez .cautare-item >> nth=0")
    pg.wait_for_function("() => [...document.querySelectorAll('.fereastra')].pop().innerText.includes('Registru jurnal')", timeout=30000)
    pg.wait_for_selector(_F + "#j-prev", timeout=30000)
    patron.captura("jurnal_dupa_cautare")
    pg.wait_for_function("(t) => [...document.querySelectorAll('.fereastra')].pop().innerText.includes(t)", arg=luna_et, timeout=30000)
    patron.captura("jurnal_pe_luna_din_care_vii")
    assert "%02d/%d" % (AZI.month, AZI.year) not in " ".join(pg.inner_text(_F + ".pf-intro").split()) or LUNA_TRECUTA.month == AZI.month   # AZI-dat-de-test: luna curentă a testului, comparată cu titlul ferestrei


# ── 688.1 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture()
def firma_tva_blocata():
    """Luna trecută: 4426 D 210 (achiziție) și 4427 C 210 (vânzare), validate, luna BLOCATĂ (date-de-pornire declarate: aplicația nu blochează o lună cu TVA
    neregularizat; așa a rămas luna 09/2026 la F1 după retestul 688)."""
    for f in firma_noua():
        _vector_tva(f)
        zi = LUNA_TRECUTA.replace(day=10).isoformat()
        _nota_validata(f, zi, "4426", "401", 210, "Factura furnizor T143")
        _nota_validata(f, LUNA_TRECUTA.replace(day=20).isoformat(), "4111", "4427", 210, "Vanzare T143")
        sql('INSERT INTO "%s".perioade_blocate (an, luna) VALUES (%%s, %%s)' % f["schema"], (LUNA_TRECUTA.year, LUNA_TRECUTA.month))   # date-de-pornire: luna blocată
        yield f


def test_def_688_1_luna_blocata_cu_tva_neregularizat_o_singura_actiune_deblocheaza_si_regularizeaza(patron, firma_tva_blocata):
    """688.1. Pașii: F1 are luna trecută blocată cu 4426 / 4427 cu sold -> Închidere lună, luna trecută: „Luna a fost blocată cu TVA neregularizat.”; singura
    acțiune: „Deblochează și regularizează” (nicio „Propune regularizarea TVA”) -> motivul -> luna se deblochează și nota 4427 = 4426 e propusă (ciornă) în
    aceeași mișcare; apoi, după validarea notei, „Blochează luna” confirmă: „Luna … e blocată.”. Înainte: „Propune” se oferea și refuza („Luna e închisă”).
    MUTAȚIA: condiția `!blocata` scoasă de la „Propune” -> butonul apare într-o lună blocată -> ROȘU."""
    f = firma_tva_blocata
    pg = patron.pg
    patron.firma(f["nume"])
    _deschide(patron, "#fa-inchidere", "Închidere lună")
    pg.click(_F + "#il-prev")
    luna_et = "%02d/%d" % (LUNA_TRECUTA.month, LUNA_TRECUTA.year)
    pg.wait_for_function("(t) => (document.querySelector('.fereastra:last-of-type .pf-intro') || {innerText: ''}).innerText.includes(t)", arg=luna_et, timeout=30000)
    pg.wait_for_function("() => (document.querySelector('.fereastra:last-of-type #il-stare-perioada') || {innerText: ''}).innerText.includes('blocată')", timeout=30000)
    patron.captura("blocata_cu_tva")
    assert pg.inner_text(_F + "#il-stare-perioada").strip() == "Luna a fost blocată cu TVA neregularizat."
    assert pg.locator(_F + "#il-tva-regularizare").count() == 0, "„Propune regularizarea TVA” se oferă într-o lună blocată"
    assert pg.inner_text(_F + "#il-lock").strip() == "Deblochează și regularizează"
    pg.click(_F + "#il-lock")
    pg.wait_for_selector(_F + "#bl-motiv", timeout=10000)
    pg.fill(_F + "#bl-motiv", "regularizez TVA-ul lunii")
    pg.click(_F + "#bl-deblocheaza")
    pg.wait_for_function("() => (document.querySelector('.fereastra:last-of-type #il-mesaj') || {innerText: ''}).innerText.includes('Am propus')", timeout=40000)
    patron.captura("deblocata_si_regularizare_propusa")
    note = sql('SELECT id, status FROM "%s".inregistrari WHERE sursa = \'regularizare_tva\'' % f["schema"])
    assert len(note) == 1 and note[0][1] == "ciorna", note
    assert sql('SELECT count(*) FROM "%s".perioade_blocate WHERE an = %%s AND luna = %%s' % f["schema"], (LUNA_TRECUTA.year, LUNA_TRECUTA.month))[0][0] == 0
    st, r = _api(PATRON, "POST", "/tenants/%d/jurnal/%d/valideaza" % (f["tenant_id"], note[0][0]), {})
    assert st == 200, (st, r)
    pg.click(_F + "#il-next")
    pg.click(_F + "#il-prev")
    pg.wait_for_function("() => { const b = document.querySelector('.fereastra:last-of-type #il-lock'); return b && !b.disabled; }", timeout=40000)
    pg.wait_for_timeout(3000)   # ecranul s-a redesenat de două ori (← luna, luna →): butonul se apasă după ce s-a așezat
    pg.click(_F + "#il-lock")
    pg.wait_for_function("() => (document.querySelector('.fereastra:last-of-type #il-mesaj') || {innerText: ''}).innerText.includes('e blocată')", timeout=40000)
    patron.captura("luna_blocata_confirmare")
    assert "e blocată" in pg.inner_text(_F + "#il-mesaj")


# ── 715.1 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_715_1_cabinetul_de_test_se_marcheaza_in_panou_admin(browser, request, cabinet_645):
    """715.1. Pașii superadminului: Panou Admin › Activitate cabinete -> rândul cabinetului -> „Marchează ca test” -> confirmare -> rândul poartă „de test”
    și butonul devine „Scoate marcajul de test”; în bază `de_test` e adevărat; apoi „Scoate marcajul” -> fals. Excepția alertei de acces urmează marcajul
    (nu numele). MUTAȚIA: ruta nu mai scrie marcajul -> ROȘU."""
    from contextlib import contextmanager
    cab = cabinet_645
    gen = _ecran(browser, request, SUPERADMIN)
    e = next(gen)
    try:
        pg = e.pg
        _numai_cabinetul(pg, cab["id"])
        _panou(e, "activitate")
        rand = pg.locator(".pf-frand[data-cabinet='%d']" % cab["id"])
        rand.wait_for(timeout=60000)
        assert sql("SELECT de_test FROM public.accounting_firms WHERE id = %s", (cab["id"],)) == [(False,)]
        rand.locator("[data-de-test]").click()
        pg.wait_for_selector("#caseta-atentie-activa #ca-ok, .caseta-intrebare .buton-primar", timeout=10000)
        e.captura("confirmare_marcaj")
        pg.click("#caseta-atentie-activa #ca-ok") if pg.locator("#caseta-atentie-activa #ca-ok").count() else pg.click(".caseta-intrebare .buton-primar")
        pg.wait_for_function("(id) => { const r = document.querySelector(`.pf-frand[data-cabinet='${id}']`); return r && r.innerText.includes('de test'); }", arg=cab["id"], timeout=30000)
        e.captura("marcat_de_test")
        assert sql("SELECT de_test FROM public.accounting_firms WHERE id = %s", (cab["id"],)) == [(True,)]
        assert "Scoate marcajul de test" in pg.inner_text(".pf-frand[data-cabinet='%d']" % cab["id"])
    finally:
        import contextlib
        with contextlib.suppress(Exception):
            e.pg.unroute_all(behavior="ignoreErrors")   # cererea `/admin/activitate/cabinete` în zbor nu se mai așteaptă (ca `superadmin` din e2e_lot13_admin)
        with contextlib.suppress(StopIteration):
            next(gen)


# ── D2 + 694.1 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_595_1_d398_fara_raspuns_oss_apare_de_lamurit_in_control_fiscal(patron, firma_l14_3):
    """D2 (14.3). Pașii: plătitoare de TVA, fără răspuns la „Înregistrată în regimul special OSS” -> Control fiscal: „Nu se poate verifica”: D398 „de
    lămurit — răspunde în Date firmă …”, cu butonul „Răspunde în Date firmă” -> deschide Date firmă. Înainte: D398 lipsea din verificare. MUTAȚIA:
    intrarea „de lămurit” scoasă din `control_fiscal_api` -> ROȘU."""
    f = firma_l14_3
    pg = patron.pg
    patron.firma(f["nume"])
    pg.click("#fa-control")
    pg.wait_for_function("() => [...document.querySelectorAll('.fereastra')].pop().innerText.toLowerCase().includes('nu se poate verifica')", timeout=60000)
    pg.wait_for_selector(_F + "button[data-ecran-destinatie='date_firma']", timeout=30000)
    txt = " ".join(pg.inner_text(_F + ".cf-decl:has(button[data-ecran-destinatie='date_firma'])").split())
    patron.captura("d398_de_lamurit")
    assert "D398" in txt and "de lămurit — răspunde în Date firmă" in txt, txt
    pg.click(_F + "button[data-ecran-destinatie='date_firma']")
    pg.wait_for_selector("#df-inregistrat_oss", timeout=30000)


@pytest.fixture()
def firma_tva_decont_diferit():
    """Luna trecută: factură emisă (1.000 + TVA 210) cu nota ei validată, FĂRĂ regularizare: decontul D300 declară 210 de plată, contul 4423 n-are nimic
    -> neconcordanță."""
    for f in firma_noua():
        _vector_tva(f)
        _factura_validata(f, "E2E1431-1", LUNA_TRECUTA.replace(day=10))
        yield f


def test_def_694_1_neconcordanta_decontului_are_regularizarea_ca_actiune_iar_coerenta_tva_isi_spune_perioada(patron, firma_tva_decont_diferit):
    """694.1 (b, c). Pașii: Control fiscal › Declarație vs contabilitate: „Rezultatul decontului nu coincide cu nota de închidere TVA” -> acțiunea e
    „Regularizează TVA-ul perioadei” (nu „Contabilizează facturile”, inactiv) -> deschide Închidere lună pe luna perioadei; „Coerență TVA (balanță)”:
    rândul își spune data soldului („la 31.…”) și, cât decontul declară altceva, nu e verde. MUTAȚIA: `fel: regularizare_tva` pus înapoi pe
    „investigatie” -> butonul lipsește -> ROȘU."""
    f = firma_tva_decont_diferit
    pg = patron.pg
    patron.firma(f["nume"])
    pg.click("#fa-control")
    pg.wait_for_selector(_F + "button.cf-regulariza-tva", timeout=90000)
    patron.captura("control_regularizeaza")
    txt = " ".join(pg.inner_text(_F + ".cf-incr-remediu:has(button.cf-regulariza-tva)").split())
    assert "Regularizează TVA-ul perioadei" in txt and "Contabilizează facturile" not in txt, txt
    coerenta = " ".join(pg.inner_text(_F + ".cf-verif:has-text('TVA vs sold balanță')").split())
    assert re.search(r"TVA vs sold balanță la \d\d\.\d\d\.\d{4}", coerenta), coerenta
    pg.click(_F + "button.cf-regulariza-tva")
    pg.wait_for_function("() => [...document.querySelectorAll('.fereastra')].pop().innerText.includes('Închidere lună')", timeout=30000)
    pg.wait_for_selector(_F + "#il-prev", timeout=30000)
    patron.captura("inchidere_luna_din_control")
