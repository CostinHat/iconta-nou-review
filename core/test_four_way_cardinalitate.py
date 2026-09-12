# -*- coding: utf-8 -*-
"""Bratul four-way nu se poate inchide pe o multime INCOMPLETA.

CE S-A MASURAT (12.09.2026, la publicarea lui `a9566af0`): bratul a tiparit «TOATE procesele de
productie poarta HEAD: 1 din 1» pe o productie cu DOI workeri. N-a mintit despre ce a vazut — a
vazut un singur proces inregistrat, fiindca cei doi se inregistreaza la ~0,8 s distanta si
intrebarea a nimerit fereastra dintre ele. A mintit prin ce NU s-a intrebat: *cati ar fi trebuit sa
fie.* Aceeasi clasa cu `all([])`, cu un pas mai departe: acolo multimea era vida, aici incompleta.

CE PAZESTE FISIERUL: verdictul are DOUA conditii — cardinalitate completa SI fiecare proces la HEAD
— si niciuna nu se poate ocoli. Plus purtarea in timp (cardinalitatea care creste, si cea care nu
creste pana la expirare), fiindca acolo s-a produs defectul: nu intr-o stare, ci intr-un MOMENT.

DE CE PROBELE SUNT PE FUNCTII PURE. `judeca` nu atinge baza, iar `asteapta_si_judeca` primeste
ceasul si somnul din afara. Asa se pot proba starile care pe productie apar o data la cateva sute
de milisecunde — si se pot proba TOATE, nu doar cele pe care le-am prins din zbor.
"""
from __future__ import annotations

import importlib.util
import os
import sys

RADACINA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RADACINA)

HEAD = "a9566af02fe48485f486221c4aab5291564747de"
ALTUL = "94d655a81070ba0341dbc2bf9ed9042d600f8f5b"


def _brat():
    cale = os.path.join(RADACINA, "scripts", "toate_poarta_head.py")
    spec = importlib.util.spec_from_file_location("toate_poarta_head_probe", cale)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


B = _brat()


def _proces(pid, sha=HEAD, gazda="iconta-prod"):
    return (gazda, pid, sha, "2026-09-13 00:00:00")


def _citire(lista):
    """(total, rataciti) — forma pe care o intoarce `instante.toate_poarta` bratului."""
    return len(lista), [x for x in lista if x[2] != HEAD]


# ============================================================
#  1. CELE OPT STARI CERUTE
# ============================================================
def test_zero_inregistrate_din_doua_asteptate_PICA():
    """Multimea vida era deja pazita; aici e pazita impreuna cu cardinalitatea."""
    v = B.judeca(*_citire([]), asteptate=2)
    assert v.stare == B.INCOMPLET and v.total == 0 and v.asteptate == 2


def test_UNUL_din_doua_la_HEAD_PICA_desi_cel_gasit_e_curat():
    """EXACT cazul din productie: procesul gasit poarta HEAD, si tocmai de-aia forma veche trecea."""
    v = B.judeca(*_citire([_proces(1001)]), asteptate=2)
    assert v.stare == B.INCOMPLET, "un brat care se inchide pe 1 din 2 afirma despre TOATE"
    assert v.rataciti == [], "premisa: procesul gasit chiar poarta HEAD"


def test_DOUA_din_doua_la_HEAD_TREC():
    v = B.judeca(*_citire([_proces(1001), _proces(1002)]), asteptate=2)
    assert v.stare == B.PASS and v.total == 2 and v.rataciti == []


def test_doua_din_doua_dar_UNUL_la_alt_commit_PICA():
    v = B.judeca(*_citire([_proces(1001), _proces(1002, ALTUL)]), asteptate=2)
    assert v.stare == B.RATACITI and len(v.rataciti) == 1


def test_TREI_inregistrate_din_doua_asteptate_PICA():
    """Mai multe decat se asteptau nu e o veste buna: e un registru despre care nu se stie ce
    contine. `PASS` ar insemna ca s-a verificat si ce nu se stie ce e."""
    v = B.judeca(*_citire([_proces(1001), _proces(1002), _proces(1003)]), asteptate=2)
    assert v.stare == B.PREA_MULTE and v.total == 3


def test_un_rand_STALE_nu_produce_un_PASS_fals():
    """Randul unui proces mort care inca e in fereastra de bataie umfla numaratoarea. Verdictul
    trebuie sa fie «nu se stie», nu «toate poarta HEAD» — chiar daca randul mort poarta HEAD."""
    vii_plus_stale = [_proces(1001), _proces(1002), _proces(999999)]
    v = B.judeca(*_citire(vii_plus_stale), asteptate=2)
    assert v.stare != B.PASS and v.stare == B.PREA_MULTE


def test_cardinalitatea_creste_de_la_1_la_2_si_ABIA_ATUNCI_trece():
    """Purtarea in TIMP — acolo s-a produs defectul. Prima citire vede un proces, a doua vede doi."""
    citiri = [[_proces(1001)], [_proces(1001), _proces(1002)]]
    vazute = []

    def citeste():
        lista = citiri[min(len(vazute), len(citiri) - 1)]
        vazute.append(lista)
        return _citire(lista)

    t = [0.0]
    v = B.asteapta_si_judeca(citeste, asteptate=2, rabdare_sec=90, pas_sec=2,
                             ceas=lambda: t[0], dormi=lambda s: t.__setitem__(0, t[0] + s))
    assert v.stare == B.PASS and v.total == 2
    assert len(vazute) == 2, "n-a reinterogat dupa citirea incompleta: %d citiri" % len(vazute)


def test_cardinalitatea_ramane_1_pana_la_expirare_si_PICA():
    """Cealalta ramura a aceleiasi bucle: daca al doilea proces nu apare niciodata, raspunsul e NU,
    nu «am asteptat destul, hai sa zicem ca da»."""
    t = [0.0]
    apeluri = []

    def citeste():
        apeluri.append(1)
        return _citire([_proces(1001)])

    v = B.asteapta_si_judeca(citeste, asteptate=2, rabdare_sec=10, pas_sec=2,
                             ceas=lambda: t[0], dormi=lambda s: t.__setitem__(0, t[0] + s))
    assert v.stare == B.INCOMPLET
    assert len(apeluri) >= 5, "n-a reincercat pana la expirare: %d incercari" % len(apeluri)


# ============================================================
#  2. RED-PROOF — forma de la `a9566af0` ar fi trecut cazul 1 din 2
# ============================================================
def test_RED_forma_de_dinainte_ar_fi_trecut_pe_1_din_2():
    """Predicatul de atunci, scris aici ca sa se vada ce s-a schimbat: `bool(lista) and not
    rataciti`. Pe un singur proces inregistrat, la HEAD, el raspunde DA — si exact asta s-a
    tiparit in producție. Daca vreodata proba asta incepe sa pice, inseamna ca predicatul vechi a
    fost reintrodus si cardinalitatea nu mai e ceruta."""
    lista = [_proces(1001)]
    total, rataciti = _citire(lista)
    vechi = bool(lista) and not rataciti
    assert vechi is True, "premisa RED-proof: forma veche chiar raspundea DA pe 1 din 2"
    assert B.judeca(total, rataciti, asteptate=2).stare == B.INCOMPLET, (
        "forma noua raspunde la fel ca cea veche — cardinalitatea nu se cere")


# ============================================================
#  3. NUMARUL ASTEPTAT — citit, nu presupus; si niciun drum de la «nu stiu» la «da»
# ============================================================
def test_numarul_se_citeste_din_Environment_ul_unitatii():
    campuri = {"LoadState": ["loaded"], "Environment": ["WEB_CONCURRENCY=2"],
               "EnvironmentFiles": []}
    n, sursa = B.numar_asteptat(campuri=campuri)
    assert n == 2 and sursa.fel == B.UNITATE_ENV


def test_numarul_se_citeste_si_dintr_un_EnvironmentFile(tmp_path):
    f = tmp_path / "db.env"
    f.write_text("# comentariu\nexport WEB_CONCURRENCY=4\n", encoding="utf-8")
    campuri = {"LoadState": ["loaded"], "Environment": [""],
               "EnvironmentFiles": ["%s (ignore_errors=no)" % f]}
    n, sursa = B.numar_asteptat(campuri=campuri)
    assert (n, sursa.fel) == (4, B.FISIER_ENV)


def test_fara_nicio_valoare_numarul_e_UNU_si_se_spune_de_ce():
    """Absenta e DETERMINATA, nu necunoscuta: fara `--workers` si fara `WEB_CONCURRENCY`, uvicorn
    porneste un singur proces. Motivul se tipareste, ca cine citeste sa nu creada ca e o ghicire."""
    campuri = {"LoadState": ["loaded"], "Environment": [""], "EnvironmentFiles": []}
    n, sursa = B.numar_asteptat(campuri=campuri)
    assert (n, sursa.fel) == (1, B.IMPLICIT)


def test_unitatea_necitibila_da_NECUNOSCUT_nu_un_numar():
    for campuri in (None, {"LoadState": ["not-found"]}, {"LoadState": []}):
        n, sursa = B.numar_asteptat(campuri=campuri)
        assert n is None and sursa.fel == B.NECUNOSCUT, (
            "o unitate necitibila a produs un numar: %r" % (n,))


def test_o_valoare_stricata_NU_trece_drept_absenta():
    """`WEB_CONCURRENCY=doi` n-are voie sa cada pe implicitul 1: ar transforma o configuratie
    gresita intr-un brat care trece."""
    campuri = {"LoadState": ["loaded"], "Environment": ["WEB_CONCURRENCY=doi"],
               "EnvironmentFiles": []}
    n, sursa = B.numar_asteptat(campuri=campuri)
    assert n is None and sursa.fel == B.NECUNOSCUT


def test_necunoscutul_iese_cu_2_nu_cu_0(monkeypatch, capsys):
    """Ultima poarta ceruta: nu exista drum prin care «nu stiu cati» sa devina PASS."""
    monkeypatch.setattr(B, "numar_asteptat",
                        lambda *a, **k: (None, B.Sursa(B.NECUNOSCUT, "unitate necitibila")))
    assert B.main([HEAD]) == 2
    assert capsys.readouterr().out.strip(), "a iesit cu 2 fara sa spuna nimic"


# ============================================================
#  4. ANTI-VACUU — verdictul chemat de brat e CHIAR cel probat aici
# ============================================================
def test_bucla_bratului_foloseste_judeca():
    """Fara asta, `judeca` ar putea fi o functie corecta pe care bratul n-o cheama — iar probele de
    mai sus ar pazi cod mort."""
    import ast
    import io as _io
    cale = os.path.join(RADACINA, "scripts", "toate_poarta_head.py")
    arbore = ast.parse(_io.open(cale, encoding="utf-8").read())
    bucla = [n for n in ast.walk(arbore)
             if isinstance(n, ast.FunctionDef) and n.name == "asteapta_si_judeca"]
    assert bucla, "n-am gasit bucla bratului — proba ar trece in gol"
    apelate = {n.func.id for n in ast.walk(bucla[0])
               if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    assert apelate >= {"judeca"}, "bucla nu cheama `judeca`: %s" % apelate


def test_main_cere_numarul_INAINTE_de_a_intreba_baza(monkeypatch):
    """Ordinea conteaza: daca numarul s-ar citi dupa interogare, o baza indisponibila ar ascunde
    faptul ca nici cardinalitatea nu se putea sti."""
    ordine = []

    def numar(*a, **k):
        ordine.append("numar")
        return 2, B.Sursa(B.UNITATE_ENV, "proba")

    def dsn():
        ordine.append("dsn")
        return None            # opreste `main` aici: ce urmeaza nu ne intereseaza

    monkeypatch.setattr(B, "numar_asteptat", numar)
    monkeypatch.setattr(B, "dsn_productie", dsn)
    assert B.main([HEAD]) == 2
    assert ordine == ["numar", "dsn"], "ordinea intrebarilor s-a schimbat: %s" % ordine
