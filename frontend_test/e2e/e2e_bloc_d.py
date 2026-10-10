# -*- coding: utf-8 -*-
"""Blocul D (DEFICIENTE.md 99–143) — deficiențele probate în browser, pașii contabilului, pe aplicația de acum.

Datele se pun pe DRUMUL APLICAȚIEI: rutele HTTP ale aplicației pornite (`_api`, cu tokenul contului de test), iar intrarea notelor
asistentului în coadă prin `coada_api.pune_notele_in_coada` — funcția pe care o cheamă middleware-ul după cererea unui asistent
fără drept de validare (`uc_coada.note_in_coada`; contul de test „asistent” are acum și dreptul de validare, deci middleware-ul
n-o mai cheamă singur). Firmele scrise sunt sintetice (`firma_e2e`, `firma_gv`), scoase la final."""
import datetime as _dt
import json
import re
import urllib.error
import urllib.request

import pytest

from conftest import BAZA, PREFIX_FIRMA, _db, _scoate_firmele_e2e, cui_cu_control, sql

AZI = _dt.date.today()
LUNA_TRECUTA = (AZI.replace(day=1) - _dt.timedelta(days=1)).replace(day=1)
PATRON, ASISTENT = "patron@prisma-cont.test", "asistent@prisma-cont.test"


# ── ajutoare ────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _uid(email):
    return sql("SELECT id FROM public.users WHERE email = %s", (email,))[0][0]


_TOKENURI = {}


def _token(email):
    if email not in _TOKENURI:
        from core import auth_api
        db = _db()
        with db.get_conn() as c:
            s = auth_api.sesiune_pentru_user(c, _uid(email))
            c.rollback()
        _TOKENURI[email] = s["token"]
    return _TOKENURI[email]


def _api(email, metoda, cale, corp=None):
    """O cerere pe ruta aplicației, ca utilizatorul `email` -> (status, json)."""
    req = urllib.request.Request(BAZA + cale, method=metoda, data=None if corp is None else json.dumps(corp).encode(),
                                 headers={"Authorization": "Bearer " + _token(email), "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return r.status, json.loads(r.read() or b"null")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"null")


def _in_coada(firma, email=ASISTENT, notifica=True):
    """Notele ciornă ale asistentului intră în coada de validare (ce face middleware-ul după cererea lui)."""
    from core import coada_api, uc_comun
    db = _db()
    with db.get_conn(firma["schema"]) as c:
        r = coada_api.pune_notele_in_coada(c, firma["cabinet_id"], firma["tenant_id"], _uid(email))
    if r and notifica:   # și notificarea validatorilor, ca după cererea asistentului (`uc_coada.note_in_coada`)
        with db.get_conn() as c:
            uc_comun._notif_note_de_validat(c, firma["cabinet_id"], [a["eticheta"] for a in r], _uid(email),
                                            tenant_id=firma["tenant_id"], coada_id=r[0]["coada_id"])
    return r


def _respinge(coada_id, motiv):
    st, r = _api(PATRON, "POST", "/coada/%d/respinge" % coada_id, {"motiv": motiv})
    assert st == 200, (st, r)
    return r


def _deschide(ecran, buton, text_asteptat, timeout=20000):
    """Din fereastra firmei, butonul cardului -> fereastra lui, așteptată până apare textul."""
    ecran.pg.click(buton)
    _asteapta_text(ecran, text_asteptat, timeout)


def _asteapta_text(ecran, text, timeout=20000):
    ecran.pg.wait_for_function("(t) => { const f = [...document.querySelectorAll('.fereastra')].pop(); "
                               "return f && f.innerText.includes(t); }", arg=text, timeout=timeout)


def _coada(ecran):
    """Contabilul-șef deschide coada de validare din cardul ei de pe birou."""
    ecran.acasa()
    ecran.pg.click("button.cab-card:has([data-cheie='validat'])")
    ecran.pg.wait_for_selector(".fereastra:last-of-type #val-titlu", timeout=30000)


def _firma_noua(sufix):
    """O firmă sintetică în plus (pe același drum ca `firma_e2e`: `provision_tenant` din șablon), scoasă la final."""
    import io as _io
    import os
    import time as _t
    from core import tenant_provisioning as tp
    db = _db()
    nume = "%s %s %d SRL" % (PREFIX_FIRMA, sufix, int(_t.time() * 1000) % 10000000)
    rad = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sql_t = _io.open(os.path.join(rad, "tenant_template.sql"), encoding="utf-8").read()
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute("SELECT id, accounting_firm_id FROM public.users WHERE email = %s", (PATRON,))
        uid, cab = cur.fetchone()
        r = tp.provision_tenant(c, nume, cui_cu_control(80000000 + int(_t.time() * 1000) % 9000000), cab, uid, sql_t)
        c.commit()
    f = {"tenant_id": r["tenant_id"], "schema": r["schema_name"], "nume": nume, "cabinet_id": cab}
    _atribuie_asistentului(f)
    _date_firma(f)
    return f


def _atribuie_asistentului(firma):
    """Contabilul-șef atribuie firma asistentului (Asistenți -> firmele lui): fără atribuire, asistentul n-o vede."""
    st, r = _api(PATRON, "POST", "/asistenti/%d/firme/%d" % (_uid(ASISTENT), firma["tenant_id"]), {})
    assert st == 200, (st, r)


def _metoda(firma, metoda):
    st, r = _api(PATRON, "POST", "/tenants/%d/firma-profil/date" % firma["tenant_id"], {"metoda_stoc": metoda})
    assert st == 200 and r.get("ok") is not False, (st, r)


@pytest.fixture(scope="module")
def firma_cv(firma_e2e):
    """`firma_e2e` cu stocul cantitativ-valoric (declarat de contabil în Date firmă)."""
    _atribuie_asistentului(firma_e2e)
    _date_firma(firma_e2e)
    _metoda(firma_e2e, "cantitativ_valoric")
    return firma_e2e


@pytest.fixture(scope="module")
def firma_gv():
    f = _firma_noua("GV")
    try:
        _metoda(f, "global_valoric")
        yield f
    finally:
        _scoate_firmele_e2e(f["tenant_id"])


def _nir_cv(firma, numar, articol, cant=10, pret=55, refacut_din=None, articol_id=None, **extra):
    linie = {"cantitate": cant, "pret_achizitie": pret, "cota_tva": 21}
    linie.update({"articol_id": articol_id} if articol_id else {"denumire": articol, "articol_nou": True})
    corp = {"numar": numar, "data": AZI.isoformat(), "furnizor": "Furnizor Proba E2E SRL", "linii": [linie], **extra}
    if refacut_din:
        corp["refacut_din_id"] = refacut_din
    st, r = _api(ASISTENT, "POST", "/tenants/%d/stocuri/nir" % firma["tenant_id"], corp)
    assert st == 200 and "eroare" not in r, (st, r)
    return r


def _nir_respins(firma, numar, articol, motiv):
    """Asistentul salvează NIR-ul (la cost), notele lui intră în coadă, contabilul-șef îl respinge cu motiv."""
    r = _nir_cv(firma, numar, articol)
    el = [a for a in _in_coada(firma) if "NIR nr %s " % numar in a["eticheta"]]
    assert len(el) == 1, el
    _respinge(el[0]["coada_id"], motiv)
    return r


def _stocuri(ecran, firma):
    ecran.firma(firma["nume"])
    _deschide(ecran, "#fa-stocuri", "NIR-urile lunii")
    ecran.pg.wait_for_selector(".fereastra:last-of-type #s-situatie-tabel, .fereastra:last-of-type #s-situatie .stare-goala",
                               timeout=20000)


def _rand_stoc(ecran, articol):
    """Rândul articolului din „Situația stocului”: [articol, UM, cantitate, CMP, valoare]."""
    return ecran.pg.evaluate("(a) => { const f = [...document.querySelectorAll('.fereastra')].pop(); "
                             "const tr = [...f.querySelectorAll('#s-situatie-tabel tbody tr')].find((r) => r.cells[0].innerText.trim() === a); "
                             "return tr ? [...tr.cells].map((c) => c.innerText.trim()) : null; }", articol)


# ── 99–113: NIR respins, refăcut, coada ─────────────────────────────────────────────────────────────────────────────────
def test_def_99_nir_respins_scade_marfa_din_stoc(patron, firma_cv):
    """99. NIR: un NIR respins nu scădea marfa din stoc.
    Pașii contabilului: asistentul salvează NIR-ul (10 buc × 55 lei, la cost) -> Stocuri arată 10 / 550,00 -> contabilul-șef deschide
    coada, pe NIR apasă „Respinge”, scrie motivul -> Stocuri arată articolul cu 0 / 0,00 (intrarea stornată în roșu)."""
    _nir_cv(firma_cv, "D99", "Marfa D99")
    _in_coada(firma_cv)
    pg = patron.pg
    _stocuri(patron, firma_cv)
    rand = _rand_stoc(patron, "Marfa D99")
    assert (rand[2], rand[4]) == ("10", "550,00"), rand
    patron.captura("inainte")
    _coada(patron)
    card = pg.locator(".fereastra:last-of-type .val-card", has_text=firma_cv["nume"]).filter(has_text="NIR nr D99 ")
    card.locator(".val-respinge").click()
    pg.fill("#dlg-input", "NIR greșit D99")
    pg.click("#dlg-ok")
    _asteapta_text(patron, "Ai respins")
    _stocuri(patron, firma_cv)
    rand = _rand_stoc(patron, "Marfa D99")
    patron.captura("dupa")
    assert (rand[2], rand[4]) == ("0", "0,00"), rand


def _card_coada(ecran, firma, text):
    return ecran.pg.locator(".fereastra:last-of-type .val-card", has_text=firma["nume"]).filter(has_text=text)


def _nir_lista(ecran):
    """Textul listei „NIR-urile lunii” (ultima `.pf-lista` a ecranului Stocuri)."""
    return ecran.pg.evaluate("() => { const f = [...document.querySelectorAll('.fereastra')].pop(); "
                             "const l = [...f.querySelectorAll('.pf-lista')].pop(); return l ? l.innerText : ''; }")


def test_def_100_nir_respins_are_stare_motiv_si_se_reface(patron, firma_cv):
    """100. NIR: NIR-ul respins fără stare și motiv în „NIR-urile lunii”; nu putea fi refăcut.
    Pașii contabilului: NIR-ul salvat de asistent e respins în coadă cu motiv -> Stocuri -> „NIR-urile lunii”: rândul NIR-ului
    spune „Respins la validare: <motiv>” și are „Refă NIR-ul”; apăsat, formularul NIR se deschide cu NIR-ul respins de refăcut."""
    _nir_respins(firma_cv, "D100", "Marfa D100", "lipsește avizul D100")
    pg = patron.pg
    _stocuri(patron, firma_cv)
    rand = pg.locator(".fereastra:last-of-type .pf-lista .pf-frand", has_text="NIR D100 ")
    assert "Respins la validare: lipsește avizul D100." in rand.inner_text(), rand.inner_text()
    patron.captura("lista")
    rand.locator(".nir-reface").click()
    _asteapta_text(patron, "Refaci NIR-ul D100, respins la validare (lipsește avizul D100)")
    assert pg.input_value(".fereastra:last-of-type #sn-numar") == "D100"
    patron.captura("reface")


def test_def_112_refa_nir_precompleteaza_articolul_fara_zecimale_in_exces(patron, firma_cv):
    """112. NIR: la „Refă NIR-ul”, articol neprecompletat; zecimale în exces.
    Pașii contabilului: NIR respins (Marfa D112, 10 buc × 55 lei) -> Stocuri -> „Refă NIR-ul”: rândul formularului are articolul
    ales (Marfa D112), cantitatea „10” și prețul „55.00” (nu „10.000” / „55.0000”)."""
    _nir_respins(firma_cv, "D112", "Marfa D112", "preț greșit D112")
    pg = patron.pg
    _stocuri(patron, firma_cv)
    pg.locator(".fereastra:last-of-type .pf-lista .pf-frand", has_text="NIR D112 ").locator(".nir-reface").click()
    _asteapta_text(patron, "Refaci NIR-ul D112")
    f = ".fereastra:last-of-type "
    ales = pg.eval_on_selector(f + "#nir-l0-articol", "s => s.options[s.selectedIndex].text")
    valori = (ales, pg.input_value(f + "#nir-l0-cantitate"), pg.input_value(f + "#nir-l0-pret_achizitie"))
    patron.captura()
    assert valori == ("Marfa D112", "10", "55.00"), valori


def _refa_din_ecran(ecran, firma, numar, cantitate=None):
    """Contabilul apasă „Refă NIR-ul”, (opțional schimbă cantitatea), salvează; confirmă dacă e identic cu cel respins."""
    pg = ecran.pg
    _stocuri(ecran, firma)
    pg.locator(".fereastra:last-of-type .pf-lista .pf-frand", has_text="NIR %s " % numar).locator(".nir-reface").click()
    _asteapta_text(ecran, "Refaci NIR-ul %s" % numar)
    if cantitate is not None:
        pg.fill(".fereastra:last-of-type #nir-l0-cantitate", str(cantitate))
    pg.click(".fereastra:last-of-type #sn-salveaza")
    _asteapta_text(ecran, "NIR salvat")


def test_def_113_nir_respins_si_refacut_o_linie_langa_cel_valabil(patron, firma_cv):
    """113. NIR: respins și refăcut cu același număr; cel respins primul, card complet.
    Pașii contabilului: NIR D113 respins -> „Refă NIR-ul” (12 buc) -> salvează -> „NIR-urile lunii”: un singur card „NIR D113”
    (cel valabil), iar sub el o linie „NIR D113 din … · Respins · înlocuit de NIR nr D113 din …”."""
    _nir_respins(firma_cv, "D113", "Marfa D113", "cantitate greșită D113")
    _refa_din_ecran(patron, firma_cv, "D113", 12)
    pg = patron.pg
    carduri = pg.locator(".fereastra:last-of-type .pf-lista .pf-frand", has_text="NIR D113 ")
    linii = pg.locator(".fereastra:last-of-type .pf-lista .nir-inlocuit", has_text="NIR D113 ")
    patron.captura()
    assert carduri.count() == 1, _nir_lista(patron)
    assert "Respins" not in carduri.inner_text(), carduri.inner_text()
    assert linii.count() == 1 and "· Respins · înlocuit de NIR nr D113 din" in linii.inner_text(), _nir_lista(patron)


def test_def_111_cardul_nir_refacut_spune_retrimis_dupa_respingere(patron, firma_cv):
    """111. Coadă: la „Refă NIR-ul”, cardul fără „retrimis după respingere”.
    Pașii contabilului: NIR D111 respins cu motiv -> refăcut (alte cantități) -> notele lui intră în coadă -> contabilul-șef
    deschide coada: cardul NIR-ului refăcut spune „Retrimisă după respingere · motivul anterior: „…” · nota s-a schimbat”."""
    _nir_respins(firma_cv, "D111", "Marfa D111", "lipsește factura D111")
    vechi = sql("SELECT id FROM \"%s\".nir WHERE numar = 'D111'" % firma_cv["schema"])[0][0]
    aid = sql("SELECT id FROM \"%s\".articole WHERE denumire = 'Marfa D111'" % firma_cv["schema"])[0][0]
    _nir_cv(firma_cv, "D111", None, cant=8, refacut_din=vechi, articol_id=aid)
    _in_coada(firma_cv)
    _coada(patron)
    card = _card_coada(patron, firma_cv, "NIR nr D111 ")
    text = card.inner_text()
    patron.captura()
    assert card.count() == 1, text
    assert "Retrimisă după respingere · motivul anterior: „lipsește factura D111”" in text, text
    assert "nota s-a schimbat față de cea respinsă" in text, text


def test_def_199_nir_refacut_identic_nu_apare_schimbat(patron, firma_cv):
    """199. Coadă: cardul unui document retrimis după respingere (ex. NIR refăcut) putea spune greșit că notele s-au schimbat față de
    cele respinse; lista de note a documentului putea repeta o notă — la întâmplare, după ordinea notelor din aceeași tranzacție.
    [partea rămasă, registrul: „fără test de capăt la capăt în browser”] Pașii: NIR D199 respins cu motiv -> refăcut IDENTIC (aceeași
    cantitate și preț, confirmat „neschimbat”) -> notele intră în coadă; capul grupului e notă cea mai nouă, iar aici ea e ultimul
    membru (ordinea care strica, fixată ca să nu depindă de noroc) -> contabilul-șef deschide coada: cardul spune „nota nu s-a schimbat
    față de cea respinsă”, iar notele documentului apar fiecare o singură dată."""
    from core import coada_api
    _nir_respins(firma_cv, "D199", "Marfa D199", "lipsește factura D199")
    vechi = sql("SELECT id FROM \"%s\".nir WHERE numar = 'D199'" % firma_cv["schema"])[0][0]
    aid = sql("SELECT id FROM \"%s\".articole WHERE denumire = 'Marfa D199'" % firma_cv["schema"])[0][0]
    _nir_cv(firma_cv, "D199", None, refacut_din=vechi, articol_id=aid, confirma_neschimbata=True)
    el = [a for a in _in_coada(firma_cv) if "NIR nr D199 " in a["eticheta"]]
    assert len(el) == 1, el
    with _db().get_conn() as c, c.cursor() as cur:
        ids = sorted(m for m, _p in coada_api.membri_grup(cur, el[0]["coada_id"]))
    assert len(ids) >= 2, ids
    sql("UPDATE public.declaratii_coada SET creat_la = now() + interval '1 second' WHERE id = %s", (ids[-1],))
    _coada(patron)
    card = _card_coada(patron, firma_cv, "NIR nr D199 ")
    text = card.inner_text()
    membri = card.get_attribute("data-coada-ids").split(",")
    patron.captura()
    assert card.count() == 1, text
    assert "nota nu s-a schimbat față de cea respinsă" in text, text
    assert len(membri) == len(set(membri)) and sorted(map(int, membri)) == ids, (membri, ids)


def test_def_101_titlul_documentului_in_coada_e_scurt(patron, firma_gv):
    """101. Coadă: titlul repeta numele NIR-ului la fiecare notă.
    Pașii contabilului: asistentul salvează un NIR la preț de vânzare (4 note: 371=408, 4428=408, 371=378, 371=4428) -> contabilul-șef
    deschide coada: un singur card, titlul „NIR nr D101 din <data> · Furnizor Proba E2E SRL · 4 note” (documentul o dată)."""
    st, r = _api(ASISTENT, "POST", "/tenants/%d/stocuri/nir" % firma_gv["tenant_id"],
                 {"numar": "D101", "data": AZI.isoformat(), "furnizor": "Furnizor Proba E2E SRL",
                  "linii": [{"denumire": "Marfa D101", "cantitate": 10, "pret_achizitie": 50, "pret_vanzare": 80, "cota_tva": 21}]})
    assert st == 200 and len(r["inregistrari"]) == 4, (st, r)
    _in_coada(firma_gv)
    _coada(patron)
    card = _card_coada(patron, firma_gv, "NIR nr D101 ")
    titlu = card.locator(".val-titlu").inner_text().strip()
    patron.captura()
    assert titlu == "NIR nr D101 din %s · Furnizor Proba E2E SRL · 4 note" % AZI.strftime("%d.%m.%Y"), titlu


def test_def_127_fereastra_cozii_spune_ce_contine(patron, firma_gv):
    """127. Coadă: fereastra se numea „De depus”.
    Pașii contabilului: o notă a asistentului așteaptă validarea -> contabilul-șef deschide coada de pe birou: titlul ferestrei
    începe cu „Note de validat”, nu „De depus”."""
    st, r = _api(ASISTENT, "POST", "/tenants/%d/jurnal" % firma_gv["tenant_id"],
                 {"data": AZI.isoformat(), "descriere": "Chirie D127", "linii": [{"debit": "612", "credit": "401", "suma": 100}]})
    assert st == 200, (st, r)
    _in_coada(firma_gv)
    _coada(patron)
    titlu = patron.pg.inner_text(".fereastra:last-of-type #val-titlu").strip()
    patron.captura()
    assert titlu.startswith("Note de validat"), titlu
    assert "De depus" not in titlu.split(" · ")[0], titlu


# ── 114–116, 128–129: clopoțelul, facturi încasate, chitanțe, notele din coadă ─────────────────────────────────────────────
def test_def_114_clopotelul_ramane_vizibil_si_apasabil(patron):
    """114. Antet: clopoțelul nu se vedea; la 0 nimic de apăsat.
    Pașii contabilului: contabilul-șef are o notificare necitită -> pe birou, clopoțelul din antet arată pictograma și „1”+ -> îl
    apasă (panoul se deschide, notificările devin citite) -> clopoțelul rămâne cu pictograma, la 0, și se poate apăsa din nou."""
    from core import notificari_api
    db = _db()
    with db.get_conn() as c:
        notificari_api.adauga(c, _uid(PATRON), "info", "Probă E2E clopoțel D114", link=None)
    pg = patron.pg
    patron.acasa()
    pg.wait_for_function("() => { const b = document.querySelector('#nav-clopot-badge'); return b && b.textContent.trim() !== ''; }",
                         timeout=20000)
    assert pg.locator("#nav-clopot svg").count() == 1
    patron.captura("inainte")
    pg.click("#nav-clopot")
    pg.wait_for_selector("#nav-clopot-panou .clopot-item", timeout=20000)
    pg.wait_for_function("() => { const b = document.querySelector('#nav-clopot-badge'); return b && b.textContent.trim() === '' "
                         "&& !document.querySelector('#nav-clopot').disabled; }", timeout=20000)
    patron.captura("dupa")
    assert pg.locator("#nav-clopot svg").count() == 1, pg.inner_html("#nav-clopot")
    cutie = pg.locator("#nav-clopot").bounding_box()
    assert cutie and cutie["width"] >= 16 and cutie["height"] >= 16, cutie
    pg.click("#nav-clopot")                      # a doua apăsare închide panoul: butonul încă răspunde
    pg.wait_for_selector("#nav-clopot-panou", state="detached", timeout=10000)


_NR_FACT = {"n": 0}


def _factura_emisa(firma, pret=100):
    """O factură emisă (1 × `pret` + TVA 21%), creată de contabilul-șef pe ruta facturilor."""
    _NR_FACT["n"] += 1
    numar = "E2ED%d%d" % (_NR_FACT["n"], int(_dt.datetime.now().timestamp()) % 100000)
    st, r = _api(PATRON, "POST", "/tenants/%d/facturi" % firma["tenant_id"],
                 {"numar": numar, "data_emitere": AZI.isoformat(), "directie": "emisa", "tert_nume": "Client Proba E2E SRL",
                  "tert_cui": cui_cu_control(31000001), "linii": [{"descriere": "Servicii D", "cantitate": 1, "pret_unitar": pret,
                                                                    "cota_tva": 21}]})
    assert st == 200, (st, r)
    return numar, r.get("id") or r.get("factura_id")


def _istoric(ecran, firma):
    pg = ecran.pg
    ecran.firma(firma["nume"])
    pg.click("#fa-facturi")
    pg.wait_for_selector(".fereastra:last-of-type #fac-istoric", timeout=20000)
    pg.click(".fereastra:last-of-type #fac-istoric")
    pg.wait_for_selector(".fereastra:last-of-type .fac-frand-btn", timeout=20000)


def _detaliu_factura(ecran, firma, numar):
    pg = ecran.pg
    _istoric(ecran, firma)
    pg.locator(".fereastra:last-of-type .fac-frand-btn", has_text=numar).first.click()
    pg.wait_for_selector(".fereastra:last-of-type #fd-chitanta, .fereastra:last-of-type .fd-stare", timeout=20000)


def test_def_116_refuzul_chitantei_duce_la_campul_seriei(patron, firma_gv):
    """116. Chitanțe: „Deschide Date firmă” ducea la începutul paginii.
    Pașii contabilului: firma n-are serie de chitanțe -> factura emisă -> „Emite chitanță” -> „Emite” -> refuzul spune că lipsește
    seria și are „Deschide Date firmă” -> apăsat, Date firmă se deschide cu câmpul „Seria chitanțelor” în vedere și în focus."""
    assert not sql('SELECT serie_chitanta FROM "%s".firma_profil WHERE serie_chitanta IS NOT NULL' % firma_gv["schema"])
    numar, _fid = _factura_emisa(firma_gv)
    pg = patron.pg
    _detaliu_factura(patron, firma_gv, numar)
    pg.click(".fereastra:last-of-type #fd-chitanta")
    pg.click(".fereastra:last-of-type #fd-chit-ok")
    buton = pg.wait_for_selector(".fereastra:last-of-type [data-ecran-destinatie='date_firma']", timeout=20000)
    assert "n-are serie pentru chitanțe" in patron.fereastra()
    patron.captura("refuz")
    buton.click()
    pg.wait_for_selector(".fereastra:last-of-type #df-serie_chitanta", timeout=20000)
    pg.wait_for_function("() => document.activeElement && document.activeElement.id === 'df-serie_chitanta'", timeout=10000)
    vazut = pg.evaluate("() => { const r = document.querySelector('.fereastra:last-of-type #df-serie_chitanta').getBoundingClientRect();"
                        " return r.top >= 0 && r.bottom <= window.innerHeight; }")
    patron.captura("date_firma")
    assert vazut, "câmpul seriei nu e în vedere"


def _serie_chitante(firma, serie="CHD"):
    if not sql('SELECT 1 FROM "%s".firma_profil WHERE serie_chitanta IS NOT NULL' % firma["schema"]):
        st, r = _api(PATRON, "POST", "/tenants/%d/firma-profil/date" % firma["tenant_id"], {"serie_chitanta": serie})
        assert st == 200 and r.get("ok") is not False, (st, r)


def test_def_115_factura_incasata_prin_chitanta_spune_incasata(patron, firma_gv):
    """115. Factură: F1A3 încasată rămânea „contabilizată”.
    Pașii contabilului: factura emisă de 121,00 lei -> „Emite chitanță” pe suma întreagă -> detaliul facturii arată „încasată”, iar
    în „Istoric facturi” rândul ei spune „încasată”."""
    _serie_chitante(firma_gv)
    numar, _fid = _factura_emisa(firma_gv)
    pg = patron.pg
    _detaliu_factura(patron, firma_gv, numar)
    stari = pg.eval_on_selector_all(".fereastra:last-of-type .fd-stare", "els => els.map(e => e.innerText.trim())")
    assert "neîncasată" in stari, stari
    pg.click(".fereastra:last-of-type #fd-chitanta")
    assert pg.input_value(".fereastra:last-of-type #fd-chit-suma") in ("121", "121.00")
    pg.click(".fereastra:last-of-type #fd-chit-ok")
    _asteapta_text(patron, "a fost emisă")
    _detaliu_factura(patron, firma_gv, numar)
    stari = pg.eval_on_selector_all(".fereastra:last-of-type .fd-stare", "els => els.map(e => e.innerText.trim())")
    patron.captura("detaliu")
    assert "încasată" in stari, stari
    _istoric(patron, firma_gv)
    rand = pg.locator(".fereastra:last-of-type .fac-frand-btn", has_text=numar).first.inner_text()
    patron.captura("istoric")
    assert re.search(r"·\s*încasată\b", rand), rand


def _chitanta_asistent(firma, fid, suma=121):
    st, r = _api(ASISTENT, "POST", "/tenants/%d/chitante" % firma["tenant_id"],
                 {"data": AZI.isoformat(), "suma": suma, "factura_id": fid})
    assert st == 200 and r.get("ok"), (st, r)
    return r


def test_def_128_nota_chitantei_arata_factura_stinsa(patron, firma_gv):
    """128. Chitanțe: nota chitanței nu arăta factura stinsă.
    Pașii contabilului: asistentul emite chitanța pe factura emisă -> nota ei (5311=4111) intră în coadă -> contabilul-șef deschide
    coada: cardul notei spune „stinge factura <număr> din <data>”; „Vezi nota” arată același lucru."""
    _serie_chitante(firma_gv)
    numar, fid = _factura_emisa(firma_gv)
    ch = _chitanta_asistent(firma_gv, fid)
    _in_coada(firma_gv)
    pg = patron.pg
    _coada(patron)
    card = _card_coada(patron, firma_gv, "%s-%s" % (ch["serie"], ch["numar"]))
    asteptat = "stinge factura %s din %s" % (numar, AZI.strftime("%d.%m.%Y"))
    text = card.inner_text()
    patron.captura("card")
    assert card.count() == 1 and asteptat in text, text
    card.locator(".val-vezi-nota").click()
    pg.wait_for_selector(".fereastra:last-of-type .fd-tabel", timeout=20000)
    patron.captura("detaliu")
    assert asteptat in patron.fereastra(), patron.fereastra()


def test_def_129_detaliul_notei_are_valideaza_si_respinge(patron, firma_gv):
    """129. Note: detaliul notei fără Validează/Respinge.
    Pașii contabilului: o notă a asistentului e în coadă -> contabilul-șef deschide coada -> „Vezi nota →” -> detaliul are
    „Validează” și „Respinge”; „Validează” din detaliu validează nota (intră în evidență)."""
    st, r = _api(ASISTENT, "POST", "/tenants/%d/jurnal" % firma_gv["tenant_id"],
                 {"data": AZI.isoformat(), "descriere": "Telefon D129", "document_ref": "Factura TEL D129",
                  "linii": [{"debit": "626", "credit": "401", "suma": 77}]})
    assert st == 200, (st, r)
    nid = r.get("id")
    _in_coada(firma_gv)
    pg = patron.pg
    _coada(patron)
    _card_coada(patron, firma_gv, "Telefon D129").locator(".val-vezi-nota").click()
    pg.wait_for_selector(".fereastra:last-of-type #val-nota-actiuni", timeout=20000)
    f = ".fereastra:last-of-type #val-nota-actiuni "
    assert pg.locator(f + ".val-aproba").inner_text().strip() == "Validează"
    assert pg.locator(f + ".val-respinge").inner_text().strip() == "Respinge"
    patron.captura("detaliu")
    pg.click(f + ".val-aproba")
    _asteapta_text(patron, "Ai validat")
    patron.captura("validata")
    assert sql('SELECT status FROM "%s".inregistrari WHERE id = %%s' % firma_gv["schema"], (nid,)) == [("validata",)]


# ── 102, 103, 109, 110: salarii ─────────────────────────────────────────────────────────────────────────────────────────
def _cnp(baza12):
    """CNP cu cifra de control (algoritmul din CLAUDE.md „Date de test”), verificat, nu inventat."""
    ch = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]
    c = sum(int(baza12[i]) * ch[i] for i in range(12)) % 11
    return baza12 + str(1 if c == 10 else c)


@pytest.fixture(scope="module")
def firma_sal():
    """Firmă sintetică cu un salariat (5.000 lei, normă întreagă, funcție de bază), adăugat pe ruta salariaților."""
    f = _firma_noua("SAL")
    try:
        st, r = _api(PATRON, "POST", "/tenants/%d/salariati" % f["tenant_id"],
                     {"nume": "Popescu", "prenume": "Ion", "cnp": _cnp("185010140123"), "data_angajare": "2026-01-05",
                      "tip_norma": "intreaga", "ore_zi": 8, "salariu_brut": 5000, "persoane_intretinere": 0,
                      "scutit_contrib_minim": False, "functie_baza": True, "cor": "331302"})
        assert st == 200, (st, r)
        f["salariat_id"] = r.get("id") or r.get("salariat_id")
        # luna preluării = luna trecută (Date firmă, „Luna preluării”): ce e dinainte nu se numără la restanțe
        st, r = _api(PATRON, "POST", "/tenants/%d/firma-profil/date" % f["tenant_id"], {"luna_preluare": LUNA_TRECUTA.strftime("%Y-%m")})
        assert st == 200 and r.get("ok") is not False, (st, r)
        yield f
    finally:
        _scoate_firmele_e2e(f["tenant_id"])


def _stat(ecran, firma, luni_inapoi=0):
    pg = ecran.pg
    ecran.firma(firma["nume"])
    _deschide(ecran, "#fa-salariati", "Stat de plat")
    pg.wait_for_selector(".fereastra:last-of-type .pf-lista .pf-frand", timeout=30000)
    for _ in range(luni_inapoi):
        prev = pg.inner_text(".fereastra:last-of-type .pf-intro")
        pg.click(".fereastra:last-of-type #sp-prev")
        pg.wait_for_function("(p) => { const f = [...document.querySelectorAll('.fereastra')].pop(); const i = f.querySelector('.pf-intro');"
                             " return i && i.innerText !== p && f.querySelector('.pf-lista .pf-frand'); }", arg=prev, timeout=30000)


def _rand_salariat(ecran):
    """Textul rândului salariatului, cu compoziția netului (și partea ei pliată)."""
    return ecran.pg.eval_on_selector(".fereastra:last-of-type .pf-lista .pf-frand", "e => e.textContent.replace(/\\s+/g, ' ')")


def _adauga_prima(ecran, denumire, suma):
    pg = ecran.pg
    pg.click(".fereastra:last-of-type [data-elem]")
    pg.wait_for_selector(".fereastra:last-of-type #el-tip", timeout=20000)
    pg.select_option(".fereastra:last-of-type #el-tip", "prima")
    pg.fill(".fereastra:last-of-type #el-denumire", denumire)
    pg.fill(".fereastra:last-of-type #el-suma", str(suma))
    pg.click(".fereastra:last-of-type #el-adauga")
    pg.wait_for_function("(d) => { const f = [...document.querySelectorAll('.fereastra')].pop(); "
                         "return f && !f.querySelector('#el-tip') && f.querySelector('.pf-lista .pf-frand'); }", arg=denumire, timeout=30000)


def test_def_103_salariu_de_la_e_prima_zi_a_lunii_lucrate(patron, firma_sal):
    """103. Salarii: „de la” venea cu data de azi.
    Pașii contabilului: Stat de plată -> „← luna” (luna trecută) -> „Salariu” pe salariat: „de la” e 01 al lunii afișate, nu azi."""
    _stat(patron, firma_sal, luni_inapoi=1)
    pg = patron.pg
    pg.click(".fereastra:last-of-type [data-salariu]")
    pg.wait_for_selector(".fereastra:last-of-type #salariu-data", timeout=20000)
    luna_trecuta = (AZI.replace(day=1) - _dt.timedelta(days=1)).replace(day=1)
    val = pg.input_value(".fereastra:last-of-type #salariu-data")
    patron.captura()
    assert val == luna_trecuta.isoformat(), (val, luna_trecuta)


def test_def_102_prima_intra_in_brut_si_pe_fluturas(patron, firma_sal):
    """102. Salarii: lipseau primele, sporurile și orele suplimentare.
    Pașii contabilului: Stat de plată (luna curentă) -> „Prime, sporuri, ore supl.” pe salariat -> Primă „prima de performanță D”
    500,50 lei -> Adaugă: brutul devine 5.500,50 (5.000 + 500,50), iar compoziția netului arată prima, cu numele ei."""
    _stat(patron, firma_sal)
    assert "brut 5.000,00" in _rand_salariat(patron), _rand_salariat(patron)
    _adauga_prima(patron, "prima de performanță D", "500.50")
    rand = _rand_salariat(patron)
    patron.captura()
    assert "brut 5.500,50" in rand, rand
    assert "prima de performanță D" in rand, rand


def test_def_110_costul_pe_salariat_are_cam_pe_prima(patron, firma_sal):
    """110. Salarii: costul pe salariat fără CAM pe elementele variabile.
    Pașii contabilului: Stat de plată cu salariul 5.000 + prima 500,50 (testul 102) -> rândul salariatului: cost = brut + CAM pe
    tot venitul = 5.500,50 + 124 = 5.624,50 (CAM 2,25% din 5.501 la leu; fără primă în bază ar fi 113 -> 5.613,50).
    Temei: CF art.220^4 alin.(1) — baza CAM = suma câștigurilor brute realizate din salarii."""
    _stat(patron, firma_sal)
    rand = _rand_salariat(patron)
    if "brut 5.500,50" not in rand:          # rulat singur: prima o pune contabilul aici
        _adauga_prima(patron, "prima de performanță D", "500.50")
        rand = _rand_salariat(patron)
    patron.captura()
    assert "brut 5.500,50" in rand and "cost 5.624,50" in rand, rand


def test_def_109_dupa_prima_ciorna_veche_se_inlocuieste_si_merge_la_validare(asistent, patron, firma_sal):
    """109. Salarii: după o primă, ciorna veche nu era rescrisă și nu ajungea la validare.
    Pașii contabilului (luna trecută): asistentul „Contabilizează statul” -> „Scrie nota ciornă” (ajunge la validare) -> adaugă o
    primă de 1.000 lei -> „Contabilizează statul”: ecranul spune că ciorna are alte sume și oferă „Înlocuiește ciorna cu nota din
    statul de acum” -> apăsat: ciorna veche iese, nota nouă (cu prima) e singura ciornă a lunii și ajunge în coada contabilului-șef."""
    pg = asistent.pg
    _stat(asistent, firma_sal, luni_inapoi=1)
    pg.click(".fereastra:last-of-type #sp-contare")
    pg.wait_for_selector(".fereastra:last-of-type #sp-contare-scrie", timeout=30000)
    pg.click(".fereastra:last-of-type #sp-contare-scrie")
    pg.wait_for_function("() => { const z = [...document.querySelectorAll('.fereastra')].pop().querySelector('#sp-contare-zona');"
                         " return z && !z.querySelector('#sp-contare-scrie'); }", timeout=30000)
    s = firma_sal["schema"]
    vechi = sql('SELECT id FROM "%s".inregistrari WHERE status = \'ciorna\' AND sursa = \'salarii\'' % s)
    assert len(vechi) == 1, vechi
    _in_coada(firma_sal)
    _adauga_prima(asistent, "prima D109", "1000")
    pg.click(".fereastra:last-of-type #sp-contare")
    pg.wait_for_selector(".fereastra:last-of-type #sp-contare-scrie", timeout=30000)
    assert "Ciorna #%d din jurnal are alte sume decât statul afișat" % vechi[0][0] in asistent.fereastra(), asistent.fereastra()
    asistent.captura("alte_sume")
    pg.click(".fereastra:last-of-type #sp-contare-scrie")
    _asteapta_text(asistent, "Ciorna #%d, cu sumele statului de dinainte, a fost înlocuită" % vechi[0][0], timeout=30000)
    asistent.captura("inlocuita")
    noi = sql('SELECT i.id, (SELECT sum(suma) FROM "%s".inregistrari_linii l WHERE l.inregistrare_id = i.id AND l.cont_debit = \'641\') '
              'FROM "%s".inregistrari i WHERE i.status = \'ciorna\' AND i.sursa = \'salarii\'' % (s, s))
    assert len(noi) == 1 and noi[0][0] != vechi[0][0] and float(noi[0][1]) == 6000.0, noi
    _in_coada(firma_sal)
    _coada(patron)
    carduri = patron.pg.locator(".fereastra:last-of-type .val-card", has_text=firma_sal["nume"])
    texte = [carduri.nth(i).inner_text() for i in range(carduri.count())]
    patron.captura("coada")
    assert len(texte) == 1, texte


# ── 121–125: Control fiscal ─────────────────────────────────────────────────────────────────────────────────────────────
def _control(ecran):
    ecran.acasa()
    ecran.pg.click("button.cab-card:has([data-cheie='control'])")
    ecran.pg.wait_for_selector(".fereastra:last-of-type #cf-lista .mig-frand", timeout=60000)


def _control_firma(ecran, firma):
    _control(ecran)
    ecran.pg.locator(".fereastra:last-of-type #cf-lista .mig-frand", has_text=firma["nume"]).first.click()
    ecran.pg.wait_for_selector(".fereastra:last-of-type .cf-decl, .fereastra:last-of-type .cf-grup-titlu", timeout=60000)


def _grupuri_control(ecran):
    """{titlul grupului: [„TIP perioada termen …”, …]} din detaliul firmei (grupurile de declarații cu termen)."""
    return ecran.pg.evaluate("""() => { const f = [...document.querySelectorAll('.fereastra')].pop(); const out = {};
        f.querySelectorAll('.cf-grup-titlu').forEach((t) => { const d = t.tagName === 'SUMMARY' ? t.parentElement.querySelector('.cf-decl')
            : t.nextElementSibling; if (d && d.classList.contains('cf-decl')) out[t.textContent.replace(/\\s+/g, ' ').trim()] =
            [...d.querySelectorAll('.cf-rand-decl')].map((r) => r.textContent.replace(/\\s+/g, ' ').trim()); }); return out; }""")


def test_def_121_restantele_se_numara_de_la_luna_preluarii(patron, firma_sal):
    """121. Control fiscal: restanțe numărate din ianuarie.
    Pașii contabilului: firma cu salariat din 01/2026, preluată în iConta în luna trecută (Date firmă) -> Control fiscal -> firma:
    D112 pe lunile dinaintea preluării NU sunt „Restanțe”; stau în grupul „Înainte de preluare în iConta.eu — LL/AAAA”."""
    _control_firma(patron, firma_sal)
    g = _grupuri_control(patron)
    patron.captura()
    restante = [r for k, v in g.items() if k.startswith("Restanțe") for r in v]
    inainte = next((v for k, v in g.items() if k.startswith("Înainte de preluare în iConta.eu — %s" % LUNA_TRECUTA.strftime("%m/%Y"))),
                   None)
    assert inainte and any(r.startswith("D112 01/2026") for r in inainte), g
    assert not [r for r in restante if r.startswith("D112")], g


def test_def_122_declaratia_se_marcheaza_depusa_in_afara_iconta(patron, firma_sal):
    """122. Control fiscal: lipsea marcarea „depusă în afara iConta”.
    Pașii contabilului: Control fiscal -> firma -> „Înainte de preluare” -> pe D112 01/2026 „Marchează depusă în afara iConta.eu” ->
    data depunerii 25.02.2026, recipisa „REC-D122” -> Salvează: rândul are acum „Modifică marcarea” / „Anulează marcarea”."""
    pg = patron.pg
    _control_firma(patron, firma_sal)
    pg.click(".fereastra:last-of-type details.cf-inainte > summary")
    item = pg.locator(".fereastra:last-of-type .cf-decl-item[data-cheie='d112-2026-1']")
    item.locator(".cf-extern-btn").click()
    item.locator(".cf-extern-form input[type=date]").fill("2026-02-25")
    item.locator(".cf-extern-form input[type=text]").fill("REC-D122")
    item.locator(".cf-extern-salveaza").click()
    pg.wait_for_function("() => { const i = [...document.querySelectorAll('.fereastra')].pop()"
                         ".querySelector(\".cf-decl-item[data-cheie='d112-2026-1']\"); return i && i.querySelector('.cf-extern-anuleaza'); }",
                         timeout=30000)
    patron.captura()
    assert "Modifică marcarea" in item.inner_text(), item.inner_text()
    assert sql("SELECT sursa, recipisa FROM public.declaratii_depuse WHERE tenant_id = %s AND tip = 'd112' AND an = 2026 AND luna = 1",
               (firma_sal["tenant_id"],)) == [("extern", "REC-D122")]


def test_def_124_de_urmarit_are_scadentele_din_30_de_zile(patron, firma_sal):
    """124. Control fiscal: „de urmărit” 0, deși 4 scadente pe 26.10.
    Pașii contabilului: Control fiscal -> firma: orice declarație nedepusă cu termenul în următoarele 30 de zile e la „De urmărit”
    (D112 pe luna preluării are termenul pe 25 a lunii următoare)."""
    _control_firma(patron, firma_sal)
    g = _grupuri_control(patron)
    patron.captura()
    urmarit = next((v for k, v in g.items() if k.startswith("De urmărit")), [])
    toate = [(k, r) for k, v in g.items() for r in v]
    in_30 = []
    for k, r in toate:
        m = re.search(r"termen (\d\d)\.(\d\d)\.(\d{4})", r)
        if m and 0 <= (_dt.date(int(m.group(3)), int(m.group(2)), int(m.group(1))) - AZI).days <= 30 and not k.startswith("La zi"):
            in_30.append(r)
    assert any(r.startswith("D112") for r in in_30), g
    assert sorted(in_30) == sorted(urmarit), g


def test_def_125_cardul_arata_aceleasi_cifre_ca_fereastra(patron, firma_sal):
    """125. Control fiscal: cardul ≠ fereastra.
    Pașii contabilului: după o scriere (firma tocmai preluată) -> birou: cardul „Control fiscal” -> fereastra Control fiscal: aceleași
    contoare pe card și în fereastră, iar firma are deja faptele ei (de urmărit), nu „în recalculare”/gri."""
    pg = patron.pg
    patron.acasa()
    pg.wait_for_function("() => { const z = document.querySelector(\"[data-cheie='control']\"); return z && /\\d/.test(z.innerText); }",
                         timeout=30000)
    card = pg.inner_text("[data-cheie='control']")
    _control(patron)
    fereastra = pg.inner_text(".fereastra:last-of-type .cf-sumar")
    nr = lambda t, eticheta: (re.search(r"(\d+) cu " + eticheta, t) or [None, None])[1]  # noqa: E731
    rand = pg.locator(".fereastra:last-of-type #cf-lista .mig-frand", has_text=firma_sal["nume"]).first.inner_text()
    patron.captura()
    for et in ("restanțe", "neconcordanțe", "declarații de urm"):
        assert nr(card, et) == nr(fereastra, et), (et, card, fereastra)
    assert "de urmărit" in rand, rand


def test_def_123_fara_declaratie_spune_nedeclarat(patron, firma_sal):
    """123. Control fiscal: „diferă de contabilitate” fără declarație; trebuie „nedeclarat”.
    Pașii contabilului: luna trecută are nota de salarii VALIDATĂ (cu o primă), apoi prima se scoate din stat; D112 nu e depusă ->
    Control fiscal -> firma -> „Declarație vs contabilitate”: constatarea spune „D112 nedeclarat (generat azi) ar avea …”, nu că
    o declarație „declară” ceva diferit."""
    s, tid, sid = firma_sal["schema"], firma_sal["tenant_id"], firma_sal["salariat_id"]
    an, luna = LUNA_TRECUTA.year, LUNA_TRECUTA.month
    st, r = _api(PATRON, "GET", "/tenants/%d/salariati/%d/elemente?an=%d&luna=%d" % (tid, sid, an, luna))
    if not r["elemente"]:
        st, r = _api(PATRON, "POST", "/tenants/%d/salariati/%d/elemente" % (tid, sid),
                     {"an": an, "luna": luna, "tip": "prima", "denumire": "prima D123", "suma": 700})
        assert st == 200, (st, r)
    st, r = _api(PATRON, "POST", "/tenants/%d/salarii-contare?an=%d&luna=%d" % (tid, an, luna), {})
    assert st == 200, (st, r)
    for (nid,) in sql('SELECT id FROM "%s".inregistrari WHERE status = \'ciorna\' AND sursa = \'salarii\'' % s):
        st, r = _api(PATRON, "POST", "/tenants/%d/jurnal/%d/valideaza" % (tid, nid), {})
        assert st == 200, (st, r)
    st, r = _api(PATRON, "GET", "/tenants/%d/salariati/%d/elemente?an=%d&luna=%d" % (tid, sid, an, luna))
    for e in r["elemente"]:
        st2, r2 = _api(PATRON, "DELETE", "/tenants/%d/salariati/%d/elemente/%d" % (tid, sid, e["id"]))
        assert st2 == 200, (st2, r2)
    _control_firma(patron, firma_sal)
    text = patron.fereastra()
    patron.captura()
    assert "declarație vs contabilitate" in text.lower(), text
    assert "D112 nedeclarat (generat azi) ar avea" in text, text
    assert "D112 declară" not in text, text


# ── 126, 138–141, 143: închiderea lunii, registrul MF, balanța, ferestrele late ───────────────────────────────────────────
def _nota_validata(firma, data, debit, credit, suma, descriere):
    st, r = _api(PATRON, "POST", "/tenants/%d/jurnal" % firma["tenant_id"],
                 {"data": data, "descriere": descriere, "document_ref": "Doc %s" % descriere,
                  "linii": [{"debit": debit, "credit": credit, "suma": suma}]})
    assert st == 200 and r.get("id"), (st, r)
    st, r2 = _api(PATRON, "POST", "/tenants/%d/jurnal/%d/valideaza" % (firma["tenant_id"], r["id"]), {})
    assert st == 200, (st, r2)
    return r["id"]


@pytest.fixture(scope="module")
def firma_mf():
    """Firmă sintetică cu un mijloc fix (12.000 lei, 60 de luni, PIF 15.01.2026, liniar -> 200 lei/lună din 02/2026), adus pe ruta
    de import a migrării; amortizarea înregistrată numai pe 02/2026 (6811=2813 200, validată); în luna trecută o depunere de
    numerar la bancă fără a doua parte (581=5311 300, validată)."""
    f = _firma_noua("MF")
    try:
        st, r = _api(PATRON, "POST", "/tenants/%d/mijloace-fixe-import" % f["tenant_id"],
                     {"randuri": [{"cod": "MF-D1", "denumire": "Utilaj probă D", "valoare": 12000, "rezidual": 0, "dnf_luni": 60,
                                   "data_pif": "2026-01-15", "metoda": "liniara", "cont_imobilizare": "2131",
                                   "cont_amortizare": "2813"}]})
        assert st == 200 and r.get("importati") == 1, (st, r)
        _nota_validata(f, "2026-02-28", "6811", "2813", 200, "Amortizare 02/2026 D")
        _nota_validata(f, LUNA_TRECUTA.replace(day=20).isoformat(), "581", "5311", 300, "Depunere numerar D141")
        yield f
    finally:
        _scoate_firmele_e2e(f["tenant_id"])


def _mijloace(ecran, firma):
    ecran.firma(firma["nume"])
    _deschide(ecran, "#fa-mijloace", "Mijloace fixe")
    ecran.pg.wait_for_selector(".fereastra:last-of-type .fd-tabel tbody tr", timeout=30000)


def _celule_mf(ecran, cod):
    return ecran.pg.evaluate("(c) => { const f = [...document.querySelectorAll('.fereastra')].pop(); "
                             "const tr = [...f.querySelectorAll('.fd-tabel tbody tr')].find((r) => r.cells[0] && r.cells[0].innerText.trim() === c);"
                             " return tr ? [...tr.cells].map((x) => x.innerText.replace(/\\s+/g, ' ').trim()) : null; }", cod)


def _luni_de_la(an, luna, pana):
    out = []
    while (an, luna) <= (pana.year, pana.month):
        out.append((an, luna))
        an, luna = (an + 1, 1) if luna == 12 else (an, luna + 1)
    return out


def test_def_139_registrul_mf_arata_amortizarea_inregistrata_si_diferenta(patron, firma_mf):
    """139. Mijloace fixe: amortizat 4.200 vs 2813 = 2.400.
    Pașii contabilului: Mijloace fixe -> rândul MF-D1: „Amortizat (calculat)” = 200 × lunile 02/2026…luna trecută, „Înregistrat
    (cont)” = 200,00 (soldul 2813, numai 02/2026 validată), „Diferență” = calculat − 200, cu lunile neînregistrate (03/2026…)."""
    _mijloace(patron, firma_mf)
    c = _celule_mf(patron, "MF-D1")
    patron.captura()
    n = len(_luni_de_la(2026, 2, LUNA_TRECUTA))
    calc = "{:,.2f}".format(200 * n).replace(",", "X").replace(".", ",").replace("X", ".")
    dif = "{:,.2f}".format(200 * (n - 1)).replace(",", "X").replace(".", ",").replace("X", ".")
    assert (c[5], c[6]) == (calc, "200,00"), c
    assert c[7].startswith(dif) and "neînregistrate: %d luni: 03" % (n - 1) in c[7], c


def test_def_140_registrul_mf_are_durata_catalogul_si_planul_lunar(patron, firma_mf):
    """140. Mijloace fixe: lipseau durata, codul din catalog și planul lunar.
    Pașii contabilului: Mijloace fixe -> MF-D1: durata „60 luni”; „Cod din catalog” 2.1.17.2.1 -> Salvează -> apare denumirea din
    Catalogul HG 2139/2004 cu plaja de ani; „Planul lunar de amortizare” are 60 de luni, 02/2026 „înregistrată”, 03/2026
    „neînregistrată”."""
    pg = patron.pg
    _mijloace(patron, firma_mf)
    assert _celule_mf(patron, "MF-D1")[3] == "60 luni"
    mid = sql('SELECT id FROM "%s".mijloace_fixe WHERE cod = %%s' % firma_mf["schema"], ("MF-D1",))[0][0]
    pg.fill(".fereastra:last-of-type #mf-catalog-%d" % mid, "2.1.17.2.1")
    pg.click(".fereastra:last-of-type [data-catalog='%d']" % mid)
    pg.wait_for_function("() => { const r = [...document.querySelectorAll('.fereastra')].pop().querySelector('.fd-tabel tbody tr');"
                         " return r && /\\d+–\\d+ ani/.test(r.innerText); }",
                         timeout=20000)
    rezumat = pg.locator(".fereastra:last-of-type details summary", has_text="Planul lunar de amortizare")
    assert "(60 luni)" in rezumat.inner_text(), rezumat.inner_text()
    rezumat.click()
    plan = pg.evaluate("() => [...[...document.querySelectorAll('.fereastra')].pop().querySelectorAll('details[open] .fd-tabel tbody tr')]"
                       ".map((r) => [...r.cells].map((c) => c.innerText.trim()))")
    patron.captura()
    assert len(plan) == 60 and plan[0] == ["02/2026", "200,00", "înregistrată"] and plan[1] == ["03/2026", "200,00", "neînregistrată"], plan[:3]


def test_def_141_inchiderea_lunii_semnaleaza_581_cu_sold(patron, firma_mf):
    """141. Închidere lună: 581 cu sold nenul nesemnalat.
    Pașii contabilului: Închidere lună -> „← luna” (luna trecută, cu depunerea de 300 lei la bancă înregistrată doar pe partea
    casei) -> „Semnale”: „contul 581 (viramente interne) are sold 300,00 lei la sfârșitul lunii”."""
    pg = patron.pg
    patron.firma(firma_mf["nume"])
    _deschide(patron, "#fa-inchidere", "Închidere lună")
    pg.wait_for_selector(".fereastra:last-of-type #il-controale .ci-mesaj, .fereastra:last-of-type #il-controale .ca-mesaj", timeout=30000)
    pg.click(".fereastra:last-of-type #il-prev")
    _asteapta_text(patron, "Luna %s" % LUNA_TRECUTA.strftime("%m/%Y"))
    pg.wait_for_selector(".fereastra:last-of-type #il-controale .ci-mesaj, .fereastra:last-of-type #il-controale .ca-mesaj", timeout=30000)
    text = pg.inner_text(".fereastra:last-of-type #il-controale")
    patron.captura()
    assert "contul 581 (viramente interne) are sold 300,00 lei la sfârșitul lunii" in text, text


def test_def_126_inchiderea_lunii_are_card_in_zilnic(patron, firma_mf):
    """126. Închidere lună: fără intrare vizibilă; card nou.
    Pașii contabilului: deschide firma: în grupul „Zilnic” există cardul „Închidere lună”; apăsat, deschide ecranul cu perioada
    contabilă (controalele, blocarea) și evidența facturilor."""
    pg = patron.pg
    patron.firma(firma_mf["nume"])
    grup = pg.evaluate("() => { const b = document.querySelector('#fa-inchidere'); const s = b && b.closest('section.firme-grup');"
                       " return s ? s.querySelector('h3').innerText.trim() : null; }")
    assert grup == "Zilnic", grup
    patron.captura("card")
    _deschide(patron, "#fa-inchidere", "Evidența facturilor")
    text = patron.fereastra()
    patron.captura("ecran")
    assert "Perioada contabilă" in text and "Închidere lună" in text, text


def test_def_138_balanta_lunii_are_numai_notele_lunii(asistent, firma_mf):
    """138. Registru jurnal: F2 ca Ana „0 note”, balanța cu rulaje 7.750.
    Pașii contabilului (asistentul): luna curentă n-are note -> Registru jurnal pe luna curentă: nicio notă -> Balanță de verificare pe
    luna curentă: rulajul lunii 0,00 (aceleași note ca jurnalul), iar notele lunilor anterioare (500,00 = 200 + 300) stau la „Sume
    precedente”."""
    pg = asistent.pg
    asistent.firma(firma_mf["nume"])
    _deschide(asistent, "#fa-jurnal", "Registru")
    pg.wait_for_timeout(1500)
    jurnal = asistent.fereastra()
    assert "Amortizare 02/2026 D" not in jurnal and "Depunere numerar D141" not in jurnal, jurnal[:800]
    asistent.captura("jurnal")
    asistent.firma(firma_mf["nume"])
    _deschide(asistent, "#fa-balanta", "Balanță de verificare")
    pg.wait_for_selector(".fereastra:last-of-type .fd-tabel tbody tr", timeout=30000)
    total = pg.evaluate("() => { const f = [...document.querySelectorAll('.fereastra')].pop(); const t = f.querySelector('.fd-tabel:last-of-type') ;"
                        " const rows = [...f.querySelectorAll('.fd-tabel')].find((x) => x.innerText.includes('Rulaj lun'));"
                        " const tr = [...rows.querySelectorAll('tbody tr')].pop(); return [...tr.cells].map((c) => c.innerText.trim()); }")
    asistent.captura("balanta")
    # [cont, denumire, si_d, si_c, prec_d, prec_c, rul_d, rul_c, tot_d, tot_c, sf_d, sf_c]
    assert total[1] == "Total" and (total[6], total[7]) == ("0,00", "0,00") and (total[4], total[5]) == ("500,00", "500,00"), total


def test_def_143_ferestrele_cu_tabele_fara_derulare_laterala_la_1920(patron, firma_mf):
    """143. General: derulare laterală la 1920 px (Balanță, MF, Declarații).
    Pașii contabilului: ecran 1920 × 1080 -> firma -> Mijloace fixe, apoi Balanță de verificare (luna trecută), apoi Declarații:
    nicio fereastră nu are derulare laterală (nici fereastra, nici tabelul din ea)."""
    pg = patron.pg
    pg.set_viewport_size({"width": 1920, "height": 1080})
    lat = ("() => { const f = [...document.querySelectorAll('.fereastra')].pop(); return [...f.querySelectorAll('*')].concat([f])"
           ".filter((e) => { const s = getComputedStyle(e); return /(auto|scroll)/.test(s.overflowX) && e.scrollWidth > e.clientWidth + 1; })"
           ".map((e) => (e.className || e.tagName) + ':' + e.scrollWidth + '>' + e.clientWidth); }")
    rez = {}
    _mijloace(patron, firma_mf)
    rez["mijloace"] = pg.evaluate(lat)
    patron.captura("mijloace")
    patron.firma(firma_mf["nume"])
    _deschide(patron, "#fa-balanta", "Balanță de verificare")
    pg.click(".fereastra:last-of-type #b-prev")
    pg.wait_for_selector(".fereastra:last-of-type .fd-tabel tbody tr", timeout=30000)
    rez["balanta"] = pg.evaluate(lat)
    patron.captura("balanta")
    patron.firma(firma_mf["nume"])
    _deschide(patron, "#fa-declaratii", "Declara")
    pg.wait_for_timeout(1500)
    rez["declaratii"] = pg.evaluate(lat)
    patron.captura("declaratii")
    assert not any(rez.values()), rez


# ── 136, 137: ecranul declarației ────────────────────────────────────────────────────────────────────────────────────────
def _date_firma(firma):
    """Datele cerute de ANAF în declarații, completate de contabil în Date firmă (IBAN-ul e exemplul standard, cu control valid)."""
    st, r = _api(PATRON, "POST", "/tenants/%d/firma-profil/date" % firma["tenant_id"],
                 {"reg_com": "J40/1234/2020", "caen": "4711", "adresa": "Str. Probei nr. 1", "oras": "București", "judet": "B",
                  "cod_postal": "010101", "banca": "Banca Probă", "iban": "RO49AAAA1B31007593840000", "telefon": "0211234567",
                  "email": "proba@prisma-cont.test", "patron_nume": "Ion Popescu", "declarant_nume": "Popescu",
                  "declarant_prenume": "Ion", "declarant_functie": "Administrator",
                  "forma_juridica": "SRL", "capital_subscris": "200", "capital_varsat": "200"})
    assert st == 200 and r.get("ok") is not False, (st, r)


def _genereaza(ecran, firma, tip, an, luna):
    """Firma -> Declarații -> tipul -> anul și luna -> „Continuă →” -> pasul 2 (rezultatul)."""
    pg = ecran.pg
    ecran.firma(firma["nume"])
    _deschide(ecran, "#fa-declaratii", "Pasul 1 din 3")
    pg.select_option(".fereastra:last-of-type #dec-tip", tip)
    pg.fill(".fereastra:last-of-type #dec-an", str(an))
    pg.dispatch_event(".fereastra:last-of-type #dec-an", "change")
    if pg.query_selector(".fereastra:last-of-type #dec-luna"):
        pg.select_option(".fereastra:last-of-type #dec-luna", str(luna))
    pg.click(".fereastra:last-of-type #dec-continua")
    pg.wait_for_function("() => { const t = [...document.querySelectorAll('.fereastra')].pop().innerText; "
                         "return t.includes('Pasul 2 din 3 — verifică') || !!document.querySelector('.fereastra:last-of-type .dec-eroare'); }",
                         timeout=90000)


def test_def_137_rezumatul_declaratiei_nu_e_avertisment(patron, firma_sal):
    """137. Declarații: rezumatele corecte în caseta „Avertisment”.
    Pașii contabilului: Declarații -> D112 pe luna trecută -> pasul 2: rezumatul („D112: 1 salariati - impozit …, CAS …”) e în caseta
    albastră „Rezumat”; nu apare în „Avertismente”."""
    _date_firma(firma_sal)
    _genereaza(patron, firma_sal, "d112", LUNA_TRECUTA.year, LUNA_TRECUTA.month)
    pg = patron.pg
    casete = pg.evaluate("() => [...[...document.querySelectorAll('.fereastra')].pop().querySelectorAll('.caseta-info, .dec-avert')]"
                         ".map((c) => c.innerText.trim())")
    patron.captura()
    rezumat = [c for c in casete if c.startswith("Rezumat")]
    assert rezumat and "D112: 1 salariati - impozit" in rezumat[0], casete
    assert not [c for c in casete if c.startswith("Avertismente") and "D112: 1 salariati" in c], casete


def test_def_136_componentele_d406_arata_cont_debit_credit_suma(patron, firma_mf):
    """136. D406: „[object Object]” în coloana „linii”.
    Pașii contabilului: Declarații -> D406 pe luna trecută (nota 581=5311 300,00 validată) -> pasul 2 -> „Din ce e făcută declarația”:
    coloana „linii” arată „581 · debit 300,00” și „5311 · credit 300,00”, niciodată „[object Object]”."""
    _date_firma(firma_mf)
    _genereaza(patron, firma_mf, "d406", LUNA_TRECUTA.year, LUNA_TRECUTA.month)
    pg = patron.pg
    rez = pg.locator(".fereastra:last-of-type details.dec-xml summary", has_text="Din ce e făcută declarația")
    assert rez.count() == 1, patron.fereastra()[:2000]
    rez.click()
    text = pg.inner_text(".fereastra:last-of-type details.dec-xml[open]")
    patron.captura()
    assert "[object Object]" not in text, text
    assert "581 · debit 300,00" in text and "5311 · credit 300,00" in text, text


# ── 104–106: retrimiterea după respingere, notificările ─────────────────────────────────────────────────────────────────
def _nota_asistent_respinsa(firma, descriere, motiv, suma=100):
    st, r = _api(ASISTENT, "POST", "/tenants/%d/jurnal" % firma["tenant_id"],
                 {"data": AZI.isoformat(), "descriere": descriere, "document_ref": "Doc %s" % descriere,
                  "linii": [{"debit": "612", "credit": "401", "suma": suma}]})
    assert st == 200, (st, r)
    el = [a for a in _in_coada(firma) if descriere in a["eticheta"]]
    assert len(el) == 1, el
    _respinge(el[0]["coada_id"], motiv)
    return r["id"], el[0]["coada_id"]


def _jurnal(ecran, firma):
    ecran.firma(firma["nume"])
    _deschide(ecran, "#fa-jurnal", "Registru")
    ecran.pg.wait_for_selector(".fereastra:last-of-type [data-nota-id]", timeout=30000)


def test_def_192_nota_din_nir_nu_ofera_ce_serverul_refuza(patron, firma_gv):
    """192. Registru jurnal: notele care vin din NIR și din raportul Z arată „Editează” și „Șterge”, deși serverul le refuză.
    Pașii: contabilul-șef salvează NIR-ul D192 (fără factură, 2 × 50 lei) -> Registru jurnal: notele NIR-ului (ciorne) n-au
    „Editează” și n-au „Șterge” (NIR-ul le indică din alt tabel) și spun unde se corectează („în Stoc › NIR-urile lunii”); o notă
    manuală ciornă are în continuare amândouă -> cererea directă de ștergere a notei NIR e refuzată (serverul, neschimbat)."""
    tid = firma_gv["tenant_id"]
    st, r = _api(PATRON, "POST", "/tenants/%d/stocuri/nir" % tid,
                 {"numar": "D192", "data": AZI.isoformat(), "furnizor": "Furnizor D192 SRL", "factura_id": None,
                  "linii": [{"denumire": "Marfa D192", "cantitate": 2, "pret_achizitie": 50, "pret_vanzare": 80, "cota_tva": 21}]})
    assert st == 200 and r.get("inregistrari"), (st, r)
    nir_ids = r["inregistrari"]
    st, m = _api(PATRON, "POST", "/tenants/%d/jurnal" % tid, {"data": AZI.isoformat(), "descriere": "Manuala D192", "document_ref": "D192",
                                                            "linii": [{"debit": "5311", "credit": "4111", "suma": 10}]})
    assert st == 200 and m.get("id"), (st, m)
    pg = patron.pg
    _jurnal(patron, firma_gv)
    stare = pg.evaluate("""(ids) => ids.map(i => { const r = document.querySelector(`.fereastra:last-of-type [data-nota-id='${i}']`);
        return r ? {id: i, edit: !!r.querySelector('[data-edit]'), del: !!r.querySelector('[data-del]'), text: r.innerText} : {id: i, lipsa: true}; })""",
                        nir_ids + [m["id"]])
    patron.captura()
    *nir, manuala = stare
    assert all(not x.get("lipsa") and not x["edit"] and not x["del"] and "NIR-urile lunii" in x["text"] for x in nir), nir
    assert manuala["edit"] and manuala["del"], manuala
    st, rr = _api(PATRON, "DELETE", "/tenants/%d/jurnal/%d" % (tid, nir_ids[0]))
    assert st >= 400 or (rr or {}).get("eroare"), (st, rr)


def test_def_104_retrimiterea_notei_neschimbate_cere_confirmare(asistent, firma_gv):
    """104. Coadă: retrimiterea unei note identice cu cea respinsă fără avertisment.
    Pașii contabilului: nota asistentului e respinsă („lipsește contractul D104”) -> asistentul, în Registru jurnal, pe notă
    „Trimite din nou la validare” fără s-o schimbe -> apare avertismentul „nimic nu s-a schimbat de la respingere”, cu motivul
    alături, și „Retrimite fără schimbări” -> confirmat, nota e din nou la validare."""
    nid, _cid = _nota_asistent_respinsa(firma_gv, "Chirie D104", "lipsește contractul D104")
    pg = asistent.pg
    _jurnal(asistent, firma_gv)
    pg.click(".fereastra:last-of-type [data-nota-id='%d'] [data-retrimite]" % nid)
    pg.wait_for_selector("#caseta-atentie-activa #ca-ok", timeout=20000)
    mesaj = pg.inner_text("#caseta-atentie-activa")
    asistent.captura("avertisment")
    assert "lipsește contractul D104" in mesaj and "nimic nu s-a schimbat" in mesaj.lower(), mesaj
    assert pg.inner_text("#caseta-atentie-activa #ca-ok").strip() == "Retrimite fără schimbări"
    pg.click("#caseta-atentie-activa #ca-ok")
    pg.wait_for_function("(n) => { const r = [...document.querySelectorAll('.fereastra')].pop().querySelector(`[data-nota-id='${n}']`);"
                         " return r && r.innerText.includes('La validare în cabinet'); }", arg=nid, timeout=20000)
    asistent.captura("retrimisa")


def test_def_105_cardul_notei_retrimise_spune_retrimisa_si_motivul(patron, firma_gv):
    """105. Coadă: cardul notei retrimise fără „retrimisă” și motiv.
    Pașii contabilului: nota respinsă („suma greșită D105”) e retrimisă de asistent fără schimbări (confirmat) -> contabilul-șef
    deschide coada: cardul spune „Retrimisă după respingere · motivul anterior: „suma greșită D105” · nota nu s-a schimbat față
    de cea respinsă”."""
    nid, _cid = _nota_asistent_respinsa(firma_gv, "Telefon D105", "suma greșită D105")
    st, r = _api(ASISTENT, "POST", "/tenants/%d/jurnal/%d/retrimite?confirma=true" % (firma_gv["tenant_id"], nid), {})
    assert st == 200 and r.get("ok") is not False, (st, r)
    _coada(patron)
    card = _card_coada(patron, firma_gv, "Telefon D105")
    text = card.inner_text()
    patron.captura()
    assert "Retrimisă după respingere · motivul anterior: „suma greșită D105” · nota nu s-a schimbat față de cea respinsă" in text, text


def test_def_106_notificarea_de_validat_se_rezolva_la_respingere(patron, firma_gv):
    """106. Notificări: rămâneau active după validare/respingere; nota F5 apărea de două ori.
    Pașii contabilului: asistentul trimite o notă la validare -> contabilul-șef primește „Notă pregătită, de validat …” -> o
    respinge din coadă -> în clopoțel, notificarea ei spune „rezolvată: respinsă” (nu mai e de făcut); iar pentru o notă validată,
    „rezolvată: validată”."""
    st, r = _api(ASISTENT, "POST", "/tenants/%d/jurnal" % firma_gv["tenant_id"],
                 {"data": AZI.isoformat(), "descriere": "Curier D106", "document_ref": "Doc D106",
                  "linii": [{"debit": "624", "credit": "401", "suma": 40}]})
    assert st == 200, (st, r)
    st, r2 = _api(ASISTENT, "POST", "/tenants/%d/jurnal" % firma_gv["tenant_id"],
                  {"data": AZI.isoformat(), "descriere": "Posta D106", "document_ref": "Doc2 D106",
                   "linii": [{"debit": "626", "credit": "401", "suma": 30}]})
    assert st == 200, (st, r2)
    el = {a["eticheta"]: a["coada_id"] for a in _in_coada(firma_gv, notifica=False)}
    c_resp = next(v for k, v in el.items() if "Curier D106" in k)
    c_val = next(v for k, v in el.items() if "Posta D106" in k)
    from core import uc_comun
    db = _db()
    with db.get_conn() as c:   # fiecare element își are notificarea lui (`uc_coada.note_in_coada` -> `_notif_note_de_validat`)
        for et, cid in (("Notă · Curier D106", c_resp), ("Notă · Posta D106", c_val)):
            uc_comun._notif_note_de_validat(c, firma_gv["cabinet_id"], [et], _uid(ASISTENT), tenant_id=firma_gv["tenant_id"],
                                            coada_id=cid)
    pg = patron.pg
    _coada(patron)
    _card_coada(patron, firma_gv, "Curier D106").locator(".val-respinge").click()
    pg.fill("#dlg-input", "fără factură D106")
    pg.click("#dlg-ok")
    _asteapta_text(patron, "Ai respins")
    st, r = _api(PATRON, "POST", "/coada/%d/aproba" % c_val, {})
    assert st == 200, (st, r)
    stari = dict(sql("SELECT link, rezolvata FROM public.notificari WHERE user_id = %s AND link IN (%s, %s)",
                     (_uid(PATRON), "validat:%d" % c_resp, "validat:%d" % c_val)))
    assert stari == {"validat:%d" % c_resp: "respins", "validat:%d" % c_val: "validat"}, stari
    patron.acasa()
    pg.click("#nav-clopot")
    pg.wait_for_selector("#nav-clopot-panou .clopot-item", timeout=20000)
    itemi = pg.eval_on_selector_all("#nav-clopot-panou .clopot-item", "els => els.map(e => e.innerText.replace(/\\s+/g, ' '))")
    patron.captura()
    assert any("Curier D106" in t and "rezolvată: respinsă" in t for t in itemi), itemi[:10]
    assert any("Posta D106" in t and "rezolvată: validată" in t for t in itemi), itemi[:10]


# ── 119, 120: TVA din NIR și poarta D300 = balanța ───────────────────────────────────────────────────────────────────────
LUNA_DOUA = (LUNA_TRECUTA - _dt.timedelta(days=1)).replace(day=1)


@pytest.fixture(scope="module")
def firma_tva():
    """Firmă sintetică plătitoare de TVA (decont lunar), stoc global-valoric, cu datele cerute de ANAF completate."""
    f = _firma_noua("TVA")
    try:
        st, r = _api(PATRON, "POST", "/tenants/%d/vector" % f["tenant_id"],
                     {"regim_fiscal": "profit", "platitor_tva": True, "tip_decont": "lunar", "operatiuni_ic": False,
                      "inreg_art317": False, "tva_data_inceput": "2025-01-01"})
        assert st == 200 and r.get("ok") is not False, (st, r)
        _date_firma(f)
        _metoda(f, "global_valoric")
        yield f
    finally:
        _scoate_firmele_e2e(f["tenant_id"])


def _trimite_declaratia(ecran):
    pg = ecran.pg
    b = pg.query_selector(".fereastra:last-of-type #dec-trimite") or pg.query_selector(".fereastra:last-of-type #dec-gol-da")
    assert b, ecran.fereastra()[:1500]
    b.click()
    pg.wait_for_function("() => { const f = [...document.querySelectorAll('.fereastra')].pop(); const m = f.querySelector('#dec-coada-mesaj');"
                         " return f.innerText.includes('Trimisă în coada de validare') || (m && m.innerText.trim()); }", timeout=90000)
    return ecran.fereastra()


def test_def_120_d300_nu_intra_in_coada_cand_4426_are_tva_neinclus_chiar_cu_ciorne_in_luna(patron, firma_tva):
    """120. Declarații TVA: D300, D394, D390 din aceeași sursă ca balanța, cu gardă 4427/4426. (și 210: garda nu mai bloca)
    [retestul Costin 09.10, cuvânt cu cuvânt] „D300 F1 10/2026 se poate trimite deși 4426 are 241,50 neincluși.” Situația F1: NIR-urile
    fără factură validate pe 4426 = 401 (115,50 + 126,00), D300 regenerat din documente cu deductibila 0, iar în lună stăteau notele de
    corecție în ciornă (121/122) — iar o ciornă în perioadă făcea din blocaj doar avertisment (R36). Pașii: luna trecută are nota
    validată 4426 = 401 de 241,50 și o ciornă -> Declarații -> D300 pe luna trecută -> „Trimite în coadă”: refuzat, cu diferența pe
    cont („contul 4426 are 241.50”) și ciorna numită; nu intră în coadă.
    [testul vechi trecea pe defect: avea diferența pe 4427, dar nicio ciornă în lună]"""
    tid = firma_tva["tenant_id"]
    _nota_validata(firma_tva, LUNA_TRECUTA.replace(day=7).isoformat(), "4426", "401", 241.50, "NIR fara factura D120")
    st, r = _api(PATRON, "POST", "/tenants/%d/jurnal" % tid,
                 {"data": LUNA_TRECUTA.replace(day=9).isoformat(), "descriere": "Plata furnizor ciorna D120", "document_ref": "DP-D120",
                  "linii": [{"debit": "401", "credit": "5311", "suma": 100}]})
    assert st == 200 and r.get("id"), (st, r)
    try:
        _genereaza(patron, firma_tva, "d300", LUNA_TRECUTA.year, LUNA_TRECUTA.month)
        text = _trimite_declaratia(patron)
        patron.captura()
        assert "Declarația nu intră în coadă: TVA-ul ei nu se potrivește cu balanța lunii" in text, text[:2000]
        assert "contul 4426 are 241.50" in text, text[:2000]
        assert "nevalidat" in text, text[:2000]
        assert not sql("SELECT id FROM public.declaratii_coada WHERE tenant_id = %s AND tip = 'd300'", (tid,))
    finally:
        _api(PATRON, "DELETE", "/tenants/%d/jurnal/%d" % (tid, r["id"]))


def test_def_210_d394_nu_intra_in_coada_cu_diferenta_tva_si_ciorne_in_luna(patron, firma_tva):
    """210. D300: garda D300 față de balanță nu mai blochează trimiterea (regresie a lui 120).
    Regresia venea din regula R36 (ciornă în perioadă -> numai avertisment), comună tuturor declarațiilor de TVA. Pașii: luna trecută are
    TVA deductibilă validată pe 4426 pe care documentele nu o au (din testul 120) și o ciornă -> D394 pe luna trecută -> „Trimite în
    coadă”: refuzat pe aceeași diferență; nu intră în coadă."""
    tid = firma_tva["tenant_id"]
    if not sql('SELECT 1 FROM "%s".inregistrari WHERE descriere = %%s' % firma_tva["schema"], ("NIR fara factura D120",)):
        _nota_validata(firma_tva, LUNA_TRECUTA.replace(day=7).isoformat(), "4426", "401", 241.50, "NIR fara factura D120")
    st, r = _api(PATRON, "POST", "/tenants/%d/jurnal" % tid,
                 {"data": LUNA_TRECUTA.replace(day=9).isoformat(), "descriere": "Plata furnizor ciorna D210", "document_ref": "DP-D210",
                  "linii": [{"debit": "401", "credit": "5311", "suma": 100}]})
    assert st == 200 and r.get("id"), (st, r)
    try:
        _genereaza(patron, firma_tva, "d394", LUNA_TRECUTA.year, LUNA_TRECUTA.month)
        text = _trimite_declaratia(patron)
        patron.captura()
        assert "Declarația nu intră în coadă: TVA-ul ei nu se potrivește cu balanța lunii" in text, text[:2000]
        assert "contul 4426 are 241.50" in text, text[:2000]
        assert not sql("SELECT id FROM public.declaratii_coada WHERE tenant_id = %s AND tip = 'd394'", (tid,))
    finally:
        _api(PATRON, "DELETE", "/tenants/%d/jurnal/%d" % (tid, r["id"]))


def test_def_119_tva_din_nir_fara_factura_nu_e_pe_4426_deci_d300_se_potriveste(asistent, patron, firma_tva):
    """119. D300: TVA deductibilă 0, deși 4426 avea 451,50.
    Pașii contabilului: NIR fără factură (10 × 215 lei + TVA 21%) salvat de asistent, notele lui validate -> Balanța lunii nu are TVA
    deductibilă pe 4426 (TVA-ul stă neexigibil pe 4428.01 până vine factura, CF art.299 alin.(1) lit.a) -> D300 pe luna aceea are
    deductibila 0 și intră în coadă (nu mai e diferență D300 ↔ 4426)."""
    data = LUNA_DOUA.replace(day=10).isoformat()
    st, r = _api(ASISTENT, "POST", "/tenants/%d/stocuri/nir" % firma_tva["tenant_id"],
                 {"numar": "D119", "data": data, "furnizor": "Furnizor Proba E2E SRL", "factura_id": None,
                  "linii": [{"denumire": "Marfa D119", "cantitate": 10, "pret_achizitie": 215, "pret_vanzare": 330, "cota_tva": 21}]})
    assert st == 200 and "eroare" not in r, (st, r)
    for nid in r["inregistrari"]:
        st, r2 = _api(PATRON, "POST", "/tenants/%d/jurnal/%d/valideaza" % (firma_tva["tenant_id"], nid), {})
        assert st == 200, (st, r2)
    linii = sql('SELECT l.cont_debit, l.suma::text FROM "%s".inregistrari_linii l WHERE l.inregistrare_id = ANY(%%s) AND '
                "l.cont_debit LIKE '442%%%%'" % firma_tva["schema"], (r["inregistrari"],))
    assert linii == [("4428.01", "451.50")], linii
    _genereaza(patron, firma_tva, "d300", LUNA_DOUA.year, LUNA_DOUA.month)
    text = _trimite_declaratia(patron)
    patron.captura()
    assert "TVA-ul ei nu se potrivește cu balanța" not in text, text[:2000]
    assert "Trimisă în coada de validare" in text, text[:2000]


def test_def_107_factura_dupa_nir_fara_factura_nu_incarca_371_a_doua_oara(patron, firma_tva):
    """107. Factură/NIR: factura după NIR „fără factură” încărca de două ori 371.
    Pașii contabilului: asistentul salvează NIR-ul D107 fără factură (10 × 100 lei, furnizorul X) -> vine factura primită a
    furnizorului X (1.000 + TVA) -> în Istoric facturi, „Contează”: aplicația propune legarea de NIR-ul D107 -> „Leagă de NIR-ul
    ales”: nota facturii închide 408 (408 = 401 1.210,00 cu TVA, 4426 = 4428.01 210,00), fără al doilea 371 = 401."""
    cui = cui_cu_control(32000002)
    st, r = _api(ASISTENT, "POST", "/tenants/%d/stocuri/nir" % firma_tva["tenant_id"],
                 {"numar": "D107", "data": AZI.isoformat(), "furnizor": "Furnizor D107 SRL", "cui": cui,
                  "linii": [{"denumire": "Marfa D107", "cantitate": 10, "pret_achizitie": 100, "pret_vanzare": 150, "cota_tva": 21}]})
    assert st == 200 and "eroare" not in r, (st, r)
    st, f = _api(PATRON, "POST", "/tenants/%d/facturi" % firma_tva["tenant_id"],
                 {"numar": "FD107", "data_emitere": AZI.isoformat(), "directie": "primita", "tert_nume": "Furnizor D107 SRL",
                  "tert_cui": cui, "linii": [{"descriere": "Marfa D107", "cantitate": 10, "pret_unitar": 100, "cota_tva": 21}]})
    assert st == 200, (st, f)
    fid = f["factura_id"]
    pg = patron.pg
    _istoric(patron, firma_tva)
    rand = pg.locator(".fereastra:last-of-type .fac-frand-btn", has_text="FD107").first
    rand.locator(".fac-cont").click()
    pg.wait_for_selector(".fereastra:last-of-type #nir-legat", timeout=30000)
    ales = pg.eval_on_selector(".fereastra:last-of-type #nir-legat", "s => s.options[s.selectedIndex].text")
    patron.captura("propunere")
    assert ales.startswith("NIR nr D107 ") and ales.endswith("— propus"), ales
    pg.click(".fereastra:last-of-type #nir-leaga")
    pg.wait_for_function("(f) => { const o = document.querySelector('#caseta-atentie-activa #ca-ok'); if (o) { o.click(); return false; }"
                         " return ![...document.querySelectorAll('.fereastra')].pop().querySelector('#nir-legat'); }", arg=fid, timeout=30000)
    pg.wait_for_timeout(1500)
    patron.captura("contata")
    linii = sql('SELECT l.cont_debit, l.cont_credit, l.suma::text FROM "%s".inregistrari_linii l JOIN "%s".inregistrari i '
                'ON i.id = l.inregistrare_id WHERE i.factura_id = %%s ORDER BY l.id' % (firma_tva["schema"], firma_tva["schema"]), (fid,))
    assert linii and not [x for x in linii if x[0] == "371"], linii
    assert sorted(linii) == [("408", "401", "1210.00"), ("4426", "4428.01", "210.00")], linii


def test_def_134_notele_de_stoc_au_jurnalul_lor_in_d406(patron, firma_tva):
    """134. D406: notele de stocuri în jurnalul DIVERSE.
    Pașii contabilului: luna cu NIR-ul D119 validat (notele lui au sursa „stocuri”) -> Declarații -> D406 pe luna aceea -> „Vezi
    XML-ul generat”: notele NIR-ului sunt în jurnalul STOCURI, nu în DIVERSE."""
    assert sql('SELECT 1 FROM "%s".nir WHERE numar = %%s' % firma_tva["schema"], ("D119",)), "rulează după testul 119 (NIR-ul D119)"
    _genereaza(patron, firma_tva, "d406", LUNA_DOUA.year, LUNA_DOUA.month)
    pg = patron.pg
    pg.click(".fereastra:last-of-type details.dec-xml > summary:has-text('Vezi XML-ul generat')")
    xml = pg.inner_text(".fereastra:last-of-type details.dec-xml[open] .dec-xml-pre")
    patron.captura()
    assert re.search(r"<(\w+:)?JournalID>STOCURI</", xml), xml[:3000]
    jurnale = re.findall(r"<(?:\w+:)?JournalID>([^<]+)</", xml)
    assert "DIVERSE" not in jurnale, jurnale


def test_def_131_factura_multi_cota_spune_regula_anaf_in_rezumat(patron, firma_tva):
    """131. D394: rândul pe cota 11% cu 0 facturi.
    Pașii contabilului: factura emisă cu o linie la 21% și una la 11% -> Declarații -> D394 pe luna ei -> „Rezumat”: factura se
    numără o singură dată, la cota cu TVA-ul cel mai mare (21%), iar la 11% apare cu 0 facturi — regula OPANAF 2194/2025 (secțiunea a
    2-a pct.5), spusă pe ecran ca cifra 0 să nu pară o pierdere."""
    st, r = _api(PATRON, "POST", "/tenants/%d/facturi" % firma_tva["tenant_id"],
                 {"numar": "MC131", "data_emitere": LUNA_TRECUTA.replace(day=15).isoformat(), "directie": "emisa",
                  "tert_nume": "Client Multi Cota SRL", "tert_cui": cui_cu_control(33000003),
                  "linii": [{"descriere": "Marfa 21", "cantitate": 1, "pret_unitar": 1000, "cota_tva": 21},
                            {"descriere": "Carte 11", "cantitate": 1, "pret_unitar": 200, "cota_tva": 11}]})
    assert st == 200, (st, r)
    _genereaza(patron, firma_tva, "d394", LUNA_TRECUTA.year, LUNA_TRECUTA.month)
    casete = patron.pg.evaluate("() => [...[...document.querySelectorAll('.fereastra')].pop().querySelectorAll('.caseta-info')]"
                                ".map((c) => c.innerText.trim())")
    patron.captura()
    rez = next((c for c in casete if c.startswith("Rezumat")), "")
    assert "are operațiuni pe cotele 11%, 21%" in rez or "are operațiuni pe cotele 21%, 11%" in rez, casete
    assert "se numără o singură dată, la cota cu TVA-ul cel mai mare (21%); la 11% apare cu 0 facturi" in rez, rez


def test_def_135_planul_de_conturi_fara_731_738(patron, firma_e2e):
    """135. Plan de conturi: conținea 731–738.
    Pașii contabilului: deschide firma -> Plan de conturi -> caută „73”. Planul unei societăți comerciale nu are conturile 731–738
    (OMFP 3103/2017, entități fără scop patrimonial); se vede 722 / 741 din jur, nu 731…738."""
    pg = patron.pg
    patron.firma(firma_e2e["nume"])
    _deschide(patron, "#fa-planconturi", "Plan de conturi")
    pg.wait_for_selector(".fereastra:last-of-type .pf-frand[data-simbol='722']", timeout=20000)
    simboluri = pg.eval_on_selector_all(".fereastra:last-of-type .pf-frand[data-simbol]", "els => els.map(e => e.dataset.simbol)")
    assert "741" in simboluri and "722" in simboluri, simboluri[:20]
    interzise = [s for s in simboluri if re.match(r"^73[1-8]", s)]
    pg.fill(".fereastra:last-of-type #pcf-cauta", "73")
    pg.wait_for_timeout(300)
    patron.captura()
    assert not interzise, "planul firmei noi conține %s" % interzise
