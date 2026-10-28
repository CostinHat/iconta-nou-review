# -*- coding: utf-8 -*-
"""Lotul 13, comanda 13.1 (verbatim în DECIZII „Comanda 13.1”), zona admin — ecranele cabinetului:

  * 562 prezentarea aplicației nu se mai deschide singură la prima logare; asistentul nu vede pașii administratorului;
  * 563 aceeași numărătoare a notelor de validat: cardul de pe pagina principală și „De validat” numără NOTE;
  * 570 notificarea de control fiscal spune culoarea ecranului („de urmărit”, nu „în roșu”);
  * 571 Control fiscal: „comparat cu decontul generat azi”, nu „ce s-a depus nu s-a păstrat”;
  * 572 triajul AI: răspunsul ghicit nu pleacă la om, confirmarea la stânga; 573 motivul escaladării în Panou Admin, confirmarea cu
    diacritice;
  * 574 (+ 575) Tipare de erori: numai respingerile omului (și notele), valorile sub coloane; 576 analiza AI sub prag refuzată;
  * 648 răspunsul echipei ajunge în clopoțel;
  * 458.1 retragerea proprie regenerată nu e eroare a echipei; C87.1 „Declarații și note lucrate” în cuvintele aplicației.

Pe aplicația din index, pe baza de TEST, cu AI simulat (`ICONTA_AI_SIMULAT`). Rândurile de coadă sintetice stau pe perioade 2099."""
import contextlib
import json
import os
import sys
import time

import pytest

from conftest import BAZA, _ecran, ai_pregateste, ai_prompturi, sql

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_bloc_a import T_COMERT, cont_asistent, ecran_cont   # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.common import cate   # noqa: E402

SUPERADMIN = "admin@prisma-cont.test"
PATRON = "patron@prisma-cont.test"


@pytest.fixture()
def superadmin(browser, request):
    yield from _ecran(browser, request, SUPERADMIN)


def _uid(email):
    return sql("SELECT id FROM public.users WHERE email = %s", (email,))[0][0]


def _rand_coada(cab, tid, fel, tip, perioada, creat_de, creat_la, stare="la_senior", respins_de=None, respins_la=None, motiv=None,
                payload=None):
    # date-de-pornire: rândurile cozii pe care le scriu pregătirea, regenerarea și respingerea (drumurile lor sunt probate în loturile 7–12)
    return sql("INSERT INTO public.declaratii_coada (cabinet_id, tenant_id, fel, tip, perioada, stare, payload, creat_de, creat_de_id, "
               "creat_la, respins_de, respins_de_id, respins_la, motiv_respingere) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
               "RETURNING id", (cab, tid, fel, tip, perioada, stare, json.dumps(payload or {}), str(creat_de), creat_de, creat_la,
                                str(respins_de) if respins_de else None, respins_de, respins_la, motiv))[0][0]


# ── 562 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_562_prezentarea_nu_se_deschide_singura_iar_asistentul_nu_vede_pasii_administratorului(browser, request):
    """562. Pașii asistentului junior (numai „Poate pregăti”), la prima intrare: pagina principală, fără nicio fereastră deschisă singură;
    „?” -> „Prezentarea aplicației”: fără firul de preluare (vector fiscal, solduri inițiale, asociați, migrare cabinet — pașii
    administratorului), cu cardurile lui de început. ROȘU înainte: fereastra „bun venit” se deschidea singură, cu pașii administratorului."""
    with cont_asistent(pregati=True, valida=False, firme=(T_COMERT,), bun_venit_vazut=False) as a, \
            ecran_cont(browser, request, a["email"]) as e:
        pg = e.pg
        pg.goto(BAZA + "/", wait_until="domcontentloaded")
        pg.wait_for_selector(".cab-grila", timeout=30000)
        pg.wait_for_timeout(2000)
        assert pg.query_selector(".bun-venit-overlay, .fereastra") is None, "s-a deschis o fereastră fără clic"
        e.captura("pagina_principala")
        pg.click("#nav-ghid")
        pg.wait_for_selector(".fereastra .ans-continut [data-card='ans-card-inceput']", timeout=30000)   # [lotul 14, 687] „Primii pași” e un card, deschis la clic
        pg.wait_for_timeout(800)
        t = pg.inner_text(".fereastra .ans-continut")
        e.captura("prezentarea")
        pg.click("[data-card='ans-card-inceput']")
        pg.wait_for_selector(".fereastra #ans-inceput", timeout=30000)
        pg.wait_for_timeout(800)
        assert pg.query_selector(".fereastra .ans-fir, .fereastra .ans-pas-titlu, #ans-alta-aplicatie") is None, \
            "asistentul primește firul de pași al administratorului"
        # pașii de preluare nu sunt la el (catalogul „Ce cuprinde aplicația” poate numi funcțiile — „Vector fiscal per firmă” —, nu pașii)
        assert "Firul de intrare" not in t and "Vii din altă aplicație" not in t, t[:500]
        assert "Lucrezi pe firmele pe care ți le alocă administratorul cabinetului" in t, t[:300]


# ── 563 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture()
def document_cu_doua_note(firma_e2e):
    cab = sql("SELECT accounting_firm_id FROM public.tenants WHERE id = %s", (firma_e2e["tenant_id"],))[0][0]
    asist = _uid("asistent@prisma-cont.test")
    p = {"grup": "factura-990563", "doc": "factura-990563", "document_ref": "Factura E2E563 nr. 1", "data": "2099-01-15", "total": "121.00",
         "rulaj": "121.00", "descriere": "Contare factura E2E563"}
    ids = [_rand_coada(cab, firma_e2e["tenant_id"], "nota", "nota", "nota-99056%d" % i, asist, "2099-01-15 10:0%d" % i,
                       payload=dict(p, inregistrare_id=990560 + i)) for i in (1, 2)]
    try:
        yield ids
    finally:
        sql("DELETE FROM public.declaratii_coada WHERE id = ANY(%s)", (ids,))


def test_def_563_cardul_si_de_validat_numara_aceleasi_note(patron, document_cu_doua_note):
    """563. Un document (o factură) cu două note la validare -> pagina principală: cardul spune N note de validat; „De validat”:
    „Note de validat (N)” — același N (note, nu documente); rândul documentului spune „2 note ale documentului”. ROȘU înainte: cardul și
    fereastra numărau documente, iar Registrul jurnal note (8 / 6 / 5)."""
    pg = patron.pg
    patron.acasa()
    pg.wait_for_function("() => /not[ăe] de validat/.test((document.querySelector(\".cab-card-sinteza[data-cheie='validat']\") || {}).innerText || '')",
                         timeout=30000)
    card = pg.inner_text(".cab-card-sinteza[data-cheie='validat']")
    import re
    n_card = int(re.search(r"(\d+)\s+(?:de\s+)?not[ăe] de validat", card).group(1))
    pg.click("button.cab-card:has([data-cheie='validat'])")
    pg.wait_for_selector("#val-note-titlu", timeout=30000)
    titlu = pg.text_content("#val-note-titlu")                    # textul, nu forma afișată (titlul e cu majuscule din CSS)
    patron.captura()
    n_fer = int(re.search(r"Note de validat \((\d+)\)", titlu).group(1))
    assert n_card == n_fer, (card, titlu)
    tb = pg.locator("#val-note tbody.tn-nota[data-coada-ids='%s']" % ",".join(str(i) for i in document_cu_doua_note))
    assert tb.count() == 1 and "2 note ale documentului" in tb.inner_text(), tb.count()
    rand = len(pg.eval_on_selector_all("#val-note tbody.tn-nota", "els => els"))
    assert n_fer > rand - 1, (n_fer, rand)                          # numără note: documentul cu 2 note adaugă 2, rândul lui unul


# ── 570 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_570_notificarea_de_control_fiscal_spune_culoarea_ecranului(patron, firma_e2e):
    """570. Notificarea agregată a controlului fiscal (textul `alerte_control_fiscal.text_alerta`, cel scris de cronul zilnic) -> clopoțel:
    „… 2 controale fiscale de urmărit (TVA, D112 (salarii))”, nu „în roșu” — galbenul detaliului firmei. ROȘU înainte: „în roșu”."""
    from core.alerte_control_fiscal import text_alerta
    uid = _uid(PATRON)
    t = text_alerta(firma_e2e["nume"], [("tva", "TVA"), ("d112", "D112 (salarii)")])
    # date-de-pornire: cronul zilnic (`alerte_control_fiscal.ruleaza`) scrie notificarea; plasa nu așteaptă 08:00
    nid = sql("INSERT INTO public.notificari (user_id, tip, text, link) VALUES (%s, 'control_fiscal', %s, %s) RETURNING id",
              (uid, t, "control-fiscal:%d" % firma_e2e["tenant_id"]))[0][0]
    try:
        pg = patron.pg
        patron.acasa()
        pg.click("#nav-clopot")
        it = pg.locator(".clopot-item", has_text=firma_e2e["nume"]).first
        it.wait_for(timeout=20000)
        txt = it.inner_text()
        patron.captura()
        assert "2 controale fiscale de urmărit (TVA, D112 (salarii))" in txt and "roșu" not in txt, txt
    finally:
        sql("DELETE FROM public.notificari WHERE id = %s", (nid,))


# ── 571 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture()
def firma_ctrl():
    from conftest import firma_noua
    for f in firma_noua():
        yield f


def test_def_571_control_fiscal_spune_ca_se_compara_cu_declaratia_generata_azi(patron, firma_ctrl):
    """571. Firmă plătitoare cu o factură validată în luna trecută, fără D300 depus prin aplicație -> Control fiscal -> firma ->
    «Declarație vs contabilitate»: sub rând „comparat cu decontul generat azi din evidență, nu cu cel depus”; nicăieri „nu s-a păstrat”.
    ROȘU înainte: „recalculat acum — ce s-a depus nu s-a păstrat …” (citit ca pierdere de date)."""
    from e2e_bloc_a import pregateste_firma
    from e2e_bloc_d import _control_firma
    from e2e_lot12_ctrl import LUNA_TRECUTA, _factura_validata
    pregateste_firma(patron, firma_ctrl, platitor=True, regim_fiscal="micro")
    _factura_validata(firma_ctrl, "E2E571-1", LUNA_TRECUTA.replace(day=10))
    _control_firma(patron, firma_ctrl)
    pg = patron.pg
    pg.wait_for_selector(".fereastra:last-of-type #cf-incrucisat", timeout=60000)
    pg.locator(".fereastra:last-of-type #cf-incrucisat").scroll_into_view_if_needed()
    text = " ".join(pg.inner_text(".fereastra:last-of-type").split())
    patron.captura()
    assert "comparat cu decontul generat azi din evidență, nu cu cel depus" in text, text[-1500:]
    assert "nu s-a păstrat" not in text, text[-1500:]


# ── 572 / 573 / 648 ────────────────────────────────────────────────────────────────────────────────────────────────────────────
TEXT_ESCALADARE = "Sesizarea ta a fost transmisă echipei iConta.eu. Vei primi răspunsul aici, în acest fir."


def _sesizare(e, text):
    pg = e.pg
    e.acasa()
    pg.click("[data-banda='raport']")
    pg.wait_for_selector("#rap-text", timeout=20000)
    pg.fill("#rap-text", text)
    pg.click("#rap-trimite")
    pg.wait_for_function("() => document.querySelector('#rap-msg').innerText.includes('Sesizare trimisă')", timeout=20000)


@contextlib.contextmanager
def _sesizarile_patronului():
    uid = _uid(PATRON)
    peste = sql("SELECT COALESCE(max(id), 0) FROM public.raportari")[0][0]
    try:
        yield uid, peste
    finally:
        sql("DELETE FROM public.notificari WHERE user_id = %s AND tip = 'raspuns_suport' AND creat_la > now() - interval '1 hour'", (uid,))
        sql("DELETE FROM public.raportari_mesaje WHERE raportare_id IN (SELECT id FROM public.raportari WHERE autor_id = %s AND id > %s)",
            (uid, peste))
        sql("DELETE FROM public.raportari WHERE autor_id = %s AND id > %s", (uid, peste))


def _sesizarea_triata(patron, text, peste):
    """Suport -> sesizarea `text`; așteaptă triajul AI (simulat) în fir. -> id-ul sesizării (cea nouă, peste `peste`)."""
    _sesizare(patron, text)
    for _ in range(60):
        r = sql("SELECT r.id FROM public.raportari r JOIN public.raportari_mesaje m ON m.raportare_id = r.id AND m.rol_autor = 'ai' "
                "WHERE r.autor_id = %s AND r.id > %s", (_uid(PATRON), peste))
        if r:
            return r[0][0]
        time.sleep(0.5)
    raise AssertionError("triajul AI nu a scris în fir")


def test_def_572_raspunsul_ghicit_nu_pleaca_la_om(patron):
    """572. AI simulat: răspunde ghicit („De obicei…”), fără diacritice, cu un rol din cod. Pașii: Suport -> „Cum adaug un asistent nou?”
    -> firul primește confirmarea escaladării (nu răspunsul ghicit), la stânga, cu textul aliniat la stânga; sesizarea e escaladată cu
    motivul „Asistentul AI a încercat să răspundă, dar …”. ROȘU înainte: răspunsul ghicit ajungea la om."""
    ai_pregateste(json.dumps({"decizie": "raspund", "raspuns": "De obicei apesi pe + in Asistenti. Rolul admin_firma poate adauga."}))
    with _sesizarile_patronului() as (uid, peste):
        rid = _sesizarea_triata(patron, "Cum adaug un asistent nou?", peste)
        assert ai_prompturi(), "modelul (simulat) n-a fost întrebat"
        pg = patron.pg
        patron.acasa()
        pg.click("[data-banda='raport']")
        pg.click(".rap-fir[data-id='%d'] .rap-fir-cap" % rid)
        m = pg.locator(".rap-fir[data-id='%d'] .rap-msg-admin" % rid).first
        m.wait_for(timeout=20000)
        txt = " ".join(m.inner_text().split())
        stil = m.evaluate("(e) => [getComputedStyle(e).textAlign, getComputedStyle(e).alignSelf]")
        patron.captura("firul")
        assert TEXT_ESCALADARE in txt and "De obicei" not in txt, txt
        assert stil[0] in ("start", "left") and stil[1] != "flex-end", stil
        (dec, motiv), = sql("SELECT triaj_decizie, triaj_motiv FROM public.raportari WHERE id = %s", (rid,))
        assert dec == "escaladare" and motiv.startswith("Asistentul AI a încercat să răspundă, dar"), (dec, motiv)


def test_def_573_motivul_escaladarii_se_vede_in_panou_admin(patron, browser, request):
    """573. AI simulat: escaladează, cu motivul lui. Pașii: Suport -> sesizarea -> firul primește confirmarea cu diacritice („Sesizarea ta a
    fost transmisă echipei iConta.eu…”); Panou Admin -> Raportări -> „De la AI” -> sesizarea: „Asistentul AI a trimis sesizarea la echipă.
    Motivul: <motivul AI-ului>”. ROȘU înainte: motivul nu se vedea; confirmarea fără diacritice."""
    ai_pregateste(json.dumps({"decizie": "escaladez", "motiv": "Este o eroare de date, nu o întrebare de folosire E2E573."}))
    with _sesizarile_patronului() as (uid, peste):
        rid = _sesizarea_triata(patron, "Balanța nu se închide pe luna trecută E2E573", peste)
        pg = patron.pg
        patron.acasa()
        pg.click("[data-banda='raport']")
        pg.click(".rap-fir[data-id='%d'] .rap-fir-cap" % rid)
        m = pg.locator(".rap-fir[data-id='%d'] .rap-msg-admin" % rid).first
        m.wait_for(timeout=20000)
        assert TEXT_ESCALADARE in " ".join(m.inner_text().split())
        with contextlib.contextmanager(_ecran)(browser, request, SUPERADMIN) as sa:
            sa.pg.goto(BAZA + "/", wait_until="domcontentloaded")
            sa.pg.wait_for_selector(".cab-grila", timeout=30000)
            sa.pg.click("button.cab-card:has([data-cheie='raportari'])")
            sa.pg.click(".rap-tab[data-tab='tine']")
            sa.pg.locator(".rap-rand", has_text="Balanța nu se închide pe luna trecută E2E573").first.click()
            sa.pg.wait_for_selector("#rap-triaj", timeout=20000)
            t = " ".join(sa.pg.inner_text("#rap-triaj").split())
            sa.captura("panou_admin")
            assert t == "Asistentul AI a trimis sesizarea la echipă. Motivul: Este o eroare de date, nu o întrebare de folosire E2E573.", t


def test_def_648_raspunsul_echipei_ajunge_in_clopotel(patron, browser, request):
    """648. Pașii: contabilul trimite o sesizare (AI simulat: escaladează) -> Admin iConta răspunde din Raportări -> clopoțelul
    contabilului, fără să deschidă Suport: „Echipa iConta.eu ți-a răspuns la sesizarea …”; clic -> se deschide Suport. ROȘU înainte:
    clopoțelul nu arăta nimic."""
    ai_pregateste(json.dumps({"decizie": "escaladez", "motiv": "cerere de date"}))
    with _sesizarile_patronului() as (uid, peste):
        _sesizare(patron, "Proba 648: cum export balanța în SAGA?")
        rid = None
        for _ in range(60):
            r = sql("SELECT id FROM public.raportari WHERE autor_id = %s AND id > %s AND pentru_admin", (uid, peste))
            if r:
                rid = r[0][0]
                break
            time.sleep(0.5)
        assert rid, "sesizarea nu a ajuns la echipă"
        with contextlib.contextmanager(_ecran)(browser, request, SUPERADMIN) as sa:
            sa.pg.goto(BAZA + "/", wait_until="domcontentloaded")
            sa.pg.wait_for_selector(".cab-grila", timeout=30000)
            sa.pg.click("button.cab-card:has([data-cheie='raportari'])")
            sa.pg.click(".rap-tab[data-tab='tine']")
            sa.pg.locator(".rap-rand", has_text="Proba 648").first.click()
            sa.pg.wait_for_selector("#rap-text", timeout=20000)
            sa.pg.fill("#rap-text", "Balanța se exportă din Raportări.")
            sa.pg.click("#rap-trimite")
            sa.pg.wait_for_function("() => [...document.querySelectorAll('#rap-mesaje .rap-msg-text')].some((x) => "
                                    "x.innerText.includes('Balanța se exportă'))", timeout=20000)
        pg = patron.pg
        patron.acasa()
        pg.click("#nav-clopot")
        it = pg.locator(".clopot-item", has_text="Echipa iConta.eu ți-a răspuns la sesizarea").first
        it.wait_for(timeout=30000)
        patron.captura("clopot")
        assert "Proba 648" in it.inner_text()
        assert sql("SELECT count(*) FROM public.notificari WHERE user_id = %s AND tip = 'raspuns_suport' AND de_livrat IS NOT NULL", (uid,))[0][0] >= 1
        it.click()
        pg.wait_for_selector("#rap-lista .rap-fir[data-id='%d']" % rid, timeout=20000)


# ── 574 / 575 / 576 / 458.1 / C87.1 ────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture()
def coada_574(firma_e2e):
    """D300 01/2099 al patronului: (1) înlocuit la „Generează din nou” (urmașul în aceeași tranzacție); (2) retras de el însuși cu motiv
    („Depășită, lipsește F1A5”), apoi generat din nou de el (458.1); nota asistentei respinsă de patron, cu motiv."""
    tid = firma_e2e["tenant_id"]
    cab = sql("SELECT accounting_firm_id FROM public.tenants WHERE id = %s", (tid,))[0][0]
    sef, asist = _uid(PATRON), _uid("asistent@prisma-cont.test")
    ids = [
        _rand_coada(cab, tid, "declaratie", "d300", "25.01.2099", sef, "2099-01-10 10:00", "respinsa", sef, "2099-01-10 11:00",
                    "Înlocuită de declarația generată din nou (E2E)."),
        _rand_coada(cab, tid, "declaratie", "d300", "25.01.2099", sef, "2099-01-10 11:00", "respinsa", sef, "2099-01-11 09:00",
                    "Depășită, lipsește E2E574 (servicii UE)"),
        _rand_coada(cab, tid, "declaratie", "d300", "25.01.2099", sef, "2099-01-11 09:02"),
        _rand_coada(cab, tid, "nota", "nota", "nota-990574", asist, "2099-01-12 10:00", "respinsa", sef, "2099-01-12 12:00",
                    "Lipsește documentul justificativ E2E574", {"descriere": "Ridicare numerar E2E574", "document_ref": "CEC E2E574",
                                                                "grup": "nota-990574"}),
    ]
    try:
        yield ids
    finally:
        sql("DELETE FROM public.declaratii_coada WHERE id = ANY(%s)", (ids,))


def _tipare(patron):
    pg = patron.pg
    patron.acasa()
    pg.click("button.cab-card:has([data-cheie='activitate'])")
    pg.click("#opt-tipare")
    pg.wait_for_selector(".tip-ecran", timeout=30000)
    return pg


def test_def_574_tiparele_numara_respingerile_omului_si_notele(patron, coada_574):
    """574 (+ 575, tabelul). Pașii: Activitate -> Tipare de erori: motivul notei respinse de om e în listă („Lipsește documentul
    justificativ E2E574”), „Depășită, lipsește E2E574” (retragerea proprie regenerată) și „Înlocuită…” nu; rândul „Note contabile” în
    tabelul ratelor, cu antetele numerice deasupra cifrelor (la dreapta). ROȘU înainte: înlocuirea numărată, notele lipsă, valori sub
    alte coloane."""
    pg = _tipare(patron)
    t = pg.inner_text(".tip-ecran")
    assert "Lipsește documentul justificativ E2E574" in t and "Depășită, lipsește E2E574" not in t and "Înlocuită de declarația" not in t, t
    rand = pg.locator("#tip-tabel-tipuri tr", has_text="Note contabile")
    assert rand.count() == 1, pg.inner_text("#tip-tabel-tipuri")
    al = pg.evaluate("""() => { const th = document.querySelectorAll('#tip-tabel-tipuri thead th');
        const td = document.querySelector('#tip-tabel-tipuri tbody tr').children;
        return [getComputedStyle(th[1]).textAlign, getComputedStyle(td[1]).textAlign, th.length, td.length]; }""")
    assert al[0] == al[1] == "right" and al[2] == al[3] == 3, al
    patron.captura("tipare")


def test_def_576_analiza_ai_sub_prag_nu_intreaba_modelul(patron, coada_574):
    """576. Pașii: Activitate -> Tipare de erori -> „Generează analiză AI” cu o singură respingere a omului (sub pragul de 5): „Prea puține
    respingeri pentru o analiză”, fără întrebare la model. ROȘU înainte: modelul generaliza dintr-un caz („omite sistematic”)."""
    ai_pregateste("Analiză care n-ar trebui cerută.")
    pg = _tipare(patron)
    pg.click("#tip-ai")
    pg.wait_for_function("() => (document.querySelector('#tip-ai-rez') || {}).innerText.includes('Prea puține respingeri')", timeout=30000)
    patron.captura("analiza_sub_prag")
    assert ai_prompturi() == [], ai_prompturi()


def test_def_458_1_retragerea_proprie_regenerata_nu_e_eroare_a_echipei(patron, coada_574):
    """458.1. Pașii: Asistenți -> „Vezi erorile” (sau „Erori — echipa”): administratorul nu apare cu „Depășită, lipsește E2E574”
    (și-a retras singur declarația și a generat-o din nou); asistenta apare cu respingerea notei. ROȘU înainte: retragerea proprie
    numărată ca respingere."""
    from core import asistenti_api, db
    from conftest import _db
    _db()
    cab = sql("SELECT accounting_firm_id FROM public.users WHERE email = %s", (PATRON,))[0][0]
    with db.get_conn() as c:
        sef = asistenti_api.calitate(c, cab, _uid(PATRON))
    assert "Depășită, lipsește E2E574" not in [x["motiv"] for x in sef["tipare"]], sef["tipare"]
    pg = patron.pg
    patron.acasa()
    pg.click("button.cab-card:has([data-cheie='asistenti'])")
    pg.wait_for_selector("#asi-banner", timeout=30000)
    pg.wait_for_timeout(1500)
    if pg.query_selector("#asi-vezi-erori:not([aria-disabled='true'])"):   # [675] butonul stă mereu; fără erori e inactiv
        pg.click("#asi-vezi-erori")
        # fereastra „Erori — echipa” (lista Asistenți are și ea `.val-card`: se așteaptă textul ferestrei noi)
        pg.wait_for_function("() => /Cine a produs respingeri|Nicio respingere/.test((document.querySelector('.fereastra-corp') || {}).innerText || '')",
                             timeout=20000)
        t = pg.inner_text(".fereastra-corp")
        patron.captura("erori_echipa")
        assert "Depășită, lipsește E2E574" not in t, t[:800]
        assert "Lipsește documentul justificativ E2E574" in t, t[:800]


def test_def_c87_1_activitatea_numeste_notele_si_starile_in_cuvinte(patron, coada_574):
    """C87.1. Pașii: Asistenți -> asistenta -> „Vizualizează”: „Declarații și note lucrate”; rândul notei „Notă · Ridicare numerar E2E574 ·
    CEC E2E574” cu „respinsă”, fără „nota-990574” / „la_senior”; „Acoperire: note contabile”. ROȘU înainte: „nota · nota-143”, „stare:
    la_senior”, „Acoperire: nota”."""
    pg = patron.pg
    patron.acasa()
    pg.click("button.cab-card:has([data-cheie='asistenti'])")
    import re
    prenume, nume, email = sql("SELECT prenume, nume, email FROM public.users WHERE email = 'asistent@prisma-cont.test'")[0]
    nume_rand = " ".join(x for x in (prenume, nume) if x) or email          # cum îl scrie lista Asistenți (ca la C87)
    pg.wait_for_selector("#asi-lista .val-card", timeout=30000)
    al_ei = pg.locator(".asi-nume").filter(has_text=re.compile(r"^\s*%s\s*$" % re.escape(nume_rand)))
    pg.locator("#asi-lista .val-card", has=al_ei).first.locator("[data-act='vezi']").click()
    pg.wait_for_selector(".fereastra:last-of-type #asi-activitate", timeout=30000)
    f = pg.inner_text(".fereastra:last-of-type")
    a = pg.inner_text(".fereastra:last-of-type #asi-activitate")
    patron.captura()
    assert "Declarații și note lucrate" in f and "Notă · Ridicare numerar E2E574 · CEC E2E574" in a, a[:600]
    assert "nota-990574" not in a and "la_senior" not in a and "stare:" not in a, a[:600]
    assert "note contabile" in f and "Acoperire: nota" not in f, f[:800]
