

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
