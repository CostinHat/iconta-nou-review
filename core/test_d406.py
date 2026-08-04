

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
    assert "704" in oficial, "704 (venituri servicii) trebuie sa fie in norma comerciala 'A'"



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
                "contul strain 731 (nu apartine normei 'A') trebuie SEMNALAT in avertisment, nu exclus tacit; "
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
        assert re.fullmatch(r"[A-Z0-9]{2,3}", cod), "cod UoM ne-UNECE in UOM_UNECE: %r" % cod


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
        "90": "Cheltuieli ulterioare incluse in valoarea de intrare",
        "100": "Diferente de pret pozitive", "101": "Diferente de pret negative",
        "110": "Plus de inventar", "120": "Minus de inventar",
        "130": "Ajustari pentru deprecierea stocurilor",
        "140": "Reluari de ajustari pentru deprecierea stocurilor",
        "150": "Bunuri acordate cu titlu gratuit", "160": "Bunuri degradate",
        "170": "Bunuri expirate", "180": "Alte tranzactii",
    }
    # setul de coduri = exact cele 19 oficiale (nici lipsa -> miscare nereprezentabila, nici in plus
    # -> valoare respinsa fatal de validator, nota 5)
    assert set(MISCARI_STOC) == set(OFICIAL), (
        "MISCARI_STOC difera de nomenclatorul oficial: lipsa %r / in plus %r" % (
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
    assert emise, "niciun BaseRate emis in MasterFiles"
    assert set(emise) == {str(BASE_RATE)}, "BaseRate emis divergent de BASE_RATE: %r" % sorted(set(emise))
    # fiecare valoare emisa respecta SAFBaseRate
    for v in emise:
        assert _safbaserate_valid(v), "BaseRate emis invalid: %r" % v
