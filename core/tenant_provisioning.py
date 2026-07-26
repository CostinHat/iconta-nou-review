"""
core/tenant_provisioning.py — creează un tenant nou: schemă PostgreSQL + cele 21
de tabele (din template) + rândul în public.tenants + legarea userului.

Template-ul (tenant_template.sql) e generat o dată din tenant_001 (schema reală,
validată). Aici: generăm numele schemei noi, parametrizăm template-ul (înlocuim
numele schemei sursă), și provisionăm totul într-o singură tranzacție.

Pur (testabil fără DB): urmator_schema_name, parametrizeaza_template.
DB (se dovedește pe server): creeaza_schema, provision_tenant.
"""
from __future__ import annotations
import re

from core import db

REGULI = "2026.1"
MODUL = "tenant_provisioning"

SCHEMA_SURSA = "TENANT_PLACEHOLDER"   # schema din care s-a generat template-ul
_RE_TENANT_NR = re.compile(r"^tenant_(\d+)$")


# ============================================================
#  GENERARE schema_name — PURĂ
# ============================================================
def urmator_schema_name(existente, lat=3):
    """
    Dat lista numelor de scheme existente, întoarce următorul 'tenant_NNN' liber.
    Ia max(NNN)+1; dacă nu există niciuna, începe de la 1.
    """
    maxn = 0
    for s in existente or []:
        m = _RE_TENANT_NR.match(s or "")
        if m:
            maxn = max(maxn, int(m.group(1)))
    return "tenant_%0*d" % (lat, maxn + 1)


# ============================================================
#  PARAMETRIZARE template — PURĂ
# ============================================================
def parametrizeaza_template(sql_template, schema_noua, schema_sursa=SCHEMA_SURSA):
    """
    Transformă template-ul (dump al schemei sursă) într-un script rulabil pentru
    schema nouă: înlocuiește numele schemei + scoate meta-comenzile psql (\\...)
    și resetarea search_path (inofensivă, dar evităm efecte pe conexiune).
    """
    linii = []
    for ln in sql_template.splitlines():
        s = ln.strip()
        if s.startswith("\\"):                       # \restrict, \unrestrict, etc.
            continue
        if "set_config('search_path'" in s:           # nu atingem search_path conexiunii
            continue
        linii.append(ln)
    sql = "\n".join(linii)
    # înlocuiește numele schemei (prefix calificat: schema.tabela + CREATE SCHEMA)
    sql = sql.replace(schema_sursa, schema_noua)
    return sql


# ============================================================
#  CREARE schemă — DB (se dovedește pe server)
# ============================================================
def creeaza_schema(conn, schema_noua, sql_template):
    """Rulează SQL-ul parametrizat care creează schema + tabelele. Nu face commit
    (lasă tranzacția deschisă pentru provision_tenant)."""
    if not db.schema_valida(schema_noua):
        raise ValueError("schema invalidă: %r" % schema_noua)
    sql = parametrizeaza_template(sql_template, schema_noua)
    with conn.cursor() as cur:
        cur.execute(sql)


# ============================================================
#  PROVISION tenant — orchestrare, o singură tranzacție
# ============================================================
def cui_valid(cui):
    """True daca CUI-ul are cifra de control corecta (algoritm oficial ANAF, Codul
    fiscal). Pur, testabil. Acceptata forma cu/fara prefix RO si cu spatii - se
    extrag doar cifrele. CUI romanesc: 2-10 cifre (numar identificare 1-9 + control)."""
    c = "".join(ch for ch in str(cui or "") if ch.isdigit())
    if not (2 <= len(c) <= 10):
        return False
    ponderi = [7, 5, 3, 2, 1, 7, 5, 3, 2]
    corp, ctrl = c[:-1].rjust(9, "0"), int(c[-1])
    s = sum(int(corp[i]) * ponderi[i] for i in range(9))
    r = (s * 10) % 11
    if r == 10:
        r = 0
    return r == ctrl


def provision_tenant(conn, nume, cui, accounting_firm_id, user_id, sql_template, tip_firma="srl"):
    # cui_control_v1: cifra de control CUI validata OFFLINE, inainte de orice - ANAF
    # (anaf_api.valideaza_cui) e best-effort in rutele de register (except: pass), deci
    # cand ANAF e jos un CUI malformat ajungea tenant real -> sparge toate declaratiile
    # ulterioare (RegistrationNumber D406/D394 etc. cer CUI valid). Algoritmul e obiectiv
    # (lege), nu depinde de disponibilitatea ANAF.
    if not cui_valid(cui):
        raise ValueError("CUI invalid: cifra de control nu corespunde (%r)" % cui)
    # cui_unic_v1: un CUI o singura data per cabinet
    with conn.cursor() as _c:
        _c.execute("SELECT id FROM public.tenants WHERE cui=%s AND accounting_firm_id=%s",
                   (str(cui), accounting_firm_id))
        if _c.fetchone():
            raise ValueError("Firma cu acest CUI exista deja in portofoliu")
    """
    Creează un tenant complet, totul-sau-nimic:
      1. generează schema_name nou (tenant_NNN)
      2. creează schema + 21 tabele (din template)
      3. INSERT în public.tenants
      4. INSERT în public.user_tenants (leagă userul care creează)
    Întoarce {ok, tenant_id, schema_name} sau ridică excepție (apelantul face rollback).
    """
    import psycopg2.extras as _E
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        # nume scheme existente -> următorul liber
        cur.execute("SELECT schema_name FROM public.tenants")
        existente = [r["schema_name"] for r in cur.fetchall()]
    schema_noua = urmator_schema_name(existente)

    # 2) schema + tabele
    creeaza_schema(conn, schema_noua, sql_template)

    # 3) rândul în public.tenants
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            "INSERT INTO public.tenants (schema_name, nume, cui, accounting_firm_id, activ) "
            "VALUES (%s,%s,%s,%s,true) RETURNING id",
            (schema_noua, nume, cui, accounting_firm_id))
        tenant_id = cur.fetchone()["id"]
        # 4) leagă userul care creează (acces imediat)
        cur.execute(
            "INSERT INTO public.user_tenants (user_id, tenant_id) VALUES (%s,%s) "
            "ON CONFLICT DO NOTHING",
            (user_id, tenant_id))
    # profil_la_provisionare_v1: profil minim (numerotare facturi functionala din prima)
    # [tip_firma_v1] tip_firma (srl/pfa) decide straturii de migrare + cardurile vizibile.
    # CHECK (srl/pfa) pe coloana: normalizam prin primitiva (default srl la lipsa), validam la {srl,pfa}.
    from core.migrare_api import tip_firma_nrm  # default 'srl' -> UNICA primitiva, nu literal inline
    _tip = tip_firma_nrm(tip_firma)
    if _tip not in ("srl", "pfa"):
        _tip = "srl"
    with conn.cursor() as cur:
        cur.execute(
            f"INSERT INTO {schema_noua}.firma_profil (id, nume, cui, serie_factura, urmator_numar_factura, tip_firma) "
            "VALUES (1, %s, %s, '', 1, %s) ON CONFLICT (id) DO NOTHING",
            (nume, str(cui), _tip))
    return {"ok": True, "tenant_id": tenant_id, "schema_name": schema_noua}


# ============================================================
#  CITIRE / EDITARE — DB
# ============================================================
def detalii_tenant(conn, tenant_id):
    """Detaliile unui tenant (sau None). Apelantul verifică deja accesul."""
    import psycopg2.extras as _E
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            "SELECT id, schema_name, nume, cui, accounting_firm_id, activ, "
            "plan_importat_la, balanta_importata_la, salariati_importati_la "
            "FROM public.tenants WHERE id = %s", (tenant_id,))
        r = cur.fetchone()
    return dict(r) if r else None


def actualizeaza_tenant(conn, tenant_id, nume=None, cui=None):
    """Editează nume/cui (NU schema_name — fix). Întoarce {ok}."""
    seturi, valori = [], []
    if nume is not None:
        seturi.append("nume = %s"); valori.append(nume)
    if cui is not None:
        seturi.append("cui = %s"); valori.append(cui)
    if not seturi:
        return {"ok": True, "neschimbat": True}
    valori.append(tenant_id)
    with conn.cursor() as cur:
        cur.execute("UPDATE public.tenants SET %s WHERE id = %%s"
                    % ", ".join(seturi), valori)
    return {"ok": True}
