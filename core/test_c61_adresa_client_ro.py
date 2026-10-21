# -*- coding: utf-8 -*-
"""[deficiența C61, găsită de Code 19.10.2026] Factura emisă din formular către un client din România n-avea localitatea și județul
(formularul le trimite numai la clientul străin): generatorul scotea CityName „-” și nicio CountrySubentity, iar validatorul FACT1
răspundea `nok` — deci poarta 2 din `efactura_trimitere.trimite` oprea ORICE astfel de factură.

Temei: eFactura regula BR-RO-110 (validatorul ANAF FACT1, mesajul verbatim): „Daca Codul tarii Cumparatorului (BT-55) este RO, atunci
Subdiviziunea tarii Cumparatorului (BT-54) trebuie sa fie codificata folosind lista de coduri ISO 3166-2:RO”; CF art.319 alin.(20) lit.f
(anaf_surse/cod_fiscal_227_2015_consolidat.txt:8061): factura cuprinde „denumirea/numele și adresa beneficiarului bunurilor sau
serviciilor”. Sursa faptului: ANAF PlatitorTvaRest v9, `adresa_domiciliu_fiscal.ddenumire_Localitate` / `dcod_JudetAuto`
(anaf_surse/doc_WS_V9.txt) — domiciliul fiscal, aceeași adresă ca `date_generale.adresa`, cea scrisă pe factură.

ANAF e SIMULAT (răspunsul cu structura din doc_WS_V9; valorile sunt sintetice), niciodată real. Schemă efemeră din tenant_template,
o singură conexiune reală, anulată la final."""
import re
import contextlib
import io
import xml.etree.ElementTree as ET

import pytest

from core import anaf_api, db as _db, efactura_send as _ef, efactura_trimitere as _et, facturi_api, tenant_provisioning as _tp

ANAF_LA_EMITERE_REAL = True   # core/conftest.py: aici se probează consultarea însăși, cu ANAF simulat (anaf_api.requests)

_SCHEMA = "test_c61_adresa_ro"
_NS = {"cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
       "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"}
_LINIE = {"descriere": "Marfa C61", "cantitate": 1, "pret_unitar": 100, "cota_tva": 21, "um": "buc", "cont_venit": "707"}

#: răspunsul ANAF simulat, cu structura din anaf_surse/doc_WS_V9.txt (date sintetice; sediul social diferă intenționat de domiciliul
#: fiscal, ca să se vadă de unde se iau localitatea și județul)
_RASPUNS_ANAF = {"found": [{
    "date_generale": {"cui": 14399840, "denumire": "DANTE INTERNATIONAL SA", "adresa": "MUNICIPIUL BUCUREŞTI, SECTOR 2, STR. SINTETICA NR.1",
                      "stare_inregistrare": "INREGISTRAT", "nrRegCom": "J40/0000/2000", "cod_CAEN": "4791"},
    "inregistrare_scop_Tva": {"scpTVA": True, "perioade_TVA": [{"data_inceput_ScpTVA": "2002-01-01", "data_sfarsit_ScpTVA": ""}]},
    "inregistrare_RTVAI": {"statusTvaIncasare": False},
    "stare_inactiv": {"statusInactivi": False},
    "adresa_sediu_social": {"sdenumire_Localitate": "Mun. Cluj-Napoca", "scod_JudetAuto": "CJ"},
    "adresa_domiciliu_fiscal": {"ddenumire_Strada": "Str. Sintetica", "dnumar_Strada": "1",
                                "ddenumire_Localitate": " Sector 2 Mun. Bucureşti ", "dcod_JudetAuto": " B ", "dtara": "România"},
}], "notFound": []}


class _Raspuns:
    status_code = 200

    def __init__(self, j):
        self._j = j

    def json(self):
        return self._j

    def raise_for_status(self):
        pass


def _anaf(monkeypatch, raspuns=_RASPUNS_ANAF, jos=False):
    """ANAF simulat la nivelul HTTP al lui `anaf_api` (numai modulul lui), ca drumul să treacă prin parsarea reală a lui `valideaza_cui`."""
    apeluri = []

    class _Req:
        @staticmethod
        def post(url, json=None, **k):
            apeluri.append(json)
            if jos:
                raise OSError("ANAF simulat indisponibil")
            return _Raspuns(raspuns)
    monkeypatch.setattr(anaf_api, "requests", _Req)
    return apeluri


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


class _FaraCommit:
    def __init__(self, c):
        self._c = c

    def commit(self):
        pass

    def __getattr__(self, n):
        return getattr(self._c, n)


@pytest.fixture
def conn(monkeypatch):
    """Schema efemeră; `db.get_conn` întoarce aceeași conexiune reală (fără commit), anulată la final — drumurile probate (emiterea,
    trimiterea) își deschid singure conexiunile."""
    from core import ai_client, uc_comun
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(_tp.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                cur.execute("SET search_path TO %s, public" % _SCHEMA)
                cur.execute("INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, caen, telefon, banca, iban, regim_fiscal, "
                            "platitor_tva, tip_decont, declarant_nume, declarant_prenume, declarant_functie, reg_com, forma_juridica, "
                            "capital_subscris, metoda_stoc) VALUES (1,'C61 SRL','14399840','Str Test 1','Sector 1','B','4690',"
                            "'0722000000','BCR','RO49AAAA1B31007593840000','real',true,'L','Popescu','Ion','ADMINISTRATOR',"
                            "'J40/1/2020','SRL',200,'global_valoric')")
            facturi_api.seteaza_numerotare(c, serie="CS", numar_start=1)

            @contextlib.contextmanager
            def _gc(*a, **k):
                yield _FaraCommit(c)
            monkeypatch.setattr(_db, "get_conn", _gc)
            monkeypatch.setattr(ai_client, "disponibil", lambda: False)
            monkeypatch.setattr(uc_comun, "_schema_sau_404", lambda *a, **k: _SCHEMA)
            yield c
        finally:
            c.rollback()


def _emite(**k):
    import main
    from core import uc_tenants
    date = main.EmitereIn(**dict({"linii": [dict(_LINIE)], "tert_nume": "DANTE INTERNATIONAL SA", "tert_cui": "RO14399840",
                                  "tert_adresa": "MUNICIPIUL BUCUREŞTI, SECTOR 2, STR. SINTETICA NR.1", "data_emitere": "2026-10-19",
                                  "data_scadenta": "2026-11-18"}, **k))
    r = uc_tenants.facturi_emite(1, date, {"uid": 1})
    with _db.get_conn(_SCHEMA) as c, c.cursor() as cur:
        cur.execute("SELECT tert_oras, tert_judet FROM facturi WHERE id = %s", (r["factura_id"],))
        return cur.fetchone()


def _factura_fara_judet(conn):
    """Factura emisă așa cum o lasă azi celelalte drumuri (și formularul de dinainte de C61): client RO, fără localitate și județ."""
    r = facturi_api.creeaza_factura(conn, "CS7", "2026-10-19", "emisa", [dict(_LINIE)], data_scadenta="2026-11-18",
                                    tert_nume="DANTE INTERNATIONAL SA", tert_cui="RO14399840",
                                    tert_adresa="MUNICIPIUL BUCUREŞTI, SECTOR 2, STR. SINTETICA NR.1", status="emisa")
    return r["factura_id"]


def _xml_trimis(monkeypatch, factura_id):
    """XML-ul pe care `trimite` l-ar încărca: token și drept simulate; validatorul simulat îl reține și oprește trimiterea la poarta 2
    (nimic încărcat, niciun rând scris)."""
    retinut = []
    monkeypatch.setattr(_et.spv_conector, "ia_token_activ", lambda c, p: {"id": 1})
    monkeypatch.setattr(_et.spv_conector, "stare_firma", lambda c, p, cui: {})
    monkeypatch.setattr(_ef, "valideaza", lambda xml, standard="FACT1": (retinut.append(xml), (False, ["oprit de test"]))[1])
    assert _et.trimite(_SCHEMA, factura_id, "P")["stare"] == "nevalidat"
    adr = ET.fromstring(retinut[0].encode("utf-8")).find("cac:AccountingCustomerParty/cac:Party/cac:PostalAddress", _NS)
    return adr.findtext("cbc:CityName", namespaces=_NS), adr.findtext("cbc:CountrySubentity", namespaces=_NS)


# ── a) sursa: domiciliul fiscal din răspunsul ANAF ─────────────────────────────────────────────────────────────────────────────────
def test_c61_valideaza_cui_scoate_localitatea_si_judetul_domiciliului_fiscal(monkeypatch):
    """doc_WS_V9.txt: `adresa_domiciliu_fiscal.ddenumire_Localitate` / `dcod_JudetAuto` — nu sediul social (`s…`).
    MUTAȚIE: câmpurile citite din `adresa_sediu_social` -> „Mun. Cluj-Napoca” / „CJ” -> pică."""
    _anaf(monkeypatch)
    r = anaf_api.valideaza_cui(["RO14399840"])[0]
    assert (r["gasit"], r["localitate"], r["judet"]) == (True, "Sector 2 Mun. Bucureşti", "B"), r
    _anaf(monkeypatch, raspuns={"found": [], "notFound": [14399840]})
    r = anaf_api.valideaza_cui(["14399840"])[0]
    assert (r["gasit"], r["localitate"], r["judet"]) == (False, "", ""), r


# ── b) emiterea din formular: documentul emis rămâne ce a scris omul ─────────────────────────────────────────────────────────────────
@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c61_emiterea_nu_scrie_pe_factura_localitatea_si_judetul_din_anaf(conn, monkeypatch):
    """Serverul nu consultă ANAF la emitere: pe factură ajunge ce trimite formularul. [Decizia Costin 19.10.2026, „Da, câmpuri și la
    român”, supersedează „numai la trimitere”] formularul precompletează localitatea și județul din „Verifică” (modificabile) și le trimite
    și la clientul român (partea d); fără ele, factura rămâne fără, iar XML-ul le ia la trimitere (partea c)."""
    _anaf(monkeypatch)
    assert _emite() == (None, None)
    assert _emite(tert_oras="Sector 4") == ("Sector 4", None)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c61_clientul_strain_nu_intreaba_anaf(conn, monkeypatch):
    apeluri = _anaf(monkeypatch)
    assert _emite(tert_tara="DE", tert_cui="DE123456789", tert_oras="Berlin", tert_judet="BE") == ("Berlin", "BE")
    assert apeluri == []


# ── c) trimiterea în SPV: drumul unic spre ANAF, pentru facturile de pe orice drum de emitere ─────────────────────────────────────
@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c61_xml_trimis_are_judetul_si_sectorul_din_anaf_fara_sa_rescrie_factura(conn, monkeypatch):
    """eFactura regula BR-RO-110 (BT-54 = RO-B) și eFactura regula BR-RO-100 (în București CityName = SECTORn).
    MUTAȚIE: `completeaza_client_ro` scos din `efactura_trimitere.trimite` -> („-”, None) -> pică."""
    fid = _factura_fara_judet(conn)
    _anaf(monkeypatch)
    assert _xml_trimis(monkeypatch, fid) == ("SECTOR2", "RO-B")
    with conn.cursor() as cur:   # documentul emis nu se rescrie
        cur.execute("SELECT tert_oras, tert_judet FROM facturi WHERE id = %s", (fid,))
        assert cur.fetchone() == (None, None)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c61_xml_trimis_cu_anaf_jos_ramane_ca_azi(conn, monkeypatch):
    """[lotul 10, C69] Cu ANAF jos și fără localitate pe factură, XML-ul nu mai pleacă cu CityName „-”: trimiterea se oprește numit
    (FACT1 BR-RO-092: „Localitatea Cumparatorului (BT-52) trebuie furnizata”; cu „-” validatorul răspundea „ok”)."""
    fid = _factura_fara_judet(conn)
    _anaf(monkeypatch, jos=True)
    with pytest.raises(_ef.EDateIncomplete) as ei:
        _xml_trimis(monkeypatch, fid)
    # numai localitatea lipsește (strada e pe factură), cu regula ei: FACT1 „[BR-RO-090]-Localitatea Cumparatorului (BT-52) trebuie furnizata”
    assert re.findall(r"lipsesc (.+?) — ANAF le cere \(regulile (.+?)\)\.", str(ei.value)) == [("localitatea clientului", "BR-RO-092 (BT-52)")], str(ei.value)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c61_trimiterea_nu_intreaba_anaf_cand_factura_are_judetul(conn, monkeypatch):
    fid = _factura_fara_judet(conn)
    with conn.cursor() as cur:
        cur.execute("UPDATE facturi SET tert_oras = 'Sector 5', tert_judet = 'B' WHERE id = %s", (fid,))
    apeluri = _anaf(monkeypatch)
    assert _xml_trimis(monkeypatch, fid) == ("SECTOR5", "RO-B")
    assert apeluri == []


def test_c61_completarea_nu_suprascrie_si_nu_atinge_clientul_strain(monkeypatch):
    _anaf(monkeypatch)
    cl = {"tara": "RO", "cui": "RO14399840", "oras": "Sector 2", "judet": ""}
    assert _et.completeaza_client_ro(cl) == dict(cl, judet="B") and cl["judet"] == ""   # copie; orașul omului rămâne
    strain = {"tara": "DE", "cui": "DE123456789", "oras": None, "judet": None}
    assert _et.completeaza_client_ro(strain) is strain


# ── d) [decizia Costin 19.10.2026, „Închiderea lotului 9”: „Da, câmpuri și la român”] formularul trimite localitatea și județul și la
# clientul român; factura și PDF-ul le poartă, fără dublarea localității ──────────────────────────────────────────────────────────────
@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c61_emiterea_pastreaza_localitatea_si_judetul_clientului_roman(conn, monkeypatch):
    """Ce a trimis formularul (precompletat din ANAF: domiciliul fiscal, doc_WS_V9) se scrie pe factură, iar adresa din detaliu / PDF
    (`factura_pdf.adresa_tert`, aceeași funcție pentru amândouă) nu repetă localitatea și județul cuprinse deja în adresă. CF art.319
    alin.(20) lit.f (anaf_surse/cod_fiscal_227_2015_consolidat.txt:8061): „denumirea/numele și adresa beneficiarului”.
    MUTAȚIE: `tert_oras` / `tert_judet` scoase din apelul lui `emite_factura` în `uc_tenants.facturi_emite` -> (None, None) -> pică."""
    _anaf(monkeypatch)   # emiterea întreabă ANAF numai de plătitorul de TVA (`_platitor_tva_tert`), nu de adresă
    assert _emite(tert_oras="Sector 2 Mun. Bucureşti", tert_judet="B") == ("Sector 2 Mun. Bucureşti", "B")
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM facturi ORDER BY id DESC LIMIT 1")
        fid = cur.fetchone()[0]
    assert facturi_api.detalii_factura(conn, fid)["tert_adresa_completa"] == "MUNICIPIUL BUCUREŞTI, SECTOR 2, STR. SINTETICA NR.1"


def test_c61_adresa_pe_factura_fara_dublarea_localitatii_si_judetului():
    """Localitatea / județul deja cuprinse în adresă nu se repetă; județul clientului român apare cu numele, nu cu codul; un cuvânt al
    adresei nu ascunde un județ („Str. Cluj 5”, „Cluj-Napoca”); regiunea clientului străin rămâne cum a scris-o omul.
    MUTAȚII: `_cuprinsa_in` întoarce mereu False -> „…, Sector 2 Mun. Bucureşti, București” -> pică; maparea `JUDETE_NUME` scoasă -> „B”
    -> pică; acoperirea fără tăierea la felul localității (`_FEL_LOCALITATE`) -> „…, București” după „Sector 2 Mun. Bucureşti” -> pică."""
    from core import factura_pdf as fp
    adr = "MUNICIPIUL BUCUREŞTI, SECTOR 2, STR. SINTETICA NR.1"
    assert fp.adresa_tert(adr, "Sector 2 Mun. Bucureşti", "B", "RO") == adr
    assert fp.adresa_tert("Str. Sintetica 1", "Sector 2 Mun. Bucureşti", "B", "RO") == "Str. Sintetica 1, Sector 2 Mun. Bucureşti"
    assert fp.adresa_tert("Str. X 1", "Turda", "CJ", "RO") == "Str. X 1, Turda, Cluj"
    assert fp.adresa_tert("Str. Cluj 5", "Turda", "CJ", "RO") == "Str. Cluj 5, Turda, Cluj"
    assert fp.adresa_tert("Str. X 1", "Cluj-Napoca", "CJ", "RO") == "Str. X 1, Cluj-Napoca, Cluj"
    assert fp.adresa_tert("JUD. CLUJ, MUN. TURDA, STR. A 1", "Mun. Turda", "CJ", "RO") == "JUD. CLUJ, MUN. TURDA, STR. A 1"
    assert fp.adresa_tert("Hauptstr. 1", "Berlin", "BE", "DE") == "Hauptstr. 1, Berlin, BE, Germania"   # „BE” e regiunea, nu Brașov
    assert fp.adresa_tert("1 GRAND CANAL\nDUBLIN 4", "DUBLIN 4", None, "IE") == "1 GRAND CANAL\nDUBLIN 4, Irlanda"   # 331, neschimbat


def test_c61_judetele_formularului_sunt_ale_pdf_si_ale_efactura():
    """Paritatea listelor: județele din „Emite factură” (`JUDETE_RO`) = numele de pe PDF (`factura_pdf.JUDETE_NUME`) = lista declarațiilor
    (`_D603_JUDETE`), iar codurile sunt exact cele pe care XML-ul le codifică (`efactura_send._CODURI_JUD`, ISO 3166-2:RO — eFactura regula
    BR-RO-110). MUTAȚIE: un județ scos din `JUDETE_RO` -> pică."""
    import re
    from core import factura_pdf as fp
    def lista(fisier, nume):
        js = io.open(fisier, encoding="utf-8").read()
        a = js.index("const %s = [" % nume)
        return dict(re.findall(r'\["([A-Z]{1,2})","([^"]+)"\]', js[a:js.index("]];", a) + 2]))
    din_emitere = lista("static/js/ecrane/emitere_ecran.js", "JUDETE_RO")
    assert din_emitere == fp.JUDETE_NUME
    assert din_emitere == lista("static/js/ecrane/declaratii.js", "_D603_JUDETE")
    assert set(din_emitere) == _ef._CODURI_JUD and len(din_emitere) == 42
