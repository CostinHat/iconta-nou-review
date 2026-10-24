# -*- coding: utf-8 -*-
"""Lotul 12, comanda Costin 12.1 (verbatim în DECIZII „Comanda 12.1”), pachetul `coada` — notele automate, coada de validare și
ecranele ei. Fiecare test reface pașii contabilului pe aplicația din index, pe baza de TEST, pe firma nouă a fișierului (`firma_e2e`)
sau pe un cabinet nou (52: cifrele cabinetului nu depind de ce lasă alte rulări în cabinetul de test).

  * 499 (fost N17): mesajul de respingere nu se mai termină cu punct dublu — motivul încheiat de om („Lipsește factura.”) nu mai
    primește încă un punct, nici pe nota din Registrul jurnal, nici pe NIR-ul din „NIR-urile lunii” (`motivInFraza`).
  * 500 (fost N18): totalizarea Registrului jurnal numește notele fără document justificativ fără „derivabil” (cuvânt de programator).
  * 92: „Respinge” din dialog rămâne roșu plin și activ după ce s-a scris motivul (cazul descris de Costin: „cu motivul completat”).
  * 52: cardul „De validat” și fereastra numără EXACT notele de validat: 3 -> 2 după o validare -> 1 după o respingere.
  * C (nou, clasa lui 80 — „validarea contării NU a validat ieșirea din stoc”): „Validează” pe contarea facturii, în Registrul jurnal,
    validează și ieșirea din stoc a aceleiași facturi, ca în coadă.

Temei: N/A — texte de ecran și reguli de produs (CLAUDE.md §9)."""
import contextlib
import datetime as _dt
import io as _io
import os
import re
import time as _t

import pytest

from conftest import _ecran, cui_cu_control, sql
from e2e_bloc_a import cabinet_separat, cont_asistent
from e2e_bloc_b import (_articol_cu_stoc, _asigura_serie, _client, _coada_nota, _de_validat, _emitere, _firma_gata, _jurnal, _linie,
                        _nota_prin_ecran, _respinge_din_coada, ana, ana_cont)  # noqa: F401 — fixture (ana, ana_cont)
from e2e_bloc_d import _nir_lista, _nir_respins, _stocuri, firma_cv  # noqa: F401 — fixture (firma_cv)

AZI = _dt.date.today()
LUNA = (AZI.year, AZI.month)
ecran_cont = contextlib.contextmanager(_ecran)


def _tag():
    return int(_t.time() * 1000) % 1000000


# ── 499 — punctul dublu după motivul respingerii ─────────────────────────────────────────────────────────────────────────────
def test_def_499_motivul_incheiat_de_om_nu_primeste_al_doilea_punct_pe_nota(ana, patron, firma_e2e):
    """499. Coadă: mesajul de respingere se termină cu punct dublu.
    Pașii: Ana scrie o notă (intră la validare) -> contabilul-șef: „De validat” -> „Respinge”, motivul „Lipsește factura furnizorului N.”
    (încheiat cu punct, cum scrie omul) -> Ana deschide Registrul jurnal: rândul spune „Respinsă la validare: Lipsește factura
    furnizorului N. Corecteaz-o, apoi trimite-o din nou.” — un singur punct, fără „..”."""
    _firma_gata(firma_e2e)
    desc = "E2E 499 servicii %d" % _tag()
    motiv = "Lipsește factura furnizorului %d." % _tag()
    nid = _nota_prin_ecran(ana, firma_e2e, desc, AZI.isoformat(), luna=LUNA)
    assert (_coada_nota(firma_e2e, nid) or (None, None))[1] == "la_senior"
    _respinge_din_coada(patron, firma_e2e, desc, motiv)
    _jurnal(ana, firma_e2e, LUNA)
    rand = ana.pg.locator(".pf-frand[data-nota-id='%d']" % nid)
    rand.scroll_into_view_if_needed()
    txt = " ".join(rand.inner_text().split())
    ana.captura("nota_respinsa")
    assert "Respinsă la validare: %s Corecteaz-o, apoi trimite-o din nou." % motiv in txt, txt
    assert ".." not in txt, txt


def test_def_499_motivul_incheiat_de_om_nu_primeste_al_doilea_punct_pe_nir(patron, firma_cv):
    """499 (același defect, alt ecran). Pașii: NIR-ul asistentului e respins în coadă cu motivul „Lipsește avizul N.” -> Stocuri ->
    „NIR-urile lunii”: rândul spune „Respins la validare: Lipsește avizul N. …” — un singur punct."""
    numar = "L12N%d" % (_tag() % 10000)
    motiv = "Lipsește avizul %s." % numar
    _nir_respins(firma_cv, numar, "Marfa %s" % numar, motiv)
    _stocuri(patron, firma_cv)
    txt = " ".join(_nir_lista(patron).split())
    patron.captura("nir_respins")
    assert "Respins la validare: %s " % motiv in txt, txt
    assert ".." not in txt, txt


# ── 500 — „Fără document justificativ derivabil” ─────────────────────────────────────────────────────────────────────────────
@pytest.fixture()
def firma_500():
    from conftest import firma_noua
    for f in firma_noua():
        yield f


def test_def_500_totalizarea_jurnalului_numeste_notele_fara_document_fara_derivabil(patron, firma_500):
    """500. Registru jurnal: formularea „Fără document justificativ derivabil”.
    Pașii: firmă nouă -> Registru jurnal -> „+ Notă nouă” fără document justificativ -> Salvează. Bara de totaluri de jos spune „Note
    fără document justificativ (nici document scris, nici factură legată)” cu cifra 1 — fără „derivabil”."""
    _firma_gata(firma_500)
    desc = "E2E 500 chirie %d" % _tag()
    _nota_prin_ecran(patron, firma_500, desc, AZI.isoformat(), luna=LUNA, doc="")
    pg = patron.pg
    rand = pg.locator(".fd-tot-rand", has_text="Note fără document justificativ")
    rand.wait_for(timeout=20000)
    patron.captura("totaluri")
    assert " ".join(rand.inner_text().split()) == "Note fără document justificativ (nici document scris, nici factură legată) 1", \
        rand.inner_text()
    assert "derivabil" not in patron.fereastra().lower()


# ── 92 — „Respinge” cu motivul completat ─────────────────────────────────────────────────────────────────────────────────────
def test_def_92_respinge_ramane_rosu_plin_si_activ_cu_motivul_completat(ana, patron, firma_e2e):
    """92. Coadă: „Respinge” pare dezactivat cu motivul completat.
    Pașii: Ana scrie o notă -> contabilul-șef: „De validat” -> „Respinge” pe ea -> scrie motivul în dialog: butonul „Respinge” al
    dialogului are aceleași culori ca „Respinge” de pe card (roșu plin, text alb), opacitate 1, și e activ."""
    _firma_gata(firma_e2e)
    desc = "E2E 92 motiv %d" % _tag()
    _nota_prin_ecran(ana, firma_e2e, desc, AZI.isoformat(), luna=LUNA)
    pg = patron.pg
    _de_validat(patron)
    card = pg.locator("#val-note .val-card").filter(has_text=firma_e2e["nume"]).filter(has_text=desc).first
    card.wait_for(timeout=20000)
    stil = "(e) => { const s = getComputedStyle(e); return [s.backgroundColor, s.color, s.opacity]; }"
    pe_card = card.locator(".val-respinge").evaluate(stil)
    card.locator(".val-respinge").click()
    pg.wait_for_selector("#dlg-input", timeout=10000)
    pg.locator("#dlg-input").press_sequentially("lipsește contractul", delay=20)   # tastat, ca omul (fiecare literă)
    pg.wait_for_timeout(300)
    in_dialog = pg.locator("#dlg-ok").evaluate(stil)
    patron.captura("motiv_completat")
    assert pe_card[2] == "1" and in_dialog == pe_card, "dialog %s ≠ card %s" % (in_dialog, pe_card)
    assert pg.locator("#dlg-ok").is_enabled()
    pg.click("#dlg-anuleaza")


# ── 52 — cifrele exacte ale cardului și ferestrei ────────────────────────────────────────────────────────────────────────────
@contextlib.contextmanager
def _cabinet_cu_firma():
    """Un cabinet nou (administratorul validează), cu o firmă a lui și un asistent „Poate pregăti” alocat ei; scoase la final."""
    from conftest import _scoate_firmele_e2e
    from core import db, tenant_provisioning as tp
    from curatenie import PREFIX_FIRMA
    rad = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sql_t = _io.open(os.path.join(rad, "tenant_template.sql"), encoding="utf-8").read()
    with cabinet_separat() as cab:
        nume = "%s 52 %d SRL" % (PREFIX_FIRMA, _tag())
        with db.get_conn() as c:
            r = tp.provision_tenant(c, nume, cui_cu_control(70000000 + _tag()), cab["firm_id"], cab["user_id"], sql_t)
            c.commit()
        f = {"tenant_id": r["tenant_id"], "schema": r["schema_name"], "nume": nume, "cabinet_id": cab["firm_id"]}
        try:
            with cont_asistent(firme=(f["tenant_id"],), cabinet=cab["firm_id"], eticheta="c52") as a:
                try:
                    yield cab, f, a
                finally:   # rândurile care numesc conturile, înainte ca ele să fie scoase
                    sql("DELETE FROM public.declaratii_coada WHERE tenant_id = %s", (f["tenant_id"],))
                    sql("DELETE FROM public.notificari WHERE user_id = ANY(%s)", ([a["id"], cab["user_id"]],))
        finally:
            _scoate_firmele_e2e(f["tenant_id"])


def _cifra_card(e):
    pg = e.pg
    e.acasa()
    pg.wait_for_function("() => /not[ăe] de validat/.test((document.querySelector(\".cab-card-sinteza[data-cheie='validat']\") || {})"
                         ".innerText || '')", timeout=20000)
    t = pg.inner_text(".cab-card-sinteza[data-cheie='validat']")
    return int(re.search(r"(\d+)\s+not[ăe] de validat", t).group(1)), t


def _cifre_fereastra(e):
    pg = e.pg
    pg.click("button.cab-card:has([data-cheie='validat'])")
    titlu_el = pg.locator("#val-note .cf-grup-titlu", has_text="Note de validat (")
    titlu_el.wait_for(timeout=20000)
    titlu = titlu_el.text_content()   # textul, nu majusculele CSS (.cf-grup-titlu are text-transform: uppercase)
    return int(re.search(r"Note de validat \((\d+)\)", titlu).group(1)), pg.locator("#val-note .val-card").count()


def test_def_52_cardul_si_fereastra_numara_exact_notele_de_validat(browser, request):
    """52. Coadă: cardul „De depus” arăta 3 nevalidate, fereastra 2.
    Pașii, pe un cabinet nou (cifrele nu depind de alte rulări): asistentul scrie 3 note -> administratorul: cardul „3 note de validat”,
    fereastra „Note de validat (3)” cu 3 rânduri -> validează una -> „2 note de validat”, „(2)”, 2 rânduri -> respinge una cu motiv ->
    „1 notă de validat”, „(1)”, 1 rând."""
    with _cabinet_cu_firma() as (cab, f, a):
        _firma_gata(f)
        desc = ["E2E 52 nota %d-%d" % (i, _tag()) for i in range(3)]
        with ecran_cont(browser, request, a["email"]) as asist:
            for d in desc:
                _nota_prin_ecran(asist, f, d, AZI.isoformat(), luna=LUNA)
        with ecran_cont(browser, request, cab["email"]) as sef:
            pg = sef.pg
            n, t = _cifra_card(sef)
            sef.captura("card_3")
            assert n == 3 and "3 note de validat" in t, t
            assert _cifre_fereastra(sef) == (3, 3)
            sef.captura("fereastra_3")
            card = pg.locator("#val-note .val-card", has_text=desc[0]).first
            card.locator(".val-aproba").click()
            pg.wait_for_function("() => document.body.innerText.includes('Ai validat')", timeout=20000)
            n, t = _cifra_card(sef)
            assert n == 2 and "2 note de validat" in t, t
            assert _cifre_fereastra(sef) == (2, 2)
            sef.captura("fereastra_2")
            card = pg.locator("#val-note .val-card", has_text=desc[1]).first
            card.locator(".val-respinge").click()
            pg.fill("#dlg-input", "lipsește documentul 52")
            pg.click("#dlg-ok")
            pg.wait_for_function("() => document.body.innerText.includes('Ai respins')", timeout=20000)
            n, t = _cifra_card(sef)
            sef.captura("card_1")
            assert n == 1 and "1 notă de validat" in t, t
            assert _cifre_fereastra(sef) == (1, 1)


# ── C (nou, clasa lui 80) — validarea contării din Registrul jurnal validează documentul ────────────────────────────────────────
def test_def_c107_validarea_contarii_din_jurnal_valideaza_si_iesirea_din_stoc(patron, firma_e2e):
    """C (clasa lui 80: „validarea contării NU a validat ieșirea din stoc”). Pașii: contabilul-șef emite o factură cu un articol din stoc,
    „Da, pleacă marfa” -> două ciorne (contarea și ieșirea 607 = 371) -> Registru jurnal -> „Validează” pe contare: ambele note sunt
    validate (în bază și pe rânduri: niciun „Validează” rămas pe ele), ca în coadă, unde documentul se validează o dată."""
    aid = _articol_cu_stoc(firma_e2e)
    _asigura_serie(firma_e2e)
    pg = patron.pg
    _emitere(patron, firma_e2e)
    _client(pg)
    _linie(pg, 0, None, 2, 10, articol_id=aid)
    pg.click("#em-emite")
    pg.wait_for_selector("#em-poarta-da", timeout=20000)
    pg.click("#em-poarta-da")
    pg.wait_for_selector("#em-rezultat.em-bun", timeout=30000)
    s = firma_e2e["schema"]
    fid = sql('SELECT id FROM "%s".facturi ORDER BY id DESC LIMIT 1' % s)[0][0]
    contare = sql('SELECT id FROM "%s".inregistrari WHERE factura_id = %%s ORDER BY id LIMIT 1' % s, (fid,))[0][0]
    iesire = sql('SELECT DISTINCT inregistrare_id FROM "%s".miscari_stoc WHERE factura_id = %%s AND inregistrare_id IS NOT NULL' % s,
                 (fid,))
    assert len(iesire) == 1 and iesire[0][0] != contare, iesire
    iesire = iesire[0][0]
    _jurnal(patron, firma_e2e, LUNA)
    pg.locator("[data-val='%d']" % contare).scroll_into_view_if_needed()
    patron.captura("inainte")
    with pg.expect_response(lambda r: ("/jurnal/%d/valideaza" % contare) in r.url, timeout=30000) as rr:
        pg.click("[data-val='%d']" % contare)
    assert rr.value.status == 200, rr.value.text()
    pg.wait_for_function("(i) => !document.querySelector(`[data-val='${i}']`) && !!document.querySelector(`[data-nota-id='${i}']`)",
                         arg=contare, timeout=20000)
    stari = dict(sql('SELECT id, status FROM "%s".inregistrari WHERE id = ANY(%%s)' % s, ([contare, iesire],)))
    pg.locator("[data-nota-id='%d']" % iesire).scroll_into_view_if_needed()
    patron.captura("dupa")
    assert stari == {contare: "validata", iesire: "validata"}, stari
    assert pg.locator("[data-val='%d']" % iesire).count() == 0, "ieșirea din stoc a rămas de validat"
