# -*- coding: utf-8 -*-
"""Lotul 12, comanda Costin 12.3 (verbatim în DECIZII), pachetul `sal3`: C133.

  * C133 — pct.8: „«Scutit» și «Motiv» se pot corecta, cu jurnal (cine, când, vechi → nou); motivul e obligatoriu când e bifat «Scutit».”
    Salariații → „Corectează datele” arată scutirea salvată (Da / Nu) și, la „Da”, motivul scutirii (cele cinci motive ale D112); „Da”
    fără motiv se refuză lângă câmp; salvarea spune ce face corectura cu D112; fereastra arată apoi „Corecturile scutirii” (când, cine,
    câmp, valoare veche, valoare nouă). Refuzul serverului (motivul lipsă la „Scutit” = Da) stă pe câmpul motivului.

DATE DE PORNIRE fără ecran (declarate): salariatul salvat NESCUTIT se scrie cu INSERT, cum stă orice fișă salvată înainte de reparație (pe
F1 și F5 toți salariații sunt nescutiți); salariul lui la fel. CNP-ul are cifra de control verificată (algoritmul din CLAUDE.md).

Temei: OPANAF 605/2026 anexa 2, „Date de identificare ale asiguratului”, pct.12: „Motivul exceptării - se completează în cazul în care
caseta de la pct.11 a fost completată cu valoarea "1"” — motivele "1"–"5" (CF art.146 alin.(5^7) lit.a–e); "5" = „două sau mai multe
contracte individuale de muncă, a căror baza lunară cumulate […] este cel puţin egală cu salariul de bază minim brut pe ţară”."""
import re

import pytest

from conftest import firma_noua, sql

CNP_SAL3 = "1960101078916"   # cifra de control verificată (test_import_saga.CNP_OK)


@pytest.fixture(scope="module")
def firma_s3_noua():
    for f in firma_noua():
        yield f


@pytest.fixture()
def firma_s3(patron, firma_s3_noua):
    """Firma nouă, cu Date firmă și vectorul fiscal (idempotent)."""
    from e2e_bloc_a import pregateste_firma
    pregateste_firma(patron, firma_s3_noua, platitor=True, regim_fiscal="profit")
    return firma_s3_noua


def _api(e, metoda, cale, corp=None):
    from e2e_bloc_a import _api as a
    return a(e, metoda, cale, corp)


def _deschide_corectarea(pg, sid):
    """[lotul 13, 675] scutirea (o setare care schimbă cifrele) se corectează din „Date de calcul”, în fereastra salariatului."""
    if not pg.locator(".fereastra:last-of-type #ss-butoane").count():
        pg.wait_for_selector(".fereastra:last-of-type #sp-tabel tbody tr.sp-rand[data-sid='%s']" % sid, timeout=30000)
        pg.click(".fereastra:last-of-type #sp-tabel tbody tr.sp-rand[data-sid='%s'] .sp-deschide" % sid)
        pg.wait_for_selector(".fereastra:last-of-type #ss-butoane", timeout=30000)
    pg.click(".fereastra:last-of-type #ss-butoane [data-calcul='%s']" % sid)
    pg.wait_for_selector(".alegere-butoane:has(+ #ed-scutit)", timeout=20000)
    # fișa citită: scutirea salvată e pe câmp (datele deducerilor vin din aceeași cerere)
    pg.wait_for_function("() => (document.querySelector('#ed-scutit') || {}).value !== ''", timeout=20000)


def test_def_c133_scutirea_se_corecteaza_din_corecteaza_datele_cu_jurnal(patron, firma_s3):
    """C133. Pașii: salariatul salvat nescutit (fișă veche) -> Salariați -> „Corectează datele”: „Scutit de contribuția minimă” = Nu (din
    fișă), „Motivul scutirii” ascuns -> Da: motivul apare, nimic ales -> Salvează: „Alege o valoare” lângă motiv, nimic salvat -> motivul
    5 -> Salvează: „datele corectate s-au salvat” + „Corectura scutirii intră …” -> din nou „Corectează datele”: Scutit = Da, motivul 5,
    tabelul „Corecturile scutirii” cu cele două rânduri (Nu -> Da; — -> motivul 5) și numele contabilului. În bază: fișa (true, 5), jurnalul
    cu utilizatorul patron. Refuzul serverului: „Scutit” = Da cu motivul golit -> 422 pe câmpul `motiv_exceptare`."""
    f, s = firma_s3, firma_s3["schema"]
    sql('DELETE FROM "%s".salariati WHERE cnp = %%s' % s, (CNP_SAL3,))
    # date-de-pornire: salariatul salvat nescutit, cum stă orice fișă de dinainte de reparație
    sid = sql('INSERT INTO "%s".salariati (cnp, nume, prenume, data_angajare, scutit_contrib_minim, motiv_exceptare, cor, judet_casa, '
              "functie_baza, part_time, declaratie_copii) VALUES (%%s, 'CORECTAT', 'ANA', '2024-01-01', false, NULL, '241107', 'B', true, "
              "false, false) RETURNING id" % s, (CNP_SAL3,))[0][0]
    # date-de-pornire: salariul aceluiași salariat
    sql('INSERT INTO "%s".salariu_istoric (salariat_id, valabil_din, salariu_brut) VALUES (%%s, %%s, 5000)' % s, (sid, "2024-01-01"))
    uid = sql("SELECT id, TRIM(CONCAT_WS(' ', prenume, nume)) FROM public.users WHERE email = 'patron@prisma-cont.test'")[0]
    pg = patron.pg
    patron.firma(f["nume"])
    pg.click("#fa-salariati")
    _deschide_corectarea(pg, sid)
    assert pg.eval_on_selector("#ed-scutit", "s => s.value") == "false"
    assert pg.locator("#ed-motiv").is_visible() is False
    patron.captura("vechi_corecteaza_datele_scutit_nu")
    pg.click(".alegere-butoane:has(+ #ed-scutit) button[data-valoare='true']")   # [lotul 13, 676] Da / Nu = butoane
    assert pg.locator(".alegere-butoane:has(+ #ed-motiv)").is_visible() and pg.eval_on_selector("#ed-motiv", "s => s.value") == ""
    pg.click("#ed-save")
    pg.wait_for_selector('.msg-eroare[data-camp="ed-motiv"]', timeout=20000)
    patron.captura("motiv_cerut")
    assert sql('SELECT scutit_contrib_minim, motiv_exceptare FROM "%s".salariati WHERE id = %%s' % s, (sid,)) == [(False, None)]
    pg.click(".alegere-butoane:has(+ #ed-motiv) button[data-valoare='5']")
    pg.click("#ed-save")
    pg.wait_for_function("() => document.body.innerText.includes('Corectura scutirii intră')", timeout=30000)
    # mesajul întreg: salariatul, consecința și efectul în D112 (firma nouă n-are nicio D112 depusă) — în fereastra salariatului
    assert pg.inner_text("#ss-msg").strip() == (
        "CORECTAT ANA: datele de calcul s-au salvat; statul se calculează cu ele. Corectura scutirii intră în statul de plată și în D112 "
        "calculate de acum înainte. Fluturașii deja emiși rămân cum au fost tipăriți."), pg.inner_text("#ss-msg")
    patron.captura("salvat_efect_d112")
    assert sql('SELECT scutit_contrib_minim, motiv_exceptare FROM "%s".salariati WHERE id = %%s' % s, (sid,)) == [(True, 5)]
    assert sql('SELECT camp, valoare_veche, valoare_noua, user_id FROM "%s".salariati_jurnal WHERE salariat_id = %%s ORDER BY id' % s,
               (sid,)) == [("scutit_contrib_minim", "false", "true", uid[0]), ("motiv_exceptare", None, "5", uid[0])]
    _deschide_corectarea(pg, sid)
    pg.wait_for_selector("#ed-jurnal-tabel", timeout=20000)
    assert pg.eval_on_selector("#ed-scutit", "s => s.value") == "true" and pg.eval_on_selector("#ed-motiv", "s => s.value") == "5"
    # rândurile tabelului, celulă cu celulă (cel mai nou primul; aceeași salvare -> ordinea scrierii, inversă): când, cine, câmp, vechi, nou
    randuri = pg.eval_on_selector_all("#ed-jurnal-tabel tbody tr", "rs => rs.map(r => [...r.cells].map(c => c.innerText.trim()))")
    assert [r[1:] for r in randuri] == [
        [uid[1], "Motivul scutirii", "\u2014", "are două sau mai multe contracte, cu baza cumulată cel puțin salariul minim"],
        [uid[1], "Scutit de contribuția minimă", "Nu", "Da"]], randuri
    assert all(re.fullmatch(r"\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}", r[0]) for r in randuri), randuri
    patron.captura("jurnalul_corecturilor")
    # refuzul serverului, pe câmpul motivului: „Scutit” = Da cu motivul golit
    r = _api(patron, "PUT", "/tenants/%s/salariati/%s" % (f["tenant_id"], sid), {"scutit_contrib_minim": True, "motiv_exceptare": None})
    assert r["status"] == 422 and [e["camp"] for e in (r["json"].get("detail") or {}).get("erori_campuri", [])] == ["motiv_exceptare"], r
    assert sql('SELECT scutit_contrib_minim, motiv_exceptare FROM "%s".salariati WHERE id = %%s' % s, (sid,)) == [(True, 5)]
