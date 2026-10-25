# -*- coding: utf-8 -*-
"""[lotul 12, pachetul fisc3, comanda 12.3 pct.3 și pct.10] Prestarea intracomunitară de servicii a firmei NEPLĂTITOARE de TVA.

Decizia Costin 12.3 pct.3, verbatim: „Prestarea intracomunitară de servicii a neplătitorului înregistrat art. 317: fără TVA român, mențiunea
«taxare inversă», codul RO art. 317 pe factură, P în D390 (C156); fără înregistrare art. 317, avertisment la emitere, nu refuz (C157)”.
Pct.10: „Facturile vechi ale neplătitorilor nu se migrează; regula se aplică de la facturile noi, declarațiile depuse rămân neatinse.”

C156 — înainte: linia prestării purta categoria regimului special („neplatitor”, O): PDF-ul spunea „Scutit de TVA — regim special … art.
310” și „CIF: …”, XML-ul e-Factura ieșea O fără codurile părților. Acum, la neplătitorul ÎNREGISTRAT art.317, linia de servicii către
clientul din alt stat membru cu cod de TVA primește la emitere categoria prestării cu locul la client (`categorii_tva.PRESTARE_IC_317`):
AE + „taxare inversă” în XML și pe PDF, codul RO art.317 al firmei (PDF „Cod TVA (art.317): RO…”, XML BT-31), codul clientului (BT-48),
axa „servicii” (D390 P). Pe ecran: detaliul facturii arată aceleași mențiuni ca PDF-ul (`facturi_api.detalii_factura`, clasa 417).
C157 — neplătitorul NEînregistrat art.317 (sau cu alegerea lipsă în Date firmă): factura se emite ca până acum (O), cu avertismentul
emiterii (`categorii_tva.avertismente_emitere`), în „Emite factură” și în Operațiuni.

Temei (anaf_surse/cod_fiscal_227_2015_consolidat.txt; anaf_surse/mf_ghid_coduri_facturi_efactura_v2_9.txt), citat pe linia aserțiunii.
Schemă efemeră din `tenant_template.sql`, tranzacție anulată, date sintetice în 2097. CUI firmei: 14399840 (cifra de control verificată
cu algoritmul din CLAUDE.md); clientul DE811907980 (cel din probele R187 / C78 / C110 / C154; `d390.checksum_vies` -> ok)."""
import contextlib
import io
import os
import xml.etree.ElementTree as ET

import pytest

from core import db as _db, tenant_provisioning as _tp

SCH = "tenant_test_lot12_fisc3_c156"
RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COD_CLIENT = "DE811907980"
SERVICIU = "Servicii de consultanta IT"   # felul din denumire („servici” -> 704), ca la emiterea din ecran
#: mențiunea întreagă a liniei prestării art.317 pe PDF și pe ecran (`factura_pdf.mentiuni_categorii`, motivul categoriei)
MENTIUNE_317 = ("1 linie (nr. 1): Taxare inversă — prestare de servicii cu locul în alt stat membru, art.278 alin.(2) din Legea nr.227/2015 "
                "privind Codul fiscal.")
NS = {"cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
      "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"}

#: (plătitor, înregistrat art.317, tip decont)
FIRME = {"art317": (False, True, None), "neinregistrat": (False, False, None), "neales": (False, None, None),
         "platitor": (True, False, "lunar")}


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


class _P:
    """Conexiunea testului, cu starea firmei (pentru aserțiuni); commit / rollback nu închid tranzacția testului."""
    def __init__(s, c, fel): s._c, s.fel = c, fel
    def commit(s): pass
    def rollback(s): pass
    def __getattr__(s, n): return getattr(s._c, n)


@contextlib.contextmanager
def _firma(fel):
    if not _db_ok():
        pytest.skip("DB indisponibil")
    platitor, art317, decont = FIRME[fel]
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
                cur.execute(_tp.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), SCH))
                cur.execute("SET LOCAL search_path TO %s, public" % SCH)
                cur.execute("INSERT INTO firma_profil (id,nume,cui,reg_com,adresa,oras,judet,caen,banca,iban,telefon,platitor_tva,tip_decont,"
                            "inreg_art317,operatiuni_ic,regim_fiscal,tip_firma,declarant_nume,declarant_prenume,declarant_functie,"
                            "forma_juridica,capital_subscris,serie_factura,metoda_stoc) VALUES (1,'X SRL','14399840','J12/1/2020','Str 1',"
                            "'Cluj-Napoca','CJ','6201','BCR','RO49RNCB0000000000000001','0700000000',%s,%s,%s,true,'micro','srl','Popescu',"
                            "'Ion','ADMINISTRATOR','SRL',200,'SDC','global_valoric')", (platitor, decont, art317))
            yield _P(c, fel)
        finally:
            c.rollback()


@pytest.fixture
def art317():
    with _firma("art317") as c:
        yield c


def _sql(c, q, args=()):
    with c.cursor() as cur:
        cur.execute("SET LOCAL search_path TO %s, public" % SCH)
        cur.execute(q, args)
        return cur.fetchall() if cur.description else None


def _emite(c, linii=None, tert_cui=COD_CLIENT, tert_tara="DE", data="2097-09-10", **k):
    """„Emite factură” cu payload-ul ecranului (`emitere_ecran.trimiteEmitere`: linia fără cont de venit, cota 0, la neplătitor fără
    categorie) și starea de plătitor din profil, ca use-case-ul (`uc_tenants.facturi_emite`). Întoarce răspunsul emiterii."""
    from core import facturi_api, uc_comun
    _sql(c, "SELECT 1")
    if linii is None:
        linii = [{"descriere": SERVICIU, "cantitate": 1, "um": "serv.", "pret_unitar": "500", "cota_tva": 0,
                  "categorie_tva": "serviciu_extern" if c.fel == "platitor" else None}]
    return facturi_api.emite_factura(c, linii, tert_nume="KUNDE GMBH", tert_cui=tert_cui, tert_tara=tert_tara, data_emitere=data,
                                     tert_adresa="Unter den Linden 1", tert_oras="Berlin", tert_judet="Berlin",
                                     platitor_tva=uc_comun._platitor_tva_firma(c), **k)


def _pdf(c, fid):
    from pypdf import PdfReader
    from core import factura_pdf, facturi_api, firma_profil_api
    _sql(c, "SELECT 1")
    d = facturi_api.detalii_factura(c, fid)
    return d, " ".join(" ".join(p.extract_text().split()) for p in
                       PdfReader(io.BytesIO(factura_pdf.genereaza_pdf(firma_profil_api.citeste_profil(c), d))).pages)


def _xml(c, fid):
    from core import efactura_trimitere
    _sql(c, "SELECT 1")
    xml, _f = efactura_trimitere.genereaza_din_factura(c, SCH, fid)
    return xml, ET.fromstring(xml)


def _d390(c, an=2097, luna=9):
    from core import d390
    _sql(c, "SELECT 1")
    prof, facturi = d390.pull(c, SCH, an, luna)
    return d390.calcul_d390(prof, an, luna, facturi)


# ── C156 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_c156_prestarea_neplatitorului_art317_poarta_taxare_inversa_si_codul_ro(art317):
    """Neplătitorul înregistrat art.317 emite un serviciu (500 lei) către clientul din DE (cod de TVA): linia 0% cu categoria prestării
    cu locul la client, axa „servicii”, D390 P 500; PDF-ul și detaliul de pe ecran au „Cod TVA (art.317): RO14399840” și „taxare inversă”,
    fără mențiunea scutirii art.310; niciun avertisment.
    MUTAȚIE: `prestare_317 = ... and art317 is True and ...` -> `prestare_317 = False` (`categorii_tva.verifica_linii`) -> linia O, PDF
    „CIF” și „Scutit de TVA” -> ROȘU."""
    from core import categorii_tva as ct, factura_pdf as fp
    r = _emite(art317)
    fid = r["factura_id"]
    assert r["avertismente"] == []
    # CF art.310 alin.(10) lit.b: neplătitorul „nu are voie să menționeze taxa pe factură sau pe alt document” -> cota 0, fără TVA român
    assert _sql(art317, "SELECT categorie_tva, cota_tva::text, cont_venit FROM factura_linii WHERE factura_id = %s", (fid,)) == [
        (ct.PRESTARE_IC_317, "0.00", "704")]
    assert _sql(art317, "SELECT axa_ic, tva::text FROM facturi WHERE id = %s", (fid,)) == [("servicii", "0.00")]
    # CF art.325 alin.(1) lit.c: înregistratul art.317 declară „prestările de servicii prevăzute la art. 278 alin. (2) efectuate în beneficiul
    # unor persoane impozabile nestabilite în România, dar stabilite în Uniunea Europeană” -> cod P
    res = _d390(art317)
    assert sorted((k[0], k[1], k[2], v) for k, v in res.ops.items()) == [("P", "DE", "811907980", 500)], res.ops
    d, text = _pdf(art317, fid)
    # CF art.318 alin.(1): „Codul de înregistrare în scopuri de TVA, atribuit conform art. 316 și 317, are prefixul RO”; alin.(4) lit.b
    # pct.2: înregistrații art.317 comunică codul „beneficiarului, persoană impozabilă din alt stat membru, către care prestează servicii
    # pentru care acesta este obligat la plata taxei”; CF art.319 alin.(20) lit.d: factura cuprinde „codul de înregistrare în scopuri de TVA
    # sau, după caz, codul de identificare fiscală” al prestatorului
    # antetul PDF-ului: rândul întreg al firmei (codul, apoi Registrul Comerțului), o dată; fără „CIF”
    assert (text.count("Cod TVA (art.317): RO14399840 · J12/1/2020"), text.count("CIF: 14399840")) == (1, 0), text[:400]
    # CF art.319 alin.(20) lit.m: „în cazul în care clientul este persoana obligată la plata TVA, mențiunea «taxare inversă»” — mențiunea
    # întreagă a liniei, o dată; scutirea art.310 a neplătitorului, niciodată (locul prestării e la client)
    assert (text.count(MENTIUNE_317), text.count(" ".join(fp.MENTIUNE_NEPLATITOR.split()))) == (1, 0), text[-600:]
    # ecranul (detaliul facturii, `facturi_ecran.js` -> `f.mentiuni`): aceleași mențiuni ca PDF-ul, întregi
    assert d["mentiuni"] == ["Codul de TVA al firmei pe această factură (art.317): RO14399840", MENTIUNE_317], d["mentiuni"]
    assert d["linii"][0]["categorie_tva_eticheta"] == ct.CATEGORII[ct.PRESTARE_IC_317]["eticheta"]


def test_c156_xml_efactura_iese_ae_cu_codurile_partilor(art317):
    """XML-ul e-Factura al prestării art.317: defalcarea AE 0% cu VATEX-EU-AE și „taxare inversă” (BT-120), linia AE, vânzătorul cu
    BT-31 = RO14399840, cumpărătorul cu BT-48 = DE811907980.
    MUTAȚIE: `art317 = _ct.cod_tva_art317(...)` -> `art317 = False` (`efactura_send.genereaza_xml`) -> fără BT-31 / BT-48 -> ROȘU."""
    from core import categorii_tva as ct
    fid = _emite(art317)["factura_id"]
    _x, root = _xml(art317, fid)
    sub = root.findall("cac:TaxTotal/cac:TaxSubtotal", NS)
    # Ghidul MF e-Factura v2.9 cap.3.3: „BT-151: Categoria de TVA trebuie să fie «AE»”, „BT-152: Cota de TVA trebuie să fie 0”, „BT-121 [...]
    # (VATEX-EU-AE – taxare inversă)”
    assert [(s.findtext("cac:TaxCategory/cbc:ID", namespaces=NS), s.findtext("cac:TaxCategory/cbc:Percent", namespaces=NS),
             s.findtext("cac:TaxCategory/cbc:TaxExemptionReasonCode", namespaces=NS),
             s.findtext("cac:TaxCategory/cbc:TaxExemptionReason", namespaces=NS)) for s in sub] == [
        ("AE", "0.00", "VATEX-EU-AE", ct.CATEGORII[ct.PRESTARE_IC_317]["mentiune"])]
    assert [x.text for x in root.findall("cac:InvoiceLine/cac:Item/cac:ClassifiedTaxCategory/cbc:ID", NS)] == ["AE"]
    furn = root.find("cac:AccountingSupplierParty/cac:Party", NS)
    cli = root.find("cac:AccountingCustomerParty/cac:Party", NS)
    # CF art.318 alin.(1) + alin.(4) lit.b pct.2 (codul RO art.317, comunicat beneficiarului) -> BT-31; clientul: codul lui de TVA -> BT-48
    assert furn.findtext("cac:PartyTaxScheme/cbc:CompanyID", namespaces=NS) == "RO14399840"
    assert cli.findtext("cac:PartyTaxScheme/cbc:CompanyID", namespaces=NS) == COD_CLIENT


def test_c156_prestarea_si_alte_linii_pe_aceeasi_factura_se_refuza(art317):
    """Serviciul către clientul din DE + o marfă pe aceeași factură: refuz numit (pe linia mărfii), nimic scris — liniile O și AE nu pot sta
    pe aceeași factură. MUTAȚIE: blocul `if PRESTARE_IC_317 in cats and NEPLATITOR["cod"] in cats:` -> `if False:` -> factura mixtă se emite
    -> ROȘU."""
    from core import categorii_tva as ct, facturi_api
    linii = [{"descriere": SERVICIU, "cantitate": 1, "um": "serv.", "pret_unitar": "500", "cota_tva": 0},
             {"descriere": "Marfa revanzare", "cantitate": 1, "um": "buc", "pret_unitar": "100", "cota_tva": 0}]
    with pytest.raises(facturi_api.LiniiIncomplete) as e:
        _emite(art317, linii)
    # Ghidul MF e-Factura v2.9 cap.5: „daca factura conţine o linie a facturii (BG-25) în care articolul este clasificat din perspectiva
    # codului categoriei de TVA - «Nu face obiectul TVA», aceasta trebuie să NU conţină identificatorul de TVA al Vânzătorului (BT-31) [...]
    # sau identificatorul de TVA al Cumpărătorului (BT-48)”
    assert [(x["camp"], x["cod"]) for x in e.value.campuri] == [("em-l1-categorie", ct.COD_NEPLATITOR_317_MIXT)], e.value.campuri
    assert _sql(art317, "SELECT count(*) FROM facturi")[0][0] == 0


def test_c156_clientul_fara_cod_de_tva_si_bunurile_raman_neplatitor(art317):
    """Fără cod de TVA al clientului (persoană fizică din DE) serviciul are locul în România (CF art.278 alin.(3)) -> O, CIF, scutirea art.310;
    marfa către clientul din DE rămâne O (art.317 alin.(1) lit.b e pentru servicii); clientul din România -> O, fără axă."""
    from core import categorii_tva as ct, factura_pdf as fp
    n = ct.NEPLATITOR["cod"]
    pf = _emite(art317, tert_cui=None, tert_pf=True)["factura_id"]
    marfa = _emite(art317, [{"descriere": "Marfa revanzare", "cantitate": 1, "um": "buc", "pret_unitar": "100", "cota_tva": 0}],
                   data="2097-09-11")["factura_id"]
    ro = _emite(art317, tert_cui="RO14399840", tert_tara="RO", data="2097-09-12")["factura_id"]
    for fid in (pf, marfa, ro):
        assert _sql(art317, "SELECT categorie_tva FROM factura_linii WHERE factura_id = %s", (fid,)) == [(n,)], fid
    _d, text = _pdf(art317, pf)
    # CF art.278 alin.(3): „Locul de prestare a serviciilor către o persoană neimpozabilă este locul unde prestatorul își are stabilit sediul”
    assert (text.count("CIF: 14399840 · J12/1/2020"), text.count(" ".join(fp.MENTIUNE_NEPLATITOR.split())),
            text.count("Cod TVA (art.317)"), text.count(MENTIUNE_317)) == (1, 1, 0, 0), text[:600]


def test_c156_stornarea_pastreaza_categoria_facturii_stornate(art317):
    """Stornarea prestării art.317 iese tot AE (aceeași categorie, același cod RO) și după ce firma și-a anulat înregistrarea art.317
    (CF art.317 alin.(8)); stornarea unei facturi vechi O (dinainte de reparație) iese tot O — CF art.330 alin.(1) lit.b: factura de
    stornare cuprinde informațiile facturii inițiale „cu valorile cu semnul minus”.
    MUTAȚIE: `continue   # stornarea: categoria liniei stornate` scos -> stornarea prestării, după anularea înregistrării, iese O -> ROȘU."""
    from core import categorii_tva as ct, facturi_api
    fid = _emite(art317)["factura_id"]
    vechi = _emite(art317, data="2097-09-11")["factura_id"]
    _sql(art317, "UPDATE factura_linii SET categorie_tva = %s WHERE factura_id = %s", (ct.NEPLATITOR["cod"], vechi))   # ca înainte de C156
    _sql(art317, "UPDATE firma_profil SET inreg_art317 = false")   # înregistrarea art.317 anulată după emitere
    s_nou = facturi_api.storneaza(art317, fid)["factura_id"]
    s_vechi = facturi_api.storneaza(art317, vechi)["factura_id"]
    assert _sql(art317, "SELECT categorie_tva FROM factura_linii WHERE factura_id = %s", (s_nou,)) == [(ct.PRESTARE_IC_317,)]
    assert _sql(art317, "SELECT categorie_tva FROM factura_linii WHERE factura_id = %s", (s_vechi,)) == [(ct.NEPLATITOR["cod"],)]


# ── pct.10 — facturile vechi nu se migrează ──────────────────────────────────────────────────────────────────────────────────────────
def test_pct10_factura_veche_a_neplatitorului_art317_ramane_cum_a_fost_emisa(art317):
    """Factura emisă înainte de C156 (linia „neplatitor”, axa „servicii” — C154) nu se rescrie: rândul din bază rămâne identic după ce
    se citesc detaliul, PDF-ul, XML-ul și D390; ieșirile sunt cele de dinainte (O, CIF, scutirea art.310), iar D390 rămâne P (axa ei).
    Decizia Costin 12.3 pct.10: „Facturile vechi ale neplătitorilor nu se migrează” — lotul n-aduce nicio migrare pentru ele."""
    from core import categorii_tva as ct, factura_pdf as fp
    fid = _emite(art317)["factura_id"]
    _sql(art317, "UPDATE factura_linii SET categorie_tva = %s WHERE factura_id = %s", (ct.NEPLATITOR["cod"], fid))   # forma de dinainte
    inainte = _sql(art317, "SELECT f::text FROM facturi f WHERE id = %s UNION ALL SELECT l::text FROM factura_linii l "
                           "WHERE factura_id = %s", (fid, fid))
    d, text = _pdf(art317, fid)
    xml, root = _xml(art317, fid)
    res = _d390(art317)
    assert _sql(art317, "SELECT f::text FROM facturi f WHERE id = %s UNION ALL SELECT l::text FROM factura_linii l "
                        "WHERE factura_id = %s", (fid, fid)) == inainte
    assert (text.count("CIF: 14399840 · J12/1/2020"), text.count(" ".join(fp.MENTIUNE_NEPLATITOR.split())),
            text.count(MENTIUNE_317)) == (1, 1, 0), text[:600]
    assert [x.text for x in root.findall("cac:InvoiceLine/cac:Item/cac:ClassifiedTaxCategory/cbc:ID", NS)] == ["O"]
    assert root.find("cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme", NS) is None
    assert d["mentiuni"] == [fp.MENTIUNE_NEPLATITOR], d["mentiuni"]
    assert [k[0] for k in res.ops] == ["P"], res.ops


# ── C157 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("fel", ["neinregistrat", "neales", "art317", "platitor"])
def test_c157_neplatitorul_neinregistrat_primeste_avertisment_nu_refuz(fel):
    """Serviciul către clientul din DE: neînregistratul art.317 (și alegerea lipsă din Date firmă) primește avertismentul emiterii, iar
    factura se emite (O, fără cod RO); înregistratul și plătitorul — niciun avertisment.
    MUTAȚIE: `if platitor is not False or art317 is True or ...: return []` -> `return []` mereu -> neînregistratul fără avertisment -> ROȘU."""
    from core import categorii_tva as ct
    with _firma(fel) as c:
        r = _emite(c)
        asteptat = {"neinregistrat": [ct.AVERTISMENT_FARA_ART317], "neales": [ct.AVERTISMENT_ART317_NEALES]}.get(fel, [])
        # CF art.317 alin.(1) lit.b: are obligația să solicite înregistrarea persoana impozabilă neînregistrată „dacă prestează servicii care
        # au locul în alt stat membru, pentru care beneficiarul serviciului este persoana obligată la plata taxei [...], înainte de prestarea
        # serviciului” — decizia Costin 12.3 pct.3: „avertisment la emitere, nu refuz”
        assert r["avertismente"] == asteptat, r["avertismente"]
        assert r["factura_id"]
        if fel in ("neinregistrat", "neales"):
            assert _sql(c, "SELECT categorie_tva FROM factura_linii WHERE factura_id = %s", (r["factura_id"],)) == [(ct.NEPLATITOR["cod"],)]
    # textul întreg al avertismentului: ce lipsește, temeiul (CF art.317 alin.(1) lit.b) și ce face contabilul
    assert ct.AVERTISMENT_FARA_ART317 == (
        "Firma nu e înregistrată în scopuri de TVA conform art.317, iar factura are prestări de servicii către un client din alt stat "
        "membru, care plătește el taxa. Codul fiscal cere înregistrarea înainte de prestare (art.317 alin.(1) lit.b). Factura s-a emis ca "
        "neplătitor (fără cod de TVA, fără „taxare inversă”). Cere înregistrarea la organul fiscal, apoi bifează „Înregistrată art. 317” în "
        "Date firmă.")


def test_c157_fara_avertisment_cand_nu_e_prestare_catre_ue():
    """Neînregistratul: marfa către clientul din DE, serviciul către clientul din România sau către persoana fizică din DE — fără
    avertisment (art.317 alin.(1) lit.b privește serviciile cu locul în alt stat membru, pentru care beneficiarul plătește taxa)."""
    with _firma("neinregistrat") as c:
        assert _emite(c, [{"descriere": "Marfa revanzare", "cantitate": 1, "um": "buc", "pret_unitar": "100", "cota_tva": 0}])[
            "avertismente"] == []
        assert _emite(c, tert_cui="RO14399840", tert_tara="RO", data="2097-09-11")["avertismente"] == []
        assert _emite(c, tert_cui=None, tert_pf=True, data="2097-09-12")["avertismente"] == []


def test_c157_prestarea_din_operatiuni_avertizeaza_neinregistratul(monkeypatch):
    """Operațiuni › „Livrare/prestare intracomunitară” › Servicii (`uc_tenants.vanzare_ic`), pe firma neînregistrată art.317: nota și factura
    se scriu, iar răspunsul poartă avertismentul (`avertisment`, arătat de `operatiuni_ecran.js` sub confirmare)."""
    from core import auth_api, categorii_tva as ct, intracomunitar, uc_comun, uc_tenants
    with _firma("neinregistrat") as c:
        @contextlib.contextmanager
        def _gc(*a, **k):
            with c.cursor() as cur:
                cur.execute("SET LOCAL search_path TO %s, public" % SCH)
            yield c
        monkeypatch.setattr(uc_tenants.db, "get_conn", _gc)
        monkeypatch.setattr(auth_api, "schema_tenant", lambda *a, **k: SCH)
        monkeypatch.setattr(uc_comun, "_cere_luna_deschisa", lambda *a, **k: None)
        monkeypatch.setattr(intracomunitar, "verifica_vies", lambda cod: {
            "valid": True, "nume": "KUNDE GMBH", "adresa": "Berlin", "tara": "DE", "numar": cod[2:], "eroare": None})
        r = uc_tenants.vanzare_ic(1, {"data": "2097-09-10", "valoare": 1000, "cod_tva_client": COD_CLIENT, "tip": "servicii",
                                      "cont_venit": "704", "descriere": "Consultanta IC"}, {"uid": 1})
        assert r["factura_id"] and r["inregistrare_id"]
        assert r["avertisment"] == ct.AVERTISMENT_FARA_ART317, r
