# -*- coding: utf-8 -*-
"""GARD [R43, 06.09.2026]: confirmarea unei plăți atinge O SINGURĂ firmă, iar plata simulată o spune.

**Ce s-a reparat.** `POST /public/plata/{ref}/confirma` — rută **neautentificată** — citea
`SELECT schema_name FROM public.tenants` și încerca un `UPDATE` în **fiecare** schemă, până la prima
potrivire. Nu era o scurgere (răspunsul e doar `{ok}`, iar `ref` are 128 de biți), dar nu exista
**nicio barieră structurală** între firme: două referințe identice ar fi însemnat scriere în firma
greșită, iar „improbabil" nu e o izolare, e un pariu.

**Ce apără gardul, în ordinea în care contează:**
  1. `public.plata_referinte.ref` e **PRIMARY KEY** — coliziunea între firme e imposibilă *prin
     construcție*. Se cere constrângerea, nu comportamentul: un test care doar încearcă două
     inserări ar trece și pe un index obișnuit, șters din greșeală;
  2. o referință **neînregistrată** nu se confirmă — nici măcar dacă valoarea `plata_ref` există pe
     o factură. Ăsta e testul care deosebește codul nou de cel vechi: vechiul o găsea plimbând
     schemele, noul cere perechea din `public`;
  3. confirmarea atinge firma ei, iar cealaltă rămâne **neatinsă**, verificat pe amândouă;
  4. plata pe calea `mock` poartă `plata_confirmata_de='mock'` — *simulare*, nu bani intrați.

**CE NU APĂRĂ, declarat:** că plata a avut loc. Confirmarea tot nu vine semnată de la un procesator
real — partea EXTERNĂ a lui R43, care rămâne deschisă.
"""
import os
import sys

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAD not in sys.path:
    sys.path.insert(0, _RAD)

from core import db as _db  # noqa: E402
from core import plati as _pl  # noqa: E402
from core import tenant_provisioning as _tp  # noqa: E402
from core import migrare_plata_referinte as _mig  # noqa: E402

A, B = "ztest_plata_a", "ztest_plata_b"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:  # noqa: BLE001
        return False


def _sablon():
    return open(os.path.join(_RAD, "tenant_template.sql"), encoding="utf-8").read()


def _seed(conn, schema, numar):
    """Schemă efemeră + o factură EMISĂ, neplătită."""
    with conn.cursor() as cur:
        cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % schema)
        cur.execute(_tp.parametrizeaza_template(_sablon(), schema))
        cur.execute(f"""INSERT INTO {schema}.facturi
            (numar, data_emitere, directie, status, total, moneda, tert_nume)
            VALUES (%s, '2026-09-01', 'emisa', 'emisa', 100, 'RON', 'Client proba')
            RETURNING id""", (numar,))
        fid = cur.fetchone()[0]
    conn.commit()
    return fid


@pytest.fixture(scope="module")
def doua_firme():
    if not _db_ok():
        pytest.skip("DB indisponibil")
    with _db.get_conn() as conn:
        fa, fb = _seed(conn, A, "PROBA-A-1"), _seed(conn, B, "PROBA-B-1")
        _mig.aplica(conn, scheme=[A, B])
        with conn.cursor() as cur:
            cur.execute("DELETE FROM public.plata_referinte WHERE schema_name IN (%s, %s)", (A, B))
        conn.commit()
    yield {"a": (A, fa), "b": (B, fb)}
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM public.plata_referinte WHERE schema_name IN (%s, %s)", (A, B))
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % A)
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % B)
        conn.commit()


def _stare(conn, schema, fid):
    with conn.cursor() as cur:
        cur.execute(f"SELECT platita_la, plata_confirmata_de FROM {schema}.facturi WHERE id=%s", (fid,))
        return cur.fetchone()


# ── 1. STRUCTURA: coliziunea e imposibilă, nu improbabilă ──────────────────────────────────────

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_referinta_e_CHEIE_PRIMARA_pe_tot_portofoliul():
    """Se cere CONSTRÂNGEREA, nu comportamentul. Un test care doar încearcă două inserări ar trece
    și pe un index obișnuit — iar un index nu e o barieră, e o optimizare."""
    with _db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("""SELECT c.contype
                       FROM pg_constraint c
                       JOIN pg_class t ON t.oid = c.conrelid
                       JOIN pg_namespace n ON n.oid = t.relnamespace
                       WHERE n.nspname='public' AND t.relname='plata_referinte' AND c.contype='p'""")
        assert cur.fetchone(), "public.plata_referinte n-are cheie primară pe `ref`"


# ── 2. CE DEOSEBEȘTE CODUL NOU DE CEL VECHI ────────────────────────────────────────────────────

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_o_referinta_NEINREGISTRATA_nu_se_confirma(doua_firme):
    """Miezul. Codul vechi găsea referința plimbând toate schemele; cel nou pleacă de la perechea
    din `public`. Aici `plata_ref` EXISTĂ pe factură, dar perechea NU — deci confirmarea trebuie să
    nu aibă drum."""
    sch, fid = doua_firme["a"]
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(f"UPDATE {sch}.facturi SET plata_ref=%s WHERE id=%s", ("pl_orfan_xyz", fid))
        conn.commit()
        assert _pl.firma_pentru_ref(conn, "pl_orfan_xyz") is None
        assert _stare(conn, sch, fid)[0] is None, "factura n-avea voie să fie deja plătită"


# ── 3. COMPORTAMENT: o firmă atinsă, cealaltă nu ───────────────────────────────────────────────

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_confirmarea_atinge_o_singura_firma_si_poarta_marca(doua_firme):
    scha, fa = doua_firme["a"]
    schb, fb = doua_firme["b"]
    with _db.get_conn() as conn:
        r = _pl.genereaza_link(conn, scha, fa, "http://x", tenant_id=1)
        assert r.get("ref"), r
        gasit = _pl.firma_pentru_ref(conn, r["ref"])
        assert gasit and gasit[1] == scha, gasit
        _pl.confirma_plata(conn, gasit[1], r["ref"])

        plat_a, cine_a = _stare(conn, scha, fa)
        plat_b, cine_b = _stare(conn, schb, fb)
    assert plat_a is not None, "firma emitentă n-a fost marcată"
    assert cine_a == "mock", "plata simulată nu poartă marca: %r" % cine_a
    assert plat_b is None and cine_b is None, "cealaltă firmă a fost atinsă — izolarea a căzut"


# ── 4. CALIBRARE ÎN CEALALTĂ DIRECȚIE ──────────────────────────────────────────────────────────

@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_un_link_fara_firma_se_REFUZA_nu_se_scrie(doua_firme):
    """Un `ref` scris pe factură fără perechea lui ar fi un link care nu se poate confirma
    niciodată. Se refuză, nu se scrie pe jumătate."""
    schb, fb = doua_firme["b"]
    with _db.get_conn() as conn:
        r = _pl.genereaza_link(conn, schb, fb, "http://x")     # fără tenant_id
        assert r.get("eroare"), r
        with conn.cursor() as cur:
            cur.execute(f"SELECT plata_ref, link_plata FROM {schb}.facturi WHERE id=%s", (fb,))
            ref, link = cur.fetchone()
    assert ref is None and link is None, "s-a scris un link neconfirmabil: %r / %r" % (ref, link)
