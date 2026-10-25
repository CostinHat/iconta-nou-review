# -*- coding: utf-8 -*-
"""Lotul 11, comanda 11.1 (Costin 21.10.2026, verbatim în DECIZII „Comanda 11.1”) — subagentul W1: 440 (pct.16) pe „Notă nouă” din
Registru jurnal și 443 (pct.19) pe nota chitanței. Pașii contabilului pe aplicația din index, pe baza de TEST, pe firme NOI de test
(`firma_noua`); CUI-urile au cifra de control verificată (`cui_cu_control`, algoritmul din CLAUDE.md, prin `pregateste_firma`).

Date de pornire scrise direct: niciuna. Numerotarea, profilul, seria chitanțelor și factura se fac pe rutele pe care le cheamă ecranele
(`PUT facturi/numerotare`, `pregateste_firma`, `POST firma-profil/date`, `emite_api`); ce se probează (nota, chitanța) se face pe ecran."""
import pytest

from conftest import firma_noua, sql
from e2e_bloc_a import _api, _card, _octeti, _ok, _pdf_text, emite_api, pregateste_firma
from e2e_bloc_b import _deschide_rand


@pytest.fixture(scope="module")
def firma_w1():
    for f in firma_noua():
        yield f


# ── 440 — „Notă nouă”: toate erorile liniilor deodată, fiecare cu textul ei, lângă câmp ─────────────────────────────────────────
def test_def_440_nota_noua_arata_toate_erorile_liniilor_deodata(patron, firma_w1):
    """440 (comanda 11.1 pct.16: „toate erorile apar deodată, fiecare cu textul ei, în casetă și lângă câmp.”). Înainte, serverul refuza
    nota la PRIMA problemă: o notă cu două linii greșite se salva de patru ori, câte o eroare.
    Pașii: Registru jurnal -> „+ Notă nouă” -> linia 1: 9999 = (credit gol), 100 -> „+ linie” -> linia 2: 401 = 5121, -5, fără partener ->
    „Salvează”: fereastra spune toate cele patru probleme (contul 9999 din afara planului, contul creditor lipsă, suma -5, partenerul
    cerut la 401), fiecare cu textul ei; suma liniei 2 și conturile liniei 1 sunt marcate lângă câmp (aria-invalid, textul legat prin
    aria-describedby); nota nu se scrie."""
    s = firma_w1["schema"]
    pg = patron.pg
    patron.firma(firma_w1["nume"])
    _card(patron, "jurnal", "#j-nota-noua")
    pg.click("#j-nota-noua")
    pg.wait_for_selector("#je-salveaza", timeout=10000)
    pg.fill("#je-desc", "Notă E2E 440 W1")
    pg.fill("#je-doc", "Document E2E 440")
    pg.click("#je-plus")
    r1, r2 = pg.locator("#je-linii > div").nth(0), pg.locator("#je-linii > div").nth(1)
    r1.locator(".je-deb").fill("9999")
    r1.locator(".je-sum").fill("100")
    r2.locator(".je-deb").fill("401")
    r2.locator(".je-cre").fill("5121")
    r2.locator(".je-sum").fill("-5")
    n0 = sql('SELECT count(*) FROM "%s".inregistrari' % s)[0][0]
    pg.click("#je-salveaza")
    pg.wait_for_function("() => [...document.querySelectorAll('.fereastra')].pop().innerText.includes('linia 2 e pe contul 401')",
                         timeout=20000)
    patron.captura()
    text = pg.inner_text(".fereastra:last-of-type")
    for bucata in ("linia 1: Contul 9999", "linia 1 n-are contul creditor", "linia 2 are suma -5", "linia 2 e pe contul 401"):
        assert bucata in text, (bucata, text)                                     # 440: „toate erorile apar deodată, fiecare cu textul ei”
    assert "mai sus" not in text and "mai jos" not in text, text
    campuri = pg.evaluate("""() => ['je-sum-1', 'je-deb-0', 'je-cre-0'].map((id) => {
        const el = document.getElementById(id);
        if (!el) return [id, null, []];
        const d = (el.getAttribute('aria-describedby') || '').split(' ').map((x) => document.getElementById(x)).filter(Boolean);
        return [id, el.getAttribute('aria-invalid'), d.map((x) => x.textContent.trim())];
      })""")
    assert campuri[0][1] == "true" and any("linia 2 are suma -5" in t for t in campuri[0][2]), campuri   # „lângă câmp”
    assert campuri[1][1] == "true" and any("Contul 9999" in t for t in campuri[1][2]), campuri
    assert campuri[2][1] == "true" and any("n-are contul creditor" in t for t in campuri[2][2]), campuri
    assert sql('SELECT count(*) FROM "%s".inregistrari' % s)[0][0] == n0                                  # nota nu s-a scris


# ── 443 — seria și numărul separat pe nota chitanței (Registru jurnal) ──────────────────────────────────────────────────────────────
def test_def_443_nota_chitantei_din_registru_jurnal_spune_f6_nr_1(patron, firma_w1):
    """443 (pct.19: „seria și numărul se afișează separat peste tot (F6 nr. 1, nu F61)”). Pașii: Configurare emitere cu seria „F6”, de la
    1 (ruta ecranului) + seria chitanțelor (Date firmă) -> factura emisă (ruta formularului) -> Facturi -> Istoric -> detaliul ei ->
    „Emite chitanță” -> „Emite” -> Registru jurnal: rândul notei chitanței spune „factura F6 nr. 1 din …” (ce stinge și „contravaloare
    factura …”), nicăieri „F61”; PDF-ul chitanței: „reprezentând: contravaloare factura F6 nr. 1 din …”, titlul „Chitanța <serie> nr. <număr>”."""
    tid, s = firma_w1["tenant_id"], firma_w1["schema"]
    _ok(_api(patron, "PUT", "/tenants/%d/facturi/numerotare" % tid, {"serie": "F6", "numar_start": 1}), "seria F6")
    pregateste_firma(patron, firma_w1)
    if not sql('SELECT 1 FROM "%s".firma_profil WHERE serie_chitanta IS NOT NULL' % s):
        _ok(_api(patron, "POST", "/tenants/%d/firma-profil/date" % tid, {"serie_chitanta": "CHW"}), "seria chitanțelor")
    f = emite_api(patron, firma_w1)
    assert sql('SELECT serie, numar FROM "%s".facturi WHERE id = %%s' % s, (f["factura_id"],))[0] == ("F6", "F61")
    pg = patron.pg
    patron.firma(firma_w1["nume"])
    _card(patron, "facturi", "#fac-istoric")
    pg.click("#fac-istoric")
    pg.wait_for_selector(".fereastra:last-of-type .fac-frand-btn[data-id='%s']" % f["factura_id"], timeout=20000)
    pg.click(".fereastra:last-of-type .fac-frand-btn[data-id='%s']" % f["factura_id"])
    pg.wait_for_selector(".fereastra:last-of-type #fd-chitanta", timeout=20000)
    pg.click(".fereastra:last-of-type #fd-chitanta")
    pg.wait_for_selector(".fereastra:last-of-type #fd-chit-ok", timeout=20000)
    pg.click(".fereastra:last-of-type #fd-chit-ok")
    pg.wait_for_function("() => document.body.innerText.includes('a fost emisă')", timeout=20000)
    nid = sql('SELECT inregistrare_id FROM "%s".chitante WHERE factura_id = %%s AND NOT anulata' % s, (f["factura_id"],))[0][0]
    patron.firma(firma_w1["nume"])
    _card(patron, "jurnal", "#j-nota-noua")
    sel = ".fereastra:last-of-type tbody.tn-nota[data-nota-id='%s']" % nid   # [lotul 12, 617] rândul notei în tabelul de note
    pg.wait_for_selector(sel, timeout=30000)
    _deschide_rand(patron, sel)        # [617] documentul justificativ („… · stinge …”) și liniile notei, în detaliul rândului: deschis
    rand = " ".join(pg.inner_text(sel).split())
    patron.captura()
    assert "stinge factura F6 nr. 1 din" in rand, rand             # 443: „F6 nr. 1”
    assert "F61" not in rand, rand                                  # 443: „nu F61”
    # chitanța însăși (PDF-ul, aceeași cale și sesiune ca butonul ecranului): „reprezentând: contravaloare factura F6 nr. 1 din …”, titlul
    # documentului „Chitanța <serie> nr. <număr>”
    cid, ser_ch, nr_ch = sql('SELECT id, serie, numar FROM "%s".chitante WHERE factura_id = %%s AND NOT anulata' % s, (f["factura_id"],))[0]
    text, titlu = _pdf_text(_octeti(patron, "/tenants/%d/chitante/%d/pdf" % (tid, cid)))
    assert "contravaloare factura F6 nr. 1 din" in text and "F61" not in text, text[:600]
    assert titlu == "Chitanța %s nr. %s" % (ser_ch, nr_ch), titlu
