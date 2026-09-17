# -*- coding: utf-8 -*-
"""USE_CASE — rutele `/migrare`.

[P7 · valul use-case, 13.09.2026] Corpurile astea stateau in `main.py`, adica in stratul HTTP, si
isi deschideau singure tranzactia. Textul canonic (`PLAN_HARDENING.md:840`) spune ca use-case-ul e
cel care **detine tranzactia si orchestreaza**; aici e mutarea, nu o rescriere.

CE S-A PASTRAT, literă cu literă: corpul, cu tot cu blocurile `with db.get_conn()`, in aceeasi
ordine, cu aceleasi efecte. CE S-A TRADUS: `HTTPException(cod, mesaj)` a devenit
`_erori.<Clasa>(mesaj)` — acelasi mesaj, iar codul se pune la loc in stratul HTTP, dintr-o singura
harta. Se poate face fiindca `HTTPException` **nu e prinsa nicaieri** in aplicatie.

CE A RAMAS IN `main.py`: semnatura rutei (FastAPI valideaza pe ea), docstringul ei, si o linie care
cheama functia de aici prin adaptorul `_http`.
"""

from core import db, migrare_api
from core import erori as _erori
from core import db, auth_api, migrare_api, istoric_declaratii_import_api
from core import uc_comun as _uc_comun
from core import db, auth_api, tenant_provisioning, anaf_api, migrare_api, istoric_declaratii_import_api, observare as _obs
from core import repo_tenants
from core import tranzactie   # [C2] savepoint-uri numite (SQL sta in modulul de tranzactie, nu in use-case)


def migrare_status_citeste(ctx):
    """[P7 · use-case] Corpul rutei `/migrare/status`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        status = migrare_api.citeste_status(conn, ctx["firm"])
        rem = migrare_api.reminder(conn, ctx["firm"])
    return {"straturi": migrare_api.STRATURI, "status": status, "reminder": rem}


def migrare_status_seteaza(date, ctx):
    """[P7 · use-case] Corpul rutei `/migrare/status`; docstringul ei a ramas in stratul HTTP."""
    try:
        with db.get_conn() as conn:
            r = migrare_api.seteaza_status(conn, ctx["firm"], date.strat, date.stare, date.nota)
    except ValueError as e:
        raise _erori.CerereGresita(str(e))
    return r


def migrare_istoric_status(ctx):
    """[P7 · use-case] Corpul rutei `/migrare/istoric-declaratii`; docstringul ei a ramas in stratul HTTP."""
    out = []
    with db.get_conn() as conn:
        firme = auth_api.tenantii_userului(conn, ctx["uid"])
        try:
            rez = istoric_declaratii_import_api.rezumat_lot(conn, [f.get("id") for f in firme])
        except Exception:
            _uc_comun._LOG_VERDICT.warning("istoric-declaratii: rezumatul de lot a esuat -> zero pentru tot "
                                 "portofoliul (ca bucla veche, per firma)", exc_info=True)
            rez = {}
    for f in firme:
        r = rez.get(f.get("id")) or {"are_istoric": False, "randuri": 0}
        out.append({"tenant_id": f.get("id"), "nume": f.get("nume"), "cui": f.get("cui"),
                    "are_istoric": r["are_istoric"], "randuri": r["randuri"]})
    return {"firme": out}


def migrare_importa(date, ctx):
    """[P7 · use-case] Corpul rutei `/migrare/importa`; docstringul ei a ramas in stratul HTTP."""
    if _uc_comun._TENANT_TEMPLATE is None:
        raise _erori.EsecIntern("template tenant indisponibil pe server")
    creat, erori = [], []
    _de_precompletat = []          # [(schema_name, cui)] — ANAF se cheamă abia după bloc
    with db.get_conn() as conn:
        # CUI-urile deja existente în portofoliul cabinetului (normalizate la cifre)
        with conn.cursor() as cur:
            existente = set()
            for (c,) in repo_tenants.cui_uri_din_portofoliu(cur, ctx["firm"]):
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
            # [C2, 17.09.2026] Denumirea depaseste `tenants.nume varchar(255)`? Se respinge CURAT, nu
            # se lasa sa crape INSERT-ul in mijlocul blocului. `MigrareFirma.denumire` e nelimitat.
            if len(nume) > 255:
                erori.append(migrare_api.respinge(
                    "firmă", "firma %s (CUI %s)" % (nume[:60] + "…", f.cui), "creare_esuata",
                    "denumirea depășește 255 de caractere (are %d)" % len(nume), cui=str(f.cui), nume=nume[:255]))
                continue
            # [C2] SAVEPOINT per firma: o eroare la UNA nu aborteaza tranzactia pentru celelalte si nu
            # lasa commitul final sa faca ROLLBACK TACIT peste tot. Pana azi, o eroare psycopg2 (ex:
            # denumire prea lunga) aborta tranzactia, firmele urmatoare picau cu „current transaction is
            # aborted", iar la iesirea din `with` commitul pe tranzactie abortata = ROLLBACK tacit —
            # raspunsul spunea „creat", baza nu continea nimic. Masurat de audit (C2).
            with conn.cursor() as _cur:
                tranzactie.savepoint_firma(_cur)
            try:
                r = tenant_provisioning.provision_tenant(
                    conn, nume, str(f.cui), ctx["firm"], ctx["uid"], _uc_comun._TENANT_TEMPLATE)
                with conn.cursor() as _cur:
                    tranzactie.elibereaza_firma(_cur)
                # [P5 val 3] ANAF se cheamă DUPĂ bloc, și numai pentru firmele CHIAR create —
                # exact ca azi. Aici doar se reține ce urmează să se precompleteze.
                _de_precompletat.append((r["schema_name"], f.cui))
                creat.append({"cui": str(f.cui), "nume": nume, "tenant_id": r.get("tenant_id")})
                if cuic:
                    existente.add(cuic)   # prinde și duplicate în același lot
            except Exception as e:
                # [C2] recuperam tranzactia la savepoint: firmele deja create raman, cea care a esuat
                # se anuleaza doar pe ea. ESEC, nu respingere de date — cauza se poate deosebi.
                with conn.cursor() as _cur:
                    tranzactie.intoarce_la_firma(_cur)
                erori.append(migrare_api.respinge(
                    "firmă", "firma %s (CUI %s)" % (nume, f.cui), "creare_esuata",
                    "nu s-a putut crea: %s" % e, cui=str(f.cui), nume=nume))
    # ── [P5 val 3] ANAF, FĂRĂ nicio conexiune (termen 20 s + 1,1 s între loturi) ────────
    _anaf = []
    for _schema_n, _cui_f in _de_precompletat:
        try:
            _anaf.append((_schema_n, tenant_provisioning.date_din_anaf(_cui_f)))
        except Exception as _ea:
            _obs.esec_secundar("precompletare ANAF la import firma", _ea)  # firma creata; ANAF completabil manual
    if _anaf:
        with db.get_conn() as conn:          # tranzacție scurtă, doar scrierea
            for _schema_n, _d in _anaf:
                try:
                    tenant_provisioning.precompleteaza_din_anaf(conn, _schema_n, _d, seteaza_nume=False)
                except Exception as _ea:
                    _obs.esec_secundar("precompletare ANAF la import firma", _ea)
    return {"creat": creat, "erori": erori, "total": len(creat)}

