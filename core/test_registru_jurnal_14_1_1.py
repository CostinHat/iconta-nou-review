# -*- coding: utf-8 -*-
"""GARD — Registrul-jurnal păstrează cele trei coloane cerute de norma 14-1-1.

  core/test_registru_jurnal_14_1_1.py

Confruntat cu OMFP 2634/2015 anexa 2 (cod 14-1-1) pe 24.08.2026: din opt coloane, patru ieșeau, iar
trei lipseau — **coloana 1** (numărul curent de la 1 ianuarie), **coloana 3** (felul, numărul și data
documentului justificativ) și **totalizarea lunară**. Reparate prin derivare la citire.

CE FACE IMPOSIBIL: ca vreuna dintre cele trei să dispară tăcut dintr-un artefact care se prezintă la
control. Un registru din care lipsește coloana documentului justificativ nu se poate apăra.

CE NU VERIFICĂ, declarat: dacă valorile sunt corecte pe datele unei firme anume — aia cere baza de
date și e o probă, nu un gard. Aici se păzește **contractul**: că cele trei elemente sunt produse, și
că numerotarea e pe AN, nu pe lună.

DOUĂ ASERȚIUNI AU FOST MUTATE DE PE PROZĂ PE COD, după ce RED-proof-ul le-a prins verzi: căutau
`nr_curent` și `note_fara_document` *oriunde* în rută — iar amândouă apar și în **docstringul** rutei,
scris de mine. Un gard care se potrivește pe proza de lângă cod nu păzește codul. Acum se caută forma
de **cheie în răspuns** (`"nume":`), pe textul cu docstring și comentarii **scoase**.
"""
import io
import os
import re
from datetime import date

from core import jurnal_api as _j

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _ruta():
    t = io.open(os.path.join(RAD, "main.py"), encoding="utf-8").read()
    m = re.search(r'@app\.get\("/tenants/\{tenant_id\}/jurnal"\).*?\n(?=@app\.)', t, re.S)
    assert m, "nu mai gasesc ruta /jurnal in main.py — gardul masoara ce nu vede"
    return m.group(0)


def _cod():
    """Ruta FĂRĂ docstringul ei și fără comentarii — ce vede interpretorul, nu ce scrie lângă.

    Se scoate DOAR docstringul funcției, nu orice bloc triplu-citat: SQL-ul rutei trăiește într-un
    `f\"\"\"...\"\"\"`, iar o curățare lacomă îl șterge și el — prima formă a acestui helper făcea exact
    asta și lăsa gardul să acuze că numerotarea a dispărut."""
    r = _ruta()
    i = r.find('"""')
    if i != -1 and (i == 0 or r[i - 1] != "f"):
        j = r.find('"""', i + 3)
        if j != -1:
            r = r[:i] + " " + r[j + 3:]
    r = re.sub(r"(?m)^\s*#.*$", " ", r)
    return r


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


# ── coloanele 1 si totalizarea, in CODUL rutei ───────────────────────────────
def test_ruta_produce_numarul_curent():
    assert '"nr_curent":' in _cod(), "coloana 1 (numarul curent) nu mai e cheie in raspuns"


def test_CALIBRARE_numerotarea_e_pe_AN_nu_pe_luna():
    """Partea subtila, si singura care poate regresa tacit: norma cere numerotare *incepand de la 1
    ianuarie*. Daca fereastra ROW_NUMBER ar fi pe luna, fiecare luna ar reincepe de la 1 — raspunsul
    ar arata la fel de plauzibil, dar registrul ar fi gresit."""
    r = _cod()
    assert "ROW_NUMBER() OVER" in r, "numerotarea nu mai e calculata"
    i = r.index("WITH pe_an")
    fereastra = r[i:r.index("ROW_NUMBER() OVER", i) + 200]
    assert "date_trunc('year'" in fereastra, (
        "fereastra de numerotare nu mai e pe AN — daca e pe luna, numarul curent reincepe lunar, "
        "contra normei 14-1-1 col. 1")


def test_ruta_totalizeaza_lunar():
    r = _cod()
    for cheie in ('"total_debit":', '"total_credit":'):
        assert cheie in r, "totalizarea lunara ceruta de 14-1-1 lipseste: %s" % cheie


def test_absenta_documentului_se_NUMARA_nu_se_ascunde():
    """P6: ce nu se poate deriva se spune. Un registru cu jumatate din coloana 3 goala, fara sa spuna
    cate, arata la fel cu unul complet."""
    assert '"note_fara_document":' in _cod(), (
        "numarul notelor fara document justificativ nu mai e cheie in raspuns")


def test_CALIBRARE_gardul_citeste_COD_nu_PROZA():
    """Modul de esec al gardului insusi, prins de RED-proof: doua aserțiuni cautau numele *oriunde*
    in ruta si treceau din DOCSTRING. Aici se dovedeste ca `_cod()` chiar scoate proza."""
    r = _ruta()
    c = _cod()
    assert "Confruntat cu norma" in r, "premisa calibrarii a disparut din docstringul rutei"
    assert "Confruntat cu norma" not in c, "`_cod()` nu mai scoate docstringul — gardul citeste proza"
