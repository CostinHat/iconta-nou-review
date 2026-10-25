# -*- coding: utf-8 -*-
"""Lotul 12, comanda Costin 12.2 (verbatim în DECIZII „Comanda 12.2”), pachetul stoc2 — 450.1 și 628 (partea de date):
  * 450.1 (pct.4): „Borderourile noi sunt corecte, dar Stocuri pe F1 arată tot două rânduri «grau» (200 + 10 kg). Un articol, un rând.”
  * 628 (pct.15): „Stocuri F1: două deschideri consecutive arată liste diferite (4, apoi 6 rânduri); borderourile scriu «buc» la grâu (kg).”

CE E PE F1. Articolele „grau” nr. 5 (200 kg, BA-2) și nr. 6 (10 kg, BA-3), create tacit de borderou înainte de 450; liniile BA-2 / BA-3 pe
„buc”. Reparațiile lotului 12 (475: `core/migrare_articole_dublate.py`; C115: `core/migrare_um_borderou.py`) le acoperă, dar lotul 12 nu
e încă publicat: Costin a retestat producția pe codul lotului 11, deci pe F1 de producție migrările n-au rulat. Pe copia firmelor de test
(migrată: `public.migrari_rulate`, 23.10 / 24.10.2026) F1 are un singur „grau” (210 kg) și liniile BA-2 / BA-3 în „kg”.
Lista din `GET /tenants/{id}/stocuri/articole` (`stocuri_cv_api.articole`) e una pe articol, în ordinea denumirii, fără stare: două cereri
la rând dau aceeași listă — diferența dintre deschideri (628) e a ecranului (`static/js/ecrane/firme.js`, pachetul ui2), nu a datelor.

Testul reface F1 dinainte de reparație pe o schemă efemeră (date din 2099), rulează cele două migrări în ordinea registrului și citește
lista ca ecranul. Temei: N/A — regulă de produs (CLAUDE.md §9: un articol, un rând), nu fiscală. ROLLBACK la final."""
import io
import os

import pytest

from core import db as _db
from core import tenant_provisioning as _tp

SCH = "efemer_l12_stoc2_450"
RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:  # noqa: BLE001
        return False


@pytest.fixture()
def conn():
    if not _db_ok():
        pytest.skip("DB indisponibil")
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tp.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), SCH))
            # CUI 14399840 (DANTE INTERNATIONAL SA) — cifra de control verificată
            cur.execute("INSERT INTO %s.firma_profil (id, nume, cui, metoda_stoc) VALUES (1, 'F1 450 SRL', '14399840', "
                        "'cantitativ_valoric')" % SCH)
            cur.execute("SET LOCAL search_path TO %s, public" % SCH)
        try:
            yield c
        finally:
            c.rollback()   # schema efemeră și urma unirii în `public.audit_log` nu rămân


def _borderou_vechi(cur, numar, data, aid, cant):
    """Borderoul de achiziție scris înainte de 450 / C115: linia „grau” pe „buc”, intrarea în stoc pe articolul creat tacit."""
    cur.execute("INSERT INTO facturi (numar, data_emitere, directie, total, tva, tert_nume, tert_cui, status, tip) VALUES "
                "(%s, %s, 'primita', %s, 0, 'Maria Ionescu', '', 'importata', 'borderou') RETURNING id", (numar, data, cant))
    fid = cur.fetchone()[0]
    cur.execute("INSERT INTO factura_linii (factura_id, descriere, cantitate, pret_unitar, cota_tva, um) VALUES (%s, 'grau', %s, 1, 0, 'buc')",
                (fid, cant))
    cur.execute("INSERT INTO miscari_stoc (articol_id, data, tip, cantitate, pret_unitar, valoare, document, factura_id) VALUES "
                "(%s, %s, 'intrare', %s, 1, %s, %s, %s)", (aid, data, cant, cant, numar, fid))
    return fid


def _lista(conn):
    from core import stocuri_cv_api as cv
    return [(a["denumire"], a["um"], a["stoc"], a["valoare"]) for a in cv.articole(conn, SCH)]


def test_def_450_1_f1_doua_articole_grau_devin_un_rand_de_210_kg_si_borderourile_kg(conn):
    """450.1 + 628 (datele): starea F1 de dinainte — două „grau” (200 + 10 kg), BA-2 / BA-3 pe „buc” — după migrările lotului 12 (cele
    rulate la publicare, în ordinea registrului): Stocuri are UN rând „grau”, kg, 210; liniile BA-2 / BA-3 au „kg”; două citiri la rând ale
    listei dau aceeași listă.
    MUTAȚIE: în `migrare_articole_dublate.grupuri`, `if len(g) > 1` -> `if len(g) > 2` -> două rânduri „grau” -> pică."""
    from core import migrare_articole_dublate as dubl, migrare_um_borderou as um
    with conn.cursor() as cur:
        cur.execute("INSERT INTO articole (denumire, um, cont_stoc, cont_cheltuiala) VALUES ('Marfa A', 'buc', '371', '607'), "
                    "('grau', 'kg', '371', '607'), ('grau', 'kg', '371', '607') RETURNING id")
        _a, a5, a6 = [r[0] for r in cur.fetchall()]
        ba2, ba3 = _borderou_vechi(cur, "BA-2", "2099-10-20", a5, 200), _borderou_vechi(cur, "BA-3", "2099-10-21", a6, 10)
    inainte = _lista(conn)
    assert [x for x in inainte if x[0] == "grau"] == [("grau", "kg", "200.000", "200.00"), ("grau", "kg", "10.000", "10.00")], inainte
    # ordinea registrului (`migrari_registru.DUPA`): amândouă după `migrare_punte_stoc`; între ele nu e nicio dependență
    assert dubl.aplica(conn, SCH)["unite"] == [(a5, [a6], 1)]
    assert um.aplica(conn, SCH) == {"linii": 2, "borderouri": ["BA-2", "BA-3"]}
    dupa = _lista(conn)
    assert dupa == [("grau", "kg", "210.000", "210.00"), ("Marfa A", "buc", "0", "0")], dupa
    assert _lista(conn) == dupa                      # 628: două deschideri la rând, aceeași listă
    with conn.cursor() as cur:
        cur.execute("SELECT f.numar, l.um FROM factura_linii l JOIN facturi f ON f.id = l.factura_id WHERE f.id = ANY(%s) ORDER BY 1",
                    ([ba2, ba3],))
        assert cur.fetchall() == [("BA-2", "kg"), ("BA-3", "kg")]
    assert dubl.verifica(conn, SCH) and um.verifica(conn, SCH)
