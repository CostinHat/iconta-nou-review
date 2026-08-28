# -*- coding: utf-8 -*-
"""GARD [R80, 27.08.2026]: clasa de rute despre care detectorul din R70 nu poate afirma nimic
nu mai creste in tacere.

DE UNDE VINE. Am mutat un buton de pe `PUT /tenants/{id}` pe `POST /tenants/{id}/nume-ales`.
Ruta veche a ramas cu **zero** apelanti in `static/`. Gardul R70 — construit exact pentru clasa
„ruta fara apelant" — n-a raportat-o: singura ei ancora literala e `tenants`, care apare de 235
de ori in JS. Deci pentru ea, detectorul raspunde intotdeauna „are apelant".

CE FACE IMPOSIBIL: o ruta noua a carei ancora nu o identifica intra fara sa se stie. Nu o
interzice — o **numara**. Cine adauga a 52-a coboara clichetul deliberat, sau ii da o cale mai
specifica.

CE NU FACE, declarat: **nu spune care rute chiar n-au apelant.** Spune despre care dintre ele
detectorul e mut. Iar clichetul e o FOTOGRAFIE, nu o tinta: 51 la 27.08.2026, pe pragul de 40.

DE CE NU REPAR DETECTORUL IN LOC SA-L MASOR. Fiindca a patra regula e deja „cea mai putin
gresita, nu cea corecta" (scris in R70), iar a cincea ar cere sa stiu cum compune fiecare ecran
calea la rulare. Masuratoarea e ieftina si onesta; repararea e o campanie, si are nevoie de
decizia lui Costin.
"""
import io
import os
import sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RAD)
sys.path.insert(0, os.path.join(_RAD, "scripts"))

_CLICHET = 51          # masurat 27.08.2026, pe pragul de 40
_PRAG = 40


def _masoara():
    from scan_ancore_rute import masoara
    return masoara(_PRAG)


def test_clasa_oarba_nu_creste():
    _rute, _js, orbi, _vazute = _masoara()
    assert len(orbi) <= _CLICHET, (
        "rute despre care detectorul de apelanti nu poate afirma nimic: %d, clichetul e %d.\n"
        "Ruta noua are o ancora care nu o identifica (ex. o cale de forma `/tenants/{id}`, unde\n"
        "singurul cuvant literal apare peste tot). Ori dai o cale mai specifica, ori cobori\n"
        "clichetul deliberat si scrii de ce.\n  %s"
        % (len(orbi), _CLICHET,
           "\n  ".join("%s %s (ancora %r x%d)" % (m, c, a, f)
                       for m, c, f, a in sorted(orbi, key=lambda x: x[1])[:8])))


def test_clichetul_nu_pastreaza_morti():
    """A doua directie. Daca a scazut, se coboara deliberat — altfel cifra ramane o amintire."""
    _rute, _js, orbi, _vazute = _masoara()
    assert len(orbi) >= _CLICHET, (
        "clasa a scazut de la %d la %d — coboara `_CLICHET` in fisierul asta, ca urmatoarea "
        "crestere sa fie prinsa de la cifra reala, nu de la una veche" % (_CLICHET, len(orbi)))


def test_ANTI_VACUU_masuratoarea_chiar_vede():
    rute, js, orbi, vazute = _masoara()
    assert len(rute) > 300, "doar %d rute — s-ar masura in gol" % len(rute)
    assert js.count("tenants") > 100, (
        "textul JS nu contine nici macar `tenants` — prima versiune a masuratorii sparsese sirul "
        "in caractere si raporta 1 in loc de 51, adica exact greseala comoda")
    assert vazute, "toate rutele ies oarbe — pragul n-ar imparti nimic"
    assert orbi, "nicio ruta oarba — dar cazul cunoscut de mai jos e una"


def test_cazul_cunoscut_e_in_clasa():
    """Calibrare pe instanta care a produs gardul: daca nu mai e in clasa, masuratoarea s-a rupt
    sau ruta a primit o cale mai specifica — si atunci se citeste, nu se ignora."""
    _rute, _js, orbi, _vazute = _masoara()
    cai = {(m, c) for m, c, _f, _a in orbi}
    assert ("PUT", "/tenants/{tenant_id}") in cai, (
        "`PUT /tenants/{tenant_id}` nu mai e in clasa oarba. Daca i s-a dat o cale mai specifica, "
        "bine — coboara clichetul. Daca nu, masuratoarea nu mai masoara ce credea.")


# ─────────────────────────────────────────────────────────────────────────────
# [S1/S2, 28.08.2026] VERDICTUL IN PATRU STARI, si cele trei locuri care il citesc.
#
# Decizia lui Costin la R80: **(c)** — gardul ramane masurat si clichetat, (a) si (b) deferate. Dar
# cu un fix obligatoriu: *„cele 51 de rute unde gardul e mut trebuie sa raporteze explicit GRI, nu
# tacere."* Pana azi cadeau in verde prin constructie.
#
# DESCOMPUNEREA CELOR 51, si e o cifra noua care nu contrazice pe cea veche: din cele **51** de rute
# oarbe (ancora nu discrimineaza), **6** sunt deja EXCLUSE — isi declara in cod lipsa ecranului
# (`# [api_intern_v1]`) sau sunt artefacte cunoscute ale detectorului. Raman **45** cu adevarat GRI.
# `_CLICHET = 51` de mai sus masoara ORBIREA instrumentului; `_GRI = 45` masoara cate rute raman,
# dupa declaratii, in starea „nu se poate afirma nimic". Sunt doua intrebari diferite, si de-aia doua
# cifre — nu doua masuratori ale aceluiasi lucru.
_GRI = 45
_EXCLUS = 32
_ROSU = 0


def _verdicte():
    from scan_ancore_rute import verdicte, rezumat, STARI
    return verdicte(_PRAG), rezumat(_PRAG), STARI


def test_fiecare_ruta_are_EXACT_un_verdict():
    """Fara rest: o ruta care n-ar primi verdict ar disparea din toate cele patru numere, si tocmai
    disparitia tacuta e clasa pe care gardul o repara."""
    v, (total, r), stari = _verdicte()
    rute, _js, _o, _vz = _masoara()
    assert len(v) == len(rute) == total, (
        "verdicte %d, rute %d, total %d — cineva a cazut printre" % (len(v), len(rute), total))
    assert sum(r.values()) == total, "sumele nu inchid: %s" % r
    assert set(r) == set(stari), "starile s-au schimbat: %s" % sorted(r)


def test_nicio_ruta_GRI_nu_mai_cade_in_VERDE():
    """**Chiar reparatia**, si se probeaza pe mecanismul care o producea.

    Detectorul vechi raspundea „are apelant" cand toate bucatile literale ale caii se gasesc in JS.
    Pentru o ruta oarba asta e adevarat INTOTDEAUNA — ancora ei apare peste tot. Deci testul de mai
    jos verifica exact asta: fiecare ruta GRI **ar fi trecut** drept verde pe regula veche. Daca
    vreodata n-ar mai fi asa, inseamna ca sensul lui GRI s-a mutat si trebuie recitit."""
    import core.test_ruta_fara_apelant as r70
    v, _r, _s = _verdicte()
    js = r70._static()
    gri = [c for c, stare in v.items() if stare == "GRI"]
    assert gri, "[anti-vacuu] nicio ruta GRI — dar cazul cunoscut din R80 e una"
    ar_fi_trecut = [c for c in gri if all(b in js for b in r70.bucati(c[1]))]
    assert len(ar_fi_trecut) == len(gri), (
        "%d din %d rute GRI NU ar fi trecut drept verde pe regula veche: %s — sensul lui GRI s-a "
        "mutat, reciteste masuratoarea"
        % (len(gri) - len(ar_fi_trecut), len(gri),
           [c for c in gri if c not in ar_fi_trecut][:5]))


def test_clichetul_de_GRI_in_ambele_directii():
    _v, (_total, r), _s = _verdicte()
    assert r["GRI"] <= _GRI, (
        "rutele GRI au crescut de la %d la %d — o ruta noua are o cale pe care ancora n-o "
        "identifica. Ori ii dai o cale mai specifica, ori cobori clichetul si scrii de ce."
        % (_GRI, r["GRI"]))
    assert r["GRI"] >= _GRI, (
        "rutele GRI au scazut de la %d la %d — coboara `_GRI` AICI, `RUTE_GRI_CLICHET` in "
        "verificator si cifra din R80. Toate trei, altfel cele trei cititoare diverg."
        % (_GRI, r["GRI"]))
    assert r["ROSU"] == _ROSU, (
        "rute fara apelant si nedeclarate: %d (asteptat %d)" % (r["ROSU"], _ROSU))


def _numar_din_verificator():
    """`RUTE_GRI_CLICHET` citit ca NOD din AST, nu ca sir cautat in fisier."""
    import ast
    sursa = io.open(os.path.join(_RAD, "verificator_conformitate.py"), encoding="utf-8").read()
    for n in ast.walk(ast.parse(sursa)):
        if (isinstance(n, ast.Assign) and len(n.targets) == 1
                and isinstance(n.targets[0], ast.Name)
                and n.targets[0].id == "RUTE_GRI_CLICHET"
                and isinstance(n.value, ast.Constant)):
            return n.value.value
    return None


def _numar_din_registru():
    """Campul `- **gri**: N` din sectiunea R80 a lui CONFORMITATE.md."""
    import re as _re
    t = io.open(os.path.join(_RAD, "CONFORMITATE.md"), encoding="utf-8").read()
    i = t.index("### R80 —")
    corp = t[i:t.index("### R79 —", i)]
    m = _re.search(r"^- \*\*gri\*\*: (\d+)", corp, _re.M)
    return int(m.group(1)) if m else None


def test_cei_trei_cititori_ai_GRI_ului_nu_pot_diverge():
    """[S2] GRI se citeste in **trei** locuri: garda asta, `verificator_conformitate.py` (adica
    raportul portii) si `CONFORMITATE.md` la R80. Trei cifre scrise separat se despart in tacere —
    a opta instanta a lectiei R62. Aici nu se pot: se compara toate trei cu masuratoarea."""
    _v, (_total, r), _s = _verdicte()
    verif = _numar_din_verificator()
    reg = _numar_din_registru()
    assert verif is not None, "`RUTE_GRI_CLICHET` a disparut din verificator — poarta n-ar mai numi GRI"
    assert reg is not None, (
        "R80 din CONFORMITATE.md n-are campul `- **gri**: N` — registrul n-ar mai spune cat de mut e "
        "gardul, iar cifra ar trai doar in cod")
    assert verif == reg == _GRI == r["GRI"], (
        "cele trei cifre de GRI diverg: garda=%d · verificator=%d · registru=%d · masurat=%d"
        % (_GRI, verif, reg, r["GRI"]))


def test_CALIBRARE_verdictul_deosebeste_EXCLUS_de_GRI():
    """Ordinea starilor nu e o preferinta: o ruta care isi declara in cod lipsa ecranului ramane
    declarata chiar daca ancora ei e oarba. Daca ordinea s-ar inversa, cele 6 declarate ar aparea
    ca «nu stim», iar cifra de orbire ar creste cu 6 fara ca nimic sa se fi schimbat."""
    import core.test_ruta_fara_apelant as r70
    v, _r, _s = _verdicte()
    _rute, _js, orbi, _vz = _masoara()
    oarbe = {(m, c) for m, c, _f, _a in orbi}
    declarate_si_oarbe = oarbe & r70.acceptate()
    assert declarate_si_oarbe, (
        "[anti-vacuu] nicio ruta e si oarba si declarata — calibrarea n-ar avea obiect")
    for c in declarate_si_oarbe:
        assert v[c] == "EXCLUS", "%s e oarba SI declarata, dar verdictul e %r" % (c, v[c])
    assert len(oarbe) - len(declarate_si_oarbe) == _GRI, (
        "descompunerea nu mai inchide: %d oarbe - %d declarate != %d GRI"
        % (len(oarbe), len(declarate_si_oarbe), _GRI))
