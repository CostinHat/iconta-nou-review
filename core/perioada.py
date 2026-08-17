# -*- coding: utf-8 -*-
"""core/perioada.py — starea CONFIRMAT/NECONFIRMAT a unei perioade (an, luna, domeniu). Tipar GENERAL
(DESIGN_SYSTEM.md cap.23): cat timp e NECONFIRMAT, datele perioadei sunt informative si orice calcul din aval
BLOCHEAZA cu blocaj motivat; confirmarea (admin_firma, la inchidere) le face autoritative. Revine la inchiderea
lunii contabile si la confirmarea inventarului - aceeasi regula, nu una paralela per modul.

Reversibilitate: INAINTE de depunere, o modificare a datelor de-confirma AUTOMAT (deconfirma); DUPA depunere,
modificarea se blocheaza (fapt declarat la ANAF) - se corecteaza prin rectificativa (vezi apelantii)."""


class PerioadaNeconfirmata(ValueError):
    """Blocaj MOTIVAT (cele 4 elemente, DESIGN_SYSTEM cap.23): un calcul depinde de o perioada NECONFIRMATA.
    Subclasa de ValueError; tag PERIOADA_BLOCATA -> handler-ul global (main.py) o arata ca 423, nu traceback."""
    def __init__(self, ce, an, luna, domeniu, temei=""):
        self.an, self.luna, self.domeniu = an, luna, domeniu
        det = ("%s nu se poate calcula pentru %02d.%04d: pontajul lunii (%s) nu e CONFIRMAT - datele sunt "
               "informative, nu autoritative%s. Confirmă %s-ul lunii (buton, rol de administrator al firmei, la închidere) sau "
               "corectează datele; până atunci calculul e blocat." % (
                   ce, luna, an, domeniu, (" (" + temei + ")") if temei else "", domeniu))
        super().__init__("PERIOADA_BLOCATA: " + det)


def _tbl(schema):
    """[perioada_confirmata_v2_qualified] Numele calificat al tabelei. Cand `schema` e dat, califica
    {schema}.perioada_confirmata (robust pe orice conexiune, inclusiv fara search_path pe tenant - ruta
    stat-plata folosea db.get_conn() fara schema -> UndefinedTable -> 500). schema gol/None -> necalificat
    (search_path; apelanti ca salariati_api:410 care paseaza "")."""
    return ('"%s".perioada_confirmata' % schema) if schema else "perioada_confirmata"


def e_confirmat(conn, schema, an, luna, domeniu):
    """{confirmat: bool, confirmat_de, confirmat_la} pentru perioada (an, luna, domeniu)."""
    with conn.cursor() as cur:
        cur.execute("SELECT confirmat_de, confirmat_la FROM " + _tbl(schema) + " "
                    "WHERE an = %s AND luna = %s AND domeniu = %s", (an, luna, domeniu))
        r = cur.fetchone()
    return {"confirmat": r is not None,
            "confirmat_de": (r[0] if r else None),
            "confirmat_la": (r[1].isoformat() if r and r[1] else None)}


def confirma(conn, schema, an, luna, domeniu, user_id):
    """Marcheaza perioada CONFIRMATA (autoritativa). Idempotent (re-confirmarea reimprospateaza confirmat_la)."""
    with conn.cursor() as cur:
        cur.execute("INSERT INTO " + _tbl(schema) + " (an, luna, domeniu, confirmat_de) VALUES (%s, %s, %s, %s) "
                    "ON CONFLICT (an, luna, domeniu) DO UPDATE SET confirmat_de = EXCLUDED.confirmat_de, "
                    "confirmat_la = now()", (an, luna, domeniu, user_id))
    return {"ok": True}


def deconfirma(conn, schema, an, luna, domeniu):
    """Revine la NECONFIRMAT (o modificare a datelor inainte de depunere -> calculele din aval re-blocheaza)."""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM " + _tbl(schema) + " WHERE an = %s AND luna = %s AND domeniu = %s",
                    (an, luna, domeniu))
    return {"ok": True}
