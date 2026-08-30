# -*- coding: utf-8 -*-
"""GARD: cele doua registre ale art. 321 alin. (4) CF — ce le tine sa nu se strice tacut.

Trei clase de defect, fiecare cu proba ei:

**1. Diferenta dintre cele doua liste de campuri sa nu fie „netezita".** Lit. e) cere *valoarea
bunurilor transportate*; **lit. f) nu cere nicio valoare**. Amandoua registrele au acum acelasi tabel
si acelasi cod, deci prima „curatenie" tentanta e sa aiba si aceleasi campuri obligatorii — ceea ce ar
insemna ori un camp cerut fara temei, ori unul cerut de norma si nepretins.

**2. Aplicatia sa nu decida ca o scutire se aplica.** Cele cinci exceptii de la registrul
nontransferurilor se ARATA omului. O scutire hotarata de masina pe descrierea unui bun ar produce
exact evidenta care nu se poate apara la un control: completa la vedere, incompleta in fapt. Proba e
pe **AST**, nu pe text: `EXCEPTII_NONTRANSFER` nu are voie sa apara intr-o conditie.

**3. Registrul sa nu completeze in locul omului.** Substanta lui nu se deriva din facturi (un
nontransfer e o miscare de bunuri FARA vanzare). Un producator care ar pune o valoare implicita ar
fabrica evidenta, nu ar tine-o — de-aia refuzul e pe fiecare camp cerut, si NUMESTE campul.

Calibrarile stau pe cazuri SINTETICE, nu pe randurile din baza (METODA §29): ce trebuie sa ramana
adevarat nu e ca o firma anume are un registru incomplet, ci ca refuzul se produce.
"""
import ast
import io
import os

import pytest

from core import db as _db
from core import registre_art321 as _r
from core import tenant_provisioning as _tp

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = "ztest_registre321"

_COMPLET = {
    "partener_denumire": "Lucrari Mecanice SRL", "partener_adresa": "Str. Uzinei 4, Timisoara",
    "data_transport": "2026-03-11", "descriere": "Matrite de presare, lot 7",
    "cantitate": "12.000", "valoare": "48250.00",
}


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def conn():
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA)
                cur.execute(_tp.parametrizeaza_template(
                    io.open(os.path.join(_RAD, "tenant_template.sql"), encoding="utf-8").read(), SCHEMA))
            yield c
        finally:
            c.rollback()


# ── 1. DIFERENTA DINTRE CELE DOUA LISTE ──────────────────────────────────────────────────────

def test_nomenclatorul_felurilor_e_inchis_si_are_exact_doua_intrari():
    """Normele numesc DOUA registre la art. 321, lit. e) si f). Un al treilea `fel` ar fi un registru
    inventat — si ar trece prin `CHECK`-ul din DDL doar daca cineva il schimba si acolo."""
    assert set(_r.FELURI) == {"nontransfer", "bunuri_primite"}
    assert set(_r.TEMEI) == set(_r.FELURI), "un fel fara temei citat, sau un temei fara fel"
    assert set(_r.CAMPURI_CERUTE) == set(_r.FELURI)


def test_valoarea_e_ceruta_NUMAI_la_nontransferuri():
    """Defectul pe care il pazeste: „uniformizarea" celor doua liste.

    Nu e o scapare ca lit. f) n-are valoare — norma chiar nu o cere acolo. Daca cineva o adauga
    „pentru simetrie", registrul bunurilor primite ar refuza inscrieri pe care legea le accepta.
    Invers, daca dispare de la nontransferuri, registrul devine incomplet fata de lit. e).
    """
    assert set(_r.CAMPURI_CERUTE["nontransfer"]) >= {"valoare"}, (
        "lit. e) cere expres valoarea bunurilor transportate")
    assert "valoare" not in set(_r.CAMPURI_CERUTE["bunuri_primite"]), (
        "lit. f) NU cere nicio valoare — un camp obligatoriu fara temei blocheaza o inscriere legala")
    # si restul listei e comuna: diferenta trebuie sa fie EXACT una, altfel s-a strecurat alta
    dif = set(_r.CAMPURI_CERUTE["nontransfer"]) ^ set(_r.CAMPURI_CERUTE["bunuri_primite"])
    assert dif == {"valoare"}, "cele doua liste difera prin altceva decat `valoare`: %s" % sorted(dif)


def test_fiecare_temei_e_structurat_si_citeaza_norma_nu_articolul():
    """Temeiul e HG 1/2016 (normele), nu art. 321 din Cod: articolul trimite, norma spune CE contine.
    E chiar lectia METODA §30, pusa ca aserttiune."""
    for fel, t in _r.TEMEI.items():
        assert t.tip == "HG" and t.nr == 1 and t.an == 2016, (
            "%s nu e sursat pe normele metodologice: %r" % (fel, t))
        assert t.text_citat and len(t.text_citat) > 200, "%s: citarea e prea scurta ca sa fie norma" % fel
    assert _r.TEMEI["nontransfer"].lit == "e"
    assert _r.TEMEI["bunuri_primite"].lit == "f"


# ── 2. APLICATIA NU DECIDE CA O SCUTIRE SE APLICA ────────────────────────────────────────────

def _arbore_modul():
    return ast.parse(io.open(_r.__file__, encoding="utf-8").read())


def test_exceptiile_se_ARATA_nu_se_APLICA():
    """Proba pe STRUCTURA (METODA §23): `EXCEPTII_NONTRANSFER` nu apare in nicio conditie.

    Cautarea unui cuvant in cod n-ar tine — un `if` scris altfel ar trece. Se umbla pe AST si se
    cere ca fiecare folosire a numelui sa fie in afara unui `if`/`while`/comparatie/comprehensiune
    cu filtru. Adica: se poate CITI si TRIMITE mai departe, nu se poate DECIDE pe el.
    """
    arb = _arbore_modul()
    rele = []
    for nod in ast.walk(arb):
        conditii = []
        if isinstance(nod, (ast.If, ast.While)):
            conditii = [nod.test]
        elif isinstance(nod, ast.IfExp):
            conditii = [nod.test]
        elif isinstance(nod, ast.Compare):
            conditii = [nod]
        elif isinstance(nod, (ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp)):
            conditii = [c for g in nod.generators for c in g.ifs]
        for c in conditii:
            for n in ast.walk(c):
                if isinstance(n, ast.Name) and n.id == "EXCEPTII_NONTRANSFER":
                    rele.append(getattr(nod, "lineno", "?"))
    assert not rele, (
        "`EXCEPTII_NONTRANSFER` e folosit intr-o CONDITIE (liniile %s) — adica aplicatia hotaraste "
        "ca o scutire se aplica. Cele cinci cazuri se arata omului; decizia e a lui." % rele)


def test_calibrare_proba_exceptiilor_VEDE_o_decizie(tmp_path):
    """CALIBRARE NEGATIVA pe modul propriu de esec (METODA §22): daca instrumentul n-ar vedea un
    `if`, ar tacea verde la fix defectul pe care-l pazeste. Se probeaza pe cod SINTETIC."""
    def _decizii(sursa):
        arb = ast.parse(sursa)
        gasite = []
        for nod in ast.walk(arb):
            conditii = []
            if isinstance(nod, (ast.If, ast.While, ast.IfExp)):
                conditii = [nod.test]
            elif isinstance(nod, ast.Compare):
                conditii = [nod]
            elif isinstance(nod, (ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp)):
                conditii = [c for g in nod.generators for c in g.ifs]
            for c in conditii:
                for n in ast.walk(c):
                    if isinstance(n, ast.Name) and n.id == "EXCEPTII_NONTRANSFER":
                        gasite.append(getattr(nod, "lineno", "?"))
        return gasite

    assert _decizii("if descriere in EXCEPTII_NONTRANSFER:\n    scutit = True\n"), \
        "instrumentul nu vede un `if` direct"
    assert _decizii("x = [b for b in bunuri if b.desc in EXCEPTII_NONTRANSFER]\n"), \
        "instrumentul nu vede filtrul unei comprehensiuni"
    assert _decizii("scutit = True if d in EXCEPTII_NONTRANSFER else False\n"), \
        "instrumentul nu vede o expresie conditionala"
    assert not _decizii("return {'exceptii': list(EXCEPTII_NONTRANSFER)}\n"), \
        "instrumentul da fals-pozitiv pe simpla REDARE a exceptiilor — atunci n-ar mai fi pazit nimic"


def test_exceptiile_ies_doar_la_registrul_care_le_are():
    """Lit. f) n-are exceptii scrise in norma. Daca ar iesi si acolo, omul ar citi ca poate sa nu
    completeze un registru pentru care norma nu prevede nicio scutire."""
    assert len(_r.EXCEPTII_NONTRANSFER) == 5, "cele cinci cazuri din norma nu mai sunt cinci"


# ── 3. REGISTRUL NU COMPLETEAZA IN LOCUL OMULUI ──────────────────────────────────────────────

@pytest.mark.parametrize("fel", ["nontransfer", "bunuri_primite"])
def test_fiecare_camp_cerut_produce_un_refuz_care_NUMESTE_campul(fel):
    """Refuzul poarta `camp` si `temei` ca DATE. Un mesaj din care omul trebuie sa ghiceasca ce
    lipseste il trimite sa incerce la intamplare pe un formular de treisprezece campuri."""
    for c in _r.CAMPURI_CERUTE[fel]:
        date = {k: v for k, v in _COMPLET.items() if k in _r.CAMPURI_CERUTE[fel] and k != c}
        with pytest.raises(_r.InregistrareIncompleta) as ex:
            _r.valideaza(fel, date)
        assert ex.value.camp == c, (
            "lipseste `%s`, dar refuzul numeste `%s`" % (c, ex.value.camp))
        assert ex.value.temei, "refuz fara temei: `%s` la %s" % (c, fel)


@pytest.mark.parametrize("fel", ["nontransfer", "bunuri_primite"])
def test_un_camp_alb_nu_trece_drept_completat(fel):
    """Spatiile sunt forma cea mai ieftina de evidenta „completa": trec de un `NOT NULL`."""
    date = {k: v for k, v in _COMPLET.items() if k in _r.CAMPURI_CERUTE[fel]}
    date["descriere"] = "   "
    with pytest.raises(_r.InregistrareIncompleta) as ex:
        _r.valideaza(fel, date)
    assert ex.value.camp == "descriere"


def test_fel_necunoscut_e_refuzat():
    with pytest.raises(_r.InregistrareIncompleta) as ex:
        _r.valideaza("registru_inventat", dict(_COMPLET))
    assert ex.value.camp == "fel"


def test_o_inscriere_completa_NU_e_refuzata():
    """Anti-vacuu: fara asta, un `valideaza` care ridica mereu ar trece toate probele de mai sus."""
    _r.valideaza("nontransfer", dict(_COMPLET))
    _r.valideaza("bunuri_primite", {k: v for k, v in _COMPLET.items() if k != "valoare"})


# ── 4. PE DATE REALE ─────────────────────────────────────────────────────────────────────────

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_numarul_de_ordine_se_DERIVA_si_e_unic_pe_registru(conn):
    """Un numar de ordine tastat de om se repeta. Cele doua registre isi numara separat."""
    a = _r.adauga(conn, SCHEMA, "nontransfer", dict(_COMPLET))
    b = _r.adauga(conn, SCHEMA, "nontransfer", dict(_COMPLET))
    c = _r.adauga(conn, SCHEMA, "bunuri_primite",
                  {k: v for k, v in _COMPLET.items() if k != "valoare"})
    assert (a["nr_ordine"], b["nr_ordine"]) == (1, 2), "numerotarea nu curge"
    assert c["nr_ordine"] == 1, "cele doua registre impart aceeasi numerotare"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_registrul_gol_e_o_AFIRMATIE_cu_temei_nu_o_lista_goala(conn):
    """„Niciun rand" nu poate ajunge la om ca tacere. Registrul spune ce acopera chiar cand e gol."""
    a = _r.registru(conn, SCHEMA, "nontransfer")
    assert a["randuri"] == []
    assert a["temei_completitudine"], "registru gol fara temei de completitudine"
    assert a["temei"], "registru fara norma citata"
    assert set(a) >= {"registru", "randuri", "temei", "campuri_cerute", "exceptii"}


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_randurile_ies_in_ordinea_numarului_si_serializate(conn):
    """`Decimal` si `date` nu trec prin JSON. Un registru care crapa la randare e un registru care
    exista in baza si nu exista pentru om — chiar defectul listei 3."""
    import json
    for _ in range(3):
        _r.adauga(conn, SCHEMA, "nontransfer", dict(_COMPLET))
    a = _r.registru(conn, SCHEMA, "nontransfer")
    assert [x["nr_ordine"] for x in a["randuri"]] == [1, 2, 3]
    json.dumps(a)  # nu trebuie sa ridice


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_exceptiile_ajung_la_om_doar_pe_registrul_nontransferurilor(conn):
    assert len(_r.registru(conn, SCHEMA, "nontransfer")["exceptii"]) == 5
    assert _r.registru(conn, SCHEMA, "bunuri_primite")["exceptii"] == []


# ── 5. PRODUCATORUL AJUNGE LA OM ─────────────────────────────────────────────────────────────

def test_exista_rutele_si_ecranul_care_livreaza_registrul():
    """Defectul propriu al listei 3 e „producator fara livrare". Modulul asta s-a nascut din el, deci
    proba ca lantul e intreg sta LANGA producator, nu intr-un registru de trasee citit rar."""
    main = io.open(os.path.join(_RAD, "main.py"), encoding="utf-8").read()
    arb = ast.parse(main)
    cai = set()
    for f in ast.walk(arb):
        if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for d in f.decorator_list:
                if (isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute)
                        and isinstance(d.func.value, ast.Name) and d.func.value.id == "app"
                        and d.args and isinstance(d.args[0], ast.Constant)):
                    cai.add((d.func.attr, d.args[0].value))
    assert ("get", "/tenants/{tenant_id}/registre-art321/{fel}") in cai, "registrul nu se poate citi"
    assert ("post", "/tenants/{tenant_id}/registre-art321/{fel}") in cai, (
        "registrul nu se poate completa — iar substanta lui nu se deriva din facturi, deci ar ramane "
        "gol pentru totdeauna")

    # Pe STRUCTURA, nu pe text (clichet 50 / METODA §23). Prima aserttiune interogheaza inventarul
    # de ecrane — o MULTIME calculata, deci `>=` crapa daca ar deveni vreodata un sir. A doua ia
    # VERDICTUL de ancora al rutei: `ACCEPTAT` inseamna ca fiecare segment discriminant al caii
    # apare ca ancora in JS, adica ruta chiar e chemata. Un `"ecranRegistre321" in js` n-ar fi putut
    # deosebi implementarea de o pomenire intr-un comentariu.
    from core import test_harta_ecrane as _harta
    assert _harta._ecrane_din_cod() >= {"fa-registre321"}, "nu exista ecran care sa-l deschida"

    from scripts import scan_ancore_rute as _anc
    v = _anc.verdicte()
    for metoda in ("GET", "POST"):
        assert v.get((metoda, "/tenants/{tenant_id}/registre-art321/{fel}")) == "ACCEPTAT", (
            "%s pe registre-art321 nu e ACCEPTAT de detectorul de apelanti: %r — ruta exista dar "
            "nimic n-o cheama" % (metoda, v.get((metoda, "/tenants/{tenant_id}/registre-art321/{fel}"))))


def test_citirea_registrului_trece_pe_poarta_COMUNA():
    """Nu pe cea de citire-istorica: registrul e o clasa NOUA de acces, nu a doua iesire a unui
    artefact vechi. Zavorul din `test_poarta_citire_istorica` cere exact asta — proba e aici ca
    largirea sa nu se faca din neatentie, dintr-un copy-paste de la ruta vecina."""
    arb = ast.parse(io.open(os.path.join(_RAD, "main.py"), encoding="utf-8").read())
    for f in ast.walk(arb):
        if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)) and f.name.startswith("registre_art321_"):
            apeluri = [c.func.attr for c in ast.walk(f)
                       if isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)]
            assert set(apeluri) >= {"schema_tenant"}, "%s nu cere nicio poarta" % f.name
            assert set(apeluri).isdisjoint({"schema_tenant_citire"}), (
                "%s a migrat pe poarta de citire-istorica fara sa se declare acolo" % f.name)
