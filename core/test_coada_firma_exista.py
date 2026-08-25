# -*- coding: utf-8 -*-
"""GARD [R44]: o declarație nu poate intra în coadă legată de o firmă care nu există.

Măsurat 25.08.2026: **1 din 3** elemente din coadă avea `tenant_id = 13245`, care nu e în
`public.tenants` și n-are schemă. Nimic n-o semnala — nici ecranul, nici vreo verificare.

De ce refuzul stă în `adauga_in_coada` și nu ca cheie străină: `declaratii_coada` e o tabelă
partajată, iar firmele trăiesc și ca scheme; o cheie străină ar lega două modele de date
diferite. Poarta de intrare în coadă e una singură, deci acolo se pune.

**Testat pe COMPORTAMENT, nu pe sursă.** Prima formă a acestui fișier căuta șiruri în codul
lui `adauga_in_coada` (`"public.tenants" in ...`) — adică exact forma pe care METODA §23 o
interzice, și pe care `test_garzi_pe_text` a prins-o în chiar commitul ei. Aici se **cheamă**
funcția cu o firmă inexistentă și se verifică ce răspunde și ce a scris. Un refuz mutat după
`INSERT` pică proba a doua: numărătoarea s-ar schimba.
"""
import os

import pytest

from core import coada_api, db

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Orfani cunoscuți la 25.08.2026, pe commitul care aduce gardul. Scade la ștergere; nu crește.
_ORFANI_CLICHET = 1
# id care nu poate exista: `public.tenants.id` e serial, iar aici e deliberat în afara oricărei
# secvențe plauzibile. Nu se inserează nimic cu el — tocmai asta se probează.
_FIRMA_INEXISTENTA = 999_000_777


@pytest.fixture(scope="module")
def conn():
    try:
        db.init_pool()
        with db.get_conn() as c:
            yield c
    except Exception as ex:                                   # pragma: no cover
        pytest.skip("fără bază de date: %s" % str(ex)[:80])


def _nr_coada(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM public.declaratii_coada")   # fixtura-sintetica-ok: doar NUMĂRĂ, nu scrie
        return cur.fetchone()[0]


def test_o_firma_inexistenta_e_REFUZATA(conn):
    r = coada_api.adauga_in_coada(
        conn, cabinet_id=1968, tenant_id=_FIRMA_INEXISTENTA, tip="d300", an=2099,
        payload={"xml": "<x/>"}, creat_de="test", luna=1)
    assert r.get("ok") is False, "o firmă inexistentă a fost ACCEPTATĂ în coadă: %r" % r
    assert r.get("cod") == "FIRMA_INEXISTENTA", "cod greșit: %r" % r.get("cod")
    assert r.get("mesaj"), "refuzul nu spune omului nimic"


def test_refuzul_NU_scrie_nimic(conn):
    """Proba că refuzul e ÎNAINTEA inserării, nu după. Unul scris după n-ar refuza — ar curăța,
    iar între cele două momente rândul ar exista."""
    inainte = _nr_coada(conn)
    coada_api.adauga_in_coada(
        conn, cabinet_id=1968, tenant_id=_FIRMA_INEXISTENTA, tip="d300", an=2099,
        payload={"xml": "<x/>"}, creat_de="test", luna=2)
    assert _nr_coada(conn) == inainte, (
        "coada a crescut deși firma nu există — refuzul e după INSERT, nu înaintea lui")


def test_calibrare_o_firma_REALA_nu_e_refuzata_din_motivul_asta(conn):
    """Direcția cealaltă (METODA §22): garda trebuie să refuze firma inexistentă **și să nu
    refuze** una reală. Fără proba asta, un `return FIRMA_INEXISTENTA` necondiționat ar trece
    testele de mai sus și ar bloca toată coada."""
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM public.tenants ORDER BY id LIMIT 1")
        r = cur.fetchone()
    if not r:
        pytest.skip("instalarea n-are nicio firmă")
    rez = coada_api.adauga_in_coada(
        conn, cabinet_id=1968, tenant_id=r[0], tip="d300", an=2099,
        payload={"xml": "<x/>"}, creat_de="test", luna=3)
    # Poate eșua din alt motiv (deja în coadă) — dar NU din ăsta.
    assert rez.get("cod") != "FIRMA_INEXISTENTA", (
        "o firmă REALĂ (#%s) a fost refuzată ca inexistentă — garda refuză tot" % r[0])
    if rez.get("ok"):
        with conn.cursor() as cur:
            cur.execute("DELETE FROM public.declaratii_coada WHERE id = %s", (rez["coada_id"],))
        conn.commit()


def test_orfanii_din_coada_nu_cresc(conn):
    """Clichet pe date. Rândul orfan de azi rămâne până se decide ce se face cu el; ce nu are
    voie e să apară al doilea."""
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM public.declaratii_coada c WHERE NOT EXISTS "
                    "(SELECT 1 FROM public.tenants t WHERE t.id = c.tenant_id)")
        n = cur.fetchone()[0]
    assert n <= _ORFANI_CLICHET, (
        "elemente din coadă legate de firme inexistente: %d (clichet %d). Poarta de intrare "
        "le refuză de la R44 — un orfan NOU înseamnă că a intrat pe altă cale."
        % (n, _ORFANI_CLICHET))
