# -*- coding: utf-8 -*-
"""GARD — emiterea pe F1: Date firmă la deschidere, forma propusă, cota consemnată, data/scadența/seria, PDF-ul conform art.319
(comanda Costin 05.10.2026, pct.2–5).

Pct.2: *„Datele firmei care blochează emiterea (formă juridică, capital) se verifică la deschiderea «Emite factură», nu după
completarea întregului formular. Forma juridică se precompletează din ANAF / denumire unde e neechivocă.”*
Pct.3: *„contabilul poate corecta cota; schimbarea rămâne consemnată (propus → ales, cine, când).”*
Pct.4: *„Formularul de factură nu arată data emiterii, scadența și seria … scadența alimentează scadențarul.”*
Pct.5: *„codul de TVA … fără RO (lit. d, f); lipsește seria (lit. a); data apare ca «Emisă - …», ca o stare, nu ca «Data
emiterii»; fără scadență; fișierul se deschide ca «(anonymous)», fără nume.”*
Temei pct.5: CF art.319 alin.(20) lit.a), b), d), f); CF art.318 alin.(1) („are prefixul RO”).
"""
import glob
import datetime
import io
import os
import re

import pytest

from core import capital_social as CS
from core import factura_pdf as FP

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANAF_LA_EMITERE_REAL = True   # vezi core/conftest.py: aici se probează consultarea însăși, cu ANAF simulat


# ── pct.2: forma juridică propusă numai când e neechivocă ───────────────────────────────────────────────────────────────
@pytest.mark.parametrize("denumire,forma", [
    ("F1 Comert Stoc SRL", "SRL"), ("SUPORT VIRTUAL S.R.L.", "SRL"), ("Firma Ion SRL-D", "SRL"),
    ("DANTE INTERNATIONAL SA", "SA"), ("Alfa S.A.", "SA"), ("ALFA S.N.C.", "SNC"), ("Beta S.C.A.", "SCA"),
    ("MUSA", None), ("Cabinet Prisma", None), ("MICHAEL H.HENKE", None), ("", None)])
def test_forma_din_denumire(denumire, forma):
    assert CS.forma_din_denumire(denumire) == forma


def test_forma_propusa_cere_acord_intre_surse():
    """Valorile ANAF sunt cele văzute pe răspunsul REAL v9 (05.10.2026); surse în dezacord -> nicio propunere (nu se ghicește)."""
    assert CS.forma_propusa("SOCIETATE COMERCIALĂ CU RĂSPUNDERE LIMITATĂ", "SUPORT VIRTUAL S.R.L.") == ("SRL", "ANAF")
    assert CS.forma_propusa("SOCIETATE COMERCIALĂ PE ACŢIUNI", "DANTE INTERNATIONAL SA") == ("SA", "ANAF")
    assert CS.forma_propusa(None, "F1 Comert Stoc SRL") == ("SRL", "denumire")
    assert CS.forma_propusa(None, "X SRL", "X SA") == (None, None)
    assert CS.forma_propusa("SOCIETATE COMERCIALĂ PE ACŢIUNI", "X SRL") == (None, None)
    assert CS.forma_propusa("ASOCIAȚIE", "Asociația Y") == (None, None)


def test_mesajul_de_la_deschidere_nu_spune_ca_factura_a_fost_refuzata():
    m = CS.mesaj_la_deschidere(["forma juridică a firmei (SRL, SA etc.)"], "SRL", "denumire")
    assert re.search(r"^Înainte de a emite: în Date firmă lipsește forma juridică", m)
    assert re.search(r"Forma propusă: SRL \(din denumirea firmei\)", m)
    assert not re.search(r"nu s-a emis", m)
    assert CS.mesaj_la_deschidere([]) is None


# ── pe bază: schemă efemeră din template, în ROLLBACK ─────────────────────────────────────────────────────────────────
def _db_ok():
    try:
        from core import db
        db.init_pool()
        with db.get_conn():
            return True
    except Exception:
        return False


SCH = "ztest_emitere_f1"


@pytest.fixture
def conn():
    from core import db, tenant_provisioning as _tp
    db.init_pool()
    with db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
                cur.execute(_tp.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), SCH))
                cur.execute("SET LOCAL search_path TO %s, public" % SCH)
                cur.execute("INSERT INTO firma_profil (id, nume, cui, platitor_tva, tip_firma) VALUES (1, 'ZT Comert Proba SRL', '14399840', true, 'srl')")
            yield c
        finally:
            c.rollback()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_pregatirea_emiterii_spune_lipsurile_forma_propusa_si_cotele(conn):
    """MUTAȚIE: `lipsuri_firma` scos din `pregatire_emitere` -> pică."""
    from core import facturi_api
    r = facturi_api.pregatire_emitere(conn, -1, datetime.date(2026, 10, 5))
    assert r["lipsuri_firma"] == ["forma juridică a firmei (SRL, SA etc.)"]
    assert (r["forma_propusa"], r["forma_propusa_sursa"]) == ("SRL", "denumire")
    assert r["cote_permise"] == [21, 11, 0]
    with conn.cursor() as cur:
        cur.execute("UPDATE firma_profil SET forma_juridica='SRL', capital_subscris=200")
    r = facturi_api.pregatire_emitere(conn, -1, datetime.date(2026, 10, 5))
    assert r["lipsuri_firma"] == [] and r["forma_propusa"] is None and r["mesaj_lipsuri"] is None


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_cotele_permise_se_citesc_la_data_facturii_nu_azi(conn):
    """Cotele oferite pe linie sunt cele în vigoare la DATA FACTURII din formular (OUG 89/2025 art.III a schimbat cotele de la
    01.08.2025). O factură datată 31.07.2025 nu primește 21/11. MUTAȚIE: `la_data` înlocuit cu „azi” în `pregatire_emitere`
    -> pe 31.07.2025 ies [21, 11, 0] -> pică. Data e obligatorie (interdicția 3, `test_data_curenta`)."""
    from core import facturi_api
    assert facturi_api.pregatire_emitere(conn, -1, datetime.date(2025, 7, 31))["cote_permise"] == [19, 9, 5, 0]
    assert facturi_api.pregatire_emitere(conn, -1, datetime.date(2025, 8, 1))["cote_permise"] == [21, 11, 0]
    import inspect
    assert "la_data=None" not in str(inspect.signature(facturi_api.pregatire_emitere)), "data facturii e obligatorie"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_scadenta_inaintea_emiterii_se_refuza(conn):
    from core import facturi_api
    with pytest.raises(ValueError) as e:
        facturi_api.creeaza_factura(conn, "ZT1", "2026-10-05", "emisa",
                                    [{"descriere": "x", "cantitate": 1, "pret_unitar": 10, "cota_tva": 21}],
                                    tert_nume="ZT", tert_cui="14399840", data_scadenta="2026-10-01")
    assert str(e.value) == facturi_api.MESAJ_SCADENTA_INAINTE_DE_EMITERE


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_cota_schimbata_se_consemneaza_doar_cand_difera(conn):
    """MUTAȚIE: INSERT-ul scos -> [] -> pică; comparația scoasă -> rânduri și pentru cota păstrată -> pică."""
    from core import repo_facturi
    with conn.cursor() as cur:
        cur.execute("INSERT INTO facturi (numar, data_emitere, directie, total, tva) VALUES ('ZT1', '2026-10-05', 'emisa', 0, 0) RETURNING id")
        fid = cur.fetchone()[0]
        linii = [{"descriere": "Pâine", "cota_propusa": 21, "cota_tva": 11},        # schimbată -> rând
                 {"descriere": "Consultanță", "cota_propusa": 21, "cota_tva": 21},  # păstrată -> nimic
                 {"descriere": "Manual", "cota_propusa": None, "cota_tva": 21}]     # fără propunere -> nimic
        assert repo_facturi.jurnalizeaza_cota_aleasa(cur, fid, linii, 7) == 1
        cur.execute("SELECT factura_id, linie_nr, descriere, cota_propusa, cota_aleasa, user_id FROM factura_cota_jurnal")
        assert [tuple(map(lambda v: float(v) if hasattr(v, "as_tuple") else v, r)) for r in cur.fetchall()] == [(fid, 1, "Pâine", 21.0, 11.0, 7)]
        with pytest.raises(ValueError):
            repo_facturi.jurnalizeaza_cota_aleasa(cur, fid, linii, None)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_factura_stearsa_ia_cu_ea_jurnalul_cotei_si_migrarea_repara_legatura_veche(conn):
    """O factură necontată se poate șterge (`facturi_api` — `DELETE FROM facturi`); jurnalul cotei e atributul liniilor ei, deci
    pleacă odată cu ea, ca `factura_linii` (ON DELETE CASCADE). Fără asta ștergerea ar cădea pe cheia străină (500).
    Tabelele create înainte de reparație (test 35, producție 5) au legătura fără CASCADE: migrarea o reface.
    MUTAȚIE: `ON DELETE CASCADE` scos din migrare -> ștergerea pică pe cheia străină -> pică."""
    from core import migrare_factura_cota_jurnal as m, repo_facturi
    with conn.cursor() as cur:
        cur.execute("SELECT conname FROM pg_constraint WHERE conrelid = %s::regclass AND contype = 'f'", (SCH + ".factura_cota_jurnal",))
        (fk,) = cur.fetchone()
        cur.execute("ALTER TABLE factura_cota_jurnal DROP CONSTRAINT %s" % fk)   # forma de dinainte de reparație
        cur.execute("ALTER TABLE factura_cota_jurnal ADD FOREIGN KEY (factura_id) REFERENCES %s.facturi(id)" % SCH)
    assert not m.verifica(conn, SCH)
    m.aplica(conn, SCH)
    assert m.verifica(conn, SCH)
    with conn.cursor() as cur:
        cur.execute("INSERT INTO facturi (numar, data_emitere, directie, total, tva) VALUES ('ZT9', '2026-10-05', 'emisa', 0, 0) RETURNING id")
        fid = cur.fetchone()[0]
        assert repo_facturi.jurnalizeaza_cota_aleasa(cur, fid, [{"descriere": "x", "cota_propusa": 21, "cota_tva": 11}], 7) == 1
        cur.execute("DELETE FROM facturi WHERE id = %s", (fid,))
        cur.execute("SELECT count(*) FROM factura_cota_jurnal WHERE factura_id = %s", (fid,))
        assert cur.fetchone()[0] == 0


def test_emiterea_consemneaza_cota_in_aceeasi_tranzactie():
    """Structural: apelul la jurnal stă în `facturi_emite`, ÎNĂUNTRUL blocului conexiunii (comis odată cu factura)."""
    src = io.open(os.path.join(RAD, "core", "uc_tenants.py"), encoding="utf-8").read()
    corp = src[src.index("def facturi_emite("):src.index("def proforma_transforma(")]
    bloc = corp[corp.index("with db.get_conn(schema) as conn:"):corp.index("# [lot 2] moneda inexistenta")]
    assert len(re.findall(r"repo_facturi\.jurnalizeaza_cota_aleasa\(cur, r\[\"factura_id\"\], linii, ctx\[\"uid\"\]\)", bloc)) == 1


# ── pct.5: consultarea ANAF pentru beneficiar (simulată) ─────────────────────────────────────────────────────────────────
def test_platitorul_de_tva_al_beneficiarului_din_anaf(monkeypatch):
    from core import uc_comun, anaf_api
    raspuns = {"14399840": [{"gasit": True, "platitor_tva": True}], "40510009": [{"gasit": True, "platitor_tva": False}],
               "999": [{"gasit": False}]}
    monkeypatch.setattr(anaf_api, "valideaza_cui", lambda l: raspuns[l[0]])
    assert uc_comun._platitor_tva_tert("14399840") is True
    assert uc_comun._platitor_tva_tert("40510009") is False
    assert uc_comun._platitor_tva_tert("999") is None
    assert uc_comun._platitor_tva_tert("14399840", "DE") is None
    monkeypatch.setattr(anaf_api, "valideaza_cui", lambda l: (_ for _ in ()).throw(RuntimeError("ANAF jos")))
    assert uc_comun._platitor_tva_tert("14399840") is None


# ── pct.5: PDF-ul facturii ──────────────────────────────────────────────────────────────────────────────────────────────
def _text_pdf(b):
    from pypdf import PdfReader
    r = PdfReader(io.BytesIO(b))
    return "\n".join(p.extract_text() for p in r.pages), (r.metadata or {}).get("/Title")


@pytest.mark.parametrize("cui,platitor,asteptat", [
    ("14399840", True, ("Cod TVA", "RO14399840")), ("RO14399840", True, ("Cod TVA", "RO14399840")),
    ("40510009", False, ("CIF", "40510009")), ("RO14399840", None, ("Cod TVA", "RO14399840")),
    ("14399840", None, ("CUI", "14399840")), ("", True, (None, None))])
def test_codul_fiscal_pe_factura(cui, platitor, asteptat):
    assert FP.cod_fiscal_pe_factura(cui, platitor) == asteptat


def test_pdf_facturii_are_ro_seria_data_emiterii_scadenta_si_titlu():
    """MUTAȚIE: `title=` scos -> metadata „(anonymous)” -> pică; „Data emiterii” înapoi la „Emisă -” -> pică."""
    profil = {"nume": "ZT Comert Proba SRL", "cui": "40410000", "platitor_tva": True, "tip_firma": "srl",
              "forma_juridica": "SRL", "capital_subscris": 200}
    factura = {"numar": "FCT12", "serie": "FCT", "data_emitere": "2026-10-05", "data_scadenta": "2026-11-04",
               "directie": "emisa", "moneda": "RON", "tert_nume": "DANTE INTERNATIONAL SA", "tert_cui": "14399840",
               "tert_platitor_tva": True, "total": 121, "tva": 21,
               "linii": [{"descriere": "Consultanță", "um": "buc", "cantitate": 1, "pret_unitar": 100, "cota_tva": 21}]}
    text, titlu = _text_pdf(FP.genereaza_pdf(profil, factura))
    t = re.sub(r"\s+", " ", text)
    assert re.search(r"Cod TVA: RO40410000", t), t[:400]                     # furnizor plătitor — lit.d) + art.318
    assert re.search(r"DANTE INTERNATIONAL SA - Cod TVA: RO14399840", t)      # beneficiar plătitor — lit.f)
    assert re.search(r"Seria FCT nr\. 12", t)                                 # lit.a)
    assert re.search(r"Data emiterii: 05\.10\.2026", t) and not re.search(r"Emisă -", t)   # lit.b)
    assert re.search(r"Data scadenței: 04\.11\.2026", t)
    assert titlu == "Factura FCT nr. 12"


def test_niciun_pdf_fara_titlu():
    """Clasa „(anonymous)”: orice `SimpleDocTemplate(` din aplicație primește `title=` (reportlab scrie altfel „(anonymous)”)."""
    fara = []
    for f in sorted(glob.glob(os.path.join(RAD, "core", "*.py"))):
        if os.path.basename(f).startswith("test_"):
            continue
        src = io.open(f, encoding="utf-8").read()
        for m in re.finditer(r"SimpleDocTemplate\(", src):
            apel = src[m.end():m.end() + 600]
            inchis = apel[:apel.index(")\n")] if ")\n" in apel else apel
            if not re.search(r"\btitle=", inchis):
                fara.append("%s:%d" % (os.path.relpath(f, RAD), src.count("\n", 0, m.start()) + 1))
    assert len(glob.glob(os.path.join(RAD, "core", "*.py"))) > 100
    assert not fara, "PDF-uri fără titlu (se deschid ca „(anonymous)”): %s" % fara


# ── găsit la proba pct.2: poarta „perioadă închisă” (R46) pe PREZENȚA câmpului, nu pe SCHIMBARE ─────────────────────────────
@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_date_firma_cu_luna_inchisa_se_salveaza_daca_nu_schimba_ce_decide(conn):
    """Formularul trimite mereu CUI-ul; pe o firmă cu o lună închisă, Date firmă nu se mai salva deloc, iar refuzul ieșea 500.
    MUTAȚIE: comparația cu valoarea curentă scoasă -> salvarea identică refuzată -> pică."""
    from core import firma_profil_api as fpa
    with conn.cursor() as cur:
        cur.execute("INSERT INTO perioade_blocate (an, luna, blocat_la) VALUES (2026, 8, now())")
        # date sintetice pe tabele partajate, în ROLLBACK (fixtura): CUI cu cifra de control verificată (CLAUDE.md)
        cur.execute("INSERT INTO public.accounting_firms (nume) VALUES ('ZT EMITERE F1') RETURNING id")
        firm = cur.fetchone()[0]
        cur.execute("INSERT INTO public.tenants (schema_name, nume, cui, accounting_firm_id, activ) "
                    "VALUES (%s, 'ZT Comert Proba SRL', '14399840', %s, true) RETURNING id", (SCH, firm))
        tid = cur.fetchone()[0]
    r = fpa.salveaza_date(conn, {"cui": "14399840", "telefon": "0712345678"}, tenant_id=tid)
    assert r.get("ok") is True, r
    r = fpa.salveaza_date(conn, {"cui": "40410000"}, tenant_id=tid)
    assert r.get("ok") is False and r.get("camp") == "cui" and re.search(r"perioade închise", r["mesaj"]), r


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_vectorul_cu_luna_inchisa_se_salveaza_cu_aceleasi_valori(conn):
    """Date firmă trimite și vectorul la fiecare salvare: aceleași valori nu rescriu nimic.
    MUTAȚIE: comparația scoasă -> salvarea identică refuzată -> pică."""
    from core import vector_fiscal_api as v
    with conn.cursor() as cur:
        cur.execute("UPDATE firma_profil SET regim_fiscal='micro', platitor_tva=true, tip_decont='T', operatiuni_ic=false, inreg_art317=false")
        cur.execute("INSERT INTO perioade_blocate (an, luna, blocat_la) VALUES (2026, 8, now())")
    assert v.salveaza(conn, "micro", True, "trimestrial", False, user_id=5)["ok"] is True   # „T” = trimestrial: nicio schimbare
    r = v.salveaza(conn, "micro", True, "lunar", False, user_id=5)
    assert r["ok"] is False and r["cod"] == "PESTE_PERIOADA_INCHISA", r
