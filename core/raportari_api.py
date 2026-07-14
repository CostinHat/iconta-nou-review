"""
core/raportari_api.py — canal de feedback: cei care proceseaza trimit raportari
catre Admin iConta; raspunsurile vin inapoi in firul fiecaruia.
Strat 1: text + fir de mesaje + contor necitite (becul rosu). Imagini si AI: ulterior.
"""
import psycopg2.extras as _E


def _nume(u_pre, u_num, email):
    n = " ".join(x for x in [u_pre, u_num] if x).strip()
    return n or email or "(necunoscut)"


def creeaza_raportare(conn, autor_id, cabinet_id, subiect, text):
    """Deschide o raportare noua cu primul mesaj (de la utilizator)."""
    if not (text or "").strip():
        return {"ok": False, "cod": "TEXT_GOL"}
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            "INSERT INTO public.raportari (autor_id, cabinet_id, subiect) "
            "VALUES (%s,%s,%s) RETURNING id",
            (autor_id, cabinet_id, (subiect or "").strip() or None))
        rid = cur.fetchone()["id"]
        cur.execute(
            "INSERT INTO public.raportari_mesaje (raportare_id, autor_id, rol_autor, text) "
            "VALUES (%s,%s,'utilizator',%s) RETURNING id",
            (rid, autor_id, text.strip()))
        mid = cur.fetchone()["id"]
    return {"ok": True, "raportare_id": rid, "mesaj_id": mid}


def adauga_mesaj(conn, raportare_id, autor_id, rol_autor, text, schimba_stare=True):
    """Adauga un mesaj in fir. rol_autor = 'utilizator', 'admin' sau 'ai' (autor_id NULL).
    Mesajul nou e necitit pentru destinatar (becul rosu)."""
    if rol_autor not in ("utilizator", "admin", "ai"):
        return {"ok": False, "cod": "ROL_INVALID"}
    if not (text or "").strip():
        return {"ok": False, "cod": "TEXT_GOL"}
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute("SELECT id FROM public.raportari WHERE id = %s", (raportare_id,))
        if not cur.fetchone():
            return {"ok": False, "cod": "INEXISTENT"}
        cur.execute(
            "INSERT INTO public.raportari_mesaje (raportare_id, autor_id, rol_autor, text) "
            "VALUES (%s,%s,%s,%s) RETURNING id",
            (raportare_id, autor_id, rol_autor, text.strip()))
        mid = cur.fetchone()["id"]
        # [inchidere_v1] mesaj intr-un fir inchis il redeschide
        cur.execute("UPDATE public.raportari SET stare='noua' WHERE id=%s AND stare='inchisa'", (raportare_id,))
        # [triaj_ai] replica utilizatorului dupa un raspuns AI = AI-ul nu a rezolvat -> escaladare
        if rol_autor == "utilizator":
            cur.execute("SELECT rol_autor FROM public.raportari_mesaje WHERE raportare_id=%s "
                        "AND id < %s ORDER BY id DESC LIMIT 1", (raportare_id, mid))
            ult = cur.fetchone()
            if ult and ult["rol_autor"] == "ai":
                cur.execute("UPDATE public.raportari SET pentru_admin = true WHERE id = %s", (raportare_id,))
        if not schimba_stare:  # [triaj_ai] confirmarea de escaladare nu stinge bulina
            cur.execute("UPDATE public.raportari SET ultim_mesaj_la = now() WHERE id = %s", (raportare_id,))
            return {"ok": True, "mesaj_id": mid}
        # raspunsul de la admin/AI schimba starea + marcheaza fir activ
        stare = "raspuns" if rol_autor in ("admin", "ai") else "noua"
        cur.execute(
            "UPDATE public.raportari SET ultim_mesaj_la = now(), stare = %s WHERE id = %s",
            (stare, raportare_id))
    return {"ok": True, "mesaj_id": mid}


def _mesaje_firului(cur, raportare_id):
    cur.execute(
        "SELECT m.id, m.autor_id, m.rol_autor, m.text, m.citit, m.creat_la, "
        "       u.prenume, u.nume, u.email "
        "  FROM public.raportari_mesaje m "
        "  LEFT JOIN public.users u ON u.id = m.autor_id "
        " WHERE m.raportare_id = %s ORDER BY m.creat_la ASC",
        (raportare_id,))
    randuri = cur.fetchall()
    # atasamentele tuturor mesajelor din fir, intr-o singura interogare
    ids = [r["id"] for r in randuri]
    atas = {}
    if ids:
        cur.execute(
            "SELECT mesaj_id, cale, nume_orig FROM public.raportari_atasamente "
            " WHERE mesaj_id = ANY(%s) ORDER BY id ASC", (ids,))
        for a in cur.fetchall():
            atas.setdefault(a["mesaj_id"], []).append(
                {"cale": a["cale"], "nume": a["nume_orig"]})
    out = []
    for r in randuri:
        out.append({
            "id": r["id"], "rol_autor": r["rol_autor"], "text": r["text"],
            "citit": r["citit"], "cand": r["creat_la"].isoformat(),
            "autor": _nume(r["prenume"], r["nume"], r["email"]),
            "atasamente": atas.get(r["id"], []),
        })
    return out


def adauga_atasament(conn, mesaj_id, cale, nume_orig):
    """Leaga o imagine (deja salvata pe disc) de un mesaj."""
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM public.raportari_mesaje WHERE id = %s", (mesaj_id,))
        if not cur.fetchone():
            return {"ok": False, "cod": "MESAJ_INEXISTENT"}
        cur.execute(
            "INSERT INTO public.raportari_atasamente (mesaj_id, cale, nume_orig) "
            "VALUES (%s,%s,%s)", (mesaj_id, cale, nume_orig))
    return {"ok": True}


def autor_mesajului(conn, mesaj_id):
    """Cine a scris mesajul + firul lui (pt verificare acces la upload)."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT m.autor_id, m.raportare_id, r.autor_id "
            "  FROM public.raportari_mesaje m "
            "  JOIN public.raportari r ON r.id = m.raportare_id "
            " WHERE m.id = %s", (mesaj_id,))
        r = cur.fetchone()
    if not r:
        return None
    return {"mesaj_autor": r[0], "raportare_id": r[1], "fir_autor": r[2]}


def raportarile_mele(conn, autor_id):
    """Firele deschise de mine + mesaje. Contor = raspunsuri admin necitite (bec rosu)."""
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            "SELECT id, subiect, stare, creat_la, ultim_mesaj_la "
            "  FROM public.raportari WHERE autor_id = %s ORDER BY ultim_mesaj_la DESC",
            (autor_id,))
        fire = [dict(r) for r in cur.fetchall()]
        rez, necitite = [], 0
        for f in fire:
            mesaje = _mesaje_firului(cur, f["id"])
            # "in asteptare" = firul nu are inca raspuns de la admin (becul)
            are_raspuns = any(m["rol_autor"] == "admin" for m in mesaje)
            nc = 0 if are_raspuns else 1
            necitite += nc
            rez.append({
                "id": f["id"], "subiect": f["subiect"], "stare": f["stare"],
                "creat_la": f["creat_la"].isoformat(),
                "ultim_mesaj_la": f["ultim_mesaj_la"].isoformat(),
                "necitite": nc, "mesaje": mesaje,
            })
    return {"ok": True, "raportari": rez, "necitite_total": necitite}


def marcheaza_citit(conn, raportare_id, cine_rol):
    """Marcheaza citite mesajele celuilalt rol (stinge becul).
    cine_rol='utilizator' -> citeste mesajele de la admin; invers pt admin."""
    celalalt = "admin" if cine_rol == "utilizator" else "utilizator"
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE public.raportari_mesaje SET citit = true "
            "WHERE raportare_id = %s AND rol_autor = %s AND citit = false",
            (raportare_id, celalalt))
    return {"ok": True}


def contor_necitite(conn, autor_id):
    """Cifra rosie = sesizarile mele in asteptare de raspuns (stare 'noua').
    Se aprinde la trimitere, scade pe masura ce vin raspunsuri reale (admin sau AI);
    confirmarea de escaladare NU stinge (sesizarea inca asteapta). [triaj_ai]"""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) FROM public.raportari r "
            " WHERE r.autor_id = %s AND r.stare = 'noua'",
            (autor_id,))
        n = cur.fetchone()[0]
    return {"ok": True, "necitite": int(n)}


# ---- ADMIN iConta (superadmin): vede toate raportarile ----
def toate_raportarile(conn):
    """Pentru Admin iConta: toate firele, cu autor + cabinet + nr mesaje + necitite admin."""
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            "SELECT r.id, r.subiect, r.stare, r.creat_la, r.ultim_mesaj_la, "
            "       r.pentru_admin, "  # [p38_pentru_admin]
            "       u.prenume, u.nume, u.email, af.nume AS cabinet, "
            "       (SELECT COUNT(*) FROM public.raportari_mesaje m "
            "          WHERE m.raportare_id = r.id AND m.rol_autor='utilizator' AND m.citit=false) AS necitite, "
            "       (SELECT m2.text FROM public.raportari_mesaje m2 "  # [p40_text_lista]
            "          WHERE m2.raportare_id = r.id ORDER BY m2.creat_la ASC LIMIT 1) AS text "
            "  FROM public.raportari r "
            "  LEFT JOIN public.users u ON u.id = r.autor_id "
            "  LEFT JOIN public.accounting_firms af ON af.id = r.cabinet_id "
            " ORDER BY r.ultim_mesaj_la DESC")
        fire = []
        for r in cur.fetchall():
            fire.append({
                "id": r["id"], "subiect": r["subiect"], "stare": r["stare"],
                "creat_la": r["creat_la"].isoformat(),
                "ultim_mesaj_la": r["ultim_mesaj_la"].isoformat(),
                "autor": _nume(r["prenume"], r["nume"], r["email"]),
                "cabinet": r["cabinet"], "necitite": int(r["necitite"] or 0),
                "pentru_admin": bool(r["pentru_admin"]),  # [p38_pentru_admin]
                "text": (r["text"] or ""),  # [p40_text_lista]
            })
    return {"ok": True, "raportari": fire}


def firul_complet(conn, raportare_id):
    """Un fir cu toate mesajele (pt admin sau pt detaliu)."""
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            "SELECT r.id, r.subiect, r.stare, r.autor_id, "
            "       u.prenume, u.nume, u.email, af.nume AS cabinet "
            "  FROM public.raportari r "
            "  LEFT JOIN public.users u ON u.id = r.autor_id "
            "  LEFT JOIN public.accounting_firms af ON af.id = r.cabinet_id "
            " WHERE r.id = %s", (raportare_id,))
        f = cur.fetchone()
        if not f:
            return {"ok": False, "cod": "INEXISTENT"}
        mesaje = _mesaje_firului(cur, raportare_id)
    return {"ok": True, "raportare": {
        "id": f["id"], "subiect": f["subiect"], "stare": f["stare"],
        "autor_id": f["autor_id"],
        "autor": _nume(f["prenume"], f["nume"], f["email"]),
        "cabinet": f["cabinet"], "mesaje": mesaje,
        "text": next((m["text"] for m in mesaje if m.get("rol_autor") == "utilizator"), "")}}  # [titlu_fir]


# [inchidere_v1] inchiderea unei sesizari (fara stergere - istoricul ramane in DB)
def seteaza_stare(conn, raportare_id, stare):
    if stare not in ("noua", "raspuns", "inchisa"):
        return {"ok": False, "cod": "STARE_INVALIDA"}
    with conn.cursor() as cur:
        cur.execute("UPDATE public.raportari SET stare = %s WHERE id = %s RETURNING id", (stare, raportare_id))
        if not cur.fetchone():
            return {"ok": False, "cod": "INEXISTENT"}
    return {"ok": True, "stare": stare}

# [p38_pentru_admin]
def seteaza_pentru_admin(conn, raportare_id, valoare):
    """Marcheaza/demarcheaza o raportare ca 'pentru Admin iConta' (nu tine de aplicatie).
    valoare=True -> casuta 'Pentru tine'; False -> casuta 'De la utilizatori'."""
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM public.raportari WHERE id = %s", (raportare_id,))
        if not cur.fetchone():
            return {"ok": False, "cod": "INEXISTENT"}
        cur.execute("UPDATE public.raportari SET pentru_admin = %s WHERE id = %s",
                    (bool(valoare), raportare_id))
    return {"ok": True, "pentru_admin": bool(valoare)}
