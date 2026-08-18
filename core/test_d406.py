

# ── GARD CALE NOMENCLATOR (01.08.2026): plan_oficial trebuie sa CITEASCA nomenclatorul oficial ──
# Bug prins de sweep-ul DUK: fisierul d406_nomenclatoare_anaf.properties a fost mutat in anaf_surse/,
# dar plan_oficial il cauta in radacina repo -> intorcea set GOL -> filtrarea pe norma nu rula ->
# conturile ONG (731-738, OMFP 3103/2017) scapau in SAF-T comercial -> DUK: "AccountID [731] trebuie
# sa se gaseasca in planul de conturi". Cu set gol nu se putea distinge "nomenclator lipsa" de "cale
# gresita" - de aceea gardul cere EXPLICIT continut, nu doar absenta erorii.
from core import d406 as _d406


def test_plan_oficial_citeste_nomenclatorul_norma_A():
    """Norma 'A' (societati comerciale, OMFP 1802/2014) are sute de conturi in nomenclatorul ANAF.
    Set gol = fisierul nu e gasit (cale stale) -> filtrarea moare tacut. Contul ONG 731 NU e in
    norma comerciala; un cont comercial standard (704) DA."""
    oficial = _d406.plan_oficial("A")
    assert len(oficial) > 100, "plan_oficial('A') GOL/mic (%d) - nomenclatorul nu e citit (cale?)" % len(oficial)
    assert "731" not in oficial, "731 (ONG) nu apartine normei comerciale 'A'"
    assert "704" in oficial, "704 (venituri servicii) trebuie să fie în norma comerciala 'A'"


def test_conturi_ong_731_738_norma_specifica():
    """[Regula 2/5 - verificat la sursa 18.08.2026] Conturile de venituri ONG 731-738 (OMFP 3103/2017)
    sunt NORMA-SPECIFICE: absente din planul comercial 'A' (OMFP 1802/2014), prezente in planul ONG.
    Sursa = nomenclatorul validatorului oficial ANAF (d406_nomenclatoare_anaf.properties, arbitrul).
    Blocheaza faptul care justifica excluderea din D406 la o firma norma-A: nu e un drop orb al clasei 73,
    ci filtrare pe planul normei declarate. Fara latura ONG, gardul nu ar distinge 'exclus corect' de 'clasa 73
    lipseste peste tot'."""
    A = _d406.plan_oficial("A")
    ONG = _d406.plan_oficial("ONG")
    assert len(ONG) > 100, "plan_oficial('ONG') GOL/mic (%d) - nomenclatorul ONG nu e citit (cheie/cale?)" % len(ONG)
    C73 = ("731", "732", "733", "734", "735", "736", "737", "738")
    gresit_in_A = [c for c in C73 if c in A]
    lipsa_in_ONG = [c for c in C73 if c not in ONG]
    assert not gresit_in_A, "conturi 73x (venituri ONG) gasite GRESIT in norma comerciala 'A': %s" % gresit_in_A
    assert not lipsa_in_ONG, "conturi 73x LIPSA din planul ONG (ar trebui sa existe, OMFP 3103/2017): %s" % lipsa_in_ONG




def test_taxcode_livrari_period_aware():
    """TaxCode-ul SAF-T pentru livrari e PERIOD-AWARE pe data facturii: ANAF a schimbat codurile cu
    01.08.2025 (Legea 141/2025). O factura dinainte foloseste codurile epocii (19/9/5), una de dupa
    cele noi (21/11/9/5). Fara period-awareness, o raportare retroactiva (luna < 08.2025) emitea
    coduri gresite (19% negasit in tabela noua -> default 310312 = taxare inversa)."""
    from core.d406 import _taxcode_livrari
    from datetime import date
    assert _taxcode_livrari(21, date(2026, 3, 1)) == "310344"     # post: 21%
    assert _taxcode_livrari(11, date(2025, 8, 1)) == "310351"     # post: 11% (chiar la granita)
    assert _taxcode_livrari(19, date(2025, 6, 1)) == "310309"     # pre: 19% (exista DOAR pre)
    assert _taxcode_livrari(9,  date(2025, 6, 1)) == "310310"     # pre: 9%
    assert _taxcode_livrari(9,  date(2026, 1, 1)) == "310357"     # post: 9% (cod DIFERIT de pre!)
    assert _taxcode_livrari(21, None) == "310344"                 # data lipsa -> tabela curenta (post)


def _db_ok_d406():
    from core import db
    try:
        db.init_pool()
        with db.get_conn():
            return True
    except Exception:
        return False


import pytest as _pytest_d406


@_pytest_d406.mark.skipif(not _db_ok_d406(), reason="DB indisponibil")
def test_conturi_straine_de_norma_sunt_semnalate_nu_excluse_tacit():
    """Cluster plan conturi pe norma: un cont din plan_conturi care NU e in nomenclatorul normei firmei
    (ex. 731 venituri ONG intr-o firma soc-com, baza_contabila='A') se EXCLUDE din D406 (ANAF il respinge:
    'ID-ul contului trebuie sa se gaseasca in planul de conturi'), DAR NU tacit - genereaza il SEMNALEAZA in
    avertisment, numind contul exclus (decizie de clasa, ca operatiunile N in d394 - Costin 04.08). Fara asta,
    un cont cu sold ar disparea din SAF-T fara ca contabilul sa stie."""
    from core import db, tenant_provisioning as _tp, d406 as _d406mod
    SCHEMA = "ztest_d406_strain"
    db.init_pool()
    with db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA)
                cur.execute(_tp.parametrizeaza_template(
                    open("tenant_template.sql", encoding="utf-8").read(), SCHEMA))
                cur.execute("SET search_path TO %s, public" % SCHEMA)
                cur.execute(
                    "INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, caen, banca, iban, "
                    "declarant_nume, declarant_prenume, declarant_functie, platitor_tva, tip_decont, regim_fiscal) "
                    "VALUES (1, 'TEST SRL', '14399840', 'Str. Testul 1', 'Bucuresti', 'B', '6920', 'BCR', "
                    "'RO49BCRA0000000000000000', 'POPESCU', 'GHEORGHE', 'EXPERT CONTABIL', true, 'L', 'real')")
                # 731 = venituri ONG (OMFP 3103/2017) - NU e in planul soc-com 'A' -> cont STRAIN
                cur.execute("INSERT INTO plan_conturi (simbol, denumire, tip, sold_creditor) "
                            "VALUES ('731', 'Venituri din cotizatii ONG', 'Pasiv', 100) "
                            "ON CONFLICT (simbol) DO UPDATE SET denumire = EXCLUDED.denumire")
            _xml, res = _d406mod.genereaza(conn, SCHEMA, 2026, 6)
            av = " ".join(res.avertismente)
            assert "731" in av and "EXCLUS" in av.upper(), (
                "contul străin 731 (nu apartine normei 'A') trebuie SEMNALAT în avertisment, nu exclus tacit; "
                "avertismente: %s" % res.avertismente)
        finally:
            conn.rollback()


def test_uom_unece_mapare_coduri_valide():
    """Cluster UoM UN/ECE: UOM_UNECE mapeaza unitatile RO in coduri UN/ECE Recommendation 20. Codurile-tinta
    sunt validator-confirmate (15.07.2026: 'BUC' respins 'nu se afla in lista'; H87/KGM/GRM/TNE/LTR/MLT/MTR/CMT/
    KMT/MTK/MTQ/HUR/KWH/MWH prezente in D406Validator.jar - verificat prin extractie). Verifica maparea + default
    H87 + semnalarea la necunoscut (mai bine o unitate implicita DECLARATA decat un XML respins)."""
    import re
    from core.d406 import uom_unece, UOM_UNECE, UOM_IMPLICIT
    assert UOM_IMPLICIT == "H87"
    assert uom_unece("buc") == ("H87", True)
    assert uom_unece("kg") == ("KGM", True)
    assert uom_unece("mp") == ("MTK", True) and uom_unece("mc") == ("MTQ", True)
    assert uom_unece("H87") == ("H87", True)              # deja cod UN/ECE -> pass-through
    assert uom_unece("unitate_necunoscuta") == ("H87", False)   # default + SEMNAL (False)
    assert uom_unece("") == ("H87", False) and uom_unece(None) == ("H87", False)
    # niciun cod-tinta nu e o unitate romaneasca respinsa de validator (ex. BUC)
    assert "BUC" not in set(UOM_UNECE.values())
    # toate valorile sunt coduri UN/ECE (2-3 caractere alfanumerice majuscule)
    for cod in set(UOM_UNECE.values()):
        assert re.fullmatch(r"[A-Z0-9]{2,3}", cod), "cod UoM ne-UNECE în UOM_UNECE: %r" % cod


def test_movementtype_nomenclator_oficial():
    """Cluster MovementType nomenclator: MISCARI_STOC = nomenclatorul OFICIAL ANAF de miscari de
    produse in stocuri (anaf_surse/d406_schema_anaf.xlsx, foaia 'Nomenclator stocuri', 19 coduri).
    Codurile completeaza campul MovementType (MasterFiles/2.8 MovementTypeTable) si 'Movement subtype'
    (SourceDocuments/StockMovement) - AMBELE OBLIGATORII in raportarea de stocuri. Nota 5 a foii: o
    valoare din AFARA listei -> eroare FATALA, D406 respins. De aceea gardul cere setul COMPLET, nu un
    subset: un nomenclator incomplet ar face o miscare reala nereprezentabila (ex. 40 'Retur produse
    vandute') sau ar impinge-o pe un default gresit. Dormant azi (sectiunile de stocuri se emit goale
    lunar - <MovementTypeTable/>, <MovementOfGoods/>), dar pazit ca sa fie corect din prima cand se
    cableaza raportarea de stocuri. Sursa = foaia oficiala, nu comentariul (LECTIE: comentariul nu e
    proba)."""
    import re
    from core.d406 import MISCARI_STOC, MOVEMENT_IMPLICIT
    # Nomenclatorul oficial, inghetat din foaia ANAF "Nomenclator stocuri" (Cod_miscari_stoc -> RO).
    OFICIAL = {
        "10": "Achizitie", "20": "Productie", "30": "Vanzare",
        "40": "Retur produse vandute", "50": "Retur produse achizitionate",
        "60": "Reduceri comerciale primite", "70": "Consum", "80": "Transfer intern",
        "90": "Cheltuieli ulterioare incluse în valoarea de intrare",
        "100": "Diferente de preț pozitive", "101": "Diferente de preț negative",
        "110": "Plus de inventar", "120": "Minus de inventar",
        "130": "Ajustari pentru deprecierea stocurilor",
        "140": "Reluari de ajustari pentru deprecierea stocurilor",
        "150": "Bunuri acordate cu titlu gratuit", "160": "Bunuri degradate",
        "170": "Bunuri expirate", "180": "Alte tranzacții",
    }
    # setul de coduri = exact cele 19 oficiale (nici lipsa -> miscare nereprezentabila, nici in plus
    # -> valoare respinsa fatal de validator, nota 5)
    assert set(MISCARI_STOC) == set(OFICIAL), (
        "MISCARI_STOC difera de nomenclatorul oficial: lipsă %r / în plus %r" % (
            sorted(set(OFICIAL) - set(MISCARI_STOC)), sorted(set(MISCARI_STOC) - set(OFICIAL))))
    # etichetele RO coincid (eticheta informativa in rapoartele ANAF, dar sursa unica = foaia oficiala)
    assert MISCARI_STOC == OFICIAL
    # default-ul e un cod VALID din lista (nota 5: un default din afara listei = D406 respins)
    assert MOVEMENT_IMPLICIT in MISCARI_STOC
    # nota 4 a foii: cod alfanumeric de maxim 9 caractere
    for cod in MISCARI_STOC:
        assert re.fullmatch(r"[A-Za-z0-9]{1,9}", cod), "cod MovementType ne-conform nota 4: %r" % cod


def test_baserate_encoding_pro_rata_fractie():
    """Cluster BaseRate (encoding pro-rata): BaseRate din TaxCodeDetails (MF.TT.11) e o FRACTIE in
    [0.0000, 1.0000] unde 1.0000 = 100.00%, NU un procent 0-100. Documentul ANAF (d406_schema_anaf.xlsx,
    foaia '2. MasterFiles', MF.TT.11) e INTERN CONTRADICTORIU: proza spune 'Standard is 100 (whole amount)
    / 60 if 60%' (text OECD-legacy pe procente) DAR restrictia OBLIGATORIE din aceeasi celula e
    'Restrictie: [0,0000 - 1,0000] (unde 1,0000 = 100,00%)' iar tipul e SAFBaseRate = decimal(totalDigits
    5, fractionDigits 4). Restrictia CASTIGA: 100 sau 60 ar viola [0-1] -> D406 respins. Deci BASE_RATE=1
    (=1.0000=100%) e CORECT pentru codurile LIVRARI standard (integral; livrarile n-au pro-rata de
    deducere - deducerea e la achizitii). LECTIE (a 3-a in campanie): comentariul vechi cita GRESIT doc-ul
    ('standard 1'); concluzia (1) era corecta dar din RESTRICTIE, nu din proza care spune 100. Un fix la
    100 ar sparge declaratia."""
    import re
    from decimal import Decimal
    from core import d406
    from core.d406 import BASE_RATE

    def _safbaserate_valid(v):
        """True daca v respecta restrictia ANAF [0,0000-1,0000] SI tipul SAFBaseRate = decimal(5,4)."""
        d = Decimal(str(v))
        if not (Decimal("0.0000") <= d <= Decimal("1.0000")):     # restrictia ANAF [0,1]
            return False
        _s, digits, exp = d.normalize().as_tuple()                # tipul XSD: totalDigits<=5, fractionDigits<=4
        return max(0, -exp) <= 4 and len(digits) <= 5

    # 1) encoding: intreaga suma deductibila = 1 (=1.0000=100%), in restrictia oficiala
    assert Decimal(str(BASE_RATE)) == Decimal("1")
    assert _safbaserate_valid(BASE_RATE), "BASE_RATE iese din SAFBaseRate/restrictia [0,1]"
    # 2) DINTII gardului: valorile-capcana din proza (procente) sunt RESPINSE de restrictie
    assert not _safbaserate_valid(100), "100 (procent) trebuie respins de restrictia [0,1]"
    assert not _safbaserate_valid(60), "60 (procent) trebuie respins de restrictia [0,1]"
    # exemple valide de pro-rata partiala, ca fractie (nu procent): 0.5 = 50%, 0.6 = 60%
    assert _safbaserate_valid(Decimal("0.5")) and _safbaserate_valid(Decimal("0.6"))
    # 3) SURSA UNICA: valoarea EMISA in XML == BASE_RATE pentru fiecare cod de taxa (nu literal divergent)
    res = d406.Rezultat(an=2026, luna=3, prof={}, conturi=[], clienti=[], furnizori=[],
                        cote_tva=d406.COTE_TVA_STANDARD)
    xml = "\n".join(d406._masterfiles(res))
    emise = re.findall(r"<BaseRate>([^<]*)</BaseRate>", xml)
    assert emise, "niciun BaseRate emis în MasterFiles"
    assert set(emise) == {str(BASE_RATE)}, "BaseRate emis divergent de BASE_RATE: %r" % sorted(set(emise))
    # fiecare valoare emisa respecta SAFBaseRate
    for v in emise:
        assert _safbaserate_valid(v), "BaseRate emis invalid: %r" % v


def test_registration_number_partener_si_firma_proprie():
    """Cluster registration_number (00+CUI) | d406. Doua reguli oficiale distincte (d406_schema_anaf.xlsx,
    foaia '5. Structures'):

    PARTENER (S.C.1 Customer/Supplier CompanyStructure) - cod unic = tip(2 cifre) + cod, cu exemplele
    EXACTE din schema:
      00 + CUI          operator RO, FARA prefixul fiscal "RO" (ex. 004221306)
      01 + tara + VAT   operator UE (non-RO), verificat VIES - ex. 01EL123456789 sau 01HU12345678
      02 + tara + VAT   operator non-UE - ex. 02TK123005284
    ATENTIE Grecia: prefixul VAT/VIES e "EL", NU ISO "GR" - schema exemplifica LITERAL "01EL123456789".
    Bug reparat: _UE_NON_RO avea "GR" (nu "EL") -> un partener grec "EL..." cadea pe 02 (non-UE) = partener
    UE raportat gresit ca non-UE. Acum EL e recunoscut UE si un "GR" din surse ISO se normalizeaza la EL.

    FIRMA PROPRIE (Header/Company, 5.5 S.CMH.1 CompanyHeaderStructure): rezident platitor TVA -> VAT CU
    prefixul RO; neplatitor -> CUI fara prefix. (Regula diferita de partener, unde "00" NU ia RO.)"""
    from core.d406 import _partener_registration_number as prn, registration_number as rn

    # --- PARTENER: exemplele oficiale exacte ---
    assert prn("RO4221306") == "004221306"          # RO platitor: 00 + CUI, prefixul RO scos
    assert prn("4221306") == "004221306"            # bare numeric RO -> 00
    assert prn("EL123456789") == "01EL123456789"    # Grecia VIES: EL, UE (exemplul oficial)
    assert prn("GR123456789") == "01EL123456789"    # ISO "GR" din surse -> normalizat la EL (ANAF cere EL)
    assert prn("HU12345678") == "01HU12345678"      # UE: 01 + tara + VAT (exemplul oficial)
    assert prn("DE811234567") == "01DE811234567"    # UE: Germania
    assert prn("TK123005284") == "02TK123005284"    # non-UE: 02 + tara + VAT (exemplul oficial Turcia)
    assert prn("") is None and prn(None) is None     # fara cod -> None
    # "00" nu accepta substringul RO (regula 1.1 validare sintactica)
    assert "RO" not in prn("RO4221306")[2:]

    # --- FIRMA PROPRIE ---
    assert rn({"cui": "RO12345678", "platitor_tva": True}) == "RO12345678"    # platitor: cu RO
    assert rn({"cui": "12345678", "platitor_tva": True}) == "RO12345678"      # platitor: RO adaugat
    assert rn({"cui": "12345678", "platitor_tva": False}) == "12345678"       # neplatitor: fara RO
    assert rn({"cui": "12345678"}) == "RO12345678"    # implicit platitor (majoritatea D406)
    assert rn({"cui": ""}) == ""


def _res_d406_complet():
    """Un D406 cu TOATE sub-sectiunile SourceDocuments populate (vanzari+cumparari+plati+note),
    profil minim izolat. CUI-uri reale, deja acceptate de validator (ALTEX 4221306)."""
    from decimal import Decimal
    from datetime import date
    from core import d406 as m
    prof = {"cui": "14399840", "nume": "FIRMA TEST SRL", "adresa": "Str. Test 1", "oras": "Bucuresti",
            "cod_postal": "010101", "baza_contabila": "A", "platitor_tva": True}
    CID = "004221306"
    conturi = [m.Cont(id="4111", descriere="Clienti", cont_standard="4111", tip="Activ"),
               m.Cont(id="707", descriere="Venituri marfuri", cont_standard="707", tip="Pasiv"),
               m.Cont(id="4427", descriere="TVA colectata", cont_standard="4427", tip="Pasiv"),
               m.Cont(id="401", descriere="Furnizori", cont_standard="401", tip="Pasiv"),
               m.Cont(id="371", descriere="Marfuri", cont_standard="371", tip="Activ"),
               m.Cont(id="4426", descriere="TVA deductibila", cont_standard="4426", tip="Activ"),
               m.Cont(id="5121", descriere="Banca", cont_standard="5121", tip="Activ")]
    client = [m.Partener(id=CID, nume="ALTEX ROMANIA SRL", cui="RO4221306", oras="Bucuresti")]
    nota = m.Nota(id="1", data=date(2026, 6, 10), descriere="Contare factura 1", linii=[
        m.LinieNota(record_id="1", cont="4111", descriere="", debit=Decimal("1210"), credit=Decimal("0"), cont_partener_id=CID),
        m.LinieNota(record_id="2", cont="707", descriere="", debit=Decimal("0"), credit=Decimal("1000"), cont_partener_id=CID),
        m.LinieNota(record_id="3", cont="4427", descriere="", debit=Decimal("0"), credit=Decimal("210"), cont_partener_id=CID)])
    fv = m.Factura(nr="1", data=date(2026, 6, 10), partener_id=CID, partener_nume="ALTEX ROMANIA SRL",
                   tip="380", cont="4111", linii=[m.LinieFactura(nr=1, cont="707", descriere="Marfa",
                   cantitate=Decimal("1"), pret_unitar=Decimal("1000"), valoare=Decimal("1000"), sens="C",
                   tva_cod="310344", tva_procent=Decimal("21"), tva_suma=Decimal("210"))])
    fc = m.Factura(nr="F100", data=date(2026, 6, 12), partener_id=CID, partener_nume="ALTEX ROMANIA SRL",
                   tip="380", cont="401", linii=[m.LinieFactura(nr=1, cont="371", descriere="Marfa cump",
                   cantitate=Decimal("1"), pret_unitar=Decimal("500"), valoare=Decimal("500"), sens="D",
                   tva_cod="301344", tva_procent=Decimal("21"), tva_suma=Decimal("105"))])
    pl = m.Plata(ref="P1", data=date(2026, 6, 13), metoda="01", partener_id=CID, descriere="Plata",
                 linii=[m.LiniePlata(nr=1, cont="5121", descriere="incasare", suma=Decimal("1210"), sens="D", doc_sursa="")])
    return m.construieste(prof, 2026, 6, conturi, client, [], note=[nota],
                          facturi_vanzare=[fv], facturi_cumparare=[fc], plati=[pl])


def _valideaza_xsd(xml):
    """Valideaza XML-ul D406 contra schemei SAF-T oficiale (saft.xsd), aliniind namespace-ul
    d406->d406t (schema are targetNamespace d406t; structura SAF-T e identica). (ok, [mesaje])."""
    from lxml import etree
    xml_t = xml.replace("mfp:anaf:dgti:d406:declaratie:v1", "mfp:anaf:dgti:d406t:declaratie:v1")
    doc = etree.fromstring(xml_t.encode("utf-8"))
    sch = etree.XMLSchema(etree.parse("/opt/duk/saft/saft.xsd"))
    ok = sch.validate(doc)
    return ok, [e.message for e in sch.error_log]


def test_structura_xsd_conforma_saft():
    """Cluster structura XSD (Header/MasterFiles/GLE) | d406: XML-ul D406 e VALIDAT MECANIC contra
    schemei oficiale SAF-T (/opt/duk/saft/saft.xsd). Schema are targetNamespace 'd406t' (varianta pe
    cerere) dar STRUCTURA SAF-T (AuditFile/Header/MasterFiles/GeneralLedgerEntries/SourceDocuments,
    tipuri, ordine, obligatorii) e identica cu d406 lunar - se aliniaza namespace-ul pt validare.

    (1) Cu TOATE sub-sectiunile populate -> XSD-valid ZERO erori: intreaga structura SAF-T conforma.
    (2) Raportarea lunara OMITE sub-sectiunile de liste goale (DUK-confirmat 16.07.2026: emise vide ->
        respinse 'elementul ... minimum 1 ori'). Fata de schema d406t asta produce EXACT O diferenta
        (PurchaseInvoices absent inainte de MovementOfGoods) - comportament lunar corect, nu eroare de
        structura. Gardul CONFIRMA ca asta e SINGURA abatere (nici una in plus).

    Validarea XSD e complementara validarii DUK (d406 DUK = xfail preexistent 'cont referit absent',
    validare SEMANTICA - aici verificam STRUCTURA)."""
    import os
    import pytest as _pt
    if not os.path.exists("/opt/duk/saft/saft.xsd"):
        _pt.skip("saft.xsd indisponibil (server-only)")
    from core import d406

    # (1) toate sub-sectiunile populate -> zero erori structurale
    res_full = _res_d406_complet()
    ok, erori = _valideaza_xsd(d406.build_xml(res_full))
    assert ok, "D406 complet NU e XSD-valid:\n" + "\n".join(erori[:20])

    # (2) lunar cu doar vanzari -> exact O abatere: PurchaseInvoices omis (comportament lunar corect)
    res_luna = _res_d406_complet()
    res_luna.facturi_cumparare = []
    res_luna.plati = []
    ok2, erori2 = _valideaza_xsd(d406.build_xml(res_luna))
    assert not ok2, "asteptam abaterea lunara (PurchaseInvoices omis), dar XML-ul a validat integral"
    assert len(erori2) == 1, "asteptam EXACT o abatere lunara, sunt %d:\n%s" % (len(erori2), "\n".join(erori2))
    assert "PurchaseInvoices" in erori2[0], "abaterea nu e omisiunea PurchaseInvoices: %s" % erori2[0]



@_pytest_d406.mark.skipif(not _db_ok_d406(), reason="DB indisponibil")
def test_genereaza_emite_liniile_reale_din_factura_linii():
    """GOLD pe DATE REALE — inchide golul: niciun test nu exercita pull() cu randuri REALE din
    factura_linii (cazul traia doar intr-un comentariu, d406.py:1279). Regresia 27.07.2026: in DB
    'Deseuri fier vechi' 1000 kg x 5,00 lei/kg -> in SAF-T iesea 1 buc x 5000 lei (cantitate, UM si
    descriere FALSE catre ANAF). Aici: factura cu DOUA linii reale distincte (kg + buc) trebuie sa
    apara FIDEL in <Invoice>, nu ca o singura linie sintetica 1 x net. Mutatia care il probeaza:
    daca _factura_xml revine la linia sintetica, count(<InvoiceLine>)==1 si <InvoiceUOM>KGM</> dispare."""
    from core import db, tenant_provisioning as _tp, d406 as _d406mod
    from decimal import Decimal
    SCHEMA = "ztest_d406_linii_reale"
    db.init_pool()
    with db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA)
                cur.execute(_tp.parametrizeaza_template(
                    open("tenant_template.sql", encoding="utf-8").read(), SCHEMA))
                cur.execute("SET search_path TO %s, public" % SCHEMA)
                cur.execute(
                    "INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, caen, banca, iban, "
                    "declarant_nume, declarant_prenume, declarant_functie, platitor_tva, tip_decont, regim_fiscal) "
                    "VALUES (1, 'TEST SRL', '14399840', 'Str. Testul 1', 'Bucuresti', 'B', '4711', 'BCR', "
                    "'RO49BCRA0000000000000000', 'POPESCU', 'GHEORGHE', 'EXPERT CONTABIL', true, 'L', 'real')")
                # factura de vanzare cu DOUA linii reale, reconciliate cu antetul (net 6000 + tva 1260 = 7260)
                cur.execute(
                    "INSERT INTO facturi (numar, data_emitere, tert_cui, tert_nume, total, tva, directie) "
                    "VALUES ('FV100', '2026-06-10', 'RO14399840', 'Client SRL', 7260, 1260, 'emisa') RETURNING id")
                fid = cur.fetchone()[0]
                cur.execute("INSERT INTO factura_linii (factura_id, descriere, um, cantitate, pret_unitar, cota_tva) "
                            "VALUES (%s, 'Deseuri fier vechi', 'kg', 1000, 5, 21)", (fid,))
                cur.execute("INSERT INTO factura_linii (factura_id, descriere, um, cantitate, pret_unitar, cota_tva) "
                            "VALUES (%s, 'Transport', 'buc', 1, 1000, 21)", (fid,))
            xml, res = _d406mod.genereaza(conn, SCHEMA, 2026, 6)
            # (1) liniile reale ajung in modelul pull() - nu o linie sintetica
            fv = res.facturi_vanzare
            assert len(fv) == 1 and len(fv[0].linii) == 2, "ambele linii reale, nu una sintetica"
            l0 = fv[0].linii[0]
            assert l0.descriere == "Deseuri fier vechi" and l0.cantitate == Decimal("1000") and l0.um == "KGM", (
                "kg -> UN/ECE KGM, cantitate 1000 reala, descriere fidela; got %r" % (l0,))
            assert l0.valoare == Decimal("5000") and l0.tva_procent == Decimal("21") and l0.tva_suma == Decimal("1050")
            # (2) ajung FIDEL in XML (nu 1 buc x net)
            assert "<Quantity>1000.00</Quantity>" in xml, "cantitatea reala 1000 lipsește din XML"
            assert "<InvoiceUOM>KGM</InvoiceUOM>" in xml, "UM reala (kg->KGM) lipseste din XML"
            assert "<Description>Deseuri fier vechi</Description>" in xml, "descrierea reala lipsește din XML"
            assert xml.count("<InvoiceLine>") == 2, "doua linii reale in <Invoice>, nu o linie sintetica"
        finally:
            conn.rollback()
