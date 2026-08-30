# -*- coding: utf-8 -*-
"""Cele DOUĂ registre cerute de art. 321 alin. (4) din Codul fiscal, prin normele lui.

DE UNDE VINE, citit la sursă (lista 3, 30.08.2026). Art. 321 alin. (1)-(3) cere „evidențe corecte și
complete ale tuturor operațiunilor". **Alin. (4) trimite conținutul la normele metodologice** și
numește acolo, expres, două registre — HG 1/2016, normele la art. 321, literele e) și f).

**Rândul vechi al listei 3 spunea despre art. 321: *„substanța e derivabilă pe fiecare linie, lipsește
documentul"*. E FALS pentru primul dintre ele** — un **nontransfer** e o mișcare de bunuri **fără
vânzare**, deci nu se derivă din facturi. Verificat și în e-Transport: `etransport_trimiteri` ține
*trimiterea* (UIT, XML, stare), nu bunurile și partenerul. Deci nu e „documentul lipsește peste o
substanță existentă" — **lipsește substanța**, și de-aia registrele au tabel propriu.

CE FACE: ține evidența, o validează după normă, și o redă. **NU decide scutiri** — vezi
`EXCEPTII_NONTRANSFER`.
"""
from decimal import Decimal

from core.afirmatii import afirmatie
from core.common import Temei
from core.unde import Unde

MODUL = "registre_art321"

#: Nomenclator ÎNCHIS. Cele două registre sunt oglinzi: unul pleacă de la primitor, celălalt de la
#: expeditor.
FELURI = ("nontransfer", "bunuri_primite")

_TEMEI_E = Temei(
    "HG", 1, 2016, art="norme art.321", lit="e",
    data_in="2016-01-01", verificat_la="2026-08-30", de_cine="Code/Costin", nivel_sursa="MO",
    url="anaf_surse/hg_1_2016_norme_cod_fiscal.txt",
    text_citat=("un registru al nontransferurilor de bunuri transportate de persoana impozabila sau "
                "de alta persoana in contul acesteia in afara Romaniei, dar in interiorul "
                "Comunitatii, pentru operatiunile prevazute la art. 270 alin. (12) lit. f)-h) din "
                "Codul fiscal. Registrul nontransferurilor va cuprinde: denumirea si adresa "
                "primitorului, un numar de ordine, data transportului bunurilor, descrierea "
                "bunurilor transportate, cantitatea bunurilor transportate, valoarea bunurilor "
                "transportate, data transportului bunurilor care se intorc dupa efectuarea de "
                "lucrari asupra acestora, descrierea bunurilor returnate, cantitatea bunurilor "
                "returnate, descrierea bunurilor care nu sunt returnate, cantitatea acestora si o "
                "mentiune referitoare la documentele emise in legatura cu aceste operatiuni, dupa "
                "caz, precum si data emiterii acestor documente"))

_TEMEI_F = Temei(
    "HG", 1, 2016, art="norme art.321", lit="f",
    data_in="2016-01-01", verificat_la="2026-08-30", de_cine="Code/Costin", nivel_sursa="MO",
    url="anaf_surse/hg_1_2016_norme_cod_fiscal.txt",
    text_citat=("un registru pentru bunurile mobile corporale primite care au fost transportate din "
                "alt stat membru al Uniunii Europene in Romania sau care au fost importate in "
                "Romania ori achizitionate din Romania de o persoana impozabila nestabilita in "
                "Romania si care sunt date unei persoane impozabile in Romania in scopul evaluarii "
                "sau pentru lucrari efectuate asupra acestor bunuri in Romania. Registrul bunurilor "
                "primite nu trebuie tinut in cazul bunurilor care sunt plasate in regimul vamal de "
                "perfectionare activa"))

TEMEI = {"nontransfer": _TEMEI_E, "bunuri_primite": _TEMEI_F}

#: Câmpurile pe care norma le cere la ÎNSCRIERE, per registru. `valoare` e cerută **numai** la lit.
#: e) — lit. f) nu cere nicio valoare. Diferența e reală, nu o scăpare, și de-aia stă aici, lângă
#: citarea care o justifică, nu într-un `CHECK` din DDL.
CAMPURI_CERUTE = {
    "nontransfer": ("partener_denumire", "partener_adresa", "data_transport",
                    "descriere", "cantitate", "valoare"),
    "bunuri_primite": ("partener_denumire", "partener_adresa", "data_transport",
                       "descriere", "cantitate"),
}

#: Câmpurile piciorului de RETUR — se completează când bunurile se întorc, nu la înscriere.
CAMPURI_RETUR = ("data_retur", "descriere_returnate", "cantitate_returnate",
                 "descriere_nereturnate", "cantitate_nereturnate")

#: Cele CINCI cazuri pentru care norma spune că registrul nontransferurilor **nu** se completează.
#: Se ARATĂ omului; **aplicația nu decide că un caz se aplică.** O scutire hotărâtă de mașină pe
#: baza unei descrieri de bun ar fi exact „răspunsul în locul omului" pe care registrul îl refuză în
#: altă parte — iar aici greșeala ar însemna o evidență incompletă la un control.
EXCEPTII_NONTRANSFER = (
    "mijloacele de transport înmatriculate în România",
    "paleți, containere și alte ambalaje care circulă fără facturare",
    "bunurile necesare desfășurării activității de presă, radiodifuziune și televiziune",
    "bunurile necesare exercitării unei profesii sau meserii, dacă prețul sau valoarea normală pe "
    "fiecare bun nu depășește 1.250 de euro (și bunul nu e folosit mai mult de 7 zile în afara "
    "României), sau nu depășește 250 de euro (și bunul nu e folosit mai mult de 24 de luni)",
    "computerele portabile și alt material profesional similar transportat în afara României în "
    "cadrul unei deplasări de afaceri",
)


class InregistrareIncompleta(ValueError):
    """Un câmp cerut de normă lipsește. Poartă `camp` și `temei` ca DATE, nu doar în mesaj."""

    def __init__(self, mesaj, camp=None, temei=None):
        super().__init__(mesaj)
        self.camp = camp
        self.temei = temei


def _gol(v):
    return v is None or (isinstance(v, str) and not v.strip())


def valideaza(fel, date):
    """Ridică `InregistrareIncompleta` la primul câmp cerut care lipsește.

    NU completează nimic implicit. Un registru care ar pune o valoare în locul omului ar produce
    exact felul de evidență care nu se poate apăra: completă la vedere, inventată pe dedesubt.
    """
    if fel not in FELURI:
        raise InregistrareIncompleta("fel necunoscut %r; nomenclatorul e închis: %s"
                                     % (fel, ", ".join(FELURI)), camp="fel")
    for c in CAMPURI_CERUTE[fel]:
        if _gol(date.get(c)):
            raise InregistrareIncompleta(
                "Registrul cere «%s», iar câmpul e gol. Norma: %s" % (c, TEMEI[fel]),
                camp=c, temei=str(TEMEI[fel]))
    if Decimal(str(date.get("cantitate") or 0)) <= 0:
        raise InregistrareIncompleta("cantitatea trebuie să fie mai mare decât zero",
                                     camp="cantitate", temei=str(TEMEI[fel]))


def adauga(conn, schema, fel, date):
    """Înscrie un rând. `nr_ordine` se DERIVĂ — un număr de ordine tastat de om se poate repeta."""
    valideaza(fel, date)
    campuri = list(CAMPURI_CERUTE[fel]) + [c for c in CAMPURI_RETUR if not _gol(date.get(c))]
    for c in ("documente", "data_documente"):
        if not _gol(date.get(c)):
            campuri.append(c)
    with conn.cursor() as cur:
        cur.execute("SELECT COALESCE(MAX(nr_ordine), 0) + 1 FROM {s}.registre_art321 "
                    "WHERE fel = %s".format(s=schema), (fel,))
        nr = cur.fetchone()[0]
        cur.execute(
            "INSERT INTO {s}.registre_art321 (fel, nr_ordine, {c}) VALUES (%s, %s, {p}) "
            "RETURNING id".format(s=schema, c=", ".join(campuri),
                                  p=", ".join(["%s"] * len(campuri))),
            [fel, nr] + [date.get(c) for c in campuri])
        iid = cur.fetchone()[0]
    conn.commit()
    return {"id": iid, "nr_ordine": nr}


def randuri(conn, schema, fel, an=None):
    from psycopg2.extras import RealDictCursor
    unde, arg = "fel = %s", [fel]
    if an:
        unde += " AND date_trunc('year', data_transport) = %s"
        arg.append("%d-01-01" % an)
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM {s}.registre_art321 WHERE {u} ORDER BY nr_ordine"
                    .format(s=schema, u=unde), arg)
        return [dict(r) for r in cur.fetchall()]


def _simplu(v):
    import datetime
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, (datetime.date, datetime.datetime)):
        return v.isoformat()
    return v


def registru(conn, schema, fel, an=None):
    """Registrul, ca AFIRMAȚIE — cu temeiul lui și cu ce NU acoperă."""
    if fel not in FELURI:
        raise ValueError("fel necunoscut: %r" % fel)
    rs = [{k: _simplu(v) for k, v in r.items()} for r in randuri(conn, schema, fel, an)]
    return afirmatie(
        "fapt", tip="registru_art321_" + fel,
        motiv=("Registrul %s, ținut potrivit art. 321 alin. (4) din Codul fiscal"
               % ("nontransferurilor" if fel == "nontransfer" else "bunurilor primite")),
        temei_completitudine=("toate rândurile înscrise în `registre_art321` pentru felul %r%s, în "
                              "ordinea numărului de ordine. **Registrul cuprinde ce s-a înscris — "
                              "nu se derivă din facturi**, fiindcă operațiunile pe care le "
                              "consemnează sunt mișcări de bunuri FĂRĂ vânzare"
                              % (fel, (", exercițiul %d" % an) if an else ", toate exercițiile")),
        # Domeniul e OBIECTUL, nu perioada: norma nu cere reluarea numerotarii la 1 ianuarie, deci
        # un registru fara `an` nu e un fapt nedatat, e un fapt despre registrul intreg. `an` ramane
        # alaturi cand se cere filtrat, ca sa nu se piarda ce s-a intrebat.
        an=an, luna=None, unde=Unde("registru", fel),
        **{
        # NU `fel`: `afirmatie()` are deja un parametru cu numele asta — nomenclatorul ei inchis
        # (fapt / necunoastere / contradictie / ...). Doua intelesuri pe acelasi nume in acelasi
        # payload ar fi o ambiguitate pe care cititorul o descopera abia cand ceva crapa.
        "registru": fel,
        "randuri": rs,
        "temei": str(TEMEI[fel]),
        "campuri_cerute": list(CAMPURI_CERUTE[fel]),
        "exceptii": list(EXCEPTII_NONTRANSFER) if fel == "nontransfer" else [],
        })
