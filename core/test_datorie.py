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

# [INCHISA 07.08.2026] upgrade la MO a INCEPUT: primul temei MO+text_citat verbatim in COTE = plafon_facilitate_salariu_minim @2025 (OUG 156/2024 art.LXVI). Coada REDARE ramasa se stinge pe masura ce se capteaza verbatim. Vezi DECIZII.md.
def test_datorie_temeiuri_toate_redare_niciun_mo_verbatim():
    """Cand macar UN Temei din COTE e MO cu text_citat verbatim, datoria incepe sa se stinga."""
    from core.common import COTE
    mo_cu_text = [(n, str(d)) for n, intr in COTE.items() for d, v, t in intr
                  if getattr(t, "nivel_sursa", None) == "MO" and getattr(t, "text_citat", None)]
    assert mo_cu_text, "niciun temei MO cu verbatim inca - registrul sta pe REDARE"



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
    assert not vechi, (
        "datorie mai veche de 90 de zile: %s -> repar-o sau RESPINGE-O explicit in DECIZII.md. "
        "(Daca data e A UNUI ACT NORMATIV, nu vechimea datoriei, scrie-o cu luna in litere - "
        "ex. '1 august 2025' - ca garda sa n-o citeasca; vezi conventia in TESTE.md.)"
        % sorted(vechi))
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
    "DATORIE 29.07.2026, RESTATUATA 20.08.2026: state_plata nu se persista LA EMITERE. Statul se "
    "recalculeaza la fiecare afisare, deci un stat 'emis' in ianuarie si reafisat in iulie poate iesi "
    "ALTFEL daca s-a schimbat cota, salariul minim sau codul intre timp. Pentru un document care se "
    "semneaza si se da salariatului, asta e o problema de integritate, nu de performanta. De decis: se "
    "persista la emitere (cu hash, ca declaratiile depuse) sau tabelul se scoate ca sa nu para ca exista "
    "ceva ce nu exista. || CORECTIE 20.08.2026: formularea veche spunea 'nimic nu scrie in el' si era "
    "FALSA - main.py scria, din GET /stat-plata (efect secundar al unei citiri). Testul n-a prins-o "
    "fiindca isi cauta dovada DOAR in core/*.py, niciodata in main.py: o datorie care descria o lume pe "
    "care nu o verifica. Scrierea-din-GET a fost scoasa (RFC 9110 §9.2.1: GET trebuie sa fie safe), deci "
    "azi chiar nimic nu scrie - dar asta e o consecinta, nu starea de la care s-a plecat. Cautarea acopera "
    "acum si radacina repo-ului."))
def test_datorie_state_plata_se_persista():
    # Prerechizit MECANIC: statul de plata sa fie PERSISTAT la emitere. Azi state_plata (salariat_id+luna)
    # e tabel mort - zero INSERT in cod -> statul se recalculeaza de fiecare data (risc de integritate).
    import re as _re
    rad = pathlib.Path(__file__).resolve().parent
    patt = _re.compile(r"insert\s+into\s+[\"\w.{}]*state_plata", _re.IGNORECASE)
    # [20.08.2026] cauta si in RADACINA repo-ului (main.py), nu doar in core/ - vechea forma se uita
    # doar langa ea si de-aia a ratat exact scrierea care exista.
    _fisiere = list(rad.glob("*.py")) + list(rad.parent.glob("*.py"))
    scrie = any(patt.search(f.read_text(encoding="utf-8", errors="replace")) for f in _fisiere)
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


# [INCHISA 06.08.2026] scara deducerii 20/25/30/35/45% (art.77 alin.4, 4+ = 45%) confirmata VERBATIM la MO in anaf_surse/cod_fiscal_227_2015_consolidat.html; codul foloseste 45%; nivel_sursa ridicat REDARE->MO. Vezi DECIZII.md.
def test_datorie_deducere_45pct_4plus_neconfirmat_la_mo():
    # Se inchide cand reverificarea la MO e consemnata in DECIZII.md (marker stabil, case-insensitive).
    # strict=True: cand devine adevarat, xpass -> pica -> semnaleaza sa scoti xfail-ul.
    dz = (pathlib.Path(__file__).resolve().parent.parent / "DECIZII.md").read_text(encoding="utf-8")
    assert "deducere 45% 4+ verificat in monitorul oficial" in dz.lower()


@pytest.mark.xfail(strict=True, reason="DATORIE 02.08.2026 (art.77 alin.(12)-(13)): deducerea de 100 lei/copil e NECABLATA - copii_scoala nu e coloana pe salariati, niciun apelant real n-o trece >0, deci nu se acorda azi. Gard defensiv pus (ridica daca copii_scoala>0 fara flag declaratie_copii, citand art.77(12)-(13)) ca la cablare sa esueze VIZIBIL, nu sa acorde dublu. Cablarea completa (input copii scolarizati + declaratie parinte + UI) = build-new, in §PRODUS. Se inchide cand feature-ul e cablat cu temei art.77(10)b/(12)/(13).")
def test_datorie_deducere_copil_parinte_multi_angajatori():
    # Se inchide cand tratarea alin.(12)-(13) e consemnata in DECIZII.md (marker stabil, case-insensitive).
    dz = (pathlib.Path(__file__).resolve().parent.parent / "DECIZII.md").read_text(encoding="utf-8")
    assert "deducere copil parinte unic multi angajatori tratat" in dz.lower()


# [INCHISA 06.08.2026] salariu_minim_luna() aplica art.77(3) (cea mai mica valoare din luna), verificat verbatim la MO + proba no-op D112 (byte-identic) - vezi DECIZII.md.
def test_datorie_cota_cea_mai_mica_valoare_din_luna():
    # Se inchide cand regula 'cea mai mica valoare in luna' e consemnata in DECIZII.md (marker stabil).
    dz = (pathlib.Path(__file__).resolve().parent.parent / "DECIZII.md").read_text(encoding="utf-8")
    assert "salariu minim cea mai mica valoare din luna tratat" in dz.lower()


def test_datorie_tichete_masa_zile_efectiv_lucrate():
    # Se inchide cand numarul de tichete = zile efectiv lucrate (CO/delegare/absente scad) e implementat
    # si consemnat in DECIZII.md (marker stabil, case-insensitive).
    dz = (pathlib.Path(__file__).resolve().parent.parent / "DECIZII.md").read_text(encoding="utf-8")
    assert "tichete masa zile efectiv lucrate din pontaj implementat" in dz.lower()


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


@pytest.mark.xfail(strict=True, reason="DATORIE 31.07.2026 (ingustata 02.08): sub-randurile C2 infectocontagioase (cod 05, Rd.1.1-1.4 cu conditii D_12/data) nedefalcate, emise 0 (corect cat timp nu exista cod 05 in luna). INCHISE separat 02.08: cod 08 (maternitate, Rd.3 DUK VALID) si cod 06 (urgente, D_11 + DUK VALID - test_d112_cod06_urgenta_valid_duk). RAMAS DOAR cod 05: se inchide cand un cert cod 05 in luna e defalcat pe sub-randuri si trece DUK, consemnat in DECIZII.md.")
def test_datorie_cm05_subrows_infectocontagioase():
    # Se inchide cand un certificat cod 05 in luna e defalcat pe sub-randurile Rd.1.1-1.4 si trece DUK.
    dz = (pathlib.Path(__file__).resolve().parent.parent / "DECIZII.md").read_text(encoding="utf-8")
    assert "cm05 sub-randuri infectocontagioase defalcate duk" in dz.lower()


# [INCHISA 02.08.2026] CM4 plafon 12 sm implementat in _calcul_cm_core (venituri_lunare) - vezi DECIZII.md.
def test_datorie_cm_plafon_12sm():
    dz = (pathlib.Path(__file__).resolve().parent.parent / "DECIZII.md").read_text(encoding="utf-8")
    assert "cm plafon 12 salarii minime aplicat in calcul_cm" in dz.lower()


# [INCHISA 07.08.2026] forma pre-141 a art.17(1) (75% uniform) obtinuta verbatim la MO (anaf_surse/oug_158_2005_pre_L141.html) + varianta datata in _VARIANTE_PROCENT_CM selectata pe data certificatului INITIAL (art.XI); probe pe granita 31 iulie / 1 august 2025 - vezi DECIZII.md.
def test_datorie_cm_art_xi_regim_initial():
    dz = (pathlib.Path(__file__).resolve().parent.parent / "DECIZII.md").read_text(encoding="utf-8")
    assert "cm art xi regim dupa certificat initial verificat la sursa" in dz.lower()


# [INCHISA 13.08.2026] MF/D406 calculeaza amortizarea PE METODA (CF art.28 alin.6/7/8/8^1):
# core/d406_active.py rescris (liniara/degresiva/accelerata/superaccelerata) + golden pe fiecare
# metoda (core/test_d406_amortizare.py) + proba DUK pe tenant_013 - vezi DECIZII.md.
def test_datorie_mf_metode_amortizare():
    dz = (pathlib.Path(__file__).resolve().parent.parent / "DECIZII.md").read_text(encoding="utf-8")
    assert "mf amortizare degresiva si accelerata calculate dupa metoda activului" in dz.lower()


# [INCHISA 02.08.2026] IMCA implementat in d101 (art.18^1) + probat DUK - vezi DECIZII.md.
def test_datorie_d101_imca():
    dz = (pathlib.Path(__file__).resolve().parent.parent / "DECIZII.md").read_text(encoding="utf-8")
    assert "d101 imca impozit minim cifra de afaceri implementat si probat duk" in dz.lower()


# [INCHISA 06.08.2026] D394 reclasifica L->LS (nu mai arunca linia scutita catre RO CUI) + proba DUK multi-cota (21+11+scutit) - vezi DECIZII.md.
def test_datorie_d394_scutit_catre_cui_proba_duk():
    dz = (pathlib.Path(__file__).resolve().parent.parent / "DECIZII.md").read_text(encoding="utf-8")
    assert "d394 linie scutita catre cui proba duk facuta" in dz.lower()


@pytest.mark.xfail(strict=True, reason="DATORIE 31.07.2026: factura_pdf - fix-ul cota_tva None -> eroare (runda 1 B) presupune ca genereaza_pdf atinge linia INAINTE de alte campuri lipsa; testul verifica DOAR ca ridica pe cota None, NU ca PDF-ul se genereaza corect pe un profil REAL complet (reportlab, toate campurile firma/factura). Se inchide cand PDF-ul e probat pe profil real (genereaza bytes valizi) si consemnat in DECIZII.md.")
def test_datorie_factura_pdf_proba_pe_profil_real():
    dz = (pathlib.Path(__file__).resolve().parent.parent / "DECIZII.md").read_text(encoding="utf-8")
    assert "factura_pdf probat pe profil real complet" in dz.lower()


def test_datorie_d300_reverse_charge_manual_reconfirmat_mo():
    dz = (pathlib.Path(__file__).resolve().parent.parent / "DECIZII.md").read_text(encoding="utf-8")
    assert "d300 reverse charge doar manual reconfirmat la sursa oficiala" in dz.lower()


@pytest.mark.xfail(strict=True, reason="DATORIE 31.07.2026 (clasa noua - unealta care se inseala singura): verificator_conformitate.py a produs 13 fals-pozitive prin propriul bug (regex-ul de rute rata 'async def' -> a marcat 13 rute ca fara schema_tenant cand ele il aveau). Instrumentul care MASOARA conformitatea nu e el insusi masurat: niciun test nu verifica ca analizatorul verificatorului clasifica corect (rute/resolveri/goluri). Un gard cu fals-pozitive se dezactiveaza si moare (GARZI regula 3); un gard cu fals-NEGATIVE tace pe un leak real. DE FACUT: teste pe logica de analiza a verificatorului (fixturi de cod cu rute known-good / known-bad -> asertie ca gardul le clasifica corect). Se inchide cand analizatorul verificatorului are teste si e consemnat in DECIZII.md.")
def test_datorie_verificatorul_nu_e_el_insusi_testat():
    dz = (pathlib.Path(__file__).resolve().parent.parent / "DECIZII.md").read_text(encoding="utf-8")
    assert "analizatorul verificatorului are teste pe clasificare" in dz.lower()


@pytest.mark.xfail(strict=True, reason="DATORIE 03.08.2026 (cluster cote TVA->randuri | d300): achizitiile deductibile cu cota 9% (art.III Legea 141/2025) NU se pot declara AUTOMAT in D300 - structura v12.0.0 le pune la Rd.25.1 (R75), dar validatorul DUKIntegrator INSTALAT respinge R75 ('nu trebuie sa exista aici'); R76 e taxare inversa (Rd.27.4, legat de R72 prin R96.2/R96.3). Reparat in cluster: 11% deductibil mutat de la R74 (=19% legacy, marja 18-20%) la R23 (Rd.25, DUK valid); 9% deductibil scos din auto si semnalat pentru declarare MANUALA (altfel TVA de plata supraevaluata). Vechiul cod emitea R76 la 9% -> respins de DUK + pierdut din totalul R27. RAMAS: cand validatorul DUK instalat accepta R75 (sau se identifica randul deductibil 9% corect la sursa), 9% deductibil trece pe auto cu proba DUK. Se inchide cand 9% deductibil se emite automat pe un rand DUK-valid, cu proba, consemnat in DECIZII.md.")
def test_datorie_d300_9pct_deductibil_auto():
    dz = (pathlib.Path(__file__).resolve().parent.parent / "DECIZII.md").read_text(encoding="utf-8")
    assert "d300 achizitii deductibile 9% emise automat pe rand duk valid" in dz.lower()


def test_datorie_d300_exigibilitate_tva_la_incasare():
    dz = (pathlib.Path(__file__).resolve().parent.parent / "DECIZII.md").read_text(encoding="utf-8")
    assert "d300 aplica exigibilitatea tva la incasare pentru firme pe regim" in dz.lower()


