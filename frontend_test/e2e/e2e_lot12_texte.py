# -*- coding: utf-8 -*-
"""Lotul 12, comanda 12.1 (verbatim în DECIZII „Comanda 12.1”), pachetul TEXTE — 163, 172, 184, 45 și C132: textul de pe ecran e în limba
contabilului (CLAUDE.md §9: „Textele dau instrucțiuni directe, în limba contabilului, cu diacritice; fără termeni de programator.”).

  * C132 — axa D101 a supervizorului: „Nu ma pronunt inca: D101 declara…” (fără diacritice, la persoana întâi, „CIORNA” cu majuscule)
    devine „Verificarea așteaptă: D101 declară …, există note în ciornă …”;
  * 172 — aceeași axă, fără D101 depus: „-> comparația devine posibilă … GRI, nu roșu” și „nu am ce confrunta” nu mai apar;
  * 163 — un text compus din bucăți (mesajul cheii API: „copiaz-o ACUM, nu se mai afiseaza”) era scăpat de gărzile de sursă;
  * 184 — perioada în forma „LL/AAAA” și în refuzurile serverului („Pontajul lunii 10.2026 …” -> „10/2026”);
  * 45 — mesajul de după buton, scris direct într-o zonă fără clasă de mesaj (cheia API), vine în vedere.

DATE DE PORNIRE fără ecran (declarate, regula lui 429): D101 depus (rândul 48 = 1.000 lei) și D112 depus — `public.declaratii_depuse`, pe
firma sintetică a fișierului (`firma_e2e` / `firma_sal`), scoase la final; D101 pe anul 2099 (perioadă sintetică, CLAUDE.md §10); nota în
ciornă pe 691 în 2099 intră pe ruta Registrului jurnal (`POST jurnal`, fără „Validează”); rezultatul supervizorului e calculat cum îl
calculează lucrătorul de la 5 minute (`supervizor_cache.recalculeaza_firma`). Restul, pe ecran."""
import pytest

from conftest import linie_nota, sql
from e2e_bloc_a import _api
from e2e_bloc_d import PATRON, _api as _api_cont, _stat, firma_sal  # noqa: F401 — firma_sal: fixtura

_F = ".fereastra:last-of-type "
AN_SINTETIC = 2099


def _supervizor(patron, firma):
    """Rezultatul supervizorului pentru firmă (lucrătorul), apoi Supervizor din cabinet -> blocul firmei: textul rândurilor D101."""
    from core import supervizor_cache as sc
    from core.common import azi_ro
    from core.control_fiscal_api import luna_confruntata
    azi = azi_ro()
    an, luna = luna_confruntata(azi.year, azi.month)
    sc.recalculeaza_firma(firma["tenant_id"], firma["schema"], an, luna)
    patron.acasa()
    patron.pg.click("button.cab-card:has([data-cheie='supervizor'])")
    patron.pg.wait_for_selector(_F + ".sv-antet", timeout=60000)
    bloc = patron.pg.locator(_F + ".sv-firma", has_text=firma["nume"])
    bloc.first.wait_for(timeout=30000)
    return [r for r in bloc.first.locator(".cf-incr-rand").all_inner_texts() if "D101" in r]


def _defecte(text):
    from core import limba_ecran
    return limba_ecran.defecte(text)


# ── 172 — axa D101 fără nicio depunere: fără săgeți, „GRI”, persoana întâi ──────────────────────────────────────────────────────────
def test_def_172_supervizorul_fara_d101_depus_vorbeste_limba_contabilului(patron, firma_e2e):
    """172. Pașii: firma fără niciun D101 depus prin aplicație -> Supervizor (din cabinet) -> blocul firmei: cele două rânduri D101 („D101
    vs D100”, „D101 vs contabilitate”) spun „Niciun D101 depus prin aplicație — nu se poate confrunta nimic.” și temeiul „Confruntarea
    declarației cu o sursă independentă, pe an. … Absența unei depuneri nu e o divergență, deci nu e semnalată cu roșu.” Judecate cu
    regulile ecranului (`core/limba_ecran.py`): nicio săgeată „->”, niciun „GRI”, nimic la persoana întâi, nicio formă fără diacritice.
    Înainte: „… pe niciun an -> comparația devine posibilă după prima depunere. GRI, nu roșu: …”."""
    randuri = _supervizor(patron, firma_e2e)
    patron.captura("supervizor_fara_d101")
    assert len(randuri) == 2, randuri
    for r in randuri:
        assert "Niciun D101 depus prin aplicație — nu se poate confrunta nimic." in r, r
        assert "deci nu e semnalată cu roșu" in r and "->" not in r and "GRI" not in r, r
        assert not _defecte(r), (_defecte(r), r)


# ── C132 — axa D101 cu note în ciornă pe 691: „Verificarea așteaptă”, cu diacritice ─────────────────────────────────────────────────
@pytest.fixture()
def d101_cu_ciorna_691(firma_e2e):
    """D101 depus pe 2099 (rd.48 = 1.000 lei) + o notă în ciornă pe 691 în 2099 — ramura „verificarea așteaptă” a perechii D101 / 691."""
    import json
    s, tid = firma_e2e["schema"], firma_e2e["tenant_id"]
    # date-de-pornire: D101 depus la ANAF pe anul sintetic 2099 — depunerea trece prin SPV, nu se poate produce în plasă
    sql("INSERT INTO public.declaratii_depuse (tenant_id, an, luna, tip, sursa, randuri) VALUES (%s, %s, 12, 'd101', 'iconta', %s)",
        (tid, AN_SINTETIC, json.dumps({"P": {"P48": 1000, "P50": 0}, "d_grup": 0})))
    st, r = _api_cont(PATRON, "POST", "/tenants/%d/jurnal" % tid,   # nota în ciornă, pe ruta Registrului jurnal (fără „Validează”)
                      {"data": "%d-12-31" % AN_SINTETIC, "descriere": "Probă C132: impozitul pe profit, în ciornă",
                       "document_ref": "Probă C132", "linii": [linie_nota("691", "4411", "1000.00")]})
    assert st == 200 and r.get("id"), (st, r)
    nid = r["id"]
    try:
        yield firma_e2e
    finally:
        sql('DELETE FROM "%s".inregistrari_linii WHERE inregistrare_id = %%s' % s, (nid,))
        sql('DELETE FROM "%s".inregistrari WHERE id = %%s' % s, (nid,))
        sql("DELETE FROM public.declaratii_depuse WHERE tenant_id = %s AND tip = 'd101' AND an = %s", (tid, AN_SINTETIC))


def test_def_c132_supervizorul_spune_axa_d101_in_limba_contabilului(patron, d101_cu_ciorna_691):
    """C132. Pașii: firma cu D101 depus (rândul 48 = 1.000 lei) și o notă în ciornă pe 691 în același an -> Supervizor -> blocul firmei:
    rândul „D101 rd.48 vs cont 691” spune „Verificarea așteaptă: D101 declară 1.000,00 lei, contul 691 are 0,00 lei validat, dar există
    note în ciornă pe 691 în 2099. Diferența se poate închide la validarea lor, deci nu e o eroare constatată.”, iar temeiul se încheie
    cu „Există note nevalidate pe contul 691 în anul evaluat.” Înainte: „Nu ma pronunt inca: D101 declara …, dar exista note in CIORNA
    pe 691 pe 2099. Diferenta se poate inchide …” (fără diacritice, persoana întâi, majuscule)."""
    randuri = [r for r in _supervizor(patron, d101_cu_ciorna_691) if "691" in r]
    patron.captura("supervizor_d101_691")
    assert len(randuri) == 1, randuri
    r = randuri[0]
    assert ("Verificarea așteaptă: D101 declară 1.000,00 lei, contul 691 are 0,00 lei validat, dar există note în ciornă pe 691 în "
            "%d. Diferența se poate închide la validarea lor, deci nu e o eroare constatată." % AN_SINTETIC) in r, r
    assert "Există note nevalidate pe contul 691 în anul evaluat." in r, r
    assert not _defecte(r), (_defecte(r), r)


# ── 163 / 45 — mesajul cheii API: fără majuscule, cu diacritice, adus în vedere ─────────────────────────────────────────────────────
def _chei_api(patron, inaltime=None):
    pg = patron.pg
    if inaltime:
        pg.set_viewport_size({"width": 1280, "height": inaltime})
    patron.acasa()
    pg.click("button.cab-card:has([data-cheie='setari'])")
    pg.locator(_F + ".set-meniu button", has_text="Chei API").click()
    pg.wait_for_selector(_F + "#set-cheie-noua", timeout=25000)
    pg.wait_for_selector(_F + "#set-chei-lista:not(:has(.ecran-nota))", timeout=25000)


def _revoca_cheile_probei(patron, nume):
    r = _api(patron, "GET", "/cabinet/api-chei")
    for c in (r["json"] or {}).get("chei") or []:
        if c.get("nume") == nume and c.get("activ"):
            _api(patron, "DELETE", "/cabinet/api-chei/%s" % c["id"])


def test_def_163_mesajul_cheii_api_fara_majuscule_si_cu_diacritice(patron):
    """163. Pașii: Setări -> „Chei API” -> numele cheii -> „Generează cheie nouă”: mesajul spune „Cheia ta (copiaz-o acum: nu se mai
    afișează):”, iar rândul cheii din listă oferă „Revocă”. Judecat cu regulile ecranului: niciun cuvânt scris cu majuscule ca accent,
    nicio formă fără diacritice. Înainte: „Cheia ta (copiaz-o ACUM, nu se mai afiseaza):” și „Revoca” (text compus din bucăți, scăpat de
    gărzile de sursă)."""
    nume = "Probă 163 texte"
    pg = patron.pg
    _chei_api(patron)
    try:
        pg.fill(_F + "#set-cheie-nume", nume)
        pg.click(_F + "#set-cheie-noua")
        pg.wait_for_function("() => (document.querySelector('.fereastra:last-of-type #set-msg-chei') || {}).innerText", timeout=25000)
        msg = pg.inner_text(_F + "#set-msg-chei")
        pg.wait_for_selector(_F + ".set-cheie-revoca", timeout=25000)
        patron.captura("cheie_api")
        assert msg.startswith("Cheia ta (copiaz-o acum: nu se mai afișează):"), msg
        assert not _defecte(msg.split("\n")[0]), (_defecte(msg), msg)
        assert pg.locator(_F + ".set-cheie-revoca").first.inner_text().strip() == "Revocă"
    finally:
        _revoca_cheile_probei(patron, nume)


def _la_marginea_de_jos(pg, sel):
    """Derulează fereastra din față așa încât butonul `sel` să stea la marginea de jos a zonei vizibile (mesajul de sub el cade dedesubt)."""
    pg.evaluate("(s) => { const b = document.querySelector('.fereastra:last-of-type ' + s); "
                "const c = b.closest('.fereastra-corp') || document.scrollingElement; "
                "const r = b.getBoundingClientRect(), jos = Math.min(window.innerHeight, c.getBoundingClientRect ? c.getBoundingClientRect().bottom : window.innerHeight); "
                "c.scrollTop += r.bottom - jos + 2; }", sel)


def _in_vedere(pg, sel):
    return pg.evaluate("(s) => { const m = document.querySelector('.fereastra:last-of-type ' + s); const r = m.getBoundingClientRect(); "
                       "const c = m.closest('.fereastra-corp'); const jos = Math.min(window.innerHeight, c ? c.getBoundingClientRect().bottom : window.innerHeight); "
                       "return {sus: r.top, jos: r.bottom, limita: jos, ok: r.top >= 0 && r.bottom <= jos + 1}; }", sel)


def test_def_45_mesajul_cheii_api_vine_in_vedere(patron):
    """45. Pașii: fereastră de 520 px înălțime -> Setări -> „Chei API” -> butonul „Generează cheie nouă” adus la marginea de jos a
    ecranului -> apăsat: mesajul cu cheia (scris sub buton) intră întreg în zona vizibilă. Înainte: zona mesajului n-avea clasă de mesaj și
    era scrisă direct, deci mecanismul unic din `api.js` (`aduInVedere`) n-o vedea — mesajul rămânea sub marginea ecranului."""
    nume = "Probă 45 texte"
    pg = patron.pg
    _chei_api(patron, inaltime=520)
    try:
        pg.fill(_F + "#set-cheie-nume", nume)
        pg.evaluate("() => { const b = document.querySelector('.fereastra:last-of-type #set-cheie-noua'); "
                    "const c = b.closest('.fereastra-corp') || document.scrollingElement; "
                    "const r = b.getBoundingClientRect(), jos = Math.min(window.innerHeight, c.getBoundingClientRect ? c.getBoundingClientRect().bottom : window.innerHeight); "
                    "c.scrollTop += r.bottom - jos + 2; }")
        pg.click(_F + "#set-cheie-noua")
        pg.wait_for_function("() => (document.querySelector('.fereastra:last-of-type #set-msg-chei') || {}).innerText", timeout=25000)
        _MASOARA_CHEIE = ("() => { const m = document.querySelector('.fereastra:last-of-type #set-msg-chei'); const r = m.getBoundingClientRect(); "
                          "const c = m.closest('.fereastra-corp'); const jos = Math.min(window.innerHeight, c ? c.getBoundingClientRect().bottom : window.innerHeight); "
                          "return {sus: r.top, jos: r.bottom, limita: jos}; }")
        # derularea lină a lui `aduInVedere` (durata ei variază cu încărcarea): se așteaptă condiția însăși, nu un timp fix
        for _ in range(50):
            vede = pg.evaluate(_MASOARA_CHEIE)
            if vede["sus"] >= 0 and vede["jos"] <= vede["limita"] + 1:
                break
            pg.wait_for_timeout(100)
        patron.captura("mesaj_in_vedere")
        assert vede["sus"] >= 0 and vede["jos"] <= vede["limita"] + 1, vede
    finally:
        _revoca_cheile_probei(patron, nume)


# ── 184 — perioada într-o singură formă, și în refuzul serverului ───────────────────────────────────────────────────────────────────
def test_def_184_refuzul_pontajului_scrie_luna_ca_LL_AAAA(patron, firma_sal):
    """184. Pașii: firma cu un salariat -> Salariați -> „Pontaj” pe rândul lui -> (D112 depus pe luna afișată — date de pornire) -> o zi
    trecută pe „absent motivat”: refuzul spune „Pontajul lunii LL/AAAA nu se poate modifica: D112 e deja depusă la ANAF. Corectează prin
    rectificativă (nu prin editare liberă).”, cu luna în aceeași formă ca antetul ecranului („luna LL/AAAA”). Judecat cu regulile
    ecranului: nicio perioadă în altă formă („10.2026”), nicio dată ISO. Înainte: „Pontajul lunii 10.2026 …”."""
    import re
    pg = patron.pg
    tid = firma_sal["tenant_id"]
    _stat(patron, firma_sal)
    pg.click(_F + "[data-pontaj] >> nth=0")
    pg.wait_for_selector(_F + ".pj-sel", timeout=30000)
    antet = pg.inner_text(_F + ".pf-intro >> nth=0")
    m = re.search(r"luna (\d{2})/(\d{4})", antet)
    assert m, antet
    luna, an = int(m.group(1)), int(m.group(2))
    # date-de-pornire: D112 depus la ANAF pe luna stării de plată — depunerea trece prin SPV, nu se poate produce în plasă
    sql("INSERT INTO public.declaratii_depuse (tenant_id, an, luna, tip, sursa, randuri) VALUES (%s, %s, %s, 'd112', 'iconta', NULL)",
        (tid, an, luna))
    try:
        pg.select_option(_F + ".pj-sel >> nth=0", "absent_motivat")
        pg.wait_for_function("() => (document.querySelector('.fereastra:last-of-type #pj-msg') || {}).innerText", timeout=25000)
        msg = pg.inner_text(_F + "#pj-msg").strip()
        patron.captura("pontaj_refuz")
        assert msg == ("Pontajul lunii %02d/%d nu se poate modifica: D112 e deja depusă la ANAF. Corectează prin rectificativă "
                       "(nu prin editare liberă)." % (luna, an)), msg
        assert not [d for d in _defecte(msg) if d[0] in ("perioada", "data")], _defecte(msg)
    finally:
        sql("DELETE FROM public.declaratii_depuse WHERE tenant_id = %s AND tip = 'd112' AND an = %s AND luna = %s", (tid, an, luna))


@pytest.fixture()
def factura_e2e(patron, firma_e2e):
    """O factură emisă pe firma fișierului, pe ruta formularului (date de pornire: `e2e_bloc_a.emite_api`)."""
    from e2e_bloc_a import emite_api, pregateste_firma
    pregateste_firma(patron, firma_e2e)
    r = emite_api(patron, firma_e2e)
    return dict(firma_e2e, factura_id=r.get("id") or r.get("factura_id"))


def test_def_45_refuzul_emailului_facturii_vine_in_vedere(patron, factura_e2e):
    """45, a doua zonă: zona de rezultat scrisă direct (`rez.textContent = …; rez.className = "em-rezultat em-rau"`), fără `arataMesaj`.
    Pașii: fereastra browserului de 1280 × 520 -> Facturi -> „Istoric facturi” -> factura -> „Trimite pe email” -> adresa ștearsă ->
    „Trimite”: „Introdu o adresă validă.” e în zona vizibilă, lângă „Trimite”, în bara lipită jos a ferestrei.
    [lotul 12, C164 — comanda Costin 12.3 pct.4, verbatim: „pe ecranele scunde, antetul detaliului facturii se strânge pe un rând (număr,
    client, total, stare SPV); acțiunea principală rămâne fixă jos (clasa 285).”] Până la C164 (aici un `xfail(strict=True)`), zona
    e-mailului stătea în antetul lipit sus, care pe un ecran mai scund decât el nu se derula: un refuz scris mai jos de marginea ecranului
    nu mai putea intra în vedere. Acum, pe ecranul scund (DS cap.9 v2.103), butoanele detaliului și zonele lor de rezultat stau în bara
    lipită jos — zona refuzului e mereu în vedere, oricât s-ar derula tabelul. Mutația (`mut_lot12_fe3.json`: media query-ul ecranului scund
    scos din stil.css) o pune înapoi în antet -> ROȘU (zona nu mai e în bară)."""
    from e2e_bloc_a import _deschide_factura
    pg = patron.pg
    pg.set_viewport_size({"width": 1280, "height": 520})
    _deschide_factura(patron, factura_e2e, factura_e2e["factura_id"])
    pg.click(_F + "#fd-email")
    pg.wait_for_selector(_F + "#fd-email-send", timeout=20000)
    pg.fill(_F + "#fd-email-input", "")
    pg.evaluate("() => { const c = document.querySelector('.fereastra:last-of-type .fereastra-corp'); c.scrollTop = c.scrollHeight; }")
    pg.click(_F + "#fd-email-send")
    pg.wait_for_function("() => (document.querySelector('.fereastra:last-of-type #fd-email-rez') || {}).innerText", timeout=20000)
    pg.wait_for_timeout(1200)   # derularea lină a lui `aduInVedere`, dacă ar fi fost nevoie de ea
    patron.captura("email_factura_in_vedere")
    assert pg.inner_text(_F + "#fd-email-rez").strip() == "Introdu o adresă validă."
    v = _in_vedere(pg, "#fd-email-rez")
    assert v["ok"], v
    assert pg.eval_on_selector(_F + "#fd-email-rez", "z => !!z.closest('.bara-fixa')"), "zona refuzului nu e în bara lipită jos (C164)"


def test_def_45_confirmarea_modelului_de_factura_vine_in_vedere(patron, firma_e2e):
    """45, a treia zonă: „Model factură” -> „Salvează” adus la marginea de jos -> apăsat: „✓ Model salvat.” (scris direct în
    `#mf-rezultat`, clasa `em-bun` pusă după text) intră în zona vizibilă."""
    from e2e_bloc_a import _card
    pg = patron.pg
    pg.set_viewport_size({"width": 1280, "height": 520})
    patron.firma(firma_e2e["nume"])
    _card(patron, "facturi", "#fac-model")
    pg.click("#fac-model")
    pg.wait_for_selector(_F + "#mf-salveaza", timeout=25000)
    _la_marginea_de_jos(pg, "#mf-salveaza")
    pg.click(_F + "#mf-salveaza")
    pg.wait_for_function("() => (document.querySelector('.fereastra:last-of-type #mf-rezultat') || {}).innerText", timeout=20000)
    pg.wait_for_timeout(1200)
    patron.captura("model_factura_in_vedere")
    assert pg.inner_text(_F + "#mf-rezultat").strip() == "✓ Model salvat."
    v = _in_vedere(pg, "#mf-rezultat")
    assert v["ok"], v
