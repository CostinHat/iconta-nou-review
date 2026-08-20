# -*- coding: utf-8 -*-
"""core/test_perimetru_firma_declarat.py — GARD: perimetrul declarat al unei firme nu poate ramane
NESCRIS, si nici nu poate deveni STATUT fara ca cineva sa afle.

De ce (20.08.2026, cerut de Costin). tenant_006 are 47 de tabele in schema si DATE in trei
(firma_profil 1, d301_operatiuni 3, plan_conturi 185 = nomenclatorul OMFP). Restul — salariati,
facturi, casa, banca, stocuri, mijloace fixe, solduri — sunt goale **prin constructie**: 006 e
purtatoarea regimului „neplatitor micro cu achizitii intracomunitare", nu o firma completa.
Fara declaratie scrisa, cine citeste registrul peste trei luni are doua feluri de a gresi:
  (a) citeste golurile ca DATORIE si porneste sa parcurga F3/F7 pe tabele goale — dar F3 („pe date
      POPULATE, nu pe fixture goale") si F7 („compara cifrele afisate cu faptele") n-au ce compara,
      deci dau verde fiindca n-au ce contrazice = exact falsul sentiment de acoperire pe care
      GARZI.md il interzice;
  (b) citeste declaratia veche ca inca valabila dupa ce cineva a umplut firma cu date — si atunci
      „in afara perimetrului" devine o minciuna linistita.

Doua colti, amandoi pe sectiunile `## tenant_0XX` din ISTORIC_TENANTI.md:

  1. COMPLETITUDINE (fara DB) — orice sectiune de firma are blocul de perimetru, cu ambele laturi
     numite: ce e IN perimetru (proza) si ce e IN AFARA (lista de tabele, citabila mecanic).
     FARA BASELINE, deliberat: azi exista o singura sectiune de firma (006) si primeste blocul in
     acelasi commit cu gardul, deci poarta e verde din prima. Gardul musca la prima tura care creeaza
     sectiunea urmatoarei firme — acolo unde e si contextul ei. Un baseline ar fi fost fie greutate
     moarta (gol), fie o lista de amnistie care legitimeaza absenta cat o tine in viata.

  2. NE-STATUT (cu DB) — fiecare tabel declarat „in afara perimetrului" EXISTA in schema si e GOL.
     Daca cineva umple firma, declaratia devine rosie in aceeasi zi, nu peste trei luni.

LIMITA DECLARATA (GARZI.md cere sa fie scrisa): gardul apara sectiunile CARE EXISTA. Daca o tura
auditeaza o firma si nu-i creeaza deloc rand in registru, nimic nu se aprinde aici — asta ramane pe
disciplina §11 din CLAUDE.md (raportul numeste obligatoriu ISTORIC_TENANTI.md). Gardul acopera
„scris pe jumatate" si „scris si uitat", nu „nescris deloc".
"""
import io
import os
import re

import pytest

from core import db as _db

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_REGISTRU = os.path.join(_RAD, "ISTORIC_TENANTI.md")

_SECTIUNE_FIRMA = re.compile(r"^## (tenant_(\d{3}))\b", re.M)
_IN_PERIMETRU = "**În perimetru:**"
_IN_AFARA = "**În afara perimetrului"
_ANTET_BLOC = "**Perimetru"
# marcajul „niciunul" pentru o firma care exercita tot: linia se scrie cu o liniuta lunga
_NICIUNUL = "—"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


def _sectiuni():
    """[(schema, corpul sectiunii)] pentru fiecare `## tenant_0XX` din registru."""
    txt = io.open(_REGISTRU, encoding="utf-8").read()
    taieturi = [(m.group(1), m.start()) for m in _SECTIUNE_FIRMA.finditer(txt)]
    urmatoarele = [m.start() for m in re.finditer(r"^## ", txt, re.M)]
    out = []
    for schema, poz in taieturi:
        capat = min([p for p in urmatoarele if p > poz] or [len(txt)])
        out.append((schema, txt[poz:capat]))
    return out


def _linie_in_afara(corp):
    for linie in corp.splitlines():
        if linie.strip().startswith(_IN_AFARA):
            return linie
    return None


def _tabele_declarate(corp):
    """Numele de tabele din linia «În afara perimetrului», citite din backtick-uri."""
    linie = _linie_in_afara(corp)
    if linie is None:
        return None
    if _NICIUNUL in linie.split(":", 1)[-1] and "`" not in linie:
        return []          # firma exercita tot — declaratie explicita, nu omisiune
    return re.findall(r"`(\w+)`", linie)


# ==========================================================================================
#  COLTUL 1 — perimetrul nu poate ramane NESCRIS (fara DB)
# ==========================================================================================
def test_registrul_are_cel_putin_o_sectiune_de_firma():
    """Daca regexul de sectiune nu mai prinde nimic, gardul de mai jos ar trece pe gol."""
    assert _sectiuni(), (
        "nicio sectiune `## tenant_0XX` in ISTORIC_TENANTI.md — s-a schimbat formatul antetului? "
        "Gardul de perimetru ar deveni vacuu.")


def test_fiecare_firma_isi_declara_perimetrul():
    rele = []
    for schema, corp in _sectiuni():
        if _ANTET_BLOC not in corp:
            rele.append("%s: nu are blocul **Perimetru** — golurile din schema se citesc ca datorie, "
                        "nu ca alegere" % schema)
            continue
        if _IN_PERIMETRU not in corp:
            rele.append("%s: blocul nu numeste ce e IN perimetru (linia «%s»)" % (schema, _IN_PERIMETRU))
        if _linie_in_afara(corp) is None:
            rele.append("%s: blocul nu numeste ce e IN AFARA perimetrului (linia «%s:») — fara ea "
                        "declaratia nu e verificabila mecanic" % (schema, _IN_AFARA))
    assert not rele, "\n".join(rele)


def test_lista_din_afara_perimetrului_e_citabila_mecanic():
    """O linie prezenta dar fara niciun nume de tabel (si fara marcajul «niciunul») ar face
    coltul 2 sa nu verifice NIMIC — declaratie decorativa."""
    rele = []
    for schema, corp in _sectiuni():
        tab = _tabele_declarate(corp)
        if tab is None:
            continue          # lipsa liniei e raportata de testul de mai sus
        if tab == [] and _NICIUNUL not in (_linie_in_afara(corp) or ""):
            rele.append("%s: linia «În afara perimetrului» nu contine niciun nume de tabel intre "
                        "backtick-uri si nici marcajul «%s» (niciunul) — nimic de verificat"
                        % (schema, _NICIUNUL))
    assert not rele, "\n".join(rele)


# ==========================================================================================
#  COLTUL 2 — perimetrul nu poate deveni STATUT (cu DB)
# ==========================================================================================
def test_perimetrul_declarat_nu_e_statut():
    """Fiecare tabel declarat «in afara perimetrului» EXISTA si e GOL. Daca firma s-a umplut,
    declaratia e falsa si trebuie rescrisa — nu descoperita peste trei luni."""
    if not _db_ok():
        pytest.skip("DB indisponibil")
    rele = []
    with _db.get_conn() as conn:
        for schema, corp in _sectiuni():
            declarate = _tabele_declarate(corp)
            if not declarate:
                continue
            with conn.cursor() as cur:
                cur.execute("SELECT tablename FROM pg_tables WHERE schemaname = %s", (schema,))
                exista = {r[0] for r in cur.fetchall()}
                if not exista:
                    rele.append("%s: schema nu exista in baza — declaratia de perimetru nu se poate "
                                "verifica (firma stearsa? redenumita?)" % schema)
                    continue
                for tabel in declarate:
                    if tabel not in exista:
                        rele.append("%s: tabelul declarat `%s` nu exista in schema (typo, sau schema "
                                    "s-a schimbat) — declaratia verifica pe gol" % (schema, tabel))
                        continue
                    cur.execute('SELECT count(*) FROM "%s"."%s"' % (schema, tabel))
                    n = int(cur.fetchone()[0])
                    if n:
                        rele.append("%s: `%s` e declarat IN AFARA perimetrului dar are %d randuri — "
                                    "declaratia e STATUTA. Ori firma a capatat regimul asta (mut-o in "
                                    "perimetru si parcurge-i fatetele pe date reale), ori datele sunt "
                                    "reziduu de proba si se curata." % (schema, tabel, n))
    assert not rele, "\n".join(rele)
