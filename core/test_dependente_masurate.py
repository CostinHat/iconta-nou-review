# -*- coding: utf-8 -*-
"""GARD — registrul de dependențe nu se poate depărta nici de măsurătoare, nici de document.

**CE PAZEȘTE, și de ce sunt trei lucruri, nu unul.**

  1. **DOCUMENTUL nu îmbătrânește tăcut.** Blocul din `DEPENDENTE_P2.md` e GENERAT din
     `firma_rezumat.ASPECTE`; garda îl regenerează și îl compară **caracter cu caracter**. Un
     document care repetă o listă din cod e a doua copie a ei — și prima care rămâne în urmă.
  2. **REGISTRUL nu se poate subția sub măsurătoare.** Artefactul `masuratori/p2/dependente_masurate.json`
     e ce a găsit `scripts/scan_dependente.py` rulând chiar funcțiile de calcul. Orice tabel măsurat
     ca sursă trebuie să fie în registru. *Un tabel-sursă care iese din registru nu produce o eroare,
     produce o valoare veche etichetată `curent` — cea mai tăcută formă de defect.*
  3. **Fiecare sursă din registru chiar are trigger**, întrebând BAZA, nu lista din cod despre ea
     însăși.

**Aserțiune anti-vacuu.** Fiecare probă verifică întâi că are ce compara: un artefact gol, un
registru gol sau un domeniu de căutare greșit ar face toate cele trei probe să treacă verde despre
o lume pe care n-o văd.
"""
import json
import os
import sys

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RAD)
sys.path.insert(0, os.path.join(_RAD, "scripts"))

from core import firma_rezumat as FR  # noqa: E402
import scan_dependente as SD  # noqa: E402

ARTEFACT = os.path.join(_RAD, "masuratori", "p2", "dependente_masurate.json")
DOC = os.path.join(_RAD, "DEPENDENTE_P2.md")


def _artefact():
    if not os.path.exists(ARTEFACT):
        pytest.fail("lipsește artefactul măsurătorii (%s) — matricea n-are pe ce se sprijini. "
                    "Rulează `python3 -m scripts.scan_dependente`." % ARTEFACT)
    with open(ARTEFACT, encoding="utf-8") as f:
        return json.load(f)


# ============================================================================
#  1. DOCUMENTUL
# ============================================================================
def test_blocul_din_document_e_cel_generat_acum():
    assert os.path.exists(DOC), "lipsește %s" % DOC
    with open(DOC, encoding="utf-8", newline="") as f:
        s = f.read()
    i, j = s.find(SD.MARCAJ_START), s.find(SD.MARCAJ_STOP)
    assert i >= 0 and j > i, "marcajele blocului generat lipsesc din document"
    in_doc = s[i:j + len(SD.MARCAJ_STOP)]
    acum = SD.bloc_matrice()
    assert len(acum.splitlines()) > 10, "generatorul produce un bloc gol — proba n-ar putea eșua"
    assert in_doc == acum, (
        "blocul din DEPENDENTE_P2.md nu mai e cel generat din `firma_rezumat.ASPECTE`.\n"
        "Rescrie-l: `python3 -m scripts.scan_dependente --doc`")


def test_documentul_numeste_fiecare_aspect():
    """Anti-vacuu pe documentul însuși: un bloc generat corect dintr-un registru gol ar trece."""
    with open(DOC, encoding="utf-8") as f:
        s = f.read()
    assert FR.TOATE, "registrul de aspecte e gol"
    for a in FR.TOATE:
        assert "`%s`" % a in s, "aspectul %s nu apare în document" % a


# ============================================================================
#  2. REGISTRUL contra MĂSURĂTORII
# ============================================================================
def test_registrul_cuprinde_tot_ce_s_a_masurat():
    """Direcția care doare: măsurat ca sursă, absent din registru = invalidare care nu se întâmplă."""
    inv = _artefact()
    aspecte = inv.get("aspecte") or {}
    assert aspecte, "artefactul n-are niciun aspect — proba n-ar putea eșua"

    lipsa = {}
    for a, r in aspecte.items():
        if a not in FR.ASPECTE:
            continue                       # aspect retras (v. `tip_firma`) — are proba lui
        masurate = {t[1] for t in r.get("plan", []) if str(t[0]).startswith("tenant_")}
        masurate -= set(SD.CONTABILITATE_PROPRIE)
        assert masurate or a in ("solduri", "plan_conturi", "vector"), (
            "aspectul %s n-are nicio sursă măsurată — artefactul e gol pentru el" % a)
        declarate = set(FR.ASPECTE[a]["tabele"])
        if masurate - declarate:
            lipsa[a] = sorted(masurate - declarate)
    assert not lipsa, (
        "tabele MĂSURATE ca surse și absente din registru: %s\n"
        "O scriere în ele n-ar invalida aspectul, iar valoarea veche ar rămâne `curent`." % lipsa)


def test_publicul_masurat_e_urmarit_sau_declarat_neurmarit():
    inv = _artefact()
    urmarite = set(FR.tabele_publice_urmarite())
    neurmarite = set(FR.NEURMARITE_PUBLIC)
    assert urmarite, "niciun tabel public urmărit — proba n-ar putea eșua"
    neclasificate = {}
    for a, r in (inv.get("aspecte") or {}).items():
        if a not in FR.ASPECTE:
            continue
        pub = {t[1] for t in r.get("plan", []) if t[0] == "public"}
        pub -= set(SD.CONTABILITATE_PROPRIE) | urmarite | neurmarite
        if pub:
            neclasificate[a] = sorted(pub)
    assert not neclasificate, (
        "surse din `public` nici urmărite, nici declarate neurmărite: %s\n"
        "Pune-le în `tabele_public` al aspectului, sau în `NEURMARITE_PUBLIC` cu motivul."
        % neclasificate)


def test_artefactul_spune_pe_cate_firme_a_fost_masurat():
    """*Punctul orb e firma, nu ecranul.* O matrice măsurată pe o singură firmă vede doar ramurile
    pe care datele ei le ating — `miscari_stoc` a apărut la 2 firme din 20."""
    inv = _artefact()
    assert inv.get("firme_masurate", 0) >= 5, (
        "măsurat pe %s firme — prea puține ca reuniunea să acopere ramurile rare"
        % inv.get("firme_masurate"))
    assert inv.get("firme_cu_confruntare", 0) >= 1, (
        "niciun eșantion cu confruntare PLAN/STAT: nimic nu spune că PLAN n-a ratat o clasă întreagă")


def test_cele_doua_instrumente_nu_s_au_contrazis():
    """Dezacordul nu e interzis — e informație. Dar trebuie SĂ FIE VĂZUT, nu descoperit peste o lună."""
    inv = _artefact()
    dezacord = {a: r["doar_stat"] for a, r in (inv.get("aspecte") or {}).items()
                if r.get("doar_stat")}
    assert not dezacord, (
        "STAT a văzut tabele pe care PLAN nu le-a văzut: %s\n"
        "Sunt citiri din corpul unei funcții — PLAN e orb acolo. Adaugă-le în registru manual."
        % dezacord)


# ============================================================================
#  3. TRIGGERELE, întrebând BAZA
# ============================================================================
def test_fiecare_sursa_din_registru_are_trigger_pe_fiecare_firma():
    from core import db as _db
    try:
        _db.init_pool()
        with _db.get_conn() as c:
            rap = FR.verifica_triggerele(c)
    except Exception as e:      # noqa: BLE001
        pytest.skip("fara baza de date: %s" % e)
    assert not rap["domeniu_gol"], (
        "verificarea n-a găsit nicio firmă — ar raporta zero lipsuri despre o lume pe care n-o vede")
    assert rap["lipsa"] == [], "tabele-sursă fără trigger: %s" % rap["lipsa"][:20]
    assert rap["proiectii_tip_firma"] >= rap["firme_vazute"], (
        "%d proiecții `tip_firma` pentru %d firme — lista portofoliului ar arăta gol pentru unele"
        % (rap["proiectii_tip_firma"], rap["firme_vazute"]))
