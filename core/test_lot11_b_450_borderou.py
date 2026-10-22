# -*- coding: utf-8 -*-
"""[lotul 11, subagentul b] Borderoul de achiziție (450), stornarea lui (decizia 10.3) și NIR-ul cu număr repetat (decizia 10.3).

450 — comanda Costin 11.1 pct.9, verbatim: „borderoul de achiziție a creat tacit un articol nou «grau» lângă cel existent. Articolul se
alege din nomenclator; unul nou se creează doar la cerere explicită. După generare, formularul nu trebuie să permită dublarea notei.”
Cauza (F1 = tenant_049, citit pe producție: articolele 5 și 6, ambele „grau”, din BA-2 și BA-3): borderoul trimitea intrării în stoc numai
denumirea, iar `stocuri_cv_api.intrare` fără `articol_id` creează MEREU un articol nou. Plus: serverul primea de două ori același borderou.

Decizia 10.3 pct.4, verbatim: „Borderoul se corectează prin stornare, ca factura.” — până azi nu se putea corecta deloc (ștergerea îl
refuza pentru că are notă, stornarea îl refuza pentru că nu e factură emisă). „NIR cu număr repetat: refuzat, cu mesaj numit.”

Temeiul stornării: OMFP 1802/2014 pct.69 („corectarea cu semnul minus a operațiunii inițiale (stornare în roșu)”) și, pentru „nu se
stornează de două ori / nu se stornează o stornare”, CF art.330 alin.(1) lit.b) (ca la factură — lotul 10, C74). Restul: N/A — regulă de
formă (un articol nu se dublează; un document nu se înregistrează de două ori; un număr nu se dă de două ori).
Schemă efemeră din template, în tranzacție anulată."""
import ast
import contextlib
import io
import os
import re
from decimal import Decimal

import pytest

from core import db as _db, erori, tenant_provisioning as _tp

SCH = "tenant_test_lot11_b_450"
RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


class _P:
    def __init__(s, c): s._c = c
    def commit(s): pass
    def rollback(s): pass
    def __getattr__(s, n): return getattr(s._c, n)


@pytest.fixture
def conn(monkeypatch):
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
                cur.execute(_tp.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), SCH))
                cur.execute("SET LOCAL search_path TO %s, public" % SCH)
                cur.execute("INSERT INTO firma_profil (id, nume, cui, platitor_tva, forma_juridica, capital_subscris, metoda_stoc) "
                            "VALUES (1, 'F1 SRL', '14399840', true, 'SRL', 200, 'cantitativ_valoric')")
                cur.execute("UPDATE firma_profil SET tip_decont = 'lunar' WHERE id = 1")
            from core import auth_api, uc_comun, uc_tenants
            monkeypatch.setattr(uc_tenants.db, "get_conn", lambda *a, **k: contextlib.nullcontext(_P(c)))
            monkeypatch.setattr(auth_api, "schema_tenant", lambda *a, **k: SCH)
            monkeypatch.setattr(uc_comun, "_cere_luna_deschisa", lambda *a, **k: None)
            yield c
        finally:
            c.rollback()


_BA = {"data": "2026-10-20", "furnizor_nume": "Maria Ionescu", "furnizor_adresa": "Str. Mare 2, Cluj-Napoca", "furnizor_act": "CJ 123456",
       "valoare": 200, "cont_cheltuiala": "371", "cantitate": 200, "um": "kg", "categorie": "1001"}


def _borderou(corp):
    from core import uc_tenants
    return uc_tenants.achizitie_neinregistrat(1, dict(corp), {"uid": 1})


def _unu(c, sql, *a):
    with c.cursor() as cur:
        cur.execute(sql, a)
        return cur.fetchone()


def _articole(c):
    with c.cursor() as cur:
        cur.execute("SELECT id, denumire FROM articole ORDER BY id")
        return cur.fetchall()


# ── 450a: articolul se alege din nomenclator; unul nou numai la cerere explicită ─────────────────────────────────────────────
def test_def_450_articolul_ales_din_lista_nu_creeaza_altul(conn):
    """Cazul F1: „Grâu” e deja în nomenclator; borderoul îl alege din listă (`articol_id`) -> intrarea e pe el, niciun articol nou.
    MUTAȚIE: `"articol_id": articol_ales[0] if articol_ales else None` -> `"articol_id": None` -> intrarea creează al doilea articol -> pică."""
    with conn.cursor() as cur:
        cur.execute("INSERT INTO articole (denumire, um) VALUES ('Grâu', 'kg') RETURNING id")
        aid = cur.fetchone()[0]
    r = _borderou({**_BA, "articol_id": aid})
    assert _articole(conn) == [(aid, "Grâu")], _articole(conn)   # comanda 11.1 pct.9: „Articolul se alege din nomenclator”
    assert (r["intrare_stoc"]["articol_id"], r["intrare_stoc"]["articol_nou"]) == (aid, False), r
    assert _unu(conn, "SELECT articol_id, cantitate FROM miscari_stoc WHERE factura_id = %s", r["factura_id"]) == (aid, Decimal("200.000"))


def test_def_450_denumirea_fara_diacritice_gaseste_articolul_existent(conn):
    """„grau” scris, „Grâu” în nomenclator: fără cerere explicită, borderoul ia articolul existent (nu creează nimic); cu „articol nou”
    cerut explicit, refuzul numește articolul existent lângă denumire. MUTAȚIE: `cheie_denumire` fără scoaterea diacriticelor -> „grau”
    nu găsește „Grâu”, refuzul spune „nu e în nomenclator” -> pică."""
    with conn.cursor() as cur:
        cur.execute("INSERT INTO articole (denumire, um) VALUES ('Grâu', 'kg') RETURNING id")
        aid = cur.fetchone()[0]
    r = _borderou({**_BA, "articol": "grau"})
    assert r["intrare_stoc"]["articol_id"] == aid and len(_articole(conn)) == 1, (r, _articole(conn))
    with pytest.raises(erori.DateInvalide) as e:
        _borderou({**_BA, "furnizor_nume": "Vasile Test", "articol": "GRAU ", "articol_nou": True})
    d = e.value.args[0]
    assert [(x["camp"], x["mesaj"]) for x in d["erori_campuri"]] == [
        ("op-articol_den", "Articolul «Grâu» e deja în nomenclator: alege-l din listă — borderoul nu creează un al doilea articol cu același "
                           "nume.")], d
    assert len(_articole(conn)) == 1


def test_def_450_articol_necunoscut_fara_cerere_explicita_se_refuza(conn):
    """Un articol care nu e în nomenclator și nu e cerut explicit nou -> refuz lângă „Articolul”, nimic scris; cu `articol_nou` -> se creează.
    MUTAȚIE: ramura `elif not articol_ales and not articol_nou:` scoasă -> intrarea creează tacit articolul -> pică."""
    with pytest.raises(erori.DateInvalide) as e:
        _borderou({**_BA, "articol": "Orz"})
    assert [x["camp"] for x in e.value.args[0]["erori_campuri"]] == ["op-articol"], e.value.args
    assert _articole(conn) == [] and _unu(conn, "SELECT count(*) FROM facturi")[0] == 0
    r = _borderou({**_BA, "articol": "Orz", "articol_nou": True})
    assert [d for _i, d in _articole(conn)] == ["Orz"] and r["intrare_stoc"]["articol_nou"] is True, r


def test_def_450_intrarea_manuala_nu_dubleaza_articolul(conn):
    """Aceeași clasă pe „Mișcări, fișe de magazie” (intrarea manuală cu „— articol nou —”): denumirea unui articol existent -> refuz lângă
    denumire. MUTAȚIE: verificarea din `cv_intrare` scoasă -> al doilea „grau” -> pică."""
    from core import uc_tenants
    with conn.cursor() as cur:
        cur.execute("INSERT INTO articole (denumire, um) VALUES ('Grâu', 'kg')")
    with pytest.raises(erori.CerereGresita) as e:
        uc_tenants.cv_intrare(1, {"denumire": "grau", "data": "2026-10-20", "cantitate": 1, "pret_unitar": 1}, {"uid": 1})
    m_dublura = "Articolul «Grâu» e deja în listă: alege-l de acolo — intrarea nu creează un al doilea articol cu același nume."
    assert e.value.args[0] == {"mesaj": m_dublura, "erori_campuri": [{"camp": "cv-den", "mesaj": m_dublura}]}, e.value.args
    assert len(_articole(conn)) == 1


def test_def_450_nomenclatorul_produselor_potriveste_fara_diacritice(conn):
    """Produse: „grau” găsește „Grâu” (propunerea pe factură, dublura la creare), iar articolul „grau” din stoc nu mai apare „cotă lipsă”
    lângă produsul „Grâu”."""
    from core import produse_api as pa
    with conn.cursor() as cur:
        cur.execute("SET LOCAL search_path TO %s, public" % SCH)
        cur.execute("INSERT INTO produse (denumire, um, cota_tva) VALUES ('Grâu', 'kg', 11)")
        cur.execute("INSERT INTO articole (denumire, um) VALUES ('grau', 'kg')")
    assert pa.cauta_dupa_denumire(conn, "GRAU")["denumire"] == "Grâu"
    assert pa.creeaza(conn, "grau", cota_tva=11)["existent"] is True
    assert [p["denumire"] for p in pa.lista(conn)] == ["Grâu"]


def test_cheia_denumirii():
    from core.produse_api import cheie_denumire as k
    assert k("Grâu") == k("grau") == k("  GRAU ") == k("grâu") == "grau"   # â precompus și descompus
    assert k("Șură ţuică") == k("sura tuica") and k("Marfa  A") == k("marfa a") and k("Orz") != k("Ovăz")


# ── 450b: formularul retrimis nu dublează nota ───────────────────────────────────────────────────────────────────────────────
def test_def_450_a_doua_trimitere_a_aceluiasi_borderou_se_refuza(conn):
    """Același borderou trimis de două ori (formularul apăsat iar după generare) -> al doilea refuzat, numit, nimic scris; alt vânzător sau
    un număr scris (a doua cumpărare, alt document) trec. MUTAȚIE: verificarea `_borderou_identic` scoasă -> două note -> pică."""
    r = _borderou({**_BA, "articol": "Grâu", "articol_nou": True})
    note = _unu(conn, "SELECT count(*) FROM inregistrari")[0]
    with pytest.raises(erori.DateInvalide) as e:
        _borderou({**_BA, "articol_id": r["intrare_stoc"]["articol_id"]})
    d = e.value.args[0]
    assert d["cod"] == "BORDEROU_DUBLAT" and d["erori_campuri"][0]["camp"] == "op-numar", d
    assert d["mesaj"].startswith("Borderoul acesta e deja înregistrat: BA-1 din 20.10.2026 (Maria Ionescu, 200,00 lei)"), d["mesaj"]
    assert (_unu(conn, "SELECT count(*) FROM facturi")[0], _unu(conn, "SELECT count(*) FROM inregistrari")[0]) == (1, note)
    assert _borderou({**_BA, "articol": "Grâu", "furnizor_nume": "Ion Popescu"})["numar"] == "BA-2"
    assert _borderou({**_BA, "articol": "Grâu", "numar": "BA-7"})["numar"] == "BA-7"


def test_def_450_borderoul_pe_cheltuiala_retrimis_se_refuza_si_el(conn):
    """Fără articol (cont de cheltuială): același vânzător, aceeași dată, aceeași valoare -> a doua trimitere refuzată."""
    c = {**_BA, "cont_cheltuiala": "6028", "cantitate": "", "um": ""}
    _borderou(c)
    with pytest.raises(erori.DateInvalide) as e:
        _borderou(c)
    assert e.value.args[0]["cod"] == "BORDEROU_DUBLAT"


# ── decizia 10.3: borderoul se corectează prin stornare ─────────────────────────────────────────────────────────────────────────
def test_decizia_103_borderoul_se_storneaza_ca_factura(conn):
    """Stornarea scrie al doilea document (borderou BA-2, `storno_din_id` = BA-1, cantitatea cu minus), nota inversă (371 = 401 cu minus,
    OMFP 1802/2014 pct.69: „corectarea cu semnul minus a operațiunii inițiale”) și stornează în roșu intrarea în stoc; a doua stornare și
    stornarea stornării se refuză (CF art.330 alin.(1) lit.b)). MUTAȚIE: verificarea „deja stornat” scoasă -> a doua stornare trece -> pică
    (indexul unic `facturi_borderou_storno_uniq` o oprește și el, cu refuz numit)."""
    from core import uc_tenants, stocuri_cv_api as cv
    r = _borderou({**_BA, "articol": "Grâu", "articol_nou": True})
    s = uc_tenants.borderou_storneaza(1, r["factura_id"], {"data": "2026-10-21"}, {"uid": 1})
    assert s["numar"] == "BA-2" and s["storno_din_id"] == r["factura_id"], s
    assert _unu(conn, "SELECT tip, directie, storno_din_id, tert_nume, tert_act_identitate, categorie_331 FROM facturi WHERE id = %s",
                s["factura_id"]) == ("borderou", "primita", r["factura_id"], "Maria Ionescu", "CJ 123456", "1001")
    assert _unu(conn, "SELECT cantitate FROM factura_linii WHERE factura_id = %s", s["factura_id"])[0] == Decimal("-200.000")
    with conn.cursor() as cur:
        cur.execute("SELECT l.cont_debit, l.cont_credit, l.suma, i.status FROM inregistrari i JOIN inregistrari_linii l "
                    "ON l.inregistrare_id = i.id WHERE i.factura_id = %s", (s["factura_id"],))
        assert cur.fetchall() == [("371", "401", Decimal("-200.00"), "ciorna")]   # OMFP 1802/2014 pct.69: stornarea în roșu
    fisa = cv.fisa(conn, SCH, r["intrare_stoc"]["articol_id"])
    assert (fisa["linii"][-1]["sold_cantitate"], fisa["linii"][-1]["storno"]) == ("0.000", True), fisa
    with pytest.raises(erori.DateInvalide) as e:
        uc_tenants.borderou_storneaza(1, r["factura_id"], {"data": "2026-10-21"}, {"uid": 1})
    assert e.value.args == ("Borderou de achiziție BA-1 din 20.10.2026 e deja stornat prin Borderou de achiziție BA-2 din 21.10.2026: nu "
                            "mai rămâne nimic de stornat (CF art.330 alin.(1) lit.b)).",), e.value.args   # CF art.330 alin.(1) lit.b)
    with pytest.raises(erori.DateInvalide) as e:
        uc_tenants.borderou_storneaza(1, s["factura_id"], {"data": "2026-10-21"}, {"uid": 1})
    assert e.value.args == ("Borderou de achiziție BA-2 din 21.10.2026 e el însuși o stornare (a documentului Borderou de achiziție BA-1 "
                            "din 20.10.2026): o stornare nu se stornează la rândul ei (CF art.330 alin.(1) lit.b)).",), e.value.args   # CF art.330 alin.(1) lit.b)
    l = {b["numar"]: b for b in uc_tenants.borderouri_lista(1, 2026, 10, {"uid": 1})["borderouri"]}
    assert (l["BA-1"]["stornat_de"], l["BA-2"]["storno_din"]) == ("Borderou de achiziție BA-2 din 21.10.2026",
                                                                  "Borderou de achiziție BA-1 din 20.10.2026"), l
    # după stornare, același borderou se poate scrie din nou (cel corect): cel stornat nu mai e „viu”
    assert _borderou({**_BA, "articol": "Grâu"})["numar"] == "BA-3"


def test_decizia_103_stornarea_nu_lasa_stocul_negativ(conn):
    """Marfa borderoului a ieșit deja din stoc -> stornarea se refuză, numit, nimic scris. MUTAȚIE: refuzul de stoc scos (ValueError
    ignorat) -> stornarea trece cu stoc negativ -> pică."""
    from core import uc_tenants, stocuri_cv_api as cv
    r = _borderou({**_BA, "articol": "Grâu", "articol_nou": True})
    cv.iesire(conn, SCH, {"articol_id": r["intrare_stoc"]["articol_id"], "data": "2026-10-20", "cantitate": 150})
    n = _unu(conn, "SELECT count(*) FROM facturi")[0]
    with pytest.raises(erori.DateInvalide) as e:
        uc_tenants.borderou_storneaza(1, r["factura_id"], {"data": "2026-10-21"}, {"uid": 1})
    assert e.value.args == ("Stornarea nu s-a făcut: Borderou de achiziție BA-1 din 20.10.2026 a adus în stoc Grâu, iar marfa a ieșit deja. "
                            "Stornarea intrării ar lăsa stocul negativ. Anulează întâi ieșirile care au folosit-o, apoi stornează borderoul.",), \
        e.value.args
    assert _unu(conn, "SELECT count(*) FROM facturi")[0] == n


def test_decizia_103_stornarea_se_scade_din_d394(conn):
    """D394: borderoul (op. N, cereale) și stornarea lui se compensează — nicio operațiune N rămasă pe vânzător."""
    from core import uc_tenants, d394
    from core.common import Perioada
    r = _borderou({**_BA, "articol": "Grâu", "articol_nou": True})
    with conn.cursor() as cur:
        cur.execute("SET LOCAL search_path TO %s, public" % SCH)
    _p, inainte = d394.pull(conn, SCH, Perioada(2026, luna=10))
    uc_tenants.borderou_storneaza(1, r["factura_id"], {"data": "2026-10-21"}, {"uid": 1})
    with conn.cursor() as cur:
        cur.execute("SET LOCAL search_path TO %s, public" % SCH)
    _p, dupa = d394.pull(conn, SCH, Perioada(2026, luna=10))
    baza = lambda d: sum(Decimal(str(f.get("baza") or 0)) for f in d["facturi"] if (f.get("nume") or "") == "Maria Ionescu")
    assert (baza(inainte), baza(dupa)) == (Decimal("200"), Decimal("0")), (inainte["facturi"], dupa["facturi"])


def test_450_cerealele_borderoului_se_aleg_pe_codul_nc(conn):
    """D394 declară cerealele achiziționate (op. N) cu subcodul NC (`d394._op11_cod`: centralizatorul 21 „nu e valid la op11”): „cereale”
    se refuză lângă câmp, la scriere, nu la declarație; lista formularului are codurile NC (HG 1/2016 pct.109 alin.(7)) și restul
    categoriilor N. MUTAȚIE: refuzul „cereale” scos -> borderoul trece și D394 îl exclude („cereale fără subcodul NC”) -> pică."""
    from core import uc_tenants, d394, produse_api
    with pytest.raises(erori.DateInvalide) as e:
        _borderou({**_BA, "articol": "Grâu", "articol_nou": True, "categorie": "cereale"})
    assert e.value.args[0]["erori_campuri"][0]["camp"] == "op-categorie", e.value.args   # HG 1/2016 pct.109 alin.(7): codurile NC
    cat = [c["cod"] for c in uc_tenants.borderouri_lista(1, 2026, 10, {"uid": 1})["categorii_n"]]
    assert cat[:11] == list(produse_api.NC_CEREALE) and set(cat[11:]) == set(d394.CODPR_N) - {"cereale"}, cat
    assert set(uc_tenants.ETICHETE_N) == set(d394.CODPR_N) - {"cereale"}


# ── decizia 10.3: NIR cu număr repetat ────────────────────────────────────────────────────────────────────────────────────────
_NIR = {"numar": "5", "data": "2026-10-20", "furnizor": "DANTE INTERNATIONAL SA", "cui": "14399840", "factura_sosita": False}


def _nir(conn, **k):
    from core import uc_tenants
    with conn.cursor() as cur:
        cur.execute("INSERT INTO articole (denumire, um) VALUES ('Marfa %s', 'buc') RETURNING id" % k.pop("art", "A"))
        aid = cur.fetchone()[0]
    corp = {**_NIR, "linii": [{"articol_id": aid, "denumire": "x", "cantitate": 2, "pret_achizitie": 25, "cota_tva": 21}], **k}
    return uc_tenants.stocuri_adauga(1, corp, {"uid": 1})


def test_decizia_103_nir_cu_numar_repetat_se_refuza_numit(conn):
    """Al doilea NIR cu numărul 5 în același an -> refuz lângă „număr NIR”, cu NIR-ul care îl are; nimic scris. Alt an -> trece.
    MUTAȚIE: verificarea `_nir_cu_numarul` din `stocuri_adauga` scoasă -> al doilea NIR nr 5 -> pică."""
    _nir(conn)
    with pytest.raises(erori.DateInvalide) as e:
        _nir(conn, art="B", numar=" 5 ")
    d = e.value.args[0]
    assert d["erori_campuri"][0] == {"camp": "sn-numar", "mesaj": "Numărul 5 e deja al NIR-ului din 20.10.2026 (DANTE INTERNATIONAL SA). "
                                     "Scrie alt număr; un NIR respins la validare se reface din lista NIR-urilor („Refă NIR-ul”), cu numărul "
                                     "lui."}, d
    assert _unu(conn, "SELECT count(*) FROM nir")[0] == 1
    _nir(conn, art="C", data="2027-01-05")
    assert _unu(conn, "SELECT count(*) FROM nir")[0] == 2


def test_decizia_103_nir_repetat_spune_toate_refuzurile_deodata(conn):
    """Numărul repetat și o linie fără cotă -> ambele refuzuri, deodată (440), nimic scris."""
    _nir(conn)
    with conn.cursor() as cur:
        cur.execute("INSERT INTO articole (denumire, um) VALUES ('Marfa Z', 'buc') RETURNING id")
        aid = cur.fetchone()[0]
    from core import uc_tenants
    with pytest.raises(erori.DateInvalide) as e:
        uc_tenants.stocuri_adauga(1, {**_NIR, "linii": [{"articol_id": aid, "denumire": "x", "cantitate": 2, "pret_achizitie": 25}]},
                                  {"uid": 1})
    campuri = [x["camp"] for x in e.value.args[0]["erori_campuri"]]
    assert campuri[0] == "sn-numar" and len(campuri) == 2, e.value.args
    assert _unu(conn, "SELECT count(*) FROM nir")[0] == 1


def test_decizia_103_nir_refacut_isi_pastreaza_numarul(conn):
    """Refacerea unui NIR (`refacut_din_id`) poartă numărul lui: nu e un număr repetat."""
    from core import nir_legare  # noqa: F401  (modulul NIR-ului legat se încarcă la fel ca pe ruta reală)
    _nir(conn)
    nid = _unu(conn, "SELECT id FROM nir")[0]
    with conn.cursor() as cur:
        cur.execute("INSERT INTO nir (numar, data, furnizor, refacut_din_id) VALUES ('5', '2026-10-21', 'X', %s)", (nid,))
    from core import uc_tenants
    with conn.cursor() as cur:
        assert uc_tenants._nir_cu_numarul(cur, SCH, "5", "2026-10-22", None)[2] == "X"   # NIR-ul vechi e înlocuit: numărul e al refacerii
        cur.execute("SELECT id FROM nir WHERE refacut_din_id IS NOT NULL")
        assert uc_tenants._nir_cu_numarul(cur, SCH, "5", "2026-10-22", cur.fetchone()[0]) is None


# ── GARD: fiecare câmp citit de server are câmpul lui pe ecranul borderoului ─────────────────────────────────────────────────────
#: cheia din corp -> id-ul câmpului din `borderou_ecran.js` (unde nu e `op-<cheie>`)
_CAMP = {"articol": "op-articol_den", "articol_id": "op-articol", "articol_nou": "op-articol"}


def _chei_citite():
    uc = io.open(os.path.join(RAD, "core", "uc_tenants.py"), encoding="utf-8").read()
    fn = next(n for n in ast.parse(uc).body if isinstance(n, ast.FunctionDef) and n.name == "achizitie_neinregistrat")
    chei = set()
    for x in ast.walk(fn):
        if isinstance(x, ast.Subscript) and isinstance(x.value, ast.Name) and x.value.id == "corp" and isinstance(x.slice, ast.Constant):
            chei.add(x.slice.value)
        if isinstance(x, ast.Call) and x.args and isinstance(x.args[0], ast.Name) and x.args[0].id == "corp":
            if isinstance(x.func, ast.Attribute) and x.func.attr == "bifa" and isinstance(x.args[1], ast.Constant):
                chei.add(x.args[1].value)
        if isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute) and x.func.attr == "get" and isinstance(x.func.value, ast.Name) \
                and x.func.value.id == "corp" and x.args and isinstance(x.args[0], ast.Constant):
            chei.add(x.args[0].value)
    return chei


def test_gard_fiecare_cheie_a_borderoului_are_campul_ei_pe_ecran():
    """Ecranul borderoului nu e în motorul Operațiunilor (scanat de `scan_formulare_operatiuni`): gardul lui propriu. MUTAȚIE: câmpul
    „Domiciliul vânzătorului” scos din `borderou_ecran.js` -> pică; o cheie nouă citită de server fără câmp -> pică."""
    js = io.open(os.path.join(RAD, "static", "js", "ecrane", "borderou_ecran.js"), encoding="utf-8").read()
    chei = _chei_citite()
    assert {"data", "furnizor_nume", "furnizor_adresa", "furnizor_act", "valoare", "articol", "articol_id", "articol_nou"} <= chei, chei
    # câmpul = definiția lui în formular (`camp(` / `text(` / `campNumeric(` cu id-ul lui, sau `id="…"`), nu o citire `v("…")`
    # [lotul 11, K] helperul câmpului numeric se cheamă `campNumeric` (`numar` era citit de verificator ca „număr” fără diacritice)
    lipsa = sorted(k for k in chei if not re.search(r'(?:\bcamp|\btext|\bcampNumeric)\("%s"|id="%s"' % ((re.escape(_CAMP.get(k, "op-" + k)),) * 2), js))
    assert lipsa == [], "cheile citite de server fără câmp pe ecranul borderoului: %s" % lipsa


def _butoane(html_text):
    """{id: textul butonului} pentru elementele <button> din fragmentul HTML."""
    import html.parser

    class _P(html.parser.HTMLParser):
        def __init__(self):
            super().__init__()
            self.out, self.cur = {}, None

        def handle_starttag(self, tag, attrs):
            if tag == "button":
                self.cur = dict(attrs).get("id")
                self.out[self.cur] = ""

        def handle_data(self, data):
            if self.cur is not None:
                self.out[self.cur] += data

        def handle_endtag(self, tag):
            if tag == "button":
                self.cur = None
    p = _P()
    p.feed(html_text)
    p.close()
    return {k: " ".join(v.split()) for k, v in p.out.items()}


def test_gard_borderoul_nu_mai_e_in_operatiuni_si_sta_langa_nir():
    """pct.23: butonul borderoului stă lângă NIR (Stocuri), cu numele documentului; ruta nu e și în „TVA regimuri speciale”.
    (Partea din `operatiuni_ecran.js` se aplică de sesiunea principală — vezi raportul; până atunci gardul verifică numai butonul.)"""
    fj = io.open(os.path.join(RAD, "static", "js", "ecrane", "firme.js"), encoding="utf-8").read()
    i = fj.index('id="sn-toggle"')
    rand = fj[fj.rindex("<p>", 0, i):fj.index("</p>", i) + len("</p>")]
    # butoanele paragrafului lui „+ NIR nou”, ca elemente HTML (id -> textul lor), nu „șirul apare în rând” (core/test_garzi_pe_text.py)
    assert _butoane(rand).get("s-borderou") == "Borderou de achiziție", rand
