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

from core import scadente

REGULI = "2026.1"
MODUL = "coada_api"

# acțiune -> (stare_necesară, stare_rezultată)
TRANZITII = {
    "aproba": ("la_senior", "aprobata"),
    "respinge": ("la_senior", "respinsa"),
    "depune": ("aprobata", "depusa"),
}


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


def randuri_din_res(res):
    """[F163v2] Serializează `res` (dataclass) -> dict JSON-safe (Decimal->str via default=str)
    pentru payload/jsonb (persistare în public.declaratii_depuse.randuri). PURĂ.

    d112 e EXCEPȚIA: d112.genereaza întoarce (xml, avertismente) unde al 2-lea element e o
    LISTĂ de avertismente, NU un dataclass cu totaluri structurate. Aici -> None (randuri NULL).
    Temeiul: d112 își ține agregatele în variabile de structură XML, nu le expune ca res;
    a-l refactoriza ca să le întoarcă e o decizie de arhitectură pe modulul validat DUK (F181),
    NU se face aici. Vezi DECIZII 22.07 F163v2."""
    import dataclasses
    if not dataclasses.is_dataclass(res):
        return None
    return json.loads(json.dumps(dataclasses.asdict(res), default=str))


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
    perioada = scadente.scadenta(tip, an, luna=luna, trim=trim)
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
            "c.trecere_motiv, c.trecut_la, "
            "c.payload->>'xml' AS _xml "
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
                d.pop("verdict_versiune", None), xml)
            d["gata_de_depus"] = gata_de_depus(d["verdict_stare"])
            out.append(d)
        return out


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


def verdict_din_rand(verdict, erori, amp, la, versiune, xml):
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
    return {"stare": "proaspat", "verdict": verdict, "erori": erori, "la": la,
            "versiune": versiune}


def gata_de_depus(v):
    """PURA. Singura definitie a lui «gata de depus», folosita si de poarta, si de ecran.

    [R41 partea II] Pana azi ecranul isi alegea singur populatia listei „De depus"; poarta din
    server avea alta regula. Doua definitii ale aceleiasi propozitii = ecranul putea numi „de
    depus" ceva ce serverul refuza. Acum e una."""
    return bool(v) and v.get("stare") == "proaspat" and v.get("verdict") == "valid"


def verdict_stare(conn, coada_id):
    """Starea verdictului pentru un element din coada. Citeste randul si deleaga calculul."""
    with conn.cursor() as cur:
        cur.execute("SELECT verdict, verdict_erori, verdict_amprenta, verdict_la, verdict_versiune, "
                    "payload->>'xml' FROM public.declaratii_coada WHERE id=%s", (coada_id,))
        r = cur.fetchone()
    if r is None:
        return {"stare": "lipsa", "motiv": "element inexistent",
                "actiune": "verifică id-ul elementului din coadă"}
    return verdict_din_rand(*r)


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


def aproba(conn, coada_id, aprobat_de, aprobat_de_id=None, motiv_trecere=None):
    """la_senior -> aprobata. Refuză dacă starea nu permite SAU dacă
    aprobatorul e chiar pregătitorul (control „patru ochi")."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT stare, creat_de, creat_de_id, cabinet_id FROM public.declaratii_coada WHERE id = %s",  # [p54_4ochi]
            (coada_id,))
        r = cur.fetchone()
        if r is None:
            return {"ok": False, "cod": "INEXISTENT"}
        st, creat_de, creat_de_id, _cabinet_id = r[0], r[1], r[2], r[3]  # [p54_4ochi]
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


def respinge(conn, coada_id, respins_de, motiv, respins_de_id=None):
    """la_senior -> respinsa + motiv. Refuză dacă starea nu permite."""
    # [motiv_obligatoriu_v1] respingerea fără motiv lasă contabilul fără explicație
    if motiv is None or not str(motiv).strip():
        return {"ok": False, "cod": "MOTIV_LIPSA",
                "mesaj": "respingerea necesită un motiv (contabilul trebuie să știe ce să corecteze)"}
    with conn.cursor() as cur:
        st = _stare_curenta(cur, coada_id)
        if st is None:
            return {"ok": False, "cod": "INEXISTENT"}
        if not poate_tranzitiona(st, "respinge"):
            return {"ok": False, "cod": "STARE_GRESITA",
                    "mesaj": "nu pot respinge din starea '%s'" % st}
        cur.execute(
            "UPDATE public.declaratii_coada SET stare='respinsa', "
            "respins_de=%s, respins_de_id=%s, respins_la=now(), motiv_respingere=%s WHERE id=%s",
            (respins_de, respins_de_id, motiv, coada_id))
    return {"ok": True, "stare": "respinsa"}


# ============================================================
#  DEPUNERE — DB (aprobata -> depusa + jurnal declaratii_depuse)
# ============================================================
def marcheaza_depusa(conn, coada_id, spv_index=None, depus_de=None, depus_de_id=None,
                     motiv_trecere=None):
    """
    aprobata -> depusa. Scrie și în declaratii_depuse (jurnal final).
    an/luna se iau din payload (_an/_luna; pt trim/anual: luna finală/12).
    """
    import psycopg2.extras as _E
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute("SELECT stare, tenant_id, tip, payload FROM public.declaratii_coada "
                    "WHERE id = %s", (coada_id,))
        r = cur.fetchone()
        if not r:
            return {"ok": False, "cod": "INEXISTENT"}
        if not poate_tranzitiona(r["stare"], "depune"):
            return {"ok": False, "cod": "STARE_GRESITA",
                    "mesaj": "nu pot depune din starea '%s'" % r["stare"]}
        # [R41] Depunerea e tranzitia IREVERSIBILA - `depusa` n-are nicio iesire in TRANZITII.
        # Poarta e cu atat mai necesara aici: dupa ea nu se mai poate reveni prin nicio ruta.
        refuz = _poarta_verdict(conn, coada_id, "depune", motiv_trecere, depus_de_id)
        if refuz:
            return refuz
        p = r["payload"] or {}
        an = p.get("_an")
        # luna pt jurnal: lunar->luna; trimestrial->luna finală trim; anual->12
        if p.get("_luna"):
            luna = p["_luna"]
        elif p.get("_trim"):
            luna = p["_trim"] * 3
        else:
            luna = 12
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
