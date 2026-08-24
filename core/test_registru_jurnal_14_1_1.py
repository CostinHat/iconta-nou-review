# -*- coding: utf-8 -*-
"""GARD — Registrul-jurnal păstrează cele trei coloane cerute de norma 14-1-1.

Confruntat cu OMFP 2634/2015 anexa 2 (cod 14-1-1) pe 24.08.2026: din opt coloane, patru ieșeau, iar
trei lipseau — **coloana 1** (numărul curent de la 1 ianuarie), **coloana 3** (felul, numărul și data
documentului justificativ) și **totalizarea lunară**. Reparate prin derivare la citire.

CE FACE IMPOSIBIL: ca vreuna dintre cele trei să dispară tăcut dintr-un artefact care se prezintă la
control. Un registru din care lipsește coloana documentului justificativ nu se poate apăra.

ASERTEAZĂ PE STRUCTURĂ, NU PE TEXT (regula lui Costin, 24.08.2026).

**Și nici prin `in` pe un set.** A doua trecere, tot 24.08: cinci aserțiuni de aici erau `"x" in
chei` — apartenență **adevărată** cât timp `chei` e un set, dar care se transformă tăcut în sub-șir
dacă dreapta devine vreodată un `str`, **arătând identic**. Forma folosită acum e operatorul de
mulțime, `chei >= {"x"}`: pe un șir **crapă**, în loc să treacă. Fișierul care a produs regula n-are
voie să fie excepția ei.

Prima formă a acestui fișier a
fost chiar instanța care a produs regula: căuta `nr_curent` și `note_fara_document` ca **șiruri**
oriunde în rută — și le găsea în **docstringul rutei, scris de mine**. Curățarea de docstring, la
încercarea următoare, ștergea și SQL-ul din același f-string, deci gardul greșea în **ambele**
direcții. Acum ruta se **parsează** (`ast`), iar cheile de răspuns se citesc din **nodurile `Dict`**
ale funcției — o cheie care nu e construită nu poate fi găsită într-un comentariu.

UNDE NU SE POATE ASERTĂ PE STRUCTURĂ, ȘI DE CE: fereastra `ROW_NUMBER` trăiește într-un **SQL**, iar
SQL-ul e un șir chiar și în AST. Nu există aici un parser de SQL, iar a aduce unul pentru o aserțiune
ar fi mai mult risc decât acoperire. Compromisul e declarat și îngustat: AST-ul **localizează**
constanta (deci nu se poate confunda cu un comentariu sau cu un docstring), și abia în interiorul ei
se caută textul. Restul aserțiunilor n-au nevoie de asta.

CE NU VERIFICĂ, declarat: dacă valorile sunt corecte pe datele unei firme anume — aia cere baza de
date și e o probă, nu un gard. Aici se păzește **contractul**: că cele trei elemente sunt produse, și
că numerotarea e pe AN, nu pe lună.
"""
import ast
import io
import os
from datetime import date

from core import jurnal_api as _j

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _functia():
    """Nodul AST al rutei `tenant_jurnal` din main.py — structură, nu text."""
    arb = ast.parse(io.open(os.path.join(RAD, "main.py"), encoding="utf-8").read())
    for n in ast.walk(arb):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == "tenant_jurnal":
            return n
    raise AssertionError("nu mai găsesc funcția `tenant_jurnal` în main.py — gardul măsoară ce nu vede")


def _chei_construite():
    """Cheile literale ale TUTUROR dicționarelor construite în rută.

    Un docstring nu e un `ast.Dict`, un comentariu nu ajunge în AST. Deci ce se găsește aici e
    **construit**, nu descris — exact distincția pe care forma veche a acestui gard n-o putea face."""
    return {k.value
            for n in ast.walk(_functia()) if isinstance(n, ast.Dict)
            for k in n.keys
            if isinstance(k, ast.Constant) and isinstance(k.value, str)}


def _sql():
    """Constantele de șir lungi din rută, concatenate: SQL-ul, localizat prin AST."""
    return "\n".join(n.value for n in ast.walk(_functia())
                     if isinstance(n, ast.Constant) and isinstance(n.value, str)
                     and len(n.value) > 200)


# ── coloana 3: derivarea documentului justificativ ────────────────────────────
def test_documentul_se_deriva_din_factura():
    """Norma cere FELUL, NUMARUL si DATA. Toate trei trebuie sa apara."""
    d = _j.document_justificativ(None, "factura", "ALFA-E-", "001", date(2026, 8, 10))
    assert d == "Factură ALFA-E-001 din 2026-08-10", d


def test_document_ref_scris_explicit_are_prioritate():
    d = _j.document_justificativ("Chitanța 42/2026", "factura", "X", "9", date(2026, 1, 1))
    assert d == "Chitanța 42/2026"


def test_CALIBRARE_fara_sursa_documentul_ramane_LIPSA():
    """Cel mai important test din fisier. O nota fara factura si fara document_ref NU primeste un
    document inventat - primeste None, adica lipsa vizibila.

    Un registru care ar completa un document inexistent ar face exact ce s-a scos din ecranul de NIR
    prin R29: ar raspunde in locul omului. O coloana goala e onesta; una plina si falsa nu."""
    assert _j.document_justificativ(None, None, None, None, None) is None
    assert _j.document_justificativ("", None, None, None, None) is None
    assert _j.document_justificativ("   ", None, None, None, None) is None


# ── coloanele 1, 3 si totalizarea: CHEI CONSTRUITE in rută ───────────────────
def test_ruta_construieste_numarul_curent():
    assert _chei_construite() >= {"nr_curent"}, (
        "coloana 1 (numărul curent) nu mai e cheie construită în răspuns")


def test_ruta_construieste_documentul_justificativ():
    assert _chei_construite() >= {"document"}, "coloana 3 nu mai e cheie construită în răspuns"


def test_ruta_totalizeaza_lunar():
    lipsa = {"total_debit", "total_credit"} - _chei_construite()
    assert not lipsa, "totalizarea lunară cerută de 14-1-1 lipsește: %s" % sorted(lipsa)


def test_absenta_documentului_se_NUMARA_nu_se_ascunde():
    """P6: ce nu se poate deriva se spune. Un registru cu jumatate din coloana 3 goala, fara sa spuna
    cate, arata la fel cu unul complet."""
    assert _chei_construite() >= {"note_fara_document"}, (
        "numarul notelor fara document justificativ nu mai e cheie construita in raspuns")


def test_ruta_chiar_cheama_derivarea():
    """Cheia `document` ar putea exista și plină cu altceva. Aici se cere **apelul** helperului —
    tot din AST, deci un apel comentat nu contează."""
    apeluri = {getattr(n.func, "attr", None) or getattr(n.func, "id", None)
               for n in ast.walk(_functia()) if isinstance(n, ast.Call)}
    assert apeluri >= {"document_justificativ"}, (
        "ruta nu mai cheamă derivarea documentului — cheia poate fi acolo, dar goală")


# ── singura aserțiune pe text, cu motivul declarat mai sus ───────────────────
def test_CALIBRARE_numerotarea_e_pe_AN_nu_pe_luna():
    """Partea subtila, si singura care poate regresa tacit: norma cere numerotare *incepand de la 1
    ianuarie*. Daca fereastra ROW_NUMBER ar fi pe luna, fiecare luna ar reincepe de la 1 — raspunsul
    ar arata la fel de plauzibil, dar registrul ar fi gresit."""
    sql = _sql()
    assert "ROW_NUMBER() OVER" in sql, "numerotarea nu mai e calculata in SQL-ul rutei"
    i = sql.index("WITH pe_an")
    fereastra = sql[i:sql.index("ROW_NUMBER() OVER", i) + 200]
    assert "date_trunc('year'" in fereastra, (
        "fereastra de numerotare nu mai e pe AN — daca e pe luna, numarul curent reincepe lunar, "
        "contra normei 14-1-1 col. 1")


def test_CALIBRARE_gardul_citeste_STRUCTURA_nu_PROZA():
    """Modul de esec al gardului insusi, prins de RED-proof si numit de Costin ca regula: forma veche
    gasea numele in DOCSTRINGUL rutei. Aici se dovedeste ca sursa de adevar e AST-ul.

    `Confruntat cu norma` **exista** in docstringul rutei si **nu poate** aparea printre chei."""
    # PE TEXT, ȘI DE CE: aserțiunea asta e DESPRE proză — verifică chiar că fraza trăiește în
    # docstring. Un `in` pe un docstring nu e o scurtătură, e subiectul. Perechea ei e pe structură.
    doc = ast.get_docstring(_functia()) or ""
    assert "Confruntat cu norma" in doc, "premisa calibrarii a disparut din docstringul rutei"
    assert not (_chei_construite() & {"Confruntat cu norma"}), (
        "proza rutei ajunge printre cheile construite — extractorul s-a rupt")
