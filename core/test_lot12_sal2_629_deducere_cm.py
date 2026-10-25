# -*- coding: utf-8 -*-
"""[lotul 12, deficiența 629] În luna cu concediu medical, treapta deducerii personale se stabilește pe venitul brut lunar din salarii CU
indemnizația de incapacitate temporară de muncă (impozabilă) — aceeași cifră în calcul, pe stat / fluturaș și în D112.

Costin, 24.10.2026 (F5, Ionescu 10/2026): „treapta deducerii personale e stabilită pe 4.815,34, fără indemnizația CM brută (262)”.
Pe codul publicat (lotul 11) deducerea ieșea 649 (treapta lui 4.815,34); cu indemnizația (5.077,34) treapta e 519.

SURSE (locale, textul în vigoare pe 10/2026 — consolidarea din 08.08.2026 a Codului fiscal, `anaf_surse/cod_fiscal_227_2015_consolidat.txt`;
art.77 alin.(3)-(4) are ultima modificare prin OG 16/2022, art.76 alin.(1) neschimbat de OUG 8/2026):
- CF art.76 alin.(1): „Sunt considerate venituri din salarii toate veniturile în bani și/sau în natură obținute […] inclusiv
  indemnizațiile pentru incapacitate temporară de muncă acordate persoanelor care obțin venituri din salarii și asimilate salariilor.”
- CF art.77 alin.(3): „Deducerea personală de bază se acordă pentru persoanele fizice care au un venit lunar brut de până la 2.000 de lei
  peste nivelul salariului de bază minim brut pe țară […]”; alin.(4): „Pentru contribuabilii care realizează venituri brute lunare din
  salarii de până la nivelul prevăzut la alin. (3) inclusiv, deducerile personale de bază se stabilesc potrivit următorului tabel”.
- HG 1/2016 Titlul IV pct.12 alin.(1) lit.a) pct.(vii) (`anaf_surse/hg_1_2016_norme_cod_fiscal.txt`): veniturile brute din salarii
  cuprind „sumele primite în caz de incapacitate temporară de muncă”; pct.13 alin.(1): „Deducerea personală este stabilită în funcție de
  venitul brut lunar din salarii realizat la funcția de bază de către contribuabil și numărul de persoane aflate în întreținerea acestuia.”
- CF art.78 alin.(2) lit.a): impozitul lunar se aplică „asupra bazei de calcul determinată ca diferență între venitul net din salarii
  calculat prin deducerea din venitul brut a contribuțiilor sociale obligatorii aferente unei luni […] și […] (i) deducerea personală
  acordată pentru luna respectivă”; HG 1/2016 Titlul IV pct.16 alin.(3): „impozitul se calculează potrivit art. 78 din Codul fiscal,
  asupra veniturilor totale din luna respectivă”. Deci impozitul indemnizației NU e o regulă separată: o singură bază pe lună (salariu +
  indemnizație impozabilă − contribuțiile lor − deducerea), cum face D112; statul arată impozitul indemnizației ca diferența dintre
  impozitul declarat și cel din salariu (`stat_plata_api.stat_final`).

CNP-ul de test are cifra de control verificată (algoritmul din CLAUDE.md): 1800101410013.
"""
import ast
import datetime
import pathlib
from decimal import Decimal

import pytest

from core import d112, db as _db, salariati_api, salarizare, stat_plata_api
from core.common import Perioada
from core.test_lot11_s9_deducere_plafon import _setup, structura, unic

_SCHEMA = "test_lot12_sal2_629"
_RADACINA = pathlib.Path(__file__).resolve().parent.parent


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


# ---------------------------------------------------------------- calculul (pur), pe cifrele lui Ionescu (F5, 10/2026)

def test_def_629_treapta_deducerii_pe_salariu_plus_indemnizatie():
    """Ionescu, 10/2026: salariul lucrat 4.815,34, indemnizația CM cod 01 de 262 lei (CAS 66, CASS 26 -> net de contribuții 170).
    Venitul brut lunar = 5.077,34 -> treapta lui (salariul minim 4.325: 5.077,34 − 4.325 = 752,34 -> 16 trepte de 50 de lei, 20% − 8% =
    12%) -> 12% × 4.325 = 519. ROȘU pe codul publicat (lotul 11): 649, treapta lui 4.815,34 (490,34 peste salariul minim -> 10 trepte -> 15%)."""
    la = datetime.date(2026, 10, 1)
    sm, _ = salarizare.c.salariu_minim_luna(la)
    assert sm == Decimal("4325"), sm   # premisa cifrelor de mai jos (salariul minim al lunii, din registrul aplicației)
    cm = salarizare.cm_impozabil_luna([{"cod": "01", "brut_ang": 262, "brut_fnuass": 0}], la)
    assert cm == (Decimal("262"), Decimal("170")), cm   # CAS 25% = 65,50 -> 66, CASS 10% = 26,20 -> 26 (taxe_cm)
    r = salarizare.calcul_salariu(4815.34, la_data=la, cm_impozabil=cm)
    # CF art.76 alin.(1) „inclusiv indemnizațiile pentru incapacitate temporară de muncă” + CF art.77 alin.(4) „venituri brute lunare din
    # salarii”: treapta pe 4.815,34 + 262 = 5.077,34 -> ceil(752,34 / 50) = 16 trepte -> 20% − 16 × 0,5% = 12% din 4.325
    assert r["deducere"]["total"] == Decimal("519.00"), r["deducere"]
    fara = salarizare.calcul_salariu(4815.34, la_data=la, cm_impozabil=None)
    # fără indemnizație (forma veche): ceil(490,34 / 50) = 10 trepte -> 15% din 4.325 = 648,75 -> 649
    assert fara["deducere"]["total"] == Decimal("649.00"), fara["deducere"]


def test_def_629_indemnizatia_neimpozabila_nu_muta_treapta():
    """Cod 08 (maternitate) e neimpozabil (CF art.62 lit.c): nu intră în venitul brut al deducerii — `cm_impozabil_luna` întoarce None,
    deci treapta rămâne a salariului (INTERPRETARE CU TEMEI, scrisă la `salarizare._calcul_salariu_2018`)."""
    la = datetime.date(2026, 10, 1)
    assert salarizare.cm_impozabil_luna([{"cod": "08", "brut_ang": 0, "brut_fnuass": 2000}], la) is None


# ---------------------------------------------------------------- gardul clasei: niciun apelant nu uită indemnizația

def _apeluri_calcul_salariu():
    """(fișier, linie, are `cm_impozabil=`) pentru fiecare apel `calcul_salariu(...)` din codul aplicației (core/*.py fără teste, main.py)."""
    fisiere = [p for p in sorted((_RADACINA / "core").glob("*.py")) if not p.name.startswith("test_")] + [_RADACINA / "main.py"]
    out = []
    for p in fisiere:
        arbore = ast.parse(p.read_text(encoding="utf-8"), filename=str(p))
        for n in ast.walk(arbore):
            if isinstance(n, ast.Call):
                f = n.func
                nume = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else None)
                if nume == "calcul_salariu":
                    out.append((p.name, n.lineno, any(k.arg == "cm_impozabil" for k in n.keywords)))
    return out


def test_def_629_garda_fiecare_apel_spune_indemnizatia_lunii():
    """Fiecare apel `calcul_salariu` din aplicație numește `cm_impozabil` — indemnizația lunii, sau `None` cu motivul scris lângă apel
    (adeverința: salariul din contract; prăpastia salariului minim: simulare fără concedii). Un apelant nou care o uită pică aici: așa a
    rămas deducerea pe salariul lucrat până la 23.10.2026 (CF art.77 alin.(4) „venituri brute lunare din salarii”)."""
    apeluri = _apeluri_calcul_salariu()
    assert len(apeluri) >= 5, apeluri   # premisa: stat, D112, contare, adeverință, prăpastie — gardul vede apelurile
    lipsa = [(f, ln) for f, ln, are in apeluri if not are]
    assert not lipsa, "apeluri calcul_salariu fără cm_impozabil=: %s" % lipsa


# ---------------------------------------------------------------- statul, fluturașul și D112 (pe bază)

@pytest.fixture
def conn():
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            yield c
        finally:
            c.rollback()
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
            c.commit()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_def_629_stat_fluturas_si_d112_aceeasi_treapta(conn):
    """Salariat 7.000 lei, 09/2026 (22 de zile lucrătoare, salariul minim 4.325), certificat cod 01 pe 1–10.09.2026 (8 zile lucrătoare,
    media 240 lei/zi) salvat pe drumul aplicației: statul / fluturașul și D112 (E3_121, E1_41) au deducerea treptei lui salariu lucrat +
    indemnizație, iar baza impozitului din D112 (E3_14) = salariu + indemnizație − contribuții − deducere. DUK: valid."""
    with conn.cursor() as cur:
        _setup(cur, [{"cnp": "1800101410013", "nume": "IONESCU", "dn": "1980-06-01", "brut": 7000}], schema=_SCHEMA)
        cur.execute("SET LOCAL search_path TO %s, public" % _SCHEMA)
        cur.execute("SELECT id FROM salariati")
        sid = cur.fetchone()[0]
    salariati_api.salveaza_concediu(conn, sid, {
        "serie": "AB", "numar": "629", "cod": "01", "data_acordare": "2026-09-01", "data_inceput": "2026-09-01",
        "data_sfarsit": "2026-09-10", "loc_prescriere": 1, "zile_cm": 8, "venituri_6_luni": 30000, "zile_6_luni": 125,
        "an": 2026, "luna": 9})
    conn.commit()
    with conn.cursor() as cur:
        cur.execute("SET LOCAL search_path TO %s, public" % _SCHEMA)
        cur.execute("SELECT cod, brut_ang, brut_fnuass FROM concedii_medicale")
        cert = [{"cod": c, "brut_ang": a, "brut_fnuass": f} for c, a, f in cur.fetchall()]
    la = datetime.date(2026, 9, 1)
    st = stat_plata_api.stat_final(conn, _SCHEMA, 2026, 9)
    assert len(st) == 1, st
    r = st[0]
    cm_b, _cm_n = salarizare.cm_impozabil_luna(cert, la)
    assert cm_b > 0, cert
    # CF art.77 alin.(4) + HG 1/2016 Titlul IV pct.13 alin.(1): treapta pe venitul brut lunar = salariul lucrat + indemnizația impozabilă
    asteptat = salarizare.deducere_personala(Decimal(str(r["brut"])) + cm_b, la_data=la)["total"]
    pe_salariu = salarizare.deducere_personala(Decimal(str(r["brut"])), la_data=la)["total"]
    assert asteptat != pe_salariu, (asteptat, pe_salariu)    # premisa: cazul chiar mută treapta
    assert Decimal(str(r["deducere"])) == asteptat, (r["deducere"], asteptat, pe_salariu)
    assert stat_plata_api.randuri_deducere(r) == [("Deducere personală", float(asteptat))]   # rândul de pe fluturaș
    xml = d112.genereaza(conn, _SCHEMA, Perioada(an=2026, luna=9))[0]
    a = structura(xml)["1800101410013"]
    e3, e1, b4 = unic(a, "asiguratE3"), unic(a, "asiguratE1"), unic(a, "asiguratB4")
    # OPANAF 605/2026 anexa 1.2, E.1 rândul 4: „deduceri personale acordate persoanei fizice, potrivit legii”
    assert int(e3["E3_121"]) == int(e1["E1_41"]) == int(asteptat), (e3, e1, asteptat)
    # OPANAF 605/2026 anexa 2, E.3 rândul 8 „Total venit brut”: „venitul brut realizat […] suma totală a veniturilor din salarii”, CF
    # art.76 alin.(1) „inclusiv indemnizațiile pentru incapacitate temporară de muncă” -> salariul realizat (B2_5, fără sumă netaxabilă
    # la 7.000 lei) + indemnizația (B3_7) = B4_7; ROȘU înainte de 24.10.2026: 7.000 (salariul întreg, cu zilele de CM) + indemnizația
    b2, b3 = unic(a, "asiguratB2"), unic(a, "asiguratB3")
    assert int(e3["E3_8"]) == int(e1["E1_1"]) == int(b2["B2_5"]) + int(b3["B3_7"]) == int(b4["B4_7"]), (e3, e1, b2, b3, b4)
    # CF art.78 alin.(2) lit.a) + HG 1/2016 Titlul IV pct.16 alin.(3): o bază pe lună, pe veniturile totale (E3_8 = salariu + indemnizație)
    assert int(e3["E3_14"]) == int(e3["E3_8"]) - int(b4["B4_8"]) - int(b4["B4_6"]) - int(asteptat), (e3, b4)
    # statul reține exact impozitul declarat: din salariu (rândul statului) + din indemnizație (diferența, `stat_final`)
    assert Decimal(str(r["impozit"])) + Decimal(str(r["cm_impozit"])) == Decimal(e3["E3_15"]), (r["impozit"], r["cm_impozit"], e3)
    from core import duk
    if not duk.poate_valida("d112"):
        pytest.skip("DUK d112 indisponibil")
    rez = duk.valideaza(xml, "d112", an=2026, luna=9)
    assert rez["stare"] == "valid", rez
