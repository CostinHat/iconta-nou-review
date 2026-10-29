"""GDPR art.33 (pregatire) — alerta acces anormal pe public.audit_log.
Detecteaza un user care atinge un numar NEOBISNUIT de tenanti/actiuni intr-o fereastra
scurta. NU blocheaza — doar semnaleaza (fals-pozitive OK, ratarea nu). Brevo la
ICONTA_ALERTA_EMAIL, cu dedup PERSISTENT (public.alerte_acces_dedup) ca sa nu spameze
intre rulari cron. Praguri configurabile prin env. Rulat din cron (la 15 min)."""
import os
from core import audit_automat as _audit_automat, db, observare

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
        # [715, 14.2] Numără acțiunile omului: cererile de pornire ale ecranelor (vezi `core/audit_automat`, regula la citire) și conturile
        # cabinetelor marcate „de test” (testele noastre, verificatorul) nu intră. Fără ele, un singur ecran deschis însemna zeci de „acțiuni”.
        cur.execute("""SELECT l.user_id, count(DISTINCT l.tenant_id) AS t, count(*) AS a
                       FROM public.audit_log l
                       LEFT JOIN public.users u ON u.id = l.user_id
                       LEFT JOIN public.accounting_firms f ON f.id = u.accounting_firm_id
                       WHERE l.created_at > now() - make_interval(mins => %s) AND l.user_id IS NOT NULL
                         AND """ + _audit_automat.sql_actiune_omului("l") + """
                         AND NOT COALESCE(f.de_test, false)   -- [715.1, 14.3] cabinetul de test e MARCAT în Panou Admin, nu ghicit după nume
                       GROUP BY l.user_id
                       HAVING count(DISTINCT l.tenant_id) >= %s OR count(*) >= %s
                       ORDER BY t DESC, a DESC""", (fereastra_min, *_audit_automat.PARAM_OMULUI, prag_tenanti, prag_actiuni))
        flagged = [{"user_id": r[0], "tenanti": r[1], "actiuni": r[2]} for r in cur.fetchall()]
        for u in flagged:   # [715] alerta numește omul și cabinetul, nu doar numărul
            cur.execute("""SELECT trim(coalesce(u.prenume,'') || ' ' || coalesce(u.nume,'')), u.email, f.nume
                           FROM public.users u LEFT JOIN public.accounting_firms f ON f.id = u.accounting_firm_id
                           WHERE u.id = %s""", (u["user_id"],))
            r = cur.fetchone()
            u["nume"], u["email"], u["cabinet"] = (r or (None, None, None))
        return flagged

def _poate_trimite(cheie, dedup_min):
    """Rezerva fereastra de dedup pentru `cheie`, IN TRANZACTIA EI, comisa. [P4, 09.09.2026]

    Ce era pana azi: rezervarea se scria pe conexiunea apelantului, iar `ruleaza` comitea abia la
    capatul buclei — dupa ce alertele plecasera deja prin Brevo. O eroare la orice pas de dupa
    intorcea tranzactia: alertele trimise ramaneau trimise, randurile care le opreau nu. La
    urmatoarea rulare (cron la 15 minute) plecau din nou, la fel.

    `rollback`-ul nu desface un e-mail. Deci randul care il opreste se comite INAINTEA lui —
    acelasi tipar ca `efactura_send.trimite`, care scrie randul `pregatit` si abia apoi incarca."""
    with db.get_conn() as conn, conn.cursor() as cur:
        # upsert-ok: dedup alerta pe cheie cu fereastra (WHERE trimis_la<...) - reset intentionat
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
    de_trimis = []
    with db.get_conn() as c:
        flagged = detecteaza(c, p["fereastra_min"], p["prag_tenanti"], p["prag_actiuni"])
    # [P4] `c` nu scria nimic: detectia e o citire, iar rezervarea isi ia tranzactia ei. [C201, lotul 13] Deci citirea se inchide
    # INAINTE de rezervari: cat timp `c` era tinut, fiecare `_poate_trimite` era a doua conexiune a aceluiasi fir.
    for u in flagged:
        cheie = "acces_anormal_user_%s" % u["user_id"]
        if _poate_trimite(cheie, p["dedup_min"]):
            cine = "%s (%s)" % (u.get("nume") or "utilizator necunoscut", u.get("email") or "fără email")
            cabinet = u.get("cabinet") or "fără cabinet"
            firme = "%s %s" % (u["tenanti"], "firmă" if u["tenanti"] == 1 else "firme")   # [715] „1 firmă”
            subiect = "Acces anormal: %s, cabinetul %s (%s, %s acțiuni în %s min)" % (   # [317, lotul 12] cu diacritice
                cine, cabinet, firme, u["actiuni"], p["fereastra_min"])
            mesaj = ("Semnal automat (art.33): utilizatorul %s, cabinetul %s (id %s), a atins %s distincte și %s acțiuni "
                     "în ultimele %s min (praguri %s firme / %s acțiuni). Nu s-a blocat nimic. Verifică manual."
                     % (cine, cabinet, u["user_id"], firme, u["actiuni"], p["fereastra_min"], p["prag_tenanti"], p["prag_actiuni"]))
            de_trimis.append((subiect, mesaj))
    # [P5 val 3, 11.09.2026] TRIMITEREA, AICI: apelul la Brevo are termen de 10 s, iar forma
    # dinainte il facea in bucla, cu conexiunea in mana — cate 10 s pentru fiecare alerta. Ordinea
    # ramane aceeasi: rezervarea de dedup s-a facut deja mai sus, deci nici numarul de alerte, nici
    # continutul, nici conditia nu se schimba.
    for subiect, mesaj in de_trimis:
        trimite(subiect, mesaj)
        alerte += 1
    return {"verificati": len(flagged), "alerte_trimise": alerte, "praguri": p}

if __name__ == "__main__":
    import json, datetime
    from core import cron
    cron.ruleaza("alerta_acces", lambda: print("%s alerta_acces: %s" % (datetime.datetime.now().isoformat(timespec="seconds"), json.dumps(ruleaza()))))
