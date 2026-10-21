# -*- coding: utf-8 -*-
"""core/artefacte.py — R45: locul UNIC in care se pastreaza un artefact produs.

Decizia lui Costin, 25.08.2026: *"Se pastreaza, cu: artefactul insusi, momentul, autorul,
amprenta continutului, si numarul exemplarului. Iar daca e o declaratie, plus verdictul de
validare cu amprenta fisierului validat. Un artefact produs si nepastrat nu se poate apara.
E chiar P4."*

UN SINGUR loc, nu patru. Cele patru artefacte care asteptau (situatiile financiare, fisierul
de plata a salariilor, exportul contabil, auditul de preluare) au aceeasi cauza si aceeasi
reparatie — patru implementari ar fi insemnat patru vocabulare pentru acelasi lucru, si
patru feluri de a le strica separat.

CE NU FACE, declarat:
  - nu decide CE se pastreaza: felul si cheia vin de la apelant;
  - nu valideaza continutul — doar il amprenteaza;
  - nu sterge si nu suprascrie NICIODATA. Al doilea exemplar e un fapt (P4), deci se adauga
    cu numar nou. Un artefact pastrat nu se poate rescrie prin modulul asta.

"""
# [E2b, 15.09.2026] Tranzactia e a APELANTULUI: `db.get_conn` comite la iesirea din bloc, iar un
# `commit` aici ar taia tranzactia lui in doua (P4). Depozitul primeste conexiunea si scrie; nu
# deschide, nu comite.
from core.db import SchemaInvalida as _SchemaInvalida
import base64
import hashlib

from core import db
from core import chei_unice as _chei   # [lotul 10, C73 / U2] exemplarul dat de aplicație: cursa se reia, nu dă 500

# Vocabular FIX. Un fel nou se adauga AICI, nu la locul apelului — altfel apar variante
# orfane la o litera gresita, si nu se mai poate intreba „cate s-au produs".
FELURI = {
    "s1003": "situatii financiare anuale S1003",
    "s1005": "situatii financiare anuale S1005",
    "plata_salarii": "fisier de plata a salariilor, catre banca",
    "export_saga": "export contabil SAGA",
    "export_winmentor": "export contabil WinMentor",
    "audit_preluare": "verdictul auditului de preluare",
    # [deficiența 221, decizia Costin 11.10.2026] coloana „An precedent” completată de contabil când firma nu are în aplicație
    # bilanțul anului precedent: cine, când, ce cifre (JSON pe secțiuni) — exemplarele vechi rămân (P4)
    "bilant_an_precedent": "coloana „An precedent” a bilantului, completata manual",
}
# Felurile care poarta si verdict de validare (declaratii). Restul il lasa NULL.
CU_VERDICT = ("s1003", "s1005")


def amprenta(continut):
    """sha256 al continutului BRUT. Un artefact e despre UN continut, nu despre un moment.
    Pe binar (un zip de export) se amprenteaza octetii, nu reprezentarea lor."""
    if isinstance(continut, bytes):
        return hashlib.sha256(continut).hexdigest()
    return hashlib.sha256((continut or "").encode("utf-8")).hexdigest()


def _pentru_coloana(continut):
    """Binarul se pastreaza in base64, nu prin `decode(errors="replace")` — aia ar strica
    octetii tacut, iar artefactul pastrat n-ar mai fi cel produs."""
    if isinstance(continut, bytes):
        return base64.b64encode(continut).decode("ascii")
    return continut


def pastreaza(conn, schema, fel, cheie, continut, produs_de_id=None, produs_de=None,
              verdict=None, verdict_versiune=None, verdict_amprenta=None):
    """Pastreaza un artefact produs. Intoarce {ok, id, exemplar, amprenta}.

    `cheie` = contextul care il identifica in interiorul felului (anul, an-luna, id-ul
    firmei preluate). Exemplarul creste pe (fel, cheie): al doilea S1003 pe 2026 e
    exemplarul 2, nu o suprascriere a primului.
    """
    if fel not in FELURI:
        return {"ok": False, "cod": "FEL_NECUNOSCUT",
                "mesaj": "fel de artefact necunoscut: %r" % fel}
    if not db.schema_valida(schema):
        raise _SchemaInvalida(schema)
    amp = amprenta(continut)
    with conn.cursor() as cur:
        # [lotul 11.10.2026, găsit la 221: „completată manual de 1968”] Autorul se scrie cu NUMELE lui: apelanții treceau
        # `ctx.get("nume") or str(uid)`, iar contextul cererii n-are „nume” — deci în `produs_de` ajungea id-ul. Numele se ia aici, o dată
        # pentru toți apelanții, din `public.users` (prenume + nume, altfel e-mailul); textul apelantului rămâne numai dacă utilizatorul
        # nu se găsește.
        if produs_de_id is not None:
            cur.execute("SELECT COALESCE(NULLIF(trim(concat_ws(' ', prenume, nume)), ''), email) FROM public.users WHERE id = %s",
                        (produs_de_id,))
            r = cur.fetchone()
            if r and r[0]:
                produs_de = r[0]
        def _scrie():
            cur.execute('SELECT COALESCE(max(exemplar), 0) + 1 FROM "%s".artefacte_produse '
                        "WHERE fel = %%s AND cheie = %%s" % schema, (fel, str(cheie)))
            exemplar = cur.fetchone()[0]
            # `verdict_la` = now() DOAR daca exista verdict; altfel NULL. Un moment de validare
            # pe un artefact nevalidat ar fi o afirmatie despre ceva ce nu s-a intamplat.
            cur.execute(
                'INSERT INTO "%s".artefacte_produse '
                "(fel, cheie, exemplar, continut, amprenta, produs_de_id, produs_de, "
                " verdict, verdict_la, verdict_versiune, verdict_amprenta) "
                "VALUES (%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s,"
                "        CASE WHEN %%s::text IS NULL THEN NULL ELSE now() END,"
                "        %%s,%%s) RETURNING id" % schema,
                (fel, str(cheie), exemplar,
                 _pentru_coloana(continut), amp, produs_de_id, produs_de,
                 verdict, verdict,
                 verdict_versiune, verdict_amprenta))
            return cur.fetchone()[0], exemplar
        # [lotul 10, C73 / U2] exemplarul îl dă APLICAȚIA (`max + 1` pe fel și cheie): două produceri simultane ale aceluiași artefact
        # (ex. S1003 generat de două ori deodată) citeau același număr, iar a doua cădea cu 500 pe `artefacte_exemplar_unic`. Cursa se
        # reia cu exemplarul următor — al doilea exemplar e un fapt (P4), nu o greșeală a omului.
        aid, exemplar = _chei.reincearca_la_dublura(cur, ("artefacte_exemplar_unic",), _scrie, lambda cur, e: _chei.CheieDublata(
            "Artefactul %s nu s-a putut păstra: prea multe produceri simultane ale lui. Produ-l din nou." % FELURI[fel]))
    return {"ok": True, "id": aid, "exemplar": exemplar, "amprenta": amp}


def lista(conn, schema, fel=None, cheie=None):
    """Ce s-a produs, in ordine. Fara continut — ala se cere pe id."""
    if not db.schema_valida(schema):
        raise _SchemaInvalida(schema)
    cond, val = [], []
    if fel:
        cond.append("fel = %s"); val.append(fel)
    if cheie is not None:
        cond.append("cheie = %s"); val.append(str(cheie))
    unde = (" WHERE " + " AND ".join(cond)) if cond else ""
    with conn.cursor() as cur:
        cur.execute('SELECT id, fel, cheie, exemplar, amprenta, produs_la, produs_de, '
                    "verdict, verdict_la, verdict_versiune, verdict_amprenta "
                    'FROM "%s".artefacte_produse%s ORDER BY produs_la DESC, id DESC'
                    % (schema, unde), val)
        col = [d[0] for d in cur.description]
        return [dict(zip(col, r)) for r in cur.fetchall()]


def primul_si_ultimul(conn, schema, fel):
    """[deficiența 370, comanda Costin 8.2: „primul audit după preluare rămâne păstrat și vizibil (dovada a ce s-a primit de la contabilul
    anterior), alături de ultimul”] (primul, ultimul, numar) — fiecare {id, produs_la, produs_de, continut} sau None; ultimul e None când
    există un singur exemplar (e chiar primul)."""
    if not db.schema_valida(schema):
        raise _SchemaInvalida(schema)
    with conn.cursor() as cur:
        cur.execute('SELECT count(*) FROM "%s".artefacte_produse WHERE fel = %%s' % schema, (fel,))
        n = cur.fetchone()[0]
        out = []
        for ordine in ("ASC", "DESC"):
            cur.execute('SELECT id, produs_la, produs_de, continut FROM "%s".artefacte_produse WHERE fel = %%s '
                        "ORDER BY produs_la %s, id %s LIMIT 1" % (schema, ordine, ordine), (fel,))
            r = cur.fetchone()
            out.append({"id": r[0], "produs_la": r[1].isoformat() if r[1] else None, "produs_de": r[2], "continut": r[3]} if r else None)
    primul, ultimul = out
    if primul and ultimul and primul["id"] == ultimul["id"]:
        ultimul = None
    return primul, ultimul, n
