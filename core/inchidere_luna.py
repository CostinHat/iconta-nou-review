# -*- coding: utf-8 -*-
"""core/inchidere_luna.py — ACTUL DE INCHIDERE a lunii pe domeniul `facturi` (21.08.2026).

DE CE EXISTA. `d390_are_operatiuni` intorcea False pe „luna inchisa" - dar inchis insemna doar ca luna
CALENDARISTICA s-a terminat, nu ca evidenta lunii e completa. O firma care n-a introdus inca facturile
de iulie primea in august „D390 nu se datoreaza pe iulie". Ce lipsea nu era mecanismul (exista,
`core/perioada.py`, DESIGN_SYSTEM cap.23), ci DOMENIUL si actul: cineva trebuie sa DECLARE ca luna e
inchisa. Pana atunci, „luna inchisa" e o observatie despre calendar, nu o afirmatie a cuiva.

CELE DOUA REGULI ALE MECANISMULUI (cap.23), aplicate aici:
  1. Cat timp e NECONFIRMATA, evidenta lunii e informativa - afirmatiile din aval nu se sprijina pe ea.
  2. O MODIFICARE de-confirma AUTOMAT (`facturi_api` cheama `perioada.deconfirma`). O confirmare care
     supravietuieste unei modificari e chiar „verde e o afirmatie": ar spune „complet" despre alte date.

NU SE CONFIRMA PESTE O ABSENTA CUNOSCUTA. Daca ANAF ne-a dat e-Facturi pe luna aia si ele nu sunt inca
inregistrate, inchiderea e REFUZATA cu blocaj motivat: nu lasam pe cineva sa declare complet ceva ce
noi vedem deja ca nu e. Refuzul numeste cate sunt si unde se rezolva.

ADOPTAREA E PER FIRMA, si de-aia poarta din `d390` nu se converteste peste noapte. O firma care n-a
inchis niciodata o luna ramane exact cu comportamentul de dinainte (calendar + documente in asteptare);
una care a inceput sa inchida primeste afirmatia mai tare, de la prima luna inchisa incolo. Decizia:
poarta se INTARESTE, nu converteste clasa in necunoastere (Costin, 21.08).
"""

DOMENIU = "facturi"


def stare(conn, schema, an, luna):
    """{confirmat, confirmat_de, confirmat_la, poate_confirma, blocaj} pentru (an, luna)."""
    from core import perioada as _per
    st = dict(_per.e_confirmat(conn, schema, an, luna, DOMENIU))
    bl = blocaj(conn, schema, an, luna)
    st["poate_confirma"] = (not st["confirmat"]) and bl is None
    st["blocaj"] = bl
    # Blocajul NUMESTE obstacolul; remediul spune UNDE se rezolva. Vazut privind captura: ecranul
    # arata „1 e-Factura ... e inca neinregistrata" si se oprea acolo - contabilul stia ce, nu si unde.
    # Remediul e al CONTEXTULUI de inchidere, nu al sondei (semaforul foloseste acelasi motiv altfel).
    st["remediu"] = ("Înregistrează-le (sau respinge-le) în e-Factura, apoi închide luna."
                     if bl else None)
    return st


def blocaj(conn, schema, an, luna):
    """Motivul pentru care luna NU se poate declara inchisa, sau None. Sursa unica: aceeasi sonda pe
    care o foloseste si semaforul (`d390.evidenta_incompleta`) - o singura definitie a „evidentei
    incomplete", nu doua care pot diverge."""
    from core import d390 as _d390
    return _d390.evidenta_incompleta(conn, schema, an, luna)


def confirma(conn, schema, an, luna, user_id):
    """Declara luna INCHISA pe domeniul facturi. Refuza motivat daca stim de documente in asteptare.
    Idempotent (mecanismul din `perioada.confirma` reimprospateaza confirmat_la)."""
    from core import perioada as _per
    bl = blocaj(conn, schema, an, luna)
    if bl:
        raise ValueError(
            "Luna %02d.%04d nu se poate declara închisă: %s Înregistrează-le (sau respinge-le) în "
            "e-Factura, apoi închide luna." % (luna, an, bl))
    _per.confirma(conn, schema, an, luna, DOMENIU, user_id)
    return stare(conn, schema, an, luna)


def redeschide(conn, schema, an, luna):
    """Revine la NEINCHIS (o corectie de facturi cere redeschiderea lunii)."""
    from core import perioada as _per
    _per.deconfirma(conn, schema, an, luna, DOMENIU)
    return stare(conn, schema, an, luna)


def prima_luna_inchisa(conn, schema):
    """(an, luna) cea mai VECHE luna inchisa pe facturi, sau None daca firma n-a inchis niciodata.
    Punctul de ADOPTARE: dinaintea lui nu cerem inchidere, fiindca firma nu folosea mecanismul."""
    from core import perioada as _per
    with conn.cursor() as cur:
        cur.execute("SELECT an, luna FROM " + _per._tbl(schema) + " WHERE domeniu = %s "
                    "ORDER BY an, luna LIMIT 1", (DOMENIU,))
        r = cur.fetchone()
    return (r[0], r[1]) if r else None


def luna_neinchisa_desi_firma_inchide(conn, schema, an, luna):
    """Motivul „luna nu e inchisa contabil", DOAR pentru firmele care folosesc inchiderea si doar
    pentru lunile de la adoptare incolo. Altfel None - o firma care nu inchide luni nu primeste gri
    peste tot (conversia refuzata de Costin)."""
    from core import perioada as _per
    prima = prima_luna_inchisa(conn, schema)
    if not prima or (an, luna) < prima:
        return None
    if _per.e_confirmat(conn, schema, an, luna, DOMENIU)["confirmat"]:
        return None
    return ("luna %02d.%04d nu e declarată închisă pe facturi, iar firma închide lunile — până la "
            "închidere nu pot confirma că evidența lunii e completă." % (luna, an))
