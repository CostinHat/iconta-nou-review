"""
core/raportari_api.py — canal de feedback: cei care proceseaza trimit raportari
catre Admin iConta; raspunsurile vin inapoi in firul fiecaruia.
Strat 1: text + fir de mesaje + contor necitite (becul rosu). Imagini si AI: ulterior.
[15.10.2026, deficienta 270d] Doua feluri de fir (`raportari.tip`): `sesizare` si `cerere_import` (cererea de import din alta
aplicatie, cu `aplicatie` = de unde migreaza cabinetul). Fisierele firului stau in depozitul privat (`core.fisiere_private`, C36).
"""
import psycopg2.extras as _E

from core import fisiere_private as _fp

#: felurile de fir — multime inchisa, ca CHECK-ul din baza (`core/migrare_fisiere_private.py`)
TIPURI = ("sesizare", "cerere_import")


def _nume(u_pre, u_num, email):
    n = " ".join(x for x in [u_pre, u_num] if x).strip()
    return n or email or "(necunoscut)"


def creeaza_raportare(conn, autor_id, cabinet_id, subiect, text, tip="sesizare", aplicatie=None):
    """Deschide o raportare noua cu primul mesaj (de la utilizator). `tip` = `sesizare` | `cerere_import`; cererea de import
    cere `aplicatie` (din ce aplicatie migreaza cabinetul)."""
    if tip not in TIPURI:
        return {"ok": False, "cod": "TIP_INVALID"}
    aplicatie = (aplicatie or "").strip() or None
    if tip == "cerere_import" and not aplicatie:
        return {"ok": False, "cod": "APLICATIE_LIPSA"}
    if not (text or "").strip():
        return {"ok": False, "cod": "TEXT_GOL"}
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            "INSERT INTO public.raportari (autor_id, cabinet_id, subiect, tip, aplicatie) "
            "VALUES (%s,%s,%s,%s,%s) RETURNING id",
            (autor_id, cabinet_id, (subiect or "").strip() or None, tip, aplicatie if tip == "cerere_import" else None))
        rid = cur.fetchone()["id"]
        cur.execute(
            "INSERT INTO public.raportari_mesaje (raportare_id, autor_id, rol_autor, text) "
            "VALUES (%s,%s,'utilizator',%s) RETURNING id",
            (rid, autor_id, text.strip()))
        mid = cur.fetchone()["id"]
    return {"ok": True, "raportare_id": rid, "mesaj_id": mid}


#: [deficiența 291] cine scrie din partea iConta într-un fir (bulina autorului se aprinde la mesajele lor)
ROLURI_ICONTA = ("admin", "ai")


def adauga_mesaj(conn, raportare_id, autor_id, rol_autor, text, schimba_stare=True, veste=True):
    """Adauga un mesaj in fir. rol_autor = 'utilizator', 'admin' sau 'ai' (autor_id NULL).
    Mesajul nou e necitit pentru destinatar (becul rosu). [deficiența 291] `veste=False`: confirmarea automată a cererii („a fost
    transmisă echipei”) e ecoul cererii autorului, nu o veste de la iConta — intră deja citită, deci nu aprinde bulina."""
    if rol_autor not in ("utilizator", "admin", "ai"):
        return {"ok": False, "cod": "ROL_INVALID"}
    if not (text or "").strip():
        return {"ok": False, "cod": "TEXT_GOL"}
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute("SELECT id FROM public.raportari WHERE id = %s", (raportare_id,))
        if not cur.fetchone():
            return {"ok": False, "cod": "INEXISTENT"}
        cur.execute(
            "INSERT INTO public.raportari_mesaje (raportare_id, autor_id, rol_autor, text, citit) "
            "VALUES (%s,%s,%s,%s,%s) RETURNING id",
            (raportare_id, autor_id, rol_autor, text.strip(), not veste))
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
    # fisierele tuturor mesajelor din fir, intr-o singura interogare (numele, nu calea: se descarca prin ruta autentificata)
    atas = _fp.ale_mesajelor(cur, [r["id"] for r in randuri])
    out = []
    for r in randuri:
        out.append({
            "id": r["id"], "rol_autor": r["rol_autor"], "text": r["text"],
            "citit": r["citit"], "cand": r["creat_la"].isoformat(),
            "autor": _nume(r["prenume"], r["nume"], r["email"]),
            "atasamente": atas.get(r["id"], []),
        })
    return out


def autor_mesajului(conn, mesaj_id):
    """Cine a scris mesajul + firul lui (felul, cabinetul) — pt verificarea accesului la incarcarea unui fisier."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT m.autor_id, m.raportare_id, r.autor_id, r.tip, r.cabinet_id "
            "  FROM public.raportari_mesaje m "
            "  JOIN public.raportari r ON r.id = m.raportare_id "
            " WHERE m.id = %s", (mesaj_id,))
        r = cur.fetchone()
    if not r:
        return None
    return {"mesaj_autor": r[0], "raportare_id": r[1], "fir_autor": r[2], "tip": r[3], "cabinet_id": r[4]}


def raportarile_mele(conn, autor_id):
    """Firele deschise de mine + mesaje. Contor = raspunsuri admin necitite (bec rosu)."""
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            "SELECT id, subiect, stare, tip, aplicatie, creat_la, ultim_mesaj_la, stare_necitita "
            "  FROM public.raportari WHERE autor_id = %s ORDER BY ultim_mesaj_la DESC",
            (autor_id,))
        fire = [dict(r) for r in cur.fetchall()]
        rez, necitite = [], 0
        for f in fire:
            mesaje = _mesaje_firului(cur, f["id"])
            # [deficiența 291] „de citit” = vești de la iConta pe care autorul nu le-a văzut: răspunsuri necitite (admin / AI) și
            # schimbarea stării din Panou Admin — nu cererea lui (până la 16.10 era invers: 1 pe orice fir FĂRĂ răspuns)
            nc = sum(1 for m in mesaje if m["rol_autor"] in ROLURI_ICONTA and not m.get("citit")) + (1 if f["stare_necitita"] else 0)
            necitite += nc
            rez.append({
                "id": f["id"], "subiect": f["subiect"], "stare": f["stare"],
                "tip": f["tip"], "aplicatie": f["aplicatie"],
                "creat_la": f["creat_la"].isoformat(),
                "ultim_mesaj_la": f["ultim_mesaj_la"].isoformat(),
                "necitite": nc, "mesaje": mesaje,
            })
    return {"ok": True, "raportari": rez, "necitite_total": necitite}


def marcheaza_citit(conn, raportare_id, cine_rol):
    """Marcheaza citite mesajele celuilalt rol (stinge becul).
    cine_rol='utilizator' -> citeste mesajele de la iConta (admin și asistentul AI — [291] AI-ul rămânea necitit) și schimbarea stării;
    invers pt admin."""
    celalalt = ROLURI_ICONTA if cine_rol == "utilizator" else ("utilizator",)
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE public.raportari_mesaje SET citit = true "
            "WHERE raportare_id = %s AND rol_autor = ANY(%s) AND citit = false",
            (raportare_id, list(celalalt)))
        if cine_rol == "utilizator":
            cur.execute("UPDATE public.raportari SET stare_necitita = false WHERE id = %s", (raportare_id,))
    return {"ok": True}


def contor_necitite(conn, autor_id):
    """Cifra rosie = firele mele cu vești de la iConta pe care nu le-am văzut: un răspuns necitit (admin sau AI) sau starea schimbată din
    Panou Admin. [deficiența 291, comanda Costin 16.10.2026, verbatim în DECIZII] „Bulina anunță un răspuns sau o schimbare de stare
    venită de la iConta, nu propria cerere.” Până azi număra cererile MELE în așteptare (`stare = 'noua'`): se aprindea la trimitere."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) FROM public.raportari r "
            " WHERE r.autor_id = %s AND (r.stare_necitita OR EXISTS (SELECT 1 FROM public.raportari_mesaje m "
            "       WHERE m.raportare_id = r.id AND m.rol_autor = ANY(%s) AND NOT m.citit))",
            (autor_id, list(ROLURI_ICONTA)))
        n = cur.fetchone()[0]
    return {"ok": True, "necitite": int(n)}


# ---- ADMIN iConta (superadmin): vede toate raportarile ----
def toate_raportarile(conn):
    """Pentru Admin iConta: toate firele, cu autor + cabinet + nr mesaje + necitite admin."""
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            "SELECT r.id, r.subiect, r.stare, r.tip, r.aplicatie, r.creat_la, r.ultim_mesaj_la, "
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
                "tip": r["tip"], "aplicatie": r["aplicatie"],
                "creat_la": r["creat_la"].isoformat(),
                "ultim_mesaj_la": r["ultim_mesaj_la"].isoformat(),
                "autor": _nume(r["prenume"], r["nume"], r["email"]),
                "cabinet": r["cabinet"], "necitite": int(r["necitite"] or 0),
                "pentru_admin": bool(r["pentru_admin"]),  # [p38_pentru_admin]
                "text": (r["text"] or ""),  # [p40_text_lista]
            })
    return {"ok": True, "raportari": fire}


def firul_complet(conn, raportare_id, cerut_de_uid=None, e_superadmin=False):
    """Un fir cu toate mesajele (pt admin sau pt detaliu).
    [izolare_raportari 09.08.2026] Aparare de DATE sub garda de ruta (care RAMANE): daca cerut_de_uid
    e dat si NU superadmin, SQL adauga AND autor_id=cerut_de_uid -> data-layer = garda pe AUTOR, FARA
    relaxare la cabinet. Fara context (apel superadmin/intern) ramane pe id. Vezi test_izolare_raportari.py."""
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        _baza = (
            "SELECT r.id, r.subiect, r.stare, r.tip, r.aplicatie, r.autor_id, "
            "       u.prenume, u.nume, u.email, af.nume AS cabinet "
            "  FROM public.raportari r "
            "  LEFT JOIN public.users u ON u.id = r.autor_id "
            "  LEFT JOIN public.accounting_firms af ON af.id = r.cabinet_id "
            " WHERE r.id = %s")
        if cerut_de_uid is not None and not e_superadmin:
            cur.execute(_baza + " AND r.autor_id = %s", (raportare_id, cerut_de_uid))
        else:
            cur.execute(_baza, (raportare_id,))
        f = cur.fetchone()
        if not f:
            return {"ok": False, "cod": "INEXISTENT"}
        mesaje = _mesaje_firului(cur, raportare_id)
    return {"ok": True, "raportare": {
        "id": f["id"], "subiect": f["subiect"], "stare": f["stare"],
        "tip": f["tip"], "aplicatie": f["aplicatie"],
        "autor_id": f["autor_id"],
        "autor": _nume(f["prenume"], f["nume"], f["email"]),
        "cabinet": f["cabinet"], "mesaje": mesaje,
        "text": next((m["text"] for m in mesaje if m.get("rol_autor") == "utilizator"), "")}}  # [titlu_fir]


# [inchidere_v1] inchiderea unei sesizari (fara stergere - istoricul ramane in DB)
def seteaza_stare(conn, raportare_id, stare):
    if stare not in ("noua", "raspuns", "inchisa"):
        return {"ok": False, "cod": "STARE_INVALIDA"}
    with conn.cursor() as cur:
        # [291] schimbarea stării din Panou Admin e o veste pentru autor (bulina), până deschide firul
        cur.execute("UPDATE public.raportari SET stare_necitita = stare_necitita OR stare IS DISTINCT FROM %s, stare = %s WHERE id = %s "
                    "RETURNING id", (stare, stare, raportare_id))
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
