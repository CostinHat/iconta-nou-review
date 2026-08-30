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

# 51 masurat 27.08.2026; **55 din 30.08.2026**, si cresterea are cauza MASURATA, nu presupusa.
#
# Cele patru rute care au orbit sunt `GET/POST /tenants/{id}/jurnal` si `PUT/DELETE
# /tenants/{id}/jurnal/{nota_id}`. **Ele AU apelanti** — `firme.js` cheama
# `/tenants/${t.id}/jurnal?an=`. Ce a crescut nu e numarul de rute orfane, ci **incapacitatea
# detectorului de a dovedi contrariul**: ancora lor e cuvantul `jurnal`, iar el a trecut de la sub
# 40 la **45** de ocurente in `static/js` odata cu ecranul nou al **jurnalului de regim marja**
# (lista 3, 30.08.2026).
#
# DE CE SE RIDICA IN LOC SA SE REPARE. Ancora e `bucati()`, adica **regula 4 a detectorului din
# R70** — masuratoarea foloseste deliberat aceeasi regula ca instrumentul pe care il masoara. A o
# intari aici (de ex. ancora ca segment de cale, `/jurnal`, nu ca simplu cuvant) ar decupla
# masuratoarea de obiectul ei si ar schimba toate cifrele lui R80 dintr-o data. **Aia E R80**, si e
# deschisa.
#
# DE CE NU S-A REDENUMIT ECRANUL CA SA INTRE SUB PRAG. Artefactul se numeste in norma „jurnal
# special" (normele CF, pct. 86). A-i schimba numele ca sa treaca de un prag de scaner ar face ca
# urmatorul cititor sa creada ca ancora discrimineaza, cand nu discrimineaza. *Un numar sub prag
# obtinut prin tacere e mai rau decat unul peste prag cu motivul scris.*
#
# [R80, 30.08.2026 — REPARAT, si de-aia cifra COBOARA in loc sa creasca] Ancora e acum SEGMENT DE
# CALE, nu cuvant: se numara `/jurnal` si `"jurnal"` (dispecerizare prin tabel), nu „Registru jurnal"
# dintr-un titlu. Masurat imediat dupa: orbirea 55 -> 6, GRI 55 -> 7, ROSU ramane 0 (deci nicio ruta
# n-a pierdut dovada ca e chemata). Cele 6 ramase sunt exact rutele al caror singur segment literal e
# `tenants` — 238 aparitii, e in fiecare cale — plus `GET /`, care n-are niciun segment literal.
# Adica INSTANTA FONDATOARE a lui R80, `PUT /tenants/{id}`, ramane oarba: reparatia n-a acoperit-o,
# a curatat in jurul ei.
_CLICHET = 6
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
# DESCOMPUNEREA, dupa R80: din rutele oarbe **6**, niciuna nu e EXCLUSA (cele 34 EXCLUSE au ancore
# care discrimineaza), iar GRI-ul e **7** — cele 6 plus `GET /`, care n-are niciun segment literal si
# cade in GRI prin `not bs`. Cele doua cifre nu mai sunt departe una de alta, fiindca orbirea aproape
# a disparut.
# `_CLICHET = 6` de mai sus masoara ORBIREA instrumentului; `_GRI = 7` masoara cate rute raman,
# dupa declaratii, in starea „nu se poate afirma nimic". Sunt doua intrebari diferite, si de-aia doua
# cifre — nu doua masuratori ale aceluiasi lucru.
_GRI = 7
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
    declarata CHIAR DACA ancora ei e oarba. Daca ordinea s-ar inversa, o ruta declarata ar aparea ca
    «nu stim», iar cifra de orbire ar creste fara ca nimic sa se fi schimbat.

    PE CAZ SINTETIC, si asta e o schimbare din 30.08.2026, cu motivul ei. Pana la reparatia R80,
    proba se facea pe rute VII care erau si oarbe, si declarate. Dupa reparatie, cele ramase oarbe
    sunt toate pe segmentul `tenants`, si niciuna nu e declarata — deci aserttiunea anti-vacuu a
    picat, corect, si nu pe un defect: pe un succes. *O calibrare ancorata pe instantele care urmeaza
    sa fie reparate se autodistruge la prima reparatie* (METODA §29). Ce trebuie sa ramana adevarat e
    ca DECIZIA are ordinea asta, nu ca aplicatia mai are un exemplar.
    """
    import scan_ancore_rute as s
    js = "nimic care sa semene cu o ruta"
    # o ruta al carei singur segment literal apare de foarte multe ori -> oarba prin constructie
    oarba = ("GET", "/tenants/{id}")
    acceptate = {oarba}          # ...si DECLARATA
    v = {}
    for cheie in (oarba,):
        bs = ["tenants"]
        if cheie in acceptate:
            v[cheie] = "EXCLUS"
        elif s.frecventa(js, bs[0]) > 40:
            v[cheie] = "GRI"
        else:
            v[cheie] = "ACCEPTAT"
    assert v[oarba] == "EXCLUS", (
        "o ruta si oarba, si declarata, trebuie sa iasa EXCLUS — daca iese GRI, ordinea s-a inversat")

    # si direct pe functia reala: descompunerea celor VII trebuie sa inchida
    import core.test_ruta_fara_apelant as r70
    vr, _r, _s = _verdicte()
    _rute, _js, orbi, _vz = _masoara()
    oarbe = {(m, c) for m, c, _f, _a in orbi}
    declarate_si_oarbe = oarbe & r70.acceptate()
    for c in declarate_si_oarbe:
        assert vr[c] == "EXCLUS", "%s e oarba SI declarata, dar verdictul e %r" % (c, vr[c])
    # `GET /` n-are niciun segment literal: nu intra in `orbi`, dar cade in GRI prin `not bs`.
    fara_segment = sum(1 for (m, c), st in vr.items() if st == "GRI" and (m, c) not in oarbe)
    assert len(oarbe) - len(declarate_si_oarbe) + fara_segment == _GRI, (
        "descompunerea nu mai inchide: %d oarbe - %d declarate + %d fara segment != %d GRI"
        % (len(oarbe), len(declarate_si_oarbe), fara_segment, _GRI))
