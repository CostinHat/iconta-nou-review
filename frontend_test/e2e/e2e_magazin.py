# -*- coding: utf-8 -*-
"""Magazinul online și emiterea la o firmă NEplătitoare de TVA — deficiențele 221–223, găsite pe 10.10.2026 de proba R193
(`core/test_r193_model_fara_conexiune.py`), probate în browser pe o firmă nouă a rulării.

Magazinul WooCommerce e ținut de un server HTTP local, pornit de test (`/wp-json/wc/v3/orders`): aplicația îl citește exact ca pe
unul real (`woocommerce.comenzi`, `requests.get`). Temei: CF art.310 alin.(10) lit.b) — cel care aplică regimul special de scutire
„nu are voie să menționeze taxa pe factură sau pe alt document”; OMFP 1802/2014 — 704 „Venituri din servicii prestate”.
"""
import datetime as _dt
import http.server
import json
import threading

import pytest

from conftest import ai_pregateste, ai_prompturi, firma_noua, sql

AZI = _dt.date.today()
COMENZI = []


class _Magazin(http.server.BaseHTTPRequestHandler):
    def do_GET(self):   # noqa: N802 — numele îl cere http.server
        corp = json.dumps(COMENZI if self.path.startswith("/wp-json/wc/v3/orders") else []).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(corp)))
        self.end_headers()
        self.wfile.write(corp)

    def log_message(self, *a):
        pass


@pytest.fixture(scope="module")
def magazin():
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _Magazin)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield "http://127.0.0.1:%d" % srv.server_address[1]
    srv.shutdown()


@pytest.fixture(scope="module")
def firma_neplatitoare():
    """O firmă nouă a rulării, neplătitoare de TVA (Date firmă + vectorul fiscal, pe drumul ecranului), cu seria facturilor."""
    from core import db, facturi_api, firma_profil_api as fp, vector_fiscal_api as vf
    gen = firma_noua()
    f = next(gen)
    uid = sql("SELECT id FROM public.users WHERE email = 'patron@prisma-cont.test'")[0][0]
    with db.get_conn(f["schema"]) as c:
        r = fp.salveaza_date(c, {"reg_com": "J40/1/2020", "caen": "6201", "adresa": "Str. Probei 1", "oras": "București",
                                 "judet": "București", "banca": "Banca Probă", "iban": "RO49AAAA1B31007593840000",
                                 "telefon": "0700000000", "declarant_nume": "Popescu", "declarant_prenume": "Ion",
                                 "declarant_functie": "Administrator", "forma_juridica": "SRL", "capital_subscris": "200",
                                 "capital_varsat": "200"}, tenant_id=f["tenant_id"], user_id=uid)
        assert r.get("ok", True) is not False, r
        r = vf.salveaza(c, "micro", False, None, False, inreg_art317=False, user_id=uid)
        assert r.get("ok", True) is not False, r
        assert facturi_api.seteaza_numerotare(c, serie="MG", numar_start=1)["ok"]
        c.commit()
    assert sql('SELECT platitor_tva FROM "%s".firma_profil WHERE id = 1' % f["schema"]) == [(False,)]
    yield f
    try:
        next(gen)
    except StopIteration:
        pass


def _sincronizeaza(e, f, magazin, comanda):
    COMENZI[:] = [comanda]
    sql('UPDATE "%s".firma_profil SET wc_url = %%s, wc_ck = \'ck_proba\', wc_cs = \'cs_proba\', wc_ultima_sinc = NULL WHERE id = 1'
        % f["schema"], (magazin,))
    e.firma(f["nume"])
    e.pg.click("#fa-magazin")
    e.pg.wait_for_selector("#wc-sinc", timeout=30000)
    e.pg.click("#wc-sinc")
    e.pg.wait_for_function("() => { const z = document.querySelector('#wc-rezultat'); return z && !z.innerText.includes('Se sincroniz'); }",
                           timeout=60000)
    return e.pg.inner_text("#wc-rezultat")


def _comanda(nr, denumire="Servicii de mentenanță site", total="250.00"):
    return {"number": nr, "date_created": AZI.isoformat() + "T10:00:00", "currency": "RON", "total": total,
            "billing": {"first_name": "Ana", "last_name": "Pop"},
            "line_items": [{"name": denumire, "quantity": 1, "total": total}]}


def test_def_221_comenzile_magazinului_devin_facturi(patron, firma_neplatitoare, magazin):
    """221. Magazin online: nicio comandă nu se importa — fiecare factură era refuzată pe codul fiscal al clientului.
    O comandă din magazin vine de la o persoană fizică fără cod fiscal: importul o declară (`tert_pf=True`), dar emiterea nu dădea
    declarația mai departe la crearea facturii, care cerea a doua oară codul și refuza. Pașii contabilului: firma cu magazinul
    configurat -> Magazin online -> „Sincronizează acum” -> „1 facturi importate”, iar factura clientului Ana Pop există, fără cod.
    MUTAȚIE: `tert_pf=tert_pf` scos din `emite_factura` -> refuzul codului fiscal -> pică."""
    f = firma_neplatitoare
    txt = _sincronizeaza(patron, f, magazin, _comanda(601))
    patron.captura("importata")
    assert "1 facturi importate" in txt, txt
    assert sql('SELECT tert_nume, tert_cui FROM "%s".facturi WHERE sursa_externa = \'WC-601\'' % f["schema"]) == [("Ana Pop", None)]


def test_def_222_factura_din_magazin_a_neplatitorului_nu_poarta_tva(patron, firma_neplatitoare, magazin):
    """222. Magazin online, firmă neplătitoare: factura importată ar fi purtat TVA.
    Importul nu dădea emiterii statutul de plătitor al firmei, deci emiterea lua implicitul „plătitoare” — iar o linie de produs nou
    primea cota 21% (CF art.310 alin.(10) lit.b): neplătitorul „nu are voie să menționeze taxa pe factură”). Pașii contabilului:
    firma neplătitoare -> Magazin online -> „Sincronizează acum” -> linia facturii are cota 0 și TVA 0.
    MUTAȚIE: `platitor_tva=platitor` scos din `woocommerce._importa` -> cota 21 -> pică."""
    f = firma_neplatitoare
    ai_pregateste('{"cota": 21, "categorie": "standard", "tip": "servicii", "justificare": "regula standard", "incredere": "mare"}')
    txt = _sincronizeaza(patron, f, magazin, _comanda(602, denumire="Servicii de găzduire web", total="300.00"))
    assert "1 facturi importate" in txt, txt
    rand = sql('SELECT l.cota_tva::int, f.tva::text FROM "%s".facturi f JOIN "%s".factura_linii l ON l.factura_id = f.id '
               "WHERE f.sursa_externa = 'WC-602'" % (f["schema"], f["schema"]))
    patron.captura("fara_tva")
    assert rand == [(0, "0.00")], rand


def test_def_223_neplatitorul_primeste_contul_de_venit_de_la_asistent(patron, firma_neplatitoare):
    """223. Emitere, firmă neplătitoare: contul de venit al unei linii fără cuvânt-cheie era refuzat cu „asistentul nu a putut
    decide”, fără ca asistentul să fi fost întrebat. Decizia 64 (22.09): regula pe cuvinte-cheie, apoi asistentul, apoi blocarea —
    la orice firmă; la neplătitor întrebarea se punea cu „neplătitor”, pe care potrivirea cotei îl scurtcircuitează la 0, fără felul
    venitului. Pașii contabilului: firma neplătitoare -> Facturi -> „Emite factură” -> client și linia „Mentenanță platformă web”
    (fără cont) -> „Emite factură” -> factura e emisă, linia are 704 (servicii), iar asistentul a fost întrebat o dată.
    MUTAȚIE: întrebarea pentru cont pusă cu statutul de plătitor (`(d, platitor_tva)`) -> refuzul -> pică."""
    from conftest import cui_cu_control
    f = firma_neplatitoare
    ai_pregateste('{"cota": 21, "categorie": "standard", "tip": "servicii", "justificare": "prestare de servicii", "incredere": "mare"}')
    pg = patron.pg
    patron.firma(f["nume"])
    pg.click("#fa-facturi")
    pg.wait_for_selector("#fac-emite", timeout=20000)
    pg.click("#fac-emite")
    pg.wait_for_selector("#em-cui, #em-nu", timeout=20000)
    pg.fill("#em-cui", cui_cu_control(30000017))
    pg.fill("#em-nume", "Client Probă E2E SRL")
    pg.fill("#em-adresa", "Str. Clientului 2, București")
    pg.fill("#em-l0-descriere", "Mentenanță platformă web")   # neplătitor: cota e 0 prin lege, ecranul nu cere propunerea
    pg.fill("#em-l0-cantitate", "1")
    pg.fill("#em-l0-pret_unitar", "500")
    pg.click("#em-emite")
    pg.wait_for_selector("#em-rezultat.em-bun, #em-rezultat.em-rau, #em-rezultat .msg-eroare", timeout=60000)
    rez = pg.inner_text("#em-rezultat")
    patron.captura("emisa")
    assert "nu se poate stabili" not in rez, rez
    linie = sql('SELECT l.cont_venit, l.cota_tva::int FROM "%s".factura_linii l JOIN "%s".facturi f ON f.id = l.factura_id '
                "WHERE l.descriere = 'Mentenanță platformă web' ORDER BY f.id DESC LIMIT 1" % (f["schema"], f["schema"]))
    assert linie == [("704", 0)], (linie, rez)
    assert len(ai_prompturi()) == 1, ai_prompturi()


def test_def_224_comanda_refuzata_nu_opreste_sincronizarea(patron, firma_neplatitoare, magazin):
    """224. Magazin online: o comandă pe care emiterea o refuză oprea sincronizarea cu „eroare 500”, iar comenzile de după ea nu se
    mai importau. Pașii contabilului: magazinul are două comenzi — 603 „Abonament platformă online” (asistentul nu răspunde, deci
    contul de venit nu se poate stabili) și 604 „Servicii de mentenanță site” -> „Sincronizează acum” -> „1 facturi importate”, iar
    sub ea: „Comanda 603 n-a devenit factură: Contul de venit … Se reîncearcă la sincronizarea următoare.” Data ultimei citiri nu
    trece peste comanda refuzată. MUTAȚIE: refuzul nu se mai prinde în `woocommerce._importa` -> „eroare 500” -> pică."""
    f = firma_neplatitoare
    ai_pregateste()                                   # asistentul nu are răspuns: nivelul 2 al contului de venit eșuează
    COMENZI[:] = [_comanda(603, denumire="Abonament platformă online", total="90.00"), _comanda(604, total="120.00")]
    sql('UPDATE "%s".firma_profil SET wc_url = %%s, wc_ck = \'ck_proba\', wc_cs = \'cs_proba\', wc_ultima_sinc = NULL WHERE id = 1'
        % f["schema"], (magazin,))
    patron.firma(f["nume"])
    patron.pg.click("#fa-magazin")
    patron.pg.wait_for_selector("#wc-sinc", timeout=30000)
    patron.pg.click("#wc-sinc")
    patron.pg.wait_for_selector("#wc-rezultat [data-comanda-refuzata='603']", timeout=60000)
    txt = patron.pg.inner_text("#wc-rezultat")
    patron.captura("refuzata_numita")
    assert "1 facturi importate" in txt and "Comanda 603 n-a devenit factură: Contul de venit" in txt, txt
    assert sql('SELECT sursa_externa FROM "%s".facturi WHERE sursa_externa IN (\'WC-603\', \'WC-604\')' % f["schema"]) == [("WC-604",)]
    assert sql('SELECT wc_ultima_sinc FROM "%s".firma_profil WHERE id = 1' % f["schema"]) == [(None,)]
