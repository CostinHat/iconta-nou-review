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
    n-a fost nimic;
  - nu face analitic pe partener: contul corespondent e cel din nota, nu o desfasurare pe terti;
  - nu randeaza. Randarea e alta munca (lista 5), iar aici se opreste producatorul.
"""
from dataclasses import asdict, dataclass
from datetime import date as _date
from decimal import Decimal
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
    return Decimal(str(x or 0)).quantize(Decimal("0.01"))


def fisa_cont(conn, schema, cont, an, luna=None, sold_initial=None):
    """Fisa de cont pentru operatiuni diverse, pe un cont sintetic sau analitic.

    `luna=None` inseamna tot anul. `sold_initial` e un Decimal cu semn (+ debitor / − creditor);
    daca lipseste, fisa porneste de la 0 si o declara.

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

    di = "%d-%02d-01" % (an, luna) if luna else "%d-01-01" % an
    ds = ("%d-%02d-01" % (an + 1, 1) if luna == 12 else
          "%d-%02d-01" % (an, luna + 1)) if luna else "%d-01-01" % (an + 1)

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"""
            SELECT i.data, i.numar, i.descriere, i.sursa,
                   l.cont_debit, l.cont_credit, l.suma
              FROM {schema}.inregistrari i
              JOIN {schema}.inregistrari_linii l ON l.inregistrare_id = i.id
             WHERE i.status = 'validata'
               AND i.data >= %s AND i.data < %s
               AND (l.cont_debit = %s OR l.cont_credit = %s)
             ORDER BY i.data, i.id, l.id
        """, (di, ds, cont, cont))
        brut = cur.fetchall()

    sold = _q(sold_initial if sold_initial is not None else 0)
    randuri = []
    td = tc = Decimal("0.00")
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
            explicatie=(r["descriere"] or "").strip() or None,
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
        motiv="Fisa de cont pentru operatiuni diverse (cod %s), contul %s" % (COD_FORMULAR, cont),
        temei_completitudine=("toate liniile din `inregistrari_linii` care ating contul %s, pe note cu "
                              "status='validata', in intervalul [%s, %s), in ordine cronologica; "
                              "ciornele NU sunt evidenta" % (cont, di, ds)),
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
    di = "%d-%02d-01" % (an, luna) if luna else "%d-01-01" % an
    ds = ("%d-01-01" % (an + 1) if luna == 12 else
          "%d-%02d-01" % (an, luna + 1)) if luna else "%d-01-01" % (an + 1)
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
        return [r[0] for r in cur.fetchall()]
