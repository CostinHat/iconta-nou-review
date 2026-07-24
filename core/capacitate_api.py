"""
core/capacitate_api.py — panou Capacitate pentru patron (admin_firma).
Trei perspective, toate pe cabinet (nu se expune asistentului):
  1. Cabinet  — cat e de facut vs ritm
  2. Pe asistent — incarcare per procesator
  3. Timp — durata medie pe tip (creat_la - inceput_la)

Sursa de timp: declaratii_coada.inceput_la (cuplat la deschiderea ecranului
Declaratii). Pe date putine, mediile sunt orientative -> intoarcem si N (mostre).
"""
import datetime
import psycopg2.extras as _E


# stari "in lucru" (nedepuse, nerespinse)
_STARI_ACTIVE = ("la_senior", "ciorna", "in_coada_token")


def _luna_curenta():
    azi = datetime.date.today()
    return azi.year, azi.month, azi.replace(day=1)


def _zile_lucratoare_pana_azi(prima_zi):
    """Cate zile lucratoare (L-V) de la inceputul lunii pana azi inclusiv."""
    azi = datetime.date.today()
    n, d = 0, prima_zi
    while d <= azi:
        if d.weekday() < 5:
            n += 1
        d += datetime.timedelta(days=1)
    return max(n, 1)


def _fmt_durata(secunde):
    if secunde is None:
        return None
    m = int(round(secunde / 60.0))
    if m < 60:
        return "%d min" % m
    h = m // 60
    rm = m % 60
    return "%dh %02dm" % (h, rm) if rm else "%dh" % h


def capacitate(conn, cabinet_id):
    an, luna, prima_zi = _luna_curenta()
    zile_lucr = _zile_lucratoare_pana_azi(prima_zi)
    out = {"ok": True}

    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        # ---------- 1) CABINET ----------
        cur.execute(
            "SELECT "
            "  COUNT(*) FILTER (WHERE stare = ANY(%(active)s)) AS in_lucru, "
            "  COUNT(*) FILTER (WHERE stare = 'la_senior') AS de_validat, "
            "  COUNT(*) FILTER (WHERE depus_la >= %(p)s) AS depuse_luna "
            "  FROM public.declaratii_coada "
            " WHERE cabinet_id = %(c)s",
            {"active": list(_STARI_ACTIVE), "p": prima_zi, "c": cabinet_id})
        r = cur.fetchone()
        in_lucru = int(r["in_lucru"])
        depuse_luna = int(r["depuse_luna"])
        ritm = round(depuse_luna / zile_lucr, 1)
        out["cabinet"] = {
            "in_lucru": in_lucru,
            "de_validat": int(r["de_validat"]),
            "depuse_luna": depuse_luna,
            "ritm_pe_zi": ritm,
            "zile_lucratoare": zile_lucr,
        }

        # ---------- 2) PE ASISTENT ----------
        # procesatori = useri activi cu cel putin o competenta
        cur.execute(
            "SELECT id, prenume, nume, poate_pregati, poate_valida, poate_depune "
            "  FROM public.users "
            " WHERE accounting_firm_id = %s AND activ = true "
            "   AND (poate_pregati OR poate_valida OR poate_depune) "
            " ORDER BY prenume, nume", (cabinet_id,))
        procesatori = cur.fetchall()

        asistenti = []
        for p in procesatori:
            uid = p["id"]
            cur.execute(
                "SELECT "
                "  COUNT(*) FILTER (WHERE stare = ANY(%(active)s)) AS in_lucru, "
                "  COUNT(*) FILTER (WHERE creat_la >= %(p)s) AS pregatite_luna, "
                "  COUNT(*) FILTER (WHERE depus_la >= %(p)s) AS depuse_luna, "
                "  COUNT(*) FILTER (WHERE creat_la >= %(p)s AND respins_la IS NOT NULL) AS respinse_luna "
                "  FROM public.declaratii_coada "
                " WHERE cabinet_id = %(c)s AND creat_de_id = %(u)s",
                {"active": list(_STARI_ACTIVE), "p": prima_zi,
                 "c": cabinet_id, "u": uid})
            s = cur.fetchone()
            pregatite = int(s["pregatite_luna"])
            respinse = int(s["respinse_luna"])
            acceptate = pregatite - respinse
            pct = int(round(100.0 * acceptate / pregatite)) if pregatite else None

            nume_complet = ((p["prenume"] or "") + " " + (p["nume"] or "")).strip() or "—"
            asistenti.append({
                "id": uid,
                "nume": nume_complet,
                "in_lucru": int(s["in_lucru"]),
                "pregatite_luna": pregatite,
                "depuse_luna": int(s["depuse_luna"]),
                "pct_acceptate": pct,
                "poate_valida": p["poate_valida"],
            })
        out["asistenti"] = asistenti

        # ---------- 3) TIMP pe tip ----------
        cur.execute(
            "SELECT tip, "
            "  AVG(EXTRACT(EPOCH FROM (creat_la - inceput_la))) AS sec_mediu, "
            "  COUNT(*) AS n "
            "  FROM public.declaratii_coada "
            " WHERE cabinet_id = %s "
            "   AND inceput_la IS NOT NULL AND creat_la IS NOT NULL "
            "   AND creat_la > inceput_la "
            " GROUP BY tip ORDER BY tip", (cabinet_id,))
        timp = []
        total_n = 0
        for t in cur.fetchall():
            n = int(t["n"])
            total_n += n
            timp.append({
                "tip": t["tip"],
                "durata_medie": _fmt_durata(float(t["sec_mediu"]) if t["sec_mediu"] else None),
                "n": n,
            })
        out["timp"] = {"pe_tip": timp, "total_mostre": total_n}

    return out
