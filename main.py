# [patch_coada_user_id] rute paseaza int(uid)
"""
main.py — API iConta (reconstruit). Rute SUBȚIRI peste core/ (pur + DB).
Fără logică de business aici: ruta validează intrarea, cheamă modulul, întoarce.

Pornire:  uvicorn main:app
Mediu:    DB_* + JWT_SECRET + BREVO_API_KEY din /home/costin/.iconta/*.env
"""
from __future__ import annotations
import os
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Depends, Header, Body, UploadFile, File, Request
import re as _re_audit
import json as _json_audit
from starlette.concurrency import run_in_threadpool as _run_in_threadpool_audit
import psycopg2.extras as _E_audit
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from core import db, auth_api, declaratii_api, tenant_provisioning, facturi_api, clienti_api, salariati_api, coada_api, portal_api, anaf_api, migrare_api, solduri_api, solduri_parteneri_api, salariati_import_api, asociati_import_api, mijloace_fixe_import_api, istoric_declaratii_import_api, control_fiscal_api, termene_api, capacitate_api, tipare_api, produse_api, vector_fiscal_api, firma_profil_api as _fp, factura_pdf as _pdf, observare as _obs, documente_api

# template SQL pentru schema unui tenant nou (generat din tenant_001)
TENANT_TEMPLATE_PATH = os.environ.get(
    "ICONTA_TENANT_TEMPLATE",
    os.path.join(os.path.dirname(__file__), "tenant_template.sql"))
_TENANT_TEMPLATE = None


# ============================================================
#  LIFECYCLE — pool deschis la pornire, închis la oprire
# ============================================================
@asynccontextmanager
async def lifespan(app):
    global _TENANT_TEMPLATE
    db.init_pool()
    import asyncio as _asyncio_lifespan  # ICRD_LIFESPAN_ALERTE_V1
    _asyncio_lifespan.create_task(_bucla_alerte_sanatate())
    try:
        with db.get_conn() as conn:
            migrare_api.asigura_tabel(conn)
    except Exception:
        pass  # nu blocăm pornirea dacă DB e temporar indisponibil
    try:
        with open(TENANT_TEMPLATE_PATH, encoding="utf-8") as f:
            _TENANT_TEMPLATE = f.read()
    except FileNotFoundError:
        _TENANT_TEMPLATE = None   # creare tenant va da eroare clară până e pus
    yield
    db.inchide_pool()


app = FastAPI(title="iConta API", version="2026.1", lifespan=lifespan)

_APP_PORNIT_LA = __import__("time").time()  # ICRD_SANATATE_SERVER_V1 - uptime proces

# frontend: servit static de pe același origin cu API-ul (fără build step)
_STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(_STATIC_DIR):
    app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")

@app.get("/")
def index():
    cale = os.path.join(_STATIC_DIR, "index.html")
    if os.path.isfile(cale):
        return FileResponse(cale)
    raise HTTPException(404, "frontend neinstalat")


# ============================================================
#  DEPENDENȚE AUTH — Bearer token -> context
# ============================================================
def cere_context(authorization: Optional[str] = Header(None)):
    """Extrage 'Bearer <token>', verifică, întoarce contextul. 401 dacă lipsă/invalid."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "lipsă token (Authorization: Bearer ...)")
    token = authorization[7:]
    ctx = auth_api.context_din_token(token)
    if not ctx["ok"]:
        raise HTTPException(401, ctx.get("mesaj", "token invalid"))
    return ctx


def cere_rol(*roluri):
    """Factory: dependență care cere ca rolul din context să fie printre 'roluri'."""
    def _verifica(ctx=Depends(cere_context)):
        if ctx["rol"] not in roluri and ctx["rol"] != "superadmin":
            raise HTTPException(403, "rol insuficient pentru această acțiune")
        return ctx
    return _verifica


def cere_client(ctx=Depends(cere_context)):
    """Dependență pentru portal: doar rol 'client' (plus superadmin pt debug)."""
    if ctx["rol"] not in ("client", "superadmin"):
        raise HTTPException(403, "doar clienții accesează portalul")
    return ctx


def cere_cabinet(ctx=Depends(cere_context)):
    """Rute de cabinet: orice rol mai puțin 'client' (clienții au portalul)."""
    if ctx["rol"] == "client":
        raise HTTPException(403, "clienții folosesc portalul, nu rutele de cabinet")
    return ctx

# ICRD_AUDIT_LOG_V1 - activitate cabinete (portat din legacy /opt/iconta)
_AUDIT_SKIP_PATHS = ("/static", "/notificari/contor", "/favicon.ico",
                     "/.well-known")

def _inregistreaza_activitate(method, path, status, auth_header):
    if not auth_header or not auth_header.startswith("Bearer "):
        return
    if method == "OPTIONS":
        return
    if any(path.startswith(p) for p in _AUDIT_SKIP_PATHS):
        return
    token = auth_header[7:]
    try:
        ctx = auth_api.context_din_token(token)
    except Exception:
        return
    if not ctx.get("ok"):
        return
    uid = ctx.get("uid")
    if not uid:
        return
    tenant_id = None
    m = _re_audit.match(r"^/tenants/(\d+)", path)
    if m:
        tenant_id = int(m.group(1))
    actiune = f"{method} {path}"
    try:
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO public.audit_log (user_id, tenant_id, actiune, detalii) "
                    "VALUES (%s,%s,%s,%s)",
                    (uid, tenant_id, actiune, _json_audit.dumps({"status": status})))
    except Exception:
        pass

@app.middleware("http")
async def _audit_middleware(request: Request, call_next):
    response = await call_next(request)
    try:
        path = request.url.path
        if not any(path.startswith(p) for p in _AUDIT_SKIP_PATHS):
            auth = request.headers.get("authorization")
            await _run_in_threadpool_audit(
                _inregistreaza_activitate, request.method, path, response.status_code, auth)
    except Exception:
        pass
    return response

# ICRD_CABINETE_CONSOLIDAT_V1
# ICRD_SANATATE_SERVER_V1
# ICRD_ALERTE_SANATATE_V1
_PRAG_RAM_PROCENT = 75
_PRAG_DISC_PROCENT = 75
_PRAG_CONEXIUNI_DB = 20
_ALERTE_COOLDOWN_SEC = 3600
_alerte_ultima_trimitere = {}

def _citeste_metrici_pentru_alerte():
    import os as _os
    import shutil as _shutil
    rezultat = {"ram_procent": None, "disc_procent": None, "load1": None,
                "cpu_count": _os.cpu_count() or 1, "conexiuni_db": None, "erori_noi": 0}
    try:
        info = {}
        with open("/proc/meminfo") as f:
            for linie in f:
                k, v = linie.split(":", 1)
                info[k.strip()] = int(v.strip().split()[0])
        total_kb = info.get("MemTotal", 0)
        disp_kb = info.get("MemAvailable", 0)
        if total_kb:
            rezultat["ram_procent"] = round(100 * (1 - disp_kb / total_kb), 1)
    except Exception:
        pass
    try:
        total, folosit, liber = _shutil.disk_usage("/")
        rezultat["disc_procent"] = round(100 * folosit / total, 1)
    except Exception:
        pass
    try:
        rezultat["load1"] = _os.getloadavg()[0]
    except Exception:
        pass
    try:
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT count(*) FROM pg_stat_activity WHERE datname = current_database()")
                rezultat["conexiuni_db"] = cur.fetchone()[0]
                cur.execute("""
                    SELECT count(*) FROM public.audit_log
                    WHERE created_at > now() - interval '10 minutes'
                      AND (detalii->>'status')::int >= 500
                """)
                rezultat["erori_noi"] = cur.fetchone()[0]
    except Exception:
        pass
    return rezultat

def _email_superadmin():
    try:
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT email FROM public.users WHERE rol='superadmin' AND activ=true ORDER BY id LIMIT 1")
                r = cur.fetchone()
        return r[0] if r else None
    except Exception:
        return None

def _poate_alerta(categorie):
    import time as _time
    ultima = _alerte_ultima_trimitere.get(categorie, 0)
    if _time.time() - ultima < _ALERTE_COOLDOWN_SEC:
        return False
    _alerte_ultima_trimitere[categorie] = _time.time()
    return True

def _verifica_si_alerta():
    m = _citeste_metrici_pentru_alerte()
    probleme = []
    if m["ram_procent"] is not None and m["ram_procent"] >= _PRAG_RAM_PROCENT and _poate_alerta("ram"):
        probleme.append(f"RAM folosita: {m['ram_procent']}% (prag {_PRAG_RAM_PROCENT}%)")
    if m["disc_procent"] is not None and m["disc_procent"] >= _PRAG_DISC_PROCENT and _poate_alerta("disc"):
        probleme.append(f"Disc folosit: {m['disc_procent']}% (prag {_PRAG_DISC_PROCENT}%)")
    if m["load1"] is not None and m["load1"] >= 0.7 * m["cpu_count"] and _poate_alerta("load"):
        probleme.append(f"Load average: {round(m['load1'], 2)} (prag {round(0.7 * m['cpu_count'], 2)})")
    if m["conexiuni_db"] is not None and m["conexiuni_db"] >= _PRAG_CONEXIUNI_DB and _poate_alerta("conexiuni_db"):
        probleme.append(f"Conexiuni DB active: {m['conexiuni_db']} (prag {_PRAG_CONEXIUNI_DB})")
    if m["erori_noi"] and m["erori_noi"] > 0 and _poate_alerta("erori"):
        probleme.append(f"{m['erori_noi']} eroare/erori server (500+) in ultimele 10 minute")
    # ICRD_ISTORIC_SANATATE_V1 - salveaza instantaneu pentru grafice
    try:
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO public.metrici_sanatate "
                    "(ram_procent, disc_procent, load1, conexiuni_db, erori_noi) "
                    "VALUES (%s,%s,%s,%s,%s)",
                    (m["ram_procent"], m["disc_procent"], m["load1"], m["conexiuni_db"], m["erori_noi"]))
    except Exception:
        pass

    if not probleme:
        return
    email = _email_superadmin()
    if not email:
        return
    html = ("<div style='font-family:sans-serif;font-size:15px;color:#111'>"
            "<p>Alerta sanatate server iConta:</p><ul>" +
            "".join("<li>" + p + "</li>" for p in probleme) +
            "</ul><p>Verifica panoul 'Sanatate server' din Admin iConta.</p></div>")
    import core.observare as _obs
    _obs.trimite_email_html(email, "Alerta iConta - sanatate server", html)

async def _bucla_alerte_sanatate():
    import asyncio as _asyncio
    while True:
        try:
            await _run_in_threadpool_audit(_verifica_si_alerta)
        except Exception:
            pass
        await _asyncio.sleep(300)

@app.get("/admin/sanatate/istoric")
def admin_sanatate_istoric(ore: int = 24, ctx=Depends(cere_cabinet)):
    if ctx["rol"] != "superadmin":
        raise HTTPException(403, "Doar Admin iConta.")
    ore = min(max(ore, 1), 168)
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
            cur.execute("""
                SELECT ram_procent, disc_procent, load1, conexiuni_db, erori_noi, creat_la
                FROM public.metrici_sanatate
                WHERE creat_la > now() - (%s || ' hours')::interval
                ORDER BY creat_la ASC
            """, (ore,))
            rows = cur.fetchall()
    return {"istoric": rows}

@app.get("/admin/sanatate")
def admin_sanatate(ctx=Depends(cere_cabinet)):
    if ctx["rol"] != "superadmin":
        raise HTTPException(403, "Doar Admin iConta.")
    import time as _time
    import shutil as _shutil
    import os as _os

    # --- server: load average, RAM, disk ---
    try:
        load1, load5, load15 = _os.getloadavg()
    except Exception:
        load1 = load5 = load15 = None

    ram = {"total_mb": None, "disponibil_mb": None, "folosit_procent": None}
    try:
        info = {}
        with open("/proc/meminfo") as f:
            for linie in f:
                k, v = linie.split(":", 1)
                info[k.strip()] = int(v.strip().split()[0])  # kB
        total_kb = info.get("MemTotal", 0)
        disp_kb = info.get("MemAvailable", 0)
        if total_kb:
            ram = {
                "total_mb": round(total_kb / 1024, 1),
                "disponibil_mb": round(disp_kb / 1024, 1),
                "folosit_procent": round(100 * (1 - disp_kb / total_kb), 1),
            }
    except Exception:
        pass

    disc = {"total_gb": None, "liber_gb": None, "folosit_procent": None}
    try:
        total, folosit, liber = _shutil.disk_usage("/")
        disc = {
            "total_gb": round(total / (1024 ** 3), 1),
            "liber_gb": round(liber / (1024 ** 3), 1),
            "folosit_procent": round(100 * folosit / total, 1),
        }
    except Exception:
        pass

    uptime_sec = round(_time.time() - _APP_PORNIT_LA)

    # --- baza de date ---
    db_info = {"conexiuni": None, "marime": None}
    try:
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT count(*) FROM pg_stat_activity WHERE datname = current_database()")
                db_info["conexiuni"] = cur.fetchone()[0]
                cur.execute("SELECT pg_size_pretty(pg_database_size(current_database()))")
                db_info["marime"] = cur.fetchone()[0]
    except Exception:
        pass

    # --- erori recente (status >= 500 in ultimele 24h) ---
    erori_24h = 0
    lista_erori = []
    try:
        with db.get_conn() as conn:
            with conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, actiune, tenant_id, user_id, created_at, detalii
                    FROM public.audit_log
                    WHERE created_at > now() - interval '24 hours'
                      AND (detalii->>'status')::int >= 500
                    ORDER BY created_at DESC
                """)
                rows = cur.fetchall()
                erori_24h = len(rows)
                lista_erori = rows[:50]
    except Exception:
        pass

    return {
        "server": {"load1": load1, "load5": load5, "load15": load15, "ram": ram, "disc": disc},
        "aplicatie": {"uptime_secunde": uptime_sec},
        "baza_date": db_info,
        "erori_24h": erori_24h,
        "erori_lista": lista_erori,
    }

@app.get("/admin/activitate/cabinete")
def admin_activitate_cabinete(ctx=Depends(cere_cabinet)):
    if ctx["rol"] != "superadmin":
        raise HTTPException(403, "Doar Admin iConta.")
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
            cur.execute("""
                SELECT f.id, f.nume, f.activ,
                       (SELECT COUNT(*) FROM public.tenants t WHERE t.accounting_firm_id = f.id) AS nr_firme,
                       (SELECT COUNT(*) FROM public.users u2 WHERE u2.accounting_firm_id = f.id
                          AND u2.activ = true AND u2.rol IN ('admin_firma','angajat')) AS nr_angajati,
                       (SELECT COUNT(*) FROM public.audit_log a2 JOIN public.users u3 ON u3.id = a2.user_id
                          WHERE u3.accounting_firm_id = f.id AND a2.actiune LIKE 'POST /recomanda%%') AS nr_recomandari,
                       (SELECT COUNT(*) FROM public.audit_log a5 JOIN public.users u6 ON u6.id = a5.user_id
                          WHERE u6.accounting_firm_id = f.id AND a5.actiune LIKE '%%/facturi/emite%%') AS nr_facturi,
                       (SELECT COUNT(*) FROM public.audit_log a6 JOIN public.users u7 ON u7.id = a6.user_id
                          WHERE u7.accounting_firm_id = f.id AND a6.actiune LIKE '%%/depune%%') AS nr_declaratii,  -- ICRD_CABINETE_CATEGORII_V1
                       MAX(a.created_at) AS ultima_activitate,
                       MAX(a.created_at) FILTER (WHERE a.actiune = 'login') AS ultim_login,
                       COUNT(a.id) AS nr_actiuni,
                       COUNT(a.id) FILTER (WHERE a.actiune = 'login') AS nr_logari
                FROM public.accounting_firms f
                LEFT JOIN public.users u ON u.accounting_firm_id = f.id
                LEFT JOIN public.audit_log a ON a.user_id = u.id
                GROUP BY f.id, f.nume, f.activ
                ORDER BY f.nume
            """)
            rows = cur.fetchall()
    return {"cabinete": rows}

@app.post("/admin/cabinete/{firm_id}/suspenda")
def admin_cabinet_suspenda(firm_id: int, ctx=Depends(cere_cabinet)):
    if ctx["rol"] != "superadmin":
        raise HTTPException(403, "Doar Admin iConta.")
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE public.accounting_firms SET activ=false WHERE id=%s", (firm_id,))
    return {"ok": True}

@app.post("/admin/cabinete/{firm_id}/reactiveaza")
def admin_cabinet_reactiveaza(firm_id: int, ctx=Depends(cere_cabinet)):
    if ctx["rol"] != "superadmin":
        raise HTTPException(403, "Doar Admin iConta.")
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE public.accounting_firms SET activ=true WHERE id=%s", (firm_id,))
    return {"ok": True}

@app.get("/admin/activitate/conturi-gratuite")
def admin_conturi_gratuite(ctx=Depends(cere_cabinet)):
    if ctx["rol"] != "superadmin":
        raise HTTPException(403, "Doar Admin iConta.")
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
            cur.execute("""
                SELECT t.id, t.nume, t.cui, t.activ, t.creat_la,
                       (SELECT COUNT(DISTINCT ut.user_id) FROM public.user_tenants ut WHERE ut.tenant_id = t.id) AS nr_useri,
                       (SELECT MAX(a.created_at) FROM public.audit_log a
                          JOIN public.user_tenants ut2 ON ut2.user_id = a.user_id
                          WHERE ut2.tenant_id = t.id) AS ultima_activitate,
                       (SELECT COUNT(*) FROM public.audit_log a2
                          JOIN public.user_tenants ut3 ON ut3.user_id = a2.user_id
                          WHERE ut3.tenant_id = t.id AND a2.actiune LIKE '%%/facturi/emite%%') AS nr_facturi
                FROM public.tenants t
                WHERE t.accounting_firm_id IS NULL
                ORDER BY t.creat_la DESC
            """)
            rows = cur.fetchall()
    return {"conturi": rows}
@app.post("/admin/conturi-gratuite/{tenant_id}/suspenda")
def admin_cont_gratuit_suspenda(tenant_id: int, ctx=Depends(cere_cabinet)):
    if ctx["rol"] != "superadmin":
        raise HTTPException(403, "Doar Admin iConta.")
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE public.tenants SET activ=false WHERE id=%s AND accounting_firm_id IS NULL", (tenant_id,))
    return {"ok": True}
@app.post("/admin/conturi-gratuite/{tenant_id}/reactiveaza")
def admin_cont_gratuit_reactiveaza(tenant_id: int, ctx=Depends(cere_cabinet)):
    if ctx["rol"] != "superadmin":
        raise HTTPException(403, "Doar Admin iConta.")
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE public.tenants SET activ=true WHERE id=%s AND accounting_firm_id IS NULL", (tenant_id,))
    return {"ok": True}
@app.get("/admin/activitate/cabinet/{firm_id}")
def admin_activitate_cabinet(firm_id: int, limita: int = 200, ctx=Depends(cere_cabinet)):
    if ctx["rol"] != "superadmin":
        raise HTTPException(403, "Doar Admin iConta.")
    limita = min(max(limita, 1), 2000)
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
            cur.execute("""
                SELECT a.id, a.actiune, a.tenant_id, a.created_at, u.nume, u.prenume
                FROM public.audit_log a
                JOIN public.users u ON u.id = a.user_id
                WHERE u.accounting_firm_id = %s
                ORDER BY a.created_at DESC
                LIMIT %s
            """, (firm_id, limita))
            rows = cur.fetchall()
    return {"activitate": rows}


@app.get("/capacitate")  # [p70_capacitate] panou capacitate (doar patron)
def capacitate_panou(ctx=Depends(cere_rol("admin_firma"))):
    cab = ctx.get("firm")
    if not cab:
        raise HTTPException(400, "fara cabinet asociat")
    with db.get_conn() as conn:
        return capacitate_api.capacitate(conn, cab)

@app.get("/tipare")  # [p72_tipare] educatie pe tipare (doar patron)
def tipare_panou(ctx=Depends(cere_rol("admin_firma"))):
    cab = ctx.get("firm")
    if not cab:
        raise HTTPException(400, "fara cabinet asociat")
    with db.get_conn() as conn:
        return tipare_api.tipare(conn, cab)


# ============================================================
#  MODELE intrare
# ============================================================
class LoginIn(BaseModel):
    email: str
    parola: str

class RegisterIn(BaseModel):
    email: str
    parola: str
    nume_cabinet: str
    nume: Optional[str] = None
    prenume: Optional[str] = None

class DeclaratieIn(BaseModel):
    tenant_id: int
    an: int
    luna: Optional[int] = None
    trim: Optional[int] = None
    cota: Optional[float] = None
    manual: Optional[dict] = None
    date_extra: Optional[dict] = None
    ca_an_precedent_eur: Optional[float] = None

class TenantNou(BaseModel):
    nume: str
    cui: Optional[str] = None

class TenantEdit(BaseModel):
    nume: Optional[str] = None
    cui: Optional[str] = None

class LinieIn(BaseModel):
    descriere: str
    cantitate: float
    pret_unitar: float
    cota_tva: float = 21
    um: str = "buc"

class FacturaIn(BaseModel):
    numar: str
    data_emitere: str
    directie: str               # "emisa" | "primita"
    linii: list[LinieIn]
    client_id: Optional[int] = None
    tert_nume: Optional[str] = None
    tert_cui: Optional[str] = None
    data_scadenta: Optional[str] = None
    moneda: str = "RON"
    status: str = "emisa"

class ClientIn(BaseModel):
    nume: str
    cui: Optional[str] = None
    adresa: Optional[str] = None
    email: Optional[str] = None
    telefon: Optional[str] = None
    oras: Optional[str] = None
    judet: Optional[str] = None
    cod_postal: Optional[str] = None
    status: str = "activ"

class ClientEdit(BaseModel):
    nume: Optional[str] = None
    cui: Optional[str] = None
    adresa: Optional[str] = None
    email: Optional[str] = None
    telefon: Optional[str] = None
    oras: Optional[str] = None
    judet: Optional[str] = None
    cod_postal: Optional[str] = None
    status: Optional[str] = None

class SalariatIn(BaseModel):
    nume: str
    prenume: Optional[str] = None
    cnp: Optional[str] = None
    data_angajare: Optional[str] = None
    tip_norma: str = "intreaga"
    ore_zi: Optional[float] = None
    salariu_brut: float = 0
    persoane_intretinere: int = 0
    judet_casa: Optional[str] = None
    scutit_contrib_minim: bool = False
    motiv_exceptare: Optional[int] = None
    cor: Optional[str] = None

class SalariatEdit(BaseModel):
    nume: Optional[str] = None
    prenume: Optional[str] = None
    cnp: Optional[str] = None
    data_angajare: Optional[str] = None
    tip_norma: Optional[str] = None
    ore_zi: Optional[float] = None
    salariu_brut: Optional[float] = None
    persoane_intretinere: Optional[int] = None
    judet_casa: Optional[str] = None
    activ: Optional[bool] = None
    scutit_contrib_minim: Optional[bool] = None
    motiv_exceptare: Optional[int] = None
    cor: Optional[str] = None

class MigrareValideazaIn(BaseModel):
    cui_uri: list[str]

class MigrareFirma(BaseModel):
    cui: str
    denumire: str

class MigrareImportaIn(BaseModel):
    firme: list[MigrareFirma]

class MigrareStatusIn(BaseModel):
    strat: str
    stare: str
    nota: str = ""

class VectorIn(BaseModel):  # [p82_vector]
    regim_fiscal: str
    platitor_tva: bool
    tip_decont: Optional[str] = None
    operatiuni_ic: bool = False

class ProdusPotrivesteIn(BaseModel):  # [p97_produse_rute]
    denumire: str
    platitor_tva: bool = True

class ProdusCreeazaIn(BaseModel):
    denumire: str
    um: str = "buc"
    pret_unitar: float = 0
    cota_tva: Optional[float] = None  # daca lipseste -> AI potriveste
    categorie: Optional[str] = None
    confirmat: bool = False

class ProdusUpdateIn(BaseModel):
    denumire: Optional[str] = None
    um: Optional[str] = None
    pret_unitar: Optional[float] = None
    cota_tva: Optional[float] = None
    categorie: Optional[str] = None
    confirmat: Optional[bool] = None

class LinieEmitereIn(BaseModel):  # [p104_emitere_rute]
    descriere: str
    um: str = "buc"
    cantitate: float = 1
    pret_unitar: float = 0
    cota_tva: Optional[float] = None  # None -> potrivire automata (nomenclator/AI)

class EmitereIn(BaseModel):
    linii: List[LinieEmitereIn]
    tert_nume: Optional[str] = None
    tert_cui: Optional[str] = None
    tert_adresa: Optional[str] = None
    client_id: Optional[int] = None
    data_emitere: Optional[str] = None
    data_scadenta: Optional[str] = None
    moneda: str = "RON"
    curs_manual: Optional[float] = None

class NumerotareIn(BaseModel):
    serie: Optional[str] = None
    numar_start: Optional[int] = None

class SoldRand(BaseModel):
    cont: str
    denumire: str = ""
    debit: float = 0
    credit: float = 0

class SolduriIn(BaseModel):
    randuri: list[SoldRand]
    data_referinta: Optional[str] = None
class PartenerRand(BaseModel):
    cont: str
    cui: str = ""
    denumire: str = ""
    debit: float = 0
    credit: float = 0
class ParteneriIn(BaseModel):
    randuri: list[PartenerRand]
    data_referinta: Optional[str] = None
class SalariatRand(BaseModel):
    nume: str = ""
    prenume: str = ""
    cnp: str = ""
    data_angajare: Optional[str] = None
    tip_norma: str = "intreaga"
    ore_zi: float = 8
    salariu_brut: float = 0
    persoane_intretinere: int = 0
    judet_casa: str = ""
    cor: str = ""
    cnp_valid: bool = True
    cnp_motiv: str = "ok"
class SalariatiImportIn(BaseModel):
    randuri: list[SalariatRand]
class AsociatRand(BaseModel):
    nume: str = ""
    cnp: str = ""
    cota: float = 0
    tip: str = "fizica"
    cnp_valid: bool = True
    cnp_motiv: str = "ok"
class AsociatiImportIn(BaseModel):
    randuri: list[AsociatRand]
class MijlocFixRand(BaseModel):
    cod: str = ""
    denumire: str = ""
    valoare: float = 0
    rezidual: float = 0
    amortizat: float = 0
    dnf_luni: int = 0
    data_pif: Optional[str] = None
    metoda: str = "liniara"
    cont_imobilizare: str = "2131"
    cont_amortizare: str = "2813"
    avertismente: list[str] = []
    ok: bool = True
class MijloaceFixeImportIn(BaseModel):
    randuri: list[MijlocFixRand]
class IstoricDeclRand(BaseModel):
    tip: str = ""
    an: int = 0
    luna: int = 0
    data_depunere: Optional[str] = None
    tip_cunoscut: bool = True
    avertisment: list[str] = []
    ok: bool = True
class IstoricDeclImportIn(BaseModel):
    randuri: list[IstoricDeclRand]

class CoadaIn(BaseModel):
    tenant_id: int
    tip: str
    an: int
    luna: Optional[int] = None
    trim: Optional[int] = None
    manual: Optional[dict] = None
    cota: Optional[float] = None
    date_extra: Optional[dict] = None
    ca_an_precedent_eur: Optional[float] = None
    inceput_la: Optional[str] = None  # [p15] ISO, momentul deschiderii formularului

class RespingeIn(BaseModel):
    motiv: str

class DepuneIn(BaseModel):
    spv_index: Optional[str] = None


# ============================================================
#  AUTH
# ============================================================
@app.post("/auth/login")
def login(date: LoginIn):
    with db.get_conn() as conn:
        r = auth_api.login(conn, date.email, date.parola)
    if not r["ok"]:
        raise HTTPException(401, r["mesaj"])
    try:
        with db.get_conn() as conn2:
            with conn2.cursor() as cur:
                cur.execute(
                    "INSERT INTO public.audit_log (user_id, actiune) VALUES (%s,'login')",
                    (r["user"]["id"],))
    except Exception:
        pass
    return {"token": r["token"], "user": r["user"]}


@app.post("/auth/register")
def register(date: RegisterIn):
    with db.get_conn() as conn:
        r = auth_api.inregistreaza_cabinet(
            conn, date.email, date.parola, date.nume_cabinet,
            nume=date.nume, prenume=date.prenume)
    if not r["ok"]:
        raise HTTPException(400, r["mesaj"])
    return {"user_id": r["user_id"], "firm_id": r["firm_id"]}


# ============================================================
#  TENANȚI — firmele la care userul are acces
# ============================================================
@app.get("/tenants")
def tenants(ctx=Depends(cere_cabinet)):
    with db.get_conn() as conn:
        return {"tenants": auth_api.tenantii_userului(conn, ctx["uid"])}


@app.get("/tenants/{tenant_id}")
def tenant_detalii(tenant_id: int, ctx=Depends(cere_cabinet)):
    with db.get_conn() as conn:
        # verific accesul (schema_tenant întoarce None dacă userul n-are acces)
        if not auth_api.schema_tenant(conn, ctx["uid"], tenant_id):
            raise HTTPException(404, "tenant inexistent sau fără acces")
        d = tenant_provisioning.detalii_tenant(conn, tenant_id)
    return d


@app.post("/tenants")
def tenant_creeaza(date: TenantNou, ctx=Depends(cere_rol("admin_firma"))):
    if _TENANT_TEMPLATE is None:
        raise HTTPException(500, "template tenant indisponibil pe server")
    with db.get_conn() as conn:
        r = tenant_provisioning.provision_tenant(
            conn, date.nume, date.cui, ctx["firm"], ctx["uid"], _TENANT_TEMPLATE)
    return r


@app.put("/tenants/{tenant_id}")
def tenant_actualizeaza(tenant_id: int, date: TenantEdit,
                        ctx=Depends(cere_rol("admin_firma"))):
    with db.get_conn() as conn:
        if not auth_api.schema_tenant(conn, ctx["uid"], tenant_id):
            raise HTTPException(404, "tenant inexistent sau fără acces")
        r = tenant_provisioning.actualizeaza_tenant(conn, tenant_id, date.nume, date.cui)
    return r


# ============================================================
#  MIGRARE CABINET — validare CUI la ANAF + import în masă
# ============================================================
@app.post("/migrare/valideaza")
def migrare_valideaza(date: MigrareValideazaIn, ctx=Depends(cere_cabinet)):
    """Verifică o listă de CUI-uri la ANAF; întoarce denumirea + status."""
    if not date.cui_uri:
        return {"rezultate": []}
    try:
        rez = anaf_api.valideaza_cui(date.cui_uri)
    except Exception as e:
        raise HTTPException(502, f"ANAF indisponibil sau a refuzat cererea: {e}")
    return {"rezultate": rez}


@app.post("/migrare/fisier")
async def migrare_fisier(fisier: UploadFile = File(...), ctx=Depends(cere_cabinet)):
    """Primește un CSV/XLSX, extrage CUI-urile și le validează la ANAF."""
    continut = await fisier.read()
    try:
        cui_uri = anaf_api.extrage_cui_din_fisier(continut, fisier.filename or "")
    except Exception as e:
        raise HTTPException(400, f"fișier ilizibil: {e}")
    if not cui_uri:
        return {"rezultate": []}
    try:
        rez = anaf_api.valideaza_cui(cui_uri)
    except Exception as e:
        raise HTTPException(502, f"ANAF indisponibil sau a refuzat cererea: {e}")
    return {"rezultate": rez}


@app.post("/migrare/incarca")
async def migrare_incarca(fisier: UploadFile = File(...), ctx=Depends(cere_cabinet)):
    """Primește un fișier (.csv/.xlsx), extrage CUI-urile și le validează la ANAF."""
    continut = await fisier.read()
    try:
        cui_uri = anaf_api.extrage_cui_din_fisier(continut, fisier.filename or "")
    except ValueError as e:
        raise HTTPException(400, str(e))
    if not cui_uri:
        return {"rezultate": [], "extrase": 0}
    try:
        rez = anaf_api.valideaza_cui(cui_uri)
    except Exception as e:
        raise HTTPException(502, f"ANAF indisponibil sau a refuzat cererea: {e}")
    return {"rezultate": rez, "extrase": len(cui_uri)}


@app.post("/migrare/importa")
def migrare_importa(date: MigrareImportaIn, ctx=Depends(cere_rol("admin_firma"))):
    """Creează câte un tenant pentru fiecare firmă selectată. Sare peste CUI-uri deja în portofoliu."""
    if _TENANT_TEMPLATE is None:
        raise HTTPException(500, "template tenant indisponibil pe server")
    creat, erori = [], []
    with db.get_conn() as conn:
        # CUI-urile deja existente în portofoliul cabinetului (normalizate la cifre)
        with conn.cursor() as cur:
            cur.execute("SELECT cui FROM public.tenants WHERE accounting_firm_id = %s", (ctx["firm"],))
            existente = set()
            for (c,) in cur.fetchall():
                cc = anaf_api._curata(c)
                if cc:
                    existente.add(cc)
        for f in date.firme:
            nume = (f.denumire or "").strip() or f"Firmă {f.cui}"
            cuic = anaf_api._curata(f.cui)
            if cuic and cuic in existente:
                erori.append({"cui": str(f.cui), "nume": nume, "mesaj": "există deja în portofoliu"})
                continue
            try:
                r = tenant_provisioning.provision_tenant(
                    conn, nume, str(f.cui), ctx["firm"], ctx["uid"], _TENANT_TEMPLATE)
                creat.append({"cui": str(f.cui), "nume": nume, "tenant_id": r.get("tenant_id")})
                if cuic:
                    existente.add(cuic)   # prinde și duplicate în același lot
            except Exception as e:
                erori.append({"cui": str(f.cui), "nume": nume, "mesaj": str(e)})
    return {"creat": creat, "erori": erori, "total": len(creat)}


@app.get("/migrare/status")
def migrare_status_citeste(ctx=Depends(cere_cabinet)):
    """Starea fiecărui strat de migrare + reminderul (straturi în lucru)."""
    with db.get_conn() as conn:
        status = migrare_api.citeste_status(conn, ctx["firm"])
        rem = migrare_api.reminder(conn, ctx["firm"])
    return {"straturi": migrare_api.STRATURI, "status": status, "reminder": rem}


@app.post("/migrare/status")
def migrare_status_seteaza(date: MigrareStatusIn, ctx=Depends(cere_rol("admin_firma"))):
    """Marchează un strat 'gata' sau 'in_lucru' (cu notă obligatorie la in_lucru)."""
    try:
        with db.get_conn() as conn:
            r = migrare_api.seteaza_status(conn, ctx["firm"], date.strat, date.stare, date.nota)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return r


# ============================================================
#  MIGRARE STRAT 2 — SOLDURI INIȚIALE (per firmă)
# ============================================================
@app.get("/migrare/solduri")
def migrare_solduri_status(ctx=Depends(cere_cabinet)):
    """Lista firmelor cabinetului cu status solduri (are/n-are, câte conturi)."""
    out = []
    with db.get_conn() as conn:
        firme = auth_api.tenantii_userului(conn, ctx["uid"])
    for f in firme:
        tid = f.get("id")
        try:
            with db.get_conn() as c:
                schema = auth_api.schema_tenant(c, ctx["uid"], tid)
            if not schema:
                continue
            with db.get_conn(schema) as c:
                rez = solduri_api.rezumat(c)
        except Exception:
            rez = {"are_solduri": False, "randuri": 0, "total_debit": 0, "total_credit": 0}
        out.append({"tenant_id": tid, "nume": f.get("nume"), "cui": f.get("cui"),
                    "are_solduri": rez["are_solduri"], "randuri": rez["randuri"]})
    return {"firme": out}

@app.get("/migrare/vector")  # [p84_vector_front] lista firmelor cu status vector fiscal
def migrare_vector_status(ctx=Depends(cere_cabinet)):
    """Lista firmelor cabinetului cu status vector (completat sau nu)."""
    out = []
    with db.get_conn() as conn:
        firme = auth_api.tenantii_userului(conn, ctx["uid"])
    for f in firme:
        tid = f.get("id")
        try:
            with db.get_conn() as c:
                schema = auth_api.schema_tenant(c, ctx["uid"], tid)
            if not schema:
                continue
            with db.get_conn(schema) as c:
                v = vector_fiscal_api.citeste(c)
        except Exception:
            v = {"ok": False}
        out.append({"tenant_id": tid, "nume": f.get("nume"), "cui": f.get("cui"),
                    "are_vector": bool(v.get("completat")),
                    "regim_fiscal": v.get("regim_fiscal"),
                    "platitor_tva": v.get("platitor_tva"),
                    "tip_decont": v.get("tip_decont"),
                    "operatiuni_ic": v.get("operatiuni_ic")})
    return {"firme": out}


@app.post("/tenants/{tenant_id}/solduri/incarca")
async def solduri_incarca(tenant_id: int, fisier: UploadFile = File(...), ctx=Depends(cere_cabinet)):
    """Parsează o balanță și întoarce preview (nu salvează)."""
    _schema_sau_404(ctx, tenant_id)
    continut = await fisier.read()
    try:
        randuri = solduri_api.extrage_balanta(continut, fisier.filename or "")
    except ValueError as e:
        raise HTTPException(400, str(e))
    td = round(sum(r["debit"] for r in randuri), 2)
    tc = round(sum(r["credit"] for r in randuri), 2)
    return {"randuri": randuri, "total_debit": td, "total_credit": tc}


@app.get("/tenants/{tenant_id}/solduri")
def solduri_rezumat(tenant_id: int, ctx=Depends(cere_cabinet)):
    """Rezumatul soldurilor salvate pentru o firmă."""
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        return solduri_api.rezumat(conn)


@app.post("/tenants/{tenant_id}/solduri")
def solduri_salveaza(tenant_id: int, date: SolduriIn, ctx=Depends(cere_rol("admin_firma"))):
    """Salvează soldurile inițiale ale unei firme (înlocuiește ce era)."""
    schema = _schema_sau_404(ctx, tenant_id)
    randuri = [{"cont": r.cont, "denumire": r.denumire, "debit": r.debit, "credit": r.credit}
               for r in date.randuri]
    with db.get_conn(schema) as conn:
        return solduri_api.importa(conn, randuri, date.data_referinta)


# ============================================================
#  MIGRARE STRAT 3 — SOLDURI PARTENERI (4111/401 per partener)
# ============================================================
@app.get("/migrare/parteneri")
def migrare_parteneri_status(ctx=Depends(cere_cabinet)):
    """Lista firmelor cabinetului cu status parteneri (are/n-are, cati parteneri)."""
    out = []
    with db.get_conn() as conn:
        firme = auth_api.tenantii_userului(conn, ctx["uid"])
    for f in firme:
        tid = f.get("id")
        try:
            with db.get_conn() as c:
                schema = auth_api.schema_tenant(c, ctx["uid"], tid)
            if not schema:
                continue
            with db.get_conn(schema) as c:
                rez = solduri_parteneri_api.rezumat(c)
        except Exception:
            rez = {"are_parteneri": False, "randuri": 0, "total_debit": 0, "total_credit": 0}
        out.append({"tenant_id": tid, "nume": f.get("nume"), "cui": f.get("cui"),
                    "are_parteneri": rez["are_parteneri"], "randuri": rez["randuri"]})
    return {"firme": out}


@app.post("/tenants/{tenant_id}/parteneri/incarca")
async def parteneri_incarca(tenant_id: int, fisier: UploadFile = File(...), ctx=Depends(cere_cabinet)):
    """Parseaza fisierul de parteneri si intoarce preview + verificare coerenta vs balanta."""
    schema = _schema_sau_404(ctx, tenant_id)
    continut = await fisier.read()
    try:
        randuri = solduri_parteneri_api.extrage(continut, fisier.filename or "")
    except ValueError as e:
        raise HTTPException(400, str(e))
    td = round(sum(r["debit"] for r in randuri), 2)
    tc = round(sum(r["credit"] for r in randuri), 2)
    with db.get_conn(schema) as conn:
        coer = solduri_parteneri_api.coerenta(conn, randuri)
    return {"randuri": randuri, "total_debit": td, "total_credit": tc, "coerenta": coer}


@app.get("/tenants/{tenant_id}/parteneri")
def parteneri_rezumat(tenant_id: int, ctx=Depends(cere_cabinet)):
    """Rezumatul partenerilor salvati pentru o firma."""
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        return solduri_parteneri_api.rezumat(conn)


@app.post("/tenants/{tenant_id}/parteneri")
def parteneri_salveaza(tenant_id: int, date: ParteneriIn, ctx=Depends(cere_rol("admin_firma"))):
    """Salveaza soldurile partenerilor unei firme (inlocuieste ce era)."""
    schema = _schema_sau_404(ctx, tenant_id)
    randuri = [{"cont": r.cont, "cui": r.cui, "denumire": r.denumire, "debit": r.debit, "credit": r.credit}
               for r in date.randuri]
    with db.get_conn(schema) as conn:
        return solduri_parteneri_api.importa(conn, randuri, date.data_referinta)



# ============================================================
#  MIGRARE STRAT 4 — SALARIATI (import din vechea aplicatie)
# ============================================================
@app.get("/migrare/salariati")
def migrare_salariati_status(ctx=Depends(cere_cabinet)):
    """Lista firmelor cabinetului cu status salariati (are/n-are, cati)."""
    out = []
    with db.get_conn() as conn:
        firme = auth_api.tenantii_userului(conn, ctx["uid"])
    for f in firme:
        tid = f.get("id")
        try:
            with db.get_conn() as c:
                schema = auth_api.schema_tenant(c, ctx["uid"], tid)
            if not schema:
                continue
            with db.get_conn(schema) as c:
                rez = salariati_import_api.rezumat(c)
        except Exception:
            rez = {"are_salariati": False, "randuri": 0}
        out.append({"tenant_id": tid, "nume": f.get("nume"), "cui": f.get("cui"),
                    "are_salariati": rez["are_salariati"], "randuri": rez["randuri"]})
    return {"firme": out}


@app.post("/tenants/{tenant_id}/salariati-import/incarca")
async def salariati_import_incarca(tenant_id: int, fisier: UploadFile = File(...), ctx=Depends(cere_cabinet)):
    """Parseaza exportul de salariati si intoarce preview cu validare CNP (nu salveaza)."""
    _schema_sau_404(ctx, tenant_id)
    continut = await fisier.read()
    try:
        randuri = salariati_import_api.extrage(continut, fisier.filename or "")
    except ValueError as e:
        raise HTTPException(400, str(e))
    valizi = sum(1 for r in randuri if r["cnp_valid"])
    return {"randuri": randuri, "total": len(randuri), "valizi": valizi,
            "invalizi": len(randuri) - valizi}


@app.post("/tenants/{tenant_id}/salariati-import")
def salariati_import_salveaza(tenant_id: int, date: SalariatiImportIn, ctx=Depends(cere_rol("admin_firma"))):
    """Importa salariatii cu CNP valid (upsert pe CNP). Sare peste cei invalizi."""
    schema = _schema_sau_404(ctx, tenant_id)
    randuri = [r.model_dump() for r in date.randuri]
    with db.get_conn(schema) as conn:
        return salariati_import_api.importa(conn, randuri)



# ============================================================
#  MIGRARE STRAT 5 — ASOCIATI (pentru D205 / dividende)
# ============================================================
@app.get("/migrare/asociati")
def migrare_asociati_status(ctx=Depends(cere_cabinet)):
    out = []
    with db.get_conn() as conn:
        firme = auth_api.tenantii_userului(conn, ctx["uid"])
    for f in firme:
        tid = f.get("id")
        try:
            with db.get_conn() as c:
                schema = auth_api.schema_tenant(c, ctx["uid"], tid)
            if not schema:
                continue
            with db.get_conn(schema) as c:
                rez = asociati_import_api.rezumat(c)
        except Exception:
            rez = {"are_asociati": False, "randuri": 0, "total_cota": 0}
        out.append({"tenant_id": tid, "nume": f.get("nume"), "cui": f.get("cui"),
                    "are_asociati": rez["are_asociati"], "randuri": rez["randuri"]})
    return {"firme": out}


@app.post("/tenants/{tenant_id}/asociati-import/incarca")
async def asociati_import_incarca(tenant_id: int, fisier: UploadFile = File(...), ctx=Depends(cere_cabinet)):
    _schema_sau_404(ctx, tenant_id)
    continut = await fisier.read()
    try:
        randuri = asociati_import_api.extrage(continut, fisier.filename or "")
    except ValueError as e:
        raise HTTPException(400, str(e))
    coer = asociati_import_api.coerenta_cote(randuri)
    return {"randuri": randuri, "total": len(randuri), "coerenta": coer}


@app.post("/tenants/{tenant_id}/asociati-import")
def asociati_import_salveaza(tenant_id: int, date: AsociatiImportIn, ctx=Depends(cere_rol("admin_firma"))):
    schema = _schema_sau_404(ctx, tenant_id)
    randuri = [r.model_dump() for r in date.randuri]
    with db.get_conn(schema) as conn:
        return asociati_import_api.importa(conn, randuri)



# ============================================================
#  MIGRARE STRAT 6 — MIJLOACE FIXE (registru amortizare)
# ============================================================
@app.get("/migrare/mijloace-fixe")
def migrare_mijloace_status(ctx=Depends(cere_cabinet)):
    out = []
    with db.get_conn() as conn:
        firme = auth_api.tenantii_userului(conn, ctx["uid"])
    for f in firme:
        tid = f.get("id")
        try:
            with db.get_conn() as c:
                schema = auth_api.schema_tenant(c, ctx["uid"], tid)
            if not schema:
                continue
            with db.get_conn(schema) as c:
                rez = mijloace_fixe_import_api.rezumat(c)
        except Exception:
            rez = {"are_mijloace": False, "randuri": 0}
        out.append({"tenant_id": tid, "nume": f.get("nume"), "cui": f.get("cui"),
                    "are_mijloace": rez["are_mijloace"], "randuri": rez["randuri"]})
    return {"firme": out}


@app.post("/tenants/{tenant_id}/mijloace-fixe-import/incarca")
async def mijloace_import_incarca(tenant_id: int, fisier: UploadFile = File(...), ctx=Depends(cere_cabinet)):
    _schema_sau_404(ctx, tenant_id)
    continut = await fisier.read()
    try:
        randuri = mijloace_fixe_import_api.extrage(continut, fisier.filename or "")
    except ValueError as e:
        raise HTTPException(400, str(e))
    tv = round(sum(r["valoare"] for r in randuri), 2)
    tr = round(sum(r["rezidual"] for r in randuri), 2)
    cu_avert = sum(1 for r in randuri if not r["ok"])
    return {"randuri": randuri, "total": len(randuri), "total_valoare": tv,
            "total_rezidual": tr, "cu_avertismente": cu_avert}


@app.post("/tenants/{tenant_id}/mijloace-fixe-import")
def mijloace_import_salveaza(tenant_id: int, date: MijloaceFixeImportIn, ctx=Depends(cere_rol("admin_firma"))):
    schema = _schema_sau_404(ctx, tenant_id)
    randuri = [r.model_dump() for r in date.randuri]
    with db.get_conn(schema) as conn:
        return mijloace_fixe_import_api.importa(conn, randuri)



# ============================================================
#  MIGRARE STRAT 7 — ISTORIC DECLARATII (ce s-a depus deja)
# ============================================================
@app.get("/migrare/istoric-declaratii")
def migrare_istoric_status(ctx=Depends(cere_cabinet)):
    out = []
    with db.get_conn() as conn:
        firme = auth_api.tenantii_userului(conn, ctx["uid"])
    for f in firme:
        tid = f.get("id")
        try:
            with db.get_conn() as c:
                rez = istoric_declaratii_import_api.rezumat(c, tid)
        except Exception:
            rez = {"are_istoric": False, "randuri": 0}
        out.append({"tenant_id": tid, "nume": f.get("nume"), "cui": f.get("cui"),
                    "are_istoric": rez["are_istoric"], "randuri": rez["randuri"]})
    return {"firme": out}


@app.post("/tenants/{tenant_id}/istoric-declaratii-import/incarca")
async def istoric_import_incarca(tenant_id: int, fisier: UploadFile = File(...), ctx=Depends(cere_cabinet)):
    _schema_sau_404(ctx, tenant_id)
    continut = await fisier.read()
    try:
        randuri = istoric_declaratii_import_api.extrage(continut, fisier.filename or "")
    except ValueError as e:
        raise HTTPException(400, str(e))
    cu_avert = sum(1 for r in randuri if not r["ok"])
    return {"randuri": randuri, "total": len(randuri), "cu_avertismente": cu_avert}


@app.post("/tenants/{tenant_id}/istoric-declaratii-import")
def istoric_import_salveaza(tenant_id: int, date: IstoricDeclImportIn, ctx=Depends(cere_rol("admin_firma"))):
    _schema_sau_404(ctx, tenant_id)
    randuri = [r.model_dump() for r in date.randuri]
    with db.get_conn() as conn:
        return istoric_declaratii_import_api.importa(conn, tenant_id, randuri)



# ============================================================
#  CONTROL FISCAL — semafor conformare per portofoliu
# ============================================================
@app.get("/control-fiscal")
def control_fiscal_portofoliu(ctx=Depends(cere_cabinet)):
    """Semafor pentru toate firmele cabinetului + sumar (verde/galben/rosu)."""
    import datetime
    azi = datetime.date.today()
    out = []
    sumar = {"verde": 0, "galben": 0, "rosu": 0, "gri": 0}
    with db.get_conn() as conn:
        firme = auth_api.tenantii_userului(conn, ctx["uid"])
    for f in firme:
        tid = f.get("id")
        try:
            with db.get_conn() as c:
                schema = auth_api.schema_tenant(c, ctx["uid"], tid)
            if not schema:
                continue
            with db.get_conn(schema) as cs, db.get_conn() as cp:
                r = control_fiscal_api.evalueaza_firma(cs, cp, tid, schema, azi)
        except Exception:
            r = {"stare": "gri", "datorate": 0, "depuse": 0, "lipsa": [], "urmarit": []}
        sumar[r["stare"]] = sumar.get(r["stare"], 0) + 1
        out.append({"tenant_id": tid, "nume": f.get("nume"), "cui": f.get("cui"),
                    "stare": r["stare"], "lipsa": len(r["lipsa"]), "urmarit": len(r["urmarit"])})
    return {"firme": out, "sumar": sumar}


@app.get("/control-fiscal/{tenant_id}")
def control_fiscal_detaliu(tenant_id: int, ctx=Depends(cere_cabinet)):
    """Detaliu conformare pentru o firma: lista lipsa + de urmarit."""
    import datetime
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as cs, db.get_conn() as cp:
        r = control_fiscal_api.evalueaza_firma(cs, cp, tenant_id, schema, datetime.date.today())
    return r



# ============================================================
#  TERMENE — scadente viitoare pe portofoliu (orizont 60 zile)
# ============================================================
@app.get("/termene")
def termene_portofoliu(ctx=Depends(cere_cabinet)):
    """Scadente viitoare grupate pe data + tip, cu numarul de firme."""
    import datetime
    azi = datetime.date.today()
    with db.get_conn() as conn:
        firme = auth_api.tenantii_userului(conn, ctx["uid"])
    firme_eval = []
    for f in firme:
        tid = f.get("id")
        try:
            with db.get_conn() as c:
                schema = auth_api.schema_tenant(c, ctx["uid"], tid)
            if not schema:
                continue
            with db.get_conn(schema) as cs:
                with cs.cursor() as cur:
                    cur.execute("SELECT regim_fiscal, platitor_tva, tip_decont, operatiuni_ic FROM firma_profil LIMIT 1")
                    row = cur.fetchone()
                    vector = {"regim_fiscal": row[0], "platitor_tva": row[1],
                              "tip_decont": row[2], "operatiuni_ic": row[3]} if row else {}
                    cur.execute("SELECT to_regclass('salariati')")
                    are_sal = False
                    if cur.fetchone()[0]:
                        cur.execute("SELECT count(*) FROM salariati WHERE activ=true")
                        are_sal = cur.fetchone()[0] > 0
            if not vector:
                continue
            with db.get_conn() as cp:
                with cp.cursor() as cur:
                    cur.execute("SELECT tip, an, luna FROM public.declaratii_depuse WHERE tenant_id=%s", (tid,))
                    depuse = {(t, a, l) for (t, a, l) in cur.fetchall()}
            term = termene_api.termene_firma(vector, are_sal, depuse, azi)
            firme_eval.append({"tenant_id": tid, "nume": f.get("nume"), "termene": term})
        except Exception:
            continue
    return termene_api.portofoliu(firme_eval, azi)



# ============================================================
#  FACTURI (în schema tenantului)
# ============================================================
def _schema_sau_404(ctx, tenant_id):
    """Verifică accesul userului la tenant; întoarce schema sau ridică 404."""
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
    if not schema:
        raise HTTPException(404, "tenant inexistent sau fără acces")
    return schema

# [p97_produse_rute] NOMENCLATOR PRODUSE — rute generice pe tenant (cabinet + client + gratuit)
# guard unificat: _schema_sau_404 accepta orice user cu acces la tenant (schema_tenant)
@app.get("/tenants/{tenant_id}/produse")
def produse_lista(tenant_id: int, ctx=Depends(cere_context)):
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        return {"produse": produse_api.lista(conn)}

@app.post("/tenants/{tenant_id}/produse/potriveste")
def produse_potriveste(tenant_id: int, date: ProdusPotrivesteIn, ctx=Depends(cere_context)):
    # preview cota (AI), fara salvare - pentru UI la scrierea denumirii
    _schema_sau_404(ctx, tenant_id)  # doar verific accesul
    return produse_api.potriveste(date.denumire, platitor_tva=date.platitor_tva)

@app.post("/tenants/{tenant_id}/produse")
def produse_creeaza(tenant_id: int, date: ProdusCreeazaIn, ctx=Depends(cere_context)):
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        r = produse_api.creeaza(conn, date.denumire, um=date.um,
                                pret_unitar=date.pret_unitar, cota_tva=date.cota_tva,
                                categorie=date.categorie, confirmat=date.confirmat)
    if not r.get("ok"):
        raise HTTPException(400, r.get("mesaj", "produs invalid"))
    return r

@app.put("/tenants/{tenant_id}/produse/{produs_id}")
def produse_actualizeaza(tenant_id: int, produs_id: int, date: ProdusUpdateIn,
                         ctx=Depends(cere_context)):
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        r = produse_api.actualizeaza(conn, produs_id, denumire=date.denumire,
                                     um=date.um, pret_unitar=date.pret_unitar,
                                     cota_tva=date.cota_tva, categorie=date.categorie,
                                     confirmat=date.confirmat)
    if not r.get("ok"):
        raise HTTPException(404, "produs inexistent")
    return r

@app.delete("/tenants/{tenant_id}/produse/{produs_id}")
def produse_sterge(tenant_id: int, produs_id: int, ctx=Depends(cere_context)):
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        r = produse_api.sterge(conn, produs_id)
    if not r.get("ok"):
        raise HTTPException(404, "produs inexistent")
    return r

# [p104_emitere_rute] EMITERE FACTURI — rute generice pe tenant (client + gratuit + cabinet)
def _platitor_tva_firma(conn):
    """Citeste daca firma emitenta e platitoare TVA (din firma_profil)."""
    with conn.cursor() as cur:
        cur.execute("SELECT platitor_tva FROM firma_profil LIMIT 1")
        row = cur.fetchone()
    return bool(row[0]) if row and row[0] is not None else True

@app.get("/tenants/{tenant_id}/facturi/numerotare")
def facturi_numerotare_get(tenant_id: int, ctx=Depends(cere_context)):
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        return facturi_api.numerotare(conn)

@app.put("/tenants/{tenant_id}/facturi/numerotare")
def facturi_numerotare_set(tenant_id: int, date: NumerotareIn, ctx=Depends(cere_context)):
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        r = facturi_api.seteaza_numerotare(conn, serie=date.serie, numar_start=date.numar_start)
    if not r.get("ok"):
        raise HTTPException(400, r.get("mesaj", "eroare"))
    return r

class ModelFacturaIn(BaseModel):
    font: Optional[str] = None
    culoare: Optional[str] = None
    logo: Optional[str] = None      # data URI base64; "" sterge; None = nu schimba

@app.get("/tenants/{tenant_id}/firma-profil")
def firma_profil_get(tenant_id: int, ctx=Depends(cere_context)):
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        return _fp.citeste_profil(conn)

@app.post("/tenants/{tenant_id}/firma-profil/model")
def firma_profil_model(tenant_id: int, date: ModelFacturaIn, ctx=Depends(cere_context)):
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        return _fp.salveaza_model(conn, font=date.font, culoare=date.culoare, logo=date.logo)

@app.get("/tenants/{tenant_id}/facturi/{factura_id}/pdf")
def factura_pdf_ruta(tenant_id: int, factura_id: int, ctx=Depends(cere_context)):
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        f = facturi_api.detalii_factura(conn, factura_id)
        if not f:
            raise HTTPException(404, "factură inexistentă")
        profil = _fp.citeste_profil(conn)
    pdf = _pdf.genereaza_pdf(profil, f)
    nume = "factura_" + str(f.get("numar") or factura_id).replace("/", "-") + ".pdf"
    return Response(content=pdf, media_type="application/pdf",
                    headers={"Content-Disposition": f'inline; filename="{nume}"'})

class EmailFacturaIn(BaseModel):
    email: str
    mesaj: Optional[str] = None

@app.post("/tenants/{tenant_id}/facturi/{factura_id}/email")
def factura_email(tenant_id: int, factura_id: int, date: EmailFacturaIn, ctx=Depends(cere_context)):
    schema = _schema_sau_404(ctx, tenant_id)
    email = (date.email or "").strip()
    if "@" not in email or "." not in email:
        raise HTTPException(422, "adresă de email invalidă")
    with db.get_conn(schema) as conn:
        f = facturi_api.detalii_factura(conn, factura_id)
        if not f:
            raise HTTPException(404, "factură inexistentă")
        profil = _fp.citeste_profil(conn)
    import base64 as _b64
    pdf = _pdf.genereaza_pdf(profil, f)
    nume_pdf = "factura_" + str(f.get("numar") or factura_id).replace("/", "-") + ".pdf"
    b64 = _b64.b64encode(pdf).decode()
    numar = f.get("numar") or ""
    firma = profil.get("nume") or ""
    subiect = "Factura %s%s" % (numar, (" - " + firma if firma else ""))
    corp_mesaj = date.mesaj or ("Bună ziua,<br><br>Atașat găsiți factura %s.<br><br>O zi bună!" % numar)
    html = "<div style='font-family:Arial,sans-serif;font-size:14px;color:#222'>%s</div>" % corp_mesaj
    ok = _obs.trimite_email_html(email, subiect, html,
                                 attachments=[{"content": b64, "name": nume_pdf}])
    if not ok:
        raise HTTPException(502, "trimiterea email a eșuat")
    return {"ok": True, "email": email}

@app.post("/tenants/{tenant_id}/facturi/emite")
def facturi_emite(tenant_id: int, date: EmitereIn, ctx=Depends(cere_context)):
    schema = _schema_sau_404(ctx, tenant_id)
    linii = [l.model_dump() for l in date.linii]
    with db.get_conn(schema) as conn:
        platitor = _platitor_tva_firma(conn)
        try:
            r = facturi_api.emite_factura(
                conn, linii, client_id=date.client_id, tert_nume=date.tert_nume,
                tert_cui=date.tert_cui, tert_adresa=date.tert_adresa, data_emitere=date.data_emitere,
                data_scadenta=date.data_scadenta, moneda=date.moneda,
                platitor_tva=platitor, curs_manual=date.curs_manual)
        except ValueError as e:
            raise HTTPException(422, str(e))
    # curs BNR indisponibil -> 409 cu detaliile pt frontend (Reincearca / Manual)
    if isinstance(r, dict) and r.get("ok") is False and r.get("cod") == "CURS_INDISPONIBIL":
        raise HTTPException(409, detail=r)
    return r

@app.post("/tenants/{tenant_id}/facturi/{factura_id}/storno")
def facturi_storno(tenant_id: int, factura_id: int, ctx=Depends(cere_context)):
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        try:
            r = facturi_api.storneaza(conn, factura_id)
        except ValueError as e:
            raise HTTPException(422, str(e))
    return r

# ICRD_PUBLIC_VERIFICA_CUI_V1
@app.get("/public/verifica-cui/{cui}")
def public_verifica_cui(cui: str):
    try:
        rez = anaf_api.valideaza_cui([cui])
    except Exception as e:
        raise HTTPException(502, "ANAF indisponibil: %s" % e)
    if not rez:
        return {"gasit": False}
    return rez[0]

@app.get("/tenants/{tenant_id}/verifica-cui/{cui}")
def verifica_cui(tenant_id: int, cui: str, ctx=Depends(cere_context)):
    _schema_sau_404(ctx, tenant_id)  # doar verific accesul
    try:
        rez = anaf_api.valideaza_cui([cui])
    except Exception as e:
        raise HTTPException(502, "ANAF indisponibil: %s" % e)
    if not rez:
        return {"gasit": False}
    return rez[0]

@app.get("/tenants/{tenant_id}/vector")  # [p82_vector] citeste vectorul fiscal
def vector_citeste(tenant_id: int, ctx=Depends(cere_cabinet)):
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        return vector_fiscal_api.citeste(conn)

@app.post("/tenants/{tenant_id}/vector")  # [p82_vector] scrie vectorul (doar admin_firma)
def vector_salveaza(tenant_id: int, date: VectorIn, ctx=Depends(cere_rol("admin_firma"))):
    schema = _schema_sau_404(ctx, tenant_id)
    # nume+cui din public.tenants (pt cazul cand firma_profil e gol si trebuie creat)  # [p83_upsert]
    with db.get_conn() as cpub:
        with cpub.cursor() as cur:
            cur.execute("SELECT nume, cui FROM public.tenants WHERE id = %s", (tenant_id,))
            row = cur.fetchone()
    t_nume = row[0] if row else None
    t_cui = row[1] if row else None
    with db.get_conn(schema) as conn:
        rez = vector_fiscal_api.salveaza(conn, date.regim_fiscal, date.platitor_tva,
                                         date.tip_decont, date.operatiuni_ic,
                                         nume=t_nume, cui=t_cui)
    if not rez.get("ok"):
        raise HTTPException(400, rez.get("mesaj", "vector invalid"))
    # marcheaza stratul de migrare ca gata
    try:
        with db.get_conn() as c:
            migrare_api.seteaza_status(c, ctx["firm"], "vector_fiscal", "gata", "")
    except Exception:
        pass
    return rez


@app.get("/tenants/{tenant_id}/facturi")  # [p117_facturi_lista_acces] acces client+gratuit+cabinet
def facturi_lista(tenant_id: int, an: Optional[int] = None,
                  luna: Optional[int] = None, directie: Optional[str] = None,
                  ctx=Depends(cere_context)):
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        return {"facturi": facturi_api.lista_facturi(conn, an, luna, directie)}


@app.post("/tenants/{tenant_id}/facturi")
def factura_creeaza(tenant_id: int, date: FacturaIn,
                    ctx=Depends(cere_rol("admin_firma", "angajat"))):
    schema = _schema_sau_404(ctx, tenant_id)
    linii = [l.model_dump() for l in date.linii]
    try:
        with db.get_conn(schema) as conn:
            r = facturi_api.creeaza_factura(
                conn, date.numar, date.data_emitere, date.directie, linii,
                client_id=date.client_id, tert_nume=date.tert_nume,
                tert_cui=date.tert_cui, data_scadenta=date.data_scadenta,
                moneda=date.moneda, status=date.status)
    except ValueError as e:
        raise HTTPException(422, str(e))
    return r


@app.get("/tenants/{tenant_id}/facturi/{factura_id}")  # [p115_detalii_acces] acces client+gratuit+cabinet
def factura_detalii(tenant_id: int, factura_id: int, ctx=Depends(cere_context)):
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        f = facturi_api.detalii_factura(conn, factura_id)
    if not f:
        raise HTTPException(404, "factură inexistentă")
    return f


@app.delete("/tenants/{tenant_id}/facturi/{factura_id}")
def factura_sterge(tenant_id: int, factura_id: int,
                   ctx=Depends(cere_rol("admin_firma", "angajat"))):
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        return facturi_api.sterge_factura(conn, factura_id)


# ============================================================
#  CLIENȚI (în schema tenantului)
# ============================================================
@app.get("/tenants/{tenant_id}/clienti")
def clienti_lista(tenant_id: int, status: Optional[str] = None,
                  ctx=Depends(cere_cabinet)):
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        return {"clienti": clienti_api.lista_clienti(conn, status)}


@app.post("/tenants/{tenant_id}/clienti")
def client_creeaza(tenant_id: int, date: ClientIn,
                   ctx=Depends(cere_rol("admin_firma", "angajat"))):
    schema = _schema_sau_404(ctx, tenant_id)
    try:
        with db.get_conn(schema) as conn:
            return clienti_api.creeaza_client(conn, **date.model_dump())
    except ValueError as e:
        raise HTTPException(422, str(e))


@app.get("/tenants/{tenant_id}/clienti/{client_id}")
def client_detalii(tenant_id: int, client_id: int, ctx=Depends(cere_cabinet)):
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        c = clienti_api.detalii_client(conn, client_id)
    if not c:
        raise HTTPException(404, "client inexistent")
    return c


@app.put("/tenants/{tenant_id}/clienti/{client_id}")
def client_actualizeaza(tenant_id: int, client_id: int, date: ClientEdit,
                        ctx=Depends(cere_rol("admin_firma", "angajat"))):
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        return clienti_api.actualizeaza_client(conn, client_id, **date.model_dump())


@app.delete("/tenants/{tenant_id}/clienti/{client_id}")
def client_sterge(tenant_id: int, client_id: int,
                  ctx=Depends(cere_rol("admin_firma", "angajat"))):
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        r = clienti_api.sterge_client(conn, client_id)
    if not r["ok"] and r.get("cod") == "ARE_FACTURI":
        raise HTTPException(409, r["mesaj"])
    return r


# ============================================================
#  SALARIAȚI (în schema tenantului)
# ============================================================
@app.get("/tenants/{tenant_id}/salariati")
def salariati_lista(tenant_id: int, activ: Optional[bool] = None,
                    ctx=Depends(cere_cabinet)):
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        return {"salariati": salariati_api.lista_salariati(conn, activ)}


@app.post("/tenants/{tenant_id}/salariati")
def salariat_creeaza(tenant_id: int, date: SalariatIn,
                     ctx=Depends(cere_rol("admin_firma", "angajat"))):
    schema = _schema_sau_404(ctx, tenant_id)
    try:
        with db.get_conn(schema) as conn:
            return salariati_api.creeaza_salariat(conn, **date.model_dump())
    except ValueError as e:
        raise HTTPException(422, str(e))


@app.get("/tenants/{tenant_id}/salariati/{salariat_id}")
def salariat_detalii(tenant_id: int, salariat_id: int, ctx=Depends(cere_cabinet)):
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        s = salariati_api.detalii_salariat(conn, salariat_id)
    if not s:
        raise HTTPException(404, "salariat inexistent")
    return s


@app.put("/tenants/{tenant_id}/salariati/{salariat_id}")
def salariat_actualizeaza(tenant_id: int, salariat_id: int, date: SalariatEdit,
                          ctx=Depends(cere_rol("admin_firma", "angajat"))):
    schema = _schema_sau_404(ctx, tenant_id)
    try:
        with db.get_conn(schema) as conn:
            return salariati_api.actualizeaza_salariat(conn, salariat_id, **date.model_dump())
    except ValueError as e:
        raise HTTPException(422, str(e))


@app.delete("/tenants/{tenant_id}/salariati/{salariat_id}")
def salariat_sterge(tenant_id: int, salariat_id: int,
                    ctx=Depends(cere_rol("admin_firma", "angajat"))):
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        r = salariati_api.sterge_salariat(conn, salariat_id)
    if not r["ok"] and r.get("cod") == "ARE_CONCEDII":
        raise HTTPException(409, r["mesaj"])
    return r


# ============================================================
#  COADĂ DECLARAȚII (flux validare: asistent -> senior -> depusă)
# ============================================================
# [p57_notif] helpere notificari pe fluxul cozii
def _coada_info(conn, coada_id):
    with conn.cursor() as cur:
        cur.execute("SELECT tip, perioada, creat_de_id, cabinet_id FROM public.declaratii_coada WHERE id=%s",
                    (coada_id,))
        r = cur.fetchone()
    if not r:
        return None
    return {"tip": r[0], "perioada": r[1], "creat_de_id": r[2], "cabinet_id": r[3]}

def _notif_de_validat(conn, cabinet_id, tip, perioada, creat_de_id):
    # notifica validatorii (mai putin pregatitorul)
    ids = _notif.validatorii_cabinetului(conn, cabinet_id, exclude_id=creat_de_id)
    txt = "Declaratie %s (%s) trimisa spre validare." % ((tip or "").upper(), perioada or "")
    _notif.adauga_multi(conn, ids, "de_validat", txt, link="validat")

def _notif_pregatitor(conn, coada_id, tip_eveniment, motiv=None):
    info = _coada_info(conn, coada_id)
    if not info or not info["creat_de_id"]:
        return
    tip = (info["tip"] or "").upper()
    per = info["perioada"] or ""
    if tip_eveniment == "respinsa":
        txt = "Declaratia %s (%s) a fost respinsa." % (tip, per)
        if motiv:
            txt += " Motiv: " + motiv
    elif tip_eveniment == "aprobata":
        txt = "Declaratia %s (%s) a fost aprobata." % (tip, per)
    elif tip_eveniment == "depusa":
        txt = "Declaratia %s (%s) a fost depusa." % (tip, per)
    else:
        txt = "Actualizare declaratie %s (%s)." % (tip, per)
    _notif.adauga(conn, info["creat_de_id"], tip_eveniment, txt, link="validat")

@app.post("/coada")
def coada_adauga(date: CoadaIn, ctx=Depends(cere_rol("admin_firma", "angajat"))):
    schema = _schema_sau_404(ctx, date.tenant_id)
    body = date.model_dump(exclude_none=True)
    for k in ("tenant_id", "tip", "inceput_la"):  # [p15] inceput_la nu merge la generator
        body.pop(k, None)
    # 1) generează declarația pe schema tenantului
    try:
        with db.get_conn(schema) as conn:
            xml, res = declaratii_api.genereaza(conn, schema, date.tip, body)
    except ValueError as e:
        raise HTTPException(422, str(e))
    payload = {"xml": xml, "avertismente": (res if isinstance(res, list) else getattr(res, "avertismente", None))}
    # 2) pune în coadă (pe public), stare 'la_senior'
    with db.get_conn() as conn:
        r = coada_api.adauga_in_coada(
            conn, ctx["firm"], date.tenant_id, date.tip, date.an, payload,
            creat_de=str(ctx["uid"]), creat_de_id=int(ctx["uid"]), luna=date.luna, trim=date.trim,
            inceput_la=date.inceput_la)  # [p15]
    if not r["ok"] and r.get("cod") == "DEJA_IN_COADA":
        raise HTTPException(409, r["mesaj"])
    # [p57_notif] notifica validatorii ca e ceva de validat
    if r.get("ok"):
        try:
            with db.get_conn() as conn:
                _notif_de_validat(conn, ctx["firm"], date.tip,
                                  r.get("perioada") or ("%s/%s" % (date.luna or date.trim or "", date.an)),
                                  int(ctx["uid"]))
        except Exception:
            pass
    return r


@app.get("/coada")
def coada_lista(stare: Optional[str] = None, ctx=Depends(cere_cabinet)):
    with db.get_conn() as conn:
        return {"coada": coada_api.lista_coada(conn, ctx["firm"], stare)}


@app.post("/coada/{coada_id}/aproba")
def coada_aproba(coada_id: int, ctx=Depends(cere_rol("admin_firma"))):
    with db.get_conn() as conn:
        if not _are_permisiune(ctx, "poate_valida"):
            raise HTTPException(status_code=403, detail="nu ai permisiunea de a valida declarații")
        r = coada_api.aproba(conn, coada_id, str(ctx["uid"]), aprobat_de_id=int(ctx["uid"]))
    if not r["ok"]:
        cod = r.get("cod")
        http = 409 if cod == "STARE_GRESITA" else (403 if cod == "PATRU_OCHI" else 404)
        raise HTTPException(http, r.get("mesaj", cod))
    # [p57_notif] notifica pregatitorul
    try:
        with db.get_conn() as conn:
            _notif_pregatitor(conn, coada_id, "aprobata")
    except Exception:
        pass
    return r


@app.post("/coada/{coada_id}/respinge")
def coada_respinge(coada_id: int, date: RespingeIn,
                   ctx=Depends(cere_rol("admin_firma"))):
    with db.get_conn() as conn:
        r = coada_api.respinge(conn, coada_id, str(ctx["uid"]), date.motiv, respins_de_id=int(ctx["uid"]))
    if not r["ok"]:
        raise HTTPException(409 if r.get("cod") == "STARE_GRESITA" else 404,
                            r.get("mesaj", r.get("cod")))
    # [p57_notif] notifica pregatitorul cu motivul
    try:
        with db.get_conn() as conn:
            _notif_pregatitor(conn, coada_id, "respinsa", motiv=date.motiv)
    except Exception:
        pass
    return r


@app.post("/coada/{coada_id}/depune")
def coada_depune(coada_id: int, date: DepuneIn = DepuneIn(),
                 ctx=Depends(cere_rol("admin_firma"))):
    with db.get_conn() as conn:
        if not _are_permisiune(ctx, "poate_depune"):
            raise HTTPException(status_code=403, detail="nu ai permisiunea de a depune declarații")
        r = coada_api.marcheaza_depusa(conn, coada_id, date.spv_index, depus_de=str(ctx["uid"]), depus_de_id=int(ctx["uid"]))
    if not r["ok"]:
        raise HTTPException(409 if r.get("cod") == "STARE_GRESITA" else 404,
                            r.get("mesaj", r.get("cod")))
    return r

# [p57_notif] RUTE NOTIFICARI
@app.get("/notificari")
def notificari_lista(doar_necitite: bool = False, ctx=Depends(cere_cabinet)):
    with db.get_conn() as conn:
        return _notif.lista(conn, ctx["uid"], doar_necitite=doar_necitite)

@app.get("/notificari/contor")
def notificari_contor(ctx=Depends(cere_cabinet)):
    with db.get_conn() as conn:
        return _notif.contor(conn, ctx["uid"])
@app.get("/notificari/sumar")  # [p63_notif_sumar]
def notificari_sumar(ctx=Depends(cere_cabinet)):
    with db.get_conn() as conn:
        return _notif.sumar(conn, ctx["uid"])

@app.post("/notificari/citit")
def notificari_citit_toate(ctx=Depends(cere_cabinet)):
    with db.get_conn() as conn:
        return _notif.marcheaza_citit(conn, ctx["uid"])

# [p62_pachete] RUTE PACHETE LUNARE
class PachetTextIn(BaseModel):
    text: str
    status: Optional[str] = "ciorna"

def _pachet_schema(ctx, tenant_id):
    with db.get_conn() as c:
        schema = auth_api.schema_tenant(c, ctx["uid"], tenant_id)
    if not schema:
        raise HTTPException(403, "nu ai acces la acest tenant")
    return schema

@app.get("/pachete/{tenant_id}/rezumat")
def pachet_rezumat(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    schema = _pachet_schema(ctx, tenant_id)
    with db.get_conn(schema) as cs, db.get_conn() as cp:
        return _pachete.rezumat_luna(cs, cp, tenant_id, an, luna)

@app.post("/pachete/{tenant_id}/genereaza")
def pachet_genereaza(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    schema = _pachet_schema(ctx, tenant_id)
    with db.get_conn(schema) as cs, db.get_conn() as cp:
        return _pachete.genereaza_poveste(cs, cp, tenant_id, an, luna)

@app.get("/pachete/{tenant_id}/poveste")
def pachet_poveste_get(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    _pachet_schema(ctx, tenant_id)
    with db.get_conn() as cp:
        return _pachete.get_poveste(cp, tenant_id, an, luna)

# ICRD_NOTIF_EMAIL_CLIENT_V1
def _email_client_tenant(conn, tenant_id):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT u.email FROM public.users u JOIN public.user_tenants ut ON ut.user_id=u.id "
            "WHERE ut.tenant_id=%s AND u.rol='client' AND u.activ=true LIMIT 1", (tenant_id,))
        r = cur.fetchone()
    return r[0] if r else None

def _nume_tenant(conn, tenant_id):
    with conn.cursor() as cur:
        cur.execute("SELECT nume FROM public.tenants WHERE id=%s", (tenant_id,))
        r = cur.fetchone()
    return r[0] if r else ""

@app.post("/pachete/{tenant_id}/poveste")
def pachet_poveste_set(tenant_id: int, an: int, luna: int, date: PachetTextIn, ctx=Depends(cere_cabinet)):
    _pachet_schema(ctx, tenant_id)
    with db.get_conn() as cp:
        r = _pachete.salveaza_poveste(cp, tenant_id, an, luna, date.text, status=date.status or "ciorna")
        if (date.status or "") == "aprobat":
            email = _email_client_tenant(cp, tenant_id)
            if email:
                nume = _nume_tenant(cp, tenant_id)
                luni_n = ["", "ianuarie", "februarie", "martie", "aprilie", "mai", "iunie",
                          "iulie", "august", "septembrie", "octombrie", "noiembrie", "decembrie"]
                subiect = "Raportul lunar - " + (luni_n[luna] if 1 <= luna <= 12 else str(luna)) + " " + str(an)
                html = ("<div style='font-family:sans-serif;font-size:15px;color:#111'>"
                        "<p>Buna,</p><p>Contabilul tau a pregatit raportul lunar pentru <b>" +
                        (nume or "firma ta") + "</b>. Il gasesti in portalul iConta, la Povestea lunii.</p>"
                        "<p><a href='https://iconta.eu' style='background:#2563eb;color:#fff;"
                        "padding:12px 22px;border-radius:8px;text-decoration:none;font-weight:600'>"
                        "Deschide portalul</a></p></div>")
                import core.observare as _obs
                _obs.trimite_email_html(email, subiect, html)
        return r

@app.post("/pachete/{tenant_id}/trimite")
def pachet_trimite(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    schema = _pachet_schema(ctx, tenant_id)
    nume = (ctx.get("prenume") or ctx.get("nume") or "")
    semnatura = ("Cu salutari,\n" + nume) if nume else "Cu salutari,"
    with db.get_conn(schema) as cs, db.get_conn() as cp:
        r = _pachete.trimite(cs, cp, tenant_id, an, luna, semnatura=semnatura)
    if not r.get("ok"):
        cod = r.get("cod")
        msg = {"FARA_EMAIL": "Firma nu are email setat in profil.",
               "NEAPROBATA": "Aproba povestea inainte de trimitere.",
               "EMAIL_ESUAT": "Emailul nu a putut fi trimis."}.get(cod, cod or "eroare")
        raise HTTPException(400, msg)
    return r

@app.post("/notificari/{nid}/citit")
def notificari_citit_una(nid: int, ctx=Depends(cere_cabinet)):
    with db.get_conn() as conn:
        return _notif.marcheaza_citit(conn, ctx["uid"], notif_id=nid)


# ============================================================
#  DECLARAȚII
# ============================================================
@app.get("/declaratii/tipuri")
def declaratii_tipuri(ctx=Depends(cere_cabinet)):
    return {"tipuri": declaratii_api.tipuri(),
            "periodicitate": {t: declaratii_api.periodicitate(t)
                              for t in declaratii_api.tipuri()}}


@app.post("/declaratii/{tip}")
def declaratie_genereaza(tip: str, date: DeclaratieIn,
                         ctx=Depends(cere_rol("admin_firma", "angajat"))):
    body = date.model_dump(exclude_none=True)
    tenant_id = body.pop("tenant_id")
    # 1) pe public: aflu schema tenantului + verific accesul userului
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
    if not schema:
        raise HTTPException(403, "nu ai acces la acest tenant")
    # 2) pe schema tenantului (SET LOCAL search_path în get_conn, PgBouncer-safe):
    #    modulul rulează pe conexiunea deja poziționată, NU mai setează el search_path
    try:
        with db.get_conn(schema) as conn:
            xml, res = declaratii_api.genereaza(conn, schema, tip, body)
    except ValueError as e:
        raise HTTPException(422, str(e))
    avert = getattr(res, "avertismente", None)
    return {"tip": tip, "xml": xml, "avertismente": avert}


# ============================================================
#  PORTAL CLIENT (read-only, izolat)
# ============================================================
def _tenant_client(ctx, tenant_id=None):
    """Rezolvă tenantul clientului din user_tenants. Un singur tenant -> implicit."""
    with db.get_conn() as conn:
        tenants = auth_api.tenantii_userului(conn, ctx["uid"])
    if not tenants:
        raise HTTPException(404, "nu aveți nicio firmă asociată")
    if tenant_id is not None:
        t = next((x for x in tenants if x["id"] == tenant_id), None)
        if not t:
            raise HTTPException(404, "firmă inexistentă sau fără acces")
        return t
    if len(tenants) == 1:
        return tenants[0]
    raise HTTPException(400, "aveți mai multe firme; specificați tenant_id")


@app.get("/portal/firme")
def portal_firme(ctx=Depends(cere_client)):
    with db.get_conn() as conn:
        return {"firme": auth_api.tenantii_userului(conn, ctx["uid"])}


@app.get("/portal/firma")
def portal_firma(tenant_id: Optional[int] = None, ctx=Depends(cere_client)):
    t = _tenant_client(ctx, tenant_id)
    with db.get_conn(t["schema_name"]) as conn:
        firma = portal_api.date_firma(conn, t["schema_name"])
    return {"tenant_id": t["id"], "nume": t.get("nume"), "firma": firma}


class RaportZ(BaseModel):
    data: str
    total_11: float = 0
    total_21: float = 0
    numerar: float = 0
    card: float = 0
@app.get("/tenants/{tenant_id}/bonuri/de-verificat")
def bonuri_de_verificat(tenant_id: int, ctx=Depends(cere_cabinet)):
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fara acces")
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT id, comerciant, cui, data, total, tva_11, articole, status
                FROM {schema}.bonuri WHERE status = 'de_verificat' ORDER BY creat_la
            """)
            bonuri = [{"id": r[0], "comerciant": r[1], "cui": r[2],
                       "data": r[3].isoformat() if r[3] else None,
                       "total": float(r[4] or 0), "tva": float(r[5] or 0),
                       "articole": r[6] or [], "status": r[7]} for r in cur.fetchall()]
    return {"bonuri": bonuri}
class BonLinie(BaseModel):
    cont: str
    valoare: float
class BonAproba(BaseModel):
    comerciant: str = ""
    data: str
    total: float
    tva: float = 0
    linii: list[BonLinie]
@app.post("/tenants/{tenant_id}/bonuri/{bon_id}/aproba")
def bon_aproba(tenant_id: int, bon_id: int, b: BonAproba, ctx=Depends(cere_cabinet)):
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fara acces")
        suma_linii = sum(l.valoare for l in b.linii)
        if abs(suma_linii - b.total) > 0.05:
            raise HTTPException(400, f"suma articolelor ({suma_linii}) != total ({b.total})")
        # valorile articolelor sunt cu TVA inclus; scad TVA proportional
        factor = (b.total - b.tva) / b.total if b.total else 1
        with conn.cursor() as cur:
            cur.execute(f"""
                INSERT INTO {schema}.inregistrari (data, numar, descriere, sursa, status)
                VALUES (%s, %s, %s, 'bon', 'validata') RETURNING id
            """, (b.data, f"BON-{bon_id}", f"Bon {b.comerciant}"))
            iid = cur.fetchone()[0]
            for l in b.linii:
                cur.execute(f"INSERT INTO {schema}.inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, %s, '5311', %s)",
                            (iid, l.cont, round(l.valoare * factor, 2)))
            if b.tva:
                cur.execute(f"INSERT INTO {schema}.inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, '4426', '5311', %s)",
                            (iid, b.tva))
            cur.execute(f"""
                UPDATE {schema}.bonuri SET status='aprobat',
                       comerciant=%s, data=%s, total=%s, inregistrare_id=%s
                WHERE id=%s
            """, (b.comerciant, b.data, b.total, iid, bon_id))
    return {"ok": True, "nota_id": iid}
@app.post("/tenants/{tenant_id}/amortizare")
def tenant_amortizare(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    """Genereaza nota de amortizare lunara: 6811 = cont_amortizare, per MF activ."""
    from datetime import date as _date
    from decimal import Decimal as D
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fara acces")
        ref = _date(an, luna, 1)
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT numar FROM {schema}.inregistrari
                WHERE sursa = 'amortizare' AND numar = %s
            """, (f"AMORT-{an}-{luna:02d}",))
            if cur.fetchone():
                raise HTTPException(400, "amortizarea lunii e deja generata")
            cur.execute(f"""
                SELECT id, denumire, cont_amortizare, valoare, COALESCE(rezidual,0), dnf_luni, data_pif
                FROM {schema}.mijloace_fixe WHERE activ = true
            """)
            mf = cur.fetchall()
        linii = []
        for mid, den, cont_am, val, rez, dnf, pif in mf:
            if not pif or not dnf:
                continue
            luni_trecute = (an - pif.year) * 12 + (luna - pif.month)
            if luni_trecute < 1 or luni_trecute > dnf:
                continue  # amortizarea incepe luna urmatoare PIF, se opreste la DNF
            rata = ((D(str(val)) - D(str(rez))) / dnf).quantize(D("0.01"))
            if rata > 0:
                linii.append((cont_am or "2813", float(rata), den))
        if not linii:
            return {"ok": True, "mesaj": "nimic de amortizat", "linii": 0}
        with conn.cursor() as cur:
            cur.execute(f"""
                INSERT INTO {schema}.inregistrari (data, numar, descriere, sursa, status)
                VALUES (%s, %s, %s, 'amortizare', 'validata') RETURNING id
            """, (_date(an, luna, 1).replace(day=28), f"AMORT-{an}-{luna:02d}", f"Amortizare {luna:02d}/{an}"))
            iid = cur.fetchone()[0]
            for cont_am, rata, den in linii:
                cur.execute(f"""
                    INSERT INTO {schema}.inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma)
                    VALUES (%s, '6811', %s, %s)
                """, (iid, cont_am, rata))
    return {"ok": True, "nota_id": iid, "linii": len(linii), "total": round(sum(r for _, r, _ in linii), 2)}
@app.get("/tenants/{tenant_id}/jurnal")
def tenant_jurnal(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fara acces")
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT i.id, i.data, i.numar, i.descriere, i.sursa, i.status, i.factura_id,
                       l.cont_debit, l.cont_credit, l.suma
                FROM {schema}.inregistrari i
                JOIN {schema}.inregistrari_linii l ON l.inregistrare_id = i.id
                WHERE date_trunc('month', i.data) = %s
                ORDER BY i.data, i.id, l.id
            """, (f"{an}-{luna:02d}-01",))
            note = {}
            for iid, data, nr, desc, sursa, status, fid, deb, cre, suma in cur.fetchall():
                if iid not in note:
                    note[iid] = {"id": iid, "data": data.isoformat(), "numar": nr,
                                 "descriere": desc, "sursa": sursa, "status": status, "factura_id": fid, "linii": []}
                note[iid]["linii"].append({"debit": deb, "credit": cre, "suma": float(suma)})
    return {"note": list(note.values())}
@app.post("/tenants/{tenant_id}/horeca/raport-z")
def horeca_raport_z(tenant_id: int, rz: RaportZ, ctx=Depends(cere_cabinet)):
    from decimal import Decimal as D
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fara acces")
        total = D(str(rz.total_11)) + D(str(rz.total_21))
        if abs(float(total) - (rz.numerar + rz.card)) > 0.01:
            raise HTTPException(400, "numerar + card trebuie sa fie egal cu totalul pe cote")
        # suta marita: TVA = total * cota / (100 + cota)
        tva11 = (D(str(rz.total_11)) * 11 / 111).quantize(D("0.01"))
        tva21 = (D(str(rz.total_21)) * 21 / 121).quantize(D("0.01"))
        baza11 = D(str(rz.total_11)) - tva11
        baza21 = D(str(rz.total_21)) - tva21
        with conn.cursor() as cur:
            cur.execute(f"""
                INSERT INTO {schema}.inregistrari (data, numar, descriere, sursa, status)
                VALUES (%s, %s, %s, 'horeca_z', 'validata') RETURNING id
            """, (rz.data, f"Z-{rz.data}", f"Raport Z {rz.data}"))
            iid = cur.fetchone()[0]
            linii = []
            if rz.numerar: linii.append(("5311", "707", rz.numerar))
            if rz.card: linii.append(("5125", "707", rz.card))
            # corectie TVA: 707 -> 4427 pentru TVA colectata
            tva_total = tva11 + tva21
            if tva_total: linii.append(("707", "4427", float(tva_total)))
            for deb, cre, suma in linii:
                cur.execute(f"""
                    INSERT INTO {schema}.inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma)
                    VALUES (%s, %s, %s, %s)
                """, (iid, deb, cre, suma))
    return {"ok": True, "nota_id": iid,
            "tva_11": float(tva11), "tva_21": float(tva21),
            "baza_11": float(baza11), "baza_21": float(baza21)}
@app.post("/tenants/{tenant_id}/banca/parse-extras")
async def banca_parse_extras(tenant_id: int, fisier: UploadFile = File(...), ctx=Depends(cere_cabinet)):
    from core import banca_parser, banca as _bk
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fara acces")
    continut = await fisier.read()
    try:
        tranzactii = banca_parser.parse_extras(continut, fisier.filename or "")
    except Exception as e:
        raise HTTPException(400, f"nu am putut citi extrasul: {e}")
    for t in tranzactii:
        linie = {"sens": "debit" if t["suma"] < 0 else "credit",
                 "suma": abs(t["suma"]), "descriere": t.get("detalii", "")}
        r = _bk.regula_cont(linie)
        t["cui"] = r.get("cui")
        t["tip"] = r.get("tip")
        t["nota"] = r.get("nota")
    return {"tranzactii": tranzactii, "nr": len(tranzactii)}
@app.get("/tenants/{tenant_id}/stat-plata")
def tenant_stat_plata(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    from core import stat_plata_api as _sp
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fara acces")
        return {"stat": _sp.stat_plata(conn, schema, an, luna)}
@app.get("/tenants/{tenant_id}/fluturas/{salariat_id}")
def tenant_fluturas(tenant_id: int, salariat_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    from fastapi.responses import Response
    from core import stat_plata_api as _sp
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fara acces")
        cur = conn.cursor(); cur.execute("SELECT nume FROM public.tenants WHERE id=%s", (tenant_id,))
        nf = (cur.fetchone() or [""])[0]
        pdf = _sp.fluturas_pdf(conn, schema, salariat_id, an, luna, nf)
    if pdf is None:
        raise HTTPException(404, "salariat inexistent")
    return Response(content=pdf, media_type="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="fluturas_{salariat_id}_{an}_{luna:02d}.pdf"'})
@app.get("/firme/{tenant_id}/verificari")
def firma_verificari(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    from core import verificatoare as _vf
    from datetime import date as _date
    sfarsit = _date(an + (luna == 12), (luna % 12) + 1, 1)
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fara acces")
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT l.cont_debit, l.cont_credit, l.suma
                FROM {schema}.inregistrari_linii l
                JOIN {schema}.inregistrari i ON i.id = l.inregistrare_id
                WHERE i.data < %s
            """, (sfarsit,))
            note = [{"debit": r[0], "credit": r[1], "suma": r[2]} for r in cur.fetchall()]
            cur.execute(f"SELECT cont, SUM(sold_debitor) - SUM(sold_creditor) FROM {schema}.solduri_initiale GROUP BY cont")
            si = {r[0]: r[1] for r in cur.fetchall()}
    bal = _vf.balanta(note, si)
    rez = {
        "echilibru": _vf.verifica_balanta(bal),
        "trezorerie": _vf.verifica_trezorerie(bal),
        "tva": _vf.coerenta_tva(bal.get("4427", {}).get("credit", 0), bal.get("4426", {}).get("debit", 0)),
        "note": len(note),
    }
    return rez
@app.post("/portal/bon")
async def portal_bon(fisiere: list[UploadFile] = File(...), tenant_id: Optional[int] = None, ctx=Depends(cere_client)):
    from core import ai_client
    import json as _json
    t = _tenant_client(ctx, tenant_id)
    if not ai_client.disponibil():
        raise HTTPException(503, "serviciul AI indisponibil")
    imagini = []
    for f in fisiere[:4]:
        b = await f.read()
        if len(b) > 8_000_000:
            raise HTTPException(400, "imagine prea mare (max 8MB)")
        imagini.append((b, f.content_type or "image/jpeg"))
    prompt = ("Citeste bonul fiscal (poate fi in mai multe imagini, in ordine). Raspunde DOAR cu JSON, fara alt text: "
              '{"comerciant": "...", "cui": "...", "data": "YYYY-MM-DD", "total": 0.0, '
              '"articole": [{"denumire": "...", "valoare": 0.0, "cota_tva": 0, "cont_propus": "..."}], '
              '"tva": [{"cota": 0, "valoare": 0.0}]}. '
              "Cotele TVA le citesti EXACT cum apar pe bon (pot fi 19/9/11/21/5 in functie de anul bonului). "
              "cont_propus = contul de cheltuiala OMFP 1802 potrivit articolului: 6022 combustibil, "
              "623 protocol (cafea, apa, mancare), 604 materiale nestocate, 628 alte servicii. "
              "Reducerile primesc contul articolului principal. "
              "Daca un camp nu se vede, pune null.")
    try:
        text = ai_client.citeste_imagini(imagini, prompt)
        text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        date = _json.loads(text)
    except Exception:
        raise HTTPException(422, "nu am putut citi bonul; incearca o poza mai clara")
    schema = t["schema_name"]
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            tva_lista = date.get("tva") or []
            tva_total = sum(x.get("valoare") or 0 for x in tva_lista)
            cur.execute(f"""
                INSERT INTO {schema}.bonuri (comerciant, cui, data, total, tva_11, tva_21, articole)
                VALUES (%s, %s, %s, %s, %s, 0, %s) RETURNING id
            """, (date.get("comerciant"), date.get("cui"), date.get("data"),
                  date.get("total") or 0, tva_total, _json.dumps(date.get("articole") or [])))
            bon_id = cur.fetchone()[0]
    return {"ok": True, "bon": date, "bon_id": bon_id}
@app.get("/portal/documente/luni")
def portal_documente_luni(tenant_id: Optional[int] = None, ctx=Depends(cere_client)):
    t = _tenant_client(ctx, tenant_id)
    with db.get_conn() as conn:
        luni = documente_api.luni_disponibile(conn, t["schema_name"])
        decl = documente_api.declaratii_depuse(conn, t["id"])
    return {"luni": luni, "declaratii": decl}
@app.get("/portal/documente/balanta")
def portal_documente_balanta(an: int, luna: int, tenant_id: Optional[int] = None, ctx=Depends(cere_client)):
    from fastapi.responses import Response
    t = _tenant_client(ctx, tenant_id)
    with db.get_conn() as conn:
        pdf = documente_api.balanta_pdf(conn, t["schema_name"], an, luna, t.get("nume") or "")
    return Response(content=pdf, media_type="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="balanta_{an}_{luna:02d}.pdf"'})
@app.get("/portal/facturi")
def portal_facturi(tenant_id: Optional[int] = None, an: Optional[int] = None,
                   luna: Optional[int] = None, ctx=Depends(cere_client)):
    t = _tenant_client(ctx, tenant_id)
    with db.get_conn(t["schema_name"]) as conn:
        return {"facturi": facturi_api.lista_facturi(conn, an, luna, None)}


@app.get("/portal/declaratii")
def portal_declaratii(tenant_id: Optional[int] = None, ctx=Depends(cere_client)):
    t = _tenant_client(ctx, tenant_id)
    with db.get_conn() as conn:
        return {"declaratii": portal_api.declaratii_depuse(conn, t["id"])}

# ICRD_RECOMANDA_UNIFICAT_V1
def _trimite_recomandari(emails, html, subiect):
    if not emails:
        raise HTTPException(400, "Niciun email valid.")
    if len(emails) > 20:
        raise HTTPException(400, "Maxim 20 de emailuri odata.")
    import core.observare as _obs
    rezultate = []
    for em in emails:
        ok = _obs.trimite_email_html(em, subiect, html)
        rezultate.append({"email": em, "stare": "trimis" if ok else "esuat"})
    return rezultate

def _mesaj_recomanda_client_html(nume_firma):
    return (
        "<div style='font-family:sans-serif;font-size:15px;color:#111;max-width:540px;line-height:1.55'>"
        "<p>Buna,</p>"
        "<p>Sunt client iConta si ma tine departe de batai de cap cu ANAF - "
        "imi arata din timp daca am ceva de depus sau de platit, inainte sa fie o problema.</p>"
        "<p>M-am gandit ca ti-ar prinde bine si tie.</p>"
        "<p style='margin:24px 0'><a href='https://iconta.eu' style='background:#2563eb;color:#fff;"
        "padding:12px 22px;border-radius:8px;text-decoration:none;font-weight:600'>Vezi iConta</a></p>"
        "</div>"
    )

class RecomandareClientIn(BaseModel):
    emails: list[str]

@app.get("/portal/recomanda/preview")
def portal_recomanda_preview(tenant_id: Optional[int] = None, ctx=Depends(cere_client)):
    t = _tenant_client(ctx, tenant_id)
    with db.get_conn(t["schema_name"]) as conn:
        firma = portal_api.date_firma(conn, t["schema_name"])
    nume_firma = (firma or {}).get("nume") or t.get("nume") or ""
    return {"ok": True, "html": _mesaj_recomanda_client_html(nume_firma),
            "subiect": "O recomandare de la " + (nume_firma or "un antreprenor")}

@app.post("/portal/recomanda")
def portal_recomanda(date: RecomandareClientIn, tenant_id: Optional[int] = None, ctx=Depends(cere_client)):
    emails = [e.strip() for e in (date.emails or []) if e and e.strip()]
    t = _tenant_client(ctx, tenant_id)
    with db.get_conn(t["schema_name"]) as conn:
        firma = portal_api.date_firma(conn, t["schema_name"])
    nume_firma = (firma or {}).get("nume") or t.get("nume") or ""
    html = _mesaj_recomanda_client_html(nume_firma)
    rezultate = _trimite_recomandari(emails, html, "O recomandare de la " + (nume_firma or "un antreprenor"))
    return {"ok": True, "rezultate": rezultate}


@app.get("/portal/povesti")
def portal_povesti(tenant_id: Optional[int] = None, ctx=Depends(cere_client)):
    t = _tenant_client(ctx, tenant_id)
    with db.get_conn() as conn:
        rows = _pachete.lista_povesti_aprobate(conn, t["id"])
        with db.get_conn(t["schema_name"]) as conn_s:
            for r in rows:
                an, luna = r["an"], r["luna"]
                an_p, luna_p = (an - 1, 12) if luna == 1 else (an, luna - 1)
                cur_rz = _pachete.rezumat_luna(conn_s, conn, t["id"], an, luna)
                prev_rz = _pachete.rezumat_luna(conn_s, conn, t["id"], an_p, luna_p)
                r["venituri"] = cur_rz["venituri"]
                r["cheltuieli"] = cur_rz["cheltuieli"]
                r["rezultat"] = cur_rz["rezultat"]
                r["rezultat_anterior"] = prev_rz["rezultat"]
                r["diferenta"] = round(cur_rz["rezultat"] - prev_rz["rezultat"], 2)
    return {"povesti": rows}

# ICRD_SOLICITARI_V1 - bucla solicitari client <-> cabinet
import psycopg2.extras as _E_sol
class SolicitareIn(BaseModel):
    mesaj: str

@app.get("/portal/solicitari")
def portal_solicitari_lista(tenant_id: Optional[int] = None, ctx=Depends(cere_client)):
    t = _tenant_client(ctx, tenant_id)
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=_E_sol.RealDictCursor) as cur:
            cur.execute(
                "SELECT id, mesaj, autor_rol, creat_la FROM public.solicitari_client "
                "WHERE tenant_id=%s ORDER BY id", (t["id"],))
            rows = cur.fetchall()
    return {"solicitari": rows}

@app.post("/portal/solicitari")
def portal_solicitari_trimite(date: SolicitareIn, tenant_id: Optional[int] = None, ctx=Depends(cere_client)):
    t = _tenant_client(ctx, tenant_id)
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO public.solicitari_client (tenant_id, mesaj, autor_rol, autor_id) "
                "VALUES (%s,%s,'client',%s)", (t["id"], date.mesaj, ctx["uid"]))
        with conn.cursor() as cur:
            cur.execute("SELECT accounting_firm_id, nume FROM public.tenants WHERE id=%s", (t["id"],))
            r = cur.fetchone()
        if r and r[0]:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id FROM public.users WHERE accounting_firm_id=%s AND activ=true", (r[0],))
                ids = [x[0] for x in cur.fetchall()]
            txt = "Mesaj nou de la %s: %s" % (r[1] or "firma", date.mesaj[:80])
            _notif.adauga_multi(conn, ids, "solicitare_client", txt, link="solicitari:%s" % t["id"])
    return {"ok": True}

@app.get("/tenants/{tenant_id}/solicitari")
def cabinet_solicitari_lista(tenant_id: int, ctx=Depends(cere_context)):
    _schema_sau_404(ctx, tenant_id)
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=_E_sol.RealDictCursor) as cur:
            cur.execute(
                "SELECT id, mesaj, autor_rol, creat_la, citit FROM public.solicitari_client "
                "WHERE tenant_id=%s ORDER BY id", (tenant_id,))
            rows = cur.fetchall()
    return {"solicitari": rows}

@app.post("/tenants/{tenant_id}/solicitari")
def cabinet_solicitari_raspunde(tenant_id: int, date: SolicitareIn, ctx=Depends(cere_context)):
    _schema_sau_404(ctx, tenant_id)
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO public.solicitari_client (tenant_id, mesaj, autor_rol, autor_id) "
                "VALUES (%s,%s,'cabinet',%s)", (tenant_id, date.mesaj, ctx["uid"]))
        conn.commit()
        email = _email_client_tenant(conn, tenant_id)
        if email:
            nume = _nume_tenant(conn, tenant_id)
            subiect = "Raspuns nou de la contabilul tau"
            html = ("<div style='font-family:sans-serif;font-size:15px;color:#111'>"
                    "<p>Buna,</p><p>Contabilul tau ti-a raspuns la o solicitare pentru <b>" +
                    (nume or "firma ta") + "</b>:</p>"
                    "<p style='background:#f5f5f5;padding:14px;border-radius:8px'>" +
                    date.mesaj.replace("<", "&lt;").replace(">", "&gt;") + "</p>"
                    "<p><a href='https://iconta.eu' style='background:#2563eb;color:#fff;"
                    "padding:12px 22px;border-radius:8px;text-decoration:none;font-weight:600'>"
                    "Deschide portalul</a></p></div>")
            import core.observare as _obs
            _obs.trimite_email_html(email, subiect, html)
    return {"ok": True}


@app.get("/portal/acasa")  # [p91_portal_acasa] status ANAF + scadente pentru firma clientului
def portal_acasa(tenant_id: Optional[int] = None, ctx=Depends(cere_client)):
    t = _tenant_client(ctx, tenant_id)
    schema = t["schema_name"]
    with db.get_conn(schema) as conn_schema:
        with db.get_conn() as conn_public:
            rez = control_fiscal_api.evalueaza_firma(conn_schema, conn_public, t["id"], schema)
    # normalizez pentru portal: stare + liste scurte de scadente
    return {
        "tenant_id": t["id"],
        "nume": t.get("nume"),
        "stare": rez.get("stare"),
        "mesaj": rez.get("mesaj"),
        "restante": rez.get("lipsa", []),
        "de_urmarit": rez.get("urmarit", []),
        "datorate": rez.get("datorate", 0),
        "depuse": rez.get("depuse", 0),
    }


# === ASISTENTI_API ROUTES ===
from core import asistenti_api as _asist
import core.notificari_api as _notif  # [p57_notif]
import core.pachete_api as _pachete  # [p62_pachete]
import core.raportari_api as _rap  # [p33]


def _cer_admin_cabinet(ctx):
    """Doar admin_firma (și superadmin) gestionează actorii. Întoarce id cabinet."""
    if ctx["rol"] not in ("admin_firma", "superadmin"):
        raise HTTPException(status_code=403, detail="Doar administratorul cabinetului.")
    return ctx["firm"]


@app.get("/asistenti")
def asistenti_lista(ctx=Depends(cere_cabinet)):
    cabinet_id = _cer_admin_cabinet(ctx)
    with db.get_conn() as conn:
        return {
            "sumar": _asist.sumar(conn, cabinet_id),
            "actori": _asist.lista_actori(conn, cabinet_id),
        }


@app.get("/asistenti/{uid}")
def asistenti_detalii(uid: int, ctx=Depends(cere_cabinet)):
    cabinet_id = _cer_admin_cabinet(ctx)
    with db.get_conn() as conn:
        r = _asist.detalii_actor(conn, cabinet_id, uid)
        if not r.get("ok"):
            raise HTTPException(status_code=404, detail=r.get("cod"))
        return r


@app.post("/asistenti/{uid}/permisiuni")
def asistenti_permisiuni(uid: int, date: dict = Body(...), ctx=Depends(cere_cabinet)):
    cabinet_id = _cer_admin_cabinet(ctx)
    with db.get_conn() as conn:
        r = _asist.set_permisiuni(
            conn, cabinet_id, uid,
            date.get("poate_pregati", False),
            date.get("poate_valida", False),
            date.get("poate_depune", False),
        )
        if not r.get("ok"):
            raise HTTPException(status_code=400, detail=r.get("cod"))
        return r


@app.post("/asistenti/{uid}/firme/{tid}")
def asistenti_atribuie(uid: int, tid: int, ctx=Depends(cere_cabinet)):
    cabinet_id = _cer_admin_cabinet(ctx)
    with db.get_conn() as conn:
        r = _asist.atribuie_firma(conn, cabinet_id, uid, tid)
        if not r.get("ok"):
            raise HTTPException(status_code=400, detail=r.get("cod"))
        return r


@app.delete("/asistenti/{uid}/firme/{tid}")
def asistenti_elimina(uid: int, tid: int, ctx=Depends(cere_cabinet)):
    cabinet_id = _cer_admin_cabinet(ctx)
    with db.get_conn() as conn:
        r = _asist.elimina_firma(conn, cabinet_id, uid, tid)
        if not r.get("ok"):
            raise HTTPException(status_code=400, detail=r.get("cod"))
        return r


@app.post("/asistenti/{uid}/dezactiveaza")
def asistenti_dezactiveaza(uid: int, ctx=Depends(cere_cabinet)):
    cabinet_id = _cer_admin_cabinet(ctx)
    with db.get_conn() as conn:
        r = _asist.dezactiveaza(conn, cabinet_id, uid, ctx["uid"])
        if not r.get("ok"):
            raise HTTPException(status_code=400, detail=r.get("cod"))
        return r


@app.post("/asistenti/{uid}/reactiveaza")
def asistenti_reactiveaza(uid: int, ctx=Depends(cere_cabinet)):
    cabinet_id = _cer_admin_cabinet(ctx)
    with db.get_conn() as conn:
        r = _asist.reactiveaza(conn, cabinet_id, uid)
        if not r.get("ok"):
            raise HTTPException(status_code=400, detail=r.get("cod"))
        return r



# [patch7_finalizeaza_firme]
@app.post("/asistenti/{uid}/finalizeaza-firme")
def asistenti_finalizeaza_firme(uid: int, ctx=Depends(cere_cabinet)):
    cabinet_id = _cer_admin_cabinet(ctx)
    with db.get_conn() as conn:
        r = _asist.aplica_regula_zero_firme(conn, cabinet_id, uid)
        if not r.get("ok"):
            raise HTTPException(status_code=400, detail=r.get("cod"))
        return r



# [patch9_semafor_rute]
@app.get("/asistenti/echipa/semafor")
def asistenti_semafor(zile: int = 30, ctx=Depends(cere_cabinet)):
    cabinet_id = _cer_admin_cabinet(ctx)
    with db.get_conn() as conn:
        return _asist.semafor_echipa(conn, cabinet_id, zile)


@app.get("/asistenti/echipa/erori")
def asistenti_erori(zile: int = 30, ctx=Depends(cere_cabinet)):
    cabinet_id = _cer_admin_cabinet(ctx)
    with db.get_conn() as conn:
        return _asist.erori_echipa(conn, cabinet_id, zile)

# [p16_activitate_cabinet_routes]
@app.get("/asistenti/echipa/centralizator")
def asistenti_centralizator(de: Optional[str] = None, pana: Optional[str] = None,
                            ctx=Depends(cere_cabinet)):
    cabinet_id = _cer_admin_cabinet(ctx)
    with db.get_conn() as conn:
        return _asist.centralizator(conn, cabinet_id, de=de, pana=pana)


@app.get("/asistenti/echipa/jurnal")
def asistenti_jurnal(de: Optional[str] = None, pana: Optional[str] = None,
                     limit: int = 200, ctx=Depends(cere_cabinet)):
    cabinet_id = _cer_admin_cabinet(ctx)
    with db.get_conn() as conn:
        return _asist.jurnal(conn, cabinet_id, de=de, pana=pana, limit=limit)


# [patch_asistenti_calitate]
@app.get("/asistenti/{uid}/calitate")
def asistenti_calitate(uid: int, de: Optional[str] = None,
                       pana: Optional[str] = None, ctx=Depends(cere_cabinet)):
    cabinet_id = _cer_admin_cabinet(ctx)
    with db.get_conn() as conn:
        r = _asist.calitate(conn, cabinet_id, uid, de=de, pana=pana)
        if not r.get("ok"):
            raise HTTPException(404, r.get("cod", "eroare"))
        return r


@app.get("/asistenti/{uid}/activitate")
def asistenti_activitate(uid: int, ctx=Depends(cere_cabinet)):
    cabinet_id = _cer_admin_cabinet(ctx)
    with db.get_conn() as conn:
        r = _asist.activitate(conn, cabinet_id, uid)
        if not r.get("ok"):
            raise HTTPException(status_code=404, detail=r.get("cod"))
        return r


# [p18_selfview]
@app.get("/eu/calitate")
def eu_calitate(de: Optional[str] = None, pana: Optional[str] = None,
                ctx=Depends(cere_cabinet)):
    """Self-view: propria calitate (nivel, semafor, rata, tipare). uid din token."""
    with db.get_conn() as conn:
        r = _asist.calitate(conn, ctx["firm"], ctx["uid"], de=de, pana=pana)
        if not r.get("ok"):
            raise HTTPException(404, r.get("cod", "eroare"))
        return r




# [p27_setari_routes]
class SchimbaParolaIn(BaseModel):
    parola_veche: str
    parola_noua: str


class ProfilIn(BaseModel):
    nume: Optional[str] = None
    prenume: Optional[str] = None


# [p47_compet]
class CompetenteIn(BaseModel):
    poate_pregati: bool = False
    poate_valida: bool = False
    poate_depune: bool = False

# [p50_edu]
@app.get("/eu/educatie")
def eu_educatie(ctx=Depends(cere_cabinet)):
    if ctx["rol"] not in ("admin_firma", "superadmin"):
        return {"ok": True, "educatii": []}
    with db.get_conn() as conn:
        return _asist.educatie_de_aratat(conn, ctx["firm"])

# [p54_4ochi]
class PatruOchiIn(BaseModel):
    activ: bool

@app.post("/eu/patru-ochi")
def eu_patru_ochi(date: PatruOchiIn, ctx=Depends(cere_cabinet)):
    if ctx["rol"] not in ("admin_firma", "superadmin"):
        raise HTTPException(403, "Doar patronul.")
    with db.get_conn() as conn:
        return _asist.patru_ochi_seteaza(conn, ctx["firm"], date.activ)


@app.post("/eu/educatie/patru-ochi/vazut")
def eu_educatie_vazut(ctx=Depends(cere_cabinet)):
    if ctx["rol"] not in ("admin_firma", "superadmin"):
        raise HTTPException(403, "Doar patronul.")
    with db.get_conn() as conn:
        return _asist.educatie_marcheaza(conn, ctx["firm"])


@app.get("/eu/competente")
def eu_competente_get(ctx=Depends(cere_cabinet)):
    with db.get_conn() as conn:
        return _asist.get_competente_proprii(conn, ctx["uid"])

@app.post("/eu/competente")
def eu_competente_set(date: CompetenteIn, ctx=Depends(cere_cabinet)):
    with db.get_conn() as conn:
        return _asist.set_competente_proprii(
            conn, ctx["uid"], date.poate_pregati, date.poate_valida, date.poate_depune)


@app.post("/eu/schimba-parola")
def eu_schimba_parola(date: SchimbaParolaIn, ctx=Depends(cere_cabinet)):
    if len(date.parola_noua or "") < 8:
        raise HTTPException(422, "Parola noua trebuie sa aiba minim 8 caractere.")
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT password_hash FROM public.users WHERE id = %s", (ctx["uid"],))
            row = cur.fetchone()
        if not row or not auth_api.verifica_parola_orice(date.parola_veche, row[0]):
            raise HTTPException(403, "Parola actuala este gresita.")
        auth_api.schimba_parola(conn, ctx["uid"], date.parola_noua)
    return {"ok": True}


@app.post("/eu/profil")
def eu_profil(date: ProfilIn, ctx=Depends(cere_cabinet)):
    with db.get_conn() as conn:
        r = auth_api.actualizeaza_profil(conn, ctx["uid"], nume=date.nume, prenume=date.prenume)
    if not r.get("ok"):
        raise HTTPException(422, r.get("cod", "eroare"))
    return r


# [p29_cabinet_routes]
class CabinetIn(BaseModel):
    nume: Optional[str] = None
    cui: Optional[str] = None


@app.get("/eu/cabinet")
def eu_cabinet_get(ctx=Depends(cere_cabinet)):
    with db.get_conn() as conn:
        r = auth_api.get_cabinet(conn, ctx["firm"])
    if not r.get("ok"):
        raise HTTPException(404, r.get("cod", "eroare"))
    return r


@app.post("/eu/cabinet")
def eu_cabinet_set(date: CabinetIn, ctx=Depends(cere_cabinet)):
    if ctx["rol"] not in ("admin_firma", "superadmin"):
        raise HTTPException(403, "Doar administratorul cabinetului poate edita datele cabinetului.")
    with db.get_conn() as conn:
        r = auth_api.actualizeaza_cabinet(conn, ctx["firm"], nume=date.nume, cui=date.cui)
    if not r.get("ok"):
        raise HTTPException(422, r.get("cod", "eroare"))
    return r


# [p30_recomanda]
_APP_URL = "https://iconta.eu"


def _mesaj_promo_html(nume_cabinet):
    # [p32_mesaj] text cu diacritice, 4 atribute principale ale aplicatiei
    cine = nume_cabinet or "Un cabinet de contabilitate"
    _li = "margin:0 0 10px 0;padding-left:2px"
    return (
        "<!-- [p32_mesaj] -->"
        "<div style='font-family:sans-serif;font-size:15px;color:#111;max-width:540px;line-height:1.55'>"
        "<p>Bună,</p>"
        "<p>" + cine + " folosește <b>iConta</b> și s-a gândit că ți-ar prinde bine și ție.</p>"
        "<p>iConta e contabilitatea în cloud care lucrează pentru tine și echipa ta:</p>"
        "<ul style='margin:14px 0;padding-left:20px'>"
        "<li style='" + _li + "'><b>Te apără</b> &mdash; semaforul fiscal te avertizează înainte "
        "să depui ceva ce-ți aduce control.</li>"
        "<li style='" + _li + "'><b>Face munca grea</b> &mdash; citește documentele și propune "
        "contările; tu doar verifici și aprobi.</li>"
        "<li style='" + _li + "'><b>Îți conduce echipa</b> &mdash; împarți firmele pe asistenți, "
        "urmărești cine ce lucrează, cu validare în patru ochi înainte de depunere.</li>"
        "<li style='" + _li + "'><b>Adună tot</b> &mdash; contabilitate, salarizare, declarații, "
        "e-Factura și SAF-T, pe același client.</li>"
        "</ul>"
        "<p>Mai puțin timp pierdut, mai puține greșeli costisitoare.</p>"
        "<p style='margin:24px 0'><a href='" + _APP_URL + "' style='background:#2563eb;color:#fff;"
        "padding:12px 22px;border-radius:8px;text-decoration:none;font-weight:600'>Încearcă iConta</a></p>"
        "</div>"
    )


class RecomandareIn(BaseModel):
    emails: list[str]


# [p67_recprev]
@app.get("/recomanda/preview")
def recomanda_preview(ctx=Depends(cere_cabinet)):
    with db.get_conn() as conn:
        r = auth_api.get_cabinet(conn, ctx["firm"])
    nume_cabinet = (r.get("cabinet") or {}).get("nume", "") if r.get("ok") else ""
    return {"ok": True, "html": _mesaj_promo_html(nume_cabinet),
            "subiect": "O recomandare pentru cabinetul tau: iConta"}

@app.post("/recomanda")
def trimite_recomandari(date: RecomandareIn, ctx=Depends(cere_cabinet)):
    emails = [e.strip() for e in (date.emails or []) if e and e.strip()]
    with db.get_conn() as conn:
        r = auth_api.get_cabinet(conn, ctx["firm"])
    nume_cabinet = (r.get("cabinet") or {}).get("nume", "") if r.get("ok") else ""
    html = _mesaj_promo_html(nume_cabinet)
    rezultate = _trimite_recomandari(emails, html, "O recomandare pentru cabinetul tau: iConta")
    return {"ok": True, "rezultate": rezultate}


# [p33_raportari]
class RaportareNouaIn(BaseModel):
    subiect: Optional[str] = None
    text: str


class MesajIn(BaseModel):
    text: str


@app.post("/raportari")
def raportari_creeaza(date: RaportareNouaIn, ctx=Depends(cere_cabinet)):
    with db.get_conn() as conn:
        r = _rap.creeaza_raportare(conn, ctx["uid"], ctx.get("firm"), date.subiect, date.text)
    if not r.get("ok"):
        raise HTTPException(400, r.get("cod", "eroare"))
    return r


@app.get("/raportari/eu")
def raportari_mele(ctx=Depends(cere_cabinet)):
    with db.get_conn() as conn:
        return _rap.raportarile_mele(conn, ctx["uid"])


@app.get("/raportari/contor")
def raportari_contor(ctx=Depends(cere_cabinet)):
    with db.get_conn() as conn:
        return _rap.contor_necitite(conn, ctx["uid"])


@app.get("/raportari/admin")
def raportari_admin(ctx=Depends(cere_cabinet)):
    if ctx["rol"] != "superadmin":
        raise HTTPException(403, "Doar Admin iConta.")
    with db.get_conn() as conn:
        return _rap.toate_raportarile(conn)


@app.get("/raportari/{rid}")
def raportari_fir(rid: int, ctx=Depends(cere_cabinet)):
    with db.get_conn() as conn:
        r = _rap.firul_complet(conn, rid)
        if not r.get("ok"):
            raise HTTPException(404, r.get("cod", "eroare"))
        # acces: autorul firului sau superadmin
        if ctx["rol"] != "superadmin" and r["raportare"]["autor_id"] != ctx["uid"]:
            raise HTTPException(403, "Nu ai acces la aceasta raportare.")
        return r


@app.post("/raportari/{rid}/mesaj")
def raportari_mesaj(rid: int, date: MesajIn, ctx=Depends(cere_cabinet)):
    rol_autor = "admin" if ctx["rol"] == "superadmin" else "utilizator"
    with db.get_conn() as conn:
        # utilizatorul poate scrie doar in firele lui
        if rol_autor == "utilizator":
            f = _rap.firul_complet(conn, rid)
            if not f.get("ok"):
                raise HTTPException(404, "Inexistent.")
            if f["raportare"]["autor_id"] != ctx["uid"]:
                raise HTTPException(403, "Nu ai acces.")
        r = _rap.adauga_mesaj(conn, rid, ctx["uid"], rol_autor, date.text)
    if not r.get("ok"):
        raise HTTPException(400, r.get("cod", "eroare"))
    return r


@app.post("/raportari/{rid}/citit")
def raportari_citit(rid: int, ctx=Depends(cere_cabinet)):
    cine_rol = "admin" if ctx["rol"] == "superadmin" else "utilizator"
    with db.get_conn() as conn:
        return _rap.marcheaza_citit(conn, rid, cine_rol)


# [p38_pentru_admin]
class PentruAdminIn(BaseModel):
    valoare: bool = True

@app.post("/raportari/{rid}/pentru-admin")
def raportari_pentru_admin(rid: int, date: PentruAdminIn, ctx=Depends(cere_cabinet)):
    if ctx["rol"] != "superadmin":
        raise HTTPException(403, "Doar Admin iConta.")
    with db.get_conn() as conn:
        r = _rap.seteaza_pentru_admin(conn, rid, date.valoare)
    if not r.get("ok"):
        raise HTTPException(404, r.get("cod", "eroare"))
    return r


# [p35_raportari_imagine]
@app.post("/raportari/mesaj/{mid}/imagine")
async def raportari_imagine(mid: int, fisier: UploadFile = File(...), ctx=Depends(cere_cabinet)):
    import os as _os, uuid as _uuid
    tip = (fisier.content_type or "").lower()
    if tip not in ("image/png", "image/jpeg", "image/jpg", "image/webp"):
        raise HTTPException(415, "Doar capturi de ecran (PNG, JPG, WEBP).")
    continut = await fisier.read()
    if len(continut) > 8 * 1024 * 1024:
        raise HTTPException(413, "Imaginea e prea mare (max 8MB).")
    with db.get_conn() as conn:
        info = _rap.autor_mesajului(conn, mid)
        if not info:
            raise HTTPException(404, "Mesaj inexistent.")
        # acces: superadmin, sau autorul mesajului
        if ctx["rol"] != "superadmin" and info["mesaj_autor"] != ctx["uid"]:
            raise HTTPException(403, "Nu ai acces.")
        ext = {"image/png": ".png", "image/jpeg": ".jpg", "image/jpg": ".jpg",
               "image/webp": ".webp"}.get(tip, ".png")
        nume = "r%d_m%d_%s%s" % (info["raportare_id"], mid, _uuid.uuid4().hex[:8], ext)
        director = _os.path.join(_STATIC_DIR, "raportari")
        _os.makedirs(director, exist_ok=True)
        cale_disc = _os.path.join(director, nume)
        with open(cale_disc, "wb") as fh:
            fh.write(continut)
        cale_web = "/static/raportari/" + nume
        r = _rap.adauga_atasament(conn, mid, cale_web, fisier.filename)
    if not r.get("ok"):
        raise HTTPException(400, r.get("cod", "eroare"))
    return {"ok": True, "cale": cale_web}
# === /ASISTENTI_API ROUTES ===


# === PERMISIUNI FLUX (coada) ===
def _are_permisiune(ctx, flag):
    """True dacă userul curent are flagul (poate_valida / poate_depune).
    superadmin trece mereu. Citește direct din public.users."""
    if ctx.get("rol") == "superadmin":
        return True
    if flag not in ("poate_pregati", "poate_valida", "poate_depune"):
        return False
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT %s FROM public.users WHERE id = %%s" % flag,
                        (ctx["uid"],))
            r = cur.fetchone()
            return bool(r and r[0])


@app.get("/eu/permisiuni")
def eu_permisiuni(ctx=Depends(cere_cabinet)):
    """Permisiunile actorului curent — pentru ca frontendul să rescrie butoanele
    fără relogare (permisiunile se schimbă din cardul Asistenți)."""
    if ctx.get("rol") == "superadmin":
        return {"poate_pregati": True, "poate_valida": True, "poate_depune": True,
                "rol": "superadmin"}
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT poate_pregati, poate_valida, poate_depune, rol "
                "FROM public.users WHERE id = %s", (ctx["uid"],))
            r = cur.fetchone()
    if not r:
        raise HTTPException(status_code=404, detail="user inexistent")
    return {"poate_pregati": bool(r[0]), "poate_valida": bool(r[1]),
            "poate_depune": bool(r[2]), "rol": r[3]}
# === /PERMISIUNI FLUX ===


# --- reconciliere bancara ---
@app.post("/tenants/{tenant_id}/banca/reconciliere/import")
async def banca_rec_import(tenant_id: int, fisier: UploadFile = File(...), ctx=Depends(cere_cabinet)):
    from core import banca_parser, banca as _bk, reconciliere_api as _rec
    continut = await fisier.read()
    try:
        tranzactii = banca_parser.parse_extras(continut, fisier.filename or "")
    except Exception as e:
        raise HTTPException(400, f"nu am putut citi extrasul: {e}")
    for t in tranzactii:
        r = _bk.regula_cont({"sens": "debit" if t["suma"] < 0 else "credit",
                             "suma": abs(t["suma"]), "descriere": t.get("detalii", "")})
        t["cui"], t["tip"], t["nota"] = r.get("cui"), r.get("tip"), r.get("nota")
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fara acces")
        return {"linii": _rec.importa_extras(conn, schema, tranzactii, fisier.filename or "")}

@app.get("/tenants/{tenant_id}/banca/reconciliere")
def banca_rec_lista(tenant_id: int, status: str = None, ctx=Depends(cere_cabinet)):
    from core import reconciliere_api as _rec
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fara acces")
        return {"linii": _rec.lista(conn, schema, status)}

@app.post("/tenants/{tenant_id}/banca/reconciliere/{linie_id}/conteaza")
def banca_rec_conteaza(tenant_id: int, linie_id: int, corp: dict = Body(default={}), ctx=Depends(cere_cabinet)):
    from core import reconciliere_api as _rec
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fara acces")
        rez = _rec.conteaza(conn, schema, linie_id, corp.get("alocari"))
    if rez is None:
        raise HTTPException(404, "linie inexistenta")
    if rez.get("eroare"):
        raise HTTPException(400, rez["eroare"])
    return rez


@app.get("/tenants/{tenant_id}/banca/reconciliere/facturi-deschise")
def banca_rec_facturi(tenant_id: int, ctx=Depends(cere_cabinet)):
    from core import reconciliere_api as _rec
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fara acces")
        return {"facturi": _rec.facturi_deschise_detalii(conn, schema)}


# --- jurnal: editare/stergere/validare ciorne ---
def _jurnal_rez(rez):
    if rez is None:
        raise HTTPException(404, "nota inexistenta")
    if rez.get("eroare"):
        raise HTTPException(400, rez["eroare"])
    return rez

@app.put("/tenants/{tenant_id}/jurnal/{nota_id}")
def jurnal_editeaza(tenant_id: int, nota_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    from core import jurnal_api as _j
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fara acces")
        return _jurnal_rez(_j.editeaza(conn, schema, nota_id,
                                       corp.get("descriere"), corp.get("data"), corp.get("linii")))

@app.delete("/tenants/{tenant_id}/jurnal/{nota_id}")
def jurnal_sterge(tenant_id: int, nota_id: int, ctx=Depends(cere_cabinet)):
    from core import jurnal_api as _j
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fara acces")
        return _jurnal_rez(_j.sterge(conn, schema, nota_id))

@app.post("/tenants/{tenant_id}/jurnal/{nota_id}/valideaza")
def jurnal_valideaza(tenant_id: int, nota_id: int, ctx=Depends(cere_cabinet)):
    from core import jurnal_api as _j
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fara acces")
        return _jurnal_rez(_j.valideaza(conn, schema, nota_id))


@app.post("/tenants/{tenant_id}/banca/reconciliere/{linie_id}/ignora")
def banca_rec_ignora(tenant_id: int, linie_id: int, ctx=Depends(cere_cabinet)):
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fara acces")
        with conn.cursor() as cur:
            cur.execute(f"UPDATE {schema}.extras_linii SET status='ignorat' WHERE id=%s AND status != 'contat' RETURNING id", (linie_id,))
            r = cur.fetchone()
        conn.commit()
    if not r:
        raise HTTPException(400, "linie inexistenta sau deja contata")
    return {"ok": True}


# --- registru de casa ---
@app.get("/tenants/{tenant_id}/casa/registru")
def casa_registru(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    from core import casa_api as _c
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fara acces")
        return _c.registru(conn, schema, an, luna)

@app.post("/tenants/{tenant_id}/casa/operatiuni")
def casa_adauga(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    from core import casa_api as _c
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fara acces")
        rez = _c.adauga(conn, schema, corp)
    if rez.get("eroare"):
        raise HTTPException(400, rez["eroare"])
    return rez

@app.delete("/tenants/{tenant_id}/casa/operatiuni/{op_id}")
def casa_sterge(tenant_id: int, op_id: int, ctx=Depends(cere_cabinet)):
    from core import casa_api as _c
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fara acces")
        rez = _c.sterge(conn, schema, op_id)
    if rez is None:
        raise HTTPException(404, "operatiune inexistenta")
    if rez.get("eroare"):
        raise HTTPException(400, rez["eroare"])
    return rez


# --- stocuri global-valorica ---
@app.get("/tenants/{tenant_id}/stocuri/nir")
def stocuri_lista(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    from core import stocuri_api as _s
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fara acces")
        return {"nir": _s.lista_nir(conn, schema, an, luna)}

@app.post("/tenants/{tenant_id}/stocuri/nir")
def stocuri_adauga(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    from core import stocuri_api as _s
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fara acces")
        rez = _s.adauga_nir(conn, schema, corp)
    if rez.get("eroare"):
        raise HTTPException(400, rez["eroare"])
    return rez

@app.post("/tenants/{tenant_id}/stocuri/descarcare")
def stocuri_descarcare(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    from core import stocuri_api as _s
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fara acces")
        rez = _s.descarca_luna(conn, schema, an, luna)
    if rez.get("eroare"):
        raise HTTPException(400, rez["eroare"])
    return rez


# --- stocuri cantitativ-valorice ---
@app.get("/tenants/{tenant_id}/stocuri/articole")
def cv_articole(tenant_id: int, ctx=Depends(cere_cabinet)):
    from core import stocuri_cv_api as _s
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fara acces")
        return {"articole": _s.articole(conn, schema)}

@app.get("/tenants/{tenant_id}/stocuri/articole/{articol_id}/fisa")
def cv_fisa(tenant_id: int, articol_id: int, ctx=Depends(cere_cabinet)):
    from core import stocuri_cv_api as _s
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fara acces")
        rez = _s.fisa(conn, schema, articol_id)
    if rez is None:
        raise HTTPException(404, "articol inexistent")
    return rez

@app.post("/tenants/{tenant_id}/stocuri/intrare")
def cv_intrare(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    from core import stocuri_cv_api as _s
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fara acces")
        rez = _s.intrare(conn, schema, corp)
    if rez.get("eroare"):
        raise HTTPException(400, rez["eroare"])
    return rez

@app.post("/tenants/{tenant_id}/stocuri/iesire")
def cv_iesire(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    from core import stocuri_cv_api as _s
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fara acces")
        rez = _s.iesire(conn, schema, corp)
    if rez is None:
        raise HTTPException(404, "articol inexistent")
    if rez.get("eroare"):
        raise HTTPException(400, rez["eroare"])
    return rez


@app.post("/tenants/{tenant_id}/stocuri/inventar")
def cv_inventar(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    from core import stocuri_cv_api as _s
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fara acces")
        return _s.inventar(conn, schema, corp)


# --- D112 ---
@app.get("/tenants/{tenant_id}/d112-xml")
def d112_xml(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    from core import d112 as _d
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fara acces")
        xml, av = _d.genereaza(conn, schema, an, luna)
    return {"xml": xml, "avertismente": av}

@app.post("/tenants/{tenant_id}/d112-valideaza")
def d112_valideaza(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    import base64, subprocess, tempfile, os
    from core import d112 as _d
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fara acces")
        xml, av = _d.genereaza(conn, schema, an, luna)
    with tempfile.TemporaryDirectory() as td:
        cale = os.path.join(td, f"d112_{tenant_id}_{an}_{luna:02d}.xml")
        open(cale, "w", encoding="utf-8").write(xml)
        r = subprocess.run(["java", "-jar", "DUKIntegrator.jar", "-v", "D112", cale],
                           cwd="/home/costin/duk/dist", capture_output=True, text=True, timeout=120)
        erori = ""
        err_f = cale + ".err.txt"
        if os.path.exists(err_f):
            erori = open(err_f, encoding="utf-8").read()
    ok = "fara erori" in (r.stdout + r.stderr) and not erori.strip().startswith(("E:", "F:"))
    return {"ok": ok, "erori": erori, "avertismente": av,
            "xml_b64": base64.b64encode(xml.encode()).decode()}


# --- S1005 (bilant micro) ---
@app.get("/tenants/{tenant_id}/s1005-xml")
def s1005_xml(tenant_id: int, an: int, ctx=Depends(cere_cabinet)):
    from core import bilant_api as _ba
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fara acces")
        xml, av = _ba.genereaza(conn, schema, an)
    return {"xml": xml, "avertismente": av}

@app.post("/tenants/{tenant_id}/s1005-valideaza")
def s1005_valideaza(tenant_id: int, an: int, ctx=Depends(cere_cabinet)):
    import base64, subprocess, tempfile, os
    from core import bilant_api as _ba
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fara acces")
        xml, av = _ba.genereaza(conn, schema, an)
    with tempfile.TemporaryDirectory() as td:
        cale = os.path.join(td, f"s1005_{tenant_id}_{an}.xml")
        open(cale, "w", encoding="utf-8").write(xml)
        r = subprocess.run(["java", "-jar", "DUKIntegrator.jar", "-v", "S1005", cale],
                           cwd="/home/costin/duk/dist", capture_output=True, text=True, timeout=120)
        erori = ""
        err_f = cale + ".err.txt"
        if os.path.exists(err_f):
            erori = open(err_f, encoding="utf-8").read()
    ok = "fara erori" in (r.stdout + r.stderr)
    return {"ok": ok, "erori": erori, "avertismente": av,
            "xml_b64": base64.b64encode(xml.encode()).decode()}


# --- S1003 (bilant mici) ---
@app.get("/tenants/{tenant_id}/s1003-xml")
def s1003_xml(tenant_id: int, an: int, ctx=Depends(cere_cabinet)):
    from core import bilant_api as _ba
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fara acces")
        xml, av = _ba.genereaza_s1003(conn, schema, an)
    return {"xml": xml, "avertismente": av}

@app.post("/tenants/{tenant_id}/s1003-valideaza")
def s1003_valideaza(tenant_id: int, an: int, ctx=Depends(cere_cabinet)):
    import base64, subprocess, tempfile, os
    from core import bilant_api as _ba
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fara acces")
        xml, av = _ba.genereaza_s1003(conn, schema, an)
    with tempfile.TemporaryDirectory() as td:
        cale = os.path.join(td, f"s1003_{tenant_id}_{an}.xml")
        open(cale, "w", encoding="utf-8").write(xml)
        r = subprocess.run(["java", "-jar", "DUKIntegrator.jar", "-v", "S1003", cale],
                           cwd="/home/costin/duk/dist", capture_output=True, text=True, timeout=120)
        erori = ""
        if os.path.exists(cale + ".err.txt"):
            erori = open(cale + ".err.txt", encoding="utf-8").read()
    ok = "fara erori" in (r.stdout + r.stderr)
    return {"ok": ok, "erori": erori, "avertismente": av,
            "xml_b64": base64.b64encode(xml.encode()).decode()}


# --- Retetar HoReCa ---
@app.get("/tenants/{tenant_id}/retete")
def retete_lista(tenant_id: int, ctx=Depends(cere_cabinet)):
    from core import retete_api as _r
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fara acces")
        return _r.lista(conn, schema)

@app.post("/tenants/{tenant_id}/retete")
def retete_salveaza(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    from core import retete_api as _r
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fara acces")
        return _r.salveaza(conn, schema, corp)

@app.delete("/tenants/{tenant_id}/retete/{reteta_id}")
def retete_sterge(tenant_id: int, reteta_id: int, ctx=Depends(cere_cabinet)):
    from core import retete_api as _r
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fara acces")
        return _r.sterge(conn, schema, reteta_id)

@app.post("/tenants/{tenant_id}/retete/descarca")
def retete_descarca(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    from core import retete_api as _r
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fara acces")
        try:
            return _r.descarca(conn, schema, corp)
        except ValueError as e:
            raise HTTPException(400, str(e))


@app.get("/tenants/{tenant_id}/verificare-stocuri")
def verificare_stocuri(tenant_id: int, ctx=Depends(cere_cabinet)):
    """Compara soldul contabil (solduri_initiale + note validate) pe fiecare cont de stoc
    folosit in articole cu valoarea insumata a fiselor CV (cantitate x CMP)."""
    from decimal import Decimal
    from psycopg2.extras import RealDictCursor
    from core import stocuri_cv as _m
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fara acces")
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(f"SELECT id, denumire, cont_stoc FROM {schema}.articole ORDER BY id")
            arts = [dict(r) for r in cur.fetchall()]
            val_cv = {}
            for a in arts:
                cur.execute(f"""SELECT data, tip, cantitate, pret_unitar FROM {schema}.miscari_stoc
                                WHERE articol_id=%s ORDER BY data, id""", (a["id"],))
                fisa = _m.fisa_magazie([dict(r) for r in cur.fetchall()])
                if fisa:
                    u = fisa[-1]
                    v = Decimal(str(u["sold_cantitate"] or 0)) * Decimal(str(u["cmp"] or 0))
                    val_cv[a["cont_stoc"]] = val_cv.get(a["cont_stoc"], Decimal("0")) + v
            rez = []
            for cont, vcv in sorted(val_cv.items()):
                cur.execute(f"""SELECT COALESCE(SUM(sold_debitor - sold_creditor),0) AS si
                                FROM {schema}.solduri_initiale WHERE cont = %s""", (cont,))
                sold = Decimal(str(cur.fetchone()["si"]))
                cur.execute(f"""SELECT COALESCE(SUM(CASE WHEN l.cont_debit=%s THEN l.suma ELSE 0 END),0) AS d,
                                       COALESCE(SUM(CASE WHEN l.cont_credit=%s THEN l.suma ELSE 0 END),0) AS c
                                FROM {schema}.inregistrari_linii l
                                JOIN {schema}.inregistrari i ON i.id = l.inregistrare_id
                                WHERE i.status = 'validata'""", (cont, cont))
                r = cur.fetchone()
                sold += Decimal(str(r["d"])) - Decimal(str(r["c"]))
                dif = (sold - vcv).quantize(Decimal("0.01"))
                rez.append({"cont": cont, "sold_contabil": str(sold.quantize(Decimal("0.01"))),
                            "valoare_fise_cv": str(vcv.quantize(Decimal("0.01"))),
                            "diferenta": str(dif), "ok": abs(dif) <= Decimal("0.01")})
    return {"conturi": rez, "ok": all(x["ok"] for x in rez),
            "nota": "Diferentele pot veni din note ciorna nevalidate sau operatiuni in afara fiselor CV."}


# --- e-Transport (v1: XML pt upload manual in SPV; API OAuth = etapa 2) ---
@app.post("/tenants/{tenant_id}/etransport-xml")
def etransport_xml(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    import re
    from core import etransport as _e
    from psycopg2.extras import RealDictCursor
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fara acces")
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(f"SELECT cui FROM {schema}.firma_profil WHERE id = 1")
            r = cur.fetchone() or {}
    cui = re.sub(r"\D", "", r.get("cui") or "")
    if not cui:
        raise HTTPException(422, "CUI firma lipsa in Profil firma")
    try:
        xml = _e.xml_notificare(cui, corp)
    except KeyError as e:
        raise HTTPException(422, f"camp lipsa: {e}")
    return {"xml": xml,
            "nota": "XML v2 pt. incarcare manuala in SPV (e-Transport). UIT-ul vine de la ANAF dupa upload."}


# --- OAuth2 ANAF (e-Factura / e-Transport) ---
_ANAF_AUTH = "https://logincert.anaf.ro/anaf-oauth2/v1/authorize"
_ANAF_TOKEN = "https://logincert.anaf.ro/anaf-oauth2/v1/token"

@app.get("/anaf/oauth/start")
def anaf_oauth_start(ctx=Depends(cere_cabinet)):
    import os, urllib.parse
    cid = os.environ.get("ANAF_CLIENT_ID", "")
    ruri = os.environ.get("ANAF_REDIRECT_URI", "")
    if not cid or not ruri:
        raise HTTPException(500, "ANAF_CLIENT_ID/ANAF_REDIRECT_URI lipsesc din api_keys.env")
    q = urllib.parse.urlencode({
        "response_type": "code", "client_id": cid,
        "redirect_uri": ruri, "token_content_type": "jwt",
        "state": str(ctx["firm"]),
    })
    return {"url": f"{_ANAF_AUTH}?{q}",
            "nota": "Deschide link-ul intr-un browser cu certificatul digital instalat."}

@app.get("/efactura/callback")
def anaf_oauth_callback(code: str = "", state: str = "", error: str = ""):
    import os, base64, requests
    from psycopg2.extras import Json
    if error or not code:
        return {"ok": False, "eroare": error or "cod lipsa"}
    cid = os.environ.get("ANAF_CLIENT_ID", "")
    cs = os.environ.get("ANAF_CLIENT_SECRET", "")
    ruri = os.environ.get("ANAF_REDIRECT_URI", "")
    auth = base64.b64encode(f"{cid}:{cs}".encode()).decode()
    r = requests.post(_ANAF_TOKEN, data={
        "grant_type": "authorization_code", "code": code,
        "redirect_uri": ruri, "token_content_type": "jwt",
    }, headers={"Authorization": f"Basic {auth}"}, timeout=30)
    if r.status_code != 200:
        return {"ok": False, "eroare": f"token: HTTP {r.status_code}", "detaliu": r.text[:300]}
    tok = r.json()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""CREATE TABLE IF NOT EXISTS public.anaf_tokens (
                accounting_firm_id integer PRIMARY KEY,
                access_token text, refresh_token text,
                obtinut_la timestamptz NOT NULL DEFAULT now())""")
            cur.execute("""INSERT INTO public.anaf_tokens (accounting_firm_id, access_token, refresh_token)
                           VALUES (%s,%s,%s)
                           ON CONFLICT (accounting_firm_id) DO UPDATE
                           SET access_token=EXCLUDED.access_token,
                               refresh_token=EXCLUDED.refresh_token, obtinut_la=now()""",
                        (int(state or 0), tok.get("access_token"), tok.get("refresh_token")))
        conn.commit()
    return {"ok": True, "mesaj": "Autorizare ANAF reusita. Tokenul a fost salvat; poti inchide fereastra."}

@app.get("/anaf/oauth/stare")
def anaf_oauth_stare(ctx=Depends(cere_cabinet)):
    from psycopg2.extras import RealDictCursor
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""SELECT to_regclass('public.anaf_tokens') AS t""")
            if not cur.fetchone()["t"]:
                return {"autorizat": False}
            cur.execute("SELECT obtinut_la FROM public.anaf_tokens WHERE accounting_firm_id=%s",
                        (ctx["firm"],))
            r = cur.fetchone()
    return {"autorizat": bool(r), "obtinut_la": str(r["obtinut_la"]) if r else None}
