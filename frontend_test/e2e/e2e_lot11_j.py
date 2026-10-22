# -*- coding: utf-8 -*-
"""Lotul 11 (comanda Costin 11.1), subagentul J — testele de capăt la capăt.

  - 8c (decizia 10.3: „8c: reparația centrală, cu DS cap. 6 actualizat.”; clasa din comanda 10.2 pct.8c: „După generare, titlul «Notă
    generată» e roșu, conturile notei nu se văd, iar «Generează notă» rămâne activ.”) — Raport Z și amortizarea lunii, pe drumul unic
    `api.dupaGenerare`;
  - 422 (decizia 10.3: „contorul «De validat» și clopoțelul nu se actualizează după acțiuni (clasa 286); se repară.”);
  - pct.23 (mărunte): etichetele „mâncare” / „alcool” și „Consum pe rețetă” numai la alimentația publică; „Generează amortizarea” inactiv
    pe luna deja amortizată, cu nota numită, iar a doua generare refuzată de server.

Pașii contabilului pe aplicația din index, pe baza de TEST. Nimic nu se scrie direct în bază (garda `core/test_e2e_fara_date_fabricate.py`):
mijlocul fix al amortizării intră pe drumul aplicației — Migrare -> Mijloace fixe -> „Salvează registrul” (`POST
/tenants/{id}/mijloace-fixe-import`, ca `e2e_bloc_d.firma_mf`; registrul nu are alt ecran de adăugare) —, iar nota de amortizare se
validează pe ruta butonului „Validează” din Registru jurnal (`POST /tenants/{id}/jurnal/{nota}/valideaza`, chemată prin `api.js` din pagină).
"""
import re
import time as _t

from conftest import sql
from e2e_bloc_d import PATRON, _api as _api_cont
from e2e_bloc_b import _coada_nota, _firma_gata, _nota_prin_ecran, ana, ana_cont  # noqa: F401 — fixturile asistentei
from e2e_bloc_c import AZI, _deschide, firma_cv  # noqa: F401 — firma cantitativ-valorică (comerț, fără rețete)

CASA = "8000000001"
VERDE_INCHIS = "rgb(27, 115, 73)"   # --verde-inchis (#1b7349), titlul `.caseta-ok` (stil.css)


def _z(patron, f, nr, total_21="231", numerar="231", card="0", bonuri="12"):
    pg = patron.pg
    _deschide(patron, f["nume"], "raportz", "#z-salveaza")
    pg.fill("#z-data", AZI.isoformat())
    pg.fill("#z-nui", CASA)
    pg.fill("#z-nr", nr)
    pg.fill("#z-21", total_21)
    pg.fill("#z-num", numerar)
    pg.fill("#z-card", card)
    pg.fill("#z-bonuri", bonuri)
    return pg


# ================================================================ 8c — după generare (Raport Z)
def test_def_8c_dupa_generarea_notei_z_confirmarea_e_verde_cu_conturile_iar_butonul_inactiv(patron, firma_cv):
    """8c. Pașii: Raport Z nr. 3101, total 21% 231,00, numerar 200,00 -> „Generează notă” (refuzat: numerar + card ≠ total) -> card 31,00
    -> „Generează notă”. Confirmarea: caseta verde (`.caseta-ok`, titlul „Notă generată” în verdele închis, nu roșul refuzului), conturile
    notei (5311 = 707 · 200,00 lei; 5125 = 707 · 31,00 lei; 707 = 4427 · 40,09 lei); „Generează notă” inactiv, cu motivul lângă el
    („Nota e generată — o vezi în Registru jurnal.”); alt număr de Z scris -> butonul redevine activ, motivul dispare."""
    pg = _z(patron, firma_cv, "3101", numerar="200")
    pg.click("#z-salveaza")
    pg.wait_for_function("() => (document.querySelector('#z-rezultat') || {innerText: ''}).innerText.includes('diferență')", timeout=20000)
    pg.fill("#z-card", "31")
    pg.click("#z-salveaza")
    pg.wait_for_selector("#z-rezultat .caseta-ok .cok-titlu", timeout=20000)
    patron.captura("generata")
    assert pg.inner_text("#z-rezultat .cok-titlu") == "Notă generată"
    assert pg.eval_on_selector("#z-rezultat .cok-titlu", "e => getComputedStyle(e).color") == VERDE_INCHIS
    assert "msg-eroare" not in (pg.get_attribute("#z-rezultat", "class") or "")
    linii = [" ".join(x.split()) for x in pg.inner_text("#z-nota-linii").split("\n")]
    # TVA = 231,00 × 21 / 121 = 40,09 (CF art.291 alin.(1) lit.a, cota standard; rotunjire aritmetică)
    assert linii == ["5311 = 707 · 200,00 lei", "5125 = 707 · 31,00 lei", "707 = 4427 · 40,09 lei"], linii
    assert pg.is_disabled("#z-salveaza")
    motiv = pg.get_attribute("#z-salveaza", "aria-describedby")
    assert motiv and pg.inner_text("#" + motiv) == "Nota e generată — o vezi în Registru jurnal."
    pg.fill("#z-nr", "3102")
    assert pg.is_enabled("#z-salveaza") and pg.query_selector("#z-salveaza-motiv-generat") is None


# ================================================================ pct.23 — etichetele alimentației publice la comerț
def test_def_23_z_la_comert_cotele_sunt_neutre_fara_consum_pe_reteta(patron, firma_cv):
    """pct.23: „etichetele «mâncare» / «alcool» și «Consum pe rețetă» la firme de comerț”. Pașii: firma de comerț (fără CAEN HoReCa,
    fără rețete) -> Raport Z: câmpurile se numesc „Total 11%” și „Total 21%”; Z generat -> la descărcare: „Ieșire pe articol”, fără
    „Consum pe rețetă”. Criteriul e al ecranului Stocuri (`stocuri_cv_api.retete_vizibile`: CAEN din CF art.48 alin.(2^2) / art.54
    alin.(4) sau rețete definite)."""
    pg = _z(patron, firma_cv, "3103")
    assert (pg.inner_text("#z-et-11"), pg.inner_text("#z-et-21")) == ("Total 11%", "Total 21%")
    pg.click("#z-salveaza")
    pg.wait_for_selector("#z-rezultat .caseta-ok", timeout=20000)
    (zid,) = [r[0] for r in sql('SELECT id FROM "%s".inregistrari WHERE numar = %%s' % firma_cv["schema"], ("Z-%s-3103" % CASA,))]
    pg.wait_for_selector("#z-descarcare [data-z='%d'] .zd-iesire" % zid, timeout=20000)
    patron.captura("comert")
    assert pg.query_selector("#z-descarcare [data-z='%d'] .zd-reteta" % zid) is None
    assert "rețetă" not in pg.inner_text("#z-descarcare")


# ================================================================ pct.23 + 8c — amortizarea lunii
def _mf(f, cod, valoare, luni, pif):
    """Mijlocul fix în registru, pe drumul aplicației: Migrare -> Mijloace fixe -> „Salvează registrul” (ruta importului, cu sesiunea
    contabilului-șef): liniar, 2131 / 2813, fără amortizare preluată."""
    st, r = _api_cont(PATRON, "POST", "/tenants/%d/mijloace-fixe-import" % f["tenant_id"],
                      {"randuri": [{"cod": cod, "denumire": cod, "valoare": float(valoare), "rezidual": 0, "dnf_luni": luni,
                                    "data_pif": pif, "metoda": "liniara", "cont_imobilizare": "2131", "cont_amortizare": "2813"}]})
    assert st == 200 and r.get("importati") == 1, (st, r)


def test_def_23_generarea_amortizarii_inactiva_pe_luna_amortizata_cu_nota_numita(patron, firma_cv):
    """pct.23: „«Generează amortizarea» activ pe luni deja amortizate”. Pașii: Registru jurnal, luna 08/2026 (încheiată) -> „Generează
    amortizarea” -> caseta verde cu nota (6811 = 2813 · <rata> lei), butonul inactiv cu motivul -> a doua generare (prin aplicație, aceeași
    rută) refuzată de server, numit („deja generată, cu exact sumele registrului”) -> nota validată -> luna redeschisă: butonul inactiv,
    motivul numește nota („Amortizarea lunii e generată: nota nr. crt. … validată”)."""
    f = firma_cv
    _mf(f, "MF-L11J-%d" % (int(_t.time()) % 100000), "12000", 60, "2026-05-10")
    pg = patron.pg
    _deschide(patron, f["nume"], "jurnal", "#j-amort")
    for _ in range(24):   # luna 08/2026
        if "08/2026" in pg.inner_text(".fereastra-corp .pf-intro"):
            break
        pg.click("#j-prev")
        pg.wait_for_timeout(700)
    assert "08/2026" in pg.inner_text(".fereastra-corp .pf-intro")
    pg.click("#j-amort")
    pg.wait_for_selector("#j-mesaj .caseta-ok", timeout=30000)
    patron.captura("amortizare_generata")
    assert re.search(r"6811 = 2813 · [\d.]+,\d\d lei", pg.inner_text("#j-mesaj .cok-linii")), pg.inner_text("#j-mesaj")
    assert pg.is_disabled("#j-amort")
    (nid,) = [r[0] for r in sql('SELECT id FROM "%s".inregistrari WHERE numar = %%s' % f["schema"], ("AMORT-2026-08",))]
    r = pg.evaluate("""async (tid) => { const m = await import('/static/js/api.js');
        try { await m.api.post(`/tenants/${tid}/amortizare?an=2026&luna=8`, {}); return 'scris'; } catch (e) { return e.mesaj; } }""",
                    f["tenant_id"])
    assert "deja generată, cu exact sumele registrului" in r, r
    assert len(sql('SELECT id FROM "%s".inregistrari WHERE numar = %%s' % f["schema"], ("AMORT-2026-08",))) == 1
    pg.evaluate("async ([tid, nid]) => { const m = await import('/static/js/api.js'); await m.api.post(`/tenants/${tid}/jurnal/${nid}/valideaza`, {}); }",
                [f["tenant_id"], nid])
    pg.click("#j-next")
    pg.wait_for_timeout(800)
    pg.click("#j-prev")
    pg.wait_for_function("() => /Amortizarea lunii e generată: nota nr\\. crt\\./.test((document.querySelector('#j-amort-motiv') || {}).innerText || '')",
                         timeout=20000)
    patron.captura("amortizare_validata")
    assert pg.is_disabled("#j-amort")
    assert "validată" in pg.inner_text("#j-amort-motiv")


# ================================================================ 422 — contorul „De validat” și clopoțelul
def _note_pe_card(pg):
    t = pg.inner_text(".cab-card-sinteza[data-cheie='validat']")
    m = re.search(r"(\d+)\s+(?:de\s+)?not[ăe] de validat", t)
    return int(m.group(1)) if m else 0


def test_def_422_contorul_de_validat_si_clopotelul_urmeaza_actiunile(ana, patron, firma_e2e):
    """422. Pașii: contabilul-șef are pagina principală deschisă și notificările văzute (clopoțelul fără cifră). Ana (asistentă) scrie o
    notă -> pleacă la validare. Fără reîncărcare, la întoarcerea în filă: clopoțelul arată 1, iar cardul „De validat” numără o notă în
    plus. Șeful validează nota (prin aplicație) -> fără reîncărcare: notificarea e rezolvată (clopoțelul fără cifră), cardul revine."""
    _firma_gata(firma_e2e)
    pg = patron.pg
    patron.acasa()
    pg.wait_for_function("() => (document.querySelector('.cab-card-sinteza[data-cheie=validat]') || {innerText: ''}).innerText.length > 0",
                         timeout=20000)
    pg.click("#nav-clopot")                       # notificările de dinainte: văzute
    pg.wait_for_selector(".clopot-item, .clopot-gol", timeout=20000)
    pg.wait_for_timeout(800)
    pg.click("#nav-clopot")
    pg.wait_for_function("() => (document.querySelector('#nav-clopot-badge') || {}).textContent === ''", timeout=15000)
    pg.wait_for_timeout(1500)
    n0 = _note_pe_card(pg)
    desc = "E2E 422 chirie %d" % (int(_t.time()) % 100000)
    nid = _nota_prin_ecran(ana, firma_e2e, desc, "2026-10-06", luna=(2026, 10))
    cid = _coada_nota(firma_e2e, nid)[0]
    pg.evaluate("() => document.dispatchEvent(new Event('visibilitychange'))")   # șeful se întoarce în filă
    pg.wait_for_function("() => (document.querySelector('#nav-clopot-badge') || {}).textContent === '1'", timeout=20000)
    pg.wait_for_function("(n) => { const t = document.querySelector(\".cab-card-sinteza[data-cheie='validat']\").innerText;"
                         " const m = t.match(/(\\d+)\\s+(?:de\\s+)?not[ăe] de validat/); return (m ? +m[1] : 0) === n; }",
                         arg=n0 + 1, timeout=20000)
    patron.captura("dupa_trimitere")
    pg.evaluate("async (cid) => { const m = await import('/static/js/api.js'); await m.api.post(`/coada/${cid}/aproba`, {}); }", cid)
    pg.wait_for_function("() => (document.querySelector('#nav-clopot-badge') || {}).textContent === ''", timeout=20000)
    pg.wait_for_function("(n) => { const t = document.querySelector(\".cab-card-sinteza[data-cheie='validat']\").innerText;"
                         " const m = t.match(/(\\d+)\\s+(?:de\\s+)?not[ăe] de validat/); return (m ? +m[1] : 0) === n; }",
                         arg=n0, timeout=20000)
    patron.captura("dupa_validare")
