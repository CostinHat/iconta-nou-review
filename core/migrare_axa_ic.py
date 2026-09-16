# -*- coding: utf-8 -*-
"""core/migrare_axa_ic.py — axa bunuri/servicii a unei operatiuni intracomunitare, PE DOCUMENT.

DE CE (R186, decizia lui Costin, 16.09.2026). Ruta dedicata achizitiei IC cerea de la om
`tip: bunuri|servicii`, il valida si il REFUZA daca era altceva — dar valoarea intra doar in textul
descrierii. D300 lua axa din `tip_def_ic = "L" if emisa else "A"`, adica *orice achizitie IC e
„bunuri"* daca n-o reclasifica cineva manual. Masurat pe 15.09.2026: 800 lei servicii IC intrau la
rd.5 (bunuri) in loc de rd.7, iar `R5_1` crestea cu 1.800 = 1.000 bunuri + 800 servicii.

DECIZIA, verbatim: *„axa bunuri/servicii se inregistreaza pe document (coloana pe factura),
inghetata la introducere. Reclasificarea nu e sursa — cheia ei partener-luna nu poate desparti doua
operatiuni din aceeasi luna."*

  - axa_ic  text  NULL  -- 'bunuri' | 'servicii' | NULL

DE CE `NULL` E PERMIS, si nu un implicit „bunuri": pentru facturile ISTORICE nu se stie care era axa,
iar un implicit ar transforma o NECUNOASTERE in afirmatie (interdictia 32: *un necunoscut nu se
rotunjeste la „stiu ca nu"*). Deci trei stari: cele doua valori, plus absenta. Pe absenta se pastreaza
comportamentul de pana acum (implicit + reclasificare) SI se semnaleaza — nu se ghiceste in tacere.

NU SE FACE BACKFILL, deliberat. Prefixul CUI-ului spune TARA, nu axa; nimic din factura veche nu
spune daca a fost bun sau serviciu. *Un backfill ar fi exact rotunjirea pe care coloana o repara.*

Sursa UNICA a DDL-ului = oglinda in `tenant_template.sql` (CREATE TABLE facturi). Idempotent
(ADD COLUMN IF NOT EXISTS). Se aplica: tenanti NOI prin template; EXISTENTI prin
`python3 -m core.migrare_axa_ic`.
"""
import sys

from core import db

#: Cele doua valori. Lista e aici, nu in fiecare modul care o citeste: a doua definitie a aceluiasi
#: nomenclator e inceputul unei divergente.
AXE = ("bunuri", "servicii")

_DDL = [
    'ALTER TABLE "{s}".facturi ADD COLUMN IF NOT EXISTS axa_ic text;',
    # Poarta e in BAZA, nu doar in cod: o valoare din afara nomenclatorului nu poate intra nici prin
    # `psql`. `NULL` rimane permis — e a treia stare, nu o scapare.
    'ALTER TABLE "{s}".facturi DROP CONSTRAINT IF EXISTS facturi_axa_ic_chk;',
    'ALTER TABLE "{s}".facturi ADD CONSTRAINT facturi_axa_ic_chk '
    "CHECK (axa_ic IS NULL OR axa_ic IN ('bunuri','servicii'));",
]

_COLOANE = ("axa_ic",)


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    with conn.cursor() as cur:
        for ddl in _DDL:
            cur.execute(ddl.format(s=schema))


def verifica(conn, schema):
    """Coloana EXISTA si poarta constrangerea — amandoua, nu doar prima."""
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema=%s "
                    "AND table_name='facturi' AND column_name = ANY(%s)", (schema, list(_COLOANE)))
        col = cur.fetchone()[0] == len(_COLOANE)
        cur.execute("SELECT count(*) FROM pg_constraint WHERE conname = 'facturi_axa_ic_chk' "
                    "AND connamespace = %s::regnamespace", (schema,))
        chk = cur.fetchone()[0] == 1
    return col and chk


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT schema_name FROM information_schema.schemata "
                        "WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY schema_name")
            scheme = [r[0] for r in cur.fetchall()]
    ok, esec = 0, []
    for s in scheme:
        try:
            with db.get_conn() as conn:
                aplica(conn, s)
                conn.commit()
            with db.get_conn() as conn:
                if verifica(conn, s):
                    ok += 1
                else:
                    esec.append((s, "verificarea a picat dupa aplicare"))
        except Exception as e:  # noqa: BLE001
            esec.append((s, "%s: %s" % (type(e).__name__, e)))
    print("scheme: %d · aplicat+verificat: %d · esec: %d" % (len(scheme), ok, len(esec)))
    for s, m in esec:
        print("  ESEC %s — %s" % (s, m))
    return 1 if esec else 0


if __name__ == "__main__":
    sys.exit(_main())
