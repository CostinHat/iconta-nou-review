# -*- coding: utf-8 -*-
"""Lotul 5, comanda 3 (Costin 15.10.2026 noaptea, verbatim în DECIZII „Lotul 5 — comanda 3”) — partea coordonatorului: 259 (motivul
sub textul notei), 260 (titlul editorului urmează data), 264 (diacriticele din editarea asistentului), 267 (ciorna formularului de
înregistrare). Pe aplicația de probă, pe baza de TEST, pe o firmă sintetică alocată asistentului."""
import datetime
import os
import sys

import pytest

from conftest import BAZA, INALT, LAT, Ecran, _scoate_firmele_e2e, sql

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_bloc_d import ASISTENT, PATRON, _firma_noua, _jurnal   # noqa: E402
from e2e_ciorne_proprii import _nota   # noqa: E402
from e2e_invitatii import _client_nou, mod_inregistrare   # noqa: E402
from e2e_inregistrare_libera import _asteapta_turnstile   # noqa: E402


@pytest.fixture(scope="module")
def firma_c3():
    f = _firma_noua("C3L5")          # alocată asistentului (`_atribuie_asistentului`)
    try:
        yield f
    finally:
        _scoate_firmele_e2e(f["tenant_id"])


def test_def_259_motivul_sta_sub_textul_notei_nu_in_coloana_butoanelor(asistent, firma_c3):
    """259. Registru jurnal, ca Ana Asistent: pe ciorna contabilului-șef, motivul („e ciorna lui …”) stă sub textul notei, nu în coloana
    butoanelor; textul notei ocupă cel puțin jumătate din rând (înainte, motivul lărgea coloana butoanelor și strângea textul)."""
    nid = _nota(PATRON, firma_c3["tenant_id"], "Ciorna contabilului-șef 259, cu o descriere destul de lungă cât să se vadă strângerea")
    _jurnal(asistent, firma_c3)
    m = asistent.pg.evaluate("""(i) => { const r = document.querySelector(`.fereastra:last-of-type [data-nota-id='${i}']`);
        const mot = r.querySelector('.jn-a-altuia'), txt = r.querySelector('.pf-frand-text'), but = r.querySelector('.pf-frand-butoane');
        return {in_text: !!(mot && mot.closest('.pf-frand-text')), w_text: txt.getBoundingClientRect().width,
                w_but: but.getBoundingClientRect().width, w_rand: r.getBoundingClientRect().width}; }""", nid)
    asistent.captura()
    assert m["in_text"] is True, m
    assert m["w_text"] > m["w_but"] and m["w_text"] >= 0.5 * m["w_rand"], m


def test_def_260_titlul_notei_noi_urmeaza_data_aleasa(patron, firma_c3):
    """260. Registru jurnal, „+ Notă nouă”: titlul era „Notă nouă · 01.10.2026” oricare ar fi fost data notei. Alegând altă dată, titlul
    o arată pe aceea."""
    _nota(PATRON, firma_c3["tenant_id"], "Nota de pornire 260")
    _jurnal(patron, firma_c3)
    pg = patron.pg
    pg.click(".fereastra:last-of-type #j-nota-noua")
    pg.wait_for_selector("#je-data", timeout=10000)
    zi = datetime.date.today().replace(day=17)
    pg.fill("#je-data", zi.isoformat())
    titlu = pg.inner_text("#je-titlu")
    patron.captura()
    assert titlu == "Notă nouă · %s" % zi.strftime("%d.%m.%Y"), titlu


def test_def_264_editarea_asistentului_are_diacritice(patron):
    """264. Asistenți -> „Editează” la un asistent: titlul, secțiunea competențelor, nota despre bifare și butonul de dezactivare au
    diacriticele („Editează”, „Alege competențe”, „stare finală”, „Dezactivează asistentul”)."""
    (nume,) = sql("SELECT COALESCE(NULLIF(btrim(concat_ws(' ', prenume, nume)), ''), email) FROM public.users WHERE email = %s",
                  (ASISTENT,))[0]
    pg = patron.pg
    patron.acasa()
    pg.click("button.cab-card:has([data-cheie='asistenti'])")
    pg.wait_for_selector("#asi-lista .val-card", timeout=20000)
    pg.locator("#asi-lista .val-card", has_text=nume).first.locator("[data-act='edit']").click()
    pg.wait_for_selector("#asi-dezactiveaza", timeout=10000)
    fer = pg.locator(".fereastra").last
    titlu = (fer.get_attribute("aria-label") or "") + " | " + fer.locator(".pf-titlu").first.inner_text()
    corp = fer.inner_text()
    patron.captura()
    assert titlu.count("Editează — %s" % nume) == 2, titlu       # numele ferestrei și titlul ei
    assert pg.inner_text("#asi-dezactiveaza") == "Dezactivează asistentul"
    assert corp.count("Alege competențe") == 1 and corp.count("stare finală") == 1, corp[:400]


EMAIL_267 = "e2e.ciorna267@exemplu.ro"


@pytest.fixture()
def inregistrare_libera():
    era = mod_inregistrare("libera")
    sql("DELETE FROM public.inregistrari_in_asteptare WHERE email = %s", (EMAIL_267,))
    sql("DELETE FROM public.cereri_ritm WHERE cheie IN ('inregistrare_ip', 'inregistrare_email')")
    try:
        yield
    finally:
        sql("DELETE FROM public.inregistrari_in_asteptare WHERE email = %s", (EMAIL_267,))
        mod_inregistrare(era or "invitatie")


def test_def_267_formularul_de_inregistrare_se_pastreaza_fara_parole(browser, request, inregistrare_libera):
    """267. „Înregistrează cabinetul tău”: ce s-a completat se pierdea la închiderea formularului sau la ieșirea din pagină. Acum: închis
    și redeschis -> datele sunt acolo (fără parole), cu nota că au fost păstrate; la fel după reîncărcarea paginii; după trimiterea
    reușită, formularul redeschis e gol."""
    ctx = browser.new_context(viewport={"width": LAT, "height": INALT})
    viz = Ecran(ctx.new_page(), request.node.name)
    pg = viz.pg
    try:
        _client_nou(pg, BAZA + "/")
        pg.wait_for_selector("#reg-email", timeout=10000)
        date = {"#reg-cabinet": "Cabinet Ciornă 267", "#reg-nume-admin": "Test 267", "#reg-email": EMAIL_267}
        for sel, v in date.items():
            pg.fill(sel, v)
        pg.fill("#reg-parola", "Parola-267-x")
        pg.fill("#reg-parola2", "Parola-267-x")
        pg.check("#reg-termeni")
        pg.click("#acces-x")                                               # închis

        def refacut():
            pg.wait_for_selector("#reg-email", timeout=10000)
            return ({s: pg.input_value(s) for s in date}, pg.input_value("#reg-parola"), pg.input_value("#reg-parola2"),
                    pg.is_checked("#reg-termeni"), pg.is_visible("#reg-ciorna"))
        _client_nou(pg, BAZA + "/")
        assert refacut() == (date, "", "", True, True)
        viz.captura("redeschis")
        pg.goto("about:blank")                                             # ieșirea din pagină
        _client_nou(pg, BAZA + "/")
        assert refacut() == (date, "", "", True, True)
        viz.captura("dupa_iesire")
        pg.fill("#reg-parola", "Parola-267-x")
        pg.fill("#reg-parola2", "Parola-267-x")
        _asteapta_turnstile(pg)
        pg.click("#reg-buton")
        pg.wait_for_selector("#reg-verifica", timeout=20000)               # cererea s-a creat
        pg.goto("about:blank")
        _client_nou(pg, BAZA + "/")
        assert refacut() == ({s: "" for s in date}, "", "", False, False)
        viz.captura("dupa_trimitere")
        assert not viz.erori and not viz.cereri_rele
    finally:
        ctx.close()


EMAIL_C39 = "e2e.c39@exemplu.ro"


def _curata_cont(email):
    uids = [r[0] for r in sql("SELECT id FROM public.users WHERE email = %s", (email,))]
    if not uids:
        return
    for (tabel,) in sql("SELECT c.table_name FROM information_schema.columns c JOIN information_schema.tables t ON t.table_schema = "
                        "c.table_schema AND t.table_name = c.table_name AND t.table_type = 'BASE TABLE' WHERE c.table_schema = "
                        "'public' AND c.column_name = 'user_id' AND c.table_name <> 'users'"):
        sql('DELETE FROM public."%s" WHERE user_id = ANY(%%s)' % tabel, (uids,))
    sql("DELETE FROM public.users WHERE id = ANY(%s)", (uids,))


def test_def_c39_mesajul_cabinetului_ajunge_in_email_ca_text_nu_ca_html(firma_c3):
    """C39. Contabilul-șef dă acces la portal unui client, cu un mesaj care conține etichete HTML: emailul clientului arată mesajul ca
    text (etichetele escapate, rândurile păstrate), nu ca markup."""
    import glob
    import json
    from e2e_bloc_d import _api
    _curata_cont(EMAIL_C39)
    try:
        st, r = _api(PATRON, "POST", "/tenants/%d/client-acces" % firma_c3["tenant_id"],
                     {"email": EMAIL_C39, "nume": "Client C39", "mesaj": 'Bună <b id="injectat">ziua</b>\nRândul doi'})
        assert st == 200, (st, r)
        (m,) = [json.load(open(f, encoding="utf-8")) for f in sorted(glob.glob(os.path.join(os.environ["ICONTA_EMAIL_CUTIE"], "*.json")))
                if json.load(open(f, encoding="utf-8"))["catre"] == EMAIL_C39]
        assert m["html"].count("Bună &lt;b id=&quot;injectat&quot;&gt;ziua&lt;/b&gt;<br>Rândul doi") == 1, m["html"][:400]
        assert m["html"].count('<b id="injectat">') == 0
    finally:
        _curata_cont(EMAIL_C39)
