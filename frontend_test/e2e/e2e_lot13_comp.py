# -*- coding: utf-8 -*-
"""Lotul 13 (comanda Costin 13.1), zona `comp`: deficiența 536 — centrul de cost pe tot ce se contează automat.

Verbatim: „Centre de cost | Centrul se pune doar pe notele manuale; tot ce se contează automat (facturi, NIR, salarii, amortizare) iese
«nealocat» — pe F2: Producție 0, nealocat cheltuieli 1.900 / venituri 5.000. Centrul se poate pune pe liniile facturilor, NIR-urilor,
salariilor și pe mijloacele fixe (amortizarea moștenește centrul activului). Adăugarea și raportul funcționează.”

Testul reface pașii contabilului pe o firmă NOUĂ (`firma_noua`, scoasă la final), pregătită pe drumul ecranelor (`pregateste_firma`), și
verifică ecranul ȘI cifrele din bază; lasă capturi. Datele de PORNIRE care nu sunt ale pasului probat se scriu direct (declarat, pe rând):
mijlocul fix din registru. Mutațiile care îl fac ROȘU: `mut_lot13_comp.json`."""
import pytest

from conftest import firma_noua, sql
from e2e_bloc_a import AZI, ARTICOL, CLIENT, PRODUS, _api, _card, _deschide_emiterea, _ok, articol_in_stoc, pregateste_firma

_F = ".fereastra:last-of-type "
CENTRU = "Producție E2E 536"


def _cnp(baza12):
    """CNP de test cu cifra de control verificată (algoritmul oficial, CLAUDE.md)."""
    ch = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]
    s = sum(int(baza12[i]) * ch[i] for i in range(12)) % 11
    return baza12 + str(1 if s == 10 else s)


@pytest.fixture()
def firma_comp(patron):
    for f in firma_noua():
        pregateste_firma(patron, f, regim_fiscal="profit")
        yield f


def _luna_incheiata():
    """Ultima lună încheiată față de azi (amortizarea se generează numai pe lunile încheiate)."""
    return (AZI.year, AZI.month - 1) if AZI.month > 1 else (AZI.year - 1, 12)


def test_def_536_centrul_pe_factura_salariat_si_mijloc_fix_ajunge_in_raport(patron, firma_comp):
    """536. Pașii contabilului: Centre de cost -> scrie „Producție E2E 536” -> Adaugă; „Salariați și mijloace fixe” -> fereastra nouă:
    salariatul și strungul primesc centrul -> „Salvează alocarea” („Alocarea s-a salvat (2 rânduri schimbate)”); Facturi -> Emite factură:
    linia de consultanță (150 lei) pe centrul nou -> Emite; amortizarea lunii încheiate (generată de aplicație) -> rândul 6811 poartă
    centrul strungului; după validarea notelor, Centre de cost -> „Vezi realizat”: centrul are venituri 150,00 și cheltuieli 100,00
    (amortizarea 6.000 / 60 luni), iar „Nealocat (fără centru)” nu mai apare. Înainte: centrul se putea pune numai pe notele manuale,
    iar factura și amortizarea ieșeau „nealocat”."""
    f, pg = firma_comp, patron.pg
    s, tid = f["schema"], f["tenant_id"]
    # 1. centrul, din ecranul lui
    patron.firma(f["nume"])
    _card(patron, "centrecost", "#cc-nume")
    pg.fill("#cc-nume", CENTRU)
    pg.click("#cc-add")
    pg.wait_for_selector(_F + ".pf-frand-nume:has-text('%s')" % CENTRU, timeout=20000)
    (cid,) = sql('SELECT id FROM "%s".centre_cost WHERE nume = %%s' % s, (CENTRU,))[0]
    # 2. salariatul (pe drumul ecranului „Salariat nou”) și mijlocul fix
    sal = _ok(_api(patron, "POST", "/tenants/%d/salariati" % tid,
                   {"nume": "Ionescu", "prenume": "Vasile", "cnp": _cnp("185010140001"), "data_angajare": "2026-01-05",
                    "tip_norma": "intreaga", "ore_zi": 8, "salariu_brut": 6000, "persoane_intretinere": 0, "scutit_contrib_minim": False,
                    "functie_baza": True, "cor": "331302"}), "salariatul")
    sid = sal.get("id") or sal.get("salariat_id")
    from decimal import Decimal
    from core import db, repo_mijloace_fixe
    with db.get_conn(s) as c:
        with c.cursor() as cur:
            # date-de-pornire: mijlocul fix în registru, pe scrierea din care îl adaugă aplicația (Mijloace fixe / migrare)
            (mid,) = repo_mijloace_fixe.adauga_cu_reevaluare(cur, s, "MF-536", "Strung E2E 536", "2131", "2813", Decimal("6000"), Decimal(0),
                                                            60, "2026-01-15", "liniara")[:1]
        c.commit()
    # 3. alocarea, în fereastra nouă din Centre de cost
    pg.click("#cc-alocari")
    pg.wait_for_selector("#cc-aloc-salveaza", timeout=20000)
    pg.select_option("#cc-sal-%d" % sid, str(cid))
    pg.select_option("#cc-mf-%d" % mid, str(cid))
    pg.click("#cc-aloc-salveaza")
    pg.wait_for_selector("#cc-aloc-mesaj:has-text('Alocarea s-a salvat')", timeout=20000)
    assert "2 rânduri schimbate" in " ".join(pg.inner_text("#cc-aloc-mesaj").split())
    patron.captura("alocarea")
    assert sql('SELECT centru_cost_id FROM "%s".salariati WHERE id = %%s' % s, (sid,)) == [(cid,)]
    assert sql('SELECT centru_cost_id FROM "%s".mijloace_fixe WHERE id = %%s' % s, (mid,)) == [(cid,)]
    # 4. factura emisă cu centrul pe linie
    _deschide_emiterea(patron, f["nume"])
    for sel, v in CLIENT.items():
        pg.fill(sel, v)
    pg.fill("#em-l0-descriere", PRODUS)
    pg.wait_for_function("() => document.querySelector('#em-l0-pret_unitar').value !== ''", timeout=20000)
    pg.fill("#em-l0-cantitate", "1")
    pg.wait_for_selector("#em-l0-centru", timeout=10000)
    pg.select_option("#em-l0-centru", str(cid))
    patron.captura("linia_cu_centru")
    with pg.expect_response(lambda r: r.url.endswith("/facturi/emite"), timeout=60000) as rr:
        pg.click("#em-emite")
    fid = rr.value.json()["factura_id"]
    pg.wait_for_selector("#em-rezultat.em-bun", timeout=20000)
    assert sql('SELECT centru_cost_id FROM "%s".factura_linii WHERE factura_id = %%s' % s, (fid,)) == [(cid,)]
    venit = sql('SELECT l.suma::text, l.centru_cost_id FROM "%s".inregistrari_linii l JOIN "%s".inregistrari i ON i.id = l.inregistrare_id '
                "WHERE i.factura_id = %%s AND l.cont_credit LIKE '70%%%%'" % (s, s), (fid,))
    assert venit == [("150.00", cid)], venit
    # 5. amortizarea lunii încheiate, generată de aplicație: rândul 6811 moștenește centrul strungului
    an, luna = _luna_incheiata()
    _ok(_api(patron, "POST", "/tenants/%d/amortizare?an=%d&luna=%d" % (tid, an, luna), {}), "amortizarea lunii")
    am = sql('SELECT l.suma::text, l.centru_cost_id FROM "%s".inregistrari_linii l JOIN "%s".inregistrari i ON i.id = l.inregistrare_id '
             "WHERE i.numar = %%s AND l.cont_debit = '6811'" % (s, s), ("AMORT-%d-%02d" % (an, luna),))
    assert am == [("100.00", cid)], am
    # 6. notele validate (din Registrul jurnal, pe ruta butonului „Validează”) -> raportul pe centre
    for (nid,) in sql('SELECT id FROM "%s".inregistrari WHERE status <> \'validata\' AND (factura_id = %%s OR numar = %%s) ORDER BY id' % s,
                      (fid, "AMORT-%d-%02d" % (an, luna))):
        _ok(_api(patron, "POST", "/tenants/%d/jurnal/%d/valideaza" % (tid, nid), {}), "validarea notei")
    patron.firma(f["nume"])
    _card(patron, "centrecost", "#cc-raport")
    pg.fill("#cc-de", "%d-01-01" % an)   # anul lunii amortizate (în ianuarie, anul trecut)
    pg.fill("#cc-pana", AZI.isoformat())
    pg.click("#cc-raport")
    pg.wait_for_selector("#cc-raport-zona .pf-frand", timeout=20000)
    rap = " ".join(pg.inner_text("#cc-raport-zona").split())
    patron.captura("raport")
    assert "%s cheltuieli 100,00 · venituri 150,00" % CENTRU in rap and "Nealocat" not in rap, rap


def test_def_536_iesirea_din_stoc_mosteneste_centrul_articolului(patron, firma_comp):
    """536 / NIR — decizia Costin, varianta (a): „centrul pe articol sau pe gestiune, ieșirea din stoc îl moștenește”. NIR-ul scrie numai
    stoc / TVA / furnizor, deci centrul se vede la ieșire. Pașii contabilului: firma cu stocul la cost (Date firmă), marfa intrată în
    fișa de magazie; Centre de cost -> centrul nou -> „Salariați, mijloace fixe, articole” -> articolul pe centru -> „Salvează alocarea”;
    ieșirea din stoc (ruta din „Mișcări, fișe de magazie”) -> rândul 607 = 371 al notei poartă centrul articolului. Înainte: ieșirea ieșea
    „nealocat”, iar centrul de pe NIR n-ar fi avut unde să apară."""
    f, pg = firma_comp, patron.pg
    s, tid = f["schema"], f["tenant_id"]
    _ok(_api(patron, "POST", "/tenants/%d/firma-profil/date" % tid, {"metoda_stoc": "cantitativ_valoric"}), "metoda de stoc (Date firmă)")
    aid = articol_in_stoc(patron, f)
    patron.firma(f["nume"])
    _card(patron, "centrecost", "#cc-nume")
    pg.fill("#cc-nume", CENTRU)
    pg.click("#cc-add")
    pg.wait_for_selector(_F + ".pf-frand-nume:has-text('%s')" % CENTRU, timeout=20000)
    (cid,) = sql('SELECT id FROM "%s".centre_cost WHERE nume = %%s' % s, (CENTRU,))[0]
    pg.click("#cc-alocari")
    pg.wait_for_selector("#cc-art-%d" % aid, timeout=20000)
    assert ARTICOL in " ".join(pg.inner_text(_F + ".fereastra-corp").split())
    pg.select_option("#cc-art-%d" % aid, str(cid))
    pg.click("#cc-aloc-salveaza")
    pg.wait_for_selector("#cc-aloc-mesaj:has-text('Alocarea s-a salvat')", timeout=20000)
    patron.captura("articolul_pe_centru")
    assert sql('SELECT centru_cost_id FROM "%s".articole WHERE id = %%s' % s, (aid,)) == [(cid,)]
    r = _ok(_api(patron, "POST", "/tenants/%d/stocuri/iesire" % tid, {"articol_id": aid, "cantitate": 2, "data": AZI.isoformat(),
                                                                      "document": "Bon de consum E2E 536"}), "ieșirea din stoc")
    linii = sql('SELECT cont_debit, cont_credit, suma::text, centru_cost_id FROM "%s".inregistrari_linii WHERE inregistrare_id = %%s' % s,
                (r["inregistrare_id"],))
    assert linii == [("607", "371", "25.00", cid)], linii   # 2 × 12,50 (CMP-ul intrării), pe centrul articolului
