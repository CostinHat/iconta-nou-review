# -*- coding: utf-8 -*-
"""Lotul 13, comanda Costin 13.1 (verbatim în DECIZII „Comanda 13.1”), pachetul PORTAL / P2 — Setări cont (chei API, notificări), sinteza
zilnică, emailul notificărilor, WhatsApp:

  * 564 — Chei API: butonul „Copiază”, ultima folosire în listă, cheia completă dispare la revocare, „Revocă” e buton;
  * 565 — sinteza zilnică apare în Setări cont → Notificări (bifată, numai pe email) și se poate opri;
  * 566 — „O solicitare nouă de la un client” bifată din oficiu, și la contul care și-a salvat bifele cât implicitul era greșit (migrarea);
  * 567 — emailul notificării: propoziție întreagă („Un element pregătit de tine a fost respins.”), cu elementul și firma, fără motiv;
  * 568 — Sinteza zilei: „de validat” = coada întreagă (și elementele de ieri), nu numai ce a intrat azi;
  * 569 — Sinteza zilei, „Ultimele evenimente”: elementul numit prin eticheta lui („Notă · <descriere> · <document>”), nu „NOTA”;
  * 647 — „Trimite codul pe WhatsApp” refuzat de Meta (133010, simulat): avertisment simplu, fără caseta „NU s-a salvat”.

Pe aplicația din index, pe baza de TEST. Nimic nu pleacă: emailurile ajung în cutia de test (`ICONTA_EMAIL_CUTIE`), WhatsApp e simulat
(`ICONTA_WHATSAPP_SIMULAT`, fixtura `meta_refuza` din `e2e_lot12_notif.py`).

DATE DE PORNIRE fără ecran (declarate, regula lui 429): bifele salvate ale patronului (566, cu data de dinainte de reparație), rândul de
notificare din cutia de ieșire (567: textul în forma reală a respingerii unei note, `uc_comun._notif_pregatitor`), elementele din coadă
(568 / 569: o declarație pregătită acum două zile, `coada_api.adauga_in_coada` + data mutată; o notă pregătită azi, forma
`coada_api._insereaza_nota`), an 2099. Toate scoase la final.

Temei: N/A — funcții ale aplicației, nu reguli fiscale. 647: documentația Meta „Error codes”: „133010 — Phone number not registered on the
WhatsApp Business Platform.”
"""
import glob
import json
import os
import re
import sys
import time
import urllib.request

import pytest

from conftest import BAZA, _db, sql

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lot12_notif import meta_refuza   # noqa: E402,F401 — fixtura
from e2e_lot72_cont import deschide_setari_panou   # noqa: E402
from e2e_bloc_d import ASISTENT, _api, _atribuie_asistentului, _in_coada, _respinge   # noqa: E402
from e2e_bloc_e import _sterge_note   # noqa: E402

PATRON = "patron@prisma-cont.test"
_F = ".fereastra:last-of-type "


def _patron_uid():
    return sql("SELECT id, accounting_firm_id FROM public.users WHERE email = %s", (PATRON,))[0]


# ── 564 — Chei API ──────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _chei_api(patron):
    deschide_setari_panou(patron, "Chei API", "#set-cheie-noua")
    patron.pg.wait_for_selector(_F + "#set-chei-lista:not(:has(.ecran-nota))", timeout=25000)


def test_def_564_cheia_api_se_copiaza_spune_folosirea_si_dispare_la_revocare(patron):
    """564. Pașii: Setări cont -> „Chei API” -> numele -> „Generează cheie nouă”: mesajul are butonul „Copiază”, care pune cheia în
    clipboard; rândul cheii spune „creată <zz.ll.aaaa hh:mm> · nefolosită încă” -> o aplicație folosește cheia (`GET /api/v1/firme`) ->
    lista, redeschisă: „folosită ultima dată <zz.ll.aaaa hh:mm>” -> „Revocă” (buton) -> confirmare: cheia completă dispare de pe ecran,
    rândul spune „revocată”, fără „Revocă”. Înainte: fără „Copiază”, ultima folosire numai ISO tăiat, cheia rămânea afișată după revocare,
    „Revocă” era text pe care se dă clic."""
    pg = patron.pg
    nume = "Probă 564 %d" % (int(time.time()) % 100000)
    pg.context.grant_permissions(["clipboard-read", "clipboard-write"], origin=BAZA)
    _chei_api(patron)
    try:
        pg.fill(_F + "#set-cheie-nume", nume)
        pg.click(_F + "#set-cheie-noua")
        pg.wait_for_selector(_F + "#set-msg-chei #set-cheie-copiaza", timeout=25000)
        cheie = pg.inner_text(_F + "#set-cheie-text").strip()
        assert cheie.startswith("ick_") and len(cheie) > 30
        kid = pg.get_attribute(_F + "#set-msg-chei", "data-cheie-id")
        assert kid and kid.isdigit(), kid
        pg.click(_F + "#set-cheie-copiaza")
        pg.wait_for_function("() => document.querySelector('.fereastra:last-of-type #set-cheie-copiaza').innerText.trim() === 'Copiată'",
                             timeout=10000)
        assert pg.evaluate("() => navigator.clipboard.readText()") == cheie
        rand = _F + ".pf-frand[data-cheie-id='%s']" % kid
        pg.wait_for_selector(rand, timeout=20000)
        sub = pg.inner_text(rand + " .pf-frand-sub")
        assert re.fullmatch(r"activă · creată \d{2}\.\d{2}\.\d{4} \d{2}:\d{2} · nefolosită încă", sub.strip()), sub
        assert pg.eval_on_selector(rand + " .set-cheie-revoca", "b => b.tagName") == "BUTTON"
        patron.captura("cheie_noua_copiaza")
        # o aplicație externă folosește cheia (citire)
        cer = urllib.request.Request(BAZA + "/api/v1/firme", headers={"X-Api-Key": cheie})
        with urllib.request.urlopen(cer, timeout=20) as r:
            assert r.status == 200
        _chei_api(patron)
        sub = pg.inner_text(rand + " .pf-frand-sub").strip()
        assert re.search(r"· folosită ultima dată \d{2}\.\d{2}\.\d{4} \d{2}:\d{2}$", sub), sub
        assert not re.search(r"\d{4}-\d{2}-\d{2}", sub), "data în forma aplicației, nu ISO: %s" % sub
        # din nou cheia nouă, apoi revocarea ei: mesajul cu cheia completă dispare
        pg.fill(_F + "#set-cheie-nume", nume + " b")
        pg.click(_F + "#set-cheie-noua")
        pg.wait_for_selector(_F + "#set-msg-chei #set-cheie-copiaza", timeout=25000)
        kid2 = pg.get_attribute(_F + "#set-msg-chei", "data-cheie-id")
        cheie2 = pg.inner_text(_F + "#set-cheie-text").strip()
        rand2 = _F + ".pf-frand[data-cheie-id='%s']" % kid2
        pg.wait_for_selector(rand2 + " .set-cheie-revoca", timeout=20000)
        pg.click(rand2 + " .set-cheie-revoca")
        pg.click("#ca-ok")
        pg.wait_for_function("(s) => /revocată/.test((document.querySelector(s) || {}).innerText || '')", arg=rand2 + " .pf-frand-sub",
                             timeout=20000)
        assert cheie2 not in pg.content(), "cheia completă a rămas pe ecran după revocare"
        assert pg.locator(rand2 + " .set-cheie-revoca").count() == 0
        patron.captura("revocata_cheia_dispare")
    finally:
        r = sql("SELECT id FROM public.api_chei WHERE nume LIKE %s", (nume + "%",))
        for (i,) in r or []:
            # date-de-pornire: curățenie după probă — o cheie rămasă activă după o probă căzută se revocă (nu e o dată a probei)
            sql("UPDATE public.api_chei SET activ = false WHERE id = %s", (i,))


# ── 565 / 566 — Setări cont → Notificări ────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture()
def bifele_patronului():
    """Bifele salvate ale patronului, puse la loc la final."""
    uid, _cab = _patron_uid()
    (tipuri, salvat), = sql("SELECT notificari_tipuri::text, notificari_salvate_la FROM public.users WHERE id = %s", (uid,))
    try:
        yield uid
    finally:
        sql("UPDATE public.users SET notificari_tipuri = %s::jsonb, notificari_salvate_la = %s WHERE id = %s", (tipuri, salvat, uid))


def _notificari(patron):
    deschide_setari_panou(patron, "Notificări", "#not-telefon")
    patron.pg.wait_for_selector(_F + "#not-tipuri [data-tip]", timeout=20000)


def test_def_565_sinteza_zilnica_apare_in_notificari_si_se_poate_opri(patron, bifele_patronului):
    """565. Pașii: administratorul -> Setări cont -> Notificări: grupa „Cont și echipă” are „Sinteza zilei din cabinet”, cu rândul „Seara,
    la 19:00, în zilele lucrătoare: … Vine numai pe email.”, bifată din oficiu -> o debifează -> „Salvează” -> alegerea e salvată (jobul de
    seară n-o mai trimite: `sinteza_zilnica.dorita`). Înainte: sinteza nu apărea nicăieri în Setări cont."""
    pg = patron.pg
    uid = bifele_patronului
    sql("UPDATE public.users SET notificari_tipuri = NULL WHERE id = %s", (uid,))   # fără bife salvate: implicitul
    _notificari(patron)
    bifa = _F + "#not-tipuri input[data-tip='sinteza_zilnica']"
    assert pg.is_checked(bifa)
    eticheta = pg.inner_text(_F + "#not-tipuri label.not-tip:has([data-tip='sinteza_zilnica'])")
    assert "Sinteza zilei din cabinet" in eticheta and "Vine numai pe email." in eticheta, eticheta
    # textContent, nu innerText: titlul grupei e scris cu majuscule din CSS (`.cf-grup-titlu`), textul lui rămâne „Cont și echipă”
    grup = pg.eval_on_selector(bifa, "c => c.closest('.not-grup').querySelector('.cf-grup-titlu').textContent.trim()")
    assert grup == "Cont și echipă", grup
    pg.locator(bifa).scroll_into_view_if_needed()
    patron.captura("sinteza_in_notificari")
    pg.uncheck(bifa)
    pg.click(_F + "#not-salveaza-canal")
    pg.wait_for_function("() => /Alegerile tale sunt salvate/.test(document.querySelector('.fereastra:last-of-type #not-msg').innerText)",
                         timeout=20000)
    (v,), = sql("SELECT notificari_tipuri->>'sinteza_zilnica' FROM public.users WHERE id = %s", (uid,))
    assert v == "false", v
    from core import sinteza_zilnica
    (tipuri,), = sql("SELECT notificari_tipuri FROM public.users WHERE id = %s", (uid,))
    assert sinteza_zilnica.dorita({"notificari_tipuri": tipuri}) is False


def test_def_566_solicitarea_clientului_bifata_si_la_bifele_salvate_inainte(patron, bifele_patronului):
    """566. Pașii: patronul își salvase bifele pe 01.10.2026, cât „O solicitare nouă de la un client” venea debifată din oficiu (date de
    pornire: `solicitare_client: false` salvat) -> migrarea datelor existente (`core/migrare_notificari_solicitare_client.py`) -> Setări
    cont -> Notificări: „O solicitare nouă de la un client” e bifată; la un cont fără bife salvate, la fel (implicitul)."""
    pg = patron.pg
    uid = bifele_patronului
    sql("UPDATE public.users SET notificari_tipuri = '{\"solicitare_client\": false, \"de_validat\": true}'::jsonb, "
        "notificari_salvate_la = '2026-10-01 10:00+03' WHERE id = %s", (uid,))
    from core import migrare_notificari_solicitare_client as M
    db = _db()
    with db.get_conn() as c:
        M.aplica(c)
        c.commit()
    _notificari(patron)
    bifa = _F + "#not-tipuri input[data-tip='solicitare_client']"
    assert pg.is_checked(bifa), "bifa salvată cu implicitul greșit a rămas debifată"
    assert pg.is_checked(_F + "#not-tipuri input[data-tip='de_validat']"), "celelalte bife rămân"
    pg.locator(bifa).scroll_into_view_if_needed()
    patron.captura("vechi_solicitare_client_bifata")
    sql("UPDATE public.users SET notificari_tipuri = NULL WHERE id = %s", (uid,))
    _notificari(patron)
    assert pg.is_checked(bifa), "implicitul: bifată"


# ── 567 — emailul notificării ───────────────────────────────────────────────────────────────────────────────────────────────────
def _emailuri(cutie, catre, inainte):
    out = []
    for f in sorted(set(glob.glob(os.path.join(cutie, "*.json"))) - inainte):
        m = json.load(open(f, encoding="utf-8"))
        if m.get("catre") == catre:
            out.append(m)
    return out


def test_def_567_emailul_notificarii_spune_elementul_si_firma(patron, firma_e2e):
    """567. Pașii: asistentul scrie în Registrul jurnal nota „Plată chirie probă 567” (documentul OP 567), care intră în coada de validare
    -> contabilul-șef o respinge cu motivul „contul 612 nu se potrivește, suma 1.234,00 lei” (ruta butonului „Respinge”) -> aplicația
    face notificarea „respinsă” a asistentului (textul din clopoțel) și o trimite pe email: subiectul „iConta.eu — un element pregătit
    de tine a fost respins”, corpul începe cu propoziția „Un element pregătit de tine a fost respins.” și spune firma și nota; motivul și
    cifrele rămân în aplicație. Înainte: „Ai un element pregătit de tine a fost respins în iConta.eu.”, fără element, fără firmă."""
    (uid_a,), = sql("SELECT id FROM public.users WHERE email = %s", (ASISTENT,))
    (tipuri, canal, salvat), = sql("SELECT notificari_tipuri::text, canal_notificari, notificari_salvate_la FROM public.users WHERE id = %s",
                                   (uid_a,))
    sql("UPDATE public.users SET notificari_tipuri = COALESCE(notificari_tipuri, '{}'::jsonb) || '{\"respinsa\": true}'::jsonb, "
        "canal_notificari = 'email' WHERE id = %s", (uid_a,))   # bifa „respinsă” și canalul email ale asistentului (Setări cont)
    cutie = os.environ["ICONTA_EMAIL_CUTIE"]
    inainte = set(glob.glob(os.path.join(cutie, "*.json")))
    el = _nota_asistentului(firma_e2e, "Plată chirie probă 567", "OP 567")
    try:
        _respinge(el["coada_id"], "contul 612 nu se potrivește, suma 1.234,00 lei")
        (text,), = sql("SELECT text FROM public.notificari WHERE user_id = %s AND tip = 'respinsa' ORDER BY id DESC LIMIT 1", (uid_a,))
        assert firma_e2e["nume"] in text and "Plată chirie probă 567" in text and "Motiv:" in text, text   # textul clopoțelului
        gasite = []
        for _ in range(150):   # bucla de livrare a aplicației: la 30 de secunde
            gasite = [x for x in _emailuri(cutie, ASISTENT, inainte) if "respins" in x["subiect"]]
            if gasite:
                break
            time.sleep(0.5)
        assert len(gasite) == 1, gasite
        m = gasite[0]
        assert m["subiect"] == "iConta.eu — un element pregătit de tine a fost respins", m["subiect"]
        corp = " ".join(m["html"].split())
        assert "Ai un element" not in corp, corp
        assert "<b>Un element pregătit de tine a fost respins.</b>" in corp, corp
        assert firma_e2e["nume"] in corp and "Plată chirie probă 567" in corp and "a fost respinsă." in corp, corp
        assert "Motiv" not in corp and "1.234" not in corp and "612" not in corp, corp
    finally:
        sql("UPDATE public.users SET notificari_tipuri = %s::jsonb, canal_notificari = %s, notificari_salvate_la = %s WHERE id = %s",
            (tipuri, canal, salvat, uid_a))
        _scoate_nota_asistentului(firma_e2e, el)


# ── 568 / 569 — Sinteza zilei ───────────────────────────────────────────────────────────────────────────────────────────────────
def _sinteza_zilei(patron):
    patron.acasa()
    patron.pg.click("button.cab-card:has([data-cheie='brief'])")
    patron.pg.wait_for_selector(_F + ".sa-cifra", timeout=30000)
    patron.pg.wait_for_timeout(500)


def _nota_asistentului(firma, descriere, document_ref):
    """Asistentul scrie o notă în Registrul jurnal (ruta formularului, `POST /tenants/{id}/jurnal`), iar nota intră în coada de validare
    (`e2e_bloc_d._in_coada`, ce face middleware-ul după cererea lui) -> elementul cozii {coada_id, eticheta}."""
    import datetime
    _atribuie_asistentului(firma)
    st, r = _api(ASISTENT, "POST", "/tenants/%d/jurnal" % firma["tenant_id"], {
        "data": datetime.date.today().isoformat(), "descriere": descriere, "document_ref": document_ref,
        "linii": [{"debit": "612", "credit": "401", "suma": 100, "partener_nume": "PARTENER PROBA SRL"}]})
    assert st == 200, (st, r)
    el = [a for a in _in_coada(firma) if descriere in a["eticheta"]]
    assert len(el) == 1, el
    ((per,),) = sql("SELECT perioada FROM public.declaratii_coada WHERE id = %s", (el[0]["coada_id"],))
    return dict(el[0], nota_id=int(per.split("-", 1)[1]))   # perioada elementului = „nota-<id>”


def _scoate_nota_asistentului(firma, el):
    """Curățenia: nota ciornă a asistentului și elementul ei din coadă (`e2e_bloc_e._sterge_note`). Fără ea, nota rămasă ciornă reintră în
    coadă la proba următoare (`pune_notele_in_coada` ia toate ciornele asistentului fără element), iar proba vede două elemente."""
    _sterge_note(firma, [el["nota_id"]])


@pytest.fixture()
def coada_probei(firma_e2e):
    """O declarație D300 2099/01 pregătită acum două zile (în așteptare) și o notă pregătită azi de asistent, pe firma probei. Scoase la
    final."""
    from core import coada_api as c
    uid, cab = _patron_uid()
    db = _db()
    with db.get_conn() as conn:
        r = c.adauga_in_coada(conn, cab, firma_e2e["tenant_id"], "d300", 2099, {"xml": "<x/>"}, creat_de=str(uid), creat_de_id=uid, luna=1)
        conn.commit()
    assert r["ok"], r
    decl = r["coada_id"]
    # date-de-pornire: vârsta declarației din coadă (pregătită acum două zile) — aplicația nu poate scrie o pregătire în trecut
    sql("UPDATE public.declaratii_coada SET creat_la = now() - interval '2 days', inceput_la = now() - interval '2 days' WHERE id = %s",
        (decl,))
    el = _nota_asistentului(firma_e2e, "Plată chirie probă 569", "OP 569")
    nota = el["coada_id"]
    try:
        yield {"cab": cab, "decl": decl, "nota": nota}
    finally:
        sql("DELETE FROM public.declaratii_coada WHERE id = %s", (decl,))
        _scoate_nota_asistentului(firma_e2e, el)


def test_def_568_sinteza_zilei_numara_toata_coada(patron, coada_probei):
    """568. Pașii: în coadă stau o declarație pregătită acum două zile și o notă pregătită azi -> Sinteza zilei: „de validat” = toată
    coada de acum (cât arată și „De validat”), deci cel puțin 2; înainte numai ce a intrat azi (aici 1, ca „1 de validat” cu 5 note + 1
    declarație în coadă pe 22.10)."""
    from core import asistenti_api
    import datetime
    pg = patron.pg
    db = _db()
    azi = datetime.date.today().isoformat()
    with db.get_conn() as conn:
        toata = asistenti_api.centralizator(conn, coada_probei["cab"])["totaluri"]["in_asteptare"]
        numai_azi = asistenti_api.centralizator(conn, coada_probei["cab"], azi, azi)["totaluri"]["in_asteptare"]
        conn.rollback()
    assert toata > numai_azi, (toata, numai_azi)        # calibrarea: declarația de acum două zile e în coadă, nu în „azi”
    _sinteza_zilei(patron)
    vazut = pg.inner_text(_F + ".sa-cifra[data-ecran='validat'] .sa-num").strip()
    patron.captura("de_validat_coada_intreaga")
    assert vazut == str(toata), (vazut, toata, numai_azi)


def test_def_569_evenimentele_sintezei_numesc_elementul(patron, coada_probei):
    """569. Pașii: o notă pregătită azi („Plată chirie probă 569”, documentul OP 569) -> Sinteza zilei -> „Ultimele evenimente”: rândul
    spune „Notă · Plată chirie probă 569 · OP 569”, nu „NOTA” (tipul intern cu majuscule, fără număr și fără descriere)."""
    pg = patron.pg
    _sinteza_zilei(patron)
    ev = pg.eval_on_selector_all(_F + ".sa-jurnal .sa-ev-txt", "els => els.map((e) => e.innerText.replace(/\\s+/g, ' ').trim())")
    patron.captura("evenimente")
    al_notei = [e for e in ev if "Plată chirie probă 569" in e]
    assert al_notei, ev
    assert "Notă · Plată chirie probă 569 · OP 569" in al_notei[0], al_notei
    assert not any(re.search(r"\bNOTA\b", e) for e in ev), ev


# ── 647 — WhatsApp neînregistrat la Meta ────────────────────────────────────────────────────────────────────────────────────────
def test_def_647_whatsapp_neinregistrat_avertisment_fara_nu_s_a_salvat(patron, meta_refuza):
    """647. Pașii: Setări cont -> Notificări (numărul salvat, neconfirmat; Meta refuză cu 133010 „Account not registered”, simulat) ->
    bifa de acord -> „Trimite codul pe WhatsApp”: avertismentul „WhatsApp nu e disponibil acum, … pe email”, fără caseta „NU s-a salvat.”
    (numărul și acordul SUNT salvate) și fără textul Meta; numărul rămâne „nu e confirmat încă”, canalul email."""
    from core.uc_cont_notificari import MESAJ_WA_ESUAT
    pg = patron.pg
    deschide_setari_panou(patron, "Notificări", "#not-telefon")
    pg.wait_for_selector(_F + "#not-cere-cod", state="visible", timeout=20000)
    pg.check(_F + "#not-acord")
    pg.click(_F + "#not-cere-cod")
    pg.wait_for_function("() => /WhatsApp/.test((document.querySelector('.fereastra:last-of-type #not-msg') || {}).innerText || '')",
                         timeout=30000)
    pg.wait_for_timeout(600)
    patron.captura("whatsapp_neinregistrat")
    m = pg.inner_text(_F + "#not-msg").strip()
    assert m == MESAJ_WA_ESUAT, m
    assert "msg-avert" in (pg.get_attribute(_F + "#not-msg", "class") or ""), pg.get_attribute(_F + "#not-msg", "class")
    assert pg.locator(_F + ".refuz-salvare").count() == 0, pg.inner_text(_F + ".refuz-salvare")
    assert "NU s-a salvat" not in pg.inner_text(_F.strip())
    assert not re.search(r"133010|HTTP|Meta |OAuth", pg.inner_text("body")), "textul Meta a ajuns pe ecran"
    assert "nu e confirmat încă" in pg.inner_text(_F + "#not-stare-telefon")
    (canal, acord), = sql("SELECT canal_notificari, acord_whatsapp_la IS NOT NULL FROM public.users WHERE id = %s", (meta_refuza,))
    assert (canal, acord) == ("email", True)
