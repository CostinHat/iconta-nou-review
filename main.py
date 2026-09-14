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
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from core import articole_import_api
#: [P6 val 1, 12.09.2026] Casa comuna a starii business care nu mai are voie sa traiasca
#: in memoria unui proces. V. docstringul modulului pentru masuratorile de dinainte.
from core import stare_partajata as _stare_part
#: [P6 val 3, 12.09.2026] Ce trebuie sa stie un proces care nu mai e singur: cine instaleaza
#: infrastructura, cine face munca de fundal, si cine poarta ce commit.
from core import instante as _instante
# [R23] RE-EXPORT, nu import nefolosit: `core/firma_rezumat.py` cheama `main.pastila_firma` si
# `main.stare_din_nivel` prin `import main as _main` — lucratorul modelului de citire ii cere
# de acolo. Scoase de o curatenie automata, sase firme au ajuns cu `control_fiscal` in stare de
# EROARE. „Nefolosit aici" nu inseamna „nefolosit" intr-un modul care e citit din afara.
from core.common import pastila_firma, stare_din_nivel  # noqa: F401
from core import db, auth_api, anaf_api, migrare_api, solduri_api, asociati_import_api, mijloace_fixe_import_api, istoric_declaratii_import_api, termene_api, produse_api, observare as _obs
# [P7 · V1] Repository-urile de citire: SQL-ul rutelor a plecat acolo.
from core import afirmatii as _af  # [P8] afirmatiile despre datele firmei sunt obiecte, nu siruri
from core import raport_z as _raport_z  # [R61] unicitatea raportului Z, impusa in BAZA
from core import cronometru as _crono   # [P5] segmentele unei cereri; INERT fara ICONTA_CRONOMETRU
from core.unde import Unde as _Unde  # [P8] domeniul poate fi un OBIECT, nu o perioada
from core.mesaje import (ROL_INSUFICIENT, DOAR_ADMIN_ICONTA)
from core.common import nomenclator_cerut


# ============================================================
#  [P7 · valul use-case, 13.09.2026] HOTARUL HTTP <-> USE_CASE
# ============================================================
# Stratul use-case refuza in limbajul domeniului (`core/erori.py`); AICI, si numai aici, refuzul
# devine cod de protocol. Harta e completa peste `erori.TOATE` — o clasa noua fara traducere ar iesi
# din aplicatie ca `500`, si de-aia `core/test_p7_uc.py` cere acoperirea ei.
#
# De ce se poate face traducerea fara sa schimbe nimic: `HTTPException` **nu e prinsa nicaieri** in
# aplicatie (masurat: zero `except HTTPException`), deci rolul ei e exclusiv de iesire. Codul si
# mesajul ies literă cu literă cum ieseau.
from core import erori as _erori
from core import uc_comun as _uc_comun
from core import uc_auth as _uc_auth
from core import uc_recomanda as _uc_recomanda
from core import uc_firme as _uc_firme
from core import uc_tipare as _uc_tipare
from core import uc_termene as _uc_termene
from core import uc_tenants as _uc_tenants
from core import uc_supervizor as _uc_supervizor
from core import uc_raportari as _uc_raportari
from core import uc_public as _uc_public
from core import uc_portal as _uc_portal
from core import uc_pachete as _uc_pachete
from core import uc_notificari as _uc_notificari
from core import uc_migrare as _uc_migrare
from core import uc_gdpr as _uc_gdpr
from core import uc_firme_scoase as _uc_firme_scoase
from core import uc_eu as _uc_eu
from core import uc_declaratii as _uc_declaratii
from core import uc_cor as _uc_cor
from core import uc_control_fiscal as _uc_control_fiscal
from core import uc_cont as _uc_cont
from core import uc_coada as _uc_coada
from core import uc_capacitate as _uc_capacitate
from core import uc_cabinet as _uc_cabinet
from core import uc_asistenti as _uc_asistenti
from core import uc_api as _uc_api
from core import uc_admin as _uc_admin

_COD_EROARE = (
    (_erori.CerereGresita, 400),
    (_erori.Neautentificat, 401),
    (_erori.FaraDrept, 403),
    (_erori.Inexistent, 404),
    (_erori.Conflict, 409),
    (_erori.DateInvalide, 422),
    (_erori.Blocat, 423),
    (_erori.IntrarePreaMare, 413),
    (_erori.FormatNeacceptat, 415),
    (_erori.PreaDes, 429),
    (_erori.EsecIntern, 500),
    (_erori.ServiciuStrainCazut, 502),
    (_erori.ServiciuIndisponibil, 503),
)


def _http_din(e):
    """Traduce un refuz de domeniu in `HTTPException`. INTOARCE exceptia; ridicarea o face apelantul.

    De ce nu un inveli care cheama functia: pasand-o ca valoare, muchia ruta -> use-case dispare din
    orice analiza statica de graf. Masurat: candidatii P5 au scazut 54 -> 48, nu fiindca s-ar fi
    reparat ceva, ci fiindca patru rute nu mai erau vizibile de la punctul de intrare.

    Ce nu e in vocabular nu se traduce: se re-ridica neatins, ca sa nu inventam niciun cod."""
    for _clasa, _cod in _COD_EROARE:
        if isinstance(e, _clasa):
            return HTTPException(_cod, e.detaliu)
    return e



def _cere_perioada(an=None, luna=None, exercitiu=None, camp_an="an"):
    """[P7 · use-case] Invelisul HTTP al lui `core/uc_comun._cere_perioada` — traduce refuzul de
    domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._cere_perioada(an, luna, exercitiu, camp_an)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


def _mesaj_intrare(e):
    """[P7 · use-case] Invelisul HTTP al lui `core/uc_comun._mesaj_intrare` — traduce refuzul de
    domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._mesaj_intrare(e)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

# template SQL pentru schema unui tenant nou (generat din tenant_001)
TENANT_TEMPLATE_PATH = os.environ.get(
    "ICONTA_TENANT_TEMPLATE",
    os.path.join(os.path.dirname(__file__), "tenant_template.sql"))
# [P7 · lotul 2] Sablonul traieste in `core/uc_comun.py`; aici se PUNE, in `lifespan`.
# [P7 · valul use-case] Declaratia a plecat cu VALOAREA, in `core/uc_comun.py`: registrul P6 cere ca
# fiecare stare declarata sa-si poarte cele cinci lucruri in modulul in care traieste.


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
                pg_tz = _repo.sql(cur)[0]
    if pg_tz != "Europe/Bucharest":
        raise RuntimeError(
            "PG timezone nu e Europe/Bucharest (%s) — app-ul refuză să pornească "
            "(nepotrivire OS<->PG pe verdictele de zi)" % pg_tz)


# ============================================================
#  LIFECYCLE — pool deschis la pornire, închis la oprire
# ============================================================
#: Câte taskuri de fundal a pornit `lifespan()`. Există ca să se poată PROBA că ele nu pornesc
#: când infrastructura critică pică — o afirmație despre ordine nu se poate verifica altfel decât
#: numărând, iar `asyncio` nu ține o evidență la care să ajungă un test.
_TASKURI_FUNDAL_PORNITE = 0


@asynccontextmanager
async def lifespan(app):
    verifica_secrete_obligatorii()   # fail-fast INAINTE de orice: fara JWT_SECRET nu pornim
    from core import versiune as _versiune_boot; _versiune_boot.stampileaza()  # running==HEAD: commitul de pornire (in memorie)
    db.init_pool()
    verifica_fus_orar()   # fail-fast: OS TZ + PG timezone = Europe/Bucharest (invarianta de provisionare)
    # ════════════════════════════════════════════════════════════════════════
    #  INFRASTRUCTURA CRITICĂ — FAIL-CLOSED (09.09.2026, la auditul remedierii P2)
    # ════════════════════════════════════════════════════════════════════════
    # Aici era `except Exception: pass`, cu motivul scris „nu blocam pornirea daca DB e temporar
    # indisponibil". Motivul era FALS de la naștere: `verifica_fus_orar()`, două linii mai sus,
    # deschide deja o conexiune și ridică — deci o bază căzută oprea pornirea și înainte. Ce
    # apuca `except`-ul nu era indisponibilitatea bazei, ci **eșecul instalării infrastructurii**.
    #
    # Iar asta e incompatibil cu chiar garanția pe care o poartă P2: *nicio valoare veche nu se
    # arată drept curentă*. Fără registrul aspect->sursă, versiunea oricărui aspect e 0, deci
    # ORICE rezumat pare curent, pe veci. Fără triggere, nimic nu mai invalidează. Fără coloana
    # `epoca`, dependența de timp dispare. **Niciuna nu produce o eroare la citire** — produc
    # exact defectul pe care P2 îl repară. O aplicație care nu poate garanta prospețimea nu are
    # voie să pretindă că o garantează; are voie doar să nu pornească.
    #
    # ┌────────────────────────────────────────────────────────────────────────────┐
    # │ INVARIANTĂ — NU RELAXA BLOCUL ĂSTA.                                        │
    # │ Infrastructura P2 decide dacă un rezumat poate fi considerat CURENT.        │
    # │ Eșecul DDL-ului, al migrării triggerelor sau al verificării e FATAL pentru  │
    # │ pornire. Nu reveni la `except Exception: pass` sub pretextul „baza poate fi │
    # │ temporar indisponibilă": dacă baza e jos și P2 nu se poate verifica,        │
    # │ serviciul NU e `ready`. Asta e purtarea corectă, nu o strictețe inutilă.    │
    # │ Gardat de `core/test_p2_infrastructura.py` — a se păstra permanent.         │
    # └────────────────────────────────────────────────────────────────────────────┘
    _log_boot = logging.getLogger("iconta")
    try:
        with db.get_conn() as conn:
            # [P6 val 3, 12.09.2026 · REPARAT 12.09.2026] PRIMUL lucru din tranzactie — si de
            # data asta chiar primul. `migreaza_triggerele` face `DROP TRIGGER` + `CREATE TRIGGER`
            # pentru FIECARE firma; doi workeri porniti in aceeasi secunda ar face-o simultan, pe
            # aceleasi obiecte. Blocajul e legat de TRANZACTIE, deci se elibereaza singur la commit
            # sau la rollback — un worker care moare la mijloc nu lasa poarta incuiata. Nimeni nu
            # SARE peste instalare: se asteapta.
            #
            # CE ERA STRICAT, masurat pe productie la prima pornire reala cu doi workeri: blocajul
            # se lua aici, dar linia URMATOARE (`migrare_api.asigura_tabel`) se termina cu
            # `conn.commit()`, iar un blocaj legat de tranzactie moare odata cu ea. Deci tot ce
            # trebuia aparat — DDL-ul supervizorului, tabelele valului 1, triggerele celor 37 de
            # firme, verificarea P2 — rula NESERIALIZAT, si la fiecare repornire un worker murea cu
            # `tuple concurrently updated`. Patru reporniri din patru. In `pg_locks`, pe toata
            # durata pornirii, blocajul nu se vedea NICIODATA — asa s-a si gasit.
            #
            # Reparatia are trei parti, si a treia conteaza cel mai mult: blocajul se ia INAINTE de
            # orice · `asigura_tabel` nu mai comite pe calea asta · iar la CAPATUL sectiunii se cere
            # dovada ca blocajul mai e tinut. Fara a treia, orice apel viitor care comite ar putea
            # desface serializarea la fel de tacut.
            _instante.blocaj_pornire(conn)
            _instante.aplica_ddl(conn)
            migrare_api.asigura_tabel(conn, comite=False)
            # [P1] tabelele rezultatului persistat al supervizorului. Idempotent (CREATE IF NOT
            # EXISTS), langa migrarea existenta, cu aceeasi purtare la esec.
            from core import supervizor_cache as _sc_boot
            _sc_boot.aplica_ddl(conn)
            # [P6 val 1, 12.09.2026] Tabelele starii business scoase din memoria procesului.
            # In blocul FAIL-CLOSED deliberat: fara ele, blocarea la autentificare n-ar mai
            # exista, iar o poarta de securitate care lipseste in TACERE e mai rea decat un
            # serviciu care refuza sa porneasca.
            from core import stare_partajata as _sp_boot
            _sp_boot.aplica_ddl(conn)
            # [P2-remediere 08.09.2026] Modelul de citire al portofoliului: tabelele, functiile de
            # trigger si registrul aspect->sursa.
            from core import firma_rezumat as _fr_boot
            _fr_boot.aplica_ddl(conn)
            # Triggerele, pentru TOTI tenantii existenti — nu doar pentru cei noi. Idempotent
            # (DROP IF EXISTS + CREATE), deci o pornire care le gaseste puse nu schimba nimic.
            _mig = _fr_boot.migreaza_triggerele(conn)
            if _mig["esecuri"]:
                for _e in _mig["esecuri"]:
                    _log_boot.error(
                        "[P2] triggere nelegate — tenant_id=%s schema=%s: %s%s%s",
                        _e.get("tenant_id"), _e.get("schema"), _e.get("exceptie"),
                        chr(10), _e.get("traceback", ""))
                raise RuntimeError(
                    "[P2] infrastructura de invalidare INCOMPLETĂ pentru %d firme din %d — "
                    "aplicația nu pornește. Fără triggere, rezumatele acelor firme n-ar mai fi "
                    "invalidate niciodată, iar ecranele le-ar arăta drept curente."
                    % (len(_mig["esecuri"]), _mig["firme"] + len(_mig["esecuri"])))
            # VERIFICAREA de după migrare: că `CREATE TRIGGER` n-a ridicat excepție NU e destul.
            _ver = _fr_boot.verifica_infrastructura(conn)
            if not _ver["ok"]:
                for _p in _ver["probleme"]:
                    _log_boot.error("[P2] infrastructură incompletă [%s]: %s | %s",
                                    _p["cod"], _p["diagnostic"], _p["ce"])
                raise RuntimeError(
                    "[P2] verificarea infrastructurii a picat (%d probleme): %s | detaliu: %s"
                    % (len(_ver["probleme"]),
                       " · ".join("%s: %s" % (p["cod"], p["diagnostic"]) for p in _ver["probleme"]),
                       _ver["detaliu"]))
            _log_boot.info("[P2] infrastructură verificată: %s", _ver["detaliu"])
            # [R61 / P5 val 1b] Unicitatea raportului Z, impusă în BAZĂ pe toate firmele
            # existente — nu doar pe cele create de acum înainte din template. Aceeași
            # purtare ca migrarea de mai sus: fiecare firmă în savepointul ei, iar un eșec
            # oprește pornirea. NIMIC nu se șterge: dacă o firmă are deja duplicate,
            # `CREATE UNIQUE INDEX` pică pe ea, iar mesajul le NUMEȘTE.
            _mz = _raport_z.migreaza(conn)
            if _mz["esecuri"]:
                for _e in _mz["esecuri"]:
                    _log_boot.error("[R61] index Z nelegat — tenant_id=%s schema=%s: %s%s%s",
                                    _e.get("tenant_id"), _e.get("schema"),
                                    _e.get("exceptie"), chr(10), _e.get("traceback", ""))
                raise RuntimeError(_raport_z.mesaj_esec(_mz))
            _vz = _raport_z.verifica(conn)
            if not _vz["ok"]:
                raise RuntimeError("[R61] verificarea indexului Z a picat: %s | lipsă pe: %s"
                                   % (_vz["detaliu"], _vz["lipsa"]))
            _log_boot.info("[R61] unicitate raport Z: %s", _vz["detaliu"])

            # [P6 val 3, 12.09.2026] Procesul intra in registru ABIA ACUM, in aceeasi tranzactie
            # cu verificarile de mai sus: daca vreuna pica, inregistrarea se intoarce odata cu ele.
            # *Un proces care n-a terminat verificarea nu are voie sa apara ca viu* — altfel bratul
            # four-way ar numara un proces care tocmai refuza sa porneasca.
            from core import versiune as _versiune_reg
            # [P6 val 3 reparatie, 12.09.2026] DOVADA, nu presupunerea: sectiunea critica s-a
            # terminat cu blocajul inca in mana. Daca ceva l-a eliberat pe drum, pornirea pica aici
            # — in acelasi bloc fail-closed cu celelalte verificari, nu cu un avertisment in log.
            _instante.confirma_blocaj(conn)
            _instante.inregistreaza(conn, _versiune_reg.RUNNING_COMMIT)
            _log_boot.info("[P6] instanta inregistrata: %s pid=%s commit=%s",
                           _instante.eu()[0], _instante.eu()[1],
                           (_versiune_reg.RUNNING_COMMIT or "?")[:8])
    except Exception:
        _log_boot.exception(
            "[P2] INFRASTRUCTURA CRITICĂ nu s-a putut instala sau verifica — aplicația REFUZĂ să "
            "pornească. O aplicație care nu poate garanta prospețimea read-modelului nu are voie "
            "să servească trafic: ar arăta valori vechi ca fiind curente, tăcut.")
        raise

    # ── TASKURILE DE FUNDAL, ABIA ACUM ──────────────────────────────────────
    # [POST-P2 HARDENING, 09.09.2026] Bucla de sănătate pornea ÎNAINTE de blocul critic de mai
    # sus. Nu era un defect de corectitudine — startup-ul e fail-closed, deci un eșec tot oprea
    # pornirea —, dar era o ordine care nu se poate apăra: un task de fundal se lega de o bază
    # despre care încă nu se știa dacă poartă infrastructura P2, iar la eșec rămânea pornit câteva
    # sute de milisecunde peste un proces care murea. *Ordinea corectă e: deschizi resursele,
    # instalezi, VERIFICI, și abia dacă totul a trecut pornești ce rulează singur.*
    import asyncio as _asyncio_lifespan  # ICRD_LIFESPAN_ALERTE_V1
    _asyncio_lifespan.create_task(_bucla_alerte_sanatate())
    global _TASKURI_FUNDAL_PORNITE
    _TASKURI_FUNDAL_PORNITE += 1
    try:
        with open(TENANT_TEMPLATE_PATH, encoding="utf-8") as f:
            _uc_comun.pune_sablon_tenant(f.read())
    except FileNotFoundError:
        _uc_comun.pune_sablon_tenant(None)   # creare tenant va da eroare clară până e pus
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
_uc_comun.pune_static_dir(_STATIC_DIR)   # [P7 · lotul 2] HTTP alege, use-case consuma
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
            r = _repo.select_u(cur, ctx)
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
                _repo.insert_public(cur, uid, tenant_id, actiune, _json_audit, status)
    except Exception as _e:
        _obs.esec_secundar("audit_log activitate", _e)  # inghitit, dar nu tacut (27.07.2026)

_METODE_MUTATIE = ("POST", "PUT", "DELETE", "PATCH")


@app.middleware("http")
async def _preview_readonly_guard(request: Request, call_next):
    """[F-preview] Read-only enforcement pe BACKEND: un token de PREVIZUALIZARE portal blocheaza
    orice mutatie (POST/PUT/DELETE/PATCH -> 403); GET permis. La nivel de request (nu ascuns butoane
    in UI - UI-ul se ocoleste). Tokenul preview e emis de /tenants/{id}/acces-portal, marcat preview=True."""
    _crono.marca("mw_audit_intrare")
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
    _crono.marca("mw_edge")
    response = await call_next(request)
    _crono.marca("intors_din_ruta")
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
    # [P5, 10.09.2026] CEL MAI DIN AFARĂ middleware, deci aici pornește cronometrul. Inert fără
    # `ICONTA_CRONOMETRU=1`. Ordinea lanțului e citită din urma unei excepții, nu presupusă:
    # `_edge_canonic_head` -> `_audit_middleware` -> `_preview_readonly_guard` -> rută.
    _crono.porneste()
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
#: [P6 val 3, 12.09.2026] Cate conexiuni sunt NORMALE nu mai e un numar ales, e o consecinta:
#: fiecare worker isi tine pool-ul lui. Era `20`, scris cand exista un singur proces cu pool maxim
#: 10 — iar la doi workeri ar fi devenit o ALARMA FALSA PERMANENTA, fiindca 2 x 10 atinge pragul
#: din prima clipa, cu aplicatia complet inactiva. Nu e o ipoteza: zborul de proba de pe portul
#: 8011 a pornit chiar o alerta (inerta, fiindca rulase fara cheia Brevo, dinadins).
#:
#: LA UN SINGUR WORKER FORMULA DA TOT 20. Adica schimbarea nu misca purtarea de azi — o face doar
#: sa se tina singura cand numarul de procese creste. `WEB_CONCURRENCY` e aceeasi variabila pe care
#: o citeste uvicorn pentru `--workers` (verificat empiric, nu presupus), deci numarul de instante
#: are UN singur loc unde e scris.
_WORKERI = max(1, int(os.environ.get("WEB_CONCURRENCY") or 1))
_PRAG_CONEXIUNI_DB = _WORKERI * db.config_din_env()["maxconn"] + 10
_ALERTE_COOLDOWN_SEC = 3600

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
                rezultat["conexiuni_db"] = _repo.select_pg_stat_activity(cur)[0]
                rezultat["erori_noi"] = _repo.select_public(cur)[0]
    except Exception as _e:
        _obs.esec_secundar("metrici sanatate: citire", _e)  # inghitit, dar nu tacut (27.07.2026)
    return rezultat

def _email_superadmin():
    try:
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                r = _repo.select_public_2(cur)
        return r[0] if r else None
    except Exception as _e:
        _obs.esec_secundar("email superadmin", _e)  # inghitit, dar nu tacut (27.07.2026)
        return None

def _poate_alerta(categorie):
    """REZERVA dreptul de a trimite alerta din categoria asta. `True` = trimite TU.

    [P6 val 1, 12.09.2026] Era un dictionar de modul, deci pragul de o ora se aplica de N ori cu
    N procese: aceeasi alerta pleca de N ori. E o rezervare si acum — ca inainte, apelul care
    raspunde `True` scrie si marca de timp —, dar intrebarea si scrierea sunt o SINGURA
    instructiune atomica in baza, deci din doua procese care incearca simultan castiga exact unul.

    La baza cazuta raspunde `False` si CONSEMNEAZA. Fara rezervare nu putem sti ca alt proces nu
    trimite chiar acum, iar a trimite «ca sa fim siguri» e chiar defectul pe care valul il inchide.
    Consecinta, declarata: cat timp baza e jos, alertele nu pleaca — semnalul pentru asta e
    deadman-ul de cron, care nu trece pe aici.
    """
    try:
        with db.get_conn() as conn:
            return _stare_part.rezerva_alerta(conn, categorie, _ALERTE_COOLDOWN_SEC)
    except Exception as _e:
        _obs.esec_secundar("rezervare alerta %s" % categorie, _e)  # inghitit, dar nu tacut
        return False

def _verifica_drift_p2():
    """[POST-P2 HARDENING] Driftul infrastructurii P2, verificat periodic și **read-only**.

    `verifica_infrastructura` apără momentul pornirii. Dacă după aceea cineva rulează
    `DROP TRIGGER` — o migrare externă, o mână pe `psql` —, aplicația ar afla abia la următoarea
    repornire, iar între timp rezumatele acelei firme ar rămâne `curent` fără ca nimic să le mai
    invalideze.

    **Detectează și alertează; NU repară.** O buclă care ar recrea singură triggerele ar șterge
    chiar semnalul: driftul ar dispărea din log, iar cauza n-ar mai fi căutată de nimeni.

    Rulează în bucla de sănătate care există deja (la 5 minute), **niciodată în calea de cerere**:
    o verificare per cerere ar întreba catalogul de zeci de ori pe secundă — exact felul de muncă
    pe care P2 a scos-o din cererea interactivă."""
    from core import firma_rezumat as _fr_h
    try:
        with db.get_conn() as conn:
            st = _fr_h.verifica_drift(conn)
    except Exception as _e:
        _obs.esec_secundar("verificare drift P2", _e)   # înghițit, dar nu tăcut
        return None
    if st["ok"] is False and _poate_alerta("p2_infrastructura"):
        return ("Infrastructura P2 a derivat: %s"
                % " · ".join("%s %s" % (p["cod"], p["ce"]) for p in st["probleme"]))
    return None


def _verifica_si_alerta():
    m = _citeste_metrici_pentru_alerte()
    alerte = []
    _drift = _verifica_drift_p2()
    if _drift:
        alerte.append(_drift)
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
                _repo.insert_public_2(cur, m)
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

def _ciclu_sanatate():
    """Un ciclu al buclei de sanatate, cu mai multe procese in minte.

    [P6 val 3, 12.09.2026] Se despart doua lucruri care pana azi erau unul singur:
      · BATAIA si curatenia registrului se fac din FIECARE worker. Un registru care ar bate numai
        pentru lider ar declara moarte toate celelalte instante, iar bratul four-way ar raporta
        ca poarta HEAD un singur proces din patru.
      · MUNCA — metricile, verificarea de drift, alertele — o face DOAR liderul. Cu N workeri,
        `_verifica_si_alerta` ar scrie N randuri in `metrici_sanatate` la fiecare 5 minute si ar
        intreba catalogul de N ori. Alertele n-ar pleca de N ori (cooldownul e global din valul 1),
        dar munca s-ar face degeaba.

    Liderul se alege prin LEASE, nu prin `pg_try_advisory_lock`: acela s-ar lega de o CONEXIUNE,
    iar conexiunile vin dintr-un pool si se rotesc. Un lease expira singur, deci daca liderul moare
    urmatorul il preia fara ca nimeni sa curete nimic.
    """
    with db.get_conn() as conn:
        _instante.bate(conn)
        _instante.curata(conn)
        # [12.09.2026] Perechea lui `curata` pentru LEASE. Fara ea, dupa o repornire lease-ul
        # ramanea pe procesul mort pana la expirare (900 s), iar in tot acel timp munca de fundal
        # nu se facea deloc — masurat pe productie de doua ori. Bucla ruleaza un ciclu CHIAR LA
        # pornire, deci fereastra fara lider devine durata unei reporniri, nu un sfert de ora.
        _instante.retrage_liderul_mort(conn, "sanatate")
        sunt_lider = _instante.cere_lider(conn, "sanatate")
    if sunt_lider:
        _verifica_si_alerta()


async def _bucla_alerte_sanatate():
    import asyncio as _asyncio
    while True:
        try:
            await _run_in_threadpool_audit(_ciclu_sanatate)
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
    try:
        return _uc_admin.admin_sanatate_istoric(ore, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.get("/admin/sanatate")
def admin_sanatate(ctx=Depends(cere_cabinet)):
    try:
        return _uc_admin.admin_sanatate(ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

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
    try:
        return _uc_admin.admin_anunt_creeaza(date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.get("/admin/alerte-fiscale")  # [F103 partea 2] propunerile monitorului pentru anunturi
def admin_alerte_fiscale(ctx=Depends(cere_rol("superadmin"))):
    try:
        return _uc_admin.admin_alerte_fiscale(ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)
@app.post("/admin/alerte-fiscale/{aid}/tratat")  # [F103 partea 2]
def admin_alerta_tratata(aid: int, ctx=Depends(cere_rol("superadmin"))):
    try:
        return _uc_admin.admin_alerta_tratata(aid, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)
@app.get("/eu/anunturi")
def eu_anunturi(ctx=Depends(cere_cabinet)):
    try:
        return _uc_eu.eu_anunturi(ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/eu/anunturi/{aid}/confirma")
def eu_anunt_confirma(aid: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_eu.eu_anunt_confirma(aid, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.get("/admin/activitate/cabinete")
def admin_activitate_cabinete(ctx=Depends(cere_cabinet)):
    try:
        return _uc_admin.admin_activitate_cabinete(ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/admin/cabinete/{firm_id}/suspenda")
def admin_cabinet_suspenda(firm_id: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_admin.admin_cabinet_suspenda(firm_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/admin/cabinete/{firm_id}/reactiveaza")
def admin_cabinet_reactiveaza(firm_id: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_admin.admin_cabinet_reactiveaza(firm_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.get("/admin/activitate/cabinet/{firm_id}")
def admin_activitate_cabinet(firm_id: int, limita: int = 200, ctx=Depends(cere_cabinet)):
    try:
        return _uc_admin.admin_activitate_cabinet(firm_id, limita, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


class StergereCabinetIn(BaseModel):
    confirmare: str


class CerereStergereIn(BaseModel):  # [F200b] cabinetul DEPUNE o cerere; NU executa
    confirmare_nume: str
    motiv: Optional[str] = None


@app.post("/gdpr/sterge-cabinet/{cabinet_id}/previzualizare")  # [F200] GDPR art.17 pas 1 (superadmin)
def gdpr_sterge_previzualizare(cabinet_id: int, ctx=Depends(cere_rol("superadmin"))):
    try:
        return _uc_gdpr.gdpr_sterge_previzualizare(cabinet_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/gdpr/sterge-cabinet/{cabinet_id}/executa")  # [F200] GDPR art.17 pas 2 (superadmin, confirmare typed-back)
def gdpr_sterge_executa(cabinet_id: int, date: StergereCabinetIn, ctx=Depends(cere_rol("superadmin"))):
    try:
        return _uc_gdpr.gdpr_sterge_executa(cabinet_id, date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/gdpr/export-cabinet")  # [F199] GDPR art.20 portabilitate — export complet cabinet
def gdpr_export_cabinet(cabinet_id: Optional[int] = None, ctx=Depends(cere_rol("admin_firma"))):
    try:
        _zip, cab = _uc_gdpr.gdpr_export_cabinet(cabinet_id, ctx)
        return Response(content=_zip, media_type="application/zip",
                        headers={"Content-Disposition": 'attachment; filename="gdpr-export-cabinet-%s.zip"' % cab})
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/gdpr/cerere-stergere")  # [F200b] GDPR art.17 — cabinetul DEPUNE o cerere; superadmin executa. NU sterge nimic.
def gdpr_cerere_stergere(date: CerereStergereIn, ctx=Depends(cere_rol("admin_firma"))):
    try:
        return _uc_gdpr.gdpr_cerere_stergere(date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/capacitate")  # [p70_capacitate] panou capacitate (doar patron)
def capacitate_panou(ctx=Depends(cere_rol("admin_firma"))):
    try:
        return _uc_capacitate.capacitate_panou(ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.get("/tipare")  # [p72_tipare] educatie pe tipare (doar patron)
def tipare_panou(ctx=Depends(cere_rol("admin_firma"))):
    try:
        return _uc_tipare.tipare_panou(ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/tipare/ai")  # [F120] analiza generativa AI peste tiparele de respingere (doar patron)
def tipare_ai_panou(ctx=Depends(cere_rol("admin_firma"))):
    try:
        return _uc_tipare.tipare_ai_panou(ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


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
# [R138] Faptul „ce e o adresa de email" traieste in `core/common`, nu aici. Numele vechi
# ramane, ca sa nu se schimbe apelantul, dar nu mai poarta el definitia.
# [login_lockout_v1] esecuri per CONT (email); per-IP ramane la nginx (iconta_auth 5r/m).
# [P6 val 1, 12.09.2026] Era `_login_fail = {}`, un dictionar la nivel de modul. Purta o DECIZIE
# DE SECURITATE — blocarea unui cont — care se pierdea la fiecare repornire si pe care al doilea
# proces n-o vedea (masurat: cinci esecuri pe A, `blocat=False` pe B). Iar `_login_blocat` facea
# CITESTE-FILTREAZA-SCRIE peste acelasi dictionar, deci esecurile concurente se pierdeau unul pe
# altul: 4326 din 5000 la k=10 fire x 500 runde. Acum: un RAND per esec, un COUNT cu fereastra in
# `WHERE`. Contractul e acelasi — cinci esecuri in cincisprezece minute.
# Fiecare functie isi deschide tranzactia EI, scurta. Loginul deschide oricum conexiuni separate
# pentru autentificare si pentru audit; una tinuta peste toti pasii ar fi exact clasa C5.
def _login_blocat(email):
    """[P7 · use-case] Invelisul HTTP al lui `core/uc_comun._login_blocat` — traduce refuzul de
    domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._login_blocat(email)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)
def _login_esec(email):
    """[P7 · use-case] Invelisul HTTP al lui `core/uc_comun._login_esec` — traduce refuzul de
    domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._login_esec(email)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)
def _login_reset(email):
    """[P7 · use-case] Invelisul HTTP al lui `core/uc_comun._login_reset` — traduce refuzul de
    domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._login_reset(email)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/auth/login")
def login(date: LoginIn):
    try:
        return _uc_auth.login(date)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/auth/register")
def register(date: RegisterIn):
    try:
        return _uc_auth.register(date)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


# ============================================================
#  TENANȚI — firmele la care userul are acces
# ============================================================
@app.get("/tenants")
def tenants(inactive: bool = False, ctx=Depends(cere_cabinet)):
    """`inactive=true` cuprinde ȘI firmele dezactivate — altfel o firmă dezactivată ar ieși din
    listă fără nicio cale de întoarcere. [R72]"""
    try:
        return _uc_tenants.tenants(inactive, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/firme-scoase")
def firme_scoase(ctx=Depends(cere_cabinet)):
    """[R72] Urma firmelor scoase din portofoliu — CITITĂ, nu doar scrisă.

    Fără ruta asta, `public.firme_scoase` ar fi a doua instanță, în aceeași zi, a clasei
    declarate dimineață la `urme-portal`: *scrisă, necitită de om*. După o ștergere, ea e
    singura dovadă că firma a existat.
    """
    try:
        return _uc_firme_scoase.firme_scoase(ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/tenants/{tenant_id}/scoatere")
def tenant_scoatere_previzualizare(tenant_id: int, ctx=Depends(cere_cabinet)):
    """[R72] Ce se întâmplă dacă firma se scoate: are evidență sau nu, și ce anume s-a găsit.
    Se citește ÎNAINTE de apăsare — un refuz care apare abia după apăsare e o surpriză."""
    try:
        return _uc_tenants.tenant_scoatere_previzualizare(tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


class FirmaActivareIn(BaseModel):
    activ: bool


def _acces_pentru_activare(conn, rol, firm, tenant_id):
    """[P7 · use-case, lotul 2] Invelisul HTTP al lui `core/uc_comun._acces_pentru_activare` — traduce
    refuzul de domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._acces_pentru_activare(conn, rol, firm, tenant_id)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


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
    try:
        return _uc_tenants.tenant_activare(tenant_id, date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


class NumeAlesIn(BaseModel):
    alege: str


@app.post("/tenants/{tenant_id}/nume-ales")
def tenant_nume_ales(tenant_id: int, date: NumeAlesIn, ctx=Depends(cere_rol("admin_firma"))):
    """[R77] Alegerea între denumirea din aplicație și cea de la ANAF. **Amândouă** ramurile scriu:
    a păstra pe a ta e un act, nu absența unuia."""
    try:
        return _uc_tenants.tenant_nume_ales(tenant_id, date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.delete("/tenants/{tenant_id}")
def tenant_scoate(tenant_id: int, confirmare: str = "", ctx=Depends(cere_rol("admin_firma"))):
    """[R72] Scoate din portofoliu o firmă FĂRĂ evidență. Confirmarea e CUI-ul, nu numele:
    instanța care a produs restanța sunt două firme cu ACELAȘI nume."""
    try:
        return _uc_tenants.tenant_scoate(tenant_id, confirmare, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/tenants/{tenant_id}")
def tenant_detalii(tenant_id: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.tenant_detalii(tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants")
def tenant_creeaza(date: TenantNou, ctx=Depends(cere_rol("admin_firma"))):
    try:
        return _uc_tenants.tenant_creeaza(date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


# [client_acces_v1] acces client la portal: creare cont + email cu parola temporara
class ClientAccesIn(BaseModel):
    email: str
    nume: str = ""
    mesaj: str = ""  # client_mesaj_v1

@app.get("/tenants/{tenant_id}/client-acces")
def client_acces_lista(tenant_id: int, ctx=Depends(cere_rol("admin_firma", "angajat"))):
    try:
        return _uc_tenants.client_acces_lista(tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/tenants/{tenant_id}/client-acces")
def client_acces_creeaza(tenant_id: int, date: ClientAccesIn,
                         ctx=Depends(cere_rol("admin_firma"))):
    try:
        return _uc_tenants.client_acces_creeaza(tenant_id, date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

class ActivareIn(BaseModel):
    token: str
    parola: str

# === MAGIC LINK === # magic_link_v1
# [token_hash_v1] Tokenurile de acces (magic-link + activare) se stocheaza DOAR ca hash sha256:
# un dump/backup nu mai permite impersonarea. Clarul traieste doar in link (email). Mecanica = ca la reset.
def _hash_tok(t):
    """[P7 · use-case] Invelisul HTTP al lui `core/uc_comun._hash_tok` — traduce refuzul de
    domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._hash_tok(t)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

def _pune_token(cur, tok, user_id, interval_sql):
    """[P7 · use-case] Invelisul HTTP al lui `core/uc_comun._pune_token` — traduce refuzul de
    domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._pune_token(cur, tok, user_id, interval_sql)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

class MagicCereIn(BaseModel):
    email: str

from core.uc_comun import _TERMENI_PATH  # noqa: E402  [P7 lot 2] definitia a plecat in use-case

def _termeni_versiune(txt):
    """[P7 · use-case] Invelisul HTTP al lui `core/uc_comun._termeni_versiune` — traduce refuzul de
    domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._termeni_versiune(txt)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

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
from core.uc_comun import _magic_rate  # noqa: E402  [P7 lot 2] definitia a plecat in use-case  # [magic_link_v1] rate-limit per IP pt /public/magic-link (aceleasi praguri ca reset)
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
    try:
        return _uc_public.reset_parola_cere(date)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/public/reset-parola/seteaza")  # [reset_parola_v1] valideaza tokenul (single-use), seteaza parola, invalideaza sesiunile
def reset_parola_seteaza(date: ResetSeteazaIn):
    try:
        return _uc_public.reset_parola_seteaza(date)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/public/magic-link")
def magic_link_cere(date: MagicCereIn, request: Request):
    """Trimite link de logare fara parola. Raspuns identic indiferent daca emailul exista (fara enumerare)."""
    _rate_limit_email(_magic_rate, request)
    try:
        return _uc_public.magic_link_cere(date)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

class MagicLoginIn(BaseModel):
    token: str

@app.post("/public/magic-login")
def magic_login(date: MagicLoginIn):
    try:
        return _uc_public.magic_login(date)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/public/activare")
def activare_cont(date: ActivareIn):
    try:
        return _uc_public.activare_cont(date)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.delete("/tenants/{tenant_id}/client-acces/{user_id}")
def client_acces_revoca(tenant_id: int, user_id: int, ctx=Depends(cere_rol("admin_firma"))):
    try:
        return _uc_tenants.client_acces_revoca(tenant_id, user_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/acces-portal")  # [F-preview] previzualizare portal client din cabinet
def acces_portal_preview(tenant_id: int, ctx=Depends(cere_rol("admin_firma", "angajat"))):
    """Emite un token de PREVIZUALIZARE (read-only, tab-local) pentru portalul clientului firmei.
    Cabinetul vede exact ce vede clientul, fara sa poata scrie (guard pe backend, nu doar UI).
    Necesita un cont de client al firmei (rol=client in user_tenants); daca nu exista -> 400 cu indrumare."""
    try:
        return _uc_tenants.acces_portal_preview(tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.put("/tenants/{tenant_id}")
def tenant_actualizeaza(tenant_id: int, date: TenantEdit,                         ctx=Depends(cere_rol("admin_firma"))):
    try:
        return _uc_tenants.tenant_actualizeaza(tenant_id, date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


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
def migrare_fisier(fisier: UploadFile = File(...), ctx=Depends(cere_cabinet)):
    """Primește un CSV/XLSX, extrage CUI-urile și le validează la ANAF."""
    continut = _octetii(fisier)
    try:
        cui_uri = anaf_api.extrage_cui_din_fisier(continut, fisier.filename or "")
    except Exception as e:
        raise HTTPException(400, f"fișier ilizibil: {e}")
    if not cui_uri:
        # [lotul 6] „0 rezultate" arata identic cu „fisierul n-a fost citit".
        raise HTTPException(422, "Din fișierul %s n-am putut citi niciun cod fiscal. "
                                 "Se așteaptă un CSV sau un XLSX cu o coloană de CUI-uri "
                                 "— un fișier necitit nu e un fișier gol."
                                 % (fisier.filename or "trimis",))
    try:
        rez = anaf_api.valideaza_cui(cui_uri)
    except Exception as e:
        raise HTTPException(502, f"ANAF indisponibil sau a refuzat cererea: {e}")
    return {"rezultate": rez}


@app.post("/migrare/incarca")
def migrare_incarca(fisier: UploadFile = File(...), ctx=Depends(cere_cabinet)):
    """Primește un fișier (.csv/.xlsx), extrage CUI-urile și le validează la ANAF."""
    continut = _octetii(fisier)
    try:
        cui_uri = anaf_api.extrage_cui_din_fisier(continut, fisier.filename or "")
    except ValueError as e:
        raise HTTPException(400, str(e))
    if not cui_uri:
        # [lotul 6] idem — aceeasi clasa, a doua cale.
        raise HTTPException(422, "Din fișierul %s n-am putut citi niciun cod fiscal. "
                                 "Se așteaptă un CSV sau un XLSX cu o coloană de CUI-uri "
                                 "— un fișier necitit nu e un fișier gol."
                                 % (fisier.filename or "trimis",))
    try:
        rez = anaf_api.valideaza_cui(cui_uri)
    except Exception as e:
        raise HTTPException(502, f"ANAF indisponibil sau a refuzat cererea: {e}")
    return {"rezultate": rez, "extrase": len(cui_uri)}


@app.post("/migrare/importa")
def migrare_importa(date: MigrareImportaIn, ctx=Depends(cere_rol("admin_firma"))):
    """Creează câte un tenant pentru fiecare firmă selectată. Sare peste CUI-uri deja în portofoliu."""
    try:
        return _uc_migrare.migrare_importa(date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/migrare/status")
def migrare_status_citeste(ctx=Depends(cere_cabinet)):
    """Starea fiecărui strat de migrare + reminderul (straturi în lucru)."""
    try:
        return _uc_migrare.migrare_status_citeste(ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/migrare/straturi")
def migrare_straturi_aplicabile(tip_firma: str = "srl", ctx=Depends(cere_cabinet)):
    # [lotul 6] `tip_firma=ceva-ce-nu-exista` intorcea lista INTREAGA de straturi, ca si cum ar fi
    # raspunsul pentru tipul ala. Un nomenclator nerecunoscut nu se rotunjeste la „toate".
    _TIPURI_FIRMA = ("srl", "pfa", "ii", "ong", "sa")
    if tip_firma not in _TIPURI_FIRMA:
        raise HTTPException(422, nomenclator_cerut("tip_firma", _TIPURI_FIRMA))
    """[p_pfa_rip 20.07] Straturile de migrare aplicabile unui regim (srl/pfa).
    Sursa unica de adevar = migrare_api.straturi_pentru (filtreaza pe STRATURI_META),
    ca meniul per-firma sa nu reinventeze in JS ce strat apartine carui regim."""
    return {"straturi": migrare_api.straturi_pentru(tip_firma)}


@app.post("/migrare/status")
def migrare_status_seteaza(date: MigrareStatusIn, ctx=Depends(cere_rol("admin_firma"))):
    """Marchează un strat 'gata' sau 'in_lucru' (cu notă obligatorie la in_lucru)."""
    try:
        return _uc_migrare.migrare_status_seteaza(date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


# ============================================================
#  MIGRARE STRAT 2 — SOLDURI INIȚIALE (per firmă)
# ============================================================

# [P2, 08.09.2026] CITIREA PORTOFOLIULUI — o singură interogare, indiferent câte firme.
# Măsurat înainte: cele trei rute de mai jos făceau 2 conexiuni și 3–4 interogări PER FIRMĂ
# (la 1000 de firme: ~2.000 de conexiuni, 3.000–4.000 de interogări, ~1 s fiecare).
def _portofoliu_din_model(ctx, aspect, implicit):
    """`[(firma, date, prospetime)]` pentru firmele utilizatorului, dintr-un singur `SELECT`.

    `implicit` e valoarea arătată când rezumatul lipsește — și **nu tace**: prospețimea spune
    `lipseste`, deci ecranul poate arăta că firma așteaptă recalcularea, nu o valoare inventată."""
    from core import firma_rezumat as _fr
    with db.get_conn() as conn:
        firme = auth_api.tenantii_userului(conn, ctx["uid"])
        ids = [f.get("id") for f in firme]
        model = _fr.citeste(conn, ids, [aspect])
    out = []
    for f in firme:
        st = (model.get(f.get("id")) or {}).get(aspect) or {
            "date": None, "stare": _fr.LIPSESTE, "calculat_la": None,
            "versiune_sursa": None, "versiune_curenta": 0}
        out.append((f, dict(st.get("date") or implicit),
                    {"stare": st["stare"], "calculat_la": st["calculat_la"]}))
    return out

@app.get("/migrare/solduri")
def migrare_solduri_status(ctx=Depends(cere_cabinet)):
    """Lista firmelor cabinetului cu status solduri (are/n-are, câte conturi)."""
    out = []
    for f, d, prosp in _portofoliu_din_model(ctx, "solduri",
                                             {"are_solduri": False, "randuri": 0}):
        out.append({"tenant_id": f.get("id"), "nume": f.get("nume"), "cui": f.get("cui"),
                    "are_solduri": bool(d.get("are_solduri")), "randuri": d.get("randuri") or 0,
                    "prospetime": prosp})
    return {"firme": out}

@app.get("/migrare/plan-conturi")  # [p95_plan_conturi] lista firmelor cu numar de conturi in plan
def migrare_plan_conturi_status(ctx=Depends(cere_cabinet)):
    out = []
    for f, d, prosp in _portofoliu_din_model(ctx, "plan_conturi", {"conturi": 0}):
        out.append({"tenant_id": f.get("id"), "nume": f.get("nume"), "cui": f.get("cui"),
                    "nr_conturi": d.get("conturi") or 0, "prospetime": prosp})
    return {"firme": out}
@app.get("/tenants/{tenant_id}/plan-conturi")  # [p95_plan_conturi] cauta/listeaza conturile firmei
def tenant_plan_conturi_lista(tenant_id: int, q: Optional[str] = None, ctx=Depends(cere_context)):
    try:
        return _uc_tenants.tenant_plan_conturi_lista(tenant_id, q, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)
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
def tenant_plan_conturi_adauga(tenant_id: int, date: PlanContIn,                                ctx=Depends(cere_rol("admin_firma"))):
    try:
        return _uc_tenants.tenant_plan_conturi_adauga(tenant_id, date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)
@app.get("/migrare/vector")  # [p84_vector_front] lista firmelor cu status vector fiscal
def migrare_vector_status(ctx=Depends(cere_cabinet)):
    """Lista firmelor cabinetului cu status vector (completat sau nu)."""
    out = []
    for f, d, prosp in _portofoliu_din_model(ctx, "vector", {"completat": False}):
        out.append({"tenant_id": f.get("id"), "nume": f.get("nume"), "cui": f.get("cui"),
                    "are_vector": bool(d.get("completat")),
                    "regim_fiscal": d.get("regim_fiscal"),
                    "regim_contabil": f.get("regim_contabil"),   # [regim] partida simpla/dubla -> ascunde regim la PFA
                    "platitor_tva": d.get("platitor_tva"),
                    "tip_decont": d.get("tip_decont"),
                    "operatiuni_ic": d.get("operatiuni_ic"),
                    "prospetime": prosp})
    return {"firme": out}


@app.post("/tenants/{tenant_id}/solduri/incarca")
def solduri_incarca(tenant_id: int, fisier: UploadFile = File(...), ctx=Depends(cere_cabinet)):
    """Parsează o balanță și întoarce preview (nu salvează)."""
    _schema_sau_404(ctx, tenant_id)
    continut = _octetii(fisier)
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
        return _raspuns(dict(_baza, motiv=motiv))
    return _raspuns(dict(_baza, **migrare_api.respinge(
        "balanță de deschidere", _Unde("fisier", fisier.filename or "(fără nume)"),
        "balanta_nu_se_echilibreaza", motiv)))


@app.get("/tenants/{tenant_id}/solduri")
def solduri_rezumat(tenant_id: int, ctx=Depends(cere_cabinet)):
    """Rezumatul soldurilor salvate pentru o firmă."""
    try:
        return _uc_tenants.solduri_rezumat(tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/solduri")
def solduri_salveaza(tenant_id: int, date: SolduriIn, ctx=Depends(cere_rol("admin_firma"))):
    """Salvează soldurile inițiale ale unei firme (înlocuiește ce era)."""
    try:
        return _uc_tenants.solduri_salveaza(tenant_id, date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


# ============================================================
#  MIGRARE STRAT 3 — SOLDURI PARTENERI (4111/401 per partener)
# ============================================================
@app.get("/migrare/parteneri")
def migrare_parteneri_status(ctx=Depends(cere_cabinet)):
    """[P3 val B, 09.09.2026] CITEȘTE MODELUL, nu portofoliul firmă cu firmă.

    Măsurat înainte: `q = 4 + 4N`, `c = 3 + 2N` — la 1000 de firme, 4.004 interogări și
    2.003 conexiuni. Bucla cerea schema per firmă (o conexiune) și o deschidea (încă una).

    **Nu e un cache.** Valoarea se calculează cu `firma_rezumat._parteneri`, care cheamă exact
    `solduri_parteneri_api.rezumat` — funcția pe care o chema ruta —, iar invalidarea vine din triggerul de pe
    `solduri_parteneri`. Prospețimea NU se stochează: se derivă comparând versiunea cu care s-a calculat
    cu versiunea de acum. O firmă fără rezumat primește `stare='lipseste'` și ecranul o arată ca
    **necunoscută**, nu ca „nu are" — un necunoscut nu se rotunjește la «știu că nu»."""
    out = []
    for f, d, prosp in _portofoliu_din_model(ctx, "parteneri", {"are_parteneri": False, "randuri": 0}):
        out.append({"tenant_id": f.get("id"), "nume": f.get("nume"), "cui": f.get("cui"),
                    "are_parteneri": bool(d.get("are_parteneri")), "randuri": d.get("randuri") or 0,
                    "prospetime": prosp})
    return {"firme": out}


@app.post("/tenants/{tenant_id}/parteneri/incarca")
def parteneri_incarca(tenant_id: int, fisier: UploadFile = File(...), ctx=Depends(cere_cabinet)):
    """Parseaza fisierul de parteneri si intoarce preview + verificare coerenta vs balanta."""
    try:
        return _uc_tenants.parteneri_incarca(tenant_id, _octetii(fisier), fisier.filename, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/tenants/{tenant_id}/parteneri")
def parteneri_rezumat(tenant_id: int, ctx=Depends(cere_cabinet)):
    """Rezumatul partenerilor salvati pentru o firma."""
    try:
        return _uc_tenants.parteneri_rezumat(tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/parteneri")
def parteneri_salveaza(tenant_id: int, date: ParteneriIn, ctx=Depends(cere_rol("admin_firma"))):
    """Salveaza soldurile partenerilor unei firme (inlocuieste ce era)."""
    try:
        return _uc_tenants.parteneri_salveaza(tenant_id, date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)



# ============================================================
#  MIGRARE STRAT 4 — SALARIATI (import din vechea aplicatie)
# ============================================================
@app.get("/migrare/salariati")
def migrare_salariati_status(ctx=Depends(cere_cabinet)):
    """[P3 val B, 09.09.2026] CITEȘTE MODELUL, nu portofoliul firmă cu firmă.

    Măsurat înainte: `q = 4 + 3N`, `c = 3 + 2N` — la 1000 de firme, 3.004 interogări și
    2.003 conexiuni. Bucla cerea schema per firmă (o conexiune) și o deschidea (încă una).

    **Nu e un cache.** Valoarea se calculează cu `firma_rezumat._salariati`, care cheamă exact
    `salariati_import_api.rezumat` — funcția pe care o chema ruta —, iar invalidarea vine din triggerul de pe
    `salariati`. Prospețimea NU se stochează: se derivă comparând versiunea cu care s-a calculat
    cu versiunea de acum. O firmă fără rezumat primește `stare='lipseste'` și ecranul o arată ca
    **necunoscută**, nu ca „nu are" — un necunoscut nu se rotunjește la «știu că nu»."""
    out = []
    for f, d, prosp in _portofoliu_din_model(ctx, "salariati", {"are_salariati": False, "randuri": 0}):
        out.append({"tenant_id": f.get("id"), "nume": f.get("nume"), "cui": f.get("cui"),
                    "are_salariati": bool(d.get("are_salariati")), "randuri": d.get("randuri") or 0,
                    "prospetime": prosp})
    return {"firme": out}


@app.post("/tenants/{tenant_id}/salariati-import/incarca")
def salariati_import_incarca(tenant_id: int, fisier: UploadFile = File(...), ctx=Depends(cere_cabinet)):
    """Parseaza exportul de salariati si intoarce preview cu validare CNP (nu salveaza)."""
    try:
        return _uc_tenants.salariati_import_incarca(tenant_id, _octetii(fisier), fisier.filename, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/salariati-import")
def salariati_import_salveaza(tenant_id: int, date: SalariatiImportIn, ctx=Depends(cere_rol("admin_firma"))):
    """Importa salariatii cu CNP valid (upsert pe CNP). Sare peste cei invalizi."""
    try:
        return _uc_tenants.salariati_import_salveaza(tenant_id, date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)



# ============================================================
#  MIGRARE STRAT 5 — ASOCIATI (pentru D205 / dividende)
# ============================================================
@app.get("/migrare/asociati")
def migrare_asociati_status(ctx=Depends(cere_cabinet)):
    """[P3 val B, 09.09.2026] CITEȘTE MODELUL, nu portofoliul firmă cu firmă.

    Măsurat înainte: `q = 4 + 3N`, `c = 3 + 2N` — la 1000 de firme, 3.004 interogări și
    2.003 conexiuni. Bucla cerea schema per firmă (o conexiune) și o deschidea (încă una).

    **Nu e un cache.** Valoarea se calculează cu `firma_rezumat._asociati`, care cheamă exact
    `asociati_import_api.rezumat` — funcția pe care o chema ruta —, iar invalidarea vine din triggerul de pe
    `asociati`. Prospețimea NU se stochează: se derivă comparând versiunea cu care s-a calculat
    cu versiunea de acum. O firmă fără rezumat primește `stare='lipseste'` și ecranul o arată ca
    **necunoscută**, nu ca „nu are" — un necunoscut nu se rotunjește la «știu că nu»."""
    out = []
    for f, d, prosp in _portofoliu_din_model(ctx, "asociati", {"are_asociati": False, "randuri": 0}):
        out.append({"tenant_id": f.get("id"), "nume": f.get("nume"), "cui": f.get("cui"),
                    "are_asociati": bool(d.get("are_asociati")), "randuri": d.get("randuri") or 0,
                    "prospetime": prosp})
    return {"firme": out}


@app.post("/tenants/{tenant_id}/asociati-import/incarca")
def asociati_import_incarca(tenant_id: int, fisier: UploadFile = File(...), ctx=Depends(cere_cabinet)):
    _schema_sau_404(ctx, tenant_id)
    continut = _octetii(fisier)
    try:
        randuri = asociati_import_api.extrage(continut, fisier.filename or "")
    except ValueError as e:
        raise HTTPException(400, str(e))
    coer = asociati_import_api.coerenta_cote(randuri)
    erori = migrare_api.erori_verifica(asociati_import_api.verifica_randuri(randuri))  # [Q5] poarta unica
    return _raspuns({"randuri": randuri, "total": len(randuri), "coerenta": coer, "erori": erori})


@app.post("/tenants/{tenant_id}/asociati-import")
def asociati_import_salveaza(tenant_id: int, date: AsociatiImportIn, ctx=Depends(cere_rol("admin_firma"))):
    try:
        return _uc_tenants.asociati_import_salveaza(tenant_id, date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)



# === IMPORT RETETE HORECA (F150) ===
class ReteteImportIn(BaseModel):
    retete: list[dict]
@app.post("/tenants/{tenant_id}/retete-import/incarca")
def retete_import_incarca(tenant_id: int, fisier: UploadFile = File(...), ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.retete_import_incarca(tenant_id, _octetii(fisier), fisier.filename, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)
@app.post("/tenants/{tenant_id}/retete-import")
def retete_import_salveaza(tenant_id: int, date: ReteteImportIn, ctx=Depends(cere_rol("admin_firma"))):
    try:
        return _uc_tenants.retete_import_salveaza(tenant_id, date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)
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
def articole_import_incarca(tenant_id: int, fisier: UploadFile = File(...), ctx=Depends(cere_cabinet)):
    _schema_sau_404(ctx, tenant_id)
    continut = _octetii(fisier)
    try:
        randuri = articole_import_api.extrage(continut, fisier.filename or "")
    except ValueError as e:
        raise HTTPException(400, str(e))
    return _raspuns({"randuri": randuri, "rezumat": articole_import_api.rezumat(randuri)})
@app.post("/tenants/{tenant_id}/articole-import")
def articole_import_salveaza(tenant_id: int, date: ArticoleImportIn, ctx=Depends(cere_rol("admin_firma"))):
    try:
        return _uc_tenants.articole_import_salveaza(tenant_id, date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)
# ============================================================
#  MIGRARE STRAT 6 — MIJLOACE FIXE (registru amortizare)
# ============================================================
@app.get("/migrare/mijloace-fixe")
def migrare_mijloace_status(ctx=Depends(cere_cabinet)):
    """[P3 val B, 09.09.2026] CITEȘTE MODELUL, nu portofoliul firmă cu firmă.

    Măsurat înainte: `q = 4 + 3N`, `c = 3 + 2N` — la 1000 de firme, 3.004 interogări și
    2.003 conexiuni. Bucla cerea schema per firmă (o conexiune) și o deschidea (încă una).

    **Nu e un cache.** Valoarea se calculează cu `firma_rezumat._mijloace_fixe`, care cheamă exact
    `mijloace_fixe_import_api.rezumat` — funcția pe care o chema ruta —, iar invalidarea vine din triggerul de pe
    `mijloace_fixe`. Prospețimea NU se stochează: se derivă comparând versiunea cu care s-a calculat
    cu versiunea de acum. O firmă fără rezumat primește `stare='lipseste'` și ecranul o arată ca
    **necunoscută**, nu ca „nu are" — un necunoscut nu se rotunjește la «știu că nu»."""
    out = []
    for f, d, prosp in _portofoliu_din_model(ctx, "mijloace_fixe", {"are_mijloace": False, "randuri": 0}):
        out.append({"tenant_id": f.get("id"), "nume": f.get("nume"), "cui": f.get("cui"),
                    "are_mijloace": bool(d.get("are_mijloace")), "randuri": d.get("randuri") or 0,
                    "prospetime": prosp})
    return {"firme": out}


@app.post("/tenants/{tenant_id}/mijloace-fixe-import/incarca")
def mijloace_import_incarca(tenant_id: int, fisier: UploadFile = File(...), ctx=Depends(cere_cabinet)):
    _schema_sau_404(ctx, tenant_id)
    continut = _octetii(fisier)
    try:
        randuri = mijloace_fixe_import_api.extrage(continut, fisier.filename or "")
    except ValueError as e:
        raise HTTPException(400, str(e))
    tv = round(sum(r["valoare"] for r in randuri), 2)
    tr = round(sum(r["rezidual"] for r in randuri), 2)
    cu_avert = sum(1 for r in randuri if not r["ok"])
    erori = migrare_api.erori_verifica(mijloace_fixe_import_api.verifica_randuri(randuri))  # [Q5] poarta unica
    return _raspuns({"randuri": randuri, "total": len(randuri), "total_valoare": tv,
            "total_rezidual": tr, "cu_avertismente": cu_avert, "erori": erori})


@app.post("/tenants/{tenant_id}/mijloace-fixe-import")
def mijloace_import_salveaza(tenant_id: int, date: MijloaceFixeImportIn, ctx=Depends(cere_rol("admin_firma"))):
    try:
        return _uc_tenants.mijloace_import_salveaza(tenant_id, date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)



# ============================================================
#  MIGRARE STRAT 7 — ISTORIC DECLARATII (ce s-a depus deja)
# ============================================================
@app.get("/migrare/istoric-declaratii")
def migrare_istoric_status(ctx=Depends(cere_cabinet)):
    """[P3, 09.09.2026] O SINGURĂ interogare pentru tot portofoliul, pe ACEEAȘI conexiune.

    Măsurat înainte: `q = 4 + 1*N`, `c = 3 + 1*N` — la 1000 de firme, 1.004 interogări și 1.003
    conexiuni, pentru o listă de stări. Bucla chema `rezumat()` per firmă, fiecare cu conexiunea
    ei din pool.

    **Nu e un cache și nu schimbă prospețimea:** se citește exact aceeași sursă
    (`public.declaratii_depuse`, `sursa = 'migrare'`), la fel de proaspăt, doar o dată.

    **Purtarea la eroare, păstrată.** Bucla veche prindea excepția *per firmă* și punea
    `{False, 0}`. O interogare unică nu poate eșua pentru o singură firmă — dacă eșuează,
    eșuează pentru toate —, iar atunci fiecare firmă primește exact valoarea pe care i-ar fi
    dat-o bucla veche în aceeași situație. *Se scrie aici fiindcă e singurul loc în care forma
    nouă nu e identică cu cea veche, ci echivalentă.*"""
    try:
        return _uc_migrare.migrare_istoric_status(ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/istoric-declaratii-import/incarca")
def istoric_import_incarca(tenant_id: int, fisier: UploadFile = File(...), ctx=Depends(cere_cabinet)):
    _schema_sau_404(ctx, tenant_id)
    continut = _octetii(fisier)
    try:
        randuri = istoric_declaratii_import_api.extrage(continut, fisier.filename or "")
    except ValueError as e:
        raise HTTPException(400, str(e))
    cu_avert = sum(1 for r in randuri if not r["ok"])
    erori = migrare_api.erori_verifica(istoric_declaratii_import_api.verifica_randuri(randuri))  # [Q5] poarta unica
    return _raspuns({"randuri": randuri, "total": len(randuri), "cu_avertismente": cu_avert, "erori": erori})


@app.post("/tenants/{tenant_id}/istoric-declaratii-import")
def istoric_import_salveaza(tenant_id: int, date: IstoricDeclImportIn, ctx=Depends(cere_rol("admin_firma"))):
    try:
        return _uc_tenants.istoric_import_salveaza(tenant_id, date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


# ============================================================
#  MIGRARE STRAT PFA — REGISTRU INCASARI/PLATI (RIP, partida simpla)
#  [p_pfa_rip 20.07] Preluarea unui PFA: istoric cronologic al anului curent,
#  NU balanta de deschidere (partida simpla nu are sold-rand separat).
# ============================================================
@app.post("/tenants/{tenant_id}/rip-import/incarca")
def rip_import_incarca(tenant_id: int, fisier: UploadFile = File(...), ctx=Depends(cere_rol("admin_firma"))):
    """
    Import registru incasari-plati la preluarea unui PFA. Parseaza fisierul, RAPORTEAZA
    randurile respinse (ambigue/incomplete) INAINTE de commit, apoi importa operatiunile
    valide intr-o tranzactie atomica (rip_migrare_api.importa) si marcheaza stratul 'rip'
    pentru reminder(): 'gata' daca nimic respins, 'in_lucru' cu nota daca au ramas randuri.
    """
    try:
        return _uc_tenants.rip_import_incarca(tenant_id, _octetii(fisier), fisier.filename, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)



# ============================================================
#  CONTROL FISCAL — semafor conformare per portofoliu
# ============================================================
def _flag_constatare(stare, eticheta, mesaj, temei, an, luna, remediu=None):
    """[P7 · use-case, lotul 2] Invelisul HTTP al lui `core/uc_comun._flag_constatare` — traduce
    refuzul de domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._flag_constatare(stare, eticheta, mesaj, temei, an, luna, remediu)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


from core.uc_comun import _LOG_VERDICT  # noqa: E402  [P7 lot 2] definitia a plecat in use-case


def _constatare_esuata(eticheta, nume, e, an, luna):
    """[P7 · use-case, lotul 2] Invelisul HTTP al lui `core/uc_comun._constatare_esuata` — traduce
    refuzul de domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._constatare_esuata(eticheta, nume, e, an, luna)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


def _verificator_esuat(contabil, eticheta, nume, e, an, luna):
    """[P7 · use-case, lotul 2] Invelisul HTTP al lui `core/uc_comun._verificator_esuat` — traduce
    refuzul de domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._verificator_esuat(contabil, eticheta, nume, e, an, luna)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


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
    """[P7 · use-case, lotul 2] Invelisul HTTP al lui `core/uc_comun._construieste_contabil` — traduce
    refuzul de domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._construieste_contabil(schema, tid, ctx, an, luna, regim_tva_anaf)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/control-fiscal")
def control_fiscal_portofoliu(ctx=Depends(cere_cabinet)):
    """Semafor pentru toate firmele cabinetului + sumar (verde/galben/rosu).

    [P2, 08.09.2026] CITEȘTE din modelul de citire — o singură interogare, indiferent câte firme.
    Măsurat înainte, la 1000 de firme, într-o singură cerere: **278.882 de interogări, 12.001 de
    conexiuni, 70,8 s**, fiindcă `_construieste_contabil` regenera D300/D112/D390 **per firmă**.
    Calculul n-a dispărut și n-a fost rescris — se face în `firma_rezumat.recalculeaza_greu`, o
    dată per firmă per schimbare.

    O firmă al cărei rezumat lipsește sau e învechit **nu tace și nu minte**: iese `gri`, cu
    `prospetime` care spune de ce. *O stare „în recalculare" declarată e acceptabilă; una veche și
    tăcută nu e.*
    """
    try:
        return _uc_control_fiscal.control_fiscal_portofoliu(ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/control-fiscal/{tenant_id}")
def control_fiscal_detaliu(tenant_id: int, ctx=Depends(cere_cabinet)):
    """Detaliu conformare pentru o firma: lista lipsa + de urmarit + constatari contabile."""
    try:
        return _uc_control_fiscal.control_fiscal_detaliu(tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


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
    try:
        return _uc_supervizor.supervizor_la_cerere(ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/control-fiscal/{tenant_id}/audit-preluare")
# [R45] POST: auditul e declansat de un buton, deci e un ACT — iar verdictul lui se pastreaza.
# Un GET n-are voie sa scrie (interdictia 6).
def control_fiscal_audit_preluare(tenant_id: int, ctx=Depends(cere_rol("admin_firma"))):
    """F183: audit de PRELUARE firma — coerenta INTERNA a pachetului preluat de la contabilul anterior
    (balanta echilibrata, defalcare parteneri vs sintetic, solduri fiscale vs istoric declaratii, RIP la
    PFA). Motor separat (core/audit_preluare), NU control_incrucisat: la preluare ambele surse sunt EXTERNE.
    Repetabil, datat cu momentul rularii — gri-urile trec in verde/rosu pe masura ce apar documentele."""
    try:
        return _uc_control_fiscal.control_fiscal_audit_preluare(tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)



# ============================================================
#  TERMENE — scadente viitoare pe portofoliu (orizont 60 zile)
# ============================================================
def _termene_una_firma(f, ctx, azi):
    """Blocul per firmă al lui `/termene`, MUTAT din buclă — cuvânt cu cuvânt.

    [P2, 08.09.2026] Nu mai rulează într-o cerere interactivă: îl cheamă calea de
    recalculare (`firma_rezumat.recalculeaza_greu`), o dată per firmă per schimbare.
    Măsurat înainte: `/termene` costa 8.000 de interogări și 3.001 de conexiuni la 1000 de
    firme — 12,9 s pentru o cerere. Codul e ACELAȘI; ce s-a schimbat e cine îl plătește.

    Întoarce `(eval, neevaluat)` — exact cele două ramuri ale buclei."""
    firme_eval = []
    neevaluate = []
    tid = f.get("id")
    try:
        with db.get_conn() as c:
            schema = auth_api.schema_tenant(c, ctx["uid"], tid)
        if not schema:
            # [P2] era `continue` in bucla; in functie: firma nu produce nimic
            return (None, None)
        with db.get_conn(schema) as cs:
            with cs.cursor() as cur:
                row = _repo.select_firma_profil(cur)
                from core.migrare_api import regim_contabil
                vector = {"regim_fiscal": row[0], "platitor_tva": row[1],
                          "tip_decont": row[2], "operatiuni_ic": row[3],
                          "tip_firma": row[4],
                          # [T2] partida_simpla din primitiva UNICA (ca semaforul) -> motorul nu emite D100/D101/D406 la PFA.
                          "partida_simpla": regim_contabil(row[4]) == "simpla",
                          # [§4] data inceperii inregistrarii TVA (fapt ANAF) -> motorul margineste D300/D394/D406
                          # la perioadele DE DUPA inregistrare (marginit=True), ca semaforul. Inchide asimetria intre ecrane.
                          "tva_data_inceput": row[5], "inreg_art317": row[6]} if row else {}
                _repo.select(cur)
                are_sal = False
                if cur.fetchone()[0]:
                    are_sal = _repo.select_salariati(cur)[0] > 0
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
                # [P2] era `continue`; in functie: firma iese NEEVALUATA, cu afirmatia ei
                return (None, neevaluate[0] if neevaluate else None)
            with db.get_conn() as cp:
                with cp.cursor() as cur:
  # [F163v2] vederea = depunerea curentă
                    depuse = {(t, a, l) for (t, a, l) in _repo.select_public_4(cur, tid)}
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
    return (firme_eval[0] if firme_eval else None,
            neevaluate[0] if neevaluate else None)


@app.get("/termene")
def termene_portofoliu(ctx=Depends(cere_cabinet)):
    """Scadente viitoare grupate pe data + tip, cu numarul de firme.

    [P2] CITEȘTE din modelul de citire — o singură interogare, indiferent câte firme. Firmele
    al căror rezumat lipsește sau e învechit NU tac: intră în `neevaluate` cu o afirmație
    tipată care spune **de ce** — aceeași interdicție ca la P1, o valoare veche nu se arată
    drept curentă."""
    try:
        return _uc_termene.termene_portofoliu(ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)



# ============================================================
#  FACTURI (în schema tenantului)
# ============================================================
def _raspuns(continut):
    """[P7 · use-case] Invelisul HTTP al lui `core/uc_comun._raspuns` — traduce refuzul de
    domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._raspuns(continut)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


def _octetii(fisier):
    """[P7 · use-case] Invelisul HTTP al lui `core/uc_comun._octetii` — traduce refuzul de
    domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._octetii(fisier)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


def _schema_sau_404(ctx, tenant_id):
    """[P7 · use-case] Invelisul HTTP al lui `core/uc_comun._schema_sau_404` — traduce refuzul de
    domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._schema_sau_404(ctx, tenant_id)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


def _anaf_tva_check(cui, valoare_manuala):
    """[P7 · use-case] Invelisul HTTP al lui `core/uc_comun._anaf_tva_check` — traduce refuzul de
    domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._anaf_tva_check(cui, valoare_manuala)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

# [p97_produse_rute] NOMENCLATOR PRODUSE — rute generice pe tenant (cabinet + client + gratuit)
# guard unificat: _schema_sau_404 accepta orice user cu acces la tenant (schema_tenant)
@app.get("/tenants/{tenant_id}/produse")
def produse_lista(tenant_id: int, ctx=Depends(cere_context)):
    try:
        return _uc_tenants.produse_lista(tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/tenants/{tenant_id}/produse/potriveste")
def produse_potriveste(tenant_id: int, date: ProdusPotrivesteIn, ctx=Depends(cere_context)):
    # preview cota (AI), fara salvare - pentru UI la scrierea denumirii
    _schema_sau_404(ctx, tenant_id)  # doar verific accesul
    return produse_api.potriveste(date.denumire, platitor_tva=date.platitor_tva)

@app.post("/tenants/{tenant_id}/produse")
def produse_creeaza(tenant_id: int, date: ProdusCreeazaIn, ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.produse_creeaza(tenant_id, date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.put("/tenants/{tenant_id}/produse/{produs_id}")
def produse_actualizeaza(tenant_id: int, produs_id: int, date: ProdusUpdateIn,                          ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.produse_actualizeaza(tenant_id, produs_id, date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.delete("/tenants/{tenant_id}/produse/{produs_id}")
def produse_sterge(tenant_id: int, produs_id: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.produse_sterge(tenant_id, produs_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

# [p104_emitere_rute] EMITERE FACTURI — rute generice pe tenant (client + gratuit + cabinet)
def _platitor_tva_firma(conn):
    """[P7 · use-case] Invelisul HTTP al lui `core/uc_comun._platitor_tva_firma` — traduce refuzul de
    domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._platitor_tva_firma(conn)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.get("/tenants/{tenant_id}/facturi/numerotare")
def facturi_numerotare_get(tenant_id: int, ctx=Depends(cere_context)):
    try:
        return _uc_tenants.facturi_numerotare_get(tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.put("/tenants/{tenant_id}/facturi/numerotare")
# [R42] Seria documentelor emise: o schimbare aici lasa goluri intr-o numerotare (interdictia 35).
def facturi_numerotare_set(tenant_id: int, date: NumerotareIn,                            ctx=Depends(cere_rol("admin_firma"))):
    try:
        return _uc_tenants.facturi_numerotare_set(tenant_id, date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.get("/tenants/{tenant_id}/scadentar")
def scadentar_get(tenant_id: int, ctx=Depends(cere_context)):
    """F131: scadentarul facturilor emise neincasate (restante/scade curand/in termen)
    + fisa client agregata. Read-only, fara schema noua."""
    try:
        return _uc_tenants.scadentar_get(tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

class OptInScadentarIn(BaseModel):
    activ: bool

@app.put("/tenants/{tenant_id}/scadentar/opt-in")
def scadentar_optin(tenant_id: int, date: OptInScadentarIn,                     ctx=Depends(cere_rol("admin_firma"))):
    """F131: activeaza/dezactiveaza notificarile email de scadenta pt firma (default OFF)."""
    try:
        return _uc_tenants.scadentar_optin(tenant_id, date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

class SupapaScadentarIn(BaseModel):
    stop: bool = False
    amanata_pana: Optional[str] = None

@app.put("/tenants/{tenant_id}/facturi/{factura_id}/notificare")
def scadentar_supapa(tenant_id: int, factura_id: int, date: SupapaScadentarIn,                      ctx=Depends(cere_rol("admin_firma"))):
    """F131: supapa per factura - nu notifica (stop) / amana pana la data X."""
    try:
        return _uc_tenants.scadentar_supapa(tenant_id, factura_id, date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.get("/util/zile-lucratoare")
def util_zile_lucratoare(start: str, end: str, ctx=Depends(cere_context)):
    """Zile lucratoare (L-V, fara sarbatori legale) intre doua date - auto-calcul CM
    (OUG 158/2005 art.10). Un an neacoperit de calendar da 422 vizibil, nu tacut."""
    from core import scadente as _scad
    from datetime import date as _d
    try:
        _s, _e = _d.fromisoformat(start), _d.fromisoformat(end)
    except ValueError:
        raise HTTPException(422, "Datele de început și de sfârșit se scriu ca AAAA-LL-ZZ, cu zile "
                                 "care există în calendar — am primit %r și %r." % (start, end))
    # [lotul 7] Un interval INVERSAT intorcea `{"zile": 0}` — o cifra, adica un raspuns. Iar cifra
    # asta intra in calculul indemnizatiei de concediu medical (auto-calcul CM, OUG 158/2005
    # art.10): „0 zile lucratoare" si „intervalul e scris invers" nu sunt acelasi lucru.
    if _e < _s:
        raise HTTPException(422, "Sfârșitul intervalului (%s) e înaintea începutului (%s). "
                                 "Zilele lucrătoare se numără pe un interval, iar intervalul are "
                                 "o ordine." % (end, start))
    try:
        return {"zile": _scad.zile_lucratoare_interval(_s, _e)}
    except ValueError as ex:
        raise HTTPException(422, str(ex))

class ModelFacturaIn(BaseModel):
    font: Optional[str] = None
    #: [lotul 6] `culoare="ceva-ce-nu-e-culoare"` intra in profil si ajungea in PDF-ul facturii,
    #: unde generatorul o citeste ca hex. Se cere forma, aici, unde se poate spune.
    culoare: Optional[str] = None
    logo: Optional[str] = None      # data URI base64; "" sterge; None = nu schimba

@app.get("/tenants/{tenant_id}/firma-profil")
def firma_profil_get(tenant_id: int, ctx=Depends(cere_context)):
    try:
        return _uc_tenants.firma_profil_get(tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

class RegimTvaIn(BaseModel):
    platitor_tva: bool

@app.post("/tenants/{tenant_id}/firma-profil/regim-tva")  # [tva_config_v1] setat la Configurare emitere
# [R42 (c)] Criteriul adăugat de Costin: *ce schimbă CE DATOREAZĂ firma cere `admin_firma`*.
# Nu e o ieșire — nu pleacă nimic — dar `platitor_tva` decide dacă firma datorează D300/D394 și
# pe ce perioade. O schimbare greșită nu produce o eroare vizibilă: produce declarații care nu se
# mai depun, sau se depun greșit.
def firma_profil_regim_tva(tenant_id: int, date: RegimTvaIn, ctx=Depends(cere_rol("admin_firma"))):
    try:
        return _uc_tenants.firma_profil_regim_tva(tenant_id, date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.get("/tenants/{tenant_id}/firma-profil/date")  # [date_firma_v1]
def firma_profil_date(tenant_id: int, ctx=Depends(cere_context)):
    try:
        return _uc_tenants.firma_profil_date(tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/firma-profil/date")  # [date_firma_v1]
def firma_profil_date_salveaza(tenant_id: int, date: dict = Body(...),                                ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.firma_profil_date_salveaza(tenant_id, date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/firma-profil/model")
def firma_profil_model(tenant_id: int, date: ModelFacturaIn, ctx=Depends(cere_context)):
    try:
        return _uc_tenants.firma_profil_model(tenant_id, date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.get("/tenants/{tenant_id}/facturi/{factura_id}/pdf")
def factura_pdf_ruta(tenant_id: int, factura_id: int, ctx=Depends(cere_context)):
    try:
        pdf, nume = _uc_tenants.factura_pdf_ruta(tenant_id, factura_id, ctx)
        return Response(content=pdf, media_type="application/pdf",
                        headers={"Content-Disposition": f'inline; filename="{nume}"'})
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

class EmailFacturaIn(BaseModel):
    email: str
    mesaj: Optional[str] = None

@app.post("/tenants/{tenant_id}/facturi/{factura_id}/email")
# [R42] Trimiterea către client: „iese către un om". Un email plecat nu se poate reface.
def factura_email(tenant_id: int, factura_id: int, date: EmailFacturaIn,
                  ctx=Depends(cere_rol("admin_firma"))):
    try:
        return _uc_tenants.factura_email(tenant_id, factura_id, date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.get("/tenants/{tenant_id}/facturi-recurente")
def fr_lista(tenant_id: int, ctx=Depends(cere_context)):
    try:
        return _uc_tenants.fr_lista(tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/tenants/{tenant_id}/facturi-recurente")
def fr_adauga(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_context)):
    try:
        return _uc_tenants.fr_adauga(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.put("/tenants/{tenant_id}/facturi-recurente/{sid}")
def fr_comuta(tenant_id: int, sid: int, activ: bool, ctx=Depends(cere_context)):
    try:
        return _uc_tenants.fr_comuta(tenant_id, sid, activ, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.delete("/tenants/{tenant_id}/facturi-recurente/{sid}")
def fr_sterge(tenant_id: int, sid: int, ctx=Depends(cere_context)):
    try:
        return _uc_tenants.fr_sterge(tenant_id, sid, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

def _preincalzeste_cursul(moneda, data_emitere):
    """[P7 · use-case, lotul 2] Invelisul HTTP al lui `core/uc_comun._preincalzeste_cursul` — traduce
    refuzul de domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._preincalzeste_cursul(moneda, data_emitere)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/facturi/emite")
# [R42] „emiterea unui document" — factura primește număr din serie și ajunge la un om.
def facturi_emite(tenant_id: int, date: EmitereIn, ctx=Depends(cere_rol("admin_firma"))):
    try:
        return _uc_tenants.facturi_emite(tenant_id, date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/tenants/{tenant_id}/facturi/{factura_id}/storno")
# [R42] Stornarea nu corectează documentul emis — emite AL DOILEA document (P4).
def facturi_storno(tenant_id: int, factura_id: int, ctx=Depends(cere_rol("admin_firma"))):
    try:
        return _uc_tenants.facturi_storno(tenant_id, factura_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

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
    try:
        return _uc_tenants.vector_citeste(tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/tenants/{tenant_id}/vector")  # [p82_vector] scrie vectorul (doar admin_firma)
def vector_salveaza(tenant_id: int, date: VectorIn, ctx=Depends(cere_rol("admin_firma"))):
    try:
        return _uc_tenants.vector_salveaza(tenant_id, date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/tenants/{tenant_id}/facturi")  # [p117_facturi_lista_acces] acces client+gratuit+cabinet
def facturi_lista(tenant_id: int, an: Optional[int] = None,                   luna: Optional[int] = None, directie: Optional[str] = None,                   limit: Optional[int] = None, offset: int = 0,                   ctx=Depends(cere_context)):
    try:
        return _uc_tenants.facturi_lista(tenant_id, an, luna, directie, limit, offset, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/facturi")
# [R42] A doua cale de creare a facturii (vezi R14: două funcții, stări implicite diferite).
# Amândouă produc un document numerotat, deci amândouă intră la „emiterea unui document".
def factura_creeaza(tenant_id: int, date: FacturaIn,                     ctx=Depends(cere_rol("admin_firma"))):
    try:
        return _uc_tenants.factura_creeaza(tenant_id, date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


def _moneda_facturii(schema, factura_id):
    """[P7 · use-case] Invelisul HTTP al lui `core/uc_comun._moneda_facturii` — traduce refuzul de
    domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._moneda_facturii(schema, factura_id)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/facturi/{factura_id}/transforma")
def proforma_transforma(tenant_id: int, factura_id: int, ctx=Depends(cere_rol("admin_firma"))):
    """Transforma proforma/aviz in factura fiscala (numerotare noua, nota se genereaza normal)."""
    try:
        return _uc_tenants.proforma_transforma(tenant_id, factura_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.get("/tenants/{tenant_id}/facturi/{factura_id:int}")  # [p115_detalii_acces] acces client+gratuit+cabinet
# {factura_id:int} (F187): fara tipare int, ruta asta captura literalele /facturi/export-saga si
# /facturi/export-winmentor (factura_id="export-..."->422 int_parsing), umbrindu-le. Bug latent la SAGA
# month (F171) - export-zip pe luna era nereachable. :int face literalele sa treaca la rutele lor.
def factura_detalii(tenant_id: int, factura_id: int, ctx=Depends(cere_context)):
    try:
        return _uc_tenants.factura_detalii(tenant_id, factura_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.delete("/tenants/{tenant_id}/facturi/{factura_id}")
# [R42] „ștergerea a ceva emis" — o factură ștearsă lasă un gol în serie (interdicția 35).
def factura_sterge(tenant_id: int, factura_id: int,                    ctx=Depends(cere_rol("admin_firma"))):
    """[EEE2] Refuzul e EXPLICAT, nu o eroare de bază: `409`, cu numărul notei și cu ieșirea numită
    (storno). Fără el, cu note automate, ștergerea ar fi început să pice pe cheia străină
    `inregistrari_factura_id_fkey`, care n-are `ON DELETE`."""
    try:
        return _uc_tenants.factura_sterge(tenant_id, factura_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


# ============================================================
#  CLIENȚI (în schema tenantului)
# ============================================================
@app.get("/tenants/{tenant_id}/clienti")
def clienti_lista(tenant_id: int, status: Optional[str] = None,                   ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.clienti_lista(tenant_id, status, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/clienti")
def client_creeaza(tenant_id: int, date: ClientIn,                    ctx=Depends(cere_rol("admin_firma", "angajat"))):
    try:
        return _uc_tenants.client_creeaza(tenant_id, date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/tenants/{tenant_id}/clienti/{client_id}")
def client_detalii(tenant_id: int, client_id: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.client_detalii(tenant_id, client_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.put("/tenants/{tenant_id}/clienti/{client_id}")
def client_actualizeaza(tenant_id: int, client_id: int, date: ClientEdit,                         ctx=Depends(cere_rol("admin_firma", "angajat"))):
    try:
        return _uc_tenants.client_actualizeaza(tenant_id, client_id, date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.delete("/tenants/{tenant_id}/clienti/{client_id}")
def client_sterge(tenant_id: int, client_id: int,                   ctx=Depends(cere_rol("admin_firma", "angajat"))):
    try:
        return _uc_tenants.client_sterge(tenant_id, client_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


# ============================================================
#  SALARIAȚI (în schema tenantului)
# ============================================================
@app.get("/tenants/{tenant_id}/salariati")
def salariati_lista(tenant_id: int, activ: Optional[bool] = None,                     ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.salariati_lista(tenant_id, activ, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/salariati")
def salariat_creeaza(tenant_id: int, date: SalariatIn,                      ctx=Depends(cere_rol("admin_firma", "angajat"))):
    try:
        return _uc_tenants.salariat_creeaza(tenant_id, date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/tenants/{tenant_id}/salariati/{salariat_id}")
def salariat_detalii(tenant_id: int, salariat_id: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.salariat_detalii(tenant_id, salariat_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.put("/tenants/{tenant_id}/salariati/{salariat_id}")
def salariat_actualizeaza(tenant_id: int, salariat_id: int, date: SalariatEdit,                           ctx=Depends(cere_rol("admin_firma", "angajat"))):
    try:
        return _uc_tenants.salariat_actualizeaza(tenant_id, salariat_id, date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/cor")
def cor_cauta(q: str = "", ctx=Depends(cere_context)):
    """[F137] Cauta in nomenclatorul COR national dupa cod (prefix) sau denumire (substring,
    diacritic-insensitiv). Pt lookup-ul de ocupatie pe contract/salariat. Orice user logat."""
    try:
        return _uc_cor.cor_cauta(q, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.put("/tenants/{tenant_id}/salariati/{salariat_id}/beneficiu-lunar")
def salariat_beneficiu_lunar(tenant_id: int, salariat_id: int, corp: dict = Body(...),                              ctx=Depends(cere_rol("admin_firma", "angajat"))):
    """[F133 Faza 2a] beneficiu one-off pe luna (vacanta/cadou/cultural) - upsert; 0 = sterge."""
    try:
        return _uc_tenants.salariat_beneficiu_lunar(tenant_id, salariat_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.delete("/tenants/{tenant_id}/salariati/{salariat_id}")
def salariat_sterge(tenant_id: int, salariat_id: int,                     ctx=Depends(cere_rol("admin_firma", "angajat"))):
    try:
        return _uc_tenants.salariat_sterge(tenant_id, salariat_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/tenants/{tenant_id}/salariati/{salariat_id}/concedii")  # cm_lista_v1
def cm_lista(tenant_id: int, salariat_id: int, an: int = None, ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.cm_lista(tenant_id, salariat_id, an, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/salariati/{salariat_id}/concedii")  # cm_salveaza_v1
def cm_salveaza(tenant_id: int, salariat_id: int, corp: dict = Body(...),                 ctx=Depends(cere_rol("admin_firma", "angajat"))):
    try:
        return _uc_tenants.cm_salveaza(tenant_id, salariat_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.delete("/tenants/{tenant_id}/salariati/{salariat_id}/concedii/{cm_id}")  # cm_sterge_v1
def cm_sterge(tenant_id: int, salariat_id: int, cm_id: int,               ctx=Depends(cere_rol("admin_firma", "angajat"))):
    try:
        return _uc_tenants.cm_sterge(tenant_id, salariat_id, cm_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


# ============================================================
#  COADĂ DECLARAȚII (flux validare: asistent -> senior -> depusă)
# ============================================================
# [p57_notif] helpere notificari pe fluxul cozii
def _coada_info(conn, coada_id):
    """[P7 · use-case, lotul 2] Invelisul HTTP al lui `core/uc_comun._coada_info` — traduce
    refuzul de domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._coada_info(conn, coada_id)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

def _notif_de_validat(conn, cabinet_id, tip, perioada, creat_de_id):
    """[P7 · use-case] Invelisul HTTP al lui `core/uc_comun._notif_de_validat` — traduce refuzul de
    domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._notif_de_validat(conn, cabinet_id, tip, perioada, creat_de_id)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

def _notif_pregatitor(conn, coada_id, tip_eveniment, motiv=None):
    """[P7 · use-case, lotul 2] Invelisul HTTP al lui `core/uc_comun._notif_pregatitor` — traduce
    refuzul de domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._notif_pregatitor(conn, coada_id, tip_eveniment, motiv)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/coada")
def coada_adauga(date: CoadaIn, ctx=Depends(cere_rol("admin_firma", "angajat"))):
    try:
        return _uc_coada.coada_adauga(date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/coada")
def coada_lista(stare: Optional[str] = None, ctx=Depends(cere_cabinet)):
    try:
        return _uc_coada.coada_lista(stare, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/coada/{coada_id}/continut")
def coada_continut(coada_id: int, ctx=Depends(cere_cabinet)):
    """[patru-ochi] Continutul unui element din coada pentru VIZUALIZARE inainte de aprobare:
    declaratia (avertismente/note), XML-ul generat si verdictul DUK. Read-only. Fara asta,
    validarea in doi era oarba - cine aproba nu vedea ce aproba (declaratie/XML/verdict)."""
    try:
        return _uc_coada.coada_continut(coada_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/coada/{coada_id}/aproba")
def coada_aproba(coada_id: int, date: dict = Body(default={}),
                 ctx=Depends(cere_rol("admin_firma", "angajat"))):
    try:
        return _uc_coada.coada_aproba(coada_id, date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/coada/{coada_id}/respinge")
def coada_respinge(coada_id: int, date: RespingeIn,
                   ctx=Depends(cere_rol("admin_firma", "angajat"))):
    try:
        return _uc_coada.coada_respinge(coada_id, date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/coada/{coada_id}/depune")
# [R42] „confirmarea depunerii" — declarația pleacă la autoritate și nu se mai poate reface.
# Validarea (`aproba`/`respinge`) rămâne la asistent: aia se poate reface.
def coada_depune(coada_id: int, date: DepuneIn = DepuneIn(),
                 ctx=Depends(cere_rol("admin_firma"))):
    try:
        return _uc_coada.coada_depune(coada_id, date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

# [p57_notif] RUTE NOTIFICARI
@app.get("/notificari")
def notificari_lista(doar_necitite: bool = False, ctx=Depends(cere_cabinet)):
    try:
        return _uc_notificari.notificari_lista(doar_necitite, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.get("/notificari/contor")
def notificari_contor(ctx=Depends(cere_cabinet)):
    try:
        return _uc_notificari.notificari_contor(ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)
@app.get("/notificari/sumar")  # [p63_notif_sumar]
def notificari_sumar(ctx=Depends(cere_cabinet)):
    try:
        return _uc_notificari.notificari_sumar(ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/notificari/citit")
def notificari_citit_toate(ctx=Depends(cere_cabinet)):
    try:
        return _uc_notificari.notificari_citit_toate(ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

# [p62_pachete] RUTE PACHETE LUNARE
class PachetTextIn(BaseModel):
    text: str
    status: Optional[str] = "ciorna"

def _pachet_schema(ctx, tenant_id):
    """[P7 · use-case] Invelisul HTTP al lui `core/uc_comun._pachet_schema` — traduce refuzul de
    domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._pachet_schema(ctx, tenant_id)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.get("/pachete/{tenant_id}/rezumat")
def pachet_rezumat(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_pachete.pachet_rezumat(tenant_id, an, luna, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/pachete/{tenant_id}/genereaza")
def pachet_genereaza(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_pachete.pachet_genereaza(tenant_id, an, luna, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.get("/pachete/{tenant_id}/poveste")
def pachet_poveste_get(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_pachete.pachet_poveste_get(tenant_id, an, luna, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

# ICRD_NOTIF_EMAIL_CLIENT_V1
def _email_client_tenant(conn, tenant_id):
    """[P7 · use-case] Invelisul HTTP al lui `core/uc_comun._email_client_tenant` — traduce refuzul de
    domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._email_client_tenant(conn, tenant_id)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

def _nume_tenant(conn, tenant_id):
    """[P7 · use-case] Invelisul HTTP al lui `core/uc_comun._nume_tenant` — traduce refuzul de
    domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._nume_tenant(conn, tenant_id)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/pachete/{tenant_id}/poveste")
# [R42] „iese către un om" — pe `status=aprobat` pleacă raportul lunar la client.
def pachet_poveste_set(tenant_id: int, an: int, luna: int, date: PachetTextIn,                        ctx=Depends(cere_rol("admin_firma"))):
    try:
        return _uc_pachete.pachet_poveste_set(tenant_id, an, luna, date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.get("/pachete/{tenant_id}/preview")
def pachet_preview(tenant_id: int, an: int, luna: int, text: str = "", ctx=Depends(cere_cabinet)):
    try:
        return _uc_pachete.pachet_preview(tenant_id, an, luna, text, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/pachete/{tenant_id}/trimite")
# [R42] „iese către un om" — pachetul lunar pleacă la clientul cabinetului.
def pachet_trimite(tenant_id: int, an: int, luna: int, ctx=Depends(cere_rol("admin_firma"))):
    try:
        return _uc_pachete.pachet_trimite(tenant_id, an, luna, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/notificari/{nid}/citit")
def notificari_citit_una(nid: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_notificari.notificari_citit_una(nid, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


# ============================================================
#  DECLARAȚII
# ============================================================
@app.get("/declaratii/tipuri")
def declaratii_tipuri(tenant_id: Optional[int] = None, ctx=Depends(cere_cabinet)):
    try:
        return _uc_declaratii.declaratii_tipuri(tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/declaratii/{tip}/valideaza")  # duk_valideaza_v1
def declaratie_valideaza(tip: str, date: DeclaratieIn,                          ctx=Depends(cere_rol("admin_firma", "angajat"))):
    """Genereaza declaratia si o trece prin validatorul OFICIAL ANAF (DUKIntegrator).
    Intoarce TREI stari: valid / erori / gri (gri = nu am putut valida; un XML
    nevalidat NU se declara valid). Vezi core/duk.py."""
    try:
        return _uc_declaratii.declaratie_valideaza(tip, date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/declaratii/{tip}")
def declaratie_genereaza(tip: str, date: DeclaratieIn,                          ctx=Depends(cere_rol("admin_firma", "angajat"))):
    try:
        return _uc_declaratii.declaratie_genereaza(tip, date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)  # [lista 5]


# ============================================================
#  PORTAL CLIENT (read-only, izolat)
# ============================================================
def _tenant_client(ctx, tenant_id=None):
    """[P7 · use-case] Invelisul HTTP al lui `core/uc_comun._tenant_client` — traduce refuzul de
    domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._tenant_client(ctx, tenant_id)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/portal/firme")
def portal_firme(ctx=Depends(cere_client)):
    try:
        return _uc_portal.portal_firme(ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

# [portal_acces_cont_v1] patronul isi gestioneaza propriul email + acces suplimentar (fara parola, magic-link)
class SchimbaEmailIn(BaseModel):
    tenant_id: Optional[int] = None
    email: str
class AdaugaAccesIn(BaseModel):
    tenant_id: Optional[int] = None
    email: str
    nume: str = ""
def _titular_client(cur, tenant_id):
    """[P7 · use-case] Invelisul HTTP al lui `core/uc_comun._titular_client` — traduce refuzul de
    domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._titular_client(cur, tenant_id)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/portal/acces-cont")
def portal_acces_cont(tenant_id: Optional[int] = None, ctx=Depends(cere_client)):
    try:
        return _uc_portal.portal_acces_cont(tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)
def _adresa_e_libera(cur, email, exclude_user_id):
    """[P7 · use-case] Invelisul HTTP al lui `core/uc_comun._adresa_e_libera` — traduce refuzul de
    domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._adresa_e_libera(cur, email, exclude_user_id)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


def _urma_portal(cur, tenant_id, actiune, detaliu, autor_id):
    """[P7 · use-case] Invelisul HTTP al lui `core/uc_comun._urma_portal` — traduce refuzul de
    domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._urma_portal(cur, tenant_id, actiune, detaliu, autor_id)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


def _cere_acelasi_cabinet(ex, firm_id):
    """[P7 · use-case] Invelisul HTTP al lui `core/uc_comun._cere_acelasi_cabinet` — traduce refuzul de
    domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._cere_acelasi_cabinet(ex, firm_id)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


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
    try:
        return _uc_public.portal_confirma_email(date)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/tenants/{tenant_id}/urme-portal")  # [api_intern_v1] scrisa, NECITITA de om: niciun ecran n-o cheama, deci punctul (3) din R62 ramane NESATISFACUT. Iese din lista cand se construieste ecranul. (27.08.2026)
def cabinet_urme_portal(tenant_id: int, ctx=Depends(cere_cabinet)):
    """[R62 (3)] Urma se poate CITI. Lectia din R58: o urma care nu se poate citi e scrisa degeaba."""
    try:
        return _uc_tenants.cabinet_urme_portal(tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.put("/portal/acces-cont/email")
def portal_schimba_email(date: SchimbaEmailIn, ctx=Depends(cere_client)):
    try:
        return _uc_portal.portal_schimba_email(date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)
@app.post("/portal/acces-cont/acces")
def portal_adauga_acces(date: AdaugaAccesIn, ctx=Depends(cere_client)):
    try:
        return _uc_portal.portal_adauga_acces(date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)
@app.delete("/portal/acces-cont/acces/{user_id}")
def portal_revoca_acces(user_id: int, tenant_id: Optional[int] = None, ctx=Depends(cere_client)):
    try:
        return _uc_portal.portal_revoca_acces(user_id, tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/portal/firma")
def portal_firma(tenant_id: Optional[int] = None, ctx=Depends(cere_client)):
    try:
        return _uc_portal.portal_firma(tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


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
    try:
        return _uc_tenants.bonuri_de_verificat(tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)
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
def bon_aproba(tenant_id: int, bon_id: int, b: BonAproba,                ctx=Depends(cere_rol("admin_firma"))):
    try:
        return _uc_tenants.bon_aproba(tenant_id, bon_id, b, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)
# [R33] Nota propusa mecanic intra CIORNA. Validarea o face al doilea om - patru-ochi.


@app.post("/tenants/{tenant_id}/salarii-contare/propunere")
# [R33, decizia Costin 25.08.2026] Semnalul de coerenta nota-vs-D112 apare LA PROPUNERE:
# *„singurul moment in care omul poate face ceva cu informatia; la inchiderea lunii e prea tarziu,
# iar pe suprafata de control fiscal e o constatare despre trecut."*
#
# POST desi nu scrie nimic - acelasi precedent ca `calcul-cm` si `prapastie-salariu`. Regula pe
# care o respecta e cealalta: un GET n-are voie sa scrie (interdictia 6). Aici nu scrie nimeni.
def salarii_contare_propunere(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    """Nota pe care ar scrie-o statul de plata + divergentele fata de D112, cu ambele cifre."""
    try:
        return _uc_tenants.salarii_contare_propunere(tenant_id, an, luna, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/salarii-contare")
# [R33] Actul: scrie nota CIORNA a statului de plata. Semnaleaza, NU blocheaza - divergenta se
# intoarce si dupa contare, ca sa nu se stinga prin ignorare (regula de la contradictiile pe
# statul de plata). Ciorna, nu validata: patru-ochi ramane.
def salarii_contare_scrie(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    """Scrie nota ciorna a statului de plata. Idempotent pe `document_ref` (interdictia 8:
    schema nu lasa un al doilea exemplar)."""
    try:
        return _uc_tenants.salarii_contare_scrie(tenant_id, an, luna, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/amortizare")
# [R55, 26.08.2026] Rolul e aici fiindca ruta scrie nota `validata` DIRECT — deci produce
# EVIDENTA, nu o propunere, si sare peste poarta de validare. Din cele 40 de rute care scriu
# in `inregistrari_linii`, 36 scriu `ciorna`; astea trei nu. E aceeasi clasa pe care R33 a
# reparat-o la nota de salarii (vezi antetul `core/salarii_contare.py`: „status='validata'
# direct -- ocolea patru-ochi"), ramasa nereparata in trei locuri.
def tenant_amortizare(tenant_id: int, an: int, luna: int,                       ctx=Depends(cere_rol("admin_firma"))):
    """Genereaza nota de amortizare lunara: 6811 = cont_amortizare, per MF activ."""
    try:
        return _uc_tenants.tenant_amortizare(tenant_id, an, luna, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)
def _perioada_blocata(conn, schema, data_nota):
    """[P7 · use-case] Invelisul HTTP al lui `core/uc_comun._perioada_blocata` — traduce refuzul de
    domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._perioada_blocata(conn, schema, data_nota)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

def _interval_cerut(valoare, nume, minim, maxim, unitate):
    """[P7 · use-case, lotul 2] Invelisul HTTP al lui `core/uc_comun._interval_cerut` — traduce
    refuzul de domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._interval_cerut(valoare, nume, minim, maxim, unitate)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


def _cere_luna_deschisa(conn, schema, data):
    """[P7 · use-case] Invelisul HTTP al lui `core/uc_comun._cere_luna_deschisa` — traduce refuzul de
    domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._cere_luna_deschisa(conn, schema, data)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


def _cere_admin_firma(ctx, mesaj):
    """[P7 · use-case] Invelisul HTTP al lui `core/uc_comun._cere_admin_firma` — traduce refuzul de
    domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._cere_admin_firma(ctx, mesaj)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


def _declaratie_generata(conn, tenant_id, tip, an, luna):
    """[P7 · use-case] Invelisul HTTP al lui `core/uc_comun._declaratie_generata` — traduce refuzul de
    domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._declaratie_generata(conn, tenant_id, tip, an, luna)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


def _cere_perioada_deschisa(conn, schema, nota_id):
    """[P7 · use-case] Invelisul HTTP al lui `core/uc_comun._cere_perioada_deschisa` — traduce refuzul de
    domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._cere_perioada_deschisa(conn, schema, nota_id)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.get("/tenants/{tenant_id}/perioade-blocate")
def perioade_blocate_lista(tenant_id: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.perioade_blocate_lista(tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

def _facturi_neincheiate_in_perioada(cur, schema, an, luna):
    """[P7 · use-case] Invelisul HTTP al lui `core/uc_comun._facturi_neincheiate_in_perioada` — traduce refuzul de
    domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._facturi_neincheiate_in_perioada(cur, schema, an, luna)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


def _ciorne_in_perioada(cur, schema, an, luna):
    """[P7 · use-case] Invelisul HTTP al lui `core/uc_comun._ciorne_in_perioada` — traduce refuzul de
    domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._ciorne_in_perioada(cur, schema, an, luna)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


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
    try:
        return _uc_tenants.perioada_blocheaza(tenant_id, an, luna, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.delete("/tenants/{tenant_id}/perioade-blocate")
# [R58] Redeschiderea e ACT CONSEMNAT, CU MOTIV — P15 și interdicția 36, care o cereau explicit.
# Până azi `DELETE` ștergea rândul, iar odată cu el dispăreau `blocat_de`, `blocat_la` și însuși
# faptul că perioada fusese închisă. Urma trăiește acum în `perioade_inchideri` (append-only,
# cu constrângerea de motiv în BAZĂ, nu doar aici — o urmă care se poate scrie fără motiv de pe
# altă cale n-ar fi o urmă). Poarta rămâne neatinsă: `_cere_luna_deschisa` citește ca înainte.
def perioada_deblocheaza(tenant_id: int, an: int, luna: int, motiv: str = "",                          ctx=Depends(cere_rol("admin_firma"))):
    try:
        return _uc_tenants.perioada_deblocheaza(tenant_id, an, luna, motiv, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.get("/tenants/{tenant_id}/perioade-blocate/istoric")
# [R58] Urma se poate CITI — altfel ar fi scrisă degeaba. Cine a închis, cine a redeschis, când
# și de ce.
def perioade_istoric(tenant_id: int, an: Optional[int] = None, luna: Optional[int] = None,                      ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.perioade_istoric(tenant_id, an, luna, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.get("/tenants/{tenant_id}/jurnal")
def tenant_jurnal(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    """Registrul-jurnal (OMFP 2634/2015, cod 14-1-1), pe luna ceruta.

    Confruntat cu norma pe 24.08.2026: coloana 1 (nr. curent de la 1 ianuarie), coloana 3
    (felul/numarul/data documentului justificativ) si totalizarea lunara lipseau. Toate trei
    se DERIVA aici, la citire - nicio cale de scriere nu se atinge. Ce nu se poate deriva
    ramane null: `note_fara_document` spune cate sunt, ca absenta sa fie numarata, nu ascunsa.
    """
    try:
        return _uc_tenants.tenant_jurnal(tenant_id, an, luna, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)
# Sursele in care traieste un raport Z. Constanta, nu literal in SQL: gardul o citeste din AST
# si compara MULTIMEA, in loc sa caute un sir intr-un text (METODA §23).
# [P5 val 1b] Se IMPORTA din `core/raport_z.py`, unde sta si indexul care o impune in baza:
# doua liste scrise separat ar fi putut descrie doua multimi diferite, iar poarta din cod si
# indexul din baza ar fi aparat lucruri diferite fara ca nimic sa spuna.


def _cere_z_unic(cur, schema, numar):
    """[P7 · use-case, lotul 2] Invelisul HTTP al lui `core/uc_comun._cere_z_unic` — traduce
    refuzul de domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._cere_z_unic(cur, schema, numar)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/horeca/import-amef")
# [P5 val 1b, 10.09.2026] MUTATĂ PE FIR, după ce garanția pe care se sprijinea a devenit una
# a DATELOR. Până azi rămăsese `async def` deliberat: bucla îi serializa verificarea de
# unicitate a raportului Z, iar baza n-avea index care s-o înlocuiască. Acum îl are
# (`core/raport_z.py`), pus pe firmele noi din template și pe cele existente la pornire, deci
# serializarea buclei nu mai e nimănui necesară.
def horeca_import_amef(tenant_id: int, fisier: UploadFile = File(...), ctx=Depends(cere_cabinet)):
    """Upload p7b/XML AMEF (OPANAF 146/2018 II.7) -> nota Raport Z CIORNA.
    Nota se genereaza pe cote reale din XML: 5311/5125=707 + 707=4427 per cota."""
    try:
        return _uc_tenants.horeca_import_amef(tenant_id, _octetii(fisier), ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/tenants/{tenant_id}/horeca/raport-z")
# [R55, 26.08.2026] Rolul e aici fiindca ruta scrie nota `validata` DIRECT — deci produce
# EVIDENTA, nu o propunere, si sare peste poarta de validare. Din cele 40 de rute care scriu
# in `inregistrari_linii`, 36 scriu `ciorna`; astea trei nu. E aceeasi clasa pe care R33 a
# reparat-o la nota de salarii (vezi antetul `core/salarii_contare.py`: „status='validata'
# direct -- ocolea patru-ochi"), ramasa nereparata in trei locuri.
def horeca_raport_z(tenant_id: int, rz: RaportZ,
                    ctx=Depends(cere_rol("admin_firma"))):
    try:
        return _uc_tenants.horeca_raport_z(tenant_id, rz, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)
@app.post("/tenants/{tenant_id}/banca/parse-extras")  # [api_intern_v1] parsare extras la upload - fara UI inca, pastrat deliberat
def banca_parse_extras(tenant_id: int, fisier: UploadFile = File(...), ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.banca_parse_extras(tenant_id, _octetii(fisier), fisier.filename, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)
@app.get("/tenants/{tenant_id}/stat-plata")
def tenant_stat_plata(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.tenant_stat_plata(tenant_id, an, luna, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)
@app.get("/tenants/{tenant_id}/fluturas/{salariat_id}")
# [R52] Poartă salariul unei PERSOANE — date despre cineva care nu e firma.
def tenant_fluturas(tenant_id: int, salariat_id: int, an: int, luna: int,
                    ctx=Depends(cere_rol("admin_firma"))):
    try:
        pdf = _uc_tenants.tenant_fluturas(tenant_id, salariat_id, an, luna, ctx)
        return Response(content=pdf, media_type="application/pdf",
                        headers={"Content-Disposition": f'attachment; filename="fluturas_{salariat_id}_{an}_{luna:02d}.pdf"'})
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


# ---------------------------------------------------------------------------------------------
# [stat_emis 21.08.2026] Statul de plata ca DOCUMENT EMIS. Pana aici, statul si fluturasul se
# recalculau la fiecare afisare: un fluturas dat unui om in ianuarie putea iesi altfel in iulie.
# Emiterea ingheata cifrele cu amprenta; divergenta fata de recalcul se SEMNALEAZA; corectia e al
# doilea exemplar, care il refera pe primul. Aplicatia nu corecteaza singura - contabilul decide.
def _cere_an_luna(corp):
    """[P7 · use-case, lotul 2] Invelisul HTTP al lui `core/uc_comun._cere_an_luna` — traduce
    refuzul de domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._cere_an_luna(corp)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/stat-plata/emite")
# [R42] „iese către un om" — statul se îngheață cu amprentă, exemplar numerotat (P4).
# Dreptul fin `poate_valida` rămâne, verificat în corp: rolul e condiția, dreptul e a doua.
def tenant_stat_emite(tenant_id: int, corp: dict = Body(...),
                      ctx=Depends(cere_rol("admin_firma"))):
    """corp: {an, luna}. Idempotent: cine are deja exemplar nu primeste al doilea (ala e o corectie)."""
    try:
        return _uc_tenants.tenant_stat_emite(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/tenants/{tenant_id}/stat-plata/emis")
def tenant_stat_emis(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    """Exemplarele emise + contradictiile DERIVATE (emis vs recalcul de acum). Nu scrie nimic."""
    try:
        return _uc_tenants.tenant_stat_emis(tenant_id, an, luna, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/stat-plata/corectie")
def tenant_stat_corectie(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {salariat_id, an, luna}. Al doilea exemplar. Primul ramane - el a ajuns la om."""
    try:
        return _uc_tenants.tenant_stat_corectie(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/stat-plata/motiv")
def tenant_stat_motiv(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {exemplar_id, motiv}. ASUMA divergenta, nu o sterge: ramane in lista, cu cine si cand."""
    try:
        return _uc_tenants.tenant_stat_motiv(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/tenants/{tenant_id}/plata-salarii-preview")
def tenant_plata_salarii_preview(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    """[F134] Sumar inainte de generarea fisierului SEPA: cate plati, total, cine e exclus (fara IBAN)."""
    try:
        return _uc_tenants.tenant_plata_salarii_preview(tenant_id, an, luna, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/plata-salarii-fisier")
# [R45] POST, nu GET: producerea fișierului care pleacă la bancă e un ACT, iar un GET n-are
# voie să scrie (interdicția 6, `core/test_get_fara_scriere.py`). Metoda contrazicea fapta.
def tenant_plata_salarii_fisier(tenant_id: int, an: int, luna: int,
                                ctx=Depends(cere_rol("admin_firma"))):
    """[F134] Fisierul SEPA/ISO 20022 pain.001.001.03 de plata a salariilor NET pe card (download).
    [R45] Se pastreaza: continut, moment, autor, amprenta, numar de exemplar."""
    try:
        xml, meta = _uc_tenants.tenant_plata_salarii_fisier(tenant_id, an, luna, ctx)
        return Response(content=xml, media_type="application/xml",
                        headers={"Content-Disposition": f'attachment; filename="{meta["fisier"]}"'})
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


# ---- [F125] clasificare manuala D390 (reclasificare + adaugare) ----
def _schema_cabinet_sau_404(ctx, tenant_id):
    """[P7 · use-case] Invelisul HTTP al lui `core/uc_comun._schema_cabinet_sau_404` — traduce refuzul de
    domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._schema_cabinet_sau_404(ctx, tenant_id)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/tenants/{tenant_id}/d390-clasificare")
def d390_clasificare_stare(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    """Operatiunile auto-derivate (cu tipul curent) + liniile manuale, pt ecranul de clasificare."""
    try:
        return _uc_tenants.d390_clasificare_stare(tenant_id, an, luna, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.put("/tenants/{tenant_id}/d390-clasificare/reclasificare")
def d390_reclasificare(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """Override tip pe o operatiune auto: {an, luna, directie, tara, cod, tip}."""
    try:
        return _uc_tenants.d390_reclasificare(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/d390-clasificare/manual")
def d390_manual_adauga(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """Adauga linie pur manuala: {an, luna, tip, tara, cod, den, baza}."""
    try:
        return _uc_tenants.d390_manual_adauga(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.delete("/tenants/{tenant_id}/d390-clasificare/manual/{mid}")
def d390_manual_sterge(tenant_id: int, mid: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.d390_manual_sterge(tenant_id, mid, an, luna, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


# [D301 27.07.2026] Introducerea operatiunilor D301 (decont special TVA). Geaman cu
# d390-clasificare: grila lunara + adaugare + stergere, cere_cabinet (operatiuni de contabil).
@app.get("/tenants/{tenant_id}/d301-operatiuni")
def d301_operatiuni_lista(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    """Operatiunile lunii + nomenclatoare (tipuri, valute, cote period-aware) pt ecranul D301."""
    try:
        return _uc_tenants.d301_operatiuni_lista(tenant_id, an, luna, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/d301-operatiuni")
def d301_operatiuni_adauga(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """Adauga o operatiune: {an, luna, tip, nr_doc, data_doc, val_valuta, tip_valuta, curs, cota}."""
    try:
        return _uc_tenants.d301_operatiuni_adauga(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.delete("/tenants/{tenant_id}/d301-operatiuni/{op_id}")
def d301_operatiuni_sterge(tenant_id: int, op_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.d301_operatiuni_sterge(tenant_id, op_id, an, luna, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)




# [B2/B3 D300] Randuri manuale D300 (Decont TVA). Geaman cu d301-operatiuni: grila lunara +
# adaugare + stergere, cere_cabinet (operatiuni de contabil). Persistate in d300_manual;
# d300.genereaza le re-citeste pe calea de depunere (paritate preview<->depunere).
@app.get("/tenants/{tenant_id}/d300-manual")
def d300_manual_lista(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    """Randurile manuale ale perioadei + randurile inca disponibile de adaugat (allow-list minus
    auto-derivate minus deja introduse), cu etichete oficiale din backend."""
    try:
        return _uc_tenants.d300_manual_lista(tenant_id, an, luna, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/d300-manual")
def d300_manual_adauga(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """Adauga/actualizeaza un rand manual D300: {an, luna, rand, baza, tva, descriere}."""
    try:
        return _uc_tenants.d300_manual_adauga(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.delete("/tenants/{tenant_id}/d300-manual/{rid}")
def d300_manual_sterge(tenant_id: int, rid: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.d300_manual_sterge(tenant_id, rid, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


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
    try:
        pdf = _uc_tenants.tenant_adeverinta(tenant_id, salariat_id, date, ctx)
        return Response(content=pdf, media_type="application/pdf",
                        headers={"Content-Disposition": f'attachment; filename="adeverinta_{salariat_id}.pdf"'})
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.get("/tenants/{tenant_id}/salariati/{salariat_id}/pontaj")
def tenant_pontaj_get(tenant_id: int, salariat_id: int, an: int, luna: int, ctx=Depends(cere_context)):
    """F135: grila lunara de pontaj (informativ) - zile lucratoare, exceptii, rezumat."""
    try:
        return _uc_tenants.tenant_pontaj_get(tenant_id, salariat_id, an, luna, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

class PontajIn(BaseModel):
    zi: str
    stare: Optional[str] = None

@app.put("/tenants/{tenant_id}/salariati/{salariat_id}/pontaj")
def tenant_pontaj_set(tenant_id: int, salariat_id: int, date: PontajIn, ctx=Depends(cere_context)):
    """F135: seteaza starea unei zile (stare goala/prezent = sterge exceptia)."""
    try:
        return _uc_tenants.tenant_pontaj_set(tenant_id, salariat_id, date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


class ConfirmaPontajIn(BaseModel):
    an: int
    luna: int


@app.get("/tenants/{tenant_id}/facturi/perioada")
def tenant_facturi_perioada(tenant_id: int, an: int, luna: int, ctx=Depends(cere_context)):
    """[cap.23, 21.08.2026] Starea INCHIDERII lunii pe domeniul `facturi`: confirmat / cine / cand,
    daca se poate confirma acum si — daca nu — DE CE (documente primite de la ANAF, neinregistrate)."""
    try:
        return _uc_tenants.tenant_facturi_perioada(tenant_id, an, luna, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/facturi/perioada/confirma")
def tenant_facturi_perioada_confirma(tenant_id: int, date: ConfirmaPontajIn,                                      ctx=Depends(cere_rol("admin_firma"))):
    """[cap.23] Declara luna INCHISA pe facturi: evidenta ei devine autoritativa, iar semaforul se poate
    sprijini pe ea cand spune ca o declaratie nu se datoreaza. Rol admin_firma, ca la pontaj.
    REFUZA motivat daca stim de e-Facturi primite si neinregistrate — nu lasam pe cineva sa declare
    complet ceva ce noi vedem deja ca nu e."""
    try:
        return _uc_tenants.tenant_facturi_perioada_confirma(tenant_id, date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/facturi/perioada/redeschide")
def tenant_facturi_perioada_redeschide(tenant_id: int, date: ConfirmaPontajIn,                                        ctx=Depends(cere_rol("admin_firma"))):
    """[cap.23] Redeschide luna (o corectie de facturi cere redeschiderea). Simetric cu confirmarea;
    o modificare de facturi o face oricum AUTOMAT (facturi_api._redeschide_luna)."""
    try:
        return _uc_tenants.tenant_facturi_perioada_redeschide(tenant_id, date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/pontaj/confirma")
def tenant_pontaj_confirma(tenant_id: int, date: ConfirmaPontajIn, ctx=Depends(cere_rol("admin_firma"))):
    """[cap.23] Confirma pontajul lunii -> devine AUTORITATIV pentru salarizare (tichete pe zile efectiv
    lucrate). Rol admin_firma. Idempotent (re-confirmarea reimprospateaza)."""
    try:
        return _uc_tenants.tenant_pontaj_confirma(tenant_id, date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

# cf_verificari_v1: verificari contabile reutilizabile (echilibru + trezorerie)
def _verifica_documente_pozate(schema):
    """[P7 · use-case, lotul 2] Invelisul HTTP al lui `core/uc_comun._verifica_documente_pozate` — traduce
    refuzul de domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._verifica_documente_pozate(schema)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

def _verificari_contabile(schema, an, luna):
    """[P7 · use-case, lotul 2] Invelisul HTTP al lui `core/uc_comun._verificari_contabile` — traduce
    refuzul de domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._verificari_contabile(schema, an, luna)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/firme/{tenant_id}/verificari")
def firma_verificari(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_firme.firma_verificari(tenant_id, an, luna, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

def _tenant_pentru_documente(ctx, tenant_id):
    """[P7 · use-case, lotul 2] Invelisul HTTP al lui `core/uc_comun._tenant_pentru_documente` — traduce
    refuzul de domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._tenant_pentru_documente(ctx, tenant_id)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/portal/bon")
def portal_bon(fisiere: list[UploadFile] = File(...), tenant_id: Optional[int] = None, ctx=Depends(cere_context)):
    """Extrage datele bonului cu AI si salveaza ca DRAFT (status='extras') + pozele pe disc.
    Intra la contabil doar dupa confirmarea clientului (POST /portal/bon/{id}/confirma)."""
    try:
        return _uc_portal.portal_bon([(_octetii(_f), _f.filename) for _f in fisiere], tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

def _bon_imagine_cale(schema, bon_id, n):
    """[P7 · use-case, lotul 2] Invelisul HTTP al lui `core/uc_comun._bon_imagine_cale` — traduce
    refuzul de domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._bon_imagine_cale(schema, bon_id, n)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/portal/bon/{bon_id}/confirma")
def portal_bon_confirma(bon_id: int, tenant_id: Optional[int] = None, ctx=Depends(cere_context)):
    """Clientul confirma ca poza e intreaga si lizibila -> bonul intra la contabil."""
    try:
        return _uc_portal.portal_bon_confirma(bon_id, tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.delete("/portal/bon/{bon_id}")
def portal_bon_sterge(bon_id: int, tenant_id: Optional[int] = None, ctx=Depends(cere_context)):
    """Clientul reface poza -> draftul (status='extras') si pozele lui se sterg."""
    try:
        return _uc_portal.portal_bon_sterge(bon_id, tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

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
    try:
        cale = _uc_tenants.cabinet_bon_imagine(tenant_id, bon_id, n, ctx)
        return FileResponse(cale)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)
@app.get("/tenants/{tenant_id}/bonuri/{bon_id}/facturi-candidate")
def bon_facturi_candidate(tenant_id: int, bon_id: int, ctx=Depends(cere_cabinet)):
    """Pentru o chitanta: facturile PRIMITE, neplatite, care ar putea fi stinse de ea.
    Ordonare: potrivire CUI intai, apoi apropiere de suma."""
    try:
        return _uc_tenants.bon_facturi_candidate(tenant_id, bon_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

class ChitantaStinge(BaseModel):
    data: str
    suma: float
    partener: str = ""
    cui: str = ""
    document: str = ""
    factura_id: Optional[int] = None

@app.post("/tenants/{tenant_id}/bonuri/{bon_id}/stinge")
def chitanta_stinge(tenant_id: int, bon_id: int, c: ChitantaStinge,                     ctx=Depends(cere_rol("admin_firma"))):
    """Chitanta certificata de contabil: plata furnizor prin Registrul de casa
    (casa_api.adauga -> 401=5311 ciorna + operatiune casa + verificare plafon).
    Optional leaga si marcheaza platita factura primita."""
    try:
        return _uc_tenants.chitanta_stinge(tenant_id, bon_id, c, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

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
    try:
        return _uc_tenants.chitanta_emite(tenant_id, c, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.get("/tenants/{tenant_id}/chitante")
def chitante_lista(tenant_id: int, factura_id: Optional[int] = None, ctx=Depends(cere_context)):
    try:
        return _uc_tenants.chitante_lista(tenant_id, factura_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.get("/tenants/{tenant_id}/chitante/{chitanta_id}/pdf")
# [R52] Poartă numele și suma plătită de un terț.
def chitanta_pdf(tenant_id: int, chitanta_id: int, ctx=Depends(cere_rol("admin_firma"))):
    try:
        pdf, r = _uc_tenants.chitanta_pdf(tenant_id, chitanta_id, ctx)
        return Response(content=pdf, media_type="application/pdf",
                        headers={"Content-Disposition": 'attachment; filename="chitanta_%s_%s.pdf"' % (r[0], r[1])})
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.get("/portal/documente/luni")
def portal_documente_luni(tenant_id: Optional[int] = None, ctx=Depends(cere_client)):
    try:
        return _uc_portal.portal_documente_luni(tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)
@app.get("/tenants/{tenant_id}/balanta")
def cabinet_balanta_date(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    """[lista 5, 30.08.2026] Balanta ca DATE, nu ca PDF.

    Pana azi singura cale spre cifrele balantei era `documente/balanta`, care intoarce un fisier:
    ecranul avea titlu, navigare pe luna si un buton de descarcare, atat. O cifra pe care n-o poti
    citi decat descarcand-o nu se poate verifica pe ecran - chiar asta e criteriul listei 5.

    Inchiderea vine ODATA cu randurile, si ca obiect, nu ca propozitie: pe o balanta goala starea e
    `nimic_de_verificat`, nu `se_inchide`.
    """
    try:
        return _uc_tenants.cabinet_balanta_date(tenant_id, an, luna, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/tenants/{tenant_id}/registru-evidenta-fiscala")
def registru_fiscal_citeste(tenant_id: int, an: int, varianta: str = "profit",                             totalizare: str = "an", ctx=Depends(cere_cabinet)):
    """[lista 3, 30.08.2026] Registrul de evidență fiscală. Sunt DOUĂ, nu unul.

    `profit` — CF art. 19 alin. (7) + HG 1/2016 pct. 8, derivat din aceleași câmpuri din care iese
    D101. `venituri_pf` — CF art. 68 alin. (8)-(9) + OMFP 3254/2017, ținut pe fiecare sursă din
    fiecare categorie de venit.
    """
    try:
        return _uc_tenants.registru_fiscal_citeste(tenant_id, an, varianta, totalizare, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/registru-evidenta-fiscala")
def registru_fiscal_adauga(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """Înscrie un rând în varianta PERSOANE FIZICE — singura care se completează.

    Varianta pe profit se derivă din D101 și n-are ce primi: un `POST` pe ea ar însemna o a doua
    sursă de adevăr despre același an.
    """
    try:
        return _uc_tenants.registru_fiscal_adauga(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/tenants/{tenant_id}/registru-inventar")
def registru_inventar_citeste(tenant_id: int, exercitiu: int,                               momentul: str = "sfarsit_exercitiu",                               ctx=Depends(cere_cabinet)):
    """[lista 3, 30.08.2026] Registrul-inventar (cod 14-1-2), al doilea registru obligatoriu.

    Legea 82/1991 art. 20 il cere; OMFP 2634/2015 Anexa 2 ii spune continutul. Poarta COMUNA, ca la
    registrele art. 321 si din acelasi motiv.
    """
    try:
        return _uc_tenants.registru_inventar_citeste(tenant_id, exercitiu, momentul, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/tenants/{tenant_id}/registru-inventar/propunere")
def registru_inventar_propunere(tenant_id: int, an: int, luna: int = 12,                                 ctx=Depends(cere_cabinet)):
    """Coloana 3 PROPUSA din balanta — soldurile pe cont, ca sa nu fie retastate.

    Nu creeaza niciun rand si NU atinge coloana 4: valoarea de inventar vine din numararea faptica.
    Un ajutor care ar completa si coloana 4 ar produce un registru fara nicio diferenta, adica o
    inventariere perfecta care nu s-a facut.
    """
    try:
        return _uc_tenants.registru_inventar_propunere(tenant_id, an, luna, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/registru-inventar")
def registru_inventar_adauga(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """Inscrie un rand. Refuzul iese pe contractul comun `detail.erori_campuri`."""
    try:
        return _uc_tenants.registru_inventar_adauga(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


def _mesaj_scurt_inventar(e):
    """[P7 · use-case] Invelisul HTTP al lui `core/uc_comun._mesaj_scurt_inventar` — traduce refuzul de
    domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._mesaj_scurt_inventar(e)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/tenants/{tenant_id}/registre-art321/{fel}")
def registre_art321_citeste(tenant_id: int, fel: str, an: Optional[int] = None,                             ctx=Depends(cere_cabinet)):
    """[lista 3, 30.08.2026] Cele doua registre cerute de art. 321 alin. (4) CF, prin normele lui.

    POARTA COMUNA, nu cea de citire-istorica. Registrul e o clasa NOUA de acces, nu a doua iesire a
    unui artefact vechi — iar zavorul din `test_poarta_citire_istorica` cere exact ca o intrare care
    nu e nici din cele 13 de la deschidere, nici pereche declarata a uneia, sa nu treaca. Daca
    vreodata se va cere citirea registrului pe o firma scoasa din portofoliu, se declara acolo, cu
    propozitie scrisa.
    """
    try:
        return _uc_tenants.registre_art321_citeste(tenant_id, fel, an, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/registre-art321/{fel}")
def registre_art321_adauga(tenant_id: int, fel: str, corp: dict = Body(...),                            ctx=Depends(cere_cabinet)):
    """Inscrie un rand. Refuzul de completitudine iese ca 400 CU campul si temeiul, nu ca proza.

    Pe contractul care EXISTA deja — `detail.erori_campuri = [{camp, mesaj}]`, normalizat de
    `static/js/api.js` si randat de trei ecrane. Un contract paralel, oricat de bine gandit, ar fi
    insemnat ca acelasi fel de refuz se citeste in doua feluri; `temei` se adauga ALATURI de el,
    fiindca niciun refuz de-al nostru nu se rosteste fara norma pe care se sprijina.
    """
    try:
        return _uc_tenants.registre_art321_adauga(tenant_id, fel, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/tenants/{tenant_id}/documente/balanta")
def cabinet_documente_balanta(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    try:
        pdf = _uc_tenants.cabinet_documente_balanta(tenant_id, an, luna, ctx)
        return Response(content=pdf, media_type="application/pdf",
                        headers={"Content-Disposition": f'attachment; filename="balanta_{an}_{luna:02d}.pdf"'})
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.get("/portal/documente/balanta")
def portal_documente_balanta(an: int, luna: int, tenant_id: Optional[int] = None, ctx=Depends(cere_client)):
    try:
        pdf = _uc_portal.portal_documente_balanta(an, luna, tenant_id, ctx)
        return Response(content=pdf, media_type="application/pdf",
                        headers={"Content-Disposition": f'attachment; filename="balanta_{an}_{luna:02d}.pdf"'})
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)
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
    """[P7 · use-case] Invelisul HTTP al lui `core/uc_comun._api_schema` — traduce refuzul de
    domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._api_schema(actx, tenant_id)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/cabinet/api-chei")  # api_public_v1
def api_cheie_creeaza(corp: dict = Body(default={}), ctx=Depends(cere_rol("admin_firma"))):
    try:
        return _uc_cabinet.api_cheie_creeaza(corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/cabinet/api-chei")  # api_public_v1
def api_chei_lista(ctx=Depends(cere_rol("admin_firma"))):
    try:
        return _uc_cabinet.api_chei_lista(ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.delete("/cabinet/api-chei/{kid}")  # api_public_v1
def api_cheie_revoca(kid: int, ctx=Depends(cere_rol("admin_firma"))):
    try:
        return _uc_cabinet.api_cheie_revoca(kid, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/api/v1/firme")  # api_public_v1
def apiv1_firme(actx=Depends(cere_api_key)):
    try:
        return _uc_api.apiv1_firme(actx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/api/v1/firme/{tenant_id}/facturi")  # api_public_v1
def apiv1_facturi(tenant_id: int, an: Optional[int] = None, luna: Optional[int] = None,                   actx=Depends(cere_api_key)):
    try:
        return _uc_api.apiv1_facturi(tenant_id, an, luna, actx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/api/v1/firme/{tenant_id}/kpi")  # api_public_v1
def apiv1_kpi(tenant_id: int, an: Optional[int] = None, luna: Optional[int] = None,               actx=Depends(cere_api_key)):
    try:
        return _uc_api.apiv1_kpi(tenant_id, an, luna, actx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/api/v1/firme/{tenant_id}/balanta")  # api_public_v1
def apiv1_balanta(tenant_id: int, an: int, luna: int, actx=Depends(cere_api_key)):
    try:
        return _uc_api.apiv1_balanta(tenant_id, an, luna, actx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

# === LINK PLATA === scos 06.09.2026, odata cu retragerea caii de plata online (decizia 75).
# Ruta `POST /tenants/{tenant_id}/facturi/{factura_id}/link-plata` a fost STEARSA, nu lasata
# sa refuze: butonul care o chema nu mai exista, deci ea ramasese fara apelant — clasa R70.
# *O ruta care doar refuza nu e o poarta, e o ramasita.*

# === PLATA ONLINE === retrasa complet 06.09.2026 (decizia 75).
#
# Au fost trei rute: generarea linkului (din ecran) si cele doua publice (pagina + confirmarea).
# TOATE sunt scoase. Ordinea in care au cazut e a portii, si fiecare pas a fost intemeiat:
#   1. butonul scos din ecran  -> ruta de generare a ramas fara apelant (R70) -> scoasa;
#   2. confirmarea, care doar refuza -> «pas fara efect derivabil»: nu se mai poate scrie
#      nicio verificare pe ea -> scoasa;
#   3. pagina publica era piatra de mormant pentru un link vechi — dar linkuri vechi NU
#      EXISTA: masurat, ZERO generate vreodata pe toate cele 20 de firme. *O piatra de
#      mormant la care nu poate ajunge nimeni nu e o curtoazie, e cod mort.*
#
# Decizia, refuzul si motivul traiesc in `core/plati.py` (comutatorul `CALEA_ONLINE_ACTIVA`),
# pazite de `core/test_plata_izolare.py`. Reactivarea cere o decizie noua, nu un `if` sters.

@app.post("/api/v1/firme/{tenant_id}/facturi")  # api_public_v1
def apiv1_factura_emite(tenant_id: int, corp: dict = Body(...), actx=Depends(cere_api_key)):
    try:
        return _uc_api.apiv1_factura_emite(tenant_id, corp, actx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/woocommerce/sincronizeaza")  # wc_sinc_v1
def wc_sinc(tenant_id: int, ctx=Depends(cere_rol("admin_firma"))):
    from core import woocommerce as _wc
    schema = _schema_sau_404(ctx, tenant_id)
    # [P5 val 3] `sincronizeaza` isi deschide singura conexiunile: una pentru config, alta pentru
    # scriere — iar intre ele nu tine niciuna peste apelul de 30 s catre magazin.
    r = _wc.sincronizeaza(schema)
    if r.get("eroare"):
        _ec = r.get("erori_campuri")  # [G10] contract {mesaj, erori_campuri}
        raise HTTPException(422, detail={"mesaj": r["eroare"], "erori_campuri": _ec} if _ec else r["eroare"])
    return r


@app.get("/tenants/{tenant_id}/woocommerce/config")  # wc_config_get_v1
def wc_config_get(tenant_id: int, ctx=Depends(cere_context)):
    try:
        return _uc_tenants.wc_config_get(tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)
@app.put("/tenants/{tenant_id}/woocommerce/config")  # wc_sinc_v1
# [R42 (d)] Pornirea și oprirea unui canal cer `admin_firma`. Costin: *„nu e organizare internă —
# e o decizie despre cum comunică firma cu autoritatea și cu clienții."* Ruta asta scrie chiar
# cheile canalului: cu ele pline canalul e pornit, golite îl oprește.
def wc_config(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_rol("admin_firma"))):
    try:
        return _uc_tenants.wc_config(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/cabinet/consolidare")  # consolidare_v1
def cabinet_consolidare(an: Optional[int] = None, luna: Optional[int] = None,                         ctx=Depends(cere_cabinet)):
    try:
        return _uc_cabinet.cabinet_consolidare(an, luna, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/portal/kpi")  # portal_kpi_v1
def portal_kpi(an: Optional[int] = None, luna: Optional[int] = None,                tenant_id: Optional[int] = None, ctx=Depends(cere_client)):
    try:
        return _uc_portal.portal_kpi(an, luna, tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/portal/cashflow")  # portal_cashflow_v1
def portal_cashflow(tenant_id: Optional[int] = None, ctx=Depends(cere_client)):
    try:
        return _uc_portal.portal_cashflow(tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/portal/facturi")
def portal_facturi(tenant_id: Optional[int] = None, an: Optional[int] = None,                    luna: Optional[int] = None, ctx=Depends(cere_client)):
    try:
        return _uc_portal.portal_facturi(tenant_id, an, luna, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/portal/declaratii")
def portal_declaratii(tenant_id: Optional[int] = None, ctx=Depends(cere_client)):
    try:
        return _uc_portal.portal_declaratii(tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

# ICRD_RECOMANDA_UNIFICAT_V1
def _trimite_recomandari(emails, html, subiect):
    """[P7 · use-case, lotul 2] Invelisul HTTP al lui `core/uc_comun._trimite_recomandari` — traduce
    refuzul de domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._trimite_recomandari(emails, html, subiect)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

def _mesaj_recomanda_client_html(nume_firma):
    """[P7 · use-case, lotul 2] Invelisul HTTP al lui `core/uc_comun._mesaj_recomanda_client_html` — traduce
    refuzul de domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._mesaj_recomanda_client_html(nume_firma)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

class RecomandareClientIn(BaseModel):
    emails: list[str]

@app.get("/portal/recomanda/preview")
def portal_recomanda_preview(tenant_id: Optional[int] = None, ctx=Depends(cere_client)):
    try:
        return _uc_portal.portal_recomanda_preview(tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/portal/recomanda")
def portal_recomanda(date: RecomandareClientIn, tenant_id: Optional[int] = None, ctx=Depends(cere_client)):
    try:
        return _uc_portal.portal_recomanda(date, tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/portal/povesti")
def portal_povesti(tenant_id: Optional[int] = None, ctx=Depends(cere_client)):
    try:
        return _uc_portal.portal_povesti(tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

# ICRD_SOLICITARI_V1 - bucla solicitari client <-> cabinet
class SolicitareIn(BaseModel):
    mesaj: str

@app.get("/portal/solicitari/contor")  # [icrd_sol_badge_v1] necitite de la cabinet, pt clientul curent
def portal_solicitari_contor(tenant_id: Optional[int] = None, ctx=Depends(cere_client)):
    try:
        return _uc_portal.portal_solicitari_contor(tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.get("/portal/solicitari")
def portal_solicitari_lista(tenant_id: Optional[int] = None, ctx=Depends(cere_client)):
    try:
        return _uc_portal.portal_solicitari_lista(tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/portal/solicitari")
def portal_solicitari_trimite(date: SolicitareIn, tenant_id: Optional[int] = None, ctx=Depends(cere_client)):
    try:
        return _uc_portal.portal_solicitari_trimite(date, tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.get("/tenants/{tenant_id}/solicitari")
def cabinet_solicitari_lista(tenant_id: int, ctx=Depends(cere_context)):
    try:
        return _uc_tenants.cabinet_solicitari_lista(tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/tenants/{tenant_id}/solicitari")
# [R42] „iese către un om" — răspunsul pleacă pe email la clientul firmei.
def cabinet_solicitari_raspunde(tenant_id: int, date: SolicitareIn,                                 ctx=Depends(cere_rol("admin_firma"))):
    try:
        return _uc_tenants.cabinet_solicitari_raspunde(tenant_id, date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/portal/acasa")  # [p91_portal_acasa] status ANAF + scadente pentru firma clientului
def portal_acasa(tenant_id: Optional[int] = None, ctx=Depends(cere_client)):
    try:
        return _uc_portal.portal_acasa(tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


# === ASISTENTI_API ROUTES ===


def _cer_admin_cabinet(ctx):
    """[P7 · use-case] Invelisul HTTP al lui `core/uc_comun._cer_admin_cabinet` — traduce refuzul de
    domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._cer_admin_cabinet(ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/asistenti")
def asistenti_lista(ctx=Depends(cere_cabinet)):
    try:
        return _uc_asistenti.asistenti_lista(ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/asistenti/{uid}")
def asistenti_detalii(uid: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_asistenti.asistenti_detalii(uid, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


# === ASISTENT NOU === # asistent_nou_v1
class AsistentNouIn(BaseModel):
    email: str
    nume: str = ""
    poate_valida: bool = False

@app.post("/asistenti")
def asistent_creeaza(date: AsistentNouIn, ctx=Depends(cere_rol("admin_firma"))):
    try:
        return _uc_asistenti.asistent_creeaza(date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/asistenti/{uid}/permisiuni")
def asistenti_permisiuni(uid: int, date: dict = Body(...), ctx=Depends(cere_cabinet)):
    try:
        return _uc_asistenti.asistenti_permisiuni(uid, date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/asistenti/{uid}/firme/{tid}")
def asistenti_atribuie(uid: int, tid: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_asistenti.asistenti_atribuie(uid, tid, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.delete("/asistenti/{uid}/firme/{tid}")
def asistenti_elimina(uid: int, tid: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_asistenti.asistenti_elimina(uid, tid, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/asistenti/{uid}/dezactiveaza")
def asistenti_dezactiveaza(uid: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_asistenti.asistenti_dezactiveaza(uid, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/asistenti/{uid}/reactiveaza")
def asistenti_reactiveaza(uid: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_asistenti.asistenti_reactiveaza(uid, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)



# [patch7_finalizeaza_firme]
@app.post("/asistenti/{uid}/finalizeaza-firme")
def asistenti_finalizeaza_firme(uid: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_asistenti.asistenti_finalizeaza_firme(uid, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)



# [patch9_semafor_rute]
@app.get("/asistenti/echipa/semafor")
def asistenti_semafor(zile: int = 30, ctx=Depends(cere_cabinet)):
    try:
        return _uc_asistenti.asistenti_semafor(zile, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/asistenti/echipa/erori")
def asistenti_erori(zile: int = 30, ctx=Depends(cere_cabinet)):
    try:
        return _uc_asistenti.asistenti_erori(zile, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

# [p16_activitate_cabinet_routes]
@app.get("/asistenti/echipa/centralizator")
def asistenti_centralizator(de: Optional[str] = None, pana: Optional[str] = None,                             ctx=Depends(cere_cabinet)):
    try:
        return _uc_asistenti.asistenti_centralizator(de, pana, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/asistenti/echipa/jurnal")
def asistenti_jurnal(de: Optional[str] = None, pana: Optional[str] = None,                      limit: int = 200, ctx=Depends(cere_cabinet)):
    try:
        return _uc_asistenti.asistenti_jurnal(de, pana, limit, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


# [patch_asistenti_calitate]
@app.get("/asistenti/{uid}/calitate")
def asistenti_calitate(uid: int, de: Optional[str] = None,                        pana: Optional[str] = None, ctx=Depends(cere_cabinet)):
    try:
        return _uc_asistenti.asistenti_calitate(uid, de, pana, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/asistenti/{uid}/activitate")
def asistenti_activitate(uid: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_asistenti.asistenti_activitate(uid, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


# [p18_selfview]
@app.get("/eu/calitate")
def eu_calitate(de: Optional[str] = None, pana: Optional[str] = None,                 ctx=Depends(cere_cabinet)):
    """Self-view: propria calitate (nivel, semafor, rata, tipare). uid din token."""
    try:
        return _uc_eu.eu_calitate(de, pana, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)




# [p27_setari_routes]
class SchimbaParolaIn(BaseModel):
    parola_veche: str
    parola_noua: str


class ProfilIn(BaseModel):
    nume: Optional[str] = None
    prenume: Optional[str] = None


# [p47_compet]
class CompetenteIn(BaseModel):
    # [lotul 9, 04.09.2026] Cele trei aveau implicit `False`, deci un corp GOL insemna „scoate-mi
    # toate drepturile" — si chiar asta s-a intamplat la proba: patronul 1968, care depusese o
    # declaratie prin interfata cu o zi inainte, a ramas fara `poate_depune`. *Absenta unui camp nu
    # e un raspuns; un drept nu se pierde din tacere.* Fara implicit: cine seteaza competentele le
    # declara pe toate trei, iar cine nu trimite nimic primeste un refuz, nu o golire.
    poate_pregati: bool
    poate_valida: bool
    poate_depune: bool

# [p50_edu]
@app.get("/eu/educatie")
def eu_educatie(ctx=Depends(cere_cabinet)):
    try:
        return _uc_eu.eu_educatie(ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

# [p54_4ochi]
class PatruOchiIn(BaseModel):
    activ: bool

@app.get("/eu/patru-ochi")  # po_stare_v1
def eu_patru_ochi_stare(ctx=Depends(cere_cabinet)):
    """[po_efectiv_v1] {activ, posibil, efectiv} din SURSA UNICA folosita si de enforcement
    (core.coada_api.patru_ochi_stare). Inainte intorcea DOAR flagul brut `activ`, iar UI-ul
    afisa "validarea in doi ✓" pe un cabinet cu un singur validator - divergenta front<->back."""
    try:
        return _uc_eu.eu_patru_ochi_stare(ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/eu/patru-ochi")
def eu_patru_ochi(date: PatruOchiIn, ctx=Depends(cere_cabinet)):
    try:
        return _uc_eu.eu_patru_ochi(date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/eu/educatie/patru-ochi/vazut")
def eu_educatie_vazut(ctx=Depends(cere_cabinet)):
    try:
        return _uc_eu.eu_educatie_vazut(ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/eu/competente")
def eu_competente_get(ctx=Depends(cere_cabinet)):
    try:
        return _uc_eu.eu_competente_get(ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/eu/competente")
def eu_competente_set(date: CompetenteIn, ctx=Depends(cere_cabinet)):
    try:
        return _uc_eu.eu_competente_set(date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/eu/schimba-parola")
def eu_schimba_parola(date: SchimbaParolaIn, ctx=Depends(cere_cabinet)):
    try:
        return _uc_eu.eu_schimba_parola(date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/eu/profil")
def eu_profil(date: ProfilIn, ctx=Depends(cere_cabinet)):
    try:
        return _uc_eu.eu_profil(date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


# [p29_cabinet_routes]
class CabinetIn(BaseModel):
    nume: Optional[str] = None
    cui: Optional[str] = None


@app.get("/eu/cabinet")
def eu_cabinet_get(ctx=Depends(cere_cabinet)):
    try:
        return _uc_eu.eu_cabinet_get(ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/eu/cabinet")
def eu_cabinet_set(date: CabinetIn, ctx=Depends(cere_cabinet)):
    try:
        return _uc_eu.eu_cabinet_set(date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


# [p30_recomanda]


def _mesaj_promo_html(nume_cabinet):
    """[P7 · use-case, lotul 2] Invelisul HTTP al lui `core/uc_comun._mesaj_promo_html` — traduce
    refuzul de domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._mesaj_promo_html(nume_cabinet)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


class RecomandareIn(BaseModel):
    emails: list[str]


# [p67_recprev]
@app.get("/recomanda/preview")
def recomanda_preview(ctx=Depends(cere_cabinet)):
    try:
        return _uc_recomanda.recomanda_preview(ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/recomanda")
def trimite_recomandari(date: RecomandareIn, ctx=Depends(cere_cabinet)):
    try:
        return _uc_recomanda.trimite_recomandari(date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


# [p33_raportari]
class RaportareNouaIn(BaseModel):
    subiect: Optional[str] = None
    text: str


class MesajIn(BaseModel):
    text: str


@app.post("/raportari")
def raportari_creeaza(date: RaportareNouaIn, ctx=Depends(cere_cabinet)):
    try:
        return _uc_raportari.raportari_creeaza(date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/raportari/eu")
def raportari_mele(ctx=Depends(cere_cabinet)):
    try:
        return _uc_raportari.raportari_mele(ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/raportari/contor")
def raportari_contor(ctx=Depends(cere_cabinet)):
    try:
        return _uc_raportari.raportari_contor(ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/raportari/admin")
def raportari_admin(ctx=Depends(cere_cabinet)):
    try:
        return _uc_raportari.raportari_admin(ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/raportari/{rid}")
def raportari_fir(rid: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_raportari.raportari_fir(rid, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/raportari/{rid}/mesaj")
def raportari_mesaj(rid: int, date: MesajIn, ctx=Depends(cere_cabinet)):
    try:
        return _uc_raportari.raportari_mesaj(rid, date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/raportari/{rid}/citit")
def raportari_citit(rid: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_raportari.raportari_citit(rid, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


# [p38_pentru_admin]
class StareIn(BaseModel):
    stare: str

class PentruAdminIn(BaseModel):
    valoare: bool = True

@app.post("/raportari/{rid}/stare")  # [inchidere_v1]
def raportari_stare(rid: int, date: StareIn, ctx=Depends(cere_rol("superadmin"))):
    try:
        return _uc_raportari.raportari_stare(rid, date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/raportari/{rid}/pentru-admin")
def raportari_pentru_admin(rid: int, date: PentruAdminIn, ctx=Depends(cere_cabinet)):
    try:
        return _uc_raportari.raportari_pentru_admin(rid, date, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


# [p35_raportari_imagine]
@app.post("/raportari/mesaj/{mid}/imagine")
def raportari_imagine(mid: int, fisier: UploadFile = File(...), ctx=Depends(cere_cabinet)):
    try:
        return _uc_raportari.raportari_imagine(mid, _octetii(fisier), fisier.filename, fisier.content_type, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)
# === /ASISTENTI_API ROUTES ===


# === PERMISIUNI FLUX (coada) ===
def _are_permisiune(ctx, flag):
    """[P7 · use-case] Invelisul HTTP al lui `core/uc_comun._are_permisiune` — traduce refuzul de
    domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._are_permisiune(ctx, flag)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/eu/permisiuni")
def eu_permisiuni(ctx=Depends(cere_cabinet)):
    """Permisiunile actorului curent — pentru ca frontendul să rescrie butoanele
    fără relogare (permisiunile se schimbă din cardul Asistenți)."""
    try:
        return _uc_eu.eu_permisiuni(ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)
# === /PERMISIUNI FLUX ===


# --- reconciliere bancara ---
@app.post("/tenants/{tenant_id}/banca/reconciliere/import")
def banca_rec_import(tenant_id: int, fisier: UploadFile = File(...), ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.banca_rec_import(tenant_id, _octetii(fisier), fisier.filename, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.get("/tenants/{tenant_id}/banca/reconciliere")
def banca_rec_lista(tenant_id: int, status: str = None, ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.banca_rec_lista(tenant_id, status, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/tenants/{tenant_id}/banca/reconciliere/{linie_id}/conteaza")
def banca_rec_conteaza(tenant_id: int, linie_id: int, corp: dict = Body(default={}), ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.banca_rec_conteaza(tenant_id, linie_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/tenants/{tenant_id}/banca/reconciliere/facturi-deschise")
def banca_rec_facturi(tenant_id: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.banca_rec_facturi(tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


# --- rapoarte comerciale (F144 v1, read-only) ---
def _perioada_an(de, pana):
    """[P7 · use-case] Invelisul HTTP al lui `core/uc_comun._perioada_an` — traduce refuzul de
    domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._perioada_an(de, pana)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.get("/tenants/{tenant_id}/rapoarte-comerciale")
def rapoarte_comerciale(tenant_id: int, de: str = None, pana: str = None, ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.rapoarte_comerciale(tenant_id, de, pana, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.get("/tenants/{tenant_id}/rapoarte-comerciale/fisa")
def rapoarte_comerciale_fisa(tenant_id: int, cui: str, de: str = None, pana: str = None, ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.rapoarte_comerciale_fisa(tenant_id, cui, de, pana, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


# --- rapoarte salvate (F145: variante ale firmei, partajate) ---
@app.get("/tenants/{tenant_id}/rapoarte-salvate")
def rapoarte_salvate_lista(tenant_id: int, tip_raport: str = "comercial", ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.rapoarte_salvate_lista(tenant_id, tip_raport, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/tenants/{tenant_id}/rapoarte-salvate")
def rapoarte_salvate_creeaza(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.rapoarte_salvate_creeaza(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.delete("/tenants/{tenant_id}/rapoarte-salvate/{vid}")
def rapoarte_salvate_sterge(tenant_id: int, vid: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.rapoarte_salvate_sterge(tenant_id, vid, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


# --- registratura documente (F146: registru unic intrare-iesire) ---
@app.get("/tenants/{tenant_id}/registratura")
def registratura_lista(tenant_id: int, an: int = None, ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.registratura_lista(tenant_id, an, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/tenants/{tenant_id}/registratura")
def registratura_creeaza(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.registratura_creeaza(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


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
    try:
        return _uc_tenants.contracte_sabloane_lista(tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/tenants/{tenant_id}/contracte/sabloane")
def contracte_sabloane_salveaza(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.contracte_sabloane_salveaza(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.delete("/tenants/{tenant_id}/contracte/sabloane/{sid}")
def contracte_sabloane_sterge(tenant_id: int, sid: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.contracte_sabloane_sterge(tenant_id, sid, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/tenants/{tenant_id}/contracte/genereaza")
# [R42] „iese către un om" — contractul individual de muncă.
def contracte_genereaza(tenant_id: int, corp: dict = Body(...),
                        ctx=Depends(cere_rol("admin_firma"))):
    try:
        pdf = _uc_tenants.contracte_genereaza(tenant_id, corp, ctx)
        return Response(content=pdf, media_type="application/pdf",
                        headers={"Content-Disposition": 'attachment; filename="contract.pdf"'})
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


# --- export facturi emise catre SAGA (F171, read-only) ---
@app.get("/tenants/{tenant_id}/facturi/{factura_id}/export-saga")
def export_saga_factura(tenant_id: int, factura_id: int, ctx=Depends(cere_context)):
    try:
        xml, nume = _uc_tenants.export_saga_factura(tenant_id, factura_id, ctx)
        return Response(content=xml, media_type="application/xml",
                        headers={"Content-Disposition": 'attachment; filename="%s"' % nume})
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/tenants/{tenant_id}/facturi/export-saga")
# [R45] POST: exportul e un act (ce s-a exportat și când e chiar întrebarea la o preluare
# inversă), iar un GET n-are voie să scrie.
def export_saga_luna(tenant_id: int, an: int, luna: int, ctx=Depends(cere_rol("admin_firma"))):
    try:
        buf, nume_zip = _uc_tenants.export_saga_luna(tenant_id, an, luna, ctx)
        return Response(content=buf.getvalue(), media_type="application/zip",
                        headers={"Content-Disposition": 'attachment; filename="%s"' % nume_zip})
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/facturi/export-winmentor")  # [F187]
# [R45] POST: acelasi motiv ca la SAGA — exportul e un act, iar un GET n-are voie sa scrie.
def export_winmentor_luna(tenant_id: int, an: int, luna: int,
                          ctx=Depends(cere_rol("admin_firma"))):
    """Export WinMENTOR: Facturi.txt + Articole.txt (Windows-1250) co-locate intr-un zip.
    Facturile emise ale lunii (paritate cu SAGA, fara filtru status). Dependenta de config nomenclator WinMentor (vezi export_winmentor)."""
    try:
        buf, nume_zip = _uc_tenants.export_winmentor_luna(tenant_id, an, luna, ctx)
        return Response(content=buf.getvalue(), media_type="application/zip",
                        headers={"Content-Disposition": 'attachment; filename="%s"' % nume_zip})
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


# --- jurnal: editare/stergere/validare ciorne ---
def _jurnal_rez(rez):
    """[P7 · use-case, lotul 2] Invelisul HTTP al lui `core/uc_comun._jurnal_rez` — traduce
    refuzul de domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._jurnal_rez(rez)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/tenants/{tenant_id}/jurnal")
def jurnal_creeaza(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.jurnal_creeaza(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)
@app.put("/tenants/{tenant_id}/jurnal/{nota_id}")
def jurnal_editeaza(tenant_id: int, nota_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.jurnal_editeaza(tenant_id, nota_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.delete("/tenants/{tenant_id}/jurnal/{nota_id}")
def jurnal_sterge(tenant_id: int, nota_id: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.jurnal_sterge(tenant_id, nota_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

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
    try:
        return _uc_tenants.jurnal_dezleaga(tenant_id, nota_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


def _urma_dezlegare(conn, uid, tenant_id, nota_id, factura_id, motiv):
    """[P7 · use-case, lotul 2] Invelisul HTTP al lui `core/uc_comun._urma_dezlegare` — traduce
    refuzul de domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._urma_dezlegare(conn, uid, tenant_id, nota_id, factura_id, motiv)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/jurnal/{nota_id}/valideaza")
# [R55, 26.08.2026] Validarea e pasul care transforma o CIORNA in EVIDENTA — deci intra sub
# criteriul „ce schimba ce datoreaza firma" (R42, extins). Crearea, editarea si stergerea raman
# pe `cere_cabinet`: citite la sursa, `jurnal_api.editeaza` si `.sterge` refuza orice nota care
# nu e `ciorna`, deci nu ating evidenta. E munca zilnica a asistentului.
def jurnal_valideaza(tenant_id: int, nota_id: int, ctx=Depends(cere_rol("admin_firma"))):
    try:
        return _uc_tenants.jurnal_valideaza(tenant_id, nota_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


# [F143 Faza 1] centre de cost — nomenclator per firma (dimensiune pe linia de nota)
@app.get("/tenants/{tenant_id}/centre-cost")
def centre_cost_lista(tenant_id: int, doar_active: bool = False, ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.centre_cost_lista(tenant_id, doar_active, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/tenants/{tenant_id}/centre-cost")
def centre_cost_adauga(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.centre_cost_adauga(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.put("/tenants/{tenant_id}/centre-cost/{centru_id}")
def centre_cost_activ(tenant_id: int, centru_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.centre_cost_activ(tenant_id, centru_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.get("/tenants/{tenant_id}/centre-cost/raport")
def centre_cost_raport(tenant_id: int, de: str, pana: str, ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.centre_cost_raport(tenant_id, de, pana, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

# [F143 Faza 2] bugete anuale pe centru + varianta buget vs realizat
@app.get("/tenants/{tenant_id}/centre-cost/varianta")
def centre_cost_varianta(tenant_id: int, an: int, ctx=Depends(cere_cabinet)):
    """Buget vs realizat pe an, per centru (note validate, clasele 6/7)."""
    try:
        return _uc_tenants.centre_cost_varianta(tenant_id, an, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.put("/tenants/{tenant_id}/centre-cost/{centru_id}/buget")
def centre_cost_buget(tenant_id: int, centru_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """Seteaza bugetul anual (cheltuieli + venituri) al unui centru pe un an."""
    try:
        return _uc_tenants.centre_cost_buget(tenant_id, centru_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/banca/reconciliere/{linie_id}/ignora")
def banca_rec_ignora(tenant_id: int, linie_id: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.banca_rec_ignora(tenant_id, linie_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


# --- registru incasari/plati (RIP) ---
def _rip_ctx(conn, ctx, tenant_id):
    """[P7 · use-case] Invelisul HTTP al lui `core/uc_comun._rip_ctx` — traduce refuzul de
    domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._rip_ctx(conn, ctx, tenant_id)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.get("/tenants/{tenant_id}/rip/registru")
def rip_lista(tenant_id: int, an: int, luna: int = None, status: str = None, ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.rip_lista(tenant_id, an, luna, status, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/tenants/{tenant_id}/rip/operatiuni")
def rip_adauga(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.rip_adauga(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.put("/tenants/{tenant_id}/rip/operatiuni/{op_id}/valideaza")
def rip_valideaza(tenant_id: int, op_id: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.rip_valideaza(tenant_id, op_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.delete("/tenants/{tenant_id}/rip/operatiuni/{op_id}")
def rip_sterge(tenant_id: int, op_id: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.rip_sterge(tenant_id, op_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/tenants/{tenant_id}/rip/import-banca")
def rip_import_banca(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.rip_import_banca(tenant_id, an, luna, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/tenants/{tenant_id}/rip/import-casa")
def rip_import_casa(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.rip_import_casa(tenant_id, an, luna, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.get("/tenants/{tenant_id}/rip/inventar/{an}")
def rip_inventar(tenant_id: int, an: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.rip_inventar(tenant_id, an, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.get("/tenants/{tenant_id}/rip/d212/{an}")
def rip_d212(tenant_id: int, an: int, optiune_cas: bool = False, optiune_cass: bool = False, ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.rip_d212(tenant_id, an, optiune_cas, optiune_cass, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

# --- registru de casa ---
@app.get("/tenants/{tenant_id}/concedii/coduri")  # [cm_coduri_v1] denumirea din nomenclator + procentul din registru
def concedii_coduri(tenant_id: int, la_data: Optional[str] = None, ctx=Depends(cere_cabinet)):
    """Codurile de indemnizatie pentru ecran, cu procentul VALABIL LA DATA certificatului.

    Inainte de 22.08.2026 lista traia scrisa de mana in `flux_concediu.js` (18 coduri, cu procentele
    lipite in eticheta): ecranul NU oferea 11/91/92 - coduri legale pe care aplicatia le accepta -
    deci bloca un contabil sa introduca un cod valid. Vezi `core/coduri_cm_api.py`."""
    try:
        return _uc_tenants.concedii_coduri(tenant_id, la_data, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/tenants/{tenant_id}/casa/registru")
def casa_registru(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.casa_registru(tenant_id, an, luna, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/tenants/{tenant_id}/casa/operatiuni")
def casa_adauga(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.casa_adauga(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.delete("/tenants/{tenant_id}/casa/operatiuni/{op_id}")
def casa_sterge(tenant_id: int, op_id: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.casa_sterge(tenant_id, op_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


# --- stocuri global-valorica ---
@app.get("/tenants/{tenant_id}/stocuri/nir")
def stocuri_lista(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.stocuri_lista(tenant_id, an, luna, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/tenants/{tenant_id}/stocuri/nir")
def stocuri_adauga(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.stocuri_adauga(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/tenants/{tenant_id}/stocuri/descarcare")
def stocuri_descarcare(tenant_id: int, an: int, luna: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.stocuri_descarcare(tenant_id, an, luna, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


# --- stocuri cantitativ-valorice ---
@app.get("/tenants/{tenant_id}/stocuri/articole")
def cv_articole(tenant_id: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.cv_articole(tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.get("/tenants/{tenant_id}/stocuri/articole/{articol_id}/fisa")
def cv_fisa(tenant_id: int, articol_id: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.cv_fisa(tenant_id, articol_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/tenants/{tenant_id}/stocuri/intrare")
def cv_intrare(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.cv_intrare(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/tenants/{tenant_id}/stocuri/iesire")
def cv_iesire(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.cv_iesire(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/stocuri/inventar")
def cv_inventar(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.cv_inventar(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/tenants/{tenant_id}/stocuri/locatii")
def cv_locatii(tenant_id: int, articol_id: int = None, ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.cv_locatii(tenant_id, articol_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/stocuri/transfer")
def cv_transfer(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.cv_transfer(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/stocuri/reclasificare")
def cv_reclasificare(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.cv_reclasificare(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/tenants/{tenant_id}/stocuri/analitica")
def cv_analitica(tenant_id: int, zile_inert: int = 90, ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.cv_analitica(tenant_id, zile_inert, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/stocuri/articole/{articol_id}/nivel-minim")
def cv_nivel_minim(tenant_id: int, articol_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.cv_nivel_minim(tenant_id, articol_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/tenants/{tenant_id}/stocuri/barcode/{cod}")
def cv_barcode_gaseste(tenant_id: int, cod: str, ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.cv_barcode_gaseste(tenant_id, cod, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/stocuri/articole/{articol_id}/barcode")
def cv_barcode_set(tenant_id: int, articol_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.cv_barcode_set(tenant_id, articol_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


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
    try:
        return _uc_tenants.cabinet_categorie_marime(tenant_id, an, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/tenants/{tenant_id}/s1005-xml")
def s1005_xml(tenant_id: int, an: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.s1005_xml(tenant_id, an, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/tenants/{tenant_id}/s1005-valideaza")
# [R45] Artefactul care încheie exercițiul financiar se PĂSTREAZĂ: conținutul, momentul,
# autorul, amprenta, numărul exemplarului — plus verdictul cu amprenta fișierului validat.
# Se scrie aici, nu pe `-xml`: aia e o citire (GET), asta e actul.
def s1005_valideaza(tenant_id: int, an: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.s1005_valideaza(tenant_id, an, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


# --- S1003 (bilant mici) ---
@app.get("/tenants/{tenant_id}/s1003-xml")
def s1003_xml(tenant_id: int, an: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.s1003_xml(tenant_id, an, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/tenants/{tenant_id}/s1003-valideaza")
# [R45] Artefactul care încheie exercițiul financiar se PĂSTREAZĂ: conținutul, momentul,
# autorul, amprenta, numărul exemplarului — plus verdictul cu amprenta fișierului validat.
# Se scrie aici, nu pe `-xml`: aia e o citire (GET), asta e actul.
def s1003_valideaza(tenant_id: int, an: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.s1003_valideaza(tenant_id, an, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


# --- Retetar HoReCa ---
@app.get("/tenants/{tenant_id}/retete")
def retete_lista(tenant_id: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.retete_lista(tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/tenants/{tenant_id}/retete")
def retete_salveaza(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.retete_salveaza(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.delete("/tenants/{tenant_id}/retete/{reteta_id}")
def retete_sterge(tenant_id: int, reteta_id: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.retete_sterge(tenant_id, reteta_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/tenants/{tenant_id}/retete/descarca")
def retete_descarca(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.retete_descarca(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/tenants/{tenant_id}/verificare-stocuri")
def verificare_stocuri(tenant_id: int, ctx=Depends(cere_cabinet)):
    """Compara soldul contabil (solduri_initiale + note validate) pe fiecare cont de stoc
    folosit in articole cu valoarea insumata a fiselor CV (cantitate x CMP)."""
    try:
        return _uc_tenants.verificare_stocuri(tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


# --- e-Transport (v1: XML pt upload manual in SPV; API OAuth = etapa 2) ---
@app.post("/tenants/{tenant_id}/etransport-xml")
def etransport_xml(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.etransport_xml(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/etransport/trimite")
# [R42] „iese către o autoritate" — declarația UIT ajunge la ANAF.
def etransport_trimite(tenant_id: int, corp: dict = Body(...),                        ctx=Depends(cere_rol("admin_firma"))):
    """Trimite notificarea UIT in SPV (F121): genereaza XML + trimite() cu PORTI in ordine (garda de timp
    -> idempotency -> validare pe TEST -> upload). Poll-ul stare NU e sincron. Live pending drept e-Transport."""
    try:
        return _uc_tenants.etransport_trimite(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/tenants/{tenant_id}/etransport/trimiteri")
def etransport_trimiteri_lista(tenant_id: int, ctx=Depends(cere_context)):
    """UIT-uri trimise + semafor de TIMP (valabilitate UIT) SEPARAT de semaforul de trimitere. Fara apel ANAF."""
    try:
        return _uc_tenants.etransport_trimiteri_lista(tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/banca/reconciliere/{linie_id}/reactiveaza")
def banca_rec_reactiveaza(tenant_id: int, linie_id: int, ctx=Depends(cere_cabinet)):
    try:
        return _uc_tenants.banca_rec_reactiveaza(tenant_id, linie_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


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
    try:
        return _uc_tenants.factura_recunoaste(tenant_id, factura_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


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
    try:
        return _uc_tenants.factura_contabilizeaza(tenant_id, factura_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)



@app.post("/tenants/{tenant_id}/vanzare-marja")
def vanzare_marja(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, pret_vanzare, pret_cumparare, cota?, descriere?}. Nota ciorna
    regim marja (art. 312): 4111=707 cost + 4111=707 marja neta + 4111=4427 TVA marja."""
    try:
        return _uc_tenants.vanzare_marja(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/vanzare-marja-turism")
def vanzare_marja_turism(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, calitate_client PF|PJ, locuri [RO|UE|NONUE], optiune_normal?,
    intermediar?, cota?, descriere?} + per regim:
    special: incasat, cost_ue, cost_non_ue? | normal: componente [{descriere,baza,cota}]
    | intermediar: comision, tva_inclus?. Nota intra mereu ciorna (art. 311 CF)."""
    try:
        return _uc_tenants.vanzare_marja_turism(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/vanzare-aur-investitii")
def vanzare_aur_investitii(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, tip lingou|plancheta|moneda, puritate, an_emisie?, pret_unitar?,
    valoare_aur?, suma, optiune_taxare?, calitate_client PF|PJ, client_identificare,
    descriere?}. Scutit (art. 313 al. 3) sau taxare inversa (art. 331 al. 2 lit. h).
    Nota ciorna: 4111=707 fara TVA."""
    try:
        return _uc_tenants.vanzare_aur_investitii(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/achizitie-agricultor")
def achizitie_agricultor(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, valoare (fara taxa), cont_cheltuiala, agricultor_in_registru,
    agricultor?, descriere?}. Nota ciorna: % cont_chelt + 4426(compensatie 8%) = 401."""
    try:
        return _uc_tenants.achizitie_agricultor(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


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
    try:
        return _uc_tenants.vanzare_agricultor(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/tenants/{tenant_id}/fisa-cont")
def cabinet_fisa_cont(tenant_id: int, an: int, cont: Optional[str] = None,                       luna: Optional[int] = None, ctx=Depends(cere_cabinet)):
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
    try:
        return _uc_tenants.cabinet_fisa_cont(tenant_id, an, cont, luna, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/tenants/{tenant_id}/jurnal-marja")  # [api_intern_v1] raport regim marja - fara UI inca, pastrat deliberat
def jurnal_marja(tenant_id: int, tip: str, luna: str, ctx=Depends(cere_cabinet)):
    """tip: secondhand|turism; luna: YYYY-MM. Jurnal special vanzari regim marja:
    per nota cost/marja neta/TVA + totaluri perioada (norme pct. 86)."""
    try:
        return _uc_tenants.jurnal_marja(tenant_id, tip, luna, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/tenants/{tenant_id}/d406-active")  # [api_intern_v1] SAF-T sub-sectiune - fara UI inca, pastrat deliberat
def d406_active_xml(tenant_id: int, an: int, ctx=Depends(cere_cabinet)):
    """Sectiunea Assets SAF-T pentru anul dat (D406 anual - active)."""
    try:
        xml = _uc_tenants.d406_active_xml(tenant_id, an, ctx)
        return Response(content=xml, media_type="application/xml")
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/tenants/{tenant_id}/d406-stocuri")  # [api_intern_v1] SAF-T sub-sectiune - fara UI inca, pastrat deliberat
def d406_stocuri_xml(tenant_id: int, data_start: str, data_end: str, cui: str,
                     ctx=Depends(cere_cabinet)):
    """Sectiunea PhysicalStock SAF-T pe perioada (D406 la cerere ANAF).
    data_start/data_end: YYYY-MM-DD; cui: OwnerID (CUI firma)."""
    try:
        xml = _uc_tenants.d406_stocuri_xml(tenant_id, data_start, data_end, cui, ctx)
        return Response(content=xml, media_type="application/xml")
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)




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
    try:
        return _uc_tenants.calcul_cm_endpoint(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/facturi/{factura_id}/trimite-spv")
# [R42] „iese către o autoritate" — e-Factura ajunge la ANAF.
def factura_trimite_spv(tenant_id: int, factura_id: int, ctx=Depends(cere_rol("admin_firma"))):
    """Trimite o factura emisa in SPV (F126/F160). Porti in ordine fixa (efactura_trimitere.trimite):
    token viu -> validare/FACT1 -> idempotency -> upload pe tokenul PRINCIPALULUI (cabinet/gratuit).
    Poll-ul stareMesaj/descarcare ramane pe cron. Recipisa live = pending drept (ca F176)."""
    try:
        return _uc_tenants.factura_trimite_spv(tenant_id, factura_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/tenants/{tenant_id}/trimiteri-spv")
def facturi_trimiteri_spv(tenant_id: int, ctx=Depends(cere_context)):
    """Starea SPV cea mai recenta per factura (pentru semaforul butonului). Fara apel ANAF."""
    try:
        return _uc_tenants.facturi_trimiteri_spv(tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


def _factura_din_parsat(cur, schema, f):
    """[P7 · use-case, lotul 2] Invelisul HTTP al lui `core/uc_comun._factura_din_parsat` — traduce
    refuzul de domeniu inapoi in `HTTPException`. Corpul a plecat in stratul use-case."""
    try:
        return _uc_comun._factura_din_parsat(cur, schema, f)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/import-efactura")  # [api_intern_v1] upload manual XML/ZIP - fara buton in UI, pastrat deliberat. Verificat 27.08.2026 - niciun apelant in static/, in crontab sau in timerele systemd. (R70). CORECTAT 29.08.2026: forma veche scria ca `core/spv_receive` cheama direct `_factura_din_parsat` - E FALS. `spv_receive.importa_mesaj` scrie DOAR in `efactura_primite`, si numai mesaje al caror `cif_beneficiar` e chiar tenantul (gard anti-scurgere), deci numai PRIMITE. Consecinta, si e chiar perimetrul lui R91: singura cale prin care o factura EMISA intra prin import e ruta asta, incarcarea manuala de XML.
def import_efactura(tenant_id: int, fisiere: list[UploadFile] = File(...),
                          ctx=Depends(cere_cabinet)):
    """Upload XML/ZIP e-Factura. Parseaza UBL, directie auto (CUI firma vs furnizor),
    idempotent pe (numar, tert_cui, data_emitere)."""
    try:
        return _uc_tenants.import_efactura(tenant_id, [(_octetii(_f), _f.filename) for _f in fisiere], ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/tenants/{tenant_id}/facturi-primite")
def facturi_primite_lista(tenant_id: int, ctx=Depends(cere_context)):
    """Facturi primite din SPV de VALIDAT (four-eyes): ciorne parsate + cont sugerat. Acces = are
    acces la tenant (rol cu drept SAU proprietar gratuit); NU compara identitati (importatorul e cronul)."""
    try:
        return _uc_tenants.facturi_primite_lista(tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/tenants/{tenant_id}/facturi-primite/{primita_id}/xml")
def factura_primita_xml(tenant_id: int, primita_id: int, ctx=Depends(cere_context)):
    """XML-ul brut arhivat (la click, nu in fata)."""
    try:
        return _uc_tenants.factura_primita_xml(tenant_id, primita_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/facturi-primite/{primita_id}/valideaza")
def factura_primita_valideaza(tenant_id: int, primita_id: int, corp: dict = Body(default={}),
                              ctx=Depends(cere_rol("admin_firma"))):
    """FOUR-EYES: omul valideaza ciorna importata de cron -> creeaza cheltuiala (factura primita) +
    leaga factura_id + status=validata. Idempotent (FOR UPDATE + verifica status). cont sugerat,
    confirmat de om. Gard = acces la tenant + actiune umana explicita; NU identitate != importator."""
    try:
        return _uc_tenants.factura_primita_valideaza(tenant_id, primita_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/facturi-primite/{primita_id}/respinge")
def factura_primita_respinge(tenant_id: int, primita_id: int, corp: dict = Body(default={}),                              ctx=Depends(cere_context)):
    """Respinge o factura primita: status=respinsa + motiv. NU sterge randul (ramane cu istoric)."""
    try:
        return _uc_tenants.factura_primita_respinge(tenant_id, primita_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/reges-config")
# [R56, 26.08.2026] Cheile de acces la un sistem extern nu sunt date ale firmei — sunt
# CREDENTIALE. Costin: *„admin_firma, nu drept fin. Un drept nou e un al doilea sistem de
# autorizare de intretinut, iar cele trei rute nu justifica unul."* Acelasi criteriu ca la
# R42 (d), pornirea/oprirea unui canal — deja aplicat pe `PUT /woocommerce/config`.
def reges_config(tenant_id: int, corp: dict = Body(...),                  ctx=Depends(cere_rol("admin_firma"))):
    """corp: {username, parola, mediu test|prod}. Chei API din aplicatia REGES Angajator."""
    try:
        return _uc_tenants.reges_config(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/reges-trimite-salariat")
# [R42] „iese către o autoritate" — salariatul ajunge în registrul de evidență a muncii.
def reges_trimite_salariat(tenant_id: int, corp: dict = Body(...),
                           ctx=Depends(cere_rol("admin_firma"))):
    """corp: {salariat_id, adresa, contract {numar, data_contract, data_inceput, salariu, cor, ...}?}.
    Trimite InregistrareSalariat (+ AdaugareContract daca vine si contract dupa referinta)."""
    try:
        return _uc_tenants.reges_trimite_salariat(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/reges-poll")
# [R56, 26.08.2026] Cheile de acces la un sistem extern nu sunt date ale firmei — sunt
# CREDENTIALE. Costin: *„admin_firma, nu drept fin. Un drept nou e un al doilea sistem de
# autorizare de intretinut, iar cele trei rute nu justifica unul."* Acelasi criteriu ca la
# R42 (d), pornirea/oprirea unui canal — deja aplicat pe `PUT /woocommerce/config`.
def reges_poll(tenant_id: int, ctx=Depends(cere_rol("admin_firma"))):
    """Citeste+consuma un mesaj din coada REGES; salveaza referintele in reges_mesaje."""
    try:
        return _uc_tenants.reges_poll(tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/achizitie-taxare-inversa")
def achizitie_taxare_inversa(tenant_id: int, corp: dict = Body(...),                              ctx=Depends(cere_rol("admin_firma"))):
    """corp: {data, categorie, valoare (fara TVA), cont_destinatie, cota?,
    furnizor_platitor_tva, descriere?}. Beneficiarul (firma) trebuie platitor TVA.
    Nota ciorna: cont_dest=401 valoare + 4426=4427 TVA (norme pct. 109)."""
    try:
        return _uc_tenants.achizitie_taxare_inversa(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/tenants/{tenant_id}/verifica-vies")  # [vies_emitere_v1] validare VIES - folosit din emitere
def verifica_vies_ep(tenant_id: int, cod_tva: str, ctx=Depends(cere_context)):
    """Verifica un cod TVA UE in VIES (API oficial CE)."""
    try:
        return _uc_tenants.verifica_vies_ep(tenant_id, cod_tva, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/achizitie-ic")
def achizitie_ic(tenant_id: int, corp: dict = Body(...),                  ctx=Depends(cere_rol("admin_firma"))):
    """AIC bunuri/servicii primite (art. 268 / 278(2), plata = beneficiar art. 308).
    corp: {data, valoare (RON), cont_destinatie, cota?, tip bunuri|servicii, descriere?}.
    Nota ciorna: cont_dest=401 + 4426=4427 (norme 109)."""
    try:
        return _uc_tenants.achizitie_ic(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/achizitie-neinregistrat")
def achizitie_neinregistrat(tenant_id: int, corp: dict = Body(...),                             ctx=Depends(cere_rol("admin_firma"))):
    """Achizitie de la persoana fizica NEINREGISTRATA in scop TVA -> op N in D394 (pct.216 tip_partener=2).
    corp: {data, furnizor_nume (obligatoriu), valoare, cont_cheltuiala, numar?, categorie? (CODPR_N lit.D),
    descriere?}. Fara CUI furnizor -> tip N. categorie OPTIONALA: FARA ea N ramane EXCLUS din D394 cu avertisment
    (nu se ghiceste - continut declarat). PF nu factureaza TVA -> linie cota 0. Nota: cont_cheltuiala = 401."""
    try:
        return _uc_tenants.achizitie_neinregistrat(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/vanzare-ic")
def vanzare_ic(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """LIC bunuri (art. 294(2)a) sau prestare servicii IC (art. 278(2)).
    corp: {data, valoare, cod_tva_client, tip bunuri|servicii, dovada_transport?,
    cont_venit?, descriere?}. Verifica VIES LIVE. Nota: 4111=70x fara TVA."""
    try:
        return _uc_tenants.vanzare_ic(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)



@app.post("/tenants/{tenant_id}/import-extracomunitar")
def import_extracomunitar(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, valoare_vamala (RON), procent_taxa_vamala?, accize?, accesorii?,
    cota?, certificat_amanare?, cont_destinatie, descriere?}.
    Nota ciorna: marfa cont=401; taxe vamale cont=446; TVA dupa mod:
    decont 4426=4427 | vama 4426=446 | cost cont=446."""
    try:
        return _uc_tenants.import_extracomunitar(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/export-extracomunitar")
def export_extracomunitar(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, valoare, tara_client, dovada_export, cont_venit?, descriere?}.
    Scutit art. 294(1)a cu DVE. Nota: 4111=70x fara TVA."""
    try:
        return _uc_tenants.export_extracomunitar(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/tenants/{tenant_id}/intrastat-praguri")
def intrastat_praguri(tenant_id: int, an: int, ctx=Depends(cere_cabinet)):
    """Monitor praguri Intrastat (Ordin INS 1604/2025, 1.000.000 lei/flux):
    introduceri = facturi primite de la parteneri UE; expedieri = facturi emise
    catre parteneri UE. Cumulat pe an, status + luna depasirii per flux."""
    try:
        return _uc_tenants.intrastat_praguri(tenant_id, an, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/nota-tva-incasare")
def nota_tva_incasare(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, sens incasare|plata, suma_incasata, cota?, descriere?}.
    incasare: 4428=4427 devine exigibil TVA colectat (suta marita);
    plata: 4426=4428 devine deductibil TVA achitat furnizorului. Nota ciorna."""
    try:
        return _uc_tenants.nota_tva_incasare(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

@app.post("/tenants/{tenant_id}/decontare-valuta")
def decontare_valuta(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """Incasare creanta / plata datorie in valuta cu diferenta de curs 665/765.
    corp: {data, valoare_valuta, moneda, curs_evidenta, tip creanta|datorie,
    cont_tert, cont_banca?, descriere?}. Cursul decontarii = BNR la data (auto)."""
    try:
        return _uc_tenants.decontare_valuta(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/reevaluare-valuta")
def reevaluare_valuta(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """Reevaluare lunara solduri valuta (OMFP 1802 pct. 316), curs BNR auto.
    corp: {data (ultima zi luna), solduri: [{cont, valoare_valuta, moneda,
    curs_evidenta, tip creanta|datorie|disponibil}]}. O nota cu toate liniile."""
    try:
        return _uc_tenants.reevaluare_valuta(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/nota-leasing")
def nota_leasing(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, tip primire|rata|reziduala|operational, descriere?, cota?,
    + campuri pe tip: primire{valoare_capital, dobanda_totala, cont_imobilizare?};
    rata{capital, dobanda?, comision?}; reziduala{valoare_reziduala};
    operational{chirie, cont_cheltuiala?}}. Nota ciorna."""
    try:
        return _uc_tenants.nota_leasing(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/nota-credit")
def nota_credit(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, operatie primire|dobanda|plata|restanta|garantie, tip lung|scurt,
    descriere?, + pe operatie: primire{suma}; dobanda{dobanda}; plata{rata?, dobanda?,
    comision?, dobanda_angajata?}; restanta{suma}; garantie{suma, fel primita|acordata,
    actiune inregistrare|eliberare}}. Nota ciorna."""
    try:
        return _uc_tenants.nota_credit(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/nota-avans")
def nota_avans(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, operatie avans_platit|regularizare_platit|avans_incasat|
    regularizare_incasat, suma (fara TVA), cota?, destinatie? (platit:
    stocuri|servicii|imobilizari|imobilizari_necorporale), descriere?}."""
    try:
        return _uc_tenants.nota_avans(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/achizitie-necorporala")
def achizitie_necorporala(tenant_id: int, corp: dict = Body(...),                           ctx=Depends(cere_rol("admin_firma"))):
    """corp: {data, denumire, valoare (fara TVA), tip software|licenta|brevet|
    dezvoltare|constituire, dnf_luni?, cota?, cod?}.
    Art. 28(9): software = 36 luni (fix); licenta/brevet = durata contract (dnf_luni
    obligatoriu); constituire = max 60 luni. Nota ciorna 20x+4426=404 + inscriere
    in mijloace_fixe (amortizare lunara preluata de mecanismul existent)."""
    try:
        return _uc_tenants.achizitie_necorporala(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/reevaluare-imobilizare")
def reevaluare_imobilizare(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, operatie reevaluare|surplus, + reevaluare{mijloc_fix_id,
    valoare_justa, sold_105_activ?, pierdere_655_anterioara?} | surplus{suma}}.
    Reevaluarea citeste valoarea+amortizarea cumulata din mijloace_fixe si
    actualizeaza valoarea/dnf ramane manual (raport evaluator)."""
    try:
        return _uc_tenants.reevaluare_imobilizare(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/nota-provizion")
def nota_provizion_ep(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, fel creanta|provizion|stoc, actiune constituire|reluare, suma,
    descriere?, + creanta{zile_depasire?, garantata?, afiliata?, faliment?} |
    provizion{tip litigii|garantii|dezafectare|restructurare|impozite|altele} |
    stoc{cont_ajustare?}}. Raspunsul include deductibilitatea fiscala."""
    try:
        return _uc_tenants.nota_provizion_ep(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/nota-productie")
def nota_productie(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, operatie obtinere|pic|vanzare, descriere?, +
    obtinere{cost_standard, cost_efectiv?}; pic{suma, moment constatare|reluare};
    vanzare{pret_vanzare, cost_standard_iesit, cota?, coef_348?}}."""
    try:
        return _uc_tenants.nota_productie(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/nota-obiect-inventar")
def nota_obiect_inventar(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, operatie achizitie|dare_folosinta|scoatere, valoare, cota?,
    descriere?}. Achizitia verifica pragul MF (5000 din 25.02.2026, OUG 8/2026)
    si refuza daca valoarea e peste prag (foloseste fluxul de mijloace fixe)."""
    try:
        return _uc_tenants.nota_obiect_inventar(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/nota-asociati")
def nota_asociati(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, operatie dividend|regularizare|imprumut, descriere?, +
    dividend{brut, interimar?, cu_plata?}; regularizare{total_interimar,
    dividend_anual}; imprumut{suma, fel primire|restituire, dobanda?}}."""
    try:
        return _uc_tenants.nota_asociati(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/nota-sponsorizare")
def nota_sponsorizare_ep(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, suma, mod contract|plata, descriere?, + optional pentru calcul
    credit: cifra_afaceri, impozit_profit, tip_impozit profit|micro,
    beneficiar_in_registru}. Nota 6582 + info credit fiscal/D177."""
    try:
        return _uc_tenants.nota_sponsorizare_ep(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/nota-subventie")
def nota_subventie(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, fel exploatare|investitii|reluare, descriere?, +
    exploatare/investitii{suma, moment drept|incasare};
    reluare{valoare_activ, subventie, amortizare_lunara}}."""
    try:
        return _uc_tenants.nota_subventie(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/nota-chirie")
def nota_chirie(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, fel comodat|chirie_platita|chirie_incasata|refacturare,
    descriere?, cota?, + comodat{valoare, moment primire|restituire};
    chirie_platita{chirie, proprietar pj|pf}; chirie_incasata{chirie};
    refacturare{total_factura, parte_refacturata}}.
    Refacturarea creeaza DOUA note (primire+emitere)."""
    try:
        return _uc_tenants.nota_chirie(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/nota-decont-deplasare")
def nota_decont_deplasare(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, fel avans|decont|plafon, descriere?, sursa casa|banca, +
    avans{suma}; decont{avans, diurna?, transport?, cazare?, cota?};
    plafon{diurna_pe_zi, zile, salariu_baza, zile_lucratoare, diurna_bugetara?,
    curs?} - plafon NU creeaza nota, doar calculeaza}."""
    try:
        return _uc_tenants.nota_decont_deplasare(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/nota-bacsis")
def nota_bacsis(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, fel incasare|distribuire, suma, sursa card|numerar (incasare) /
    banca|casa (distribuire), descriere?}. Legea 376/2022: fara TVA, fara
    CAS/CASS, impozit 10% retinut la distribuire (D100, informativ D205)."""
    try:
        return _uc_tenants.nota_bacsis(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/nota-sgr")
def nota_sgr(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, operatie achizitie|vanzare|restituire|autofactura|virare,
    descriere?, + nr_ambalaje|suma, sursa casa|banca, +
    autofactura{garantii_returnate, tarif_gestionare?, cota?}; virare{suma,
    catre furnizor|plata}}. Garantia 0,50 lei/ambalaj, in afara sferei TVA."""
    try:
        return _uc_tenants.nota_sgr(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/nota-perisabilitati")
def nota_perisabilitati(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, valoare_intrari, procent_limita (coef. grupa HG 831/2004),
    pierdere_constatata, cota?, cont_stoc?, degradare_dovedita_distrusa?,
    descriere?}. Nota 607 (split deductibil/nedeductibil) + ajustare TVA 635=4426
    pe depasire."""
    try:
        return _uc_tenants.nota_perisabilitati(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/nota-contract-special")
def nota_contract_special(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, fel zilier|cenzor|mandat, brut, sursa casa|banca, descriere?}.
    Zilieri: impozit 10%+CAS 25% fara CASS (L52/2011). Cenzor/mandat: CAS+CASS+
    impozit, fara CAM (art. 76(2)g/i)."""
    try:
        return _uc_tenants.nota_contract_special(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/tenants/{tenant_id}/mijloace-fixe")
def tenant_mijloace_fixe(tenant_id: int, ctx=Depends(cere_cabinet)):
    """[ecran_mf_v1 14.08.2026; amortizare pe metoda 16.08.2026] Registrul mijloacelor fixe ale
    firmei: valoare, amortizat la zi PE METODA activului (liniar/degresiv/accelerat/superaccelerat,
    CF art.28 - motor unic core.d406_active.amortizat_la_data), ramas (net book value), stare
    activ/casat. Randul al carui activ are metoda nepermisa pe categorie (alin.5/8^1) NU se
    calculeaza liniar tacit: intoarce amortizat=None, ramas=None, eroare=<motiv> (DS cap.17).
    Casat: amortizat/ramas None (instantaneul de la casare nu se pastreaza in mijloace_fixe).
    Sursa unica pentru ID-ul cerut de casare/reevaluare (pana acum netastabil - niciun ecran)."""
    try:
        return _uc_tenants.tenant_mijloace_fixe(tenant_id, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/nota-inventariere")
def nota_inventariere(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, operatie plus|plus_mf|minus|casare, descriere?, +
    plus{valoare, cont_stoc?}; plus_mf{valoare, cont_imobilizare?};
    minus{valoare, cont_stoc?, imputabil?, valoare_imputare?, vinovat
    salariat|tert, cota?, asigurat_sau_distrus?};
    casare{mijloc_fix_id SAU valoare_bruta+amortizare_cumulata+conturi}.
    Casarea cu mijloc_fix_id calculeaza amortizarea auto si dezactiveaza MF."""
    try:
        return _uc_tenants.nota_inventariere(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/nota-lichidare")
def nota_lichidare(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, operatie vanzare_activ|partaj, descriere?, +
    vanzare_activ{pret, valoare_bruta, amortizare_cumulata, conturi?, cota?};
    partaj{capital_social, rezerve?, profituri?}}. OMFP 897/2015."""
    try:
        return _uc_tenants.nota_lichidare(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.post("/tenants/{tenant_id}/nota-ong")
def nota_ong(tenant_id: int, corp: dict = Body(...), ctx=Depends(cere_cabinet)):
    """corp: {data, operatie venit|scutire, descriere?, +
    venit{suma, fel cotizatie|contributie|donatie|sponsorizare|financiar|
    fonduri|ocazional|alte, sursa casa|banca};
    scutire{venituri_economice, venituri_neimpozabile, curs_eur} - doar calcul,
    fara nota}. OMFP 3103/2017 + art. 15(2)-(3) CF."""
    try:
        return _uc_tenants.nota_ong(tenant_id, corp, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)

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
    try:
        return _uc_cont.cont_bun_venit_vazut(ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


# ============================================================
#  PAGINI PUBLICE DE GHID (DS cap.22) — /ghid/{slug} + index + sitemap + robots
# ============================================================
import re as _ghid_re
import html as _ghid_html
import json as _ghid_json
from core import repo_main as _repo

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


class EvenimentPublicIn(BaseModel):
    tip: str
    pagina: Optional[str] = None


@app.post("/api/eveniment-public")
def eveniment_public(date: EvenimentPublicIn):
    """Inregistrare eveniment public de interes (deschidere modal, click Intra in cont, vizita ghid).
    Se stocheaza DOAR: tip (lista alba), pagina (calea proprie, curatata) si momentul (DEFAULT now()).
    NU se citeste si NU se retine IP, User-Agent, cookie, sesiune sau vreun identificator -> fara date
    personale -> fara obligatie de consimtamant. Fire-and-forget (clientul foloseste sendBeacon)."""
    try:
        return _uc_api.eveniment_public(date)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


@app.get("/admin/analytics")
def admin_analytics(zile: int = 30, ctx=Depends(cere_rol("superadmin"))):
    """Cifre agregate din public.eveniment_public: pe eveniment, pe zi, pe pagina de provenienta.
    Fara date personale (tabela nu contine niciun identificator)."""
    try:
        return _uc_admin.admin_analytics(zile, ctx)
    except _erori.EroareDeDomeniu as e:
        raise _http_din(e)


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
           "Disallow: /\n"                  # restul suprafetei (app, /auth, rute API)
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
