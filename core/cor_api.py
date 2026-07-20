# -*- coding: utf-8 -*-
"""
core/cor_api.py — [F137] nomenclatorul COR (Clasificarea Ocupatiilor din Romania).

Nomenclator NATIONAL (acelasi pentru toate firmele) -> traieste in public.cor_ocupatii, NU per-tenant.
Sursa oficiala: data.gov.ro (dataset "Clasificarea Ocupatiilor din Romania"), lista alfabetica,
Ordin 573/180/2024 (MO 344/12.04.2024) - 4422 ocupatii, cod pe 6 cifre. Fisier in cor_surse/,
incarcat prin cor_incarca.py. Codul COR trebuie sa fie unul REAL din nomenclator: REGES respinge
un cod inexistent (art. contract), deci il validam la sursa, nu il lasam free-text ca pana acum.

Cautarea e diacritic-insensitiva (numele contin ă/î/ș/ț; utilizatorul tasteaza fara diacritice):
comparam pe forma normalizata (ASCII minuscule), stocata in coloana denumire_cauta.
"""
VERSIUNE_COR = 10  # versiunea COR ceruta de REGES (10 = COR 2010, ISCO-08); DataInceput contract

_DIAC = {"ă": "a", "â": "a", "î": "i", "ș": "s", "ş": "s", "ț": "t", "ţ": "t"}


def normalizeaza(s):
    """Text -> forma de cautare: diacritice -> ASCII, minuscule, spatii colapsate."""
    s = "".join(_DIAC.get(c, c) for c in str(s or "").lower())
    return " ".join(s.split())


def cauta(conn, q, limit=25):
    """Cauta ocupatii dupa COD (prefix) sau DENUMIRE (substring, diacritic-insensitiv).
    Intoarce [{cod, denumire}] (max limit). q gol -> lista goala."""
    q = (q or "").strip()
    if not q:
        return []
    with conn.cursor() as cur:
        if q.isdigit():
            cur.execute("SELECT cod, denumire FROM public.cor_ocupatii "
                        "WHERE cod LIKE %s ORDER BY cod LIMIT %s", (q + "%", limit))
        else:
            nq = normalizeaza(q)
            cur.execute("SELECT cod, denumire FROM public.cor_ocupatii "
                        "WHERE denumire_cauta LIKE %s ORDER BY denumire_cauta LIMIT %s",
                        ("%" + nq + "%", limit))
        return [{"cod": c, "denumire": d} for c, d in cur.fetchall()]


def exista(conn, cod):
    """True daca acest cod COR (6 cifre) exista in nomenclator. cod gol -> False."""
    cod = (cod or "").strip()
    if not cod:
        return False
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM public.cor_ocupatii WHERE cod = %s", (cod,))
        return cur.fetchone() is not None


def denumire(conn, cod):
    """Denumirea ocupatiei pentru un cod, sau None."""
    cod = (cod or "").strip()
    if not cod:
        return None
    with conn.cursor() as cur:
        cur.execute("SELECT denumire FROM public.cor_ocupatii WHERE cod = %s", (cod,))
        r = cur.fetchone()
    return r[0] if r else None


def nr_ocupatii(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM public.cor_ocupatii")
        return cur.fetchone()[0]
