# -*- coding: utf-8 -*-
"""GARDA deciziilor Costin 08.10.2026 §6 pct.1–3 — NIR-ul „fără factură” pe 408, factura legată îl închide (verbatim în DECIZII 08.10.2026):

  pct.1 „NIR fără factură → factură, la cantitativ-valoric: aceeași alegere ca la celelalte metode — la contarea facturii se leagă de
         NIR-ul deschis (408 = 401), fără a doua intrare în stoc. Fără refuz.”
  pct.2 „NIR din exercițiul trecut: se propune la legare și între exerciții, cât timp 408 e deschis. Exercițiul închis nu se modifică;
         diferența de preț intră în perioada facturii.”
  pct.3 „TVA din NIR fără factură: 4428 până la factură, apoi 4428 → 4426 la contarea facturii (CF art.299 alin.(1) lit.a).”

TEMEI: OMFP 1802/2014, funcțiunea contului 408: „În creditul contului 408 «Furnizori - facturi nesosite» se înregistrează: – valoarea
bunurilor aprovizionate … (301, 302, 303, 361, 371, 381, 4428, …)”; pct.68 alin.(1): „Corectarea erorilor aferente exercițiilor
financiare precedente nu determină modificarea situațiilor financiare ale acelor exerciții.”; CF art.299 alin.(1) lit.a: deducerea cere
„să dețină o factură emisă în conformitate cu prevederile art. 319”.

CE FACE IMPOSIBIL:
  * a doua intrare în stoc a aceleiași mărfi la cantitativ-valoric (fișa: o intrare; `intrare_din_factura` nu mai scrie);
  * diferența de preț pierdută sau scrisă în exercițiul NIR-ului: GV 378 = 401, CV 371 = 401 + ajustare de valoare în fișă (CMP nou),
    CV cu marfa ieșită 607 = 401 — toate cu data facturii;
  * re-contarea după respingere care uită legarea și încarcă 371 a doua oară;
  * ajustarea citită ca ieșire de D406 Stocuri.

Schemă efemeră din `tenant_template.sql`, ștearsă la ieșire; date în 2098–2099. Nimic în tabele partajate.
"""
import io
from datetime import date
from decimal import Decimal

import pytest

from core import db as _db
from core import tenant_provisioning as _tp

SCH = "efemer_nir_408"
CUI = "14399840"   # CUI real, cifra de control verificată (CLAUDE.md)


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


def _lume(metoda, tvai=False):
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tp.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), SCH))
            cur.execute("INSERT INTO %s.firma_profil (id, nume, cui, platitor_tva, metoda_stoc, tva_la_incasare) "
                        "VALUES (1, 'NIR 408 SRL', 'RO14399840', true, %%s, %%s)" % SCH, (metoda, tvai))
        c.commit()


@pytest.fixture()
def lume():
    yield _lume
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        c.commit()


def _articol(conn):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO articole (denumire, um, cont_stoc, cont_cheltuiala) VALUES ('Marfa A', 'buc', '371', '607') RETURNING id")
        return cur.fetchone()[0]


def _nir(conn, articol=None, data="2099-10-07"):
    from core import stocuri_api as s
    linie = {"denumire": "Marfa A", "cantitate": 10, "pret_achizitie": 55, "cota_tva": 21}
    if articol:
        linie["articol_id"] = articol
    else:
        linie["pret_vanzare"] = 80
    r = s.adauga_nir(conn, SCH, {"numar": "1", "data": data, "furnizor": "FURNIZOR", "cui": CUI, "linii": [linie]})
    assert "eroare" not in r, r
    return r


def _factura(conn, pret=55, data="2099-10-20"):
    from core import facturi_api as fa
    return fa.creeaza_factura(conn, "FP1", data, "primita", [{"descriere": "Marfa A", "cantitate": 10, "pret_unitar": pret, "cota_tva": 21}],
                              tert_nume="FURNIZOR", tert_cui="RO" + CUI)["factura_id"]


def _conteaza(conn, fid, nir_legat=None):
    from core import contare_facturi as cf
    with cf.cursor_dict(conn) as cur:
        return cf.contabilizeaza(cur, SCH, fid, automat=False, nir_legat=nir_legat)


def _linii(r):
    return [(x["debit"], x["credit"], x["suma"]) for x in r["linii"]]


def _rulaj(conn, cont):
    with conn.cursor() as cur:
        cur.execute("SELECT COALESCE(SUM(CASE WHEN cont_debit = %s THEN suma END), 0), COALESCE(SUM(CASE WHEN cont_credit = %s THEN suma END), 0) "
                    "FROM inregistrari_linii", (cont, cont))
        return tuple(str(x) for x in cur.fetchone())


def _fisa(conn, art):
    from core import stocuri_cv_api as cv
    return [(l["tip"], l["cantitate"], l["valoare"], l["cmp"]) for l in cv.fisa(conn, SCH, art)["linii"]]


def test_cantitativ_valoric_o_singura_intrare_in_stoc(lume):
    """pct.1 „fără a doua intrare în stoc. Fără refuz.” — închide fosta datorie test_datorie_nir_fara_factura_la_cost_dubleaza_intrarea.
    MUTAȚIE: `METODE = (_ms.GV,)` în nir_legare -> factura se contează 371 = 401 peste NIR (371 D 1100) -> pică."""
    lume("cantitativ_valoric")
    with _db.get_conn(SCH) as conn:
        art = _articol(conn)
        n = _nir(conn, art)
        fid = _factura(conn)
        r = _conteaza(conn, fid, nir_legat=n["id"])
        assert _linii(r) == [("408", "401", "665.50"), ("4426", "4428.01", "115.50")]   # pct.3: 4428 -> 4426 la factură
        assert _rulaj(conn, "371") == ("550.00", "0")                                   # marfa intrată o dată
        assert _rulaj(conn, "408") == ("665.50", "665.50")                              # 408 închis
        assert _fisa(conn, art) == [("intrare", "10.000", "550.00", "55.0000")]
        from core import stocuri_cv_api as cv
        assert cv.intrare_din_factura(conn, SCH, fid, "371", "2099-10-20")["stare"] == "intrat_prin_nir"
        assert _fisa(conn, art) == [("intrare", "10.000", "550.00", "55.0000")]          # nimic în plus în fișă
        conn.rollback()


def test_cantitativ_valoric_diferenta_de_pret_in_fisa_cu_cmp_nou(lume):
    """pct.2 „diferența de preț intră în perioada facturii” — pe stoc: ajustare de valoare (cantitate 0), CMP recalculat; în contabilitate
    371 = 401 cu data facturii; TVA-ul în plus 4426 = 401. MUTAȚIE: `scrie_ajustari_cv` necheamat -> fișa rămâne la CMP 55 -> pică."""
    lume("cantitativ_valoric")
    with _db.get_conn(SCH) as conn:
        art = _articol(conn)
        n = _nir(conn, art)
        r = _conteaza(conn, _factura(conn, pret=56), nir_legat=n["id"])
        assert _linii(r) == [("408", "401", "665.50"), ("4426", "4428.01", "115.50"), ("4426", "401", "2.10"), ("371", "401", "10.00")]
        assert _fisa(conn, art)[-1] == ("ajustare", "0.000", "10.00", "56.0000")
        with conn.cursor() as cur:
            cur.execute("SELECT data FROM inregistrari WHERE id = %s", (r["inregistrare_id"],))
            assert cur.fetchone()[0] == date(2099, 10, 20)                               # perioada facturii
        conn.rollback()


def test_cantitativ_valoric_marfa_iesita_diferenta_pe_607(lume):
    """Marfa vândută înainte de factură: diferența nu mai are pe ce sta în stoc -> 607 = 401, fără ajustare în fișă. MUTAȚIE: `d_607=0`
    în contabilizeaza -> 371 = 401 10 pe stoc zero -> pică."""
    lume("cantitativ_valoric")
    with _db.get_conn(SCH) as conn:
        art = _articol(conn)
        n = _nir(conn, art)
        from core import stocuri_cv_api as cv
        assert cv.iesire(conn, SCH, {"articol_id": art, "data": "2099-10-10", "cantitate": 10}) is not None
        r = _conteaza(conn, _factura(conn, pret=56), nir_legat=n["id"])
        assert ("607", "401", "10.00") in _linii(r) and not [x for x in _linii(r) if x[0] == "371"]
        assert [x[0] for x in _fisa(conn, art)] == ["intrare", "iesire"]
        conn.rollback()


def test_global_valoric_diferenta_pe_adaos(lume):
    """GV: diferența de cost pe 378 (adaosul), cu data facturii; 371 rămâne cel din NIR."""
    lume("global_valoric")
    with _db.get_conn(SCH) as conn:
        n = _nir(conn)
        r = _conteaza(conn, _factura(conn, pret=56), nir_legat=n["id"])
        assert ("378", "401", "10.00") in _linii(r)
        assert _rulaj(conn, "371")[0] == "800.00"                                       # NIR: 550 cost + adaos + TVA neexigibil
        conn.rollback()


def test_intre_exercitii_exercitiul_inchis_nu_se_modifica(lume):
    """pct.2 „se propune la legare și între exerciții, cât timp 408 e deschis. Exercițiul închis nu se modifică” (OMFP 1802/2014 pct.68
    alin.(1)). Factura din 2099 închide NIR-ul din 2098: nicio notă nouă datată 2098. MUTAȚIE: condiția `n["forma_noua"] or` scoasă din
    `candidati` -> NIR-ul din 2098 nu e propus -> pică."""
    lume("global_valoric")
    with _db.get_conn(SCH) as conn:
        n = _nir(conn, data="2098-12-20")
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM inregistrari WHERE data < '2099-01-01'")
            in_2098 = cur.fetchone()[0]
        from core import contare_facturi as cf
        fid = _factura(conn, data="2099-01-15")
        with pytest.raises(cf.RefuzContare) as e:
            _conteaza(conn, fid)
        assert e.value.detalii["propus"] == n["id"]
        r = _conteaza(conn, fid, nir_legat=n["id"])
        assert r["nir_legat"]["forma_noua"] is True and r["nir_legat"]["stornare_id"] is None
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM inregistrari WHERE data < '2099-01-01'")
            assert cur.fetchone()[0] == in_2098
        conn.rollback()


def test_tva_la_incasare_tva_neexigibil_se_anuleaza_tva_facturii_ramane(lume):
    """La TVA la încasare factura își scrie TVA-ul pe 4428 (CF art.282); TVA-ul din NIR (4428.01) se anulează pe 408, nu trece în 4426."""
    lume("global_valoric", tvai=True)
    with _db.get_conn(SCH) as conn:
        n = _nir(conn)
        r = _conteaza(conn, _factura(conn), nir_legat=n["id"])
        assert _linii(r)[:2] == [("408", "401", "550.00"), ("408", "4428.01", "115.50")]
        assert not [x for x in _linii(r) if x[0] == "4426"]
        assert _rulaj(conn, "408") == ("665.50", "665.50") and _rulaj(conn, "4428.01") == ("115.50", "115.50")
        conn.rollback()


def test_recontarea_dupa_respingere_pastreaza_legarea(lume, monkeypatch):
    """Nota facturii respinsă la validare, apoi „Contabilizează” din nou: NIR-ul rămâne legat (alegerea s-a făcut), nota nouă închide
    același 408; ajustarea veche fără notă se înlocuiește. MUTAȚIE: ramura `deja_legat` scoasă din contabilizeaza -> nota nouă 371 = 401
    (371 D 1110) -> pică."""
    lume("cantitativ_valoric")
    with _db.get_conn(SCH) as conn:
        art = _articol(conn)
        n = _nir(conn, art)
        fid = _factura(conn, pret=56)
        r1 = _conteaza(conn, fid, nir_legat=n["id"])
        from core import note_derivate as nd
        monkeypatch.setattr(nd, "respinsa", lambda cur, schema, iid: iid == r1["inregistrare_id"])
        r2 = _conteaza(conn, fid)
        assert r2["stare"] == "contata" and r2["inregistrare_id"] != r1["inregistrare_id"]
        assert _linii(r2) == _linii(r1)
        assert _rulaj(conn, "371") == ("560.00", "0")
        assert [x[0] for x in _fisa(conn, art)] == ["intrare", "ajustare"]
        conn.rollback()


def test_d406_stocuri_ajustarea_adauga_valoare():
    """D406 Stocuri: ajustarea de valoare (cantitate 0) se adună cu semnul ei, nu se scade ca o ieșire. MUTAȚIE: `semn = 1 if tip ==
    "intrare" else -1` -> close_v 540 -> pică."""
    from core import d406_stocuri as d
    s = d.solduri([{"data": date(2099, 10, 7), "tip": "intrare", "cantitate": 10, "valoare": 550},
                   {"data": date(2099, 10, 20), "tip": "ajustare", "cantitate": 0, "valoare": 10}], date(2099, 10, 1), date(2099, 10, 31))
    assert (s["close_q"], s["close_v"], s["pret"]) == (Decimal("10.000"), Decimal("560.00"), Decimal("56.0000"))


def test_refacerea_facturii_nu_reface_ajustarea_ca_iesire(lume):
    """Respingerea facturii stornează în roșu și ajustarea ei (`stocuri_anulare.storneaza`, grupul „factura-<id>”); refacerea stocului
    facturii (`reface_factura`) nu o reface — o rescrie contarea. MUTAȚIE: filtrul `o.tip <> 'ajustare'` scos -> refacerea o ia drept
    factură emisă și descarcă stocul -> pică."""
    lume("cantitativ_valoric")
    with _db.get_conn(SCH) as conn:
        art = _articol(conn)
        n = _nir(conn, art)
        fid = _factura(conn, pret=56)
        _conteaza(conn, fid, nir_legat=n["id"])
        from core import stocuri_anulare as sa
        assert len(sa.storneaza(conn, SCH, "factura-%d" % fid, [], "proba")["stornate"]) == 1
        assert _fisa(conn, art)[-1][3] == "55.0000"                                     # CMP înapoi la prețul NIR-ului
        assert sa.reface_factura(conn, SCH, fid) is None
        assert [x[0] for x in _fisa(conn, art)] == ["intrare", "ajustare", "ajustare"]
        conn.rollback()


def test_k_nu_citeste_tva_neexigibil_al_nir_ului_fara_factura(lume):
    """pct.3: 4428.01 e TVA-ul achizițiilor fără factură, nu TVA-ul din prețul de raft. Un sold inițial pe 4428.01 (NIR fără factură
    preluat) nu schimbă coeficientul K al descărcării global-valorice. MUTAȚIE: `AND cont <> %s` scos din soldurile inițiale ale lui K
    -> K diferă -> pică."""
    lume("global_valoric")
    with _db.get_conn(SCH) as conn:
        from core import stocuri_api as s
        with conn.cursor() as cur:
            for cont, d, c in (("371", 1210, 0), ("378", 0, 400), ("4428", 0, 210)):
                cur.execute("INSERT INTO solduri_initiale (cont, sold_debitor, sold_creditor) VALUES (%s, %s, %s)", (cont, d, c))
            cur.execute("INSERT INTO inregistrari (data, descriere, sursa, status) VALUES ('2099-10-15', 'vanzare', 'facturi', 'validata') "
                        "RETURNING id")
            iid = cur.fetchone()[0]
            cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, '4111', '707', 500)", (iid,))
            cur.execute("SAVEPOINT k")
        fara = s.descarca_luna(conn, SCH, 2099, 10)
        with conn.cursor() as cur:
            cur.execute("ROLLBACK TO SAVEPOINT k")
            cur.execute("INSERT INTO solduri_initiale (cont, sold_debitor, sold_creditor) VALUES ('4428.01', 115.50, 0)")
        cu = s.descarca_luna(conn, SCH, 2099, 10)
        assert fara.get("k") and cu["k"] == fara["k"], (fara, cu)
        conn.rollback()


def test_bilant_tva_neexigibil_debitor_e_creanta():
    """Soldul debitor al lui 4428.01 (TVA-ul NIR-ului fără factură, nedeductibil încă) e creanță — OMFP 1802/2014, bilanțul
    prescurtat, rd.06 CREANȚE: „… + 4424 + din ct. 4428** + 444** …” (** = solduri debitoare). MUTAȚIE: "4428" scos din lista
    r[301] -> creanțele 0 -> pică."""
    from core import bilant as b
    r = b.f10_din_balanta({"4428.01": (Decimal("115.50"), Decimal("0")), "408": (Decimal("0"), Decimal("115.50"))})
    assert (r[301], r[13], r[5]) == (116, 116, 0)                                        # lei întregi, rotunjire aritmetică


def test_d406_analiticul_se_declara_pe_sintetic_si_trece_a_doua_cale(lume):
    """D406: 4428.01 nu e în nomenclatorul oficial (numai sintetice, anaf_surse/d406_nomenclatoare_anaf.properties), iar AccountID cu
    punct e respins („numar intreg eronat”). Analiticul se declară pe 4428 — în plan și pe linii — și a doua cale (`d406_reconciliere`)
    ajunge la aceleași rulaje. Proba pe DUK (valid, 0 erori) e în raportul §6. MUTAȚIE: `sintetic_saft` scos de pe liniile notelor ->
    ReconciliereD406 -> pică."""
    lume("global_valoric")
    with _db.get_conn(SCH) as conn:
        n = _nir(conn, data="2099-09-07")
        _conteaza(conn, _factura(conn, data="2099-09-20"), nir_legat=n["id"])
        with conn.cursor() as cur:
            cur.execute("UPDATE inregistrari SET status = 'validata'")
            cur.execute("UPDATE firma_profil SET adresa = 'Str. Proba 1', oras = 'Bucuresti', reg_com = 'J40/1/2099', tip_decont = 'L'")
        from core import d406
        xml, res = d406.genereaza(conn, SCH, 2099, 9)
        from xml.etree import ElementTree as ET
        ids = [e.text for e in ET.fromstring(xml).iter() if e.tag.rsplit("}", 1)[-1] == "AccountID"]
        assert ids and all(i.isdigit() for i in ids), ids                              # „numar intreg” — niciun punct
        strain = d406.pull(conn, SCH, 2099, 9)[8]
        assert sorted(strain) == ["731", "732", "733", "734", "736", "738"]              # 4428.01 nu e „exclus din normă”
        conts = {c.id: c for c in res.conturi}
        assert [k for k in conts if d406.sintetic_saft(k) == "4428"] == ["4428"]        # un singur cont, sinteticul
        conn.rollback()


def test_poarta_d300_compara_cu_4426_tva_din_nir_nu_e_deductibil(lume):
    """pct.3 „Poarta D300 compară cu 4426.” NIR-ul fără factură nu deduce (TVA-ul stă pe 4428.01 — CF art.299 alin.(1) lit.a cere
    factura): R27_2 = 0 = rulajul 4426. După factura legată, 4426 = 4428.01 aduce exact TVA-ul facturii: R27_2 116 ↔ 4426 115,50
    (toleranța de rotunjire). Semnalul „exigibilitate decalată” pe 4428 nu mai citește TVA-ul din prețul de raft (371 = 4428).
    MUTAȚIE: NIR-ul pe 4426 (`cont_tva` = "4426" și fără factură) -> 4426 115,50 față de R27_2 0 -> roșu -> pică."""
    lume("global_valoric")
    from core import control_incrucisat as ci
    with _db.get_conn(SCH) as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE firma_profil SET adresa = 'Str. Proba 1', oras = 'Bucuresti', judet = 'Bucuresti', caen = '4711', "
                        "banca = 'Banca Proba', iban = 'RO49AAAA1B31007593840000', tip_decont = 'L', declarant_nume = 'Popescu', "
                        "declarant_prenume = 'Ion', declarant_functie = 'Administrator'")
        n = _nir(conn, data="2099-09-07")

        def tva():
            with conn.cursor() as cur:
                cur.execute("UPDATE inregistrari SET status = 'validata'")
            v = ci.verifica_tva(conn, SCH, 2099, 9)
            c = {x.get("cont"): x for x in v["constatari"]}
            assert not [x for x in v["constatari"] if x.get("stare") == "gri"], v["constatari"]   # semnalul 4428 (gri) nu apare
            return c["4426"]["stare"], str(c["4426"]["declarat"]), str(c["4426"]["contabil"])

        assert tva() == ("verde", "0", "0")
        _conteaza(conn, _factura(conn, data="2099-09-20"), nir_legat=n["id"])
        assert tva() == ("verde", "116", "115.50")
        conn.rollback()
