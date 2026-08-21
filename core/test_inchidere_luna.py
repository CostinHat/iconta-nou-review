# -*- coding: utf-8 -*-
"""ACTUL DE ÎNCHIDERE a lunii pe domeniul `facturi` (21.08.2026) — DESIGN_SYSTEM cap.23.

DE CE. `d390_are_operatiuni` întorcea False pe „lună închisă", dar închis însemna doar că luna
CALENDARISTICĂ s-a terminat. Ce lipsea nu era mecanismul (`core/perioada.py` există din cap.23), ci
DOMENIUL și ACTUL: cineva trebuie să declare că evidența lunii e completă.

CELE DOUĂ REGULI ale mecanismului, gardate aici:
  1. **Nu se confirmă peste o absență cunoscută.** Dacă ANAF ne-a dat e-Facturi pe luna aia și nu sunt
     înregistrate, închiderea e REFUZATĂ motivat — nu lăsăm pe cineva să declare complet ceva ce noi
     vedem deja că nu e.
  2. **O modificare de-confirmă AUTOMAT.** O închidere care supraviețuiește unei facturi noi ar afirma
     „evidența lunii e completă" despre alte date decât cele văzute la închidere — exact „verde e o
     afirmație". Simetric cu `pontaj.seteaza`.

ADOPTAREA E PER FIRMĂ: o firmă care n-a închis niciodată o lună rămâne cu comportamentul de dinainte.
Altfel întărirea ar fi convertit clasa în necunoaștere peste noapte — ce s-a decis să NU se facă.
"""
from datetime import date

import pytest

from core import d390 as _d390
from core import db as _db
from core import facturi_api as _fa
from core import inchidere_luna as _il
from core import perioada as _per
from core import tenant_provisioning as _tp

SCHEMA = "ztest_inchidere"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


@pytest.fixture
def conn():
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA)
                cur.execute(_tp.parametrizeaza_template(
                    open("tenant_template.sql", encoding="utf-8").read(), SCHEMA))
                cur.execute("SET search_path TO %s, public" % SCHEMA)
            yield c
        finally:
            c.rollback()


def _efactura_in_asteptare(conn, an, luna, n=1):
    with conn.cursor() as cur:
        for i in range(n):
            cur.execute(
                "INSERT INTO %s.efactura_primite (id_mesaj_anaf, cif_emitent, cif_beneficiar, "
                "xml_sha256, status, data_creare) VALUES (%%s,%%s,%%s,%%s,'descarcata',%%s)" % SCHEMA,
                ("msg-%d-%d-%d" % (an, luna, i), "DE811569869", "14399840",
                 "sha%d%d%d" % (an, luna, i), date(an, luna, 15)))


# ─────────── anti-vacuu: fixtura chiar are ce trebuie ───────────

def test_fixtura_are_tabelele(conn):
    """Fără asta, toate testele de mai jos ar trece pe gol pe o schemă fără tabele."""
    with conn.cursor() as cur:
        for t in ("perioada_confirmata", "efactura_primite", "facturi"):
            cur.execute("SELECT to_regclass(%s)", ("%s.%s" % (SCHEMA, t),))
            assert cur.fetchone()[0], "lipsește %s din schema de test" % t


# ─────────── ciclul de închidere ───────────

def test_luna_curata_se_poate_inchide(conn):
    st = _il.stare(conn, SCHEMA, 2026, 6)
    assert st["confirmat"] is False and st["poate_confirma"] is True and st["blocaj"] is None
    st2 = _il.confirma(conn, SCHEMA, 2026, 6, user_id=7)
    assert st2["confirmat"] is True and st2["confirmat_de"] == 7 and st2["confirmat_la"]
    assert st2["poate_confirma"] is False, "o lună deja închisă nu se mai oferă spre închidere"


def test_nu_se_inchide_peste_documente_in_asteptare(conn):
    """Regula 1. Refuzul NUMEȘTE câte sunt și unde se rezolvă — blocaj motivat, nu «nu se poate»."""
    _efactura_in_asteptare(conn, 2026, 6, n=2)
    st = _il.stare(conn, SCHEMA, 2026, 6)
    assert st["poate_confirma"] is False and st["blocaj"]
    assert "2 e-Facturi" in st["blocaj"], st["blocaj"]
    # Blocajul numeste obstacolul; remediul spune UNDE se rezolva. Vazut PRIVIND captura: ecranul se
    # oprea la „e inca neinregistrata" - contabilul stia ce, nu si unde.
    assert st["remediu"] and "e-Factura" in st["remediu"], st["remediu"]
    with pytest.raises(ValueError) as e:
        _il.confirma(conn, SCHEMA, 2026, 6, user_id=7)
    m = str(e.value)
    assert "06.2026" in m and "e-Factura" in m, m
    assert _per.e_confirmat(conn, SCHEMA, 2026, 6, "facturi")["confirmat"] is False, \
        "a închis luna deși a ridicat"


def test_o_factura_noua_redeschide_luna(conn):
    """Regula 2, miezul. Fără ea, închiderea ar fi o afirmație despre date care s-au schimbat."""
    _il.confirma(conn, SCHEMA, 2026, 6, user_id=7)
    _fa.emite_factura(conn, [{"descriere": "consultanță", "cantitate": 1, "pret_unitar": 100,
                              "cota_tva": 21}],
                      tert_nume="CLIENT SRL", tert_cui="14399840",
                      data_emitere="2026-06-20", moneda="RON", platitor_tva=True)
    assert _per.e_confirmat(conn, SCHEMA, 2026, 6, "facturi")["confirmat"] is False, \
        "luna a rămas închisă după o factură nouă"


def test_stergerea_unei_facturi_redeschide_luna(conn):
    r = _fa.emite_factura(conn, [{"descriere": "x", "cantitate": 1, "pret_unitar": 50, "cota_tva": 21}],
                          tert_nume="CLIENT SRL", tert_cui="14399840",
                          data_emitere="2026-06-20", moneda="RON", platitor_tva=True)
    _il.confirma(conn, SCHEMA, 2026, 6, user_id=7)
    _fa.sterge_factura(conn, r["factura_id"])
    assert _per.e_confirmat(conn, SCHEMA, 2026, 6, "facturi")["confirmat"] is False


def test_factura_din_alta_luna_nu_redeschide(conn):
    """Contra-direcția: dacă orice factură ar redeschide orice lună, închiderea n-ar ține niciodată."""
    _il.confirma(conn, SCHEMA, 2026, 6, user_id=7)
    _fa.emite_factura(conn, [{"descriere": "x", "cantitate": 1, "pret_unitar": 50, "cota_tva": 21}],
                      tert_nume="CLIENT SRL", tert_cui="14399840",
                      data_emitere="2026-07-03", moneda="RON", platitor_tva=True)
    assert _per.e_confirmat(conn, SCHEMA, 2026, 6, "facturi")["confirmat"] is True


def test_redeschiderea_manuala(conn):
    _il.confirma(conn, SCHEMA, 2026, 6, user_id=7)
    st = _il.redeschide(conn, SCHEMA, 2026, 6)
    assert st["confirmat"] is False and st["poate_confirma"] is True


# ─────────── adoptarea: per firmă, nu peste noapte ───────────

def test_firma_care_nu_inchide_luni_ramane_neatinsa(conn):
    """Decizia lui Costin: poarta se ÎNTĂREȘTE, nu convertește clasa în necunoaștere. O firmă care
    n-a închis nicio lună nu primește gri nicăieri."""
    assert _il.prima_luna_inchisa(conn, SCHEMA) is None
    assert _il.luna_neinchisa_desi_firma_inchide(conn, SCHEMA, 2026, 7) is None
    assert _d390.evidenta_incompleta_sau_neinchisa(conn, SCHEMA, 2026, 7) is None


def test_dupa_adoptare_lunile_neinchise_devin_motiv(conn):
    _il.confirma(conn, SCHEMA, 2026, 6, user_id=7)
    assert _il.prima_luna_inchisa(conn, SCHEMA) == (2026, 6)
    m = _il.luna_neinchisa_desi_firma_inchide(conn, SCHEMA, 2026, 7)
    assert m and "07.2026" in m and "nu e declarată închisă" in m, m
    assert _il.luna_neinchisa_desi_firma_inchide(conn, SCHEMA, 2026, 6) is None, \
        "luna închisă nu are ce reproșa"


def test_lunile_dinaintea_adoptarii_raman_neatinse(conn):
    """Punctul de adoptare contează: firma n-avea cum să închidă luni înainte să existe actul.

    DOUĂ luni închise, nu una — prima versiune închidea doar 2026-06, iar acolo «prima» și «ultima»
    coincid: mutația care lua ULTIMA lună închisă drept punct de adoptare a trecut nevăzută. O
    aserțiune care nu poate fi falsificată nu e gardă."""
    _il.confirma(conn, SCHEMA, 2026, 6, user_id=7)
    _il.confirma(conn, SCHEMA, 2026, 9, user_id=7)
    assert _il.prima_luna_inchisa(conn, SCHEMA) == (2026, 6), "punctul de adoptare e cea mai VECHE lună"
    assert _il.luna_neinchisa_desi_firma_inchide(conn, SCHEMA, 2026, 5) is None
    assert _il.luna_neinchisa_desi_firma_inchide(conn, SCHEMA, 2025, 12) is None
    m = _il.luna_neinchisa_desi_firma_inchide(conn, SCHEMA, 2026, 7)
    assert m and "07.2026" in m, "o lună DINTRE cele închise, rămasă deschisă, trebuie semnalată: %r" % m


def test_documentele_in_asteptare_bat_lipsa_inchiderii(conn):
    """Ordinea contează: un fapt observabil (document primit, neînregistrat) e un motiv mai bun decât
    absența unei semnături — și se citește mai ușor."""
    _il.confirma(conn, SCHEMA, 2026, 6, user_id=7)
    _efactura_in_asteptare(conn, 2026, 7, n=1)
    m = _d390.evidenta_incompleta_sau_neinchisa(conn, SCHEMA, 2026, 7)
    assert m and "e-Factură" in m, m


# ─────────── doc-cod: mecanismul e chemat, nu doar scris ───────────

def test_rutele_exista_si_cheama_modulul():
    import os
    rad = os.path.dirname(os.path.dirname(os.path.abspath(_il.__file__)))
    src = open(os.path.join(rad, "main.py"), encoding="utf-8").read()
    for r in ("/tenants/{tenant_id}/facturi/perioada",
              "/tenants/{tenant_id}/facturi/perioada/confirma",
              "/tenants/{tenant_id}/facturi/perioada/redeschide"):
        assert r in src, "ruta lipsă: " + r
    assert "_il.confirma(conn, schema" in src and "cere_rol(\"admin_firma\")" in src


def test_semaforul_foloseste_poarta_completa():
    """Funcția poate fi corectă și nefolosită: semaforul trebuie să cheme varianta care include
    închiderea, nu doar documentele în așteptare."""
    import inspect

    from core import control_fiscal_api as _cf
    src = inspect.getsource(_cf.evalueaza_firma)
    assert "evidenta_incompleta_sau_neinchisa" in src


def test_facturi_api_redeschide_la_scriere():
    """Anti-vacuu pe cablaj: dacă apelul dispare din calea de scriere, închiderea devine o minciună."""
    import inspect
    # `creeaza_factura` e cea care face INSERT-ul; `emite_factura` o cheamă. Prima versiune a testului
    # asertaza pe wrapper — trecea comportamentul, pica cablajul. Ancora stă pe funcția care scrie.
    assert "_redeschide_luna(conn, data_emitere)" in inspect.getsource(_fa.creeaza_factura)
    assert "_redeschide_luna" in inspect.getsource(_fa.sterge_factura)
