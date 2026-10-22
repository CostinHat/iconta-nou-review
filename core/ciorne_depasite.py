# -*- coding: utf-8 -*-
"""core/ciorne_depasite.py — ciorna DERIVATĂ dintr-o sursă se validează numai cât e ce ar scrie sursa ACUM (lotul 11, deficiența 451).

Comanda Costin 11.1 pct.6, verbatim: „Prioritar, 451: ciornele generate înainte de o reparație rămân validabile cu regula veche. Cazuri:
ieșirea Marfa A din Z 0042 cu «Bon de consum nr 1», F1; ciorna salariilor 10/2026 cu alte sume decât statul curent, F5 (448). Toate
trebuie refăcute din sursă sau marcate depășite și oprite de la validare, pe toate firmele.”

CLASA (nu cele două instanțe): o ciornă scrisă de aplicație dintr-o sursă (statul de plată, raportul Z, factura, NIR-ul, registrul
mijloacelor fixe, mișcarea de stoc …) păstrează regula de LA SCRIERE; o reparație a regulii (documentul Z-ului în loc de bonul de consum
— 438; statul cu concediul medical — 448) nu atinge ciornele deja scrise, iar validarea le ducea în evidență așa. Nicio dată (o
„versiune a regulii” ștampilată pe notă) nu poate ține pasul cu reparațiile — de aceea comparația e cu SURSA, nu cu o etichetă:

  · la VALIDARE (`jurnal_api.valideaza` — drumul unic: Registrul jurnal, coada „De validat”, validarea în masă, validarea internă la
    PFA), ciorna derivată se REGENEREAZĂ PE USCAT (aceleași funcții care o scriu, fără nicio scriere) și se compară cu ea pe ce intră în
    evidență: data, documentul justificativ, conturile și sumele. Diferă -> refuz NUMIT („nota a fost generată pe <data> după o regulă
    care s-a schimbat: acum ar fi …; refă-o din <sursă>”), cu refacerea oferită (`POST …/jurnal/{nota_id}/reface`);
  · sursa care nu mai poate scrie nota (statul nu se mai poate contabiliza, factura de stornare nu mai există, un mijloc fix fără
    date) -> ciorna e DEPĂȘITĂ cu motivul, și nu se validează;
  · nota la zi trece mai departe neatinsă.

INVENTARUL SURSELOR (`SURSE`, păzit de `core/test_lot11_s_451_ciorne_depasite.py`: o sursă nouă de notă — în `note_derivate.UNDE` sau în
scrierile din cod — fără rând aici pică poarta). Fiecare fel are UNA din trei stări, cu motivul:
  · REGENERAT — comparat la validare, cu refacerea din sursă;
  · VERIFICAT ALTFEL — o poartă existentă compară deja ciorna cu sursa de acum (închiderea anului: `inchidere_an.refuz_validare`);
  · NEREGENERABIL — ciorna se scrie din alegeri ale omului pe care sursa nu le păstrează (contul ales la contare, NIR-ul legat, încadrarea
    lipsei la inventar, sumele tastate ale Z-ului, operațiunea de casă): nu se poate spune ce ar scrie sursa acum fără să ghicim. Pentru
    acestea validarea rămâne cum era, iar `scripts/ciorne_depasite.py --proba` le numără separat („neverificate”) — limita e declarată, nu
    ascunsă.

Temei: OMFP 2634/2015 anexa 1 pct.58 lit.c (criteriile minimale ale programelor informatice) — „fiecare dată înregistrată în contabilitate
trebuie să se regăsească în conținutul unui document, la care să poată avea acces atât beneficiarii, cât și organele de control”; o ciornă
cu alte sume decât statul de acum, sau cu alt document decât cel al vânzării, ar intra în evidență fără să se regăsească în documentul ei.
"""
import re
from collections import namedtuple
from decimal import Decimal, ROUND_HALF_UP

from core.common import Temei

COD = "NOTA_DEPASITA"
#: ruta refacerii din sursă (butonul de pe rândul ciornei, `data-actiune` — dreptul „Poate pregăti”)
ACTIUNE_REFACERE = "POST /tenants/{tenant_id}/jurnal/{nota_id}/reface"

TEMEI = Temei(
    "OMFP", 2634, 2015, art="pct.58", lit="c", text="OMFP 2634/2015 pct.58 lit.c",
    data_in="2016-01-01", verificat_la="2026-10-21", de_cine="Code", nivel_sursa="MO",   # ART. 8: „se aplică începând cu data de 1 ianuarie 2016”
    url="anaf_surse/omfp_2634_2015_anexa1_norme_generale.txt",
    text_citat=("fiecare dată înregistrată în contabilitate trebuie să se regăsească în conținutul unui document, la care să poată avea "
                "acces atât beneficiarii, cât și organele de control"))

REGENERAT, VERIFICAT_ALTFEL, NEREGENERABIL = "regenerat", "verificat_altfel", "neregenerabil"

#: fel -> (starea, cum se verifică / de ce nu se poate)
SURSE = {
    "salarii": (REGENERAT, "statul de plată de acum: `salarii_contare.propunere` (D112 al lunii) + `salarii_contare.antet_nota`"),
    "amortizare": (REGENERAT, "registrul mijloacelor fixe de acum: `amortizare_lunii.linii`; documentul (tabloul) rămâne al notei"),
    "stoc_iesire": (REGENERAT, "mișcarea de stoc (articolul, valoarea ieșită) cu regula de acum a documentului: "
                               "`stocuri_cv_api.propunere_nota_miscare` — ieșirea manuală, din factură, din raportul Z"),
    "stoc_retur": (REGENERAT, "returul la stornarea facturii, din mișcare și din factura de stornare: `stocuri_cv_api.propunere_nota_miscare`"),
    "factura_emisa": (REGENERAT, "contarea facturii EMISE din factura de acum: `contare_facturi.note_propuse` (conturile de venit ale "
                                 "liniilor, regimul TVA la data ei, stornarea); data notei (contarea istorică) și documentul rămân ale notei"),
    "inchidere_an": (VERIFICAT_ALTFEL, "`inchidere_an.refuz_validare` compară nota cu soldurile validate de acum (deficiența 243)"),
    "factura": (NEREGENERABIL, "contarea facturii PRIMITE poartă alegerile omului de la „Contabilizează” (contul de cheltuială, NIR-ul "
                               "legat sau „altă livrare”), pe care factura nu le păstrează"),
    "borderou": (NEREGENERABIL, "nota borderoului poartă contul ales de om în Stocuri › „Borderou de achiziție”"),
    "plata_factura": (NEREGENERABIL, "plata e operațiunea omului (suma, data), nu o regulă a aplicației"),
    "plata_borderou": (NEREGENERABIL, "plata e operațiunea omului (suma, data), nu o regulă a aplicației"),
    "nir": (NEREGENERABIL, "nota NIR-ului poartă alegerea omului (factura legată sau „fără factură”, pe 408) de la recepție"),
    "inventar": (NEREGENERABIL, "nota inventarului poartă încadrarea lipsei aleasă de om (imputabilă / neimputabilă / justificată, cota)"),
    "stoc_alt": (NEREGENERABIL, "mișcările fără notă proprie regenerabilă (rețeta — mai multe ieșiri pe o notă —, intrările)"),
    "casa": (NEREGENERABIL, "operațiunea de casă e chiar ce a scris omul (suma, contul, documentul)"),
    "chitanta": (NEREGENERABIL, "chitanța e documentul omului; nota ei se reface anulând chitanța"),
    "extras": (NEREGENERABIL, "nota extrasului poartă alocarea liniei aleasă de om la reconciliere"),
    "compensare": (NEREGENERABIL, "compensarea e actul omului (facturile alese, suma)"),
    "raport_z": (NEREGENERABIL, "nota raportului Z poartă sumele tastate / importate ale Z-ului (numerar, card, cote)"),
    "salarii_alt": (NEREGENERABIL, "notă pe sursa salarii fără documentul statului (SAL LL/AAAA)"),
    "amortizare_alt": (NEREGENERABIL, "notă pe sursa amortizare fără numărul lunii (AMORT-AAAA-LL)"),
}

#: `inregistrari.sursa` scrisă de aplicație -> felurile de documente din care poate deriva nota (`felul`); () = nederivată (nota manuală,
#: notele din Operațiuni — jurnalul e calea lor de corectare, `note_derivate`). Păzit: o sursă nouă scrisă în cod fără rând aici pică.
SURSA_NOTEI = {
    "manual": (),
    "operatiuni": (),
    "facturi": ("factura", "factura_emisa", "borderou", "plata_factura", "plata_borderou", "compensare"),
    "banca": ("extras", "plata_factura", "plata_borderou", "compensare"),
    "casa": ("casa", "chitanta", "plata_factura", "plata_borderou"),
    "stocuri": ("stoc_iesire", "stoc_retur", "inventar", "stoc_alt", "nir"),
    "salarii": ("salarii", "salarii_alt"),
    "amortizare": ("amortizare", "amortizare_alt"),
    "bon": ("raport_z",),
    "horeca_z": ("raport_z",),
    "amef": ("raport_z",),
    "inchidere_an": ("inchidere_an",),
}

_RE_SAL = re.compile(r"^SAL (\d{2})/(\d{4})$")
_RE_AMORT = re.compile(r"^AMORT-(\d{4})-(\d{2})$")


class Neregenerabila(Exception):
    """Sursa nu mai poate scrie nota acum: ciorna e depășită cu motivul acesta."""


#: ce ar scrie sursa ACUM: `data` / `document` None = nu se compară (rămâne a notei); `document_generat` = tipul documentului intern generat
#: (orice număr al lui e la zi); `unde` = sursa, cum o numește contabilul; `refacere` = eticheta butonului de refacere
Acum = namedtuple("Acum", "data document document_generat linii unde refacere")


def _q(schema):
    return '"%s".' % str(schema).strip('"') if schema else ""


def _rand(cur, sql, *p):
    cur.execute(sql, p)
    r = cur.fetchone()
    if r is None:
        return None
    return dict(r) if isinstance(r, dict) else dict(zip([d[0] for d in cur.description], r))


def _bani(x):
    return Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _linii(randuri):
    return sorted((str(d).strip(), str(c).strip(), _bani(s)) for d, c, s in randuri)


def felul(cur, schema, nota_id):
    """Felul sursei din care derivă nota (cheia din `SURSE`), sau None (notă manuală / din Operațiuni — nederivată)."""
    from core import inchidere_an as _ia, note_derivate as _nd, stocuri_cv_api as _cva
    n = _rand(cur, "SELECT sursa, numar FROM %sinregistrari WHERE id = %%s" % _q(schema), nota_id)
    if not n:
        return None
    if n["sursa"] == _ia.SURSA:
        return "inchidere_an"
    doc = _nd.documentul_sursa(cur, schema, nota_id)
    if not doc:
        return None
    fel = doc[0]
    if fel == "stoc":
        p = _cva.propunere_nota_miscare(cur, schema, nota_id)
        if p:
            return "stoc_" + p["fel"]
        m = _rand(cur, "SELECT count(*) AS n, bool_or(document = 'inventar') AS inv FROM %smiscari_stoc WHERE inregistrare_id = %%s"
                  % _q(schema), nota_id)
        return "inventar" if m and m["inv"] else "stoc_alt"
    if fel == "factura":
        f = _rand(cur, "SELECT f.directie FROM %sfacturi f JOIN %sinregistrari i ON i.factura_id = f.id WHERE i.id = %%s"
                  % (_q(schema), _q(schema)), nota_id)
        return "factura_emisa" if f and f["directie"] == "emisa" else "factura"
    if fel == "salarii":
        return "salarii" if _RE_SAL.match(str(n["numar"] or "").strip()) else "salarii_alt"
    if fel == "amortizare":
        return "amortizare" if _RE_AMORT.match(str(n["numar"] or "").strip()) else "amortizare_alt"
    return fel


def _acum_salarii(conn, cur, schema, n):
    from core import salarii_contare as _sc
    m = _RE_SAL.match(str(n["numar"]).strip())
    luna, an = int(m.group(1)), int(m.group(2))
    try:
        p = _sc.propunere(conn, schema, an, luna)
    except ValueError as e:
        raise Neregenerabila("statul de plată %02d/%d nu se mai poate contabiliza acum: %s" % (luna, an, e))
    data, _nr, _descr, document = _sc.antet_nota(an, luna)
    return Acum(data, document, None, _linii((x["debit"], x["credit"], x["suma"]) for x in p["note"]),
                "statul de plată %02d/%d" % (luna, an), "Refă nota din statul de plată")


def _acum_amortizare(conn, cur, schema, n):
    from core import amortizare_lunii as _al, uc_comun as _uc
    m = _RE_AMORT.match(str(n["numar"]).strip())
    an, luna = int(m.group(1)), int(m.group(2))
    try:
        rand = _al.linii(cur, schema, an, luna)
    except ValueError as e:
        raise Neregenerabila(str(e))
    if not rand:
        raise Neregenerabila("registrul mijloacelor fixe nu mai are nimic de amortizat în %02d/%d" % (luna, an))
    return Acum(_uc.ultima_zi_a_lunii(an, luna), None, None, _linii((_al.CONT_CHELTUIALA, c, r) for c, r, _d in rand),
                "registrul mijloacelor fixe (amortizarea %02d/%d)" % (luna, an), "Refă nota din registrul mijloacelor fixe")


def _acum_stoc(conn, cur, schema, n):
    from core import stocuri_cv_api as _cva
    p = _cva.propunere_nota_miscare(cur, schema, n["id"])
    if not p:
        raise Neregenerabila("mișcarea de stoc a notei nu mai e o ieșire sau un retur pe un singur articol")
    if p["document"] is None:
        raise Neregenerabila("factura de stornare a returului nu mai există")
    generat = "bon_consum" if p["document"] == _cva.BON_CONSUM_GENERAT else None
    return Acum(p["data"], None if generat else p["document"], generat, _linii(p["linii"]), p["unde"], "Refă nota din mișcarea de stoc")


def _acum_factura_emisa(conn, cur, schema, n):
    from psycopg2.extras import RealDictCursor
    from core import contare_facturi as _cf
    # cursor dict pe aceeași conexiune (aceeași tranzacție, același punct de salvare): contarea citește rândurile pe nume
    with cur.connection.cursor(cursor_factory=RealDictCursor) as c:
        c.execute("SELECT f.* FROM %sfacturi f JOIN %sinregistrari i ON i.factura_id = f.id WHERE i.id = %%s" % (_q(schema), _q(schema)),
                  (n["id"],))
        f = c.fetchone()
        if not f:
            raise Neregenerabila("factura notei nu mai există")
        try:
            note = _cf.note_propuse(c, schema, dict(f))[1]
        except _cf.RefuzContare as e:
            raise Neregenerabila("factura nu se mai poate contabiliza acum: %s" % e)
    from core import eticheta_nota as _et
    return Acum(None, None, None, _linii((x["debit"], x["credit"], x["suma"]) for x in note),
                _et.factura_din_rand(dict(f)), "Refă nota din factură")


REGENERATOARE = {"factura_emisa": _acum_factura_emisa, "salarii": _acum_salarii, "amortizare": _acum_amortizare, "stoc_iesire": _acum_stoc, "stoc_retur": _acum_stoc}


def _fmt_linii(linii):
    from core import pdf_util as _pu
    return "; ".join("%s = %s %s" % (d, c, _pu.bani(s)) for d, c, s in linii)


def _diferente(n, linii_nota, acum):
    """Ce ar fi altfel acum, în cuvintele contabilului: [(ce, acum, pe ciornă)]; listă goală = la zi."""
    from core import documente_interne as _di, pdf_util as _pu
    out = []
    if acum.data is not None and str(n["data"]) != str(acum.data):
        out.append(("data", _pu.data_ro(acum.data), _pu.data_ro(n["data"])))
    doc = str(n["document_ref"] or "").strip()
    if acum.document_generat:
        if not _di.e_generat(doc, acum.document_generat):
            out.append(("documentul justificativ", "%s (generat odată cu nota)" % _di.TIPURI[acum.document_generat], doc or "fără document"))
    elif acum.document is not None and doc != str(acum.document).strip():
        out.append(("documentul justificativ", "«%s»" % acum.document, "«%s»" % doc if doc else "fără document"))
    if linii_nota != acum.linii:
        noi = [x for x in acum.linii if x not in linii_nota] or acum.linii
        vechi = [x for x in linii_nota if x not in acum.linii] or linii_nota
        out.append(("rândurile", _fmt_linii(noi), _fmt_linii(vechi)))
    return out


def verifica(conn, cur, schema, nota_id):
    """None (nota nu e o ciornă derivată regenerabilă, sau e la zi) ori afirmația `neconformitate` a ciornei depășite (`_depasita`:
    `cod`, `mesaj`, `sursa_fel`, `sursa`, `diferente`: [{ce, acum, pe_ciorna}], `neregenerabila`, `refacere`: {eticheta, actiune}).
    Nu scrie nimic."""
    from core import eticheta_nota as _et, pdf_util as _pu
    n = _rand(cur, "SELECT id, data, numar, status, document_ref, sursa, creat_la FROM %sinregistrari WHERE id = %%s" % _q(schema),
              nota_id)
    if not n or n["status"] != "ciorna":
        return None
    fel = felul(cur, schema, nota_id)
    if fel not in REGENERATOARE:
        return None
    et = _et.nota(cur, schema, nota_id)
    creat = _pu.data_ro(n["creat_la"].date() if hasattr(n["creat_la"], "date") else n["creat_la"])
    refacere = {"eticheta": None, "actiune": ACTIUNE_REFACERE}
    # regenerarea PE USCAT: într-un punct de salvare anulat după ea — orice ar scrie o funcție a sursei, nu rămâne; o eroare a ei nu strică
    # tranzacția apelantului (validarea). FAIL-CLOSED: o regenerare care cade nu lasă ciorna să treacă necomparată (motivul se spune).
    import psycopg2 as _pg
    cur.execute("SAVEPOINT ciorna_pe_uscat")
    try:
        acum = REGENERATOARE[fel](conn, cur, schema, n)
        cur.execute("ROLLBACK TO SAVEPOINT ciorna_pe_uscat")
    except (Neregenerabila, _pg.Error, ValueError, KeyError, TypeError) as e:
        cur.execute("ROLLBACK TO SAVEPOINT ciorna_pe_uscat")
        if not isinstance(e, Neregenerabila):
            from core import observare as _obs
            _obs.esec_secundar("regenerarea pe uscat a notei %s (%s)" % (nota_id, fel), e)
            e = Neregenerabila("regenerarea din sursă a căzut (%s) — eroarea e consemnată" % type(e).__name__)
        return _depasita(nota_id, et, fel, None, None, [], True,
                         "Nota %s a fost generată pe %s, după regula de atunci, iar sursa ei nu o mai poate scrie acum: %s. Nota e depășită "
                         "și nu se validează — corectează sursa, apoi generează nota din nou." % (et, creat, e))
    cur.execute("SELECT cont_debit, cont_credit, suma FROM %sinregistrari_linii WHERE inregistrare_id = %%s" % _q(schema), (nota_id,))
    linii_nota = _linii(tuple(r.values()) if isinstance(r, dict) else tuple(r) for r in cur.fetchall())
    dif = _diferente(n, linii_nota, acum)
    if not dif:
        return None
    refacere["eticheta"] = acum.refacere
    ce = "; ".join("%s %s (pe ciornă: %s)" % (d, a, v) for d, a, v in dif)
    return _depasita(nota_id, et, fel, acum.unde, refacere, [{"ce": d, "acum": a, "pe_ciorna": v} for d, a, v in dif], False,
                     "Nota %s a fost generată pe %s după o regulă care s-a schimbat de atunci: acum %s ar scrie %s. Nota e depășită și nu se "
                     "validează — refă-o din %s („%s”), apoi valideaz-o." % (et, creat, acum.unde, ce, acum.unde, acum.refacere))


def _depasita(nota_id, eticheta, fel, sursa, refacere, diferente, neregenerabila, mesaj):
    """Ciorna depășită, ca AFIRMAȚIE TIPATĂ (`neconformitate`: valoarea — ciorna — nu satisface regula — sursa de acum; P8, decizia din
    21.08.2026), cu ce trebuie ecranului: `sursa` (cum o numește contabilul), `diferente`, `refacere` (butonul), `neregenerabila`."""
    from core.afirmatii import afirmatie
    from core.unde import Unde
    return dict(afirmatie("neconformitate", tip="ciorna_depasita", motiv=mesaj, unde=Unde("inregistrare", nota_id, eticheta),
                          regula=str(TEMEI), cod=COD, mesaj=mesaj, sursa_fel=fel, sursa=sursa, refacere=refacere,
                          diferente=diferente, neregenerabila=neregenerabila))


def refuz_validare(conn, cur, schema, nota_id):
    """Refuzul validării (dict pentru `jurnal_api._refuz` + cod) sau None. Apelat din `jurnal_api.valideaza` — drumul unic."""
    return verifica(conn, cur, schema, nota_id)


def reface_factura_emisa(conn, schema, nota_id):
    """Refacerea din sursă a ciornei de contare a unei facturi EMISE, pe drumul care o scrie (`contare_facturi.contabilizeaza`, actul omului):
    ciorna veche scoasă (`note_derivate.sterge_ciorna_inlocuita`: numai o ciornă; elementul ei din coadă cade odată cu ea), nota nouă scrisă
    din factura de acum, la DATA ciornei vechi (contarea istorică rămâne la data ei) și cu descrierea ei (mențiunea datei și motivul scris de
    om). Întoarce id-ul notei noi; ValueError cu motivul pentru contabil dacă factura nu se mai poate contabiliza. Nu comite."""
    from psycopg2.extras import RealDictCursor
    from core import contare_facturi as _cf, note_derivate as _nd
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT id, data, descriere, factura_id, status FROM %sinregistrari WHERE id = %%s" % _q(schema), (nota_id,))
        n = cur.fetchone()
        if not n or n["status"] != "ciorna" or not n["factura_id"]:
            raise ValueError("Nota nu mai e o ciornă de contare a unei facturi: nu e nimic de refăcut.")
        _nd.sterge_ciorna_inlocuita(cur, schema, nota_id)
        try:
            r = _cf.contabilizeaza(cur, schema, n["factura_id"], automat=False, data_nota=n["data"])
        except _cf.RefuzContare as e:
            raise ValueError("Nota nu se reface: contarea facturii e refuzată acum — %s" % e.mesaj)
        if r.get("stare") != "contata":
            raise ValueError("Factura are deja altă notă de contare: nota depășită nu se reface peste ea.")
        cur.execute("UPDATE %sinregistrari SET descriere = %%s WHERE id = %%s AND status = 'ciorna'" % _q(schema),
                    (n["descriere"], r["inregistrare_id"]))
        return r["inregistrare_id"]


def an_luna(cur, schema, nota_id):
    """(an, luna) din numărul notei statului (SAL LL/AAAA) sau al amortizării (AMORT-AAAA-LL); None altfel. Pentru refacere."""
    n = _rand(cur, "SELECT numar FROM %sinregistrari WHERE id = %%s" % _q(schema), nota_id)
    nr = str((n or {}).get("numar") or "").strip()
    m = _RE_SAL.match(nr)
    if m:
        return int(m.group(2)), int(m.group(1))
    m = _RE_AMORT.match(nr)
    if m:
        return int(m.group(1)), int(m.group(2))
    return None
