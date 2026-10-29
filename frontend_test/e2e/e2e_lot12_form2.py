# -*- coding: utf-8 -*-
"""Lotul 12, comanda Costin 12.2 (pct.3, 13, 14, 19; verbatim în DECIZII „Comanda 12.2”), pachetul form2 — formularele:

  * 446.1 — „Avertismentul apare acum o singură dată, corect, dar tabelul se strânge la un rând tăiat, iar întrebarea stă într-o casetă
    roșie.” Clasa: `api.confirmaCaseta` (toate întrebările de confirmare) — caseta neutră `.caseta-intrebare`, întrebarea și butoanele
    pe un rând, în locul butonului principal;
  * 626 — „după ce scrii și golești «Aplică de la», perioada nouă rămâne obligatorie și oprește salvarea. Perioadă nouă doar la cerere.”;
  * 627 — „după o salvare parțială, «Profil incomplet» nu se actualizează.”;
  * 642 — formularul din invitație: „mesajul de refuz apare de două ori; fereastra formularului iese din ecran sus și jos, «Creează cont»
    abia se vede”; iar pe server: contul nu se mai creează fără firma lui (cererea liberă cu CUI-ul greșit, scrisă înainte de verificarea
    de la formular, ca înregistrarea din 23.10).

Pașii contabilului / ai vizitatorului pe aplicația din index, pe baza de TEST, pe firme NOI (`firma_noua`). CUI-ul 12345678 are cifra de
control GREȘITĂ (algoritmul din CLAUDE.md: suma 95, 950 mod 11 = 4 ≠ 8) — e chiar CUI-ul înregistrării din 23.10.

Temei 626: CF art.282 alin.(3^1) (data de la care se aplică sistemul TVA la încasare; regula datei e pe server). Restul: N/A — reguli de UI
(CLAUDE.md §9; DS cap.5, cap.6).
"""
import os
import secrets
import sys

import pytest

from conftest import BAZA, Ecran, firma_noua, sql
from e2e_bloc_a import _card
from e2e_lot11_m import ANTET_MIGRARE, _incarca, _pas
from e2e_lot12_migr import confirma_firma_fisierului, alege_analitic_117

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.test_lot11_m_balanta_saga import fisier   # noqa: E402

LAPTOP = {"width": 1280, "height": 720}
CUI_GRESIT = "12345678"
ROSU = ("rgb(253, 243, 243)", "rgb(217, 140, 140)")      # fundalul și bordura `.caseta-atentie`


@pytest.fixture()
def firma_f2():
    for f in firma_noua():
        yield f


# ── 446.1 — întrebarea înlocuirii nu e roșie, tabelul rămâne citibil ────────────────────────────────────────────────────────────────
def test_def_446_1_intrebarea_inlocuirii_nu_e_rosie_iar_tabelul_ramane_citibil(patron, firma_f2):
    """446.1. Pașii, la 1280×720: firma -> Import date -> Solduri inițiale -> balanța SAGA (21 de conturi) -> 30.09.2026, cantitativ-valoric
    -> „Salvează soldurile” -> din nou Solduri inițiale -> aceeași balanță în forma „total rulaje” -> avertismentul o dată -> „Înlocuiește
    balanța” -> întrebarea „Înlocuiești balanța de deschidere a firmei cu cea din fișier?” într-o casetă NEUTRĂ (`.caseta-intrebare`, nu
    roșul refuzului), cu „Înlocuiesc balanța” / „Renunță” pe rândul ei; tabelul păstrează ≥ 150 px și cel puțin 3 rânduri întregi
    vizibile. ROȘU înainte: `.caseta-atentie` (#fdf3f3 / #d98c8c), bara +91 px, tabelul 10 px (niciun rând) -> „Renunță”: nimic scris."""
    pg, s = patron.pg, firma_f2["schema"]
    _pas(patron, firma_f2, "Solduri ini")
    _incarca(patron, "balanta_saga.csv", fisier("rulaje_precedente"), "#mig-salveaza-sold")
    pg.fill("#mig-data-bal", "2026-09-30")
    pg.select_option("#mig-metoda-stoc", "cantitativ_valoric")
    alege_analitic_117(pg)
    pg.click("#mig-salveaza-sold")
    confirma_firma_fisierului(pg, ANTET_MIGRARE)    # antetul fișierului numește altă firmă (599): întâi confirmarea firmei
    pg.wait_for_function("() => document.body.innerText.includes('21 de conturi salvate')", timeout=30000)
    vp = pg.viewport_size
    pg.set_viewport_size(LAPTOP)
    try:
        _pas(patron, firma_f2, "Solduri ini")
        _incarca(patron, "balanta_saga_2.csv", fisier("total_rulaje"), "#mig-salveaza-sold")
        alege_analitic_117(pg)
        pg.click("#mig-salveaza-sold")
        confirma_firma_fisierului(pg, ANTET_MIGRARE)    # antetul fișierului numește altă firmă (599): întâi confirmarea firmei
        pg.wait_for_function("() => (document.querySelector('#ca-ok') || {}).textContent === 'Înlocuiesc balanța'", timeout=10000)
        o = pg.evaluate("""() => { const c = [...document.querySelectorAll('.fereastra-corp')].pop();
          const rez = c.querySelector('.rezumat-fix'), bara = c.querySelector('.bara-fixa'), th = c.querySelector('table thead');
          const r = (e) => e.getBoundingClientRect(); c.scrollTop = 1e7;
          const sus = Math.max(r(rez).bottom, th ? r(th).bottom : 0), jos = Math.min(r(bara).top, r(c).bottom);
          const randuri = [...c.querySelectorAll('table tbody tr')].filter((t) => r(t).top >= sus - 1 && r(t).bottom <= jos + 1).length;
          const cutie = document.querySelector('#caseta-atentie-activa').firstElementChild, st = getComputedStyle(cutie);
          return {loc: Math.round(jos - sus), randuri, clasa: cutie.className, culori: [st.backgroundColor, st.borderTopColor],
                  intrebare: cutie.innerText}; }""")
        patron.captura("intrebarea")
        assert o["clasa"] == "caseta-intrebare" and not set(o["culori"]) & set(ROSU), o
        assert "Înlocuiești balanța de deschidere a firmei cu cea din fișier?" in o["intrebare"], o
        assert o["loc"] >= 150 and o["randuri"] >= 3, o                  # „tabelul se strânge la un rând tăiat”
        pg.click("#ca-nu")
        assert pg.is_visible("#mig-salveaza-sold") and sql('SELECT count(*) FROM "%s".solduri_initiale' % s)[0][0] == 21
    finally:
        pg.set_viewport_size(vp)


# ── 626 — „Aplică de la” golit nu cere o perioadă nouă ──────────────────────────────────────────────────────────────────────────────
def _tva_incasare_de_la_01_10(s):
    sql('DELETE FROM "%s".tva_incasare_perioade' % s)
    # date-de-pornire: firma plătitoare de TVA, în sistemul TVA la încasare de la 01.10.2026 (ca F2 / F6) — starea scrisă înainte de 626
    sql('UPDATE "%s".firma_profil SET platitor_tva = true, tip_decont = \'lunar\', regim_fiscal = \'micro\', operatiuni_ic = false, '
        'tva_la_incasare = true, platitor_tva_anaf_inceput = \'2025-01-01\' WHERE id = 1' % s)
    # date-de-pornire: perioada de la 01.10.2026, scrisă înainte de reparație (forma `regim_tva_incasare.salveaza`)
    sql('INSERT INTO "%s".tva_incasare_perioade (de_la, pana_la, sursa) VALUES (\'2026-10-01\', NULL, \'manual\')' % s)


def test_def_626_aplica_de_la_golit_nu_cere_perioada_noua(patron, firma_f2):
    """626. Pașii: firma cu TVA la încasare de la 01.10.2026 -> Date firmă -> „Aplică de la”: 01.11.2026, apoi golit -> la ieșirea din
    câmp revine 01.10.2026 -> golit din nou și „Salvează” direct -> salvat, fără „Scrie data de la care firma aplică…”, fără „NU s-a
    salvat”; perioada rămâne cea de la 01.10.2026 (nicio perioadă nouă). ROȘU înainte: „S-au salvat: datele firmei, vectorul fiscal.
    Restul NU — vezi câmpurile marcate.” + „Aplică de la — Scrie data de la care firma aplică sistemul TVA la încasare.”"""
    pg, s = patron.pg, firma_f2["schema"]
    _tva_incasare_de_la_01_10(s)
    patron.firma(firma_f2["nume"])
    _card(patron, "datefirma", "#df-salveaza")
    assert pg.input_value("#vf-tva_incasare_de_la") == "2026-10-01"
    pg.fill("#vf-tva_incasare_de_la", "2026-11-01")
    pg.fill("#vf-tva_incasare_de_la", "")
    pg.click("#df-telefon")
    assert pg.input_value("#vf-tva_incasare_de_la") == "2026-10-01"
    patron.captura("golit_revine")
    pg.eval_on_selector("#vf-tva_incasare_de_la", "e => { e.value = ''; }")
    pg.evaluate("() => { const m = document.querySelector('#df-msg'); if (m) m.innerHTML = ''; }")
    pg.click("#df-salveaza")
    pg.wait_for_function("() => /salvat/i.test((document.querySelector('#df-msg') || {innerText: ''}).innerText)", timeout=30000)
    pg.wait_for_selector("#df-salveaza:not([disabled])", timeout=30000)
    patron.captura("salvat")
    t = pg.inner_text("#df-msg")
    assert "Scrie data de la care" not in patron.fereastra() and not pg.query_selector(".refuz-salvare"), t
    assert sql('SELECT de_la::text, pana_la FROM "%s".tva_incasare_perioade' % s) == [("2026-10-01", None)]


# ── 627 — „Profil incomplet” după o salvare parțială ────────────────────────────────────────────────────────────────────────────────
def test_def_627_salvarea_partiala_actualizeaza_profil_incomplet(patron, firma_f2):
    """627. Pașii: Date firmă (Nr. registrul comerțului lipsă, în „Profil incomplet”) -> scrii J40/627/2026 -> „Data cesiunii” fără o
    structură nouă a asociaților (refuzată pe ecran: salvare parțială) -> „Salvează” -> „S-au salvat: datele firmei …”, iar „Profil
    incomplet” nu mai numește Nr. registrul comerțului; ce n-a intrat rămâne scris. ROȘU înainte: lista de sus neschimbată."""
    pg, s = patron.pg, firma_f2["schema"]
    # date-de-pornire: Nr. registrul comerțului lipsă (firma nouă de probă îl primește din provizionare), ca să apară în „Profil incomplet”
    sql('UPDATE "%s".firma_profil SET reg_com = NULL WHERE id = 1' % s)
    patron.firma(firma_f2["nume"])
    _card(patron, "datefirma", "#df-salveaza")
    from e2e_lot10_date_firma import _panou_profil   # [lotul 14, 687] „Profil incomplet” e un card: se deschide, se citește lista, se revine
    assert "Nr. registrul comerțului" in _panou_profil(pg)
    pg.fill("#df-reg_com", "J40/627/2026")
    pg.fill("#as-data-cesiune", "2026-10-01")
    pg.click("#df-salveaza")
    pg.wait_for_function("() => (document.querySelector('#df-msg') || {innerText: ''}).innerText.includes('S-au salvat: datele firmei')",
                         timeout=30000)
    pg.wait_for_selector("#df-salveaza:not([disabled])", timeout=30000)
    patron.captura("profil_actualizat")
    bloc = _panou_profil(pg, poate_lipsi=True)
    assert "Nr. registrul comerțului" not in bloc, bloc
    assert pg.input_value("#as-data-cesiune") == "2026-10-01"           # ce n-a intrat rămâne scris
    assert sql('SELECT reg_com FROM "%s".firma_profil' % s) == [("J40/627/2026",)]


# ── 642 — formularul din invitație și contul fără firma lui ─────────────────────────────────────────────────────────────────────────
def _scoate_contul(email):
    """Contul de probă, dacă o mutație l-a creat: generic, pe coloanele `user_id` / `accounting_firm_id` din `public` (ca
    `e2e_invitatii._curata`), ca o rulare cu mutație să nu lase cabinete în baza de test."""
    def tabele(col):
        return [r[0] for r in sql("SELECT c.table_name FROM information_schema.columns c JOIN information_schema.tables t "
                                  "ON t.table_schema = c.table_schema AND t.table_name = c.table_name AND t.table_type = 'BASE TABLE' "
                                  "WHERE c.table_schema = 'public' AND c.column_name = %s AND c.table_name NOT IN ('users', "
                                  "'accounting_firms')", (col,))]
    rr = sql("SELECT id, accounting_firm_id FROM public.users WHERE email = %s", (email,))
    uids, fids = [r[0] for r in rr], [r[1] for r in rr if r[1]]
    sql("DELETE FROM public.acord_termeni WHERE email = %s", (email,))
    if uids:
        for t in tabele("user_id"):
            sql('DELETE FROM public."%s" WHERE user_id = ANY(%%s)' % t, (uids,))
        sql("DELETE FROM public.users WHERE id = ANY(%s)", (uids,))
    if fids:
        for t in tabele("accounting_firm_id"):
            sql('DELETE FROM public."%s" WHERE accounting_firm_id = ANY(%%s)' % t, (fids,))
        sql("DELETE FROM public.accounting_firms WHERE id = ANY(%s)", (fids,))


@pytest.fixture()
def invitatie_642():
    """O invitație NOUĂ (pe drumul aplicației, `invitatii.creeaza`) pentru un email de probă; scoasă la final, cu orice cont creat."""
    from conftest import _db
    from core import invitatii
    email = "e2e.642.%s@exemplu.ro" % secrets.token_hex(3)
    db = _db()
    with db.get_conn() as c, c.cursor() as cur:
        tok = invitatii.creeaza(cur, email, None)
        c.commit()
    yield email, tok
    creat = sql("SELECT count(*) FROM public.users WHERE email = %s", (email,))
    _scoate_contul(email)
    sql("DELETE FROM public.invitatii_cabinet WHERE email = %s", (email,))
    assert creat == [(0,)], "s-a creat un cont la un refuz"


def test_def_642_refuzul_cui_apare_o_data_iar_formularul_incape(browser, request, invitatie_642):
    """642 (formularul). Pașii vizitatorului, la 1280×720: linkul invitației -> „Continuă” -> CUI 12345678 -> „Verifică la ANAF” (CUI-ul
    nu e valid) -> denumirea, parolele, termenii -> „Creează cont” -> refuzul o singură dată, lângă „Creează cont”; formularul întreg în
    ecran, fără derulare; nimic în afara ferestrei; niciun cont. ROȘU înainte: textul de 2 ori (sub CUI și sub termeni), formularul de
    967 px într-o fereastră de 672, „Creează cont” la 716–752 px (sub marginea ecranului)."""
    email, tok = invitatie_642
    ctx = browser.new_context(viewport=LAPTOP)
    e = Ecran(ctx.new_page(), request.node.name)
    try:
        vp = e.pg
        vp.goto(BAZA + "/#invitatie=" + tok, wait_until="domcontentloaded")
        vp.wait_for_selector("#pr-continua", timeout=20000)
        vp.click("#pr-continua")
        vp.wait_for_selector("#reg-buton", timeout=10000)
        vp.fill("#reg-cui", CUI_GRESIT)
        vp.click("#reg-cui-verifica")
        vp.wait_for_function("() => document.querySelector('#reg-cui-info').textContent.includes('nu e valid')", timeout=20000)
        vp.fill("#reg-cabinet", "E2E Cabinet Test Inregistrare 642")
        vp.fill("#reg-parola", "ParolaE2e!642x")
        vp.fill("#reg-parola2", "ParolaE2e!642x")
        vp.check("#reg-termeni")
        vp.click("#reg-buton")
        vp.wait_for_selector("#reg-eroare:not([hidden])", timeout=20000)
        vp.wait_for_timeout(900)    # după plasa „refuz nevăzut” (700 ms)
        e.captura("refuzul_o_data")
        o = vp.evaluate("""() => { const md = document.querySelector('#acces-modal'); const b = document.querySelector('#reg-buton').getBoundingClientRect();
          const z = document.querySelector('#reg-eroare').getBoundingClientRect(); const t = document.body.innerText.replace(/\\s+/g, ' ');
          return {deruleaza: md.scrollHeight > md.clientHeight + 1, buton: b.top >= 0 && b.bottom <= innerHeight, zona: z.top >= 0 && z.bottom <= innerHeight,
                  de_cate_ori: t.split('nu e valid: cifra de control nu corespunde').length - 1, in_afara: document.querySelector('.acces-overlay').children.length,
                  banner: !!document.querySelector('#refuz-nevazut')}; }""")
        assert o["de_cate_ori"] == 1 and not o["banner"] and o["in_afara"] == 1, o      # „mesajul de refuz apare de două ori”
        assert not o["deruleaza"] and o["buton"] and o["zona"], o                       # „iese din ecran”, „«Creează cont» abia se vede”
        assert not e.erori and not e.cereri_rele, (e.erori, e.cereri_rele)
    finally:
        ctx.close()


def test_def_642_confirmarea_cu_cui_gresit_nu_lasa_cont_fara_firma(browser, request):
    """642 (serverul). O cerere de înregistrare liberă scrisă cu CUI-ul 12345678 (ca înainte de verificarea de la formular, 459) -> clic
    pe linkul de confirmare -> „Contul nu s-a creat: firma proprie a cabinetului (CUI 12345678) nu se poate adăuga. CUI-ul 12345678 nu e
    valid …”, iar contul NU există și linkul rămâne nefolosit. ROȘU înainte (23.10, 14:15): contul creat, firma proprie nu, emailul de bun
    venit „Firma proprie a cabinetului este deja adăugată în portofoliu.”"""
    from conftest import _db
    from core import inregistrare_libera as il, nucleu
    email = "e2e.642.liber.%s@exemplu.ro" % secrets.token_hex(3)
    db = _db()
    with db.get_conn() as c, c.cursor() as cur:
        tok = il.creeaza(cur, {"email": email, "nume_cabinet": "E2E Cabinet Test Inregistrare 642 liber", "nume": "Proba", "prenume": None,
                               "cui": CUI_GRESIT}, nucleu.hash_parola("ParolaE2e!642x"), "v-e2e-642", None)
        c.commit()
    ctx = browser.new_context(viewport=LAPTOP)
    e = Ecran(ctx.new_page(), request.node.name)
    try:
        vp = e.pg
        vp.goto(BAZA + "/#confirmare=" + tok, wait_until="domcontentloaded")
        vp.wait_for_selector("#conf-rezultat", timeout=30000)
        e.captura("vechi_cererea_cu_cui_gresit")
        t = " ".join(vp.inner_text("#conf-rezultat").split())
        assert t.startswith("Contul nu s-a creat: firma proprie a cabinetului (CUI 12345678) nu se poate adăuga."), t
        assert "nu e valid" in t and "înregistrează-te din nou" in t, t
        assert sql("SELECT count(*) FROM public.users WHERE email = %s", (email,)) == [(0,)]
        assert sql("SELECT confirmata_la FROM public.inregistrari_in_asteptare WHERE email = %s", (email,)) == [(None,)]
    finally:
        ctx.close()
        _scoate_contul(email)
        sql("DELETE FROM public.inregistrari_in_asteptare WHERE email = %s", (email,))
        sql("DELETE FROM public.cereri_ritm WHERE cheie = 'confirmare_ip'")
