# -*- coding: utf-8 -*-
"""core/test_tip_decont_lung.py — GARD: periodicitatea decont TVA ajunge la UI in forma LUNGA.

BUG (audit tenant_005, 17.08.2026): seed-ul (date_test/seed/transa2_coerenta_tva.py) scrie coduri
legacy 'L'/'T' in firma_profil.tip_decont (12 din 20 tenanti). UI-ul (migrare.js vector, date_firma.js)
compara pe forma LUNGA (decont==='lunar'/'trimestrial') -> pt 'L'/'T' NICIUN buton/optiune nu se
selecteaza -> periodicitatea apare NESELECTATA desi e salvata. Motoarele fiscale erau deja imune
(perioada_tva_tip). Fix: normalizare la GRANITA UI (common.tip_decont_lung) in citeste / citeste_date /
portal_api.date_firma.

Gard: (1) contractul primitivei; (2) integrare - un tenant cu cod legacy, citit prin oricare din cele
3 granite UI, intoarce forma lunga, NICIODATA litera bruta. RED-probat: scot normalizarea din citeste
-> testul de integrare pica ('T' in loc de 'trimestrial').
"""
import pytest

from core.common import tip_decont_lung, DECONT_LUNG

_LUNGI = set(DECONT_LUNG.values())   # {'lunar','trimestrial','semestrial','anual'}
_LEGACY = set(DECONT_LUNG.keys())    # {'L','T','S','A'}


def test_primitiva_contract():
    # legacy litera -> forma lunga
    assert tip_decont_lung("L") == "lunar"
    assert tip_decont_lung("T") == "trimestrial"
    assert tip_decont_lung("S") == "semestrial"
    assert tip_decont_lung("A") == "anual"
    # forma lunga -> ea insasi (idempotent)
    assert tip_decont_lung("lunar") == "lunar"
    assert tip_decont_lung("trimestrial") == "trimestrial"
    # gol / necunoscut -> None (FARA default tacit, DEFAULT_FISCAL_TACIT)
    assert tip_decont_lung(None) is None
    assert tip_decont_lung("") is None
    assert tip_decont_lung("xyz") is None
    # NICIODATA nu intoarce litera bruta (semnatura bug-ului)
    for x in ["L", "T", "S", "A", "lunar", "trimestrial", None, "", "zzz"]:
        assert tip_decont_lung(x) not in _LEGACY


def _db_ok():
    try:
        from core import db
        db.init_pool(); 
        with db.get_conn() as c:
            with c.cursor() as cur:
                cur.execute("SELECT 1")
        return True
    except Exception:
        return False


def _tenant_legacy():
    """Schema unui tenant cu tip_decont in {'L','T','S','A'} (seed legacy), sau None."""
    from core import db
    with db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("SELECT schema_name FROM public.tenants ORDER BY id")
            schemas = [r[0] for r in cur.fetchall()]
    for sch in schemas:
        try:
            with db.get_conn(sch) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT tip_decont FROM firma_profil WHERE id=1")
                    r = cur.fetchone()
            if r and r[0] in _LEGACY:
                return sch, r[0]
        except Exception:
            continue
    return None, None


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_granite_ui_normalizeaza_legacy():
    """Cele 3 granite UI (vector citeste, date_firma citeste_date, portal date_firma) intorc forma
    lunga pt un tenant cu cod legacy - niciodata litera bruta."""
    from core import db, vector_fiscal_api, portal_api
    sch, raw = _tenant_legacy()
    if not sch:
        pytest.skip("niciun tenant cu tip_decont legacy in DB (seed absent)")
    # /vector (citeste) alimenteaza AMBELE ecrane cu vector: formularul de migrare SI Date firma
    # (date_firma.js citeste vectorul din /tenants/{id}/vector, nu din firma-profil/date).
    with db.get_conn(sch) as conn:
        v = vector_fiscal_api.citeste(conn)
    assert v["tip_decont"] in _LUNGI, "citeste (vector) nu a normalizat %r -> %r" % (raw, v["tip_decont"])
    assert v["tip_decont"] not in _LEGACY
    # portalul clientului
    with db.get_conn(sch) as conn:
        pf = portal_api.date_firma(conn, sch)
    assert pf["tip_decont"] in _LUNGI, "portal date_firma nu a normalizat %r" % raw
    assert pf["tip_decont"] not in _LEGACY


def test_formular_vector_incarca_vectorul_salvat():
    """B1: formularVectorFirma (migrare.js) trebuie sa INCARCE vectorul salvat (/tenants/{id}/vector).
    Pe traseul per-firma (meniuMigrarePerFirma) `f` vine doar cu {tenant_id,nume,tip_firma} - fara
    campurile vectorului. Fara acest fetch formularul apare GOL (regim gol, 'Nu' tacit la TVA) si ar
    SUPRASCRIE vectorul la salvare. Clamp anti-regresie pe prezenta fetch-ului."""
    import os
    p = "static/js/ecrane/migrare.js"
    if not os.path.exists(p):
        pytest.skip("migrare.js absent")
    src = open(p, encoding="utf-8").read()
    i = src.index("async function formularVectorFirma")
    j = src.index("async function wizardSolduri", i)
    corp = src[i:j]
    assert "/vector`" in corp and "api.get" in corp, \
        "formularVectorFirma nu mai incarca vectorul salvat (/tenants/{id}/vector) - formularul ar aparea gol"
