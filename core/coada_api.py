# [patch_coada_user_id] fundatie user_id
"""
core/coada_api.py — coada de validare a declarațiilor (public.declaratii_coada).
Flux: asistent generează -> 'la_senior' -> senior aprobă/respinge -> depusă.

Separarea responsabilităților (RBAC în main): angajatul adaugă, admin_firma
aprobă/respinge/depune. Asta e controlul fiscal — nimic nu se depune nevalidat.

Tranzițiile de stare + hash-ul sunt PURE (testabile). Restul e DB.
Constrângerea ux_coada_activa din DB blochează o a doua intrare activă pentru
aceeași (tenant, tip, perioadă) — prindem eroarea și întoarcem mesaj clar.
"""
from __future__ import annotations
import hashlib
import json
import datetime as _dt

from core import scadente

REGULI = "2026.1"
MODUL = "coada_api"

# acțiune -> (stare_necesară, stare_rezultată)
TRANZITII = {
    "aproba": ("la_senior", "aprobata"),
    "respinge": ("la_senior", "respinsa"),
    "depune": ("aprobata", "depusa"),
}

#: Stările pe care le poate avea un element din coadă — DERIVATE din tabela de mai sus, ca să
#: nu existe o a doua listă care rămâne în urmă. Filtrul din `GET /coada` se verifică pe ele.
STARI = tuple(sorted({s for t in TRANZITII.values() for s in t}))


# ============================================================
#  TRANZIȚII DE STARE — PURE
# ============================================================
def poate_tranzitiona(stare_curenta, actiune):
    """True dacă acțiunea e permisă din starea curentă. Pură."""
    t = TRANZITII.get(actiune)
    return bool(t) and stare_curenta == t[0]


def stare_dupa(actiune):
    """Starea rezultată după acțiune, sau None. Pură."""
    t = TRANZITII.get(actiune)
    return t[1] if t else None


# ============================================================
#  HASH payload — PUR (integritate)
# ============================================================
def calcul_hash(payload):
    """SHA256 din payload (serializat determinist). Pură."""
    s = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _chei_serializabile(x):
    """Recursiv: cheile care nu sunt `str` devin JSON (listă pentru tuplu, valoare altfel).

    De ce nu `str(cheie)`: `str(("C", 1))` dă `"('C', 1)"` — un text din care componentele nu se mai
    pot scoate fără să parsezi Python. Cu `json.dumps` cheia rămâne **citibilă înapoi**, iar cine
    confruntă două declarații poate întreba „ce tip de operațiune e" fără ghicit."""
    if isinstance(x, dict):
        out = {}
        for k, v in x.items():
            if not isinstance(k, str):
                k = json.dumps(list(k) if isinstance(k, tuple) else k, default=str)
            out[k] = _chei_serializabile(v)
        return out
    if isinstance(x, (list, tuple)):
        return [_chei_serializabile(v) for v in x]
    return x


def randuri_din_res(res):
    """[F163v2] Serializează `res` (dataclass) -> dict JSON-safe (Decimal->str via default=str)
    pentru payload/jsonb (persistare în public.declaratii_depuse.randuri). PURĂ.

    **d112 NU mai e excepția, din 30.08.2026 (R105).** Textul de aici spunea, din 22.07.2026, că
    `d112.genereaza` întoarce `(xml, avertismente)` cu o LISTĂ pe poziția a doua, deci `randuri`
    rămâne NULL — și că refactorizarea *„e o decizie de arhitectură pe modulul validat DUK (F181),
    NU se face aici"*. **Amânarea era corectă și avea condiție scrisă; condiția s-a îndeplinit:**
    Costin a dat decizia pe 30.08.2026 — *„R105: motorul se schimbă"* — iar `_d112_genereaza`
    întoarce acum `RezultatD112`.

    **Efectul, scris fiindcă nu e evident:** de la commitul acela, D112 își persistă rândurile în
    `public.declaratii_depuse.randuri`, ca celelalte declarații. Depunerile de DINAINTE rămân cu
    `randuri` NULL — nu se completează retroactiv, fiindcă n-ar fi ce s-a depus, ci ce s-ar depune
    azi.

    **[02.09.2026] CHEILE TUPLU — un D394 cu operațiuni nu putea fi trimis în coadă deloc.**
    `Rezultat`-ul D394 ține `op1`, `rezumat1` și `detaliu` cu **chei tuplu**
    (`(tip, tip_partener, cota, cuiP, denP)`), iar `json.dumps` ridică pe orice cheie care nu e
    `str/int/float/bool/None`. Apelul din `main.py` (`POST /coada`) e negardat, deci cererea ieșea
    **500** — și se aprindea exact pe firmele care aveau ce declara, fiindcă pe `op1` gol
    serializarea trecea. *Un defect care tace pe firmele goale și lovește pe cele reale.*

    **Cheia tuplu devine un JSON de listă**, nu un șir lipit cu separator: componentele includ
    denumirea partenerului, iar orice separator ales ar putea apărea în ea. Așa cheia rămâne
    **reversibilă** (`json.loads(cheie)` întoarce componentele) și nu se poate ciocni.

    Ce rămâne adevărat din textul vechi: funcția e PURĂ, iar ce nu e dataclass -> None."""
    import dataclasses
    if not dataclasses.is_dataclass(res):
        return None
    return json.loads(json.dumps(_chei_serializabile(dataclasses.asdict(res)), default=str))


# ============================================================
#  ADĂUGARE în coadă — DB
# ============================================================
def adauga_in_coada(conn, cabinet_id, tenant_id, tip, an, payload,
                    creat_de, luna=None, trim=None, coerenta=None, creat_de_id=None,
                    inceput_la=None):  # [p15]
    """
    Pune o declarație generată în coadă, stare 'la_senior'.
    perioada = data scadenței (zz/ll/aaaa), calculată din tip+an+luna/trim.
    payload (jsonb) conține xml + avertismente + randuri (res serializat, F163v2; None la
    d112) + an/luna/trim pentru depunere ulterioară. Cheia `randuri` se persistă în
    public.declaratii_depuse la marcheaza_depusa (control D-vs-D fără reparsare XML).
    Întoarce {ok, coada_id, perioada} sau {ok:False, cod} dacă există deja o
    intrare activă (constrângerea ux_coada_activa).
    """
    import psycopg2
    import psycopg2.extras as _E
    # [R44] O declaratie legata de o firma care nu exista sta in coada fara ca nimic s-o
    # semnaleze — masurat: 1 din 3 elemente. `declaratii_coada` n-are cheie straina catre
    # `public.tenants` (firmele traiesc si ca scheme, iar tabela e partajata), deci refuzul
    # se scrie aici, unde e singura poarta de intrare in coada.
    with conn.cursor() as _cur:
        _cur.execute("SELECT 1 FROM public.tenants WHERE id = %s", (tenant_id,))
        if _cur.fetchone() is None:
            return {"ok": False, "cod": "FIRMA_INEXISTENTA",
                    "mesaj": "firma #%s nu există — o declarație nu poate intra în coadă "
                             "legată de o firmă ștearsă sau necreată" % tenant_id}
    # [C2/C11, 07.10.2026] `perioada` = scadența, când modulul de scadențe o are SURSATĂ. Un tip fără termen sursat (31 din 52 la
    # 07.10: bilanțul și declarațiile anuale cu formular) intra în coadă cu 500 („scadenta: lipsește luna sau trim”) — deci
    # nicio declarație anuală cu formular nu putea fi depusă prin aplicație. Nu se GHICEȘTE un termen: se pune perioada de
    # raportare („anul 2025”); termenul lipsă e datorie (`core/test_datorie.py`), nu o valoare inventată.
    perioada = (scadente.scadenta(tip, an, luna=luna, trim=trim) if scadente.are_termen(tip, an, luna=luna, trim=trim)
                else "anul %d" % an if (luna is None and trim is None)
                else "%s %d" % ("luna %02d" % luna if luna else "T%d" % trim, an))
    # asigurăm an/luna în payload pentru declaratii_depuse la depunere
    payload = {**(payload or {}), "_an": an, "_luna": luna, "_trim": trim}
    h = calcul_hash(payload)
    try:
        with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
            cur.execute(
                "INSERT INTO public.declaratii_coada "
                "(cabinet_id, tenant_id, tip, perioada, stare, coerenta, payload, hash, creat_de, creat_de_id, inceput_la) "  # [p15]
                "VALUES (%s,%s,%s,%s,'la_senior',%s,%s,%s,%s,%s,%s) RETURNING id",
                (cabinet_id, tenant_id, tip, perioada, coerenta,
                 _E.Json(payload), h, creat_de, creat_de_id, inceput_la))  # [p15]
            coada_id = cur.fetchone()["id"]
        return {"ok": True, "coada_id": coada_id, "perioada": perioada}
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return {"ok": False, "cod": "DEJA_IN_COADA",
                "mesaj": "există deja o declarație activă %s pentru perioada %s" % (tip, perioada)}


# ============================================================
#  NOTELE — coada extinsă (comanda Costin 06.10.2026, pct.1, varianta (a))
# ============================================================
#: cheia elementului unei note: o notă are cel mult UN element activ (indexul `ux_coada_activa` pe tenant, tip, perioadă)
TIP_NOTA = "nota"


def perioada_nota(nota_id):
    return "nota-%d" % int(nota_id)


#: [lotul 07.10 pct.4, comanda Costin 06.10.2026] „Retrimiterea nu e o pregătire nouă.” O PREGĂTIRE = un document pregătit:
#: declarația pe firma, tipul și perioada ei; nota pe documentul ei (`payload.grup`, vezi `grup_nota`) — oricâte rânduri a lăsat în
#: coadă (respinsă, retrimisă, validată). Expresia SQL e una, aici; o folosesc toate numărătorile de „pregătite” (calitatea
#: asistentului, Capacitate, Activitate cabinet, sinteza zilnică). Gard: `core/test_pregatiri.py`.
def sql_cheie_pregatire(alias=""):
    a = (alias + ".") if alias else ""
    return ("(%stenant_id::text || '|' || %sfel || '|' || %stip || '|' || CASE WHEN %sfel = 'nota' "
            "THEN COALESCE(%spayload->>'grup', %sperioada) ELSE %sperioada END)") % ((a,) * 7)


def grup_nota(nota_id, grup_doc=None):
    """[lotul 07.10 pct.9, comanda Costin 06.10.2026] Cheia DOCUMENTULUI pe care cabinetul îl validează: „O factură produce două
    note de validat separat (contare + ieșire stoc). Cabinetul validează sau respinge documentul o dată.” Cheia vine din
    `_GRUP_DOC` (SQL, o singură definiție): notele aceleiași facturi (contarea și ieșirile din stoc) -> `factura-<id>`; [lotul
    07.10 B, C8] cele 4 note ale unui NIR -> `nir-<id>`. Orice altă notă e propriul ei document (`nota-<id>`). Fiecare notă își
    păstrează rândul în coadă (triggerul de sincronizare cu jurnalul rămâne pe notă); cheia leagă rândurile în listă, la
    validare, la respingere și la numărare."""
    return str(grup_doc) if grup_doc else perioada_nota(nota_id)


def eticheta_element(fel, tip, perioada, payload):
    """PURĂ. Cum se numește un element din coadă oriunde apare (listă, notificare, Activitate cabinet) — o singură formă.
    Declarația: „D300 · <scadența>”. Nota: „Notă · <descriere> · <document>”."""
    if fel == "nota":
        p = payload or {}
        descr = [str(d or "").strip() or "fără descriere" for d in (p.get("descrieri") or [p.get("descriere")])]
        doc = (p.get("document_ref") or "").strip()
        if len(descr) > 1:
            # [retest 07.10 R2, comanda Costin] un document cu mai multe note se numește SCURT: „NIR nr 1 din 07.10.2026 · DANTE
            # INTERNATIONAL SA · 4 note” — documentul, partenerul, câte note. Descrierile (aceeași, repetată pe fiecare notă) nu
            # mai intră în titlu; notele se văd la „Vezi notele”.
            return " · ".join(x for x in [doc or "Document", (p.get("partener") or "").strip(), "%d note" % len(descr)] if x)
        parti = ["Notă", descr[0]]
        # [lotul 07.10 pct.13] documentul nu se repetă când descrierea îl spune deja (fără diacritice, fără majuscule)
        if doc and _fara_diacritice(doc) not in _fara_diacritice(descr[0]) and _fara_diacritice(descr[0]) not in _fara_diacritice(doc):
            parti.append(doc)
        return " · ".join(parti)
    return "%s · %s" % ((tip or "").upper(), perioada or "")


def _fara_diacritice(t):
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFKD", str(t or "")) if not unicodedata.combining(c)).lower().strip()


def e_validator(conn, user_id):
    """Are utilizatorul dreptul de validare? Cine îl are nu „pregătește pentru altcineva”: notele lui nu intră în coadă."""
    with conn.cursor() as cur:
        cur.execute("SELECT poate_valida FROM public.users WHERE id = %s", (user_id,))
        r = cur.fetchone()
    return bool(r and r[0])


def _payload_nota(n):
    """Documentul justificativ se DERIVĂ cu aceeași funcție ca în Registrul-jurnal (`jurnal_api.document_justificativ`:
    `document_ref`, altfel factura legată) — coada nu poate spune „fără document” despre o notă pe care jurnalul o arată cu
    document."""
    from core import jurnal_api as _j
    d = n["data"]
    doc = _j.document_justificativ(n["document_ref"], n.get("f_tip"), n.get("f_serie"), n.get("f_nr"), n.get("f_data"))
    p = {"inregistrare_id": n["id"], "data": d.isoformat(), "descriere": n["descriere"], "sursa": n["sursa"],
         "document_ref": doc, "total": str(n["total"]), "_an": d.year, "_luna": d.month,
         "partener": n.get("partener"), "stinge": n.get("stinge"),   # [08.10, U5]
         "grup": grup_nota(n["id"], n.get("grup_doc"))}
    # [retest 07.10 seara, S3] documentul notei, documentul pe care îl reface (NIR-ul refăcut: cel respins) și amprenta notei —
    # din ele cardul din coadă spune „retrimisă după respingere”, motivul anterior și dacă nota s-a schimbat
    p["doc"] = cheie_document(p)
    p["doc_anterior"] = ("nir-%d" % int(n["nir_refacut_din"])) if n.get("nir_refacut_din") else p["doc"]
    p["amprenta"] = n.get("amprenta")
    return p


def cheie_document(p):
    """[S3] Documentul unei note din coadă, din payload (o singură definiție; și migrarea o folosește): factura / NIR-ul
    (`grup`); o notă automată (`sursa`, ex. statul de plată) — documentul ei justificativ; altfel nota însăși."""
    g = str(p.get("grup") or "")
    if g.startswith(("factura-", "nir-")):
        return g
    if (p.get("sursa") or "manual") != "manual" and p.get("document_ref"):
        return "doc:%s:%s" % (p["sursa"], p["document_ref"])
    return perioada_nota(p.get("inregistrare_id")) if p.get("inregistrare_id") else g


def ciornele_documentului(cur, schema, grup):
    """[S3] Notele CIORNĂ ale unui document (cheia `_GRUP_DOC`, ex. `factura-12`), pe schema firmei."""
    cur.execute('SET LOCAL search_path TO "%s", public' % str(schema).strip('"'))
    cur.execute("SELECT i.id FROM inregistrari i WHERE (" + _GRUP_DOC + ") = %s AND i.status = 'ciorna' ORDER BY i.id", (grup,))
    return [(x[0] if not isinstance(x, dict) else x["id"]) for x in cur.fetchall()]


def amprente_note(cur, nota_ids, schema=None):
    """[S3] Amprentele notelor (lista sortată). `schema` gol = schema din calea conexiunii."""
    ids = [int(i) for i in nota_ids or []]
    if not ids:
        return []
    a = _AMPRENTA if not schema else _AMPRENTA.replace("inregistrari_linii", '"%s".inregistrari_linii' % str(schema).strip('"'))
    cur.execute("SELECT " + a + " FROM %sinregistrari i WHERE i.id = ANY(%%s)" % (('"%s".' % str(schema).strip('"')) if schema else ""),
                (ids,))
    return sorted((x[0] if not isinstance(x, dict) else list(x.values())[0]) for x in cur.fetchall())


def motiv_respingere(cur, schema, nota_id):
    """[S3] Motivul ultimei respingeri a notei (elementul ei din coadă), pe firma schemei (gol = schema conexiunii)."""
    cur.execute("SELECT c.motiv_respingere FROM public.declaratii_coada c JOIN public.tenants t ON t.id = c.tenant_id "
                "WHERE t.schema_name = COALESCE(NULLIF(%s, ''), current_schema()) AND c.fel = 'nota' AND c.perioada = %s "
                "AND c.stare = 'respinsa' ORDER BY c.id DESC LIMIT 1", (str(schema or "").strip('"'), perioada_nota(nota_id)))
    r = cur.fetchone()
    return (r[0] if not isinstance(r, dict) else r["motiv_respingere"]) if r else None


COD_NESCHIMBATA = "NESCHIMBATA"
MESAJ_NESCHIMBATA = ("Nimic nu s-a schimbat de la respingere: nota scrisă acum e aceeași cu cea respinsă (motivul respingerii: „%s”). "
                     "Retrimiți totuși aceeași notă la validare?")


def avertisment_neschimbata(vechi, noi, motiv, confirmat):
    """[S3, comanda Costin] „dacă recontabilizarea produce aceeași notă ca cea respinsă, asistentul vede un avertisment («nimic nu
    s-a schimbat de la respingere», cu motivul alături) și confirmă explicit; nu se blochează.” Întoarce avertismentul (cererea
    de confirmare) sau None. `vechi` / `noi` = amprentele documentului respins și ale celui scris acum."""
    if confirmat or not vechi or sorted(vechi) != sorted(noi):
        return None
    return {"ok": False, "cod": COD_NESCHIMBATA, "cere_confirmare": True, "motiv": motiv,
            "mesaj": MESAJ_NESCHIMBATA % (motiv or "fără motiv")}


def retrimisa(cur, tenant_id, membri):
    """[S3] Pentru cardul din coadă: documentul acestor elemente reface unul RESPINS? -> {motiv, la, schimbata (True / False /
    None = necunoscut: nota respinsă n-avea amprentă)}; altfel None. `motiv_respingere` = același nume ca la `stari_note`. `membri` = [(coada_id, payload)]."""
    p0 = (membri[0][1] or {}) if membri else {}
    doc = p0.get("doc_anterior")
    if not doc:
        return None
    cur.execute("SELECT id, motiv_respingere, payload->>'amprenta', respins_la FROM public.declaratii_coada WHERE tenant_id = %s "
                "AND fel = 'nota' AND stare = 'respinsa' AND payload->>'doc' = %s AND id < %s ORDER BY respins_la DESC, id DESC",
                (tenant_id, doc, min(m[0] for m in membri)))
    rows = [tuple(x.values()) if isinstance(x, dict) else tuple(x) for x in cur.fetchall()]
    if not rows:
        return None
    ultima = [x for x in rows if (x[3], x[1]) == (rows[0][3], rows[0][1])]   # același act de respingere (tot documentul)
    vechi = [x[2] for x in ultima]
    noi = [(m[1] or {}).get("amprenta") for m in membri]
    schimbata = None if (None in vechi or None in noi) else (sorted(vechi) != sorted(noi))
    return {"motiv_respingere": ultima[0][1], "la": ultima[0][3].isoformat() if ultima[0][3] else None, "schimbata": schimbata}


def _insereaza_nota(cur, cabinet_id, tenant_id, n, uid):
    import psycopg2.extras as _E
    payload = _payload_nota(n)
    cur.execute(
        "INSERT INTO public.declaratii_coada (cabinet_id, tenant_id, tip, fel, perioada, stare, payload, hash, creat_de, "
        "creat_de_id) VALUES (%s,%s,%s,'nota',%s,'la_senior',%s,%s,%s,%s) ON CONFLICT DO NOTHING RETURNING id",
        (cabinet_id, tenant_id, TIP_NOTA, perioada_nota(n["id"]), _E.Json(payload), calcul_hash(payload), str(uid), uid))
    r = cur.fetchone()
    if not r:
        return None
    return r["id"] if isinstance(r, dict) else r[0]


#: [lotul 07.10 B, C8] Documentul notei, o singură definiție (lista, retrimiterea și migrarea `migrare_grup_coada` o folosesc):
#:   · factura: contarea ei (`sursa='facturi'`, `inregistrari.factura_id`) și ieșirile din stoc făcute de pe ea (`miscari_stoc`);
#:     o PLATĂ legată de factură (bancă, casă) e alt document (extrasul, registrul de casă) — nu intră în grupul facturii;
#:   · NIR: notele lui (`nir.inregistrari_ids`) — 371=401, 4426=401, 371=378, 371=4428 sunt un singur document.
_GRUP_DOC = ("CASE WHEN i.sursa IN ('facturi', 'stocuri') AND COALESCE(i.factura_id, (SELECT ms.factura_id FROM miscari_stoc ms "
             "WHERE ms.inregistrare_id = i.id AND ms.factura_id IS NOT NULL ORDER BY ms.id LIMIT 1)) IS NOT NULL "
             "THEN 'factura-' || COALESCE(i.factura_id, (SELECT ms.factura_id FROM miscari_stoc ms WHERE ms.inregistrare_id = i.id "
             "AND ms.factura_id IS NOT NULL ORDER BY ms.id LIMIT 1)) "
             "ELSE (SELECT 'nir-' || n.id FROM nir n WHERE n.inregistrari_ids @> to_jsonb(i.id) ORDER BY n.id LIMIT 1) END")

#: [retest 07.10 R2] Partenerul documentului, pentru titlul elementului din coadă: al facturii (legată de notă sau de ieșirea din
#: stoc a notei), altfel furnizorul NIR-ului. O singură definiție (lista, notificarea, migrarea titlurilor existente).
_PARTENER = ("COALESCE(f.tert_nume, (SELECT f2.tert_nume FROM miscari_stoc ms JOIN facturi f2 ON f2.id = ms.factura_id "
             "WHERE ms.inregistrare_id = i.id ORDER BY ms.id LIMIT 1), (SELECT n.furnizor FROM nir n "
             "WHERE n.inregistrari_ids @> to_jsonb(i.id) ORDER BY n.id LIMIT 1))")

#: [retest 07.10 seara, S3] AMPRENTA notei: data + liniile (debit / credit / sumă), în ordine — „aceeași notă” înseamnă aceeași
#: amprentă. Se păstrează în payload-ul elementului, ca o notă respinsă și apoi ștearsă la înlocuire să poată fi comparată.
_AMPRENTA = ("md5(i.data::text || ':' || COALESCE((SELECT string_agg(l.cont_debit || '/' || l.cont_credit || '/' || l.suma::text, ';' "
             "ORDER BY l.cont_debit, l.cont_credit, l.suma) FROM inregistrari_linii l WHERE l.inregistrare_id = i.id), ''))")

_SELECT_NOTE = ("SELECT i.id, i.data, i.descriere, i.sursa, i.document_ref, f.tip AS f_tip, f.serie AS f_serie, "
                "f.numar AS f_nr, f.data_emitere AS f_data, "
                + _GRUP_DOC + " AS grup_doc, " + _PARTENER + " AS partener, " + _AMPRENTA + " AS amprenta, "
                "(SELECT n.refacut_din_id FROM nir n WHERE n.inregistrari_ids @> to_jsonb(i.id) ORDER BY n.id LIMIT 1) AS nir_refacut_din, "
                "(SELECT COALESCE(SUM(l.suma), 0) FROM inregistrari_linii l WHERE l.inregistrare_id = i.id) AS total "
                "FROM inregistrari i LEFT JOIN facturi f ON f.id = i.factura_id ")


def pune_notele_in_coada(conn, cabinet_id, tenant_id, uid):
    """Notele CIORNĂ scrise de `uid` pe firmă care n-au încă niciun element în coadă intră acum, una câte una, `la_senior`.
    `conn` e pe schema firmei (`db.get_conn(schema)`, care are și `public` în cale). O notă respinsă NU se repune singură:
    revine numai prin `retrimite_nota` — altfel o respingere s-ar anula la următoarea apăsare a asistentului.
    Întoarce lista elementelor adăugate: [{coada_id, eticheta}]."""
    import psycopg2.extras as _E
    out = []
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(_SELECT_NOTE + "WHERE i.status = 'ciorna' AND i.creat_de_id = %s AND NOT EXISTS ("
                    "SELECT 1 FROM public.declaratii_coada c WHERE c.tenant_id = %s AND c.fel = 'nota' "
                    "AND c.perioada = 'nota-' || i.id) ORDER BY i.id", (uid, tenant_id))
        note = [dict(n) for n in cur.fetchall()]
        from core import jurnal_api as _j   # [08.10, U5] factura stinsă de chitanța notei, pe cardul din coadă
        _st = _j.facturi_stinse(cur, None, [n["id"] for n in note])
        for n in note:
            n["stinge"] = _st.get(n["id"])
        grupuri = {}
        for n in note:
            cid = _insereaza_nota(cur, cabinet_id, tenant_id, n, uid)
            if cid:
                pl = _payload_nota(n)
                grupuri.setdefault(pl["grup"], []).append((cid, pl))
        # [lotul 07.10 pct.9] un document = un element de anunțat (contarea + ieșirea din stoc a aceleiași facturi = unul)
        for membri in grupuri.values():
            out.append({"coada_id": membri[0][0], "eticheta": eticheta_element("nota", TIP_NOTA, None, _payload_grup(membri))})
    return out


def _payload_grup(membri):
    """Payload-ul unui document cu una sau mai multe note: [(coada_id, payload)] -> payload-ul primului + descrieri + total."""
    from decimal import Decimal as _D
    p = dict(membri[0][1])
    if len(membri) > 1:
        p["descrieri"] = [m[1].get("descriere") for m in membri]
        p["total"] = str(sum(_D(str(m[1].get("total") or 0)) for m in membri))
        p["note"] = [m[1] for m in membri]
    return p


def membri_grup(cur, coada_id, stare="la_senior"):
    """[lotul 07.10 pct.9] Rândurile documentului din care face parte elementul `coada_id` (inclusiv el), în `stare`, în
    ordinea id-ului: [(id, payload)]. Un element fără grup (declarație, notă singură) e singurul membru al documentului lui.
    `stare=None` = starea elementului însuși (conținutul unui document, oricare i-ar fi starea)."""
    cur.execute("SELECT tenant_id, fel, payload->>'grup' AS grup, stare FROM public.declaratii_coada WHERE id = %s", (coada_id,))
    r = cur.fetchone()
    if not r:
        return []
    tenant_id, fel, grup, st = (r["tenant_id"], r["fel"], r["grup"], r["stare"]) if isinstance(r, dict) else r
    stare = st if stare is None else stare
    if fel != "nota" or not grup:
        cur.execute("SELECT id, payload FROM public.declaratii_coada WHERE id = %s", (coada_id,))
    else:
        cur.execute("SELECT id, payload FROM public.declaratii_coada WHERE tenant_id = %s AND fel = 'nota' "
                    "AND payload->>'grup' = %s AND stare = %s ORDER BY id", (tenant_id, grup, stare))
    return [((x["id"], x["payload"]) if isinstance(x, dict) else (x[0], x[1])) for x in cur.fetchall()]


def retrimite_nota(conn, cabinet_id, tenant_id, nota_id, uid, confirma=False):
    """O notă RESPINSĂ, corectată, se trimite din nou la validare — act explicit al celui care a pregătit-o.
    [S3] Nota neschimbată față de cea respinsă (aceeași amprentă) cere confirmare explicită (`confirma`); nu se blochează."""
    import psycopg2.extras as _E
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(_SELECT_NOTE + "WHERE i.id = %s", (nota_id,))
        n = cur.fetchone()
        if not n:
            return {"ok": False, "cod": "INEXISTENT", "mesaj": "nota #%s nu există" % nota_id}
        cur.execute("SELECT status FROM inregistrari WHERE id = %s", (nota_id,))
        if cur.fetchone()["status"] != "ciorna":
            return {"ok": False, "cod": "STARE_GRESITA", "mesaj": "numai o notă ciornă se trimite la validare"}
        cur.execute("SELECT stare, payload->>'amprenta' AS amprenta, motiv_respingere FROM public.declaratii_coada "
                    "WHERE tenant_id = %s AND fel = 'nota' AND perioada = %s ORDER BY id DESC LIMIT 1", (tenant_id, perioada_nota(nota_id)))
        ultim = cur.fetchone()
        if ultim and ultim["stare"] != "respinsa":
            return {"ok": False, "cod": "DEJA_IN_COADA", "mesaj": "nota e deja la validare sau validată"}
        from core import stocuri_anulare as _sa   # [retest 07.10 R1] documentul cu stocul stornat se reface, nu se retrimite
        _st = _sa.document_stornat(cur, None, nota_id)
        if _st:
            return {"ok": False, "cod": _sa.COD_DOCUMENT_STORNAT, "mesaj": _sa.MESAJ_NOTA_STORNATA % _st}
        if ultim:
            _av = avertisment_neschimbata([ultim["amprenta"]] if ultim["amprenta"] else [], [n["amprenta"]],
                                          ultim["motiv_respingere"], confirma)
            if _av:
                return _av
        # [lotul 07.10 pct.9] documentul se retrimite ÎNTREG: celelalte ciorne ale aceleiași facturi, respinse odată cu ea
        grup = grup_nota(n["id"], n.get("grup_doc"))
        frati = [n]
        if grup != perioada_nota(n["id"]):
            cur.execute(_SELECT_NOTE + "WHERE i.status = 'ciorna' AND i.id <> %s ORDER BY i.id", (nota_id,))
            for x in cur.fetchall():
                if grup_nota(x["id"], x.get("grup_doc")) != grup:
                    continue
                cur.execute("SELECT stare FROM public.declaratii_coada WHERE tenant_id = %s AND fel = 'nota' AND perioada = %s "
                            "ORDER BY id DESC LIMIT 1", (tenant_id, perioada_nota(x["id"])))
                u = cur.fetchone()
                if not u or u["stare"] == "respinsa":
                    frati.append(x)
        membri = []
        for x in frati:
            cid = _insereaza_nota(cur, cabinet_id, tenant_id, x, uid)
            if cid:
                membri.append((cid, _payload_nota(x)))
    return {"ok": bool(membri), "coada_id": membri[0][0] if membri else None,
            "eticheta": eticheta_element("nota", TIP_NOTA, None, _payload_grup(membri) if membri else _payload_nota(n))}


#: [lotul 07.10 pct.6, comanda Costin 06.10.2026] „Cât timp nota e la validare, asistentul o poate edita sau șterge; cabinetul ar
#: valida altceva decât a văzut.” Nota la validare NU se modifică și NU se șterge, pe niciun drum (jurnal: editare, ștergere;
#: casa: ștergerea operațiunii cu nota ei; dezlegarea de factură). Calea de corectare: cabinetul o respinge cu motiv.
MESAJ_NOTA_LA_VALIDARE = ("Nota #%s e la validare în cabinet: cât timp așteaptă, nu se modifică și nu se șterge — cabinetul "
                          "validează exact ce a văzut. Dacă trebuie corectată, cabinetul o respinge cu motiv, iar după "
                          "corectare o trimiți din nou.")
COD_NOTA_LA_VALIDARE = "NOTA_LA_VALIDARE"


def nota_la_validare(cur, schema, nota_id):
    """Ultimul element din coadă al notei e `la_senior`? Pe schema firmei (orice cursor; `public` e calificat)."""
    cur.execute("SELECT c.stare FROM public.declaratii_coada c JOIN public.tenants t ON t.id = c.tenant_id "
                "WHERE t.schema_name = %s AND c.fel = 'nota' AND c.perioada = %s ORDER BY c.id DESC LIMIT 1",
                (str(schema).strip('"'), perioada_nota(nota_id)))
    r = cur.fetchone()
    st = (r["stare"] if isinstance(r, dict) else r[0]) if r else None
    return st == "la_senior"


def stari_note(conn, tenant_id, nota_ids):
    """{nota_id: {stare_coada, motiv_respingere, la}} — ultimul element din coadă al fiecărei note (jurnalul și statul de plată îl arată)."""
    ids = [int(i) for i in nota_ids or []]
    if not ids:
        return {}
    with conn.cursor() as cur:
        cur.execute("SELECT DISTINCT ON (perioada) perioada, stare, motiv_respingere, "
                    "COALESCE(respins_la, aprobat_la, creat_la) FROM public.declaratii_coada "
                    "WHERE tenant_id = %s AND fel = 'nota' AND perioada = ANY(%s) ORDER BY perioada, id DESC",
                    (tenant_id, [perioada_nota(i) for i in ids]))
        return {int(p.split("-", 1)[1]): {"stare_coada": st, "motiv_respingere": m, "la": la.isoformat() if la else None}
                for p, st, m, la in cur.fetchall()}


# ============================================================
#  LISTĂ coadă — DB
# ============================================================
def lista_coada(conn, cabinet_id, stare=None):
    """Declarațiile din coadă pentru un cabinet, opțional filtrate pe stare."""
    import psycopg2.extras as _E
    cond, val = ["cabinet_id = %s"], [cabinet_id]
    if stare is not None:
        cond.append("stare = %s"); val.append(stare)
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            "SELECT c.id, c.tenant_id, c.tip, c.perioada, c.stare, c.coerenta, c.creat_de, "
            "c.creat_la, c.aprobat_de, c.respins_de, c.motiv_respingere, "
            # [perioada_declarata_v1] perioada DECLARATA (an/luna/trim din payload), separata de
            # c.perioada = data scadentei (termen). Consumatorii existenti ai lui `perioada` NU se strica.
            "(c.payload->>'_an')::int   AS p_an, "
            "(c.payload->>'_luna')::int AS p_luna, "
            "(c.payload->>'_trim')::int AS p_trim, "
            "COALESCE(u.nume, u.email) AS creat_de_nume, "  # [val_nume_v1] numele pregatitorului, nu UID brut
            # [R41 partea II] verdictul oficial ajunge in lista, ca ecranul sa nu-si mai
            # inventeze o eticheta. XML-ul NU se intoarce - doar amprenta lui, calculata aici.
            "c.verdict, c.verdict_erori, c.verdict_amprenta, c.verdict_la, c.verdict_versiune, "
            "c.trecere_motiv, c.trecut_la, c.fel, "
            "CASE WHEN c.fel = 'nota' THEN c.payload END AS nota, "
            "c.payload->>'xml' AS _xml, c.payload->'confirmare_atentionari' AS _conf "
            "FROM public.declaratii_coada c "
            "LEFT JOIN public.users u ON u.id = c.creat_de_id "
            "WHERE " + " AND ".join("c." + x for x in cond) +
            " ORDER BY c.creat_la DESC", val)
        out = []
        for r in cur.fetchall():
            d = dict(r)
            xml = d.pop("_xml", None)
            d["verdict_stare"] = verdict_din_rand(
                d.pop("verdict", None), d.pop("verdict_erori", None),
                d.pop("verdict_amprenta", None), d.pop("verdict_la", None),
                d.pop("verdict_versiune", None), xml, d.pop("_conf", None))
            d["gata_de_depus"] = gata_de_depus(d["verdict_stare"])
            out.append(d)
        # [lotul 07.10 pct.9-10] notele aceluiași document, în aceeași stare, sunt UN element (o validare, o cifră)
        grupate, vazute = [], {}
        for d in out:
            g = (d.get("nota") or {}).get("grup") if d["fel"] == "nota" else None
            cheie = (d["tenant_id"], g, d["stare"]) if g else None
            if cheie and cheie in vazute:
                vazute[cheie]["membri"].append(d)
                continue
            if cheie:
                d["membri"] = [d]
                vazute[cheie] = d
            grupate.append(d)
        for d in grupate:
            membri = d.pop("membri", None)
            if membri and len(membri) > 1:
                membri.sort(key=lambda m: m["id"])
                d["nota"] = _payload_grup([(m["id"], m["nota"]) for m in membri])
                d["id"] = membri[0]["id"]
                d["membri_ids"] = [m["id"] for m in membri]
            d["eticheta"] = eticheta_element(d["fel"], d["tip"], d["perioada"], d.get("nota"))
            if d["fel"] == "nota" and d["stare"] == "la_senior":
                # [S3] „cardul unei note retrimise arată «retrimisă după respingere», motivul respingerii anterioare și dacă
                # nota s-a schimbat față de cea respinsă”
                _m = [(m["id"], m["nota"]) for m in membri] if membri and len(membri) > 1 else [(d["id"], d.get("nota"))]
                d["retrimisa"] = retrimisa(cur, d["tenant_id"], _m)
        return grupate


def _stare_curenta(cur, coada_id):
    cur.execute("SELECT stare FROM public.declaratii_coada WHERE id = %s", (coada_id,))
    r = cur.fetchone()
    return r[0] if r else None


# ============================================================
#  APROBARE / RESPINGERE — DB (verifică tranziția)
# ============================================================
def validatori_activi(conn, cabinet_id, exclude_id=None):
    """[po_efectiv_v1] SURSA UNICA a multimii „cine poate aproba in acest cabinet" -> lista de id-uri.

    Aceeasi intrebare era pusa in TREI locuri, cu trei interogari proprii (coada_api: count pentru
    aplicabilitate; asistenti_api._nr_validatori: count pentru educatie; notificari_api: lista de
    destinatari). Trei copii care puteau diverge tacit: educatia ar fi propus patru-ochi acolo unde
    enforcement-ul nu-l aplica, sau notificarea ar fi mers la cine nu poate aproba. Acum toate trei
    deriva de aici."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id FROM public.users "
            " WHERE accounting_firm_id = %s AND activ = true AND poate_valida = true",
            (cabinet_id,))
        ids = [r[0] for r in cur.fetchall()]
    if exclude_id is not None:
        ids = [i for i in ids if i != exclude_id]
    return ids


def patru_ochi_posibil(conn, cabinet_id):
    """APLICABILITATE (axa automata, calculata live): patru-ochi se poate aplica DOAR daca
    cabinetul are >=2 validatori activi.

    De ce >=2 VALIDATORI, si nu formula veche ">=1 pregatitor + >=1 validator + >=2 oameni"
    (pana la 20.08.2026): enforcement-ul (`aproba` mai jos) blocheaza EXCLUSIV auto-aprobarea
    (pregatitor == aprobator). Cu un SINGUR validator, orice lucrare pregatita chiar de el nu mai
    poate fi aprobata de nimeni -> DEADLOCK, fara iesire din aplicatie.
    Scenariul concret care il producea (cabinet 1968, audit tenant_006): patron singur validator,
    3 declaratii pregatite de el in coada; se angajeaza un asistent DOAR cu `poate_pregati` ->
    formula veche dadea posibil=True (1 pregatitor, 1 validator, 2 oameni) si cele 3 declaratii
    deveneau neaprobabile de oricine.
    Formula noua nu pierde nicio protectie: un al doilea om FARA drept de validare nu putea
    oricum aproba nimic, deci vechea conditie nu gardase niciodata vreo lucrare in plus.
    Vezi DECIZII 20.08.2026 (patru-ochi: politica explicita x aplicabilitate automata).
    """
    return len(validatori_activi(conn, cabinet_id)) >= 2


def patru_ochi_activ(conn, cabinet_id):
    """Patronul a activat patru-ochi pentru acest cabinet?"""
    with conn.cursor() as cur:
        cur.execute("SELECT patru_ochi_activ FROM public.accounting_firms WHERE id = %s",
                    (cabinet_id,))
        r = cur.fetchone()
    return bool(r[0]) if r and r[0] is not None else False


def patru_ochi_stare(conn, cabinet_id):
    """SURSA UNICA a starii patru-ochi - consumata SI de enforcement SI de UI (GET /eu/patru-ochi).

      activ   = POLITICA explicita a patronului (flag persistat, setat din UI)
      posibil = APLICABILITATEA aritmetica, calculata live (>=2 validatori activi)
      efectiv = activ AND posibil = ce se aplica DE FAPT

    Exista pentru ca UI-ul citea flagul brut `activ` si afisa "Validarea in doi ✓" pe un cabinet
    cu un singur validator, in timp ce `aproba` folosea deja `activ AND posibil` -> indicator
    MINCINOS (audit tenant_006 / cabinet Prisma 1968, 20.08.2026). Front si back nu mai pot
    diverge: amandoua citesc de aici.
    """
    activ = patru_ochi_activ(conn, cabinet_id)
    posibil = patru_ochi_posibil(conn, cabinet_id)
    return {"activ": activ, "posibil": posibil, "efectiv": bool(activ and posibil)}


def amprenta_xml(xml):
    """Amprenta continutului validat. [R41] Un verdict e despre UN XML, nu despre un moment."""
    import hashlib
    return hashlib.sha256((xml or "").encode("utf-8")).hexdigest()


def scrie_verdict(conn, coada_id, rez, versiune, xml):
    """Persista verdictul oficial: rezultat, erori, moment, versiunea validatorului, amprenta.

    [R41] Se cheama de acolo de unde DEJA se rula validatorul (`GET /coada/{id}/continut`). Nu se
    adauga o a doua rulare: se pastreaza cea care se facea si se arunca."""
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE public.declaratii_coada SET verdict=%s, verdict_erori=%s, verdict_la=now(), "
            "verdict_versiune=%s, verdict_amprenta=%s WHERE id=%s",
            ((rez or {}).get("stare"), (rez or {}).get("erori") or None,
             versiune, amprenta_xml(xml), coada_id))
    return {"ok": True}


def verdict_din_rand(verdict, erori, amp, la, versiune, xml, confirmare=None):
    """PURA. Starea verdictului pentru un rand deja citit: `proaspat` | `statut` | `lipsa`.

    `statut` = exista un verdict, dar pe ALT continut decat cel din coada acum. Se trateaza ca
    ABSENT, nu ca favorabil (P6: necunoscutul domina favorabilul). Fara distinctia asta, o
    regenerare tacuta ar pastra un verdict care nu mai e despre nimic.

    [R41 partea II] Extrasa ca functie pura fiindca o cheama DOUA locuri: poarta care refuza
    depunerea (`verdict_stare`) si lista pe care o vede omul (`lista_coada`). A doua
    implementare ar fi putut diverge tacit de prima - adica ecranul ar fi aratat verde exact
    acolo unde serverul refuza."""
    if not verdict or not amp:
        return {"stare": "lipsa", "motiv": "nu s-a păstrat niciun verdict pentru elementul ăsta",
                "actiune": "deschide elementul în ecranul de validare — validatorul rulează și verdictul se păstrează"}
    acum = amprenta_xml(xml or "")
    if amp != acum:
        return {"stare": "statut", "verdict": verdict, "motiv":
                "verdictul e pe alt conținut decât cel din coadă (XML-ul s-a regenerat între timp)",
                "actiune": "redeschide elementul ca să fie validat conținutul CURENT",
                "amprenta_verdict": amp[:16], "amprenta_acum": acum[:16]}
    # [comanda Costin 07.10.2026, C3] „O atenționare DUK nu oprește coada: se afișează și cere confirmarea scrisă a contabilului.
    # O eroare DUK oprește.” DUK pune ORICE ieșire în `erori`; severitatea o dă `duk.severitate` (A: / E:, fail-safe spre
    # eroare). Confirmarea ține numai cât XML-ul e același: e legată de amprenta conținutului confirmat.
    from core import duk as _duk
    sev = _duk.severitate(erori) if verdict == "erori" else None
    conf = bool(confirmare and confirmare.get("amprenta") == acum)
    return {"stare": "proaspat", "verdict": verdict, "erori": erori, "la": la,
            "versiune": versiune, "severitate": sev, "atentionari_confirmate": conf,
            "confirmare": ({k: confirmare.get(k) for k in ("text", "de_id", "la")} if conf else None)}


def gata_de_depus(v):
    """PURA. Singura definitie a lui «gata de depus», folosita si de poarta, si de ecran.

    [R41 partea II] Pana azi ecranul isi alegea singur populatia listei „De depus"; poarta din
    server avea alta regula. Doua definitii ale aceleiasi propozitii = ecranul putea numi „de
    depus" ceva ce serverul refuza. Acum e una."""
    if not v or v.get("stare") != "proaspat":
        return False
    if v.get("verdict") == "valid":
        return True
    # [C3, 07.10.2026] atenționările (fără nicio linie de eroare), confirmate în scris pe ACEST conținut
    return v.get("verdict") == "erori" and v.get("severitate") == "atentionare" and bool(v.get("atentionari_confirmate"))


def verdict_stare(conn, coada_id):
    """Starea verdictului pentru un element din coada. Citeste randul si deleaga calculul."""
    with conn.cursor() as cur:
        cur.execute("SELECT verdict, verdict_erori, verdict_amprenta, verdict_la, verdict_versiune, "
                    "payload->>'xml', payload->'confirmare_atentionari' FROM public.declaratii_coada WHERE id=%s", (coada_id,))
        r = cur.fetchone()
    if r is None:
        return {"stare": "lipsa", "motiv": "element inexistent",
                "actiune": "verifică id-ul elementului din coadă"}
    return verdict_din_rand(*r)


def confirma_atentionari(conn, coada_id, motiv, cine_id):
    """[C3, 07.10.2026] Confirmarea scrisă a atenționărilor DUK, legată de amprenta XML-ului din coadă: textul, cine, când.
    Un XML regenerat (altă amprentă) nu mai e confirmat — se citește din nou."""
    with conn.cursor() as cur:
        cur.execute("SELECT payload->>'xml' FROM public.declaratii_coada WHERE id=%s", (coada_id,))
        r = cur.fetchone()
        # textul confirmării = act al omului (cine, când), nu o afirmație despre datele firmei
        conf = {"text": str(motiv).strip()[:500], "de_id": cine_id, "la": _dt.datetime.now().isoformat(timespec="seconds"),
                "amprenta": amprenta_xml((r or [""])[0] or "")}
        cur.execute("UPDATE public.declaratii_coada SET payload = jsonb_set(payload, '{confirmare_atentionari}', %s::jsonb, true) "
                    "WHERE id=%s", (json.dumps(conf, ensure_ascii=False), coada_id))
    return conf


def _poarta_verdict(conn, coada_id, actiune, motiv, cine_id):
    """Refuza actiunea daca verdictul lipseste, e statut, sau nu e `valid` - afara de cazul in care
    se trece EXPLICIT, cu motiv, si trecerea se CONSEMNEAZA.

    [R41] «gata de depus» nu se poate defini fara verdict pastrat. Un buton care confirma depunerea
    a ceva nevalidat nu e o scurtatura, e o afirmatie falsa despre starea lucrului."""
    st = verdict_stare(conn, coada_id)
    # [R41 partea II] Aceeasi functie pe care o foloseste lista pe care o vede omul.
    # Poarta si ecranul nu pot diverge fiindca nu exista doua conditii, ci una.
    if gata_de_depus(st):
        return None
    if st.get("stare") == "proaspat" and st.get("verdict") == "erori":
        if st.get("severitate") != "atentionare":
            # [C3, 07.10.2026] „O eroare DUK oprește.” Fără portiță: motivul scris nu mai trece peste un verdict cu erori.
            return {"ok": False, "cod": "ERORI_DUK",
                    "mesaj": "nu pot %s: validatorul oficial ANAF a găsit erori — declarația ar fi respinsă la depunere" % actiune,
                    "actiune": "corectează ce semnalează validatorul și generează din nou", "verdict": st}
        if not motiv or not str(motiv).strip():
            return {"ok": False, "cod": "ATENTIONARI_NECONFIRMATE",
                    "mesaj": "nu pot %s: validatorul oficial a semnalat atenționări, pe care nu le-a confirmat nimeni în scris" % actiune,
                    "actiune": "citește atenționările și confirmă-le în scris (de ce declarația e corectă așa)", "verdict": st}
        confirma_atentionari(conn, coada_id, motiv, cine_id)
        return None
    if not motiv or not str(motiv).strip():
        return {"ok": False, "cod": "FARA_VERDICT",
                "mesaj": "nu pot %s: %s" % (
                    actiune, st.get("motiv") or "validatorul a raportat '%s'" % st.get("verdict")),
                "actiune": st.get("actiune") or "deschide elementul ca să fie validat, sau treci peste explicit, cu motiv scris",
                "verdict": st}
    with conn.cursor() as cur:
        cur.execute("UPDATE public.declaratii_coada SET trecere_motiv=%s, trecut_de_id=%s, "
                    "trecut_la=now() WHERE id=%s", (str(motiv).strip()[:500], cine_id, coada_id))
    return None


def aproba(conn, coada_id, aprobat_de, aprobat_de_id=None, motiv_trecere=None, cabinet_id_apelant=None, schema_nota=None):
    """la_senior -> aprobata. Refuză dacă starea nu permite SAU dacă
    aprobatorul e chiar pregătitorul (control „patru ochi").

    [B1, 17.09.2026] APARTENENȚA PE OBIECT: `cabinet_id_apelant` = cabinetul care cere acțiunea
    (`ctx["firm"]`). Dacă elementul aparține ALTUI cabinet, se refuză cu `ALT_CABINET` — mapat la 404
    în stratul HTTP, ca elementul altui cabinet să nu-și dezvăluie nici existența. Până azi doar
    `_are_permisiune` verifica DREPTUL apelantului, nu PROPRIETATEA elementului, iar `GET /continut`
    era singura rută scoped; aproba/respinge/depune lucrau pe orice `coada_id`."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT stare, creat_de, creat_de_id, cabinet_id, fel, payload FROM public.declaratii_coada WHERE id = %s",  # [p54_4ochi]
            (coada_id,))
        r = cur.fetchone()
        if r is None:
            return {"ok": False, "cod": "INEXISTENT",
                    "mesaj": "declarația nu mai e în coadă (id %s): a fost ștearsă, depusă de altcineva, sau id-ul e greșit" % (coada_id,)}
        st, creat_de, creat_de_id, _cabinet_id = r[0], r[1], r[2], r[3]  # [p54_4ochi]
        if cabinet_id_apelant is not None and _cabinet_id != cabinet_id_apelant:
            return {"ok": False, "cod": "ALT_CABINET",  # [B1] apartenenta pe OBIECT
                    "mesaj": "element de coadă negăsit (sau alt cabinet)"}
        if not poate_tranzitiona(st, "aproba"):
            return {"ok": False, "cod": "STARE_GRESITA",
                    "mesaj": "nu pot aproba din starea '%s'" % st}
        # [patch_coada_user_id] patru-ochi pe ID (fallback pe text)
        _vinovat = (
            (creat_de_id is not None and aprobat_de_id is not None
             and creat_de_id == aprobat_de_id)
            or (creat_de_id is None and creat_de is not None
                and str(creat_de) == str(aprobat_de))
        )
        # [p54_4ochi] patru-ochi se aplica doar daca patronul l-a activat SI e posibil pe competente
        if _vinovat and patru_ochi_stare(conn, _cabinet_id)["efectiv"]:
            return {"ok": False, "cod": "PATRU_OCHI",
                    "mesaj": "nu poți aproba o declarație pe care ai pregătit-o tu însuți "
                             "(control intern: pregătirea și validarea se fac de persoane diferite)"}
        if r[4] == "nota":
            # [validare_note] Aprobarea unei note = VALIDAREA ei în jurnal, în ACEEAȘI tranzacție (conn e pe schema firmei).
            # Poarta de verdict DUK e a declarațiilor (XML); nota n-are XML. Triggerul de sincronizare vede elementul deja
            # trecut mai jos și nu-l mai atinge.
            if not schema_nota:
                return {"ok": False, "cod": "INEXISTENT", "mesaj": "firma notei nu e accesibilă"}
            from core import jurnal_api as _jurnal
            membri = membri_grup(cur, coada_id)   # [lotul 07.10 pct.9] documentul se validează o dată, cu toate notele lui
            for _mid, _pl in membri:
                rv = _jurnal.valideaza(conn, schema_nota, int((_pl or {}).get("inregistrare_id") or 0))
                if not rv or rv.get("eroare"):
                    return {"ok": False, "cod": "STARE_GRESITA",
                            "mesaj": "nota nu se poate valida: %s" % ((rv or {}).get("eroare") or "nu mai există în jurnal")}
            cur.execute(
                "UPDATE public.declaratii_coada SET stare='aprobata', "
                "aprobat_de=%s, aprobat_de_id=%s, aprobat_la=now() WHERE id = ANY(%s)",
                (aprobat_de, aprobat_de_id, [m[0] for m in membri]))
            return {"ok": True, "stare": "aprobata", "membri": [m[0] for m in membri]}
        else:
            # [R41] Poarta pe verdict vine DUPA patru-ochi: ordinea conteaza, ca mesajul primit sa
            # numeasca primul obstacol real, nu pe al doilea.
            refuz = _poarta_verdict(conn, coada_id, "aproba", motiv_trecere, aprobat_de_id)
            if refuz:
                return refuz
        cur.execute(
            "UPDATE public.declaratii_coada SET stare='aprobata', "
            "aprobat_de=%s, aprobat_de_id=%s, aprobat_la=now() WHERE id=%s",
            (aprobat_de, aprobat_de_id, coada_id))
    return {"ok": True, "stare": "aprobata"}


def auto_aproba_daca_e_cazul(conn, coada_id, aprobat_de, aprobat_de_id=None, motiv_trecere=None,
                             cabinet_id_apelant=None):
    """`la_senior` -> `aprobata`, **numai** cand patru-ochi nu e efectiv. Altfel nu atinge nimic.

    **DE CE EXISTA (02.09.2026, defect gasit apasand).** Inlantuirea „aproba + depune" traia in
    CLIENT: ecranul chema `POST /aproba`, apoi `POST /depune`. Poarta confirmarii traieste in
    `depune` — deci aproba trecea, si poarta cadea **dupa**. Masurat in `uvicorn.log`:

        POST /coada/8052/aproba  -> 200 OK
        POST /coada/8052/depune  -> 409          (constatare CERTA neconfirmata)
        POST /coada/8052/aproba  -> 409          (a doua apasare: "nu pot aproba din starea 'aprobata'")

    **Ce lasa in urma un refuz al portii, in forma veche:** elementul ramane `aprobata`. Din starea
    aia **nu se mai poate RESPINGE** (`respinge` cere `la_senior`), deci refuzul portii ingusta
    optiunile omului — iar contractul spune, scris, ca supervizorul *nu blocheaza niciodata*. Si un
    client care si-a pastrat starea veche re-cheama `aproba` si moare inainte sa ajunga la `depune`.

    **Acum aprobarea e a serverului, si vine DUPA poarta.** Un refuz nu mai misca nimic: elementul
    ramane `la_senior`, respingerea ramane pe masa, iar a doua apasare se comporta ca prima.

    Intoarce `{"ok": True, "sarit": True}` cand n-avea ce aproba — un „n-am facut nimic" explicit,
    nu un `True` care se citeste ca „am aprobat"."""
    with conn.cursor() as cur:
        cur.execute("SELECT stare, cabinet_id FROM public.declaratii_coada WHERE id = %s", (coada_id,))
        r = cur.fetchone()
    if r is None:
        return {"ok": False, "cod": "INEXISTENT",
                "mesaj": "declarația nu mai e în coadă (id %s): a fost ștearsă, depusă de altcineva, sau id-ul e greșit" % (coada_id,)}
    stare, cabinet_id = r[0], r[1]
    if cabinet_id_apelant is not None and cabinet_id != cabinet_id_apelant:
        return {"ok": False, "cod": "ALT_CABINET",  # [B1] apartenenta pe OBIECT
                "mesaj": "element de coadă negăsit (sau alt cabinet)"}
    if stare != "la_senior":
        return {"ok": True, "sarit": True, "stare": stare}
    if patru_ochi_stare(conn, cabinet_id)["efectiv"]:
        # Validarea in doi NU se ocoleste de aici: cand e efectiva, aprobarea e actul altcuiva.
        return {"ok": False, "cod": "CERE_APROBARE",
                "mesaj": "declarația e încă la validare: cu patru-ochi activ, o aprobă un coleg "
                         "înainte de depunere"}
    return aproba(conn, coada_id, aprobat_de, aprobat_de_id, motiv_trecere,
                  cabinet_id_apelant=cabinet_id_apelant)


def respinge(conn, coada_id, respins_de, motiv, respins_de_id=None, cabinet_id_apelant=None, schema_nota=None):
    """la_senior -> respinsa + motiv. Refuză dacă starea nu permite.
    [B1] Apartenența pe obiect: `cabinet_id_apelant` = cabinetul care cere; alt cabinet -> ALT_CABINET.
    [retest 07.10 R1] O NOTĂ respinsă își stornează documentul în fișa de magazie (`stocuri_anulare.storneaza`, pe `schema_nota`),
    în aceeași tranzacție; dacă marfa a ieșit deja, respingerea se refuză (STOC_IESIT) și nu se scrie nimic."""
    # [motiv_obligatoriu_v1] respingerea fără motiv lasă contabilul fără explicație
    if motiv is None or not str(motiv).strip():
        return {"ok": False, "cod": "MOTIV_LIPSA",
                "mesaj": "respingerea necesită un motiv (contabilul trebuie să știe ce să corecteze)"}
    with conn.cursor() as cur:
        cur.execute("SELECT stare, cabinet_id FROM public.declaratii_coada WHERE id = %s", (coada_id,))
        _row = cur.fetchone()
        st = _row[0] if _row else None
        if st is None:
            return {"ok": False, "cod": "INEXISTENT",
                    "mesaj": "declarația nu mai e în coadă (id %s): a fost ștearsă, depusă de altcineva, sau id-ul e greșit" % (coada_id,)}
        if cabinet_id_apelant is not None and _row[1] != cabinet_id_apelant:
            return {"ok": False, "cod": "ALT_CABINET",  # [B1] apartenenta pe OBIECT
                    "mesaj": "element de coadă negăsit (sau alt cabinet)"}
        if not poate_tranzitiona(st, "respinge"):
            return {"ok": False, "cod": "STARE_GRESITA",
                    "mesaj": "nu pot respinge din starea '%s'" % st}
        membri = membri_grup(cur, coada_id) or []
        ids = [m[0] for m in membri] or [coada_id]   # [lotul 07.10 pct.9] tot documentul
        note_ids = [int((p or {}).get("inregistrare_id") or 0) for _i, p in membri if (p or {}).get("inregistrare_id")]
        if note_ids and schema_nota:
            from core import stocuri_anulare as _sa
            grup = (membri[0][1] or {}).get("grup")
            st = _sa.storneaza(conn, schema_nota, grup, note_ids, motiv)
            if st.get("eroare"):
                return {"ok": False, "cod": "STOC_IESIT", "mesaj": st["eroare"]}
        cur.execute(
            "UPDATE public.declaratii_coada SET stare='respinsa', "
            "respins_de=%s, respins_de_id=%s, respins_la=now(), motiv_respingere=%s WHERE id = ANY(%s)",
            (respins_de, respins_de_id, motiv, ids))
    return {"ok": True, "stare": "respinsa", "membri": ids}


# ============================================================
#  DEPUNERE — DB (aprobata -> depusa + jurnal declaratii_depuse)
# ============================================================
def perioada_din_payload(payload):
    """`(an, luna)` pentru jurnal: lunar -> luna; trimestrial -> **luna finală a trimestrului**;
    anual -> 12.

    **SURSĂ UNICĂ, din 02.09.2026.** Derivarea asta trăia doar în `marcheaza_depusa`. De când poarta
    confirmării trebuie să știe *pe ce perioadă se depune* ÎNAINTE de depunere, ar fi existat două
    locuri care răspund la aceeași întrebare — iar al doilea se învechește. *Regula „nu construi
    paralel", aplicată înainte ca paralela să apară.*"""
    p = payload or {}
    an = p.get("_an")
    if p.get("_luna"):
        luna = p["_luna"]
    elif p.get("_trim"):
        luna = p["_trim"] * 3
    else:
        luna = 12
    return an, luna


def firma_si_perioada(conn, coada_id):
    """`(tenant_id, an, luna)` pentru un element din coadă, sau `None` dacă nu există.

    Ce citește poarta confirmării ca să știe **pe ce firmă și pe ce perioadă** se depune — exact
    întrebarea pusă de Costin (02.09): *„o constatare CERTĂ pe firma și perioada care se depune"*."""
    with conn.cursor() as cur:
        cur.execute("SELECT tenant_id, payload FROM public.declaratii_coada WHERE id = %s",
                    (coada_id,))
        r = cur.fetchone()
    if not r:
        return None
    an, luna = perioada_din_payload(r[1])
    return r[0], an, luna
def marcheaza_depusa(conn, coada_id, spv_index=None, depus_de=None, depus_de_id=None,
                     motiv_trecere=None, cabinet_id_apelant=None):
    """
    aprobata -> depusa. Scrie și în declaratii_depuse (jurnal final).
    an/luna se iau din payload (_an/_luna; pt trim/anual: luna finală/12).
    [B1] Apartenența pe obiect: alt cabinet -> ALT_CABINET (nu scrie în declaratii_depuse al altei firme).
    """
    import psycopg2.extras as _E
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute("SELECT stare, tenant_id, tip, payload, cabinet_id FROM public.declaratii_coada "
                    "WHERE id = %s", (coada_id,))
        r = cur.fetchone()
        if not r:
            return {"ok": False, "cod": "INEXISTENT",
                    "mesaj": "declarația nu mai e în coadă (id %s): a fost ștearsă, depusă de altcineva, sau id-ul e greșit" % (coada_id,)}
        if cabinet_id_apelant is not None and r["cabinet_id"] != cabinet_id_apelant:
            return {"ok": False, "cod": "ALT_CABINET",  # [B1] apartenenta pe OBIECT
                    "mesaj": "element de coadă negăsit (sau alt cabinet)"}
        if (r["payload"] or {}).get("inregistrare_id") is not None or r["tip"] == TIP_NOTA:
            return {"ok": False, "cod": "STARE_GRESITA", "mesaj": "o notă contabilă nu se depune; se validează"}
        if not poate_tranzitiona(r["stare"], "depune"):
            return {"ok": False, "cod": "STARE_GRESITA",
                    "mesaj": "nu pot depune din starea '%s'" % r["stare"]}
        # [R41] Depunerea e tranzitia IREVERSIBILA - `depusa` n-are nicio iesire in TRANZITII.
        # Poarta e cu atat mai necesara aici: dupa ea nu se mai poate reveni prin nicio ruta.
        refuz = _poarta_verdict(conn, coada_id, "depune", motiv_trecere, depus_de_id)
        if refuz:
            return refuz
        p = r["payload"] or {}
        an, luna = perioada_din_payload(p)
        cur.execute(
            "UPDATE public.declaratii_coada SET stare='depusa', depus_la=now(), "
            "spv_index=%s, depus_de=%s, depus_de_id=%s WHERE id=%s",
            (spv_index, depus_de, depus_de_id, coada_id))
        # [F163v2 varianta A] persistăm xml + randuri (res serializat, din payload) cu VERSIONARE:
        # nr_depunere = MAX(existente)+1 calculat în ACEEAȘI instrucțiune. Fiecare depunere (inclusiv
        # rectificativa de același tip) = rând nou, cu xml/randuri proprii; "curenta" = nr_depunere
        # maxim (vederea declaratii_depuse_curente). NU mai e ON CONFLICT DO NOTHING (first-write-wins
        # devenea fals fiscal odată ce persistăm valori — vezi DECIZII F163v2). PK-ul
        # (tenant,an,luna,tip,nr_depunere) e garda la cursă: două depuneri concurente care calculează
        # același nr_depunere -> a doua pică pe PK (conflictul NU se înghite tăcut). randuri = jsonb
        # (None la d112 -> SQL NULL).
        randuri = p.get("randuri")
        tip_c = (r["tip"] or "").lower()   # [tip_lowercase] canonic la stocare (cheie de join); CHECK il impune
        cur.execute(
            "INSERT INTO public.declaratii_depuse (tenant_id, an, luna, tip, xml, randuri, nr_depunere) "
            "SELECT %s,%s,%s,%s,%s,%s, COALESCE(MAX(nr_depunere),0)+1 "
            "FROM public.declaratii_depuse WHERE tenant_id=%s AND an=%s AND luna=%s AND tip=%s",
            (r["tenant_id"], an, luna, tip_c, p.get("xml"),
             _E.Json(randuri) if randuri is not None else None,
             r["tenant_id"], an, luna, tip_c))
    return {"ok": True, "stare": "depusa", "an": an, "luna": luna}
