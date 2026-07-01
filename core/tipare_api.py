"""
core/tipare_api.py — Ecran G: Educatie pe tipare (statistic, fara AI).
Agregate deterministe pe declaratii_coada, materia prima pentru viitorul
strat AI. Trei perspective, toate pe cabinet (doar patron):
  1. Motive de respingere recurente
  2. Tipuri de declaratii cu rata de respingere
  3. Firme cu cele mai multe respingeri

La teste se umple singur. AI-ul (stratul 5) va citi exact aceste agregate.
"""
import psycopg2.extras as _E


def tipare(conn, cabinet_id):
    out = {"ok": True}
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:

        # ---------- 1) MOTIVE DE RESPINGERE recurente ----------
        cur.execute(
            "SELECT COALESCE(NULLIF(TRIM(motiv_respingere), ''), '(fara motiv)') AS motiv, "
            "       COUNT(*) AS n "
            "  FROM public.declaratii_coada "
            " WHERE cabinet_id = %s AND respins_la IS NOT NULL "
            " GROUP BY motiv ORDER BY n DESC, motiv LIMIT 15",
            (cabinet_id,))
        out["motive"] = [{"motiv": r["motiv"], "n": int(r["n"])} for r in cur.fetchall()]

        # ---------- 2) TIPURI cu rata de respingere ----------
        # pregatite = au fost create vreodata; respinse = au respins_la
        cur.execute(
            "SELECT tip, "
            "  COUNT(*) AS total, "
            "  COUNT(*) FILTER (WHERE respins_la IS NOT NULL) AS respinse "
            "  FROM public.declaratii_coada "
            " WHERE cabinet_id = %s "
            " GROUP BY tip ORDER BY respinse DESC, tip",
            (cabinet_id,))
        tipuri = []
        for r in cur.fetchall():
            total = int(r["total"])
            resp = int(r["respinse"])
            pct = int(round(100.0 * resp / total)) if total else 0
            tipuri.append({
                "tip": r["tip"], "total": total, "respinse": resp, "pct": pct,
            })
        out["tipuri"] = tipuri

        # ---------- 3) FIRME cu cele mai multe respingeri ----------
        cur.execute(
            "SELECT c.tenant_id, t.nume, t.cui, "
            "  COUNT(*) FILTER (WHERE c.respins_la IS NOT NULL) AS respinse, "
            "  COUNT(*) AS total "
            "  FROM public.declaratii_coada c "
            "  LEFT JOIN public.tenants t ON t.id = c.tenant_id "
            " WHERE c.cabinet_id = %s "
            " GROUP BY c.tenant_id, t.nume, t.cui "
            "HAVING COUNT(*) FILTER (WHERE c.respins_la IS NOT NULL) > 0 "
            " ORDER BY respinse DESC LIMIT 15",
            (cabinet_id,))
        firme = []
        for r in cur.fetchall():
            firme.append({
                "tenant_id": r["tenant_id"],
                "nume": r["nume"] or "(firma necunoscuta)",
                "cui": r["cui"] or "",
                "respinse": int(r["respinse"]),
                "total": int(r["total"]),
            })
        out["firme"] = firme

    # rezumat: avem date sau nu (pentru mesajul de gol)
    out["are_date"] = bool(out["motive"] or any(t["respinse"] for t in out["tipuri"]))
    return out
