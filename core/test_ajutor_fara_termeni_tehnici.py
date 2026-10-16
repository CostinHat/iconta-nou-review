# -*- coding: utf-8 -*-
"""GARD — comanda Costin 16.10.2026, „Lotul 6, comanda 1” (verbatim în DECIZII): 276c „Ajutorul nu folosește termeni de programator
(«magic bytes», «motor»)” și 273d „Ajutorul nu folosește termeni de programator («parsează», «parserul»)”.

CLASA (din perspectiva contabilului): orice text pe care îl citește contabilul — ajutorul „?” (coloana `ajutor` din FUNCTIONALITATI.csv),
titlul funcționalității (fereastra de ajutor și pagina publică a funcționalităților) și frazele ecranelor (static/js) — fără termeni de
programator. Măsurat la 16.10.2026: 67 de texte de ajutor (54 de fraze: „motorul”, „parsează”, „magic bytes”, „payload-ul e sigilat cu
hash”, „dispecerul intern”, „azi prin dispatch/API”, „drift”, „cron”), 3 titluri pe pagina publică („Motor D212”, „Motorul contabil”,
„… prin API SPV”) și 3 fraze pe ecrane („Match exact”, „Fără match”, „motorul care o produce nu întoarce pozițiile”). Toate rescrise.

CE NU E ÎN CLASĂ (calibrarea de mai jos): „cronologic”, „cronometru”, „sold scriptic”, formatul „JSON” / „XML” al unui fișier, „API-ul
public” al integrărilor (e chiar funcționalitatea, pentru integratori), „motor diesel”.
LIMITA: motivele scrise de server (Python) care ajung pe ecran nu sunt citite aici — au fost corectate la vedere („match exact pe o
factura”, „alocare partiala FIFO” în `core/reconciliere.py`); frazele dintr-un singur cuvânt nu le vede `scan_js_texte` (limita lui, M3).
"""
import csv
import io
import os
import re
import sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RAD)

TERMENI = re.compile(
    r"magic bytes|\bpars(ează|are|area|ării|at|ate|ată|ăm|ez)\b|\bparser\w*|\bmotor(ul|ului|ii|ul)?\b(?! (diesel|electric|termic|vehicul|auto))"
    r"|\bhash\w*|\bpayload\w*|\bcron(ul|-ul)?\b|\bfallback\b|\bflag(-ul|ul|uri)?\b|\bbackend\b|\bfrontend\b|\bendpoint\w*|\bhardcod\w*"
    r"|\bdocstring\w*|\bdispecer\w*|\bdispatch\w*|\bdrift\b|\bmatch\b|\btenant\w*|\bschema (firmei|bazei)\b|\bdoar ca API\b"
    r"|\bîn parser\b|DUK pe server", re.I)


def _registru():
    with io.open(os.path.join(_RAD, "FUNCTIONALITATI.csv"), encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def test_calibrarea_tiparului():
    for da in ("Aplicația detectează formatul (magic bytes)", "Parsează fișierul", "Încarcă fișierul în parser.", "Motorul propune cota",
               "Fără match", "un cron le generează", "payload-ul e sigilat cu hash", "apare doar în dispecerul intern",
               "azi prin dispatch/API", "detalii per actor (nivel, tipare, drift)", "accesibil doar ca API"):
        assert TERMENI.search(da), da
    for nu in ("evidența cronologică", "un cronometru de efort", "soldul scriptic", "arhivă JSON per tabelă", "fișierul XML",
               "cheile API ale cabinetului", "motor diesel", "Potrivire exactă", "Calculul Declarației unice D212"):
        assert not TERMENI.search(nu), nu


def test_ajutorul_nu_are_termeni_de_programator():
    """MUTAȚIE: „Motorul propune cota” pus înapoi în ajutorul F023 -> pică."""
    rele = [(r["ID"], m.group(0)) for r in _registru() for m in TERMENI.finditer(r.get("ajutor") or "")]
    assert rele == [], rele


def test_titlurile_vazute_de_contabil_nu_au_termeni_de_programator():
    """Titlul apare în fereastra de ajutor (`/ajutor/{fid}` -> „Ajutor · <titlu>”) și pe pagina publică a funcționalităților
    (`GRUPE_FUNC`, generat din registru). Se verifică titlurile cu semn „?” pe un ecran și pe cele din pagina publică."""
    import genereaza_grupe_functii as g
    publice = {f for x in g.repartizeaza() for f in x["functii"]}
    js = ""
    for d, _s, fs in os.walk(os.path.join(_RAD, "static", "js")):
        js += "".join(io.open(os.path.join(d, f), encoding="utf-8").read() for f in fs if f.endswith(".js"))
    cu_semn = set(re.findall(r'semnAjutor\(\s*"(F\d{3})"', js))
    assert len(publice) > 100 and len(cu_semn) > 20, (len(publice), len(cu_semn))
    rele = [(r["ID"], r["Functionalitate"]) for r in _registru()
            if (r["Functionalitate"] in publice or r["ID"] in cu_semn) and TERMENI.search(r["Functionalitate"])]
    assert rele == [], rele


def test_frazele_ecranelor_nu_au_termeni_de_programator():
    """Frazele din static/js care ajung la om (`core/scan_js_texte.inventar`). Atributele `data-actiune` („POST /tenants/…”) nu se
    afișează. MUTAȚIE: „● Fără match” pus înapoi pe ecranul Bancă -> pică."""
    from core import scan_js_texte as s
    rele = [(loc[0], f) for f, loc in s.inventar().items()
            if TERMENI.search(f) and not re.match(r"^(GET|POST|PUT|PATCH|DELETE) /", f)]
    assert rele == [], rele
