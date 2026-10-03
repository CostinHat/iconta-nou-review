# -*- coding: utf-8 -*-
"""GARD — capitalul social pe factură (lot 19, defectul 12, 03.10.2026).

Legea 31/1990 art.74 alin.(3): „dacă acestea provin de la o societate cu răspundere limitată, se va menționa și capitalul
social, iar dacă ele provin de la o societate pe acțiuni sau în comandită pe acțiuni, se vor menționa atât capitalul social
subscris, cât și cel vărsat.” Decizia lui Costin: câmp pe profil + refuz la emitere (factura rămâne tastată, mesaj în
termenii contabilului, trimitere la Date firmă, temeiul citat); PFA/II/IF nu intră sub regulă.
"""
import io
import os

import pytest

from core import capital_social as cs
from core import db as _db, tenant_provisioning as _tp

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SCHEMA = "test_capital_social_emitere"


def test_temeiul_e_verbatim_in_corpus():
    act, fisier, citat = cs.TEMEI
    assert citat in " ".join(io.open(os.path.join(RAD, fisier), encoding="utf-8").read().split())


@pytest.mark.parametrize("profil,asteptat", [
    ({"forma_juridica": "SRL"}, ["capitalul social"]),                                   # art.74 alin.(3): SRL -> capitalul social
    ({"forma_juridica": "SRL", "capital_subscris": "200"}, []),
    ({"forma_juridica": "SA", "capital_subscris": "90000"}, ["capitalul social vărsat"]),  # SA -> subscris ȘI vărsat
    ({"forma_juridica": "SCA"}, ["capitalul social subscris", "capitalul social vărsat"]),
    ({"forma_juridica": "SNC"}, []),                                                     # SNC/SCS/ONG: art.74 alin.(3) nu le cere
    ({"forma_juridica": "ALTA"}, []),
    ({}, ["forma juridică a firmei (SRL, SA etc.)"]),                                    # forma necunoscută: nu se ghicește
    ({"tip_firma": "pfa"}, []),                                                          # PFA/II/IF: în afara regulii
])
def test_ce_lipseste(profil, asteptat):
    assert cs.lipsa(profil) == asteptat


def test_randul_de_pe_factura():
    assert cs.text_factura({"forma_juridica": "SRL", "capital_subscris": "200"}) == "Capital social: 200,00 lei"
    assert cs.text_factura({"forma_juridica": "SA", "capital_subscris": "90000", "capital_varsat": "45000"}) == \
        "Capital social subscris: 90.000,00 lei, vărsat: 45.000,00 lei"
    assert cs.text_factura({"forma_juridica": "SNC"}) is None and cs.text_factura({"tip_firma": "pfa"}) is None


def test_mesajul_spune_ce_lipseste_unde_si_temeiul():
    # mesajul E produsul (ce citește contabilul): egalitate pe textul întreg — ce lipsește, unde, temeiul, că factura rămâne
    assert cs.mesaj_refuz(["capitalul social"]) == (
        "Factura nu s-a emis: în Date firmă lipsește capitalul social, pe care legea cere să-l treci pe factură (Legea "
        "31/1990 art. 74 alin. (3)). Completează-l în Date firmă și apasă din nou «Emite» — factura rămâne așa cum ai "
        "scris-o.")
    assert cs.mesaj_refuz(["forma juridică a firmei (SRL, SA etc.)"]) == (
        "Factura nu s-a emis: în Date firmă lipsește forma juridică a firmei — de ea depinde ce capital social trebuie "
        "trecut pe factură (Legea 31/1990 art. 74 alin. (3): la SRL capitalul social, la SA și SCA capitalul subscris și "
        "cel vărsat). Completează forma și capitalul în Date firmă și apasă din nou «Emite» — factura rămâne așa cum ai "
        "scris-o.")


def test_validarea_din_date_firma():
    assert cs.valideaza({"forma_juridica": "XYZ"})[0][0] == "forma_juridica"
    assert cs.valideaza({"capital_subscris": "-5"})[0][0] == "capital_subscris"
    assert cs.valideaza({"capital_subscris": "100", "capital_varsat": "200"})[0][0] == "capital_varsat"
    assert cs.valideaza({"forma_juridica": "SA", "capital_subscris": "100", "capital_varsat": "50"}) == []


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
            yield c
        finally:
            c.rollback()


def _schema(cur, **profil):
    cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
    cur.execute(_tp.parametrizeaza_template(open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), _SCHEMA))
    cur.execute("SET search_path TO %s, public" % _SCHEMA)
    cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,platitor_tva) VALUES (1,'CAP SRL','14399840','Str 1',true)")
    for k, v in profil.items():
        cur.execute("UPDATE firma_profil SET %s = %%s WHERE id = 1" % k, (v,))


_LINIE = {"descriere": "Consultanta", "cantitate": 1, "pret_unitar": 1000, "um": "buc", "cont_venit": "704", "cota_tva": 21}


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_emiterea_refuza_societatea_fara_capital_si_accepta_dupa_completare(conn):
    from core import facturi_api
    with conn.cursor() as cur:
        _schema(cur, forma_juridica="SRL")
    with pytest.raises(ValueError) as e:
        facturi_api.creeaza_factura(conn, "CS1", "2026-07-10", "emisa", [_LINIE], tert_nume="Client PF", tert_pf=True)
    # Legea 31/1990 art.74 alin.(3): SRL -> „se va menționa și capitalul social”
    assert (e.value.cod, e.value.temei, e.value.lipsa) == ("CAPITAL_SOCIAL_LIPSA", "Legea 31/1990 art.74 alin.(3)",
                                                           ["capitalul social"])
    with conn.cursor() as cur:
        cur.execute("UPDATE firma_profil SET capital_subscris = 200 WHERE id = 1")
    r = facturi_api.creeaza_factura(conn, "CS2", "2026-07-10", "emisa", [_LINIE], tert_nume="Client PF", tert_pf=True)
    assert r["ok"]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_pfa_si_factura_primita_nu_sunt_oprite(conn):
    from core import facturi_api
    with conn.cursor() as cur:
        _schema(cur, tip_firma="pfa")
    assert facturi_api.creeaza_factura(conn, "PF1", "2026-07-10", "emisa", [_LINIE], tert_nume="Client PF", tert_pf=True)["ok"]
    with conn.cursor() as cur:
        _schema(cur, forma_juridica="SRL")
    assert facturi_api.creeaza_factura(conn, "FP1", "2026-07-10", "primita", [_LINIE], tert_nume="Furnizor", tert_cui="14399840")["ok"]


def _noduri(fisier, functie):
    """Nodurile AST din corpul funcției `functie` (structură, nu text: un comentariu nu trece)."""
    import ast
    arb = ast.parse(io.open(os.path.join(RAD, fisier), encoding="utf-8").read())
    fn = [n for n in arb.body if isinstance(n, ast.FunctionDef) and n.name == functie]
    assert fn, "%s: funcția %s lipsește" % (fisier, functie)
    return list(ast.walk(fn[0]))


def _cheama(noduri, atribut):
    import ast
    return [n for n in noduri if isinstance(n, ast.Call) and getattr(n.func, "attr", None) == atribut]


def test_refuzul_ajunge_structurat_si_ecranul_trimite_la_date_firma():
    import ast
    n = _noduri("core/uc_tenants.py", "facturi_emite")
    assert _cheama(n, "detaliu"), "facturi_emite nu mai trimite refuzul structurat (capital_social.detaliu)"
    assert any(isinstance(x, ast.Constant) and x.value == "CAPITAL_SOCIAL_LIPSA" for x in n)
    e = cs.refuz(["capitalul social"])
    d = cs.detaliu(e)
    assert (d["fel"], d["cod"], d["regula"], d["lipsa"], d["ecran"], d["mesaj"]) == (
        "neconformitate", "CAPITAL_SOCIAL_LIPSA", "Legea 31/1990 art.74 alin.(3)", ["capitalul social"], "date_firma", str(e))
    # Date firmă: câmpurile citite din ecranul REAL de proba UI (frontend_test/proba_lot19_ui.py, playwright) — artefact
    # JSON, nu șir din sursa JS. LIMITA: artefactul e al ultimei rulări a probei, nu al acestui commit.
    import json
    ui = json.load(io.open(os.path.join(RAD, "frontend_test/proba_lot19_ui.json"), encoding="utf-8"))
    assert ui["date_firma_capital"] == 3 and ui["buton_date_firma"] == 1
    assert ui["pastrat"] == {"denumire": "Consultanta contabila", "nume": "DANTE INTERNATIONAL SA", "cui": "14399840",
                             "pret": "100"}


def test_pdf_tipareste_capitalul():
    assert _cheama(_noduri("core/factura_pdf.py", "genereaza_pdf"), "text_factura"), "PDF-ul nu mai tipărește capitalul"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_profilul_citit_pentru_factura_poarta_capitalul(conn):
    from core import firma_profil_api
    with conn.cursor() as cur:
        _schema(cur, forma_juridica="SA", capital_subscris=90000, capital_varsat=45000)
    p = firma_profil_api.citeste_profil(conn)
    assert (p["forma_juridica"], float(p["capital_subscris"]), float(p["capital_varsat"])) == ("SA", 90000.0, 45000.0)
    assert cs.text_factura(p) == "Capital social subscris: 90.000,00 lei, vărsat: 45.000,00 lei"
