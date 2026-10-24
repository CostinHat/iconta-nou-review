# -*- coding: utf-8 -*-
"""Lotul 12, pachetul triaj3 — căderea e2e `test_def_475_nirul_cu_doua_linii_ale_aceluiasi_articol_nou_face_un_singur_articol`
(`POST /tenants/<id>/stocuri/nir` -> 422, „NIR salvat” nu apare).

CEREREA FORMULARULUI, refăcută câmp cu câmp din `static/js/ecrane/firme.js` (`ecranStocuri`, handlerul `#sn-salveaza`): la stocul la cost
(cantitativ-valoric) fiecare linie pleacă `{denumire, cantitate, pret_achizitie, articol_id, articol_nou, cota_tva}` — fără `um`, fără
`pret_vanzare` —, iar antetul `{numar, data, furnizor, cui, transport: 0, taxe: 0, cont_transport: null, cota_tva_transport: null,
factura_sosita, cont_taxe: "446", linii}`. Ecranul pornește cu UN rând de articol (`liniiNir = [{}]` înainte de `deseneaza()`), iar
„+ articol” adaugă un rând gol (`linieNouaNir()`): pașii „+ articol” înaintea fiecărei linii lasă un al treilea rând gol, pe care serverul
îl refuză lângă câmpurile lui — corect (cap.24 regula 2: lista trimisă = lista randată, nimic nu se filtrează tacit).

Concluzia triajului: testul e2e era greșit (un „+ articol” în plus), nu aplicația — cererea cu cele două rânduri completate se salvează,
cu un singur articol (reparația 475, `stocuri_cv_api.articol_pentru_intrare`), și fără `um` pe linie. Testele de mai jos țin amândouă
jumătățile pe cererea EXACTĂ a formularului (testul vechi din `test_lot12_firme2_articole.py` trimitea și `um`, pe care ecranul nu-l are).
Temei: N/A — regulă de produs (CLAUDE.md §9), nu fiscală. Schemă efemeră din template, ștearsă la ieșire.
"""
import io
import os

import pytest

from core import db as _db, stocuri_api as _s, tenant_provisioning as _tprov

SCH = "efemer_l12_triaj3_nir"
_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


db_necesar = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


@pytest.fixture()
def conn_cv():
    _db.init_pool()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tprov.parametrizeaza_template(io.open(os.path.join(_RAD, "tenant_template.sql"), encoding="utf-8").read(), SCH))
            cur.execute("SET LOCAL search_path TO %s, public" % SCH)
            # CUI 14399840 (DANTE INTERNATIONAL SA) — cifra de control verificată
            cur.execute("INSERT INTO firma_profil (id, nume, cui, platitor_tva, forma_juridica, capital_subscris, metoda_stoc) "
                        "VALUES (1, 'F2 SRL', '14399840', true, 'SRL', 200, 'cantitativ_valoric')")
        c.commit()
    with _db.get_conn(SCH) as c:
        yield c
        c.rollback()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        c.commit()


def _linie_formular(denumire, cantitate, pret):
    """Rândul „+ articol nou…” completat, exact cum îl trimite `firme.js` la cost (`nr()` -> float, `cota_tva` -> Number)."""
    return {"denumire": denumire, "cantitate": cantitate, "pret_achizitie": pret, "articol_id": None, "articol_nou": True, "cota_tva": 11}


#: rândul gol adăugat de „+ articol” și necompletat (`linieNouaNir()` -> corpul trimis)
RAND_GOL = {"denumire": "", "cantitate": None, "pret_achizitie": None, "articol_id": None, "articol_nou": False, "cota_tva": None}


def _corp_formular(linii):
    return {"numar": "E2E-475-1", "data": "2026-10-20", "furnizor": "DANTE INTERNATIONAL SA", "cui": "14399840", "transport": 0,
            "taxe": 0, "cont_transport": None, "cota_tva_transport": None, "factura_sosita": False, "cont_taxe": "446", "linii": linii}


def _articole(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT a.denumire, COALESCE((SELECT sum(m.cantitate) FROM miscari_stoc m WHERE m.articol_id = a.id), 0) "
                    "FROM articole a ORDER BY a.id")
        return [(d, str(q)) for d, q in cur.fetchall()]


@db_necesar
def test_475_cererea_formularului_cu_doua_randuri_completate_se_salveaza_cu_un_singur_articol(conn_cv):
    """Pașii contabilului (un rând la deschidere, „+ articol” o dată): „Grâu E2E 475” 5 la 2 lei și „grau e2e 475” 3 la 2,50, 11%, fără
    UM pe ecran -> NIR salvat, un articol „Grâu E2E 475” cu 8. Cererea e cea a formularului, nu una construită pe gustul serverului."""
    r = _s.adauga_nir(conn_cv, SCH, _corp_formular([_linie_formular("Grâu E2E 475", 5, 2), _linie_formular("grau e2e 475", 3, 2.5)]),
                      cere_decizia=True)
    assert "eroare" not in r, r
    assert _articole(conn_cv) == [("Grâu E2E 475", "8.000")]


@db_necesar
def test_475_randul_gol_lasat_de_plus_articol_se_refuza_langa_campurile_lui(conn_cv):
    """Căderea e2e, refăcută: două rânduri completate + rândul gol lăsat de un „+ articol” în plus -> refuz (422 pe rută, `DateInvalide`),
    cu fiecare câmp al rândului 3 numit — nu un NIR salvat tacit fără el și nu un refuz pe rândurile completate."""
    r = _s.adauga_nir(conn_cv, SCH, _corp_formular([_linie_formular("Grâu E2E 475", 5, 2), _linie_formular("grau e2e 475", 3, 2.5),
                                                    RAND_GOL]), cere_decizia=True)
    assert r["eroare"] == ("Completează articolele: Articolul 3: denumirea; Articolul 3: cantitatea; Articolul 3: prețul de achiziție "
                           "Alege cota de TVA la «»."), r
    assert sorted(x["camp"] for x in r["erori_campuri"]) == ["nir-l2-cantitate", "nir-l2-cota_tva", "nir-l2-denumire",
                                                              "nir-l2-pret_achizitie"], r
    assert _articole(conn_cv) == []
