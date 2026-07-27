"""GDPR art.33 (pregatire) — alerta acces anormal pe public.audit_log.
Detecteaza un user care atinge un numar NEOBISNUIT de tenanti/actiuni intr-o fereastra
scurta. NU blocheaza — doar semnaleaza (fals-pozitive OK, ratarea nu). Brevo la
ICONTA_ALERTA_EMAIL, cu dedup PERSISTENT (public.alerte_acces_dedup) ca sa nu spameze
intre rulari cron. Praguri configurabile prin env. Rulat din cron (la 15 min)."""
import os
from core import db, observare

def _int(env, d):
    try: return max(1, int(os.environ.get(env, str(d))))
    except (ValueError, TypeError): return d

def praguri():
    return {"fereastra_min": _int("ACCES_FEREASTRA_MIN", 10),
            "prag_tenanti": _int("ACCES_PRAG_TENANTI", 8),
            "prag_actiuni": _int("ACCES_PRAG_ACTIUNI", 300),
            "dedup_min": _int("ACCES_DEDUP_MIN", 60)}

def detecteaza(conn, fereastra_min, prag_tenanti, prag_actiuni):
    with conn.cursor() as cur:
        cur.execute("""SELECT user_id, count(DISTINCT tenant_id) AS t, count(*) AS a
                       FROM public.audit_log
                       WHERE created_at > now() - make_interval(mins => %s) AND user_id IS NOT NULL
                       GROUP BY user_id
                       HAVING count(DISTINCT tenant_id) >= %s OR count(*) >= %s
                       ORDER BY t DESC, a DESC""", (fereastra_min, prag_tenanti, prag_actiuni))
        return [{"user_id": r[0], "tenanti": r[1], "actiuni": r[2]} for r in cur.fetchall()]

def _poate_trimite(conn, cheie, dedup_min):
    with conn.cursor() as cur:
        cur.execute("""INSERT INTO public.alerte_acces_dedup (cheie, trimis_la) VALUES (%s, now())
                       ON CONFLICT (cheie) DO UPDATE SET trimis_la = now()
                       WHERE public.alerte_acces_dedup.trimis_la < now() - make_interval(mins => %s)
                       RETURNING cheie""", (cheie, dedup_min))
        return cur.fetchone() is not None

def ruleaza(trimite=None, **override):
    p = praguri()
    for k, v in override.items():
        if v is not None and k in p: p[k] = v
    trimite = trimite or observare._trimite_brevo
    try: db.pool()
    except Exception: db.init_pool()
    alerte = 0
    with db.get_conn() as c:
        flagged = detecteaza(c, p["fereastra_min"], p["prag_tenanti"], p["prag_actiuni"])
        for u in flagged:
            cheie = "acces_anormal_user_%s" % u["user_id"]
            if _poate_trimite(c, cheie, p["dedup_min"]):
                subiect = "Acces anormal: user %s (%s tenanti, %s actiuni / %s min)" % (
                    u["user_id"], u["tenanti"], u["actiuni"], p["fereastra_min"])
                mesaj = ("Semnal automat (art.33): userul %s a atins %s tenanti distincti si %s actiuni "
                         "in ultimele %s min (praguri %s tenanti / %s actiuni). NU s-a blocat nimic. Verifica manual."
                         % (u["user_id"], u["tenanti"], u["actiuni"], p["fereastra_min"], p["prag_tenanti"], p["prag_actiuni"]))
                trimite(subiect, mesaj); alerte += 1
        c.commit()
    return {"verificati": len(flagged), "alerte_trimise": alerte, "praguri": p}

if __name__ == "__main__":
    import json, datetime
    from core import cron
    cron.ruleaza("alerta_acces", lambda: print("%s alerta_acces: %s" % (datetime.datetime.now().isoformat(timespec="seconds"), json.dumps(ruleaza()))))
