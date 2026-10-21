# -*- coding: utf-8 -*-
"""[lotul 10, deficiența C69] D406: localitatea partenerilor și contul bancar al firmei — fără valori inventate.

Ce era (core/d406.py, înainte): Customers / Suppliers `<City>` = `oras or "-"`; pe fiecare factură `<BillingAddress><City>-</City>
<Country>RO</Country>` (și pentru partenerul german); firma fără IBAN se oprea fără nicio cale pentru „nu are cont bancar”.

Deciziile Costin 20.10.2026 (verbatim în DECIZII „Lotul 10, C69 … deciziile lui Costin”):
  pct.1 „Completez din ANAF” — „pentru partenerii cu CUI românesc, localitatea se aduce automat din ANAF la generare; se blochează
  numai ce rămâne necompletat”;
  pct.3 „Varianta 1, cu o condiție: dacă firma are bifa «nu are cont bancar», dar are rulaj sau sold pe 512x în perioadă, D406 se
  oprește și spune contradicția.”
Sursa: anaf_surse/d406_schema_anaf.xlsx, foaia „5. Structures”: S.C.3 Address „Mandatory … 1..*”, S.AD.5 City „Mandatory … 1”,
S.AD.8 Country „Default Value ”RO” for Romania”, S.I.25 / S.I.28 BillingAddress „Mandatory … 1”, S.BA.2 BankAccountNumber „Pentru
companiile care nu detin cont bancar se va inscrie in sectiunea Header, subsectiunea CompanyHeaderStructure, la campul
BankAccountNumber : "Fara cont bancar"”; XSD /opt/duk/saft/saft.xsd BankAccountStructure = choice IBANNumber | BankAccountNumber.
ANAF e simulat (`interogare=`), niciodată real (core/conftest.py). Fixturile: schemă efemeră, ROLLBACK; CUI-urile 14399840 / 2864518
(cifra de control verificată în testul fixturii), IBAN RO59BTRLRONCRT0C69TEST01 (mod-97 verificat).
"""
import re
import io
import xml.etree.ElementTree as ET

import pytest

from core import anaf_api, d406
from core.erori import RefuzGenerare

LOCALITATI_ANAF_REAL = True   # modulul probează `aduce_localitati` cu ANAF simulat prin `interogare=` (core/conftest.py)

IBAN = "RO59BTRLRONCRT0C69TEST01"
PROF = {"cui": "14399840", "nume": "FIRMA C69 SRL", "platitor_tva": True, "tip_decont": "L", "baza_contabila": "A",
        "adresa": "Str. Probei 9", "oras": "Cluj-Napoca", "telefon": "0264111222", "iban": IBAN,
        "declarant_nume": "POPESCU", "declarant_prenume": "ION"}


def _texte(xml, tag, sectiune=None):
    """Textele elementelor `tag` (numele local), din XML-ul PARSAT; cu `sectiune`, numai sub elementele cu acel nume local."""
    rad = ET.fromstring(xml.encode("utf-8"))
    local = lambda e: e.tag.rsplit("}", 1)[-1]   # noqa: E731
    radacini = [rad] if sectiune is None else [e for e in rad.iter() if local(e) == sectiune]
    return [e.text or "" for r in radacini for e in r.iter() if local(e) == tag]


def _intre(mesaj, dupa, inainte):
    """Fragmentul refuzului dintre `dupa` și `inainte` — lista numită de generator (partenerii / conturile), comparată întreagă."""
    return mesaj.split(dupa, 1)[1].split(inainte, 1)[0]


def test_fixtura_e_valida():
    from core.identitate import valideaza_cui
    from core.salariati_api import iban_valid
    assert valideaza_cui("14399840")[0] and valideaza_cui("2864518")[0] and iban_valid(IBAN)


# ── localitatea partenerului ────────────────────────────────────────────────────────────────────────────────────────────────────────
def _anaf_simulat(raspunsuri):
    cerute = []

    def interogare(lista):
        cerute.append(list(lista))
        return [dict(raspunsuri[c], cui=c, gasit=True) if c in raspunsuri else {"cui": c, "gasit": False} for c in lista]
    return interogare, cerute


def test_tara_partenerului_din_identitate():
    assert d406.tara_partener("01DE123456789") == "DE"      # S.AD.8 Country ISO 3166 — partenerul UE (era RO pe factură)
    assert d406.tara_partener("01EL123456789") == "GR"      # prefixul de TVA EL -> țara GR (ISO 3166)
    assert d406.tara_partener("0014399840") == "RO"         # S.AD.8 „Valoare implicită ”RO” pentru România”
    assert d406.tara_partener("04POPESCUION", "IT") == "IT"  # țara scrisă pe factură, la partenerul fără cod


def test_aduce_localitati_din_anaf_in_cache_fara_retea_in_generator():
    interogare, cerute = _anaf_simulat({"2864518": {"localitate": "Pantelimon", "judet": "IF"}})
    assert anaf_api.localitate_din_cache("2864518") is None
    assert anaf_api.aduce_localitati(["RO2864518", "14399841"], interogare=interogare) == 1   # doar cine e găsit cu localitate
    assert cerute == [["14399841", "2864518"]]                                                # un singur apel, în lot
    assert anaf_api.localitate_din_cache("RO 2864518") == {"localitate": "Pantelimon", "judet": "IF"}
    anaf_api.aduce_localitati(["2864518"], interogare=interogare)
    assert len(cerute) == 1                                                                    # din cache, fără al doilea apel


def test_completarea_localitatilor_si_lista_celor_ramase():
    interogare, _c = _anaf_simulat({"2864518": {"localitate": "Pantelimon", "judet": "IF"}})
    anaf_api.aduce_localitati(["2864518"], interogare=interogare)
    cl = [d406.Partener(id="002864518", nume="ALTEX ROMANIA SRL", cui="2864518"),         # fără localitate: ANAF
          d406.Partener(id="0014399840", nume="ALFA SRL", cui="14399840"),                # din nomenclator / facturi (`locale`)
          d406.Partener(id="04POPESCUION", nume="POPESCU ION", cui="")]                   # PF fără cod: rămâne fără
    fv = [d406.Factura(nr="F1", data=None, partener_id="04POPESCUION", partener_nume="POPESCU ION"),
          d406.Factura(nr="F2", data=None, partener_id="002864518", partener_nume="ALTEX ROMANIA SRL", oras="Voluntari")]
    d406.completeaza_localitati(cl, [], fv, {"0014399840": "Iasi"})
    assert [p.oras for p in cl] == ["Pantelimon", "Iasi", ""]     # S.AD.5 City: ANAF / scrisă de contabil / nimic inventat
    assert fv[1].oras == "Voluntari"                               # factura își păstrează localitatea ei
    assert d406.parteneri_fara_localitate(cl, [], fv) == [("POPESCU ION", "04POPESCUION", ["F1"])]


def test_niciun_drum_nu_scrie_liniuta():
    p = d406.Partener(id="0014399840", nume="ALFA SRL", cui="14399840")
    res = d406.construieste(PROF, 2026, 6, [], [p], [])
    with pytest.raises(ValueError):          # S.AD.5 City „Mandatory” — fără localitate, `build_xml` nu scrie „-” (era `oras or "-"`)
        d406.build_xml(res)
    p.oras = "Iasi"
    assert _texte(d406.build_xml(res), "City", "Customers") == ["Iasi"]      # S.AD.5 City — localitatea partenerului, nu „-”


# ── pe bază: schemă efemeră, ROLLBACK ───────────────────────────────────────────────────────────────────────────────────────────────
def _db_ok():
    try:
        from core import db
        db.init_pool()
        with db.get_conn():
            return True
    except Exception:
        return False


_SCHEMA = "ztest_c69_d406_parteneri"


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
                            "(1, 'FIRMA C69 SRL', '14399840', 'Str. Probei 9', 'Cluj-Napoca', 'CJ', '6920', 'BT', %s, '0264111222', "
                            "'POPESCU', 'ION', 'ADMINISTRATOR', true, 'L', 'real', 'A')", (IBAN,))
                # vânzare către ALTEX (CUI românesc, fără localitate pe factură) și cumpărare de la o persoană fizică fără localitate
                for nr, dir_, cui, nume in (("FV1", "emisa", "RO2864518", "ALTEX ROMANIA SRL"), ("FC1", "primita", "", "POPESCU ION")):
                    cur.execute("INSERT INTO facturi (numar, data_emitere, directie, total, tva, tert_cui, tert_nume, status) "
                                "VALUES (%s, '2026-06-10', %s, 121, 21, %s, %s, %s) RETURNING id", (nr, dir_, cui, nume, dir_))
                    fid = cur.fetchone()[0]
                    cur.execute("INSERT INTO factura_linii (factura_id, descriere, um, cantitate, pret_unitar, cota_tva) "
                                "VALUES (%s, 'Marfa', 'buc', 1, 100, 21)", (fid,))
            yield c
        finally:
            c.rollback()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_D406_refuza_partenerii_ramasi_fara_localitate_numindu_i(conn):
    with pytest.raises(RefuzGenerare) as ei:
        d406.genereaza(conn, _SCHEMA, 2026, 6)
    m = str(ei.value)
    # lista partenerilor, cu facturile lor — întreagă (S.AD.5 City „Mandatory … 1”)
    assert _intre(m, "(localitatea e obligatorie). ", ". Pentru cei") == "ALTEX ROMANIA SRL (facturile FV1); POPESCU ION (facturile FC1)", m
    assert _intre(m, "Pentru cei cu CUI românesc, ", ".") == "ANAF n-a dat localitatea (nu a răspuns sau n-are adresa lor)", m         # ANAF simulat: n-a răspuns


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_D406_ia_localitatea_din_anaf_si_de_pe_factura(conn):
    interogare, cerute = _anaf_simulat({"2864518": {"localitate": "Pantelimon", "judet": "IF"}})
    with conn.cursor() as cur:
        cur.execute("UPDATE facturi SET tert_oras = 'Sibiu' WHERE numar = 'FC1'")   # localitatea scrisă de contabil pe factura PF
        import psycopg2.extras as _E
        with conn.cursor(cursor_factory=_E.RealDictCursor) as c2:
            from core import repo_d406
            de_cerut = d406.cuiuri_de_cerut_anaf(repo_d406.parteneri_si_localitati(c2))
    assert de_cerut == ["2864518"]                     # numai CUI-ul românesc fără localitate scrisă se cere ANAF-ului
    anaf_api.aduce_localitati(de_cerut, interogare=interogare)
    xml, _res = d406.genereaza(conn, _SCHEMA, 2026, 6)
    assert _texte(xml, "City", "Customers") == ["Pantelimon"]     # S.C.3 / S.AD.5 — din ANAF (domiciliul fiscal)
    assert _texte(xml, "City", "Suppliers") == ["Sibiu"]          # de pe factura persoanei fizice
    assert _texte(xml, "City", "BillingAddress") == ["Pantelimon", "Sibiu"]   # S.I.25 / S.I.28 BillingAddress — nu „-”
    assert "-" not in _texte(xml, "City")                         # nicio localitate inventată, nicăieri în fișier


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_D406_cu_localitatile_partenerilor_e_valid_pe_DUK(conn):
    from core import duk
    with conn.cursor() as cur:
        cur.execute("UPDATE facturi SET tert_oras = CASE numar WHEN 'FV1' THEN 'Pantelimon' ELSE 'Sibiu' END")
    xml, _res = d406.genereaza(conn, _SCHEMA, 2026, 6)
    v = duk.valideaza(xml, "d406", an=2026, luna=6)
    if v.get("stare") == "gri":
        pytest.skip("validator SAF-T indisponibil: %s" % v.get("temei"))
    assert v.get("stare") == "valid", v


def test_prefetch_inaintea_tranzactiei_numai_pentru_d406_si_d394(monkeypatch):
    """`uc_declaratii.aduce_localitati_parteneri`: citirea scurtă se ÎNCHIDE, apoi ANAF cu pool-ul liber (ca `_aduce_cursurile`); la
    celelalte declarații nu cheamă nimic; ANAF jos nu ridică (refuzul generatorului numește partenerii)."""
    import contextlib
    from core import uc_declaratii, repo_d406
    ev = []

    @contextlib.contextmanager
    def _conn(schema=None):
        ev.append("deschis")
        yield type("C", (), {"cursor": lambda self, **k: contextlib.nullcontext(None)})()
        ev.append("inchis")
    monkeypatch.setattr(uc_declaratii.db, "get_conn", _conn)
    monkeypatch.setattr(repo_d406, "parteneri_si_localitati", lambda cur: [
        {"cui": "RO2864518", "nume": "ALTEX", "oras": None}, {"cui": "14399840", "nume": "ALFA", "oras": "Iasi"},
        {"cui": "", "nume": "POPESCU ION", "oras": None}])
    monkeypatch.setattr(anaf_api, "aduce_localitati", lambda lista, interogare=None: ev.append(("anaf", list(lista))) or 0)
    uc_declaratii.aduce_localitati_parteneri("s", "d300")
    assert ev == []
    uc_declaratii.aduce_localitati_parteneri("s", "d406")
    assert ev == ["deschis", "inchis", ("anaf", ["2864518"])]   # ANAF după închiderea conexiunii; numai CUI-ul fără localitate
    monkeypatch.setattr(anaf_api, "aduce_localitati", lambda lista, interogare=None: (_ for _ in ()).throw(OSError("ANAF jos")))
    uc_declaratii.aduce_localitati_parteneri("s", "d394")       # nu ridică


# ── firma fără cont bancar ──────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_fara_cont_bancar_scrie_textul_schemei_in_locul_ibanului():
    x = "\n".join(d406.antet_firma(dict(PROF, iban="", fara_cont_bancar=True)))
    assert _texte(x, "BankAccountNumber") == ["Fara cont bancar"]          # S.BA.2: „Fara cont bancar” (textul schemei)
    assert _texte(x, "IBANNumber") == []                                    # choice IBANNumber | BankAccountNumber (XSD)
    assert not d406.erori_generare(dict(PROF, iban="", fara_cont_bancar=True))


def test_fara_bifa_si_fara_iban_ramane_refuzul():
    er = d406.erori_generare(dict(PROF, iban="", fara_cont_bancar=False))
    assert len(er) == 1, er                                                  # S.BA.1 IBANNumber „Mandatory” fără bifă: numai IBAN-ul
    assert "Lipsă IBAN-ul firmei" in er[0] and "„Nu are cont bancar: Da”" in er[0], er   # și calea pentru firma fără cont


def test_bifa_cu_iban_completat_e_o_contradictie_numita():
    er = d406.erori_generare(dict(PROF, fara_cont_bancar=True))
    assert len(er) == 1 and "fără cont bancar, dar are IBAN" in er[0], er


def test_lipsurile_nu_mai_cer_ibanul_la_D406_cu_bifa():
    from core import firma_profil_api as fp
    fara = {x["camp"]: x["declaratii"] for x in fp.lipsuri({"iban": "", "fara_cont_bancar": True})}
    assert set(fara["iban"]) & {"D406", "D300"} == {"D300"}, fara    # cu bifa, IBAN-ul lipsă nu mai blochează D406 (D300 rămâne)
    cu = {x["camp"]: x["declaratii"] for x in fp.lipsuri({"iban": "", "fara_cont_bancar": False})}
    assert set(cu["iban"]) >= {"D406", "D300"}, cu


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_bifa_contrazisa_de_512_opreste_D406_cu_cifrele(conn):
    with conn.cursor() as cur:
        cur.execute("UPDATE firma_profil SET iban = NULL, fara_cont_bancar = true WHERE id = 1")
        cur.execute("UPDATE facturi SET tert_oras = 'Pantelimon'")
        cur.execute("INSERT INTO solduri_initiale (cont, denumire, sold_debitor, sold_creditor) VALUES ('5121', 'Conturi la banci in lei', 300, 0)")
        cur.execute("INSERT INTO inregistrari (data, descriere, status, sursa) VALUES ('2026-06-15', 'incasare', 'validata', 'manual') RETURNING id")
        nid = cur.fetchone()[0]
        cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, '5121', '4111', 121)", (nid,))
    with pytest.raises(RefuzGenerare) as ei:
        d406.genereaza(conn, _SCHEMA, 2026, 6)
    m = str(ei.value)
    assert re.findall(r"^D406 nu se poate genera: firma e declarată (fără cont bancar) \(Date firmă\), dar balanța arată (cont bancar) ", m) == [
        ("fără cont bancar", "cont bancar")], m                                       # decizia Costin pct.3: contradicția, spusă
    # cifrele din balanță, pe cont, întregi: 300 sold inițial + 121 încasare = 421
    assert _intre(m, "2026 – 30.06.2026: ", ". D406 ar declara") == (
        "contul 5121 — sold la început 300,00 lei, rulaj debitor 121,00 lei, rulaj creditor 0,00 lei, sold la sfârșit 421,00 lei"), m
    assert ei.value.detaliu()["camp_ecran"] == "df-fara_cont_bancar"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_bifa_fara_512_iese_cu_fara_cont_bancar_valid_pe_DUK(conn):
    from core import duk
    with conn.cursor() as cur:
        cur.execute("UPDATE firma_profil SET iban = NULL, fara_cont_bancar = true WHERE id = 1")
        cur.execute("UPDATE facturi SET tert_oras = CASE numar WHEN 'FV1' THEN 'Pantelimon' ELSE 'Sibiu' END")
    xml, _res = d406.genereaza(conn, _SCHEMA, 2026, 6)
    assert "<BankAccountNumber>Fara cont bancar</BankAccountNumber>" in xml and "<IBANNumber>" not in xml
    v = duk.valideaza(xml, "d406", an=2026, luna=6)
    if v.get("stare") == "gri":
        pytest.skip("validator SAF-T indisponibil: %s" % v.get("temei"))
    assert v.get("stare") == "valid", v
