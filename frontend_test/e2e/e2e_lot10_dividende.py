# -*- coding: utf-8 -*-
"""Lotul 10 (comanda Costin 20.10.2026, verbatim în DECIZII): 430 — dividende (Decontări asociați), 431 — D205 fără beneficiari, pct.9 —
Operațiunile speciale separate în lunare / recurente și rare.

Pașii contabilului pe aplicația din index, pe baza de TEST, pe o firmă NOUĂ a cabinetului de test (`firma_e2e`, scoasă la final), cu
rezultatul reportat preluat pe 117 (34.650,00, ca la F6) și doi asociați cu CNP-uri sintetice (cifra de control verificată cu
algoritmul din CLAUDE.md: 1800101400016, 2850202400023)."""
import pytest

from conftest import alege_perioada, alege_tipul, sql

_AN = 2026          # scenariul comenzii (F6, dividend anual 2026, impozit 16%)
# D205 se generează numai pe un an ÎNCHEIAT (383, comanda 10.2 pct.1: „O declarație pe o perioadă neîncheiată se refuză la generare”):
# testele 431 pun dividendul pe 2025, unde cota e 10% (Legea 141/2025: 16% pentru distribuirile de la 01.01.2026; 10% anterior)
_AN_D205 = 2025


@pytest.fixture()
def f6(firma_e2e):
    s = firma_e2e["schema"]
    sql('DELETE FROM "%s".inregistrari_linii' % s)
    sql('DELETE FROM "%s".inregistrari' % s)
    sql('DELETE FROM "%s".asociati' % s)
    # D205 cere declarantul înaintea oricărui alt refuz (R101; fără valoare implicită de la C69)
    sql('UPDATE "%s".firma_profil SET declarant_nume = %%s, declarant_prenume = %%s, declarant_functie = %%s, adresa = %%s, oras = %%s, '
        'judet = %%s WHERE id = 1' % s, ("POPESCU", "ION", "ADMINISTRATOR", "Str. Probei 431", "București", "B"))   # D205: adresa domiciliului fiscal
    sql('DELETE FROM "%s".solduri_initiale WHERE cont = %%s' % s, ("117",))
    sql('INSERT INTO "%s".solduri_initiale (cont, denumire, sold_debitor, sold_creditor, data_referinta) '
        "VALUES ('117', 'Rezultatul reportat', 0, 34650, '%d-12-31')" % (s, _AN_D205 - 1))
    return firma_e2e


def _asociati(s):
    sql('INSERT INTO "%s".asociati (nume, cnp, cota) VALUES (%%s, %%s, 60), (%%s, %%s, 40)' % s,
        ("POPESCU ION", "1800101400016", "IONESCU MARIA", "2850202400023"))


def _deschide_dividendul(e, firma, an=_AN):
    e.firma(firma["nume"])
    e.pg.click("#fa-operatiuni")
    e.pg.wait_for_selector("[data-op]", timeout=20000)
    e.pg.locator("button[data-op='asociati']").click()
    e.pg.wait_for_selector("#op-trimite", timeout=10000)
    e.pg.select_option("#op-operatie", "dividend")
    e.pg.fill("#op-data", "%d-05-20" % an)
    e.pg.fill("#op-brut", "10000")
    e.pg.fill("#op-numar_hotarare", "3")
    e.pg.fill("#op-data_hotarare", "%d-05-15" % an)
    e.pg.select_option("#op-interimar", "0")
    e.pg.select_option("#op-cu_plata", "false")


def test_def_430_dividendul_se_imparte_pe_asociati_din_profitul_preluat_pe_117(patron, f6):
    """430 a–f. Pașii: Operațiuni speciale -> „Decontări asociați” -> Dividend, 10.000 brut, hotărârea nr. 3 din 15.05 -> tabelul
    împărțirii apare ÎNAINTE de generare (POPESCU ION 60% 6.000,00 / 960,00 / 5.040,00; IONESCU MARIA 40% 4.000,00 / 640,00 / 3.360,00),
    cu avertismentul că profitul e pe 117 fără analitic -> „Generează nota” -> confirmarea numește nota și conturile (117 = 457
    10.000,00 lei; 457 = 446 1.600,00 lei), „Deschide nota … în Registrul jurnal” o deschide evidențiată, cu documentul „Hotărârea
    adunării generale a asociaților nr 3 din 15.05.<an>” și sursa „operațiunile speciale”."""
    s = f6["schema"]
    _asociati(s)
    pg = patron.pg
    _deschide_dividendul(patron, f6)
    pg.wait_for_selector("#op-div-tabel", timeout=15000)
    tabel = pg.inner_text("#op-div-tabel")
    assert "POPESCU ION" in tabel and "6.000,00" in tabel and "960,00" in tabel and "5.040,00" in tabel, tabel
    assert "IONESCU MARIA" in tabel and "4.000,00" in tabel and "640,00" in tabel and "3.360,00" in tabel, tabel
    assert "Impozit 16%" in tabel and "16.00" not in tabel
    assert pg.locator("#op-propunere .msg-avert", has_text="contul sintetic 117").count() == 1
    patron.captura("propunere")
    pg.click("#op-trimite")
    pg.wait_for_selector("#op-mesaj.msg-ok", timeout=20000)
    msg = pg.inner_text("#op-mesaj.msg-ok")
    assert "Notă generată" in msg and "117 = 457 10.000,00 lei; 457 = 446 1.600,00 lei" in msg, msg
    assert sql('SELECT sursa, document_ref FROM "%s".inregistrari' % s) == [
        ("operatiuni", "Hotărârea adunării generale a asociaților nr 3 din 15.05.%d" % _AN)]
    assert sql('SELECT count(*) FROM "%s".inregistrari_linii WHERE partener_nume IS NOT NULL' % s) == [(4,)]
    patron.captura("generata")
    pg.click("#op-deschide-nota")
    pg.wait_for_selector(".val-evidentiat", timeout=20000)
    rand = pg.inner_text(".val-evidentiat")
    assert "Hotărârea adunării generale a asociaților nr 3" in rand and "operațiunile speciale" in rand, rand
    assert "facturile" not in rand
    patron.captura("jurnal")


def test_def_430_peste_profit_si_fara_asociati_refuza_cu_trimitere(patron, f6):
    """430 a+b. Fără asociați: propunerea spune unde se adaugă (Date firmă → Asociați), cu butonul „Deschide Date firmă”. Cu asociați, un
    dividend de 40.000 peste profitul de 34.650 se refuză lângă câmpul „Dividend brut”, cu temeiul (Legea 31/1990 art.67 alin.(3))."""
    pg = patron.pg
    _deschide_dividendul(patron, f6)
    pg.wait_for_selector("#op-propunere .msg-avert", timeout=15000)
    assert "Date firmă → Asociați" in pg.inner_text("#op-propunere .msg-avert")
    pg.wait_for_selector("#op-propunere [data-ecran-destinatie='date_firma']", timeout=10000)
    patron.captura("fara_asociati")
    _asociati(f6["schema"])
    pg.fill("#op-brut", "40000")
    pg.click("#op-trimite")
    pg.wait_for_selector(".msg-eroare[data-camp='op-brut']", timeout=15000)
    assert "depășește profitul nerepartizat" in pg.inner_text(".msg-eroare[data-camp='op-brut']")
    assert sql('SELECT count(*) FROM "%s".inregistrari' % f6["schema"]) == [(0,)]
    patron.captura("peste_profit")


def test_def_431_d205_spune_ca_nota_de_dividende_e_ciorna(patron, f6):
    """431. Pașii: nota de dividende generată (ciornă) -> Declarații -> D205 pe anul încheiat: refuzul spune „nota de dividende din 20.05.<an>
    (10.000,00 lei) e ciornă” și trimite la Registrul jurnal — nu „D205 fără niciun beneficiar de venit” sec."""
    _asociati(f6["schema"])
    pg = patron.pg
    _deschide_dividendul(patron, f6, _AN_D205)
    pg.click("#op-trimite")
    pg.wait_for_selector("#op-mesaj.msg-ok", timeout=20000)
    patron.firma(f6["nume"])
    pg.click("#fa-declaratii")
    pg.wait_for_selector("#dec-tip", timeout=20000)
    alege_tipul(pg, "d205")
    pg.wait_for_selector("#dec-an", timeout=10000)
    alege_perioada(pg, _AN_D205)
    pg.click("#dec-continua")
    pg.wait_for_selector(".fereastra:last-of-type .dec-eroare, .fereastra:last-of-type details.dec-xml", timeout=90000)
    corp = patron.fereastra()
    patron.captura("refuz")
    assert "nota de dividende din 20.05.%d (10.000,00 lei) e ciornă" % _AN_D205 in corp and "valideaz-o în Registrul jurnal" in corp, corp[:600]
    patron.captura()
    # [431] „mesajul de refuz trimite la ce lipsește”: sub refuz, butonul spre nota în ciornă (`RefuzGenerare.note`), care deschide
    # Registrul jurnal în luna ei. MUTAȚIA (sesiunea principală): în core/d205.py `note=[{"nota_id": r["id"],` -> `note=[] and [{"nota_id": r["id"],`
    # -> ROȘU (refuzul rămâne text, fără buton).
    b = pg.locator(".dec-eroare .coada-note-refuz button[data-nota]")
    assert b.count() == 1 and "20.05.%d" % _AN_D205 in b.inner_text(), pg.inner_text(".dec-eroare")
    b.click()
    pg.wait_for_function("() => [...document.querySelectorAll('.fereastra')].pop().innerText.includes('Registru')", timeout=20000)
    patron.captura("nota")


def test_def_pct9_operatiunile_lunare_sunt_separate_de_cele_rare(patron, f6):
    """Pct.9. Pașii: Operațiuni speciale. Ecranul are două grupuri: „Lunare și recurente” (TVA la încasare, valută, avansuri — fiecare
    propusă cu „se propune automat: …” unde aplicația o propune) și „Rare” (lichidare, reevaluare imobilizări)."""
    pg = patron.pg
    patron.firma(f6["nume"])
    pg.click("#fa-operatiuni")
    pg.wait_for_selector("[data-op]", timeout=20000)
    lunare, rare = pg.locator(".op-grup[data-frecventa='lunar']"), pg.locator(".op-grup[data-frecventa='rar']")
    for ch in ("tva_incasare", "reeval_valuta", "avans"):
        assert lunare.locator("button[data-op='%s']" % ch).count() == 1, ch
        assert lunare.locator("[data-propune='%s']" % ch).count() == 1, ch
    for ch in ("lichidare", "reevaluare"):
        assert rare.locator("button[data-op='%s']" % ch).count() == 1, ch
    assert "se propune automat" in pg.inner_text("[data-propune='tva_incasare']")
    patron.captura(intreaga=True)


def test_def_431_d205_cuprinde_dividendele_neplatite_la_31_12(patron, f6):
    """431, decizia Costin A (verbatim în DECIZII „Lotul 10: deciziile lui Costin la întrebările din lot”): „D205 include și dividendele
    distribuite neplătite la 31.12, pe anul distribuirii, cu impozitul datorat”. Pașii: nota de dividende de 10.000 cu „Dividendul se
    plătește acum: Nu” (117 = 457; 457 = 446), validată -> Declarații -> D205 pe anul încheiat -> declarația se generează (nu mai e refuzul
    „dividendele distribuite … nu sunt plătite”) -> „Vezi XML-ul generat”: POPESCU ION divid_D 6000, divid_P 0, baza1 6000, imp1 600 (10% în 2025);
    IONESCU MARIA 4000 / 0 / 4000 / 400 (OPANAF 179/2022 anexa 1 cap.II pct.9: impozitul distribuitelor neplătite „se cuprinde în
    declaraţia aferentă perioadei în care s-a aprobat distribuirea dividendelor”)."""
    s = f6["schema"]
    _asociati(s)
    pg = patron.pg
    _deschide_dividendul(patron, f6, _AN_D205)
    pg.click("#op-trimite")
    pg.wait_for_selector("#op-mesaj.msg-ok", timeout=20000)
    # validarea notei (Registrul jurnal) nu e pasul probat aici: D205 preia numai notele validate (431, testul cu ciorna)
    sql('UPDATE "%s".inregistrari SET status = %%s' % s, ("validata",))
    patron.firma(f6["nume"])
    pg.click("#fa-declaratii")
    pg.wait_for_selector("#dec-tip", timeout=20000)
    alege_tipul(pg, "d205")
    pg.wait_for_selector("#dec-an", timeout=10000)
    alege_perioada(pg, _AN_D205)
    pg.click("#dec-continua")
    pg.wait_for_selector(".fereastra:last-of-type .dec-eroare, .fereastra:last-of-type details.dec-xml", timeout=90000)
    assert not pg.query_selector(".fereastra:last-of-type .dec-eroare"), patron.fereastra()[:1500]
    assert "nu sunt plătite" not in patron.fereastra()
    pg.click(".fereastra:last-of-type details.dec-xml > summary:has-text('Vezi XML-ul generat')")
    xml = pg.inner_text(".fereastra:last-of-type details.dec-xml[open] .dec-xml-pre")
    patron.captura()
    assert 'den1="POPESCU ION"' in xml and 'divid_D="6000" divid_P="0" baza1="6000" imp1="600"' in xml, xml
    assert 'den1="IONESCU MARIA"' in xml and 'divid_D="4000" divid_P="0" baza1="4000" imp1="400"' in xml, xml
