"""
core/auth_api.py — autentificare API: login, register, context token, acces tenant.
Strat SUBȚIRE peste nucleu.py (pur) + db.py (pool). Aliniat la schema reală
public.users / public.tenants / public.user_tenants de pe iconta-prod.

Compatibilitate parole (DRUM A):
  Userii existenți au hash BCRYPT ($2b$12$...). nucleu.py știe doar scrypt.
  -> verifica_parola_orice() detectează formatul și verifică pe cel potrivit.
  -> userii vechi se loghează în continuare; la următoarea schimbare de parolă
     se face rehash în scrypt (nucleu.hash_parola). Migrare lină, nimeni resetat.

nucleu.py rămâne NEATINS (scrypt pentru parole noi). Adaptarea stă la margine.

Roluri: baza are 4 (superadmin/admin_firma/angajat/client). nucleu.ROLURI are 3.
  -> login NU filtrează pe rol; emite token cu rolul din DB.

Se dovedește pe server (parte DB): query users/tenants/user_tenants.
"""
from __future__ import annotations

from core import nucleu, db
from core.common import cfg, cfg_secret

REGULI = "2026.1"
MODUL = "auth_api"

# JWT_SECRET = SECRET de semnare token — citit LA APEL prin cfg_secret (EXCEPȚIE DURĂ la absență/gol,
# NICIODATĂ default: un secret gol face tokenurile forjabile, bypass de auth). DURATA_TOKEN_SEC = durată
# (nu secret), lazy prin cfg. Vezi DECIZII 22.07.

_BCRYPT_PREFIX = ("$2a$", "$2b$", "$2y$")


# ============================================================
#  PAROLĂ dual-format — PURĂ (testabilă fără DB)
# ============================================================
def verifica_parola_orice(parola, hash_stocat):
    """
    Verifică parola contra hash-ului, indiferent de format:
      - $2a/$2b/$2y -> bcrypt (userii vechi)
      - scrypt$...  -> nucleu.verifica_parola (userii noi)
    Întoarce True/False. Nu aruncă pe hash necunoscut (întoarce False).
    """
    if not hash_stocat:
        return False
    if hash_stocat.startswith(_BCRYPT_PREFIX):
        import bcrypt
        try:
            return bcrypt.checkpw(parola.encode("utf-8"), hash_stocat.encode("utf-8"))
        except (ValueError, TypeError):
            return False
    if hash_stocat.startswith("scrypt$"):
        return nucleu.verifica_parola(parola, hash_stocat)
    return False


def e_bcrypt(hash_stocat):
    """True dacă hash-ul e bcrypt (deci candidat la rehash scrypt). Pură."""
    return bool(hash_stocat) and hash_stocat.startswith(_BCRYPT_PREFIX)


# ============================================================
#  PAYLOAD TOKEN — PURĂ
# ============================================================
def construieste_payload(user_row):
    """
    Din rândul user (dict) construiește payload-ul token (doar ce e necesar).
    NU pune email/nume în token — minim necesar pentru autorizare.
    """
    p = {
        "uid": user_row["id"],
        "rol": user_row["rol"],
        "firm": user_row.get("accounting_firm_id"),
    }
    if user_row.get("preview"):  # [F-preview] token de previzualizare portal (read-only), tab-local
        p["preview"] = True
    return p


def emite_token(user_row, secret=None, durata=None, acum=None):
    """Emite token semnat pentru un user. Pură (delegă la nucleu)."""
    secret = cfg_secret("JWT_SECRET") if secret is None else secret
    durata = cfg("ICONTA_TOKEN_DURATA_SEC", str(8 * 3600), int) if durata is None else durata
    return nucleu.creeaza_token(construieste_payload(user_row), secret,
                                durata_sec=durata, acum=acum)


def context_din_token(token, secret=None, acum=None):
    """
    Verifică token-ul, întoarce contextul {ok, uid, rol, firm} sau {ok:False,...}.
    Rutele cer asta la fiecare request protejat.
    """
    secret = cfg_secret("JWT_SECRET") if secret is None else secret
    r = nucleu.verifica_token(token, secret, acum=acum)
    if not r["ok"]:
        return r
    p = r["payload"]
    return {"ok": True, "uid": p.get("uid"), "rol": p.get("rol"), "firm": p.get("firm"),
            "iat": p.get("iat"),  # [reset_parola_v1] pt invalidarea sesiunilor la schimbarea parolei
            "preview": bool(p.get("preview"))}  # [F-preview] read-only enforcement pe backend


# ============================================================
#  LOGIN — parte DB (se dovedește pe server)
# ============================================================
def _tenant_client(conn, u):
    """Pentru un CLIENT: (nume_tenant, tenant_are_cabinet) din tenantul lui (user_tenants, LIMIT 1).
    tenant_are_cabinet = tenantul e gestionat de un cabinet (accounting_firm_id setat). Determinarea
    gratuit-vs-cabinet e la nivel de TENANT, NU user.firm (care e NULL la ORICE client, deci nu putea
    distinge gratuit de client-portal gestionat). Vezi DECIZII.md 18.07 F161. Non-client -> (None, False)."""
    import psycopg2.extras as _E
    if u["rol"] != "client":
        return None, False
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            "SELECT t.nume, t.accounting_firm_id FROM public.user_tenants ut "
            "JOIN public.tenants t ON t.id = ut.tenant_id "
            "WHERE ut.user_id = %s ORDER BY ut.tenant_id LIMIT 1", (u["id"],))
        row = cur.fetchone()
    if not row:
        return None, False
    return row["nume"], bool(row["accounting_firm_id"])


def sesiune_pentru_user(conn, user_id, secret=None):
    """Emite token + user pentru un user_id deja autentificat (magic link). # sesiune_pentru_user_v1"""
    import psycopg2.extras as _E
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            "SELECT u.id, u.email, u.nume, u.prenume, u.rol, u.accounting_firm_id, u.activ, "
            "u.poate_pregati, u.poate_valida, u.poate_depune, u.bun_venit_vazut_la, "
            "af.nume AS nume_firma, af.activ AS firma_activa "
            "FROM public.users u "
            "LEFT JOIN public.accounting_firms af ON af.id = u.accounting_firm_id "
            "WHERE u.id = %s", (user_id,))
        u = cur.fetchone()
    if not u or not u["activ"]:
        return {"ok": False, "cod": "AUTH_ESEC", "mesaj": "cont inexistent sau inactiv"}
    if u["accounting_firm_id"] and u["firma_activa"] is False:
        return {"ok": False, "cod": "CABINET_SUSPENDAT", "mesaj": "Cabinetul este suspendat."}
    token = emite_token(u, secret=secret)
    nume_tenant, tenant_are_cabinet = _tenant_client(conn, u)
    return {"ok": True, "token": token,
            "user": {"id": u["id"], "rol": u["rol"],
                     "nume": u.get("nume"), "prenume": u.get("prenume"),
                     "firm": u["accounting_firm_id"],
                     "nume_firma": u.get("nume_firma"),
                     "nume_tenant": nume_tenant,
                     "tenant_are_cabinet": tenant_are_cabinet,
                     "poate_pregati": bool(u.get("poate_pregati")),
                     "poate_valida": bool(u.get("poate_valida")),
                     "poate_depune": bool(u.get("poate_depune")),
                     "bun_venit_vazut": bool(u.get("bun_venit_vazut_la"))}}


def login(conn, email, parola, secret=None):
    """
    Caută userul după email, verifică activ + parolă (dual format), emite token.
    Întoarce {ok, token, user:{id,rol,nume,firm}} sau {ok:False, cod, mesaj}.
    Mesaj generic la eșec (nu divulgăm dacă emailul există).
    """
    import psycopg2.extras as _E
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(  # [p20_sursa_unica]
            "SELECT u.id, u.email, u.password_hash, u.nume, u.prenume, u.rol, "
            "u.accounting_firm_id, u.activ, "
            "u.poate_pregati, u.poate_valida, u.poate_depune, u.bun_venit_vazut_la, "
            "af.nume AS nume_firma, af.activ AS firma_activa "  # ICRD_CABINETE_CONSOLIDAT_LOGIN_V1
            "FROM public.users u "
            "LEFT JOIN public.accounting_firms af ON af.id = u.accounting_firm_id "
            "WHERE u.email = %s",
            (email,))
        u = cur.fetchone()

    if not u or not u["activ"]:
        return {"ok": False, "cod": "AUTH_ESEC", "mesaj": "email sau parolă greșite"}
    if u["accounting_firm_id"] and u["firma_activa"] is False:
        return {"ok": False, "cod": "CABINET_SUSPENDAT", "mesaj": "Cabinetul este suspendat. Contactați furnizorul."}
    if not verifica_parola_orice(parola, u["password_hash"]):
        return {"ok": False, "cod": "AUTH_ESEC", "mesaj": "email sau parolă greșite"}

    token = emite_token(u, secret=secret)
    # [[p90_client_bara]] pentru client: numele firmei lui (tenant) + daca e gestionat de cabinet
    nume_tenant, tenant_are_cabinet = _tenant_client(conn, u)
    return {"ok": True, "token": token,
            "user": {"id": u["id"], "rol": u["rol"],
                     "nume": u.get("nume"), "prenume": u.get("prenume"),
                     "firm": u["accounting_firm_id"],
                     "nume_firma": u.get("nume_firma"),
                     "nume_tenant": nume_tenant,
                     "tenant_are_cabinet": tenant_are_cabinet,
                     "poate_pregati": bool(u.get("poate_pregati")),
                     "poate_valida": bool(u.get("poate_valida")),
                     "poate_depune": bool(u.get("poate_depune")),
                     "bun_venit_vazut": bool(u.get("bun_venit_vazut_la"))},
            "rehash_recomandat": e_bcrypt(u["password_hash"])}


def marcheaza_bun_venit(conn, user_id):
    """Marcheaza pagina de bun-venit ca vazuta (o data). Idempotent: seteaza doar daca era NULL."""
    with conn.cursor() as cur:
        cur.execute("UPDATE public.users SET bun_venit_vazut_la = now() "
                    "WHERE id = %s AND bun_venit_vazut_la IS NULL", (user_id,))
    return {"ok": True}


# [p27_setari]
def actualizeaza_profil(conn, user_id, nume=None, prenume=None):
    """Actualizeaza nume/prenume. Intoarce {ok, user} cu datele noi (pt sesiune)."""
    import psycopg2.extras as _E
    sets, par = [], []
    if nume is not None:
        sets.append("nume = %s"); par.append(nume.strip())
    if prenume is not None:
        sets.append("prenume = %s"); par.append(prenume.strip())
    if not sets:
        return {"ok": False, "cod": "NIMIC_DE_SCHIMBAT"}
    par.append(user_id)
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute("UPDATE public.users SET " + ", ".join(sets) +
                    " WHERE id = %s RETURNING id, email, nume, prenume, rol, "
                    "accounting_firm_id, poate_pregati, poate_valida, poate_depune, bun_venit_vazut_la",
                    tuple(par))
        u = cur.fetchone()
    if not u:
        return {"ok": False, "cod": "USER_INEXISTENT"}
    # nume_firma pentru sursa unica (bara 1)
    with conn.cursor() as cur:
        cur.execute("SELECT nume FROM public.accounting_firms WHERE id = %s",
                    (u["accounting_firm_id"],))
        r = cur.fetchone()
        nume_firma = r[0] if r else None
    return {"ok": True, "user": {
        "id": u["id"], "rol": u["rol"], "nume": u.get("nume"),
        "prenume": u.get("prenume"), "firm": u["accounting_firm_id"],
        "nume_firma": nume_firma,
        "poate_pregati": bool(u.get("poate_pregati")),
        "poate_valida": bool(u.get("poate_valida")),
        "poate_depune": bool(u.get("poate_depune")),
                     "bun_venit_vazut": bool(u.get("bun_venit_vazut_la"))}}


def schimba_parola(conn, user_id, parola_noua):
    """
    Setează parolă nouă cu SCRYPT (nucleu). Folosit la rehash-ul userilor bcrypt
    sau la schimbare normală. Marchează parola_schimbata=true.
    """
    h = nucleu.hash_parola(parola_noua)
    with conn.cursor() as cur:
        cur.execute("UPDATE public.users SET password_hash = %s, "
                    "parola_schimbata = true WHERE id = %s", (h, user_id))
    return {"ok": True}


# ============================================================
#  REGISTER — self-service cabinet (ca vechiul /register)
# ============================================================
# [p29_cabinet]
def get_cabinet(conn, firm_id):
    """Datele cabinetului (nume, cui)."""
    import psycopg2.extras as _E
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute("SELECT id, nume, cui FROM public.accounting_firms WHERE id = %s", (firm_id,))
        r = cur.fetchone()
    return {"ok": True, "cabinet": dict(r)} if r else {"ok": False, "cod": "INEXISTENT"}


def actualizeaza_cabinet(conn, firm_id, nume=None, cui=None):
    """Actualizeaza nume/cui cabinet."""
    import psycopg2.extras as _E
    sets, par = [], []
    if nume is not None:
        sets.append("nume = %s"); par.append(nume.strip())
    if cui is not None:
        sets.append("cui = %s"); par.append((cui or "").strip() or None)
    if not sets:
        return {"ok": False, "cod": "NIMIC_DE_SCHIMBAT"}
    par.append(firm_id)
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute("UPDATE public.accounting_firms SET " + ", ".join(sets) +
                    " WHERE id = %s RETURNING id, nume, cui", tuple(par))
        r = cur.fetchone()
    return {"ok": True, "cabinet": dict(r)} if r else {"ok": False, "cod": "INEXISTENT"}


def inregistreaza_cabinet(conn, email, parola, nume_cabinet, nume=None, prenume=None):
    """
    Creează un cabinet nou (accounting_firms) + user admin_firma (scrypt).
    Respectă chk_firm_required (admin_firma cere accounting_firm_id).
    Întoarce {ok, user_id, firm_id} sau {ok:False, cod, mesaj}.
    """
    import psycopg2.extras as _E
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute("SELECT 1 FROM public.users WHERE email = %s", (email,))
        if cur.fetchone():
            return {"ok": False, "cod": "EMAIL_EXISTA", "mesaj": "email deja înregistrat"}
        cur.execute("INSERT INTO public.accounting_firms (nume) VALUES (%s) RETURNING id",
                    (nume_cabinet,))
        firm_id = cur.fetchone()["id"]
        h = nucleu.hash_parola(parola)
        cur.execute(
            # [B3 06.08.2026] proprietarul cabinetului (radacina) primeste drepturile operationale la
            # creare: nimeni deasupra nu i le poate acorda, iar un cabinet solo are nevoie de tot lantul
            # pregatire->validare->depunere. Personalul suplimentar primeste drepturi separat (Asistenti).
            "INSERT INTO public.users (email, password_hash, nume, prenume, rol, "
            "accounting_firm_id, poate_pregati, poate_valida, poate_depune) "
            "VALUES (%s,%s,%s,%s,'admin_firma',%s,true,true,true) RETURNING id",
            (email, h, nume, prenume, firm_id))
        user_id = cur.fetchone()["id"]
    return {"ok": True, "user_id": user_id, "firm_id": firm_id}


# ============================================================
#  ACCES TENANT — izolare: userul vede DOAR tenanții lui
# ============================================================
def _rol_si_firma(conn, user_id):
    """(rol, accounting_firm_id) ale userului, sau (None, None)."""
    with conn.cursor() as cur:
        cur.execute("SELECT rol, accounting_firm_id FROM public.users WHERE id = %s", (user_id,))
        r = cur.fetchone()
    return (r[0], r[1]) if r else (None, None)


def schema_tenant(conn, user_id, tenant_id):
    """
    Întoarce schema_name a tenantului dacă userul are acces, altfel None.
      - superadmin: orice firmă activă
      - admin_firma: firmele cabinetului lui (accounting_firm_id)
      - restul (angajat/client): doar prin user_tenants
    """
    rol, firm = _rol_si_firma(conn, user_id)
    with conn.cursor() as cur:
        if rol == "superadmin":
            # GDPR: superadmin acceseaza continut DOAR pentru conturi gratuite (fara cabinet).
            cur.execute("SELECT schema_name FROM public.tenants WHERE id = %s AND accounting_firm_id IS NULL AND activ = true", (tenant_id,))
        elif rol == "admin_firma":
            cur.execute("SELECT schema_name FROM public.tenants WHERE id = %s AND accounting_firm_id = %s AND activ = true",
                        (tenant_id, firm))
        else:
            cur.execute(
                "SELECT t.schema_name FROM public.tenants t "
                "JOIN public.user_tenants ut ON ut.tenant_id = t.id "
                "WHERE ut.user_id = %s AND t.id = %s AND t.activ = true",
                (user_id, tenant_id))
        row = cur.fetchone()
    return row[0] if row else None


def tenantii_userului(conn, user_id):
    """
    Lista tenanților la care userul are acces: [{id, nume, schema_name, cui, activ}].
      - superadmin: toate firmele active
      - admin_firma: firmele cabinetului lui
      - restul: doar prin user_tenants
    """
    import psycopg2.extras as _E
    rol, firm = _rol_si_firma(conn, user_id)
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        if rol == "superadmin":
            # GDPR: superadmin vede in lista DOAR conturi gratuite (fara cabinet).
            cur.execute("SELECT id, nume, schema_name, cui, activ FROM public.tenants "
                        "WHERE accounting_firm_id IS NULL AND activ = true ORDER BY nume")
        elif rol == "admin_firma":
            cur.execute("SELECT id, nume, schema_name, cui, activ FROM public.tenants "
                        "WHERE accounting_firm_id = %s AND activ = true ORDER BY nume", (firm,))
        else:
            cur.execute(
                "SELECT t.id, t.nume, t.schema_name, t.cui, t.activ FROM public.tenants t "
                "JOIN public.user_tenants ut ON ut.tenant_id = t.id "
                "WHERE ut.user_id = %s AND t.activ = true ORDER BY t.nume",
                (user_id,))
        lista = [dict(r) for r in cur.fetchall()]
    # [tip_firma_v1] tip_firma traieste in {schema}.firma_profil (schema-per-tenant),
    # nu in public.tenants -> il aducem per firma. Default 'srl' daca profilul lipseste.
    with conn.cursor() as cur:
        for t in lista:
            # savepoint per firma: o interogare esuata (schema fara firma_profil)
            # abortul tranzactiei psycopg2 -> altfel toate firmele urmatoare ar cadea pe 'srl'
            try:
                cur.execute("SAVEPOINT sp_tip")
                cur.execute(f'SELECT tip_firma FROM "{t["schema_name"]}".firma_profil WHERE id=1')
                row = cur.fetchone()
                from core.migrare_api import tip_firma_nrm  # default 'srl' -> UNICA primitiva, nu literal inline
                t["tip_firma"] = tip_firma_nrm(row[0] if row else None)
                cur.execute("RELEASE SAVEPOINT sp_tip")
            except Exception:
                from core.migrare_api import tip_firma_nrm
                cur.execute("ROLLBACK TO SAVEPOINT sp_tip")
                t["tip_firma"] = tip_firma_nrm(None)  # firma fara profil -> srl (partida dubla), prin primitiva
            # [regim] expune FAPTUL existent (partida simpla/dubla) derivat din tip_firma - frontendul nu-l
            # recalculeaza si nu defaulteaza regim inline. Nicio regula noua, doar expunere. Vezi DECIZII 23.07.
            from core.migrare_api import regim_contabil
            t["regim_contabil"] = regim_contabil(t["tip_firma"])
    return lista
