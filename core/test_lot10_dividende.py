# -*- coding: utf-8 -*-
"""430 — dividende (Decontări asociați), lotul 10 (comanda Costin 20.10.2026, verbatim):
„10. Deficiența 430 — dividende (Decontări asociați), F6, dividend anual brut 10.000. Sumele notei sunt corecte (1171 = 457 10.000;
457 = 446 1.600). Probleme: a) F6 are rezultatul reportat importat pe 117 (34.650), iar nota debitează 1171 (sold 0), fără avertisment
și fără verificarea că dividendul nu depășește profitul disponibil; b) nu se cer asociații și cotele lor, deci nu se vede cât revine
fiecăruia și cât impozit se reține pe fiecare; c) documentul justificativ propus e „Notă de calcul”, nu hotărârea adunării asociaților /
decizia asociatului unic; d) pe linia 457 = 446 scrie „sursa: facturile”; e) formate: „brut 10000”, „16.00%” în loc de 10.000 și 16%;
f) după generare, mesajul nu arată nota și nu duce la ea.”

Temeiuri (citate pe linie lângă assert): Legea 31/1990 art.67 alin.(1)–(3), art.194 alin.(1) lit.a, art.196^1 alin.(1)–(2); OMFP
1802/2014 funcțiunea conturilor 117 și 457; CF art.97 alin.(7). Schemă EFEMERĂ din tenant_template (ștearsă la final), perioade 2099;
CNP-urile sintetice au cifra de control verificată (`identitate.valideaza_cnp`)."""
import ast
import datetime
import io
import os
import re
from decimal import Decimal

import pytest

from core import db as _db
from core import decontari_asociati as da
from core import tenant_provisioning as _tprov

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCH = "efemer_lot10_div"
A1 = ("POPESCU ION", "1800101400016", 60)        # CNP-uri sintetice, cifra de control verificată
A2 = ("IONESCU MARIA", "2850202400023", 40)


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


# ── motorul (pur) ────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_430b_dividendul_se_imparte_pe_asociati_cu_impozitul_pe_fiecare():
    parti = da.imparte_dividend(10000, [(A1[1], A1[0], 60), (A2[1], A2[0], 40)], Decimal("16"))
    # Legea 31/1990 art.67 alin.(2): „Dividendele se distribuie asociaților proporțional cu cota de participare la capitalul social vărsat”
    assert [(p["nume"], p["brut"], p["impozit"], p["net"]) for p in parti] == [
        ("POPESCU ION", Decimal("6000.00"), Decimal("960.00"), Decimal("5040.00")),
        ("IONESCU MARIA", Decimal("4000.00"), Decimal("640.00"), Decimal("3360.00"))]


def test_430b_impozitul_se_rotunjeste_pe_fiecare_asociat():
    parti = da.imparte_dividend(Decimal("100.01"), [("1", "A", Decimal("33.33")), ("2", "B", Decimal("33.33")), ("3", "C", Decimal("33.34"))],
                                Decimal("16"))
    # suma părților = dividendul aprobat (diferența de rotunjire la cota cea mai mare — INTERPRETARE CU TEMEI în `imparte_dividend`)
    assert sum(p["brut"] for p in parti) == Decimal("100.01")
    # CF art.97 alin.(7): „se impozitează cu o cotă de 16% din suma acestora” — pe dividendul FIECĂRUIA, ROUND_HALF_UP la ban
    assert [p["impozit"] for p in parti] == [(p["brut"] * Decimal("0.16")).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP") for p in parti]


def test_430b_fara_asociati_sau_cote_incomplete_refuza_si_trimite_la_date_firma():
    with pytest.raises(da.StructuraAsociati, match="Date firmă → Asociați"):
        da.imparte_dividend(10000, [], Decimal("16"))
    # Legea 31/1990 art.67 alin.(2): fără 100% din capital, o parte din dividend n-ar avea beneficiar
    with pytest.raises(da.StructuraAsociati, match="însumează 90%, nu 100%"):
        da.imparte_dividend(10000, [("1", "A", 50), ("2", "B", 40)], Decimal("16"))


def test_430b_nota_are_randurile_fiecarui_asociat_din_contul_sursa():
    r = da.nota_dividend(10000, datetime.date(2099, 5, 20), False, False, asociati=[(A1[1], A1[0], 60), (A2[1], A2[0], 40)],
                         cont_sursa="117")
    # OMFP 1802/2014, contul 457: „În creditul contului 457 [...]: – dividendele datorate acționarilor/asociaților din profitul realizat
    # în exercițiile precedente (117)”
    assert [p["linii"] for p in r["parti"]] == [[("117", "457", Decimal("6000.00")), ("457", "446", Decimal("960.00"))],
                                                [("117", "457", Decimal("4000.00")), ("457", "446", Decimal("640.00"))]]
    assert (r["impozit"], r["net"]) == (Decimal("1600.00"), Decimal("8400.00"))


def test_430e_cota_fara_zecimale_inutile():
    assert str(da.cota_dividend(datetime.date(2099, 1, 1))) == "16"            # era „16.00”
    assert da.procent_text(da.cota_dividend(datetime.date(2099, 1, 1))) == "16%"
    assert da.procent_text(Decimal("33.33")) == "33,33%"


# ── nota din Operațiuni speciale, pe baza de test ────────────────────────────────────────────────────────────────────────────
@pytest.fixture()
def firma(monkeypatch):
    """F6 pe scurt: rezultatul reportat preluat pe 117 (34.650,00, fără analitic) la 31.12.2098."""
    if not _db_ok():
        pytest.skip("DB indisponibil")
    from core import auth_api
    with _db.get_conn() as c, c.cursor() as cur:
        cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        cur.execute(_tprov.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), SCH))
        cur.execute("SET LOCAL search_path TO %s, public" % SCH)   # [lotul 10] LOCAL: nu se scurge în pool (ascundea 500-ul de la 430)
        cur.execute("INSERT INTO firma_profil (id, nume, cui) VALUES (1, 'F6 TEST SRL', '14399840')")
        cur.execute("INSERT INTO solduri_initiale (cont, denumire, sold_debitor, sold_creditor, data_referinta) "
                    "VALUES ('117', 'Rezultatul reportat', 0, 34650, '2098-12-31')")
        c.commit()
    monkeypatch.setattr(auth_api, "schema_tenant", lambda conn, uid, tid: SCH)
    yield SCH
    with _db.get_conn() as c, c.cursor() as cur:
        cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        c.commit()


def _sql(q, a=()):
    with _db.get_conn() as c, c.cursor() as cur:
        cur.execute("SET LOCAL search_path TO %s, public" % SCH)   # [lotul 10] LOCAL: nu se scurge în pool (ascundea 500-ul de la 430)
        cur.execute(q, a)
        r = cur.fetchall() if cur.description else None
        c.commit()
        return r


def _asociati(*a):
    for nume, cnp, cota in a:
        _sql("INSERT INTO asociati (nume, cnp, cota) VALUES (%s, %s, %s)", (nume, cnp, cota))


CORP = {"data": "2099-05-20", "operatie": "dividend", "brut": 10000, "interimar": "0", "cu_plata": "false",
        "numar_hotarare": "3", "data_hotarare": "2099-05-15"}
CTX = {"uid": 1, "rol": "admin_firma"}


def _nota(corp=None):
    from core import uc_tenants
    return uc_tenants.nota_asociati(1, dict(CORP, **(corp or {})), CTX)


def _refuz(corp=None):
    from core import erori
    with pytest.raises(erori.DateInvalide) as e:
        _nota(corp)
    return e.value.detaliu


def test_430b_fara_asociati_refuzul_trimite_la_date_firma(firma):
    d = _refuz()
    assert d["ecran"] == "date_firma"              # DS cap.6 v2.74: butonul „Deschide Date firmă” lângă refuz
    assert d["mesaj"] == da.FARA_ASOCIATI, d       # refuzul care trimite la Date firmă → Asociați (constanta, nu o copie a textului)
    assert _sql("SELECT count(*) FROM inregistrari") == [(0,)]


def test_430a_dividendul_peste_profitul_disponibil_se_refuza(firma):
    _asociati(A1, A2)
    d = _refuz({"brut": 40000})
    # Legea 31/1990 art.67 alin.(3): „Nu se vor putea distribui dividende decât din profituri determinate potrivit legii.” — refuzul
    # numește data hotărârii și soldul creditor al fiecărui cont sursă (34.650 pe 117, fără analitic)
    assert d["mesaj"].startswith("Dividendul brut de 40.000,00 lei depășește profitul nerepartizat la 15.05.2099 — 1171: sold creditor "
                                 "0,00 lei; 117 (fără analitic): sold creditor 34.650,00 lei."), d
    assert d["erori_campuri"][0]["camp"] == "op-brut"


def test_430a_din_117_preluat_fara_analitic_nota_debiteaza_117_cu_avertisment(firma):
    _asociati(A1, A2)
    r = _nota()
    # OMFP 1802/2014, contul 117: „soldul creditor, profitul nerepartizat” — nota debitează contul care ARE soldul, nu 1171 cu sold 0
    # avertismentul e o afirmație tipată (`fapt`, decizia 21.08: afirmațiile despre datele firmei sunt obiecte); ecranul arată `motiv`
    assert r["cont_sursa"] == "117" and r["afirmatie"]["fel"] == "fapt"
    assert r["afirmatie"]["unde"] == "contul 117, la 15.05.2099", r["afirmatie"]
    assert "fără analiticul 1171: nota debitează 117, contul care are soldul. Reclasifică soldul pe 1171 (nota 117 = 1171)" in \
        r["afirmatie"]["motiv"], r["afirmatie"]
    assert {d for d, c, s in _sql("SELECT cont_debit, cont_credit, suma FROM inregistrari_linii WHERE cont_credit = '457'")} == {"117"}


def test_430a_cu_1171_nota_debiteaza_1171_fara_avertisment(firma):
    _sql("INSERT INTO solduri_initiale (cont, denumire, sold_debitor, sold_creditor, data_referinta) "
         "VALUES ('1171', 'Rezultatul reportat - profit', 0, 20000, '2098-12-31')")
    _asociati(A1, A2)
    r = _nota()
    assert r["cont_sursa"] == "1171" and "afirmatie" not in r


def test_430a_ciornele_de_dividende_consuma_profitul_disponibil(firma):
    _asociati(A1, A2)
    _nota({"brut": 30000})
    d = _refuz({"brut": 10000})        # 34.650 - 30.000 propuși în ciornă = 4.650 disponibili
    assert ("117 (fără analitic): sold creditor 34.650,00 lei; din 117, 30.000,00 lei sunt deja propuși ca dividende în nota "
            "nevalidată (din 20.05.2099)") in d["mesaj"], d


def test_430bcde_nota_pe_asociati_cu_hotararea_sursa_si_formatele(firma):
    _asociati(A1, A2)
    r = _nota()
    nid = r["inregistrare_id"]
    sursa, doc, descr = _sql("SELECT sursa, document_ref, descriere FROM inregistrari WHERE id = %s", (nid,))[0]
    # c) Legea 31/1990 art.194 alin.(1) lit.a: adunarea asociaților „să aprobe situația financiară anuală și să stabilească repartizarea
    # profitului net” — hotărârea e documentul justificativ, nu „Notă de calcul”
    assert doc == "Hotărârea adunării generale a asociaților nr 3 din 15.05.2099"
    assert sursa == "operatiuni"                                           # d) nu „facturi”
    from core import jurnal_api
    assert jurnal_api.eticheta_sursa(sursa) == "operațiunile speciale"
    # e) „brut 10000”, „16.00%” -> „10.000,00 lei”, „16%”
    assert descr == ("Dividende anuale 10.000,00 lei brut, impozit 16% (Hotărârea adunării generale a asociaților nr 3 din "
                     "15.05.2099)"), descr
    assert r["cota"] == "16%"
    # b) un rând pe fiecare asociat, cu asociatul ca partener al rândului
    assert _sql("SELECT cont_debit, cont_credit, suma::text, partener_cui, partener_nume FROM inregistrari_linii "
                "WHERE inregistrare_id = %s ORDER BY id", (nid,)) == [
        ("117", "457", "6000.00", A1[1], A1[0]), ("457", "446", "960.00", A1[1], A1[0]),
        ("117", "457", "4000.00", A2[1], A2[0]), ("457", "446", "640.00", A2[1], A2[0])]
    assert [(a["nume"], a["cota"], a["brut"], a["impozit"], a["net"]) for a in r["asociati"]] == [
        ("POPESCU ION", "60%", "6000.00", "960.00", "5040.00"), ("IONESCU MARIA", "40%", "4000.00", "640.00", "3360.00")]
    # f) răspunsul numește nota (cum o arată Registrul jurnal) și conturile ei, cu id-ul și data pentru legătura spre ea
    assert r["nota"] == "117 = 457 10.000,00 lei; 457 = 446 1.600,00 lei" and r["nota_eticheta"] and r["data"] == "2099-05-20"


def test_430c_asociatul_unic_decide_prin_decizie(firma):
    _asociati((A1[0], A1[1], 100))
    r = _nota()
    # Legea 31/1990 art.196^1 alin.(1)–(2): asociatul unic „va exercita atribuțiile adunării generale” și „va consemna de îndată, în
    # scris, orice decizie”
    assert r["document"] == "Decizia asociatului unic nr 3 din 15.05.2099"


def test_430c_numarul_si_data_hotararii_se_cer(firma):
    _asociati(A1, A2)
    assert _refuz({"numar_hotarare": ""})["erori_campuri"][0]["camp"] == "op-numar_hotarare"
    assert _refuz({"data_hotarare": ""})["erori_campuri"][0]["camp"] == "op-data_hotarare"
    assert _refuz({"data": "2099-05-10"})["erori_campuri"][0]["camp"] == "op-data"     # nota înaintea hotărârii


def test_430b_propunerea_inainte_de_generare_nu_scrie(firma):
    from core import uc_tenants
    _asociati(A1, A2)
    p = uc_tenants.dividende_impartire(1, {"brut": "10000", "data_hotarare": "2099-05-15", "interimar": "0", "data": ""}, CTX)
    assert [(a["nume"], a["brut"], a["impozit"]) for a in p["asociati"]] == [("POPESCU ION", "6000.00", "960.00"),
                                                                            ("IONESCU MARIA", "4000.00", "640.00")]
    assert (p["cota"], p["impozit"], p["net"]) == ("16%", "1600.00", "8400.00")
    assert _sql("SELECT count(*) FROM inregistrari") == [(0,)]


def test_430b_structura_de_la_data_hotararii_nu_cea_de_azi(firma):
    """Legea 31/1990 art.67 alin.(6): „Dividendele care se cuvin după data transmiterii acțiunilor aparțin cesionarului” — la o hotărâre
    de dinaintea cesiunii, dividendul e al cedentului (structura din `asociati_istoric`)."""
    _asociati(A2[0:2] + (100,))
    _sql("INSERT INTO asociati_istoric (cnp, nume, cota, valabil_pana_la) VALUES (%s, %s, 100, '2099-06-30')", (A1[1], A1[0]))
    r = _nota()
    assert [a["nume"] for a in r["asociati"]] == ["POPESCU ION"]


# ── 430d / 430e, clasa: toate operațiunile speciale ─────────────────────────────────────────────────────────────────────────
def _functii_operatiuni():
    """Use-case-urile rutelor din `REGISTRU` (ecranul Operațiuni speciale), citite din cod."""
    import sys
    sys.path.insert(0, os.path.join(RAD, "scripts"))
    from scan_formulare_operatiuni import _citeste, formulare, functie_uc
    js, main, uc = _citeste("static/js/ecrane/operatiuni_ecran.js"), _citeste("main.py"), _citeste("core/uc_tenants.py")
    return {ruta: functie_uc(ruta, main, uc) for _ch, ruta, _c in formulare(js)}


#: [430d] Cele două funcții care mai scriu cu sursa veche sunt în lucru la alți executori ai lotului 10 (TVA la încasare — T; reevaluarea
#: în valută — V). Clichet: lista nu crește; trec la `nota_operatiune_ciorna` odată cu lucrul lor.
SURSA_VECHE_PERMISA = set()   # [lotul 10] T / V trecute și ele pe `nota_operatiune_ciorna`


def _cheama(src, nume):
    """Funcția use-case (sursa ei, `functie_uc`) cheamă `nume(...)` — apelul, ca nod AST al funcției din `core/uc_tenants.py` (un
    comentariu sau un șir care pomenește numele nu e un apel)."""
    fn = _UC_FUNCTII[src.split("(", 1)[0][len("def "):].strip()]
    return any(isinstance(x, ast.Call) and (getattr(x.func, "attr", None) or getattr(x.func, "id", None)) == nume for x in ast.walk(fn))


_UC_FUNCTII = {n.name: n for n in ast.parse(io.open(os.path.join(RAD, "core", "uc_tenants.py"), encoding="utf-8").read()).body
               if isinstance(n, ast.FunctionDef)}


def test_430d_clasa_operatiunile_speciale_isi_scriu_sursa_lor():
    f = _functii_operatiuni()
    assert len(f) == 34 and all(f.values()), [r for r, s in f.items() if not s]
    vechi = {r for r, s in f.items() if re.search(r"repo_contabilitate\.nota_(facturi|banca|casa|salarii)_ciorna", s)}
    assert vechi <= SURSA_VECHE_PERMISA, sorted(vechi - SURSA_VECHE_PERMISA)
    # cele care scriu o notă fără factură legată trec prin nota_operatiune_ciorna (sursa „operatiuni”)
    assert sum(_cheama(s, "nota_operatiune_ciorna") for s in f.values()) >= 27


def test_430e_clasa_sumele_din_explicatii_trec_prin_bani():
    """O sumă citită din cerere sau din calcul, pusă în explicația notei, se formatează (10.000,00), nu se lipește ca număr brut."""
    bani_bruti = re.compile(r"""\{(?:corp|r)\[['"](?:brut|net|suma|valoare\w*|pret\w*|limita|deductibil|nedeductibil|neamortizat)['"]\]\}""")
    rele = {r: bani_bruti.findall(s) for r, s in _functii_operatiuni().items() if bani_bruti.search(s)}
    assert rele == {}, rele
