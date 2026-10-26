# -*- coding: utf-8 -*-
"""Lotul 9, închiderea (Costin 19.10.2026, verbatim în DECIZII „Închiderea lotului 9”): 394, partea „Migrare cabinet” — deciziile
„Instrucțiunile pliate” (pașii rămân în aceeași ordine; instrucțiunile devin „Cum se face”, pliate) și „Rânduri mai compacte” (fiecare pas
pe un rând mai scund, aceeași ordine, o coloană; cei 12 pași încap). Pașii contabilului pe aplicația din index, pe baza de TEST."""
import pytest

from conftest import INALT, LAT
from e2e_lot5_migrare import PASI, TEXT_B, _migrare

_MASOARA = """() => { const f = [...document.querySelectorAll('.fereastra')].pop(), c = f.querySelector('.fereastra-corp');
  const d = c.querySelector('#mig-apl-cum'), s = d && d.querySelector('summary'), rc = c.getBoundingClientRect();
  const pasi = [...c.querySelectorAll('#mig-meniu .mig-op')];
  return {exista: !!d, deschis: !!(d && d.open), h_cum: d ? d.getBoundingClientRect().height : null,
          h_summary: s ? s.getBoundingClientRect().height : null, titlu: s ? s.textContent.trim() : null,
          sh: c.scrollHeight, ch: c.clientHeight, h_pas_min: Math.min(...pasi.map((x) => x.getBoundingClientRect().height)),
          pasi_la_vedere: pasi.filter((x) => x.getBoundingClientRect().bottom <= rc.bottom).length}; }"""


@pytest.fixture()
def ecran(patron, request):
    """Mărimea ecranului din parametru, refăcută la mărimea plasei la final."""
    lat, inalt = request.param
    patron.pg.set_viewport_size({"width": lat, "height": inalt})
    try:
        yield patron
    finally:
        patron.pg.set_viewport_size({"width": LAT, "height": INALT})


@pytest.mark.parametrize("ecran", [(1366, 768), (1700, 1000)], indirect=True, ids=["laptop_1366x768", "desktop_1700x1000"])
def test_def_394_migrare_cabinet_incape_cu_cum_se_face_pliat(ecran):
    """394 (Migrare cabinet). Fereastra avea 1.342 px de conținut în 661 px (1366×768) și în 893 px (1700×1000). Pașii: Firme -> Migrare
    cabinet -> pașii 1–12 în ordinea de până acum, fiecare pe un rând scund; „Cum se face” e pliat (textul nu se vede, ocupă numai rândul
    titlului); fereastra NU derulează (`scrollHeight <= clientHeight`) -> clic pe „Cum se face” -> textul (b) apare, cuvânt cu cuvânt.
    MUTAȚIA 1: în static/js/ecrane/migrare.js `<details class="dec-xml" id="mig-apl-cum">` ->
    `<details class="dec-xml" id="mig-apl-cum" open>` -> ROȘU („Cum se face” deschis la randare; și fereastra derulează).
    MUTAȚIA 2: în static/stil.css `  .mig-op { padding: 1px 12px; gap: 10px; }` (lotul 11: 3 -> 1 px) -> `  .mig-op { padding: 13px 15px; gap: 10px; }` -> ROȘU
    pe 1366×768 (rândurile înalte: fereastra derulează)."""
    pg = ecran.pg
    _migrare(ecran)
    assert pg.eval_on_selector_all("#mig-meniu .mig-op .mig-op-titlu", "els => els.map(e => e.textContent.trim())") == PASI
    assert pg.eval_on_selector_all("#mig-meniu .mig-op .mig-op-nr", "els => els.map(e => e.textContent.trim())") == \
        [str(i) for i in range(1, len(PASI) + 1)]
    m = pg.evaluate(_MASOARA)
    print("394 Migrare cabinet %s:" % pg.viewport_size, m)
    ecran.captura("pliat")
    assert m["exista"] and m["titlu"] == "Cum se face", m
    assert not m["deschis"], m                                        # pliat la randare
    assert m["h_cum"] <= m["h_summary"] + 1, m                         # închis: numai rândul titlului
    assert not pg.is_visible("#mig-apl-text"), "textul instrucțiunilor se vede cu „Cum se face” pliat"
    assert m["sh"] <= m["ch"] + 1 and m["pasi_la_vedere"] == len(PASI), m   # cei 12 pași încap, fără derulare
    # descrierea tăiată cu „…” pe rândul scund rămâne întreagă în `title`
    sub = pg.eval_on_selector_all("#mig-meniu .mig-op .mig-op-sub", "els => els.map(e => [e.textContent, e.title])")
    assert all(t and t == ti for t, ti in sub), sub
    pg.click("#mig-apl-cum > summary")
    pg.wait_for_selector("#mig-apl-text", state="visible", timeout=5000)
    assert pg.evaluate("() => document.querySelector('#mig-apl-cum').open")
    text = pg.eval_on_selector_all("#mig-apl-text p, #mig-apl-text li", "els => els.map(e => e.innerText.trim())")
    ecran.captura("deschis")
    assert text == TEXT_B, text


@pytest.mark.parametrize("ecran", [(393, 851)], indirect=True, ids=["telefon_393x851"])
def test_def_394_pe_telefon_pasii_raman_tinte_de_atingere_mari(ecran):
    """394. Rândurile scunde sunt numai pe ecranul lat (stil.css `@media (min-width: 761px)`): pe telefon (Pixel 5, 393 px) fiecare pas
    rămâne de cel puțin 44 px înălțime (ținta de atingere, DS cap.4 / WCAG 2.5.5), cu descrierea sub titlu.
    MUTAȚIA: în static/stil.css `@media (min-width: 761px) {\\n  .mig-meniu { gap: 1px; }` -> `@media (min-width: 1px) {\\n  .mig-meniu { gap: 1px; }`
    -> ROȘU (rândul de ~35 px și pe telefon)."""
    pg = ecran.pg
    _migrare(ecran)
    m = pg.evaluate(_MASOARA)
    ecran.captura()
    assert m["h_pas_min"] >= 44, m


# ── 368 — notele unei PFA: validate automat, ca note interne ─────────────────────────────────────────────────────────────────────
@pytest.fixture()
def pfa_tva():
    """O PFA NOUĂ (partidă simplă), plătitoare de TVA lunar."""
    from conftest import firma_noua
    for f in firma_noua("pfa"):
        yield f


def test_def_368_nota_pfa_e_interna_nu_de_validat_si_z_intra_in_d300(patron, pfa_tva):
    """368 (decizia Costin 19.10.2026 „Se validează automat”). La PFA notele scrise în fundal apăreau „de validat”, iar Z-ul rămânea
    ciornă și lipsea din D300. Pașii: PFA plătitoare de TVA -> Casă -> „+ Dispoziție nouă” -> ridicare de la bancă 150 lei, document
    „DI368” -> Adaugă -> mesajul spune „notă internă” și „Poartă TVA-ul pentru D300 / D394; evidența PFA e registrul de încasări și
    plăți.”; nota e validată, nu e nici în coadă, nici între „Notele tale în ciornă”. (Z-ul și D300: `test_def_c65_*`.)
    MUTAȚIA: în core/uc_coada.py `            if not coada_api.partida_simpla(cur):\\n                return gol` ->
    `            if True:\\n                return gol` -> ROȘU (mesajul spune „ciornă”, nota rămâne ciornă)."""
    from conftest import sql
    from e2e_bloc_a import _api, _card, _ok, pregateste_firma
    f = pfa_tva
    pregateste_firma(patron, f, forma=False, regim_fiscal=None)   # PFA: fără regim micro / profit (serverul îl refuză)
    pg = patron.pg
    patron.firma(f["nume"])
    _card(patron, "casa", "#c-toggle")
    pg.click("#c-toggle")
    pg.select_option("#c-cat", "ridicare_banca")
    pg.fill("#c-suma", "150")
    pg.fill("#c-doc", "DI368")
    pg.wait_for_timeout(600)
    pg.click("#c-adauga")
    # confirmarea stă în paragraful de sus al Casei (`mesajSucces`, redesenat după salvare), nu în `#c-mesaj` (refuzurile)
    pg.wait_for_function("() => [...document.querySelectorAll('p.pf-intro')].some((p) => p.textContent.includes('Dispoziția a fost salvată'))",
                         timeout=20000)
    t = " ".join(pg.locator("p.pf-intro", has_text="Dispoziția a fost salvată").first.inner_text().split())
    patron.captura("casa")
    assert "e notă internă." in t and "Poartă TVA-ul pentru D300 / D394; evidența PFA e registrul de încasări și plăți." in t, t
    s = f["schema"]
    (nid, st), = sql('SELECT i.id, i.status FROM "%s".inregistrari i JOIN "%s".casa_operatiuni c ON c.inregistrare_id = i.id '
                     'WHERE c.document = %%s' % (s, s), ("DI368",))
    assert st == "validata", st
    assert sql("SELECT count(*) FROM public.declaratii_coada WHERE tenant_id = %s AND fel = 'nota' AND perioada = %s",
               (f["tenant_id"], "nota-%d" % nid)) == [(0,)]
    ciorne = _ok(_api(patron, "GET", "/eu/ciorne"), "ciornele mele")
    assert all(n["id"] != nid for x in ciorne["firme"] if x["tenant_id"] == f["tenant_id"] for n in x["note"]), ciorne


def test_def_c65_z_la_pfa_validat_intern_intra_in_d300(patron, pfa_tva):
    """C65 (găsită de Code la 368, 19.10.2026). La PFA nota raportului Z (TVA-ul pe cote) rămânea ciornă, iar D300 / D394 o citesc numai
    validată — TVA-ul Z-ului lipsea din D300 rd.9. Pașii: PFA plătitoare de TVA, stoc cantitativ-valoric -> Raport Z de 121 lei la 21%
    (numerar) pe luna trecută -> refuzul validării interne se spune („descărcarea mărfii vândute”) -> „Fără marfă din stoc” -> nota se
    validează ca notă internă -> D300 luna trecută, „Rânduri completate”: rândul 9 are TVA-ul Z-ului (21 lei).
    MUTAȚIA: `z_descarcare.deblocat` fără efect -> Z-ul rămâne ciornă după „Fără marfă din stoc” -> ROȘU."""
    import datetime as _dt
    from conftest import sql
    from e2e_bloc_a import _card, pregateste_firma
    from e2e_bloc_e import _declaratie, _deschide_componente, _sectiune
    f = pfa_tva
    pregateste_firma(patron, f, forma=False, regim_fiscal=None)   # PFA: fără regim micro / profit (serverul îl refuză)
    pg = patron.pg
    patron.firma(f["nume"])
    s = f["schema"]
    # Raportul Z pe luna trecută: nota lui (TVA-ul pe cote) e internă, validată -> D300 rd.9
    zi = (_dt.date.today().replace(day=1) - _dt.timedelta(days=1))
    _card(patron, "raportz", "#z-salveaza")
    pg.fill("#z-data", zi.isoformat())
    pg.fill("#z-nui", "8000000368")
    pg.fill("#z-nr", "0368")
    pg.fill("#z-21", "121")
    pg.fill("#z-num", "121")
    pg.fill("#z-card", "0")
    pg.fill("#z-bonuri", "2")
    pg.click("#z-salveaza")
    pg.wait_for_selector("#z-rip, #z-rezultat .msg-eroare, #z-rezultat .caseta-eroare", timeout=30000)
    _q = 'SELECT status FROM "%s".inregistrari WHERE sursa = \'horeca_z\' AND numar = %%s' % s
    # firma ține stocul cantitativ-valoric: Z-ul nu se validează nedescărcat — refuzul validării interne se SPUNE, cu motivul
    pg.wait_for_selector("#z-interna-refuz", timeout=20000)
    refuz = " ".join(pg.inner_text("#z-interna-refuz").split())
    patron.captura("z-refuz")
    assert "nu s-a validat ca notă internă" in refuz and "descărcarea mărfii vândute" in refuz, refuz
    assert sql(_q, ("Z-8000000368-0368",)) == [("ciorna",)]
    # „Fără marfă din stoc” rezolvă cauza: nota Z-ului se reîncearcă și se validează ca notă internă
    pg.wait_for_selector(".zd-fara", timeout=20000)
    # omul nu apasă în aceeași secundă: peste marja ceasului (`uc_coada._MARJA_CEAS_SECUNDE`), nota Z-ului nu mai e „a cererii” —
    # o validează numai reîncercarea (`autor_cerere.reincearca_interna`), deci asta probează testul
    pg.wait_for_timeout(2500)
    pg.click(".zd-fara")
    pg.click("#ca-ok")
    pg.wait_for_function("(t) => ((document.querySelector('#z-descarcare') || {}).textContent || '').includes(t)",
                         arg="Poartă TVA-ul pentru D300 / D394", timeout=20000)
    patron.captura("z-interna")
    assert sql(_q, ("Z-8000000368-0368",)) == [("validata",)]
    _declaratie(patron, f, "d300", zi.year, zi.month)
    _deschide_componente(patron)
    sec = _sectiune(patron, "Rânduri completate")
    patron.captura("d300")
    r9 = [" ".join(" ".join(r).split()) for r in sec[1] if r and r[0].startswith("rândul 9")]
    assert r9 and any("21" in r for r in r9), sec   # CF art.291: 121 lei cu TVA la 21% -> TVA 21,00, baza 100,00; D300 rd.9


def test_def_c66_d212_nu_cere_validarea_notelor(patron, pfa_tva):
    """C66 (găsită de Code la 368, 19.10.2026). La „Trimite în coadă” pe D212, avertismentul „În perioadă sunt N note nevalidate … validează-le
    înainte de depunere” apărea, deși D212 nu citește notele (se face din registrul de încasări și plăți, `d212.pull`). Pașii: PFA cu o
    notă ciornă în 2025 -> Declarații -> D212 pe 2025 -> identitatea (CNP, nume, adresă) -> Regenerează -> Trimite în coadă: mesajul nu
    numește nota și nu cere validarea ei.
    MUTAȚIA: în core/coada_api.py `    note = [] if tip in DECLARATII_FARA_NOTE else note_nevalidate(cur, schema, de_la, pana_la)` ->
    `    note = note_nevalidate(cur, schema, de_la, pana_la)` -> ROȘU (mesajul numește nota ciornă)."""
    from conftest import alege_perioada, alege_tipul, sql
    from e2e_bloc_a import _card, pregateste_firma
    f = pfa_tva
    pregateste_firma(patron, f, forma=False, regim_fiscal=None)   # PFA: fără regim micro / profit (serverul îl refuză)
    s = f["schema"]
    # o notă ciornă în anul declarației: la PFA notele din aplicație se validează automat (368), deci ciorna se scrie direct
    nid = sql('INSERT INTO "%s".inregistrari (data, descriere, sursa, status, document_ref) VALUES (\'2025-12-15\', \'Notă C66\', '
              '\'manual\', \'ciorna\', \'DI C66\') RETURNING id' % s)[0][0]
    sql('INSERT INTO "%s".inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%%s, \'5311\', \'5121\', 66)' % s,
        (nid,))
    try:
        pg = patron.pg
        patron.firma(f["nume"])
        _card(patron, "declaratii", "#dec-tip")
        alege_tipul(pg, "d212")
        alege_perioada(pg, 2025)
        pg.wait_for_selector("#dec-continua:not([disabled])", timeout=8000)
        pg.click("#dec-continua")
        pg.wait_for_selector("#d212-cnp", timeout=30000)
        for sel, v in (("#d212-cnp", "1800101221144"), ("#d212-nume", "POPESCU ION"), ("#d212-adr", "Bucuresti Sector 1")):   # CNP: cifra de control verificată
            pg.fill(sel, v)
            pg.dispatch_event(sel, "change")
        # alegerile fără implicit (FAPT_FISCAL_NECERUT): fără venit din registru, fără excepție de la baza minimă CASS
        pg.select_option("#d212-rip", "false")
        pg.dispatch_event("#d212-rip", "change")
        pg.select_option("#d212-exccass", label="nicio excepție — CASS cel puțin la baza de 6 salarii minime")
        pg.dispatch_event("#d212-exccass", "change")
        pg.click("#d212-regen")
        pg.wait_for_selector("#dec-trimite", timeout=90000)
        pg.click("#dec-trimite")
        pg.wait_for_selector(".dec-gata, .caseta-atentie #coada-confirmare", timeout=60000)
        if pg.locator("#coada-confirmare").count():
            pg.fill("#coada-confirmare", "Probă E2E: D212 fără venituri în anul de probă.")
            pg.click("#coada-confirma")
            pg.wait_for_selector(".dec-gata", timeout=60000)
        txt = patron.fereastra()
        patron.captura()
        assert "Trimisă în coadă" in txt, txt[:800]
        assert "nevalidat" not in txt and "validează-le" not in txt and "Notă C66" not in txt, txt[:1500]
    finally:
        sql("DELETE FROM public.declaratii_coada WHERE tenant_id = %s AND fel <> 'nota' AND tip = 'd212'", (f["tenant_id"],))


# ── C67 — „Salariat nou” păstrează data nașterii, copiii, declarația și data încetării ────────────────────────────────────────────
@pytest.fixture()
def srl_nou(patron):
    from conftest import firma_noua
    from e2e_bloc_a import pregateste_firma
    for f in firma_noua():
        pregateste_firma(patron, f)
        yield f


def test_def_c67_salariat_nou_pastreaza_datele_deducerilor(patron, srl_nou):
    """C67 (găsită de Code la 412, 19.10.2026). „Salariat nou” trimitea data nașterii, copiii școlarizați, declarația copiilor și data
    încetării, dar modelul rutei (`main.SalariatIn`) nu le avea: se pierdeau tăcut la creare (deducerile CF art.77). Pașii: Salariați ->
    „+ Salariat nou” -> completat, cu data nașterii 01.01.1990, 2 copii școlarizați, declarația „Da”, data încetării 31.12.2026 ->
    Salvează: formularul se golește (salvat), iar în fișa salariatului din bază cele patru valori sunt cele scrise (niciun ecran nu le
    afișează: intră în calculul deducerilor, `salarizare`).
    MUTAȚIA: în main.py `    data_nastere: Optional[str] = None\\n` scos din `SalariatIn` -> ROȘU (data nașterii lipsește din fișă)."""
    from conftest import sql
    from e2e_bloc_a import _card
    f = srl_nou
    pg = patron.pg
    patron.firma(f["nume"])
    _card(patron, "salariati", "#sp-salariat-nou")
    pg.click("#sp-salariat-nou")
    pg.wait_for_selector("#sn-salveaza", timeout=20000)
    for sel, v in (("#sn-nume", "POPESCU"), ("#sn-prenume", "MARIA"), ("#sn-cnp", "1900101410011"),   # CNP: cifra de control verificată
                   ("#sn-data_angajare", "2024-01-01"), ("#sn-data_incetare", "2026-12-31"), ("#sn-salariu_brut", "4050"),
                   ("#sn-data_nastere", "1990-01-01"), ("#sn-copii_scolarizati", "2"), ("#sn-judet_casa", "B")):
        pg.fill(sel, v)
    for sel, v in (("#sn-tip_norma", "intreaga"), ("#sn-declaratie_copii", "true"), ("#sn-functie_baza", "true"),
                   ("#sn-scutit_contrib_minim", "false"), ("#sn-tip_contract", "nedeterminata")):
        pg.click(".alegere-butoane:has(+ %s) button[data-valoare='%s']" % (sel, v))   # [lotul 13, 676] listele scurte = butoane alăturate
    pg.fill("#sn-cor-cauta", "241107")
    pg.wait_for_selector("#sn-cor-rez [data-cod='241107']", timeout=20000)
    pg.click("#sn-cor-rez [data-cod='241107']")
    pg.click("#sn-salveaza")
    pg.wait_for_function("() => !(document.querySelector('#sn-nume') || {}).value", timeout=30000)
    patron.captura()
    r = sql('SELECT data_nastere::text, copii_scolarizati, declaratie_copii, data_incetare::text FROM "%s".salariati WHERE cnp = %%s'
            % f["schema"], ("1900101410011",))
    assert r == [("1990-01-01", 2, True, "2026-12-31")], r
