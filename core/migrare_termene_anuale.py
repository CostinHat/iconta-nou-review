"""
core/migrare_termene_anuale.py — termenul declarațiilor anuale în coadă (lotul 12, deficiența 493).

DEFECTUL. Până la 493, 29 de tipuri de declarații n-aveau termen de depunere în `core/scadente.py`; coada le punea în `perioada` perioada
de raportare („anul 2025”, `coada_api.coada_adauga`), nu termenul. Acum 12 dintre ele au termenul din textul actului (`scadente._ANUALE`,
`scadente.TEMEI_TERMEN`), deci o declarație generată din nou intră cu termenul („25.06.2026”). Cheia elementului activ din coadă e
(firmă, tip, `perioada`) — indexul `ux_coada_activa` și `coada_api.element_activ` —, deci un element vechi cu „anul 2025” n-ar mai fi
găsit: aceeași declarație ar putea sta de două ori în coadă, iar „De depus” ar arăta-o fără termen.

DATELE EXISTENTE („Orice reparație acoperă și datele existente”, comanda Costin 11.2 pct.3): în `public.declaratii_coada`, rândurile
celor 12 tipuri cu `perioada` = „anul AAAA” primesc termenul calculat de aceeași funcție ca la intrarea în coadă (`scadente.scadenta`),
pe anul din `perioada`. Un rând al cărui termen ar ciocni un element ACTIV deja existent pe același (firmă, tip, termen) se sare și se
numește (nu se alege în locul omului care dintre cele două rămâne). Nu se atinge nimic altceva (payload, stare, XML). Idempotentă.
Rulare: `python -m core.migrari_registru ruleaza [--productie] core/migrare_termene_anuale.py`.
"""
import re

from core import db

_RE_ANUL = re.compile(r"^anul (\d{4})$")
_STARI_INCHISE = ("respinsa", "depusa")   # ca indexul parțial ux_coada_activa (infra/bootstrap_public.sql)


def tipuri():
    from core import scadente
    return sorted(scadente._ANUALE)


def aplica(conn):
    """{"actualizate": n, "sarite": [(id, tip, perioada, motiv)]}."""
    from core import scadente
    rez = {"actualizate": 0, "sarite": []}
    with conn.cursor() as cur:
        cur.execute("SELECT id, tenant_id, tip, perioada, stare FROM public.declaratii_coada WHERE tip = ANY(%s) AND perioada ~ '^anul [0-9]{4}$' "
                    "ORDER BY id", (tipuri(),))
        for cid, tenant_id, tip, perioada, stare in cur.fetchall():
            termen = scadente.scadenta(tip, int(_RE_ANUL.match(perioada).group(1)))
            if stare not in _STARI_INCHISE:
                cur.execute("SELECT id FROM public.declaratii_coada WHERE tenant_id = %s AND tip = %s AND perioada = %s "
                            "AND NOT (stare = ANY(%s)) AND id <> %s", (tenant_id, tip, termen, list(_STARI_INCHISE), cid))
                alt = cur.fetchone()
                if alt:
                    rez["sarite"].append((cid, tip, perioada, "elementul activ %s are deja termenul %s" % (alt[0], termen)))
                    continue
            cur.execute("UPDATE public.declaratii_coada SET perioada = %s WHERE id = %s", (termen, cid))
            rez["actualizate"] += 1
    return rez


def verifica(conn):
    """True dacă niciun rând al celor 12 tipuri nu mai are „anul AAAA” în locul termenului (în afara celor sărite, care se numesc)."""
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM public.declaratii_coada WHERE tip = ANY(%s) AND perioada ~ '^anul [0-9]{4}$'", (tipuri(),))
        return cur.fetchone()[0]


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        rez = aplica(conn)
    with db.get_conn() as conn:
        ramase = verifica(conn)
    print("Termenele declarațiilor anuale în coadă: %d rânduri actualizate; %d rămase cu „anul AAAA”." % (rez["actualizate"], ramase))
    for cid, tip, perioada, motiv in rez["sarite"]:
        print("  sărit: elementul %s (%s, %s): %s" % (cid, tip.upper(), perioada, motiv))
    return ramase == len(rez["sarite"])


if __name__ == "__main__":
    import sys
    sys.exit(0 if _main() else 1)
