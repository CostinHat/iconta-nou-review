# -*- coding: utf-8 -*-
"""core/firma_rezumat.py — MODELUL DE CITIRE al portofoliului: un rând per firmă și aspect.

**DE CE EXISTĂ.** P2: *„numărul de interogări pentru o cerere de portofoliu nu crește proporțional cu
numărul de firme"*. Măsurat pe cele cinci rute, la 1000 de firme (curba 100/250/500/1000, creștere
liniară confirmată, ~2,0× la fiecare dublare):

| ruta | interogări | conexiuni | secunde |
|---|---|---|---|
| `migrare/solduri` | 4.000 | 2.001 | 1,24 |
| `migrare/plan-conturi` | 3.000 | 2.001 | 0,98 |
| `migrare/vector` | 3.000 | 2.001 | 1,01 |
| `termene` | 8.000 | 3.001 | 12,88 |
| **`control-fiscal`** | **278.882** | **12.001** | **70,81** |

`control-fiscal` rulează **pipeline-ul fiscal întreg per firmă** — `_verificari_contabile`
regenerează D300/D112/D390, o spune chiar docstringul ei. 279 de mii de interogări pentru **o**
cerere interactivă.

**CE FACE MODULUL ĂSTA.** Ține, în `public`, câte un rând per (firmă, aspect), cu aceeași disciplină
de prospețime ca P1: versiunea sursei din care s-a calculat, momentul, iar starea **derivată** din
comparație — niciodată stocată. Citirea întregului portofoliu, pentru toate aspectele, e **o singură
interogare**.

**ASPECTELE nu sunt o listă de convenienta.** Fiecare poartă:
  * `tabele` — tabelele-sursă din schema firmei, adică ce anume îl invalidează. Triggerele se pun
    pe ele, deci invalidarea nu depinde de memoria mea despre căile de scriere;
  * `calcul` — funcția care produce valoarea, chemată **exact ca azi**, ca să nu existe două
    definiții ale aceleiași cifre.

**INTERDICȚIA, aceeași ca la P1, și nu se relaxează:** o valoare veche NU se arată ca fiind curentă.
Citirea întoarce `stare ∈ {curent, invalidat, lipseste}` plus `calculat_la`. *O stare „în
recalculare" declarată e acceptabilă; una veche și tăcută nu e.*

**CE NU REZOLVĂ, declarat.** Modelul mută costul din citire în scriere; nu-l desființează. O firmă
care se schimbă des se recalculează des. Ce se câștigă e că **cererea interactivă nu mai plătește
pentru portofoliu** — plătește o dată, per firmă, per schimbare.
"""
from __future__ import annotations

import json

CURENT, INVALIDAT, LIPSESTE = "curent", "invalidat", "lipseste"

DDL = """
CREATE TABLE IF NOT EXISTS public.firma_rezumat (
    tenant_id      integer     NOT NULL,
    aspect         text        NOT NULL,
    date           jsonb       NOT NULL,
    versiune_sursa bigint      NOT NULL,
    calculat_la    timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (tenant_id, aspect)
);
"""


def _solduri(conn, schema):
    from core import solduri_api
    r = solduri_api.rezumat(conn)
    return {"are_solduri": r["are_solduri"], "randuri": r["randuri"]}


def _plan_conturi(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM plan_conturi")
        return {"conturi": cur.fetchone()[0]}


def _vector(conn, schema):
    """Cheamă `vector_fiscal_api.citeste` — ACEEAȘI funcție pe care o chema ruta.

    Prima formă a acestui aspect făcea o interogare proprie pe `firma_profil` și inventa un câmp
    `complet`; ruta citea `completat`, din altă funcție. *Două definiții ale aceleiași stări sunt
    începutul unei divergențe tăcute* — și e chiar clasa reparată la R94 acum două zile."""
    from core import vector_fiscal_api
    v = vector_fiscal_api.citeste(conn) or {}
    return {"completat": bool(v.get("completat")), "regim_fiscal": v.get("regim_fiscal"),
            "platitor_tva": v.get("platitor_tva"), "tip_decont": v.get("tip_decont"),
            "operatiuni_ic": v.get("operatiuni_ic")}


#: REGISTRUL ASPECTELOR. `tabele` = ce invalidează aspectul; `calcul(conn, schema) -> dict`.
#: Tabelele NU sunt ghicite: sunt cele pe care le citește chiar funcția de calcul.
def _tip_firma(conn, schema):
    """`tip_firma` al firmei — prin ACEEAȘI primitivă ca `tenantii_userului` (`tip_firma_nrm`),
    ca să nu existe două normalizări ale aceleiași valori."""
    from core.migrare_api import regim_contabil, tip_firma_nrm
    with conn.cursor() as cur:
        cur.execute("SELECT tip_firma FROM firma_profil WHERE id = 1")
        r = cur.fetchone()
    t = tip_firma_nrm(r[0] if r else None)
    return {"tip_firma": t, "regim_contabil": regim_contabil(t)}


ASPECTE = {
    "tip_firma": {"tabele": ("firma_profil",), "calcul": _tip_firma},
    "solduri": {"tabele": ("solduri_initiale",), "calcul": _solduri},
    "plan_conturi": {"tabele": ("plan_conturi",), "calcul": _plan_conturi},
    "vector": {"tabele": ("firma_profil",), "calcul": _vector},
}

#: Aspectele GRELE — `termene` și `control_fiscal` — cer conexiune la `public` pe lângă cea a firmei,
#: deci se calculează prin `core/firma_rezumat_greu.py`, care le primește pe amândouă. Se ține
#: separat ca să nu se creadă că toate aspectele au aceeași formă de apel.
ASPECTE_GRELE = ("termene", "control_fiscal")

TOATE = tuple(ASPECTE) + ASPECTE_GRELE


def aplica_ddl(conn):
    with conn.cursor() as cur:
        cur.execute(DDL)


def tabele_urmarite():
    """Toate tabelele-sursă ale aspectelor ușoare, ca mulțime. Derivată din registru, nu scrisă."""
    out = set()
    for a in ASPECTE.values():
        out |= set(a["tabele"])
    return sorted(out)


def scrie(conn, tenant_id, aspect, date, versiune):
    with conn.cursor() as cur:
        cur.execute(
            # upsert-ok: rezumatul e o valoare DERIVATĂ, recalculabilă din sursă. A o suprascrie cu
            # una mai nouă e chiar scopul; nu e o intrare de utilizator care s-ar pierde.
            "INSERT INTO public.firma_rezumat (tenant_id, aspect, date, versiune_sursa, calculat_la) "
            "VALUES (%s, %s, %s::jsonb, %s, now()) "
            "ON CONFLICT (tenant_id, aspect) DO UPDATE "
            "SET date = EXCLUDED.date, versiune_sursa = EXCLUDED.versiune_sursa, "
            "    calculat_la = EXCLUDED.calculat_la",
            (tenant_id, aspect, json.dumps(date, ensure_ascii=False, default=str), versiune))


def citeste(conn, tenant_ids, aspecte=None):
    """**O SINGURĂ interogare pentru tot portofoliul și toate aspectele cerute.**

    `{tenant_id: {aspect: {date, stare, calculat_la, versiune_sursa, versiune_curenta}}}`.
    Firmele/aspectele fără rând apar cu `stare = "lipseste"` — absența se declară."""
    aspecte = list(aspecte or TOATE)
    if not tenant_ids:
        return {}
    with conn.cursor() as cur:
        cur.execute(
            "SELECT t.id, a.aspect, r.date, r.versiune_sursa, r.calculat_la, "
            "       COALESCE(s.versiune, 0) "
            "  FROM unnest(%s::int[])  AS t(id) "
            " CROSS JOIN unnest(%s::text[]) AS a(aspect) "
            "  LEFT JOIN public.firma_rezumat r "
            "         ON r.tenant_id = t.id AND r.aspect = a.aspect "
            "  LEFT JOIN public.supervizor_sursa s ON s.tenant_id = t.id",
            (list(tenant_ids), aspecte))
        randuri = cur.fetchall()

    out = {}
    for tid, aspect, date, v_calc, calculat_la, v_acum in randuri:
        d = out.setdefault(tid, {})
        if date is None:
            d[aspect] = {"date": None, "stare": LIPSESTE, "calculat_la": None,
                         "versiune_sursa": None, "versiune_curenta": v_acum}
        else:
            d[aspect] = {"date": date, "calculat_la": calculat_la,
                         "stare": CURENT if v_calc == v_acum else INVALIDAT,
                         "versiune_sursa": v_calc, "versiune_curenta": v_acum}
    return out


def recalculeaza_firma(tenant_id, schema, aspecte=None, deschide=None):
    """Recalculează aspectele UȘOARE ale unei firme, într-o singură conexiune la schema ei.

    Versiunea se citește ÎNAINTE de calcul — ca la P1, și din același motiv: altfel un calcul lung
    ar ștampila o versiune apărută în timpul lui, iar rezultatul ar părea curent fără să fie."""
    from core import db as _db, supervizor_cache as _sc
    deschide = deschide or _db.get_conn
    aspecte = [a for a in (aspecte or ASPECTE) if a in ASPECTE]

    with _db.get_conn() as c:
        v = _sc.versiune_sursa(c, tenant_id)

    valori = {}
    with deschide(schema) as cs:
        for a in aspecte:
            try:
                valori[a] = ASPECTE[a]["calcul"](cs, schema)
            except Exception as e:      # noqa: BLE001 — eroarea devine valoare DECLARATĂ
                valori[a] = {"eroare": "%s: %s" % (type(e).__name__, e)}

    with _db.get_conn() as c:
        for a, date in valori.items():
            scrie(c, tenant_id, a, date, v)
        c.commit()
    return valori

# ============================================================================
#  ASPECTELE GRELE — aici stă tot costul mutat din cererile interactive
# ============================================================================
def recalculeaza_greu(tenant_id, schema, azi=None, ctx=None, nume=None, cui=None):
    """Recalculează `termene` și `control_fiscal` pentru o firmă.

    Chemată de lucrător / la invalidare, **niciodată dintr-o cerere interactivă**. Măsurat înainte
    de P2, la 1000 de firme, într-o singură cerere: `control-fiscal` — 278.882 de interogări, 12.001
    de conexiuni, **70,8 s**; `termene` — 8.000 de interogări, 3.001 de conexiuni, **12,9 s**.

    Calculul e CHEMAT EXACT CA ÎNAINTE (`control_fiscal_api.evalueaza_firma`,
    `main._construieste_contabil`, `main._termene_una_firma`), ca să nu existe două definiții ale
    aceleiași cifre. Ce s-a schimbat e **cine plătește**: o dată per firmă per schimbare, nu o dată
    per cerere per firmă.

    Versiunea se citește ÎNAINTE de calcul — ca la P1, și din același motiv."""
    from core import db as _db, supervizor_cache as _sc
    from core.common import azi_ro as _azi_ro
    azi = azi or _azi_ro()

    with _db.get_conn() as c:
        v = _sc.versiune_sursa(c, tenant_id)
        if nume is None:
            with c.cursor() as cur:
                cur.execute("SELECT nume, cui FROM public.tenants WHERE id = %s", (tenant_id,))
                r = cur.fetchone()
            nume, cui = (r[0], r[1]) if r else (None, None)
        # CTX CU ACCES LA FIRMA. Doua sub-verificari din `_construieste_contabil` (stocuri, praguri
        # Intrastat) trec prin `_schema_sau_404(ctx, tenant_id)`; fara un utilizator care are acces,
        # ele cad pe „gri" cu 404 — adica verdictul firmei ar depinde de cine il cere. Se alege
        # administratorul cabinetului EI.
        if not (ctx or {}).get("uid"):
            with c.cursor() as cur:
                cur.execute(
                    "SELECT u.id FROM public.users u "
                    "  JOIN public.tenants t ON t.accounting_firm_id = u.accounting_firm_id "
                    " WHERE t.id = %s AND u.rol = 'admin_firma' AND u.activ "
                    " ORDER BY u.id LIMIT 1", (tenant_id,))
                r = cur.fetchone()
            ctx = {"uid": r[0]} if r else {"uid": None}

    valori = {}

    # ── control_fiscal ─────────────────────────────────────────────────────
    try:
        import main as _main
        from core import control_fiscal_api as _cf
        with _db.get_conn(schema) as cs, _db.get_conn() as cp:
            r = _cf.evalueaza_firma(cs, cp, tenant_id, schema, azi)
        contabil, _vc = _main._construieste_contabil(schema, tenant_id, ctx, azi.year, azi.month,
                                                     r.get("regim_tva_anaf"))
        valori["control_fiscal"] = {
            "stare": _main.pastila_firma(r["stare"], contabil),
            "lipsa": len(r.get("lipsa") or []), "urmarit": len(r.get("urmarit") or []),
            "neclar": len(r.get("neclar") or []), "contabil": contabil}
    except Exception as e:      # noqa: BLE001 — eroarea devine valoare DECLARATĂ, nu tăcere
        valori["control_fiscal"] = {"eroare": "%s: %s" % (type(e).__name__, e), "stare": "gri",
                                    "lipsa": 0, "urmarit": 0, "neclar": 0, "contabil": []}

    # ── termene — prin blocul EXTRAS din rută; el își deschide singur conexiunile ──
    try:
        import main as _main2
        ev, neev = _main2._termene_una_firma({"id": tenant_id, "nume": nume, "cui": cui}, ctx, azi)
        valori["termene"] = {"eval": ev, "neevaluat": neev}
    except Exception as e:      # noqa: BLE001
        valori["termene"] = {"eval": None, "neevaluat": None,
                             "eroare": "%s: %s" % (type(e).__name__, e)}

    with _db.get_conn() as c:
        for a, date in valori.items():
            scrie(c, tenant_id, a, date, v)
        c.commit()
    return valori


#: Mărimea LOTULUI de recalculare — nu e o valoare fiscală, e cât ia lucrătorul
#: într-o tură ca să nu țină conexiunea ocupată. Se schimbă fără temei legal.
LOT_RECALCULARE = 200


def de_recalculat(conn, limita=LOT_RECALCULARE):
    """Firmele al căror rezumat nu mai e curent, pe oricare aspect."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT DISTINCT s.tenant_id "
            "  FROM public.supervizor_sursa s "
            "  LEFT JOIN public.firma_rezumat r ON r.tenant_id = s.tenant_id "
            " WHERE r.tenant_id IS NULL OR r.versiune_sursa <> s.versiune "
            " ORDER BY s.tenant_id LIMIT %s", (limita,))
        return [x[0] for x in cur.fetchall()]


def recalculeaza_lot(limita=LOT_RECALCULARE, azi=None, cu_greu=True, ctx=None):
    """Lucrătorul. Aspectele ușoare, și — dacă se cere — cele grele."""
    from core import db as _db
    with _db.get_conn() as c:
        ids = de_recalculat(c, limita)
        with c.cursor() as cur:
            cur.execute("SELECT id, schema_name, nume, cui FROM public.tenants "
                        "WHERE id = ANY(%s)", (ids,))
            info = {r[0]: r[1:] for r in cur.fetchall()}
    facute, sarite = 0, []
    for tid in ids:
        d = info.get(tid)
        if not d:
            sarite.append(tid)      # contor fără firmă (probă, firmă ștearsă) — se raportează
            continue
        schema, nume, cui = d
        recalculeaza_firma(tid, schema)
        if cu_greu:
            # `ctx=None` -> se alege per firma administratorul cabinetului ei (v. `recalculeaza_greu`)
            recalculeaza_greu(tid, schema, azi=azi, ctx=ctx, nume=nume, cui=cui)
        facute += 1
    return {"invalidate": len(ids), "recalculate": facute, "fara_firma": sarite}
