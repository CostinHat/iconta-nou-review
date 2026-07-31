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
from core import agenda

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


@pytest.mark.xfail(strict=True, reason="DATORIE 30.07.2026: staleness pe continutul Sesiunii B nu se poate verifica mecanic pana nu exista teste N3 (cap-coada pe firma). Etapele Fazei 1 sunt neincepute si nu se mapeaza pe fisiere, deci nu exista pe ce compara 'marcat done vs realitate'. Cade singur cand apar testele N3.")
def test_datorie_staleness_sesiune_b_content():
    # Se aprinde (xpass -> strict pica) cand prima etapa a Fazei 1 primeste bifa = are teste N3 cap-coada.
    b = agenda.stare_sesiune_b()
    assert b is not None and b["etape_facute"] > 0


@pytest.mark.xfail(strict=True, reason="DATORIE 30.07.2026: cele 8 mentiuni canonizate la DUK/eFactura regula n-au fost re-verificate la sursa - s-a schimbat doar markerul. Daca vreuna cita o regula GRESITA inainte, canonizarea a facut-o sa arate corect si sa ramana greșita. De verificat fiecare cod (A91b, R28, R17, R11b, R15, F10_68, BR-RO-100, BR-RO-110) contra documentatiei de validator: ce spune regula si daca e cea aplicabila acolo.")
def test_datorie_reguli_validator_verificate_la_sursa():
    # Se inchide cand verificarea la sursa e consemnata in DECIZII.md (marker stabil, case-insensitive).
    # strict=True: cand devine adevarat, xpass -> pica -> semnaleaza sa scoti xfail-ul.
    dz = (pathlib.Path(__file__).resolve().parent.parent / "DECIZII.md").read_text(encoding="utf-8")
    assert "reguli validator verificate la sursa" in dz.lower()


@pytest.mark.xfail(strict=True, reason="DATORIE 30.07.2026: R17/R28/R32 din D300/D394 au fost lasate bare ca RANDURI de declaratie, dedus din CONTEXT, nu verificat in structura oficiala a formularului. Daca vreunul e de fapt regula de validator, a rămas nemarcat si gardul nu-l va prinde. De verificat in structura oficiala D300 si D394 ce reprezinta fiecare.")
def test_datorie_d300_d394_randuri_vs_reguli_verificate():
    # Se inchide cand verificarea in structura oficiala e consemnata in DECIZII.md (marker stabil).
    dz = (pathlib.Path(__file__).resolve().parent.parent / "DECIZII.md").read_text(encoding="utf-8")
    assert "d300/d394 randuri-vs-reguli verificate in structura oficiala" in dz.lower()


@pytest.mark.xfail(strict=True, reason="DATORIE 30.07.2026: formatul ANAF structura <formular> <versiune> nu e pazit mecanic. Fraza 'structura oficiala D300' apare identic in proza explicativa si in citare, deci un gard ar da fals-pozitive pe descrieri. Cele 18 mentiuni au fost canonizate manual la PASUL 3; o regresie viitoare rămâne pe seama review-ului. De reluat daca apare o forma de marcare care distinge citarea de proza (ex. un prefix sau un registru separat de structuri).")
def test_datorie_gard_structura_absent():
    # Se inchide cand test_temeiuri.py capata un gard de structura (functie cu 'structura' in nume).
    tt = (pathlib.Path(__file__).resolve().parent / "test_temeiuri.py").read_text(encoding="utf-8")
    assert re.search(r"def test_\w*structura\w*\(", tt)


@pytest.mark.xfail(strict=True, reason="DATORIE 31.07.2026: deducere personala de baza 45% pentru 4+ persoane (Cod fiscal art.77 alin.4) confirmata pe pliant ANAF (AJFP Vrancea) + redare text codificat (noulcodfiscal.ro), NEGASIT direct la MO/legislatie.just.ro - documentul consolidat e prea mare pentru fetch (intoarce doar Titlul I). De reverificat tabelul alin.4 in Monitorul Oficial si consemnat in DECIZII.md.")
def test_datorie_deducere_45pct_4plus_neconfirmat_la_mo():
    # Se inchide cand reverificarea la MO e consemnata in DECIZII.md (marker stabil, case-insensitive).
    # strict=True: cand devine adevarat, xpass -> pica -> semnaleaza sa scoti xfail-ul.
    dz = (pathlib.Path(__file__).resolve().parent.parent / "DECIZII.md").read_text(encoding="utf-8")
    assert "deducere 45% 4+ verificat in monitorul oficial" in dz.lower()


@pytest.mark.xfail(strict=True, reason="DATORIE 31.07.2026: Cod fiscal art.77 alin.(12)-(13) - deducerea de 100 lei/copil la mai multi angajatori se acorda UNUI SINGUR parinte, pe baza de declaratie. Codul (deducere_personala) primeste copii_scoala si aplica 100 lei/copil neconditionat, fara sa trateze care parinte o ia sau dubla acordare la angajatori diferiti. De implementat cand exista fluxul de declaratie parinte. Se inchide cand e consemnat in DECIZII.md.")
def test_datorie_deducere_copil_parinte_multi_angajatori():
    # Se inchide cand tratarea alin.(12)-(13) e consemnata in DECIZII.md (marker stabil, case-insensitive).
    dz = (pathlib.Path(__file__).resolve().parent.parent / "DECIZII.md").read_text(encoding="utf-8")
    assert "deducere copil parinte unic multi angajatori tratat" in dz.lower()


@pytest.mark.xfail(strict=True, reason="DATORIE 31.07.2026: pliant ANAF - daca in aceeasi luna se folosesc mai multe valori ale salariului minim, se ia in calcul CEA MAI MICA. cota() intoarce valoarea in vigoare la la_data, nu implementeaza explicit 'cea mai mica din luna'. Nu musca in iulie 2026 (o singura valoare, 4325 de la 1 iul). De tratat daca o modificare de salariu minim pica la mijloc de luna. Se inchide cand e consemnat in DECIZII.md.")
def test_datorie_cota_cea_mai_mica_valoare_din_luna():
    # Se inchide cand regula 'cea mai mica valoare in luna' e consemnata in DECIZII.md (marker stabil).
    dz = (pathlib.Path(__file__).resolve().parent.parent / "DECIZII.md").read_text(encoding="utf-8")
    assert "salariu minim cea mai mica valoare din luna tratat" in dz.lower()


@pytest.mark.xfail(strict=True, reason="DATORIE FISCALA 31.07.2026: tichetele de masa se acorda DOAR pe zile EFECTIV LUCRATE (HG 1045/2018 art.10 alin.(3): numar 'cel mult egal cu numarul de zile lucrate'). Zilele de concediu de odihna, delegatie/detasare cu indemnizatie, invoire, absenta NU dau dreptul la tichet. Codul foloseste tichet_zile = zile_lucratoare - concediu_medical (stat_plata_api.py, d112.py) -> ACORDA tichete pe zilele de concediu de odihna si absente -> nominal supra-declarat -> baza CASS/impozit gresita in D112. Datele brute exista in pontaj (F135: concediu_odihna/absent_*/delegatie) DAR (a) modelul de prezenta nu distinge 'pontaj neintrodus' de 'tot prezent' (ambele 0 randuri); (b) deciziile 17.07 (F135 informativ) + 20.07 (opt.A) l-au decuplat deliberat de payroll, iar limita 20.07 acoperea doar absentele nemotivate, NU concediul de odihna. Fixul = alimentarea tichet_zile din pontaj SAU tracking documentat al CO/absentelor (ca la CM) - feature multi-sit + reversarea/rafinarea F135, NU o linie. Se inchide cand e implementat si consemnat in DECIZII.md.")
def test_datorie_tichete_masa_zile_efectiv_lucrate():
    # Se inchide cand numarul de tichete = zile efectiv lucrate (CO/delegare/absente scad) e implementat
    # si consemnat in DECIZII.md (marker stabil, case-insensitive).
    dz = (pathlib.Path(__file__).resolve().parent.parent / "DECIZII.md").read_text(encoding="utf-8")
    assert "tichete masa zile efectiv lucrate din pontaj implementat" in dz.lower()


@pytest.mark.xfail(strict=True, reason="DATORIE FISCALA 31.07.2026: excesul voucherelor de vacanta peste plafonul anual (6 sal.minime, OUG 8/2009 art.1) = avantaj salarial INTEGRAL (CAS+CASS+impozit, in baza salariala). Decizie de scop (Costin, DECIZII 31.07): cele 3 scutiri (CF art.76(3)h, 142 lit.r, 157(2)) sunt conditionate de aceeasi formula 'acordate potrivit legii' - nu exista citire care sa piarda doua si sa pastreze a treia. Codul azi taxeaza CASS+impozit dar NU CAS = INCOERENT, nu conservator. DE IMPLEMENTAT la clusterul D112 (nu acum): excesul intra in baza salariala, deci misca deducerea personala (art.77, degresiva) - se face cu tot lantul sub ochi. DUK accepta CAS pe exces DOAR prin baza salariala (S731/S74). Se inchide cand e implementat la D112, DUK-valid, consemnat in DECIZII.md.")
def test_datorie_cas_peste_plafon_vacanta():
    # Se inchide cand CAS pe excesul de vacanta e declarat corect in D112 si validat pe DUK, consemnat
    # in DECIZII.md (marker stabil, case-insensitive).
    dz = (pathlib.Path(__file__).resolve().parent.parent / "DECIZII.md").read_text(encoding="utf-8")
    assert "cas peste plafon vacanta declarat in d112 validat duk" in dz.lower()


@pytest.mark.xfail(strict=True, reason="DATORIE 31.07.2026: doua citate literale la clusterul tichete confirmate din sursa SECUNDARA (noulcodfiscal.ro), NEreverificat verbatim pe legislatie.just.ro (portalul randeaza dinamic, pagina se trunchiaza la fetch automat): (a) art.25 alin.(3) - litera exacta b) vs c) pt deductibilitatea la profit a tichetelor de masa/vacanta; (b) art.78 alin.(2) lit.a) - textul care confirma ca CASS-ul se deduce din baza impozitului pe tichete (bifa #3). Fondul e confirmat prin DERIVARE (art.157 face CASS obligatorie din 2024 -> art.78 deduce contributiile obligatorii), dar litera de pe portalul autoritativ ramane de reconfirmat pe PDF-ul MO. Se inchide cand citatele sunt reconfirmate verbatim si consemnate in DECIZII.md.")
def test_datorie_citate_literale_tichete_portal():
    # Se inchide cand art.25 alin.(3) lit.b/c si art.78 alin.(2) lit.a sunt reconfirmate verbatim de pe
    # legislatie.just.ro (nu doar noulcodfiscal) si consemnate in DECIZII.md (marker stabil).
    dz = (pathlib.Path(__file__).resolve().parent.parent / "DECIZII.md").read_text(encoding="utf-8")
    assert "citate literale tichete reconfirmate verbatim pe portal" in dz.lower()


@pytest.mark.xfail(strict=True, reason="DATORIE 31.07.2026: teste care ASERTEAZA valoarea GRESITA apara bugul si impiedica repararea (a patra aparitie a clasei azi): test_cm_cas_mereu_zero (cas=0 pe CM, REPARAT 31.07 prin unificarea CM -> test_cm_cas_25pct_uniform); test_coduri_75 (aserta carantina 07=75%, reparat 667f46d); precedente - FIX5 (tabelul avea 3700 la 2025, aparat pana la corectie) si gard cat.9 gdpr (test_gdpr_functional, fisier necolectat care parea acoperire). Un test scris pe presupunere nu verifica nimic. AMPLOARE MASURATA (inventar 31.07.2026): 114 teste asertaza o constanta fiscala - 29 CU temei (act+articol pe linie), 85 FARA. Dominant: cota TVA 21% hardcodata fara temei in ~15 module contabile (Legea 141/2025 citata doar in d394/d212); d212 e modelul (temei pe fiecare sectiune). NU e reparabil intr-un tur - plan separat, decis de Costin. DE FACUT: trecere SISTEMATICA peste toate testele care asertaza constante fiscale (cote/procente/valori), sa se verifice ca fiecare are TEMEIUL citat pe linie (act+articol). Se inchide cand trecerea e facuta si consemnata in DECIZII.md.")
def test_datorie_teste_care_apara_buguri():
    # Se inchide cand trecerea sistematica peste testele care asertaza constante fiscale (fiecare cu temei
    # citat) e facuta si consemnata in DECIZII.md (marker stabil, case-insensitive).
    dz = (pathlib.Path(__file__).resolve().parent.parent / "DECIZII.md").read_text(encoding="utf-8")
    assert "teste cu constante fiscale trecute sistematic cu temei citat" in dz.lower()


@pytest.mark.xfail(strict=True, reason="DATORIE 31.07.2026: D112 nu genereaza corect campurile D-field pentru toate codurile CM SPECIALE. REPARAT: cod 08 (maternitate) - agregate C2 pe Rd.3 (C2_31/32/34/36) + split 100% FNUASS, DUK VALID. RAMAS: (a) cod 06 (urgente) cere D_11 (cod urgenta, nomenclator HG 423/2020, C(3)) - concedii_medicale nu are campul, cere camp de date nou + UI; (b) sub-randuri C2 infectocontagioase (cod 05, Rd.1.1-1.4 cu conditii D_12/data) nedefalcate, emise 0 (corect cat timp nu exista cod 05 in luna). Se inchide cand cod 06 + sub-randurile 05 trec DUK, consemnat in DECIZII.md.")
def test_datorie_cm_dfield_coduri_speciale():
    # Se inchide cand D112 cu CM cod 08 (maternitate) si 06 (urgente) trece DUKIntegrator, consemnat in DECIZII.md.
    dz = (pathlib.Path(__file__).resolve().parent.parent / "DECIZII.md").read_text(encoding="utf-8")
    assert "cm d112 coduri speciale d-field validate duk" in dz.lower()


@pytest.mark.xfail(strict=True, reason="DATORIE 31.07.2026: D394 exclude linia scutita (cota 0) catre partener cu CUI (structD394 pct.217: cota 0 permisa doar pentru LS/AS/ASI/N/V) - o linie scutita pe o factura tip L catre partener RO cu CUI e IGNORATA cu avertisment, nu inclusa. Proba DUK pe factura MULTI-COTA cu exact acest caz (21+11+scutit catre CUI -> DUK valid + incadrare corecta a scutitului) NEFACUTA - probele D394 (test_d300_d394_paritate) folosesc date care evita cazul (A4 = date consistente fara scutit-catre-CUI). Se inchide cand proba e facuta si consemnata in DECIZII.md.")
def test_datorie_d394_scutit_catre_cui_proba_duk():
    dz = (pathlib.Path(__file__).resolve().parent.parent / "DECIZII.md").read_text(encoding="utf-8")
    assert "d394 linie scutita catre cui proba duk facuta" in dz.lower()


@pytest.mark.xfail(strict=True, reason="DATORIE 31.07.2026: factura_pdf - fix-ul cota_tva None -> eroare (runda 1 B) presupune ca genereaza_pdf atinge linia INAINTE de alte campuri lipsa; testul verifica DOAR ca ridica pe cota None, NU ca PDF-ul se genereaza corect pe un profil REAL complet (reportlab, toate campurile firma/factura). Se inchide cand PDF-ul e probat pe profil real (genereaza bytes valizi) si consemnat in DECIZII.md.")
def test_datorie_factura_pdf_proba_pe_profil_real():
    dz = (pathlib.Path(__file__).resolve().parent.parent / "DECIZII.md").read_text(encoding="utf-8")
    assert "factura_pdf probat pe profil real complet" in dz.lower()


@pytest.mark.xfail(strict=True, reason="DATORIE 31.07.2026 (GRI, nu verde): verdictul 'divergenta d300/d394 pe reverse charge = cerinta ANAF, nu bug' (runda 2 B) sta pe DEDUCTIE din cod (d300.pull nu citeste taxare_inversa) + practica, NU pe text MO. De reconfirmat la SURSA PRIMARA (structura oficiala D300 / OPANAF) ca reverse charge se trateaza DOAR manual (rd.12) si ca D394 tip C la cota bunului e cerinta, nu optiune de implementare. Pana atunci verdictul ramane GRI. Se inchide cand e reconfirmat pe sursa oficiala si consemnat in DECIZII.md.")
def test_datorie_d300_reverse_charge_manual_reconfirmat_mo():
    dz = (pathlib.Path(__file__).resolve().parent.parent / "DECIZII.md").read_text(encoding="utf-8")
    assert "d300 reverse charge doar manual reconfirmat la sursa oficiala" in dz.lower()
