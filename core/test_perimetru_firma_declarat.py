# -*- coding: utf-8 -*-
"""core/test_perimetru_firma_declarat.py — GARD: perimetrul declarat al unei firme nu poate ramane
NESCRIS, nu poate deveni STATUT, si nu poate fi INCOMPLET in tacere.

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

Trei colti, pe sectiunile `## tenant_0XX` din ISTORIC_TENANTI.md:

  1. COMPLETITUDINE (fara DB) — orice sectiune de firma are blocul de perimetru, cu laturile numite:
     ce e IN perimetru (proza), ce e IN AFARA (lista de tabele) si ce e in perimetru dar POATE primi
     date (lista de tabele). FARA BASELINE, deliberat: la nasterea gardului exista o singura sectiune
     de firma (006) si primeste blocul in acelasi commit, deci poarta e verde din prima. Gardul musca
     la prima tura care creeaza sectiunea firmei urmatoare — acolo unde e si contextul ei.

  2. NE-STATUT (cu DB) — fiecare tabel declarat „in afara perimetrului" EXISTA in schema si e GOL.
     Daca cineva umple firma, declaratia devine rosie in aceeasi zi, nu peste trei luni.

  3. NE-INCOMPLET (cu DB) — **orice tabel GOL din schema trebuie CLASIFICAT**: ori „in afara
     perimetrului" (si atunci e gardat sa ramana gol), ori „in perimetru, poate primi date" (si
     atunci golul lui e o stare, nu o promisiune). Un tabel gol neclasificat = ambiguitatea de la
     care a pornit totul. Coltul asta prinde si tabelele NOI din `tenant_template.sql`: la aparitia
     lor cineva trebuie sa decida, o data, de care parte sunt. Tabelele CU date nu se cer clasificate
     — un tabel populat nu e ambiguu.

LIMITA DECLARATA (GARZI.md cere sa fie scrisa): gardul apara sectiunile CARE EXISTA. Daca o tura
auditeaza o firma si nu-i creeaza deloc rand in registru, nimic nu se aprinde aici — asta ramane pe
disciplina §11 din CLAUDE.md (raportul numeste obligatoriu ISTORIC_TENANTI.md). Gardul acopera
„scris pe jumatate", „scris si uitat" si „scris incomplet", NU „nescris deloc".
"""
import io
import os
import re

import pytest

from core import db as _db

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_REGISTRU = os.path.join(_RAD, "ISTORIC_TENANTI.md")

_SECTIUNE_FIRMA = re.compile(r"^## (tenant_(\d{3}))\b", re.M)
_ANTET_BLOC = "**Perimetru"
_IN_PERIMETRU = "**În perimetru:**"
_IN_AFARA = "**În afara perimetrului"
_POT_PRIMI = "**În perimetru, tabele care pot primi date"
# marcajul „niciunul" pentru o firma care exercita tot: liniuta lunga, fara backtick-uri
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


def _linie(corp, marcaj):
    for l in corp.splitlines():
        if l.strip().startswith(marcaj):
            return l
    return None


def _tabele(corp, marcaj):
    """Numele de tabele de pe linia marcata, citite din backtick-uri. None = linia lipseste."""
    l = _linie(corp, marcaj)
    if l is None:
        return None
    if "`" not in l and _NICIUNUL in l.split(":", 1)[-1]:
        return []          # declaratie explicita „niciunul", nu omisiune
    return re.findall(r"`(\w+)`", l)


def _probleme_sectiune(cur, schema, corp):
    """Verificarile care au nevoie de baza, pentru o (schema, sectiune). Separata de teste ca sa
    poata fi probata SI pe o schema inexistenta, fara sa sterg nimic din baza."""
    probleme = []
    declarate = _tabele(corp, _IN_AFARA) or []
    pot_primi = _tabele(corp, _POT_PRIMI) or []

    cur.execute("SELECT tablename FROM pg_tables WHERE schemaname = %s", (schema,))
    exista = {r[0] for r in cur.fetchall()}
    if not exista:
        return ["%s: schema nu exista in baza — declaratia de perimetru nu se poate verifica "
                "(firma stearsa? redenumita? typo in antetul sectiunii?)" % schema]

    goale = set()
    for tabel in sorted(exista):
        cur.execute('SELECT count(*) FROM "%s"."%s"' % (schema, tabel))
        if int(cur.fetchone()[0]) == 0:
            goale.add(tabel)

    # coltul 2 — ce e declarat in afara perimetrului exista si a ramas gol
    for tabel in declarate:
        if tabel not in exista:
            probleme.append("%s: tabelul declarat `%s` nu exista in schema (typo, sau schema s-a "
                            "schimbat) — declaratia verifica pe gol" % (schema, tabel))
        elif tabel not in goale:
            cur.execute('SELECT count(*) FROM "%s"."%s"' % (schema, tabel))
            probleme.append("%s: `%s` e declarat IN AFARA perimetrului dar are %d randuri — "
                            "declaratia e STATUTA. Ori firma a capatat regimul asta (mut-o in "
                            "perimetru si parcurge-i fatetele pe date reale), ori datele sunt "
                            "reziduu de proba si se curata."
                            % (schema, tabel, int(cur.fetchone()[0])))
    for tabel in pot_primi:
        if tabel not in exista:
            probleme.append("%s: tabelul `%s` din lista «pot primi date» nu exista in schema (typo?)"
                            % (schema, tabel))

    # coltul 3 — orice tabel GOL e clasificat de o parte sau de alta
    neclasificate = sorted(goale - set(declarate) - set(pot_primi))
    if neclasificate:
        probleme.append(
            "%s: tabele GOALE neclasificate: %s. Un tabel gol e ambiguu — ori e IN AFARA "
            "perimetrului (si atunci se gardeaza sa ramana gol), ori e IN perimetru si POATE primi "
            "date (si atunci golul lui e o stare, nu o promisiune). Daca sunt tabele NOI din "
            "tenant_template, decide o data de care parte sunt."
            % (schema, ", ".join("`%s`" % t for t in neclasificate)))
    return probleme


# ==========================================================================================
#  COLTUL 1 — perimetrul nu poate ramane NESCRIS (fara DB)
# ==========================================================================================
def test_registrul_are_cel_putin_o_sectiune_de_firma():
    """Daca regexul de sectiune nu mai prinde nimic, toate gardurile de mai jos ar trece pe gol."""
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
        for marcaj, ce in ((_IN_PERIMETRU, "ce e IN perimetru"),
                           (_IN_AFARA, "ce e IN AFARA perimetrului"),
                           (_POT_PRIMI, "ce e in perimetru dar POATE primi date")):
            if _linie(corp, marcaj) is None:
                rele.append("%s: blocul nu numeste %s (linia «%s»)" % (schema, ce, marcaj))
    assert not rele, "\n".join(rele)


def test_listele_sunt_citabile_mecanic():
    """O linie prezenta dar fara niciun nume de tabel (si fara marcajul «niciunul») ar face coltii
    2 si 3 sa nu verifice NIMIC — declaratie decorativa."""
    rele = []
    for schema, corp in _sectiuni():
        for marcaj in (_IN_AFARA, _POT_PRIMI):
            l = _linie(corp, marcaj)
            if l is None:
                continue      # lipsa e raportata de testul de mai sus
            if not _tabele(corp, marcaj) and _NICIUNUL not in l:
                rele.append("%s: linia «%s» n-are niciun nume de tabel intre backtick-uri si nici "
                            "marcajul «%s» (niciunul) — nimic de verificat" % (schema, marcaj, _NICIUNUL))
    assert not rele, "\n".join(rele)


# ==========================================================================================
#  COLTII 2 si 3 — nu poate deveni STATUT, nu poate fi INCOMPLET (cu DB)
# ==========================================================================================
def test_perimetrul_declarat_e_valid_si_complet():
    if not _db_ok():
        pytest.skip("DB indisponibil")
    rele = []
    with _db.get_conn() as conn, conn.cursor() as cur:
        for schema, corp in _sectiuni():
            rele += _probleme_sectiune(cur, schema, corp)
    assert not rele, "\n".join(rele)


def test_ramura_schema_inexistenta_e_raportata():
    """Proba pe ramura care altfel n-ar fi executata niciodata: o sectiune care numeste o schema
    care nu exista NU trebuie sa treaca in tacere (ar fi un gard care verifica pe gol).
    Sintetic: nu se sterge si nu se creeaza nimic in baza."""
    if not _db_ok():
        pytest.skip("DB indisponibil")
    corp = ("## tenant_999 — firma sintetica\n"
            "**Perimetru.** x\n**În perimetru:** x\n"
            "**În afara perimetrului (tabele care trebuie să rămână goale):** `salariati`.\n"
            "**În perimetru, tabele care pot primi date:** —\n")
    with _db.get_conn() as conn, conn.cursor() as cur:
        probleme = _probleme_sectiune(cur, "tenant_999", corp)
    assert probleme and "schema nu exista" in probleme[0], probleme
