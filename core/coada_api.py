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
            "COALESCE(u.nume, u.email) AS creat_de_nume "  # [val_nume_v1] numele pregatitorului, nu UID brut
            "FROM public.declaratii_coada c "
            "LEFT JOIN public.users u ON u.id = c.creat_de_id "
            "WHERE " + " AND ".join("c." + x for x in cond) +
            " ORDER BY c.creat_la DESC", val)
        return [dict(r) for r in cur.fetchall()]


def _stare_curenta(cur, coada_id):
    cur.execute("SELECT stare FROM public.declaratii_coada WHERE id = %s", (coada_id,))
    r = cur.fetchone()
    return r[0] if r else None


# ============================================================
#  APROBARE / RESPINGERE — DB (verifică tranziția)
# ============================================================
def patru_ochi_posibil(conn, cabinet_id):
    """Posibil DOAR daca exista pregatitor + validator pe persoane distincte (competente)."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) FILTER (WHERE poate_pregati), "
            "       COUNT(*) FILTER (WHERE poate_valida), "
            "       COUNT(*) "
            "  FROM public.users "
            " WHERE accounting_firm_id = %s AND activ = true AND (poate_pregati OR poate_valida)",
            (cabinet_id,))
        r = cur.fetchone()
    return int(r[0]) >= 1 and int(r[1]) >= 1 and int(r[2]) >= 2


def patru_ochi_activ(conn, cabinet_id):
    """Patronul a activat patru-ochi pentru acest cabinet?"""
    with conn.cursor() as cur:
        cur.execute("SELECT patru_ochi_activ FROM public.accounting_firms WHERE id = %s",
                    (cabinet_id,))
        r = cur.fetchone()
    return bool(r[0]) if r and r[0] is not None else False


def aproba(conn, coada_id, aprobat_de, aprobat_de_id=None):
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
        if _vinovat and patru_ochi_activ(conn, _cabinet_id) and patru_ochi_posibil(conn, _cabinet_id):
            return {"ok": False, "cod": "PATRU_OCHI",
                    "mesaj": "nu poți aproba o declarație pe care ai pregătit-o tu însuți "
                             "(control intern: pregătirea și validarea se fac de persoane diferite)"}
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
def marcheaza_depusa(conn, coada_id, spv_index=None, depus_de=None, depus_de_id=None):
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
        cur.execute(
            "INSERT INTO public.declaratii_depuse (tenant_id, an, luna, tip, xml, randuri, nr_depunere) "
            "SELECT %s,%s,%s,%s,%s,%s, COALESCE(MAX(nr_depunere),0)+1 "
            "FROM public.declaratii_depuse WHERE tenant_id=%s AND an=%s AND luna=%s AND tip=%s",
            (r["tenant_id"], an, luna, r["tip"], p.get("xml"),
             _E.Json(randuri) if randuri is not None else None,
             r["tenant_id"], an, luna, r["tip"]))
    return {"ok": True, "stare": "depusa", "an": an, "luna": luna}
