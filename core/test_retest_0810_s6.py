# -*- coding: utf-8 -*-
"""GARDA lotului „Retest 08.10” (comanda Costin 08.10.2026, verbatim în DECIZII) — deciziile la §6 S6 și constatările retestului.

pct.1 „Bilanț 4428: aprob separarea — analitic propriu pentru TVA-ul din prețul de raft, cu migrarea soldurilor existente. În bilanț acesta
se scade doar din stocuri (rd.05) și nu mai apare la datorii. Închide datoria bilant_4428_creditor_numarat_de_doua_ori.”
TEMEI: OMFP 1802/2014, bilanțul prescurtat — rd.05 STOCURI „… 371 +/- 378 … - din ct. 4428”, rd.13 DATORII „… 4428*** …”.

Schemă efemeră din `tenant_template.sql`, ștearsă la ieșire; date în 2099. Nimic în tabele partajate.
"""
import io
from decimal import Decimal

import pytest

from core import db as _db
from core import tenant_provisioning as _tp

SCH = "efemer_retest_0810"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture()
def lume():
    if not _db_ok():
        pytest.skip("DB indisponibil")

    def _f(metoda="global_valoric", tvai=False):
        with _db.get_conn() as c:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
                cur.execute(_tp.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), SCH))
                cur.execute("INSERT INTO %s.firma_profil (id, nume, cui, platitor_tva, metoda_stoc, tva_la_incasare, tip_decont) "
                            "VALUES (1, 'RETEST SRL', 'RO14399840', true, %%s, %%s, 'L')" % SCH, (metoda, tvai))
            c.commit()
    yield _f
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        c.commit()


def _nota(conn, data, linii, sursa="stocuri", status="validata"):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO inregistrari (data, descriere, sursa, status, document_ref) VALUES (%s, 'n', %s, %s, 'NC n') RETURNING id",
                    (data, sursa, status))   # [09.10.2026, regulile de fond R3] nota validată are documentul justificativ
        nid = cur.fetchone()[0]
        for d, c, s in linii:
            cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, %s, %s, %s)",
                        (nid, d, c, Decimal(str(s))))
    return nid


# ── pct.1 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_pct1_bilant_tva_stoc_numai_la_stocuri():
    """Fosta datorie `test_datorie_bilant_4428_creditor_numarat_de_doua_ori`, acum pozitivă: TVA-ul din prețul de raft (4428.02) scade
    stocul și NU e și datorie; TVA-ul la încasare (4428 creditor) rămâne datorie. MUTAȚIE: `_fara_tva_stoc` scos -> rd.13 210 -> pică."""
    from core import bilant as b
    r = b.f10_din_balanta({"371": (Decimal(1210), 0), "378": (0, Decimal(400)), "4428.02": (0, Decimal(210)), "1012": (0, Decimal(600))})
    assert (r[5], r[13]) == (600, 0)
    r = b.f10_din_balanta({"371": (Decimal(1210), 0), "378": (0, Decimal(400)), "4428.02": (0, Decimal(210)),
                           "4428": (0, Decimal(50)), "1012": (0, Decimal(650))})
    assert (r[5], r[13]) == (600, 50)                                                 # 4428 sintetic: TVA la încasare -> datorie


def test_pct1_nir_si_descarcarea_gv_scriu_pe_analitic(lume):
    """NIR-ul GV scrie `371 = 4428.02`, descărcarea `4428.02 = 371`; K citește analiticul. MUTAȚIE: NIR înapoi pe 4428 -> pică."""
    from core import stocuri_api as sa
    lume()
    with _db.get_conn(SCH) as conn:
        r = sa.adauga_nir(conn, SCH, {"numar": "1", "data": "2099-10-07", "furnizor": "F", "cui": "14399840",
                                      "linii": [{"denumire": "Marfa A", "cantitate": 10, "pret_achizitie": 55, "cota_tva": 21, "pret_vanzare": 80}]})
        with conn.cursor() as cur:
            cur.execute("SELECT cont_debit, cont_credit FROM inregistrari_linii WHERE inregistrare_id = ANY(%s) ORDER BY id", (r["inregistrari"],))
            assert ("371", "4428.02") in cur.fetchall()
            cur.execute("UPDATE inregistrari SET status = 'validata'")
        _nota(conn, "2099-10-10", [("4111", "707", 500), ("4111", "4427", 105)], sursa="facturi")
        d = sa.descarca_luna(conn, SCH, 2099, 10)
        with conn.cursor() as cur:
            cur.execute("SELECT cont_debit, cont_credit FROM inregistrari_linii WHERE inregistrare_id = ANY(%s) ORDER BY id", (d["inregistrari"],))
            assert ("4428.02", "371") in cur.fetchall()
        conn.rollback()


def test_pct1_k_nu_citeste_tva_la_incasare_de_pe_sintetic(lume):
    """K = adaos / (stoc la preț de vânzare - TVA-ul STOCULUI): un sold 4428 (TVA la încasare) nu-l mai schimbă. MUTAȚIE: K pe
    `4428%` -> K diferă -> pică."""
    from core import stocuri_api as sa
    lume()
    with _db.get_conn(SCH) as conn:
        with conn.cursor() as cur:
            for cont, d, c in (("371", 1210, 0), ("378", 0, 400), ("4428.02", 0, 210)):
                cur.execute("INSERT INTO solduri_initiale (cont, sold_debitor, sold_creditor) VALUES (%s, %s, %s)", (cont, d, c))
            cur.execute("SAVEPOINT k")
        _nota(conn, "2099-10-15", [("4111", "707", 500), ("4111", "4427", 105)], sursa="facturi")
        fara = sa.descarca_luna(conn, SCH, 2099, 10)
        with conn.cursor() as cur:
            cur.execute("ROLLBACK TO SAVEPOINT k")
            cur.execute("INSERT INTO solduri_initiale (cont, sold_debitor, sold_creditor) VALUES ('4428', 0, 77)")
        _nota(conn, "2099-10-15", [("4111", "707", 500), ("4111", "4427", 105)], sursa="facturi")
        cu = sa.descarca_luna(conn, SCH, 2099, 10)
        assert fara["k"] == cu["k"] == "0.400000", (fara, cu)
        conn.rollback()


def test_pct1_migrarea_muta_numai_tva_stocului(lume):
    """Migrarea soldurilor: rândurile pe 4428 cu contrapartida 371 trec pe 4428.02; TVA-ul la încasare (4111 = 4428) rămâne; soldul inițial
    4428 trece la firma global-valorică fără TVA la încasare. MUTAȚIE: condiția pe 371 scoasă -> și 4111 = 4428 mutat -> pică."""
    from core import migrare_retest_0810 as m
    lume()
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SET search_path TO %s, public" % SCH)
        _nota(conn, "2099-09-01", [("371", "4428", 252), ("4428", "371", 21), ("4111", "4428", 10)])
        with conn.cursor() as cur:
            cur.execute("INSERT INTO solduri_initiale (cont, sold_debitor, sold_creditor) VALUES ('4428', 0, 99)")
        r = m.plan_si_solduri_tva_stoc(conn, SCH)
        assert (r["linii"], r["solduri"], r["raportat"]) == (2, 1, 0)
        with conn.cursor() as cur:
            cur.execute("SELECT cont_debit, cont_credit, suma::text FROM inregistrari_linii ORDER BY id")
            assert cur.fetchall() == [("371", "4428.02", "252.00"), ("4428.02", "371", "21.00"), ("4111", "4428", "10.00")]
        assert m.plan_si_solduri_tva_stoc(conn, SCH)["linii"] == 0                     # idempotentă
        conn.rollback()


def test_pct1_migrarea_nu_ghiceste_soldul_firmei_cu_tva_la_incasare(lume):
    """La firma cu TVA la încasare, soldul inițial 4428 poate fi oricare din cele două: rămâne pe loc și se raportează."""
    from core import migrare_retest_0810 as m
    lume(tvai=True)
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SET search_path TO %s, public" % SCH)
            cur.execute("INSERT INTO solduri_initiale (cont, sold_debitor, sold_creditor) VALUES ('4428', 0, 99)")
        r = m.plan_si_solduri_tva_stoc(conn, SCH)
        assert (r["solduri"], r["raportat"]) == (0, 1)
        conn.rollback()


# ── pct.3 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_pct3_mai_multe_note_fiecare_pe_drumul_aprobarii(monkeypatch):
    """„Coada de validare permite validarea mai multor note deodată.” Fiecare element trece prin `coada_aproba` (porțile ei); un refuz
    nu le anulează pe celelalte și e numit. MUTAȚIE: refuzul ridicat mai departe -> toată cererea cade -> pică."""
    from core import erori, uc_coada as uq, uc_comun
    monkeypatch.setattr(uc_comun, "_are_permisiune", lambda ctx, p: True)
    chemate = []

    def aproba(i, date, ctx):
        chemate.append(i)
        if i == 2:
            raise erori.FaraDrept({"mesaj": "ai pregătit-o tu", "cod": "PATRU_OCHI"})
        return {"ok": True}
    monkeypatch.setattr(uq, "coada_aproba", aproba)
    r = uq.coada_aproba_mai_multe([1, 2, 3, 3], {"uid": 1, "firm": 1})
    assert (r["validate"], [(x["id"], x["mesaj"], x["fel"]) for x in r["refuzate"]], chemate) == \
        ([1, 3], [(2, "ai pregătit-o tu", "neconformitate")], [1, 2, 3])   # refuzul e o afirmație tipată (P8)


def test_pct3_fara_drept_nu_se_valideaza_nimic(monkeypatch):
    """Dreptul se cere înaintea oricărei aprobări. MUTAȚIE: verificarea scoasă -> `coada_aproba` chemată -> pică."""
    from core import erori, uc_coada as uq, uc_comun
    monkeypatch.setattr(uc_comun, "_are_permisiune", lambda ctx, p: False)
    monkeypatch.setattr(uq, "coada_aproba", lambda *a: pytest.fail("aprobare fără drept"))
    with pytest.raises(erori.FaraDrept):
        uq.coada_aproba_mai_multe([1], {"uid": 1, "firm": 1})


def test_pct3_ruta_cere_poate_valida():
    import ast
    import inspect
    import main
    src = inspect.getsource(main.coada_aproba_mai_multe)
    apel = [n for n in ast.walk(ast.parse(src)) if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "cere_drept"]
    assert apel and ast.unparse(apel[0].args[0]) == "_drepturi.VALIDA"


# ── pct.4 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_pct4_nir_vechi_refacut_pe_408_prin_nota_de_validat(lume):
    """„Refă notele existente pe 408 / 4428.01; notele refăcute trec din nou prin validare.” Nota veche validată rămâne (istoria); nota
    de refacere e CIORNĂ: stornarea în roșu de pe 401 + forma nouă. După validare: 401 și 4426 la zero, datoria pe 408, TVA-ul pe
    4428.01; factura se leagă apoi în forma nouă (408 = 401). MUTAȚIE: stornarea scoasă -> 401 rămâne 665,50 -> pică."""
    from core import migrare_retest_0810 as m, stocuri_api as sa, facturi_api as fa, contare_facturi as cf
    lume()
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SET search_path TO %s, public" % SCH)
        n = sa.adauga_nir(conn, SCH, {"numar": "2", "data": "2099-10-07", "furnizor": "F", "cui": "14399840",
                                      "linii": [{"denumire": "Marfa A", "cantitate": 10, "pret_achizitie": 55, "cota_tva": 21, "pret_vanzare": 80}]})
        with conn.cursor() as cur:   # forma VECHE, ca F1: 371 = 401, 4426 = 401, validată, autor 7
            cur.execute("UPDATE inregistrari_linii SET cont_credit = '401' WHERE inregistrare_id = ANY(%s) AND cont_credit = '408'", (n["inregistrari"],))
            cur.execute("UPDATE inregistrari_linii SET cont_debit = '4426' WHERE inregistrare_id = ANY(%s) AND cont_debit = '4428.01'", (n["inregistrari"],))
            cur.execute("UPDATE inregistrari SET status = 'validata', creat_de_id = 7")
        r = m.refa_nir_forma_veche(conn, SCH)
        assert [(x[0], x[1], x[3]) for x in r] == [(n["id"], "2", 7)]
        nid = r[0][2]
        with conn.cursor() as cur:
            cur.execute("SELECT status, creat_de_id FROM inregistrari WHERE id = %s", (nid,))
            assert cur.fetchone() == ("ciorna", 7)
            cur.execute("SELECT cont_debit, cont_credit, suma::text FROM inregistrari_linii WHERE inregistrare_id = %s ORDER BY id", (nid,))
            assert cur.fetchall() == [("371", "401", "-550.00"), ("4426", "401", "-115.50"), ("371", "408", "550.00"),
                                      ("4428.01", "408", "115.50")]
            cur.execute("UPDATE inregistrari SET status = 'validata' WHERE id = %s", (nid,))
            cur.execute("""SELECT cont, sum(d) - sum(c) FROM (SELECT cont_debit cont, suma d, 0 c FROM inregistrari_linii UNION ALL
                           SELECT cont_credit, 0, suma FROM inregistrari_linii) x WHERE cont IN ('401','408','4426','4428.01') GROUP BY 1 ORDER BY 1""")
            assert [(a, str(b)) for a, b in cur.fetchall()] == [("401", "0.00"), ("408", "-665.50"), ("4426", "0.00"), ("4428.01", "115.50")]
        assert m.refa_nir_forma_veche(conn, SCH) == []                                # idempotentă
        fid = fa.creeaza_factura(conn, "FP1", "2099-10-20", "primita", [{"descriere": "Marfa A", "cantitate": 10, "pret_unitar": 55, "cota_tva": 21}],
                                 tert_nume="F", tert_cui="RO14399840")["factura_id"]
        with cf.cursor_dict(conn) as cur:
            rc = cf.contabilizeaza(cur, SCH, fid, automat=False, nir_legat=n["id"])
        assert rc["nir_legat"]["forma_noua"] is True
        conn.rollback()


# ── pct.5 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_pct5_d406_totalurile_facturii_pe_fiecare_cota():
    """F1 nr. 2: 5.000 la 21% + 800 la 11%. XML-ul spunea „bază 5.800, TVA 1.138” sub codul de 21% (codul primei linii). XSD
    `TaxInformationTotals maxOccurs="unbounded"`: câte unul pe cotă. MUTAȚIE: totalurile din prima linie -> o singură grupă -> pică."""
    from xml.etree import ElementTree as ET
    from core import d406
    f = d406.Factura(nr="2", data=__import__("datetime").date(2026, 10, 5), partener_id="0014399840", partener_nume="DANTE",
                     linii=[d406.LinieFactura(nr=1, cont="707", descriere="Marfa A", valoare=Decimal("5000"), tva_cod="310344",
                                              tva_procent=Decimal(21), tva_suma=Decimal("1050")),
                            d406.LinieFactura(nr=2, cont="707", descriere="Carte", valoare=Decimal("800"), tva_cod="310351",
                                              tva_procent=Decimal(11), tva_suma=Decimal("88"))])
    xml = "\n".join(d406._factura_xml(f, True, 0))
    tot = ET.fromstring(xml).find("InvoiceDocumentTotals")
    grupe = [(g.findtext("TaxCode"), g.findtext("TaxBase"), g.find("TaxAmount").findtext("Amount")) for g in tot.findall("TaxInformationTotals")]
    assert grupe == [("310344", "5000.00", "1050.00"), ("310351", "800.00", "88.00")]
    assert (tot.findtext("NetTotal"), tot.findtext("GrossTotal")) == ("5800.00", "6938.00")


# ── pct.6 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_pct6_numarul_in_serie_nu_ia_cifrele_seriei():
    """„F1A3 iese ca seria F1A, nr. 13 (corect: 3).” Inversa lui `numar_cu_serie`, aceeași regulă. MUTAȚIE: prefixul seriei
    nescos -> 13 -> pică."""
    from core.pdf_util import numar_in_serie as n
    assert (n("F1A", "F1A3"), n("F1A", "f1a0045"), n("-", "2"), n("", "2"), n(None, "17"), n("FCT", "ABC"), n("FCT", "12")) == \
        (3, 45, 2, 2, 17, None, 12)


# ── pct.7–10 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_pct7_contoarele_numara_fapte_nu_culoarea():
    """„F1 și F5 arată «restanță» cu «0 restanțe», iar contorul de sus «0 de urmărit», deși detaliul F1 are 5 de urmărit.” MUTAȚIE:
    „de urmărit” numărat pe culoarea galbenă -> F1 (roșie din contabilitate) iese din contor -> pică."""
    from core import uc_control_fiscal as u
    firme = [{"stare": "rosu", "lipsa": 0, "urmarit": 5, "contabil": [{"stare": "rosu"}]},     # F1
             {"stare": "rosu", "lipsa": 0, "urmarit": 3, "contabil": [{"stare": "galben"}]},   # F5
             {"stare": "rosu", "lipsa": 2, "urmarit": 0, "contabil": []},
             {"stare": "verde", "lipsa": 0, "urmarit": 0, "contabil": []}]
    assert u.contoare_portofoliu(firme) == {"restante": 1, "de_urmarit": 2, "neconcordante": 2, "nu_se_pot_verifica": 0, "la_zi": 1}


def test_pct8_necunoasterile_dinaintea_preluarii_trec_la_grupul_lor():
    """„D100 și D205 pe 2025 apar la «Nu pot verifica»; sunt dinaintea preluării și intră în grupul acela.” MUTAȚIE: comparația pe
    domeniu inversată -> rămân la „Nu pot verifica” -> pică."""
    from core import control_fiscal_api as cf
    neclar = [{"tip": "d100", "motiv": "necunoscut 2025", "domeniu_de": "2025-01", "domeniu_pana": "2025-12"},
              {"tip": "d390", "motiv": "neclar acum", "domeniu_de": "2026-09", "domeniu_pana": "2026-09"},
              {"tip": "d205", "motiv": "fără domeniu"}]
    ramase, inainte = cf.separa_neclar_inainte_de_preluare(neclar, (2026, 9))
    # [Retest 2 pct.10, 09.10.2026] domeniul se desface în perioadele declarației: D100 trimestrial -> T1–T4/2025, câte un rând
    assert [x["tip"] for x in ramase] == ["d390", "d205"]
    assert [(x["tip"], x["an"], x["perioada"]) for x in inainte] == [("d100", 2025, "T%d/2025" % t) for t in (1, 2, 3, 4)]
    assert {x["motiv"] for x in inainte} == {""}   # [deficiența 212] explicația e a grupului, nu a fiecărui rând
    assert cf.separa_neclar_inainte_de_preluare(neclar, None) == (neclar, [])


def test_212_domeniul_care_trece_peste_preluare_se_desface():
    """[deficiența 212, retestul Costin 09.10: „D100 T1–T2/2026 în alt grup decât D406 T1/2026, deși sunt aceeași perioadă”] Un
    domeniu 2026-01…2026-12 la o firmă preluată în 07/2026: T1 și T2 merg în grupul preluării, restul rămâne „Nu pot verifica”, cu
    domeniul de la 07/2026. MUTAȚIE: condiția veche (numai domeniile încheiate înaintea preluării) -> D100 rămâne întreg -> pică."""
    from core import control_fiscal_api as cf
    ramase, inainte = cf.separa_neclar_inainte_de_preluare(
        [{"tip": "d100", "motiv": "necunoscut 2026", "domeniu_de": "2026-01", "domeniu_pana": "2026-12"}], (2026, 7))
    assert [(x["perioada"], x["motiv"]) for x in inainte] == [("T1/2026", ""), ("T2/2026", "")]
    assert [(x["tip"], x["domeniu_de"], x["motiv"]) for x in ramase] == [("d100", "2026-07", "necunoscut 2026")]


TID_SINTETIC = 990811


@pytest.fixture()
def marcari(lume, monkeypatch):
    from core import uc_comun
    lume()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("UPDATE %s.firma_profil SET luna_preluare = '2099-06-01'" % SCH)
            cur.execute("DELETE FROM public.declaratii_depuse WHERE tenant_id = %s", (TID_SINTETIC,))
        c.commit()
    monkeypatch.setattr(uc_comun, "_schema_sau_404", lambda ctx, tid: SCH)
    import datetime as _dt
    from core import uc_control_fiscal as u
    monkeypatch.setattr(u, "azi_ro", lambda: _dt.date(2099, 12, 31))   # perioadele de probă sunt în 2099
    yield
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DELETE FROM public.declaratii_depuse WHERE tenant_id = %s", (TID_SINTETIC,))
            cur.execute("DELETE FROM public.firma_sursa_versiune WHERE tenant_id = %s", (TID_SINTETIC,))
            cur.execute("DELETE FROM public.supervizor_sursa WHERE tenant_id = %s", (TID_SINTETIC,))
        c.commit()


def _depuneri():
    with _db.get_conn() as c, c.cursor() as cur:
        cur.execute("SELECT tip, an, luna, sursa, nr_depunere FROM public.declaratii_depuse WHERE tenant_id = %s ORDER BY 1, 2, 3, 5",
                    (TID_SINTETIC,))
        return cur.fetchall()


def test_pct9_marcheaza_toate_dinaintea_preluarii(marcari):
    """„Marchează toate ca depuse de contabilul anterior.” Numai perioadele dinaintea preluării (06/2099) și numai cele nedepuse; data
    nu se cunoaște, deci sursa `contabil_anterior`. MUTAȚIE: verificarea lunii preluării scoasă -> 07/2099 marcat -> pică."""
    from core import uc_control_fiscal as u
    r = u.control_fiscal_depuse_anterior(TID_SINTETIC, {"perioade": [{"tip": "d300", "an": 2099, "luna": 4},
                                                                     {"tip": "d300", "an": 2099, "luna": 7}]}, {"uid": 1, "firm": 1})
    assert r["marcate"] == 1 and [x["luna"] for x in r["sarite"]] == [7]
    assert _depuneri() == [("d300", 2099, 4, "contabil_anterior", 1)]


def test_pct10_marcarea_se_modifica_si_se_anuleaza_depunerea_reala_nu(marcari):
    """„marcarea nu se poate modifica sau anula.” Modificarea = versiune nouă; anularea scoate toate versiunile marcate; o depunere prin
    iConta.eu nu se suprascrie și nu se anulează. MUTAȚIE: filtrul pe sursă scos din anulare -> depunerea reală cade -> pică."""
    from core import erori, uc_control_fiscal as u
    ctx = {"uid": 1, "firm": 1}
    with _db.get_conn() as c, c.cursor() as cur:   # o depunere PRIN iConta.eu pe 02/2099
        cur.execute("INSERT INTO public.declaratii_depuse (tenant_id, an, luna, tip, sursa) VALUES (%s, 2099, 2, 'd300', 'iconta')",
                    (TID_SINTETIC,))
        c.commit()
    u.control_fiscal_depusa_extern(TID_SINTETIC, {"tip": "d300", "an": 2099, "luna": 3, "data_depunere": "2099-04-20"}, ctx)
    u.control_fiscal_depusa_extern(TID_SINTETIC, {"tip": "d300", "an": 2099, "luna": 3, "data_depunere": "2099-04-22",
                                                  "recipisa": "R-2"}, ctx)                        # modificare
    with pytest.raises(erori.Conflict):
        u.control_fiscal_depusa_extern(TID_SINTETIC, {"tip": "d300", "an": 2099, "luna": 2, "data_depunere": "2099-03-20"}, ctx)
    assert _depuneri() == [("d300", 2099, 2, "iconta", 1), ("d300", 2099, 3, "extern", 1), ("d300", 2099, 3, "extern", 2)]
    assert u.control_fiscal_anuleaza_marcare(TID_SINTETIC, {"tip": "d300", "an": 2099, "luna": 3}, ctx)["anulate"] == 2
    with pytest.raises(erori.Conflict):
        u.control_fiscal_anuleaza_marcare(TID_SINTETIC, {"tip": "d300", "an": 2099, "luna": 2}, ctx)
    assert _depuneri() == [("d300", 2099, 2, "iconta", 1)]


def test_pct10_anularea_nu_atinge_niciodata_o_depunere_prin_iconta(marcari):
    """Apărare în adâncime: chiar cu ambele surse pe aceeași perioadă, anularea scoate numai marcările. MUTAȚIE: filtrul pe sursă scos
    din `delete_marcari` -> și depunerea reală cade -> pică."""
    from core import repo_control_fiscal_api as rp
    with _db.get_conn() as c, c.cursor() as cur:
        cur.execute("INSERT INTO public.declaratii_depuse (tenant_id, an, luna, tip, sursa, nr_depunere) VALUES "
                    "(%s, 2099, 5, 'd300', 'iconta', 1), (%s, 2099, 5, 'd300', 'extern', 2)", (TID_SINTETIC, TID_SINTETIC))
        assert rp.delete_marcari(cur, TID_SINTETIC, 2099, 5, "d300") == 1
        c.commit()
    assert _depuneri() == [("d300", 2099, 5, "iconta", 1)]


# ── pct.11 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_pct11_luna_se_inchide_dupa_ce_s_a_incheiat():
    """„luna în curs (10/2026, azi 08.10) se poate bloca, la perioadă și la evidența facturilor”. MUTAȚIE: `>=` -> `>` în
    `luna_in_curs` -> luna curentă trece -> pică."""
    from datetime import date
    from core import inchidere_luna as il
    assert il.luna_in_curs(2026, 10, azi=date(2026, 10, 8)) is not None                  # luna în curs
    assert il.luna_in_curs(2026, 11, azi=date(2026, 10, 8)) is not None                  # luna viitoare
    assert il.luna_in_curs(2026, 9, azi=date(2026, 10, 1)) is None                       # luna trecută, din prima zi a lunii următoare


def test_pct11_luna_in_curs_opreste_ambele_inchideri(lume, monkeypatch):
    """O singură regulă pentru amândouă actele: blocarea perioadei (controalele) și închiderea evidenței facturilor. MUTAȚIE: rândul
    LUNA_IN_CURS scos din `controale_inchidere` -> blocajul perioadei dispare -> pică."""
    from datetime import date
    from core import common, inchidere_luna as il, uc_comun
    lume()
    monkeypatch.setattr(common, "azi_ro", lambda: date(2099, 4, 15))
    with _db.get_conn() as c:
        ctl = uc_comun.controale_inchidere(c, SCH, 2099, 4)
        assert [b["cod"] for b in ctl["blocaje"]] == ["LUNA_IN_CURS"]                     # un rând, nu două (EFACTURI nu-l repetă)
        with pytest.raises(ValueError, match="nu s-a încheiat"):
            il.confirma(c, SCH, 2099, 4, user_id=7)
        assert il.stare(c, SCH, 2099, 4)["remediu"] is None                               # „Înregistrează e-Facturile” n-ar avea sens
        assert uc_comun.controale_inchidere(c, SCH, 2099, 3)["blocaje"] == []              # luna trecută se poate închide


def test_pct11_inchiderea_are_un_singur_loc_cardul():
    import glob
    """„«Închide luna» apare și în Istoric facturi — un singur loc, cardul.” + „«Blochează luna» e activ deși există blocaje”."""
    import re
    js = lambda p: io.open(p, encoding="utf-8").read()   # noqa: E731
    # apelurile care ÎNCHID / REDESCHID evidența facturilor, numărate pe fișier: un singur ecran le face
    apeluri = {p.rsplit("/", 1)[-1]: len(re.findall(r"api\.post\(`[^`]*/facturi/perioada/(?:confirma|redeschide)`", js(p)))
               for p in sorted(glob.glob("static/js/ecrane/*.js"))}
    assert {f: n for f, n in apeluri.items() if n} == {"firme.js": 2}
    firme = js("static/js/ecrane/firme.js")
    # [deficiența 197] poarta stă în `legaBlocareLuna` — sursa ambelor butoane (Închidere lună și antetul Registrului jurnal)
    fn = firme[firme.index("async function legaBlocareLuna"):firme.index("async function ecranInchidereLuna")]
    # blocarea e inactivă până sosesc controalele și se activează NUMAI fără blocaje (citirea nu ține ecranul — proba plasei, 58)
    assert re.search(r"if \(!lunaBlocata\) \{\s*bLock\.disabled = true;", fn)
    assert re.search(r"if \(ctl && !\(ctl\.blocaje \|\| \[\]\)\.length\) \{ bLock\.disabled = false;", fn)
    assert len(re.findall(r"legaBlocareLuna\(", firme)) == 3   # definiția + cele două butoane


# ── pct.12 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_pct12_furnizor_cu_sold_debitor_e_semnalat(lume, monkeypatch):
    """„Semnal nou la închidere: furnizor cu sold debitor (F2: 401 D 500, fără factură).” MUTAȚIE: semnul soldului inversat
    (`sold_401 < 0`) -> semnalul nu apare -> pică."""
    from datetime import date
    from core import common, uc_comun
    lume()
    monkeypatch.setattr(common, "azi_ro", lambda: date(2099, 12, 31))
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("SET search_path TO %s, public" % SCH)
        _nota(c, "2099-03-10", [("401", "5121", 500)], sursa="manual")                   # plată fără factura furnizorului
        s = uc_comun.controale_inchidere(c, SCH, 2099, 3)["semnale"]
        assert [(x["cod"], Decimal(x["sold"])) for x in s] == [("FURNIZORI_SOLD_DEBITOR", Decimal("500"))]
        _nota(c, "2099-04-02", [("601", "401", 800)], sursa="manual")                    # factura sosește: 401 creditor 300
        assert uc_comun.controale_inchidere(c, SCH, 2099, 4)["semnale"] == []
        c.rollback()


# ── pct.13 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_pct13_lunile_lipsa_se_strang_in_intervale(tmp_path):
    """„Lunile lipsă scurtate («8 luni: 01–08/2026»)”. Funcția din ecran rulată cu node (importul `api.js` înlocuit, numai
    `luniScurte` se cheamă). MUTAȚIE: condiția de consecutivitate `+ 1` -> `+ 2` -> fiecare lună separat -> pică."""
    import re
    import subprocess
    src = io.open("static/js/ecrane/mijloace_ecran.js", encoding="utf-8").read()
    src = re.sub(r'from "\.\./api\.js[^"]*"', 'from "data:text/javascript,export const api=0,esc=0,arataMesaj=0,confirmaCaseta=0,'
                 'bani=0,dataRo=0,dataIso=0"', src)
    (tmp_path / "m.mjs").write_text(src, encoding="utf-8")
    cod = ("import('%s').then((m) => console.log(JSON.stringify([m.luniScurte(%s), m.luniScurte(%s), m.luniScurte(%s)])))"
           % ((tmp_path / "m.mjs").as_posix(), ["%02d/2026" % i for i in range(1, 9)], ["11/2025", "12/2025", "01/2026", "03/2026"],
              ["05/2026"]))
    r = subprocess.run(["node", "-e", cod], capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() == '["8 luni: 01–08/2026","4 luni: 11/2025–01/2026, 03/2026","1 lună: 05/2026"]'


def test_pct13_actiunile_mijlocului_fix_sunt_intr_un_meniu():
    """„acțiunile ascunse … acțiunile într-un meniu”, „PIF tăiat”. Gardul general e `ACTIUNI_RAND_LIBERE` (verificator)."""
    import re
    src = io.open("static/js/ecrane/mijloace_ecran.js", encoding="utf-8").read()
    # celula acțiunilor: butoanele ei stau toate în meniu (numărate în celulă), PIF-ul pe un rând
    celula = re.search(r"<td>\$\{m\.activ \? `(.*?)` : \"—\"\}</td>", src, re.S).group(1)
    assert re.match(r"\s*<details class=\"dec-xml\"><summary>Acțiuni</summary>", celula) and len(re.findall(r"<button\b", celula)) == 3
    assert re.search(r'<td style="white-space:nowrap">\$\{m\.data_pif \? dataRo\(m\.data_pif\)', src)


# ── pct.15–16 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_pct16_validarea_si_generarea_spun_acelasi_lucru_despre_rezultat():
    """„D406: caseta «Rezumat» nu se vede” — `sinteza` intrase numai în răspunsul generării, iar ecranul cheamă validarea.
    Amândouă rutele întorc acum aceleași câmpuri de rezultat, dintr-o singură funcție. MUTAȚIE: `sinteza` scos din
    `campuri_rezultat` -> pică."""
    import ast
    from core import uc_declaratii as u

    class Res:
        avertismente, note_rezultat, sinteza = ["a"], [], ["D406 v2.4.9: 3 conturi"]
    assert u.campuri_rezultat("d406", Res())["sinteza"] == ["D406 v2.4.9: 3 conturi"]
    arb = ast.parse(io.open("core/uc_declaratii.py", encoding="utf-8").read())
    despachetat = {fn.name for fn in ast.walk(arb) if isinstance(fn, ast.FunctionDef)
                   for d in ast.walk(fn) if isinstance(d, ast.Dict)
                   for k, v in zip(d.keys, d.values) if k is None and isinstance(v, ast.Call)
                   and isinstance(v.func, ast.Name) and v.func.id == "campuri_rezultat"}
    assert despachetat == {"declaratie_valideaza", "declaratie_genereaza"}


def test_pct15_fereastra_larga_nu_striveste_sectiunile():
    """„«Vezi XML-ul generat», textul de subsol și «Trimite în coadă» se suprapun peste tabel; spații goale mari între
    secțiuni.” Gardul general e FER_LARG_STRIVIT (verificator); aici, regula ei pe ecranul Declarații."""
    import re
    css = re.sub(r"/\*.*?\*/", "", io.open("static/stil.css", encoding="utf-8").read(), flags=re.S)   # fără comentarii
    reguli = dict((sel.strip(), decl.strip()) for sel, decl in re.findall(r"([^{}]*\.fer-larg[^{}]*)\{([^}]*)\}", css))
    assert reguli[".fereastra.fer-larg .fereastra-corp > *"] == "flex-shrink: 0;"
    assert reguli[".fereastra.fer-larg .dec-xml"] == "flex: 0 0 auto;"


# ── pct.17 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_pct17_sablonul_firmei_nu_mai_seamana_731_738(lume):
    """„Conturile 731–738 (OMFP 3103/2017) se scot din șablonul de firmă”. MUTAȚIE: un rând 731 pus la loc în șablon -> pică."""
    lume()
    with _db.get_conn() as c, c.cursor() as cur:
        cur.execute("SELECT simbol FROM %s.plan_conturi WHERE simbol LIKE '73%%'" % SCH)
        assert cur.fetchall() == []


def _plan_73x(cur):
    for x in ("731", "732", "733", "734", "736", "738"):
        cur.execute("INSERT INTO %s.plan_conturi (simbol, denumire, tip) VALUES (%%s, 'x', 'Bifunctional')" % SCH, (x,))


def test_pct17_migrarea_scoate_numai_conturile_nefolosite(lume):
    """„… și din firmele existente care nu le folosesc.” Folosit = orice coloană de cont care îl poartă (aici: o notă pe 733 și un
    sold inițial pe analiticul 734.01). MUTAȚIE: condiția „folosit” scoasă -> 733 și 734 dispar și ele -> pică."""
    from core import migrare_retest_0810 as m
    lume()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            _plan_73x(cur)
            cur.execute("SET search_path TO %s, public" % SCH)
            cur.execute("INSERT INTO solduri_initiale (cont, denumire, sold_debitor, sold_creditor) VALUES ('734.01', 'x', 0, 50)")
        _nota(c, "2099-03-10", [("5311", "733", 100)], sursa="manual")
        r = m.scoate_conturi_73x(c, SCH)
        assert r["scoase"] == ["731", "732", "736", "738"] and r["in_plan_legal"] == []
        assert r["folosite"] == {"733": ["inregistrari_linii.cont_credit"], "734": ["solduri_initiale.cont"]}
        with c.cursor() as cur:
            cur.execute("SELECT simbol FROM %s.plan_conturi WHERE simbol LIKE '73%%' ORDER BY 1" % SCH)
            assert [x[0] for x in cur.fetchall()] == ["733", "734"]
        assert m.scoate_conturi_73x(c, SCH)["scoase"] == []                                # idempotentă
        c.rollback()


def test_pct17_firma_cu_norma_ong_isi_pastreaza_conturile(lume):
    """La norma ONG (OMFP 3103/2017) 731–738 SUNT planul legal — nu se scot. MUTAȚIE: filtrul `in_plan_legal` scos -> pică."""
    from core import migrare_retest_0810 as m
    lume()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            _plan_73x(cur)
            cur.execute("UPDATE %s.firma_profil SET baza_contabila = 'ONG'" % SCH)
        r = m.scoate_conturi_73x(c, SCH)
        assert r["scoase"] == [] and r["in_plan_legal"] == ["731", "732", "733", "734", "736", "738"]
        c.rollback()


# ── pct.18 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_pct18_pdf_balanta_are_cui_si_data(lume):
    """„PDF balanță: CUI-ul firmei și data generării în antet.” Textul se citește din PDF-ul generat (pypdf), nu din cod.
    MUTAȚIE: `antet_raport(...)` înlocuit cu numele firmei -> pică."""
    import datetime
    import io as _io
    import pypdf
    from core import documente_api as d
    lume()
    assert d.antet_raport("RETEST SRL", "RO14399840", datetime.datetime(2026, 10, 8, 21, 5)) == \
        "RETEST SRL · Cod TVA RO14399840 — Generată la 08.10.2026 21:05"   # [Retest 2 pct.16] eticheta ca pe factură
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("SET search_path TO %s, public" % SCH)
        pdf = d.balanta_pdf(c, SCH, 2099, 3, "RETEST SRL")
        c.rollback()
    import re
    text = "".join(p.extract_text() for p in pypdf.PdfReader(_io.BytesIO(pdf)).pages)
    m = re.search(r"^(.+) · Cod TVA (\S+) — Generată la (\d{2}\.\d{2}\.\d{4} \d{2}:\d{2})$", text, re.M)   # [Retest 2 pct.16]
    assert m and m.group(1, 2) == ("RETEST SRL", "RO14399840"), text[:300]


# ── pct.19 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_pct19_nota_chitantei_spune_chitanta_si_factura_stinsa(lume):
    """„Nota chitanței (F1, nr. crt. 17): descrierea e doar numele clientului; trebuie să conțină chitanța și factura stinsă.”
    Proba pe nota scrisă efectiv de `casa_api.adauga`. MUTAȚIE: descrierea înapoi la `partener` -> pică."""
    from core import casa_api
    lume()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("SET search_path TO %s, public" % SCH)
        r = casa_api.adauga(c, SCH, {"data": "2099-03-10", "categorie": "incasare_client", "suma": 121, "document": "CHF1-1",
                                     "fel_document": "chitanța", "stinge": "contravaloare factura F1A13 din 14.08.2026",
                                     "partener": "DANTE INTERNATIONAL SA"})
        with c.cursor() as cur:
            cur.execute("SELECT descriere, document_ref FROM inregistrari WHERE id = %s", (r["inregistrare_id"],))
            assert cur.fetchone() == ("Încasare de la client — chitanța CHF1-1 — contravaloare factura F1A13 din 14.08.2026 — "
                                      "DANTE INTERNATIONAL SA", "CHF1-1")
        c.rollback()
    assert casa_api.descriere_nota({"categorie": "depunere_banca", "document": "DP-4"}) == \
        "Depunere de numerar în bancă — document DP-4"                                   # aceeași regulă, orice operațiune


def test_pct19_chitanta_emisa_trimite_factura_stinsa():
    import ast
    fn = next(n for n in ast.walk(ast.parse(io.open("core/uc_tenants.py", encoding="utf-8").read()))
              if isinstance(n, ast.FunctionDef) and n.name == "chitanta_emite")
    op = next(d for d in ast.walk(fn) if isinstance(d, ast.Dict)
              and any(isinstance(k, ast.Constant) and k.value == "stinge" for k in d.keys))
    campuri = {k.value: v for k, v in zip(op.keys, op.values) if isinstance(k, ast.Constant)}
    assert isinstance(campuri["stinge"], ast.Name) and campuri["stinge"].id == "reprezentand"
    assert isinstance(campuri["fel_document"], ast.Constant) and campuri["fel_document"].value == "chitanța"


# ── pct.20 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_pct20_luna_preluarii_vine_completata_cu_propunerea():
    """„câmpul arată «---------- ----»; vine completat cu propunerea (06/2026), fără textul «Gol = propunerea»”. Iar propunerea
    neschimbată nu se fixează la salvare (rămâne propunere). MUTAȚIE: `|| lp.propunere` scos din `value` -> pică."""
    import re
    js = io.open("static/js/ecrane/date_firma.js", encoding="utf-8").read()
    camp = re.search(r'<input type="month" class="camp-input" id="df-luna_preluare" value="\$\{esc\(([^)]*)\)\}"', js)
    assert camp and camp.group(1) == 'lp.salvata || lp.propunere || ""'
    ajutor = re.search(r'<span class="camp-ajutor">De la ea se numără restanțele[^\n]*</span>', js).group(0)
    assert re.findall(r"Gol = propunerea", ajutor) == []
    assert re.search(r"date\.luna_preluare = \(_lp\.value && _lp\.value !== _lp\.dataset\.propunere\) \? _lp\.value : null;", js)
