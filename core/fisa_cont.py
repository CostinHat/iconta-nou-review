# -*- coding: utf-8 -*-
"""Fisa de cont pentru operatiuni diverse (cod 14-6-22).

DE CE EXISTA, si de ce ea prima. `Cartea mare` (cod 14-1-3) si `Cartea mare (sah)` (14-1-3/a) sunt
registre obligatorii, iar aplicatia nu le producea: `motor.carte_mare` e un invelis peste
`agrega_conturi`, care intoarce RULAJE TOTALE - adica o balanta de rulaje, nu Cartea mare.

Ce a decis constructia e o propozitie din norma, aceeasi la amandoua codurile, citita verbatim din
corpus (`anaf_surse/omfp_2634_2015_anexa2_norme_specifice.txt`, poz. 165 si 166):

    „Registrul Cartea mare poate fi inlocuit cu Fisa de cont pentru operatiuni diverse."

Deci obligatia se poate stinge cu UN artefact, indiferent de forma de inregistrare a entitatii
(„pe jurnale" sau „maestru-sah") - vezi R21, inchisa exact pe iesirea asta. Fisa e si mai ieftina, si
mai informativa: pastreaza CRONOLOGIA si contul corespondent pe fiecare rand, ceea ce balanta pierde
chiar la insumare.

CE CONTINE UN RAND, dupa modelul din Anexa 2: data operatiunii · documentul (felul si numarul) ·
explicatia · CONTUL CORESPONDENT · debit · credit · soldul curent, cu sensul lui (D/C).

CE NU FACE, declarat:
  - nu inventeaza sold initial: daca nu i se da unul, porneste de la zero si O SPUNE in antet
    (`sold_initial_declarat=False`), fiindca o fisa care porneste tacit de la zero afirma ca inainte
    n-a fost nimic. [lotul 10, 425] Ruta (Cartea mare) i-l da: `sold_initial_preluat`, din balanta de deschidere
    si notele dinainte, cu aceeasi regula ca balanta;
  - nu face analitic pe partener: contul corespondent e cel din nota, nu o desfasurare pe terti;
  - nu randeaza. Randarea e alta munca (lista 5), iar aici se opreste producatorul.
"""
from dataclasses import asdict, dataclass
from datetime import date as _date
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from psycopg2.extras import RealDictCursor

from core.afirmatii import afirmatie

MODUL = "fisa_cont"
REGULI = "2026.1"

# Norma: „Registrul Cartea mare poate fi inlocuit cu Fisa de cont pentru operatiuni diverse."
# (OMFP 2634/2015, Anexa 2, cod 14-1-3 si 14-1-3/a; fisa insasi e cod 14-6-22.)
COD_FORMULAR = "14-6-22"


@dataclass
class RandFisa:
    """Un rand de fisa e un OBIECT cu atribute, nu un dict de proza (P3, 21.08.2026).

    Prima forma il construia ca dict literal, iar `scan_afirmatii` l-a clasificat drept afirmatie
    netipata - pe drept: un rand care spune „contul 5311 a primit 1000 de la 4111, sold 1000 D" e o
    afirmatie despre datele firmei. Ca obiect, campurile lui nu se pot rata la citire si nu se pot
    inmulti tacit."""
    data: _date
    cont_corespondent: str
    debit: Decimal
    credit: Decimal
    sold: Decimal
    sens_sold: str                      # "D" | "C" | "0"
    document: Optional[str] = None      # numarul notei
    explicatie: Optional[str] = None
    jurnal: Optional[str] = None        # jurnalul de origine (`inregistrari.sursa`)

    def ca_dict(self):
        """Pentru randare/JSON. Conversia se face la MARGINE, nu in interior."""
        return asdict(self)


def _q(x):
    return Decimal(str(x or 0)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _fereastra(an, luna):
    di = "%d-%02d-01" % (an, luna) if luna else "%d-01-01" % an
    ds = ("%d-%02d-01" % (an + 1, 1) if luna == 12 else
          "%d-%02d-01" % (an, luna + 1)) if luna else "%d-01-01" % (an + 1)
    return di, ds


def sold_initial_preluat(conn, schema, cont, an, luna=None):
    """[lotul 10, deficiența 425, comanda Costin 10.1] Soldul de la începutul ferestrei fișei (Cartea mare) și rulajul preluat care intră în
    ea — (sold cu semn: + debitor / − creditor, (data_preluarii, debit, credit) sau None). ACEEAȘI regulă ca balanța
    (`documente_api.balanta`), din `core/rulaje_preluate` (fără logică proprie): „Când fișierul are soldurile inițiale ale anului și
    rulajele, ele intră ca sold inițial și sume precedente [...]. Când are doar solduri finale, comportamentul de acum rămâne”.
      * fereastra cuprinde întreg intervalul preluat [01.01, data preluării] (`rulaje_preluate.rulaje`: anul întreg) -> soldul de la
        1 ianuarie (`si_an`) + rulajul preluat ca prim rând al fișei; soldul final iese același;
      * altfel -> partea preluată a soldului la începutul ferestrei (`rulaje_preluate.sold_preluat`: `si_an` la 1 ianuarie, soldul final
        de la data preluării în rest);
    plus notele VALIDATE ale contului dinaintea ferestrei. Conturile preluate se iau pe prefix (`sold_preluat`: analiticele contului)."""
    from core import rulaje_preluate as _rp
    di, ds = _fereastra(an, luna)
    d_i, d_s = _date.fromisoformat(di), _date.fromisoformat(ds)
    with conn.cursor() as cur:
        rul = {k: v for k, v in _rp.rulaje(cur, schema, d_i, d_s).items() if str(k).startswith(cont)}
        rulaj = None
        if rul:
            p = _rp.preluate(cur, schema, d_i.year)
            sd = sum((v["si_d"] for k, v in p["conturi"].items() if str(k).startswith(cont)), Decimal("0"))
            sc = sum((v["si_c"] for k, v in p["conturi"].items() if str(k).startswith(cont)), Decimal("0"))
            rulaj = (p["ref"], sum((v[0] for v in rul.values()), Decimal("0")), sum((v[1] for v in rul.values()), Decimal("0")))
        else:
            sd, sc = _rp.sold_preluat(cur, schema, cont, d_i)
        cur.execute(f"""SELECT COALESCE(SUM(CASE WHEN l.cont_debit = %s THEN l.suma ELSE 0 END), 0)
                              - COALESCE(SUM(CASE WHEN l.cont_credit = %s THEN l.suma ELSE 0 END), 0)
                          FROM {schema}.inregistrari i JOIN {schema}.inregistrari_linii l ON l.inregistrare_id = i.id
                         WHERE i.status = 'validata' AND i.data < %s AND (l.cont_debit = %s OR l.cont_credit = %s)""",
                    (cont, cont, di, cont, cont))
        r = cur.fetchone()
        note = Decimal(str((list(r.values())[0] if isinstance(r, dict) else r[0]) or 0))
    return _q(sd - sc + note), rulaj


def fisa_cont(conn, schema, cont, an, luna=None, sold_initial=None, rulaj_preluat=None):
    """Fisa de cont pentru operatiuni diverse, pe un cont sintetic sau analitic.

    `luna=None` inseamna tot anul. `sold_initial` e un Decimal cu semn (+ debitor / − creditor);
    daca lipseste, fisa porneste de la 0 si o declara. `rulaj_preluat` = (data preluarii, debit, credit) — [lotul 10, 425] rulajul
    anului adus de balanta de deschidere (`sold_initial_preluat`), primul rand al fisei.

    Se citesc DOAR notele VALIDATE.

    [R96, 06.09.2026] Propozitia de dinainte spunea „aceeasi regula ca la restul motorului" — si era
    FALSA despre restul motorului: `documente_api.balanta` si ruta `/tenants/{id}/jurnal` NU
    filtreaza pe status deloc, iar a doua chiar duce `status` mai departe pe fiecare rand. Masurat
    pe 08/2026: pe 8 firme din 20 multimile difera; pe patru dintre ele TOATE notele lunii sunt
    ciorne, deci intra in doua registre obligatorii si lipsesc din al treilea.

    Abaterea e acum DECLARATA si gardata: `core/scan_populatii_registre.ABATERI_DECLARATE` +
    `core/test_populatii_registre.py`. CARE multime e cea corecta ramane **R36** — o decizie nedata;
    pana atunci abaterea e vizibila, nu justificata.
    """
    cont = str(cont or "").strip()
    if not cont:
        raise ValueError("Fișa de cont: contul e obligatoriu.")
    if luna is not None and not (1 <= int(luna) <= 12):
        raise ValueError("Fișa de cont: luna invalidă (%r)." % luna)

    di, ds = _fereastra(an, luna)

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"""
            SELECT i.id, i.data, i.numar, i.descriere, i.sursa,
                   l.cont_debit, l.cont_credit, l.suma
              FROM {schema}.inregistrari i
              JOIN {schema}.inregistrari_linii l ON l.inregistrare_id = i.id
             WHERE i.status = 'validata'
               AND i.data >= %s AND i.data < %s
               AND (l.cont_debit = %s OR l.cont_credit = %s)
             ORDER BY i.data, i.id, l.id
        """, (di, ds, cont, cont))
        brut = cur.fetchall()
        # [lotul 11, 443 — datele existente] nota validată scrisă înainte de 443 („Contare factura F1A3”) nu se modifică (OMFP 1802/2014
        # pct.69); explicația o arată cu seria separat, ca Registrul jurnal
        from core import jurnal_api as _j
        afisat = _j.note_fara_serie_lipita(cur, schema, sorted({r["id"] for r in brut}))

    sold = _q(sold_initial if sold_initial is not None else 0)
    randuri = []
    td = tc = Decimal("0.00")
    if rulaj_preluat:
        # [lotul 10, 425] rulajul 01.01 .. data preluării, din balanța de deschidere: „sume precedente” ale anului, ca în balanță
        from core.pdf_util import data_ro
        ref, rd, rc = rulaj_preluat
        rd, rc = _q(rd), _q(rc)
        sold = _q(sold + rd - rc)
        td += rd
        tc += rc
        randuri.append(RandFisa(data=ref, document=None, jurnal="preluare", cont_corespondent="",
                                explicatie="Rulajele preluate din balanța de deschidere, %s – %s" % (data_ro("%d-01-01" % ref.year), data_ro(ref)),
                                debit=rd, credit=rc, sold=abs(sold), sens_sold="D" if sold > 0 else ("C" if sold < 0 else "0")))
    for r in brut:
        suma = _q(r["suma"])
        pe_debit = r["cont_debit"] == cont
        # Contul CORESPONDENT e celalalt capat al aceleiasi linii - exact ce pierde balanta.
        corespondent = r["cont_credit"] if pe_debit else r["cont_debit"]
        debit = suma if pe_debit else Decimal("0.00")
        credit = Decimal("0.00") if pe_debit else suma
        sold = _q(sold + debit - credit)
        td += debit
        tc += credit
        randuri.append(RandFisa(
            data=r["data"],
            document=(r["numar"] or "").strip() or None,
            explicatie=((afisat.get(r["id"]) or {}).get("descriere") or r["descriere"] or "").strip() or None,
            jurnal=(r["sursa"] or "").strip() or None,
            cont_corespondent=corespondent,
            debit=debit,
            credit=credit,
            sold=abs(sold),
            sens_sold="D" if sold > 0 else ("C" if sold < 0 else "0"),
        ))

    # Fisa e o AFIRMATIE despre datele firmei, nu un dict de proza (P3, 21.08.2026) - iar la un
    # control exact asta o face aparabila: `temei_completitudine` spune DE CE credem ca am vazut tot.
    # Fara el, o fisa care omite o nota arata identic cu una completa.
    return afirmatie(
        "fapt", tip="fisa_cont",
        motiv="Fișa de cont pentru operațiuni diverse (cod %s), contul %s" % (COD_FORMULAR, cont),
        temei_completitudine=("toate liniile notelor validate care ating contul %s, de la %s până înainte de %s, "
                              "în ordine cronologică; ciornele nu sunt evidență" % (cont, di, ds)),
        **{
        "formular": COD_FORMULAR,
        "cont": cont,
        "an": an,
        "luna": luna,
        "sold_initial": _q(sold_initial if sold_initial is not None else 0),
        "sold_initial_declarat": sold_initial is not None,
        "randuri": randuri,
        "total_debit": _q(td),
        "total_credit": _q(tc),
        "sold_final": abs(_q(sold)),
        "sens_sold_final": "D" if sold > 0 else ("C" if sold < 0 else "0"),
        })


def pentru_json(f):
    """Fisa, cu valorile pe care le poate purta un JSON. Conversia se face la MARGINE, aici — nu in
    interiorul motorului, si nici in ruta.

    `Decimal` si `date` nu pleaca asa cum sunt, iar randurile sunt dataclass-uri. Traieste aici
    fiindca modulul asta e singurul care STIE ce tipuri produce: o conversie scrisa in ruta ar
    ramane in urma la primul camp nou.
    """
    def _v(x):
        if isinstance(x, Decimal):
            return float(x)
        if isinstance(x, _date):
            return x.isoformat()
        if isinstance(x, RandFisa):
            return {k: _v(v) for k, v in x.ca_dict().items()}
        if isinstance(x, dict):
            return {k: _v(v) for k, v in x.items()}
        if isinstance(x, (list, tuple)):
            return [_v(v) for v in x]
        return x
    return {k: _v(v) for k, v in f.items()}


def conturi_cu_miscare(conn, schema, an, luna=None):
    """Conturile care au cel putin o linie in perioada - domeniul pe care fisa se poate emite.

    Exista ca sa nu se ceara o fisa pe un cont ales din plan si sa iasa goala: o fisa goala pe un
    cont fara miscare NU e o eroare, dar nici nu e ce cere organul de control.
    """
    di, ds = _fereastra(an, luna)
    from core import rulaje_preluate as _rp
    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT DISTINCT c FROM (
                SELECT l.cont_debit AS c FROM {schema}.inregistrari i
                  JOIN {schema}.inregistrari_linii l ON l.inregistrare_id = i.id
                 WHERE i.status='validata' AND i.data >= %s AND i.data < %s
                UNION ALL
                SELECT l.cont_credit FROM {schema}.inregistrari i
                  JOIN {schema}.inregistrari_linii l ON l.inregistrare_id = i.id
                 WHERE i.status='validata' AND i.data >= %s AND i.data < %s
            ) t WHERE c IS NOT NULL AND c <> '' ORDER BY 1
        """, (di, ds, di, ds))
        conturi = {(r[0] if not isinstance(r, dict) else list(r.values())[0]) for r in cur.fetchall()}
        # [lotul 10, 425] „cu toate conturile care au rulaj”: și cele cu rulaj numai în balanța de deschidere a anului
        conturi |= {k for k, (d, c) in _rp.rulaje(cur, schema, _date.fromisoformat(di), _date.fromisoformat(ds)).items() if d or c}
        return sorted(conturi)
