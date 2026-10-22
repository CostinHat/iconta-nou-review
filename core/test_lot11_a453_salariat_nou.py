# -*- coding: utf-8 -*-
"""[lotul 11, deficiența 454] „Salariat nou”: toate erorile la aceeași salvare; CNP și Tip normă marcate obligatorii.

Comanda Costin 11.3 pct.7, verbatim: „454: la salariat nou erorile apar pe rând, în trei salvări; CNP și Tip normă nu sunt marcate
obligatorii.”

CAUZELE. (1) Pe server, `creeaza_salariat` refuza în trepte: întâi validarea de formă (`valideaza_salariat`), abia după ea codul COR în
nomenclator (`_verifica_cor`, un `raise` separat), abia la INSERT CNP-ul deja existent la firmă (constrângerea) — trei salvări pentru
trei erori. (2) CNP-ul nu era cerut la creare, deși D112 refuză salariatul fără el (`d112.pull`). (3) Pe ecran, CNP-ul și Tip normă nu
purtau asteriscul câmpului obligatoriu (DS cap.6 v2.0: „Câmp obligatoriu: marcat cu asterisc roșu prin <span class="oblig">*</span>”),
iar CNP-ul greșit se afla abia din răspunsul serverului. (4) Eroarea „Data încetării nu poate fi înainte de data angajării” era un șir
simplu într-o listă de perechi (câmp, mesaj): `_eroare_campuri` o despacheta și crăpa (500 în loc de refuz).

CNP-uri verificate cu algoritmul cifrei de control (CLAUDE.md): 1800101410013 (valid), 1800101410014 (cifra de control greșită).
"""
import re

import pytest

from core import db as _db, salariati_api, tenant_provisioning as _tp

_SCHEMA = "test_lot11_a453_sn"
_CNP_OK = "1800101410013"
_CNP_GRESIT = "1800101410014"


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
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
            cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
            cur.execute("SET LOCAL search_path TO %s, public" % _SCHEMA)
        try:
            yield c
        finally:
            c.rollback()


def _campuri(e):
    return {x["camp"] for x in getattr(e, "erori_campuri", [])}


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_454_creare_toate_erorile_la_aceeasi_salvare(conn):
    """Un salariat există cu CNP-ul X; „Salariat nou” fără nume, cu CNP-ul X, cu un cod COR inexistent și fără tip normă / funcție de
    bază / scutire: UN refuz, cu toate șapte. RED pe codul vechi: refuzul avea numai câmpurile de formă (COR și CNP-ul dublat veneau
    la salvările următoare)."""
    salariati_api.creeaza_salariat(conn, nume="Pop", cnp=_CNP_OK, cor="251401", salariu_brut=5000, tip_norma="intreaga",
                                   functie_baza=True, scutit_contrib_minim=False, data_angajare="2026-01-01")
    with pytest.raises(ValueError) as ei:
        salariati_api.creeaza_salariat(conn, nume="", cnp=_CNP_OK, cor="999999", salariu_brut=None, tip_norma=None,
                                       functie_baza=None, scutit_contrib_minim=None)
    assert _campuri(ei.value) == {"nume", "cnp", "cor", "salariu_brut", "tip_norma", "functie_baza", "scutit_contrib_minim"}, (
        ei.value.erori_campuri)
    # pe câmp, nu pe textul lipit al tuturor mesajelor: CNP-ul dublat pe `cnp` (același refuz ca la INSERT), COR-ul inexistent pe `cor`
    er = {x["camp"]: x["mesaj"] for x in ei.value.erori_campuri}
    assert er["cnp"] == salariati_api._refuz_cnp(_CNP_OK).erori_campuri[0]["mesaj"], er
    assert er["cor"] == "cod COR inexistent în nomenclator: 999999 (alege din lista)", er


def test_454_cnp_obligatoriu_la_creare_nu_la_editare():
    er = dict(salariati_api.valideaza_salariat({"nume": "X"}, la_creare=True))
    assert er.get("cnp", "").startswith("CNP-ul este obligatoriu"), er
    assert "cnp" not in dict(salariati_api.valideaza_salariat({"nume": "X"}))          # editarea validează numai ce s-a trimis
    # cifra de control greșită: refuz pe câmp, la creare și la editare (cheia 279146358279)
    assert dict(salariati_api.valideaza_salariat({"nume": "X", "cnp": _CNP_GRESIT}, la_creare=True))["cnp"].startswith("CNP invalid")


def test_454_data_incetarii_inainte_de_angajare_e_refuz_pe_camp():
    """Înainte: șirul simplu din listă -> `_eroare_campuri` arunca „too many values to unpack” (500), nu refuzul."""
    with pytest.raises(ValueError) as ei:
        salariati_api.creeaza_salariat(None, nume="X", cnp=_CNP_GRESIT, data_angajare="2026-05-01", data_incetare="2026-04-01")
    er = {x["camp"]: x["mesaj"] for x in ei.value.erori_campuri}
    assert er["data_incetare"] == "Data încetării nu poate fi înainte de data angajării.", er
    assert all(isinstance(e, tuple) and len(e) == 2 for e in salariati_api.valideaza_salariat(
        {"nume": "X", "data_angajare": "2026-05-01", "data_incetare": "2026-04-01"}, la_creare=True))


def _formular_salariat_nou():
    js = open("static/js/ecrane/firme.js", encoding="utf-8").read()
    i = js.index("function formularSalariatNou(")
    return js[i:js.index("\n}\n", i)]


def test_454_garda_ce_cere_serverul_la_creare_e_marcat_pe_ecran():
    """GARDA: fiecare câmp pe care serverul îl cere la creare (`valideaza_salariat({}, la_creare=True)`) poartă asteriscul pe ecranul
    „Salariat nou” (DS cap.6 v2.0) — `camp(…, {obligatoriu: true})`, un DA/NU (`danu`, mereu cu asterisc) sau COR (`campCorLookup(…,
    true)`). Un câmp nou cerut de server și nemarcat pe ecran pică aici."""
    cerute = {c for c, _m in salariati_api.valideaza_salariat({}, la_creare=True)}
    f = _formular_salariat_nou()
    marcate = set(re.findall(r'camp\("(\w+)", "[^"]*", "\w+", \{[^}]*obligatoriu: true', f))
    marcate |= set(re.findall(r'camp\("(\w+)", "[^"]*", "danu"', f))
    if re.search(r'campCorLookup\("sn", true\)', f):
        marcate.add("cor")
    assert cerute <= marcate, "cerute de server la creare, nemarcate obligatorii pe ecran: %s" % sorted(cerute - marcate)
    assert {"cnp", "tip_norma"} <= cerute


def test_454_garda_ecranul_cere_cnp_si_verifica_cifra_de_control_la_aceeasi_salvare():
    """GARDA: butonul „Salvează” cere CNP-ul (gol) și îi verifică cifra de control în aceeași trecere cu celelalte câmpuri (fără
    `return` între ele), cu funcția comună `cnpValid` (una singură în fișier, folosită și de „Corectează datele”)."""
    f = _formular_salariat_nou()
    salv = f[f.index('querySelector("#sn-salveaza").addEventListener'):]
    salv = salv[:salv.index("if (lipsa) return;")]
    # pe structura handlerului, nu pe prezența unui șir: lista câmpurilor cerute completate (în ordine) și apelul cifrei de control pe
    # valoarea citită din `#sn-cnp`, cu eroarea pusă pe același câmp
    assert re.findall(r'\{ id: "(sn-[\w-]+)", mesaj:', salv) == ["sn-nume", "sn-cnp"], salv
    citit = re.findall(r'const (\w+) = corp\.querySelector\("#sn-cnp"\)\.value\.trim\(\);', salv)
    assert len(citit) == 1, salv
    assert re.findall(r'if \(%s && !cnpValid\(%s\)\) \{ eroareCamp\(corp, "(sn-[\w-]+)"' % (citit[0], citit[0]), salv) == ["sn-cnp"], salv
    assert "return" not in salv.split("let lipsa = false;", 1)[1], "un `return` înainte de capătul verificărilor = erori pe rând"
    js = open("static/js/ecrane/firme.js", encoding="utf-8").read()
    assert len(re.findall(r"(?:function cnpValid\b|const cnpValid\b)", js)) == 1


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_454_corecteaza_datele_cnp_dublat_si_data_incetarii_in_acelasi_refuz(conn):
    """Aceeași clasă la „Corectează datele” (PUT): CNP-ul altui salariat al firmei și data încetării înaintea angajării se spun deodată;
    CNP-ul propriu (neschimbat) nu e „dublat”. RED pe codul vechi: șirul simplu al datei încetării rupea refuzul (despachetare)."""
    a = salariati_api.creeaza_salariat(conn, nume="Pop", cnp=_CNP_OK, cor="251401", salariu_brut=5000, tip_norma="intreaga",
                                       functie_baza=True, scutit_contrib_minim=False, data_angajare="2026-01-01")["salariat_id"]
    b = salariati_api.creeaza_salariat(conn, nume="Ion", cnp="5000101410011", cor="251401", salariu_brut=5000, tip_norma="intreaga",
                                       functie_baza=True, scutit_contrib_minim=False, data_angajare="2026-01-01")["salariat_id"]
    with pytest.raises(ValueError) as ei:
        salariati_api.actualizeaza_salariat(conn, b, cnp=_CNP_OK, data_angajare="2026-05-01", data_incetare="2026-04-01")
    assert _campuri(ei.value) == {"cnp", "data_incetare"}, ei.value.erori_campuri
    assert salariati_api.actualizeaza_salariat(conn, a, cnp=_CNP_OK, prenume="Ana") == {"ok": True}
