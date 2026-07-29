# -*- coding: utf-8 -*-
"""REGISTRUL DE DATORIE — ce e amanat, ca test care ruleaza.

DE CE (27.07.2026, cerut de Costin): "mereu lasam cate ceva in urma de care nu mai stim si
de care nu ne mai amintim decat cand crapa ceva". DE_FACUT.md are 80.000 de caractere;
fiecare item pare rezonabil singur, impreuna sunt o datorie pe care nimeni n-o tine minte.
Iar un registru care nu e verificat mecanic se DESINCRONIZEAZA: LANSARE.md declara
"Un singur deployment activ - REZOLVAT (25.07)", dar pe 27.07 /opt/iconta era viu, cu chiar
venv-ul din care rula aplicatia.

CUM: fiecare lucru amanat = un test care afirma comportamentul CORECT, marcat
`xfail(strict=True)` cu motivul si data. Consecinte:
  - rularea suitei ARATA datoria (xfailed in raport), nu o ascunde;
  - cand cineva repara defectul, testul TRECE, iar `strict=True` il face sa PICE - te
    anunta ca e timpul sa inchizi itemul din DE_FACUT. Datoria devine zgomotoasa.

Un item intra aici DOAR daca e verificabil mecanic. Deciziile de produs, verificarile
vizuale si sarcinile juridice raman in DE_FACUT/LANSARE - dar atunci stii ca acolo e doar
ce NU se poate automatiza, nu un depozit.
"""
import datetime
import pathlib
import re

import pytest

from core import db

_AZI = datetime.date(2026, 7, 27)


def _db_ok():
    try:
        db.init_pool()
        with db.get_conn():
            return True
    except Exception:
        return False


# ============================================================
#  DATORIE FISCALA
# ============================================================
# ============================================================
#  DATORIE TEHNICA
# ============================================================
# ============================================================
#  IGIENA REGISTRULUI
# ============================================================
def test_fiecare_datorie_are_data_si_motiv():
    """Un item fara data devine invizibil in timp - exact problema pe care o rezolvam."""
    import inspect, sys
    mod = sys.modules[__name__]
    itemi = []
    for nume, fn in inspect.getmembers(mod, inspect.isfunction):
        for marca in getattr(fn, "pytestmark", []):
            if marca.name != "xfail":
                continue
            motiv = marca.kwargs.get("reason", "")
            itemi.append((nume, motiv))
    # Registrul GOL e starea DORITA, nu o eroare: inseamna ca tot ce era amanat s-a inchis
    # (reparat sau respins cu motiv). 27.07.2026 - prima zi cand s-a intamplat.
    for nume, motiv in itemi:
        assert "DATORIE" in motiv, "%s: motiv fara eticheta DATORIE" % nume
        assert re.search(r"\d{2}\.\d{2}\.\d{4}", motiv), "%s: motiv fara data" % nume
        assert len(motiv) > 60, "%s: motiv prea scurt ca sa fie util peste 3 luni" % nume


def test_datoria_nu_imbatraneste_nelimitat():
    """Semnal, nu blocaj: un item mai vechi de 90 de zile se re-decide (reparat sau RESPINS
    explicit), nu se cara la nesfarsit. Pica DOAR daca a fost ignorat un trimestru."""
    import inspect, sys
    mod = sys.modules[__name__]
    text = " ".join(m.kwargs.get("reason", "")
                    for _n, fn in inspect.getmembers(mod, inspect.isfunction)
                    for m in getattr(fn, "pytestmark", []) if m.name == "xfail")
    vechi = []
    for d in set(re.findall(r"(\d{2})\.(\d{2})\.(\d{4})", text)):
        data = datetime.date(int(d[2]), int(d[1]), int(d[0]))
        if (_AZI - data).days > 90:
            vechi.append(data.isoformat())
    assert not vechi, ("datorie mai veche de 90 de zile: %s -> repar-o sau RESPINGE-O "
                       "explicit in DECIZII.md" % sorted(vechi))
import re as _re, io as _io


def _exercita_trunchiere_den(tip, body):
    """Genereaza <tip> pe firma efemera cu nume >75 car. si afirma ca niciun atribut nu depaseste 75.
    Fix-ul de trunchiere (29.07) e aplicat in generator; testul il EXERCITA - dar doar daca firma
    datoreaza declaratia. Fara datele care o declanseaza, generatorul sare -> xfail pana la Faza 1."""
    from core import db as _db, tenant_provisioning as _tp, declaratii_api
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS ztest_dat CASCADE")
                cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), "ztest_dat"))
                cur.execute("SET LOCAL search_path TO ztest_dat, public")
                cur.execute("INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, banca, iban, "
                            "tip_decont, regim_fiscal, platitor_tva) VALUES "
                            "(1, %s, '14399840', 'Str Test 1', 'Bucuresti', 'B', 'BCR', "
                            "'RO49BCRA0000000000000000', 'L', 'real', true)", ("CABINET " + "X" * 120,))
                xml, _ = declaratii_api.genereaza(conn, "ztest_dat", tip, dict(body))
            t = xml.decode("utf-8") if isinstance(xml, (bytes, bytearray)) else xml
            lungi = [(a, len(v)) for a, v in _re.findall(r'(\w+)="([^"]*)"', t) if len(v) > 75]
            assert not lungi, "atribute >75: %s" % lungi
        finally:
            conn.rollback()


@pytest.mark.xfail(strict=True, reason="DATORIE FISCALA 29.07.2026: fix trunchiere den/adresa aplicat in d205, dar NEEXERCITAT - d205 sare 'nu se datoreaza' pe firma fara beneficiari. Il exercita o firma Faza 1 cu dividende.")
@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_datorie_d205_trunchiere_neexercitata():
    _exercita_trunchiere_den("d205", {"an": 2026})


@pytest.mark.xfail(strict=True, reason="DATORIE FISCALA 29.07.2026: fix trunchiere den/adresa aplicat in d390, dar NEEXERCITAT - d390 sare 'nu se datoreaza' pe firma fara operatiuni IC. Il exercita o firma Faza 1 cu achizitii intracomunitare.")
@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_datorie_d390_trunchiere_neexercitata():
    _exercita_trunchiere_den("d390", {"an": 2026, "luna": 6})


@pytest.mark.xfail(strict=True, reason="DATORIE FISCALA 29.07.2026: fix trunchiere den/adresa aplicat in d710, dar d710 nu e in CERERI din test_limita_text_anaf - niciun test ii verifica trunchierea. De adaugat cand se cunoaste profilul care il datoreaza.")
def test_datorie_d710_trunchiere_in_garda():
    from core.test_limita_text_anaf import CERERI
    assert any(t == "d710" for t, _ in CERERI), "d710 lipseste din garda de 75 (test_limita_text_anaf)"


@pytest.mark.xfail(strict=True, reason=(
    "DATORIE 29.07.2026: facilitatea nu se prorateaza dupa art. LXVI alin.(4) lit.a) OUG 156/2024 "
    "(preluat OUG 89/2025) - 'perioada din luna in care salariul de baza este MENTINUT la nivelul "
    "salariului minim'. Cauza: salariati are o singura coloana salariu_brut, valoarea CURENTA, fara "
    "istoric. Nu se poate sti daca salariul a fost la minim toata luna sau doar o parte (marire/scadere "
    "la mijloc de luna). Consecinta: salariat caruia i se mareste salariul pe 15 ale lunii primeste "
    "facilitatea INTREAGA, desi legea o cere proratata. "
    "ACEEASI LIPSA, TREI FATETE - modelul n-are dimensiune temporala pe contract: "
    "lit.b) angajare -> REZOLVAT (data_angajare exista); lit.d) incetare -> xfail, cere data_incetare; "
    "lit.a) mentinere -> acest xfail, cere istoric de salariu. Cand se modeleaza contractul in timp "
    "(perioada de valabilitate + istoric de salariu), cad toate trei odata. Pana atunci, fiecare e o "
    "eroare separata in calcul."))
def test_datorie_facilitate_prorata_la_mentinere_partiala():
    # Prerechizitul MECANIC (lit.a): modelul sa stie DACA salariul a fost la minim toata luna sau doar o
    # parte. salariati are doar salariu_brut CURENT, fara istoric -> mentinerea partiala nu se poate prorata.
    tpl = pathlib.Path(__file__).resolve().parent.parent / "tenant_template.sql"
    ddl = tpl.read_text(encoding="utf-8")
    assert "salariu_istoric" in ddl or "istoric_salariu" in ddl or "salariati_istoric" in ddl


@pytest.mark.xfail(strict=True, reason=(
    "DATORIE 29.07.2026: state_plata exista in schema dar nimic nu scrie in el. Statul de plata se "
    "recalculeaza la fiecare afisare, deci un stat 'emis' in ianuarie si reafisat in iulie poate iesi "
    "ALTFEL daca s-a schimbat cota, salariul minim sau codul intre timp. Pentru un document care se "
    "semneaza si se da salariatului, asta e o problema de integritate, nu de performanta. De decis: se "
    "persista la emitere (cu hash, ca declaratiile depuse) sau tabelul se scoate ca sa nu para ca exista "
    "ceva ce nu exista."))
def test_datorie_state_plata_se_persista():
    # Prerechizit MECANIC: statul de plata sa fie PERSISTAT la emitere. Azi state_plata (salariat_id+luna)
    # e tabel mort - zero INSERT in cod -> statul se recalculeaza de fiecare data (risc de integritate).
    import re as _re
    rad = pathlib.Path(__file__).resolve().parent
    patt = _re.compile(r"insert\s+into\s+[\"\w.{}]*state_plata", _re.IGNORECASE)
    scrie = any(patt.search(f.read_text(encoding="utf-8")) for f in rad.glob("*.py"))
    assert scrie, "nimic nu scrie in state_plata - statul de plata nu se persista la emitere"
