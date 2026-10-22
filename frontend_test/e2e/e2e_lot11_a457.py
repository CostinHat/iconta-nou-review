# -*- coding: utf-8 -*-
"""Lotul 11, comanda 11.3 pct.4 (Costin 22.10.2026, verbatim în DECIZII „Comanda 11.3”) — deficiența 457: „ciornele făcute de contabil nu
ajung în nicio coadă (182 nerezolvată); după contarea din bancă, rândul spune «la validare» deși nota e ciornă.”

Pe aplicația din index, pe baza de TEST, pe firma nouă a fișierului (`firma_e2e`), cu contul contabilului-șef (`patron`: validează, deci
ciornele lui nu pleacă în coada patru-ochi — exact cazul de pe producție, F1: nota comisionului din 16.10, scrisă de contabil).
Datele se fac pe drumul aplicației (nota pe `POST /tenants/{id}/jurnal`, extrasul încărcat în ecranul Bancă, „Contează” apăsat); nicio
scriere SQL (garda `core/test_e2e_fara_date_fabricate.py`)."""
import time

from conftest import linie_nota, sql
from e2e_bloc_a import AZI, _api, _card, _ok, pregateste_firma


def _fata(pg):
    return ".fereastra:last-of-type"


def _de_validat(e):
    """Pagina principală -> cardul „De validat” -> fereastra, cu lista „Notele tale în ciornă” încărcată."""
    pg = e.pg
    e.acasa()
    pg.click("button.cab-card:has([data-cheie='validat'])")
    pg.wait_for_selector(_fata(pg) + " #val-ciorne .val-ciorne-firma", timeout=30000)


def _status(firma, nid):
    return sql('SELECT status FROM "%s".inregistrari WHERE id = %%s' % firma["schema"], (nid,))[0][0]


def test_def_457_ciorna_contabilului_e_in_coada_lui_si_se_valideaza_de_acolo(patron, firma_e2e):
    """457 (182). Pașii contabilului: scrie o notă (rămâne ciornă: el validează, deci nu pleacă la nimeni) -> pagina principală ->
    „De validat” -> „Notele tale în ciornă”: rândul notei, „nevalidată, netrimisă”, cu „Validează” și „Deschide nota” -> „Deschide nota”
    duce în Registrul jurnal, pe nota evidențiată -> înapoi -> „Validează” -> confirmarea „Ai validat nota …: a intrat în evidență.”, iar
    nota iese din listă (și e validată în Registrul jurnal)."""
    pregateste_firma(patron, firma_e2e)
    tid = firma_e2e["tenant_id"]
    desc = "Ciornă proprie probă E2E 457 %d" % (time.time() % 100000)
    nid = _ok(_api(patron, "POST", "/tenants/%d/jurnal" % tid, {"data": AZI.isoformat(), "descriere": desc, "document_ref": "Chitanța E2E-457",
                                                              "linii": [linie_nota("5311", "4111", "75.00")]}), "nota")["id"]
    assert _status(firma_e2e, nid) == "ciorna"
    pg = patron.pg
    _de_validat(patron)
    rand = _fata(pg) + " #val-ciorne li[data-ciorna='%d']" % nid
    pg.wait_for_selector(rand, timeout=20000)
    pg.eval_on_selector(rand, "e => e.scrollIntoView({block: 'center'})")
    t = pg.inner_text(rand)
    patron.captura("in_coada")
    assert desc in t and "rulaj 75,00 lei" in t and "nevalidată, netrimisă" in t, t
    assert pg.locator(rand + " [data-val-ciorna]").count() == 1, "rândul ciornei n-are „Validează”: %s" % t
    # „Deschide nota” -> Registrul jurnal, pe luna notei, cu nota evidențiată
    pg.click(rand + " [data-deschide-ciorna]")
    pg.wait_for_selector(_fata(pg) + " [data-nota-id='%d']" % nid, timeout=30000)
    assert desc in pg.inner_text(_fata(pg) + " [data-nota-id='%d']" % nid)
    patron.captura("registru_jurnal")
    pg.click(_fata(pg) + " .nav-inapoi")
    pg.wait_for_selector(rand, timeout=20000)
    # „Validează” din coada lui
    pg.click(rand + " [data-val-ciorna]")
    pg.wait_for_selector(rand, state="detached", timeout=30000)
    pg.wait_for_function("() => { const f = [...document.querySelectorAll('.fereastra')].pop(); return f && f.innerText.includes('Ai validat nota'); }",
                         timeout=20000)
    patron.captura("validata")
    assert "a intrat în evidență" in patron.fereastra()
    assert _status(firma_e2e, nid) == "validata"


def test_def_457_contarea_din_banca_spune_ciorna_nu_la_validare(patron, firma_e2e):
    """457, al doilea defect. Pașii contabilului: Bancă -> încarcă extrasul cu un comision -> „Contează 627=5121” -> rândul spune
    „Contată · notă ciornă” (nota e ciornă, n-a trimis-o nimeni la validare), NU „la validare” și nu „Contat ✓” -> „De validat”: nota
    comisionului e în „Notele tale în ciornă” -> „Validează” -> înapoi în Bancă, rândul spune „Contat ✓”."""
    pregateste_firma(patron, firma_e2e)
    tag = "E2E457B%d" % (time.time() % 100000)
    zi = AZI.strftime("%d.%m.%Y")
    extras = "Data;Detalii;Suma\n%s;Comision administrare cont %s;-12,50\n" % (zi, tag)
    patron.firma(firma_e2e["nume"])
    pg = patron.pg
    _card(patron, "banca", "#bk-fisier")
    pg.set_input_files("#bk-fisier", {"name": "extras_%s.csv" % tag, "mimeType": "text/csv", "buffer": extras.encode("utf-8")})
    pg.wait_for_function("() => document.querySelector('#bk-mesaj').innerText.includes('importat')", timeout=30000)
    rand = pg.locator(".pf-frand", has_text="Comision administrare cont " + tag)
    rand.locator("[data-cont]").click()
    pg.wait_for_function("() => document.querySelector('#bk-mesaj').innerText.includes('creat')", timeout=30000)
    rand.get_by_text("Contată · notă ciornă").wait_for(timeout=20000)
    t = rand.inner_text()
    patron.captura("banca_ciorna")
    assert "la validare" not in t and "Contat ✓" not in t, t
    assert "ciornă" in pg.inner_text("#bk-mesaj"), pg.inner_text("#bk-mesaj")   # mesajul de după „Contează” spunea deja starea reală
    # nota comisionului e în coada contabilului
    nid = sql('SELECT i.id FROM "%s".inregistrari i WHERE i.descriere LIKE %%s ORDER BY i.id DESC LIMIT 1' % firma_e2e["schema"],
              ("%" + tag + "%",))[0][0]
    _de_validat(patron)
    rv = _fata(pg) + " #val-ciorne li[data-ciorna='%d']" % nid
    pg.wait_for_selector(rv, timeout=20000)
    assert "nevalidată, netrimisă" in pg.inner_text(rv), pg.inner_text(rv)
    pg.click(rv + " [data-val-ciorna]")
    pg.wait_for_selector(rv, state="detached", timeout=30000)
    assert _status(firma_e2e, nid) == "validata"
    patron.firma(firma_e2e["nume"])
    _card(patron, "banca", "#bk-fisier")
    rand = pg.locator(".pf-frand", has_text="Comision administrare cont " + tag)
    rand.get_by_text("Contat ✓").wait_for(timeout=20000)
    patron.captura("banca_validata")
