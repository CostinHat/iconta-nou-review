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


# ============================================================
#  F120 — strat AI generativ peste agregatele de mai sus
# ============================================================
def analiza_ai(conn, cabinet_id):
    """[F120] Analiza generativa: citeste agregatele deterministe (tipare) si cere lui Claude o
    explicatie a tiparelor + recomandari CONCRETE. GROUNDED strict pe datele furnizate (fara cifre
    inventate). Refoloseste core.ai_client (model ales de proiect). Fallback curat daca AI indisponibil
    sau nu-s date - apelantul afiseaza mesajul, nu crapa ecranul."""
    from core import ai_client
    date = tipare(conn, cabinet_id)
    if not date.get("are_date"):
        return {"disponibil": False, "motiv": "Nu există încă respingeri de analizat."}
    if not ai_client.disponibil():
        return {"disponibil": False, "motiv": "Asistentul AI nu e configurat pe acest server."}

    motive = "\n".join("- %s: %d respingeri" % (m["motiv"], m["n"]) for m in date["motive"][:15])
    tipuri = "\n".join("- %s: %d din %d respinse (%d%%)" % (t["tip"].upper(), t["respinse"], t["total"], t["pct"])
                       for t in date["tipuri"] if t["respinse"] > 0)
    firme = "\n".join("- %s: %d respinse din %d" % (f["nume"], f["respinse"], f["total"]) for f in date["firme"][:10])

    sistem = ("Esti asistentul unui cabinet de contabilitate din Romania. Analizezi tiparele de respingere "
              "a declaratiilor fiscale la ANAF si propui recomandari CONCRETE, actionabile, pentru a reduce "
              "respingerile. Foloseste DOAR datele furnizate - nu inventa cifre, firme sau motive care nu apar. "
              "Raspunzi in romana, concis si structurat: intai ce tipare observi (2-3 fraze), apoi 3-5 recomandari "
              "practice cu bullet. Fara introduceri de politete, direct la analiza.")
    prompt = ("Date agregate ale cabinetului (respingeri reale de declaratii):\n\n"
              "MOTIVE DE RESPINGERE RECURENTE:\n%s\n\n"
              "TIPURI DE DECLARATII CU RATA DE RESPINGERE:\n%s\n\n"
              "FIRME CU CELE MAI MULTE RESPINGERI:\n%s\n\n"
              "Analizeaza tiparele si propune recomandari."
              % (motive or "(niciunul)", tipuri or "(niciunul)", firme or "(niciuna)"))
    try:
        text = ai_client.genereaza_text(prompt, sistem=sistem, max_tokens=1000, temperatura=0.4)
    except Exception as e:
        return {"disponibil": False, "motiv": "Nu am putut genera analiza acum (%s)." % type(e).__name__}
    return {"disponibil": True, "analiza": text}
