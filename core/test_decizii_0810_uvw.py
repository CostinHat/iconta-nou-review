# -*- coding: utf-8 -*-
"""GARDA mesajelor Costin 08.10.2026 (al patrulea și completările 2–3, verbatim în DECIZII 08.10.2026), pe ce nu e păzit în altă parte:

  U3  „Închiderea lunii devine card separat, «Închidere lună», în grupul Zilnic al ferestrei firmei.”
  U4  „Fereastra cu note de validat se numește «De depus». Titlul trebuie să spună ce conține.”
  U5  „Nota unei chitanțe (de ex. CHF1-1) afișează factura pe care o stinge. Detaliul notei are direct Validează și Respinge.”
  V3  „un cont care nu e în planul legal nu se poate crea sau folosi fără avertisment.”
  V4  „«Din ce e făcută declarația» afișează «[object Object]» în coloana «linii». Trebuie să arate cont, debit/credit și sumă.”
  V5  „Un rezumat nu e avertisment.”
  W2  registrul MF: amortizarea înregistrată, diferența față de calcul cu lunile neînregistrate, durata, codul din catalog, planul
      lunar; „Închiderea lunii e blocată dacă amortizarea lunii nu e înregistrată.”
  W3  „Controalele de la închiderea lunii semnalează 581 cu sold nenul.”
  W5  „Ferestrele cu tabele (Balanță, Mijloace fixe, Declarații) se lățesc; fără derulare laterală la 1920.”
  V1  „totalurile GeneralLedgerEntries din D406 trebuie să egaleze rulajele balanței pe lună; dacă nu, «Trimite în coadă» e blocat.”
(U1 — `test_retest_0810.py`; U2 — `test_control_preluare.py`; W1 — `test_balanta_jurnal.py`; W4 — `test_drepturi_rol.py`.)

Schemă efemeră din `tenant_template.sql`, ștearsă la ieșire. Modulele JS rulează în Chromium (ca `test_buton_blocat_structura`).
"""
import datetime
import functools
import http.server
import io
import os
import re
import socketserver
import threading
from decimal import Decimal

import pytest

from core import db as _db
from core import tenant_provisioning as _tp

SCH = "efemer_decizii_0810_uvw"
_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:  # noqa: BLE001
        return False


def _js(cale):
    return io.open(os.path.join(_RAD, cale), encoding="utf-8").read()


@pytest.fixture()
def conn():
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tp.parametrizeaza_template(_js("tenant_template.sql"), SCH))
            cur.execute("INSERT INTO %s.firma_profil (id, nume, cui, platitor_tva) VALUES (1, 'UVW SRL', 'RO14399840', true)" % SCH)
        c.commit()
    try:
        with _db.get_conn(SCH) as c:
            yield c
    finally:
        with _db.get_conn() as c:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            c.commit()


def _nota(cur, data, linii, status="validata"):
    cur.execute("INSERT INTO inregistrari (data, numar, descriere, status, sursa) VALUES (%s, 'UVW', 'proba', %s, 'manual') RETURNING id",
                (data, status))
    iid = cur.fetchone()[0]
    for d, c, s in linii:
        cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, %s, %s, %s)",
                    (iid, d, c, s))
    return iid


# ── V1 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d406_intra_in_coada_numai_cand_GL_e_rulajul_balantei(conn):
    """Completarea 2, pct.1: „totalurile GeneralLedgerEntries din D406 trebuie să egaleze rulajele balanței pe lună; dacă nu, «Trimite
    în coadă» e blocat.” Balanța arată și ciornele; D406 numai notele validate -> ciorna din lună blochează, cu numărul ei."""
    import types
    from core import uc_coada as uq
    with conn.cursor() as cur:
        cur.execute("UPDATE firma_profil SET tip_decont = 'L'")
        _nota(cur, "2099-09-20", [("5311", "704", 70)])                    # altă lună: în afara ferestrei
        _nota(cur, "2099-10-05", [("4111", "704", 100)])
        ciorna = _nota(cur, "2099-10-06", [("5121", "4111", 50)], status="ciorna")
    conn.commit()
    res = lambda *sume: types.SimpleNamespace(note=[types.SimpleNamespace(linii=[types.SimpleNamespace(debit=Decimal(x), credit=0)])
                                                    for x in sume])
    r = uq.poarta_d406_balanta(SCH, 2099, 10, res(100))
    assert (r["cod"], r["d406"], r["balanta"], r["diferenta"], r["ciorne"]) == ("D406_DIFERA_DE_BALANTA", "100.00", "150.00",
                                                                                "-50.00", 1)
    with conn.cursor() as cur:
        cur.execute("UPDATE inregistrari SET status = 'validata' WHERE id = %s", (ciorna,))
    conn.commit()
    assert uq.poarta_d406_balanta(SCH, 2099, 10, res(100, 50)) is None


def test_coada_cere_poarta_d406(monkeypatch):
    import types
    from core import uc_coada as uq, uc_comun, declaratii_api, erori
    monkeypatch.setattr(uc_comun, "_are_permisiune", lambda ctx, p: True)
    monkeypatch.setattr(uc_comun, "_schema_sau_404", lambda ctx, tid: "tenant_x")
    monkeypatch.setattr(declaratii_api, "genereaza", lambda c, s, tip, body: ("<x/>", types.SimpleNamespace(note=[], avertismente=[])))
    monkeypatch.setattr(uq.db, "get_conn", lambda schema=None: __import__("contextlib").nullcontext(None))
    monkeypatch.setattr(uq, "poarta_d406_balanta", lambda s, an, luna, res: {"cod": uq.COD_D406_BALANTA, "mesaj": "m"})
    d = types.SimpleNamespace(tip="d406", tenant_id=1, an=2099, luna=10, trim=None, motiv_trecere=None,
                              model_dump=lambda **k: {"tip": "d406", "an": 2099, "luna": 10})
    with pytest.raises(erori.DateInvalide) as e:
        uq.coada_adauga(d, {"uid": 1, "firm": 1})
    assert e.value.detaliu["cod"] == "D406_DIFERA_DE_BALANTA"


# ── V3 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_contul_din_afara_planului_legal_se_numeste_si_se_avertizeaza(conn):
    from core import jurnal_api, plan_legal
    with conn.cursor() as cur:
        # OMFP 1802/2014 (norma A): 731 (venituri ONG, OMFP 3103/2017) nu e în nomenclatorul validatorului; 4111 și 5311.01 sunt
        assert plan_legal.in_afara(cur, SCH, ["731", "4111", "5311.01", "7311"]) == ["731", "7311"]
        av = plan_legal.avertisment(cur, SCH, ["4111", "731"])
        assert av["cod"] == plan_legal.COD and av["conturi"] == ["731"] and "731" in av["motiv"]
        assert plan_legal.avertisment(cur, SCH, ["4111", "704"]) is None
    r = jurnal_api.creeaza(conn, SCH, "proba V3", "2099-10-05", [{"debit": "5311", "credit": "731", "suma": 10}])
    assert r["avertisment"]["conturi"] == ["731"]
    r2 = jurnal_api.creeaza(conn, SCH, "proba V3", "2099-10-05", [{"debit": "5311", "credit": "704", "suma": 10}])
    assert "avertisment" not in r2


# ── V5 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_rezumatul_declaratiei_nu_sta_in_avertismente():
    """CLASA: orice declarație care își sintetizează cifrele o face pe `sinteza`, nu pe `avertismente`. Se caută în surse
    forma rezumatului („Dxxx …: N …”) scrisă pe canalul avertismentelor."""
    rau = []
    for f in sorted(os.listdir(os.path.join(_RAD, "core"))):
        if not re.match(r"^d\d{3}\.py$", f):
            continue
        for n, linie in enumerate(_js("core/" + f).splitlines(), 1):
            if re.search(r'(avertismente|\bav|\bavert)\.(append|insert)\(\s*(\d+,\s*)?"D\d{3}( v%s| %d/%d| %02d/%d)?: %d ', linie):
                rau.append("%s:%d" % (f, n))
    assert not rau, rau
    from core import d112, d301, d394, d406
    assert all({"sinteza"} <= set(m.__dataclass_fields__) for m in (d112.RezultatD112, d301.Rezultat, d394.Rezultat, d406.Rezultat))


# ── U5 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_nota_chitantei_spune_ce_factura_stinge(conn):
    from core import jurnal_api
    with conn.cursor() as cur:
        cur.execute("INSERT INTO facturi (numar, data_emitere, tip, serie, directie, total) VALUES ('3', '2099-10-02', 'factura', "
                    "'F1A', 'emisa', 242) RETURNING id")
        fid = cur.fetchone()[0]
        iid = _nota(cur, "2099-10-03", [("5311", "4111", 242)])
        alta = _nota(cur, "2099-10-03", [("5311", "4111", 10)])
        cur.execute("INSERT INTO chitante (serie, numar, data, factura_id, suma, inregistrare_id, anulata) VALUES "
                    "('CHF1', 1, '2099-10-03', %s, 242, %s, false)", (fid, iid))
        st = jurnal_api.facturi_stinse(cur, SCH, [iid, alta])
    assert st == {iid: "factura F1A3 din 02.10.2099"}, st


# ── W2 + W3 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture()
def cu_mf(conn):
    """MF-001: 12.000 lei, 60 de luni, PIF 15.01.2099 (rata 200/lună din 02.2099); 2813 cu sold inițial 200 în `solduri_initiale`
    (sursa balanței; `plan_conturi` rămâne 0, ca pe F2) — amortizarea lui 02.2099, preluată; amortizare VALIDATĂ pe 03.2099, iar pe
    04 numai o ciornă."""
    with conn.cursor() as cur:
        cur.execute("INSERT INTO mijloace_fixe (cod, denumire, cont_imobilizare, cont_amortizare, valoare, rezidual, dnf_luni, data_pif, "
                    "metoda, activ) VALUES ('MF-001', 'Utilaj', '2131', '2813', 12000, 0, 60, '2099-01-15', 'liniar', true)")
        cur.execute("INSERT INTO solduri_initiale (cont, denumire, sold_debitor, sold_creditor) VALUES ('2813', 'Amortizare', 0, 200)")
        _nota(cur, "2099-03-31", [("6811", "2813", 200)])
        _nota(cur, "2099-04-30", [("6811", "2813", 200)], status="ciorna")   # propunere, nu înregistrare
    conn.commit()
    return conn


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_registrul_arata_amortizarea_inregistrata_si_lunile_lipsa(cu_mf):
    from core import mf_registru, repo_mijloace_fixe
    with cu_mf.cursor() as cur:
        r = mf_registru.registru(cur, repo_mijloace_fixe.toate(cur), azi=datetime.date(2099, 6, 10))[0]
    # decizia W2: „registrul afișează amortizarea înregistrată în contabilitate, iar separat diferența față de calculul teoretic”
    assert Decimal(r["inregistrat"]) == 400                           # 200 inițial (solduri_initiale) + 200 validat; ciorna nu
    assert Decimal(r["amortizat_teoretic"]) - Decimal(r["inregistrat"]) == Decimal(r["diferenta"]) > 0
    assert r["luni_neinregistrate"] == ["04/2099", "05/2099"]          # iunie e luna curentă, nu „lipsă”
    assert r["durata_luni"] == 60 and len(r["plan_lunar"]) == 60
    # soldul preluat stinge lunile cele mai vechi (02.2099): nu e „neînregistrată” (pe F2: 2.200 = 02–12.2025)
    assert [p["stare"] for p in r["plan_lunar"][:6]] == ["sold_initial", "inregistrata", "neinregistrata", "neinregistrata",
                                                          "in_curs", "viitoare"]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_codul_din_catalog_e_cel_din_HG_2139_2004():
    from core import mf_registru
    cat = mf_registru.catalog()
    assert len(cat) > 400 and {"2.1.17.2.1"} <= set(cat)               # HG 2139/2004, codurile cu plajă de durată
    assert mf_registru.verifica_cod("9.9.9", 60)[0] is not None
    refuz, av = mf_registru.verifica_cod("2.1.17.2.1", 60)
    assert refuz is None


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_inchiderea_lunii_cere_amortizarea_lunii_si_semnaleaza_581(cu_mf):
    from core import uc_comun
    with cu_mf.cursor() as cur:
        _nota(cur, "2099-04-20", [("581", "5311", 1000)])              # ridicare din casă, fără depunerea în bancă
    cu_mf.commit()
    c = uc_comun.controale_inchidere(cu_mf, SCH, 2099, 4)
    # W2: „Închiderea lunii e blocată dacă amortizarea lunii nu e înregistrată.”
    # (ciorna amortizării din aprilie blochează ca ciornă și NU ține loc de amortizare înregistrată)
    assert [b["cod"] for b in c["blocaje"]] == ["CIORNE", "AMORTIZARE_NEINREGISTRATA"] and c["blocaje"][1]["cont"] == "2813"
    # W3: „Controalele de la închiderea lunii semnalează 581 cu sold nenul.”
    assert [(s["cod"], Decimal(s["sold"])) for s in c["semnale"]] == [("SOLD_581", 1000)]
    c3 = uc_comun.controale_inchidere(cu_mf, SCH, 2099, 3)
    assert c3["blocaje"] == [] and c3["semnale"] == []
    assert uc_comun.controale_inchidere(cu_mf, SCH, 2099, 2)["blocaje"] == []   # amortizarea lui 02 e în soldul preluat


# ── U3 + W5 (structură) ──────────────────────────────────────────────────────────────────────────────────────────────────────
def test_inchiderea_lunii_are_cardul_ei_in_grupul_zilnic():
    firme = _js("static/js/ecrane/firme.js")
    m = re.search(r'\{ cheie: "inchidere", regim: "[a-z]+", grup: "([a-z]+)", titlu: "([^"]+)"', firme)
    assert m and m.group(1) == "zilnic" and m.group(2) == "\\u00cenchidere lun\\u0103", m and m.groups()
    # cardul deschide ecranul închiderii (cu controalele lunii, aceleași ca poarta)
    assert re.search(r'bInchidere\.addEventListener\("click", \(\) => \{ nav\.deschide\("Închidere lună", \(c2\) => ecranInchidereLuna\(', firme)


def test_ferestrele_cu_tabele_se_latesc():
    """W5: Balanța, Mijloacele fixe și Declarațiile se deschid cu `lat: "tabel"` -> `.fer-tabel` (DS cap.9)."""
    firme = _js("static/js/ecrane/firme.js") + _js("static/js/ecrane/asistent.js")
    for titlu in ("Balanță de verificare", "Mijloace fixe", "Declara(?:ț|\\\\u021b)ii"):
        deschideri = re.findall(r'nav\.deschide\("%s"[^\n]*' % titlu, firme)
        assert deschideri and [bool(re.search(r'\{ lat: "tabel" \}', d)) for d in deschideri] == [True] * len(deschideri), (titlu, deschideri)
    assert re.search(r"\.fereastra\.fer-tabel\s*\{[^}]*max-width:\s*calc\(100vw", _js("static/stil.css"))
    assert re.search(r'classList\.toggle\("fer-tabel"', _js("static/js/navigator.js"))


# ── V4 + U4 (modulele reale, în Chromium) ───────────────────────────────────────────────────────────────────────────────────
@pytest.fixture(scope="module")
def pg():
    from playwright.sync_api import sync_playwright
    from core.test_emitere_randuri_dinamice import _lanseaza_chromium
    srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(http.server.SimpleHTTPRequestHandler, directory=_RAD))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    pw = sync_playwright().start()
    b = _lanseaza_chromium(pw)
    if b is None:
        pw.stop(); srv.shutdown()
        pytest.fail("GARD headless nu poate rula: chromium indisponibil. NU e skip verde-fals.")
    p = b.new_page()
    p.goto("http://127.0.0.1:%d/static/" % srv.server_address[1])
    try:
        yield p
    finally:
        b.close(); pw.stop(); srv.shutdown()


def test_liniile_unei_note_se_arata_cont_parte_suma_nu_object_object(pg):
    r = pg.evaluate("""async () => {
      const m = await import('/static/js/ecrane/declaratii.js');
      const html = m._blocComponente({ acoperire: "completa", total: 1, sectiuni: [{ nume: "Note D406", total: 1, aratate: 1, monetare: [],
        randuri: [{ nota: "N1", linii: [{ cont: "4111", debit: 100, credit: 0 }, { cont: "704", debit: 0, credit: 100 }] }] }] });
      const d = document.createElement("div"); d.innerHTML = html;
      const col = [...d.querySelectorAll("thead th")].map((th) => th.innerText).indexOf("linii");
      const celule = [...d.querySelectorAll("tbody tr")].map((tr) => tr.children[col].innerHTML);
      return { celule, unu: m.celulaObiect({ cont: "5311", debit: 0, credit: 55 }), alt: m.celulaObiect({ a: 1 }) };
    }""")
    # celula coloanei „linii”, rând cu rând: cont · parte sumă (niciun obiect prin String())
    assert r["celule"] == ["4111 · debit 100,00<br>704 · credit 100,00"], r["celule"]
    assert r["unu"] == "5311 · credit 55,00" and r["alt"] == "a: 1"


def test_titlul_cozii_spune_ce_contine(pg):
    r = pg.evaluate("""async () => {
      const { titluCoada } = await import('/static/js/ecrane/validat.js');
      return [titluCoada({ note: 2 }), titluCoada({ note: 1, deDepus: 3 }), titluCoada({ deValidat: 1 }), titluCoada({})];
    }""")
    # U4: „Fereastra cu note de validat se numește «De depus». Titlul trebuie să spună ce conține.”
    assert r == ["Note de validat", "Note de validat · Declarații de depus", "Declarații de validat", "Coada de validare și depunere"]
