# -*- coding: utf-8 -*-
"""Lotul 11, W4 — decizia Costin 10.3 (verbatim în DECIZII „Comanda 10.3” pct.4): „Totalurile și rezumatul fix, mesajele lângă buton, 394
la 1280×720: da, reorganizezi ecranele; totul încape într-un ecran, fără derulare.” Pașii contabilului pe aplicația din index, pe baza de
TEST, pe firme NOI de test, la 1280×720 (mărimea refăcută la final).

Datele de pornire: notele Registrului jurnal se scriu cu `e2e_bloc_e._nota` (drumul `jurnal_api.creeaza` / `valideaza`, ca la celelalte
e2e ale jurnalului); ajustările fiscale se scriu prin ruta aplicației (`POST /tenants/{id}/ajustari-fiscale`, din sesiunea contabilului).
Nicio inserare SQL directă."""
import datetime as _dt

import pytest

from conftest import INALT, LAT, firma_noua
from e2e_lot82 import firma_profit  # noqa: F401 — fixtura (firmă nouă pe impozit pe profit)

AZI = _dt.date.today()
LAT_MIC, INALT_MIC = 1280, 720


@pytest.fixture(scope="module")
def firma_w4():
    for f in firma_noua():
        yield f


@pytest.fixture()
def ecran_mic(patron):
    patron.pg.set_viewport_size({"width": LAT_MIC, "height": INALT_MIC})
    try:
        yield patron
    finally:
        patron.pg.set_viewport_size({"width": LAT, "height": INALT})


_CORP = "[...document.querySelectorAll('.fereastra-corp')].pop()"


# ── 394 la 1280×720 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_394_nota_noua_incape_la_1280x720(ecran_mic, firma_w4):
    """394 (10.3: „394 la 1280×720 […] fără derulare”). Pașii: 8 note în luna curentă -> Registru jurnal -> „+ Notă nouă”: fereastra nu
    derulează, „Salvează” se vede; data, descrierea și documentul stau pe un rând -> „Renunță”: notele revin."""
    from e2e_bloc_a import _card
    from e2e_bloc_e import _nota
    for i in range(8):
        _nota(firma_w4, AZI.replace(day=1).isoformat(), [{"debit": "627", "credit": "5121", "suma": 10 + i}], "Comision E2E W4 %d" % i,
              document_ref="Extras bancar E2E W4 nr. %d" % i)
    pg = ecran_mic.pg
    ecran_mic.firma(firma_w4["nume"])
    _card(ecran_mic, "jurnal", "#j-nota-noua")
    pg.click("#j-nota-noua")
    pg.wait_for_selector("#je-salveaza", timeout=10000)
    pg.wait_for_timeout(400)
    m = pg.evaluate("""() => { const c = %s, s = document.querySelector('#je-salveaza');
      const sus = ['#je-data', '#je-desc', '#je-doc'].map((x) => Math.round(document.querySelector(x).getBoundingClientRect().top));
      return {sh: c.scrollHeight, ch: c.clientHeight, jos_s: s.getBoundingClientRect().bottom, jos_c: c.getBoundingClientRect().bottom,
              un_rand: new Set(sus).size === 1}; }""" % _CORP)
    ecran_mic.captura()
    assert m["sh"] <= m["ch"] + 1 and m["jos_s"] <= m["jos_c"] and m["un_rand"], m
    pg.click("#je-renunta")
    pg.wait_for_function("() => document.body.innerText.includes('Comision E2E W4 7')", timeout=20000)


def test_def_394_migrare_cabinet_incape_la_1280x720_cu_saga_si_cum_se_face(ecran_mic):
    """394 (10.3). Pașii: Firme -> Migrare cabinet: cei 12 pași la vedere, fără derulare -> SAGA: tot fără derulare (înainte: 92 px) ->
    „Cum se face”: textul se arată peste pași, întreg în fereastră, iar fereastra tot nu derulează (înainte: 326 px)."""
    from e2e_lot5_migrare import _migrare
    pg = ecran_mic.pg
    _migrare(ecran_mic)
    masoara = """() => { const c = %s, rc = c.getBoundingClientRect(), pasi = [...c.querySelectorAll('#mig-meniu .mig-op')];
      const t = c.querySelector('#mig-apl-text'), rt = t && t.offsetParent ? t.getBoundingClientRect() : null;
      return {sh: c.scrollHeight, ch: c.clientHeight, la_vedere: pasi.filter((x) => x.getBoundingClientRect().bottom <= rc.bottom + 1).length,
              cum_in_corp: rt ? rt.bottom <= rc.bottom + 1 : null}; }""" % _CORP
    stari = {"fara": pg.evaluate(masoara)}
    pg.click("#mig-aplicatii button[data-aplicatie='saga']")
    pg.wait_for_selector("#mig-apl-aleasa", timeout=20000)
    pg.wait_for_timeout(300)
    stari["saga"] = pg.evaluate(masoara)
    pg.click("#mig-apl-cum > summary")
    pg.wait_for_selector("#mig-apl-text", state="visible", timeout=5000)
    stari["cum"] = pg.evaluate(masoara)
    ecran_mic.captura()
    pg.click("#mig-aplicatii button[data-aplicatie='saga']")   # al doilea clic revine la pașii cu modele (starea inițială)
    assert all(s["sh"] <= s["ch"] + 1 and s["la_vedere"] == 12 for s in stari.values()), stari
    assert stari["cum"]["cum_in_corp"], stari


# ── un ecran cu total ──────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_421_totalurile_registrului_jurnal_raman_in_vedere(ecran_mic, firma_w4):
    """10.3: „Totalurile […] fix”. Pașii: 30 de note validate în luna curentă -> Registru jurnal: totalul sumelor debitoare se vede jos fără
    derulare (înainte: la capătul celor 30 de note, sub marginea ferestrei) și după derularea la mijlocul listei.
    Cele 30 de note sunt plăți din casă (6022 = 5311, 1 + 2 + … + 30 = 465 lei): întâi numerarul din care se plătesc, ridicarea de la bancă
    (5311 = 581, 500 lei, validată) — casa nu poate ajunge sub zero (deficiența 406, `casa_sold.refuz_iesire` la validare; lotul 11, 455:
    aceeași cifră ca registrul de casă). Fără ea, prima notă de 1,00 lei se refuză la validare: „nu încape în casă”."""
    from e2e_bloc_a import _card
    from e2e_bloc_e import _nota
    _nota(firma_w4, AZI.replace(day=1).isoformat(), [{"debit": "5311", "credit": "581", "suma": 500}], "Ridicare numerar E2E W4",
          valideaza=True, document_ref="Cec E2E W4")
    for i in range(30):
        _nota(firma_w4, AZI.replace(day=1).isoformat(), [{"debit": "6022", "credit": "5311", "suma": 1 + i}], "Consum E2E W4 total %d" % i,
              valideaza=True, document_ref="Bon E2E W4 nr. %d" % i)
    pg = ecran_mic.pg
    ecran_mic.firma(firma_w4["nume"])
    _card(ecran_mic, "jurnal", "#j-nota-noua")
    pg.wait_for_function("() => document.body.innerText.includes('Consum E2E W4 total 29')", timeout=20000)
    # [lotul 14, 687] corpul ferestrei nu mai derulează: lista notelor derulează în zona ei (`.zona-derulare`, pusă de navigator), iar rezumatul
    # și totalurile rămân în corp; se derulează zona, se măsoară totalurile față de corp
    vede = """(loc) => { const corp = %s; const c = corp.querySelector('.zona-derulare') || corp;
      c.scrollTop = loc ? Math.round((c.scrollHeight - c.clientHeight) / 2) : 0;
      const t = [...corp.querySelectorAll('.fd-totaluri .fd-tot-rand')].find((x) => x.innerText.startsWith('Total sume debitoare'));
      if (!t) return null; const r = t.getBoundingClientRect(), rc = corp.getBoundingClientRect(), el = document.elementFromPoint(r.left + 10, r.top + r.height / 2);
      return {in_corp: r.top >= rc.top && r.bottom <= rc.bottom + 1, vizibil: !!(el && t.contains(el)), deruleaza: c.scrollHeight - c.clientHeight}; }""" % _CORP
    v0, v1 = pg.evaluate(vede, 0), pg.evaluate(vede, 1)
    ecran_mic.captura()
    assert v0 and v0["deruleaza"] > 300, v0                         # anti-vacuu: lista chiar derulează
    assert v0["in_corp"] and v0["vizibil"] and v1["in_corp"] and v1["vizibil"], (v0, v1)
    # „Registru jurnal” are rezumatul lipit sus: luna și butoanele rămân în vedere după derulare
    # [lotul 14, 687] rezumatul nu mai e lipit de marginea de sus a corpului (stă sub titlul ferestrei), ci rămâne FIX în afara zonei care
    # derulează: după ce lista e derulată până la capăt, rezumatul e în același loc, în corp, și se vede (nu e acoperit)
    poz = """() => { const c = %s; const z = c.querySelector('.zona-derulare') || c; const r = c.querySelector('#j-rezumat');
      const mv = (s) => { z.scrollTop = s; const b = r.getBoundingClientRect(), cb = c.getBoundingClientRect(), el = document.elementFromPoint(b.left + 10, b.top + 10);
        return {sus: Math.round(b.top - cb.top), in_corp: b.top >= cb.top && b.bottom <= cb.bottom + 1, vizibil: !!(el && r.contains(el))}; };
      return [mv(0), mv(z.scrollHeight)]; }""" % _CORP
    sus, jos = pg.evaluate(poz)
    assert sus == jos and jos["in_corp"] and jos["vizibil"], (sus, jos)


# ── un mesaj lângă buton ─────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_410_mesajul_ajustarii_sta_langa_buton(ecran_mic, firma_profit):  # noqa: F811 — fixtura din e2e_lot82
    """10.3: „mesajele lângă buton”. Pașii: firmă pe impozit pe profit (`e2e_lot82.firma_profit`), 25 de ajustări fiscale pe anul în curs ->
    Registrul de evidență fiscală (impozit pe profit), anul în curs ->
    rândul D101 și trimestrul alese, suma goală -> „Adaugă ajustarea”: refuzul serverului apare lângă buton, în vedere (`#aj-mesaj`, sau
    caseta „NU s-a salvat.” a butonului, care îl ține cât stă — lotul 13, 515)
    (înainte: sub lista celor 25 de ajustări, deasupra câmpurilor, departe de bara de jos)."""
    from e2e_bloc_a import _api, _ok, _card
    tid, an = firma_profit["tenant_id"], AZI.year
    d = _ok(_api(ecran_mic, "GET", "/tenants/%d/ajustari-fiscale?an=%d" % (tid, an)), "ajustări")
    anuale = set(d.get("anuale") or [])
    rand = next(r["rand"] for r in d["randuri"] if r["rand"] not in anuale)
    for i in range(25):
        _ok(_api(ecran_mic, "POST", "/tenants/%d/ajustari-fiscale" % tid,
                 {"an": an, "rand": rand, "trim": 1 + i % 3, "suma": "%d.00" % (10 + i), "descriere": "Ajustare E2E W4 %d" % i,
                  "document": "Notă E2E W4 %d" % i}), "ajustarea %d" % i)
    pg = ecran_mic.pg
    ecran_mic.firma(firma_profit["nume"])
    _card(ecran_mic, "regfiscal", "#rf-var")
    pg.fill("#rf-an", str(an))
    pg.dispatch_event("#rf-an", "change")
    pg.wait_for_function("() => document.body.innerText.includes('Ajustare E2E W4 24')", timeout=30000)
    pg.wait_for_selector("#aj-adauga", timeout=30000)
    pg.select_option("#aj-rand", rand)
    pg.select_option("#aj-trim", "1")
    pg.click("#aj-adauga")
    pg.wait_for_function("() => (document.querySelector('#aj-mesaj') || {}).innerText", timeout=20000)
    m = pg.evaluate("""() => { const c = %s, rc = c.getBoundingClientRect(), b = document.querySelector('#aj-adauga').getBoundingClientRect();
      // [lotul 13, 515] refuzul de lângă buton stă în caseta „NU s-a salvat.” a butonului (`api.arataRefuzul`: zona lui se ascunde cât stă
      // caseta, același text o singură dată); se măsoară ce vede omul
      const zm = document.querySelector('#aj-mesaj'), bt = document.querySelector('#aj-adauga');
      const z = zm.hidden && bt._refuz && bt._refuz.isConnected ? bt._refuz : zm, r = z.getBoundingClientRect();
      return {in_corp: r.top >= rc.top - 1 && r.bottom <= rc.bottom + 1, distanta: Math.round(Math.max(0, r.top - b.bottom, b.top - r.bottom)),
              text: z.innerText.trim()}; }""" % _CORP)
    ecran_mic.captura()
    assert m["in_corp"] and m["distanta"] <= 80 and m["text"], m
