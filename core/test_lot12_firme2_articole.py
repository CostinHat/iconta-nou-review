# -*- coding: utf-8 -*-
"""Lotul 12, pachetul firme2 — 475: „Stocuri: Același articol «grau» de două ori în stoc.”

CLASA (articole dublate): orice drum care scrie un articol nou în nomenclatorul de stoc. Căutare:
`grep -rniE "insert into[^;]{0,40}articole" --include=*.py core scripts main.py` — trei locuri înainte de reparație:
`stocuri_cv_api.intrare` (factura primită, intrarea manuală, borderoul), `stocuri_api.adauga_nir` (NIR-ul la cost) și
`articole_import_api` (importul „Articole și stoc inițial”). Fiecare hotăra singur dacă denumirea e nouă; două linii cu aceeași marfă pe
aceeași factură primită sau pe același NIR creau două articole. Acum un singur loc scrie articole (`stocuri_cv_api.articol_pentru_intrare`),
iar datele existente (F1: „grau” nr. 5 și nr. 6) le unește `core/migrare_articole_dublate.py`, numai unde unirea nu schimbă nicio sumă.
Temei: N/A — regulă de produs (CLAUDE.md §9), nu fiscală. Schemă efemeră din template, ștearsă la ieșire.
"""
import glob
import io
import os
import re

import pytest

from core import db as _db, stocuri_api as _s, stocuri_cv_api as _cv, tenant_provisioning as _tprov

SCH = "efemer_l12_firme2_art"
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
                        "VALUES (1, 'F1 SRL', '14399840', true, 'SRL', 200, 'cantitativ_valoric')")
        c.commit()
    with _db.get_conn(SCH) as c:
        yield c
        c.rollback()   # urmele în `public.audit_log` ale migrării nu rămân
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        c.commit()


def _articole(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT a.id, a.denumire, a.um, COALESCE((SELECT sum(m.cantitate) FROM miscari_stoc m WHERE m.articol_id = a.id), 0) "
                    "FROM articole a ORDER BY a.id")
        return [(i, d, u, str(q)) for i, d, u, q in cur.fetchall()]


# ── gard structural ────────────────────────────────────────────────────────────────────────────────────────────────────────────
_RE_INSERT = re.compile(r"insert\s+into\s+[^\s(;]*\barticole\s*\(", re.I)


def test_475_un_singur_loc_scrie_articole_noi():
    """Gardul clasei: în tot codul aplicației (fără teste și migrări) un singur `INSERT INTO … articole (`, în
    `stocuri_cv_api.articol_pentru_intrare`, care caută întâi articolul cu aceeași cheie de denumire. Un drum nou care și-ar scrie singur
    articolul (și ar putea dubla „grau”) pică aici. MUTAȚIE: `INSERT INTO articole` pus la loc în `stocuri_api.adauga_nir` -> pică."""
    gasite = []
    for f in sorted(glob.glob(os.path.join(_RAD, "core", "*.py"))) + [os.path.join(_RAD, "main.py")]:
        b = os.path.basename(f)
        if b.startswith("test_") or b.startswith("migrare_"):
            continue
        text = io.open(f, encoding="utf-8").read()
        for m in _RE_INSERT.finditer(text):
            inainte = text[:m.start()]
            functia = re.findall(r"^def (\w+)\(", inainte, re.M)
            gasite.append((b, functia[-1] if functia else None))
    assert gasite == [("stocuri_cv_api.py", "articol_pentru_intrare")], gasite


# ── drumurile ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────
@db_necesar
def test_475_factura_primita_cu_doua_linii_din_aceeasi_marfa_face_un_singur_articol(conn_cv):
    """Factura primită de marfă cu două linii „Grâu” (10 kg) și „grau” (20 kg) — aceeași marfă, scrisă diferit — intră în stoc pe UN
    articol, cu 30 kg. Înainte: două articole (amândouă liniile vedeau „nu există” înainte de prima creare)."""
    with conn_cv.cursor() as cur:
        cur.execute("INSERT INTO facturi (serie, numar, data_emitere, directie, total, tva, status, tert_nume, tert_cui) VALUES "
                    "('FZ', '475', '2026-10-20', 'primita', 363, 63, 'contata', 'DANTE INTERNATIONAL SA', '14399840') RETURNING id")
        fid = cur.fetchone()[0]
        for den, q in (("Grâu", 10), ("grau", 20)):
            cur.execute("INSERT INTO factura_linii (factura_id, descriere, cantitate, pret_unitar, cota_tva, cont_cheltuiala, um) "
                        "VALUES (%s, %s, %s, 10, 21, '371', 'kg')", (fid, den, q))
    r = _cv.intrare_din_factura(conn_cv, SCH, fid, "371", "2026-10-20")
    assert r["stare"] == "intrat" and r["linii"] == 2, r
    assert [x[1:] for x in _articole(conn_cv)] == [("Grâu", "kg", "30.000")]


@db_necesar
def test_475_nirul_cu_doua_linii_ale_aceluiasi_articol_nou_face_un_singur_articol(conn_cv):
    """NIR la cost (Stocuri -> NIR, `stocuri_api.adauga_nir`) cu două linii „articol nou” „grau” (5 kg la 2 lei, 3 kg la 2,50 lei):
    un singur articol „grau”, 8 kg; fiecare linie își păstrează costul. Înainte: două articole „grau”."""
    linie = {"denumire": "grau", "articol_nou": True, "cota_tva": 21, "um": "kg"}
    r = _s.adauga_nir(conn_cv, SCH, {"numar": "475", "data": "2026-10-20", "furnizor": "DANTE INTERNATIONAL SA", "cui": "14399840",
                                     "linii": [{**linie, "cantitate": 5, "pret_achizitie": 2}, {**linie, "cantitate": 3, "pret_achizitie": 2.5}],
                                     "factura_sosita": False}, cere_decizia=True)
    assert "eroare" not in r, r
    (aid, den, um, q), = _articole(conn_cv)
    assert (den, um, q) == ("grau", "kg", "8.000")
    with conn_cv.cursor() as cur:
        cur.execute("SELECT valoare FROM miscari_stoc WHERE articol_id = %s ORDER BY id", (aid,))
        assert [str(v) for v, in cur.fetchall()] == ["10.00", "7.50"]


@db_necesar
def test_475_intrarea_fara_articol_ales_ia_articolul_existent(conn_cv):
    """`stocuri_cv_api.intrare` fără `articol_id` (drumul facturii primite și al borderoului): o denumire care e deja a unui articol
    („GRÂU ” față de „grau”) nu mai creează al doilea."""
    a = _cv.intrare(conn_cv, SCH, {"denumire": "grau", "um": "kg", "cantitate": "2", "pret_unitar": "1", "data": "2026-10-20"})
    b = _cv.intrare(conn_cv, SCH, {"denumire": "  GRÂU ", "um": "kg", "cantitate": "3", "pret_unitar": "1", "data": "2026-10-21"})
    assert a["articol_id"] == b["articol_id"]
    assert _articole(conn_cv) == [(a["articol_id"], "grau", "kg", "5.000")]


# ── datele existente: migrarea ─────────────────────────────────────────────────────────────────────────────────────────────────
def _articol(cur, den, um="kg", cont_stoc="371"):
    cur.execute("INSERT INTO articole (denumire, um, cont_stoc) VALUES (%s, %s, %s) RETURNING id", (den, um, cont_stoc))
    return cur.fetchone()[0]


def _miscare(cur, aid, tip, q, data="2026-10-20", doc="BA-2"):
    cur.execute("INSERT INTO miscari_stoc (articol_id, data, tip, cantitate, pret_unitar, valoare, document) VALUES (%s,%s,%s,%s,1,%s,%s) "
                "RETURNING id", (aid, data, tip, q, q, doc))
    return cur.fetchone()[0]


@db_necesar
def test_475_migrarea_uneste_dublurile_create_tacit(conn_cv):
    """F1 înainte de reparație: „grau” nr. 5 (200 kg, BA-2) și „grau” nr. 6 (10 kg, BA-3), create tacit de borderou. Migrarea le unește în
    cel mai vechi: un articol, 210 kg, cele două intrări cu valorile lor neschimbate, urma în `public.audit_log`. A doua rulare: nimic."""
    from core import migrare_articole_dublate as mig
    with conn_cv.cursor() as cur:
        a5, a6 = _articol(cur, "grau"), _articol(cur, "grau")
        m5, m6 = _miscare(cur, a5, "intrare", 200), _miscare(cur, a6, "intrare", 10, "2026-10-21", "BA-3")
    assert mig.verifica(conn_cv, SCH) is False
    r = mig.aplica(conn_cv, SCH)
    assert r == {"unite": [(a5, [a6], 1)], "neunite": []}, r
    assert _articole(conn_cv) == [(a5, "grau", "kg", "210.000")]
    with conn_cv.cursor() as cur:
        cur.execute("SELECT id, articol_id, valoare FROM miscari_stoc ORDER BY id")
        assert [(i, a, str(v)) for i, a, v in cur.fetchall()] == [(m5, a5, "200.00"), (m6, a5, "10.00")]
        cur.execute("SELECT detalii->'unite'->0->>'id', detalii->'randuri_mutate'->'miscari_stoc' FROM public.audit_log "
                    "WHERE actiune = 'unire_articole' AND detalii->>'schema' = %s", (SCH,))
        assert cur.fetchall() == [(str(a6), [m6])]
    assert mig.verifica(conn_cv, SCH) is True
    assert mig.aplica(conn_cv, SCH) == {"unite": [], "neunite": []}


@db_necesar
def test_475_migrarea_nu_uneste_ce_ar_schimba_o_suma_sau_ar_amesteca_doua_lucruri(conn_cv):
    """Nu se unesc: (a) dublurile cu o ieșire (evaluată la CMP-ul articolului ei — unite, fișa ar arăta alt cost decât nota); (b) aceeași
    denumire în alte unități de măsură (kg / sac); (c) o lună blocată (regula de fond a bazei refuză, grupul se lasă și se numește).
    Fiecare se numește, cu motivul; nimic nu se schimbă."""
    from core import migrare_articole_dublate as mig
    with conn_cv.cursor() as cur:
        o1, o2 = _articol(cur, "orz"), _articol(cur, "Orz")
        _miscare(cur, o1, "intrare", 50)
        _miscare(cur, o2, "intrare", 10)
        _miscare(cur, o2, "iesire", 4)
        s1, s2 = _articol(cur, "secara", "kg"), _articol(cur, "secară", "sac")
        _miscare(cur, s1, "intrare", 5)
        p1, p2 = _articol(cur, "porumb"), _articol(cur, "porumb")
        _miscare(cur, p1, "intrare", 5, "2026-08-10")
        _miscare(cur, p2, "intrare", 6, "2026-08-11")
        cur.execute("INSERT INTO perioade_blocate (an, luna) VALUES (2026, 8)")
    inainte = _articole(conn_cv)
    r = mig.aplica(conn_cv, SCH)
    assert r["unite"] == [], r
    motive = {den: (ids, m) for den, ids, m in r["neunite"]}
    assert set(motive) == {"orz", "secara", "porumb"}, motive
    assert motive["orz"][0] == [o1, o2] and motive["orz"][1].split(", ")[0] == "are ieșiri din stoc", motive["orz"]
    assert motive["secara"][0] == [s1, s2] and _motiv(motive["secara"][1]) == ("unități de măsură diferite", "kg / sac"), motive["secara"]
    assert motive["porumb"][0] == [p1, p2] and motive["porumb"][1].startswith("baza a refuzat unirea: PERIOADA_BLOCATA"), motive["porumb"]
    assert _articole(conn_cv) == inainte


def _motiv(m):
    """(felul motivului, ce stă în paranteza de la capăt | None) — motivul se citește pe structura lui, nu prin „șirul apare undeva”."""
    return re.fullmatch(r"(.*?)(?: \((.*)\))?", m).groups()


def test_475_motivul_neunirii_e_pur():
    from core import migrare_articole_dublate as mig
    a = {"id": 1, "denumire": "grau", "um": "kg", "cont_stoc": "371", "cont_cheltuiala": "607", "barcode": None, "nivel_minim": None,
         "iesiri": 0}
    assert mig.motiv_neunibil([a, {**a, "id": 2}]) is None
    assert _motiv(mig.motiv_neunibil([a, {**a, "id": 2, "cont_stoc": "301"}])) == ("conturi diferite", "371/607 față de 301/607")
    assert _motiv(mig.motiv_neunibil([{**a, "barcode": "1"}, {**a, "id": 2, "barcode": "2"}])) == ("articolele au coduri de bare diferite",
                                                                                                  None)
