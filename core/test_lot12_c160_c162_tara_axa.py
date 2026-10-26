# -*- coding: utf-8 -*-
"""[lotul 12, C160 + C161 + C162] Drumurile rămase deschise după C154 / C155: factura emisă care se naște fără țara clientului și fără axă,
și calendarul D390 al neplătitorului art.317 citit dintr-o altă sursă decât Control fiscal.

C160 — factura RECURENTĂ: șablonul n-avea țara clientului, iar emiterea lui (proba de la salvare, `facturi_recurente._proba_emiterii`, și
cronul, `emite_scadente`) chema `emite_factura` cu implicitul „RO”. La neplătitorul art.317 factura către clientul din DE ieșea fără axa
„servicii” (`categorii_tva.axa_neplatitor` cere țara) -> D390 L; la plătitor categoria „serviciu_extern” se refuza față de țara „RO”.
Acum șablonul poartă țara (`facturi_recurente.tert_tara`, `core/migrare_tara_sablon_recurent.py`) de la salvare până la emitere.

C161 — importul XML al facturii EMISE (`uc_comun._factura_din_parsat`, singurul drum al importului: `uc_tenants._factura_importata`): factura
intra cu țara „RO”, fără axă și fără categorie -> o prestare / livrare intracomunitară importată intra în D390 ca L. Acum țara vine din
adresa clientului din XML (BT-55), categoria din categoria liniei (BT-151) — aceeași regulă ca la emitere —, axa și taxarea inversă din
categorii; ce nu se poate deduce sigur se numește (`f["avertismente"]`).

C162 — „Termene” și selectorul Declarații (`termene_api.termene_firma`) puneau D390 pe toate lunile neplătitorului art.317: motorul nu primea
calendarul lui (`control_incrucisat.d390_luni_neplatitor`, sursa lui Control fiscal din C155).

Temei (anaf_surse/cod_fiscal_227_2015_consolidat.txt):
  · CF art.325 alin.(1) lit.a — D390 cuprinde „livrările intracomunitare scutite de taxă în condițiile prevăzute la art. 294 alin. (2)
    lit. a) și d)”; lit.c — „prestările de servicii prevăzute la art. 278 alin. (2) efectuate în beneficiul unor persoane impozabile
    nestabilite în România, dar stabilite în Uniunea Europeană”;
  · CF art.325 alin.(2) — „Declarația se întocmește pentru fiecare lună calendaristică în care ia naștere exigibilitatea taxei pentru
    operațiunile prevăzute la alin. (1)”;
  · CF art.278 alin.(2) — „Locul de prestare a serviciilor către o persoană impozabilă care acționează ca atare este locul unde respectiva
    persoană care primește serviciile își are stabilit sediul activității sale economice”;
  · CF art.307 alin.(1) — taxa o datorează furnizorul, „cu excepția cazurilor pentru care beneficiarul este obligat la plata taxei conform
    alin. (2)-(6) și art. 331” (de aici „AE”, taxarea inversă, pe factura emisă).
Judecătorul structurii D390: validatorul DUK local (`core/duk.py`, `valideaza(xml, "d390", an=, luna=)`).

Schemă efemeră din `tenant_template.sql`, tranzacție anulată, perioade sintetice în 2097. CUI firmei: 14399840 (cifra de control
verificată cu algoritmul din CLAUDE.md); clientul DE811907980 (cel din proba R187 / C78 / C110 / C154)."""
import ast
import contextlib
import datetime
import io
import json
import os

import pytest

from core import db as _db, tenant_provisioning as _tp

SCH = "tenant_test_lot12_c160"
RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CUI_FIRMA = "14399840"
COD_CLIENT = "DE811907980"
SERVICIU = "Servicii de consultanta IT"   # felul din denumire („servici” -> 704, `facturi.tip_din_denumire`)
AZI_SALVARE = datetime.date(2097, 9, 5)
AZI_CRON = datetime.date(2097, 9, 10)
#: ziua „de azi” a termenelor: 24.10.2097 — fereastra de 60 de zile cuprinde D390 09/2097 (termen 25.10) și D390 10/2097 (termen 25.11)
AZI = datetime.date(2097, 10, 24)


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:  # noqa: BLE001
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")

#: (plătitor, înregistrat art.317, tip decont): plătitorul art.316 și neplătitorul înregistrat art.317 (forma firmei de test F3)
FIRME = {"platitor": (True, False, "lunar"), "neplatitor_art317": (False, True, None)}


class _P:
    """Conexiunea testului, cu starea de plătitor (pentru aserțiuni); commit / rollback nu închid tranzacția testului."""
    def __init__(s, c, platitor): s._c, s.platitor = c, platitor
    def commit(s): pass
    def rollback(s): pass
    def __getattr__(s, n): return getattr(s._c, n)


@contextlib.contextmanager
def _firma(platitor, art317, decont):
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
                cur.execute(_tp.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), SCH))
                cur.execute("SET LOCAL search_path TO %s, public" % SCH)
                cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,telefon,platitor_tva,tip_decont,"
                            "inreg_art317,operatiuni_ic,regim_fiscal,tip_firma,declarant_nume,declarant_prenume,declarant_functie,"
                            "forma_juridica,capital_subscris,serie_factura,metoda_stoc) VALUES (1,'X SRL',%s,'Str 1','Cluj-Napoca',"
                            "'CJ','6201','BCR','RO49RNCB0000000000000001','0700000000',%s,%s,%s,true,'micro','srl','Popescu','Ion',"
                            "'ADMINISTRATOR','SRL',200,'SDC','global_valoric')", (CUI_FIRMA, platitor, decont, art317))
            yield _P(c, platitor)
        finally:
            c.rollback()


@pytest.fixture(params=sorted(FIRME))
def conn(request):
    with _firma(*FIRME[request.param]) as c:
        yield c


@pytest.fixture
def platitor():
    with _firma(*FIRME["platitor"]) as c:
        yield c


@pytest.fixture
def neplatitor():
    with _firma(*FIRME["neplatitor_art317"]) as c:
        yield c


def _sql(c, q, args=()):
    with c.cursor() as cur:
        cur.execute("SET LOCAL search_path TO %s, public" % SCH)
        cur.execute(q, args)
        return cur.fetchall() if cur.description else None


def _d390(c, an=2097, luna=9):
    from core import d390
    _sql(c, "SELECT 1")
    prof, facturi = d390.pull(c, SCH, an, luna)
    return d390.calcul_d390(prof, an, luna, facturi)


def _ops(res):
    return sorted((k[0], k[1], k[2], v) for k, v in res.ops.items())


# ── C160 — factura recurentă ──────────────────────────────────────────────────────────────────────────────────────────────────────────
def _linie_serviciu(c):
    """Linia de servicii a șablonului: la neplătitor cota 0 (CF art.310 alin.(10) lit.b), categoria o pune regimul firmei; la plătitor
    cota 0 cu categoria prestării cu locul în afara României (art.278 alin.(2)) — ce trimite API-ul (ecranul șablonului n-o alege)."""
    l = {"descriere": SERVICIU, "cantitate": 1, "um": "serv.", "pret_unitar": 500, "cota_tva": 0}  # [lotul 13, regula UM] linia șablonului poartă UM-ul
    if c.platitor:
        l["categorie_tva"] = "serviciu_extern"
    return l


def _adauga(c, **k):
    from core import facturi_recurente as fr
    _sql(c, "SELECT 1")
    corp = {"tert_cui": COD_CLIENT, "tert_nume": "KUNDE GMBH", "tert_tara": "DE", "linii": [_linie_serviciu(c)], "zi_emitere": 1,
            "moneda": "RON", "scadenta_zile": 15, "data_inceput": "2026-01-01", "valabil_pana": "oprire", "mod_emitere": "automata", "trimite_spv": False}   # [lotul 13, 680] întrebările emiterii
    corp.update(k)
    return fr.adauga(c, SCH, corp, azi=AZI_SALVARE)


def _cron(c, monkeypatch):
    """`emite_scadente` pe conexiunea testului (cronul își deschide conexiunile cu `db.get_conn`); ANAF neatins (beneficiar străin)."""
    from core import facturi_recurente as fr, uc_comun

    @contextlib.contextmanager
    def _gc(*a, **k):
        with c.cursor() as cur:
            cur.execute("SET LOCAL search_path TO %s, public" % SCH)
        yield c
    monkeypatch.setattr(_db, "get_conn", _gc)
    monkeypatch.setattr(uc_comun, "_platitor_tva_tert", lambda *a, **k: None)
    return fr.emite_scadente(SCH, AZI_CRON)


def test_c160_sablonul_poarta_tara_clientului_pana_la_emitere(conn, monkeypatch):
    """Șablonul către clientul din DE (serviciu, 500 lei) se salvează cu țara lui, iar factura lunară emisă de cron o poartă: axa
    „servicii”, D390 = P 500 (CF art.325 alin.(1) lit.c), pe ambele firme. Înainte: țara „RO” -> la neplătitor axa NULL și D390 = L 500, la
    plătitor categoria „serviciu_extern” refuzată față de „RO” (șablonul nu se salva).
    MUTAȚII: `tert_tara=tara_sablonului(s)` scos din `emite_scadente` -> neplătitorul: D390 L, plătitorul: factura refuzată -> ROȘU;
    `tert_tara=tara_sablonului(corp)` scos din `_proba_emiterii` -> plătitorul nu-și poate salva șablonul -> ROȘU."""
    r = _adauga(conn)
    assert set(r) == {"id"}, r
    assert _sql(conn, "SELECT tert_tara FROM facturi_recurente WHERE id = %s", (r["id"],)) == [("DE",)]
    assert _sql(conn, "SELECT count(*) FROM facturi")[0][0] == 0          # proba de la salvare nu lasă nicio factură
    emise = _cron(conn, monkeypatch)
    assert [(e["sablon"], bool(e.get("factura")), e.get("eroare")) for e in emise if "sablon" in e] == [(r["id"], True, None)], emise
    assert _sql(conn, "SELECT tert_tara, axa_ic, data_emitere FROM facturi") == [("DE", "servicii", AZI_CRON)]
    # CF art.325 alin.(1) lit.c: prestarea art.278 alin.(2) către clientul stabilit în UE -> cod P, baza pe client
    assert _ops(_d390(conn)) == [("P", "DE", "811907980", 500)]


def test_c160_d390_din_factura_recurenta_trece_validatorul_duk(neplatitor, monkeypatch):
    """Proba până la validatorul DUK local: D390 cu prestarea emisă din factura recurentă (P 500) e valid. Operațiunile sunt cele citite
    din bază pe 09/2097; declarația se construiește pe 09/2026, perioadă pe care validatorul o acceptă — aceleași operațiuni, aceeași firmă."""
    from core import d390, duk
    if not duk.poate_valida("d390"):
        pytest.skip("DUK d390 indisponibil")
    assert "id" in _adauga(neplatitor)
    _cron(neplatitor, monkeypatch)
    _sql(neplatitor, "SELECT 1")
    prof, facturi = d390.pull(neplatitor, SCH, 2097, 9)
    res = d390.calcul_d390(prof, 2026, 9, facturi)
    assert [k[0] for k in res.ops] == ["P"], res.ops
    rez = duk.valideaza(d390.build_xml(res), "d390", an=2026, luna=9)
    assert rez["stare"] == "valid", rez


def _pe_campuri(r):
    return [(x["camp"], x["mesaj"]) for x in (r.get("erori_campuri") or [])]


def test_c160_refuzurile_raman_numai_unde_sablonul_nu_poate_spune_operatiunea(conn):
    """Codul unui stat UE cu țara „România” (ce trimitea orice șablon de dinainte de C160) rămâne refuzat lângă „CUI beneficiar”; o țară
    care nu e cod de țară, lângă „Țara beneficiarului”. Plătitorul, clientul din DE, linia FĂRĂ cotă aleasă: refuzat lângă cota liniei (cota
    s-ar lua lunar din nomenclator, ca la o vânzare în România); [lotul 12, comanda Costin 12.3 pct.9: „Da: cota și categoria pe linia
    șablonului recurent, ca la factură.”] linia cu cota ALEASĂ (21%) se salvează — refuzul C160 se ridică acolo unde linia are cota;
    neplătitorul, linia fără cotă: salvat (cota 0 prin lege, CF art.310 alin.(10) lit.b; categoria o pune regimul firmei). Nimic salvat din
    refuzuri.
    MUTAȚIE: ramura `elif tara != "RO" and platitor is True …` scoasă din `verificari_drum` -> plătitorul își salvează șablonul cu linia fără
    cotă -> ROȘU."""
    from core import facturi_recurente as fr
    r = _adauga(conn, tert_tara=None)
    assert _pe_campuri(r) == [("fr-cui", fr.MESAJ_CLIENT_STRAIN % COD_CLIENT)], r
    r = _adauga(conn, tert_tara="Germania")
    assert ("fr-tara", fr.MESAJ_TARA % "Germania") in _pe_campuri(r), r
    r = _adauga(conn, linii=[{"descriere": SERVICIU, "cantitate": 1, "um": "serv.", "pret_unitar": 500, "cota_tva": None}])
    if conn.platitor:
        assert _pe_campuri(r) == [("fr-l0-cota", fr.MESAJ_STRAIN_FARA_COTA % (1, "DE"))], r
        assert _sql(conn, "SELECT count(*) FROM facturi_recurente")[0][0] == 0
        r = _adauga(conn, linii=[{"descriere": SERVICIU, "cantitate": 1, "um": "serv.", "pret_unitar": 500, "cota_tva": 21}])
        assert set(r) == {"id"}, r   # 12.3 pct.9: cota aleasă pe linie = alegerea contabilului (CLAUDE.md §8), ca la „Emite factură”
    else:
        assert set(r) == {"id"}, r


def test_c160_sablonul_vechi_fara_tara_e_refuzat_la_cron(conn, monkeypatch):
    """Un șablon scris înainte de C160 (fără țară: coloana îi dă „RO”) cu codul clientului din DE nu se emite ca vânzare în România:
    eroarea în jurnalul cronului, nicio factură. Datele existente: neafectate (țara pe care o lua deja), refuzul rămâne.
    MUTAȚIE: condiția `tara == "RO"` scoasă din ramura `MESAJ_CLIENT_STRAIN` a `verificari_drum` -> și șablonul cu țara DE e refuzat ->
    testul de emitere de mai sus ROȘU; condiția întreagă scoasă -> aici se emite -> ROȘU."""
    from core import facturi_recurente as fr
    _sql(conn, "INSERT INTO facturi_recurente (id, tert_nume, tert_cui, linii, zi_emitere) VALUES (1, 'KUNDE GMBH', %s, %s, 1)",
         (COD_CLIENT, json.dumps([_linie_serviciu(conn)])))
    assert _sql(conn, "SELECT tert_tara FROM facturi_recurente") == [("RO",)]
    emise = _cron(conn, monkeypatch)
    assert [(e["sablon"], e.get("eroare")) for e in emise if "sablon" in e] == [(1, fr.MESAJ_CLIENT_STRAIN % COD_CLIENT)], emise
    assert _sql(conn, "SELECT count(*) FROM facturi")[0][0] == 0


def test_c160_structura_tarii_din_sablon_si_migrarea():
    """Sursa unică a structurii: blocul din tenant_template.sql = `migrare_tara_sablon_recurent.bloc_template()`; migrarea e idempotentă
    și dă „RO” șabloanelor existente."""
    from core import migrare_tara_sablon_recurent as m
    assert m.bloc_template() in io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read()
    with _firma(*FIRME["platitor"]) as c:
        _sql(c, "ALTER TABLE facturi_recurente DROP COLUMN tert_tara")
        _sql(c, "INSERT INTO facturi_recurente (id, tert_nume, linii) VALUES (1, 'A SRL', '[]')")
        assert not m.verifica(c, SCH)
        m.aplica(c, SCH)
        m.aplica(c, SCH)
        assert m.verifica(c, SCH)
        assert _sql(c, "SELECT tert_tara FROM facturi_recurente") == [("RO",)]


# ── C161 — importul XML al facturii emise ─────────────────────────────────────────────────────────────────────────────────────────────
def _xml(numar, linii, tara="DE", cod_client=COD_CLIENT, data="2097-09-12", furnizor="RO" + CUI_FIRMA, client_nume="KUNDE GMBH"):
    """Factura UBL 2.1 minimă (CIUS-RO): furnizorul, clientul (cu țara în adresă — BT-55, sau fără), liniile (denumire, categoria BT-151,
    cota BT-152, valoarea netă BT-131)."""
    tara_xml = "<cac:Country><cbc:IdentificationCode>%s</cbc:IdentificationCode></cac:Country>" % tara if tara else ""
    randuri = "".join(
        "<cac:InvoiceLine><cbc:ID>%d</cbc:ID><cbc:InvoicedQuantity unitCode=\"C62\">1</cbc:InvoicedQuantity>"
        "<cbc:LineExtensionAmount currencyID=\"RON\">%s</cbc:LineExtensionAmount><cac:Item><cbc:Name>%s</cbc:Name>"
        "<cac:ClassifiedTaxCategory><cbc:ID>%s</cbc:ID><cbc:Percent>%s</cbc:Percent><cac:TaxScheme><cbc:ID>VAT</cbc:ID></cac:TaxScheme>"
        "</cac:ClassifiedTaxCategory></cac:Item><cac:Price><cbc:PriceAmount currencyID=\"RON\">%s</cbc:PriceAmount></cac:Price>"
        "</cac:InvoiceLine>" % (i + 1, suma, den, cat, cota, suma) for i, (den, cat, cota, suma) in enumerate(linii))
    total = sum(float(s) for _d, _c, _p, s in linii)
    return ("<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
            "<Invoice xmlns=\"urn:oasis:names:specification:ubl:schema:xsd:Invoice-2\" "
            "xmlns:cac=\"urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2\" "
            "xmlns:cbc=\"urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2\">"
            "<cbc:ID>%s</cbc:ID><cbc:IssueDate>%s</cbc:IssueDate><cbc:DocumentCurrencyCode>RON</cbc:DocumentCurrencyCode>"
            "<cac:AccountingSupplierParty><cac:Party><cac:PostalAddress><cac:Country><cbc:IdentificationCode>RO</cbc:IdentificationCode>"
            "</cac:Country></cac:PostalAddress><cac:PartyTaxScheme><cbc:CompanyID>%s</cbc:CompanyID><cac:TaxScheme><cbc:ID>VAT</cbc:ID>"
            "</cac:TaxScheme></cac:PartyTaxScheme><cac:PartyLegalEntity><cbc:RegistrationName>X SRL</cbc:RegistrationName>"
            "</cac:PartyLegalEntity></cac:Party></cac:AccountingSupplierParty>"
            "<cac:AccountingCustomerParty><cac:Party><cac:PostalAddress>%s</cac:PostalAddress><cac:PartyTaxScheme>"
            "<cbc:CompanyID>%s</cbc:CompanyID><cac:TaxScheme><cbc:ID>VAT</cbc:ID></cac:TaxScheme></cac:PartyTaxScheme>"
            "<cac:PartyLegalEntity><cbc:RegistrationName>%s</cbc:RegistrationName></cac:PartyLegalEntity></cac:Party>"
            "</cac:AccountingCustomerParty>"
            "<cac:TaxTotal><cbc:TaxAmount currencyID=\"RON\">0.00</cbc:TaxAmount></cac:TaxTotal>"
            "<cac:LegalMonetaryTotal><cbc:TaxInclusiveAmount currencyID=\"RON\">%.2f</cbc:TaxInclusiveAmount></cac:LegalMonetaryTotal>"
            "%s</Invoice>") % (numar, data, furnizor, tara_xml, cod_client, client_nume, total, randuri)


def _importa(c, xml):
    """Drumul importului (`uc_tenants.import_efactura` -> `_factura_importata` -> `uc_comun._factura_din_parsat`), pe cursorul testului."""
    from core import efactura_import, uc_tenants
    f = efactura_import.parseaza_xml(xml.encode("utf-8"), CUI_FIRMA)
    with c.cursor() as cur:
        cur.execute("SET LOCAL search_path TO %s, public" % SCH)
        fid, nou = uc_tenants._factura_importata(cur, SCH, f)
    assert nou
    return fid, f


def _factura(c, fid):
    return (_sql(c, "SELECT directie, tert_tara, axa_ic, taxare_inversa FROM facturi WHERE id = %s", (fid,))[0],
            [r[0] for r in _sql(c, "SELECT categorie_tva FROM factura_linii WHERE factura_id = %s ORDER BY id", (fid,))])


def test_c161_prestarea_ic_importata_intra_in_d390_ca_prestare(platitor):
    """Factura emisă importată din XML: serviciu 500 lei către clientul din DE, linia „AE” 0% (taxare inversă — prestarea cu locul la
    client, art.278 alin.(2)). În bază: țara DE, axa „servicii”, categoria „serviciu_extern” (cum o scrie emiterea din ecran); D390 = P 500
    (CF art.325 alin.(1) lit.c); niciun avertisment. Înainte: țara RO, axa NULL, fără categorie -> D390 L 500.
    MUTAȚIE: blocul `if f["directie"] == "emisa":` din `_factura_din_parsat` dezactivat -> țara RO, D390 L -> ROȘU."""
    fid, f = _importa(platitor, _xml("XM-1", [(SERVICIU, "AE", "0", "500.00")]))
    assert _factura(platitor, fid) == (("emisa", "DE", "servicii", False), ["serviciu_extern"])
    assert f["avertismente"] == []
    assert _ops(_d390(platitor)) == [("P", "DE", "811907980", 500)]


def test_c161_d390_din_factura_importata_trece_validatorul_duk(platitor):
    """Proba până la validatorul DUK local: D390 cu prestarea importată (P 500) și livrarea importată (L 300) e valid (construit pe 09/2026,
    cu operațiunile citite din bază pe 09/2097)."""
    from core import d390, duk
    if not duk.poate_valida("d390"):
        pytest.skip("DUK d390 indisponibil")
    _importa(platitor, _xml("XM-2", [(SERVICIU, "AE", "0", "500.00")]))
    _importa(platitor, _xml("XM-3", [("Marfa revanzare", "K", "0", "300.00")]))
    _sql(platitor, "SELECT 1")
    prof, facturi = d390.pull(platitor, SCH, 2097, 9)
    res = d390.calcul_d390(prof, 2026, 9, facturi)
    assert sorted(k[0] for k in res.ops) == ["L", "P"], res.ops
    rez = duk.valideaza(d390.build_xml(res), "d390", an=2026, luna=9)
    assert rez["stare"] == "valid", rez


def test_c161_livrarea_ic_exportul_si_taxarea_inversa_romana(platitor):
    """„K” către clientul din DE: livrare intracomunitară, axa „bunuri” (D390 L — CF art.325 alin.(1) lit.a). „G” către clientul din US:
    export, axa „bunuri”. „AE” către clientul din România: taxarea inversă art.331 (CF art.307 alin.(1)), factura cu taxare inversă și
    avertismentul pentru categoria produsului (codul D394 nu stă în XML). Grecia: ISO „GR” -> codul de TVA „EL” (`d406._ISO_TO_VAT`)."""
    fid, f = _importa(platitor, _xml("XM-4", [("Marfa revanzare", "K", "0", "300.00")]))
    assert _factura(platitor, fid) == (("emisa", "DE", "bunuri", False), ["livrare_ic"]) and f["avertismente"] == []
    fid, f = _importa(platitor, _xml("XM-5", [("Marfa export", "G", "0", "200.00")], tara="US", cod_client="US123456789",
                                     client_nume="ACME INC"))
    assert _factura(platitor, fid) == (("emisa", "US", "bunuri", False), ["export"]) and f["avertismente"] == []
    fid, f = _importa(platitor, _xml("XM-6", [("Deseuri feroase", "AE", "0", "100.00")], tara="RO", cod_client="RO14399840",
                                     client_nume="DANTE INTERNATIONAL SA"))
    assert _factura(platitor, fid) == (("emisa", "RO", None, True), ["taxare_inversa"])
    assert [a for a in f["avertismente"] if "art.331" in a] == f["avertismente"] and len(f["avertismente"]) == 1, f["avertismente"]
    fid, _f = _importa(platitor, _xml("XM-7", [("Marfa revanzare", "K", "0", "300.00")], tara="GR", cod_client="EL094014201",
                                      client_nume="ELLINIKA AE"))
    assert _factura(platitor, fid)[0][1] == "EL"
    _ops_l = _ops(_d390(platitor))
    assert ("L", "DE", "811907980", 300) in _ops_l, _ops_l


def test_c161_ce_nu_se_poate_deduce_sigur_se_numeste(platitor):
    """„E” 0% către clientul din US (scutire, operațiune în afara sferei sau prestare cu locul în afara UE — codul nu le desparte): fără
    categorie, fără axă, două avertismente (categoria liniei, natura operației). „K” către clientul din România: contradicție, linia
    rămâne fără categorie. Bunuri și servicii pe aceeași factură către clientul din UE: fără axă, avertismentul spune că se clasifică în
    D390. Fișierul fără țara clientului: rămâne „RO”, cu avertisment. Linia taxabilă (S, 21%) nu are categorie și nu produce avertisment."""
    fid, f = _importa(platitor, _xml("XN-1", [("Consultanta", "E", "0", "100.00")], tara="US", cod_client="US123456789",
                                     client_nume="ACME INC"))
    assert _factura(platitor, fid) == (("emisa", "US", None, False), [None])
    assert len(f["avertismente"]) == 2 and "categoria de TVA a liniei" in f["avertismente"][0] \
        and "livrare de bunuri sau prestare de servicii" in f["avertismente"][1], f["avertismente"]
    fid, f = _importa(platitor, _xml("XN-2", [("Marfa", "K", "0", "100.00")], tara="RO", cod_client="RO14399840",
                                     client_nume="DANTE INTERNATIONAL SA"))
    assert _factura(platitor, fid) == (("emisa", "RO", None, False), [None])
    assert len(f["avertismente"]) == 1 and "livrare intracomunitară" in f["avertismente"][0], f["avertismente"]
    fid, f = _importa(platitor, _xml("XN-3", [("Marfa revanzare", "K", "0", "100.00"), (SERVICIU, "AE", "0", "50.00")]))
    assert _factura(platitor, fid) == (("emisa", "DE", None, False), ["livrare_ic", "serviciu_extern"])
    assert len(f["avertismente"]) == 1 and "Clasificare intracomunitară" in f["avertismente"][0], f["avertismente"]
    fid, f = _importa(platitor, _xml("XN-4", [("Abonament", "S", "21", "100.00")], tara=None, cod_client="RO14399840",
                                     client_nume="DANTE INTERNATIONAL SA"))
    assert _factura(platitor, fid) == (("emisa", "RO", None, False), [None])
    assert len(f["avertismente"]) == 1 and "țara clientului" in f["avertismente"][0], f["avertismente"]


def test_c161_neplatitorul_si_factura_primita(neplatitor):
    """Neplătitorul: liniile „O” primesc categoria regimului special („neplatitor”); felul (bunuri / servicii) nu stă în XML -> fără axă,
    cu avertisment (nimic ghicit). Factura PRIMITĂ nu trece prin clasificarea emisei: țara și restul i le pune validarea
    (`uc_factura_primita.valideaza`), ca înainte."""
    fid, f = _importa(neplatitor, _xml("XO-1", [(SERVICIU, "O", "0", "500.00")]))
    assert _factura(neplatitor, fid) == (("emisa", "DE", None, False), ["neplatitor"])
    assert len(f["avertismente"]) == 1 and "D390" in f["avertismente"][0], f["avertismente"]
    fid, f = _importa(neplatitor, _xml("XP-1", [("Licenta software", "AE", "0", "70.00")], furnizor=COD_CLIENT, cod_client=CUI_FIRMA,
                                       client_nume="X SRL", tara="RO"))
    assert _factura(neplatitor, fid) == (("primita", "RO", None, False), [None])
    assert "avertismente" not in f


def test_c161_categoria_liniei_emise_din_xml():
    """`uc_comun._categoria_emisei_din_xml` — pură: aceeași regulă ca factura emisă din ecran (`categorii_tva.verifica_linii`) și inversul
    hărții de la emitere (`categorii_tva.CATEGORII[...]["ubl"]`)."""
    from core.uc_comun import _categoria_emisei_din_xml as cat
    assert cat("K", "0", "DE") == ("livrare_ic", None)
    assert cat("G", "0.00", "US") == ("export", None)
    assert cat("AE", "0", "DE") == ("serviciu_extern", None)
    assert cat("AE", "0", "RO") == ("taxare_inversa", None)
    assert cat("O", "0", "DE") == ("neplatitor", None)
    assert cat("S", "21", "DE") == (None, None)
    assert cat("K", "21", "DE") == (None, None)                     # cota pozitivă: linia taxabilă, nu scutirea
    for ubl, tara in (("K", "RO"), ("K", "US"), ("G", "DE"), ("G", "RO"), ("AE", "US"), ("E", "DE"), (None, "DE"), ("Z", "RO")):
        c, motiv = cat(ubl, "0", tara)
        assert c is None and motiv, (ubl, tara)


# ── C162 — „Termene” și selectorul Declarații ─────────────────────────────────────────────────────────────────────────────────────────
VECTOR_NEPLATITOR = {"regim_fiscal": "micro", "platitor_tva": False, "tip_decont": None, "operatiuni_ic": True, "tip_firma": "srl",
                     "partida_simpla": False, "tva_data_inceput": None, "inreg_art317": True}


def test_c162_termenele_neplatitorului_art317_numai_pe_lunile_cu_operatiuni(neplatitor):
    """Prestarea IC emisă în 09/2097; azi 24.10.2097, fereastra de 60 de zile cuprinde D390 09/2097 (25.10) și 10/2097 (25.11). Cu
    calendarul neplătitorului (`control_incrucisat.d390_luni_neplatitor`, sursa lui Control fiscal) „Termene” arată numai D390 09/2097
    (CF art.325 alin.(2)); fără el (forma de dinainte) arăta și 10/2097, lună fără nicio operațiune intracomunitară.
    MUTAȚIE: `d390_luni_neplatitor=d390_luni_neplatitor` scos din `termene_api.termene_firma` -> apare și 10/2097 -> ROȘU."""
    from core import control_incrucisat as ci, facturi_api, termene_api, uc_comun
    _sql(neplatitor, "SELECT 1")
    facturi_api.emite_factura(neplatitor, [{"descriere": SERVICIU, "cantitate": 1, "um": "serv.", "pret_unitar": "500", "cota_tva": 0}],
                              tert_nume="KUNDE GMBH", tert_cui=COD_CLIENT, tert_tara="DE", data_emitere="2097-09-10",
                              platitor_tva=uc_comun._platitor_tva_firma(neplatitor))

    from core import d390

    def _d390_termene(**k):
        # faptul lunar D390, cum îl dă drumul real (`firma_rezumat._termene_una_firma`); fără el motorul ia forma veche, pe bifă
        fapt = lambda a, m: d390.d390_are_operatiuni(neplatitor, SCH, a, m, AZI)   # noqa: E731
        t = termene_api.termene_firma(VECTOR_NEPLATITOR, False, set(), AZI, d390_fapt=fapt, **k)
        return sorted((x["an"], x["luna"]) for x in t if x["tip"] == "d390")
    luni = lambda a: ci.d390_luni_neplatitor(neplatitor, SCH, a, AZI)   # noqa: E731
    assert _d390_termene(d390_luni_neplatitor=luni) == [(2097, 9)]
    fara = _d390_termene()
    assert (2097, 9) in fara and (2097, 10) in fara, fara   # anti-vacuu: fără calendar, D390 și pe luna fără operațiuni


def test_c162_termenele_firmei_primesc_calendarul_neplatitorului():
    """Drumul real al „Termene” și al selectorului Declarații (`firma_rezumat._termene_una_firma`, chemat și de
    `uc_declaratii._datorate_firmei`) dă motorului termenelor calendarul neplătitorului art.317 — ACEEAȘI funcție ca Control fiscal
    (`control_fiscal_api.evalueaza_firma`: `control_incrucisat.d390_luni_neplatitor`).
    MUTAȚIE: argumentul `d390_luni_neplatitor=` scos din apelul `termene_api.termene_firma` din `firma_rezumat` -> ROȘU."""
    arb = ast.parse(io.open(os.path.join(RAD, "core", "firma_rezumat.py"), encoding="utf-8").read())
    apeluri = [n for n in ast.walk(arb) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
               and n.func.attr == "termene_firma"]
    assert len(apeluri) == 1, "apelul termenelor din firma_rezumat nu mai e unul singur: %d" % len(apeluri)
    kw = {k.arg: k.value for k in apeluri[0].keywords}
    assert "d390_luni_neplatitor" in kw, "firma_rezumat nu dă motorului termenelor calendarul D390 al neplătitorului art.317"
    numit = {n.attr for n in ast.walk(kw["d390_luni_neplatitor"]) if isinstance(n, ast.Attribute)}
    assert "d390_luni_neplatitor" in numit, ast.dump(kw["d390_luni_neplatitor"])
