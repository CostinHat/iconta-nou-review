# -*- coding: utf-8 -*-
"""GARD — comanda Costin 12.10.2026 seara (răspunsul la §6 al lotului 233–236, verbatim în DECIZII): C14, C15; C16 (găsită de Code).

C14 — „construiește F30 cap.XIX pentru S1005, după formularul ANAF 2025, cu listele de conturi tipărite pe fiecare rând.” CE ERA: S1005 nu
scria situația veniturilor și cheltuielilor (F30 cap.XIX, rd.167–236), iar DUK S1005 o compară cu F20 („F20_F30_2: F20_0012 (1000) =
F30_1672 (0)”, „F20_F30_8: F20_0082 (500) = F30_2352 (0)”) — orice S1005 cu activitate era respins. Listele și totalurile cap.XIX sunt
comparate cu formularul în `core/test_bilant_formular.py`; aici: XML-ul generat de aplicație e VALID pe validatorul instalat.

C15 — „Clasele 6/7 neînchise în 121: varianta (c) acum. Generarea bilanțului se oprește cu motivul «închide clasele 6/7 în 121 la 31.12»,
cu suma rezultatului.” TEMEI: OMFP 1802/2014, funcțiunea contului 121 — „În creditul contului 121 «Profit sau pierdere» se înregistrează: la
sfârșitul perioadei, soldul creditor al conturilor din clasa 7 (701 la 786)”; „În debitul … soldul debitor al conturilor de cheltuieli (601
la 698)”. Și clasa: rulajele claselor 6 / 7 citite FĂRĂ închiderea în 121 (altfel, după închiderea cerută, 711 / 712 pe sold ies 0 în
bilanț, iar 709 / 609 închise umflă veniturile / cheltuielile din D100, D101 și centrele de cost).

C16 — S1003 scria F30 rd.01 / 02 („unități care au înregistrat profit / pierdere”) din rd.08 / 09 ale contului de profit și pierdere S1003,
care sunt variația stocurilor (sold D) și producția de imobilizări — rândurile S1005. Profitul / pierderea netă S1003 sunt rd.69 / 70.
Schemă efemeră din `tenant_template.sql`, ROLLBACK."""
import datetime
import os
import re
from decimal import Decimal

import pytest
from psycopg2.extras import RealDictCursor

from core import bilant as b, bilant_api as ba, db as _db, tenant_provisioning as _tp

_SCHEMA = "ztest_bilant_f30"
_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def cur():
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as c:
                c.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                c.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                c.execute("SET search_path TO %s, public" % _SCHEMA)
                c.execute("INSERT INTO firma_profil (id, nume, cui) VALUES (1, 'PROBA SRL', '14399840') ON CONFLICT (id) DO NOTHING")
                c.execute("UPDATE firma_profil SET data_infiintare = '2025-01-10', reg_com = 'J40/1/2025', caen = '6202', adresa = 'Str 1', "
                          "oras = 'Buc', judet = 'B', declarant_nume = 'Popescu', declarant_prenume = 'Ion', "
                          "declarant_functie = 'ADMINISTRATOR', mare_contribuabil = false, forma_proprietate = '35' WHERE id = 1")  # [lotul 10, C69] antetul bilanțului: codTT, bifaMC/codJJ, codPP, nume_admin — din Date firmă
                yield c
        finally:
            conn.rollback()


def _nota(c, zi, debit, credit, suma):
    c.execute("INSERT INTO inregistrari (data, status, sursa, descriere) VALUES (%s, 'validata', 't', 'Probă') RETURNING id", (zi,))
    c.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, %s, %s, %s)",
              (c.fetchone()["id"], debit, credit, suma))


_31_12 = datetime.date(2025, 12, 31)


def _anul_2025(c):
    """Firma înființată în 2025 (primul exercițiu — coloana „An precedent” e legal goală): capital 1.000, vânzări 1.000 cu reducere 100,
    servicii 200, chirie 40, producție în curs 50 (711), provizion 30 reluat 10."""
    for d, cr, s in (("5121", "1012", 1000), ("4111", "704", 1000), ("709", "4111", 100), ("628", "401", 200), ("6123", "401", 40),
                     ("331", "711", 50), ("6812", "1518", 30), ("1518", "7812", 10), ("5121", "4111", 900), ("401", "5121", 240)):
        _nota(c, datetime.date(2025, 6, 30), d, cr, Decimal(s))


def _inchide(c):
    """Nota de închidere la 31.12: 121 = cheltuielile, veniturile = 121 (OMFP 1802/2014, contul 121)."""
    for cont, sens in (("704", "c"), ("711", "c"), ("7812", "c"), ("709", "d"), ("628", "d"), ("6123", "d"), ("6812", "d")):
        sold = ba.sold_la(c, _SCHEMA, _31_12)[cont]
        if sens == "c":
            _nota(c, _31_12, cont, "121", sold[1])
        else:
            _nota(c, _31_12, "121", cont, sold[0])


def test_def_c15_clasele_6_7_neinchise_opresc_bilantul_cu_suma_rezultatului(cur):
    """C15: veniturile și cheltuielile anului cu sold la 31.12 -> refuz „închide clasele 6/7 în 121 la 31.12.2025”, cu rezultatul (profit
    1.000 − 100 + 50 + 10 − 200 − 40 − 30 = 690,00 lei) și conturile; după nota de închidere — bilanțul se generează, profitul e în 121
    (F10 rd.43 = 690), iar F20 rămâne cel din operațiuni (rd.02 = 711 50 + 7812 nu; închiderea nu e rulaj). MUTAȚII: verificarea scoasă din
    `coloana_curenta_f10` -> pică; închiderea numărată în `_rulaje_67` -> F20 rd.02 = 0 -> pică."""
    _anul_2025(cur)
    with pytest.raises(ValueError) as e:
        ba.coloanele(cur, _SCHEMA, "s1005", 2025, [])
    m = str(e.value)
    assert m.startswith("Bilanțul pe 2025 nu se poate genera: închide clasele 6/7 în 121 la 31.12.2025. Rezultatul de închis: profit "
                        "690,00 lei"), m
    assert re.findall(r"• (\d+) sold (debitor|creditor) ([\d.,]+)", m) == [
        ("6123", "debitor", "40,00"), ("628", "debitor", "200,00"), ("6812", "debitor", "30,00"), ("704", "creditor", "1.000,00"),
        ("709", "debitor", "100,00"), ("711", "creditor", "50,00"), ("7812", "creditor", "10,00")], m
    _inchide(cur)
    f10p, f10c, f20p, f30p = ba.coloanele(cur, _SCHEMA, "s1005", 2025, [])
    assert (f10c[43], f10c[44], f10c[49]) == (690, 0, 1690), f10c
    rl = ba._rulaje_67(cur, _SCHEMA, 2025)
    assert rl["711"] == (Decimal(0), Decimal(50)) and rl["704"] == (Decimal(0), Decimal(1000)), rl
    f20 = b.f20_din_rulaje(rl)
    assert (f20[1], f20[2], f20[8]) == (900, 50, 690), f20


def test_def_c14_s1005_cu_activitate_scrie_cap_xix_si_e_valid_pe_duk(cur):
    """C14: S1005 al unei firme cu activitate (anul de mai sus, închis) are F30 cap.XIX pe rândurile formularului — cifra de afaceri rd.167
    = 704 − 709 = 900, sold C 711 rd.173 = 50, chiria 6123 la rd.198a (331) și „din care” 198d (334), provizioanele rd.205 = 30 − 10,
    profitul net rd.235 = 690 = F20 rd.08 — și e VALID pe DUK S1005. Înainte: „F20_F30_2: F20_0012 (900) = F30_1672 (0)”. MUTAȚII: cap.XIX
    nescris în XML -> DUK respinge -> pică; 612 numărat și la rd.198 -> rd.197 / 235 diferă de F20 -> DUK respinge -> pică."""
    from core import duk
    _anul_2025(cur)
    _inchide(cur)
    xml, av = ba.genereaza(cur.connection, _SCHEMA, 2025)
    f30 = {int(r): int(v) for r, v in re.findall(r'\bF30_(\d{3})2="(-?\d+)"', xml)}
    assert {k: f30.get(k) for k in (167, 168, 170, 173, 182, 197, 198, 205, 208, 230, 235, 331, 334)} == {
        167: 900, 168: 1000, 170: 100, 173: 50, 182: 950, 197: 240, 198: 200, 205: 20, 208: 260, 230: 690, 235: 690, 331: 40, 334: 40}, f30
    assert re.findall(r'\bF20_0082="(\d+)"', xml) == ["690"] and re.findall(r'\bF30_0012="(\d+)"', xml) == ["690"], xml[:800]
    v = duk.valideaza(xml, "s1005", an=2025, luna=12)
    assert v["stare"] == "valid", v


def test_def_c16_s1003_unitatile_cu_profit_sunt_din_profitul_net():
    """C16: F30 rd.01 / 02 ale S1003 = profitul / pierderea netă (rd.69 / 70), nu rd.08 / 09 (variația stocurilor sold D, producția de
    imobilizări). MUTAȚIE: `rezultat` scos din `xml_s1003` -> F30_0012 = rd.08 -> pică."""
    f20 = b.f20_complet_din_rulaje({"704": (0, 5000), "641": (1000, 0), "711": (300, 0), "721": (0, 200)})
    assert (f20[8], f20[9], f20[69], f20[70]) == (300, 200, 3900, 0), f20
    x = b.xml_s1003({"cui_numeric": 14399840, "nume": "Z", "reg_com": "J40/1/2020", "caen": "6202", "cod_judet": 40, "mare_contribuabil": False,
                     "forma_proprietate": "35", "declarant_nume": "Pop", "declarant_prenume": "Ion"}, 2025, {}, {}, {}, f20)  # [lotul 10, C69] antetul bilanțului: codTT, bifaMC/codJJ, codPP, nume_admin — din Date firmă
    assert dict(((int(r), int(c)), int(v)) for r, c, v in re.findall(r'\bF30_00(\d)(\d)="(\d+)"', x)) == {
        (1, 1): 1, (1, 2): 3900, (2, 1): 0, (2, 2): 0, (3, 1): 0, (3, 2): 0}, x


def test_c15_inchiderea_in_121_nu_e_rulaj_in_nicio_interogare_pe_clasele_6_7():
    """C15, clasa: fiecare interogare SQL din aplicație care adună rulaje pe clasele 6 / 7 (`cont_debit / cont_credit LIKE '6…' / '7…'`)
    exclude închiderea în 121 — altfel, după închiderea cerută de bilanț, 709 închis umflă veniturile (D100, D101), 609 cheltuielile, iar
    centrele de cost văd anul de două ori. Locurile găsite: D100 (repo + reconcilierea), D101 (repo + reconcilierea), centrele de cost;
    bilanțul (`bilant_api._rulaje_67`) o face în Python — probat de testul C15 de mai sus. Un loc nou fără excludere pică aici.
    MUTAȚIE: excluderea scoasă din `repo_d100.select_inregistrari_linii` -> pică."""
    rele = []
    for f in sorted(os.listdir(os.path.join(_RAD, "core"))):
        if not f.endswith(".py") or f.startswith("test_"):
            continue
        t = re.sub(r"(?m)^\s*#.*$", "", open(os.path.join(_RAD, "core", f), encoding="utf-8").read())   # comentariile nu sunt SQL
        for seg in re.split(r"\bSELECT\b", t)[1:]:
            if re.search(r"cont_(?:debit|credit)\s+LIKE\s+'[67]", seg) and "NOT LIKE '121" not in seg:
                rele.append((f, seg[:80]))
    assert not rele, rele


def test_c15_d101_fara_inchiderea_in_121(cur):
    """C15 pe D101: veniturile din exploatare ale anului = 704 1.000 + 711 50 + 7812 10 = 1.060 — nimic din închidere (nota 121 = 709
    creditează 709 cu 100 și s-ar fi adunat la venituri). MUTAȚIE: excluderea scoasă -> 1.160 -> pică.
    [lotul 10, deficiența 425] baza D101 se citește acum din `bilant_api.rulaje_67` (note + rulajele preluate), prin
    `d101.rulaje_fereastra` — aceeași excludere a închiderii ca F20, o singură sursă (fostul `repo_d101.select_inregistrari_linii`)."""
    from core import d101
    _anul_2025(cur)
    _inchide(cur)
    r = d101.rulaje_fereastra(cur, _SCHEMA, datetime.date(2025, 1, 1), datetime.date(2026, 1, 1))
    assert (r["ven_expl"], r["chelt_expl"]) == (1060, 270), r
