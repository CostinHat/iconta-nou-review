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

from core import nucleu as _nucleu, articole_import_api, retete_import_api, rip_migrare_api
from core.pdf_util import bani, data_ro
from core.common import azi_ro, stare_din_nivel, pastila_firma  # [fus] ziua RO; [verdict] nivel->culoare + escaladare pastila
from core import common as _common
from core import tenant_stergere  # [R72] calea UNICA de scoatere a unei firme
from core import db, auth_api, declaratii_api, tenant_provisioning, facturi_api, clienti_api, salariati_api, coada_api, portal_api, anaf_api, migrare_api, solduri_api, solduri_parteneri_api, salariati_import_api, asociati_import_api, mijloace_fixe_import_api, istoric_declaratii_import_api, control_fiscal_api, termene_api, capacitate_api, tipare_api, produse_api, vector_fiscal_api, firma_profil_api as _fp, factura_pdf as _pdf, observare as _obs, documente_api, declaratii_componente, supervizor
from core import afirmatii as _af  # [P8] afirmatiile despre datele firmei sunt obiecte, nu siruri
from core import cont_valid as _cv  # [R54] contul din corpul cererii se confrunta cu planul firmei
from core.unde import Unde as _Unde  # [P8] domeniul poate fi un OBIECT, nu o perioada
from core.mesaje import (mesaj_din_cod, FARA_CABINET, EMAIL_INVALID, EMAIL_EXISTA,
                         EMAIL_NICIUNUL_VALID, CUI_FIRMA_LIPSA, PERIOADA_INCHISA,
                              MESAJ_Z_DUPLICAT, MESAJ_Z_FARA_CHEIE,
                              MESAJ_CLIENT_ALT_CABINET, MESAJ_EMAIL_ACELASI,
                              MESAJ_DOAR_TITULARUL, MESAJ_LINK_LOGARE_CERUT,
                              MESAJ_EMAIL_TOKEN_INVALID, MESAJ_EMAIL_DE_CONFIRMAT,
                         ROL_INSUFICIENT, DOAR_ADMIN_ICONTA, DOAR_ADMIN_CABINET, DOAR_PATRON,
                         FARA_DREPT_VALIDARE, FARA_DREPT_DEPUNERE, FARA_ACCES_TENANT,
                         COD_FARA_ACCES_TENANT,
                         FARA_ACCES_RAPORTARE, FARA_ACCES)
from core.common import nomenclator_cerut


def _cere_perioada(an=None, luna=None, exercitiu=None, camp_an="an"):
    """Refuza o perioada care nu exista, INAINTE de a cauta date pentru ea.

    [lotul 3, 04.09.2026] Masurat pe sase rute: `luna=13` pe `GET /jurnal` dadea `500`; pe
    `GET /balanta`, pe calea de API si pe `registru-inventar/propunere` dadea `200` cu rezultat
    gol; iar `GET /documente/balanta?luna=0` **genera un PDF** — un document oficial pentru o luna
    care nu exista. Cel mai rau era `balanta`, care adauga si o afirmatie: `"stare":
    "nimic_de_verificat"`. *„Nu exista date pentru luna asta" si „luna asta nu exista" nu sunt
    acelasi lucru, iar a doua nu se repara cautand mai bine.*"""
    if luna is not None and not (1 <= luna <= 12):
        raise HTTPException(422, "luna invalidă: %r (aștept 1-12)" % (luna,))
    if an is not None and not (1990 <= an <= 2100):
        raise HTTPException(422, "%s invalid: %r (aștept 1990-2100)" % (camp_an, an))
    if exercitiu is not None and not (1990 <= exercitiu <= 2100):
        raise HTTPException(422, "exercițiu invalid: %r (aștept 1990-2100)" % (exercitiu,))


def _mesaj_intrare(e):
    """Mesajul unui refuz de intrare, cand exceptia poate fi si `KeyError`.

    [lotul 3, 04.09.2026] `except (ValueError, KeyError) as e: HTTPException(422, str(e))` apare in
    37 de locuri, iar pe ramura `KeyError` `str(e)` e **numele campului intre ghilimele simple**:
    contabilul primea `{"detail": "'brut'"}`. Cod intern ca mesaj — aceeasi clasa scoasa din coada
    in lotul 1, gasita aici pe alta cale. Se traduce o data, in locul comun."""
    if isinstance(e, KeyError):
        return ("Lipsește câmpul `%s` din cererea trimisă. Operațiunea nu se poate consemna fără "
                "el." % (e.args[0] if e.args else "?"))
    return str(e)

# template SQL pentru schema unui tenant nou (generat din tenant_001)
TENANT_TEMPLATE_PATH = os.environ.get(
    "ICONTA_TENANT_TEMPLATE",
    os.path.join(os.path.dirname(__file__), "tenant_template.sql"))
_TENANT_TEMPLATE = None


# ============================================================
#  FAIL-FAST secrete obligatorii la pornire (testabil separat)
# ============================================================
def verifica_secrete_obligatorii(env=None):
    """App-ul REFUZĂ să pornească fără secretele critice. JWT_SECRET absent = tokenuri forjabile
    (default gol pe cheie HMAC = bypass complet de auth). JWT_SECRET acoperă și auth_api.SECRET și
    spv_conector.STATE_SECRET (același env). Vezi DECIZII 22.07. Ridică RuntimeError la absență."""
    env = os.environ if env is None else env
    lipsa = [k for k in ("JWT_SECRET",) if not (env.get(k) or "").strip()]
    if lipsa:
        raise RuntimeError(
            "secrete obligatorii absente din env: %s — app-ul refuză să pornească "
            "(fără ele autentificarea ar fi forjabilă cu cheie goală)" % ", ".join(lipsa))


def verifica_fus_orar(offset_local=None, pg_tz=None):
    """App-ul REFUZĂ să pornească dacă OS TZ SAU PG timezone != Europe/Bucharest. Un fus greșit sare
    ziua pe verdictele de zi (la termen/întârziat, fereastra UIT, cron alerte) SAU creează nepotrivire
    OS<->PG între cele două laturi ale aceluiași verdict. Invariantă de provisionare (ca JWT_SECRET),
    nu presupunere. Vezi DECIZII 22.07. offset_local/pg_tz injectabile pt test."""
    import datetime, zoneinfo
    buc = datetime.datetime.now(zoneinfo.ZoneInfo("Europe/Bucharest")).utcoffset()
    if offset_local is None:
        offset_local = datetime.datetime.now().astimezone().utcoffset()   # fusul PROCESULUI
    if offset_local != buc:
        raise RuntimeError(
            "OS TZ nu e Europe/Bucharest (offset proces %s != %s) — app-ul refuză să pornească "
            "(verdictele de zi ar sări ziua)" % (offset_local, buc))
    if pg_tz is None:
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SHOW timezone")
                pg_tz = cur.fetchone()[0]
    if pg_tz != "Europe/Bucharest":
        raise RuntimeError(
            "PG timezone nu e Europe/Bucharest (%s) — app-ul refuză să pornească "
            "(nepotrivire OS<->PG pe verdictele de zi)" % pg_tz)


# ============================================================
#  LIFECYCLE — pool deschis la pornire, închis la oprire
# ============================================================
@asynccontextmanager
async def lifespan(app):
    global _TENANT_TEMPLATE
    verifica_secrete_obligatorii()   # fail-fast INAINTE de orice: fara JWT_SECRET nu pornim
    from core import versiune as _versiune_boot; _versiune_boot.stampileaza()  # running==HEAD: commitul de pornire (in memorie)
    db.init_pool()
    verifica_fus_orar()   # fail-fast: OS TZ + PG timezone = Europe/Bucharest (invarianta de provisionare)
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


app = FastAPI(title="iConta.eu API", version="2026.1", lifespan=lifespan)

# [log_500_v1] configurare logging o singura data (nu exista basicConfig anterior)
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

@app.exception_handler(Exception)
async def _handler_perioada_blocata(request: Request, exc: Exception):
    from fastapi.responses import JSONResponse as _JR
    msg = str(exc)
    if "PERIOADA_BLOCATA" in msg:
        detaliu = msg.split("PERIOADA_BLOCATA:")[1].split("\n")[0].strip() \
            if "PERIOADA_BLOCATA:" in msg else "perioada este blocata"
        return _JR(status_code=423, content={"detail": f"Perioada {detaliu}."})
    # [log_500_v1] traceback vizibil pt erori necunoscute inainte de re-raise
    logging.getLogger("iconta").exception("Eroare 500 la %s %s", request.method, request.url.path)
    raise exc

# [probare invalid, 03.09.2026] REFUZUL DE VALIDARE, PE ÎNȚELESUL UNUI CONTABIL.
#
# Ce vedea omul până azi, pe un câmp lipsă sau greșit, era răspunsul brut al bibliotecii:
#   {"detail":[{"type":"missing","loc":["body","tenant_id"],"msg":"Field required","input":{}}]}
# Numește câmpul — dar în engleză, în formă de structură, și fără să spună CE să facă. Măsurat pe
# lotul T01: patru din douăzeci și una de probe invalide răspundeau așa.
#
# CE NU SE SCHIMBĂ, deliberat: forma răspunsului rămâne cea pe care ecranul o știe deja citi —
# `detail = {mesaj, erori_campuri:[{camp, mesaj}]}`, contractul din `static/js/api.js`. Deci nu e o
# formă nouă inventată aici, e cea existentă, aplicată și refuzurilor de validare.
from fastapi.exceptions import RequestValidationError as _RVE


def _camp_omenesc(loc):
    """`["body","randuri",0,"an"]` -> `randuri[0].an`. Prefixele tehnice (body/query/path) cad."""
    parti = []
    for x in loc:
        if x in ("body", "query", "path", "header", "cookie"):
            continue
        parti.append("[%d]" % x if isinstance(x, int) else ("." + str(x) if parti else str(x)))
    return "".join(parti) or "corpul cererii"


def _motiv_omenesc(e):
    t = str(e.get("type", ""))
    intrare = e.get("input", None)
    if t == "missing":
        return "lipsește"
    if t.startswith("int_"):
        return "aștept un număr întreg, am primit %r" % (intrare,)
    if t.startswith("float_") or t.startswith("decimal_"):
        return "aștept un număr, am primit %r" % (intrare,)
    if t.startswith("bool_"):
        return "aștept da/nu, am primit %r" % (intrare,)
    if t.startswith("date_") or t.startswith("datetime_"):
        return "aștept o dată (AAAA-LL-ZZ), am primit %r" % (intrare,)
    if t in ("list_type", "dict_type", "model_attributes_type"):
        return "forma trimisă nu e cea așteptată (am primit %r)" % (intrare,)
    if t == "string_type":
        return "aștept text, am primit %r" % (intrare,)
    return "%s (am primit %r)" % (e.get("msg", "valoare invalidă"), intrare)


@app.exception_handler(_RVE)
async def _handler_validare_camp(request: Request, exc: _RVE):
    from fastapi.responses import JSONResponse as _JR
    campuri = []
    for e in exc.errors():
        campuri.append({"camp": _camp_omenesc(e.get("loc", [])), "mesaj": _motiv_omenesc(e)})
    if len(campuri) == 1:
        rezumat = "Cererea nu poate fi acceptată: %s — %s." % (campuri[0]["camp"], campuri[0]["mesaj"])
    else:
        rezumat = ("Cererea nu poate fi acceptată, %d câmpuri: %s."
                   % (len(campuri), "; ".join("%s — %s" % (c["camp"], c["mesaj"]) for c in campuri)))
    return _JR(status_code=422, content={"detail": {"mesaj": rezumat, "erori_campuri": campuri}})


_APP_PORNIT_LA = __import__("time").time()  # ICRD_SANATATE_SERVER_V1 - uptime proces

# frontend: servit static de pe același origin cu API-ul (fără build step)
#
# [R118, 02.09.2026] CE SE SERVEȘTE NU MAI E CE E ÎN LUCRU.
#
# Până azi, `_STATIC_DIR` era chiar arborele de lucru: serviciul rulează cu `WorkingDirectory` acolo,
# deci un `.js` scris pe server era **live în aceeași secundă** — fără commit, fără poartă, fără
# restart. *Poarta verde apără Python-ul, fiindcă procesul îl încarcă la pornire; JS-ul nu trecea
# prin ea deloc.* Instanța, măsurată 01.09: o ghilimea românească închisă cu `"` ASCII în
# `supervizor.js` a oprit **tot desktopul cabinetului** — 15 ecrane —, fiindcă `cabinet.js` importă
# modulul. Pe producție, pe fișierul viu, fără ca nimic să semnaleze.
#
# Acum se servește `../iconta_publicat/static`, scris de `scripts/publica_static.py` (din HEAD, în
# `post-commit`). Publicarea trece prin `node --check` pe fiecare `.js`, deci nici măcar publicarea
# deliberată din arbore nu poate duce la un browser un modul care nu se parsează.
#
# **DE CE RIDICĂ, în loc să cadă înapoi pe arbore.** Un director publicat fără amprentă citibilă e o
# publicare oprită la jumătate. Alternativa la refuz ar fi să servim arborele de lucru — adică exact
# defectul pe care îl reparăm, reapărut tăcut, tocmai când publicarea s-a rupt. *Un implicit minte;
# ăsta ar minți în direcția în care doare.* Remediul e o comandă, și e scris în mesaj.
def _alege_static():
    """`(cale, motiv)` — CE se servește și DE CE. Fără alegere tăcută."""
    import io as _io
    import json as _json
    publicat = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "iconta_publicat", "static")
    if os.path.isdir(publicat):
        amprenta = os.path.join(publicat, ".publicat.json")
        try:
            _a = _json.loads(_io.open(amprenta, encoding="utf-8").read())
        except Exception as _e:
            raise RuntimeError(
                "R118: directorul publicat %s nu are amprentă citibilă (%s). NU se cade înapoi pe "
                "arborele de lucru — aia e chiar clasa reparată. Republică: "
                "./venv/bin/python scripts/publica_static.py" % (publicat, _e))
        return publicat, "publicat (%s%s)" % (
            _a.get("sursa"), " " + str(_a.get("commit"))[:8] if _a.get("commit") else "")
    return os.path.join(os.path.dirname(__file__), "static"), "arbore de lucru (nepublicat)"


_STATIC_DIR, _STATIC_MOTIV = _alege_static()
logging.getLogger("iconta").info("[R118] /static servit din %s — %s", _STATIC_DIR, _STATIC_MOTIV)
if os.path.isdir(_STATIC_DIR):
    # [nocache_static_v1]: browserul revalideaza automat (304), fara ?v= manual
    class _StaticNoCache(StaticFiles):
        def file_response(self, *a, **k):
            r = super().file_response(*a, **k)
            r.headers["Cache-Control"] = "no-cache"
            return r
    app.mount("/static", _StaticNoCache(directory=_STATIC_DIR), name="static")

@app.get("/")
def index():
    cale = os.path.join(_STATIC_DIR, "index.html")
    if os.path.isfile(cale):
        return FileResponse(cale)
    raise HTTPException(404, "frontend neinstalat")


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    # favicon_v1: browserul cere /favicon.ico implicit -> servim SVG-ul (fara 404 in loguri)
    cale = os.path.join(_STATIC_DIR, "favicon.svg")
    if os.path.isfile(cale):
        return FileResponse(cale, media_type="image/svg+xml")
    raise HTTPException(404, "favicon absent")


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
            raise HTTPException(403, ROL_INSUFICIENT)
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
    # [suspendare-live] cabinet suspendat => 403 imediat, nu doar la login
    if ctx["rol"] != "superadmin":
        with db.get_conn() as conn, conn.cursor() as cur:
            cur.execute("""SELECT af.activ, extract(epoch FROM u.sesiuni_valide_de) FROM public.users u
                           LEFT JOIN public.accounting_firms af ON af.id = u.accounting_firm_id
                           WHERE u.id = %s""", (ctx["uid"],))
            r = cur.fetchone()
            if r and r[0] is False:
                raise HTTPException(403, "Cabinetul este suspendat. Contactați furnizorul.")
            # [reset_parola_v1] sesiune emisa INAINTE de o schimbare de parola (iat < sesiuni_valide_de) -> invalidata
            if r and r[1] is not None and ctx.get("iat") is not None and ctx["iat"] < r[1]:
                raise HTTPException(401, "Sesiune încheiată (parola a fost schimbată). Autentifică-te din nou.")
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
                # [R79, 27.08.2026] `tenant_id` trece printr-o SUB-INTEROGARE, nu direct.
                # Instanta: la stergerea unei firme, randul asta se scrie la ~78 ms DUPA ce
                # tranzactia a comis - deci trimitea la o firma care nu mai exista. Fiecare firma
                # scoasa lasa exact un orfan; masurat pe primele doua, 67 -> 69.
                # Sub-interogarea intoarce NULL cand firma nu mai e, in ACELASI statement: nu se
                # adauga niciun drum dus-intors, iar fapta se pastreaza intreaga (cine, cand, ce a
                # cerut) - se pierde doar filtrarea pe o firma care nu mai exista.
                # De ce nu cheie straina cu ON DELETE SET NULL: masurat 27.08 - pe cele 10 tabele cu
                # `tenant_id NOT NULL` ar face stergerea IMPOSIBILA (NotNullViolation), iar pe cele
                # nullable ar RESPINGE randul de dupa stergere, nu l-ar trece pe NULL. Adica linia
                # de audit ar disparea in loc sa ramana orfana. Vezi R79.
                cur.execute(
                    "INSERT INTO public.audit_log (user_id, tenant_id, actiune, detalii) "
                    "VALUES (%s, (SELECT id FROM public.tenants WHERE id = %s), %s, %s)",
                    (uid, tenant_id, actiune, _json_audit.dumps({"status": status})))
    except Exception as _e:
        _obs.esec_secundar("audit_log activitate", _e)  # inghitit, dar nu tacut (27.07.2026)

_METODE_MUTATIE = ("POST", "PUT", "DELETE", "PATCH")


@app.middleware("http")
async def _preview_readonly_guard(request: Request, call_next):
    """[F-preview] Read-only enforcement pe BACKEND: un token de PREVIZUALIZARE portal blocheaza
    orice mutatie (POST/PUT/DELETE/PATCH -> 403); GET permis. La nivel de request (nu ascuns butoane
    in UI - UI-ul se ocoleste). Tokenul preview e emis de /tenants/{id}/acces-portal, marcat preview=True."""
    if request.method in _METODE_MUTATIE:
        auth = request.headers.get("authorization")
        if auth and auth.startswith("Bearer "):
            try:
                ctx = auth_api.context_din_token(auth[7:])
            except Exception:
                ctx = None
            if ctx and ctx.get("ok") and ctx.get("preview"):
                from fastapi.responses import JSONResponse
                return JSONResponse(status_code=403, content={
                    "detail": "Previzualizare — doar vizualizare. Acțiunile sunt dezactivate în modul preview."})
    return await call_next(request)


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

@app.middleware("http")
async def _edge_canonic_head(request: Request, call_next):
    # [www_canonic 15.08.2026] www.iconta.eu servea acelasi continut ca iconta.eu (200 pe ambele) -> duplicat SEO,
    # semnalul se imparte. Forma canonica = fara www (_GHID_BAZA, pe care se genereaza sitemap+canonical).
    # Redirect 301 PERMANENT, PASTREAZA calea+query (www.../ghid/x -> iconta.eu/ghid/x, nu radacina). In app,
    # nu in nginx (nginx trece Host $host la upstream, deci hostul ajunge aici; nginx-ul e sub sudo, prod).
    _canonic = _GHID_BAZA.split("://")[-1]              # "iconta.eu"
    host = (request.headers.get("host") or "").split(":")[0].lower()
    if host == "www." + _canonic:
        from fastapi.responses import RedirectResponse
        q = ("?" + request.url.query) if request.url.query else ""
        return RedirectResponse(_GHID_BAZA + request.url.path + q, status_code=301)
    # [head_ca_get 15.08.2026] FastAPI NU adauga HEAD la rutele GET -> 405. Googlebot foloseste HEAD ca sa verifice
    # daca pagina s-a schimbat inainte de a o descarca; 405 iroseste buget de crawl. Tratam HEAD ca GET la rutare;
    # uvicorn suprima corpul pe fir pentru cererea HEAD (raspunde doar cu headerele, inclusiv Content-Length).
    if request.method == "HEAD":
        request.scope["method"] = "GET"
        return await call_next(request)
    return await call_next(request)


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
    except Exception as _e:
        _obs.esec_secundar("metrici sanatate: citire", _e)  # inghitit, dar nu tacut (27.07.2026)
    return rezultat

def _email_superadmin():
    try:
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT email FROM public.users WHERE rol='superadmin' AND activ=true ORDER BY id LIMIT 1")
                r = cur.fetchone()
        return r[0] if r else None
    except Exception as _e:
        _obs.esec_secundar("email superadmin", _e)  # inghitit, dar nu tacut (27.07.2026)
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
    alerte = []
    if m["ram_procent"] is not None and m["ram_procent"] >= _PRAG_RAM_PROCENT and _poate_alerta("ram"):
        alerte.append(f"RAM folosita: {m['ram_procent']}% (prag {_PRAG_RAM_PROCENT}%)")
    if m["disc_procent"] is not None and m["disc_procent"] >= _PRAG_DISC_PROCENT and _poate_alerta("disc"):
        alerte.append(f"Disc folosit: {m['disc_procent']}% (prag {_PRAG_DISC_PROCENT}%)")
    if m["load1"] is not None and m["load1"] >= 0.7 * m["cpu_count"] and _poate_alerta("load"):
        alerte.append(f"Load average: {round(m['load1'], 2)} (prag {round(0.7 * m['cpu_count'], 2)})")
    if m["conexiuni_db"] is not None and m["conexiuni_db"] >= _PRAG_CONEXIUNI_DB and _poate_alerta("conexiuni_db"):
        alerte.append(f"Conexiuni DB active: {m['conexiuni_db']} (prag {_PRAG_CONEXIUNI_DB})")
    if m["erori_noi"] and m["erori_noi"] > 0 and _poate_alerta("erori"):
        alerte.append(f"{m['erori_noi']} eroare/erori server (500+) in ultimele 10 minute")
    # ICRD_ISTORIC_SANATATE_V1 - salveaza instantaneu pentru grafice
    try:
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO public.metrici_sanatate "
                    "(ram_procent, disc_procent, load1, conexiuni_db, erori_noi) "
                    "VALUES (%s,%s,%s,%s,%s)",
                    (m["ram_procent"], m["disc_procent"], m["load1"], m["conexiuni_db"], m["erori_noi"]))
    except Exception as _e:
        _obs.esec_secundar("metrici sanatate: scriere", _e)  # inghitit, dar nu tacut (27.07.2026)

    if not alerte:
        return
    email = _email_superadmin()
    if not email:
        return
    html = ("<div style='font-family:sans-serif;font-size:15px;color:#111'>"
            "<p>Alerta sanatate server iConta.eu:</p><ul>" +
            "".join("<li>" + p + "</li>" for p in alerte) +
            "</ul><p>Verifica panoul 'Sanatate server' din Admin iConta.</p></div>")
    _obs.trimite_email_html(email, "Alerta iConta.eu - sanatate server", html)

async def _bucla_alerte_sanatate():
    import asyncio as _asyncio
    while True:
        try:
            await _run_in_threadpool_audit(_verifica_si_alerta)
        except Exception:
            pass
        await _asyncio.sleep(300)

@app.post("/admin/sanatate/test-alerta")
def admin_sanatate_test_alerta(ctx=Depends(cere_cabinet)):
    if ctx["rol"] != "superadmin":
        raise HTTPException(403, DOAR_ADMIN_ICONTA)
    email = _email_superadmin()
    if not email:
        raise HTTPException(500, "email superadmin negăsit")
    r = _obs.trimite_email_html(email, "TEST Alerta iConta.eu - sanatate server",
        "<p>Test manual alerta sanatate. Daca ai primit acest email, livrarea functioneaza.</p>")
    return {"trimis_catre": email, "rezultat": str(r)}

@app.get("/admin/sanatate/istoric")
def admin_sanatate_istoric(ore: int = 24, ctx=Depends(cere_cabinet)):
    if ctx["rol"] != "superadmin":
        raise HTTPException(403, DOAR_ADMIN_ICONTA)
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
        raise HTTPException(403, DOAR_ADMIN_ICONTA)
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
    except Exception as _e:
        _obs.esec_secundar("admin sanatate: info DB", _e)  # inghitit, dar nu tacut (27.07.2026)

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
    except Exception as _e:
        _obs.esec_secundar("admin sanatate: erori 24h", _e)  # inghitit, dar nu tacut (27.07.2026)

    return {
        "server": {"load1": load1, "load5": load5, "load15": load15, "ram": ram, "disc": disc},
        "aplicatie": {"uptime_secunde": uptime_sec},
        "baza_date": db_info,
        "erori_24h": erori_24h,
        "erori_lista": lista_erori,
    }

# === ANUNTURI CABINET === # anunturi_v1
class AnuntIn(BaseModel):
    mesaj: str
    cabinet_id: Optional[int] = None  # None = toate cabinetele
    data_afisare: Optional[str] = None  # [F103] None = imediat
    segment: Optional[str] = None
    cabinet_ids: Optional[list] = None
    tenant_ids: Optional[list] = None

@app.post("/admin/anunturi")
def admin_anunt_creeaza(date: AnuntIn, ctx=Depends(cere_rol("superadmin"))):
    if not (date.mesaj or "").strip():
        raise HTTPException(422, "mesaj gol")
    mesaj = date.mesaj.strip()
    data_af = (date.data_afisare or "").strip() or None
    n = 0
    with db.get_conn() as conn, conn.cursor() as cur:
        if date.cabinet_ids:  # [anunturi_alese_v1] cabinete alese cu bife
            for cid in date.cabinet_ids:
                cur.execute("INSERT INTO public.anunturi_cabinet (cabinet_id, mesaj, data_afisare) VALUES (%s,%s,%s)", (int(cid), mesaj, data_af))
                n += 1
        elif date.cabinet_id:
            cur.execute("INSERT INTO public.anunturi_cabinet (cabinet_id, mesaj, data_afisare) VALUES (%s,%s,%s)", (date.cabinet_id, mesaj, data_af))
            n = 1
        else:
            cur.execute("SELECT id FROM public.accounting_firms WHERE activ")
            for (cid,) in cur.fetchall():
                cur.execute("INSERT INTO public.anunturi_cabinet (cabinet_id, mesaj, data_afisare) VALUES (%s,%s,%s)", (cid, mesaj, data_af))
                n += 1
        conn.commit()
    return {"ok": True, "trimise": n}

@app.get("/admin/alerte-fiscale")  # [F103 partea 2] propunerile monitorului pentru anunturi
def admin_alerte_fiscale(ctx=Depends(cere_rol("superadmin"))):
    with db.get_conn() as conn, conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
        cur.execute("""SELECT id, sursa, titlu, rezumat, url, relevanta, creat_la
                       FROM public.alerte_fiscale WHERE NOT vazut AND sursa != 'anaf_buletin' ORDER BY id DESC LIMIT 30""")
        rows = [dict(r) for r in cur.fetchall()]
    for r in rows:
        r["creat_la"] = str(r["creat_la"])
    return {"alerte": rows}
@app.post("/admin/alerte-fiscale/{aid}/tratat")  # [F103 partea 2]
def admin_alerta_tratata(aid: int, ctx=Depends(cere_rol("superadmin"))):
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("UPDATE public.alerte_fiscale SET vazut=true WHERE id=%s RETURNING id", (aid,))
        r = cur.fetchone()
        conn.commit()
    if not r:
        raise HTTPException(404, "alertă inexistentă")
    return {"ok": True}
@app.get("/eu/anunturi")
def eu_anunturi(ctx=Depends(cere_cabinet)):
    from psycopg2.extras import RealDictCursor
    with db.get_conn() as conn, conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
        cur.execute("""SELECT id, mesaj, creat_la FROM public.anunturi_cabinet
                       WHERE cabinet_id=%s AND confirmat_la IS NULL AND (data_afisare IS NULL OR data_afisare <= CURRENT_DATE) ORDER BY id""", (ctx.get("firm"),))
        rows = [dict(r) for r in cur.fetchall()]
    for r in rows:
        r["creat_la"] = str(r["creat_la"])
    return {"anunturi": rows}

@app.post("/eu/anunturi/{aid}/confirma")
def eu_anunt_confirma(aid: int, ctx=Depends(cere_cabinet)):
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("""UPDATE public.anunturi_cabinet SET confirmat_la=now()
                       WHERE id=%s AND cabinet_id=%s AND confirmat_la IS NULL RETURNING id""", (aid, ctx.get("firm")))
        r = cur.fetchone()
        conn.commit()
    if not r:
        raise HTTPException(404, "anunt inexistent")
    return {"ok": True}

@app.get("/admin/activitate/cabinete")
def admin_activitate_cabinete(ctx=Depends(cere_cabinet)):
    if ctx["rol"] != "superadmin":
        raise HTTPException(403, DOAR_ADMIN_ICONTA)
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
        raise HTTPException(403, DOAR_ADMIN_ICONTA)
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE public.accounting_firms SET activ=false WHERE id=%s", (firm_id,))
    return {"ok": True}

@app.post("/admin/cabinete/{firm_id}/reactiveaza")
def admin_cabinet_reactiveaza(firm_id: int, ctx=Depends(cere_cabinet)):
    if ctx["rol"] != "superadmin":
        raise HTTPException(403, DOAR_ADMIN_ICONTA)
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE public.accounting_firms SET activ=true WHERE id=%s", (firm_id,))
    return {"ok": True}

@app.get("/admin/activitate/cabinet/{firm_id}")
def admin_activitate_cabinet(firm_id: int, limita: int = 200, ctx=Depends(cere_cabinet)):
    if ctx["rol"] != "superadmin":
        raise HTTPException(403, DOAR_ADMIN_ICONTA)
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


class StergereCabinetIn(BaseModel):
    confirmare: str


class CerereStergereIn(BaseModel):  # [F200b] cabinetul DEPUNE o cerere; NU executa
    confirmare_nume: str
    motiv: Optional[str] = None


@app.post("/gdpr/sterge-cabinet/{cabinet_id}/previzualizare")  # [F200] GDPR art.17 pas 1 (superadmin)
def gdpr_sterge_previzualizare(cabinet_id: int, ctx=Depends(cere_rol("superadmin"))):
    from core import gdpr_sterge as _gs
    with db.get_conn() as conn:
        try:
            return _gs.previzualizare(conn, cabinet_id)
        except ValueError as e:
            raise HTTPException(404, str(e))


@app.post("/gdpr/sterge-cabinet/{cabinet_id}/executa")  # [F200] GDPR art.17 pas 2 (superadmin, confirmare typed-back)
def gdpr_sterge_executa(cabinet_id: int, date: StergereCabinetIn, ctx=Depends(cere_rol("superadmin"))):
    from core import gdpr_sterge as _gs
    with db.get_conn() as conn:
        try:
            return _gs.executa(conn, cabinet_id, date.confirmare, ctx.get("uid"))
        except ValueError as e:
            raise HTTPException(422, str(e))


@app.get("/gdpr/export-cabinet")  # [F199] GDPR art.20 portabilitate — export complet cabinet
def gdpr_export_cabinet(cabinet_id: Optional[int] = None, ctx=Depends(cere_rol("admin_firma"))):
    from core import gdpr_export as _ge
    if ctx["rol"] == "superadmin":
        cab = cabinet_id
        if not cab:
            raise HTTPException(422, "Alegeți cabinetul (obligatoriu pentru superadmin).")
    else:
        cab = ctx.get("firm")
    if not cab:
        raise HTTPException(400, FARA_CABINET)
    with db.get_conn() as conn:
        _zip = _ge.export_cabinet(conn, cab)
        try:  # [F199] jurnalizare export (cine/cand, FARA continut)
            with conn.cursor() as _cur:
                _cur.execute(
                    "INSERT INTO public.audit_log (user_id, actiune, entitate, entitate_id, detalii) "
                    "VALUES (%s,'gdpr_export',%s,%s,%s)",
                    (ctx.get("uid"), "cabinet", cab, _json_audit.dumps({"octeti": len(_zip)})))
            conn.commit()
        except Exception as _e:
            _obs.esec_secundar("audit_log export GDPR", _e, alerta=True)  # inghitit, dar nu tacut (27.07.2026)
    return Response(content=_zip, media_type="application/zip",
                    headers={"Content-Disposition": 'attachment; filename="gdpr-export-cabinet-%s.zip"' % cab})


@app.post("/gdpr/cerere-stergere")  # [F200b] GDPR art.17 — cabinetul DEPUNE o cerere; superadmin executa. NU sterge nimic.
def gdpr_cerere_stergere(date: CerereStergereIn, ctx=Depends(cere_rol("admin_firma"))):
    from core import gdpr_cerere as _gc
    cab = ctx.get("firm")
    if not cab:
        raise HTTPException(400, FARA_CABINET)
    with db.get_conn() as conn:
        try:
            r = _gc.depune_cerere(conn, cab, ctx.get("uid"), date.confirmare_nume, date.motiv)
            conn.commit()
            return r
        except ValueError as e:
            raise HTTPException(422, str(e))


@app.get("/capacitate")  # [p70_capacitate] panou capacitate (doar patron)
def capacitate_panou(ctx=Depends(cere_rol("admin_firma"))):
    cab = ctx.get("firm")
    if not cab:
        raise HTTPException(400, FARA_CABINET)
    with db.get_conn() as conn:
        return capacitate_api.capacitate(conn, cab)

@app.get("/tipare")  # [p72_tipare] educatie pe tipare (doar patron)
def tipare_panou(ctx=Depends(cere_rol("admin_firma"))):
    cab = ctx.get("firm")
    if not cab:
        raise HTTPException(400, FARA_CABINET)
    with db.get_conn() as conn:
        return tipare_api.tipare(conn, cab)


@app.get("/tipare/ai")  # [F120] analiza generativa AI peste tiparele de respingere (doar patron)
def tipare_ai_panou(ctx=Depends(cere_rol("admin_firma"))):
    cab = ctx.get("firm")
    if not cab:
        raise HTTPException(400, FARA_CABINET)
    with db.get_conn() as conn:
        return tipare_api.analiza_ai(conn, cab)


# ============================================================
#  MODELE intrare
# ============================================================
class LoginIn(BaseModel):
    email: str
    parola: str
    cod_acces: Optional[str] = None  # [beta_gate_v1] poarta beta

class RegisterIn(BaseModel):
    email: str
    parola: str
    nume_cabinet: str
    nume: Optional[str] = None
    prenume: Optional[str] = None
    cui: Optional[str] = None  # register_primul_tenant_v1
    accept_termeni: bool = False  # [termeni_v1] bifa obligatorie, validata pe BACKEND

class DeclaratieIn(BaseModel):
    tenant_id: int
    an: int
    luna: Optional[int] = None
    trim: Optional[int] = None
    cota: Optional[float] = None
    manual: Optional[dict] = None
    date_extra: Optional[dict] = None
    ca_an_precedent_eur: Optional[float] = None
    obligatii: Optional[list] = None   # [formular_manual_d710] corectiile D710 (direct in body, nu DB)

class TenantNou(BaseModel):
    nume: str
    cui: Optional[str] = None
    tip_firma: str = "srl"  # [tip_firma_v1] srl (partida dubla) / pfa (partida simpla)

class TenantEdit(BaseModel):
    nume: Optional[str] = None
    cui: Optional[str] = None

class LinieIn(BaseModel):
    descriere: str
    cantitate: float
    pret_unitar: float
    cota_tva: Optional[float] = None   # None -> potrivire automata / eroare la lipsa (fara valoare implicita)
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
    tert_tara: str = "RO"                       # [B1 D300] cod ISO 2 litere partener (IC/export)
    tip_operatiune: str = "normal"             # [B1 D300] normal|avans|regularizare_avans
    furnizor_tva_incasare: bool = False        # [B1 D300] doar pe primite (deducere amanata)

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
    tichet_masa_valoare: Optional[float] = None  # [F133]
    iban: Optional[str] = None  # [F134] cont beneficiar pt plata pe card

class SalariatEdit(BaseModel):
    nume: Optional[str] = None
    prenume: Optional[str] = None
    cnp: Optional[str] = None
    data_angajare: Optional[str] = None
    # [R51] Lipsea, iar ecranul o trimitea: pydantic o ignora TACIT si ruta raspundea 200.
    # Backendul o sustine pe tot restul drumului (_CAMPURI_API, validare, „in serviciu").
    data_incetare: Optional[str] = None
    tip_norma: Optional[str] = None
    ore_zi: Optional[float] = None
    salariu_brut: Optional[float] = None
    valabil_din: Optional[str] = None  # [salariu_edit] data efectiva a schimbarii de salariu (implicit azi)
    persoane_intretinere: Optional[int] = None
    judet_casa: Optional[str] = None
    activ: Optional[bool] = None
    scutit_contrib_minim: Optional[bool] = None
    motiv_exceptare: Optional[int] = None
    cor: Optional[str] = None
    tichet_masa_valoare: Optional[float] = None  # [F133]
    iban: Optional[str] = None  # [F134] cont beneficiar pt plata pe card

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
    regim_fiscal: Optional[str] = None  # [regim] partida simpla -> NULL valid; Optional doar ca sa nu pice la boundary
    platitor_tva: Optional[bool] = None  # obligatoriu (ca operatiuni_ic) -> None respins in salveaza cu TVA_LIPSA, fara default tacit False. Vezi DECIZII 23.07.
    tip_decont: Optional[str] = None
    operatiuni_ic: Optional[bool] = None   # obligatoriu la migrare (ca tip_decont) -> None respins in salveaza, fara default tacit
    inreg_art317: Optional[bool] = False   # [art.317] inregistrare speciala scopuri TVA (art. 317 CF)
    tva_data_inceput: Optional[str] = None   # [tva_inceput] data inreg. in scopuri de TVA (ISO 'YYYY-MM-DD'); ceruta contabilului cand ANAF n-o are

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
    articol_id: Optional[int] = None  # [punte_stoc_v1] F172: leaga linia de stoc (CV); None = serviciu

class EmitereIn(BaseModel):
    tip: str = "factura"  # factura|proforma|aviz
    linii: List[LinieEmitereIn]
    tert_nume: Optional[str] = None
    tert_cui: Optional[str] = None
    tert_adresa: Optional[str] = None
    client_id: Optional[int] = None
    data_emitere: Optional[str] = None
    data_scadenta: Optional[str] = None
    moneda: str = "RON"
    curs_manual: Optional[float] = None
    data_curs_manual: Optional[str] = None  # [R130] data la care cursul manual a fost comunicat
    pleaca_marfa: Optional[bool] = None  # [punte_stoc_v1] F172 poarta: DA descarca gestiunea, NU doar fiscal
    tert_tara: str = "RO"               # [B1 D300] cod ISO 2 litere partener (emise IC/export)
    tip_operatiune: str = "normal"      # [B1 D300] normal|avans|regularizare_avans (avans exigibil la emitere)

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
    tip_norma: str = ""     # [Q11] fara default tacit (DS cap.17): necunoscut ramane necunoscut, semnalat
    ore_zi: float = 0
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
    cont_imobilizare: str = ""   # [Q13] fara default tacit 2131 (extrage lasa gol intentionat, DS cap.17); gol = neclasificat -> lit.c
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
    motiv_trecere: Optional[str] = None  # trecerea EXPLICITA peste un verdict care nu e `valid`

class RespingeIn(BaseModel):
    motiv: str

class DepuneIn(BaseModel):
    motiv_trecere: Optional[str] = None  # [R41] trecere explicită peste verdict lipsă/stătut/cu erori
    spv_index: Optional[str] = None
    # [supervizor, 02.09.2026] Confirmările constatărilor CERTE de pe firma și perioada care se
    # depune: `[{amprenta, motiv}]`. Amprenta leagă confirmarea de o nepotrivire ANUME — o cifră
    # schimbată o invalidează, o reformulare nu.
    confirmari: Optional[list] = None


# ============================================================
#  AUTH
# ============================================================
_EMAIL_RE = _re_audit.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")  # [email_valid_v1]
_login_fail = {}  # [login_lockout_v1] esecuri per CONT (email); per-IP e la nginx (iconta_auth 5r/m)
def _login_blocat(email):
    import time as _t
    q = [t for t in _login_fail.get(email, []) if _t.time() - t < 900]
    _login_fail[email] = q
    return len(q) >= 5
def _login_esec(email):
    import time as _t
    _login_fail.setdefault(email, []).append(_t.time())
def _login_reset(email):
    _login_fail.pop(email, None)

@app.post("/auth/login")
def login(date: LoginIn):
    _email = (date.email or "").strip().lower()
    if _login_blocat(_email):  # [login_lockout_v1] 5 esecuri / 15 min per cont
        raise HTTPException(429, "Prea multe încercări eșuate pentru acest cont. Încearcă din nou peste câteva minute.")
    with db.get_conn() as conn:
        r = auth_api.login(conn, date.email, date.parola)
    if not r["ok"]:
        _login_esec(_email)
        raise HTTPException(401, r["mesaj"])
    _login_reset(_email)
    # [beta_gate_v1 SCOS 14.08] poarta "Site in lucru" eliminata - acces liber (decizie Costin).
    try:
        with db.get_conn() as conn2:
            with conn2.cursor() as cur:
                cur.execute(
                    "INSERT INTO public.audit_log (user_id, actiune) VALUES (%s,'login')",
                    (r["user"]["id"],))
    except Exception as _e:
        _obs.esec_secundar("audit_log login", _e)  # inghitit, dar nu tacut (27.07.2026)
    return {"token": r["token"], "user": r["user"]}


@app.post("/auth/register")
def register(date: RegisterIn):
    if not date.accept_termeni:  # [termeni_v1] fara bifa -> contul NU se creeaza (gard pe backend, nu doar JS)
        raise HTTPException(400, "Trebuie să accepți Termenii și condițiile pentru a crea contul.")
    if not _nucleu.parola_ok(date.parola):  # [parola_min_v1] aceeasi cerinta ca activare/reset/schimbare
        raise HTTPException(400, _nucleu.PAROLA_MESAJ)
    if not _EMAIL_RE.match((date.email or "").strip()):  # [email_valid_v1] email obligatoriu + format valid
        raise HTTPException(400, EMAIL_INVALID)
    with db.get_conn() as conn:
        r = auth_api.inregistreaza_cabinet(
            conn, date.email, date.parola, date.nume_cabinet,
            nume=date.nume, prenume=date.prenume)
    if not r["ok"]:
        raise HTTPException(400, r["mesaj"])
    try:  # [termeni_v1] dovada de consimtamant: cine, cand, ce versiune (linia 3 din fisier)
        with db.get_conn() as conn, conn.cursor() as cur:
            cur.execute("INSERT INTO public.acord_termeni (user_id, cabinet_id, email, versiune) "
                        "VALUES (%s,%s,%s,%s)",
                        (r.get("user_id"), r.get("firm_id"), date.email.strip().lower(),
                         _termeni_versiune(open(_TERMENI_PATH, encoding="utf-8").read())))
            conn.commit()
    except Exception as _e:
        print("[termeni] acord neinregistrat pentru %s: %s" % (date.email, _e))
    try:  # register_email_v1: email de bun venit
        html = ("<p>Buna,</p><p>Contul cabinetului <b>%s</b> a fost creat pe iConta.eu.</p>"
                "<p>Te poti loga oricand cu emailul <b>%s</b> la <a href='https://iconta.eu'>iconta.eu</a>.</p>"
                "<p>Firma proprie a cabinetului este deja adaugata in portofoliu.</p>") % (date.nume_cabinet, date.email)
        _obs.trimite_email_html(date.email, "Bine ai venit pe iConta.eu", html)
    except Exception as _e:
        # [R73] fara alerta: bun venit nu e cale de ACCES, doar politete
        _obs.esec_secundar("email bun venit cabinet", _e)
    try:  # [alerta_cont_nou_v1] notificare interna la fiecare cont nou de cabinet (fara date personale)
        from datetime import datetime as _dt
        from zoneinfo import ZoneInfo as _Z
        _acum = _dt.now(_Z("Europe/Bucharest")).strftime("%Y-%m-%d %H:%M:%S")
        _mesaj_cn = ("S-a inregistrat un cont nou de cabinet pe iConta.eu la %s (ora Romaniei). "
                     "Alerta nu contine date personale." % _acum)
        if _obs.trebuie_trimisa("cont_nou_cabinet"):  # [alerta_dedup_v1] throttle anti-flood (implicit 15 min)
            _ok_cn = _obs._trimite_brevo("Cont nou de cabinet", _mesaj_cn)
            print("[alerta_cont_nou] trimisa=%s | %s" % (_ok_cn, _mesaj_cn), flush=True)
        else:
            print("[alerta_cont_nou] throttled (dedup) | %s" % _mesaj_cn, flush=True)
    except Exception as _e:
        print("[alerta_cont_nou] netrimisa: %s" % _e, flush=True)
    # [register_firma_v2 27.07.2026] Provisionarea primei firme poate esua (ANAF jos, schema
    # incompleta, DB). Inainte, esecul era INGHITIT si raspunsul spunea SUCCES - userul ramanea
    # cu cont valid si FARA firma, fara sa stie. Contul NU se anuleaza (e valid si util), dar
    # raspunsul poarta adevarul, iar ecranul il arata.
    _firma_ok = None                       # None = nu s-a incercat (fara CUI la inregistrare)
    _firma_motiv = ""
    if date.cui and _TENANT_TEMPLATE:  # register_primul_tenant_v1: entitatea proprie = prima firma
        _firma_ok = False
        try:
            with db.get_conn() as conn:
                _cui = date.cui.replace("RO", "").strip()
                _t = tenant_provisioning.provision_tenant(
                    conn, date.nume_cabinet, _cui,
                    r["firm_id"], r["user_id"], _TENANT_TEMPLATE)
                # [register_cabinet_cui_v1] CUI-ul a trecut cifra de control in provision_tenant
                # -> descrie entitatea proprie a cabinetului. Se persista SI pe accounting_firms.cui
                # (nu doar pe firma-tenant): altfel get_cabinet il citeste NULL si ecranul Setari
                # cabinet ramane gol desi userul l-a tastat si verificat la ANAF la inregistrare.
                auth_api.actualizeaza_cabinet(conn, r["firm_id"], cui=_cui)
                # [register_profil_anaf_v1] Datele de la ANAF se SALVEAZA in profil, nu
                # doar se afiseaza pe ecran la inregistrare. Fara ele firma noua se naste
                # cu caen gol si platitor_tva necunoscut -> D394 blocat (caen e obligatoriu),
                # iar TVA-ul ramane pe valoarea din template in loc de realitate.
                # Acelasi tipar ca [gratuit_tva_anaf_v1] la contul gratuit (DS: aceeasi
                # situatie = aceeasi rezolvare), extins la toate campurile pe care ANAF
                # le da: denumire, cod_caen, adresa, platitor_tva.
                try:
                    # [register_profil_anaf_v2] SURSA UNICA de precompletare ANAF
                    # (tenant_provisioning.precompleteaza_din_anaf), aceeasi ca la add-firm/import.
                    # seteaza_nume=True: firma proprie preia si denumirea de la ANAF.
                    if _t and _t.get("schema_name"):
                        tenant_provisioning.precompleteaza_din_anaf(conn, _t["schema_name"], _cui, seteaza_nume=True)
                except Exception as _e:
                    # ANAF jos -> profilul ramane de completat manual. Firma EXISTA, doar
                    # datele preluate lipsesc - deci NU e esec de provisionare.
                    _obs.esec_secundar("precompletare ANAF la register", _e)
                conn.commit()
                _firma_ok = True
        except Exception as _e:
            # Contul RAMANE valid: userul se poate loga si adauga firma manual din ecranul
            # Firme. Dar raspunsul NU mai minte cu succes - vezi register_firma_v2 mai sus.
            # [register_motiv_real_v1] Raspunsul poarta MOTIVUL real, nu un generic. Modelul e mesajul
            # de la numerotarea facturilor ("nu putem presupune numarul 1") - spune DE CE. Contul + cabinetul
            # SUNT create si userul e logat automat -> mesajul il indruma spre ecranul Firme, nu "te poti loga".
            _obs.esec_secundar("provisionare tenant la register", _e, alerta=True)
            _txt = str(_e).lower()
            _cui_afis = (date.cui or "").strip()
            if "cifra de control" in _txt or "cui invalid" in _txt:
                _motiv = ("CUI-ul introdus (%s) nu este valid \u2014 cifra de control nu corespunde. "
                          "Verific\u0103 cifrele (f\u0103r\u0103 spa\u021bii sau litere)." % _cui_afis)
            elif "exist" in _txt and "deja" in _txt:
                _motiv = "exist\u0103 deja o firm\u0103 cu acest CUI \u00een portofoliul cabinetului."
            else:
                _motiv = "a ap\u0103rut o eroare tehnic\u0103 la ad\u0103ugarea firmei."
            _firma_motiv = ("Contul \u0219i cabinetul au fost create. Firma proprie NU a putut fi ad\u0103ugat\u0103 "
                            "automat: %s O po\u021bi ad\u0103uga oric\u00e2nd din ecranul Firme." % _motiv)
    raspuns = {"user_id": r["user_id"], "firm_id": r["firm_id"]}
    if _firma_ok is not None:
        raspuns["firma_creata"] = _firma_ok
        if _firma_motiv:
            raspuns["avertisment"] = _firma_motiv
    return raspuns


# ============================================================
#  TENANȚI — firmele la care userul are acces
# ============================================================
@app.get("/tenants")
def tenants(inactive: bool = False, ctx=Depends(cere_cabinet)):
    """`inactive=true` cuprinde ȘI firmele dezactivate — altfel o firmă dezactivată ar ieși din
    listă fără nicio cale de întoarcere. [R72]"""
    with db.get_conn() as conn:
        return {"tenants": auth_api.tenantii_userului(conn, ctx["uid"], doar_active=not inactive)}


@app.get("/firme-scoase")
def firme_scoase(ctx=Depends(cere_cabinet)):
    """[R72] Urma firmelor scoase din portofoliu — CITITĂ, nu doar scrisă.

    Fără ruta asta, `public.firme_scoase` ar fi a doua instanță, în aceeași zi, a clasei
    declarate dimineață la `urme-portal`: *scrisă, necitită de om*. După o ștergere, ea e
    singura dovadă că firma a existat.
    """
    with db.get_conn() as conn, conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
        cur.execute(
            "SELECT id, tenant_id, nume, cui, schema_name, motiv, randuri_sterse, "
            "       urme_pastrate, scos_de_user_id, scos_la, "
            "       (SELECT u.email FROM public.users u WHERE u.id = fs.scos_de_user_id) AS scos_de "
            "FROM public.firme_scoase fs WHERE cabinet_id = %s "
            "ORDER BY scos_la DESC LIMIT 200", (ctx["firm"],))
        return {"firme": [dict(r) for r in cur.fetchall()]}


@app.get("/tenants/{tenant_id}/scoatere")
def tenant_scoatere_previzualizare(tenant_id: int, ctx=Depends(cere_cabinet)):
    """[R72] Ce se întâmplă dacă firma se scoate: are evidență sau nu, și ce anume s-a găsit.
    Se citește ÎNAINTE de apăsare — un refuz care apare abia după apăsare e o surpriză."""
    with db.get_conn() as conn:
        if not auth_api.schema_tenant(conn, ctx["uid"], tenant_id):
            raise HTTPException(404, "tenant inexistent sau fără acces")
        return tenant_stergere.previzualizare(conn, tenant_id)


class FirmaActivareIn(BaseModel):
    activ: bool


def _acces_pentru_activare(conn, rol, firm, tenant_id):
    """[R83/JJ1, 28.08.2026] Poarta rutei de ACTIVARE — scrisă **local**, nu în funcția comună.

    DE CE EXISTĂ. `auth_api.schema_tenant` cere `activ = true` pe **toate trei** ramurile de rol.
    E corect pentru orice rută care lucrează *în* firmă — o firmă scoasă din portofoliul de lucru
    n-are de ce să răspundă la cereri de conținut. Dar ruta de activare e **singura** al cărei act
    are sens tocmai pe o firmă **inactivă**: reactivarea. Cu poarta comună, ea răspundea 404
    întotdeauna, deci **reactivarea nu se putea face niciodată** (R83, probat pe 28.08.2026).

    DE CE AICI ȘI NU ÎN `schema_tenant`. Decizia lui Costin — varianta **(a)**: *„restul rutelor
    rămân neatinse — nicio semnătură comună nu se schimbă, izolarea rămâne exact cum era."*
    Un parametru `si_inactive=` pe funcția comună ar fi reparat clasa, dar ar fi atins o semnătură
    folosită în **154** de rute, fiecare cu propriul risc *(numărate pe AST înainte de reparație;
    după ea sunt 153 — ruta asta a ieșit din mulțime)*. Excepția e locală, deci și riscul e.

    CE PĂSTREAZĂ NEATINS: **regula de rol**, identică cu a funcției comune —
      * `superadmin` ajunge doar la firme **fără cabinet** (GDPR: nu vede conținutul clienților);
      * oricine altcineva ajunge doar la firmele **cabinetului lui**.
    Singura diferență față de `schema_tenant` e `activ`, și e diferența cerută.

    CE NU FACE: nu întoarce schema și nu dă acces la **conținut**. Întoarce un `bool` — dreptul de a
    comuta un rând din `public.tenants`. Cine vrea conținutul firmei trece tot prin poarta comună.

    Refuzul e **același mesaj** ca al porții comune, deliberat: „inexistent" și „fără acces" nu se
    despart, ca să nu se poată afla din afară ce firme există.
    """
    with conn.cursor() as cur:
        cur.execute("SELECT accounting_firm_id FROM public.tenants WHERE id = %s", (tenant_id,))
        r = cur.fetchone()
    if not r:
        return False
    cabinet = r[0]
    if rol == "superadmin":
        return cabinet is None
    return cabinet is not None and cabinet == firm


@app.post("/tenants/{tenant_id}/activare")
def tenant_activare(tenant_id: int, date: FirmaActivareIn, ctx=Depends(cere_rol("admin_firma"))):
    """[R72] Dezactivează / reactivează firma. O firmă CU evidență nu se șterge — iese din listă
    pe calea asta, iar documentele ei rămân.

    [R83] Poarta e `_acces_pentru_activare`, nu `auth_api.schema_tenant`: aia cere `activ = true`,
    ceea ce făcea reactivarea imposibilă. Vezi funcția pentru de ce excepția stă aici și nu acolo.

    IDEMPOTENT, decis explicit (JJ1): a cere activarea unei firme deja active **nu e o eroare**.
    `comuta_activ` întoarce `{"schimbat": false}` și nu scrie nimic — nici rând, nici audit. Motivul
    e al ecranului: butonul se poate apăsa de două ori, iar o a doua apăsare care ar da eroare ar
    arăta ca un defect acolo unde nu e niciunul. Un refuz se păstrează pentru ce **nu se poate
    face**, nu pentru ce **e deja făcut**."""
    with db.get_conn() as conn:
        if not _acces_pentru_activare(conn, ctx["rol"], ctx.get("firm"), tenant_id):
            raise HTTPException(404, "tenant inexistent sau fără acces")
        try:
            return tenant_stergere.comuta_activ(conn, tenant_id, date.activ, ctx["uid"])
        except ValueError as e:
            raise HTTPException(400, str(e))


class NumeAlesIn(BaseModel):
    alege: str


@app.post("/tenants/{tenant_id}/nume-ales")
def tenant_nume_ales(tenant_id: int, date: NumeAlesIn, ctx=Depends(cere_rol("admin_firma"))):
    """[R77] Alegerea între denumirea din aplicație și cea de la ANAF. **Amândouă** ramurile scriu:
    a păstra pe a ta e un act, nu absența unuia."""
    with db.get_conn() as conn:
        if not auth_api.schema_tenant(conn, ctx["uid"], tenant_id):
            raise HTTPException(404, "tenant inexistent sau fără acces")
        try:
            return tenant_provisioning.alege_denumirea(conn, tenant_id, date.alege, ctx["uid"])
        except ValueError as e:
            raise HTTPException(400, str(e))


@app.delete("/tenants/{tenant_id}")
def tenant_scoate(tenant_id: int, confirmare: str = "", ctx=Depends(cere_rol("admin_firma"))):
    """[R72] Scoate din portofoliu o firmă FĂRĂ evidență. Confirmarea e CUI-ul, nu numele:
    instanța care a produs restanța sunt două firme cu ACELAȘI nume."""
    with db.get_conn() as conn:
        if not auth_api.schema_tenant(conn, ctx["uid"], tenant_id):
            raise HTTPException(404, "tenant inexistent sau fără acces")
        try:
            r = tenant_stergere.sterge(conn, tenant_id, "scoatere_firma", ctx["uid"],
                                       confirmare=confirmare)
        except PermissionError as e:
            raise HTTPException(409, str(e))
        except ValueError as e:
            raise HTTPException(400, str(e))
    # DUPĂ commit: un `rmtree` nu se dă înapoi.
    r["fisiere_sterse"] = tenant_stergere.sterge_fisiere(r["schema"])
    return r


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
    try:  # tenant_cui_400
        with db.get_conn() as conn:
            r = tenant_provisioning.provision_tenant(
                conn, date.nume, date.cui, ctx["firm"], ctx["uid"], _TENANT_TEMPLATE,
                tip_firma=date.tip_firma)
            # [F188] pre-completare din ANAF v9 - SURSA UNICA (tenant_provisioning.precompleteaza_din_anaf),
            # aceeasi ca la register/import. NU atinge 'nume' (setat de contabil): seteaza_nume=False.
            # ANAF jos -> default, corectabil din Date firma.
            try:
                tenant_provisioning.precompleteaza_din_anaf(conn, r["schema_name"], date.cui, seteaza_nume=False)
            except Exception as _e:
                _obs.esec_secundar("precompletare ANAF la firma noua", _e)  # inghitit, dar nu tacut (27.07.2026)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return r


# [client_acces_v1] acces client la portal: creare cont + email cu parola temporara
class ClientAccesIn(BaseModel):
    email: str
    nume: str = ""
    mesaj: str = ""  # client_mesaj_v1

@app.get("/tenants/{tenant_id}/client-acces")
def client_acces_lista(tenant_id: int, ctx=Depends(cere_rol("admin_firma", "angajat"))):
    with db.get_conn() as conn:
        if not auth_api.schema_tenant(conn, ctx["uid"], tenant_id):
            raise HTTPException(404, "tenant inexistent sau fără acces")
        with conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
            cur.execute("""SELECT u.id, u.email, u.nume, u.activ FROM public.users u
                           JOIN public.user_tenants ut ON ut.user_id = u.id
                           WHERE ut.tenant_id = %s AND u.rol = 'client' ORDER BY u.id""", (tenant_id,))
            return {"clienti": cur.fetchall()}

@app.post("/tenants/{tenant_id}/client-acces")
def client_acces_creeaza(tenant_id: int, date: ClientAccesIn,
                         ctx=Depends(cere_rol("admin_firma"))):
    email = (date.email or "").strip().lower()
    if "@" not in email:
        raise HTTPException(400, EMAIL_INVALID)
    import secrets
    parola_temp = secrets.token_urlsafe(9)
    with db.get_conn() as conn:
        if not auth_api.schema_tenant(conn, ctx["uid"], tenant_id):
            raise HTTPException(404, "tenant inexistent sau fără acces")
        d = tenant_provisioning.detalii_tenant(conn, tenant_id)
        with conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
            cur.execute("SELECT id, rol, activ, accounting_firm_id FROM public.users "
                        "WHERE lower(email)=%s", (email,))
            _ex = cur.fetchone()
            if _ex and (_ex["rol"] != "client" or _ex["activ"]):
                raise HTTPException(400, EMAIL_EXISTA)
            # [R62 (2)] Aceeasi ramura de reactivare exista si aici. Gardul repara CLASA, nu
            # instanta: daca ar sta doar pe ruta clientului, calea prin cabinet ar ramane deschisa.
            _cere_acelasi_cabinet(_ex, ctx["firm"])
            if _ex:  # client_mesaj_v1: reinvitare client dezactivat
                uid = _ex["id"]
                cur.execute("UPDATE public.users SET activ=true, nume=%s WHERE id=%s",
                            (date.nume or email.split("@")[0], uid))
                cur.execute("INSERT INTO public.user_tenants (user_id, tenant_id) VALUES (%s, %s) ON CONFLICT DO NOTHING", (uid, tenant_id))
            el_creaza = _ex is None
            if el_creaza:
                cur.execute("""INSERT INTO public.users (email, password_hash, nume, rol, accounting_firm_id, activ)
                               VALUES (%s, %s, %s, 'client', %s, true) RETURNING id""",
                            (email, _nucleu.hash_parola(parola_temp), date.nume or email.split("@")[0], ctx["firm"]))
                uid = cur.fetchone()["id"]
                cur.execute("INSERT INTO public.user_tenants (user_id, tenant_id) VALUES (%s, %s)", (uid, tenant_id))
            _urma_portal(cur, tenant_id, "acces_dat",
                         "cabinetul a dat acces la portal lui %s (utilizator #%s)" % (email, uid),
                         ctx["uid"])
    # client_activare_v2: link magic (fara parola)
    import secrets as _sec
    tok = "ml_" + _sec.token_urlsafe(32)
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            _pune_token(cur, tok, uid, "48 hours")
    baza = os.environ.get("ICONTA_BAZA_URL", "http://localhost:8010")
    link = baza + "/#magic=" + tok
    _pm = ("<p style='border-left:3px solid #3d8fd6;padding-left:12px;color:#334155'>%s</p>" % date.mesaj.strip()) if (date.mesaj or "").strip() else ""  # client_mesaj_v1
    html = ("<p>Buna,</p>" + _pm + "<p>Ai primit acces la portalul iConta.eu pentru firma <b>%s</b>.</p>"
            "<p><a href='%s' style='display:inline-block;background:#3d8fd6;color:#fff;padding:10px 22px;border-radius:6px;text-decoration:none'>Intra in portal</a></p>"
            "<p>Linkul e valabil 48 de ore.</p>") % (d.get("nume", ""), link)
    _obs.trimite_email_html(email, "Acces portal iConta.eu — " + d.get("nume", ""), html)
    return {"ok": True, "user_id": uid}

class ActivareIn(BaseModel):
    token: str
    parola: str

# === MAGIC LINK === # magic_link_v1
# [token_hash_v1] Tokenurile de acces (magic-link + activare) se stocheaza DOAR ca hash sha256:
# un dump/backup nu mai permite impersonarea. Clarul traieste doar in link (email). Mecanica = ca la reset.
def _hash_tok(t):
    import hashlib
    return hashlib.sha256((t or "").encode("utf-8")).hexdigest()

def _pune_token(cur, tok, user_id, interval_sql):
    """Curata expiratele/folositele, apoi stocheaza DOAR hash-ul tokenului (nu clarul)."""
    cur.execute("DELETE FROM public.tokene_activare WHERE expira < now() OR folosit = true")
    cur.execute("INSERT INTO public.tokene_activare (token_hash, user_id, expira) "
                "VALUES (%s, %s, now() + (%s)::interval)", (_hash_tok(tok), user_id, interval_sql))

class MagicCereIn(BaseModel):
    email: str

_TERMENI_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "TERMENI_SI_CONDITII.md")

def _termeni_versiune(txt):
    """Versiunea = linia 3 din fisier (fara markdown bold). Stocata la acceptare ca dovada."""
    linii = txt.split("\n")
    return (linii[2].strip().strip("*").strip() if len(linii) > 2 else "necunoscuta")

def _termeni_public_md(txt):
    """Randeaza fisierul PUBLIC, dar ELIMINA ce fisierul insusi marcheaza intern: nota 'de eliminat
    inainte de publicare', pasajele [AVOCAT: ...] si Anexa interna (pentru avocat). Cand textul se
    finalizeaza (notele scoase manual) filtrarea devine no-op -> fisierul ramane inlocuibil fara cod."""
    out, in_anexa = [], False
    for ln in txt.split("\n"):
        s = ln.strip()
        if s.startswith("## Anex") and "intern" in s.lower():
            in_anexa = True
        if in_anexa:
            continue
        if s.startswith("> **Not") and "intern" in s.lower():
            continue
        if s.startswith(">") and "[AVOCAT:" in s:
            continue
        out.append(ln)
    return "\n".join(out)

_TERMENI_PAGINA = """<!doctype html><html lang="ro" class="pagina-publica"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Termeni si conditii - iConta.eu</title>
<link rel="stylesheet" href="/static/stil.css">
<style>
body{background:#f4f6f9;margin:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:#1d3a5f;line-height:1.6}
.tc-bara{display:flex;align-items:center;gap:10px;padding:14px 22px;background:#1d3a5f;color:#fff;font-weight:600}
.tc-bara a{color:#fff;text-decoration:none}
.tc-wrap{max-width:820px;margin:0 auto;padding:30px 22px 90px}
.tc-wrap h1{font-size:1.7rem;margin:.2em 0 .3em}
.tc-wrap h2{font-size:1.2rem;margin:1.6em 0 .4em}
.tc-wrap p,.tc-wrap li{color:#33445a}
.tc-wrap a{color:#1d4ed8}
.tc-wrap blockquote{border-left:3px solid #b9c2cf;margin:1em 0;padding:.2em 0 .2em 14px;color:#5b6b7c;background:#eef4fd}
.tc-wrap hr{border:none;border-top:1px solid #dbe1ea;margin:1.6em 0}
.tc-inapoi{margin-top:44px}
</style></head><body class="pagina-publica">
<div class="tc-bara"><a href="/">iConta.eu</a><span>&middot; Termeni si conditii</span></div>
<main class="tc-wrap">%(corp)s<p class="tc-inapoi"><a href="/">&larr; Inapoi la iConta.eu</a></p></main>
</body></html>"""

@app.get("/public/termeni")  # [termeni_v1] markdown->HTML DIN FISIER (inlocuibil fara cod); exclude notele interne marcate in fisier
def public_termeni():
    import markdown as _md
    try:
        txt = open(_TERMENI_PATH, encoding="utf-8").read()
    except Exception:
        raise HTTPException(404, "Termenii nu sunt disponibili momentan.")
    corp = _md.markdown(_termeni_public_md(txt), extensions=["extra", "sane_lists"])
    return Response(content=_TERMENI_PAGINA % {"corp": corp}, media_type="text/html; charset=utf-8")

@app.get("/public/config")  # [beta_gate_v1] doar STAREA portii (bool), NU valoarea codului
def public_config():
    return {"beta": False}   # [beta_gate SCOS 14.08] acces liber - campul de cod nu mai apare


class ResetCereIn(BaseModel):
    email: str

class ResetSeteazaIn(BaseModel):
    token: str
    parola: str

_reset_rate = {}  # [reset_parola_v1] rate-limit in-memory per IP (single worker uvicorn) — anti-spam prin emailurile noastre
def _ip_client(request):
    # [xff_realip_v1] nginx suprascrie X-Real-IP cu $remote_addr (nefalsificabil); primul hop XFF e
    # controlat de client -> citim X-Real-IP, altfel ULTIMUL hop XFF (adaugat de nginx), altfel peer TCP.
    xr = request.headers.get("x-real-ip")
    if xr:
        return xr.strip()
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[-1].strip()
    return request.client.host if request.client else "?"
_magic_rate = {}  # [magic_link_v1] rate-limit per IP pt /public/magic-link (aceleasi praguri ca reset)
_cui_rate = {}  # [verifica_cui_v1] rate-limit /public/verifica-cui (protejeaza cheia ANAF)
def _rate_limit_email(store, request, maxreq=5, fereastra=900):
    """Anti-spam per IP (in-memory, single worker). Implicit 5 cereri / 15 min."""
    import time as _t
    ip = _ip_client(request); acum = _t.time()
    q = [t for t in store.get(ip, []) if acum - t < fereastra]
    if len(q) >= maxreq:
        raise HTTPException(429, "Prea multe cereri. Încearcă din nou peste câteva minute.")
    q.append(acum); store[ip] = q
def _rate_limit_reset(request):
    _rate_limit_email(_reset_rate, request)

@app.post("/public/reset-parola/cere")  # [reset_parola_v1] "Am uitat parola" cabinet — raspuns IDENTIC (anti-enumerare), rate-limited
def reset_parola_cere(date: ResetCereIn, request: Request):
    _rate_limit_reset(request)
    from core import reset_parola as _rp
    with db.get_conn() as conn:
        token, u = _rp.cere_reset(conn, date.email)
        conn.commit()
    if token and u:
        try:
            baza = os.environ.get("ICONTA_BAZA_URL", "https://iconta.eu")
            link = baza + "/#reset=" + token
            nume = (u.get("prenume") or u.get("nume") or "").strip()
            html = ("<p>Buna%s,</p>"
                    "<p>Am primit o cerere de resetare a parolei contului tau de cabinet pe iConta.eu.</p>"
                    "<p><a href='%s' style='display:inline-block;background:#3d8fd6;color:#fff;padding:10px 22px;border-radius:6px;text-decoration:none'>Seteaza o parola noua</a></p>"
                    "<p>Linkul e valabil 60 de minute si poate fi folosit o singura data. "
                    "Daca nu tu ai cerut resetarea, ignora acest mesaj — parola ramane neschimbata.</p>"
                    % ((" " + nume) if nume else "", link))
            _obs.trimite_email_html(u["email"], "Resetare parola iConta.eu", html)
        except Exception as _e:
            # [R73] ALERTA: e cale de acces. Tacerea aici inseamna ca omul nu mai poate intra
            # si nimeni nu afla — chiar criteriul din docstringul lui `esec_secundar`.
            _obs.esec_secundar("email resetare parola", _e, alerta=True)
        try:
            with db.get_conn() as c, c.cursor() as cur:
                cur.execute("INSERT INTO public.audit_log (user_id, actiune) VALUES (%s,'reset_parola_cerut')", (u["user_id"],))
                c.commit()
        except Exception as _e:
            _obs.esec_secundar("audit_log reset parola cerut", _e)  # inghitit, dar nu tacut (27.07.2026)
    return {"ok": True, "mesaj": "Dacă adresa e înregistrată, vei primi un mesaj cu instrucțiuni de resetare."}

@app.post("/public/reset-parola/seteaza")  # [reset_parola_v1] valideaza tokenul (single-use), seteaza parola, invalideaza sesiunile
def reset_parola_seteaza(date: ResetSeteazaIn):
    if not _nucleu.parola_ok(date.parola):
        raise HTTPException(400, _nucleu.PAROLA_MESAJ)
    from core import reset_parola as _rp
    with db.get_conn() as conn:
        try:
            r = _rp.seteaza(conn, date.token, date.parola)
            conn.commit()
        except ValueError:
            raise HTTPException(400, "Link invalid, expirat sau deja folosit. Cere alt link din sectiunea Am uitat parola.")
    try:
        with db.get_conn() as c, c.cursor() as cur:
            cur.execute("INSERT INTO public.audit_log (user_id, actiune) VALUES (%s,'reset_parola_schimbat')", (r["user_id"],))
            c.commit()
    except Exception as _e:
        _obs.esec_secundar("audit_log reset parola schimbat", _e)  # inghitit, dar nu tacut (27.07.2026)
    return {"ok": True}

@app.post("/public/magic-link")
def magic_link_cere(date: MagicCereIn, request: Request):
    """Trimite link de logare fara parola. Raspuns identic indiferent daca emailul exista (fara enumerare)."""
    _rate_limit_email(_magic_rate, request)  # [magic_link_v1] anti-spam: 5/15min per IP (ca reset)
    import secrets as _sec
    email = (date.email or "").strip().lower()
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id FROM public.users WHERE email=%s AND activ", (email,))
        r = cur.fetchone()
        if r:
            tok = "ml_" + _sec.token_urlsafe(32)
            _pune_token(cur, tok, r[0], "15 minutes")
            conn.commit()
            baza = os.environ.get("ICONTA_BAZA_URL", "http://localhost:8010")
            link = baza + "/#magic=" + tok
            html = ("<p>Buna,</p><p>Apasa butonul pentru a intra in iConta.eu, fara parola:</p>"
                    "<p><a href='%s' style='display:inline-block;background:#3d8fd6;color:#fff;padding:10px 22px;border-radius:6px;text-decoration:none'>Intra in iConta.eu</a></p>"
                    "<p>Linkul e valabil 15 minute si poate fi folosit o singura data.</p>") % link
            try:
                _obs.trimite_email_html(email, "Link de logare iConta.eu", html)
            except Exception as _e:
                # [R73] ALERTA: SINGURA usa de intrare in portalul clientului.
                _obs.esec_secundar("email link de logare", _e, alerta=True)
    return {"ok": True, "mesaj": MESAJ_LINK_LOGARE_CERUT}

class MagicLoginIn(BaseModel):
    token: str

@app.post("/public/magic-login")
def magic_login(date: MagicLoginIn):
    tok = (date.token or "").strip()
    if not tok.startswith("ml_"):
        raise HTTPException(401, "link invalid")
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("""SELECT user_id FROM public.tokene_activare
                       WHERE token_hash=%s AND NOT folosit AND expira > now()""", (_hash_tok(tok),))
        r = cur.fetchone()
        if not r:
            raise HTTPException(401, "link expirat sau folosit")
        cur.execute("UPDATE public.tokene_activare SET folosit=true WHERE token_hash=%s", (_hash_tok(tok),))
        conn.commit()
    with db.get_conn() as conn:
        rez = auth_api.sesiune_pentru_user(conn, r[0])
    if not rez.get("ok"):
        raise HTTPException(401, rez.get("mesaj", "cont inactiv"))
    return rez

@app.post("/public/activare")
def activare_cont(date: ActivareIn):
    if not _nucleu.parola_ok(date.parola):
        raise HTTPException(400, _nucleu.PAROLA_MESAJ)
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
            cur.execute("""SELECT user_id FROM public.tokene_activare
                           WHERE token_hash=%s AND NOT folosit AND expira > now()""", (_hash_tok(date.token),))
            r = cur.fetchone()
            if not r:
                raise HTTPException(400, "link de activare invalid sau expirat")
            cur.execute("UPDATE public.users SET password_hash=%s, parola_schimbata=true, activ=true WHERE id=%s",
                        (_nucleu.hash_parola(date.parola), r["user_id"]))
            cur.execute("UPDATE public.tokene_activare SET folosit=true WHERE token_hash=%s", (_hash_tok(date.token),))
    return {"ok": True}

@app.delete("/tenants/{tenant_id}/client-acces/{user_id}")
def client_acces_revoca(tenant_id: int, user_id: int, ctx=Depends(cere_rol("admin_firma"))):
    with db.get_conn() as conn:
        if not auth_api.schema_tenant(conn, ctx["uid"], tenant_id):
            raise HTTPException(404, "tenant inexistent sau fără acces")
        with conn.cursor() as cur:
            cur.execute("""UPDATE public.users SET activ=false WHERE id=%s AND rol='client'
                           AND id IN (SELECT user_id FROM public.user_tenants WHERE tenant_id=%s)""",
                        (user_id, tenant_id))
            _urma_portal(cur, tenant_id, "acces_retras",
                         "cabinetul a retras accesul utilizatorului #%s" % user_id, ctx["uid"])
    return {"ok": True}


@app.post("/tenants/{tenant_id}/acces-portal")  # [F-preview] previzualizare portal client din cabinet
def acces_portal_preview(tenant_id: int, ctx=Depends(cere_rol("admin_firma", "angajat"))):
    """Emite un token de PREVIZUALIZARE (read-only, tab-local) pentru portalul clientului firmei.
    Cabinetul vede exact ce vede clientul, fara sa poata scrie (guard pe backend, nu doar UI).
    Necesita un cont de client al firmei (rol=client in user_tenants); daca nu exista -> 400 cu indrumare."""
    with db.get_conn() as conn:
        if not auth_api.schema_tenant(conn, ctx["uid"], tenant_id):
            raise HTTPException(404, "tenant inexistent sau fără acces")
        with conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
            cur.execute("""SELECT u.id FROM public.users u
                           JOIN public.user_tenants ut ON ut.user_id = u.id
                           WHERE ut.tenant_id=%s AND u.rol='client' AND u.activ=true
                           ORDER BY u.id LIMIT 1""", (tenant_id,))
            row = cur.fetchone()
            # [F-preview] identitatea tenantului previzualizat: nume_tenant + tenant_are_cabinet
            # (accounting_firm_id setat) -> exact ce foloseste portal.js/_eGratuit ca la login.
            cur.execute("SELECT nume, accounting_firm_id FROM public.tenants WHERE id=%s", (tenant_id,))
            tr = cur.fetchone()
    if not row:
        raise HTTPException(400, "Firma nu are încă un cont de client. Invită unul din 'Acces client', apoi poți previzualiza.")
    # token de client, marcat preview -> read-only middleware blocheaza orice mutatie
    token = auth_api.emite_token({"id": row["id"], "rol": "client", "accounting_firm_id": None, "preview": True})
    # user cu contextul de tenant: fara el, tab-ul de preview cade pe portalul gratuit (bug F197).
    return {"token": token, "user": {"rol": "client",
                                     "nume_tenant": tr["nume"] if tr else None,
                                     "tenant_are_cabinet": bool(tr and tr["accounting_firm_id"])}}


@app.put("/tenants/{tenant_id}")
def tenant_actualizeaza(tenant_id: int, date: TenantEdit,
                        ctx=Depends(cere_rol("admin_firma"))):
    with db.get_conn() as conn:
        if not auth_api.schema_tenant(conn, ctx["uid"], tenant_id):
            raise HTTPException(404, "tenant inexistent sau fără acces")
        # [R77] `ctx["uid"]` nu e decorativ: o redenumire care se departeaza de denumirea de la
        # ANAF se consemneaza ca alegere deliberata, iar o alegere fara autor nu e o alegere.
        r = tenant_provisioning.actualizeaza_tenant(conn, tenant_id, date.nume, date.cui,
                                                    user_id=ctx["uid"])
    return r


# ============================================================
#  MIGRARE CABINET — validare CUI la ANAF + import în masă
# ============================================================
@app.post("/migrare/valideaza")
def migrare_valideaza(date: MigrareValideazaIn, ctx=Depends(cere_cabinet)):
    """Verifică o listă de CUI-uri la ANAF; întoarce denumirea + status."""
    if not date.cui_uri:
        return {"rezultate": [], "ignorate": []}
    _curatate, ignorate = anaf_api.separa_cui(date.cui_uri)
    try:
        rez = anaf_api.valideaza_cui(date.cui_uri)
    except Exception as e:
        raise HTTPException(502, f"ANAF indisponibil sau a refuzat cererea: {e}")
    return {"rezultate": rez, "ignorate": ignorate}


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
                # [P8/C] respingere TIPATA: pana azi ecranul numara duplicatele potrivind PROZA
                # (`(e.mesaj || "").includes("există deja")`), deci o reformulare a textului ar fi
                # spus tacit „0 firme erau deja in portofoliu" despre un import in care erau.
                erori.append(migrare_api.respinge(
                    "firmă", "firma %s (CUI %s)" % (nume, f.cui), "deja_exista",
                    "există deja în portofoliu - nu s-a dublat", cui=str(f.cui), nume=nume))
                continue
            try:
                r = tenant_provisioning.provision_tenant(
                    conn, nume, str(f.cui), ctx["firm"], ctx["uid"], _TENANT_TEMPLATE)
                try:  # [import_profil_anaf_v1] aceeasi precompletare ANAF ca la add-firm (SURSA UNICA)
                    tenant_provisioning.precompleteaza_din_anaf(conn, r["schema_name"], f.cui, seteaza_nume=False)
                except Exception as _ea:
                    _obs.esec_secundar("precompletare ANAF la import firma", _ea)  # firma creata; ANAF completabil manual
                creat.append({"cui": str(f.cui), "nume": nume, "tenant_id": r.get("tenant_id")})
                if cuic:
                    existente.add(cuic)   # prinde și duplicate în același lot
            except Exception as e:
                # ESEC, nu respingere de date: sta in aceeasi lista cu `deja_exista`, dar cauza e
                # alta si omul trebuie s-o poata deosebi - altfel cauta greseala in fisier cand
                # problema e la noi.
                erori.append(migrare_api.respinge(
                    "firmă", "firma %s (CUI %s)" % (nume, f.cui), "creare_esuata",
                    "nu s-a putut crea: %s" % e, cui=str(f.cui), nume=nume))
    return {"creat": creat, "erori": erori, "total": len(creat)}


@app.get("/migrare/status")
def migrare_status_citeste(ctx=Depends(cere_cabinet)):
    """Starea fiecărui strat de migrare + reminderul (straturi în lucru)."""
    with db.get_conn() as conn:
        status = migrare_api.citeste_status(conn, ctx["firm"])
        rem = migrare_api.reminder(conn, ctx["firm"])
    return {"straturi": migrare_api.STRATURI, "status": status, "reminder": rem}


@app.get("/migrare/straturi")
def migrare_straturi_aplicabile(tip_firma: str = "srl", ctx=Depends(cere_cabinet)):
    """[p_pfa_rip 20.07] Straturile de migrare aplicabile unui regim (srl/pfa).
    Sursa unica de adevar = migrare_api.straturi_pentru (filtreaza pe STRATURI_META),
    ca meniul per-firma sa nu reinventeze in JS ce strat apartine carui regim."""
    return {"straturi": migrare_api.straturi_pentru(tip_firma)}


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

@app.get("/migrare/plan-conturi")  # [p95_plan_conturi] lista firmelor cu numar de conturi in plan
def migrare_plan_conturi_status(ctx=Depends(cere_cabinet)):
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
                with c.cursor() as cur:
                    cur.execute("SELECT count(*) FROM plan_conturi")
                    n = cur.fetchone()[0]
        except Exception:
            n = 0
        out.append({"tenant_id": tid, "nume": f.get("nume"), "cui": f.get("cui"), "nr_conturi": n})
    return {"firme": out}
@app.get("/tenants/{tenant_id}/plan-conturi")  # [p95_plan_conturi] cauta/listeaza conturile firmei
def tenant_plan_conturi_lista(tenant_id: int, q: Optional[str] = None, ctx=Depends(cere_context)):
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        with conn.cursor() as cur:
            if q:
                cur.execute(
                    "SELECT simbol, denumire, tip FROM plan_conturi "
                    "WHERE simbol ILIKE %s OR denumire ILIKE %s ORDER BY simbol LIMIT 100",
                    (f"%{q}%", f"%{q}%"))
            else:
                cur.execute("SELECT simbol, denumire, tip FROM plan_conturi ORDER BY simbol LIMIT 100")
            rows = cur.fetchall()
    return {"conturi": [{"simbol": r[0], "denumire": r[1], "tip": r[2]} for r in rows]}
# [p95_plan_conturi] Modelul TREBUIE definit INAINTE de handler: cu `from __future__ import annotations`
# (PEP 563) adnotarea `date: PlanContIn` e string, iar @app.post o rezolva la IMPORT, in ordinea sursei.
# Definit DUPA handler => FastAPI nu-l recunoaste ca model de body => trateaza `date` ca query param =>
# orice adaugare de cont pica cu 422 "date required". (Bug gasit la auditul vizual tenant_005, 17.08.)
class PlanContIn(BaseModel):  # [p95_plan_conturi]
    simbol: str
    denumire: str
    tip: Optional[str] = "Bifunctional"


@app.post("/tenants/{tenant_id}/plan-conturi")  # [p95_plan_conturi] adauga cont nou (analitic/nestandard)
# [R55, 26.08.2026] Rolul e AICI, nu doar la validarea notei. Motivul, al lui Costin: refuzul pe
# cont inexistent (R54) „nu apara nimic daca oricine poate adauga contul". Planul de conturi e
# nomenclator de registru (PLAN_ARHITECTURA Partea III), iar a-l extinde e o decizie despre ce
# poate inregistra firma — nu o completare de formular.
def tenant_plan_conturi_adauga(tenant_id: int, date: PlanContIn,
                               ctx=Depends(cere_rol("admin_firma"))):
    schema = _schema_sau_404(ctx, tenant_id)
    simbol = (date.simbol or "").strip()
    denumire = (date.denumire or "").strip()
    if not simbol or not denumire:
        raise HTTPException(422, "Completează atât simbolul, cât și denumirea contului.")
    # [lotul 3, 04.09.2026] `simbol="ABC"` intra in plan si de acolo putea ajunge pe o nota, intr-o
    # balanta si intr-o declaratie. Criteriul e DERIVAT din nomenclatorul propriu: planul general
    # seed-uit la crearea firmei are peste 700 de conturi, toate incepand cu o cifra de clasa.
    if not simbol[0].isdigit() or simbol[0] == "0":
        raise HTTPException(422, "Simbolul contului începe cu cifra clasei (1-9), ca toate "
                                 "conturile din planul general — am primit %r. Dacă e un analitic, "
                                 "scrie-l după contul sintetic (de exemplu 4111.01)." % simbol)
    if not all(c.isdigit() or c in "._-/" for c in simbol):
        raise HTTPException(422, "Simbolul contului se scrie din cifre, cu separator pentru "
                                 "analitic (`.`, `_`, `-`, `/`) — am primit %r." % simbol)
    with db.get_conn(schema) as conn:
        with conn.cursor() as cur:
            # Regula 4 + 14.4: un simbol care exista deja NU se suprascrie tacut (ar redenumi un cont OMFP
            # standard, seed-uit la crearea firmei). Calea bulk (solduri_api) foloseste ON CONFLICT DO NOTHING;
            # calea manuala refuza explicit, cu denumirea contului existent, si trimite la cautarea de mai sus.
            cur.execute("SELECT denumire FROM plan_conturi WHERE simbol = %s", (simbol,))
            existent = cur.fetchone()
            if existent:
                raise HTTPException(409,
                    "Contul %s există deja în plan: „%s”. Caută-l în lista de mai sus; dacă ai nevoie "
                    "de un cont diferit, folosește alt simbol." % (simbol, existent[0]))
            cur.execute(
                "INSERT INTO plan_conturi (simbol, denumire, tip) VALUES (%s, %s, %s)",
                (simbol, denumire, date.tip or "Bifunctional"))
        conn.commit()
    return {"ok": True, "simbol": simbol}
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
                    "regim_contabil": f.get("regim_contabil"),   # [regim] partida simpla/dubla -> ascunde regim la PFA
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
    valida, motiv = solduri_api.balanta_valida(randuri)
    # [P8] cand fisierul NU e o balanta valida, spunem CE regula nu tine si PE CE fisier - nu doar
    # un text. Domeniul e FISIERUL incarcat (fel de referent adaugat 22.08).
    _baza = {"randuri": randuri, "total_debit": td, "total_credit": tc, "valida": valida}
    if valida:
        return dict(_baza, motiv=motiv)
    return dict(_baza, **migrare_api.respinge(
        "balanță de deschidere", _Unde("fisier", fisier.filename or "(fără nume)"),
        "balanta_nu_se_echilibreaza", motiv))


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
        try:
            return solduri_api.importa(conn, randuri, date.data_referinta)
        except ValueError as e:  # balanta neechilibrata -> 422 cu mesaj explicativ
            raise HTTPException(422, str(e))


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
    erori = migrare_api.erori_verifica(solduri_parteneri_api.verifica_randuri(randuri))  # [Q5] poarta unica
    return {"randuri": randuri, "total_debit": td, "total_credit": tc, "coerenta": coer, "erori": erori}


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
        try:
            return solduri_parteneri_api.importa(conn, randuri, date.data_referinta)
        except ValueError as e:  # randuri invalide -> 422 cu mesaj explicativ
            raise HTTPException(422, str(e))



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
    erori = migrare_api.erori_verifica(salariati_import_api.verifica_randuri(randuri))  # [Q5] poarta unica
    from core import cor_api as _cor   # [Q16] imbogateste COR cu denumirea ocupatiei (nomenclator public.cor_ocupatii)
    _cache = {}
    with db.get_conn() as conn:
        for r in randuri:
            c = (r.get("cor") or "").strip()
            if c and c not in _cache:
                _cache[c] = _cor.denumire(conn, c)
    for r in randuri:
        r["cor_denumire"] = _cache.get((r.get("cor") or "").strip())
    return {"randuri": randuri, "total": len(randuri), "valizi": valizi,
            "invalizi": len(randuri) - valizi, "erori": erori}


@app.post("/tenants/{tenant_id}/salariati-import")
def salariati_import_salveaza(tenant_id: int, date: SalariatiImportIn, ctx=Depends(cere_rol("admin_firma"))):
    """Importa salariatii cu CNP valid (upsert pe CNP). Sare peste cei invalizi."""
    schema = _schema_sau_404(ctx, tenant_id)
    randuri = [r.model_dump() for r in date.randuri]
    with db.get_conn(schema) as conn:
        try:
            return salariati_import_api.importa(conn, randuri)
        except ValueError as e:  # randuri invalide -> 422 cu mesaj
            raise HTTPException(422, str(e))



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
    erori = migrare_api.erori_verifica(asociati_import_api.verifica_randuri(randuri))  # [Q5] poarta unica
    return {"randuri": randuri, "total": len(randuri), "coerenta": coer, "erori": erori}


@app.post("/tenants/{tenant_id}/asociati-import")
def asociati_import_salveaza(tenant_id: int, date: AsociatiImportIn, ctx=Depends(cere_rol("admin_firma"))):
    schema = _schema_sau_404(ctx, tenant_id)
    randuri = [r.model_dump() for r in date.randuri]
    with db.get_conn(schema) as conn:
        try:
            return asociati_import_api.importa(conn, randuri)
        except ValueError as e:  # randuri invalide -> 422 cu mesaj
            raise HTTPException(422, str(e))



# === IMPORT RETETE HORECA (F150) ===
class ReteteImportIn(BaseModel):
    retete: list[dict]
@app.post("/tenants/{tenant_id}/retete-import/incarca")
async def retete_import_incarca(tenant_id: int, fisier: UploadFile = File(...), ctx=Depends(cere_cabinet)):
    schema = _schema_sau_404(ctx, tenant_id)
    continut = await fisier.read()
    try:
        retete = retete_import_api.extrage(continut, fisier.filename or "")
    except ValueError as e:
        raise HTTPException(400, str(e))
    with db.get_conn(schema) as conn:
        retete = retete_import_api.potriveste(conn, schema, retete)
    return {"retete": retete, "rezumat": retete_import_api.rezumat(retete)}
@app.post("/tenants/{tenant_id}/retete-import")
def retete_import_salveaza(tenant_id: int, date: ReteteImportIn, ctx=Depends(cere_rol("admin_firma"))):
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        return retete_import_api.importa(conn, schema, date.retete)
# === IMPORT ARTICOLE + STOC INITIAL CV (F151) ===
class ArticolImportIn(BaseModel):
    denumire: str
    um: str = "buc"
    cantitate: float = 0
    pret: float = 0
    cont_stoc: str = "302"
    cont_cheltuiala: str = "601"
    valid: bool = True
    motiv: str = "ok"
class ArticoleImportIn(BaseModel):
    randuri: list[ArticolImportIn]
    data_sold: Optional[str] = None
@app.post("/tenants/{tenant_id}/articole-import/incarca")
async def articole_import_incarca(tenant_id: int, fisier: UploadFile = File(...), ctx=Depends(cere_cabinet)):
    _schema_sau_404(ctx, tenant_id)
    continut = await fisier.read()
    try:
        randuri = articole_import_api.extrage(continut, fisier.filename or "")
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {"randuri": randuri, "rezumat": articole_import_api.rezumat(randuri)}
@app.post("/tenants/{tenant_id}/articole-import")
def articole_import_salveaza(tenant_id: int, date: ArticoleImportIn, ctx=Depends(cere_rol("admin_firma"))):
    schema = _schema_sau_404(ctx, tenant_id)
    randuri = [r.model_dump() for r in date.randuri]
    with db.get_conn(schema) as conn:
        return articole_import_api.importa(conn, schema, randuri, data_sold=date.data_sold)
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
    erori = migrare_api.erori_verifica(mijloace_fixe_import_api.verifica_randuri(randuri))  # [Q5] poarta unica
    return {"randuri": randuri, "total": len(randuri), "total_valoare": tv,
            "total_rezidual": tr, "cu_avertismente": cu_avert, "erori": erori}


@app.post("/tenants/{tenant_id}/mijloace-fixe-import")
def mijloace_import_salveaza(tenant_id: int, date: MijloaceFixeImportIn, ctx=Depends(cere_rol("admin_firma"))):
    schema = _schema_sau_404(ctx, tenant_id)
    randuri = [r.model_dump() for r in date.randuri]
    with db.get_conn(schema) as conn:
        try:
            return mijloace_fixe_import_api.importa(conn, randuri)
        except ValueError as e:  # randuri invalide -> 422 cu mesaj
            raise HTTPException(422, str(e))



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
    erori = migrare_api.erori_verifica(istoric_declaratii_import_api.verifica_randuri(randuri))  # [Q5] poarta unica
    return {"randuri": randuri, "total": len(randuri), "cu_avertismente": cu_avert, "erori": erori}


@app.post("/tenants/{tenant_id}/istoric-declaratii-import")
def istoric_import_salveaza(tenant_id: int, date: IstoricDeclImportIn, ctx=Depends(cere_rol("admin_firma"))):
    _schema_sau_404(ctx, tenant_id)
    randuri = [r.model_dump() for r in date.randuri]
    with db.get_conn() as conn:
        try:
            return istoric_declaratii_import_api.importa(conn, tenant_id, randuri)
        except ValueError as e:  # randuri invalide -> 422 cu mesaj
            raise HTTPException(422, str(e))


# ============================================================
#  MIGRARE STRAT PFA — REGISTRU INCASARI/PLATI (RIP, partida simpla)
#  [p_pfa_rip 20.07] Preluarea unui PFA: istoric cronologic al anului curent,
#  NU balanta de deschidere (partida simpla nu are sold-rand separat).
# ============================================================
@app.post("/tenants/{tenant_id}/rip-import/incarca")
async def rip_import_incarca(tenant_id: int, fisier: UploadFile = File(...), ctx=Depends(cere_rol("admin_firma"))):
    """
    Import registru incasari-plati la preluarea unui PFA. Parseaza fisierul, RAPORTEAZA
    randurile respinse (ambigue/incomplete) INAINTE de commit, apoi importa operatiunile
    valide intr-o tranzactie atomica (rip_migrare_api.importa) si marcheaza stratul 'rip'
    pentru reminder(): 'gata' daca nimic respins, 'in_lucru' cu nota daca au ramas randuri.
    """
    schema = _schema_sau_404(ctx, tenant_id)
    continut = await fisier.read()
    try:
        date, raport = rip_migrare_api.extrage_operatiuni(continut, fisier.filename or "")
    except ValueError as e:
        raise HTTPException(400, str(e))
    ops = date.get("operatiuni", [])
    respinse = raport.get("respinse", [])
    if not ops and not respinse:
        raise HTTPException(400, "fișierul nu conține operațiuni de import")
    # import atomic (importa face commit/rollback propriu); erori DB -> nimic scris
    with db.get_conn(schema) as conn:
        rez = rip_migrare_api.importa(conn, schema, ops)
    if rez["erori"]:
        raise HTTPException(422, "import eșuat: " + str(rez["erori"][0].get("motiv", "eroare la scriere")))
    # marcheaza stratul rip (public.migrare_status, per cabinet) pentru reminder()
    with db.get_conn() as conn:
        if respinse:
            migrare_api.seteaza_status(conn, ctx["firm"], "rip", "in_lucru",
                                       f"{len(respinse)} rânduri respinse la import — de completat")
        else:
            migrare_api.seteaza_status(conn, ctx["firm"], "rip", "gata", "")
    return {"importate": rez["importate"], "sarite_duplicat": rez.get("sarite_duplicat", 0), "raport": raport}



# ============================================================
#  CONTROL FISCAL — semafor conformare per portofoliu
# ============================================================
def _flag_constatare(stare, eticheta, mesaj, temei, an, luna, remediu=None):
    # [verdict_colapsat] constatare STRUCTURATA (dot + mesaj + temei + remediu), randata identic cu D390/TVA
    # in control.js. `eticheta` = label scurt (sumar de lista + dedup fata de «Declaratie vs contabilitate»).
    # [P8, 21.08.2026] Constatarea E o afirmatie, imbracata pentru ecran - ca in control_incrucisat.
    # Felul se alege dupa STARE, fiindca asta E ce afirma: verde = am verificat si tine (fapt);
    # rosu = doua surse nu pot fi amandoua adevarate (contradictie); gri = nu pot spune (necunoastere).

    _txt = mesaj or eticheta
    if stare == "gri":
        _dom = ("%04d-%02d" % (an, luna)) if (an and luna) else (str(an) if an else None)
        _a = _af.afirmatie("necunoastere", eticheta, _txt, domeniu_de=_dom, domeniu_pana=_dom)
    elif stare == "rosu":
        _a = _af.afirmatie("contradictie", eticheta, _txt,
                           sursele="evidența contabilă a firmei; verificarea „%s”" % eticheta)
    else:
        _a = _af.afirmatie("fapt", eticheta, _txt, an=an, luna=luna,
                           temei_completitudine=temei or "verificarea „%s” a rulat pe datele lunii"
                                                         % eticheta)
    # Campurile se pun UNUL CATE UNUL: un `{... "mesaj": ...}` aici ar fi numarat de
    # `core/scan_afirmatii` drept inca o afirmatie netipata, iar CONSTRUCTORUL afirmatiilor ar aparea
    # pe vecie in clichet ca datorie. Nu e cosmetica - chiar exista un singur dictionar, imbogatit.
    _a["stare"] = stare
    _a["eticheta"] = eticheta
    _a["mesaj"] = _txt
    _a["temei"] = temei or ""
    _a["remediu"] = remediu
    return _a


import logging as _logging
_LOG_VERDICT = _logging.getLogger("iconta.verdict")


def _constatare_esuata(eticheta, nume, e, an, luna):
    """Constatare GRI pentru un verificator care CRAPA (nu 'nimic de raportat' - e 'nu am putut verifica').
    Excepția înghițită face firma să pară mai curată decât e (minciună prin omisiune). GRI nu escaladeaza
    pastila_firma (rezistenta se pastreaza - un esec izolat nu doboara semaforul), dar il anunta pe CONTABIL,
    care decide. Doua straturi: GRI = principal (il vede contabilul); log = secundar (sa se vada daca pica
    SISTEMATIC). Vezi DECIZII 23.07. Intoarce constatarea (apelantul o pune unde e vizibila)."""
    _LOG_VERDICT.warning("verificator esuat pe cale de verdict: %s -> gri (%r)", nume, e)
    return _flag_constatare("gri", eticheta, "Nu am putut verifica %s." % nume,
        "Verificarea a eșuat (%s). GRI înseamnă 'nu am putut verifica', NU 'curat' — o constatare reală "
        "poate lipsi. Reîncarcă; dacă persistă, semnalează." % e, an, luna)


def _verificator_esuat(contabil, eticheta, nume, e, an, luna):
    """Varianta pt lista de constatari (contabil): adauga constatarea gri. Vezi _constatare_esuata."""
    contabil.append(_constatare_esuata(eticheta, nume, e, an, luna))


# [paritate_severitate 24.07] Chei din verificari_contabile (vc) care NU se pliaza in `contabil` -> nu urca
# pastila_firma (severitatea firmei). Declarate EXPLICIT, cu motiv — nu judecate: garda le SCOATE la iveala
# (VERDICT_PARITATE sub-regula severitate, in verificator), decizia de a le urca in pastila ramane a lui Costin.
# Contractul: fiecare cheie vc e ori pliata in `contabil` (mai jos), ori aici. O cheie noua fara niciuna =
# eroare in verificator. Vezi DESIGN_SYSTEM cap.20.
VC_FARA_SEVERITATE = {
    "documente_pozate": "verificare de flux operational (bonuri/note de casa confirmate de client, necontate); informativa, nu ridica inca severitatea firmei — vezi comentariul din _verificari_contabile",
    "tva": "coerenta bruta 4427/4426 pe balanta; severitatea TVA vine din tva_incrucisat (D300 vs contabilitate), nu din soldurile brute",
    "note": "contor de note contabile pe perioada, nu o constatare",
}


def _construieste_contabil(schema, tid, ctx, an, luna, regim_tva_anaf):
    """Constatarile contabile STRUCTURATE ale unei firme + verificari_contabile brute (vc). UN SINGUR loc,
    folosit de LISTA (portofoliu) SI de DETALIU -> severitatea (pastila_firma) e aceeasi indiferent cine
    intreaba (headerul de detaliu nu mai poate fi mai bun decat ce e sub el). Cost pe calea de detaliu:
    _verificari_contabile rula deja acolo (partea grea - regenereaza D300/D112/D390); se adauga doar
    verificare_stocuri (O(articole) query-uri usoare) + intrastat_praguri (1 query). Vezi DECIZII 23.07.
    Intoarce (contabil, vc)."""
    contabil = []
    vc = None
    try:
        vc = _verificari_contabile(schema, an, luna)
        ech = vc.get("echilibru") or {}
        if not ech.get("ok", True):
            contabil.append(_flag_constatare(stare_din_nivel(ech.get("nivel")), "Balanță dezechilibrată", ech.get("mesaj"), ech.get("temei"), an, luna))
        tz = vc.get("trezorerie") or []
        tz_probleme = tz if isinstance(tz, list) else ([tz] if isinstance(tz, dict) and not tz.get("ok", True) else [])
        for p in tz_probleme:
            contabil.append(_flag_constatare(stare_din_nivel(p.get("nivel")), "Solduri creditoare trezorerie", p.get("mesaj"), p.get("temei"), an, luna))
        # [control_incrucisat_v1 + F163_ui] declaratie vs evidenta. Constatarea INTREAGA e in «Declaratie vs
        # contabilitate»; aici doar sumarul (eticheta + temei). Etichete = EXACT cele filtrate in control.js.
        for cheie, et in (("tva_incrucisat", "TVA declarat diferă de contabilitate"),
                          ("d112_incrucisat", "Salarii declarate diferă de contabilitate"),
                          ("d390_incrucisat", "Operațiuni intracomunitare declarate diferă de evidență"),
                          ("cota_tva_conformitate", "Facturi emise cu cotă TVA greșită pentru perioadă")):
            vd = vc.get(cheie) or {}
            if vd.get("stare") == "rosu":
                prima = next((c for c in (vd.get("constatari") or []) if c.get("stare") == "rosu"), {})
                contabil.append(_flag_constatare(prima.get("stare"), et, prima.get("mesaj"), prima.get("temei"), an, luna, prima.get("remediu")))
    except Exception as e:
        _verificator_esuat(contabil, "Verificări contabile — eșuate",
                           "verificările contabile (echilibru, trezorerie, declarație vs contabilitate)",
                           e, an, luna)
    try:  # stocuri contabil vs fise CV
        vs = verificare_stocuri(tid, ctx)
        if not vs.get("ok", True):
            difs = [c for c in vs.get("conturi", []) if not c.get("ok")]
            mesaj = ("Sold contabil diferit de fișele CV pe conturile: " + ", ".join(c["cont"] for c in difs) + "."
                     if difs else "Soldul contabil diferă de fișele de magazie CV.")
            # verificare_stocuri NU declara `nivel` (cauze legitime) -> stare_din_nivel(None)=gri. Vezi DECIZII 23.07.
            contabil.append(_flag_constatare(stare_din_nivel(vs.get("nivel")), "Diferențe stocuri", mesaj, vs.get("nota"), an, luna))
    except Exception as e:
        _verificator_esuat(contabil, "Verificare stocuri — eșuată", "stocurile (sold contabil vs fișe CV)", e, an, luna)
    try:  # praguri Intrastat
        ip = intrastat_praguri(tid, an, ctx)
        fluxuri = [nume for nume in ("introduceri", "expedieri") if ip[nume]["status"] != "sub_prag"]
        if fluxuri:
            # Intrastat declara nivel=AVERTISMENT (intrastat.NIVEL_STATUS) -> galben prin stare_din_nivel.
            contabil.append(_flag_constatare(stare_din_nivel(ip.get("nivel")), "Prag Intrastat depășit",
                                             "Prag Intrastat depășit pe: " + ", ".join(fluxuri) + ".",
                                             ip.get("nota"), an, luna))
    except Exception as e:
        _verificator_esuat(contabil, "Verificare Intrastat — eșuată", "pragurile Intrastat", e, an, luna)
    # [F180] regim TVA local vs snapshot ANAF (constatare structurata deja produsa de evalueaza_firma)
    rta = regim_tva_anaf or {}
    if rta.get("stare") == "rosu":
        contabil.append(_flag_constatare(rta.get("stare"), "Regim TVA diferă de ANAF", rta.get("mesaj"), rta.get("temei"), an, luna, rta.get("remediu")))
    return contabil, vc


@app.get("/control-fiscal")
def control_fiscal_portofoliu(ctx=Depends(cere_cabinet)):
    """Semafor pentru toate firmele cabinetului + sumar (verde/galben/rosu)."""
    azi = azi_ro()   # [fus] verdict semafor per firma (la termen/intarziat) = zi RO, robust la OS TZ
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
        # Constatarile contabile: functie PARTAJATA cu detaliul (aceeasi severitate, oricine intreaba).
        contabil, _vc = _construieste_contabil(schema, tid, ctx, azi.year, azi.month, r.get("regim_tva_anaf"))
        # Pastila-firma = escaladare unica din constatari (nu poate depasi severitatea lor maxima).
        r["stare"] = pastila_firma(r["stare"], contabil)
        sumar[r["stare"]] = sumar.get(r["stare"], 0) + 1
        out.append({"tenant_id": tid, "nume": f.get("nume"), "cui": f.get("cui"),
                    "stare": r["stare"], "lipsa": len(r["lipsa"]), "urmarit": len(r["urmarit"]),
                    # [eticheta_din_fapt 20.08.2026] fara numarul de neverificabile, lista nu poate
                    # spune DE CE e o firma gri - si afisa un text fix ("vector necompletat") care e
                    # fals cand vectorul e complet. Rosu si galben poarta deja numarul lor.
                    "neclar": len(r.get("neclar") or []),
                    "contabil": contabil})
    return {"firme": out, "sumar": sumar}


@app.get("/control-fiscal/{tenant_id}")
def control_fiscal_detaliu(tenant_id: int, ctx=Depends(cere_cabinet)):
    """Detaliu conformare pentru o firma: lista lipsa + de urmarit + constatari contabile."""
    azi = azi_ro()   # [fus] verdict de zi = zi RO (acelasi ca portofoliul)
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as cs, db.get_conn() as cp:
        r = control_fiscal_api.evalueaza_firma(cs, cp, tenant_id, schema, azi)
    try:  # cf_verificari_v1 — ACEEASI functie partajata ca lista: severitatea (pastila_firma) e identica.
        contabil, vc = _construieste_contabil(schema, tenant_id, ctx, azi.year, azi.month, r.get("regim_tva_anaf"))
        r["verificari_contabile"] = vc
        r["contabil"] = contabil
        # [P4 21.08.2026] Fiecare verificator isi declara SINGUR limita; sectiunea o aduna, n-o
        # repovesteste. Fara asta, limitele apar doar cand exista o constatare - adica dispar exact
        # cand verdictul e cel mai usor de citit gresit.
        r["limite"] = list(r.get("limite") or []) + [
            {"fel": "acoperire", "text": v["limita"], "sursa": k}
            for k, v in sorted((vc or {}).items())
            if isinstance(v, dict) and v.get("limita")]
        # Headerul de detaliu nu poate fi mai bun decat ce e sub el: pastila_firma peste constatari (ex.
        # trezorerie BLOCANT -> nu mai poate ramane "la zi" cu rosu dedesubt). Vezi DECIZII 23.07.
        r["stare"] = pastila_firma(r["stare"], contabil)
    except Exception:
        pass
    return r


@app.get("/supervizor")
def supervizor_la_cerere(ctx=Depends(cere_cabinet)):
    """SUPERVIZORUL, rulat LA CERERE pe firmele utilizatorului curent.

    **Al doilea declanșator**, lângă cel de la 08:00 *(Costin, 01.09.2026: „extinde cronul de 08:00
    care există. Plus rulare la cerere. Nu construi al doilea mecanism")*. Amândouă cheamă ACEEAȘI
    funcție — `supervizor.ruleaza_portofoliu` —, deci nu există două definiții ale aceleiași
    propoziții. Ce diferă e **domeniul**, și el se declară.

    **Recalculează la fiecare cerere; nu persistă nimic**, exact ca `/control-fiscal`. *„Constatări
    deschise" = ce produce rularea curentă* (Costin). Un ciclu de viață — apărut la · încă deschisă —
    își va avea contractul lui când va avea consumator (stratul asistentului, urmărirea performanței);
    nu înainte.

    **DOMENIUL DE AICI NU E CEL AL SUPERVIZORULUI, ȘI DE-AIA SE SCRIE.** Motorul rulează pe tot
    portofoliul; un om vede **firmele lui**. Fără numele domeniului în răspuns, cifra „N firme" s-ar
    citi ca portofoliul întreg — de-aia `ruleaza_portofoliu` RIDICĂ dacă i se dau firme fără să i se
    spună ce sunt.
    """
    azi = azi_ro()   # [fus] perioada evaluată = zi RO, ca la /control-fiscal și ca în cronul de 08:00
    with db.get_conn() as conn:
        ale_mele = auth_api.tenantii_userului(conn, ctx["uid"])
    firme = []
    for f in ale_mele:
        tid = f.get("id")
        with db.get_conn() as c:
            schema = auth_api.schema_tenant(c, ctx["uid"], tid)
        if not schema:
            continue   # fara acces la tenant — nu se afiseaza (identic cu semaforul /control-fiscal)
        firme.append({"tenant_id": tid, "schema": schema, "nume": f.get("nume")})
    r = supervizor.ruleaza_portofoliu(
        azi.year, azi.month, firme=firme,
        domeniu=("firmele la care are acces utilizatorul curent (%d), NU tot portofoliul; "
                 "supervizorul rulează zilnic pe portofoliu, ecranul arată partea ta" % len(firme)))
    # `schema` e detaliu intern de stocare: nu iese pe rută (nici semaforul nu-l dă).
    r["firme"] = [{k: v for k, v in rand.items() if k != "schema"} for rand in r["firme"]]
    return r


@app.post("/control-fiscal/{tenant_id}/audit-preluare")
# [R45] POST: auditul e declansat de un buton, deci e un ACT — iar verdictul lui se pastreaza.
# Un GET n-are voie sa scrie (interdictia 6).
def control_fiscal_audit_preluare(tenant_id: int, ctx=Depends(cere_rol("admin_firma"))):
    """F183: audit de PRELUARE firma — coerenta INTERNA a pachetului preluat de la contabilul anterior
    (balanta echilibrata, defalcare parteneri vs sintetic, solduri fiscale vs istoric declaratii, RIP la
    PFA). Motor separat (core/audit_preluare), NU control_incrucisat: la preluare ambele surse sunt EXTERNE.
    Repetabil, datat cu momentul rularii — gri-urile trec in verde/rosu pe masura ce apar documentele."""
    import datetime
    from core import audit_preluare
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as cs, db.get_conn() as cp:
        r = audit_preluare.audit(cs, schema, tenant_id, cp)
        with cp.cursor() as cur:  # creat_la = de cand e firma in iConta sub cabinet (proxy preluare)
            cur.execute("SELECT creat_la FROM public.tenants WHERE id=%s", (tenant_id,))
            row = cur.fetchone()
    r["data"] = datetime.datetime.now().isoformat(timespec="minutes")  # cu ora: doua rulari/zi se disting
    r["in_iconta_din"] = row[0].date().isoformat() if row and row[0] else None  # data simpla (scara = luni)
    # [R45] Verdictul se pastreaza: continut (verdictul intreg, serializat), moment, autor,
    # amprenta, numar de exemplar. Cheia e ANUL rularii — doua audituri in ani diferiti sunt
    # doua artefacte, doua in aceeasi zi sunt exemplarul 1 si 2 ale aceluiasi.
    try:
        import json as _json
        from core import artefacte as _art
        with db.get_conn(schema) as _c:
            _art.pastreaza(_c, schema, "audit_preluare", str(datetime.date.today().year),
                           _json.dumps(r, ensure_ascii=False, default=str),
                           produs_de_id=int(ctx["uid"]),
                           produs_de=ctx.get("nume") or str(ctx["uid"]))
    except Exception as _e:
        import logging
        logging.getLogger("iconta").warning("[R45] audit de preluare nepastrat: %s", _e)
    return r



# ============================================================
#  TERMENE — scadente viitoare pe portofoliu (orizont 60 zile)
# ============================================================
@app.get("/termene")
def termene_portofoliu(ctx=Depends(cere_cabinet)):
    """Scadente viitoare grupate pe data + tip, cu numarul de firme."""
    azi = azi_ro()   # [fus] fereastra scadentelor = verdict (ce vede contabilul), zi RO
    with db.get_conn() as conn:
        firme = auth_api.tenantii_userului(conn, ctx["uid"])
    firme_eval = []
    neevaluate = []   # [T1] firme care nu au putut fi evaluate — NU dispar tacut (gri cu temei, ca semaforul)
    for f in firme:
        tid = f.get("id")
        try:
            with db.get_conn() as c:
                schema = auth_api.schema_tenant(c, ctx["uid"], tid)
            if not schema:
                continue   # fara acces la tenant — nu se afiseaza (identic cu semaforul /control-fiscal)
            with db.get_conn(schema) as cs:
                with cs.cursor() as cur:
                    cur.execute("SELECT regim_fiscal, platitor_tva, tip_decont, operatiuni_ic, tip_firma, "
                                "platitor_tva_anaf_inceput, inreg_art317 FROM firma_profil LIMIT 1")
                    row = cur.fetchone()
                    from core.migrare_api import regim_contabil
                    vector = {"regim_fiscal": row[0], "platitor_tva": row[1],
                              "tip_decont": row[2], "operatiuni_ic": row[3],
                              "tip_firma": row[4],
                              # [T2] partida_simpla din primitiva UNICA (ca semaforul) -> motorul nu emite D100/D101/D406 la PFA.
                              "partida_simpla": regim_contabil(row[4]) == "simpla",
                              # [§4] data inceperii inregistrarii TVA (fapt ANAF) -> motorul margineste D300/D394/D406
                              # la perioadele DE DUPA inregistrare (marginit=True), ca semaforul. Inchide asimetria intre ecrane.
                              "tva_data_inceput": row[5], "inreg_art317": row[6]} if row else {}
                    cur.execute("SELECT to_regclass('salariati')")
                    are_sal = False
                    if cur.fetchone()[0]:
                        cur.execute("SELECT count(*) FROM salariati WHERE (data_incetare IS NULL OR data_incetare >= CURRENT_DATE) AND (data_angajare IS NULL OR data_angajare <= CURRENT_DATE)")
                        are_sal = cur.fetchone()[0] > 0
                if not vector:
                    # [T1] firma exista dar vectorul fiscal e gol -> nu se ascunde: gri cu temei (ca evalueaza_firma)
                    # [P8] NECUNOASTERE declarata, nu o cauza in proza: „nu pot evalua" e o afirmatie
                    # despre firma, si trebuie sa spuna PE CE perioada nu poate - altfel peste sase
                    # luni se citeste ca fapt permanent.
                    _n = _af.afirmatie(
                        "necunoastere", "obligații fiscale",
                        "Vector fiscal necompletat — nu pot evalua obligațiile firmei.",
                        domeniu_de=azi.isoformat(), domeniu_pana=azi.isoformat())
                    _n["tenant_id"] = tid
                    _n["nume"] = f.get("nume")
                    _n["cauza"] = _n["motiv"]
                    neevaluate.append(_n)
                    continue
                with db.get_conn() as cp:
                    with cp.cursor() as cur:
                        cur.execute("SELECT tip, an, luna FROM public.declaratii_depuse_curente WHERE tenant_id=%s", (tid,))  # [F163v2] vederea = depunerea curentă
                        depuse = {(t, a, l) for (t, a, l) in cur.fetchall()}
                # [D390-fapt] termene intreaba faptul lunar prin cs (conn pe schema firmei, cat timp e deschis):
                # luna deschisa -> AFISAM (nu putem exclude operatiuni pana la finalul lunii); vezi obligatii_datorate.
                from core import d390 as _d390
                _fapt = lambda a, l: _d390.d390_are_operatiuni(cs, schema, a, l, azi)
                term = termene_api.termene_firma(vector, are_sal, depuse, azi, d390_fapt=_fapt)
                # [P2] deschideFirma->meniuFirma cere {id, nume, cui, tip_firma} + [regim_card] regim_contabil
                # (contract STRICT in meniuFirma pe amandoua). Le avem din firma_profil (vector) prin primitiva.
                firme_eval.append({"tenant_id": tid, "nume": f.get("nume"), "cui": f.get("cui"),
                                   "tip_firma": vector.get("tip_firma"),
                                   "regim_contabil": regim_contabil(vector.get("tip_firma")), "termene": term})
        except Exception as e:
            # [T1] o firma care crapa NU dispare din ecran: gri cu temei (doctrina 23.07 — gri = "nu am putut", nu tacere).
            # [item4] numele tehnic al exceptiei merge DOAR in log (%r); pe ecran - temei citibil pentru contabil (DS cap.6).
            _LOG_VERDICT.warning("termene: evaluare esuata tenant %s -> gri (%r)", tid, e)
            # [P8] VERIFICARE RUPTA, nu necunoastere: masinaria a crapat, iar asta se spune ca atare -
            # altfel se amesteca pe ecran cu „nu am date", si nimeni nu mai stie unde sa se uite.
            # `eroare` sta in obiect pentru diagnostic; pe ecran ramane `cauza`, in limba omului.
            _n = _af.afirmatie(
                "verificare_rupta", "obligații fiscale",
                "Nu am putut evalua această firmă acum — a apărut o eroare internă. "
                "Am notat-o; reîncearcă mai târziu sau anunță suportul.",
                eroare="%s: %s" % (type(e).__name__, e))
            _n["tenant_id"] = tid
            _n["nume"] = f.get("nume")
            _n["cauza"] = _n["motiv"]
            neevaluate.append(_n)
    return termene_api.portofoliu(firme_eval, azi, neevaluate)



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


def _anaf_tva_check(cui, valoare_manuala):
    """[F180] Live ANAF v9 pe CUI. Întoarce (anaf_val|None, avertisment|None, tva_data_inceput|None). NU atinge
    DB și NU ridică niciodată (ANAF jos/notFound -> (None,None,None), salvarea trece — signal-not-block).
    anaf_val None = ANAF necunoscut -> snapshot NU se reîmprospătează. [B1] data inceperii inregistrarii TVA."""
    try:
        c = (cui or "").replace("RO", "").strip()
        if not c:
            return None, None, None
        rez = anaf_api.valideaza_cui([c])
        if not (rez and rez[0].get("gasit")):
            return None, None, None
        anaf_val = bool(rez[0].get("platitor_tva"))
        return anaf_val, _fp.avertisment_tva_anaf(valoare_manuala, anaf_val), rez[0].get("tva_data_inceput")
    except Exception:
        return None, None, None

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
def produse_creeaza(tenant_id: int, date: ProdusCreeazaIn, ctx=Depends(cere_cabinet)):  # [rol_produse 27.07.2026] DECIS 24.07: scrierea e de cabinet
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
                         ctx=Depends(cere_cabinet)):  # [rol_produse 27.07.2026]
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
def produse_sterge(tenant_id: int, produs_id: int, ctx=Depends(cere_cabinet)):  # [rol_produse 27.07.2026]
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
# [R42] Seria documentelor emise: o schimbare aici lasa goluri intr-o numerotare (interdictia 35).
def facturi_numerotare_set(tenant_id: int, date: NumerotareIn,
                           ctx=Depends(cere_rol("admin_firma"))):
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        r = facturi_api.seteaza_numerotare(conn, serie=date.serie, numar_start=date.numar_start)
    if not r.get("ok"):
        raise HTTPException(400, r.get("mesaj", "eroare"))
    return r

@app.get("/tenants/{tenant_id}/scadentar")
def scadentar_get(tenant_id: int, ctx=Depends(cere_context)):
    """F131: scadentarul facturilor emise neincasate (restante/scade curand/in termen)
    + fisa client agregata. Read-only, fara schema noua."""
    from core import scadentar as _sc
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        return _sc.pull(conn, schema)

class OptInScadentarIn(BaseModel):
    activ: bool

@app.put("/tenants/{tenant_id}/scadentar/opt-in")
def scadentar_optin(tenant_id: int, date: OptInScadentarIn,
                    ctx=Depends(cere_rol("admin_firma"))):
    """F131: activeaza/dezactiveaza notificarile email de scadenta pt firma (default OFF)."""
    from core import scadentar as _sc
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        r = _sc.seteaza_optin(conn, date.activ)
    if not r.get("ok"):
        raise HTTPException(422, r.get("mesaj", "eroare"))
    return r

class SupapaScadentarIn(BaseModel):
    stop: bool = False
    amanata_pana: Optional[str] = None

@app.put("/tenants/{tenant_id}/facturi/{factura_id}/notificare")
def scadentar_supapa(tenant_id: int, factura_id: int, date: SupapaScadentarIn,
                     ctx=Depends(cere_rol("admin_firma"))):
    """F131: supapa per factura - nu notifica (stop) / amana pana la data X."""
    from core import scadentar as _sc
    schema = _schema_sau_404(ctx, tenant_id)
    try:
        with db.get_conn(schema) as conn:
            r = _sc.seteaza_supapa(conn, factura_id, stop=date.stop,
                                   amanata_pana=date.amanata_pana)
    except ValueError as e:   # [lot 2] data amanarii invalida: mesaj, nu 500
        raise HTTPException(422, str(e))
    if not r.get("ok"):
        raise HTTPException(404, "factură inexistentă")
    return r

@app.get("/util/zile-lucratoare")
def util_zile_lucratoare(start: str, end: str, ctx=Depends(cere_context)):
    """Zile lucratoare (L-V, fara sarbatori legale) intre doua date - auto-calcul CM
    (OUG 158/2005 art.10). Un an neacoperit de calendar da 422 vizibil, nu tacut."""
    from core import scadente as _scad
    from datetime import date as _d
    try:
        return {"zile": _scad.zile_lucratoare_interval(_d.fromisoformat(start), _d.fromisoformat(end))}
    except ValueError as ex:
        raise HTTPException(422, str(ex))

class ModelFacturaIn(BaseModel):
    font: Optional[str] = None
    culoare: Optional[str] = None
    logo: Optional[str] = None      # data URI base64; "" sterge; None = nu schimba

@app.get("/tenants/{tenant_id}/firma-profil")
def firma_profil_get(tenant_id: int, ctx=Depends(cere_context)):
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        return _fp.citeste_profil(conn)

class RegimTvaIn(BaseModel):
    platitor_tva: bool

@app.post("/tenants/{tenant_id}/firma-profil/regim-tva")  # [tva_config_v1] setat la Configurare emitere
# [R42 (c)] Criteriul adăugat de Costin: *ce schimbă CE DATOREAZĂ firma cere `admin_firma`*.
# Nu e o ieșire — nu pleacă nimic — dar `platitor_tva` decide dacă firma datorează D300/D394 și
# pe ce perioade. O schimbare greșită nu produce o eroare vizibilă: produce declarații care nu se
# mai depun, sau se depun greșit.
def firma_profil_regim_tva(tenant_id: int, date: RegimTvaIn, ctx=Depends(cere_rol("admin_firma"))):
    schema = _schema_sau_404(ctx, tenant_id)
    # [F180] CUI din public.tenants -> apel ANAF live FARA a tine conexiunea pe schema
    with db.get_conn() as cpub:
        with cpub.cursor() as cur:
            cur.execute("SELECT cui FROM public.tenants WHERE id = %s", (tenant_id,))
            row = cur.fetchone()
    anaf_val, avert, tva_inceput = _anaf_tva_check(row[0] if row else None, date.platitor_tva)
    with db.get_conn(schema) as conn:
        # [R46] `platitor_tva` decide daca firma datoreaza D300/D394 si pe ce perioade.
        try:
            _fp.cere_perioade_deschise(conn, "Regimul de TVA")
        except ValueError as e:
            raise HTTPException(422, str(e))
        with conn.cursor() as cur:
            cur.execute("UPDATE firma_profil SET platitor_tva = %s", (date.platitor_tva,))
        if anaf_val is not None:                      # ANAF a raspuns -> reimprospateaza snapshot (+ data inceput TVA)
            _fp.seteaza_snapshot_tva(conn, anaf_val, tva_inceput)
        conn.commit()
    r = {"ok": True, "platitor_tva": date.platitor_tva}
    if avert:                                          # divergenta -> informeaza, nu blocheaza
        r["avertisment"] = avert
    return r

@app.get("/tenants/{tenant_id}/firma-profil/date")  # [date_firma_v1]
def firma_profil_date(tenant_id: int, ctx=Depends(cere_context)):
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        return _fp.citeste_date(conn)


@app.post("/tenants/{tenant_id}/firma-profil/date")  # [date_firma_v1]
def firma_profil_date_salveaza(tenant_id: int, date: dict = Body(...),
                               ctx=Depends(cere_cabinet)):
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        r = _fp.salveaza_date(conn, date, tenant_id=tenant_id)
    if not r.get("ok"):
        raise HTTPException(422, r.get("mesaj", "date invalide"))
    return r


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
    try:
        pdf = _pdf.genereaza_pdf(profil, f)
    except ValueError as e:
        # [bilant_422_v1] refuzul motivat al generatorului de PDF (ex. linie fara cota TVA)
        # ajungea la contabil ca 500 gol. Gasit de core/test_refuz_generator_422.py.
        raise HTTPException(422, str(e))
    nume = "factura_" + str(f.get("numar") or factura_id).replace("/", "-") + ".pdf"
    return Response(content=pdf, media_type="application/pdf",
                    headers={"Content-Disposition": f'inline; filename="{nume}"'})

class EmailFacturaIn(BaseModel):
    email: str
    mesaj: Optional[str] = None

@app.post("/tenants/{tenant_id}/facturi/{factura_id}/email")
# [R42] Trimiterea către client: „iese către un om". Un email plecat nu se poate reface.
def factura_email(tenant_id: int, factura_id: int, date: EmailFacturaIn,
                  ctx=Depends(cere_rol("admin_firma"))):
    schema = _schema_sau_404(ctx, tenant_id)
    email = (date.email or "").strip()
    if "@" not in email or "." not in email:
        raise HTTPException(422, EMAIL_INVALID)
    with db.get_conn(schema) as conn:
        f = facturi_api.detalii_factura(conn, factura_id)
        if not f:
            raise HTTPException(404, "factură inexistentă")
        profil = _fp.citeste_profil(conn)
    import base64 as _b64
    try:
        pdf = _pdf.genereaza_pdf(profil, f)
    except ValueError as e:
        # [bilant_422_v1] refuzul motivat al generatorului de PDF (ex. linie fara cota TVA)
        # ajungea la contabil ca 500 gol. Gasit de core/test_refuz_generator_422.py.
        raise HTTPException(422, str(e))
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

@app.get("/tenants/{tenant_id}/facturi-recurente")
def fr_lista(tenant_id: int, ctx=Depends(cere_context)):
    from core import facturi_recurente as _fr
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn() as conn:
        return {"sabloane": _fr.lista(conn, schema)}

@app.post("/tenants/{tenant_id}/facturi-recurente")
def fr_adauga(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_context)):
    from core import facturi_recurente as _fr
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn() as conn:
        r = _fr.adauga(conn, schema, corp)
    if r.get("eroare"):
        _ec = r.get("erori_campuri")  # [G10] contract {mesaj, erori_campuri}
        raise HTTPException(422, detail={"mesaj": r["eroare"], "erori_campuri": _ec} if _ec else r["eroare"])
    return r

@app.put("/tenants/{tenant_id}/facturi-recurente/{sid}")
def fr_comuta(tenant_id: int, sid: int, activ: bool, ctx=Depends(cere_context)):
    from core import facturi_recurente as _fr
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn() as conn:
        r = _fr.comuta(conn, schema, sid, activ)
    if r.get("eroare"):
        raise HTTPException(404, r["eroare"])
    return r

@app.delete("/tenants/{tenant_id}/facturi-recurente/{sid}")
def fr_sterge(tenant_id: int, sid: int, ctx=Depends(cere_context)):
    from core import facturi_recurente as _fr
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn() as conn:
        r = _fr.sterge(conn, schema, sid)
    if r.get("eroare"):
        raise HTTPException(404, r["eroare"])
    return r

@app.post("/tenants/{tenant_id}/facturi/emite")
# [R42] „emiterea unui document" — factura primește număr din serie și ajunge la un om.
def facturi_emite(tenant_id: int, date: EmitereIn, ctx=Depends(cere_rol("admin_firma"))):
    schema = _schema_sau_404(ctx, tenant_id)
    linii = [l.model_dump() for l in date.linii]
    if not (date.tert_nume or "").strip():
        raise HTTPException(422, "Denumirea beneficiarului e obligatorie pe factură. Completeaz-o înainte de emitere.")
    with db.get_conn(schema) as conn:
        are_stoc = any(l.get("articol_id") for l in linii)
        # poarta doar la FACTURA (nu proforma/aviz), la firma CV cu linie de stoc
        poarta_ceruta = (date.tip == "factura") and are_stoc
        if poarta_ceruta and date.pleaca_marfa is None:
            raise HTTPException(422, "Raspunde la poarta: pleaca marfa acum? (DA descarca gestiunea / NU doar fiscal)")
        platitor = _platitor_tva_firma(conn)
        try:
            r = facturi_api.emite_factura(
                conn, linii, client_id=date.client_id, tert_nume=date.tert_nume,
                tert_cui=date.tert_cui, tert_adresa=date.tert_adresa, data_emitere=date.data_emitere,
                data_scadenta=date.data_scadenta, moneda=date.moneda,
                platitor_tva=platitor, curs_manual=date.curs_manual, tip=date.tip,
                tert_tara=date.tert_tara, tip_operatiune=date.tip_operatiune,
                data_curs_manual=date.data_curs_manual,
                # [R130] „consemnat cine și când" — autorul vine din context, nu din corp: cine
                # trimite cererea nu poate scrie în locul altcuiva cine a ales cursul.
                curs_manual_de="utilizator %s" % ctx["uid"])
        except facturi_api.LiniiIncomplete as e:
            raise HTTPException(422, {"cod": "LINII_INCOMPLETE",
                "mesaj": "Completează liniile: " + "; ".join(x["eticheta"] for x in e.campuri),
                "campuri": e.campuri})
        except ValueError as e:
            raise HTTPException(422, str(e))
        # descarcare gestiune DOAR la poarta = DA, in ACEEASI tranzactie (atomic: emit + descarcare)
        if poarta_ceruta and date.pleaca_marfa is True and isinstance(r, dict) and r.get("factura_id"):
            from core import stocuri_cv_api as _cv
            from datetime import date as _dt_date  # fix F821: datetime neimportat in scope (date = param Pydantic)
            r["descarcare"] = _cv.descarca_factura(conn, schema, r["factura_id"],
                                                   date.data_emitere or _dt_date.today().isoformat())
    # [lot 2] moneda inexistenta e o INTRARE gresita (422), nu un conflict temporar (409):
    # 409 cu „reincearca / manual" ii promitea contabilului ca mai tarziu ar merge.
    if isinstance(r, dict) and r.get("ok") is False and r.get("cod") == "MONEDA_NECOTATA":
        raise HTTPException(422, detail=r)
    # [R130] Cursul e mai vechi decat pragul: emiterea AUTOMATA se opreste, facturarea NU. `409`,
    # cu iesirea numita in corp (curs manual + data lui) — un refuz fara iesire ar fi interdictia 47.
    if isinstance(r, dict) and r.get("ok") is False and r.get("cod") == "CURS_PREA_VECHI":
        raise HTTPException(409, detail=r)
    # curs BNR indisponibil -> 409 cu detaliile pt frontend (Reincearca / Manual)
    if isinstance(r, dict) and r.get("ok") is False and r.get("cod") == "CURS_INDISPONIBIL":
        raise HTTPException(409, detail=r)
    return r

@app.post("/tenants/{tenant_id}/facturi/{factura_id}/storno")
# [R42] Stornarea nu corectează documentul emis — emite AL DOILEA document (P4).
def facturi_storno(tenant_id: int, factura_id: int, ctx=Depends(cere_rol("admin_firma"))):
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        try:
            r = facturi_api.storneaza(conn, factura_id)
        except ValueError as e:
            raise HTTPException(422, str(e))
    return r

# ICRD_PUBLIC_VERIFICA_CUI_V1
@app.get("/public/verifica-cui/{cui}")
def public_verifica_cui(cui: str, request: Request):
    _rate_limit_email(_cui_rate, request, maxreq=10)  # [verifica_cui_v1] protejeaza cheia ANAF (10/15min per IP)
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
    # [F180] apel ANAF live pe CUI INAINTE de a deschide conexiunea pe schema
    anaf_val, avert, tva_inceput = _anaf_tva_check(t_cui, date.platitor_tva)
    with db.get_conn(schema) as conn:
        rez = vector_fiscal_api.salveaza(conn, date.regim_fiscal, date.platitor_tva,
                                         date.tip_decont, date.operatiuni_ic,
                                         nume=t_nume, cui=t_cui, inreg_art317=date.inreg_art317,
                                         tva_data_inceput=date.tva_data_inceput)  # [tva_inceput] data manuala INTAI
        # [tva_inceput] ANAF autoritar CAND are data: seteaza_snapshot_tva o suprascrie. Cand ANAF nu raspunde
        # (anaf_val None, gasit=False) NU se cheama deloc -> data manuala ramane. Cand ANAF raspunde dar NU are
        # data (tva_inceput None), guard-ul din seteaza_snapshot_tva NU goleste coloana -> data manuala ramane.
        if rez.get("ok") and anaf_val is not None:     # salvat + ANAF a raspuns -> snapshot (+ data inceput TVA)
            _fp.seteaza_snapshot_tva(conn, anaf_val, tva_inceput)
    if not rez.get("ok"):
        _mesaj = rez.get("mesaj", "vector invalid")
        _camp = rez.get("camp")
        if _camp:   # Regula 14.4 pct.4: marcheaza campul vinovat, nu doar mesaj generic
            raise HTTPException(400, {"mesaj": _mesaj, "erori_campuri": [{"camp": _camp, "mesaj": _mesaj}]})
        raise HTTPException(400, _mesaj)
    if avert:                                          # divergenta -> informeaza, nu blocheaza
        rez["avertisment"] = avert
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
                  limit: Optional[int] = None, offset: int = 0,
                  ctx=Depends(cere_context)):
    schema = _schema_sau_404(ctx, tenant_id)
    try:
        with db.get_conn(schema) as conn:
            return {"facturi": facturi_api.lista_facturi(conn, an, luna, directie,
                                                         limit=limit, offset=offset)}
    except ValueError as e:   # [lot 2] filtru invalid: mesaj, nu 500 si nu lista goala tacuta
        raise HTTPException(422, str(e))


@app.post("/tenants/{tenant_id}/facturi")
# [R42] A doua cale de creare a facturii (vezi R14: două funcții, stări implicite diferite).
# Amândouă produc un document numerotat, deci amândouă intră la „emiterea unui document".
def factura_creeaza(tenant_id: int, date: FacturaIn,
                    ctx=Depends(cere_rol("admin_firma"))):
    schema = _schema_sau_404(ctx, tenant_id)
    linii = [l.model_dump() for l in date.linii]
    try:
        with db.get_conn(schema) as conn:
            r = facturi_api.creeaza_factura(
                conn, date.numar, date.data_emitere, date.directie, linii,
                client_id=date.client_id, tert_nume=date.tert_nume,
                tert_cui=date.tert_cui, data_scadenta=date.data_scadenta,
                moneda=date.moneda, status=date.status,
                tert_tara=date.tert_tara, tip_operatiune=date.tip_operatiune,
                furnizor_tva_incasare=date.furnizor_tva_incasare)
    except ValueError as e:
        raise HTTPException(422, str(e))
    return r


@app.post("/tenants/{tenant_id}/facturi/{factura_id}/transforma")
def proforma_transforma(tenant_id: int, factura_id: int, ctx=Depends(cere_rol("admin_firma"))):
    """Transforma proforma/aviz in factura fiscala (numerotare noua, nota se genereaza normal)."""
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT tip, transformat_in_id FROM facturi WHERE id=%s", (factura_id,))
            r = cur.fetchone()
        if not r:
            raise HTTPException(404, "document inexistent")
        if r[0] == "factura":
            raise HTTPException(422, "documentul e deja factura")
        if r[1]:
            raise HTTPException(409, f"deja transformat in factura #{r[1]}")
        f = facturi_api.detalii_factura(conn, factura_id)
        linii = [{"descriere": l.get("descriere"), "cantitate": l.get("cantitate"),
                  "pret_unitar": l.get("pret_unitar"), "cota_tva": l.get("cota_tva")}
                 for l in (f.get("linii") or [])]
        platitor = _platitor_tva_firma(conn)
        try:
            rez = facturi_api.emite_factura(conn, linii, client_id=f.get("client_id"),
                tert_nume=f.get("tert_nume"), tert_cui=f.get("tert_cui"),
                moneda=f.get("moneda") or "RON", platitor_tva=platitor)
        except ValueError as e:
            raise HTTPException(422, str(e))
        with conn.cursor() as cur:
            cur.execute("UPDATE facturi SET transformat_in_id=%s WHERE id=%s",
                        (rez["factura_id"], factura_id))
        conn.commit()
    return rez

@app.get("/tenants/{tenant_id}/facturi/{factura_id:int}")  # [p115_detalii_acces] acces client+gratuit+cabinet
# {factura_id:int} (F187): fara tipare int, ruta asta captura literalele /facturi/export-saga si
# /facturi/export-winmentor (factura_id="export-..."->422 int_parsing), umbrindu-le. Bug latent la SAGA
# month (F171) - export-zip pe luna era nereachable. :int face literalele sa treaca la rutele lor.
def factura_detalii(tenant_id: int, factura_id: int, ctx=Depends(cere_context)):
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        f = facturi_api.detalii_factura(conn, factura_id)
    if not f:
        raise HTTPException(404, "factură inexistentă")
    return f


@app.delete("/tenants/{tenant_id}/facturi/{factura_id}")
# [R42] „ștergerea a ceva emis" — o factură ștearsă lasă un gol în serie (interdicția 35).
def factura_sterge(tenant_id: int, factura_id: int,
                   ctx=Depends(cere_rol("admin_firma"))):
    """[EEE2] Refuzul e EXPLICAT, nu o eroare de bază: `409`, cu numărul notei și cu ieșirea numită
    (storno). Fără el, cu note automate, ștergerea ar fi început să pice pe cheia străină
    `inregistrari_factura_id_fkey`, care n-are `ON DELETE`."""
    from core import contare_facturi as _cf
    schema = _schema_sau_404(ctx, tenant_id)
    try:
        with db.get_conn(schema) as conn:
            return facturi_api.sterge_factura(conn, factura_id)
    except _cf.RefuzContare as e:
        raise HTTPException(409, e.mesaj)


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
        _ec = getattr(e, "erori_campuri", None)  # [G10] contract {detail, erori_campuri}
        raise HTTPException(422, detail={"mesaj": str(e), "erori_campuri": _ec} if _ec else str(e))


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
    # [R51] `None` inseamna doua lucruri diferite: „n-am trimis campul" si „goleste-l".
    # `exclude_unset` le separa — ce a trimis clientul EXPLICIT cu null e o golire ceruta.
    trimise = date.model_dump(exclude_unset=True)
    golite = [k for k, v in trimise.items() if v is None]
    try:
        with db.get_conn(schema) as conn:
            return salariati_api.actualizeaza_salariat(conn, salariat_id,
                                                       _golite=golite, **date.model_dump())
    except ValueError as e:
        _ec = getattr(e, "erori_campuri", None)  # [G10] contract {detail, erori_campuri}
        raise HTTPException(422, detail={"mesaj": str(e), "erori_campuri": _ec} if _ec else str(e))


@app.get("/cor")
def cor_cauta(q: str = "", ctx=Depends(cere_context)):
    """[F137] Cauta in nomenclatorul COR national dupa cod (prefix) sau denumire (substring,
    diacritic-insensitiv). Pt lookup-ul de ocupatie pe contract/salariat. Orice user logat."""
    from core import cor_api
    with db.get_conn() as conn:
        return {"rezultate": cor_api.cauta(conn, q)}


@app.put("/tenants/{tenant_id}/salariati/{salariat_id}/beneficiu-lunar")
def salariat_beneficiu_lunar(tenant_id: int, salariat_id: int, corp: dict = Body(...),
                             ctx=Depends(cere_rol("admin_firma", "angajat"))):
    """[F133 Faza 2a] beneficiu one-off pe luna (vacanta/cadou/cultural) - upsert; 0 = sterge."""
    from core import beneficii_api as _ben
    an, luna = corp.get("an"), corp.get("luna")
    if not isinstance(an, int) or not isinstance(luna, int) or luna < 1 or luna > 12:
        raise HTTPException(400, "an/luna invalide")
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        r = _ben.seteaza(conn, schema, salariat_id, an, luna, corp.get("tip"), corp.get("valoare"),
                         eveniment=corp.get("eveniment", ""), nr_copii=corp.get("nr_copii", 1))
        if r is None:
            raise HTTPException(404, "salariat inexistent")
        if r.get("eroare"):
            raise HTTPException(400, r["eroare"])
        return r


@app.delete("/tenants/{tenant_id}/salariati/{salariat_id}")
def salariat_sterge(tenant_id: int, salariat_id: int,
                    ctx=Depends(cere_rol("admin_firma", "angajat"))):
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        r = salariati_api.sterge_salariat(conn, salariat_id)
    if not r["ok"] and r.get("cod") == "ARE_CONCEDII":
        raise HTTPException(409, r["mesaj"])
    return r


@app.get("/tenants/{tenant_id}/salariati/{salariat_id}/concedii")  # cm_lista_v1
def cm_lista(tenant_id: int, salariat_id: int, an: int = None, ctx=Depends(cere_cabinet)):
    schema = _schema_sau_404(ctx, tenant_id)
    # [lotul 4] `salariat_id=999999` intorcea `{"concedii": []}` — „salariatul asta n-are concedii"
    # arata identic cu „salariatul asta nu exista". Iar `GET /fluturas`, pe ACELASI id inexistent,
    # raspunde `404 salariat inexistent`: aplicatia stia deosebirea intr-un loc si n-o facea in
    # celalalt. `an=1900` intorcea la fel, gol.
    _cere_perioada(an=an)
    with db.get_conn(schema) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM salariati WHERE id=%s", (salariat_id,))
            if not cur.fetchone():
                raise HTTPException(404, "salariat inexistent")
        return {"concedii": salariati_api.lista_concedii(conn, salariat_id, an)}


@app.post("/tenants/{tenant_id}/salariati/{salariat_id}/concedii")  # cm_salveaza_v1
def cm_salveaza(tenant_id: int, salariat_id: int, corp: dict = Body(...),
                ctx=Depends(cere_rol("admin_firma", "angajat"))):
    schema = _schema_sau_404(ctx, tenant_id)
    try:
        with db.get_conn(schema) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM salariati WHERE id=%s", (salariat_id,))
                if not cur.fetchone():
                    raise HTTPException(404, "salariat inexistent")
            return salariati_api.salveaza_concediu(conn, salariat_id, corp)
    except (ValueError, ZeroDivisionError) as e:
        raise HTTPException(422, str(e))


@app.delete("/tenants/{tenant_id}/salariati/{salariat_id}/concedii/{cm_id}")  # cm_sterge_v1
def cm_sterge(tenant_id: int, salariat_id: int, cm_id: int,
              ctx=Depends(cere_rol("admin_firma", "angajat"))):
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        return salariati_api.sterge_concediu(conn, salariat_id, cm_id)


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
    # [F163v2] păstrăm și `res` întreg (serializat) în payload, nu doar avertismente: e singura
    # cale prin care rândurile depuse ajung persistate (marcheaza_depusa le scrie în
    # declaratii_depuse.randuri). d112 -> randuri None (randuri_din_res, temei acolo).
    payload = {"xml": xml,
               "avertismente": (res if isinstance(res, list) else getattr(res, "avertismente", None)),
               "note_rezultat": ([] if isinstance(res, list) else (getattr(res, "note_rezultat", None) or [])),
               "randuri": coada_api.randuri_din_res(res)}
    # 2) POARTA: se VALIDEAZĂ ÎNAINTE de a intra în coadă (decizia lui Costin, 26.08.2026).
    #
    # Până azi coada primea orice se genera, iar validatorul rula abia când cineva deschidea
    # elementul (`GET /coada/{id}/continut`). Poarta exista, dar la DEPUNERE. Consecința: lista
    # pe care ecranul o numește „De depus" putea conține declarații care n-au trecut niciodată
    # prin validator — o afirmație falsă despre propria stare (P13). Cazul care a produs regula
    # e chiar cel din antetul lui `TRASEE.md`: trei declarații în coadă fără verdict, găsite
    # fiindcă cineva a apăsat un buton, nu de vreo măsurătoare.
    #
    # NU se adaugă o a doua rulare de validator în lanț: rularea de aici e cea care oricum se
    # făcea la prima deschidere, mutată mai devreme. Verdictul se PĂSTREAZĂ imediat după
    # inserare, cu amprenta XML-ului validat, deci elementul intră în coadă purtându-l din
    # naștere — nu îl capătă când se uită cineva la el.
    #
    # `gri` (nu am putut valida) NU trece drept favorabil (P6): se refuză la fel ca `erori`.
    # Portița e aceeași ca la aprobare și depunere — `motiv_trecere` scris explicit, care se
    # păstrează. Fără ea, un validator picat ar bloca toată munca; cu ea, trecerea are autor.
    from core import duk as _duk_poarta
    _rez = _duk_poarta.valideaza(xml, date.tip, an=date.an, luna=date.luna) if xml else {
        "stare": "gri", "erori": "", "severitate": None,
        "temei": "Generarea n-a produs XML.", "limita": ""}
    _motiv = (date.motiv_trecere or "").strip()
    if _rez.get("stare") != "valid" and not _motiv:
        # Refuzul poartă CE lipsește, nu doar că lipsește — altfel contabilul află ce are de
        # făcut abia deschizând altceva.
        raise HTTPException(422, detail={
            "mesaj": ("Declarația nu intră în coadă: validatorul oficial a răspuns „%s”."
                      % _rez.get("stare")),
            "stare": _rez.get("stare"), "erori": _rez.get("erori") or "",
            "severitate": _rez.get("severitate"), "temei": _rez.get("temei"),
            "limita": _rez.get("limita"),
            # Mesajul NU numește câmpul intern al cererii (Regula 14 pct.4): contabilul vede
            # ce are de făcut, nu numele coloanei. Câmpul rămâne în contractul API, la `detalii`.
            "actiune": ("Corectează ce semnalează validatorul și generează din nou. Dacă treci "
                        "peste deliberat, scrie motivul trecerii — se păstrează cu numele tău."),
            "camp_trecere": "motiv_trecere"})

    # 3) pune în coadă (pe public), stare 'la_senior'
    with db.get_conn() as conn:
        r = coada_api.adauga_in_coada(
            conn, ctx["firm"], date.tenant_id, date.tip, date.an, payload,
            creat_de=str(ctx["uid"]), creat_de_id=int(ctx["uid"]), luna=date.luna, trim=date.trim,
            inceput_la=date.inceput_la)  # [p15]
    if not r["ok"] and r.get("cod") == "DEJA_IN_COADA":
        raise HTTPException(409, r["mesaj"])
    # verdictul intră odată cu elementul, nu la prima privire asupra lui
    if r.get("ok") and r.get("coada_id"):
        try:
            with db.get_conn() as conn:
                coada_api.scrie_verdict(conn, r["coada_id"], _rez,
                                        _duk_poarta.versiune_validator(date.tip), xml)
        except Exception as _e:
            import logging
            logging.getLogger("iconta").warning("verdict nepersistat la intrarea in coada (%s): %s",
                                                r.get("coada_id"), _e)
    r["verdict"] = {"stare": _rez.get("stare"), "trecut_cu_motiv": _motiv or None}
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
    # [probare invalid, 03.09.2026] Un filtru de stare necunoscut întorcea `200 {"coada": []}` —
    # adică TĂCERE: „nu există nimic în starea asta" arată identic cu „starea asta nu există".
    if stare is not None and stare not in coada_api.STARI:
        raise HTTPException(422, "stare necunoscută: %r (stările cozii: %s)"
                            % (stare, ", ".join(coada_api.STARI)))
    with db.get_conn() as conn:
        return {"coada": coada_api.lista_coada(conn, ctx["firm"], stare)}


@app.get("/coada/{coada_id}/continut")
def coada_continut(coada_id: int, ctx=Depends(cere_cabinet)):
    """[patru-ochi] Continutul unui element din coada pentru VIZUALIZARE inainte de aprobare:
    declaratia (avertismente/note), XML-ul generat si verdictul DUK. Read-only. Fara asta,
    validarea in doi era oarba - cine aproba nu vedea ce aproba (declaratie/XML/verdict)."""
    import base64 as _b64
    from core import duk as _duk
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT tip, payload, (payload->>'_an')::int, (payload->>'_luna')::int "
                        "FROM public.declaratii_coada WHERE id=%s AND cabinet_id=%s",
                        (coada_id, ctx["firm"]))
            row = cur.fetchone()
    if not row:
        raise HTTPException(404, "Element de coadă negăsit (sau alt cabinet).")
    tip, payload, _an, _luna = row
    payload = payload or {}
    xml = payload.get("xml") or ""
    if xml:
        rez = _duk.valideaza(xml, tip, an=_an, luna=_luna)  # java blocant - verdictul oficial ANAF
    else:
        rez = {"stare": "gri", "erori": "", "severitate": None,
               "temei": "XML lipsă din payload-ul cozii.", "limita": ""}
    # [R41] Verdictul se PĂSTREAZĂ. Până azi se producea aici și se arunca, iar ecranul numea
    # „De depus" o listă care conținea declarații fără verdict. Nu se adaugă o a doua rulare de
    # validator: se scrie exact rezultatul celei care se făcea oricum, cu amprenta XML-ului validat.
    try:
        with db.get_conn() as conn:
            coada_api.scrie_verdict(conn, coada_id, rez, _duk.versiune_validator(tip), xml)
    except Exception as _e:
        import logging
        logging.getLogger("iconta").warning("verdict nepersistat (coada %s): %s", coada_id, _e)
    return {"tip": tip,
            "xml_b64": _b64.b64encode(xml.encode()).decode(),
            "avertismente": payload.get("avertismente") or [],
            "note_rezultat": payload.get("note_rezultat") or [],
            "stare": rez["stare"], "erori": rez["erori"], "severitate": rez.get("severitate"),
            "temei": rez.get("temei"), "limita": rez.get("limita")}


@app.post("/coada/{coada_id}/aproba")
def coada_aproba(coada_id: int, date: dict = Body(default={}),
                 ctx=Depends(cere_rol("admin_firma", "angajat"))):
    with db.get_conn() as conn:
        if not _are_permisiune(ctx, "poate_valida"):
            raise HTTPException(status_code=403, detail=FARA_DREPT_VALIDARE)
        # [R41] `motiv_trecere` = trecerea EXPLICITĂ peste un verdict lipsă, stătut sau cu erori.
        # Fără el, acțiunea e refuzată; cu el, se consemnează cine și de ce.
        r = coada_api.aproba(conn, coada_id, str(ctx["uid"]), aprobat_de_id=int(ctx["uid"]),
                             motiv_trecere=(date or {}).get("motiv_trecere"))
    if not r["ok"]:
        cod = r.get("cod")
        http = (409 if cod == "STARE_GRESITA" else
                403 if cod in ("PATRU_OCHI", "FARA_VERDICT") else 404)
        raise HTTPException(http, r.get("mesaj", cod))
    # [p57_notif] notifica pregatitorul
    try:
        with db.get_conn() as conn:
            _notif_pregatitor(conn, coada_id, "aprobata")
    except Exception as _e:
        import logging; logging.getLogger("iconta").warning("notificare pregatitor esuata (aprobare, coada %s): %s", coada_id, _e)
    return r


@app.post("/coada/{coada_id}/respinge")
def coada_respinge(coada_id: int, date: RespingeIn,
                   ctx=Depends(cere_rol("admin_firma", "angajat"))):
    with db.get_conn() as conn:
        if not _are_permisiune(ctx, "poate_valida"):
            raise HTTPException(status_code=403, detail=FARA_DREPT_VALIDARE)
        r = coada_api.respinge(conn, coada_id, str(ctx["uid"]), date.motiv, respins_de_id=int(ctx["uid"]))
    if not r["ok"]:  # [motiv_lipsa_400_v1] MOTIV_LIPSA e input invalid -> 400
        _cod = r.get("cod")
        _http = 409 if _cod == "STARE_GRESITA" else (400 if _cod == "MOTIV_LIPSA" else 404)
        raise HTTPException(_http, r.get("mesaj", _cod))
    # [p57_notif] notifica pregatitorul cu motivul
    try:
        with db.get_conn() as conn:
            _notif_pregatitor(conn, coada_id, "respinsa", motiv=date.motiv)
    except Exception as _e:
        import logging; logging.getLogger("iconta").warning("notificare pregatitor esuata (respingere, coada %s): %s", coada_id, _e)
    return r


@app.post("/coada/{coada_id}/depune")
# [R42] „confirmarea depunerii" — declarația pleacă la autoritate și nu se mai poate reface.
# Validarea (`aproba`/`respinge`) rămâne la asistent: aia se poate reface.
def coada_depune(coada_id: int, date: DepuneIn = DepuneIn(),
                 ctx=Depends(cere_rol("admin_firma"))):
    # [supervizor, EFECT — Costin, 02.09.2026] „O constatare CERTĂ pe firma și perioada care se
    # depune cere confirmare explicită înainte de depunere, iar confirmarea rămâne scrisă: cine,
    # când, peste ce constatare. NU BLOCHEAZĂ NICIODATĂ."
    #
    # DE CE E TOT ÎNTR-UN `try` CARE ÎNGHITE: dacă supervizorul însuși crapă (schemă ruptă, profil
    # incomplet, orice), depunerea TREBUIE să treacă. Altfel motorul care „nu blochează niciodată" ar
    # deveni exact poarta pe care contractul lui o interzice — și ar bloca prin AVARIE, felul cel mai
    # prost, fiindcă n-ar fi nici măcar o decizie. Eșecul se loghează, nu se ascunde.
    _ramase = []
    try:
        with db.get_conn() as _cp:
            _fp = coada_api.firma_si_perioada(_cp, coada_id)
        if _fp:
            _tid, _an_d, _luna_d = _fp
            with db.get_conn() as _cp:
                _schema_d = auth_api.schema_tenant(_cp, ctx["uid"], _tid)
            if _schema_d:
                with db.get_conn(_schema_d) as _cs:
                    _ramase = supervizor.poarta_confirmarii(
                        _cs, _schema_d, _tid, _an_d, _luna_d,
                        confirmari=date.confirmari, confirmat_de=str(ctx["uid"]),
                        confirmat_de_id=int(ctx["uid"]))
    except Exception as _e:
        import logging
        logging.getLogger("iconta").warning(
            "poarta confirmarii supervizorului a esuat pe coada %s: %s — depunerea CONTINUA "
            "(supervizorul nu blocheaza niciodata)", coada_id, _e)
        _ramase = []
    if _ramase:
        # NU e un blocaj: e o cerere de confirmare, cu calea de trecere numită în chiar răspunsul
        # ăsta (trimite `confirmari` cu amprenta și motivul). Interdicția 47 — un refuz fără cale
        # de ieșire pentru om.
        raise HTTPException(409, {
            "cod": "CONSTATARI_NECONFIRMATE",
            "mesaj": ("%d constatare/constatări certe pe firma și perioada asta cer o confirmare "
                      "scrisă înainte de depunere. Depunerea NU e blocată: confirmă-le, cu motiv, "
                      "și continuă." % len(_ramase)),
            # constatarile se trimit AȘA CUM SUNT: sunt deja afirmații tipate, produse de
            # `control_incrucisat`. Reîmpachetarea lor aici ar fi fost o a doua afirmație, netipată
            # — și cine o citea n-ar fi știut care e cea adevărată.
            "constatari": _ramase,
            "actiune": "Retrimite cererea cu `confirmari`: [{amprenta, motiv}] pentru fiecare.",
        })
    with db.get_conn() as conn:
        if not _are_permisiune(ctx, "poate_depune"):
            raise HTTPException(status_code=403, detail=FARA_DREPT_DEPUNERE)
        # [02.09.2026, defect gasit apasand] APROBAREA VINE DUPA POARTA, si e a serverului.
        # Inlantuirea traia in client (`POST /aproba` apoi `POST /depune`), deci aprobarea trecea si
        # poarta cadea dupa ea — iar elementul ramanea `aprobata`, stare din care nu se mai poate
        # RESPINGE. Un refuz al portii ingusta optiunile omului, exact ce contractul interzice.
        # Masurat in `uvicorn.log` pe elementul 8052; v. `coada_api.auto_aproba_daca_e_cazul`.
        _ap = coada_api.auto_aproba_daca_e_cazul(
            conn, coada_id, str(ctx["uid"]), int(ctx["uid"]),
            motiv_trecere=getattr(date, "motiv_trecere", None))
        if not _ap.get("ok"):
            # [probare invalid, 03.09.2026] `INEXISTENT` cădea pe 403 — „n-ai voie" în loc de
            # „nu există". Aceeași cerere pe `/aproba` răspundea 404: două coduri pentru
            # aceeași stare.
            _c = _ap.get("cod")
            raise HTTPException(409 if _c in ("CERE_APROBARE", "STARE_GRESITA") else
                                (404 if _c == "INEXISTENT" else 403),
                                _ap.get("mesaj") or _c)
        r = coada_api.marcheaza_depusa(conn, coada_id, date.spv_index, depus_de=str(ctx["uid"]),
                                       depus_de_id=int(ctx["uid"]),
                                       motiv_trecere=getattr(date, "motiv_trecere", None))
    if not r["ok"]:
        cod = r.get("cod")
        raise HTTPException(409 if cod == "STARE_GRESITA" else (403 if cod == "FARA_VERDICT" else 404),
                            r.get("mesaj", cod))
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
        raise HTTPException(COD_FARA_ACCES_TENANT, FARA_ACCES_TENANT)
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
        return _pachete.genereaza_poveste(cs, cp, tenant_id, an, luna, schema)

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
# [R42] „iese către un om" — pe `status=aprobat` pleacă raportul lunar la client.
def pachet_poveste_set(tenant_id: int, an: int, luna: int, date: PachetTextIn,
                       ctx=Depends(cere_rol("admin_firma"))):
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
                        (nume or "firma ta") + "</b>. Il gasesti in portalul iConta.eu, la Povestea lunii.</p>"
                        "<p><a href='https://iconta.eu' style='background:#2563eb;color:#fff;"
                        "padding:12px 22px;border-radius:8px;text-decoration:none;font-weight:600'>"
                        "Deschide portalul</a></p></div>")
                _obs.trimite_email_html(email, subiect, html)
        return r

@app.get("/pachete/{tenant_id}/preview")
def pachet_preview(tenant_id: int, an: int, luna: int, text: str = "", ctx=Depends(cere_cabinet)):
    # preview = ACELASI _html ca trimiterea (corp + semnatura din DB). text vine din editor,
    # deci reflecta ciorna needitata, nu doar ce e salvat in pachet_povestea.
    schema = _pachet_schema(ctx, tenant_id)
    with db.get_conn(schema) as cs, db.get_conn() as cp:
        html = _pachete.preview_html(cs, cp, tenant_id, an, luna, text, ctx.get("uid"), ctx.get("firm"))
    return {"html": html}

@app.post("/pachete/{tenant_id}/trimite")
# [R42] „iese către un om" — pachetul lunar pleacă la clientul cabinetului.
def pachet_trimite(tenant_id: int, an: int, luna: int, ctx=Depends(cere_rol("admin_firma"))):
    schema = _pachet_schema(ctx, tenant_id)
    with db.get_conn(schema) as cs, db.get_conn() as cp:
        semnatura = _pachete.semnatura_cabinet(cp, ctx.get("uid"), ctx.get("firm"))
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
def declaratii_tipuri(tenant_id: Optional[int] = None, ctx=Depends(cere_cabinet)):
    # [G1] tenant_id OBLIGATORIU: aplicabilitatea prin forma depinde de firma. Fara firma -> 400 (NU {} tacit -
    # "nimic exclus" implicit = tiparul eliminat de 5 ori azi). UI-ul re-cere la fiecare schimbare de firma.
    if tenant_id is None:
        raise HTTPException(400, "Alege firma întâi.")
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT tip_firma, tip_decont, platitor_tva, operatiuni_ic FROM firma_profil WHERE id = 1")
            row = cur.fetchone()
        _vec = ({"tip_firma": row[0], "tip_decont": row[1], "platitor_tva": row[2], "operatiuni_ic": row[3]}
                if row else {})
        # [21.08.2026] FAPTUL BATE VECTORUL: selectorul nu mai blocheaza D390/D301 pe bifa cand exista
        # operatiuni IC reale (sau cand evidenta e incompleta). Tiparul tenant_006. Sonda se cheama
        # INAINTE de inchiderea conexiunii - inainte era calculata dupa `with`, ceea ce n-ar fi mers.
        _neap = control_fiscal_api.neaplicabile_selector(
            _vec, ic_fapt=(lambda: control_fiscal_api.ic_fapt_din_db(conn, schema, azi_ro().year)))
    _tipd = _vec.get("tip_decont")
    return {"tipuri": declaratii_api.tipuri(),
            "periodicitate": {t: declaratii_api.periodicitate_firma(t, _tipd) for t in declaratii_api.tipuri()},
            "neaplicabile": _neap}


@app.post("/declaratii/{tip}/valideaza")  # duk_valideaza_v1
def declaratie_valideaza(tip: str, date: DeclaratieIn,
                         ctx=Depends(cere_rol("admin_firma", "angajat"))):
    """Genereaza declaratia si o trece prin validatorul OFICIAL ANAF (DUKIntegrator).
    Intoarce TREI stari: valid / erori / gri (gri = nu am putut valida; un XML
    nevalidat NU se declara valid). Vezi core/duk.py."""
    import base64 as _b64
    from core import duk as _duk
    body = date.model_dump(exclude_none=True)
    tenant_id = body.pop("tenant_id")
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
    if not schema:
        raise HTTPException(COD_FARA_ACCES_TENANT, FARA_ACCES_TENANT)
    try:
        with db.get_conn(schema) as conn:
            xml, res = declaratii_api.genereaza(conn, schema, tip, body)
    except ValueError as e:
        raise HTTPException(422, str(e))
    # an/luna OBLIGATORII pentru D406 (27.07.2026): SAF-T se valideaza cu
    # DUKIntegrator_AnLunaUI.jar, care le primeste ca parametri; fara ele
    # _valideaza_saft intoarce GRI intotdeauna - deci validarea D406 din aplicatie
    # nu s-a facut NICIODATA, desi calea merge (dovedit manual pe tenant_002/iunie
    # 2026: "Validare fara erori"). Celelalte declaratii le ignora (optionale).
    rez = _duk.valideaza(xml, tip, an=body.get("an"), luna=body.get("luna"))  # java blocant
    return {"tip": tip, "stare": rez["stare"], "erori": rez["erori"],
            "severitate": rez.get("severitate"),  # [A2] E:(eroare) vs A:(atentionare) - frontendul il citeste
            "temei": rez["temei"], "limita": rez["limita"],
            "avertismente": getattr(res, "avertismente", None),
            "note_rezultat": getattr(res, "note_rezultat", None) or [],   # canal neutru (fapte despre rezultat); [] pt declaratiile fara canal
            # [poarta_gol_v1 27.07.2026] cate operatiuni are declaratia; None = nu se poate
            # numara (d101/d112). Ecranul pune o poarta la 0, ca declaratia goala legitima
            # sa nu mai arate identic cu cea golita de un query rupt.
            "operatiuni": declaratii_api.numar_operatiuni(tip, res),
            # [lista 5, 30.08.2026] DIN CE e facuta cifra, nu doar CATE. Pana azi ruta intorcea un
            # contor - „valid, 18 operatiuni" - iar contabilul nu putea vedea CARE 18: 0 din 92 de
            # iesiri isi aratau componentele (1c). Componentele existau pe obiectul de rezultat al
            # motorului; lipsea transportul. Ce nu se poate desface spune de ce, nu tace.
            "componente": declaratii_componente.componente(tip, res),
            "xml_b64": _b64.b64encode(xml.encode()).decode()}


@app.post("/declaratii/{tip}")
def declaratie_genereaza(tip: str, date: DeclaratieIn,
                         ctx=Depends(cere_rol("admin_firma", "angajat"))):
    body = date.model_dump(exclude_none=True)
    tenant_id = body.pop("tenant_id")
    # 1) pe public: aflu schema tenantului + verific accesul userului
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
    if not schema:
        raise HTTPException(COD_FARA_ACCES_TENANT, FARA_ACCES_TENANT)
    # 2) pe schema tenantului (SET LOCAL search_path în get_conn, PgBouncer-safe):
    #    modulul rulează pe conexiunea deja poziționată, NU mai setează el search_path
    try:
        with db.get_conn(schema) as conn:
            xml, res = declaratii_api.genereaza(conn, schema, tip, body)
    except ValueError as e:
        raise HTTPException(422, str(e))
    avert = getattr(res, "avertismente", None)
    constat = getattr(res, "note_rezultat", None) or []   # canal neutru; [] pt declaratiile fara canal
    return {"tip": tip, "xml": xml, "avertismente": avert, "note_rezultat": constat,
            "operatiuni": declaratii_api.numar_operatiuni(tip, res),  # [poarta_gol_v1]
            "componente": declaratii_componente.componente(tip, res)}  # [lista 5]


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
    raise HTTPException(400, "Aveți mai multe firme; alegeți firma.")


@app.get("/portal/firme")
def portal_firme(ctx=Depends(cere_client)):
    with db.get_conn() as conn:
        return {"firme": auth_api.tenantii_userului(conn, ctx["uid"])}

# [portal_acces_cont_v1] patronul isi gestioneaza propriul email + acces suplimentar (fara parola, magic-link)
class SchimbaEmailIn(BaseModel):
    tenant_id: Optional[int] = None
    email: str
class AdaugaAccesIn(BaseModel):
    tenant_id: Optional[int] = None
    email: str
    nume: str = ""
def _titular_client(cur, tenant_id):
    """[R62 (b), 26.08.2026] Cine e titularul contului de portal: PRIMUL cont de client al firmei.

    Regula era scrisa in DOUA locuri si era DIFERITA. Citirea (`GET /portal/acces-cont`) cadea pe
    primul cont cand `tenants.principal_client_id` era NULL; cele trei scrieri comparau direct cu
    coloana. Cum coloana n-avea NICIO cale de scriere — zero INSERT, zero UPDATE, niciun ecran,
    iar `tenant_provisioning` insereaza fara ea — ecranul ii spunea omului *„esti titularul"* si ii
    arata butoanele, iar rutele ii raspundeau 403. **O afirmatie falsa pe ecran, la un om real**
    (utilizatorul #8284, firma #8396). Costin a ridicat-o la PRAG 1: *„ecranul spune una, serverul
    face alta"* — P13, in forma cea mai directa.

    Decizia lui, varianta (b): intrebarea se pune ALTFEL — primul cont de client — fiindca aia e
    regula pe care citirea o folosea deja. *„Alinierea lor nu adauga nimic — scoate o
    inconsistenta."* Iar *titular = primul venit* e o decizie de produs, asumata: la o firma mica,
    primul care primeste acces la portal e patronul sau administratorul. Daca se dovedeste gresita,
    se repara printr-o CALE de schimbare a titularului — alta functionalitate, nu o coloana.

    De aceea `principal_client_id` s-a si SCOS: o coloana cu drum de citire si fara drum de scriere
    e a treia cale prin care intrebarea s-ar putea pune altfel maine."""
    cur.execute("""SELECT u.id FROM public.users u
                   JOIN public.user_tenants ut ON ut.user_id = u.id
                   WHERE ut.tenant_id = %s AND u.rol = 'client'
                   ORDER BY u.id LIMIT 1""", (tenant_id,))
    r = cur.fetchone()
    if not r:
        return None
    return r["id"] if isinstance(r, dict) else r[0]


@app.get("/portal/acces-cont")
def portal_acces_cont(tenant_id: Optional[int] = None, ctx=Depends(cere_client)):
    t = _tenant_client(ctx, tenant_id)
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
            pid = _titular_client(cur, t["id"])
            cur.execute("""SELECT u.id, u.email, u.nume FROM public.users u
                           JOIN public.user_tenants ut ON ut.user_id=u.id
                           WHERE ut.tenant_id=%s AND u.rol='client' ORDER BY u.id""", (t["id"],))
            conturi = cur.fetchall()
    # Fara fallback: `_titular_client` ESTE regula, deci n-are pe ce sa cada. Fallback-ul de aici
    # era chiar jumatatea care mintea — citirea il avea, scrierile nu.
    principal = next((c for c in conturi if c["id"] == pid), None)
    suplimentare = [c for c in conturi if principal and c["id"] != principal["id"]]
    # [R63] A DOUA adresa a aceleiasi persoane. Pachetul lunar NU pleaca la `users.email`, ci la
    # `firma_profil` (`pachete_api`: patron_email, altfel email). Ecranul le arata pe amandoua si
    # le numeste diferit, fiindca decizia lui Costin e ca raman doua: cine INTRA si cine PRIMESTE
    # pot fi persoane diferite. Un ecran care arata aceeasi adresa in doua campuri fara sa spuna
    # ca sunt distincte produce chiar presupunerea gresita.
    with db.get_conn(t["schema_name"]) as conn_s:
        with conn_s.cursor() as cur:
            # [R65] O SINGURA adresa: `patron_email` s-a scos din schema, avea precedenta si niciun
            # scriitor. Aici era a doua folosire a lui `coalesce`, pusa ieri pentru R63.
            cur.execute("SELECT email FROM firma_profil WHERE id = 1")
            rand = cur.fetchone()
    email_pachet = ((rand[0] if rand else None) or "").strip()
    email_logare = ((principal or {}).get("email") or "").strip()
    return {"principal": principal, "suplimentare": suplimentare,
            "eu_principal": bool(principal) and principal["id"] == ctx["uid"],
            "email_pachet": email_pachet,
            "aceeasi_adresa": bool(email_pachet) and email_pachet.lower() == email_logare.lower()}
def _adresa_e_libera(cur, email, exclude_user_id):
    """[R62] Adresa nu e a altcuiva. UN singur loc, chemat si la cerere, si la confirmare.

    Intre cele doua momente pot trece 48 de ore: daca intrebarea ar fi pusa doar la cerere, o
    adresa luata intre timp ar fi aplicata peste, iar unicitatea s-ar sparge. Un loc, ca gardul
    sa poata asertea STRUCTURAL ca amandoua rutele il cheama."""
    cur.execute("SELECT id FROM public.users WHERE lower(email)=%s AND id<>%s",
                (email, exclude_user_id))
    if cur.fetchone():
        raise HTTPException(400, EMAIL_EXISTA)


def _urma_portal(cur, tenant_id, actiune, detaliu, autor_id):
    """[R62 (3), 26.08.2026] Urma pe care o vede CABINETUL.

    Pana azi, un client putea sa-si schimbe adresa de autentificare si sa creeze un utilizator
    SUB cabinet, fara ca acesta sa afle: niciun rand de audit, nicio notificare. Singurul email
    pleca la cel invitat. Append-only, `actiune` dintr-o lista inchisa in BAZA, `detaliu` care nu
    poate fi gol — o urma care nu spune nimic nu e o urma."""
    cur.execute("INSERT INTO public.urme_portal (tenant_id, actiune, detaliu, autor_id) "
                "VALUES (%s, %s, %s, %s)", (tenant_id, actiune, detaliu, autor_id))


def _cere_acelasi_cabinet(ex, firm_id):
    """[R62 (2), 26.08.2026] Un cont de client DEZACTIVAT al altui cabinet nu se reactiveaza aici.

    Ruta refuza deja o adresa care apartine unui cont ACTIV, sau unuia care nu e `client`. Dar un
    cont de client dezactivat intra pe ramura de reactivare si se lega de firma pastrandu-si
    `accounting_firm_id`-ul vechi — care poate fi al altui cabinet. Rezultatul: un utilizator care
    apartine, dupa coloana, cabinetului A, avand acces la o firma a cabinetului B.

    Costin a cerut punctul asta PRIMUL din cele trei: *„e singura cale prin care date ale unui
    cabinet ajung la altul, iar aia nu e o chestiune de urma, e izolarea din P12."*"""
    if not ex:
        return
    al_lui = ex.get("accounting_firm_id") if isinstance(ex, dict) else None
    if al_lui is not None and firm_id is not None and al_lui != firm_id:
        raise HTTPException(400, MESAJ_CLIENT_ALT_CABINET)


class ConfirmaEmailIn(BaseModel):
    token: str


# Sub `/public/`, nu sub `/portal/`, si asta e o alegere: toate rutele care se dovedesc cu un
# TOKEN si nu cu o sesiune stau acolo — `/public/activare`, `/public/magic-login`,
# `/public/reset-parola/seteaza`. O ruta fara garda ascunsa intre cele `/portal/*`, care sunt
# toate pe `cere_client`, ar fi fost aceeasi clasa cu tratament diferit.
@app.post("/public/confirma-email")
def portal_confirma_email(date: ConfirmaEmailIn):
    """[R62 (1)] Confirmarea schimbarii de adresa. FARA garda de sesiune, deliberat.

    Dovada nu e sesiunea — sesiunea o are si cel care a cerut schimbarea, iar chiar aia era
    problema. Dovada e tokenul trimis pe adresa NOUA: il are doar cine o citeste. Tokenul se
    stocheaza doar ca hash, ca la magic-link.

    Adresa se reconfrunta cu `users` la confirmare: intre cerere si confirmare, altcineva poate
    lua adresa, iar o scriere facuta pe nevazute ar sparge unicitatea."""
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
            cur.execute("SELECT id, user_id, tenant_id, email_vechi, email_nou "
                        "FROM public.schimbari_email "
                        "WHERE token_hash=%s AND confirmat_la IS NULL AND expira > now()",
                        (_hash_tok(date.token),))
            r = cur.fetchone()
            if not r:
                raise HTTPException(400, MESAJ_EMAIL_TOKEN_INVALID)
            _adresa_e_libera(cur, r["email_nou"], r["user_id"])
            cur.execute("UPDATE public.users SET email=%s WHERE id=%s",
                        (r["email_nou"], r["user_id"]))
            cur.execute("UPDATE public.schimbari_email SET confirmat_la=now() WHERE id=%s",
                        (r["id"],))
            _urma_portal(cur, r["tenant_id"], "email_confirmat",
                         "adresa de autentificare schimbata: %s -> %s"
                         % (r["email_vechi"], r["email_nou"]), r["user_id"])
    return {"ok": True, "email": r["email_nou"]}


@app.get("/tenants/{tenant_id}/urme-portal")  # [api_intern_v1] scrisa, NECITITA de om: niciun ecran n-o cheama, deci punctul (3) din R62 ramane NESATISFACUT. Iese din lista cand se construieste ecranul. (27.08.2026)
def cabinet_urme_portal(tenant_id: int, ctx=Depends(cere_cabinet)):
    """[R62 (3)] Urma se poate CITI. Lectia din R58: o urma care nu se poate citi e scrisa degeaba."""
    with db.get_conn() as conn:
        if not auth_api.schema_tenant_citire(conn, ctx["uid"], tenant_id):
            raise HTTPException(404, "tenant inexistent sau fără acces")
        with conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
            cur.execute("SELECT actiune, detaliu, autor_id, creat_la FROM public.urme_portal "
                        "WHERE tenant_id=%s ORDER BY creat_la DESC LIMIT 200", (tenant_id,))
            urme = [dict(x) for x in cur.fetchall()]
    return {"urme": urme, "nr": len(urme)}


@app.put("/portal/acces-cont/email")
def portal_schimba_email(date: SchimbaEmailIn, ctx=Depends(cere_client)):
    t = _tenant_client(ctx, date.tenant_id)
    email_nou = date.email.strip().lower()
    if "@" not in email_nou:
        raise HTTPException(400, EMAIL_INVALID)
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
            pid = _titular_client(cur, t["id"])   # [R62 (b)] aceeasi regula ca la citire
            if pid is None or pid != ctx["uid"]:
                raise HTTPException(403, MESAJ_DOAR_TITULARUL)
            _adresa_e_libera(cur, email_nou, ctx["uid"])
            # [R62 (1)] NU se mai scrie `users.email` aici. Adresa e identitatea de autentificare
            # (intrarea se face prin magic-link pe email), deci un UPDATE imediat insemna ca cine
            # are o sesiune deschisa muta contul, definitiv, dintr-un singur camp.
            cur.execute("SELECT email FROM public.users WHERE id=%s", (ctx["uid"],))
            email_vechi = ((cur.fetchone() or {}).get("email") or "").strip().lower()
            if email_vechi == email_nou:
                raise HTTPException(400, MESAJ_EMAIL_ACELASI)
            import secrets as _sec3
            tok = "se_" + _sec3.token_urlsafe(32)
            cur.execute("DELETE FROM public.schimbari_email "
                        "WHERE user_id=%s AND confirmat_la IS NULL", (ctx["uid"],))
            cur.execute("INSERT INTO public.schimbari_email "
                        "(user_id, tenant_id, email_vechi, email_nou, token_hash, expira) "
                        "VALUES (%s, %s, %s, %s, %s, now() + interval '48 hours')",
                        (ctx["uid"], t["id"], email_vechi, email_nou, _hash_tok(tok)))
            _urma_portal(cur, t["id"], "email_cerut",
                         "schimbare de adresa ceruta: %s -> %s" % (email_vechi, email_nou),
                         ctx["uid"])
    baza = os.environ.get("ICONTA_BAZA_URL", "http://localhost:8010")
    link = baza + "/#email-nou=" + tok
    _obs.trimite_email_html(email_nou, "Confirmă adresa nouă — iConta.eu",
        "<p>Bună,</p><p>S-a cerut mutarea contului iConta.eu pe adresa asta.</p>"
        "<p><a href='%s' style='display:inline-block;background:#3d8fd6;color:#fff;"
        "padding:10px 22px;border-radius:6px;text-decoration:none'>Confirmă adresa</a></p>"
        "<p>Linkul e valabil 48 de ore. Dacă nu ai cerut tu, ignoră mesajul — "
        "nu se schimbă nimic.</p>" % link)
    # Adresa VECHE afla, chiar daca nu ea confirma: altfel o mutare de cont ar fi tacuta
    # exact pentru cel care pierde accesul.
    _obs.trimite_email_html(email_vechi, "Cerere de schimbare a adresei — iConta.eu",
        "<p>Bună,</p><p>S-a cerut mutarea contului tău iConta.eu pe adresa "
        "<b>%s</b>.</p><p>Dacă nu ai cerut tu, spune-i cabinetului acum: "
        "schimbarea se face doar după confirmarea de pe adresa nouă.</p>" % email_nou)
    return {"ok": True, "confirmare_ceruta": True, "mesaj": MESAJ_EMAIL_DE_CONFIRMAT}
@app.post("/portal/acces-cont/acces")
def portal_adauga_acces(date: AdaugaAccesIn, ctx=Depends(cere_client)):
    t = _tenant_client(ctx, date.tenant_id)
    email = date.email.strip().lower()
    if "@" not in email:
        raise HTTPException(400, EMAIL_INVALID)
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
            pid = _titular_client(cur, t["id"])   # [R62 (b)] aceeasi regula ca la citire
            if pid is None or pid != ctx["uid"]:
                raise HTTPException(403, MESAJ_DOAR_TITULARUL)
            cur.execute("SELECT accounting_firm_id FROM public.tenants WHERE id=%s", (t["id"],))
            firm_id = cur.fetchone()["accounting_firm_id"]
            cur.execute("SELECT id, rol, activ, accounting_firm_id FROM public.users "
                        "WHERE lower(email)=%s", (email,))
            ex = cur.fetchone()
            if ex and (ex["rol"] != "client" or ex["activ"]):
                raise HTTPException(400, EMAIL_EXISTA)
            _cere_acelasi_cabinet(ex, firm_id)   # [R62 (2)] izolarea intre cabinete, P12
            import secrets as _sec2
            if ex:
                uid = ex["id"]
                cur.execute("UPDATE public.users SET activ=true, nume=%s WHERE id=%s", (date.nume or email.split("@")[0], uid))
                cur.execute("INSERT INTO public.user_tenants (user_id, tenant_id) VALUES (%s, %s) ON CONFLICT DO NOTHING", (uid, t["id"]))
            else:
                cur.execute("""INSERT INTO public.users (email, password_hash, nume, rol, accounting_firm_id, activ)
                               VALUES (%s, %s, %s, 'client', %s, true) RETURNING id""",
                            (email, _nucleu.hash_parola(_sec2.token_urlsafe(16)), date.nume or email.split("@")[0], firm_id))
                uid = cur.fetchone()["id"]
                cur.execute("INSERT INTO public.user_tenants (user_id, tenant_id) VALUES (%s, %s)", (uid, t["id"]))
            tok = "ml_" + _sec2.token_urlsafe(32)
            _pune_token(cur, tok, uid, "48 hours")
            _urma_portal(cur, t["id"], "acces_dat",
                         "clientul a dat acces la portal lui %s (utilizator #%s)" % (email, uid),
                         ctx["uid"])
    baza = os.environ.get("ICONTA_BAZA_URL", "http://localhost:8010")
    link = baza + "/#magic=" + tok
    html = ("<p>Buna,</p><p>Ai primit acces la portalul iConta.eu pentru firma <b>%s</b>.</p>"
            "<p><a href='%s' style='display:inline-block;background:#3d8fd6;color:#fff;padding:10px 22px;border-radius:6px;text-decoration:none'>Intra in portal</a></p>"
            "<p>Linkul e valabil 48 de ore.</p>") % (t.get("nume", ""), link)
    _obs.trimite_email_html(email, "Acces portal iConta.eu — " + t.get("nume", ""), html)
    return {"ok": True}
@app.delete("/portal/acces-cont/acces/{user_id}")
def portal_revoca_acces(user_id: int, tenant_id: Optional[int] = None, ctx=Depends(cere_client)):
    t = _tenant_client(ctx, tenant_id)
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
            pid = _titular_client(cur, t["id"])   # [R62 (b)] aceeasi regula ca la citire
            if pid is None or pid != ctx["uid"]:
                raise HTTPException(403, MESAJ_DOAR_TITULARUL)
            if user_id == pid:
                raise HTTPException(400, "nu poți revoca propriul acces principal")
            cur.execute("DELETE FROM public.user_tenants WHERE user_id=%s AND tenant_id=%s", (user_id, t["id"]))
            cur.execute("SELECT count(*) AS n FROM public.user_tenants WHERE user_id=%s", (user_id,))
            if cur.fetchone()["n"] == 0:
                cur.execute("UPDATE public.users SET activ=false WHERE id=%s", (user_id,))
            _urma_portal(cur, t["id"], "acces_retras",
                         "clientul a retras accesul utilizatorului #%s" % user_id, ctx["uid"])
    return {"ok": True}


@app.get("/portal/firma")
def portal_firma(tenant_id: Optional[int] = None, ctx=Depends(cere_client)):
    t = _tenant_client(ctx, tenant_id)
    with db.get_conn(t["schema_name"]) as conn:
        firma = portal_api.date_firma(conn, t["schema_name"])
    return {"tenant_id": t["id"], "nume": t.get("nume"), "firma": firma}


class RaportZ(BaseModel):
    data: str
    # [R61] NUI-ul casei de marcat + numarul raportului Z. Sunt CHEIA de unicitate, nu
    # data: o firma cu doua case de marcat are doua rapoarte Z legitime in aceeasi zi.
    # Aceeasi cheie ca la `import-amef`, ca notele tastate si cele importate sa se vada.
    nui: str = ""
    nr_raport: str = ""
    total_11: float = 0
    total_21: float = 0
    numerar: float = 0
    card: float = 0
@app.get("/tenants/{tenant_id}/bonuri/de-verificat")
def bonuri_de_verificat(tenant_id: int, ctx=Depends(cere_cabinet)):
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT id, comerciant, cui, data, total, tva_11, tva_21, articole, status, nr_imagini, tip, numar_document, mentiuni, tva, creat_la, orientare
                FROM {schema}.bonuri WHERE status = 'de_verificat' ORDER BY creat_la DESC
            """)
            bonuri = [{"id": r[0], "comerciant": r[1], "cui": r[2],
                       "data": r[3].isoformat() if r[3] else None,
                       "total": float(r[4] or 0),
                       "tva": (round(sum(float(x.get("valoare") or 0) for x in r[13]), 2)
                               if r[13] else float(r[5] or 0) + float(r[6] or 0)),
                       "articole": r[7] or [], "status": r[8],
                       "nr_imagini": r[9] or 0, "tip": r[10] or "bon",
                       "numar_document": r[11], "mentiuni": r[12],
                       "primit_la": r[14].isoformat() if r[14] else None,
                       "orientare": r[15] or 0} for r in cur.fetchall()]  # bon_flux_e9_v1
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
# [R55, 26.08.2026] Rolul e aici fiindca ruta scrie nota `validata` DIRECT — deci produce
# EVIDENTA, nu o propunere, si sare peste poarta de validare. Din cele 40 de rute care scriu
# in `inregistrari_linii`, 36 scriu `ciorna`; astea trei nu. E aceeasi clasa pe care R33 a
# reparat-o la nota de salarii (vezi antetul `core/salarii_contare.py`: „status='validata'
# direct -- ocolea patru-ochi"), ramasa nereparata in trei locuri.
def bon_aproba(tenant_id: int, bon_id: int, b: BonAproba,
               ctx=Depends(cere_rol("admin_firma"))):
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        with conn.cursor() as cur:  # bon_flux_e1b_v1
            cur.execute(f"SELECT tip FROM {schema}.bonuri WHERE id=%s", (bon_id,))
            rt = cur.fetchone()
            if not rt:
                raise HTTPException(404, "bon inexistent")
            if (rt[0] or "bon") != "bon":
                raise HTTPException(400, "documentul e chitanță; folosește stingerea de factură, nu contarea pe cheltuială")
        _cere_luna_deschisa(conn, schema, b.data)   # [R42 (a)] nota poartă data bonului
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
# [R33] Nota propusa mecanic intra CIORNA. Validarea o face al doilea om - patru-ochi.
STARE_CIORNA = "ciorna"


@app.post("/tenants/{tenant_id}/salarii-contare/propunere")
# [R33, decizia Costin 25.08.2026] Semnalul de coerenta nota-vs-D112 apare LA PROPUNERE:
# *„singurul moment in care omul poate face ceva cu informatia; la inchiderea lunii e prea tarziu,
# iar pe suprafata de control fiscal e o constatare despre trecut."*
#
# POST desi nu scrie nimic - acelasi precedent ca `calcul-cm` si `prapastie-salariu`. Regula pe
# care o respecta e cealalta: un GET n-are voie sa scrie (interdictia 6). Aici nu scrie nimeni.
def salarii_contare_propunere(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    """Nota pe care ar scrie-o statul de plata + divergentele fata de D112, cu ambele cifre."""
    _cere_perioada(an, luna)
    from core import salarii_contare as _sc
    schema = _schema_cabinet_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        try:
            p = _sc.propunere(conn, schema, an, luna)
        except ValueError as e:
            # D112 nu se poate genera (profil incomplet). Refuzul lui e scris pentru contabil;
            # fara asta ar ajunge la el ca 500 gol.
            raise HTTPException(422, str(e))
    with db.get_conn(schema) as conn, conn.cursor() as cur:
        cur.execute("SELECT id FROM inregistrari WHERE numar = %s", (p["document_ref"],))
        r = cur.fetchone()
    p["deja_contata"] = bool(r)
    p["nota_id"] = r[0] if r else None
    return p


@app.post("/tenants/{tenant_id}/salarii-contare")
# [R33] Actul: scrie nota CIORNA a statului de plata. Semnaleaza, NU blocheaza - divergenta se
# intoarce si dupa contare, ca sa nu se stinga prin ignorare (regula de la contradictiile pe
# statul de plata). Ciorna, nu validata: patru-ochi ramane.
def salarii_contare_scrie(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    """Scrie nota ciorna a statului de plata. Idempotent pe `document_ref` (interdictia 8:
    schema nu lasa un al doilea exemplar)."""
    _cere_perioada(an, luna)
    from datetime import date as _date
    from core import salarii_contare as _sc
    schema = _schema_cabinet_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        # [R42 (a)] Nota poarta ultima zi a lunii declarate; intr-o luna inchisa nu se scrie.
        ultima = _date(an, luna, 28)
        _cere_luna_deschisa(conn, schema, ultima)
        try:
            p = _sc.propunere(conn, schema, an, luna)
        except ValueError as e:
            raise HTTPException(422, str(e))
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM inregistrari WHERE numar = %s", (p["document_ref"],))
            r = cur.fetchone()
            if r:
                return {**p, "deja_contata": True, "nota_id": r[0],
                         "cod": "DEJA_CONTATA"}
            # Statusul e PARAMETRU, nu text in SQL: asa se poate asertaza pe structura ca nota
            # intra CIORNA (patru-ochi), nu cautand `'ciorna'` intr-un sir (METODA §23).
            cur.execute("INSERT INTO inregistrari (data, numar, descriere, sursa, status) "
                        "VALUES (%s,%s,%s,%s,%s) RETURNING id",
                        (ultima, p["document_ref"],
                         "Stat de plata %02d/%d" % (luna, an), "salarii", STARE_CIORNA))
            nota_id = cur.fetchone()[0]
            for n in p["note"]:
                cur.execute("INSERT INTO inregistrari_linii "
                            "(inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,%s,%s,%s)",
                            (nota_id, n["debit"], n["credit"], n["suma"]))
        conn.commit()
    return {**p, "deja_contata": True, "nota_id": nota_id, "cod": "CONTATA"}


@app.post("/tenants/{tenant_id}/amortizare")
# [R55, 26.08.2026] Rolul e aici fiindca ruta scrie nota `validata` DIRECT — deci produce
# EVIDENTA, nu o propunere, si sare peste poarta de validare. Din cele 40 de rute care scriu
# in `inregistrari_linii`, 36 scriu `ciorna`; astea trei nu. E aceeasi clasa pe care R33 a
# reparat-o la nota de salarii (vezi antetul `core/salarii_contare.py`: „status='validata'
# direct -- ocolea patru-ochi"), ramasa nereparata in trei locuri.
def tenant_amortizare(tenant_id: int, an: int, luna: int,
                      ctx=Depends(cere_rol("admin_firma"))):
    """Genereaza nota de amortizare lunara: 6811 = cont_amortizare, per MF activ."""
    from datetime import date as _date
    from decimal import Decimal as D
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        # [R42 (a)] Nota de amortizare se datează în ziua 28 a lunii cerute (mai jos).
        _cere_luna_deschisa(conn, schema, _date(an, luna, 1).replace(day=28))
        ref = _date(an, luna, 1)
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT numar FROM {schema}.inregistrari
                WHERE sursa = 'amortizare' AND numar = %s
            """, (f"AMORT-{an}-{luna:02d}",))
            if cur.fetchone():
                raise HTTPException(400, "Amortizarea lunii e deja generată.")
            cur.execute(f"""
                SELECT id, denumire, cont_amortizare, valoare, COALESCE(rezidual,0), dnf_luni,
                       data_pif, cont_imobilizare, metoda
                FROM {schema}.mijloace_fixe WHERE activ = true
            """)
            mf = cur.fetchall()
        from core import d406_active as _d406
        linii = []
        for mid, den, cont_am, val, rez, dnf, pif, cont_imob, met in mf:
            if not pif or not dnf:
                continue
            mf_d = {"cod": den, "denumire": den, "cont_imobilizare": cont_imob,
                    "cont_amortizare": cont_am, "valoare": val, "rezidual": rez,
                    "dnf_luni": dnf, "data_pif": pif, "metoda": met}
            try:
                rata = _d406.amortizare_luna(mf_d, an, luna)   # metoda reala (CF art.28), nu liniar
            except ValueError as e:
                raise HTTPException(422, f"Amortizarea nu se poate genera pentru {den}: {e}")
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
def _perioada_blocata(conn, schema, data_nota):
    """True daca luna notei e blocata. data_nota: date sau str ISO.

    [29.08.2026] Interogarea s-a mutat in `core/contare_facturi.luna_blocata`, fiindca de azi o
    cere si contarea automata. Doua definitii ale lui „luna e blocata" ar fi dat doua raspunsuri la
    prima divergenta (P1); aici a ramas doar apelul."""
    from core import contare_facturi as _cf
    with conn.cursor() as cur:
        return _cf.luna_blocata(cur, schema, data_nota)

def _cere_luna_deschisa(conn, schema, data):
    """[R42 (a), 25.08.2026] P15 pe o notă NOUĂ, nu doar pe una existentă.

    Decizia lui Costin: *„o notă contabilă nu e ceva emis — e o înregistrare în evidență, nu un
    artefact predat. Dar nu e nici liberă: o notă care a intrat în evidență nu se șterge, se
    stornează."* Deci nu `admin_firma`, ci verificarea de perioadă.

    `_cere_perioada_deschisa` de mai jos păzea editarea, ștergerea și validarea unei note care
    EXISTĂ. Crearea intra pe altă ușă și nu era păzită: o notă nouă datată într-o lună închisă e
    tot o modificare a perioadei închise."""
    if not data:
        return
    # [31.08.2026] Data se VALIDEAZĂ înainte de a fi întrebată despre perioadă. Fără asta,
    # `_perioada_blocata` primea „10.03.2025" brut, driverul de bază ridica, iar cererea ieșea 500 —
    # o defecțiune în locul unui refuz, exact înainte ca producătorul (care are refuzul scris, cu
    # temei) să apuce să fie chemat. Poarta de perioadă era corectă; ordinea nu era.
    from core import jurnal_api as _ja
    _d, _refuz = _ja._data_valida(data)
    if _refuz:
        raise HTTPException(400, {"mesaj": _refuz["eroare"], "temei": _refuz.get("temei"),
                                  "erori_campuri": [{"camp": "data", "mesaj": _refuz["eroare"]}]})
    if _perioada_blocata(conn, schema, _d):
        raise HTTPException(423, PERIOADA_INCHISA)


def _cere_admin_firma(ctx, mesaj):
    """Verificarea pe care o face `cere_rol("admin_firma")`, dar în corp — pentru cazurile în care
    rolul cerut depinde de STAREA datelor, nu de rută. Aceeași comparație, ca să nu existe două
    definiții ale lui «e administrator» (P1)."""
    if ctx["rol"] not in ("admin_firma", "superadmin"):
        raise HTTPException(403, mesaj)


def _declaratie_generata(conn, tenant_id, tip, an, luna):
    """[R42 (b)] Există deja o declarație generată pentru perioada asta — în coadă sau depusă?

    Decizia lui Costin: *„o completare manuală e parte din declarație DA, după generare; NU,
    înainte. Înainte de generare e pregătire — se poate schimba fără consecință. După, declarația
    existentă nu mai corespunde datelor din care a ieșit."* Asta e P4 citit invers: documentul
    emis e fapt, deci ce l-a produs nu mai poate dispărea în tăcere."""
    from core import scadente as _sc
    try:
        perioada = _sc.scadenta(tip, an, luna=luna)
    except Exception:
        perioada = None
    with conn.cursor() as cur:
        if perioada:
            cur.execute("SELECT 1 FROM public.declaratii_coada "
                        "WHERE tenant_id=%s AND tip=%s AND perioada=%s LIMIT 1",
                        (tenant_id, tip, perioada))
            if cur.fetchone():
                return True
        cur.execute("SELECT 1 FROM public.declaratii_depuse "
                    "WHERE tenant_id=%s AND tip=%s AND an=%s AND luna=%s LIMIT 1",
                    (tenant_id, tip, an, luna))
        return cur.fetchone() is not None


def _cere_perioada_deschisa(conn, schema, nota_id):
    with conn.cursor() as cur:
        cur.execute(f"SELECT data FROM {schema}.inregistrari WHERE id=%s", (nota_id,))
        r = cur.fetchone()
    if r and _perioada_blocata(conn, schema, r[0]):
        raise HTTPException(423, PERIOADA_INCHISA)

@app.get("/tenants/{tenant_id}/perioade-blocate")
def perioade_blocate_lista(tenant_id: int, ctx=Depends(cere_cabinet)):
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        with conn.cursor() as cur:
            cur.execute(f"SELECT an, luna FROM {schema}.perioade_blocate ORDER BY an, luna")
            return {"blocate": [{"an": r[0], "luna": r[1]} for r in cur.fetchall()]}

def _facturi_neincheiate_in_perioada(cur, schema, an, luna):
    """[PPP1, 29.08.2026] Câte FACTURI ale perioadei sunt încă într-o stare neîncheiată.

    Poarta vedea, din 26.08, doar notele. O factură lăsată în `ciorna` sau în `de_recunoscut` e
    aceeași pierdere, pe alt obiect: documentul e acolo, dar actul care-l duce în evidență n-a fost
    făcut, iar după închidere nu se mai poate face — `contabilizeaza` și `recunoaste` cer amândouă o
    lună deschisă. **`de_recunoscut` e chiar starea introdusă azi la R91**, deci clasa n-avea cum să
    fie acoperită de verificarea scrisă acum trei zile.

    Se numără pe `data_emitere`, ca și restul porții: luna documentului, nu ziua în care cineva se
    uită la el."""
    from datetime import date as _d
    sfarsit = _d(an + (luna == 12), (luna % 12) + 1, 1)
    cur.execute(f"""SELECT count(*) FROM {schema}.facturi
                    WHERE status IN ('ciorna','de_recunoscut')
                      AND data_emitere >= %s AND data_emitere < %s""",
                (_d(an, luna, 1), sfarsit))
    return cur.fetchone()[0]


def _ciorne_in_perioada(cur, schema, an, luna):
    """Câte note NEVALIDATE are perioada. [R58] O ciornă închisă înăuntru nu se mai poate valida,
    nu se mai poate șterge, și nu apare nicăieri — Costin: *„e o cheltuială sau un venit care
    dispare fără urmă."*"""
    from datetime import date as _d
    sfarsit = _d(an + (luna == 12), (luna % 12) + 1, 1)
    cur.execute(f"""SELECT count(*) FROM {schema}.inregistrari
                    WHERE status='ciorna' AND data >= %s AND data < %s""",
                (_d(an, luna, 1), sfarsit))
    return cur.fetchone()[0]


@app.post("/tenants/{tenant_id}/perioade-blocate")
# [R58, decizia lui Costin 26.08.2026] Poarta VERIFICĂ înainte de a închide. Până azi făcea un
# singur INSERT — măsurat: închiderea lunii curente pe o firmă reală ar fi lăsat 5 ciorne
# închise înăuntru. Două condiții, amândouă cerute de el:
#   (1) ciorne nevalidate în perioadă — *„o ciornă închisă înăuntru nu se mai poate valida, nu se
#       mai poate șterge, și nu apare nicăieri"*;
#   (2) blocajul care EXISTĂ DEJA în `inchidere_luna` (e-Facturi primite și neînregistrate) —
#       *„o verificare care refuză motivat, dar nu oprește scrierile, e o afirmație despre
#       perioadă, nu o poartă."* Verificarea era scrisă și testată din 21.08; lipsea doar de pe
#       poartă. NU se duplică: se cheamă exact `inchidere_luna.blocaj`.
# Ce NU s-a adăugat, cu motivul lui: echilibrul și orfanii — cer o măsurătoare pe ce s-ar bloca
# azi pe firme reale, iar aia se discută separat.
def perioada_blocheaza(tenant_id: int, an: int, luna: int, ctx=Depends(cere_rol("admin_firma"))):
    from core import inchidere_luna as _il
    from core import migrare_inchideri as _ui
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        with conn.cursor() as cur:
            ciorne = _ciorne_in_perioada(cur, schema, an, luna)
            facturi_desch = _facturi_neincheiate_in_perioada(cur, schema, an, luna)
        bl = _il.blocaj(conn, schema, an, luna)
        if ciorne or facturi_desch or bl:
            # Refuzul spune CE oprește și UNDE se rezolvă — nu doar că nu se poate.
            motive = []
            if ciorne:
                motive.append("%d notă(e) rămân în ciornă în perioadă; validează-le sau șterge-le "
                              "din Jurnal, altfel rămân închise înăuntru și nu mai apar nicăieri"
                              % ciorne)
            if facturi_desch:
                motive.append("%d factură(i) din perioadă sunt încă neîncheiate (ciornă sau "
                              "ciornă de recunoaștere); contabilizează-le sau recunoaște-le, "
                              "altfel după închidere nu se mai poate — amândouă actele cer o lună "
                              "deschisă" % facturi_desch)
            if bl:
                motive.append(str(bl) + " Înregistrează-le (sau respinge-le) în e-Factura.")
            # Refuzul e o AFIRMAȚIE DESPRE DATELE FIRMEI, deci poartă `fel` din nomenclator (P8):
            # o valoare — starea perioadei — nu satisface o regulă. `unde` și `regula` sunt cerute
            # tocmai fiindcă un refuz fără adresă e un reproș.
            raise HTTPException(422, detail=dict(
                _af.afirmatie(
                    "neconformitate", "inchidere_perioada",
                    "Luna %02d/%04d nu se poate închide." % (luna, an),
                    unde="perioada %02d/%04d" % (luna, an),
                    regula="o perioadă se închide doar după ce tot ce s-a întâmplat în ea e "
                           "înregistrat și validat"),
                cod="PERIOADA_NU_SE_POATE_INCHIDE",
                motive=motive, ciorne=ciorne, facturi=facturi_desch, blocaj=bl))
        with conn.cursor() as cur:
            cur.execute(f"""INSERT INTO {schema}.perioade_blocate (an, luna, blocat_de)
                            VALUES (%s,%s,%s) ON CONFLICT DO NOTHING""", (an, luna, ctx["uid"]))
        _ui.scrie(conn, schema, an, luna, "inchisa", ctx["uid"])
        conn.commit()
    return {"blocat": f"{luna:02d}/{an}"}

@app.delete("/tenants/{tenant_id}/perioade-blocate")
# [R58] Redeschiderea e ACT CONSEMNAT, CU MOTIV — P15 și interdicția 36, care o cereau explicit.
# Până azi `DELETE` ștergea rândul, iar odată cu el dispăreau `blocat_de`, `blocat_la` și însuși
# faptul că perioada fusese închisă. Urma trăiește acum în `perioade_inchideri` (append-only,
# cu constrângerea de motiv în BAZĂ, nu doar aici — o urmă care se poate scrie fără motiv de pe
# altă cale n-ar fi o urmă). Poarta rămâne neatinsă: `_cere_luna_deschisa` citește ca înainte.
def perioada_deblocheaza(tenant_id: int, an: int, luna: int, motiv: str = "",
                         ctx=Depends(cere_rol("admin_firma"))):
    from core import migrare_inchideri as _ui
    if not (motiv or "").strip():
        raise HTTPException(422, detail={
            "cod": "REDESCHIDERE_FARA_MOTIV",
            "mesaj": "Redeschiderea unei perioade închise se consemnează cu motiv.",
            "camp": "motiv",
            "temei": "OMFP 1802/2014 — o perioadă închisă se redeschide ca act, nu prin ștergere."})
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        with conn.cursor() as cur:
            cur.execute(f"DELETE FROM {schema}.perioade_blocate WHERE an=%s AND luna=%s", (an, luna))
        _ui.scrie(conn, schema, an, luna, "redeschisa", ctx["uid"], motiv.strip())
        conn.commit()
    return {"deblocat": f"{luna:02d}/{an}"}

@app.get("/tenants/{tenant_id}/perioade-blocate/istoric")
# [R58] Urma se poate CITI — altfel ar fi scrisă degeaba. Cine a închis, cine a redeschis, când
# și de ce.
def perioade_istoric(tenant_id: int, an: Optional[int] = None, luna: Optional[int] = None,
                     ctx=Depends(cere_cabinet)):
    from core import migrare_inchideri as _ui
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant_citire(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        return {"istoric": _ui.istoric(conn, schema, an, luna)}

@app.get("/tenants/{tenant_id}/jurnal")
def tenant_jurnal(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    """Registrul-jurnal (OMFP 2634/2015, cod 14-1-1), pe luna ceruta.

    Confruntat cu norma pe 24.08.2026: coloana 1 (nr. curent de la 1 ianuarie), coloana 3
    (felul/numarul/data documentului justificativ) si totalizarea lunara lipseau. Toate trei
    se DERIVA aici, la citire - nicio cale de scriere nu se atinge. Ce nu se poate deriva
    ramane null: `note_fara_document` spune cate sunt, ca absenta sa fie numarata, nu ascunsa.
    """
    _cere_perioada(an, luna)
    from core import jurnal_api as _j
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant_citire(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        with conn.cursor() as cur:
            # [14-1-1] `nr_curent` se numara de la 1 IANUARIE, nu de la inceputul lunii: norma cere
            # "numarul curent al operatiunilor inregistrate incepand de la 1 ianuarie ... pana la
            # sfarsitul exercitiului financiar". De aceea fereastra e pe AN, iar filtrul pe luna se
            # aplica DUPA numerotare - altfel fiecare luna ar reincepe de la 1.
            cur.execute(f"""
                WITH pe_an AS (
                    SELECT id, data, numar, descriere, sursa, status, factura_id, document_ref,
                           ROW_NUMBER() OVER (ORDER BY data, id) AS nr_curent
                    FROM {schema}.inregistrari
                    WHERE date_trunc('year', data) = %s
                )
                SELECT n.id, n.data, n.numar, n.descriere, n.sursa, n.status, n.factura_id,
                       n.document_ref, n.nr_curent,
                       f.tip, f.serie, f.numar, f.data_emitere,
                       l.cont_debit, l.cont_credit, l.suma, l.centru_cost_id, cc.nume AS centru_nume
                FROM pe_an n
                JOIN {schema}.inregistrari_linii l ON l.inregistrare_id = n.id
                LEFT JOIN {schema}.facturi f ON f.id = n.factura_id
                LEFT JOIN {schema}.centre_cost cc ON cc.id = l.centru_cost_id
                WHERE date_trunc('month', n.data) = %s
                ORDER BY n.data, n.id, l.id
            """, (f"{an}-01-01", f"{an}-{luna:02d}-01"))
            note, total = {}, 0.0
            for (iid, data, nr, desc, sursa, status, fid, dref, nrc,
                 f_tip, f_serie, f_nr, f_data,
                 deb, cre, suma, cc_id, cc_nume) in cur.fetchall():
                if iid not in note:
                    note[iid] = {"id": iid, "nr_curent": int(nrc), "data": data.isoformat(),
                                 "numar": nr, "descriere": desc, "sursa": sursa, "status": status,
                                 "factura_id": fid,
                                 "document": _j.document_justificativ(dref, f_tip, f_serie, f_nr, f_data),
                                 "linii": []}
                note[iid]["linii"].append({"debit": deb, "credit": cre, "suma": float(suma),
                                           "centru_cost_id": cc_id, "centru_nume": cc_nume})
                total += float(suma)
    # [14-1-1] "Sumele debitoare si sumele creditoare se totalizeaza lunar." In partida dubla fiecare
    # linie e simultan debit si credit, deci cele doua totaluri sunt egale prin constructie - se dau
    # amandoua, cum cere formularul, nu unul singur.
    lista = list(note.values())
    fara_document = sum(1 for n in lista if not n["document"])
    return {"note": lista, "total_debit": round(total, 2), "total_credit": round(total, 2),
            "note_fara_document": fara_document}
# Sursele in care traieste un raport Z. Constanta, nu literal in SQL: gardul o citeste din AST
# si compara MULTIMEA, in loc sa caute un sir intr-un text (METODA §23).
_SURSE_Z = ("horeca_z", "amef")


def _cere_z_unic(cur, schema, numar):
    """[R61, 26.08.2026] Un raport Z e unic pe casa de marcat si pe zi — deci pe NUI + numar.

    Decizia lui Costin: *„raportul Z e un document al casei de marcat, unic pe zi si pe aparat.
    Doua rapoarte Z pe aceeasi data nu exista in realitate, deci nici in evidenta."* Varianta (a)
    din R61: a doua nota se REFUZA, nu se accepta cu stornare — un duplicat nu e o corectie, e o
    greseala de operare.

    Cauta in AMANDOUA sursele. Cheia e aceeasi la ruta tastata si la import, deci un raport deja
    importat nu mai poate fi tastat a doua oara, si invers — altfel poarta ar fi tinut doar
    jumatate din drum."""
    cur.execute("SELECT id, data, sursa FROM %s.inregistrari "
                "WHERE sursa = ANY(%%s) AND numar = %%s LIMIT 1" % schema,
                (list(_SURSE_Z), numar))
    r = cur.fetchone()
    if not r:
        return
    iid, data_ex, sursa = (r["id"], r["data"], r["sursa"]) if isinstance(r, dict) else r
    raise HTTPException(409, MESAJ_Z_DUPLICAT % {
        "numar": numar, "data": data_ex, "id": iid,
        "cum": "importata din fisier AMEF" if sursa == "amef" else "tastata"})


@app.post("/tenants/{tenant_id}/horeca/import-amef")
async def horeca_import_amef(tenant_id: int, fisier: UploadFile = File(...), ctx=Depends(cere_cabinet)):
    """Upload p7b/XML AMEF (OPANAF 146/2018 II.7) -> nota Raport Z CIORNA.
    Nota se genereaza pe cote reale din XML: 5311/5125=707 + 707=4427 per cota."""
    from decimal import Decimal as D
    from core import amef_import as _am
    continut = await fisier.read()
    try:
        xml = _am.extrage_xml(continut)
        rz = _am.parseaza_raport_z(xml)
    except (ValueError, Exception) as e:
        raise HTTPException(422, f"fisier AMEF invalid: {e}")
    if not rz["data"]:
        raise HTTPException(422, "nu am putut extrage data din idR")
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        # [R61] Poarta de perioada lipsea DOAR aici, iar asta era pe dos: ruta fara rol era si
        # cea fara poarta. O nota intr-o luna inchisa e aceeasi clasa indiferent ca e ciorna.
        _cere_luna_deschisa(conn, schema, rz["data"])
        numerar = sum((p["suma"] for p in rz["plati"] if p["tip"] == "numerar"), D("0"))
        rest = sum((p["suma"] for p in rz["plati"] if p["tip"] != "numerar"), D("0"))
        with conn.cursor() as cur:
            _cere_z_unic(cur, schema, f"Z-{rz['nui']}-{rz['nr_raport']}")
            cur.execute(f"""INSERT INTO {schema}.inregistrari (data, numar, descriere, sursa, status)
                            VALUES (%s,%s,%s,'amef','ciorna') RETURNING id""",
                        (rz["data"], f"Z-{rz['nui']}-{rz['nr_raport']}",
                         f"Raport Z {rz['data']} AMEF {rz['nui']} nr {rz['nr_raport']} ({rz['nr_bonuri']} bonuri) - de verificat cu Z tiparit"))
            iid = cur.fetchone()[0]
            linii = []
            if numerar: linii.append(("5311", "707", numerar))
            if rest: linii.append(("5125", "707", rest))
            for cota in rz["cote"]:
                if cota["tva"]:
                    linii.append(("707", "4427", cota["tva"]))
            for deb, cred, suma in linii:
                cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                                (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,%s,%s,%s)""",
                            (iid, deb, cred, suma))
        conn.commit()
    return {"inregistrare_id": iid, "status": "ciorna", "data": rz["data"],
            "total": str(rz["total"]), "tva_total": str(rz["total_tva"]),
            "cote": [{"cota": x["cota"], "tva": str(x["tva"])} for x in rz["cote"]],
            "numerar": str(numerar), "card_altele": str(rest)}

@app.post("/tenants/{tenant_id}/horeca/raport-z")
# [R55, 26.08.2026] Rolul e aici fiindca ruta scrie nota `validata` DIRECT — deci produce
# EVIDENTA, nu o propunere, si sare peste poarta de validare. Din cele 40 de rute care scriu
# in `inregistrari_linii`, 36 scriu `ciorna`; astea trei nu. E aceeasi clasa pe care R33 a
# reparat-o la nota de salarii (vezi antetul `core/salarii_contare.py`: „status='validata'
# direct -- ocolea patru-ochi"), ramasa nereparata in trei locuri.
def horeca_raport_z(tenant_id: int, rz: RaportZ,
                    ctx=Depends(cere_rol("admin_firma"))):
    from decimal import Decimal as D
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        _cere_luna_deschisa(conn, schema, rz.data)   # [R42 (a)] nota poartă data raportului Z
        nui = (rz.nui or "").strip()
        nr_raport = (rz.nr_raport or "").strip()
        if not nui or not nr_raport:
            raise HTTPException(400, MESAJ_Z_FARA_CHEIE)
        numar = "Z-%s-%s" % (nui, nr_raport)
        total = D(str(rz.total_11)) + D(str(rz.total_21))
        if total <= 0:
            raise HTTPException(400, "totalul pe cote trebuie să fie pozitiv")
        if abs(float(total) - (rz.numerar + rz.card)) > 0.01:
            raise HTTPException(400, "numerar + card trebuie să fie egal cu totalul pe cote")
        # suta marita: TVA = total * cota / (100 + cota)
        tva11 = (D(str(rz.total_11)) * 11 / 111).quantize(D("0.01"))
        tva21 = (D(str(rz.total_21)) * 21 / 121).quantize(D("0.01"))
        baza11 = D(str(rz.total_11)) - tva11
        baza21 = D(str(rz.total_21)) - tva21
        with conn.cursor() as cur:
            _cere_z_unic(cur, schema, numar)
            cur.execute(f"""
                INSERT INTO {schema}.inregistrari (data, numar, descriere, sursa, status)
                VALUES (%s, %s, %s, 'horeca_z', 'validata') RETURNING id
            """, (rz.data, numar, "Raport Z %s casa %s nr %s" % (rz.data, nui, nr_raport)))
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
@app.post("/tenants/{tenant_id}/banca/parse-extras")  # [api_intern_v1] parsare extras la upload - fara UI inca, pastrat deliberat
async def banca_parse_extras(tenant_id: int, fisier: UploadFile = File(...), ctx=Depends(cere_cabinet)):
    from core import banca_parser, banca as _bk
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
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
    _cere_perioada(an, luna)
    from core import stat_plata_api as _sp
    with db.get_conn() as conn:  # [search_path_tenant_v1] schema pe conn public
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
    with db.get_conn(schema) as conn:  # helper-ele (pontaj/perioada) folosesc nume necalificate -> search_path pe tenant
        # [get_safe_v1 20.08.2026] AICI se chema _snapshot_stat_plata() -> INSERT + commit pe un GET.
        # Efect: simpla deschidere a ecranului Salariati scria un rand per salariat si il comitea
        # (orice monitorizare/prefetch/al doilea tab faceau acelasi lucru), iar poarta de stergere din
        # salariati_api.sterge_salariat se inchidea din vizitare. Consumatorul (POST /calcul-cm)
        # calculeaza acum media din sursa, nu din cache-ul de navigare.
        stat = _sp.stat_plata(conn, schema, an, luna)
        # [lista 5, 30.08.2026] Compozitia netului, din ACEEASI sursa ca fluturasul. Pana azi
        # componentele se vedeau numai in PDF-ul descarcat: ruta trimitea cele 12 campuri, ecranul
        # nu randa niciunul (R97). Se trimite gata compusa ca ecranul sa n-o compuna a doua oara -
        # doua liste ale aceluiasi lucru nu raman egale.
        for _r in stat:
            _r["compozitie"] = _sp.compozitie_fluturas(_r)
        with conn.cursor() as _rc:
            _rc.execute("SELECT 1 FROM public.reges_chei WHERE tenant_id=%s", (tenant_id,))
            _reges_ok = _rc.fetchone() is not None
        return {"stat": stat, "reges_configurat": _reges_ok}
@app.get("/tenants/{tenant_id}/fluturas/{salariat_id}")
# [R52] Poartă salariul unei PERSOANE — date despre cineva care nu e firma.
def tenant_fluturas(tenant_id: int, salariat_id: int, an: int, luna: int,
                    ctx=Depends(cere_rol("admin_firma"))):
    from fastapi.responses import Response
    from core import stat_plata_api as _sp
    _cere_perioada(an, luna)
    with db.get_conn() as conn:  # [search_path_tenant_v1] schema + nume firma pe conn public
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        cur = conn.cursor(); cur.execute("SELECT nume FROM public.tenants WHERE id=%s", (tenant_id,))
        nf = (cur.fetchone() or [""])[0]
    with db.get_conn(schema) as conn:  # fluturas_pdf foloseste nume necalificate -> search_path pe tenant
        pdf = _sp.fluturas_pdf(conn, schema, salariat_id, an, luna, nf)
    if pdf is None:
        raise HTTPException(404, "salariat inexistent")
    return Response(content=pdf, media_type="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="fluturas_{salariat_id}_{an}_{luna:02d}.pdf"'})


# ---------------------------------------------------------------------------------------------
# [stat_emis 21.08.2026] Statul de plata ca DOCUMENT EMIS. Pana aici, statul si fluturasul se
# recalculau la fiecare afisare: un fluturas dat unui om in ianuarie putea iesi altfel in iulie.
# Emiterea ingheata cifrele cu amprenta; divergenta fata de recalcul se SEMNALEAZA; corectia e al
# doilea exemplar, care il refera pe primul. Aplicatia nu corecteaza singura - contabilul decide.
def _cere_an_luna(corp):
    """(an, luna) din corp, sau 422. Nu KeyError -> 500: o cerere incompleta e o cerere gresita, nu
    o defectiune a serverului, iar 500 spune mai mult decat trebuie despre ruta."""
    try:
        an, luna = int((corp or {})["an"]), int((corp or {})["luna"])
    except (KeyError, TypeError, ValueError):
        raise HTTPException(422, "lipsesc an și luna")
    if not (1 <= luna <= 12):
        raise HTTPException(422, "luna trebuie să fie între 1 și 12")
    return an, luna


@app.post("/tenants/{tenant_id}/stat-plata/emite")
# [R42] „iese către un om" — statul se îngheață cu amprentă, exemplar numerotat (P4).
# Dreptul fin `poate_valida` rămâne, verificat în corp: rolul e condiția, dreptul e a doua.
def tenant_stat_emite(tenant_id: int, corp: dict = Body(...),
                      ctx=Depends(cere_rol("admin_firma"))):
    """corp: {an, luna}. Idempotent: cine are deja exemplar nu primeste al doilea (ala e o corectie)."""
    from core import stat_plata_emis as _spe
    # ORDINEA: acces (404) -> drept (403) -> validarea corpului (422). Prima forma citea `corp["an"]`
    # INAINTE de verificarea accesului: un strain primea KeyError -> 500, adica invata ca ruta exista
    # si ce campuri asteapta. Prins de gardul de izolare structurala, care probeaza fiecare ruta noua
    # {tenant_id} cu corp gol.
    schema = _schema_sau_404(ctx, tenant_id)
    if not _are_permisiune(ctx, "poate_valida"):
        raise HTTPException(403, FARA_DREPT_VALIDARE)
    an, luna = _cere_an_luna(corp)
    with db.get_conn(schema) as conn:
        _spe.aplica(conn, schema)
        emise = _spe.emite(conn, schema, an, luna, de_cine=str(ctx["uid"]))
        return {"emise": len(emise), "total": len(_spe.citeste(conn, schema, an, luna))}


@app.get("/tenants/{tenant_id}/stat-plata/emis")
def tenant_stat_emis(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    """Exemplarele emise + contradictiile DERIVATE (emis vs recalcul de acum). Nu scrie nimic."""
    _cere_perioada(an, luna)
    from core import stat_plata_emis as _spe
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        ex = _spe.citeste(conn, schema, an, luna)
        return {"exemplare": ex, "contradictii": _spe.verifica(conn, schema, an, luna)}


@app.post("/tenants/{tenant_id}/stat-plata/corectie")
def tenant_stat_corectie(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {salariat_id, an, luna}. Al doilea exemplar. Primul ramane - el a ajuns la om."""
    from core import stat_plata_emis as _spe
    schema = _schema_sau_404(ctx, tenant_id)
    if not _are_permisiune(ctx, "poate_valida"):
        raise HTTPException(403, FARA_DREPT_VALIDARE)
    an, luna = _cere_an_luna(corp)
    try:
        sid = int(corp["salariat_id"])
    except (KeyError, TypeError, ValueError):
        raise HTTPException(422, "cererea nu spune pentru care salariat se face corecția")
    with db.get_conn(schema) as conn:
        try:
            return _spe.corectie(conn, schema, sid, an, luna, de_cine=str(ctx["uid"]))
        except ValueError as e:
            raise HTTPException(409, str(e))


@app.post("/tenants/{tenant_id}/stat-plata/motiv")
def tenant_stat_motiv(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {exemplar_id, motiv}. ASUMA divergenta, nu o sterge: ramane in lista, cu cine si cand."""
    from core import stat_plata_emis as _spe
    schema = _schema_sau_404(ctx, tenant_id)
    if not _are_permisiune(ctx, "poate_valida"):
        raise HTTPException(403, FARA_DREPT_VALIDARE)
    try:
        eid = int(corp["exemplar_id"])
    except (KeyError, TypeError, ValueError):
        raise HTTPException(422, "cererea nu spune care exemplar al statului se asumă")
    with db.get_conn(schema) as conn:
        try:
            _spe.motiveaza(conn, schema, eid, corp.get("motiv") or "", de_cine=str(ctx["uid"]))
        except ValueError as e:
            raise HTTPException(422, str(e))
    return {"ok": True}


@app.get("/tenants/{tenant_id}/plata-salarii-preview")
def tenant_plata_salarii_preview(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    """[F134] Sumar inainte de generarea fisierului SEPA: cate plati, total, cine e exclus (fara IBAN)."""
    from core import plata_salarii as _ps
    with db.get_conn() as conn:  # [search_path_tenant_v1] schema + nume firma pe conn public
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        cur = conn.cursor(); cur.execute("SELECT nume FROM public.tenants WHERE id=%s", (tenant_id,))
        nf = (cur.fetchone() or [""])[0]
    with db.get_conn(schema) as conn:  # genereaza_pain001 foloseste nume necalificate -> search_path pe tenant
        try:
            _xml, meta = _ps.genereaza_pain001(conn, schema, an, luna, nume_firma_fallback=nf)
        except ValueError as e:
            raise HTTPException(422, str(e))
    return meta


@app.post("/tenants/{tenant_id}/plata-salarii-fisier")
# [R45] POST, nu GET: producerea fișierului care pleacă la bancă e un ACT, iar un GET n-are
# voie să scrie (interdicția 6, `core/test_get_fara_scriere.py`). Metoda contrazicea fapta.
def tenant_plata_salarii_fisier(tenant_id: int, an: int, luna: int,
                                ctx=Depends(cere_rol("admin_firma"))):
    """[F134] Fisierul SEPA/ISO 20022 pain.001.001.03 de plata a salariilor NET pe card (download).
    [R45] Se pastreaza: continut, moment, autor, amprenta, numar de exemplar."""
    from fastapi.responses import Response
    from core import plata_salarii as _ps
    from core import artefacte as _art
    with db.get_conn() as conn:  # [search_path_tenant_v1] schema + nume firma pe conn public
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        cur = conn.cursor(); cur.execute("SELECT nume FROM public.tenants WHERE id=%s", (tenant_id,))
        nf = (cur.fetchone() or [""])[0]
    with db.get_conn(schema) as conn:  # genereaza_pain001 foloseste nume necalificate -> search_path pe tenant
        try:
            xml, meta = _ps.genereaza_pain001(conn, schema, an, luna, nume_firma_fallback=nf)
        except ValueError as e:
            raise HTTPException(422, str(e))
        _art.pastreaza(conn, schema, "plata_salarii", "%04d-%02d" % (an, luna), xml,
                       produs_de_id=int(ctx["uid"]), produs_de=ctx.get("nume") or str(ctx["uid"]))
    return Response(content=xml, media_type="application/xml",
                    headers={"Content-Disposition": f'attachment; filename="{meta["fisier"]}"'})


# ---- [F125] clasificare manuala D390 (reclasificare + adaugare) ----
def _schema_cabinet_sau_404(ctx, tenant_id):
    """Rezolva schema tenantului (conexiune separata); d390.pull foloseste nume necalificate,
    deci apelantul deschide apoi db.get_conn(schema) pozitionat pe schema."""
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
    if not schema:
        raise HTTPException(404, "tenant inexistent sau fără acces")
    return schema


@app.get("/tenants/{tenant_id}/d390-clasificare")
def d390_clasificare_stare(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    """Operatiunile auto-derivate (cu tipul curent) + liniile manuale, pt ecranul de clasificare."""
    from core import d390_clasificare_api as _cl
    schema = _schema_cabinet_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        return _cl.stare(conn, schema, an, luna)


@app.put("/tenants/{tenant_id}/d390-clasificare/reclasificare")
def d390_reclasificare(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """Override tip pe o operatiune auto: {an, luna, directie, tara, cod, tip}."""
    from core import d390_clasificare_api as _cl
    schema = _schema_cabinet_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        r = _cl.salveaza_reclasificare(conn, schema, corp.get("an"), corp.get("luna"),
                                       corp.get("directie"), corp.get("tara"), corp.get("cod"), corp.get("tip"))
    if r.get("eroare"):
        _ec = r.get("erori_campuri")  # [G10] contract {mesaj, erori_campuri}
        raise HTTPException(422, detail={"mesaj": r["eroare"], "erori_campuri": _ec} if _ec else r["eroare"])
    return r


@app.post("/tenants/{tenant_id}/d390-clasificare/manual")
def d390_manual_adauga(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """Adauga linie pur manuala: {an, luna, tip, tara, cod, den, baza}."""
    from core import d390_clasificare_api as _cl
    schema = _schema_cabinet_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        r = _cl.manual_adauga(conn, schema, corp.get("an"), corp.get("luna"), corp.get("tip"),
                              corp.get("tara"), corp.get("cod"), corp.get("den"), corp.get("baza"))
    if r.get("eroare"):
        _ec = r.get("erori_campuri")  # [G10] contract {mesaj, erori_campuri}
        raise HTTPException(422, detail={"mesaj": r["eroare"], "erori_campuri": _ec} if _ec else r["eroare"])
    return r


@app.delete("/tenants/{tenant_id}/d390-clasificare/manual/{mid}")
def d390_manual_sterge(tenant_id: int, mid: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    from core import d390_clasificare_api as _cl
    schema = _schema_cabinet_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        # [R42 (b)] Înainte de generare linia manuală e pregătire — o poate scoate un asistent.
        # După, e parte din declarația care există deja, iar ștergerea o face să nu mai
        # corespundă datelor din care a ieșit.
        if _declaratie_generata(conn, tenant_id, "D390", an, luna):
            _cere_admin_firma(ctx, "declarația D390 pe %02d/%d e deja generată — o linie completată "
                                   "manual face parte din ea, iar scoaterea ei o face să nu mai "
                                   "corespundă datelor din care a ieșit" % (luna, an))
        return _cl.manual_sterge(conn, schema, an, luna, mid)


# [D301 27.07.2026] Introducerea operatiunilor D301 (decont special TVA). Geaman cu
# d390-clasificare: grila lunara + adaugare + stergere, cere_cabinet (operatiuni de contabil).
@app.get("/tenants/{tenant_id}/d301-operatiuni")
def d301_operatiuni_lista(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    """Operatiunile lunii + nomenclatoare (tipuri, valute, cote period-aware) pt ecranul D301."""
    from core import d301_operatiuni_api as _op
    schema = _schema_cabinet_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        return _op.lista(conn, schema, an, luna)


@app.post("/tenants/{tenant_id}/d301-operatiuni")
def d301_operatiuni_adauga(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """Adauga o operatiune: {an, luna, tip, nr_doc, data_doc, val_valuta, tip_valuta, curs, cota}."""
    from core import d301_operatiuni_api as _op
    schema = _schema_cabinet_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        r = _op.adauga(conn, schema, corp.get("an"), corp.get("luna"), corp)
    if r.get("eroare"):
        _ec = r.get("erori_campuri")  # [G10] contract {mesaj, erori_campuri}
        raise HTTPException(422, detail={"mesaj": r["eroare"], "erori_campuri": _ec} if _ec else r["eroare"])
    return r


@app.delete("/tenants/{tenant_id}/d301-operatiuni/{op_id}")
def d301_operatiuni_sterge(tenant_id: int, op_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    from core import d301_operatiuni_api as _op
    schema = _schema_cabinet_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        return _op.sterge(conn, schema, an, luna, op_id)




# [B2/B3 D300] Randuri manuale D300 (Decont TVA). Geaman cu d301-operatiuni: grila lunara +
# adaugare + stergere, cere_cabinet (operatiuni de contabil). Persistate in d300_manual;
# d300.genereaza le re-citeste pe calea de depunere (paritate preview<->depunere).
@app.get("/tenants/{tenant_id}/d300-manual")
def d300_manual_lista(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    """Randurile manuale ale perioadei + randurile inca disponibile de adaugat (allow-list minus
    auto-derivate minus deja introduse), cu etichete oficiale din backend."""
    from core import d300_manual_api as _dm
    schema = _schema_cabinet_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        return _dm.lista(conn, schema, an, luna)


@app.post("/tenants/{tenant_id}/d300-manual")
def d300_manual_adauga(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """Adauga/actualizeaza un rand manual D300: {an, luna, rand, baza, tva, descriere}."""
    from core import d300_manual_api as _dm
    schema = _schema_cabinet_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        r = _dm.adauga(conn, schema, corp.get("an"), corp.get("luna"), corp)
    if r.get("eroare"):
        _ec = r.get("erori_campuri")  # [G10] contract {mesaj, erori_campuri}
        raise HTTPException(422, detail={"mesaj": r["eroare"], "erori_campuri": _ec} if _ec else r["eroare"])
    return r


@app.delete("/tenants/{tenant_id}/d300-manual/{rid}")
def d300_manual_sterge(tenant_id: int, rid: int, ctx=Depends(cere_cabinet)):
    from core import d300_manual_api as _dm
    schema = _schema_cabinet_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        # [R42 (b)] Aceeași regulă ca la D390. Perioada nu vine din cerere, ci din rândul însuși —
        # altfel s-ar putea șterge un rând dintr-o lună generată trimițând altă lună.
        with conn.cursor() as _cur_per:
            _cur_per.execute(f"SELECT an, luna FROM {schema}.d300_manual WHERE id=%s", (rid,))
            _r = _cur_per.fetchone()
        if _r and _declaratie_generata(conn, tenant_id, "D300", _r[0], _r[1]):
            _cere_admin_firma(ctx, "declarația D300 pe %02d/%d e deja generată — un rând completat "
                                   "manual face parte din ea, iar scoaterea lui o face să nu mai "
                                   "corespundă datelor din care a ieșit" % (_r[1], _r[0]))
        return _dm.sterge(conn, schema, rid)


class AdeverintaIn(BaseModel):  # F136
    scop: Optional[str] = None
    mentiuni: Optional[str] = None
    serie_ci: Optional[str] = None
    nr_ci: Optional[str] = None
    functie: Optional[str] = None
    tip_contract: Optional[str] = None
    nr_cim: Optional[str] = None
    data_cim: Optional[str] = None
    departament: Optional[str] = None
    vechime_munca: Optional[str] = None
    vechime_specialitate: Optional[str] = None
    venit_an_precedent: Optional[float] = None
    sporuri: Optional[str] = None
    retineri: Optional[str] = None
    nr_iesire: Optional[str] = None
    data_iesire: Optional[str] = None
    an: Optional[int] = None
    luna: Optional[int] = None

@app.post("/tenants/{tenant_id}/salariati/{salariat_id}/adeverinta")
# [R42] „iese către un om" — adeverința pleacă la salariat (art. 34(5) Codul muncii).
def tenant_adeverinta(tenant_id: int, salariat_id: int, date: AdeverintaIn,
                      ctx=Depends(cere_rol("admin_firma"))):
    """F136: adeverinta de salariat (art. 34(5) Codul muncii) -> PDF."""
    from fastapi.responses import Response
    from core import adeverinta as _adv
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        try:
            pdf = _adv.pdf(conn, schema, salariat_id, date.dict())
        except ValueError as e:   # [R66 (c)] refuzul numeste documentul si unde se completeaza
            raise HTTPException(422, str(e))
    if pdf is None:
        raise HTTPException(404, "salariat inexistent")
    return Response(content=pdf, media_type="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="adeverinta_{salariat_id}.pdf"'})

@app.get("/tenants/{tenant_id}/salariati/{salariat_id}/pontaj")
def tenant_pontaj_get(tenant_id: int, salariat_id: int, an: int, luna: int, ctx=Depends(cere_context)):
    """F135: grila lunara de pontaj (informativ) - zile lucratoare, exceptii, rezumat."""
    from core import pontaj as _p
    from core import perioada as _per
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        g = _p.grila(conn, schema, salariat_id, an, luna)
        if g is not None:
            g["perioada_confirmata"] = _per.e_confirmat(conn, schema, an, luna, "pontaj")  # [cap.23]
    if g is None:
        raise HTTPException(404, "salariat inexistent")
    return g

class PontajIn(BaseModel):
    zi: str
    stare: Optional[str] = None

@app.put("/tenants/{tenant_id}/salariati/{salariat_id}/pontaj")
def tenant_pontaj_set(tenant_id: int, salariat_id: int, date: PontajIn, ctx=Depends(cere_context)):
    """F135: seteaza starea unei zile (stare goala/prezent = sterge exceptia)."""
    from core import pontaj as _p
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        r = _p.seteaza(conn, schema, salariat_id, date.zi, date.stare, tenant_id=tenant_id)
    if not r.get("ok"):
        raise HTTPException(422, r.get("mesaj", "eroare"))
    return r


class ConfirmaPontajIn(BaseModel):
    an: int
    luna: int


@app.get("/tenants/{tenant_id}/facturi/perioada")
def tenant_facturi_perioada(tenant_id: int, an: int, luna: int, ctx=Depends(cere_context)):
    """[cap.23, 21.08.2026] Starea INCHIDERII lunii pe domeniul `facturi`: confirmat / cine / cand,
    daca se poate confirma acum si — daca nu — DE CE (documente primite de la ANAF, neinregistrate)."""
    from core import inchidere_luna as _il
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        return _il.stare(conn, schema, an, luna)


@app.post("/tenants/{tenant_id}/facturi/perioada/confirma")
def tenant_facturi_perioada_confirma(tenant_id: int, date: ConfirmaPontajIn,
                                     ctx=Depends(cere_rol("admin_firma"))):
    """[cap.23] Declara luna INCHISA pe facturi: evidenta ei devine autoritativa, iar semaforul se poate
    sprijini pe ea cand spune ca o declaratie nu se datoreaza. Rol admin_firma, ca la pontaj.
    REFUZA motivat daca stim de e-Facturi primite si neinregistrate — nu lasam pe cineva sa declare
    complet ceva ce noi vedem deja ca nu e."""
    from core import inchidere_luna as _il
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        try:
            st = _il.confirma(conn, schema, date.an, date.luna, ctx.get("uid"))
        except ValueError as e:
            raise HTTPException(422, str(e))
    return {"ok": True, "perioada": st}


@app.post("/tenants/{tenant_id}/facturi/perioada/redeschide")
def tenant_facturi_perioada_redeschide(tenant_id: int, date: ConfirmaPontajIn,
                                       ctx=Depends(cere_rol("admin_firma"))):
    """[cap.23] Redeschide luna (o corectie de facturi cere redeschiderea). Simetric cu confirmarea;
    o modificare de facturi o face oricum AUTOMAT (facturi_api._redeschide_luna)."""
    from core import inchidere_luna as _il
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        st = _il.redeschide(conn, schema, date.an, date.luna)
    return {"ok": True, "perioada": st}


@app.post("/tenants/{tenant_id}/pontaj/confirma")
def tenant_pontaj_confirma(tenant_id: int, date: ConfirmaPontajIn, ctx=Depends(cere_rol("admin_firma"))):
    """[cap.23] Confirma pontajul lunii -> devine AUTORITATIV pentru salarizare (tichete pe zile efectiv
    lucrate). Rol admin_firma. Idempotent (re-confirmarea reimprospateaza)."""
    from core import perioada as _per
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        _per.confirma(conn, schema, date.an, date.luna, "pontaj", ctx.get("uid"))
        st = _per.e_confirmat(conn, schema, date.an, date.luna, "pontaj")
    return {"ok": True, "perioada_confirmata": st}

# cf_verificari_v1: verificari contabile reutilizabile (echilibru + trezorerie)
def _verifica_documente_pozate(schema):  # verif_doc_pozate_v1
    """Documente pozate de clienti blocate in flux: necontate >3 zile sau note ciorna casa >3 zile."""
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute(f"""SELECT count(*) FROM {schema}.bonuri
                        WHERE status='de_verificat' AND creat_la < now() - interval '3 days'""")
        bonuri_vechi = cur.fetchone()[0]
        cur.execute(f"""SELECT count(*) FROM {schema}.casa_operatiuni co
                        JOIN {schema}.inregistrari i ON i.id = co.inregistrare_id
                        WHERE i.status='ciorna' AND co.creat_la < now() - interval '3 days'""")
        ciorne = cur.fetchone()[0]
    return {"ok": bonuri_vechi == 0 and ciorne == 0,
            "bonuri_neverificate": bonuri_vechi, "ciorne_casa": ciorne}

def _verificari_contabile(schema, an, luna):
    from core import verificatoare as _vf
    from datetime import date as _date
    sfarsit = _date(an + (luna == 12), (luna % 12) + 1, 1)
    with db.get_conn() as conn, conn.cursor() as cur:
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
    # [R33 varianta b'', 26.08.2026] ECHILIBRUL E UN VERDICT COMPUS DIN DOUA VERIFICARI.
    # Pana azi aici rula doar `verifica_balanta`, iar `core/echilibru_perioada` -- scris, testat,
    # cu garda proprie -- nu era chemat de nimeni. Se credea ca e "a doua implementare a aceleiasi
    # verificari"; masurat pe aceleasi date (25.08.2026), modurile de esec sunt DISJUNCTE:
    #   echilibru_perioada -> linia cu o parte lipsa (NULL, gol sau numai spatii) si orfanul;
    #   verifica_balanta   -> soldurile initiale care nu se inchid.
    # Fiecare o rateaza pe cealalta, deci a alege una ar fi STERS o verificare (CONFORMITATE R33).
    # Cele doua se compun intr-un SINGUR verdict `echilibru` -- contabilul nu trebuie sa stie ca
    # sunt doua module -- iar compunerea se face LA CONSTRUCTIE, in verdict_echilibru (pur).
    # LIMITA DECLARATA: felia de ledger e LUNA curenta si doar notele `validata` (domeniul
    # modulului); o ciorna cu contul rupt se vede abia dupa validare, cand devine evidenta.
    from core import echilibru_perioada as _ep
    try:
        with db.get_conn() as _cl:
            _ledger = _ep.echilibru_perioada_db(_cl, schema, an, luna)
    except Exception as _e:
        # verificare RUPTA, nu date curate: verdict_echilibru o trece la `neverificat`, deci
        # verdele nu se poate afirma peste ea (P6).
        _ledger = {"eroare": "%s: %s" % (type(_e).__name__, _e)}
    # [control_incrucisat_v1 + F163_ui] punti declaratie <-> contabilitate/evidenta (D-vs-contabilitate):
    #   D300 vs 4427/4426 · D112 (salarii) vs 444/4315/4316/436 · D390 (bunuri IC) vs evidenta validata.
    # Motoare SEPARATE (core/control_incrucisat), doar EXPUSE aici - aceeasi anatomie (trei stari + temei +
    # remediu). NU se atinge engine-ul. Fiecare pe conexiune proprie pe schema; esec izolat -> gri cu cauza
    # (gri e informatie, nu absenta - filozofia control_incrucisat), nu doboara ceilalti verificatori.
    from core import control_incrucisat as _ci
    def _incrucisat(fn, eticheta):
        try:
            with db.get_conn(schema) as _c:
                return fn(_c, schema, an, luna)
        except Exception as _e:
            # [P8] VERIFICARE RUPTA: motorul a crapat, nu datele lipsesc. Pe ecran ramane gri, in
            # date se DEOSEBESTE - cine numara „cate nu pot fi verificate" nu mai inghite si rupturile.
            # Starea intra la CONSTRUCTIE, nu prin atribuire dupa: `_c["stare"] = "gri"` e prins de
            # verificator (VERDICT_COLAPSAT, stare-literal), si pe drept - un verdict carpit dupa
            # constructie are doua surse. A doua oara azi cand fac asta.
            _c = dict(_af.afirmatie("verificare_rupta", eticheta,
                                    "NU pot verifica %s: %s" % (eticheta, _e),
                                    eroare="%s: %s" % (type(_e).__name__, _e)),
                      stare="gri", eticheta=eticheta, temei="Verificarea nu a rulat.",
                      remediu={"fel": "investigatie", "cauza": "Eroare la verificare.",
                               "actiune": "Reîncearcă; dacă persistă, verifică datele firmei.",
                               "facturi": []})
            _c["mesaj"] = _c["motiv"]
            return {"stare": "gri", "constatari": [_c],
                    "limita": "Verificarea %s nu a rulat: %s" % (eticheta, _e)}
    tva_incr = _incrucisat(_ci.verifica_tva, "TVA")
    d112_incr = _incrucisat(_ci.verifica_d112, "salarii (D112)")
    d390_incr = _incrucisat(_ci.verifica_d390, "operatiuni intracomunitare (D390)")
    # [F184] conformitate cota TVA facturi emise vs cota standard pe perioada (value-aware, NU decl-vs-contab)
    cota_tva_incr = _incrucisat(_ci.verifica_cota_tva, "cotă TVA facturi emise")
    rezultat = {
        "tva_incrucisat": tva_incr,
        "d112_incrucisat": d112_incr,
        "d390_incrucisat": d390_incr,
        "cota_tva_conformitate": cota_tva_incr,
        "echilibru": _ep.verdict_echilibru(_ledger, _vf.verifica_balanta(bal),
                                           "%04d-%02d" % (an, luna)),
        "trezorerie": _vf.verifica_trezorerie(bal),
        "tva": _vf.coerenta_tva(bal.get("4427", {}).get("credit", 0), bal.get("4426", {}).get("debit", 0)),
        "note": len(note),
    }
    try:  # verif_doc_pozate_v1
        rezultat["documente_pozate"] = _verifica_documente_pozate(schema)
    except Exception as e:
        # gri, nu tacere: chiar daca azi nu e surfacat in pastila, devine corect cand cineva il surfaceaza.
        rezultat["documente_pozate"] = _constatare_esuata("Documente pozate — verificare eșuată", "documentele pozate", e, an, luna)
    # [d205_legacy_eliminat 23.07] Verificarea d205_vs_457 a fost ELIMINATA: citea suma D205 din tabela
    # d205_beneficiari care NU are niciun writer in cod -> suma_d205 era mereu 0 -> orice firma cu dividende
    # (1171->457) primea rosu fals. D205 real foloseste cont 457 din d205.py; coerenta D205-vs-457 pe FAPT
    # traieste deja in semafor (control_incrucisat.dividende_distribuite via declaratii_fapt). Vezi DECIZII 23.07.
    return rezultat


@app.get("/firme/{tenant_id}/verificari")
def firma_verificari(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    # [probare invalid, 03.09.2026] `luna=13` întorcea 200 cu stare „gri" și „NU pot verifica" —
    # adică o INTRARE GREȘITĂ îmbrăcată în NECUNOAȘTERE. Sunt două lucruri diferite: una se
    # corectează tastând altceva, cealaltă e un risc rămas neacoperit. Confuzia le ascunde pe
    # amândouă (și producea „trimestrul 5/2026").
    # [lotul 3, 04.09.2026] Aceeasi verificare traia scrisa de mana aici si lipsea din alte sase
    # rute. Acum toate sapte cheama acelasi ajutor: o singura sursa, si urmatoarea ruta o mosteneste.
    _cere_perioada(an, luna)
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
    if not schema:
        raise HTTPException(404, "tenant inexistent sau fără acces")
    return _verificari_contabile(schema, an, luna)  # cf_verificari_v1
BON_DIR_BAZA = "~/iconta_date/bonuri"  # bon_flux_e1_v1

def _tenant_pentru_documente(ctx, tenant_id):  # bon_cabinet_v1
    """Client -> firma lui (ca pana acum); rolurile de cabinet -> tenant_id obligatoriu,
    cu verificarea accesului. Intoarce dict cu schema_name + id."""
    if (ctx.get("rol") or "") == "client":
        return _tenant_client(ctx, tenant_id)
    if not tenant_id:
        raise HTTPException(400, "Alegeți firma (necesar pentru rolurile de cabinet).")
    return {"schema_name": _schema_sau_404(ctx, tenant_id), "id": tenant_id}

@app.post("/portal/bon")
async def portal_bon(fisiere: list[UploadFile] = File(...), tenant_id: Optional[int] = None, ctx=Depends(cere_context)):
    """Extrage datele bonului cu AI si salveaza ca DRAFT (status='extras') + pozele pe disc.
    Intra la contabil doar dupa confirmarea clientului (POST /portal/bon/{id}/confirma)."""
    from core import ai_client
    import json as _json, os as _os
    t = _tenant_pentru_documente(ctx, tenant_id)
    if not ai_client.disponibil():
        raise HTTPException(503, "serviciul AI indisponibil")
    imagini = []
    for f in fisiere[:4]:
        b = await f.read()
        if len(b) > 8_000_000:
            raise HTTPException(400, "imagine prea mare (max 8MB)")
        imagini.append((b, f.content_type or "image/jpeg"))
    prompt = ("Primesti un document pozat (un singur document, posibil pe mai multe imagini, in ordine). "
              "Clasifica-l: bon fiscal SAU chitanta. Raspunde DOAR cu JSON, fara alt text: "
              '{"tip": "bon", "comerciant": "...", "cui": "...", "data": "YYYY-MM-DD", "total": 0.0, '
              '"numar_document": "...", "mentiuni": "...", '
              '"articole": [{"denumire": "...", "valoare": 0.0, "cota_tva": 0, "cont_propus": "..."}], '
              '"tva": [{"cota": 0, "valoare": 0.0}], "bon_complet": true, "orientare": 0}. '
              'tip = "bon" pentru bon fiscal, "chitanta" pentru chitanta. '
              "Pentru BON FISCAL: numar_document = numarul bonului daca se vede; articole si tva ca mai jos. "
              "Cotele TVA le citesti EXACT cum apar pe bon (pot fi 19/9/11/21/5 in functie de anul bonului). "
              "cont_propus = contul de cheltuiala OMFP 1802 potrivit articolului: 6022 combustibil, "
              "623 protocol (cafea, apa, mancare), 604 materiale nestocate, 628 alte servicii. "
              "Reducerile primesc contul articolului principal. "
              "Pentru CHITANTA: comerciant = emitentul chitantei (cel care a incasat), total = suma platita, "
              "numar_document = numarul chitantei, mentiuni = textul de dupa 'reprezentand' (ex. factura platita); "
              "articole si tva raman liste goale. "
              "bon_complet = false daca documentul pare taiat in poza (nu se vad antetul si totalul) "
              "ori e partial ilizibil. "
              "orientare = cate grade trebuie rotita PRIMA imagine in sens orar ca textul sa fie drept: 0, 90, 180 sau 270. "
              "Daca un camp nu se vede, pune null.")
    try:
        text = ai_client.citeste_imagini(imagini, prompt)
        text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        date = _json.loads(text)
    except Exception:
        raise HTTPException(422, "nu am putut citi bonul; încearcă o poză mai clară")
    avertismente = []
    if date.get("bon_complet") is False:
        avertismente.append("Documentul pare incomplet sau greu lizibil \u00een poz\u0103. Fotografiaz\u0103-l \u00eentreg, cu lumin\u0103 bun\u0103 \u0219i totalul vizibil.")  # bon_flux_e3b_v1
    total = float(date.get("total") or 0)  # avertismentul aritmetic se arata doar contabilului (bon_flux_e3b_v1)
    tva_lista = date.get("tva") or []
    # cotele TVA period-aware din common.COTE (Legea 141/2025), nu literali cuplati la anul curent
    _r_std = int(_common.cota("tva_standard", strict=False)[0] * 100)
    _r_red = int(_common.cota("tva_redusa", strict=False)[0] * 100)
    tva_11 = round(sum(float(x.get("valoare") or 0) for x in tva_lista if x.get("cota") == _r_red), 2)
    tva_21 = round(sum(float(x.get("valoare") or 0) for x in tva_lista if x.get("cota") == _r_std), 2)
    schema = t["schema_name"]
    with db.get_conn() as conn:  # verif_doc_pozate_v1: drafturi abandonate >24h se curata (rand + poze)
        with conn.cursor() as cur:
            cur.execute(f"""DELETE FROM {schema}.bonuri
                            WHERE status='extras' AND creat_la < now() - interval '24 hours'
                            RETURNING id""")
            for (vechi_id,) in cur.fetchall():
                import shutil as _shutil
                d = _os.path.join(_os.path.expanduser(BON_DIR_BAZA), schema, str(vechi_id))
                if _os.path.isdir(d):
                    _shutil.rmtree(d, ignore_errors=True)
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            tip_doc = "chitanta" if date.get("tip") == "chitanta" else "bon"  # bon_flux_e1b_v1
            cur.execute(f"""
                INSERT INTO {schema}.bonuri (comerciant, cui, data, total, tva_11, tva_21, articole, tva, nr_imagini, bon_complet, status, tip, numar_document, mentiuni, orientare)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'extras', %s, %s, %s, %s) RETURNING id
            """, (date.get("comerciant"), date.get("cui"), date.get("data"),
                  total, tva_11, tva_21, _json.dumps(date.get("articole") or []),
                  _json.dumps(tva_lista), len(imagini), date.get("bon_complet") is not False,
                  tip_doc, date.get("numar_document"), date.get("mentiuni"),
                  int(date.get("orientare") or 0) % 360))
            bon_id = cur.fetchone()[0]
    dir_bon = _os.path.join(_os.path.expanduser(BON_DIR_BAZA), schema, str(bon_id))
    _os.makedirs(dir_bon, exist_ok=True)
    _EXT = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}
    for i, (b, mt) in enumerate(imagini, 1):
        with open(_os.path.join(dir_bon, "img_%d.%s" % (i, _EXT.get(mt, "jpg"))), "wb") as fh:
            fh.write(b)
    return {"ok": True, "bon": date, "bon_id": bon_id, "avertismente": avertismente}

def _bon_imagine_cale(schema, bon_id, n):
    import os as _os, glob as _glob
    cai = sorted(_glob.glob(_os.path.join(_os.path.expanduser(BON_DIR_BAZA), schema, str(int(bon_id)), "img_%d.*" % int(n))))
    return cai[0] if cai else None

@app.post("/portal/bon/{bon_id}/confirma")
def portal_bon_confirma(bon_id: int, tenant_id: Optional[int] = None, ctx=Depends(cere_context)):
    """Clientul confirma ca poza e intreaga si lizibila -> bonul intra la contabil."""
    t = _tenant_pentru_documente(ctx, tenant_id)
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute(f"UPDATE {t['schema_name']}.bonuri SET status='de_verificat' WHERE id=%s AND status='extras' RETURNING id", (bon_id,))
        if not cur.fetchone():
            raise HTTPException(404, "bon inexistent sau deja trimis")
    return {"ok": True}

@app.delete("/portal/bon/{bon_id}")
def portal_bon_sterge(bon_id: int, tenant_id: Optional[int] = None, ctx=Depends(cere_context)):
    """Clientul reface poza -> draftul (status='extras') si pozele lui se sterg."""
    import os as _os, shutil as _shutil
    t = _tenant_pentru_documente(ctx, tenant_id)
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute(f"DELETE FROM {t['schema_name']}.bonuri WHERE id=%s AND status='extras' RETURNING id", (bon_id,))
        if not cur.fetchone():
            raise HTTPException(404, "bon inexistent sau deja trimis")
    dir_bon = _os.path.join(_os.path.expanduser(BON_DIR_BAZA), t["schema_name"], str(bon_id))
    if _os.path.isdir(dir_bon):
        _shutil.rmtree(dir_bon, ignore_errors=True)
    return {"ok": True}

@app.get("/portal/bon/{bon_id}/imagine/{n}")
def portal_bon_imagine(bon_id: int, n: int, tenant_id: Optional[int] = None, ctx=Depends(cere_context)):
    from fastapi.responses import FileResponse
    t = _tenant_pentru_documente(ctx, tenant_id)
    cale = _bon_imagine_cale(t["schema_name"], bon_id, n)
    if not cale:
        raise HTTPException(404, "imagine inexistentă")
    return FileResponse(cale)

@app.get("/tenants/{tenant_id}/bonuri/{bon_id}/imagine/{n}")
# [R52] Fotografia unui bon: orice apare pe hârtia aia, inclusiv ce nu ține de firmă.
def cabinet_bon_imagine(tenant_id: int, bon_id: int, n: int,
                        ctx=Depends(cere_rol("admin_firma"))):
    from fastapi.responses import FileResponse
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
    if not schema:
        raise HTTPException(404, "tenant inexistent sau fără acces")
    cale = _bon_imagine_cale(schema, bon_id, n)
    if not cale:
        raise HTTPException(404, "imagine inexistentă")
    return FileResponse(cale)
@app.get("/tenants/{tenant_id}/bonuri/{bon_id}/facturi-candidate")
def bon_facturi_candidate(tenant_id: int, bon_id: int, ctx=Depends(cere_cabinet)):
    """Pentru o chitanta: facturile PRIMITE, neplatite, care ar putea fi stinse de ea.
    Ordonare: potrivire CUI intai, apoi apropiere de suma."""
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        with conn.cursor() as cur:
            cur.execute(f"SELECT cui, total FROM {schema}.bonuri WHERE id=%s", (bon_id,))
            r = cur.fetchone()
            if not r:
                raise HTTPException(404, "document inexistent")
            cui = (r[0] or "").upper().replace("RO", "").strip()
            suma = float(r[1] or 0)
            cur.execute(f"""
                SELECT id, numar, serie, data_emitere, total, tert_nume, tert_cui
                FROM {schema}.facturi
                WHERE directie='primita' AND COALESCE(status,'') <> 'anulata' AND platita_la IS NULL
                ORDER BY (upper(replace(COALESCE(tert_cui,''),'RO','')) = %s) DESC,
                         abs(total - %s) ASC, data_emitere DESC
                LIMIT 10
            """, (cui, suma))
            fc = [{"id": x[0], "numar": ((x[2] or "") + str(x[1] or "")).strip(),
                   "data": x[3].isoformat() if x[3] else None,
                   "total": float(x[4] or 0), "furnizor": x[5], "cui": x[6],
                   "potrivire_cui": bool(cui) and (x[6] or "").upper().replace("RO", "").strip() == cui,
                   "potrivire_suma": abs(float(x[4] or 0) - suma) <= 0.05} for x in cur.fetchall()]
    return {"facturi": fc}

class ChitantaStinge(BaseModel):
    data: str
    suma: float
    partener: str = ""
    cui: str = ""
    document: str = ""
    factura_id: Optional[int] = None

@app.post("/tenants/{tenant_id}/bonuri/{bon_id}/stinge")
def chitanta_stinge(tenant_id: int, bon_id: int, c: ChitantaStinge,
                    ctx=Depends(cere_rol("admin_firma"))):
    """Chitanta certificata de contabil: plata furnizor prin Registrul de casa
    (casa_api.adauga -> 401=5311 ciorna + operatiune casa + verificare plafon).
    Optional leaga si marcheaza platita factura primita."""
    from core import casa_api
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        with conn.cursor() as cur:
            cur.execute(f"SELECT tip, status FROM {schema}.bonuri WHERE id=%s", (bon_id,))
            r = cur.fetchone()
            if not r:
                raise HTTPException(404, "document inexistent")
            if (r[0] or "bon") != "chitanta":
                raise HTTPException(400, "documentul nu e chitanta")
            if r[1] != "de_verificat":
                raise HTTPException(400, "documentul nu e in asteptare")
        rez = casa_api.adauga(conn, schema, {"data": c.data, "categorie": "plata_furnizor",
                                             "suma": c.suma, "document": c.document or ("CHIT-%d" % bon_id),
                                             "partener": c.partener, "cui": c.cui})
        if rez.get("eroare"):
            raise HTTPException(400, rez["eroare"])
        with conn.cursor() as cur:
            cur.execute(f"""UPDATE {schema}.bonuri SET status='aprobat', factura_id=%s,
                            casa_operatiune_id=%s, inregistrare_id=%s,
                            comerciant=%s, data=%s, total=%s WHERE id=%s""",
                        (c.factura_id, rez["id"], rez["inregistrare_id"],
                         c.partener or None, c.data, c.suma, bon_id))
            if c.factura_id:
                cur.execute(f"UPDATE {schema}.facturi SET platita_la=now() WHERE id=%s AND directie='primita'", (c.factura_id,))
    return {"ok": True, "operatiune_id": rez["id"], "nota_id": rez["inregistrare_id"],
            "avertismente": rez.get("avertismente") or []}

# chitante_emise_v1
class ChitantaEmite(BaseModel):
    data: str
    suma: float
    factura_id: Optional[int] = None

@app.post("/tenants/{tenant_id}/chitante")
# [R42] „iese către un om" — chitanța (14-4-1) e document cu regim de numerotare.
def chitanta_emite(tenant_id: int, c: ChitantaEmite, ctx=Depends(cere_rol("admin_firma"))):
    """Emite chitanta (cod 14-4-1, Ordin 2634/2015) pentru incasare in numerar:
    numerotare pe serie per firma + operatiune in Registrul de casa prin casa_api
    (5311=4111, nota ciorna, verificare plafon Legea 70/2015)."""
    from core import casa_api
    schema = _schema_sau_404(ctx, tenant_id)
    if c.suma <= 0:
        raise HTTPException(400, "suma trebuie să fie > 0")
    client_nume = client_cui = reprezentand = None
    total_fact = None
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            if c.factura_id:
                cur.execute(f"SELECT serie, numar, tert_nume, tert_cui, total, directie, data_emitere FROM {schema}.facturi WHERE id=%s", (c.factura_id,))
                r = cur.fetchone()
                if not r:
                    raise HTTPException(404, "factură inexistentă")
                if r[5] != "emisa":
                    raise HTTPException(400, "chitanta se emite doar pentru facturi emise")
                client_nume, client_cui, total_fact = r[2], r[3], float(r[4] or 0)
                nrtxt = str(r[1] or "")  # chitante_emise_v2_reprezentand: numar contine adesea si seria (ex. MD-2)
                if r[0] and not nrtxt.startswith(str(r[0])):
                    nrtxt = str(r[0]) + nrtxt
                reprezentand = "contravaloare factura %s din %s" % (
                    nrtxt, data_ro(r[6]))
            cur.execute(f"SELECT COALESCE(serie_chitanta, 'CH') FROM {schema}.firma_profil LIMIT 1")
            rs = cur.fetchone()
            serie = (rs[0] if rs else None) or "CH"
            cur.execute(f"SELECT COALESCE(max(numar), 0) + 1 FROM {schema}.chitante WHERE serie=%s", (serie,))
            nr = cur.fetchone()[0]
        rez = casa_api.adauga(conn, schema, {"data": c.data, "categorie": "incasare_client",
                                             "suma": c.suma, "document": "%s-%s" % (serie, nr),
                                             "partener": client_nume, "cui": client_cui})
        if rez.get("eroare"):
            raise HTTPException(400, rez["eroare"])
        with conn.cursor() as cur:
            cur.execute(f"""INSERT INTO {schema}.chitante
                            (serie, numar, data, factura_id, client_nume, client_cui, suma, reprezentand,
                             casa_operatiune_id, inregistrare_id)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                        (serie, nr, c.data, c.factura_id, client_nume, client_cui, c.suma,
                         reprezentand, rez["id"], rez["inregistrare_id"]))
            cid = cur.fetchone()[0]
            if c.factura_id and total_fact is not None and c.suma >= total_fact - 0.005:
                cur.execute(f"UPDATE {schema}.facturi SET platita_la=now() WHERE id=%s", (c.factura_id,))
    return {"ok": True, "chitanta_id": cid, "serie": serie, "numar": nr,
            "avertismente": rez.get("avertismente") or []}

@app.get("/tenants/{tenant_id}/chitante")
def chitante_lista(tenant_id: int, factura_id: Optional[int] = None, ctx=Depends(cere_context)):
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn() as conn, conn.cursor() as cur:
        if factura_id:
            cur.execute(f"SELECT id, serie, numar, data, suma, client_nume FROM {schema}.chitante WHERE factura_id=%s AND NOT anulata ORDER BY id DESC", (factura_id,))
        else:
            cur.execute(f"SELECT id, serie, numar, data, suma, client_nume FROM {schema}.chitante WHERE NOT anulata ORDER BY id DESC LIMIT 100")
        chi = [{"id": r[0], "serie": r[1], "numar": r[2], "data": r[3].isoformat() if r[3] else None,
                "suma": float(r[4] or 0), "client_nume": r[5]} for r in cur.fetchall()]
    return {"chitante": chi}

@app.get("/tenants/{tenant_id}/chitante/{chitanta_id}/pdf")
# [R52] Poartă numele și suma plătită de un terț.
def chitanta_pdf(tenant_id: int, chitanta_id: int, ctx=Depends(cere_rol("admin_firma"))):
    from fastapi.responses import Response
    from core import chitante as _ch
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute(f"SELECT serie, numar, data, client_nume, client_cui, suma, reprezentand FROM {schema}.chitante WHERE id=%s", (chitanta_id,))
        r = cur.fetchone()
        if not r:
            raise HTTPException(404, "chitanță inexistentă")
        cur.execute("SELECT nume, cui FROM public.tenants WHERE id=%s", (tenant_id,))
        te = cur.fetchone() or (None, None)
    pdf = _ch.pdf_chitanta({"nume": te[0], "cui": te[1]},
                           {"serie": r[0], "numar": r[1],
                            "data": data_ro(r[2]),
                            "client_nume": r[3], "client_cui": r[4], "suma": float(r[5] or 0),
                            "reprezentand": r[6]})
    return Response(content=pdf, media_type="application/pdf",
                    headers={"Content-Disposition": 'attachment; filename="chitanta_%s_%s.pdf"' % (r[0], r[1])})

@app.get("/portal/documente/luni")
def portal_documente_luni(tenant_id: Optional[int] = None, ctx=Depends(cere_client)):
    t = _tenant_client(ctx, tenant_id)
    with db.get_conn() as conn:
        luni = documente_api.luni_disponibile(conn, t["schema_name"])
        decl = documente_api.declaratii_depuse(conn, t["id"])
    return {"luni": luni, "declaratii": decl}
@app.get("/tenants/{tenant_id}/balanta")
def cabinet_balanta_date(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    """[lista 5, 30.08.2026] Balanta ca DATE, nu ca PDF.

    Pana azi singura cale spre cifrele balantei era `documente/balanta`, care intoarce un fisier:
    ecranul avea titlu, navigare pe luna si un buton de descarcare, atat. O cifra pe care n-o poti
    citi decat descarcand-o nu se poate verifica pe ecran - chiar asta e criteriul listei 5.

    Inchiderea vine ODATA cu randurile, si ca obiect, nu ca propozitie: pe o balanta goala starea e
    `nimic_de_verificat`, nu `se_inchide`.
    """
    _cere_perioada(an, luna)
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant_citire(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
    with db.get_conn(schema) as conn:  # balanta foloseste nume necalificate -> search_path pe tenant
        randuri = documente_api.balanta(conn, schema, an, luna)
    return {"randuri": randuri,
            "totaluri": documente_api.totaluri_balanta(randuri),
            "inchidere": documente_api.inchidere_balanta(randuri)}


@app.get("/tenants/{tenant_id}/registru-evidenta-fiscala")
def registru_fiscal_citeste(tenant_id: int, an: int, varianta: str = "profit",
                            totalizare: str = "an", ctx=Depends(cere_cabinet)):
    """[lista 3, 30.08.2026] Registrul de evidență fiscală. Sunt DOUĂ, nu unul.

    `profit` — CF art. 19 alin. (7) + HG 1/2016 pct. 8, derivat din aceleași câmpuri din care iese
    D101. `venituri_pf` — CF art. 68 alin. (8)-(9) + OMFP 3254/2017, ținut pe fiecare sursă din
    fiecare categorie de venit.
    """
    from core import registru_evidenta_fiscala as _ref
    if varianta not in _ref.VARIANTE:
        raise HTTPException(404, "variantă necunoscută: %r" % varianta)
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        if varianta == "venituri_pf":
            return _ref.registru_pf(conn, schema, an)
        try:
            return _ref.registru_profit(conn, schema, an, totalizare)
        except _ref.RegistruNeconstruibil:
            # 409, nu 400: cererea e legitimă, iar refuzul nu e al ei — e al nostru, și poartă de ce.
            # Corpul e o AFIRMAȚIE tipată, nu un dicționar de proză (decizia din 21.08): e o
            # afirmație despre datele firmei, iar `verificare_rupta` o ține să nu fie citită ca un
            # verdict gri permanent — „nu se poate pe trimestru", nu „nu există pe trimestru".
            raise HTTPException(409, _ref.refuz_totalizare(an, totalizare))


@app.post("/tenants/{tenant_id}/registru-evidenta-fiscala")
def registru_fiscal_adauga(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """Înscrie un rând în varianta PERSOANE FIZICE — singura care se completează.

    Varianta pe profit se derivă din D101 și n-are ce primi: un `POST` pe ea ar însemna o a doua
    sursă de adevăr despre același an.
    """
    from core import registru_evidenta_fiscala as _ref
    an = corp.get("an")
    if not an:
        raise HTTPException(400, {
            "mesaj": "Nu am înscris rândul: lipsește anul.",
            "erori_campuri": [{"camp": "an", "mesaj": "cerut, nu poate lipsi"}]})
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        try:
            return _ref.adauga_pf(conn, schema, int(an), corp)
        except _ref.InregistrareIncompletaPF as e:
            raise HTTPException(400, {
                "mesaj": "Nu am înscris rândul: registrul cere un câmp pe care nu l-am primit.",
                "erori_campuri": [{"camp": e.camp, "mesaj": str(e)}],
                "temei": e.temei})


@app.get("/tenants/{tenant_id}/registru-inventar")
def registru_inventar_citeste(tenant_id: int, exercitiu: int,
                              momentul: str = "sfarsit_exercitiu",
                              ctx=Depends(cere_cabinet)):
    """[lista 3, 30.08.2026] Registrul-inventar (cod 14-1-2), al doilea registru obligatoriu.

    Legea 82/1991 art. 20 il cere; OMFP 2634/2015 Anexa 2 ii spune continutul. Poarta COMUNA, ca la
    registrele art. 321 si din acelasi motiv.
    """
    from core import registru_inventar as _ri
    if momentul not in _ri.MOMENTE:
        raise HTTPException(404, "moment necunoscut: %r" % momentul)
    # [lotul 3] `exercitiu=1900` intorcea un registru gol — cu temeiul legal citat langa el, ca si
    # cum ar fi fost un raspuns despre un exercitiu care exista.
    _cere_perioada(exercitiu=exercitiu)
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        return _ri.registru(conn, schema, exercitiu, momentul)


@app.get("/tenants/{tenant_id}/registru-inventar/propunere")
def registru_inventar_propunere(tenant_id: int, an: int, luna: int = 12,
                                ctx=Depends(cere_cabinet)):
    """Coloana 3 PROPUSA din balanta — soldurile pe cont, ca sa nu fie retastate.

    Nu creeaza niciun rand si NU atinge coloana 4: valoarea de inventar vine din numararea faptica.
    Un ajutor care ar completa si coloana 4 ar produce un registru fara nicio diferenta, adica o
    inventariere perfecta care nu s-a facut.
    """
    from core import registru_inventar as _ri
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
    # [lotul 3] `luna=13` intorcea `{"an": 2026, "luna": 13, "randuri": []}` — adica repeta luna
    # imposibila inapoi, ca si cum ar fi o perioada goala.
    _cere_perioada(an, luna)
    with db.get_conn(schema) as conn:  # balanta foloseste nume necalificate -> search_path pe tenant
        return {"an": an, "luna": luna, "randuri": _ri.solduri_de_pornire(conn, schema, an, luna)}


@app.post("/tenants/{tenant_id}/registru-inventar")
def registru_inventar_adauga(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """Inscrie un rand. Refuzul iese pe contractul comun `detail.erori_campuri`."""
    from core import registru_inventar as _ri
    exercitiu = corp.get("exercitiu")
    if not exercitiu:
        raise HTTPException(400, {
            "mesaj": "Nu am înscris rândul: lipsește exercițiul financiar.",
            "erori_campuri": [{"camp": "exercitiu", "mesaj": "cerut, nu poate lipsi"}]})
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        try:
            return _ri.adauga(conn, schema, int(exercitiu), corp)
        except _ri.InregistrareIncompleta as e:
            raise HTTPException(400, {
                "mesaj": "Nu am înscris rândul: registrul cere un câmp pe care nu l-am primit.",
                "erori_campuri": [{"camp": e.camp, "mesaj": _mesaj_scurt_inventar(e)}],
                "temei": e.temei})


def _mesaj_scurt_inventar(e):
    """Pe camp incape o propozitie, nu o norma. Cauza e singura care are nevoie de mai mult de
    „cerut de norma": omul trebuie sa stie CA exista o diferenta, nu doar ca lipseste un camp."""
    if e.camp == "cauza":
        return "există o diferență între valoarea contabilă și cea de inventar — scrie cauza ei"
    if e.camp == "valoare_inventar":
        return "valoarea numărată; nu se completează singură din valoarea contabilă"
    return "cerut de normă, nu poate lipsi"


@app.get("/tenants/{tenant_id}/registre-art321/{fel}")
def registre_art321_citeste(tenant_id: int, fel: str, an: Optional[int] = None,
                            ctx=Depends(cere_cabinet)):
    """[lista 3, 30.08.2026] Cele doua registre cerute de art. 321 alin. (4) CF, prin normele lui.

    POARTA COMUNA, nu cea de citire-istorica. Registrul e o clasa NOUA de acces, nu a doua iesire a
    unui artefact vechi — iar zavorul din `test_poarta_citire_istorica` cere exact ca o intrare care
    nu e nici din cele 13 de la deschidere, nici pereche declarata a uneia, sa nu treaca. Daca
    vreodata se va cere citirea registrului pe o firma scoasa din portofoliu, se declara acolo, cu
    propozitie scrisa.
    """
    from core import registre_art321 as _r
    if fel not in _r.FELURI:
        raise HTTPException(404, "registru necunoscut: %r" % fel)
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        return _r.registru(conn, schema, fel, an)


@app.post("/tenants/{tenant_id}/registre-art321/{fel}")
def registre_art321_adauga(tenant_id: int, fel: str, corp: dict = Body(...),
                           ctx=Depends(cere_cabinet)):
    """Inscrie un rand. Refuzul de completitudine iese ca 400 CU campul si temeiul, nu ca proza.

    Pe contractul care EXISTA deja — `detail.erori_campuri = [{camp, mesaj}]`, normalizat de
    `static/js/api.js` si randat de trei ecrane. Un contract paralel, oricat de bine gandit, ar fi
    insemnat ca acelasi fel de refuz se citeste in doua feluri; `temei` se adauga ALATURI de el,
    fiindca niciun refuz de-al nostru nu se rosteste fara norma pe care se sprijina.
    """
    from core import registre_art321 as _r
    if fel not in _r.FELURI:
        raise HTTPException(404, "registru necunoscut: %r" % fel)
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        try:
            return _r.adauga(conn, schema, fel, corp)
        except _r.InregistrareIncompleta as e:
            # Mesajul de pe CAMP e scurt — el se randeaza langa un input, iar acolo un paragraf de
            # normа nu se citeste. Norma intreaga sta la nivelul refuzului, unde are loc.
            raise HTTPException(400, {
                "mesaj": "Nu am înscris rândul: registrul cere un câmp pe care nu l-am primit.",
                "erori_campuri": [{"camp": e.camp, "mesaj": "cerut de normă, nu poate lipsi"}],
                "temei": e.temei})


@app.get("/tenants/{tenant_id}/documente/balanta")
def cabinet_documente_balanta(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    _cere_perioada(an, luna)
    from fastapi.responses import Response
    with db.get_conn() as conn:  # [search_path_tenant_v1] schema + detalii pe conn public
        schema = auth_api.schema_tenant_citire(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        d = tenant_provisioning.detalii_tenant(conn, tenant_id)
    with db.get_conn(schema) as conn:  # balanta_pdf foloseste nume necalificate -> search_path pe tenant
        pdf = documente_api.balanta_pdf(conn, schema, an, luna, (d or {}).get("nume") or "")
    return Response(content=pdf, media_type="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="balanta_{an}_{luna:02d}.pdf"'})

@app.get("/portal/documente/balanta")
def portal_documente_balanta(an: int, luna: int, tenant_id: Optional[int] = None, ctx=Depends(cere_client)):
    from fastapi.responses import Response
    t = _tenant_client(ctx, tenant_id)
    with db.get_conn() as conn:
        pdf = documente_api.balanta_pdf(conn, t["schema_name"], an, luna, t.get("nume") or "")
    return Response(content=pdf, media_type="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="balanta_{an}_{luna:02d}.pdf"'})
# === API PUBLIC === # api_public_v1
def cere_api_key(x_api_key: Optional[str] = Header(None)):
    from core import api_public as _ap
    if not x_api_key:
        raise HTTPException(401, "lipsă X-Api-Key")
    with db.get_conn() as conn:
        firm_id = _ap.verifica(conn, x_api_key)
    if not firm_id:
        raise HTTPException(401, "cheie invalidă sau revocată")
    return {"firm": firm_id}


def _api_schema(actx, tenant_id):
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("""SELECT schema_name FROM public.tenants
                       WHERE id=%s AND accounting_firm_id=%s""", (tenant_id, actx["firm"]))
        r = cur.fetchone()
    if not r:
        # [probare invalid lot 2, 03.09.2026] Spunea „firmă inexistentă" și pentru o firmă care
        # EXISTĂ, dar e a altui cabinet — aceeași afirmație falsă scoasă din `FARA_ACCES_TENANT`
        # în lotul 1. Forma de acum nu deosebește cele două stări, deci nici nu divulgă care e.
        raise HTTPException(404, "Firma nu există sau nu e în portofoliul cabinetului căruia îi "
                                 "aparține cheia de API folosită.")
    return r[0]


@app.post("/cabinet/api-chei")  # api_public_v1
def api_cheie_creeaza(corp: dict = Body(default={}), ctx=Depends(cere_rol("admin_firma"))):
    from core import api_public as _ap
    with db.get_conn() as conn:
        return _ap.genereaza(conn, ctx["firm"], (corp or {}).get("nume"))


@app.get("/cabinet/api-chei")  # api_public_v1
def api_chei_lista(ctx=Depends(cere_rol("admin_firma"))):
    from core import api_public as _ap
    with db.get_conn() as conn:
        return {"chei": _ap.lista(conn, ctx["firm"])}


@app.delete("/cabinet/api-chei/{kid}")  # api_public_v1
def api_cheie_revoca(kid: int, ctx=Depends(cere_rol("admin_firma"))):
    from core import api_public as _ap
    with db.get_conn() as conn:
        r = _ap.revoca(conn, ctx["firm"], kid)
    if r.get("eroare"):
        raise HTTPException(404, r["eroare"])
    return r


@app.get("/api/v1/firme")  # api_public_v1
def apiv1_firme(actx=Depends(cere_api_key)):
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("""SELECT id, nume, cui FROM public.tenants
                       WHERE accounting_firm_id=%s ORDER BY nume""", (actx["firm"],))
        return {"firme": [{"id": r[0], "nume": r[1], "cui": r[2]} for r in cur.fetchall()]}


@app.get("/api/v1/firme/{tenant_id}/facturi")  # api_public_v1
def apiv1_facturi(tenant_id: int, an: Optional[int] = None, luna: Optional[int] = None,
                  actx=Depends(cere_api_key)):
    schema = _api_schema(actx, tenant_id)
    try:
        with db.get_conn(schema) as conn:
            return {"facturi": facturi_api.lista_facturi(conn, an, luna, None)}
    except ValueError as e:   # [lot 2] acelasi refuz ca in ecran, nu un 500 catre integrator
        raise HTTPException(422, str(e))


@app.get("/api/v1/firme/{tenant_id}/kpi")  # api_public_v1
def apiv1_kpi(tenant_id: int, an: Optional[int] = None, luna: Optional[int] = None,
              actx=Depends(cere_api_key)):
    from datetime import date as _d
    from core import kpi_client as _kpi
    schema = _api_schema(actx, tenant_id)
    azi = _d.today()
    an = an or azi.year
    luna = luna or azi.month
    with db.get_conn() as conn:
        randuri = documente_api.balanta(conn, schema, an, luna)
    return {"an": an, "luna": luna, "kpi": _kpi.kpi_din_balanta(randuri)}


@app.get("/api/v1/firme/{tenant_id}/balanta")  # api_public_v1
def apiv1_balanta(tenant_id: int, an: int, luna: int, actx=Depends(cere_api_key)):
    _cere_perioada(an, luna)
    schema = _api_schema(actx, tenant_id)
    with db.get_conn() as conn:
        return {"balanta": documente_api.balanta(conn, schema, an, luna)}

# === LINK PLATA === # plati_link_v1
@app.post("/tenants/{tenant_id}/facturi/{factura_id}/link-plata")
# [R42] „iese către un om" — linkul ajunge la client, iar `platita_la` atârnă de el (R43).
def factura_link_plata(tenant_id: int, factura_id: int, ctx=Depends(cere_rol("admin_firma"))):
    from core import plati as _pl
    schema = _schema_sau_404(ctx, tenant_id)
    baza = os.environ.get("ICONTA_BAZA_URL", "https://iconta.eu")
    with db.get_conn() as conn:
        r = _pl.genereaza_link(conn, schema, factura_id, baza)
    if r.get("eroare"):
        _ec = r.get("erori_campuri")  # [G10] contract {mesaj, erori_campuri}
        raise HTTPException(422, detail={"mesaj": r["eroare"], "erori_campuri": _ec} if _ec else r["eroare"])
    return r

@app.get("/public/plata/{ref}")
def plata_pagina(ref: str):
    """Pagina mock: confirma plata (pana la integrarea provider real)."""
    return Response(content=f"""<!doctype html><html lang="ro"><meta charset="utf-8">
<title>Plata factura</title><body style="font-family:sans-serif;max-width:420px;margin:10vh auto">
<h2>Plat\u0103 factur\u0103 (demo)</h2>
<p>Integrarea cu procesatorul de pl\u0103\u021bi urmeaz\u0103. Ap\u0103sa\u021bi pentru a simula plata.</p>
<form method="post" action="/public/plata/{ref}/confirma"><button style="padding:10px 22px">Pl\u0103te\u0219te</button></form>
</body></html>""", media_type="text/html",
                    headers={"X-Robots-Tag": "noindex, nofollow"})  # [plata_noindex 15.08.2026] ref e secret in URL; daca un link ajunge la crawler, se poate cere - inchis independent de robots.txt

@app.post("/public/plata/{ref}/confirma")
def plata_confirma(ref: str):
    from core import plati as _pl
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT schema_name FROM public.tenants ORDER BY id")
        scheme = [r[0] for r in cur.fetchall()]
    for sch in scheme:
        with db.get_conn() as conn:
            r = _pl.confirma_plata(conn, sch, ref)
        if r.get("ok"):
            return {"ok": True}
    raise HTTPException(404, "referință necunoscută")

@app.post("/api/v1/firme/{tenant_id}/facturi")  # api_public_v1
def apiv1_factura_emite(tenant_id: int, corp: dict = Body(...), actx=Depends(cere_api_key)):
    # [26.08.2026] DOUA DIFERENTE FATA DE RUTA DIN ECRAN, amandoua reparate aici.
    #
    # (1) `platitor_tva` venea DIN CORPUL CERERII, cu implicit `True`. E un FAPT DESPRE FIRMA,
    #     nu despre cerere: intra in `_potriveste_linii` -> `cote_tva.potriveste_cota`, deci
    #     decide COTA de pe liniile facturii. Un integrator care nu-l trimite ar fi facturat cu
    #     TVA o firma neplatitoare. Ruta din ecran il citeste din `firma_profil`
    #     (`_platitor_tva_firma`); acum si aceasta. E interdictia 45 (P20): o valoare intrata
    #     din afara, fara sursa si grad de certitudine, peste un fapt pe care il stim.
    #     Masurat inainte de reparatie: `public.api_chei` = 0, deci efectul n-a fost produs.
    # (2) Numele beneficiarului nu era cerut, desi ruta din ecran il refuza explicit — iar o
    #     factura fara beneficiar nu e factura.
    #
    # CE RAMANE DIFERIT, DECLARAT: poarta „pleaca marfa acum?" (descarcarea gestiunii) nu se
    # poate pune pe o cale neinteractiva fara sa alegem in locul integratorului. E o decizie de
    # produs, consemnata, nu una tehnica.
    schema = _api_schema(actx, tenant_id)
    if not str(corp.get("tert_nume") or "").strip():
        raise HTTPException(422, "Denumirea beneficiarului e obligatorie pe factură.")
    # [R57, decizia lui Costin 26.08.2026] Aceeași poartă ca în ecran, dar pe o cale
    # neinteractivă nu se poate ÎNTREBA — deci se REFUZĂ fără răspuns explicit. Motivul lui:
    # *„un implicit, oricare ar fi, alege în locul integratorului: «descarcă» îl face să descarce
    # gestiunea fără să știe; «nu descarcă» lasă stocul greșit fără să afle."* Iar refuzul e
    # ieftin acum — `public.api_chei` = 0 — și ar fi imposibil de introdus peste un an.
    # Câmpul spune CE SE ÎNTÂMPLĂ, nu ce face codul: `marfa_pleaca_cu_factura`.
    _linii = corp.get("linii") or []
    _tip = corp.get("tip", "factura")
    _poarta_ceruta = (_tip == "factura") and any(
        isinstance(l, dict) and l.get("articol_id") for l in _linii)
    _pleaca = corp.get("marfa_pleaca_cu_factura")
    if _poarta_ceruta and _pleaca is None:
        raise HTTPException(422, detail={
            "cod": "POARTA_GESTIUNE_FARA_RASPUNS",
            "mesaj": ("Factura are linii de stoc, deci trebuie spus dacă marfa pleacă odată cu ea. "
                      "Nu există un răspuns implicit: unul ar descărca gestiunea fără știrea ta, "
                      "celălalt ar lăsa stocul greșit fără să afli."),
            "camp": "marfa_pleaca_cu_factura",
            "valori": {"true": "marfa pleacă acum — se descarcă gestiunea în aceeași tranzacție",
                       "false": "marfa nu pleacă acum — factura e doar fiscală, stocul rămâne"}})
    with db.get_conn(schema) as conn:
        # [lot 2, 03.09.2026] Ruta din ecran traducea de mult `ValueError` in `422`; asta nu —
        # deci `linii=[]` sau un cod de partener lipsa ieseau catre integrator ca
        # `500 Internal Server Error`, adica fara nicio vorba despre ce lipseste.
        try:
            r = facturi_api.emite_factura(
                conn,
                linii=corp.get("linii"),
                client_id=corp.get("client_id"),
                tert_nume=corp.get("tert_nume"),
                tert_cui=corp.get("tert_cui"),
                tert_adresa=corp.get("tert_adresa"),
                data_emitere=corp.get("data_emitere"),
                data_scadenta=corp.get("data_scadenta"),
                moneda=corp.get("moneda", "RON"),
                platitor_tva=_platitor_tva_firma(conn),
                status=corp.get("status", "de_preluat"),
                curs_manual=corp.get("curs_manual"),
                data_curs_manual=corp.get("data_curs_manual"),   # [R130] data cursului manual
                # [R130] Pe calea de API „cine" e CHEIA cabinetului, nu un utilizator — se scrie ca
                # atare. Un `integer` de utilizator ar fi trebuit sa inventeze unul.
                curs_manual_de="cheie API a cabinetului %s" % actx["firm"],
                tip=_tip,
            )
        except facturi_api.LiniiIncomplete as e:
            raise HTTPException(422, {"cod": "LINII_INCOMPLETE",
                                      "mesaj": "Completează liniile: "
                                               + "; ".join(x["eticheta"] for x in e.campuri),
                                      "campuri": e.campuri})
        except ValueError as e:
            raise HTTPException(422, str(e))
        # [R57] Acelasi efect ca in ecran: descarcarea se face DOAR la raspuns afirmativ si in
        # ACEEASI tranzactie cu emiterea (atomic), nu intr-un al doilea apel al integratorului.
        if _poarta_ceruta and _pleaca is True and isinstance(r, dict) and r.get("factura_id"):
            from core import stocuri_cv_api as _cv_api
            from datetime import date as _dt_api
            r["descarcare"] = _cv_api.descarca_factura(
                conn, schema, r["factura_id"],
                corp.get("data_emitere") or _dt_api.today().isoformat())
    if not r.get("ok", True) and r.get("cod") == "MONEDA_NECOTATA":
        raise HTTPException(422, r.get("mesaj"))      # [lot 2] aceeasi deosebire ca in ecran
    if not r.get("ok", True) and r.get("cod") == "CURS_PREA_VECHI":
        raise HTTPException(409, detail=r)            # [R130] acelasi refuz cu iesire ca in ecran
    if not r.get("ok", True) and r.get("cod") == "CURS_INDISPONIBIL":
        raise HTTPException(422, r.get("mesaj"))
    return r


@app.post("/tenants/{tenant_id}/woocommerce/sincronizeaza")  # wc_sinc_v1
def wc_sinc(tenant_id: int, ctx=Depends(cere_rol("admin_firma"))):
    from core import woocommerce as _wc
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        r = _wc.sincronizeaza(conn, schema)
    if r.get("eroare"):
        _ec = r.get("erori_campuri")  # [G10] contract {mesaj, erori_campuri}
        raise HTTPException(422, detail={"mesaj": r["eroare"], "erori_campuri": _ec} if _ec else r["eroare"])
    return r


@app.get("/tenants/{tenant_id}/woocommerce/config")  # wc_config_get_v1
def wc_config_get(tenant_id: int, ctx=Depends(cere_context)):
    schema = _schema_sau_404(ctx, tenant_id)
    # [wc_config_no_mask] o eroare de DB NU se ambaleaza intr-un 200 "neconfigurat" (masca cat.0) - se propaga
    # (500), iar frontend-ul arata eroare vizibila. "neconfigurat" ramane DOAR pentru lipsa reala de rand (r None).
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute(f"SELECT wc_url, (wc_ck IS NOT NULL AND wc_cs IS NOT NULL) AS are_chei FROM {schema}.firma_profil LIMIT 1")
        r = cur.fetchone()
    if not r:
        return {"configurat": False, "url": None}
    return {"configurat": bool(r[0] and r[1]), "url": r[0]}
@app.put("/tenants/{tenant_id}/woocommerce/config")  # wc_sinc_v1
# [R42 (d)] Pornirea și oprirea unui canal cer `admin_firma`. Costin: *„nu e organizare internă —
# e o decizie despre cum comunică firma cu autoritatea și cu clienții."* Ruta asta scrie chiar
# cheile canalului: cu ele pline canalul e pornit, golite îl oprește.
def wc_config(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_rol("admin_firma"))):
    schema = _schema_sau_404(ctx, tenant_id)
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute(f"""UPDATE {schema}.firma_profil
                        SET wc_url=%s, wc_ck=%s, wc_cs=%s""",
                    (corp.get("url"), corp.get("ck"), corp.get("cs")))
        conn.commit()
    return {"ok": True}


@app.get("/cabinet/consolidare")  # consolidare_v1
def cabinet_consolidare(an: Optional[int] = None, luna: Optional[int] = None,
                        ctx=Depends(cere_cabinet)):
    from datetime import date as _d
    from core import kpi_client as _kpi
    azi = _d.today()
    an = an or azi.year
    luna = luna or azi.month
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("""SELECT id, nume, schema_name FROM public.tenants
                       WHERE accounting_firm_id = %s ORDER BY nume""",
                    (ctx["firm"],))
        tenanti = cur.fetchall()
    firme = []
    total = {"venituri": 0, "cheltuieli": 0, "profit": 0,
             "cash": 0, "de_incasat": 0, "de_platit": 0}
    with db.get_conn() as conn:
        for tid, nume, schema in tenanti:
            try:
                k = _kpi.kpi_din_balanta(documente_api.balanta(conn, schema, an, luna))
            except Exception:
                k = None
            firme.append({"tenant_id": tid, "nume": nume, "kpi": k})
            if k:
                for c in total:
                    total[c] = round(total[c] + k[c], 2)
    return {"an": an, "luna": luna, "firme": firme, "total": total}


@app.get("/portal/kpi")  # portal_kpi_v1
def portal_kpi(an: Optional[int] = None, luna: Optional[int] = None,
               tenant_id: Optional[int] = None, ctx=Depends(cere_client)):
    from datetime import date as _d
    from core import kpi_client as _kpi
    t = _tenant_client(ctx, tenant_id)
    azi = _d.today()
    an = an or azi.year
    luna = luna or azi.month
    with db.get_conn() as conn:
        randuri = documente_api.balanta(conn, t["schema_name"], an, luna)
    return {"an": an, "luna": luna, "kpi": _kpi.kpi_din_balanta(randuri)}


@app.get("/portal/cashflow")  # portal_cashflow_v1
def portal_cashflow(tenant_id: Optional[int] = None, ctx=Depends(cere_client)):
    from datetime import date as _d
    from core import kpi_client as _kpi
    from core import cashflow as _cf
    t = _tenant_client(ctx, tenant_id)
    azi = _d.today()
    with db.get_conn() as conn:
        randuri = documente_api.balanta(conn, t["schema_name"], azi.year, azi.month)
    k = _kpi.kpi_din_balanta(randuri)
    with db.get_conn(t["schema_name"]) as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT directie, data_emitere, data_scadenta, total
                           FROM facturi WHERE tip='factura' AND storno_din_id IS NULL""")
            fs = [{"directie": r[0], "data_emitere": str(r[1]),
                   "data_scadenta": str(r[2]) if r[2] else None, "total": float(r[3] or 0)}
                  for r in cur.fetchall()]
    emise = _cf.aloca_sold([f for f in fs if f["directie"] == "emisa"], k["de_incasat"])
    primite = _cf.aloca_sold([f for f in fs if f["directie"] == "primita"], k["de_platit"])
    obligatii = _cf.obligatii_din_balanta(randuri)  # portal_cashflow_v2
    medie = _cf.cheltuieli_lunare_cash(randuri, azi.month)
    primite = primite + _cf.plati_estimate(obligatii, medie, azi=azi)
    return {"cash": k["cash"], "medie_cheltuieli": medie,
            "saptamani": _cf.forecast(k["cash"], emise, primite, azi=azi)}


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
        raise HTTPException(400, EMAIL_NICIUNUL_VALID)
    if len(emails) > 20:
        raise HTTPException(400, "Maxim 20 de emailuri odata.")
    rezultate = []
    for em in emails:
        ok = _obs.trimite_email_html(em, subiect, html)
        rezultate.append({"email": em, "stare": "trimis" if ok else "esuat"})
    return rezultate

def _mesaj_recomanda_client_html(nume_firma):
    return (
        "<div style='font-family:sans-serif;font-size:15px;color:#111;max-width:540px;line-height:1.55'>"
        "<p>Buna,</p>"
        "<p>Sunt client iConta.eu si ma tine departe de batai de cap cu ANAF - "
        "imi arata din timp daca am ceva de depus sau de platit, inainte sa fie o problema.</p>"
        "<p>M-am gandit ca ti-ar prinde bine si tie.</p>"
        "<p style='margin:24px 0'><a href='https://iconta.eu' style='background:#2563eb;color:#fff;"
        "padding:12px 22px;border-radius:8px;text-decoration:none;font-weight:600'>Vezi iConta.eu</a></p>"
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

@app.get("/portal/solicitari/contor")  # [icrd_sol_badge_v1] necitite de la cabinet, pt clientul curent
def portal_solicitari_contor(tenant_id: Optional[int] = None, ctx=Depends(cere_client)):
    t = _tenant_client(ctx, tenant_id)
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT count(*) FROM public.solicitari_client "
                "WHERE tenant_id=%s AND autor_rol='cabinet' AND citit=false", (t["id"],))
            n = cur.fetchone()[0]
    return {"necitite": n}

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
                    "SELECT id FROM public.users WHERE accounting_firm_id=%s AND activ=true "
                    "AND rol IN ('admin_firma', 'angajat')", (r[0],))
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
# [R42] „iese către un om" — răspunsul pleacă pe email la clientul firmei.
def cabinet_solicitari_raspunde(tenant_id: int, date: SolicitareIn,
                                ctx=Depends(cere_rol("admin_firma"))):
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
        raise HTTPException(status_code=403, detail=DOAR_ADMIN_CABINET)
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
            raise HTTPException(status_code=404, detail=mesaj_din_cod(r.get("cod")))
        return r


# === ASISTENT NOU === # asistent_nou_v1
class AsistentNouIn(BaseModel):
    email: str
    nume: str = ""
    poate_valida: bool = False

@app.post("/asistenti")
def asistent_creeaza(date: AsistentNouIn, ctx=Depends(cere_rol("admin_firma"))):
    from core import nucleu as _nucleu
    import secrets as _sec
    email = date.email.strip().lower()
    if "@" not in email:
        raise HTTPException(422, EMAIL_INVALID)
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
            cur.execute("SELECT id, activ FROM public.users WHERE email=%s", (email,))
            if cur.fetchone():
                raise HTTPException(422, EMAIL_EXISTA)
            cur.execute("""INSERT INTO public.users (email, password_hash, nume, rol, accounting_firm_id, activ, poate_valida)
                           VALUES (%s, %s, %s, 'angajat', %s, true, %s) RETURNING id""",
                        (email, _nucleu.hash_parola(_sec.token_urlsafe(16)),
                         date.nume or email.split("@")[0], ctx["firm"], date.poate_valida))
            uid = cur.fetchone()["id"]
        with conn.cursor() as cur:
            tok = _sec.token_urlsafe(32)
            _pune_token(cur, tok, uid, "48 hours")
    baza = os.environ.get("ICONTA_BAZA_URL", "http://localhost:8010")
    link = baza + "/#activare=" + tok
    html = ("<p>Buna,</p><p>Ai fost adaugat ca asistent in cabinetul tau pe iConta.eu.</p>"
            "<p><a href='%s' style='display:inline-block;background:#3d8fd6;color:#fff;padding:10px 22px;border-radius:6px;text-decoration:none'>Activeaza contul</a></p>"
            "<p>Dupa activare, intra cu emailul <b>%s</b> si parola setata. Linkul e valabil 48 de ore.</p>") % (link, email)
    try:
        _obs.trimite_email_html(email, "Acces asistent iConta.eu", html)
    except Exception as _e:
        # [R73] ALERTA: fara linkul de activare, asistentul nu are cont.
        _obs.esec_secundar("email invitatie asistent", _e, alerta=True)
    return {"ok": True, "user_id": uid}

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
            raise HTTPException(status_code=400, detail=mesaj_din_cod(r.get("cod")))
        return r


@app.post("/asistenti/{uid}/firme/{tid}")
def asistenti_atribuie(uid: int, tid: int, ctx=Depends(cere_cabinet)):
    cabinet_id = _cer_admin_cabinet(ctx)
    with db.get_conn() as conn:
        r = _asist.atribuie_firma(conn, cabinet_id, uid, tid)
        if not r.get("ok"):
            raise HTTPException(status_code=400, detail=mesaj_din_cod(r.get("cod")))
        return r


@app.delete("/asistenti/{uid}/firme/{tid}")
def asistenti_elimina(uid: int, tid: int, ctx=Depends(cere_cabinet)):
    cabinet_id = _cer_admin_cabinet(ctx)
    with db.get_conn() as conn:
        r = _asist.elimina_firma(conn, cabinet_id, uid, tid)
        if not r.get("ok"):
            raise HTTPException(status_code=400, detail=mesaj_din_cod(r.get("cod")))
        return r


@app.post("/asistenti/{uid}/dezactiveaza")
def asistenti_dezactiveaza(uid: int, ctx=Depends(cere_cabinet)):
    cabinet_id = _cer_admin_cabinet(ctx)
    with db.get_conn() as conn:
        r = _asist.dezactiveaza(conn, cabinet_id, uid, ctx["uid"])
        if not r.get("ok"):
            raise HTTPException(status_code=400, detail=mesaj_din_cod(r.get("cod")))
        return r


@app.post("/asistenti/{uid}/reactiveaza")
def asistenti_reactiveaza(uid: int, ctx=Depends(cere_cabinet)):
    cabinet_id = _cer_admin_cabinet(ctx)
    with db.get_conn() as conn:
        r = _asist.reactiveaza(conn, cabinet_id, uid)
        if not r.get("ok"):
            raise HTTPException(status_code=400, detail=mesaj_din_cod(r.get("cod")))
        return r



# [patch7_finalizeaza_firme]
@app.post("/asistenti/{uid}/finalizeaza-firme")
def asistenti_finalizeaza_firme(uid: int, ctx=Depends(cere_cabinet)):
    cabinet_id = _cer_admin_cabinet(ctx)
    with db.get_conn() as conn:
        r = _asist.aplica_regula_zero_firme(conn, cabinet_id, uid)
        if not r.get("ok"):
            raise HTTPException(status_code=400, detail=mesaj_din_cod(r.get("cod")))
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
            raise HTTPException(404, mesaj_din_cod(r.get("cod")))
        return r


@app.get("/asistenti/{uid}/activitate")
def asistenti_activitate(uid: int, ctx=Depends(cere_cabinet)):
    cabinet_id = _cer_admin_cabinet(ctx)
    with db.get_conn() as conn:
        r = _asist.activitate(conn, cabinet_id, uid)
        if not r.get("ok"):
            raise HTTPException(status_code=404, detail=mesaj_din_cod(r.get("cod")))
        return r


# [p18_selfview]
@app.get("/eu/calitate")
def eu_calitate(de: Optional[str] = None, pana: Optional[str] = None,
                ctx=Depends(cere_cabinet)):
    """Self-view: propria calitate (nivel, semafor, rata, tipare). uid din token."""
    with db.get_conn() as conn:
        r = _asist.calitate(conn, ctx["firm"], ctx["uid"], de=de, pana=pana)
        if not r.get("ok"):
            raise HTTPException(404, mesaj_din_cod(r.get("cod")))
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

@app.get("/eu/patru-ochi")  # po_stare_v1
def eu_patru_ochi_stare(ctx=Depends(cere_cabinet)):
    """[po_efectiv_v1] {activ, posibil, efectiv} din SURSA UNICA folosita si de enforcement
    (core.coada_api.patru_ochi_stare). Inainte intorcea DOAR flagul brut `activ`, iar UI-ul
    afisa "validarea in doi ✓" pe un cabinet cu un singur validator - divergenta front<->back."""
    with db.get_conn() as conn:
        return coada_api.patru_ochi_stare(conn, ctx["firm"])

@app.post("/eu/patru-ochi")
def eu_patru_ochi(date: PatruOchiIn, ctx=Depends(cere_cabinet)):
    if ctx["rol"] not in ("admin_firma", "superadmin"):
        raise HTTPException(403, DOAR_PATRON)
    with db.get_conn() as conn:
        return _asist.patru_ochi_seteaza(conn, ctx["firm"], date.activ)


@app.post("/eu/educatie/patru-ochi/vazut")
def eu_educatie_vazut(ctx=Depends(cere_cabinet)):
    if ctx["rol"] not in ("admin_firma", "superadmin"):
        raise HTTPException(403, DOAR_PATRON)
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
    if not _nucleu.parola_ok(date.parola_noua):
        raise HTTPException(400, _nucleu.PAROLA_MESAJ)
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
        raise HTTPException(422, mesaj_din_cod(r.get("cod")))
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
        raise HTTPException(404, mesaj_din_cod(r.get("cod")))
    return r


@app.post("/eu/cabinet")
def eu_cabinet_set(date: CabinetIn, ctx=Depends(cere_cabinet)):
    if ctx["rol"] not in ("admin_firma", "superadmin"):
        raise HTTPException(403, "Doar administratorul cabinetului poate edita datele cabinetului.")
    with db.get_conn() as conn:
        r = auth_api.actualizeaza_cabinet(conn, ctx["firm"], nume=date.nume, cui=date.cui)
    if not r.get("ok"):
        raise HTTPException(422, mesaj_din_cod(r.get("cod")))
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
        "<p>" + cine + " folosește <b>iConta.eu</b> și s-a gândit că ți-ar prinde bine și ție.</p>"
        "<p>iConta.eu e contabilitatea în cloud care lucrează pentru tine și echipa ta:</p>"
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
        "padding:12px 22px;border-radius:8px;text-decoration:none;font-weight:600'>Încearcă iConta.eu</a></p>"
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
            "subiect": "O recomandare pentru cabinetul tau: iConta.eu"}

@app.post("/recomanda")
def trimite_recomandari(date: RecomandareIn, ctx=Depends(cere_cabinet)):
    emails = [e.strip() for e in (date.emails or []) if e and e.strip()]
    with db.get_conn() as conn:
        r = auth_api.get_cabinet(conn, ctx["firm"])
    nume_cabinet = (r.get("cabinet") or {}).get("nume", "") if r.get("ok") else ""
    html = _mesaj_promo_html(nume_cabinet)
    rezultate = _trimite_recomandari(emails, html, "O recomandare pentru cabinetul tau: iConta.eu")
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
        raise HTTPException(400, mesaj_din_cod(r.get("cod")))
    # [triaj_ai] AI raspunde la intrebarile de folosire sau escaladeaza (pentru_admin); nu blocheaza crearea
    import threading
    from core import raportari_ai as _rai
    threading.Thread(target=_rai.proceseaza, args=(r["raportare_id"], date.subiect, date.text), daemon=True).start()
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
        raise HTTPException(403, DOAR_ADMIN_ICONTA)
    with db.get_conn() as conn:
        return _rap.toate_raportarile(conn)


@app.get("/raportari/{rid}")
def raportari_fir(rid: int, ctx=Depends(cere_cabinet)):
    with db.get_conn() as conn:
        r = _rap.firul_complet(conn, rid, cerut_de_uid=ctx["uid"], e_superadmin=(ctx["rol"] == "superadmin"))
        if not r.get("ok"):
            raise HTTPException(404, mesaj_din_cod(r.get("cod")))
        # acces: autorul firului sau superadmin
        if ctx["rol"] != "superadmin" and r["raportare"]["autor_id"] != ctx["uid"]:
            raise HTTPException(403, FARA_ACCES_RAPORTARE)
        return r


@app.post("/raportari/{rid}/mesaj")
def raportari_mesaj(rid: int, date: MesajIn, ctx=Depends(cere_cabinet)):
    rol_autor = "admin" if ctx["rol"] == "superadmin" else "utilizator"
    with db.get_conn() as conn:
        # utilizatorul poate scrie doar in firele lui
        if rol_autor == "utilizator":
            f = _rap.firul_complet(conn, rid, cerut_de_uid=ctx["uid"], e_superadmin=False)
            if not f.get("ok"):
                raise HTTPException(404, "Inexistent.")
            if f["raportare"]["autor_id"] != ctx["uid"]:
                raise HTTPException(403, FARA_ACCES)
        r = _rap.adauga_mesaj(conn, rid, ctx["uid"], rol_autor, date.text)
    if not r.get("ok"):
        raise HTTPException(400, mesaj_din_cod(r.get("cod")))
    return r


@app.post("/raportari/{rid}/citit")
def raportari_citit(rid: int, ctx=Depends(cere_cabinet)):
    cine_rol = "admin" if ctx["rol"] == "superadmin" else "utilizator"
    with db.get_conn() as conn:
        # [izolare_raportari 09.08.2026] utilizatorul marcheaza citit DOAR firele lui (nu ale altui cabinet)
        if cine_rol == "utilizator":
            f = _rap.firul_complet(conn, rid, cerut_de_uid=ctx["uid"], e_superadmin=False)
            if not f.get("ok"):
                raise HTTPException(404, "Inexistent.")
        return _rap.marcheaza_citit(conn, rid, cine_rol)


# [p38_pentru_admin]
class StareIn(BaseModel):
    stare: str

class PentruAdminIn(BaseModel):
    valoare: bool = True

@app.post("/raportari/{rid}/stare")  # [inchidere_v1]
def raportari_stare(rid: int, date: StareIn, ctx=Depends(cere_rol("superadmin"))):
    with db.get_conn() as conn:
        r = _rap.seteaza_stare(conn, rid, date.stare)
        conn.commit()
    if not r.get("ok"):
        raise HTTPException(400, mesaj_din_cod(r.get("cod")))
    return r

@app.post("/raportari/{rid}/pentru-admin")
def raportari_pentru_admin(rid: int, date: PentruAdminIn, ctx=Depends(cere_cabinet)):
    if ctx["rol"] != "superadmin":
        raise HTTPException(403, DOAR_ADMIN_ICONTA)
    with db.get_conn() as conn:
        r = _rap.seteaza_pentru_admin(conn, rid, date.valoare)
    if not r.get("ok"):
        raise HTTPException(404, mesaj_din_cod(r.get("cod")))
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
            raise HTTPException(403, FARA_ACCES)
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
        raise HTTPException(400, mesaj_din_cod(r.get("cod")))
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
            raise HTTPException(404, "tenant inexistent sau fără acces")
        return {"linii": _rec.importa_extras(conn, schema, tranzactii, fisier.filename or "")}

@app.get("/tenants/{tenant_id}/banca/reconciliere")
def banca_rec_lista(tenant_id: int, status: str = None, ctx=Depends(cere_cabinet)):
    from core import reconciliere_api as _rec
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        return {"linii": _rec.lista(conn, schema, status)}

@app.post("/tenants/{tenant_id}/banca/reconciliere/{linie_id}/conteaza")
def banca_rec_conteaza(tenant_id: int, linie_id: int, corp: dict = Body(default={}), ctx=Depends(cere_cabinet)):
    from core import reconciliere_api as _rec
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        rez = _rec.conteaza(conn, schema, linie_id, corp.get("alocari"))
    if rez is None:
        raise HTTPException(404, "linie inexistentă")
    if rez.get("eroare"):
        raise HTTPException(400, rez["eroare"])
    return rez


@app.get("/tenants/{tenant_id}/banca/reconciliere/facturi-deschise")
def banca_rec_facturi(tenant_id: int, ctx=Depends(cere_cabinet)):
    from core import reconciliere_api as _rec
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        return {"facturi": _rec.facturi_deschise_detalii(conn, schema)}


# --- rapoarte comerciale (F144 v1, read-only) ---
def _perioada_an(de, pana):
    """Fallback: daca lipsesc, perioada = anul curent (01.01 - 31.12)."""
    import datetime
    an = datetime.date.today().year
    return (de or f"{an}-01-01", pana or f"{an}-12-31")

@app.get("/tenants/{tenant_id}/rapoarte-comerciale")
def rapoarte_comerciale(tenant_id: int, de: str = None, pana: str = None, ctx=Depends(cere_cabinet)):
    from core import rapoarte_comerciale_api as _rc
    de, pana = _perioada_an(de, pana)
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant_citire(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        return {"vanzari": _rc.vanzari_pe_partener(conn, schema, de, pana),
                "durata_incasare": _rc.durata_medie_incasare(conn, schema, de, pana),
                "parteneri": _rc.lista_parteneri(conn, schema),
                "profit_produs": _rc.profit_pe_produs(conn, schema, de, pana),  # [punte_stoc_v1] F144 LIVE la CV
                "de": de, "pana": pana}

@app.get("/tenants/{tenant_id}/rapoarte-comerciale/fisa")
def rapoarte_comerciale_fisa(tenant_id: int, cui: str, de: str = None, pana: str = None, ctx=Depends(cere_cabinet)):
    from core import rapoarte_comerciale_api as _rc
    de, pana = _perioada_an(de, pana)
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant_citire(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        return _rc.fisa_partener(conn, schema, cui, de, pana)


# --- rapoarte salvate (F145: variante ale firmei, partajate) ---
@app.get("/tenants/{tenant_id}/rapoarte-salvate")
def rapoarte_salvate_lista(tenant_id: int, tip_raport: str = "comercial", ctx=Depends(cere_cabinet)):
    from core import rapoarte_comerciale_api as _rc
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant_citire(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        return {"variante": _rc.variante(conn, schema, tip_raport)}

@app.post("/tenants/{tenant_id}/rapoarte-salvate")
def rapoarte_salvate_creeaza(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    from core import rapoarte_comerciale_api as _rc
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        rez = _rc.salveaza_varianta(conn, schema, corp.get("tip_raport", "comercial"),
                                    corp.get("nume"), corp.get("filtru"), ctx["uid"])
    if not rez.get("ok"):
        mesaje = {"TIP_INVALID": "tip de raport necunoscut",
                  "NUME_GOL": "numele variantei e obligatoriu",
                  "NUME_EXISTA": "exista deja o varianta cu acest nume"}
        raise HTTPException(422, mesaje.get(rez.get("cod"), "eroare"))
    return rez

@app.delete("/tenants/{tenant_id}/rapoarte-salvate/{vid}")
def rapoarte_salvate_sterge(tenant_id: int, vid: int, ctx=Depends(cere_cabinet)):
    from core import rapoarte_comerciale_api as _rc
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        rez = _rc.sterge_varianta(conn, schema, vid)
    if not rez.get("ok"):
        raise HTTPException(404, "variantă inexistentă")
    return rez


# --- registratura documente (F146: registru unic intrare-iesire) ---
@app.get("/tenants/{tenant_id}/registratura")
def registratura_lista(tenant_id: int, an: int = None, ctx=Depends(cere_cabinet)):
    from core import registratura_api as _reg
    import datetime as _dt
    an = an or _dt.date.today().year
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        return _reg.lista(conn, schema, an)

@app.post("/tenants/{tenant_id}/registratura")
def registratura_creeaza(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    from core import registratura_api as _reg
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        rez = _reg.inregistreaza(conn, schema, corp, ctx["uid"])
    if not rez.get("ok"):
        mesaje = {"DIRECTIE_INVALIDA": "directie invalida (intrare/iesire)",
                  "DESCRIERE_GOALA": "descrierea e obligatorie"}
        raise HTTPException(422, mesaje.get(rez.get("cod"), "eroare"))
    return rez


# --- generare contracte din sabloane (F147: mail-merge) ---
@app.get("/contracte/marcaje")
def contracte_marcaje(ctx=Depends(cere_cabinet)):
    # nomenclator GLOBAL de marcaje de contract (nu per-tenant) - mutat din
    # /tenants/{tenant_id}/ (C-5 P1, decizie Costin): tenant_id era decorativ, ruta
    # nu atinge schema tenantului; sub /tenants/ pretindea izolare pe care n-o avea.
    from core import contracte_api as _ct
    return {"marcaje": _ct.MARCAJE}

@app.get("/tenants/{tenant_id}/contracte/sabloane")
def contracte_sabloane_lista(tenant_id: int, ctx=Depends(cere_cabinet)):
    from core import contracte_api as _ct
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        return {"sabloane": _ct.lista_sabloane(conn, schema)}

@app.post("/tenants/{tenant_id}/contracte/sabloane")
def contracte_sabloane_salveaza(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    from core import contracte_api as _ct
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        rez = _ct.salveaza_sablon(conn, schema, corp.get("id"), corp.get("nume"),
                                  corp.get("continut"), ctx["uid"])
    if not rez.get("ok"):
        mesaje = {"NUME_GOL": "numele sablonului e obligatoriu",
                  "CONTINUT_GOL": "continutul sablonului e obligatoriu",
                  "NUME_EXISTA": "exista deja un sablon cu acest nume",
                  "MARCAJ_INVALID": "marcaj necunoscut: {{%s}}" % rez.get("marcaj"),
                  "INEXISTENT": "sablon inexistent"}
        raise HTTPException(422, mesaje.get(rez.get("cod"), "eroare"))
    return rez

@app.delete("/tenants/{tenant_id}/contracte/sabloane/{sid}")
def contracte_sabloane_sterge(tenant_id: int, sid: int, ctx=Depends(cere_cabinet)):
    from core import contracte_api as _ct
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        rez = _ct.sterge_sablon(conn, schema, sid)
    if not rez.get("ok"):
        raise HTTPException(404, "sablon inexistent")
    return rez

@app.post("/tenants/{tenant_id}/contracte/genereaza")
# [R42] „iese către un om" — contractul individual de muncă.
def contracte_genereaza(tenant_id: int, corp: dict = Body(...),
                        ctx=Depends(cere_rol("admin_firma"))):
    from core import contracte_api as _ct
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        try:
            pdf = _ct.genereaza_pdf(conn, schema, corp.get("sablon_id"), corp)
        except ValueError as e:   # [R66 (c)]
            raise HTTPException(422, str(e))
    if pdf is None:
        raise HTTPException(404, "sablon inexistent")
    return Response(content=pdf, media_type="application/pdf",
                    headers={"Content-Disposition": 'attachment; filename="contract.pdf"'})


# --- export facturi emise catre SAGA (F171, read-only) ---
@app.get("/tenants/{tenant_id}/facturi/{factura_id}/export-saga")
def export_saga_factura(tenant_id: int, factura_id: int, ctx=Depends(cere_context)):
    from core import export_saga as _xs
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant_citire(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        date_f = _xs.date_factura(conn, schema, factura_id)
    if date_f is None:
        raise HTTPException(404, "factură inexistentă sau nu e emisă")
    firma, factura, linii = date_f
    xml = _xs.xml_factura(firma, factura, linii)
    nume = _xs.nume_fisier(firma.get("cui"), factura.get("numar"), factura.get("data_emitere"))
    return Response(content=xml, media_type="application/xml",
                    headers={"Content-Disposition": 'attachment; filename="%s"' % nume})

@app.post("/tenants/{tenant_id}/facturi/export-saga")
# [R45] POST: exportul e un act (ce s-a exportat și când e chiar întrebarea la o preluare
# inversă), iar un GET n-are voie să scrie.
def export_saga_luna(tenant_id: int, an: int, luna: int, ctx=Depends(cere_rol("admin_firma"))):
    from core import export_saga as _xs
    from core import artefacte as _art
    import io as _io, zipfile as _zip
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        ids = _xs.facturi_emise_luna(conn, schema, an, luna)
        if not ids:
            raise HTTPException(404, "nicio factură emisă în luna aleasă")
        buf = _io.BytesIO()
        with _zip.ZipFile(buf, "w", _zip.ZIP_DEFLATED) as z:
            for fid in ids:
                d = _xs.date_factura(conn, schema, fid)
                if not d:
                    continue
                firma, factura, linii = d
                z.writestr(_xs.nume_fisier(firma.get("cui"), factura.get("numar"), factura.get("data_emitere")),
                           _xs.xml_factura(firma, factura, linii))
    nume_zip = "export_saga_%04d_%02d.zip" % (an, luna)
    # [R45] Arhiva se păstrează întreagă (base64 în coloană), iar amprenta e pe OCTEȚII ei.
    with db.get_conn() as _c:
        _art.pastreaza(_c, schema, "export_saga", "%04d-%02d" % (an, luna), buf.getvalue(),
                       produs_de_id=int(ctx["uid"]), produs_de=ctx.get("nume") or str(ctx["uid"]))
    return Response(content=buf.getvalue(), media_type="application/zip",
                    headers={"Content-Disposition": 'attachment; filename="%s"' % nume_zip})


@app.post("/tenants/{tenant_id}/facturi/export-winmentor")  # [F187]
# [R45] POST: acelasi motiv ca la SAGA — exportul e un act, iar un GET n-are voie sa scrie.
def export_winmentor_luna(tenant_id: int, an: int, luna: int,
                          ctx=Depends(cere_rol("admin_firma"))):
    """Export WinMENTOR: Facturi.txt + Articole.txt (Windows-1250) co-locate intr-un zip.
    Facturile emise ale lunii (paritate cu SAGA, fara filtru status). Dependenta de config nomenclator WinMentor (vezi export_winmentor)."""
    from core import export_winmentor as _wm
    from core import artefacte as _art
    import io as _io, zipfile as _zip
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        try:
            fisiere = _wm.export_luna(conn, schema, an, luna)
        except ValueError as e:  # caracter neencodabil cp1250 -> nu scrie byte gresit tacit
            raise HTTPException(422, str(e))
    if not fisiere:
        raise HTTPException(404, "nicio factură emisă în luna aleasă")
    buf = _io.BytesIO()
    with _zip.ZipFile(buf, "w", _zip.ZIP_DEFLATED) as z:
        for nume, continut in fisiere.items():
            z.writestr(nume, continut)
    nume_zip = "export_winmentor_%04d_%02d.zip" % (an, luna)
    # [R45] Arhiva se pastreaza intreaga (base64), amprenta pe octetii ei.
    with db.get_conn() as _c:
        _art.pastreaza(_c, schema, "export_winmentor", "%04d-%02d" % (an, luna), buf.getvalue(),
                       produs_de_id=int(ctx["uid"]), produs_de=ctx.get("nume") or str(ctx["uid"]))
    return Response(content=buf.getvalue(), media_type="application/zip",
                    headers={"Content-Disposition": 'attachment; filename="%s"' % nume_zip})


# --- jurnal: editare/stergere/validare ciorne ---
def _jurnal_rez(rez):
    if rez is None:
        raise HTTPException(404, "notă inexistentă")
    if rez.get("eroare"):
        # [31.08.2026] Refuzul poartă temeiul mai departe, pe contractul comun
        # `detail.erori_campuri`. Până azi îl turtea într-un șir: producătorul putea spune sub ce
        # normă refuză, iar ruta arunca partea aia. Interdicția 77 pe cea mai folosită cale de
        # scriere — măsurată în exercițiul de intrare din 31.08, 12 refuzuri fără niciun temei.
        if rez.get("temei"):
            # Producătorul întoarce o AFIRMAȚIE tipată (`neconformitate`); ruta o trece mai departe
            # întreagă, nu construiește un al doilea obiect din bucăți. Prima formă o reconstruia,
            # și era ea însăși o afirmație netipată — prinsă de gardul din 21.08.
            det = dict(rez)
            det["mesaj"] = rez["eroare"]
            if rez.get("camp"):
                det["erori_campuri"] = [{"camp": rez["camp"], "mesaj": rez["eroare"]}]
            raise HTTPException(400, det)
        raise HTTPException(400, rez["eroare"])
    return rez

@app.post("/tenants/{tenant_id}/jurnal")
def jurnal_creeaza(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    from core import jurnal_api as _j
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        _cere_luna_deschisa(conn, schema, corp.get("data"))
        return _jurnal_rez(_j.creeaza(conn, schema, corp.get("descriere"), corp.get("data"), corp.get("linii")))
@app.put("/tenants/{tenant_id}/jurnal/{nota_id}")
def jurnal_editeaza(tenant_id: int, nota_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    from core import jurnal_api as _j
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        _cere_perioada_deschisa(conn, schema, nota_id)
        return _jurnal_rez(_j.editeaza(conn, schema, nota_id,
                                       corp.get("descriere"), corp.get("data"), corp.get("linii")))

@app.delete("/tenants/{tenant_id}/jurnal/{nota_id}")
def jurnal_sterge(tenant_id: int, nota_id: int, ctx=Depends(cere_cabinet)):
    from core import jurnal_api as _j
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        _cere_perioada_deschisa(conn, schema, nota_id)
        return _jurnal_rez(_j.sterge(conn, schema, nota_id))

@app.post("/tenants/{tenant_id}/jurnal/{nota_id}/dezleaga")  # [api_intern_v1] fara buton in UI, pastrat deliberat: MASURAT 29.08.2026 — nicio cale din `static/` nu sterge o factura (`api.del` pe facturi nu exista; cel de la 1015 e pe `facturi-recurente`), deci si `DELETE /facturi/{id}` e act de API. Dezlegarea e perechea lui: ar fi singurul buton dintr-un drum care n-are ecran. Clasa e R70 (rute fara apelant), iar orbirea detectorului pe cai compuse e R80 — amandoua deja deschise. R92 NU exista: comentariul asta a numit-o dintr-o forma intermediara a deciziei, iar o trimitere la ceva inexistent se semnaleaza, nu se lasa.
# [R90, 29.08.2026 — varianta (a), decizia lui Costin] Rolul e `admin_firma`, nu `cere_cabinet`, și
# criteriul e cel din **R55**, nu din R42 — corectat: prima formă a comentariului scria „R42", iar
# registrul și excepția din `core/test_r42_criteriu.py` spun R55. R42 e despre *ce se predă*; nota nu
# se predă. R55 e despre *ce schimbă ce datorează firma*, iar actul ăsta schimbă: dezlegarea unei
# plăți face factura să reapară ca neîncasată în `reconciliere_api.facturi_deschise`, care calculează
# soldul chiar din notele legate prin `factura_id`. Deci nu e o corecție de fișă, e o schimbare de
# sold. *Ruta de reactivare a unei linii de extras a rămas pe `cere_cabinet` fiindcă ea nu atinge
# nicio notă legată; asta atinge.*
def jurnal_dezleaga(tenant_id: int, nota_id: int, corp: dict = Body(default={}),
                    ctx=Depends(cere_rol("admin_firma"))):
    """RUPE legătura notă↔factură, cu URMĂ. Cerut de R90: până azi cheia străină
    `inregistrari_factura_id_fkey` (fără `ON DELETE`) bloca ștergerea facturii pentru ORICE notă
    legată, inclusiv o plată — iar dezlegarea nu exista ca act.

    **De ce un act explicit și nu o dezlegare automată la ștergere** (cele două forme ale variantei
    (a), vezi `DECIZII.md`): urma. O dezlegare făcută pe furiș, ca efect secundar al unei ștergeri,
    n-ar avea nici autor, nici motiv, nici moment propriu — iar după ștergere nici n-ai mai putea
    spune ce s-a dezlegat. Aici fiecare dezlegare e o faptă cu numele ei.

    **Motivul e OBLIGATORIU.** Actul repară o eroare de reconciliere; fără motiv, peste șase luni
    nimeni nu mai poate spune dacă potrivirea a fost greșită sau dacă cineva a vrut doar să scape de
    o factură."""
    from core import contare_facturi as _cf
    motiv = (corp.get("motiv") or "").strip()
    if not motiv:
        from core import afirmatii as _af
        raise HTTPException(422, dict(_af.afirmatie(
            "neconformitate", "MOTIV_OBLIGATORIU",
            "Scrie motivul dezlegării: actul repară o potrivire greșită, iar peste șase luni "
            "urma fără motiv nu mai spune dacă a fost o eroare sau o scăpare.",
            unde="nota #%s" % nota_id, regula="dezlegarea unei note poartă motivul"),
            cod="MOTIV_OBLIGATORIU"))
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        # P15, prin helperul canonic — același pe care îl cheamă editarea, ștergerea și validarea
        # unei note care există. Dezlegarea schimbă soldul facturii, deci e o modificare a lunii.
        _cere_perioada_deschisa(conn, schema, nota_id)
        try:
            with _cf.cursor_dict(conn) as cur:
                fid = _cf.dezleaga_nota(cur, schema, nota_id)
        except _cf.RefuzContare as e:
            conn.rollback()
            if e.cod == "NOTA_INEXISTENTA":
                raise HTTPException(404, e.mesaj)
            raise HTTPException(422, e.mesaj)
        _urma_dezlegare(conn, ctx.get("uid"), tenant_id, nota_id, fid, motiv)
        conn.commit()
    # Fără cheie de revendicare în răspuns (`motiv` e una): afirmațiile despre datele firmei sunt
    # obiecte tipate, iar aici motivul e ecoul intrării, nu o afirmație a aplicației. Urma îl poartă.
    return {"ok": True, "nota_id": nota_id, "factura_id_dezlegata": fid}


def _urma_dezlegare(conn, uid, tenant_id, nota_id, factura_id, motiv):
    """URMA actului, ca FAPTĂ, nu doar ca linie de acces.

    Middleware-ul de audit scrie deja `POST <cale>` cu statusul, pentru orice mutație — dar atât:
    *că* s-a cerut ceva, nu *ce* s-a dezlegat. Aici se scrie fapta: care notă, de pe care factură,
    cu ce motiv. Se folosește ACELAȘI tabel (`public.audit_log`), cu aceeași sub-interogare pe
    `tenant_id` ca middleware-ul — R79: un rând de audit scris după o ștergere ar trimite la o firmă
    care nu mai există."""
    from core import afirmatii as _af
    # Urma e o AFIRMAȚIE TIPATĂ, nu proză într-un dicționar (P3, decizia din 21.08): `fel='fapt'`,
    # fiindcă exact asta e — un fapt petrecut, cu domeniul lui (nota și factura) și cu temeiul care
    # spune de ce e completă. Prima formă scria `{"motiv": ...}` și a fost prinsă de
    # `test_afirmatii_tipate`: o cheie de revendicare fără `fel` e chiar clasa vânată acolo.
    fapt = _af.afirmatie(
        "fapt", "DEZLEGARE_NOTA_FACTURA", motiv[:500],
        unde="nota #%s, factura #%s" % (nota_id, factura_id),
        temei_completitudine="urma se scrie în ACEEAȘI tranzacție cu dezlegarea, deci nu poate "
                             "exista dezlegare fără ea",
        nota_id=nota_id, factura_id=factura_id)
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO public.audit_log (user_id, tenant_id, actiune, detalii) "
            "VALUES (%s, (SELECT id FROM public.tenants WHERE id = %s), %s, %s)",
            (uid, tenant_id, "DEZLEGARE nota-factura", _json_audit.dumps(fapt)))


@app.post("/tenants/{tenant_id}/jurnal/{nota_id}/valideaza")
# [R55, 26.08.2026] Validarea e pasul care transforma o CIORNA in EVIDENTA — deci intra sub
# criteriul „ce schimba ce datoreaza firma" (R42, extins). Crearea, editarea si stergerea raman
# pe `cere_cabinet`: citite la sursa, `jurnal_api.editeaza` si `.sterge` refuza orice nota care
# nu e `ciorna`, deci nu ating evidenta. E munca zilnica a asistentului.
def jurnal_valideaza(tenant_id: int, nota_id: int, ctx=Depends(cere_rol("admin_firma"))):
    from core import jurnal_api as _j
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        _cere_perioada_deschisa(conn, schema, nota_id)
        return _jurnal_rez(_j.valideaza(conn, schema, nota_id))


# [F143 Faza 1] centre de cost — nomenclator per firma (dimensiune pe linia de nota)
@app.get("/tenants/{tenant_id}/centre-cost")
def centre_cost_lista(tenant_id: int, doar_active: bool = False, ctx=Depends(cere_cabinet)):
    from core import centre_cost_api as _cc
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        return {"centre": _cc.lista(conn, schema, doar_active=doar_active)}

@app.post("/tenants/{tenant_id}/centre-cost")
def centre_cost_adauga(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    from core import centre_cost_api as _cc
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        r = _cc.adauga(conn, schema, corp.get("nume"))
        if r.get("eroare"):
            raise HTTPException(400, r["eroare"])
        return r

@app.put("/tenants/{tenant_id}/centre-cost/{centru_id}")
def centre_cost_activ(tenant_id: int, centru_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    from core import centre_cost_api as _cc
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        r = _cc.seteaza_activ(conn, schema, centru_id, bool(corp.get("activ", True)))
        if r is None:
            raise HTTPException(404, "centru inexistent")
        return r

@app.get("/tenants/{tenant_id}/centre-cost/raport")
def centre_cost_raport(tenant_id: int, de: str, pana: str, ctx=Depends(cere_cabinet)):
    """Realizat pe centru de cost, perioada [de, pana] (note validate, clasele 6/7)."""
    from core import centre_cost_api as _cc
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant_citire(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        return _cc.raport_realizat(conn, schema, de, pana)

# [F143 Faza 2] bugete anuale pe centru + varianta buget vs realizat
@app.get("/tenants/{tenant_id}/centre-cost/varianta")
def centre_cost_varianta(tenant_id: int, an: int, ctx=Depends(cere_cabinet)):
    """Buget vs realizat pe an, per centru (note validate, clasele 6/7)."""
    from core import centre_cost_api as _cc
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        return _cc.raport_varianta(conn, schema, an)

@app.put("/tenants/{tenant_id}/centre-cost/{centru_id}/buget")
def centre_cost_buget(tenant_id: int, centru_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """Seteaza bugetul anual (cheltuieli + venituri) al unui centru pe un an."""
    from core import centre_cost_api as _cc
    an = corp.get("an")
    if not isinstance(an, int) or an < 2020 or an > 2100:
        raise HTTPException(400, "an invalid")
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        r = _cc.seteaza_buget(conn, schema, centru_id, an,
                              corp.get("buget_cheltuieli"), corp.get("buget_venituri"))
        if r is None:
            raise HTTPException(404, "centru inexistent")
        if r.get("eroare"):
            raise HTTPException(400, r["eroare"])
        return r


@app.post("/tenants/{tenant_id}/banca/reconciliere/{linie_id}/ignora")
def banca_rec_ignora(tenant_id: int, linie_id: int, ctx=Depends(cere_cabinet)):
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        with conn.cursor() as cur:
            cur.execute(f"UPDATE {schema}.extras_linii SET status='ignorat' WHERE id=%s AND status != 'contat' RETURNING id", (linie_id,))
            r = cur.fetchone()
        conn.commit()
    if not r:
        raise HTTPException(400, "linie inexistentă sau deja contată")
    return {"ok": True}


# --- registru incasari/plati (RIP) ---
def _rip_ctx(conn, ctx, tenant_id):
    schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
    if not schema:
        raise HTTPException(404, "tenant inexistent sau fără acces")
    return schema

@app.get("/tenants/{tenant_id}/rip/registru")
def rip_lista(tenant_id: int, an: int, luna: int = None, status: str = None, ctx=Depends(cere_cabinet)):
    from core import rip_api as _r
    with db.get_conn() as conn:
        return _r.lista(conn, _rip_ctx(conn, ctx, tenant_id), an, luna, status)

@app.post("/tenants/{tenant_id}/rip/operatiuni")
def rip_adauga(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    from core import rip_api as _r
    with db.get_conn() as conn:
        rez = _r.adauga(conn, _rip_ctx(conn, ctx, tenant_id), corp, ctx["uid"])
    if rez.get("eroare"):
        raise HTTPException(400, rez["eroare"])
    return rez

@app.put("/tenants/{tenant_id}/rip/operatiuni/{op_id}/valideaza")
def rip_valideaza(tenant_id: int, op_id: int, ctx=Depends(cere_cabinet)):
    from core import rip_api as _r
    with db.get_conn() as conn:
        rez = _r.valideaza(conn, _rip_ctx(conn, ctx, tenant_id), op_id, ctx["uid"])
    if rez.get("eroare"):
        raise HTTPException(400, rez["eroare"])
    return rez

@app.delete("/tenants/{tenant_id}/rip/operatiuni/{op_id}")
def rip_sterge(tenant_id: int, op_id: int, ctx=Depends(cere_cabinet)):
    from core import rip_api as _r
    with db.get_conn() as conn:
        rez = _r.sterge(conn, _rip_ctx(conn, ctx, tenant_id), op_id)
    if rez.get("eroare"):
        raise HTTPException(400, rez["eroare"])
    return rez

@app.post("/tenants/{tenant_id}/rip/import-banca")
def rip_import_banca(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    from core import rip_api as _r
    with db.get_conn() as conn:
        return _r.import_banca(conn, _rip_ctx(conn, ctx, tenant_id), an, luna, ctx["uid"])

@app.post("/tenants/{tenant_id}/rip/import-casa")
def rip_import_casa(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    from core import rip_api as _r
    with db.get_conn() as conn:
        return _r.import_casa(conn, _rip_ctx(conn, ctx, tenant_id), an, luna, ctx["uid"])

@app.get("/tenants/{tenant_id}/rip/inventar/{an}")
def rip_inventar(tenant_id: int, an: int, ctx=Depends(cere_cabinet)):
    from core import rip_api as _r
    with db.get_conn() as conn:
        return _r.registru_inventar(conn, _rip_ctx(conn, ctx, tenant_id), an)

@app.get("/tenants/{tenant_id}/rip/d212/{an}")
def rip_d212(tenant_id: int, an: int, optiune_cas: bool = False, optiune_cass: bool = False, ctx=Depends(cere_cabinet)):
    from core import rip_api as _r
    with db.get_conn() as conn:
        rez = _r.fisa_d212(conn, _rip_ctx(conn, ctx, tenant_id), an, optiune_cas, optiune_cass)
    if isinstance(rez, dict) and rez.get("eroare"):
        raise HTTPException(400, rez["eroare"])
    return rez

# --- registru de casa ---
@app.get("/tenants/{tenant_id}/concedii/coduri")  # [cm_coduri_v1] denumirea din nomenclator + procentul din registru
def concedii_coduri(tenant_id: int, la_data: Optional[str] = None, ctx=Depends(cere_cabinet)):
    """Codurile de indemnizatie pentru ecran, cu procentul VALABIL LA DATA certificatului.

    Inainte de 22.08.2026 lista traia scrisa de mana in `flux_concediu.js` (18 coduri, cu procentele
    lipite in eticheta): ecranul NU oferea 11/91/92 - coduri legale pe care aplicatia le accepta -
    deci bloca un contabil sa introduca un cod valid. Vezi `core/coduri_cm_api.py`."""
    from core import coduri_cm_api as _cc
    import datetime as _d
    # [izolare] ruta e sub {tenant_id}, deci ACCESUL se verifica, chiar daca raspunsul nu depinde de
    # firma: altfel un 200 pe tenantul altui cabinet spune ca tenantul EXISTA. Prins de
    # test_izolare_structurala, nu de mine.
    with db.get_conn() as conn:
        if not auth_api.schema_tenant(conn, ctx["uid"], tenant_id):
            raise HTTPException(COD_FARA_ACCES_TENANT, FARA_ACCES_TENANT)
    d = None
    if la_data:
        try:
            d = _d.date.fromisoformat(la_data)
        except ValueError:
            raise HTTPException(422, "Data trebuie să fie în formatul AAAA-LL-ZZ.")
    return {"coduri": _cc.optiuni(d)}


@app.get("/tenants/{tenant_id}/casa/registru")
def casa_registru(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    from core import casa_api as _c
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant_citire(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        return _c.registru(conn, schema, an, luna)

@app.post("/tenants/{tenant_id}/casa/operatiuni")
def casa_adauga(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    from core import casa_api as _c
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
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
            raise HTTPException(404, "tenant inexistent sau fără acces")
        rez = _c.sterge(conn, schema, op_id)
    if rez is None:
        raise HTTPException(404, "operațiune inexistentă")
    if rez.get("eroare"):
        raise HTTPException(400, rez["eroare"])
    return rez


# --- stocuri global-valorica ---
@app.get("/tenants/{tenant_id}/stocuri/nir")
def stocuri_lista(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    _cere_perioada(an, luna)   # [lotul 5] `luna=13` dadea `500`, `an=1900` dadea `200 {"nir": []}`
    from core import stocuri_api as _s
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        return {"nir": _s.lista_nir(conn, schema, an, luna)}

@app.post("/tenants/{tenant_id}/stocuri/nir")
def stocuri_adauga(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    from core import stocuri_api as _s
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        rez = _s.adauga_nir(conn, schema, corp)
    if rez.get("eroare"):
        _ec = rez.get("erori_campuri")  # [cap.24] contract {mesaj, erori_campuri} ca celelalte ecrane
        raise HTTPException(422, detail={"mesaj": rez["eroare"], "erori_campuri": _ec} if _ec else rez["eroare"])
    return rez

@app.post("/tenants/{tenant_id}/stocuri/descarcare")
def stocuri_descarcare(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    from core import stocuri_api as _s
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
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
            raise HTTPException(404, "tenant inexistent sau fără acces")
        return {"articole": _s.articole(conn, schema)}

@app.get("/tenants/{tenant_id}/stocuri/articole/{articol_id}/fisa")
def cv_fisa(tenant_id: int, articol_id: int, ctx=Depends(cere_cabinet)):
    from core import stocuri_cv_api as _s
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant_citire(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
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
            raise HTTPException(404, "tenant inexistent sau fără acces")
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
            raise HTTPException(404, "tenant inexistent sau fără acces")
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
            raise HTTPException(404, "tenant inexistent sau fără acces")
        return _s.inventar(conn, schema, corp)


@app.get("/tenants/{tenant_id}/stocuri/locatii")
def cv_locatii(tenant_id: int, articol_id: int = None, ctx=Depends(cere_cabinet)):
    from core import stocuri_cv_api as _s
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        return {"locatii": _s.stoc_pe_locatii(conn, schema, articol_id)}


@app.post("/tenants/{tenant_id}/stocuri/transfer")
def cv_transfer(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    from core import stocuri_cv_api as _s
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        rez = _s.transfer(conn, schema, corp)
    if rez is None:
        raise HTTPException(404, "articol inexistent")
    if rez.get("eroare"):
        raise HTTPException(400, rez["eroare"])
    return rez


@app.post("/tenants/{tenant_id}/stocuri/reclasificare")
def cv_reclasificare(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    from core import stocuri_cv_api as _s
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        rez = _s.reclasificare(conn, schema, corp)
    if rez is None:
        raise HTTPException(404, "articol inexistent")
    if rez.get("eroare"):
        raise HTTPException(400, rez["eroare"])
    return rez


@app.get("/tenants/{tenant_id}/stocuri/analitica")
def cv_analitica(tenant_id: int, zile_inert: int = 90, ctx=Depends(cere_cabinet)):
    from core import stocuri_cv_api as _s
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        return _s.analitica(conn, schema, zile_inert)


@app.post("/tenants/{tenant_id}/stocuri/articole/{articol_id}/nivel-minim")
def cv_nivel_minim(tenant_id: int, articol_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    from core import stocuri_cv_api as _s
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        rez = _s.set_nivel_minim(conn, schema, articol_id, corp.get("nivel_minim"))
    if rez is None:
        raise HTTPException(404, "articol inexistent")
    if rez.get("eroare"):
        raise HTTPException(400, rez["eroare"])
    return rez


@app.get("/tenants/{tenant_id}/stocuri/barcode/{cod}")
def cv_barcode_gaseste(tenant_id: int, cod: str, ctx=Depends(cere_cabinet)):
    from core import stocuri_cv_api as _s
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        a = _s.gaseste_barcode(conn, schema, cod)
    if a is None:
        raise HTTPException(404, "niciun articol cu acest cod de bare")
    return a


@app.post("/tenants/{tenant_id}/stocuri/articole/{articol_id}/barcode")
def cv_barcode_set(tenant_id: int, articol_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    from core import stocuri_cv_api as _s
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        rez = _s.set_barcode(conn, schema, articol_id, corp.get("barcode"))
    if rez is None:
        raise HTTPException(404, "articol inexistent")
    if rez.get("eroare"):
        raise HTTPException(400, rez["eroare"])
    return rez


# --- D112 ---

@app.get("/tenants/{tenant_id}/categorie-marime")
def cabinet_categorie_marime(tenant_id: int, an: int, ctx=Depends(cere_cabinet)):
    """[R3, lista 3, 30.08.2026] CATEGORIA DE MARIME — precondiția situațiilor financiare.

    Cerința lui Costin, 26.08.2026: *„situațiile financiare cerute depind de categoria de mărime.
    Dacă aceasta nu există ca dimensiune, ruta nu poate ști ce datorează firma — se declară, nu se
    presupune."* Până azi nu exista: nici câmp, nici derivare, nici măcar numele.

    NU ALEGE FORMULARUL. Întoarce o **afirmație** — categoria, indicatorii din care iese, pragurile
    cu temeiul lor, și motivul. Ce face contabilul cu ea rămâne decizia lui: `s1005-valideaza` și
    `s1003-valideaza` nu se ating. *Aplicația spune ce știe; nu decide în locul omului pe baza unei
    derivări care poate să nu aibă datele.*
    """
    from core import categorie_marime as _cm
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
    with db.get_conn(schema) as conn:
        return _cm.categorie(conn, schema, an)


@app.get("/tenants/{tenant_id}/s1005-xml")
def s1005_xml(tenant_id: int, an: int, ctx=Depends(cere_cabinet)):
    from core import bilant_api as _ba
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        try:
            xml, av = _ba.genereaza(conn, schema, an)
        except ValueError as e:
            # [bilant_422_v1] mesajul de refuz al lui bilant_api (ex. lipsa nr. reg. com.) e scris
            # pentru contabil; fara asta ajungea la el ca 500 gol (oprire generica, interzisa de DS).
            raise HTTPException(422, str(e))
    return {"xml": xml, "avertismente": av}

@app.post("/tenants/{tenant_id}/s1005-valideaza")
# [R45] Artefactul care încheie exercițiul financiar se PĂSTREAZĂ: conținutul, momentul,
# autorul, amprenta, numărul exemplarului — plus verdictul cu amprenta fișierului validat.
# Se scrie aici, nu pe `-xml`: aia e o citire (GET), asta e actul.
def s1005_valideaza(tenant_id: int, an: int, ctx=Depends(cere_cabinet)):
    import base64, subprocess, tempfile, os
    from core import bilant_api as _ba
    from core import artefacte as _art
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        try:
            xml, av = _ba.genereaza(conn, schema, an)
        except ValueError as e:
            # [bilant_422_v1] mesajul de refuz al lui bilant_api (ex. lipsa nr. reg. com.) e scris
            # pentru contabil; fara asta ajungea la el ca 500 gol (oprire generica, interzisa de DS).
            raise HTTPException(422, str(e))
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
    # [R45] Artefactul se pastreaza AICI, dupa ce verdictul exista: cele cinci campuri plus
    # verdictul cu amprenta fisierului validat. `verdict_amprenta` e amprenta XML-ului care a
    # intrat in validator — daca se regenereaza, verdictul devine statut (aceeasi regula ca R41).
    try:
        from core import duk as _duk
        with db.get_conn() as _c:
            _art.pastreaza(_c, schema, "s1005", str(an), xml,
                           produs_de_id=int(ctx["uid"]),
                           produs_de=ctx.get("nume") or str(ctx["uid"]),
                           verdict=("valid" if ok else "erori"),
                           verdict_versiune=_duk.versiune_validator("s1005"),
                           verdict_amprenta=_art.amprenta(xml))
    except Exception as _e:
        import logging
        logging.getLogger("iconta").warning("[R45] artefact s1005 nepastrat: %s", _e)
    return {"ok": ok, "erori": erori, "avertismente": av,
            "xml_b64": base64.b64encode(xml.encode()).decode()}


# --- S1003 (bilant mici) ---
@app.get("/tenants/{tenant_id}/s1003-xml")
def s1003_xml(tenant_id: int, an: int, ctx=Depends(cere_cabinet)):
    from core import bilant_api as _ba
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        try:
            xml, av = _ba.genereaza_s1003(conn, schema, an)
        except ValueError as e:
            # [bilant_422_v1] mesajul de refuz al lui bilant_api (ex. lipsa nr. reg. com.) e scris
            # pentru contabil; fara asta ajungea la el ca 500 gol (oprire generica, interzisa de DS).
            raise HTTPException(422, str(e))
    return {"xml": xml, "avertismente": av}

@app.post("/tenants/{tenant_id}/s1003-valideaza")
# [R45] Artefactul care încheie exercițiul financiar se PĂSTREAZĂ: conținutul, momentul,
# autorul, amprenta, numărul exemplarului — plus verdictul cu amprenta fișierului validat.
# Se scrie aici, nu pe `-xml`: aia e o citire (GET), asta e actul.
def s1003_valideaza(tenant_id: int, an: int, ctx=Depends(cere_cabinet)):
    import base64, subprocess, tempfile, os
    from core import bilant_api as _ba
    from core import artefacte as _art
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        try:
            xml, av = _ba.genereaza_s1003(conn, schema, an)
        except ValueError as e:
            # [bilant_422_v1] mesajul de refuz al lui bilant_api (ex. lipsa nr. reg. com.) e scris
            # pentru contabil; fara asta ajungea la el ca 500 gol (oprire generica, interzisa de DS).
            raise HTTPException(422, str(e))
    with tempfile.TemporaryDirectory() as td:
        cale = os.path.join(td, f"s1003_{tenant_id}_{an}.xml")
        open(cale, "w", encoding="utf-8").write(xml)
        r = subprocess.run(["java", "-jar", "DUKIntegrator.jar", "-v", "S1003", cale],
                           cwd="/home/costin/duk/dist", capture_output=True, text=True, timeout=120)
        erori = ""
        if os.path.exists(cale + ".err.txt"):
            erori = open(cale + ".err.txt", encoding="utf-8").read()
    ok = "fara erori" in (r.stdout + r.stderr)
    # [R45] Artefactul se pastreaza AICI, dupa ce verdictul exista: cele cinci campuri plus
    # verdictul cu amprenta fisierului validat. `verdict_amprenta` e amprenta XML-ului care a
    # intrat in validator — daca se regenereaza, verdictul devine statut (aceeasi regula ca R41).
    try:
        from core import duk as _duk
        with db.get_conn() as _c:
            _art.pastreaza(_c, schema, "s1003", str(an), xml,
                           produs_de_id=int(ctx["uid"]),
                           produs_de=ctx.get("nume") or str(ctx["uid"]),
                           verdict=("valid" if ok else "erori"),
                           verdict_versiune=_duk.versiune_validator("s1003"),
                           verdict_amprenta=_art.amprenta(xml))
    except Exception as _e:
        import logging
        logging.getLogger("iconta").warning("[R45] artefact s1003 nepastrat: %s", _e)
    return {"ok": ok, "erori": erori, "avertismente": av,
            "xml_b64": base64.b64encode(xml.encode()).decode()}


# --- Retetar HoReCa ---
@app.get("/tenants/{tenant_id}/retete")
def retete_lista(tenant_id: int, ctx=Depends(cere_cabinet)):
    from core import retete_api as _r
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        return _r.lista(conn, schema)

@app.post("/tenants/{tenant_id}/retete")
def retete_salveaza(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    from core import retete_api as _r
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        r = _r.salveaza(conn, schema, corp)
    if r.get("eroare"):
        _ec = r.get("erori_campuri")  # [cap.24] contract {mesaj, erori_campuri} ca facturi-recurente/emitere
        raise HTTPException(422, detail={"mesaj": r["eroare"], "erori_campuri": _ec} if _ec else r["eroare"])
    return r

@app.delete("/tenants/{tenant_id}/retete/{reteta_id}")
def retete_sterge(tenant_id: int, reteta_id: int, ctx=Depends(cere_cabinet)):
    from core import retete_api as _r
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        return _r.sterge(conn, schema, reteta_id)

@app.post("/tenants/{tenant_id}/retete/descarca")
def retete_descarca(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    from core import retete_api as _r
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
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
            raise HTTPException(404, "tenant inexistent sau fără acces")
        with conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
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
            raise HTTPException(404, "tenant inexistent sau fără acces")
        with conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
            cur.execute(f"SELECT cui FROM {schema}.firma_profil WHERE id = 1")
            r = cur.fetchone() or {}
    cui = re.sub(r"\D", "", r.get("cui") or "")
    if not cui:
        raise HTTPException(422, CUI_FIRMA_LIPSA)
    lipsa = _e.campuri_required_lipsa(corp)
    if lipsa:
        raise HTTPException(422, {"cod": "CAMPURI_LIPSA",
            "mesaj": "Câmpuri obligatorii lipsă (schema eTransport): " + "; ".join(x["eticheta"] for x in lipsa),
            "campuri": lipsa})
    try:
        xml = _e.xml_notificare(cui, corp)
    except KeyError as e:
        raise HTTPException(422, f"câmp lipsă: {e}")
    return {"xml": xml,
            "nota": "XML v2 pt. incarcare manuala in SPV (e-Transport). UIT-ul vine de la ANAF dupa upload."}


@app.post("/tenants/{tenant_id}/etransport/trimite")
# [R42] „iese către o autoritate" — declarația UIT ajunge la ANAF.
def etransport_trimite(tenant_id: int, corp: dict = Body(...),
                       ctx=Depends(cere_rol("admin_firma"))):
    """Trimite notificarea UIT in SPV (F121): genereaza XML + trimite() cu PORTI in ordine (garda de timp
    -> idempotency -> validare pe TEST -> upload). Poll-ul stare NU e sincron. Live pending drept e-Transport."""
    import re as _re2
    from core import etransport as _egen, etransport_send as _es
    principal = _spv_rute.spv_principal(ctx)
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        with conn.cursor() as cur:
            cur.execute(f"SELECT cui FROM {schema}.firma_profil WHERE id=1")
            r0 = cur.fetchone()
    cui = _re2.sub(r"\D", "", (r0[0] if r0 else "") or "")
    if not cui:
        raise HTTPException(422, CUI_FIRMA_LIPSA)
    lipsa = _egen.campuri_required_lipsa(corp)
    if lipsa:
        raise HTTPException(422, {"cod": "CAMPURI_LIPSA",
            "mesaj": "Câmpuri obligatorii lipsă (schema eTransport): " + "; ".join(x["eticheta"] for x in lipsa),
            "campuri": lipsa})
    try:
        xml = _egen.xml_notificare(cui, corp)
    except KeyError as e:
        raise HTTPException(422, "câmp lipsă: %s" % e)
    data_transport = (corp.get("transport") or {}).get("data")
    if not data_transport:
        raise HTTPException(422, "data transport lipsă")
    intracom = str(corp.get("cod_tip_operatiune")) == "10"   # AIC = achizitie intracomunitara -> UIT 15 zile
    mediu = os.environ.get("ETRANSPORT_MEDIU", os.environ.get("EFACTURA_MEDIU", "prod"))
    return _es.trimite(schema, principal, cui, xml, data_transport, intracom=intracom,
                       mediu=mediu, ref=corp.get("ref"))


@app.get("/tenants/{tenant_id}/etransport/trimiteri")
def etransport_trimiteri_lista(tenant_id: int, ctx=Depends(cere_context)):
    """UIT-uri trimise + semafor de TIMP (valabilitate UIT) SEPARAT de semaforul de trimitere. Fara apel ANAF."""
    from datetime import date as _date
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        with conn.cursor() as cur:
            cur.execute(f"""SELECT id, stare, uit, data_transport, uit_valabil_pana, intracom, error_message
                              FROM {schema}.etransport_trimiteri WHERE mediu='prod'
                              ORDER BY id DESC LIMIT 50""")
            rows = cur.fetchall()
    azi = _date.today()
    out = []
    for (tid, stare, uit, dt, valp, intra, err) in rows:
        zile = (valp - azi).days if valp else None
        timp = "gri" if zile is None else ("rosu" if zile < 0 else ("galben" if zile <= 1 else "verde"))
        trimit = "verde" if stare in ("ok", "incarcat") else ("rosu" if stare in ("nok", "eroare_upload") else "gri")
        out.append({"id": tid, "stare": stare, "uit": uit,
                    "data_transport": str(dt) if dt else None,
                    "uit_valabil_pana": str(valp) if valp else None,
                    "zile_ramase": zile, "intracom": intra,
                    "semafor_timp": timp, "semafor_trimitere": trimit, "error_message": err})
    return {"trimiteri": out}


@app.post("/tenants/{tenant_id}/banca/reconciliere/{linie_id}/reactiveaza")
def banca_rec_reactiveaza(tenant_id: int, linie_id: int, ctx=Depends(cere_cabinet)):
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        with conn.cursor() as cur:
            cur.execute(f"""UPDATE {schema}.extras_linii SET status='nou'
                            WHERE id=%s AND status='ignorat' RETURNING id""", (linie_id,))
            r = cur.fetchone()
        conn.commit()
    if not r:
        raise HTTPException(422, "linia nu e ignorata")
    return {"ok": True}


@app.post("/tenants/{tenant_id}/facturi/{factura_id}/recunoaste")  # [api_intern_v1] fara buton in UI, pastrat deliberat: perechea lui `POST /import-efactura`, care n-are nici el ecran (R70). Un act de recunoastere fara calea care aduce documentul n-ar avea ce recunoaste.
# [R91, 29.08.2026 — decizia lui Costin, varianta (iii)] Rolul e `admin_firma`, ca la validarea unei
# facturi primite: actul recunoaste un fapt economic si ii scrie evidenta. Simetria nu e estetica —
# e chiar argumentul deciziei: la primita, faptul nu e sosirea documentului, ci recunoasterea
# cheltuielii; la emisa venita din import, faptul nu e sosirea, ci recunoasterea emiterii facute in
# alta parte.
def factura_recunoaste(tenant_id: int, factura_id: int, ctx=Depends(cere_rol("admin_firma"))):
    """RECUNOAȘTEREA unei facturi EMISE venite prin import — actul care îi scrie nota.

    STRUCTURAL SIMETRIC cu `POST /facturi-primite/{id}/valideaza`, punct cu punct: patru-ochi (rolul
    e același) · o singură tranzacție · nota se scrie **în același act** cu recunoașterea · nota intră
    **ciornă**, deci automat nu înseamnă validat (R47) · idempotent, a doua chemare e **no-op**, nu
    eroare.

    CE CONFIRMĂ OMUL, și de ce actul are sens: documentul a fost emis în **altă parte** — aplicația
    nu l-a produs, l-a **primit înapoi**. Cine apasă spune „da, factura asta e a firmei și e completă
    așa cum a venit". Abia atunci devine fapt al firmei, cu evidență.

    CE NU FACE, declarat: nu editează factura. Dacă documentul importat e greșit, corecția fiscală e
    prin al doilea document (storno, P4), nu prin retușarea celui adus.
    """
    from core import contare_facturi as _cf
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        with conn.cursor() as cur:
            cur.execute(f"SELECT status, directie, (xml IS NOT NULL) FROM {schema}.facturi "
                        f"WHERE id=%s FOR UPDATE", (factura_id,))
            r = cur.fetchone()
        if not r:
            raise HTTPException(404, "factură inexistentă")
        stare, directie, din_import = r
        if stare != "de_recunoscut":
            # Idempotență ca RĂSPUNS — dar NUMAI pentru o factură care chiar a venit prin import.
            # Discriminatorul e `xml`: `_factura_din_parsat` îl scrie, `creeaza_factura` nu. Fără el,
            # actul răspundea „deja recunoscută" și despre o factură emisă normal prin aplicație,
            # care n-a fost niciodată ciornă de recunoaștere — o afirmație mică și falsă. Prins de
            # gardă la prima rulare.
            with _cf.cursor_dict(conn) as cur:
                deja = _cf.contare_existenta(cur, schema, factura_id)
            if deja and din_import:
                return {"stare": "deja_recunoscuta", "factura_id": factura_id,
                        "inregistrare_id": deja["id"]}
            raise HTTPException(422, "factura nu e o ciornă de recunoaștere (stare `%s`): actul e "
                                     "pentru facturile EMISE aduse prin import" % stare)
        try:
            with _cf.cursor_dict(conn) as cur:
                rez = _cf.contabilizeaza(cur, schema, factura_id, automat=True)
                cur.execute(f"UPDATE {schema}.facturi SET status='emisa' WHERE id=%s", (factura_id,))
        except _cf.RefuzContare as e:
            conn.rollback()
            if e.cod == "LUNA_INCHISA":
                raise HTTPException(423, PERIOADA_INCHISA)
            raise HTTPException(422, e.mesaj)
        conn.commit()
    return {"stare": "recunoscuta", "factura_id": factura_id, "contare": rez}


@app.post("/tenants/{tenant_id}/facturi/{factura_id}/contabilizeaza")
def factura_contabilizeaza(tenant_id: int, factura_id: int, ctx=Depends(cere_cabinet)):
    """RUTA MANUALĂ de contare — **a doua cale, declarată** (R87, decizia lui Costin 29.08.2026,
    varianta (ii)+(iii) din AAA4).

    De ce există, deși contarea e automată de azi: e singura cale de a contabiliza o factură pe care
    automatul a **refuzat-o** — lună închisă la emitere, cotă lipsă pe linii, sau clasa
    furnizor-la-încasare. Ștergând-o, refuzul automatului ar deveni un blocaj fără ieșire.

    [EEE3 / FFF3] **IDEMPOTENTĂ**: a doua chemare pe o factură deja contată e **no-op** — răspuns
    `200` cu `stare='deja_contata'`, nu `422`. Refuzul de dinainte era corect, prezentarea lui nu:
    un comportament corect care arată ca o eroare învață pe cineva să se ferească de el.

    Diferența față de calea automată e una singură, și e declarată: aici `automat=False`, deci clasa
    ambiguă de TVA la încasare **trece** (omul are contextul pe care automatul nu-l are), iar plasa
    anti-dublare **avertizează** în loc să oprească."""
    from core import contare_facturi as _cf
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        try:
            with _cf.cursor_dict(conn) as cur:
                rez = _cf.contabilizeaza(cur, schema, factura_id, automat=False)
        except _cf.RefuzContare as e:
            conn.rollback()
            if e.cod == "INEXISTENTA":
                raise HTTPException(404, e.mesaj)
            # Codul de stare se pastreaza pe fiecare clasa de refuz: luna inchisa raspundea `423`
            # inainte de rescriere si raspunde `423` si acum. O rescriere care schimba tacit codul
            # de raspuns ar rupe apelanti fara sa spuna.
            if e.cod == "LUNA_INCHISA":
                raise HTTPException(423, PERIOADA_INCHISA)
            raise HTTPException(422, e.mesaj)
        conn.commit()
    return rez



@app.post("/tenants/{tenant_id}/vanzare-marja")
def vanzare_marja(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, pret_vanzare, pret_cumparare, cota?, descriere?}. Nota ciorna
    regim marja (art. 312): 4111=707 cost + 4111=707 marja neta + 4111=4427 TVA marja."""
    from decimal import Decimal
    from core import tva_marja as _m
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        _cere_luna_deschisa(conn, schema, corp.get("data"))
        try:
            r = _m.vanzare_marja(corp["pret_vanzare"], corp["pret_cumparare"], _common.cota_ceruta(corp))
        except (ValueError, KeyError) as e:
            raise HTTPException(422, _mesaj_intrare(e))
        with conn.cursor() as cur:
            cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status)
                            VALUES (%s,%s,'facturi','ciorna') RETURNING id""",
                        (corp["data"], (corp.get("descriere") or "Vanzare regim marja (art. 312)")[:200]))
            iid = cur.fetchone()[0]
            linii = [("4111", "707", Decimal(str(corp["pret_cumparare"])))]
            if r["marja_neta"] > 0:
                linii.append(("4111", "707", r["marja_neta"]))
            if r["tva"] > 0:
                linii.append(("4111", "4427", r["tva"]))
            for d, c, s in linii:
                if s > 0:
                    cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                                    (inregistrare_id, cont_debit, cont_credit, suma)
                                    VALUES (%s,%s,%s,%s)""", (iid, d, c, s))
        conn.commit()
    return dict(_af.afirmatie(
        "fapt", "vânzare în regim de marjă", r["nota"] or "marjă calculată conform art. 312",
        unde=_Unde("inregistrare", iid),
        temei_completitudine="prețul de vânzare și cel de cumpărare din nota creată "
                             "(Cod fiscal art. 312, regimul marjei)"),
        inregistrare_id=iid, marja_bruta=str(r["marja_bruta"]),
        tva=str(r["tva"]), marja_neta=str(r["marja_neta"]), avertisment=r["nota"])


@app.post("/tenants/{tenant_id}/vanzare-marja-turism")
def vanzare_marja_turism(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, calitate_client PF|PJ, locuri [RO|UE|NONUE], optiune_normal?,
    intermediar?, cota?, descriere?} + per regim:
    special: incasat, cost_ue, cost_non_ue? | normal: componente [{descriere,baza,cota}]
    | intermediar: comision, tva_inclus?. Nota intra mereu ciorna (art. 311 CF)."""
    from decimal import Decimal
    from core import tva_marja_turism as _m
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        _cere_luna_deschisa(conn, schema, corp.get("data"))
        try:
            regim = _m.determina_regim(corp["calitate_client"], corp.get("locuri", ["RO"]),
                                       corp.get("optiune_normal", False),
                                       corp.get("intermediar", False))
            if regim == "special":
                r = _m.marja_turism_special(corp["incasat"], corp["cost_ue"],
                                            corp.get("cost_non_ue", 0), _common.cota_ceruta(corp))
                linii = [("4111", "704", Decimal(str(corp["cost_ue"])) + Decimal(str(corp.get("cost_non_ue", 0))))]
                if r["marja_neta"] > 0:
                    linii.append(("4111", "704", r["marja_neta"]))
                if r["tva"] > 0:
                    linii.append(("4111", "4427", r["tva"]))
                rasp = {"regim": regim, "marja_bruta": str(r["marja_bruta"]),
                        "marja_scutita": str(r["marja_scutita"]), "tva": str(r["tva"]),
                        "marja_neta": str(r["marja_neta"]), "nota": r["nota"]}
            elif regim == "normal":
                r = _m.marja_turism_normal(corp["componente"])
                linii = [("4111", "704", comp["baza"]) for comp in r["componente"]]
                if r["total_tva"] > 0:
                    linii.append(("4111", "4427", r["total_tva"]))
                rasp = {"regim": regim, "total_baza": str(r["total_baza"]),
                        "total_tva": str(r["total_tva"]), "total_factura": str(r["total_factura"])}
            else:
                r = _m.comision_intermediar(corp["comision"], _common.cota_ceruta(corp), corp.get("tva_inclus", False))
                linii = [("4111", "704", r["baza"])]
                if r["tva"] > 0:
                    linii.append(("4111", "4427", r["tva"]))
                rasp = {"regim": regim, "baza": str(r["baza"]), "tva": str(r["tva"]),
                        "total": str(r["total"])}
        except (ValueError, KeyError) as e:
            raise HTTPException(422, _mesaj_intrare(e))
        with conn.cursor() as cur:
            cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status)
                            VALUES (%s,%s,'facturi','ciorna') RETURNING id""",
                        (corp["data"], (corp.get("descriere") or f"Vanzare marja turism ({regim}, art. 311)")[:200]))
            iid = cur.fetchone()[0]
            for d, c, s in linii:
                if s > 0:
                    cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                                    (inregistrare_id, cont_debit, cont_credit, suma)
                                    VALUES (%s,%s,%s,%s)""", (iid, d, c, s))
        conn.commit()
    rasp["inregistrare_id"] = iid
    return rasp


@app.post("/tenants/{tenant_id}/vanzare-aur-investitii")
def vanzare_aur_investitii(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, tip lingou|plancheta|moneda, puritate, an_emisie?, pret_unitar?,
    valoare_aur?, suma, optiune_taxare?, calitate_client PF|PJ, client_identificare,
    descriere?}. Scutit (art. 313 al. 3) sau taxare inversa (art. 331 al. 2 lit. h).
    Nota ciorna: 4111=707 fara TVA."""
    from decimal import Decimal
    from core import tva_aur as _m
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        _cere_luna_deschisa(conn, schema, corp.get("data"))
        try:
            ok, motiv = _m.este_aur_investitii(corp["tip"], corp["puritate"],
                                               corp.get("an_emisie"), corp.get("pret_unitar"),
                                               corp.get("valoare_aur"))
            if not ok:
                raise ValueError("nu este aur de investitii: " + motiv)
            regim = _m.livrare_aur(corp.get("optiune_taxare", False),
                                   corp["calitate_client"], corp["client_identificare"])
            suma = Decimal(str(corp["suma"]))
            if suma <= 0:
                raise ValueError("suma invalida")
        except (ValueError, KeyError) as e:
            raise HTTPException(422, _mesaj_intrare(e))
        mentiune = "taxare inversa (art. 331 al. 2 lit. h)" if regim == "taxare_inversa" \
                   else "scutit (art. 313 al. 3)"
        descr = (corp.get("descriere") or "Livrare aur investitii") + " - " + mentiune \
                + " - client: " + corp["client_identificare"]
        with conn.cursor() as cur:
            cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status)
                            VALUES (%s,%s,'facturi','ciorna') RETURNING id""",
                        (corp["data"], descr[:200]))
            iid = cur.fetchone()[0]
            cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                            (inregistrare_id, cont_debit, cont_credit, suma)
                            VALUES (%s,'4111','707',%s)""", (iid, suma))
        conn.commit()
    return {"inregistrare_id": iid, "regim": regim, "suma": str(suma)}


@app.post("/tenants/{tenant_id}/achizitie-agricultor")
def achizitie_agricultor(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, valoare (fara taxa), cont_cheltuiala, agricultor_in_registru,
    agricultor?, descriere?}. Nota ciorna: % cont_chelt + 4426(compensatie 8%) = 401."""
    from decimal import Decimal
    from core import tva_agricultori as _m
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        _cere_luna_deschisa(conn, schema, corp.get("data"))
        try:
            r = _m.achizitie_de_la_agricultor(corp["valoare"], corp["agricultor_in_registru"])
            # [R54] confruntarea cu planul firmei inlocuieste verificarea de PREZENTA:
            # `cere_cont` refuza si absenta, si contul care nu exista in plan, si spune CE
            # cont si UNDE se creeaza. Doua verificari suprapuse ar fi doua locuri.
            cont = _cv.cere_cont(conn, schema, corp.get("cont_cheltuiala"), "cont_cheltuiala")
        except (ValueError, KeyError) as e:
            raise HTTPException(422, _mesaj_intrare(e))
        descr = (corp.get("descriere") or "Achizitie agricultor regim special (art. 315^1)") \
                + ((" - " + corp["agricultor"]) if corp.get("agricultor") else "")
        with conn.cursor() as cur:
            cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status)
                            VALUES (%s,%s,'facturi','ciorna') RETURNING id""",
                        (corp["data"], descr[:200]))
            iid = cur.fetchone()[0]
            for d, c, s in [(cont, "401", r["pret"]), ("4426", "401", r["compensatie"])]:
                cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                                (inregistrare_id, cont_debit, cont_credit, suma)
                                VALUES (%s,%s,%s,%s)""", (iid, d, c, s))
        conn.commit()
    return {"inregistrare_id": iid, "pret": str(r["pret"]),
            "compensatie": str(r["compensatie"]), "total": str(r["total"])}


@app.post("/tenants/{tenant_id}/vanzare-agricultor")
def vanzare_agricultor(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, pret (fara taxa), descriere?}. FIRMA E AGRICULTORUL in regim special si
    VINDE: factura fara TVA, mentiune regim + compensatie 8%. Nota: 4111 = 704 pret + 704
    compensatie — compensatia e VENITUL firmei, nu TVA (art. 315^1 alin. 1 lit. h si alin. 2).

    [R16, corectat 26.08.2026] Textul de aici spunea „Client agricultor regim special", adica
    EXACT PE DOS — ca si cum firma ar vinde CATRE un agricultor. Codul spune altceva, si o spune
    de trei ori: corpul cere doar {data, pret}, FARA identificarea agricultorului si FARA
    `in_registru` (pe care sora ei, /achizitie-agricultor, le cere); descrierea generata e
    „Livrare produse agricole"; iar compensatia se contabilizeaza ca VENIT al firmei, ceea ce
    are sens doar daca firma e cea care o incaseaza. Proza a produs o intrebare reala cand
    Costin a scris verificarea pasului: nu se putea sti in ce sens merge operatiunea.

    CE NU S-A VERIFICAT, declarat: daca `4111 = 704` pentru compensatie e tratamentul contabil
    corect. S-a citit ce FACE codul si ce cita modulul; nu s-a confruntat cu actul."""
    from core import tva_agricultori as _m
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        _cere_luna_deschisa(conn, schema, corp.get("data"))
        try:
            r = _m.compensatie(corp["pret"])
        except (ValueError, KeyError) as e:
            raise HTTPException(422, _mesaj_intrare(e))
        descr = (corp.get("descriere") or "Livrare produse agricole") \
                + " - regim special agricultori (art. 315^1), compensatie 8%"
        with conn.cursor() as cur:
            cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status)
                            VALUES (%s,%s,'facturi','ciorna') RETURNING id""",
                        (corp["data"], descr[:200]))
            iid = cur.fetchone()[0]
            for s in (r["pret"], r["compensatie"]):
                cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                                (inregistrare_id, cont_debit, cont_credit, suma)
                                VALUES (%s,'4111','704',%s)""", (iid, s))
        conn.commit()
    return {"inregistrare_id": iid, "pret": str(r["pret"]),
            "compensatie": str(r["compensatie"]), "total": str(r["total"])}


@app.get("/tenants/{tenant_id}/fisa-cont")
def cabinet_fisa_cont(tenant_id: int, an: int, cont: Optional[str] = None,
                      luna: Optional[int] = None, ctx=Depends(cere_cabinet)):
    """[lista 3, 30.08.2026] CARTEA MARE (14-1-3), prin inlocuitorul ei legal.

    Norma: *„Registrul Cartea mare poate fi inlocuit cu Fisa de cont pentru operatiuni diverse"*
    (OMFP 2634/2015, Anexa 2, cod 14-1-3 si 14-1-3/a; fisa insasi e cod 14-6-22).

    Producatorul (`core/fisa_cont.py`) exista din iulie si producea pe date reale — 6 firme cu
    miscare, 43 de conturi in 2026 — dar n-avea NICI ruta, NICI ecran. Deci artefactul se calcula si
    nu ajungea la nimeni: lista 3, cauza „nu ajunge la om", nu „nu exista producator".

    Fara `cont`: intoarce doar conturile cu miscare — domeniul pe care fisa se poate cere. Asa
    ecranul nu ofera un cont pe care fisa ar iesi goala, ceea ce norma nu cere si controlul nu
    accepta.

    POARTA COMUNA, deliberat (`schema_tenant`, nu `schema_tenant_citire`): decizia (b) din 28.08 a
    numit EXPLICIT 13 rute de citire-istorica, iar a 14-a a intrat azi doar fiindca e a doua iesire
    a uneia dintre ele. Asta e o ruta NOUA, deci ar fi o largire a deciziei — se cere, nu se face.
    LIMITA DECLARATA: Cartea mare a unei firme DEZACTIVATE nu se poate citi pe ruta asta.
    """
    from core import fisa_cont as _fc
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
    with db.get_conn(schema) as conn:
        conturi = _fc.conturi_cu_miscare(conn, schema, an, luna)
        fisa = None
        if cont:
            try:
                # [lotul 3, 04.09.2026] `cont=9999` intorcea o FISA — cu `temei_completitudine`
                # scris despre contul 9999, cu sold zero si zero randuri. Adica un artefact
                # contabil, cu temei citat, despre un cont care nu exista in planul firmei.
                # Aceeasi aplicatie il refuza explicit la `POST /jurnal` („contul 9999 nu exista
                # in planul de conturi al firmei"): stia raspunsul, dar nu si aici. *Un formular
                # gol despre un cont inexistent nu e o fisa goala — e o afirmatie ca acel cont
                # exista si n-are miscare.* `cere_cont` ridica `ValueError`, deci intra in `try`.
                _cv.cere_cont(conn, schema, cont, "cont")
                fisa = _fc.pentru_json(_fc.fisa_cont(conn, schema, cont, an, luna))
            except ValueError as e:
                raise HTTPException(422, str(e))
    return {"an": an, "luna": luna, "formular": _fc.COD_FORMULAR,
            "conturi": conturi, "fisa": fisa}


@app.get("/tenants/{tenant_id}/jurnal-marja")  # [api_intern_v1] raport regim marja - fara UI inca, pastrat deliberat
def jurnal_marja(tenant_id: int, tip: str, luna: str, ctx=Depends(cere_cabinet)):
    """tip: secondhand|turism; luna: YYYY-MM. Jurnal special vanzari regim marja:
    per nota cost/marja neta/TVA + totaluri perioada (norme pct. 86)."""
    from decimal import Decimal
    marker = {"secondhand": "art. 312", "turism": "art. 311"}.get(tip)
    if not marker:
        raise HTTPException(422, "tip invalid (secondhand|turism)")
    if len(luna) != 7 or luna[4] != "-":
        raise HTTPException(422, "luna format YYYY-MM")
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant_citire(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        with conn.cursor() as cur:
            cur.execute(f"""SELECT i.id, i.data, i.descriere, i.status,
                                   l.cont_credit, l.suma, l.id
                            FROM {schema}.inregistrari i
                            JOIN {schema}.inregistrari_linii l ON l.inregistrare_id = i.id
                            WHERE i.descriere LIKE %s
                              AND to_char(i.data, 'YYYY-MM') = %s
                            ORDER BY i.data, i.id, l.id""",
                        ("%" + marker + "%", luna))
            rows = cur.fetchall()
    note = {}
    for iid, data, descr, status, cont, suma, lid in rows:
        n = note.setdefault(iid, {"id": iid, "data": str(data), "descriere": descr,
                                  "status": status, "cost": Decimal("0"),
                                  "marja_neta": Decimal("0"), "tva": Decimal("0")})
        if cont == "4427":
            n["tva"] += suma
        elif n["cost"] == 0:
            n["cost"] = suma
        else:
            n["marja_neta"] += suma
    tot_cost = sum(n["cost"] for n in note.values())
    tot_marja = sum(n["marja_neta"] for n in note.values())
    tot_tva = sum(n["tva"] for n in note.values())
    return {"tip": tip, "luna": luna, "numar_note": len(note),
            "note": [{**n, "cost": str(n["cost"]), "marja_neta": str(n["marja_neta"]),
                      "tva": str(n["tva"])} for n in note.values()],
            "total_cost": str(tot_cost), "total_baza_marja_neta": str(tot_marja),
            "total_tva_colectata": str(tot_tva)}


@app.get("/tenants/{tenant_id}/d406-active")  # [api_intern_v1] SAF-T sub-sectiune - fara UI inca, pastrat deliberat
def d406_active_xml(tenant_id: int, an: int, ctx=Depends(cere_cabinet)):
    """Sectiunea Assets SAF-T pentru anul dat (D406 anual - active)."""
    from fastapi.responses import Response
    from core import d406_active as _m
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        with conn.cursor() as cur:
            cur.execute(f"""SELECT id, cod, denumire, cont_imobilizare, cont_amortizare,
                                   valoare, rezidual, dnf_luni, data_pif, metoda, activ
                            FROM {schema}.mijloace_fixe
                            WHERE data_pif IS NOT NULL
                              AND EXTRACT(YEAR FROM data_pif) <= %s
                            ORDER BY id""", (an,))
            cols = [d[0] for d in cur.description]
            lista = [dict(zip(cols, r)) for r in cur.fetchall()]
    if not lista:
        raise HTTPException(404, "niciun mijloc fix cu PIF până în anul cerut")
    try:
        xml = _m.xml_assets(lista, an)
    except ValueError as e:
        raise HTTPException(422, str(e))
    return Response(content=xml, media_type="application/xml")


@app.get("/tenants/{tenant_id}/d406-stocuri")  # [api_intern_v1] SAF-T sub-sectiune - fara UI inca, pastrat deliberat
def d406_stocuri_xml(tenant_id: int, data_start: str, data_end: str, cui: str,
                     ctx=Depends(cere_cabinet)):
    """Sectiunea PhysicalStock SAF-T pe perioada (D406 la cerere ANAF).
    data_start/data_end: YYYY-MM-DD; cui: OwnerID (CUI firma)."""
    from datetime import date as _date
    from fastapi.responses import Response
    from core import d406_stocuri as _m
    try:
        ds, de = _date.fromisoformat(data_start), _date.fromisoformat(data_end)
    except ValueError:
        raise HTTPException(422, "date format YYYY-MM-DD")
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        with conn.cursor() as cur:
            cur.execute(f"""SELECT a.id, a.denumire, a.um, a.cont_stoc,
                                   m.data, m.tip, m.cantitate, m.valoare
                            FROM {schema}.articole a
                            JOIN {schema}.miscari_stoc m ON m.articol_id = a.id
                            WHERE m.data <= %s
                            ORDER BY a.id, m.data, m.id""", (de,))
            rows = cur.fetchall()
    grupat = {}
    for aid, den, um, cont, data, tip, cant, val in rows:
        art, mis = grupat.setdefault(aid, ({"id": aid, "denumire": den, "um": um,
                                            "cont_stoc": cont}, []))
        mis.append({"data": data, "tip": tip, "cantitate": cant, "valoare": val})
    try:
        xml = _m.xml_physical_stock(list(grupat.values()), ds, de, cui)
    except ValueError as e:
        raise HTTPException(422, str(e))
    return Response(content=xml, media_type="application/xml")




class PrapastieIn(BaseModel):
    salariu_brut: float
    persoane_intretinere: int = 0
    data_nastere: Optional[str] = None
    copii_scolarizati: int = 0
    declaratie_copii: bool = False
    tip_norma: str = "intreaga"
    ore_zi: Optional[float] = None
    data_angajare: Optional[str] = None
    scutit_contrib_minim: bool = False


@app.post("/tenants/{tenant_id}/prapastie-salariu")
# [R49, varianta (c)] Cat pierde salariatul daca brutul trece peste salariul minim — cu cifre,
# calculate cu TOATE elementele formularului, nu cu valori implicite (aia a invalidat R28).
# NU scrie nimic: e un calcul peste ce s-a completat pe ecran.
def tenant_prapastie_salariu(tenant_id: int, date: PrapastieIn, ctx=Depends(cere_cabinet)):
    from core import prapastie_salariu as _pr
    _schema_sau_404(ctx, tenant_id)
    return _pr.prapastie(date.salariu_brut, date.model_dump())


@app.post("/tenants/{tenant_id}/calcul-cm")  # [api_intern_v1] calculator CM - fara UI inca, pastrat deliberat
def calcul_cm_endpoint(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {salariat_id, an, luna (luna certificatului), zile_lucratoare_cm,
    cod?, zile_episod?, prima_zi_din_episod?, spitalizare?, data_certificat?}.
    Media pe 6 luni anterioare lunii certificatului (sau cate exista, art. 10 al. 4 OUG 158/2005),
    din statele EMISE - vezi core/baza_cm.py. Raspunsul poarta `baza_temei`, care spune pe ce s-a
    facut media (cate luni emise, cate recalculate) - o cifra fara sursa nu se poate contesta."""
    from datetime import date as _date
    from core import salarizare as _s
    from core import stat_plata_api as _sp
    from core import scadente as _scad
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
    # [lotul 4, 04.09.2026] Trei defecte, toate aici. `{}` cadea cu `KeyError` NEPRINS (`500`);
    # `luna=13` mergea pana la capat si intorcea o indemnizatie calculata — cu alta baza, fiindca
    # fereastra de 6 luni se muta —, iar `zile_lucratoare_cm=-5` trecea tacut, cu `brut 0`. *O
    # indemnizatie de concediu medical calculata pe o luna care nu exista e o cifra care intra in
    # stat, in D112 si in decontul cu CNAS.*
    try:
        an, luna = int(corp["an"]), int(corp["luna"])
        sal_id = int(corp["salariat_id"])
        zile_cm = int(corp["zile_lucratoare_cm"])
    except (KeyError, TypeError, ValueError) as e:
        raise HTTPException(422, _mesaj_intrare(e) if isinstance(e, KeyError) else
                            "Anul, luna, salariatul și zilele de concediu medical se așteaptă ca "
                            "numere întregi: %s" % e)
    _cere_perioada(an, luna)
    if zile_cm < 0:
        raise HTTPException(422, "Zilele de concediu medical nu pot fi negative (am primit %d). "
                                 "Se numără zilele lucrătoare acoperite de certificat." % zile_cm)
    # [baza_cm 22.08.2026, DECIS DE COSTIN: EMIS] Baza vine din statele EMISE; lunile neemise se
    # recalculeaza, dar se NUMARA separat si se spun in `temei`.
    #
    # Argumentul din 20.08 („calculeaza, nu citi din state_plata") era corect PENTRU TABELUL DE
    # ATUNCI: un cache de navigare, populat ca efect secundar al unui GET, in care lunile nedeschise
    # lipseau tacit. Din 21.08 `state_plata` e REGISTRUL DOCUMENTELOR EMISE, cu amprenta si
    # exemplare - sursa s-a schimbat sub argument. Ce s-a platit efectiv e un FAPT, iar media legala
    # (OUG 158/2005 art.10 al.4) se face pe ce a PRIMIT omul, nu pe ce ar rezulta din calculul de azi.
    from core import baza_cm as _bcm
    _luni = _bcm.luni_anterioare(an, luna)
    with db.get_conn(schema) as conn:  # stat_plata foloseste nume necalificate -> search_path pe tenant
        _emise, _recalc = _bcm.culege(conn, schema, sal_id, _luni)
    _b = _bcm.aduna(_luni, _emise, _recalc, _scad.zile_lucratoare_luna)
    venituri, zile, nr_luni = _b["venituri"], _b["zile"], _b["nr_luni"]
    if nr_luni == 0 or zile == 0:
        raise HTTPException(422, "Nu pot calcula media: salariatul nu are nicio lună lucrată în cele "
                                 "6 luni dinaintea certificatului. Verifică data angajării și pontajul.")
    try:
        r = _s.calcul_cm(venituri, zile, zile_cm,
                         cod=corp.get("cod", "01"),
                         zile_episod=corp.get("zile_episod"),
                         prima_zi_din_episod=corp.get("prima_zi_din_episod", True),
                         spitalizare=corp.get("spitalizare", False),
                         la_data=_date.fromisoformat(corp["data_certificat"])
                                 if corp.get("data_certificat") else None)
    except (ValueError, KeyError) as e:
        raise HTTPException(422, _mesaj_intrare(e))
    r["luni_in_baza"] = nr_luni
    r["venituri_baza"] = str(venituri)
    r["zile_baza"] = int(zile)
    # [baza_cm 22.08.2026] PE CE s-a facut media - o cifra fara sursa nu se poate contesta. Cand se
    # amesteca luni emise cu luni recalculate, contabilul trebuie s-o vada, nu s-o deduca.
    r["baza_temei"] = _b["temei"]
    r["baza_luni_emise"] = _b["luni_emise"]
    r["baza_luni_recalculate"] = _b["luni_recalculate"]
    return r


@app.post("/tenants/{tenant_id}/facturi/{factura_id}/trimite-spv")
# [R42] „iese către o autoritate" — e-Factura ajunge la ANAF.
def factura_trimite_spv(tenant_id: int, factura_id: int, ctx=Depends(cere_rol("admin_firma"))):
    """Trimite o factura emisa in SPV (F126/F160). Porti in ordine fixa (efactura_send.trimite):
    token viu -> validare/FACT1 -> idempotency -> upload pe tokenul PRINCIPALULUI (cabinet/gratuit).
    Poll-ul stareMesaj/descarcare ramane pe cron. Recipisa live = pending drept (ca F176)."""
    from core import efactura_send as _efs
    principal = _spv_rute.spv_principal(ctx)   # token owner (cabinet XOR gratuit); 403 daca niciunul
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
    if not schema:
        raise HTTPException(404, "tenant inexistent sau fără acces")
    mediu = os.environ.get("EFACTURA_MEDIU", "prod")
    try:
        r = _efs.trimite(schema, factura_id, principal, mediu=mediu)
    except _efs.EDateIncomplete as e:
        raise HTTPException(422, str(e))
    except NotImplementedError as e:
        raise HTTPException(422, "Tip de factură netratat încă în e-Factura: %s" % e)
    st = r.get("stare")
    if st == "fara_token":
        raise HTTPException(409, r.get("mesaj", "Conectează ANAF (SPV) înainte de a trimite."))
    if st == "deja_trimisa":
        raise HTTPException(409, "Factura are deja o trimitere activa in SPV (%s)." % r.get("stare_existenta"))
    if st == "nevalidat":
        return {"stare": "nevalidat", "erori": r.get("validare_mesaje", [])}
    return {"stare": st, "index_incarcare": r.get("index_incarcare"),
            "execution_status": r.get("execution_status"),
            "erori": r.get("errors") or ([r.get("raspuns", "")] if st in ("nok", "eroare_upload") else []),
            "mesaj": r.get("raspuns")}


@app.get("/tenants/{tenant_id}/trimiteri-spv")
def facturi_trimiteri_spv(tenant_id: int, ctx=Depends(cere_context)):
    """Starea SPV cea mai recenta per factura (pentru semaforul butonului). Fara apel ANAF."""
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        with conn.cursor() as cur:
            cur.execute(f"""SELECT DISTINCT ON (factura_id) factura_id, stare, index_incarcare, error_message
                              FROM {schema}.efactura_trimiteri ORDER BY factura_id, id DESC""")
            rows = cur.fetchall()
    return {str(r[0]): {"stare": r[1], "index_incarcare": r[2], "error_message": r[3]} for r in rows}


def _factura_din_parsat(cur, schema, f):
    """Insereaza o factura parsata (dict de la efactura_import.parseaza_xml) in facturi + linii.
    Idempotent pe (numar, tert_cui, data_emitere). Intoarce (factura_id, creat_nou): daca exista
    deja, intoarce id-ul EXISTENT + False (nu insereaza). Sursa UNICA a inserarii - folosit de
    /import-efactura (upload manual) SI de validarea four-eyes a facturilor primite (nu doua conducte)."""
    cur.execute(f"""SELECT id FROM {schema}.facturi
                    WHERE numar=%s AND COALESCE(tert_cui,'')=%s AND data_emitere=%s""",
                (f["numar"], f["tert_cui"], f["data_emitere"]))
    ex = cur.fetchone()
    if ex:
        return ex[0], False
    # [R91/KKK1] Starea depinde de DIRECȚIE, și nu e o subtilitate:
    #   * **primită** -> `importata`, ca până acum. Recunoașterea ei există deja și e alt act:
    #     `/facturi-primite/{id}/valideaza`, unde omul alege contul și clasifică regimul (R88).
    #   * **emisă** -> `de_recunoscut`. Documentul a fost emis în altă parte, deci sosirea lui nu e
    #     faptul economic al firmei. Nota vine din `/facturi/{id}/recunoaste`.
    # **NICIUNA nu primește notă aici** — la fel ca înainte. Ce se schimbă e că absența nu mai e o
    # scăpare declarată, ci o etapă cu act propriu.
    _stare = "de_recunoscut" if f["directie"] == "emisa" else "importata"
    cur.execute(f"""INSERT INTO {schema}.facturi
                    (numar, data_emitere, data_scadenta, total, tva, moneda, directie, status,
                     xml, tert_nume, tert_cui)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                (f["numar"], f["data_emitere"], f["data_scadenta"], f["total"], f["tva"],
                 f["moneda"], f["directie"], _stare, f["xml"], (f["tert_nume"] or "")[:255],
                 (f["tert_cui"] or "")[:30]))
    fid = cur.fetchone()[0]
    for ln in f["linii"]:
        cur.execute(f"""INSERT INTO {schema}.factura_linii
                        (factura_id, descriere, cantitate, pret_unitar, cota_tva)
                        VALUES (%s,%s,%s,%s,%s)""",
                    (fid, ln["descriere"][:255], ln["cantitate"], ln["pret_unitar"], ln["cota_tva"]))
    return fid, True


@app.post("/tenants/{tenant_id}/import-efactura")  # [api_intern_v1] upload manual XML/ZIP - fara buton in UI, pastrat deliberat. Verificat 27.08.2026 - niciun apelant in static/, in crontab sau in timerele systemd. (R70). CORECTAT 29.08.2026: forma veche scria ca `core/spv_receive` cheama direct `_factura_din_parsat` - E FALS. `spv_receive.importa_mesaj` scrie DOAR in `efactura_primite`, si numai mesaje al caror `cif_beneficiar` e chiar tenantul (gard anti-scurgere), deci numai PRIMITE. Consecinta, si e chiar perimetrul lui R91: singura cale prin care o factura EMISA intra prin import e ruta asta, incarcarea manuala de XML.
async def import_efactura(tenant_id: int, fisiere: list[UploadFile] = File(...),
                          ctx=Depends(cere_cabinet)):
    """Upload XML/ZIP e-Factura. Parseaza UBL, directie auto (CUI firma vs furnizor),
    idempotent pe (numar, tert_cui, data_emitere)."""
    from core import efactura_import as _ef
    rezultate = {"importate": 0, "duplicate": 0, "erori": []}
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        with conn.cursor() as cur:
            cur.execute(f"SELECT cui FROM {schema}.firma_profil LIMIT 1")
            rand = cur.fetchone()
            if not rand or not rand[0]:
                raise HTTPException(422, CUI_FIRMA_LIPSA)
            cui_firma = rand[0]
            for up in fisiere:
                continut = await up.read()
                try:
                    perechi = _ef.extrage_fisiere(up.filename or "f.xml", continut)
                except Exception as e:
                    rezultate["erori"].append(f"{up.filename}: {e}")
                    continue
                for nume, xmlb in perechi:
                    try:
                        f = _ef.parseaza_xml(xmlb, cui_firma)
                    except ValueError as e:
                        rezultate["erori"].append(f"{nume}: {e}")
                        continue
                    _fid, _nou = _factura_din_parsat(cur, schema, f)
                    rezultate["importate" if _nou else "duplicate"] += 1
        conn.commit()
    return rezultate


@app.get("/tenants/{tenant_id}/facturi-primite")
def facturi_primite_lista(tenant_id: int, ctx=Depends(cere_context)):
    """Facturi primite din SPV de VALIDAT (four-eyes): ciorne parsate + cont sugerat. Acces = are
    acces la tenant (rol cu drept SAU proprietar gratuit); NU compara identitati (importatorul e cronul)."""
    from core import efactura_import as _ef
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        out = []
        with conn.cursor() as cur:
            cur.execute(f"""SELECT id, cif_emitent, cif_beneficiar, status, xml_brut, factura_id
                              FROM {schema}.efactura_primite WHERE status IN ('descarcata','ciorna')
                              ORDER BY importat_la DESC LIMIT 100""")
            rows = cur.fetchall()
            for (pid, cife, cifb, status, xmlb, fid) in rows:
                cur.execute(f"""SELECT cont_cheltuiala FROM {schema}.efactura_primite
                                WHERE cif_emitent=%s AND cont_cheltuiala IS NOT NULL
                                ORDER BY validat_la DESC NULLS LAST LIMIT 1""", (cife,))
                pr = cur.fetchone()
                info = {"id": pid, "cif_emitent": cife, "status": status, "factura_id": fid,
                        "cont_sugerat": pr[0] if pr else ""}
                try:
                    f = _ef.parseaza_xml((xmlb or "").encode("utf-8"), cifb)
                    info.update({"parsabila": True, "furnizor": f.get("tert_nume"),
                                 "numar": f.get("numar"), "data": str(f.get("data_emitere") or ""),
                                 "total": str(f.get("total") or ""), "tva": str(f.get("tva") or ""),
                                 "moneda": f.get("moneda"),
                                 "linii": [{"descriere": l["descriere"], "cantitate": str(l["cantitate"]),
                                            "pret": str(l["pret_unitar"]), "cota": str(l["cota_tva"])}
                                           for l in (f.get("linii") or [])]})
                except Exception as e:
                    info.update({"parsabila": False, "eroare_parse": str(e)[:200]})
                out.append(info)
    return {"primite": out}


@app.get("/tenants/{tenant_id}/facturi-primite/{primita_id}/xml")
def factura_primita_xml(tenant_id: int, primita_id: int, ctx=Depends(cere_context)):
    """XML-ul brut arhivat (la click, nu in fata)."""
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant_citire(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        with conn.cursor() as cur:
            cur.execute(f"SELECT xml_brut FROM {schema}.efactura_primite WHERE id=%s", (primita_id,))
            r = cur.fetchone()
    if not r:
        raise HTTPException(404, "factură primită inexistentă")
    return {"xml": r[0] or ""}


@app.post("/tenants/{tenant_id}/facturi-primite/{primita_id}/valideaza")
def factura_primita_valideaza(tenant_id: int, primita_id: int, corp: dict = Body(default={}),
                              ctx=Depends(cere_rol("admin_firma"))):
    """FOUR-EYES: omul valideaza ciorna importata de cron -> creeaza cheltuiala (factura primita) +
    leaga factura_id + status=validata. Idempotent (FOR UPDATE + verifica status). cont sugerat,
    confirmat de om. Gard = acces la tenant + actiune umana explicita; NU identitate != importator."""
    from core import efactura_import as _ef
    from core import contare_facturi as _cf
    cont = (corp.get("cont") or "").strip()
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        with conn.cursor() as cur:
            cur.execute(f"""SELECT status, xml_brut, cif_beneficiar, factura_id
                              FROM {schema}.efactura_primite WHERE id=%s FOR UPDATE""", (primita_id,))
            r = cur.fetchone()
            if not r:
                raise HTTPException(404, "factură primită inexistentă")
            status, xmlb, cifb, fid_ex = r
            if status == "validata":          # idempotent - nu crea a doua cheltuiala
                return {"stare": "deja_validata", "factura_id": fid_ex}
            if status == "respinsa":
                raise HTTPException(409, "factura a fost respinsa; nu se poate valida")
            # [FFF1] CONTUL DE CHELTUIALĂ E OBLIGATORIU. Decizia lui Costin (29.08.2026): nu cont
            # implicit — la venit, implicitul e o presupunere despre ce vinde firma; la cheltuială ar
            # fi una despre natura cheltuielii, adică exact lucrul pe care omul îl are în față —, și
            # nu validare fără notă, fiindcă asta ar reintroduce golul R88 pe ușa din spate.
            # SCHIMBARE DE COMPORTAMENT, declarată: până azi câmpul era `cont or None`, deci
            # validarea trecea fără el. De azi refuză.
            if not cont:
                # Detaliul e o STRUCTURĂ, ca la `LINII_INCOMPLETE`: frontendul (și garda) citesc
                # `cod`, nu propoziția. Un refuz recunoscut după text s-ar rupe la prima rescriere.
                from core import afirmatii as _af
                raise HTTPException(422, dict(_af.afirmatie(
                    "neconformitate", "CONT_CHELTUIALA_OBLIGATORIU",
                    "Alege contul de cheltuială înainte de a valida: validarea recunoaște "
                    "cheltuiala și îi scrie nota contabilă în același act, iar nota nu poate "
                    "ghici contul.",
                    unde="factura primită #%s" % primita_id,
                    regula="validarea unei facturi primite cere contul de cheltuială"),
                    cod="CONT_CHELTUIALA_OBLIGATORIU"))
            try:
                f = _ef.parseaza_xml((xmlb or "").encode("utf-8"), cifb)
            except Exception as e:
                raise HTTPException(422, "XML neparsabil: %s" % str(e)[:200])
            fid, _nou = _factura_din_parsat(cur, schema, f)   # leaga si factura existenta (dedup)
            cur.execute(f"""UPDATE {schema}.efactura_primite
                            SET status='validata', factura_id=COALESCE(%s, factura_id),
                                cont_cheltuiala=%s, validat_la=now() WHERE id=%s
                            RETURNING factura_id""", (fid, cont or None, primita_id))
            fid_final = cur.fetchone()[0]
            # [B1 D300] optiuni de clasificare pe factura primita, alese de contabil la validare:
            # furnizor cu TVA la incasare (deducere amanata la plata, art.297 alin.2) / tara
            # partenerului (achizitie IC vs import). Setate pe factura legata (fid_final).
            _ftva = corp.get("furnizor_tva_incasare")
            _ttara = (corp.get("tert_tara") or "").strip().upper()
            if fid_final and (_ftva is not None or _ttara):
                _sets, _vals = [], []
                if _ftva is not None:
                    _sets.append("furnizor_tva_incasare=%s"); _vals.append(bool(_ftva))
                if _ttara:
                    _sets.append("tert_tara=%s"); _vals.append(_ttara)
                _vals.append(fid_final)
                cur.execute(f"UPDATE {schema}.facturi SET " + ", ".join(_sets) + " WHERE id=%s", _vals)
        # [FFF1] NOTA SE SCRIE AICI, în același act cu validarea — după ce clasificarea e pusă pe
        # factură, ca nota s-o poată citi. Validarea *este* actul prin care firma recunoaște
        # cheltuiala: patru-ochi s-a consumat deja, contul tocmai a fost ales, regimul tocmai a fost
        # clasificat. La import n-ar fi existat niciuna dintre ele.
        # [FFF2] Clasa ambiguă — furnizor la încasare + firmă în regim normal — e REFUZATĂ automat
        # (varianta (ii)), cu motivul întors pe ecran. Factura se validează oricum; nota o scrie omul
        # din butonul de contabilizare. Un refuz al notei nu poate anula recunoașterea cheltuielii.
        from core import afirmatii as _af
        contare = {"stare": "neaplicabil", "afirmatie": _af.afirmatie(
            "absenta_observatie", "CONTARE_NEAPLICABILA",
            "validarea n-a legat nicio factură, deci n-are ce conta",
            surse_consultate=["efactura_primite.factura_id"])}
        if fid_final:
            try:
                with _cf.cursor_dict(conn) as cur2:
                    contare = _cf.contabilizeaza(cur2, schema, fid_final, automat=True,
                                                 cont_cheltuiala=cont or None)
            except _cf.RefuzContare as e:
                contare = {"stare": "refuzata", "cod": e.cod, "detalii": e.detalii,
                           "afirmatie": _af.afirmatie(
                               "neconformitate", e.cod, e.mesaj,
                               unde="factura #%s" % fid_final,
                               regula="nota automată se scrie doar când toate intrările ei sunt "
                                      "cunoscute")}
        conn.commit()
    return {"stare": "validata", "factura_id": fid_final, "contare": contare}


@app.post("/tenants/{tenant_id}/facturi-primite/{primita_id}/respinge")
def factura_primita_respinge(tenant_id: int, primita_id: int, corp: dict = Body(default={}),
                             ctx=Depends(cere_context)):
    """Respinge o factura primita: status=respinsa + motiv. NU sterge randul (ramane cu istoric)."""
    motiv = (corp.get("motiv") or "").strip()
    if not motiv:
        raise HTTPException(422, "motivul respingerii e obligatoriu")
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        with conn.cursor() as cur:
            cur.execute(f"SELECT status FROM {schema}.efactura_primite WHERE id=%s FOR UPDATE", (primita_id,))
            r = cur.fetchone()
            if not r:
                raise HTTPException(404, "factură primită inexistentă")
            if r[0] == "validata":
                raise HTTPException(409, "factura a fost deja validată")
            cur.execute(f"""UPDATE {schema}.efactura_primite SET status='respinsa', motiv_respins=%s
                            WHERE id=%s""", (motiv, primita_id))
        conn.commit()
    return {"stare": "respinsa"}


@app.post("/tenants/{tenant_id}/reges-config")
# [R56, 26.08.2026] Cheile de acces la un sistem extern nu sunt date ale firmei — sunt
# CREDENTIALE. Costin: *„admin_firma, nu drept fin. Un drept nou e un al doilea sistem de
# autorizare de intretinut, iar cele trei rute nu justifica unul."* Acelasi criteriu ca la
# R42 (d), pornirea/oprirea unui canal — deja aplicat pe `PUT /woocommerce/config`.
def reges_config(tenant_id: int, corp: dict = Body(...),
                 ctx=Depends(cere_rol("admin_firma"))):
    """corp: {username, parola, mediu test|prod}. Chei API din aplicatia REGES Angajator."""
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        if corp.get("mediu", "test") not in ("test", "prod"):
            raise HTTPException(422, nomenclator_cerut("mediu", "test|prod"))
        with conn.cursor() as cur:
            # upsert-ok: salvare credentiale REGES per tenant - update intentionat al aceleiasi chei (tenant_id)
            cur.execute("""INSERT INTO public.reges_chei (tenant_id, username, parola, mediu)
                           VALUES (%s,%s,%s,%s)
                           ON CONFLICT (tenant_id) DO UPDATE
                           SET username=EXCLUDED.username, parola=EXCLUDED.parola,
                               mediu=EXCLUDED.mediu""",
                        (tenant_id, corp["username"], corp["parola"], corp.get("mediu", "test")))
        conn.commit()
    return {"ok": True}


@app.post("/tenants/{tenant_id}/reges-trimite-salariat")
# [R42] „iese către o autoritate" — salariatul ajunge în registrul de evidență a muncii.
def reges_trimite_salariat(tenant_id: int, corp: dict = Body(...),
                           ctx=Depends(cere_rol("admin_firma"))):
    """corp: {salariat_id, adresa, contract {numar, data_contract, data_inceput, salariu, cor, ...}?}.
    Trimite InregistrareSalariat (+ AdaugareContract daca vine si contract dupa referinta)."""
    from core import reges_client as _rg
    import uuid as _uuid
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        with conn.cursor() as cur:
            cur.execute("SELECT username, parola, mediu, author_id FROM public.reges_chei WHERE tenant_id=%s",
                        (tenant_id,))
            chei = cur.fetchone()
            if not chei:
                raise HTTPException(422, "chei REGES neconfigurate - folosește reges-config")
            cur.execute(f"SELECT cnp, nume, prenume FROM {schema}.salariati WHERE id=%s",
                        (corp["salariat_id"],))
            s = cur.fetchone()
            if not s:
                raise HTTPException(404, "salariat inexistent")
        mid = _uuid.uuid4()
        xml = _rg.mesaj_inregistrare_salariat(
            {"cnp": s[0], "nume": s[1], "prenume": s[2], "adresa": corp.get("adresa")},
            str(chei[3]), chei[0], message_id=mid)
        cl = _rg.RegesClient(chei[0], chei[1], chei[2])
        try:
            status, rasp = cl.trimite_salariat(xml)
        except Exception as e:
            raise HTTPException(502, f"REGES: {e}")
        with conn.cursor() as cur:
            cur.execute("""INSERT INTO public.reges_mesaje
                           (tenant_id, salariat_id, operatie, message_id, response_id, raspuns)
                           VALUES (%s,%s,'InregistrareSalariat',%s,%s,%s) RETURNING id""",
                        (tenant_id, corp["salariat_id"], str(mid), None, rasp[:4000]))
            rid = cur.fetchone()[0]
        conn.commit()
    return {"mesaj_id": rid, "http_status": status, "raspuns": rasp[:500]}


@app.post("/tenants/{tenant_id}/reges-poll")
# [R56, 26.08.2026] Cheile de acces la un sistem extern nu sunt date ale firmei — sunt
# CREDENTIALE. Costin: *„admin_firma, nu drept fin. Un drept nou e un al doilea sistem de
# autorizare de intretinut, iar cele trei rute nu justifica unul."* Acelasi criteriu ca la
# R42 (d), pornirea/oprirea unui canal — deja aplicat pe `PUT /woocommerce/config`.
def reges_poll(tenant_id: int, ctx=Depends(cere_rol("admin_firma"))):
    """Citeste+consuma un mesaj din coada REGES; salveaza referintele in reges_mesaje."""
    from core import reges_client as _rg
    import re as _re
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        with conn.cursor() as cur:
            cur.execute("SELECT username, parola, mediu FROM public.reges_chei WHERE tenant_id=%s",
                        (tenant_id,))
            chei = cur.fetchone()
            if not chei:
                raise HTTPException(422, "chei REGES neconfigurate")
        cl = _rg.RegesClient(chei[0], chei[1], chei[2])
        try:
            status, rasp = cl.poll_mesaj()
        except Exception as e:
            raise HTTPException(502, f"REGES: {e}")
        m_mid = _re.search(r"<(?:Initial)?MessageId>([0-9a-f-]{36})", rasp)
        m_rs = _re.search(r"ReferintaSalariat>?\s*<Id>([0-9a-f-]{36})", rasp)
        m_rc = _re.search(r"ReferintaContract>?\s*<Id>([0-9a-f-]{36})", rasp)
        if m_mid:
            with conn.cursor() as cur:
                cur.execute("""UPDATE public.reges_mesaje
                               SET status='raspuns', raspuns=%s,
                                   referinta_salariat=COALESCE(%s::uuid, referinta_salariat),
                                   referinta_contract=COALESCE(%s::uuid, referinta_contract)
                               WHERE message_id=%s::uuid AND tenant_id=%s""",
                            (rasp[:4000], m_rs.group(1) if m_rs else None,
                             m_rc.group(1) if m_rc else None, m_mid.group(1), tenant_id))
            conn.commit()
    return {"http_status": status, "raspuns": rasp[:1000]}


@app.post("/tenants/{tenant_id}/achizitie-taxare-inversa")
def achizitie_taxare_inversa(tenant_id: int, corp: dict = Body(...),
                             ctx=Depends(cere_rol("admin_firma"))):
    """corp: {data, categorie, valoare (fara TVA), cont_destinatie, cota?,
    furnizor_platitor_tva, descriere?}. Beneficiarul (firma) trebuie platitor TVA.
    Nota ciorna: cont_dest=401 valoare + 4426=4427 TVA (norme pct. 109)."""
    from decimal import Decimal
    from datetime import date as _date
    from core import taxare_inversa as _ti
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        _cere_luna_deschisa(conn, schema, corp.get("data"))
        with conn.cursor() as cur:
            cur.execute(f"SELECT COALESCE(platitor_tva, true) FROM {schema}.firma_profil LIMIT 1")
            rand = cur.fetchone()
            beneficiar_tva = bool(rand[0]) if rand else True
        from core import facturi_api as _fa
        try:
            categorie = str(corp["categorie"])
            ok, mentiune = _ti.se_aplica(categorie, corp["valoare"],
                                         corp.get("furnizor_platitor_tva", True),
                                         beneficiar_tva,
                                         _date.fromisoformat(corp["data"]))
            cont = _cv.cere_cont(conn, schema, corp.get("cont_destinatie"), "cont_destinatie")  # [R54]
            val = Decimal(str(corp["valoare"]))
            cota = _common.cota_ceruta(corp)
            tva = _ti.tva_beneficiar(val, cota)
            furnizor_cui = str(corp.get("furnizor_cui") or "").strip().upper().replace(" ", "")
            if not furnizor_cui:
                raise ValueError("CUI furnizor obligatoriu (taxare inversa e intre platitori RO - furnizor cu CUI)")
            numar = str(corp.get("numar") or "").strip()
            if not numar:
                raise ValueError("numar factura furnizor obligatoriu")
            furnizor_nume = str(corp.get("furnizor_nume") or "").strip()
        except (ValueError, KeyError) as e:
            raise HTTPException(422, _mesaj_intrare(e))
        descr = (corp.get("descriere") or "Achizitie") + " - " + mentiune
        with conn.cursor() as cur:
            cur.execute(f"SET LOCAL search_path TO {schema}")   # creeaza_factura foloseste INSERT necalificat
            # 1) rand FACTURA (directie=primita, furnizor RO cu CUI, categorie_331 -> codPR, taxare_inversa=True)
            #    = sursa citita de D394 (op1 tip C + op11 codPR). Linie cota reala -> baza/tva reverse-charge.
            from core import anaf_api as _anaf
            _furn_pl = str(corp.get("furnizor_platitor_tva", True)).strip().lower() not in ("false", "nu", "0")
            _tert_pl = _anaf.platitor_tva_freeze(furnizor_cui, fallback=_furn_pl)   # INGHETAT la creare (fapt)
            fres = _fa.creeaza_factura(conn, numar=numar, data_emitere=corp["data"], directie="primita",
                                       linii=[{"descriere": descr[:200], "cantitate": 1,
                                               "pret_unitar": str(val), "cota_tva": cota}],
                                       tert_nume=furnizor_nume or None, tert_cui=furnizor_cui,
                                       categorie_331=categorie, taxare_inversa=True, status="importata",
                                       tert_platitor_tva=_tert_pl)
            fid = fres["factura_id"]
            # 2) contabilizare LEGATA (factura_id) - nota specializata reverse-charge 4426=4427, NU cea standard
            cur.execute(f"""INSERT INTO {schema}.inregistrari (data, factura_id, descriere, sursa, status)
                            VALUES (%s,%s,%s,'facturi','ciorna') RETURNING id""",
                        (corp["data"], fid, descr[:200]))
            iid = cur.fetchone()[0]
            for d, c, s in [(cont, "401", val), ("4426", "4427", tva)]:
                cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                                (inregistrare_id, cont_debit, cont_credit, suma)
                                VALUES (%s,%s,%s,%s)""", (iid, d, c, s))
        conn.commit()
    return {"inregistrare_id": iid, "factura_id": fid, "valoare": str(val), "tva": str(tva),
            "mentiune": mentiune}


@app.get("/tenants/{tenant_id}/verifica-vies")  # [vies_emitere_v1] validare VIES - folosit din emitere
def verifica_vies_ep(tenant_id: int, cod_tva: str, ctx=Depends(cere_context)):
    """Verifica un cod TVA UE in VIES (API oficial CE)."""
    from core import intracomunitar as _ic
    with db.get_conn() as conn:
        if not auth_api.schema_tenant(conn, ctx["uid"], tenant_id):
            raise HTTPException(404, "tenant inexistent sau fără acces")
    try:
        return _ic.verifica_vies(cod_tva)
    except ValueError as e:
        raise HTTPException(422, str(e))
    except Exception as e:
        raise HTTPException(502, f"VIES indisponibil: {e}")


@app.post("/tenants/{tenant_id}/achizitie-ic")
def achizitie_ic(tenant_id: int, corp: dict = Body(...),
                 ctx=Depends(cere_rol("admin_firma"))):
    """AIC bunuri/servicii primite (art. 268 / 278(2), plata = beneficiar art. 308).
    corp: {data, valoare (RON), cont_destinatie, cota?, tip bunuri|servicii, descriere?}.
    Nota ciorna: cont_dest=401 + 4426=4427 (norme 109)."""
    from decimal import Decimal
    from core import intracomunitar as _ic
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        _cere_luna_deschisa(conn, schema, corp.get("data"))
        from core import facturi_api as _fa
        try:
            val = Decimal(str(corp["valoare"]))
            tva = _ic.tva_taxare_inversa(val, _common.cota_ceruta(corp))
            cont = _cv.cere_cont(conn, schema, corp.get("cont_destinatie"), "cont_destinatie")  # [R54]
            cod_tva_furnizor = str(corp.get("cod_tva_furnizor") or "").strip().upper().replace(" ", "")
            if not cod_tva_furnizor:
                raise ValueError("cod TVA furnizor UE obligatoriu (fara el achizitia NU ajunge in D390)")
            numar = str(corp.get("numar") or "").strip()
            if not numar:
                raise ValueError("numar factura furnizor obligatoriu")
            furnizor_nume = str(corp.get("furnizor_nume") or "").strip()
            data_fg = corp.get("data_faptului_generator") or None
            # [lotul 5, 04.09.2026] `tip` se citea cu un `if ... == "servicii" else bunuri`: orice
            # altceva — inclusiv o valoare gresita — devenea BUNURI, tacut. Probat cu
            # `tip="altceva"`: `200`, si achizitia a intrat in evidenta ca bunuri. Nu e o nuanta:
            # tipul decide incadrarea in D390 (bunuri vs servicii) si temeiul citat pe nota.
            if corp.get("tip") not in ("bunuri", "servicii"):
                raise ValueError(nomenclator_cerut("tip", "bunuri|servicii"))
        except (ValueError, KeyError) as e:
            raise HTTPException(422, _mesaj_intrare(e))
        tip = "servicii IC primite (art. 278(2))" if corp.get("tip") == "servicii"               else "achizitie intracomunitara bunuri (art. 268)"
        descr = (corp.get("descriere") or "AIC") + f" - {tip}, taxare inversa 4426=4427"
        with conn.cursor() as cur:
            cur.execute(f"SET LOCAL search_path TO {schema}")   # creeaza_factura foloseste INSERT necalificat
            # 1) rand FACTURA (directie=primita, furnizor UE) = sursa citita de D390. Factura UE fara TVA RON
            #    (taxare inversa la beneficiar) -> linie cota 0 -> total=val, tva=0 -> baza D390 = val.
            fres = _fa.creeaza_factura(conn, numar=numar, data_emitere=corp["data"], directie="primita",
                                       linii=[{"descriere": descr[:200], "cantitate": 1,
                                               "pret_unitar": str(val), "cota_tva": 0}],
                                       tert_nume=furnizor_nume or None, tert_cui=cod_tva_furnizor,
                                       data_faptului_generator=data_fg, status="importata")
            fid = fres["factura_id"]
            # 2) contabilizare LEGATA (factura_id) - nota specializata reverse-charge, NU cea standard
            cur.execute(f"""INSERT INTO {schema}.inregistrari (data, factura_id, descriere, sursa, status)
                            VALUES (%s,%s,%s,'facturi','ciorna') RETURNING id""",
                        (corp["data"], fid, descr[:200]))
            iid = cur.fetchone()[0]
            for d, c, s in [(cont, "401", val), ("4426", "4427", tva)]:
                cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                                (inregistrare_id, cont_debit, cont_credit, suma)
                                VALUES (%s,%s,%s,%s)""", (iid, d, c, s))
        conn.commit()
    return {"inregistrare_id": iid, "factura_id": fid, "valoare": str(val), "tva": str(tva)}


@app.post("/tenants/{tenant_id}/achizitie-neinregistrat")
def achizitie_neinregistrat(tenant_id: int, corp: dict = Body(...),
                            ctx=Depends(cere_rol("admin_firma"))):
    """Achizitie de la persoana fizica NEINREGISTRATA in scop TVA -> op N in D394 (pct.216 tip_partener=2).
    corp: {data, furnizor_nume (obligatoriu), valoare, cont_cheltuiala, numar?, categorie? (CODPR_N lit.D),
    descriere?}. Fara CUI furnizor -> tip N. categorie OPTIONALA: FARA ea N ramane EXCLUS din D394 cu avertisment
    (nu se ghiceste - continut declarat). PF nu factureaza TVA -> linie cota 0. Nota: cont_cheltuiala = 401."""
    from decimal import Decimal
    from core import facturi_api as _fa
    from core import d394 as _d394
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        _cere_luna_deschisa(conn, schema, corp.get("data"))
        try:
            furnizor_nume = str(corp.get("furnizor_nume") or "").strip()
            if not furnizor_nume:
                raise ValueError("nume furnizor obligatoriu (persoana fizica - apare in denP si in avertisment)")
            val = Decimal(str(corp["valoare"]))
            if val <= 0:
                raise ValueError("valoare invalidă")
            cont = _cv.cere_cont(conn, schema, corp.get("cont_cheltuiala"), "cont_cheltuiala")  # [R54]
            numar = str(corp.get("numar") or "").strip() or ("BORDEROU-" + str(corp["data"]))
            categorie = str(corp.get("categorie") or "").strip() or None
            if categorie and not _d394.codpr_N_din_categorie(categorie):
                raise ValueError("categorie N invalida (nomenclator lit.D CODPR_N): %s" % categorie)
        except (ValueError, KeyError) as e:
            raise HTTPException(422, _mesaj_intrare(e))
        descr = (corp.get("descriere") or "Achizitie de la neinregistrat") + " - " + furnizor_nume
        with conn.cursor() as cur:
            cur.execute(f"SET LOCAL search_path TO {schema}")
            # tert_cui GOL -> clasifica_partener -> tip_partener 2 (N); PF nu factureaza TVA -> linie cota 0.
            # `tert_pf=True` (23.08.2026): pana azi lipsa codului era declarata DOAR in comentariul de
            # deasupra, iar garda noua de la `cere_cod_partener` n-avea cum s-o citeasca. Achizitia de la
            # o persoana neinregistrata E cazul legitim fara cod - acum o spune CODUL, nu proza.
            fres = _fa.creeaza_factura(conn, numar=numar, data_emitere=corp["data"], directie="primita",
                                       linii=[{"descriere": descr[:200], "cantitate": 1,
                                               "pret_unitar": str(val), "cota_tva": 0}],
                                       tert_nume=furnizor_nume, tert_cui="", categorie_331=categorie,
                                       status="importata", tert_platitor_tva=False, tert_pf=True)
            fid = fres["factura_id"]
            cur.execute(f"""INSERT INTO {schema}.inregistrari (data, factura_id, descriere, sursa, status)
                            VALUES (%s,%s,%s,'facturi','ciorna') RETURNING id""",
                        (corp["data"], fid, descr[:200]))
            iid = cur.fetchone()[0]
            cur.execute(f"""INSERT INTO {schema}.inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma)
                            VALUES (%s,%s,'401',%s)""", (iid, cont, val))
        conn.commit()
    return {"inregistrare_id": iid, "factura_id": fid, "valoare": str(val),
            "categorie": categorie, "in_d394": bool(categorie)}


@app.post("/tenants/{tenant_id}/vanzare-ic")
def vanzare_ic(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """LIC bunuri (art. 294(2)a) sau prestare servicii IC (art. 278(2)).
    corp: {data, valoare, cod_tva_client, tip bunuri|servicii, dovada_transport?,
    cont_venit?, descriere?}. Verifica VIES LIVE. Nota: 4111=70x fara TVA."""
    from decimal import Decimal
    from core import intracomunitar as _ic
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        _cere_luna_deschisa(conn, schema, corp.get("data"))
        try:
            v = _ic.verifica_vies(corp["cod_tva_client"])
        except ValueError as e:
            raise HTTPException(422, str(e))
        except Exception as e:
            raise HTTPException(502, f"VIES indisponibil: {e}")
        try:
            if corp.get("tip") == "servicii":
                ok, ment = _ic.valideaza_prestare_ic(corp["cod_tva_client"], v["valid"])
                cont_venit = _cv.cere_cont(conn, schema, corp.get("cont_venit"), "cont_venit", "704")
                cont_venit = _cv.cere_cont(conn, schema, cont_venit, "cont_venit")
            else:
                ok, ment = _ic.valideaza_lic(corp["cod_tva_client"], v["valid"],
                                             bool(corp.get("dovada_transport")))
                cont_venit = _cv.cere_cont(conn, schema, corp.get("cont_venit"), "cont_venit", "707")
                cont_venit = _cv.cere_cont(conn, schema, cont_venit, "cont_venit")
            val = Decimal(str(corp["valoare"]))
            if val <= 0:
                raise ValueError("valoare invalidă")
        except (ValueError, KeyError) as e:
            raise HTTPException(422, _mesaj_intrare(e))
        descr = (corp.get("descriere") or "Vanzare IC") + " - " + ment +                 f" [{v['nume']}]"
        with conn.cursor() as cur:
            cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status)
                            VALUES (%s,%s,'facturi','ciorna') RETURNING id""",
                        (corp["data"], descr[:200]))
            iid = cur.fetchone()[0]
            cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                            (inregistrare_id, cont_debit, cont_credit, suma)
                            VALUES (%s,'4111',%s,%s)""", (iid, cont_venit, val))
        conn.commit()
    return {"inregistrare_id": iid, "mentiune": ment, "vies": v}



@app.post("/tenants/{tenant_id}/import-extracomunitar")
def import_extracomunitar(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, valoare_vamala (RON), procent_taxa_vamala?, accize?, accesorii?,
    cota?, certificat_amanare?, cont_destinatie, descriere?}.
    Nota ciorna: marfa cont=401; taxe vamale cont=446; TVA dupa mod:
    decont 4426=4427 | vama 4426=446 | cost cont=446."""
    from decimal import Decimal
    from core import import_export as _ie
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        _cere_luna_deschisa(conn, schema, corp.get("data"))
        with conn.cursor() as cur:
            cur.execute(f"SELECT COALESCE(platitor_tva, true) FROM {schema}.firma_profil LIMIT 1")
            rand = cur.fetchone()
            platitor = bool(rand[0]) if rand else True
        try:
            # [lotul 5] `procent_taxa_vamala=500` trecea: taxa vamala 5.000 la o valoare
            # vamala de 1.000, baza TVA 6.000. Un procent e o parte dintr-un intreg.
            _ptv = corp.get("procent_taxa_vamala", 0) or 0
            if not (0 <= float(_ptv) <= 100):
                raise ValueError("Procentul taxei vamale e între 0 și 100 — am primit %s. Taxa "
                                 "vamală e o parte din valoarea în vamă, nu un multiplu al ei."
                                 % (_ptv,))
            r = _ie.calcul_import(corp["valoare_vamala"],
                                  corp.get("procent_taxa_vamala", 0),
                                  corp.get("accize", 0), corp.get("accesorii", 0),
                                  _common.cota_ceruta(corp),
                                  bool(corp.get("certificat_amanare")), platitor)
            cont = _cv.cere_cont(conn, schema, corp.get("cont_destinatie"), "cont_destinatie")  # [R54]
            val = Decimal(str(corp["valoare_vamala"]))
        except (ValueError, KeyError) as e:
            raise HTTPException(422, _mesaj_intrare(e))
        mod_txt = {"decont": "TVA in decont (certificat art. 326(4), 4426=4427)",
                   "vama": "TVA platita in vama (deducere pe DVI art. 299(1)c)",
                   "cost": "neplatitor - TVA in cost"}[r["mod_tva"]]
        descr = (corp.get("descriere") or "Import extracomunitar") + " - DVI, " + mod_txt
        linii = [(cont, "401", val)]
        if r["taxa_vamala"] > 0:
            linii.append((cont, "446", r["taxa_vamala"]))
        if r["mod_tva"] == "decont":
            linii.append(("4426", "4427", r["tva"]))
        elif r["mod_tva"] == "vama":
            linii.append(("4426", "446", r["tva"]))
        else:
            linii.append((cont, "446", r["tva"]))
        with conn.cursor() as cur:
            cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status)
                            VALUES (%s,%s,'facturi','ciorna') RETURNING id""",
                        (corp["data"], descr[:200]))
            iid = cur.fetchone()[0]
            for d, c, s in linii:
                cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                                (inregistrare_id, cont_debit, cont_credit, suma)
                                VALUES (%s,%s,%s,%s)""", (iid, d, c, s))
        conn.commit()
    return {"inregistrare_id": iid, "taxa_vamala": str(r["taxa_vamala"]),
            "baza_tva": str(r["baza_tva"]), "tva": str(r["tva"]), "mod_tva": r["mod_tva"]}


@app.post("/tenants/{tenant_id}/export-extracomunitar")
def export_extracomunitar(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, valoare, tara_client, dovada_export, cont_venit?, descriere?}.
    Scutit art. 294(1)a cu DVE. Nota: 4111=70x fara TVA."""
    from decimal import Decimal
    from core import import_export as _ie
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        _cere_luna_deschisa(conn, schema, corp.get("data"))
        try:
            ok, ment = _ie.valideaza_export(corp.get("tara_client"),
                                            bool(corp.get("dovada_export")))
            val = Decimal(str(corp["valoare"]))
            if val <= 0:
                raise ValueError("valoare invalidă")
            # [R54] confruntarea cu planul firmei stă ÎN try: refuzul e un mesaj pentru om
            # (422), nu o defecțiune (500). Era după `except`, deci ar fi ieșit 500.
            cont_venit = _cv.cere_cont(conn, schema,
                                       _cv.cere_cont(conn, schema, corp.get("cont_venit"), "cont_venit", "707"),
                                       "cont_venit")
        except (ValueError, KeyError) as e:
            raise HTTPException(422, _mesaj_intrare(e))
        descr = (corp.get("descriere") or "Export") + f" ({corp['tara_client']}) - " + ment
        with conn.cursor() as cur:
            cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status)
                            VALUES (%s,%s,'facturi','ciorna') RETURNING id""",
                        (corp["data"], descr[:200]))
            iid = cur.fetchone()[0]
            cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                            (inregistrare_id, cont_debit, cont_credit, suma)
                            VALUES (%s,'4111',%s,%s)""", (iid, cont_venit, val))
        conn.commit()
    return {"inregistrare_id": iid, "mentiune": ment}


@app.get("/tenants/{tenant_id}/intrastat-praguri")
def intrastat_praguri(tenant_id: int, an: int, ctx=Depends(cere_cabinet)):
    """Monitor praguri Intrastat (Ordin INS 1604/2025, 1.000.000 lei/flux):
    introduceri = facturi primite de la parteneri UE; expedieri = facturi emise
    catre parteneri UE. Cumulat pe an, status + luna depasirii per flux."""
    from core import intrastat as _is
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        intro, exped = {}, {}
        with conn.cursor() as cur:
            cur.execute(f"""SELECT directie, tert_cui,
                                   EXTRACT(MONTH FROM data_emitere)::int AS luna,
                                   COALESCE(total,0) - COALESCE(tva,0) AS baza
                            FROM {schema}.facturi
                            WHERE EXTRACT(YEAR FROM data_emitere) = %s""", (an,))
            for directie, cui, luna, baza in cur.fetchall():
                if not _is.e_partener_ue(cui):
                    continue
                tinta = intro if directie == "primita" else exped
                tinta[luna] = tinta.get(luna, 0) + float(baza or 0)
    ri = _is.analiza_flux(intro)
    re_ = _is.analiza_flux(exped)
    def fmt(r):
        return {"cumulat": str(r["cumulat"]), "status": r["status"],
                "luna_depasirii": r["luna_depasirii"], "procent": str(r["procent"]),
                "prag": str(r["prag"])}
    # nivel agregat pt constatare (severitatea vine din motor, cf. intrastat.NIVEL_STATUS): AVERTISMENT
    # daca vreun flux e atentie/depasit, altfel None. Randarea deriva culoarea prin stare_din_nivel.
    nivel = ri.get("nivel") or re_.get("nivel")
    return {"an": an, "introduceri": fmt(ri), "expedieri": fmt(re_), "nivel": nivel,
            "nota": "obligatia de declarare la INS (intrastat.ro) incepe cu luna "
                    "depasirii pragului, separat pe flux (Ordin INS 1604/2025)"}


@app.post("/tenants/{tenant_id}/nota-tva-incasare")
def nota_tva_incasare(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, sens incasare|plata, suma_incasata, cota?, descriere?}.
    incasare: 4428=4427 devine exigibil TVA colectat (suta marita);
    plata: 4426=4428 devine deductibil TVA achitat furnizorului. Nota ciorna."""
    from core import tva_incasare as _ti
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        _cere_luna_deschisa(conn, schema, corp.get("data"))
        sens = corp.get("sens")
        if sens not in ("incasare", "plata"):
            raise HTTPException(422, "sens invalid (incasare/plata)")
        try:
            tva = _ti.tva_din_incasare(corp["suma_incasata"], _common.cota_ceruta(corp))
        except (ValueError, KeyError) as e:
            raise HTTPException(422, _mesaj_intrare(e))
        debit, credit = ("4428", "4427") if sens == "incasare" else ("4426", "4428")
        desc = corp.get("descriere") or (
            "TVA la incasare - exigibilitate la " + ("incasare (art. 282)" if sens == "incasare" else "plata furnizor"))
        with conn.cursor() as cur:
            cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status)
                            VALUES (%s,%s,'facturi','ciorna') RETURNING id""", (corp["data"], desc[:200]))
            iid = cur.fetchone()[0]
            cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                            (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,%s,%s,%s)""",
                        (iid, debit, credit, tva))
        conn.commit()
    return {"inregistrare_id": iid, "tva_exigibil": str(tva), "nota": f"{debit}={credit}"}

@app.post("/tenants/{tenant_id}/decontare-valuta")
def decontare_valuta(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """Incasare creanta / plata datorie in valuta cu diferenta de curs 665/765.
    corp: {data, valoare_valuta, moneda, curs_evidenta, tip creanta|datorie,
    cont_tert, cont_banca?, descriere?}. Cursul decontarii = BNR la data (auto)."""
    from datetime import date as _date
    from core import diferente_curs as _dc
    from core import curs_bnr as _cb
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        _cere_luna_deschisa(conn, schema, corp.get("data"))
        try:
            data = _date.fromisoformat(corp["data"])
            curs_dec, _dcurs, _sursa = _cb.curs_pentru(conn, corp.get("moneda", "EUR"), data)
            r = _dc.nota_decontare(corp["valoare_valuta"], corp["curs_evidenta"],
                                   curs_dec, corp["tip"],
                                    _cv.cere_cont(conn, schema, corp.get("cont_tert"), "cont_tert"),
                                   _cv.cere_cont(conn, schema, corp.get("cont_banca"), "cont_banca", "5124"))
        except (ValueError, KeyError) as e:
            raise HTTPException(422, _mesaj_intrare(e))
        d = r["diferenta"]
        descr = (corp.get("descriere") or "Decontare valuta") +                 f" {corp['valoare_valuta']} {corp.get('moneda','EUR')} curs {curs_dec}" +                 (f", dif. {d['sens']} {bani(d['diferenta'], 'lei')} ({d['cont']})" if d["cont"] else "")
        with conn.cursor() as cur:
            cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status)
                            VALUES (%s,%s,'banca','ciorna') RETURNING id""",
                        (corp["data"], descr[:200]))
            iid = cur.fetchone()[0]
            for dd, cc, ss in r["linii"]:
                cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                                (inregistrare_id, cont_debit, cont_credit, suma)
                                VALUES (%s,%s,%s,%s)""", (iid, dd, cc, ss))
        conn.commit()
    return {"inregistrare_id": iid, "curs_decontare": str(curs_dec),
            "lei_evidenta": str(r["lei_evidenta"]),
            "diferenta": {"suma": str(d["diferenta"]), "cont": d["cont"],
                          "sens": d["sens"]}}


@app.post("/tenants/{tenant_id}/reevaluare-valuta")
def reevaluare_valuta(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """Reevaluare lunara solduri valuta (OMFP 1802 pct. 316), curs BNR auto.
    corp: {data (ultima zi luna), solduri: [{cont, valoare_valuta, moneda,
    curs_evidenta, tip creanta|datorie|disponibil}]}. O nota cu toate liniile."""
    from datetime import date as _date
    from core import diferente_curs as _dc
    from core import curs_bnr as _cb
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        _cere_luna_deschisa(conn, schema, corp.get("data"))
        try:
            data = _date.fromisoformat(corp["data"])
            solduri = corp["solduri"]
            if not solduri:
                raise ValueError("solduri gol")
        except (ValueError, KeyError) as e:
            raise HTTPException(422, _mesaj_intrare(e))
        linii, detalii = [], []
        try:
            for s in solduri:
                curs_bnr, _dcurs, _sursa = _cb.curs_pentru(conn, s.get("moneda", "EUR"), data)
                r = _dc.reevaluare_sold(s["valoare_valuta"], s["curs_evidenta"],
                                        curs_bnr, s["tip"], str(s["cont"]))
                if r:
                    linii.append(r["linie"])
                    detalii.append({"cont": s["cont"], "curs_bnr": str(curs_bnr),
                                    "diferenta": str(r["diferenta"]["diferenta"]),
                                    "cont_rezultat": r["diferenta"]["cont"]})
        except (ValueError, KeyError) as e:
            raise HTTPException(422, _mesaj_intrare(e))
        if not linii:
            _d = _date.fromisoformat(str(corp["data"])[:10])
            return dict(_af.afirmatie(
                "fapt", "reevaluare valută", "nicio diferență de reevaluat",
                an=_d.year, luna=_d.month,
                temei_completitudine="soldurile în valută ale firmei, la cursul BNR din data cerută"),
                inregistrare_id=None, detalii=[], mesaj="nicio diferență de reevaluat")
        with conn.cursor() as cur:
            cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status)
                            VALUES (%s,%s,'banca','ciorna') RETURNING id""",
                        (corp["data"], f"Reevaluare solduri valuta la {corp['data']} "
                                       "(OMFP 1802 pct. 316, curs BNR)"))
            iid = cur.fetchone()[0]
            for dd, cc, ss in linii:
                cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                                (inregistrare_id, cont_debit, cont_credit, suma)
                                VALUES (%s,%s,%s,%s)""", (iid, dd, cc, ss))
        conn.commit()
    return {"inregistrare_id": iid, "detalii": detalii}


@app.post("/tenants/{tenant_id}/nota-leasing")
def nota_leasing(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, tip primire|rata|reziduala|operational, descriere?, cota?,
    + campuri pe tip: primire{valoare_capital, dobanda_totala, cont_imobilizare?};
    rata{capital, dobanda?, comision?}; reziduala{valoare_reziduala};
    operational{chirie, cont_cheltuiala?}}. Nota ciorna."""
    from core import leasing as _ls
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        _cere_luna_deschisa(conn, schema, corp.get("data"))
        tip = corp.get("tip")
        try:
            if tip == "primire":
                r = _ls.nota_primire_financiar(corp["valoare_capital"],
                                               corp.get("dobanda_totala", 0),
                                               _cv.cere_cont(conn, schema, corp.get("cont_imobilizare"), "cont_imobilizare", "2133"))
                d0 = "Primire bun leasing financiar (2133=167 + D8051 dobanda)"
            elif tip == "rata":
                r = _ls.nota_rata_financiar(corp["capital"], corp.get("dobanda", 0),
                                            corp.get("comision", 0), _common.cota_ceruta(corp))
                d0 = "Rata leasing financiar (167/666/628=404 + C8051)"
            elif tip == "reziduala":
                r = _ls.nota_reziduala(corp["valoare_reziduala"], _common.cota_ceruta(corp))
                d0 = "Valoare reziduala leasing (167=404, inchide 167)"
            elif tip == "operational":
                r = _ls.nota_rata_operational(corp["chirie"], _common.cota_ceruta(corp),
                                              _cv.cere_cont(conn, schema, corp.get("cont_cheltuiala"), "cont_cheltuiala", "612"))
                d0 = "Rata leasing operational (612=401)"
            else:
                raise ValueError(nomenclator_cerut("tip", "primire|rata|reziduala|operational"))
        except (ValueError, KeyError) as e:
            raise HTTPException(422, _mesaj_intrare(e))
        descr = (corp.get("descriere") or d0) + " - OMFP 1802 pct. 212-217"
        with conn.cursor() as cur:
            cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status)
                            VALUES (%s,%s,'facturi','ciorna') RETURNING id""",
                        (corp["data"], descr[:200]))
            iid = cur.fetchone()[0]
            for dd, cc, ss in r["linii"]:
                cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                                (inregistrare_id, cont_debit, cont_credit, suma)
                                VALUES (%s,%s,%s,%s)""", (iid, dd, cc, ss))
        conn.commit()
    return {"inregistrare_id": iid, "linii": [[a, b, str(c)] for a, b, c in r["linii"]]}


@app.post("/tenants/{tenant_id}/nota-credit")
def nota_credit(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, operatie primire|dobanda|plata|restanta|garantie, tip lung|scurt,
    descriere?, + pe operatie: primire{suma}; dobanda{dobanda}; plata{rata?, dobanda?,
    comision?, dobanda_angajata?}; restanta{suma}; garantie{suma, fel primita|acordata,
    actiune inregistrare|eliberare}}. Nota ciorna."""
    from core import credite as _cr
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        _cere_luna_deschisa(conn, schema, corp.get("data"))
        op = corp.get("operatie")
        tip = corp.get("tip", "lung")
        try:
            if op == "primire":
                r = _cr.nota_primire(corp["suma"], tip)
                d0 = f"Primire credit bancar termen {tip}"
            elif op == "dobanda":
                r = _cr.nota_dobanda_angajata(corp["dobanda"], tip)
                d0 = "Dobanda angajata credit (666=168x/519x)"
            elif op == "plata":
                r = _cr.nota_plata(corp.get("rata", 0), corp.get("dobanda", 0),
                                   corp.get("comision", 0), tip,
                                   dobanda_angajata=corp.get("dobanda_angajata", True))
                d0 = "Plata rata/dobanda/comision credit"
            elif op == "restanta":
                r = _cr.nota_restanta(corp["suma"], tip)
                d0 = "Credit nerambursat la scadenta"
            elif op == "garantie":
                r = _cr.nota_garantie(corp["suma"], corp.get("fel", "primita"),
                                      corp.get("actiune", "inregistrare"))
                d0 = f"Garantie {corp.get('fel','primita')} extracontabil 801x"
            else:
                raise ValueError(nomenclator_cerut("operatie", "primire|dobanda|plata|restanta|garantie"))
        except (ValueError, KeyError) as e:
            raise HTTPException(422, _mesaj_intrare(e))
        descr = (corp.get("descriere") or d0) + " - OMFP 1802"
        with conn.cursor() as cur:
            cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status)
                            VALUES (%s,%s,'banca','ciorna') RETURNING id""",
                        (corp["data"], descr[:200]))
            iid = cur.fetchone()[0]
            for dd, cc, ss in r["linii"]:
                cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                                (inregistrare_id, cont_debit, cont_credit, suma)
                                VALUES (%s,%s,%s,%s)""", (iid, dd, cc, ss))
        conn.commit()
    return {"inregistrare_id": iid, "linii": [[a, b, str(c)] for a, b, c in r["linii"]]}


@app.post("/tenants/{tenant_id}/nota-avans")
def nota_avans(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, operatie avans_platit|regularizare_platit|avans_incasat|
    regularizare_incasat, suma (fara TVA), cota?, destinatie? (platit:
    stocuri|servicii|imobilizari|imobilizari_necorporale), descriere?}."""
    from core import avansuri as _av
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        _cere_luna_deschisa(conn, schema, corp.get("data"))
        op = corp.get("operatie")
        dest = corp.get("destinatie", "stocuri")
        _OPERATII_AVANS = ("avans_platit", "regularizare_platit", "avans_incasat",
                           "regularizare_incasat")
        try:
            # [lotul 3] ORDINEA e reparatia: cota se cerea INAINTE de a se uita la operatie, deci
            # cine uita felul operatiunii — sau il scria gresit — afla despre cotă. Felul intai.
            if op not in _OPERATII_AVANS:
                raise ValueError(nomenclator_cerut("operatie", _OPERATII_AVANS))
            cota = _common.cota_ceruta(corp)
            if op == "avans_platit":
                r = _av.nota_avans_platit(corp["suma"], cota, dest)
                d0 = f"Factura avans furnizor ({r['cont_avans']}+4426=401)"
            elif op == "regularizare_platit":
                r = _av.nota_regularizare_avans_platit(corp["suma"], cota, dest)
                d0 = "Regularizare avans furnizor la factura finala"
            elif op == "avans_incasat":
                r = _av.nota_avans_incasat(corp["suma"], cota)
                d0 = "Factura avans client (4111=419+4427)"
            elif op == "regularizare_incasat":
                r = _av.nota_regularizare_avans_incasat(corp["suma"], cota)
                d0 = "Regularizare avans client la factura finala"
            else:                       # nu se poate ajunge aici: `op` e verificat mai sus
                raise ValueError(nomenclator_cerut("operatie", _OPERATII_AVANS))
        except (ValueError, KeyError) as e:
            raise HTTPException(422, _mesaj_intrare(e))
        descr = (corp.get("descriere") or d0) + " - art. 282(2)b CF"
        with conn.cursor() as cur:
            cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status)
                            VALUES (%s,%s,'facturi','ciorna') RETURNING id""",
                        (corp["data"], descr[:200]))
            iid = cur.fetchone()[0]
            for dd, cc, ss in r["linii"]:
                cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                                (inregistrare_id, cont_debit, cont_credit, suma)
                                VALUES (%s,%s,%s,%s)""", (iid, dd, cc, ss))
        conn.commit()
    return {"inregistrare_id": iid, "linii": [[a, b, str(c)] for a, b, c in r["linii"]]}


@app.post("/tenants/{tenant_id}/achizitie-necorporala")
def achizitie_necorporala(tenant_id: int, corp: dict = Body(...),
                          ctx=Depends(cere_rol("admin_firma"))):
    """corp: {data, denumire, valoare (fara TVA), tip software|licenta|brevet|
    dezvoltare|constituire, dnf_luni?, cota?, cod?}.
    Art. 28(9): software = 36 luni (fix); licenta/brevet = durata contract (dnf_luni
    obligatoriu); constituire = max 60 luni. Nota ciorna 20x+4426=404 + inscriere
    in mijloace_fixe (amortizare lunara preluata de mecanismul existent)."""
    from decimal import Decimal
    TIPURI = {"software":    ("208", "2808", 36),
              "licenta":     ("205", "2805", None),
              "brevet":      ("205", "2805", None),
              "dezvoltare":  ("203", "2803", None),
              "constituire": ("201", "2801", 60)}
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        _cere_luna_deschisa(conn, schema, corp.get("data"))
        tip = corp.get("tip")
        if tip not in TIPURI:
            raise HTTPException(422, nomenclator_cerut("tip", TIPURI))
        cont_imo, cont_am, dnf_regula = TIPURI[tip]
        dnf = corp.get("dnf_luni")
        if tip == "software":
            dnf = 36  # art. 28(9): programe informatice = 3 ani, fix
        elif tip == "constituire":
            dnf = min(int(dnf or 60), 60)  # art. 28(11): max 5 ani
        elif not dnf:
            raise HTTPException(422, f"Durata normală de funcționare (luni) obligatorie pentru {tip} "
                                     "(durata contractului/de utilizare, art. 28(9))")
        from core import facturi_api as _fa
        try:
            val = Decimal(str(corp["valoare"]))
            if val <= 0:
                raise ValueError("valoare invalidă")
            cota = _common.cota_ceruta(corp)
            tva = (val * Decimal(str(cota)) / 100).quantize(Decimal("0.01"))
            furnizor_cui = str(corp.get("furnizor_cui") or "").strip().upper().replace(" ", "")
            if not furnizor_cui:
                raise ValueError("CUI furnizor obligatoriu (achizitia necorporala e factura de la furnizor)")
            numar = str(corp.get("numar") or "").strip()
            if not numar:
                raise ValueError("numar factura furnizor obligatoriu")
            furnizor_nume = str(corp.get("furnizor_nume") or "").strip()
        except (ValueError, KeyError) as e:
            raise HTTPException(422, str(e) or "valoare invalidă")
        with conn.cursor() as cur:
            cur.execute(f"""INSERT INTO {schema}.mijloace_fixe
                            (cod, denumire, cont_imobilizare, cont_amortizare, valoare,
                             rezidual, dnf_luni, data_pif, metoda, activ)
                            VALUES (%s,%s,%s,%s,%s,0,%s,%s,'liniara',true) RETURNING id""",
                        (corp.get("cod") or f"NEC-{tip[:3].upper()}",
                         corp["denumire"][:200], cont_imo, cont_am, val,
                         int(dnf), corp["data"]))
            mfid = cur.fetchone()[0]
            cur.execute(f"SET LOCAL search_path TO {schema}")   # creeaza_factura foloseste INSERT necalificat
            # rand FACTURA (achizitie normala de la furnizor RO cu CUI) -> D394 tip A. MF (mijloace_fixe) ramane
            # separat: factura = documentul de achizitie; imobilizarea = activul amortizabil (amortizare/D406).
            from core import anaf_api as _anaf
            _tert_pl = _anaf.platitor_tva_freeze(furnizor_cui, fallback=True)   # TVA deductibila -> furnizor platitor
            fres = _fa.creeaza_factura(conn, numar=numar, data_emitere=corp["data"], directie="primita",
                                       linii=[{"descriere": corp["denumire"][:200], "cantitate": 1,
                                               "pret_unitar": str(val), "cota_tva": cota}],
                                       tert_nume=furnizor_nume or None, tert_cui=furnizor_cui, status="importata",
                                       tert_platitor_tva=_tert_pl)
            fid = fres["factura_id"]
            cur.execute(f"""INSERT INTO {schema}.inregistrari (data, factura_id, descriere, sursa, status)
                            VALUES (%s,%s,%s,'facturi','ciorna') RETURNING id""",
                        (corp["data"], fid, f"Achizitie necorporala {tip}: {corp['denumire']}"
                                       f" (amortizare {dnf} luni, art. 28(9) CF)"[:200]))
            iid = cur.fetchone()[0]
            for dd, cc, ss in [(cont_imo, "404", val), ("4426", "404", tva)]:
                cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                                (inregistrare_id, cont_debit, cont_credit, suma)
                                VALUES (%s,%s,%s,%s)""", (iid, dd, cc, ss))
        conn.commit()
    return {"inregistrare_id": iid, "factura_id": fid, "mijloc_fix_id": mfid, "dnf_luni": int(dnf),
            "conturi": [cont_imo, cont_am]}


@app.post("/tenants/{tenant_id}/reevaluare-imobilizare")
def reevaluare_imobilizare(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, operatie reevaluare|surplus, + reevaluare{mijloc_fix_id,
    valoare_justa, sold_105_activ?, pierdere_655_anterioara?} | surplus{suma}}.
    Reevaluarea citeste valoarea+amortizarea cumulata din mijloace_fixe si
    actualizeaza valoarea/dnf ramane manual (raport evaluator)."""
    from decimal import Decimal
    from datetime import date as _date
    from core import reevaluare as _rv
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        _cere_luna_deschisa(conn, schema, corp.get("data"))
        op = corp.get("operatie", "reevaluare")
        try:
            if op == "surplus":
                r = _rv.nota_realizare_surplus(corp["suma"])
                descr = "Transfer surplus reevaluare realizat (105=1175, pct.109-110)"
                extra = {}
            else:
                with conn.cursor() as cur:
                    cur.execute(f"""SELECT denumire, cont_imobilizare, cont_amortizare,
                                           valoare, COALESCE(rezidual,0), dnf_luni, data_pif, metoda
                                    FROM {schema}.mijloace_fixe WHERE id=%s AND activ=true""",
                                (corp["mijloc_fix_id"],))
                    mf = cur.fetchone()
                if not mf:
                    raise HTTPException(404, "mijloc fix inexistent/inactiv")
                den, ci, ca, val, rez, dnf, pif, met = mf
                ref = _date.fromisoformat(corp["data"])
                from core import d406_active as _d406
                mf_d = {"cod": den, "denumire": den, "cont_imobilizare": ci, "cont_amortizare": ca,
                        "valoare": val, "rezidual": rez, "dnf_luni": dnf, "data_pif": pif, "metoda": met}
                amortizare = _d406.amortizat_la_data(mf_d, ref)["amortizat"]   # metoda reala, nu liniar
                r = _rv.nota_reevaluare(val, amortizare, corp["valoare_justa"], ci, ca,
                                        corp.get("sold_105_activ", 0),
                                        corp.get("pierdere_655_anterioara", 0))
                descr = f"Reevaluare {den}: neta {r['valoare_neta']} -> justa "                         f"{corp['valoare_justa']} (OMFP 1802 pct.111-116)"
                extra = {"valoare_neta": str(r["valoare_neta"]),
                         "diferenta": str(r["diferenta"]), "amortizare_eliminata": str(amortizare)}
                if not r["linii"]:
                    _d = _date.fromisoformat(str(corp["data"])[:10]) if corp.get("data") else None
                    return dict(_af.afirmatie(
                        "fapt", "reevaluare imobilizare", "nicio diferență de reevaluat",
                        unde=_Unde("mijloc_fix", corp.get("mijloc_fix_id") or den),
                        temei_completitudine="valoarea netă contabilă vs valoarea justă declarată "
                                             "(OMFP 1802 pct.111-116)"),
                        inregistrare_id=None, mesaj="nicio diferență de reevaluat",
                        data=str(_d) if _d else None, **extra)
        except (ValueError, KeyError) as e:
            raise HTTPException(422, _mesaj_intrare(e))
        with conn.cursor() as cur:
            cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status)
                            VALUES (%s,%s,'facturi','ciorna') RETURNING id""",
                        (corp["data"], descr[:200]))
            iid = cur.fetchone()[0]
            for dd, cc, ss in r["linii"]:
                cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                                (inregistrare_id, cont_debit, cont_credit, suma)
                                VALUES (%s,%s,%s,%s)""", (iid, dd, cc, ss))
        conn.commit()
    return {"inregistrare_id": iid,
            "linii": [[a, b, str(c)] for a, b, c in r["linii"]], **extra}


@app.post("/tenants/{tenant_id}/nota-provizion")
def nota_provizion_ep(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, fel creanta|provizion|stoc, actiune constituire|reluare, suma,
    descriere?, + creanta{zile_depasire?, garantata?, afiliata?, faliment?} |
    provizion{tip litigii|garantii|dezafectare|restructurare|impozite|altele} |
    stoc{cont_ajustare?}}. Raspunsul include deductibilitatea fiscala."""
    from core import provizioane as _pv
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        _cere_luna_deschisa(conn, schema, corp.get("data"))
        fel = corp.get("fel")
        act = corp.get("actiune", "constituire")
        info = {}
        try:
            if fel == "creanta":
                r = _pv.nota_ajustare_creanta(corp["suma"], act)
                pct, temei = _pv.deductibilitate_creanta(
                    corp.get("zile_depasire", 0), bool(corp.get("garantata")),
                    bool(corp.get("afiliata")), bool(corp.get("faliment")))
                info = {"deductibil_procent": pct, "temei": temei}
                d0 = f"Ajustare creanta ({act}) - deductibil {pct}%"
            elif fel == "provizion":
                r = _pv.nota_provizion(corp["suma"], corp.get("tip", "garantii"), act)
                info = {"deductibil": r["deductibil"]}
                d0 = f"Provizion {corp.get('tip','garantii')} ({act})" +                      ("" if r["deductibil"] else " - NEDEDUCTIBIL fiscal")
            elif fel == "stoc":
                r = _pv.nota_ajustare_stoc(corp["suma"], _cv.cere_cont(conn, schema, corp.get("cont_ajustare"), "cont_ajustare", "397"), act)
                info = {"deductibil": False}
                d0 = f"Ajustare depreciere stocuri ({act}) - nedeductibil fiscal"
            else:
                raise ValueError(nomenclator_cerut("fel", "creanta|provizion|stoc"))
        except (ValueError, KeyError) as e:
            raise HTTPException(422, _mesaj_intrare(e))
        descr = (corp.get("descriere") or d0) + " - art. 26 CF / OMFP 1802"
        with conn.cursor() as cur:
            cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status)
                            VALUES (%s,%s,'facturi','ciorna') RETURNING id""",
                        (corp["data"], descr[:200]))
            iid = cur.fetchone()[0]
            for dd, cc, ss in r["linii"]:
                cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                                (inregistrare_id, cont_debit, cont_credit, suma)
                                VALUES (%s,%s,%s,%s)""", (iid, dd, cc, ss))
        conn.commit()
    return {"inregistrare_id": iid,
            "linii": [[a, b, str(c)] for a, b, c in r["linii"]], **info}


@app.post("/tenants/{tenant_id}/nota-productie")
def nota_productie(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, operatie obtinere|pic|vanzare, descriere?, +
    obtinere{cost_standard, cost_efectiv?}; pic{suma, moment constatare|reluare};
    vanzare{pret_vanzare, cost_standard_iesit, cota?, coef_348?}}."""
    from core import productie as _pr
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        _cere_luna_deschisa(conn, schema, corp.get("data"))
        op = corp.get("operatie")
        try:
            if op == "obtinere":
                r = _pr.nota_obtinere(corp["cost_standard"], corp.get("cost_efectiv"))
                d0 = "Obtinere produse finite 345=711 (cost standard)"
            elif op == "pic":
                r = _pr.nota_productie_in_curs(corp["suma"], corp.get("moment", "constatare"))
                d0 = f"Productie in curs ({corp.get('moment','constatare')}) 331/711"
            elif op == "vanzare":
                r = _pr.nota_vanzare(corp["pret_vanzare"], corp["cost_standard_iesit"],
                                     _common.cota_ceruta(corp), corp.get("coef_348"))
                d0 = "Vanzare produse finite 4111=701+4427, descarcare 711=345"
            else:
                raise ValueError(nomenclator_cerut("operatie", "obtinere|pic|vanzare"))
        except (ValueError, KeyError) as e:
            raise HTTPException(422, _mesaj_intrare(e))
        descr = (corp.get("descriere") or d0) + " - OMFP 1802"
        with conn.cursor() as cur:
            cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status)
                            VALUES (%s,%s,'facturi','ciorna') RETURNING id""",
                        (corp["data"], descr[:200]))
            iid = cur.fetchone()[0]
            for dd, cc, ss in r["linii"]:
                cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                                (inregistrare_id, cont_debit, cont_credit, suma)
                                VALUES (%s,%s,%s,%s)""", (iid, dd, cc, ss))
        conn.commit()
    return {"inregistrare_id": iid, "linii": [[a, b, str(c)] for a, b, c in r["linii"]]}


@app.post("/tenants/{tenant_id}/nota-obiect-inventar")
def nota_obiect_inventar(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, operatie achizitie|dare_folosinta|scoatere, valoare, cota?,
    descriere?}. Achizitia verifica pragul MF (5000 din 25.02.2026, OUG 8/2026)
    si refuza daca valoarea e peste prag (foloseste fluxul de mijloace fixe)."""
    from datetime import date as _date
    from core import obiecte_inventar as _oi
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        _cere_luna_deschisa(conn, schema, corp.get("data"))
        op = corp.get("operatie")
        try:
            if op == "achizitie":
                ref = _date.fromisoformat(corp["data"])
                if not _oi.e_obiect_inventar(corp["valoare"], ref,
                                             bool(corp.get("durata_sub_1_an"))):
                    raise ValueError(f"valoarea depaseste pragul MF de "
                                     f"{bani(_oi.prag_mf(ref), 'lei')} (OUG 8/2026) - "
                                     "inregistreaza ca mijloc fix")
                r = _oi.nota_achizitie(corp["valoare"], _common.cota_ceruta(corp))
                d0 = "Achizitie obiect de inventar 303+4426=401"
            elif op == "dare_folosinta":
                r = _oi.nota_dare_folosinta(corp["valoare"])
                d0 = "Dare in folosinta OI: 603=303 + D8035"
            elif op == "scoatere":
                r = _oi.nota_scoatere_uz(corp["valoare"])
                d0 = "Scoatere din uz OI: C8035 (proces-verbal)"
            else:
                raise ValueError(nomenclator_cerut("operatie", "achizitie|dare_folosinta|scoatere"))
        except (ValueError, KeyError) as e:
            raise HTTPException(422, _mesaj_intrare(e))
        descr = (corp.get("descriere") or d0) + " - OMFP 1802 / OUG 8/2026"
        with conn.cursor() as cur:
            cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status)
                            VALUES (%s,%s,'facturi','ciorna') RETURNING id""",
                        (corp["data"], descr[:200]))
            iid = cur.fetchone()[0]
            for dd, cc, ss in r["linii"]:
                cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                                (inregistrare_id, cont_debit, cont_credit, suma)
                                VALUES (%s,%s,%s,%s)""", (iid, dd, cc, ss))
        conn.commit()
    return {"inregistrare_id": iid, "linii": [[a, b, str(c)] for a, b, c in r["linii"]]}


@app.post("/tenants/{tenant_id}/nota-asociati")
def nota_asociati(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, operatie dividend|regularizare|imprumut, descriere?, +
    dividend{brut, interimar?, cu_plata?}; regularizare{total_interimar,
    dividend_anual}; imprumut{suma, fel primire|restituire, dobanda?}}."""
    from datetime import date as _date
    from core import decontari_asociati as _da
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        _cere_luna_deschisa(conn, schema, corp.get("data"))
        op = corp.get("operatie")
        info = {}
        try:
            if op == "dividend":
                r = _da.nota_dividend(corp["brut"], _date.fromisoformat(corp["data"]),
                                      bool(corp.get("interimar")),
                                      corp.get("cu_plata", True))
                info = {"impozit": str(r["impozit"]), "net": str(r["net"]),
                        "cota": r["cota"]}
                d0 = f"Dividende {'interimare' if corp.get('interimar') else 'anuale'} "                      f"brut {corp['brut']}, impozit {r['cota']}%"
            elif op == "regularizare":
                r = _da.nota_regularizare_interimar(corp["total_interimar"],
                                                    corp["dividend_anual"])
                info = {"exces_de_restituit": str(r["exces_de_restituit"])}
                d0 = "Regularizare dividende interimare (457=463, OMFP 3067/2018)"
            elif op == "imprumut":
                r = _da.nota_imprumut_asociat(corp.get("suma", 0),
                                              corp.get("fel", "primire"),
                                              corp.get("dobanda", 0))
                d0 = f"Imprumut asociat 4551 ({corp.get('fel','primire')})"
            else:
                raise ValueError(nomenclator_cerut("operatie", "dividend|regularizare|imprumut"))
        except (ValueError, KeyError) as e:
            raise HTTPException(422, _mesaj_intrare(e))
        descr = (corp.get("descriere") or d0)
        with conn.cursor() as cur:
            cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status)
                            VALUES (%s,%s,'facturi','ciorna') RETURNING id""",
                        (corp["data"], descr[:200]))
            iid = cur.fetchone()[0]
            for dd, cc, ss in r["linii"]:
                cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                                (inregistrare_id, cont_debit, cont_credit, suma)
                                VALUES (%s,%s,%s,%s)""", (iid, dd, cc, ss))
        conn.commit()
    return {"inregistrare_id": iid,
            "linii": [[a, b, str(c)] for a, b, c in r["linii"]], **info}


@app.post("/tenants/{tenant_id}/nota-sponsorizare")
def nota_sponsorizare_ep(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, suma, mod contract|plata, descriere?, + optional pentru calcul
    credit: cifra_afaceri, impozit_profit, tip_impozit profit|micro,
    beneficiar_in_registru}. Nota 6582 + info credit fiscal/D177."""
    from core import sponsorizari as _sp
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        _cere_luna_deschisa(conn, schema, corp.get("data"))
        try:
            r = _sp.nota_sponsorizare(corp["suma"], corp.get("mod", "contract"))
            info = {}
            if corp.get("cifra_afaceri") is not None:
                c = _sp.credit_sponsorizare(corp["cifra_afaceri"],
                                            corp.get("impozit_profit", 0),
                                            corp["suma"],
                                            corp.get("tip_impozit", "profit"),
                                            corp.get("beneficiar_in_registru", True))
                info = {k: (str(v) if not isinstance(v, str) else v)
                        for k, v in c.items()}
        except (ValueError, KeyError) as e:
            raise HTTPException(422, _mesaj_intrare(e))
        descr = (corp.get("descriere") or "Sponsorizare (6582, nedeductibil, "
                 "credit fiscal art. 25(4)i)")
        with conn.cursor() as cur:
            cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status)
                            VALUES (%s,%s,'facturi','ciorna') RETURNING id""",
                        (corp["data"], descr[:200]))
            iid = cur.fetchone()[0]
            for dd, cc, ss in r["linii"]:
                cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                                (inregistrare_id, cont_debit, cont_credit, suma)
                                VALUES (%s,%s,%s,%s)""", (iid, dd, cc, ss))
        conn.commit()
    return {"inregistrare_id": iid,
            "linii": [[a, b, str(c)] for a, b, c in r["linii"]], "credit_fiscal": info}


@app.post("/tenants/{tenant_id}/nota-subventie")
def nota_subventie(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, fel exploatare|investitii|reluare, descriere?, +
    exploatare/investitii{suma, moment drept|incasare};
    reluare{valoare_activ, subventie, amortizare_lunara}}."""
    from core import subventii as _sb
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        _cere_luna_deschisa(conn, schema, corp.get("data"))
        fel = corp.get("fel")
        info = {}
        try:
            if fel == "exploatare":
                r = _sb.nota_subventie_exploatare(corp["suma"], corp.get("moment", "drept"),
                                                  _cv.cere_cont(conn, schema, corp.get("cont_venit"), "cont_venit", "741"))
                d0 = f"Subventie exploatare ({corp.get('moment','drept')})"
            elif fel == "investitii":
                r = _sb.nota_subventie_investitii(corp["suma"], corp.get("moment", "drept"))
                d0 = f"Subventie investitii 4751 ({corp.get('moment','drept')})"
            elif fel == "reluare":
                r = _sb.reluare_lunara_investitii(corp["valoare_activ"], corp["subventie"],
                                                  corp["amortizare_lunara"])
                info = {"procent_subventionat": r["procent_subventionat"]}
                d0 = "Reluare subventie investitii 4751=7584 (proportional cu amortizarea)"
            else:
                raise ValueError(nomenclator_cerut("fel", "exploatare|investitii|reluare"))
        except (ValueError, KeyError) as e:
            raise HTTPException(422, _mesaj_intrare(e))
        descr = (corp.get("descriere") or d0) + " - OMFP 1802 pct. 392-402"
        with conn.cursor() as cur:
            cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status)
                            VALUES (%s,%s,'facturi','ciorna') RETURNING id""",
                        (corp["data"], descr[:200]))
            iid = cur.fetchone()[0]
            for dd, cc, ss in r["linii"]:
                cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                                (inregistrare_id, cont_debit, cont_credit, suma)
                                VALUES (%s,%s,%s,%s)""", (iid, dd, cc, ss))
        conn.commit()
    return {"inregistrare_id": iid,
            "linii": [[a, b, str(c)] for a, b, c in r["linii"]], **info}


@app.post("/tenants/{tenant_id}/nota-chirie")
def nota_chirie(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, fel comodat|chirie_platita|chirie_incasata|refacturare,
    descriere?, cota?, + comodat{valoare, moment primire|restituire};
    chirie_platita{chirie, proprietar pj|pf}; chirie_incasata{chirie};
    refacturare{total_factura, parte_refacturata}}.
    Refacturarea creeaza DOUA note (primire+emitere)."""
    from core import comodat_chirii as _cc
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        _cere_luna_deschisa(conn, schema, corp.get("data"))
        fel = corp.get("fel")
        note = []  # [(descriere, linii)]
        info = {}
        try:
            if fel == "comodat":
                r = _cc.nota_comodat(corp["valoare"], corp.get("moment", "primire"))
                note.append((f"Comodat 8038 ({corp.get('moment','primire')}) - art. 2146 CC",
                             r["linii"]))
            elif fel == "chirie_platita":
                r = _cc.nota_chirie_platita(corp["chirie"], _common.cota_ceruta(corp),
                                            corp.get("proprietar", "pj"))
                info = {"nota": r.get("nota", "")}
                note.append((f"Chirie platita ({corp.get('proprietar','pj')})", r["linii"]))
            elif fel == "chirie_incasata":
                r = _cc.nota_chirie_incasata(corp["chirie"], _common.cota_ceruta(corp))
                note.append(("Chirie incasata 4111=706", r["linii"]))
            elif fel == "refacturare":
                r = _cc.nota_refacturare(corp["total_factura"],
                                         corp["parte_refacturata"], _common.cota_ceruta(corp))
                info = {"tva_refacturat": str(r["tva_refacturat"])}
                if r["primire"]:
                    note.append(("Factura utilitati: parte proprie + de refacturat (art. 271)",
                                 r["primire"]))
                if r["emitere"]:
                    note.append(("Refacturare utilitati 4111=708 (aceeasi cota)",
                                 r["emitere"]))
            else:
                raise ValueError(nomenclator_cerut("fel", "comodat|chirie_platita|chirie_incasata|refacturare"))
        except (ValueError, KeyError) as e:
            raise HTTPException(422, _mesaj_intrare(e))
        ids = []
        with conn.cursor() as cur:
            for d0, linii in note:
                descr = (corp.get("descriere") or d0)
                cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status)
                                VALUES (%s,%s,'facturi','ciorna') RETURNING id""",
                            (corp["data"], descr[:200]))
                iid = cur.fetchone()[0]
                ids.append(iid)
                for dd, cc, ss in linii:
                    cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                                    (inregistrare_id, cont_debit, cont_credit, suma)
                                    VALUES (%s,%s,%s,%s)""", (iid, dd, cc, ss))
        conn.commit()
    return {"inregistrari": ids, **info}


@app.post("/tenants/{tenant_id}/nota-decont-deplasare")
def nota_decont_deplasare(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, fel avans|decont|plafon, descriere?, sursa casa|banca, +
    avans{suma}; decont{avans, diurna?, transport?, cazare?, cota?};
    plafon{diurna_pe_zi, zile, salariu_baza, zile_lucratoare, diurna_bugetara?,
    curs?} - plafon NU creeaza nota, doar calculeaza}."""
    from core import deconturi as _dp
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        _cere_luna_deschisa(conn, schema, corp.get("data"))
        fel = corp.get("fel")
        info = {}
        try:
            if fel == "plafon":
                p = _dp.plafon_diurna(corp["diurna_pe_zi"], corp["zile"],
                                      corp["salariu_baza"], corp["zile_lucratoare"],
                                      corp.get("diurna_bugetara"), corp.get("curs", 1))
                return {k: str(v) for k, v in p.items()}
            if fel == "avans":
                r = _dp.nota_avans(corp["suma"], corp.get("sursa", "casa"))
                d0 = "Avans spre decontare 542"
            elif fel == "decont":
                # cota CERUTA, ca la celelalte 14 rute: `corp.get("cota", 0)` punea tacit 0,
                # adica „scutit", pe un decont care putea avea cazare cu TVA (R26, a doua runda).
                r = _dp.nota_decont(corp.get("avans", 0), corp.get("diurna", 0),
                                    corp.get("transport", 0), corp.get("cazare", 0),
                                    _common.cota_ceruta(corp), corp.get("sursa", "casa"))
                info = {"total_cheltuieli": str(r["total_cheltuieli"]),
                        "diferenta": str(r["diferenta"])}
                d0 = "Decont deplasare 625=542 (ordin de deplasare + justificative)"
            else:
                raise ValueError(nomenclator_cerut("fel", "avans|decont|plafon"))
        except (ValueError, KeyError) as e:
            raise HTTPException(422, _mesaj_intrare(e))
        descr = (corp.get("descriere") or d0) + " - art. 76(2)k CF / HG 714/2018"
        with conn.cursor() as cur:
            cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status)
                            VALUES (%s,%s,'casa','ciorna') RETURNING id""",
                        (corp["data"], descr[:200]))
            iid = cur.fetchone()[0]
            for dd, cc, ss in r["linii"]:
                cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                                (inregistrare_id, cont_debit, cont_credit, suma)
                                VALUES (%s,%s,%s,%s)""", (iid, dd, cc, ss))
        conn.commit()
    return {"inregistrare_id": iid,
            "linii": [[a, b, str(c)] for a, b, c in r["linii"]], **info}


@app.post("/tenants/{tenant_id}/nota-bacsis")
def nota_bacsis(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, fel incasare|distribuire, suma, sursa card|numerar (incasare) /
    banca|casa (distribuire), descriere?}. Legea 376/2022: fara TVA, fara
    CAS/CASS, impozit 10% retinut la distribuire (D100, informativ D205)."""
    from core import bacsis as _bc
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        _cere_luna_deschisa(conn, schema, corp.get("data"))
        fel = corp.get("fel")
        info = {}
        try:
            if fel == "incasare":
                r = _bc.nota_incasare(corp["suma"], corp.get("sursa", "card"))
                d0 = "Bacsis incasat pe bon fiscal (461=462, fara TVA)"
            elif fel == "distribuire":
                r = _bc.nota_distribuire(corp["suma"], corp.get("sursa", "banca"))
                info = {"impozit": str(r["impozit"]), "net": str(r["net"])}
                d0 = "Distribuire bacsis salariati (impozit 10% retinut, 462=446)"
            else:
                raise ValueError(nomenclator_cerut("fel", "incasare|distribuire"))
        except (ValueError, KeyError) as e:
            raise HTTPException(422, _mesaj_intrare(e))
        descr = (corp.get("descriere") or d0) + " - Legea 376/2022"
        with conn.cursor() as cur:
            cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status)
                            VALUES (%s,%s,'casa','ciorna') RETURNING id""",
                        (corp["data"], descr[:200]))
            iid = cur.fetchone()[0]
            for dd, cc, ss in r["linii"]:
                cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                                (inregistrare_id, cont_debit, cont_credit, suma)
                                VALUES (%s,%s,%s,%s)""", (iid, dd, cc, ss))
        conn.commit()
    return {"inregistrare_id": iid,
            "linii": [[a, b, str(c)] for a, b, c in r["linii"]], **info}


@app.post("/tenants/{tenant_id}/nota-sgr")
def nota_sgr(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, operatie achizitie|vanzare|restituire|autofactura|virare,
    descriere?, + nr_ambalaje|suma, sursa casa|banca, +
    autofactura{garantii_returnate, tarif_gestionare?, cota?}; virare{suma,
    catre furnizor|plata}}. Garantia 0,50 lei/ambalaj, in afara sferei TVA."""
    from core import sgr as _sg
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        _cere_luna_deschisa(conn, schema, corp.get("data"))
        op = corp.get("operatie")
        try:
            if op == "achizitie":
                r = _sg.nota_garantie_achizitie(corp.get("nr_ambalaje"), corp.get("suma"))
                d0 = "SGR: garantie platita furnizorului 461=401 (fara TVA)"
            elif op == "vanzare":
                r = _sg.nota_garantie_vanzare(corp.get("nr_ambalaje"), corp.get("suma"),
                                              corp.get("sursa", "casa"))
                d0 = "SGR: garantie incasata de la client (distinct pe bon)"
            elif op == "restituire":
                r = _sg.nota_restituire_consumator(corp.get("nr_ambalaje"),
                                                   corp.get("suma"),
                                                   corp.get("sursa", "casa"))
                d0 = "SGR: restituire garantie consumator (461=creanta RetuRO)"
            elif op == "autofactura":
                r = _sg.nota_autofactura_returo(corp.get("garantii_returnate", 0),
                                                corp.get("tarif_gestionare", 0),
                                                _common.cota_ceruta(corp))
                d0 = "SGR: autofactura RetuRO (garantii fara TVA + tarif gestionare cu TVA)"
            elif op == "virare":
                r = _sg.nota_virare_garantii(corp["suma"], corp.get("catre", "furnizor"))
                d0 = "SGR: virare garantii incasate catre amonte 462"
            else:
                raise ValueError(nomenclator_cerut("operatie", "achizitie|vanzare|restituire|autofactura|virare"))
        except (ValueError, KeyError) as e:
            raise HTTPException(422, _mesaj_intrare(e))
        descr = (corp.get("descriere") or d0) + " - HG 1074/2021"
        with conn.cursor() as cur:
            cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status)
                            VALUES (%s,%s,'facturi','ciorna') RETURNING id""",
                        (corp["data"], descr[:200]))
            iid = cur.fetchone()[0]
            for dd, cc, ss in r["linii"]:
                cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                                (inregistrare_id, cont_debit, cont_credit, suma)
                                VALUES (%s,%s,%s,%s)""", (iid, dd, cc, ss))
        conn.commit()
    return {"inregistrare_id": iid, "linii": [[a, b, str(c)] for a, b, c in r["linii"]]}


@app.post("/tenants/{tenant_id}/nota-perisabilitati")
def nota_perisabilitati(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, valoare_intrari, procent_limita (coef. grupa HG 831/2004),
    pierdere_constatata, cota?, cont_stoc?, degradare_dovedita_distrusa?,
    descriere?}. Nota 607 (split deductibil/nedeductibil) + ajustare TVA 635=4426
    pe depasire."""
    from core import perisabilitati as _pe
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        _cere_luna_deschisa(conn, schema, corp.get("data"))
        try:
            r = _pe.calcul(corp["valoare_intrari"], corp["procent_limita"],
                           corp["pierdere_constatata"], _common.cota_ceruta(corp),
                           _cv.cere_cont(conn, schema, corp.get("cont_stoc"), "cont_stoc", "371"),
                           bool(corp.get("degradare_dovedita_distrusa")))
        except (ValueError, KeyError) as e:
            raise HTTPException(422, _mesaj_intrare(e))
        descr = (corp.get("descriere") or
                 f"Perisabilitati: limita {r['limita']}, deductibil {r['deductibil']}, "
                 f"nedeductibil {r['nedeductibil']} (PV inventariere)")[:200]
        with conn.cursor() as cur:
            cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status)
                            VALUES (%s,%s,'facturi','ciorna') RETURNING id""",
                        (corp["data"], descr + " - HG 831/2004"))
            iid = cur.fetchone()[0]
            for dd, cc, ss in r["linii"]:
                cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                                (inregistrare_id, cont_debit, cont_credit, suma)
                                VALUES (%s,%s,%s,%s)""", (iid, dd, cc, ss))
        conn.commit()
    return {"inregistrare_id": iid, "limita": str(r["limita"]),
            "deductibil": str(r["deductibil"]), "nedeductibil": str(r["nedeductibil"]),
            "ajustare_tva": str(r["ajustare_tva"]),
            "linii": [[a, b, str(c)] for a, b, c in r["linii"]]}


@app.post("/tenants/{tenant_id}/nota-contract-special")
def nota_contract_special(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, fel zilier|cenzor|mandat, brut, sursa casa|banca, descriere?}.
    Zilieri: impozit 10%+CAS 25% fara CASS (L52/2011). Cenzor/mandat: CAS+CASS+
    impozit, fara CAM (art. 76(2)g/i)."""
    from core import contracte_speciale as _cs
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        _cere_luna_deschisa(conn, schema, corp.get("data"))
        try:
            r = _cs.nota(corp["brut"], corp.get("fel", "zilier"),
                         corp.get("sursa", "casa"), la_data=corp.get("data"))
        except (ValueError, KeyError) as e:
            raise HTTPException(422, _mesaj_intrare(e))
        fel = corp.get("fel", "zilier")
        descr = (corp.get("descriere") or
                 f"Remuneratie {fel} brut {corp['brut']} (net {r['net']})") +                 (" - L52/2011" if fel == "zilier" else " - art. 76(2)g/i CF")
        with conn.cursor() as cur:
            cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status)
                            VALUES (%s,%s,'salarii','ciorna') RETURNING id""",
                        (corp["data"], descr[:200]))
            iid = cur.fetchone()[0]
            for dd, cc, ss in r["linii"]:
                cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                                (inregistrare_id, cont_debit, cont_credit, suma)
                                VALUES (%s,%s,%s,%s)""", (iid, dd, cc, ss))
        conn.commit()
    return {"inregistrare_id": iid, "brut": str(r["brut"]), "cas": str(r["cas"]),
            "cass": str(r["cass"]), "impozit": str(r["impozit"]), "net": str(r["net"]),
            "linii": [[a, b, str(c)] for a, b, c in r["linii"]]}


@app.get("/tenants/{tenant_id}/mijloace-fixe")
def tenant_mijloace_fixe(tenant_id: int, ctx=Depends(cere_cabinet)):
    """[ecran_mf_v1 14.08.2026; amortizare pe metoda 16.08.2026] Registrul mijloacelor fixe ale
    firmei: valoare, amortizat la zi PE METODA activului (liniar/degresiv/accelerat/superaccelerat,
    CF art.28 - motor unic core.d406_active.amortizat_la_data), ramas (net book value), stare
    activ/casat. Randul al carui activ are metoda nepermisa pe categorie (alin.5/8^1) NU se
    calculeaza liniar tacit: intoarce amortizat=None, ramas=None, eroare=<motiv> (DS cap.17).
    Casat: amortizat/ramas None (instantaneul de la casare nu se pastreaza in mijloace_fixe).
    Sursa unica pentru ID-ul cerut de casare/reevaluare (pana acum netastabil - niciun ecran)."""
    from decimal import Decimal
    from datetime import date as _date
    schema = _schema_sau_404(ctx, tenant_id)
    azi = _date.today()
    out = []
    with db.get_conn(schema) as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT id, cod, denumire, cont_imobilizare, cont_amortizare,
                                  valoare, rezidual, dnf_luni, data_pif, metoda, activ
                           FROM mijloace_fixe ORDER BY activ DESC, id""")
            rows = cur.fetchall()
    from core import d406_active as _d406
    for (mid, cod, den, ci, ca, val, rez, dnf, pif, met, activ) in rows:
        val = Decimal(str(val or 0)); rez = Decimal(str(rez or 0))
        amortizat = ramas = eroare = None
        if activ:
            mf_d = {"cod": cod, "denumire": den, "cont_imobilizare": ci, "cont_amortizare": ca,
                    "valoare": val, "rezidual": rez, "dnf_luni": dnf, "data_pif": pif, "metoda": met}
            try:
                r = _d406.amortizat_la_data(mf_d, azi)   # metoda reala (CF art.28), nu liniar
                amortizat = str(r["amortizat"]); ramas = str(r["ramas"])
            except (ValueError, KeyError) as e:
                eroare = str(e)   # metoda nepermisa / date invalide -> se arata, nu se fabrica liniar
        out.append({"id": mid, "cod": cod, "denumire": den,
                    "cont_imobilizare": ci, "cont_amortizare": ca,
                    "valoare": str(val), "rezidual": str(rez),
                    "dnf_luni": dnf, "data_pif": str(pif) if pif else None,
                    "metoda": met, "activ": bool(activ),
                    "amortizat": amortizat, "ramas": ramas, "eroare": eroare})
    return {"mijloace": out}


@app.post("/tenants/{tenant_id}/nota-inventariere")
def nota_inventariere(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, operatie plus|plus_mf|minus|casare, descriere?, +
    plus{valoare, cont_stoc?}; plus_mf{valoare, cont_imobilizare?};
    minus{valoare, cont_stoc?, imputabil?, valoare_imputare?, vinovat
    salariat|tert, cota?, asigurat_sau_distrus?};
    casare{mijloc_fix_id SAU valoare_bruta+amortizare_cumulata+conturi}.
    Casarea cu mijloc_fix_id calculeaza amortizarea auto si dezactiveaza MF."""
    from decimal import Decimal
    from datetime import date as _date
    from core import inventariere as _iv
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        _cere_luna_deschisa(conn, schema, corp.get("data"))
        op = corp.get("operatie")
        mf_id = None
        try:
            if op == "plus":
                r = _iv.nota_plus(corp["valoare"], _cv.cere_cont(conn, schema, corp.get("cont_stoc"), "cont_stoc", "371"))
                d0 = "Plus la inventar stocuri"
            elif op == "plus_mf":
                # [ruptura mijloc-fix post-migrare 14.08.2026] valideaza (art.28 alin.5/8^1) SI inscrie
                # activul in registrul mijloace_fixe (nu doar nota 21x=4754) -> ajunge la amortizare/D406.
                mf_reg = _iv.pregateste_mf_plus(corp)
                r = _iv.nota_plus_mf(corp["valoare"], mf_reg["cont_imobilizare"])
                d0 = "Plus la inventar mijloace fixe (21x=4754)"
            elif op == "minus":
                r = _iv.nota_minus(corp["valoare"], _cv.cere_cont(conn, schema, corp.get("cont_stoc"), "cont_stoc", "371"),
                                   bool(corp.get("imputabil")),
                                   corp.get("valoare_imputare"),
                                   corp.get("vinovat", "salariat"),
                                   _common.cota_ceruta(corp),
                                   bool(corp.get("asigurat_sau_distrus")))
                d0 = "Minus la inventar" + (" imputabil" if corp.get("imputabil") else
                                            " neimputabil")
            elif op == "casare":
                if corp.get("mijloc_fix_id"):
                    mf_id = corp["mijloc_fix_id"]
                    with conn.cursor() as cur:
                        cur.execute(f"""SELECT denumire, cont_imobilizare, cont_amortizare,
                                               valoare, COALESCE(rezidual,0), dnf_luni, data_pif, metoda
                                        FROM {schema}.mijloace_fixe
                                        WHERE id=%s AND activ=true""", (mf_id,))
                        mf = cur.fetchone()
                    if not mf:
                        raise HTTPException(404, "mijloc fix inexistent/inactiv")
                    den, ci, ca, val, rez, dnf, pif, met = mf
                    ref = _date.fromisoformat(corp["data"])
                    from core import d406_active as _d406
                    mf_d = {"cod": den, "denumire": den, "cont_imobilizare": ci, "cont_amortizare": ca,
                            "valoare": val, "rezidual": rez, "dnf_luni": dnf, "data_pif": pif, "metoda": met}
                    am = _d406.amortizat_la_data(mf_d, ref)["amortizat"]   # metoda reala, nu liniar
                    r = _iv.nota_casare_mf(val, am, ci, ca)
                    d0 = f"Casare {den} (PV comisie, neamortizat {r['neamortizat']})"
                else:
                    r = _iv.nota_casare_mf(corp["valoare_bruta"],
                                           corp["amortizare_cumulata"],
                                           _cv.cere_cont(conn, schema, corp.get("cont_imobilizare"), "cont_imobilizare", "2131"),
                                           _cv.cere_cont(conn, schema, corp.get("cont_amortizare"), "cont_amortizare", "2813"))
                    d0 = "Casare mijloc fix (PV comisie)"
            else:
                raise ValueError(nomenclator_cerut("operatie", "plus|plus_mf|minus|casare"))
        except (ValueError, KeyError) as e:
            raise HTTPException(422, _mesaj_intrare(e))
        descr = (corp.get("descriere") or d0) + " - OMFP 2861/2009"
        with conn.cursor() as cur:
            cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status)
                            VALUES (%s,%s,'facturi','ciorna') RETURNING id""",
                        (corp["data"], descr[:200]))
            iid = cur.fetchone()[0]
            for dd, cc, ss in r["linii"]:
                cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                                (inregistrare_id, cont_debit, cont_credit, suma)
                                VALUES (%s,%s,%s,%s)""", (iid, dd, cc, ss))
            if mf_id:
                cur.execute(f"UPDATE {schema}.mijloace_fixe SET activ=false WHERE id=%s",
                            (mf_id,))
            mf_nou_id = None
            if op == "plus_mf":
                cur.execute(f"""INSERT INTO {schema}.mijloace_fixe
                                (cod, denumire, cont_imobilizare, cont_amortizare, valoare,
                                 rezidual, dnf_luni, data_pif, metoda, activ)
                                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,true) RETURNING id""",
                            (mf_reg["cod"], mf_reg["denumire"], mf_reg["cont_imobilizare"],
                             mf_reg["cont_amortizare"], mf_reg["valoare"], mf_reg["rezidual"],
                             mf_reg["dnf_luni"], mf_reg["data_pif"], mf_reg["metoda"]))
                mf_nou_id = cur.fetchone()[0]
        conn.commit()
    rez_out = {"inregistrare_id": iid, "linii": [[a, b, str(c)] for a, b, c in r["linii"]]}
    if mf_nou_id:
        rez_out["mijloc_fix_id"] = mf_nou_id
    return rez_out


@app.post("/tenants/{tenant_id}/nota-lichidare")
def nota_lichidare(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, operatie vanzare_activ|partaj, descriere?, +
    vanzare_activ{pret, valoare_bruta, amortizare_cumulata, conturi?, cota?};
    partaj{capital_social, rezerve?, profituri?}}. OMFP 897/2015."""
    from datetime import date as _date
    from core import lichidare as _li
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        _cere_luna_deschisa(conn, schema, corp.get("data"))
        op = corp.get("operatie")
        info = {}
        try:
            if op == "vanzare_activ":
                r = _li.nota_vanzare_activ(corp["pret"], corp["valoare_bruta"],
                                           corp["amortizare_cumulata"],
                                           _cv.cere_cont(conn, schema, corp.get("cont_imobilizare"), "cont_imobilizare", "2131"),
                                           _cv.cere_cont(conn, schema, corp.get("cont_amortizare"), "cont_amortizare", "2813"),
                                           _common.cota_ceruta(corp))
                d0 = "Lichidare: valorificare activ (7583 + descarcare)"
            elif op == "partaj":
                r = _li.partaj(corp["capital_social"], corp.get("rezerve", 0),
                               corp.get("profituri", 0),
                               _date.fromisoformat(corp["data"]))
                info = {"castig_impozabil": str(r["castig_impozabil"]),
                        "impozit": str(r["impozit"]),
                        "net_asociat": str(r["net_asociat"]), "cota": r["cota"]}
                d0 = "Partaj lichidare: capital neimpozabil + castig cu impozit dividend"
            else:
                raise ValueError(nomenclator_cerut("operatie", "vanzare_activ|partaj"))
        except (ValueError, KeyError) as e:
            raise HTTPException(422, _mesaj_intrare(e))
        descr = (corp.get("descriere") or d0) + " - OMFP 897/2015"
        with conn.cursor() as cur:
            cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status)
                            VALUES (%s,%s,'facturi','ciorna') RETURNING id""",
                        (corp["data"], descr[:200]))
            iid = cur.fetchone()[0]
            for dd, cc, ss in r["linii"]:
                cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                                (inregistrare_id, cont_debit, cont_credit, suma)
                                VALUES (%s,%s,%s,%s)""", (iid, dd, cc, ss))
        conn.commit()
    return {"inregistrare_id": iid,
            "linii": [[a, b, str(c)] for a, b, c in r["linii"]], **info}


@app.post("/tenants/{tenant_id}/nota-ong")
def nota_ong(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, operatie venit|scutire, descriere?, +
    venit{suma, fel cotizatie|contributie|donatie|sponsorizare|financiar|
    fonduri|ocazional|alte, sursa casa|banca};
    scutire{venituri_economice, venituri_neimpozabile, curs_eur} - doar calcul,
    fara nota}. OMFP 3103/2017 + art. 15(2)-(3) CF."""
    from core import ong as _on
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise HTTPException(404, "tenant inexistent sau fără acces")
        _cere_luna_deschisa(conn, schema, corp.get("data"))
        op = corp.get("operatie", "venit")
        try:
            if op == "scutire":
                r = _on.scutire_economica(corp["venituri_economice"],
                                          corp["venituri_neimpozabile"],
                                          corp["curs_eur"])
                return {k: str(v) for k, v in r.items()}
            r = _on.nota_venit(corp["suma"], corp.get("fel", "cotizatie"),
                               corp.get("sursa", "casa"))
        except (ValueError, KeyError) as e:
            raise HTTPException(422, _mesaj_intrare(e))
        descr = (corp.get("descriere") or
                 f"Venit AFSP {corp.get('fel', 'cotizatie')} pe {r['cont_venit']}") +                 " - OMFP 3103/2017"
        with conn.cursor() as cur:
            cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status)
                            VALUES (%s,%s,'casa','ciorna') RETURNING id""",
                        (corp["data"], descr[:200]))
            iid = cur.fetchone()[0]
            for dd, cc, ss in r["linii"]:
                cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                                (inregistrare_id, cont_debit, cont_credit, suma)
                                VALUES (%s,%s,%s,%s)""", (iid, dd, cc, ss))
        conn.commit()
    return {"inregistrare_id": iid, "cont_venit": r["cont_venit"],
            "linii": [[a, b, str(c)] for a, b, c in r["linii"]]}

# bon_flux_e6_v1


# --- Conector SPV/ANAF (rute in core/spv_rute.py; montate aici ca sa refoloseasca
#     cere_cabinet fara import circular). Ecranul de conectare = Regula 0, separat. ---
from core import spv_rute as _spv_rute
_spv_rute.monteaza(app, cere_context)  # proprietatea principalului o impune spv_principal (cabinet XOR gratuit)


@app.get("/ajutor/{fid}")
def ajutor_contextual(fid: str):
    """Ajutor contextual pentru contabil (semnul "?" din UI). Public: text de FOLOSIRE a
    functionalitatii (ce face, cand, pasi, reguli fiscale) - NU date de firma. Sursa: coloana
    ajutor din FUNCTIONALITATI.csv (core/ajutor.py). 404 daca nu are ajutor scris."""
    from core import ajutor as _aj
    a = _aj.pentru(fid)
    if not a:
        raise HTTPException(404, "fără ajutor pentru această funcționalitate")
    return a


@app.get("/ansamblu")
def ansamblu_aplicatie(ctx=Depends(cere_context)):
    """Prezentarea de ansamblu a aplicatiei (semnul "?" GENERAL din bara de stare +
    pagina de bun-venit). Continut DERIVAT, nu scris separat: grupele din registru
    (genereaza_grupe_functii.repartizeaza, SURSA UNICA a repartizarii) + flagul de ajutor
    per functionalitate (core/ajutor.py). Firul de intrare (pasii de migrare) e in front
    (STRATURI, migrare.js). Autentificat: orice rol logat."""
    from genereaza_grupe_functii import repartizeaza
    from core import ajutor as _aj
    import csv as _csv
    grupe = repartizeaza()  # [{titlu, icon, functii:[nume sortate]}]
    rows = list(_csv.reader(open("FUNCTIONALITATI.csv", encoding="utf-8-sig")))[1:]
    nume2id = {r[0].strip(): r[2].strip() for r in rows if len(r) > 2}
    cu = _aj.cu_ajutor()
    out = []
    for gr in grupe:
        ff = [{"nume": n, "id": nume2id.get(n),
               "are_ajutor": bool(nume2id.get(n) and nume2id.get(n) in cu)}
              for n in gr["functii"]]
        out.append({"titlu": gr["titlu"], "icon": gr["icon"], "functii": ff})
    return {"grupe": out}


@app.post("/cont/bun-venit-vazut")
def cont_bun_venit_vazut(ctx=Depends(cere_context)):
    """Marcheaza prezentarea de bun-venit ca vazuta (o data, la prima logare)."""
    with db.get_conn() as conn:
        auth_api.marcheaza_bun_venit(conn, ctx["uid"])
    return {"ok": True}


# ============================================================
#  PAGINI PUBLICE DE GHID (DS cap.22) — /ghid/{slug} + index + sitemap + robots
# ============================================================
import re as _ghid_re
import html as _ghid_html
import json as _ghid_json

_GHID_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ghid")
_GHID_SLUG_RE = _ghid_re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_GHID_BAZA = "https://iconta.eu"          # domeniu canonic public (canonical, og:url, sitemap)
# [ghid_redirect] slug-uri retrase -> 301 permanent catre succesor (consolidare continut, pastreaza SEO).
_GHID_REDIRECT = {
    "cote-tva-2025": "cote-tva-2026",
    "corelare-d406-d300-d301-contabil": "corelare-d406-d300-d301",
    "credit-fiscal-cercetare-dezvoltare-contabil": "credit-fiscal-cercetare-dezvoltare",
    "d406-active-microintreprinderi-contabil": "d406-active-microintreprinderi",
    "formular-800-facturi-netransmise-contabil": "formular-800-facturi-netransmise",
    "rectificativa-dupa-bonificatie-contabil": "rectificativa-dupa-bonificatie",
    "risc-fiscal-ridicat-contabil": "risc-fiscal-ridicat",
}
_GHID_OG_IMAGINE = _GHID_BAZA + "/static/logo_login.png"   # provizoriu; DE_FACUT: imagine dedicata per ghid

# Shell public: leaga stil.css, foloseste DOAR clase + tokeni (fara <style> inline, fara culori
# scrise direct). {{META}} = description + canonical + Open Graph + JSON-LD, construite PER PAGINA.
_GHID_PAGINA = """<!doctype html>
<html lang="ro" class="pagina-publica">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{TITLU}} · iConta.eu</title>
{{META}}
<link rel="stylesheet" href="/static/stil.css">
<link rel="manifest" href="/static/manifest.json">
<link rel="apple-touch-icon" href="/static/icon-192.png">
</head>
<body class="pagina-publica">
<div class="ghid-shell">
  <header class="pagina-bara">
    <a class="pagina-bara-stanga" href="/">
      <img class="pagina-bara-logo" src="/static/logo_login.png" alt="iConta.eu">
      <span class="pagina-bara-marca">iConta.eu</span>
    </a>
    <a class="pagina-bara-acces" href="/">Intră în cont</a>
  </header>
  <main class="ghid-wrap">
{{CORP}}
    <hr>
    <p class="ghid-subsol"><a href="/ghid">Toate ghidurile</a> · <a href="/">← iConta.eu</a> · <a href="/public/termeni">Termeni și condiții</a></p>
  </main>
</div>
{{BEACON}}</body>
</html>"""


def _ghid_frontmatter(txt):
    """Front-matter simplu la inceputul fisierului, intre linii '---':
        ---
        title: ...        (optional; altfel titlul = primul H1)
        description: ...  (meta description + og:description; sub 160 caractere)
        published: 2026-07-26   (data publicarii)
        modified: 2026-07-26    (data ultimei actualizari)
        ---
    Intoarce (meta_dict cu chei lowercase, corp_markdown fara front-matter). Fara front-matter -> ({}, txt)."""
    linii = txt.split("\n")
    if linii and linii[0].strip() == "---":
        for i in range(1, len(linii)):
            if linii[i].strip() == "---":
                meta = {}
                for ln in linii[1:i]:
                    if ":" in ln:
                        k, v = ln.split(":", 1)
                        meta[k.strip().lower()] = v.strip().strip('"').strip("'")
                return meta, "\n".join(linii[i + 1:]).lstrip("\n")
    return {}, txt


def _ghid_titlu(txt):
    for _ln in txt.split("\n"):
        if _ln.startswith("# "):
            return _ln[2:].strip()
    return "Ghid"


def _ghid_mtime(cale):
    import datetime as _d
    try:
        return _d.date.fromtimestamp(os.path.getmtime(cale)).isoformat()
    except Exception:
        return ""


def _ghid_semafor(linii):
    """Semafor grafic (DS cap.8/22): linii 'rosu|galben|verde|gri: text' -> randuri cu LED
    colorat DOAR prin token (--rosu-semafor/--galben/--verde/--gri-semafor), ordinea din fisier."""
    randuri = []
    for _ln in linii:
        _s = _ln.strip()
        if not _s:
            continue
        _m = _ghid_re.match(r'^(rosu|galben|verde|gri)\s*:\s*(.*)$', _s, _ghid_re.I)
        if not _m:
            continue
        _cul = _m.group(1).lower()
        _txt = _ghid_html.escape(_m.group(2).strip())
        randuri.append(
            '<div class="ghid-semafor-rand ghid-semafor-%s"><span class="ghid-semafor-led"></span>'
            '<span class="ghid-semafor-text">%s</span></div>' % (_cul, _txt))
    return '<div class="ghid-semafor">' + "".join(randuri) + '</div>'


def _ghid_containers(txt):
    """Sintaxa proprie, simpla de scris de mana: blocuri ':::nume ... :::' -> <div class=nume>
    (markdown randat inauntru prin md_in_html). ':::ghid-semafor' e special (linii culoare:text)."""
    linii = txt.split("\n")
    out = []
    i = 0
    n = len(linii)
    while i < n:
        ln = linii[i]
        m = _ghid_re.match(r'^:::\s*([a-z0-9-]+)\s*$', ln.strip())
        if m:
            nume = m.group(1)
            j = i + 1
            corp = []
            while j < n and linii[j].strip() != ":::":
                corp.append(linii[j])
                j += 1
            if nume == "ghid-semafor":
                out.append(_ghid_semafor(corp))
            else:
                out.append('<div class="%s" markdown="1">' % nume)
                out.append("")
                out.extend(corp)
                out.append("")
                out.append("</div>")
            i = j + 1
        else:
            out.append(ln)
            i += 1
    return "\n".join(out)


def _ghid_randeaza(txt):
    import markdown as _md
    return _md.markdown(_ghid_containers(txt),
                        extensions=["extra", "sane_lists", "md_in_html", "attr_list"])


def _ghid_pagina_html(titlu, descriere, canonical, corp_html, noindex=False, jsonld=None, og_type="article", slug=""):
    meta = []
    if noindex:
        meta.append('<meta name="robots" content="noindex">')
    if descriere:
        _d = _ghid_html.escape(descriere)
        meta.append('<meta name="description" content="%s">' % _d)
    if canonical:
        _c = _ghid_html.escape(canonical)
        meta.append('<link rel="canonical" href="%s">' % _c)
        meta.append('<meta property="og:url" content="%s">' % _c)
    meta.append('<meta property="og:type" content="%s">' % og_type)
    meta.append('<meta property="og:site_name" content="iConta.eu">')
    meta.append('<meta property="og:locale" content="ro_RO">')
    meta.append('<meta property="og:title" content="%s">' % _ghid_html.escape(titlu))
    if descriere:
        meta.append('<meta property="og:description" content="%s">' % _ghid_html.escape(descriere))
    meta.append('<meta property="og:image" content="%s">' % _ghid_html.escape(_GHID_OG_IMAGINE))
    if jsonld:
        _s = _ghid_json.dumps(jsonld, ensure_ascii=False).replace("<", "\\u003c")
        meta.append('<script type="application/ld+json">%s</script>' % _s)
    _beacon = ("<script>try{var b=JSON.stringify({tip:'vizita_ghid',pagina:%s});navigator.sendBeacon&&navigator.sendBeacon('/api/eveniment-public',new Blob([b],{type:'application/json'}))}catch(e){}</script>\n"
               % _ghid_json.dumps(slug)) if slug else ""
    return (_GHID_PAGINA
            .replace("{{TITLU}}", _ghid_html.escape(titlu))
            .replace("{{META}}", "\n".join(meta))
            .replace("{{BEACON}}", _beacon)
            .replace("{{CORP}}", corp_html))


def _ghid_404():
    return Response(
        content=_ghid_pagina_html("Ghid inexistent", "", "",
                                  "<h1>Ghid inexistent</h1><p>Pagina căutată nu există sau a fost mutată.</p>",
                                  noindex=True),
        media_type="text/html; charset=utf-8", status_code=404)


def _ghid_lista():
    """Lista ghidurilor PUBLICATE = TOATE fisierele ghid/*.md cu front-matter valid. Sursa UNICA pentru index +
    sitemap (aliniat la ce declara comentariul: ghid/ e sursa unica). FUNCTIONALITATI.csv (coloana ghid_slug) NU
    mai decide ce pagini EXISTA - ramane doar pentru legatura inversa functionalitate->ghid. Un fisier fara
    front-matter valid e EXCLUS cu LOG EXPLICIT (nu tacut). Fiecare: {slug, titlu, descriere, published, modified}."""
    import glob as _glob
    out = []
    for cale in sorted(_glob.glob(os.path.join(_GHID_DIR, "*.md"))):
        nume = os.path.basename(cale)
        slug = nume[:-3]
        if not _GHID_SLUG_RE.match(slug):
            print("[ghid] EXCLUS (slug invalid): %s" % nume, flush=True)
            continue
        try:
            meta, corp = _ghid_frontmatter(open(cale, encoding="utf-8").read())
        except Exception as e:
            print("[ghid] EXCLUS (citire esuata): %s (%s)" % (nume, e), flush=True)
            continue
        if not meta:
            print("[ghid] EXCLUS (fara front-matter valid): %s" % nume, flush=True)
            continue
        out.append({"slug": slug,
                    "titlu": meta.get("title") or _ghid_titlu(corp),
                    "descriere": meta.get("description", ""),
                    "published": meta.get("published", ""),
                    "modified": meta.get("modified", "") or _ghid_mtime(cale)})
    out.sort(key=lambda g: g["slug"])
    return out


# ---- Analytics public FARA date personale (eveniment: ce/de unde/cand; NU ip/UA/cookie/sesiune/user) ----
_EVENIMENTE_PUBLICE = frozenset((
    "vizita_landing", "modal_functionalitati", "deschide_preturi", "intra_in_cont", "vizita_ghid"))


class EvenimentPublicIn(BaseModel):
    tip: str
    pagina: Optional[str] = None


@app.post("/api/eveniment-public")
def eveniment_public(date: EvenimentPublicIn):
    """Inregistrare eveniment public de interes (deschidere modal, click Intra in cont, vizita ghid).
    Se stocheaza DOAR: tip (lista alba), pagina (calea proprie, curatata) si momentul (DEFAULT now()).
    NU se citeste si NU se retine IP, User-Agent, cookie, sesiune sau vreun identificator -> fara date
    personale -> fara obligatie de consimtamant. Fire-and-forget (clientul foloseste sendBeacon)."""
    tip = (date.tip or "").strip()
    if tip not in _EVENIMENTE_PUBLICE:
        return {"ok": False}   # tip necunoscut -> se ignora (nu strica clientul)
    pagina = "".join(c for c in (date.pagina or "landing").strip().lower()
                     if c.isalnum() or c in "/_-")[:128] or "landing"
    try:
        with db.get_conn() as conn, conn.cursor() as cur:
            cur.execute("INSERT INTO public.eveniment_public (tip, pagina) VALUES (%s, %s)", (tip, pagina))
    except Exception:
        return {"ok": False}
    return {"ok": True}


@app.get("/admin/analytics")
def admin_analytics(zile: int = 30, ctx=Depends(cere_rol("superadmin"))):
    """Cifre agregate din public.eveniment_public: pe eveniment, pe zi, pe pagina de provenienta.
    Fara date personale (tabela nu contine niciun identificator)."""
    zile = max(1, min(int(zile or 30), 365))
    with db.get_conn() as conn, conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
        cur.execute("SELECT tip, COUNT(*) AS n FROM public.eveniment_public "
                    "WHERE creat_la >= now() - (%s || ' days')::interval GROUP BY tip ORDER BY n DESC", (zile,))
        pe_eveniment = cur.fetchall()
        cur.execute("SELECT to_char(date_trunc('day', creat_la), 'YYYY-MM-DD') AS zi, COUNT(*) AS n "
                    "FROM public.eveniment_public WHERE creat_la >= now() - (%s || ' days')::interval "
                    "GROUP BY 1 ORDER BY 1 DESC", (zile,))
        pe_zi = cur.fetchall()
        cur.execute("SELECT COALESCE(NULLIF(pagina,''),'landing') AS pagina, COUNT(*) AS n "
                    "FROM public.eveniment_public WHERE creat_la >= now() - (%s || ' days')::interval "
                    "GROUP BY 1 ORDER BY n DESC LIMIT 100", (zile,))
        pe_pagina = cur.fetchall()
        cur.execute("SELECT COUNT(*) AS n FROM public.eveniment_public "
                    "WHERE creat_la >= now() - (%s || ' days')::interval", (zile,))
        total = cur.fetchone()["n"]
    return {"zile": zile, "total": total, "pe_eveniment": pe_eveniment, "pe_zi": pe_zi, "pe_pagina": pe_pagina}


@app.get("/ghid/{slug}")
def public_ghid(slug: str):
    """Pagina publica de ghid (DS cap.22). Fara autentificare. slug -> ghid/{slug}.md -> markdown -> shell.
    Front-matter per pagina: title (optional), description, published, modified."""
    if not _GHID_SLUG_RE.match(slug or ""):
        return _ghid_404()
    if slug in _GHID_REDIRECT:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(_GHID_BAZA + "/ghid/" + _GHID_REDIRECT[slug], status_code=301)
    cale = os.path.join(_GHID_DIR, slug + ".md")
    if not os.path.isfile(cale):
        return _ghid_404()
    meta, corp_md = _ghid_frontmatter(open(cale, encoding="utf-8").read())
    h1 = _ghid_titlu(corp_md)
    titlu = meta.get("title") or h1
    descriere = meta.get("description", "")
    canonical = _GHID_BAZA + "/ghid/" + slug
    jsonld = {"@context": "https://schema.org", "@type": "Article",
              "headline": h1, "description": descriere, "inLanguage": "ro-RO",
              "datePublished": meta.get("published", ""),
              "dateModified": meta.get("modified", "") or _ghid_mtime(cale),
              "author": {"@type": "Organization", "name": "iConta.eu", "url": _GHID_BAZA},
              "publisher": {"@type": "Organization", "name": "iConta.eu", "legalName": "FISCALOS ICONTA SRL",
                            "url": _GHID_BAZA,
                            "logo": {"@type": "ImageObject", "url": _GHID_BAZA + "/static/icon-512.png"}},
              "mainEntityOfPage": {"@type": "WebPage", "@id": canonical},
              "image": _GHID_OG_IMAGINE}
    jsonld = {k: v for k, v in jsonld.items() if v not in ("", None)}
    return Response(content=_ghid_pagina_html(titlu, descriere, canonical, _ghid_randeaza(corp_md), jsonld=jsonld, slug=slug),
                    media_type="text/html; charset=utf-8")


@app.get("/ghid")
def public_ghid_index():
    """Index-ul ghidurilor: legat din subsol, ca paginile sa nu existe doar in sitemap. Generat din _ghid_lista()."""
    guides = _ghid_lista()
    items = []
    for g in guides:
        t = _ghid_html.escape(g["titlu"])
        items.append('<h2><a href="/ghid/%s">%s</a></h2>' % (g["slug"], t))
        if g["descriere"]:
            items.append('<p>%s</p>' % _ghid_html.escape(g["descriere"]))
    corp = ('<h1>Ghiduri fiscale iConta.eu</h1>'
            '<p>Ghiduri practice pentru contabili: temei legal verificat la sursă, procedura manuală și '
            'ce automatizează iConta.eu. Se adaugă pe măsură ce le scriem.</p>'
            + ("\n".join(items) if items else "<p>În curând.</p>"))
    return Response(content=_ghid_pagina_html(
        "Ghiduri fiscale",
        "Ghiduri fiscale practice pentru contabili — temei legal, proceduri și controalele automate iConta.eu.",
        _GHID_BAZA + "/ghid", corp, og_type="website"),
        media_type="text/html; charset=utf-8")


@app.get("/sitemap.xml")
def public_sitemap():
    """Sitemap generat din aceleasi surse ca index-ul (CSV + fisiere) — nu scris de mana."""
    guides = _ghid_lista()

    def u(loc, lastmod=None):
        s = "  <url><loc>%s</loc>" % _ghid_html.escape(loc)
        if lastmod:
            s += "<lastmod>%s</lastmod>" % lastmod
        return s + "</url>"

    lastmods = [g["modified"] for g in guides if g["modified"]]
    urls = [u(_GHID_BAZA + "/"),
            u(_GHID_BAZA + "/ghid", max(lastmods) if lastmods else None)]
    for g in guides:
        urls.append(u(_GHID_BAZA + "/ghid/" + g["slug"], g["modified"] or None))
    urls.append(u(_GHID_BAZA + "/public/termeni"))
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + "\n".join(urls) + "\n</urlset>\n")
    return Response(content=xml, media_type="application/xml; charset=utf-8")


@app.get("/robots.txt")
def public_robots():
    # [robots_allowlist 15.08.2026] Allow-list a suprafetei publice indexabile; restul Disallow.
    # Adaugat ca REPARATIE pentru un raport Search Console de 404-uri pe cai care nu exista
    # (prima detectare 05.08.2026, 18 cai la RADACINA, de forma /depune, /tva?an, /d406-mapare).
    #
    # CE S-A MASURAT, 27.08.2026, dupa ce Costin a raportat 17 cai ramase:
    #   sitemap.xml            NU le contine. Generatorul (`public_sitemap`) listeaza EXCLUSIV
    #                          ghid/*.md + landing + termeni; nu atinge inventarul de rute.
    #   HTML-ul public randat  NU le contine (landing 4 linkuri interne, toate /static/; /ghid 208,
    #                          toate ghiduri; /public/termeni 2).
    #   cele 202 de ghiduri    NU le contin.
    #   JS-ul servit azi       3 din 17 apar ca sub-sir, si acelea in COMENTARII sau ca segment al
    #                          unei cai reale (`/tenants/${id}/salariati`).
    #   istoria git            `d205-beneficiari`, `nota-manuala`, `pacht`, `documents/list`,
    #                          `facturi/primita`, `feedback/cabinet`: ZERO commituri, niciodata,
    #                          nicaieri in repo. Iar "pacht" e "pachet" scris gresit - un fragment
    #                          cules dintr-un bundle ar reproduce bundle-ul, nu o eroare de tastare.
    #   logurile nginx         0 cereri catre cele 17 cai, in 40.878 de linii (17-27.08).
    #
    # DECI: mecanismul presupus initial - Googlebot culege fragmente concatenate din app.js - a fost
    # verificat si NU SE SUSTINE pentru cel putin sase din 17. A stat trei saptamani citit ca fapt,
    # iar comentariul asta era singura sursa din repo pentru doua dintre caile pe care le explica.
    # (Clasa R16: proza care descrie codul, falsa de la nastere.)
    #
    # DATELE DE ACCESARE, din Search Console (Costin, 27.08.2026) - ele inchid intrebarea:
    #   ultima accesare cu crawlere, pe toate 17: 30 iul · 27 iul (x4) · 26 iul · 24 iul ·
    #   23 iul (x3) · 13 iul · 4 iul · 15 iun (x2) · 14 iun (x2) · 12 iul.
    #   NICIUNA dupa 17.08. Cea mai recenta e 30 iulie. Deci raportul din Search Console e
    #   REZIDUU: descrie o stare veche, nu una care se produce acum.
    #
    # CE NU SE POATE AFIRMA, si e o limita a inferentei, nu a masuratorii: ca allow-list-ul a OPRIT
    # accesarile. Ultima e din 30 iulie, adica cu SAISPREZECE ZILE inainte de el (15.08). Google
    # incetase deja. Absenta de dupa 17.08 arata ca starea e curata, NU ca reparatia a produs-o.
    # Ce garanteaza reparatia e altceva, si se verifica direct: suprafata e Disallow de-acum incolo.
    #
    # CE RAMANE NECUNOSCUT: de unde le stia Google atunci. Fereastra - iunie/iulie - nu mai exista
    # in loguri (se pastreaza 11 zile), iar Search Console nu pastreaza referrerul pentru accesari
    # atat de vechi. Nu se mai poate masura de nicaieri. Se scrie asa, nu se umple cu o ipoteza:
    # necunoscut, masurat pana aici.
    txt = ("User-agent: *\n"
           "Allow: /$\n"                    # exact landing-ul
           "Allow: /ghid\n"                 # index + /ghid/{slug}
           "Allow: /public/termeni\n"
           "Allow: /static/\n"              # CSS, iconite, manifest (necesare la randare)
           "Disallow: /static/js/\n"        # bundle-ul app (app.js) expune fragmente de rute API -> Googlebot le culege; nu se scaneaza (05.08: 18x404+1x401)
           "Allow: /sitemap.xml\n"
           "Allow: /robots.txt\n"
           "Disallow: /\n"                  # restul suprafetei (app, /public/plata, /auth, rute API)
           "Sitemap: %s/sitemap.xml\n" % _GHID_BAZA)
    return Response(content=txt, media_type="text/plain; charset=utf-8")


@app.get("/admin/versiune")
def admin_versiune(ctx=Depends(cere_rol("superadmin"))):
    """Detector "running == HEAD" (superadmin): commitul cu care a pornit procesul viu (stampilat in memorie la
    startup) vs HEAD de pe disc citit acum. Semnaleaza divergenta; NU reporneste, NU repara (decizia iulie).
    Vizibil in app DOAR pentru superadmin (cere_rol -> 403 pentru orice alt rol). Commitul rulat vine din
    memoria procesului (stampila de la pornire), nu din mtime-uri de fisier."""
    from core import versiune as _versiune
    return _versiune.stare()
