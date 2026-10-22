# -*- coding: utf-8 -*-
"""[lotul 11] Fișa partenerului (decizia Costin 10.3 pct.4) și numele de la ANAF față de fișă (deficiența 444).

Decizia 10.3, verbatim în DECIZII „Comanda 10.3”: „Localitatea și județul la PF și la firmele neînregistrate se completează în fișa
partenerului; refuzul declarației trimite direct acolo.” Comanda 11.1 pct.20 (444): „când numele de la ANAF diferă de fișa partenerului,
se spune și se propune actualizarea.”

Temeiul câmpurilor cerute (schema / structura ANAF, citate la sursa lor):
  D406 — anaf_surse/d406_schema_anaf.xlsx, „5. Structures”: S.C.3 Address „Mandatory … 1..*”, S.AD.5 City „Mandatory … 1”;
  D394 — anaf_surse/d394_struct_anaf.txt pct.222: „judP Judet beneficiar/ furnizor/ prestator C(2) Nomenclator … Obligatoriu pt
  tip_partener=2 și cuiP=null și taraP=RO”.
Fixturile pe bază: schemă efemeră din `tenant_template.sql`, ROLLBACK; CUI 2864518 (cifra de control verificată în
`test_lot10_c69_d406_parteneri.py::test_fixtura_e_valida`). ANAF simulat (core/conftest.py), niciodată real.
MUTAȚII (unit): `tinta_fisa_partener` scos din refuzul D406 -> `test_D406_refuzul_trimite_la_fisa_partenerului` pică; `nume_diferit`
întoarce False -> `test_numele_diferit_de_anaf` pică; fișa scoasă din `sql_camp_fisa` -> `test_declaratia_citeste_judetul_din_fisa` pică.
"""
import io

import pytest

from core import clienti_api as ca, d406
from core.erori import DateInvalide, RefuzGenerare


def test_cheia_partenerului():
    assert ca.cheie_partener("RO 2864518", "ALTEX") == ca.cheie_partener("2864518", "Altex Romania") == "cui-2864518"
    assert ca.cheie_partener("DE123456789", "X GmbH") == "cui-DE123456789"     # codul din alt stat rămâne cu prefixul lui (CF art.318 alin.(1))
    assert ca.cheie_partener("", "Popescu Ion") == ca.cheie_partener(None, "POPESCU  ION") == "nume-POPESCU_ION"
    assert ca.cheie_partener("", "Ștefănescu Ana") == "nume-STEFANESCU_ANA"
    assert ca.cheie_partener(None, "") is None


def test_numele_diferit_de_anaf():
    assert not ca.nume_diferit("Altex Romania S.R.L.", "ALTEX ROMANIA SRL")      # puncte / majuscule nu sunt o diferență
    assert not ca.nume_diferit("FISCALOS  ICONTA SRL", "FISCALOS ICONTA S.R.L.")
    assert ca.nume_diferit("ALTEX SRL", "ALTEX ROMANIA SRL")                     # alt nume = diferență, se spune
    assert not ca.nume_diferit("", "ALTEX ROMANIA SRL") and not ca.nume_diferit("ALTEX", None)   # gol = nimic de propus


def test_judetul_fisei_e_codul_din_lista():
    assert ca._judet_cod("cj") == "CJ" and ca._judet_cod("Cluj") == "CJ" and ca._judet_cod("București") == "B"
    assert ca._judet_cod("") is None
    with pytest.raises(ValueError) as ei:
        ca._judet_cod("Atlantida")
    assert ei.value.args == ("Județul 'Atlantida' nu e în listă: alege-l din listă (ex. Cluj, București).",), ei.value.args


def test_tinta_refuzului_d406():
    cl = [d406.Partener(id="002864518", nume="ALTEX ROMANIA SRL", cui="2864518")]
    assert d406.tinta_fisa_partener([("ALTEX ROMANIA SRL", "002864518", ["FV1"])], cl, [], []) == (
        "clienti", "partener:cui-2864518:oras")
    assert d406.tinta_fisa_partener([("POPESCU ION", "04POPESCUION", ["FC1"])], cl, [], []) == (
        "furnizori", "partener:nume-POPESCU_ION:oras")
    assert d406.tinta_fisa_partener([], cl, [], []) == (None, None)


# ── pe bază: schemă efemeră, ROLLBACK ───────────────────────────────────────────────────────────────────────────────────────────────
def _db_ok():
    try:
        from core import db
        db.init_pool()
        with db.get_conn():
            return True
    except Exception:
        return False


_SCHEMA = "ztest_l11p_parteneri"
IBAN = "RO59BTRLRONCRT0C69TEST01"


@pytest.fixture
def conn():
    from core import db, tenant_provisioning as tp
    db.init_pool()
    with db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(tp.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                cur.execute("SET LOCAL search_path TO %s, public" % _SCHEMA)
                cur.execute("INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, caen, banca, iban, telefon, declarant_nume, "
                            "declarant_prenume, declarant_functie, platitor_tva, tip_decont, regim_fiscal, baza_contabila) VALUES "
                            "(1, 'FIRMA L11 SRL', '14399840', 'Str. Probei 9', 'Cluj-Napoca', 'CJ', '6920', 'BT', %s, '0264111222', "
                            "'POPESCU', 'ION', 'ADMINISTRATOR', true, 'L', 'real', 'A')", (IBAN,))
                # vânzare către o persoană fizică fără cod, fără localitate pe factură; cumpărare (borderou) de la alta, cu localitatea scrisă
                for nr, dir_, tip, cui, nume, oras, jud in (("FV1", "emisa", "factura", "", "POPESCU ION", None, None),
                                                            ("BA-1", "primita", "borderou", "", "MARIA IONESCU", "Cluj-Napoca", "CJ"),
                                                            ("FV2", "emisa", "factura", "RO2864518", "ALTEX ROMANIA SRL", "Pantelimon", "IF")):
                    cur.execute("INSERT INTO facturi (numar, data_emitere, directie, tip, total, tva, tert_cui, tert_nume, tert_oras, tert_judet, "
                                "status) VALUES (%s, '2026-06-10', %s, %s, 121, 21, %s, %s, %s, %s, %s) RETURNING id",
                                (nr, dir_, tip, cui, nume, oras, jud, dir_))
                    fid = cur.fetchone()[0]
                    cur.execute("INSERT INTO factura_linii (factura_id, descriere, um, cantitate, pret_unitar, cota_tva) "
                                "VALUES (%s, 'Marfa', 'buc', 1, 100, 21)", (fid,))
            yield c
        finally:
            c.rollback()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_partenerii_fara_fisa_inclusiv_persoanele_fizice(conn):
    cl = {p["cheie"]: p for p in ca.parteneri_fara_fisa(conn, "clienti")}
    assert set(cl) == {"nume-POPESCU_ION", "cui-2864518"}, cl                      # PF fără cod: după nume (decizia 10.3)
    assert (cl["cui-2864518"]["oras"], cl["cui-2864518"]["judet"]) == ("Pantelimon", "IF")   # propunerea de pe factură
    fz = {p["cheie"]: p for p in ca.parteneri_fara_fisa(conn, "furnizori")}
    assert set(fz) == {"nume-MARIA_IONESCU"} and fz["nume-MARIA_IONESCU"]["facturi"] == 1, fz   # borderoul de achiziție
    # fișa creată: partenerul nu mai e „fără fișă”
    ca.creeaza_client(conn, "Popescu Ion", oras="Sibiu", judet="Sibiu")
    assert "nume-POPESCU_ION" not in {p["cheie"] for p in ca.parteneri_fara_fisa(conn, "clienti")}


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_fisa_furnizorului_cu_cui_fara_ro_si_dublura_numita(conn):
    from core import chei_unice
    r = ca.creeaza_furnizor(conn, "ALTEX ROMANIA SRL", cui="RO 2864518", oras="Pantelimon", judet="Ilfov")
    f = ca.detalii_furnizor(conn, r["furnizor_id"])
    assert (f["cui"], f["judet"]) == ("2864518", "IF"), f                  # decizia 10.3: fără „RO” / spații; județul = codul listei
    with pytest.raises(chei_unice.CheieDublata) as ei:
        ca.creeaza_furnizor(conn, "ALTEX", cui="2864518")                  # același CUI, scris altfel -> refuz numit, nu 500
    assert ei.value.args == ("Există deja furnizorul ALTEX ROMANIA SRL cu CUI-ul 2864518 (în lista Furnizori): deschide fișa existentă "
                             "și schimbă acolo ce ai de schimbat.",), ei.value.args
    ca.actualizeaza_furnizor(conn, r["furnizor_id"], oras="", judet="")   # golirea e o alegere
    assert (ca.detalii_furnizor(conn, r["furnizor_id"])["oras"], ca.detalii_furnizor(conn, r["furnizor_id"])["judet"]) == (None, None)
    # [lotul 11, 440] fișa se judecă întreagă (`core.erori.ErorileFormularului`): refuzul e `DateInvalide`, cu fiecare câmp numit
    with pytest.raises(DateInvalide) as ei:
        ca.actualizeaza_furnizor(conn, r["furnizor_id"], judet="Atlantida")
    assert [c["camp"] for c in ei.value.detaliu["erori_campuri"]] == ["judet"], ei.value.detaliu


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_compararea_cu_anaf_numeste_fisa_diferita(conn):
    ca.creeaza_client(conn, "ALTEX SRL", cui="2864518")
    with conn.cursor() as cur:
        r = ca.compara_cu_anaf(cur, "RO2864518", "ALTEX ROMANIA SRL")
    assert r["nume_diferit"] is True and [f["nume"] for f in r["fise"]] == ["ALTEX SRL"], r
    assert r["mesaj_nume"] == ("Numele de la ANAF (ALTEX ROMANIA SRL) diferă de fișa clientului: ALTEX SRL. Actualizează fișa cu numele "
                               "de la ANAF, dacă e cel corect."), r
    with conn.cursor() as cur:
        assert ca.compara_cu_anaf(cur, "2864518", "ALTEX ROMANIA S.R.L.")["nume_diferit"] is True
        assert ca.compara_cu_anaf(cur, "2864518", "Altex S.R.L")["nume_diferit"] is False      # aceeași denumire, scrisă altfel


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_declaratia_citeste_judetul_din_fisa(conn):
    """„declarațiile citesc din fișă când factura nu are” — subinterogarea comună (`sql_camp_fisa`): factura fără județ -> fișa."""
    ca.creeaza_client(conn, "POPESCU ION", oras="Sibiu", judet="SB")
    with conn.cursor() as cur:
        cur.execute("SELECT numar, COALESCE(NULLIF(btrim(f.tert_judet), ''), " + ca.sql_camp_fisa("judet") + "), "
                    "COALESCE(NULLIF(btrim(f.tert_oras), ''), " + ca.sql_camp_fisa("oras") + ") FROM facturi f ORDER BY numar")
        assert cur.fetchall() == [("BA-1", "CJ", "Cluj-Napoca"), ("FV1", "SB", "Sibiu"), ("FV2", "IF", "Pantelimon")]


def _oras_client(xml, customer_id):
    """`City` din adresa clientului `customer_id` (MasterFiles/Customers/Customer, CompanyStructure/Address/City), din arborele XML
    — nu „<City>Sibiu</City> apare undeva în fișier” (core/test_garzi_pe_text.py)."""
    import xml.etree.ElementTree as _ET
    rad = _ET.fromstring(xml.encode("utf-8") if xml.lstrip().startswith("<?xml") else xml)
    for e in rad.iter():
        e.tag = e.tag.rsplit("}", 1)[-1]
    return [c.findtext("CompanyStructure/Address/City") for c in rad.iter("Customer") if c.findtext("CustomerID") == customer_id]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_D406_refuzul_trimite_la_fisa_partenerului_apoi_o_citeste(conn):
    """D406: PF fără localitate -> refuzul trimite la fișa ei (Clienți, câmpul localității); completată în fișă -> D406 o ia de acolo."""
    with pytest.raises(RefuzGenerare) as ei:
        d406.genereaza(conn, _SCHEMA, 2026, 6)
    d = ei.value.detaliu()
    assert (d["ecran"], d["camp_ecran"]) == ("clienti", "partener:nume-POPESCU_ION:oras"), d   # decizia 10.3: „trimite direct acolo”
    assert d["mesaj"] == ("D406 nu se poate genera: lipsește localitatea pentru 1 partener — D406 cere adresa fiecărui partener "
                          "(localitatea e obligatorie). POPESCU ION (facturile FV1). Completează localitatea în fișa partenerului "
                          "(Clienți / Furnizori) sau pe factura lui, apoi generează din nou."), d["mesaj"]
    ca.creeaza_client(conn, "POPESCU ION", oras="Sibiu", judet="SB")    # pe calea ecranului (POST /clienti)
    xml, _res = d406.genereaza(conn, _SCHEMA, 2026, 6)
    assert _oras_client(xml, "04POPESCUION") == ["Sibiu"], xml[:3000]   # S.AD.5 City — din fișa partenerului
